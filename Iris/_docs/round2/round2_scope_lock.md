# Round 2 Scope Lock

Generated: 2026-06-10T15:46:56.460270+00:00

## Scope

Round 2 is limited to staging-retention and artifact-disposition governance for `Iris/build/description/v2/staging/**`, `Iris/staging/**`, and the Round 2 docs/reports needed to preserve traceability.

## Non-Claims

This scope does not claim runtime behavior change, runtime equivalence, package build, release readiness, Workshop readiness, B42 readiness, Layer4 resolved state, semantic-quality completion, or acquisition lexical expansion.

## Classification Vocabulary

- `current`: live writer, execution, validation, or current contract dependency.
- `historical`: closed readpoint, predecessor evidence, or manual validation evidence kept for trace.
- `reproduction`: generated, staging, or replay evidence that is not current authority by path existence.
- `stale`: superseded or empty remnant that is not current authority.

## Disposition Vocabulary

- `keep-current`
- `promote`
- `keep-evidence`
- `summarize-then-archive`
- `archive`
- `delete`
- `unresolved`

## Durability Labels

- `local-cold-archive`: raw files moved out of default Git/search surface but not Git-preserved for fresh clones.
- `versioned-summary`: Git-tracked summary, manifest, hash ledger, or closeout pointer.
- `versioned-raw-archive`: explicitly Git-tracked raw archive exception.
- `external-or-manual-archive`: out-of-repo preservation with recorded owner/location.

## Metric Protocol

The fixed token set is `layer4_boundary|legacy_active_silent|interaction_cluster|weak_active_cleanup`. Metrics are root-by-root for `Iris`, `docs`, `tools`, and `.gitignore`, in both default and `-uu` modes, with canary checks. Multi-root `rg` is not accepted as authority evidence.

## Precondition State

Physical archive/delete and authority-manifest mutation are blocked in this pass because the current worktree contains dirty and untracked prerequisite surfaces, including `Iris/_docs/authority/**`, `Iris/_docs/round1a/**`, Round 2 plan files, and broad predecessor doc deletions. This is recorded as `unresolved`, not as a complete Round 2 closeout.

## Official Guard Baseline Route

The legacy active/silent guard baseline uses a validator code repair that enumerates scan roots separately. The known `ENTRYPOINTS.md:151` and `INVENTORY.md:302` findings were reworded, and the repaired run is recorded in `round2_guard_baseline_report.md`.
