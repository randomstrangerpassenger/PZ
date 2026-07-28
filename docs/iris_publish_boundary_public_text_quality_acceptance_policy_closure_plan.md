# Implementation Plan

> 상태: owner-directed `aa49e8f9` four-plan synchronized implementation plan; synchronization-only revision requires no additional plan-level review; Foundation Track waits for G1/G2/G3 and official Phase 0 waits for G5 immutable handoff
>
> 대상: Iris Publish Boundary / Public Text Quality Acceptance Policy Closure
>
> 기반 로드맵: `Iris Publish Boundary — Public Text Quality Acceptance Policy Closure Roadmap`
>
> 동기화 대상: `docs/dvf_3_3_korean_prose_naturalization_public_text_rewrite_closure_plan.md`
>
> 교차 계획 계약: `dvf3_3_korean_naturalization__publish_boundary_sync_v1`
>
> 로드맵 입력 SHA-256 planning observation:
> `4b28e1fd3302877de81d85b14b6a7facd79b5b97a09e6db5aa5bcf8e2d4b07b9`
>
> 역사적 작성 기준 checkout: `main` / `129c6c124ffa5a6b671041c6ab86675c660fb494`
>
> 공통 실행 ancestry/readpoint: `aa49e8f9fce19955a374b45d0744b1418a45ac9e`
>
> 주의: 이 문서의 checkout, hash, count는 계획 수립 시점의 관찰값이다. 실행 authority나 threshold가 아니며 Phase 0에서 전부 재측정한다. 이번 coordination-only 동기화는 policy, threshold, waiver, metric 또는 terminal predicate를 바꾸지 않으며 추가 plan-level review를 요구하지 않는다.

## 0. `aa49e8f9` Four-Plan Synchronization Contract

이 계획은 공통 계약 `iris_aa49_four_plan_execution_sync_v1`에서 `G4_publish_boundary_foundation`과 `G6_publish_boundary_official_phase0_through_phase7`을 소유한다. `aa49e8f9fce19955a374b45d0744b1418a45ac9e`는 immutable ancestry/planning readpoint이며, 그 commit에는 이 계획을 포함한 네 plan blob 전부가 없으므로 직접 execution base가 아니다.

`G0_plan_set_materialization_and_owner_sync`는 네 exact plan blob과 SHA-256, 공통 projection을 clean descendant commit에 tracked 상태로 materialize한다. 현재 dirty planning worktree의 staged/unstaged/untracked implementation, staging, candidate 또는 prior official-attempt 산출물은 자동 편입하지 않는다. 이번 개정은 owner-directed synchronization-only 변경이므로 추가 plan-level review를 요구하지 않는다.

네 계획이 동일하게 소비할 canonical compact-JSON projection은 다음과 같다.

```json
{"authority_boundaries":{"clean":"validation_reproducibility_only","food":"sealed_non_current_successor_only","naturalization_phase8":"immutable_candidate_handoff_only","naturalization_terminal":"requires_publish_accepted_and_policy_closure_complete","publish_foundation":"authority_effect_none","publish_official":"accepted_required_before_live_gate","registry_cutover":"separate_registry_owned_plan"},"baseline_commit":"aa49e8f9fce19955a374b45d0744b1418a45ac9e","baseline_role":"immutable_ancestry_and_planning_readpoint_only","contract_id":"iris_aa49_four_plan_execution_sync_v1","fresh_attempt_rules":{"clean":"fresh_phase0_from_plan_set_commit","food":"fresh_attempt_from_change0_no_attempt_0007_reuse","naturalization":"fresh_attempt_from_phase0_do_not_resume_attempt_0014","publish":"fresh_official_attempt_from_phase0_do_not_resume_attempt_0003"},"owner_directive":"synchronization_only_no_additional_plan_level_review","plan_paths":["docs/iris_clean_checkout_full_repository_validation_reproducibility_authority_closure_plan.md","docs/dvf_3_3_food_semantic_facts_authority_reconstruction_implementation_plan.md","docs/dvf_3_3_korean_prose_naturalization_public_text_rewrite_closure_plan.md","docs/iris_publish_boundary_public_text_quality_acceptance_policy_closure_plan.md"],"prerequisite_closures":{"registry_authority":"canonical_complete","registry_runtime_compatibility":"canonical_complete"},"stage_order":["G0_plan_set_materialization_and_owner_sync","G1_clean_checkout_full_repository_validation","G2_food_semantic_facts_authority","G3_registry_food_successor_operational_cutover","G4_publish_boundary_foundation","G5_naturalization_phase0_through_phase8","G6_publish_boundary_official_phase0_through_phase7","G7_naturalization_terminal_finalize"]}
```

```text
four_plan_sync_projection_sha256 = 12c32873dc7e16e0d64e416bdb6693599e2790e9fc129606a90a72ca745a6eb0
```

| Global stage | Publish Boundary relationship |
|---|---|
| `G0_plan_set_materialization_and_owner_sync` | 네 plan blob/projection equality를 결속한다. |
| `G1_clean_checkout_full_repository_validation` | terminal PASS가 없으면 이후 계획 실행을 금지한다. |
| `G2_food_semantic_facts_authority` | fresh Food attempt가 sealed non-current successor를 만든다. |
| `G3_registry_food_successor_operational_cutover` | successor facts/manifest current adoption receipt를 만든다. |
| `G4_publish_boundary_foundation` | 이 계획의 Foundation Track F만 실행하며 official attempt를 만들지 않는다. |
| `G5_naturalization_phase0_through_phase8` | 새 Naturalization attempt가 foundation을 소비해 immutable handoff를 만든다. |
| `G6_publish_boundary_official_phase0_through_phase7` | `attempt-0003`을 재개하지 않고 새 official Phase 0 attempt를 연다. `accepted`만 Phase 6/7로 진행한다. |
| `G7_naturalization_terminal_finalize` | accepted/complete Publish 결과를 Naturalization이 역인계 받아 종결한다. |

G1~G3 중 하나라도 complete/PASS가 아니면 Foundation Track F를 실행하지 않는다. G5 immutable handoff가 없으면 official Phase 0을 열지 않는다. Candidate가 `blocked` 또는 `deferred_internal_debt`이면 Phase 6/7과 G7을 금지하고 새 Naturalization remediation attempt로 반환한다.

## 1. Objective

Iris의 exact public-text evaluation subject에 대해 다음 함수를 소유하고 재현 가능하게 실행하는 Publish Boundary 전용 정책·검증 체계를 구현한다. 독립 current-payload 진단에서는 current runtime payload를 subject로 사용할 수 있지만, 한국어 번역체 개선과 동기화된 canonical execution에서는 DVF naturalization 계획이 만든 immutable candidate와 exact handoff evidence bundle을 subject로 사용한다.

```text
exact acceptance-input binding
+ canonical metric/denominator snapshot
+ sealed acceptance policy
+ applicable waiver set
-> accepted | blocked | deferred_internal_debt
```

구체적인 목표는 다음과 같다.

- evaluation subject kind를 `current_runtime_payload | dvf_3_3_korean_naturalization_candidate`로 명시하고 각 kind의 required constituent와 applicability를 하나의 fresh acceptance input으로 결속한다.
- current subject의 `coverage_quality_candidate`·required-section·adopted/unadopted 축과 naturalization candidate의 semantic preservation·structural satisfaction·raw Korean prose detector·human-review 축을 서로 다른 metric/denominator applicability로 봉인한다.
- 로드맵의 v1 zero-tolerance 정책, 공집합 default exception, debt-only waiver, freshness 규칙을 owner-ratified machine-readable policy로 만든다.
- sealed policy와 exact binding만 소비하는 deterministic, fail-closed validator를 구현한다.
- roadmap mandatory 36개와 plan-additive fixture를 구분해 threshold·denominator·exception·waiver·freshness 우회를 차단한다.
- exact evaluation subject에 정확히 하나의 qualified disposition을 부여한다.
- Publish Boundary-owned required gate를 기존 Legacy Combined DVF Governance Route에 additive하게 연결한다.
- machine result, independent review, owner seal, terminal hash seal을 분리해 policy closure를 닫는다.

본 계획의 최대 허용 claim은 다음과 같다.

```text
Public Text Quality Acceptance Policy Closure: complete
Evaluation subject: current_runtime_payload | dvf_3_3_korean_naturalization_candidate
Qualified disposition: accepted | blocked | deferred_internal_debt
```

독립 current-payload 경로에서는 `Public Text Quality Acceptance Policy Closure: complete`가 current payload의 `accepted`를 뜻하지 않는다. 그러나 `dvf3_3_korean_naturalization__publish_boundary_sync_v1`의 canonical remediation 경로는 candidate가 `accepted`일 때만 live gate adoption과 Phase 7 closure로 진행한다.

---

## 2. Scope

이 계획은 로드맵 Phase 0~7을 현재 Iris 저장소 구조에 맞게 구현하는 범위를 포함한다.

- durable acceptance-input binding
- candidate-independent development foundation contract와 dry-run runner/validator
- canonical entries와 metric projection
- metric/denominator registry와 contract
- v1 normative acceptance policy
- exception/waiver/freshness contract
- policy ratification과 detached hash seal
- fail-closed validator와 실행/검증 wrapper
- adversarial fixture suite와 metamorphic determinism 검증
- exact evaluation-subject disposition
- stale disposition consumption guard
- overclaim scanner
- additive current-route required gate
- required artifact VCS preservation
- independent review, owner seal, closeout, terminal hash seal
- 필요 시 additive top-doc successor entry

### Phase Correspondence

이 계획의 Phase 번호는 roadmap Phase 0~7과 일대일로 대응한다.

| Roadmap phase | Planned change | Attempt artifact root |
|---|---|---|
| Phase 0 | Change 0 — Durable Acceptance-Input Binding | `<attempt-root>/phase0/` |
| Phase 1 | Change 1 — Metric and Denominator Contract | `<attempt-root>/phase1/` |
| Phase 2 | Change 2 — Normative Policy Adoption | `<attempt-root>/phase2/` |
| Phase 3 | Change 3 — Validator Implementation | `<attempt-root>/phase3/` |
| Phase 4 | Change 4 — Adversarial Review and Negative Fixtures | `<attempt-root>/phase4/` |
| Phase 5 | Change 5 — Exact Evaluation-Subject Disposition | `<attempt-root>/phase5/` |
| Phase 6 | Change 6 — Gate Integration and Overclaim Guard | `<attempt-root>/phase6/` |
| Phase 7 | Change 7 — Independent Closeout, Owner Seal, and Policy Closure | `<attempt-root>/phase7/` |

Change 7의 `Phase 0~6 claim-bearing artifact`는 이 계획의 Phase 0부터 Phase 6까지를 뜻한다. 저장소에 이미 존재하는 다른 round의 `phase0`~`phase6` staging evidence는 predecessor/external readpoint일 뿐 이 계획의 phase artifact로 재분류하지 않는다.

### Cross-Plan Canonical Execution Order

교차 계획 계약 `dvf3_3_korean_naturalization__publish_boundary_sync_v1`의 실행 순서는 다음 하나로 고정한다.

| Sync stage | Owning plan | Allowed work | Required exit |
|---|---|---|---|
| `S0_plan_sync` | 양쪽 계획 | 공통 schema, enum, artifact path, freshness, claim boundary를 동결 | 두 계획의 sync-contract projection hash 일치 |
| `S1_publish_foundation` | 이 계획 | candidate-independent metric/denominator/policy-candidate schema, detector mapping, human-review selection contract, runner/validator, fixture, dry-run 구현 | `foundation_contract_ready_for_remediation=true` |
| `S2_naturalization_build` | DVF naturalization 계획 | 그 foundation hash를 소비해 corpus, proposition/structural contract, compiler, candidate, semantic/raw-detector/human-review evidence 생성 | immutable Phase 8 handoff bundle 생성 |
| `S3_publish_official_attempt` | 이 계획 | handoff bundle을 subject로 fresh Phase 0부터 Phase 7까지 실행 | candidate `accepted`, live gate adopted, policy closure complete |
| `S4_naturalization_finalize` | DVF naturalization 계획 | exact Publish disposition/closure hash를 역인계 받아 compiler gate, Registry packet, terminal closure 수행 | naturalization closure complete |

이 local `S0~S4` contract는 전역 계약에 다음처럼 매핑한다.

```text
S0_plan_sync               = G0_plan_set_materialization_and_owner_sync의 Naturalization/Publish projection
S1_publish_foundation      = G4_publish_boundary_foundation
S2_naturalization_build    = G5_naturalization_phase0_through_phase8
S3_publish_official        = G6_publish_boundary_official_phase0_through_phase7
S4_naturalization_finalize = G7_naturalization_terminal_finalize
```

`S1_publish_foundation`은 roadmap Phase 0 이전의 **pre-attempt development track**이다. 다음 field를 가진 tracked foundation contract와 readiness report를 만들지만 official acceptance attempt, policy seal, disposition, live gate adoption 또는 closure를 만들지 않는다.

```text
synchronization_contract_id
foundation_contract_version
metric_registry_candidate_hash
denominator_registry_candidate_hash
policy_candidate_hash
detector_mapping_candidate_hash
human_review_selection_contract_hash
runner_validator_interface_hash
required_handoff_schema_hash
foundation_contract_ready_for_remediation = true
authority_effect = none
official_disposition = not_issued
live_gate_adopted = false
policy_closure_state = not_started
```

foundation contract를 바꾸면 그 hash를 소비한 naturalization corpus, candidate, review와 handoff가 모두 stale이다. 반대로 candidate 결과를 본 뒤 foundation threshold, blocker mapping 또는 denominator를 그대로 고쳐 통과시키는 것은 금지하며, 변경이 정당하게 필요하면 새 foundation version과 naturalization earliest-affected phase부터 재실행한다.

