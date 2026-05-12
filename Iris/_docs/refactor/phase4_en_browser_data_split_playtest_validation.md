# Phase 4-3 English BrowserData Split Playtest Validation

Date: 2026-05-06

Source log:

- `C:\Users\MW\Zomboid\Console.txt`

Archived evidence:

- `Iris/_docs/refactor/playtest_evidence/2026-05-06-en-browser-data-split/console.txt`

## Result

Status: pass at the console-validation level.

The English playtest loaded the Phase 4-3 BrowserData split modules without
Iris Lua exceptions.

## Language And Boot Evidence

The log contains two boot/load sequences. Both reached English translator mode
and Iris bootstrap completion.

First sequence:

- `translator: language is EN`: line 336
- `[Iris] Bootstrap complete`: line 1325

Latest sequence:

- `translator: language is EN`: line 2717
- `[Iris] Bootstrap complete`: line 3675

The log also contains `user.language=ko` at line 107, so this is the same
in-session translator-switch pattern seen in prior English validations rather
than a cold process boot with `user.language=en`.

## BrowserData Split Module Load Evidence

First sequence:

- `IrisBrowserCategoryIndex.lua`: line 1406
- `IrisBrowserData.lua`: line 1408
- `IrisBrowserFilters.lua`: line 1409
- `IrisBrowserQuery.lua`: line 1411
- `IrisBrowserVariantIndex.lua`: line 1412

Latest sequence:

- `IrisBrowserCategoryIndex.lua`: line 3756
- `IrisBrowserData.lua`: line 3758
- `IrisBrowserFilters.lua`: line 3759
- `IrisBrowserQuery.lua`: line 3761
- `IrisBrowserVariantIndex.lua`: line 3762

The deployed mod copy also contains the new split files under
`C:\Users\MW\Zomboid\mods\Iris\media\lua\client\Iris\UI\Browser`.

## Counts

Total lines: 3839

| Pattern | Count |
|---|---:|
| `Iris` | 152 |
| `IrisBrowserData` | 2 |
| `IrisBrowserCategoryIndex` | 2 |
| `IrisBrowserFilters` | 2 |
| `IrisBrowserQuery` | 2 |
| `IrisBrowserVariantIndex` | 2 |
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
- One Pulse `LuaAdapter` save/event error.
- Vanilla/mod recipe, sound, model, vehicle, moveables, and
  `SuburbsDistributions["laboratory"]` warnings/errors.
- Missing optional require warnings such as `ISTimer` and CheatMenuRebirth
  modules.

None of these entries referenced Iris, IrisBrowser, or IrisAPI.

## Remaining QA

Korean console validation is still required before Phase 4-3 can be closed at
the console-validation level.

Screenshot-level UI evidence for category/list/detail/search behavior remains
optional supporting evidence.
