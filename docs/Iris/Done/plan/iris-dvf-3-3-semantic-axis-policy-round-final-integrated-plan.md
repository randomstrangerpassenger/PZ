# Iris DVF 3-3 Semantic Axis Policy Round Final Integrated Plan

> 상태: FINAL v1.1  
> 기준일: 2026-04-19  
> 상위 기준: `docs/Philosophy.md`, `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`  
> 선행 문서: `docs/Iris/Done/dvf_3_3_body_role_execution_plan.md`, `docs/Iris/Done/quality_state_ownership_spec.md`, `docs/Iris/Done/semantic_quality_ui_exposure_agenda.md`, `docs/Iris/Done/iris-dvf-3-3-source-expansion-distribution-remeasurement-gate-final-integrated-execution-plan.md`  
> authority input: `Iris/build/description/v2/staging/source_expansion_distribution_remeasurement_gate/phase6_semantic_decision/semantic_decision_input_packet.json`, `Iris/build/description/v2/staging/source_expansion_distribution_remeasurement_gate/phase6_semantic_decision/semantic_decision_review.md`, `Iris/build/description/v2/staging/source_expansion_distribution_remeasurement_gate/phase6_semantic_decision/decisions_md_patch_proposal.md`, `Iris/build/description/v2/staging/source_expansion_distribution_remeasurement_gate/closeout/source_expansion_remeasurement_terminal_handoff.json`, `Iris/build/description/v2/staging/source_expansion_distribution_remeasurement_gate/closeout/source_expansion_remeasurement_terminal_status.json`, `Iris/build/description/v2/staging/semantic_quality/phaseE_contract_migration/quality_baseline_v4.json`, `Iris/build/description/v2/staging/body_role/phase4/body_role_lint_report.json`  
> 목적: `quality_baseline_v4 -> v5` 승계 여부와 weak signal의 semantic axis candidate 취급 여부를 별도 policy text authority round로 닫기 위한 SAPR(Semantic Axis Policy Round)의 scope, phase order, review protocol, canonical output contract를 고정한다.  
> 실행 상태: planning only. 이 round는 policy text authority만 생성하며 구현, same-build mutation, runtime/publish mutation을 소유하지 않는다.

> 이 문서는 `quality_state`를 직접 emit하지 않는다.  
> `quality/publish decision stage`의 single writer 지위는 이 round 전, 중, 후 모두 유지된다.

---

## 0. Round Identity와 Opening Baseline

### 0-1. Round identity

| 항목 | 값 |
|---|---|
| round 이름 | `Iris DVF 3-3 Semantic Axis Policy Round (SAPR)` |
| round 성격 | operating rule authority round |
| trigger | SDRG `round_exit_status = PASS` + `docs/ROADMAP.md`의 SDRG Next 두 질문 |
| 핵심 질문 | `quality_baseline_v4 -> v5` 승계 여부, weak signal의 semantic axis candidate 취급 여부 |
| canonical input | `phase6_semantic_decision/semantic_decision_input_packet.json` |
| canonical output | `docs/DECISIONS.md` 신규 항목, `docs/ARCHITECTURE.md`의 current semantic decision authority read point section 갱신, `docs/ROADMAP.md` 갱신 |

### 0-2. 한 문장 scope lock

> 이번 round는 "weak signal을 semantic axis 후보로 다룰 것인가, 그리고 `quality_baseline_v4`를 `v5`로 승계할 것인가"만 결정한다.

### 0-3. Current opening snapshot

| 항목 | 현재 상태 |
|---|---|
| SDRG closeout | `round_exit_status = PASS` |
| current handoff branch | `maintain_identity_fallback_isolation_confirmed` |
| semantic decision packet | present |
| semantic decision review | present |
| prior `DECISIONS.md` patch proposal | present |
| `quality_state_ownership_spec.md` supporting reference | present |

### 0-3-b. Phase 3 entry mode determination

