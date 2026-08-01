[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateSet('LocalCandidate', 'StagedChangeset', 'CleanCheckout')]
    [string]$Mode,
    [Parameter(Mandatory = $true)]
    [string]$RepositoryRoot,
    [string]$TargetCommit,
    [string]$WorkRoot,
    [string]$ResultRoot,
    [string]$ManifestPath,
    [switch]$IntegrityOnly,
    [switch]$InternalMaterialized
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$ManifestRelativePath = 'Iris/_docs/refactor/core_refactor/phase1_validation_asset_manifest.json'
$ValidatorRelativePath = 'Iris/test/validate_validation_assets.ps1'
$Utf8NoBom = New-Object System.Text.UTF8Encoding($false)

function Get-Sha256Bytes([byte[]]$Bytes) {
    $sha256 = [System.Security.Cryptography.SHA256]::Create()
    try {
        return [System.BitConverter]::ToString($sha256.ComputeHash($Bytes)).Replace('-', '').ToLowerInvariant()
    }
    finally { $sha256.Dispose() }
}

function Get-Sha256File([string]$Path) {
    return (Get-FileHash -Algorithm SHA256 -LiteralPath $Path).Hash.ToLowerInvariant()
}

function Invoke-GitText([string[]]$Arguments, [switch]$AllowFailure) {
    $output = @(& git -C $script:ValidatedRepositoryRoot @Arguments 2>&1)
    $exitCode = $LASTEXITCODE
    if (-not $AllowFailure -and $exitCode -ne 0) {
        throw "git command failed ($exitCode): git $($Arguments -join ' ')`n$($output -join "`n")"
    }
    return [pscustomobject]@{ ExitCode = $exitCode; Text = (($output -join "`n") + $(if ($output.Count -gt 0) { "`n" } else { '' })) }
}

function Assert-ExternalRoot([string]$Candidate, [string]$Label) {
    if (-not $Candidate) { throw "$Label is required" }
    $resolved = [System.IO.Path]::GetFullPath($Candidate)
    $repo = $script:ValidatedRepositoryRoot.TrimEnd('\', '/')
    if ($resolved -eq $repo -or $resolved.StartsWith($repo + [System.IO.Path]::DirectorySeparatorChar, [System.StringComparison]::OrdinalIgnoreCase) -or $repo.StartsWith($resolved.TrimEnd('\', '/') + [System.IO.Path]::DirectorySeparatorChar, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "$Label must be external and disjoint from the repository: $resolved"
    }
    return $resolved
}

function Test-ManifestContent([string]$ManifestContent, [string]$SourceLabel) {
    if ([string]::IsNullOrWhiteSpace($ManifestContent)) {
        throw "empty asset manifest content: $SourceLabel"
    }
    try { $assetManifest = $ManifestContent | ConvertFrom-Json }
    catch { throw "invalid asset manifest JSON: $SourceLabel" }
    if ((-not ($assetManifest.schema_version -is [int])) -and (-not ($assetManifest.schema_version -is [long]))) { throw 'schema_version must be an integer' }
    if ([long]$assetManifest.schema_version -ne 1) { throw 'unsupported asset manifest schema_version' }
    if ((-not ($assetManifest.generation -is [int])) -and (-not ($assetManifest.generation -is [long]))) { throw 'generation must be an integer' }
    if ([long]$assetManifest.generation -lt 1) { throw 'generation must be positive' }
    if (-not ($assetManifest.sealed -is [bool])) { throw 'sealed must be boolean' }
    if (-not ($assetManifest.assets -is [System.Array])) { throw "asset manifest missing 'assets' array" }
    $assets = @($assetManifest.assets)
    if ($assets.Count -eq 0) { throw 'asset manifest assets must be non-empty' }
    if ((-not ($assetManifest.expected_required_count -is [int])) -and (-not ($assetManifest.expected_required_count -is [long]))) { throw 'expected_required_count must be an integer' }
    $expectedRequiredCount = [long]$assetManifest.expected_required_count
    if ($expectedRequiredCount -le 0) { throw 'expected_required_count must be positive' }
    if (-not ($assetManifest.expected_required_asset_ids -is [System.Array])) { throw 'expected_required_asset_ids must be an array' }
    $expectedRequiredIds = [string[]]@($assetManifest.expected_required_asset_ids)
    if ($expectedRequiredIds.Count -ne $expectedRequiredCount) { throw 'expected required ID count mismatch' }
    $sortedExpectedIds = [string[]]@($expectedRequiredIds)
    [System.Array]::Sort($sortedExpectedIds, [System.StringComparer]::Ordinal)
    if (($expectedRequiredIds -join "`0") -cne ($sortedExpectedIds -join "`0")) { throw 'expected required IDs must be ordinal sorted' }
    $allowedArtifactClasses = @('python_test','validation_support_asset','fixture','schema','evidence','binding_record','inventory','corpus','validator','ceiling')
    $allowedRouteClasses = @('current','historical','diagnostic')
    $requiredFields = @('asset_id','path','required','lifecycle_state','artifact_class','route_class_or_null','owner_change','tracked_required','clean_checkout_required')
    foreach ($asset in $assets) {
        foreach ($field in $requiredFields) { if ($asset.PSObject.Properties.Name -notcontains $field) { throw "asset missing field '$field'" } }
        if ((-not ($asset.asset_id -is [string])) -or [string]::IsNullOrWhiteSpace($asset.asset_id) -or $asset.asset_id -cnotmatch '^[a-z0-9._-]+$') { throw 'invalid asset_id' }
        if ((-not ($asset.path -is [string])) -or [string]::IsNullOrWhiteSpace($asset.path) -or $asset.path -cnotmatch '^[A-Za-z0-9._/-]+$') { throw "invalid asset path: $($asset.asset_id)" }
        if ($asset.path.Contains('\') -or $asset.path.StartsWith('/') -or $asset.path.EndsWith('/') -or $asset.path.Contains('//') -or $asset.path -match '^[A-Za-z]:') { throw "non-canonical asset path: $($asset.path)" }
        $segments = @($asset.path.Split('/'))
        if (@($segments | Where-Object { $_ -in @('', '.', '..') }).Count -ne 0) { throw "asset path contains forbidden segment: $($asset.path)" }
        if (-not ($asset.required -is [bool])) { throw 'required must be boolean' }
        if ((-not ($asset.lifecycle_state -is [string])) -or $asset.lifecycle_state -notin @('reserved_future','required_active','sealed')) { throw "invalid lifecycle_state: $($asset.asset_id)" }
        if ((-not ($asset.artifact_class -is [string])) -or $asset.artifact_class -notin $allowedArtifactClasses) { throw "invalid artifact_class: $($asset.asset_id)" }
        if ($asset.artifact_class -eq 'python_test') {
            if ((-not ($asset.route_class_or_null -is [string])) -or $asset.route_class_or_null -notin $allowedRouteClasses) { throw "python test requires route class: $($asset.asset_id)" }
        }
        elseif ($null -ne $asset.route_class_or_null) { throw "non-test asset route must be null: $($asset.asset_id)" }
        if (((-not ($asset.owner_change -is [int])) -and (-not ($asset.owner_change -is [long]))) -or [long]$asset.owner_change -lt 1 -or [long]$asset.owner_change -gt 9) { throw "invalid owner_change: $($asset.asset_id)" }
        if (-not ($asset.tracked_required -is [bool]) -or -not ($asset.clean_checkout_required -is [bool])) { throw "tracking flags must be boolean: $($asset.asset_id)" }
        if ($asset.required -and $asset.lifecycle_state -notin @('required_active','sealed')) { throw "invalid active lifecycle: $($asset.asset_id)" }
        if (-not $asset.required -and $asset.lifecycle_state -ne 'reserved_future') { throw "invalid future lifecycle: $($asset.asset_id)" }
        if ($asset.required -and (-not $asset.tracked_required -or -not $asset.clean_checkout_required)) { throw "active asset must require tracking and clean checkout: $($asset.asset_id)" }
    }
    if (@($assets | Group-Object asset_id | Where-Object Count -gt 1).Count -ne 0) { throw 'duplicate asset_id' }
    $normalizedPaths = @($assets | ForEach-Object { ([string]$_.path).ToLowerInvariant() })
    if (@($normalizedPaths | Group-Object | Where-Object Count -gt 1).Count -ne 0) { throw 'duplicate asset path' }
    $requiredAssets = @($assets | Where-Object { $_.required -eq $true })
    $actualRequiredIds = [string[]]@($requiredAssets.asset_id)
    [System.Array]::Sort($actualRequiredIds, [System.StringComparer]::Ordinal)
    if ($requiredAssets.Count -ne $expectedRequiredCount -or $expectedRequiredIds.Count -ne $expectedRequiredCount -or ($actualRequiredIds -join "`0") -cne ($expectedRequiredIds -join "`0")) { throw 'required asset denominator mismatch' }
    $reservedFutureAssets = @($assets | Where-Object lifecycle_state -eq 'reserved_future')
    if ($assetManifest.sealed -and $reservedFutureAssets.Count -ne 0) { throw 'sealed manifest contains reserved future asset' }
    if ($assetManifest.sealed -and @($requiredAssets | Where-Object lifecycle_state -ne 'sealed').Count -ne 0) { throw 'sealed manifest contains unsealed required asset' }
    if (-not $assetManifest.sealed -and @($requiredAssets | Where-Object lifecycle_state -eq 'sealed').Count -ne 0) { throw 'unsealed manifest contains sealed required asset' }
    $canonicalIds = ($actualRequiredIds -join "`n") + "`n"
    $actualIdHash = Get-Sha256Bytes $Utf8NoBom.GetBytes($canonicalIds)
    if ([string]$assetManifest.expected_required_asset_ids_sha256 -cnotmatch '^[0-9a-f]{64}$') { throw 'required asset identity hash must be lowercase SHA-256 hexadecimal' }
    if ($actualIdHash -ne [string]$assetManifest.expected_required_asset_ids_sha256) { throw 'required asset identity hash mismatch' }
    return $assetManifest
}

function Assert-RequiredFiles($Manifest, [ValidateSet('working','index','checkout')] [string]$SourceKind) {
    foreach ($asset in @($Manifest.assets | Where-Object required -eq $true)) {
        $relative = [string]$asset.path
        $fullPath = [System.IO.Path]::GetFullPath((Join-Path $script:ValidatedRepositoryRoot $relative))
        $rootPrefix = $script:ValidatedRepositoryRoot.TrimEnd('\', '/') + [System.IO.Path]::DirectorySeparatorChar
        if (-not $fullPath.StartsWith($rootPrefix, [System.StringComparison]::OrdinalIgnoreCase)) { throw "asset resolves outside repository: $relative" }
        if ($SourceKind -eq 'index') {
            $typeResult = Invoke-GitText @('cat-file','-t',":$relative") -AllowFailure
            if ($typeResult.ExitCode -ne 0 -or $typeResult.Text.Trim() -ne 'blob') { throw "required index asset is not a blob: $relative" }
        }
        else {
            if (-not (Test-Path -LiteralPath $fullPath -PathType Leaf)) { throw "required asset missing: $relative" }
            if ($SourceKind -eq 'checkout') {
                $tracked = Invoke-GitText @('ls-files','--error-unmatch','--',$relative) -AllowFailure
                if ($tracked.ExitCode -ne 0) { throw "required asset is not tracked: $relative" }
            }
        }
        $ignore = Invoke-GitText @('check-ignore','--',$relative) -AllowFailure
        if ($ignore.ExitCode -eq 0) { throw "required asset is ignored: $relative" }
        if ($ignore.ExitCode -ne 1) { throw "git check-ignore failed for $relative" }
    }
}

$rootCandidate = [System.IO.Path]::GetFullPath($RepositoryRoot).TrimEnd('\', '/')
$gitRootResult = & git -C $rootCandidate rev-parse --show-toplevel 2>&1
if ($LASTEXITCODE -ne 0) { throw "RepositoryRoot is not a Git worktree: $rootCandidate" }
$gitRoot = [System.IO.Path]::GetFullPath(($gitRootResult -join '').Trim()).TrimEnd('\', '/')
if (-not $gitRoot.Equals($rootCandidate, [System.StringComparison]::OrdinalIgnoreCase)) { throw "RepositoryRoot identity mismatch: $rootCandidate != $gitRoot" }
$script:ValidatedRepositoryRoot = $gitRoot

if ($ManifestPath) {
    if ($Mode -ne 'LocalCandidate' -or -not $IntegrityOnly) { throw 'ManifestPath is allowed only for LocalCandidate -IntegrityOnly' }
    $manifestFull = [System.IO.Path]::GetFullPath($ManifestPath)
    $manifest = Test-ManifestContent ([System.IO.File]::ReadAllText($manifestFull)) $manifestFull
    Write-Output "validation asset manifest integrity PASS: $manifestFull"
    exit 0
}

if ($Mode -eq 'StagedChangeset' -and -not $InternalMaterialized) {
    $workingValidator = Join-Path $ValidatedRepositoryRoot $ValidatorRelativePath
    $indexValidatorResult = Invoke-GitText @('show',":$ValidatorRelativePath")
    $indexBytes = $Utf8NoBom.GetBytes($indexValidatorResult.Text)
    $workingHash = Get-Sha256File $workingValidator
    $indexHash = Get-Sha256Bytes $indexBytes
    if ($workingHash -ne $indexHash) { throw 'working/index validator identity mismatch' }
    $tempRoot = Join-Path ([System.IO.Path]::GetTempPath()) ('iris-core-refactor-index-validator-' + [guid]::NewGuid().ToString('N'))
    New-Item -ItemType Directory -Path $tempRoot | Out-Null
    $materialized = Join-Path $tempRoot 'validate_validation_assets.ps1'
    try {
        [System.IO.File]::WriteAllBytes($materialized, $indexBytes)
        & powershell -NoProfile -ExecutionPolicy Bypass -File $materialized -Mode StagedChangeset -RepositoryRoot $ValidatedRepositoryRoot -InternalMaterialized
        if ($LASTEXITCODE -ne 0) { throw "materialized staged validator failed: $LASTEXITCODE" }
    }
    finally { Remove-Item -LiteralPath $tempRoot -Recurse -Force -ErrorAction SilentlyContinue }
    Write-Output "validation assets PASS: mode=StagedChangeset validator_sha256=$indexHash"
    exit 0
}

if ($Mode -eq 'CleanCheckout' -and -not $InternalMaterialized) {
    if (-not $TargetCommit) { throw 'TargetCommit is required for CleanCheckout' }
    $validatedWorkRoot = Assert-ExternalRoot $WorkRoot 'WorkRoot'
    $validatedResultRoot = Assert-ExternalRoot $ResultRoot 'ResultRoot'
    if ($validatedWorkRoot.Equals($validatedResultRoot, [System.StringComparison]::OrdinalIgnoreCase)) { throw 'WorkRoot and ResultRoot must be disjoint' }
    if (Test-Path -LiteralPath $validatedWorkRoot) { throw 'WorkRoot must not exist' }
    if (Test-Path -LiteralPath $validatedResultRoot) { throw 'ResultRoot must not exist' }
    $sourceStatusBefore = (Invoke-GitText @('status','--porcelain=v1','-uall')).Text
    New-Item -ItemType Directory -Path $validatedResultRoot | Out-Null
    $stdoutPath = Join-Path $validatedResultRoot 'stdout.txt'
    $stderrPath = Join-Path $validatedResultRoot 'stderr.txt'
    $cleanup = $false
    try {
        & git clone --no-local --no-checkout -- $ValidatedRepositoryRoot $validatedWorkRoot 1>$stdoutPath 2>$stderrPath
        if ($LASTEXITCODE -ne 0) { throw 'external clone failed' }
        & git -C $validatedWorkRoot checkout --detach $TargetCommit 1>>$stdoutPath 2>>$stderrPath
        if ($LASTEXITCODE -ne 0) { throw 'detached checkout failed' }
        $committedValidator = Join-Path $validatedWorkRoot $ValidatorRelativePath
        & powershell -NoProfile -ExecutionPolicy Bypass -File $committedValidator -Mode CleanCheckout -RepositoryRoot $validatedWorkRoot -TargetCommit $TargetCommit -InternalMaterialized 1>>$stdoutPath 2>>$stderrPath
        if ($LASTEXITCODE -ne 0) { throw 'committed clean-checkout validator failed' }
    }
    finally {
        if (Test-Path -LiteralPath $validatedWorkRoot) { Remove-Item -LiteralPath $validatedWorkRoot -Recurse -Force -ErrorAction SilentlyContinue }
        $cleanup = -not (Test-Path -LiteralPath $validatedWorkRoot)
    }
    $sourceStatusAfter = (Invoke-GitText @('status','--porcelain=v1','-uall')).Text
    if ($sourceStatusBefore -cne $sourceStatusAfter) { throw 'source worktree changed during CleanCheckout validation' }
    if (-not $cleanup) { throw 'disposable checkout cleanup failed' }
    $identity = Invoke-GitText @('show','-s','--format=%H:%T',$TargetCommit)
    $manifestBlob = (Invoke-GitText @('rev-parse',"$TargetCommit`:$ManifestRelativePath")).Text.Trim()
    $validatorBlob = (Invoke-GitText @('rev-parse',"$TargetCommit`:$ValidatorRelativePath")).Text.Trim()
    $receipt = [ordered]@{schema_version=1;mode='CleanCheckout';target_identity=$identity.Text.Trim();manifest_blob=$manifestBlob;validator_blob=$validatorBlob;source_status_sha256=Get-Sha256Bytes $Utf8NoBom.GetBytes($sourceStatusBefore);checkout_cleanup=$cleanup;work_root=$validatedWorkRoot;result_root=$validatedResultRoot}
    $receiptPath = Join-Path $validatedResultRoot 'receipt.json'
    [System.IO.File]::WriteAllText($receiptPath, (($receipt | ConvertTo-Json -Depth 10) + "`n"), $Utf8NoBom)
    $canonical = [ordered]@{status='pass';mode='CleanCheckout';target_commit=$TargetCommit;receipt_sha256=Get-Sha256File $receiptPath;stdout_sha256=Get-Sha256File $stdoutPath;stderr_sha256=Get-Sha256File $stderrPath}
    [System.IO.File]::WriteAllText((Join-Path $validatedResultRoot 'canonical-result.json'), (($canonical | ConvertTo-Json -Compress) + "`n"), $Utf8NoBom)
    Write-Output "validation assets PASS: mode=CleanCheckout result_root=$validatedResultRoot"
    exit 0
}

if ($Mode -eq 'LocalCandidate') {
    $manifestFull = Join-Path $ValidatedRepositoryRoot $ManifestRelativePath
    $manifestContent = [System.IO.File]::ReadAllText($manifestFull)
    $manifest = Test-ManifestContent $manifestContent "working:$ManifestRelativePath"
    if (-not $IntegrityOnly) { Assert-RequiredFiles $manifest 'working' }
    Write-Output "validation assets PASS: mode=LocalCandidate required=$($manifest.expected_required_count) generation=$($manifest.generation)"
    exit 0
}

if ($Mode -eq 'StagedChangeset') {
    $manifestResult = Invoke-GitText @('show',":$ManifestRelativePath")
    $manifest = Test-ManifestContent $manifestResult.Text "index:$ManifestRelativePath"
    Assert-RequiredFiles $manifest 'index'
    $stagedIgnore = (Invoke-GitText @('show',':.gitignore')).Text
    foreach ($testAsset in @($manifest.assets | Where-Object { $_.required -and $_.artifact_class -eq 'python_test' })) {
        $exactRule = '!' + [string]$testAsset.path
        if (@($stagedIgnore -split "`r?`n" | Where-Object { $_ -ceq $exactRule }).Count -ne 1) { throw "missing exact staged .gitignore rule: $exactRule" }
    }
    Write-Output "validation assets PASS: mode=StagedChangeset(materialized) required=$($manifest.expected_required_count) generation=$($manifest.generation)"
    exit 0
}

if ($Mode -eq 'CleanCheckout') {
    $head = (Invoke-GitText @('rev-parse','HEAD')).Text.Trim()
    $resolvedTarget = (Invoke-GitText @('rev-parse',$TargetCommit)).Text.Trim()
    if ($head -ne $resolvedTarget) { throw 'clean checkout HEAD/target mismatch' }
    if (-not [string]::IsNullOrWhiteSpace((Invoke-GitText @('status','--porcelain=v1','-uall')).Text)) { throw 'materialized checkout is dirty' }
    $manifestFull = Join-Path $ValidatedRepositoryRoot $ManifestRelativePath
    $manifest = Test-ManifestContent ([System.IO.File]::ReadAllText($manifestFull)) "commit:$resolvedTarget`:$ManifestRelativePath"
    Assert-RequiredFiles $manifest 'checkout'
    Write-Output "validation assets PASS: mode=CleanCheckout(materialized) required=$($manifest.expected_required_count) generation=$($manifest.generation)"
    exit 0
}

throw "unsupported validation state: $Mode"
