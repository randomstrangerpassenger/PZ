# Iris Post-Cleanup Status Model / Runtime Adoption / Backlog Expansion Execution Plan

> 상태: Frozen v1.0 (`Phase 1 ready`)  
> 기준일: 2026-03-30  
> 상위 기준: `Philosophy.md`, `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`  
> 선행 문서: `docs/iris-weak-active-cleanup-execution-plan.md`, `docs/iris-weak-active-cleanup-walkthrough.md`  
> 목적: weak-active cleanup 결과를 2-stage status model로 계약화하고, 그 규칙 위에서 runtime adoption과 backlog expansion을 순서대로 실행한다.

---

## 1. 실행 판정

- 이번 작업은 weak-active cleanup 이후의 **post-cleanup interpretation track**이다.
- 이 작업의 초점은 새 데이터를 더 많이 만드는 것이 아니라, 이미 만들어진 cleanup 결과를 시스템 의미로 고정하는 것이다.
- 따라서 순서는 `Phase 1: status model -> Phase 2: runtime adoption -> Phase 3: backlog expansion`으로 고정한다.
- `Phase 1 -> Phase 2`는 하드 선행이다.
- `Phase 3`의 탐색은 `Phase 1`과 병행 가능하지만, 본실행은 `Phase 2` 이후가 기준선 관리상 안전하다.

## 2. 현재 상태 고정

이번 계획의 입력 baseline은 weak-active cleanup W-6 aggregate 결과로 고정한다.

기준 artifact:

- `Iris/build/description/v2/staging/weak_active_cleanup/w6_aggregate/weak_cleanup_aggregate_summary.json`
- `Iris/build/description/v2/staging/weak_active_cleanup/w6_aggregate/weak_active_disposition_matrix.json`
- `Iris/build/description/v2/staging/weak_active_cleanup/w6_aggregate/status_model_input_from_weak_cleanup.json`
- `Iris/build/description/v2/staging/weak_active_cleanup/w6_aggregate/full_runtime_fourway_classification.json`
- `Iris/build/description/v2/staging/weak_active_cleanup/w6_aggregate/weak_cleanup_to_source_backlog_map.json`
- `Iris/build/description/v2/staging/weak_active_cleanup/w6_aggregate/integrated_facts.post_cleanup_candidate.jsonl`

baseline 수치는 다음과 같이 고정한다.

### 2-1. cleanup scope `830`

| 분류 | 수 |
|------|---:|
| semantic-strong | 194 |
| semantic-adequate | 458 |
| semantic-weak | 178 |

### 2-2. full runtime `2105`

| 분류 | 수 |
|------|---:|
| semantic-strong | 1469 |
| semantic-adequate | 458 |
| semantic-weak | 178 |

### 2-3. runtime x semantic cross matrix

| runtime | strong | adequate | weak | 합계 |
|---------|------:|---------:|-----:|----:|
| generated | 173 | 449 | 133 | 755 |
| missing | 21 | 9 | 45 | 75 |
| 합계 | 194 | 458 | 178 | 830 |

### 2-4. backlog `178` 출처

| 출처 phase | 수 | runtime 상태 | 성격 |
|------------|---:|-------------|------|
| W-1 | 1 | generated | 단건 backlog |
| W-2 | 51 | generated | 기존 cluster 흡수 불가 |
| W-3 | 65 | generated | Unknown 분류 후 source 부족 |
| W-5 | 16 | generated | role_fallback active 잔여 |
| W-6 | 45 | missing | silent review 후 source 부족 |

## 3. 세 작업의 의존관계

- `Phase 1 -> Phase 2`는 하드 선행이다.
- `Phase 2 -> Phase 3`는 운영상 권장 순서다.
- `Phase 3`의 탐색 단계만 `Phase 1`과 병행 가능하다.

해석은 다음과 같다.

- `Phase 1`은 "이 상태를 runtime이 어떻게 읽을 것인가"를 정한다.
- `Phase 2`는 그 규칙을 실제 runtime facts / rendered / Lua bridge에 적용할지 결정한다.
- `Phase 3`은 `semantic-weak 178`을 strong 또는 adequate로 줄여 나가는 후속 제작 lane이다.

## 4. 불변 원칙

