param(
    [string[]] $Roots = @(
        "Iris\media\lua",
        "Iris\build\package\Iris\media\lua"
    )
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot
$Luac = Get-Command luac -ErrorAction SilentlyContinue

if ($null -eq $Luac) {
    Write-Error "luac executable is required for Lua syntax validation."
    exit 2
}

$Files = @()
foreach ($Root in $Roots) {
    $ResolvedRoot = Join-Path $RepoRoot $Root
    if (Test-Path -LiteralPath $ResolvedRoot) {
        $Files += Get-ChildItem -LiteralPath $ResolvedRoot -Recurse -File -Filter "*.lua"
    }
}

$Files = $Files | Sort-Object FullName -Unique
if ($Files.Count -eq 0) {
    Write-Error "No Lua files found under requested roots: $($Roots -join ', ')"
    exit 2
}

$Failures = @()
foreach ($File in $Files) {
    $Output = & $Luac.Source -p $File.FullName 2>&1
    if ($LASTEXITCODE -ne 0) {
        $Failures += [pscustomobject]@{
            Path = $File.FullName
            Output = ($Output -join "`n")
        }
    }
}

if ($Failures.Count -gt 0) {
    Write-Host "Lua syntax validation failed: $($Failures.Count) / $($Files.Count)"
    foreach ($Failure in $Failures) {
        Write-Host ""
        Write-Host $Failure.Path
        Write-Host $Failure.Output
    }
    exit 1
}

Write-Host "Lua syntax validation OK: $($Files.Count) files"
exit 0
