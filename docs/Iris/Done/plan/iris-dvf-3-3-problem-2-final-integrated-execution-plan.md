# Iris DVF 3-3 Problem 2 Final Integrated Execution Plan

> 상태: draft v0.3  
> 기준일: 2026-04-06  
> 상위 기준: `docs/Philosophy.md`, `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`  
> 선행 문서: `docs/dvf_3_3_body_role_execution_plan.md`, `docs/iris-dvf-3-3-body-role-walkthrough.md`  
> 목적: body-role closeout 이후의 다음 round에서, active 내부에 semantic quality feedback loop를 구축하고 조건 충족 시에만 active 의미 재정의를 판단한다.

> 이 문서는 상위 문서의 하위 운영 계획 문서다. 상위 문서와 충돌 시 상위 문서가 우선한다.

---

## 0. 출발점 동결

이번 round의 출발점은 다음 문장으로 고정한다.

> 현재 `active`는 quality-pass가 아니라 runtime-adopted 상태다.

이 문장은 현재 baseline과 기존 status model 결정을 함께 읽은 결과다.

- current runtime baseline: `2105 rows / active 2084 / silent 21`
- active origin 분포: `cluster_summary 1440 / identity_fallback 617 / role_fallback 48`

따라서 이번 round는 active/silent 외부 계약을 곧바로 재정의하는 작업이 아니다. 먼저 active 내부의 semantic quality를 실측하고, compose 소비와 feedback loop를 붙인 뒤, 그 결과가 충분할 때만 active 의미 재정의를 별도 조건부 phase로 연다.

### 공통 제약

- active/silent 외부 계약은 Phase D 이전까지 바꾸지 않는다.
- 신규 runtime 상태 축은 만들지 않는다.
- `no_ui_exposure` 계약은 이번 round에서 실행하지 않는다.
- facts 슬롯은 확장하지 않는다.
- Lua bridge 계약은 바꾸지 않는다.
- `semantic_quality`는 새 runtime 축이 아니라 기존 semantic axis의 데이터화로만 다룬다.

---

## 1. 이번 계획의 성격

이번 계획의 실질 목표는 **semantic axis에 행동 권한을 부여하는 것**이다. 다만 그 행동이 곧바로 active 재정의를 뜻하지는 않는다.

이번 round의 순서는 다음 네 phase로 압축한다.

- Phase A: 실측 + 정책 결정
- Phase B: 파이프라인 구현
- Phase C: 추적 + 피드백 루프
- Phase D: active 의미 재정의 판단

Phase D는 조건부다. A~C 완료와 수치 성숙이 확인되기 전에는 열지 않는다.

## 1-A. 현재 실행 스냅샷 (2026-04-06)

현재 구현 상태는 다음처럼 읽는다.

- Phase A 완료
  - `layer3_active_quality_summary.json`: `active 2084 / semantic strong 1316 / adequate 0 / weak 768`
  - `cross_analysis_generated_weak_vs_body_role.json`: 기존 `generated::weak 133`과 body-role 교차 분석 완료
- Phase B 완료
  - overlay의 `semantic_quality` 기록과 validator drift hard fail 동작 중
  - compose는 `strong + FUNCTION_NARROW` representative repair, `weak` 계열 requeue 태깅을 수행 중
- Phase C 완료
  - `quality baseline v1` 동결 완료
  - `quality_tracking_report.json`, `compose_requeue_candidates.jsonl` 자동 생성 중
- Phase D 부분 착수
  - `active_semantics_redefinition_simulation.json` 생성 완료
  - `phase_d_readiness_report.json` 기준 현재 gate 상태는 `baseline_v1_frozen = pass`, `quality_ratio_sustained = pass`, `runtime_regression_clear = pass`, `requeue_tolerability = pending_policy`, `lane_stability = pending_policy`

참조 artifact:

- `Iris/build/description/v2/staging/semantic_quality/phaseD/phase_d_readiness_report.json`
- `Iris/build/description/v2/staging/semantic_quality/phaseD/phase_d_gate_threshold_proposal.json`

