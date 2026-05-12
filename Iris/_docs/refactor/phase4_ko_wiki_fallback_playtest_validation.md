# Phase 4-6 Korean Wiki Fallback Playtest Validation

Date: 2026-05-06

Source log:

- `C:\Users\MW\Zomboid\Console.txt`

Archived evidence:

- `Iris/_docs/refactor/playtest_evidence/2026-05-06-ko-wiki-fallback/console.txt`

## Result

Status: pass at the console-validation level.

The Korean playtest loaded the Phase 4-6 Wiki fallback runtime module and
translation loader without Iris Lua exceptions.

## Language And Boot Evidence

- `user.language=ko`: line 49
- `translator: language is KO`: line 277
- `[Iris] Bootstrap complete`: line 1266

## Wiki Fallback Module Load Evidence

- `Iris/IrisTranslationLoader.lua`: line 1333
- `Iris/UI/Wiki/IrisWikiSections.lua`: line 1361

The deployed mod copy also contains the expected Phase 4-6 runtime files under
`C:\Users\MW\Zomboid\mods\Iris`:

- `media/lua/client/Iris/UI/Wiki/IrisWikiSections.lua`
- `media/lua/client/Iris/IrisTranslationLoader.lua`

The deployed `IrisWikiSections.lua` contains the Phase 4-6 centralized fallback
helper patterns:

- `local function eachTranslationLoader(callback)`: line 55
- `local function resolveTranslationText(key, fallback)`: line 66
- `local function getRuntimeLangKey()`: line 80
- `return resolveTranslationText(key, key:gsub("Iris_Detail_", ""))`: line 93
- `local lang = getRuntimeLangKey()`: line 631
- `local lang = getRuntimeLangKey()`: line 646

## Counts

Total lines: 2509

| Pattern | Count |
|---|---:|
| `Iris` | 78 |
| `IrisWikiSections` | 1 |
| `IrisTranslationLoader` | 1 |
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

None of these entries referenced Iris, IrisWiki, IrisTranslation, or IrisAPI.

## Remaining QA

English console validation is still required before Phase 4-6 can be closed at
the console-validation level.

Explicit missing-key fallback UI evidence has not been captured in this pass.
