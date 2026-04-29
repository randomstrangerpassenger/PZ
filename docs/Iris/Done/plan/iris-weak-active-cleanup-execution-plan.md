# Iris Weak-Active Cleanup Execution Plan

> 상태: Implemented v1.0 (`runtime reflection deferred`)  
> 기준일: 2026-03-29  
> 상위 기준: `Philosophy.md`, `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`  
> 기준 runtime artifact: `Iris/build/description/v2/staging/interaction_cluster/source_coverage_runtime/`  
> 목적: rebuilt integrated runtime 위에서 weak-active cleanup을 provenance 기준으로 수행하고, 이후 2-stage status model과 source expansion backlog가 소비할 수 있는 구조화된 입력 데이터를 만든다.

이 문서는 초기 실행 계획과 2026-03-29 기준 1차 구현 결과를 함께 기록한다.  
분류/disposition layer 구현은 완료되었고, runtime 반영은 여전히 별도 단계다.

---

## 1. 실행 판정

- 이 작업은 `post-C integrated runtime rebuild` 이후의 **semantic cleanup track**이다.
- 이 작업의 초점은 `active` 총량을 줄이는 것이 아니라, 현재 `active 2030` 안의 runtime-active row를 **`semantic-strong / semantic-weak / semantic-adequate` 후보로 분해**하는 것이다.
- 현재 `active`는 계속 **runtime-displayable** 상태만 뜻한다. semantic completion을 뜻하지 않는다.
- 따라서 이번 cleanup은 rendered 문장 polish가 아니라 `primary_use`가 어떤 source 경로에서 생성되었는지, 그 source가 item-centric explanation으로 충분한지를 판정하는 provenance 작업으로 다룬다.
- `cluster_summary 1275`의 전면 품질 감사는 이번 cleanup의 본체가 아니다. 그쪽은 이후 별도 심화 review lane으로 남긴다.

## 2. 범위 고정

2026-03-29 기준 rebuilt integrated runtime의 전체 분포는 다음과 같이 고정한다.

- 전체 runtime rows: `2105`
- active rows: `2030`
- silent rows: `75`
- runtime path counts: `cluster_summary 1275 / identity_fallback 718 / role_fallback 112 / direct_use 0`

이번 cleanup의 직접 대상은 다음 두 묶음이다.

- weak-active 후보: `755`
  - `identity_fallback active 718`
  - `role_fallback active 37`
- missing 하위 묶음: `75`
  - `role_fallback silent 75`

이번 문서의 직접 범위 밖인 항목은 다음과 같다.

- `cluster_summary 1275`의 전면 quality review
- `C1-H1`, `C1-H2`, `C1-RH` 같은 policy-closed hold subset 재오픈
- runtime active/silent를 즉시 다시 쓰는 반영 작업
- 3-4 상세 구조를 3-3에 끌어오는 문장 확장

## 3. 기준 산출물과 authority 규칙

이번 cleanup의 authority artifact는 다음 4개로 고정한다.

- `Iris/build/description/v2/staging/interaction_cluster/source_coverage_runtime/dvf_3_3_facts.integrated.jsonl`
- `Iris/build/description/v2/staging/interaction_cluster/source_coverage_runtime/dvf_3_3_decisions.integrated.jsonl`
- `Iris/build/description/v2/staging/interaction_cluster/source_coverage_runtime/dvf_3_3_rendered.integrated.json`
- `Iris/build/description/v2/staging/interaction_cluster/source_coverage_runtime/source_coverage_runtime_summary.json`

추가 참조 자산은 다음 묶음으로 고정한다.

- `Iris/build/description/v2/staging/source_coverage/block_c/b1_consumable_package/`
- `Iris/build/description/v2/staging/source_coverage/block_c/b3_resource_package/`
- `Iris/build/description/v2/staging/source_coverage/block_c/bw_wearable_package/`
- staged `B/C` package summary, clusters, templates, facts, decisions

측정 authority는 다음처럼 분리한다.

- path provenance authority: `facts.fact_origin.primary_use`
- runtime state authority: `decisions.state`
- rendered surface reference: `rendered.entries`
- runtime headline summary reference: `source_coverage_runtime_summary.json`

