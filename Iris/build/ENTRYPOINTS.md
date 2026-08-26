# Iris Build Active Manifest

Status: Current lightweighting active manifest.

Historical source roadmap label:
`docs/Iris/iris-refactoring-final-roadmap-v1.md`.

Current readpoint for this active manifest is the inline content below plus
`docs/DECISIONS.md` and `docs/ROADMAP.md`, not the archived Iris docs path.

Date: 2026-05-04

This file is the active build contract for the root `Iris/build` tree. It is
also the Phase 1 keep-list used to prevent filename-glob cleanup from moving
live build scripts.

## Supported root commands

- Classification indexes are built into a repository-external candidate by the
  installed `iris_tooling classification build` command and enter runtime only
  through `iris_tooling classification install` with the exact candidate-manifest
  SHA-256. The broken legacy `main.py` orchestration is not a supported entrypoint.
- `recipe_evidence_pipeline.py`: recipe evidence pipeline.
- Installed current right-click command: `python -m iris_tooling --repository-root <repo> rightclick`.
  `rightclick_evidence_pipeline.py` is a retained non-current predecessor and is
  not a supported current entrypoint.
- `quality_gates.py`: frozen-output and quality gate checks.
- `description_generator.py`: description JSON generator.
- `test_require_render.py`: runtime require-order/render smoke test.

## Active phase package directories

Current phase helpers are owned by their supported focused producers. No phase
directory is current merely because the retired root `main.py` imported it.

## Relocated pipeline tools

Pipeline helpers and legacy build utilities were moved to:

- `tools/pipeline/`

Pipeline keep-list:

- `apply_registry_merge.py`
- `build_action_requirement_index.py`
- `build_legacy_candidates.py`
- `build_legacy_inventory.py`
- `build_recipe_nav_registry.py`
- `build_recipe_requirements_index.py`
- `build_usecases_by_fulltype.py`
- `classify_action_evidence.py`
- `parse_recipe_require_fields.py`
- `registry_utils.py`

Every active pipeline helper that reads or writes generated artifacts requires
the absolute repository-external `IRIS_CLEAN_CHECKOUT_LEGACY_OUTPUT_ROOT`.
`Iris/output` is not a supported default or fallback.

Retained non-current predecessors:

- `convert_descriptions_to_lua.py` retains pure Layer 4 render helpers used by
  external candidate generation, but its direct current-runtime write command
  is retired. Current runtime projection changes are Git-authored.
- `convert_labelmap_to_lua.py` retains pure label-map coverage/render helpers
  for focused tests, but its deleted `Iris/output` input and direct runtime-write
  command are retired. Current `IrisUseCaseLabelMap.lua` changes are Git-authored.
- `build_recipe_classification_matches.py` depends on retired phase packages;
  installed `iris_tooling classification` owns current classification indexes.
- `context_outcomes_main.py` is a fail-loud retirement stub. Its former phase
  packages are not recovered, and it cannot write current runtime Lua.
- `build_iris_translation_data.py` is not a current entrypoint because it writes
  a runtime target directly; current runtime changes are Git-authored.

Root-level tests were moved to:

- `tests/`

Active root test files:

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
- Legacy root snapshots formerly under `Iris/output/legacy_root/` are historical
  archive material and are not current producer inputs.
- Legacy `source_scan_targets.json` now lives under
  `Iris/input/legacy_root/`.
- `subcategory_analysis.md` now lives under `Iris/evidence/analysis/`.
- Historical `_archive/p0-2/` payloads are excluded from packaging by
  `Iris/tools/package_iris.ps1` and from git noise by `.gitignore`.

## Phase 1 readpoint update (2026-06-07)

Historical amendment labels:
`docs/Iris/Iris_Refactoring_Roadmap.md` and
`docs/Iris/Iris_Refactoring_Plan.md` (Draft v6.0) Change 1. This section is
additive; the contract above remains valid.

- Historical single readpoint label:
  `docs/Iris/phase1_inventory_readpoint.md`. Historical baseline metrics label:
  `docs/Iris/phase1_baseline_metrics.md`.
- Historical execution build/generation manifest label (38 scripts, repo-relative,
  single input for "active-only" measurements such as the v2.4 hardcode count):
  `docs/Iris/phase1_active_script_manifest.txt`.
