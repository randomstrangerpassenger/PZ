# Iris Refactor Phase 3 Pytest Infra

Date: 2026-05-06

Historical source roadmap label: `docs/Iris/iris-refactoring-final-roadmap-v1.md`

This record starts Phase 3-6. The goal is to add pytest discovery without
breaking the existing unittest and direct-script compatibility paths.

## Measurement

Current `test_*.py` inventory:

- `Iris/build/description/v2/tests`: 169 files
- `Iris/build/tests`: 7 files
- other root build/test paths: 2 files
- total measured under `Iris/build` and `Iris/test`: 178 files

`Iris/build/tests` is mixed: most files are script-style regression checks, and
some perform work at import time or end in `sys.exit()`. That folder is not safe
for broad unittest or pytest collection yet.

## Added Infrastructure

- `pytest.ini`
- `Iris/build/tests/conftest.py`
- `Iris/build/build_import_contract.md` pytest section

Default pytest discovery is limited to:

- `Iris/build/description/v2/tests`
- `Iris/build/tests`

The build test `conftest.py` allows only:

- `test_evidence_pipeline_cross_track.py`

All other `Iris/build/tests/test_*.py` files remain direct execution checks
until they are converted into import-safe unittest/pytest modules.

## Compatibility

Existing unittest targets remain the required compatibility path:

- `python -B -m unittest Iris.build.description.v2.tests.test_build_iris_index_data`
- `python -B -m unittest Iris.build.tests.test_evidence_pipeline_cross_track`

Pytest is not installed in the current local Python environment, so this batch
verified configuration syntax through `compileall` for `conftest.py` and kept
runtime verification on the existing unittest path.