이번 문서에서 쓰는 핵심 용어도 함께 고정한다.

- `승격`
  - 즉시 runtime rewrite를 뜻하지 않는다. provenance 상 `cluster_summary` justified candidate로 disposition되는 것을 뜻한다.
  - runtime 반영은 이후 2-stage status model 설계 후 별도 결정한다.

중요한 선행 리스크도 여기서 고정한다.

- 현재 integrated summary에는 `decision_use_source_counts`와 `merged_runtime_path_counts` 사이의 불일치가 존재한다.
- 2026-03-29 기준 `decision_use_source_counts`는 `cluster_summary 1275 / role_fallback 828 / identity_fallback 2`다.
- 같은 시점의 `fact_origin.primary_use` 기준 path counts는 `cluster_summary 1275 / identity_fallback 718 / role_fallback 112 / direct_use 0`다.
- 즉, weak-active cleanup의 분모와 분자는 `decisions.use_source`가 아니라 `facts.fact_origin.primary_use + decisions.state`로 계산해야 한다.
- 이 불일치는 historical rows 일부가 `decisions.use_source = role_fallback`을 유지한 채 `facts.primary_use`는 이미 `identity_fallback` 본문을 담고 있기 때문에 발생한다.

## 4. 불변 원칙

- `active != quality`를 끝까지 유지한다.
- rendered 문장만 보고 strong/weak를 판정하지 않는다.
- 먼저 보는 것은 `primary_use`의 생성 경로와 그 경로가 아이템 중심 설명으로 충분한지다.
- 3-3과 3-4의 경계는 다시 열지 않는다.
- 허용되는 것은 representative work context 요약뿐이다.
- 금지되는 것은 리스트, 재료 나열, 절차, 조건, 메뉴명, 세부 interaction 구조의 압축 복붙이다.
- `identity_fallback` 자체를 악으로 취급하지 않는다. 문제는 그것이 설명의 본체가 되는 경우다.
- weak를 전부 silent로 밀어내지 않는다. 이번 cleanup의 목적은 purge가 아니라 구조화다.
- Wearable에 억지 cluster를 붙이지 않는다. `착용`만으로는 representative work context가 아닐 수 있다.
- cleanup 결과를 runtime active/silent에 즉시 반영하지 않는다. 분류와 runtime 반영은 분리한다.

## 5. strong / weak 판정 기준

### 5-1. strong row 기준

strong row는 다음 4조건을 동시에 만족해야 한다.

- `primary_use`가 item-centric하게 읽힌다.
- representative work context가 드러난다.
- `identity_fallback`이 설명의 본체가 아니다.
- 3-4 상세 구조를 빌리지 않고도 3-3 설명이 독립적으로 성립한다.

### 5-2. weak-active taxonomy

- `W1 Salvage Fallback Weak`
  - 현재는 `identity_fallback` 또는 얕은 `role_fallback`에 기대지만, 기존 cluster 역적용이나 source 재활용으로 `cluster_summary` 승격 가능성이 있는 row
- `W2 Structurally Unclusterable`
  - 의미 있는 개별 interaction cluster를 만들 구조가 없어서 `identity_fallback`이 최종 semantic state가 될 수 있는 row
  - 신규 source를 더 파도 representative work context 자체가 3-3에 강하게 생기지 않는 row다. 해당 아이템 유형의 interaction 구조가 cluster 생성을 허용하지 않음이 확인된 경우에만 쓴다.
- `W3 Should-Be-Resourced`
  - 현재 fallback 문장을 조금 고쳐도 개선 한계가 커서, 신규 source 확장으로 넘기는 것이 맞는 row
  - 현재 source가 부족해서 약할 뿐, source가 늘면 representative work context가 생길 수 있는 row다. interaction 구조는 존재하지만 아직 매핑되지 않은 경우에 쓴다.
- `W4 Should-Be-Silent Candidate`
  - runtime active로 살아 있지만 semantic 3-3로는 말하지 않는 편이 나은 row
  - fallback 문장이 약하다는 이유만으로 부여할 수 없다. 3-3에서 침묵이 더 적절하다는 구조 근거가 있을 때만 부여한다.

### 5-3. cleanup 후 상위 semantic 분류

