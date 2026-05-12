# Iris Refactor Phase 3 Version Manifest

Date: 2026-05-06

Source roadmap: `docs/Iris/iris-refactoring-final-roadmap-v1.md`

This record starts Phase 3-5. The goal is to keep build suffixes, require-field
suffixes, and quality-gate labels from drifting across scripts.

## Decision

Adopted a Python-only manifest first:

- `Iris/build/tools/common/versions.py`

Current constants:

- `BUILD_VERSION = "v2.4"`
- `REQUIRE_FIELDS_VERSION = "v2.5"`
- `QUALITY_GATES_VERSION = "v2.5"`

JSON `build_manifest.json` is deferred until Lua/runtime code consumes the
version contract directly. Current consumers are Python build and quality-gate
scripts, so a Python module keeps the contract simpler and avoids adding a
runtime-facing file before it has a reader.

## Migrated Consumers

- `Iris/build/quality_gates.py`
- `Iris/build/recipe_evidence_pipeline.py`
- `Iris/build/description_generator.py`
- `Iris/build/convert_descriptions_to_lua.py`
- `Iris/build/tools/pipeline/build_action_requirement_index.py`
- `Iris/build/tools/pipeline/classify_action_evidence.py`
- `Iris/build/tools/pipeline/build_usecases_by_fulltype.py`
- `Iris/build/tools/pipeline/build_legacy_inventory.py`
- `Iris/build/tools/pipeline/build_legacy_candidates.py`
- `Iris/build/tools/pipeline/build_recipe_classification_matches.py`
- `Iris/build/tools/pipeline/build_recipe_nav_registry.py`
- `Iris/build/tools/pipeline/build_recipe_requirements_index.py`
- `Iris/build/tools/pipeline/parse_recipe_require_fields.py`

## Remaining Boundary

Hard-coded `v2.4` and `v2.5` strings may remain in docstrings and comments when
they describe historical artifacts or phase labels. Operational output names,
input names, and report labels should use `tools.common.versions`.
