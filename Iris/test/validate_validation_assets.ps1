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
$ApprovalAuthorityRelativePath = 'Iris/_docs/refactor/core_refactor/phase9_protected_surface_approval_authority.json'
$ApprovalAuthorityCommit = 'dd732e1fb7f529da40befdd3b658571aa898031f'
$ApprovalAuthorityBlob = '7aebc178d8a0b1716f131f7b6a7c5f046b888244'
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

function Remove-LongPathDirectoryTree([string]$Path) {
    $resolved = [System.IO.Path]::GetFullPath($Path)
    if (-not [System.IO.Directory]::Exists($resolved)) { return }
    $deletePath = if ([System.IO.Path]::DirectorySeparatorChar -eq '\') {
        '\\?\' + $resolved
    }
    else { $resolved }
    foreach ($file in [System.IO.Directory]::EnumerateFiles(
        $deletePath, '*', [System.IO.SearchOption]::AllDirectories
    )) {
        [System.IO.File]::SetAttributes($file, [System.IO.FileAttributes]::Normal)
    }
    foreach ($directory in [System.IO.Directory]::EnumerateDirectories(
        $deletePath, '*', [System.IO.SearchOption]::AllDirectories
    )) {
        [System.IO.File]::SetAttributes(
            $directory, [System.IO.FileAttributes]::Directory
        )
    }
    [System.IO.Directory]::Delete($deletePath, $true)
}

function Get-PinnedProtectedApproval([string]$SnapshotRoot) {
    & git -C $SnapshotRoot merge-base --is-ancestor $ApprovalAuthorityCommit HEAD 2>$null
    if ($LASTEXITCODE -ne 0) { throw 'pinned protected approval commit is not an ancestor of HEAD' }
    $actualBlob = (& git -C $SnapshotRoot rev-parse "$ApprovalAuthorityCommit`:$ApprovalAuthorityRelativePath" 2>$null | Out-String).Trim()
    if ($LASTEXITCODE -ne 0 -or $actualBlob -cne $ApprovalAuthorityBlob) { throw 'pinned protected approval blob mismatch' }
    $authorityText = (& git -C $SnapshotRoot show "$ApprovalAuthorityCommit`:$ApprovalAuthorityRelativePath" 2>$null | Out-String)
    if ($LASTEXITCODE -ne 0) { throw 'cannot read pinned protected approval authority' }
    $authority = $authorityText | ConvertFrom-Json
    if ([long]$authority.schema_version -ne 1 -or [string]$authority.authority_kind -cne 'owner_preauthorization_record' -or [string]$authority.scope -cne 'one_time_exact_current_route_authority_rebind') { throw 'invalid pinned protected approval authority' }
    $approved = $authority.approved_change
    if ([string]$approved.path -cne 'Iris/_docs/round3/current_route_required_validations.json' -or
        [string]$approved.before_sha256 -cne 'ef586ef40a45f3b1c448f0220d30aff18fff3f1d359fe0f02d14d48b5de1df14' -or
        [string]$approved.after_sha256 -cne '82be732a2e3a2b4f5a7deae342ceda93a59990dca0543f6ca7b7b82dc0c18d66' -or
        [bool]$authority.constraints.additional_protected_paths_allowed -or
        [bool]$authority.constraints.runtime_or_public_text_change_allowed -or
        [bool]$authority.constraints.existing_package_peer_change_allowed) {
        throw 'pinned protected approval scope mismatch'
    }
    return @{ ([string]$approved.path) = [string]$approved.after_sha256 }
}

