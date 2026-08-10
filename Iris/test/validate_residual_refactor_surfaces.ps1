[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateSet('Baseline', 'Closeout', 'AttestationProbe')]
    [string]$Mode,
    [Parameter(Mandatory = $true)]
    [string]$RepositoryRoot,
    [Parameter(Mandatory = $true)]
    [string]$EvidenceRoot,
    [string]$HistoricalManifestAttestationPath
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$Utf8NoBom = New-Object System.Text.UTF8Encoding($false)
$Utf8Strict = New-Object System.Text.UTF8Encoding($false, $true)

function Write-Json([string]$Path, [object]$Value) {
    $Parent = Split-Path -Parent $Path
    if (-not (Test-Path -LiteralPath $Parent)) {
        New-Item -ItemType Directory -Path $Parent -Force | Out-Null
    }
    [System.IO.File]::WriteAllText(
        $Path,
        (($Value | ConvertTo-Json -Depth 100) + "`n"),
        $Utf8NoBom
    )
}

function Get-Relative([string]$Path) {
    $RootUri = New-Object System.Uri(($RepositoryRoot.TrimEnd('\') + '\'))
    $PathUri = New-Object System.Uri([System.IO.Path]::GetFullPath($Path))
    return [System.Uri]::UnescapeDataString($RootUri.MakeRelativeUri($PathUri).ToString()).Replace('\','/')
}

function Get-GitTracked([string]$RelativePath) {
    $Rows = @(& git -C $RepositoryRoot ls-files -- $RelativePath)
    if ($LASTEXITCODE -ne 0) { throw "git ls-files failed for $RelativePath" }
    return $Rows.Count -gt 0
}

function Get-HashOrNull([string]$Path) {
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) { return $null }
    return (Get-FileHash -Algorithm SHA256 -LiteralPath $Path).Hash.ToLowerInvariant()
}

function Get-TextSha256([string]$Text) {
    $Algorithm = [System.Security.Cryptography.SHA256]::Create()
    try {
        $Bytes = $Utf8NoBom.GetBytes($Text)
        return [System.BitConverter]::ToString($Algorithm.ComputeHash($Bytes)).Replace('-', '').ToLowerInvariant()
    }
    finally { $Algorithm.Dispose() }
}

function Test-LineEndingEquivalent([string]$Path, [string]$ExpectedHash) {
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) { return $false }
    try {
        $Text = [System.IO.File]::ReadAllText($Path, [System.Text.Encoding]::UTF8)
        if ($Text.Contains([char]0)) { return $false }
        $Normalized = $Text.Replace("`r`n", "`n").Replace("`r", "`n")
        $Variants = @(
            $Normalized,
            $Normalized.Replace("`n", "`r`n"),
            $Normalized.Replace("`n", "`r")
        )
        return @($Variants | Where-Object {
            (Get-TextSha256 $_) -ceq $ExpectedHash
        }).Count -gt 0
    }
    catch {
        return $false
    }
}

function Get-LfTextHashOrNull([string]$Path) {
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) { return $null }
    $Text = [System.IO.File]::ReadAllText($Path, [System.Text.Encoding]::UTF8)
    if ($Text.Contains([char]0)) { return $null }
    return Get-TextSha256 $Text.Replace("`r`n", "`n").Replace("`r", "`n")
}

function Get-GitBlobLfHash([string]$Blob) {
    if ($Blob -notmatch '^[0-9a-f]{40,64}$') { throw "invalid Git blob identity: $Blob" }
    $StartInfo = New-Object System.Diagnostics.ProcessStartInfo
    $StartInfo.FileName = 'git'
    $EscapedRoot = $RepositoryRoot.Replace('"', '\"')
    $StartInfo.Arguments = '-C "' + $EscapedRoot + '" cat-file blob ' + $Blob
    $StartInfo.UseShellExecute = $false
    $StartInfo.RedirectStandardOutput = $true
    $StartInfo.RedirectStandardError = $true
    $Process = New-Object System.Diagnostics.Process
    $Process.StartInfo = $StartInfo
    $Stream = New-Object System.IO.MemoryStream
    try {
        [void]$Process.Start()
        $Process.StandardOutput.BaseStream.CopyTo($Stream)
        $StandardError = $Process.StandardError.ReadToEnd()
        $Process.WaitForExit()
        if ($Process.ExitCode -ne 0) { throw "git cat-file failed for ${Blob}: $StandardError" }
        $Text = $Utf8Strict.GetString($Stream.ToArray())
        if ($Text.Contains([char]0)) { throw "Git blob is not a text surface: $Blob" }
        return Get-TextSha256 $Text.Replace("`r`n", "`n").Replace("`r", "`n")
    }
    finally {
        $Stream.Dispose()
        $Process.Dispose()
    }
}

function Assert-HistoricalManifestAttestation([object]$Attestation, [string]$ExpectedPath) {
    if (
        [string]$Attestation.path -cne $ExpectedPath -or
        [string]$Attestation.commit -notmatch '^[0-9a-f]{40}$' -or
        [string]$Attestation.tree -notmatch '^[0-9a-f]{40}$' -or
        [string]$Attestation.git_blob_id -notmatch '^[0-9a-f]{40,64}$' -or
        [string]$Attestation.sha256_lf -notmatch '^[0-9a-f]{64}$' -or
        [string]$Attestation.attested_schema_version -cne 'iris_repository_runtime_lightweighting_protected_surface_successor_v1' -or
        [string]$Attestation.attested_authority -cne 'repository_owner_user' -or
        [string]$Attestation.interpretation -cne 'embedded_identity_chain_only'
    ) {
        throw 'repository lightweighting historical manifest attestation invalid'
    }
    $Commit = [string]$Attestation.commit
    $Tree = (& git -C $RepositoryRoot rev-parse ($Commit + '^{tree}')).Trim()
    if ($LASTEXITCODE -ne 0 -or $Tree -cne [string]$Attestation.tree) {
        throw 'repository lightweighting historical manifest attestation tree mismatch'
    }
    & git -C $RepositoryRoot merge-base --is-ancestor $Commit HEAD 2>$null
    if ($LASTEXITCODE -ne 0) {
        throw 'repository lightweighting historical manifest attestation is not durable ancestry'
    }
    $Blob = (& git -C $RepositoryRoot rev-parse ($Commit + ':' + $ExpectedPath)).Trim()
    if (
        $LASTEXITCODE -ne 0 -or
        $Blob -cne [string]$Attestation.git_blob_id -or
        (Get-GitBlobLfHash $Blob) -cne [string]$Attestation.sha256_lf
    ) {
        throw 'repository lightweighting historical manifest attestation blob mismatch'
    }
    $ManifestLines = @(& git -C $RepositoryRoot cat-file blob $Blob)
    if ($LASTEXITCODE -ne 0) {
        throw 'repository lightweighting historical manifest attestation read failed'
    }
    $Payload = ($ManifestLines -join "`n") | ConvertFrom-Json
    if (
        [string]$Payload.schema_version -cne [string]$Attestation.attested_schema_version -or
        [string]$Payload.authority -cne [string]$Attestation.attested_authority
    ) {
        throw 'repository lightweighting attested historical manifest payload mismatch'
    }
    return [pscustomobject]@{
        commit = $Commit
        tree = $Tree
        blob = $Blob
        payload = $Payload
    }
}

function Get-TreeRows([string]$Root) {
    $Rows = @()
    if (-not (Test-Path -LiteralPath $Root -PathType Container)) { return $Rows }
    foreach ($File in Get-ChildItem -LiteralPath $Root -File -Recurse | Sort-Object FullName) {
        $Relative = $File.FullName.Substring($Root.TrimEnd('\').Length + 1).Replace('\','/')
        $Rows += [ordered]@{
            path = $Relative
            bytes = $File.Length
            sha256 = (Get-FileHash -Algorithm SHA256 -LiteralPath $File.FullName).Hash.ToLowerInvariant()
        }
    }
    return $Rows
}

$RepositoryRoot = [System.IO.Path]::GetFullPath($RepositoryRoot).TrimEnd('\','/')
$GitRoot = (& git -C $RepositoryRoot rev-parse --show-toplevel 2>&1 | Out-String).Trim()
if ($LASTEXITCODE -ne 0 -or -not $RepositoryRoot.Equals(
    [System.IO.Path]::GetFullPath($GitRoot).TrimEnd('\','/'),
    [System.StringComparison]::OrdinalIgnoreCase
)) { throw 'RepositoryRoot identity mismatch' }
$EvidenceRoot = if ([System.IO.Path]::IsPathRooted($EvidenceRoot)) {
    [System.IO.Path]::GetFullPath($EvidenceRoot)
} else {
    [System.IO.Path]::GetFullPath((Join-Path $RepositoryRoot $EvidenceRoot))
}
$SubjectCommit = (& git -C $RepositoryRoot rev-parse HEAD).Trim()
$SubjectTree = (& git -C $RepositoryRoot rev-parse 'HEAD^{tree}').Trim()
$PredecessorSupportedPath = Join-Path $RepositoryRoot 'Iris/_docs/refactor/core_refactor/phase0_supported_api_manifest.json'
$PredecessorProtectedPath = Join-Path $RepositoryRoot 'Iris/_docs/refactor/core_refactor/phase0_protected_surface_manifest.json'
$SupportedBaselinePath = Join-Path $EvidenceRoot 'phase0_supported_api_manifest.json'
$ProtectedBaselinePath = Join-Path $EvidenceRoot 'phase0_protected_surface_manifest.json'
$ApprovedDeltaManifestRelative = 'Iris/validation/clean_checkout/authority/offline_build_validation_protected_surface_delta.json'
$ApprovedDeltaManifestPath = Join-Path $RepositoryRoot $ApprovedDeltaManifestRelative
$LightweightingSuccessorRelative = 'Iris/_docs/refactor/repository_runtime_lightweighting/protected_surface_successor_manifest.json'
$LightweightingSuccessorPath = Join-Path $RepositoryRoot $LightweightingSuccessorRelative
$EvidenceLightweightingSuccessorRelative = 'Iris/_docs/refactor/repository_evidence_lightweighting/protected_surface_successor_manifest.json'
$EvidenceLightweightingSuccessorPath = Join-Path $RepositoryRoot $EvidenceLightweightingSuccessorRelative
if ($Mode -eq 'AttestationProbe') {
    if (
        [string]::IsNullOrWhiteSpace($HistoricalManifestAttestationPath) -or
        -not (Test-Path -LiteralPath $HistoricalManifestAttestationPath -PathType Leaf)
    ) {
        throw 'historical manifest attestation probe input missing'
    }
    $ProbeAttestation = Get-Content -LiteralPath $HistoricalManifestAttestationPath -Raw | ConvertFrom-Json
    [void](Assert-HistoricalManifestAttestation $ProbeAttestation $LightweightingSuccessorRelative)
    Write-Output 'repository lightweighting historical manifest attestation probe PASS'
    exit 0
}
if (-not (Test-Path -LiteralPath $ApprovedDeltaManifestPath -PathType Leaf)) {
    throw 'canonical approved protected-surface delta manifest missing'
}
$ApprovedDeltaManifestBlob = (& git -C $RepositoryRoot rev-parse ("HEAD:" + $ApprovedDeltaManifestRelative)).Trim()
if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($ApprovedDeltaManifestBlob)) {
    throw 'canonical approved protected-surface delta manifest is not tracked by HEAD'
}
$ApprovedDeltaManifestWorkingBlob = (& git -C $RepositoryRoot hash-object ("--path=" + $ApprovedDeltaManifestRelative) $ApprovedDeltaManifestPath).Trim()
if ($LASTEXITCODE -ne 0 -or $ApprovedDeltaManifestWorkingBlob -cne $ApprovedDeltaManifestBlob) {
    throw 'canonical approved protected-surface delta manifest differs from HEAD'
}
if (-not (Test-Path -LiteralPath $LightweightingSuccessorPath -PathType Leaf)) {
    throw 'repository lightweighting protected-surface successor manifest missing'
}
$LightweightingSuccessorBlob = (& git -C $RepositoryRoot rev-parse ("HEAD:" + $LightweightingSuccessorRelative)).Trim()
if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($LightweightingSuccessorBlob)) {
    throw 'repository lightweighting protected-surface successor is not tracked by HEAD'
}
$LightweightingSuccessorWorkingBlob = (& git -C $RepositoryRoot hash-object ("--path=" + $LightweightingSuccessorRelative) $LightweightingSuccessorPath).Trim()
if ($LASTEXITCODE -ne 0 -or $LightweightingSuccessorWorkingBlob -cne $LightweightingSuccessorBlob) {
    throw 'repository lightweighting protected-surface successor differs from HEAD'
}
if (-not (Test-Path -LiteralPath $EvidenceLightweightingSuccessorPath -PathType Leaf)) {
    throw 'repository evidence lightweighting protected-surface successor manifest missing'
}
$EvidenceLightweightingSuccessorBlob = (& git -C $RepositoryRoot rev-parse ("HEAD:" + $EvidenceLightweightingSuccessorRelative)).Trim()
if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($EvidenceLightweightingSuccessorBlob)) {
    throw 'repository evidence lightweighting protected-surface successor is not tracked by HEAD'
}
$EvidenceLightweightingSuccessorWorkingBlob = (& git -C $RepositoryRoot hash-object ("--path=" + $EvidenceLightweightingSuccessorRelative) $EvidenceLightweightingSuccessorPath).Trim()
if ($LASTEXITCODE -ne 0 -or $EvidenceLightweightingSuccessorWorkingBlob -cne $EvidenceLightweightingSuccessorBlob) {
    throw 'repository evidence lightweighting protected-surface successor differs from HEAD'
}

if ($Mode -eq 'Baseline') {
    $PredecessorSupported = Get-Content -LiteralPath $PredecessorSupportedPath -Raw | ConvertFrom-Json
    $Supported = [ordered]@{
        schema_version = 'iris-residual-supported-api-v1'
        validation_status = 'passed'
        claim_boundary = 'predecessor_20_listed_surfaces_only'
        subject_commit = $SubjectCommit
        subject_tree = $SubjectTree
        predecessor_manifest = Get-Relative $PredecessorSupportedPath
        predecessor_manifest_sha256 = Get-HashOrNull $PredecessorSupportedPath
        surface_count = @($PredecessorSupported.surfaces).Count
        intended_identity_delta = [ordered]@{
            return_table_identity = 'copy_on_read_for_frozen_array_and_tooltip_summary_boundaries'
            value_shape_signature = 'preserved'
        }
        surfaces = @($PredecessorSupported.surfaces)
    }
    Write-Json $SupportedBaselinePath $Supported

    $PredecessorProtected = Get-Content -LiteralPath $PredecessorProtectedPath -Raw | ConvertFrom-Json
    $Rows = @()
    foreach ($Row in $PredecessorProtected.rows) {
        $FullPath = Join-Path $RepositoryRoot ([string]$Row.path)
        $Rows += [ordered]@{
            path = [string]$Row.path
            exists = Test-Path -LiteralPath $FullPath -PathType Leaf
            tracked = Get-GitTracked ([string]$Row.path)
            role = [string]$Row.role
            hash_policy = [string]$Row.hash_policy
            sha256 = Get-HashOrNull $FullPath
        }
    }
    $Protected = [ordered]@{
        schema_version = 'iris-residual-protected-surface-v1'
        validation_status = 'passed'
        subject_commit = $SubjectCommit
        subject_tree = $SubjectTree
        predecessor_manifest = Get-Relative $PredecessorProtectedPath
        predecessor_manifest_sha256 = Get-HashOrNull $PredecessorProtectedPath
        approved_activation_deltas = @(
            [ordered]@{path='Iris/_docs/round3/round3_test_taxonomy.json';owner='residual_refactor_plan';reason='register five current-route tests'},
            [ordered]@{path='Iris/_docs/round3/current_route_required_validations.json';owner='residual_refactor_plan';reason='add five tests to required denominator'}
        )
        rows = $Rows
    }
    Write-Json $ProtectedBaselinePath $Protected

    $PackageBaseline = [ordered]@{
        schema_version = 'iris-residual-package-baseline-v1'
        validation_status = 'passed'
        subject_commit = $SubjectCommit
        subject_tree = $SubjectTree
        existing_package_role = 'read_only_projection'
        existing_package_rows = @(Get-TreeRows (Join-Path $RepositoryRoot 'Iris/build/package'))
        source_runtime_manifest_sha256 = Get-HashOrNull (Join-Path $RepositoryRoot 'Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks.lua')
    }
    Write-Json (Join-Path $EvidenceRoot 'phase0_package_identity_baseline.json') $PackageBaseline
    Write-Output "residual surface Baseline PASS: supported=$($Supported.surface_count) protected=$($Rows.Count)"
    exit 0
}

if (-not (Test-Path -LiteralPath $SupportedBaselinePath -PathType Leaf)) { throw 'supported API baseline missing' }
if (-not (Test-Path -LiteralPath $ProtectedBaselinePath -PathType Leaf)) { throw 'protected surface baseline missing' }
$SupportedBaseline = Get-Content -LiteralPath $SupportedBaselinePath -Raw | ConvertFrom-Json
$ProtectedBaseline = Get-Content -LiteralPath $ProtectedBaselinePath -Raw | ConvertFrom-Json
$LightweightingSuccessor = Get-Content -LiteralPath $LightweightingSuccessorPath -Raw | ConvertFrom-Json
$EvidenceLightweightingSuccessor = Get-Content -LiteralPath $EvidenceLightweightingSuccessorPath -Raw | ConvertFrom-Json
if ([string]$LightweightingSuccessor.schema_version -cne 'iris_repository_runtime_lightweighting_protected_surface_successor_v2') {
    throw 'repository lightweighting protected-surface successor schema mismatch'
}

if ([string]$LightweightingSuccessor.authority -cne 'repository_owner_user') {
    throw 'repository lightweighting protected-surface successor authority mismatch'
}
if ([string]$EvidenceLightweightingSuccessor.schema_version -cne 'iris_repository_evidence_lightweighting_protected_surface_successor_v1') {
    throw 'repository evidence lightweighting protected-surface successor schema mismatch'
}
if ([string]$EvidenceLightweightingSuccessor.authority -cne 'repository_owner_user') {
    throw 'repository evidence lightweighting protected-surface successor authority mismatch'
}
$EvidenceProtectionPredecessor = $EvidenceLightweightingSuccessor.protection_predecessor
if (
    [string]$EvidenceProtectionPredecessor.commit -notmatch '^[0-9a-f]{40}$' -or
    [string]$EvidenceProtectionPredecessor.tree -notmatch '^[0-9a-f]{40}$' -or
    [string]$EvidenceProtectionPredecessor.path -cne $LightweightingSuccessorRelative -or
    [string]$EvidenceProtectionPredecessor.git_blob_id -cne $LightweightingSuccessorBlob
) {
    throw 'repository evidence lightweighting protection predecessor identity mismatch'
}
$EvidenceProtectionPredecessorTree = (& git -C $RepositoryRoot rev-parse ([string]$EvidenceProtectionPredecessor.commit + '^{tree}')).Trim()
if ($LASTEXITCODE -ne 0 -or $EvidenceProtectionPredecessorTree -cne [string]$EvidenceProtectionPredecessor.tree) {
    throw 'repository evidence lightweighting protection predecessor tree mismatch'
}
& git -C $RepositoryRoot merge-base --is-ancestor ([string]$EvidenceProtectionPredecessor.commit) HEAD 2>$null
if ($LASTEXITCODE -ne 0) {
    throw 'repository evidence lightweighting protection predecessor is not an ancestor'
}
$HistoricalAttestation = $LightweightingSuccessor.historical_manifest_attestation
$HistoricalValidation = Assert-HistoricalManifestAttestation $HistoricalAttestation $LightweightingSuccessorRelative
$HistoricalCommit = [string]$HistoricalValidation.commit
$HistoricalTree = [string]$HistoricalValidation.tree
$HistoricalBlob = [string]$HistoricalValidation.blob
$HistoricalSuccessor = $HistoricalValidation.payload
$CanonicalProtectedRelative = 'Iris/_docs/refactor/residual_refactor/phase0_protected_surface_manifest.json'
$CanonicalProtectedPath = Join-Path $RepositoryRoot $CanonicalProtectedRelative
$CanonicalProtectedBlob = (& git -C $RepositoryRoot rev-parse ("HEAD:" + $CanonicalProtectedRelative)).Trim()
$CanonicalProtectedWorkingBlob = (& git -C $RepositoryRoot hash-object ("--path=" + $CanonicalProtectedRelative) $CanonicalProtectedPath).Trim()
if (
    [string]$HistoricalSuccessor.predecessor.path -cne $CanonicalProtectedRelative -or
    $LASTEXITCODE -ne 0 -or
    [string]$HistoricalSuccessor.predecessor.git_blob_id -cne $CanonicalProtectedBlob -or
    $CanonicalProtectedWorkingBlob -cne $CanonicalProtectedBlob -or
    [string]$HistoricalSuccessor.predecessor.sha256_lf -cne (Get-LfTextHashOrNull $CanonicalProtectedPath)
) {
    throw 'repository lightweighting protected-surface predecessor identity mismatch'
}
$HistoricalRevisions = @($HistoricalSuccessor.revisions)
if ($HistoricalRevisions.Count -eq 0) {
    throw 'repository lightweighting attested historical manifest has no revisions'
}
$ActiveProtectionAnchor = $LightweightingSuccessor.active_protection_anchor
if (
    [string]$ActiveProtectionAnchor.commit -notmatch '^[0-9a-f]{40}$' -or
    [string]$ActiveProtectionAnchor.tree -notmatch '^[0-9a-f]{40}$' -or
    [string]$ActiveProtectionAnchor.state_source -cne 'folded_v1_final_rows'
) {
    throw 'repository lightweighting active protection anchor invalid'
}
$AnchorCommit = [string]$ActiveProtectionAnchor.commit
$AnchorTree = (& git -C $RepositoryRoot rev-parse ($AnchorCommit + '^{tree}')).Trim()
if ($LASTEXITCODE -ne 0 -or $AnchorTree -cne [string]$ActiveProtectionAnchor.tree) {
    throw 'repository lightweighting active protection anchor tree mismatch'
}
& git -C $RepositoryRoot merge-base --is-ancestor $AnchorCommit HEAD 2>$null
if ($LASTEXITCODE -ne 0) {
    throw 'repository lightweighting active protection anchor is not an ancestor'
}
$EvidenceActiveRevisions = @($EvidenceLightweightingSuccessor.active_revisions)
if ($EvidenceActiveRevisions.Count -eq 0) {
    throw 'repository evidence lightweighting protected-surface successor has no active revisions'
}
$ActiveRevisions = @($LightweightingSuccessor.active_revisions) + @($EvidenceActiveRevisions)
if ($ActiveRevisions.Count -eq 0) {
    throw 'repository lightweighting protected-surface successor has no active revisions'
}
$LightweightingRevisions = @($HistoricalRevisions) + @($ActiveRevisions)

$ModuleFiles = @{
    'Iris/IrisAPI' = 'Iris/media/lua/client/Iris/IrisAPI.lua'
    'Iris/API/Description' = 'Iris/media/lua/client/Iris/API/Description.lua'
    'Iris/API/UseCases' = 'Iris/media/lua/client/Iris/API/UseCases.lua'
    'Iris/UI/Browser/IrisBrowserData' = 'Iris/media/lua/client/Iris/UI/Browser/IrisBrowserData.lua'
    'Iris/UI/Wiki/IrisWikiSections' = 'Iris/media/lua/client/Iris/UI/Wiki/IrisWikiSections.lua'
    'Iris/UI/Wiki/IrisWikiPanel' = 'Iris/media/lua/client/Iris/UI/Wiki/IrisWikiPanel.lua'
    'Iris/UI/Browser/IrisBrowser' = 'Iris/media/lua/client/Iris/UI/Browser/IrisBrowser.lua'
    'Iris/Data/IrisData' = 'Iris/media/lua/client/Iris/Data/IrisData.lua'
    'generated runtime global' = 'Iris/media/lua/client/Iris/Data/IrisClassifications.lua'
}
$SurfaceRows = @()
$Incompatible = 0
foreach ($Surface in $SupportedBaseline.surfaces) {
    $ModulePath = [string]$Surface.module_path
    $RelativeFile = $ModuleFiles[$ModulePath]
    $Exists = $false
    if ($RelativeFile) {
        $Exists = Test-Path -LiteralPath (Join-Path $RepositoryRoot $RelativeFile) -PathType Leaf
    }
    if (-not $Exists -and $ModulePath -eq 'generated runtime global') {
        $PrimarySource = Join-Path $RepositoryRoot 'Iris/media/lua/client/Iris/Data/IrisClassifications.lua'
        $Exists = Test-Path -LiteralPath $PrimarySource -PathType Leaf
    }
    $Status = if ($Exists) { 'compatible' } else { 'incompatible' }
    if (-not $Exists) { $Incompatible += 1 }
    $SurfaceRows += [ordered]@{
        symbol = [string]$Surface.symbol
        module_path = $ModulePath
        status = $Status
        identity_delta = if ([string]$Surface.symbol -in @('IrisAPI.getTags','IrisAPI.getUseCaseLines','IrisAPI.getOutcomes','IrisAPI.getCapabilities')) { 'copy_on_read_only' } else { 'none' }
    }
}
$SupportedReport = [ordered]@{
    schema_version = 'iris-residual-supported-api-report-v1'
    validation_status = if ($Incompatible -eq 0) { 'passed' } else { 'failed' }
    claim_boundary = 'predecessor_20_listed_surfaces_only'
    baseline_manifest = Get-Relative $SupportedBaselinePath
    baseline_manifest_sha256 = Get-HashOrNull $SupportedBaselinePath
    surface_count = $SurfaceRows.Count
    incompatible_count = $Incompatible
    surfaces = $SurfaceRows
}
Write-Json (Join-Path $EvidenceRoot 'final_supported_api_compatibility_report.json') $SupportedReport

$ProtectedRows = @()
$Unauthorized = 0
$AuthorizedChanged = 0
$AuthorizedAdded = 0
$ApprovedDeltas = @{}
$AddedProtectedRows = @{}
$RemovedProtectedRows = @{}
$BaselineProtectedRows = @{}
foreach ($Row in @($ProtectedBaseline.rows)) {
    $RowPath = [string]$Row.path
    if ($BaselineProtectedRows.ContainsKey($RowPath)) { throw "duplicate protected baseline row: $RowPath" }
    $BaselineProtectedRows[$RowPath] = $Row
}
foreach ($Delta in @($ProtectedBaseline.approved_activation_deltas)) {
    $DeltaPath = [string]$Delta.path
    if ($ApprovedDeltas.ContainsKey($DeltaPath)) { throw "duplicate protected baseline delta: $DeltaPath" }
    $ApprovedDeltas[$DeltaPath] = $Delta
}
$ApprovedDeltaPayload = Get-Content -LiteralPath $ApprovedDeltaManifestPath -Raw | ConvertFrom-Json
if ([string]$ApprovedDeltaPayload.schema_version -cne 'iris-residual-protected-surface-delta-v1') {
    throw 'approved protected-surface delta schema mismatch'
}
if ([string]$ApprovedDeltaPayload.authority -cne 'repository_owner') {
    throw 'approved protected-surface delta authority mismatch'
}
$SuccessorApprovedDeltaRows = @($ApprovedDeltaPayload.approved_activation_deltas)
if ($SuccessorApprovedDeltaRows.Count -eq 0) {
    throw 'approved protected-surface delta manifest is empty'
}
foreach ($Delta in $SuccessorApprovedDeltaRows) {
    $DeltaPath = [string]$Delta.path
    if (
        -not ($Delta.PSObject.Properties.Name -contains 'expected_git_blob_id') -or
        [string]::IsNullOrWhiteSpace([string]$Delta.expected_git_blob_id)
    ) {
        throw "approved protected-surface delta Git blob missing: $DeltaPath"
    }
    if ([string]$Delta.after_sha256_lf -notmatch '^[0-9a-f]{64}$') {
        throw "approved protected-surface delta LF hash invalid: $DeltaPath"
    }
    if ($ApprovedDeltas.ContainsKey($DeltaPath)) {
        throw "offline approved protected-surface delta duplicates predecessor authority: $DeltaPath"
    }
    $ApprovedDeltas[$DeltaPath] = $Delta
}
$SeenRevisionIds = @{}
$LightweightingDeltaPaths = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::Ordinal)
$LastRevisionPredecessor = $AnchorCommit
$AnchorStateVerified = $false
$RevisionEntries = @()
foreach ($HistoricalRevision in $HistoricalRevisions) {
    $RevisionEntries += [pscustomobject]@{ active = $false; revision = $HistoricalRevision }
}
foreach ($ActiveRevision in $ActiveRevisions) {
    $RevisionEntries += [pscustomobject]@{ active = $true; revision = $ActiveRevision }
}
foreach ($RevisionEntry in $RevisionEntries) {
    $Revision = $RevisionEntry.revision
    $IsActiveRevision = [bool]$RevisionEntry.active
    if ($IsActiveRevision -and -not $AnchorStateVerified) {
        foreach ($DeltaPath in $LightweightingDeltaPaths) {
            $Delta = $ApprovedDeltas[$DeltaPath]
            $AnchorBlob = (& git -C $RepositoryRoot rev-parse ($AnchorCommit + ':' + $DeltaPath)).Trim()
            if ($LASTEXITCODE -ne 0 -or $AnchorBlob -cne [string]$Delta.expected_git_blob_id) {
                throw "repository lightweighting active anchor delta Git blob mismatch: $DeltaPath"
            }
            if ((Get-GitBlobLfHash $AnchorBlob) -cne [string]$Delta.after_sha256_lf) {
                throw "repository lightweighting active anchor delta LF hash mismatch: $DeltaPath"
            }
        }
        foreach ($Entry in $AddedProtectedRows.GetEnumerator()) {
            $Added = $Entry.Value
            $AddedPath = [string]$Added.path
            $AnchorBlob = (& git -C $RepositoryRoot rev-parse ($AnchorCommit + ':' + $AddedPath)).Trim()
            if ($LASTEXITCODE -ne 0 -or $AnchorBlob -cne [string]$Added.expected_git_blob_id) {
                throw "repository lightweighting active anchor added-row Git blob mismatch: $AddedPath"
            }
            if ((Get-GitBlobLfHash $AnchorBlob) -cne [string]$Added.after_sha256_lf) {
                throw "repository lightweighting active anchor added-row LF hash mismatch: $AddedPath"
            }
        }
        $AnchorStateVerified = $true
    }
    $RevisionId = [string]$Revision.revision_id
    if ([string]::IsNullOrWhiteSpace($RevisionId) -or $SeenRevisionIds.ContainsKey($RevisionId)) {
        throw "repository lightweighting protected-surface revision identity invalid: $RevisionId"
    }
    $SeenRevisionIds[$RevisionId] = $true
    if ($Revision.approved -ne $true -or [string]$Revision.owner -cne 'repository_owner_user') {
        throw "repository lightweighting protected-surface revision approval invalid: $RevisionId"
    }
    if ($IsActiveRevision) {
        if ($Revision.PSObject.Properties.Name -contains 'predecessor_commit') {
            throw "repository lightweighting active revision uses ambiguous predecessor field: $RevisionId"
        }
        $RevisionPredecessor = [string]$Revision.protection_predecessor_commit
        $RevisionPredecessorTree = [string]$Revision.protection_predecessor_tree
        if (
            $RevisionPredecessor -notmatch '^[0-9a-f]{40}$' -or
            $RevisionPredecessorTree -notmatch '^[0-9a-f]{40}$'
        ) {
            throw "repository lightweighting active revision predecessor identity invalid: $RevisionId"
        }
        $ActualRevisionTree = (& git -C $RepositoryRoot rev-parse ($RevisionPredecessor + '^{tree}')).Trim()
        if ($LASTEXITCODE -ne 0 -or $ActualRevisionTree -cne $RevisionPredecessorTree) {
            throw "repository lightweighting active revision predecessor tree mismatch: $RevisionId"
        }
        $HasEvidenceCommit = $Revision.PSObject.Properties.Name -contains 'evidence_subject_commit'
        $HasEvidenceTree = $Revision.PSObject.Properties.Name -contains 'evidence_subject_tree'
        if ($HasEvidenceCommit -ne $HasEvidenceTree) {
            throw "repository lightweighting active revision evidence subject pair mismatch: $RevisionId"
        }
        if (
            $HasEvidenceCommit -and
            (
                [string]$Revision.evidence_subject_commit -notmatch '^[0-9a-f]{40}$' -or
                [string]$Revision.evidence_subject_tree -notmatch '^[0-9a-f]{40}$'
            )
        ) {
            throw "repository lightweighting active revision evidence subject format invalid: $RevisionId"
        }
    }
    else {
        $RevisionPredecessor = [string]$Revision.predecessor_commit
    }
    if ($RevisionPredecessor -notmatch '^[0-9a-f]{40}$') {
        throw "repository lightweighting revision predecessor invalid: $RevisionId"
    }
    if ($IsActiveRevision) {
        & git -C $RepositoryRoot merge-base --is-ancestor $RevisionPredecessor HEAD 2>$null
        if ($LASTEXITCODE -ne 0) {
            throw "repository lightweighting revision predecessor is not an ancestor: $RevisionId"
        }
        & git -C $RepositoryRoot merge-base --is-ancestor $LastRevisionPredecessor $RevisionPredecessor 2>$null
        if ($LASTEXITCODE -ne 0) {
            throw "repository lightweighting revision predecessor regressed: $RevisionId"
        }
        $LastRevisionPredecessor = $RevisionPredecessor
    }
    foreach ($Delta in @($Revision.approved_activation_deltas)) {
        $DeltaPath = [string]$Delta.path
        if (-not $BaselineProtectedRows.ContainsKey($DeltaPath)) {
            throw "repository lightweighting delta path is absent from predecessor rows: $DeltaPath"
        }
        if (
            [string]$Delta.expected_git_blob_id -notmatch '^[0-9a-f]{40,64}$' -or
            [string]$Delta.after_sha256_lf -notmatch '^[0-9a-f]{64}$' -or
            [string]$Delta.before_git_blob_id -notmatch '^[0-9a-f]{40,64}$' -or
            [string]$Delta.before_sha256_lf -notmatch '^[0-9a-f]{64}$'
        ) {
            throw "repository lightweighting delta identity invalid: $DeltaPath"
        }
        if ($IsActiveRevision) {
            $BeforeBlob = (& git -C $RepositoryRoot rev-parse ($RevisionPredecessor + ':' + $DeltaPath)).Trim()
            if ($LASTEXITCODE -ne 0 -or $BeforeBlob -cne [string]$Delta.before_git_blob_id) {
                throw "repository lightweighting delta predecessor Git blob mismatch: $DeltaPath"
            }
            if ((Get-GitBlobLfHash $BeforeBlob) -cne [string]$Delta.before_sha256_lf) {
                throw "repository lightweighting delta predecessor LF hash mismatch: $DeltaPath"
            }
        }
        if ($ApprovedDeltas.ContainsKey($DeltaPath)) {
            $PriorAfter = [string]$ApprovedDeltas[$DeltaPath].after_sha256_lf
            if ([string]$Delta.before_sha256_lf -cne $PriorAfter) {
                throw "repository lightweighting delta chain mismatch: $DeltaPath"
            }
            if (
                $LightweightingDeltaPaths.Contains($DeltaPath) -and
                [string]$Delta.before_git_blob_id -cne [string]$ApprovedDeltas[$DeltaPath].expected_git_blob_id
            ) {
                throw "repository lightweighting delta Git blob chain mismatch: $DeltaPath"
            }
        }
        elseif ([string]$Delta.predecessor_sha256 -cne [string]$BaselineProtectedRows[$DeltaPath].sha256) {
            throw "repository lightweighting delta predecessor mismatch: $DeltaPath"
        }
        $ApprovedDeltas[$DeltaPath] = $Delta
        [void]$LightweightingDeltaPaths.Add($DeltaPath)
    }
    foreach ($Added in @($Revision.added_protected_rows)) {
        $AddedPath = [string]$Added.path
        if ($BaselineProtectedRows.ContainsKey($AddedPath) -or $ApprovedDeltas.ContainsKey($AddedPath)) {
            throw "repository lightweighting added row overlaps predecessor surface: $AddedPath"
        }
        if (
            [string]$Added.expected_git_blob_id -notmatch '^[0-9a-f]{40,64}$' -or
            [string]$Added.after_sha256_lf -notmatch '^[0-9a-f]{64}$' -or
            -not ($Added.PSObject.Properties.Name -contains 'before_sha256_lf') -or
            ($null -ne $Added.before_sha256_lf -and [string]$Added.before_sha256_lf -notmatch '^[0-9a-f]{64}$') -or
            [string]::IsNullOrWhiteSpace([string]$Added.role) -or
            [string]::IsNullOrWhiteSpace([string]$Added.writer) -or
            [string]::IsNullOrWhiteSpace([string]$Added.reason) -or
            @($Added.consumers).Count -eq 0
        ) {
            throw "repository lightweighting added row identity invalid: $AddedPath"
        }
        $BeforeGitIsNull = $null -eq $Added.before_git_blob_id
        $BeforeLfIsNull = $null -eq $Added.before_sha256_lf
        if ($BeforeGitIsNull -ne $BeforeLfIsNull) {
            throw "repository lightweighting added row predecessor identity pair mismatch: $AddedPath"
        }
        if ($IsActiveRevision) {
            $BeforeTreeRows = @(& git -C $RepositoryRoot ls-tree $RevisionPredecessor -- $AddedPath)
            $BeforeTreeEntry = ($BeforeTreeRows -join "`n").Trim()
            if ($LASTEXITCODE -ne 0) {
                throw "repository lightweighting added row predecessor tree inspection failed: $AddedPath"
            }
            $BeforeBlob = if ([string]::IsNullOrWhiteSpace($BeforeTreeEntry)) {
                $null
            }
            else {
                @($BeforeTreeEntry -split '\s+', 4)[2]
            }
            if ($BeforeGitIsNull) {
                if ($null -ne $BeforeBlob) {
                    throw "repository lightweighting new row unexpectedly exists in predecessor: $AddedPath"
                }
            }
            elseif (
                [string]$Added.before_git_blob_id -notmatch '^[0-9a-f]{40,64}$' -or
                $LASTEXITCODE -ne 0 -or
                $BeforeBlob -cne [string]$Added.before_git_blob_id
            ) {
                throw "repository lightweighting added row predecessor Git blob mismatch: $AddedPath"
            }
            elseif ((Get-GitBlobLfHash $BeforeBlob) -cne [string]$Added.before_sha256_lf) {
                throw "repository lightweighting added row predecessor LF hash mismatch: $AddedPath"
            }
        }
        if ($AddedProtectedRows.ContainsKey($AddedPath)) {
            $PriorAddedAfter = [string]$AddedProtectedRows[$AddedPath].after_sha256_lf
            if ([string]$Added.before_sha256_lf -cne $PriorAddedAfter) {
                throw "repository lightweighting added row chain mismatch: $AddedPath"
            }
            if ([string]$Added.before_git_blob_id -cne [string]$AddedProtectedRows[$AddedPath].expected_git_blob_id) {
                throw "repository lightweighting added row Git blob chain mismatch: $AddedPath"
            }
        }
        $AddedProtectedRows[$AddedPath] = $Added
        if ($RemovedProtectedRows.ContainsKey($AddedPath)) {
            $RemovedProtectedRows.Remove($AddedPath)
        }
    }
    foreach ($Removed in @($Revision.removed_protected_rows)) {
        $RemovedPath = [string]$Removed.path
        if (
            [string]$Removed.before_git_blob_id -notmatch '^[0-9a-f]{40,64}$' -or
            [string]$Removed.before_sha256_lf -notmatch '^[0-9a-f]{64}$' -or
            [string]$Removed.owner -cne 'repository_owner_user' -or
            [string]::IsNullOrWhiteSpace([string]$Removed.reason)
        ) {
            throw "repository lightweighting removed row identity invalid: $RemovedPath"
        }
        if (-not $AddedProtectedRows.ContainsKey($RemovedPath)) {
            throw "repository lightweighting removed row is not an active added row: $RemovedPath"
        }
        $PriorAdded = $AddedProtectedRows[$RemovedPath]
        if (
            [string]$Removed.before_git_blob_id -cne [string]$PriorAdded.expected_git_blob_id -or
            [string]$Removed.before_sha256_lf -cne [string]$PriorAdded.after_sha256_lf
        ) {
            throw "repository lightweighting removed row chain mismatch: $RemovedPath"
        }
        if ($IsActiveRevision) {
            $BeforeBlob = (& git -C $RepositoryRoot rev-parse ($RevisionPredecessor + ':' + $RemovedPath)).Trim()
            if ($LASTEXITCODE -ne 0 -or $BeforeBlob -cne [string]$Removed.before_git_blob_id) {
                throw "repository lightweighting removed row predecessor Git blob mismatch: $RemovedPath"
            }
            if ((Get-GitBlobLfHash $BeforeBlob) -cne [string]$Removed.before_sha256_lf) {
                throw "repository lightweighting removed row predecessor LF hash mismatch: $RemovedPath"
            }
        }
        $AddedProtectedRows.Remove($RemovedPath)
        $RemovedProtectedRows[$RemovedPath] = $Removed
    }
}
if (-not $AnchorStateVerified) {
    throw 'repository lightweighting active protection anchor was not verified'
}
foreach ($DeltaPath in $LightweightingDeltaPaths) {
    $Delta = $ApprovedDeltas[$DeltaPath]
    $ActualBlob = (& git -C $RepositoryRoot rev-parse ("HEAD:" + $DeltaPath)).Trim()
    if ($LASTEXITCODE -ne 0 -or $ActualBlob -cne [string]$Delta.expected_git_blob_id) {
        throw "repository lightweighting final delta Git blob mismatch: $DeltaPath"
    }
    if ((Get-LfTextHashOrNull (Join-Path $RepositoryRoot $DeltaPath)) -cne [string]$Delta.after_sha256_lf) {
        throw "repository lightweighting final delta LF hash mismatch: $DeltaPath"
    }
}
foreach ($Entry in $AddedProtectedRows.GetEnumerator()) {
    $Added = $Entry.Value
    $AddedPath = [string]$Added.path
    $ActualBlob = (& git -C $RepositoryRoot rev-parse ("HEAD:" + $AddedPath)).Trim()
    if ($LASTEXITCODE -ne 0 -or $ActualBlob -cne [string]$Added.expected_git_blob_id) {
        throw "repository lightweighting final added-row Git blob mismatch: $AddedPath"
    }
    if ((Get-LfTextHashOrNull (Join-Path $RepositoryRoot $AddedPath)) -cne [string]$Added.after_sha256_lf) {
        throw "repository lightweighting final added-row LF hash mismatch: $AddedPath"
    }
}
foreach ($RemovedPath in $RemovedProtectedRows.Keys) {
    & git -C $RepositoryRoot cat-file -e ("HEAD:" + [string]$RemovedPath) 2>$null
    if ($LASTEXITCODE -eq 0 -or (Test-Path -LiteralPath (Join-Path $RepositoryRoot ([string]$RemovedPath)))) {
        throw "repository lightweighting removed row unexpectedly exists: $RemovedPath"
    }
}
foreach ($Row in $ProtectedBaseline.rows) {
    $RowPath = [string]$Row.path
    $FullPath = Join-Path $RepositoryRoot $RowPath
    $After = Get-HashOrNull $FullPath
    $Before = if ($null -eq $Row.sha256) { $null } else { [string]$Row.sha256 }
    $RawChanged = if ($null -eq $Before -and $null -eq $After) { $false } else { $After -cne $Before }
    $LineEndingEquivalent = $false
    if ($RawChanged -and $null -ne $Before -and $null -ne $After) {
        $LineEndingEquivalent = Test-LineEndingEquivalent $FullPath $Before
    }
    $OptionalProjectionAbsent = (
        $RawChanged -and
        $null -ne $Before -and
        $null -eq $After -and
        $Row.tracked -eq $false -and
        [string]$Row.hash_policy -eq 'read_only_pre_post'
    )
    $Changed = $RawChanged -and -not $LineEndingEquivalent -and -not $OptionalProjectionAbsent
    $AfterLf = Get-LfTextHashOrNull $FullPath
    $Authorized = (
        $Changed -and
        $ApprovedDeltas.ContainsKey($RowPath) -and
        $AfterLf -ceq [string]$ApprovedDeltas[$RowPath].after_sha256_lf
    )
    if ($Authorized) { $AuthorizedChanged += 1 }
    elseif ($Changed) { $Unauthorized += 1 }
    $ProtectedRows += [ordered]@{
        path = $RowPath
        before_sha256 = $Before
        after_sha256 = $After
        after_sha256_lf = $AfterLf
        raw_changed = $RawChanged
        line_ending_equivalent = $LineEndingEquivalent
        optional_untracked_projection_absent = $OptionalProjectionAbsent
        changed = $Changed
        authorized = $Authorized
        authorization_owner = if ($Authorized) { [string]$ApprovedDeltas[$RowPath].owner } else { $null }
        authorization_reason = if ($Authorized) { [string]$ApprovedDeltas[$RowPath].reason } else { $null }
    }
}
foreach ($Entry in @($AddedProtectedRows.GetEnumerator() | Sort-Object Key)) {
    $Added = $Entry.Value
    $AddedPath = [string]$Added.path
    $FullPath = Join-Path $RepositoryRoot $AddedPath
    $After = Get-HashOrNull $FullPath
    $AfterLf = Get-LfTextHashOrNull $FullPath
    $BeforeLf = if ($null -eq $Added.before_sha256_lf) { $null } else { [string]$Added.before_sha256_lf }
    $AuthorizedAdded += 1
    $ProtectedRows += [ordered]@{
        path = $AddedPath
        before_sha256 = $null
        before_sha256_lf = $BeforeLf
        after_sha256 = $After
        after_sha256_lf = $AfterLf
        raw_changed = $true
        line_ending_equivalent = $false
        optional_untracked_projection_absent = $false
        changed = $true
        authorized = $true
        authorized_addition = $true
        role = [string]$Added.role
        writer = [string]$Added.writer
        consumers = @($Added.consumers)
        authorization_owner = [string]$Added.owner
        authorization_reason = [string]$Added.reason
        expected_git_blob_id = [string]$Added.expected_git_blob_id
    }
}
$ProtectedReport = [ordered]@{
    schema_version = 'iris-residual-protected-surface-report-v1'
    validation_status = if ($Unauthorized -eq 0) { 'passed' } else { 'failed' }
    baseline_manifest = Get-Relative $ProtectedBaselinePath
    baseline_manifest_sha256 = Get-HashOrNull $ProtectedBaselinePath
    approved_delta_manifest = Get-Relative $ApprovedDeltaManifestPath
    approved_delta_manifest_git_blob_id = $ApprovedDeltaManifestBlob
    approved_delta_manifest_sha256 = Get-HashOrNull $ApprovedDeltaManifestPath
    repository_lightweighting_successor_manifest = $LightweightingSuccessorRelative
    repository_lightweighting_successor_git_blob_id = $LightweightingSuccessorBlob
    repository_lightweighting_successor_sha256 = Get-HashOrNull $LightweightingSuccessorPath
    repository_lightweighting_successor_schema_version = [string]$LightweightingSuccessor.schema_version
    repository_evidence_lightweighting_successor_manifest = $EvidenceLightweightingSuccessorRelative
    repository_evidence_lightweighting_successor_git_blob_id = $EvidenceLightweightingSuccessorBlob
    repository_evidence_lightweighting_successor_sha256 = Get-HashOrNull $EvidenceLightweightingSuccessorPath
    repository_evidence_lightweighting_successor_schema_version = [string]$EvidenceLightweightingSuccessor.schema_version
    historical_manifest_attestation = [ordered]@{
        commit = $HistoricalCommit
        tree = $HistoricalTree
        git_blob_id = $HistoricalBlob
        sha256_lf = [string]$HistoricalAttestation.sha256_lf
        interpretation = [string]$HistoricalAttestation.interpretation
    }
    historical_subject_object_dereference_count = 0
    active_protection_anchor = [ordered]@{
        commit = $AnchorCommit
        tree = $AnchorTree
        state_source = [string]$ActiveProtectionAnchor.state_source
        final_state_verified = $AnchorStateVerified
    }
    historical_revision_ids = @($HistoricalRevisions | ForEach-Object { [string]$_.revision_id })
    active_revision_ids = @($ActiveRevisions | ForEach-Object { [string]$_.revision_id })
    repository_lightweighting_revision_ids = @($LightweightingRevisions | ForEach-Object { [string]$_.revision_id })
    removed_protected_paths = @($RemovedProtectedRows.Keys | Sort-Object)
    changed_count = @($ProtectedRows | Where-Object changed).Count
    authorized_changed_count = $AuthorizedChanged
    authorized_added_count = $AuthorizedAdded
    unauthorized_changed_count = $Unauthorized
    rows = $ProtectedRows
}
Write-Json (Join-Path $EvidenceRoot 'final_protected_surface_report.json') $ProtectedReport

$CandidateRoot = Join-Path ([System.IO.Path]::GetTempPath()) ('iris-residual-package-' + [guid]::NewGuid().ToString('N'))
$ExistingPackageBefore = @(Get-TreeRows (Join-Path $RepositoryRoot 'Iris/build/package'))
try {
    & powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $RepositoryRoot 'Iris/tools/package_iris.ps1') -OutputRoot $CandidateRoot
    if ($LASTEXITCODE -ne 0) { throw "package_iris.ps1 failed: $LASTEXITCODE" }
    $CandidateIris = Join-Path $CandidateRoot 'Iris'
    $CandidateRows = @(Get-TreeRows $CandidateIris)
    $SourceLuaRoot = Join-Path $RepositoryRoot 'Iris/media/lua/client/Iris'
    $CandidateLuaRoot = Join-Path $CandidateIris 'media/lua/client/Iris'
    $SourceLuaRows = @(Get-TreeRows $SourceLuaRoot | Where-Object { $_.path.EndsWith('.lua') })
    $CandidateLuaRows = @(Get-TreeRows $CandidateLuaRoot | Where-Object { $_.path.EndsWith('.lua') })
    $SourceIdentity = @($SourceLuaRows | ForEach-Object { "$($_.path)`t$($_.sha256)" }) -join "`n"
    $CandidateIdentity = @($CandidateLuaRows | ForEach-Object { "$($_.path)`t$($_.sha256)" }) -join "`n"
    $PackageEqual = $SourceIdentity -ceq $CandidateIdentity
    $ExistingPackageAfter = @(Get-TreeRows (Join-Path $RepositoryRoot 'Iris/build/package'))
    $ExistingUnchanged = (@($ExistingPackageBefore | ConvertTo-Json -Depth 10) -join '') -ceq (@($ExistingPackageAfter | ConvertTo-Json -Depth 10) -join '')
    $PackageReport = [ordered]@{
        schema_version = 'iris-residual-package-identity-report-v1'
        validation_status = if ($PackageEqual -and $ExistingUnchanged) { 'passed' } else { 'failed' }
        disposable_candidate_lua_count = $CandidateLuaRows.Count
        source_lua_count = $SourceLuaRows.Count
        source_candidate_identity_equal = $PackageEqual
        candidate_lua_identity_sha256 = Get-TextSha256 $CandidateIdentity
        existing_package_peer_unchanged = $ExistingUnchanged
        candidate_cleanup_status = 'pending_finally'
        writer_target_policy = 'existing package peer is never a writer target'
    }
    Write-Json (Join-Path $EvidenceRoot 'final_package_identity_report.json') $PackageReport
}
finally {
    if (Test-Path -LiteralPath $CandidateRoot) {
        Remove-Item -LiteralPath $CandidateRoot -Recurse -Force -ErrorAction SilentlyContinue
    }
    if (Test-Path -LiteralPath $CandidateRoot) { throw "candidate cleanup failed: $CandidateRoot" }
}

