# Iris DVF 3-3 Layer4 Confirmed Detector Field Map Reseal Round Plan

> 상태: Draft v0.3-second-pass-feedback-applied
> 기준일: 2026-06-02
> 상위 기준: `docs/Philosophy.md`, `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`
> authority input: `ROADMAP - Layer4 Confirmed Detector Field Map Reseal` (2026-06-01 user-provided pasted roadmap)
> review input: `REVIEW - Integrated Review: Iris DVF 3-3 Layer4 Confirmed Detector Field Map Reseal Round Plan` (2026-06-02 user-provided synthesis). v0.2 applies Critical C-1 by removing predecessor-colliding branch aliases, and incorporates R2-R11 as execution/audit hardening.
> second-pass review input: `REVIEW - Integrated 2nd Pass Review: Iris DVF 3-3 Layer4 Confirmed Detector Field Map Reseal Round Plan v0.2` (2026-06-02 user-provided synthesis). v0.3 applies Critical C2-1 by aligning `§1 Objective` topology to `source_object -> explicit_edge_relation -> destination_body_slot` with `target_layer3_row_or_item` as identity anchor, and incorporates Minor R2-2/R2-3 plus template/contract verification note.
> 직접 상위 readpoint:
> - 2026-05-31 Layer4 Boundary Current Corpus Lock Round `closed_with_layer4_boundary_current_corpus_locked_no_count_inheritance_design_preflight`
> - 2026-05-31 Layer4 Confirmed Detector Field Map Seal Round `closed_with_confirmed_measurement_unavailable_trace_absent`
> - 2026-06-01 Layer4 Trace-Edge Authority Admission Round `EDGE_AUTHORITY_PRODUCED_AND_ADMITTED`
> 계획 형식: `docs/PLAN_TEMPLATE.md`
> template attestation: this plan follows the 1-12 section structure in `docs/PLAN_TEMPLATE.md`.
> execution_contract_reference: `docs/EXECUTION_CONTRACT.md` checked for closeout-state vocabulary and claim ceiling discipline.
> template_contract_verify_status: `docs/PLAN_TEMPLATE.md` and `docs/EXECUTION_CONTRACT.md` checked by the plan author in-session; closeout-state vocabulary is `{complete, partial, implemented_only, blocked}`.
> draft_origin: AI-assisted draft from user-provided roadmap; execution requires normal review/gate approval.
> execution_scale: governance
> scope_qualifier: `detector_field_map_reseal_against_admitted_trace_edge_authority`
> 실행 상태: planning authority only. This document opens no `LAYER4_ABSORPTION_CONFIRMED` count, runtime mutation, publish mutation review, deployment, release, or closeout claim.

---

## 1. Objective

이번 execution plan의 목적은 2026-06-01에 admitted 된 trace-edge sidecar artifact인 `layer4_trace_edges.v1.jsonl`을 기준으로, `LAYER4_ABSORPTION_CONFIRMED` confirmed detector가 실제로 읽을 canonical field map을 봉인하는 것이다.

이번 라운드가 답해야 하는 질문은 다음 하나로 제한한다.

```text
admitted trace-edge artifact 기준으로
source_object -> explicit_edge_relation -> destination_body_slot,
with target_layer3_row_or_item as the row/item identity anchor.
이 topology를 detector가 해석 없이 읽을 수 있는 canonical field map이 있는가?
```

The target row/item is not a sequential hop between relation and slot. It is the identity anchor used to locate the row/item that owns the `source_object -> destination_body_slot` relation.

Round id:

```text
layer4_confirmed_detector_field_map_reseal_round
```

Round-local artifact root:

```text
Iris/build/description/v2/staging/compose_contract_migration/layer4_confirmed_detector_field_map_reseal_round/
```

Primary input:

```text
Iris/build/description/v2/staging/compose_contract_migration/layer4_trace_edge_authority_admission_round/layer4_trace_edges.v1.jsonl
```

Branch taxonomy:

```text
complete_success:
  closed_with_layer4_confirmed_detector_field_map_resealed
  shorthand = FIELD_MAP_SEALED

complete_negative_seal:
  closed_with_field_map_trace_absent_admitted_artifact
  shorthand = TRACE_EDGE_ABSENT_ADMITTED_ARTIFACT

blocked:
  closed_with_field_map_ambiguous_admitted_artifact
  shorthand = FIELD_MAP_AMBIGUOUS
```

Closeout vocabulary rule:

```text
Use only the canonical branch_closeout labels above in sealed artifacts.
The shorthand values are review/navigation labels only and must not be written as branch_closeout.
Do not introduce *_MEASUREMENT_UNAVAILABLE aliases or labels near
TRACE_EDGE_ABSENT_MEASUREMENT_UNAVAILABLE, which belongs to the 2026-05-31 predecessor.
```

