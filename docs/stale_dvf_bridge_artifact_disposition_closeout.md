# Stale DVF Bridge Artifact Disposition Closeout

> 상태: implemented / review_pending / not sealed PASS
> 기준일: 2026-06-15
> Plan: `docs/stale_dvf_bridge_artifact_disposition_plan.md`
> Evidence root: `Iris/build/description/v2/staging/stale_dvf_bridge_artifact_disposition/`

## Result

`media/lua/shared/Iris/IrisDvfBridgeData.lua` was classified as `stale` for this round and removed from the current-looking root `media/` path.

The exact 6-entry legacy payload was retained as staging quarantine evidence at:

* `Iris/build/description/v2/staging/stale_dvf_bridge_artifact_disposition/quarantine/IrisDvfBridgeData.legacy_6_entry.lua`

The current DVF bridge authority remains unchanged:

* `Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks.lua`
* `Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks/*.lua`

## Implementation

Changed surfaces:

* Removed old current-looking root artifact: `media/lua/shared/Iris/IrisDvfBridgeData.lua`
* Added staging-only quarantine evidence for the legacy 6-entry payload.
* Hardened `Iris/tools/package_iris.ps1` to fail loud on:
  * old root path
  * `Iris/media/...` alternate path
  * package-output equivalent path
  * `IrisDvfBridgeData.lua` filename in package/current surfaces
  * exact legacy payload SHA256
  * legacy 6-entry payload shape
* Extended `Iris/build/description/v2/tests/test_package_layer3_chunks_only_contract.py` for stale bridge guard coverage.
* Added `Iris/build/description/v2/tools/build/stale_dvf_bridge_artifact_disposition.py` to generate inventory, classification, package scan, guard, and no-mutation evidence.

## Evidence

Key generated reports:

* `classification_verdict.json`: `verdict = stale`, `disposition = quarantined_outside_current_looking_path`
* `package_output_equivalence_report.json`: forbidden stale bridge absent from package root and ZIP
* `no_mutation_verdict.json`: `PASS`, `changed_count = 0`
* `guard_positive_negative_behavior_report.json`: old-path positive case failed as expected; default package route passed
* `final_disposition_contract_report.json`: `state = review_pending`
* `independent_review_gate.md`: independent review not performed; seal remains pending

## Validation

Passed:

* `python -B Iris\build\description\v2\tools\build\stale_dvf_bridge_artifact_disposition.py --stage before`
* `python -B Iris\build\description\v2\tools\build\stale_dvf_bridge_artifact_disposition.py --stage after`
* `python -B -m unittest discover -s Iris\build\description\v2\tests -p "test_package_layer3_chunks_only_contract.py"`
* `powershell -ExecutionPolicy Bypass -File .\Iris\tools\package_iris.ps1 -Clean -Zip`
* guard positive/negative behavior command recorded in `guard_positive_negative_behavior_report.json`
* `uv run python -B -m unittest discover -s Iris\build\description\v2\tests -p "test_lua_bridge_export_contract_realign.py"` with workspace-local uv cache: 7 tests OK
* `uv run python -B -m unittest discover -s Iris\build\description\v2\tests -p "test_package_layer3_chunks_only_contract.py"` with workspace-local uv cache: 4 tests OK
* `uv run python -B -m pytest -q` with workspace-local uv cache: 58 passed, 368 deselected, 5 subtests passed
* `powershell -ExecutionPolicy Bypass -File .\tools\check_lua_syntax.ps1`: 188 files OK

Failed / not claimed:

* `uv run python -B Iris\_docs\round3\round3_run_contract_tests.py --class current --enforce-current-build-closure` exited 1. It ran 57 tests and failed with 7 import errors because Round 3 current closure blocks `tools.build.export_dvf_3_3_lua_bridge` imports from `test_lua_bridge_export_contract_realign.py`.
* Therefore this closeout does not claim current route regression pass.

## Validation Ceiling

Validated:

* target inventory and payload profile
* direct named-token consumer audit
* package output and ZIP absence for old path, old filename, exact hash, and payload shape
* package guard positive and negative behavior
* current chunk/facts/decisions/rendered no-mutation hash diff
* focused package and bridge tests
* default pytest route
* Lua syntax

Out of scope:

* PZ long-session in-game QA
* multiplayer validation
* external mod compatibility sweep
* DVF vNext successor baseline validation
* release, deployment, Workshop, or B42 readiness

Unvalidated / unresolved in scope:

* independent post-implementation review gate
* current contract route regression, due the import-block failure above

## Non-Claims

This closeout does not declare:

* sealed PASS
* release readiness
* deployment readiness
* Workshop readiness
* DVF vNext cutover
* runtime rollout
* Browser / Wiki / Tooltip behavior change
* full runtime behavior equivalence
