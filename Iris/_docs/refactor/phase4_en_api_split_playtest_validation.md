# Phase 4-2 English API Split Playtest Validation

Date: 2026-05-06

Evidence root:

- `Iris/_docs/refactor/playtest_evidence/2026-05-06-en-api-split-attempt/console.txt`
- `Iris/_docs/refactor/playtest_evidence/2026-05-06-en-api-split-attempt/DebugLog.txt`
- `Iris/_docs/refactor/playtest_evidence/2026-05-06-en-api-split-attempt/echo_report_20260506_074834.json`

Validated batch:

- `Iris/_docs/refactor/phase4_iris_api_split_batch1.md`

## Result

Status: English console validation pass for Phase 4-2 API split batch 1.

This is not a full Phase 4-2 runtime closeout because Korean post-split QA has
not been recorded yet.

## Language Read

- Process starts with `user.language=ko` at console line 49.
- Runtime translator switches to `EN` at console line 278.

This validates the English runtime surface after translator selection/switch.
It is not a cold process boot with `user.language=en`.

## Iris Runtime Read

- Iris bootstrap completed at console line 1267:
  `[Iris] Bootstrap complete`
- Split-batch public facade loaded at console line 1326:
  `Iris/media/lua/client/Iris/IrisAPI.lua`
- Deployed split files were present under:
  `C:/Users/MW/Zomboid/mods/Iris/media/lua/client/Iris/API/`

The console does not print `Iris/API/*` submodule load lines, but no require
failure, Lua error, or stack trace appears after `IrisAPI.lua` loads. Since the
facade requires the submodules at module load time, this is read as a successful
API split load path.

## Error Scan

Console scan:

| Pattern | Count |
|---|---:|
| `Iris` | 67 |
| `IrisAPI` | 1 |
| `Iris/API` | 0 |
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
- Vanilla/mod data warnings such as broken `laboratory` distributions, missing
  FMOD events, vehicle distribution warnings, mannequin zone warning, and
  moveables settings warnings.

None of these are attributed to the Iris API split.

## Echo Report Read

From `echo_report_20260506_074834.json`:

- `performance_score`: `100.0`
- `quality_score`: `90`
- `total_freezes`: `1`
- `used_fallback_ticks`: `true`
- `fallback_contaminated_timing`: `false`
- `phase_status`: `OK`
- `tick_contract_valid`: `true`
- report `score`: `100`

Echo fallback tick usage remains non-blocking for this Iris runtime validation
because timing is not marked contaminated and there is no Iris-specific error.

## Manual QA State

English post-split playtest is accepted as console-validated.

Still required before closing Phase 4-2 batch 1:

- Korean post-split playtest validation.
- Any screenshot/user-observed UI notes the user wants to preserve for tooltip,
  browser detail, recipe requirements, and right-click capability surfaces.