위 threshold proposal은 **결정이 아니라 non-binding candidate** 이다. 현재 candidate 값은 다음처럼 둔다.

- requeue candidate ratio vs active `<= 0.10`
- lane loss ratio `<= 0.20`
- baseline count `< 10`인 small lane은 loss `0`

현재 수치에서는 Scenario C만 proposal lane rule을 통과하므로, 운영상 권고는 계속 `Phase D closed / Scenario C 유지`다.

### `DECISIONS.md` 반영 원칙

- execution plan 자체는 이 문서에서 관리한다.
- A-3 완료 전 `docs/DECISIONS.md`에는 계획이나 가설을 먼저 올리지 않는다.
- 예외는 이번 final review에서 선행 guardrail로 확정된 항목뿐이다.
  - 출발점 문장 동결
  - `FUNCTION_NARROW` precondition
- A-3의 **전체 매핑 규칙**은 A-3 완료 이후에만 `docs/DECISIONS.md`에 기록한다.

---

## 2. 현재 기준선

이번 계획이 참조하는 current authority는 second-pass closeout 이후 baseline이다.

- total rows: `2105`
- active: `2084`
- silent: `21`
- active origin:
  - `cluster_summary 1440`
  - `identity_fallback 617`
  - `role_fallback 48`

이 baseline은 다음을 뜻한다.

- `active`는 이미 runtime 소비 여부를 뜻한다.
- `identity_fallback 617`과 `role_fallback 48`이 active 안에 존재하므로, active를 곧바로 quality-pass로 읽으면 semantic quality와 runtime availability가 다시 섞인다.
- 이번 round의 첫 과제는 active 내부 품질 분포의 정량화다.

---

## 3. Phase 구조

| Phase | 초점 | 핵심 산출물 | 개방 조건 |
|---|---|---|---|
| A | active 내부 품질 실측과 매핑 정책 고정 | quality audit, cross analysis, mapping decision | 즉시 시작 |
| B | `semantic_quality`를 decisions/compose에 연결 | decisions overlay, compose 분기 | Phase A gate 통과 |
| C | 품질 추적, 재큐잉, baseline 동결 | tracking report, requeue list, agenda note | Phase B gate 통과 |
| D | active 의미 재정의 시뮬레이션과 결정 | simulation, staged decision | Phase C 조건 충족 시에만 |

---

## 4. Phase A. 실측 + 정책 결정

## A-1. active 내부 품질 분포 전수 실측

### 목적

active `2084` 전수에 대해 semantic quality와 body-role 상태를 같은 분모에서 읽는다.

### 측정 축

| 측정 축 | 허용값 |
|---|---|
| `semantic_quality` | `strong / adequate / weak` |
| `layer3_role_check` | `ADEQUATE / FUNCTION_NARROW / IDENTITY_ONLY / ACQ_DOMINANT` |
| `origin` | `cluster_summary / identity_fallback / role_fallback` |
| `requeue_reason` | `NEEDS_SOURCE_EXPANSION / NEEDS_CLUSTER_REDESIGN / NEEDS_COMPOSE_TUNING / NONE` |

여기서 A-1의 `requeue_reason`은 canonical 운영값이 아니라, audit 단계에서 분석자가 산출하는 **진단 예측값**이다. Phase C-2의 compose 운영값과 이름은 같지만 역할은 다르다.

### 권장 구현 경로

- script candidate: `Iris/build/description/v2/tools/build/report_layer3_active_quality_audit.py`
- output:
  - `Iris/build/description/v2/staging/semantic_quality/phaseA/layer3_active_quality_audit.jsonl`
  - `Iris/build/description/v2/staging/semantic_quality/phaseA/layer3_active_quality_summary.json`

### 핵심 질문

active `2084` 중 실제 quality-pass 가능한 row 수는 얼마인가.

## A-2. generated::weak와 body-role 교차 분석

### 목적

