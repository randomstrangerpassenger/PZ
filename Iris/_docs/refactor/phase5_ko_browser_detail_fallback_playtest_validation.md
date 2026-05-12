# Phase 5-8 Korean BrowserDetail Fallback Playtest Validation

Date: 2026-05-08

Batch: `Iris/_docs/refactor/phase5_browser_detail_fallback_batch17.md`

Status: pass at console-validation level for Korean runtime QA.

Source console:
`C:\Users\MW\Zomboid\console.txt`

Archived evidence:
`Iris/_docs/refactor/playtest_evidence/2026-05-08-ko-browser-detail-fallback/console.txt`

## Console Metadata

- LastWriteTime: `2026-05-08 13:46:24`
- Length: `271379`
- Line count: `2606`

## Language And Boot

- line 335: `translator: language is KO`
- line 1324: `[Iris] Bootstrap complete`

## BrowserDetail Runtime Evidence

- line 1415: `Iris/UI/Browser/IrisBrowserDetail.lua`
- `IrisBrowserDetail`: 1 match

The current deployed mod also loaded the Phase 4 generated Layer3 chunk path:

- line 1374: `Iris/Data/IrisLayer3DataChunks.lua`
- lines 1375-1385: `Iris/Data/IrisLayer3DataChunks/Chunk001.lua` through
  `Chunk011.lua`

## Dev Harness Gate

- `TestHarness`: 0 matches

The dev-only test harness did not load during the Korean playtest session.

## Error Scan

| Pattern | Count |
|---|---:|
| `Lua error` | 0 |
| `ExceptionLogger` | 0 |
| `Stack trace` | 0 |
| `stack traceback` | 0 |
| `attempt to` | 0 |
| `nil value` | 0 |
| `[Iris][ERROR]` | 0 |
| `[Iris][WARN]` | 0 |
| `[Iris][DEBUG]` | 0 |
| `Iris:Layer3` | 0 |

Non-Iris warnings from Echo, CheatMenuRebirth optional requires, fonts, sounds,
models, vehicles, and vanilla/mod loading were present in the global console but
did not reference Iris, IrisBrowserDetail, or the Phase 5 refactor modules.

## Result

Pass at console-validation level for the Korean BrowserDetail fallback runtime
path. English playtest validation remains optional follow-up evidence for
bilingual closeout.
