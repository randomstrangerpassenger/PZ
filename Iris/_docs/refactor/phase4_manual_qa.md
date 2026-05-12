# Iris Refactor Phase 4 Manual QA

Date: 2026-05-06

Source roadmap: `docs/Iris/iris-refactoring-final-roadmap-v1.md`

Phase 4 changes affect Lua runtime behavior. No Phase 4 runtime refactor batch
is complete until this checklist is run against an in-game build and the result
is recorded in the batch notes.

## Deployment Precheck

Before running any in-game actions for a runtime batch, confirm that the
deployed mod copy under `C:\Users\MW\Zomboid\mods\Iris` contains that batch's
changed runtime files.

For Phase 4-1, the deployed runtime file must be:

- `media/lua/client/Iris/Data/layer3_renderer.lua`

If generated chunk output is part of the playtest deployment, the deployed mod
copy must also contain:

- `media/lua/client/Iris/Data/IrisLayer3DataChunks.lua`
- `media/lua/client/Iris/Data/IrisLayer3DataChunks/Chunk###.lua`

If chunk output is not deployed, this batch can only validate the monolithic
fallback path through `media/lua/client/Iris/Data/IrisLayer3Data.lua`.

For Phase 4-5, the deployed files must be:

- `media/lua/client/Iris/UI/Browser/IrisBrowserBase.lua`
- `media/lua/client/Iris/UI/Browser/IrisBrowser.lua`
- `media/lua/client/Iris/UI/Browser/IrisBrowserListController.lua`
- `media/lua/client/Iris/UI/Browser/IrisBrowserDetail.lua`

For Phase 4-6, the deployed file must be:

- `media/lua/client/Iris/UI/Wiki/IrisWikiSections.lua`

If any required file is missing from the deployed mod copy, the playtest can
still exercise old behavior and must not be accepted as validation for the
current batch.

## Test Matrix

Run each scenario with Korean and English UI language settings when possible.
If only one language can be tested, record the tested language and treat
fallback behavior as unverified.

| Area | Scenario | Expected result | Evidence |
|---|---|---|---|
| Boot | Start game with Iris enabled | Iris loads without Lua errors | `console.txt` excerpt |
| Boot log | Inspect Iris boot messages | release log is concise; dev-only details stay behind dev flag | `console.txt` excerpt |
| Tooltip | Hold Alt over a supported item | Iris tooltip appears with Layer 3 description block | screenshot or note |
| Tooltip off | Release Alt or inspect unsupported item | Iris tooltip hides or falls back without stale data | screenshot or note |
| Right-click | Right-click supported item | Iris entry point appears | screenshot or note |
| Right-click detail | Open "Iris 메뉴에서 더보기" | Browser/detail flow opens for the selected item | screenshot or note |
| Browser open | Open Iris Browser directly | Browser opens without empty index errors | screenshot or note |
| Browser search | Search by known item/category text | Result list filters deterministically | query + expected item |
| Browser category | Select category | Category list matches pre-refactor behavior | category name |
| Browser list/detail | Select item from list | Detail panel shows use cases, description, and requirements | item fulltype |
| Recipe requirements | Inspect recipe-capable item | recipe requirement atoms render when present | item fulltype |
| Right-click capability | Inspect action-capable item | right-click capability renders when present | item fulltype |
| KO fallback | Missing KO key or EN-only key | EN/key fallback is visible and non-crashing | key/item |
| EN fallback | Missing EN key | key fallback is visible and non-crashing | key/item |
| Error logging | Force or observe recoverable missing data | release log avoids noisy stack spam; dev log keeps diagnostics | `console.txt` excerpt |

## Required Regression Items

Use at least one item from each group:

- Layer 3 description block: any item present in `IrisLayer3Data`
- recipe requirement: an item with `recipe_requirements_index.v2.4.json` entries
- right-click capability: an item with `usecases_by_fulltype.v2.4.json`
  `context_menu` evidence
- mixed browser flow: an item with both recipe and right-click surfaces when
  available

## External Input Contract Check

Before Phase 4-2 or Phase 4-4 changes, verify that the batch does not break
planned external mod input contracts:

- `IrisAPI` public table names and function names
- translation key loading and fallback behavior
- item fulltype keys used by generated data
- browser category keys and search tokens
- generated description/use-case/requirement JSON and Lua data keys

If a runtime API must move, the batch needs a compatibility window and a
deprecation note before code changes land.

## Batch Rule

Phase 4-1, Phase 4-2, and Phase 4-8 must stay in separate runtime batches.
Phase 4-4 translation source changes must also stay separate from release/dev
log behavior changes.

## Recorded Baselines

- Korean playtest: `Iris/_docs/refactor/phase4_ko_playtest_validation.md`
- English playtest: `Iris/_docs/refactor/phase4_en_playtest_validation.md`

Both baselines reached Iris bootstrap completion without Iris Lua exceptions.
The English baseline was validated after an in-session translator switch to
`EN`; it is not a cold process boot with `user.language=en`.

## Runtime Batch Validation

- Phase 4-2 IrisAPI split batch 1:
  `Iris/_docs/refactor/phase4_iris_api_split_batch1.md`

English post-split console validation:

- `Iris/_docs/refactor/phase4_en_api_split_playtest_validation.md`

Korean post-split console validation:

- `Iris/_docs/refactor/phase4_ko_api_split_playtest_validation.md`

This batch is closed at the console-validation level. Screenshot-level evidence
for individual UI interactions remains optional supporting evidence, not a
blocking gate for this batch.

Next runtime batch pending QA:

- Phase 4-2 IrisAPI consumer migration batch 2:
  `Iris/_docs/refactor/phase4_iris_api_consumer_migration_batch2.md`

