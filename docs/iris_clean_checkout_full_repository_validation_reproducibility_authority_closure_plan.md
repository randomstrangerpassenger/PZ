# Iris Clean-Checkout Full-Repository Validation Reproducibility Authority Closure Plan

Status: review-complete implementation plan (`r6`) plus owner-directed `aa49e8f9` four-plan synchronization addendum; eligible for owner-authorized Phase 0 after the synchronized plan set is tracked in a clean descendant of `aa49e8f9`. The synchronization addendum requires no additional plan-level review. Implementation has not started because the owner has not yet issued an implementation-start instruction.

Roadmap source: `Iris Clean-Checkout Full-Repository Validation Reproducibility Authority Closure — Synthesized Final Roadmap`

Review sources:

- cycle 1: `Iris Clean-Checkout Full-Repository Validation Reproducibility Authority Closure Plan — Synthesized Review`
- cycle 2: `Iris Clean-Checkout Full-Repository Validation Reproducibility Authority Closure Plan — Synthesized Review (r2)`, target SHA-256 `59b3e7b1d980030c53f54b40b2ae225ed1e9fec367128718f93924b6d284658d`
- cycle 3: `Iris Clean-Checkout Full-Repository Validation Reproducibility Authority Closure Plan — Synthesized Review (r3)`, target SHA-256 `48f7ef281b392ce79e654d15967fc9143c6293396416b6d46fc696064ab36e64`
- cycle 4: inline review of revision `r4`, target SHA-256 `1ee4f2f33c24fc260ec1f94a8c4bac93ec268fa25571e5abee9ca6d834ea6ae8`
- cycle 5: inline review of revision `r5`, target SHA-256 `91e843d9bee7d7c0708f751d526aef9a0aa6d1c134b031be48380138a80ef1d0`

Planning inspection readpoint:

- repository: `C:\Users\MW\Downloads\coding\PZ`
- inspected `HEAD`: `aa49e8f9fce19955a374b45d0744b1418a45ac9e`
- preservation commit containing failure-observation artifacts: `9d0d4285f9176313de756eeb428b2d20f682d6d9`
- the inspected worktree is materially dirty and contains unrelated user changes; it is not an admissible empirical baseline or execution workspace

Plan-level conflict resolutions:

| Review decision | Resolution adopted by this revision |
|---|---|
| D-01 — owner and terminal target | Interpretation A: the logical owner is fixed as `Iris Repository Validation / Clean-Checkout Reproducibility Authority`; the terminal target is a canonical mandatory full-repository gate. Phase 0 may ratify physical storage and consumer relationships, but may not replace the target with a subset or advisory gate. |
| D-02 — mandatory decision scope | Phase 0 contains only decisions required for the observed closure. Quarantine, POSIX/dual-platform expansion, broad locale/timezone policy, and cross-machine portability are finding-triggered extensions. Provenance is mandatory rather than optional. |
| D-03 — reviewer environment | `same_machine_different_operator`. Machine portability is outside the claim. A different-machine claim requires a separately approved extension and the EOL/locale/timezone/path matrix. |
| D-04 — Python provisioning | `pre_provisioned_external_environment_as_explicit_prerequisite`. Provisioning is outside Run A/B; its receipt and frozen package identity are inputs to both runs. Execution caches remain separate. |
| D-05 — partial status | `partial` is a non-terminal diagnostic execution state. It releases no downstream blocker and grants no downstream approval. |
| D-06 — aggregate versus route verdicts | Claude C-09 Option A is adopted. The full-repository gate is a superset execution surface; current, historical, diagnostic, and aggregate execution verdicts are reported separately. The aggregate claim does not replace or imply a sealed route verdict, package-gate verdict, or full historical artifact byte reproducibility. |

Review-cycle-1 disposition carried forward from the cycle-2 common findings:

| Finding | Carried status | Contract location |
|---|---|---|
| SYN-C1 | `superseded_by_explicit_owner_decision` | D-01 and Change 1 |
| SYN-C2 | `resolved` | Change 2 commit/evidence lifecycle |
| SYN-C3 | `resolved` | Section 4 origin state plus Changes 2 and 4 fail-loud reconciliation |
| SYN-C4 | `resolved` | Change 3 D0/D1 family |
| SYN-C5 | `superseded_by_explicit_owner_decision` | D-04, environment prerequisite, and Change 5 |
| SYN-C6 | `resolved` | mandatory provenance and hash-only prohibition |
| SYN-C7 | `superseded_by_explicit_owner_decision` | D-03, validation limits, and governance EOL guard |
| SYN-C8 | `resolved` | live-manifest role and OR-04 |
| SYN-C9 | `resolved` | OR-05 and `approved_tooling_surface` |
| SYN-C10 | `resolved` | OR-07 and Change 10 reviewer sequencing |
| SYN-I1 | `superseded_by_explicit_owner_decision` | D-02 finding-triggered extensions |
| SYN-I2 | `resolved` | three-ledger split |
| SYN-I3 | `resolved` | Change 6 content/stat/transient-write evidence |
| SYN-I4 | `resolved` | repeated census and order variation |
| SYN-I5 | `resolved` | per-test temp isolation and leakage negative case |
| SYN-I6 | `resolved` | collection-error accounting |
| SYN-I7 | `superseded_by_explicit_owner_decision` | D-05 no-unblock partial rule |
| SYN-I8 | `resolved` | unit-qualified `56` fields |
| SYN-I9 | `resolved` | contract blob-ID binding |
| SYN-I10 | `resolved` | R0→C0 red/green evidence |

Review cycle 2 found these cycle-1 contract defects substantially resolved. Revision r3 does not reopen them.

Review-cycle-2 disposition carried forward from the cycle-3 common findings:

| Finding | Confirmed status | Contract location |
|---|---|---|
| SYN-C09 | `resolved` | D-06 Option A adoption, Objective, Change 3, Validation Limits, Governance Constraints, and Expected Closeout State |
| SYN-I1 | `resolved` | separate origin-command provenance and origin-failure coverage gates |
| SYN-I2 | `resolved` | positive downstream-unblock boundary in Section 12 |
| SYN-I3 | `resolved` | OR-08 and Change 6 transient-write mechanism contract |
| SYN-I4 | `resolved` | `DOC0` rename and V0-only greenness rule |
| SYN-I5 | `resolved` | collection identity-source field |
| SYN-I6 | `resolved` | durable environment receipt promotion |
| SYN-I7 | `resolved` | reviewer-unavailable blocked state |
| SYN-M1 | `resolved` | `D0c` renamed to `DOC0` |
| SYN-M2 | `resolved` | Objective separates repository inputs from the external environment prerequisite |
| SYN-M3 | `resolved` | `Iris Publish Boundary` canonical name and `Publish Boundary` alias clarified |
| SYN-M4 | `resolved` | adoption-introduced D1 identity guard |
| SYN-M5 | `resolved` | dirty planning readpoint usage boundary |
| SYN-M6 | `resolved` | execution-unit budget |
| SYN-M7 | `resolved` | pytest cache mode bound into canonical command identity |

Review cycle 3 confirmed `SYN-C09` and all listed cycle-2 findings resolved. Revision r4 does not reopen them.

Review-cycle-3 finding disposition incorporated:

| Finding | Accepted status | Contract location |
|---|---|---|
| SYN-C10 | `resolved` | strict origin-coverage equation in Section 4 and Changes 2/4 |
| SYN-I11 | `resolved` | OR-04 invocation DAG, leaf-only adoption, and recursion negative fixture |
| SYN-I12 | `resolved` | split immutable-B0 initial and candidate-bound C0 preterminal route-feasibility readpoints in Change 3 |
| SYN-I13 | `resolved` | OR-08 expected-attempt allowlist and denied-write accounting |
| SYN-M1 | `resolved` | route verdict derivation-source fields |
| SYN-M2 | `resolved` | OR-09A policy and OR-09B measured ceilings with safety factor |
| SYN-M3 | `resolved` | `taxonomy_fallback_row_count` reporting |
| SYN-M4 | `resolved` | downstream-unblock boundary promoted into the terminal closeout packet |

These cycle-3 dispositions are accepted and carried forward by the completed review chain.

Review-cycle-4 finding disposition incorporated:

| Finding | Accepted status | Contract location |
|---|---|---|
| ICCR-I1 | `resolved` | Change 2 `CXn` lifecycle, Change 3 split initial/preterminal readpoints, Change 9 budget, and Expected Closeout State |
| ICCR-M1 | `resolved` | recursion fixture reserved in Change 3 D1 delta, implemented in Change 5, and only rerun in Change 10 |
| ICCR-M2 | `resolved` | external V0 binding for `gate_input = true` documents and DOC0-only embedded V0 trace |
| I-1 | `resolved` | OR-09A bounded feasibility units and `c0_preterminal_feasibility_attempt_count` |
| I-2 | `resolved` | absolute stored terminal-PASS read prohibition and `stored_terminal_pass_read_count = 0` |
| I-3 | `resolved` | append-only OR-08 census amendment and D0-to-D1 Git-invocation preflight expansion |
| M-1 | `resolved` | terminal `taxonomy_fallback_row_count = 0` |
| M-2 | `recorded_out_of_scope` | Non-Goals dirty-workspace transition boundary |

These cycle-4 dispositions are accepted and carried forward by the completed review chain.

Review-cycle-5 finding disposition incorporated:

| Finding | Accepted status | Contract location |
|---|---|---|
| ICCR-M1 | `resolved` | canonical live-manifest/`legacy_combined_governance_route` container sentence in Sections 4, 6, and 11 |
| ICCR-M2 | `resolved` | Change 4 observed attempted/successful write-event evidence ceiling |
| I-1 | `resolved` | Change 3/8 D1 invalidation, successor additive-delta review, and non-resetting CXn attempt count |
| I-2 | `resolved` | OR-08 discovery/enforcement run classes and D0-then-D1 Git preflight expansion |
| M-1 | `resolved` | post-D1-freeze identity-ratio rescaling of OR-09B without an extra execution |

The owner confirms that review is complete. These cycle-5 dispositions are accepted, retained blocking findings are resolved, and no additional plan-level review is required before owner-authorized Phase 0. The later `iris_aa49_four_plan_execution_sync_v1` addendum changes coordination metadata only, does not alter this plan's authority target, validation denominator rules, write boundary, or terminal predicate, and is owner-directed not to reopen plan review.

Fixed logical authority:

`Iris Repository Validation / Clean-Checkout Reproducibility Authority`

Fixed maximum terminal claim, available only after every required gate and seal below passes:

`Iris Clean-Checkout Full-Repository Validation Reproducibility Authority PASS`

Fingerprint rule:

- this file does not embed its own byte hash;
- the owner-accepted implementation record must bind this revision's Git blob ID or SHA-256 at B0;
- a later substantive plan-byte change requires an updated fingerprint and explicit owner approval; the owner-directed `iris_aa49_four_plan_execution_sync_v1` coordination-only addendum is not substantive and requires fingerprint refresh without additional plan-level review; any later authority, scope, validation, or terminal-predicate change remains substantive;
- the implementation manifest must bind the exact Git blob IDs of this plan, `docs/PLAN_TEMPLATE.md`, and `docs/EXECUTION_CONTRACT.md` at the implementation base.

This plan itself creates no PASS claim and changes no existing sealed authority. The completed review plus the owner-directed synchronization addendum make Phase 0 eligible after `G0_plan_set_materialization_and_owner_sync`; implementation begins only on the owner's explicit start instruction, and Phase 0 ratification is the first implementation step.

## 0. `aa49e8f9` Four-Plan Synchronization Contract

This plan is the `G1_clean_checkout_full_repository_validation` owner in the shared four-plan execution contract. The immutable ancestry and planning readpoint is:

```text
aa49e8f9fce19955a374b45d0744b1418a45ac9e
```

That commit is not itself the implementation base because only the Food Semantic plan and its preimplementation review are tracked there. `G0_plan_set_materialization_and_owner_sync` must create a clean descendant commit that tracks the exact four plan blobs, their SHA-256 values, and this shared projection. Existing dirty staged, unstaged, untracked, staging, candidate, attempt, or implementation outputs are not imported merely because they exist in the planning worktree.

All four plans use the following canonical compact-JSON projection. Its SHA-256 is computed over the exact UTF-8 bytes of the one-line object below:

```json
{"authority_boundaries":{"clean":"validation_reproducibility_only","food":"sealed_non_current_successor_only","naturalization_phase8":"immutable_candidate_handoff_only","naturalization_terminal":"requires_publish_accepted_and_policy_closure_complete","publish_foundation":"authority_effect_none","publish_official":"accepted_required_before_live_gate","registry_cutover":"separate_registry_owned_plan"},"baseline_commit":"aa49e8f9fce19955a374b45d0744b1418a45ac9e","baseline_role":"immutable_ancestry_and_planning_readpoint_only","contract_id":"iris_aa49_four_plan_execution_sync_v1","fresh_attempt_rules":{"clean":"fresh_phase0_from_plan_set_commit","food":"fresh_attempt_from_change0_no_attempt_0007_reuse","naturalization":"fresh_attempt_from_phase0_do_not_resume_attempt_0014","publish":"fresh_official_attempt_from_phase0_do_not_resume_attempt_0003"},"owner_directive":"synchronization_only_no_additional_plan_level_review","plan_paths":["docs/iris_clean_checkout_full_repository_validation_reproducibility_authority_closure_plan.md","docs/dvf_3_3_food_semantic_facts_authority_reconstruction_implementation_plan.md","docs/dvf_3_3_korean_prose_naturalization_public_text_rewrite_closure_plan.md","docs/iris_publish_boundary_public_text_quality_acceptance_policy_closure_plan.md"],"prerequisite_closures":{"registry_authority":"canonical_complete","registry_runtime_compatibility":"canonical_complete"},"stage_order":["G0_plan_set_materialization_and_owner_sync","G1_clean_checkout_full_repository_validation","G2_food_semantic_facts_authority","G3_registry_food_successor_operational_cutover","G4_publish_boundary_foundation","G5_naturalization_phase0_through_phase8","G6_publish_boundary_official_phase0_through_phase7","G7_naturalization_terminal_finalize"]}
```

```text
four_plan_sync_projection_sha256 = 12c32873dc7e16e0d64e416bdb6693599e2790e9fc129606a90a72ca745a6eb0
```

The global order is mandatory:

