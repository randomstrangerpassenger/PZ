# Implementation Plan

> Status: planned / roadmap-derived / codebase-inspected / WARN feedback incorporated / Cycle 2 PASS minor revisions incorporated / owner decision capture clarified / DVF 3-3 completion vocabulary and external gate vocabulary split / governance-only
> 작성일: 2026-06-27
> Roadmap input: `C:/Users/MW/.codex/attachments/fd5eb05f-451c-4cc6-b0ee-ff6ae1bb5535/pasted-text.txt` / sha256 `D0E056B67A448C4DBC4F422017D51F6F32A18C20223E4FA4C5A9239468527399` / lines `694`
> Review input: `C:/Users/MW/.codex/attachments/3cc137cf-1a29-451f-a057-6ccd3951db6b/pasted-text.txt` / sha256 `C542110F0AFBCD8DEC09DB8DF032F70370566DEE6623B49FE85A019C4EBF67CA` / lines `438` / WARN revisions incorporated
> Review input: `C:/Users/MW/.codex/attachments/68315d45-6a66-4c15-96ae-3e8f5c449c19/pasted-text.txt` / sha256 `68690237A04738A3C3C11778A8C0DE7166F18D0F91CEC28E622F9F2D37C416E1` / lines `305` / PASS minor revisions incorporated
> Template input: `docs/PLAN_TEMPLATE.md` / sha256 `38D70D4D624733DB4D24F047E0B737A47C75522A967C84F06FE5AABC5EBD9BA1`
> Top authority: `docs/Philosophy.md`
> Current ecosystem readpoints: `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`
> Direct plan artifact: `docs/dvf_3_3_completion_vocabulary_external_gate_vocabulary_split_plan.md`
> Evidence root target: `Iris/build/description/v2/staging/dvf_3_3_completion_vocabulary_external_gate_vocabulary_split/`

---

## 1. Objective

DVF 3-3 current governance chain에서 `PASS`가 machine validation, external validation bundle, independent review, owner decision, owner seal, external gate, canonical external review state를 동시에 표현하는 문제를 분리한다.

이 계획의 목적은 `PASS`를 검증 predicate 결과에만 남기고, human / governance state는 별도 vocabulary로 봉인하는 것이다. 현재 코드베이스에는 이미 broad completion word를 axis-qualified하는 `docs/completion_vocabulary_separation_policy.md`가 있지만, 그 정책은 `PASS`의 owner / review / external gate 축 분리를 충분히 강제하지 않는다. 따라서 이번 라운드는 기존 completion policy의 하위 governance split으로 동작한다.

최대 claim은 다음으로 제한한다.

```text
DVF 3-3 current governance vocabulary is split by axis.
Machine validation PASS, external validation bundle result, independent review verdict,
owner decision, owner seal, external gate state, and canonical external review state
are represented by separate fields.
Self-generated machine PASS cannot satisfy independent review or external gate closure.
This is governance-only and does not mutate source, rendered, Lua bridge, runtime chunks,
package payload, release readiness, manual QA, semantic quality, or public-facing text.
```

완료 후에도 `PASS`는 다음 축에만 허용한다.

* `machine_contract_validation=PASS|FAIL`
* `external_validation_bundle_result=PASS|FAIL|null`
* `independent_review_verdict=PASS|FAIL|PASS_WITH_NOTES|null`

다음 축에는 bare `PASS`를 금지한다.

* `owner_decision=approved|rejected|pending`
* `owner_seal_state=sealed|pending|blocked`
* `external_gate_state=satisfied|blocked|pending`
* `canonical_external_review_state=satisfied|blocked`

`PASS_WITH_NOTES`는 machine validation 값이 아니다. Independent review verdict로만 허용하며, blocking note가 없고 review artifact contract가 모두 충족될 때만 external gate `satisfied` 후보가 된다.

Cycle 2 review의 plan-level verdict는 `PASS with minor revisions`로 읽는다. 이 verdict는 implementation 진입 가능성에 대한 계획 품질 판정이며, independent-review gate satisfaction, canonical external review satisfaction, canonical seal allowance를 의미하지 않는다. Upstream roadmap author가 작성한 검토는 구조적으로 independent-review hard gate를 닫지 못하므로, genuine non-Claude independent review artifact, owner-supplied owner decision / owner seal record, required external validation bundle, and required author-reserved sign-offs가 모두 충족되기 전까지 `canonical_external_review_state=blocked`와 `canonical_seal_allowed=false`를 유지한다.

Owner decision은 external artifact가 아니다. Project owner의 명시적 입력이 owner decision이며, tooling이 해야 할 일은 그 입력을 `owner_supplied` provenance가 있는 machine-readable governance record로 전사하고 scope / readpoint / hash binding을 검증하는 것이다. 이 축의 실패 위험은 구조적 외부 의존성이 아니라 capture / transcription / scope-binding risk로 취급한다. 반대로 independent review와 external validation bundle은 owner decision으로 대체할 수 없는 별도 gate 축이다.

---

## 2. Scope

이 계획은 DVF 3-3 governance vocabulary, current artifact schema, validators, focused tests, current-route required-validation manifest adoption을 다룬다.

포함 범위:

* current governance artifact의 `PASS` / legacy token inventory
* legacy token semantic classification
* 7축 canonical vocabulary schema 작성
* scope별 gate requirement matrix 작성
* owner decision / owner seal / independent review / external gate / canonical external review state 분리
* independent review artifact minimum contract 작성
* `PASS_WITH_NOTES` note severity / blocking schema 작성
* owner approval이 review를 대체하지 못하게 하는 substitution guard 작성
* self-generated report가 external / independent gate completion을 선언하지 못하게 하는 writer identity guard 작성
* roadmap author / upstream governance-chain artifact author independence guard 작성
* current artifact vocabulary migration
* historical artifact vocabulary preservation
* current / historical mode discriminator 작성
* sealed governance evidence hash preservation guard 작성
* fail-closed validator와 negative fixture matrix 작성
* live `Iris/_docs/round3/current_route_required_validations.json` additive adoption
* protected source / rendered / Lua bridge / runtime / package no-mutation report 작성
* final claim boundary와 ledger packet 작성
* retained legacy check / relocated current artifact dual-field relocation invariant 작성
* `absence_maps_to` enum을 `blocked|pending`으로 제한
* upstream governance-chain artifact author membership rule 작성
* reviewer identity normalization rule 작성
* `gate_requirement_by_scope` scope_id naming 고정
* legacy projection cleanup debt와 separate owner-approved cleanup plan requirement 기록
* token rename / split author sign-off tracking
* owner-supplied decision / seal capture contract 작성
* 본 라운드 자체의 self-application: genuine independent review와 owner-supplied owner seal record 전에는 `canonical_external_review_state=blocked`로 기록

Primary execution evidence root:

* `Iris/build/description/v2/staging/dvf_3_3_completion_vocabulary_external_gate_vocabulary_split/`

Direct documentation artifacts:

* `docs/dvf_3_3_completion_vocabulary_external_gate_vocabulary_split_plan.md`
* `docs/dvf_3_3_completion_vocabulary_external_gate_vocabulary_split_policy.md`
* `docs/dvf_3_3_completion_vocabulary_external_gate_vocabulary_split_claim_boundary.md`
* `docs/dvf_3_3_completion_vocabulary_external_gate_vocabulary_split_ledger_packet.md`

Related policy surface:

* `docs/completion_vocabulary_separation_policy.md`

`docs/completion_vocabulary_separation_policy.md`는 broad completion word policy로 유지한다. 이 라운드에서 수정이 필요하면 새 axis split policy를 가리키는 pointer / addendum 수준으로만 수정하고, 두 문서가 서로 다른 claim-boundary authority가 되지 않게 한다.

### Explicitly Out Of Scope

* runtime payload 수정
* source facts / decisions / overlay 수정
* rendered output regeneration
* Lua bridge export
* runtime chunk replacement
* package payload mutation
* current authority cutover
* live migration execution
* release / package / Workshop / B42 / deployment readiness 선언
* manual in-game QA
* semantic quality completion
* public-facing text acceptance
* historical closeout artifact retroactive rewrite
* 모든 과거 `PASS` 문자열 제거
* actual external reviewer 선정 또는 review 수행 자체
* independent review content quality 자동 판단
* full clean-checkout required-evidence reproducibility 봉인
* full historical byte reproducibility
* terminal disposition / denominator / sealed population 재계산
* broad current open-state reconciliation across all historical records
* legacy required-validation check 수정 / retire / removal
* blocked 또는 partial closeout을 canonical complete ledger update로 기록하는 것
* token rename / split author sign-off 없이 final canonical closeout으로 닫는 것
* unrelated refactor

---

## 3. Non-Goals

이 계획은 다음을 해결하지 않는다.

* `PASS`를 프로젝트 전체에서 금지하지 않는다. Machine predicate result에는 계속 허용한다.
* historical evidence의 기존 `owner_seal_status=PASS`, `independent_review_status=PASS`, `external_review_complete=true`, `blocked_external_gate=false`를 소급 수정하지 않는다.
* sealed historical record가 무효라는 주장을 하지 않는다.
* current-route required-validation manifest adoption을 runtime writer 또는 source writer로 승격하지 않는다.
* external validation bundle `PASS`를 independent review artifact로 대체하지 않는다.
* owner approval 또는 owner seal을 independent review verdict로 대체하지 않는다.
* `canonical_external_review_state=satisfied`를 machine validation alone으로 닫지 않는다.
* self-generated tool report를 independent review report로 materialize하지 않는다.
* REVIEW_TEMPLATE 자체를 rewrite하지 않는다. 필요하면 verdict mapping policy에서 `PASS / WARN / FAIL`을 새 review vocabulary로 투영한다.
* `WARN` review verdict를 자동으로 `PASS_WITH_NOTES` 또는 satisfied 후보로 승격하지 않는다.
* `pending`을 `canonical_external_review_state` 값으로 허용하지 않는다. Pending evidence는 `external_gate_state` 또는 axis-local state로만 남긴다.
* `not_required`를 gate 우회로로 쓰지 않는다. Scope별 requirement matrix에 없는 absence는 blocked로 처리한다.
* plan-level PASS를 independent-review gate satisfied 또는 canonical seal allowed로 해석하지 않는다.
* legacy projection cleanup은 이 라운드에서 실행하지 않는다. cleanup은 별도 owner-approved plan 없이는 수행하지 않는다.

---

## 4. Assumptions

* `docs/Philosophy.md`가 최상위 설계 authority다.
* `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`의 current readpoint를 따른다.
* `docs/EXECUTION_CONTRACT.md`는 execution disclosure / evidence / closeout discipline 기준이다.
* Iris는 100% Lua runtime 모드이며, 이 계획은 runtime Lua 동작이 아니라 offline build / governance tooling만 다룬다.
* `Iris/_docs/round3/current_route_required_validations.json`은 schema `round3-current-route-required-validations-v1`의 live required-validation manifest다.
* `Iris/_docs/round3/round3_run_contract_tests.py`는 current route 실행 시 taxonomy test set과 live required manifest의 required tests를 union으로 실행하고, required artifact field mismatch를 fail-closed로 처리한다.
* Current runner는 generic JSON field equality / one-of checks만 수행한다. Vocabulary semantics는 새 validator와 required artifact checks로 추가한다.
* Existing `docs/completion_vocabulary_separation_policy.md`는 broad completion word policy이며, 이번 라운드의 owner / review / external gate axis split을 대체하지 않는다.
* Current codebase inspection 기준으로 legacy / mixed vocabulary가 남아 있는 주요 surface가 존재한다.
  * `Iris/build/description/v2/tools/build/dvf_3_3_closeout_reentry_guard_seal_common.py`
  * `Iris/build/description/v2/tools/build/dvf_3_3_current_route_required_validation_evidence_freshness_reseal.py`
  * `Iris/build/description/v2/tools/build/dvf_3_3_current_source_authority_drift_verification.py`
  * `Iris/build/description/v2/tools/build/dvf_3_3_current_source_authority_drift_verification_adoption_reseal.py`
  * `Iris/build/description/v2/tools/build/run_dvf_3_3_durable_current_authority_surface_alignment.py`
  * `Iris/build/description/v2/tools/build/runtime_payload_state_integrity_residual_seal.py`
  * `Iris/build/description/v2/tools/build/dvf_3_3_terminal_disposition_adjudication_common.py`
  * `Iris/build/description/v2/tools/build/dvf_3_3_shared_disposition_consumption_common.py`
  * `Iris/build/description/v2/tools/build/consumer_universe_denominator_lock_common.py`
* Some older surfaces already use better split states such as `review_pending`, `review_pass`, or `satisfied`; these must be classified, not mechanically rewritten.
* Historical evidence under old staging roots remains provenance trace. Current-looking regenerated artifacts must use the new schema.
* The live required-validation manifest may contain checks against legacy fields such as `independent_review_status == PASS` or `owner_seal_status == PASS`. This round must not modify, remove, or retire those existing checks.
* Manifest handling uses dual-field coexistence. Existing legacy checks remain in place, and new canonical-field checks are added in parallel.
* Legacy projection fields are compatibility-only and must not be consumed as current gate closure inputs.
* Required artifact/test/check predicate removal or modification from the live manifest is forbidden in this round. If legacy check retirement is needed, it requires a separate owner-approved cleanup plan.
* Machine tools may write machine validation fields, inventory reports, transition reports, and validator reports. They must not fabricate owner approval, owner seal, or independent review verdict.
* Owner decision is owner-supplied, not external-review-supplied. A direct owner instruction in the current governance session may be captured as an owner decision record when the record stores `source_kind=owner_supplied`, `decision_authority=owner`, `owner_identity`, `scope_id`, `decision`, `decision_basis`, `captured_by`, timestamp, and the readpoint or artifact hash set it applies to.
* A tool may transcribe an owner-supplied decision into JSON, but the record must distinguish `source_kind=owner_supplied` from `source_kind=tool_generated_placeholder`. A placeholder may only record `pending` or `blocked`.
* Owner decision / owner seal capture risk is controllable by schema and validation. It is not classified as the same structural external dependency as independent review or external validation bundle availability.
* Review artifact presence is not enough. Reviewer identity, role, scope, independence declaration, reviewed artifact list, reviewed validation result or rerun result, timestamp, and hash-sealed bundle are required for a review verdict to close a gate.
* Independent review must also prove the reviewer is independent from the roadmap author and upstream governance-chain artifact author, not only the implementation author / executor / self-record generator.
* For this round's final canonical seal scope, `gate_requirement_by_scope` must set `machine_contract_validation_required=true`, `external_validation_bundle_required=true`, `independent_review_required=true`, `owner_decision_required=true`, `owner_seal_required=true`, and `canonical_external_review_required=true`.
* `gate_requirement_by_scope` uses stable scope IDs:
  * `final_canonical_external_gate_seal`
  * `machine_only_partial`
  * `review_pending_partial`
