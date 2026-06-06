# Iris DVF 3-3 Layer4 Boundary Namespace Reseal Round Plan

> 상태: Draft v0.4-pass-minor-feedback-applied
> 기준일: 2026-06-03
> 상위 기준: `docs/Philosophy.md`, `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`
> authority input: `Iris DVF 3-3 - Layer4 Boundary Namespace Re-Seal Round - 종합 최종 로드맵` (user-provided pasted roadmap)
> review input: `Iris DVF 3-3 Layer4 Boundary Namespace Re-Seal Round - 종합 최종 REVIEW` (user-provided pasted review). v0.2 applies Critical C1/C2/C3 by demoting template/contract attestation to a carry-forward limitation, separating read-only top-doc inputs from post-gate writes, and making adversarial review PASS mandatory for `complete` closeout. It also incorporates important/minor feedback for M2 absence terminal, unconditional predecessor sha256 proof, non-`Done/` draft placement, selected branch metadata, artifact-list consistency, forbidden scan patterns, and naming/ceiling token normalization. v0.3 clarifies review-gate ordering: adversarial review is a pre-promotion artifact, not a post-gate side effect. v0.4 incorporates PASS-cycle Minor feedback by defining predecessor hash manifest schema, requiring `m2_basis_status` in B1/B3 closeout metadata, carrying DECISIONS `absorption:` tokens, and separating current-target branch tokens from axis disposition tokens.
> 직접 상위 readpoint:
> - 2026-04-29 Layer4 Absorption Policy Round `closed_with_policy_sealed_zero_count_production_safe`
> - 2026-05-31 Layer4 Boundary Current Corpus Lock Round `closed_with_layer4_boundary_current_corpus_locked_no_count_inheritance_design_preflight`
> - 2026-05-31 Layer4 Confirmed Detector Field Map Seal Round `closed_with_confirmed_measurement_unavailable_trace_absent`
> - 2026-06-01 Layer4 Trace-Edge Authority Admission Round `EDGE_AUTHORITY_PRODUCED_AND_ADMITTED`
> - 2026-06-02 Layer4 Confirmed Detector Field Map Reseal Round `closed_with_layer4_confirmed_detector_field_map_resealed`
> - 2026-06-02 Layer4 Confirmed Current Count Remeasurement Round `closed_with_layer4_confirmed_current_count_measured_positive`
> - 2026-06-03 Layer4 Confirmed Measurement Canonicalization Boundary Seal Round `closed_with_layer4_confirmed_measurement_canonicalized_as_readpoint_only`
> 계획 형식: `docs/PLAN_TEMPLATE.md` carry-forward form basis. This line records the intended 1-12 section form only; it is not semantic authority and is not sufficient evidence for `complete` closeout.
> template_contract_review_limitation: `docs/PLAN_TEMPLATE.md` / `docs/EXECUTION_CONTRACT.md` conformance must not be used as positive complete-closeout evidence unless the execution closeout includes local read/verification evidence for those files. The closeout ceiling is anchored to sealed predecessor tokens, produced round-local evidence, adversarial review PASS, and `docs_governance_boundary_only`.
> 실행 상태: planning authority only. This document does not mutate source facts, source decisions, rendered text, runtime Lua, packaged Lua, bridge payload, state axes, public-facing behavior, top-doc closeout state, or release readiness.

---

## 1. Objective

이번 execution plan의 목적은 `LAYER4_ABSORPTION_CONFIRMED`를 `FUNCTION_NARROW / ACQ_DOMINANT` disposition 계열과 분리된 independent `layer_boundary_hard_block` namespace로 재봉인하는 것이다.

이 라운드는 이미 닫힌 detector execution count를 다시 계산하지 않는다. 라운드가 답해야 하는 질문은 다음으로 제한한다.

