# Phase 4-2 Korean API Consumer Migration Playtest Validation

Date: 2026-05-06

Evidence root:

- `Iris/_docs/refactor/playtest_evidence/2026-05-06-ko-api-consumer-migration/console.txt`

Validated batch:

- `Iris/_docs/refactor/phase4_iris_api_consumer_migration_batch2.md`

## Result

Status: Korean console validation pass for Phase 4-2 API consumer migration
batch 2.

This does not close batch 2 by itself. English post-batch-2 validation is still
required before runtime closeout.

## Language Read

- Process starts with `user.language=ko` at console line 91.
- Runtime translator reports `KO` at console line 319.
- Translation load attempts include `KO` at console line 2136.

This validates a Korean runtime surface in the default process language path.

## Iris Runtime Read

- Iris bootstrap completed at console line 1308:
  `[Iris] Bootstrap complete`
- API split sub-facades loaded:
  - `Iris/API/Description.lua` at console line 1343
  - `Iris/API/Tags.lua` at console line 1345
  - `Iris/API/StaticData.lua` at console line 1346
  - `Iris/API/Index.lua` at console line 1347
  - `Iris/API/UseCases.lua` at console line 1348
- Public compatibility facade loaded at console line 1373:
  `Iris/media/lua/client/Iris/IrisAPI.lua`
- Batch 2 UI consumer files loaded:
  - `Iris/UI/Browser/IrisBrowserDetail.lua` at console line 1385
  - `Iris/UI/Browser/IrisBrowserInteractionRenderer.lua` at console line 1386
  - `Iris/UI/Browser/IrisBrowserData.lua` at console line 1390
  - `Iris/UI/Wiki/IrisWikiSections.lua` at console line 1397

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
default Zomboid log location for this Korean attempt. This validation is based
on `Console.txt`.

## Manual QA State

Korean post-batch-2 playtest is accepted as console-validated. Interactive UI
flows are not individually visible in the console log; their execution is read
from the user's playtest report.

