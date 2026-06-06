# Iris DVF 3-3 Layer4 Confirmed Current Count Remeasurement Round Plan

> 상태: Draft v0.4-pass-minor-feedback-applied
> 기준일: 2026-06-02
> 상위 기준: `docs/Philosophy.md`, `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`
> authority input: `ROADMAP - Iris DVF 3-3 Layer4 Confirmed Current Count Remeasurement Round` (2026-06-02 user-provided pasted roadmap)
> review input: `WARN feedback - Iris DVF 3-3 Layer4 Confirmed Current Count Remeasurement Round Plan` (2026-06-02 user-provided synthesis). v0.2 applies prior WARN feedback by pinning corpus manifest sha256, defining sidecar-to-corpus membership join, and narrowing Opening Decision to an objective authority-consumption gate. It also incorporates feedback on non-mutation targets, unittest side-effect handling, edge_type policy, rejected_fallback count status, branch naming, and hash capture timing.
> second review input: `WARN feedback - Iris DVF 3-3 Layer4 Confirmed Current Count Remeasurement Round Plan v0.2` (2026-06-02 user-provided synthesis). v0.3 adopts the generated-provenance row-level confirmability option: admitted generated generation-time trace-edge rows are confirmable detector inputs only after row-level detector partitioning under sealed authority; admitted row count remains forbidden as a shape-metric shortcut.
> third review input: `PASS feedback - Iris DVF 3-3 Layer4 Confirmed Current Count Remeasurement Round Plan v0.3` (2026-06-02 user-provided synthesis). v0.4 incorporates non-blocking Minor recommendations by adding recovered-row confirmed condition symmetry, replacing earlier option-label wording with descriptive measurement semantics, adding unmapped `edge_basis` disposition, and retaining sealed-sha256 / review-surface limitation disclosure.
> 직접 상위 readpoint:
> - 2026-05-31 Layer4 Boundary Current Corpus Lock Round `closed_with_layer4_boundary_current_corpus_locked_no_count_inheritance_design_preflight`
> - 2026-05-31 Layer4 Confirmed Detector Field Map Seal Round `closed_with_confirmed_measurement_unavailable_trace_absent`
> - 2026-06-01 Layer4 Trace-Edge Authority Admission Round `EDGE_AUTHORITY_PRODUCED_AND_ADMITTED`
> - 2026-06-02 Layer4 Confirmed Detector Field Map Reseal Round `closed_with_layer4_confirmed_detector_field_map_resealed`
> 계획 형식: `docs/PLAN_TEMPLATE.md`
> template attestation: this plan follows the 1-12 section structure in `docs/PLAN_TEMPLATE.md`.
> execution_contract_reference: `docs/EXECUTION_CONTRACT.md` checked for closeout-state vocabulary and claim ceiling discipline.
> template_contract_verify_status: `docs/PLAN_TEMPLATE.md` and `docs/EXECUTION_CONTRACT.md` checked by the plan author in-session; closeout-state vocabulary is `{complete, partial, implemented_only, blocked}`.
> draft_origin: AI-assisted draft from user-provided roadmap; execution requires normal review/gate approval.
> execution_scale: governance
> scope_qualifier: `layer4_confirmed_current_count_remeasurement`
> 실행 상태: planning authority only. This document does not execute measurement, mutate runtime, open publish review, or declare release readiness.

---

## 1. Objective

이번 execution plan의 목적은 sealed current corpus lock, admitted trace-edge authority, and sealed detector field map을 함께 소비해 `LAYER4_ABSORPTION_CONFIRMED`의 authoritative current detector count를 산출하거나, count 산출이 불가능한 authoritative branch reason을 봉인하는 것이다.

이번 라운드가 답해야 하는 질문은 다음 하나로 제한한다.

```text
current corpus lock 아래에서
sealed trace-edge authority와 sealed field map을 detector input으로 소비했을 때,
LAYER4_ABSORPTION_CONFIRMED confirmed count는 무엇인가?
```

Allowed terminal answers:

```text
measured_positive
measured_zero_detector_executed
rejected_fallback
ambiguous
unavailable_or_blocked
detector_contract_violation
```

Round id:

```text
layer4_confirmed_current_count_remeasurement_round
```

Round-local artifact root:

```text
Iris/build/description/v2/staging/compose_contract_migration/layer4_confirmed_current_count_remeasurement_round/
```

Primary input authorities:

```text
Iris/build/description/v2/staging/compose_contract_migration/layer4_boundary_current_corpus_lock_round/layer4_boundary_current_corpus_manifest.json
Iris/build/description/v2/staging/compose_contract_migration/layer4_boundary_current_corpus_lock_round/layer4_corpus_partition.json
Iris/build/description/v2/staging/compose_contract_migration/layer4_trace_edge_authority_admission_round/trace_edge_admission_manifest.json
Iris/build/description/v2/staging/compose_contract_migration/layer4_trace_edge_authority_admission_round/layer4_trace_edges.v1.jsonl
Iris/build/description/v2/staging/compose_contract_migration/layer4_confirmed_detector_field_map_reseal_round/canonical_field_map_manifest.json
```

Pinned sealed authority hashes:

```text
layer4_boundary_current_corpus_manifest.json sha256 =
  d394f95f5f2a157679238e005a90929349eb807a8180824d8f0ed30240290402

layer4_trace_edges.v1.jsonl sha256 =
  44a863a288bb1debf570a1d1b63a35f31a29661f09e3175003939d364496c1ca
```

Field map readpoint:

```text
field_map_version = field_map.v1
source_ref -> source object field
row_id -> target Layer3 row/item identity anchor
destination_slot -> destination body slot field
edge_type -> explicit edge relation field
edge_basis -> tuple support only
```

Branch taxonomy:

```text
complete_terminal:
  closed_with_layer4_confirmed_current_count_measured_positive
  closed_with_layer4_confirmed_current_count_measured_zero_detector_executed
  closed_with_layer4_confirmed_current_count_rejected_fallback
  closed_with_layer4_confirmed_current_count_ambiguous

blocked:
  blocked_with_layer4_confirmed_measurement_unavailable
  blocked_with_layer4_confirmed_detector_contract_violation
  blocked_missing_current_corpus_lock
  blocked_missing_trace_edge_authority
  blocked_missing_detector_field_map
  blocked_authority_chain_mismatch
  blocked_missing_opening_decision
  blocked_partition_invariant_failed
  blocked_non_mutation_invariant_failed
  blocked_review_gate_failed
  blocked_claim_overreach
```

Closeout records must separate `docs/EXECUTION_CONTRACT.md` state from branch label:

```text
contract_closeout_state = complete | blocked
branch_closeout = one canonical branch label from this plan
```

`complete` is allowed only when the branch result is sealed inside the validation ceiling. A complete ambiguous branch means ambiguity was measured and partitioned as the terminal result; it does not mean a count was computed.

`complete_terminal` means the round reached a sealed terminal disposition; it does not mean a measured integer count exists for every complete branch.

Success may claim only:

```text
The round consumed the sealed current corpus lock, sealed trace-edge authority,
and sealed detector field map, then produced a detector-execution count result
or an authoritative non-count branch reason for LAYER4_ABSORPTION_CONFIRMED.
```

