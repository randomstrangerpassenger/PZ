# Implementation Plan

> Status: proposed input-normalization prerequisite roadmap-and-plan draft / Cycle 4 PASS optional hardening applied / implementation may start for core input normalization only / no roadmap final approval / no migration execution / no current cutover
> Roadmap input: `C:/Users/MW/.codex/attachments/b4d588fb-b9a3-429c-ad29-9f4c69bec41f/pasted-text.txt` / sha256 `D3C7AA1131089BF78CAFAF521628202DC2CA70A57447138CD4156E4641C43AE4` / non-authority synthesis reference
> Review input: `C:/Users/MW/.codex/attachments/f2a13595-31b2-428a-9a88-0d6218a9acec/pasted-text.txt` / sha256 `C88C861F69741EAC1AC7293C18905CB5684ECD9F808D3EE3EB99236FAADE145B` / WARN targeted revision reference
> Review input: `C:/Users/MW/.codex/attachments/d8e2c8d3-9413-431a-9a87-e7fcc320d082/pasted-text.txt` / sha256 `388C302F79B3AB11A9D087073248A4B2614BB96C1DB556C5AB7408BDA8BDD556` / Cycle 2 PASS with minor non-blocking revisions reference
> Review input: `C:/Users/MW/.codex/attachments/9698c681-284f-407a-975c-b26b62a827d9/pasted-text.txt` / sha256 `DDD2CECFA02C0E3D4F2C222DA3473861FC2D7D3B7F3F3CAE917C7A514F06B33A` / Cycle 3 WARN targeted revision reference
> Review input: `C:/Users/MW/.codex/attachments/589fa429-400c-4976-a0ff-08e2c5b0ad50/pasted-text.txt` / sha256 `6C45A959A96A41F6E66C7C446B046FC5133FD5C8D98722F50DF8C581AE7DA7B3` / Cycle 4 PASS with optional minor revision reference
> Template input: `docs/PLAN_TEMPLATE.md` / sha256 `38D70D4D624733DB4D24F047E0B737A47C75522A967C84F06FE5AABC5EBD9BA1`
> Upstream principle: `docs/dvf_3_3_vnext_consumer_migration_principles.md`
> Downstream readiness plan: `docs/dvf_3_3_vnext_current_authority_cutover_tooling_readiness_plan.md`
> Cutover contract: `docs/dvf_3_3_vnext_cutover_contract.md`
> Top authority: `docs/Philosophy.md`

## 1. Objective

DVF 3-3 vNext current authority cutover tooling readiness가 actual consumer migration executor, row-level ledger, actual diff-to-ledger validator, downstream command-surface handoff를 안전하게 구현하기 전에, `change-required 311` 입력을 executor-safe row-level contract로 정규화한다.

이 계획은 migration 실행 계획이나 cutover 실행 계획이 아니다. 목표는 후속 tooling readiness 라운드가 raw `change_required_index.md` 또는 raw `consumer_migration_matrix.jsonl`을 직접 실행 입력으로 오독하지 않도록, 다음 downstream input contract surface를 staging evidence로 검토 가능한 상태까지 정규화하는 것이다.

* row-level terminal disposition
* missing-path disposition ledger
* deterministic anchor relocation evidence
* authority-role migration rule seed
* downstream Phase 0 / 4 / 5 command-surface compatibility manifest
* downstream tooling-readiness Phase 3 / 4 / 6 source-target bridge contract
* single reconciled input manifest
* final contract report and handoff packet

완료 claim은 다음 범위로 제한한다.

```text
DVF 3-3 vNext consumer migration input normalization is machine-validated for downstream tooling-readiness consumption.
This is not consumer migration execution, current authority adoption, live runtime replacement,
successor baseline identity final seal, package readiness, or release readiness.
Governance complete requires independent review after machine PASS.
```

---

## 2. Scope

이 계획은 `2105 Baseline Consumption Audit`과 vNext execution Phase 8 consumer migration matrix / dry-run 산출물을 read-only provenance input으로 사용하여, 후속 executor가 사용할 단일 정규화 입력을 만든다.

포함 범위:

* canonical source input inventory, freshness binding, fingerprint, row-count contract 작성
* audit 311 population과 execution matrix 311 membership cross-check 작성
* `change-required 311`의 7-value terminal disposition matrix 생성
* blocked reason allowlist와 apply/non-apply blocked class 작성
* missing path row의 non-apply / blocked disposition ledger 생성
* line-anchor drift deterministic relocation validator 작성
* anchor freshness와 row-id set reconciliation 작성
* actual apply-eligible row 기반 authority-role migration rule seed 작성
* downstream Phase 0 / 4 / 5 compatibility manifest와 source binding 작성
* downstream tooling-readiness Phase 3 consumer migration materialization / authority rule / missing-path ledger compatibility contract 작성
* downstream tooling-readiness Phase 4 actual diff-to-ledger target contract 작성
* downstream tooling-readiness Phase 6 consumer migration reconciled input manifest compatibility contract 작성
* raw input direct-consumption 금지 guard 작성
* exact command validation registry 작성
* single reconciled input manifest 작성
* `cutover_input_usable` / `handoff_usable` machine-readable gate 작성
* exact command validation, focused unit / contract tests, negative tests 작성
* protected surface no-mutation verdict 작성
* `machine_contract_status`와 `governance_closeout_status`가 분리된 final normalization contract report, closeout, handoff packet, ledger packet draft 작성

Primary execution evidence root:

* `Iris/build/description/v2/staging/dvf_3_3_vnext_consumer_migration_input_normalization/`

Plan artifact:

* `docs/dvf_3_3_vnext_consumer_migration_input_normalization_plan.md`

Roadmap / plan draft relationship:

* This document is a roadmap-and-plan draft for this prerequisite normalization round, not a final roadmap artifact.
* The roadmap sequence is the Phase 0-8 artifact and change sequence in this document; implementation must not reinterpret the order or merge gates without updating this plan first.
* Roadmap draft completion means the prerequisite route, artifact families, gates, and closeout claim boundary are change-controlled for implementation planning. It does not mean tooling implementation, migration execution, current authority adoption, cutover completion, or governance final approval.
* Final roadmap approval is allowed only after machine PASS, independent review, and any required DECISIONS / ARCHITECTURE / ROADMAP update or explicit reviewer clearance.
* If governance requires a standalone ROADMAP_TEMPLATE artifact, it must be produced as a separate companion artifact. This plan cannot satisfy that requirement by self-declaring final approval.
* Machine-readable boundary fields emitted by Phase 0 and repeated in final report:
  * `roadmap_artifact_status=draft_not_final`
  * `implementation_allowed_scope=core_input_normalization_only`
  * `downstream_target_contract_execution_allowed=false`
  * `roadmap_final_approval_required_before_governance_complete=true`

### Explicitly Out Of Scope

* current authority baseline 실제 채택
* successor baseline identity final seal
* live runtime chunk replacement
* runtime cutover tool 실행 또는 완성 claim
* actual consumer migration executor 실행 완료
* main repo / live tree consumer migration completion 선언
* frozen `2105 / 2084 / 21` 복구
* 숫자 `2105`, `2084`, `21` 또는 vocabulary 문자열의 기계적 치환
* historical / diagnostic / generated row의 current hard gate 승격
* `change_forbidden 27558` rows 재판정 또는 cleanup mutation
* source facts / decisions / rendered output / runtime Lua payload 변경
* Browser / Wiki / Tooltip behavior 변경
* package readiness / release readiness / Workshop readiness / B42 readiness 선언
* manual in-game validation, multiplayer validation, long-session runtime validation
* downstream implementation plan body 수정
* current-route tooling allowlist 자동 확장 또는 current core 12 확장

---

## 3. Non-Goals

* `change_required == actual_apply_eligible`로 재해석하지 않는다.
* raw audit index 또는 raw migration matrix를 executable instruction list로 만들지 않는다.
* no-op / preserve / generated / false-positive row를 migrated diff로 세지 않는다.
* missing path row를 삭제 대상, migration failure, 또는 migrated diff로 오독하지 않는다.
* line number만 신뢰해 executor가 변경 위치를 결정하게 하지 않는다.
* authority-role migration을 hardcoded numeric replacement로 축소하지 않는다.
* dry-run evidence를 actual migration completion으로 읽지 않는다.
* `cutover_input_usable=true` candidate predicate를 current cutover authorization으로 읽지 않는다.
* independent review handoff를 authority adoption이나 execution approval로 표현하지 않는다.

---

## 4. Assumptions

