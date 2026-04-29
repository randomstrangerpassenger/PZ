# Iris DVF 3-3 Three-Axis Contract Migration Execution Plan

> 상태: draft v0.2  
> 기준일: 2026-04-06  
> 상위 기준: `docs/Philosophy.md`, `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`  
> 선행 문서: `docs/iris-dvf-3-3-problem-2-final-integrated-execution-plan.md`, `docs/semantic_quality_ui_exposure_agenda.md`  
> 목적: problem 2 round에서 닫힌 internal semantic-quality feedback loop를 유지한 채, threshold adoption 이후에만 `runtime_state / quality_state / publish_state` 3축 계약으로 안전하게 이행한다.

> 이 문서는 상위 문서의 하위 운영 계획 문서다. 상위 문서와 충돌 시 상위 문서가 우선한다.

---

## 0. 이 문서의 위치

이 문서는 problem 2 round의 연장 구현 문서가 아니다. 현재 problem 2 round는 이미 다음 상태로 닫혀 있다.

- `active = runtime-adopted`, not `quality-pass`
- `semantic_quality`는 derived/cache field
- `Phase D = closed`
- `no_ui_exposure` 유지
- 추가 인게임 검증은 contract 변경 round에서만 다시 요구

따라서 이번 문서는 **future contract migration round** 를 여는 계획 문서로 읽는다. 핵심은 `semantic_quality`를 바로 UI로 올리거나 `active/silent`를 먼저 흔드는 것이 아니라, 먼저 threshold를 채택하고, 그 다음에만 3축 계약을 여는 것이다.

---

## 1. 현재 authority baseline

현재 출발점은 `quality baseline v1`과 `Phase D readiness` 산출물로 고정한다.

- total rows: `2105`
- active: `2084`
- silent: `21`
- semantic strong: `1316`
- semantic adequate: `0`
- semantic weak: `768`
- quality ratio: `0.6315`
- requeue: `624`
  - `identity_only 617`
  - `function_narrow 7`
- sustained gate: `pass`
- pending policy gate:
  - `requeue_tolerability`
  - `lane_stability`

현재 baseline이 뜻하는 바는 명확하다.

- current `active`는 quality-pass 집합이 아니다.
- 현재 구조는 이미 semantic quality를 추적, repair, requeue, readiness 판단까지 수행할 수 있다.
- 아직 없는 것은 threshold adoption과 contract change decision이다.

현재 authority artifact는 다음 네 묶음으로 본다.

- `Iris/build/description/v2/staging/semantic_quality/phaseC/quality_baseline_v1.json`
- `Iris/build/description/v2/staging/semantic_quality/phaseC/quality_tracking_report.json`
- `Iris/build/description/v2/staging/semantic_quality/phaseD/phase_d_readiness_report.json`
- `Iris/build/description/v2/staging/semantic_quality/phaseD/phase_d_gate_threshold_proposal.json`

---

## 2. 목표 구조

이번 round의 최종 목표 구조는 다음 3축이다.

- `runtime_state`
  - `active / silent`
  - 의미는 유지한다.
  - `active`는 runtime adopted만 뜻하고 quality-pass를 암시하지 않는다.
- `quality_state`
  - 이번 round에서 실제 허용값은 `strong / adequate / weak`
  - `fail`은 reserved 상태로만 두고, 이번 round에서는 emit하지 않는다.
  - 현재 `semantic_quality`를 **의도적 의미 재설계**를 거쳐 authoritative quality contract로 승격해 사용한다.
- `publish_state`
  - `internal_only / exposed / quality_exposed`
  - 초기 migration round에서는 `internal_only / exposed`만 실제 사용한다.
  - `quality_exposed`는 별도 future round로 미룬다.

운영 원칙은 다음처럼 고정한다.

- 2단 모델은 폐기하지 않고 운영 계약층으로 인정한다.
- 3축은 2단 모델 위에 덧씌우는 방식으로 전환한다.
- 모든 판단은 offline에서 결정론적으로 수행한다.
- runtime Lua는 판정하지 않고 렌더만 한다.
- compose와 `quality/publish decision stage`는 분리한다.
- `quality/publish decision stage`는 repair stage가 아니라 contract decision stage다.

추가로 이번 round는 `semantic_quality`의 **의미 재설계 round** 라는 점을 먼저 인정한다.

