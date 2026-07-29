# DVF 3-3 Current Facts Correction Successor Contract

## Status and scope

This contract authorizes one append-only correction successor rooted at
`correction-0001` and one Registry correction cutover rooted at
`attempt-0010`.

The correction is opened by the immutable Codex Reviewer `FAIL` for
Naturalization `attempt-0018-g3-reseal-a`. That Naturalization attempt remains
blocked and Phase 7/8 re-entry is forbidden.

## Immutable predecessors

The following evidence is read-only:

- Food semantic facts-authority `attempt-0022`;
- Registry operational-cutover `attempt-0009`;
- the first G3 Registry adoption receipt;
- Naturalization `attempt-0018-g3-reseal-a`.

No correction may rewrite, delete, reclassify, or replace those artifacts.

## Cohort rule

The correction intake must screen all 2,105 current facts. For every Reviewer
seed it must retain separate denominators for:

- the exact field-generation rule;
- every row with the same selected interaction cluster, regardless of role;
- the exact fact-origin class.

Because every current acquisition hint has `seed` origin, origin alone is not
a narrowing predicate. The report therefore records the full 2,105-row origin
screen separately from the deduplicated rule/cluster investigation cohort.
The sealed origin screen is 2,105 acquisition `seed` rows and, for
`primary_use`, 1,275 `cluster_summary`, 718 `identity_fallback`, 100
`role_fallback`, and 12 `direct_use` rows.

The final correction denominator is the count of rows whose semantic fields
actually change after the full cohort review. Unchanged cohort members remain
explicit controls and are not silently omitted from the inventory. The
Reviewer-confirmed conservative cohort contains 393 unique rows: 184 corrected
items and 209 unchanged investigated controls.

## Successor and cutover

The successor must:

- preserve the 2,105 item-id universe and row order;
- preserve unchanged rows byte-for-byte;
- bind every changed field to an exact predecessor value, replacement value,
  rule id, cohort id, reason, and repository evidence;
- preserve all Food semantic propositions and G2 lineage;
- remain non-current until Registry cutover.

Registry cutover must use an exclusive lock, one-use owner authorization,
rollback snapshots, facts-first/manifest-last replacement, post-write hash
verification, and an append-only correction adoption receipt. This is a
process-crash-recoverable two-file transaction; it does not claim a single
filesystem primitive or power-loss atomicity.

## Downstream boundary

After correction adoption, G4 readiness receives an additive binding to the
new current facts/manifest and correction receipt. A fresh Naturalization
attempt may then begin at Phase 0 and must include compiler fix
`b399cdbacf884ed97a884e8a0266f94a7e4a13d5`.

Official Publish creation and live Publish gate mutation remain forbidden
until a new Naturalization Phase 8 handoff is complete.
