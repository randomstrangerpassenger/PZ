# Phase 4-5 Browser Common Base Batch 5

Date: 2026-05-06

Status: implemented, static checks complete, Korean and English console
validation pass.

## Scope

This batch follows `phase4_translation_source_batch4.md`.

It extracts Browser dependency access and panel lifecycle helpers into a shared
Browser base module without changing Browser layout.

This batch does not change the public Browser entrypoints:

- `IrisBrowser.openSearch()`
- `IrisBrowser.openForItem(item)`
- `IrisBrowser:selectItem(item)`
- `IrisBrowser:showDetail(fullType)`

## Runtime Files Changed

- `Iris/media/lua/client/Iris/UI/Browser/IrisBrowserBase.lua`
- `Iris/media/lua/client/Iris/UI/Browser/IrisBrowser.lua`
- `Iris/media/lua/client/Iris/UI/Browser/IrisBrowserListController.lua`
- `Iris/media/lua/client/Iris/UI/Browser/IrisBrowserDetail.lua`

## Test Files Changed

- `Iris/build/description/v2/tests/test_browser_common_base_contract.py`

## Extracted Responsibilities

`IrisBrowserBase.lua` now owns:

- Browser data lookup through the install context.
- Wiki section lookup through the install context.
- Browser data build-on-open helper.
- Visible instance close helper.
- Centered panel bounds calculation.
- Centered panel creation and UI manager attachment.

`IrisBrowserInteractionRenderer.lua` was inspected but left unchanged in this
batch because it does not own Browser dependency lookup or panel lifecycle
logic.

The centered panel math is intentionally unchanged:

- width: `math.min(1200, screenW - 100)`
- height: `math.min(700, screenH - 100)`
- position: centered on the current screen size

## Drift Closed

Before this batch:

- `IrisBrowser.openSearch()` and `IrisBrowser.openForItem(item)` duplicated the
  same screen-size, panel-size, centering, instantiate, UI-manager, visibility,
  and bring-to-top sequence.
- `IrisBrowserListController.lua` and `IrisBrowserDetail.lua` each carried local
  context access helpers for Browser data.
- `IrisBrowserDetail.lua` also carried a local context access helper for Wiki
  sections.

After this batch:

- Browser panel lifecycle is centralized in `IrisBrowserBase.createCenteredPanel`.
- Browser data build-on-open is centralized in
  `IrisBrowserBase.ensureBrowserDataBuilt`.
- Split Browser modules use `IrisBrowserBase.getBrowserData(context)` and
  `IrisBrowserBase.getWikiSections(context)`.

## Non-Goals

This batch intentionally does not change:

- Browser layout proportions.
- `openSearch` / `openForItem` panel dimensions.
- category, subcategory, item, search, detail, or recipe navigation behavior.
- Browser data classification, query, filter, or variant behavior.
- release/dev log policy.

## Static Checks

Performed:

- `python -B -m unittest Iris\build\description\v2\tests\test_browser_common_base_contract.py`
  passed: `3 tests / OK`.
- `python -B -m unittest discover -s Iris\build\description\v2\tests -p "test_*.py"`
  passed: `325 tests / OK`.
- `git diff --check` for changed Phase 4-5 runtime, test, and documentation
  files. Passed with only the existing LF-to-CRLF warning for
  `IrisBrowser.lua`.

Still not performed:

- Lua bytecode/syntax compile check. No `lua` or `luac` executable is available
  in the current environment.
- Screenshot-level Browser layout evidence.

## Runtime Validation

English console validation passed:

- `Iris/_docs/refactor/phase4_en_browser_common_base_playtest_validation.md`
- archived evidence:
  `Iris/_docs/refactor/playtest_evidence/2026-05-06-en-browser-common-base/console.txt`

Key English runtime evidence:

- `user.language=ko`: line 67
- `translator: language is EN`: line 296
- `[Iris] Bootstrap complete`: line 1285
- `Iris/UI/Browser/IrisBrowser.lua`: line 1360
- `Iris/UI/Browser/IrisBrowserBase.lua`: line 1361
- `Iris/UI/Browser/IrisBrowserListController.lua`: line 1362
- `Iris/UI/Browser/IrisBrowserDetail.lua`: line 1364
- Iris-specific `ERROR`/`WARN` matches: 0
- Iris error patterns `Lua error`, `stack traceback`, `ExceptionLogger`,
  `attempt to`, and `nil value`: 0

The English log keeps `user.language=ko`, so it follows the same in-session
translator-switch pattern as prior English validations rather than a cold
process boot with `user.language=en`.

Prior English attempt invalid:

- archived evidence:
  `Iris/_docs/refactor/playtest_evidence/2026-05-06-en-browser-common-base-invalid/console.txt`

That attempt reached `translator: language is EN` and Iris bootstrap completion
without Iris errors, but did not validate this batch because the deployed mod
copy was missing `Iris/UI/Browser/IrisBrowserBase.lua`.

Korean console validation passed:

- `Iris/_docs/refactor/phase4_ko_browser_common_base_playtest_validation.md`
- archived evidence:
  `Iris/_docs/refactor/playtest_evidence/2026-05-06-ko-browser-common-base/console.txt`

Key Korean runtime evidence:

- `user.language=ko`: line 49
- `translator: language is KO`: line 277
- `[Iris] Bootstrap complete`: line 1266
- `Iris/UI/Browser/IrisBrowser.lua`: line 1341
- `Iris/UI/Browser/IrisBrowserBase.lua`: line 1342
- `Iris/UI/Browser/IrisBrowserListController.lua`: line 1343
- `Iris/UI/Browser/IrisBrowserDetail.lua`: line 1345
- Iris-specific `ERROR`/`WARN` matches: 0
- Iris error patterns `Lua error`, `stack traceback`, `ExceptionLogger`,
  `attempt to`, and `nil value`: 0

## Closeout

Korean and English console validation both confirmed:

- `Iris/UI/Browser/IrisBrowserBase.lua` loaded.
- `Iris/UI/Browser/IrisBrowser.lua` loaded.
- `Iris/UI/Browser/IrisBrowserListController.lua` loaded.
- `Iris/UI/Browser/IrisBrowserDetail.lua` loaded.
- Iris bootstrap completion.
- no Iris `Lua error`, `stack traceback`, `ExceptionLogger`, `attempt to`, or
  `nil value`.

This batch is closed at the console-validation level. Screenshot-level Browser
layout evidence remains optional supporting evidence.
