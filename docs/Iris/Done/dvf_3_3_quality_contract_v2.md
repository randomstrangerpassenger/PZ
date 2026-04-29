# DVF 3-3 Quality Contract V2

> 상태: draft v0.1  
> 기준일: 2026-04-10  
> 상위 기준: `docs/dvf_3_3_information_type_contract.md`, `docs/dvf_3_3_compose_v2_spec.md`, `docs/quality_state_ownership_spec.md`  
> 실행 계획: `docs/iris-dvf-3-3-compose-contract-migration-execution-plan.md`

---

## 1. 목적

이 문서는 DVF 3-3의 `quality_state`를 기존 양적 slot 사고에서 분리하고, 정보 유형 커버리지와 profile-relative completeness 기준으로 다시 정의한다.

핵심 원칙은 아래 두 가지다.

- quality는 분량이 아니라 **무슨 정보 유형이 실제로 emitted되었는가**로 읽는다.
- `strong / adequate / weak`의 authoritative 기준은 profile-relative minimum이다.

---

## 2. writer 경계

이 문서는 `quality_state` 판정 계약만 정의한다.

- quality writer는 단일 decision stage다.
- structural audit는 non-writer sensor다.
- audit 결과는 quality를 직접 쓰지 않는다.
- 허용형 신호는 보고용 meta일 뿐 가점이 아니다.

즉, audit와 quality는 연결되지만 ownership은 분리된다.

---

## 3. 상위 정의

### 3-1. `strong`

아래 조건을 모두 만족하는 본문이다.

- 필수 section이 모두 채워져 있다.
- `identity_core`가 generic fallback이 아니라 item-specific 서술이다.
- profile-relative strong 최소선을 충족한다.
- cross-layer support가 있더라도 보강으로만 작동한다.
- 위반형 flag가 없다.

### 3-2. `adequate`

아래 조건을 만족하지만 `strong`까지는 아닌 본문이다.

- `identity_core`가 존재한다.
- 최소 1개 추가 section이 의미 있게 emitted된다.
- profile-relative adequate 최소선을 충족한다.
- 위반형 flag가 없다.

### 3-3. `weak`

아래 중 하나에 해당하는 본문이다.

- 위반형 flag가 하나 이상 존재한다.
- emitted section이 사실상 `identity_core` 하나뿐이다.
- generic fallback 수준이다.
- profile별 adequate 최소선을 충족하지 못한다.

---

## 4. direct machine rule

quality 판정의 direct machine rule은 아래처럼 고정한다.

### `strong`

- profile 필수 section이 모두 emitted 상태다.
- `identity_core`가 item-specific 서술이다.
- profile별 strong 최소선 조합을 충족한다.
- 위반형 audit flag가 없다.

### `adequate`

- `identity_core`가 emitted 상태다.
- 최소 1개 추가 section이 emitted 상태다.
- profile별 adequate 최소선 조합을 충족한다.
- 위반형 audit flag가 없다.

### `weak`

- 위반형 audit flag가 1개 이상이거나,
- emitted section이 사실상 `identity_core` 하나뿐이거나,
- profile별 adequate 최소선을 충족하지 못한다.

아래는 direct scoring rule로 쓰지 않는다.

- 슬롯 수
- connector 개수
- 문장 수
- 문자 수

section 내부 슬롯 수가 `0`이면 해당 section은 미완성으로 보고 emitted로 계산하지 않는다.

---

## 5. profile별 adequate 최소선

`adequate`는 전역 공통 조건과 profile별 최소선을 모두 통과해야 한다.

전역 공통 조건:

- `identity_core` emitted
- 최소 1개 추가 section emitted
- 위반형 flag 없음

profile별 최소선:

| 프로파일 | adequate 최소 emitted section |
|---|---|
| `tool_body` | `identity_core + use_core` |
| `material_body` | `identity_core + context_support` |
| `consumable_body` | `identity_core + use_core` |
| `wearable_body` | `identity_core + (limitation_tail 또는 context_support)` |
| `container_body` | `identity_core + use_core` |
| `output_body` | `identity_core + context_support` |

