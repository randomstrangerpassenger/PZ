# Iris DVF 3-3 Surface Contract Authority Migration Execution Plan

> 상태: Draft v0.1  
> 기준일: 2026-04-07  
> 상위 기준: `docs/Philosophy.md`, `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`  
> 선행 문서: `docs/iris-dvf-3-3-style-normalization-execution-plan.md`, `docs/iris-dvf-3-3-role-violation-bridge-execution-plan.md`, `docs/quality_state_ownership_spec.md`, `docs/publish_state_spec.md`  
> 입력 기준: `DVF Style/Normalizer Authority 보강 — 통합 최종 로드맵` (2026-04-07)  
> 기준 코드 경로: `Iris/build/description/v2/`  
> 목적: 닫힌 runtime/bridge 계약을 재개방하지 않고, default surface에 어떤 row를 노출할지 결정하는 authority를 `quality/publish decision stage` 단일 write 경로 안에 명문화한다.

> 이 문서는 상위 문서의 하위 운영 계획 문서다. 상위 문서와 충돌 시 상위 문서가 우선한다.
> 또한 `docs/iris-dvf-3-3-role-violation-bridge-execution-plan.md`의 사전 설계를 계승하는 final integrated execution plan이다.

---

## 1. 실행 판정

이번 라운드는 **style normalization 강화 라운드**가 아니다.  
이번 라운드는 **surface contract authority migration round** 다.

이 문서의 핵심 판정은 아래 한 줄로 닫는다.

> 이번 작업의 정답은 style linter를 승격하는 것이 아니라,  
> 닫힌 compose/runtime 계약 위에서 structural contract signal을 분리하고,  
> 그 신호를 `quality/publish decision stage` 단일 writer 안에서만 `quality_state`와 `publish_state`에 반영하도록 설계하는 것이다.

따라서 이번 문서는 다음을 하지 않는다.

- style linter를 authoritative gate로 승격하지 않는다.
- second-pass를 재개하지 않는다.
- compose 외부 repair/rewrite를 재도입하지 않는다.
- runtime/bridge contract를 다시 열지 않는다.

반대로 이번 문서가 여는 것은 다음 하나다.

- **default surface exposure policy authority를 single-writer contract 안으로 이관하는 구조 설계와 실행 순서**

---

## 2. 기존 봉인 유지

이번 계획은 아래 봉인을 전부 유지한다.

- compose 외부 repair 금지
- `quality_state` / `publish_state` single writer 유지
- validator = drift checker only
- style linter advisory-only 유지
- `quality_state = fail` reserved 유지
- `Philosophy.md`가 유일한 헌법
- `publish_state`는 visibility contract이며 deletion contract가 아님
- `internal_only` row는 runtime artifact와 bridge row를 유지함
- manual override는 lexical/style rule 면제일 뿐, future surface contract gate 자동 면제 사유가 아님
- 새 runtime 상태 축(`surface_quality`, `runtime_only` 등) 도입 금지

---

## 3. 현재 authority baseline

현재 DVF 3-3 authority baseline은 이미 닫혀 있다.

- current runtime model
  - `runtime_state = active / silent`
  - `quality_state = strong / adequate / weak`
  - `publish_state = internal_only / exposed`
- current writer model
  - authoritative writer: `quality/publish decision stage`
  - non-writer: compose, style linter, validator, Lua bridge, runtime consumer
- current style model
  - style linter는 normalizer 뒤에서 실행된다
  - report만 생성하고 산출물을 바꾸지 않는다
- current runtime visibility model
  - `internal_only`는 bridge/runtime preservation + default Browser/Wiki suppression을 뜻한다
  - `identity_fallback 617`은 row deletion이 아니라 policy-isolation inventory다

현재 구조에서 남은 갭은 `quality/publish contract` 자체가 아니라, **role-violation 계열 structural signal이 style advisory 채널 안에 갇혀 decision stage authority로 들어가지 못한다는 점**이다.

즉, 현재 구조는 다음처럼 읽는다.