```text
LAYER4_ABSORPTION_CONFIRMED는 current governance에서
FUNCTION_NARROW / ACQ_DOMINANT disposition table의 row인가,
아니면 독립된 Layer4 boundary hard-block namespace인가?

confirmed_count = 24와 current build application target = 0은
같은 metric인가, 별도 축인가?
```

Allowed answer:

```text
LAYER4_ABSORPTION_CONFIRMED is an independent layer_boundary_hard_block namespace.
confirmed_count = 24 is sealed_detector_execution measurement_readpoint_only.
current build application target is a separate axis and must not be silently merged with M1.
```

Round id:

```text
layer4_boundary_namespace_reseal_round
```

Allowed complete branch tokens:

```text
closed_with_layer4_boundary_namespace_resealed_b1_m2_axis
closed_with_layer4_boundary_namespace_resealed_b2_m1_readpoint
closed_with_layer4_boundary_namespace_resealed_b3_dual_axis
```

Required current-target branch decision tokens:

```text
B1_M2_axis_reseal
B2_M1_readpoint_additive_succession
B3_dual_axis_explicit_seal
```

Current-target axis disposition tokens:

```text
application_target_measurement_unavailable
```

Blocked or incomplete branch tokens:

```text
blocked_current_target_branch_not_selected
blocked_namespace_disposition_mixed
blocked_forbidden_positive_claim_detected
blocked_non_mutation_invariant_failed
blocked_public_exposure_detected
blocked_additive_only_invariant_failed
blocked_review_gate_failed
blocked_application_target_basis_missing
partial_namespace_sealed_current_target_unresolved
implemented_only
```

Success may claim only when the selected complete branch token is explicit:

```text
LAYER4_ABSORPTION_CONFIRMED was sealed as an independent Layer4 boundary
hard-block namespace, separated from FUNCTION_NARROW / ACQ_DOMINANT.
confirmed_count = 24 remains a detector-execution measurement readpoint only.
The selected M1/M2 branch defines the current-target relationship.
Adversarial review passed within docs_governance_boundary_only.
```

Success must not claim:

```text
Layer4 absorption resolved
Layer4 policy redesign
semantic quality completion
publish mutation review opened
source facts mutation
source decisions mutation
rendered text mutation
runtime Lua mutation
packaged Lua mutation
bridge runtime payload mutation
quality_state mutation
publish_state mutation
runtime_state mutation
Browser / Wiki / Tooltip public exposure
FUNCTION_NARROW second rollout
ACQ_DOMINANT publish review
SUSPECT tier defined
runtime rollout
manual in-game validation pass
deployment
Workshop readiness
B42 readiness
release readiness
ready_for_release
admitted row count shortcut
prior zero-count inheritance
```

---

## 2. Scope

This is a docs/governance and static-invariant round. It consumes sealed predecessor readpoints and may create round-local governance artifacts plus additive top-doc closeout entries if hard gates pass.

In scope:

* Read-only inventory of the Layer4 predecessor chain.
* Explicit separation of `LAYER4_ABSORPTION_CONFIRMED` from `FUNCTION_NARROW / ACQ_DOMINANT`.
* Namespace map declaring `layer_boundary_hard_block_namespace`.
* M1/M2 disambiguation table.
* Required branch decision among B1, B2, or B3 before `complete` closeout.
* M2-axis basis or explicit `application_target_measurement_unavailable` terminal for B1/B3.
* SUSPECT boundary lock as out-of-scope / no-current-authority.
* Protected-surface non-mutation guard for source, rendered, runtime, packaged, bridge, and state surfaces.
* Unconditional predecessor sealed-artifact sha256 comparison for referenced predecessor artifacts.
* Public-facing non-exposure scan for Browser / Wiki / Tooltip wording.
* Mandatory adversarial review PASS before `complete` closeout.
* Additive-only closeout updates to `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, and `docs/ROADMAP.md`, only in Change 6 after hard gates and review pass.

### Explicitly Out Of Scope

* Recomputing `confirmed_count = 24`.
* Reopening detector execution, field-map reseal, or trace-edge authority admission.
* Treating `TRACE_EDGE_ABSENT_MEASUREMENT_UNAVAILABLE` as count `0`.
* Treating admitted generated edge row count `24` as detector count shortcut.
* Rewriting predecessor closeout bodies.
* Rewriting structural disposition tables.
* Opening `FUNCTION_NARROW` second rollout.
* Opening `ACQ_DOMINANT` publish mutation review.
* Defining SUSPECT detector or SUSPECT tier.
* Mutating source facts, source decisions, rendered text, runtime Lua, packaged Lua, bridge payload, or state fields.
* Browser / Wiki / Tooltip exposure.
* Manual in-game, multiplayer, long-session, deployment, Workshop, B42, or release validation.

---

## 3. Non-Goals

This plan does not attempt to:

* Prove that Layer4 absorption is resolved.
* Redesign Layer4 policy.
* Decide that a positive measurement count creates publish or runtime authority.
* Decide that current build application target `0` and detector confirmed count `24` are the same metric.
* Convert quality, publish, or runtime state from internal/offline evidence into user-facing status.
* Establish SUSPECT as a fallback or report-only authority tier.
* Expand Iris beyond its render-only runtime posture.
* Create release, Workshop, or B42 readiness claims.

---

## 4. Assumptions

* `docs/Philosophy.md` remains the top authority.
* Iris remains a 100% Lua wiki module that presents practical facts without recommendation, comparison, or policy judgment.
* `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, and `docs/ROADMAP.md` are the canonical governance surfaces for this round.
* The current sealed measurement readpoint is `confirmed_count = 24` by detector execution.
* The count basis is `sealed_detector_execution`, not admitted row count shortcut.
* Prior zero-count and trace-absent predecessor states are historical readpoints and are not inherited as current count.
* `FUNCTION_NARROW` and `ACQ_DOMINANT` remain closed in their current states and are not reopened by this plan.
* Any `complete` closeout must include a stated validation ceiling of `docs_governance_boundary_only` or a narrower non-runtime equivalent.
* `PLAN_TEMPLATE.md` / `EXECUTION_CONTRACT.md` conformance is treated as a carry-forward limitation unless the execution closeout includes local verification evidence.

---

## 5. Repository Areas Affected

### Code

* None.

### Docs

* Current draft plan: `docs/Iris/iris-dvf-3-3-layer4-boundary-namespace-reseal-round-plan.md`
* Read-only canonical references during Changes 1-5:
  * `docs/DECISIONS.md`
  * `docs/ARCHITECTURE.md`
  * `docs/ROADMAP.md`
* Pre-promotion review target:
  * `docs/Iris/iris-dvf-3-3-layer4-boundary-namespace-reseal-round-review.md`
* Post-gate additive write targets during Change 6 only:
  * `docs/DECISIONS.md`
  * `docs/ARCHITECTURE.md`
  * `docs/ROADMAP.md`
  * `docs/Iris/iris-dvf-3-3-layer4-boundary-namespace-reseal-round-closeout.md`

Current plan / review / closeout drafts remain in the active non-`Done` planning surface under `docs/Iris/` until the round is sealed. Round-local machine-readable evidence remains under `Iris/build/description/v2/staging/compose_contract_migration/layer4_boundary_namespace_reseal_round/`. After sealed closeout, final documents may be moved or copied into `docs/Iris/Done/` only if that promotion is explicitly recorded.

### Config

* None.

### Generated Artifacts

Execution may create round-local governance artifacts only:

* `Iris/build/description/v2/staging/compose_contract_migration/layer4_boundary_namespace_reseal_round/layer4_absorption_authority_chain.json`
* `Iris/build/description/v2/staging/compose_contract_migration/layer4_boundary_namespace_reseal_round/layer4_absorption_readpoint_inventory.md`
* `Iris/build/description/v2/staging/compose_contract_migration/layer4_boundary_namespace_reseal_round/layer4_absorption_namespace_map.json`
* `Iris/build/description/v2/staging/compose_contract_migration/layer4_boundary_namespace_reseal_round/layer4_absorption_disposition_separation_report.md`
* `Iris/build/description/v2/staging/compose_contract_migration/layer4_boundary_namespace_reseal_round/current_target_branch_decision.md`
* `Iris/build/description/v2/staging/compose_contract_migration/layer4_boundary_namespace_reseal_round/layer4_absorption_suspect_boundary_lock.md`
* `Iris/build/description/v2/staging/compose_contract_migration/layer4_boundary_namespace_reseal_round/layer4_absorption_non_claims.json`
* `Iris/build/description/v2/staging/compose_contract_migration/layer4_boundary_namespace_reseal_round/layer4_absorption_surface_invariant_report.json`
* `Iris/build/description/v2/staging/compose_contract_migration/layer4_boundary_namespace_reseal_round/layer4_absorption_public_exposure_scan.json`
* `Iris/build/description/v2/staging/compose_contract_migration/layer4_boundary_namespace_reseal_round/predecessor_sealed_artifact_hashes.json`
* `Iris/build/description/v2/staging/compose_contract_migration/layer4_boundary_namespace_reseal_round/predecessor_sealed_artifact_hash_diff.md`

No runtime payload, packaged Lua, rendered text, source fact, source decision, or state artifact is generated by this plan.

---

## 6. Planned Changes

### Change 1 - Readpoint Chain Inventory

Purpose:

Establish the exact predecessor chain and prevent prior zero-count, trace-absent, generated row count, and detector count from being collapsed into one ambiguous value.

Read-only inputs:

* `docs/DECISIONS.md`
* `docs/ARCHITECTURE.md`
* `docs/ROADMAP.md`

Write targets:

* `Iris/build/description/v2/staging/compose_contract_migration/layer4_boundary_namespace_reseal_round/layer4_absorption_authority_chain.json`
* `Iris/build/description/v2/staging/compose_contract_migration/layer4_boundary_namespace_reseal_round/layer4_absorption_readpoint_inventory.md`

Implementation Notes:

* Inventory the 2026-04-29, 2026-05-31, 2026-06-01, 2026-06-02, and 2026-06-03 Layer4 readpoints.
* Record `confirmed_count = 24` only as detector execution output.
* Record `current build application target = 0` only as a separate M2-axis predecessor/application-target concept unless selected branch says otherwise.

Validation:

* Predecessor readpoint count matches known chain.
* `prior_zero_count_inherited = false`.
* `admitted_row_count_shortcut_used = false`.
* `trace_absent_interpreted_as_zero = false`.

---

### Change 2 - Namespace Separation Seal

Purpose:

Seal `LAYER4_ABSORPTION_CONFIRMED` as an independent `layer_boundary_hard_block_namespace`.

Read-only inputs:

* `docs/DECISIONS.md`
* `docs/ARCHITECTURE.md`
* `docs/ROADMAP.md`

Write targets:

* `Iris/build/description/v2/staging/compose_contract_migration/layer4_boundary_namespace_reseal_round/layer4_absorption_namespace_map.json`
* `Iris/build/description/v2/staging/compose_contract_migration/layer4_boundary_namespace_reseal_round/layer4_absorption_disposition_separation_report.md`

Implementation Notes:

* Declare the relationship to `FUNCTION_NARROW` as `separated`.
* Declare the relationship to `ACQ_DOMINANT` as `separated`.
* Forbid adding Layer4 confirmed count into structural or publish disposition tables.
* Preserve `confirmed_count = 24` as `measurement_readpoint_only`.

Validation:

* `LAYER4_ABSORPTION_CONFIRMED` is present in the independent namespace map.
* No new `FUNCTION_NARROW / ACQ_DOMINANT` publish-disposition row is introduced.
* No writer, publish, quality, runtime, rollout, or release authority is introduced.

---

