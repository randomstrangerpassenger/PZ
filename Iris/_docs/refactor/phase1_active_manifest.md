# Iris Refactor Phase 1 Active Manifest

Date: 2026-05-04

Source roadmap: `docs/Iris/iris-refactoring-final-roadmap-v1.md`

This manifest starts Phase 1 by recording the live build surface before any
archive/delete action. The repository already contains earlier P0-P7 cleanup
work, so this document treats that work as input and records the current
v1.4-gated state.

## Worktree guard

The worktree has existing Iris runtime and build changes. This manifest does
not revert, normalize, or reinterpret those edits. Phase 1 cleanup must avoid
runtime Lua files and generated runtime data unless a later phase explicitly
opens that scope.

## Remeasurement summary

Command basis: `rg --files -u` with `__pycache__` and known inaccessible temp
test directories excluded from counts.

| Surface | Count | Phase 1 treatment |
|---|---:|---|
| Root `Iris/build/*.py` entrypoints | 8 | active |
| Root `Iris/build/tests/*.py` | 7 | active |
| `Iris/build/tools/pipeline/*.py` | 12 | active keep-list |
| `Iris/build/tools/oneshots/*.py` | 15 | archived one-shot reference set |
| Phase package directories, total `.py` | 30 | active, not empty leftovers |
| `Iris/build/description/v2/tests/test_*.py` | 169 | active test surface |
| `Iris/build/description/v2/tools/build/*.py` | 269 | governed by local inventory |
| Global `build_*.py` candidate universe | 178 | not an archive criterion |
| Global `report_*.py` candidate universe | 55 | not an archive criterion |

## Active root build commands

The active root command surface is `Iris/build/ENTRYPOINTS.md`.

Current root commands:

- `main.py`
- `recipe_evidence_pipeline.py`
- `rightclick_evidence_pipeline.py`
- `quality_gates.py`
- `description_generator.py`
- `convert_descriptions_to_lua.py`
- `convert_labelmap_to_lua.py`
- `test_require_render.py`

## Pipeline keep-list

These files are active even when their names match `build_*.py`.

- `Iris/build/tools/pipeline/apply_registry_merge.py`
- `Iris/build/tools/pipeline/build_action_requirement_index.py`
- `Iris/build/tools/pipeline/build_legacy_candidates.py`
- `Iris/build/tools/pipeline/build_legacy_inventory.py`
- `Iris/build/tools/pipeline/build_recipe_classification_matches.py`
- `Iris/build/tools/pipeline/build_recipe_nav_registry.py`
- `Iris/build/tools/pipeline/build_recipe_requirements_index.py`
- `Iris/build/tools/pipeline/build_usecases_by_fulltype.py`
- `Iris/build/tools/pipeline/classify_action_evidence.py`
- `Iris/build/tools/pipeline/context_outcomes_main.py`
- `Iris/build/tools/pipeline/parse_recipe_require_fields.py`
- `Iris/build/tools/pipeline/registry_utils.py`

Important direct-path reference:

- `Iris/build/tests/test_recipe_evidence.py` directly points at
  `Iris/build/tools/pipeline/build_usecases_by_fulltype.py`.

## Phase package disposition

The old phase directories are active imports, not empty relocated leftovers.

| Directory | Python files | Current references | Disposition |
|---|---:|---|---|
| `Iris/build/phase0_validation/` | 5 | `main.py` | active |
| `Iris/build/phase1_extraction/` | 8 | `main.py`, root tests, pipeline tools | active |
| `Iris/build/phase2_rules/` | 7 | `main.py`, root tests, pipeline tools | active |
| `Iris/build/phase3_output/` | 6 | `main.py`, context-outcome pipeline | active |
| `Iris/build/phase4_tests/` | 4 | `main.py` | active |

Deletion or relocation of these directories is blocked until `main.py`,
pipeline imports, and tests are migrated together.

## Description v2 tool disposition

`Iris/build/description/v2/tools/build/INVENTORY.md` remains the local authority
for description v2 build tools.

Current Phase 1 read:

- 269 Python scripts in the directory.
- 171 `build_*.py` scripts.
- 55 `report_*.py` scripts.
- 43 other Python scripts.
- No file in this directory is eligible for filename-glob archive.

## Root Iris artifact disposition

Detailed disposition record:

- `Iris/_docs/refactor/phase1_root_artifact_disposition.md`

The roadmap calls out root intermediate artifacts for migration, but current
references still pin several of them to root-level paths.