```text
facts
  -> decisions / body-role overlay seam
  -> compose(internal repair + requeue capture)
  -> normalizer
  -> style linter(advisory only)
  -> quality/publish decision stage(single writer)
  -> rendered + publish decision preview
  -> Lua bridge
  -> runtime consumer
```

이번 라운드의 직접 과제는 이 경로를 뒤엎는 것이 아니라, **style advisory와 structural contract signal을 분리한 뒤 single-writer stage에만 연결하는 새 input seam을 추가하는 것**이다.

---

## 4. 목표 구조

목표 구조는 아래처럼 고정한다.

```text
facts
  -> decisions / body-role overlay seam
  -> compose(internal repair + requeue capture)
  -> normalizer
  -> style linter (advisory sensor branch)
  -> structural audit (surface_contract_signal 생성)
  -> quality/publish decision stage (single writer)
  -> rendered + publish decision preview
  -> Lua bridge
  -> runtime consumer
```

핵심 권한 분리는 다음처럼 닫는다.

| 단계 | 역할 | writer 여부 |
|---|---|---|
| style linter | surface-style 관측 | non-writer |
| structural audit | structural contract signal 생성 | non-writer |
| quality/publish decision stage | `quality_state` / `publish_state` 기록 | single writer |
| validator | writer drift와 emitted contract inconsistency 검사 | non-writer |
| Lua bridge / runtime consumer | 이미 계산된 state 소비 | non-writer |

### 계획 산출물

- 문서
  - `docs/iris-dvf-3-3-surface-contract-authority-migration-execution-plan.md`
- 신규 artifact
  - `structural_audit_scope_inventory.json`
  - `surface_contract_signal.jsonl`
  - `structural_audit_dry_run_delta.json`
  - `quality_baseline_v4.json`
- 신규/변경 코드 경로
  - `Iris/build/description/v2/tools/build/layer3_structural_audit.py`
  - `Iris/build/description/v2/tools/build/report_quality_publish_decision_preview.py`
  - `Iris/build/description/v2/tools/build/validate_quality_publish_decision_preview.py`
  - pipeline entry / build wiring 경로
- 갱신 문서
  - `docs/quality_state_ownership_spec.md`
  - `docs/DECISIONS.md`
  - `docs/ARCHITECTURE.md`
  - `docs/ROADMAP.md`

### 신규 signal artifact 최소 스키마

`surface_contract_signal.jsonl`의 최소 필드는 아래처럼 고정한다.

- `item_id`
- `structural_verdict`
  - `clean | flag | hard_fail`
- `violation_type`
  - **Phase 1-1 감사 완료 후 최종 enum 확정**
  - current candidate:
    - `LAYER4_ABSORPTION`
    - `IDENTITY_ONLY`
    - `BODY_LACKS_ITEM_SPECIFIC_USE`
    - `FUNCTION_NARROW`
    - `ACQ_DOMINANT`
    - `none`
- `recommended_tier`
  - `hard_block_candidate | publish_isolation_candidate | advisory_only`
- `evidence`

설계 원칙은 다음과 같다.

- structural audit는 새 의미 해석을 만들지 않는다.
- 입력은 **compose 이후, rendered 생성 이전 단계의 pre-render contract candidate** 와 `decisions.jsonl`을 사용한다.
- 감지는 keyword blocking이 아니라 structural role encroachment 기준으로 한다.
- 이 artifact는 input-only다.
- `recommended_tier`는 처분 확정값이 아니라 **decision stage가 참고하는 추천 입력** 이다.
- `quality_state`와 `publish_state`는 오직 downstream single writer만 기록한다.

---

## 5. Work Breakdown

### Phase 0 — 라운드 성격 봉인

### 목적

이번 라운드를 `style 강화`, `미완성 구현 보강`, `post-compose repair 복귀`로 오독하지 못하게 상위 문서에 먼저 못 박는다.

### 작업

