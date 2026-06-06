# Iris DVF 3-3 Layer4 Trace-Edge Authority Admission Round Plan

> 상태: Draft v0.3-pass-minor-applied
> 기준일: 2026-06-01
> 상위 기준: `docs/Philosophy.md`, `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`
> authority input: `Layer4 Trace-Edge Authority & Corpus Admission Seal - Integrated Roadmap` (2026-06-01 user-provided synthesis)
> review input: `REVIEW - Iris DVF 3-3 Layer4 Trace-Edge Authority Admission Round Plan` (2026-06-01 user-provided synthesis). v0.1 WARN review Critical C1-C3 and that review's R1-R9 revision set incorporated in v0.2. v0.2 PASS-with-minor-revisions review Critical/Major 0 and R1-R7 polish incorporated in v0.3.
> 직접 상위 readpoint:
> - 2026-04-29 Layer4 Absorption Policy Round predecessor zero-count: historical only, no current count inheritance
> - 2026-05-31 Layer4 Boundary Current Corpus Lock Round `closed_with_layer4_boundary_current_corpus_locked_no_count_inheritance_design_preflight`
> - 2026-05-31 Layer4 Confirmed Detector Field Map Seal Round `closed_with_confirmed_measurement_unavailable_trace_absent`
> 계획 형식: `docs/PLAN_TEMPLATE.md`
> template attestation: this plan follows the 1-12 section structure in `docs/PLAN_TEMPLATE.md`.
> execution_scale: `governance`
> scope_qualifier: `trace_edge_authority_admission_only`
> execution_entry_condition: execution-ready after v0.3 spot-check; Critical/Major `0`
> template_contract_verify_status: `docs/PLAN_TEMPLATE.md` and `docs/EXECUTION_CONTRACT.md` checked in-session for structure and closeout-state vocabulary
> 실행 상태: planning authority only. This document opens no `LAYER4_ABSORPTION_CONFIRMED` count, runtime mutation, publish mutation review, deployment, release, or closeout claim.

---

## 1. Objective

이번 execution plan의 목적은 `LAYER4_ABSORPTION_CONFIRMED` confirmed detector가 요구하는 explicit row-level trace-edge authority를 회수하거나, 조건부로 생산하거나, 회수/생산 불가 상태를 명시적으로 봉인하는 것이다.

이번 라운드의 최대 claim은 다음으로 제한한다.

```text
Layer4 source object -> Layer3 body slot explicit trace-edge authority의
회수 가능성, 생산 여부, schema, admission manifest state, detector-readiness boundary가 봉인되었다.
Confirmed count 산출은 별도 후속 measurement round의 범위다.
```

이번 라운드가 답해야 하는 질문은 다음이다.

```text
1. 기존 build/body_plan/compose trace에 detector가 소비할 수 있는 explicit trace-edge authority가 있는가?
2. 없다면 같은 라운드에서 별도 row-level sidecar artifact production을 열 것인가, 아니면 별도 opening으로 defer할 것인가?
3. 회수 또는 생산된 trace artifact는 current detector input으로 admission 가능한가?
4. detector는 admitted artifact를 count 없이 dry-run으로 읽을 수 있는가?
```

Round id:

```text
layer4_trace_edge_authority_admission_round
```

Round-local artifact root:

```text
Iris/build/description/v2/staging/compose_contract_migration/layer4_trace_edge_authority_admission_round/
```

Required minimum trace-edge fields:

```text
row_id
item_full_type
source_ref
source_cardinality
destination_ref
destination_slot
edge_type
edge_basis
```

Per-row trace-edge records own relation identity only. `authority_class`, `admission_state`, and detector input partition are owned only by Change 4 admission manifest / partition artifacts. Edge rows must not be rewritten by downstream admission.

Confirmed detector accepted edge type:

```text
edge_type = placed_in_body_output
```

Allowed `edge_basis` enum:

```text
recovered_body_plan_relation_trace
recovered_compose_relation_trace
generated_body_plan_relation_trace
generated_compose_relation_trace
```

Forbidden `edge_basis` values or substitutes:

```text
text_similarity
expression_match
rendered_substring_only
cluster_label
provenance_label
row_co_occurrence
body_slot_hint_only
source_object_hint_only
diagnostic_report_label
historical_reference_only
preview_or_fixture_only
```

Terminal branch taxonomy:

```text
complete_success:
  EDGE_AUTHORITY_RECOVERED_AND_ADMITTED
  EDGE_AUTHORITY_PRODUCED_AND_ADMITTED

complete_negative_seal:
  EDGE_AUTHORITY_UNRECOVERABLE_NO_ARTIFACT_PRODUCED
  closed_rejected_non_authority_trace_candidates

blocked:
  blocked_trace_edge_authority_unavailable_no_detector_count
  blocked_trace_edge_schema_invalid
  blocked_trace_edge_referential_integrity_failed
  blocked_trace_edge_provenance_failed
  blocked_trace_edge_admission_rejected
  blocked_detector_readiness_failed
  blocked_production_approval_missing
  blocked_no_count_guard_failed
  blocked_non_mutation_invariant_failed
  blocked_claim_overreach
```

Closeout records must separate `docs/EXECUTION_CONTRACT.md` state from branch label:

```text
contract_closeout_state = complete | blocked

branch_closeout =
  EDGE_AUTHORITY_RECOVERED_AND_ADMITTED
  | EDGE_AUTHORITY_PRODUCED_AND_ADMITTED
  | EDGE_AUTHORITY_UNRECOVERABLE_NO_ARTIFACT_PRODUCED
  | closed_rejected_non_authority_trace_candidates
  | blocked_trace_edge_authority_unavailable_no_detector_count
  | blocked_trace_edge_schema_invalid
  | blocked_trace_edge_referential_integrity_failed
  | blocked_trace_edge_provenance_failed
  | blocked_trace_edge_admission_rejected
  | blocked_detector_readiness_failed
  | blocked_production_approval_missing
  | blocked_no_count_guard_failed
  | blocked_non_mutation_invariant_failed
  | blocked_claim_overreach
```

---

## 2. Scope

이 계획의 범위는 `LAYER4_ABSORPTION_CONFIRMED` 후속 measurement를 열기 위한 prerequisite authority/admission seal이다.

포함 범위:

* current locked corpus와 Field Map Seal Branch B를 predecessor readpoint로 재확인한다.
* 기존 build/body_plan/compose trace에서 explicit trace-edge authority를 recovery discovery한다.
* recovery 후보를 `explicit_trace_edge`, `body_slot_hint_only`, `source_object_hint_only`, `co_occurrence_only`, `label_or_provenance_only`, `diagnostic_only`, `historical_only`, `rejected_non_edge`로 분류한다.
* recovery/production branch 전에 `layer4_trace_edge.v1` schema와 explicit-edge referential-integrity gate를 공통으로 봉인한다.
* recovery 가능 시 recovered trace edge를 공통 schema/minimum requirement에 맞춰 정규화한다.
* recovery 불가 시 same-round production 여부를 별도 decision gate로 남긴다.
* production이 명시 승인된 경우에만 row-level trace-edge sidecar artifact를 build-time/offline side-output으로 생성한다.
* 회수 또는 생산된 artifact를 authority partition과 admission manifest로 current detector input에 연결한다.
* detector readiness dry-run은 schema/readability/admission 검증까지만 수행하고 count를 산출하지 않는다.
* closeout은 trace-edge authority/admission 상태와 후속 count round prerequisite만 기록한다.

### Explicitly Out Of Scope

* `LAYER4_ABSORPTION_CONFIRMED` current count 산출
* live-corpus occurrence count 산출
* confirmed count `0` 선언
* zero-occurrence closeout
* Layer4 absorption resolved 선언
* SUSPECT tier 재개방 또는 coverage 확장
* Layer4 policy redesign
* current locked corpus 4개 path의 rewrite
* source facts / decisions / rendered text mutation
* runtime Lua regeneration 또는 packaged Lua mutation
* Browser / Wiki / Tooltip behavior 변경
* publish mutation review 개방
* runtime rollout / deployment / release readiness 주장
* machine-enforced preflight 구현
* `FUNCTION_NARROW` second rollout
* `ACQ_DOMINANT` 재측정
* `active/silent` and `adopted/unadopted` vocabulary 재정의

---

## 3. Non-Goals

이 계획은 다음을 해결하려 하지 않는다.

* Layer4 absorption 정책 자체의 재설계
* confirmed detector의 의미 확장
* 텍스트 유사도, 표현 감지, cluster/provenance label, source/target co-occurrence 기반 detector 작성
* body-slot hint를 confirmed trace로 승격
* historical / diagnostic / report-only / preview-only / staging residue / test fixture surface 전체를 current measurement corpus로 승격
* trace-edge artifact row count를 confirmed count처럼 해석
* Iris runtime Lua에 JSON parser 또는 detector authority 추가
* default compose authority 자체 변경
* source-row writer, runtime writer, publish writer authority 변경

---

## 4. Assumptions

* `docs/Philosophy.md`가 최상위 authority이며, Iris는 해석·권장·비교를 하지 않는다.
* `docs/PLAN_TEMPLATE.md` is the canonical implementation-plan template for this workspace under the active AGENTS.md instruction.
* `docs/EXECUTION_CONTRACT.md` closeout states are `complete`, `partial`, `implemented_only`, and `blocked`.
* `Layer4 Boundary Current Corpus Lock Round`는 current measurement corpus 4개 path와 excluded surface classes를 봉인한 상태다.
* `current_locked_corpus_paths` are manifest-confirmed from `Iris/build/description/v2/staging/compose_contract_migration/layer4_boundary_current_corpus_lock_round/layer4_boundary_current_corpus_manifest.json` `included_surfaces[].path` and match the four-path current readpoint:

```text
Iris/build/description/v2/data/dvf_3_3_facts.jsonl
Iris/build/description/v2/output/dvf_3_3_rendered.json
Iris/build/description/v2/staging/body_role/phase2/layer3_role_check_overlay.jsonl
Iris/build/description/v2/tools/style/rules/structural_rules.json
```

* current locked corpus manifest sha256 `d394f95f5f2a157679238e005a90929349eb807a8180824d8f0ed30240290402`는 predecessor readpoint로 유지한다.
* `Layer4 Confirmed Detector Field Map Seal Round`는 explicit trace-edge field path count `0`, ambiguous field path count `0`, downstream count disposition `not_applicable_under_current_corpus`로 닫혔다.
* 위 Field Map Seal closeout은 count `0`이 아니라 `TRACE_EDGE_ABSENT_MEASUREMENT_UNAVAILABLE`이다.
* current Layer 3 production pipeline은 `facts -> decisions -> compose -> normalizer -> style linter -> rendered -> Lua bridge`로 읽는다.
* default compose authority는 `compose_profiles_v2.json + body_plan`이며, runtime Lua는 render-only다.
* trace-edge 회수/생산 위치는 runtime이 아니라 build/body_plan/compose side 또는 staging artifact다.
* 새 trace artifact가 필요하더라도 current corpus 자체를 재정의하지 않고 detector auxiliary authority 또는 trace-edge authority partition으로 admission한다.
* sidecar production은 recovery failure 후 자동으로 열리지 않는다. Phase 2 decision gate에서 명시 승인되거나 별도 라운드로 defer되어야 한다.
* `item_full_type` is resolved from locked corpus row identity, not from rendered text substring or inferred display text.
* Field Map Seal Branch B readiness-state 전이는 predecessor rewrite가 아니라 additive successor readpoint로만 기록한다.

