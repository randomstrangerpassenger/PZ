# Iris DVF 3-3 Layer4 Current Build Application Target Remeasurement / Zero Reseal Round Plan

> 상태: Draft v0.4-current-surface-zero-reseal-execution-amendment
> 기준일: 2026-06-03
> 상위 기준: `docs/Philosophy.md`, `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`
> authority input: `Iris DVF 3-3 Layer4 Current Build Application Target Remeasurement / Zero Reseal Round - 종합 ROADMAP` (user-provided pasted roadmap)
> review input: `Iris DVF 3-3 Layer4 Current Build Application Target Remeasurement / Zero Reseal Round - 종합 REVIEW` (user-provided pasted review). v0.2 applies Critical C1/C2/C3 by adding path/hash/line-count proof for the plan template and execution contract, routing system-wide build consumer absence to first-class basis-unavailable seal instead of zero, and promoting basis unavailable as a complete additive terminal rather than a blocked validation failure. v0.2 also aligns branch tokens, review vocabulary, build-consumer basis schema, protected-surface hashes, deterministic claim-scan bucketing, and gated-promotion ordering.
> pass review input: `Iris DVF 3-3 Layer4 Current Build Application Target Remeasurement / Zero Reseal Round - 종합 REVIEW` (Cycle 2 PASS, user-provided pasted review). v0.3 applies optional PASS feedback by repeating Branch C's non-count/non-zero meaning, renaming partition `blocked` bucket language to `unresolved_bucket`, and carrying template/contract identity-proof independence limits into validation ceiling.
> execution amendment: v0.4 supersedes v0.2/v0.3 no-consumer-to-Branch-C language for this round. A complete current production/build/runtime surface scan with zero `LAYER4_ABSORPTION_CONFIRMED` application paths is accepted as the M2 measurement basis for Branch B zero reseal. This is not M1 `24`, admitted-row, diagnostic-residue, prior-zero, or SUSPECT inheritance.
> 직접 상위 readpoint:
> - 2026-05-31 Layer4 Boundary Current Corpus Lock Round `closed_with_layer4_boundary_current_corpus_locked_no_count_inheritance_design_preflight`
> - 2026-05-31 Layer4 Confirmed Detector Field Map Seal Round `closed_with_confirmed_measurement_unavailable_trace_absent`
> - 2026-06-01 Layer4 Trace-Edge Authority Admission Round `EDGE_AUTHORITY_PRODUCED_AND_ADMITTED`
> - 2026-06-02 Layer4 Confirmed Detector Field Map Reseal Round `closed_with_layer4_confirmed_detector_field_map_resealed`
> - 2026-06-02 Layer4 Confirmed Current Count Remeasurement Round `closed_with_layer4_confirmed_current_count_measured_positive`
> - 2026-06-03 Layer4 Confirmed Measurement Canonicalization Boundary Seal Round `closed_with_layer4_confirmed_measurement_canonicalized_as_readpoint_only`
> - 2026-06-03 Layer4 Boundary Namespace Reseal Round `closed_with_layer4_boundary_namespace_resealed_b3_dual_axis`
> - 2026-06-03 Layer4 current build application target follow-up mapping: M2 current checkout build application target count remains unsealed and separate from M1 `confirmed_count = 24`.
> 계획 형식: `docs/PLAN_TEMPLATE.md`; path verified; sha256 `38D70D4D624733DB4D24F047E0B737A47C75522A967C84F06FE5AABC5EBD9BA1`; line_count `109`
> execution contract reference: `docs/EXECUTION_CONTRACT.md`; path verified; sha256 `A185BBD78EB849B0310D9AADC9102CB156B892513266FAC0EC7903EB3D3A9493`; line_count `220`
> review verdict vocabulary: `docs/REVIEW_TEMPLATE.md` uses `PASS / WARN / FAIL`; this plan does not introduce an extra conditional verdict token as a closeout gate.
> template/contract verify status: accessible governance surface identity proof recorded above.
> 실행 상태: planning authority only. This document does not execute measurement, mutate source facts, source decisions, rendered text, runtime Lua, packaged Lua, bridge payload, state axes, public-facing behavior, publish review, rollout, or release readiness.

---

## 1. Objective

이번 execution plan의 목적은 `LAYER4_ABSORPTION_CONFIRMED`의 M2 축, 즉 current checkout / current build 기준 실제 build application target count를 측정하고, current production/build/runtime surface scan에서 적용 경로가 없으면 current M2 application target `0`으로 재봉인하는 것이다.

이번 라운드가 답해야 하는 질문은 다음 하나로 제한한다.

```text
current checkout/current build 기준으로
LAYER4_ABSORPTION_CONFIRMED build application target이 실제로 존재하는가?
존재하지 않는다면 그 0은 current production/build/runtime surface scan 위의 genuine-zero인가?
측정 입력이 M1 `24`, admitted row count, diagnostic residue, prior zero-count, or SUSPECT inheritance 없이 닫혔는가?
```

