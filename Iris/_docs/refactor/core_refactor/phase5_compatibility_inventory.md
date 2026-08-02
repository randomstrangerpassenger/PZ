# Phase 5 compatibility inventory

Scope is limited to the supported surfaces listed in `phase0_supported_api_manifest.json`; unknown third-party mod compatibility is not claimed.

| Surface | Fresh repository callers | Dynamic/event reachability | Disposition |
|---|---:|---|---|
| `IrisBrowserData.getGroupVariants(groupId)` | 0 internal call sites; one public definition | Public module may be dynamically required by external code | Retain signature through `IrisBrowserVariantIndex` adapter. |
| `IrisData.ItemGroups` | 0 current data producers and 0 current query readers | Historical global-only callers remain possible | Isolate the read in `StaticData.getLegacyIrisData`; current query code does not read the global. Missing group data returns documented `nil`. |
| `IrisAPI.getCapabilities` / `hasCapability` | Browser interaction collector and shared detail model consume capability data | `IrisBrowser` is installed through runtime module loading | Retain the `can_*` compatibility projection unchanged. |
| Category/subcategory codes and labels | BrowserData/Filters consume CategoryIndex | Browser and map-icon open paths | CategoryIndex remains presentation projection only; Classification/Rule data remains semantic authority. |
| `IrisTooltipSummary.get` | Alt tooltip runtime hook | `IrisMain` registers the tooltip hook | Retain exact tag/connection/use-case summary behavior. |

Generated `IrisData.lua` and `IrisClassifications.lua` are not merged or manually regenerated in this change. `IrisData` remains a generated legacy alias, while all new/current reads use focused modules or the isolated compatibility loader. No runtime recommendation, priority, score, or new taxonomy inference is introduced.

Compatibility fallback matrix:

| Input state | Result |
|---|---|
| Focused/current runtime, no `ItemGroups` producer | `getGroupVariants` returns `nil` |
| Legacy global-only `IrisData.ItemGroups[groupId]` | Adapter returns sorted `{fullType, displayName}` rows |
| Missing generated `IrisData` module and no global | `StaticData` negative-caches the failure; adapter returns `nil`; `getFailureReason("legacyData")` exposes the reason |
