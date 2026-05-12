# Phase 5-4 Ordering Single Pass Batch 13

Date: 2026-05-08

Roadmap item: `docs/Iris/iris-refactoring-final-roadmap-v1.md` Phase 5-4

Status: implemented and static-verified.

## Scope

- Remove the duplicate `TagParser.toArray()` conversion in the normal
  description generation path.
- Preserve anchor selection and subcategory ordering rules.
- Keep existing `pickAnchor()` and `orderSubcategories()` API functions
  available for compatibility.

## Implementation

- Added `sortedSubcategories()` as the single `TagParser.toArray()` call site
  inside `Ordering.lua`.
- Added `moveAnchorToFront()` to share anchor-front behavior.
- Added `Ordering.resolveSubcategories(subcat_set, meta_primary_opt)`, which
  returns both `anchor` and `ordered` from one sorted array.
- Updated `Generator.lua` to use `resolveSubcategories()` instead of calling
  `pickAnchor()` and `orderSubcategories()` sequentially.

## Validation

Passed:

- `python -B -m unittest Iris\build\description\v2\tests\test_phase5_ordering_single_pass_contract.py`
- `python -B -m unittest Iris\build\description\v2\tests\test_phase5_generator_debug_gate_contract.py`
- `python -B -m unittest Iris\build\description\v2\tests\test_phase5_array_util_contract.py`
- `python -B -m unittest Iris\build\description\v2\tests\test_phase5_test_harness_dev_gate_contract.py`
- `python -B -m unittest Iris\build\description\v2\tests\test_layer3_data_chunking_contract.py`
- `python -B -m unittest discover -s Iris\build\description\v2\tests -p "test_*.py"`:
  `358 tests / OK`
- whitespace diff check: pass

## Runtime QA Notes

This batch should not alter rendered description ordering. A later playtest can
spot-check items with multiple tags, including a meta primary tag, to confirm
the first displayed block and subsequent block order are unchanged.
