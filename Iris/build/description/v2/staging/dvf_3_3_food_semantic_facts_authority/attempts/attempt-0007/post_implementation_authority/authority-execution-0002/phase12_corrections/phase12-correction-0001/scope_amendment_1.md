# Phase 12 correction scope amendment 0001

## Why this amendment exists

The approved six-file correction is implemented at commit
`2b32c2cdcdcdbd3e76fd6a45c27adf9abc6ec367`. The exact D16 acceptance and
preservation suites and all three compose regression suites pass. The focused
food-semantic suite reaches 46 tests but four Phase 9/10 fixture tests fail
before their assertions because `shutil.copytree` recursively copies the later
`phase12_corrections` evidence into an already nested temporary directory and
exceeds the Windows legacy path limit.

This is an implementation-discovered test-fixture portability defect. It is not
either original correction finding, and it does not authorize production or
authority behavior changes.

## Exact proposed scope

One preimage-bound test file and four existing methods may change. In each
method, the existing
`shutil.copytree(AUTHORITY_ROOT, authority_copy)` call may gain only
`ignore=shutil.ignore_patterns("phase12_corrections")`.

The Phase 9/10 tests do not consume Phase 12 correction evidence. All authority
inputs relevant to their assertions remain in the copy. No assertion, expected
value, gate, contract, product code, Naturalization behavior, current surface,
or preserved evidence may change.

## Lifecycle

This amendment requires a fresh focused Codex Reviewer scope review with
Critical 0, Important 0, and out-of-scope change 0, followed by owner preimage
scope approval. Only then may the four call expressions be edited. The final
replacement hash remains subject to the original post-implementation external
review and owner result approval.
