# Command Surface Resolution

| Phase | Command | Expected |
| --- | --- | --- |
| `all` | `python -B Iris/build/description/v2/tools/build/run_dvf_3_3_vnext_rejected_delta_correction_reparity.py` | `0` |
| `current-route-validation` | `python -B Iris/_docs/round3/round3_run_contract_tests.py --class current --enforce-current-build-closure` | `0` |
| `unittest-discovery` | `python -B -m unittest discover -s Iris/build/description/v2/tests -p "test_*.py"` | `0` |
| `lua-syntax` | `powershell -ExecutionPolicy Bypass -File ./tools/check_lua_syntax.ps1` | `0` |
