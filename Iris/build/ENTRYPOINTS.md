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
iris-tooling --repository-root <repo> build tooltip-t1 --output-root <external-empty-root> --decision-contract-sha256 <sha256> --verify-invariants
iris-tooling --repository-root <repo> finalize tooltip-t1 --candidate-root <external-candidate-root> --candidate-run-receipt-sha256 <sha256> --run-a-orchestration-receipt <external-receipt> --run-b-orchestration-receipt <external-receipt> --comparator-receipt <external-receipt> --output-root <external-empty-root>
iris-tooling --repository-root <repo> install classification --candidate-root <external-candidate-root> --manifest-sha256 <sha256>
iris-tooling --repository-root <repo> inspect current
```

`classification`, `rightclick`, `layer3`, `layer4`, and `public-text` remain compatibility aliases for their corresponding `build` targets. They are projections of the same package owners, not separate authorities. `tooltip-t1` is lifecycle-bound and has no legacy compatibility alias.

`tooltip-t1` reads only the owner-bound current Classification, pointer-selected Layer 3, current Layer 4 owner data, translation, Browser/Menu consumer, and Tooltip sources. It does not consume `Iris/build/baseline/**` as semantic authority. It writes a new immutable audit result only to the supplied repository-external empty root. A blocked T2 progression emits the cause-attributed progression record and does not emit T2 handoff input.

`finalize tooltip-t1` is a narrow post-gate binder, not a semantic producer. It verifies the candidate artifact hashes, candidate `partial/implemented_only` state, exact subject, two successful canonical orchestration/inner result receipts, and their successful deterministic comparator receipt before writing one complete closeout record to a repository-external empty root. Any failed gate, hash failure, or subject mismatch exits nonzero without a complete closeout.

The lifecycle-bound Tooltip T1 focused test command is:

```powershell
uv run --project .\Iris\tooling python -B -m pytest .\Iris\tooling\tests\test_tooltip_t1_contract.py .\Iris\tooling\tests\test_tooltip_t1_projection.py .\Iris\tooling\tests\test_tooltip_t1_audit.py -q
```

These six parameterized test families and the repository-external audit are lifecycle evidence. They are not added to regular validation membership by this adoption.

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
