# Iris P0.7 Readiness Note

Archived under `_done` by the Phase 1 v1.4 refactor doc split.

Date: 2026-05-01

Status: CLOSED. P0.7 destructive actions were executed after the runtime and
packaging gates passed.

## Scope

This note records the non-destructive P0.7 preflight for
`iris_refactor_roadmap_v2.0.md`.

P0.7 is allowed to delete `action=delete` candidates and move
`action=archive` candidates only after all gates pass. This preflight has a
dedicated Iris packaging path and a completed manual runtime marker check:

1. P0.6 requires an in-game run and console marker confirmation.
2. Any release path other than `Iris/tools/package_iris.ps1` must prove an
   equivalent `Iris/_archive/` exclusion before P0.7 can execute.

## Candidate Match

All action candidates from `cleanup_candidates.md` currently exist:

| Path | Action | Match |
|---|---|---|
| `Iris/lua/` | `delete` | yes |
| `Iris/Iris/` | `archive` | yes |
| `Iris/build/description/v2/staging/recovery/recover_missing_staging_artifacts.py` | `delete` | yes |
| `Iris/desktop.ini` | `delete` | yes |
| `.tmp/iris_backup_pre_dvf_runtime_restore_20260327_200041/Iris/desktop.ini` | `delete` | yes |
| `.tmp/iris_backup_pre_dvf_runtime_restore_20260327_200052/desktop.ini` | `delete` | yes |

No `action=preserve` path is approved for deletion or archive.

## Runtime Gate

P0.6 produced a static marker checklist at:

`Iris/build/baseline/golden/runtime_marker_checklist.md`

The actual Project Zomboid runtime marker observation was checked from:

`C:/Users/MW/Zomboid/console.txt`

Log timestamp: 2026-05-01 23:28:17

Result:

- all required Iris bootstrap and initialize markers were present;
- no Iris `ERROR`, `traceback`, or `FAILED to load` marker was found;
- one non-blocking Iris warning was present:
  `[IrisFixingIndex] WARNING: Fixing scan failed or not available yet:
  java.lang.RuntimeException`;
- `FixingIndex.build() success` was still emitted after the warning.

## Packaging Gate

The initial repository scan found no script that explicitly packaged or copied
the `Iris/` mod directory:

- root `settings.gradle` includes `Pulse`, `Echo`, `Fuse`, `Nerve`, and
  `pulse-api`, but not `Iris`;
- root and Pulse Gradle files build Java artifacts and do not package `Iris`;
- `*.gradle`, `*.ps1`, `*.bat`, and `*.cmd` search found no Iris copy/zip
  packaging path and no existing `Iris/_archive/` exclusion rule.

This change adds:

`Iris/tools/package_iris.ps1`

The script stages a release payload under `Iris/build/package/Iris` and copies
only these runtime roots:

- `mod.info`
- `poster.png` if present
- `media/`

It also records a SHA256 file manifest at:

`Iris/build/package/Iris.package_manifest.sha256.json`

The script explicitly treats these root names as forbidden package content:

- `_archive`
- `_docs`
- `build`
- `evidence`
- `input`
- `output`
- `test`
- `lua`
- `Iris`

Verification run result:

- package staging command completed successfully;
- manifest file count: 36;
- package root contains only `mod.info` and `media/`;
- no forbidden root directory was present in the staged package.

This closes the packaging gate for the `package_iris.ps1` release path. If a
different release path is used later, it must repeat this exclusion proof.

## Execution Decision

P0.7 delete/archive steps were executed after the gates above passed.

Processed actions:

| Path | Action | Result |
|---|---|---|
| `Iris/lua/` | `delete` | deleted |
| `Iris/Iris/` | `archive` | moved to `Iris/_archive/p0-2/Iris/Iris/` |
| `Iris/build/description/v2/staging/recovery/recover_missing_staging_artifacts.py` | `delete` | deleted |
| `Iris/desktop.ini` | `delete` | deleted |
| `.tmp/iris_backup_pre_dvf_runtime_restore_20260327_200041/Iris/desktop.ini` | `delete` | deleted |
| `.tmp/iris_backup_pre_dvf_runtime_restore_20260327_200052/desktop.ini` | `delete` | deleted |

Post-action package verification:

- `Iris/tools/package_iris.ps1 -Clean` completed successfully;
- staged package root contains only `mod.info` and `media/`;
- `Iris/_archive/` is not included in the package.

The baseline diff is intentionally not used as P0.7 safety proof. The roadmap
defines P0.7 as a dead-path quarantine step, so safety must come from source of
truth, packaging, smoke/build, and runtime marker evidence.
