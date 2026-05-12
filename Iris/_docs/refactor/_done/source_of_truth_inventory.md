# Iris Source Of Truth Inventory

Archived under `_done` by the Phase 1 v1.4 refactor doc split.

This document records the non-obvious P0 source-of-truth decisions from
`iris_refactor_roadmap_v2.0.md`. P0 is manifest-only: no file is deleted or
moved here.

## iris-lua

### Scope

Tracked files currently under `Iris/lua/`:

| Path | Role observed |
|---|---|
| `Iris/lua/IrisApi.lua` | legacy standalone Iris API facade |
| `Iris/lua/IrisData.lua` | legacy standalone generated classification data |
| `Iris/lua/test_iris_api.lua` | local Lua test harness using sibling `dofile()` calls |

### Evidence

| Check | Result |
|---|---|
| Runtime loader root | Current mod loader entry is `Iris/media/lua/client/AIrisBoot.lua`, which requires `Iris/IrisMain`. |
| Runtime replacement authority | Current runtime API/data live under `Iris/media/lua/client/Iris/`, especially `Iris/IrisAPI.lua` and `Iris/Data/IrisData.lua`. |
| External runtime references | No active runtime `require()` target points at `Iris/lua/`. The only direct sibling `dofile()` consumer is `Iris/lua/test_iris_api.lua`. |
| PZ loader path | PZ mod Lua loading is rooted under `media/lua/client`, not repo-root `Iris/lua`. |

### Decision

`Iris/lua/` is a tracked legacy standalone fixture, not the current runtime
authority. Register it as `action=delete` in `cleanup_candidates.md`, but do
not delete it before P0.7.

### Follow-up Gate

Before P0.7 deletion, rerun the current unit/smoke suite and confirm no
packaging or external script still consumes repo-root `Iris/lua/`.

## iris-iris

### Scope

Tracked files currently under `Iris/Iris/`:

| Path | Role observed |
|---|---|
| `Iris/Iris/media/lua/client/Iris/Data/IrisLayer3Data.lua` | nested stale Lua data copy |

### Evidence

| Check | Result |
|---|---|
| Current runtime authority | `Iris/media/lua/client/Iris/Data/IrisLayer3Data.lua` is the current deployed runtime data path referenced by `Iris/media/lua/client/Iris/Data/layer3_renderer.lua`. |
| Nested file SHA256 | `52C848E81105E62AD815B22C50D7D338C2A086F9A743213B3FBF55E0ACEA081E` |
| Runtime file SHA256 | `A108F3E5BEE473D00F4CB7DC63BADE3374670A21BC0D9B4049EDB4CA179D3162` |
| Nested/runtime size | nested `220027` bytes vs runtime `1024287` bytes |
| `Iris/output` comparison | `Iris/output/IrisLayer3Data.lua` is absent; `Iris/output/` contains older JSON/Lua build outputs such as `IrisData.lua` and indexes. |
| External references | Search excluding `Iris/Iris/**` found no active code path requiring or packaging `Iris/Iris/media/...`. Docs consistently name `Iris/media/lua/client/Iris/Data/IrisLayer3Data.lua` as workspace/runtime authority. |

### Decision

`Iris/Iris/` is not an exact duplicate of the runtime data, but it is a nested
dead path outside the active PZ loader root. Because the content is non-identical
and may be useful for forensic comparison, register it as `action=archive`
rather than `action=delete`.

### Follow-up Gate

Before P0.7 archive, confirm the packaging script excludes `Iris/_archive/` and
that runtime/package file lists are unchanged after the move.
