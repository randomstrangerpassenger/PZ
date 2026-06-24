# Implementation Plan

> Status: planned / WARN review incorporated / Problem 7 repair-packet verification plan / current codebase readpoint incorporated / authorized reconnect evidence exists / no release or deployment readiness claim
> 작성일: 2026-06-21
> 상위 기준: `docs/Philosophy.md`, `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`
> Execution 기준: `docs/EXECUTION_CONTRACT.md` / sha256 `A185BBD78EB849B0310D9AADC9102CB156B892513266FAC0EC7903EB3D3A9493`
> Template input: `docs/PLAN_TEMPLATE.md` / sha256 `38D70D4D624733DB4D24F047E0B737A47C75522A967C84F06FE5AABC5EBD9BA1`
> Roadmap input: `C:/Users/MW/.codex/attachments/fe094bbb-91c3-4bee-9121-1cf8dda91002/pasted-text.txt` / sha256 `1FC8E614DF22ED4F6459AFE6C53FD3FF157F1CB8294C0B44ACFF45ABA74FFAEB` / provisional drafting input until canonical docs roadmap artifact is materialized
> Review input: `C:/Users/MW/.codex/attachments/a3d8ba15-d982-4d0e-82f7-f6f70c398e6a/pasted-text.txt` / sha256 `9AE6824FBCD62FCE4EC5F6E8BEB4C0BA76D4C0B697D95341AD101BBBAFB7E314`
> FAIL review input: `C:/Users/MW/.codex/attachments/7c238b52-ce5c-4423-bcaf-882ee22e9ddc/pasted-text.txt` / sha256 `ADC90E6E036B298554670E4BF6DC2F2AD8C2CCA4D845D878710011BC5661156B`
> WARN review input: `C:/Users/MW/.codex/attachments/24fcf40d-c9cf-46b9-a892-85f848ea4ab4/pasted-text.txt` / sha256 `62C2922CC6BCF26675D50A3FED9273C118CBB9B3DBF4A4D80E295A4E0FB46FB7`
> Current codebase readpoint: 2026-06-23 / live facts, decisions, and overlay each contain 2105 rows / focused repair validation passed 6 tests / focused witness validation passed 27 tests
> Current repair evidence: `Iris/build/description/v2/staging/dvf_3_3_current_route_baseline_source_overlay_repair/phase7/final_current_route_baseline_source_overlay_repair_predecessor_report.json` reports `status=PASS`, `implementation_plan_ready=true`, `bounded_repair_packet_complete=true`, `closeout_state=partial`
> Provenance alignment warning: current repair runner still references `docs/dvf_3_3_current_route_baseline_source_overlay_repair_plan.md`; this restored Problem 7 plan is `docs/dvf_3_3_current_route_baseline_source_overlay_repair_problem7_plan.md`. Canonical seal requires explicit plan-path reconciliation.
> Evidence root target: `Iris/build/description/v2/staging/dvf_3_3_current_route_baseline_source_overlay_repair/`

---

## 1. Objective

DVF 3-3 full current-route build surface가 이미 채택된 vNext Baseline의 live current-route materialization을 공식 input으로 다시 소비하지 못했던 문제를 현재 코드베이스 readpoint 기준으로 재검증하고, 이미 존재하는 authorized reconnect / repair packet evidence가 Problem 7 claim boundary 안에서 충분한지 판정한다.

이 계획은 vNext Baseline을 재정의하거나 새 baseline을 만드는 계획이 아니다. Repair target은 adopted vNext Baseline 자체가 아니라 current route가 실제로 읽는 live materialized files와 그 소비 경로다. 2026-06-23 readpoint에서는 authorized reconnect evidence가 이미 존재하므로, 이 계획의 현재 역할은 추가 live write 실행이 아니라 live 2105 materialization, overlay coverage, compose/current-authority/Layer4 trace alignment, authorization/review, and provenance alignment를 검증하는 것이다.

원래 broad / full current-route failure는 denominator, terminal disposition, shared disposition consumption, live migration readiness 실패가 아니라 다음 build-input contract 불일치로 읽었다.

```text
CURRENT_FACTS=6 vs expected 2105
runtime-adopted Base.CanOpener missing body_source_overlay
compose / current-authority / Layer4 trace baseline-source-overlay contract divergence
```

Iris 코드베이스 확인 결과, current route는 추상 baseline 선언이 아니라 live `data/` paths를 직접 읽는다. 원래 hypothesis는 `data/dvf_3_3_input_manifest.json` 및 `data/dvf_3_3_overlay_support.jsonl`이 2105 successor current authority 쪽을 가리키는 반면, live `data/dvf_3_3_facts.jsonl`과 `data/dvf_3_3_decisions.jsonl`이 6-entry fixture universe로 돌아간 split materialization일 수 있다는 것이었다. 2026-06-23 readpoint에서는 live facts / decisions / overlay가 모두 2105로 맞고 focused validation이 PASS하므로, 이 hypothesis는 "현존 failure"가 아니라 "해소된 predecessor failure / regression guard input"으로 다룬다.

이 계획의 최대 claim은 다음으로 제한한다.

```text
Current codebase evidence verifies whether the predecessor full current-route
failure has been resolved by the bounded authorized repair packet. This plan
may claim a sealed bounded repair packet only if live facts/decisions/overlay
match the 2105 manifest, source/runtime row identity and overlay coverage pass,
authorization and independent review evidence are present, and plan-path
provenance is reconciled. It does not claim release readiness, deployment
readiness, package readiness, manual QA, canonical PASS for unrelated surfaces,
or adopted required-gate mutation.
```

이 계획은 source facts 재판정, rendered promotion, runtime chunk replacement, Phase 4 live migration execution, package route mutation, release readiness, Workshop readiness, B42 readiness, manual in-game QA를 선언하지 않는다.

Execution readiness boundary:

* Current execution mode is verification of an already bounded repair packet. Additional live materialization writes remain out of scope unless a separate authorization supersedes the existing repair authorization.
* Live facts, decisions, and overlay must match the 2105 manifest before any bounded repair packet can be considered sealed.
* The 6-entry fixture route remains predecessor / diagnostic / regression evidence only; it cannot be promoted back to full current authority.
* If validation rediscovers `CURRENT_FACTS=6`, source/runtime row identity mismatch, or overlay gap, the plan reverts to `blocked_authorized_reconnect_pending` or `revised_plan_needed`.
* The current repair evidence may support `partial / sealed_bounded_repair_packet`, not release readiness, package readiness, deployment readiness, or manual QA.
* Adopted required-gate mutation remains out of scope unless separately authorized.
* Canonical seal requires resolving the plan-path provenance mismatch between `...repair_plan.md` and `...repair_problem7_plan.md`.

---

## 2. Scope

포함 범위:

* full current-route failure snapshot과 scope lock 작성
* `CURRENT_FACTS=6` predecessor failure, `2105`, fixture, historical, diagnostic, staging, predecessor, full current route의 baseline role classification
* full current-route baseline branch decision gate verification against current 2105 live readpoint
* selected baseline branch row universe와 sealed runtime-deployable bundle row universe의 row-identity reconciliation
* existing authorized live facts/decisions reconnect evidence가 manifest / corrected source / runtime row identity와 일치하는지 검증
* adopted source artifact cross-attestation 및 authorization / independent review evidence 존재 여부 검증
* runtime-adopted current-route compose 대상 row의 `body_source_overlay` requirement contract 작성
* source-overlay execution mode decision: current 2105 overlay verification / no-write diagnostic / future authorization-gated reconnect only if regression is rediscovered
* `Base.CanOpener`가 selected Branch A row universe에 속하는지 확인하고, 속하지 않으면 fixture leak symptom으로 격리하는 trace 작성
* selected Branch A compose target row의 overlay coverage inventory / gap ledger 작성
* compose, current-authority validation, Layer4 trace consumer가 같은 baseline/source-overlay contract를 소비하는지 검증
* compose / current-authority / Layer4 consumer actual read path scan 또는 import/read graph report 작성
* Layer4 trace를 source authority로 승격하지 않는 role matrix 작성
* required-validation guard candidate 상태 확인; adopted gate claim은 별도 authorization 없이는 금지
* full current-route validation 가능 범위 확인, read-only run if safe, 및 residual failure classification
* repair runner `PLAN_PATH`가 restored Problem 7 plan 또는 명시된 predecessor plan 관계를 올바르게 참조하는지 provenance alignment 확인
* final report와 ledger packet 작성

Primary execution evidence root:

* `Iris/build/description/v2/staging/dvf_3_3_current_route_baseline_source_overlay_repair/`

Direct plan artifact:

* `docs/dvf_3_3_current_route_baseline_source_overlay_repair_problem7_plan.md`

### Explicitly Out Of Scope

