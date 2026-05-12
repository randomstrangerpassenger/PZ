# Phase 4-4 Translation Source Batch 4

Date: 2026-05-06

Status: implemented, static checks complete, Korean and English console
validation pass.

## Scope

This batch follows `phase4_iris_browser_data_split_batch3.md`.

It makes `media/lua/shared/translate/*/Iris_*.txt` the canonical source for
Iris UI translation keys, then generates the Lua runtime data consumed by
`IrisTranslationLoader`.

This batch does not change the `IrisTranslationLoader` public surface:

- `IrisTranslationLoader.init()`
- `IrisTranslationLoader.get(key, fallback)`
- `IrisTranslationLoader.getLangKey()`
- global `IrisTranslationLoader`
- global `IrisTranslations`

## Runtime Files Changed

- `Iris/media/lua/client/Iris/IrisTranslationLoader.lua`
- `Iris/media/lua/client/Iris/Data/IrisTranslationData.lua`
- `Iris/media/lua/shared/translate/en/Iris_en.txt`
- `Iris/media/lua/shared/translate/ko/Iris_ko.txt`

## Build/Test Files Changed

- `Iris/build/tools/pipeline/build_iris_translation_data.py`
- `Iris/build/description/v2/tests/test_translation_source_contract.py`

## Source Decision

Canonical source:

- `Iris/media/lua/shared/translate/en/Iris_en.txt`
- `Iris/media/lua/shared/translate/ko/Iris_ko.txt`

Generated runtime data:

- `Iris/media/lua/client/Iris/Data/IrisTranslationData.lua`

Reason:

- The roadmap prefers txt canonical when aligning with the Project Zomboid
  native translation flow.
- The runtime still needs a Lua table because prior manual QA showed the PZ
  translation files were not reliably loaded for this mod.
- The generated Lua data preserves ASCII-only byte escapes for Korean text, so
  runtime behavior stays compatible with the existing Lua text handling.

## Drift Closed

Before this batch:

- `IrisTranslationLoader.lua` held inline `KO` and `EN` translation tables.
- `shared/translate/en/Iris_en.txt` had 85 keys.
- `shared/translate/ko/Iris_ko.txt` had 95 keys.
- The inline runtime table had 109 keys per language.

After this batch:

- `Iris_en.txt` has 109 keys.
- `Iris_ko.txt` has 109 keys.
- `IrisTranslationData.lua` has 109 generated keys per language.
- The loader no longer contains `local TRANSLATIONS = { ... }`.

Known value drift resolved while moving to txt canonical:

- EN `Iris_Sub_1K`, `Iris_Sub_1L`, `Iris_Sub_7A`, and `Iris_Sub_9A` now match
  the current runtime inline table values.
- KO `Iris_Sub_1D` now matches the current runtime inline table value.
- KO `Iris_Cap_RemoveEmbeddedObject` uses the human-readable txt value
  `박힌 물체 제거` instead of carrying forward the old escaped-byte typo from
  the inline table.

## Fallback Behavior

`IrisTranslationLoader.get(key, fallback)` now checks:

1. active language table
2. generated EN table
3. supplied fallback
4. key

This preserves existing callers while making missing non-EN keys fall back to
the canonical EN text before returning raw keys.

## Static Checks

Performed:

- `python -B Iris\build\tools\pipeline\build_iris_translation_data.py`
  generated `IrisTranslationData.lua`: `109 keys per language`.
- `git diff --check` for changed translation files, loader, generator, and
  translation source contract test.
- `python -B -m unittest Iris\build\description\v2\tests\test_translation_source_contract.py`
  passed: `3 tests / OK`.
- `python -B -m unittest discover -s Iris\build\description\v2\tests -p "test_*.py"`
  passed: `322 tests / OK`.

Still not performed:

- Lua bytecode/syntax compile check. No `lua` or `luac` executable is available
  in the current environment.
- Screenshot-level UI evidence for translated UI labels.

## Runtime Validation

Korean console validation passed:

- `Iris/_docs/refactor/phase4_ko_translation_source_playtest_validation.md`
- archived evidence:
  `Iris/_docs/refactor/playtest_evidence/2026-05-06-ko-translation-source/console.txt`

Key Korean runtime evidence:

- `user.language=ko`: line 82
- `translator: language is KO`: line 310
- `[Iris] Bootstrap complete`: line 1299
- `Iris/Data/IrisTranslationData.lua`: line 1352
- `Iris/IrisTranslationLoader.lua`: line 1366
- Iris-specific `ERROR`/`WARN` matches: 0
- Iris error patterns `Lua error`, `stack traceback`, `ExceptionLogger`,
  `attempt to`, and `nil value`: 0

English console validation passed:

- `Iris/_docs/refactor/phase4_en_translation_source_playtest_validation.md`
- archived evidence:
  `Iris/_docs/refactor/playtest_evidence/2026-05-06-en-translation-source/console.txt`

Key English runtime evidence:

- `user.language=ko`: line 104
- `translator: language is EN`: line 333
- `[Iris] Bootstrap complete`: line 1322
- `Iris/Data/IrisTranslationData.lua`: line 1375
- `Iris/IrisTranslationLoader.lua`: line 1389
- Iris-specific `ERROR`/`WARN` matches: 0
- Iris error patterns `Lua error`, `stack traceback`, `ExceptionLogger`,
  `attempt to`, and `nil value`: 0

The English log keeps `user.language=ko`, so it follows the same in-session
translator-switch pattern as prior English validations rather than a cold
process boot with `user.language=en`.

## Closeout

Korean and English console validation both confirmed:

- `Iris/IrisTranslationLoader.lua` loaded.
- `Iris/Data/IrisTranslationData.lua` loaded.
- Iris bootstrap completion.
- no Iris `Lua error`, `stack traceback`, `ExceptionLogger`, `attempt to`, or
  `nil value`.

This batch is closed at the console-validation level. Screenshot-level evidence
for translated Browser, tooltip, and context menu labels remains optional
supporting evidence.
