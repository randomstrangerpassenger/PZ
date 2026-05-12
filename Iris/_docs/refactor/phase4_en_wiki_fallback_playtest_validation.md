# Phase 4-6 English Wiki Fallback Playtest Validation

Date: 2026-05-07

Source log:

- `C:\Users\MW\Zomboid\Console.txt`
- last modified: 2026-05-06 22:53:39

Archived evidence:

- `Iris/_docs/refactor/playtest_evidence/2026-05-06-en-wiki-fallback/console.txt`

## Result

Status: pass at the console-validation level.

The English playtest loaded the Phase 4-6 Wiki fallback runtime module and
translation loader without Iris Lua exceptions.

## Language And Boot Evidence

- `user.language=ko`: line 83
- `translator: language is EN`: line 312
- `[Iris] Bootstrap complete`: line 1301

The log keeps `user.language=ko`, so this follows the same in-session
translator-switch pattern as prior English validations rather than a cold
process boot with `user.language=en`.

## Wiki Fallback Module Load Evidence

- `Iris/IrisTranslationLoader.lua`: line 1368
- `Iris/UI/Wiki/IrisWikiSections.lua`: line 1396

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

Total lines: 2536

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

## Closeout

English and Korean console validation have both passed. Phase 4-6 can be closed
at the console-validation level.

Explicit missing-key fallback UI evidence has not been captured in this pass.
