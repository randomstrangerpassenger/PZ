# Round 3 Pytest Route Report

Generated: `2026-06-11T21:51:00+09:00`

## Default Route

`python -B -m pytest -q`

Result: `45 passed, 363 deselected, 5 subtests passed`.

The default pytest route now collects:

- 44 description-v2 current-contract tests from `Iris/build/description/v2/tests`
- 1 root build active pytest test:
  `Iris/build/tests/test_evidence_pipeline_cross_track.py`

## Explicit Routes

| Command | Result |
|---|---|
| `python -B -m pytest -q --round3-contract=historical Iris\build\description\v2\tests` | 284 passed, 123 deselected |
| `python -B -m pytest -q --round3-contract=diagnostic Iris\build\description\v2\tests` | 79 passed, 328 deselected |

## Implementation

- `Iris/build/description/v2/tests/conftest.py` filters description-v2 tests by
  `Iris/_docs/round3/round3_test_taxonomy.json`.
- `pytest.ini` uses a file-level root build testpath so script-style root build
  tests are not imported by default.
- Historical and diagnostic tests remain explicit pytest routes.
