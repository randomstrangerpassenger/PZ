# Iris DVF 3-3 Interaction Cluster Execution Plan

> 상태: Draft v0.1  
> 기준일: 2026-03-27  
> 상위 기준: `Philosophy.md`, `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`  
> 목적: DVF 3-3이 4계층의 대표 작업 맥락을 합헌적으로 요약할 수 있도록, 기존 v4 실행계획 위에 interaction cluster 연계 구조를 증설한다.

---

## 1. 실행 판정

- 실행 프레임은 **독립 로드맵**이 아니라 **기존 v4 실행계획 확장형**으로 고정한다.
- 따라서 새 작업은 별도 Phase 체계를 만들지 않고, 기존 A/B/C/D와 G1/G3/G5 게이트에 매핑한다.
- Phase C와 Phase D의 이름과 구조는 기존 v4를 유지한다.
  - Phase C: `C-1 pilot -> C-2 확대 -> C-3 full rebuild go/no-go`
  - Phase D: `D-1 Lua bridge -> D-2 소비자 확인 -> D-3 인게임 검증`
- 다만 Claude안만으로는 경계 문서화와 병합 규칙이 약하므로, ChatGPT안의 정책 선행 단계와 경계 예시집, 병합 4케이스, FAIL 코드 확장을 필수로 병합한다.

## 2. 불변 원칙

- 3-3은 계속 **item-centric body**이며, 3-4 상세 상호작용층을 흡수하지 않는다.
- 3-3이 4계층에서 차용할 수 있는 것은 **대표 용도 / 대표 작업군 / 대표 상호작용 맥락의 요약**뿐이다.
- 3-3이 차용하면 안 되는 것은 **상호작용 목록, 재료 목록, 요구 조건, 메뉴명/행동명, 세부 절차, 레시피 열거**다.
- 기존 direct use 문장이 이미 작업 맥락 수준의 구체성을 갖고 있으면 cluster 요약으로 덮어쓰지 않는다.
- cluster 운영은 현재 approval backlog용 hotspot/cluster 운영과 혼동하지 않는다. 이번 문서의 cluster는 **3-3 본문 생성용 interaction cluster**다.

## 3. 산출물 기준 경로

실제 구현 문서는 historical DVF 경로를 기준으로 가정한다.

- 기준 루트: `Iris/build/description/v2/`
- 현재 문서는 그 실행안을 `docs/`에 별도 고정한 것이다.

예상 산출물은 다음과 같다.

- `dvf_3_3_text_policy.md`
- `3_3_vs_4_boundary_examples.md`
- `interaction_clusters.json`
- `cluster_summary_templates.json`
- `cluster_abstraction_floor.md`
- `cluster_selection_rules.md`
- `use_hint_generation_rules_v2.md`

## 4. Work Breakdown

### A-4-0. 정책 재정의 및 경계 문서화

- 목표: cluster 정의 전에 3-3과 3-4의 차용 경계를 문서로 먼저 잠근다.
- 산출물: `dvf_3_3_text_policy.md`, `3_3_vs_4_boundary_examples.md`
- 작업:
  - 3-3이 4계층에서 빌려올 수 있는 정보 유형을 명시한다.
  - 3-3이 빌려오면 안 되는 정보 유형을 명시한다.
  - 허용/금지 예시 쌍을 최소 10쌍 이상 작성한다.
  - 허용 예시는 게임 내 작업 맥락을 포함한 허용 골격으로 고정한다.
  - 금지 예시는 레시피 열거, 재료 나열, 메뉴명, 세부 조작 경로를 포함한 형태로 고정한다.
- 완료 기준:
  - 제3자가 예시집만 읽고 허용/금지를 구분할 수 있다.
  - 경계 논쟁 없이 A-4-1 cluster 정의에 착수할 수 있다.
- 기간: +0.5~1일
- 의존: 없음

### A-4-1. Interaction Cluster 정의

