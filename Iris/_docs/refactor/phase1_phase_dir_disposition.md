# Iris Refactor Phase 1 Phase Directory Disposition

Date: 2026-05-04

This file closes the roadmap's verify-first gate for
`Iris/build/phase0_validation/` through `Iris/build/phase4_tests/`.

## Rule

No phase directory is treated as empty or disposable by directory name. A file
is active when `main.py`, `ENTRYPOINTS.md`, tests, pipeline tools, direct path
execution, or documented commands still import or execute it.

## Inventory

| Directory | Files | Disposition | Evidence |
|---|---:|---|---|
| `phase0_validation` | 5 | active | `main.py` imports schema, allowlist, and evidence table validation. |
| `phase1_extraction` | 8 | active | `main.py`, root tests, and `tools/pipeline/context_outcomes_main.py` import extraction modules. |
| `phase2_rules` | 7 | active | `main.py`, root tests, and context-outcome tools import rules, predicates, blocklist, and manual injection. |
| `phase3_output` | 6 | active | `main.py` and context-outcome tools import output generation and validators. |
| `phase4_tests` | 4 | active | `main.py` imports golden extractor and regression test runner. |

## Disposition result

| Disposition | Count |
|---|---:|
| active | 30 |
| relocated_duplicate | 0 |
| oneshot_archive | 0 |
| delete_candidate | 0 |

## Gate result

The phase directory cleanup gate is blocked for delete/archive and closed for
inventory. Any future relocation must first replace the active imports and run
the root build/test smoke suite.