---

## 5. Repository Areas Affected

### Code

Conditional only. Recovery-only branch에서는 code mutation이 없어야 한다.

* `Iris/build/description/v2/tools/build/`
* `Iris/build/description/v2/tools/`
* `Iris/build/description/v2/tests/`

Potential code touch is limited to trace-edge discovery, schema validation, sidecar emission, admission validation, and detector readiness dry-run tooling. Runtime Lua code is excluded.

### Docs

* `docs/Iris/iris-dvf-3-3-layer4-trace-edge-authority-admission-round-plan.md`
* `docs/DECISIONS.md` (closeout addendum candidate only)
* `docs/ROADMAP.md` (closeout addendum candidate only)
* `docs/ARCHITECTURE.md` (compact ledger candidate only)

### Config

None expected by default.

Conditional if tooling requires explicit path/schema config:

* `Iris/build/description/v2/config/`
* `Iris/build/description/v2/tools/build/*.json`

### Generated Artifacts

All generated artifacts stay under:

```text
Iris/build/description/v2/staging/compose_contract_migration/layer4_trace_edge_authority_admission_round/
```

Expected or conditional artifacts:

* `layer4_trace_edge_authority_scope_manifest.json`
* `trace_edge_recovery_audit.json`
* `trace_edge_candidate_fields.jsonl`
* `trace_edge_recovery_classification_summary.json`
* `trace_edge_branch_decision.json`
* `trace_edge_branch_decision_table.json`
* `recovered_trace_edges.v1.jsonl`
* `layer4_trace_edge.schema.json`
* `layer4_trace_edge_schema_seal_report.json`
* `trace_edge_referential_integrity_contract.json`
* `trace_edge_referential_integrity_report.json`
* `trace_edge_recovered_referential_integrity_appendix.json`
* `trace_edge_generated_referential_integrity_appendix.json`
* `trace_edge_provenance_report.json`
* `trace_edge_reject_reason_contract.md`
* `layer4_trace_edges.v1.jsonl`
* `layer4_trace_edge_generation_report.json`
* `layer4_trace_edge_determinism_report.json`
* `non_mutation_hash_report.json`
* `trace_edge_admission_manifest.json`
* `trace_edge_authority_partition.json`
* `trace_edge_admission_report.json`
* `trace_edge_rejected_candidates.jsonl`
* `confirmed_detector_trace_edge_readiness_dry_run.json`
* `confirmed_detector_readiness_summary.md`
* `fallback_path_guard_report.json`
* `layer4_trace_edge_authority_admission_closeout.md`

Artifact ownership rule:

```text
trace_edge_recovery_classification_summary.json = Change 2 only
recovered_trace_edges.v1.jsonl = Change 3A only
trace_edge_referential_integrity_contract.json = Change 3 only
trace_edge_referential_integrity_report.json = Change 3 aggregate/index only
trace_edge_recovered_referential_integrity_appendix.json = Change 3A only
trace_edge_generated_referential_integrity_appendix.json = Change 3B only
```

---

## 6. Planned Changes

### Change 1 - Scope Re-Seal / Round Ceiling Lock

Purpose:

This change seals the round as trace-edge authority/admission work only. It prevents count execution, runtime mutation, publish mutation review, and Layer4 resolved claims from entering the round.

Files:

* `layer4_trace_edge_authority_scope_manifest.json`
* `layer4_trace_edge_authority_admission_closeout.md` preamble

Implementation Notes:

* Record predecessor readpoints for 2026-04-29 Layer4 policy, 2026-05-31 corpus lock, and 2026-05-31 field-map seal.
* Pin current locked corpus membership and `d394...` predecessor manifest hash.
* Record `current_locked_corpus_paths` as:
  * `Iris/build/description/v2/data/dvf_3_3_facts.jsonl`
  * `Iris/build/description/v2/output/dvf_3_3_rendered.json`
  * `Iris/build/description/v2/staging/body_role/phase2/layer3_role_check_overlay.jsonl`
  * `Iris/build/description/v2/tools/style/rules/structural_rules.json`
* Record `current_locked_corpus_paths_manifest_confirmation = confirmed`.
* Declare `count_generation_allowed = false`.
* Declare `runtime_mutation_allowed = false`.
* Declare `publish_review_opened = false`.
* Declare `round_goal = trace_edge_authority_and_admission_only`.
* Record that prior zero-count is historical-only and not inherited.

Validation:

* Scope manifest JSON parse pass.
* Required predecessor fields present.
* `current_locked_corpus_paths` count is `4` and matches the predecessor corpus lock readpoint.
* `current_locked_corpus_paths` string equality check passes against `layer4_boundary_current_corpus_manifest.json` `included_surfaces[].path`.
* No-count and non-mutation flags are explicitly false/forbidden.
* Claim ceiling check passes before later phases run.

---

### Change 2 - Existing Trace Recovery Discovery / Decision Gate

Purpose:

This change determines whether existing build/body_plan/compose trace surfaces already contain detector-consumable explicit trace-edge authority.

Files:

* `trace_edge_recovery_audit.json`
* `trace_edge_candidate_fields.jsonl`
* `trace_edge_recovery_classification_summary.json`
* `trace_edge_branch_decision.json`

Implementation Notes:

* Inventory candidate fields from body_plan trace, compose trace, structural overlay, rendered generation trace, source coverage trace, and related build-time current-authority surfaces.
* Change 2 owns `trace_edge_recovery_classification_summary.json`; later changes may consume it but must not rewrite it.
* Classify every candidate into one of:
  * `explicit_trace_edge`
  * `body_slot_hint_only`
  * `source_object_hint_only`
  * `co_occurrence_only`
  * `label_or_provenance_only`
  * `diagnostic_only`
  * `historical_only`
  * `rejected_non_edge`
* For every candidate, record availability of relation fields only at this stage: `row_id`, `item_full_type`, `source_ref`, `source_cardinality`, `destination_ref`, `destination_slot`, `edge_type`, and `edge_basis`.
* Treat body-slot hints, source labels, cluster/provenance, same-row co-occurrence, and text similarity as non-edge unless automated referential-integrity validation can prove direct source -> destination relation.
* Do not write `authority_class` or `admission_state` into candidate or edge rows. These are owned by Change 4 manifests.
* Record a decision gate:
  * `RECOVERABLE`
  * `NOT_RECOVERABLE_PRODUCTION_APPROVED`
  * `NOT_RECOVERABLE_PRODUCTION_DEFERRED`
  * `BLOCKED_AUTHORITY_UNAVAILABLE`
* `trace_edge_branch_decision.json` must include:

```text
production_approval_basis
approved_by_plan = true | false
approved_by_successor_instruction = true | false
reason
generation_time_relation_evidence
```

* `NOT_RECOVERABLE_PRODUCTION_APPROVED` requires `generation_time_relation_evidence` to be present. If it is absent, the branch must be `NOT_RECOVERABLE_PRODUCTION_DEFERRED` or `BLOCKED_AUTHORITY_UNAVAILABLE`.
* This plan does not grant blanket production approval. `approved_by_plan = true` is valid only when the common schema is sealed, generation-time relation evidence is present, and non-mutation guard targets are pinned before production.

Validation:

* Candidate field classification completeness `100%`.
* Unknown/unclassified candidate count `0`.
* Every rejected candidate has a reject reason.
* `explicit_trace_edge` candidates pass automated source/destination/slot referential-integrity validation and include a row-level source -> destination relation, not inferred co-occurrence.
* Forbidden `edge_basis` candidates fail loud.
* Decision gate is exactly one of the allowed branch decisions.

---

### Change 3 - Common Trace-Edge Schema / Referential-Integrity Seal

Purpose:

This change seals the single authoritative `layer4_trace_edge.v1` schema and automated explicit-edge validation before either recovery normalization or net-new production may complete.

Files:

* `layer4_trace_edge.schema.json`
* `layer4_trace_edge_schema_seal_report.json`
* `trace_edge_referential_integrity_contract.json`
* `trace_edge_referential_integrity_report.json`
* `trace_edge_reject_reason_contract.md`

Implementation Notes:

* `layer4_trace_edge.v1` is written by this common step only. Recovery and production branches consume this schema and must not define branch-local variants.
* Change 3 owns the referential-integrity contract and aggregate/index report. Branch-specific execution evidence goes to branch appendices, not to the common contract artifact.
* Require relation identity fields only: `row_id`, `item_full_type`, `source_ref`, `source_cardinality`, `destination_ref`, `destination_slot`, `edge_type`, and `edge_basis`.
* Do not include `authority_class` or `admission_state` in the required row schema. Admission/classification is decided only by Change 4 manifest/partition artifacts.
* Seal `edge_type = placed_in_body_output` as the confirmed detector accepted edge.
* Seal the allowed `edge_basis` enum as:

```text
recovered_body_plan_relation_trace
recovered_compose_relation_trace
generated_body_plan_relation_trace
generated_compose_relation_trace
```

* Seal the forbidden basis/substitute list as:

```text
text_similarity
expression_match
rendered_substring_only
cluster_label
provenance_label
row_co_occurrence
body_slot_hint_only
source_object_hint_only
diagnostic_report_label
historical_reference_only
preview_or_fixture_only
```

* Add automated referential-integrity checks:
  * `row_id` resolves to a row in the current locked corpus.
  * `item_full_type` matches the locked corpus row identity.
  * `source_ref` resolves to a Layer4 source object or stable source-object reference in current body_plan/compose authority.
  * `destination_ref` resolves to the same locked corpus row identity or an explicitly linked destination row.
  * `destination_slot` resolves to a known Layer3 body slot enum or sealed body slot identifier, not a rendered substring.
  * `destination_slot_enum_source` or `sealed_slot_identifier_source` is recorded in `trace_edge_referential_integrity_report.json`.
  * `edge_type` and `edge_basis` together prove direct source -> destination relation, not co-occurrence.
* Make malformed edges fail-loud.
* Keep `destination_slot` stable and reject rendered-substring-only references.
* Keep aggregate or multi-source edges explicit through `source_cardinality`.

Validation:

* Schema validation pass.
* Required relation field missing count `0` for accepted edge rows.
* Unknown enum count `0`.
* `edge_basis` allowed enum validation pass.
* Forbidden basis fail-loud validation pass.
* `source_ref`, `destination_ref`, and `destination_slot` referential-integrity validation pass.
* Malformed sample fails loud.
* Source/rendered/runtime/state non-mutation hash diff `delta 0`.

---

### Change 3A - Recovered Edge Authority Normalization Against Common Schema