`S3_publish_official_attempt`만 이 계획의 formal Phase 0~7을 실행한다. candidate가 `blocked` 또는 `deferred_internal_debt`이면 `adoption_timing=after_remediation`으로 attempt를 incomplete하게 보존하고 naturalization retry로 반환한다. synchronized canonical 경로에서는 blocked candidate의 `adoption_timing=immediate`를 사용하지 않는다.

naturalization Phase 8 handoff의 required constituent ID는 다음과 같다.

```text
naturalization_attempt_id
foundation_contract_hash
candidate_rendered_hash
candidate_manifest_hash
source_proposition_manifest_hash
body_plan_requirement_digest
structural_satisfaction_ledger_hash
semantic_preservation_report_hash
raw_detector_report_hash
human_review_sample_manifest_hash
human_review_decision_hash
compiler_implementation_hash
korean_prose_policy_hash
corpus_manifest_hash
protected_surface_no_mutation_report_hash
requested_evaluation_subject_kind = dvf_3_3_korean_naturalization_candidate
```

accepted official result의 naturalization 역인계 field는 다음과 같다.

```text
evaluation_subject_kind = dvf_3_3_korean_naturalization_candidate
evaluation_subject_hash = candidate_rendered_hash
consumed_handoff_manifest_hash = exact Phase 8 handoff hash
consumed_foundation_contract_hash = exact naturalization Phase 0 bound foundation hash
qualified_disposition = accepted
publish_policy_closure_state = complete
publish_live_required_gate_adopted = true
registry_runtime_current_adoption_claimed = false
```

두 계획이 canonical JSON으로 투영해 hash를 비교할 synchronization projection은 다음 field를 정확히 사용한다.

```text
synchronization_contract_id
canonical_stage_order = S0_plan_sync,S1_publish_foundation,S2_naturalization_build,S3_publish_official_attempt,S4_naturalization_finalize
foundation_required_state
evaluation_subject_kind_enum
candidate_structural_status_enum
required_handoff_constituent_ids
nonaccepted_candidate_action = after_remediation
blocked_immediate_allowed_for_synchronized_candidate = false
candidate_runtime_parity_applicability = not_applicable
candidate_runtime_parity_reason = candidate_not_registry_adopted
publish_owns_metric_mapping_threshold_waiver_disposition = true
dvf_owns_proposition_discourse_realization_raw_detector = true
```

### Explicitly Out Of Scope

- `dvf_3_3_facts.jsonl`, `dvf_3_3_decisions.jsonl`, overlay, profile, identity/precedence rule의 내용 변경
- current rendered payload 재작성 또는 current output path write
- Lua bridge, runtime chunk manifest, runtime chunks, package payload 변경
- source item key의 merge, rename, winner selection
- 문장 rewrite 또는 blocked payload 자동 remediation
- item별 semantic exception 판정
- source 사실 정확성의 신규 판정, 실용성·게임플레이 추천성의 신규 판정
- naturalness 문장을 직접 생성·교정하는 행위. 단, exact candidate에 대한 raw detector와 denominator-qualified human review를 sealed policy로 분류하는 acceptance 판정은 in scope다.
- Browser/Wiki/Tooltip의 quality badge, 정렬, 필터, 숨김, 추천, trust/confidence 표시
- runtime `quality_state`, `publish_state`, `runtime_state` 추가 또는 변경
- DVF System / DVF Body Compiler 책임 확대
- Registry Authority 또는 Registry Runtime Compatibility 재개방
- current core 12-module closure 또는 tooling allowlist cap 1 확대
- package publication, release, Workshop publication
- B42/deployment readiness
- manual/in-game QA
- multiplayer/long-session/external-mod compatibility sweep
- `Publish Boundary PASS` 또는 `semantic-quality-complete` 선언

---

## 3. Non-Goals

- current payload나 naturalization candidate를 `accepted`로 만들기 위해 threshold, exception, waiver를 역산하지 않는다.
- `adequate`나 `strong` 비율을 semantic-quality PASS로 사용하지 않는다.
- `unadopted`를 `weak` 또는 public-text quality failure로 재분류하지 않는다.
- ignored rendered JSON을 durable acceptance authority로 승격하지 않는다.
- Publish Boundary validator가 source, profile, policy, exception, waiver, owner decision을 생성하지 않는다.
- validator가 blocker를 직접 수정하거나 source writer를 호출하지 않는다.
- `blocked`를 policy closure 실패와 동일시하지 않는다.
- current-route PASS, DVF Body Compiler PASS, Registry Authority PASS, Registry Runtime Compatibility PASS를 public text acceptance로 대체하지 않는다.
- active waiver가 존재하는 상태를 clean `accepted`로 축약하지 않는다.
- machine-generated verdict로 independent review 또는 owner seal을 대체하지 않는다.
- development foundation readiness를 policy ratification, official disposition, live gate adoption 또는 policy closure로 표현하지 않는다.
- Publish Boundary의 naturalness acceptance를 DVF compiler의 문장 생성 책임으로 재흡수하지 않는다.

---

## 4. Assumptions

### Codebase Inspection Summary

계획 작성 시점에 확인한 현재 구조는 다음과 같다.

- `Iris/build/description/v2/data/dvf_3_3_input_manifest.json`은 tracked current input manifest다.
- facts, decisions, overlay support, `compose_profiles_v2.json`, identity rules, precedence rules는 tracked다.
- `Iris/build/description/v2/output/dvf_3_3_rendered.json`은 `.gitignore`에 의해 ignored이며 current durable writer surface가 아니다.
- runtime authority는 tracked `IrisLayer3DataChunks.lua` manifest와 tracked chunk 11개다.
- current rendered planning observation은 total 2,105 / adopted 2,084 / unadopted 21이다.
- current rendered planning observation은 weak 1,040 / adequate 729 / strong 315다.
- required-section planning observation은 missing-any row 1,507, missing occurrence 1,508이다.
- section별 missing planning observation은 context 537 / limitation 917 / use 54다.
- rendered raw SHA-256 planning observation은 `4ebdb0b6c381fb07d8a61517133c7f61483d979563fc9c0e6ebbb8f2359fa50d`다.
- rendered `entries_sha256` planning observation은 `6ef48bcf84183ea6700b3768431cbbcf77340aef224f4f45ac4e7195b426cfed`다.
- 위 수치는 Phase 0 fresh remeasurement 전에는 disposition evidence가 아니다.
- `compose_layer3_text.build_rendered()`는 모든 direct write에서 explicit `compose_context`를 요구한다.
- isolated regeneration은 current context가 아니라 explicit `compose_context="staging"`과 attempt-local output path를 사용해야 한다.
- `compose_layer3_body_profile.derive_coverage_quality_candidate()`가 current weak/adequate/strong 계산 의미를 소유한다.
- `docs/dvf_3_3_korean_prose_naturalization_public_text_rewrite_closure_plan.md`는 synchronized candidate producer이며, source proposition inventory, structural satisfaction ledger, semantic preservation, raw detector, exact-hash human-review evidence와 candidate manifest를 Publish Boundary handoff로 제공한다.
- `dvf_3_3_registry_runtime_compatibility.py`에는 exact case-sensitive runtime chunk reconstruction과 runtime projection 로직이 존재한다.
- current-route runner는 `round3_active_core_closure.json`의 12개 current module과 1개 tooling module만 in-process import로 허용한다.
- 새 Publish Boundary current-route test는 validator를 standalone subprocess로 실행해 current core/tooling allowlist를 확대하지 않아야 한다.
- live `current_route_required_validations.json`은 planning observation 기준 required artifact 149개, required test 56개다. 실행 시 재계량하며 이 수를 상수로 사용하지 않는다.
- 현재 worktree에는 기존 drift-verification staging evidence 49개가 수정되어 있다. 이 변경은 사용자 소유이며 본 계획의 실행 evidence에 흡수하거나 덮어쓰지 않는다.

### Repository and Environment Assumptions

- 실행은 repository root에서 PowerShell로 수행한다.
- Python command는 `uv run python -B`를 사용한다.
- required execution tool은 `uv`, Python, Git, PowerShell, Lua syntax checker와 그 checker가 요구하는 dependency다.
- `jq`와 `rg`는 optional inspection convenience다. 사용할 수 없으면 authoritative JSON/identity 검사는 Python으로, 비권위적 text inspection은 PowerShell로 동일하게 수행한다.
- exact case-sensitive key/JSON projection은 `jq` 또는 PowerShell object materialization에 의존하지 않고 Python production parser/validator path를 사용한다.
- Lua syntax 검사는 `powershell -ExecutionPolicy Bypass -File .\tools\check_lua_syntax.ps1`을 사용한다.
- required execution tool이 없으면 해당 validation은 `blocked`다. optional `jq` 또는 `rg` 부재만으로 validation이나 policy closure를 `blocked`로 만들지 않는다.
- actual execution은 기존 dirty checkout을 정리하거나 수정하지 않고, owner-approved clean execution worktree 또는 그와 동등하게 격리·기록된 clean baseline에서 수행한다.
- evidence root는 다음을 기본으로 한다.

```text
Iris/build/description/v2/staging/
  iris_publish_boundary_public_text_quality_acceptance_policy_closure/
    attempts/<attempt_id>/
```

- 같은 attempt의 claim-bearing artifact는 write-once다.
- 재실행이 필요하면 새 `attempt_id`와 새 output root를 사용하고 predecessor failure evidence를 보존한다.
- externally authored owner ratification/waiver/gate-authorization/seal source는 staging output과 분리된 `owner_inputs` 아래에 둔다.
- externally authored independent review source는 owner authority와 분리된 `reviewer_inputs` 아래에 둔다. owner input과 reviewer input은 같은 root나 같은 external input manifest에 섞지 않는다.
- owner 또는 independent reviewer 입력을 기다리는 동안 attempt는 `awaiting_owner_input` 또는 `awaiting_independent_review` 상태로 장기간 열려 있을 수 있다. 이 상태는 closure가 아니며 terminal seal을 만들 수 없다.
- 외부 입력 대기 중 policy/binding/payload/calculator/waiver/reviewer-input freshness가 바뀌면 열린 attempt를 `stale_while_awaiting_external_input`으로 보존 종료하고 Phase 0부터 새 attempt를 연다.

### Authority Assumptions

- source authority, rendered authority, Registry Authority, runtime authority, package identity authority는 이동하지 않는다.
- Publish Boundary는 policy, acceptance-input binding, exact qualified disposition만 새 authority로 소유한다.
- DVF naturalization은 proposition/discourse/surface realization과 raw detector 산출만 소유하고 blocker mapping, threshold, waiver 또는 aggregate disposition을 소유하지 않는다.
- development foundation contract는 remediation target을 동결하는 candidate-independent interface이며 sealed policy closure가 아니다.
- policy owner ratification은 validator가 생성하지 않는다.
- applicable waiver set은 명시적 artifact로 존재해야 하며, waiver가 없을 때도 sealed empty set을 사용한다.
- independent reviewer는 roadmap/plan/implementation author와 분리하고, 자기 산출물을 validator가 대신 작성하지 않는다.
- owner seal은 independent review를 대체하지 않는다.
- user가 이 계획 작성을 요청한 사실은 Phase 2 policy ratification, Phase 6 gate adoption, Phase 7 owner seal을 자동 승인한 것으로 해석하지 않는다.

### Review Decision Resolutions

이번 plan-level feedback의 세 판정 충돌은 다음처럼 보수적으로 고정한다.

1. **Gate adoption은 policy closure의 필수조건이다.**
   - owner가 adoption을 거부하면 write-once non-adoption record를 보존하고 attempt state를 `owner_declined_gate_adoption`으로 닫는다.
   - 이때 policy closure state는 `incomplete`이며 Phase 6 `post_adoption_*` artifact는 `not_applicable`로 대체할 수 없고 Phase 7 finalize/terminal seal을 실행할 수 없다.
2. **Blocked disposition의 live adoption은 informed operational authorization을 요구한다.**
   - owner는 expected official route state, expected exit code, exact blocker attribution, adoption timing을 확인하고 명시적으로 승인해야 한다.
   - `adoption_timing=immediate`이면 remediation 전 official route가 지속적으로 nonzero일 수 있음을 승인한다.
   - `adoption_timing=after_remediation`이면 현재 attempt에서 live adoption과 closure를 진행하지 않는다.
   - synchronized naturalization candidate 경로에서는 `accepted`만 live adoption 대상이다. `blocked` 또는 `deferred_internal_debt`는 `after_remediation`으로 naturalization retry owner에게 반환하며 `immediate` adoption을 금지한다.
3. **Policy ratification은 metric-level affirm을 요구한다.**
   - canonical policy bytes/hash의 포괄 승인만으로 충분하지 않다.
   - ratification record는 registry의 모든 metric에 대해 disposition, threshold, exception, waiver effect를 정확히 한 번씩 owner가 affirm한 증적을 포함해야 한다.
4. **Development foundation과 official attempt를 분리한다.**
   - foundation runner/validator/schema/fixture 구현은 official Phase 0 전에 가능하지만 `authority_effect=none`, `official_disposition=not_issued`를 유지한다.
   - official Phase 0은 naturalization Phase 8 handoff의 immutable candidate/evidence hash가 준비된 뒤 fresh attempt로만 시작한다.
   - official Phase 2에서 ratify하는 policy bytes와 metric/denominator semantics는 foundation contract가 precommit한 candidate-independent projection과 같아야 한다. 차이가 있으면 candidate를 평가하지 않고 stale 반환한다.