* `absence_maps_to` is limited to `blocked|pending`. `absence_maps_to=satisfied` is invalid and must fail schema validation.
* Machine-only partial execution is allowed, but it cannot produce `external_gate_state=satisfied`, `canonical_external_review_state=satisfied`, `canonical_seal_allowed=true`, or canonical complete ledger updates.
* `PASS_WITH_NOTES` requires structured note metadata. Free-text-only notes, missing severity, or any blocking note keep the external gate blocked or pending.
* Current / historical separation must be machine-readable through lifecycle field, path prefix, manifest membership, or an explicit combination recorded by the mode discriminator.
* Historical frozen governance evidence is part of the protected set for this round. Writer migration must not regenerate sealed evidence or change its frozen hash.
* Spec token rename / split, including `external_validation_bundle` to `external_validation_bundle_result` plus `external_validation_bundle_state`, is author-reserved and must be recorded in policy token mapping before final closeout.
* Retained legacy checks and relocated current artifacts must obey a dual-field relocation invariant. The execution must choose and record one of these valid modes:
  * retained legacy checks target only frozen historical artifacts
  * relocated current artifacts are targeted only by new canonical checks
  * retained legacy check target artifacts keep legacy fields at the existing checked path
* Upstream governance-chain artifact author membership includes at minimum roadmap input, synthesized roadmap, policy documents, prior plans, prior reviews, and current plan source artifacts consumed by this round.
* Reviewer identity matching must normalize names, handles, model labels, tool labels, and artifact author strings before comparing reviewer identity against author / executor / self-record generator / roadmap author / upstream governance-chain artifact author.
* Legacy projection cleanup is tracked as future debt. It is forbidden in this round and requires a separate owner-approved cleanup plan.
* Token rename / split author sign-off is required before final canonical closeout. Without it, machine artifacts may remain partial / implemented-only but cannot become canonical complete.
* REVIEW_TEMPLATE verdict mapping is not inferred. `PASS -> PASS`, `PASS with minor revisions -> PASS_WITH_NOTES`, `FAIL -> FAIL`, and `WARN -> author_reserved_mapping_required` are the planned default mappings unless owner policy says otherwise.
* Owner approval and owner seal remain owner-authored or owner-supplied governance records. Tool-generated placeholders may only say `pending` or `blocked`.
* Dirty working tree changes outside this plan must be preserved.

---

## 5. Repository Areas Affected

### Code

Expected new offline tooling surfaces:

* `Iris/build/description/v2/tools/build/dvf_3_3_completion_vocabulary_external_gate_vocabulary_split.py`
* `Iris/build/description/v2/tools/build/run_dvf_3_3_completion_vocabulary_external_gate_vocabulary_split.py`
* `Iris/build/description/v2/tools/build/validate_dvf_3_3_completion_vocabulary_external_gate_vocabulary_split.py`
* `Iris/build/description/v2/tests/test_dvf_3_3_completion_vocabulary_external_gate_vocabulary_split.py`

Likely current artifact migration candidates:

* `Iris/build/description/v2/tools/build/dvf_3_3_closeout_reentry_guard_seal_common.py`
* `Iris/build/description/v2/tools/build/dvf_3_3_current_route_required_validation_evidence_freshness_reseal.py`
* `Iris/build/description/v2/tools/build/dvf_3_3_current_source_authority_drift_verification.py`
* `Iris/build/description/v2/tools/build/dvf_3_3_current_source_authority_drift_verification_adoption_reseal.py`
* `Iris/build/description/v2/tools/build/run_dvf_3_3_durable_current_authority_surface_alignment.py`
* `Iris/build/description/v2/tools/build/runtime_payload_state_integrity_residual_seal.py`
* `Iris/build/description/v2/tools/build/dvf_3_3_terminal_disposition_adjudication_common.py`
* `Iris/build/description/v2/tools/build/dvf_3_3_shared_disposition_consumption_common.py`
* `Iris/build/description/v2/tools/build/consumer_universe_denominator_lock_common.py`

Existing read-only runner / manifest surfaces:

* `Iris/_docs/round3/round3_run_contract_tests.py`
* `Iris/_docs/round3/round3_active_core_closure.json`
* `Iris/_docs/round3/round3_test_taxonomy.json`
* `Iris/_docs/round3/current_route_required_validations.json`

No runtime Lua file is planned for mutation.

### Docs

Direct plan artifact:

* `docs/dvf_3_3_completion_vocabulary_external_gate_vocabulary_split_plan.md`

Expected execution docs:

* `docs/dvf_3_3_completion_vocabulary_external_gate_vocabulary_split_policy.md`
* `docs/dvf_3_3_completion_vocabulary_external_gate_vocabulary_split_claim_boundary.md`
* `docs/dvf_3_3_completion_vocabulary_external_gate_vocabulary_split_ledger_packet.md`

Possible pointer update:

* `docs/completion_vocabulary_separation_policy.md`

Possible additive ledger updates after successful execution:

* `docs/DECISIONS.md`
* `docs/ARCHITECTURE.md`
* `docs/ROADMAP.md`

### Config

Expected additive-only target:

* `Iris/_docs/round3/current_route_required_validations.json`

### Generated Artifacts

Primary evidence root:

* `Iris/build/description/v2/staging/dvf_3_3_completion_vocabulary_external_gate_vocabulary_split/`

Expected generated artifacts include:

* `phase1/pass_usage_inventory.jsonl`
* `phase1/legacy_token_mapping_table.json`
* `phase2/canonical_vocabulary_schema.json`
* `phase2/spec_token_mapping_report.json`
* `phase2/review_template_verdict_mapping_report.json`
* `phase2/pass_with_notes_note_schema.json`
* `phase2/vocabulary_policy_report.json`
* `phase3/gate_requirement_by_scope.json`
* `phase3/gate_requirement_scope_id_stability_report.json`
* `phase3/absence_mapping_schema_report.json`
* `phase3/external_gate_transition_matrix.json`
* `phase3/fail_loud_truth_table.json`
* `phase4/independent_review_artifact_contract.json`
* `phase4/review_independence_validation_report.json`
* `phase4/reviewer_identity_normalization_report.json`
* `phase4/upstream_governance_chain_author_membership_report.json`
* `phase4/reviewer_independence_conflict_fixture_report.json`
* `phase5/owner_decision_owner_seal_schema.json`
* `phase5/owner_review_substitution_guard_report.json`
* `phase6/current_artifact_vocabulary_migration_report.json`
* `phase6/dual_field_relocation_invariant_report.json`
* `phase6/historical_trace_preservation_report.json`
* `phase6/current_historical_mode_discriminator.json`
* `phase6/historical_frozen_evidence_hash_report.json`
* `phase7/negative_fixture_matrix_report.json`
* `phase7/protected_surface_no_mutation_report.json`
* `phase7/sealed_governance_evidence_no_mutation_report.json`
* `phase8/required_validation_manifest_adoption_report.json`
* `phase8/legacy_manifest_dual_field_coexistence_report.json`
* `phase8/legacy_projection_cleanup_debt_report.json`
* `phase8/current_route_validation_result.json`
* `phase9/final_completion_vocabulary_external_gate_split_report.json`
* `phase9/token_rename_author_signoff_report.json`
* `phase9/primary_review_artifact_manifest.json`
* `phase9/independent_review_artifact_hash_report.json`
* `phase9/claim_boundary_scan_report.json`

