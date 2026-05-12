# Iris Refactor Phase 1 Closeout Scope

Date: 2026-05-05

Source roadmap: `docs/Iris/iris-refactoring-final-roadmap-v1.md`

This is the post-cleanup remeasurement required before Phase 3 build-pipeline
structure work.

## Active build surface

| Surface | Count | Disposition |
|---|---:|---|
| Root `Iris/build/*.py` entrypoints | 8 | active |
| `Iris/build/tools/pipeline/*.py` | 12 | active keep-list |
| `Iris/build/tests/*.py` | 7 | active, script-style test folder |
| Phase package directories, total `.py` | 30 | active imports |
| `Iris/build/tools/oneshots/*.py` | 15 | historical one-shot reference set |
| `Iris/build/description/v2/tests/test_*.py` | 169 | active description v2 tests |
| `Iris/build/description/v2/tools/build/*.py` | 269 | governed by local inventory |
| Description v2 `build_*.py` | 171 | candidate universe only |
| Description v2 `report_*.py` | 55 | candidate universe only |
| Description v2 other `.py` | 43 | candidate universe only |

## Root cleanup result

The Iris root now contains only active root contract files:

- `Iris/iris-input-schema-v0.2-final.meta.json`
- `Iris/mod.info`

Root intermediate artifacts were moved according to:

- `Iris/_docs/refactor/phase1_root_artifact_disposition.md`

Historical `_archive/p0-2/` payloads are excluded from packaging and git noise.

## Phase 3 precondition

Phase 3 work must use the active surfaces above. In particular:

- Do not treat `build_*.py` or `report_*.py` names as an archive criterion.
- Do not introduce a common build helper before the Python import/execution
  contract is documented.
- Preserve standalone script execution for the active root and pipeline commands
  unless a later contract explicitly changes it.
- Phase 3 import and execution rules are sealed in
  `Iris/build/build_import_contract.md`.
- Phase 3 JSON I/O common migration state is tracked in
  `Iris/_docs/refactor/phase3_json_io_common_migration.md`.