- 기존 `semantic_quality`: upstream semantic/body-role diagnostic
- 승격 이후 `quality_state` 또는 재정의된 `semantic_quality`: downstream publish decision을 구동하는 authoritative contract

즉, "새 field를 만들지 않는다"는 말은 의미 변화가 없다는 뜻이 아니다. 이번 round는 기존 필드의 역할을 의도적으로 다시 정의하는 작업이다.

---

## 3. 합헌 가드레일

`Philosophy.md` 기준으로 이번 migration round는 다음 금지선을 넘지 않아야 한다.

- 해석형 quality badge를 지금 도입하지 않는다.
- `semantic_quality`를 추천/비추천/비교 신호로 번역하지 않는다.
- `active/silent`를 quality 의미로 재정의하지 않는다.
- weak row를 runtime에서 즉시 숨기는 식의 조기 정책 실행을 하지 않는다.
- `quality/publish decision stage`와 compose를 합치지 않는다.

현 시점에서 합헌으로 읽을 수 있는 범위는 다음이다.

- `internal_only`: runtime artifact에는 있으나 기본 표면에 노출하지 않음
- `exposed`: 사실 그대로 노출
- `fact_origin` 같은 provenance 메타 노출
  - 단, quality surrogate/proxy로 읽히지 않게 쓸 때만 허용

현 시점에서 위헌 후보로 보는 범위는 다음이다.

- "품질이 낮음", "추천하지 않음", "덜 신뢰 가능" 같은 해석 문구
- quality_state 기반 ranking, sorting, 추천
- `fact_origin`을 fallback 품질 신호처럼 번역하는 것
- `quality_exposed`를 이번 round 안에서 함께 설계/집행하는 것

---

## 4. 전체 phase 구조

| Phase | 초점 | 개방 조건 | 종료 조건 | 주요 산출물 |
|---|---|---|---|---|
| 0 | 선행조건 정산 | 즉시 시작 | 현재 authority와 열린 이슈가 문서로 고정됨 | `phase_0_precondition_checklist.json` |
| 1 | threshold 채택 + 경로 선택 | Phase 0 종료 | threshold 2건과 A/B 실행 경로가 `DECISIONS.md`에 봉인됨 | `DECISIONS.md` 3건, `threshold_adoption_evidence.json` |
| 2 | source expansion / policy isolation 실행 | Phase 1 종료 | 선택된 경로 기준 Phase 3 입력 산출물 동결 | cluster 설계 문서, batch 결과, `quality_baseline_v2.json` 또는 `quality_baseline_v2_partial.json` |
| 3 | Phase D 재개방 판단 | Phase 2 종료 | path-aware 5-gate pass, migration scenario 채택 | `DECISIONS.md` 1건, `phase_d_opening_evidence.json` |
| 3A | Phase 4 진입 게이트 | Phase 3 pass | decision stage legality, single writer, bridge semantics, reserved state가 고정됨 | `DECISIONS.md` guardrail 항목, `phase4_entry_contract_guardrails.md` |
| 4 | 3축 계약 설계 | Phase 3A pass | 합헌 검사와 계약 명세 완료 | `quality_state_ownership_spec.md`, `publish_state_spec.md`, `lua_bridge_publish_state_contract.md`, `philosophy_constitutionality_check.md` |
| 5 | pipeline + Lua migration | Phase 4 종료 | offline/Lua/validator 계약 반영 + baseline v3 동결 | pipeline diff, Lua bridge 문서, validator 명세, `quality_baseline_v3.json` |
| 6 | in-game validation | Phase 5 종료 | contract migration validation pack pass | `in_game_validation_result.json` |
| 7 | closeout + 재봉인 | Phase 6 pass | `DECISIONS/ARCHITECTURE/ROADMAP` 재봉인 완료 | round closeout packet |

---

## 5. Phase 0 — 선행조건 정산

- 목적: 현재 닫힌 구조와 아직 열리지 않은 gate를 하나의 checklist로 고정한다.
- 입력:
  - `quality_baseline_v1.json`
  - `phase_d_readiness_report.json`
  - `phase_d_gate_threshold_proposal.json`
  - problem 2 closeout 관련 `DECISIONS.md`, `ARCHITECTURE.md`, `ROADMAP.md`
