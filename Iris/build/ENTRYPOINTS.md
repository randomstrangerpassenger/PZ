# Iris Build and Validation Entrypoints

Status: current human command literal owner

All commands require an explicit repository root and repository-external output roots. The installed wheel owns build and install implementations. Validation membership and verdict remain owned by `Iris/validation`; the CLI only delegates to that authority.

## Installed CLI

From an environment containing the exact `iris-tooling` wheel:

```powershell
iris-tooling --repository-root <repo> build classification --output-root <external-empty-root>
iris-tooling --repository-root <repo> build rightclick <arguments>
iris-tooling --repository-root <repo> build layer3 <arguments>
iris-tooling --repository-root <repo> build layer4 <arguments>
iris-tooling --repository-root <repo> build public-text <arguments>
iris-tooling --repository-root <repo> install classification --candidate-root <external-candidate-root> --manifest-sha256 <sha256>
iris-tooling --repository-root <repo> inspect current
```

`classification`, `rightclick`, `layer3`, `layer4`, and `public-text` remain compatibility aliases for their corresponding `build` targets. They are projections of the same package owners, not separate authorities.

## Receipt-bound full validation

The canonical CLI adapter invokes the repository-owned receipt-bound launcher:

```powershell
iris-tooling --repository-root <repo> validate full --commit <commit> --claim-id <claim-id> --environment-receipt <external-environment-receipt> --work-root <external-empty-work-root> --result-root <external-empty-result-root> --orchestration-receipt <external-new-orchestration-receipt>
```

The owning launcher is `Iris/validation/clean_checkout/invoke_receipt_bound_full_gate.ps1`; deterministic comparison is owned by `Iris/validation/clean_checkout/invoke_deterministic_compare.ps1`. Their parameters, validation membership, applicability, and verdict must not be reproduced in wrappers or documentation.

## Current and historical route selection

The exact read-only current denominator is:

```powershell
uv run python .\Iris\_docs\round3\round3_run_contract_tests.py --class current --list
```

Historical and diagnostic routes are opt-in only:

```powershell
uv run python .\Iris\_docs\round3\round3_run_contract_tests.py --class historical --list
uv run python .\Iris\_docs\round3\round3_run_contract_tests.py --class diagnostic --list
```

## Package output

Runtime packaging remains a separate repository-owned command:

```powershell
powershell -ExecutionPolicy Bypass -File .\Iris\tools\package_iris.ps1 -OutputRoot <external-package-root> -Clean -Zip -PackageApplicability current_runtime_payload
```

Direct execution of retired `Iris/build/description/v2/tools/build` copies is not a current command. Historical evidence may mention predecessor commands without re-adopting them.