### Roadmap Provenance Assumption

현재 로드맵은 repository 바깥의 user-provided input이다. 실행 전에 다음 중 하나를 충족해야 한다.

1. 권장 경로 `docs/iris_publish_boundary_public_text_quality_acceptance_policy_closure_roadmap.md`에 owner-approved 원문을 materialize하고 hash를 결속한다.
2. owner-authored plan approval record가 이 계획에 기록된 roadmap input SHA-256과 소비 범위를 직접 승인한다.

로드맵 provenance가 불명확하면 Phase 0 implementation entry는 `blocked`다.

---

## 5. Repository Areas Affected

### Code

신규 구현 후보:

- `Iris/build/description/v2/tools/build/public_text_quality_acceptance.py`
- `Iris/build/description/v2/tools/build/run_public_text_quality_acceptance.py`
- `Iris/build/description/v2/tools/build/validate_public_text_quality_acceptance.py`
- `Iris/build/description/v2/tests/test_public_text_quality_metric_contract.py`
- `Iris/build/description/v2/tests/test_public_text_quality_acceptance_policy.py`
- `Iris/build/description/v2/tests/test_public_text_quality_acceptance.py`
- `Iris/build/description/v2/tests/test_public_text_quality_acceptance_fixtures.py`
- `Iris/build/description/v2/tests/test_public_text_quality_acceptance_current_route.py`
- `Iris/build/description/v2/tests/fixtures/public_text_quality_acceptance/`

읽기 전용 dependency surface:

- `Iris/build/description/v2/tools/build/compose_layer3_text.py`
- `Iris/build/description/v2/tools/build/compose_layer3_body_profile.py`
- `Iris/build/description/v2/tools/build/_dvf_3_3_vnext_common.py`
- `Iris/build/description/v2/tools/build/dvf_3_3_registry_runtime_compatibility.py`
- `Iris/build/description/v2/data/dvf_3_3_input_manifest.json`
- `Iris/build/description/v2/data/dvf_3_3_facts.jsonl`
- `Iris/build/description/v2/data/dvf_3_3_decisions.jsonl`
- `Iris/build/description/v2/data/dvf_3_3_overlay_support.jsonl`
- `Iris/build/description/v2/data/compose_profiles_v2.json`
- `Iris/build/description/v2/data/compose_profile_identity_hint_rules.json`
- `Iris/build/description/v2/data/compose_profile_conflict_precedence_rules.json`
- `Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks.lua`
- `Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks/*.lua`
- synchronized candidate execution에서 추가로 읽는 naturalization handoff surface:
  - immutable `candidate_rendered.json`
  - `candidate_manifest.json`
  - `source_proposition_manifest.json`
  - `structural_satisfaction_ledger.jsonl`
  - `semantic_preservation_report.json`
  - `raw_detector_report.json`
  - `human_review_sample_manifest.json`
  - externally authored `human_review_decision.json`
  - `publish_acceptance_handoff_manifest.json`

기존 dependency surface 변경은 기본값이 아니다. 실제 구현 결함이 별도로 증명되면 이 계획을 확대하지 않고 correction successor를 연다.

### Docs

신규:

- `docs/iris_publish_boundary_public_text_quality_acceptance_policy_closure_plan.md`
- `docs/public_text_quality_metric_contract.md`
- `docs/public_text_quality_denominator_contract.md`
- `docs/public_text_quality_acceptance_policy.md`
- `docs/public_text_quality_acceptance_claim_boundary.md`
- `docs/public_text_quality_exception_policy.md`
- `docs/public_text_quality_waiver_policy.md`
- `docs/public_text_quality_freshness_policy.md`
- `docs/iris_publish_boundary_public_text_quality_acceptance_policy_closure_closeout.md`
- `docs/dvf_3_3_korean_prose_naturalization_public_text_rewrite_closure_plan.md` (read-only synchronized plan input; 이 계획이 수정하는 구현 산출물은 아님)

조건부 신규:

- `docs/iris_publish_boundary_public_text_quality_acceptance_policy_closure_roadmap.md`

Phase 7 이후 owner-approved additive sync 후보:

- `docs/DECISIONS.md`
- `docs/ARCHITECTURE.md`
- `docs/ROADMAP.md`

top-doc sync는 **Successor Documentation Trace** 방식만 사용한다. terminal seal 이후 owner-approved additive successor entry로 수행하며 sealed execution이나 terminal hash DAG에 다시 편입하지 않는다. successor entry는 sealed terminal hash를 참조하고 다음 두 축을 별도 field로 병기한다.

```text
Policy closure state: complete
Evaluation subject kind: current_runtime_payload | dvf_3_3_korean_naturalization_candidate
Qualified disposition: accepted | blocked | deferred_internal_debt
```

top-doc에는 bare `PASS` 또는 두 축을 합친 단일 상태를 기록하지 않는다.

### Config

- `.gitignore`
  - 신규 tool/test/fixture와 required claim-bearing artifact의 exact path만 선택적으로 unignore한다.
  - `Iris/build/description/v2/staging/**` broad unignore는 금지한다.
  - attempt가 live adoption 전에 중단되거나 owner가 adoption을 거부하면 이 attempt가 추가한 exact unignore line만 base hash/diff에 따라 되돌리고 conditional rollback report를 남긴다.
- `Iris/_docs/round3/current_route_required_validations.json`
  - Phase 6에서 Publish Boundary-owned required artifact/test entry만 additive하게 추가한다.
  - `route`, existing claim/non-claim, existing required entries, Registry/DVF ownership을 변경하지 않는다.
- `Iris/_docs/round3/iris_publish_boundary_public_text_quality_acceptance_policy_closure/foundation/`
  - `public_text_quality_foundation_contract.json`
  - `public_text_quality_development_readiness_report.json`
  - 두 artifact는 tracked, candidate-independent, `authority_effect=none`이며 official disposition이나 closure를 주장하지 않는다.
- `Iris/build/description/v2/owner_inputs/iris_publish_boundary_public_text_quality_acceptance_policy_closure/`
  - policy ratification decision, explicit waiver set, gate adoption decision/authorization, owner seal의 externally authored owner source만 둔다.
  - `policy_ratification_decision.json`은 `decision=ratified|declined`, candidate policy hash, owner identity, rationale, decision timestamp, owner-binding proof를 포함한다.
  - `gate_adoption_decision.json`은 `decision=authorized|declined`, candidate/contract hash, adoption timing, owner identity, rationale, decision timestamp, owner-binding proof를 포함한다.
- `Iris/build/description/v2/reviewer_inputs/iris_publish_boundary_public_text_quality_acceptance_policy_closure/`
  - independent review와 reviewer eligibility declaration의 externally authored reviewer source만 둔다.
  - reviewer source를 owner authorization으로, owner source를 independent review로 재분류하거나 대체하지 않는다.
  - Phase 7 진입 전에 review와 eligibility source는 모두 tracked, not ignored여야 하며 required artifact VCS census에 포함한다.

### Generated Artifacts

기본 root:

```text
<attempt-root> =
Iris/build/description/v2/staging/
  iris_publish_boundary_public_text_quality_acceptance_policy_closure/
    attempts/<attempt_id>
```

Phase 0:

- `<attempt-root>/phase0/evaluation_subject_manifest.json`
- `<attempt-root>/phase0/cross_plan_handoff_binding_report.json` (naturalization candidate subject일 때)
- `<attempt-root>/phase0/current_input_constituent_manifest.json`
- `<attempt-root>/phase0/isolated_regeneration_run1_report.json`
- `<attempt-root>/phase0/isolated_regeneration_run2_report.json`
- `<attempt-root>/phase0/canonical_entries_projection.jsonl`
- `<attempt-root>/phase0/canonical_entries_digest.json`
- `<attempt-root>/phase0/runtime_bundle_reconstruction_report.json`
- `<attempt-root>/phase0/canonical_metric_projection.jsonl`
- `<attempt-root>/phase0/canonical_metric_projection_digest.json`
- `<attempt-root>/phase0/acceptance_input_binding_manifest.json`
- `<attempt-root>/phase0/protected_surface_no_mutation_report.json`
- `<attempt-root>/phase0/vcs_required_surface_preflight.json`

`isolated_regeneration_run*`과 `runtime_bundle_reconstruction_report.json`은 current subject에서만 필수다. synchronized candidate path에서는 `cross_plan_handoff_binding_report.json`, independent canonical projection/recomputation report가 canonical이며 subject-inapplicable artifact를 빈 PASS placeholder로 합성하지 않는다.

Phase 1:

- `<attempt-root>/phase1/metric_registry.json`
- `<attempt-root>/phase1/denominator_registry.json`
- `<attempt-root>/phase1/profile_section_applicability_matrix.json`
- `<attempt-root>/phase1/metric_overlap_and_partition_report.json`
- `<attempt-root>/phase1/unadopted_axis_separation_report.json`
- `<attempt-root>/phase1/metric_denominator_contract_validation_report.json`

Phase 2:

- `<attempt-root>/phase2/public_text_quality_acceptance_policy.json`
- `<attempt-root>/phase2/applicable_waiver_set.json`
- `<attempt-root>/phase2/policy_ratification_record.json` (owner ratified 시)
- `<attempt-root>/phase2/policy_ratification_refusal_record.json` (owner decline 시 조건부)
- `<attempt-root>/phase2/policy_threshold_rationale_report.json`
- `<attempt-root>/phase2/policy_hash_seal.json` (owner ratified 시)

Phase 3:

- `<attempt-root>/phase3/validator_contract_report.json`
- `<attempt-root>/phase3/validator_determinism_report.json`
- `<attempt-root>/phase3/fail_closed_path_report.json`

Phase 4:

- `<attempt-root>/phase4/adversarial_fixture_manifest.json`
- `<attempt-root>/phase4/negative_fixture_results.json`
- `<attempt-root>/phase4/threshold_boundary_report.json`
- `<attempt-root>/phase4/row_occurrence_confusion_report.json`
- `<attempt-root>/phase4/unadopted_axis_attack_report.json`
- `<attempt-root>/phase4/waiver_bypass_attack_report.json`
- `<attempt-root>/phase4/metamorphic_determinism_report.json`
- `<attempt-root>/phase4/adversarial_review.md`

Phase 5:

- `<attempt-root>/phase5/evaluation_subject_metric_snapshot.json`
- `<attempt-root>/phase5/evaluation_subject_raw_metric_report.json`
- `<attempt-root>/phase5/evaluation_subject_disposition.json`
- `<attempt-root>/phase5/evaluation_subject_disposition.md`
- `<attempt-root>/phase5/evaluation_subject_disposition_hash_manifest.json`
- `<attempt-root>/phase5/current_payload_metric_snapshot.json`
- `<attempt-root>/phase5/current_payload_raw_metric_report.json`
- `<attempt-root>/phase5/current_payload_exception_application_report.json`
- `<attempt-root>/phase5/current_payload_waiver_application_report.json`
- `<attempt-root>/phase5/current_payload_effective_finding_report.json`
- `<attempt-root>/phase5/current_public_text_disposition.json`
- `<attempt-root>/phase5/current_public_text_disposition.md`
- `<attempt-root>/phase5/current_disposition_hash_manifest.json`
- `<attempt-root>/phase5/protected_surface_no_mutation_report.json`

`current_payload_*`, `current_public_text_*`, `current_disposition_hash_manifest.json` artifact는 `evaluation_subject_kind=current_runtime_payload`에서만 필수다. synchronized candidate path에서는 `evaluation_subject_*`가 canonical이고 subject-inapplicable artifact를 빈 placeholder로 합성하지 않는다.

Phase 6:

- `<attempt-root>/phase6/required_gate_adoption_contract.md`
- `<attempt-root>/phase6/required_gate_adoption_contract.json`
- `<attempt-root>/phase6/required_gate_candidate.json`
- `<attempt-root>/phase6/required_gate_patch.json`
- `<attempt-root>/phase6/candidate_current_route_result.json`
- `<attempt-root>/phase6/gate_adoption_decision_record.json`
- `<attempt-root>/phase6/owner_declined_gate_adoption_report.json` (owner decline 시 조건부)
- `<attempt-root>/phase6/gitignore_exact_unignore_patch.json`
- `<attempt-root>/phase6/pre_adoption_unignore_rollback_report.json` (중단/거부 시 조건부)
- `<attempt-root>/phase6/required_artifact_recensus_report.json`
- `<attempt-root>/phase6/post_adoption_current_route_result.json` (informed immediate adoption 시)
- `<attempt-root>/phase6/post_adoption_overclaim_scan_report.json` (informed immediate adoption 시)
- `<attempt-root>/phase6/stale_disposition_consumption_guard_report.json`
- `<attempt-root>/phase6/post_adoption_protected_surface_report.json` (informed immediate adoption 시)

Phase 7:

- `<attempt-root>/phase7/final_evidence_freeze_manifest.json`
- `<attempt-root>/phase7/final_artifact_hash_manifest.json`
- `<attempt-root>/phase7/independent_closeout_review.md`
- `<attempt-root>/phase7/independent_review_hash_report.json`
- `<attempt-root>/phase7/owner_canonical_seal_record.json`
- `<attempt-root>/phase7/final_public_text_quality_policy_closure_report.json`
- `<attempt-root>/phase7/terminal_hash_seal.json`

required gate가 소비하는 artifact와 closure가 요구하는 exact owner/reviewer external input만 exact-path unignore와 tracking 대상으로 삼는다. intermediate raw output, temporary regeneration root, negative fixture scratch output은 기본적으로 ignored 상태를 유지한다.

---

## 6. Planned Changes

