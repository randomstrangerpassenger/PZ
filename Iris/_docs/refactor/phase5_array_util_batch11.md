# Phase 5-2 Array Utility Batch 11

Date: 2026-05-08

Roadmap item: `docs/Iris/iris-refactoring-final-roadmap-v1.md` Phase 5-2

Status: implemented and static-verified.

## Scope

- Extract small array membership logic into `Iris/Util/Array.lua`.
- Keep `StaticData.arrayContains()` available as a compatibility alias.
- Move direct membership consumers to the shared utility.
- Do not change static data loading, tag generation, use-case output, or
  moveables index data.

## Implementation

- Added `Iris/Util/Array.lua` with `Array.contains(values, value)`.
- `Iris/API/StaticData.lua` now delegates `arrayContains()` to
  `Array.contains()` instead of carrying its own loop.
- `Iris/API/Tags.lua` and `Iris/API/UseCases.lua` now use `Array.contains()`
  directly for membership checks.
- `Iris/Data/IrisMoveablesIndex.lua` now uses `Array.contains()` for
  `tagIn()`.

## Validation

Passed:

- `python -B -m unittest Iris\build\description\v2\tests\test_phase5_array_util_contract.py`
- `python -B -m unittest Iris\build\description\v2\tests\test_phase5_generator_debug_gate_contract.py`
- `python -B -m unittest Iris\build\description\v2\tests\test_layer3_data_chunking_contract.py`
- `python -B -m unittest discover -s Iris\build\description\v2\tests -p "test_*.py"`:
  `350 tests / OK`
- whitespace diff check: pass

## Runtime QA Notes

This batch changes shared helper placement only. A later console playtest should
confirm that Iris bootstrap still loads `Iris/Util/Array.lua` without require
errors and that tag/use-case/moveables interactions remain error-free.
