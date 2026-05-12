# Iris Cleanup Candidates

Archived under `_done` by the Phase 1 v1.4 refactor doc split.

This is the P0 manifest from `iris_refactor_roadmap_v2.0.md`. P0 only records
candidate actions. P0.7 is the first phase allowed to delete or move files.

Before auditing P0.7, read `p0_7_readiness.md`. The P0.7 execution is complete.
The packaging gate is closed only for the `Iris/tools/package_iris.ps1` release
path.

## Action Semantics

| Action | Meaning |
|---|---|
| `delete` | Remove in P0.7 after gates pass. |
| `archive` | Move to `Iris/_archive/<phase>/<original_relative_path>` in P0.7 after gates pass. |
| `preserve` | Intentionally keep; recorded so later reviews can distinguish deliberate preservation from omission. |

## Candidates

| Path | Action | Phase | Evidence |
|---|---|---|---|
| `Iris/lua/` | `delete` | P0-1 | Dead repo-root Lua fixture; see `source_of_truth_inventory.md#iris-lua`. |
| `Iris/Iris/` | `archive` | P0-2 | Nested stale non-identical runtime-data copy; see `source_of_truth_inventory.md#iris-iris`. |
| `Iris/build/description/v2/staging/body_role/` | `preserve` | P0-3 | Ignored staging output group, 1 file. Referenced by build tooling paths; no deletion decision in P0. |
| `Iris/build/description/v2/staging/compose_contract_migration/` | `preserve` | P0-3 | Ignored staging output group, 45 files. Active build tooling references this staging root. |
| `Iris/build/description/v2/staging/identity_fallback_source_expansion/` | `preserve` | P0-3 | Ignored staging output group, 42 files. Active validation/build tooling references this staging root. |
| `Iris/build/description/v2/staging/interaction_cluster/` | `preserve` | P0-3 | Ignored staging output group, 70 files. Active validation/build tooling references this staging root. |
| `Iris/build/description/v2/staging/recovery/recover_missing_staging_artifacts.py` | `delete` | P0-3 | One-off recovery helper created for restoration; no active build reference found. |
| `Iris/build/description/v2/staging/semantic_quality/` | `preserve` | P0-3 | Ignored staging output group, 2 files. Active quality tooling references this staging root. |
| `Iris/build/description/v2/staging/source_coverage/` | `preserve` | P0-3 | Ignored staging output group, 357 files. Active report/build tooling references this staging root. |
| `Iris/build/description/v2/staging/source_expansion_distribution_remeasurement_gate/` | `preserve` | P0-3 | Ignored staging output group, 32 files. Current docs and tooling reference this gate output. |
| `Iris/desktop.ini` | `delete` | P0-5 | OS metadata file. |
| `.tmp/iris_backup_pre_dvf_runtime_restore_20260327_200041/Iris/desktop.ini` | `delete` | P0-5 | OS metadata file under temporary backup. |
| `.tmp/iris_backup_pre_dvf_runtime_restore_20260327_200052/desktop.ini` | `delete` | P0-5 | OS metadata file under temporary backup. |

## P0 Probe Notes

| Probe | Result |
|---|---|
| `git ls-files Iris/build/description/v2/staging` | No tracked files currently listed under staging. |
| `git ls-files -o -i --exclude-standard Iris/build/description/v2/staging` | 550+ ignored files, grouped above by top-level staging directory. |
| `*.pyc` discovery | No accessible `*.pyc` candidates were found during P0. Several old temp directories denied traversal and must be handled separately if they remain relevant. |
| `desktop.ini` discovery | 3 candidates listed above. |
