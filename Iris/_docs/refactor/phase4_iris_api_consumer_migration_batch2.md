# Phase 4-2 IrisAPI Consumer Migration Batch 2

Date: 2026-05-06

Status: implemented, static checks complete, English and Korean console
validation pass. Runtime batch 2 is closed at the console-validation level.

## Scope

This batch follows `phase4_iris_api_split_batch1.md`.

It migrates internal runtime consumers from legacy top-level `IrisAPI.*`
function calls to the new sub-facade surface exposed by `require("Iris/IrisAPI")`.

Direct imports such as `require("Iris/API/Description")` were not added.

## Runtime Files Changed

- `Iris/media/lua/client/Iris/UI/Browser/IrisBrowserData.lua`
- `Iris/media/lua/client/Iris/UI/Browser/IrisBrowserDetail.lua`
- `Iris/media/lua/client/Iris/UI/Browser/IrisBrowserInteractionRenderer.lua`
- `Iris/media/lua/client/Iris/UI/Wiki/IrisWikiSections.lua`

## Mapping Applied

| Consumer call | New internal call |
|---|---|
| `IrisAPI.getTagsForItem(...)` | `IrisAPI.Tags.getTagsForItem(...)` |
| `IrisAPI.getRecipeConnectionsForItem(...)` | `IrisAPI.Index.getRecipeConnectionsForItem(...)` |
| `IrisAPI.getMoveablesInfoForItem(...)` | `IrisAPI.Index.getMoveablesInfoForItem(...)` |
| `IrisAPI.getFixingInfoForItem(...)` | `IrisAPI.Index.getFixingInfoForItem(...)` |
| `IrisAPI.getDescription(...)` | `IrisAPI.Description.getDescription(...)` |
| `IrisAPI.getUseCaseLines(...)` | `IrisAPI.UseCases.getUseCaseLines(...)` |
| `IrisAPI.getCapabilities(...)` | `IrisAPI.UseCases.getCapabilities(...)` |

## Compatibility

`Iris/media/lua/client/Iris/IrisAPI.lua` still keeps all legacy top-level
functions for external callers and older internal paths.

This batch only changes first-party consumer call sites to exercise the
sub-facade ownership boundary.

## Test Contract Update

Updated:

- `Iris/build/description/v2/tests/test_interaction_cluster_phase_d_runtime.py`

Reason:

- The runtime consumer marker changed from `IrisAPI.getDescription` to
  `IrisAPI.Description.getDescription`.
- The ordering contract remains the same: Browser description output must still
  precede `renderLayer3Section(item)`.

## Static Checks

Performed:

- `git diff --check` for changed runtime consumer files.
- Verified no first-party UI consumer keeps legacy top-level `IrisAPI.get*`
  calls.
- Verified first-party UI consumers now call `IrisAPI.Tags`, `IrisAPI.Index`,
  `IrisAPI.Description`, and `IrisAPI.UseCases`.
- `python -B -m unittest discover -s Iris\build\description\v2\tests -p "test_*.py"`
  passed: `319 tests / OK`.

Still not performed:

- Lua bytecode/syntax compile check. No `lua` or `luac` executable is available
  in the current environment.
- Screenshot-level UI evidence for tooltip, browser detail, recipe requirement,
  and right-click capability surfaces. Console validation did not expose
  per-interaction markers.

Runtime validation recorded:

- Korean API consumer migration playtest:
  `Iris/_docs/refactor/phase4_ko_api_consumer_migration_playtest_validation.md`
- English API consumer migration playtest:
  `Iris/_docs/refactor/phase4_en_api_consumer_migration_playtest_validation.md`

## QA Required

The Phase 4 manual checklist has console validation coverage for EN and KO.
Preserve screenshot/user-observed notes separately if a future release package
needs visual evidence for:

- Iris boot without Lua exceptions.
- Browser open/search/category/list/detail.
- Layer 3 description blocks.
- Recipe requirement and right-click capability surfaces.
- Release/dev log behavior.