- 실행:
  - 현재 닫힌 것과 아직 미채택인 것 구분
  - contract change round가 별도 round라는 점 명시
  - Phase 1 이전에는 어떤 contract migration도 열리지 않음을 재확인
- 종료 조건:
  - 미결 이슈가 `requeue_tolerability`, `lane_stability`, `publish_state 축 부재`, `quality_state authoritative owner 부재`, `Phase 4 진입 전 contract guardrail 미채택`으로 정리됨
- 산출물:
  - `phase_0_precondition_checklist.json`

이 Phase는 구현 단계가 아니다. authority와 입력 조건을 다시 흔들지 못하게 만드는 문서화 단계다.

---

## 6. Phase 1 — Threshold 채택 + 경로 선택

- 목적: Phase D를 열기 위한 policy threshold 두 건을 실제 `DECISIONS.md` 항목으로 봉인한다.
- 핵심 원칙:
  - 이 Phase가 닫히기 전에는 3축 contract migration을 열지 않는다.
  - proposal artifact는 non-binding candidate일 뿐이며, 이 Phase에서만 binding decision으로 승격할 수 있다.

### 6-1. `requeue_tolerability` 채택

현재 `requeue 624` 중 `617`이 `identity_fallback`이므로, 실무상 권고는 **B안 우선 검토** 다.

- 권고 이유:
  - 현 requeue 대부분이 동일 성격 lane에 집중되어 있다.
  - 이 lane은 이후 `publish_state = internal_only` 초기 정책과 직접 연결된다.
  - 일반 weak backlog와 identity-fallback publish policy 문제를 같은 수치로 계속 읽으면, source expansion과 contract decision이 다시 섞인다.

이 Phase에서 닫아야 하는 것은 "정답"이 아니라 **binding interpretation** 이다.

- A안 채택 시:
  - source expansion을 먼저 강하게 요구하는 구조
  - quality ratio 개선이 직접 gate
- B안 채택 시:
  - identity_fallback lane을 별도 publish-policy lane으로 분리
  - non-identity requeue와 identity_fallback publish handling을 분리해 해석

### 6-2. `lane_stability` 채택

현재 proposal artifact의 candidate 값은 다음이다.

- lane loss ratio max: `0.20`
- baseline count `< 10` small lane은 loss `0`

실무상 권고는 **proposal 수치를 그대로 채택 후보의 출발점으로 삼는 것** 이다. 이유는 이미 simulation/readiness artifact가 이 기준으로 계산돼 있어, decision만 닫히면 곧바로 Phase 3 gate에 재사용할 수 있기 때문이다.

### 6-3. A/B 경로 선택

이 계획은 C-3에 대해 **Option 1** 을 채택한다. 즉, A안과 B안을 모두 합법적 실행 경로로 인정하되, threshold adoption 직후 현재 cycle에서 어느 경로를 탈지 `DECISIONS.md`에 별도 항목으로 봉인해야만 Phase 2로 진입할 수 있다.

- A-path
  - full expansion 우선 구조
  - full baseline v2 동결이 필요
- B-path
  - `identity_fallback` lane을 offline policy 레벨에서 `publish_state = internal_only` 예정 lane으로 격리
  - non-identity lane의 threshold 충족을 먼저 닫는 구조
  - 이 격리는 Phase 2/3의 gate 해석용 policy isolation일 뿐이며, Lua bridge/runtime consumer 구현 변경을 뜻하지 않는다.

### 6-4. 종료 조건

- `DECISIONS.md`에 threshold 2건이 채택 상태로 기록됨
- `DECISIONS.md`에 A/B 실행 경로가 추가로 봉인됨
- threshold 숫자, lane 분리 해석, path-dependent gate 해석이 binding rule로 고정됨
- `threshold_adoption_evidence.json`이 decision 근거를 묶음으로 남김

---

## 7. Phase 2 — Source Expansion / Policy Isolation 실행

- 목적: Phase 1에서 채택한 threshold를 통과할 수 있도록 source coverage를 실제로 확장한다.
- 개방 규칙:
  - A-path면 full expansion이 필수다.
  - B-path면 `identity_fallback` policy isolation과 non-identity expansion을 병행한다.

### 7-1. 실행 우선순위

A-path에서는 아래 순서를 full blocking path로 읽는다.

- `bucket_1` `11`건
  - 기존 cluster 재사용
  - 즉시 실행