---

## 6. Planned Changes

### Change 1 — Inventory and Legacy Token Classification

Purpose:

Inventory current and historical `PASS` / review / owner / external gate vocabulary usage and classify each occurrence by semantic axis.

Files:

* `Iris/build/description/v2/tools/build/dvf_3_3_completion_vocabulary_external_gate_vocabulary_split.py`
* `Iris/build/description/v2/staging/dvf_3_3_completion_vocabulary_external_gate_vocabulary_split/phase1/pass_usage_inventory.jsonl`
* `Iris/build/description/v2/staging/dvf_3_3_completion_vocabulary_external_gate_vocabulary_split/phase1/legacy_token_mapping_table.json`

Implementation Notes:

* Scan current governance docs, current-route required manifest, relevant DVF runner modules, focused tests, and current staging final reports.
* Classify usages as `machine_contract_validation`, `external_validation_bundle`, `independent_review_verdict`, `owner_decision`, `owner_seal_state`, `external_gate_state`, `canonical_external_review_state`, `historical_trace`, or `ambiguous_current`.
* Known legacy tokens include `owner_seal_status=PASS`, `independent_review_status=PASS`, `review_pass`, `review_pending`, `external_review_complete=true`, `blocked_external_gate=false`, `external_independent_review_status=PASS`, and `canonical_*_seal_allowed=true`.
* Historical records are not failure by themselves. Current-looking regenerated artifacts and live manifest checks are failure candidates.

Validation:

* Unknown current usage count must be `0`.
* Ambiguous current usage must block final closeout.
* Historical trace classification must preserve path / source / readpoint.

---

### Change 2 — Canonical Vocabulary Schema

Purpose:

Define the axis-split schema and forbid bare `PASS` outside allowed validation-result axes.

Files:

* `docs/dvf_3_3_completion_vocabulary_external_gate_vocabulary_split_policy.md`
* `Iris/build/description/v2/staging/dvf_3_3_completion_vocabulary_external_gate_vocabulary_split/phase2/canonical_vocabulary_schema.json`
* `Iris/build/description/v2/staging/dvf_3_3_completion_vocabulary_external_gate_vocabulary_split/phase2/spec_token_mapping_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_completion_vocabulary_external_gate_vocabulary_split/phase2/review_template_verdict_mapping_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_completion_vocabulary_external_gate_vocabulary_split/phase2/pass_with_notes_note_schema.json`

Implementation Notes:

* Define these canonical fields:
  * `machine_contract_validation=PASS|FAIL`
  * `external_validation_bundle_result=PASS|FAIL|null`
  * `external_validation_bundle_state=present|missing|required_missing|not_required|pending`
  * `independent_review_verdict=PASS|FAIL|PASS_WITH_NOTES|null`
  * `independent_review_state=present|missing|pending|invalid`
  * `owner_decision=approved|rejected|pending`
  * `owner_seal_state=sealed|pending|blocked`
  * `external_gate_state=satisfied|blocked|pending`
  * `canonical_external_review_state=satisfied|blocked`
  * `review_notes_present=true|false`
  * `blocking_note_count=<int>`
  * `nonblocking_note_count=<int>`
  * `review_notes_blocking=true|false`
  * `blocking_note_ids=[]`
  * `note_severity_allowed_values=info|minor|blocking`
  * `pass_with_notes_gate_effect=satisfied_candidate|blocked|pending`
* `external_validation_bundle_state` carries pending/absence information; `external_validation_bundle_result` stays a validation result and therefore only allows `PASS`, `FAIL`, or `null`.
* `canonical_external_review_state` must never be `pending`; missing evidence maps to `blocked`.
* `PASS_WITH_NOTES` is valid only for independent review verdict. Blocking notes keep `external_gate_state` pending or blocked and `canonical_external_review_state=blocked`.
* `PASS_WITH_NOTES` with `blocking_note_count > 0`, missing note severity, or free-text-only notes cannot satisfy the external gate.
* Record spec token mapping before execution. In particular, `external_validation_bundle` is split into `external_validation_bundle_result` and `external_validation_bundle_state`.
* Record REVIEW_TEMPLATE mapping as:
  * `PASS -> PASS`
  * `PASS with minor revisions -> PASS_WITH_NOTES`
  * `FAIL -> FAIL`
  * `WARN -> author_reserved_mapping_required`

Validation:

* Owner field `PASS` fixture fails.
* Gate field `PASS` fixture fails.
* Machine field `approved`, `sealed`, or `satisfied` fixture fails.
* Review verdict without review artifact fails.
* `canonical_external_review_state=pending` fixture fails.
* `PASS_WITH_NOTES + blocking_note_count > 0` fixture cannot produce `external_gate_state=satisfied`.
* `PASS_WITH_NOTES + missing note severity` fixture fails.
* `WARN` without author-reserved mapping fixture fails.

---

### Change 3 — Gate Requirement Matrix, Transition, and Independent Review Contract

Purpose:

Define which scope requires which gate axis, and exactly when external gate and canonical external review can close.

Files:

* `Iris/build/description/v2/staging/dvf_3_3_completion_vocabulary_external_gate_vocabulary_split/phase3/gate_requirement_by_scope.json`
* `Iris/build/description/v2/staging/dvf_3_3_completion_vocabulary_external_gate_vocabulary_split/phase3/gate_requirement_scope_id_stability_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_completion_vocabulary_external_gate_vocabulary_split/phase3/absence_mapping_schema_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_completion_vocabulary_external_gate_vocabulary_split/phase3/external_gate_transition_matrix.json`
* `Iris/build/description/v2/staging/dvf_3_3_completion_vocabulary_external_gate_vocabulary_split/phase3/fail_loud_truth_table.json`
* `Iris/build/description/v2/staging/dvf_3_3_completion_vocabulary_external_gate_vocabulary_split/phase4/independent_review_artifact_contract.json`
* `Iris/build/description/v2/staging/dvf_3_3_completion_vocabulary_external_gate_vocabulary_split/phase4/review_independence_validation_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_completion_vocabulary_external_gate_vocabulary_split/phase4/reviewer_identity_normalization_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_completion_vocabulary_external_gate_vocabulary_split/phase4/upstream_governance_chain_author_membership_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_completion_vocabulary_external_gate_vocabulary_split/phase4/reviewer_independence_conflict_fixture_report.json`

Implementation Notes:

* `gate_requirement_by_scope.json` must define at minimum:
  * `scope_id`
  * `machine_contract_validation_required`
  * `external_validation_bundle_required`
  * `independent_review_required`
  * `owner_decision_required`
  * `owner_seal_required`
  * `canonical_external_review_required`
  * `allowed_absence_reason`
  * `absence_maps_to`
* Stable `scope_id` values are:
  * `final_canonical_external_gate_seal`
  * `machine_only_partial`
  * `review_pending_partial`
* `absence_maps_to` enum is exactly `blocked|pending`; `satisfied` is forbidden.
* This round's final seal scope must set all six required booleans to true:
  * `machine_contract_validation_required=true`
  * `external_validation_bundle_required=true`
  * `independent_review_required=true`
  * `owner_decision_required=true`
  * `owner_seal_required=true`
  * `canonical_external_review_required=true`
