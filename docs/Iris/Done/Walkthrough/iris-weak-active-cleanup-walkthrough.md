# Iris Weak-Active Cleanup Walkthrough

_Last updated: 2026-03-29_

## 1. 목적

이 문서는 `docs/iris-weak-active-cleanup-execution-plan.md`가 실제로 어떻게 실행됐는지 한 번에 따라가기 위한 walkthrough다.

이 walkthrough의 초점은 네 가지다.

- 어떤 runtime baseline에서 weak-active cleanup이 시작됐는가
- `W-0`부터 `W-6`까지 각 phase가 실제로 무엇을 닫았는가
- 최종 disposition layer가 어떤 수치로 끝났는가
- 무엇이 이번 로드맵의 완료 범위이고, 무엇이 다음 단계로 넘어갔는가

상위 기준은 다음 문서들이다.

- `Philosophy.md`
- `docs/DECISIONS.md`
- `docs/ARCHITECTURE.md`
- `docs/ROADMAP.md`
- `docs/iris-weak-active-cleanup-execution-plan.md`

## 2. 시작점과 끝점

이 작업은 이미 rebuilt integrated runtime이 존재하는 상태에서 시작했다.

- 시작 runtime rows: `2105`
- 시작 active rows: `2030`
- 시작 silent rows: `75`
- 시작 path distribution: `cluster_summary 1275 / identity_fallback 718 / role_fallback 112 / direct_use 0`

cleanup의 직접 대상은 다음 `830` rows였다.

- weak-active: `755`
- missing 하위 묶음: `75`

이 walkthrough 시점의 최종 disposition layer는 다음 상태로 닫혔다.

- cleanup scope semantic split: `semantic-strong 194 / semantic-adequate 458 / semantic-weak 178`
- full runtime semantic split: `semantic-strong 1469 / semantic-adequate 458 / semantic-weak 178`
- runtime-semantic split: `generated::strong 173 / generated::adequate 449 / generated::weak 133 / missing::strong 21 / missing::adequate 9 / missing::weak 45`
- residual `active_transition_candidate`: `0`

즉, 이번 로드맵은 "weak-active와 silent review input을 provenance 기준 disposition layer로 끝까지 닫는 것"까지를 포함한다.  
반대로 runtime 반영과 2-stage status model 채택은 이 walkthrough의 완료 범위 밖이다.

## 3. 전체 흐름

실행 흐름은 크게 7단계로 볼 수 있다.

1. `W-0`에서 baseline, measurement authority, strong exemplar를 고정한다.
2. `W-1`에서 Consumable / Resource 일부를 기존 cluster로 역적용한다.
3. `W-2`에서 기타 identity-fallback row를 기존 staged cluster에 흡수한다.
4. `W-3`에서 Unknown row를 분류하고 승격 또는 backlog로 닫는다.
5. `W-4`에서 Wearable을 row별 봉합이 아니라 구조 판정으로 닫는다.
6. `W-5`에서 role-fallback active/silent를 정리하고 silent review input을 분리한다.
7. `W-6`에서 전체 disposition matrix와 status-model input을 생성한다.

아래부터는 이 7단계를 순서대로 본다.

## 4. W-0: Baseline Freeze

`W-0`의 역할은 숫자 논쟁을 끝내고 이후 phase가 모두 같은 authority를 보게 만드는 것이었다.

핵심 산출물:

- `Iris/build/description/v2/staging/weak_active_cleanup/w0/weak_cleanup_baseline_manifest.json`
- `Iris/build/description/v2/staging/weak_active_cleanup/w0/weak_cleanup_measurement_rule_note.md`
- `Iris/build/description/v2/staging/weak_active_cleanup/w0/active_path_distribution.integrated.json`
- `Iris/build/description/v2/staging/weak_active_cleanup/w0/strong_exemplar_set.json`
- `Iris/build/description/v2/staging/weak_active_cleanup/w0/weak_active_candidate_list.json`

이 단계에서 고정된 핵심 판단은 다음과 같다.