Closeout records must separate `docs/EXECUTION_CONTRACT.md` state from branch label:

```text
contract_closeout_state = complete | blocked

branch_closeout =
  closed_with_layer4_confirmed_detector_field_map_resealed
  | closed_with_field_map_trace_absent_admitted_artifact
  | closed_with_field_map_ambiguous_admitted_artifact
  | blocked_with_input_artifact_missing
  | blocked_with_admission_manifest_missing
  | blocked_with_schema_inventory_incomplete
  | blocked_with_requirement_mapping_incomplete
  | blocked_with_forbidden_fallback_reached
  | blocked_with_no_count_guard_failed
  | blocked_with_non_mutation_invariant_failed
  | blocked_with_review_gate_failed
  | blocked_with_claim_overreach
```

Success may claim only:

```text
The admitted trace-edge artifact has, lacks, or ambiguously exposes a detector-consumable
field map for LAYER4_ABSORPTION_CONFIRMED.
Count remains not computed.
```

Success must not claim:

```text
LAYER4_ABSORPTION_CONFIRMED current count 산출
live-corpus occurrence count 산출
confirmed count 0
confirmed count 24
zero-occurrence closeout
Layer4 absorption resolved
Layer4 policy redesign
SUSPECT tier coverage
source facts mutation
source decisions mutation
rendered text mutation
runtime Lua mutation
packaged Lua mutation
quality_state mutation
publish_state mutation
runtime_state mutation
Browser / Wiki / Tooltip behavior change
runtime rollout
manual in-game validation pass
deployment
Workshop readiness
B42 readiness
release readiness
ready_for_release
```

---

## 2. Scope

This is a governance-scale docs/static-artifact detector field-map reseal round. It consumes the 2026-05-31 field-map Branch B readpoint and the 2026-06-01 trace-edge authority admission readpoint as immutable predecessors, then seals an additive successor field-map readpoint against the admitted trace-edge artifact.

In scope:

* Read-only intake of the 2026-05-31 corpus lock, 2026-05-31 field-map Branch B, and 2026-06-01 trace-edge authority admission readpoints.
* Read-only intake of `layer4_trace_edges.v1.jsonl`.
* Read-only intake of admission manifest / partition artifacts from the trace-edge authority admission round.
* Admission artifact discovery in this order:
  * primary manifest: `Iris/build/description/v2/staging/compose_contract_migration/layer4_trace_edge_authority_admission_round/trace_edge_admission_manifest.json`
  * primary partition: `Iris/build/description/v2/staging/compose_contract_migration/layer4_trace_edge_authority_admission_round/trace_edge_authority_partition.json`
  * primary report: `Iris/build/description/v2/staging/compose_contract_migration/layer4_trace_edge_authority_admission_round/trace_edge_admission_report.json`
  * secondary closeout read: `Iris/build/description/v2/staging/compose_contract_migration/layer4_trace_edge_authority_admission_round/layer4_trace_edge_authority_admission_closeout.md`
* If the manifest/partition pair is absent and the secondary closeout cannot prove `admission_partition = current_detector_input`, close as `blocked_with_admission_manifest_missing`.
* Verification that the admitted artifact belongs to `current_detector_input`.
* Actual schema and field-path inventory for the admitted artifact.
* Role binding for these four detector roles:
  * `source_object`
  * `target_layer3_row_or_item`
  * `destination_body_slot`
  * `explicit_edge_relation`
* End-to-end traversal check. The core relation is `source_object -> destination_body_slot`; `target_layer3_row_or_item` is the detector row/item identity anchor.

```text
source_object -> explicit_edge_relation -> destination_body_slot
target_layer3_row_or_item = row/item identity anchor for that relation
```

