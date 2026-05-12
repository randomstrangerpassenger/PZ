# Iris Refactoring Final Roadmap Closeout

Date: 2026-05-08

Roadmap: `docs/Iris/iris-refactoring-final-roadmap-v1.md`

Status: implemented and closed at static-test plus console-validation level.

## Scope Closed

The roadmap implementation ran through all planned phases:

- Phase 1: build residue cleanup and active scope disposition
- Phase 2: dead-code and compatibility-boundary cleanup
- Phase 3: build pipeline structure and test infrastructure
- Phase 4: Lua runtime responsibility split
- Phase 5: small runtime cleanup items 5-1 through 5-9

The final implemented roadmap item is Phase 5-9:
`Iris/_docs/refactor/phase5_module_bootstrap_batch18.md`.

## Phase Evidence

Primary completion records:

- Phase 1-3 historical execution records:
  `Iris/_docs/refactor/_done/`
- Phase 4 runtime batches:
  - `Iris/_docs/refactor/phase4_iris_api_split_batch1.md`
  - `Iris/_docs/refactor/phase4_iris_api_consumer_migration_batch2.md`
  - `Iris/_docs/refactor/phase4_iris_browser_data_split_batch3.md`
  - `Iris/_docs/refactor/phase4_translation_source_batch4.md`
  - `Iris/_docs/refactor/phase4_browser_common_base_batch5.md`
  - `Iris/_docs/refactor/phase4_wiki_fallback_batch6.md`
  - `Iris/_docs/refactor/phase4_layer3_presentation_formatting_batch7.md`
  - `Iris/_docs/refactor/phase4_protected_call_boundary_batch8.md`
  - `Iris/_docs/refactor/phase4_layer3_data_chunking_batch9.md`
- Phase 5 cleanup batches:
  - `Iris/_docs/refactor/phase5_generator_debug_gate_batch10.md`
  - `Iris/_docs/refactor/phase5_array_util_batch11.md`
  - `Iris/_docs/refactor/phase5_test_harness_dev_gate_batch12.md`
  - `Iris/_docs/refactor/phase5_ordering_single_pass_batch13.md`
  - `Iris/_docs/refactor/phase5_iris_main_function_specs_batch14.md`
  - `Iris/_docs/refactor/phase5_iris_desc_logger_direct_require_batch15.md`
  - `Iris/_docs/refactor/phase5_iris_config_constants_batch16.md`
  - `Iris/_docs/refactor/phase5_browser_detail_fallback_batch17.md`
  - `Iris/_docs/refactor/phase5_module_bootstrap_batch18.md`

## Latest Validation

Static tests:

- `python -B -m unittest discover -s Iris\build\description\v2\tests -p "test_*.py"`
- Result: `380 tests / OK`

Latest runtime smoke:

- `Iris/_docs/refactor/phase5_ko_module_bootstrap_playtest_validation.md`
- Archived console:
  `Iris/_docs/refactor/playtest_evidence/2026-05-08-ko-module-bootstrap/console.txt`
- Language: KO
- `[Iris] Bootstrap complete`: present
- `Iris/Util/IrisModuleBootstrap.lua`: loaded
- `TestHarness`: 0 matches
- Iris Lua error patterns: 0 matches

## 2026-05-12 Roadmap v4.1 Addendum

The follow-up refactoring plan from `C:/Users/MW/Downloads/1.txt` was executed
on top of this closeout.

Completed follow-up items:

- T0-A/T0-B/T0-C: browser theme extraction, build backup ignore cleanup, and
  bootstrap log cleanup.
- T1-A/T1-B: translation fallback centralization and protected Java/Kahlua
  access helper extraction.
- T2-A/T2-B/T2-C: item access helper extraction, UseCaseDescriptions
  requirements lookup split, and deprecated no-op API markers.
- T3-C: Layer 3 runtime deployment is chunks-only for the user's actual
  workspace-copy validation path.

Latest in-game validation:

- Source: `C:/Users/MW/Zomboid/Console.txt`
- Last write time observed: `2026-05-12 20:42:50`
- `Iris/Data/IrisLayer3Data.lua`: 0 loads.
- `Iris/Data/IrisLayer3DataChunks.lua`: 1 load.
- `Iris/Data/IrisLayer3DataChunks/Chunk*.lua`: 11 loads.
- Installed monolith path: absent.
- CheatMenu context-menu regression markers
  (`getWidthOrig`, `ISContextMenu.lua line # 475`, stack traces, thrown
  exceptions): 0 matches.

## Residual Non-Blocking Notes

- Phase 5-8 English detail fallback validation is optional follow-up evidence,
  not a blocking closeout requirement.
- Packaging, commit creation, and release notes are outside this roadmap
  implementation closeout unless opened as a separate task.
- The working tree contains many pre-existing modified, deleted, and untracked
  files. This closeout does not claim a clean git state.

## Result

`docs/Iris/iris-refactoring-final-roadmap-v1.md` is complete at the intended
implementation, static-test, and console-validation level.