### Change 3 - Current Target Branch Decision

Purpose:

Prevent M1 `confirmed_count = 24` and M2 `current build application target = 0` from being silently merged.

Read-only inputs:

* `docs/DECISIONS.md`
* `docs/ARCHITECTURE.md`
* `docs/ROADMAP.md`

Write targets:

* `Iris/build/description/v2/staging/compose_contract_migration/layer4_boundary_namespace_reseal_round/current_target_branch_decision.md`

Implementation Notes:

One branch must be selected before `complete` closeout:

* B1: M2-axis reseal. Current build application target is treated as the operative target axis, with M1 preserved separately. B1 must record current corpus anchor and measurement basis before any `0` reseal claim. If that basis is unavailable, B1 must record `application_target_measurement_unavailable` and must not claim a current `0` reseal. In all B1 outcomes, `confirmed_count = 24 remains M1 measurement_readpoint_only`.
* B2: M1 readpoint additive succession. Detector count `24` is the current measurement readpoint, and `0 reseal` wording is not applied to M1.
* B3: dual-axis explicit seal. M1 measurement readpoint and M2 build application target are both named, with no inheritance relation. B3 must record either M2 corpus anchor / measurement basis or `application_target_measurement_unavailable`.

Validation:

* Exactly one branch token is selected for complete closeout.
* Non-selected branches are recorded as not executed.
* B1/B3 M2 axis records a measurement basis or `application_target_measurement_unavailable`.
* No branch claims unvalidated runtime behavior.

---

### Change 4 - SUSPECT Boundary Lock

Purpose:

Keep SUSPECT out of current authority until a separate approved detector round exists.

Write targets:

* `Iris/build/description/v2/staging/compose_contract_migration/layer4_boundary_namespace_reseal_round/layer4_absorption_non_claims.json`
* `Iris/build/description/v2/staging/compose_contract_migration/layer4_boundary_namespace_reseal_round/layer4_absorption_suspect_boundary_lock.md`

Implementation Notes:

* Set `suspect_tier_defined = false`.
* Set `suspect_detector_round_opened = false`.
* Set `suspect_current_authority = false`.
* Preserve any SUSPECT-like material as non-current report-only context unless future authority opens it.

Validation:

* SUSPECT schema absent.
* SUSPECT detector input absent.
* SUSPECT count absent.
* SUSPECT public exposure absent.
* SUSPECT-driven mutation absent.

---

### Change 5 - Protected Surface Non-Mutation Guard

Purpose:

Prove the round stayed inside docs/governance/static-invariant scope.

Read-only inputs:

* Referenced predecessor sealed artifacts.
* Protected source / rendered / runtime / packaged / bridge / state surfaces.

Write targets:

* `Iris/build/description/v2/staging/compose_contract_migration/layer4_boundary_namespace_reseal_round/layer4_absorption_surface_invariant_report.json`
* `Iris/build/description/v2/staging/compose_contract_migration/layer4_boundary_namespace_reseal_round/layer4_absorption_public_exposure_scan.json`
* `Iris/build/description/v2/staging/compose_contract_migration/layer4_boundary_namespace_reseal_round/predecessor_sealed_artifact_hashes.json`
* `Iris/build/description/v2/staging/compose_contract_migration/layer4_boundary_namespace_reseal_round/predecessor_sealed_artifact_hash_diff.md`

Implementation Notes:

* Check source facts, source decisions, rendered text, runtime Lua, packaged Lua, bridge payload, `quality_state`, `publish_state`, and `runtime_state`.
* Compare predecessor sealed-artifact sha256 values unconditionally, regardless of whether top-doc promotion is later performed.
* `predecessor_sealed_artifact_hashes.json` must use at least these fields per entry:
  * `readpoint_id`
  * `artifact_path_or_topdoc_anchor`
  * `expected_sha256_or_not_applicable`
  * `actual_sha256_or_not_applicable`
  * `comparison_status`
  * `unavailable_reason`
