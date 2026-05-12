# P5 Execution - Data Layer

Archived under `_done` by the Phase 1 v1.4 refactor doc split.

Date: 2026-05-02

## P5-1 Data File Split Decision

Measured largest runtime data files:

| file | bytes |
|---|---:|
| `IrisUseCaseDescriptions.lua` | 1,305,937 |
| `IrisLayer3Data.lua` | 1,024,287 |
| `IrisClassifications.lua` | 111,083 |
| `IrisRecipeIndexData.lua` | 78,265 |
| `IrisData.lua` | 75,143 |

Decision: do not split the large Lua data files in this pass.

Reason:

- `IrisLayer3Data.lua` is the generated bridge artifact and is referenced by many runtime validation, reflection, and regression scripts by exact path.
- `layer3_renderer.lua` currently owns the single loading boundary for `IrisLayer3Data`; splitting it would require a manifest/router redesign plus validator updates.
- `IrisUseCaseDescriptions.lua` is consumed by `IrisAPI`, Browser interaction rendering, and the new tooltip summary path. Splitting it needs a lazy router design, not only mechanical file movement.
- P6 changed UI load structure in the same session, so adding a data-router change before in-game validation would combine two high-risk runtime changes.

P5-1 status: split not adopted now. Revisit after Browser runtime validation and after P5-3/P5-4 clarify the data access boundaries.

## P5-4 ItemKey utility

Status: implemented.

- Added `Iris/Util/ItemKey.lua` as the shared Iris-only fullType extraction helper.
- Replaced duplicated `getFullType` / `getFullName` / `fullType` fallback logic in `IrisAPI`, `IrisAltTooltip`, `IrisWikiSections`, `IrisBrowserData`, `IrisBrowserListController`, and `IrisBrowser`.
- Kept the helper inside Iris to preserve the Pulse hub/spoke boundary.

## P5-3 BrowserData index split

Status: implemented.

- Added `Iris/UI/Browser/IrisBrowserItemIndex.lua` for whole-item scanning and `fullType -> item` storage.
- Added `Iris/UI/Browser/IrisBrowserClassificationIndex.lua` for static Iris tag to category/subcategory indexing.
- Kept `IrisBrowserData.lua` as the public facade that joins both indexes for existing Browser consumers.
- `searchAll()` now uses the prebuilt classification location index instead of rescanning category buckets.

## P5-2 UseCase unlabeled output

Status: implemented.

- `description_generator.py` now resolves missing `uc.recipe.*` labels from `recipe_nav_registry.v2.4.json` using translated recipe name first and original recipe name as fallback.
- Missing non-recipe labels and missing recipe nav entries now fail loud at build time.
- Added a generator-level no-unlabeled output gate and unit tests for recipe fallback and missing-label failure.

## P5-2 Unlabeled Spike

Precondition spike result:

- Current generated `IrisUseCaseDescriptions.lua` contains 791 `(unlabeled: ...)` occurrences.
- Runtime does not correct those entries.
- `IrisWikiSections.renderUseCaseLine()` uses `lineObj.display_text` first; if that text already contains `(unlabeled: ...)`, the label-map fallback is bypassed.
- `IrisUseCaseLabelMap.lua` covers common `uc.craft`, `uc.exclusion`, and action keys, but not the broad `uc.recipe.*` space that produces most unlabeled rows.

Original conclusion:

- Enabling a hard build-fail gate immediately would block the current generated artifact.
- The next P5-2 implementation must first change the generation path so recipe rows produce acceptable `display_text` from `recipe_translated_name` / `recipe_original_name`, or emit a structured missing-label report that can be drained before the hard gate is enabled.

Final outcome:

- The generation path now uses `recipe_nav_registry.v2.4.json` for missing `uc.recipe.*` labels.
- The hard no-unlabeled gate is enabled in `description_generator.py`.
- Regenerated `descriptions_by_fulltype.v2.4.json` and `IrisUseCaseDescriptions.lua` contain zero `(unlabeled: ...)` occurrences.

## Validation

Latest completed validation:

```text
python -B -m unittest discover -s Iris\build\description\v2\tests -p "test_*.py"
Ran 319 tests in 3.376s
OK
```

Additional P5-2 validation:

```text
python -B Iris\build\test_require_render.py
FINAL RESULT: ALL PASSED
```

```text
rg -n "\(unlabeled:|UNKNOWN_REQUIRE_ATOM" Iris\output\descriptions_by_fulltype.v2.4.json Iris\media\lua\client\Iris\Data\IrisUseCaseDescriptions.lua
no matches
```

Package manifest after P5:

- includes `media/lua/client/Iris/Util/ItemKey.lua`
- includes `media/lua/client/Iris/UI/Browser/IrisBrowserItemIndex.lua`
- includes `media/lua/client/Iris/UI/Browser/IrisBrowserClassificationIndex.lua`