- `semantic-strong`
  - `cluster_summary` 기반이며 item별 작업 맥락 요약이 존재
- `semantic-adequate`
  - `identity_fallback`이지만 cluster 불가능이 확인되어 최종 상태로 인정
  - 강한 representative work context는 없지만, identity-level item meaning만으로도 3-3 침묵보다 낫다고 확인된 경우에만 인정한다.
- `semantic-weak`
  - 현재 fallback 상태가 유지되고 있으며 후속 승격 또는 resourcing 대상
- `silent`
  - `primary_use` 생성이 불가하거나 유지하지 않는 것이 맞는 경우

## 6. 실행 순서

### 6-0. W-0 Baseline Freeze and Strong Exemplar Extraction

- 목적: cleanup 분모, 판정 authority, strong vs weak 비교 기준을 한 phase 안에서 같이 봉인한다.
- 작업:
  - current integrated runtime batch를 baseline으로 고정한다.
  - 약한 row 집계가 `fact_origin.primary_use + decisions.state` 기준임을 명문화한다.
  - current summary mismatch를 known issue로 기록한다.
  - active weak 범위 `755`와 silent missing 범위 `75`를 artifact 기준으로 재확인한다.
  - `cluster_summary 1275`에서 소분류별 strong exemplar를 `2~3`개씩 뽑는다.
  - exemplar 후보는 가능하면 다음 조건을 우선 사용한다.
  - `hard_fail_codes` 없음
  - `v9_warn = false`
  - `tie_break_review_required = false`
  - representative context가 분명한 row
  - strong vs weak 판정 기준을 note 형태로 문서화한다.
- 산출물:
  - `weak_cleanup_baseline_manifest`
  - `weak_cleanup_measurement_rule_note`
  - `active_path_distribution.integrated`
  - `strong_exemplar_set`
  - `strong_vs_weak_criteria_note`
  - `weak_active_candidate_list`
  - `weak_active_candidate_summary_by_type`
- 종료 조건:
  - 이후 모든 weak-active 수치가 동일한 분모를 사용한다.
  - 이후 phase가 동일한 strong 기준을 참조한다.
- 실행 결과:
  - baseline manifest, measurement rule note, `active_path_distribution.integrated`, `strong_exemplar_set`, `weak_active_candidate_list`, `weak_active_candidate_summary_by_type`를 생성했다.
  - artifact 기준 weak-active는 `755`, missing 하위 묶음은 `75`, cleanup 총 scope는 `830`으로 고정됐다.
  - `strong_exemplar_set`은 `65`개 subgroup exemplar를 포함한다.

### 6-1. W-1 Consumable Identity-Fallback Reverse Mapping

- 목적: 이미 정의된 `B-1/B-3` 자산을 기존 weak-active row에 역적용한다.
- 대상:
  - roadmap prose 기준 `85`
  - artifact scope 기준 `88`
- 입력:
  - `b1_consumable_package`
  - `b3_resource_package`
- 작업:
  - 각 row의 subclass, item_id, current primary_use를 기준으로 기존 cluster에 1:1 매핑 가능한지 확인한다.
  - 매핑 가능 row는 `cluster_summary` 승격 후보로 분리한다.
  - 매핑 불가능 row는 `W1/W3/W4` 중 하나로 분류한다.
  - rendered 문장 비교가 아니라 cluster availability와 source 재사용성으로 판정한다.
- 산출물:
  - `w1_consumable_reverse_mapping`
  - `w1_consumable_promoted_facts`
  - `w1_consumable_disposition_note`
- 종료 조건:
  - 해당 scope 전부가 승격 또는 weak type 판정으로 닫힌다.
- 실행 결과:
  - actual scope `88`
  - `promote_candidate 87`
  - `source_backlog_candidate 1`
  - 단일 backlog row는 `Base.Bleach`다.

### 6-2. W-2 Tier 4 Existing Cluster Absorption

- 목적: 기존 staged `B/C` package cluster를 활용해 기타 identity-fallback row를 흡수한다.
- 대상:
  - roadmap prose 기준 `122`
  - artifact scope 기준 `89`
  - `Combat`, `Literature`, `Tool`, `Resource` 등 기존 cluster 후보가 남아 있는 identity-fallback row
