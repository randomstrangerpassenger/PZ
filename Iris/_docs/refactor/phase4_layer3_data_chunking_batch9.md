# Phase 4-1 Layer3 Data Chunking Batch 9

Date: 2026-05-08

Historical roadmap item label: `docs/Iris/iris-refactoring-final-roadmap-v1.md` Phase 4-1

Status: closed at console-validation level. Korean and English chunk-path
console validation passed.

Correction note: the first English playtest for this batch validated only the
monolithic fallback path because the chunk manifest and chunk directory had not
yet been generated. That playtest is retained as fallback evidence, but it does
not close Phase 4-1.

## Scope

- Add optional chunk output to `export_dvf_3_3_lua_bridge.py`.
- Add a generated chunk manifest module for `IrisLayer3Data`.
- Make the Layer 3 runtime loader prefer the chunk manifest and fall back to
  the existing monolithic generated file.
- Do not manually split or rewrite the existing generated
  `IrisLayer3Data.lua`.

## Implementation

- `Iris/build/description/v2/tools/build/export_dvf_3_3_lua_bridge.py`
  now keeps monolithic `IrisLayer3Data.lua` output as the default contract.
- Chunk output is opt-in through:
  - `--chunk-output-dir`
  - `--chunk-manifest-path`
  - `--chunk-size`
  - `--chunk-module-prefix`
- Default chunk settings target:
  - manifest module: `Iris/Data/IrisLayer3DataChunks`
  - chunk modules: `Iris/Data/IrisLayer3DataChunks/Chunk###`
  - default chunk size: `200`
- The bridge report now records whether chunk output was written and includes
  chunk count, chunk size, manifest path, output directory, and per-chunk
  module metadata.
- `Iris/media/lua/client/Iris/Data/layer3_renderer.lua` now attempts
  `Iris/Data/IrisLayer3DataChunks` first, before using an already-loaded global
  `IrisLayer3Data`. If the manifest is absent or fails, it silently falls back
  to the existing global or to `Iris/Data/IrisLayer3Data`.
- Because the authoritative full rendered JSON referenced by earlier style
  closeout docs is not present in this workspace, the deployed chunk bundle was
  generated from the current authoritative runtime monolith:
  `Iris/media/lua/client/Iris/Data/IrisLayer3Data.lua`.
- Generated chunk bundle:
  - manifest: `Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks.lua`
  - chunks: `Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks/Chunk001.lua`
    through `Chunk011.lua`
  - chunk size: `200`
  - runtime entries: `2105`
  - generation report:
    `Iris/build/description/v2/staging/interaction_cluster/phase_d_runtime/phase4_layer3_chunks_from_monolith_report.json`

## Runtime Policy

The runtime policy is manifest-first, monolith-fallback.

This preserves current deployments that only contain `IrisLayer3Data.lua`, while
allowing a generated chunk manifest to replace the monolith load path when a
future build publishes chunks.

The current workspace's `output/dvf_3_3_rendered.json` is a small fixture, not
the full runtime authority. Do not regenerate deployed Layer 3 runtime data from
that fixture. For this batch, chunks were generated from the current deployed
runtime monolith to preserve the exact 2105-entry runtime data.

## Static Validation

Passed:

- `python -B -m unittest Iris\build\description\v2\tests\test_layer3_data_chunking_contract.py`
- `python -B -m unittest Iris\build\description\v2\tests\test_interaction_cluster_phase_d_runtime.py`
- `python -B -m unittest Iris\build\description\v2\tests\test_style_runtime_closeout.py`
- monolith/chunk key parity check: `2105 == 2105`, same order, unique keys

Completed after initial implementation:

- full unit discovery: `343 tests / OK`
- whitespace diff check: no whitespace errors; existing LF/CRLF warning only
- English chunk-path console validation:
  `Iris/_docs/refactor/phase4_en_layer3_data_chunking_playtest_validation.md`
