# Iris Round 1-A Scope Lock

Date: 2026-06-10

Status: Round 1-A live reference reconciliation artifact.

This file records the execution scope for Iris Round 1-A. It is a round
artifact and successor-round input, not a replacement for `docs/DECISIONS.md`,
`docs/ARCHITECTURE.md`, or `docs/ROADMAP.md`.

## Scope

Round 1-A is limited to live reference reconciliation for the exact Group A,
Group B, and Group C files named in
`docs/iris-round1-authority-live-reference-reconciliation-plan.md`.

Round 1-A does not restore archived Iris docs, does not create a full authority
manifest, and does not classify the wider archived corpus.

## Worktree File State

At Round 1-A execution start, these Group A current contract files were already
deleted in the working tree:

- `Iris/build/ENTRYPOINTS.md`
- `Iris/build/build_import_contract.md`

They were recreated in this round from the HEAD contract content, then given
Round 1-A wording repair so archived Iris docs paths read as historical labels
or inline contract provenance rather than current authority inputs. This
recreation was user-requested and is part of the current Round 1-A scope.

Group A files handled by this round:

- `Iris/build/ENTRYPOINTS.md`
- `Iris/build/build_import_contract.md`
- `Iris/_docs/refactor/phase1_active_manifest.md`

## Disposition Vocabulary

Round 1-A uses only these plan-local reference dispositions:

- `retire`
- `keep-inline`
- `re-point`
- `untouched`
- `unresolved`

These labels are operational reference labels for this round. They are not
ecosystem path-classification states.

## Special References

The historical active manifest label
`docs/Iris/phase1_active_script_manifest.txt` remains a historical reference
only in the local inventory. Round 1-A does not move, restore, or replace that
file. Future relocation can be proposed only in a successor round.

No backup-root provenance path was pinned in this round.

## Explicit Exclusions

Out of scope for this round:

- archived Iris docs restoration
- full current authority manifest creation
- broad current / historical / reproduction / stale path classification
- repo-wide rewrite of archived Iris doc strings
- staging or generated artifact cleanup
- runtime Lua, generated runtime data, package, or build behavior changes
- release, Workshop, packaging, B42, runtime equivalence, or in-game readiness

## Validation Ceiling

The validation ceiling is reference-integrity only for the current worktree
files in the exact Group A/B/C scope. Runtime, build, package, release, and
manual QA validation remain out of scope.