현재 workspace 기준으로 `phase6_semantic_decision/decisions_md_patch_proposal.md`가 존재하므로, 기본 진입 모드는 `expansion mode` 후보다.

단, `expansion mode`는 아래 admissibility를 통과할 때만 확정한다.

- prior patch proposal이 현 round Non-goals와 충돌하지 않을 것
- proposal이 `sapr_input_freeze.json`과 수치 정합성을 유지할 것

위 조건을 통과하지 못하면 prior patch file이 존재해도 `zero-base mode`로 강등한다.

### 0-4. Staging root

이번 round의 provenance artifact root는 아래로 고정한다.

- `Iris/build/description/v2/staging/semantic_axis_policy_round/`

권장 하위 디렉터리:

- `phase0_input_freeze/`
- `phase1_scoping/`
- `phase2_diagnostic/`
- `phase3_options/`
- `phase4_selection/`
- `phase5_patch_draft/`
- `phase6_consistency_review/`
- `closeout/`
- `handoff/`

---

## 1. 전역 봉인선

### 1-1. Single writer 재확인

- 이 round는 `quality_state` 값을 직접 emit하지 않는다.
- semantic axis carry가 필요하더라도 `quality/publish decision stage`를 단일 writer로 유지한다.
- validator, overlay builder, compose, Lua bridge, Browser/Wiki는 writer가 아니다.

### 1-2. Non-goals

아래는 모든 phase에서 재개방 금지다.

- three-axis contract 재정의
- `runtime_state` 의미 변경
- `quality_state` 허용값 확장
- compose 외부 repair 재도입
- UI exposure 판단 재개방
- facts 슬롯 확장
- `identity_fallback`, `bucket_3_scope_hold`, `bucket_2 599` lane reopen
- SDRG 재개방 또는 retroactive backfill 범위 확장
- `layer3_role_check -> semantic_quality` 기본 매핑 재개방
- body-role round의 `LAYER4_ABSORPTION` hard block 경계 재개방
- same-build re-compose 또는 신규 상태 축 도입
- `active`를 quality-pass로 재정의하는 것

### 1-3. 철학 guardrail

- `Philosophy.md`의 금지선인 해석, 권장, 비교는 policy reasoning의 근거로 쓰지 않는다.
- selection text는 `forward justification`과 `backward consistency`만 사용한다.
- semantic weak candidate는 user-facing meaning이 아니라 operating rule input으로만 다룬다.

---

## 2. Phase 0 — Input Consolidation & Scope Freeze

**목적:** scope와 input snapshot을 함께 봉인해 이후 phase가 다른 기준을 읽지 못하게 한다.

### 2-1. 해야 할 일

- scope를 0-2의 한 문장으로 다시 기록한다.
- `decisions_md_patch_proposal.md` 존재 여부를 freeze snapshot에 명시한다.
- 아래 canonical input을 inventory로 고정한다.
  - `semantic_decision_input_packet.json`
  - `semantic_decision_review.md`
  - `decisions_md_patch_proposal.md`
  - `quality_baseline_v4.json`
  - `source_expansion_remeasurement_terminal_handoff.json`
  - `source_expansion_remeasurement_terminal_status.json`
  - `body_role_lint_report.json`
- preamble supporting reference의 실재 여부를 함께 고정한다.
  - `docs/Iris/Done/quality_state_ownership_spec.md`
- 아래 baseline/current-state 수치를 `sapr_input_freeze.json`에 dual-layer read point로 동결한다.
  - `historical_comparison_baseline`
    - runtime row count `2105`
    - runtime path counts `cluster_summary 1440 / identity_fallback 617 / role_fallback 48`
  - `current_handoff_authority`
    - semantic strong / adequate / weak 분포
    - `quality_ratio`
    - `requeue_candidate_ratio`
    - runtime row count `2105`
    - runtime path counts `cluster_summary 2040 / identity_fallback 17 / role_fallback 48`
    - publish split `internal_only 617 / exposed 1467`
    - `LAYER4_ABSORPTION` 제외 signal-type 분포
