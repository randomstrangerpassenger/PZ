# Round 3 Discovery Reconciliation

Generated after D1 approval on `2026-06-11`.

## D1 Decision

```text
gate_id: D1
decision: approved
approved_by: user in current Codex chat
timestamp: 2026-06-11T21:18:56+09:00
allowed_scope: Change 4 unittest-compatible manifest runner route; no pytest routing; no test moves
blocked_scope: pytest routing; physical test moves; archive/delete/disposition
evidence_artifact: Iris/_docs/round3/round3_discovery_reconciliation.md
status: approved
```

## Sealed Commands

Current default contract route:

```powershell
python -B Iris\_docs\round3\round3_run_contract_tests.py --class current --enforce-current-build-closure
```

Historical reproduction route:

```powershell
python -B Iris\_docs\round3\round3_run_contract_tests.py --class historical
```

Diagnostic/advisory route:

```powershell
python -B Iris\_docs\round3\round3_run_contract_tests.py --class diagnostic
```

Boundary guard:

```powershell
python -B Iris\_docs\round3\round3_boundary_guard.py --self-test
```

## Results

| Route | Test Count | Closure Enforced | Exit | Report |
| --- | ---: | --- | ---: | --- |
| current | 44 | true | 0 | `Iris/_docs/round3/round3_current_test_run.json` |
| historical | 284 | false | 0 | `Iris/_docs/round3/round3_historical_test_run.json` |
| diagnostic | 79 | false | 0 | `Iris/_docs/round3/round3_diagnostic_test_run.json` |
| boundary guard | n/a | n/a | 0 | `Iris/_docs/round3/round3_boundary_guard_report.json` |

Legacy full discovery baseline:

```powershell
python -B -m unittest discover -s Iris\build\description\v2\tests -p "test_*.py"
```

Result: `407 tests / OK`.

Reconciliation:

```text
current 44 + historical 284 + diagnostic 79 = 407
```

The current route includes the manual-audited `test_compose_layer3_text_overlay.py` rows. The current route also enforces the `tools.build` current closure at import time, so any current test importing an out-of-closure `tools.build.*` module fails loud.

## Claim Boundary

This records test-contract separation only. It does not approve archive/delete/disposition, release readiness, runtime equivalence, package readiness, or full historical preservation policy. D2 and D3 remain separate gates.
