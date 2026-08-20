[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateSet('Baseline', 'Closeout', 'AttestationProbe', 'OverlayDispositionProbe')]
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

function Get-FileHash {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)][string]$LiteralPath,
        [ValidateSet('SHA256')][string]$Algorithm = 'SHA256'
    )

    $hasher = [System.Security.Cryptography.SHA256]::Create()
    $stream = $null
    try {
        $stream = [System.IO.File]::OpenRead($LiteralPath)
        $hash = $hasher.ComputeHash($stream)
        return [pscustomobject]@{ Algorithm = $Algorithm; Hash = ([System.BitConverter]::ToString($hash)).Replace('-', '').ToLowerInvariant(); Path = $LiteralPath }
    }
    finally {
        if ($null -ne $stream) { $stream.Dispose() }
        $hasher.Dispose()
    }
}

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

function Get-FollowupOverlayDisposition(
    [bool]$Exists,
    [AllowNull()][string]$TrackedBlob,
    [AllowNull()][string]$WorkingBlob
) {
    if (-not $Exists) { return 'absent' }
    if (
        -not [string]::IsNullOrWhiteSpace($TrackedBlob) -and
        $WorkingBlob -ceq $TrackedBlob
    ) { return 'tracked_historical_evidence' }
    return 'active_working_overlay'
}

function Get-CodebaseOverlayRowDisposition(
    [bool]$HeadMatchesBefore,
    [bool]$HeadMatchesAfterLf,
    [bool]$WorkingMatchesAfterLf
) {
    if ($HeadMatchesBefore -and $WorkingMatchesAfterLf) { return 'active_working_overlay' }
    if ($HeadMatchesAfterLf) { return 'tracked_historical_evidence' }
    return 'blocked'
}

function Get-ProtectedWorkingDriftDisposition([bool]$MatchesExpectedLf) {
    if ($MatchesExpectedLf) { return 'clean' }
    return 'blocked'
}

function Get-ProtectedChangeAuthorizationDisposition(
    [bool]$Changed,
    [bool]$OverlayAfterMatches,
    [bool]$DurableDeltaAfterMatches
) {
    if (-not $Changed) { return 'unchanged' }
    if ($OverlayAfterMatches -or $DurableDeltaAfterMatches) { return 'authorized' }
    return 'unauthorized'
}

$ItemPageApprovedBaseCommit = '8a11894b9352752e81d2059feb7b5ef67cfe18a4'
$ItemPageApprovedBaseTree = 'ea20a31e40e67404f7556ff2b10d839de856eaf7'

function Get-ItemPageOverlayBaseDisposition([string]$DeclaredCommit, [string]$DeclaredTree) {
    if ($DeclaredCommit -ceq $ItemPageApprovedBaseCommit -and $DeclaredTree -ceq $ItemPageApprovedBaseTree) {
        return 'exact_approved_base'
    }
    return 'blocked'
}

function Get-ItemPageOverlayScopeDisposition([object[]]$Rows) {
    $ExpectedReasons = [System.Collections.Generic.Dictionary[string,string]]::new([System.StringComparer]::Ordinal)
    $ExpectedReasons.Add('Iris/_docs/round3/current_route_required_validations.json', 'Register the exact item-page information-sufficiency result and closeout path as current-route component evidence in the approved active-or-durable successor.')
    $ExpectedReasons.Add('Iris/_docs/round3/round3_active_core_closure.json', 'Register the approved evaluator in the exact offline-tooling closure while preserving the twelve-module current core.')
    $ExpectedReasons.Add('Iris/build/description/v2/tools/build/INVENTORY.md', 'Register the approved item-page information-sufficiency evaluator in the bounded tooling inventory without expanding runtime authority.')
    $ExpectedReasons.Add('.gitattributes', 'Preserve exact raw-byte item-page information-sufficiency policy and generated evidence identities across Windows clean checkouts.')
    $ExpectedReasons.Add('Iris/test/validate_residual_refactor_surfaces.ps1', 'Validate the plan-local active-or-durable protected successor while retaining exact predecessor and current LF and Git identities.')
    $ExpectedReasons.Add('Iris/build/description/v2/tests/test_iris_residual_contract_surfaces.py', 'Exercise the approved active and tracked-durable successor dispositions through the existing registered residual current-route test.')
    if ($Rows.Count -ne $ExpectedReasons.Count) { return 'blocked' }
    $Seen = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::Ordinal)
    foreach ($Row in $Rows) {
        $RowPath = [string]$Row.path
        if (
            -not $ExpectedReasons.ContainsKey($RowPath) -or
            -not $Seen.Add($RowPath) -or
            [string]$Row.reason -cne [string]$ExpectedReasons[$RowPath]
        ) { return 'blocked' }
    }
    return 'exact_six_path_scope'
}

