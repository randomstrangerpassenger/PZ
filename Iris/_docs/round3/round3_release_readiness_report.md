# Round 3 Automated Release Readiness Report

Generated: `2026-06-11T21:51:00+09:00`

## Automated Gates

| Gate | Command | Result |
|---|---|---|
| default current pytest | `python -B -m pytest -q` | pass: 45 passed, 363 deselected, 5 subtests passed |
| historical pytest route | `python -B -m pytest -q --round3-contract=historical Iris\build\description\v2\tests` | pass: 284 passed, 123 deselected |
| diagnostic pytest route | `python -B -m pytest -q --round3-contract=diagnostic Iris\build\description\v2\tests` | pass: 79 passed, 328 deselected |
| legacy full unittest | `python -B -m unittest discover -s Iris\build\description\v2\tests -p "test_*.py"` | pass: 407 tests |
| current contract runner | `python -B Iris\_docs\round3\round3_run_contract_tests.py --class current --enforce-current-build-closure` | pass: 44 tests |
| boundary guard | `python -B Iris\_docs\round3\round3_boundary_guard.py --self-test` | pass |
| Lua syntax | `powershell -ExecutionPolicy Bypass -File .\tools\check_lua_syntax.ps1` | pass: 188 files |
| package | `.\Iris\tools\package_iris.ps1 -Clean -Zip` | pass |
| package manifest JSON | `jq -e type Iris\build\package\Iris.package_manifest.sha256.json` | pass |
| package forbidden path check | PowerShell manifest path filter | pass |

Package output:

- `Iris/build/package/Iris`
- `Iris/build/package/Iris.package_manifest.sha256.json`
- `Iris/build/package/Iris.zip`

Package manifest summary:

- file_count: 100
- zip bytes: 250619

## Status

Automated release/package readiness gates are green for this round.

This report does not replace in-game manual QA or Workshop publication checks.
