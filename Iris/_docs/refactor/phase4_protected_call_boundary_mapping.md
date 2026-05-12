# Phase 4-8 ProtectedCall Boundary Mapping

Date: 2026-05-08

Status: active for Phase 4-8

## Boundary Criteria

`ProtectedCall.call(...)` is the raw legacy primitive. Runtime call sites should
use one of the explicit boundary wrappers:

| Wrapper | Use for | Failure mode |
|---|---|---|
| `ProtectedCall.engine(...)` | PZ engine globals, Java/userdata methods, item identity/display access, translation globals, player/perk checks | Return `false, err`; emit dev-only boundary diagnostic when `IrisConfig.DEBUG == true`. |
| `ProtectedCall.ui(...)` | UI panel/window methods, UI manager calls, crafting UI navigation, UI child enumeration | Return `false, err`; emit dev-only boundary diagnostic when `IrisConfig.DEBUG == true`. |
| `ProtectedCall.data(...)` | Iris static data/index/API lookups, Layer 3 data access, description/use-case generation | Return `false, err`; emit dev-only boundary diagnostic when `IrisConfig.DEBUG == true`. |
| `ProtectedCall.compat(...)` | Compatibility monkey patches and calls made inside compatibility shims | Return `false, err`; emit dev-only boundary diagnostic when `IrisConfig.DEBUG == true`. |

Release mode behavior is intentionally quiet. The wrappers preserve the prior
`pcall` return shape, so existing fallback code keeps control over user-facing
behavior.

## Migration Table

| Runtime surface | Boundary |
|---|---|
| `Iris/Compat/IrisBulletReloadCompat.lua` safe method invocation | `compat` |
| `Iris/IrisMain.lua` module lifecycle callbacks | function spec: `ProtectedCall.ui`, `ProtectedCall.data`, or `ProtectedCall.compat` |
| `Iris/IrisMain.lua` startup test execution | `data` |
| `Iris/IrisTranslationLoader.lua` `Translator.getLanguage` | `engine` |
| `Iris/API/Description.lua` generator execution | `data` |
| `Iris/API/Index.lua` recipe/moveables/fixing index reads | `data` |
| `Iris/Data/layer3_renderer.lua` Layer 3 table reads | `data` |
| `Iris/Util/ItemKey.lua` item fulltype/fullname/field access | `engine` |
| `Iris/UI/Tooltip/IrisTooltipSummary.lua` precompiled index reads | `data` |
| `Iris/UI/Wiki/IrisContextMenu.lua` stack/list item resolution | `engine` |
| `Iris/UI/Wiki/IrisWikiPanel.lua` item display-name access | `engine` |
| `Iris/UI/Wiki/IrisWikiSections.lua` item methods and module-name access | `engine` |
| `Iris/UI/Wiki/IrisWikiSections.lua` Iris API/index reads | `data` |
| `Iris/UI/Browser/IrisBrowser.lua` PZ `getText` fallback | `engine` |
| `Iris/UI/Browser/IrisBrowserData.lua` PZ `getText` fallback | `engine` |
| `Iris/UI/Browser/IrisBrowserData.lua` Iris tag lookup | `data` |
| `Iris/UI/Browser/IrisBrowserDetail.lua` detail-panel child enumeration | `ui` |
| `Iris/UI/Browser/IrisBrowserDetail.lua` item display-name access | `engine` |
| `Iris/UI/Browser/IrisBrowserDetail.lua` Iris description lookup | `data` |
| `Iris/UI/Browser/IrisBrowserInteractionRenderer.lua` recipe/use-case lookups | `data` |
| `Iris/UI/Browser/IrisBrowserInteractionRenderer.lua` PZ recipe-name translation | `engine` |
| `Iris/UI/Browser/IrisBrowserItemIndex.lua` PZ item list scan | `engine` |
| `Iris/UI/Browser/IrisBrowserRecipeNav.lua` crafting UI navigation | `ui` |
| `Iris/UI/Browser/IrisBrowserQuery.lua` item display-name access | `engine` |
| `Iris/UI/Browser/IrisBrowserVariantIndex.lua` item method access | `engine` |
| `Iris/UI/Browser/IrisBrowserVariantIndex.lua` Iris API/index reads | `data` |
| `Iris/UI/Browser/IrisMapIcon.lua` UI manager cleanup | `ui` |
| `Iris/UI/Browser/IrisRequirementPolicy.lua` player/perk checks | `engine` |

## QA Checklist

Before closing Phase 4-8:

- Static test confirms no runtime call site still uses `ProtectedCall.call(...)`.
- Static test confirms all boundary wrappers exist and dev-only diagnostics are
  gated by `IrisConfig.DEBUG`.
- Korean and English playtests confirm Iris bootstrap and Browser/Wiki/tooltip
  surfaces still load without Iris Lua exceptions.
- Release-mode console stays quiet: no `[Iris][DEBUG]` entries unless
  `IrisConfig.DEBUG` is explicitly enabled.
