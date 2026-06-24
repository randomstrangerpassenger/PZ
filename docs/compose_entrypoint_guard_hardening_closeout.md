# Compose Entrypoint Guard Hardening Closeout

> Status: complete as guard-hardening execution and self-validation only
> Date: 2026-06-13
> Scope authority: `docs/compose_entrypoint_guard_hardening_plan.md`

## Summary

The DVF 3-3 compose current rendered write guard now runs at the shared
`build_rendered()` boundary. Direct programmatic calls and CLI calls must pass
the same write contract before facts, decisions, or any rendered/style/requeue
outputs are written.

This closeout does not claim vNext cutover, runtime Lua replacement, release
readiness, Workshop readiness, manual in-game QA, or canonical governance
promotion.

## Implemented

- Added explicit `compose_context` values: `current`, `staging`, `historical`,
  and `diagnostic`.
- Added `ComposeEntrypointGuardError` fail-loud errors for missing/invalid
  context, rejected output path class, rejected profile class, and unlisted
  current-equivalent output-root targets.
- Moved current write authorization into `build_rendered()` before data load and
  before output writes.
- Added positive `v2_current` profile classification; legacy, partial,
  ambiguous, and unknown profiles are rejected for current output writes.
- Closed the current protected output set for this round:
  `dvf_3_3_rendered.json`, `style_normalization_changes.jsonl`, and
  `compose_requeue_candidates.jsonl`.
- Migrated direct tool/test callers to explicit `compose_context` and explicit
  non-current `style_log_path` where the previous default would have targeted
  canonical output.
- Preserved explicit historical and diagnostic non-current lanes.
- Added focused guard hardening tests and Round3 taxonomy coverage for the new
  guard tests.

## Evidence

- `Iris/build/description/v2/staging/compose_entrypoint_guard_hardening/compose_entrypoint_guard_call_surface_inventory.md`
- `Iris/build/description/v2/staging/compose_entrypoint_guard_hardening/compose_write_path_matrix.md`
- `Iris/build/description/v2/staging/compose_entrypoint_guard_hardening/compose_protected_output_paths.json`
- `Iris/build/description/v2/staging/compose_entrypoint_guard_hardening/compose_pre_change_hash_snapshot.json`
- `Iris/build/description/v2/staging/compose_entrypoint_guard_hardening/compose_guard_tool_selftest_report.json`
- `Iris/build/description/v2/staging/compose_entrypoint_guard_hardening/compose_entrypoint_guard_regression_report.json`
- `Iris/build/description/v2/staging/compose_entrypoint_guard_hardening/compose_entrypoint_guard_no_mutation_verdict.json`

`compose_pre_change_hash_snapshot.json` is a pre rejected-call validation
snapshot captured after implementation. It is not a pre-code-change snapshot.

## Validation

All commands below exited with code 0.

- `python -B -m compileall -q Iris/build/description/v2/tools/build`
- `python -B -m unittest discover -s Iris/build/description/v2/tests -p "test_compose_entrypoint_guard_hardening.py"`: 7 tests OK
- `python -B -m unittest discover -s Iris/build/description/v2/tests -p "test_compose_layer3_text_v2.py"`: 15 tests OK
- `python -B -m unittest discover -s Iris/build/description/v2/tests -p "test_current_authority_source_path_guard.py"`: 4 tests OK
- `python -B -m unittest discover -s Iris/build/description/v2/tests -p "test_compose_layer3_text_overlay.py"`: 7 tests OK
- `python -B -m unittest discover -s Iris/build/description/v2/tests -p "test_interaction_cluster_pipeline.py"`: 10 tests OK
- `python -B Iris/_docs/round3/round3_run_contract_tests.py --class current --enforce-current-build-closure`: 50 tests OK
- `python -B Iris/_docs/round3/round3_run_contract_tests.py --class historical`: 285 tests OK
- `python -B Iris/_docs/round3/round3_run_contract_tests.py --class diagnostic`: 81 tests OK
- `python -B -m pytest -q`: 51 passed, 366 deselected, 5 subtests passed

The Round3 counts changed from the plan baseline because the new compose
entrypoint guard tests were classified into the taxonomy and an existing
current-authority reconstruction helper test was classified as diagnostic.

## No-Mutation Verdict

Rejected guard tests left the closed protected current set unchanged:

- `Iris/build/description/v2/output/dvf_3_3_rendered.json`: unchanged
- `Iris/build/description/v2/output/style_normalization_changes.jsonl`: unchanged
- `Iris/build/description/v2/output/compose_requeue_candidates.jsonl`: absent before and after

The full hash comparison is recorded in
`compose_entrypoint_guard_no_mutation_verdict.json`.

## Limits

- No separate guard or validator tool was introduced, so guard tool self-test is
  recorded as not applicable.
- No runtime Lua, Lua bridge, chunk manifest, chunk payload, Browser, Tooltip,
  or Wiki behavior was intentionally changed.
- Canonical `docs/DECISIONS.md` and `docs/ROADMAP.md` were not promoted by this
  closeout.
