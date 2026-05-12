# Phase 4-2 IrisAPI Layer Mapping

Status: pre-implementation artifact for Phase 4-2.

Date: 2026-05-06

Scope:

- Target runtime file: `Iris/media/lua/client/Iris/IrisAPI.lua`
- Planned split namespace: `IrisAPI.Tags`, `IrisAPI.Index`, `IrisAPI.Description`, `IrisAPI.UseCases`
- This document does not change runtime behavior.

## Boundary Rule

`ARCHITECTURE.md` fixes the runtime boundary as:

- Core: classification and frozen fact lookup.
- Description: presentation composition and description block generation.
- Browser: search, navigation, sorting, visibility, and UI display policy.

Phase 4-2 must preserve this rule:

> Classification belongs to Core, expression belongs to Description, display policy belongs to Browser.

`IrisAPI.lua` is therefore not a new ownership layer. It remains a compatibility facade over smaller query facades.

## Module Mapping

| Planned facade | Architecture layer | Responsibility | Explicit non-responsibility |
|---|---|---|---|
| `IrisAPI.Tags` | Core facade | Read frozen item classification tags from `IrisClassifications`; expose tag arrays, tag sets, and simple membership checks. | Does not sort for UI, translate tags, infer missing tags, or explain what a tag means. |
| `IrisAPI.Index` | Core index facade | Read frozen static indexes: recipe roles, moveables registration, fixing/fixer metadata. Return raw normalized lookup results. | Does not turn recipe roles into recommendations, prose, section order, or Browser navigation policy. |
| `IrisAPI.Description` | Description facade | Load `IrisDesc/Generator`, request tags as immutable input, and return Layer 3 description blocks or joined text. | Does not re-check evidence, correct tags, create classifications, filter rendered text, or own Browser layout behavior. |
| `IrisAPI.UseCases` | Core fact facade with sealed display-payload passthrough | Read frozen use-case/outcome/capability artifacts: `IrisUseCaseDescriptions`, `IrisContextOutcomes`, `IrisCapabilities`. Return static facts and prebuilt use-case lines. | Does not generate new runtime prose, interpret right-click actions, rank usefulness, or merge use-case lines into Layer 3 description blocks. |

## Ambiguity Resolution

`UseCases` is the only ambiguous candidate because it exposes both fact-like data (`getOutcomes`, `getCapabilities`) and prebuilt line payloads (`getUseCaseLines`).

The adopted split is:

- `IrisAPI.UseCases` owns the use-case surface because the returned values are frozen build artifacts.
- `getUseCaseLines()` is a passthrough of sealed display payload, not runtime description composition.
- Runtime text composition remains in `IrisAPI.Description`.
- Browser/Wiki consumers may display use-case payloads, but they do not become the owner of the fact contract.

This keeps the 4-module split without introducing a fifth public facade.

## Public Surface Allocation

| Current public function | Target facade | Contract after split |
|---|---|---|
| `getTagsForItem(item)` | `IrisAPI.Tags` | Core tag set lookup by item fullType. |
| `getTags(fullType)` | `IrisAPI.Tags` | Core tag array lookup by fullType. |
| `hasTag(fullType, tag)` | `IrisAPI.Tags` | Membership check over frozen tag array. |
| `isClassified(fullType)` | `IrisAPI.Tags` | True when frozen tag array is non-empty. |
| `getRecipeConnectionsForItem(item)` | `IrisAPI.Index` | Raw recipe role/category lookup. |
| `getMoveablesInfoForItem(item)` | `IrisAPI.Index` | Raw moveables registration/tag lookup. |
| `getFixingInfoForItem(item)` | `IrisAPI.Index` | Raw fixer lookup. |
| `getDescriptionBlocks(fullType, primarySubcategory)` | `IrisAPI.Description` | Runtime description block generation from frozen tags and generator templates. |
| `getDescription(fullType, primarySubcategory)` | `IrisAPI.Description` | Joined text form of generated description blocks. |
| `getDescriptionForItem(item, primarySubcategory)` | `IrisAPI.Description` | Item convenience wrapper around `getDescription`. |
| `getUseCaseLines(fullType)` | `IrisAPI.UseCases` | Static use-case line payload passthrough. |
| `getOutcomes(fullType)` | `IrisAPI.UseCases` | Static context outcome lookup. |
| `hasOutcome(fullType, outcome)` | `IrisAPI.UseCases` | Membership check over static context outcomes. |
| `getCapabilities(fullType)` | `IrisAPI.UseCases` | Static right-click capability lookup. |
| `hasCapability(fullType, capability)` | `IrisAPI.UseCases` | Membership check over static capabilities. |