| Global stage | Owner | Exit required for the next stage |
|---|---|---|
| `G0_plan_set_materialization_and_owner_sync` | operational handoff | clean descendant of `aa49e8f9`; four tracked plan blobs; four identical projection hashes; no imported implementation/attempt output |
| `G1_clean_checkout_full_repository_validation` | this plan | terminal `Iris Clean-Checkout Full-Repository Validation Reproducibility Authority PASS` and downstream-unblock receipt |
| `G2_food_semantic_facts_authority` | Food Semantic plan | fresh Change 0 execution; sealed non-current successor and terminal closeout |
| `G3_registry_food_successor_operational_cutover` | separate Registry-owned plan | successor facts/manifest current adoption and exact adoption receipt |
| `G4_publish_boundary_foundation` | Publish Boundary plan | tracked candidate-independent foundation with `authority_effect=none` and readiness PASS |
| `G5_naturalization_phase0_through_phase8` | Naturalization plan | fresh Phase 0 attempt and immutable Phase 8 handoff |
| `G6_publish_boundary_official_phase0_through_phase7` | Publish Boundary plan | fresh official attempt; candidate `accepted`; live gate adopted; policy closure complete |
| `G7_naturalization_terminal_finalize` | Naturalization plan | accepted Publish result rebound and Naturalization terminal closure |

This plan may release only `G2`. It grants no Food semantic approval, Registry cutover approval, foundation readiness, Naturalization acceptance, Publish disposition, current adoption, package, runtime, or release claim. `partial` or `blocked` never releases `G2`. The clean attempt starts at fresh Phase 0 from the tracked synchronized plan-set commit and does not consume later local branch attempts as PASS evidence.

## 1. Objective

Establish a commit-bound, toolchain-bound, test-inventory-bound, input-complete, repository-non-mutating validation contract for Iris.

For an exact tracked subject commit, the contract must make the following statement reproducible by a separately appointed, eligible reviewer on the same machine under a different operator identity:

> Given the separately declared, pre-provisioned external environment prerequisite, the full-repository validation gate can be bootstrapped and run from two separate fresh checkouts using only tracked repository inputs or explicitly declared deterministic materialization, while writing all generated state outside the checkout and producing equivalent canonical result bundles.

The closure must bind all of the following:

- exact commit and clean-checkout identity;
- a declared pre-provisioned external Python environment, interpreter, package set, Git, PowerShell, Lua-checker, and platform requirement;
- an owner-ratified canonical full-gate command derived after D0 route reconciliation;
- a versioned D0 census denominator and additive D1 terminal denominator;
- current-route, historical-route, diagnostic-route, and aggregate reproducibility execution verdicts as separate result fields;
- every active test dependency and producer/bootstrap step;
- a repository-external work, cache, temporary, and result root;
- before/after tracked, untracked, and ignored-state non-mutation evidence;
- two independent reproduction runs with no shared materialized inputs or caches;
- an independent reviewer finding and a separate owner seal;
- an axis-qualified claim that does not imply `Iris Artifact Registry` authority, `Registry Runtime Compatibility`, `DVF Body Compiler`, `Iris Publish Boundary`, semantic correctness, or gameplay approval.

The full-repository gate is a superset execution surface:

```text
aggregate D1 execution surface
contains current-route projection
contains historical-route projection
contains diagnostic-route projection
contains any tracked aggregate-only identity outside the Round 3 route taxonomy
```

Its four execution verdicts remain separate. A route projection PASS in this result is an attempt-local machine-execution result, not a replacement for that route's existing authority verdict or seal.

The terminal identity is the exact validated subject commit, not necessarily the later commit that stores a review or seal record. Successor review/seal records bind the validated subject commit and canonical result hash without requiring a tracked file to contain the SHA of the commit that contains itself.

## 2. Scope

### In Scope

- Phase 0 ratification of the fixed logical authority, physical authority root, single-writer, bootstrap, external environment prerequisite, VCS relationship, live required-manifest relationship, approved tooling allowlist, reviewer identity, and claim vocabulary.
- Preservation and verification of the completed r6 review chain, with every prior Critical finding tracked to `resolved` or `superseded_by_explicit_owner_decision`; the owner-directed coordination-only synchronization addendum requires no additional plan-level review.
- Exact commit/evidence lifecycle from implementation base through terminal successor seal.
- Preservation and binding of the roadmap's failure observation:
  - `309 tests / 13 failures / 21 errors / exit 1`;
  - `612` reported status entries;
  - preservation commit `9d0d4285f9176313de756eeb428b2d20f682d6d9`.
- Re-derivation of the complete test denominator at the selected execution commit.
- Recovery or fail-loud non-recoverability recording of the exact command, route, working directory, environment, and receipt that produced the preserved `309 / 13 / 21 / exit 1` observation.
- Reconciliation of:
  - `pytest.ini`;
  - `Iris/build/description/v2/tests/conftest.py`;
  - `Iris/_docs/round3/round3_test_taxonomy.json`;
  - `Iris/_docs/round3/round3_active_core_closure.json`;
  - `Iris/_docs/round3/current_route_required_validations.json`;
  - `Iris/_docs/round3/round3_run_contract_tests.py`;
  - all additional collected Iris test roots and explicit ignore/deselect rules.
- Full failure, error, import, missing-input, producer, and worktree-mutation census.
- Dependency-edge classification using the roadmap's input/artifact classes:
  - `required_tracked_source`;
  - `hermetic_test_fixture`;
  - `deterministically_materialized_input`;
  - `sealed_current_required_artifact`;
  - `historical_optional_evidence`;
  - `obsolete_or_misrouted_test_dependency`.
- Failure disposition using `genuine_code_regression` only as an outcome, not as an input dependency class.
- Separate `test_inventory`, `dependency_edge_ledger`, and `failure_disposition_ledger` artifacts.
- A single declared bootstrap/orchestration path with explicit repository and external-work-root inputs.
- Migration of active-suite writers to an explicit repository-external output-sink contract.
- Narrow VCS and ignore-rule alignment for dependencies proven required by the frozen gate.
- Focused contract tests, negative fixtures, adversarial reruns, and two-checkout equivalence verification.
- Additive gate adoption, reviewer approval, owner seal, and top-level documentation updates when their owning decision permits them.

### Explicitly Out Of Scope

- Changes to gameplay behavior, in-game UI, rendering, navigation, search, or Lua runtime logic.
- Reinterpretation, recommendation, comparison, strategy guidance, or new semantic facts.
- Public Korean or English text rewriting.
- Reopening a sealed `Iris Artifact Registry`, `DVF Body Compiler`, `Registry Runtime Compatibility`, `Iris Publish Boundary`, Governance Guard, or semantic reconstruction result.
- Treating `Legacy Combined DVF Governance Route` as current compiler or registry authority.
- Adding repository-local generated artifacts merely to make a dirty checkout pass.
- Deleting, skipping, marking `xfail`, deselecting, or weakening assertions for a failing test.
- Reducing the test denominator after observing failures.
- Opportunistic broad refactoring of historical build tools. A historical-named path may change only when the frozen active call graph reaches it, the explicit approved-tooling allowlist includes it, and its owner authorizes the repair.
- Package publication, release approval, or in-game manual acceptance.
- Correcting a genuine runtime, public-text, or semantic regression inside this closure. Such a regression must be routed to its owning axis.

## 3. Non-Goals

- This plan does not declare that every historical or diagnostic Iris test is current authority.
- This plan does not allow the aggregate reproducibility verdict to replace or imply:
  - an existing current-route authority PASS;
  - an existing historical-route authority PASS;
  - an existing diagnostic-route authority PASS;
  - a package-gate PASS;
  - full historical artifact byte reproducibility.
- This plan does not equate “tracked” with “authoritative,” “generated” with “disposable,” or “required by a test” with “required at runtime.”
- This plan does not make the default `pytest` route synonymous with full-repository validation. That route currently defaults to the `current` Round 3 contract and contains explicit test-path and ignore rules.
- This plan does not permit a subset or advisory route to close the fixed full-repository target. Such a route may be diagnostic evidence only.
- This plan does not hard-code the roadmap's observed `309` tests, the current taxonomy row count, or the current required-manifest counts as the future denominator.
- This plan does not make clean-checkout reproducibility a substitute for evidence integrity, semantic correctness, runtime compatibility, or public-surface quality.
- This plan does not convert attempt-local logs, caches, temporary trees, or generated intermediates into current authority.
- This plan does not authorize a new authority taxonomy where an existing Iris taxonomy already owns the concept.
- This plan does not claim environment provisioning reproducibility. It requires a separately provisioned, frozen external environment receipt as an explicit prerequisite.
- This plan does not claim cross-machine, POSIX, dual-platform, broad locale/timezone, or external-mod portability.
- This plan does not define or authorize the plan author's transition from the current dirty workspace into an implementation checkout. Branch creation, patch transfer, staging, cleanup, or reset for that transition is a separate operational handoff after plan acceptance and must preserve the dirty-workspace protections below.
- This plan uses `Iris Publish Boundary` as the canonical authority name. `Publish Boundary` is treated only as its abbreviated alias when encountered in prior text.

## 4. Assumptions

- The implementation will begin from an owner-selected exact commit in a dedicated checkout, not from the inspected dirty worktree.
- The preservation commit remains immutable evidence of an observed failure readpoint. It is not automatically the implementation baseline, success baseline, or authority seal.
- The roadmap and preservation material inspected during planning do not identify the exact command that produced `309 / 13 / 21 / exit 1`. The initial recorded state is:

```text
origin_observation_command = unidentifiable
origin_working_directory = unidentifiable
origin_environment = unidentifiable
origin_route = unidentifiable
origin_execution_time_or_receipt = unidentifiable
origin_execution_commit = unidentifiable
preservation_commit = 9d0d4285f9176313de756eeb428b2d20f682d6d9
```

- Origin command provenance and origin failure-surface coverage are separate gates:

```text
origin_command_provenance_status
= identified | unidentifiable

origin_failure_surface_coverage_status
= complete | incomplete
```

- `origin_command_provenance_status = unidentifiable` keeps `309 / 13 / 21 / 612` as qualitative trigger observations and forbids any claim that the exact O0 command was reproduced. It does not by itself block V0 PASS when P0 failure rows, a complete B0 D0 universe, and individual reconciliation prove `origin_failure_surface_coverage_status = complete`.
- Origin coverage is calculated strictly:

```text
origin_surface_total_count
= covered_origin_surface_count
 + insufficient_preserved_evidence_count
 + unreconciled_origin_surface_count

origin_failure_surface_coverage_status = complete
iff
unreconciled_origin_surface_count = 0
and
insufficient_preserved_evidence_count = 0

coverage_complete_with_insufficient_evidence = false
```

- `insufficient_preserved_evidence` contributes to `uncovered`, never to `covered` or merely `classified`.
- `origin_failure_surface_coverage_status = incomplete` is terminal-blocking. No aggregate count, owner waiver, or classification label may substitute for row-level or deterministic-group evidence. Adding an exception requires a new plan revision, updated fingerprint, and explicit owner approval.
- Planning inspection confirms that the preservation commit is a three-parent merge titled `full-suite generated side effects 2026-07-28`. Its parents are discovery candidates only; the merge topology does not prove which parent/tree was O0.
- Counts observed during planning are diagnostic only:
  - the dirty planning readpoint contains `243` filesystem files matching `test_*.py`;
  - `round3_test_taxonomy.json` contains `465` rows, split across current, diagnostic, and historical classes;
  - the dirty planning readpoint's required-validation manifest contains `149` required artifacts and `56` required tests.
- Those counts describe different units and routes. None may be reused in D0 or D1 without collection and reconciliation at the bound commit.
- The dirty planning readpoint is allowed only for discovery, diagnostic path existence, and non-authoritative code inspection. It is forbidden as an execution baseline, mutation census baseline, success evidence, or terminal input source.
- Numeric fields must always include their unit and readpoint. In particular, `required_test_count_at_planning_readpoint = 56` must never be conflated with any sealed `required_artifact_count = 56` from another lifecycle record.
- `pytest.ini` currently names `Iris/build/description/v2/tests` and one cross-track test as test paths, and explicitly ignores several `Iris/build/tests` files.
- `Iris/build/description/v2/tests/conftest.py` defaults `--round3-contract` to `current`; `all` is a separate selection. Change 3 must derive the full tracked test universe and select a command whose collected surface covers it; a narrower route is non-terminal.
- `round3_run_contract_tests.py` already combines taxonomy IDs with required-manifest tests and checks required artifact fields, but it does not freeze a full-repository collection denominator or prove checkout non-mutation.
- `docs/dvf_vcs_tracking_policy.md` owns the existing distinction between tracking and authority. Any extension must reuse its states or be explicitly assigned to a different owner; this closure must not invent a competing taxonomy.
- `Iris/build/description/v2/tests/test_dvf_vcs_tracking_policy.py` currently proves only a narrow current-required surface and selected forbidden/predecessor guards. It is not a complete clean-checkout dependency census.
- Existing build helpers accept some absolute output paths through `resolve_repo`, and `Registry Runtime Compatibility` tooling demonstrates detached temporary-clone execution. However, output behavior is inconsistent: some required-gate temporary roots still live under repository staging.
- The planning scan found dozens of Python producers with repository-local staging/evidence/output defaults. That scan is a candidate set, not proof that every producer is in the selected gate's active call graph.
- Runtime Lua remains a passive viewer. Python validation and evidence construction remain offline build/governance concerns.
- The existing canonical names remain:
  - `DVF System`;
  - `DVF Body Compiler`;
  - `Iris Artifact Registry`;
  - `Registry Runtime Compatibility`;
  - `Iris Publish Boundary`;
  - `legacy_combined_governance_route` as the preserved live-manifest container identity, not as a compiler or validation ownership authority.
- Preserve the canonical container boundary:

```text
current_route_required_validations.json
= live required-validation manifest
= legacy_combined_governance_route container
!= Iris Repository Validation / Clean-Checkout Reproducibility Authority ownership
!= DVF Body Compiler PASS authority
```
- The maximum validation claim is unavailable if the owner declines the fixed mandatory full-repository gate. Declining it blocks or abandons this plan; it does not redefine this plan as a subset closure.
- No tracked Python lockfile was found during planning. The selected environment mode is therefore a pre-provisioned external environment with a tracked environment-contract schema and an external immutable provisioning receipt. If implementation instead proposes repository-managed provisioning, that is a plan-changing decision requiring a tracked lockfile, an updated plan fingerprint, and explicit owner approval.
- The external environment must be a dedicated virtual environment with `include-system-site-packages = false`, user-site disabled, and ambient `PYTHONPATH` cleared. Its required contract fields are:

```text
provisioning_mode = pre_provisioned_external_environment_as_explicit_prerequisite
tracked_lockfile_identity = absent_by_selected_mode
interpreter_identity = resolved path + file hash + Python version/build
package_set_identity = installed distribution names/versions + RECORD/content digests
ambient_site_packages_isolation = required
frozen_environment_rule = receipt hash and environment content manifest must match
provisioning_network_mode = declared in receipt, never used during canonical runs
environment_provisioning_cache = outside Run A/B and not an execution input
execution_cache = separate per run
```
- `docs/Philosophy.md`, `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`, `docs/PLAN_TEMPLATE.md`, and `docs/EXECUTION_CONTRACT.md` are confirmed live paths at the planning readpoint.

## 5. Repository Areas Affected

### Code

Existing code to inspect and, only where the active call graph proves it necessary, adapt:

- `Iris/_docs/round3/round3_run_contract_tests.py`
- `Iris/build/description/v2/tests/conftest.py`
- `Iris/build/description/v2/tools/build/_dvf_3_3_vnext_common.py`
- `Iris/build/description/v2/tools/build/run_dvf_3_3_registry_runtime_compatibility.py`
- `Iris/build/description/v2/tools/build/validate_dvf_3_3_registry_runtime_compatibility.py`
- active producers discovered under `Iris/build/description/v2/tools/build/`
- any additional producer reached by the frozen full-gate call graph

Candidate new implementation components, whose exact paths must be fixed in the Phase 0 `approved_tooling_surface` allowlist before creation:

- `Iris/build/description/v2/tools/build/iris_clean_checkout_validation_common.py`
- `Iris/build/description/v2/tools/build/run_iris_clean_checkout_validation.py`
- `Iris/build/description/v2/tools/build/validate_iris_clean_checkout_validation.py`
- `Iris/build/description/v2/tests/test_iris_clean_checkout_validation.py`

The listed `description/v2` paths are planning candidates, not pre-authorized write targets. The fixed logical authority is independent; Phase 0 must either ratify these as hosted implementation paths with an explicit ownership note or choose one independent repository-level root. The common module, runner, validator, tests, schemas, and manifests must move together and must not be duplicated under both roots.

### Docs

- this plan
- `docs/PLAN_TEMPLATE.md`, read-only contract input
- `docs/EXECUTION_CONTRACT.md`, read-only execution contract input
- `docs/dvf_vcs_tracking_policy.md`, only if Phase 0 assigns the dependency/tracking relationship to that existing owner
- `docs/DECISIONS.md`
- `docs/ARCHITECTURE.md`
- `docs/ROADMAP.md`
- a closeout document created only after terminal validation

### Config

- `pytest.ini`, only if the selected canonical gate cannot be expressed without an additive, reviewed collection change
- `.gitignore`, only through narrow path-level changes justified by the dependency ledger
- `.gitattributes`, only if a measured EOL drift requires an owner-authorized correction; line-ending preservation for edited governance docs is mandatory even when this file does not change
- `Iris/_docs/round3/current_route_required_validations.json`, only after its live-manifest owner and single-writer authorize the exact non-recursive leaf and the before-write invocation DAG is acyclic
- `Iris/_docs/round3/round3_test_taxonomy.json`, only to reconcile stale test identities under its existing ownership
- `Iris/_docs/round3/round3_active_core_closure.json`, only if the owner explicitly changes a current core/tooling boundary; no such change is presumed

Candidate new tracked contract data, with final location selected by Phase 0:

- an environment-contract schema;
- a D0 census manifest and D1 terminal manifest;
- separate `test_inventory`, `dependency_edge_ledger`, and `failure_disposition_ledger`;
- a producer graph, route-projection/verdict schema, output policy, commit-transition schema, and result-bundle schema;
- focused hermetic fixtures;
- a minimal durable terminal result bundle containing the immutable environment receipt, route/aggregate verdict report, reviewer record, and seal.

### Generated Artifacts

Attempt-local material must live under a caller-supplied repository-external root:

```text
<external-root>/
  environment/
    immutable-provisioning-receipt/
    pre-provisioned-venv/
  census-a/
  census-b/
  transient-write-preflight/
  run-a/
    checkout/
    materialized-inputs/
    test-temp/
    caches/
    result-bundle/
  run-b/
    checkout/
    materialized-inputs/
    test-temp/
    caches/
    result-bundle/
  reviewer-run/
    checkout/
    materialized-inputs/
    test-temp/
    caches/
    result-bundle/
  comparison/
  disposal/
```

The pre-provisioned environment is a declared read-only prerequisite and may be shared. Run A, Run B, post-adoption runs, and reviewer-run may not share execution caches, materialized inputs, temp directories, or result directories.

Raw logs, caches, scratch clones, generated intermediates, and failed-attempt payloads are non-authoritative. Only an owner-defined minimal terminal contract/result/review/seal bundle may be promoted into a tracked durable location. The immutable environment receipt and its hash are mandatory durable members; the external environment itself is not. Promotion requires provenance; hash-only promotion is forbidden.

## 6. Planned Changes

### Change 1 — Ratify the fixed authority contract and implementation boundaries

**Purpose**

Bind the review conflict resolutions, physical ownership, write scope, environment prerequisite, and reviewer rules before any implementation mutation.

**Files**

- `docs/DECISIONS.md`
- the completed review-chain and owner-acceptance record

**Implementation Notes**

The decision record must use the existing append-only `DECISIONS.md` style and contain: date, problem ID, status, logical owner, physical owner/root, decision, rationale, write authority, affected consumers, evidence IDs, claim ceiling, and supersession rule.

The following are fixed by this plan revision and require ratification, not reopening:

| ID | Fixed contract |
|---|---|
| OD-01 | Logical owner: `Iris Repository Validation / Clean-Checkout Reproducibility Authority` |
| OD-02 | Terminal target: canonical mandatory full-repository gate |
| OD-03 | Bootstrap: one explicit deterministic orchestration command after the external environment prerequisite is satisfied |
| OD-04 | Platform: Windows-first; POSIX/dual-platform is a later claim extension |
| OD-05 | Reviewer environment: same machine, different operator |
| OD-06 | Python provisioning: pre-provisioned external dedicated environment with immutable receipt |
| OD-07 | Provenance: mandatory; hash-only promotion forbidden |
| OD-08 | Partial: non-terminal, no downstream blocker release |
| OD-09 | Aggregate gate is a superset execution surface; route execution verdicts and aggregate verdict are separate and do not replace sealed route/package/historical-byte claims |

Phase 0 must additionally ratify these implementation-specific values:

| ID | Required ratification |
|---|---|
| OR-01 | Physical authority root and single-writer |
| OR-02 | Exact PASS/FAIL vocabulary and non-PASS diagnostic status vocabulary |
| OR-03 | `docs/dvf_vcs_tracking_policy.md` owner relationship and permission to extend its test |
| OR-04 | Whether the live `current_route_required_validations.json` consumes a non-recursive leaf guard from this closure; owner, write authority, single-writer, lifecycle state, invocation DAG, and affected-consumer reruns |
| OR-05 | Explicit `approved_tooling_surface` path allowlist |
| OR-06 | External environment-contract path, receipt schema, resolved interpreter invocation, and durable receipt-promotion rule |
| OR-07 | Eligible independent reviewer identity, distinct owner identity, and operator separation evidence |
| OR-08 | Approved Windows transient-write evidence mechanism and all mechanism fields defined below |
| OR-09A | Phase 0 policy: maximum full-suite-equivalent units, dedicated feasibility-readpoint units, preterminal repeat cap, budget-expansion authority, mandatory-run non-dropping rule, and measurement safety factor |

OR-04 must record an acyclic invocation DAG. The only live-manifest adoption candidates are:

- focused contract guard;
- schema guard;
- static manifest-consistency guard;
- non-recursive leaf validator that does not consume an aggregate result.

The live manifest must not adopt:

- the aggregate runner;
- Run A/B or reviewer orchestration;
- a current-attempt terminal-result verifier;
- a review/owner-seal verifier that requires unfinished output;
- any validator that reads a stored terminal PASS.

The invocation rules are:

```text
aggregate_runner may call current_route_runner
current_route_runner may consume approved non-recursive leaf guards
current_route_runner must not call aggregate_runner
current_route_runner must not consume the current aggregate attempt result
leaf guards must not read stored terminal PASS
```

If a safe leaf-only DAG cannot be proven, OR-04 must set `live_manifest_consumption = no`. Storage convenience or a prior PASS cannot override this fallback.

Stored terminal-PASS consumption has no default/non-default distinction in this revision. Any such read is forbidden and increments `stored_terminal_pass_read_count`.

OR-08 must record:

```text
approved_transient_write_evidence_mechanism
write_denial_scope
required_privilege_level
child_process_coverage
application_run
failure_behavior
denied_attempt_receipt_schema
expected_attempt_allowlist
expected_attempt_allowlist_amendment_log
run_class = discovery | enforcement
```

The ratified values must satisfy these minimums:

- `write_denial_scope` covers the entire validation checkout, including `.git`;
- ACL/write-denial setup completes before the before-manifest and is recorded in a preflight receipt;
- ACL teardown occurs only after the after-manifest and terminal event receipt are sealed;
- `child_process_coverage` includes the full descendant process tree;
- `application_run` includes B0 initial feasibility, both D0 census runs, every candidate-bound preterminal readpoint, Run A, Run B, every post-adoption terminal run, and reviewer-run, not only a separate audit run;
- `discovery` runs are B0 initial feasibility and both D0 census runs; `enforcement` runs are every candidate-bound preterminal, C0 Run A/B, G0 post-adoption, and reviewer run;
- the event mechanism records attempted and successful create/write/rename/delete operations with timestamp, process identity, operation, path, and result;
- each `expected_attempt_allowlist` row binds process identity, target-path pattern, command identity, and expected-denial classification;
- allowlisted attempts remain in the immutable receipt; the allowlist changes classification only and never deletes evidence;
- the initial disposable-clone preflight covers every Git command used by the harness and every Git-invoking D0 identity known from B0 collection/static inspection, including `git status`, `git ls-files`, and `git check-ignore`;
- after the Change 4 census and again after each final or successor D1 freeze, OR-08 may receive an owner-reviewed additive amendment. Rows may be added but not deleted, weakened, or broadened; each new row binds the census evidence, D0/D1 test identity, source blob, observed Git command, process identity, target-path pattern, and expected-denial classification that justify it;
- every amendment is append-only, preserves all earlier attempts and classifications, and triggers a fresh disposable-clone preflight before any candidate-bound preterminal or terminal run;
- the post-D1 preflight expands coverage to every Git-invoking frozen D1 identity under denial;
- discovery runs report and retain expected, unexpected, and unclassified denied-attempt counts without applying the enforcement zero predicate. Those rows are evidence for the post-census amendment and must have a disposition before the first candidate run;
- enforcement runs require `unexpected_denied_repository_write_attempt_count = 0` and `unclassified_denied_repository_write_attempt_count = 0`;
- every run class requires `successful_repository_write_count = 0`;
- required privilege is declared and proven in preflight; no undeclared privilege escalation occurs during a run;
- mechanism unavailability, incomplete child coverage, trace loss, or ACL setup/teardown ambiguity sets `failure_behavior = blocked`.

OR-09B is created from the dedicated bounded B0 initial feasibility readpoint at clean immutable B0. That readpoint is the first measured execution unit and is separate from the two Change 4 D0 census runs. OR-09B must record:

```text
OR09B_revision
ceiling_basis = D0_measured | D1_identity_rescaled
measured_elapsed_time
measured_external_disk
measured_peak_concurrency
measurement_safety_factor
d0_measured_identity_count
d1_frozen_identity_count
d1_identity_expansion_ratio
d1_rescale_factor
elapsed_time_ceiling
external_disk_ceiling
concurrency_ceiling
raw_evidence_retention_period
disposal_schedule
```

The safety factor is ratified in OR-09A and must be greater than `1.0`. The initial `D0_measured` ceiling equals each bounded B0 measurement multiplied by that factor and rounded upward.

Immediately after every final or successor D1 freeze, revise OR-09B without another suite execution:

```text
d1_identity_expansion_ratio = d1_frozen_identity_count / d0_measured_identity_count
d1_rescale_factor = max(1.0, d1_identity_expansion_ratio)
D1 active ceiling
= ceil(B0 measured value * measurement_safety_factor * d1_rescale_factor)
```

The rescale applies to elapsed time, external disk, and concurrency ceilings, binds the exact D1 revision/inventory hash, and must be reviewed and sealed before a candidate-bound preterminal run. A successor D1 freeze produces a successor OR-09B revision. OR-09B may not reduce an earlier applicable ceiling or OR-09A's mandatory run count.

OR-09A initially fixes:

```text
b0_initial_feasibility_attempt_count = 1
OR09A_c0_preterminal_feasibility_attempt_cap = 2
```

Any cap or total-unit expansion uses OR-09A's named amendment authority, preserves prior attempt receipts, and records the revised cap and recomputed maximum totals before another run begins.

Finding-triggered extensions are not Phase 0 blockers unless the corresponding condition occurs:

- quarantine requires a concrete dependency that cannot be classified without it;
- EOL/encoding correction requires measured drift, while line-ending preservation on edited governance docs is always required;
- locale/timezone normalization requires measured result divergence;
- POSIX, dual-platform, or different-machine validation requires a separate portability claim;
- network provisioning requires an owner-approved plan change, tracked lockfile, and updated fingerprint.

The Phase 0 artifact must set `approved_tooling_surface` to explicit repository-relative paths. At minimum it may include the new common/runner/validator/test/schema files. An existing producer may be added only when the census proves it is active, its current owner authorizes the repair, and the allowlist amendment is reviewed before the edit.

**Validation**