### Foundation Track F — Candidate-Independent Development Readiness

Purpose:

naturalization 구현이 결과에 맞춰 acceptance 기준을 역산하지 않도록 official attempt 전에 subject-independent contract와 실행 도구를 고정한다.

Global entry:

`G0` synchronized plan-set binding, G1 Clean-Checkout terminal PASS/downstream-unblock receipt, G2 Food sealed-successor terminal closeout와 G3 Registry current-adoption receipt를 exact path/hash로 검증한 뒤에만 이 track을 시작한다. Foundation은 candidate-independent이지만 이 global order는 upstream 변경 직후 foundation이 stale해지는 것을 방지하는 실행 계약이다.

Files:

- tracked `public_text_quality_foundation_contract.json`
- tracked `public_text_quality_development_readiness_report.json`
- metric/denominator/policy schema와 focused test
- raw detector mapping·human-review selection·handoff schema fixture
- development runner/validator

Implementation Notes:

1. 이 track은 official Phase 0~7과 다른 namespace와 `foundation_id`를 사용한다.
2. metric/denominator registry, policy candidate, threshold rationale, detector mapping, human-review selection, handoff schema와 runner/validator interface는 candidate content나 candidate metric을 입력으로 읽지 않는다.
3. current payload dry-run은 detector coverage와 tool operability 진단에만 사용하고 official disposition을 발행하지 않는다.
4. foundation artifact는 tracked, exact hash, owner-reviewed remediation target이어야 하지만 policy ratification, independent closeout, gate adoption 또는 terminal seal로 표현하지 않는다.
5. naturalization 계획은 이 exact foundation hash를 Phase 0 prerequisite로 소비한다.
6. foundation 변경은 새 version을 요구하고 기존 naturalization candidate/review/handoff를 stale하게 만든다.

Validation:

```text
four_plan_sync_projection_sha256_match = true
clean_validation_terminal_pass = true
food_sealed_successor_terminal_closeout = true
registry_food_successor_adoption_receipt_valid = true
foundation_contract_ready_for_remediation = true
candidate_content_dependency_count = 0
candidate_metric_dependency_count = 0
authority_effect = none
official_disposition = not_issued
live_gate_adopted = false
policy_closure_state = not_started
naturalization_required_handoff_schema_complete = true
foundation_runner_validator_fixture_pass = true
```

---

### Change 0 — Durable Acceptance-Input Binding

Purpose:

declared evaluation subject, source authority, subject-specific evidence constituent와 canonical metric projection을 하나의 fresh acceptance input으로 결속한다.

Files:

- 신규 `public_text_quality_acceptance.py`
- 신규 `run_public_text_quality_acceptance.py`
- Phase 0 generated artifacts
- 읽기 전용 current source/runtime dependency surface

Implementation Notes:

1. 실행 진입 시 `aa49e8f9` ancestry, synchronized plan-set commit, four-plan projection hash, G5 immutable handoff, plan/roadmap hash, HEAD, clean execution baseline, tool availability, attempt ID uniqueness를 기록한다. `attempt-0003`을 재개하거나 그 Phase 0 binding을 복사하지 않는다.
2. `dvf_3_3_input_manifest.json`의 facts/decisions/overlay/profile/identity/precedence path와 declared hash를 실제 tracked file hash와 대조한다.
3. `evaluation_subject_kind`는 `current_runtime_payload | dvf_3_3_korean_naturalization_candidate`의 닫힌 enum이며 implicit default를 허용하지 않는다.
4. required constituent 발견 경로와 inventory 결속을 subject별로 분리한다.
   - source constituent는 `dvf_3_3_input_manifest.json`과 그 manifest가 선언한 dependency에서 발견하고 declared hash를 검증한다.
   - `current_runtime_payload` constituent는 tracked `IrisLayer3DataChunks.lua` manifest에서 current exact-case chunk set을 파생하고 source inventory와 runtime inventory를 합류시킨다.
   - `dvf_3_3_korean_naturalization_candidate` constituent는 naturalization Phase 8 handoff가 열거한 candidate, proposition/source manifest, structural satisfaction, semantic preservation, raw detector, human-review binding/decision, compiler/ruleset/corpus hash를 exact path/hash로 소비한다.
   - candidate subject에서는 current runtime parity를 `not_applicable`로 기록하되 reason은 `candidate_not_registry_adopted` 하나만 허용한다. 이를 Registry/runtime PASS나 mismatch 무시로 해석하지 않는다.
5. current ignored rendered file은 planning comparison에만 사용할 수 있으며 acceptance authority input으로 직접 읽은 횟수는 0이어야 한다.
6. current subject는 `compose_layer3_text.build_rendered()`를 explicit six-input binding과 `compose_context="staging"`으로 attempt-local run1/run2 root에서 실행한다. candidate subject는 handoff의 immutable candidate bytes를 재작성하지 않고 canonical projection과 raw metric을 독립 재계산한다.
7. current output path, style side output, requeue side output에는 write하지 않는다.
8. canonical entries projection은 `item_id` ascending, UTF-8, stable key order, canonical JSON, LF로 만든다.
9. `generated_at`, host, absolute path, mtime 같은 volatile metadata는 canonical digest에서 제외한다.
10. exact item key의 decoded Unicode sequence와 case를 보존하고 duplicate exact identity는 fail-closed한다.
11. current adopted row에는 `resolved_profile`, `coverage_quality_candidate`, `emitted_section_names`, `missing_required_sections`가 반드시 존재해야 한다. candidate row에는 source proposition resolution, structural role satisfaction, realization trace foreign key가 존재해야 한다.
12. candidate structural status는 `emitted_direct | satisfied_by_verified_fusion | satisfied_by_verified_suppression | not_required | missing`으로 고정한다. required role의 앞 세 status는 satisfied이고 `missing`만 missing이며 required role에 `not_required`를 사용할 수 없다.
13. unadopted row는 quality-evaluable row와 분리하고 quality fields의 null/absence contract를 명시한다.
14. existing Registry Runtime Compatibility reconstruction 로직은 current subject에서만 read-only dependency 또는 standalone subprocess로 재사용하고 tool hash를 binding constituent로 포함한다.
15. Publish Boundary는 compatibility disposition을 다시 판정하지 않는다. candidate subject에서는 Registry/runtime compatibility claim을 생성하지 않는다.
16. acceptance binding에는 synchronization contract hash, foundation contract hash, evaluation subject kind, constituent hash와 전체 canonical binding hash를 모두 기록한다.
17. candidate가 소비한 foundation hash가 현재 tracked foundation과 다르거나 handoff 이후 candidate/source/compiler/ruleset/corpus/review bytes가 바뀌면 fail-closed stale이다.
18. self-referential hash는 금지한다. binding manifest hash는 detached digest artifact가 manifest raw bytes를 결속하는 방식으로 구성한다.
19. protected source/rendered/Lua/runtime/package surface의 before/after hash를 비교한다.

Validation:

- current subject: current item count = canonical entry count = runtime reconstructed count
- current subject: source/canonical/runtime exact key-set parity와 runtime projection payload mismatch 0
- candidate subject: source universe = candidate key set + explicit unadopted key set, handoff constituent hash mismatch 0
- candidate subject: runtime parity applicability = `not_applicable`, reason = `candidate_not_registry_adopted`, Registry/runtime PASS claim count 0
- run1/run2 canonical entries hash parity
- run1/run2 metric projection hash parity
- unknown profile 0
- duplicate item identity 0
- required structural role with `not_required` count 0
- proof 없는 fusion/suppression count 0
- ignored rendered direct-authority read 0
- protected surface mutation 0
- dirty/untracked/ignored required input 0

---

### Change 1 — Metric and Denominator Contract

Purpose:

모든 public-text quality metric의 의미, unit, numerator, denominator, applicability, partition, overlap 규칙을 봉인한다.

Files:

- `docs/public_text_quality_metric_contract.md`
- `docs/public_text_quality_denominator_contract.md`
- 신규 metric contract test
- Phase 1 generated artifacts

Implementation Notes:

다음 denominator ID를 최소 registry로 고정한다.

```text
current_item_universe_v1
quality_evaluable_adopted_item_v1
unadopted_item_v1
required_section_opportunity_v1
required_identity_core_opportunity_v1
required_context_support_opportunity_v1
required_limitation_tail_opportunity_v1
required_use_core_opportunity_v1
profile_adopted_item_v1:<profile_id>
naturalization_candidate_item_v1
naturalization_source_proposition_v1
naturalization_required_body_plan_role_v1
naturalization_raw_detector_opportunity_v1:<detector_id>
naturalization_human_review_required_v1
```

다음 규칙을 구현한다.

- 모든 metric과 denominator는 `applicable_subject_kinds`를 가진다. 다른 subject kind의 metric을 0으로 합성하거나 PASS로 해석하지 않는다.
- `unadopted`는 quality denominator에서 제외하고 별도 adoption axis로 유지한다.
- adopted row는 정확히 하나의 resolved profile과 하나의 weak/adequate/strong class를 가진다.
- missing/unknown profile은 denominator 제외가 아니라 technical blocker다.
- section opportunity는 `compose_profiles_v2.json`의 profile별 `required_sections`에서 계산한다.
- item row count와 section occurrence count를 분리한다.
- `missing_any_required_section_row`는 unique row cardinality다.
- `missing_required_section_occurrence`는 missing section occurrence 합이다.
- `missing_required_section_occurrence`는 `missing_any_required_section_row`와 별도의 중복 blocker가 아니다.
- raw occurrence advisory evidence는 final disposition과 관계없이 항상 보존한다. unresolved blocking row finding이 이미 `blocked`를 결정한 경우 occurrence advisory는 `effective_blocking_finding_count`를 늘리거나 final disposition을 추가로 악화시키지 않는다.
- blocking row finding이 valid waiver로 debt-only 전환된 경우 raw row/occurrence 값을 모두 보존하고, waiver debt와 occurrence debt를 함께 `deferred_internal_debt` report에 남긴다.
- per-section missing 합은 total missing occurrence와 일치해야 한다.
- applicable section이 없는 denominator는 0%가 아니라 fail-closed다.
- count equality만으로 서로 다른 denominator ID를 동일시하지 않는다.
- overlapping metric을 합산해 숨겨진 종합 PASS score를 만들지 않는다.
- per-profile/per-section breakdown은 표본이 아니라 current profile/adopted-row/required-section universe 전수를 대상으로 생성해 aggregate masking을 막는다.
- current `derive_coverage_quality_candidate()` 의미와 metric calculator identity를 hash-bound한다.
- current `coverage_quality_*`와 required-section metric은 `current_runtime_payload`에만 적용한다. naturalization candidate의 문장 병합·침묵을 legacy emitted-section count로 재평가하지 않는다.
- naturalization candidate는 structural satisfaction ledger를 authority로 사용한다. `emitted_direct`, `satisfied_by_verified_fusion`, `satisfied_by_verified_suppression`은 satisfied이며 proof가 없는 fusion/suppression과 `missing`은 failure다.
- naturalization raw detector는 full candidate denominator에서 configured detector별 hit/no-hit 또는 metric을 빠짐없이 산출한다.
- human-only metric은 sealed selection contract가 정의한 required review denominator에만 적용한다. 전수 review가 아니면 corpus-wide human-only blocker 0을 주장하지 않는다.

machine-readable `disposition_class` enum은 다음 세 token만 허용한다.

```text
blocking_gate
advisory_debt
non_claim
```

`diagnostic`, `diagnostic_breakdown`, `separate_adoption_axis` 같은 설명은 별도 annotation/axis field에 두며 `disposition_class` 값으로 사용하지 않는다.

필수 metric registry:

| Metric ID | Unit / denominator | `disposition_class` | Annotation / axis |
|---|---|---|---|
| `coverage_quality_weak` | ratio / adopted item | `blocking_gate` | acceptance blocker |
| `coverage_quality_adequate` | ratio / adopted item | `non_claim` | quality distribution |
| `coverage_quality_strong` | ratio / adopted item | `non_claim` | quality distribution |
| `missing_any_required_section_row` | ratio / adopted item | `blocking_gate` | acceptance blocker |
| `missing_required_section_occurrence` | ratio / required-section opportunity | `advisory_debt` | missing occurrence debt |
| `missing_context_support` | ratio / context opportunity | `non_claim` | diagnostic breakdown |
| `missing_limitation_tail` | ratio / limitation opportunity | `non_claim` | diagnostic breakdown |
| `missing_use_core` | ratio / use opportunity | `non_claim` | diagnostic breakdown |
| `unadopted` | count/ratio / total item universe | `non_claim` | separate adoption axis |

naturalization candidate subject의 필수 metric registry:

| Metric ID | Unit / denominator | `disposition_class` | Annotation / axis |
|---|---|---|---|
| `semantic_preservation_failure` | count / source proposition | `blocking_gate` | source-provenance blocker |
| `unsatisfied_required_body_plan_role` | count / required body-plan role | `blocking_gate` | structural satisfaction blocker |
| `equivalence_proof_failure` | count / fusion·suppression transformation | `blocking_gate` | technical/semantic blocker |
| `compiler_invalid_pattern` | count / candidate item | `blocking_gate` | compiler contract blocker |
| `duplicate_proposition_realization` | count/ratio / candidate item | policy-defined | raw Korean prose detector |
| `repeated_identity_noun_window` | count/ratio / candidate item | policy-defined | raw Korean prose detector |
| `banned_internal_abstraction` | count/ratio / candidate item | policy-defined | raw Korean prose detector |
| `repeated_skeleton_concentration` | rational metric / candidate item | policy-defined | corpus-level detector |
| `paragraph_fragmentation` | count/ratio / candidate item | policy-defined | raw Korean prose detector |
| `passive_translationese_pattern` | count/ratio / candidate item | policy-defined | raw Korean prose detector |
| `empty_or_filler_sentence` | count/ratio / candidate item | policy-defined | raw Korean prose detector |
| `human_review_blocker_required_denominator` | count / required human-review row | `blocking_gate` | denominator-qualified human-only finding |

