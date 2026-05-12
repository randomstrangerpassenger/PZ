# Phase 4-4 Korean Translation Source Playtest Validation

Date: 2026-05-06

Source log:

- `C:\Users\MW\Zomboid\Console.txt`

Archived evidence:

- `Iris/_docs/refactor/playtest_evidence/2026-05-06-ko-translation-source/console.txt`

## Result

Status: pass at the console-validation level.

The Korean playtest loaded the Phase 4-4 translation source modules without
Iris Lua exceptions.

## Language And Boot Evidence

- `user.language=ko`: line 82
- `translator: language is KO`: line 310
- `[Iris] Bootstrap complete`: line 1299

## Translation Source Module Load Evidence

- `Iris/Data/IrisTranslationData.lua`: line 1352
- `Iris/IrisTranslationLoader.lua`: line 1366

The deployed mod copy also contains the expected translation source files under
`C:\Users\MW\Zomboid\mods\Iris`:

- `media/lua/client/Iris/Data/IrisTranslationData.lua`
- `media/lua/client/Iris/IrisTranslationLoader.lua`
- `media/lua/shared/translate/ko/Iris_ko.txt`
- `media/lua/shared/translate/en/Iris_en.txt`

## Counts

Total lines: 2551

| Pattern | Count |
|---|---:|
| `Iris` | 77 |
| `IrisTranslationLoader` | 1 |
| `IrisTranslationData` | 1 |
| `Lua error` | 0 |
| `stack traceback` | 0 |
| `ExceptionLogger` | 0 |
| `attempt to` | 0 |
| `nil value` | 0 |
| `[Iris][DEBUG]` | 0 |

Iris-specific `ERROR`/`WARN` matches: 0.

## Non-Iris Noise

Observed non-Iris noise includes:

- Echo freeze/fallback tick warnings.
- Pulse `LuaAdapter` save/event errors.
- TextManager font warnings.
- Vanilla/mod recipe, sound, script, vehicle, moveables, mannequin, and
  `SuburbsDistributions["laboratory"]` warnings/errors.
- Missing optional require warnings such as `ISTimer`, CheatMenuRebirth modules,
  and `ISBuildingObject`.

None of these entries referenced Iris, IrisTranslation, or IrisAPI.

## Remaining QA

English console validation is still required before Phase 4-4 can be closed at
the console-validation level.

Screenshot-level UI evidence for translated Browser, tooltip, and context menu
labels remains optional supporting evidence.