기존 status model의 `generated::weak 133`과 body-role 진단의 `FUNCTION_NARROW 48 + IDENTITY_ONLY 617`이 어떻게 겹치는지 확정한다.

### 산출물

- script candidate: `Iris/build/description/v2/tools/build/report_generated_weak_body_role_cross_analysis.py`
- output:
  - `Iris/build/description/v2/staging/semantic_quality/phaseA/cross_analysis_generated_weak_vs_body_role.json`

### 필수 판정

- 교집합 수치
- 차집합 수치
- 기존 5개 핵심 결정과의 충돌 여부
  - `충돌 없음`
  - 또는 구체 충돌 항목 목록

## A-3. `layer3_role_check -> semantic_quality` 매핑 규칙 고정

### 목적

body-role 신호를 semantic axis에 연결하되, 기존 semantic authority를 덮어쓰지 않도록 매핑 우선순위를 고정한다.

### 매핑 규칙

| `layer3_role_check` | `semantic_quality` 판정 |
|---|---|
| `ADEQUATE` | 기존 semantic 유지 |
| `FUNCTION_NARROW` | 기본 `weak`, 단 기존 semantic axis가 `strong`인 row는 `strong` 유지 |
| `IDENTITY_ONLY` | `weak` 확정 |
| `ACQ_DOMINANT` | `adequate` 유지 + compose repair 대상 |

### 우선순위 원칙

- 기존 semantic 판정이 authority다.
- body-role 매핑은 기존 semantic 판정이 없거나 `adequate`인 row만 재검토한다.
- 기존 `strong`은 body-role 이유만으로 내리지 않는다.
- `FUNCTION_NARROW`의 기본 판정 방식은 A-3 착수 전 `docs/DECISIONS.md`에 선행 guardrail로 기록한다.

### 실행 방식

- 최초 1회는 전수 수동 승인
- 이후 빌드부터는 overlay builder 자동 생성 + diff report 확인

### 문서 반영

- A-3 완료 후 `docs/DECISIONS.md`에 전체 매핑 규칙을 별도 항목으로 채택
- 기존 5개 핵심 결정과의 충돌 없음 확인 기록 포함

## Phase A 게이트

- [ ] active `2084` 전수 실측 완료
- [ ] `generated::weak 133` 교차 분석 수치 확정
- [ ] 매핑 규칙 `DECISIONS.md` 항목 작성 완료
- [ ] 기존 5개 핵심 결정과 충돌 없음 확인

---

## 5. Phase B. 파이프라인 구현

## B-1. decisions overlay에 `semantic_quality` 필드 추가

### 목적

기존 semantic axis를 별도 runtime 축으로 승격하지 않고, decisions에서 기계적으로 소비 가능한 필드로 만든다.

### 규칙

- field: `semantic_quality`
- 허용값: `strong / adequate / weak`
- rendered에는 올리지 않는다.
- runtime 소비자에 전달하지 않는다.
- active/silent를 바꾸지 않는다.
- `semantic_quality` overlay는 기존 semantic axis의 **derived/cache field** 이며, 독립 편집·수동 수정 대상이 아니다.
- authority drift가 감지되면 validator hard fail로 처리한다.

### 구현 후보

- 기존 확장: `Iris/build/description/v2/tools/build/build_layer3_role_check_overlay.py`
- 또는 별도 builder: `Iris/build/description/v2/tools/build/build_semantic_quality_overlay.py`

## B-2. compose가 `semantic_quality`를 소비하는 분기 추가

### 목적

semantic quality가 출력 차단이 아니라 repair/진단/재큐잉 입력으로 작동하게 만든다.

### compose 행동

| `semantic_quality` | compose 행동 |
|---|---|
| `strong` | 현행 경로 유지 |
| `adequate` | 현행 경로 유지, 필요 시 `ACQ_DOMINANT` 계열 repair 경로만 적용 |
| `weak` | 현행 출력 유지, `layer3_role_check`에 따라 repair/진단/재큐잉 분기 |

