# Round 3 Closeout Report

Generated: `2026-06-11T21:30:09+09:00`

## Closeout Status

Round 3 is closed for build script / test contract disentanglement.

## Final Contract Split

| Surface | Count | Default? | Command |
|---|---:|---|---|
| current | 44 tests | yes | `python -B Iris\_docs\round3\round3_run_contract_tests.py --class current --enforce-current-build-closure` |
| historical | 284 tests | no | `python -B Iris\_docs\round3\round3_run_contract_tests.py --class historical` |
| diagnostic | 79 tests | no | `python -B Iris\_docs\round3\round3_run_contract_tests.py --class diagnostic` |

Current tests are guarded by the 12-module active build closure recorded in
`Iris/_docs/round3/round3_active_core_closure.json`.

Pytest default route is now also current-only for description-v2:

- `python -B -m pytest -q` -> 45 passed, 363 deselected, 5 subtests passed
- explicit historical pytest route -> 284 passed
- explicit diagnostic pytest route -> 79 passed

## Disposition Result

| Disposition | Count |
|---|---:|
| keep_current_core | 12 |
| keep_historical_reproduction | 173 |
| keep_diagnostic_advisory | 95 |
| keep_manifest_only | 1 |
| archive/delete eligible | 0 |

No file was moved, archived, deleted, or removed from `.gitignore`.

The single manifest-only retained row is:

- `Iris/build/description/v2/tools/build/validate_interaction_cluster_seed.py`

## D3 Historical Preservation Policy

D3 selected `pass_required`. The sealed historical route ran 284 tests and
exited successfully, so the historical executable route is preserved for this
round's measured contract.

Full historical artifact byte reproducibility was audited separately and remains
fail-loud unresolved because all 281 artifact dependency rows have unresolved
production mappings and no byte-parity rows are proven.

## Release Gate

Automated release/package gates passed for this round:

- default pytest
- historical and diagnostic pytest routes
- legacy full unittest discovery
- current contract runner
- boundary guard
- Lua syntax
- `Iris/tools/package_iris.ps1 -Clean -Zip`
- package manifest and forbidden-path checks

## Claim Boundary

This closeout claims contract separation, default current-route narrowing for
unittest-compatible runner and pytest, explicit historical/diagnostic routes,
evidence-based non-destructive disposition, and automated package-gate
readiness. It does not claim runtime equivalence, in-game manual QA, Workshop
publication readiness, full historical artifact byte reproducibility, or
universal script deletion safety.