- 2-stage status model은 표시용 label이 아니라 **Iris 내부 semantic contract**다.
- 기존 active/silent를 폐기하지 않는다. `generated/missing`으로 명시화하고 semantic axis를 독립적으로 얹는다.
- `integrated_facts.post_cleanup_candidate.jsonl`은 adoption 전까지 candidate artifact다.
- `semantic-adequate`를 `semantic-strong`처럼 다루지 않는다.
- W-4 Wearable 구조 판정은 재오픈하지 않는다.
- backlog expansion에서도 3-3 / 3-4 경계를 다시 열지 않는다.
- cleanup disposition authority를 다시 분류하지 않는다. 기준은 `weak_active_disposition_matrix`다.
- 이 모델은 Pulse 플랫폼 정책이 아니라 Iris 내부 semantic 체계다.

## 5. Phase 0: Post-Cleanup Input Freeze

목적:

- post-cleanup 이후의 후속 설계가 모두 같은 입력 artifact를 기준으로 하게 만든다.

작업:

- cleanup W-6 aggregate 산출물 경로와 row count를 manifest에 고정한다.
- cleanup scope `830`, full runtime `2105`, backlog `178`을 baseline 수치로 재기록한다.
- `integrated_facts.post_cleanup_candidate.jsonl`을 candidate-only artifact로 명시한다.
- 이후 status model 논의에서 사용 가능한 field authority를 함께 기록한다.

산출물:

- `post_cleanup_baseline_manifest.json`
- `post_cleanup_input_note.md`

완료 조건:

- 이후 phase가 동일한 분모와 동일한 artifact 집합을 본다.

## 6. Phase 1: 2-Stage Status Model 설계

### 6-1. 목적

- cleanup 결과를 runtime이 소비 가능한 2축 semantic/runtime 모델로 계약화한다.

### 6-2. 축 정의

#### runtime axis

| 상태 | 조건 | 현재 대응 |
|------|------|----------|
| generated | runtime-consumable body가 존재하여 runtime이 이 row를 소비할 수 있음 | 현재 active와 대체로 대응 |
| missing | runtime-consumable body가 없어 runtime이 이 row를 소비할 수 없음 | 현재 silent와 대체로 대응 |

현재 active/silent 대응은 설명용 reference이며, runtime axis의 정의 자체는 runtime-consumable body의 존재 여부를 기준으로 한다.

#### semantic axis

| 상태 | 조건 | cleanup 대응 |
|------|------|-------------|
| strong | representative work context가 cluster_summary로 정당화됨 | 기존 cluster_summary + cleanup promote |
| adequate | identity-level meaning이 최종 상태로 구조적으로 허용됨 | W2 retain |
| weak | source 부족 또는 미매핑으로 후속 작업 필요 | W1/W3 backlog |

`semantic-silent`는 예약 상태로만 열어 두고, 현재 row count는 `0`으로 유지한다.

### 6-3. 6셀 처리 규칙 초안

| runtime \ semantic | strong | adequate | weak |
|--------------------|--------|----------|------|
| generated | 정상 표시 | 표시 유지 | 표시 유지 / demotion 검토 |
| missing | adopt 후보 | adopt 검토 또는 유지 | source-expansion 대상 |

이 표는 Phase 1에서 최종 확정될 provisional draft이며, 특히 `generated::weak`, `missing::strong`, `missing::adequate`의 세부 처리 규칙은 이 phase의 결정 사항으로 닫힌다.

### 6-4. 이 phase에서 닫아야 할 5개 결정

1. `generated::weak 133`의 runtime 취급
2. `missing::strong 21`의 adopt 시점
3. `missing::adequate 9`의 adopt 여부
4. `missing::weak 45`의 우선순위
5. semantic quality를 runtime UI에 노출할지의 방향

이 5개는 선택지를 열어 두고 시작하되, phase 종료 시 반드시 단일 판정으로 닫아야 한다.

Phase 1 진입 시 우선적으로 정밀화할 잔여 포인트는 다음 두 가지다.

- `missing::strong 21`을 즉시 adopt할지, 별도 validation gate 이후 adopt할지
- `generated::weak 133`에 대해 `유지 / 보류 / demotion 검토` 중 어떤 원칙을 default로 둘지

이 두 항목은 현재 문서의 미결함이 아니라, 의도적으로 Phase 1의 5개 결정 사항 안에 남겨 둔 핵심 쟁점이다.

### 6-5. 작업

- `generated/missing x strong/adequate/weak`의 허용 조합을 정의한다.
- 각 조합의 runtime consume rule을 문서화한다.
- 각 조합이 `adopt / keep / demote / backlog` 중 어느 처리로 이어지는지 전환 규칙을 정리한다.
- UI contract가 runtime contract를 오염시키지 않도록 두 층을 분리 기록한다.
- 5개 결정 사항을 JSON과 note 양쪽에 남긴다.