### `strong + FUNCTION_NARROW` 처리

- semantic strong은 유지한다.
- 다만 body-role 왜곡을 그냥 통과시키지 않고, representative focus repair는 적용한다.
- 즉, 강등은 하지 않되 representative slot을 전면에 두는 compose repair는 수행한다.

### `weak` 세부 조합별 처리

| 조합 | compose 행동 |
|---|---|
| `weak + IDENTITY_ONLY` | 현행 출력 유지 / `quality_flag = identity_only` / 재큐잉 등록 |
| `weak + FUNCTION_NARROW` | 현행 출력 유지 / `quality_flag = function_narrow` / 재큐잉 등록 / representative focus 복구 repair 우선 적용 |
| `weak + ACQ_DOMINANT` | 현행 출력 유지 / `quality_flag = acq_dominant_reordered` / compose 배치 순서 repair 적용 |

`FUNCTION_NARROW`와 `ACQ_DOMINANT`의 차이는 다음처럼 읽는다.

- `FUNCTION_NARROW`: 대표성 왜곡이므로 representative focus repair가 핵심이다.
- `ACQ_DOMINANT`: 배치 순서 문제이므로 acquisition/order repair가 핵심이다.

### 구현 원칙

- weak라도 출력을 막지 않는다.
- compose 외부 단계를 추가하지 않는다.
- runtime contract는 계속 유지한다.
- Phase B에서는 `compose_requeue_candidates.jsonl` 생성 **로직**만 구현한다. canonical 파일 경로와 운영 계약은 Phase C-2에서만 고정한다.

## Phase B 게이트

- [ ] `ADEQUATE + semantic::strong` row의 rendered SHA-256 변경 `0`
- [ ] introduced hard fail `0`
- [ ] compose 외부 단계 추가 없음
- [ ] decisions에 `semantic_quality` 전수 기록 확인

---

## 6. Phase C. 추적 + 피드백 루프

## C-1. 빌드별 품질 추적 리포트

### 목적

active 내부 semantic quality 분포를 빌드마다 자동 추적한다.

### 산출물

- script candidate: `Iris/build/description/v2/tools/build/report_quality_tracking.py`
- output:
  - `Iris/build/description/v2/staging/semantic_quality/phaseC/quality_tracking_report.json`

### 필수 필드

```text
total_rows
active_total
silent_count
semantic_strong / adequate / weak
semantic_weak_breakdown:
  identity_only / function_narrow / acq_dominant
quality_ratio = (strong + adequate) / active_total
total_quality_ratio = (strong + adequate) / total_rows
delta_from_previous
```

`quality_ratio`는 active 기준 핵심 추적 지표다. `total_quality_ratio`는 전체 `2105` 기준 참고 지표로만 사용한다.

## C-2. compose 재큐잉 메커니즘

### 목적

weak-active를 자동 재처리하지 않고, 다음 source/cluster/compose backlog 우선순위 입력으로 정리한다.

### 산출물

- `Iris/build/description/v2/staging/semantic_quality/phaseC/compose_requeue_candidates.jsonl`

이 파일의 canonical 위치는 위 경로 하나로 고정한다. Phase B는 이 파일을 쓰는 로직을 구현하고, Phase C부터 운영 artifact로 취급한다.

### 포함 필드

- `item_id`
- `layer3_role_check`
- `quality_flag`
- `requeue_reason`

여기서 C-2의 `requeue_reason`은 compose가 매 빌드 실제로 기록하는 **운영값**이다. A-1의 audit 예측값과 이름은 같지만, canonical authority는 C-2 artifact에 있다.

### `requeue_reason`

| 값 | 의미 |
|---|---|
| `NEEDS_SOURCE_EXPANSION` | facts 부족, compose repair 불가 |
| `NEEDS_CLUSTER_REDESIGN` | 기존 cluster 부적합 |
| `NEEDS_COMPOSE_TUNING` | facts는 충분하나 compose 배치 왜곡 |

### 운영 원칙