- 목표: 4계층의 풍부한 상호작용 공간을 3-3용 대표 작업군으로 압축한다.
- 산출물: `interaction_clusters.json`
- 작업:
  - 4계층 데이터에서 대표 작업 맥락군을 도출한다.
  - cluster는 3-3용 요약 단위이지 4계층 목록 축약본이 아님을 유지한다.
  - A-4-1 종료 시점에 1차 smoke test를 실행한다.
  - cluster 수가 30개를 초과하면 granularity 기준이 잘못된 것으로 판정하고 A-4-1을 재작업한다.
  - 현 단계에서는 2단계 계층 구조를 도입하지 않는다.
- 완료 기준:
  - 1차 smoke test에서 cluster 배정률 80% 이상
  - 랜덤 샘플 50건 중 `cluster_misaligned` 비율 10% 이하
  - 랜덤 샘플 50건 중 `too_generic_use` 비율 10% 이하
  - 세 조건을 모두 통과해야 A-4-2로 진행한다.
  - 배정률 90% 이상은 운영 목표로 추적하되, 단독 게이트로 사용하지 않는다.
- 기간: +2일
- 의존: A-4-0

### A-4-2. Cluster -> 3-3 요약문 매핑

- 목표: cluster를 3-3용 대표 용도 문장 템플릿으로 변환한다.
- 산출물: `cluster_summary_templates.json`, `cluster_abstraction_floor.md`
- 작업:
  - 각 cluster마다 대표 요약문 템플릿을 정의한다.
  - 추상도 하한선을 별도 문서로 명시한다.
  - 최소 허용 골격을 아래 3개로 고정한다.
  - `~작업에서 ~할 때 쓴다`
  - `~에 쓰는 도구/부품/재료다`
  - `~작업에 들어가는 ~다`
  - 세 골격 중 어느 것이든 반드시 게임 내 작업 맥락을 포함해야 한다.
  - `아이템을 제작할 때 쓴다`처럼 작업 맥락이 빠진 문장은 골격과 무관하게 금지한다.
  - 너무 일반적인 표현, 목록 구조 차용, 레시피식 열거를 금지 패턴으로 분리한다.
- 완료 기준:
  - cluster 요약문이 item-centric 3-3 본문에 들어가도 3-4의 listification으로 읽히지 않는다.
  - `cluster_abstraction_floor.md`만으로 validator 금지 패턴을 구현할 수 있다.
  - 판정은 `3_3_vs_4_boundary_examples.md`의 허용/금지 예시와 대조해 수행한다.
  - 요약문 템플릿을 예시 아이템에 적용한 결과가 금지 예시 패턴에 해당하지 않아야 한다.
- 기간: +1일
- 의존: A-4-1

### A-4-3. 대표 Cluster 선택 규칙

- 목표: 다중 소속 아이템에서 대표 cluster 1개를 안정적으로 고른다.
- 산출물: `cluster_selection_rules.md`
- 작업:
  - 선택 순서를 `전용 우선 -> 빈도 우선 -> 특수성 우선 -> 수동 override`로 고정한다.
  - 특수성 판정은 `cluster에 속한 고유 아이템 수가 적을수록 더 좁다`로 조작적 정의를 둔다.
  - role 동률 시 `tool -> material -> output`을 **provisional tie-breaker**로 사용한다.
  - tie-breaker 적용 아이템은 Phase C pilot에서 별도 추적한다.
  - pilot 결과를 바탕으로 freeze 또는 수정 판정을 내린다.
  - override 진입 조건을 모호성 남용이 아니라 계산 불가 case로 제한한다.
- 완료 기준:
  - 같은 입력에서 항상 같은 대표 cluster가 선택된다.
  - 다중 소속 edge case를 규칙 문서만으로 재현 설명할 수 있다.
  - role 동률 규칙이 provisional임이 문서에 명시되어 있다.
- 기간: +0.5일
- 의존: A-4-2

### A-4-4. 기존 A-4 규칙 수정 및 병합 규칙 통합