M1과 M2는 별도 축으로 유지한다.

```text
M1 confirmed_count = 24
  -> detector-execution measurement readpoint only

M2 current build application target count
  -> current checkout/current build가 실제로 적용해야 하는 target count
```

Allowed complete branch tokens:

```text
closed_with_layer4_m2_current_build_application_target_measured_positive
closed_with_layer4_m2_current_build_application_target_zero_resealed
closed_with_layer4_m2_application_target_basis_unavailable_carried_forward
```

Canonical blocked gate tokens:

```text
blocked_predecessor_non_mutation_or_identity_gate_failed
blocked_non_mutation_invariant_failed
blocked_public_exposure_detected
blocked_claim_overreach
blocked_review_gate_failed
blocked_additive_only_invariant_failed
blocked_measurement_artifact_determinism_failed
```

Canonical partial/defer token:

```text
deferred_pending_separate_basis_definition_or_suspect_authorization
```

Success may claim only one of the following:

```text
M2 current build application target was measured positive.
M2 current build application target was measured as genuine current zero.
M2 application target measurement/basis was unavailable and sealed as a first-class fail-loud carry-forward terminal.
```

Success must not claim:

```text
Layer4 absorption resolved
Layer4 policy redesign
semantic quality completion
M1 confirmed_count rewrite
M1 confirmed_count remeasurement
FUNCTION_NARROW second rollout
ACQ_DOMINANT publish review
SUSPECT tier defined
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
Browser / Wiki / Tooltip behavior change
public-facing exposure
runtime rollout
manual in-game validation pass
deployment
Workshop readiness
B42 readiness
release readiness
ready_for_release
M1 24 inherited as M2 target count
prior zero-count inherited as current zero
measurement unavailable collapsed into zero
```

---

## 2. Scope

This is a governance and measurement-readpoint planning round for Iris DVF 3-3 Layer4. Execution under this plan may create round-local measurement artifacts and additive governance closeout records, but only after all hard gates pass.

In scope:

* Predecessor non-mutation and identity gate over sealed Layer4 readpoints.
* Current build application surface definition.
* Excluded surface definition.
* M2 measurement basis availability check.
* M2 application target predicate definition.
* M2 non-target reason code definition.
* Current checkout scan for `LAYER4_ABSORPTION_CONFIRMED` occurrences.
* Target / non-target / unresolved partition.
* Positive target seal, genuine-zero reseal, or first-class basis-unavailable terminal seal.
* M1/M2 no-inheritance guard.
* Protected surface non-mutation proof.
* Public-facing non-exposure scan.
* Adversarial review before top-doc promotion.
* Additive-only updates to governance docs after gate pass.

### Explicitly Out Of Scope

* Layer4 policy redesign.
* `LAYER4_ABSORPTION_CONFIRMED` definition change.
* M1 detector count remeasurement.
* M1 `confirmed_count = 24` validity re-argument.
* M1 readpoint rewrite or reinterpretation.
* `FUNCTION_NARROW` second rollout.
* `ACQ_DOMINANT` publish review.
* SUSPECT detector or SUSPECT tier design.
* Source facts, source decisions, rendered text, runtime Lua, packaged Lua, bridge payload, `quality_state`, `publish_state`, or `runtime_state` mutation.
* Runtime Lua regeneration.
* Packaged Lua mutation.
* Browser / Wiki / Tooltip exposure.
* Publish mutation review opening.
* Runtime rollout.
* Deployment, Workshop, B42, or release readiness.
* `ready_for_release` declaration.
* Manual in-game validation pass.
* Positive M2 target discovery followed by same-round publish mutation.
* Machine-enforced preflight guard implementation beyond round-local validation artifacts.

---

## 3. Non-Goals

This plan does not attempt to:

* Prove that Layer4 absorption is resolved.
* Turn M1 detector evidence into M2 application target evidence.
* Use grep count, diagnostic residue count, admitted row count, or historical zero-count as M2 target count.
* Treat missing basis, missing consumer, missing field, or ambiguous authority as genuine zero.
* Open SUSPECT as a fallback target class.
* Decide future publish mutation.
* Decide public exposure.
* Decide release readiness.
* Validate runtime behavior.
* Validate external mod compatibility.

---

## 4. Assumptions