* Check Browser / Wiki / Tooltip exposure terms.
* Limit hash proof to non-mutation support, not runtime equivalence proof.

Validation:

* Protected surface delta is `0`.
* Predecessor sealed-artifact sha256 comparison passes.
* Every predecessor hash manifest entry has the required schema fields.
* `comparison_status` is one of `matched`, `not_applicable`, or `unavailable_with_reason`.
* Public exposure scan is `0`.
* Validation ceiling remains `docs_governance_boundary_only`.

---

### Change 6 - Additive Closeout And Top-Doc Alignment

Purpose:

Record the completed branch and namespace separation without rewriting sealed predecessor bodies.

Pre-gate prerequisites:

* Changes 1-5 completed.
* Exactly one selected branch token recorded.
* Forbidden claim scan passed.
* Predecessor sealed-artifact sha256 comparison passed.
* Protected-surface non-mutation guard passed.
* Public-facing non-exposure scan passed.
* Adversarial review PASS recorded in `docs/Iris/iris-dvf-3-3-layer4-boundary-namespace-reseal-round-review.md`.

Post-gate write targets:

* `docs/DECISIONS.md`
* `docs/ARCHITECTURE.md`
* `docs/ROADMAP.md`
* `docs/Iris/iris-dvf-3-3-layer4-boundary-namespace-reseal-round-closeout.md`

Implementation Notes:

* Add only additive closeout entries.
* Preserve predecessor readpoints as historical/current inputs.
* Record the selected B1/B2/B3 branch and non-selected branch disposition.
* Include a `selected_branch` field or first-paragraph equivalent in the closeout.
* If B1 or B3 is selected, include `m2_basis_status` with either a concrete basis label or `application_target_measurement_unavailable`.
* Additive `docs/DECISIONS.md` closeout must carry house-style absorption tokens:
  * `absorption: COMMON-RELEASE-NONDECISION / COMMON-RUNTIME-SURFACE-NONMUTATION / COMMON-EVIDENCE-TRACE`
* Include non-claims for resolved, mutation, publish, exposure, rollout, and release readiness.
* Use one of the branch-specific closeout tokens:
  * `closed_with_layer4_boundary_namespace_resealed_b1_m2_axis`
  * `closed_with_layer4_boundary_namespace_resealed_b2_m1_readpoint`
  * `closed_with_layer4_boundary_namespace_resealed_b3_dual_axis`

Validation:

* Addendum-only diff.
* Forbidden claim scan pass.
* B1/B3 closeout metadata includes `m2_basis_status`.
* DECISIONS additive closeout includes the required `absorption:` token line.
* Adversarial review PASS using `docs/REVIEW_TEMPLATE.md` exists before top-doc promotion.
* Review failure terminal is `blocked_review_gate_failed`.

---

## 7. Validation Plan

### Automated Validation

* `rg` forbidden-claim scan over modified docs and round artifacts.
  * Minimum forbidden patterns:
    * `Layer4 absorption resolved`
    * `Layer4 resolved`
    * `publish review opened`
    * `publish mutation review opened`
    * `runtime rollout`
    * `public exposure enabled`
    * `Browser exposure`
    * `Wiki exposure`
    * `Tooltip exposure`
    * `ready_for_release`
    * `release-ready`
    * `Workshop readiness`
    * `B42 readiness`
    * `SUSPECT tier defined`
    * `admitted row count shortcut`
    * `prior zero-count inheritance`
  * Scan hits inside explicit non-claim / must-not-claim / forbidden-pattern sections must be bucketed as `allowed_non_claim_hit`.
  * Any unbucketed hit or positive-claim hit fails the gate.
* JSON parse validation for round-local `.json` artifacts.
* JSONL parse validation for any round-local `.jsonl` artifact, if created.
* Determinism check for round-local generated governance artifacts, if generation scripts are used.
* Unconditional predecessor sealed-artifact sha256 comparison for referenced predecessor artifacts.
* Protected-surface hash comparison for source/rendered/runtime/packaged/bridge/state surfaces.
* `git diff --stat` and `git diff` review for additive-only scope.