`policy-defined`은 runtime default가 아니다. S1 foundation contract와 Phase 2 ratification에서 각 detector ID에 대해 `blocking_gate | advisory_debt | non_claim` 중 정확히 하나와 threshold를 명시해야 한다. unknown detector, unmapped detector 또는 mapping 누락은 technical blocker다.

Validation:

```text
weak + adequate + strong = adopted
missing_any_row_count <= adopted
sum(per_section_missing_count) = missing_occurrence_count
sum(per_section_opportunity) = required_section_opportunity
unadopted_in_quality_denominator_count = 0
unknown_metric_count = 0
unknown_denominator_count = 0
profile_applicability_unknown_count = 0
profile_breakdown_covered_count = current_profile_universe_count
adopted_row_breakdown_covered_count = adopted
uncovered_profile_or_adopted_row_count = 0
zero_denominator_unhandled_count = 0
overlap_additive_claim_count = 0
candidate_structural_satisfaction_partition_pass = true
required_role_not_required_count = 0
fusion_or_suppression_without_equivalence_proof_count = 0
raw_detector_full_candidate_completeness_pass = true
unmapped_raw_detector_count = 0
human_review_claim_scope_expansion_count = 0
```

---

### Change 2 — Normative Policy Adoption

Purpose:

로드맵의 v1 current-subject metric disposition과 synchronized naturalization-candidate metric disposition, threshold, exception, waiver, freshness, final state machine을 subject-applicable owner-ratified machine-readable authority로 봉인한다.

Files:

- `docs/public_text_quality_acceptance_policy.md`
- `docs/public_text_quality_acceptance_claim_boundary.md`
- `docs/public_text_quality_exception_policy.md`
- `docs/public_text_quality_waiver_policy.md`
- `docs/public_text_quality_freshness_policy.md`
- Phase 2 policy/ratification/hash artifacts
- owner input policy ratification과 applicable waiver set

Implementation Notes:

v1 current-subject policy는 다음을 변경 없이 구현한다.

| Metric ID | Disposition | Threshold / effect |
|---|---|---|
| `coverage_quality_weak` | `blocking_gate` | effective numerator `== 0` |
| `coverage_quality_adequate` | `non_claim` | threshold 없음 |
| `coverage_quality_strong` | `non_claim` | threshold 없음 |
| `missing_any_required_section_row` | `blocking_gate` | effective numerator `== 0` |
| `missing_required_section_occurrence` | `advisory_debt` | raw numerator `== 0`이어야 clean accepted |
| section별 missing metric | `non_claim` | diagnostic breakdown |
| `unadopted` | `non_claim` | separate adoption axis |

naturalization candidate extension은 S1 foundation contract에서 candidate-independent하게 precommit하고 Phase 2에서 exact bytes로 ratify한다.

| Metric ID | Disposition | Threshold / effect |
|---|---|---|
| `semantic_preservation_failure` | `blocking_gate` | numerator `== 0` |
| `unsatisfied_required_body_plan_role` | `blocking_gate` | numerator `== 0` |
| `equivalence_proof_failure` | `blocking_gate` | numerator `== 0` |
| `compiler_invalid_pattern` | `blocking_gate` | numerator `== 0` |
| raw Korean prose detector | foundation/ratified registry의 exact mapping | exact integer/rational threshold |
| `human_review_blocker_required_denominator` | `blocking_gate` | numerator `== 0` |

candidate subject의 `accepted`에는 semantic·structural·compiler-invalid·Publish-classified machine blocker·required-denominator human blocker가 모두 0이어야 한다. advisory가 허용되는 detector는 raw finding과 debt를 보존하며 clean `accepted`가 아닌 `deferred_internal_debt`를 만든다.

추가 contract:

- `policy_ratification_record.json`은 canonical policy bytes/hash 승인과 함께 registry의 모든 metric을 exact `metric_id`로 한 번씩 다루는 `metric_affirmations`를 포함한다.
- 각 `metric_affirmations` row에는 다음 field가 필수다.

```text
metric_id
owner_affirmed_disposition_class
owner_affirmed_threshold_operator
owner_affirmed_threshold_value
owner_affirmed_exception_rule
owner_affirmed_waiver_effect
```

- threshold가 없는 `non_claim` metric도 operator `none`, value `null`을 명시하며 missing field나 implicit default를 허용하지 않는다.
- ratification record에는 `owner_acknowledges_evaluation_subject_may_be_blocked=true`, evaluation subject kind/hash, owner identity, ratified policy hash, ratified metric registry hash, decision timestamp, owner-binding proof가 있어야 한다.
- generic policy-level 승인만 있고 metric affirmation이 누락·중복·불일치하면 ratification은 invalid다.
- owner가 `policy_ratification_decision.json`에서 `decision=declined`를 선택하면 candidate policy를 seal하지 않고 exact decision bytes/hash를 `policy_ratification_refusal_record.json`에 보존한다. attempt state와 policy closure state는 각각 `owner_declined_policy_ratification`, `incomplete`이며 Phase 3 이후로 진행하지 않는다.
- v1 default exception set은 공집합이다.
- future exception은 exact metric/profile/static predicate 기반 machine-computable rule만 허용한다.
- item ID + reviewer 자유 판단 기반 semantic exception은 금지한다.
- exception과 waiver는 raw metric을 변경하지 않는다.
- active waiver는 clean `accepted`를 만들 수 없다.
- blocking finding + valid waiver는 `deferred_internal_debt`다.
- `missing_required_section_occurrence` advisory는 `effective_blocking_finding_count`에 기여하지 않으며 `missing_any_required_section_row` blocker를 중복 계산하지 않는다.
- unresolved missing-row blocker가 있으면 disposition은 `blocked`이고 occurrence는 raw advisory evidence로 계속 보고하되 disposition을 더 악화시키지 않는다.
- 모든 applicable missing-row blocker가 valid waiver로 debt-only 전환되면 raw row/occurrence 값, waiver 적용 내역, occurrence debt를 모두 보존하고 disposition은 다른 blocker가 없는 한 `deferred_internal_debt`다.
- technical/freshness failure는 waiver할 수 없다.
- policy, subject binding, metric calculator/schema, subject-applicable runtime bundle 또는 candidate handoff constituent, applicable waiver set 중 하나라도 바뀌면 prior disposition은 stale다.
- official policy projection은 S1 foundation의 metric/denominator/detector mapping, human-review selection contract와 byte-equivalent해야 한다. candidate 결과를 본 뒤 달라진 official projection은 ratification 대상이 아니라 stale foundation/candidate blocker다.
- `quality_baseline_v4` 97.1%는 threshold로 상속하지 않는다.
- ratio threshold는 binary float가 아니라 exact integer numerator/denominator 또는 rational comparison으로 평가한다.
- zero-tolerance threshold는 `numerator == 0`으로 비교한다.
- policy JSON missing field에 default를 주입하지 않는다.
- policy hash는 canonical policy projection에서 `policy_hash` self-field를 제외하는 규칙을 schema에 고정하고, detached `policy_hash_seal.json`이 complete policy bytes와 canonical hash를 함께 결속한다.
- policy ratification은 policy hash seal 전에 owner-authored input으로 존재해야 한다.
- policy hash seal 이후 current evaluation 전에 같은 policy version을 수정할 수 없다.
- threshold 변경은 새 policy version, 새 hash, 새 rationale, full re-evaluation을 요구한다.

non-empty waiver의 required schema는 다음으로 고정한다.

```text
waiver_schema_version
waivers[]:
  waiver_id
  payload_binding_hash
  policy_hash
  metric_id
  item_id or exact_aggregate_scope
  profile_id or not_applicable
  original_disposition
  waived_disposition
  owner_identity
  rationale
  issued_at
  expires_at or reevaluation_condition
  evidence_reference
  owner_signature_or_owner_binding_proof
```

waiver invariant:

```text
waived_disposition = deferred_internal_debt
raw_metric_mutated = false
technical_failure_scope = forbidden
expired_or_unbound_waiver = invalid
```

waiver가 없을 때도 다음 sealed empty set을 사용한다.

```text
waiver_schema_version = <current>
waivers = []
```

final disposition algorithm:

```text
if technical_blocker_count > 0:
    blocked
else if effective_blocking_finding_count > 0:
    blocked
else if advisory_debt_count > 0 or active_waiver_count > 0:
    deferred_internal_debt
else:
    accepted
```

Validation:

- 모든 metric에 disposition 정확히 하나
- blocking metric threshold 누락 0
- default exception count 0
- technical waiver path 0
- waiver-to-clean-accepted path 0
- historical threshold inheritance 0
- current-payload back-solving claim 0
- ratification bytes/hash/owner/scope valid
- metric affirmation missing/duplicate/mismatch count 0
- owner acknowledges exact evaluation subject may be blocked
- declined ratification cannot produce policy seal
- waiver schema/invariant violation count 0
- policy version/hash sealed
- current payload disposition은 Phase 2에서 아직 계산하지 않음

---

### Change 3 — Validator Implementation

Purpose:

sealed policy와 exact binding만 소비해 deterministic qualified disposition을 산출하는 fail-closed validator를 구현한다.

Files:

- `public_text_quality_acceptance.py`
- `run_public_text_quality_acceptance.py`
- `validate_public_text_quality_acceptance.py`
- focused policy/validator tests
- Phase 3 reports

Implementation Notes:

공통 module은 다음 책임을 가진다.

- strict JSON/JSONL loader
- schema/hash validator
- canonical JSON/JSONL serializer
- acceptance-input binding validator
- constituent freshness validator
- metric projection recomputation
- denominator/applicability evaluator
- threshold evaluator
- exception evaluator
- waiver validator
- raw/effective finding materialization
- exactly-one disposition state machine
- blocker owner routing
- claim-boundary scanner
- protected-surface no-mutation comparison

runner는 단계별 explicit mode만 허용한다.

```text
foundation-build
phase0-binding
phase1-contracts
phase2-policy
phase3-validator
phase4-adversarial
phase5-disposition
phase6-gate-candidate
phase6-adopt-gate
phase7-freeze
phase7-finalize
```

`foundation-build`는 `foundation_id` namespace에서만 허용하고 official `attempt_id` 또는 disposition을 만들 수 없다. `--mode all`, implicit default mode, 단계 건너뛰기, prior PASS reuse는 금지한다.

validator는 다음 권한을 가지지 않는다.

- source/profile/rendered/runtime/package write
- threshold/exception/waiver 생성
- owner/reviewer verdict 생성
- source proposition을 새로 해석하거나 semantic correctness를 자체 생성하는 판단. 단, naturalization handoff의 independently generated semantic-preservation verdict와 trace completeness를 검증·소비하는 것은 허용한다.
- current payload remediation
- runtime quality exposure

모든 parser/runtime exception은 structured technical blocker로 변환하고 최종 disposition을 `blocked`로 만든다. crash를 advisory로 내리거나 마지막 known-good disposition을 반환하지 않는다.

blocked reason은 다음 owner 축으로 라우팅한다.

```text
identity/binding/runtime parity
-> Iris Artifact Registry or Registry Runtime Compatibility

metric calculator/denominator
-> Publish Boundary metric-contract correction

sealed threshold unsatisfied
-> source/description remediation successor

candidate compiler/realization/raw-detector blocker
-> DVF Korean Prose Naturalization retry at earliest affected phase

manual semantic review required
-> approved semantic-review successor

invalid/stale waiver
-> waiver governance correction
```

Validation:

- strict schema, no default injection
- binding/policy/calculator/waiver mismatch fail-closed
- unknown metric/profile/denominator fail-closed
- denominator zero fail-closed
- invalid waiver fail-closed
- validator exception fail-closed
- raw metric mutation 0
- exactly one disposition
- repeated-run normalized output parity
- protected surface mutation 0

---

### Change 4 — Adversarial Review and Negative Fixtures

Purpose:

current payload을 평가하기 전에 production validator가 우회·오독·경계값 공격을 견디는지 검증한다.

Files:

- `tests/fixtures/public_text_quality_acceptance/`
- `test_public_text_quality_acceptance_fixtures.py`
- Phase 4 reports

Implementation Notes:

fixture manifest는 로드맵의 36개 mandatory case에 일대일 trace ID를 부여하고, 추가 case는 별도 `plan_additive` origin으로 기록한다. 모든 fixture row는 `origin=roadmap_mandatory|plan_additive`, immutable trace ID, production evaluator path를 가진다.

