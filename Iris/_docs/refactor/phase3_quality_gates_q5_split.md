# Iris Refactor Phase 3 Quality Gates Q5 Split

Date: 2026-05-06

Historical source roadmap label: `docs/Iris/iris-refactoring-final-roadmap-v1.md`

This record starts Phase 3-3. The goal is to split Q5 into collect, compare,
and report helpers while preserving the existing command surface and fail
conditions.

## First split

Updated:

- `Iris/build/quality_gates.py`

Extracted helpers:

- `q5_validate_allowed_changes(expected_diff, allowed)`
- `q5_collect_decision_status_changes(decisions, expected_diff)`
- `q5_collect_usecase_aggregate_changes(usecases_data, expected_diff)`
- `q5_collect_description_aggregate_changes(expected_diff)`
- `q5_collect_requirements_aggregate_changes(expected_diff)`
- `q5_collect_legacy_count_changes(expected_diff)`
- `q5_collect_require_channel_changes(req_fulltypes, expected_diff)`
- `q5_compare_metric_changes(new_metrics, expected_diff)`
- `q5_collect_usecase_line_metrics(uc_fulltypes)`
- `q5_collect_evidence_strength_metrics(uc_fulltypes)`
- `q5_collect_recipe_role_metrics(uc_fulltypes, expected_diff)`
- `q5_validate_keep_unresolved_count()`
- `q5_collect_registry_override_metrics()`
- `q5_collect_diagnostic_metrics()`
- `q5_collect_recipe_nav_metrics(expected_diff)`
- `q5_collect_recipe_requirement_index_metrics(expected_diff)`
- `q5_report_allowed_changes(all_changes, allowed)`

Current boundary:

- `collect`: PASS/REVIEW set changes and NO aggregate changes are now collected
  by `q5_collect_decision_status_changes`.
- `collect`: usecase, description, requirements, legacy, and require-channel
  aggregate changes are now collected by dedicated helpers.
- `compare`: metric value policy comparison is now handled by
  `q5_compare_metric_changes`.
- `collect/compare`: usecase-derived metrics and their FAIL-LOUD source checks
  are now split into dedicated helper functions.
- `report`: final `allowed_changes` comparison and pending allowed warnings are
  now handled by `q5_report_allowed_changes`.
- remaining: `gate_q5` still orchestrates the helpers directly. A future cleanup
  can move these helpers into a Q5-specific module once the local boundary stays
  stable across another change batch.

## Verification

- `python -B -m compileall -q Iris\build\quality_gates.py`
- `python -B Iris\build\quality_gates.py`
- `python -B -m Iris.build.quality_gates`
- `python -B -m unittest Iris.build.description.v2.tests.test_build_iris_index_data`
- `python -B -m unittest Iris.build.tests.test_evidence_pipeline_cross_track`

All commands passed. Q1~Q5 command surface and report keys are unchanged.