- Remeasured tracked Python under `Iris/build` = 73, decomposed as:
  active build/generation 38 (root entrypoints 7 + `tools/pipeline` 13 +
  `tools/common` 3 + `description/v2/tools/build` core 12 +
  `description/v2/tools` 3), active-validation tests 16,
  `tools/oneshots` legacy 15, tracked staging round generators 4.
- `description/v2/tools/build/*.py` remeasured = 281 (excl `__pycache__`);
  12 tracked core, 269 gitignored reproduction scripts. Filename-glob
  archive/delete remains forbidden (conflict 14.3 resolved: per-file/per-directory
  disposition only).
- Direct script execution baseline is unchanged. conflict 14.2 (direct execution
  vs package entrypoint) is **deferred** to a user decision and gates Phase 3;
  until resolved, the direct-execution contract above is preserved verbatim.

## Change 3 update (2026-06-07): compose package form

conflict 14.2 is now **resolved = package form** (supersedes the 14.2-deferred
note just above). The `compose_layer3_*.py` core uses package imports
(relative internal + `tools.style` / `tools.common` absolute) with the
`try/except ImportError` dance removed; run via
`python -m tools.build.compose_layer3_text`. Leaf helper
`Iris/build/description/v2/tools/common/paths.py` added. Four caller scripts'
compose imports were updated to the package path. Frozen reproduction scripts
retain their direct-execution bootstrap and migrate incrementally.
Historical compose import note label:
`docs/Iris/phase3_compose_import_contract_note.md`.

## Current installed Description v2 tooling

Use the locked project or the immutable clean-checkout environment. Commands
must receive an explicit repository root; package code does not infer one from
its installation path or current working directory.

- Probe: `uv run --project .\Iris\tooling --locked --no-editable python -B -m iris_tooling --help`
- Classification candidate: `uv run --project .\Iris\tooling --locked --no-editable python -B -m iris_tooling --repository-root . classification build --output-root <external-empty-root>`
- Classification install: `uv run --project .\Iris\tooling --locked --no-editable python -B -m iris_tooling --repository-root . classification install --candidate-root <external-candidate-root> --manifest-sha256 <sha256>`
- Right-click v2.4: `uv run --project .\Iris\tooling --locked --no-editable python -B -m iris_tooling --repository-root . rightclick <arguments>`
- Layer 3 compose: `uv run --project .\Iris\tooling --locked --no-editable python -B -m iris_tooling --repository-root . layer3 --output-path <external-file> --style-log-path <external-file> <arguments>`
  Diagnostic resolver mode additionally requires an explicit external
  `--requeue-candidates-path`; no Layer 3 mode has a repository-local output fallback.
- Layer 4 export: `uv run --project .\Iris\tooling --locked --no-editable python -B -m iris_tooling --repository-root . layer4 <arguments>`
- Public-text/naturalization: `uv run --project .\Iris\tooling --locked --no-editable python -B -m iris_tooling --repository-root . public-text <arguments>`

The corresponding files under `Iris/build/description/v2/tools/build/` are
retained reproduction predecessors. They are not current imports or documented
entrypoints.

## DVF 3-3 stateless complete-generation successor

Run these from the repository root. Generation and reports must use explicit external roots.

- Build: installed `iris_tooling.build.build_dvf_3_3_complete_generation` with explicit repository/output arguments.
- Validate: installed `iris_tooling.build.validate_dvf_3_3_complete_generation` with explicit repository/generation arguments.
- Validate key/runtime projection: installed `iris_tooling.build.dvf_3_3_runtime_compatibility` against the external generation.
- Install after every R2-B gate is satisfied: installed `iris_tooling.build.install_dvf_3_3_complete_generation` with the exact expected predecessor generation id.
- Package current runtime: `powershell -ExecutionPolicy Bypass -File .\Iris\tools\package_iris.ps1 -OutputRoot <external-package-root> -Clean -Zip -PackageApplicability current_runtime_payload`

Only the installer may change the protected `IrisLayer3DataCurrent.lua` pointer. Source facts are edited through normal Git-authored diffs and rebuilt off-live. Historical correction/cutover/adoption entrypoints remain reproducibility evidence and are not current generation commands; RTC remains separate governance.
