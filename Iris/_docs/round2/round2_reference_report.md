# Round 2 Reference And Search Report

Generated: 2026-06-10T16:02:18.031154+00:00

All accepted scans are root-by-root. Multi-root `rg` output is not used as authority evidence.

## Staging Reference Scan

Pattern: `Iris/build/description/v2/staging|staging/`

| mode | root | exit_code | count |
| --- | --- | --- | --- |
| default | Iris | 0 | 1131 |
| default | docs | 0 | 64 |
| default | tools | 1 | 0 |
| default | .gitignore | 0 | 26 |
| full_tree | Iris | 0 | 75930 |
| full_tree | docs | 0 | 64 |
| full_tree | tools | 1 | 0 |
| full_tree | .gitignore | 0 | 26 |

## Fixed Token Search Metrics

Pattern: `layer4_boundary|legacy_active_silent|interaction_cluster|weak_active_cleanup`

| mode | root | exit_code | count |
| --- | --- | --- | --- |
| default | Iris | 0 | 360 |
| default | docs | 0 | 43 |
| default | tools | 1 | 0 |
| default | .gitignore | 0 | 5 |
| full_tree | Iris | 0 | 53461 |
| full_tree | docs | 0 | 43 |
| full_tree | tools | 1 | 0 |
| full_tree | .gitignore | 0 | 5 |

## Canaries

- Default-search staging/archive canaries are hidden by `.rgignore` unless an explicit path or `-uu` search is used.
- Archived boundary canary: `Iris/_archive/staging/compose_contract_migration/layer4_boundary_current_corpus_lock_round/layer4_boundary_current_corpus_lock_closeout.md`
- Kept staging full-tree canary: `Iris/build/description/v2/staging/interaction_cluster/interaction_cluster_build_report.json`

## Reduction

- Staging files: 783 -> 698
- Staging bytes: 106664635 -> 32078467
- Original Round 2 baseline before adding `staging/README.md`: 782 files / 106664169 bytes
- Moved bytes: 74586168
- Default `rg` excludes staging/archive through `.rgignore`; use `rg -uu` for forensic scans.