- `all delta reasoning in SAPR uses current_handoff_authority unless explicitly marked historical` 문장을 freeze snapshot에 함께 봉인한다.
- `LAYER4_ABSORPTION` 제외 signal-type 분포는 Phase 2 taxonomy 입력이며, hard-block family를 SAPR carry scope 밖에 둔 상태로 읽는다는 주석을 붙인다.

### 2-2. 산출물

- `phase0_input_freeze/sapr_input_freeze.json`
- `phase0_input_freeze/sapr_input_freeze.md`

### 2-3. Review gate

- Critical
  - canonical input inventory 누락
  - frozen 수치와 authority source 불일치
  - dual-layer baseline read point가 historical/current authority로 분리되지 않음
  - round scope가 두 질문 이상으로 확장됨
- Important
  - baseline/current-state 항목 일부 결락
- Minor
  - 표기 일관성

### 2-4. 종료 조건

- 이후 phase가 읽을 input이 하나의 snapshot에 고정된다.
- dual-layer baseline read point와 delta reasoning rule이 함께 고정된다.
- Phase 3 진입 모드가 `expansion mode` 또는 `zero-base mode`로 명시된다.

---

## 3. Phase 1 — Scoping Document

**목적:** 이 round가 무엇을 결정하고 무엇을 결정하지 않는지 문서로 봉인한다.

### 3-1. 해야 할 일

- Round identity table을 문서 본문에 포함한다.
- Non-goals 전체를 그대로 포함한다.
- agenda를 아래 다섯 질문으로 고정한다.
  - Q1. weak signal을 semantic axis candidate로 다루는가, backlog only로 두는가
  - Q2. promote 기준은 무엇인가
  - Q3. promote 경로가 필요한가, 필요하다면 single-writer 안에서 어디인가
  - Q4. `quality_baseline_v4 -> v5` 승계 조건은 무엇인가
  - Q5. retroactive 범위는 어디까지 다시 봉인하는가
- review rule을 `PASS가 나올 때까지 반복, circuit breaker 없음`으로 적는다.

### 3-2. 산출물

- `phase1_scoping/sapr_scoping_v0_1.md`

### 3-3. Review gate

- Critical
  - Non-goals 침범
  - agenda가 이미 봉인된 결정을 다시 여는 형태로 작성됨
- Important
  - Q1-Q5 누락 또는 중복
  - input inventory 언급 누락
- Minor
  - 용어 정합성

### 3-4. 종료 조건

- review `PASS`
- Non-goals 해석 여지가 좁게 봉인된다.

---

## 4. Phase 2 — Current-State Diagnostic + Weak Signal Taxonomy

**목적:** existing output을 policy-decision input으로 재구성하고 weak를 결정 가능한 family 단위로 분해한다.

### 4-1. Weak taxonomy 고정

weak는 아래 5군으로 분리한다.

| 분류 | 포함 signal | 이번 round에서의 상태 |
|---|---|---|
| body-role mapping weak | `FUNCTION_NARROW`, `IDENTITY_ONLY` | mapping closure sealed; carry default `KEEP_OBSERVER_ONLY` |
| adequate 유지군 | `ACQ_DOMINANT` | 이번 round 대상 아님 |
| structural feedback weak candidate | `BODY_LACKS_ITEM_SPECIFIC_USE`, `SINGLE_FUNCTION_LOCK` | 결정 대상 |
| legacy/generated weak | `generated::weak 133` 계열 | sealed legacy weak reference; remapping reopen 금지 |
| source-expansion 이후 신규 weak | SDRG 이후 추가 weak | 결정 대상 |

