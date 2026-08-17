# Iris test scenario execution consolidation closeout

Status: `implementation_complete_validation_blocked`.

The test-only implementation is complete on commit `991414badc7d470c04bad2967dd26e78aff0b697`. It adopts three non-pilot qualified-proxy scenario groups, preserves the existing test identities, removes the runtime-payload module-global writable root, and does not change Iris or Pulse runtime authority.

## Structural consolidation outcome

| Scenario group | Comparable consolidatable invocations | Reduction | Total invocations | Evidence category |
| --- | ---: | ---: | ---: | --- |
| `artifact-inventory-git-fixture-seed` | 14 -> 2 | 85.71% | 35 -> 26 | qualified proxy |
| `registry-authority-common-source-compile` | 16 -> 1 | 93.75% | 16 -> 1 | qualified proxy |
| `registry-authority-round3-runner-source-compile` | 3 -> 1 | 66.67% | 3 -> 1 | qualified proxy |

These rows make no removable-cost or wall-time claim. The runtime-payload workspace change is an isolation-only correction: one import-time writable global root became one class-owned read-only root plus six case-owned writable roots, so materialization count intentionally changed from 1 to 7 and has `cost_claim=none`.

## Identity, review, and focused validation

- Identity map: 35 mapped rows, zero duplicate new checkpoint IDs, zero unmapped terminal dispositions.
- Codex Reviewer: initial P0/P1/P2 `0/4/0`; all blockers resolved; final `0/0/0`, PASS. The reviewer performed static review only.
- Syntax compilation: PASS.
- Bounded alone/forward/reverse order matrix: PASS.
- Normal adopted-family batch: 46 passed plus 36 passed subtests in 89.80 seconds.
- Exact-current: 219 -> 219 nodes, zero drift.
- Configured-current: 471/645 with 174 deselected before and after, zero node drift.

The full-universe baseline was observed once: 643 passed, 1 skipped, 1 failed, and 126 subtests passed in 793.66 seconds. Its one failure was the pre-existing current registry-runtime compatibility identity expecting `implementation_toolchain_freshness_failed` but observing `durable_bundle_destination_drift`; it is not a known historical advisory and was not remediated outside this plan's scope.

## Canonical validation blocker

The one declared final canonical wrapper invocation targeted the exact implementation commit. It exited before test execution because the selected external work root exceeded the Windows checkout path budget: `103 > 56`. The wrapper recorded native exit code 2, created no full-run result receipt, and therefore cannot support a canonical PASS claim. It was not rerun, preserving the plan's single full-gate execution budget.

Accordingly, the implementation, identity, isolation, reviewer, focused-validation, denominator, and structural cost axes are satisfied. The canonical validation axis remains blocked; configured and full-gate performance axes remain respectively `not_measured_no_comparable_baseline` and `not_measured_no_baseline`.