- `docs/DECISIONS.md`에 이번 라운드를 **surface contract authority migration**으로 정식 기록
- `style linter 승격`이 아님을 명시
- `post-compose repair 재도입`이 아님을 명시
- `현재 runtime 재오픈`이 아님을 명시
- `docs/ROADMAP.md`에 이번 라운드가 **닫힌 runtime/bridge 계약 위에서 surface exposure policy만 강화하는 round**임을 기록

### 산출물

- `docs/DECISIONS.md` 갱신본
- `docs/ROADMAP.md` 갱신본

### Gate

- 라운드 정체성이 문서 언어로 먼저 봉인된다.
- 팀 내에서 이번 라운드를 `style linter 강화`로 읽는 해석이 남지 않는다.

---

### Phase 1 — 재분류 근거 확보 및 권한 경계 명문화

### 목적

새 gate를 만들기 전에, 무엇이 `surface style 문제`이고 무엇이 `layer boundary contract violation`인지 경계를 문서로 고정한다.

### 1-1. 현재 감지 로직 분류 감사

현재 style linter 규칙군(`L-01`~`L-04` 계열 포함)을 아래 기준으로 재분류한다.

- `Philosophy.md` [5]의 역할 침범 금지와 직접 연결되면
  - style 문제가 아니라 `layer boundary contract violation` 후보
- 직접 연결되지 않으면
  - style linter advisory 잔류

분리 후보는 아래처럼 고정한다.

- 3-3 body가 3-1 또는 3-2의 구조적 역할을 대체하는 패턴
- `identity_fallback` 비해당 row에서 generic fallback pattern이 3-3 body에 재출현하는 패턴
- `LAYER4_ABSORPTION`

style linter에 남길 항목은 아래처럼 고정한다.

- 반복 명사
- 상투 표현
- discovery phrase residue
- family lexical anomaly
- 어미/톤/forbidden pattern 계열

애매한 항목은 원칙적으로 style linter 잔류로 닫는다.

### 1-2. surface contract gate owner 명문화

owner는 계속 하나다.

- owner
  - `quality/publish decision stage`

non-owner는 아래처럼 고정한다.

- style linter
- normalizer
- validator
- Lua bridge
- runtime consumer

`style_lint_report.json`은 계속 non-authoritative sensor로 확정한다.

### 1-3. 신호 분류표 확정

새 contract signal의 신호 등급은 아래 표로 고정한다.

| 등급 | 항목 | 처리 경로 |
|---|---|---|
| hard block candidate | `LAYER4_ABSORPTION`, 기존 구조 위반 | decision stage 기본 처리: `quality_state = weak` + `publish_state = internal_only` |
| publish isolation candidate | `IDENTITY_ONLY`, `BODY_LACKS_ITEM_SPECIFIC_USE`, unresolved `FUNCTION_NARROW`, unresolved `ACQ_DOMINANT` | `publish_state = internal_only` 후보. 단, current/future rollout guardrail 적용 |
| advisory-only | 반복 명사, 상투 표현, discovery phrase residue, family lexical anomaly | style lint 유지 |

### 1-4. false positive 허용선 정의

1차 rollout용 false positive 허용선은 이 phase에서 같이 고정한다.

- 1차 rollout 허용선
  - **수동 검수 표본 기준 false positive rate = 0**
- 수동 검수 표본 선정 기준
  - 대상 row가 50 이하이면 전수 검수
  - 50 초과이면 `max(50, 전체의 20%)`를 층화 추출
  - 층화 축:
    - `violation_type`
    - source lane
    - 경계 사례
- threshold 초과 시 처리 경로
  - structural audit 규칙 재조정
  - rollout 중단
  - baseline freeze 보류

### 1-5. 현행 파이프라인 실제 실행 순서 확인

`decisions`, `body-role overlay`, `compose`의 실제 코드상 실행 순서를 확인한다.

- `body-role overlay`가 별도 seam이면 다이어그램을 유지
- `decisions` 내부 로직이면 문서 다이어그램을 수정
- 목표 구조 다이어그램도 동일 기준으로 맞춘다

