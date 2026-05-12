# Iris P0.7 Execution Note

Archived under `_done` by the Phase 1 v1.4 refactor doc split.

Date: 2026-05-01

## Runtime Marker Evidence

Source log: `C:/Users/MW/Zomboid/console.txt`

Log timestamp: 2026-05-01 23:28:17

Required marker line references:

| Marker | Line |
|---|---:|
| `!!!!! IRIS BOOTSTRAP: START LOAD !!!!!` | 1283 |
| `[Iris:IrisMain] ========== MODULE LOAD START ==========` | 1285 |
| `[Iris:IrisMain] OnGameBoot registered` | 1292 |
| `[Iris:IrisMain] OnCreatePlayer registered` | 1294 |
| `!!!!! IRIS BOOTSTRAP: IrisMain loaded successfully !!!!!` | 1296 |
| `[Iris] Bootstrap complete` | 1297 |
| `[Iris:initialize] ========== INITIALIZE START ==========` | 1392 |
| `[Iris:initialize] Step 2a: RecipeIndex.build() success` | 1399 |
| `[Iris:initialize] Step 2b: MoveablesIndex.build() success` | 1402 |
| `[Iris:initialize] Step 2c: FixingIndex.build() success` | 1418 |
| `[Iris:initialize] Step 5b: hookContextMenu() success` | 1435 |
| `[Iris:initialize] ========== INITIALIZE COMPLETE ==========` | 2347 |

Failure scan result:

- no Iris `ERROR` line found;
- no `traceback` line found;
- no Iris `FAILED to load` line found;
- one non-blocking warning found at line 1417:
  `[IrisFixingIndex] WARNING: Fixing scan failed or not available yet:
  java.lang.RuntimeException`.

## Quarantine Actions

| Path | Action | Result |
|---|---|---|
| `Iris/lua/` | delete | removed |
| `Iris/Iris/` | archive | moved to `Iris/_archive/p0-2/Iris/Iris/` |
| `Iris/build/description/v2/staging/recovery/recover_missing_staging_artifacts.py` | delete | removed |
| `Iris/desktop.ini` | delete | removed |
| `.tmp/iris_backup_pre_dvf_runtime_restore_20260327_200041/Iris/desktop.ini` | delete | removed |
| `.tmp/iris_backup_pre_dvf_runtime_restore_20260327_200052/desktop.ini` | delete | removed |

## Packaging Verification

Command:

`Iris/tools/package_iris.ps1 -Clean`

Result:

- package staging succeeded;
- package root: `Iris/build/package/Iris`;
- package manifest: `Iris/build/package/Iris.package_manifest.sha256.json`;
- staged root contains only `mod.info` and `media/`;
- forbidden roots including `_archive`, `_docs`, `build`, `input`, `output`,
  `lua`, and nested `Iris` were not included.
