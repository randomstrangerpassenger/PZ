# Phase 5-9 Korean Module Bootstrap Playtest Validation

Date: 2026-05-08

Batch: `Iris/_docs/refactor/phase5_module_bootstrap_batch18.md`

Status: pass at console-validation level for Korean runtime smoke.

Source console:
`C:\Users\MW\Zomboid\console.txt`

Archived evidence:
`Iris/_docs/refactor/playtest_evidence/2026-05-08-ko-module-bootstrap/console.txt`

## Console Metadata

- LastWriteTime: `2026-05-08 14:28:20`
- Length: `267061`
- Line count: `2575`

## Language And Boot

- line 315: `translator: language is KO`
- line 1297: `!!!!! IRIS BOOTSTRAP: START LOAD !!!!!`
- line 1304: `!!!!! IRIS BOOTSTRAP: IrisMain loaded successfully !!!!!`
- line 1305: `[Iris] Bootstrap complete`

## Phase 5-9 Load Evidence

- line 1299: `Iris/IrisMain.lua`
- line 1300: `Iris/Util/IrisModuleBootstrap.lua`
- line 1301: `Iris/Util/IrisRequire.lua`
- line 1302: `Iris/Util/IrisLogger.lua`
- line 1303: `Iris/IrisConfig.lua`

Core runtime consumers still loaded after the shared bootstrap helper:

- line 1340: `Iris/API/Description.lua`
- line 1344: `Iris/API/StaticData.lua`
- line 1383: `Iris/Data/layer3_renderer.lua`
- line 1385: `Iris/IrisTranslationLoader.lua`
- line 1392: `Iris/UI/Browser/IrisBrowser.lua`
- line 1402: `Iris/UI/Browser/IrisBrowserData.lua`
- line 1404: `Iris/UI/Browser/IrisBrowserItemIndex.lua`
- line 1407: `Iris/UI/Browser/IrisMapIcon.lua`
- line 1409: `Iris/UI/Tooltip/IrisAltTooltip.lua`
- line 1411: `Iris/UI/Wiki/IrisContextMenu.lua`
- line 1413: `Iris/UI/Wiki/IrisWikiSections.lua`

## Dev Harness Gate

- `TestHarness`: 0 matches

Legacy `Pulse/Iris/Logic/IrisDesc/*` compatibility wrappers loaded, but no
production `TestHarness` module loaded.

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
| `FAILED to load IrisMain` | 0 |

The broad `FAILED to load` pattern matched five non-Iris font texture messages:
`mainfont_0.png`, `mainfont2_0.png`, and `zomboidDialogue.bmfc_0.png`.

## Result

Pass at console-validation level for the Korean Phase 5-9 module bootstrap
runtime smoke.