- 자동 수집만 수행한다.
- 자동 source 생성이나 cluster 재설계는 하지 않는다.
- 기존 `identity_fallback 617` expansion plan과 교차해 backlog 우선순위 입력으로만 사용한다.

## C-3. `no_ui_exposure` 재검토 의제 등록

### 목적

계약은 유지하되, 조건 성숙 시 어떤 질문을 다시 열어야 하는지 문서화한다.

### 산출물

- `docs/semantic_quality_ui_exposure_agenda.md`

### 포함 항목

- 어떤 `quality_ratio` 수준에서 UI 재검토를 열 것인가
- UI 노출 형태 후보
  - 표시기
  - 필터
  - weak 숨김
- 해석·권장·비교 금지와의 충돌 검토

### 규칙

- 이번 round에서 실행하지 않는다.
- `docs/DECISIONS.md`에는 `재검토 의제 등록, 실행은 별도 결정`으로만 남긴다.

## C-4. 회귀 검증 + quality baseline v1 동결

### 목적

semantic quality feedback loop의 첫 수치를 운영 기준선으로 고정한다.

### 확인 항목

- `ADEQUATE + semantic::strong` SHA-256 변경 `0`
- runtime smoke 회귀 없음
- `quality_tracking_report.json` 첫 값을 `quality baseline v1`으로 동결

## Phase C 게이트

- [ ] `quality_tracking_report.json` 자동 생성 확인
- [ ] `compose_requeue_candidates.jsonl` 포맷 검증
- [ ] `docs/semantic_quality_ui_exposure_agenda.md` 완성
- [ ] `quality baseline v1` 동결
- [ ] 회귀 항목 `0`

---

## 7. Phase D. active 의미 재정의 판단

Phase D는 A~C가 끝났다고 자동으로 열리지 않는다.

## D 개방 조건

다음 네 조건이 모두 충족되어야 한다.

1. Phase C의 `quality baseline v1`이 동결돼 있다.
2. `quality_ratio`가 최소 2회 연속 빌드에서 안정적이다.
3. `compose_requeue_candidates.jsonl` 규모가 충분히 줄어, active 재정의에 따른 coverage 손실이 감당 가능하다고 수치로 확인된다.
4. 주요 lane(`identity_fallback`, `role_fallback`, `multiuse tool`, `weapon/tool hybrid`)에서 급격한 coverage 손실이 없다.

조건 3과 4의 구체 수치는 Phase C 종료 후 `quality baseline v1` 동결 시점에 별도 결정으로 닫는다.

## D-1. active 재정의 시뮬레이션

### 목적

active 의미를 quality-pass로 바꿀 경우의 손실과 보수 시나리오를 수치로 비교한다.

### 산출물

- `Iris/build/description/v2/staging/semantic_quality/phaseD/active_semantics_redefinition_simulation.json`

### 비교 시나리오

| 시나리오 | 정의 | 리스크 |
|---|---|---|
| A | `active = semantic adequate 이상` | `identity_fallback 617` 대량 탈락 가능 |
| B | `active = adequate 이상 + body-role ADEQUATE` | coverage 손실 더 큼 |
| C | `active 유지, quality-pass 별도 추적` | 해결 속도는 느리지만 리스크 최소 |

### 필수 수치

- active 수
- silent 증가량
- lane 손실량

## D-2. weak-active 재개방 결정

### 목적

기존 `generated::weak 133`과 `identity_fallback 617`을 어떤 계약으로 다시 읽을지 명시적으로 닫는다.

### 선택지

- 결정 1: 현 계약 유지
  - quality-pass는 내부 추적만 수행
- 결정 2: active 의미 재정의
  - staged migration으로 진행

### staged migration 기본 순서

- Round 1: internal quality-pass 추적만
- Round 2: UI/validator 반영
- Round 3: active 의미 재정의

