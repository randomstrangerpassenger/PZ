# Iris Core Refactor Integrated Closeout

## Scope and state

This closeout covers mandatory Changes 1–6, the Change 7
`deferred_by_design` disposition, the Change 8 no-op disposition, and the
Change 9 integrated validation and seal candidate. All mandatory implementation
axes and pre-seal validation axes are closed without an
`unvalidated_but_in_scope` row. The exact committed CleanCheckout and terminal
binding remain fail-closed until the post-seal report records `status=complete`.

Plan-specific state: `seal_candidate_ready_pending_terminal_attestation`.
Standard closeout state: `implemented_only` pending terminal attestation.

Final completion authority: post-seal
`final_evidence_binding_report.json.status=complete`.

The diagnostic route remains a non-blocking advisory axis. It is not promoted
to a behavior, release-readiness, B42, multiplayer/soak, or unknown-consumer
compatibility claim.

## Delivered changes

- Description string output derives from the block API.
- Browser selection fallback and BrowserData cache/build states are explicit.
- Browser and Wiki detail presentation share a read-only fact model; wheel
  scrolling repositions existing widgets instead of rebuilding them.
- Legacy `IrisData` access and Browser variant compatibility are isolated
  behind named adapters.
- Build-tool decomposition is `deferred_by_design`: current core remains 12,
  allowed tooling remains 4/4, and no unapproved slot was created.
- Repository cleanup is a no-op: zero paths met the deletion predicate.
- Historical/full discovery tests now use pinned Git inputs and bounded
  disposable roots, so they do not mutate the source checkout or depend on a
  local package mirror.

## Final validation axes

The final pre-seal implementation commit is
`34db710b568907eec6aa3d5c325f50e0cb0b5188`.

- PZ/Kahlua B41 acceptance remains validated for Description 4, Browser 7,
  Detail 4, and Legacy 3 cases against implementation commit `60a919f0`.
- Standalone auxiliary characterization remains validated for 15 rows against
  baseline `72e76b36`; it is not used to overclaim PZ equivalence.
- Current route: 145 tests, 0 failures, 0 errors, 82.259 seconds.
- Historical route: 285 tests, 0 failures, 0 errors, 7.295 seconds; pinned
  corpus 2,409 rows, archive SHA-256
  `a8e3eef24aa1982090eb90b02a9059b84e9f93b8764e1b6f430ea96d74974e12`.
- Full v2 discovery: 520 tests, 0 failures, 0 errors, 295.190 seconds.
- Production Lua syntax: 95 files passed.
- Disposable package identity: 95 Lua files and 12 Layer 3 files passed; the
  external candidate was removed. A fresh checkout correctly had no ignored
  existing package peer.
- Diagnostic route (advisory): 77 tests, 3 failures, 26 errors. These failures
  are confined to historical overlays that intentionally omit retired inputs
  and ignored local source-contract anchors; `blocking=false`.

## Protected and compatibility boundaries

One protected governance file has an approved exact change. Baseline commit
`72e76b36` advanced `current_generation_descriptor.json` but left
`current_route_required_validations.json` bound to the preceding descriptor.
Change 9 updates only that repeated SHA-256 binding under pinned ancestor
authority `dd732e1f` / blob `7aebc178`. The protected report records changed 1,
approved 1, unauthorized 0.

Mixed-line-ending working-tree hashes in the original Phase 0 inventory were
canonicalized to the unchanged Git blob identities. Baseline and final Git
blobs are identical for runtime facts, decisions, rendered data,
classifications, all 11 chunks, clean-checkout support, and the build-tool role
inventory. The existing source-side package peer remains read-only and
unchanged; the committed fresh checkout intentionally contains no ignored
peer.

Supported API compatibility is limited to the exact Phase 0 manifest. No claim
is made for unlisted external consumers.

## Manifest and seal

Validation asset manifest generation 8 is sealed with exactly 75 required
assets, `reserved_future_count=0`, and all lifecycle rows `sealed`. Its previous
generation content SHA-256 is
`d85f40c4c28609e9f7c4d24dd4d05a60b1d5dab274a6b39414cbba30a331ccda`.
The final required-ID SHA-256 is
`6398631fe53b239e670ac6b5bf5a405fb80936b1016246b689fb2d0ab853ae2e`;
the sealed manifest content SHA-256 is
`b92ba19aaa67f653b15404631161bec22409a52f295fbe5ffbc45c02a618813a`
and its staged Git blob is `480e838d07aab7b231678f4bf5d09ef5a11e43bf`.
Validation ceiling generation 8 is sealed by Change 9 and has zero mandatory
unvalidated axes. Its final content SHA-256 is
`3c334fe9d92b7a90cb7f161c97035a4634a5ea354bdfd00facc51b6d848f35f3`.

The operational order is fixed:

1. Stage the sealed candidate and validate its exact index manifest and index
   validator.
2. Commit the seal candidate.
3. Run `CleanCheckout` against that exact commit/tree in disjoint external work
   and result roots.
4. Materialize `final_evidence_binding_report.json` in an evidence-only
   terminal attestation commit, recheck receipt/canonical/stdout/stderr hashes,
   then remove the exact result root.

The terminal report is intentionally excluded from the sealed 75-asset
denominator to prevent self-input recursion. It does not change sealed runtime,
manifest, ceiling, or closeout content.

## Conditional branches and non-claims

- Change 7 build decomposition: `deferred_by_design`, standard state
  `complete`.
- Change 8 cleanup: `no_op`, standard state `complete`.
- Generator full removal and global alias removal were not selected; their
  compatibility facades remain intentionally supported.
- No release-readiness, B42 behavior, multiplayer/soak, Workshop deployment,
  or unknown external-consumer compatibility claim is made.
