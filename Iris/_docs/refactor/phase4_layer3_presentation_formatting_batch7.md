# Phase 4-7 Layer 3 Presentation Formatting Batch 7

Date: 2026-05-07

Status: implemented, static checks complete, Korean and English console
validation pass.

## Scope

This batch follows `phase4_wiki_fallback_batch6.md`.

It makes the existing Layer 3 display formatting boundary explicit. Layer 3
source text remains owned by build-time authority and runtime data. Browser and
Wiki surfaces own display-only line formatting.

This batch does not change Layer 3 generated data or renderer authority:

- `rendered.json` text remains source text.
- `IrisLayer3Data.lua` remains source-text preserving.
- `layer3_renderer.lua` remains a raw text gate and does not own UI wrapping.

## Runtime Files Changed

- `Iris/media/lua/client/Iris/UI/Layer3/IrisLayer3DisplayFormatter.lua`
- `Iris/media/lua/client/Iris/UI/Wiki/IrisWikiSections.lua`

## Contract And Test Files Changed

- `Iris/_docs/layer3_presentation_formatting_contract.md`
- `Iris/build/description/v2/tests/test_layer3_presentation_formatting_contract.py`
- `Iris/build/description/v2/tests/test_interaction_cluster_phase_d_runtime.py`

## Extracted Responsibilities

`IrisLayer3DisplayFormatter.lua` is now the canonical UI-only Layer 3
presentation formatter.

`IrisWikiSections.renderLayer3Section(item)` still retrieves text through
`Layer3Renderer.getText(fullType)`, then applies display formatting through:

- `Layer3DisplayFormatter.format(l3text)`

The extracted formatter preserves the previous display behavior:

- trims empty display lines
- keeps one- or two-sentence lines as one display line
- splits longer lines into two-sentence display chunks
- preserves decimal numbers while detecting sentence boundaries

## Non-Goals

This batch intentionally does not change:

- Layer 3 sentence text
- `IrisLayer3Data.lua`
- `layer3_renderer.lua`
- publish-state gating
- Browser layout
- Wiki panel layout
- translation behavior
- release/dev log policy

## Static Checks

Performed:

- `python -B -m unittest Iris\build\description\v2\tests\test_layer3_presentation_formatting_contract.py`
  passed: `5 tests / OK`.
- `python -B -m unittest Iris\build\description\v2\tests\test_interaction_cluster_phase_d_runtime.py`
  passed: `4 tests / OK`.
- `python -B -m unittest Iris\build\description\v2\tests\test_wiki_fallback_contract.py`
  passed: `3 tests / OK`.
- `python -B -m unittest discover -s Iris\build\description\v2\tests -p "test_*.py"`
  passed: `333 tests / OK`.

Still not performed:

- Lua bytecode/syntax compile check. No `lua` or `luac` executable is available
  in the current environment.
- Screenshot-level Layer 3 display line evidence.

## Runtime Validation

English console validation:

- `Iris/_docs/refactor/phase4_en_layer3_presentation_formatting_playtest_validation.md`
- archived evidence:
  `Iris/_docs/refactor/playtest_evidence/2026-05-08-en-layer3-presentation-formatting/console.txt`

English pass evidence:

- `user.language=ko`: line 105
- `translator: language is EN`: line 334
- `[Iris] Bootstrap complete`: line 1323
- `Iris/Data/layer3_renderer.lua`: line 1388
- `Iris/UI/Layer3/IrisLayer3DisplayFormatter.lua`: line 1414
- `Iris/UI/Wiki/IrisWikiSections.lua`: line 1419
- Iris `Lua error`, `stack traceback`, `ExceptionLogger`, `attempt to`, and
  `nil value` counts: 0.
- Iris-specific `ERROR`/`WARN` matches: 0.

Korean console validation:

- `Iris/_docs/refactor/phase4_ko_layer3_presentation_formatting_playtest_validation.md`
- archived evidence:
  `Iris/_docs/refactor/playtest_evidence/2026-05-08-ko-layer3-presentation-formatting/console.txt`

Korean pass evidence:

- `user.language=ko`: line 49
- `translator: language is KO`: line 277
- `[Iris] Bootstrap complete`: line 1266
- `Iris/Data/layer3_renderer.lua`: line 1331
- `Iris/UI/Layer3/IrisLayer3DisplayFormatter.lua`: line 1357
- `Iris/UI/Wiki/IrisWikiSections.lua`: line 1362
- Iris `Lua error`, `stack traceback`, `ExceptionLogger`, `attempt to`, and
  `nil value` counts: 0.
- Iris-specific `ERROR`/`WARN` matches: 0.

## QA Closeout

Korean and English playtests validated `Console.txt` for:

- `Iris/UI/Layer3/IrisLayer3DisplayFormatter.lua` loaded.
- `Iris/UI/Wiki/IrisWikiSections.lua` loaded.
- `Iris/Data/layer3_renderer.lua` loaded.
- Iris bootstrap completion.
- translator language is `KO` or `EN` for the tested pass.
- no Iris `Lua error`, `stack traceback`, `ExceptionLogger`, `attempt to`, or
  `nil value`.
- no Iris-specific `ERROR`/`WARN`.

This batch is closed at the console-validation level. Browser/detail or Wiki
Layer 3 display line screenshots remain optional supporting evidence.