Success must not claim:

```text
Layer4 absorption resolved
Layer4 policy redesign
SUSPECT tier coverage
semantic quality completion
publish mutation review approval
runtime rollout
manual in-game validation pass
deployment
Workshop readiness
B42 readiness
release readiness
ready_for_release
generated edge row count 24 as confirmed count
admitted row count shortcut as confirmed count
prior zero-count inherited as current count
```

---

## 2. Scope

This is a governance-scale measurement round. It consumes immutable predecessor readpoints and creates additive measurement authority artifacts under a new round-local staging root.

In scope:

* Read-only intake of the 2026-05-31 current corpus lock manifest and corpus partition.
* Read-only intake of the 2026-06-01 trace-edge authority admission manifest and admitted `layer4_trace_edges.v1.jsonl`.
* Read-only intake of the 2026-06-02 canonical field-map reseal manifest.
* Input path, sha256, branch closeout, and authority state recording.
* Opening decision as an objective authority-consumption preflight, not a predecessor authority re-adjudication.
* Sidecar edge row membership join using `row_id` against the sealed current corpus member set derived from corpus partition included substrate.
* Generated-provenance row-level routing under detector contract:
  * admitted generated generation-time trace-edge rows are confirmable detector inputs under Reading A.
  * admitted row count itself remains forbidden as a shape-metric shortcut.
  * measured positive count, if any, is scoped to row-level qualified admitted generated generation-time trace-edge rows.
* Detector contract freeze before count execution.
* Partitioned detector execution over the admitted edge rows and current corpus boundary.
* Partition manifests for `confirmed`, `rejected_fallback`, `ambiguous`, `unavailable`, `malformed`, and `out_of_corpus`.
* Dual-zero separation between prior trace absence and detector-executed zero.
* Count summary, validation report, non-mutation report, and closeout artifact.
* Additive docs addendum candidate for `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, and `docs/ROADMAP.md` only after hard gate.

### Explicitly Out Of Scope

* Layer4 absorption resolved declaration.
* Layer4 policy redesign.
* Machine-enforced preflight implementation beyond round-local validation.
* SUSPECT tier coverage expansion.
* Layer4 explanation rewrite.
* `FUNCTION_NARROW` second rollout.
* `ACQ_DOMINANT` publish review or publish mutation review.
* Source facts or source decisions mutation.
* Rendered text regeneration.
* Runtime Lua regeneration.
* Packaged Lua regeneration.
* Browser / Wiki / Tooltip behavior change.
* `quality_state`, `publish_state`, or `runtime_state` mutation.
* Runtime rollout.
* Manual in-game validation pass.
* Deployment, Workshop readiness, B42 readiness, or release readiness.
* Current corpus lock redesign.
* Trace-edge authority reproduction.
* Field map redesign.
* Historical sealed body rewrite.
* Report-only, diagnostic, staging, test, or historical artifact promotion to current authority.
* User-facing exposure of the confirmed count.

---

## 3. Non-Goals

This plan does not attempt to:

* Prove that `LAYER4_ABSORPTION_CONFIRMED` is semantically complete.
* Use text similarity, keyword residue, rendered substring, category tag, cluster/provenance label, or co-occurrence as count evidence.
* Treat admitted edge row count `24` as confirmed count.
* Treat generated provenance itself as sufficient without row-level detector qualification.
* Treat prior zero-count, trace-absent Branch B, or detector readiness dry-run as current count.
* Collapse unavailable or blocked state into `confirmed_count = 0`.
* Collapse rejected fallback into `confirmed_count = 0`.
* Collapse ambiguous rows into positive or zero count.
* Reopen the 2026-05-31 field-map Branch B predecessor.
* Reopen the 2026-06-01 trace-edge admission predecessor.
* Reopen the 2026-06-02 field-map reseal predecessor.
* Change Iris runtime, Browser, Wiki, Tooltip, rendered text, or public-facing copy.
* Create release, deployment, Workshop, or B42 readiness evidence.

---

## 4. Assumptions

Authority assumptions:

* `docs/Philosophy.md` is the top authority. Iris remains a 100% Lua wiki-style information module and must not become an interpretation, recommendation, comparison, or gameplay-policy system.
* `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, and `docs/ROADMAP.md` are current governance readpoints at execution start.
* The 2026-05-31 current corpus lock is immutable and forbids inheriting prior zero-count as current count.
* The 2026-05-31 corpus lock manifest hash must equal `d394f95f5f2a157679238e005a90929349eb807a8180824d8f0ed30240290402`; mismatch blocks measurement as `blocked_authority_chain_mismatch` or `blocked_missing_current_corpus_lock`.
* The 2026-06-01 trace-edge authority admission is immutable and identifies `layer4_trace_edges.v1.jsonl` as `current_detector_input`.
* The 2026-06-02 field-map reseal is immutable and seals `source_ref`, `row_id`, `destination_slot`, and `edge_type` as detector-consumable roles.
* The admitted edge artifact hash is expected to match `44a863a288bb1debf570a1d1b63a35f31a29661f09e3175003939d364496c1ca`.
* Admitted edge row count `24` is an artifact shape metric only until this round partitions rows by detector execution.
* `confirmed_measurement_executed = false` and `confirmed_count = not_computed` remain true at execution start.

Opening decision assumptions:

* Reading A and Reading B must not be silently blended.
* Reading A: the admitted generated edge artifact is a valid `current_detector_input`, so detector execution may classify its rows.
* Opening Decision is not a predecessor re-adjudication. It is an authority-consumption preflight gate over already sealed predecessors.
* Reading A is the default when artifact existence, sha256 equality, partition, authority chain, and field-map checks pass.
* Reading B may be selected only when a concrete authority-consumption failure is recorded:
  * missing artifact
  * hash mismatch
  * partition mismatch
  * field-map role binding failure
  * schema or required field violation before row-level classification
  * authority chain mismatch
* Reading B requires `selected_reading_reason_code`, `failing_artifact`, `failing_field_or_manifest_key`, and `evidence_path`.
* The selected reading must be recorded before measurement execution; if Reading A preflight passes, the plan must not choose Reading B as a discretionary policy choice.
* If no opening decision is recorded, close as `blocked_missing_opening_decision`.

Detector assumptions:

* `confirmed_count = count(rows where disposition == "confirmed")`.
* Confirmed rows must come from explicit row-level trace-edge detector result.
* `source_ref`, `row_id`, `destination_slot`, and `edge_type` are required roles.
* `edge_basis` may be recorded as tuple support but is not an independent confirmed basis.
* `edge_derivation` is derived from `edge_basis`:
  * `recovered_body_plan_relation_trace` or `recovered_compose_relation_trace` -> `recovered`
  * `generated_body_plan_relation_trace` or `generated_compose_relation_trace` -> `generated_generation_time`
* `edge_basis` disposition:
  * missing, null, non-string, or schema-invalid `edge_basis` -> `malformed`
  * present-but-unmapped `edge_basis` -> `ambiguous` with reason code `EDGE_BASIS_UNMAPPED`
* `generated_provenance_route = confirmed_candidate_under_reading_a`.
* Generated-edge row-level measurement semantics are adopted:

```text
Reading A means admitted generated generation-time edges are confirmable detector inputs.
Admitted row count itself remains forbidden only as a shape-metric shortcut.
confirmed_count may be N over generated generation-time edges only if detector partitioning qualifies them row-by-row.
```

* Generated provenance is not sufficient by itself. A generated generation-time row can route to `confirmed` only when all of the following are true:

```text
reading = Reading A
admission_partition = current_detector_input
input_artifact_sha256 matches sealed sha256
corpus_manifest_sha256 matches sealed sha256
field_map_sealed = true
membership_key_role = row_id
row_id joins to sealed current corpus member set
edge_type = placed_in_body_output
edge_basis in ["generated_body_plan_relation_trace", "generated_compose_relation_trace"]
source_ref, row_id, destination_slot, edge_type are present and non-empty
row is not malformed
row is not out_of_corpus
row does not use a forbidden fallback basis
```

* If a generated generation-time row fails row-level qualification, it must route to `malformed`, `out_of_corpus`, `ambiguous`, `unavailable`, or `rejected_fallback` by explicit reason code; it must not silently become confirmed.
* A recovered row can route to `confirmed` only when all of the following are true:

```text
recovered_row_confirmed_condition =
  reading == Reading A
  and edge_derivation == recovered
  and admission_partition == current_detector_input
  and input_artifact_sha256 matches sealed sha256
  and corpus_manifest_sha256 matches sealed sha256
  and field_map_sealed == true
  and membership_key_role = row_id
  and row_id joins to sealed current corpus member set
  and edge_type == placed_in_body_output
  and edge_basis in ["recovered_body_plan_relation_trace", "recovered_compose_relation_trace"]
  and source_ref, row_id, destination_slot, edge_type are present and non-empty
  and row is not malformed
  and row is not out_of_corpus
  and row does not use a forbidden fallback basis
```

* If a recovered row fails row-level qualification, it must route to `malformed`, `out_of_corpus`, `ambiguous`, `unavailable`, or `rejected_fallback` by explicit reason code; it must not silently become confirmed.
* `membership_key_role = row_id`.
* `member_set_source = sealed current corpus lock / corpus partition included substrate, after corpus manifest sha256 equality is verified`.
* The corpus member row id set must be derived only from included corpus substrate artifacts declared by `layer4_corpus_partition.json`; if the member set cannot be constructed deterministically, close as `blocked_with_layer4_confirmed_measurement_unavailable`.
* Malformed rows are classified before out-of-corpus rows.
* Out-of-corpus rows are separated before confirmed counting.
* `in_corpus_candidate_count = input_edge_row_count - malformed_count - out_of_corpus_count`.
* Malformed rows fail loud into `malformed` or detector contract violation; they must not be skipped silently.
* `allowed_confirmed_edge_type_values = ["placed_in_body_output"]`.
* `rejected_edge_type_values = []` by default; value-level rejection must be introduced only through a recorded no-fallback reason, not silent downgrade.
* `ambiguous_edge_type_conditions` include mixed relation direction, slot scope ambiguity, or a value that is field-present but not contract-supported.
* `unsupported_edge_type_fail_loud_rule`: any `edge_type` other than `placed_in_body_output` blocks as detector contract violation unless the opening decision already routed the artifact to rejected/unavailable before measurement.
* `generated_row_edge_type_handling`: generated rows with `edge_type = placed_in_body_output` may be classified only under Reading A and only after membership join and partition checks.
* `generated_row_provenance_handling`: generated rows are confirmable candidates under generated-edge row-level measurement semantics, not automatic confirmed rows. The forbidden-basis rule forbids using row count or generated provenance as a shortcut; it does not forbid row-level qualified generated generation-time edges from routing to confirmed.
* Unsupported edge types, authority chain mismatch, corpus hash mismatch, or field-map bypass block the closeout.

Path and determinism assumptions:

```text
repository_root = local run-config only; not sealed artifact content
path_normalization = repo_relative_posix_path
json_key_order = stable
jsonl_row_order = file_order_then_line_offset
partition_order = confirmed, rejected_fallback, ambiguous, unavailable, malformed, out_of_corpus
artifact_hashing = sha256
sealed_artifact_paths = repo_relative_posix_path only
```

Template/contract assumptions:

* `docs/PLAN_TEMPLATE.md` is the required plan form for this request.
* `docs/EXECUTION_CONTRACT.md` closeout states are `complete`, `partial`, `implemented_only`, and `blocked`.
* Missing tools or blocked validation commands must be recorded as `blocked` or `not_run`, not `pass`.

---

## 5. Repository Areas Affected

### Code

None expected.

Optional round-local helper scripts may be created only under:

```text
Iris/build/description/v2/staging/compose_contract_migration/layer4_confirmed_current_count_remeasurement_round/
```

Shared build tools are not planned mutation targets. Any shared tooling change requires explicit scope amendment.

### Docs

Plan artifact:

```text
docs/Iris/iris-dvf-3-3-layer4-confirmed-current-count-remeasurement-round-plan.md
```

Potential staged docs candidate after hard gate:

```text
Iris/build/description/v2/staging/compose_contract_migration/layer4_confirmed_current_count_remeasurement_round/docs_addendum_candidate.md
```

Potential live governance docs only after gated promotion:

```text
docs/DECISIONS.md
docs/ARCHITECTURE.md
docs/ROADMAP.md
```

### Config

None expected.

### Generated Artifacts

Round-local generated artifacts may be created under:

```text
Iris/build/description/v2/staging/compose_contract_migration/layer4_confirmed_current_count_remeasurement_round/
```

Expected generated artifacts:

```text
layer4_confirmed_current_count_scope_lock.md
layer4_confirmed_current_count_authority_input_manifest.json
layer4_confirmed_current_count_opening_decision.json
layer4_confirmed_detector_contract.json
layer4_confirmed_detector_input_manifest.json
layer4_confirmed_detector_normalization_report.json
layer4_confirmed_current_count_summary.json
layer4_confirmed_matches.jsonl
layer4_confirmed_rejected_fallback.jsonl
layer4_confirmed_ambiguous.jsonl
layer4_confirmed_unavailable.jsonl
layer4_confirmed_malformed.jsonl
layer4_confirmed_out_of_corpus.jsonl
layer4_confirmed_partition_invariant_report.json
layer4_confirmed_dual_zero_guard_report.json
layer4_confirmed_forbidden_basis_guard_report.json
layer4_confirmed_non_mutation_hash_report.json
layer4_confirmed_validation_report.json
layer4_confirmed_current_count_closeout.json
layer4_confirmed_current_count_closeout.md
artifact_hash_manifest.json
docs_addendum_candidate.md
```

Conditional generated artifacts:

```text
rejected_fallback_rationale.md
  condition = branch_closeout == closed_with_layer4_confirmed_current_count_rejected_fallback

ambiguous_measurement_rationale.md
  condition = branch_closeout == closed_with_layer4_confirmed_current_count_ambiguous

measurement_unavailable_rationale.md
  condition = branch_closeout == blocked_with_layer4_confirmed_measurement_unavailable

detector_contract_violation_rationale.md
  condition = branch_closeout == blocked_with_layer4_confirmed_detector_contract_violation
```

---