- payload/source/runtime/calculator/policy/waiver freshness mismatch
- missing/unknown profile·metric·denominator
- denominator zero
- row count와 occurrence count 혼동
- unadopted의 quality denominator/weak 혼입
- expired/wrong-policy/wrong-payload/invalid-owner waiver
- technical failure waiver 시도
- threshold equality, just-below, just-above
- 한 row의 multiple missing sections
- adequate+missing, weak+no-missing 독립축 사례
- exception predicate mismatch와 raw mutation 시도
- multiple/no disposition
- validator execution exception
- historical threshold reuse
- current-pass threshold back-solving
- active waiver + accepted 시도
- missing required section silent advisory 시도
- `[plan_additive]` missing-any row와 missing occurrence가 모두 양수인 payload의 모든 blocking row를 valid waiver로 debt-only 전환했을 때 raw row/occurrence 보존, effective blocker 0, advisory debt 양수, `deferred_internal_debt`가 되는 reconciliation 사례
- policy default injection
- volatile metadata-only change
- semantic item waiver를 machine exception으로 위장
- `[plan_additive]` required role이 `satisfied_by_verified_fusion`이고 typed equivalence proof가 유효한 candidate를 missing으로 오판하지 않는 사례
- `[plan_additive]` required role이 `satisfied_by_verified_suppression`이지만 equivalence proof가 누락·불일치한 candidate를 fail-closed하는 사례
- `[plan_additive]` optional role의 `not_required`와 required role의 불법 `not_required`를 구분하는 사례
- `[plan_additive]` 동일 source proposition을 두 clause로 재진술한 candidate의 raw detector hit가 Phase 8 mapping까지 보존되는 사례
- `[plan_additive]` foundation contract hash와 naturalization handoff가 다른 stale candidate 사례
- `[plan_additive]` candidate runtime parity `not_applicable`를 Registry Runtime Compatibility PASS로 과장하는 claim을 차단하는 사례
- `[plan_additive]` human-review 표본 결과를 corpus-wide human-only blocker 0으로 확장하는 claim을 차단하는 사례

모든 fixture는 production parser/evaluator path를 그대로 통과한다. test-only evaluator 복제는 금지한다.

threshold back-solving 관련 machine fixture는 policy/evaluation 단계 순서, rationale field 존재, prohibited phrase, sealed hash chronology만 검증한다. rationale가 실제 product contract에 근거하며 current payload 결과를 보고 작성되지 않았는지는 independent reviewer가 판단한다. machine PASS는 이 reviewer judgment를 대체하지 않는다.

metamorphic checks:

- item order permutation 후 canonical metric hash 동일
- `generated_at`만 변경 후 canonical projection hash 동일
- single source constituent 변경 후 prior binding stale
- single waiver-set 변경 후 prior disposition stale
- line ending/absolute path/host metadata 차이가 canonical identity를 바꾸지 않음

Validation:

```text
roadmap_mandatory_fixture_count = 36
plan_additive_fixture_count >= 1
fixture_without_origin_count = 0
total_fixture_count >= 37
unexpected_fixture_pass_count = 0
expected_blocked_fixture_fail_count = 0
expected_deferred_fixture_fail_count = 0
expected_accepted_fixture_fail_count = 0
technical_waiver_bypass_count = 0
multiple_disposition_count = 0
silent_default_count = 0
```

---

### Change 5 — Exact Evaluation-Subject Disposition

Purpose:

Phase 2 policy를 변경하지 않고 exact evaluation subject에 정확히 하나의 qualified disposition을 부여한다.

Files:

- Phase 5 reports
- current applicable waiver set

Implementation Notes:

1. Phase 0 constituent, exact evaluation subject와 current checkout의 freshness를 다시 확인한다.
2. stale이면 prior Phase 0 binding을 재사용하지 않고 Phase 0부터 새 attempt를 연다.
3. canonical metric projection을 fresh recompute한다.
4. raw metric, exception application, waiver application, effective finding을 분리해 저장한다.
   - missing-any row와 missing occurrence raw evidence는 disposition에 관계없이 모두 보존한다.
   - missing occurrence advisory를 missing-any row와 별도의 blocker로 계산하지 않으며 unresolved row blocker가 있으면 occurrence는 `blocked`를 추가로 악화시키지 않는다.
   - 모든 applicable row blocker가 valid waiver로 debt-only 전환되면 effective blocking count는 0으로 계산하고 row waiver debt와 occurrence debt를 함께 `deferred_internal_debt` report에 남긴다.
5. omitted blocker/debt가 없도록 subject-applicable universe 전수에 대한 breakdown을 포함하며 표본 검증으로 대체하지 않는다. candidate raw detector는 full candidate denominator, human-only 판정은 required review denominator를 사용한다.
6. policy hash, input binding hash, metric snapshot hash, waiver set hash를 disposition에 결속한다.
7. subject result가 불리해도 policy/threshold/denominator를 변경하지 않는다.
8. source 수정과 같은 attempt 재평가를 금지한다.
9. result가 `blocked`여도 Phase 5 execution 자체는 정상 완료될 수 있다.
10. current subject에서는 planning observation이 유지되고 v1 default exception/waiver가 비어 있다면 `blocked`가 예상되지만, 이 예상은 Phase 5 verdict가 아니며 코드에 hard-code하지 않는다.
11. synchronized candidate subject에서 `blocked` 또는 `deferred_internal_debt`이면 exact failure ledger와 earliest affected naturalization phase를 기록하고 `after_remediation`으로 반환한다. `accepted`만 S3 Phase 6으로 진행한다.

Validation:

- policy hash = sealed Phase 2 policy
- input binding fresh
- evaluation subject kind/hash = Phase 0 binding
- foundation contract hash = naturalization handoff consumed hash
- metric snapshot fresh
- waiver set fresh
- raw/effective coverage complete
- exactly one disposition
- omitted blocking/advisory finding 0
- protected surface mutation 0
- candidate subject일 때 semantic/structural/raw-detector/human-review handoff completeness pass

---

### Change 6 — Gate Integration and Overclaim Guard

Purpose:

Publish Boundary-owned disposition을 additive required validation으로 연결하고 adjacent PASS의 public acceptance 대체를 차단한다.

Files:

- `.gitignore`
- `Iris/_docs/round3/current_route_required_validations.json`
- `test_public_text_quality_acceptance_current_route.py`
- Phase 6 artifacts

Implementation Notes:

1. live manifest를 직접 수정하기 전에 exact base hash와 candidate copy를 만든다.
2. candidate에는 role `publish_boundary_public_text_acceptance_required_validation`을 사용한다.
3. required artifact는 Phase 0 subject/handoff binding, Phase 1 contract validation, Phase 2 policy/hash, Phase 4 adversarial PASS, Phase 5 exact subject disposition, Phase 6 stale/overclaim/no-mutation report를 결속한다.
4. required test는 current-route process 안에서 Publish Boundary module을 import하지 않고 `validate_public_text_quality_acceptance.py --required-gate`를 standalone subprocess로 실행한다.
5. `round3_active_core_closure.json`의 current core 12개와 tooling allowlist 1개를 변경하지 않는다.
6. candidate manifest를 사용해 pre-adoption route를 실행하고 expected disposition별 exit를 분리한다. candidate output은 `execution_class=sandbox_candidate`, `authority_effect=none`, `official_route=false`를 명시하며 official current-route result로 인용할 수 없다.
7. exact candidate/base/diff/contract hash와 아래 informed operational authorization field를 owner가 승인한 뒤에만 live manifest에 additive patch를 적용한다.
8. existing required artifact/test entry를 삭제·수정·재정렬해 의미를 바꾸지 않는다.
9. live manifest는 계속 `legacy_combined_governance_route` container다.
10. manifest adoption은 DVF/Registry responsibility transfer가 아니다.
11. required artifact는 present, tracked, not ignored여야 한다.
12. stale Phase 5 disposition을 current gate가 소비하면 fail-closed한다.
13. live required gate adoption과 complete post-adoption artifact set은 policy closure의 필수조건이다.
14. owner가 gate adoption을 거부하면 `gate_adoption_decision_record.json`과 `owner_declined_gate_adoption_report.json`을 write-once로 보존하고 attempt를 `owner_declined_gate_adoption`으로 종료한다. policy closure는 `incomplete`이며 Phase 7 finalize는 금지한다.
15. `adoption_timing=after_remediation`은 현재 attempt의 adoption authorization이 아니다. remediation은 이 계획 밖의 successor로 라우팅하고, remediation 후 fresh Phase 0부터 새 attempt에서 재평가한다.
16. synchronized naturalization candidate path에서는 candidate가 `accepted`일 때만 live gate adoption을 허용한다. non-accepted disposition은 `after_remediation`으로 naturalization attempt에 반환하며 blocked-immediate branch는 독립 current-subject 운영에만 남긴다.

`required_gate_adoption_contract.json`과 owner-authored `gate_adoption_decision.json`은 최소 다음 field를 exact hash로 결속한다.

```text
candidate_manifest_hash
candidate_patch_hash
evaluation_subject_kind
evaluation_subject_hash
evaluation_subject_disposition
evaluation_subject_disposition_hash
naturalization_handoff_manifest_hash or not_applicable
expected_post_adoption_official_route_state
expected_exit_code
exact_blocker_attribution
adoption_timing = immediate | after_remediation
owner_acknowledgement
owner_authorization
owner_identity
authorized_at
owner_binding_proof
```

authorization rule:

```text
if evaluation_subject_kind == dvf_3_3_korean_naturalization_candidate
   and evaluation_subject_disposition != accepted:
    adoption_timing = after_remediation
    live adoption in current attempt = forbidden
    policy closure state = incomplete
elif evaluation_subject_disposition == blocked and adoption_timing == immediate:
    expected_post_adoption_official_route_state = blocked
    expected_exit_code = exact nonzero expected code
    exact_blocker_attribution = Publish Boundary public-text acceptance blocker
    owner_acknowledgement explicitly accepts persistent official-route nonzero until remediation
    owner_authorization = true
elif evaluation_subject_disposition == blocked and adoption_timing == after_remediation:
    live adoption in current attempt = forbidden
    policy closure state = incomplete
else:
    expected route state/exit must match the sealed disposition matrix
```

필수 freeze sentence:

```text
Legacy Combined DVF Governance Route PASS
!= public text accepted
!= Public Text Quality Acceptance Policy Closure
!= Publish Boundary PASS
!= package-ready
!= release-ready
```

disposition별 gate effect:

```text
accepted
-> public-text acceptance component may pass

deferred_internal_debt
-> component remains explicitly qualified/debt-bearing
-> bare accepted claim is forbidden

blocked
-> public-text acceptance required gate fails
```

`blocked`일 때 official current-route command는 nonzero가 예상된다. 이 결과를 PASS로 기록하지 않는다. 대신 다음을 분리한다.

- gate implementation/structural validation: exit 0 필수
- exact disposition production: complete 필수
- official current-route: `accepted/deferred`이면 exit 0, `blocked`이면 exact Publish Boundary blocker 하나로 귀속된 nonzero
- adjacent/pre-existing failure: 별도 owner와 first-failure로 분리

gate가 informed authorization에 따라 실제 채택된 뒤라면 expected `blocked` route 결과만으로 policy closure가 실패하지 않는다. owner non-adoption, `after_remediation`, missing acknowledgement/authorization, 또는 incomplete post-adoption artifact set은 policy closure를 `incomplete`로 유지한다. nonzero를 PASS로 축약하거나 다른 failure를 숨기면 Phase 7 진입을 차단한다.

Validation:

- gate role exact match
- DVF/Registry responsibility reabsorption 0
- deferred → bare accepted 0
- Public Text Policy Closure → Publish Boundary PASS overclaim 0
- package/release/Workshop/manual-QA overclaim 0
- stale disposition consumption 0
- missing/untracked/ignored required artifact 0
- informed operational authorization field missing/mismatch 0
- blocked-immediate owner acknowledgement valid
- owner decline/after-remediation path cannot enter Phase 7
- live_required_gate_adopted = true
- post_adoption_artifact_set_complete = true
- additive-only manifest diff
- current core/tooling allowlist unchanged
- protected surface mutation 0

---

### Change 7 — Independent Closeout, Owner Seal, and Policy Closure

Purpose:

machine validation, independent review, owner seal, final claim을 분리해 closure를 봉인한다.

Files:

- Phase 7 artifacts
- closeout doc
- `Iris/build/description/v2/reviewer_inputs/iris_publish_boundary_public_text_quality_acceptance_policy_closure/`
- `Iris/build/description/v2/owner_inputs/iris_publish_boundary_public_text_quality_acceptance_policy_closure/`
- Phase 7 terminal seal 이후 조건부 additive top-doc successor updates

Implementation Notes:

1. 이 계획의 Phase 0~6 claim-bearing artifact, live gate adoption evidence, complete post-adoption artifact set, implementation HEAD를 final evidence freeze에 결속한다.
2. final artifact hash manifest는 자기 자신과 terminal seal을 포함하지 않는 non-self-referential ordered input set을 사용한다.
3. independent review와 reviewer eligibility declaration은 `reviewer_inputs`에서만 소비한다. 두 source는 tracked, not ignored, hash-bound이며 owner input으로 cross-reclassified되지 않았음을 VCS/authority census로 검증한다. reviewer는 policy, denominator, validator, adversarial coverage, exact disposition, gate effect, failure preservation을 검토한다.
4. reviewer finding은 Critical/Important/Minor로 분리하고 Critical/Important 0을 요구한다.
5. validator는 independent review 문장이나 verdict를 생성·요약·수정하지 않는다.
6. owner ratification/waiver/gate authorization/seal은 `owner_inputs`에서만 소비한다. owner는 exact policy closure state, evaluation subject kind/hash와 exact qualified disposition을 별도 field로 승인하거나 거부한다.
7. owner seal은 independent review hash와 evaluation-subject disposition hash를 직접 결속한다.
8. failed review/evaluation evidence를 삭제하거나 같은 artifact ID의 PASS로 덮어쓰지 않는다.
9. final closeout report는 machine/reviewer/owner 축을 별도로 표현한다.
10. terminal seal은 final report까지의 ordered hash DAG를 결속하고 이후 claim-bearing mutation을 금지한다.
11. top-doc sync는 terminal seal 밖의 additive **Successor Documentation Trace**로만 수행한다. successor는 terminal seal hash를 참조하고 affected documentation consumer를 별도 재검증하지만 sealed closure DAG나 terminal seal을 수정하지 않는다.
12. 독립 `current_runtime_payload` subject가 `blocked`여도 informed immediate adoption, expected blocker attribution, complete post-adoption evidence가 있으면 policy closure는 `complete`일 수 있다. synchronized naturalization candidate에는 이 예외를 적용하지 않는다.
13. owner gate non-adoption 또는 `after_remediation` decision은 Phase 7 input completeness를 충족하지 않으며 final closure report나 terminal seal로 승격하지 않는다.