Purpose:

If existing trace-edge authority is recoverable, this change normalizes recovered edges against the common sealed schema without creating a branch-local schema or writing admission/class state into edge rows.

Files:

* `recovered_trace_edges.v1.jsonl`
* `trace_edge_recovered_referential_integrity_appendix.json`

Implementation Notes:

* Consume the common `layer4_trace_edge.v1` schema from Change 3.
* Consume `trace_edge_recovery_classification_summary.json` from Change 2 without rewriting it.
* Normalize recovered explicit trace edges into relation-only row records.
* Do not write `authority_class`, `admission_state`, or detector input partition into recovered edge rows.
* Preserve `source_cardinality` for aggregate or multi-source edges rather than flattening them into a false single-source relation.
* If any recovered edge fails schema or referential-integrity validation, it is rejected or the branch is blocked; it is not silently downgraded into detector input.

Validation:

* Recovered edge JSONL parse pass.
* Common schema validation pass.
* Referential-integrity validation pass.
* Edge artifact contains no `authority_class` or `admission_state` fields.
* Source/rendered/runtime/state non-mutation hash diff `delta 0`.

---

### Change 3B - Conditional Net-New Trace-Edge Artifact Production

Purpose:

If existing trace recovery fails and same-round production is explicitly approved, this change produces a separate row-level trace-edge sidecar artifact without changing source, rendered, runtime, or publish surfaces.

Files:

* `layer4_trace_edges.v1.jsonl`
* `trace_edge_generated_referential_integrity_appendix.json`
* `layer4_trace_edge_generation_report.json`
* `layer4_trace_edge_determinism_report.json`
* `non_mutation_hash_report.json`
* observer-only emission contract in closeout or report

Implementation Notes:

* This branch can run only after Change 3 seals the common `layer4_trace_edge.v1` schema.
* This branch consumes the common schema and must not define a branch-local schema.
* `trace_edge_branch_decision.json` must show production approval basis:

```text
production_approval_basis
approved_by_plan = true | false
approved_by_successor_instruction = true | false
reason
generation_time_relation_evidence
```

* `generation_time_relation_evidence` is required. If no generation-time relation evidence exists, same-round production must be deferred or blocked.
* Producer location is build-time/offline only, preferably immediately after body_plan/compose generation where source and destination relation is known.
* Runtime Lua consumer, rendered text reverse parser, and text similarity detector are forbidden.
* Sidecar artifact is a side-output and must not alter body text, rendered text, Lua payload, source facts, decisions, `quality_state`, `publish_state`, or `runtime_state`.
* Sidecar edge rows contain relation fields only and must not contain `authority_class`, `admission_state`, or detector input partition.
* Source object inference is forbidden. Edges must be emitted only from explicit generation-time relation data.
* `generated_edge_count` is an artifact shape metric only and must not be reported as confirmed count.
* After production, the edge artifact is immutable input to Change 4. Admission must not rewrite the edge artifact.
* If production cannot satisfy observer-only emission, this branch must close as blocked or defer production.

Validation:

* JSONL parse pass.
* Schema validation pass.
* `edge_basis` allowed enum validation pass.
* Source/destination/slot referential-integrity validation pass.
* Two-run determinism pass.
* Compose emission on/off byte-identical check.
* Source/rendered/runtime/state non-mutation hash diff `delta 0`.
* Edge artifact post-production non-mutation hash diff `delta 0` across Change 4/5.
* Row identity consistency check.
* `confirmed_count` absent or `not_computed`.

---

### Change 3C - Recovery-Blocked / Production-Deferred Closeout

Purpose:

If recovery is impossible and same-round production is not approved, this change records the blocked/deferred state as a first-class closeout rather than silently treating absence as resolved.

Files:

* `trace_edge_branch_decision.json`
* `layer4_trace_edge_authority_admission_closeout.md`
* production-deferred handoff note

Implementation Notes:

* Use `EDGE_AUTHORITY_UNRECOVERABLE_NO_ARTIFACT_PRODUCED` when recovery is not possible and production is deferred.
* Use `blocked_trace_edge_authority_unavailable_no_detector_count` when authority/admission cannot be established and no complete negative seal is justified.
* Record `confirmed_measurement_executed = false`.
* Record `confirmed_count = not_computed`.
* Define the next opening condition for sidecar production or measurement.

Validation:

* Branch decision parse pass.
* Missing trace-edge authority reason present.
* No count output exists.
* Next opening condition present.
* Non-claim checklist present.

---

### Change 4 - Authority Classification / Corpus Admission Seal

Purpose:

This change decides whether recovered or produced trace artifacts can be consumed as current detector input and records partition/admission boundaries.

Files:

* `trace_edge_admission_manifest.json`
* `trace_edge_authority_partition.json`
* `trace_edge_admission_report.json`
* `trace_edge_rejected_candidates.jsonl`

Implementation Notes:

* Change 4 is the single owner of `authority_class`, `admission_state`, and detector input partition.
* Change 4 must not mutate recovered or produced edge artifact rows. It writes only manifest/partition/report artifacts.
* Partition artifacts into:
  * `current_detector_input`
  * `current_supporting_trace_only`
  * `diagnostic_only`
  * `historical_only`
  * `rejected_non_edge`
* `current_supporting_trace_only` means the artifact may support audit/review of the round but is not a detector input and cannot be consumed by count measurement.
* Admit an artifact only when:
  * it is linked to current locked corpus row identity,
  * it derives from current compose/body_plan authority,
  * it satisfies `layer4_trace_edge.v1`,
  * it is not diagnostic/historical/staging-only,
  * it has hash recorded in the manifest,
  * its admission scope is trace-edge authority only,
  * source/rendered/runtime/state mutation is absent.
