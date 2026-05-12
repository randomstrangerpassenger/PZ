# Phase 4-7 English Layer 3 Presentation Formatting Playtest Validation

Date: 2026-05-08

Source log:

- `C:\Users\MW\Zomboid\Console.txt`
- last modified: 2026-05-08 01:01:39

Archived evidence:

- `Iris/_docs/refactor/playtest_evidence/2026-05-08-en-layer3-presentation-formatting/console.txt`

## Result

Status: pass at the console-validation level.

The English playtest loaded the Phase 4-7 UI-only Layer 3 display formatter,
Wiki section consumer, and raw Layer 3 renderer without Iris Lua exceptions.

## Language And Boot Evidence

- `user.language=ko`: line 105
- `translator: language is EN`: line 334
- `[Iris] Bootstrap complete`: line 1323

The log keeps `user.language=ko`, so this follows the same in-session
translator-switch pattern as prior English validations rather than a cold
process boot with `user.language=en`.

## Layer 3 Presentation Module Load Evidence

- `Iris/Data/layer3_renderer.lua`: line 1388
- `Iris/UI/Layer3/IrisLayer3DisplayFormatter.lua`: line 1414
- `Iris/UI/Wiki/IrisWikiSections.lua`: line 1419

The deployed mod copy also contains the expected Phase 4-7 runtime files under
`C:\Users\MW\Zomboid\mods\Iris`:

- `media/lua/client/Iris/UI/Layer3/IrisLayer3DisplayFormatter.lua`
- `media/lua/client/Iris/UI/Wiki/IrisWikiSections.lua`
- `media/lua/client/Iris/Data/layer3_renderer.lua`

The deployed files contain the expected boundary markers:

- `IrisLayer3DisplayFormatter.lua`: `local function splitSentences(text)`, line
  34.
- `IrisLayer3DisplayFormatter.lua`: `function Formatter.format(text)`, line 56.
- `IrisWikiSections.lua`:
  `require("Iris/UI/Layer3/IrisLayer3DisplayFormatter")`, line 20.
- `IrisWikiSections.lua`: `return Layer3DisplayFormatter.format(l3text)`, line
  189.
- `layer3_renderer.lua`: `function Layer3Renderer.getText(fullType, options)`,
  line 103.
- `layer3_renderer.lua`: `return entry.text_ko`, lines 98 and 116.

## Counts

Total lines: 2562

| Pattern | Count |
|---|---:|
| `Iris` | 79 |
| `IrisLayer3DisplayFormatter` | 1 |
| `IrisWikiSections` | 1 |
| `layer3_renderer` | 1 |
| `Lua error` | 0 |
| `stack traceback` | 0 |
| `ExceptionLogger` | 0 |
| `attempt to` | 0 |
| `nil value` | 0 |
| `[Iris][DEBUG]` | 0 |

Iris-specific `ERROR`/`WARN` matches: 0.

## Non-Iris Noise

Observed non-Iris noise includes:

- Echo/Pulse profiler, event bus, and command registration logs.
- Echo freeze/fallback tick warnings.
- TextManager font warnings.
- Vanilla/mod recipe, sound, script, vehicle, moveables, mannequin, and
  `SuburbsDistributions["laboratory"]` warnings/errors.
- Missing optional require warnings such as `ISTimer`, CheatMenuRebirth modules,
  and `ISBuildingObject`.

None of these entries referenced Iris, IrisWiki, IrisTranslation, IrisAPI, or
Layer3.

## Remaining QA

Korean console validation is still required before Phase 4-7 can be closed at
the console-validation level.

Screenshot-level Layer 3 display line evidence remains optional supporting
evidence.