여기서 `mapping closure sealed`는 `layer3_role_check -> semantic_quality` 매핑 관점의 closure만 뜻한다. axis carry closure는 SAPR 범위 안에 남아 있으며, 해당 family는 Phase 4 selection 전까지 기본적으로 `KEEP_OBSERVER_ONLY`로 전제한 뒤 필요 시 explicit carry만 재판정한다.

### 4-2. Diagnostic 원칙

- 수치는 `publish_state`와 runtime path 기준으로 cross-cut한다.
- overlap row count를 별도로 센다.
- 해석, 권장, promote recommendation 문장은 넣지 않는다.
- 이 phase는 "무엇이 더 낫다"가 아니라 "정책이 닿는 범위가 어디인가"를 고정한다.

### 4-3. 산출물

- `phase2_diagnostic/semantic_weak_taxonomy.md`
- `phase2_diagnostic/sapr_current_state_diagnostic.json`
- `phase2_diagnostic/sapr_current_state_diagnostic.md`

### 4-4. Review gate

- Critical
  - frozen 수치와 diagnostic 수치 불일치
  - signal 분류 오류
  - 해석/권장 문장 삽입
- Important
  - overlap 처리 누락
  - family별 결정 대상 여부가 불명확
- Minor
  - 표기 정렬

### 4-5. 종료 조건

- review `PASS`
- weak 5개 군의 결정 대상 여부가 분리된다.
- option별 영향 row 범위가 수치로 고정된다.

---

## 5. Phase 3 — Admission Rule + Policy Option Enumeration

**목적:** 어떤 weak가 candidate 자격을 갖는지 admission rule로 먼저 봉인하고, 그 다음 정책 선택지를 망라한다.

### 5-1. Admission rule 4문

weak signal이 semantic axis candidate가 되려면 아래 4문을 모두 통과해야 한다.

1. auto update 금지
2. same-build mutation 금지
3. source-expansion 이후 재측정에서 재현성 확보
4. explicit `DECISIONS.md` 채택 이후에만 axis carry 허용

### 5-2. Option set

Phase 0 결과에 따라 아래처럼 진입한다.

- prior patch present -> `expansion mode`
- prior patch absent -> `zero-base mode`

최소 enumerate 대상은 아래 다섯 옵션이다.

| 옵션 | 요지 | writer path | baseline impact |
|---|---|---|---|
| A | explicit gated carry의 `KEEP_OBSERVER_ONLY` 인스턴스; 모든 weak family를 backlog observer로 유지 | 없음 | `v4 유지` |
| B | consecutive-build conditional promote | `alpha` | 조건부 `v5` |
| C | signal-type differential | `alpha` | 조건부 `v5` |
| D | manual batch promote | `beta` | 조건부 `v5` |
| E | hybrid(A + D) | `beta` | 조건부 `v5` |

모든 옵션은 아래 5필드를 동일하게 채운다.

- `policy_name`
- `scope`
- `writer_path`
- `sealed_constraint_check`
- `baseline_impact`

주석:

- Option A는 ungated backlog-only가 아니라, carry matrix에서 모든 family를 `KEEP_OBSERVER_ONLY`로 닫는 explicit gated carry 인스턴스다.
- Option B/C의 consecutive-build observation은 candidate admission의 선행 관측 조건일 뿐이다. 실제 semantic axis carry는 admission rule 4의 explicit decision 경로로만 일어난다.
- Option B/C/D/E의 `baseline_impact`는 family 단위 carry matrix 결과에 따라 확정된다. 최소 한 family라도 `CARRY_TO_BASELINE_V5`로 닫히면 `v5` cutover가 필요하고, 그 외에는 `v4`를 유지한다.

### 5-3. D/E 특수 경계

- `semantic_quality_override`가 decision stage input인지 writer인지 경계를 문장으로 명시해야 한다.
- 이 경계 문장이 없으면 single-writer 위반으로 Critical FAIL이다.

### 5-4. 산출물

- `phase3_options/semantic_axis_candidate_admission_rule.md`
- `phase3_options/sapr_policy_options_enumeration.md`