* `derives from current compose/body_plan authority` requires all of the following:
  * the source surface exists in current checkout,
  * the source surface is consumed by current default compose/body_plan generation or is a direct side-output from that generation,
  * the source surface is not historical, report-only, preview-only, diagnostic-only, staging residue, or test fixture by primary purpose,
  * any dual-role path records its focal role and predecessor rationale,
  * provenance is recorded in `trace_edge_provenance_report.json`.
* Authority provenance failures are fail-loud and close as `blocked_trace_edge_provenance_failed` unless the candidate is explicitly partitioned as supporting-only or rejected.
* Do not rewrite the 2026-05-31 corpus lock. This admission is additive successor authority.
* Field Map Seal Branch B remains a predecessor readpoint. Any readiness-state transition is an additive successor, not a rewrite of the Branch B closeout.

Validation:

* Admission manifest parse pass.
* Admitted artifact unknown count `0`.
* Rejected artifact has reject reason `100%`.
* `current_detector_input` artifact hash recorded.
* Supporting-only artifact is absent from detector input path.
* Admission manifest is the only location containing `authority_class`, `admission_state`, and detector input partition.
* Edge artifact hash after admission matches edge artifact hash before admission.
* Current-authority provenance validation pass.
* Manifest includes `count_allowed = false`.
* Predecessor `d394...` readpoint remains unchanged.

---

### Change 5 - Detector Readiness Dry-Run

Purpose:

This change confirms that the detector can read admitted trace-edge authority without executing confirmed measurement or producing a count.

Files:

* `confirmed_detector_trace_edge_readiness_dry_run.json`
* `confirmed_detector_readiness_summary.md`
* `fallback_path_guard_report.json`

Implementation Notes:

* Dry-run checks schema compatibility, required field coverage, admission manifest state, rejected reason classes, missing field behavior, referential-integrity readability, and fail-loud behavior.
* `confirmed_detector_readiness_summary.md` may claim only schema/admission/readability readiness. It must not claim measurement validity, occurrence count, or Layer4 resolved state.
* Output must include `confirmed_measurement_executed = false`.
* Output must include `confirmed_count = not_computed` or omit `confirmed_count` entirely with an explicit non-count explanation.
* Text similarity, co-occurrence, keyword, body text substring, cluster/provenance, and diagnostic/report-only fallback paths must not run.
* Missing required fields must fail loud rather than silently skip.

Validation:

* Dry-run output parse pass.
* `confirmed_measurement_executed = false`.
* `confirmed_count = not_computed` or no count field by contract.
* Fallback detector path not reached.
* Missing required field fail-loud test passes.
* Referential-integrity failure path fails loud.
* Admitted edge schema read success or blocked reason recorded.

---

### Change 6 - Closeout / Canonical Absorption Candidate

Purpose:

This change records the round outcome and prepares addendum-only canonical absorption candidates without opening count, runtime, or release claims.

Files:

* `layer4_trace_edge_authority_admission_closeout.md`
* `docs/DECISIONS.md` addendum candidate
* `docs/ROADMAP.md` addendum candidate
* `docs/ARCHITECTURE.md` compact ledger candidate
* next-round handoff note

Implementation Notes:

* Select one terminal branch.
* Branch selection precedence:

```text
Evaluate blocked conditions first.
Select success or negative-seal branches only after schema, referential-integrity,
provenance, admission, dry-run, no-count, non-mutation, and claim-ceiling
preconditions required by that branch have passed or are explicitly not applicable.
```

* Apply this deterministic branch decision table:

| Recovery / production gate | Admission result | Dry-run result | Branch closeout |
|---|---|---|---|
| `RECOVERABLE` | admitted as `current_detector_input` | pass | `EDGE_AUTHORITY_RECOVERED_AND_ADMITTED` |
| `NOT_RECOVERABLE_PRODUCTION_APPROVED` with generation-time relation evidence | admitted as `current_detector_input` | pass | `EDGE_AUTHORITY_PRODUCED_AND_ADMITTED` |
| all inspected candidates are non-edge or non-authority | no detector input; all candidates rejected with reasons | not run or not applicable | `closed_rejected_non_authority_trace_candidates` |
| `NOT_RECOVERABLE_PRODUCTION_DEFERRED` | no artifact produced | not run | `EDGE_AUTHORITY_UNRECOVERABLE_NO_ARTIFACT_PRODUCED` |
| `BLOCKED_AUTHORITY_UNAVAILABLE` | no valid authority | not run | `blocked_trace_edge_authority_unavailable_no_detector_count` |
| any gate | schema invalid | not run | `blocked_trace_edge_schema_invalid` |
| any gate | referential-integrity failed | not run | `blocked_trace_edge_referential_integrity_failed` |
| any gate | provenance failed | not run | `blocked_trace_edge_provenance_failed` |
| production requested without approval/evidence | not applicable | not run | `blocked_production_approval_missing` |
| admitted as `current_detector_input` | admitted | fail | `blocked_detector_readiness_failed` |
| any gate | no-count guard failed | any | `blocked_no_count_guard_failed` |
| any gate | non-mutation invariant failed | any | `blocked_non_mutation_invariant_failed` |
| any gate | claim ceiling exceeded | any | `blocked_claim_overreach` |

