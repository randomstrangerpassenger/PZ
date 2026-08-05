[CmdletBinding()]
param([Parameter(Mandatory = $true)][string]$DataRoot)

$ErrorActionPreference = 'Stop'
$scriptRoot = if ($PSScriptRoot) { $PSScriptRoot } else { Split-Path -Parent $MyInvocation.MyCommand.Path }
Import-Module -Name (Join-Path $scriptRoot 'RuntimeLookupIndexIdentity.psm1') -Force
Assert-RuntimeLookupIndexIdentity -DataRoot $DataRoot -IndexName 'IrisLayer3DataChunkIndex.lua'
Assert-RuntimeLookupIndexIdentity -DataRoot $DataRoot -IndexName 'UseCaseDescriptions/ChunkIndex.lua'
Assert-RuntimeLookupIndexIdentity -DataRoot $DataRoot -IndexName 'UseCaseDescriptions/LineCountIndex.lua'
Write-Output '{"status":"PASS","validator":"runtime_lookup_index_identity"}'
