# Pulse Update Checker (Windows PowerShell)
# Checks GitHub Releases for the latest Pulse version
# Usage: .\check-pulse-update.ps1 [-CurrentVersion "1.0.0"]

param(
    [string]$CurrentVersion = "",
    [switch]$Silent = $false,
    [switch]$DownloadLink = $false
)

$repo = "randomstrangerpassenger/Pulse"
$apiUrl = "https://api.github.com/repos/$repo/releases/latest"

function Write-Status {
    param([string]$Message, [string]$Color = "White")
    if (-not $Silent) {
        Write-Host $Message -ForegroundColor $Color
    }
}

try {
    # Read current version from file if not specified
    if ([string]::IsNullOrEmpty($CurrentVersion)) {
        $versionFile = Join-Path $PSScriptRoot "..\pulse-version.txt"
        if (Test-Path $versionFile) {
            $CurrentVersion = (Get-Content $versionFile -Raw).Trim()
        } else {
            $CurrentVersion = "Unknown"
        }
    }

    Write-Status "Checking for Pulse updates..." "Cyan"
    Write-Status "Current version: $CurrentVersion" "Gray"
    
    # Query GitHub API
    $response = Invoke-RestMethod -Uri $apiUrl -Method Get -TimeoutSec 10 -ErrorAction Stop
    
    $latestVersion = $response.tag_name -replace '^v', ''
    $releaseUrl = $response.html_url
    $publishedAt = $response.published_at
    $releaseNotes = $response.body
    
    Write-Status "Latest version: $latestVersion" "Gray"
    
    # Compare versions
    $currentParts = $CurrentVersion -split '\.' | ForEach-Object { [int]$_ }
    $latestParts = $latestVersion -split '\.' | ForEach-Object { [int]$_ }
    
    $needsUpdate = $false
    for ($i = 0; $i -lt [Math]::Max($currentParts.Count, $latestParts.Count); $i++) {
        $current = if ($i -lt $currentParts.Count) { $currentParts[$i] } else { 0 }
        $latest = if ($i -lt $latestParts.Count) { $latestParts[$i] } else { 0 }
        
        if ($latest -gt $current) {
            $needsUpdate = $true
            break
        } elseif ($latest -lt $current) {
            break
        }
    }
    
    if ($needsUpdate) {
        Write-Status "" 
        Write-Status "========================================" "Yellow"
        Write-Status "  UPDATE AVAILABLE!" "Yellow"
        Write-Status "========================================" "Yellow"
        Write-Status "  Current: $CurrentVersion" "White"
        Write-Status "  Latest:  $latestVersion" "Green"
        Write-Status "  Released: $publishedAt" "Gray"
        Write-Status "========================================" "Yellow"
        Write-Status ""
        Write-Status "Download: $releaseUrl" "Cyan"
        Write-Status ""
        
        if ($DownloadLink) {
            # Find the JAR asset
            $jarAsset = $response.assets | Where-Object { $_.name -like "*.jar" } | Select-Object -First 1
            if ($jarAsset) {
                Write-Status "Direct download: $($jarAsset.browser_download_url)" "Green"
            }
        }
        
        return @{
            UpdateAvailable = $true
            CurrentVersion = $CurrentVersion
            LatestVersion = $latestVersion
            DownloadUrl = $releaseUrl
        }
    } else {
        Write-Status ""
        Write-Status "You are running the latest version!" "Green"
        Write-Status ""
        
        return @{
            UpdateAvailable = $false
            CurrentVersion = $CurrentVersion
            LatestVersion = $latestVersion
        }
    }
    
} catch [System.Net.WebException] {
    Write-Status "Could not check for updates (network error)" "Yellow"
    Write-Status "Please check your internet connection." "Gray"
    return @{ UpdateAvailable = $false; Error = "Network error" }
    
} catch {
    Write-Status "Could not check for updates" "Yellow"
    Write-Status "Error: $($_.Exception.Message)" "Gray"
    return @{ UpdateAvailable = $false; Error = $_.Exception.Message }
}