- OD-01 through OD-09, OR-01 through OR-08, and OR-09A are explicit and mutually consistent.
- OR-04's static DAG has `execution_dependency_cycle_count = 0`.
- OR-08 defines its append-only amendment schema, amendment owner, evidence fields, and mandatory post-amendment preflight.
- OR-08 fixes `discovery` versus `enforcement` run membership and limits unexpected/unclassified denied-attempt zero predicates to enforcement runs.
- OR-09A records `b0_initial_feasibility_attempt_count = 1`, `OR09A_c0_preterminal_feasibility_attempt_cap = 2`, and the corresponding maximum totals.
- OR-09B defines its base D0 measurement fields and mandatory post-D1-freeze identity-ratio rescale/reseal fields.
- The logical owner is introduced through an explicit architecture decision, and the physical writer is named.
- The chosen claim cannot be confused with `Iris Artifact Registry`, `Registry Runtime Compatibility`, `DVF Body Compiler`, or `Iris Publish Boundary` claims.
- `repairs_outside_approved_tooling_surface = 0`.
- The completed review chain records `Critical unresolved count = 0` and `blocking Important unresolved count = 0`; the owner-accepted B0 record binds this file's exact fingerprint.
- No implementation file is added before the owner issues the implementation-start instruction and the Phase 0 record is accepted.

### Change 2 — Bind origin evidence and the commit/evidence lifecycle

**Purpose**

Separate the observed failed run, implementation base, candidate, adoption, validated subject, review/seal successor, and documentation trace.

**Files**

- candidate clean-checkout gate manifest
- candidate preservation/baseline evidence record
- candidate commit-transition ledger
- origin-observation reconciliation ledger

**Implementation Notes**

- Verify that `9d0d4285f9176313de756eeb428b2d20f682d6d9` resolves to the preserved observation.
- Search the preservation commit and retained external receipts for:
  - `origin_observation_command`;
  - `origin_working_directory`;
  - `origin_execution_commit`;
  - `origin_environment`;
  - `origin_route`;
  - `origin_execution_time_or_receipt`.
- If the exact origin command is not recovered, retain the literal `unidentifiable` fields from Section 4 and do not use `309 / 13 / 21 / 612` as quantitative acceptance counts.
- Inspect P0 and all three parent trees for candidate commands, receipts, and route identities. These searches are diagnostic and may not designate a parent as O0 by inference alone.
- Record command provenance and coverage separately:
  - exact O0 command/route receipt sets `origin_command_provenance_status = identified`;
  - absence after the bounded search sets it to `unidentifiable` and activates the claim limitation;
  - P0 failure rows plus complete D0 universe plus row/group reconciliation determine `origin_failure_surface_coverage_status`;
  - `insufficient_preserved_evidence` contributes to the uncovered count and therefore forces `origin_failure_surface_coverage_status = incomplete`;
  - `origin_failure_surface_coverage_status = incomplete` blocks terminal work without an owner-waiver path.
- Reconcile preserved failure/error rows and worktree entries individually or by deterministic content-identical group using only:
  - `reproduced_same_root_cause`;
  - `reproduced_transitive_failure`;
  - `resolved_by_declared_dependency_repair`;
  - `pre_existing_unrelated_workspace_state`;
  - `superseded_by_bound_commit_difference`;
  - `insufficient_preserved_evidence`.
- Coverage contribution is fixed:

| Disposition | Coverage contribution |
|---|---|
| `reproduced_same_root_cause` | `covered` |
| `reproduced_transitive_failure` | `covered` |
| `resolved_by_declared_dependency_repair` | `covered` |
| `pre_existing_unrelated_workspace_state` | `covered`, only with bound evidence proving it predates or lies outside the observed suite mutation |
| `superseded_by_bound_commit_difference` | `covered`, only with an exact commit/path crosswalk proving the difference |
| `insufficient_preserved_evidence` | `uncovered`; terminal-blocking |

- A row with insufficient evidence remains separately classified for audit but never counts as reconciled coverage. This revision provides no owner-exception path.
- Use this lifecycle:

```text
O0 = origin_execution_commit, unidentifiable until a receipt proves it
P0 = preservation_commit containing retained observation artifacts
B0 = implementation_base_commit after Phase 0 ratification and synchronized-plan fingerprint binding
R0 = optional test-only red tree/commit for a new regression test
CXn = provisional exact candidate commit containing implementation plus frozen D1
C0 = the selected CXn commit after its candidate-bound preterminal projection statuses all PASS
G0 = gate_adoption_commit, only when live-gate adoption changes tracked inputs
V0 = exact validated subject commit; C0 when no adoption change exists, otherwise G0
S0 = successor review/owner-seal record that binds V0 and its canonical bundle hash
DOC0 = optional non-claim documentation-trace successor
```

- B0 must have:
  - detached checkout at that commit;
  - no tracked modifications;
  - no untracked or ignored execution residue;
  - no overlay copied from the current dirty worktree.
- B0 is immutable for this lifecycle. Its initial route-feasibility receipt remains diagnostic and is never overwritten, reissued, or relabeled after a repair.
- A repaired tree must be committed as a new exact `CXn` identity before candidate-bound preterminal feasibility runs. If all four preterminal projections pass, that same commit SHA/tree is selected as C0 without a byte change. If any projection does not pass, the `CXn` receipt remains diagnostic, the repair produces a new candidate commit, and no result from the failed candidate is carried forward as C0 evidence.
- External attempt receipts bind every identifiable O0/P0/B0/R0/CXn/C0/G0/V0 identity by commit and tree ID. No tracked contract may require the SHA of the commit containing that same contract blob.
- Run A/B and negative evidence for C0 become diagnostic-only if G0 changes any gate input, inventory, route, config, producer, test, or required consumer. G0 must receive fresh Run A/B, negative validation, and independent reviewer reproduction before becoming V0.
- Change 3 records `gate_input = true|false` for each top document. A `true` document change made before V0 is part of V0 and must be included in validation, but it may not embed the SHA of the commit that contains it; an external attempt receipt or S0 binds that document blob to V0. DOC0 may update only `false` documentation after V0 and may reference the exact V0 SHA as a non-claim successor trace.
- Gate greenness is claimed for V0 only, never for DOC0 or a later documentation-only repository HEAD.
- S0 may store review and seal records, but the claim subject remains V0. A seal cannot be a required input to the machine gate it seals.
- Any post-V0 source, config, manifest, inventory, route, environment-contract, or gate change invalidates the terminal evidence and starts a successor candidate lifecycle.
- Record Git commit/tree IDs, submodule state if any, contract blob IDs, platform, path root, environment receipt, and tool versions at every transition.
- Terminal attempts use separate external clones with no shared working state, materialized input, execution cache, temp state, or result state. Git object sharing is forbidden for terminal attempts; use independent clones or independently materialized object stores.

**Validation**

- `git rev-parse "HEAD^{commit}"` and `git rev-parse "HEAD^{tree}"` match the transition ledger.
- `git status --porcelain=v2 --untracked-files=all` is empty before the run.
- ignored-state census is captured separately.
- every lifecycle transition is explicit and no evidence is reused across a tracked-input change;
- the preservation record, B0, every CXn, C0, G0, V0, and S0 are clearly labeled as different identities, except that C0 intentionally selects the already tested SHA/tree of one passing CXn without creating another commit;
- `self_referential_commit_fields = 0`;
- `origin_command_provenance_status` is present and is `identified` or `unidentifiable`;
- `origin_failure_surface_coverage_status = complete`;
- `origin_surface_total_count = covered_origin_surface_count + insufficient_preserved_evidence_count + unreconciled_origin_surface_count`;
- `unreconciled_origin_surface_count = 0`;
- `insufficient_preserved_evidence_count = 0`;
- `coverage_complete_with_insufficient_evidence = false`.

### Change 3 — Establish the D0/D1 denominator family and separate ledgers

**Purpose**

Make “full repository” a versioned, additive, collected set and prevent this plan's own tests from contradicting the census freeze.

**Files**

- `pytest.ini`
- `Iris/build/description/v2/tests/conftest.py`
- `Iris/_docs/round3/round3_test_taxonomy.json`
- `Iris/_docs/round3/round3_active_core_closure.json`
- `Iris/_docs/round3/current_route_required_validations.json`, conditionally for the OR-04 leaf-only projection
- candidate D0 and D1 gate manifests
- candidate `test_inventory`
- candidate `dependency_edge_ledger`
- candidate `failure_disposition_ledger`

**Implementation Notes**

- At B0, collect without executing every candidate route:
  - default `pytest` route;
  - `pytest --round3-contract all`;
  - v2 `unittest discover`;
  - test files outside the configured pytest roots;
  - files excluded by `pytest.ini`;
  - taxonomy rows in current, diagnostic, and historical states;
  - required-manifest tests.
- Inventory tracked test source files separately from executable identities.
- Normalize each collected identity to source path/blob, class/function, parameters, contract class, route projection, selection reason, and `identity_source`.
- `identity_source` must be exactly one of:
  - `live_collection`;
  - `preserved_receipt`;
  - `taxonomy_fallback`.
- When a collection/import error prevents identity enumeration, create an `uncollected_due_to_collection_error` row from a preserved receipt or taxonomy and label its exact identity source. If no defensible identity count exists, mark the source unresolved and block terminal freeze.
- Define:

```text
D0 = B0 census denominator before implementation/repair tests
D1 = D0 + owner-approved additive contract, isolation, negative, and regression tests
```

- D0 is immutable for this lifecycle. D1 has a reviewed `additive_delta` whose rows include purpose, source blob, owning change, and red/green requirement where applicable.
- Reserve the plan-known recursion negative fixture in the D1 `additive_delta` before freeze, including its intended source path, stable test identity, OR-04 purpose, owner, and expected cycle-failure reason. Change 5 implements that reserved identity and records its final source blob before D1 freezes; Change 10 only reruns it against the final G0 graph.
- Project D0 at the immutable B0 initial readpoint and final frozen D1 at each candidate-bound preterminal/terminal readpoint into:
  - current route;
  - historical route;
  - diagnostic route;
  - aggregate-only tracked identities not owned by the Round 3 route taxonomy.
- `aggregate-only` is a report-mapping status, not a new authority class or route.
- The union of all projections must equal D1, and no identity may disappear because it is outside the Round 3 taxonomy.
- The B0 initial projections use D0 only and are diagnostic. They are not compared as if they contained the later D1 additive delta.
- Before Change 4, execute one dedicated bounded diagnostic feasibility readpoint at immutable B0 and report:

```text
B0_initial_current_route_projection_status
B0_initial_historical_route_projection_status
B0_initial_diagnostic_route_projection_status
B0_initial_aggregate_only_projection_status
```

- Each B0 initial status is `PASS`, `FAIL`, `BLOCKED`, or `UNCOLLECTABLE` and carries the exact B0 commit/tree, failing identities, dependency owners, and whether repair lies inside `approved_tooling_surface`. This readpoint determines the Change 4 census and Changes 5–8 repair scope; it is not a terminal gate and is never rerun or overwritten after B0 changes.
- A B0 initial non-PASS status whose repair cannot be authorized inside the allowlist blocks the closure. An authorized repair proceeds through Change 4 and Changes 5–8 without changing the B0 receipt.
- After Change 4 and Changes 5–8, freeze D1, create an exact provisional candidate commit `CXn`, and execute a candidate-bound preterminal feasibility readpoint that reports:

```text
candidate_subject_commit
candidate_subject_tree
D1_revision
D1_inventory_hash
C0_preterminal_current_route_projection_status
C0_preterminal_historical_route_projection_status
C0_preterminal_diagnostic_route_projection_status
C0_preterminal_aggregate_only_projection_status
c0_preterminal_feasibility_attempt_count
```

- All four `C0_preterminal_*` statuses must be `PASS` for that exact candidate commit before Run A/B may begin. A passing candidate is fixed as C0 by selecting the same SHA/tree, without a new commit between the preterminal readpoint and C0 Run A.
- A non-PASS candidate receipt remains diagnostic. A repair that uses only existing D0/D1 test identities may keep the same D1 revision, but must create a new `CXn` commit and a fresh candidate-bound readpoint.
- If the failure requires any new test identity, exit the CXn retry loop: invalidate the current D1 freeze, return to Change 8, create an owner-reviewed successor `additive_delta`, obtain the required R0 red evidence, freeze a new D1 revision/inventory hash, rescale and reseal OR-09B, amend/re-preflight OR-08, and only then create a new `CXn`.
- The failed preterminal attempt remains counted and diagnostic across a D1 revision. `c0_preterminal_feasibility_attempt_count` is monotonic for the whole B0 lifecycle, never resets on D1 refreeze, and may not exceed the OR-09A cap without a pre-run amendment.
- Results never migrate between candidate SHAs or D1 inventory hashes. D0 remains immutable through every successor D1 revision.
- Required sequencing is: immutable B0 initial feasibility → Change 4 census → Changes 5–8 repair and reserved D1 test implementation → D1 freeze → OR-09B D1 identity-ratio rescale/seal and OR-08 D1 amendment/preflight → exact `CXn` commit → candidate-bound preterminal feasibility → four PASS statuses → select the same commit as C0 → C0 Run A/B.
- Record separate attempt-local execution verdicts:
  - `current_route_execution_verdict`;
  - `historical_route_execution_verdict`;
  - `diagnostic_route_execution_verdict`;
  - `aggregate_reproducibility_execution_verdict`.
- Each verdict record must include:

```text
verdict_source = aggregate_projection | separate_route_command
source_command_id
projection_membership_hash
execution_result_hash
```

- A `separate_route_command` must bind the same V0, environment receipt, D1 projection, and external isolation contract. An `aggregate_projection` must derive only from the canonical aggregate result for that exact projection hash.
- Aggregate PASS requires all D1 identities to pass under the canonical aggregate command, each of the three route execution verdicts to be `PASS`, and every aggregate-only identity to pass. These machine results do not alter or replace existing route authority verdicts or seals.
- Record the exact canonical command only after route reconciliation proves it collects the full tracked test universe. Record its complete ordered identity set, route projections, collection-error accounting, and cache mode.
- If the command uses pytest, command identity must include exactly one:
  - `-p no:cacheprovider`; or
  - `-o cache_dir=<run-specific-external-cache>`.
- Before D1 freeze, mark each of `DECISIONS.md`, `ARCHITECTURE.md`, `ROADMAP.md`, this plan, `PLAN_TEMPLATE.md`, and `EXECUTION_CONTRACT.md` with `gate_input = true|false`. A missing classification blocks V0 lifecycle planning.
- Before D1 freeze, materialize OR-04's proposed invocation DAG with node/edge types, command IDs, manifest consumers, result consumers, and a topological-order hash. Reject any edge from the current route or a manifest leaf back to the aggregate runner or current-attempt result.
- Fail closed on:
  - a newly collected unknown test;
  - a missing D0 test;
  - duplicate or ambiguous normalized identities;
  - an unexpected deselection;
  - an additive D1 test without owner-approved delta;
  - any removal or weakening of D0;
  - post-failure route or denominator shrink.