* Terminal Disposition Adjudication 재실행 또는 재판정
* Consumer Universe Denominator 재정의
* Shared Disposition Ledger Consumption 재채택
* Phase 4 live migration execution
* Phase 2+ live `data/` source write without sealed current-cutover authorization
* baseline 재정의 목적의 live runtime chunk replacement
* package route mutation
* public-facing Korean text quality acceptance
* semantic quality baseline cutover
* `quality_state` UI exposure
* publish-state 판단 변경
* `adopted / unadopted` enum 재정의
* `active / silent` current vocabulary 복귀
* old `2105` predecessor byte-level 복구
* 6-entry fixture를 full current authority로 승격
* 2105 successor overlay에 fixture-only row를 개별 patch로 추가
* staging `corrected_source_manifest.json`을 단독 source-of-truth로 live current source chain에 승격
* runtime-derived seed를 source / facts / decisions authority로 승격
* Layer4 trace를 source authority로 승격
* compose 외부 repair stage 신설
* Lua runtime parser 또는 runtime JSON parser 도입
* generic fallback 문장 자동 생성으로 missing overlay를 덮는 것
* 개별 row의 의미 품질 재평가
* 인게임 수동 QA 또는 release checklist
* canonical PASS / seal without upstream roadmap canonical docs artifact, sealed current-cutover authorization, adopted-source cross-attestation, and independent review

---

## 3. Non-Goals

이 계획은 다음을 해결하려 하지 않는다.

* live migration execution / Phase 4 live apply / current authority cutover 재오픈
* adopted vNext Baseline 자체의 재판정 또는 재작성
* adopted-source cross-attestation 없는 live current-route materialization write
* facts 재판정, body-role facts 확장, acquisition-led 본문화
* postproc 표면형 repair
* canonical rendered promotion
* successor baseline identity final seal; if this remains out of scope, live materialization write also remains out of scope
* old chunk replacement
* Layer4 absorption 해소
* semantic quality interpretation
* publish mutation
* public-facing exposure
* Layer4 policy redesign
* denominator-scope widening
* `adopted`를 quality-pass, publish state, deletion, suppression 의미로 해석하는 것
* focused validation PASS를 full current-route closure로 과대 선언하는 것
* `source_overlay_gap`을 full current-route blocker로 남긴 상태에서 complete closeout을 주장하는 것
* non-2105 universe를 runtime-deployable bundle reconciliation 없이 "full current route"로 부르는 것
* independent review 없이 canonical PASS / seal을 주장하는 것

---

## 4. Assumptions

* `docs/Philosophy.md`가 최상위 설계 권위다.
* `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`의 Iris DVF 3-3 current readpoint를 따른다.
* DVF 3-3 current authority chain은 `source -> facts -> decisions -> rendered -> Lua bridge -> runtime chunks`로 유지한다.
* Runtime Lua는 sealed payload를 표시할 뿐 source validation, body repair, compose, semantic quality judgment, publish policy 판단을 수행하지 않는다.
* Denominator lock, terminal disposition, shared disposition consumption은 닫힌 readpoint다.
* `adopted / unadopted`는 current runtime row vocabulary이며 quality-pass, publish-state, delete/suppress semantics가 아니다.
* `active / silent`는 current runtime vocabulary로 복귀하지 않는다.
* `CURRENT_FACTS=6` predecessor failure는 삭제 대상으로 단정하지 않고 fixture / focused / historical / diagnostic / superseded current-drift 역할로 분류한다. 현재 live readpoint가 2105이면 regression guard evidence로만 남긴다.
* `2105`는 자동으로 full current-route successor baseline으로 확정하지 않는다. Phase 2에서 branch decision gate를 통과해야 한다.
* adopted vNext Baseline은 이미 존재하는 authority input일 수 있으나, 이 계획은 그 adopted source artifact를 단정하지 않는다. Phase 1-2는 properly sealed canonical baseline source identity와 cross-attestation을 검증해야 한다.
* current route consumers read live materialized paths, especially `Iris/build/description/v2/data/dvf_3_3_input_manifest.json`, `Iris/build/description/v2/data/dvf_3_3_facts.jsonl`, `Iris/build/description/v2/data/dvf_3_3_decisions.jsonl`, and `Iris/build/description/v2/data/dvf_3_3_overlay_support.jsonl`.
* `body_source_overlay`는 compose support input이며 source authority 자체가 아니다.
* Layer4 trace는 diagnostic / support / validation input role만 가질 수 있고 source authority가 아니다.
* raw audit / readiness / dry-run / predecessor artifact는 direct execution authority가 아니다.
* Protected source / rendered / Lua bridge / runtime / package surface mutation은 별도 approved scope 없이는 금지된다.
* Existing dirty worktree changes outside this plan must be preserved.

Mandatory invariants:

* `6-entry fixture role`은 모든 baseline branch에서 full current-route authority와 분리한다.
* `6-entry fixture`를 full current-route current authority로 유지하는 branch는 금지한다.
* `Base.CanOpener`가 Branch A 2105 source universe에 없으면 overlay row를 추가하지 않는다. It is a fixture-leak symptom, not a 2105 overlay-support target.
* Additional live current-route materialization repair is forbidden in this plan. Existing authorized reconnect evidence may be verified but not re-executed.
* Any future authorized live current-route materialization repair must update or verify manifest / facts / decisions / overlay support as one adopted-baseline file set. Partial reconnect is a failure.
* selected baseline branch row universe는 sealed runtime-deployable bundle row universe와 row-identity로 reconcile되어야 한다. Count equality alone is insufficient.
* Reconciliation failure blocks `complete` unless it is explicitly named as a non-full-route residual and the plan does not use "full current route" for that smaller universe.
* `source_overlay_gap`이 full current-route compose target에 남으면 closeout은 `blocked` 또는 `partial`이다. Complete is allowed only when the row is reclassified as non-blocking by an explicit exception disposition.
* `independent_review_gate_pass` is a hard precondition for `complete`, canonical PASS, seal, and adopted required gate claim. The attached review input does not satisfy that gate.

Open decision gates:

* Full current-route baseline branch:
  * Mainline: Branch A, `2105` successor current baseline을 full current-route expected baseline으로 둔다.
  * Fallback only if Branch A is disproved: Branch B, full current-route runner의 expected-count / facts-source contract를 재지정한다. Reassignment basis, downstream validator list, and explicit non-full-route naming are mandatory.
  * 금지: `6-entry fixture`를 full current-route current authority로 유지하는 branch.
* Current-route materialization reconnect:
  * Mainline in this plan: `verify_existing_authorized_reconnect_packet`, using read-only evidence to confirm live facts / decisions / overlay are the selected 2105 current readpoint.
  * Regression fallback: `authorization_pending_reconnect_plan`, only if live facts / decisions drift away from the 2105 manifest again.
  * Actual execution mode: additional `vnext_baseline_materialization_reconnect` is forbidden unless a separate sealed current-cutover authorization exists.
  * `Iris/build/description/v2/staging/dvf_3_3_vnext_rejected_delta_correction_reparity/phase5/corrected_source_manifest.json` is provenance / staging evidence only unless successor current authority cutover final report, ledger packet, current authority input packet, or adopted vNext Baseline seal artifact cross-attests it as adopted source input.
  * Required live target paths before any future authorized execution: `Iris/build/description/v2/data/dvf_3_3_input_manifest.json`, `Iris/build/description/v2/data/dvf_3_3_facts.jsonl`, `Iris/build/description/v2/data/dvf_3_3_decisions.jsonl`, and `Iris/build/description/v2/data/dvf_3_3_overlay_support.jsonl`.
  * Forbidden: row-level overlay patch to make a fixture-only row pass full current-route compose.
* Source-overlay execution mode:
  * Mainline in this plan: `verify_current_2105_overlay_contract`, with gap inventory, source-membership trace, cross-attestation check, and provenance alignment.
  * Authorization-gated future path: verify or regenerate `Iris/build/description/v2/data/dvf_3_3_overlay_support.jsonl` as compose support for the selected Branch A row universe only if sealed current-cutover authorization permits live materialization write.
  * `overlay_support_write` is not a general fix for rows absent from the selected source universe and is not executable in this plan without authorization.
  * Row-level alternate: `reclassification`, prove the row is not a compose target or belongs to an allowed exception route.
  * Diagnostic fallback only: `no_write`, coverage / gap ledger only; missing rows remain `source_overlay_gap` blockers and full current-route PASS is not a success criterion.
* Sealed current-cutover authorization:
  * `sealed_current_cutover_authorization_exists=false` blocks Phase 2+ live writes, complete, canonical PASS, seal, adopted required gate claim, and max current-route closure claim.
  * Independent review is not a substitute for cutover authorization.
  * Accepted authorization criteria are defined by this plan, but the accepted authorization artifact must be issued outside this plan by non-executor / owner-approved / external gate authority.
* Independent review hard gate satisfaction.
* Authority Surface wording: sealed authority mutation 없음 / consumption contract 영향 있음.

---

## 5. Repository Areas Affected

### Code

Expected or possible execution touch points:

* `Iris/_docs/round3/round3_run_contract_tests.py`
* `Iris/_docs/round3/current_route_required_validations.json`
* `Iris/build/description/v2/tools/build/run_dvf_3_3_vnext_current_authority_cutover.py`, read-only pattern extraction only; direct invocation is forbidden in this plan
* `Iris/build/description/v2/tools/build/compose_layer3_text.py`
* `Iris/build/description/v2/tools/build/export_dvf_3_3_lua_bridge.py`
* `Iris/build/description/v2/tools/build/validate_dvf_3_3_current_route_baseline_source_overlay_repair.py`, exact planned validator path for implementation handoff and diagnostic-only validation
* new round-local tools under `Iris/build/description/v2/tools/build/`, only if they remain outside current core closure unless separately reviewed