* `docs/Philosophy.md` is the top authority.
* Iris remains a 100% Lua wiki module that provides practical facts without recommendation, comparison, or policy judgment.
* `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, and `docs/ROADMAP.md` are current governance readpoints at execution start.
* `LAYER4_ABSORPTION_CONFIRMED` is already sealed as independent `layer_boundary_hard_block_namespace`.
* `FUNCTION_NARROW / ACQ_DOMINANT` remain separated from `LAYER4_ABSORPTION_CONFIRMED` and are not reopened by this plan.
* M1 `confirmed_count = 24` is detector-execution measurement readpoint only.
* M1 `24` is not source fact authority, publish mutation authority, runtime authority, public exposure authority, or M2 target count.
* Prior zero-count is historical predecessor state and is not inherited as current M2 zero.
* M2 current build application target count is currently unsealed.
* M2 basis status was previously `application_target_measurement_unavailable`, and this plan replaces that with a measured current-surface absence readpoint if the production/build/runtime scan proves zero application paths.
* Basis unavailable remains a possible terminal only when the current surface scan itself is incomplete or ambiguous; it is not selected when the complete scan finds zero application paths.
* SUSPECT remains out of scope / non-authority.
* Complete closeout requires an explicit validation ceiling.
* Missing tools or blocked validation commands are reported as blocked/not run, not pass.

---

## 5. Repository Areas Affected

### Code

None expected.

Optional round-local helper scripts may be created only under:

```text
Iris/build/description/v2/staging/compose_contract_migration/layer4_m2_current_build_application_target_round/
```

Shared build tools are not planned mutation targets. Any shared tool change requires an explicit scope amendment.

### Docs

Plan artifact:

```text
docs/Iris/iris-dvf-3-3-layer4-current-build-application-target-remeasurement-zero-reseal-round-plan.md
```

Potential pre-promotion review and closeout artifacts:

```text
docs/Iris/iris-dvf-3-3-layer4-current-build-application-target-remeasurement-zero-reseal-round-review.md
docs/Iris/iris-dvf-3-3-layer4-current-build-application-target-remeasurement-zero-reseal-round-closeout.md
```

Post-gate additive governance write targets:

```text
docs/DECISIONS.md
docs/ARCHITECTURE.md
docs/ROADMAP.md
```

### Config

None expected.

### Generated Artifacts

Execution may create round-local artifacts under:

```text
Iris/build/description/v2/staging/compose_contract_migration/layer4_m2_current_build_application_target_round/
```

Planned artifact families:

```text
predecessor_non_mutation_proof.json
m2_authority_surface_matrix.json
m2_current_build_surface_inventory.jsonl
m2_excluded_surface_inventory.jsonl
m2_build_consumer_inventory.jsonl
m1_m2_boundary_assertions.json
m2_basis_status_report.json
m2_application_target_predicate.v1.json
m2_non_target_reason_codes.v1.json
m2_predicate_dry_run_report.json
no_inheritance_input_guard_report.json
m2_layer4_occurrence_inventory.jsonl
m2_application_target_partition.json
m2_application_target_candidates.jsonl
m2_non_target_reason_distribution.json
m2_scan_validation_report.json
m2_counter_breakdown.json
m2_measurement_summary.json
m2_closeout_branch_decision.json
m2_non_mutation_hash_report.json
m2_public_exposure_scan_report.json
m2_final_handoff.md
```

No runtime payload, packaged Lua, rendered text, source fact, source decision, or state artifact is generated by this plan.

---

## 6. Planned Changes

### Change 1 - Predecessor Non-Mutation Gate And Authority / Surface Lock

Purpose:

Confirm that the execution consumes sealed predecessor readpoints read-only, and lock the current build application surface separate from historical, diagnostic, staging, test, report-only, observer-only, and M1 measurement surfaces.

Files:

* Read-only:
  * `docs/DECISIONS.md`
  * `docs/ARCHITECTURE.md`
  * `docs/ROADMAP.md`
  * sealed Layer4 predecessor artifacts referenced by those docs
* Write:
  * `predecessor_non_mutation_proof.json`
  * `m2_authority_surface_matrix.json`
  * `m2_current_build_surface_inventory.jsonl`
  * `m2_excluded_surface_inventory.jsonl`
  * `m1_m2_boundary_assertions.json`

Implementation Notes:

* Reconfirm `LAYER4_ABSORPTION_CONFIRMED` namespace as `layer_boundary_hard_block_namespace`.
* Reconfirm relationship to `FUNCTION_NARROW / ACQ_DOMINANT` as `separated`.
* Classify all referenced predecessor artifacts as read-only inputs.
* Declare M1 artifacts as `measurement_readpoint_only`.
* Define which current checkout surfaces are build-consumable for M2.
* Define excluded surfaces and require zero overlap with included surfaces.
* Define build consumer evidence through `m2_build_consumer_inventory.jsonl`.
* Each current build surface inventory row must include:

```text
surface_path
surface_class
surface_authority_source
build_consumer_basis
included_or_excluded
exclusion_reason
```

* Each build consumer basis row must include:

```text
consumer_stage
consumer_artifact_or_path
consumer_kind = build_time | runtime
consumer_surface_class = production | staging | diagnostic | report_only | test | historical
consumes_layer4_namespace = true | false | unknown
consumption_mechanism
evidence_path
evidence_field_or_line
basis_verdict = basis_available | basis_unavailable | excluded_non_authority
```

* Production/current build consumers may establish M2 basis. Staging, diagnostic, report-only, test, historical, and M1 measurement-only consumers do not establish M2 basis.
* Under v0.4, system-wide absence of any current production/build/runtime path consuming `LAYER4_ABSORPTION_CONFIRMED`, when proven by the complete current surface scan, routes to `closed_with_layer4_m2_current_build_application_target_zero_resealed`.
* Helper scripts, if any, are non-authority. Authority belongs to the sealed predicate plus validated artifacts.

Protected surfaces for this plan:

```text
docs/DECISIONS.md
docs/ARCHITECTURE.md
docs/ROADMAP.md
Iris/build/description/v2/data/
Iris/media/lua/client/Iris/Data/
Iris/media/lua/client/Iris/UI/
Iris/build/description/v2/staging/dvf_3_3_current_runtime_baseline_seal_round/reports/current_runtime_hash_manifest.json
Iris/build/description/v2/staging/compose_contract_migration/layer4_boundary_current_corpus_lock_round/layer4_boundary_current_corpus_manifest.json
Iris/build/description/v2/staging/compose_contract_migration/layer4_trace_edge_authority_admission_round/layer4_trace_edges.v1.jsonl
Iris/build/description/v2/staging/compose_contract_migration/layer4_confirmed_detector_field_map_reseal_round/canonical_field_map_manifest.json
```

Known predecessor hashes:

```text
current_runtime_hash_manifest.json sha256 =
  790b5689097a8856e6213074fda25b723060073206a7ca44bd26d9f6f08c9171

