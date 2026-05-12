# Phase 4-6 Wiki Fallback Batch 6

Date: 2026-05-06

Status: implemented, static checks complete, Korean and English console
validation pass.

## Scope

This batch follows `phase4_browser_common_base_batch5.md`.

It centralizes `IrisWikiSections.lua` translation fallback helpers without
changing the rendered section content or public Wiki section functions.

This batch does not change the public Wiki section surface:

- `IrisWikiSections.renderBasicInfoSection(item)`
- `IrisWikiSections.renderTagsSection(item)`
- `IrisWikiSections.renderLayer3Section(item)`
- `IrisWikiSections.renderFoodSection(item)`
- `IrisWikiSections.renderWeaponSection(item)`
- `IrisWikiSections.renderConnectionSection(item)`
- `IrisWikiSections.renderMiscSection(item)`
- `IrisWikiSections.getAllSections(item)`
- `IrisWikiSections.renderCoreInfoSection(item)`
- `IrisWikiSections.renderRecipeInfoSection(item)`
- `IrisWikiSections.renderMetaInfoSection(item)`
- `IrisWikiSections.renderUseCaseSection(item)`

## Runtime Files Changed

- `Iris/media/lua/client/Iris/UI/Wiki/IrisWikiSections.lua`

## Test Files Changed

- `Iris/build/description/v2/tests/test_wiki_fallback_contract.py`

## Extracted Responsibilities

`IrisWikiSections.lua` now centralizes Wiki fallback behavior in:

- `eachTranslationLoader(callback)`
- `resolveTranslationText(key, fallback)`
- `getRuntimeLangKey()`

`getLabel(key)` now delegates to `resolveTranslationText(...)` while preserving
the existing detail label fallback rule:

- missing `Iris_Detail_*` keys display as the key with `Iris_Detail_` removed.

UseCase language detection now delegates to `getRuntimeLangKey()` in both
display-text and legacy label rendering paths.

## Non-Goals

This batch intentionally does not change:

- section order
- section inclusion/exclusion rules
- Layer 3 presentation formatting
- Browser layout
- translation source files
- release/dev log policy

## Static Checks

Performed:

- `python -B -m unittest Iris\build\description\v2\tests\test_wiki_fallback_contract.py`
  passed: `3 tests / OK`.
- `python -B -m unittest discover -s Iris\build\description\v2\tests -p "test_*.py"`
  passed: `328 tests / OK`.
- `git diff --check` for changed Phase 4-6 runtime, test, and documentation
  files. Passed with only the existing LF-to-CRLF warning for
  `IrisWikiSections.lua`.

Still not performed:

- Lua bytecode/syntax compile check. No `lua` or `luac` executable is available
  in the current environment.
- Explicit missing-key fallback UI evidence.

## Runtime Validation

Korean console validation:

- `Iris/_docs/refactor/phase4_ko_wiki_fallback_playtest_validation.md`
- archived evidence:
  `Iris/_docs/refactor/playtest_evidence/2026-05-06-ko-wiki-fallback/console.txt`

Korean pass evidence:

- `user.language=ko`: line 49
- `translator: language is KO`: line 277
- `[Iris] Bootstrap complete`: line 1266
- `Iris/IrisTranslationLoader.lua`: line 1333
- `Iris/UI/Wiki/IrisWikiSections.lua`: line 1361
- Iris `Lua error`, `stack traceback`, `ExceptionLogger`, `attempt to`, and
  `nil value` counts: 0.
- Iris-specific `ERROR`/`WARN` matches: 0.

English console validation:

- `Iris/_docs/refactor/phase4_en_wiki_fallback_playtest_validation.md`
- archived evidence:
  `Iris/_docs/refactor/playtest_evidence/2026-05-06-en-wiki-fallback/console.txt`

English pass evidence:

- `user.language=ko`: line 83
- `translator: language is EN`: line 312
- `[Iris] Bootstrap complete`: line 1301
- `Iris/IrisTranslationLoader.lua`: line 1368
- `Iris/UI/Wiki/IrisWikiSections.lua`: line 1396
- Iris `Lua error`, `stack traceback`, `ExceptionLogger`, `attempt to`, and
  `nil value` counts: 0.
- Iris-specific `ERROR`/`WARN` matches: 0.

## QA Closeout

Korean and English playtests validated `Console.txt` for:

- `Iris/UI/Wiki/IrisWikiSections.lua` loaded.
- `Iris/IrisTranslationLoader.lua` loaded.
- translator language is `KO` or `EN` for the tested pass.
- Iris bootstrap completion.
- no Iris `Lua error`, `stack traceback`, `ExceptionLogger`, `attempt to`, or
  `nil value`.
- translated detail labels still render in Browser/detail and Wiki surfaces.

This batch is closed at the console-validation level. Explicit missing-key
fallback UI evidence remains optional supporting evidence.