- 목표: cluster 요약을 기존 direct use / role fallback 경로와 충돌 없이 합친다.
- 산출물: `use_hint_generation_rules_v2.md`
- 작업:
  - source 우선순위를 기존 규칙 위에 다시 명문화한다.
  - direct use 보존 조건을 명시한다.
  - 병합 decision tree에 아래 4케이스를 고정한다.
  - `direct use 충분 -> 유지`
  - `direct use 추상적 -> cluster 요약으로 대체 또는 보강`
  - `role fallback 공허 -> cluster 요약 우선`
  - `cluster 없음 -> 기존 경로 유지`
- 완료 기준:
  - 기존에 이미 좋았던 direct use 문장이 cluster 도입 때문에 회귀하지 않는다.
  - cluster 요약이 들어갈 때도 3-3이 파밍 안내문이나 3-4 요약본으로 붕괴하지 않는다.
- 기간: +1일
- 의존: A-4-3

### A-7 수정. Validator / Gate 확장

- 목표: 새 경계와 추상도 규칙을 기계적으로 검문한다.
- 산출물: validator spec 수정, FAIL code 확장
- 작업:
  - V8: 범용 fallback 비율 `< 5%` soft ceiling
  - V9: 맥락어 존재 자동 검사는 PASS/FAIL이 아니라 WARN 등급으로 운영한다.
  - V9 WARN이 붙은 아이템은 수동 검토 우선순위 버킷에 자동 배정한다.
  - hard gate 판정은 V8과 구조적 FAIL 코드에 맡긴다.
  - V9의 맥락어 어휘 목록은 초기에는 보수적으로 두고, Phase C pilot 중 보강한다.
  - FAIL 코드 추가:
  - `too_generic_use`
  - `cluster_misaligned`
  - `borrowed_list_structure`
  - `role_fallback_too_hollow`
- 완료 기준:
  - cluster 도입 후 품질 저하가 수동 감으로만 발견되지 않는다.
  - 3-3/3-4 경계 위반을 validator가 먼저 잡는다.
  - V9는 triage용 WARN으로만 작동하고 hard fail을 발생시키지 않는다.
- 기간: +0.5일
- 의존: A-4-4

### B-3a. 자동 추출기 확장

- 목표: compose 입력 단계에서 cluster 판정과 merge decision tree를 함께 반영한다.
- 작업:
  - 4계층 근거에서 cluster 후보를 계산한다.
  - direct use 구체성 검사 후 보존/대체를 결정한다.
  - 대표 cluster와 대표 role을 compose input에 기록한다.
- 완료 기준:
  - cluster 경로가 compose 이전에 결정론적으로 계산된다.
  - 동일 입력 2회 실행 시 동일한 대표 cluster가 산출된다.
- 기간: 기존 B-3a +2일 범위 안에서 반영
- 의존: A-7

### B-3b. 커버리지 리포트 확장

- 목표: cluster 품질을 coverage 숫자로 추적 가능하게 만든다.
- 작업:
  - cluster 배정률
  - cluster 없음 비율
  - generic fallback 비율
  - direct use 보존율
  - cluster misalignment bucket
  - V9 WARN priority bucket
  - manual override 후보 집중 bucket
- 완료 기준:
  - smoke test와 rollout 보고서가 같은 지표 체계를 사용한다.
  - 회귀가 생기면 bucket 수준으로 역추적 가능하다.
- 기간: B-3 변경 범위 내
- 의존: B-3a

### B-3c. Cluster 보강 루프 및 수동 보충

- 목표: 리포트에서 드러난 구멍을 cluster/템플릿/선택 규칙 수준에서 메운다.
- 작업:
  - misaligned cluster 재조정
  - abstraction floor 위반 문장 재작성
  - assignment 누락 bucket 보강
  - 필요한 경우 최소 범위 manual override
- 완료 기준:
  - fallback 과다 구간이 구조적으로 설명된다.
  - 수동 보충은 cluster 설계 결함을 가리는 임시 패치가 아니어야 한다.
- 기간: B-3 변경 범위 내
- 의존: B-3b

### 기존 v4 Phase C 보강