## 6. Planned Changes

### Change 1 - Scope Lock / Authority Input Preflight

Purpose:

Prevent the round from drifting into policy redesign, runtime mutation, or publish review, and prove that all sealed input authorities are present before detector execution.

Files:

```text
layer4_confirmed_current_count_scope_lock.md
layer4_confirmed_current_count_authority_input_manifest.json
artifact_hash_manifest.json
```

Implementation Notes:

* Record predecessor readpoints and branch labels.
* Read `layer4_boundary_current_corpus_manifest.json` and `layer4_corpus_partition.json`.
* Read `trace_edge_admission_manifest.json` and `layer4_trace_edges.v1.jsonl`.
* Read `canonical_field_map_manifest.json` from the field-map reseal round.
* Load-bearing authority verification is keyed by sealed sha256 and known sealed artifact identity, not by manifest filename alone.
* Verify corpus lock manifest sha256 equals `d394f95f5f2a157679238e005a90929349eb807a8180824d8f0ed30240290402`.
* Verify trace-edge artifact sha256 against the admission manifest and field-map manifest.
* Verify `input_artifact_partition = current_detector_input`.
* Verify `field_map_version = field_map.v1`.
* Verify `field_map_sealed = true`.
* Record that prior zero-count and Branch B trace absence are not count input.
* Record `runtime_mutation_allowed = false`.
* Record `publish_review_opened = false`.

Validation:

* Authority input manifest JSON parse pass.
* Required input artifacts exist or explicit blocked reason is recorded.
* Corpus lock manifest sha256 equality pass.
* Trace-edge artifact hash equality pass.
* Field-map input hash equality pass.
* Sealed sha256, not filename-only existence, is the pass criterion for load-bearing authority input verification.
* Authority chain mismatch count `0`.
* Missing input or mismatch blocks detector execution.

---

### Change 2 - Opening Decision Seal

Purpose:

Record the authority-consumption preflight decision before measurement execution without re-adjudicating sealed predecessor authority.

Files:

```text
layer4_confirmed_current_count_opening_decision.json
layer4_confirmed_forbidden_basis_guard_report.json
```

Implementation Notes:

* Record selected reading:

```text
Reading A = admitted generated edge rows are valid current_detector_input rows to classify.
Reading B = authority-consumption failed before row-level classification, so rows are rejected/unavailable rather than measured.
```

* Reading A also carries the v0.3 measurement semantics decision:

```text
admitted generated generation-time edge rows are confirmable detector inputs,
but only through row-level partitioning after sealed authority, corpus membership,
field-map, edge_type, and forbidden-basis checks.
```

* Reading A is the default if artifact existence, corpus manifest hash, trace-edge hash, partition, authority chain, and field-map checks pass.
* Reading B is allowed only on concrete authority-consumption failure:
  * missing artifact
  * hash mismatch
  * partition mismatch
  * field-map role binding failure
  * schema or required field violation before row-level classification
  * authority chain mismatch
* Reading B must record:

```text
selected_reading_reason_code
failing_artifact
failing_field_or_manifest_key
evidence_path
confirmed_count = null
confirmed_count_status = not_computed
confirmed_measurement_executed = false
```

* If Reading A is selected, measurement may classify rows but may not prefill confirmed count from row count.
* If Reading A is selected, generated provenance is not a rejection reason by itself and is not a confirmation reason by itself.
* If Reading B is selected, route the branch to `rejected_fallback` or `unavailable` according to the recorded authority-consumption failure. This is not detector-executed zero.
* Record forbidden bases:
  * prior zero-count
  * text similarity
  * keyword residue
  * rendered substring
  * cluster/provenance label
  * source/target co-occurrence only
  * detector readiness dry-run pass
  * admitted row count itself
* If no explicit reading is selected, close as `blocked_missing_opening_decision`.

Validation:

* Opening decision artifact exists.
* Exactly one reading selected.
* Reading B has concrete failure evidence fields if selected.
* Reading A remains selected when all authority-consumption checks pass.
* Forbidden basis list present.
* No detector execution starts before opening decision exists.
* Any reference to row count `24` is labeled as shape metric until detector partitioning completes.
* Reading A semantics are recorded as generated-generation-time row-level confirmability, not as row-count shortcut approval.

---

### Change 3 - Detector Contract Freeze

Purpose:

Define what can be counted as confirmed and how every non-confirmed case is partitioned before running the detector.

Files:

```text
layer4_confirmed_detector_contract.json
layer4_confirmed_detector_input_manifest.json
```

Implementation Notes:

Required field roles:

```text
source_ref
row_id
destination_slot
edge_type
```

Support-only field:

```text
edge_basis
```

Derivation and generated provenance policy:

```text
edge_derivation = recovered | generated_generation_time
edge_derivation_source = edge_basis
edge_basis_missing_or_schema_invalid = malformed
edge_basis_present_but_unmapped = ambiguous with reason_code EDGE_BASIS_UNMAPPED
generated_provenance_route = confirmed_candidate_under_reading_a
generated_provenance_row_is_confirmed_by_default = false
admitted_row_count_itself_forbidden = true
```

Required count fields:

```text
input_edge_row_count
in_corpus_candidate_count
confirmed_count
confirmed_count_status
rejected_fallback_count
ambiguous_count
unavailable_count
malformed_count
out_of_corpus_count
```

Membership join rule:

```text
membership_key_role = row_id
member_set_source = layer4_corpus_partition.json included substrate, gated by
  layer4_boundary_current_corpus_manifest.json sha256 =
  d394f95f5f2a157679238e005a90929349eb807a8180824d8f0ed30240290402
member_set_derivation = deterministic row_id/member identity extraction from included corpus substrate artifacts only
membership_failure = blocked_with_layer4_confirmed_measurement_unavailable
malformed_precedes_membership = true
```

Partition formula:

```text
confirmed_count = count(rows where disposition == "confirmed")
partition_sum = confirmed + rejected_fallback + ambiguous + unavailable + malformed + out_of_corpus
partition_sum must equal input_edge_row_count unless detector_contract_violation blocks before partition write
in_corpus_candidate_count = input_edge_row_count - malformed_count - out_of_corpus_count
```

Edge type policy:

```text
allowed_confirmed_edge_type_values = ["placed_in_body_output"]
rejected_edge_type_values = []
ambiguous_edge_type_conditions = relation direction ambiguity, slot scope ambiguity, field-present but contract-unsupported value
unsupported_edge_type_fail_loud_rule = any edge_type other than placed_in_body_output blocks unless Reading B routed before measurement
generated_row_edge_type_handling = generated row may be classified only when Reading A passes and edge_type == placed_in_body_output
```

Generated row confirmed condition:

```text
explicit_trace_edge_condition =
  field roles are resolved through sealed field_map.v1
  and relation tuple source_ref -> edge_type -> destination_slot is present
  and edge_type == placed_in_body_output
  and edge_derivation is recovered or generated_generation_time
  and no forbidden fallback basis is used

generated_row_confirmed_condition =
  reading == Reading A
  and edge_derivation == generated_generation_time
  and admission_partition == current_detector_input
  and sealed sha256 checks pass
  and field_map_sealed == true
  and row_id joins to sealed current corpus member set
  and edge_type == placed_in_body_output
  and edge_basis in ["recovered_body_plan_relation_trace", "recovered_compose_relation_trace"]
  and required role fields are present and non-empty
  and row is not malformed
  and row is not out_of_corpus
  and forbidden fallback basis is not used

recovered_row_confirmed_condition =
  reading == Reading A
  and edge_derivation == recovered
  and admission_partition == current_detector_input
  and sealed sha256 checks pass
  and field_map_sealed == true
  and row_id joins to sealed current corpus member set
  and edge_type == placed_in_body_output
  and required role fields are present and non-empty
  and row is not malformed
  and row is not out_of_corpus
  and forbidden fallback basis is not used
```

Disposition meanings:

```text
confirmed = row satisfies sealed field map, current corpus boundary, opening decision, and explicit trace-edge condition
rejected_fallback = row or artifact is rejected by no-fallback evidence rule; confirmed_count must remain null/not_computed for decision-only rejected fallback
ambiguous = row has relevant fields but relation, slot, identity, or edge semantics cannot be resolved
ambiguous_edge_basis_unmapped = edge_basis is present but not mapped to recovered or generated_generation_time; reason_code = EDGE_BASIS_UNMAPPED
unavailable = row cannot support count under current authority despite valid input shape
malformed = row violates schema or required role shape
out_of_corpus = row is not inside current corpus membership boundary
```

Validation:

* Contract JSON parse pass.
* Required field roles present in field-map manifest.
* Corpus member set derivation recorded.
* Membership key role is `row_id`.
* `in_corpus_candidate_count` formula recorded.
* Malformed classification precedes out-of-corpus classification.
* `allowed_confirmed_edge_type_values` contains only `placed_in_body_output`.
* `generated_provenance_route` is recorded.
* `explicit_trace_edge_condition` is recorded.
* `recovered_row_confirmed_condition` is recorded.
* Generated provenance alone cannot route to `confirmed`.
* Generated row confirmed condition is present and references row-level detector qualification.
* Unmapped `edge_basis` routes to ambiguous with reason code `EDGE_BASIS_UNMAPPED`.
* Unsupported edge type rule is fail-loud.
* Missing required role rule is fail-loud.
* Field-map bypass rule is fail-loud.
* Forbidden basis cannot route to `confirmed`.

---

### Change 4 - Detector Construction / Dry Verification

Purpose:

Build a deterministic detector harness that consumes sealed inputs without producing a count claim during dry verification.

Files:

```text
layer4_confirmed_detector_normalization_report.json
layer4_confirmed_detector_input_manifest.json
```

Implementation Notes:

* Load JSONL rows from `layer4_trace_edges.v1.jsonl`.
* Resolve fields only through `canonical_field_map_manifest.json`.
* Resolve current corpus membership by joining each sidecar row's `row_id` to the deterministic member set derived from `layer4_corpus_partition.json` included substrate artifacts.
* Build the member set only after corpus manifest sha256 equality passes.
* If included substrate row identities cannot be extracted deterministically, stop as `blocked_with_layer4_confirmed_measurement_unavailable`; do not continue with all rows treated as in-corpus or out-of-corpus by default.
* Normalize each input row into a detector row model.
* Prepare partition writers for all six partitions.
* Dry verification may check parsing, field binding, membership lookup, and deterministic ordering.
* Dry verification must keep `confirmed_measurement_executed = false` and `confirmed_count = not_computed`.

Validation:

* JSON/JSONL parse pass.
* Input sha256 matches authority manifest.
* Field map bypass count `0`.
* Corpus manifest hash equality pass before member-set construction.
* Membership resolver records `membership_key_role = row_id`.
* Member set derivation source paths recorded.
* Member set derivation failure blocks measurement.
* Malformed row handling is explicit.
* Dry verification does not emit count summary with integer `confirmed_count`.
* Deterministic row ordering is stable across two dry runs.

---

### Change 5 - Confirmed Count Measurement / Partition Write

Purpose:

Execute the detector and write partitioned evidence without collapsing non-confirmed cases into zero or positive.

Files:

```text
layer4_confirmed_current_count_summary.json
layer4_confirmed_matches.jsonl
layer4_confirmed_rejected_fallback.jsonl
layer4_confirmed_ambiguous.jsonl
layer4_confirmed_unavailable.jsonl
layer4_confirmed_malformed.jsonl
layer4_confirmed_out_of_corpus.jsonl
```

Implementation Notes:

* Execute detector only after Changes 1-4 pass.
* Classify malformed rows before semantic disposition.
* Classify out-of-corpus rows after malformed rows and before confirmed counting.
* Apply opening decision.
* Accept `confirmed` only for rows satisfying explicit detector execution conditions, including `generated_row_confirmed_condition` when `edge_derivation = generated_generation_time`.
* Do not accept all generated rows as confirmed by provenance. A generated row must pass row-level detector qualification.
* Do not reject all generated rows by provenance under Reading A. Rejection requires a concrete row-level or authority-consumption reason.
* Write every input row to exactly one partition.
* Record row-level reason codes for all non-confirmed partitions.
* For `closed_with_layer4_confirmed_current_count_rejected_fallback`, write schema-level status as:

```json
{
  "confirmed_count": null,
  "confirmed_count_status": "not_computed",
  "confirmed_measurement_executed": false
}
```

* If contract violation prevents row-level partitioning, do not write a count summary as if execution succeeded.

Validation:

* `confirmed_measurement_executed = true` for measured branches.
* `confirmed_count` equals `layer4_confirmed_matches.jsonl` row count.
* Partition counts sum to input row count.
* `in_corpus_candidate_count = input_edge_row_count - malformed_count - out_of_corpus_count`.
* `input_edge_row_count = 24` is shape metric only.
* `confirmed_count_basis = detector_execution`.
* `confirmed_count_scope = row-level qualified admitted generated generation-time trace-edge rows` when confirmed rows have generated derivation.
* If zero, `zero_count_basis = detector_executed_zero`.
* Rejected fallback branch uses `confirmed_count = null` and `confirmed_count_status = not_computed`.
* Rejected fallback, ambiguous, unavailable, malformed, and out-of-corpus are not counted as confirmed.
* Two-run determinism pass.

---

### Change 6 - Branch Resolution / Dual-Zero Guard

Purpose:

Resolve exactly one terminal branch and prevent old trace absence or unavailable state from being misread as detector-executed zero.

Files:

```text
layer4_confirmed_partition_invariant_report.json
layer4_confirmed_dual_zero_guard_report.json
layer4_confirmed_current_count_closeout.json
```

Implementation Notes:

Branch decision rules:

| Condition | Branch closeout |
|---|---|
| Detector executed and `confirmed_count >= 1` through row-level qualified admitted generated generation-time trace-edge rows or recovered rows | `closed_with_layer4_confirmed_current_count_measured_positive` |
| Detector executed and `confirmed_count == 0`, with all rows otherwise validly partitioned | `closed_with_layer4_confirmed_current_count_measured_zero_detector_executed` |
| Authority-consumption failure, no-fallback rule, or explicit row-level rejected-fallback reason rejects input as grounding before measured count | `closed_with_layer4_confirmed_current_count_rejected_fallback` |
| Rows are field-valid but relation, slot, identity, or edge semantics remain unresolved | `closed_with_layer4_confirmed_current_count_ambiguous` |
| Detector cannot compute under current authority | `blocked_with_layer4_confirmed_measurement_unavailable` |
| Required field roles, schema, authority chain, or detector contract is violated | `blocked_with_layer4_confirmed_detector_contract_violation` |