$PackageReportPath = Join-Path $EvidenceRoot 'final_package_identity_report.json'
$PackageReportFinal = Get-Content -LiteralPath $PackageReportPath -Raw | ConvertFrom-Json
$PackageReportFinal.candidate_cleanup_status = 'passed_removed'
Write-Json $PackageReportPath $PackageReportFinal
$ClaimBoundary = [ordered]@{
    schema_version = 'iris-residual-claim-boundary-v1'
    validation_status = if (
        $SupportedReport.validation_status -eq 'passed' -and
        $ProtectedReport.validation_status -eq 'passed' -and
        $PackageReportFinal.validation_status -eq 'passed'
    ) { 'passed' } else { 'failed' }
    claims = @('listed supported surfaces compatible','protected surfaces unchanged','disposable package equals source Lua projection')
    non_claims = @('release readiness','Workshop readiness','B42 readiness','unlisted external consumer compatibility','manual Project Zomboid runtime validation')
}
Write-Json (Join-Path $EvidenceRoot 'final_claim_boundary_report.json') $ClaimBoundary
if ($ClaimBoundary.validation_status -ne 'passed') { throw 'residual surface Closeout failed' }
Write-Output "residual surface Closeout PASS: supported=$($SurfaceRows.Count) protected=$($ProtectedRows.Count) package_lua=$($PackageReportFinal.disposable_candidate_lua_count)"