layer4_boundary_current_corpus_manifest.json sha256 =
  d394f95f5f2a157679238e005a90929349eb807a8180824d8f0ed30240290402

layer4_trace_edges.v1.jsonl sha256 =
  44a863a288bb1debf570a1d1b63a35f31a29661f09e3175003939d364496c1ca

field_map.v1 roles =
  source_ref / row_id / destination_slot / edge_type
```

Validation:

* Predecessor identity/hash comparison pass. An unavailable-with-reason record may explain a blocker, but it cannot satisfy a complete branch gate.
* Included/excluded surface overlap `0`.
* Unknown surface class `0`.
* M1 artifact not included as M2 target input.
* `FUNCTION_NARROW / ACQ_DOMINANT` not reopened.
* Protected-surface baseline hash captured before later phases.
* System-wide build consumer inventory has either at least one current production consumer or proves current application-path absence for Branch B zero reseal.

---

### Change 2 - M2 Basis Definition And Application Target Predicate Seal

Purpose:

Define what counts as a current build application target and determine whether the measurement basis is available.

Files:

* Write:
  * `m2_basis_status_report.json`
  * `m2_application_target_predicate.v1.json`
  * `m2_non_target_reason_codes.v1.json`
  * `m2_predicate_dry_run_report.json`
  * `no_inheritance_input_guard_report.json`

Implementation Notes:

The predicate is:

```text
M2_APPLICATION_TARGET iff:
1. occurrence belongs to LAYER4_ABSORPTION_CONFIRMED
2. namespace is independent layer_boundary_hard_block_namespace
3. occurrence is in current checkout build-consumable surface
4. occurrence is not historical / diagnostic / staging / test / report-only / observer-only
5. occurrence has build-consumable target identity
6. occurrence would be consumed by current build application logic under a recorded production/current build_consumer_basis
7. occurrence is not merely M1 measurement evidence
```

Build-consumer rule:

```text
If no current production/build/runtime application path exists system-wide for
LAYER4_ABSORPTION_CONFIRMED under the complete current surface scan, route to:

closed_with_layer4_m2_current_build_application_target_zero_resealed

For v0.4 execution, select `closed_with_layer4_m2_current_build_application_target_zero_resealed` instead of deferring solely because the application path count is `0`.
```

Initial non-target reason codes:

```text
M1_MEASUREMENT_ONLY
HISTORICAL_ONLY
DIAGNOSTIC_ONLY
STAGING_ONLY
TEST_ONLY
REPORT_ONLY
OBSERVER_ONLY
OUT_OF_CURRENT_BUILD_SURFACE
NO_BUILD_CONSUMER
NO_APPLICATION_TARGET_SLOT
NAMESPACE_MISMATCH
FIELD_MISSING
AMBIGUOUS_AUTHORITY
MALFORMED_ROW
```

Reason-code boundary:

```text
NO_BUILD_CONSUMER / NO_APPLICATION_TARGET_SLOT / FIELD_MISSING /
AMBIGUOUS_AUTHORITY may be emitted as non-target reason codes only when
the measurement basis is otherwise complete and the row is positively
classified outside current build application target scope.

