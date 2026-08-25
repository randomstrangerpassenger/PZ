[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$DataRoot,
    [string]$ExpectedGenerationId = ''
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$scriptRoot = if ($PSScriptRoot) { $PSScriptRoot } else { Split-Path -Parent $MyInvocation.MyCommand.Path }
Import-Module -Name (Join-Path $scriptRoot 'Layer3PackageProjection.psm1') -Force

$result = Assert-IrisLayer3PackageProjection `
    -DataRoot $DataRoot `
    -ExpectedGenerationId $ExpectedGenerationId
$result | ConvertTo-Json -Depth 4
