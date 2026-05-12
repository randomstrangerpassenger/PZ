# Phase 4-2 Korean API Split Playtest Validation

Date: 2026-05-06

Evidence root:

- `Iris/_docs/refactor/playtest_evidence/2026-05-06-ko-api-split-attempt/console.txt`

Validated batch:

- `Iris/_docs/refactor/phase4_iris_api_split_batch1.md`

## Result

Status: Korean console validation pass for Phase 4-2 API split batch 1.

This closes the language-side console validation pair for the first `IrisAPI`
split runtime batch:

- English post-split console validation: pass
- Korean post-split console validation: pass

## Language Read

- Process starts with `user.language=ko` at console line 107.
- Runtime translator reports `KO` at console line 335.
- Translation load attempts include `KO` at console line 2152.

This validates a Korean runtime surface in the default process language path.

## Iris Runtime Read

- Iris bootstrap completed at console line 1324:
  `[Iris] Bootstrap complete`
- API split sub-facades loaded:
  - `Iris/API/Description.lua` at console line 1359
  - `Iris/API/Tags.lua` at console line 1361
  - `Iris/API/StaticData.lua` at console line 1362
  - `Iris/API/Index.lua` at console line 1363
  - `Iris/API/UseCases.lua` at console line 1364
- Public compatibility facade loaded at console line 1389:
  `Iris/media/lua/client/Iris/IrisAPI.lua`

The order is acceptable because Project Zomboid preloads Lua files and the
compatibility facade still exists as the public API surface.

## Error Scan

Console scan:

| Pattern | Count |
|---|---:|
| `Iris` | 72 |
| `IrisAPI` | 1 |
| `Iris/API` | 5 |
| `Lua error` | 0 |
| `stack traceback` | 0 |
| `ExceptionLogger` | 0 |
| `attempt to` | 0 |
| `nil value` | 0 |
| `getDescriptionBlocks` | 0 |
| `[Iris][DEBUG]` | 0 |

Iris-specific `ERROR` / `WARN` matches: `0`.

## Non-Iris Noise

Observed non-Iris noise:

- Echo freeze/fallback tick warnings.
- Pulse `LuaAdapter` OnSave errors.
- Vanilla/mod data warnings such as broken `laboratory` distributions,
  mannequin zone warning, FMOD/no-error lines, and moveables settings warnings.

None of these are attributed to the Iris API split.

## Missing Companion Artifacts

No latest `DebugLog.txt` or `echo_report*.json` was present in the checked
default Zomboid log location for this Korean attempt. This validation is based
on `Console.txt`.

## Manual QA State

Korean post-split playtest is accepted as console-validated. Interactive UI
flows are not individually visible in the console log; their execution is read
from the user's playtest report.