- `bucket_2` `599`건
  - net-new cluster 설계
  - compose
  - rendered
  - regression
- `bucket_3` `7`건
  - 별도 residual 처리

B-path에서는 아래 순서를 읽는다.

- `identity_fallback` lane을 offline policy에서 `publish_state = internal_only` 예정 lane으로 격리
- `bucket_1` `11`건은 동일하게 즉시 실행
- non-identity lane과 `function_narrow` residual은 threshold 직접 개선 대상으로 우선 처리
- `bucket_2` `599`건 net-new cluster 설계는 계속 진행하되, policy isolation이 봉인된 뒤에는 current cycle의 Phase 3 개방을 막는 단일 절대 blocker로 읽지 않는다.

### 7-2. 종료 조건

A-path 종료 조건:

- expansion batch별 compose/regression 결과 확보
- lane별 분포 재측정 완료
- `quality_ratio`, `requeue`, lane stability를 full population 기준으로 재계산
- `quality_baseline_v2.json` 동결

B-path 종료 조건:

- `identity_fallback` lane policy isolation이 별도 artifact로 동결
- non-isolated lane의 compose/regression 결과 확보
- non-isolated lane 기준 partial baseline 재측정 완료
- `quality_baseline_v2_partial.json` 동결
- global full-population 수치는 참고용 delta로만 함께 남김

중요한 점은 B-path의 isolation이 **runtime contract 구현이 아니라 gate 해석용 policy designation** 이라는 점이다.

### 7-3. 산출물

- A-path
  - net-new cluster 설계 문서
  - expansion batch 실행 결과
  - `quality_baseline_v2.json`
  - threshold 대비 delta 비교 결과
- B-path
  - `identity_fallback_policy_isolation_report.json`
  - non-isolated lane expansion 결과
  - `quality_baseline_v2_partial.json`
  - global reference delta 비교 결과

이 Phase의 핵심은 threshold 달성에 필요한 만큼 backlog를 줄이는 것이지, expansion을 quality 해결책 일반론으로 무한 추구하는 것이 아니다.

---

## 8. Phase 3 — Phase D 재개방 판단

- 목적: threshold adoption과 baseline v2를 근거로 Phase D를 실제로 열지 판단한다.
- 평가 대상 5-gate:
  - `baseline_v2_frozen`
  - `quality_ratio_sustained`
  - `requeue_tolerability`
  - `lane_stability`
  - `runtime_regression_clear`

### 8-1. path-aware 5-gate 판정 규칙

A-path의 5-gate는 full population 기준으로 읽는다.

- `baseline_v2_frozen` = `quality_baseline_v2.json`
- `quality_ratio_sustained` = full active population 기준
- `requeue_tolerability` = full active population 기준
- `lane_stability` = 전체 active lane 기준
- `runtime_regression_clear` = full runtime artifact 기준

B-path의 5-gate는 다음처럼 재해석한다.

- `baseline_v2_frozen` = `quality_baseline_v2_partial.json` + `identity_fallback_policy_isolation_report.json`
- `quality_ratio_sustained` = `publish_state = exposed` 예정 population 기준
- `requeue_tolerability` = 같은 exposed 예정 population 기준
- `lane_stability` = non-isolated lane 기준으로 판정하되, `identity_fallback` lane은 isolation report에 명시적으로 남아 있어야 하며 silent loss처럼 사라지면 fail
- `runtime_regression_clear` = 경로와 무관하게 full runtime artifact 기준

즉, B-path는 `identity_fallback` lane을 조용히 잃어버리는 경로가 아니라, **정책적으로 격리한 뒤 나머지 노출 후보 표면을 먼저 닫는 경로** 다.

### 8-2. 회귀 규칙과 circuit breaker

- 5개 전부 pass면 Phase 3A로 진입
- 하나라도 fail이면 Phase 2로 회귀
- 모든 fail round는 `phase_d_reopen_iteration_report.json`에 gate별 delta를 남긴다.
- circuit breaker는 `N = 2`로 둔다.
- 동일한 blocking gate가 연속 2회 유지되고, 채택된 threshold precision 기준으로 material delta가 없으면 normal loop를 중단한다.
- 이 경우 round는 `Hold`로 전환하고, threshold 재검토 또는 path 재선택을 여는 별도 `DECISIONS.md` 항목을 먼저 연다.