If the missing consumer, slot, field, or authority prevents determining
targetness, route to basis unavailable instead of non-target.
```

Validation:

* Basis status is explicitly `available_by_current_surface_absence_scan`, `available`, or `unavailable`.
* If system-wide current production/build/runtime application path count is `0` under the complete scan, basis status is `available_by_current_surface_absence_scan`.
* Predicate schema parses.
* Reason-code schema parses.
* Reason-code coverage has `unknown_reason_count = 0`.
* Partition categories are mutually exclusive.
* No-inheritance guard rejects M1 `24`, admitted row count, diagnostic residue count, and prior zero-count as direct M2 count bases.
* `NO_BUILD_CONSUMER`, `FIELD_MISSING`, and `AMBIGUOUS_AUTHORITY` rows are separated into non-target versus basis-failure counters.

---

### Change 3 - Current Checkout Scan And Target / Non-Target Partition

Purpose:

Use the current checkout/current build surface scan as the M2 basis and partition `LAYER4_ABSORPTION_CONFIRMED` occurrences into target, non-target, and `unresolved_bucket` buckets.

Files:

* Write:
  * `m2_layer4_occurrence_inventory.jsonl`
  * `m2_application_target_partition.json`
  * `m2_application_target_candidates.jsonl`
  * `m2_non_target_reason_distribution.json`
  * `m2_scan_validation_report.json`
  * `m2_counter_breakdown.json`

Implementation Notes:

* Scan only current build-consumable surfaces defined in Change 1.
* Scan toward Branch B when the current production/build/runtime surface scan is complete and finds zero application paths.
* Record every occurrence with surface class, authority class, field path, row identity, and predicate result.
* Route non-target rows through exactly one reason code.
* Route malformed, ambiguous, unavailable, and out-of-corpus rows into explicit `unresolved_bucket` or non-target buckets according to predicate contract.
* Do not convert grep hit count into M2 target count.

Validation:

* JSON/JSONL parse pass.
* Total occurrence count equals target + non-target + `unresolved_bucket` buckets.
* `unknown_count = 0`.
* `unclassified_count = 0`.
* Target row count equals candidate manifest row count.
* All target rows are current build-consumable.
* All non-target rows have reason codes.
* No target row is diagnostic/staging/report-only/test/historical/observer-only.
* Determinism pass for the complete measurement artifact set, regardless of whether scripts or manual generation are used.
* `field_missing_as_basis_failure_count` and `no_consumer_as_basis_failure_count` are reported separately from non-target reasons.

---

### Change 4 - Terminal Seal / Branch Selection

Purpose:

Select the single terminal branch based on the measurement result or basis status.

Files:

* Write:
  * `m2_measurement_summary.json`
  * `m2_closeout_branch_decision.json`
  * `m2_non_mutation_hash_report.json`
  * `m2_public_exposure_scan_report.json`
  * `docs/Iris/iris-dvf-3-3-layer4-current-build-application-target-remeasurement-zero-reseal-round-closeout.md`

`docs/Iris/iris-dvf-3-3-layer4-current-build-application-target-remeasurement-zero-reseal-round-closeout.md` is a staging draft during Change 4. Final seal occurs only after Change 5 review gate and additive governance promotion pass.

Implementation Notes:

Branch A - Positive M2 Target:

```text
branch_closeout =
  closed_with_layer4_m2_current_build_application_target_measured_positive

m2_current_build_application_target_count = N
```

* Target manifest hash is recorded.
* M1 `24` remains separate measurement readpoint only.
* Same-round publish mutation review remains closed.

Branch B - Genuine-Zero Reseal:

```text
branch_closeout =
  closed_with_layer4_m2_current_build_application_target_zero_resealed

m2_current_build_application_target_count = 0
```

* `0` is based on current checkout scan and complete partition only.
* Branch B is allowed only when all of the following are true:

```text
current_surface_absence_scan_executed = true
basis_status = available_by_current_surface_absence_scan
target_count = 0
unresolved_bucket_count = 0
unknown_count = 0
unclassified_count = 0
ambiguous_count = 0
malformed_count = 0
field_missing_as_basis_failure_count = 0
no_consumer_as_basis_failure_count = 0
```

* Prior zero-count inheritance remains false.
* M1 `24` remains measurement readpoint only.
* This is not a Layer4 absorption resolved claim.

Branch C - Measurement / Basis Unavailable:

```text
contract_closeout_state = complete
branch_closeout =
  closed_with_layer4_m2_application_target_basis_unavailable_carried_forward
```

* No target count or zero claim is made.
* Missing field, missing consumer, ambiguous authority, missing surface, or incomplete basis is recorded fail-loud.
* This is a first-class additive terminal and must be promoted into `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, and `docs/ROADMAP.md` if its own gates pass.
* This is not M2 target count production.
* This is not current zero reseal.
* `complete` means only that basis unavailable was sealed as an additive readpoint within the validation ceiling.

Stop-the-Line / defer conditions:

* Predecessor non-mutation or identity failure maps to `blocked_predecessor_non_mutation_or_identity_gate_failed`.
* Need for separate basis-definition or SUSPECT authorization maps to `deferred_pending_separate_basis_definition_or_suspect_authorization`; this is not a complete terminal.

Validation:

* Exactly one branch selected.
* Positive branch target count equals target manifest row count.
* Zero branch satisfies the full Branch B condition list above.
* Basis unavailable branch has no `0` claim and still produces additive closeout artifacts.
* Protected-surface hash delta `0`.
* Public exposure positive hit count `0`.
* Change 4 closeout remains staging-only until Change 5 review gate passes.