Exact live current-route materialization targets, read-only in this plan and writable only in a separate sealed-authorized reconnect round:

* `Iris/build/description/v2/data/dvf_3_3_input_manifest.json`
* `Iris/build/description/v2/data/dvf_3_3_facts.jsonl`
* `Iris/build/description/v2/data/dvf_3_3_decisions.jsonl`
* `Iris/build/description/v2/data/dvf_3_3_overlay_support.jsonl`

Future authorized write runner boundary, defined here but not executed here:

* authorized write runner: `Iris/build/description/v2/tools/build/run_dvf_3_3_current_route_baseline_source_overlay_repair.py --mode authorized-reconnect`
* forbidden direct runner: `Iris/build/description/v2/tools/build/run_dvf_3_3_vnext_current_authority_cutover.py`

### Docs

Directly added by this planning step:

* `docs/dvf_3_3_current_route_baseline_source_overlay_repair_problem7_plan.md`

Expected execution docs:

* `docs/dvf_3_3_current_route_baseline_source_overlay_repair_roadmap.md`
* `docs/dvf_3_3_current_route_baseline_source_overlay_repair_contract.md`
* `docs/dvf_3_3_current_route_baseline_source_overlay_ledger_packet.md`
* `docs/dvf_3_3_current_route_baseline_source_overlay_repair_closeout.md`

Read-only authority / context docs:

* `docs/Philosophy.md`
* `docs/DECISIONS.md`
* `docs/ARCHITECTURE.md`
* `docs/ROADMAP.md`
* `docs/EXECUTION_CONTRACT.md`
* `docs/PLAN_TEMPLATE.md`
* `docs/dvf_3_3_shared_disposition_ledger_packet.md`
* `docs/consumer_universe_denominator_lock_ledger_packet.md`
* `docs/dvf_3_3_terminal_disposition_ledger_packet.md`
* `docs/dvf_3_3_live_migration_readiness_ledger_packet.md`

### Config

Possible candidate or adopted gate touch point:

* `Iris/_docs/round3/current_route_required_validations.json`

Direct live adoption is out of scope for this plan. Candidate patch/report is preferred; adoption belongs to the separate sealed-authorized reconnect round.

### Generated Artifacts

All generated artifacts for this round must stay under:

* `Iris/build/description/v2/staging/dvf_3_3_current_route_baseline_source_overlay_repair/`

Expected artifact families:

* `phase0/worktree_dirty_isolation_report.json`
* `phase0/canonical_roadmap_materialization_report.json`
* `phase0/current_route_failure_snapshot.json`
* `phase0/current_route_failure_snapshot.md`
* `phase0/scope_lock_verdict.json`
* `phase0/isolation_attestation.json`
* `phase1/baseline_role_classification.json`
* `phase1/baseline_role_classification.md`
* `phase1/current_facts_6_surface_inventory.json`
* `phase1/baseline_count_axis_matrix.json`
* `phase1/baseline_branch_decision_packet.md`
* `phase1/runtime_deployable_universe_reconciliation_report.json`
* `phase1/runtime_deployable_bundle_fingerprint_report.json`
* `phase2/source_overlay_requirement_matrix.json`
* `phase2/source_overlay_requirement_contract.md`
* `phase2/source_overlay_execution_mode_decision.json`
* `phase2/sealed_current_cutover_authorization_check.json`
* `phase2/accepted_authorization_artifact_schema.json`
* `phase2/adopted_source_cross_attestation_report.json`
* `phase2/adopted_source_priority_rule.json`
* `phase2/canonical_baseline_identity_validator_report.json`
* `phase2/authorized_write_runner_boundary.json`
* `phase2/current_cutover_authorization_request.md`
* `phase2/current_route_materialization_reconnect_plan.json`
* `phase2/current_route_live_path_allowlist.json`
* `phase2/current_route_materialization_hash_plan.json`
* `phase2/current_route_materialization_write_mutation_class.json`, authorization-gated definition only
* `phase2/base_canopener_fixture_leak_trace.json`
* `phase2/overlay_support_write_authorization_requirements.json`, only if a future write mode is proposed in the authorization request
* `phase2/source_overlay_exception_reason_codes.json`
* `phase2/adopted_compose_target_inventory.json`
* `phase3/body_source_overlay_coverage_report.json`
* `phase3/body_source_overlay_gap_ledger.jsonl`
* `phase3/base_canopener_overlay_blocker_trace.json`
* `phase3/overlay_row_identity_join_report.json`
* `phase4/current_route_baseline_contract.json`
* `phase4/current_route_input_packet.json`
* `phase4/forbidden_authority_read_matrix.json`
* `phase4/no_dual_authority_read_report.json`
* `phase4/protected_surface_no_mutation_report.json`
* `phase5/compose_current_authority_alignment_report.json`
* `phase5/layer4_trace_consumption_role_matrix.json`
* `phase5/baseline_identity_match_report.json`
* `phase5/source_overlay_contract_consumption_report.json`
* `phase5/actual_consumer_read_path_graph_report.json`
* `phase5/read_path_scan_report.json`
* `phase6/required_validation_manifest_patch.json`
* `phase6/current_route_baseline_source_overlay_required_gate_report.json`
* `phase6/focused_unittest_report.json`
* `phase6/future_closeout_claim_guard_report.json`
* `phase6/required_validation_gate_status_report.json`
* `phase6/tooling_core_allowlist_invariant_report.json`
* `phase7/full_current_route_validation_report.json`
* `phase7/residual_failure_classification.json`
* `phase7/independent_review_gate_report.json`
* `phase7/final_current_route_baseline_source_overlay_repair_report.json`

---

## 6. Planned Changes

### Change 1 / Phase 0 - Failure Surface Diagnosis & Scope Lock

Purpose:

full current-route predecessor failure와 현재 2105 live readpoint를 재현 가능한 snapshot으로 고정하고, split-materialization / fixture-leak hypothesis가 현재 repair packet에서 해소됐는지 검증한다. 이번 라운드는 baseline/source-overlay family의 evidence verification, provenance alignment, and bounded repair packet claim boundary를 다룬다.

Files:

* `Iris/build/description/v2/staging/dvf_3_3_current_route_baseline_source_overlay_repair/phase0/worktree_dirty_isolation_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_current_route_baseline_source_overlay_repair/phase0/canonical_roadmap_materialization_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_current_route_baseline_source_overlay_repair/phase0/current_route_failure_snapshot.json`
* `Iris/build/description/v2/staging/dvf_3_3_current_route_baseline_source_overlay_repair/phase0/current_route_failure_snapshot.md`
* `Iris/build/description/v2/staging/dvf_3_3_current_route_baseline_source_overlay_repair/phase0/scope_lock_verdict.json`
* `Iris/build/description/v2/staging/dvf_3_3_current_route_baseline_source_overlay_repair/phase0/isolation_attestation.json`
* `docs/dvf_3_3_current_route_baseline_source_overlay_repair_roadmap.md`, if canonical roadmap materialization is approved

Implementation Notes:

* Record existing dirty worktree state before implementation and isolate this round's touched files from unrelated changes.
* Materialize the provisional pasted roadmap into a canonical docs artifact or explicitly record that canonical roadmap materialization remains pending and blocks seal.
* Record the exact full current-route runner command, inputs, expected count, actual count, failing row identities, and compose/current-authority/Layer4 trace symptoms.
* Record split-materialization and `Base.CanOpener` fixture-leak as hypotheses, not conclusions.
* Explicitly classify denominator / terminal / shared / readiness surfaces as read-only non-failure sources for this round.
* Record protected source / rendered / Lua bridge / runtime / package path set by exact path before any later step.
* Failure snapshot is evidence, not new authority.
* Phase 0 is read-only except for planned docs/staging evidence writes.

Validation:

* worktree dirty isolation report exists and lists unrelated dirty paths separately from planned touched paths.
* canonical roadmap materialization is completed or explicitly marked pending with seal blocked.
* failure snapshot is deterministic and path-pinned.
* `CURRENT_FACTS=6`, expected `2105`, and missing `body_source_overlay` symptoms are present as diagnostic observations or the plan closes as revised-needed.
* split-materialization hypothesis is marked falsifiable and deferred to Phase 1 evidence.
* protected surface precheck reports no unexpected mutation before execution.
* distinct-axis non-substitution is asserted for denominator / terminal / shared / readiness surfaces.

---

### Change 2 / Phase 1 - Baseline Role Classification, Branch Decision & Runtime Bundle Reconciliation

Purpose:

`CURRENT_FACTS=6`, `2105`, fixture, historical, diagnostic, staging, predecessor, and full current route roles를 분리하고, split-materialization hypothesis를 검증 / 반증한다. full current-route baseline branch를 명시적으로 선택한 뒤 selected branch row universe와 sealed runtime-deployable bundle을 row-identity로 reconcile한다.

Files:

* `Iris/build/description/v2/staging/dvf_3_3_current_route_baseline_source_overlay_repair/phase1/current_facts_6_surface_inventory.json`
* `Iris/build/description/v2/staging/dvf_3_3_current_route_baseline_source_overlay_repair/phase1/baseline_role_classification.json`
* `Iris/build/description/v2/staging/dvf_3_3_current_route_baseline_source_overlay_repair/phase1/baseline_count_axis_matrix.json`
* `Iris/build/description/v2/staging/dvf_3_3_current_route_baseline_source_overlay_repair/phase1/baseline_branch_decision_packet.md`
* `Iris/build/description/v2/staging/dvf_3_3_current_route_baseline_source_overlay_repair/phase1/runtime_deployable_bundle_fingerprint_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_current_route_baseline_source_overlay_repair/phase1/runtime_deployable_universe_reconciliation_report.json`

