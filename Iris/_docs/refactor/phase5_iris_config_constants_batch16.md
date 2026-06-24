# Phase 5-7 IrisConfig Constants Batch 16

Date: 2026-05-08

Historical roadmap item label: `docs/Iris/iris-refactoring-final-roadmap-v1.md` Phase 5-7

Status: implemented and static-verified.

## Scope

- Name the numeric defaults in `IrisConfig.lua`.
- Preserve the public config surface and default values.
- Do not change tooltip, Browser map icon, debug, cache, or startup test
  behavior.

## Implementation

- Added local constants for:
  - `DEFAULT_ALT_TOOLTIP_MAX_LINES = 4`
  - `DEFAULT_MAP_ICON_BUTTON_X = 18`
  - `DEFAULT_MAP_ICON_BUTTON_Y = 360`
  - `DEFAULT_MAP_ICON_BUTTON_WIDTH = 32`
  - `DEFAULT_MAP_ICON_BUTTON_HEIGHT = 32`
- Replaced the public numeric assignments with those constants.

## Validation

Passed:

- `python -B -m unittest Iris\build\description\v2\tests\test_phase5_iris_config_constants_contract.py`
- `python -B -m unittest Iris\build\description\v2\tests\test_phase5_iris_main_function_specs_contract.py`
- `python -B -m unittest Iris\build\description\v2\tests\test_phase5_test_harness_dev_gate_contract.py`
- `python -B -m unittest Iris\build\description\v2\tests\test_phase5_iris_desc_logger_direct_require_contract.py`
- `python -B -m unittest Iris\build\description\v2\tests\test_protected_call_boundary_contract.py`
- `python -B -m unittest discover -s Iris\build\description\v2\tests -p "test_*.py"`:
  `368 tests / OK`
- whitespace diff check: pass

## Runtime QA Notes

This batch should not produce visible runtime differences. Production console
validation only needs to confirm normal Iris bootstrap and that `IrisConfig.lua`
still loads without Lua errors.