### 6-6. 산출물

- `2_stage_status_model_spec.md`
- `status_model_decisions.json`
- `ui_quality_indicator_decision.md`
- `runtime_state_transition_rules.md`
- `status_combination_matrix.json`

UI contract 방향 결정은 `status_model_decisions.json`에 최종 판정을 기록하고, `ui_quality_indicator_decision.md`에 rationale과 비채택 옵션을 기록한다.

### 6-7. 완료 조건

- 6셀 각각의 runtime 취급 규칙이 확정된다.
- 5개 결정 사항이 모두 닫힌다.
- Phase 2가 이 규칙을 기계적으로 적용할 수 있다.

## 7. Phase 2: Runtime Adoption 결정 및 실행

### 7-1. 목적

- Phase 1 규칙을 적용해 candidate facts 중 무엇을 실제 runtime input으로 채택할지 결정하고, 채택분만 공식 runtime에 반영한다.

### 7-2. Step 2-A: Adoption Scope Freeze

작업:

- `missing::strong 21`의 adopt 여부 확정
- `missing::adequate 9`의 adopt 여부 확정
- `generated::weak 133`의 유지 / demotion 여부 확정
- `missing::weak 45`는 기본 backlog로 남기되, 명시적 비-adopt 처리

산출물:

- `adoption_scope_manifest.json`

완료 조건:

- adopt / keep / demote 대상 row가 전부 닫힌다.

### 7-3. Step 2-B: Candidate Facts Validation

작업:

- adopt 대상 row에 대해 candidate facts validation 수행
- 기존 pipeline contract 위반 여부 확인
- rendered 생성 가능 여부 확인
- forbidden pattern / gate 위반 여부 확인

산출물:

- `adoption_validation_report.json`

완료 조건:

- adopt 대상 row가 pass 또는 exclusion rationale을 가진다.

### 7-4. Step 2-C: Runtime Rebuild

작업:

- 공식 integrated facts를 base로 사용한다.
- adopt 대상 row는 `integrated_facts.post_cleanup_candidate.jsonl`의 값으로 overlay한다.
- adopt되지 않는 row는 기존 facts를 유지한다.
- demotion 대상이 있으면 Phase 1에서 닫힌 `runtime_state_transition_rules`에 따라 `generated -> missing` 전환을 적용한다.
- facts -> rendered -> Lua bridge를 재생성한다.
- adopted runtime summary와 diff를 기록한다.

산출물:

- `dvf_3_3_facts.adopted.jsonl`
- `dvf_3_3_rendered.adopted.json`
- `IrisLayer3Data.lua`
- `adoption_runtime_summary.json`
- `adoption_diff_report.json`

완료 조건:

- adopted runtime summary가 Phase 1 규칙과 일치한다.

### 7-5. Step 2-D: In-Game Validation

작업:

- adopt된 row가 정상 표시되는지 확인
- demotion된 row가 정상 숨김되는지 확인
- 기존 strong row regression이 없는지 확인
- UI indicator를 도입했다면 그것도 같이 검증

산출물:

- `in_game_validation_checklist.md`

완료 조건:

- runtime adoption 결과가 실제 인게임에서 회귀 없이 동작한다.

## 8. Phase 3: Backlog `178` Source Expansion

### 8-1. 목적

- `semantic-weak 178`을 strong / adequate / hold 중 하나로 후속 해소한다.

여기서 `hold`는 semantic axis 상태가 아니라, Phase 3 execution 이후에도 source package로 닫지 않고 보류하기로 결정된 backlog 운영 상태다.

### 8-2. 탐색 트랙

이 단계는 `Phase 1`과 병행 가능하다.

작업:

- `178`의 소분류별 분포 집계
- 기존 cluster 재활용 가능성 재점검
- 신규 cluster 필요 cohort 식별
- `generated::weak 133`와 `missing::weak 45`의 우선순위 영향 분석

산출물:

- `backlog_178_subclass_distribution.json`
- `backlog_178_cluster_reuse_assessment.json`
- `backlog_178_new_cluster_candidates.json`

완료 조건:

- backlog를 실제 package 단위로 나눌 준비가 된다.

### 8-3. 본실행

이 단계는 `Phase 2` 이후에 시작한다.

#### Step 3-A. Package Split

작업:

- 소분류 크기
- cluster 재활용성
- runtime urgency
- `generated::weak` vs `missing::weak` 우선순위

