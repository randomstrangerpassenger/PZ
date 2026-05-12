# Phase 4-3 Korean BrowserData Split Playtest Validation

Date: 2026-05-06

Source log:

- `C:\Users\MW\Zomboid\Console.txt`

Archived evidence:

- `Iris/_docs/refactor/playtest_evidence/2026-05-06-ko-browser-data-split/console.txt`

## Result

Status: pass at the console-validation level.

The Korean playtest loaded the Phase 4-3 BrowserData split modules without Iris
Lua exceptions.

## Language And Boot Evidence

- `user.language=ko`: line 49
- `translator: language is KO`: line 277
- `[Iris] Bootstrap complete`: line 1266

## BrowserData Split Module Load Evidence

- `IrisBrowserCategoryIndex.lua`: line 1347
- `IrisBrowserData.lua`: line 1349
- `IrisBrowserFilters.lua`: line 1350
- `IrisBrowserQuery.lua`: line 1352
- `IrisBrowserVariantIndex.lua`: line 1353

The deployed mod copy also contains the new split files under
`C:\Users\MW\Zomboid\mods\Iris\media\lua\client\Iris\UI\Browser`.

## Counts

Total lines: 2522

| Pattern | Count |
|---|---:|
| `Iris` | 76 |
| `IrisBrowserData` | 1 |
| `IrisBrowserCategoryIndex` | 1 |
| `IrisBrowserFilters` | 1 |
| `IrisBrowserQuery` | 1 |
| `IrisBrowserVariantIndex` | 1 |
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
- Vanilla/mod recipe, sound, model, vehicle, moveables, mannequin, and
  `SuburbsDistributions["laboratory"]` warnings/errors.
- Missing optional require warnings such as `ISTimer` and CheatMenuRebirth
  modules.

None of these entries referenced Iris, IrisBrowser, or IrisAPI.

## Closeout

English and Korean console validation have both passed. Phase 4-3 can be closed
at the console-validation level.

Screenshot-level UI evidence for category/list/detail/search behavior remains
optional supporting evidence.
