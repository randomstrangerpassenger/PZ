[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateSet('windows_uv_python', 'windows_record_sidecar')]
    [string]$Route,
    [Parameter(Mandatory = $true)]
    [string]$AttemptRoot,
    [Parameter(Mandatory = $true)]
    [string]$SurfaceInputManifest,
    [Parameter(Mandatory = $true)]
    [ValidateSet('candidate', 'canonical_durable')]
    [string]$PolicyContext,
    [Parameter(Mandatory = $true)]
    [string]$PolicyPath,
    [Parameter(Mandatory = $true)]
    [string]$DispositionPath,
    [Parameter(Mandatory = $true)]
    [string]$BindingManifestPath
)

$ErrorActionPreference = 'Stop'
$scriptRoot = if ($PSScriptRoot) { $PSScriptRoot } else { Split-Path -Parent $MyInvocation.MyCommand.Path }
$repoRoot = [System.IO.Path]::GetFullPath((Join-Path $scriptRoot '..\..'))
$attemptRootFull = [System.IO.Path]::GetFullPath($AttemptRoot)
$surfaceManifestFull = [System.IO.Path]::GetFullPath($SurfaceInputManifest)
$policyFull = [System.IO.Path]::GetFullPath($PolicyPath)
$dispositionFull = [System.IO.Path]::GetFullPath($DispositionPath)
$bindingFull = [System.IO.Path]::GetFullPath($BindingManifestPath)
$validator = Join-Path $repoRoot 'Iris\build\description\v2\tools\build\validate_dvf_3_3_registry_runtime_compatibility.py'
$recordExporter = Join-Path $repoRoot 'Iris\build\description\v2\tools\build\export_registry_runtime_records.py'
$phase3 = Join-Path $attemptRootFull 'phase3'
New-Item -ItemType Directory -Path $phase3 -Force | Out-Null

$uv = Get-Command uv -ErrorAction SilentlyContinue
if ($null -eq $uv) {
    throw 'compatibility_blocked_required_dependency: uv executable is missing'
}
if (-not (Test-Path -LiteralPath $validator -PathType Leaf)) {
    throw "compatibility_blocked_required_dependency: validator is missing: $validator"
}

$validatorOut = Join-Path $phase3 ("{0}_validator_report.json" -f $Route)
if ($Route -eq 'windows_record_sidecar') {
    if (-not (Test-Path -LiteralPath $recordExporter -PathType Leaf)) {
        throw "compatibility_blocked_required_dependency: record exporter is missing: $recordExporter"
    }
    $recordsOut = Join-Path $phase3 'windows_projection.jsonl'
    $recordReport = Join-Path $phase3 'windows_projection_report.json'
    & $uv.Source run python -B $recordExporter `
        --surface-input-manifest $surfaceManifestFull `
        --policy-context $PolicyContext `
        --policy $policyFull `
        --disposition $dispositionFull `
        --binding-manifest $bindingFull `
        --records-out $recordsOut `
        --report-out $recordReport
    if ($LASTEXITCODE -ne 0) {
        throw "windows_record_sidecar_export_failed: exit=$LASTEXITCODE"
    }
}

& $uv.Source run python -B $validator `
    --surface-validation `
    --surface-input-manifest $surfaceManifestFull `
    --policy-context $PolicyContext `
    --policy $policyFull `
    --disposition $dispositionFull `
    --binding-manifest $bindingFull `
    --out $validatorOut
if ($LASTEXITCODE -ne 0) {
    throw "windows_registry_compatibility_validation_failed: exit=$LASTEXITCODE"
}

$validatorPayload = Get-Content -LiteralPath $validatorOut -Raw -Encoding UTF8 | ConvertFrom-Json
if ($validatorPayload.status -ne 'PASS') {
    throw "windows_registry_compatibility_validation_not_pass: $validatorOut"
}

$routeReport = [ordered]@{
    schema_version = 'rtc-windows-route-conformance-v1'
    round_id = 'dvf_3_3_registry_runtime_compatibility'
    status = 'PASS'
    route = $Route
    algorithm_proof = 'canonical_analyzer'
    transport = if ($Route -eq 'windows_uv_python') { 'uv_python_stdout_json' } else { 'utf8_jsonl_record_sidecar' }
    surface_input_manifest = $surfaceManifestFull
    policy_context = $PolicyContext
    binding_manifest_sha256 = (Get-FileHash -LiteralPath $bindingFull -Algorithm SHA256).Hash.ToLowerInvariant()
    validator_report = $validatorOut
    validator_report_sha256 = (Get-FileHash -LiteralPath $validatorOut -Algorithm SHA256).Hash.ToLowerInvariant()
}
$routeReportPath = Join-Path $phase3 ("{0}_route_report.json" -f $Route)
$json = $routeReport | ConvertTo-Json -Depth 8
$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
[System.IO.File]::WriteAllText($routeReportPath, $json + [Environment]::NewLine, $utf8NoBom)
Write-Host "Registry compatibility Windows route PASS: $Route -> $routeReportPath"