Implementation Notes:

* `6-entry fixture role` separation is a mandatory invariant, not a branch option.
* Resolution mainline is Branch A: full current-route expected baseline is `2105` successor current baseline.
* Branch B is a fallback only if Phase 1 evidence disproves Branch A. It must reassign the full current-route expected-count / facts-source contract with explicit reassignment basis, downstream validator list, and route naming that does not mislabel a smaller universe as full current route.
* A branch that keeps the 6-entry fixture as full current-route current authority is forbidden.
* If split-materialization hypothesis is disproved, stop as `revised_plan_needed` instead of forcing Phase 2.
* If Branch A is supported, record that support as diagnostic evidence only. It does not authorize live materialization write.
* Classify every `CURRENT_FACTS=6` surface as one of:
  * `full_current_route`
  * `focused_current_fixture_route`
  * `historical_reproduction_route`
  * `diagnostic_route`
  * `staging_evidence_route`
  * `predecessor_context`
  * `stale_or_forbidden_current_like_surface`
* Classify every relevant `2105` occurrence as one of:
  * `successor_current_baseline`
  * `predecessor_context`
  * `runtime_deployable_entry_count`
  * `audit_comparison_migration_count`
* A co-equal cross-surface count is not divergence by itself. A `2105` occurrence may be successor current baseline count and another `2105` occurrence may be runtime-deployable entry count; divergence is row-identity mismatch, role mismatch, or forbidden authority consumption.
* Do not silently rewrite `6` to `2105`.
* Build the selected branch row universe and reconcile it against the sealed runtime-deployable bundle. The reconciliation must use row identity, not count equality.
* Runtime-deployable bundle fingerprint evidence must include chunk manifest / chunk file paths / row identity extraction basis. If the bundle readpoint is `2105 entries / 11 chunks`, record that as input evidence; if execution finds a different sealed bundle shape, stop and revise.
* Do not proceed to Phase 2 authorization request until branch selection is recorded.
* Do not call a non-2105 or non-runtime-reconciled universe "full current route" unless the report explicitly explains why it is not the runtime-deployable full route.
* If branch cannot be selected, close this round as `blocked` with complete classification evidence.

Validation:

* duplicate baseline role hard-fails.
* fixture route cannot claim full current-route authority.
* full current-route cannot directly consume fixture baseline.
* selected branch lists downstream validators and expected count contract.
* runtime-deployable universe reconciliation reports `MATCHED` by row identity, or authorization request readiness is blocked. Complete closeout is not available in this plan.
* count-only reconciliation is recorded as insufficient.

---

### Change 3 / Phase 2 - Cutover Authorization Check & Reconnect Request

Purpose:

adopted vNext Baseline과 live current-route materialized files 사이의 끊어진 연결을 복구하려면 별도 sealed current-cutover authorization이 필요한지 확인하고, authorization이 없으면 reconnect 실행계획 / authorization request까지만 산출한다. 동시에 runtime-adopted current-route compose 대상 row가 compose 전에 `body_source_overlay`를 가져야 하는 조건과 예외 reason code를 봉인한다.

Files:

* `Iris/build/description/v2/staging/dvf_3_3_current_route_baseline_source_overlay_repair/phase2/source_overlay_requirement_contract.md`
* `Iris/build/description/v2/staging/dvf_3_3_current_route_baseline_source_overlay_repair/phase2/source_overlay_requirement_matrix.json`
* `Iris/build/description/v2/staging/dvf_3_3_current_route_baseline_source_overlay_repair/phase2/source_overlay_execution_mode_decision.json`
* `Iris/build/description/v2/staging/dvf_3_3_current_route_baseline_source_overlay_repair/phase2/sealed_current_cutover_authorization_check.json`
* `Iris/build/description/v2/staging/dvf_3_3_current_route_baseline_source_overlay_repair/phase2/accepted_authorization_artifact_schema.json`
* `Iris/build/description/v2/staging/dvf_3_3_current_route_baseline_source_overlay_repair/phase2/adopted_source_cross_attestation_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_current_route_baseline_source_overlay_repair/phase2/adopted_source_priority_rule.json`
* `Iris/build/description/v2/staging/dvf_3_3_current_route_baseline_source_overlay_repair/phase2/canonical_baseline_identity_validator_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_current_route_baseline_source_overlay_repair/phase2/authorized_write_runner_boundary.json`
* `Iris/build/description/v2/staging/dvf_3_3_current_route_baseline_source_overlay_repair/phase2/current_cutover_authorization_request.md`
* `Iris/build/description/v2/staging/dvf_3_3_current_route_baseline_source_overlay_repair/phase2/current_route_materialization_reconnect_plan.json`
* `Iris/build/description/v2/staging/dvf_3_3_current_route_baseline_source_overlay_repair/phase2/current_route_live_path_allowlist.json`
* `Iris/build/description/v2/staging/dvf_3_3_current_route_baseline_source_overlay_repair/phase2/current_route_materialization_hash_plan.json`
* `Iris/build/description/v2/staging/dvf_3_3_current_route_baseline_source_overlay_repair/phase2/current_route_materialization_write_mutation_class.json`, definition only; not executable without authorization
* `Iris/build/description/v2/staging/dvf_3_3_current_route_baseline_source_overlay_repair/phase2/base_canopener_fixture_leak_trace.json`
* `Iris/build/description/v2/staging/dvf_3_3_current_route_baseline_source_overlay_repair/phase2/overlay_support_write_authorization_requirements.json`, only if a future write mode is proposed in the authorization request
* `Iris/build/description/v2/staging/dvf_3_3_current_route_baseline_source_overlay_repair/phase2/source_overlay_exception_reason_codes.json`
* `Iris/build/description/v2/staging/dvf_3_3_current_route_baseline_source_overlay_repair/phase2/adopted_compose_target_inventory.json`

Implementation Notes:

* Phase 2 remains no-write. It may define the authorization criteria and future reconnect plan, but it must not execute live reconnect even if an authorization-like artifact is found.
* `sealed_current_cutover_authorization_check.json` must distinguish:
  * plan review / independent review.
  * current-cutover authorization.
  * adopted source artifact cross-attestation.
  * mutation authorization for live `data/` paths.
* `sealed_current_cutover_authorization_check.json` must record `phase2_plus_live_write_status=not_executed_in_this_plan`.
* `accepted_authorization_artifact_schema.json` must require:
  * `accepted_authorization_artifact_paths` as exact path list.
  * `authorization_kind = current_route_materialization_reconnect`.
  * `authorized_targets` exactly equal to the live materialization allowlist.
  * `authorized_mutation_class = current_route_materialization_write`.
  * `adopted_source_cross_attestation = PASS`.
  * `source_adjudication_changed = false`.
  * `issued_by = non_executor | owner_approved | external_gate`.
  * `self_generated = false`.
* Any self-generated authorization artifact must fail the authorization check, even if other fields are present.
* `corrected_source_manifest.json` is not source-of-truth by itself. It is provenance / staging evidence unless a successor current authority cutover final report, ledger packet, current authority input packet, or adopted vNext Baseline seal artifact cross-attests it as adopted source input.
* A "superseding adopted artifact" cannot be named by the execution report alone. It must be named by current authority seal or owner-approved manifest.
* `adopted_source_priority_rule.json` must define source selection when multiple cross-attested artifacts exist. Default priority: current authority seal artifact > current authority input packet > successor current authority cutover final report > ledger packet > staging provenance.
* `authorized_write_runner_boundary.json` must define:
  * `authorized_write_runner = Iris/build/description/v2/tools/build/run_dvf_3_3_current_route_baseline_source_overlay_repair.py --mode authorized-reconnect`.
  * `forbidden_direct_runners = [Iris/build/description/v2/tools/build/run_dvf_3_3_vnext_current_authority_cutover.py]`.
  * diagnostic modes must not open write-capable code paths.
  * future authorized write runner must touch only the exact live materialization allowlist.
  * future dry-run input, planned diff, and actual diff must share the same row universe.
* `current_route_materialization_reconnect_plan.json` must pin source and target paths, and must state `execution_allowed=false` in this plan.
* `current_route_materialization_write_mutation_class.json` defines requirements for the separate authorized round:
  * `mutation_class = current_route_materialization_write`
  * `allowed_targets = exact_live_materialization_allowlist_only`
  * `source_adjudication_changed = false`
  * `current_route_materialization_targets_changed = true|false`
  * `changed_paths = exact_allowlist_only`
  * `diff_matches_adopted_baseline = true`
  * pre-write hash, post-write hash, diff-to-adopted-source, row identity match, rollback snapshot, and no extra / no missing row report requirements.
