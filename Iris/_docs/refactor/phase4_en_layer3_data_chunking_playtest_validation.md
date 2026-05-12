# Phase 4-1 Layer3 Data Chunking English Playtest Validation

Date: 2026-05-08

Batch: `Iris/_docs/refactor/phase4_layer3_data_chunking_batch9.md`

Status: pass at console-validation level for the generated chunk path.

Source console:
`C:\Users\MW\Zomboid\Console.txt`

Archived evidence:
`Iris/_docs/refactor/playtest_evidence/2026-05-08-en-layer3-data-chunking-chunk-path/console.txt`

Prior fallback-only evidence:
`Iris/_docs/refactor/playtest_evidence/2026-05-08-en-layer3-data-chunking/console.txt`

## Console Metadata

- LastWriteTime: `2026-05-08 02:08:44`
- Length: `259684`
- Line count: `2532`

## Language And Boot

- line 76: `user.language=ko`
- line 305: `translator: language is EN`
- line 1294: `[Iris] Bootstrap complete`

This matches the prior English validation pattern: the process starts with
`user.language=ko`, then the translator switches to `EN` in-session.

## Deployment State

- `IrisLayer3DataChunks.lua`: present, length `951`, LastWriteTime `2026-05-08 02:01:13`
- `IrisLayer3DataChunks/`: present
- chunk files: `Chunk001.lua` through `Chunk011.lua`
- `layer3_renderer.lua`: present, length `3612`, LastWriteTime `2026-05-08 02:00:05`
- `IrisLayer3Data.lua`: present, length `1024287`, LastWriteTime `2026-04-30 21:46:48`

## Phase 4-1 Load Evidence

- line 1342: `Iris/Data/IrisLayer3Data.lua`
- line 1343: `Iris/Data/IrisLayer3DataChunks.lua`
- line 1344: `Iris/Data/IrisLayer3DataChunks/Chunk001.lua`
- line 1345: `Iris/Data/IrisLayer3DataChunks/Chunk002.lua`
- line 1346: `Iris/Data/IrisLayer3DataChunks/Chunk003.lua`
- line 1347: `Iris/Data/IrisLayer3DataChunks/Chunk004.lua`
- line 1348: `Iris/Data/IrisLayer3DataChunks/Chunk005.lua`
- line 1349: `Iris/Data/IrisLayer3DataChunks/Chunk006.lua`
- line 1350: `Iris/Data/IrisLayer3DataChunks/Chunk007.lua`
- line 1351: `Iris/Data/IrisLayer3DataChunks/Chunk008.lua`
- line 1352: `Iris/Data/IrisLayer3DataChunks/Chunk009.lua`
- line 1353: `Iris/Data/IrisLayer3DataChunks/Chunk010.lua`
- line 1354: `Iris/Data/IrisLayer3DataChunks/Chunk011.lua`
- line 1371: `Iris/Data/layer3_renderer.lua`

Counts:

- `IrisLayer3DataChunks`: 12
- `Iris/Data/IrisLayer3DataChunks/Chunk`: 11
- `Iris/Data/IrisLayer3Data.lua`: 1
- `Iris/Data/layer3_renderer.lua`: 1

## Error Scan

- `Lua error`: 0
- `stack traceback`: 0
- `ExceptionLogger`: 0
- `attempt to`: 0
- `nil value`: 0
- `[Iris][DEBUG]`: 0
- `[Iris:Layer3]`: 0
- `Failed to require IrisLayer3Data`: 0
- Iris-specific `WARN/ERROR`: 0

Non-Iris warnings/errors from Echo, Pulse, vanilla sound/model/vehicle loading,
and map/distribution data were present in the global console but are unrelated
to the Phase 4-1 Layer 3 data loading change.

## Result

Pass at console-validation level for the English generated chunk path.