- Keep three different ledgers:
  - `test_inventory`: one row per collected test identity or defensible collection-blocked identity;
  - `dependency_edge_ledger`: zero-to-many dependency edges per test, with each dependency assigned one input/artifact class and provenance;
  - `failure_disposition_ledger`: execution outcome/root-cause rows, including `genuine_code_regression`.
- Reconcile stale taxonomy entries through the taxonomy's existing governance. Do not relabel a failing current test merely to exclude it.

**Validation**

- Collection is deterministic across two fresh checkouts.
- `D1 = D0 + additive_delta`.
- `removed_from_D0_count = 0`.
- `test_deletion_count = 0`, `skip_added_count = 0`, `xfail_added_count = 0`, and `assertion_weakening_count = 0`.
- Each manifest count equals its normalized unique identity count.
- Every configured ignore/deselect rule has an owner-approved disposition.
- Every D0/D1 test has a source blob hash and a separate dependency-edge coverage record.
- `executed_outcomes + uncollected_due_to_collection_error = denominator` for each run; terminal `uncollected_due_to_collection_error = 0`.
- Current-route and full-repository denominators remain separately named.
- the four `B0_initial_*_projection_status` fields are recorded exactly once against immutable B0, with `b0_initial_feasibility_attempt_count = 1`;
- `C0_preterminal_current_route_projection_status = PASS`, `C0_preterminal_historical_route_projection_status = PASS`, `C0_preterminal_diagnostic_route_projection_status = PASS`, and `C0_preterminal_aggregate_only_projection_status = PASS` against the exact commit selected unchanged as C0;
- `c0_preterminal_feasibility_attempt_count <= OR09A_c0_preterminal_feasibility_attempt_cap`;
- `c0_preterminal_feasibility_attempt_count_is_monotonic = true`;
- `new_test_identity_without_D1_invalidation_count = 0`;
- every D1 invalidation records the failed candidate SHA, prior D1 inventory hash, reason, reviewed successor additive delta, new D1 inventory hash, OR-09B rescale receipt, and OR-08 amendment/preflight receipt;
- `candidate_to_C0_commit_transition_count = 0` and `candidate_to_C0_tree_change_count = 0`;
- `per_route_verdict_reported_count = 3`.
- `aggregate_verdict_reported_count = 1`.
- `route_projection_union_equals_D1 = true`.
- `route_authority_verdict_mutation_count = 0`.
- `taxonomy_fallback_row_count` is reported for diagnostic collection and equals `0` at terminal D1 freeze.
- `terminal_live_collection_identity_count = D1_count`.
- `execution_dependency_cycle_count = 0`.
- `aggregate_runner_reentry_count = 0`.
- `current_attempt_result_dependency_count = 0`.
- `stored_terminal_pass_read_count = 0`.
- `top_document_gate_input_classification_missing_count = 0`.

### Change 4 — Perform the full failure and repository-mutation census

**Purpose**

Distinguish missing inputs, producer leakage, stale routing, and genuine regressions before changing code.

**Files**

- candidate attempt result bundle
- candidate test inventory, dependency-edge ledger, failure-disposition ledger, worktree-mutation ledger, and producer call graph
- no source/config mutation in this change

**Implementation Notes**

- Execute the D0 census at least twice in separate isolated external checkouts after the immutable B0 initial feasibility receipt is sealed and before repair.
- The dedicated B0 initial feasibility readpoint is OR-09B's measurement run and is not one of these two census runs. Review and seal OR-09B before starting the first D0 census.
- Use one canonical order and one deterministic reverse or seeded order derived from the collected identities. If the framework cannot execute the varied order, run each test identity in an isolated invocation. An inability to perform either order variation or test-level isolation blocks classification.
- Capture:
  - collection output;
  - failures and errors;
  - import and setup failures;
  - subprocess commands and exit codes;
  - every opened required input through producer instrumentation or an approved filesystem/process trace;
  - generated paths;
  - tracked worktree byte/hash, mode, file-type, size, and stat/mtime manifests before and after;
  - untracked and ignored path/type/hash/size/stat manifests before and after;
  - transient filesystem events, including create-write-delete sequences;
  - `.pytest_cache`, bytecode, temp, and tool-cache locations;
  - environment variables consumed by active producers.
- Give each test an isolated external temp subtree. A shared temp/fixture root requires an explicit owner-approved allowlist and a test proving that order does not affect its consumers.
- Map each dependency edge to its input/artifact class. Map each failure and write separately to a responsible test, producer, failure disposition, and authority owner.
- The write-denial receipt proves only observed attempted or successful checkout write events. A potential downstream write prevented because an earlier denied operation stopped the process is not an observed event and is not added to an observed-event count.
- Resolve that evidence ceiling through per-test isolation, P0 reconciliation, or focused reruns under the same write-denial contract. This plan does not authorize a writable diagnostic checkout merely to elicit counterfactual writes.
- Treat the planning scan of repository-local writers as a discovery seed only. The frozen call graph determines implementation scope.
- If required-input tracing cannot identify a consumer or producer, mark the row unresolved and block edits to that path; do not replace the missing evidence with inference language.
- Make no `.gitignore`, assertion, fixture, producer, or source change until the census is reviewed.

**Validation**

- Every observed failure/error has a terminal classification or an explicit unresolved owner.
- Every observed attempted or successful checkout write event has a producer attribution.
- Potential downstream writes prevented by an earlier denial are absent from observed-event counts and have an explicit per-test-isolation, P0-reconciliation, or focused-denied-rerun disposition.
- `executed_outcomes + uncollected_due_to_collection_error = D0`.
- the two census runs have a reconciled outcome delta and no unexplained flake/order delta;
- OR-09B's initial D0 ceilings equal the dedicated B0 initial feasibility measurement multiplied by the OR-09A safety factor and rounded upward;
- `transient_repository_write_count` is measured, not inferred;
- `transient_repository_write_count` contains observed events only and makes no claim about downstream events prevented by an earlier denial;
- `origin_failure_surface_coverage_status = complete`;
- `unreconciled_origin_surface_count = 0`;
- `insufficient_preserved_evidence_count = 0`;
- `coverage_complete_with_insufficient_evidence = false`;
- the origin reconciliation uses the fixed statuses from Change 2; `origin_command_provenance_status = unidentifiable` is never described as exact-command reproduction.

### Change 5 — Implement the declared bootstrap and input reconstruction contract

**Purpose**

Allow a fresh checkout to obtain every required validation input without hidden workstation state.

**Files**

- `Iris/build/description/v2/tools/build/iris_clean_checkout_validation_common.py`
- `Iris/build/description/v2/tools/build/run_iris_clean_checkout_validation.py`
- active producer files identified by Change 4
- focused fixtures, environment contract, provenance records, and gate manifest

**Implementation Notes**

- Resolve the pre-provisioned external environment before bootstrap. The orchestrator must reject:
  - an interpreter or environment receipt mismatch;
  - ambient user-site packages;
  - ambient `PYTHONPATH`;
  - package-set fingerprint drift;
  - any write into the read-only environment during a run.
- Expose one reviewed entry point with explicit `--repo`, `--commit`, `--python`, `--environment-receipt`, `--work-root`, `--result-root`, and execution-cache policy.
- Reject a work or result root inside the checkout.
- The canonical Run A/B command performs no environment provisioning and no network access. It invokes the resolved external interpreter directly. Any displayed `uv run` form remains candidate/developer convenience syntax unless it is proven not to sync, provision, or consume ambient state.
- The one-command bootstrap requires deterministic producers, tracked source inputs, captured producer versions, content-addressed outputs, and a per-run external materialization root.
- Never copy ignored inputs from the caller's dirty workspace into the clean checkout as `Registry Runtime Compatibility` tooling currently does for its own isolated candidate scenario; clean-checkout validation inputs must come from the declared dependency contract.
- Every newly tracked source/fixture candidate must have one of:
  - tracked inputs plus deterministic producer plus regenerated byte-identity evidence; or
  - an owner-bound provenance declaration naming source, custody, purpose, and authority.
- Hash-only promotion is forbidden. A dependency with neither provenance path is `irrecoverable_dependency` and blocks terminal PASS.
- Every active producer must accept the explicit external path contract. If it does not, either add its exact path to `approved_tooling_surface` before repair or hand it to its owner and block this closure. Silent fallback to repository-local staging is forbidden.
- Materialization must be idempotent and must verify hashes before test execution.
- Implement the recursion negative fixture identity reserved by Change 3 as a focused test before final D1 freeze. Its test path, normalized identity, source blob, expected cycle reason, and OR-04 DAG edge fixture must match the reviewed additive-delta row.

**Validation**

- Missing required input fails before the test gate starts.
- Undeclared ambient input fails closed.
- Bootstrap in two fresh checkout/materialization roots produces the same canonical hashes.
- the reserved recursion negative fixture is present in the final D1 additive delta and fails for the expected cycle reason before runner reentry;
- Network-disabled canonical execution succeeds using the declared pre-provisioned external environment.
- `hash_only_promoted_dependency_count = 0`.
- `irrecoverable_dependency_count = 0` for `complete`; otherwise the state is `blocked`.

### Change 6 — Isolate all execution output outside the repository

**Purpose**

Make a clean checkout remain byte- and status-clean after collection, bootstrap, test execution, validation, and closeout bundle construction.

**Files**

- active producers identified by the call graph
- `round3_run_contract_tests.py` only if it must accept or propagate the standard external root
- `Registry Runtime Compatibility` helpers only if they are in the selected gate and fail the new output contract
- candidate validator and focused tests

**Implementation Notes**

- Standardize external subroots for materialized inputs, test temp, caches, results, and disposal.
- Set and verify external `TEMP`, `TMP`, `PYTHONPYCACHEPREFIX`, pytest base-temp, and tool-specific cache roots. Disable pytest's cache provider unless the gate explicitly tests it.
- Set `PYTHONDONTWRITEBYTECODE=1`, disable user-site consumption, clear ambient `PYTHONPATH`, and use `GIT_OPTIONAL_LOCKS=0` during the validation process.
- Do not use `HEAD^{tree}` or `git status` as content evidence. Build before/after manifests of actual worktree bytes, mode, file type, size, and stat/mtime for tracked paths, plus equivalent untracked and ignored manifests.
- Execute an OR-08 feasibility preflight before the B0 initial feasibility readpoint. It must prove the ratified privilege, full-child-process coverage, event receipt schema, initial expected-attempt allowlist for the harness and every Git-invoking D0 identity known at B0, and reversible ACL lifecycle in a disposable clone.
- For each applicable run: prepare checkout, apply denial to the checkout including `.git`, seal the ACL preflight receipt, capture the before-manifest, start the approved process-tree event mechanism, execute the gate, seal the event receipt, capture the after-manifest, and only then tear down ACLs for disposal.
- B0 initial feasibility, both D0 census runs, every candidate-bound preterminal readpoint, Run A, Run B, post-adoption terminal runs, and reviewer-run all use this mechanism. A separate audit-only success cannot substitute for its application to those runs.
- Label B0 initial feasibility and both D0 census runs `run_class = discovery`. Their expected, unexpected, and unclassified denied-attempt counts are reported and retained but do not by themselves trigger the enforcement zero predicate.
- Label candidate-bound preterminal, C0 Run A/B, G0 post-adoption, and reviewer runs `run_class = enforcement`. These runs must satisfy the denied-attempt zero predicates after the census/D1 allowlist amendment and preflight.
- A polling-only watcher is insufficient evidence for create-write-delete activity.
- Classify each denied attempt as `expected_allowlisted`, `unexpected`, or `unclassified`. Only a denied attempt whose process/path/command tuple exactly matches the ratified allowlist may be `expected_allowlisted`; successful writes are never allowlisted.
- After the census and after final D1 freeze, enumerate every Git-invoking D1 identity, append only evidence-bound OR-08 allowlist rows authorized by its owner, and rerun the disposable-clone preflight. No candidate-bound preterminal or terminal run may use an amended allowlist before that preflight passes.
- Use a short external root on Windows and record long-path configuration.
- Treat repository-local staging defaults as incompatible unless the call supplies an external override.
- Preserve compatibility for historical tools not reached by the frozen gate; do not refactor them opportunistically.

**Validation**

- focused tests reject an in-repository output root;
- focused tests detect tracked, untracked, ignored, transient, cache, and timestamp-only mutations;
- tracked content/mode/type manifests, untracked manifests, ignored manifests, and stat/mtime manifests are identical before and after;
- `transient_repository_write_count = 0`;
- `successful_repository_write_count = 0`;
- discovery-run `expected_denied_repository_write_attempt_count`, `unexpected_denied_repository_write_attempt_count`, and `unclassified_denied_repository_write_attempt_count` are reported and every row remains in the immutable event receipt;
- `discovery_denied_attempt_disposition_missing_count = 0` before the first candidate-bound preterminal run;
- enforcement-run `unexpected_denied_repository_write_attempt_count = 0`;
- enforcement-run `unclassified_denied_repository_write_attempt_count = 0`;
- enforcement-run `expected_denied_repository_write_attempt_count` is reported and every row remains in the immutable event receipt;
- `transient_write_child_process_coverage = complete`;
- `transient_write_trace_loss_count = 0`;
- `write_denial_scope = checkout_including_dot_git`;
- `write_denial_preflight_status = PASS`;
- `.pytest_cache` and bytecode files are absent from the checkout;
- all attempt outputs resolve under the declared external root;
- cleanup is explicit and cleanup failure is reported, not silently ignored.

### Change 7 — Align VCS tracking and ignore policy with the dependency ledger

**Purpose**

Ensure required clean-checkout inputs are actually present while preserving the distinction between tracking and authority.

**Files**

- `docs/dvf_vcs_tracking_policy.md`, conditionally
- `Iris/build/description/v2/tests/test_dvf_vcs_tracking_policy.py`
- `.gitignore`
- `.gitattributes`, conditionally
- candidate dependency-edge ledger and provenance records

**Implementation Notes**

- For each dependency, record:
  - repository-relative path or deterministic producer;
  - dependency class;
  - owner;
  - tracked/untracked/ignored state;
  - authority state;
  - content hash;
  - deterministic producer identity and tracked-input hashes, or owner-bound provenance declaration;
  - retention/disposal rule.