### 5-5. Review gate

- Critical
  - admission rule 4문 중 하나라도 누락
  - Option A-E 누락
  - single-writer 위반 옵션이 무표기로 섞임
  - Non-goals 침범
- Important
  - 옵션 간 경계 중복
  - `baseline_impact` 누락
  - 2026-04-05 봉인과 충돌 미검출
- Minor
  - 용어 표기

### 5-6. 종료 조건

- review `PASS`
- admission rule 4문이 봉인된다.
- option set이 주요 policy branch를 망라한다.

---

## 6. Phase 4 — Carry Policy & Option Selection

**목적:** carry policy의 허용 경로를 먼저 닫고, 그 위에서 정책 옵션 하나를 선정한다.

### 6-1. Carry policy 허용 구조

이 round는 carry policy layer에서 세 가지 운영 모드를 구분한다.

- `ungated backlog-only`: 채택 불가
- `auto-reflect`: 채택 불가
- `explicit gated carry`: 채택 가능

여기서 채택 불가 대상인 `ungated backlog-only`는 carry matrix 자체를 결어놓고 weak를 backlog로만 방치하는 운영 방식이다. Phase 3의 Option A는 이 경로가 아니라, explicit gated carry 아래에서 모든 family를 `KEEP_OBSERVER_ONLY`로 닫는 인스턴스다.

### 6-2. Weak family carry 상태

각 weak family는 아래 셋 중 하나로만 판정한다.

- `KEEP_OBSERVER_ONLY`
- `ADMIT_AS_AXIS_CANDIDATE`
- `CARRY_TO_BASELINE_V5`

운영 의미는 아래처럼 고정한다.

- `KEEP_OBSERVER_ONLY`: semantic axis 무변경, baseline `v4` 유지
- `ADMIT_AS_AXIS_CANDIDATE`: candidate 자격만 인정, 실제 axis 반영은 별도 explicit decision 필요, baseline `v4` 유지
- `CARRY_TO_BASELINE_V5`: 실제 semantic axis 반영 승인, baseline `v5` cutover 필요

### 6-3. Option selection 문서 규칙

선정 텍스트는 아래 두 축만 허용한다.

- `forward justification`
- `backward consistency`

금지:

- UX 해석
- 권장 문장
- 의미 비교

Q1-Q5에 모두 명시 응답해야 하며, 특히 아래 두 항목을 빠뜨리면 안 된다.

- `quality_baseline_v4 -> v5` 승계 여부와 조건
- retroactive 범위 재봉인

### 6-4. 산출물

- `phase4_selection/baseline_carry_policy.md`
- `phase4_selection/semantic_weak_carry_matrix.json`
- `phase4_selection/sapr_policy_selection.md`

### 6-5. Review gate

- Critical
  - Q1-Q5 중 하나라도 미응답
  - single-writer 침해
  - Philosophy 금지선 위반
  - carry rule이 3상태 밖의 경로를 허용
- Important
  - 기존 결정과 정합하지 않는 선정 근거
  - carry matrix family 누락
- Minor
  - 용어 정합성

### 6-6. 종료 조건

- review `PASS`
- 선정안이 단일 정책 명제로 고정된다.
- weak family별 carry 상태가 matrix로 봉인된다.

---

## 7. Phase 5 — Decision Text Drafting

**목적:** 선정안을 canonical 3문서 patch draft로 정리한다.

### 7-1. `DECISIONS.md` 신규 항목 구조

- `상태: 채택`
- `결정`
- `추가 결정`
- `이유`
- `영향`

### 7-2. 반드시 들어가야 할 문장

- semantic weak candidate는 자동 반영되지 않는다.
- semantic axis 반영은 explicit decision으로만 닫는다.
- runtime/publish 계약은 이번 round에서 변경하지 않는다.
- `no_ui_exposure`는 유지한다.