* Machine-only or review-pending scopes may exist only as partial / implemented-only scopes, and their absence mapping cannot produce `satisfied`.
* `external_gate_state=satisfied` requires every axis required by `gate_requirement_by_scope` for the active scope.
* `canonical_external_review_state=satisfied` requires actual independent review evidence and cannot be satisfied by machine PASS, owner approval, or external bundle PASS alone.
* Review artifact minimum fields:
  * reviewer identity
  * reviewer role
  * reviewer scope
  * reviewer independence declaration
  * `reviewer_independent_from_author`
  * `reviewer_independent_from_executor`
  * `reviewer_independent_from_self_record_generator`
  * `reviewer_independent_from_roadmap_author`
  * `reviewer_independent_from_upstream_governance_chain_artifact_author`
  * reviewed artifact list
  * reviewed validation result or rerun result
  * review verdict
  * structured notes if any
  * hash-sealed review bundle reference
  * review timestamp / readpoint
  * self-generated artifact flag
  * author / executor / reviewer separation flags
* Self-referential hash reports must be handled by explicit exclusion or presence-only rule, not by pretending the report hashes itself.
* `upstream_governance_chain_author_membership_report.json` must define the artifact membership set used for upstream author independence. Minimum membership includes roadmap input, synthesized roadmap, policy documents, prior plans, prior reviews, and current plan source artifacts.
* `reviewer_identity_normalization_report.json` must define normalization for name, handle, model label, tool label, and artifact author string before identity comparison.

Validation:

* Machine PASS + no review blocks.
* Machine PASS + owner approved + no review blocks.
* Review artifact + no hash bundle blocks.
* Review artifact + no reviewed result blocks.
* Reviewer equals author blocks.
* Reviewer equals executor blocks.
* Reviewer equals roadmap author blocks.
* Reviewer equals upstream governance-chain artifact author blocks.
* Missing reviewer independence axis blocks.
* Scope with required axis absent maps according to `gate_requirement_by_scope` and cannot silently satisfy.
* `absence_maps_to=satisfied` fixture fails.
* Unstable / unknown `scope_id` fixture fails.
* Upstream governance-chain artifact membership missing fixture fails.
* Reviewer identity alias collision fixture blocks instead of passing silently.
* Complete evidence set satisfies the gate.

---

### Change 4 — Owner Decision / Owner Seal Separation

Purpose:

Replace owner `PASS` vocabulary with decision and seal state fields. Owner decision is not an external artifact; it is the project owner's explicit decision captured as a governance record with owner-supplied provenance.

Files:

* `Iris/build/description/v2/staging/dvf_3_3_completion_vocabulary_external_gate_vocabulary_split/phase5/owner_decision_owner_seal_schema.json`
* `Iris/build/description/v2/staging/dvf_3_3_completion_vocabulary_external_gate_vocabulary_split/phase5/owner_review_substitution_guard_report.json`
* Current artifact migration candidates listed in section 5.

Implementation Notes:

* Current artifact fields should emit:
  * `owner_decision=approved|rejected|pending`
  * `decision_authority=owner`
  * `owner_identity`
  * `owner_decision_scope`
  * `owner_decision_readpoint`
  * `owner_decision_basis`
  * `owner_decision_source_kind=owner_supplied|tool_generated_placeholder`
  * `owner_decision_captured_by`
  * `owner_seal_state=sealed|pending|blocked`
  * `owner_seal_source_kind=owner_supplied|tool_generated_placeholder`
  * `owner_seal_reason`
  * `owner_seal_depends_on_independent_review=true|false`
  * `owner_seal_does_not_replace_review=true`
  * `canonical_review_claim=false`
* Existing `owner_seal_status=PASS` must be preserved only in historical trace or compatibility projection fields with explicit legacy label.
* Tools may generate `pending` or `blocked` placeholders but may not generate owner `approved` or `sealed` without explicit owner-supplied input in the governance session or a separate owner-authored record.
* Codex transcription of an owner instruction is allowed only when the resulting record says `source_kind=owner_supplied`, identifies the owner, records `captured_by`, and binds the decision to a concrete `scope_id` and readpoint / hash set.
* Owner-supplied `approved` or `sealed` satisfies only the owner axis. It never satisfies independent review, external validation bundle, external gate, or canonical external review by substitution.

Validation:

* Owner `PASS` field in current artifact fails.
* Owner-approved record with missing `owner_identity`, `decision_authority`, `source_kind`, scope, or readpoint/hash binding fails.
* Tool-generated `approved` or `sealed` record fails.
* Owner approved without independent review keeps external gate blocked or pending.
* Owner sealed is not consumed as review verdict.
* Owner rejected blocks canonical seal.

---

### Change 5 — Current Artifact Migration and Historical Preservation

Purpose:

Apply the new schema to current artifacts while preserving historical evidence byte-for-byte where required.

Files:

* `Iris/build/description/v2/tools/build/dvf_3_3_closeout_reentry_guard_seal_common.py`
* `Iris/build/description/v2/tools/build/dvf_3_3_current_route_required_validation_evidence_freshness_reseal.py`
* `Iris/build/description/v2/tools/build/dvf_3_3_current_source_authority_drift_verification.py`
* `Iris/build/description/v2/tools/build/dvf_3_3_current_source_authority_drift_verification_adoption_reseal.py`
* `Iris/build/description/v2/tools/build/run_dvf_3_3_durable_current_authority_surface_alignment.py`
* `Iris/build/description/v2/tools/build/runtime_payload_state_integrity_residual_seal.py`
* `Iris/build/description/v2/tests/test_dvf_3_3_completion_vocabulary_external_gate_vocabulary_split.py`
* `Iris/build/description/v2/staging/dvf_3_3_completion_vocabulary_external_gate_vocabulary_split/phase6/current_historical_mode_discriminator.json`
* `Iris/build/description/v2/staging/dvf_3_3_completion_vocabulary_external_gate_vocabulary_split/phase6/dual_field_relocation_invariant_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_completion_vocabulary_external_gate_vocabulary_split/phase6/historical_frozen_evidence_hash_report.json`

Implementation Notes:

* Current writers emit new canonical fields.
* Legacy fields may be retained only under explicit compatibility namespace such as `legacy_vocabulary_projection` and must not be used to close current gates.
* Existing tests that assert `independent_review_status == PASS` or `owner_seal_status == PASS` must not be mechanically rewritten if doing so modifies existing live manifest predicates.
* Preferred path is dual-field coexistence: keep legacy compatibility projection fields, add canonical fields, and add new tests / required checks for the canonical fields.
* Existing live manifest checks must remain byte-equivalent unless a separate owner-approved cleanup plan explicitly opens legacy check retirement.
* `dual_field_relocation_invariant_report.json` must record one selected invariant:
  * retained legacy checks target only frozen historical artifacts
  * relocated current artifacts are targeted only by new canonical checks
  * retained legacy check target artifacts keep legacy fields at the existing checked path
* If the selected invariant cannot be met, stop before manifest adoption and open a separate cleanup or compatibility plan.
* Historical staging artifacts are classified, not rewritten.
* Required manifest checks that currently expect legacy owner/review PASS fields remain in place; new canonical field checks are added in parallel with a dual-field coexistence report.
* `current_historical_mode_discriminator.json` must define how a row is current or historical using path prefix, lifecycle field, manifest membership, or an explicit combination.
* Historical frozen governance evidence hash baselines must be captured before writer migration and compared after migration.