* `docs/Philosophy.md`가 최상위 기준이다.
* `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`의 2026-06-17 current readpoint를 따른다.
* `docs/dvf_3_3_vnext_consumer_migration_principles.md`는 2105 audit를 read-only migration input으로 고정한다.
* `docs/dvf_3_3_vnext_cutover_contract.md`에 따라 existing chunk manifest와 chunk files는 별도 승인된 cutover 전까지 deployable runtime authority다.
* frozen `2105 / 2084 / 21`은 predecessor, comparison reference, migration input이며 current source authority 복구 대상이 아니다.
* 2105 Baseline Consumption Audit은 `raw 198815 / accepted 27869 / change-required 311 / change-forbidden 27558 / ambiguous 0` readpoint로 봉인되어 있다.
* consumer migration input은 `Iris/build/description/v2/staging/dvf_3_3_vnext_execution/phase8/consumer_migration_matrix.jsonl`과 `phase8/consumer_migration_dry_run.json`을 포함한다.
* canonical source input은 Phase 0 `required_source_inputs.json`에서 exact path, artifact role, expected count, freshness requirement, sha256, required/allowed-absent policy, claim boundary로 hard-bound한다.
* audit `classified_ledger.jsonl` / `change_required_index.md`의 `change-required 311` population과 execution `consumer_migration_matrix.jsonl`의 311 population은 membership level에서 reconcile되어야 한다. Count equality만으로는 충분하지 않다.
* current-route required validation manifest는 corrected evidence freshness를 요구하며, 이 라운드에서는 `Iris/_docs/round3/current_route_required_validations.json`을 수정하지 않는다.
* `change-forbidden` occurrence mutation count는 항상 0이어야 한다.
* current `data/`, `output/`, live runtime chunk surface는 이 라운드에서 mutation하지 않는다.
* this plan uses Phase 0 for source input contract freeze. Phase 0은 mutation phase가 아니라 fail-loud prerequisite gate다.
* validation depth는 offline contract-heavy로 둔다. Runtime-heavy, package-heavy, release-heavy validation은 이 계획의 검증 범위가 아니다.
* preserve 계열 row는 mutation rule seed에 포함하지 않는다. 필요하면 non-migration preserve ledger evidence로만 표현한다.
* rule seed는 `actual_apply_eligible` row의 mutation 후보에만 적용한다.
* `docs/dvf_3_3_vnext_current_authority_cutover_tooling_readiness_plan.md` is the immediate downstream consumer plan for this prerequisite, but it remains a future handoff / reconciliation target in this round. It is not promoted to sealed source authority by this plan.
* downstream readiness plan은 future handoff target이다. Compatibility manifest의 field source authority는 Phase 5 `compatibility_source_binding.json`에서 `docs/dvf_3_3_vnext_current_authority_implementation_2105_consumer_migration_plan.md`, `docs/dvf_3_3_vnext_cutover_contract.md`, 그리고 readiness-plan requirement를 `future_handoff_target_only`로 분리해 trace한다.
* Candidate downstream readiness paths are normalization-side expectations and future reconciliation targets, not authoritative source fields. Each path-bearing row must include `path_kind=future_readiness_target`, `materialized_by_this_round=false`, `target_only=true`, and `source_authority=false`.
* If the downstream readiness plan is later renamed, reshaped, or sealed differently, these future target rows become `stale_future_target` and block handoff until the compatibility contract is updated. They must not silently pass as exact source authority.
* Primary future reconciliation targets for this prerequisite are limited to the original downstream surfaces:
  * `Iris/build/description/v2/staging/dvf_3_3_vnext_cutover_tooling_readiness/phase3/row_level_migration_ledger.jsonl`
  * `Iris/build/description/v2/staging/dvf_3_3_vnext_cutover_tooling_readiness/phase4/actual_diff_to_ledger_report.json`
  * `Iris/build/description/v2/staging/dvf_3_3_vnext_cutover_tooling_readiness/phase4/diff_hunk_ledger_bijection_report.json`
  * `Iris/build/description/v2/staging/dvf_3_3_vnext_cutover_tooling_readiness/phase6/command_surface_mapping.for_current_cutover.json`
  * `Iris/build/description/v2/staging/dvf_3_3_vnext_cutover_tooling_readiness/phase6/consumer_migration_reconciled_input_manifest.json`
* Related readiness capabilities such as materialization preflight, missing-path ledger, authority-role rules, runtime live command template, current cutover handoff manifest, and tool-contract compatibility manifest are recorded as capability-level requirements unless a later sealed readiness source promotes them to exact artifact targets.
* Normalization terminal disposition vocabulary maps to downstream implementation-compatible vocabulary with a dedicated field named `implementation_compatible_disposition`.
* `actual_apply_eligible` maps to downstream target disposition `migrated_to_manifest_authority` only as a future readiness execution target. This normalization round must not claim that migration has already occurred.
* `no_op`, `historical_preserved`, `diagnostic_preserved`, `generated_no_mutation`, `false_positive_no_mutation`, and `blocked` retain the same downstream implementation-compatible spelling.
* readiness plan requirement를 검증 가능한 source binding 없이 compatibility authority로 소비하면 final contract is FAIL이다.
* `cutover_input_usable`과 `handoff_usable`은 prose가 아니라 reconciled manifest와 final contract report의 emitted boolean fields다. 둘 다 candidate predicate only이며 cutover authorization이 아니다.
* final contract / closeout / handoff는 한 final phase에서 생성할 수 있지만, `machine_contract_status`와 `governance_closeout_status`는 분리한다.
* independent adversarial review 전에는 `machine_contract_status=PASS`, `governance_closeout_status=review_pending`, `complete_claim_allowed=false`가 최대 상태다.
* reviewer-independence disclosure는 final claim boundary와 closeout에 포함한다.
* `docs/2105_baseline_consumption_audit_plan.md`는 local readpoint에서 absent로 알려진 risk row이며, actual migrated diff로 세지 않는다.

---

## 5. Repository Areas Affected

### Code

Expected new tooling surfaces:

* `Iris/build/description/v2/tools/build/dvf_3_3_consumer_migration_normalization_common.py`
* `Iris/build/description/v2/tools/build/generate_dvf_3_3_consumer_migration_input_contract.py`
* `Iris/build/description/v2/tools/build/generate_dvf_3_3_consumer_migration_eligibility_matrix.py`
* `Iris/build/description/v2/tools/build/generate_dvf_3_3_missing_path_disposition_ledger.py`
* `Iris/build/description/v2/tools/build/validate_dvf_3_3_consumer_migration_anchor_relocation.py`
* `Iris/build/description/v2/tools/build/generate_dvf_3_3_authority_role_migration_rule_seed.py`
* `Iris/build/description/v2/tools/build/generate_dvf_3_3_downstream_command_surface_compatibility_manifest.py`
* `Iris/build/description/v2/tools/build/generate_dvf_3_3_consumer_migration_reconciled_input_manifest.py`
* `Iris/build/description/v2/tools/build/validate_dvf_3_3_consumer_migration_input_normalization.py`

Expected new focused tests:

* `Iris/build/description/v2/tests/test_dvf_3_3_consumer_migration_input_normalization.py`

### Docs

Plan / closeout / handoff docs:

* `docs/dvf_3_3_vnext_consumer_migration_input_normalization_plan.md`
* `docs/dvf_3_3_vnext_consumer_migration_input_normalization_closeout.md`
* `docs/dvf_3_3_vnext_consumer_migration_input_normalization_handoff_packet.md`
* `docs/dvf_3_3_vnext_consumer_migration_input_normalization_ledger_packet.md`

Read-only authority / context docs:

* `docs/Philosophy.md`
* `docs/DECISIONS.md`
* `docs/ARCHITECTURE.md`
* `docs/ROADMAP.md`
* `docs/dvf_3_3_vnext_consumer_migration_principles.md`
* `docs/dvf_3_3_vnext_current_authority_cutover_tooling_readiness_plan.md`
* `docs/dvf_3_3_vnext_cutover_contract.md`

### Config

Expected unchanged.

* `pytest.ini`
* `Iris/_docs/round3/current_route_required_validations.json`

This round does not add itself, its tools, or its tests to `current_route_required_validations.json` and does not expand the current-route tooling allowlist. If a later implementation requires test discovery plumbing, that change must be planned separately and cannot be counted as consumer migration input normalization.

### Generated Artifacts

All generated artifacts stay under:

* `Iris/build/description/v2/staging/dvf_3_3_vnext_consumer_migration_input_normalization/`

Primary expected artifacts:

* `phase0/source_input_inventory.json`
* `phase0/required_source_inputs.json`
* `phase0/source_matrix_fingerprint_report.json`
* `phase0/source_membership_reconciliation.json`
* `phase0/implementation_scope_boundary.json`
* `phase0/input_contract.md`
* `phase0/disposition_vocabulary.json`
* `phase0/downstream_disposition_vocabulary_map.json`
* `phase0/blocked_reason_allowlist.json`
* `phase0/field_schema.json`
* `phase1/consumer_migration_eligibility_matrix.jsonl`
* `phase1/eligibility_matrix_summary.json`
* `phase1/normalized_row_id_set_report.json`
* `phase2/missing_path_disposition_ledger.jsonl`
* `phase2/missing_path_disposition_summary.json`
* `phase2/missing_apply_eligible_zero_proof.json`
* `phase2/missing_required_path_disposition_ledger.readiness_schema_preview.jsonl`
* `phase2/path_status_single_writer_report.json`
* `phase3/anchor_relocation_validation_report.json`
* `phase3/anchor_relocation_ledger.jsonl`
* `phase3/anchor_freshness_binding_report.json`
* `phase3/anchor_unresolved_ambiguous_zero_proof.json`
* `phase4/authority_role_migration_rule_seed.jsonl`
* `phase4/authority_role_migration_rules.readiness_target_contract.json`
* `phase4/authority_role_rule_seed_summary.json`
* `phase4/rule_seed_coverage.json`
* `phase5/downstream_command_surface_compatibility_manifest.json`
* `phase5/command_surface_mapping.for_current_cutover.target_contract.json`
* `phase5/tool_contract_compatibility_manifest.target_contract.json`
* `phase5/readiness_artifact_target_map.json`
* `phase5/compatibility_source_binding.json`
* `phase5/bound_source_fingerprint_report.json`
* `phase5/bound_source_path_reconciliation.json`
* `phase5/exact_command_validation_registry.json`
* `phase5/exact_command_validation_report.json`
* `phase5/downstream_phase0_field_mapping.json`
* `phase6/consumer_migration_reconciled_input_manifest.json`
* `phase6/row_disposition_ledger.for_readiness.jsonl`
* `phase6/readiness_consumer_migration_bridge_contract.json`
* `phase6/reconciled_input_manifest_validation_report.json`
* `phase6/cross_artifact_reconciliation.json`
* `phase6/cutover_handoff_gate_evaluation.json`
* `phase7/raw_input_direct_consumption_guard_report.json`
* `phase7/protected_surface_no_mutation_verdict.json`
* `phase7/dual_zero_mapping_report.json`
* `phase8/final_normalization_contract_report.json`
* `phase8/blocked_row_report.json`
* `phase8/downstream_tooling_readiness_handoff_packet.md`
* `phase8/closeout_report.md`