### 산출물

- `structural_audit_scope_inventory.json`
- `false_positive_threshold_definition.md`
- `pipeline_execution_order_check.md`
- `docs/quality_state_ownership_spec.md` 갱신본
- `docs/DECISIONS.md` 봉인 문구 초안
  - 역할 위반은 style 문제가 아니라 layer boundary contract violation이다

### Gate

- 재분류 경계선이 문서로 확정된다.
- 애매한 항목은 advisory에 남고, 명확한 것만 structural contract로 분리된다.
- `violation_type` enum이 Phase 1 감사 결과로 최종 확정된다.
- false positive 허용선과 초과 시 처리 경로가 문서로 봉인된다.
- 현행 파이프라인 실제 실행 순서가 확인된다.
- `Philosophy.md` 합헌 검증이 끝난다.

---

### Phase 2 — advisory lint와 contract signal 분리

### 목적

`style_lint_report.json`은 그대로 두고, `quality/publish decision stage`가 읽을 별도 structural input artifact를 추가한다.

### 2-1. `surface_contract_signal.jsonl` 설계

입력 소스는 아래처럼 고정한다.

- normalizer 이후 **pre-render contract candidate**
- `decisions.jsonl`

출력 필드는 4장 스키마를 따른다.

감지 원칙은 다음과 같다.

- pre-render contract candidate의 의미를 새로 해석하지 않는다.
- overlay/role/quality 신호를 structural pattern matching으로 정리한다.
- single-writer stage 앞에 들어가는 **input-only audit artifact** 로만 운용한다.
- `recommended_tier`는 recommendation이며, 최종 처분은 decision stage가 닫는다.

### 2-2. `layer3_structural_audit.py` 구현 설계

style linter에 있던 역할 위반 감지 로직은 신규 structural audit script로 이전한다.

- style linter에서 이전된 규칙은 deprecated 처리
- advisory-only 봉인은 그대로 유지
- deprecated 출처와 대체 signal을 문서화

### 2-3. decision stage 입력 확장 설계

채택안은 **B안** 으로 고정한다.

- `surface_contract_signal.jsonl`을 decision stage의 4번째 별도 입력으로 추가
- 기존 `active_quality_audit` 책임 범위를 건드리지 않는다
- contract seam을 분명하게 유지한다

### 산출물

- `layer3_structural_audit_spec.md`
- `surface_contract_signal.jsonl` 스키마 확정본
- decision stage 입력 확장 설계서

### Gate

- 새 input artifact가 기존 5개 봉인과 충돌하지 않는다.
- advisory lint와 structural contract signal이 명확히 분리된다.
- `Philosophy.md` 합헌 검증을 통과한다.

---

### Phase 3 — quality 경로와 publish 경로 분리 정책 확정

### 목적

enforcement를 한 축으로 뭉개지 않고, `quality_state`와 `publish_state`가 각자의 역할에 맞게 분리 작동하도록 정책을 먼저 고정한다.

### 3-1. quality_state 경로

quality 경로는 아래처럼 고정한다.

| structural verdict | quality 처리 |
|---|---|
| `hard_fail` | `quality_state = weak` 강제 |
| `flag` | 기존 `quality_state` 유지 + `structural_flag` preview/report-only meta 기록 |
| `clean` | 변화 없음 |

추가 불변 원칙:

- `quality_state = fail`은 계속 reserved다.
- `flag`는 same-build rewrite 신호가 아니라 next-build compose requeue 후보 메타다.
- `structural_flag`는 authoritative axis가 아니다.
- `structural_flag`는 emitted contract artifact, Lua bridge field, runtime consumer에 절대 포함되지 않는다.

### 3-2. publish_state 경로

publish 경로는 아래처럼 고정한다.