Validation:

* Historical evidence PASS preserved.
* Current artifact owner/review/gate PASS rejected outside allowed axes.
* Current-looking legacy vocabulary reentry count is `0`.
* Historical legacy PASS artifact accepted as historical trace fixture passes.
* Current-looking legacy PASS artifact fixture fails.
* Existing manifest required artifact/test/check removal count is `0`.
* Existing manifest required artifact/test/check modification count is `0`.
* Dual-field relocation invariant PASS.
* Historical frozen governance evidence hash mismatch count is `0`.
* Protected source / rendered / Lua bridge / runtime / package mutation count is `0`.

---

### Change 6 — Tooling, Validator, Negative Fixtures

Purpose:

Fail-closed validation for vocabulary split and gate predicates.

Files:

* `Iris/build/description/v2/tools/build/validate_dvf_3_3_completion_vocabulary_external_gate_vocabulary_split.py`
* `Iris/build/description/v2/tests/test_dvf_3_3_completion_vocabulary_external_gate_vocabulary_split.py`
* `Iris/build/description/v2/tests/fixtures/negative/completion_vocabulary_external_gate/*`
* `Iris/build/description/v2/tests/fixtures/positive/completion_vocabulary_external_gate/historical_legacy_pass_trace.json`

Implementation Notes:

* Validator checks schema enums, `gate_requirement_by_scope`, stable scope IDs, `absence_maps_to` enum, writer identity, review artifact requirements, owner/review substitution, external validation bundle/review substitution, external gate transition, `PASS_WITH_NOTES` note metadata, reviewer identity normalization, upstream governance-chain author membership, historical/current mode separation, dual-field relocation invariant, sealed governance evidence hash preservation, and protected-surface no-mutation.
* Negative fixtures must use sandbox copies and must not mutate live `current_route_required_validations.json`.
* Required tests should follow the existing pattern where current-route required tests use subprocess execution or generated JSON reports rather than importing unallowlisted `tools.build.*` modules through the current-route closure.

Validation:

* Focused unittest passes.
* Negative fixture matrix passes.
* Positive historical legacy PASS fixture passes only as historical trace.
* Current-route runner regression passes.
* Writer authority violation fixture fails.
* Reviewer equals roadmap author fixture fails.
* Reviewer equals upstream governance-chain artifact author fixture fails.
* Reviewer identity alias collision fixture fails closed.
* `PASS_WITH_NOTES` with blocking note fixture fails.
* `absence_maps_to=satisfied` fixture fails.
* Unknown `scope_id` fixture fails.
* Upstream governance-chain membership missing fixture fails.
* Dual-field relocation invariant violation fixture fails.
* Sealed governance evidence hash mutation fixture fails.

---

### Change 7 — Required Validation Manifest Adoption

Purpose:

Adopt the split as a current-route required governance gate.

Files:

* `Iris/_docs/round3/current_route_required_validations.json`
* `Iris/build/description/v2/staging/dvf_3_3_completion_vocabulary_external_gate_vocabulary_split/phase8/required_validation_manifest_adoption_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_completion_vocabulary_external_gate_vocabulary_split/phase8/legacy_manifest_dual_field_coexistence_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_completion_vocabulary_external_gate_vocabulary_split/phase8/legacy_projection_cleanup_debt_report.json`

Implementation Notes:

* Adoption is additive-only.
* Existing required artifact/test/check predicate removal count must be `0`.
* Existing required artifact/test/check predicate modification count must be `0`.
* Legacy checks are not retired by this round. New canonical checks are added beside them.
* `legacy_projection_cleanup_debt_report.json` records that dual-field coexistence is future debt and that cleanup requires a separate owner-approved plan.
* Required artifacts include final vocabulary split report, schema report, gate requirement matrix, transition matrix, `PASS_WITH_NOTES` note schema, mode discriminator, sealed governance evidence hash report, negative fixture matrix report, protected surface no-mutation report, and claim boundary scan.
* Required tests include the focused vocabulary split test methods.
* Manifest adoption is governance-only and must not be read as external gate satisfied, canonical review satisfied, source mutation, runtime mutation, or release readiness.

Validation:

* Additive diff report PASS.
* Required artifact/test/check predicate removal count `0`.
* Required artifact/test/check predicate modification count `0`.
* Legacy manifest dual-field coexistence report PASS.
* Legacy projection cleanup debt report PASS.
* Current-route validation PASS with closure enforced.
* Protected surface no-mutation PASS.

---

### Change 8 — Final Report / Claim Boundary / Ledger Packet

Purpose:

Write final report and docs that make the allowed claim and non-claims explicit.

Files:

* `docs/dvf_3_3_completion_vocabulary_external_gate_vocabulary_split_claim_boundary.md`
* `docs/dvf_3_3_completion_vocabulary_external_gate_vocabulary_split_ledger_packet.md`
* `Iris/build/description/v2/staging/dvf_3_3_completion_vocabulary_external_gate_vocabulary_split/phase9/final_completion_vocabulary_external_gate_split_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_completion_vocabulary_external_gate_vocabulary_split/phase9/token_rename_author_signoff_report.json`

Implementation Notes:

* Final report minimum fields:
  * `gate_requirement_scope_id`
  * `machine_contract_validation_required`
  * `external_validation_bundle_required`
  * `independent_review_required`
  * `owner_decision_required`
  * `owner_seal_required`
  * `canonical_external_review_required`
  * `allowed_absence_reason`
  * `absence_maps_to`
  * `plan_level_review_verdict`
  * `plan_level_pass_does_not_satisfy_independent_review_gate`
  * `machine_contract_validation`
  * `external_validation_bundle_result`
  * `external_validation_bundle_state`
  * `independent_review_verdict`
  * `independent_review_state`
  * `independent_review_artifact_present`
  * `reviewer_identity_present`
  * `reviewer_role_present`
  * `reviewer_scope_present`
  * `reviewer_independence_proven`
  * `reviewer_independent_from_author`
  * `reviewer_independent_from_executor`
  * `reviewer_independent_from_self_record_generator`
  * `reviewer_independent_from_roadmap_author`
  * `reviewer_independent_from_upstream_governance_chain_artifact_author`
  * `review_notes_present`
  * `blocking_note_count`
  * `nonblocking_note_count`
  * `review_notes_blocking`
  * `blocking_note_ids`
  * `pass_with_notes_gate_effect`
  * `review_bundle_hash_sealed`
  * `reviewed_validation_result_present`
  * `owner_decision`
  * `owner_seal_state`
  * `external_gate_state`
  * `canonical_external_review_state`
  * `current_historical_mode_discriminator_status`
  * `dual_field_relocation_invariant_status`
  * `historical_frozen_evidence_hash_mismatch_count`
  * `token_rename_author_signoff_state`
  * `token_rename_author_signoff_required_before_final_canonical_closeout`
  * `legacy_projection_cleanup_requires_separate_owner_approved_plan`
  * `self_generated_pass_substitution_blocked`
  * `machine_pass_does_not_replace_review`
  * `owner_approval_does_not_replace_review`
  * `external_validation_bundle_does_not_replace_review`
  * `legacy_projection_consumed_for_current_gate=false`
  * `canonical_seal_allowed`