Validation:

```text
machine_validation_complete = true
independent_review_complete = true
independent_review_eligible = true
critical_finding_count = 0
important_finding_count = 0
owner_seal_valid = true
live_required_gate_adopted = true
post_adoption_artifact_set_complete = true
gate_adoption_informed_authorization_valid = true
reviewer_input_tracked_count = reviewer_input_required_count
reviewer_input_ignored_count = 0
reviewer_owner_cross_reclassification_count = 0
policy_hash_unchanged_since_phase2 = true
disposition_hash_unchanged_since_phase5 = true
failed_evidence_preserved = true
final_vcs_preservation_pass = true
terminal_hash_seal_valid = true
```

---

## 7. Validation Plan

### Automated Validation

모든 command는 repository root에서 실행한다. exact command가 exit code 0을 반환한 경우에만 해당 command를 PASS로 기록한다. disposition이 `blocked`여서 required gate가 의도적으로 nonzero를 반환한 경우에는 `expected disposition blocker`로 기록하며 PASS라고 부르지 않는다.

#### 0. Pre-attempt development foundation

이 단계는 S1 전용이며 official `<attempt_id>`를 만들지 않는다.

```powershell
uv run python -B Iris/build/description/v2/tools/build/run_public_text_quality_acceptance.py --foundation-id <foundation_id> --mode foundation-build
uv run python -B Iris/build/description/v2/tools/build/validate_public_text_quality_acceptance.py --foundation-id <foundation_id> --require-foundation-ready --no-write
```

readiness report는 `authority_effect=none`, `official_disposition=not_issued`, `live_gate_adopted=false`, `policy_closure_state=not_started`여야 한다. 이 단계가 끝난 뒤 naturalization S2를 실행하고, 그 Phase 8 handoff가 준비되기 전에는 아래 formal Phase 0~7 command를 실행하지 않는다.

#### 1. Focused metric/denominator tests

```powershell
uv run python -B -m unittest discover -s Iris/build/description/v2/tests -p "test_public_text_quality_metric_contract.py"
```

#### 2. Focused policy/schema tests

```powershell
uv run python -B -m unittest discover -s Iris/build/description/v2/tests -p "test_public_text_quality_acceptance_policy.py"
```

#### 3. Focused validator tests

```powershell
uv run python -B -m unittest discover -s Iris/build/description/v2/tests -p "test_public_text_quality_acceptance.py"
```

#### 4. Adversarial fixture suite

```powershell
uv run python -B -m unittest discover -s Iris/build/description/v2/tests -p "test_public_text_quality_acceptance_fixtures.py"
```

#### 5. Phase 0 binding and determinism

```powershell
uv run python -B Iris/build/description/v2/tools/build/run_public_text_quality_acceptance.py --attempt-id <attempt_id> --mode phase0-binding --evaluation-subject-kind <kind> --subject-handoff <naturalization-phase8-handoff-or-not-applicable>
uv run python -B Iris/build/description/v2/tools/build/validate_public_text_quality_acceptance.py --attempt-id <attempt_id> --require-phase0
```

Phase 0 validator는 다음 command family를 한 report에서 분리한다.

- current subject의 isolated regeneration run1/run2 또는 candidate subject의 immutable handoff/canonical recomputation
- canonical entries hash parity
- canonical metric projection hash parity
- subject-applicable runtime parity 또는 exact candidate handoff binding
- source/runtime 또는 source/candidate constituent freshness
- ignored rendered direct-authority prohibition
- protected surface no-mutation
- required input VCS census

#### 6. Metric/denominator contract

```powershell
uv run python -B Iris/build/description/v2/tools/build/run_public_text_quality_acceptance.py --attempt-id <attempt_id> --mode phase1-contracts
uv run python -B Iris/build/description/v2/tools/build/validate_public_text_quality_acceptance.py --attempt-id <attempt_id> --require-phase1
```

#### 7. Policy seal

owner-authored `policy_ratification_decision.json`, registry 전수의 metric-level affirmation, explicit applicable waiver set이 준비된 뒤 실행한다. `decision=declined`이면 refusal record까지만 검증하고 이후 command는 실행하지 않는다.

```powershell
uv run python -B Iris/build/description/v2/tools/build/run_public_text_quality_acceptance.py --attempt-id <attempt_id> --mode phase2-policy
uv run python -B Iris/build/description/v2/tools/build/validate_public_text_quality_acceptance.py --attempt-id <attempt_id> --require-phase2
```

#### 8. Validator contract and adversarial validation

```powershell
uv run python -B Iris/build/description/v2/tools/build/run_public_text_quality_acceptance.py --attempt-id <attempt_id> --mode phase3-validator
uv run python -B Iris/build/description/v2/tools/build/validate_public_text_quality_acceptance.py --attempt-id <attempt_id> --require-phase3
uv run python -B Iris/build/description/v2/tools/build/run_public_text_quality_acceptance.py --attempt-id <attempt_id> --mode phase4-adversarial
uv run python -B Iris/build/description/v2/tools/build/validate_public_text_quality_acceptance.py --attempt-id <attempt_id> --require-phase4
```

#### 9. Exact evaluation-subject disposition

```powershell
uv run python -B Iris/build/description/v2/tools/build/run_public_text_quality_acceptance.py --attempt-id <attempt_id> --mode phase5-disposition
uv run python -B Iris/build/description/v2/tools/build/validate_public_text_quality_acceptance.py --attempt-id <attempt_id> --require-phase5
```

이 command의 exit 0은 disposition production/validation이 완료되었다는 뜻이다. canonical `evaluation_subject_disposition.json`의 값을 별도 `accepted | blocked | deferred_internal_debt` field로 읽는다. synchronized candidate가 non-accepted이면 아래 10–13번을 실행하지 않고 naturalization retry로 반환한다.

#### 10. Candidate manifest route and claim-boundary scan

```powershell
uv run python -B Iris/build/description/v2/tools/build/run_public_text_quality_acceptance.py --attempt-id <attempt_id> --mode phase6-gate-candidate
uv run python -B Iris/build/description/v2/tools/build/validate_public_text_quality_acceptance.py --attempt-id <attempt_id> --require-gate-candidate
uv run python -B Iris/_docs/round3/round3_run_contract_tests.py --class current --enforce-current-build-closure --required-validations <candidate-manifest> --out <attempt-root>/phase6/candidate_current_route_result.json
```

candidate current-route command의 expected exit는 Phase 5 disposition matrix로 판정하며 nonzero를 PASS로 기록하지 않는다.

#### 11. Post-adoption current route

exact gate candidate에 대한 informed owner authorization이 완료된 뒤 실행한다. synchronized candidate는 `accepted`와 canonical adoption timing만 허용하고, 독립 current-subject blocked 경로만 명시적 `immediate` authorization을 사용할 수 있다.

```powershell
uv run python -B Iris/build/description/v2/tools/build/run_public_text_quality_acceptance.py --attempt-id <attempt_id> --mode phase6-adopt-gate
uv run python -B Iris/_docs/round3/round3_run_contract_tests.py --class current --enforce-current-build-closure --out <attempt-root>/phase6/post_adoption_current_route_result.json
uv run python -B Iris/build/description/v2/tools/build/validate_public_text_quality_acceptance.py --attempt-id <attempt_id> --require-phase6
```