* Forbidden fallback classification and exclusion.
* Ambiguity register for fields that look relevant but cannot be accepted as canonical detector input.
* Canonical field map manifest, or explicit absent/ambiguous closeout manifest.
* Field-map-conditioned readiness dry-run that reads shape and relation only, without counting confirmed occurrences.
* Hard gate, non-mutation check, adversarial review, and gated promotion candidate.
* Additive closeout candidates for `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, and `docs/ROADMAP.md` only after review PASS.
* `accepted Conditional PASS` requires explicit user/operator acceptance before live governance doc promotion.

### Explicitly Out Of Scope

* `LAYER4_ABSORPTION_CONFIRMED` confirmed count measurement.
* Current count or live-corpus occurrence count.
* Confirmed count `0` declaration.
* Generated edge rows `24` promotion to confirmed count.
* Layer4 absorption resolved declaration.
* Layer4 policy redesign.
* 2026-05-31 Branch B rewrite or reopen.
* 2026-06-01 admission seal rewrite or reopen.
* `layer4_trace_edges.v1.jsonl` mutation or regeneration.
* SUSPECT tier coverage expansion.
* Source expansion reopen.
* Structural signal disposition reopen.
* `FUNCTION_NARROW` or `ACQ_DOMINANT` publish review.
* ACQ_DOMINANT remeasurement.
* Runtime Lua regeneration.
* Packaged Lua mutation.
* Browser / Wiki / Tooltip UI change.
* MIGV-QA or in-game validation.
* Deployment / Workshop / B42 / release readiness.
* Public-facing claim creation.
* `quality_baseline_v4` to `v5` cutover.

---

## 3. Non-Goals

This plan does not attempt to:

* Infer detector truth from text similarity, rendered substring, Korean/English keyword, category tag, cluster/provenance label, or same-row co-occurrence.
* Treat artifact row count `24` as a detector count.
* Treat prior corpus candidate field path count `188`, explicit trace-edge field path count `0`, or ambiguous field path count `0` as automatically applicable to the new admitted artifact.
* Treat any detector readiness dry-run pass as measurement completion.
* Promote diagnostic/report-only/historical/test surfaces to current detector input.
* Add missing fields to the admitted artifact in order to make Branch A possible.
* Collapse Branch C ambiguity into Branch A success.
* Collapse Branch B absence into Layer4 resolved or confirmed count `0`.
* Change Iris runtime, Browser, Wiki, Tooltip, rendered text, or user-facing behavior.
* Create repository-wide machine-enforced preflight unless a separate implementation scope explicitly does so.

---

## 4. Assumptions

Authority assumptions:

* `docs/Philosophy.md` is the top authority. Iris remains a 100% Lua wiki-style information module and must not become an interpretation, recommendation, comparison, or gameplay-policy system.
* `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, and `docs/ROADMAP.md` are the current governance readpoints at execution start.
* The 2026-05-31 field-map seal remains an immutable predecessor: current locked corpus lacked explicit Layer4 source object to Layer3 body slot trace-edge field.
* The 2026-06-01 trace-edge authority admission remains an immutable successor readpoint over the prior Branch B: explicit trace-edge was produced as a sidecar and admitted into `current_detector_input`.
* The admitted artifact path is:

```text
Iris/build/description/v2/staging/compose_contract_migration/layer4_trace_edge_authority_admission_round/layer4_trace_edges.v1.jsonl
```

* Admission manifest / partition authority is read in this order:

```text
1. trace_edge_admission_manifest.json + trace_edge_authority_partition.json
2. trace_edge_admission_report.json
3. layer4_trace_edge_authority_admission_closeout.md as secondary supporting evidence only
```

* If 2026-06-01 admission artifacts include a sealed per-file hash for `layer4_trace_edges.v1.jsonl`, this round must assert byte-level equality against that hash before field inventory.
* If no 2026-06-01 per-file hash is available, this round must record an integrity limit: the input artifact is identified by path, predecessor closeout, row count, admission partition, and newly computed hash, but byte-level equality to a prior sealed hash was not assertable.
* Generated edge row count `24` is an artifact shape metric only.
* `confirmed_measurement_executed = false` and `confirmed_count = not_computed` remain true until a separate count measurement round executes.
* A sealed field map is a prerequisite for a future measurement round, not measurement itself.
* Branch A, Branch B, and Branch C are valid fail-loud outcomes if selected by evidence.

Detector assumptions:

* `confirmed` true requires explicit `source_object -> destination_body_slot` relation.
* `source_object`, `target_layer3_row_or_item`, `destination_body_slot`, and `explicit_edge_relation` must each bind to actual fields or JSON paths.
* `target_layer3_row_or_item` is the detector row/item identity anchor, not a substitute for the required source-to-slot relation.
* Source/target/slot co-occurrence is not sufficient without relation semantics.
* Accepted field binding must be deterministic and must not rely on display text.
* Missing required field routes to Branch B or a blocked state, not silent fallback.
* Ambiguous relation direction, target identity, or slot scope routes to Branch C, not forced success.

Template/contract assumptions:

* `docs/PLAN_TEMPLATE.md` is the required plan form for this request.
* `docs/EXECUTION_CONTRACT.md` closeout states are `complete`, `partial`, `implemented_only`, and `blocked`.
* Missing tools or blocked validation commands must be recorded as `blocked` or `not_run`, not `pass`.

Path and determinism assumptions:

```text
repository_root = local run-config only; not sealed artifact content
path_normalization = repo_relative_posix_path
field_path_order = lexical_stable
json_key_order = stable
jsonl_row_order = file_order_then_line_offset
artifact_hashing = sha256
sealed_artifact_paths = repo_relative_posix_path only
```

Absolute paths may be used during local execution logs only when needed to locate files on this machine. They must not be promoted into sealed or canonical artifacts.

---

## 5. Repository Areas Affected

