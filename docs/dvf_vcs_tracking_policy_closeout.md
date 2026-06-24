# DVF VCS Tracking Policy Closeout

> Status: complete within stated validation ceiling / no release claim
> Date: 2026-06-15
> Plan: `docs/dvf_vcs_tracking_policy_plan.md`

## Scope Result

The DVF VCS tracking policy was implemented as a representation/governance layer only. It does not change DVF source facts, decisions, rendered output, runtime chunks, Browser/Wiki/Tooltip behavior, or package release status.

Implemented surfaces:

- `.gitignore` narrow exceptions for current bridge exporter and VCS policy guard files.
- `docs/dvf_vcs_tracking_policy.md` subordinate policy surface.
- `Iris/build/description/v2/tools/build/dvf_vcs_tracking_policy.py` evidence generator.
- `Iris/build/description/v2/tests/test_dvf_vcs_tracking_policy.py` focused fail-loud guard.
- Additive evidence under `Iris/build/description/v2/staging/dvf_vcs_tracking_policy/`.

## Realignment

- `export_dvf_3_3_lua_bridge.py` is classified as `regeneration-tooling / tracked_required`.
- `dvf_3_3_input_manifest.json` is classified as `current_regeneration_manifest / tracked_required`.
- `media/lua/shared/Iris/IrisDvfBridgeData.lua` is classified as `forbidden_current_looking_stale`.
- Stale bridge quarantine evidence remains non-current evidence only.

## Validation Ceiling

Validated:

- `python -B -m unittest discover -s Iris\build\description\v2\tests -p "test_dvf_vcs_tracking_policy.py"` exited 0; 5 tests OK.
- `powershell -ExecutionPolicy Bypass -File .\Iris\tools\package_iris.ps1 -Clean -Zip` exited 0.
- `python -B Iris\build\description\v2\tools\build\dvf_vcs_tracking_policy.py --write-evidence` exited 0.
- `python -B -m py_compile Iris\build\description\v2\tools\build\dvf_vcs_tracking_policy.py Iris\build\description\v2\tests\test_dvf_vcs_tracking_policy.py` exited 0.
- `test_dvf_vcs_tracking_policy.py` now guards that Round 3 current core remains 12 modules and that `export_dvf_3_3_lua_bridge` is the only current-route tooling exception.
- `expected_predicate_validation_report.json` reports `pass: true`.
- `protected_surface_no_mutation_verdict.json` reports `changed_count: 0`, `pass: true`.
- `stale_current_looking_presence_report.json` reports `violation_count: 0`, `pass: true`.
- `package_zip_forbidden_scan_report.json` reports `forbidden_hit_count: 0`, `pass: true`.
- `vcs_policy_validation_report.json` reports `pass: true`.

- `python -B Iris\_docs\round3\round3_run_contract_tests.py --class current --enforce-current-build-closure` exited 0; 57 tests OK.
- Round 3 current core remains 12 modules. `export_dvf_3_3_lua_bridge` is allowed only as current-route regeneration tooling, not as a current core module.

Out of scope:

- Manual in-game QA.
- Runtime equivalence validation.
- Multiplayer, Workshop, B42, external ecosystem compatibility.
- Full historical artifact byte reproducibility.
- Successor baseline correctness or vNext cutover.
- Stale Bridge Disposition sealed PASS.

Unvalidated but in scope:

- None for this VCS tracking policy closeout. Independent review handoff exists, but this closeout does not claim Stale Bridge Disposition sealed PASS.

## Non-Claims

This closeout does not claim release readiness, deployment, Workshop readiness, package release readiness, runtime rollout, public-facing behavior change, successor baseline identity, or manual in-game validation.

## Evidence

Primary evidence root:

```text
Iris/build/description/v2/staging/dvf_vcs_tracking_policy/
```

Expected key reports:

- `vcs_tracking_inventory.jsonl`
- `tracking_policy_matrix.json`
- `expected_predicate_validation_report.json`
- `protected_surface_no_mutation_verdict.json`
- `stale_current_looking_presence_report.json`
- `package_zip_forbidden_scan_report.json`
- `vcs_policy_validation_report.json`
- `review_handoff.md`
