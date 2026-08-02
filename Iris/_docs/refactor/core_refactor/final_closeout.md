# Iris Core Refactor Integrated Closeout

## Scope and state

This closeout covers the mandatory core refactor Changes 1–6, the Change 7
`deferred_by_design` disposition, and the Change 8 no-op repository disposition.
The implementation is complete, but the integrated final validation batch did
not satisfy the repository-wide current, historical, and full-discovery gates.
The generation-7 manifest therefore remains fail-closed and unsealed; the
post-seal CleanCheckout and terminal binding were not started.

Plan-specific state: `blocked_integrated_validation`.
Standard closeout state: `blocked`.

Reason codes:

- `blocked_current_route_validation_failed`
- `blocked_historical_route_validation_failed`
- `blocked_full_v2_discovery_failed`

## Delivered changes

- Description string output now derives from the block API.
- Browser selection fallback and BrowserData cache/build states are explicit.
- Browser and Wiki detail presentation share a read-only fact model; wheel
  scrolling repositions existing widgets instead of rebuilding them.
- Legacy `IrisData` access and Browser variant compatibility are isolated behind
  named adapters.
- Build-tool decomposition is `deferred_by_design`: current core remains 12,
  allowed tooling remains 4/4, and no unapproved slot was created.
- Repository cleanup is a no-op: zero paths met the deletion predicate.

## Validation axes

Runtime behavior, build contracts, package identity, public-text/protected
identity, supported API compatibility, Lua syntax, and route classes are
separate claims. No bare `PASS` is interpreted as release readiness, B42
compatibility, multiplayer/soak coverage, or compatibility with unknown
external consumers.

The pre-refactor denominator remains separate from owner-specific post-refactor
acceptance. PZ/Kahlua B41 evidence exists for Changes 3–6; standalone Lua rows
remain auxiliary where the dialect relation is not sufficient.

The final batch produced these separate outcomes:

- PZ/Kahlua B41 acceptance: validated for Description 4, Browser 7, Detail 4,
  and Legacy 3 cases against implementation commit `60a919f0`.
- Standalone auxiliary characterization: 15 rows passed against baseline
  `72e76b36` with a reconstructable four-row producer overlay.
- PZ pre-refactor characterization: 9 rows passed against baseline `72e76b36`
  with a reconstructable five-row producer overlay.
- Production Lua syntax: 95 files passed.
- Disposable package identity: 95 Lua files and 12 Layer 3 files passed; the
  candidate was removed and the existing 102-row package peer was unchanged.
- Current route: 135 tests ran with 1 failure and 2 errors, including stale DVF
  review/package bindings and a registry-closure parse failure.
- Historical route: import failed at
  `test_post_cleanup_phase2_adoption_validation.py:220`.
- Diagnostic route (advisory): 81 tests ran with 3 source-contract failures in
  ignored local tests that predate the shared detail model boundary.
- Full v2 discovery: 806 tests ran in 1088.098 seconds with 33 failures and 43
  errors. The run exposed existing DVF artifact/contract drift, a Windows output
  path error, and non-hermetic test writers. Its 97 tracked side effects were
  restored to HEAD without touching scoped refactor or user changes.

## Conditional branches

- Change 7 build decomposition: `deferred_by_design`, standard state `complete`.
- Change 8 cleanup: `no_op`, standard state `complete`.
- Generator full removal and global alias removal were not selected. Their
  compatibility facades remain intentionally supported.

## Seal sequence disposition

1. Stage and validate the fail-closed generation-7 manifest and its validator.
2. Commit the implemented closeout with the mandatory failures recorded.
3. Do not run CleanCheckout while the manifest is unsealed or a mandatory axis
   is unvalidated.
4. Do not create `final_evidence_binding_report.json`; that record is valid only
   after a successful seal-candidate CleanCheckout.

Re-entry requires resolving the three blocking route/discovery axes, rerunning
the final matrix, changing all 73 required rows from `required_active` to
`sealed`, setting the root and ceiling seal, then performing the exact committed
CleanCheckout and terminal attestation sequence.

External Codex Reviewer status: `reviewer_remediation_applied_pending_final_read_only_verdict`. The review
identified incomplete CleanCheckout coverage, weak evidence identity checks, an
incorrect subcategory getter, shallow nested mutability, and non-disjoint result
roots. The implementation incorporates the requested corrections; Changes 3–6
PZ evidence was regenerated from clean implementation commit `60a919f0` with a
reconstructable producer-input binding. A follow-up review identified missing
reconstruction rows in the two Phase 1 bindings and a self-authorizing
protected report. Both were remediated by replaying baseline `72e76b36` in a
disposable checkout and by pinning exact owner authority to ancestor commit
`dd732e1f` and blob `7aebc178` rather than trusting the report itself.

One protected governance file has an approved exact change. Baseline commit
`72e76b36` advanced `current_generation_descriptor.json` but left
`current_route_required_validations.json` bound to the preceding descriptor.
Change 9 updates only that repeated SHA-256 binding to the tracked descriptor;
the protected report records changed 1, approved 1, unauthorized 0. Runtime,
source facts/decisions/rendered text, chunks, and the existing package peer are
unchanged.
