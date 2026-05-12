# Phase 4-5 English Browser Common Base Playtest Validation

Date: 2026-05-06

Source log:

- `C:\Users\MW\Zomboid\Console.txt`

Archived evidence:

- `Iris/_docs/refactor/playtest_evidence/2026-05-06-en-browser-common-base/console.txt`

Prior invalid attempt evidence:

- `Iris/_docs/refactor/playtest_evidence/2026-05-06-en-browser-common-base-invalid/console.txt`

## Result

Status: pass at the console-validation level.

The English playtest loaded the Phase 4-5 Browser common base module and Browser
consumer modules without Iris Lua exceptions.

## Language And Boot Evidence

- `user.language=ko`: line 67
- `translator: language is EN`: line 296
- `[Iris] Bootstrap complete`: line 1285

The log keeps `user.language=ko`, so this follows the same in-session
translator-switch pattern as prior English validations rather than a cold
process boot with `user.language=en`.

## Browser Common Base Module Load Evidence

- `Iris/UI/Browser/IrisBrowser.lua`: line 1360
- `Iris/UI/Browser/IrisBrowserBase.lua`: line 1361
- `Iris/UI/Browser/IrisBrowserListController.lua`: line 1362
- `Iris/UI/Browser/IrisBrowserDetail.lua`: line 1364

The deployed mod copy also contains the expected Phase 4-5 Browser runtime files
under `C:\Users\MW\Zomboid\mods\Iris`:

- `media/lua/client/Iris/UI/Browser/IrisBrowserBase.lua`
- `media/lua/client/Iris/UI/Browser/IrisBrowser.lua`
- `media/lua/client/Iris/UI/Browser/IrisBrowserListController.lua`
- `media/lua/client/Iris/UI/Browser/IrisBrowserDetail.lua`

The deployed `IrisBrowser.lua` contains the Phase 4-5 common base calls:

- `require("Iris/UI/Browser/IrisBrowserBase")`
- `BrowserBase.ensureBrowserDataBuilt(...)`
- `BrowserBase.closeVisibleInstance(...)`
- `BrowserBase.createCenteredPanel(...)`

## Counts

Total lines: 2532

| Pattern | Count |
|---|---:|
| `Iris` | 78 |
| `IrisBrowserBase` | 1 |
| `IrisBrowser.lua` | 1 |
| `IrisBrowserListController` | 1 |
| `IrisBrowserDetail` | 1 |
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

None of these entries referenced Iris, IrisBrowser, IrisTranslation, or IrisAPI.

## Prior Invalid Attempt

An earlier English attempt was rejected because the deployed mod copy was
missing `IrisBrowserBase.lua` and still had the pre-batch inline panel sizing
logic in `IrisBrowser.lua`. The current pass supersedes that attempt.

## Remaining QA

Korean console validation is still required before Phase 4-5 can be closed at
the console-validation level.

Screenshot-level Browser layout evidence remains optional supporting evidence.
