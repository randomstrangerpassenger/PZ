[CmdletBinding()]
param(
    [string[]]$ProtectedRepositoryRoots,
    [string]$ProtectedRepositoryRootsJson,
    [Parameter(Mandatory = $true)][string]$ClaimId,
    [Parameter(Mandatory = $true)][string]$AttemptId,
    [Parameter(Mandatory = $true)]
    [ValidateSet('physical-capacity', 'checkpoint', 'terminal-run-a', 'terminal-run-b')]
    [string]$AllocationProfile,
    [Parameter(Mandatory = $true)][string]$ExternalParent,
    [Parameter(Mandatory = $true)][string]$AllocationLedger,
    [Parameter(Mandatory = $true)][string]$Out,
    [string]$RunId,
    [ValidateSet('none', 'after-reservation')]
    [string]$TestFailureInjection = 'none'
)

$ErrorActionPreference = 'Stop'

function Get-NormalizedPath([string]$Path) {
    return [System.IO.Path]::GetFullPath($Path).TrimEnd('\', '/')
}

function Test-SameOrNested([string]$Left, [string]$Right) {
    $leftPath = Get-NormalizedPath $Left
    $rightPath = Get-NormalizedPath $Right
    return (
        $leftPath.Equals($rightPath, [System.StringComparison]::OrdinalIgnoreCase) -or
        $leftPath.StartsWith($rightPath + [System.IO.Path]::DirectorySeparatorChar, [System.StringComparison]::OrdinalIgnoreCase)
    )
}

function Assert-DisjointFromProtected([string]$Candidate, [string]$Label) {
    foreach ($root in $script:ResolvedProtectedRoots) {
        if ((Test-SameOrNested $Candidate $root) -or (Test-SameOrNested $root $Candidate)) {
            throw "$Label must be disjoint from protected repository root: $Candidate <-> $root"
        }
    }
}

function Assert-NoReparseAncestor([string]$Path, [string]$Label) {
    $current = [System.IO.DirectoryInfo]::new((Get-NormalizedPath $Path))
    while ($null -ne $current) {
        if ($current.Exists -and (($current.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0)) {
            throw "$Label traverses a reparse point: $($current.FullName)"
        }
        $current = $current.Parent
    }
}

function Assert-SafeExistingFileLeaf([string]$Path, [string]$Label, [string]$RequiredParent) {
    $item = Get-Item -Force -LiteralPath $Path -ErrorAction SilentlyContinue
    if ($null -eq $item) { return }
    if (($item.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0) {
        throw "$Label leaf is a reparse point: $($item.FullName)"
    }
    if ($item.PSIsContainer) { throw "$Label must be a regular file: $($item.FullName)" }
    $resolvedLeaf = Get-NormalizedPath $item.FullName
    Assert-DisjointFromProtected $resolvedLeaf $Label
    if (-not (Test-SameOrNested $resolvedLeaf $RequiredParent)) {
        throw "$Label resolved leaf must remain beneath the approved external parent: $resolvedLeaf"
    }
}

function Write-JsonNoBomNew([string]$Path, [object]$Payload) {
    $resolved = Get-NormalizedPath $Path
    if ([System.IO.File]::Exists($resolved) -or [System.IO.Directory]::Exists($resolved)) {
        throw "output already exists: $resolved"
    }
    $parent = [System.IO.Path]::GetDirectoryName($resolved)
    [System.IO.Directory]::CreateDirectory($parent) | Out-Null
    $json = $Payload | ConvertTo-Json -Depth 16
    $json = $json.Replace("`r`n", "`n")
    if (-not $json.EndsWith("`n")) { $json += "`n" }
    $temporary = Join-Path $parent ('.' + [System.IO.Path]::GetFileName($resolved) + '.' + [Guid]::NewGuid().ToString('N') + '.tmp')
    [System.IO.File]::WriteAllText($temporary, $json, ([System.Text.UTF8Encoding]::new($false)))
    [System.IO.File]::Move($temporary, $resolved)
}

function Get-Sha256([string]$Path) {
    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
}

$arrayRootsProvided = $null -ne $ProtectedRepositoryRoots -and @($ProtectedRepositoryRoots).Count -gt 0
$jsonRootsProvided = -not [string]::IsNullOrWhiteSpace($ProtectedRepositoryRootsJson)
if ($arrayRootsProvided -eq $jsonRootsProvided) {
    throw 'provide exactly one protected repository roots input'
}
$protectedRootsInput = if ($jsonRootsProvided) {
    try { @(ConvertFrom-Json -InputObject $ProtectedRepositoryRootsJson) }
    catch { throw 'ProtectedRepositoryRootsJson is not valid JSON' }
}
else { @($ProtectedRepositoryRoots) }
if ($protectedRootsInput.Count -eq 0 -or @($protectedRootsInput | Where-Object { [string]::IsNullOrWhiteSpace([string]$_) }).Count -ne 0) {
    throw 'protected repository roots input must contain nonempty paths'
}

$script:ResolvedProtectedRoots = @()
foreach ($root in $protectedRootsInput) {
    $resolved = Get-NormalizedPath $root
    if (-not [System.IO.Directory]::Exists($resolved)) { throw "protected repository root is missing: $resolved" }
    Assert-NoReparseAncestor $resolved 'protected root'
    $script:ResolvedProtectedRoots += $resolved
}
$script:ResolvedProtectedRoots = @($script:ResolvedProtectedRoots | Sort-Object -Unique)

$external = Get-NormalizedPath $ExternalParent
if (-not [System.IO.Directory]::Exists($external)) { throw "external parent must already exist: $external" }
Assert-NoReparseAncestor $external 'external parent'
Assert-DisjointFromProtected $external 'external parent'

$ledger = Get-NormalizedPath $AllocationLedger
$receipt = Get-NormalizedPath $Out
if ($ledger.Equals($receipt, [System.StringComparison]::OrdinalIgnoreCase)) { throw 'allocation ledger and receipt paths must be distinct' }
Assert-DisjointFromProtected $ledger 'allocation ledger'
Assert-DisjointFromProtected $receipt 'allocation receipt'
Assert-SafeExistingFileLeaf $ledger 'allocation ledger' $external
Assert-NoReparseAncestor $ledger 'allocation ledger'
Assert-NoReparseAncestor $receipt 'allocation receipt'
if (-not (Test-SameOrNested $ledger $external)) { throw 'allocation ledger must be beneath the approved external parent' }
if (-not (Test-SameOrNested $receipt $external)) { throw 'allocation receipt must be beneath the approved external parent' }
if ([System.IO.File]::Exists($receipt) -or [System.IO.Directory]::Exists($receipt)) { throw 'allocation receipt already exists' }

$safeClaim = [System.Text.RegularExpressions.Regex]::Replace($ClaimId, '[^A-Za-z0-9._-]', '-')
if ($safeClaim.Length -gt 32) { $safeClaim = $safeClaim.Substring(0, 32) }
$safeAttempt = [System.Text.RegularExpressions.Regex]::Replace($AttemptId, '[^A-Za-z0-9._-]', '-')
if ($safeAttempt.Length -gt 32) { $safeAttempt = $safeAttempt.Substring(0, 32) }
$runIdWasExplicit = -not [string]::IsNullOrWhiteSpace($RunId)
$resolvedRunId = if ($runIdWasExplicit) { $RunId.ToLowerInvariant() } else { [Guid]::NewGuid().ToString('N') }
if ($resolvedRunId -notmatch '^[0-9a-f]{32}$') { throw 'RunId must be a 32-character lowercase hexadecimal GUID form' }
$baseName = switch ($AllocationProfile) {
    'checkpoint' { 'cp-{0}' -f $resolvedRunId.Substring(0, 12) }
    'terminal-run-a' { 'ta-{0}' -f $resolvedRunId.Substring(0, 12) }
    'terminal-run-b' { 'tb-{0}' -f $resolvedRunId.Substring(0, 12) }
    default { '{0}-{1}-{2}-{3}' -f $AllocationProfile, $safeClaim, $safeAttempt, $resolvedRunId.Substring(0, 12) }
}
$base = Join-Path $external $baseName
Assert-DisjointFromProtected $base 'allocation base'
Assert-NoReparseAncestor $base 'allocation base'
if ([System.IO.Directory]::Exists($base) -or [System.IO.File]::Exists($base)) {
    throw "allocation candidate existed before creation: $base"
}
if ($base.Length -gt 220) { throw "allocation base exceeds the approved Windows path budget: $base" }

$rootNames = switch ($AllocationProfile) {
    'physical-capacity' {
        [ordered]@{
            inventory_result = 'inventory-result'
            promotion_result = 'promotion-result'
            archive_store = 'archive-store'
            restore_result = 'restore-result'
            terminal_inventory_result = 'terminal-inventory-result'
        }
    }
    'checkpoint' {
        [ordered]@{
            work = 'work'
            result = 'result'
            current_result = 'current-result'
            historical_result = 'historical-result'
            diagnostic_raw_result = 'diagnostic-raw-result'
            diagnostic_disposition_result = 'diagnostic-disposition-result'
            package_result = 'package-result'
            orchestration_result = 'orchestration-result'
            compare_result = 'compare-result'
            test_output = 'test-output'
            uv_cache = 'uv-cache'
            uv_environment = 'uv-environment'
        }
    }
    'terminal-run-a' {
        [ordered]@{
            work = 'work'
            result = 'result'
            current_result = 'current-result'
            historical_result = 'historical-result'
            diagnostic_raw_result = 'diagnostic-raw-result'
            diagnostic_disposition_result = 'diagnostic-disposition-result'
            package_result = 'package-result'
            orchestration_result = 'orchestration-result'
            compare_result = 'compare-result'
            test_output = 'test-output'
            uv_cache = 'uv-cache'
            uv_environment = 'uv-environment'
        }
    }
    'terminal-run-b' {
        [ordered]@{
            work = 'work'
            result = 'result'
            orchestration_result = 'orchestration-result'
        }
    }
}

$candidatePaths = @($base)
foreach ($property in $rootNames.GetEnumerator()) {
    $candidatePaths += (Join-Path $base $property.Value)
}

[System.IO.Directory]::CreateDirectory([System.IO.Path]::GetDirectoryName($ledger)) | Out-Null
Assert-NoReparseAncestor $ledger 'allocation ledger'
Assert-NoReparseAncestor $receipt 'allocation receipt'
Assert-SafeExistingFileLeaf $ledger 'allocation ledger' $external
$ledgerStream = $null
$ledgerHashAfterAppend = $null
$ledgerEntryHash = $null
$ledgerAppendOffset = $null
$reservationLedgerHashAfterAppend = $null
$reservationEntryHash = $null
$reservationAppendOffset = $null
try {
    $ledgerStream = [System.IO.File]::Open(
        $ledger,
        [System.IO.FileMode]::OpenOrCreate,
        [System.IO.FileAccess]::ReadWrite,
        [System.IO.FileShare]::None
    )
    $reader = [System.IO.StreamReader]::new($ledgerStream, ([System.Text.UTF8Encoding]::new($false)), $true, 4096, $true)
    $ledgerText = $reader.ReadToEnd()
    $reader.Dispose()
    $usedPaths = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::OrdinalIgnoreCase)
    foreach ($line in ($ledgerText -split "`r?`n")) {
        if ([string]::IsNullOrWhiteSpace($line)) { continue }
        $entry = $line | ConvertFrom-Json
        foreach ($path in @($entry.paths)) { [void]$usedPaths.Add((Get-NormalizedPath ([string]$path))) }
    }
    foreach ($path in $candidatePaths) {
        $normalized = Get-NormalizedPath $path
        if ([System.IO.Directory]::Exists($normalized) -or [System.IO.File]::Exists($normalized)) {
            throw "allocation path existed before creation: $normalized"
        }
        if ($usedPaths.Contains($normalized)) { throw "allocation path was used by a prior attempt: $normalized" }
        Assert-DisjointFromProtected $normalized 'allocated root'
    }

    $candidatePathStrings = @($candidatePaths | ForEach-Object { (Get-NormalizedPath $_).Replace('\', '/') })
    $reservationEntry = [ordered]@{
        schema_version = 'iris_repository_runtime_lightweighting_allocation_ledger_v2'
        state = 'reserved'
        claim_id = $ClaimId
        attempt_id = $AttemptId
        run_id = $resolvedRunId
        run_id_source = if ($runIdWasExplicit) { 'explicit_fixture_or_replay_probe' } else { 'cryptographic_guid_generated' }
        allocation_profile = $AllocationProfile
        base = (Get-NormalizedPath $base).Replace('\', '/')
        paths = $candidatePathStrings
        pre_create_exists_count = 0
        prior_ledger_match_count = 0
    }
    $reservationJson = $reservationEntry | ConvertTo-Json -Depth 8 -Compress
    $reservationEntryBytes = ([System.Text.UTF8Encoding]::new($false)).GetBytes($reservationJson + "`n")
    $reservationSha = [System.Security.Cryptography.SHA256]::Create()
    try { $reservationEntryHash = ([BitConverter]::ToString($reservationSha.ComputeHash($reservationEntryBytes))).Replace('-', '').ToLowerInvariant() }
    finally { $reservationSha.Dispose() }
    $ledgerStream.Seek(0, [System.IO.SeekOrigin]::End) | Out-Null
    $reservationAppendOffset = $ledgerStream.Position
    $reservationWriter = [System.IO.StreamWriter]::new($ledgerStream, ([System.Text.UTF8Encoding]::new($false)), 4096, $true)
    $reservationWriter.Write($reservationJson + "`n")
    $reservationWriter.Flush()
    $reservationWriter.Dispose()
    $ledgerStream.Flush($true)
    $ledgerStream.Seek(0, [System.IO.SeekOrigin]::Begin) | Out-Null
    $reservationLedgerSha = [System.Security.Cryptography.SHA256]::Create()
    try { $reservationLedgerHashAfterAppend = ([BitConverter]::ToString($reservationLedgerSha.ComputeHash($ledgerStream))).Replace('-', '').ToLowerInvariant() }
    finally { $reservationLedgerSha.Dispose() }

    if ($TestFailureInjection -eq 'after-reservation') {
        throw 'injected failure after durable allocation reservation'
    }

    [System.IO.Directory]::CreateDirectory($base) | Out-Null
    Assert-NoReparseAncestor $base 'allocated base'
    $resolvedRoots = [ordered]@{}
    foreach ($property in $rootNames.GetEnumerator()) {
        $path = Get-NormalizedPath (Join-Path $base $property.Value)
        [System.IO.Directory]::CreateDirectory($path) | Out-Null
        Assert-NoReparseAncestor $path 'allocated root'
        if (@([System.IO.Directory]::EnumerateFileSystemEntries($path)).Count -ne 0) {
            throw "new allocation root is not empty: $path"
        }
        $resolvedRoots[$property.Key] = $path.Replace('\', '/')
    }

    $ledgerEntry = [ordered]@{
        schema_version = 'iris_repository_runtime_lightweighting_allocation_ledger_v2'
        state = 'committed'
        reservation_entry_sha256 = $reservationEntryHash
        reservation_append_offset_bytes = $reservationAppendOffset
        claim_id = $ClaimId
        attempt_id = $AttemptId
        run_id = $resolvedRunId
        run_id_source = if ($runIdWasExplicit) { 'explicit_fixture_or_replay_probe' } else { 'cryptographic_guid_generated' }
        allocation_profile = $AllocationProfile
        base = (Get-NormalizedPath $base).Replace('\', '/')
        paths = $candidatePathStrings
        pre_create_exists_count = 0
        prior_ledger_match_count = 0
        post_create_nonempty_count = 0
    }
    $ledgerJson = $ledgerEntry | ConvertTo-Json -Depth 8 -Compress
    $ledgerEntryBytes = ([System.Text.UTF8Encoding]::new($false)).GetBytes($ledgerJson + "`n")
    $entrySha = [System.Security.Cryptography.SHA256]::Create()
    try { $ledgerEntryHash = ([BitConverter]::ToString($entrySha.ComputeHash($ledgerEntryBytes))).Replace('-', '').ToLowerInvariant() }
    finally { $entrySha.Dispose() }
    $ledgerStream.Seek(0, [System.IO.SeekOrigin]::End) | Out-Null
    $ledgerAppendOffset = $ledgerStream.Position
    $writer = [System.IO.StreamWriter]::new($ledgerStream, ([System.Text.UTF8Encoding]::new($false)), 4096, $true)
    $writer.Write($ledgerJson + "`n")
    $writer.Flush()
    $writer.Dispose()
    $ledgerStream.Flush($true)
    $ledgerStream.Seek(0, [System.IO.SeekOrigin]::Begin) | Out-Null
    $ledgerSha = [System.Security.Cryptography.SHA256]::Create()
    try { $ledgerHashAfterAppend = ([BitConverter]::ToString($ledgerSha.ComputeHash($ledgerStream))).Replace('-', '').ToLowerInvariant() }
    finally { $ledgerSha.Dispose() }

    $payload = [ordered]@{
        schema_version = 'iris_repository_runtime_lightweighting_allocation_receipt_v1'
        status = 'PASS'
        claim_id = $ClaimId
        attempt_id = $AttemptId
        run_id = $resolvedRunId
        run_id_source = if ($runIdWasExplicit) { 'explicit_fixture_or_replay_probe' } else { 'cryptographic_guid_generated' }
        allocation_profile = $AllocationProfile
        external_parent = $external.Replace('\', '/')
        protected_repository_roots = @($script:ResolvedProtectedRoots | ForEach-Object { $_.Replace('\', '/') })
        allocation_ledger = [ordered]@{
            path = $ledger.Replace('\', '/')
            sha256_after_append = $ledgerHashAfterAppend
            appended_entry_sha256 = $ledgerEntryHash
            append_offset_bytes = $ledgerAppendOffset
            reservation_ledger_sha256_after_append = $reservationLedgerHashAfterAppend
            reservation_entry_sha256 = $reservationEntryHash
            reservation_append_offset_bytes = $reservationAppendOffset
        }
        base = (Get-NormalizedPath $base).Replace('\', '/')
        roots = $resolvedRoots
        pre_create_existence = [ordered]@{ checked = $true; existing_count = 0 }
        ledger_reuse = [ordered]@{ checked = $true; match_count = 0 }
        post_create_empty = [ordered]@{ checked = $true; nonempty_count = 0 }
        lifecycle_disposition = if ($AllocationProfile -eq 'terminal-run-b') {
            [ordered]@{
                unused_axes = 'not_created'
                reason = 'not_required_for_run_b_profile'
                empty_verified = $true
                delete_eligible_after_closeout = $true
            }
        }
        else { [ordered]@{ unused_axes = @() } }
    }
    if ($null -ne $ledgerStream) { $ledgerStream.Dispose(); $ledgerStream = $null }
    Assert-NoReparseAncestor $receipt 'allocation receipt'
    Write-JsonNoBomNew $receipt $payload
}
finally {
    if ($null -ne $ledgerStream) { $ledgerStream.Dispose() }
}

Write-Output (([ordered]@{ status = 'PASS'; run_id = $resolvedRunId; allocation_profile = $AllocationProfile; receipt = $receipt.Replace('\', '/') }) | ConvertTo-Json -Compress)