- 작업:
  - staged package cluster catalog와 1:1 대조한다.
  - 흡수 가능 row는 `cluster_summary` 승격 후보로 보낸다.
  - 흡수 불가이지만 representative work context가 분명하면 신규 cluster 검토 대상으로 분리한다.
  - 그것도 없으면 `W2/W3/W4`로 분류한다.
- 산출물:
  - `w2_tier4_absorption_matrix`
  - `w2_promoted_facts`
  - `w2_resourcing_candidates`
- 종료 조건:
  - 이 lane에서 `identity_fallback`으로 남는 row는 모두 사유가 기록된다.
- 실행 결과:
  - actual scope `89`
  - `promote_candidate 37`
  - `retain_identity_fallback 1`
  - `source_backlog_candidate 51`
  - 단일 `W2` row는 `Base.Rope`다.

### 6-3. W-3 Unknown 148 Classification and Closure

- 목적: `IrisData` 미분류 상태를 weak-active cleanup 내부에서 먼저 닫는다.
- 대상:
  - roadmap prose 기준 `148`
  - artifact scope 기준 `144`
- 작업:
  - IrisData 소분류를 먼저 할당한다.
  - 그다음 W-2와 같은 방식으로 기존 cluster 흡수 가능성을 재판정한다.
  - 승격, `W1/W2/W3/W4`, 또는 explicit hold-like rationale 중 하나로 닫는다.
- 산출물:
  - `w3_unknown_classification_map`
  - `w3_unknown_disposition_note`
- 종료 조건:
  - weak-active inventory 안에 `Unknown` 상태가 남지 않는다.
- 실행 결과:
  - actual scope `144`
  - `promote_candidate 18`
  - `defer_to_w4 61`
  - `source_backlog_candidate 65`
  - W-3 종료 시 cleanup inventory 안의 `Unknown` 라벨은 전부 닫혔다.

### 6-4. W-4 Wearable Structural Decision

- 목적: Wearable row를 row-by-row 임시 봉합이 아니라 구조 판정으로 닫는다.
- 중요한 선행 맥락:
  - Block A에서 `wearable_preflight_decision`은 `B-W` 분리를 이미 고정했다.
  - `B-W` package는 `wear_clothing`, `wear_accessory`, `wear_headgear`, `container_storage` proxy cluster를 통해 runtime lift를 달성했다.
  - 그러나 `B-W`의 존재만으로 그 row들이 모두 `semantic-strong`이라고 자동 인정되지는 않는다.
- 핵심 질문:
  - 착용류에 `착용` 외의 representative work context가 실제로 존재하는가
  - 존재한다면 어떤 subset에서만 존재하는가
  - 존재하지 않는다면 `identity_fallback`을 `semantic-adequate` 최종 상태로 인정할 것인가
- 권장 판정 순서:
  - `container_storage` 성격의 가방류부터 우선 판정
  - 이후 방호/유틸리티처럼 subset context가 있는지 확인
  - 마지막으로 순수 착용류 잔여를 구조적으로 닫는다
- 산출물:
  - `wearable_structural_decision_memo`
  - `wearable_subset_mapping_result`
  - `wearable_semantic_adequacy_note`
- 종료 조건:
  - Wearable 잔여 row가 `semantic-strong 후보`인지 `semantic-adequate`인지 `semantic-weak`인지 구분된다.
- 실행 결과:
  - actual scope `458`
  - 이 scope는 W-0 wearable `397`과 W-3 defer `61`을 합친 값이다.
  - `promote_candidate 11`
  - `retain_identity_fallback 447`
  - 승격된 subset은 `Wearable.6-F` bag/container lane뿐이며, 나머지는 구조적으로 `W2 semantic-adequate`로 닫았다.

### 6-5. W-5 Role-Fallback Closure

- 목적: `role_fallback 112`를 active weak와 silent missing으로 분해해 닫는다.
- 대상:
  - active `37`
  - silent `75`
- 작업:
  - active `37`은 `cluster 승격 -> identity 수준 salvage -> W 분류` 순으로 판정한다.
  - silent `75`는 `primary_use` 생성 가능/불가만 다시 판정한다.
  - 생성 불가 row는 silent 유지 사유를 명시한다.
  - 생성 가능 row는 `active 전환 검토 대상`으로만 표시하고, W-6 disposition matrix에 넘긴다.
  - W-5는 `전환 가능/불가`를 가르는 단계이지, 전환 가능 row의 최종 semantic legitimacy를 닫는 단계가 아니다.