Dual-zero guard:

```text
prior_trace_absent_zero = forbidden as current count
detector_executed_zero = allowed only if detector ran and partition invariants passed
unavailable = not_computed, not zero
rejected_fallback = not_computed with confirmed_count null, not zero
ambiguous = not zero
generated_generation_time_positive = allowed only by row-level detector qualification, not by admitted row count
```

Validation:

* Exactly one branch selected.
* Complete branch has validation ceiling.
* Blocked branch does not publish integer `confirmed_count`.
* Rejected fallback branch does not publish integer `confirmed_count`.
* Dual-zero guard report exists.
* Branch label matches count summary and partition manifests.

---

### Change 7 - Non-Mutation / Surface Guard

Purpose:

Prove the round is measurement-only and did not mutate source, rendered, runtime, or public-facing surfaces.

Files:

```text
layer4_confirmed_non_mutation_hash_report.json
layer4_confirmed_validation_report.json
```

Implementation Notes:

* Before Change 1 writes any artifact, capture a pre-execution hash manifest for declared non-mutation targets.
* After final artifact generation, capture a post-execution hash manifest for the same declared targets.
* Compare only declared non-mutation targets; generated round-local evidence root is excluded from non-mutation comparison.
* Python unittest is not part of this round's required validation. If an operator explicitly runs unittest anyway, non-mutation hashing must be isolated from unittest side effects by either restoring the frozen rendered snapshot before post-hash capture or recording the unittest run as outside the non-mutation proof.

Minimum non-mutation hash targets:

```text
Iris/build/description/v2/data/dvf_3_3_facts.jsonl
Iris/build/description/v2/data/dvf_3_3_decisions.jsonl
Iris/build/description/v2/output/dvf_3_3_rendered.json
Iris/build/description/v2/staging/body_role/phase2/layer3_role_check_overlay.jsonl
Iris/build/description/v2/tools/style/rules/structural_rules.json
Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks/*.lua
Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks.lua
Iris/media/lua/client/Iris/Data/IrisLayer3Data.lua
Iris/build/description/v2/staging/compose_contract_migration/layer4_boundary_current_corpus_lock_round/layer4_boundary_current_corpus_manifest.json
Iris/build/description/v2/staging/compose_contract_migration/layer4_boundary_current_corpus_lock_round/layer4_corpus_partition.json
Iris/build/description/v2/staging/compose_contract_migration/layer4_trace_edge_authority_admission_round/trace_edge_admission_manifest.json
Iris/build/description/v2/staging/compose_contract_migration/layer4_trace_edge_authority_admission_round/layer4_trace_edges.v1.jsonl
Iris/build/description/v2/staging/compose_contract_migration/layer4_confirmed_detector_field_map_reseal_round/canonical_field_map_manifest.json
```

If any path is absent, record one of:

```text
absent_expected
absent_unexpected
not_applicable
```

Validation:

* Source facts mutation `0`.
* Source decisions mutation `0`.
* Rendered text mutation `0`.
* Runtime Lua mutation `0`.
* Packaged Lua mutation `0`.
* State axis mutation `0`.
* Public-facing behavior mutation `0`.
* Pre/post hash capture timing recorded.
* Unittest status is `not_required`, `not_run`, or explicitly isolated from non-mutation proof.
* Generated evidence root is the only intended new artifact surface.

---

### Change 8 - Closeout / Gated Docs Candidate

Purpose:

Seal the detector result or blocked reason and prepare additive governance updates only after gates pass.

Files:

```text
layer4_confirmed_current_count_closeout.md
docs_addendum_candidate.md
```

Implementation Notes:

* Write closeout with `contract_closeout_state`, `branch_closeout`, count summary, validation ceiling, and non-claims.
* Closeout validation ceiling must record that the review surface did not itself revalidate `docs/PLAN_TEMPLATE.md`, `docs/EXECUTION_CONTRACT.md`, VCS history, or every predecessor round-local artifact body unless those were explicitly read during execution.
* Closeout reviewer limitation note must preserve this wording when applicable: `PLAN_TEMPLATE.md / EXECUTION_CONTRACT.md and round-local artifacts were not part of this review surface.`
* Closeout validation ceiling must record that Python unittest and Lua syntax are outside the required evidence ceiling because this round does not mutate runtime Lua, source facts, or rendered outputs, unless those commands are explicitly run and reported with exact exit code.
* Add DECISIONS closeout candidate.
* Add ARCHITECTURE compact evidence capsule candidate.
* Add ROADMAP ledger update candidate.
* Do not edit live canonical docs before review gate.
* Do not rewrite predecessor entries.
* If review returns Conditional PASS, require explicit user/operator acceptance before live governance doc promotion.

Validation:

* Closeout branch matches artifacts.
* Validation ceiling has `validated`, `out_of_scope`, and `unvalidated_but_in_scope`.
* Non-claims present.
* Docs candidate is additive-only.
* `all_gates_pass = true` only when every named gate passes.

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
primary input artifacts exist
input sha256 verification
corpus lock manifest sha256 equality =
  d394f95f5f2a157679238e005a90929349eb807a8180824d8f0ed30240290402