### 8-3. 시나리오 채택과 기존 A/B/C 매핑

이 Phase에서 transition scenario도 함께 닫는다.

- 기존 Scenario A/B/C는 **Phase D 개방 전 comparative diagnostic scenario** 다.
- 새 Scenario X/Y는 **Phase D 개방 후 contract migration strategy** 다.

- Scenario X
  - runtime_state 유지
  - quality_state는 offline 판정
  - publish_state가 UI 노출 여부를 결정
  - active/silent 외부 계약은 건드리지 않음
  - 기존 Scenario C의 3축 발전형으로 읽는다.
- Scenario Y
  - identity_fallback lane에 `publish_state = internal_only`를 우선 적용
  - strong/adequate와 weak handling을 순차적으로 나눠 승격
  - 기존 Scenario B의 변형으로 읽는다.

Scenario A는 여전히 comparative failure case에 가깝고, current migration target으로 직접 승격하지 않는다.

실무상 권고는 **Scenario X** 다.

- 이유:
  - 현재 closure된 `runtime_state` 계약과 가장 적게 충돌한다.
  - `active = runtime adopted`를 유지한 채 3축 분리만 추가할 수 있다.
  - publish_state를 새 UI/Lua bridge contract의 유일한 consumer axis로 두기 쉽다.

### 8-4. Phase 4 진입 게이트

Phase 4에 들어가기 전, 별도 `DECISIONS.md` guardrail 항목과 `phase4_entry_contract_guardrails.md`로 다음을 선행 봉인한다.

- `compose 외부 repair 단계 금지`의 적용 범위를 재정의
  - repair/rewrite/lint fix stage는 계속 금지
  - `quality/publish decision stage`는 post-compose contract decision stage로만 허용
- `quality/publish decision stage` = `quality_state`의 single writer
- validator = drift checker only
  - 기록자 아님
  - quality_state/publish_state를 읽어 불일치를 감지하는 역할만 수행
- 이번 round의 `quality_state` 허용값은 `strong / adequate / weak`
  - `fail`은 reserved이고 emit 금지
- `semantic_quality` 승격은 diagnostic -> authoritative contract로 가는 의도적 의미 재설계임을 명시
- Lua bridge runtime semantics 고정
  - `internal_only` row도 bridge에서 row와 3-3 body와 `publish_state`를 함께 유지
  - Browser/Wiki consumer가 `publish_state`만 보고 렌더 여부를 분기
  - nil 처리나 row 제외는 허용하지 않음

이 게이트가 닫히기 전에는 Phase 4에 진입하지 않는다.

### 8-5. 산출물

- `DECISIONS.md` 항목: Phase D 개방 여부 + 채택 시나리오
- `phase_d_opening_evidence.json`

---

## 9. Phase 4 — 3축 계약 설계

- 목적: Phase 5 구현에 앞서 quality/publish 계약을 문서로 먼저 닫는다.

### 9-1. `quality_state` 설계

- 별도 새 필드를 만들지 않는다.
- 현재 `semantic_quality`의 소유권과 downstream contract를 재정의하는 방식으로 처리한다.
- 기존 `semantic_quality`의 역할은 upstream diagnostic이었다는 점을 문서 첫머리에 명시한다.
- 승격 이후의 `quality_state` 또는 재정의된 `semantic_quality`는 downstream publish decision을 구동하는 authoritative contract로 읽는다.
- 이 의미 변화는 accidental drift가 아니라 **의도적 재설계** 로 봉인한다.
- single writer는 `quality/publish decision stage` 하나뿐이다.
- validator는 drift checker only다.
- overlay builder는 source producer이지 최종 owner가 아니다.
- 이번 round의 허용값은 `strong / adequate / weak`만 사용한다.
- `fail`은 reserved 상태이며, 별도 round에서 정의되기 전에는 emit하지 않는다.

### 9-2. `publish_state` 설계

- `internal_only`
  - runtime artifact에 존재
  - 기본 user-facing surface에는 미노출
- `exposed`
  - 기본 표면 노출 허용
  - quality badge 없음
- `quality_exposed`
  - quality_state 메타를 동반한 노출
  - 이번 round에서는 구현/집행하지 않음

### 9-3. Lua bridge publish_state contract