* Record all validation gates and validation limits.
* Explicitly separate trace-edge authority/admission from confirmed count measurement.
* State that a confirmed count measurement round may open only after admitted trace-edge authority exists.
* If no admitted authority exists, record production or recovery reopening prerequisites.
* Keep docs canonical absorption additive. Do not rewrite predecessor closeouts.
* `docs/DECISIONS.md`, `docs/ROADMAP.md`, and `docs/ARCHITECTURE.md` entries listed by this plan are staging addendum candidates until an execution explicitly edits those canonical docs after validation.

Validation:

* Closeout report parse/readability check.
* Branch decision table determinism validation pass.
* Explicit non-claims present.
* `all_gates_pass = true` only if every named gate passes.
* Claim boundary does not exceed trace-edge authority/admission.
* Docs addendum candidates do not assert runtime/source/rendered/state mutation.

---

## 7. Validation Plan

### Automated Validation

Required validation for any execution branch:

* JSON parse for generated `.json` artifacts.
* JSONL parse for generated `.jsonl` artifacts.
* `layer4_trace_edge.v1` schema validation.
* `edge_basis` allowed enum validation.
* Forbidden basis fail-loud validation.
* `source_ref` referential-integrity validation.
* `destination_ref` referential-integrity validation.
* `destination_slot` body-slot enum or sealed slot identifier validation.
* Candidate classification completeness check.
* Reject reason completeness check.
* Current compose/body_plan authority provenance validation.
* Admission manifest validation.
* Admission/class single-owner validation:
  * edge rows contain no `authority_class`
  * edge rows contain no `admission_state`
  * admission manifest owns `authority_class`, `admission_state`, and detector partition
* Artifact hash manifest validation.
* Two-run determinism check for inventory/classification/admission outputs.
* Terminal branch decision determinism validation.
* No-count guard:
  * `confirmed_measurement_executed = false`
  * `confirmed_count = not_computed` or absent by contract
  * no live-corpus occurrence count output
* Fallback guard proving no text similarity, co-occurrence, keyword, body substring, cluster/provenance, or diagnostic-only fallback was used as confirmed evidence.
* Source/rendered/runtime/state non-mutation hash diff.
* Edge artifact post-production non-mutation hash diff across admission and dry-run.

Minimum `non_mutation_hash_targets`:

```text
source facts current input files
source decisions current input files, if present in the inspected current compose/body_plan authority surface
Iris/build/description/v2/output/dvf_3_3_rendered.json
runtime Lua chunks / runtime Lua manifest
package-facing Lua if present
quality_state carrier files if present
publish_state carrier files if present
runtime_state carrier files if present
edge artifact after production or recovery normalization
```

Conditional validation if code/tooling changes are made:

* `python -B -m unittest discover -s Iris\build\description\v2\tests -p "test_*.py"`
* Any round-local validation script introduced for schema/admission/dry-run.
* Lua syntax check only if Lua files are touched; expected scope is no Lua touch.

### Manual Validation

* Backstop review that every accepted trace edge has explicit source -> destination relation after automated validation has passed.
* Review that body-slot hints and source labels are not promoted to accepted edges.
* Review that `generated_edge_count`, if present, is described only as artifact shape metric.
* Review that dry-run output does not contain a count surrogate.
* Review closeout branch against the branch taxonomy.
* Review addendum candidates for claim overreach.

### Validation Limits

This plan does not validate:

* `LAYER4_ABSORPTION_CONFIRMED` current count.
* live-corpus occurrence count.
* Layer4 absorption resolved state.
* SUSPECT tier coverage.
* multiplayer behavior.
* deployment.
* long-session runtime.
* manual in-game behavior.
* external mod compatibility sweep.
* public-facing Browser / Wiki / Tooltip behavior.
* release readiness.
* packaged Lua runtime rollout.
* full runtime equivalence.
* full compatibility preservation.

---

## 8. Risk Surface Touch

### Authority Surface

Touched.

This round creates, recovers, rejects, or admits trace-edge authority that a future `LAYER4_ABSORPTION_CONFIRMED` detector may consume. It does not create source facts authority, decisions authority, rendered text authority, runtime authority, publish writer authority, or default compose authority.

### Runtime Behavior Surface

None intended.

Runtime Lua, chunked Lua, Browser, Wiki, Tooltip, item selection, rendered text, and player-facing behavior must remain unchanged.

### Compatibility Surface

Tooling-level only.

Build artifact schema, staging validation, detector readiness dry-run, and future measurement prerequisites may be affected. External mod/runtime compatibility surfaces are not touched.

### Sealed Artifact Surface

Touched additively.

Existing sealed artifacts are predecessor readpoints and must not be rewritten. New staging artifacts and closeout artifacts may become successor authority only after validation and canonical absorption.

Field Map Seal Branch B remains a predecessor readiness-state. This round may create an additive successor readpoint only; it must not rewrite or reinterpret Branch B as count `0`.

### Public-Facing Output Surface

None.

No public description, UI copy, tooltip copy, wiki behavior, release note, Workshop claim, or B42 readiness claim is opened by this plan.

---

## 9. Risk Analysis

### Architecture Risk

* Recovery lane and production lane could be mixed without explicit decision gate.
* A sidecar artifact could be misread as a new structural axis instead of measurement support.
* Current corpus lock could be implicitly reopened by admitting too broad an artifact universe.
* Trace-edge admission could accidentally bypass single-writer authority.
* Schema ownership could diverge if recovery and production define branch-local schema variants.
* Admission/class ownership could blur if edge rows carry manifest-owned fields.

### Runtime Risk

* A production implementation could accidentally mutate rendered/runtime payloads while emitting sidecar trace.
* Detector readiness dry-run could drift into actual measurement.
* Runtime Lua could be pulled into authority parsing, violating render-only boundary.