---

### Change 5 - Governance Addendum, Adversarial Review, And Handoff Seal

Purpose:

Promote the result into governance docs only if the round has passed measurement, non-mutation, non-exposure, and review gates.

Files:

* Pre-promotion review:
  * `docs/Iris/iris-dvf-3-3-layer4-current-build-application-target-remeasurement-zero-reseal-round-review.md`
* Post-gate additive write targets:
  * `docs/DECISIONS.md`
  * `docs/ARCHITECTURE.md`
  * `docs/ROADMAP.md`
  * `docs/Iris/iris-dvf-3-3-layer4-current-build-application-target-remeasurement-zero-reseal-round-closeout.md`
* Write:
  * `m2_final_handoff.md`

Implementation Notes:

* Use additive entries only.
* Do not rewrite predecessor bodies.
* Include selected branch, count/basis state, validation ceiling, and non-claims.
* If Branch A is selected, future `Layer4 M2 Application Disposition Round` may be named as a candidate only; do not open publish mutation review in this round.
* If Branch B is selected, do not open follow-up mutation round automatically.
* If Branch C is selected, promote basis unavailable as a first-class additive terminal and record missing prerequisite as follow-up context only.
* DECISIONS addendum should carry house-style absorption tokens:

```text
absorption: COMMON-RELEASE-NONDECISION / COMMON-RUNTIME-SURFACE-NONMUTATION / COMMON-EVIDENCE-TRACE
```

Validation:

* Addendum-only diff.
* `docs/REVIEW_TEMPLATE.md`-style adversarial review `PASS` before live top-doc promotion, or `WARN` only if every listed condition is explicitly accepted and the closeout remains evidence-bounded.
* Non-claim checklist pass.
* No source/rendered/runtime/state mutation.
* No public exposure.
* `all_gates_pass = true` only if every named gate passes.

---

## 7. Validation Plan

### Automated Validation

Required change review:

```powershell
git diff --stat
git diff
```

Required artifact validation:

```text
JSON parse for every generated JSON artifact
JSONL parse for every generated JSONL artifact
predecessor identity/hash comparison
included/excluded surface overlap check
unknown surface class check
system-wide current application-path absence -> zero reseal check
M1/M2 no-inheritance guard
predicate schema validation
reason-code coverage validation
mutually exclusive partition check
target/non-target/unresolved_bucket count invariant
target manifest row-count consistency
non-target reason distribution consistency
zero branch strict gate check
current surface absence zero-reseal seal check
determinism check for the complete measurement artifact set
pre/post non-mutation hash diff over declared protected surfaces
public exposure scan
forbidden claim scan
branch decision consistency check
additive-only docs diff check
review gate check
```

Forbidden claim scan minimum patterns:

```text
Layer4 absorption resolved
Layer4 resolved
publish review opened
publish mutation review opened
runtime rollout
public exposure enabled
Browser exposure
Wiki exposure
Tooltip exposure
ready_for_release
release-ready
Workshop readiness
B42 readiness
SUSPECT tier defined
M1 count inherited
M1 24 inherited
prior zero-count inheritance
measurement unavailable as zero
admitted row count shortcut
```

Forbidden-claim scan bucketing is deterministic:

```text
If a hit is inside a fenced non-claim block, an "Expected final non-claims"
section, a "Success must not claim" section, or a forbidden-pattern list,
classify it as allowed_non_claim_hit.

All other hits require reviewer classification as positive_claim,
neutral_reference, or false_positive. Any positive_claim fails the gate.
```

Optional repo validation only if touched surface requires it:

```powershell
python -B -m unittest discover -s Iris\build\description\v2\tests -p "test_*.py"
powershell -ExecutionPolicy Bypass -File .\tools\check_lua_syntax.ps1
```

These optional commands may be claimed as passed only if the exact command exits with code `0`.

### Manual Validation

* Confirm the round answers only M2 current build application target count or basis availability.
* Confirm M1 `confirmed_count = 24` remains measurement readpoint only.
* Confirm M1 `24` is never used as M2 target count.
* Confirm prior zero-count is not inherited as current zero.
* Confirm basis unavailable is not written as `0`; current surface absence is separately recorded as the Branch B zero-reseal basis.
* Confirm `FUNCTION_NARROW / ACQ_DOMINANT` are not reopened.
* Confirm SUSPECT is not introduced.
* Confirm target rows, if any, are current build-consumable.
* Confirm zero branch has complete partition evidence.
* Confirm zero branch has `current_surface_absence_scan_executed = true` and `basis_status = available_by_current_surface_absence_scan`.
* Confirm unavailable branch records missing basis fail-loud and is promoted as a first-class additive terminal.
* Confirm public-facing non-exposure.
* Confirm validation ceiling and non-claims are present.

### Validation Limits