- measurement authority는 `facts.fact_origin.primary_use + decisions.state`
- weak-active scope는 `755`
- missing 하위 묶음은 `75`
- cleanup 총 scope는 `830`
- provenance/decision mismatch는 `716`
- strong exemplar는 `65`개 subgroup에서 추출

이 시점의 의미는 단순하다.

- 이후 약한 row 수치는 proposal-era 수치가 아니라 repo artifact 수치로 읽는다.
- `decisions.use_source`는 reference일 뿐, cleanup 집계 authority가 아니다.
- strong/weak 비교 기준도 이 시점에 동결된다.

## 5. W-1: Consumable Reverse Mapping

`W-1`은 가장 기계적으로 역적용 가능한 lane을 먼저 닫는 단계였다.

핵심 산출물:

- `Iris/build/description/v2/staging/weak_active_cleanup/w1_consumable_reverse_mapping/w1_consumable_reverse_mapping_summary.json`
- `Iris/build/description/v2/staging/weak_active_cleanup/w1_consumable_reverse_mapping/w1_consumable_reverse_mapping.json`
- `Iris/build/description/v2/staging/weak_active_cleanup/w1_consumable_reverse_mapping/w1_consumable_promoted_candidate_facts.jsonl`

실행 결과:

- roadmap prose target: `85`
- actual artifact scope: `88`
- `promote_candidate 87`
- `weak_type_required 1`
- weak-type row는 `W3 1`

승격된 cluster 분포는 다음과 같다.

- `food_consumption 64`
- `beverage_consumption 12`
- `cooking_prep 10`
- `comfort_consumption 1`

이 단계의 핵심은 "이미 staged package가 있는 lane은 weak-active cleanup에서 바로 strong candidate로 올릴 수 있다"는 패턴을 확정한 것이다.  
유일한 backlog row는 `Base.Bleach`였다.

## 6. W-2: Existing Cluster Absorption

`W-2`는 W-1 바깥의 classified identity-fallback row를 기존 staged cluster에 흡수하는 단계였다.

핵심 산출물:

- `Iris/build/description/v2/staging/weak_active_cleanup/w2_existing_cluster_absorption/w2_existing_cluster_absorption_summary.json`
- `Iris/build/description/v2/staging/weak_active_cleanup/w2_existing_cluster_absorption/w2_existing_cluster_absorption.json`
- `Iris/build/description/v2/staging/weak_active_cleanup/w2_existing_cluster_absorption/w2_promoted_candidate_facts.jsonl`

실행 결과:

- roadmap prose target: `122`
- actual artifact scope: `89`
- `promote_candidate 37`
- `retain_identity_fallback 1`
- `source_backlog_candidate 51`

승격된 cluster 분포는 다음과 같다.

- `map_reference 14`
- `medical_treatment 8`
- `kitchen_table_handling 5`
- `cooking_prep 4`
- `electronics_assembly 3`
- `melee_combat 3`

유일한 `W2` row는 `Base.Rope`다.  
즉, 이 단계는 "기존 package를 안전하게 재사용할 수 있는 row"와 "source가 더 필요한 row"를 본격적으로 갈라낸 단계다.

## 7. W-3: Unknown Closure

`W-3`의 목적은 weak-active inventory 안에 `(missing)` classification을 남기지 않는 것이었다.

핵심 산출물:

- `Iris/build/description/v2/staging/weak_active_cleanup/w3_unknown_classification/w3_unknown_classification_summary.json`
- `Iris/build/description/v2/staging/weak_active_cleanup/w3_unknown_classification/w3_unknown_classification_and_disposition.json`
- `Iris/build/description/v2/staging/weak_active_cleanup/w3_unknown_classification/w3_promoted_candidate_facts.jsonl`

실행 결과:

- roadmap prose target: `148`
- actual artifact scope: `144`
- `promote_candidate 18`
- `defer_to_w4 61`
- `source_backlog_candidate 65`

새로 할당된 primary classification 분포는 다음이 핵심이다.