전역 조건만 통과하고 profile 최소선을 통과하지 못하면 `adequate`가 아니라 `weak`이다.

---

## 6. profile별 strong 최소선

`strong`은 universal `3개 축 이상` hard rule로 읽지 않는다.  
authoritative 기준은 profile-relative minimum이다.

전역 공통 조건:

- profile 필수 section 모두 emitted
- `identity_core` item-specific
- 위반형 flag 없음

profile별 strong 최소선:

| 프로파일 | strong 최소 emitted section |
|---|---|
| `tool_body` | 필수 section + 선택 section `1개 이상` |
| `material_body` | 필수 section + 선택 section `1개 이상` |
| `consumable_body` | 필수 section 모두 |
| `wearable_body` | 필수 section 모두 |
| `container_body` | 필수 section + 선택 section `1개 이상` |
| `output_body` | 필수 section + 선택 section `1개 이상` |

즉, `핵심 정보 유형 3개 이상`은 profile 구조가 허용하는 경우의 default expectation일 뿐이다.  
예를 들어 `wearable_body`처럼 필수 축 자체가 강한 프로파일은 필수 section 완결만으로 `strong`이 가능하다.

---

## 7. publish 매핑

기존 publish mapping은 유지한다.

- `weak -> internal_only`
- `adequate` 이상 -> `exposed` 후보

이 문서는 `identity_fallback 617` 재판정이나 연쇄 승격을 직접 다루지 않는다.

---

## 8. audit 연동 원칙

quality는 audit proxy를 읽을 수 있지만, audit는 quality를 직접 쓰지 못한다.

위반형 flag는 quality 하한을 직접 내린다.  
허용형 신호는 quality를 올리지 않는다.

### 허용형 신호

- `HEALTHY_LAYER1_SUPPORT`
- `HEALTHY_LAYER2_ANCHOR`
- `HEALTHY_LAYER4_CONTEXT`

이 신호들은 **보고용 meta 전용**이다.

- quality 가점 없음
- publish 가점 없음
- cross-layer support 추적성만 제공

---

## 9. 위반형 flag 기준

quality contract v2가 직접 읽는 위반형 flag는 아래다.

- `INTERACTION_LIST_DUPLICATION`
- `CROSS_LAYER_RAW_COPY`
- `SECTION_COVERAGE_DEFICIT`
- `BODY_COLLAPSES_TO_ACQUISITION`
- `BODY_LOSES_ITEM_CENTRICITY`

### `BODY_COLLAPSES_TO_ACQUISITION`

정의:

- `acquisition_support`가 emitted되어 있고,
- 동시에 `identity_core` 외의 다른 의미 있는 section이 하나도 emitted되지 않은 상태

이 플래그는 비율 초과가 아니라 구조 붕괴를 잡는다.

### `INTERACTION_LIST_DUPLICATION`

실질 기준:

- `나열 방식`과 `맥락화 방식`의 구분

Phase D preview calibration default:

- 단일 compound context는 허용한다.
  - 예: `보관 및 휴대 작업`
- explicit list delimiter가 남아 있는 경우만 중복 열거 proxy로 본다.
  - 예: `,`, `/`, `;`, `·`

즉, 현재 proxy는 숫자 개수보다 **명시적 열거 흔적**을 우선 읽는다.  
대표 작업 맥락 하나를 재서술한 힌트는 이 플래그로 내리지 않는다.

---

## 10. review oracle 분리

아래 문장은 quality machine rule이 아니라 adversarial review oracle이다.

> 3계층을 읽은 뒤에도 4계층 탭을 열 이유가 남아 있는가?

이 oracle은 아래 용도에만 쓴다.

- audit proxy 적합성 검토
- 4계층 흡수 금지선 재확인

quality machine rule은 이 문장을 직접 읽지 않는다.

---

## 11. 비목표

이 문서는 아래를 하지 않는다.

- overlay field 설계
- section ordering 설계
- connector 문면 설계
- Lua consumer render 변경
