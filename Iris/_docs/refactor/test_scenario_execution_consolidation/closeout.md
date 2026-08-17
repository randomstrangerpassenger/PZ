# Iris test scenario execution consolidation closeout

Status: `implementation_complete_validation_blocked`.

The test-only implementation is complete on commit `991414badc7d470c04bad2967dd26e78aff0b697`. It adopts three non-pilot qualified-proxy scenario groups, preserves the existing test identities, removes the runtime-payload module-global writable root, and does not change Iris or Pulse runtime authority.

The adopted source plan is `docs/iris_test_scenario_execution_consolidation_plan.md`, SHA-256 `2e56a9c7dbda4f44f972ff9aa265b8c64d655049db1c460230619381b857a36b`. The untracked source plan was not copied into the branch; its exact hash is retained here for reproducibility.

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

The original long-path rejection was correctly reclassified as preflight rather than a canonical long execution. That receipt remains at `C:/Users/MW/Downloads/coding/PZ-scenario-consolidation-results-20260817/final-full-gate-orchestration-991414ba.json`. Two further setup attempts were also rejected before checkout/test execution: `C:/q` was not writable, and a short-root attempt against the evidence commit failed the exact-HEAD check. These attempts are disclosed but do not count as long executions.

The one actual canonical long execution used a clean detached worktree at exact implementation commit `991414badc7d470c04bad2967dd26e78aff0b697`, the same immutable environment receipt, and the short work root `C:/Users/MW/q/fw991b`. Checkout succeeded and the canonical gate started. Before pytest, full-gate source-policy validation rejected the tracked source `Iris/validation/test_workflow_consolidation/tests/test_classify_source_policy_impact.py` as unclassified. The source existed at the base commit and has no base-to-implementation diff. The wrapper recorded native exit code 2 and created no full-run result receipt. Its orchestration receipt is `C:/Users/MW/q/fo991b.json`.

No second canonical long execution was performed. Consequently the baseline's current registry-runtime compatibility failure was not reached by the final gate, and exact-current/configured-current collection equality remains denominator evidence rather than execution PASS evidence.

Accordingly, the implementation, identity, isolation, reviewer, focused-validation, denominator, and structural cost axes are satisfied. The canonical validation axis remains blocked; configured and full-gate performance axes remain respectively `not_measured_no_comparable_baseline` and `not_measured_no_baseline`.
