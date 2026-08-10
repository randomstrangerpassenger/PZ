[CmdletBinding()]
param([Parameter(Mandatory = $true)][string]$DataRoot)

$ErrorActionPreference = 'Stop'
$scriptRoot = if ($PSScriptRoot) { $PSScriptRoot } else { Split-Path -Parent $MyInvocation.MyCommand.Path }
Import-Module -Name (Join-Path $scriptRoot 'RuntimeLookupIndexIdentity.psm1') -Force
$identity = Assert-RuntimeLookupPackageParity -DataRoot $DataRoot
$result = [ordered]@{
    status = $identity.status
    validator = 'runtime_lookup_package_parity'
    generation_id = $identity.generation_id
    source_digest = $identity.source_digest
    layer3_entry_count = $identity.layer3_entry_count
    usecase_entry_count = $identity.usecase_entry_count
    line_count_entry_count = $identity.line_count_entry_count
}
Write-Output ($result | ConvertTo-Json -Compress)