function Get-ProtectedSnapshot([string]$Root, [switch]$TrackedOnly) {
    $snapshotRoot = if ($Root) { $Root } else { $script:ValidatedRepositoryRoot }
    $manifestPath = Join-Path $snapshotRoot 'Iris/_docs/refactor/core_refactor/phase0_protected_surface_manifest.json'
    $protectedManifest = [System.IO.File]::ReadAllText($manifestPath) | ConvertFrom-Json
    $approvedExpected = Get-PinnedProtectedApproval $snapshotRoot
    $rows = @()
    $changed = 0
    $approvedChanged = 0
    foreach ($row in @($protectedManifest.rows)) {
        if ($TrackedOnly -and -not [bool]$row.tracked) { continue }
        $optionalReadOnlyPeer = -not [bool]$row.tracked -and [string]$row.hash_policy -ceq 'read_only_pre_post'
        $full = Join-Path $snapshotRoot ([string]$row.path)
        if (-not (Test-Path -LiteralPath $full -PathType Leaf)) {
            if ($optionalReadOnlyPeer) {
                $rows += "$($row.path)`tabsent_optional_peer"
                continue
            }
            throw "protected surface missing: $($row.path)"
        }
        $actual = Get-Sha256File $full
        $expected = if ($optionalReadOnlyPeer) { $actual } else { [string]$row.sha256 }
        if ($approvedExpected.ContainsKey([string]$row.path)) {
            $expected = $approvedExpected[[string]$row.path]
            $approvedChanged += 1
        }
        $matchesExpected = $actual -eq $expected
        if (-not $matchesExpected -and [System.IO.Path]::GetExtension($full).ToLowerInvariant() -ne '.zip') {
            $normalizedText = [System.IO.File]::ReadAllText($full).Replace("`r`n", "`n")
            $normalized = Get-Sha256Bytes $Utf8NoBom.GetBytes($normalizedText)
            $matchesExpected = $normalized -eq $expected
        }
        if (-not $matchesExpected) { $changed += 1 }
        $canonicalIdentity = if ($matchesExpected) { $expected } else { $actual }
        $rows += "$($row.path)`t$canonicalIdentity"
    }
    [System.Array]::Sort($rows, [System.StringComparer]::Ordinal)
    $canonical = ($rows -join "`n") + $(if ($rows.Count -gt 0) { "`n" } else { '' })
    return [pscustomobject]@{ RowCount=$rows.Count; ChangedCount=$changed; ApprovedChangedCount=$approvedChanged; Sha256=Get-Sha256Bytes $Utf8NoBom.GetBytes($canonical) }
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
    if ((-not ($assetManifest.reserved_future_count -is [int])) -and (-not ($assetManifest.reserved_future_count -is [long]))) { throw 'reserved_future_count must be an integer' }
    if ([long]$assetManifest.reserved_future_count -lt 0) { throw 'reserved_future_count must be non-negative' }
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
    if ($reservedFutureAssets.Count -ne [long]$assetManifest.reserved_future_count) { throw 'reserved future count mismatch' }
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
    $workPrefix = $validatedWorkRoot.TrimEnd('\','/') + [System.IO.Path]::DirectorySeparatorChar
    $resultPrefix = $validatedResultRoot.TrimEnd('\','/') + [System.IO.Path]::DirectorySeparatorChar
    if ($validatedWorkRoot.Equals($validatedResultRoot, [System.StringComparison]::OrdinalIgnoreCase) -or
        $validatedWorkRoot.StartsWith($resultPrefix, [System.StringComparison]::OrdinalIgnoreCase) -or
        $validatedResultRoot.StartsWith($workPrefix, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw 'WorkRoot and ResultRoot must be disjoint and non-containing'
    }
    if (Test-Path -LiteralPath $validatedWorkRoot) { throw 'WorkRoot must not exist' }
    if (Test-Path -LiteralPath $validatedResultRoot) { throw 'ResultRoot must not exist' }
    $sourceStatusBefore = (Invoke-GitText @('status','--porcelain=v1','-uall')).Text
    $sourceProtectedBefore = Get-ProtectedSnapshot
    New-Item -ItemType Directory -Path $validatedResultRoot | Out-Null
    $stdoutPath = Join-Path $validatedResultRoot 'stdout.txt'
    $stderrPath = Join-Path $validatedResultRoot 'stderr.txt'
    $cleanup = $false
    try {
        & git -c core.longpaths=true clone --no-local --no-checkout -- $ValidatedRepositoryRoot $validatedWorkRoot 1>$stdoutPath 2>$stderrPath
        if ($LASTEXITCODE -ne 0) { throw 'external clone failed' }
        & git -c core.longpaths=true -C $validatedWorkRoot checkout --detach $TargetCommit 1>>$stdoutPath 2>>$stderrPath
        if ($LASTEXITCODE -ne 0) { throw 'detached checkout failed' }
        $committedValidator = Join-Path $validatedWorkRoot $ValidatorRelativePath
        & powershell -NoProfile -ExecutionPolicy Bypass -File $committedValidator -Mode CleanCheckout -RepositoryRoot $validatedWorkRoot -TargetCommit $TargetCommit -InternalMaterialized 1>>$stdoutPath 2>>$stderrPath
        if ($LASTEXITCODE -ne 0) { throw 'committed clean-checkout validator failed' }
        $validatedManifestPath = Join-Path $validatedWorkRoot $ManifestRelativePath
        $validatedManifest = [System.IO.File]::ReadAllText($validatedManifestPath) | ConvertFrom-Json
        $validatedManifestSha = Get-Sha256File $validatedManifestPath
        $validatedValidatorSha = Get-Sha256File $committedValidator
        $checkoutProtected = Get-ProtectedSnapshot -Root $validatedWorkRoot -TrackedOnly
    }
    finally {
        if (Test-Path -LiteralPath $validatedWorkRoot) {
            Remove-LongPathDirectoryTree $validatedWorkRoot
        }
        $cleanup = -not (Test-Path -LiteralPath $validatedWorkRoot)
    }
    $sourceStatusAfter = (Invoke-GitText @('status','--porcelain=v1','-uall')).Text
    $sourceProtectedAfter = Get-ProtectedSnapshot
    if ($sourceStatusBefore -cne $sourceStatusAfter) { throw 'source worktree changed during CleanCheckout validation' }
    if ($sourceProtectedBefore.Sha256 -ne $sourceProtectedAfter.Sha256 -or $sourceProtectedAfter.ChangedCount -ne 0) { throw 'source protected surface changed during CleanCheckout validation' }
    if (-not $cleanup) { throw 'disposable checkout cleanup failed' }
    $identity = Invoke-GitText @('show','-s','--format=%H:%T',$TargetCommit)
    $manifestBlob = (Invoke-GitText @('rev-parse',"$TargetCommit`:$ManifestRelativePath")).Text.Trim()
    $validatorBlob = (Invoke-GitText @('rev-parse',"$TargetCommit`:$ValidatorRelativePath")).Text.Trim()
    $receipt = [ordered]@{
        schema_version=1;mode='CleanCheckout';target_identity=$identity.Text.Trim()
        manifest_blob=$manifestBlob;validator_blob=$validatorBlob
        manifest_sha256=$validatedManifestSha;validator_sha256=$validatedValidatorSha
        required_count=[long]$validatedManifest.expected_required_count
        required_asset_ids_sha256=[string]$validatedManifest.expected_required_asset_ids_sha256
        reserved_future_count=[long]$validatedManifest.reserved_future_count;manifest_sealed=[bool]$validatedManifest.sealed
        validation_commands=@(
            'round3 current --enforce-current-build-closure',
            'round3 historical',
            'round3 diagnostic (advisory; non-zero reported but non-blocking)',
            'unittest discover test_*.py'
        )
        validation_commands_status='mandatory_pass_diagnostic_advisory_reported'
        checkout_protected_row_count=$checkoutProtected.RowCount;checkout_protected_sha256=$checkoutProtected.Sha256;checkout_protected_changed_count=$checkoutProtected.ChangedCount;checkout_protected_approved_changed_count=$checkoutProtected.ApprovedChangedCount
        source_status_sha256_before=Get-Sha256Bytes $Utf8NoBom.GetBytes($sourceStatusBefore)
        source_status_sha256_after=Get-Sha256Bytes $Utf8NoBom.GetBytes($sourceStatusAfter)
        source_status_equal=($sourceStatusBefore -ceq $sourceStatusAfter)
        source_protected_row_count=$sourceProtectedAfter.RowCount;source_protected_approved_changed_count=$sourceProtectedAfter.ApprovedChangedCount
        source_protected_sha256_before=$sourceProtectedBefore.Sha256;source_protected_sha256_after=$sourceProtectedAfter.Sha256
        source_protected_equal=($sourceProtectedBefore.Sha256 -eq $sourceProtectedAfter.Sha256)
        checkout_cleanup=$cleanup;work_root=$validatedWorkRoot;result_root=$validatedResultRoot
    }
    $receiptPath = Join-Path $validatedResultRoot 'receipt.json'
    [System.IO.File]::WriteAllText($receiptPath, (($receipt | ConvertTo-Json -Depth 10) + "`n"), $Utf8NoBom)
    $canonical = [ordered]@{status='pass';mode='CleanCheckout';target_commit=$TargetCommit;manifest_sha256=$validatedManifestSha;validator_sha256=$validatedValidatorSha;receipt_sha256=Get-Sha256File $receiptPath;stdout_sha256=Get-Sha256File $stdoutPath;stderr_sha256=Get-Sha256File $stderrPath}
    [System.IO.File]::WriteAllText((Join-Path $validatedResultRoot 'canonical-result.json'), (($canonical | ConvertTo-Json -Compress) + "`n"), $Utf8NoBom)
    Write-Output "validation assets PASS: mode=CleanCheckout result_root=$validatedResultRoot"
    exit 0
}

if ($Mode -eq 'LocalCandidate') {
    $manifestFull = Join-Path $ValidatedRepositoryRoot $ManifestRelativePath
    $manifestContent = [System.IO.File]::ReadAllText($manifestFull)
    $manifest = Test-ManifestContent $manifestContent "working:$ManifestRelativePath"
    if (-not $IntegrityOnly) { Assert-RequiredFiles $manifest 'working' }
    $protected = Get-ProtectedSnapshot
    if ($protected.ChangedCount -ne 0) { throw 'protected surface drift in LocalCandidate' }
    Write-Output "validation assets PASS: mode=LocalCandidate required=$($manifest.expected_required_count) generation=$($manifest.generation) protected=$($protected.RowCount) approved=$($protected.ApprovedChangedCount)"
    exit 0
}

if ($Mode -eq 'StagedChangeset') {
    $manifestResult = Invoke-GitText @('show',":$ManifestRelativePath")
    $manifest = Test-ManifestContent $manifestResult.Text "index:$ManifestRelativePath"
    Assert-RequiredFiles $manifest 'index'
    $protected = Get-ProtectedSnapshot -TrackedOnly
    if ($protected.ChangedCount -ne 0) { throw 'protected surface drift in StagedChangeset' }
    $stagedIgnore = (Invoke-GitText @('show',':.gitignore')).Text
    foreach ($testAsset in @($manifest.assets | Where-Object { $_.required -and $_.artifact_class -eq 'python_test' })) {
        $exactRule = '!' + [string]$testAsset.path
        if (@($stagedIgnore -split "`r?`n" | Where-Object { $_ -ceq $exactRule }).Count -ne 1) { throw "missing exact staged .gitignore rule: $exactRule" }
    }
    Write-Output "validation assets PASS: mode=StagedChangeset(materialized) required=$($manifest.expected_required_count) generation=$($manifest.generation) protected=$($protected.RowCount) approved=$($protected.ApprovedChangedCount)"
    exit 0
}

if ($Mode -eq 'CleanCheckout') {
    $head = (Invoke-GitText @('rev-parse','HEAD')).Text.Trim()
    $resolvedTarget = (Invoke-GitText @('rev-parse',$TargetCommit)).Text.Trim()
    if ($head -ne $resolvedTarget) { throw 'clean checkout HEAD/target mismatch' }
    if (-not [string]::IsNullOrWhiteSpace((Invoke-GitText @('status','--porcelain=v1','-uall')).Text)) { throw 'materialized checkout is dirty' }
    $manifestFull = Join-Path $ValidatedRepositoryRoot $ManifestRelativePath
    $manifest = Test-ManifestContent ([System.IO.File]::ReadAllText($manifestFull)) "commit:$resolvedTarget`:$ManifestRelativePath"
    if (-not $manifest.sealed) { throw 'CleanCheckout requires a sealed final manifest' }
    Assert-RequiredFiles $manifest 'checkout'
    $protected = Get-ProtectedSnapshot -TrackedOnly
    if ($protected.ChangedCount -ne 0) { throw 'tracked protected surface drift in materialized checkout' }
    $python = (Get-Command python -ErrorAction Stop).Source
    Push-Location $ValidatedRepositoryRoot
    try {
        & $python -B 'Iris/_docs/round3/round3_run_contract_tests.py' --class current --enforce-current-build-closure
        if ($LASTEXITCODE -ne 0) { throw 'clean-checkout current route failed' }
        & $python -B 'Iris/_docs/round3/round3_run_contract_tests.py' --class historical
        if ($LASTEXITCODE -ne 0) { throw 'clean-checkout historical route failed' }
        & $python -B 'Iris/_docs/round3/round3_run_contract_tests.py' --class diagnostic
        $diagnosticExitCode = $LASTEXITCODE
        Write-Output "clean-checkout diagnostic advisory exit code: $diagnosticExitCode"
        & $python -B -m unittest discover -s 'Iris/build/description/v2/tests' -p 'test_*.py'
        if ($LASTEXITCODE -ne 0) { throw 'clean-checkout full v2 Python discovery failed' }
    }
    finally { Pop-Location }
    Write-Output "validation assets PASS: mode=CleanCheckout(materialized) required=$($manifest.expected_required_count) generation=$($manifest.generation) protected=$($protected.RowCount)"
    exit 0
}

throw "unsupported validation state: $Mode"