Korean post-batch-2 console validation:

- `Iris/_docs/refactor/phase4_ko_api_consumer_migration_playtest_validation.md`

English post-batch-2 console validation:

- `Iris/_docs/refactor/phase4_en_api_consumer_migration_playtest_validation.md`

This batch is closed at the console-validation level. Screenshot-level evidence
for individual UI interactions remains optional supporting evidence, not a
blocking gate for this batch.

Next runtime batch pending QA:

- Phase 4-3 IrisBrowserData split batch 3:
  `Iris/_docs/refactor/phase4_iris_browser_data_split_batch3.md`

Required post-batch-3 console validation:

Korean post-batch-3 console validation:

- `Iris/_docs/refactor/phase4_ko_browser_data_split_playtest_validation.md`

English post-batch-3 console validation:

- `Iris/_docs/refactor/phase4_en_browser_data_split_playtest_validation.md`

This batch is closed at the console-validation level. Screenshot-level evidence
for category/list/detail/search behavior remains optional supporting evidence,
not a blocking gate for this batch.

Next runtime batch pending QA:

- Phase 4-4 Translation source batch 4:
  `Iris/_docs/refactor/phase4_translation_source_batch4.md`

Required post-batch-4 console validation:

- Korean post-batch-4 console validation:
  `Iris/_docs/refactor/phase4_ko_translation_source_playtest_validation.md`
- English post-batch-4 console validation:
  `Iris/_docs/refactor/phase4_en_translation_source_playtest_validation.md`

This batch is closed at the console-validation level. Screenshot-level evidence
for translated Browser, tooltip, and context menu labels remains optional
supporting evidence.

Next runtime batch pending QA:

- Phase 4-5 Browser common base batch 5:
  `Iris/_docs/refactor/phase4_browser_common_base_batch5.md`

Required post-batch-5 console validation:

- Korean post-batch-5 console validation:
  `Iris/_docs/refactor/phase4_ko_browser_common_base_playtest_validation.md`
- English post-batch-5 console validation:
  `Iris/_docs/refactor/phase4_en_browser_common_base_playtest_validation.md`

Prior English post-batch-5 attempt:

- `Iris/_docs/refactor/phase4_en_browser_common_base_playtest_validation.md`

The first English attempt was invalid because the deployed mod was missing
`IrisBrowserBase.lua`; the later English attempt loaded `IrisBrowserBase.lua`
and passed console validation.

This batch is closed at the console-validation level. Screenshot-level Browser
layout evidence remains optional supporting evidence.

Next runtime batch pending QA:

- Phase 4-6 Wiki fallback batch 6:
  `Iris/_docs/refactor/phase4_wiki_fallback_batch6.md`

Required post-batch-6 console validation:

- Korean post-batch-6 console validation:
  `Iris/_docs/refactor/phase4_ko_wiki_fallback_playtest_validation.md`
- English post-batch-6 console validation:
  `Iris/_docs/refactor/phase4_en_wiki_fallback_playtest_validation.md`

This batch is closed at the console-validation level. Explicit missing-key
fallback UI evidence remains optional supporting evidence.

Next runtime batch pending QA:

- Phase 4-7 Layer 3 presentation formatting batch 7:
  `Iris/_docs/refactor/phase4_layer3_presentation_formatting_batch7.md`

Required post-batch-7 console validation:

- Korean post-batch-7 console validation:
  `Iris/_docs/refactor/phase4_ko_layer3_presentation_formatting_playtest_validation.md`
- English post-batch-7 console validation:
  `Iris/_docs/refactor/phase4_en_layer3_presentation_formatting_playtest_validation.md`

This batch is closed at the console-validation level. Browser/detail or Wiki
Layer 3 display line screenshots remain optional supporting evidence.

Next runtime batch pending QA:

- Phase 4-8 ProtectedCall boundary batch 8:
  `Iris/_docs/refactor/phase4_protected_call_boundary_batch8.md`

Required post-batch-8 console validation:

- Korean post-batch-8 console validation:
  `Iris/_docs/refactor/phase4_ko_protected_call_boundary_playtest_validation.md`
- English post-batch-8 console validation:
  `Iris/_docs/refactor/phase4_en_protected_call_boundary_playtest_validation.md`

This batch is closed at the console-validation level.

Next runtime batch pending QA:

- Phase 4-1 Layer3 data chunking batch 9:
  `Iris/_docs/refactor/phase4_layer3_data_chunking_batch9.md`

Required post-batch-9 console validation:

- Korean post-batch-9 console validation:
  `Iris/_docs/refactor/phase4_ko_layer3_data_chunking_playtest_validation.md`
- English post-batch-9 console validation:
  `Iris/_docs/refactor/phase4_en_layer3_data_chunking_playtest_validation.md`

For this batch, record whether the playtest deployed generated chunk files or
only exercised the monolithic fallback path.

English post-batch-9 console validation:

- `Iris/_docs/refactor/phase4_en_layer3_data_chunking_playtest_validation.md`

The first English attempt validated only the monolithic fallback path because
generated `IrisLayer3DataChunks.lua` and
`IrisLayer3DataChunks/Chunk###.lua` files were not deployed. The later English
attempt deployed the generated chunk manifest and `Chunk001.lua` through
`Chunk011.lua`, loaded them without Iris errors, and passes at the
console-validation level.

Korean post-batch-9 console validation:

- `Iris/_docs/refactor/phase4_ko_layer3_data_chunking_playtest_validation.md`

The Korean attempt deployed the generated chunk manifest and `Chunk001.lua`
through `Chunk011.lua`, loaded them without Iris errors, and passes at the
console-validation level.

This batch is closed at the console-validation level. Screenshot-level Layer 3
UI evidence remains optional supporting evidence.
