# dvf_3_3_current_route_authority_required_evidence_integrity_closure Runner Order

command_sequence_id: `dvf_3_3_current_route_authority_required_evidence_integrity_closure_command_sequence_v1`

The command order is fixed. Any implementation change must update this document,
the scaffold ordered matrix, the final command matrix, and validator expectations together.

1. `uv run python -B Iris/build/description/v2/tools/build/run_dvf_3_3_current_route_authority_required_evidence_integrity_closure.py --mode scaffold`
2. `uv run python -B Iris/build/description/v2/tools/build/validate_dvf_3_3_current_route_authority_required_evidence_integrity_closure.py --require-scaffold`
3. `uv run python -B Iris/_docs/round3/round3_run_contract_tests.py --class current --enforce-current-build-closure --out Iris/build/description/v2/staging/dvf_3_3_current_route_authority_required_evidence_integrity_closure/phase7/full_current_route_validation_result.json`
4. `powershell -ExecutionPolicy Bypass -File .\tools\check_lua_syntax.ps1`
5. `uv run python -B Iris/build/description/v2/tools/build/run_dvf_3_3_current_route_authority_required_evidence_integrity_closure.py --mode all`
6. `uv run python -B Iris/build/description/v2/tools/build/validate_dvf_3_3_current_route_authority_required_evidence_integrity_closure.py --require-complete`
7. `uv run python -B -m unittest discover -s Iris/build/description/v2/tests -p "test_dvf_3_3_current_route_authority_required_evidence_integrity_closure.py"`
