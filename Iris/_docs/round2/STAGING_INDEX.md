# Iris Round 2 Staging Index

This index is a compact readpoint for Iris Round 2 staging disposition. It does not promote staging to current authority and does not make runtime, package, release, Workshop, B42, or semantic-quality claims.

Generated: 2026-06-10T16:02:18.031154+00:00

## Scope

- `Iris/build/description/v2/staging/**`
- `Iris/_archive/staging/**` local-cold archive
- `Iris/staging/**` empty or stale remnants
- Round 2 reports under `Iris/_docs/round2/**`

## Summary

- Before staging files: 783
- Before staging size: 106664635 bytes
- Original Round 2 baseline before adding this directory README: 782 files / 106664169 bytes
- After staging files: 698
- After staging size: 32078467 bytes
- Local-cold archive files: 85
- Local-cold archive size: 74586168 bytes
- Files moved this pass: 85
- Bytes moved this pass: 74586168
- Git-tracked files still under staging root: 89
- Default search surface: staging and `Iris/_archive/**` excluded by `.rgignore`; explicit path search or `rg -uu` remains available.
- Current authority rule: staging path existence is not authority. Staging families marked `keep-current` remain only because current tests/build tooling still reference them.

## Archived Raw Evidence

- `Iris/build/description/v2/staging/compose_contract_migration/layer4_boundary_current_corpus_lock_round` -> `Iris/_archive/staging/compose_contract_migration/layer4_boundary_current_corpus_lock_round`
- `Iris/build/description/v2/staging/compose_contract_migration/structural_signal_scope_re_seal_round` -> `Iris/_archive/staging/compose_contract_migration/structural_signal_scope_re_seal_round`
- `Iris/build/description/v2/staging/compose_contract_migration/layer4_confirmed_detector_field_map_reseal_round` -> `Iris/_archive/staging/compose_contract_migration/layer4_confirmed_detector_field_map_reseal_round`

## Staging Family Inventory

| family | files | size_bytes | tracked | generators | writer_candidate |
| --- | --- | --- | --- | --- | --- |
| staging_root_readme | 1 | 466 | 0 | 0 | no |
| acquisition_lexical_current_readpoint_reconciliation_round | 23 | 631336 | 0 | 1 | no |
| body_role | 1 | 1835 | 0 | 0 | yes |
| compose_contract_migration | 101 | 7048227 | 54 | 1 | yes |
| identity_fallback_source_expansion | 42 | 113686 | 0 | 0 | yes |
| interaction_cluster | 71 | 11682687 | 0 | 0 | yes |
| manual_in_game_validation | 35 | 105889 | 35 | 0 | yes |
| semantic_quality | 2 | 1613 | 0 | 0 | yes |
| source_coverage | 357 | 7483624 | 0 | 0 | yes |
| source_expansion_distribution_remeasurement_gate | 32 | 62318 | 0 | 0 | yes |
| weak_active_cleanup | 33 | 4946786 | 0 | 0 | yes |

## Archive Family Inventory

| family | files | size_bytes | tracked | generators |
| --- | --- | --- | --- | --- |
| compose_contract_migration | 85 | 74586168 | 0 | 3 |

## Related Artifacts

- `round2_file_inventory.jsonl` records the original file-level path, size, sha256, tracked state, and risk markers.
- `round2_staging_disposition_ledger.jsonl` records family/directory-level classification and operational disposition.
- `round2_move_ledger.jsonl` records hash-verified local-cold archive moves.
- `round2_delete_quarantine_ledger.jsonl` records empty-directory prune markers, if any.
- `round2_reference_report.md` records root-by-root reference scans and search metric results.
- `round2_writer_target_report.md` records staging writer-target candidates and keep-current decisions.
- `round2_guard_baseline_report.md` records the deterministic legacy active/silent guard baseline.
