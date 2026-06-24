# Phase 5-1 Generator Debug Gate Batch 10

Date: 2026-05-08

Historical roadmap item label: `docs/Iris/iris-refactoring-final-roadmap-v1.md` Phase 5-1

Status: implemented and static-verified.

## Scope

- Keep `IrisDesc/Generator.lua` debug diagnostics available in dev mode.
- Prevent release mode from constructing and iterating verbose Generator debug
  messages.
- Do not change description generation semantics, tag parsing, ordering,
  templates, or rendering.

## Implementation

- `Iris/Util/IrisLogger.lua` now exposes `isDebugEnabled()`, using the same
  lazy `IrisConfig.DEBUG` resolution as `debug()`.
- `Iris/Logic/IrisDesc/Logger.lua` forwards `isDebugEnabled()` to the shared
  Iris runtime logger and defaults to `false` if the shared logger is absent.
- `Iris/Logic/IrisDesc/Generator.lua` now resolves `debugEnabled` once per
  generation call and wraps all `Logger.debug(...)` calls and debug-only loops
  in `if debugEnabled then` blocks.

## Validation

Passed:

- `python -B -m unittest Iris\build\description\v2\tests\test_phase5_generator_debug_gate_contract.py`
- `python -B -m unittest Iris\build\description\v2\tests\test_layer3_data_chunking_contract.py`
- `python -B -m unittest discover -s Iris\build\description\v2\tests -p "test_*.py"`:
  `346 tests / OK`
- whitespace diff check: pass

## Runtime QA Notes

This batch changes release/dev log behavior only. It should not alter visible
description output. A later console playtest can confirm that release mode still
has no `[Iris][DEBUG]` output with `IrisConfig.DEBUG = false`.