- 산출물:
  - `role_fallback_active_disposition`
  - `role_fallback_silent_rationale`
- 종료 조건:
  - `role_fallback` row 전부가 `silent 유지` 또는 `active 전환 검토 대상` 또는 즉시 weak/승격 disposition 중 하나로 닫힌다.
- 실행 결과:
  - actual scope `112`
  - active `37`은 `promote_candidate 20 / retain_identity_fallback 1 / source_backlog_candidate 16`으로 닫혔다.
  - silent `75`는 W-5에서 `promote_candidate 3 / active_transition_candidate 72`로 넘겼다.
  - 이 `72`개 전환 후보는 최종 닫힘이 아니라 W-6 semantic legitimacy review 입력으로만 남겼다.

### 6-6. W-6 Consolidation and Status-Model Input

- 목적: W-1~W-5 결과를 하나의 disposition layer로 합친다.
- 작업:
  - 전체 `755 + 75` row에 대한 row-level disposition matrix를 생성한다.
  - W-5에서 `active 전환 검토 대상`으로 넘어온 row의 cluster 매핑 가능성과 semantic adequacy를 판정해 최종 disposition을 닫는다.
  - disposition 결과를 2-stage status model 입력으로 변환한다.
  - `W1/W3` row를 source expansion backlog와 연결한다.
  - 우선순위를 `row count x weak severity x source reusability x downstream impact` 기준으로 정렬한다.
- 산출물:
  - `active_path_distribution.integrated` 갱신본
  - `weak_active_disposition_matrix`
  - `status_model_input_from_weak_cleanup`
  - `weak_cleanup_to_source_backlog_map`
  - `weak_active_group_inventory`
  - `overall_2105_row_semantic_split`
  - `integrated_facts.post_cleanup_candidate.jsonl`
- 종료 조건:
  - weak-active cleanup 결과가 이후 status-model 설계와 source backlog planning의 직접 입력으로 사용 가능하다.
- 실행 결과:
  - `active_transition_candidate`는 최종 matrix 기준 `0`이다.
  - silent review `75`는 `promote_candidate 21 / retain_identity_fallback 9 / source_backlog_candidate 45`로 최종 disposition이 닫혔다.
  - cleanup scope `830` 기준 최종 semantic split은 `semantic-strong 194 / semantic-adequate 458 / semantic-weak 178`이다.
  - 전체 runtime `2105` 기준 split은 `semantic-strong 1469 / semantic-adequate 458 / semantic-weak 178`이다.
  - runtime-semantic 교차 집계는 `generated::strong 173 / generated::adequate 449 / generated::weak 133 / missing::strong 21 / missing::adequate 9 / missing::weak 45`다.
  - 이번 rule set에서는 최종 `silent` row가 `0`이며, 이것은 누락이 아니라 explicit disposition 결과다.
  - `integrated_facts.post_cleanup_candidate.jsonl`은 candidate artifact이며 runtime 투입본이 아니다.

## 7. phase별 산출물 계약

W-0~W-5 각 phase는 최소한 다음 5종 산출물을 남겨야 한다.

- 대상 row 목록
- cluster 역적용 또는 신규 매핑 결과
- 승격된 row의 갱신 facts 또는 승격 후보 목록
- weak 분류된 row의 유형과 사유
- 갱신된 경로별 분포 집계

W-6 산출물은 다음 3종으로 구분한다.

- W-0에서 생산되고 W-6에서 갱신되는 산출물
- `active_path_distribution.integrated`

- W-0에서 생산되고 W-6에서 참조만 하는 산출물
- `strong_exemplar_set`
- `strong_vs_weak_criteria_note`
- `weak_active_candidate_list`
- `weak_active_candidate_summary_by_type`

- W-6 고유 산출물
- `weak_active_group_inventory`
- `weak_active_disposition_matrix`
- `status_model_input_from_weak_cleanup`
- `weak_cleanup_to_source_backlog_map`
- `overall_2105_row_semantic_split`
- `integrated_facts.post_cleanup_candidate.jsonl`

