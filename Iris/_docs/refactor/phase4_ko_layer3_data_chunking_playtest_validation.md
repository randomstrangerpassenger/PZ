# Phase 4-1 Layer3 Data Chunking Korean Playtest Validation

Date: 2026-05-08

Batch: `Iris/_docs/refactor/phase4_layer3_data_chunking_batch9.md`

Status: pass at console-validation level for the generated chunk path.

Source console:
`C:\Users\MW\Zomboid\Console.txt`

Archived evidence:
`Iris/_docs/refactor/playtest_evidence/2026-05-08-ko-layer3-data-chunking-chunk-path/console.txt`

## Console Metadata

- LastWriteTime: `2026-05-08 02:15:16`
- Length: `266917`
- Line count: `2580`

## Language And Boot

- line 104: `user.language=ko`
- line 332: `translator: language is KO`
- line 1321: `[Iris] Bootstrap complete`

## Deployment State

- `IrisLayer3DataChunks.lua`: present, length `951`, LastWriteTime `2026-05-08 02:01:13`
- `IrisLayer3DataChunks/`: present
- chunk files: `Chunk001.lua` through `Chunk011.lua`
- `layer3_renderer.lua`: present, length `3612`, LastWriteTime `2026-05-08 02:00:05`
- `IrisLayer3Data.lua`: present, length `1024287`, LastWriteTime `2026-04-30 21:46:48`

## Phase 4-1 Load Evidence

- line 1369: `Iris/Data/IrisLayer3Data.lua`
- line 1370: `Iris/Data/IrisLayer3DataChunks.lua`
- line 1371: `Iris/Data/IrisLayer3DataChunks/Chunk001.lua`
- line 1372: `Iris/Data/IrisLayer3DataChunks/Chunk002.lua`
- line 1373: `Iris/Data/IrisLayer3DataChunks/Chunk003.lua`
- line 1374: `Iris/Data/IrisLayer3DataChunks/Chunk004.lua`
- line 1375: `Iris/Data/IrisLayer3DataChunks/Chunk005.lua`
- line 1376: `Iris/Data/IrisLayer3DataChunks/Chunk006.lua`
- line 1377: `Iris/Data/IrisLayer3DataChunks/Chunk007.lua`
- line 1378: `Iris/Data/IrisLayer3DataChunks/Chunk008.lua`
- line 1379: `Iris/Data/IrisLayer3DataChunks/Chunk009.lua`
- line 1380: `Iris/Data/IrisLayer3DataChunks/Chunk010.lua`
- line 1381: `Iris/Data/IrisLayer3DataChunks/Chunk011.lua`
- line 1398: `Iris/Data/layer3_renderer.lua`

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

Pass at console-validation level for the Korean generated chunk path.
