# Phase 5-5 IrisMain Function Specs Batch 14

Date: 2026-05-08

Historical roadmap item label: `docs/Iris/iris-refactoring-final-roadmap-v1.md` Phase 5-5

Status: implemented and static-verified.

## Scope

- Convert `IrisMain.lua` `INIT_MODULES` from string-dispatched lifecycle
  fields to function fields.
- Preserve module boot order.
- Preserve protected-call boundaries for UI, data, and compatibility callbacks.
- Do not change config loading, startup test gating, or event registration.

## Implementation

- Added small function fields for each lifecycle callback:
  `hookTooltip`, `installBulletReloadCompat`, `hookContextMenu`,
  `buildBrowserData`, and `initMapIcon`.
- Added `loadModule(moduleName)` so each spec owns a `load` function instead of
  a `module` string interpreted by `runModuleSpec()`.
- Replaced `assign = "API"` with `onLoaded = assignApi`.
- Replaced `call = ...` and `boundary = ...` with `invoke = ...` and
  `protectedCall = ProtectedCall.<boundary>`.
- Updated `runModuleSpec()` to call the function fields directly.

## Validation

Passed:

- `python -B -m unittest Iris\build\description\v2\tests\test_phase5_iris_main_function_specs_contract.py`
- `python -B -m unittest Iris\build\description\v2\tests\test_protected_call_boundary_contract.py`
- `python -B -m unittest Iris\build\description\v2\tests\test_phase5_test_harness_dev_gate_contract.py`
- `python -B -m unittest Iris\build\description\v2\tests\test_phase5_ordering_single_pass_contract.py`
- `python -B -m unittest Iris\build\description\v2\tests\test_phase5_generator_debug_gate_contract.py`
- `python -B -m unittest Iris\build\description\v2\tests\test_layer3_data_chunking_contract.py`
- `python -B -m unittest discover -s Iris\build\description\v2\tests -p "test_*.py"`:
  `362 tests / OK`
- whitespace diff check: pass

## Runtime QA Notes

Production console validation should show the same Iris initialization order as
before this batch: recipe index, moveables index, fixing index,
classifications, IrisAPI, tooltip hook, bullet reload compatibility,
context-menu hook, BrowserData build, then map icon init.