* If the round lacks actual independent review, final report must use `canonical_external_review_state=blocked` and `canonical_seal_allowed=false`, even if machine validation and owner-supplied owner seal record pass.
* If the round lacks owner-supplied owner decision / seal record, final report must use owner axis `pending` or `blocked`; this is an in-scope capture blocker, not external review failure.
* If token rename / split author sign-off is missing, final report must use `canonical_seal_allowed=false` even if machine validation passes.
* If `canonical_external_review_state=blocked` or `canonical_seal_allowed=false`, DECISIONS / ROADMAP / ARCHITECTURE updates may record only partial / implemented-only trace. They must not record canonical complete, satisfied external review, or canonical seal.

Validation:

* Final report schema PASS.
* Claim boundary scan PASS.
* Self-application check PASS.
* Plan-level PASS vs independent-review gate boundary PASS.
* Token rename author sign-off report PASS or final canonical closeout blocked.
* Partial closeout ledger update restriction PASS.
* Current-route validation PASS if adopted.

---

## 7. Validation Plan

### Automated Validation

Planned commands:

* `uv run python -B Iris\build\description\v2\tools\build\run_dvf_3_3_completion_vocabulary_external_gate_vocabulary_split.py --mode all`
* `uv run python -B Iris\build\description\v2\tools\build\validate_dvf_3_3_completion_vocabulary_external_gate_vocabulary_split.py --require-complete`
* `uv run python -B -m unittest discover -s Iris\build\description\v2\tests -p "test_dvf_3_3_completion_vocabulary_external_gate_vocabulary_split.py"`
* `uv run python -B Iris\_docs\round3\round3_run_contract_tests.py --class current --enforce-current-build-closure --out Iris\build\description\v2\staging\dvf_3_3_completion_vocabulary_external_gate_vocabulary_split\phase8\current_route_validation_result.json`

Expected automated checks:

* vocabulary schema enum validation
* spec token mapping validation
* REVIEW_TEMPLATE verdict mapping validation
* `gate_requirement_by_scope` validation
* stable `scope_id` validation
* `absence_maps_to ∈ {blocked,pending}` validation
* `absence_maps_to=satisfied` rejection fixture
* legacy token semantic classification
* current vs historical mode separation
* historical legacy PASS positive fixture
* current-looking legacy PASS negative fixture
* owner/review/gate PASS misuse rejection
* independent review artifact contract validation
* reviewer independent from roadmap author validation
* reviewer independent from upstream governance-chain artifact author validation
* upstream governance-chain artifact membership validation
* reviewer identity normalization validation
* `PASS_WITH_NOTES` blocking note validation
* owner/review substitution guard
* external validation bundle substitution guard
* self-generated PASS substitution guard
* external gate transition matrix validation
* canonical external review state cannot be pending
* legacy manifest dual-field coexistence validation
* existing manifest artifact/test/check predicate removal count `0`
* existing manifest artifact/test/check predicate modification count `0`
* sealed governance evidence frozen hash validation
* dual-field relocation invariant validation
* retained legacy check / relocated current artifact coexistence fixture
* token rename author sign-off tracking validation
* legacy projection cleanup debt report validation
* negative fixture matrix
* live required-validation manifest additive adoption
* protected source / rendered / Lua bridge / runtime / package no-mutation
* partial closeout canonical ledger update restriction
* current-route required-validation runner regression

### Manual Validation

Manual review should inspect:

* `docs/dvf_3_3_completion_vocabulary_external_gate_vocabulary_split_policy.md`
* `docs/dvf_3_3_completion_vocabulary_external_gate_vocabulary_split_claim_boundary.md`
* final report field matrix
* gate requirement matrix
* stable scope ID list
* absence mapping schema
* legacy token mapping table
* spec token mapping table
* token rename author sign-off report
* REVIEW_TEMPLATE verdict mapping
* live manifest additive diff
* independent review artifact contract
* reviewer conflict axes
* reviewer identity normalization report
* upstream governance-chain artifact author membership report
* `PASS_WITH_NOTES` note schema
* dual-field relocation invariant report
* current / historical mode discriminator
* sealed governance evidence hash report
* legacy projection cleanup debt report
* owner decision / owner seal schema
* non-claims and validation ceiling

Manual validation does not mean in-game validation. It is governance / artifact inspection only.

### Validation Limits

This plan will not validate:

* runtime equivalence
* in-game UI behavior
* tooltip / browser behavior
* package build readiness
* release readiness
* Workshop readiness
* B42 readiness
* deployment readiness
* manual QA
* semantic quality
* public-facing text acceptance
* live migration execution
* source/rendered/runtime/package mutation correctness
* full clean-checkout required-evidence reproducibility
* full historical byte reproducibility
* actual external reviewer quality
* actual independent review performance unless an external review artifact is supplied

---

## 8. Risk Surface Touch

### Authority Surface

Touched. This plan changes governance authority vocabulary and current-route required-validation checks. It does not change source authority, rendered authority, Lua bridge authority, runtime authority, or package authority.

### Runtime Behavior Surface

None planned. Runtime Lua and user-facing Iris behavior are out of scope.

### Compatibility Surface

Touched / concerns. Current artifact readers and validators that expect legacy fields may need compatibility projection. Historical artifact readers must continue to read legacy tokens as historical trace. Existing live manifest checks are preserved, and new canonical checks are added beside them.

### Sealed Artifact Surface

Touched by classification and frozen-hash protection only. Historical sealed artifacts must not be rewritten. New artifacts may supersede current vocabulary schema, but old artifacts remain provenance trace. Historical frozen governance evidence hashes are protected against writer migration.

### Public-Facing Output Surface

None planned. No user-facing text, release claim, README marketing claim, tooltip, Browser, or Wiki output mutation is planned.

---

## 9. Risk Analysis

### Architecture Risk

* The split can become a new broad governance framework if it expands beyond DVF 3-3 current governance. Keep scope limited to this DVF 3-3 vocabulary problem.
* Duplicate policy authority can emerge between `completion_vocabulary_separation_policy.md` and the new split policy. The broad policy should point to the split policy rather than redefine it.

### Runtime Risk

* Runtime risk is low because no runtime Lua or payload mutation is planned.
* Accidental inclusion of runtime chunk or package output in generated evidence must be blocked by protected surface hash checks.

### Compatibility Risk

* Existing tests and manifest checks that expect `independent_review_status=PASS` or `owner_seal_status=PASS` may fail if legacy projection is removed instead of preserved.
* Existing historical report readers may need legacy compatibility projection. The projection must be explicitly labeled historical or compatibility-only.
* Token split such as `external_validation_bundle` to result/state fields can break readers unless the mapping is author-confirmed and documented.
* Retained legacy checks can fail relocated current artifacts unless the dual-field relocation invariant is selected and enforced.

### Regression Risk

* The live current-route required-validation manifest can become too strict and fail on historical artifacts if current/historical mode separation is weak.
* Negative fixtures can produce false positives if they scan generated reports without excluding sandbox paths.
* `PASS_WITH_NOTES` can become a loophole if blocking notes are not modeled.
* Existing required-validation manifest checks can be modified by accident if additive-only does not count predicate changes as modifications.
* Sealed governance evidence hashes can drift if writer migration regenerates historical evidence.
* `absence_maps_to` can become a schema loophole if values beyond `blocked|pending` are accepted.