### 7-3. 추가 patch draft

- `docs/ARCHITECTURE.md`의 current semantic decision authority read point section 갱신 문구
- `docs/ROADMAP.md` body-role addendum Next -> Done 이동 문구
- `docs/ROADMAP.md` SDRG Next 두 질문 resolved 문구

### 7-4. 산출물

- `phase5_patch_draft/sapr_decisions_patch_draft.md`
- `phase5_patch_draft/sapr_architecture_patch_draft.md`
- `phase5_patch_draft/sapr_roadmap_patch_draft.md`

### 7-5. Review gate

- Critical
  - 기존 항목과 직접 모순
  - 표준 포맷 위반
  - mandatory 4문장 누락
  - Option B/C/D/E인데 writer 경계 문장 누락
- Important
  - `추가 결정` 항목 누락
  - patch 적용 시 구조 파손 위험
- Minor
  - 날짜, 섹션 표기

### 7-6. 종료 조건

- review `PASS`
- 초안이 그대로 세 문서에 붙어도 구조가 깨지지 않는다.

---

## 8. Phase 6 — Forward / Backward Consistency Review

**목적:** 저자 기준 정합성이 아니라 downstream consumer 기준 정합성을 5개 시나리오로 검증한다.

### 8-1. 시나리오

1. next-build consumption
2. single-writer 지위 유지
3. validator drift-checker-only 지위 유지
4. publish_state 연쇄 영향 차단
5. gate threshold 영향

### 8-2. 통과 기준

- 어떤 consumer도 `quality_state` writer로 오인되면 안 된다.
- Option D/E면 `semantic_quality_override`의 경계를 시나리오 안에서 재확인해야 한다.
- `publish_state = internal_only`가 자동으로 `exposed`로 전환되는 경로가 생기면 Critical FAIL이다.
- `phase_d_gate_threshold_proposal` 재개방이 필요하면 별도 round 소관으로만 넘긴다.

### 8-3. 산출물

- `phase6_consistency_review/sapr_consistency_review.md`

### 8-4. Review gate

- Critical
  - 5개 시나리오 중 하나라도 봉인 위반 경로로 귀결
- Important
  - 판정 불가 시나리오 존재
- Minor
  - 흐름 기술 정확도

### 8-5. 종료 조건

- 5개 시나리오 모두 `PASS`
- consumer perspective review 전체 `PASS`

---

## 9. Phase 7 — Adoption & Closeout

**목적:** 선택된 policy text를 canonical 문서에 반영하고 round를 terminal state로 봉인한다.

### 9-1. 해야 할 일

- `docs/DECISIONS.md` 갱신
- `docs/ARCHITECTURE.md`의 current semantic decision authority read point section 갱신
- `docs/ROADMAP.md` 갱신
- `closeout/sapr_closeout_report.md` 작성

### 9-2. Closeout report 필수 항목

- round 전체 resolved `Critical / Important / Minor` 총합
- reopen 허용 조건 3개
  - source-expansion 이후 새 weak family 발생
  - UI 정책 변화로 weak를 exposed surface까지 끌고 가야 함
  - baseline drift 누적으로 `v5` 이후 재승계 필요
- reopen 금지 3개
  - 문장이 어색해 보여서
  - weak 수치가 보기 싫어서
  - `active`를 quality-pass처럼 보이게 하고 싶어서
- `immediate_next_round_planned = false`

### 9-3. 산출물

- 갱신된 `docs/DECISIONS.md`
- 갱신된 `docs/ARCHITECTURE.md`
- 갱신된 `docs/ROADMAP.md`
- `closeout/sapr_closeout_report.md`

### 9-4. Review gate

- Critical
  - patch draft와 실제 반영본 사이 diff 발생
  - 섹션 위치 오류
- Important
  - terminal 봉인 문구 누락
  - reopen 조건 누락
- Minor
  - 날짜, 버전 표기

### 9-5. 종료 조건