* Future authorized reconnect final report must use the same field names and may claim `live_write_executed = true` only in the separate sealed-authorized round. That future report must also record `changed_paths = exact_allowlist_only` and `diff_matches_adopted_baseline = true`.
* Final report fields must include these names exactly:
  * `plan_closeout_status = partial | implemented_only | blocked | blocked_authorization_pending`
  * `sealed_current_cutover_authorization_artifact = <path | null>`
  * `authorization_self_generated = false | true | unknown`
  * `authorized_write_runner = Iris/build/description/v2/tools/build/run_dvf_3_3_current_route_baseline_source_overlay_repair.py --mode authorized-reconnect`
  * `live_write_executed = false`
  * `changed_paths = none_in_this_plan`
  * `source_adjudication_changed = false`
  * `diff_matches_adopted_baseline = not_executed_in_this_plan`
  * `independent_review_gate_status = PASS | FAIL | missing`
  * `future_complete_gate_status = blocked_independent_review_pending | blocked_authorization_pending | not_evaluated | ready_for_future_complete_gate`
* If the live state is split, for example manifest / overlay are 2105 while facts / decisions are 6, this plan records reconnect need, emits authorization request, and closes without reconnect execution.
* It is never valid to patch `Base.CanOpener` into 2105 overlay support to compensate for fixture leakage.
* Required condition is an AND condition:
  * row is a current-route row.
  * row vocabulary is `adopted`.
  * row is a compose target.
  * row requires body composition through current body plan/profile.
* `body_source_overlay` must not become source authority, quality pass, publish state, or semantic strength signal.
* `source_overlay_execution_mode_decision.json` must choose a support path before Change 4:
  * Mainline support path in this plan: `no_write_diagnostic`.
  * Authorization request path: `authorization_pending_reconnect_plan`.
  * Future authorization-gated execution path: `overlay_support_write`. It is allowed only in the separate sealed-authorized round when the selected source universe includes the row and the overlay support artifact is stale or missing. The sealed execution-mode artifact must define exactly one target path, source support, writer authorization, no-dual-authority validator, protected path exception, and rollback condition.
  * Row-level alternate repair path: `reclassification`. The row must be proven not to be a compose target or to belong to an allowed exception route.
  * Diagnostic fallback only: `no_write`. Coverage and gap ledger are allowed, but `source_overlay_gap` rows remain blockers and full current-route PASS is not a success criterion.
* Missing overlay can pass only with explicit reason code:
  * `not_compose_target`
  * `fixture_only`
  * `historical_only`
  * `diagnostic_only`
  * `evidence_only`
  * `source_overlay_gap`
  * `forbidden_as_execution_authority`

Validation:

* sealed current-cutover authorization check exists and records the accepted artifact criteria; it must not authorize execution in this plan.
* accepted authorization artifact schema validates required fields and rejects self-generated authorization.
* adopted source cross-attestation report exists. If it cannot cross-attest the selected source artifact, Phase 2+ live writes are blocked.
* adopted source priority rule validates source selection when multiple cross-attested artifacts exist.
* canonical baseline identity validator report exists or records why identity final-seal is missing and blocks live materialization.
* authorized write runner boundary validates the future command and forbidden direct runner list.
* a no-write diagnostic or authorization-request path is selected before Change 4 proceeds. If only `no_write` is selected, the closeout target is limited to `partial` or `blocked`.
* live path allowlist names exact source and target paths for future authorized execution.
* reconnect hash plan is future-execution evidence only.
* `Base.CanOpener` fixture-leak trace proves whether the row belongs to selected Branch A. If not, overlay row patch is forbidden.
* adopted compose target coverage validator passes or reports blockers.
* exception reason completeness validator passes.
* overlay-vs-source boundary validation proves overlay support is not source authority.
* overlay-support write mode is blocked in this plan; future authorized mode must validate target path, source support, no-dual-authority, protected path exception, and rollback condition.
* no quality / publish / semantic leakage is present in the contract.

---

### Change 4 / Phase 3 - Overlay Coverage Inventory & Gap Ledger

Purpose:

selected Branch A runtime-adopted compose 대상 전체의 `body_source_overlay` coverage를 row-level로 측정하고, `Base.CanOpener`가 selected source universe에 없는 fixture-leak symptom인지 또는 실제 overlay-support gap인지 구분한다. Gap은 이 계획에서 live write로 닫지 않고 blocker / authorization request / compose-target reclassification evidence로 남긴다.

Files:

* `Iris/build/description/v2/staging/dvf_3_3_current_route_baseline_source_overlay_repair/phase3/body_source_overlay_coverage_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_current_route_baseline_source_overlay_repair/phase3/body_source_overlay_gap_ledger.jsonl`
* `Iris/build/description/v2/staging/dvf_3_3_current_route_baseline_source_overlay_repair/phase3/base_canopener_overlay_blocker_trace.json`
* `Iris/build/description/v2/staging/dvf_3_3_current_route_baseline_source_overlay_repair/phase3/overlay_row_identity_join_report.json`

Implementation Notes:

* Build the compose target inventory from the selected full current baseline branch.
* The selected branch must already be reconciled with the sealed runtime-deployable bundle unless this execution is explicitly no-write / diagnostic-only.
* The coverage universe is the selected Branch A live materialization, not the stale 6-entry fixture universe.
* `Base.CanOpener` focused trace must answer one question first: is this row present in the selected Branch A 2105 source universe? If no, classify it as `fixture_only` / `stale_current_like_surface` evidence and do not add an overlay row to the 2105 support artifact.
* For each row record `fulltype`, runtime vocabulary state, compose target status, required overlay fields, actual overlay presence, overlay source, missing field list, exception reason, and blocker severity.
* Do not synthesize generic fallback prose to hide missing overlay.
* Do not use diagnostic / Layer4 trace as overlay authority unless the selected contract explicitly admits it as support-only input.
* If mode is `no_write`, gaps remain blockers and this Change cannot support a complete closeout.
* If future mode would be `materialization_reconnect`, record expected post-reconnect coverage criteria in the authorization request; do not regenerate or restore live files in this plan.
* If future mode would be `overlay_support_write`, record target and diff expectations separately from source authority surfaces; do not write rows in this plan.
* If mode is `reclassification`, the row must leave the adopted compose target blocker set through a validated exception reason.

Validation:

* row identity join validation passes.
* orphan overlay, missing overlay, duplicate overlay checks run.
* `Base.CanOpener` focused assertion is present.
* `Base.CanOpener` is not accepted as a 2105 overlay-support write target unless it is present in the selected Branch A source universe.
* compose dry-run evidence is recorded only if it can run without live current-route writes.
* peer row coverage prevents fixing only the known example while leaving equivalent blockers.
* `source_overlay_gap` complete-eligibility validator fails if any full current-route compose target remains in blocker state.

---

### Change 5 / Phase 4 - Current-Route Input Contract Materialization

Purpose:

full current-route가 소비해야 할 adopted vNext Baseline live materialization 및 baseline/source-overlay contract를 authorization-pending input packet으로 materialize한다.

Files:

* `Iris/build/description/v2/staging/dvf_3_3_current_route_baseline_source_overlay_repair/phase4/current_route_baseline_contract.json`
* `Iris/build/description/v2/staging/dvf_3_3_current_route_baseline_source_overlay_repair/phase4/current_route_input_packet.json`
* `Iris/build/description/v2/staging/dvf_3_3_current_route_baseline_source_overlay_repair/phase4/forbidden_authority_read_matrix.json`
* `Iris/build/description/v2/staging/dvf_3_3_current_route_baseline_source_overlay_repair/phase4/no_dual_authority_read_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_current_route_baseline_source_overlay_repair/phase4/protected_surface_no_mutation_report.json`

Implementation Notes:

* Packet fields include baseline row universe, adopted vNext Baseline source artifact path if cross-attested, live input manifest path, live facts path, live decisions path, overlay support path, compose profile path, rendered output target, runtime deployable reference, Layer4 trace role, forbidden raw authority paths, and fixture/historical/diagnostic exclusions.
* Packet is an input contract, not a new data authority.
* Source paths must not be copied into competing dual-authority files.
* Rendered/runtime outputs must not become source baseline inputs.
* Protected no-mutation path set must be pinned by exact path, not category label.
* Allowlisted live current-route materialization paths are future authorized targets only. They are not writable in this plan.
* If overlay-support write mode is planned, the overlay support artifact is excluded from source authority and included as compose support with its own rollback entry. It remains authorization-gated and non-executable in this plan.

Validation:

* single baseline packet validation passes.
* live materialization target path allowlist validation passes as future-execution planning evidence only.
* no dual-authority read validation reports `0`.
* no raw predecessor execution authority validation reports `0`.
* fixture exclusion validation passes.
* protected surface no-mutation validation passes.

---

### Change 6 / Phase 5 - Compose / Current-Authority / Layer4 Trace Alignment

Purpose:

compose route, current-authority validator, Layer4 trace consumer가 현재 어떤 live materialization 및 source-overlay contract를 소비하는지 read-only로 검증한다. Intended adopted vNext Baseline consumption contract와의 divergence는 authorization request에 반영한다.

Files:

* `Iris/build/description/v2/staging/dvf_3_3_current_route_baseline_source_overlay_repair/phase5/compose_current_authority_alignment_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_current_route_baseline_source_overlay_repair/phase5/layer4_trace_consumption_role_matrix.json`
* `Iris/build/description/v2/staging/dvf_3_3_current_route_baseline_source_overlay_repair/phase5/baseline_identity_match_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_current_route_baseline_source_overlay_repair/phase5/source_overlay_contract_consumption_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_current_route_baseline_source_overlay_repair/phase5/actual_consumer_read_path_graph_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_current_route_baseline_source_overlay_repair/phase5/read_path_scan_report.json`

