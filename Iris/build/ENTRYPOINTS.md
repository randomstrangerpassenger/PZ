# Iris Build Active Manifest

Status: Phase 1 active manifest for
`docs/Iris/iris-refactoring-final-roadmap-v1.md`.

Date: 2026-05-04

This file is the active build contract for the root `Iris/build` tree. It is
also the Phase 1 keep-list used to prevent filename-glob cleanup from moving
live build scripts.

## Supported root commands

- `main.py`: legacy full classification pipeline entrypoint.
- `recipe_evidence_pipeline.py`: recipe evidence pipeline.
- `rightclick_evidence_pipeline.py`: right-click evidence pipeline.
- `quality_gates.py`: frozen-output and quality gate checks.
- `description_generator.py`: description JSON generator.
- `convert_descriptions_to_lua.py`: generated description Lua converter.
- `convert_labelmap_to_lua.py`: label-map Lua converter.
- `test_require_render.py`: runtime require-order/render smoke test.

## Active phase package directories

These directories remain active. They are not empty relocation leftovers.

- `phase0_validation/`: imported by `main.py`.
- `phase1_extraction/`: imported by `main.py`, root tests, and pipeline tools.
- `phase2_rules/`: imported by `main.py`, root tests, and pipeline tools.
- `phase3_output/`: imported by `main.py` and context-outcome pipeline tools.
- `phase4_tests/`: imported by `main.py`.

## Relocated pipeline tools

Pipeline helpers and legacy build utilities were moved to:

- `tools/pipeline/`

Pipeline keep-list:

- `apply_registry_merge.py`
- `build_action_requirement_index.py`
- `build_legacy_candidates.py`
- `build_legacy_inventory.py`
- `build_recipe_classification_matches.py`
- `build_recipe_nav_registry.py`
- `build_recipe_requirements_index.py`
- `build_usecases_by_fulltype.py`
- `classify_action_evidence.py`
- `context_outcomes_main.py`
- `parse_recipe_require_fields.py`
- `registry_utils.py`

Root-level tests were moved to:

- `tests/`

Active root test files:

- `regression_test_outcomes.py`
- `test_description_generator.py`
- `test_determinism_rc.py`
- `test_fail_loud_coverage.py`
- `test_layer3_pipeline.py`
- `test_recipe_evidence.py`
- `test_wearable_6f.py`

## Relocated one-shot tools

Historical analyzers and mutation helpers were moved to:

- `tools/oneshots/`

These are not part of the active build contract.

Current one-shot archive boundary:

- 15 root historical one-shot scripts are already under `tools/oneshots/`.
- `Iris/build/description/v2/tools/build/*.py` is not covered by the one-shot
  archive rule. That directory has its own inventory and is classified as
  reproduce-required unless a later per-file disposition says otherwise.

## Relocated policy data

Root JSON/SHA policy artifacts were moved to:

- `data/v2.4/`

## Description v2 build tools

`Iris/build/description/v2/tools/build/` is governed by its local inventory:

- `Iris/build/description/v2/tools/build/INVENTORY.md`

The 2026-05-04 Phase 1 remeasurement found the roadmap universe of
`build_*.py` plus `report_*.py` to be 233 scripts, but this count is a candidate
universe only. Files in that directory must not be archived by filename glob.

## Import and execution contract

Phase 3 shared build helpers are governed by:

- `Iris/build/build_import_contract.md`
- `Iris/_docs/refactor/phase3_json_io_common_migration.md`

Direct script execution from the repository root remains the compatibility
baseline. Common helpers under `Iris/build/tools/common/` must be introduced one
active script or tightly related script family at a time.

## Phase 1 root artifact disposition

Root Iris legacy extraction summaries are tracked in:

- `Iris/_docs/refactor/phase1_active_manifest.md`
- `Iris/_docs/refactor/phase1_root_artifact_disposition.md`
- `Iris/_docs/refactor/phase1_closeout_scope.md`

No root artifact move is complete until code paths plus schema/meta/docs
references are updated or an explicit legacy-location decision is recorded.

Completed root artifact moves:

- `rightclick_source_index.v2.4.json` now lives at
  `Iris/input/rightclick_source_index.v2.4.json`.
- `iris-*-evidence-table.md` and `iris-tool-security-evidence-addendum.md` now
  live under `Iris/evidence/tables/`.
- Legacy root snapshots for `context_outcomes.json`, `diagnostics.json`,
  `extraction_stats.json`, and `scope_outside_fulltypes.json` now live under
  `Iris/output/legacy_root/`.
- Legacy `source_scan_targets.json` now lives under
  `Iris/input/legacy_root/`.
- `subcategory_analysis.md` now lives under `Iris/evidence/analysis/`.
- Historical `_archive/p0-2/` payloads are excluded from packaging by
  `Iris/tools/package_iris.ps1` and from git noise by `.gitignore`.
