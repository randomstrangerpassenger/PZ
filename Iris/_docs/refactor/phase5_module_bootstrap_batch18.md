# Phase 5-9 Module Bootstrap Batch 18

Date: 2026-05-08

Historical roadmap item label: `docs/Iris/iris-refactoring-final-roadmap-v1.md` Phase 5-9

Status: implemented, static-verified, and KO runtime smoke-validated.

## Scope

- Consolidate repeated Iris runtime module logger bootstrap boilerplate.
- Keep `IrisLogger.lua` independent of the new helper to avoid a require cycle.
- Preserve release-visible fallback logging for `IrisMain.lua` boot failures.
- Avoid changing `INIT_MODULES` boot order or module callback behavior.

## Implementation

- Added `Iris/Util/IrisModuleBootstrap.lua`.
- The helper owns:
  - shared `safeRequire` access
  - optional `IrisLogger` resolution
  - no-op logger fallbacks for normal runtime modules
  - print-backed fallback logging for `IrisMain.lua`
- Replaced repeated `loggerOk, logger` setup in:
  - `IrisMain.lua`
  - `IrisTranslationLoader.lua`
  - `API/Description.lua`
  - `API/StaticData.lua`
  - `Data/layer3_renderer.lua`
  - `UI/Browser/IrisBrowser.lua`
  - `UI/Browser/IrisBrowserData.lua`
  - `UI/Browser/IrisBrowserItemIndex.lua`
  - `UI/Browser/IrisMapIcon.lua`
  - `UI/Tooltip/IrisAltTooltip.lua`
  - `UI/Wiki/IrisContextMenu.lua`
  - `UI/Wiki/IrisWikiSections.lua`

## Contract

- `IrisModuleBootstrap.lua` is the only Iris runtime module that directly
  resolves `Iris/Util/IrisLogger` through `safeRequire`.
- Runtime consumers use `require("Iris/Util/IrisModuleBootstrap").create()`.
- `IrisMain.lua` uses `create({ printFallback = true })` so missing logger
  failures can still reach the console.
- `IrisLogger.lua` does not require `IrisModuleBootstrap.lua`.

## Validation

Passed:

- `python -B -m unittest Iris\build\description\v2\tests\test_phase5_module_bootstrap_contract.py`
- `python -B -m unittest Iris\build\description\v2\tests\test_phase5_iris_main_function_specs_contract.py`
- `python -B -m unittest discover -s Iris\build\description\v2\tests -p "test_*.py"`:
  `376 tests / OK`

## Runtime QA

Korean runtime smoke passed:

- `Iris/_docs/refactor/playtest_evidence/2026-05-08-ko-module-bootstrap/console.txt`
- `translator: language is KO`: line 315
- `IrisMain.lua`: line 1299
- `Iris/Util/IrisModuleBootstrap.lua`: line 1300
- `Iris/Util/IrisRequire.lua`: line 1301
- `Iris/Util/IrisLogger.lua`: line 1302
- `Iris/IrisConfig.lua`: line 1303
- `IrisMain loaded successfully`: line 1304
- `[Iris] Bootstrap complete`: line 1305
- `IrisTranslationLoader.lua`: line 1385
- `Iris/UI/Browser/IrisBrowserData.lua`: line 1402
- `Iris/UI/Browser/IrisMapIcon.lua`: line 1407
- `Iris/UI/Wiki/IrisContextMenu.lua`: line 1411
- `TestHarness`: 0 matches
- Iris Lua error patterns: 0 matches

The broad `FAILED to load` pattern matched only vanilla font texture messages,
not Iris module failures.