| recommended_tier | decision stage 기본 처리 |
|---|---|
| `hard_block_candidate` | 기본 `publish_state = internal_only` |
| `publish_isolation_candidate` | rollout lane이 열려 있고 current guardrail과 충돌하지 않을 때만 `publish_state = internal_only` |
| `advisory_only` | publish 영향 없음 |

`internal_only`의 의미는 그대로 유지한다.

- runtime artifact 보존
- bridge row 보존
- Browser/Wiki default surface만 suppression

기존 `identity_fallback 617` internal-only lane은 **합치지 않고 분리 유지** 한다.

decision stage의 override authority는 아래처럼 닫는다.

- `recommended_tier`는 어디까지나 추천 입력이다.
- decision stage가 최종 `publish_state`를 기록한다.
- 아래 경우 decision stage는 `recommended_tier`를 override하거나 보류할 수 있다.
  - current cycle guardrail로 아직 rollout이 열리지 않은 lane
  - existing `FUNCTION_NARROW` protected strong / direct execution guardrail과 충돌하는 경우
  - `ACQ_DOMINANT`처럼 source expansion 및 별도 decision 선행이 필요한 lane
- manual override provenance는 단독으로 exemption도, isolation 강제 사유도 아니다.

### 3-3. 세부 정책 결정

아래 네 가지를 이번 phase에서 확정한다.

- manual override 정책은 **A안** 으로 고정한다.
  - manual override row도 동일하게 structural audit 대상이다.
  - 필요 시 `publish_state = internal_only` 처분이 가능하다.
  - manual override provenance만으로 automatic exemption을 주지 않는다.
- `ACQ_DOMINANT`는 전면 blanket isolation 금지
- `ACQ_DOMINANT`는 compose reorder 이후 residual subset만 isolation 후보로 본다
- `LAYER4_ABSORPTION`은 이번 문서에서 **hard block candidate** 로 읽고, decision stage 기본 처리로 `quality_state = weak` + `publish_state = internal_only`를 같이 명시한다.

### 3-4. 3-way rollout 우선순위

전면 적용은 금지한다. rollout은 아래 순서로 끊는다.

#### 1차 rollout

- `IDENTITY_ONLY`
- 기존 `identity_fallback` explicit isolation lane 유지
- 명백한 `BODY_LACKS_ITEM_SPECIFIC_USE`
- 조치: `publish_state = internal_only`

#### 2차 rollout

- unresolved `FUNCTION_NARROW`는 future separate decision 완료 이후에만 2차 rollout 개방 가능
- 현 cycle에서는 direct execution lane 유지
- protected strong 예외는 계속 유지

#### 3차 rollout

- residual `ACQ_DOMINANT`
- source expansion 이후 재측정된 lane만 대상
- future separate decision 완료 이후에만 개방
- 조치: blanket 격리 금지, residual subset만 결정

### 산출물

- `publish_state_mapping_table.md`
- rollout 순서 문서
- `docs/DECISIONS.md` 봉인 추가
  - `quality_state = fail` reserved 유지

### Gate

- `publish_state` 매핑표가 deterministic하게 닫힌다.
- 1차 rollout 대상 목록이 확정된다.
- `internal_only` 조건이 사람이 아니라 규칙으로 재현 가능하게 정의된다.

---

### Phase 4 — 구현

### 4-1. structural audit 구현

- `Iris/build/description/v2/tools/build/layer3_structural_audit.py` 구현
- item별 아래 필드 출력
  - `structural_verdict`
  - `violation_type`
    - Phase 1 감사에서 확정된 enum만 허용
  - `recommended_tier`
  - `evidence`
- style linter에서 이전된 규칙은 deprecated 처리
- deprecated source와 새 structural source를 기록

### 4-2. decision stage 입력 연결 구현

- `Iris/build/description/v2/tools/build/report_quality_publish_decision_preview.py` 수정
  - `surface_contract_signal.jsonl` 4번째 입력 추가