- `Resource.4-E 53`
- `Wearable.6-C 37`
- `Wearable.6-B 17`
- `Combat.2-J 10`
- `Wearable.6-F 8`
- `Wearable.6-G 7`
- `Tool.1-G 6`

이 단계가 끝나면 weak-active inventory 안의 `Unknown`은 모두 사라진다.  
즉, 이후 판단은 "미분류라서 보류"가 아니라 "분류 후에도 strong/adequate/weak 중 어디냐"가 된다.

## 8. W-4: Wearable Structural Decision

`W-4`는 row-by-row wording 보정이 아니라 policy phase였다.

핵심 산출물:

- `Iris/build/description/v2/staging/weak_active_cleanup/w4_wearable_structural_decision/w4_wearable_structural_decision_summary.json`
- `Iris/build/description/v2/staging/weak_active_cleanup/w4_wearable_structural_decision/w4_wearable_structural_decision.json`
- `Iris/build/description/v2/staging/weak_active_cleanup/w4_wearable_structural_decision/wearable_decision_memo.md`

실행 결과:

- actual scope: `458`
- W-0 wearable input: `397`
- W-3 deferred wearable input: `61`
- `promote_candidate 11`
- `retain_identity_fallback 447`

정책 판단은 이렇게 고정됐다.

- bag subset은 `container_storage`로 승격 가능
- non-bag wearable은 구조적으로 `W2 semantic-adequate`

즉, 이 단계의 결론은 "Wearable을 억지 cluster로 올리지 않는다"는 것이다.  
강한 representative context가 있는 subset은 bag lane뿐이고, 나머지는 identity-level meaning을 최종 상태로 인정했다.

## 9. W-5: Role-Fallback Closure

`W-5`는 role-fallback lane을 active weak와 silent review input으로 분해하는 단계였다.

핵심 산출물:

- `Iris/build/description/v2/staging/weak_active_cleanup/w5_role_fallback_cleanup/w5_role_fallback_cleanup_summary.json`
- `Iris/build/description/v2/staging/weak_active_cleanup/w5_role_fallback_cleanup/w5_role_fallback_cleanup.json`
- `Iris/build/description/v2/staging/weak_active_cleanup/w5_role_fallback_cleanup/w5_role_fallback_promoted_candidate_facts.jsonl`

실행 결과:

- actual scope: `112`
- active rows: `37`
- silent rows: `75`

W-5 종료 시 disposition은 다음과 같았다.

- `promote_candidate 23`
- `retain_identity_fallback 1`
- `source_backlog_candidate 16`
- `active_transition_candidate 72`

여기서 중요한 점은 `72`개 전환 후보가 아직 최종 결론이 아니라는 점이다.  
W-5는 "runtime-silent을 active 검토 대상으로 넘길 것인지"만 판정했고, semantic legitimacy closure는 W-6로 넘겼다.

## 10. W-6: Consolidation and Final Disposition

`W-6`은 W-1~W-5를 하나의 disposition layer로 합치는 단계였다.

핵심 산출물:

- `Iris/build/description/v2/staging/weak_active_cleanup/w6_aggregate/weak_cleanup_aggregate_summary.json`
- `Iris/build/description/v2/staging/weak_active_cleanup/w6_aggregate/weak_active_disposition_matrix.json`
- `Iris/build/description/v2/staging/weak_active_cleanup/w6_aggregate/status_model_input_from_weak_cleanup.json`
- `Iris/build/description/v2/staging/weak_active_cleanup/w6_aggregate/weak_cleanup_to_source_backlog_map.json`
- `Iris/build/description/v2/staging/weak_active_cleanup/w6_aggregate/full_runtime_fourway_classification.json`
- `Iris/build/description/v2/staging/weak_active_cleanup/w6_aggregate/integrated_facts.post_cleanup_candidate.jsonl`

최종 결과는 다음과 같다.

- cleanup scope rows: `830`
- `semantic-strong 194`
- `semantic-adequate 458`
- `semantic-weak 178`

runtime-semantic 분포는 다음과 같다.

