# Iris P0.6 Runtime Marker Checklist

This file records the marker list that must be checked in an actual PZ game run before P0.7 quarantine execution.

Current Codex execution cannot launch the game runtime, so marker observation is pending.

## Required Markers

| Marker | Source |
|---|---|
| `!!!!! IRIS BOOTSTRAP: START LOAD !!!!!` | `Iris/media/lua/client/AIrisBoot.lua` |
| `!!!!! IRIS BOOTSTRAP: IrisMain loaded successfully !!!!!` | `Iris/media/lua/client/AIrisBoot.lua` |
| `[Iris] Bootstrap complete` | `Iris/media/lua/client/AIrisBoot.lua` |
| `[Iris:IrisMain] ========== MODULE LOAD START ==========` | `Iris/media/lua/client/Iris/IrisMain.lua` |
| `[Iris:IrisMain] OnGameBoot registered` | `Iris/media/lua/client/Iris/IrisMain.lua` |
| `[Iris:IrisMain] OnCreatePlayer registered` | `Iris/media/lua/client/Iris/IrisMain.lua` |
| `[Iris:initialize] ========== INITIALIZE START ==========` | `Iris/media/lua/client/Iris/IrisMain.lua` |
| `[Iris:initialize] Step 2a: RecipeIndex.build() success` | `Iris/media/lua/client/Iris/IrisMain.lua` |
| `[Iris:initialize] Step 2b: MoveablesIndex.build() success` | `Iris/media/lua/client/Iris/IrisMain.lua` |
| `[Iris:initialize] Step 2c: FixingIndex.build() success` | `Iris/media/lua/client/Iris/IrisMain.lua` |
| `[Iris:initialize] Step 5b: hookContextMenu() success` | `Iris/media/lua/client/Iris/IrisMain.lua` |
| `[Iris:initialize] ========== INITIALIZE COMPLETE ==========` | `Iris/media/lua/client/Iris/IrisMain.lua` |

## Failure Markers

The P0.7 manual checklist must fail if the log contains `ERROR`, `traceback`, or any `FAILED to load` line for Iris modules.
