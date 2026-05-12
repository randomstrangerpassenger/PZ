# Phase 4-2 IrisAPI Split Batch 1

Date: 2026-05-06

Status: implemented, static checks complete, English and Korean console
validation pass. Runtime batch 1 is closed at the console-validation level.

## Scope

This batch implements the first `IrisAPI.lua` responsibility split using the
mapping in `phase4_iris_api_layer_mapping.md`.

Runtime files added:

- `Iris/media/lua/client/Iris/API/StaticData.lua`
- `Iris/media/lua/client/Iris/API/Tags.lua`
- `Iris/media/lua/client/Iris/API/Index.lua`
- `Iris/media/lua/client/Iris/API/Description.lua`
- `Iris/media/lua/client/Iris/API/UseCases.lua`

Runtime file changed:

- `Iris/media/lua/client/Iris/IrisAPI.lua`

## Implemented Boundary

- `IrisAPI.Tags` owns classification tag lookup.
- `IrisAPI.Index` owns recipe, moveables, and fixing index lookup.
- `IrisAPI.Description` owns description block/text generation through
  `IrisDesc/Generator`.
- `IrisAPI.UseCases` owns frozen use-case, context outcome, and capability
  artifact lookup.
- `IrisAPI.lua` remains the public compatibility facade and keeps all existing
  top-level function names.

## Compatibility

Existing consumers can continue to use:

```lua
local IrisAPI = require("Iris/IrisAPI")
IrisAPI.getDescription(fullType, primarySubcategory)
```

The same facade now also exposes sub-facades:

```lua
IrisAPI.Tags
IrisAPI.Index
IrisAPI.Description
IrisAPI.UseCases
```

Browser/Wiki consumer imports were not migrated in this batch.

## Log Behavior

The verbose `getDescriptionBlocks()` trace path is now guarded by
`IrisConfig.DEBUG == true` before building the detailed debug messages.

Generator load failure keeps the prior warning-level behavior. Runtime
generation failures still use the existing error log path.

## Static Checks

Performed:

- `git diff --check` for the changed Phase 4-2 files.
- Verified all existing top-level `IrisAPI.*` public functions remain present.
- Verified each planned sub-facade exports the expected functions.
- `python -B -m unittest discover -s Iris\build\description\v2\tests -p "test_*.py"`
  passed: `319 tests / OK`.

Runtime validation recorded:

- English API split playtest:
  `Iris/_docs/refactor/phase4_en_api_split_playtest_validation.md`
- Korean API split playtest:
  `Iris/_docs/refactor/phase4_ko_api_split_playtest_validation.md`

Still not performed:

- Lua bytecode/syntax compile check. No `lua` or `luac` executable is available
  in the current environment.
- Screenshot-level UI evidence for tooltip, browser detail, recipe requirement,
  and right-click capability surfaces. Console validation did not expose
  per-interaction markers.

## Manual QA Required

The Phase 4 manual checklist in `phase4_manual_qa.md` has console validation
coverage for EN and KO. Preserve screenshot/user-observed notes separately if a
future release package needs visual evidence for:

- Iris boot without Lua exceptions.
- Alt tooltip.
- Right-click "Iris 메뉴에서 더보기".
- Browser open/search/category/list/detail.
- Layer 3 description blocks.
- Recipe requirement and right-click capability surfaces.
- KO/EN fallback.
- Release/dev log behavior.