## Consumer Mapping

| Consumer | Current calls | Target dependency after migration |
|---|---|---|
| `Iris/UI/Browser/IrisBrowserData.lua` | `getTagsForItem`, `getRecipeConnectionsForItem` | `Tags`, `Index` through compatibility facade first; direct sub-facade use only after QA. |
| `Iris/UI/Wiki/IrisWikiSections.lua` | `getTagsForItem`, `getRecipeConnectionsForItem`, `getMoveablesInfoForItem`, `getFixingInfoForItem`, `getUseCaseLines` | `Tags`, `Index`, `UseCases` through compatibility facade first. |
| `Iris/UI/Browser/IrisBrowserDetail.lua` | `getDescription` | `Description` through compatibility facade first. |
| `Iris/UI/Browser/IrisBrowserInteractionRenderer.lua` | `getRecipeConnectionsForItem`, `getCapabilities` | `Index`, `UseCases` through compatibility facade first. |
| `IrisMain.lua` | loads `Iris/IrisAPI` | Keep loading the compatibility facade. |

## Implementation Shape

Recommended runtime file layout:

- `Iris/media/lua/client/Iris/API/StaticData.lua`
- `Iris/media/lua/client/Iris/API/Tags.lua`
- `Iris/media/lua/client/Iris/API/Index.lua`
- `Iris/media/lua/client/Iris/API/Description.lua`
- `Iris/media/lua/client/Iris/API/UseCases.lua`
- `Iris/media/lua/client/Iris/IrisAPI.lua`

`StaticData.lua` is not a public facade. It is the private table-driven loader replacing the current repeated `ensureData()` pattern.

`IrisAPI.lua` remains the public compatibility facade:

- exposes `IrisAPI.Tags`, `IrisAPI.Index`, `IrisAPI.Description`, `IrisAPI.UseCases`;
- keeps all existing top-level function names;
- delegates each top-level function to the matching sub-facade;
- avoids changing external Lua API surface in the first runtime batch.

## Migration Rules

1. Add sub-facades and keep `IrisAPI.lua` as the only required public entrypoint in the first code batch.
2. Do not migrate Browser/Wiki consumers to direct sub-facade imports in the same batch.
3. Do not change `IrisLayer3Data.lua`, Browser splitting, translation loading, or ProtectedCall boundary policy in this batch.
4. Keep recipe, right-click, context outcome, and capability data as frozen build/runtime artifacts; do not add runtime interpretation.
5. Gate the verbose `getDescriptionBlocks()` trace logs behind a dev flag during the `Description` extraction batch.
6. After Lua syntax/load smoke passes, rerun the Phase 4 manual QA checklist for KO and EN surfaces.

## Compatibility Window

The first Phase 4-2 runtime batch must support both:

- existing consumers that call `require("Iris/IrisAPI").getDescription(...)`;
- new internal calls that may call `require("Iris/IrisAPI").Description.getDescription(...)`.

Direct imports such as `require("Iris/API/Description")` should remain internal until one successful manual QA round confirms that the compatibility facade and sub-facades return identical results.

## Non-goals

- No public function removal.
- No output text rewrite.
- No classification or evidence rule changes.
- No Browser sorting/search/list policy changes.
- No `IrisLayer3Data.lua` chunking.
- No ProtectedCall boundary policy migration.
- No external mod input contract change without a separate deprecation plan.