Implementation Notes:

* Layer4 trace role must be one of:
  * `diagnostic_only`
  * `contract_bound_support`
  * `validation_input`
  * `forbidden_execution_authority`
* Layer4 trace cannot replace facts, decisions, overlay source, or source authority.
* Composer and validator must prove row universe hash match or fail closed.
* Composer and validator must prove whether live facts / decisions / overlay support currently come from the same selected row universe.
* A test-only pass is insufficient if actual compose route reads a different input contract.
* Actual consumer path scan must inspect compose / current-authority / Layer4 consumer import or read graph, not only declared matrix role.
* If new current-route-adjacent tooling is introduced, record whether it affects current core closure or tooling allowlist.

Validation:

* compose/current-authority baseline identity match or divergence is recorded.
* Layer4 trace role validation passes.
* actual read path graph validation passes.
* no source-authority promotion from trace is detected.
* row universe hash match or mismatch is recorded.
* `VALUE_DIVERGENCE` is recorded; non-zero blocks complete but can feed authorization request.
* no-dual-authority-read result is recorded; non-zero blocks complete.

---

### Change 7 / Phase 6 - Required Validation Guard Hardening

Purpose:

future closeout에서 baseline/source-overlay regression을 fail-closed로 막는 required validation guard를 candidate gate로 준비한다. Adopted gate는 sealed current-cutover authorization 없이는 금지한다.

Files:

* `Iris/build/description/v2/staging/dvf_3_3_current_route_baseline_source_overlay_repair/phase6/required_validation_manifest_patch.json`
* `Iris/build/description/v2/staging/dvf_3_3_current_route_baseline_source_overlay_repair/phase6/current_route_baseline_source_overlay_required_gate_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_current_route_baseline_source_overlay_repair/phase6/focused_unittest_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_current_route_baseline_source_overlay_repair/phase6/future_closeout_claim_guard_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_current_route_baseline_source_overlay_repair/phase6/required_validation_gate_status_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_current_route_baseline_source_overlay_repair/phase6/tooling_core_allowlist_invariant_report.json`
* `Iris/_docs/round3/current_route_required_validations.json`, candidate patch reference only; live adoption is out of scope for this plan

Implementation Notes:

* Guard targets:
  * live current-route materialization is split, for example 2105 manifest / overlay with 6-entry facts / decisions.
  * full current-route consumes fixture baseline as current baseline.
  * predecessor/raw audit/readiness artifact is consumed as execution authority.
  * adopted compose target is missing `body_source_overlay`.
  * Layer4 trace is promoted to source authority.
* Candidate patch is the only allowed output in this plan. Adoption is forbidden and belongs to the separate sealed-authorized reconnect round.
* Focused guard PASS is not full current-route closure.
* Final report must use `required_validation_gate_status = not_attempted | candidate_only`.
* `adopted_required_gate` is out of scope for this plan; it requires sealed current-cutover authorization, explicit approval, current-route runner validation, and independent review in a later round.
* New tooling must not silently expand current core closure or tooling allowlist cap.

Validation:

* manifest patch schema validation passes.
* focused unittest passes.
* required artifact and required test existence validation pass.
* future closeout claim guard validation passes.
* required-validation gate status enum validation passes.
* tooling core / allowlist invariant validation passes.
* adopted gate validation is not run in this plan.

---

### Change 8 / Phase 7 - Full Current-Route Re-Validation, Independent Review & Residual Isolation

Purpose:

현재 repair packet evidence 이후 full current-route validation 가능 범위를 확인한다. 이 계획은 추가 live materialization reconnect를 실행하지 않으며, 현재 evidence가 유효하면 `partial / sealed_bounded_repair_packet`으로 닫는다. Drift, missing authorization/review, or plan-path provenance mismatch가 발견되면 `blocked_authorized_reconnect_pending`, `blocked_authorization_pending`, `blocked_provenance_alignment`, 또는 `revised_plan_needed`로 닫는다.

Files:

* `Iris/build/description/v2/staging/dvf_3_3_current_route_baseline_source_overlay_repair/phase7/full_current_route_validation_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_current_route_baseline_source_overlay_repair/phase7/residual_failure_classification.json`
* `Iris/build/description/v2/staging/dvf_3_3_current_route_baseline_source_overlay_repair/phase7/independent_review_gate_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_current_route_baseline_source_overlay_repair/phase7/final_current_route_baseline_source_overlay_repair_report.json`
* `docs/dvf_3_3_current_route_baseline_source_overlay_ledger_packet.md`
* `docs/dvf_3_3_current_route_baseline_source_overlay_repair_closeout.md`

Implementation Notes:

* Full current-route runner may be rerun as read-only evidence if it does not mutate live current-route files.
* Full current-route PASS may be recorded as current evidence if it is produced by no-write validation. It still does not claim release readiness.
* PASS means bounded build-surface contract closure only and still does not claim package, deployment, runtime replacement, or manual QA readiness.
* Complete closeout requires external / independent review for both canonical roadmap artifact and this restored Problem 7 plan, or explicit reconciliation showing the existing independent review covered the restored plan artifact. The attached WARN review does not satisfy that gate by itself.
* Missing independent review does not by itself fail this bounded repair packet verification round if the current closeout remains `partial`; it sets `future_complete_gate_status=blocked_independent_review_pending` unless another future complete-gate blocker is more specific.
* If failure remains, classify as:
  * `baseline_contract_failure`
  * `live_materialization_reconnect_failure`
  * `source_overlay_contract_failure`
  * `compose_alignment_failure`
  * `layer4_trace_consumption_failure`
  * `unrelated_current_route_residual`
* `source_overlay_gap` on a full current-route compose target is always `source_overlay_contract_failure`, not `unrelated_current_route_residual`.
* Final report repeats protected surface no-mutation and non-claim boundaries.

Validation:

* full current-route validation exits code is recorded if run, or skipped/blocked reason is recorded.
* existing authorized live materialization reconnect report is recorded if present; this plan does not execute a new reconnect.
* `source_overlay_gap` blocker count is recorded. `0` is required for the current bounded repair packet seal.
* independent review gate report records PASS, FAIL, or missing; PASS does not substitute for current-cutover authorization.
* focused source-overlay validation passes.
* final protected surface no-mutation passes.
* final claim boundary validation passes.
* final report hash seal or equivalent final report seal is recorded.

---

## 7. Validation Plan

### Automated Validation

Do not claim validation passed unless the exact relevant command exits with code `0`.

Expected commands after implementation:

Phase 0-1 commands may be used for conditional diagnostic/classification progress. Phase 2+ live write commands and complete-mode commands are forbidden in this plan. A separate sealed-authorized reconnect round must define and run its own write/complete commands.

```powershell
uv run python Iris\build\description\v2\tools\build\run_dvf_3_3_current_route_baseline_source_overlay_repair.py --mode diagnostic
uv run python Iris\build\description\v2\tools\build\validate_dvf_3_3_current_route_baseline_source_overlay_repair.py --diagnostic-only
uv run python -B -m unittest discover -s Iris\build\description\v2\tests -p "test_dvf_3_3_current_route_baseline_source_overlay_repair.py"
uv run python Iris\build\description\v2\tools\build\validate_consumer_universe_denominator_lock.py --require-complete
uv run python Iris\build\description\v2\tools\build\validate_dvf_3_3_terminal_disposition_adjudication.py --require-complete
uv run python Iris\build\description\v2\tools\build\validate_dvf_3_3_shared_disposition_consumption.py --require-complete
python -B Iris\_docs\round3\round3_run_contract_tests.py --class current --enforce-current-build-closure
python -B Iris\_docs\round3\round3_run_contract_tests.py --class historical
python -B Iris\_docs\round3\round3_run_contract_tests.py --class diagnostic
powershell -ExecutionPolicy Bypass -File .\tools\check_lua_syntax.ps1
```

Required automated gates:

* worktree dirty isolation validation
* canonical roadmap materialization or seal-blocking pending status validation
* failure snapshot reproduction
* baseline role classification validation
* selected branch contract validation
* fixture/full current route separation validation
* selected branch universe to sealed runtime-deployable bundle row-identity reconciliation validation
* runtime-deployable bundle fingerprint validation
* sealed current-cutover authorization existence validation
* adopted source artifact cross-attestation validation
* properly sealed canonical baseline identity validation
* cutover tool direct invocation prohibition validation
* diagnostic command no-write validation
* authorized write runner exact-allowlist boundary validation
* future dry-run / planned diff / actual diff row-universe equivalence validation
* self-generated authorization / review rejection schema validation
* live current-route materialization reconnect plan validation
* live current-route materialization target-path allowlist validation
* input manifest / facts / decisions / overlay support row-universe diagnostic validation
* `Base.CanOpener` fixture-leak vs Branch A source-membership validation
* overlay execution mode decision validation
* future overlay write-target and protected-status exception requirements validation, if a write mode is proposed in the authorization request
* source-overlay schema validation
* adopted compose target coverage validation
* `source_overlay_gap` complete-eligibility validation
* exception reason completeness validation
* row identity join validation
* `Base.CanOpener` focused blocker assertion
* compose dry-run determinism validation
* single baseline packet validation
* live materialization packet validation
* no dual-authority read validation
* forbidden raw authority read validation
* Layer4 trace role validation
* actual consumer read path scan / import-read graph validation
* compose/current-authority baseline identity match
* row universe hash match
* required-validation manifest patch validation
* required-validation gate status enum validation
* tooling core / allowlist invariant validation
* focused guard unittest
* full current-route validation, read-only if run
* residual classification validation if full current-route remains non-zero
* terminal / denominator / shared / readiness predecessor surfaces remain unchanged
* readiness evidence hash / no-mutation attestation
* independent review gate validation before any complete / canonical seal claim
* protected source / rendered / Lua bridge / runtime / package no-mutation validation
* future authorized reconnect round requirements: `current_route_materialization_write` mutation class validation, pre/post hash validation, diff-to-adopted-source validation, row identity match validation, rollback snapshot validation, and no extra / no missing row validation