- Add only narrow `.gitignore` exceptions required by owner-approved tracked inputs.
- Use `git check-ignore -v` to bind each ignored decision to the exact rule.
- Never unignore an entire staging/evidence tree to satisfy one dependency.
- Extend the current VCS policy test beyond its existing narrow two-path required surface only after its owner grants OR-03 write authority and the dependency-edge ledger is accepted.
- Preserve existing line endings for every edited governance document and verify that no content-unrelated EOL diff is introduced. If measured EOL drift affects canonical bytes, stop for a narrow `.gitattributes` owner decision before editing it.
- Capture a governance-text-format manifest before editing with encoding, BOM state, LF/CRLF/mixed classification, and per-line terminator sequence. After editing, unchanged logical lines must retain their original terminators and encoding/BOM; new lines use the file's declared existing style.
- Do not add a tracked file based only on its hash. `irrecoverable_dependency` remains blocked rather than promoted.

**Validation**

- every `required_tracked_source`, `hermetic_test_fixture`, and `sealed_current_required_artifact` is tracked and not ignored;
- every deterministic input can be produced from tracked inputs;
- every newly tracked input has deterministic regeneration evidence or an owner-bound provenance declaration;
- `hash_only_promoted_dependency_count = 0`;
- historical and diagnostic material is not promoted merely because it exists;
- forbidden current-looking predecessor paths remain absent;
- `unchanged_line_eol_mutation_count = 0`;
- `encoding_bom_drift_count = 0`;
- VCS policy tests and negative fixtures pass.

### Change 8 — Repair genuine regressions without crossing authority boundaries

**Purpose**

Reach a clean full-gate result after bootstrap and dependency defects are removed.

**Files**

- only paths explicitly present in `approved_tooling_surface`

**Implementation Notes**

- Re-run each originally failing test against the corrected input/output contract.
- If a failure is a genuine code regression inside `approved_tooling_surface`, repair it with an existing D0 test or an additive D1 focused test.
- For each new regression test, create R0 as a test-only tree/commit without the repair, record the expected failure, and then prove that the identical test blob passes in C0 with the repair. A D0 test's preserved pre-repair failure may serve as red evidence.
- If repair requires a runtime Lua, public-text, semantic-facts, rendered-output, package, sealed-registry, or other protected-surface change, stop and hand it to that owner.
- If repair requires any path outside `approved_tooling_surface`, stop, record owner handoff, and remain blocked until the allowlist is explicitly amended before the edit.
- Do not alter test selection or expected values simply to obtain PASS.
- Freeze D1 once the reviewed additive delta is complete and before C0 terminal attempts. D0 never changes in this lifecycle.
- Immediately after that freeze, revise OR-09B by the D1/D0 identity-count ratio, bind the D1 inventory hash, review/seal the revised ceilings, and complete the OR-08 D1 amendment/preflight before creating `CXn`.
- Commit the repaired implementation and frozen D1 as an exact provisional `CXn` commit, run the candidate-bound `C0_preterminal_*` feasibility readpoint, and select that same SHA/tree as C0 only when all four projection statuses pass.
- If the candidate-bound readpoint does not pass, retain its complete receipt as diagnostic evidence and increment `c0_preterminal_feasibility_attempt_count`. A code repair covered by existing D0/D1 identities creates a new candidate commit under the same D1 revision.
- If that failure requires a new regression-test identity, invalidate the D1 freeze and leave the CXn loop. Add the test only through an owner-reviewed successor additive delta with R0 red evidence, freeze a new D1 revision, perform the OR-09B identity-ratio rescale and OR-08 D1 amendment/preflight, then create the next candidate commit. The prior attempt remains counted; the counter does not reset.
- Do not relabel a failed candidate, add a test directly to a frozen D1, or rerun against an uncommitted tree.

**Validation**

- every original failure/error has a closed disposition;
- focused regression tests pass;
- every new regression test has a test-blob-identical red→green receipt;
- no protected surface changed without its own authority;
- the unchanged D0 subset of D1 passes;
- `removed_from_D0_count = 0`;
- `repairs_outside_approved_tooling_surface = 0`;
- `new_test_identity_without_D1_invalidation_count = 0`;
- each successor D1 revision preserves D0, has an owner-reviewed additive delta, and invalidates every prior candidate receipt for terminal use;
- the selected C0 SHA/tree exactly equals the passing candidate receipt's `candidate_subject_commit` and `candidate_subject_tree`;
- all four candidate-bound `C0_preterminal_*_projection_status` fields are `PASS` before Change 9 begins.

### Change 9 — Prove independent repeatability and adversarial behavior

**Purpose**

Demonstrate that success is a property of the bound repository contract, not one warmed workspace.

**Files**

- candidate validator
- focused negative/adversarial fixtures
- external Run A, Run B, and comparison bundles

**Implementation Notes**

- Create Run A and Run B as separate fresh detached checkouts of the same exact C0 commit selected by the passing candidate-bound preterminal receipt, with independent Git object stores.
- Do not share materialized-input, test-temp, execution-cache, or result directories. The read-only pre-provisioned environment and its receipt are the only shared prerequisite.
- Run the same bootstrap and frozen D1 gate in each checkout using the same resolved external interpreter identity.
- Canonicalize nondeterministic metadata such as absolute root, wall-clock time, and process ID before result-bundle comparison; preserve raw values separately.
- Define a closed normalization allowlist. Any differing field not on that allowlist fails comparison; normalization may not remove commit, toolchain, test, dependency, outcome, mutation, or provenance differences.
- Compare:
  - commit/tree identity;
  - toolchain contract;
  - collected test IDs;
  - route projections and all four execution verdicts;
  - dependency hashes;
  - producer graph;
  - result statuses;
  - canonical output hashes;
  - before/after non-mutation evidence.
- Execute negative cases for missing tracked input, stale manifest, altered fixture hash, hidden ambient file, ambient site package, ambient `PYTHONPATH`, repository-local output root, shared execution cache, denominator drift, collection error, intra-run temp-state leakage, unexpected transient write, hash-only provenance, mismatched toolchain, and mismatched environment receipt.
- Use this execution-unit budget unless OR-09A approves an amendment:

```text
B0 initial projection feasibility       = 1 D0 full-suite-equivalent run
pre-repair D0 census                     = 2 D0 full-suite-equivalent runs
C0 preterminal projection feasibility   = at most 2 D1 full-suite-equivalent attempts
C0 Run A/B                              = 2 D1 full-suite-equivalent runs
G0 post-adoption Run A/B, if required   = 2 D1 full-suite-equivalent runs
independent reviewer-run                = 1 D1 full-suite-equivalent run
negative matrix                         = focused failing cases, not full-suite reruns
R0 red evidence                         = focused affected tests only

maximum without G0 adoption             = 8 full-suite-equivalent runs
maximum with G0 adoption                = 10 full-suite-equivalent runs
```

- The single B0 initial feasibility attempt is a dedicated execution, not a projection of either D0 census run, and emits the base `D0_measured` OR-09B revision using OR-09A's safety factor. That base revision must be sealed before both census runs.
- Immediately after D1 freeze, rescale OR-09B by `max(1.0, D1_count / D0_count)` without another suite execution and seal the D1-bound revision before candidate/C0/G0/reviewer runs. Every successor D1 freeze repeats this rescale and seal.
- `b0_initial_feasibility_attempt_count = 1`. `c0_preterminal_feasibility_attempt_count` includes the first candidate and every repair retry and is capped at `2` by OR-09A. A third attempt or any other execution-budget expansion pauses work for an explicit OR-09A amendment; it does not overwrite a prior candidate receipt, silently drop a mandatory run, or reuse evidence across commits.

**Validation**

- both independent runs exit zero;
- canonical bundles are equivalent under the declared normalization;
- all negative cases fail closed for the expected reason;
- neither checkout contains post-run residue;
- the D0 subset is unchanged and D1 identities match in both runs;
- all three route execution verdicts and the aggregate verdict match between runs;
- `b0_initial_feasibility_attempt_count = 1` and `c0_preterminal_feasibility_attempt_count <= OR09A_c0_preterminal_feasibility_attempt_cap`;
- `d0_measured_identity_count > 0`, `d1_frozen_identity_count >= d0_measured_identity_count`, and the active OR-09B revision binds the exact terminal D1 inventory hash;
- actual execution units do not exceed OR-09A and measured resource use does not exceed the applicable D0- or D1-bound OR-09B revision;
- this change records machine self-validation only and does not record independent review completion.

### Change 10 — Adopt the gate, review, seal, and update top-level state

**Purpose**

Convert a reproducible technical result into an authority-scoped closure without overclaiming.

**Files**

- selected durable gate manifest and terminal result bundle
- `Iris/_docs/round3/current_route_required_validations.json`, conditionally
- `docs/DECISIONS.md`
- `docs/ARCHITECTURE.md`
- `docs/ROADMAP.md`
- a new closeout document

**Implementation Notes**

- Preserve the canonical container boundary: `Iris/_docs/round3/current_route_required_validations.json` is both the live current-route required-validation manifest and the `legacy_combined_governance_route` container. It is neither this closure's ownership authority nor `DVF Body Compiler PASS` authority; storage or consumption does not transfer either authority.
- Modify the live manifest only after OR-04 names its owner, confirms write authority and single-writer, proves the current sealed lifecycle is not bypassed, and defines affected-axis reruns and rollback.
- Adoption is limited to the exact OR-04 non-recursive leaf guard. The live manifest must not point to the aggregate runner, Run A/B/reviewer orchestrator, current-attempt result verifier, unfinished review/seal verifier, or stored prior-PASS reader.
- Validate the final G0 invocation DAG before the manifest write and again after it. If either graph is cyclic or the target is not a leaf, set `live_manifest_consumption = no` and omit adoption.
- Rerun the recursion negative fixture already implemented and frozen in D1 for `aggregate runner -> current route -> required manifest -> aggregate runner` against the final G0 graph; it must fail before runner reentry. Change 10 may not introduce this or any other new test identity.
- If adoption changes tracked gate inputs, create G0. All C0 Run A/B results become pre-adoption diagnostic evidence; rerun the full D1 gate, negative matrix, affected consumers, and non-mutation checks at G0.
- Adoption may not introduce a new test identity outside frozen D1. A new identity invalidates D1 and requires a reviewed successor additive delta before any new terminal attempt.
- Complete independent review only after the final V0 subject commit is fixed following any G0 adoption:
  - reviewer may not be a roadmap author/co-drafter, plan author/co-drafter, implementation participant, terminal-bundle constructor, prior closeout reviewer on the same chain, or owner;
  - the current ChatGPT and Claude reviewers are ineligible for independent closeout review;
  - reviewer identity must be appointed in OR-07;
  - reviewer uses a fresh checkout and separate materialized-input, temp, cache, and result roots;
  - reviewer runs on the same machine under a different operator identity and independently checks the canonical bundle.
- If no eligible reviewer is available, set `independent_review_gate = blocked` and terminal status `blocked`; do not substitute an ineligible reviewer or issue PASS.
- The owner must be distinct from the independent reviewer and seals only after reviewer success.
- Promote the full immutable environment receipt, its hash, required identity fields, and provisioning-mode summary into the durable terminal bundle. The environment itself is not promoted.
- Promote only the minimal durable contract, environment receipt, route/aggregate verdict report, comparison result, reviewer finding, and seal with mandatory provenance. Keep raw attempt data external or non-authoritative.
- The terminal closeout packet must repeat verbatim the Section 12 downstream-unblock boundary and enumerate every approval it does not grant.
- If top-level docs marked `gate_input = true` change, update them before V0 and rerun the affected gate. Their field comparison covers owner, claim vocabulary, gate identity, route non-substitution, and limits, but never requires an embedded exact V0 SHA. The external attempt receipt and S0 bind each tracked document blob to exact V0.
- A top-level document marked `gate_input = false` may be updated in DOC0 with an exact V0 SHA reference as an additive non-claim trace. DOC0's own SHA is not the claim subject and must not inherit V0 greenness.
- Gate greenness and the authority claim apply to V0 only, never to DOC0 or a later documentation-only HEAD.
- Report all four execution verdicts and preserve non-substitution:
  - current-route execution verdict;
  - historical-route execution verdict;
  - diagnostic-route execution verdict;
  - aggregate reproducibility execution verdict.
- The aggregate claim does not modify sealed route verdicts, grant package-gate PASS, or close full historical artifact byte reproducibility.
- Preserve governance-document line endings and reject content-unrelated diff.
- Emit the fixed maximum claim only when every terminal criterion passes.
- `partial` and `blocked` never emit PASS, release no downstream blocker, and grant no downstream approval.

**Validation**

- when adoption occurs, pre-adoption runs are labeled diagnostic and post-adoption V0 runs pass;
- `adoption_introduced_identity_absent_from_D1 = 0`;
- `execution_dependency_cycle_count = 0`;
- `aggregate_runner_reentry_count = 0`;
- `current_attempt_result_dependency_count = 0`;
- `stored_terminal_pass_read_count = 0`;
- recursion negative fixture fails for the expected cycle reason;
- live-manifest owner/write/single-writer and sealed-lifecycle checks pass before the write;
- `canonical_manifest_container_boundary_match = true` for `live required-validation manifest = legacy_combined_governance_route container != this closure ownership != DVF Body Compiler PASS authority`;
- affected current-route consumers pass after adoption and after any revert;
- no existing sealed axis is reopened or renamed;
- `gate_input = true` top-level docs agree through field-based comparison on owner, claim vocabulary, gate, route non-substitution, and limits, while `gate_input_true_embedded_v0_sha_count = 0`;
- each `gate_input = true` document blob is bound to exact V0 by an external attempt receipt or S0, and `unbound_gate_input_true_document_count = 0`;
- any embedded exact V0 SHA in a top-level document occurs only in a `gate_input = false` DOC0 non-claim successor trace;
- `per_route_verdict_reported_count = 3` and `aggregate_verdict_reported_count = 1`;
- `route_authority_verdict_mutation_count = 0`;
- each route verdict contains `verdict_source`, `source_command_id`, `projection_membership_hash`, and `execution_result_hash`;
- durable terminal bundle contains the immutable environment receipt and matching receipt hash;
- terminal closeout packet contains the downstream-unblock boundary and non-approval list;
- reviewer eligibility is mechanically checked and reviewer/owner identities are recorded separately;
- independent reviewer reproduction succeeds on V0 after final adoption changes;
- the final claim is mechanically derived from the terminal result rather than handwritten independently.

