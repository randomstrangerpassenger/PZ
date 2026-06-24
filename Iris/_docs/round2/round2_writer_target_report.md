# Round 2 Writer Target Report

Generated: 2026-06-10T16:02:18.031154+00:00

This report is conservative: a staging family mentioned by current build tools or tests is treated as a live-writer candidate until explicitly re-pointed or kept current.

## Keep-Current Families

| candidate | decision | reason |
| --- | --- | --- |
| body_role | keep-current | current body-role tests/tools reference staging inputs |
| compose_contract_migration/full_runtime | keep-current | current compose runtime gates reference full_runtime outputs |
| identity_fallback_source_expansion | keep-current | current authority-promotion tooling references staging inputs |
| interaction_cluster | keep-current | current tests/builders reference interaction cluster staging outputs |
| manual_in_game_validation | keep-current | tracked manual QA evidence remains versioned |
| semantic_quality | keep-current | semantic-quality tooling still names staging inputs |
| source_coverage | keep-current | current source coverage package builders reference staging outputs |
| source_expansion_distribution_remeasurement_gate | keep-current | source expansion distribution remeasurement build scripts reference this staging family |
| weak_active_cleanup | keep-current | weak-active cleanup reports and tests still reference staging outputs |

## Archived Families

| path | decision | reason |
| --- | --- | --- |
| `compose_contract_migration/layer4_boundary_current_corpus_lock_round` | summarize-then-archive | sealed historical evidence; no direct current tool/test dependency found |
| `compose_contract_migration/structural_signal_scope_re_seal_round` | summarize-then-archive | sealed historical evidence; no direct current tool/test dependency found |
| `compose_contract_migration/layer4_confirmed_detector_field_map_reseal_round` | summarize-then-archive | sealed historical evidence; no direct current tool/test dependency found |

## Search Surface Decision

Default search excludes both kept-current staging and local-cold archive paths. Current tooling uses explicit paths; humans and Codex should use `Iris/_docs/round2/STAGING_INDEX.md` first and `rg -uu` only for forensic trace work.