- Lua bridge는 `internal_only / exposed`와 무관하게 row를 그대로 내린다.
- `internal_only` row도 3-3 body와 `publish_state`를 함께 bridge에 포함한다.
- nil 처리, field 제거, row 제외는 허용하지 않는다.
- Browser/Wiki consumer layer가 `publish_state`만 읽어 렌더 여부를 분기한다.
- 이 계약으로 runtime artifact와 UI surface를 끝까지 분리한다.

### 9-4. 합헌 검사

이 Phase에서 별도 문서로 다음을 닫는다.

- Section 3은 이 로드맵 전체에 적용되는 사전 가드레일이다.
- `philosophy_constitutionality_check.md`는 3축 계약 설계안에 대한 **구체적 합헌 판정문** 으로 작성한다.
- `internal_only`는 비노출 정책이므로 해석 문구를 만들지 않는다.
- `exposed`는 사실 노출이므로 합헌이다.
- quality badge나 value judgement 문구는 아직 금지다.
- `fact_origin`은 provenance 표기 only다.
  - quality surrogate
  - quality proxy
  - fallback 품질 신호
  - 추천/비추천 신호
  로 사용하면 위헌으로 처리한다.
- UI 문구에 품질 우열을 암시하는 표현이 들어가면 위헌이다.

### 9-5. 산출물

- `quality_state_ownership_spec.md`
- `publish_state_spec.md`
- `lua_bridge_publish_state_contract.md`
- `philosophy_constitutionality_check.md`

---

## 10. Phase 5 — Offline Pipeline + Lua Bridge Contract Migration

- 목적: Phase 4에서 닫은 계약을 실제 파이프라인과 runtime consumer에 반영한다.

### 10-1. `quality/publish decision stage` 반영

목표 파이프라인:

`facts -> decisions -> overlay -> compose -> quality/publish decision stage -> rendered + publish_decision`

책임 분해는 다음처럼 고정한다.

- compose
  - repair
  - reorder
  - requeue capture
- `quality/publish decision stage`
  - quality_state authoritative decision
  - publish_state authoritative decision
  - repair/rewrite 권한 없음

- validator
  - drift checker only
  - single writer 아님

중요한 점은 `수정은 했지만 exposed는 아님` 이 가능해야 한다는 것이다. 이 분리가 3축 구조의 핵심이다.

### 10-2. Lua Bridge + Consumer 확장

- `IrisLayer3Data.lua` 계열 bridge에 `publish_state` 추가
- `internal_only`와 `exposed` row를 모두 full row 형태로 공급
- Browser/Wiki consumer가 `publish_state`를 읽어 기본 surface 렌더 여부만 분기
- row 생략이나 3-3 field nil 처리는 금지
- runtime Lua는 quality 판정을 하지 않는다.

### 10-3. Validator 강화

- validator의 hard fail 범위는 offline ownership/bridge/state drift까지만 한정한다.
- Browser/Wiki consumer가 실제로 렌더를 잘못하는지는 validator가 아니라 Phase 6 in-game validation에서 검증한다.
- `quality_state`가 `quality/publish decision stage` 밖에서 기록되면 hard fail
- `runtime_state`와 `quality_state` drift hard fail
- `publish_state` drift hard fail
- `quality_state = fail`이 emit되면 hard fail
- `publish_state = exposed`인데 `quality_state` 미설정 hard fail
- `publish_state = internal_only`인데 bridge row 또는 3-3 body가 누락되면 hard fail

### 10-4. 종료 조건

- pipeline diff 완료
- Lua bridge contract 문서화 완료
- validator hard fail 규칙 반영
- baseline v3 동결

### 10-5. 산출물

- pipeline 변경 diff
- Lua bridge 계약 변경 문서
- validator 강화 명세
- `quality_baseline_v3.json`

---

## 11. Phase 6 — In-game Validation

- 목적: Lua bridge와 UI surface 계약 변경을 실제 소비자 기준으로 검증한다.
- 성격:
  - smoke test가 아니다
  - contract migration validation pack이다

검증 항목은 다음처럼 고정한다.

1. `publish_state = internal_only` row가 bridge/runtime artifact에는 존재하면서 browser/wiki 기본 표면에서는 사라지는가
2. `publish_state = exposed` row의 3-3 body가 정상 노출되는가
3. context menu tooltip 회귀가 없는가
4. 동일 아이템의 다른 layer에서 regression이 없는가
5. 추가 필드와 분기로 인한 성능 regression이 없는가

