# Phase 4-8 English ProtectedCall Boundary Playtest Validation

Date: 2026-05-08

Source log:

- `C:\Users\MW\Zomboid\Console.txt`
- last modified: 2026-05-08 01:36:19

Archived evidence:

- `Iris/_docs/refactor/playtest_evidence/2026-05-08-en-protected-call-boundary/console.txt`

## Result

Status: pass at the console-validation level.

The English playtest loaded the Phase 4-8 ProtectedCall boundary module and
representative migrated consumers without Iris Lua exceptions or release-mode
debug spam.

## Language And Boot Evidence

- `user.language=ko`: line 94
- `translator: language is EN`: line 323
- `[Iris] Bootstrap complete`: line 1312

The log keeps `user.language=ko`, so this follows the same in-session
translator-switch pattern as prior English validations rather than a cold
process boot with `user.language=en`.

## ProtectedCall Boundary Module Load Evidence

- `Iris/Util/IrisProtectedCall.lua`: line 1306
- `Iris/IrisMain.lua`: line 1307
- `Iris/API/Description.lua`: line 1347
- `Iris/API/Index.lua`: line 1351
- `Iris/IrisTranslationLoader.lua`: line 1379
- `Iris/UI/Browser/IrisBrowserData.lua`: line 1397
- `Iris/UI/Wiki/IrisWikiSections.lua`: line 1408

The deployed mod copy also contains the expected Phase 4-8 runtime files under
`C:\Users\MW\Zomboid\mods\Iris`:

- `media/lua/client/Iris/Util/IrisProtectedCall.lua`
- `media/lua/client/Iris/IrisMain.lua`
- `media/lua/client/Iris/IrisTranslationLoader.lua`
- `media/lua/client/Iris/API/Description.lua`
- `media/lua/client/Iris/API/Index.lua`
- `media/lua/client/Iris/UI/Browser/IrisBrowserData.lua`
- `media/lua/client/Iris/UI/Wiki/IrisWikiSections.lua`

The deployed files contain the expected boundary markers:

- `IrisProtectedCall.lua`: `local function callBoundary(boundary, fn, ...)`,
  line 30.
- `IrisProtectedCall.lua`: `callBoundary("engine"|"ui"|"data"|"compat", ...)`,
  lines 47, 51, 55, and 59.
- `IrisMain.lua`: module callback `boundary = "ui"`, `boundary = "compat"`,
  and `boundary = "data"` markers on the initialization specs.
- `IrisTranslationLoader.lua`: `ProtectedCall.engine(Translator.getLanguage)`.
- `Description.lua` and `Index.lua`: `ProtectedCall.data(...)` calls.
- `IrisBrowserData.lua`: `ProtectedCall.engine(getText, key)` and
  `ProtectedCall.data(...)` calls.
- `IrisWikiSections.lua`: `ProtectedCall.engine(...)` and
  `ProtectedCall.data(...)` calls.

## Counts

Total lines: 2535

| Pattern | Count |
|---|---:|
| `Iris` | 79 |
| `IrisProtectedCall` | 1 |
| `IrisMain` | 2 |
| `IrisTranslationLoader` | 1 |
| `Iris/API/Description` | 1 |
| `Iris/API/Index` | 1 |
| `IrisBrowserData` | 1 |
| `IrisWikiSections` | 1 |
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

None of these entries referenced Iris, IrisWiki, IrisTranslation, IrisAPI,
ProtectedCall, or Layer3.

## Closeout

English and Korean console validation have both passed. Phase 4-8 can be closed
at the console-validation level.
