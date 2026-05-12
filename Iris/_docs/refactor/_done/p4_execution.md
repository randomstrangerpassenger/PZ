# P4 Execution - Translation Source Consolidation

Archived under `_done` by the Phase 1 v1.4 refactor doc split.

Date: 2026-05-02

## Completed

- Moved Browser-local KO translation data into `IrisTranslationLoader`.
- Removed duplicated Browser/BrowserData language selection helpers.
- Routed Browser, BrowserData, Tooltip, and ContextMenu display strings through `IrisTranslationLoader.get()`.
- Removed the hardcoded Browser locale result (`return "KO"`).
- Added translation keys for Browser action labels, tooltip labels, category/subcategory labels, and requirement replacement text.
- Removed the remaining hardcoded Korean UI error label from Browser detail rendering.

The translation resource is now the allowed location for byte-escaped KO strings. UI logic keeps only translation keys plus English fallback text.

## Central Accessor

Runtime UI modules now use `IrisTranslationLoader` as the shared translation source:

- `Iris/media/lua/client/Iris/UI/Browser/IrisBrowser.lua`
- `Iris/media/lua/client/Iris/UI/Browser/IrisBrowserData.lua`
- `Iris/media/lua/client/Iris/UI/Tooltip/IrisAltTooltip.lua`
- `Iris/media/lua/client/Iris/UI/Wiki/IrisContextMenu.lua`
- Existing Wiki section translation lookup remains routed through `IrisTranslationLoader`.

## Validation

Static translation scan:

```text
rg -n 'TRANSLATIONS_KO|getCurrentLanguage\(|return "KO"|\\[0-9]{3}' Iris\media\lua\client\Iris\UI
no results

rg -n '\x22[^\x22]*[가-힣][^\x22]*\x22' Iris\media\lua\client\Iris\UI
no results

rg -n "\x27[^\x27]*[가-힣][^\x27]*\x27" Iris\media\lua\client\Iris\UI
no results
```

Static test suite:

```text
python -B -m unittest discover -s Iris\build\description\v2\tests -p "test_*.py"
Ran 315 tests in 3.631s
OK
```

Packaging:

```text
.\Iris\tools\package_iris.ps1 -Clean
Iris package staged: C:\Users\MW\Downloads\coding\PZ\Iris\build\package\Iris
Manifest written: C:\Users\MW\Downloads\coding\PZ\Iris\build\package\Iris.package_manifest.sha256.json
```

Package manifest:

- `file_count`: 42
- forbidden package roots: none
