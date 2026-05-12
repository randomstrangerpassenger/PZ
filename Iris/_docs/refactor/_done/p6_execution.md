# P6 Execution - Browser UI Split

Archived under `_done` by the Phase 1 v1.4 refactor doc split.

Date: 2026-05-02

## P6-1 Browser Split

Decision at start:

- Target `IrisBrowser.lua` entrypoint line count: <= 350 physical lines.
- Keep `IrisBrowser.lua` responsible for lifecycle, singleton state, dependency accessors, and module installation only.
- Move UI behavior into independently require-able modules that return tables.

Result:

- `Iris/media/lua/client/Iris/UI/Browser/IrisBrowser.lua`: 194 lines
- `IrisBrowserLayout.lua`: layout/widget construction
- `IrisBrowserDetail.lua`: detail panel rendering and scrolling
- `IrisBrowserInteractionRenderer.lua`: interaction/usecase rendering
- `IrisBrowserRecipeNav.lua`: crafting UI navigation
- `IrisBrowserListController.lua`: category/subcategory/item list, search, and selection behavior

The phase D runtime validator and its test now aggregate `IrisBrowser*.lua` sibling files when checking Browser runtime consumers. This preserves the old validation intent after the Browser split.

## P6-2 Select Reverse Index

- Added `itemLocationsByFullType` to `IrisBrowserData` cache.
- Added `IrisBrowserData.getItemLocation(fullType)`.
- Replaced `selectItem()` category/subcategory full scan with the reverse-index lookup.
- Left `searchAll()` classification scan unchanged; broader item/classification index separation remains P5-3 scope.

## P6-3 WikiPanel Fallback

Decision: keep `IrisWikiPanel.lua` for now.

Reason:

- `IrisContextMenu` still uses `IrisWikiPanel.openForItem()` as a fail-soft fallback if Browser loading fails.
- P6 just changed Browser load structure, so removing the fallback before in-game validation would reduce recovery behavior without removing a current runtime dependency.

## P6-4 Tooltip Summary

- Added `Iris/UI/Tooltip/IrisTooltipSummary.lua`.
- Tooltip summary is keyed by `fullType` and cached after first read.
- Summary is built from precompiled Iris data tables:
  - `IrisClassifications`
  - `IrisRecipeIndex`
  - `IrisMoveablesIndex`
  - `IrisFixingIndex`
  - `IrisUseCaseDescriptions`
- `IrisAltTooltip.lua` now consumes that summary and no longer calls item-based IrisAPI lookup functions during tooltip rendering.

## Validation

Static test suite:

```text
python -B -m unittest discover -s Iris\build\description\v2\tests -p "test_*.py"
Ran 315 tests in 3.686s
OK
```

Packaging:

```text
.\Iris\tools\package_iris.ps1 -Clean
Iris package staged: C:\Users\MW\Downloads\coding\PZ\Iris\build\package\Iris
Manifest written: C:\Users\MW\Downloads\coding\PZ\Iris\build\package\Iris.package_manifest.sha256.json
```

Package manifest:

- `file_count`: 48
- forbidden package roots: none
- new Browser split modules included
- `IrisTooltipSummary.lua` included

Translation regression scans:

```text
rg -n 'TRANSLATIONS_KO|getCurrentLanguage\(|return "KO"|\\[0-9]{3}' Iris\media\lua\client\Iris\UI
no results

rg -n '\x22[^\x22]*[가-힣][^\x22]*\x22' Iris\media\lua\client\Iris\UI
no results

rg -n "\x27[^\x27]*[가-힣][^\x27]*\x27" Iris\media\lua\client\Iris\UI
no results
```

Local shell note:

- `lua` / `luac` are not installed in this environment, so Lua parser validation could not be run locally.
- Because P6 changed UI load structure, the next runtime check should open the Browser from both the Iris map icon and inventory context menu.
