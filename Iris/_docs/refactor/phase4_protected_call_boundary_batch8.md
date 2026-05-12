# Phase 4-8 ProtectedCall Boundary Batch 8

Date: 2026-05-08

Status: implemented, static checks complete, Korean and English console
validation pass.

## Scope

This batch follows `phase4_layer3_presentation_formatting_batch7.md`.

It gives `IrisProtectedCall.lua` real boundary wrappers and migrates runtime
call sites away from raw `ProtectedCall.call(...)`.

The boundary decision and call-site table are recorded in:

- `Iris/_docs/refactor/phase4_protected_call_boundary_mapping.md`

## Runtime Files Changed

- `Iris/media/lua/client/Iris/Util/IrisProtectedCall.lua`
- `Iris/media/lua/client/Iris/Util/ItemKey.lua`
- `Iris/media/lua/client/Iris/IrisMain.lua`
- `Iris/media/lua/client/Iris/IrisTranslationLoader.lua`
- `Iris/media/lua/client/Iris/API/Description.lua`
- `Iris/media/lua/client/Iris/API/Index.lua`
- `Iris/media/lua/client/Iris/Data/layer3_renderer.lua`
- `Iris/media/lua/client/Iris/Compat/IrisBulletReloadCompat.lua`
- `Iris/media/lua/client/Iris/UI/Tooltip/IrisTooltipSummary.lua`
- `Iris/media/lua/client/Iris/UI/Wiki/IrisContextMenu.lua`
- `Iris/media/lua/client/Iris/UI/Wiki/IrisWikiPanel.lua`
- `Iris/media/lua/client/Iris/UI/Wiki/IrisWikiSections.lua`
- `Iris/media/lua/client/Iris/UI/Browser/IrisBrowser.lua`
- `Iris/media/lua/client/Iris/UI/Browser/IrisBrowserData.lua`
- `Iris/media/lua/client/Iris/UI/Browser/IrisBrowserDetail.lua`
- `Iris/media/lua/client/Iris/UI/Browser/IrisBrowserInteractionRenderer.lua`
- `Iris/media/lua/client/Iris/UI/Browser/IrisBrowserItemIndex.lua`
- `Iris/media/lua/client/Iris/UI/Browser/IrisBrowserRecipeNav.lua`
- `Iris/media/lua/client/Iris/UI/Browser/IrisBrowserQuery.lua`
- `Iris/media/lua/client/Iris/UI/Browser/IrisBrowserVariantIndex.lua`
- `Iris/media/lua/client/Iris/UI/Browser/IrisMapIcon.lua`
- `Iris/media/lua/client/Iris/UI/Browser/IrisRequirementPolicy.lua`

## Test Files Changed

- `Iris/build/description/v2/tests/test_protected_call_boundary_contract.py`

## Boundary Policy

`IrisProtectedCall.lua` now centralizes runtime protected-call policy with:

- `ProtectedCall.engine(...)`
- `ProtectedCall.ui(...)`
- `ProtectedCall.data(...)`
- `ProtectedCall.compat(...)`
- `ProtectedCall.require(...)`

All wrappers preserve the prior `pcall` return shape:

- success: `true, result`
- failure: `false, error`

Release mode remains quiet. Boundary failure diagnostics are emitted only when
`IrisConfig.DEBUG == true`, using a dev-only line shaped as:

- `[Iris][DEBUG] ProtectedCall.<boundary> failed: <error>`

## Migration Summary

Runtime direct `ProtectedCall.call(...)` call sites were migrated by boundary:

- `engine`: PZ engine globals, Java/userdata item methods, translation globals,
  player/perk checks.
- `ui`: UI panel/window methods, UI manager calls, crafting UI navigation.
- `data`: Iris static data/index/API lookups, Layer 3 data access,
  description/use-case generation.
- `compat`: compatibility shim calls and monkey-patch method forwarding.

`IrisMain.lua` now records the initialization callback boundary per module spec
so boot-time callbacks are not hidden behind a generic protected call.

## Non-Goals

This batch intentionally does not change:

- IrisAPI public surface
- Browser layout
- Wiki layout
- translation source behavior
- Layer 3 generated data
- release log verbosity
- fallback return values at call sites