#### 12. Lua syntax no-regression

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\check_lua_syntax.ps1
```

이 command는 Lua source가 변경되지 않았다는 인접 regression 보강이다. manual/in-game QA 또는 runtime behavior PASS가 아니다.

#### 13. Final hash-binding and terminal validation

live gate adoption과 complete post-adoption artifact set, eligible independent review, owner seal이 모두 준비된 뒤:

```powershell
uv run python -B Iris/build/description/v2/tools/build/run_public_text_quality_acceptance.py --attempt-id <attempt_id> --mode phase7-freeze
uv run python -B Iris/build/description/v2/tools/build/validate_public_text_quality_acceptance.py --attempt-id <attempt_id> --require-independent-review
uv run python -B Iris/build/description/v2/tools/build/validate_public_text_quality_acceptance.py --attempt-id <attempt_id> --require-owner-seal
uv run python -B Iris/build/description/v2/tools/build/run_public_text_quality_acceptance.py --attempt-id <attempt_id> --mode phase7-finalize
uv run python -B Iris/build/description/v2/tools/build/validate_public_text_quality_acceptance.py --attempt-id <attempt_id> --require-terminal-seal --no-write
```

#### 14. VCS and diff validation

```powershell
git diff --check
git diff --stat
git diff
git status --short
```

required artifact 전체에 대해 다음을 report로 남긴다.

```powershell
git ls-files --error-unmatch <required-path>
git check-ignore -v <required-path>
```

`git check-ignore`는 required path가 active ignore rule에 걸리지 않는지 판정하는 용도이며, command 자체의 일반 exit 의미와 artifact verdict를 혼동하지 않는다.

`owner_inputs`의 ratification/adoption/seal source와 `reviewer_inputs`의 review/eligibility source도 closure-required input으로 같은 VCS census를 수행한다. 다음을 별도 assertion으로 남긴다.

```text
owner_input_tracked_count = owner_input_required_count
reviewer_input_tracked_count = reviewer_input_required_count
owner_input_ignored_count = 0
reviewer_input_ignored_count = 0
reviewer_owner_cross_reclassification_count = 0
```

### Manual Validation

- metric registry의 각 numerator/denominator/source field를 표본이 아니라 전 항목 기준으로 검토한다.
- profile별 `required_sections` applicability matrix와 per-profile/per-section breakdown을 표본이 아니라 current profile/adopted-row universe 전수 기준으로 current `compose_profiles_v2.json`과 대조한다.
- naturalization candidate에서는 structural satisfaction partition, source proposition coverage와 raw detector full-corpus denominator를 전수 대조하고 human-only finding은 required review denominator로 한정한다.
- raw metric과 effective finding이 분리되어 있는지 확인한다.
- exception set이 공집합인지, waiver가 raw metric을 숨기지 않는지 확인한다.
- threshold rationale의 금지 문구/순서 검사는 machine check로, rationale가 실제 product contract에 근거하고 evaluation subject 결과에서 역산되지 않았는지는 independent reviewer 판단으로 확인한다.
- owner policy ratification이 모든 metric의 disposition/threshold/exception/waiver effect를 정확히 한 번씩 affirm하는지 확인한다.
- evaluation-subject disposition report가 blocker/debt를 누락하지 않았는지 확인한다.
- overclaim scanner의 Korean/English/mixed-language positive/negative fixture를 검토한다.
- required manifest diff가 additive-only인지 확인한다.
- candidate route result가 `official_route=false`, `authority_effect=none`으로 표시되는지 확인한다.
- blocked-immediate gate adoption이면 expected official route state/exit, exact blocker attribution, persistent nonzero acknowledgement가 owner authorization에 포함되는지 확인한다.
- current core 12 modules와 tooling allowlist 1 module이 그대로인지 확인한다.
- independent reviewer eligibility와 artifact hash coverage를 확인한다.
- owner seal이 policy closure, evaluation subject kind/hash와 disposition을 별도 field로 승인하는지 확인한다.
- top-doc successor가 policy closure, evaluation subject kind/hash와 disposition을 별도 축으로 병기하고 terminal seal 밖의 successor trace로만 존재하는지 확인한다.
- failed fixture/review/disposition evidence가 보존되었는지 확인한다.
- existing dirty drift-verification staging 49개가 본 execution에서 수정·정리·흡수되지 않았는지 확인한다.

### Validation Limits

이 실행에서 검증하지 않는다.

- machine fixture만으로 threshold rationale의 제품적 정당성이나 사람의 실제 동기를 완전히 증명하지 않는다. machine validation은 artifact 순서, field/hash, prohibited phrase, sealed chronology까지만 보장하고 independent review가 rationale의 실질 근거를 판정한다.

- source 사실 자체의 정확성을 새로 판정하는 일
- required review denominator 밖의 모든 문장에 대한 사람 naturalness 전수 판정
- gameplay usefulness
- 오해 가능성
- detector/human-review rubric에 정의되지 않은 번역 품질의 포괄적 완전성
- manual/in-game Browser/Tooltip/Wiki UX
- 실제 package installation
- package publication
- release/Workshop metadata
- 장시간 runtime behavior
- multiplayer behavior
- 외부 모드 전체 compatibility
- semantic-quality-complete
- Publish Boundary 전체 PASS

---

## 8. Risk Surface Touch

### Authority Surface

변경 있음.

신규 authority는 다음으로 제한한다.

- Public Text Quality Acceptance Policy
- Public Text Acceptance Input Binding
- Exact Evaluation-Subject Public-Text Disposition

source/rendered/Registry/runtime/package authority는 이동하지 않는다.

### Runtime Behavior Surface

없음.

- runtime Lua code 변경 없음
- runtime rendering policy 변경 없음
- quality/disposition runtime 소비 없음
- Browser/Wiki/Tooltip public require contract 변경 없음

### Compatibility Surface

직접 변경 없음.

Registry Runtime Compatibility current result와 runtime reconstruction logic을 read-only prerequisite로 소비한다. mismatch는 `blocked`로 기록하고 RTC correction successor로 라우팅하며 이 계획에서 compatibility policy를 수정하지 않는다.

### Sealed Artifact Surface

additive 변경 있음.

- policy/binding/metric/disposition/review/seal artifact 신규 생성
- existing sealed artifact rewrite 없음
- failure evidence append-only 보존
- required artifact exact-path tracking 추가

### Public-Facing Output Surface

직접 변경 없음.

public text 내용과 runtime 표시에는 변화가 없다. Publish Boundary 내부의 acceptance governance surface만 추가된다.

---

## 9. Risk Analysis

### Architecture Risk

- Publish Boundary가 DVF Body Compiler 또는 Registry 책임을 재흡수할 수 있다.
- current-route manifest에 gate가 들어갔다는 이유로 gate ownership이 DVF로 오인될 수 있다.
- runtime reconstruction reuse가 RTC 재판정처럼 보일 수 있다.
- 새 module을 current core/tooling allowlist에 추가해 legacy route와 Publish Boundary 경계를 흐릴 수 있다.
- item-level semantic exception이 source 의미 재판정 통로가 될 수 있다.

Mitigation:

- standalone subprocess required test
- current core/tooling allowlist 무변경
- explicit gate role과 freeze sentence
- machine-computable exception만 허용
- mismatch owner routing과 no-writer contract

### Runtime Risk

- isolated regeneration이 current rendered/style/requeue output에 write할 수 있다.
- runtime chunks를 quality/UI input으로 오해할 수 있다.
- validator가 source/runtime repair를 실행할 수 있다.

Mitigation:

- `compose_context="staging"` + attempt-local output
- before/after protected hash
- runtime no-exposure scanner
- validator writer allowlist를 attempt root로 제한

### Compatibility Risk

- case-variant exact key가 PowerShell object materialization에서 충돌할 수 있다.
- runtime chunk parser와 RTC contract가 drift할 수 있다.
- canonicalization에서 Unicode casefold/normalization이 identity를 바꿀 수 있다.

Mitigation:

- Python exact-key record projection 사용
- RTC reconstruction/tool hash binding
- no casefold/no Unicode normalization
- exact key-set과 payload parity 검증

### Regression Risk

- 2,105 / 2,084 / 4,634 / section opportunity denominator를 혼용할 수 있다.
- row count와 occurrence count를 혼동할 수 있다.
- aggregate ratio가 profile 전면 누락을 숨길 수 있다.
- current payload 결과를 보고 threshold를 조정할 수 있다.
- waiver가 raw failure를 지우거나 clean accepted를 만들 수 있다.
- stale disposition이 live required gate에 남을 수 있다.
- required artifact가 untracked/ignored 상태로 채택될 수 있다.
- existing dirty staging evidence를 새 execution 결과로 오인할 수 있다.
- `blocked` official current-route nonzero를 PASS로 거짓 보고할 수 있다.

Mitigation:

- denominator ID registry와 per-profile breakdown
- row/occurrence adversarial fixture
- policy seal-before-evaluation sequencing
- raw/effective dual report
- stale consumption guard
- required artifact VCS recensus
- clean isolated execution baseline
- command exit와 disposition outcome을 별도 field로 기록

---

## 10. Rollback Plan

### Policy Seal 이전

- candidate policy, validator, fixture, candidate manifest는 폐기할 수 있다.
- 폐기된 artifact는 current authority가 아니며 필요하면 failed/historical attempt로 보존한다.
- source/rendered/runtime/package payload를 과거 상태로 되돌리지 않는다.

### Policy Seal 이후

- 같은 policy artifact/version을 rewrite하지 않는다.
- 변경은 새 policy version, 새 hash, 새 rationale, full re-evaluation으로만 수행한다.
- prior policy와 disposition은 historical exact evaluation으로 보존한다.

### Owner Decision Refusal and External-Input Wait

- policy ratification 거부는 `owner_inputs/.../policy_ratification_decision.json`과 attempt-local `policy_ratification_refusal_record.json`에 exact bytes/hash로 보존한다. policy seal을 만들지 않고 closure state를 `incomplete`로 유지한다.
- gate adoption 거부는 `owner_inputs/.../gate_adoption_decision.json`, `gate_adoption_decision_record.json`, `owner_declined_gate_adoption_report.json`에 보존한다. post-adoption artifact를 합성하지 않고 Phase 7 finalize를 실행하지 않는다.
- owner/reviewer 대기 상태는 closure가 아니다. 오래 열린 attempt의 freshness가 변하면 기존 attempt를 rewrite하지 않고 `stale_while_awaiting_external_input`으로 종료한 뒤 새 attempt를 연다.

### Disposition 이후

- 기존 disposition을 삭제하거나 같은 ID의 새 PASS로 교체하지 않는다.
- source/policy/waiver/calculator 변경 후에는 새 attempt와 새 disposition record를 만든다.
- stale prior acceptance는 historical evidence로만 남기고 current disposition은 `blocked`로 처리한다.

### Required Gate Adoption 이후

1. gate implementation defect
   - gate를 fail-closed로 유지하고 correction successor를 연다.
2. policy authority defect
   - current disposition을 blocked/stale로 전환하고 새 policy version을 연다.
3. integration-only defect
   - owner-approved additive rollback record와 affected-consumer rerun을 요구한다.

gate를 제거해 stale `accepted`를 복구하지 않는다. rollback이 필요한 경우 existing manifest entry 전체가 아니라 이 round의 exact additive rows만 대상으로 하며 predecessor failure와 adoption evidence를 보존한다.

### Exact-Path `.gitignore` Unignore Rollback

live gate adoption 전에 attempt가 중단되거나 owner가 adoption을 거부한 경우:

1. pre-change `.gitignore` hash, attempt-owned exact unignore patch, current hash를 대조한다.
2. 다른 line이나 사용자 변경을 건드리지 않고 이 attempt가 추가한 exact unignore line만 제거한다.
3. live required-validation consumer가 해당 path를 이미 참조하지 않는지 확인한다.
4. before/after hash, 제거 line, 잔존 diff, tracked-file 영향 여부를 `pre_adoption_unignore_rollback_report.json`에 기록한다.
5. 이미 tracked consumer 또는 adopted gate가 존재하면 pre-adoption rollback을 사용하지 않고 owner-approved correction successor를 연다.

artifact 파일이나 failure evidence를 삭제해 clean state를 연출하지 않는다. rollback은 ignore-rule의 attempt-owned additive line에만 한정한다.

### Documentation Rollback

- top-doc additive entry만 별도 successor correction으로 정정한다.
- sealed execution evidence, independent review, owner seal, terminal seal을 rewrite하지 않는다.
- 사용자 소유 dirty staging 파일을 rollback 대상으로 포함하지 않는다.

다음 중 하나라도 불명확하면 evaluation-subject disposition은 `blocked`다.

- current policy identity
- evaluated payload identity
- applicable waiver set
- gate-consumed disposition identity
- prior acceptance freshness

---

## 11. Governance Constraints

- `Philosophy.md`가 최상위 authority다.
- Iris runtime은 100% Lua renderer로 유지한다.
- runtime에서 설명, quality, acceptance를 생성·판정하지 않는다.
- 해석·권장·비교를 추가하지 않는다.
- DVF System / DVF Body Compiler는 deterministic 3-3 body production 책임만 가진다.
- Iris Artifact Registry는 artifact identity/lifecycle/current authority 책임을 유지한다.
- Registry Runtime Compatibility는 exact identity consumer-safe preservation 책임을 유지한다.
- Publish Boundary만 public-text acceptance policy와 disposition을 소유한다.
- DVF naturalization만 proposition/discourse/Korean surface realization과 raw detector 산출을 소유한다.
- synchronized path에서는 전역 G0 → G1 → G2 → G3 → G4 foundation readiness → G5 immutable naturalization handoff → G6 official Publish Phase 0~7 → G7 naturalization finalize 순서를 바꾸지 않는다. Local S1~S4는 각각 G4~G7에 매핑한다.
- foundation readiness를 official policy seal/disposition/gate/closure로 표현하지 않는다.
- candidate subject에서 runtime parity `not_applicable`를 Registry Runtime Compatibility PASS 또는 current adoption으로 확대하지 않는다.
- source/rendered/Lua/runtime/package protected surface mutation은 0이어야 한다.
- exact 2,105-key planning observation은 상수가 아니며 Phase 0 fresh count를 사용한다.
- case-variant key를 merge/rename/winner-select하지 않는다.
- ignored rendered artifact를 durable current authority로 승격하지 않는다.
- synchronized path에서는 foundation metric definition → denominator → policy-candidate/threshold → validator/fixture → naturalization handoff → official policy ratification/hash → evaluation 순서를 바꾸지 않는다.
- `disposition_class`는 `blocking_gate | advisory_debt | non_claim` 세 token만 사용하고 diagnostic/adoption 설명은 annotation으로 분리한다.
- raw metric은 immutable하다.
- default exception set은 공집합이다.
- active waiver는 `accepted`를 만들 수 없다.
- technical/freshness failure는 waiver할 수 없다.
- unknown/missing/zero/mismatch/crash는 fail-closed다.
- policy, binding, metric snapshot, disposition, review, owner seal은 write-once/additive다.
- policy ratification은 registry의 모든 metric에 대한 exact owner affirmation을 포함해야 한다.
- live required gate adoption과 complete post-adoption evidence는 policy closure `complete`의 필수조건이다.
- owner non-adoption 또는 `adoption_timing=after_remediation`은 closure를 `incomplete`로 유지한다.
- required artifact는 present, tracked, not ignored여야 한다.
- broad staging unignore를 금지한다.
- current-route manifest는 Legacy Combined DVF Governance Route container로 유지한다.
- current core 12 modules와 tooling allowlist 1 module을 확대하지 않는다.
- machine result, independent review, owner seal은 서로 대체하지 않는다.
- exact validation command가 exit code 0이 아니면 PASS라고 기록하지 않는다.
- pre-existing failure와 current-round failure를 분리한다.
- 사용자 소유 dirty worktree 변경을 정리·덮어쓰기·재분류하지 않는다.
- top-doc sync는 additive successor entry로만 수행한다.
- top-doc successor는 terminal seal 밖에서 sealed terminal hash를 참조하고 policy closure state, evaluation subject kind/hash와 qualified disposition을 별도 축으로 병기한다.
- final claim은 policy closure와 exact qualified disposition을 별도 축으로 표현한다.

필수 비대체성:

```text
DVF Body Compiler PASS
!= public text accepted

Registry Authority PASS
!= public text accepted

Registry Runtime Compatibility PASS
!= public text accepted

Public Text Quality Acceptance Policy Closure
!= Publish Boundary PASS

Current payload deferred_internal_debt
!= Current payload accepted

Current payload blocked
!= Policy Closure FAIL

Naturalization candidate accepted
!= Registry adoption complete

Foundation contract ready
!= Policy Closure complete
```

---

## 12. Expected Closeout State

목표 closeout은 두 축으로 표현한다.

```text
Policy closure state: complete
Evaluation subject kind: current_runtime_payload | dvf_3_3_korean_naturalization_candidate
Qualified disposition: accepted | blocked | deferred_internal_debt
```

`Policy closure state: complete`에는 다음이 모두 필요하다.

```text
synchronization contract projection hash match
development foundation hash bound
evaluation subject kind/hash bound
naturalization handoff hash bound when applicable
official policy projection equals foundation precommit
policy metric-level owner ratification valid
live required gate adopted
post-adoption artifact set complete
eligible independent review complete
owner seal valid
required owner/reviewer input VCS preservation valid
terminal hash seal valid
```

독립 current-subject 실행에서 계획 작성 시점의 raw planning observation이 그대로 유지되고 v1 default exception/waiver가 비어 있다면 current payload는 `blocked`일 가능성이 높다. 그러나 이 값은 Phase 5의 fresh, hash-bound evaluation 전에는 확정하지 않는다.

synchronized naturalization closeout의 정상 예:

```text
Public Text Quality Acceptance Policy Closure: complete
Evaluation subject kind: dvf_3_3_korean_naturalization_candidate
Qualified disposition: accepted
Naturalization handoff hash: <exact hash>
Gate adoption: authorized
Official route effect: exit 0
Registry/runtime/current adoption claim: false
```

독립 current-subject blocked-immediate 경로는 계속 허용되지만 `dvf3_3_korean_naturalization__publish_boundary_sync_v1`의 canonical execution 예가 아니며 naturalization 선행조건으로 인용할 수 없다.

이 closeout은 다음을 뜻하지 않는다.

```text
Publish Boundary PASS
package-ready
package-published
release-ready
Workshop-ready
B42-ready
deployment-ready
manual-QA-complete
in-game-QA-complete
semantic-quality-complete
factually-correct
unqualified natural-language-quality-complete
gameplay-usefulness-complete
```

다음 owner decision은 terminal closure가 아니라 명시적 incomplete closeout이다.

```text
Policy ratification decision: declined
Policy closure state: incomplete

Gate adoption decision: declined | after_remediation
Policy closure state: incomplete
Phase 7 finalize: forbidden
```

live gate adoption, complete post-adoption evidence, independent review, owner seal, required owner/reviewer artifact preservation, terminal hash seal 중 하나라도 완료되지 않으면 policy closure state는 `incomplete`다. 독립 current subject가 `blocked`라는 사실 자체는 informed immediate adoption과 expected blocker attribution이 존재하는 한 closure를 `incomplete`로 내리지 않을 수 있다. synchronized naturalization candidate는 `accepted`가 아니면 `after_remediation`으로 반환하므로 Phase 7 closure에 진입하지 않는다.