authority chain verification
admission partition check = current_detector_input
field_map_version check = field_map.v1
opening decision authority-consumption gate check
detector contract parse/check
field-map-only role resolution check
current corpus membership resolver check with membership_key_role = row_id
member set derivation from sealed corpus partition included substrate
malformed-before-out_of_corpus ordering check
in_corpus_candidate_count formula check
edge_type policy check with allowed_confirmed_edge_type_values = ["placed_in_body_output"]
edge_derivation extraction from edge_basis
edge_basis missing/schema-invalid -> malformed check
edge_basis present-but-unmapped -> ambiguous with EDGE_BASIS_UNMAPPED check
generated_provenance_route = confirmed_candidate_under_reading_a check
explicit_trace_edge_condition check
generated row confirmed condition check
recovered row confirmed condition check
generated provenance alone cannot route to confirmed check
admitted row count shortcut forbidden check
forbidden basis negative-control check
dry verification no-count check
measurement partition invariant check
count/manifest consistency check
rejected_fallback confirmed_count_status = not_computed check
dual-zero separation check
branch resolution single-result invariant
two-run determinism check
artifact hash manifest validation
pre/post non-mutation hash diff over declared targets
claim ceiling check
evidence ceiling limitation note check
review gate check
```

Optional repo validation only if touched surface requires it:

```powershell
python -B -m unittest discover -s Iris\build\description\v2\tests -p "test_*.py"
powershell -ExecutionPolicy Bypass -File .\tools\check_lua_syntax.ps1
```

These optional commands may be claimed as passed only if the exact command exits with code `0`.

These commands are optional because this round is a measurement artifact round over sealed staging inputs and is not expected to mutate runtime Lua or shared build tooling. If Python unittest is run, its known rendered-output side effects must be isolated before non-mutation hash proof is claimed.

Because this round does not touch runtime Lua, source facts, or rendered outputs, Python unittest and Lua syntax are outside the required evidence ceiling unless explicitly run.

Optional validation status must be recorded with one of:

```text
not_required
not_run
blocked_missing_tool
pass
fail
```

### Manual Validation

* Review that this is count measurement / non-count branch sealing only, not Layer4 policy redesign.
* Review that admitted edge row count `24` is never used directly as confirmed count.
* Review that corpus lock manifest sha256 is pinned and verified.
* Review selected opening decision before detector execution, including that Reading B is only an authority-consumption failure branch.
* Review sidecar edge row membership join by `row_id`.
* Review member set derivation from sealed corpus partition included substrate.
* Review that prior zero-count and 2026-05-31 trace absence are not inherited.
* Review field-map role use through `source_ref`, `row_id`, `destination_slot`, and `edge_type`.
* Review that `edge_basis` remains support-only.
* Review `edge_type = placed_in_body_output` as the only allowed confirmed edge type.
* Review `edge_derivation` extraction from `edge_basis`.
* Review unmapped `edge_basis` disposition and `EDGE_BASIS_UNMAPPED` reason code.
* Review generated-provenance routing: generated generation-time rows are confirmable candidates under Reading A, not automatic confirmed rows.
* Review recovered-row confirmed condition symmetry.
* Review that admitted row count shortcut remains forbidden even when generated rows are confirmable row-by-row.
* Review measured-positive wording if any confirmed rows are generated generation-time rows.
* Review rejected fallback / ambiguous / unavailable / malformed / out-of-corpus reason codes.
* Review that rejected fallback uses `confirmed_count = null` and `confirmed_count_status = not_computed`.
* Review dual-zero guard.
* Review pre/post non-mutation hash capture timing and unittest side-effect handling.
* Review branch closeout and count summary consistency.
* Review non-mutation report and validation ceiling.
* Review docs addendum candidate for additive-only wording and non-claims.

### Validation Limits

This execution will not perform:

* no runtime validation
* no in-game / MIGV-QA validation
* no multiplayer validation
* no deployment validation
* no long-session runtime validation
* no release validation
* no public-facing behavior validation beyond static non-mutation
* no tooltip validation
* no Workshop readiness validation
* no B42 readiness validation
* no external ecosystem compatibility sweep
* no semantic quality completion validation
* no publish mutation review validation
* no Layer4 policy redesign validation

---

## 8. Risk Surface Touch

### Authority Surface

Touched by the future execution. This round creates additive count authority / measurement authority for `LAYER4_ABSORPTION_CONFIRMED`, or an additive authoritative non-count branch reason.

It does not create source facts authority, source decisions authority, rendered text authority, runtime authority, publish writer authority, or default compose authority.

### Runtime Behavior Surface

None intended. Runtime Lua, packaged Lua, Browser, Wiki, Tooltip, item selection, rendered text, and player-facing behavior remain unchanged.

### Compatibility Surface

Low / internal tooling only. External mod compatibility and PZ runtime behavior are not touched. The only format surface is round-local JSON/JSONL evidence.

### Sealed Artifact Surface

Touched additively. The round may create new sealed measurement artifacts. Existing 2026-05-31, 2026-06-01, and 2026-06-02 sealed readpoints are consumed read-only.

Sealed artifacts must use repository-relative POSIX paths. Absolute local paths may appear only in local run logs or run config, not promoted sealed artifacts.

### Public-Facing Output Surface

None intended. No item description, tooltip copy, wiki behavior, README public claim, Workshop status, release note, or B42 readiness claim is opened.

---

## 9. Risk Analysis

### Architecture Risk

* The measurement result could be mistaken for Layer4 absorption resolved.
* A positive count could be mistaken for publish mutation review approval.
* A detector-executed zero could be mistaken for prior zero-count inheritance.
* Rejected fallback or unavailable state could be collapsed into zero.
* The admitted generated sidecar could be mistaken for a new structural axis.
* The opening decision could silently encode predecessor authority re-adjudication if not constrained to objective authority-consumption failure.
* The count denominator could drift if corpus manifest sha256 or `row_id` membership join is not enforced.
* Generated generation-time rows could be mistaken for automatic confirmed rows rather than row-level confirmable detector inputs.
* Conversely, generated provenance could be mistakenly rejected solely by provenance despite Reading A and sealed admission.
* Branch vocabulary could create a new unapproved closeout state unless mapped back to `complete` or `blocked`.

### Runtime Risk

* Expected runtime risk is none if scope is respected.
* A validation helper could accidentally regenerate rendered/runtime surfaces.
* Any side-effect mutation must block closeout until identified and corrected.
* Absolute local paths could leak into sealed artifacts if run-config output is promoted without filtering.

### Compatibility Risk

* Future tooling could overfit to this round's partition schema.
* Future readers could treat internal count authority as public-facing compatibility evidence.
* External mod compatibility must not be claimed without a separate compatibility sweep.

### Regression Risk

* JSONL ordering or serialization could be nondeterministic.
* Row identity may be confused between edge artifact row identity and Layer3 row/item identity.
* Current corpus membership could be misapplied to a sidecar row.
* Corpus member set derivation could accidentally consume excluded or diagnostic surfaces.
* `in_corpus_candidate_count` could drift if malformed and out-of-corpus ordering is reversed.
* Unsupported `edge_type` values could be skipped instead of fail-loud.
* Malformed rows could be silently dropped.
* Ambiguous rows could be forced into zero or positive.
* Generated rows could silently route to confirmed without satisfying `generated_row_confirmed_condition`.
* Rejected fallback could accidentally publish `confirmed_count = 0` instead of `confirmed_count_status = not_computed`.
* Count summary and partition manifests could diverge.
* Dirty working tree state could make non-mutation evidence hard to interpret.
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
Iris/build/description/v2/staging/compose_contract_migration/layer4_confirmed_current_count_remeasurement_round/
```

3. If optional helper scripts were created and are invalid, remove or quarantine only those round-local helper scripts.

4. If shared tooling was changed without explicit scope amendment, stop and revert only changes made by this round after identifying them.