## Static Checks

Performed:

- `python -B -m unittest Iris\build\description\v2\tests\test_protected_call_boundary_contract.py`
  passed: `5 tests / OK`.
- `python -B -m unittest Iris\build\description\v2\tests\test_wiki_fallback_contract.py`
  passed: `3 tests / OK`.
- `python -B -m unittest Iris\build\description\v2\tests\test_browser_common_base_contract.py`
  passed: `3 tests / OK`.
- `python -B -m unittest Iris\build\description\v2\tests\test_layer3_presentation_formatting_contract.py`
  passed: `5 tests / OK`.
- `python -B -m unittest Iris\build\description\v2\tests\test_interaction_cluster_phase_d_runtime.py`
  passed: `4 tests / OK`.
- `python -B -m unittest discover -s Iris\build\description\v2\tests -p "test_*.py"`
  passed: `338 tests / OK`.

Still not performed:

- Lua bytecode/syntax compile check. No `lua` or `luac` executable is available
  in the current environment.

## Runtime Validation

Korean console validation:

- `Iris/_docs/refactor/phase4_ko_protected_call_boundary_playtest_validation.md`
- archived evidence:
  `Iris/_docs/refactor/playtest_evidence/2026-05-08-ko-protected-call-boundary/console.txt`

Korean pass evidence:

- `user.language=ko`: line 107
- `translator: language is KO`: line 335
- `[Iris] Bootstrap complete`: line 1324
- `Iris/Util/IrisProtectedCall.lua`: line 1318
- `Iris/IrisMain.lua`: line 1319
- `Iris/API/Description.lua`: line 1359
- `Iris/API/Index.lua`: line 1363
- `Iris/IrisTranslationLoader.lua`: line 1391
- `Iris/UI/Browser/IrisBrowserData.lua`: line 1409
- `Iris/UI/Wiki/IrisWikiSections.lua`: line 1420
- Iris `Lua error`, `stack traceback`, `ExceptionLogger`, `attempt to`, and
  `nil value` counts: 0.
- Iris-specific `ERROR`/`WARN` matches: 0.
- `[Iris][DEBUG]` count: 0.

English console validation:

- `Iris/_docs/refactor/phase4_en_protected_call_boundary_playtest_validation.md`
- archived evidence:
  `Iris/_docs/refactor/playtest_evidence/2026-05-08-en-protected-call-boundary/console.txt`

English pass evidence:

- `user.language=ko`: line 94
- `translator: language is EN`: line 323
- `[Iris] Bootstrap complete`: line 1312
- `Iris/Util/IrisProtectedCall.lua`: line 1306
- `Iris/IrisMain.lua`: line 1307
- `Iris/API/Description.lua`: line 1347
- `Iris/API/Index.lua`: line 1351
- `Iris/IrisTranslationLoader.lua`: line 1379
- `Iris/UI/Browser/IrisBrowserData.lua`: line 1397
- `Iris/UI/Wiki/IrisWikiSections.lua`: line 1408
- Iris `Lua error`, `stack traceback`, `ExceptionLogger`, `attempt to`, and
  `nil value` counts: 0.
- Iris-specific `ERROR`/`WARN` matches: 0.
- `[Iris][DEBUG]` count: 0.

## QA Closeout

Korean and English playtests validated `Console.txt` for:

- `Iris/Util/IrisProtectedCall.lua` loaded.
- representative migrated consumers loaded:
  - `Iris/IrisMain.lua`
  - `Iris/IrisTranslationLoader.lua`
  - `Iris/API/Description.lua`
  - `Iris/API/Index.lua`
  - `Iris/UI/Browser/IrisBrowserData.lua`
  - `Iris/UI/Wiki/IrisWikiSections.lua`
- Iris bootstrap completion.
- translator language is `KO` or `EN` for the tested pass.
- no Iris `Lua error`, `stack traceback`, `ExceptionLogger`, `attempt to`, or
  `nil value`.
- no Iris-specific `ERROR`/`WARN`.
- release-mode console has no `[Iris][DEBUG]` entries.

This batch is closed at the console-validation level.
