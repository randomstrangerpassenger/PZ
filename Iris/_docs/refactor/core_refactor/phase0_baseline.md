# Iris core refactor Phase 0 baseline

- Captured at: 2026-08-02 (Asia/Seoul)
- Repository branch: `codex/1323`
- Subject commit: `72e76b367622f64af264f445889ea1832c87008a`
- Subject tree: `9c98dad4623cea9242a41b77f0e378a87e56559f`
- Execution contract: v1.3, SHA-256 `a185bbd78eb849b0310d9aadc9102cb156b892513266fac0ec7903eb3d3a9493`
- Current core closure: 12 modules
- Allowed current-route tooling: 4/4; remaining slots: 0
- Python: `C:/Users/MW/scoop/apps/python/current/python.exe`, Python 3.14.3
- Standalone Lua: `C:/Users/MW/scoop/shims/lua.exe`, PUC-Rio Lua 5.4.8 (auxiliary only)
- Lua compiler: `C:/Users/MW/scoop/shims/luac.exe`, PUC-Rio Lua 5.4.8
- PZ executable: `G:/Program Files (x86)/Steam/steamapps/common/ProjectZomboid/ProjectZomboid64.exe`
- PZ runtime: Steam `legacy41`; latest console identity `41.78.20`

## Pre-existing dirty paths excluded from the refactor diff

- `docs/ARCHITECTURE.md`
- `docs/DECISIONS.md`
- `docs/ROADMAP.md`
- `docs/dvf_3_3_validated_naturalization_current_runtime_adoption_plan.md`
- `.worktrees/dvf-acquisition-list-runtime/`
- `docs/iris_core_refactoring_consolidated_plan.md`
- `graphify-out/.graphify_detect.json`
- `graphify-out/.graphify_python`
- `graphify-out/.graphify_root`

These paths belong to the pre-existing worktree and are not implementation inputs except for the authority documents explicitly named by the approved plan. They must not be staged with this refactor.

## Authority readpoint

The current runtime authority is `IrisLayer3DataChunks.lua` plus `Chunk001.lua` through `Chunk011.lua`. Facts, decisions, rendered JSON, historical/probe material, and the existing package are not runtime read paths. The existing package peer is read-only and stale relative to the live chunks; Phase 0 records that mismatch without rewriting the package.

`docs/EXECUTION_CONTRACT.md` supplies disclosure, claim/evidence binding, validation-ceiling, and closeout obligations only. It does not become Iris module architecture authority.

## Execution ceiling

Standalone Lua evidence is auxiliary. Numeric formatting, `unpack` behavior, Java/Kahlua invocation, food values, and UI widget behavior require PZ/Kahlua evidence. No B42, multiplayer, soak, release, deployment, or third-party-mod compatibility claim is in scope.

