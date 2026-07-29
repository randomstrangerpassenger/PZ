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

## Append-only correction successor 0002

This section extends, and does not rewrite, the sealed `correction-0001` /
`attempt-0010` adoption above. It authorizes exactly one new Registry
correction cutover:

- input commit:
  `ea38a238bef5d7e7e283b03adcef22e0bae31e50`;
- input tree:
  `052edaf9ebf2f8fa5484b4d27e535db59450c61a`;
- successor id: `correction-0002`;
- Registry cutover attempt: `attempt-0011`;
- successor facts SHA-256:
  `37db2595eff9b58f7b08e59221e950cb529453bd96733fb29171d458e46118f6`;
- sealed non-current successor manifest SHA-256:
  `e5ccc87ad00e3c8f009ad79a294ea771046d16e12a3582908bcb813545e7e63e`;
- successor receipt SHA-256:
  `5d01e7c6d19336ed5231163060e636ad45ff6a79cc6f40faf971a89d4f8810fe`;
- predecessor current facts SHA-256:
  `ca74270191289af064d9d8fa9d739c97b0865d69e255885e815b01565243f46e`;
- predecessor current manifest SHA-256:
  `c9670c1625382444fe292158e6b50e65e2ee54316d2903835ebc4f59c199257d`.

The successor manifest is a sealed non-current contract. Registry must derive
the current manifest through a closed, machine-checked adoption projection;
copying the successor manifest unchanged is forbidden. The current facts bytes
must equal the sealed successor facts bytes exactly.

The two current files must be installed candidate-first under an exclusive
lock as one process-crash-recoverable facts-first / manifest-last transaction.
Rollback snapshots are transaction recovery material only. Once the candidate
pair reaches the committed transaction state, restoring the predecessor as a
new canonical current state, exposing a partial current pair, or maintaining
dual current identities is forbidden.

The Registry adoption contract keeps its `correction-0001` binding immutable
and adds a `correction-0002` successor binding. Food `attempt-0022`, Registry
`attempt-0009`, correction `attempt-0010`, correction successor
`correction-0001`, the Naturalization 0018/0019 evidence, every predecessor
receipt, and every predecessor terminal seal remain immutable.

This cutover may emit only Registry correction evidence and a Naturalization
current-input handoff. It does not authorize RTC, rendered-description, Lua,
runtime, package, Foundation rebind, a Naturalization attempt, or official
Publish execution.