- decision 로직 추가
  - `hard_fail + hard_block_candidate -> quality_state = weak` + `publish_state = internal_only` 동시 적용
  - `hard_fail -> quality_state = weak`
  - `hard_block_candidate -> publish_state = internal_only` 기본 처리
  - `publish_isolation_candidate -> lane open + current rule allow 시에만 publish_state = internal_only`
  - `flag -> structural_flag` 기록
- `structural_flag` 제약
  - preview/report-only meta 필드
  - emitted contract artifact, Lua bridge field, runtime consumer에 절대 포함 금지
- reason code 기록
  - `identity_only_surface_violation`
  - `layer4_absorption_surface_block`
  - `body_lacks_item_specific_use_surface_violation`
  - `function_narrow_surface_isolation`
  - `acq_dominant_residual_surface_isolation`
- 기존 `identity_fallback` 기반 publish 판정 로직은 그대로 둔다
- `recommended_tier`는 direct write instruction이 아니라 decision input으로만 소비한다

### 4-3. build path 연결

실행 순서는 아래처럼 고정한다.

```text
compose
  -> normalizer
  -> style linter (advisory sensor branch)
  -> structural audit
  -> quality/publish decision stage
  -> rendered
  -> Lua bridge
  -> runtime
```

style linter는 structural audit과 분리된 advisory sensor branch로 유지한다.
structural audit의 입력은 rendered 이후 산출물이 아니라 **pre-render contract candidate** 다.

### 4-4. validation report 갱신

- writer drift를 계속 검사
- 기존 `validate_quality_publish_decision_preview.py`의 drift check inventory를 먼저 확인
  - 이미 같은 항목이 있으면 기존 검사를 참조
  - 없으면 신규 drift check 항목 추가
- writer 수 = 1 유지 검증
- `surface_contract_signal`이 input-only인지 검증
- structural audit가 `quality_state` / `publish_state`를 직접 기록하지 않는지 검증
- `structural_flag`가 emitted contract artifact, Lua bridge, runtime consumer로 새어 나가지 않는지 검증
- non-writer direct write 시 hard fail

### 산출물

- `layer3_structural_audit.py`
- 수정된 `report_quality_publish_decision_preview.py`
- 수정된 build path wiring
- deprecated 처리된 style linter 규칙 정리본

### Gate

- 기존 전체 테스트가 회귀 없이 통과한다.
- rendered text는 한 글자도 안 바뀌고 publish split만 달라지는 샘플이 재현된다.
- writer 수 = 1 검증이 pass다.

---

### Phase 5 — baseline-delta 검증 및 1차 rollout 적용

### 5-1. dry-run delta 분석

적용 전후 distribution delta를 아래 축으로 분석한다.

- `strong -> weak` 강등 건수 및 목록
- `exposed -> internal_only` 이동 건수
- false positive 수동 샘플 검수
  - Phase 1에서 고정한 표본 규칙 적용
- `quality_baseline_v3` 대비 delta

### 5-2. baseline 갱신

dry-run pass 시 아래를 생성한다.

- `quality_baseline_v4.json`
- structural audit 반영 baseline summary
- `publish_state` 분포 스냅샷
- 1차 rollout expected `internal_only` 증가 범위
- lane stability report

### 5-3. 1차 rollout 적용

1차 rollout 대상에만 `internal_only` isolation을 실제 적용한다.

이번 phase의 성공 기준은 아래처럼 읽는다.

- 명백한 3계층 역할 위반이 default surface에 새로 노출되지 않는다
- contract drift 없이 같은 규칙이 같은 판단을 반복한다
- lane stability가 유지된다

warn 개수 감소는 성공 기준이 아니다.

### 산출물

- `structural_audit_dry_run_delta.json`
- `quality_baseline_v4.json`
- 1차 rollout 결과 보고서

### Gate

- 수동 검수 표본 기준 false positive rate = 0
- `introduced surface regression = 0`
- lane stability pass
- baseline 대비 `internal_only` 증가율이 Phase 5 dry-run expected range 이내다
- 2차 rollout 전 baseline 재동결이 확인된다

---

### Phase 6 — bridge/runtime 소비 경로 검증