### Manual Validation

* Read the final closeout wording against `docs/Philosophy.md`.
* Confirm `LAYER4_ABSORPTION_CONFIRMED` is not described as resolved.
* Confirm `FUNCTION_NARROW` and `ACQ_DOMINANT` are not reopened.
* Confirm M1/M2 branch decision is explicit and single.
* Confirm B1/B3 includes M2 measurement basis or `application_target_measurement_unavailable`.
* Confirm B1/B3 closeout metadata includes `m2_basis_status`.
* Confirm DECISIONS additive closeout includes `absorption: COMMON-RELEASE-NONDECISION / COMMON-RUNTIME-SURFACE-NONMUTATION / COMMON-EVIDENCE-TRACE`.
* Confirm validation ceiling and non-claims are present.
* Confirm adversarial review PASS is present before any `complete` closeout.

### Validation Limits

* No runtime validation.
* No in-game validation.
* No multiplayer validation.
* No long-session validation.
* No deployment validation.
* No external mod compatibility sweep.
* No release checklist.
* No B42 validation.
* No semantic quality completion validation.
* No SUSPECT detector validation.
* No full runtime equivalence proof.
* `PLAN_TEMPLATE.md` / `EXECUTION_CONTRACT.md` conformance is not used as success evidence unless execution closeout includes local verification evidence.

---

## 8. Risk Surface Touch

### Authority Surface

Touched. This round may seal namespace placement and branch disposition for `LAYER4_ABSORPTION_CONFIRMED`.

It must not create publish, runtime, quality, public-facing, rollout, or release authority.

### Runtime Behavior Surface

None. Runtime Lua, packaged Lua, bridge payload, game behavior, and default runtime behavior must not change.

### Compatibility Surface

None expected. No API, SPI, external format, mod compatibility, or PZ runtime compatibility surface changes are planned.

### Sealed Artifact Surface

Touched if execution creates round-local governance artifacts or protected-surface hash manifests. Predecessor sealed artifacts are read-only inputs and must not be rewritten. Referenced predecessor sealed artifacts require sha256 comparison regardless of top-doc promotion.

### Public-Facing Output Surface

None. Browser, Wiki, Tooltip, release notes, Workshop copy, README release claims, and user-facing status surfaces must not change.

---

## 9. Risk Analysis

### Architecture Risk

* `LAYER4_ABSORPTION_CONFIRMED` could be reabsorbed into `FUNCTION_NARROW / ACQ_DOMINANT` disposition language.
* M1 `24` and M2 `0` could be implicitly merged without branch decision.
* Hard-block namespace wording could be misread as runtime or publish authority.

### Runtime Risk

* Low if scope is preserved.
* Any runtime Lua, packaged Lua, bridge payload, rendered text, or state mutation is a scope violation.

### Compatibility Risk

* Low if no runtime/API/output formats change.
* Compatibility claims are out of scope and must not be inferred from docs/governance validation.

### Regression Risk

* Additive top-doc entries could accidentally overwrite or supersede predecessor readpoints.
* Forbidden claim wording could imply resolved, publish review, public exposure, or release readiness.
* Hash proof could be overstated as runtime behavior equivalence.

---

## 10. Rollback Plan

Because this plan targets docs/governance and round-local artifacts only, rollback is limited to additive document and artifact changes.

```text
round-local artifacts only
-> discard round-local artifacts

staging draft only
-> discard staging draft

top-doc additive entry promoted
-> revert additive entry or add corrective successor entry, depending on review policy

source/rendered/runtime/state mutation detected
-> Stop-the-Line, classify as scope violation, revert the mutation, and do not close complete

public-facing exposure detected
-> Stop-the-Line, remove exposure, and do not close complete
```

Predecessor sealed readpoints are not rollback targets.

