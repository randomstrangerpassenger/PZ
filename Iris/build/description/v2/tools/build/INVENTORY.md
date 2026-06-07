# Iris Build Tool Inventory

P0.5 inventory for `iris_refactor_roadmap_v2.0.md`.

P7-3 note: `compose_layer3_text.py` has been split into the core entrypoint plus
`compose_layer3_blocks.py`, `compose_layer3_io.py`, and
`compose_layer3_identity.py`, `compose_layer3_body_profile.py`,
`compose_layer3_item.py`, and `compose_layer3_render.py`. The P0.5 scan counts
below are retained as historical inventory values.

Phase 1 v1.4 note (2026-05-04): the current tree was remeasured for
`docs/Iris/iris-refactoring-final-roadmap-v1.md`. The global roadmap candidate
universe is `build_*.py` 178 plus `report_*.py` 55, total 233. This remains a
candidate universe only and is not an archive rule.

Current local count for this directory:

| Metric | Result |
|---|---:|
| Python scripts in this directory | 269 |
| `build_*.py` in this directory | 171 |
| `report_*.py` in this directory | 55 |
| Other Python scripts in this directory | 43 |

Current v1.4 disposition: no file under
`Iris/build/description/v2/tools/build/*.py` is archive/delete eligible by
filename glob. Per-file disposition must come from a follow-up inventory that
proves the file is not imported, documented, path-executed, or artifact
reproduction-relevant.

Scope: `Iris/build/description/v2/tools/build/*.py`

## Scan Summary

| Metric | Result |
|---|---:|
| Python scripts in scope | 264 |
| Currently tracked by Git | 1 |
| Currently ignored/local | 263 |
| Imported by at least one peer build script | 96 |
| Referenced outside the script body by docs/tests/tools | 228 |
| Contain explicit artifact path constants | 260 |
| No import/doc/artifact signal | 0 |

Current tracked core compose scripts:

| Path | Treatment |
|---|---|
| `Iris/build/description/v2/tools/build/compose_layer3_text.py` | keep tracked |
| `Iris/build/description/v2/tools/build/compose_layer3_blocks.py` | keep tracked |
| `Iris/build/description/v2/tools/build/compose_layer3_io.py` | keep tracked |
| `Iris/build/description/v2/tools/build/compose_layer3_identity.py` | keep tracked |
| `Iris/build/description/v2/tools/build/compose_layer3_body_profile.py` | keep tracked |
| `Iris/build/description/v2/tools/build/compose_layer3_item.py` | keep tracked |
| `Iris/build/description/v2/tools/build/compose_layer3_render.py` | keep tracked |

## Classification Decision

All 264 scripts are classified as `reproduce-required` for P0.5.

The ignored/local scripts are not disposable scratch files. The set has a dense
peer-import graph, current docs/tests references, and explicit artifact path
constants under `staging/`, `output/`, and runtime Lua export paths. P0.5
therefore assigns no `tools/build/*.py` file to `archive` or `delete`.

Ignored-file treatment conclusion:

| Set | Count | Treatment | Rationale |
|---|---:|---|---|
| `compose_layer3_text.py` split modules | 7 | keep tracked | Current core composer, block renderer/repair helpers, IO helpers, identity/context text helpers, body profile helpers, item composition helpers, and render orchestration helpers. |
| ignored `tools/build/*.py` with import/doc reference | 227 | track | Directly participates in reproducible build graph or documented runbooks. |
| ignored `tools/build/*.py` with artifact-path signal only | 36 | track | Generates named artifacts; not safe to archive without a replacement provenance record. |
| no-signal ignored `tools/build/*.py` | 0 | n/a | No candidates found. |

Actual tracking of the 263 ignored scripts should be a dedicated follow-up
change, because it is a large Git surface change and should not be mixed with
P0 manifest or baseline work. Until then, P0.7 must not delete or archive any
file under `Iris/build/description/v2/tools/build/*.py`.

## Family Inventory

| Family | Count | Treatment |
|---|---:|---|
| acquisition | 18 | track |
| apply_misc | 1 | track |
| body_plan_structural | 21 | track |
| body_role | 12 | track |
| build_misc | 3 | track |
| identity_fallback | 40 | track |
| interaction_cluster | 29 | track |
| post_cleanup | 27 | track |
| quality_publish | 12 | track |
| reports_misc | 19 | track |
| role_fallback_hollow | 35 | track |
| second_pass | 15 | track |
| source_coverage | 23 | track |
| source_expansion_distribution_remeasurement_gate | 4 | track |
| utility_io | 1 | track |
| utility_misc | 2 | track |
| validators | 2 | track |

## Import Hubs

These scripts are dependency hubs and must remain reproducible:

| Script | Imported by |
|---|---:|
| `compose_layer3_text.py` | 64 |
| `validate_interaction_cluster_rendered.py` | 58 |
| `report_weak_active_cleanup_w2_existing_cluster_absorption.py` | 44 |
| `export_dvf_3_3_lua_bridge.py` | 31 |
| `validate_interaction_cluster_phase_d_runtime.py` | 30 |
| `build_interaction_cluster_compose_input.py` | 22 |
| `build_identity_fallback_batch1_clothing_surface_reuse.py` | 20 |
| `acquisition_lexical_utils.py` | 19 |
| `build_interaction_cluster_candidates.py` | 19 |
| `normalize_interaction_cluster_overlay.py` | 18 |
| `report_interaction_cluster_coverage.py` | 17 |
| `validate_interaction_cluster_coverage.py` | 16 |

## Artifact-Path-Only Scripts

These 36 scripts were not found as peer imports or doc/test references, but they
contain explicit artifact paths and are therefore classified as
`reproduce-required` with `track` treatment:

| Script | Treatment |
|---|---|
| `apply_manual_ingame_qa_polish_patch.py` | track |
| `apply_role_fallback_hollow_source_promotion.py` | track |
| `build_identity_fallback_batch1_authority_promotion.py` | track |
| `build_identity_fallback_batch2_authority_promotion.py` | track |
| `build_identity_fallback_batch3_authority_promotion.py` | track |
| `build_identity_fallback_batch4_authority_promotion.py` | track |
| `build_identity_fallback_batch5_residual_taxonomy.py` | track |
| `build_layer3_body_plan_v2_closeout_artifacts.py` | track |
| `build_layer3_body_plan_v2_pilot_corpus.py` | track |
| `build_role_fallback_hollow_c1b_reuse_promotion_preview.py` | track |
| `build_role_fallback_hollow_followup_execution_inputs.py` | track |
| `build_role_fallback_hollow_followup_packages.py` | track |
| `build_role_fallback_hollow_manual_residual_blocker_memo.py` | track |
| `build_role_fallback_hollow_manual_search_pack.py` | track |
| `build_role_fallback_hollow_manual_second_pass_upgrades.py` | track |
| `build_role_fallback_hollow_net_new_work_packages.py` | track |
| `build_role_fallback_hollow_residual_after_c1b_reuse.py` | track |
| `build_role_fallback_hollow_seed_package_local_evidence.py` | track |
| `build_role_fallback_hollow_source_authoring_queue.py` | track |
| `build_role_fallback_hollow_source_expansion_seed_packages.py` | track |
| `build_role_fallback_hollow_source_promotion_manifest.py` | track |
| `build_role_fallback_hollow_source_replacement_candidates.py` | track |
| `build_role_fallback_hollow_source_replacement_delta_review.py` | track |
| `build_role_fallback_hollow_targeted_authoring_drafts.py` | track |
| `build_role_fallback_hollow_targeted_authoring_pack.py` | track |
| `build_role_fallback_hollow_targeted_source_authority_candidates.py` | track |
| `build_role_fallback_hollow_targeted_source_merge_previews.py` | track |
| `build_role_fallback_hollow_targeted_source_promotion_drafts.py` | track |
| `freeze_quality_baseline_v2_partial.py` | track |
| `report_compose_profile_migration_inventory.py` | track |
| `report_compose_profile_precedence_draft.py` | track |
| `report_compose_profile_resolution_preview.py` | track |
| `report_layer3_body_plan_v2_blockers.py` | track |
| `report_phase_d_reopen_iteration.py` | track |
| `report_role_fallback_hollow_followup_split.py` | track |
| `report_role_fallback_hollow_source_expansion_backlog.py` | track |

## P1-1 Index Reuse Findings

### RecipeIndex

Existing reusable artifacts:

| Artifact | Status |
|---|---|
| `Iris/output/recipe_index.v2.4.json` | reusable as P1-1 source data |
| `Iris/output/recipe_requirements_index.v2.4.json` | reusable as P1-1 source data |
| `Iris/output/recipe_nav_registry.v2.4.json` | reusable for navigation-related baseline checks |

Current runtime state:

- `Iris/media/lua/client/Iris/Data/IrisRecipeIndex.lua` still calls
  `getAllRecipes()` at runtime and builds in-memory indexes.
- The existing JSON artifacts are older offline outputs, not yet wired into
  `IrisRecipeIndex.lua`.

P1-1 conclusion: Recipe data is reusable, but a bridge generator/adapter is
still needed to make runtime consume precompiled data instead of calling
`IrisRecipeIndex.build()`.

### MoveablesIndex

Existing reusable artifacts:

| Artifact | Status |
|---|---|
| `Iris/output/action_requirement_index.v2.4.json` | partial source-anchor evidence for moveable tools |
| `Iris/build/description/v2/staging/source_coverage/block_c/c1c_moveable_package/` | reviewed source-coverage package, not a complete runtime index |

Current runtime state:

- `Iris/media/lua/client/Iris/Data/IrisMoveablesIndex.lua` scans
  `ISMoveableDefinitions.ToolDefinition` at runtime.
- `_tagMapping` is currently not fully populated; the file has a TODO around
  item tag matching.

P1-1 conclusion: no complete precompiled MoveablesIndex artifact exists. P1-1
must either statically parse `lua/client/Moveables/ISMoveableDefinitions.lua`
plus moveable script/tag sources, or add an in-game dump generator and then
consume the dump as precompiled data.

