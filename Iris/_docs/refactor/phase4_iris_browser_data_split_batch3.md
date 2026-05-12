# Phase 4-3 IrisBrowserData Split Batch 3

Date: 2026-05-06

Status: implemented, static checks complete, English and Korean console
validation pass. Runtime batch 3 is closed at the console-validation level.

## Scope

This batch follows `phase4_iris_api_consumer_migration_batch2.md`.

It keeps the public `IrisBrowserData` facade stable while moving BrowserData
internals into focused Browser modules:

- `IrisBrowserCategoryIndex`
- `IrisBrowserFilters`
- `IrisBrowserQuery`
- `IrisBrowserVariantIndex`

The existing first-party call surface remains:

- `IrisBrowserData.build()`
- `IrisBrowserData.getCategories()`
- `IrisBrowserData.getSubcategories(categoryName)`
- `IrisBrowserData.getItems(categoryName, subcategoryName)`
- `IrisBrowserData.searchAll(query)`
- `IrisBrowserData.getItem(fullType)`
- `IrisBrowserData.getItemLocation(fullType)`
- `IrisBrowserData.getGroupVariants(groupId)`
- `IrisBrowserData.getCategoryLabel(catName)`
- `IrisBrowserData.getSubcategoryLabel(subCode)`

## Runtime Files Changed

- `Iris/media/lua/client/Iris/UI/Browser/IrisBrowserData.lua`
- `Iris/media/lua/client/Iris/UI/Browser/IrisBrowserCategoryIndex.lua`
- `Iris/media/lua/client/Iris/UI/Browser/IrisBrowserFilters.lua`
- `Iris/media/lua/client/Iris/UI/Browser/IrisBrowserQuery.lua`
- `Iris/media/lua/client/Iris/UI/Browser/IrisBrowserVariantIndex.lua`

## Responsibility Mapping

| Module | Responsibility |
|---|---|
| `IrisBrowserData` | Compatibility facade, cache lifecycle, item/classification build wiring |
| `IrisBrowserCategoryIndex` | Canonical category/subcategory metadata and label lookup |
| `IrisBrowserFilters` | Category and subcategory display projections |
| `IrisBrowserQuery` | Search, item lookup, browser location lookup, group variant lookup |
| `IrisBrowserVariantIndex` | DisplayName folding, fold guard, primary-subcategory calculation |

## Category Metadata Change

`CATEGORY_ORDER`, `CATEGORY_KEYS`, and `SUBCATEGORY_MAP` are now derived from
one `CATEGORY_DEFINITIONS` table in `IrisBrowserCategoryIndex`.

`IrisBrowserData` still exposes the legacy tables for compatibility.

## Behavior Contract

This batch is intended to preserve Browser behavior:

- BrowserData remains a one-time cache built from `getAllItems()`.
- Classification still uses precomputed Iris tags through `IrisAPI.Tags`.
- Recipe fold guards still use `IrisAPI.Index.getRecipeConnectionsForItem`.
- Search still matches `displayName` and `fullType`.
- Item list sorting still keeps primary subcategory entries first, then
  `displayName`, then `fullType`.

No direct consumer import of the new modules is required.

## Test Contract Update

Updated:

- `Iris/build/description/v2/tests/test_interaction_cluster_phase_d_runtime.py`

Reason:

- The runtime Browser text contract now checks that the new BrowserData split
  modules are present in the Browser module set.

## Static Checks

Performed:

- `git diff --check` for changed runtime Browser files and the updated test.
- Verified removed legacy `print(...)`/`pcall(...)` paths from the changed
  BrowserData split files.
- Verified no legacy top-level `IrisAPI.getTagsForItem` or
  `IrisAPI.getRecipeConnectionsForItem` calls remain in the changed BrowserData
  split files.
- `python -B -m unittest discover -s Iris\build\description\v2\tests -p "test_*.py"`
  passed: `319 tests / OK`.

Still not performed:

- Lua bytecode/syntax compile check. No `lua` or `luac` executable is available
  in the current environment.
- Screenshot-level UI evidence for browser category/list/detail/search flows.

Runtime validation recorded:

- English BrowserData split playtest:
  `Iris/_docs/refactor/phase4_en_browser_data_split_playtest_validation.md`
- Korean BrowserData split playtest:
  `Iris/_docs/refactor/phase4_ko_browser_data_split_playtest_validation.md`

## QA Result

Korean and English playtests validated `Console.txt` for:

- Iris bootstrap completion.
- `Iris/UI/Browser/IrisBrowserData.lua` loaded.
- `Iris/UI/Browser/IrisBrowserCategoryIndex.lua` loaded.
- `Iris/UI/Browser/IrisBrowserFilters.lua` loaded.
- `Iris/UI/Browser/IrisBrowserQuery.lua` loaded.
- `Iris/UI/Browser/IrisBrowserVariantIndex.lua` loaded.
- No `Lua error`, `stack traceback`, `ExceptionLogger`, `attempt to`, or
  `nil value` from Iris.
- Browser category/list/detail/search flows still usable in-game.

This batch is closed at the console-validation level. Preserve screenshot or
user-observed notes separately if a future release package needs visual
evidence for Browser category/list/detail/search behavior.