---

## 11. Governance Constraints

* `docs/Philosophy.md` compliance.
* Hub & Spoke / SPI boundaries remain unchanged.
* Iris remains wiki/render-only at runtime.
* Runtime/build-time separation remains preserved.
* Sealed predecessor bodies are not rewritten.
* Additive amendment is preferred for top-doc alignment.
* `LAYER4_ABSORPTION_CONFIRMED` remains separated from `FUNCTION_NARROW / ACQ_DOMINANT`.
* `confirmed_count = 24` remains detector-execution measurement readpoint only.
* Prior zero-count is not inherited as current count.
* Admitted edge row count is not used as detector count shortcut.
* B1/B3 must record M2 measurement basis or `application_target_measurement_unavailable`.
* B1/B3 closeout must expose that result through `m2_basis_status`.
* SUSPECT tier is not defined without a separate approved detector round.
* Source facts, source decisions, rendered text, runtime Lua, packaged Lua, bridge payload, `quality_state`, `publish_state`, and `runtime_state` must not mutate.
* Browser / Wiki / Tooltip public exposure remains closed.
* Predecessor sealed-artifact sha256 comparison is mandatory.
* Predecessor hash manifest entries must expose readpoint, anchor/path, expected status, actual status, comparison status, and unavailable reason.
* DECISIONS additive closeout must carry `absorption: COMMON-RELEASE-NONDECISION / COMMON-RUNTIME-SURFACE-NONMUTATION / COMMON-EVIDENCE-TRACE`.
* Adversarial review PASS is mandatory before any `complete` closeout.
* Validation ceiling must be stated as `docs_governance_boundary_only` or narrower for any `complete` closeout.

---

## 12. Expected Closeout State

Expected closeout target after execution:

```text
complete
```

`complete` is allowed only if all of the following are true within the stated validation ceiling:

* `LAYER4_ABSORPTION_CONFIRMED` is sealed as independent `layer_boundary_hard_block_namespace`.
* It is separated from `FUNCTION_NARROW / ACQ_DOMINANT`.
* `confirmed_count = 24` remains `measurement_readpoint_only`.
* Exactly one current-target branch is recorded: B1, B2, or B3.
* The closeout uses the matching branch-specific token:
  * `closed_with_layer4_boundary_namespace_resealed_b1_m2_axis`
  * `closed_with_layer4_boundary_namespace_resealed_b2_m1_readpoint`
  * `closed_with_layer4_boundary_namespace_resealed_b3_dual_axis`
* Non-selected branches are recorded as not executed.
* B1/B3 records M2 measurement basis or `application_target_measurement_unavailable`.
* B1/B3 closeout includes `m2_basis_status`.
* B1, if selected, explicitly states `confirmed_count = 24 remains M1 measurement_readpoint_only`.
* SUSPECT remains out of scope and not current authority.
* Predecessor sealed-artifact sha256 comparison passes.
* `predecessor_sealed_artifact_hashes.json` entries include the required schema fields.
* Protected-surface non-mutation guard passes.
* Public-facing non-exposure scan passes.
* Additive-only documentation rule passes.
* Forbidden claim scan passes.
* Adversarial review PASS is recorded.
* DECISIONS additive closeout includes the required `absorption:` token line.
* Validation ceiling is recorded as `docs_governance_boundary_only` or a narrower non-runtime equivalent.

If current-target branch selection is not made, expected closeout becomes:

```text
partial_namespace_sealed_current_target_unresolved
```

If validation is not run after document or artifact changes, expected closeout becomes:

```text
implemented_only
```

If B1/B3 is selected but M2 basis is missing and no explicit unavailable terminal is recorded, expected closeout becomes:

```text
blocked_application_target_basis_missing
```

If adversarial review does not pass, expected closeout becomes:

```text
blocked_review_gate_failed
```

If authority, mutation, exposure, or additive-only invariants fail, expected closeout becomes:

```text
blocked
```