### Code

None expected.

Optional round-local helper scripts may be created only under:

```text
Iris/build/description/v2/staging/compose_contract_migration/layer4_confirmed_detector_field_map_reseal_round/
```

Shared build tools are not planned mutation targets. Any shared tooling change requires explicit scope amendment.

### Docs

Plan artifact:

```text
docs/Iris/iris-dvf-3-3-layer4-confirmed-detector-field-map-reseal-round-plan.md
```

Potential staged docs candidate after hard gate:

```text
Iris/build/description/v2/staging/compose_contract_migration/layer4_confirmed_detector_field_map_reseal_round/docs_addendum_candidate.md
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
Iris/build/description/v2/staging/compose_contract_migration/layer4_confirmed_detector_field_map_reseal_round/
```

Expected generated artifacts:

```text
field_map_reseal_scope_lock.md
field_map_reseal_authority_input_manifest.json
admitted_trace_edge_artifact_inventory.json
admitted_trace_edge_schema_summary.json
detector_requirement_matrix.json
role_field_binding_table.json
source_slot_relation_traversal_report.json
forbidden_fallback_classification.json
forbidden_fallback_exclusion_list.json
ambiguity_register.jsonl
ambiguity_summary.json
canonical_field_map_manifest.json
field_map_reseal_branch_determination.md
field_map_conditioned_readiness_dry_run_report.json
no_count_guard_evidence.json
non_mutation_hash_report.json
adversarial_review_report.md
field_map_reseal_closeout.md
artifact_hash_manifest.json
docs_addendum_candidate.md
```

Conditional generated artifacts:

```text
trace_absent_admitted_artifact_rationale.md
  condition = branch_closeout == closed_with_field_map_trace_absent_admitted_artifact

field_map_ambiguous_admitted_artifact_rationale.md
  condition = branch_closeout == closed_with_field_map_ambiguous_admitted_artifact
```

---

## 6. Planned Changes

### Change 1 - Scope Lock / Readpoint Intake

Purpose:

Prevent the reseal round from drifting into count measurement, runtime mutation, or predecessor rewrite.

Files:

```text
field_map_reseal_scope_lock.md
field_map_reseal_authority_input_manifest.json
```

Implementation Notes:

* Record predecessor readpoints and branch names.
* Record the admitted trace-edge artifact path and admission partition.
* Record admission manifest / partition source path, using the discovery order defined in Scope.
* Record the admitted artifact hash.
* Assert equality with the 2026-06-01 sealed per-file hash if available; otherwise record the integrity limit explicitly.
* Record that prior Branch B is not count `0`.
* Record that generated edge rows `24` is not confirmed count.
* Record `count_generation_allowed = false`.
* Record `runtime_mutation_allowed = false`.
* Record `publish_review_opened = false`.

Validation:

* Authority input manifest JSON parse pass.
* Required predecessor readpoints present.
* Primary input path present or explicit blocked reason recorded.
* Admission manifest / partition present, or secondary closeout support recorded, or `blocked_with_admission_manifest_missing`.
* Hash equality asserted if predecessor per-file hash exists; integrity limit recorded if it does not.
* Count-generation flag is false.
* Non-claim checklist present.

---

### Change 2 - Admitted Artifact Schema / Field Inventory

Purpose:

Inventory the actual schema and field paths of `layer4_trace_edges.v1.jsonl` without interpretation or fallback.

Files:

```text
admitted_trace_edge_artifact_inventory.json
admitted_trace_edge_schema_summary.json
artifact_hash_manifest.json
```

Implementation Notes:

* Parse every JSONL row in the admitted artifact.
* Confirm row count as artifact shape metric only.
* Enumerate top-level and nested field paths.
* Record null, missing, empty string, empty array, and malformed values separately.
* Record field cardinality and per-row consistency.
* Do not inherit old corpus field counts from the 2026-05-31 Branch B round.

Validation:

* JSONL parse pass.
* Stable field path enumeration.
* Artifact hash recorded.
* Predecessor sealed hash equality recorded, or predecessor-hash-unavailable integrity limit recorded.
* Row count recorded as shape metric only.
* No detector count output exists.

---

### Change 3 - Detector Requirement Matrix / Role Binding

Purpose:

Bind the four required detector roles to actual fields or JSON paths in the admitted artifact.

Files:

```text
detector_requirement_matrix.json
role_field_binding_table.json
source_slot_relation_traversal_report.json
```

Implementation Notes:

* Required role bindings:

| Requirement | Required Meaning | Accepted Field | Rejected/Fallback Field | Disposition |
|---|---|---|---|---|
| `source_object` | Layer4 source object identity | actual field path | provenance/category only | sealed/absent/ambiguous |
| `target_layer3_row_or_item` | Layer3 row/item identity anchor | actual field path | display text only | sealed/absent/ambiguous |
| `destination_body_slot` | Layer3 destination body slot | actual field path | rendered substring/report section only | sealed/absent/ambiguous |
| `explicit_edge_relation` | source -> destination slot trace relation | actual field path | co-occurrence only | sealed/absent/ambiguous |