function Get-ItemPageOverlayDisposition(
    [bool]$Exists,
    [AllowNull()][string]$TrackedBlob,
    [AllowNull()][string]$WorkingBlob,
    [bool]$BaseMatchesCurrentHead,
    [bool]$ApprovedBaseIsAncestorOfCurrentHead
) {
    if (-not $Exists) { return 'absent' }
    if (-not [string]::IsNullOrWhiteSpace($TrackedBlob) -and $WorkingBlob -ceq $TrackedBlob) {
        if ($ApprovedBaseIsAncestorOfCurrentHead) { return 'tracked_durable_successor' }
        return 'blocked'
    }
    if ($BaseMatchesCurrentHead) { return 'active_working_overlay' }
    return 'blocked'
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
if ($Mode -eq 'OverlayDispositionProbe') {
    $ExactRows = @(
        [pscustomobject]@{ path = 'Iris/_docs/round3/current_route_required_validations.json'; reason = 'Register the exact item-page information-sufficiency result and closeout path as current-route component evidence in the approved active-or-durable successor.' },
        [pscustomobject]@{ path = 'Iris/_docs/round3/round3_active_core_closure.json'; reason = 'Register the approved evaluator in the exact offline-tooling closure while preserving the twelve-module current core.' },
        [pscustomobject]@{ path = 'Iris/build/description/v2/tools/build/INVENTORY.md'; reason = 'Register the approved item-page information-sufficiency evaluator in the bounded tooling inventory without expanding runtime authority.' },
        [pscustomobject]@{ path = '.gitattributes'; reason = 'Preserve exact raw-byte item-page information-sufficiency policy and generated evidence identities across Windows clean checkouts.' },
        [pscustomobject]@{ path = 'Iris/test/validate_residual_refactor_surfaces.ps1'; reason = 'Validate the plan-local active-or-durable protected successor while retaining exact predecessor and current LF and Git identities.' },
        [pscustomobject]@{ path = 'Iris/build/description/v2/tests/test_iris_residual_contract_surfaces.py'; reason = 'Exercise the approved active and tracked-durable successor dispositions through the existing registered residual current-route test.' }
    )
    $Probe = [ordered]@{
        clean_tracked = Get-FollowupOverlayDisposition $true 'blob-a' 'blob-a'
        dirty_tracked = Get-FollowupOverlayDisposition $true 'blob-a' 'blob-b'
        untracked = Get-FollowupOverlayDisposition $true $null 'blob-b'
        absent = Get-FollowupOverlayDisposition $false $null $null
        clean_tracked_active_row_count = 0
        codebase_active_row = Get-CodebaseOverlayRowDisposition $true $false $true
        codebase_historical_row = Get-CodebaseOverlayRowDisposition $false $true $false
        codebase_mismatched_row = Get-CodebaseOverlayRowDisposition $false $false $true
        protected_working_match = Get-ProtectedWorkingDriftDisposition $true
        protected_working_drift = Get-ProtectedWorkingDriftDisposition $false
        protected_overlay_change = Get-ProtectedChangeAuthorizationDisposition $true $true $false
        protected_durable_change = Get-ProtectedChangeAuthorizationDisposition $true $false $true
        protected_unmatched_change = Get-ProtectedChangeAuthorizationDisposition $true $false $false
        item_page_active = Get-ItemPageOverlayDisposition $true $null 'working' $true $false
        item_page_durable = Get-ItemPageOverlayDisposition $true 'tracked' 'tracked' $false $true
        item_page_wrong_active_base = Get-ItemPageOverlayDisposition $true $null 'working' $false $false
        item_page_wrong_durable_base = Get-ItemPageOverlayDisposition $true 'tracked' 'tracked' $true $false
        item_page_durable_after_unrelated_commit = Get-ItemPageOverlayDisposition $true 'tracked' 'tracked' $false $true
        item_page_exact_base = Get-ItemPageOverlayBaseDisposition $ItemPageApprovedBaseCommit $ItemPageApprovedBaseTree
        item_page_rewritten_future_base = Get-ItemPageOverlayBaseDisposition ('f' * 40) ('e' * 40)
        item_page_exact_scope = Get-ItemPageOverlayScopeDisposition $ExactRows
        item_page_missing_scope = Get-ItemPageOverlayScopeDisposition @($ExactRows[0], $ExactRows[1], $ExactRows[2], $ExactRows[3], $ExactRows[4])
        item_page_added_scope = Get-ItemPageOverlayScopeDisposition @($ExactRows + [pscustomobject]@{ path = 'Iris/extra'; reason = 'extra' })
        item_page_substituted_scope = Get-ItemPageOverlayScopeDisposition @($ExactRows[0], $ExactRows[1], $ExactRows[2], $ExactRows[3], $ExactRows[4], [pscustomobject]@{ path = 'Iris/substitute'; reason = $ExactRows[5].reason })
        item_page_case_mutated_scope = Get-ItemPageOverlayScopeDisposition @([pscustomobject]@{ path = 'iris/_docs/round3/current_route_required_validations.json'; reason = $ExactRows[0].reason }, $ExactRows[1], $ExactRows[2], $ExactRows[3], $ExactRows[4], $ExactRows[5])
    }
    Write-Output ($Probe | ConvertTo-Json -Compress)
    exit 0
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
$FollowupOverlayRelative = 'Iris/_docs/refactor/codebase_optimization_followup/protected_surface_manifest.json'
$FollowupOverlayPath = Join-Path $RepositoryRoot $FollowupOverlayRelative
$ItemPageInformationSufficiencyOverlayRelative = 'Iris/_docs/round3/item_page_information_sufficiency/63077bf221b5af4874bbeb78fecd02708a7472564942b8e7e4d129df9a77b480/protected_surface_working_overlay.json'
$ItemPageInformationSufficiencyOverlayPath = Join-Path $RepositoryRoot $ItemPageInformationSufficiencyOverlayRelative
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
$FollowupOverlayRows = @{}
$OverlayExpectedHeadBlobs = @{}
$FollowupOverlayHistoricalPaths = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::Ordinal)
$FollowupOverlaySupersededPaths = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::Ordinal)
$FollowupOverlayTrackedBlob = $null
$FollowupOverlayWorkingBlob = $null
$FollowupOverlayDisposition = 'absent'
$FollowupOverlayIsCleanTrackedHistory = $false
if (Test-Path -LiteralPath $FollowupOverlayPath -PathType Leaf) {
    $FollowupOverlayTrackedOutput = & git -C $RepositoryRoot rev-parse ("HEAD:" + $FollowupOverlayRelative) 2>$null
    if ($LASTEXITCODE -eq 0) {
        $FollowupOverlayTrackedBlob = ([string]$FollowupOverlayTrackedOutput).Trim()
    }
    $FollowupOverlayWorkingBlob = (& git -C $RepositoryRoot hash-object ("--path=" + $FollowupOverlayRelative) $FollowupOverlayPath).Trim()
    if ($LASTEXITCODE -ne 0) {
        throw 'codebase optimization follow-up protected-surface overlay working blob could not be computed'
    }
    $FollowupOverlayDisposition = Get-FollowupOverlayDisposition $true $FollowupOverlayTrackedBlob $FollowupOverlayWorkingBlob
    $FollowupOverlayIsCleanTrackedHistory = $FollowupOverlayDisposition -ceq 'tracked_historical_evidence'
}
if (Test-Path -LiteralPath $FollowupOverlayPath -PathType Leaf) {
    $FollowupOverlay = Get-Content -LiteralPath $FollowupOverlayPath -Raw | ConvertFrom-Json
    if (
        [string]$FollowupOverlay.schema_version -cne 'iris_codebase_optimization_followup_protected_overlay_v1' -or
        [string]$FollowupOverlay.authority -cne 'repository_owner_preapproval' -or
        [string]$FollowupOverlay.plan -cne 'docs/iris_codebase_optimization_comprehensive_followup_plan.md' -or
        [string]$FollowupOverlay.implementation_state -cne 'uncommitted_working_tree_overlay'
    ) {
        throw 'codebase optimization follow-up protected-surface overlay identity mismatch'
    }
    $FollowupBaseCommit = [string]$FollowupOverlay.base_commit
    $FollowupBaseTree = (& git -C $RepositoryRoot rev-parse ($FollowupBaseCommit + '^{tree}') 2>$null | Out-String).Trim()
    if ($LASTEXITCODE -ne 0 -or $FollowupBaseTree -cne [string]$FollowupOverlay.base_tree) {
        throw 'codebase optimization follow-up protected-surface overlay base mismatch'
    }
    & git -C $RepositoryRoot merge-base --is-ancestor $FollowupBaseCommit $SubjectCommit 2>$null
    if ($LASTEXITCODE -ne 0) {
        throw 'codebase optimization follow-up protected-surface overlay base is not an ancestor'
    }
    if (
        $FollowupOverlayDisposition -ceq 'active_working_overlay' -and
        ($FollowupBaseCommit -cne $SubjectCommit -or $FollowupBaseTree -cne $SubjectTree)
    ) {
        throw 'codebase optimization follow-up active overlay does not bind current HEAD'
    }
    foreach ($Row in @($FollowupOverlay.rows)) {
        $RowPath = [string]$Row.path
        if (
            [string]::IsNullOrWhiteSpace($RowPath) -or
            [System.IO.Path]::IsPathRooted($RowPath) -or
            $RowPath -match '(^|/)\.\.(/|$)' -or
            $FollowupOverlayRows.ContainsKey($RowPath)
        ) {
            throw "codebase optimization follow-up protected row identity invalid: $RowPath"
        }
        $BaseBlob = (& git -C $RepositoryRoot rev-parse ($FollowupBaseCommit + ':' + $RowPath)).Trim()
        if ($LASTEXITCODE -ne 0 -or $BaseBlob -cne [string]$Row.before_git_blob_id) {
            throw "codebase optimization follow-up protected row base predecessor mismatch: $RowPath"
        }
        if ((Get-GitBlobLfHash $BaseBlob) -cne [string]$Row.before_sha256_lf) {
            throw "codebase optimization follow-up protected row predecessor LF hash mismatch: $RowPath"
        }
        if (
            [string]$Row.owner -cne 'repository_owner_preapproval' -or
            [string]::IsNullOrWhiteSpace([string]$Row.reason)
        ) {
            throw "codebase optimization follow-up protected row authorization invalid: $RowPath"
        }
        $HeadBlob = (& git -C $RepositoryRoot rev-parse ("HEAD:" + $RowPath)).Trim()
        if ($LASTEXITCODE -ne 0) { throw "codebase optimization follow-up protected row HEAD missing: $RowPath" }
        $HeadLf = Get-GitBlobLfHash $HeadBlob
        $WorkingLf = Get-LfTextHashOrNull (Join-Path $RepositoryRoot $RowPath)
        $RowDisposition = Get-CodebaseOverlayRowDisposition ($HeadBlob -ceq [string]$Row.before_git_blob_id) ($HeadLf -ceq [string]$Row.after_sha256_lf) ($WorkingLf -ceq [string]$Row.after_sha256_lf)
        if (
            $FollowupOverlayDisposition -ceq 'tracked_historical_evidence' -and
            $RowDisposition -ceq 'blocked' -and
            $RowPath -ceq 'Iris/test/validate_residual_refactor_surfaces.ps1'
        ) {
            [void]$FollowupOverlaySupersededPaths.Add($RowPath)
            continue
        }
        if ($RowDisposition -cne $FollowupOverlayDisposition) {
            throw "codebase optimization follow-up protected row lifecycle mismatch: $RowPath"
        }
        $FollowupOverlayRows[$RowPath] = $Row
        $OverlayExpectedHeadBlobs[$RowPath] = $HeadBlob
        if ($RowDisposition -ceq 'tracked_historical_evidence') {
            [void]$FollowupOverlayHistoricalPaths.Add($RowPath)
        }
    }
    if (
        $FollowupOverlayDisposition -ceq 'tracked_historical_evidence' -and
        (
            $FollowupOverlaySupersededPaths.Count -ne 1 -or
            -not $FollowupOverlaySupersededPaths.Contains('Iris/test/validate_residual_refactor_surfaces.ps1')
        )
    ) {
        throw 'codebase optimization follow-up superseded historical row set mismatch'
    }
}
elseif ($Mode -eq 'Baseline') {
    throw 'codebase optimization follow-up protected-surface overlay has no rows'
}
$CodebaseFollowupOverlayRowCount = $FollowupOverlayRows.Count
$ItemPageInformationSufficiencyOverlayRowCount = 0
$ItemPageInformationSufficiencyOverlayDisposition = 'absent'
if (Test-Path -LiteralPath $ItemPageInformationSufficiencyOverlayPath -PathType Leaf) {
    $ItemPageOverlay = Get-Content -LiteralPath $ItemPageInformationSufficiencyOverlayPath -Raw | ConvertFrom-Json
    $ItemPageOverlayTrackedPaths = @(& git -C $RepositoryRoot ls-tree -r --name-only HEAD -- $ItemPageInformationSufficiencyOverlayRelative)
    if ($LASTEXITCODE -ne 0) {
        throw 'item-page information-sufficiency protected overlay tracking query failed'
    }
    $ItemPageOverlayIsTracked = @($ItemPageOverlayTrackedPaths | Where-Object { [string]$_ -ceq $ItemPageInformationSufficiencyOverlayRelative }).Count -eq 1
    $ItemPageOverlayTrackedBlob = if ($ItemPageOverlayIsTracked) {
        (& git -C $RepositoryRoot rev-parse ("HEAD:" + $ItemPageInformationSufficiencyOverlayRelative)).Trim()
    } else { $null }
    $ItemPageOverlayWorkingBlob = (& git -C $RepositoryRoot hash-object ("--path=" + $ItemPageInformationSufficiencyOverlayRelative) $ItemPageInformationSufficiencyOverlayPath).Trim()
    if ($LASTEXITCODE -ne 0) {
        throw 'item-page information-sufficiency protected overlay working blob could not be computed'
    }
    if (
        [string]$ItemPageOverlay.schema_version -cne 'iris-item-page-information-sufficiency-protected-surface-successor-v1' -or
        [string]$ItemPageOverlay.authority -cne 'repository_owner_preapproval' -or
        [string]$ItemPageOverlay.plan -cne 'docs/새 폴더/iris_item_page_information_sufficiency_plan.md' -or
        [string]$ItemPageOverlay.implementation_state -cne 'active_or_tracked_durable_successor' -or
        (Get-ItemPageOverlayScopeDisposition @($ItemPageOverlay.rows)) -cne 'exact_six_path_scope'
    ) {
        throw 'item-page information-sufficiency protected overlay identity or scope mismatch'
    }
    $DeclaredBaseCommit = [string]$ItemPageOverlay.base_commit
    $DeclaredBaseTree = [string]$ItemPageOverlay.base_tree
    if ((Get-ItemPageOverlayBaseDisposition $DeclaredBaseCommit $DeclaredBaseTree) -cne 'exact_approved_base') {
        throw 'item-page information-sufficiency protected overlay approved base mismatch'
    }
    $ObservedBaseTree = (& git -C $RepositoryRoot rev-parse ($DeclaredBaseCommit + '^{tree}') 2>$null | Out-String).Trim()
    if ($LASTEXITCODE -ne 0 -or $ObservedBaseTree -cne $DeclaredBaseTree) {
        throw 'item-page information-sufficiency protected overlay base tree mismatch'
    }
    $BaseOverlayTreeRows = @(& git -C $RepositoryRoot ls-tree $DeclaredBaseCommit -- $ItemPageInformationSufficiencyOverlayRelative)
    if ($LASTEXITCODE -ne 0 -or $BaseOverlayTreeRows.Count -ne 0) {
        throw 'item-page information-sufficiency protected overlay unexpectedly exists in approved base tree'
    }
    $BaseMatchesCurrentHead = $DeclaredBaseCommit -ceq $SubjectCommit -and $DeclaredBaseTree -ceq $SubjectTree
    & git -C $RepositoryRoot merge-base --is-ancestor $DeclaredBaseCommit $SubjectCommit 2>$null
    $ApprovedBaseIsAncestorOfCurrentHead = $LASTEXITCODE -eq 0
    $ItemPageInformationSufficiencyOverlayDisposition = Get-ItemPageOverlayDisposition $true $ItemPageOverlayTrackedBlob $ItemPageOverlayWorkingBlob $BaseMatchesCurrentHead $ApprovedBaseIsAncestorOfCurrentHead
    if ($ItemPageInformationSufficiencyOverlayDisposition -ceq 'blocked') {
        throw 'item-page information-sufficiency protected overlay lifecycle mismatch'
    }
    foreach ($Row in @($ItemPageOverlay.rows)) {
        $RowPath = [string]$Row.path
        if (
            [System.IO.Path]::IsPathRooted($RowPath) -or
            $RowPath -match '(^|/)\.\.(/|$)' -or
            $FollowupOverlayRows.ContainsKey($RowPath) -or
            [string]$Row.after_git_blob_id -notmatch '^[0-9a-f]{40,64}$'
        ) {
            throw "item-page information-sufficiency protected row identity invalid: $RowPath"
        }
        $BeforeBlob = (& git -C $RepositoryRoot rev-parse ($DeclaredBaseCommit + ':' + $RowPath)).Trim()
        if ($LASTEXITCODE -ne 0 -or $BeforeBlob -cne [string]$Row.before_git_blob_id) {
            throw "item-page information-sufficiency protected row predecessor mismatch: $RowPath"
        }
        if ((Get-GitBlobLfHash $BeforeBlob) -cne [string]$Row.before_sha256_lf) {
            throw "item-page information-sufficiency protected row predecessor LF hash mismatch: $RowPath"
        }
        $WorkingAfterBlob = (& git -C $RepositoryRoot hash-object ("--path=" + $RowPath) (Join-Path $RepositoryRoot $RowPath)).Trim()
        if ($LASTEXITCODE -ne 0 -or $WorkingAfterBlob -cne [string]$Row.after_git_blob_id) {
            throw "item-page information-sufficiency protected row working Git blob mismatch: $RowPath"
        }
        if ((Get-LfTextHashOrNull (Join-Path $RepositoryRoot $RowPath)) -cne [string]$Row.after_sha256_lf) {
            throw "item-page information-sufficiency protected row working LF hash mismatch: $RowPath"
        }
        $ExpectedHeadBlob = if ($ItemPageInformationSufficiencyOverlayDisposition -ceq 'tracked_durable_successor') { [string]$Row.after_git_blob_id } else { [string]$Row.before_git_blob_id }
        $ObservedHeadBlob = (& git -C $RepositoryRoot rev-parse ("HEAD:" + $RowPath)).Trim()
        if ($LASTEXITCODE -ne 0 -or $ObservedHeadBlob -cne $ExpectedHeadBlob) {
            throw "item-page information-sufficiency protected row HEAD lifecycle mismatch: $RowPath"
        }
        if ([string]$Row.owner -cne 'repository_owner_preapproval') {
            throw "item-page information-sufficiency protected row authorization invalid: $RowPath"
        }
        $FollowupOverlayRows[$RowPath] = $Row
        $OverlayExpectedHeadBlobs[$RowPath] = $ExpectedHeadBlob
        $ItemPageInformationSufficiencyOverlayRowCount += 1
    }
}
$FollowupOverlayUsed = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::Ordinal)

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
    $RevisionRemovedRows = if ($Revision.PSObject.Properties.Name -contains 'removed_protected_rows') {
        @($Revision.removed_protected_rows)
    }
    else {
        @()
    }
    foreach ($Removed in $RevisionRemovedRows) {
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
    $Overlay = if ($FollowupOverlayRows.ContainsKey($DeltaPath)) { $FollowupOverlayRows[$DeltaPath] } else { $null }
    $ExpectedBlob = if ($null -ne $Overlay) { [string]$OverlayExpectedHeadBlobs[$DeltaPath] } else { [string]$Delta.expected_git_blob_id }
    $ExpectedLf = if ($null -ne $Overlay) { [string]$Overlay.after_sha256_lf } else { [string]$Delta.after_sha256_lf }
    if ($LASTEXITCODE -ne 0 -or $ActualBlob -cne $ExpectedBlob) {
        throw "repository lightweighting final delta Git blob mismatch: $DeltaPath"
    }
    if ((Get-ProtectedWorkingDriftDisposition ((Get-LfTextHashOrNull (Join-Path $RepositoryRoot $DeltaPath)) -ceq $ExpectedLf)) -ceq 'blocked') {
        throw "repository lightweighting final delta LF hash mismatch: $DeltaPath"
    }
    if ($null -ne $Overlay) { [void]$FollowupOverlayUsed.Add($DeltaPath) }
}
foreach ($Entry in $AddedProtectedRows.GetEnumerator()) {
    $Added = $Entry.Value
    $AddedPath = [string]$Added.path
    $ActualBlob = (& git -C $RepositoryRoot rev-parse ("HEAD:" + $AddedPath)).Trim()
    $Overlay = if ($FollowupOverlayRows.ContainsKey($AddedPath)) { $FollowupOverlayRows[$AddedPath] } else { $null }
    $ExpectedBlob = if ($null -ne $Overlay) { [string]$OverlayExpectedHeadBlobs[$AddedPath] } else { [string]$Added.expected_git_blob_id }
    $ExpectedLf = if ($null -ne $Overlay) { [string]$Overlay.after_sha256_lf } else { [string]$Added.after_sha256_lf }
    if ($LASTEXITCODE -ne 0 -or $ActualBlob -cne $ExpectedBlob) {
        throw "repository lightweighting final added-row Git blob mismatch: $AddedPath"
    }
    if ((Get-ProtectedWorkingDriftDisposition ((Get-LfTextHashOrNull (Join-Path $RepositoryRoot $AddedPath)) -ceq $ExpectedLf)) -ceq 'blocked') {
        throw "repository lightweighting final added-row LF hash mismatch: $AddedPath"
    }
    if ($null -ne $Overlay) { [void]$FollowupOverlayUsed.Add($AddedPath) }
}
if ($FollowupOverlayUsed.Count -ne $FollowupOverlayRows.Count) {
    $Unused = @($FollowupOverlayRows.Keys | Where-Object { -not $FollowupOverlayUsed.Contains([string]$_) } | Sort-Object)
    throw ('codebase optimization follow-up protected rows are outside active protection: ' + ($Unused -join ','))
}
foreach ($RemovedPath in $RemovedProtectedRows.Keys) {
    $FinalTreeRows = @(& git -C $RepositoryRoot ls-tree HEAD -- ([string]$RemovedPath))
    if (
        $LASTEXITCODE -ne 0 -or
        $FinalTreeRows.Count -ne 0 -or
        (Test-Path -LiteralPath (Join-Path $RepositoryRoot ([string]$RemovedPath)))
    ) {
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
    $OverlayAuthorization = if ($FollowupOverlayRows.ContainsKey($RowPath)) { $FollowupOverlayRows[$RowPath] } else { $null }
    $OverlayAfterMatches = $null -ne $OverlayAuthorization -and $AfterLf -ceq [string]$OverlayAuthorization.after_sha256_lf
    $DurableDeltaAfterMatches = $ApprovedDeltas.ContainsKey($RowPath) -and $AfterLf -ceq [string]$ApprovedDeltas[$RowPath].after_sha256_lf
    $AuthorizationDisposition = Get-ProtectedChangeAuthorizationDisposition $Changed $OverlayAfterMatches $DurableDeltaAfterMatches
    $Authorized = $AuthorizationDisposition -ceq 'authorized'
    $AuthorizationRecord = if ($OverlayAfterMatches) { $OverlayAuthorization } elseif ($DurableDeltaAfterMatches) { $ApprovedDeltas[$RowPath] } else { $null }
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
        authorization_owner = if ($Authorized) { [string]$AuthorizationRecord.owner } else { $null }
        authorization_reason = if ($Authorized) { [string]$AuthorizationRecord.reason } else { $null }
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
    codebase_optimization_followup_overlay_manifest = $FollowupOverlayRelative
    codebase_optimization_followup_overlay_sha256 = Get-HashOrNull $FollowupOverlayPath
    codebase_optimization_followup_overlay_row_count = $CodebaseFollowupOverlayRowCount
    codebase_optimization_followup_overlay_disposition = $FollowupOverlayDisposition
    codebase_optimization_followup_historical_row_count = $FollowupOverlayHistoricalPaths.Count
    codebase_optimization_followup_superseded_paths = @($FollowupOverlaySupersededPaths | Sort-Object)
    item_page_information_sufficiency_overlay_manifest = $ItemPageInformationSufficiencyOverlayRelative
    item_page_information_sufficiency_overlay_sha256 = Get-HashOrNull $ItemPageInformationSufficiencyOverlayPath
    item_page_information_sufficiency_overlay_disposition = $ItemPageInformationSufficiencyOverlayDisposition
    item_page_information_sufficiency_overlay_row_count = $ItemPageInformationSufficiencyOverlayRowCount
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