---

## 6. Planned Changes

Common tool contract for Changes 1-9:

The implementation should centralize common schema constants, enum allowlists, canonical path normalization, hash calculation, and row-count helpers in `dvf_3_3_consumer_migration_normalization_common.py`. Per-tool local copies of disposition enums, blocked reason enums, gate field names, or source artifact role strings are not allowed except in tests that intentionally check drift detection.

Every generator / validator added by this plan must emit or be covered by a central validator artifact containing these five fields:

* `source_fingerprint_ref` and `source_fingerprint_check`
* `row_count_reconciliation`
* `row_id_set_hash` or explicit `row_id_set_not_applicable_reason`
* `blocked_row_passthrough_count`
* `claim_boundary`

The central final validator owns the PASS / FAIL decision, but it must fail if any phase artifact lacks this five-element contract summary or an explicit not-applicable reason. This prevents individual tools from silently bypassing source freshness, row-count, blocked-row, or claim-boundary checks.

### Change 1 - Phase 0 Input Contract Freeze and Source Fingerprint

Purpose:

정규화가 소비할 read-only source set, row counts, hashes, allowed disposition vocabulary, field schema를 fail-loud contract로 고정한다.

Files:

* `Iris/build/description/v2/tools/build/generate_dvf_3_3_consumer_migration_input_contract.py`
* `Iris/build/description/v2/tests/test_dvf_3_3_consumer_migration_input_normalization.py`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_consumer_migration_input_normalization/phase0/*`

Implementation Notes:

* Input inventory는 `classified_ledger.jsonl`, `change_required_index.md`, `change_forbidden_index.md`, `executing_consumer_impact.md`, `consumer_migration_matrix.jsonl`, `consumer_migration_dry_run.json`을 read-only provenance로 기록한다.
* `required_source_inputs.json` is the canonical source binding artifact. Each row has:
  * `artifact_role`
  * `canonical_path`
  * `required_existence`
  * `allowed_absent`
  * `expected_round`
  * `expected_count`
  * `freshness_requirement`
  * `sha256`
  * `claim_boundary`
* `implementation_scope_boundary.json` is emitted in Phase 0 and repeated by the final report. It must contain:
  * `roadmap_artifact_status`: `draft_not_final`
  * `implementation_allowed_scope`: `core_input_normalization_only`
  * `downstream_target_contract_execution_allowed`: `false`
  * `roadmap_final_approval_required_before_governance_complete`: `true`
  * `consumer_migration_execution_allowed`: `false`
  * `current_cutover_allowed`: `false`
  * `runtime_replacement_allowed`: `false`
  * `package_or_release_readiness_allowed`: `false`
* Minimum artifact roles:
  * `audit_classified_ledger`
  * `audit_change_required_index`
  * `audit_change_forbidden_index`
  * `audit_executing_consumer_impact`
  * `execution_consumer_migration_matrix`
  * `execution_consumer_migration_dry_run`
  * `current_route_required_validation_input`
* Fingerprint는 path, existence, size, sha256, row count, expected count를 포함한다.
* `source_membership_reconciliation.json` compares audit-side `change-required` membership with execution matrix membership.
* Audit-side population source:
  * `classified_ledger.jsonl`
  * `change_required_index.md`
* Execution-side provenance source:
  * `consumer_migration_matrix.jsonl`
* The reconciliation key must be deterministic and should use canonical source artifact role, canonical path, source row identifier if present, line/evidence anchor, consumer type, and migration disposition.
* Membership divergence is not repaired in this phase. It becomes `blocked_apply_eligible` if the divergent row is apply-eligible, otherwise `blocked_non_apply` with `blocked_reason=source_membership_divergence`.
* 7-value terminal disposition vocabulary를 고정한다.
  * `actual_apply_eligible`
  * `no_op`
  * `historical_preserved`
  * `diagnostic_preserved`
  * `generated_no_mutation`
  * `false_positive_no_mutation`
  * `blocked`
* `downstream_disposition_vocabulary_map.json` is created in Phase 0 and consumed by every later phase. It maps:
  * `actual_apply_eligible` -> `migrated_to_manifest_authority`
  * `no_op` -> `no_op`
  * `historical_preserved` -> `historical_preserved`
  * `diagnostic_preserved` -> `diagnostic_preserved`
  * `generated_no_mutation` -> `generated_no_mutation`
  * `false_positive_no_mutation` -> `false_positive_no_mutation`
  * `blocked` -> `blocked`
* The map must include `normalization_claim_boundary` for `actual_apply_eligible`: `future readiness execution target only; not migrated in this normalization round`.
* Any later phase that emits `implementation_compatible_disposition` must use this map exactly. Tool-local vocabulary maps are forbidden.
* Unknown input, row-count mismatch, fingerprint mismatch, unknown disposition, dual-writer candidate는 hard fail한다.
* Phase 0은 `change-required 311`만 normalized row population으로 삼고, `change-forbidden 27558`은 no-mutation denominator로만 기록한다.
* `blocked_reason_allowlist.json` is created in Phase 0 and used by all later phases.
* Blocked rows must carry `blocked_class`:
  * `blocked_apply_eligible` means final contract FAIL.
  * `blocked_non_apply` means executor excluded and may still allow machine PASS if all exclusion predicates are satisfied.
* Initial blocked reason allowlist:
  * `source_fingerprint_mismatch`
  * `source_freshness_failed`
  * `source_membership_divergence`
  * `required_source_absent`
  * `unknown_terminal_disposition`
  * `missing_apply_eligible_path`
  * `anchor_unresolved`
  * `anchor_ambiguous`
  * `rule_seed_missing`
  * `compatibility_source_unbound`
  * `raw_input_direct_consumption`
  * `protected_surface_mutation`
  * `non_apply_missing_provenance`

Validation:

* required source input canonical binding PASS
* source fingerprint PASS
* expected count reconciliation PASS
* audit / execution 311 membership reconciliation PASS
* implementation scope boundary emitted and schema PASS
* `change-required == 311`
* `change-forbidden == 27558`
* ambiguous count 0
* unknown disposition 0
* blocked reason allowlist schema PASS
* field schema lint PASS

---

### Change 2 - Phase 1 Eligibility Matrix Generation

Purpose:

`change-required 311` rows를 executor-safe terminal disposition과 apply eligibility로 재분류한다.

Files:

* `Iris/build/description/v2/tools/build/generate_dvf_3_3_consumer_migration_eligibility_matrix.py`
* `Iris/build/description/v2/tests/test_dvf_3_3_consumer_migration_input_normalization.py`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_consumer_migration_input_normalization/phase1/*`

Implementation Notes:

* 기존 row field는 보존한다.
  * `path`
  * `line`
  * `consumer_type`
  * `current_authority`
  * `migration_disposition`
  * `change_needed_on_rebaseline`
  * `evidence_anchor`
* 새 field를 추가한다.
  * `row_id`
  * `normalized_disposition`
  * `apply_eligibility`
  * `blocked_class`
  * `blocked_reason`
  * `expected_mutation_kind`
  * `authority_role_target`
  * `implementation_compatible_disposition`
  * `anchor_strategy`
  * `path_status_source`
  * `downstream_phase`
  * `readiness_phase3_consumption_role`
  * `readiness_phase5_ledger_role`
  * `ledger_required`
  * `diff_countable`
* `row_id`는 deterministic stable identity다. It must be derived from canonical source artifact role, canonical path, source row identifier if present, line/evidence anchor, consumer type, and migration disposition.
* `apply_eligibility=true`와 `diff_countable=true`는 `actual_apply_eligible`에만 허용한다.
* `change_needed_on_rebaseline=true`는 apply 가능성과 1:1로 해석하지 않는다.
* `implementation_compatible_disposition` is derived from Phase 0 `downstream_disposition_vocabulary_map.json`.
* `readiness_phase3_consumption_role` must be one of `apply_candidate_input`, `missing_path_disposition_input`, `non_apply_reconciled_input`, or `blocked_excluded_input`.
* `readiness_phase5_ledger_role` must be one of `future_row_level_ledger_source`, `non_diff_reconciliation_source`, or `not_ledger_countable`.
* historical / diagnostic / generated / false-positive / no-op rows는 executor input에서 non-apply로 분리한다.
* Phase 1 does not own canonical path existence. It may set `path_status_source=phase2_required`, but Phase 2 is the single writer for canonical `path_status`.
* Any `blocked_reason` must come from Phase 0 `blocked_reason_allowlist.json`.

Validation:

* total normalized rows = 311
* terminal disposition coverage = 311
* unknown disposition = 0
* row-id uniqueness = 311
* row-id set hash emitted
* apply eligibility contradiction = 0
* diff-countable contradiction = 0
* blocked reason enum validation PASS
* no-op / preserve / generated / false-positive row apply eligibility = false
* repeated run output hash deterministic

---

### Change 3 - Phase 2 Missing Path Disposition Ledger

Purpose:

현재 checkout에 없는 path를 actual migration failure나 migrated diff로 오독하지 않도록 별도 disposition ledger로 분리한다.

Files:

* `Iris/build/description/v2/tools/build/generate_dvf_3_3_missing_path_disposition_ledger.py`
* `Iris/build/description/v2/tests/test_dvf_3_3_consumer_migration_input_normalization.py`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_consumer_migration_input_normalization/phase2/*`

Implementation Notes:

* Phase 2 is the single writer for canonical `path_status`.
* Missing path detection reads Phase 1 row identities and actual checkout existence, then writes the only authoritative path-status fields for this round.
* Canonical path-status fields:
  * `path_status`
  * `path_existence_checked_at`
  * `path_existence_basis`
  * `path_status_writer_phase`
  * `path_status_claim_boundary`
* The missing path ledger must also be convertible without reinterpretation to downstream readiness `phase3/missing_required_path_disposition_ledger.jsonl`. Required bridge fields:
  * `audit_row_id`
  * `row_id`
  * `path`
  * `consumer_type`
  * `disposition`
  * `normalized_disposition`
  * `implementation_compatible_disposition`
  * `disposition_reason`
  * `source_evidence_path`
  * `source_evidence_fingerprint`
  * `review_required`
  * `eligible_for_actual_apply`
* Downstream readiness missing-path dispositions are limited to `materialized_from_sealed_evidence`, `blocked_missing_source`, `excluded_non_live_historical_reference`, and `no_op_non_apply`.
* This normalization round may emit `missing_required_path_disposition_ledger.readiness_schema_preview.jsonl` under its own Phase 2 root to prove schema compatibility, but it must not write the downstream readiness Phase 3 ledger.
* Missing row는 `no_op`, `historical_preserved`, `diagnostic_preserved`, `generated_no_mutation`, `false_positive_no_mutation`, `blocked` 중 하나로만 reconciliation한다.
* Missing row 중 `actual_apply_eligible`이 하나라도 있으면 hard fail한다.
* Missing apply-eligible rows must carry `blocked_class=blocked_apply_eligible` and `blocked_reason=missing_apply_eligible_path`.
* Missing non-apply rows must carry `blocked_class=blocked_non_apply` only when provenance is insufficient; otherwise they remain explicit non-apply terminal dispositions and executor excluded.
* `docs/2105_baseline_consumption_audit_plan.md` 관련 row는 actual migrated diff로 세지 않는다.
* `docs/2105_baseline_consumption_audit_plan.md` 관련 missing rows must map to downstream `no_op_non_apply` or `excluded_non_live_historical_reference` unless sealed reconstruction evidence is explicitly added. They must not map to `materialized_from_sealed_evidence` by default.
* Path absence는 delete target, cleanup target, recovery target이 아니다.
* Missing non-apply row는 ledger evidence로 남기되 downstream executor apply set에서 제외한다.

Validation:

* missing apply-eligible row count = 0
* missing diff-countable row count = 0
* all missing rows have terminal disposition
* missing path ledger row count matches Phase 2 canonical path_status
* readiness schema preview row count matches missing path ledger row count
* downstream missing-path disposition enum validation PASS
* Phase 1 row-id set equals Phase 2 row-id set
* apply-eligible row-id set is unchanged except for explicit FAIL on missing apply-eligible
* `docs/2105_baseline_consumption_audit_plan.md` rows are non-apply and non-diff-countable
* negative test for missing apply-eligible hard fail

---

### Change 4 - Phase 3 Deterministic Anchor Relocation Validator

Purpose:

Line-anchor drift로 executor가 잘못된 위치를 변경하거나 실패하지 않도록 deterministic relocation evidence를 만든다.

Files:

* `Iris/build/description/v2/tools/build/validate_dvf_3_3_consumer_migration_anchor_relocation.py`
* `Iris/build/description/v2/tests/test_dvf_3_3_consumer_migration_input_normalization.py`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_consumer_migration_input_normalization/phase3/*`

Implementation Notes:

* Line-only anchor는 direct mutation authority가 아니다.
* Validator consumes Phase 2 canonical `path_status`; it does not independently re-adjudicate path existence.
* Validator는 row별로 Phase 2 `path_status`, expected line content, evidence anchor token, bounded context, deterministic relocation candidates 순서로 검증한다.
* Anchor relocation evidence must bind to current target content freshness:
  * `target_file_sha256`
  * `bounded_context_sha256`
  * `bounded_context_start_line`
  * `bounded_context_end_line`
  * `anchor_freshness_status`
  * `anchor_freshness_claim_boundary`
* Relocation result는 다음 중 하나다.
  * `exact_line_match`
  * `relocated_deterministically`
  * `missing_path_non_apply`
  * `unresolved`
  * `ambiguous`
* `actual_apply_eligible` row는 `exact_line_match` 또는 `relocated_deterministically`만 허용한다.
* Duplicate token, zero candidate, multiple candidate, context mismatch는 fail-loud report로 남긴다.
* Any target file hash or bounded context hash mismatch after relocation evidence generation is a downstream staleness gate failure, not a warning.
* Phase 3 must assert Phase 1 -> Phase 2 -> Phase 3 row-id set equality for all rows and apply-eligible row-id set equality for mutation candidates.

Validation:

* unresolved = 0
* ambiguous = 0
* apply-eligible unresolved = 0
* apply-eligible ambiguous = 0
* missing path apply-eligible = 0
* Phase 3 consumed Phase 2 canonical path_status for all rows
* no independent path-existence writer in Phase 3
* anchor freshness binding PASS
* target file / bounded context fingerprint emitted for every apply-eligible row
* Phase 1 / Phase 2 / Phase 3 row-id set equality PASS
* apply-eligible row-id set equality PASS
* repeated run output hash deterministic
* negative test for duplicate ambiguous anchor

---

### Change 5 - Phase 4 Authority-Role Migration Rule Seed Generator

Purpose:

후속 executor가 numeric replacement가 아니라 authority-role migration을 수행할 수 있도록 mutation rule seed를 만든다.

Files:

* `Iris/build/description/v2/tools/build/generate_dvf_3_3_authority_role_migration_rule_seed.py`
* `Iris/build/description/v2/tests/test_dvf_3_3_consumer_migration_input_normalization.py`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_consumer_migration_input_normalization/phase4/*`

Implementation Notes:

* Rule seed 대상은 `actual_apply_eligible` rows only다.
* Preserve / generated / false-positive / no-op rows는 mutation rule seed에 포함하지 않는다.
* Rule seed는 old literal to new literal 치환표가 아니라 authority role, target handle, expected postcondition, consumer type, allowed path, evidence anchor policy를 포함한다.
* Mandatory fields:
  * `rule_id`
  * `input_consumer_type`
  * `input_current_authority_role`
  * `target_authority_role`
  * `target_authority_handle`
  * `allowed_normalized_disposition`
  * `allowed_migration_disposition`
  * `operation_kind`
  * `allowed_paths`
  * `forbidden_paths`
  * `before_pattern_policy`
  * `after_pattern_policy`
  * `required_before_context_hash`
  * `required_after_anchor_policy`
  * `numeric_replacement_allowed`
  * `legacy_vocabulary_reintroduction_allowed`
  * `requires_evidence_anchor`
  * `expected_postcondition`
  * `readiness_target_rule_path`
  * `normalization_rule_seed_only`
* `allowed_migration_disposition` must use the downstream implementation-compatible vocabulary from Phase 0 and is `migrated_to_manifest_authority` for `actual_apply_eligible` rows.
* `allowed_normalized_disposition` remains `actual_apply_eligible` for source traceability; it is not the downstream executor vocabulary.
* `authority_role_migration_rules.readiness_target_contract.json` records a capability-level future target expectation for a downstream readiness authority-role rule table. It may include the currently expected target path `Iris/build/description/v2/staging/dvf_3_3_vnext_cutover_tooling_readiness/phase3/authority_role_migration_rules.json`, but that path must be marked `path_kind=future_readiness_target`, `materialized_by_this_round=false`, `target_only=true`, and `source_authority=false`.
* The readiness target contract must state that any downstream authority-role rule table preserves the rule fields required by the readiness capability: `rule_id`, `input_consumer_type`, `input_current_authority_role`, `target_authority_role`, `target_authority_handle`, `allowed_migration_disposition`, `operation_kind`, `allowed_paths`, `forbidden_paths`, `before_pattern_policy`, `after_pattern_policy`, `required_before_context_hash`, `required_after_anchor_policy`, `numeric_replacement_allowed=false`, `legacy_vocabulary_reintroduction_allowed=false`, and `requires_evidence_anchor=true`.
* `normalization_rule_seed_only=true` is mandatory in this round's seed artifacts to prevent a seed from being over-read as an executed migration rule table.
* `numeric_replacement_allowed` must be `false`.
* `legacy_vocabulary_reintroduction_allowed` must be `false`.
* Each rule must reference the row-id set or row-id group it covers.
* Any apply-eligible row not covered by a rule seed must become `blocked_apply_eligible` with `blocked_reason=rule_seed_missing`, making final contract FAIL.
* Phase 4 must assert Phase 1 -> Phase 2 -> Phase 3 -> Phase 4 apply-eligible row-id set equality before rule generation.

Validation:

* rule seed rows are subset of actual_apply_eligible rows
* all actual_apply_eligible groups are covered or explicitly blocked
* no blocked apply-eligible rule gaps in PASS state
* apply-eligible row-id set equality PASS
* no hardcoded numeric-only replacement rule
* downstream authority-rule future target metadata and stale-reconciliation policy PASS
* `allowed_migration_disposition` enum validation PASS
* no unknown rule kind
* each rule has expected postcondition
* each rule maps to downstream consumer type
* preserve / generated / false-positive / no-op rows produce no mutation rule

---

### Change 6 - Phase 5 Downstream Command Surface Compatibility Manifest

Purpose:

후속 tooling readiness의 Phase 0 / 4 / 5가 요구하는 command-surface handoff를 field-level로 고정한다.

Files:

* `Iris/build/description/v2/tools/build/generate_dvf_3_3_downstream_command_surface_compatibility_manifest.py`
* `Iris/build/description/v2/tests/test_dvf_3_3_consumer_migration_input_normalization.py`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_consumer_migration_input_normalization/phase5/*`

Implementation Notes:

* Compatibility manifest는 downstream implementation plan body를 수정하지 않고, downstream이 consume할 input mapping만 제공한다.
* `command_surface_mapping.for_current_cutover.target_contract.json` records the expected future downstream readiness target path `Iris/build/description/v2/staging/dvf_3_3_vnext_cutover_tooling_readiness/phase6/command_surface_mapping.for_current_cutover.json` with `path_kind=future_readiness_target`, `materialized_by_this_round=false`, `target_only=true`, and `source_authority=false`.
* This target contract is not the downstream readiness artifact itself and is not source authority for the path. It is a normalization-side expectation and future reconciliation target that the later readiness mapping validator must satisfy or explicitly stale-fail when it emits its implementation-compatible mapping.
* The target contract must state that `command_surface_mapping.for_current_cutover.json` preserves readiness safety fields and includes the fixed implementation Phase 0 fields `validation_family`, `concrete_command_or_tool`, `expected_artifact`, and `blocking_condition`.
* `command_surface_mapping.for_current_cutover.target_contract.json` must also require the full readiness command mapping field set: `command_id`, `validation_family`, `concrete_command_or_tool`, `tool_path`, `mode`, `required_args`, `forbidden_args`, `input_artifacts`, `output_artifacts`, `expected_artifact`, `expected_exit_code`, `blocking_condition`, `mutation_boundary`, `target_kind`, `freshness_inputs`, `schema_refs`, `claim_boundary`, `downstream_phase`, `downstream_artifact`, `readiness_artifact`, and `compatibility_status`.
* `tool_contract_compatibility_manifest.target_contract.json` records a capability-level future expectation for a downstream tool-contract compatibility manifest. If it includes the currently expected target path `Iris/build/description/v2/staging/dvf_3_3_vnext_cutover_tooling_readiness/phase6/tool_contract_compatibility_manifest.json`, that row must be marked `path_kind=future_readiness_target`, `materialized_by_this_round=false`, `target_only=true`, and `source_authority=false`.
* `tool_contract_compatibility_manifest.target_contract.json` must require the downstream readiness fields `fixed_downstream_plan_path`, `fixed_downstream_plan_fingerprint`, `phase0_command_surface_mapping_path`, `downstream_required_validation_families`, `mapped_validation_families`, `unmapped_validation_families`, `readiness_to_downstream_artifact_map`, `runtime_cutover_contract`, `consumer_migration_contract`, `claim_boundary`, and `verdict`.
* `tool_contract_compatibility_manifest.target_contract.json` must list the downstream required validation families expected of the readiness round, including fresh overlay generation, live runtime cutover, runtime restore probe, actual consumer migration executor, row-level ledger, actual diff-to-ledger validator, and command mapping validator.
* Capability-level future expectation rows must include `capability_level_requirement_only=true`, `normalization_owner=false`, and `readiness_round_must_implement=true`.
* Validation families outside consumer migration input normalization are recorded with `normalization_owner=false` and `readiness_round_must_implement=true`; this round must not claim their commands exist.
* `readiness_artifact_target_map.json` must map normalization outputs to the later readiness artifact family without claiming they already exist in the readiness root.
* Required source-to-capability mappings:
  * normalization `phase6/consumer_migration_reconciled_input_manifest.json` -> downstream consumer migration executor input contract and future readiness `consumer_migration_reconciled_input_manifest.json` reconciliation target
  * normalization `phase2/missing_required_path_disposition_ledger.readiness_schema_preview.jsonl` -> downstream missing-path disposition capability contract
  * normalization `phase4/authority_role_migration_rule_seed.jsonl` plus `phase4/authority_role_migration_rules.readiness_target_contract.json` -> downstream authority-role rule table capability contract
  * normalization `phase6/row_disposition_ledger.for_readiness.jsonl` -> downstream row-level migration ledger source contract
  * normalization Phase 3 anchor freshness evidence -> downstream actual diff-to-ledger before-anchor and stable evidence-anchor precondition
* Any path-bearing mapping in `readiness_artifact_target_map.json` must include `path_kind`, `materialized_by_this_round`, `target_only`, `source_authority=false`, and `stale_future_target_behavior=fail_until_reconciled`.
* The generator must fail if it attempts to write outside `Iris/build/description/v2/staging/dvf_3_3_vnext_consumer_migration_input_normalization/`.
* `compatibility_source_binding.json` records the source of every downstream field. It must distinguish:
  * `sealed_contract_source`
  * `fixed_plan_source`
  * `future_handoff_target_only`
* `docs/dvf_3_3_vnext_current_authority_cutover_tooling_readiness_plan.md` is treated as future handoff target unless a later review provides seal evidence. It cannot be the only source authority for a mandatory compatibility field.
* Mandatory compatibility fields must trace to `docs/dvf_3_3_vnext_current_authority_implementation_2105_consumer_migration_plan.md`, `docs/dvf_3_3_vnext_cutover_contract.md`, or another explicitly bound source path/status in `compatibility_source_binding.json`.
* Every `sealed_contract_source` and `fixed_plan_source` row must have an existence and sha256 proof in `bound_source_fingerprint_report.json`.
* `bound_source_path_reconciliation.json` must reconcile the cited implementation-plan path with the actual checkout path and source classification. If the cited path is missing, renamed, or not the intended fixed plan, compatibility manifest status is FAIL.
* `future_handoff_target_only` rows may be included for traceability, but they cannot satisfy mandatory field source requirements by themselves.
* Any mandatory field with only unsealed future-handoff source binding causes compatibility manifest FAIL.
* Mandatory fields:
  * `command_id`
  * `downstream_phase`
  * `validation_family`
  * `concrete_command_or_tool`
  * `tool_path`
  * `mode`
  * `required_args`
  * `forbidden_args`
  * `input_artifacts`
  * `output_artifacts`
  * `expected_artifact`
  * `expected_exit_code`
  * `required_input_artifact`
  * `blocking_condition`
  * `mutation_boundary`
  * `target_kind`
  * `freshness_inputs`
  * `schema_refs`
  * `success_predicate`
  * `claim_boundary`
  * `downstream_artifact`
  * `readiness_artifact`
  * `compatibility_status`
  * `forbidden_interpretation`
* Phase 0 mapping은 command surface inventory, validation family, command exactness, expected artifact mapping을 제공한다.
* Phase 4 mapping은 live runtime chunk cutover command/tool 구현이 아니라 compatibility requirement handoff로만 표현한다.
* Phase 5 mapping은 consumer migration executor input, row-level ledger input, diff-to-ledger validator input을 raw matrix가 아니라 reconciled manifest 중심으로 연결한다.
* Future placeholder는 `handoff_requirement_only`로 표시하고 concrete runnable command처럼 표현하지 않는다.
* `exact_command_validation_registry.json` defines every command that this plan expects to validate. Each command row includes:
  * `command_id`
  * `working_directory`
  * `argv`
  * `expected_exit_code`
  * `expected_artifacts`
  * `schema_checks`
  * `claim_boundary`
* Slash / invocation canonical format is PowerShell-compatible Windows path form unless a tool explicitly requires another argv shape.

Validation:

* compatibility source binding PASS
* bound sealed/fixed source existence PASS
* bound sealed/fixed source sha256 PASS
* implementation plan path reconciliation PASS
* `command_surface_mapping.for_current_cutover.target_contract.json` exists and marks the expected downstream path as `future_readiness_target`
* `command_surface_mapping.for_current_cutover.target_contract.json` includes all fixed readiness command mapping fields
* `tool_contract_compatibility_manifest.target_contract.json` exists and marks any path-bearing row as `future_readiness_target`
* `tool_contract_compatibility_manifest.target_contract.json` includes all fixed readiness compatibility fields
* `readiness_artifact_target_map.json` maps normalization artifacts to downstream capabilities and future readiness reconciliation targets
* every future target row has `materialized_by_this_round=false`, `target_only=true`, `source_authority=false`, and stale-fail behavior
* every capability-level future expectation row has `capability_level_requirement_only=true`
* all downstream required fields present
* no empty `concrete_command_or_tool` for commands already in scope
* handoff-only placeholders are explicitly marked
* each expected artifact has owner phase
* each blocking condition is machine-checkable
* exact command registry schema PASS
* exact command validation PASS
* no downstream implementation plan mutation required

---

### Change 7 - Phase 6 Consumer Migration Reconciled Input Manifest

Purpose:

Phase 0-5 산출물을 후속 executor가 직접 소비할 수 있는 단일 normalized entrypoint로 묶는다.

Files:

* `Iris/build/description/v2/tools/build/generate_dvf_3_3_consumer_migration_reconciled_input_manifest.py`
* `Iris/build/description/v2/tests/test_dvf_3_3_consumer_migration_input_normalization.py`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_consumer_migration_input_normalization/phase6/*`

Implementation Notes:

* Reconciled input manifest includes:
  * source input fingerprints
  * required source input binding refs
  * source membership reconciliation refs
  * `source_matrix_path`
  * `source_matrix_fingerprint`
  * `accepted_row_count`
  * `executing_consumer_row_count`
  * `change_required_row_count`
  * `change_forbidden_row_count`
  * `actual_apply_eligible_row_count`
  * `non_apply_reconciled_row_count`
  * `historical_preserved_row_count`
  * `diagnostic_preserved_row_count`
  * `no_op_row_count`
  * `generated_no_mutation_row_count`
  * `false_positive_no_mutation_row_count`
  * `blocked_row_count`
  * `missing_apply_eligible_row_count`
  * `row_disposition_ledger_path`
  * `actual_diff_ledger_path`
  * `actual_diff_ledger_path_kind`
  * `actual_diff_ledger_materialized_by_this_round`
  * `actual_diff_ledger_target_only`
  * `actual_diff_ledger_source_authority`
  * `actual_diff_ledger_status`
  * `downstream_phase5_consumption_note`
  * `verdict`
  * normalized row counts
  * disposition counts
  * missing path summary
  * anchor relocation summary
  * anchor freshness summary
  * apply-eligible row count
  * missing apply-eligible row count
  * blocked apply-eligible row count
  * blocked non-apply row count
  * blocked row count and reason enum distribution
  * row-id set reconciliation hashes
  * rule seed artifact path
  * compatibility manifest path
  * compatibility source binding path
  * exact command validation registry path
  * `cutover_input_usable`
  * `handoff_usable`
  * `handoff_usage_scope`
  * gate field schema descriptions
  * claim boundary
  * downstream direct mapping
* Required count values are `accepted_row_count=27869`, `executing_consumer_row_count=1062`, `change_required_row_count=311`, and `change_forbidden_row_count=27558`.
* `row_disposition_ledger.for_readiness.jsonl` is emitted as the direct readiness row-disposition bridge. Each row must include `row_id`, `audit_row_id`, `source_matrix_path`, `path`, `consumer_type`, `normalized_disposition`, `implementation_compatible_disposition`, `apply_eligibility`, `diff_countable`, `ledger_required`, `evidence_anchor`, `anchor_strategy`, `path_status`, `rule_seed_ref`, and `claim_boundary`.
* `row_disposition_ledger_path` points to normalization `phase6/row_disposition_ledger.for_readiness.jsonl`.
* `actual_diff_ledger_path` is present for downstream schema compatibility and records the currently expected future readiness target `Iris/build/description/v2/staging/dvf_3_3_vnext_cutover_tooling_readiness/phase4/actual_diff_to_ledger_report.json`.
* `actual_diff_ledger_path_kind=future_readiness_target`, `actual_diff_ledger_materialized_by_this_round=false`, `actual_diff_ledger_target_only=true`, and `actual_diff_ledger_source_authority=false` are mandatory whenever `actual_diff_ledger_path` is emitted.
* `actual_diff_ledger_status` must be `downstream_readiness_generated_after_apply`. It is not evidence that an actual diff or migration has been produced in this normalization round.
* `downstream_phase5_consumption_note` must state that downstream Phase 5 consumes the readiness-owned Phase 3 row-level ledger and Phase 4 diff-to-ledger report after the readiness executor runs; this normalization manifest is the source contract, not completion evidence.
* `readiness_consumer_migration_bridge_contract.json` records the currently expected future target path `Iris/build/description/v2/staging/dvf_3_3_vnext_cutover_tooling_readiness/phase6/consumer_migration_reconciled_input_manifest.json` with `path_kind=future_readiness_target`, `materialized_by_this_round=false`, `target_only=true`, and `source_authority=false`. It requires that a later readiness manifest preserve the mandatory fields above while replacing target-only diff/ledger paths with produced readiness evidence.
* The later readiness manifest must report `blocked_row_count=0` and `missing_apply_eligible_row_count=0` before this normalization handoff may be considered compatible.
* Raw `change_required_index.md` and raw `consumer_migration_matrix.jsonl` are provenance input only.
* The manifest must fail if referenced artifact hashes do not match Phase 0 fingerprint records.
* Blocked rows may exist only if every blocked row is non-apply and explicitly excluded from executor input.
* Any blocked apply-eligible row makes the manifest unusable.
* `cutover_input_usable` and `handoff_usable` are candidate predicates only, not cutover authorization.
* The manifest schema description for `cutover_input_usable` must repeat: `candidate predicate only; not cutover authorization`.
* The manifest schema description for `handoff_usable` must repeat: `downstream tooling-readiness input only; not migration completion`.
* Computation rule:
  * `blocked_apply_eligible_count == 0`
  * `missing_apply_eligible_count == 0`
  * `anchor_unresolved_count == 0`
  * `anchor_ambiguous_count == 0`
  * `anchor_freshness_status == PASS`
  * `cross_artifact_reconciliation == PASS`
  * `compatibility_source_binding == PASS`
  * `change_forbidden_mutation_candidate == 0`
  * `raw_input_direct_consumption_candidate == 0`
* If all predicates pass, the manifest emits:
  * `cutover_input_usable=true`
  * `handoff_usable=true`
  * `handoff_usage_scope=downstream_tooling_readiness_input_only`
  * `claim_boundary=candidate predicate only; not cutover authorization`
* If any predicate fails, `handoff_usable=false`; `cutover_input_usable` must also be false unless the failure is explicitly outside cutover-input eligibility and documented.

Validation:

* referenced artifacts exist
* artifact hashes match source fingerprint report
* total normalized rows = 311
* terminal disposition coverage = 311
* missing apply-eligible row count = 0
* unresolved anchor count = 0
* ambiguous anchor count = 0
* anchor freshness status PASS
* row-id set equality PASS across Phase 1-6
* source membership reconciliation PASS
* blocked reason enum validation PASS
* blocked apply-eligible count = 0
* compatibility source binding PASS
* change-forbidden mutation candidate = 0
* `cutover_input_usable` emitted
* `handoff_usable` emitted
* `handoff_usage_scope` emitted
* cross-artifact fingerprint / row-count reconciliation PASS
* downstream readiness Phase 6 manifest schema compatibility PASS
* `row_disposition_ledger.for_readiness.jsonl` schema PASS
* `actual_diff_ledger_status=downstream_readiness_generated_after_apply`
* `actual_diff_ledger_path_kind=future_readiness_target`
* `actual_diff_ledger_materialized_by_this_round=false`
* `actual_diff_ledger_target_only=true`
* `actual_diff_ledger_source_authority=false`
* readiness bridge future target metadata and stale-reconciliation policy PASS

---

### Change 8 - Phase 7 Raw Input Direct-Consumption Guard and No-Mutation Verdict

Purpose:

후속 executor가 raw matrix를 우회 소비하거나 protected current authority surface를 변경하는 경로를 fail-loud로 막는다.

Files:

* `Iris/build/description/v2/tools/build/validate_dvf_3_3_consumer_migration_input_normalization.py`
* `Iris/build/description/v2/tests/test_dvf_3_3_consumer_migration_input_normalization.py`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_consumer_migration_input_normalization/phase7/*`

Implementation Notes:

* Validator checks artifacts produced by this round: compatibility manifests, handoff packets, command registries, final reports, and generated docs must not name raw provenance files as executable migration input.
* This guard does not prove future unseen executor behavior. It only proves that this round's emitted compatibility / handoff artifacts route execution through `consumer_migration_reconciled_input_manifest.json`.
* Raw `change_required_index.md`, raw `consumer_migration_matrix.jsonl`, raw dry-run file을 direct executable input으로 지정하는 emitted route는 hard fail한다.
* Protected surface no-mutation verdict는 current `data/`, `output/`, live runtime chunk, package output, Lua bridge payload를 확인한다.
* Support-surface changes are not consumer migration rows and cannot be counted as migrated diffs.
* This phase may produce guard reports but must not mutate protected current surfaces.
* Dual-zero mapping for this offline round:
  * `static_protected_surface_residue_count == 0` maps to no forbidden references in emitted executable input routes and no protected surface hash mutation.
  * `dynamic_runtime_reach_count == "N/A"` because this round does not produce or execute runtime payloads.
  * `staging_write_escape_count == 0` substitutes for dynamic reach in this build-time scope.
* Any runtime dynamic reach claim in this phase is invalid and must fail claim-boundary lint.

Validation:

* raw input direct-consumption guard PASS
* protected surface no-mutation PASS
* static protected surface residue count = 0
* dynamic runtime reach explicitly N/A
* staging write escape count = 0
* changed protected surface count = 0
* support-surface diff not counted as consumer migration
* no package output mutation
* no runtime Lua payload mutation

---

### Change 9 - Phase 8 Final Contract, Tests, Closeout, and Handoff

Purpose:

정규화 라운드를 PASS / FAIL로 닫고, 후속 tooling readiness가 consume할 handoff packet을 만든다.

Files:

* `Iris/build/description/v2/tools/build/validate_dvf_3_3_consumer_migration_input_normalization.py`
* `Iris/build/description/v2/tests/test_dvf_3_3_consumer_migration_input_normalization.py`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_consumer_migration_input_normalization/phase8/*`
* `docs/dvf_3_3_vnext_consumer_migration_input_normalization_closeout.md`
* `docs/dvf_3_3_vnext_consumer_migration_input_normalization_handoff_packet.md`
* `docs/dvf_3_3_vnext_consumer_migration_input_normalization_ledger_packet.md`

Implementation Notes:

* Final contract report PASS requires:
  * all required artifacts exist
  * required source input canonical binding PASS
  * source membership reconciliation PASS
  * source fingerprint PASS
  * disposition coverage 311 / 311
  * missing apply-eligible 0
  * unresolved anchor 0
  * ambiguous anchor 0
  * anchor freshness PASS
  * row-id set reconciliation PASS
  * blocked apply-eligible 0
  * change-forbidden mutation candidate 0
  * implementation scope boundary PASS
  * compatibility source binding PASS
  * bound sealed/fixed compatibility source existence + sha256 PASS
  * implementation plan path reconciliation PASS
  * exact `command_surface_mapping.for_current_cutover.json` downstream target contract PASS
  * `tool_contract_compatibility_manifest.json` downstream target contract PASS
  * readiness Phase 3 / 4 / 6 artifact target map PASS
  * readiness consumer migration reconciled input manifest schema compatibility PASS
  * all path-bearing future target rows include `path_kind=future_readiness_target`, `materialized_by_this_round=false`, `target_only=true`, and `source_authority=false`
  * all capability-level future expectation rows include `capability_level_requirement_only=true`, `normalization_owner=false`, and `readiness_round_must_implement=true`
  * `cutover_input_usable` emitted
  * `handoff_usable` emitted
  * exact command validation PASS
  * focused unit / contract tests exit code 0
  * protected surface no-mutation PASS
  * downstream compatibility manifest required fields complete
  * raw input direct-consumption guard PASS
* Final contract report emits separated state axes:
  * `roadmap_artifact_status`: `draft_not_final`
  * `implementation_allowed_scope`: `core_input_normalization_only`
  * `downstream_target_contract_execution_allowed`: `false`
  * `roadmap_final_approval_required_before_governance_complete`: `true`
  * `machine_contract_status`: `PASS|FAIL`
  * `governance_closeout_status`: `review_pending|complete|blocked`
  * `handoff_usable`: `true|false`
  * `handoff_usage_scope`: `downstream_tooling_readiness_input_only`
  * `independent_review_required_for_complete`: `true`
  * `complete_claim_allowed`: `true|false`
* Before independent adversarial review, the maximum positive state is:
  * `machine_contract_status=PASS`
  * `governance_closeout_status=review_pending`
  * `handoff_usable=true`
  * `complete_claim_allowed=false`
* Negative tests include:
  * fingerprint mismatch
  * missing apply-eligible
  * ambiguous anchor
  * dual-writer candidate
  * numeric replacement fallback
  * raw input direct consumption
* Closeout text must state that this is not consumer migration completion, current authority adoption, runtime cutover, package readiness, or release readiness.
* Independent adversarial review handoff / reviewer-independence disclosure is required before closeout can claim `complete`.

Validation:

* final normalization contract report emits `machine_contract_status`
* final normalization contract report emits `governance_closeout_status`
* final normalization contract report emits `complete_claim_allowed`
* exact command validation PASS
* focused unit / contract tests exit code 0
* no-mutation verdict PASS
* blocked row report machine-readable
* handoff packet references reconciled manifest, not raw matrix
* handoff packet references `handoff_usable` and `handoff_usage_scope`
* claim-boundary lint PASS

---

## 7. Validation Plan

### Automated Validation

Expected exact validation commands after implementation:

* `python -B Iris\build\description\v2\tools\build\generate_dvf_3_3_consumer_migration_input_contract.py`
* `python -B Iris\build\description\v2\tools\build\generate_dvf_3_3_consumer_migration_eligibility_matrix.py`
* `python -B Iris\build\description\v2\tools\build\generate_dvf_3_3_missing_path_disposition_ledger.py`
* `python -B Iris\build\description\v2\tools\build\validate_dvf_3_3_consumer_migration_anchor_relocation.py`
* `python -B Iris\build\description\v2\tools\build\generate_dvf_3_3_authority_role_migration_rule_seed.py`
* `python -B Iris\build\description\v2\tools\build\generate_dvf_3_3_downstream_command_surface_compatibility_manifest.py`
* `python -B Iris\build\description\v2\tools\build\generate_dvf_3_3_consumer_migration_reconciled_input_manifest.py`
* `python -B Iris\build\description\v2\tools\build\validate_dvf_3_3_consumer_migration_input_normalization.py`
* `python -B -m unittest discover -s Iris\build\description\v2\tests -p "test_*.py"`

Required automated gates:

* required source input canonical binding
* audit / execution 311 membership reconciliation
* source fingerprint and row-count reconciliation
* terminal disposition coverage
* blocked reason enum validation
* missing apply-eligible zero proof
* path-existence single-writer validation
* anchor unresolved / ambiguous zero proof
* anchor freshness / bounded context fingerprint validation
* row-id set equality validation
* rule seed schema and numeric replacement rejection
* compatibility source binding validation
* bound sealed/fixed source existence and sha256 validation
* implementation plan path reconciliation validation
* downstream compatibility manifest required fields
* exact command validation registry schema
* reconciled input manifest cross-artifact reconciliation
* `cutover_input_usable` / `handoff_usable` emitted field validation
* `machine_contract_status` / `governance_closeout_status` split validation
* raw input direct-consumption guard
* dual-zero mapping validation
* protected surface no-mutation verdict
* exact command validation
* focused negative tests

### Manual Validation

* Review eligibility matrix disposition distribution.
* Review all missing path rows, especially `docs/2105_baseline_consumption_audit_plan.md`.
* Review every blocked row and confirm no blocked row is apply-eligible.
* Review blocked reason enum distribution and blocked class handling.
* Review required source input canonical paths and freshness bindings.
* Review audit classified ledger / change-required index membership against execution consumer migration matrix membership.
* Review anchor freshness binding for apply-eligible rows.
* Review compatibility manifest against downstream Phase 0 / 4 / 5 needs.
* Review readiness Phase 3 / 4 / 6 artifact target map against `docs/dvf_3_3_vnext_current_authority_cutover_tooling_readiness_plan.md` as a future reconciliation target, not source authority.
* Review `row_disposition_ledger.for_readiness.jsonl`, `readiness_consumer_migration_bridge_contract.json`, and `tool_contract_compatibility_manifest.target_contract.json` for downstream schema compatibility and target-only metadata.
* Review compatibility source binding so unsealed future handoff target is not the only mandatory field source.
* Review bound sealed/fixed source existence, sha256, and implementation-plan path reconciliation.
* Review emitted `cutover_input_usable`, `handoff_usable`, `machine_contract_status`, and `governance_closeout_status`.
* Review final closeout claim boundary and reviewer-independence disclosure.
* Review handoff packet to ensure downstream tooling readiness consumes `consumer_migration_reconciled_input_manifest.json`.

### Validation Limits

This plan will not validate:

* live runtime chunk replacement
* actual consumer migration completion
* full runtime equivalence
* package release readiness
* deployment readiness
* Workshop readiness
* manual in-game validation
* Browser / Wiki / Tooltip behavior validation
* external mod compatibility sweep
* successor baseline identity final seal
* multiplayer behavior
* long-session runtime behavior
* `change_forbidden 27558` row reclassification

---

## 8. Risk Surface Touch

### Authority Surface

Limited impact.

This plan creates a normalized downstream input contract surface for tooling-readiness consumption. It is not a second authority and does not change live runtime authority, current source authority, rendered authority, Lua bridge authority, or docs-canon authority.

### Runtime Behavior Surface

None.

Runtime Lua, chunk manifest, chunk files, Lua bridge payload, Browser / Wiki / Tooltip behavior are not changed.

### Compatibility Surface

Moderate build-time compatibility impact.

The downstream Phase 0 / 4 / 5 command-surface compatibility contract must be complete enough that later tooling readiness can consume the reconciled input manifest without raw input reinterpretation. Mandatory compatibility fields must have source binding, and unsealed future handoff target text cannot be the only source for a mandatory field.

### Read-Only Provenance Artifact Surface

Additive only.

Existing sealed artifacts are read-only provenance inputs. New evidence is written only under `Iris/build/description/v2/staging/dvf_3_3_vnext_consumer_migration_input_normalization/`.

### Public-Facing Output Surface

None.

No tooltip, browser text, wiki text, package output, release note, or Workshop-facing output is changed.

---

## 9. Risk Analysis

### Architecture Risk

* Raw audit rows may be treated as executable instructions instead of provenance input.
* The normalized manifest may accidentally become a second authority instead of a downstream input contract.
* Compatibility manifest may drift into downstream implementation plan mutation.
* Compatibility manifest mandatory fields may become unverifiable if their source binding points only to an unsealed future handoff target.
* Downstream readiness may emit a correctly shaped compatibility manifest but miss the expected `phase6/command_surface_mapping.for_current_cutover.json` future reconciliation target unless this round records target-only metadata and stale-fail behavior.
* Downstream readiness may generate `consumer_migration_reconciled_input_manifest.json` with incompatible row disposition vocabulary unless this round emits the implementation-compatible vocabulary map and bridge ledger.
* Downstream readiness Phase 3 may be forced to reinterpret missing-path rows if this round does not emit the readiness missing-ledger schema preview.
* Downstream readiness Phase 4 diff-to-ledger validation may lack stable before-anchor inputs if this round does not bind anchor freshness into the bridge contract.
* Bound source paths may be phantom, renamed, or different from the intended fixed plan unless existence and sha256 reconciliation is performed.
* Rule seed may collapse authority-role migration into numeric replacement.
* Current-route tooling allowlist may be silently expanded if validation tooling is misclassified as current core.
* Machine contract PASS may be over-read as governance complete unless state axes remain separated.

### Runtime Risk

* Direct runtime risk is low because runtime surfaces are out of scope.
* Indirect risk exists if no-mutation checks fail to include live runtime chunks, package output, or bridge payload.
* A misleading closeout could cause later operators to treat this normalization pass as runtime cutover readiness.

### Compatibility Risk

* Missing path rows may be mistaken for failed migration instead of non-apply disposition.
* Line-anchor drift may cause a later executor to mutate the wrong occurrence.
* Historical / diagnostic / generated rows may be promoted to current hard gates.
* Downstream Phase 0 / 4 / 5 may lack required fields if compatibility manifest schema is too weak.
* Downstream Phase 0 / 4 / 5 cannot gate handoff if `cutover_input_usable` and `handoff_usable` are missing or prose-only.
* Shell / path exactness may differ across Windows command invocation forms.
* Anchor evidence may become stale if target file / bounded context fingerprints are not checked.

### Regression Risk

* Row-count mismatch may hide stale source input.
* Count-only reconciliation may pass while row-id sets drift.
* Audit 311 and execution matrix 311 may have equal counts but divergent membership if `source_membership_reconciliation.json` is skipped.
* Blocked non-apply rows may be confused with successful apply rows.
* `cutover_input_usable=true` may be over-read as cutover authorization.
* Dry-run evidence may be inherited as functional migration completion evidence.
* Protected current surfaces may be touched by support tooling unless hash boundaries are checked before and after execution.

---

## 10. Rollback Plan

All implementation artifacts are additive and staging-scoped.

If validation fails:

* Delete or archive only the dedicated staging root for this round:
  * `Iris/build/description/v2/staging/dvf_3_3_vnext_consumer_migration_input_normalization/`
* Re-run from Phase 0 source fingerprint after fixing the tool or schema.
* Revert only newly added input-normalization tools / tests / docs from this plan's change boundary.
* Do not modify source facts, decisions, rendered output, Lua bridge payload, runtime chunks, package output, or existing sealed evidence to make validation pass.
* If protected surface no-mutation fails, stop the round and investigate the mutation before regenerating artifacts.
* If any blocked apply-eligible row exists, mark final contract `FAIL` and do not emit a usable downstream handoff packet.
* If audit / execution 311 membership reconciliation fails, mark `machine_contract_status=FAIL` and do not synthesize row membership.
* If required source input binding or compatibility source binding fails, mark `machine_contract_status=FAIL`.
* If bound sealed/fixed compatibility source existence or sha256 verification fails, mark `machine_contract_status=FAIL`.
* If final contract report is not PASS, set `handoff_usable=false`, `cutover_input_usable=false`, and prevent downstream tooling readiness from consuming the manifest as complete.
* If machine contract passes but independent review has not completed, keep `governance_closeout_status=review_pending` and `complete_claim_allowed=false`.

---

## 11. Governance Constraints

* `docs/Philosophy.md` compliance is mandatory.
* Runtime / build-time separation must remain intact.
* FAIL-LOUD behavior is required for mismatch, ambiguity, missing apply-eligible rows, and forbidden mutation candidates.
* Current authority ownership must not be bypassed.
* Single-writer authority must be preserved.
* Sealed readpoints are immutable provenance inputs.
* Successor-not-recovery language must be preserved.
* Staging-before-promotion must be preserved.
* Existing chunks and successor chunks must not be described as dual current authority.
* Dry-run evidence must not be interpreted as actual migration completion.
* Historical / diagnostic / generated rows must not be promoted to current apply targets without separate approval.
* `change_forbidden` row mutation count must remain 0.
* `active / silent` may be treated only as historical / diagnostic / import alias vocabulary in this scope.
* `adopted / unadopted` remains current runtime vocabulary and must not be remapped by numeric replacement.
* Missing path absence is not a cleanup instruction.
* Deterministic anchor relocation evidence is required before any apply-eligible row can become executor input.
* Source input canonical path / role / freshness binding is mandatory before any normalized manifest claim.
* Audit-side 311 population and execution-matrix 311 population must reconcile by membership, not count only.
* Compatibility manifest mandatory fields require source binding and cannot rely only on an unsealed future handoff target.
* Bound sealed/fixed compatibility sources must pass existence and sha256 verification.
* Downstream implementation-compatible disposition vocabulary must be emitted separately from internal normalization vocabulary.
* Readiness Phase 3 / 4 / 6 artifact target contracts must treat paths from `docs/dvf_3_3_vnext_current_authority_cutover_tooling_readiness_plan.md` as future reconciliation targets, not sealed source authority.
* This normalization round's readiness target contracts are prerequisites only; downstream tooling readiness remains the single writer for its staging artifacts and actual executor evidence.
* `cutover_input_usable` and `handoff_usable` must be emitted machine-readable fields and candidate predicates only.
* `machine_contract_status` and `governance_closeout_status` must remain separate.
* Shared schema constants / enum allowlists / path normalization helpers should be centralized to prevent tool-local drift.
* Downstream implementation plan body is fixed; this round emits compatibility input rather than editing downstream plan text.
* This round must not write downstream tooling-readiness staging artifacts; it only records target-only future reconciliation metadata for the later `phase6/command_surface_mapping.for_current_cutover.json` writer.
* This round does not modify `Iris/_docs/round3/current_route_required_validations.json` and does not expand current-route tooling allowlist.
* Independent adversarial review / reviewer-independence disclosure is required before `complete` closeout claim.

---

## 12. Expected Closeout State

Expected closeout target before independent review: `machine_contract_status=PASS` and `governance_closeout_status=review_pending`.

Expected closeout target after independent review: `governance_closeout_status=complete`, only if all contract gates pass and independent review handoff / reviewer-independence disclosure is present.

Machine PASS means:

* `change-required 311` all have a terminal normalized disposition.
* `actual_apply_eligible` is narrower than `change-required`.
* Required source input canonical binding is PASS.
* Audit / execution 311 membership reconciliation is PASS.
* Missing apply-eligible row count is 0.
* `docs/2105_baseline_consumption_audit_plan.md` related missing rows are non-apply and non-diff-countable.
* Anchor relocation unresolved count is 0.
* Anchor relocation ambiguous count is 0.
* Anchor freshness binding is PASS.
* Phase 1-6 row-id set reconciliation is PASS.
* Authority-role migration rule seed covers allowed apply-eligible groups without numeric replacement.
* `roadmap_artifact_status=draft_not_final`.
* `implementation_allowed_scope=core_input_normalization_only`.
* `downstream_target_contract_execution_allowed=false`.
* `roadmap_final_approval_required_before_governance_complete=true`.
* Compatibility source binding is PASS.
* Bound sealed/fixed compatibility source existence and sha256 verification are PASS.
* Implementation plan path reconciliation is PASS.
* Downstream Phase 0 / 4 / 5 compatibility manifest is complete.
* `command_surface_mapping.for_current_cutover.target_contract.json` records the expected `Iris/build/description/v2/staging/dvf_3_3_vnext_cutover_tooling_readiness/phase6/command_surface_mapping.for_current_cutover.json` future target with `path_kind=future_readiness_target`, `materialized_by_this_round=false`, `target_only=true`, and stale-fail behavior.
* `tool_contract_compatibility_manifest.target_contract.json` records capability-level compatibility expectations and marks any path-bearing future row with `path_kind=future_readiness_target`, `materialized_by_this_round=false`, `target_only=true`, and stale-fail behavior.
* `readiness_artifact_target_map.json` covers the primary downstream surfaces and labels non-primary readiness internals as capability-level requirements unless a later sealed source promotes them.
* `readiness_consumer_migration_bridge_contract.json` records the expected `Iris/build/description/v2/staging/dvf_3_3_vnext_cutover_tooling_readiness/phase6/consumer_migration_reconciled_input_manifest.json` future target with target-only metadata and schema validation.
* `row_disposition_ledger.for_readiness.jsonl` is complete and uses `implementation_compatible_disposition`.
* Future target metadata final gate is PASS for every path-bearing future row.
* Capability-level requirement marker final gate is PASS for every capability-level future expectation row.
* Exact command validation registry is complete.
* `consumer_migration_reconciled_input_manifest.json` is the only downstream normalized entrypoint.
* `cutover_input_usable=true` and `handoff_usable=true` are emitted candidate predicates.
* `handoff_usage_scope=downstream_tooling_readiness_input_only`.
* `machine_contract_status=PASS`.
* Raw input direct-consumption guard passes.
* Protected surface no-mutation verdict passes.
* Handoff packet is usable by downstream tooling readiness.

Governance complete additionally means:

* `governance_closeout_status=complete`.
* `complete_claim_allowed=true`.
* independent adversarial review accepted the evidence or explicitly cleared reviewer-independence conflict.
* closeout and ledger packet retain the no-migration / no-cutover / no-release claim boundary.

Before independent review, the expected positive state is:

```json
{
  "roadmap_artifact_status": "draft_not_final",
  "implementation_allowed_scope": "core_input_normalization_only",
  "downstream_target_contract_execution_allowed": false,
  "roadmap_final_approval_required_before_governance_complete": true,
  "machine_contract_status": "PASS",
  "governance_closeout_status": "review_pending",
  "handoff_usable": true,
  "handoff_usage_scope": "downstream_tooling_readiness_input_only",
  "independent_review_required_for_complete": true,
  "complete_claim_allowed": false
}
```

If any required machine gate fails, expected closeout becomes `blocked`, not `partial complete`.

Blocked closeout examples:

* missing apply-eligible row count > 0
* unresolved / ambiguous apply-eligible anchor > 0
* required source input binding fails
* audit / execution 311 membership reconciliation fails
* source freshness binding fails
* source fingerprint mismatch
* unknown terminal disposition
* blocked apply-eligible row exists
* hardcoded numeric replacement rule seed emitted
* implementation scope boundary missing or widened beyond `core_input_normalization_only`
* `downstream_target_contract_execution_allowed` is not `false`
* `roadmap_artifact_status` is not `draft_not_final` before final approval
* compatibility source binding fails
* bound sealed/fixed compatibility source verification fails
* `cutover_input_usable` / `handoff_usable` field missing
* machine / governance state axes missing or collapsed
* raw input direct-consumption guard fails
* protected surface mutation detected
* downstream compatibility manifest lacks mandatory fields
* `command_surface_mapping.for_current_cutover` target contract missing target-only metadata, stale-fail behavior, or required schema fields
* `tool_contract_compatibility_manifest` target contract missing target-only metadata, stale-fail behavior, or required capability fields
* readiness Phase 3 / 4 / 6 artifact target map missing, stale, or treating future target paths as source authority
* any path-bearing future target row lacks `path_kind=future_readiness_target`, `materialized_by_this_round=false`, `target_only=true`, or `source_authority=false`
* any capability-level future expectation row lacks `capability_level_requirement_only=true`
* readiness consumer migration bridge contract missing mandatory `consumer_migration_reconciled_input_manifest.json` fields
* `implementation_compatible_disposition` missing or not mapped from Phase 0 vocabulary map
* independent review handoff is absent when trying to claim governance complete

Maximum final claim:

```text
consumer migration executor와 downstream cutover tooling이 소비할 input normalization,
row disposition, anchor relocation, authority-role rule seed, and command compatibility handoff
are machine-validated as staging evidence for downstream tooling-readiness input.
```

This final claim does not authorize consumer migration execution, current authority adoption, runtime cutover, successor identity final seal, package readiness, release readiness, or public-facing behavior acceptance. Governance complete requires the separate independent review state axis.