### FixingIndex

Existing reusable artifacts:

| Artifact | Status |
|---|---|
| `scripts/fixing.txt` | static source for item fixing definitions |
| `scripts/vehicles/vehiclesfixing.txt` | static source for vehicle fixing definitions |

Current runtime state:

- `Iris/media/lua/client/Iris/Data/IrisFixingIndex.lua` calls
  `ScriptManager.instance:getAllFixing()` at runtime.
- No `Iris/output/*fixing*` precompiled runtime index was found.

P1-1 conclusion: no complete precompiled FixingIndex artifact exists. Static
parsing looks plausible because fixing definitions are present in script text
files, but an in-game dump generator remains the fallback if parser parity is
not exact.

## Offline Index Generator Decision

P1-1 should add new generators under `Iris/build/description/v2/tools/build/`
instead of extending runtime Lua scanning code.

Planned generator/output contract:

| Index | Generator path | Source input | Runtime output |
|---|---|---|---|
| Recipe | `build_iris_recipe_index_data.py` | `Iris/output/recipe_index.v2.4.json`, `Iris/output/recipe_requirements_index.v2.4.json` | `Iris/media/lua/client/Iris/Data/IrisRecipeIndexData.lua` |
| Moveables | `build_iris_moveables_index_data.py` | static parse or in-game dump of `ISMoveableDefinitions` data | `Iris/media/lua/client/Iris/Data/IrisMoveablesIndexData.lua` |
| Fixing | `build_iris_fixing_index_data.py` | `scripts/fixing.txt`, `scripts/vehicles/vehiclesfixing.txt` or in-game dump | `Iris/media/lua/client/Iris/Data/IrisFixingIndexData.lua` |

P1-1 implementation result:

| Index | Generator path | Runtime output | Generated count |
|---|---|---|---|
| Recipe | `build_iris_recipe_index_data.py` | `Iris/media/lua/client/Iris/Data/IrisRecipeIndexData.lua` | 349 item role buckets, 1 allowed `GetItemTypes` group |
| Moveables | `build_iris_moveables_index_data.py` | `Iris/media/lua/client/Iris/Data/IrisMoveablesIndexData.lua` | 23 registered items, 13 tag mappings |
| Fixing | `build_iris_fixing_index_data.py` | `Iris/media/lua/client/Iris/Data/IrisFixingIndexData.lua` | 20 fixer items |

The existing runtime modules (`IrisRecipeIndex.lua`, `IrisMoveablesIndex.lua`,
`IrisFixingIndex.lua`) now remain as API wrappers and consume the generated
`*Data.lua` modules. `IrisMain.initialize()` no longer calls `build()` on the
three indexes.

## Version Sync Policy

`v2.4` is treated as the current PZ data tag for the existing offline recipe
artifacts. Until an automated game-version detector exists, index regeneration
is a manual release task:

1. Run the relevant generator after PZ data updates.
2. Update the generated Lua data artifact.
3. Run P0.6/P1 baseline comparison.
4. Record the PZ data tag in this inventory or the follow-up generator report.

If this policy is not followed, Recipe/Moveables/Fixing data can become stale
even when Lua code remains unchanged.

## Phase 1 readpoint update (2026-06-07)

Amendment for `docs/Iris/Iris_Refactoring_Plan.md` (Draft v6.0) Change 1. The
counts above (2026-05-04, 269/264) are retained as historical inventory values;
the values below are the current remeasurement.

| Metric (2026-06-07) | Result |
|---|---:|
| Python scripts in this directory (`*.py`, excl `__pycache__`, recursive) | 281 |
| `build_*.py` in this directory | 177 |
| `report_*.py` in this directory | 57 |
| git-tracked in this directory | 12 |
| gitignored (reproduction) | 269 |

- conflict 14.1 resolved: roadmap A(282)/B(269) were the same directory measured
  at different times; the sealed canonical value is **281**
  (`docs/Iris/phase1_baseline_metrics.md` metric #1).
- Current tracked core (12): index generators
  `build_iris_{recipe,moveables,fixing}_index_data.py`, guard/recovery rounds
  `build_legacy_active_silent_current_surface_guard_round.py` +
  `build_static_report_label_cleanup_referent_recovery_round.py`, and the
  `compose_layer3_*.py` composer (7).
- Disposition unchanged: every `*.py` here stays `reproduce-required`; no file is
  archive/delete eligible by filename glob (conflict 14.3 resolved:
  per-file/per-directory disposition only).
- Phase 7a consolidation candidates (sibling families to verify with grep+diff
  before any merge): `identity_fallback batch{2..9}`,
  `source_coverage {b1..b4,c1a..c1e}`, `post_cleanup phase3_pkg3{a..j}`,
  `role_fallback_hollow`, `freeze_quality_baseline_v{1..4}`,
  `report_*_{draft,final}`.
- Readpoint: `docs/Iris/phase1_inventory_readpoint.md`; active manifest:
  `docs/Iris/phase1_active_script_manifest.txt`.