* Confirm `source_object -> destination_body_slot` explicit relation.
* Use `target_layer3_row_or_item` only as the row/item identity anchor for that relation.
* If traversal coverage returns `24` rows, record it only as admitted edge row traversal coverage, not confirmed occurrence total.
* If multiple plausible fields conflict, route to ambiguity rather than selecting by convenience.
* If relation direction cannot be established, route to Branch C.
* If a required field is absent, route to Branch B or a blocked state depending on evidence.

Validation:

* Each required role has exactly one accepted field or explicit absent/ambiguous disposition.
* Accepted relation field proves source-to-slot direction, not co-occurrence.
* Traversal report exists.
* Any traversal aggregate is labeled non-count coverage.
* Requirement matrix and binding table agree.

---

### Change 4 - Forbidden Fallback Re-Separation

Purpose:

Prevent non-authority fields from becoming detector input when the admitted artifact appears incomplete or ambiguous.

Files:

```text
forbidden_fallback_classification.json
forbidden_fallback_exclusion_list.json
```

Implementation Notes:

Rejected fallback classes:

```text
rendered_body_substring
item_display_text
korean_or_english_keyword
category_tag
cluster_label
provenance_label_only
source_target_co_occurrence_only
diagnostic_report_only_field
historical_predecessor_count
row_count_itself
predecessor_detector_readiness_dry_run_pass
field_map_conditioned_readiness_dry_run_pass_as_edge_truth
```

* Record each rejected fallback with role, field path, and reason.
* Ensure no rejected fallback is used in accepted role bindings.
* Preserve diagnostic/report-only surfaces as audit context only.
* This does not forbid using the round-local dry-run as a shape/readiness gate after independent field binding. It forbids using any dry-run pass as evidence that an edge is true.

Validation:

* Fallback accepted count `0`.
* Every rejected fallback has a reason.
* No accepted role binding references forbidden fallback classes.

---

### Change 5 - Ambiguity Register / Candidate Separation

Purpose:

Separate fields that are present but not canonical enough for detector input.

Files:

```text
ambiguity_register.jsonl
ambiguity_summary.json
```

Implementation Notes:

Ambiguity classes:

```text
AMBIGUOUS_SOURCE_OBJECT
AMBIGUOUS_TARGET_IDENTITY
AMBIGUOUS_SLOT_SCOPE
AMBIGUOUS_EDGE_RELATION
AMBIGUOUS_RELATION_DIRECTION
FORBIDDEN_FALLBACK_ONLY
```

* Ambiguous fields must not be temporarily accepted.
* Target identity ambiguity must not become duplicate count or skip logic in this round.
* Slot scope ambiguity must not be resolved through rendered section names.

Validation:

* Ambiguous accepted count `0`.
* Ambiguity reason present for every ambiguous candidate.
* Branch C remains available if any required role is ambiguous.

---

### Change 6 - Canonical Field Map Reseal Draft

Purpose:

If Branch A is available, produce the canonical field map manifest for future count measurement.

Files:

```text
canonical_field_map_manifest.json
field_map_reseal_branch_determination.md
```

Implementation Notes:

Canonical field map manifest includes:

```text
input_artifact_path
input_artifact_hash
input_artifact_partition
field_map_version
source_object_field
target_layer3_row_or_item_field
destination_body_slot_field
explicit_edge_relation_field
forbidden_fallback_list
ambiguity_disposition
measurement_enabled = false
confirmed_measurement_executed = false
confirmed_count = not_computed
```

* Initial `field_map_version = field_map.v1`.
* `field_map_version` is independent from the trace-edge artifact version in `layer4_trace_edges.v1.jsonl`.
* Branch A requires all four roles sealed.
* Branch B requires one or more required trace fields absent.
* Branch C requires one or more role fields present but semantically ambiguous.

Validation:

* Manifest JSON parse pass.
* Field map references only accepted fields.
* Fallback accepted count `0`.
* Ambiguity accepted count `0`.
* Count remains `not_computed`.

---

### Change 7 - Field-Map-Conditioned Readiness Dry-Run / Hard Gate

Purpose:

Verify that the detector can read the sealed field map, or fail loud on absent/ambiguous state, without executing measurement.

Files:

```text
field_map_conditioned_readiness_dry_run_report.json
no_count_guard_evidence.json
non_mutation_hash_report.json
adversarial_review_report.md
```

Implementation Notes:

* This dry-run is distinct from the 2026-06-01 trace-edge admission dry-run.
* The 2026-06-01 dry-run is an admitted partition executability signal.
* This round-local dry-run is a field-map-conditioned shape/readiness gate after role binding.
* Dry-run pass must not be used as edge-truth fallback.
* Parse the admitted artifact through the proposed field map.
* Check tuple shape only.
* Check missing required field behavior.
* For Branch B, field-map-conditioned dry-run may close as `fail_loud_absent` or `not_applicable` rather than `pass`.
* Check fallback path is not accessed.
* Check ambiguous row/field is not accepted.
* Run adversarial review before any canonical doc promotion.
* Hard gate must separate readiness from measurement.

Validation:

* Field-map-conditioned dry-run output parse pass.
* `confirmed_measurement_executed = false`.
* `confirmed_count = not_computed`.
* Fallback access count `0`.
* Ambiguous accepted count `0`.
* Required-field missing behavior fail-loud.
* Branch B absent/not_applicable dry-run disposition is accepted only when the branch determination is absence, not FIELD_MAP_SEALED.
* Determinism pass.
* Non-mutation hash diff pass for source/rendered/runtime/state surfaces included in the ceiling.
* Review gate PASS, or accepted Conditional PASS with explicit user/operator acceptance.

---

### Change 8 - Branch Closeout / Gated Promotion Candidate

Purpose:

Close the round as Branch A, Branch B, or Branch C and prepare additive canonical-document updates only after gates pass.

Files:

```text
field_map_reseal_closeout.md
docs_addendum_candidate.md
```

Implementation Notes:

Branch decision rules:

| Condition | Branch closeout |
|---|---|
| all four role bindings sealed, traversal pass, no fallback, no ambiguity, field-map-conditioned dry-run pass | `closed_with_layer4_confirmed_detector_field_map_resealed` |
| required trace field absent in admitted artifact, fallback rejected, count not computed | `closed_with_field_map_trace_absent_admitted_artifact` |
| relevant fields present but relation direction, target identity, or slot scope ambiguous | `closed_with_field_map_ambiguous_admitted_artifact` |
| input/admission/schema/gate missing | specific `blocked_with_*` branch |

* Branch B is a definitive absence determination for the admitted artifact, so `contract_closeout_state = complete` is allowed within the stated ceiling.
* Branch C is evidence-bounded but cannot seal a canonical detector field map, so `contract_closeout_state = blocked`.
* Add dated DECISIONS closeout candidate.
* Add ARCHITECTURE compact evidence capsule candidate.
* Add ROADMAP state update candidate.
* Do not edit live canonical docs before review gate.
* Accepted Conditional PASS is not self-accepting; it requires explicit user/operator acceptance before live governance doc promotion.
* Do not rewrite 2026-05-31 or 2026-06-01 predecessor entries.

Validation:

* Branch label matches manifest and closeout.
* Non-claim checklist present.
* Validation ceiling present.
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
primary input artifact exists
primary input artifact hash recorded
predecessor sealed per-file hash equality asserted, or predecessor-hash-unavailable integrity limit recorded
admission partition check = current_detector_input
admission manifest source path recorded
schema field inventory completeness check
detector requirement matrix parse/check
role binding table parse/check
source_object -> destination_body_slot explicit relation traversal check
target_layer3_row_or_item identity anchor check
traversal aggregate non-count labeling check
forbidden fallback negative-control check
ambiguity separation check
canonical field map manifest validation
branch determination / manifest consistency check
field-map-conditioned dry-run parse/shape validation
no-count guard check
determinism check
artifact hash manifest validation
non-mutation hash diff
review gate check
claim ceiling check
```

Optional repo validation only if touched surface requires it:

```powershell
python -B -m unittest discover -s Iris\build\description\v2\tests -p "test_*.py"
powershell -ExecutionPolicy Bypass -File .\tools\check_lua_syntax.ps1
```

These optional commands may be claimed as passed only if the exact command exits with code `0`.

Optional validation status must be recorded with one of:

```text
not_required
not_run
blocked_missing_tool
pass
fail
```

Minimum non-mutation hash targets:

```text
Iris/build/description/v2/data/dvf_3_3_facts.jsonl
Iris/build/description/v2/data/dvf_3_3_decisions.jsonl
Iris/build/description/v2/output/dvf_3_3_rendered.json
Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks/*.lua
Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks.lua
Iris/media/lua/client/Iris/Data/IrisLayer3Data.lua
Iris/build/description/v2/staging/compose_contract_migration/layer4_trace_edge_authority_admission_round/layer4_trace_edges.v1.jsonl
```

If any path is absent, the validation report must record `absent_expected`, `absent_unexpected`, or `not_applicable` rather than silently dropping it.

### Manual Validation

* Review that this is field-map reseal only and not count measurement.
* Review that `layer4_trace_edges.v1.jsonl` row count `24` is not used as confirmed count.
* Review that any `24 traversable` or equivalent traversal coverage metric is not used as confirmed count.
* Review that the 2026-06-01 admission dry-run and this round's field-map-conditioned dry-run are not conflated.
* Review admitted artifact hash equality if a predecessor sealed hash exists, or the explicit integrity limit if it does not.
* Review admission manifest / partition source path and fallback to closeout evidence if primary manifests are absent.
* Review role binding for source object, target row/item, destination body slot, and explicit relation.
* Review that source/target/slot co-occurrence is not accepted as explicit edge.
* Review forbidden fallback classification.
* Review ambiguity register.
* Review Branch A/B/C selection.
* Review non-claim list and validation ceiling.
* Review any docs addendum candidate for additive-only wording.

### Validation Limits

This execution will not perform:

* no confirmed count measurement
* no live-corpus occurrence count
* no runtime validation
* no in-game / MIGV-QA validation
* no multiplayer validation
* no deployment validation
* no long-session runtime validation
* no release validation
* no public-facing behavior validation
* no tooltip validation
* no Workshop readiness validation
* no B42 readiness validation
* no external ecosystem compatibility sweep

---

## 8. Risk Surface Touch

### Authority Surface

Touched by the future execution. The round seals detector-consumable field-map authority over an already admitted trace-edge artifact. It does not create source facts authority, decisions authority, rendered text authority, runtime authority, publish writer authority, or default compose authority.

The field-map reseal artifact is the single writer for this round's detector field-map authority. Later corrections must be additive successor/supersession rounds, not rewrites of the sealed field-map artifact.

### Runtime Behavior Surface

None intended. Runtime Lua, packaged Lua, Browser, Wiki, Tooltip, item selection, rendered text, and player-facing behavior remain unchanged.

### Compatibility Surface

Low / internal tooling only. Future measurement rounds may consume the sealed manifest, but external mod/runtime compatibility surfaces are not touched.

### Sealed Artifact Surface

Touched additively. The round may create a new field-map reseal artifact. Existing 2026-05-31 and 2026-06-01 sealed readpoints are consumed read-only.

Sealed artifacts must use repository-relative POSIX paths. Absolute local paths may appear only in local run logs or run config, not promoted sealed artifacts.

### Public-Facing Output Surface

None intended. No item description, tooltip copy, wiki behavior, README public claim, Workshop status, release note, or B42 readiness claim is opened.

---

## 9. Risk Analysis

### Architecture Risk

* The new field map could be mistaken for a count measurement.
* The admitted sidecar could be mistaken for a new structural axis rather than measurement support.
* Branch B could be overclaimed as confirmed count `0`.
* Branch A could be overclaimed as Layer4 resolved.
* Ambiguous relation direction could be forced into an accepted mapping.
* Diagnostic/report-only fields could be promoted to detector authority.
* Branch vocabulary could collide with predecessor labels if non-canonical aliases are reintroduced.
* Field-map single-writer ownership could blur if later artifacts rewrite the manifest instead of superseding it.

### Runtime Risk

* Expected runtime risk is none if scope is respected.
* A validation helper could accidentally regenerate rendered/runtime surfaces.
* Any side-effect mutation must block non-mutation closeout until identified and corrected.
* Absolute local paths could leak into sealed artifacts if run-config output is promoted without filtering.

### Compatibility Risk

* Future count tooling could rely on an overly narrow field map.
* Future count tooling could undercount or overcount if target identity or slot scope is ambiguous.
* Public wording could imply compatibility preservation without a compatibility sweep.

### Regression Risk

* JSONL schema may be inconsistent across the 24 edge rows.
* Field names may appear obvious but encode weaker semantics than detector requires.
* Dry-run readiness could be read as measurement validity.
* The 2026-06-01 admission dry-run could be conflated with this round's field-map-conditioned dry-run.
* Old corpus counts could accidentally be copied into the new artifact readpoint.
* Traversal coverage could produce a count-like `24` aggregate and contaminate no-count claims.
* Admitted artifact hash equality may be unavailable if the predecessor did not seal a per-file hash.
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
Iris/build/description/v2/staging/compose_contract_migration/layer4_confirmed_detector_field_map_reseal_round/
```

3. If optional helper scripts were created and are invalid, remove or quarantine only those round-local helper scripts.

4. If shared tooling was changed without explicit scope amendment, stop and revert only changes made by this round after identifying them.

5. If `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, or `docs/ROADMAP.md` receive invalid additive wording, correct with additive clarification when possible. If duplicate text was added by this round, remove only that duplicate addition.

6. If source facts, source decisions, rendered text, runtime Lua, packaged Lua, bridge payload, `quality_state`, `publish_state`, or `runtime_state` changed unexpectedly, stop and identify the exact source of mutation before reverting only this round's changes.

7. If dry-run outputs any confirmed count, discard the dry-run output and rerun a field-map-only dry-run.

8. If Branch A later proves ambiguous, supersede the field-map reseal with a successor correction round rather than rewriting the sealed closeout body.

9. If predecessor-colliding aliases or `*_MEASUREMENT_UNAVAILABLE` labels are reintroduced, reject the closeout vocabulary and restore the canonical branch labels before sealing.

10. If an absolute local path appears in a promoted artifact, replace it with a repository-relative POSIX path or keep it only in local run-config evidence.

---

## 11. Governance Constraints

* `docs/Philosophy.md` compliance is mandatory.
* Iris remains wiki/fact-oriented and must not introduce interpretation, recommendation, or comparison.
* Hub & Spoke and SPI boundaries remain untouched.
* Runtime/build-time separation must remain intact.
* The 2026-05-31 field-map Branch B seal remains an immutable predecessor.
* The 2026-06-01 trace-edge authority admission seal remains an immutable predecessor.
* `layer4_trace_edges.v1.jsonl` is consumed read-only.
* Admission manifest / partition must be read from the declared admission-round artifacts, with closeout text as secondary support only.
* If a predecessor per-file hash exists, admitted artifact hash equality is mandatory before field inventory.
* Field-map reseal is additive successor authority only.
* Field-map reseal has single-writer ownership in `canonical_field_map_manifest.json`; later changes are additive successor/supersession only, never direct rewrite.
* Branch closeout vocabulary must not reuse or approximate predecessor `TRACE_EDGE_ABSENT_MEASUREMENT_UNAVAILABLE`.
* `field_map_version` starts at `field_map.v1` and is independent from `layer4_trace_edges.v1.jsonl`.
* Sealed artifacts use repository-relative POSIX paths only.
* Generated edge row count `24` must not be read as confirmed count.
* Any traversal coverage aggregate, including `24`, must not be read as confirmed count.
* The 2026-06-01 detector readiness dry-run pass must not be read as this round's field-map seal.
* This round's field-map-conditioned dry-run pass must not be read as edge-truth evidence or measurement completion.
* Text similarity, keyword, rendered substring, category tag, cluster/provenance label, and source/target co-occurrence-only fallback are forbidden.
* Historical, diagnostic, report-only, preview-only, staging residue, and test fixture surfaces must not be promoted to current detector input.
* Missing required fields must fail loud or route to Branch B / blocked closeout.
* Ambiguous fields must route to Branch C / blocked closeout and must not be forced into Branch A.
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
closed_with_layer4_confirmed_detector_field_map_resealed
closed_with_field_map_trace_absent_admitted_artifact
```

Branch B is allowed as `complete` because it is a definitive admitted-artifact absence determination within the stated validation ceiling, not a count or resolved-state claim.

`blocked` is valid for:

```text
closed_with_field_map_ambiguous_admitted_artifact
blocked_with_input_artifact_missing
blocked_with_admission_manifest_missing
blocked_with_schema_inventory_incomplete
blocked_with_requirement_mapping_incomplete
blocked_with_forbidden_fallback_reached
blocked_with_no_count_guard_failed
blocked_with_non_mutation_invariant_failed
blocked_with_review_gate_failed
blocked_with_claim_overreach
```

Branch C remains `blocked` because ambiguity may be evidence-bounded and documented, but it cannot seal a canonical detector field map.

`partial` and `implemented_only` are not planned sealed success states for this field-map reseal round.

Complete success may claim only:

```text
The admitted trace-edge artifact has a sealed detector field map for the four required roles,
and field-map-conditioned readiness dry-run passed without count execution.
```

Complete negative seal may claim only:

```text
The admitted trace-edge artifact lacks one or more required canonical detector fields,
fallback paths were rejected, field-map-conditioned dry-run closed as fail_loud_absent
or not_applicable rather than pass, and confirmed measurement remains not executed.
```

Blocked closeout may claim only:

```text
The admitted trace-edge artifact is not valid enough to seal a detector field map,
or validation/review/non-mutation gates did not permit closeout.
No detector count was executed.
```

Expected final non-claims:

```text
LAYER4_ABSORPTION_CONFIRMED current count 산출 아님
live-corpus occurrence count 산출 아님
confirmed count 0 선언 아님
confirmed count 24 선언 아님
zero-occurrence closeout 아님
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
runtime rollout 아님
manual in-game validation pass 아님
deployment 아님
Workshop readiness 아님
B42 readiness 아님
release readiness 아님
ready_for_release 아님
repository-wide machine-enforced preflight 아님
```

Next round opening condition:

```text
Confirmed count measurement may open only after Branch A FIELD_MAP_SEALED,
with no-count guard evidence preserved and a separate measurement scope lock.
```
