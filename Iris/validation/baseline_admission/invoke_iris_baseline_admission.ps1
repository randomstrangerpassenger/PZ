[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][ValidateSet('Forensic', 'Qualify')][string]$Mode,
    [Parameter(Mandatory = $true)][string]$RepositoryRoot,
    [string]$ResultRoot,
    [Parameter(Mandatory = $true)][string]$Receipt,
    [string]$Commit,
    [string]$DeterminismCheckoutSlot,
    [string]$RunAWorkRoot,
    [string]$RunAResultRoot,
    [string]$RunBWorkRoot,
    [string]$RunBResultRoot,
    [string]$PathControlCheckoutRoot,
    [string]$PathControlWorkRoot,
    [string]$PathControlResultRoot,
    [string]$EnvironmentReceipt,
    [string]$DurableRoot,
    [string]$PredecessorStageReceiptSet,
    [string]$QualificationContract
)

$ErrorActionPreference = 'Stop'
$repo = [System.IO.Path]::GetFullPath($RepositoryRoot)
$receipt = [System.IO.Path]::GetFullPath($Receipt)
$runner = Join-Path $PSScriptRoot 'run_iris_baseline_admission.py'
if ($Mode -eq 'Forensic') {
    if ([string]::IsNullOrWhiteSpace($ResultRoot)) { throw 'Forensic mode requires ResultRoot' }
    $result = [System.IO.Path]::GetFullPath($ResultRoot)
    if ($result.StartsWith($repo, [System.StringComparison]::OrdinalIgnoreCase) -or $receipt.StartsWith($repo, [System.StringComparison]::OrdinalIgnoreCase)) { throw 'baseline admission result and receipt paths must be repository-external' }
    & uv run python -B $runner forensic --repo $repo --result-root $result --out $receipt
    exit $LASTEXITCODE
}
$required = @('Commit','DeterminismCheckoutSlot','RunAWorkRoot','RunAResultRoot','RunBWorkRoot','RunBResultRoot','PathControlCheckoutRoot','PathControlWorkRoot','PathControlResultRoot','EnvironmentReceipt','DurableRoot','PredecessorStageReceiptSet','QualificationContract')
foreach ($name in $required) { if ([string]::IsNullOrWhiteSpace([string](Get-Variable -Name $name -ValueOnly))) { throw "Qualify mode requires $name" } }
& uv run python -B $runner qualify --repo $repo --commit $Commit --determinism-checkout-slot $DeterminismCheckoutSlot --run-a-work-root $RunAWorkRoot --run-a-result-root $RunAResultRoot --run-b-work-root $RunBWorkRoot --run-b-result-root $RunBResultRoot --path-control-checkout-root $PathControlCheckoutRoot --path-control-work-root $PathControlWorkRoot --path-control-result-root $PathControlResultRoot --environment-receipt $EnvironmentReceipt --durable-root $DurableRoot --predecessor-stage-receipt-set $PredecessorStageReceiptSet --qualification-contract $QualificationContract --out $receipt
exit $LASTEXITCODE