5. If `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, or `docs/ROADMAP.md` receive invalid additive wording, correct with additive clarification when possible. If duplicate text was added by this round, remove only that duplicate addition.

6. If source facts, source decisions, rendered text, runtime Lua, packaged Lua, bridge payload, `quality_state`, `publish_state`, or `runtime_state` changed unexpectedly, stop and identify the exact source of mutation before reverting only this round's changes.

7. If detector output uses admitted row count `24` as confirmed count without row-level partitioning, discard the evidence root and rerun from the opening decision phase.

8. If unavailable, rejected fallback, or ambiguous state was written as `confirmed_count = 0`, discard the count summary and rewrite branch resolution before closeout.

9. If count summary and manifests disagree, closeout must stop and the evidence root must be marked invalid/quarantined.

10. If corpus manifest sha256 or membership join evidence is missing after execution, closeout must stop and the evidence root must be marked invalid/quarantined.

11. If a sealed closeout later proves wrong, do not rewrite the sealed record. Open an additive successor correction round.

---

## 11. Governance Constraints

* `docs/Philosophy.md` compliance is mandatory.
* Iris remains wiki/fact-oriented and must not introduce interpretation, recommendation, or comparison.
* Hub & Spoke and SPI boundaries remain untouched.
* Runtime/build-time separation must remain intact.
* The 2026-05-31 current corpus lock remains an immutable predecessor.
* The 2026-05-31 corpus lock manifest sha256 must equal `d394f95f5f2a157679238e005a90929349eb807a8180824d8f0ed30240290402`.
* The 2026-06-01 trace-edge authority admission remains an immutable predecessor.
* The 2026-06-02 detector field-map reseal remains an immutable predecessor.
* `layer4_trace_edges.v1.jsonl` is consumed read-only.
* `canonical_field_map_manifest.json` is consumed read-only.
* Opening decision must exist before detector execution and must remain an authority-consumption gate, not predecessor re-adjudication.
* Reading A is default when sealed artifact/hash/partition/field-map checks pass.
* Reading B is allowed only with concrete authority-consumption failure evidence.
* Sidecar membership join key is `row_id`.
* Member set source is sealed current corpus lock / corpus partition included substrate only.
* `in_corpus_candidate_count = input_edge_row_count - malformed_count - out_of_corpus_count`.
* Malformed classification precedes out-of-corpus classification.
* Prior zero-count must not be inherited as current count.
* Admitted edge row count `24` must not be read as confirmed count.
* `edge_basis` must not be promoted to independent confirmed evidence.
* `edge_type = placed_in_body_output` is the only allowed confirmed edge type for this plan.
* `edge_derivation` is derived only from `edge_basis`.
* Missing, null, non-string, or schema-invalid `edge_basis` routes to `malformed`.
* Present-but-unmapped `edge_basis` routes to `ambiguous` with reason code `EDGE_BASIS_UNMAPPED`.
* `generated_provenance_route = confirmed_candidate_under_reading_a`.
* Generated generation-time rows are confirmable detector inputs under Reading A only after row-level detector qualification.
* Generated provenance alone is not sufficient for confirmed routing.
* Generated provenance alone is not a rejection reason under Reading A.
* Recovered rows use a symmetric row-level confirmed condition and are not confirmed by provenance alone.
* Unsupported edge type must fail loud unless the artifact was already routed to rejected/unavailable before measurement.
* Text similarity, keyword, rendered substring, category tag, cluster/provenance label, source/target co-occurrence-only fallback, prior zero-count, and dry-run pass are forbidden count bases.
* Historical, diagnostic, report-only, preview-only, staging residue, and test fixture surfaces must not be promoted to current detector input.
* Missing required fields must fail loud or route to blocked closeout.
* Ambiguous rows must remain ambiguous and must not be forced into positive or zero.
* Rejected fallback must remain rejected with `confirmed_count = null` and `confirmed_count_status = not_computed`; it must not be forced into zero.
* Unavailable state must remain `not_computed` and must not be forced into zero.
* Non-mutation proof must capture pre-execution and post-execution hashes for declared targets.
* Python unittest is not required; if run, its known rendered-output side effects must be isolated before non-mutation proof is claimed.
* Python unittest and Lua syntax are outside the required evidence ceiling because this round does not mutate runtime Lua, source facts, or rendered outputs, unless explicitly run.
* Source facts, source decisions, rendered text, runtime Lua, packaged Lua, bridge payload, `quality_state`, `publish_state`, and `runtime_state` remain non-mutation targets.
* Live canonical docs promotion requires review PASS or accepted Conditional PASS.
* Accepted Conditional PASS requires explicit user/operator acceptance before live governance doc promotion.
* Additive docs wording must preserve non-claims and validation ceiling.
* Validation may not be claimed as passed unless the exact relevant command exits with code `0`.
* Release readiness, Workshop readiness, deployment readiness, B42 readiness, and `ready_for_release` claims are forbidden.

---

## 12. Expected Closeout State

Expected contract closeout state:

```text
complete or blocked
```

`complete` is valid only for:

```text
closed_with_layer4_confirmed_current_count_measured_positive
closed_with_layer4_confirmed_current_count_measured_zero_detector_executed
closed_with_layer4_confirmed_current_count_rejected_fallback
closed_with_layer4_confirmed_current_count_ambiguous
```

`blocked` is valid for:

```text
blocked_with_layer4_confirmed_measurement_unavailable
blocked_with_layer4_confirmed_detector_contract_violation
blocked_missing_current_corpus_lock
blocked_missing_trace_edge_authority
blocked_missing_detector_field_map
blocked_authority_chain_mismatch
blocked_missing_opening_decision
blocked_partition_invariant_failed
blocked_non_mutation_invariant_failed
blocked_review_gate_failed
blocked_claim_overreach
```

`partial` and `implemented_only` are not planned sealed success states for this round.

Complete measured positive may claim only:

```text
The detector executed under the sealed corpus/trace-edge/field-map authorities,
and confirmed_count is a positive integer backed by confirmed match manifest rows.
If confirmed rows are generated generation-time rows, the claim is limited to
row-level qualified admitted generated generation-time trace-edge rows under Reading A.
It is not a claim that admitted row count 24 was copied into confirmed_count.
```

Complete measured zero may claim only:

```text
The detector executed under the sealed authorities, all input rows were partitioned,
and confirmed_count is 0 because detector execution found no confirmed qualifying row.
This is not inherited prior zero-count.
```

Complete rejected fallback may claim only:

```text
The authority-consumption gate or no-fallback rule rejected the admitted/generated edge rows
as confirmed grounding, so confirmed_count = null and
confirmed_count_status = not_computed. Rejection is not zero and not detector-executed zero.
```

Complete ambiguous may claim only:

```text
The detector inputs were present, but relation, identity, slot, or edge semantics
remained ambiguous under the sealed contract. Ambiguity is not positive and not zero;
if no measured count can be computed, confirmed_count_status remains not_computed.
```

Blocked closeout may claim only:

```text
The round could not produce a validated detector count or terminal non-count branch
because an input, authority chain, detector contract, partition invariant,
non-mutation invariant, review gate, or claim boundary failed.
```

Expected final non-claims:

```text
Layer4 absorption resolved 아님
Layer4 policy redesign 아님
SUSPECT tier coverage 아님
FUNCTION_NARROW second rollout 아님
ACQ_DOMINANT publish review 아님
publish mutation review 아님
source facts mutation 아님
source decisions mutation 아님
rendered text mutation 아님
runtime Lua mutation 아님
packaged Lua mutation 아님
quality_state / publish_state / runtime_state mutation 아님
Browser / Wiki / Tooltip behavior change 아님
runtime rollout 아님
manual in-game validation pass 아님
deployment 아님
Workshop readiness 아님
B42 readiness 아님
release readiness 아님
ready_for_release 아님
prior zero-count inheritance 아님
generated edge row count 24 direct-confirmed-count claim 아님
generated provenance alone confirmed claim 아님
admitted row count shortcut 아님
```

Next round opening condition:

```text
Any publish mutation review, semantic quality interpretation, public-facing exposure,
or Layer4 policy redesign requires a separate approved plan after this measurement
round closes.
```