This execution will not perform:

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
* No public-facing behavior validation beyond exposure scan.
* No source/rendered/runtime Lua regeneration validation.
* `PLAN_TEMPLATE.md` / `EXECUTION_CONTRACT.md` path/hash/line-count proof is author-attested by the plan author in this drafting session. If the execution closeout does not independently rerun that proof, it must carry this as an identity-proof review-surface limit rather than treating it as externally reverified evidence.

---

## 8. Risk Surface Touch

### Authority Surface

Touched. This round may create or carry forward M2 measurement/basis authority for `LAYER4_ABSORPTION_CONFIRMED`.

It must not create source facts authority, source decisions authority, rendered text authority, runtime authority, publish writer authority, quality authority, public exposure authority, rollout authority, or release authority.

### Runtime Behavior Surface

None. Runtime Lua, packaged Lua, bridge payload, Browser, Wiki, Tooltip, item selection, rendered text, and player-facing behavior remain unchanged.

### Compatibility Surface

None expected. External mod compatibility, PZ runtime behavior, API, SPI, and public formats are not changed. Round-local JSON/JSONL evidence is internal governance evidence only.

### Sealed Artifact Surface

Touched additively. The round may create new sealed M2 measurement/basis artifacts. Existing Layer4 predecessor artifacts are consumed read-only.

### Public-Facing Output Surface

None. Browser, Wiki, Tooltip, README release claims, Workshop copy, release notes, and user-facing quality/trust/confidence surfaces remain unchanged.

---

## 9. Risk Analysis

### Architecture Risk

* M1 `confirmed_count = 24` could be misread as M2 application target count.
* Historical prior zero-count could be misread as current genuine zero.
* `basis unavailable` could be collapsed into `0`.
* `NO_BUILD_CONSUMER` or `FIELD_MISSING` could be misread as target absence rather than basis failure.
* Current surface absence could be overread as Layer4 resolved instead of the narrower M2 application target zero reseal.
* Diagnostic/staging/report-only residue could be promoted into current build target evidence.
* Positive M2 target could trigger same-round publish mutation review.
* SUSPECT could be introduced without a separate authority round.

### Runtime Risk

* Expected runtime risk is none if scope is preserved.
* Any runtime Lua, packaged Lua, bridge payload, rendered text, or state mutation is a scope violation.
* Optional helper scripts must not regenerate runtime or rendered surfaces.

### Compatibility Risk

* Low if no runtime/API/output formats change.
* Future readers could overread internal M2 count as external compatibility or release evidence.
* Compatibility claims remain out of scope.

### Regression Risk

* Surface inventory could be too broad and include diagnostic or staging files.
* Reason-code partition could be non-exclusive.
* JSONL ordering or serialization could be nondeterministic.
* Target manifest and count summary could diverge.
* Public exposure scan could miss wording in Browser/Wiki/Tooltip surfaces.
* Dirty working tree state could obscure non-mutation proof.
* Missing validation tools could be misreported as pass.

---

## 10. Rollback Plan

Rollback is docs/artifact rollback, not runtime rollback.

1. Review touched files with:

```powershell
git diff --stat
git diff
```

2. Remove or quarantine only artifacts created under:

```text
Iris/build/description/v2/staging/compose_contract_migration/layer4_m2_current_build_application_target_round/
```

3. If optional helper scripts were created and are invalid, remove or quarantine only those round-local helper scripts.

4. If shared tooling was changed without explicit scope amendment, stop and revert only changes made by this round after identifying them.

