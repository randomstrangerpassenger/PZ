# Round 2 Closeout

Generated: 2026-06-10T16:02:18.031154+00:00

## State

`complete-for-selected-disposition-scope`

Round 2 now has a versioned compact index, file inventory, disposition ledger, move ledger, default-search exclusion, and a local-cold archive for sealed historical compose-contract evidence. Live writer/test candidates are explicitly marked `keep-current` instead of being silently moved.

## Completed

- Default search excludes `Iris/build/description/v2/staging/**` and `Iris/_archive/**` via `.rgignore`.
- 85 files / 74586168 bytes moved from staging to `Iris/_archive/staging/**` with sha256 ledger rows.
- Empty stale staging directories were pruned with quarantine marker rows where applicable.
- Layer4 absorption guard explicitly allows `Iris/_archive/**` as historical archive evidence.
- `.gitignore` no longer whitelists archived sealed compose-contract rounds.

## Kept Current By Reference

- `interaction_cluster`, `source_coverage`, `weak_active_cleanup`, `identity_fallback_source_expansion`, `semantic_quality`, `body_role`, `source_expansion_distribution_remeasurement_gate`, and selected `compose_contract_migration` live subdirs remain in staging because current tools/tests still reference them.
- `layer4_trace_edge_authority_admission_round` remains because a current pytest imports its generator.
- `legacy_active_silent_current_surface_guard_round` remains because current guard validation still consumes its manifest.

## Non-Claims

This closeout does not claim runtime equivalence, deployment, package readiness, release readiness, Workshop readiness, B42 readiness, or semantic-quality completion.
