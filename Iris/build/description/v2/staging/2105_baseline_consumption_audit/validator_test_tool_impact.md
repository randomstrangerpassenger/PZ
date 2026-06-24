# Validator / Test / Tool Impact

- Executing consumer rows: 1062
- Current route rows: 126
- Historical route rows: 52
- Diagnostic route rows: 673
- Audit-only helper route: staging-only, not default current route.

Default current route remains `uv run python Iris/_docs/round3/round3_run_contract_tests.py --class current --enforce-current-build-closure`.
