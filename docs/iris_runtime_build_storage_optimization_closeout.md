# Iris runtime/build/storage optimization closeout

Date: 2026-09-16

Subject: `iris-runtime-build-storage-optimization-2026-09-16`

Overall state: **complete**

Walkthrough: [iris_runtime_build_storage_optimization_walkthrough.md](iris_runtime_build_storage_optimization_walkthrough.md)

This record closes the implementation scope of [the plan](iris_lightweighting_implementation_plan.md). It is not a replacement for the historical repository-lightweighting terminal closeout, a new validation authority, a current-product adoption, or a release record. The repository already contained unrelated dirty and untracked work; that work and the protected historical/adoption records were preserved.

## Disposition

| Change | Result | Direct outcome |
| --- | --- | --- |
| 1. Inputs and metrics | complete | Current dirty-tree inputs, generated Lua sizes, Git object state, LFS-backed large files, effective attributes, and selected validation boundaries were recorded before mutation. |
| 2. Archive feasibility | investigation complete; no move | Two untracked acquisition payloads totaling 112,336,280 bytes were copied into the existing CAS flow, verified, and restored with logical-tree parity. They produced two unique objects, so exact duplicate elimination was 0 bytes. The compressed archive was 17,557,685 bytes, but the originals were retained and no active reader migration was established; repository savings are therefore 0 bytes and no source was moved or deleted. |
| 3. EvolvedRecipe sharing | adopted in source/runtime artifact | Exact condition arrays and exact bilingual label/action/display pairs are deterministically interned. Relation records, ordering, owner identity, and public lookup shape remain intact. Browser projection copies the condition array at the UI-owned mutation boundary. |
| 4. Tooltip base/variant sharing | adopted in source/runtime artifact | `IrisTooltipRecipeVariants.lua` refers to the loaded StaticData base and reuses equal base rows while retaining complete final KO/EN arrays. A compact bilingual base identity plus reference identity preserves stale-pair rejection. The existing two-file installation/package boundary was not expanded. |
| 5. Recovery copy/scan reduction | adopted | Full-input copying and the repeated provenance reverse scan were replaced by a filtered fact view, one provenance-reference set, and copying only the application branch that is mutated. Acquisition successors copy only the rows whose authority reference changes. |
| 6. Browser partial refresh | adopted | Layer 3, interaction, and variant sections can be replaced independently. The static detail model, unrelated children, focus-bearing search widgets, scroll position, locale/item/generation invalidation, and dynamic requirements behavior remain under the existing Browser contract. |
| 7. Repository cleanup | partial by design | Added an ignore rule only for `Iris/tooling/.tmp/uv-cache/` and removed its final 10,392,380-byte disposable cache. Existing user files, LFS material, quality-review data, generation descriptors, and unrelated `.tmp` content were preserved. `.gitattributes` required no change. |
| 8. Residual structural deduplication | no-op | The recent responsibility-separation work already owns the remaining adapters and common modules. No second implementation body with a safe, direct benefit was confirmed, so no structure was extracted or relocated. |
| 9. Chunking | deferred | After deduplication the Tooltip two-file payload is 1,514,718 bytes. No measured post-dedup loading benefit justified new index/chunk members, I/O, install rules, or failure points. Deferral does not block Changes 3 or 4. |

## Direct measurements

| Subject | Before | After | Change |
| --- | ---: | ---: | ---: |
| `IrisEvolvedRecipeLookup.lua` | 1,742,824 bytes | 899,122 bytes | -843,702 bytes (-48.4%) |
| Evolved repeated value tables (conditions plus three locale records per 2,203 relations) | 8,812 | 172 pooled values (2 condition arrays, 170 locale pairs) | -8,640 (-98.1%); 2,203 relation records unchanged |
| `IrisTooltipRecipeVariants.lua` | 768,344 bytes | 398,532 bytes | -369,812 bytes (-48.1%) |
| StaticData plus RecipeVariants | 1,884,530 bytes | 1,514,718 bytes | -369,812 bytes (-19.6%) |
| Duplicated Tooltip base tables in the variant module | 349 | 0 | all bases reference StaticData |
| Recovery `deepcopy` call sites in the two changed modules | 20 | 16 | full input/acquisition copies removed; no timing or heap claim |
| Disposable tooling uv cache | 10,392,380 bytes | 0 bytes | removed; only this confirmed cache path was cleaned |

Cold/warm Kahlua load time, PZ heap use, input latency, and Python peak-memory improvement were not measured and are not claimed. The archive compression result is feasibility data, not repository savings.

## Validation

All commands ran from the selected repository with the non-editable tooling installation required by the plan. The fresh Recovery candidate completed with 24,342 source-confirmed facts; its disposable files were removed after the contract passed.

| Scope | Result |
| --- | --- |
| EvolvedRecipe, Tooltip serialization/projection, and affected Browser nodes | `14 passed in 10.65s`, exit 0. This includes the generated-Lua EvolvedRecipe lookup, base binding/reader order, Browser state/search/cache, partial section replacement, model reuse, and mutation isolation. |
| Recovery candidate contract | `1 passed in 1082.57s`, exit 0, with the exact `IRIS_LAYER3_RECOVERY_CANDIDATE` and installed-source identity. |
| Shared B→Menu product boundary | `2 passed in 134.92s`, exit 0. The same-process handoff produced product `l3p-ac95a82d7180e03fd14e295a386c79a7252317b5aa639e8549dc9ad223ebac08`; the disposable ZIP hash was `4ce8ecd615609d71d3f19e67068cd8c300a095f48016a4fbb9522ff18a0c7b07`. It exercised two deterministic builds, retained B identity, stage/ZIP lookup, Tooltip and Browser harnesses, package rejection fixtures, interruption/rollback, and recovery. |
| Exact repository Lua syntax command | `Lua syntax validation OK: 269 files`, exit 0. The product integration also checked the repository plus candidate stage (`396 files`, exit 0). |

The first focused attempt exposed a malformed Lua array in the new test fixture and was corrected. A later attempt required the explicit repository context expected by the non-editable installation. The first integration attempt selected a nonexistent production Apple/Soup relation for the new aliasing case; it was replaced with the owner-backed Acorn/Banana Bread pair. An attempted resume correctly rejected a different transient B ZIP path binding, so the final integration used a fresh single-process subject and passed. These failed attempts are not counted as PASS.

The repository full gate, archive test suite, Java/Gradle tests, and JS/TS checks were not run because their runner/classification/code surfaces did not change. The CAS code was not changed, so the plan's focused create/verify/restore sample replaced its full suite.

## In-game acceptance and remaining nonclaims

After the implementation handoff, the user reported that the final repository `Iris` runtime passed the requested in-game validation. This closes the Project Zomboid/Kahlua observation scope for KO/EN Alt opening lifetime, Menu/Tooltip coexistence, Browser section refresh under real focus/scroll/IME interaction, and dynamic requirement refresh. The report is user-observed acceptance; the game build, resolution, UI scale, font configuration, and external-mod set were not separately provided, so it is not a guarantee for every environment.

The planned implementation, focused automated contracts, and required in-game observation are complete. No extra confidence run, proof artifact, or validator was added after the user's acceptance.

The source-tree generated lookup/variant artifacts were updated, but no authority locator, adopted product pointer, external game installation, current-product adoption, or release was changed. Disposable Recovery, B, Menu, pytest, CAS-sample, and uv-cache workspaces created by this implementation were removed. Rollback is the removal of this closeout and the `.gitignore` rule plus restoration of the changed producer/runtime/test files; protected historical records are not part of rollback.
