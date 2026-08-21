# Iris Layer 4 adaptive interaction density presentation completion Walkthrough

Date: 2026-08-21

Closeout state: `implemented_only`

## 1. Successor subject

This is the successor record for the previously `partial` Layer 4 execution.
It does not replace the adopted plan, the owner policy decision, or the
historical partial closeout.

The implementation sequence is:

- `6cd9c3ec` — complete and safely install the Layer 4 runtime projection
- `4ebcfe1c` — add the QG-only adaptive Browser presentation
- `4e14871c` — merge current `main` non-destructively before final validation
- `21f6115a` — align the adopted validation suite with the integrated subject
- `a4a8fb90` — add the plan-required PZ density acceptance bridge and named anchors

No push was performed. `DECISIONS.md`, `ARCHITECTURE.md`, and `ROADMAP.md`
were not promoted because independent review and the final owner canonical
seal are still absent.

## 2. Layer 4 generation and installation

The installed projection is produced from the adopted description/QG sources
as one complete 13-file universe: the facade, nine chunks,
`RequirementsLookup.lua`, `ChunkIndex.lua`, and `LineCountIndex.lua`.
Generation is deterministic, the guarded updater validates before and after
apply, restores the predecessor on a post-apply failure, and returns `no-op`
when the installed bytes already match.

The installed projection contains:

- 1,631 FullTypes
- 877 positive interaction rows
- 791 Recipe rows
- 321 unique Recipe identities
- nine data chunks

Every Recipe row carries a stable `recipe_id`, and its
`recipe_nav_ref.recipe_id` matches. The installed reapply was a no-op. The
disposable package carried the same 13-file bytes as the live projection.
This is runtime/package projection validation, not publication or Workshop
readiness.

## 3. Adaptive Browser presentation

The Browser now consumes only the status-bearing QG interaction projection.
The legacy capability and Recipe-index presentation fallbacks are no longer
presentation inputs. Verified empty and lookup fault remain distinct.

The private presentation policy is:

- 0 rows: verified-empty presentation
- 1 row: immediately open
- 2 through 8 rows: all rows open
- 9 or more rows: compact initially, with lossless full view and literal search

Recipe and Right-click remain peer Sources in fixed Recipe-then-Right-click
order. Total and Source counts are preserved. Search does not change the total
or base order, duplicate display labels retain distinct identities, and blank,
duplicate, unknown-surface, or mismatched navigation identities fail closed.
State is scoped by Browser generation, locale, and FullType; item, locale, or
generation changes invalidate stale query/fold/callback state.

Recipe requirements remain row-local and navigation remains bound to the
stable Recipe identity. KO/EN control text is generated through the existing
translation producer. An unrepresentable selected-locale requirement does not
fall back to raw text from another locale. Normalized external rows use the
same contract; raw external text is not semantically inferred.

The three newly visible QG-only identities are exactly:

- `Base.BallPeenHammer / uc.action.construction`
- `Base.GardenSaw / uc.action.wood_cutting`
- `Base.HammerStone / uc.action.construction`

The current named density anchors are `Base.223BulletsMold = 1` positive Recipe
row with three requirement atoms and `Base.Tongs = 33` positive Recipe rows.
`IrisBrowserTheme.lua` was not changed, so no new theme token was introduced.
Tooltip and Layer 3 product behavior were not changed by the Layer 4
implementation.

## 4. Required validation results

| Axis | Exit | Result |
|---|---:|---|
| Gate 5 focused generation tests | 0 | `4 passed`; deterministic A/B generation, validator rejection, guarded apply/no-op, rollback. |
| Adaptive presentation plus Gate 5 focused suite | 0 | `9 passed` before the PZ bridge addition; the final adaptive focused suite is `6 passed`. |
| V1 interaction contract | 0 | `14 passed`; Gate 3 remains `capability_only=0`, `recipe_only=0`, `qg_only=3`, no contract errors. |
| V2 detail ViewModel current/diagnostic/historical | 0 | `3 passed`. |
| V3 exact current Round 3 denominator | 0 | `471 passed, 1 skipped, 190 deselected, 124 subtests passed`. The skip is the adopted zero-consumer tooling-receipt disposition. |
| V4 production/package Lua syntax | 0 | `Lua syntax validation OK: 131 files`. |
| Current Gate 5 stateless validator | 0 | 1,631 FullTypes, 13 files, 877 positive rows, 791 Recipe rows, 321 Recipe identities. |
| V5 actual PZ Kahlua runtime | 1 | `ProjectZomboid64.exe` launched but the exact harness timed out after 240 seconds. The final run had the required bridge installed; no evidence rows were produced. `BLOCKED`. |
| V6 disposable package | 0 | `candidate_lua=131`, 12 Layer 3 payload files, existing package peer unchanged. |
| Layer 4 disposable package/live parity | 0 | The existing Gate 5 validator accepted the temporary package and live parity root with the same 13-file metrics. The temporary root was deleted. |
| Manual 12-case in-game matrix | — | Not performed; `unvalidated_but_in_scope`. |

No standalone/mock result is credited as a PZ runtime PASS. No additional
validator, receipt, manifest, seal, or validation-of-validation artifact was
introduced for closeout.

## 5. V7 and claim ceiling

V7 is `stale_due_to_layer4_change`. The preserved IPS snapshot's Layer 4
representation is affected by the generated runtime changes in `6cd9c3ec` and
the Browser projection/cutover changes in `4ebcfe1c`; those Git subjects bind
the exact affected path/blob set without creating another manifest. The IPS
evaluator was not restored or rerun, and this disposition is not an updated
information-sufficiency result.

Validated scope is the installed Layer 4 projection, QG-only adaptive
presentation, KO/EN projection contract, exact automated denominator, Lua
syntax, and disposable package parity. Out of scope are QG fact changes,
Layer 3/Tooltip redesign, IPS reassessment, performance, multiplayer,
all-locale/all-resolution support, publication, release, and deployment.

`unvalidated_but_in_scope` contains the actual PZ Kahlua runtime axis and all
12 manual in-game cases. Independent review and final owner canonical seal are
also pending. Therefore this subject is `implemented_only`, not `complete`,
canonical, sealed, or release-ready.