위 네 기준으로 package를 나눈다.

산출물:

- `backlog_178_package_plan.md`

#### Step 3-B. Package Execution

작업:

- source 생성
- cluster 정의 또는 재사용
- facts / decisions / rendered 생성
- pilot review 수행

산출물:

- package별 source coverage 산출물 일체

#### Step 3-C. Runtime Integration

작업:

- Phase 2 adopted runtime을 base로 사용한다.
- 새 package를 merge한다.
- runtime summary와 semantic quality metadata를 갱신한다.

산출물:

- `backlog_integration_summary.json`
- package merge 후 runtime artifacts

#### Step 3-D. In-Game Validation

작업:

- 새로 active가 된 row 정상 표시 확인
- 기존 row regression 없음 확인

### 8-4. 완료 조건

- backlog `178`이 `semantic-strong / semantic-adequate / hold` 중 하나로 닫힌다.
- runtime 통합 후 regression 없이 인게임 검증이 통과한다.

## 9. phase별 산출물 계약

### 9-1. Phase 0

- baseline manifest
- input note

### 9-2. Phase 1

- 2-stage spec
- decisions JSON
- UI quality indicator decision note
- transition rules
- combination matrix

### 9-3. Phase 2

- adoption scope manifest
- adoption validation report
- adopted facts / rendered / Lua bridge
- runtime summary / diff report
- in-game validation checklist

### 9-4. Phase 3

- backlog exploration reports
- package split plan
- package execution outputs
- integration summary
- in-game validation checklist

## 10. 운영 게이트

- Phase 1 없이 Phase 2를 실행하지 않는다.
- Phase 2 공식 runtime 기준선 없이 Phase 3 본실행을 시작하지 않는다.
- runtime contract와 UI contract를 혼동하지 않는다.
- candidate facts를 공식 facts와 혼동하지 않는다.
- `semantic-adequate`를 strong처럼 취급하지 않는다.
- `adequate` row의 adopt는 identity_fallback 수준 이상의 runtime-consumable `primary_use` 생성이 가능한 경우에만 허용한다.
- W-4 Wearable 구조 판정을 재오픈하지 않는다.
- cleanup disposition authority를 무시하고 처음부터 다시 분류하지 않는다.
- backlog expansion에서도 3-3 / 3-4 경계를 다시 열지 않는다.

## 11. 주요 리스크

- `generated::weak 133` 처리 결정을 늦추면 adoption 범위와 backlog 우선순위가 같이 흔들릴 수 있다.
- `missing::adequate 9`를 성급하게 adopt하면 adequate와 strong의 경계가 흐려질 수 있다.
- `integrated_facts.post_cleanup_candidate.jsonl`을 공식 facts처럼 다루기 시작하면 baseline 관리가 무너진다.
- Phase 2 이전에 backlog package를 본격 실행하면 merge base가 다시 흔들린다.
- semantic quality UI 노출을 먼저 밀어붙이면 runtime contract 설계가 오염될 수 있다.

## 12. 실무적 실행 순서

실제 실행 순서는 다음으로 고정한다.

1. Phase 0 post-cleanup input freeze
2. Phase 1 2-stage status model 설계
3. Phase 2-A adoption scope freeze
4. Phase 2-B candidate validation
5. Phase 2-C runtime rebuild
6. Phase 2-D in-game validation
7. Phase 3 탐색
8. Phase 3 package split / execution / integration

이 순서를 유지하는 이유는 다음과 같다.

- status model이 없으면 adoption 판단 기준이 없다.
- adopted runtime이 없으면 backlog integration base가 흔들린다.
- backlog 탐색은 병행할 수 있지만, 본실행은 기준선이 고정된 뒤가 안전하다.

## 13. 완료 판정

이번 로드맵은 다음 상태가 되면 완료로 본다.

- 2-stage status model이 문서와 데이터 양쪽에서 확정된다.
- runtime adoption 범위가 결정되고, adopted runtime artifacts가 생성된다.
- adopted runtime이 인게임 검증을 통과한다.
- backlog `178`이 strong / adequate / hold 중 하나로 닫힌다.

이번 문서는 weak-active cleanup 자체의 완료 여부를 다시 논의하는 문서가 아니다.  
이 문서는 cleanup 이후의 해석, 채택, 확장을 어떻게 순서대로 실행할지 정리하는 후속 execution plan이다.

현재 문서 상태는 `Frozen v1.0`이며, 다음 실행 단계는 `Phase 1: 2-stage status model 설계`다.
