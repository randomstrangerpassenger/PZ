# Phase 4-2 English API Consumer Migration Playtest Validation

Date: 2026-05-06

Evidence root:

- `Iris/_docs/refactor/playtest_evidence/2026-05-06-en-api-consumer-migration/console.txt`

Validated batch:

- `Iris/_docs/refactor/phase4_iris_api_consumer_migration_batch2.md`

## Result

Status: English console validation pass for Phase 4-2 API consumer migration
batch 2.

This closes the language-side console validation pair for the second
`IrisAPI` consumer migration runtime batch:

- Korean post-batch-2 console validation: pass
- English post-batch-2 console validation: pass

## Language Read

- Process starts with `user.language=ko` at console line 49.
- Runtime translator reports `EN` at console line 278.

This validates the English runtime surface after translator selection/switch.
It is not a cold process boot with `user.language=en`.

## Iris Runtime Read

- Iris bootstrap completed at console line 1267:
  `[Iris] Bootstrap complete`
- API split sub-facades loaded:
  - `Iris/API/Description.lua` at console line 1302
  - `Iris/API/Tags.lua` at console line 1304
  - `Iris/API/StaticData.lua` at console line 1305
  - `Iris/API/Index.lua` at console line 1306
  - `Iris/API/UseCases.lua` at console line 1307
- Public compatibility facade loaded at console line 1332:
  `Iris/media/lua/client/Iris/IrisAPI.lua`
- Batch 2 UI consumer files loaded:
  - `Iris/UI/Browser/IrisBrowserDetail.lua` at console line 1344
  - `Iris/UI/Browser/IrisBrowserInteractionRenderer.lua` at console line 1345
  - `Iris/UI/Browser/IrisBrowserData.lua` at console line 1349
  - `Iris/UI/Wiki/IrisWikiSections.lua` at console line 1356

Deployed UI files were checked and contain the batch 2 sub-facade call paths:

- `IrisAPI.Tags`
- `IrisAPI.Index`
- `IrisAPI.Description`
- `IrisAPI.UseCases`

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

None of these are attributed to the Iris API consumer migration.

## Missing Companion Artifacts

No latest `DebugLog.txt` or `echo_report*.json` was present in the checked
default Zomboid log location for this English attempt. This validation is based
on `Console.txt`.

## Manual QA State

English post-batch-2 playtest is accepted as console-validated. Interactive UI
flows are not individually visible in the console log; their execution is read
from the user's playtest report.

