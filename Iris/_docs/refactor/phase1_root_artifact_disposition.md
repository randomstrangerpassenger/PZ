# Iris Refactor Phase 1 Root Artifact Disposition

Date: 2026-05-05

Historical source roadmap label: `docs/Iris/iris-refactoring-final-roadmap-v1.md`

This record closes the Phase 1 root intermediate artifact move without
overwriting active build outputs. Root artifacts that were historical snapshots
or worksheets were moved to typed locations. Root files that are still active
metadata remain at the Iris root.

## Moved artifacts

| Former root path | New path | Disposition |
|---|---|---|
| `Iris/context_outcomes.json` | `Iris/output/legacy_root/context_outcomes.json` | legacy output snapshot |
| `Iris/diagnostics.json` | `Iris/output/legacy_root/diagnostics.json` | legacy output snapshot |
| `Iris/extraction_stats.json` | `Iris/output/legacy_root/extraction_stats.json` | legacy extraction stats snapshot |
| `Iris/scope_outside_fulltypes.json` | `Iris/output/legacy_root/scope_outside_fulltypes.json` | legacy coverage output snapshot |
| `Iris/source_scan_targets.json` | `Iris/input/legacy_root/source_scan_targets.json` | legacy source scan worksheet |
| `Iris/subcategory_analysis.md` | `Iris/evidence/analysis/subcategory_analysis.md` | evidence analysis worksheet |

## Root files intentionally kept

| Root path | Reason |
|---|---|
| `Iris/iris-input-schema-v0.2-final.meta.json` | schema/meta contract file |
| `Iris/mod.info` | Project Zomboid mod metadata |

## Compatibility notes

- `Iris/output/context_outcomes.json`, `Iris/output/diagnostics.json`, and
  `Iris/output/scope_outside_fulltypes.json` already existed and are treated as
  active output paths. The root snapshots were moved under `legacy_root/`
  instead of replacing those files.
- `Iris/build/tools/pipeline/context_outcomes_main.py` already writes context
  outcomes and diagnostics under `Iris/output/`.
- `Iris/build/tools/oneshots/analyze_subcategory_groups.py` now writes
  `subcategory_analysis.md` directly under `Iris/evidence/analysis/`.
- Historical docs that cite the `2281` extraction baseline now reference
  `Iris/output/legacy_root/extraction_stats.json`.

## Verification

- `rg` no longer finds active docs references that treat
  `Iris/extraction_stats.json` as a live root file.
- The Iris root now contains only `iris-input-schema-v0.2-final.meta.json` and
  `mod.info` as files.
