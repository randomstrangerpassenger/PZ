# Iris Refactor Phase 3 JSON I/O Common Migration

Date: 2026-05-05

Historical source roadmap label: `docs/Iris/iris-refactoring-final-roadmap-v1.md`

This record starts Phase 3-1 after the import/execution contract was sealed in
`Iris/build/build_import_contract.md`.

## Common helper

The first neutral build helper is:

- `Iris/build/tools/common/io.py`

Current API:

- `load_json(path)`
- `write_json(path, data, indent=2, sort_keys=False, trailing_newline=True)`

The helper intentionally lives under `Iris/build/tools/common/`, not under
`description/v2`, to avoid making general build pipeline scripts depend on the
description-specific layer.

## Migrated scripts

| Script | Migration | Verification |
|---|---|---|
| `Iris/build/tools/pipeline/build_action_requirement_index.py` | replaced local JSON load/write with `tools.common.io` | direct script PASS, `python -m` PASS, quality gates PASS |
| `Iris/build/tools/pipeline/build_legacy_inventory.py` | replaced local JSON load/write with `tools.common.io` | direct script PASS, `python -m` PASS |
| `Iris/build/tools/pipeline/build_legacy_candidates.py` | replaced local JSON load/write with `tools.common.io` | direct script PASS, `python -m` PASS |
| `Iris/build/tools/pipeline/build_recipe_nav_registry.py` | replaced local JSON load/write with `tools.common.io`, preserving no-trailing-newline output | direct script PASS, `python -m` PASS |
| `Iris/build/tools/pipeline/build_recipe_requirements_index.py` | replaced local JSON load/write with `tools.common.io`, preserving no-trailing-newline output | direct script PASS, `python -m` PASS |
| `Iris/build/tools/pipeline/classify_action_evidence.py` | replaced local JSON load/write with `tools.common.io`; made sibling/common imports explicit; fixed pre-existing override-only aggregate initialization order exposed by direct execution without changing existing mechanical classifications | direct script PASS, `python -m` PASS |
| `Iris/build/tools/pipeline/build_usecases_by_fulltype.py` | replaced local JSON load/write with `tools.common.io`; made sibling/common imports explicit for direct and module execution | direct script PASS, `python -m` PASS |
| `Iris/build/description_generator.py` | replaced local JSON load/write with `tools.common.io`, preserving no-trailing-newline output | direct script PASS, `python -m` PASS |
| `Iris/build/convert_descriptions_to_lua.py` | replaced local JSON load with `tools.common.io` | direct script PASS, `python -m` PASS |
| `Iris/build/convert_labelmap_to_lua.py` | replaced local JSON load with `tools.common.io` | compile PASS; direct and `python -m` reach existing label-map coverage FAIL |
| `Iris/build/test_require_render.py` | replaced local JSON load with `tools.common.io` | direct script PASS, `python -m` PASS |
| `Iris/build/recipe_evidence_pipeline.py` | replaced local JSON load/write with `tools.common.io`, preserving no-trailing-newline output | direct script PASS, `python -m` PASS |
| `Iris/build/rightclick_evidence_pipeline.py` | replaced JSON load/output writes with `tools.common.io`, preserving no-trailing-newline output; deterministic hash serialization remains local | direct script PASS, `python -m` PASS |
| `Iris/build/tools/pipeline/build_recipe_classification_matches.py` | replaced JSON load/write with `tools.common.io`, preserving no-trailing-newline output; made build/pipeline import paths explicit | compile PASS; direct and `python -m` reach existing `phase2_rules.rules` missing-package blocker |
| `Iris/build/tools/pipeline/parse_recipe_require_fields.py` | replaced output JSON write with `tools.common.io`, preserving no-trailing-newline output | direct script PASS, `python -m` PASS |
| `Iris/build/quality_gates.py` | replaced JSON file loads and JSON report/frozen writes with `tools.common.io`; canonical hash serialization remains local | compile PASS, direct script PASS, `python -m` PASS |
| `Iris/build/tools/pipeline/apply_registry_merge.py` | replaced JSON loads and registry write with `tools.common.io`, preserving no-trailing-newline registry output | compile PASS, direct script PASS with no changes needed, `python -m` PASS with no changes needed |

Output diff notes:

- `Iris/output/action_requirement_index.v2.4.json` has no content diff after
  migration.
- `Iris/output/action_evidence_classification.v2.4.json` has no content diff
  after migration and the override-only initialization fix.
- `Iris/output/usecases_by_fulltype.v2.4.json` still carries the accepted
  `Base.Lemongrass` addition from the v2.4 rebaseline, not a JSON I/O helper
  formatting change.
- Regenerating descriptions propagated the current recipe label rendering and
  the accepted `Base.Lemongrass` usecase entry into
  `Iris/output/descriptions_by_fulltype.v2.4.json`; the v2.4 description
  count/hash was resealed in `expected_diff.json`.

Known verification blocker:

- `Iris/build/convert_labelmap_to_lua.py` fails its existing FAIL-LOUD coverage
  gate because `usecases_by_fulltype.v2.4.json` currently has 337 use_case_ids
  while `usecase_label_map.json` has 38 labels; 321 `uc.recipe.*` IDs are not
  covered by that label map. This blocker predates the common I/O import
  change and should be handled as a label-map coverage batch.
- `Iris/build/tools/pipeline/build_recipe_classification_matches.py` reaches an
  existing `ModuleNotFoundError: No module named 'phase2_rules.rules'` because
  `Iris/build/phase2_rules/rules/` is absent in the current tree. This blocks
  runtime verification of that generator independently of the common I/O import
  change.

## Remaining active root/pipeline JSON helper candidates

No active root/pipeline JSON helper candidates remain from this Phase 3-1
batch. Mutation-oriented verification for `apply_registry_merge.py` used the
current converged accept list and did not rewrite the registry.

`Iris/build/description/v2/tools/build/compose_layer3_io.py` remains the
description v2 local facade for now. It can later delegate to common helpers
without changing the description v2 public import surface.