- 별도 새 Phase 이름은 만들지 않고, cluster 검증 항목을 기존 v4 Phase C 하위에 삽입한다.
- `C-1 pilot`
  - 목표: 대표 실패 패턴을 작은 묶음에서 먼저 검증한다.
  - Pilot 묶음:
  - 묶음 1: 현재 추상도가 높은 아이템
  - 예: 금속 집개, 용접용 토치, 전자 부품, 조리 도구
  - 묶음 2: role fallback 과다 후보
  - 묶음 3: 4계층 풍부 / 3계층 빈약 아이템
  - 예: 총기 개조 부품, 탄약 제작 도구, 대장장이 도구
  - 측정 항목:
  - direct use 보존율
  - cluster assignment율
  - `cluster_misaligned`, `too_generic_use`, `borrowed_list_structure` 발생 분포
  - V9 WARN 분포
  - provisional tie-breaker 적용 아이템의 적합도
- `C-2 확대`
  - 목표: pilot 통과 기준을 더 넓은 bucket 집합에 적용한다.
  - 작업:
  - bucket 확장 적용
  - V9 WARN 어휘 목록 보강
  - direct use 보존율 추세 확인
- `C-3 full rebuild go/no-go`
  - 완료 기준:
  - 기존 good direct use가 불필요하게 교체되지 않는다.
  - item-centric 3-3 본문과 3-4 분리가 유지된다.
  - provisional tie-breaker의 freeze 또는 수정 판정이 기록된다.

### 기존 v4 Phase D 보강

- 별도 새 Phase 이름은 만들지 않고, cluster rollout 이후 확인 항목을 기존 v4 Phase D 하위에 삽입한다.
- `D-1 Lua bridge`
  - cluster 기반 3-3 산출물이 기존 bridge 경로에서 문제 없이 소비되는지 확인한다.
- `D-2 소비자 확인`
  - `IrisBrowser`, `IrisWikiPanel` 등 실제 소비자 표면에서 cluster 요약문이 3-4 listification처럼 보이지 않는지 확인한다.
- `D-3 인게임 검증`
  - full rollout
  - second-run determinism 확인
  - bucket별 hotspot 재점검
  - direct use 보존율 추세 확인
- 완료 기준:
  - G5 통과
  - 회귀가 cluster 품질 문제인지 merge 규칙 문제인지 분리 보고 가능

## 5. 게이트

| Gate | 기존 조건 | 추가 조건 |
|---|---|---|
| G1 Spec Freeze | 기존 유지 | `dvf_3_3_text_policy.md` 개정 완료, `interaction_clusters.json`, `cluster_summary_templates.json`, `cluster_selection_rules.md` 존재, A-4-2~A-4-4 반영 후 **최종 smoke test** 3중 조건 통과 (`배정률 >= 80%`, 50샘플 `cluster_misaligned <= 10%`, 50샘플 `too_generic_use <= 10%`) |
| G3 Data Ready | 기존 유지 | 범용 fallback 비율 5% 이하 soft ceiling, 초과 시 사유 분해 보고 |
| G5 Scale Pass | 기존 유지 | V8 hard validation 통과, V9 WARN 발생분이 priority bucket으로 분류되고 처리 기준이 기록됨 |

## 6. 일정 영향

| 구간 | 기존 v4 | 통합 후 | 증분 |
|---|---|---|---|
| Phase A | 6일 | 11.5~12.5일 | +5.5~6.5일 |
| Phase B | 8~16일 | 10~16일 | +2일 |
| Phase C/D | 변동 없음 | 변동 없음 | 0 |
| 합계 | 22~32일 | 29.5~38.5일 | +7.5~8.5일 |

Phase A 총 일정은 기존 A-1~A-7 6영업일과 A-4-0~A-4-4/A-7 수정 5.5~6.5영업일을 **순차 합산한 값**이다. 병행 작업은 가정하지 않는다.

추가 일정의 주된 원인은 A-4-0 정책 재정의와 A-4-4 병합 규칙 보강이다. 다만 이 투자는 B-3c 수동 보충량을 줄이는 쪽으로 회수될 가능성이 높다.

