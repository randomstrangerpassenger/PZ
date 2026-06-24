# Phase 5-3 TestHarness Dev Gate Batch 12

Date: 2026-05-08

Historical roadmap item label: `docs/Iris/iris-refactoring-final-roadmap-v1.md` Phase 5-3

Status: implemented and static-verified.

## Scope

- Remove `IrisDesc/TestHarness.lua` from production `media/lua/client`.
- Remove the legacy `Pulse/.../TestHarness.lua` production shim.
- Keep the test harness source available in a dev-only overlay.
- Gate startup test execution behind explicit dev config.

## Implementation

- Moved the harness to
  `Iris/_dev/media/lua/client/Iris/Dev/IrisDesc/TestHarness.lua`.
- Removed production autoload paths:
  - `Iris/media/lua/client/Iris/Logic/IrisDesc/TestHarness.lua`
  - `Iris/media/lua/client/Pulse/Iris/Logic/IrisDesc/TestHarness.lua`
- `IrisMain.lua` now uses `DEV_TESTHARNESS_MODULE =
  "Iris/Dev/IrisDesc/TestHarness"` and attempts it only when both
  `IrisConfig.DEBUG == true` and `IrisConfig.RUN_TESTS_ON_START == true`.
- `IrisConfig.lua` now documents the debug gate for startup tests.

## Validation

Passed:

- `python -B -m unittest Iris\build\description\v2\tests\test_phase5_test_harness_dev_gate_contract.py`
- `python -B -m unittest Iris\build\description\v2\tests\test_phase5_array_util_contract.py`
- `python -B -m unittest Iris\build\description\v2\tests\test_phase5_generator_debug_gate_contract.py`
- `python -B -m unittest Iris\build\description\v2\tests\test_layer3_data_chunking_contract.py`
- `python -B -m unittest discover -s Iris\build\description\v2\tests -p "test_*.py"`:
  `354 tests / OK`
- whitespace diff check: pass

## Runtime QA Notes

Production console validation should confirm that neither
`Iris/Logic/IrisDesc/TestHarness.lua` nor the legacy `Pulse/.../TestHarness.lua`
appears in the Lua loading log with default config.