### Governance Risk

* Machine PASS can again be mistaken for independent review completion.
* Owner approval can again be mistaken for review verdict.
* Owner decision capture can be over-classified as an external dependency if the plan treats owner-supplied input as external-review evidence. This is not a structural external dependency; mitigate with owner-supplied provenance, scope binding, and transcription validation.
* External validation bundle PASS can again be mistaken for independent review artifact.
* `not_required` can become a new bypass if scope requirements are not fixed in `gate_requirement_by_scope`.
* A roadmap author or upstream governance-chain artifact author can close the review gate if independence axes are incomplete.
* Manifest adoption can be over-read as canonical external review satisfaction.
* Self-application can be skipped, letting this round claim a satisfied external review state without actual independent review.
* Partial closeout can be over-recorded in DECISIONS / ROADMAP / ARCHITECTURE as canonical complete.
* Plan-level PASS can be over-read as independent-review gate satisfied.
* Upstream governance-chain author independence can become self-declared if membership and identity normalization are not materialized.

### Risk Reclassification After Owner Clarification

* Owner decision / owner seal availability is a controllable governance-capture risk when the project owner supplies an explicit decision for a named scope.
* Owner decision / owner seal must be recorded as `owner_supplied` governance records, not as `external_supplied` review artifacts and not as tool-generated `PASS`.
* The remaining structural external dependency is the genuine independent review / external validation bundle axis, because the project owner and implementation tooling cannot self-satisfy reviewer independence.
* Implementation probability should be improved by treating owner decision capture as in-scope execution work and reserving `blocked` / `pending` only for missing independent review, missing external validation bundle, failed hash binding, failed scope binding, or absent owner input.

---

## 10. Rollback Plan

Rollback is governance / tooling rollback, not runtime rollback.

* Revert the live `Iris/_docs/round3/current_route_required_validations.json` additive entries for this round as one commit-scoped diff.
* Revert new validator / runner / focused test files as the same rollback unit if the schema creates false positives.
* Leave historical evidence untouched.
* If current artifact migration causes reader compatibility failure, keep the new policy docs and validator as diagnostic artifacts but remove manifest adoption until dual-field compatibility projection is repaired.
* If a legacy manifest check must be modified or retired, stop this round and open a separate owner-approved cleanup plan.
* If sealed governance evidence hashes change, rollback writer migration before any closeout claim.
* If the dual-field relocation invariant cannot be satisfied, stop before manifest adoption and keep artifacts diagnostic-only.
* If `absence_maps_to` validation accepts a value outside `blocked|pending`, stop before final report generation.
* If token rename author sign-off is missing, do not rollback machine artifacts; close as partial / implemented-only with `canonical_seal_allowed=false`.
* If independent review / external validation bundle evidence is missing, do not rollback machine artifacts. Close with `canonical_external_review_state=blocked`, `external_gate_state=pending|blocked`, and `canonical_seal_allowed=false`.
* If owner decision / owner seal record is missing despite owner availability, capture the owner-supplied decision for the named scope before final closeout. If no owner input is supplied, close partial with owner axis `pending`, not as an external-review failure.
* Protected source / rendered / Lua bridge / runtime / package hashes must remain unchanged before and after rollback.
* Historical frozen governance evidence hashes must remain unchanged before and after rollback.

---

## 11. Governance Constraints

* `docs/Philosophy.md` compliance is mandatory.
* Hub & Spoke / SPI boundaries remain unchanged.
* Iris remains a 100% Lua runtime module; this plan only touches offline build / governance tooling.
* Runtime / build-time separation must remain preserved.
* Source / facts / decisions / rendered / Lua bridge / runtime chunks / package payload mutation is forbidden.
* Historical evidence is preserved and not retroactively rewritten.
* Current-route required-validation manifest adoption is additive-only, including no existing required artifact/test/check predicate removal or modification.
* Legacy manifest checks remain in place; new canonical checks are added in parallel.
* Legacy compatibility projection must not be consumed as current gate closure input.
* Missing or ambiguous evidence fails closed.
* Scope requirements must come from `gate_requirement_by_scope`; unlisted absence is blocked.
* `gate_requirement_by_scope.scope_id` values are fixed to `final_canonical_external_gate_seal`, `machine_only_partial`, and `review_pending_partial` unless a later owner-approved plan extends them.
* `absence_maps_to` values are limited to `blocked|pending`.
* Owner decision does not replace independent review.
* Owner seal does not replace external gate satisfaction.
* Owner decision and owner seal are owner-supplied governance records, not external-review artifacts.
* A direct owner instruction may be transcribed by tooling only with `source_kind=owner_supplied`, explicit owner identity, scope binding, readpoint / hash binding, and `captured_by`; otherwise owner fields remain `pending` or `blocked`.
* External validation bundle does not replace independent review artifact.
* Machine-generated PASS does not replace independent / external review completion.
* `PASS_WITH_NOTES` cannot satisfy a gate when blocking notes exist, note severity is missing, or notes are free-text-only.
* Reviewer independence must include author, executor, self-record generator, roadmap author, and upstream governance-chain artifact author.
* Upstream governance-chain artifact author membership and reviewer identity normalization must be materialized before independence validation can pass.
* Current / historical mode separation must be machine-readable.
* Dual-field relocation invariant must be selected and validated before manifest adoption.
* Historical frozen governance evidence hashes must be preserved.
* Partial / implemented-only closeout must not be recorded as canonical complete in DECISIONS / ROADMAP / ARCHITECTURE.
* Plan-level PASS permits implementation planning only; it does not satisfy independent-review hard gate.
* Token rename / split author sign-off is required before final canonical closeout.
* Legacy projection cleanup remains future debt and requires a separate owner-approved plan.
* Current artifact fields must be axis-qualified.
* `canonical_external_review_state` has only `satisfied|blocked`.
* Tool-generated reports may not fabricate owner approval, owner seal, or independent review verdict.
* Existing dirty worktree changes outside this plan must be preserved.

---

## 12. Expected Closeout State

Expected closeout target is conditional.

If machine validation, focused tests, current-route required validation, negative fixtures, manifest adoption, protected no-mutation, sealed governance evidence hash preservation, dual-field relocation invariant, required external validation bundle, actual independent review artifact, owner-supplied owner decision record, owner-supplied owner seal record, and token rename author sign-off all exist and pass:

* `complete_governance_only`
* `external_gate_state=satisfied`
* `canonical_external_review_state=satisfied`
* `canonical_seal_allowed=true`

If machine validation passes but required external validation bundle, actual independent review, owner-supplied owner decision / seal record, dual-field relocation invariant, or token rename author sign-off is missing:

* `implemented_only` or `partial`
* `external_gate_state=pending|blocked`
* `canonical_external_review_state=blocked`
* `canonical_seal_allowed=false`
* no canonical complete ledger update

Owner decision / owner seal absence is treated as an in-scope capture blocker, not as the same structural external dependency as independent review. Once the owner supplies a scoped decision, tooling may record it as `owner_supplied`; it still cannot satisfy `independent_review_verdict`, `external_gate_state`, or `canonical_external_review_state` by substitution.

This closeout never means release readiness, package readiness, Workshop readiness, B42 readiness, deployment readiness, manual in-game QA, semantic quality completion, public-facing text acceptance, live migration execution, source mutation, rendered regeneration, Lua bridge export, runtime chunk replacement, or package payload mutation.