- `generated::semantic-strong 173`
- `generated::semantic-adequate 449`
- `generated::semantic-weak 133`
- `missing::semantic-strong 21`
- `missing::semantic-adequate 9`
- `missing::semantic-weak 45`

silent review `75`의 최종 closure는 다음과 같다.

- `promote_candidate 21`
- `retain_identity_fallback 9`
- `source_backlog_candidate 45`

즉, `active_transition_candidate`는 최종 matrix 기준 `0`이다.  
이번 rule set에서는 semantic `silent`가 최종 `0`으로 끝났는데, 이는 omission이 아니라 explicit disposition 결과다.

## 11. 산출물의 의미

이번 로드맵이 남긴 핵심 산출물은 각각 용도가 다르다.

- `weak_active_disposition_matrix.json`
  - cleanup 대상 `830` rows의 최종 disposition 원장
- `status_model_input_from_weak_cleanup.json`
  - 이후 2-stage status model 설계가 직접 소비할 입력
- `weak_cleanup_to_source_backlog_map.json`
  - `semantic-weak 178` rows를 후속 source-expansion 큐로 넘기는 backlog 맵
- `integrated_facts.post_cleanup_candidate.jsonl`
  - cleanup 결과를 facts에 overlay한 candidate batch
  - 현재 runtime이 읽는 공식 facts 교체본은 아니다

이 네 개를 구분해서 읽는 것이 중요하다.

- disposition matrix는 분류 결과다.
- status-model input은 후속 설계 입력이다.
- backlog map은 후속 제작 큐다.
- candidate facts는 runtime 반영 후보본이다.

## 12. 구현 entrypoint

이 walkthrough를 코드 기준으로 따라가려면 아래 스크립트들이 핵심이다.

- `Iris/build/description/v2/tools/build/report_weak_active_cleanup_w0.py`
- `Iris/build/description/v2/tools/build/report_weak_active_cleanup_w1_consumable_reverse_mapping.py`
- `Iris/build/description/v2/tools/build/report_weak_active_cleanup_w2_existing_cluster_absorption.py`
- `Iris/build/description/v2/tools/build/report_weak_active_cleanup_w3_unknown_classification.py`
- `Iris/build/description/v2/tools/build/report_weak_active_cleanup_w4_wearable_structural_decision.py`
- `Iris/build/description/v2/tools/build/report_weak_active_cleanup_w5_role_fallback_cleanup.py`
- `Iris/build/description/v2/tools/build/report_weak_active_cleanup_w6_aggregate.py`

검증은 다음 테스트 묶음이 기준이다.

- `Iris/build/description/v2/tests/test_weak_active_cleanup_w0.py`
- `Iris/build/description/v2/tests/test_weak_active_cleanup_w1_consumable_reverse_mapping.py`
- `Iris/build/description/v2/tests/test_weak_active_cleanup_w2_existing_cluster_absorption.py`
- `Iris/build/description/v2/tests/test_weak_active_cleanup_w3_unknown_classification.py`
- `Iris/build/description/v2/tests/test_weak_active_cleanup_w4_wearable_structural_decision.py`
- `Iris/build/description/v2/tests/test_weak_active_cleanup_w5_role_fallback_cleanup.py`
- `Iris/build/description/v2/tests/test_weak_active_cleanup_w6_aggregate.py`

## 13. 완료 판정

이번 walkthrough 기준 완료 판정은 다음처럼 읽는다.

- weak-active cleanup roadmap 범위는 완료
- W-0~W-6 disposition layer 구현도 완료
- row-level cleanup closure도 완료
- status-model input과 backlog map 생성도 완료

반대로 아직 별도 후속 과제로 남아 있는 것은 다음이다.

- 2-stage status model 설계
- `integrated_facts.post_cleanup_candidate.jsonl`의 runtime adoption 결정
- cleanup backlog `178` row의 source-expansion 실행

즉, "weak-active cleanup 로드맵이 끝났다"와 "후속 semantic/runtime 작업이 전부 끝났다"는 같은 말이 아니다.
