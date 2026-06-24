# Lua Bridge Export Contract Realign Closeout

> 상태: complete / execution-and-self-validation only
> 기준 계획: `docs/lua_bridge_export_contract_realign_plan.md`
> evidence root: `Iris/build/description/v2/staging/lua_bridge_export_contract_realign/`

## Result

DVF 3-3 Lua bridge exporter의 default build-time route를 chunk manifest + chunk files 중심으로 재정렬했다.

Default invocation은 이제 `bridge_context=staging`, `format=chunk`로 동작하며, output은 `Iris/build/description/v2/staging/lua_bridge_export/default/` 아래에 생성된다. `IrisLayer3Data.lua` monolith 생성은 default/current route에서 제거했고, explicit `historical` 또는 `diagnostic` context의 `format=monolith`에서만 허용한다.

Live deployable chunk manifest/dir 및 live monolith destination은 exporter shared guard에서 fail-loud 처리된다. Package script는 source/package monolith를 조용히 제거하지 않고 fail-loud 처리한다.

## Changed Surfaces

- `Iris/build/description/v2/tools/build/export_dvf_3_3_lua_bridge.py`
- `Iris/tools/package_iris.ps1`
- focused and legacy-aligned tests under `Iris/build/description/v2/tests/`
- Round 3 test taxonomy: `Iris/_docs/round3/round3_test_taxonomy.json`
- additive evidence under `Iris/build/description/v2/staging/lua_bridge_export_contract_realign/`

Canonical `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, and `docs/ROADMAP.md` were not mutated.

## Evidence

- `default_invocation_contract.json`
- `bridge_export_report.json`
- `chunk_integrity_report.json`
- `chunk_determinism_report.json`
- `package_monolith_guard_report.json`
- `workspace_copy_surface_disposition.json`
- `protected_surface_hash_diff.json`
- `no_mutation_verdict.json`
- `final_contract_report.json`

Protected surface verdict: `PASS`, `changed_count=0`.

## Validation

- `python -B -m unittest discover -s Iris\build\description\v2\tests -p "test_lua_bridge_export_contract_realign.py"`: 7 tests OK
- `python -B -m unittest discover -s Iris\build\description\v2\tests -p "test_*.py"`: 423 tests OK
- `python -B -m pytest -q`: 58 passed, 366 deselected, 5 subtests passed
- `powershell -ExecutionPolicy Bypass -File .\Iris\tools\package_iris.ps1 -Clean -Zip`: OK
- default exporter invocation: OK
- explicit staging chunk exporter invocation: OK
- protected live chunk path probe: rejected as expected

## Limits

No in-game QA was performed. No live chunk payload swap, baseline switch, UI behavior change, package publication, or public deployment claim is made.

Historical monolith reflection scripts remain inventoried as historical/diagnostic surfaces. This closeout claims package/copy-like guard coverage for the current build-time path only.