## 7. 의존 구조

```text
A-4-0 정책 재정의
 -> A-4-1 cluster 정의
    -> A-4-2 cluster 요약문 매핑
       -> A-4-3 대표 cluster 선택 규칙
          -> A-4-4 병합 규칙 통합
             -> A-7 validator 확장
                -> B-3a 자동 추출기 확장
                   -> B-3b 커버리지 리포트 확장
                      -> B-3c cluster 보강 루프
                         -> 기존 v4 Phase C 보강
                            -> 기존 v4 Phase D 보강
```

## 8. 최대 리스크와 대응

### 리스크 1. cluster 정의 품질 저하

- 본질: A-4-1 quality가 전체 자동 커버리지를 결정한다.
- 대응:
  - A-4-1 종료 시 1차 smoke test를 실행한다.
  - 배정률 80% 미만, `cluster_misaligned` 샘플율 10% 초과, `too_generic_use` 샘플율 10% 초과 중 하나라도 발생하면 다음 단계로 넘기지 않는다.
  - cluster 수 30개 초과 시 A-4-1을 재작업한다.
  - G1 freeze 직전에 최종 smoke test를 다시 실행한다.

### 리스크 2. merge 규칙 회귀

- 본질: 기존 direct use가 cluster 요약으로 불필요하게 교체될 수 있다.
- 대응:
  - A-4-4에 direct use 보존 조건을 강제한다.
  - Phase C에서 `기존 direct use 보존율`을 별도 지표로 측정한다.

### 리스크 3. 추상도 하한선 붕괴

- 본질: cluster 요약이 `도구`, `재료`, `다양한 작업에 쓰인다` 수준으로 비어 버릴 수 있다.
- 대응:
  - `cluster_abstraction_floor.md`를 별도 산출물로 둔다.
  - FAIL 코드 `too_generic_use`, `role_fallback_too_hollow`, `borrowed_list_structure`를 validator에 편입한다.

## 9. Kickoff Checklist

1. `dvf_3_3_text_policy.md` 개정 방향과 금지선 문구를 먼저 확정한다.
2. 허용/금지 경계 예시 10쌍 이상을 `3_3_vs_4_boundary_examples.md` 초안으로 만든다.
3. 4계층 데이터를 기준으로 cluster seed inventory를 만들고 초기 개수를 잡는다.
4. smoke test용 대표 bucket을 선별하고 배정률을 측정한다.
5. A-4-1 종료 시 1차 smoke test 3중 조건을 검사한다.
6. cluster summary template와 abstraction floor를 함께 잠근다.
7. representative cluster 선택 규칙과 merge decision tree를 문서화한다.
8. validator FAIL/WARN 확장을 구현한다.
9. B-3a/B-3b/B-3c에 cluster 지표와 보강 루프를 연결한다.
10. G1 freeze 직전에 최종 smoke test를 재실행한다.
11. 기존 v4 Phase C/D 하위에서 direct use 보존율과 3-3/3-4 경계 회귀를 검증한다.

## 10. 비목표

- 별도 11단계 독립 로드맵을 새로 운영하지 않는다.
- 3-3이 4계층의 레시피 목록, 재료 목록, 메뉴명, 조작 절차를 가져오게 하지 않는다.
- cluster를 approval backlog용 hotspot 관리와 동일한 개념으로 취급하지 않는다.
- cluster 수가 30개를 넘는다는 이유로 현 단계에 2단계 계층 구조를 도입하지 않는다.
- template 표면형 문제를 이유로 facts, candidate_state, approval 규약을 재오픈하지 않는다.

## 11. 종료 판정

이 실행계획의 종료 조건은 단순히 cluster 문서가 생기는 것이 아니다. 아래 세 조건을 모두 만족해야 한다.

- 3-3이 4계층의 대표 작업 맥락을 요약할 수 있다.
- 기존 good direct use 문장이 회귀하지 않는다.
- validator와 gate가 3-3/3-4 경계 위반과 추상도 붕괴를 자동으로 잡는다.