- Korean chunk-path console validation:
  `Iris/_docs/refactor/phase4_ko_layer3_data_chunking_playtest_validation.md`
- English fallback-only console evidence:
  `Iris/_docs/refactor/playtest_evidence/2026-05-08-en-layer3-data-chunking/console.txt`

The first English fallback-only validation did not close Phase 4-1. The later
English chunk-path validation supersedes it for final English evidence.

## In-Game Validation Expectations

Required for both Korean and English playtests:

- `Iris/Data/layer3_renderer.lua` loads without Lua errors.
- If chunk files are deployed, `Iris/Data/IrisLayer3DataChunks.lua` and the
  relevant `Iris/Data/IrisLayer3DataChunks/Chunk###.lua` files load without
  Iris errors.
- If chunk files are not deployed, the loader falls back to
  `Iris/Data/IrisLayer3Data.lua` without warning spam.
- `Lua error`, `stack traceback`, `ExceptionLogger`, `attempt to`, `nil value`,
  `[Iris][DEBUG]`, and Iris-specific `ERROR/WARN` remain absent from the
  release console.

## English Fallback-Only Console Validation

Source log: `C:\Users\MW\Zomboid\Console.txt`

Archived evidence:
`Iris/_docs/refactor/playtest_evidence/2026-05-08-en-layer3-data-chunking/console.txt`

Result: pass for the monolithic fallback path only.

Key evidence:

- `translator: language is EN`
- `[Iris] Bootstrap complete`
- `Iris/Data/IrisLayer3Data.lua` loaded
- `Iris/Data/layer3_renderer.lua` loaded
- `IrisLayer3DataChunks.lua` and `IrisLayer3DataChunks/` were not deployed
- Iris-specific `WARN/ERROR`: 0
- `[Iris:Layer3]`: 0

This evidence is superseded for final closeout by the generated chunk bundle
above. A new English playtest must deploy the manifest and chunks.

## English Chunk-Path Console Validation

Source log: `C:\Users\MW\Zomboid\Console.txt`

Archived evidence:
`Iris/_docs/refactor/playtest_evidence/2026-05-08-en-layer3-data-chunking-chunk-path/console.txt`

Result: pass for the generated chunk path.

Key evidence:

- `translator: language is EN`
- `[Iris] Bootstrap complete`
- `Iris/Data/IrisLayer3DataChunks.lua` loaded
- `Iris/Data/IrisLayer3DataChunks/Chunk001.lua` through `Chunk011.lua` loaded
- `Iris/Data/layer3_renderer.lua` loaded
- `Iris/Data/IrisLayer3Data.lua` also loaded by PZ file discovery before the
  chunk manifest, but renderer policy now tries the chunk manifest before using
  the global monolith.
- Iris-specific `WARN/ERROR`: 0
- `[Iris:Layer3]`: 0

## Korean Chunk-Path Console Validation

Source log: `C:\Users\MW\Zomboid\Console.txt`

Archived evidence:
`Iris/_docs/refactor/playtest_evidence/2026-05-08-ko-layer3-data-chunking-chunk-path/console.txt`

Result: pass for the generated chunk path.

Key evidence:

- `translator: language is KO`
- `[Iris] Bootstrap complete`
- `Iris/Data/IrisLayer3DataChunks.lua` loaded
- `Iris/Data/IrisLayer3DataChunks/Chunk001.lua` through `Chunk011.lua` loaded
- `Iris/Data/layer3_renderer.lua` loaded
- `Iris/Data/IrisLayer3Data.lua` also loaded by PZ file discovery before the
  chunk manifest, but renderer policy now tries the chunk manifest before using
  the global monolith.
- Iris-specific `WARN/ERROR`: 0
- `[Iris:Layer3]`: 0

## Closeout

Phase 4-1 Layer3 data chunking batch 9 is closed at the console-validation
level. Screenshot-level UI evidence remains optional supporting evidence.