If `uv`, Python, PowerShell script, or a required helper is missing, validation is `blocked`, not passed.

### Manual Validation

* Review Phase 0 scope lock and failure family classification.
* Review worktree dirty isolation and protected path pin set.
* Review Phase 1 baseline branch decision before authorization request.
* Review selected branch to runtime-deployable bundle reconciliation.
* Review sealed current-cutover authorization status before any Phase 2+ write.
* Review adopted source artifact cross-attestation before naming any source artifact as current source input.
* Review exact live path allowlist for input manifest / facts / decisions / overlay support.
* Review all `CURRENT_FACTS=6` and `2105` role classifications.
* Review source-overlay execution mode decision before Change 4.
* Review `body_source_overlay` contract so it cannot become source authority or quality pass.
* Review overlay-support write authorization only as future authorization-gated materialization, not as this plan's executable step.
* Review row-level overlay coverage and `Base.CanOpener` focused trace.
* Review Layer4 trace role matrix and actual consumer read path graph for accidental source-authority promotion.
* Review required-validation manifest patch before any live adoption.
* Review required-validation gate status enum and tooling allowlist invariant report.
* Review final residual classification if full current-route does not pass.
* Review independent review gate status.
* Review final claim boundary for no release / package / runtime overclaim.

### Validation Limits

This plan will not validate:

* manual in-game QA
* Workshop/package release validation
* B42 readiness validation
* long-session runtime validation
* external mod compatibility sweep
* public-facing Korean text quality acceptance
* semantic quality remeasurement
* `quality_state` UI exposure
* live migration apply validation
* runtime chunk replacement validation
* package zip final release validation
* off-surface data files or live ledger values beyond explicit execution-side validation

---

## 8. Risk Surface Touch

### Authority Surface

Touched as read-only consumption contract diagnosis, authorization request, and validation evidence. It is not baseline redefinition.

This plan clarifies and gates current-route baseline/source-overlay consumption. It must not update live `data/` current-route materialization targets. It must not mutate adopted vNext Baseline definition, source adjudication, Lua bridge, package payload, denominator, terminal disposition, shared disposition sealed authority, or runtime surfaces.

If overlay-support write mode is planned, it is future authorization-gated materialization only and must not add fixture-only rows to the selected source universe.

### Runtime Behavior Surface

None intended.

Runtime Lua behavior, Browser / Wiki / Tooltip behavior, Lua bridge payload, runtime chunks, and package payload are not changed.

### Compatibility Surface

External compatibility surface: none expected.

Internal build / validation surface impact exists. Current-route runners, validators, compose routes, and required-validation manifests may fail earlier when baseline/source-overlay contracts are ambiguous or violated.

Internal compatibility concern remains for fixture / historical / diagnostic routes if `6` and `2105` route roles are collapsed. This plan requires route separation before Phase 2+ work.

### Sealed Artifact Surface

Touched as read-only input and additive evidence.

Denominator lock, terminal disposition, shared disposition consumption, live migration readiness, and vNext readpoints are referenced but not re-adjudicated.

### Public-Facing Output Surface

None.

No README release claim, Workshop copy, in-game UI, tooltip, Browser, Wiki, or public text changes are part of this plan.

---

## 9. Risk Analysis

### Architecture Risk

* `CURRENT_FACTS=6` fixture can be mistaken for full current authority.
* `2105` can be mistaken for predecessor restoration rather than branch-specific baseline count.
* vNext Baseline can be mistaken as absent, leading to unnecessary re-baselining instead of reconnecting live materialization.
* `Base.CanOpener` can be mistaken as a missing 2105 overlay row rather than a fixture leak from a split live materialization.
* Baseline branch selection can be skipped, making downstream overlay work ambiguous.
* Selected baseline branch can fail to reconcile with the sealed runtime-deployable bundle, making full current-route closure hollow.
* `body_source_overlay` can be over-read as source authority.
* Overlay-support write mode can become an unapproved source-authority mutation if target and validator are not pinned.
* Layer4 trace can drift into source authority or overlay authority.
* A new input packet can become an unintended dual authority.
* Independent review can be mistaken as satisfied by the attached WARN review, even though it does not close the hard gate.

### Runtime Risk

* Direct runtime risk is low because runtime surfaces are out of scope.
* Risk rises if a repair path writes runtime chunks, Lua bridge data, rendered output, live source files, or package payload to force validation to pass without sealed authorization.
* Generic fallback body generation would hide evidence gaps and must fail validation.

### Compatibility Risk

* Internal tools may depend on the 6-entry fixture route and fail if the route is renamed or reclassified carelessly.
* Historical / diagnostic route tests may break if `2105` is globally imposed without role separation.
* Required-validation adoption can affect current-route tooling closure and allowlist if added without reviewed scope.
* External mod compatibility risk is low because no public API or runtime behavior change is planned.

### Regression Risk

* `Base.CanOpener` can be patched into overlay support instead of removing the fixture leak from full current-route consumption.
* Live input manifest / facts / decisions / overlay support can remain partially connected to different row universes.
* Peer compose-target rows can remain uncovered after a focused `Base.CanOpener` fix.
* Composer and validator can read different row universes but still pass focused tests.
* Selected branch universe can match itself while failing runtime-deployable bundle reconciliation.
* Layer4 trace role can be correct in docs but wrong in executable route.
* Required-validation manifest patch can remain candidate-only while closeout wording implies adopted guard.
* `source_overlay_gap` residual can be misclassified as unrelated residual.
* Full current-route PASS can be overclaimed as release readiness or runtime cutover.

---

## 10. Rollback Plan

Rollback is limited to contract, tooling, validation, docs, and generated evidence.

* Phase artifacts under `Iris/build/description/v2/staging/dvf_3_3_current_route_baseline_source_overlay_repair/` can be regenerated, superseded, or discarded without mutating current authority.
* This plan must not execute live materialization reconnect. A future authorized reconnect round must define rollback snapshots for the exact allowlisted target paths.
* If baseline branch selection is wrong, supersede `baseline_branch_decision_packet.md` and rerun downstream phases.
* If runtime-deployable reconciliation fails, stop Phase 2+ and close as `blocked` or redefine the route name as non-full with explicit residual.
* If `CURRENT_FACTS=6` reclassification breaks fixture / historical / diagnostic routes, revert those route-name / expected-contract changes and keep the full current-route contract isolated.
* If `2105` is incorrectly imposed as global expected count, revert that change and retain surface-specific count roles.
* If any attempted overlay materialization appears before authorization, stop and classify it as out-of-scope mutation.
* If `Base.CanOpener` or any fixture-only row is added to the Branch A overlay support artifact, revert that row write and classify it as fixture leak / stale current-like surface evidence.
* If overlay-support write target is wrong, revert only that support artifact and its writer/validator wiring.
* If a `body_source_overlay` value lacks acceptable source support, remove it and classify the row as blocker or exception.
* If Layer4 trace is consumed as source authority, downgrade that route to diagnostic/support role or hard-fail it.
* If required-validation live adoption regresses current-route closure, revert only the manifest adoption and preserve the candidate patch/report.
* New tools, tests, or validators introduced by this plan must be rollback units independent of current-route core closure and tooling allowlist.
* If dirty worktree isolation fails, stop and do not stage or revert unrelated user changes.
* Adopted vNext Baseline definition, source adjudication, live current-route materialization targets, Lua bridge payload, package output, and sealed predecessor reports are not rollback targets because this plan must not mutate them.

---

## 11. Governance Constraints