### 목적

새 상태 축을 만들지 않고, 기존 bridge/runtime contract 위에서만 structural audit의 소비 결과를 검증한다.

### 검증 항목

- `internal_only` row가 Lua bridge에서 사라지지 않는가
- `quality_state = weak`으로 바뀐 row도 bridge row를 유지하는가
- 3-3 body nil 처리가 발생하지 않는가
- default Browser/Wiki에서만 suppression이 일어나는가
- context menu / other layer / perf regression이 없는가
- `structural_flag`가 preview/report scope를 넘어 Lua bridge나 runtime consumer로 유입되지 않는가
- baseline 대비 `internal_only` 증가율이 Phase 5 dry-run expected range 이내인가

### Gate

- bridge contract drift = 0
- runtime artifact preservation pass
- default consumer suppression pass
- `internal_only` 증가율이 Phase 5에서 동결한 예상 범위 이내다

---

### Phase 7 — runtime 검증 및 closeout

### 7-1. manual in-game validation

Phase 6 수준의 manual validation을 structural audit 반영 후 다시 수행한다.

- `internal_only` suppression pass
- `exposed` body render pass
- structural audit으로 `quality_state`가 바뀐 항목의 인게임 표시 이상 없음

### 7-2. 문서 동결

#### `docs/DECISIONS.md`

- style linter advisory-only 봉인 유지
- surface contract authority는 `quality/publish decision stage` 단독 소유
- post-compose repair 금지 유지
- `internal_only`는 3계층 역할 위반의 1차 격리 수단
- 역할 위반은 style 문제가 아니라 layer boundary contract violation

#### `docs/ARCHITECTURE.md`

- advisory lint와 structural contract signal 분리 경로 명시
- writer / checker / consumer 경계 재서술
- runtime contract와 UI contract 분리 유지

#### `docs/ROADMAP.md`

- 이번 라운드를 `surface contract authority migration`으로 기록
- 2차/3차 rollout을 source expansion 및 future `quality_exposed` round와 분리 기록
- `style lint가 publish를 막는다`는 오해 방지 주석 추가

### Gate

- in-game validation pass
- 전체 테스트 pass
- 문서 3종이 같은 언어로 새 구조를 설명한다

---

## 6. 금지 목록

이번 라운드 전 phase 공통 금지선은 아래처럼 고정한다.

- `style_lint_report.json`을 publish input으로 직접 승격하는 것
- compose 외부 repair / rewrite / lint fix 재도입
- validator가 writer 역할을 수행하는 것
- `active / silent`를 의미 품질 축으로 재전용하는 것
- 새 runtime 상태 축(`surface_quality`, `runtime_only` 등) 도입
- 3-3 문제를 이유로 3-4 상세를 본문에 흡수하는 것
- semantic quality를 이번 라운드에서 UI에 직접 노출하는 것
- `ACQ_DOMINANT` 전면 blanket 격리

---

## 7. 최종 성공 기준

1. `style_lint_report.json`은 advisory-only로 남는다.
2. 별도 `surface_contract_signal.jsonl`이 생성된다.
3. `quality/publish decision stage`가 그 신호를 읽는 유일한 writer다.
4. rendered text는 변경되지 않는다.
5. 3계층 역할 위반 row는 `active` 유지 상태에서 `internal_only`로 default surface에서 격리된다.
6. bridge/runtime artifact는 보존된다.
7. baseline-delta와 lane stability 기준으로 regression = 0 이 확인되고, `publish_state` delta는 expected range 이내로 유지된다.
8. 1차 rollout 수동 검수 표본 기준 false positive rate = 0 이다.
9. 2차/3차 rollout은 각 선행 조건 충족 이후에만 열린다.

---

## 8. 한 줄 요약

이번 라운드는 style linter 승격이 아니라, **structural contract gate를 single-writer publish decision stage 안으로 이관하고, quality 경로와 publish 경로를 각자의 역할에 맞게 분리 운용하는 authority migration round** 다.