## 8. 운영 게이트

- 각 phase는 시작 전에 대상 row 수를 다시 집계한다.
- 각 phase는 종료 전에 `target row count == closed row count`를 만족해야 한다.
- 승격 후보는 반드시 `source path`와 `representative context` 근거를 같이 남긴다.
- `W2` 판정은 소극적 보류가 아니라 구조적 비-cluster 가능성이 확인된 경우에만 쓴다.
- `W4` 판정은 가장 보수적으로 적용한다. fallback 문장이 약하다는 이유만으로 부여하지 않고, 3-3 침묵이 더 적절하다는 구조 근거가 있어야 한다.
- `Unknown`이나 `misc` 같은 임시 범주는 종료 상태가 될 수 없다.
- `cluster_summary`로 올린 row는 가능한 한 exemplar 기준과 비교한 rationale을 남긴다.
- cleanup 중에는 runtime bridge를 다시 쓰지 않는다. classification/disposition 확정이 먼저다.

## 9. 주요 리스크

- provenance mismatch가 정리되지 않으면 weak-active 집계가 `755`가 아니라 잘못된 `790+` 범위로 흔들릴 수 있다.
- Wearable은 `B-W` proxy runtime lift와 semantic closure가 다른 문제라서, package 존재만으로 strong 판정을 내리면 안 된다.
- Unknown `148`은 분류 drift를 일으키기 쉬우므로, classification과 semantic 판정을 한 단계로 뭉개면 안 된다.
- `identity_fallback` 문장을 더 길게 쓰는 방향으로 흐르면 cleanup이 아니라 text polish로 변질된다.
- `cluster_summary 1275`를 이번 작업에 끌어와 전면 재검토하기 시작하면 weak-active cleanup의 범위가 무너진다.

## 10. 실무적 실행 순서

실제 실행 순서는 다음으로 고정한다.

1. W-0 baseline freeze and strong exemplar extraction
2. W-1 consumable reverse mapping
3. W-2 tier 4 existing cluster absorption
4. W-3 unknown classification
5. W-4 wearable structural decision
6. W-5 role-fallback closure
7. W-6 consolidation and status-model input conversion

이 순서를 유지하는 이유는 다음과 같다.

- 초반 phase에서 승격 패턴을 먼저 고정해야 Wearable과 role-fallback 판단이 덜 흔들린다.
- Wearable은 가장 큰 덩어리지만 가장 늦게 정책 판단해야 억지 cluster 부여를 피할 수 있다.
- 최종 status model 입력은 row disposition이 다 닫힌 뒤에만 의미가 있다.

## 11. 완료 판정

이번 cleanup은 다음 상태가 되면 완료로 본다.

- weak-active 후보 `755`와 silent missing `75`가 모두 disposition을 가진다.
- 각 row가 `semantic-strong / semantic-adequate / semantic-weak / silent` 중 하나로 분류된다.
- `W1/W3` row가 후속 source backlog owner를 가진다.
- `W2` row는 `identity_fallback` 최종 상태를 정당화하는 구조 사유를 가진다.
- 이후 2-stage status model 문서가 이 cleanup 산출물을 직접 입력으로 참조할 수 있다.

현재 상태는 다음과 같다.

- 위 완료 기준은 disposition layer 기준으로 충족됐다.
- [weak_active_disposition_matrix.json](C:/Users/MW/Downloads/coding/PZ/Iris/build/description/v2/staging/weak_active_cleanup/w6_aggregate/weak_active_disposition_matrix.json), [status_model_input_from_weak_cleanup.json](C:/Users/MW/Downloads/coding/PZ/Iris/build/description/v2/staging/weak_active_cleanup/w6_aggregate/status_model_input_from_weak_cleanup.json), [weak_cleanup_to_source_backlog_map.json](C:/Users/MW/Downloads/coding/PZ/Iris/build/description/v2/staging/weak_active_cleanup/w6_aggregate/weak_cleanup_to_source_backlog_map.json)이 후속 설계 입력으로 생성됐다.
- 남은 후속 작업은 runtime 반영 여부 결정, 2-stage status model 채택, backlog `178` row의 source-expansion sequencing이다.