## 7. Validation Plan

### Automated Validation

All commands below must run inside an approved clean external checkout. The present dirty workspace is inspection-only. Commands are candidate shapes until Change 3 binds the D1 command and Phase 0 binds the external interpreter.

Baseline and VCS identity:

```powershell
git rev-parse HEAD
git rev-parse "HEAD^{tree}"
git status --porcelain=v2 --untracked-files=all
git status --porcelain=v2 --ignored=matching
git ls-files
git check-ignore -v -- <classified-path>
```

The validator must supplement these Git commands with actual byte/mode/type/stat manifests; `HEAD^{tree}` is identity evidence, not worktree-mutation evidence.

External environment verification and focused implementation-test candidate shape:

```powershell
$IrisValidationPython = '<pre-provisioned-external-venv>\Scripts\python.exe'
$env:PYTHONNOUSERSITE = '1'
$env:PYTHONPATH = $null
& $IrisValidationPython -B -s Iris\build\description\v2\tools\build\validate_iris_clean_checkout_validation.py `
  --environment-receipt <immutable-environment-receipt> `
  --verify-environment-only
& $IrisValidationPython -B -s -m unittest discover -s Iris\build\description\v2\tests -p "test_iris_clean_checkout_validation.py"
& $IrisValidationPython -B -s -m unittest discover -s Iris\build\description\v2\tests -p "test_dvf_vcs_tracking_policy.py"
```

The VCS-policy command is run only when OR-03 authorizes that consumer. Existing current-route guard candidate shape, with its result directed outside the checkout:

```powershell
& $IrisValidationPython -B -s Iris\_docs\round3\round3_run_contract_tests.py `
  --class current `
  --enforce-current-build-closure `
  --out <external-result-path>
```

Candidate full-gate collection commands to reconcile during Change 3:

```powershell
& $IrisValidationPython -B -s -m pytest --collect-only -q -p no:cacheprovider
& $IrisValidationPython -B -s -m pytest --round3-contract all --collect-only -q -p no:cacheprovider
& $IrisValidationPython -B -s -m unittest discover -s Iris\build\description\v2\tests -p "test_*.py"
```

Only the Change 3-frozen D1 command becomes canonical. The other commands remain candidate reconciliation evidence and must not be described as equivalent unless their collected identity sets prove equivalent.

Candidate terminal orchestration shape:

```powershell
& $IrisValidationPython -B -s Iris\build\description\v2\tools\build\run_iris_clean_checkout_validation.py `
  --repo <source-repository> `
  --commit <exact-commit> `
  --python $IrisValidationPython `
  --environment-receipt <immutable-environment-receipt> `
  --pytest-cache-mode <disabled-or-run-specific-external> `
  --work-root <external-run-root> `
  --result-root <external-result-root>
```

Terminal validation must include:

- B0 origin-surface and D0 census reconciliation;
- separate `origin_command_provenance_status` and `origin_failure_surface_coverage_status`;
- strict origin-coverage equation with `insufficient_preserved_evidence_count = 0`;
- D0/D1 additive proof;
- one immutable B0 initial current/historical/diagnostic/aggregate-only diagnostic feasibility readpoint;
- candidate-bound `C0_preterminal_*` feasibility receipts, with four PASS statuses on the exact SHA/tree selected unchanged as C0;
- current/historical/diagnostic projection reports and separate aggregate verdict;
- route verdict derivation-source fields and hashes;
- at least two pre-repair census runs with order variation or test-level isolation;
- environment receipt and ambient-isolation verification;
- durable environment-receipt promotion/hash verification;
- OR-08 write-denial/event mechanism preflight and application to B0 feasibility, census, candidate-bound preterminal, terminal, and reviewer runs;
- initial preflight of the harness and every known Git-invoking D0 identity, append-only census/D1 amendments, expanded preflight of every frozen D1 identity, and full receipt retention;
- discovery-run denied-attempt count reporting/disposition and enforcement-run unexpected/unclassified denied-attempt zero checks;
- R0→C0 red/green receipts for additive regression tests;
- Run A;
- Run B;
- canonical bundle comparison;
- negative/adversarial fixture suite;
- post-adoption rerun when a required gate is added;
- `adoption_introduced_identity_absent_from_D1 = 0`;
- live-manifest invocation DAG validation and recursion negative fixture;
- zero aggregate reentry, current-attempt result dependency, and stored terminal-PASS reads;
- independent reviewer-run after the final V0 commit is fixed;
- tracked/untracked/ignored/stat/mtime and transient-write evidence;
- governance-document line-ending preservation validation;
- contract blob-ID validation for this plan, `PLAN_TEMPLATE.md`, and `EXECUTION_CONTRACT.md`;
- diagnostic `taxonomy_fallback_row_count` reporting and terminal `taxonomy_fallback_row_count = 0`;
- OR-09A execution-unit policy, bounded feasibility-attempt accounting, base D0 OR-09B measurement, and post-D1-freeze identity-ratio rescaling;
- Lua syntax validation only if the selected required route or an approved protected-surface change makes it relevant:

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\check_lua_syntax.ps1
```

No command is reported as passed unless that exact command exits with code `0`.

### Manual Validation

- Ratification review of OD-01 through OD-09, OR-01 through OR-08, and OR-09A.
- Review and seal of the base D0 OR-09B revision before the first D0 census, and of the D1 identity-rescaled revision after every D1 freeze and before the next candidate-bound run.
- Verification that the completed review chain has zero unresolved Critical and blocking Important findings and that the owner-accepted B0 record binds the exact plan fingerprint.
- Review of every configured pytest ignore/deselect rule and every test found outside configured roots.
- Review of D0, D1, and the additive delta against collected output.
- Review of every D1 invalidation/successor additive delta and proof that the CXn attempt count did not reset.
- Review that the plan-known recursion fixture was reserved in the D1 additive delta, implemented before freeze, and not first introduced by Change 10.
- Review of the three route projections, aggregate-only mapping, four execution verdicts, and non-substitution statement.
- Separate review of the test inventory, dependency-edge ledger, failure-disposition ledger, and producer call graph.
- Review of origin-observation recovery and the `309 / 13 / 21 / 612` reconciliation ceiling.
- Review that every `insufficient_preserved_evidence` row remains uncovered and prevents coverage completion.
- Review of OR-04's topological DAG, leaf target, forbidden targets, and recursion fixture.
- Review of the initial OR-08 allowlist, every append-only census/D1 amendment row, and the post-amendment preflight receipt.
- Review of every top document's `gate_input` classification, external V0 binding for `true` documents, absence of embedded self-SHA, and the V0-versus-DOC0 claim boundary.
- Review that `.gitignore` and `.gitattributes` changes are narrow and justified.
- Review that governance-document edits preserve line endings and contain no unrelated byte churn.
- Review of protected-surface diff and authority routing.
- Independent reproduction by the OR-07 reviewer, after automatic eligibility exclusions are checked.
- Separate owner seal after reviewer approval.

No in-game manual test is required unless an independently owned genuine regression changes runtime behavior; that work is outside this closure.

### Validation Limits

- A PASS proves reproducible execution of the selected frozen validation gate for the bound commit and declared toolchain.
- It proves that every tracked D0/D1 identity is accounted for and that the aggregate full-repository reproducibility gate passed at V0.
- It does not replace or imply current-route, historical-route, or diagnostic-route authority PASS; package-gate PASS; or full historical artifact byte reproducibility.
- Per-route execution verdicts in the terminal bundle are attempt-local machine results and do not alter existing sealed route verdicts.
- It does not prove semantic correctness beyond the assertions in the frozen tests.
- It does not prove runtime packaging or gameplay behavior unless their independent required gates are included and pass.
- A Windows-first result does not imply POSIX or cross-machine reproducibility.
- Run A/B plus reviewer-run occur on the same machine and do not prove machine portability, EOL portability, or broad locale/timezone portability.
- The claim assumes the declared pre-provisioned environment receipt; it does not prove that environment can be provisioned from the repository.
- `origin_command_provenance_status = unidentifiable` means the exact O0 command was not reproduced and keeps origin aggregate counts qualitative. V0 PASS remains available only when `origin_failure_surface_coverage_status = complete`.
- Coverage cannot be complete unless both `unreconciled_origin_surface_count` and `insufficient_preserved_evidence_count` are zero; this revision has no owner-waiver path.
- Live-manifest consumption, when enabled, is limited to a non-recursive leaf guard. The manifest never consumes aggregate orchestration, current-attempt results, unfinished review/seal output, or a stored prior PASS.
- Gate greenness is claimed for V0 only, not DOC0 or any later documentation-only HEAD.
- Evidence integrity and clean-checkout reproducibility remain distinct claims.

## 8. Risk Surface Touch

### Authority Surface

Yes.

This plan fixes the logical owner as `Iris Repository Validation / Clean-Checkout Reproducibility Authority` and proposes a claim token, durable result bundle, and possible required-gate adoption. It must not inherit authority merely from location under Round 3 or the live required-validation manifest.

### Runtime Behavior Surface

No intended touch.

`Iris/media/lua/`, packaged Lua, runtime data chunks, UI behavior, and game-facing behavior are protected read-only inputs. Any required runtime change exits this plan.

### Compatibility Surface

Yes, limited to developer/test execution compatibility.

The plan may affect test collection, tool invocation, external output-root support, Windows path handling, and environment contracts. `Registry Runtime Compatibility` remains a separate sealed axis.

### Sealed Artifact Surface

Read-only consumption only.

Sealed current-required artifacts may be validated as dependencies, but their bytes, ownership, and seals must not change here.

### Public-Facing Output Surface

No intended touch.

Public prose, release claims, displayed facts, and `Iris Publish Boundary` acceptance remain unchanged except for internal top-level governance documentation about this new validation axis.

## 9. Risk Analysis

### Architecture Risk

- Assigning this work to the legacy combined route could recreate the authority conflation the current architecture forbids.
- Placing repository-level orchestration under DVF-specific paths could imply ownership that the tools do not possess.
- Adding the test to the live current-route required-validation manifest could confuse consumption with ownership or bypass its single-writer.
- Creating a second dependency taxonomy could diverge from `dvf_vcs_tracking_policy.md`.
- Mixing C0, G0, V0, and S0 evidence could issue a claim for an unvalidated commit.
- An aggregate PASS could be misread as replacing current/historical/diagnostic route authority verdicts or historical byte reproducibility.
- Counting `insufficient_preserved_evidence` as reconciled could make origin coverage falsely complete.
- A current-route live-manifest entry that reaches the aggregate runner or current-attempt result could create recursive execution or certify itself.
- A leaf that reads a stored prior PASS could report green without current execution.
- A `gate_input = true` document that embeds V0 SHA could create a self-referential commit contract.

Mitigation:

- ratify the fixed logical owner, physical writer, and approved path allowlist before implementation;
- keep ownership, storage, and consumption relationships explicit;
- reuse existing taxonomy terms;
- enforce the commit-transition ledger and evidence invalidation rules;
- emit three route execution verdicts and one aggregate verdict, with explicit non-substitution fields and zero sealed-route mutation;
- require the strict origin-coverage equation, count insufficient evidence as uncovered, and provide no owner exception;
- permit live-manifest adoption only for a proven acyclic leaf and fall back to `live_manifest_consumption = no`;
- forbid every stored terminal-PASS read;
- bind `gate_input = true` document blobs to V0 externally and reserve embedded V0 references for DOC0 non-claim traces;
- place execution-input documentation changes before V0 and non-claim trace changes after V0.

### Runtime Risk

- A broad producer refactor could accidentally change generated Lua or package bytes.
- Tests could materialize into live runtime paths and make a false pass depend on residue.

Mitigation:

- protected-surface before/after hashes;
- external materialization roots;
- no runtime write authorization;
- handoff of genuine runtime defects.

### Compatibility Risk

- Windows path length, case behavior, newline conversion, locale, timezone, and shell quoting may make results machine-specific.
- an external Python environment may drift or consume ambient site packages if its receipt is weak;
- Git `--shared` clones can be mistaken for fully independent state.
- environment-provisioning caches can be confused with prohibited execution-cache sharing.
- Windows ACL/event coverage may be incomplete for `.git`, descendants, denied attempts, or teardown.
- Expected denied Git metadata attempts could be mistaken for validation writes or silently omitted from mutation evidence.
- Git commands discovered inside D1 tests after Phase 0 could be absent from the initial expected-attempt allowlist.

Mitigation:

- bind exact tool versions and platform;
- use short external roots and `core.longpaths` where needed;
- bind the pre-provisioned interpreter and package-set receipt and disable ambient imports;
- separate provisioning state from per-run execution caches and materialized inputs;
- prohibit Git object sharing for terminal clones;
- ratify and preflight OR-08, apply it to feasibility, census, terminal, and reviewer runs, and fail closed on trace loss or incomplete descendant coverage;
- bind expected Git attempts by process, path pattern, command identity, and denial classification; retain every attempt and reject successful, unexpected-denied, or unclassified writes;
- preflight every known Git-invoking D0 identity initially, then allow only evidence-bound additive OR-08 amendments after census/D1 discovery and re-preflight every frozen D1 identity;
- limit this claim to Windows-first, same-machine/different-operator evidence;
- reject content-unrelated governance-document EOL changes.

### Regression Risk

- Freezing the wrong denominator could institutionalize an incomplete gate.
- a single denominator could either reject the plan's additive tests or silently shrink the original universe.
- Fixing collection by deleting or deselecting tests could launder failures.
- Broad unignore rules could promote staging evidence or obsolete artifacts.
- hash-only tracking could seal provenance-free local residue.
- an unobserved create-write-delete sequence or shared test temp could hide repository or intra-run state leakage.
- a self-written regression test could confirm its own repair without red evidence.
- route-specific failures could be hidden inside an aggregate-only verdict.
- Route projection infeasibility could be discovered only after expensive C0 runs.
- A repaired candidate result could be mislabeled as immutable B0 evidence, or a failed B0 diagnostic status could incorrectly block an authorized repair.
- Unbounded candidate-feasibility retries could escape the execution-unit budget.
- Adding a regression-test identity inside the CXn retry loop could silently mutate a frozen D1.
- Applying enforcement-run denied-attempt zero predicates to pre-census discovery runs could block the evidence needed to construct the allowlist.
- Applying a D0-measured resource ceiling directly to a larger D1 could create avoidable budget amendments.
- Timestamp, absolute path, and ordering fields could produce false bundle differences.
- Over-normalization could hide a meaningful difference.

Mitigation:

- reconcile every route before freezing;
- preserve immutable D0 and prove additive D1 with zero D0 removals;
- prohibit post-failure denominator reduction and require collection-error accounting;
- use narrow tracking rules;
- require deterministic regeneration or owner-bound provenance;
- require write denial, filesystem-event evidence, per-test temp isolation, and order variation;
- require R0→C0 test-blob-identical red/green receipts;
- report route projections and verdicts separately from the aggregate verdict;
- record one immutable B0 initial diagnostic readpoint, then bind final preterminal projection PASS only to an exact candidate commit selected unchanged as C0;
- cap candidate-bound preterminal attempts in OR-09A and preserve failed candidate receipts as diagnostic;
- invalidate and re-review D1 before adding any post-freeze identity, without resetting the CXn attempt counter;
- separate OR-08 discovery reporting from enforcement zero predicates and expand preflight from known D0 Git callers to frozen D1;
- rescale OR-09B by the frozen D1/D0 identity ratio before candidate execution;
- define an explicit normalization allowlist and retain raw values;
- make unexpected differences fail closed.

## 10. Rollback Plan

- Stop after Phase 0 and before Change 2 if Phase 0 ratification, approved-tooling allowlist, environment prerequisite, or reviewer appointment remains unresolved.
- Stop before gate adoption if origin-surface inclusion, D0/D1 reconciliation, dependency provenance, failure disposition, or protected-surface review remains unresolved.
- Remove only newly added, unsealed orchestration code, tests, fixtures, and config entries.
- Revert narrow `.gitignore`, `.gitattributes`, pytest, taxonomy, and required-manifest additions through ordinary version-control changes.
- Do not delete, rewrite, or amend:
  - preservation commit `9d0d4285f9176313de756eeb428b2d20f682d6d9`;
  - failed-attempt records;
  - reviewer findings;
  - any already sealed historical bundle.
- Mark an adopted result stale or superseded through the owning append-only mechanism rather than editing history.
- Preserve every failed `CXn` preterminal receipt as diagnostic; rollback may not relabel it as B0, C0, or V0 evidence.
- A live required-manifest revert requires its named owner/single-writer and the same affected-consumer reruns required for adoption.
- A live required-manifest adoption or revert requires before/after invocation-DAG validation; a cyclic or non-leaf result restores `live_manifest_consumption = no`.
- Preserve the commit-transition ledger and label pre-adoption or invalidated evidence diagnostic; never relabel it as V0 evidence.
- Dispose of external temporary roots only after preserving the minimal failure diagnosis required by policy.
- If the implementation exposes a genuine defect outside scope, roll back only this closure's unsealed changes and hand the defect to the responsible axis with the bound evidence.

## 11. Governance Constraints

- `docs/Philosophy.md` is controlling: runtime Lua displays; offline tooling validates and constructs; Iris does not interpret or recommend.
- `DVF System` and `DVF Body Compiler` are the current names. Bare `DVF PASS` and `DVF System PASS` remain forbidden.
- `Iris Artifact Registry` owns artifact lifecycle and identity; this closure may consume registry evidence but may not silently take that ownership.
- `Iris/_docs/round3/current_route_required_validations.json = live required-validation manifest = legacy_combined_governance_route container` remains the canonical container identity.
- That container is not `Iris Repository Validation / Clean-Checkout Reproducibility Authority` ownership and is not `DVF Body Compiler PASS` authority; its location, storage, or consumption transfers neither authority.
- `Iris Artifact Registry` canonical closure and `Registry Runtime Compatibility` seals remain closed unless a separately authorized successor or correction scope reopens them.
- The aggregate full-repository gate is a superset execution surface. Its attempt-local current/historical/diagnostic route execution verdicts and aggregate verdict are separate fields.
- Aggregate reproducibility PASS does not replace, imply, reopen, or mutate a sealed current-route, historical-route, diagnostic-route, package-gate, or full historical artifact byte-reproducibility verdict.
- Current required-evidence integrity does not imply full clean-checkout required-evidence reproducibility; this plan must preserve that distinction.
- Tracking state and authority state remain independent.
- Provenance is mandatory for every newly tracked candidate; hash-only promotion is forbidden.
- No runtime, source, rendered, package, public-text, or sealed artifact surface becomes writable merely because a validation test references it.
- No test deletion, skip, `xfail`, assertion weakening, post-failure deselection, or denominator shrink is permitted.
- D0 is immutable and D1 may differ only by an owner-approved additive delta.
- A new test identity discovered after D1 freeze invalidates that D1 revision and every terminal use of its candidate evidence. It requires a reviewed successor additive delta, a new D1 inventory hash, OR-09B rescale/seal, and OR-08 amendment/preflight before a new candidate.
- No current-looking stale artifact may re-enter through bootstrap, fixture copying, ignore exceptions, or cache reuse.
- Failed attempts are append-only evidence and may not be laundered into a later success.
- `insufficient_preserved_evidence` is uncovered origin surface, prevents coverage completion, and has no owner-waiver path in this revision.
- B0 is an immutable diagnostic base identity. No implementation, repair, D1 addition, or candidate result may be recorded as B0 evidence.
- Live-manifest consumption is limited to a proven acyclic non-recursive leaf; aggregate-runner reentry, current-attempt result consumption, unfinished review/seal consumption, and every stored prior-PASS read are forbidden.
- Expected denied Git metadata attempts remain in the immutable receipt and require an exact ratified process/path/command/classification match; no successful repository write is allowlisted.
- OR-08 allowlist amendments are append-only and evidence-bound; they may add but never delete, weaken, broaden, or erase an attempt classification, and require a fresh preflight.
- OR-08 discovery runs report all denied-attempt classes and are not subject to enforcement zero predicates; candidate-bound preterminal, terminal, adoption, and reviewer runs are enforcement runs and require zero unexpected/unclassified denied attempts.
- Write-denial evidence describes observed attempted or successful events only. It does not claim counterfactual downstream writes that an earlier denial prevented, and it grants no writable diagnostic-run authority.
- The active D1 OR-09B revision must be identity-ratio-rescaled from the B0 measurement and bound to the exact D1 inventory hash before candidate execution.
- Evidence is valid only for the exact commit, tree, D1 inventory, environment receipt, route, and contract blob IDs it names.
- The durable terminal bundle must retain the immutable environment receipt and receipt hash after external-root disposal.
- `docs/EXECUTION_CONTRACT.md` and `docs/PLAN_TEMPLATE.md` are binding execution inputs at B0; their Git blob IDs must be recorded.
- A tracked artifact never self-binds its containing commit SHA; an external receipt or successor record performs commit binding.
- A `gate_input = true` top-level document may not embed its containing V0 SHA. Its blob is bound externally by an attempt receipt or S0. Only a `gate_input = false` DOC0 non-claim successor may embed an exact V0 reference.
- Independent closeout reviewer exclusions are: roadmap author/co-drafter, plan author/co-drafter, implementation participant, terminal-bundle constructor, prior closeout reviewer on the same chain, and owner. The current ChatGPT and Claude reviewers are excluded.
- Absence of an eligible reviewer sets `independent_review_gate = blocked` and terminal state `blocked`.
- Execution reporting must classify every in-scope validation as:
  - `validated`;
  - `out_of_scope`;
  - `unvalidated_but_in_scope`.
- Allowed closeout state names remain `complete`, `partial`, and `blocked`; the selected claim token is additional axis vocabulary, not a replacement for these state names. `partial` releases no downstream blocker.
- The current dirty workspace and its staged/untracked changes belong to the user and must not be modified, cleaned, reset, or used as success evidence.
- The dirty planning workspace may be read only for discovery, path-existence checks, and diagnostic code inspection.
- Transition from the dirty planning workspace to an implementation checkout is a separate operational handoff outside this plan and receives no implied branch, patch-transfer, staging, cleanup, or reset authorization.
- Top-level documentation updates are additive state reconciliation, not retrospective rewriting.
- Governance-document edits must preserve existing line endings and avoid content-unrelated byte churn.
- Gate greenness and the authority claim bind V0 only; DOC0 and later documentation-only HEADs are non-claim successors.
- `Iris Publish Boundary` is canonical in this plan; `Publish Boundary` is an abbreviated alias only.

## 12. Expected Closeout State

Target state: `complete`.

Execution entry state at revision `r6` plus `iris_aa49_four_plan_execution_sync_v1`: `ready_for_owner_authorized_phase0_after_G0_plan_set_materialization`.

- The review chain is complete.
- `Critical unresolved count = 0`.
- `blocking Important unresolved count = 0`.
- The four-plan synchronization is owner-directed and requires no additional plan-level review.
- `aa49e8f9fce19955a374b45d0744b1418a45ac9e` is the immutable ancestry/readpoint, while the clean synchronized plan-set descendant is the Phase 0 execution base.
- Implementation begins when the owner explicitly instructs it to begin.

On that instruction, Change 1/Phase 0 begins immediately. Changes 2–10 remain sequencing-blocked—not review-blocked—until OD-01 through OD-09, OR-01 through OR-08, and OR-09A are ratified and B0 is clean. The base OR-09B revision is produced from the dedicated immutable-B0 initial feasibility measurement and sealed before the first D0 census; an identity-ratio-rescaled revision is sealed after each D1 freeze and before the next candidate-bound run.

`complete` is available only when:

- the fixed logical authority, physical single-writer, exact claim, and approved-tooling allowlist are recorded;
- O0/P0/B0/R0/CXn/C0/G0/V0/S0/DOC0 relationships are recorded without self-reference or stale evidence reuse;
- `origin_command_provenance_status` is recorded as `identified` or `unidentifiable`, and any `unidentifiable` limitation is carried into the closeout;
- `origin_failure_surface_coverage_status = complete`, `unreconciled_origin_surface_count = 0`, `insufficient_preserved_evidence_count = 0`, and `coverage_complete_with_insufficient_evidence = false`;
- a clean exact V0 commit and the immutable external environment receipt are bound;
- the full environment receipt and matching hash are preserved in the durable terminal bundle;
- D0 is preserved and every D1 revision equals D0 plus only its owner-reviewed additive delta; a new test identity after preterminal failure invalidates the prior D1 before it is added;
- all four `B0_initial_*` projection-feasibility statuses are recorded exactly once against immutable B0 as diagnostic evidence;
- all four final `C0_preterminal_*` projection-feasibility statuses are `PASS` against the exact candidate SHA/tree selected unchanged as C0, and the attempt count remains within OR-09A;
- `c0_preterminal_feasibility_attempt_count_is_monotonic = true`; no D1 refreeze resets it, and `new_test_identity_without_D1_invalidation_count = 0`;
- the three route execution verdicts and aggregate execution verdict are separately reported as `PASS`, each carries `verdict_source`, `source_command_id`, `projection_membership_hash`, and `execution_result_hash`, aggregate-only identities pass, and sealed-route mutation count is zero;
- collection-error accounting closes with terminal `uncollected_due_to_collection_error = 0`;
- every test, dependency edge, failure disposition, producer, and provenance path is classified in its proper ledger;
- bootstrap uses only tracked or deterministically materialized declared inputs;
- every execution output is external to the checkout;
- tracked bytes/modes/types, untracked, ignored, stat/mtime, transient-write, cache, intra-run temp-state, and protected-surface checks pass;
- every observed attempted or successful checkout write event has a producer attribution, while denial-prevented downstream possibilities are explicitly outside observed counts and have an approved disposition;
- OR-08 preflight and run application prove full checkout/child-process coverage with no trace loss; discovery-run expected/unexpected/unclassified counts are reported, retained, and fully dispositioned; every census/D1 allowlist amendment is append-only and re-preflighted; every run has `successful_repository_write_count = 0`; and enforcement runs have `unexpected_denied_repository_write_attempt_count = 0` and `unclassified_denied_repository_write_attempt_count = 0`;
- all genuine in-scope regressions are repaired inside the allowlist without weakening the gate and have red→green evidence;
- two separate fresh checkouts pass with equivalent canonical bundles and no shared generated state;
- adversarial cases fail closed;
- the recursion negative fixture was reserved in the D1 additive delta, implemented before D1 freeze, and only rerun—not introduced—during Change 10;
- the canonical live-manifest/`legacy_combined_governance_route` container boundary matches across the terminal bundle and top-level documents without transferring this closure or DVF Body Compiler authority;
- any required-gate adoption targets only a proven non-recursive leaf, passes before/after invocation-DAG validation and a post-adoption rerun, and has `execution_dependency_cycle_count = 0`, `aggregate_runner_reentry_count = 0`, `current_attempt_result_dependency_count = 0`, and `stored_terminal_pass_read_count = 0`; otherwise `live_manifest_consumption = no`;
- `adoption_introduced_identity_absent_from_D1 = 0`;
- diagnostic `taxonomy_fallback_row_count` is reported and terminal `taxonomy_fallback_row_count = 0`;
- OR-09A execution-unit policy is honored, the base D0 OR-09B revision is measurement-bound, and the active terminal OR-09B revision is identity-ratio-rescaled and bound to the exact final D1 inventory hash;
- an eligible same-machine/different-operator reviewer independently reproduces final V0 after adoption;
- a separate owner seal is recorded;
- any successor record binds V0 rather than claiming its own unvalidated commit;
- DOC0, when present, is explicitly non-claim and does not inherit V0 gate greenness;
- `gate_input = true` top-level document fields agree with the terminal bundle without embedding V0 SHA, their blobs are externally bound to V0, and any exact V0 reference in top-level documentation appears only in a `gate_input = false` DOC0 non-claim successor;
- the terminal closeout packet repeats the exact downstream-unblock boundary below and enumerates every approval it does not grant.

If the owner declines the mandatory full gate, or any in-scope origin, environment, dependency, provenance, mutation, regression, repeatability, adoption, reviewer, or owner criterion remains unresolved, the closeout is `partial` or `blocked`. Neither state releases a downstream blocker or emits `Iris Clean-Checkout Full-Repository Validation Reproducibility Authority PASS`.

`complete + Iris Clean-Checkout Full-Repository Validation Reproducibility Authority PASS` removes only the downstream blocker whose stated reason is failure of this validation-reproducibility axis. It does not grant Phase 12 approval, Registry cutover approval, Naturalization approval, `Iris Publish Boundary` approval, package/release approval, or any other downstream authority PASS.