* Preserve `docs/Philosophy.md` compliance.
* Preserve Hub & Spoke / SPI boundaries.
* Preserve Iris as offline evidence/outcome/source producer plus runtime display consumer.
* Preserve DVF 3-3 current authority chain: `source -> facts -> decisions -> rendered -> Lua bridge -> runtime chunks`.
* Preserve runtime/build-time separation.
* Preserve FAIL-LOUD behavior for missing source baseline, missing overlay, dual authority, and forbidden execution authority reads.
* Preserve additive amendment / supersession preference.
* Preserve terminal disposition and denominator readpoints; do not reopen adjudication.
* Preserve shared disposition consumption readpoint; do not re-adopt or redefine it in this round.
* Preserve `adopted / unadopted` as current runtime vocabulary, not quality/pass/publish/delete semantics.
* Preserve `active / silent` as non-current vocabulary.
* Preserve `body_source_overlay` as compose support input, not source authority.
* Preserve explicit source-overlay execution mode. Missing overlay cannot be silently repaired outside the selected mode.
* Preserve `source_overlay_gap` as a blocker for full current-route compose targets.
* Preserve Layer4 trace as diagnostic/support/validation input only.
* Preserve `CURRENT_FACTS=6` role classification before deletion, replacement, or route reinterpretation.
* Preserve `2105` role classification before adopting it as full current-route expected count.
* Preserve selected branch to runtime-deployable bundle row-identity reconciliation as a future complete closeout precondition.
* Preserve raw audit / readiness / dry-run / predecessor artifacts as provenance, not direct execution authority.
* Preserve protected source / rendered / Lua bridge / runtime / package no-mutation. Live materialization exceptions require a separate sealed-authorized reconnect round and are not opened by this plan.
* Preserve current-route core closure and tooling allowlist cap unless separately reviewed.
* Preserve candidate/adopted status distinction for required-validation manifest changes.
* Preserve `required_validation_gate_status = not_attempted | candidate_only` in this plan's final reporting. `adopted_required_gate` is reserved for a later sealed-authorized reconnect round.
* Preserve independent review gate as a hard precondition for `complete`, canonical PASS, seal, and adopted required gate claim.
* Preserve `COMMON-RELEASE-NONDECISION` and `COMMON-RUNTIME-SURFACE-NONMUTATION` boundaries in closeout / ledger packet.
* Do not claim release readiness, package readiness, Workshop readiness, B42 readiness, deployment readiness, manual QA, runtime rollout, public exposure, or semantic quality completion.

---

## 12. Expected Closeout State

Expected closeout target: `partial` with `sealed_bounded_repair_packet` evidence if the current 2105 live readpoint, authorization/review evidence, and repair packet reports remain valid. Use `blocked_authorized_reconnect_pending`, `blocked_provenance_alignment`, or `revised_plan_needed` only if verification rediscovers drift, missing authorization/review, or plan-path mismatch that prevents canonical trace.

This plan now verifies the existing bounded repair packet for the full current-route baseline/source-overlay failure. It does not execute additional live source materialization writes and does not claim release, deployment, package, runtime replacement, or manual QA readiness. Existing authorized reconnect evidence may be consumed only as evidence, not as permission to expand live write scope.

Realistic execution expectation is `partial` if the repair packet remains PASS and claim boundaries are preserved. `partial` here means bounded repair packet sealed, not broad project completion. If the repair runner or evidence continues to cite the predecessor `...repair_plan.md` without an explicit relationship to this restored `...repair_problem7_plan.md`, close as `blocked_provenance_alignment` until the plan-path authority is reconciled.

`partial` requires:

* full current-route failure snapshot is captured and classified as baseline/source-overlay scope.
* `CURRENT_FACTS=6` predecessor failure / fixture role classification is complete and it is not consumed as current authority.
* `2105` role classification is complete.
* full current-route baseline branch decision is recorded against the current 2105 live readpoint.
* selected baseline expected count and facts-source contract are explicit.
* selected baseline branch row universe is reconciled to the sealed runtime-deployable bundle by row identity.
* split-materialization / fixture-leak hypothesis is confirmed or falsified.
* existing authorized reconnect status is recorded, or missing status blocks repair-packet seal.
* adopted source artifact cross-attestation is recorded.
* properly sealed canonical baseline identity status is recorded.
* authorized reconnect report or no-reconnect-needed status is recorded; a new authorization request is required only if drift is rediscovered.
* exact live target path allowlist is recorded as bounded repair evidence.
* live input manifest, facts, decisions, and overlay support row-universe diagnostic is recorded.
* `Base.CanOpener` is classified as Branch A source member or fixture-leak symptom before any overlay action.
* fixture / historical / diagnostic routes are separated from full current-route claim.
* canonical roadmap docs artifact and restored Problem 7 plan are included in independent review / provenance input, or the plan-path relationship is explicitly reconciled.
* source-overlay execution mode is selected and validated.
* `body_source_overlay` requirement contract is written.
* exception reason codes are explicit.
* adopted compose target inventory is complete for the selected baseline branch.
* runtime-adopted compose target rows have row-level disposition recorded as overlay coverage, explicit non-blocking exception, or `source_overlay_gap` blocker.
* `source_overlay_gap` blocker count is recorded. For the current bounded repair packet it must be `0`; if it becomes non-zero, close as blocked or revised-needed rather than claiming the packet sealed.
* `Base.CanOpener` is not present as a full current-route blocker unless selected Branch A source identity contains that row. If it is fixture-only, it is resolved by route separation / live materialization reconnect, not by adding a 2105 overlay row.
* compose route, current-authority validator, and Layer4 trace consumer use the same baseline/source-overlay contract.
* actual consumer read path graph confirms compose / current-authority / Layer4 consumers read the expected contract.
* Layer4 trace is not promoted to source authority.
* raw audit / readiness / dry-run / predecessor artifacts are not direct execution authority.
* no dual-authority read path remains.
* protected source / rendered / Lua bridge / runtime / package changed_count is `0`.
* required-validation guard status is recorded without new adopted required-gate mutation.
* full current-route validation result is recorded if run, or skipped/blocked reason is recorded.
* residual classifications are explicit.
* any residual touching baseline/source-overlay, live materialization reconnect, runtime-deployable reconciliation, source-overlay gap, compose alignment, Layer4 trace consumption, or forbidden authority read blocks `complete`; explicitly out-of-scope residuals must be named separately and cannot support a closure claim.
* independent review gate status is recorded for both canonical roadmap artifact and this restored Problem 7 plan, or the existing review packet explicitly reconciles the predecessor plan artifact relationship.
* final report and ledger packet include claim boundary and non-claims.

Before claiming any broader `complete` outside this bounded repair packet, a later round must add:

* `current_route_materialization_write` mutation class is defined and validated for any additional live write.
* live materialization write has pre/post hash, diff-to-adopted-source, row identity match, rollback snapshot, and no extra / no missing row reports, if any new write occurs.
* required-validation guard status may be `adopted_required_gate` only after sealed authorization and current-route runner validation.
* full current-route validation exits code `0`.
* `source_overlay_gap` blocker count is `0` for full current-route compose targets.
* all in-scope residual classifications are empty.

Allowed alternate closeout states:

* `partial`: classification / contract / coverage work is partly complete but one or more planned gates remain unresolved.
* `implemented_only`: docs, tools, or tests exist but required validation did not run.
* `blocked`: baseline branch decision, required authority input, validation tool, review decision, or protected no-mutation gate blocks safe completion.
* `blocked_authorization_pending`: live materialization reconnect is required but sealed current-cutover authorization is absent.
* `blocked_authorized_reconnect_pending`: authorization exists but current live facts / decisions / overlay do not match the 2105 manifest.
* `blocked_provenance_alignment`: repair evidence passes but plan-path authority between `...repair_plan.md` and `...repair_problem7_plan.md` is not reconciled.

Blocked examples:

* baseline branch decision is missing.
* `CURRENT_FACTS=6` remains both fixture and full current baseline.
* live input manifest / facts / decisions / overlay support do not share one selected Branch A row universe.
* sealed current-cutover authorization is missing but live reconnect is required.
* adopted source artifact cross-attestation is missing.
* properly sealed canonical baseline identity is missing.
* `Base.CanOpener` is patched into 2105 overlay support without Branch A source membership.
* `2105` is consumed without surface-specific role classification.
* selected branch fails runtime-deployable bundle row-identity reconciliation.
* non-2105 universe is called full current route without runtime-deployable reconciliation.
* source-overlay execution mode is missing.
* adopted compose target is missing `body_source_overlay` and no row-level disposition is recorded as non-blocking exception or `source_overlay_gap` blocker.
* `source_overlay_gap` remains on any full current-route compose target but is not recorded as a blocker disposition, or complete / canonical PASS / seal / adopted gate is claimed while the gap is non-zero.
* Layer4 trace is consumed as source authority.
* actual consumer read path graph is missing or diverges from declared matrix role.
* raw predecessor/readiness artifact is consumed as execution authority.
* required-validation adoption is claimed but only a candidate patch exists.
* `required_validation_gate_status` is absent or outside the allowed enum.
* complete / canonical PASS / seal / adopted gate is claimed while independent review gate is missing, self-generated, or not PASS.
* protected runtime/package/source/rendered surface changes unexpectedly.

Maximum final claim:

```text
The full current-route failure has been diagnosed against baseline,
source-overlay, split-materialization, fixture-leak, and read-path evidence.
If live current-route materialization reconnect is required, this plan produced
the accepted authorization artifact criteria, source cross-attestation
requirements, authorized write runner boundary, source priority rule, mutation
class, exact target allowlist, validation requirements, and authorization
request. The plan did not execute reconnect, claim complete, claim canonical
PASS, or adopt a required gate.
```

This final claim does not authorize terminal disposition re-adjudication, denominator redefinition, shared disposition re-adoption, live migration execution, adopted vNext Baseline redefinition, source adjudication mutation, live materialization writes, Lua bridge mutation, runtime chunk replacement, package route release readiness, Workshop readiness, B42 readiness, deployment readiness, manual in-game QA, public-facing text quality acceptance, semantic quality completion, `quality_state` UI exposure, publish policy change, `active / silent` vocabulary restoration, or Layer4 trace source-authority promotion.
