# Phase 5-6 IrisDesc Logger Direct Require Batch 15

Date: 2026-05-08

Roadmap item: `docs/Iris/iris-refactoring-final-roadmap-v1.md` Phase 5-6

Status: implemented and static-verified.

## Scope

- Simplify `Iris/Logic/IrisDesc/Logger.lua`.
- Treat `Iris/Util/IrisLogger.lua` as a hard runtime dependency.
- Remove the local `safeRequire` lookup, lazy cache, and print fallback.
- Preserve the public `IrisDescLogger` adapter methods.

## Implementation

- `IrisDesc/Logger.lua` now declares
  `local logger = require("Iris/Util/IrisLogger")`.
- `debug`, `info`, `warn`, `error`, and `isDebugEnabled` now delegate directly
  to `IrisLogger`.
- Missing `Iris/Util/IrisLogger` now fails at require time instead of falling
  back to partial warn/error printing.

## Validation

Passed:

- `python -B -m unittest Iris\build\description\v2\tests\test_phase5_iris_desc_logger_direct_require_contract.py`
- `python -B -m unittest Iris\build\description\v2\tests\test_phase5_generator_debug_gate_contract.py`
- `python -B -m unittest Iris\build\description\v2\tests\test_phase5_iris_main_function_specs_contract.py`
- `python -B -m unittest Iris\build\description\v2\tests\test_phase5_ordering_single_pass_contract.py`
- `python -B -m unittest Iris\build\description\v2\tests\test_phase5_test_harness_dev_gate_contract.py`
- `python -B -m unittest Iris\build\description\v2\tests\test_protected_call_boundary_contract.py`
- `python -B -m unittest discover -s Iris\build\description\v2\tests -p "test_*.py"`:
  `365 tests / OK`
- whitespace diff check: pass

## Runtime QA Notes

Production console validation should still show `Iris/Util/IrisLogger.lua`
loading before `Iris/Logic/IrisDesc/Logger.lua`. If `IrisLogger` is missing,
that is now an explicit packaging/load failure rather than a partially silent
fallback.
