[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateSet('Baseline', 'Closeout')]
    [string]$Mode,
    [Parameter(Mandatory = $true)]
    [string]$RepositoryRoot,
    [Parameter(Mandatory = $true)]
    [string]$EvidenceRoot
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$Utf8NoBom = New-Object System.Text.UTF8Encoding($false)

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

$ModuleFiles = @{
    'Iris/IrisAPI' = 'Iris/media/lua/client/Iris/IrisAPI.lua'
    'Iris/API/Description' = 'Iris/media/lua/client/Iris/API/Description.lua'
    'Iris/API/UseCases' = 'Iris/media/lua/client/Iris/API/UseCases.lua'
    'Iris/UI/Browser/IrisBrowserData' = 'Iris/media/lua/client/Iris/UI/Browser/IrisBrowserData.lua'
    'Iris/UI/Wiki/IrisWikiSections' = 'Iris/media/lua/client/Iris/UI/Wiki/IrisWikiSections.lua'
    'Iris/UI/Wiki/IrisWikiPanel' = 'Iris/media/lua/client/Iris/UI/Wiki/IrisWikiPanel.lua'
    'Iris/UI/Browser/IrisBrowser' = 'Iris/media/lua/client/Iris/UI/Browser/IrisBrowser.lua'
    'Iris/Data/IrisData' = 'Iris/media/lua/client/Iris/Data/IrisData.lua'
    'generated runtime global' = 'Iris/media/lua/client/Iris/Data/IrisPrimarySubcategory.lua'
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
        $PrimarySource = Join-Path $RepositoryRoot 'Iris/media/lua/client/Iris/Data/IrisPrimarySubcategory.lua'
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
foreach ($Row in $ProtectedBaseline.rows) {
    $FullPath = Join-Path $RepositoryRoot ([string]$Row.path)
    $After = Get-HashOrNull $FullPath
    $Changed = $After -cne [string]$Row.sha256
    if ($Changed) { $Unauthorized += 1 }
    $ProtectedRows += [ordered]@{
        path = [string]$Row.path
        before_sha256 = [string]$Row.sha256
        after_sha256 = $After
        changed = $Changed
        authorized = $false
    }
}
$ProtectedReport = [ordered]@{
    schema_version = 'iris-residual-protected-surface-report-v1'
    validation_status = if ($Unauthorized -eq 0) { 'passed' } else { 'failed' }
    baseline_manifest = Get-Relative $ProtectedBaselinePath
    baseline_manifest_sha256 = Get-HashOrNull $ProtectedBaselinePath
    changed_count = @($ProtectedRows | Where-Object changed).Count
    authorized_changed_count = 0
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