| Artifact group | Current signal | Phase 1 disposition |
|---|---|---|
| `iris-*-evidence-table.md` | `phase0_validation/evidence_table_loader.py` now loads from `Iris/evidence/tables/` with root fallback. | migrated to evidence table path contract in this batch |
| `rightclick_source_index.v2.4.json` | `rightclick_evidence_pipeline.py` and `tools/pipeline/build_action_requirement_index.py` now read `Iris/input/rightclick_source_index.v2.4.json`. | migrated to input path contract in this batch |
| `extraction_stats.json` | docs reference the historical `items_total = 2281` count. | moved to `Iris/output/legacy_root/extraction_stats.json`; docs updated |
| `context_outcomes.json`, `diagnostics.json` | output equivalents exist under `Iris/output/`; root copies are non-identical legacy artifacts. | moved to `Iris/output/legacy_root/` without overwriting active output |
| `scope_outside_fulltypes.json` | output equivalent exists under `Iris/output/` and is non-identical. | moved to `Iris/output/legacy_root/scope_outside_fulltypes.json` |
| `source_scan_targets.json` | legacy source scan target worksheet, not an active pipeline input. | moved to `Iris/input/legacy_root/source_scan_targets.json` |
| `subcategory_analysis.md` | one-shot worksheet generated by `tools/oneshots/analyze_subcategory_groups.py`. | moved to `Iris/evidence/analysis/subcategory_analysis.md`; one-shot output path updated |
| `iris-input-schema-v0.2-final.meta.json` | root schema/meta contract file. | keep root location until schema docs are migrated together |

This batch intentionally leaves only schema/meta and mod metadata at the Iris
root. Active output files under `Iris/output/` were not overwritten by legacy
root snapshots.

## Refactor docs disposition

Earlier P0-P7 execution documents are completed records. They were moved under:

- `Iris/_docs/refactor/_done/`

The active refactor directory now holds current Phase 1 v1.4 inventory
documents.

Post-cleanup remeasurement is recorded in:

- `Iris/_docs/refactor/phase1_closeout_scope.md`

## Historical archive disposition

`Iris/_archive/p0-2/` contains a historical nested runtime snapshot. Current
active scans found only:

- `Iris/_archive/p0-2/Iris/Iris/media/lua/client/Iris/Data/IrisLayer3Data.lua`

`Iris/tools/package_iris.ps1` already excludes `_archive` from packaging.
`.gitignore` now excludes `Iris/_archive/` so this historical payload does not
re-enter source control noise.

## Next executable batch

The right-click source index path contract is complete for v2.4. The evidence
table path contract is also complete with a legacy root fallback. The legacy
root artifact path contract is complete for the files listed above. The
historical archive exclusion is also complete.

Phase 1 cleanup and post-cleanup scope remeasurement are complete. The next
executable batch is the Phase 3 import and execution contract, before
introducing `Iris/build/tools/common`.

Each batch should update code, docs/meta references, and tests together.

## Verification notes

2026-05-04 checks after the right-click source index path migration:

- `python -B Iris/build/tools/pipeline/build_action_requirement_index.py`:
  PASS, input resolved from `Iris/input/rightclick_source_index.v2.4.json`.
- `python -B -m compileall -q Iris/build/rightclick_evidence_pipeline.py Iris/build/tools/pipeline/build_action_requirement_index.py`:
  PASS.
- `python -B -m unittest Iris.build.description.v2.tests.test_build_iris_index_data`:
  PASS, 3 tests.
- `python -B Iris/build/rightclick_evidence_pipeline.py --v24`:
  PASS after resealing the v2.4 frozen baseline for the existing
  `Base.Lemongrass` NO classification.
- `python -B Iris/build/quality_gates.py`:
  PASS.
- `python -B -m unittest discover -s Iris/build/tests -p "test_*.py"`:
  FAIL. The root test folder contains script-style tests that call `sys.exit`
  at import time, plus one missing `pipeline.description` import path. Use the
  documented direct script invocations until a unittest/pytest contract is
  opened.

2026-05-05 checks after root artifact path migration:

- Root intermediate files remaining under `Iris/`: none. Only
  `iris-input-schema-v0.2-final.meta.json` and `mod.info` remain as root
  contract/metadata files.
- `tools/oneshots/analyze_subcategory_groups.py` now writes its worksheet to
  `Iris/evidence/analysis/subcategory_analysis.md`.
- `python -B -m compileall -q` for the touched Python path-contract files:
  PASS.
- `rg --files Iris/_archive` finds only the historical p0-2
  `IrisLayer3Data.lua` snapshot; package script and `.gitignore` both exclude
  `_archive`.