active 의미 재정의(결정 2)를 선택할 경우, 기존 2-stage status model closure(`docs/DECISIONS.md`, 2026-03-31)의 **명시적 재오픈 결정**이 선행되어야 하며, 이는 별도 `docs/DECISIONS.md` 항목으로 기록한다. Phase D 착수 자체가 이 재오픈 결정을 뜻하지는 않는다.

## Phase D가 열리지 않을 수 있음

Phase C 완료 후에도 조건이 충족되지 않으면 Phase D를 열지 않는다. 그 경우 이번 round의 종료 상태는 **active 내부 품질 추적과 피드백 루프가 작동하는 상태**다.

---

## 8. 실행 의존 관계

```text
A-1 실측 -> A-2 교차 분석 -> A-3 DECISIONS 항목
                                   |
                                   v
                             B-1 semantic_quality overlay
                                   |
                                   v
                             B-2 compose 소비/분기
                                   |
                                   v
                  C-1 tracking report <-> C-2 requeue mechanism
                                   |
                                   v
                        C-4 regression + baseline freeze
                                   |
                                   v
                     (조건 충족 시) D-1 simulation -> D-2 decision

C-3 agenda registration은 C-1 이후 독립 병행 가능
```

---

## 9. 이번 계획이 건드리지 않는 것

- active/silent 외부 계약
- 기존 5개 핵심 결정의 현행 운영 계약
- `no_ui_exposure` 실행
- facts 슬롯 확장
- Lua bridge 계약
- 신규 runtime 상태 축
- `identity_fallback 617`의 실제 source expansion 본실행

`identity_fallback 617`은 이번 계획에서 backlog 입력과 재큐잉 우선순위로만 연결한다.

---

## 10. 권장 수정 우선순위

| 우선순위 | 파일/경로 | 목적 |
|---|---|---|
| P0 | `docs/iris-dvf-3-3-problem-2-final-integrated-execution-plan.md` | 실행 계획 authority |
| P0 | `docs/DECISIONS.md` | 출발점 문장과 `FUNCTION_NARROW` precondition만 선행 guardrail로 기록 |
| P1 | `Iris/build/description/v2/tools/build/report_layer3_active_quality_audit.py` | Phase A 전수 실측 |
| P1 | `Iris/build/description/v2/tools/build/report_generated_weak_body_role_cross_analysis.py` | Phase A 교차 분석 |
| P1 | `docs/DECISIONS.md` | A-3 완료 후 전체 매핑 규칙과 충돌 없음 판정 기록 |
| P1 | `Iris/build/description/v2/tools/build/build_layer3_role_check_overlay.py` 또는 `build_semantic_quality_overlay.py` | Phase B overlay |
| P1 | `Iris/build/description/v2/tools/build/compose_layer3_text.py` | Phase B compose 소비 |
| P2 | `Iris/build/description/v2/tools/build/report_quality_tracking.py` | Phase C tracking |
| P2 | `docs/semantic_quality_ui_exposure_agenda.md` | Phase C agenda |

---

## 11. 성공 기준

## Phase A~C 완료 시

- decisions에 `semantic_quality` 필드가 있어 active 내 품질 분포를 매 빌드 수치로 볼 수 있다.
- compose가 `semantic_quality`에 따라 repair 또는 진단 태깅을 수행한다.
- `quality_tracking_report.json`이 매 빌드 자동 생성된다.
- `quality_ratio` 추이가 기록된다.
- 재큐잉 목록이 backlog expansion 우선순위 입력으로 연결된다.
- `no_ui_exposure` 재검토 의제가 문서로 정리된다.

## Phase D 완료 시

- active/silent의 의미를 runtime availability에서 semantic quality-pass로 재정의할지 여부가 수치 기반으로 닫힌다.
- 기존 5개 핵심 결정의 재처리 여부가 명시적 decision으로 기록된다.

## 한 줄 요약

이번 계획은 `"active가 품질을 뜻하지 않는다"`는 문제를, 먼저 **active 내부 품질 피드백 루프 구축**으로 다루고, 그 다음에만 **active 의미 재정의 여부를 조건부로 판단**하는 순서로 해결한다.