- canonical 3문서 갱신 완료
- round terminal 상태 기록 완료
- Option A면 여기서 종료

---

## 10. Phase 8 — Optional Implementation Handoff

**진입 조건:** Option A 이외로 닫혔을 때만 연다.

**목적:** SAPR decision text를 실제 pipeline 반영 round로 넘기는 별도 handoff를 정의한다. 이 문서 안에서 구현하지 않는다.

### 10-1. handoff scope

- `semantic_decision_input_packet.json`의 decision stage input schema 반영
- consecutive-build observation artifact 설계
- `semantic_quality_override` 필드 스키마 설계
- `quality_baseline_v5` cutover 절차 설계

### 10-2. 산출물

- `handoff/sapr_implementation_handoff.md`

### 10-3. Review gate

- Critical
  - SAPR decision text와 handoff scope 불일치
- Important
  - 새 round 시작 최소 input 목록 누락
- Minor
  - 표기

---

## 11. Phase Transition Rule

각 phase는 아래 두 조건이 모두 충족될 때만 다음으로 넘어간다.

1. 직전 phase deliverable이 모두 생성됨
2. 직전 phase review gate가 `PASS`

운영 규칙:

- `FAIL -> 수정 -> 재review`를 반복한다.
- circuit breaker는 없다.
- 같은 Critical이 반복되면 상위 phase로 자발 복귀할 수 있다.

---

## 12. Review Protocol

review 주체는 Claude이며, ㅇㅇ이 제출한 각 phase deliverable에 대해 아래 고정 형식으로 판정한다.

모든 phase review는 아래 고정 형식을 따른다.

1. `Good parts`
2. `Critical`
3. `Important`
4. `Minor`
5. `PASS / FAIL`

`sapr_closeout_report.md`는 round 전체 resolved count를 합산 기록한다.

---

## 13. Artifact Naming Convention

- planning/scoping: `sapr_*.md`
- snapshot/matrix: `sapr_*.json`
- taxonomy/rule 보조 문서: 설명형 고유 파일명 허용
- 위치: `Iris/build/description/v2/staging/semantic_axis_policy_round/`
- 기존 artifact는 read-only 참조만 허용
- canonical 3문서 반영 후에도 `sapr_*` 계열은 provenance로 보존한다

---

## 14. 성공 기준

### 14-1. 최소 성공

- round scope가 두 질문으로 끝까지 유지된다.
- single-writer 원칙이 Phase 0부터 Phase 7까지 깨지지 않는다.
- weak family가 observer / candidate / carry 상태로 구분된다.
- canonical output 3종이 모두 반영된다.

### 14-2. 좋은 성공

- Option selection이 기존 결정과 충돌 없이 닫힌다.
- `quality_baseline_v4 -> v5` 승계 조건이 숫자와 문장 모두로 명시된다.
- future reopen 조건이 governance 관점에서 좁게 봉인된다.

### 14-3. 실패

- SAPR가 implementation round처럼 행동한다.
- weak candidate를 same-build mutation으로 즉시 반영한다.
- `quality_state` writer가 둘 이상으로 읽히게 만든다.
- UI exposure, runtime adoption, source expansion reopen을 SAPR 안에 섞는다.

---

## 15. Read Map

```text
Phase 0  -> input freeze
Phase 1  -> scoping
Phase 2  -> weak taxonomy + current-state diagnostic
Phase 3  -> admission rule + option enumeration
Phase 4  -> carry policy + option selection
Phase 5  -> decision text patch drafting
Phase 6  -> forward/backward consistency review
Phase 7  -> adoption + closeout
Phase 8  -> optional implementation handoff
```

이 문서의 역할은 SAPR를 "지금 바로 구현하는 round"가 아니라, `DECISIONS.md / ARCHITECTURE.md / ROADMAP.md`를 동시에 갱신하는 policy authority round로 끝까지 유지하는 데 있다.