5. If `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, or `docs/ROADMAP.md` receive invalid additive wording, correct with additive clarification when possible. If duplicate text was added by this round, remove only that duplicate addition.

6. If source facts, source decisions, rendered text, runtime Lua, packaged Lua, bridge payload, `quality_state`, `publish_state`, or `runtime_state` changed unexpectedly, stop and identify the exact source of mutation before reverting only this round's changes.

7. If M1 `24`, admitted row count, grep count, diagnostic residue count, or prior zero-count was used as M2 target count, discard the evidence root and rerun from Change 1.

8. If unavailable, ambiguous, field-missing, or incomplete-scan state was written as `m2_current_build_application_target_count = 0`, discard the count summary and rewrite branch resolution before closeout. A complete current surface absence scan may write `0`.

9. If count summary and manifests disagree, closeout must stop and the evidence root must be marked invalid/quarantined.

10. If a sealed closeout later proves wrong, do not rewrite the sealed record. Open an additive successor correction round.

---

## 11. Governance Constraints

* `docs/Philosophy.md` compliance is mandatory.
* Iris remains wiki/fact-oriented and must not introduce interpretation, recommendation, or comparison.
* Hub & Spoke and SPI boundaries remain untouched.
* Runtime/build-time separation must remain intact.
* `LAYER4_ABSORPTION_CONFIRMED` remains independent `layer_boundary_hard_block_namespace`.
* `FUNCTION_NARROW / ACQ_DOMINANT` remain separated and closed.
* M1 `confirmed_count = 24` remains detector-execution measurement readpoint only.
* M1 `24` must not be inherited as M2 target count.
* Prior zero-count must not be inherited as current zero.
* Measurement unavailable must not be collapsed into zero.
* System-wide absence of a current production/build/runtime application path for `LAYER4_ABSORPTION_CONFIRMED`, when proven by the complete current surface scan, routes to `closed_with_layer4_m2_current_build_application_target_zero_resealed`.
* Branch B zero requires `current_surface_absence_scan_executed = true`, `basis_status = available_by_current_surface_absence_scan`, `target_count = 0`, and zero `unresolved_bucket`/unknown/unclassified/ambiguous/malformed/basis-failure counters.
* `NO_BUILD_CONSUMER`, `NO_APPLICATION_TARGET_SLOT`, `FIELD_MISSING`, and `AMBIGUOUS_AUTHORITY` may be non-target reasons only when targetness is otherwise decidable; otherwise they route to basis unavailable.
* Diagnostic, historical, staging, test, report-only, observer-only, and M1 measurement-only surfaces must not be promoted to current build targets.
* SUSPECT detector / SUSPECT tier introduction requires a separate approved round.
* Source facts, source decisions, rendered text, runtime Lua, packaged Lua, bridge payload, `quality_state`, `publish_state`, and `runtime_state` remain non-mutation targets.
* Browser / Wiki / Tooltip public exposure remains closed.
* Additive amendment is preferred for top-doc alignment.
* Sealed predecessor bodies are not rewritten.
* Live governance doc promotion requires review `PASS`, or `WARN` with every listed condition explicitly accepted and carried into the closeout ceiling.
* DECISIONS additive closeout should carry `absorption: COMMON-RELEASE-NONDECISION / COMMON-RUNTIME-SURFACE-NONMUTATION / COMMON-EVIDENCE-TRACE`.
* Validation may not be claimed as passed unless the exact relevant command exits with code `0`.
* Release readiness, Workshop readiness, deployment readiness, B42 readiness, and `ready_for_release` claims are forbidden.

---

## 12. Expected Closeout State

Expected contract closeout state:

```text
complete, partial, implemented_only, or blocked
```

`complete` is valid only for:

```text
closed_with_layer4_m2_current_build_application_target_measured_positive
closed_with_layer4_m2_current_build_application_target_zero_resealed
closed_with_layer4_m2_application_target_basis_unavailable_carried_forward
```

`blocked` is valid for:

```text
blocked_predecessor_non_mutation_or_identity_gate_failed
blocked_non_mutation_invariant_failed
blocked_public_exposure_detected
blocked_claim_overreach
blocked_review_gate_failed
blocked_additive_only_invariant_failed
blocked_measurement_artifact_determinism_failed
```

`partial` is valid only if execution explicitly defers because a separate basis-definition or SUSPECT authorization round is needed:

```text
deferred_pending_separate_basis_definition_or_suspect_authorization
```

`implemented_only` is not a planned sealed success state for this round. If artifacts or docs are drafted but required validation is not run, the round must be reported as `implemented_only`, not `complete`.

Complete measured positive may claim only:

```text
The current checkout/current build M2 application target measurement found
N target rows under the sealed predicate and target manifest.
M1 confirmed_count = 24 remains measurement_readpoint_only and was not inherited.
```

Complete genuine-zero reseal may claim only:

```text
The current checkout/current build M2 application target measurement executed
with complete partition evidence and found 0 target rows.
This is genuine current zero, not prior zero-count inheritance.
M1 confirmed_count = 24 remains measurement_readpoint_only.
```

Complete basis-unavailable carry-forward may claim only:

```text
The round reached a first-class terminal that could not produce a validated M2
positive count or genuine-zero reseal because application target measurement
basis was unavailable or incomplete. No target count and no zero claim is sealed.
This unavailable result is itself the additive sealed readpoint.
It is not M2 target count production and not current zero reseal.
```

Expected final non-claims:

```text
Layer4 absorption resolved 아님
Layer4 policy redesign 아님
semantic quality completion 아님
M1 confirmed_count rewrite 아님
M1 confirmed_count remeasurement 아님
FUNCTION_NARROW second rollout 아님
ACQ_DOMINANT publish review 아님
SUSPECT tier defined 아님
publish mutation review opened 아님
source facts mutation 아님
source decisions mutation 아님
rendered text mutation 아님
runtime Lua mutation 아님
packaged Lua mutation 아님
bridge runtime payload mutation 아님
quality_state / publish_state / runtime_state mutation 아님
Browser / Wiki / Tooltip behavior change 아님
public-facing exposure 아님
runtime rollout 아님
manual in-game validation pass 아님
deployment 아님
Workshop readiness 아님
B42 readiness 아님
release readiness 아님
ready_for_release 아님
M1 24 inheritance 아님
prior zero-count inheritance 아님
measurement unavailable collapsed into zero 아님
```

Next round opening condition:

```text
Any publish mutation review, semantic quality interpretation, public-facing exposure,
SUSPECT authorization, or Layer4 policy redesign requires a separate approved plan
after this M2 measurement/basis round closes.
```