산출물:

- `in_game_validation_result.json`

이 Phase는 선택이 아니다. 현재 round는 build artifact 확장만이 아니라 runtime/Lua/UI contract migration을 포함하므로, manual in-game validation이 필수다.

---

## 12. Phase 7 — Closeout 및 재봉인

- 목적: migration 이후의 새 구조를 운영 계약으로 문서에 다시 봉인한다.

### 12-1. `DECISIONS.md`

최소 추가 항목:

- `runtime_state`: active는 runtime adopted만 뜻함
- `quality_state`: post-migration `semantic_quality`를 authoritative quality contract로 재정의
- `quality_state` single writer = `quality/publish decision stage`
- validator = drift checker only
- `quality_state fail`은 reserved
- `publish_state`: `internal_only / exposed` 채택
- `internal_only`도 bridge row는 유지하고 consumer만 비노출 처리
- `quality_exposed`는 future round
- `active`는 더 이상 quality-pass를 암시하지 않음
- identity_fallback 초기 publish policy

### 12-2. `ARCHITECTURE.md`

현재 `11-41`의 `internal semantic-quality feedback loop` 설명을 덮어쓰는 것이 아니라, 그 위에 3축 migration 이후 구조를 addendum으로 이어붙인다.

### 12-3. `ROADMAP.md`

- current Hold의 `no_ui_exposure 실행` 계열 서술은 migration 완료 기준으로 재배치
- `quality_exposed`는 새 Hold 또는 future round 항목으로 이동

### 12-4. 산출물

- `DECISIONS.md` 추가 항목
- `ARCHITECTURE.md` 갱신
- `ROADMAP.md` 갱신
- round closeout packet

---

## 13. 지금 당장 착수할 순서

이번 문서 기준 immediate critical path는 다음 다섯 단계다.

1. `phase_0_precondition_checklist.json` 초안 작성
2. `DECISIONS.md`용 threshold 채택 문안 2건 + A/B path 선택 문안 작성
3. `threshold_adoption_evidence.json` 작성
4. 선택된 path 기준 Phase 2 manifest 작성
5. `phase4_entry_contract_guardrails.md` 초안 작성

이 순서가 중요한 이유는, 현재 병목이 구현 부족이 아니라 threshold 미채택 상태이기 때문이다. Lua bridge나 UI를 먼저 건드리면 현재 closeout을 무효화하고 구조를 다시 섞게 된다.

---

## 14. 봉인 항목

이 문서가 유지되는 동안 다음 항목은 계속 금지한다.

- threshold 달성을 넘어서는 무제한 backlog expansion을 quality 해결책 일반론으로 추구하는 것
- `semantic_quality`를 UI badge로 직접 노출하는 것
- active/silent를 quality 의미로 재정의하는 것
- `quality_exposed`를 이번 round에서 함께 설계/집행하는 것
- compose와 `quality/publish decision stage`를 합치거나, 그 stage에 repair 권한을 주는 것
- threshold adoption 이전에 Phase D를 사실상 열어버리는 것

---

## 15. 최종 요약

이 migration round의 순서는 고정한다.

1. 현재 authority를 Phase 0 checklist로 고정한다.
2. threshold 2건과 A/B 실행 경로를 `DECISIONS.md`에서 먼저 닫는다.
3. 선택된 경로 기준으로 source expansion 또는 policy isolation을 수행해 baseline v2 입력을 만든다.
4. path-aware gate로 Phase D를 다시 열지 판단한다.
5. 통과 시 Phase 4 진입 게이트에서 single writer, bridge semantics, reserved state를 먼저 봉인한다.
6. 그 다음에만 3축 계약 명세를 닫고, 이후 pipeline/Lua migration을 수행한다.
7. contract migration이므로 인게임 validation을 필수로 수행한다.
8. 마지막에 `DECISIONS / ARCHITECTURE / ROADMAP`를 재봉인한다.

즉, 이번 계획의 본질은 "semantic_quality를 바로 보여주는 것"이 아니라, **이미 닫힌 internal feedback loop 위에서 threshold와 publish contract를 먼저 확정하고, 그 다음에만 runtime consumer contract를 안전하게 바꾸는 것** 이다.