### Compatibility Risk

* Diagnostic, historical, preview, staging, or test fixture artifacts could be promoted to current detector input.
* Build tooling schema changes could break existing staging validation if not isolated.
* Aggregate or multi-source relations could be flattened incorrectly and produce misleading future detector input.
* Current compose/body_plan authority provenance could be under-specified, causing valid trace rejection or non-authority trace admission.

### Regression Risk

* `confirmed_count = 0` could be inferred from absence of admitted authority.
* `generated_edge_count` could be reported as a confirmed measurement.
* Dry-run readiness could be read as measurement validity rather than schema/admission/readability readiness.
* Reject reasons could be incomplete, making future blocked states hard to audit.
* Canonical docs could overclaim readiness, resolved state, runtime deployment, or release readiness.

---

## 10. Rollback Plan

Before canonical absorption, rollback is staging-only:

* Delete or quarantine invalid staging artifacts under the round-local artifact root.
* Remove invalid admission manifest entries.
* Reclassify ambiguous accepted edges as `current_supporting_trace_only` or `rejected_non_edge`.
* If sidecar production mutates source/rendered/runtime/state surfaces, revert those changes and close the branch as blocked.
* If dry-run produces counts, discard dry-run output and fix the dry-run contract before rerun.
* If schema is too loose, discard `layer4_trace_edge.v1` and reseal in the same round only if no downstream canonical absorption occurred.
* If schema is fundamentally wrong after canonical absorption, do not rewrite the prior closeout. Open a successor round that marks the prior schema obsolete/superseded.
* If docs overclaim count/resolved/release readiness, correct the addendum before closeout or open a successor correction if already absorbed.
* Default conservative closeout is `blocked_trace_edge_authority_unavailable_no_detector_count`.

---

## 11. Governance Constraints

The following constraints must remain preserved during execution:

* `docs/Philosophy.md` compliance.
* Hub & Spoke boundary preservation.
* Iris remains wiki/fact-oriented and does not introduce interpretation, recommendation, or comparison.
* Source / Evidence / Description / Runtime layer separation.
* build-time authority and runtime render-only boundary.
* single-writer authority preservation.
* current locked corpus is not rewritten.
* 2026-04-29 Layer4 zero-count is historical-only and not inherited as current count.
* `LAYER4_ABSORPTION_CONFIRMED` confirmed evidence requires explicit row-level trace-edge.
* Explicit edge validation must be automated through source/destination/slot referential integrity, with manual review only as backstop.
* `edge_basis` must come from the allowed enum; forbidden basis values must fail loud.
* Body-slot hint, target row co-occurrence, cluster/provenance label, text similarity, and expression detection are not confirmed edges.
* Edge rows own relation identity only; `authority_class`, `admission_state`, and detector input partition are owned by admission manifest/partition artifacts.
* Edge artifacts are immutable after recovery normalization or production.
* Runtime Lua, packaged Lua, Browser/Wiki/Tooltip behavior, `quality_state`, `publish_state`, and `runtime_state` remain unchanged.
* Count 산출 금지.
* Malformed or minimum-requirement-missing edge records fail loud.
* Historical / diagnostic / report-only / preview-only / staging residue / test fixture surfaces are not promoted wholesale to current measurement corpus.
* Layer4 trace-edge remains a decision-namespace/measurement lane and is not reinterpreted as structural axis.
* Additive amendment preference; predecessor closeouts are not rewritten.
* Minimal diff preservation.

---

## 12. Expected Closeout State

Expected closeout target:

```text
complete or blocked
```

`complete` is valid only for one of these terminal states:

```text
EDGE_AUTHORITY_RECOVERED_AND_ADMITTED
EDGE_AUTHORITY_PRODUCED_AND_ADMITTED
EDGE_AUTHORITY_UNRECOVERABLE_NO_ARTIFACT_PRODUCED
closed_rejected_non_authority_trace_candidates
```

`blocked` is valid for:

```text
blocked_trace_edge_authority_unavailable_no_detector_count
blocked_trace_edge_schema_invalid
blocked_trace_edge_referential_integrity_failed
blocked_trace_edge_provenance_failed
blocked_trace_edge_admission_rejected
blocked_detector_readiness_failed
blocked_production_approval_missing
blocked_no_count_guard_failed
blocked_non_mutation_invariant_failed
blocked_claim_overreach
```

`partial` and `implemented_only` are not planned sealed success states for this round.

Complete success may claim only:

```text
Explicit trace-edge authority was recovered and admitted, or produced and admitted,
using the common sealed schema and manifest-owned admission/class state,
and detector readiness was dry-run verified without count execution.
```

Complete negative seal may claim only:

```text
Existing trace-edge authority is unrecoverable within the inspected surfaces, no same-round artifact was produced,
or candidates were rejected as non-authority trace candidates. Confirmed measurement remains not executed.
```

Blocked closeout may claim only:

```text
Trace-edge authority/admission prerequisite is not available or not valid enough to open count measurement.
No detector count was executed.
```

Expected final non-claims:

```text
LAYER4_ABSORPTION_CONFIRMED current count 산출 아님
live-corpus occurrence count 산출 아님
confirmed count 0 선언 아님
zero-occurrence closeout 아님
Layer4 absorption resolved 아님
Layer4 policy redesign 아님
SUSPECT tier coverage 아님
FUNCTION_NARROW second rollout 아님
ACQ_DOMINANT 재측정 아님
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
Confirmed count measurement may open only after an admitted trace-edge authority artifact exists
and detector readiness dry-run has passed without count execution or fallback evidence.
```
