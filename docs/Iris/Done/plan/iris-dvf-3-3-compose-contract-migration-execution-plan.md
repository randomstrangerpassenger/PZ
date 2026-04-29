# Iris DVF 3-3 Compose Contract Migration Execution Plan

> 상태: Draft v0.1  
> 기준일: 2026-04-10  
> 상위 기준: `docs/Philosophy.md`, `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`  
> 선행 문서: `docs/dvf_3_3_body_role_execution_plan.md`, `docs/iris-dvf-3-3-three-axis-contract-migration-execution-plan.md`, `docs/iris-dvf-3-3-surface-contract-authority-migration-execution-plan.md`, `docs/iris-dvf-3-3-acquisition-hint-korean-standardization-execution-plan.md`  
> 입력 기준: `DVF 3-3 Compose Contract Migration 최종 통합 로드맵` (2026-04-10)  
> 기준 코드 경로: `Iris/build/description/v2/`  
> 목적: 닫힌 `body-role closed operational pass`를 재개하지 않고, 별도 `Layer 3 mini-wiki contract migration` 라운드를 열어 DVF 3-3 본문 계약을 정보 유형 section 중심 구조로 재정의한다.

> 이 문서는 상위 문서의 하위 운영 계획 문서다. 상위 문서와 충돌 시 상위 문서가 우선한다.

---

## 1. 라운드 판정

이번 작업은 현재 `body-role closed operational pass`의 연장이 아니다.  
이번 작업은 **`Layer 3 mini-wiki contract migration` 독립 라운드**다.

핵심 판정은 아래 한 줄로 고정한다.

> 이번 라운드의 정답은 body-role closed pass를 다시 뜯는 것이 아니라,  
> 3계층이 담당해야 할 정보 유형 계약을 다시 정의하고,  
> 그 계약을 overlay, body plan, quality/audit 재설계로 오프라인 authority 안에서 이행하는 것이다.

따라서 이번 문서는 다음을 하지 않는다.

- `body-role` closed operational pass를 미완료 상태로 되돌리지 않는다.
- runtime Lua에 새 판단 로직을 넣지 않는다.
- compose 외부 repair/rewrite 경로를 재도입하지 않는다.
- 1계층, 2계층, 4계층, 5계층 자체 구조를 갈아엎지 않는다.
- flat string shipping 계약을 이번 라운드에서 폐기하지 않는다.
- 한국어 문법 엔진(`josa_adaptive` 등)을 이번 라운드 범위로 당기지 않는다.
- `identity_fallback 617`을 현행 계약 기준에서 즉시 재판정하지 않는다.

반대로 이번 문서가 여는 것은 아래 네 가지다.

- 3계층 정보 유형 계약 재정의
- cross-layer support를 위한 합헌 overlay 입력 계층 설계
- `sentence_plan`에서 `body_plan`으로 compose 계약 교체
- `quality_state` 및 structural audit 규칙의 정보 유형 기준 재설계

---

## 2. 불변 헌법선

이번 라운드는 아래 헌법선을 재확인한 상태에서만 진행한다.

1. **오프라인 결정론**
   - 동일 입력이면 동일 출력이어야 한다.
   - overlay 생성, compose, validator, quality/audit 판정 모두 이 원칙을 따른다.
2. **runtime Lua는 render only**
   - Lua consumer는 이미 계산된 결과를 렌더만 한다.
   - 판단, 추론, 필터링, 내용 결정 권한을 갖지 않는다.
3. **compose 외부 repair 금지**
   - post-compose text mutation, rewrite, patch stage를 두지 않는다.
   - 본문 변경이 필요하면 compose authority 내부에서만 처리한다.
4. **single-writer decision stage**
   - `quality_state`와 `publish_state`는 계속 단일 writer만 기록한다.
   - audit, validator, overlay builder는 모두 non-writer다.
5. **해석·권장·비교 금지**
   - 3계층 본문은 위키형 설명이되, 해석, 권장, 비교로 미끄러지지 않는다.
   - cross-layer support가 들어와도 이 금지선은 그대로 유지한다.

---

## 3. 현재 기준선과 변경 경계

현재 상위 문서 기준 DVF 3-3의 닫힌 baseline은 아래처럼 읽는다.

- `body-role` round는 build/runtime/in-game closeout 상태다.
- current runtime/user-facing contract는 three-axis model로 재봉인돼 있다.
- surface contract authority는 `quality/publish decision stage` single-writer 모델로 닫혀 있다.
- acquisition lexical authority와 body-role lexical cleanup은 offline authority branch로 닫혀 있다.

이번 라운드에서 **변경되는 것**은 아래 네 가지다.

- 블록 압축문을 전제로 한 현행 body 구조
- 제한적 cross-layer support를 넣는 입력 seam 부재
- 양적 지표 중심 `quality_state` 기준
- 현행 structural audit 규칙군

이번 라운드에서 **변경되지 않는 것**은 아래 여섯 가지다.

- flat string shipping 유지
- tooltip 시스템과 1·2·4·5계층 자체 구조
- three-axis runtime consumer 구조
- `quality/publish decision stage` single-writer 모델
- 한국어 문법 엔진(`josa_adaptive` 등) 후행 예약
- `identity_fallback 617` 승격 판정은 새 contract 구현 후 재측정으로 후행

즉, 이번 round는 runtime 모델 교체가 아니라 **Layer 3 body authoring contract 교체**다.

---

## 4. 목표 계약

### 4-1. 3계층 정보 유형 계약

3계층이 담당하는 정보 유형 축은 아래 다섯 가지로 다시 정의한다.

| 유형 | 정의 | 필수 여부 |
|---|---|---|
| `identity` | 이 아이템이 무엇인가 | 전체 필수 |
| `classification_context` | 소분류 안에서 어디에 놓이는가 | profile 결정 |
| `primary_use` | 무엇을 할 수 있는가 | profile 결정 |
| `acquisition` | 어디서 어떻게 얻는가 | profile 결정 |
| `limitation_characteristic` | 사실 기반 제약 및 물리적/게임 메카닉 특성 | 선택 |

핵심은 모든 항목이 항상 전부 필요하지 않다는 점이다.

- `identity`는 전체 필수다.
- 나머지 축은 item/profile에 따라 선택적으로 채워진다.
- `quality_state`는 앞으로 단순 분량이 아니라 **어떤 정보 유형이 실제로 커버됐는가**를 기준으로 읽는다.
- `limitation_characteristic`는 사실 기반 제약만 허용한다.
  - 허용: `내구도가 낮아 빠르게 소모된다.`
  - 금지: `내구도가 낮으므로 수리 재료를 미리 챙기는 것이 좋다.`

### 4-2. 4계층 흡수 금지선

cross-layer support를 허용해도 3계층이 4계층을 흡수하면 안 된다.

허용 예시는 아래처럼 고정한다.

- `이 아이템은 ~ 작업의 재료로 쓰이기도 한다`
- `이 아이템은 ~ 작업 맥락에서 자주 쓰인다`
- `근접 무기로 사용할 수 있으며, 주로 ~ 맥락에서 쓰인다`

위 허용 예시는 모두 **목록화 없는 단일 맥락 서술**일 때만 합헌이다.

- 레시피명, 재료명, 행동명을 연쇄 나열하는 방식은 허용하지 않는다.
- `~의 재료로 쓰인다`는 문장은 recipe list 축약판이 아니라 단일 활용 맥락 서술일 때만 허용한다.

금지 예시는 아래처럼 고정한다.

- 4계층 탭의 레시피 목록 나열
- 재료 목록, 행동 목록, 상호작용 목록을 목록 형태로 그대로 나열
- 4계층 설명을 3계층 맥락화 없이 복제

판정 테스트는 아래 한 문장으로 고정한다.

> 3계층을 읽은 뒤에도 4계층 탭을 열 이유가 남아 있는가?

이 문장은 **adversarial review oracle**이다.

- `DECISIONS.md`의 4계층 흡수 금지선 설명에 기록한다.
- audit direct rule로는 쓰지 않는다.
- audit에는 이 oracle을 대체하는 proxy 규칙만 넣는다.

### 4-3. cross-layer 인용 성격

cross-layer 인용은 원문 복제가 아니라 **3계층 맥락 안에서의 재서술**이어야 한다.

예시는 아래처럼 읽는다.

- 2계층: `근접 무기는 ~`
- 3계층: `근접 무기로 사용할 수 있으며, 주로 ~ 맥락에서 쓰인다`

즉, 원문 복사 금지와 계층 독립성 유지가 같이 필요하다.

### 4-4. 목표 입력/조합 구조

target compose 입력은 아래처럼 재정의한다.

```text
facts
  + body_source_overlay
  + decisions
  + profiles
  -> body_plan
  -> rendered flat string
```

구조 원칙은 아래와 같다.

- compose는 raw layer source를 직접 읽지 않는다.
- cross-layer 정보는 오직 `body_source_overlay`를 통해서만 들어간다.
- body 조합은 block 압축이 아니라 section 기반 `body_plan`으로 결정된다.
- shipping artifact는 flat string 유지, section trace는 내부 meta로만 남긴다.

---

## 5. 실행 계획

## Phase A — 계약 재개방 및 정보 유형 계약 정의

### 목적

새 라운드를 governing documents에 선언하고, 3계층이 담당하는 정보 유형 계약을 상위 문서와 하위 명세에 함께 못 박는다.

### 산출물

- `docs/DECISIONS.md` 갱신
  - 새 round 명시
  - 기존 v1 양적 계약 공식 폐기 선언
- `docs/ARCHITECTURE.md` 갱신
  - 새 compose pipeline 위치 반영
- `docs/ROADMAP.md` 갱신
  - closed `body-role` pass와 이번 round 분리 명시
- `docs/dvf_3_3_information_type_contract.md`
  - 정보 유형 정의
  - profile별 필수/선택 축
  - 4계층 흡수 금지선
  - adversarial review 기준

### 핵심 작업

- 이번 라운드를 `body-role extension`이 아니라 독립 `mini-wiki contract migration`으로 문서화
- `identity / classification_context / primary_use / acquisition / limitation_characteristic` 축 정의
- 4계층 흡수 금지선과 합헌 cross-layer support 범위를 정의
- `3계층을 읽은 뒤에도 4계층 탭을 열 이유가 남는가` 문장을 adversarial review oracle로만 등록
- audit spec에는 oracle 문장이 아니라 proxy 규칙만 들어가도록 ownership을 분리

### Gate

- `DECISIONS.md`, `ARCHITECTURE.md`, `ROADMAP.md`에 새 round 분리 선언 반영
- `dvf_3_3_information_type_contract.md` adversarial review 통과
- `v1 양적 계약 공식`이 더 이상 current contract로 읽히지 않음

---

## Phase B — 입력 계층 확장: `body_source_overlay` 설계

### 목적

compose가 타 계층 raw source를 직접 읽지 못하게 구조적으로 차단하고, 합헌적으로 재서술된 overlay만 소비하도록 입력 seam을 다시 설계한다.

### 산출물

- `docs/dvf_3_3_cross_layer_overlay_spec.md`
  - overlay 스키마
  - 생성 규칙
  - compose 소비 계약
  - overlay builder 입력 artifact 목록
    - 파일명
    - 파일 형식
    - 파이프라인 내 위치
  - overlay builder의 실행 위치
    - facts 생성 단계 전후 관계
    - compose 진입 전 정합성 검증 타이밍
- overlay 생성 스크립트 설계

### overlay 구조

```text
body_source_overlay (per item)
  - layer1_identity_hint
  - layer2_anchor_hint
  - layer4_context_hint
```

### 필드 의미

- `layer1_identity_hint`
  - 1계층 기초 설명을 3계층 정체성 축에 맞게 재서술한 힌트
- `layer2_anchor_hint`
  - 2계층 주 소분류를 3계층 분류 맥락으로 재서술한 힌트
- `layer4_context_hint`
  - 4계층 상호작용에서 대표 작업 맥락만 요약한 힌트
  - 목록 나열 금지

### ownership 경계

overlay는 **source 재서술 계층**으로만 제한한다.

- overlay에 남는 필드
  - `layer1_identity_hint`
  - `layer2_anchor_hint`
  - `layer4_context_hint`
- overlay에서 제거하는 필드
  - `body_scope_profile`
  - `cross_layer_support_budget`

프로파일과 조합 규약의 ownership은 overlay가 아니라 아래에 둔다.

- `compose_profile` 확정 권한
  - decisions / profile resolution layer
- cross-layer support의 포함/과잉 방지 규약
  - profile rule + audit proxy

`cross_layer_support_budget` 같은 연속 비중값은 이번 라운드에서 overlay에 두지 않는다.

- budget이 필요하면 profile rule의 discrete tier로만 다룬다.
- 이 경우에도 section 포함/제외 같은 이산 규칙으로만 번역한다.

### 핵심 설계 원칙

- overlay는 오프라인 파이프라인에서 사전 생성한다.
- compose는 overlay만 읽고 raw layer를 직접 파싱하지 않는다.
- overlay 생성도 결정론적이어야 한다.
- overlay artifact는 `layer3_body_source_overlay.jsonl`로 facts와 분리한다.
- hint가 `null`이면 해당 section 생략 여부도 결정론적으로 판정한다.

### overlay builder 위치

- overlay builder는 1/2/4계층 authority artifact가 닫힌 뒤에 실행한다.
- facts의 canonical item key set이 확정된 뒤 overlay를 materialize한다.
- compose는 facts와 overlay가 둘 다 materialize되고 validator 정합성 검사를 통과한 뒤에만 실행한다.
- overlay/facts 정합성 검사는 **overlay 생성 직후, compose v2 실행 전**에 수행한다.

### 정합성 원칙

- 원본 계층 데이터가 바뀌면 overlay를 재생성한다.
- overlay와 facts의 정합성은 validator가 확인한다.
- validator는 drift checker이지 overlay writer가 아니다.

### Gate

- `dvf_3_3_cross_layer_overlay_spec.md` adversarial review 통과
- compose가 raw layer를 직접 읽지 않는 구조적 격리 확인
- overlay/facts 정합성 검사 규칙 정의 완료

---

## Phase C — compose 엔진 교체: `sentence_plan`에서 `body_plan`으로

### 목적

현행 block 압축형 `sentence_plan`을 폐기하고, 정보 유형 section 기반 가변 조합 구조로 compose 계약을 교체한다.

### 산출물

- `docs/dvf_3_3_compose_v2_spec.md`
  - 새 compose 계약 명세
  - `body_plan` 구조
  - connector 규칙
  - rendered trace 원칙
- 갱신된 profiles 스키마
- 기존 `3 profile -> 6 profile` migration spec
  - 매핑 테이블
  - 자동 migration 규칙
  - 수동 재분류 inventory 규칙
- migration inventory artifact
  - `compose_profile_migration_inventory*.jsonl`
  - `compose_profile_migration_summary*.json`
- canonical predicate / precedence artifact
  - `compose_profile_identity_hint_rules.json`
  - `compose_profile_conflict_precedence_rules.json`
  - `compose_profile_precedence_draft*.json`

### 공식 폐기 항목

- `4블록/4문장 상한`
- `블록당 슬롯 수 상한 3`
- `slot_sequence`
- block 단위 조합을 전제로 한 현행 `sentence_plan`

### 새 `body_plan` 구조 예시

```text
identity_core
use_core
context_support
acquisition_support
limitation_tail
```

새 구조의 규칙은 아래처럼 고정한다.

- section은 `0~N`개 허용
- section 존재 여부는 `facts + body_source_overlay`에서 결정론적으로 판정
- section 내부 슬롯 수 상한은 두지 않는다
- 같은 profile + 같은 입력이면 section 순서는 항상 동일하다
- 슬롯이 `0`개인 section은 emitted section으로 계산하지 않는다

### 정보 유형과 section 매핑

| Phase A 정보 유형 | Phase C section |
|---|---|
| `identity` | `identity_core` |
| `classification_context` | `context_support` |
| `primary_use` | `use_core` |
| `acquisition` | `acquisition_support` |
| `limitation_characteristic` | `limitation_tail` |

### profile 재설계

기존 `interaction_tool / interaction_component / interaction_output` 프로파일은 폐기하고, 본문 조성 규약 기반 프로파일로 다시 정의한다.

| 프로파일 | 대상 | 필수 section | 선택 section |
|---|---|---|---|
| `tool_body` | 도구형 | `identity_core`, `use_core` | `context_support`, `acquisition_support`, `limitation_tail` |
| `material_body` | 재료형 | `identity_core`, `context_support` | `use_core`, `acquisition_support`, `limitation_tail` |
| `consumable_body` | 소비형 | `identity_core`, `use_core`, `limitation_tail` | `acquisition_support`, `context_support` |
| `wearable_body` | 착용형 | `identity_core`, `limitation_tail` | `context_support`, `acquisition_support`, `use_core` |
| `container_body` | 용기형 | `identity_core`, `use_core` | `context_support`, `limitation_tail`, `acquisition_support` |
| `output_body` | 변환/출력형 | `identity_core`, `context_support` | `use_core`, `limitation_tail`, `acquisition_support` |

각 profile은 아래도 같이 가져야 한다.

- section 우선순위 리스트
- 필수 최소 커버리지 기준
- connector 허용 패턴
- acquisition 과잉 방지 규칙

Phase C 이후 문서에서는 section 참조를 `body_plan` section 명칭으로 통일한다.

- `identity`, `primary_use`, `limitation` 같은 정보 유형 명칭은 Phase A 문맥에서만 사용한다.
- Phase C 이후의 profile, compose, quality, audit 문서에서는 `identity_core / use_core / context_support / acquisition_support / limitation_tail`만 사용한다.

### 기존 decisions profile migration

이번 라운드는 기존 decisions row의 `compose_profile`을 신규 6 profile로 migration하는 계획을 Phase C 산출물에 포함해야 한다.

| 기존 profile | 기본 target | 자동 분기 기준 |
|---|---|---|
| `interaction_tool` | `tool_body` | `container` predicate set이면 `container_body`, `wearable` predicate set이면 `wearable_body`, `consumable` predicate set이면 `consumable_body`, 그 외는 `tool_body` |
| `interaction_component` | `material_body` | `standalone_use` predicate set이면 `tool_body`, 그 외는 `material_body` |
| `interaction_output` | `output_body` | `consumable_effect` predicate set이면 `consumable_body`, `wearable_trait` predicate set이면 `wearable_body`, 그 외는 `output_body` |

Phase C spec는 아래를 같이 가져야 한다.

- 자동 migration 규칙의 facts 기반 분기 조건
- `1:N` 분기에서 쓰는 canonical precedence
- 자동 매핑 불가능 row의 수동 재분류 inventory 기준
- migration 결과와 기존 decisions row count 정합성 검증
- explicit target / legacy fallback / predicate gap 분포 보고
- identity family target / selected role target conflict 분포 보고

자동 분기 조건은 아래 원칙으로만 정의한다.

- facts 및 decisions의 canonical field enum 조합으로만 분기한다.
- 자연어 해석 기반 분기 조건은 허용하지 않는다.
- enum 조합으로 표현 불가능한 item은 수동 재분류 inventory에 넣는다.

### connector 재설계 범위

이번 라운드의 connector 범위는 아래처럼 제한한다.

- literal connector 확장
- section 전환 connector 추가

이번 라운드 밖으로 미루는 것은 아래다.

- 한국어 문법 엔진
- `josa_adaptive`
- 확률적/런타임 connector 선택

### rendered 출력 원칙

- shipping artifact는 계속 flat string이다.
- 내부 `body_plan` trace는 보존한다.
- emitted section이 `2개 이상`이면 section 사이에 항상 `\n\n`을 삽입한다.
- emitted section이 `0개 또는 1개`이면 `\n\n`을 삽입하지 않는다.
- 조건부 부분 삽입은 금지한다.
- rendered 구조화 출력은 후행 라운드로 미룬다.

### Gate

- `dvf_3_3_compose_v2_spec.md` adversarial review 통과
- tool/material/bag/wearable/food/container/component 경계 사례를 포함한 pilot `40~60`개 sample corpus 통과
- pilot corpus가 golden subset seed 역할을 하도록 고정
  - 신규 profile별 대표 아이템 최소 `5`개
  - 경계 사례 포함
  - 기존 `strong / adequate / weak` 판정 아이템 각각 포함
  - deterministic artifact로 `dvf_3_3_body_plan_v2_pilot_corpus*.jsonl` 유지
- 기존 `3 profile -> 6 profile` migration table과 auto rule review 통과
- 같은 입력 2회 compose 시 동일 section order / 동일 출력 보장 확인

---

## Phase D — audit/quality 재설계

### 목적

healthy cross-layer support와 layer role absorption을 분리하고, `quality_state`를 정보 유형 커버리지 중심 계약으로 다시 정의한다.

### 산출물

- `docs/dvf_3_3_quality_contract_v2.md`
  - 새 `quality_state` 정의
  - `strong / adequate / weak` 판정 기준
- 갱신된 `layer3_structural_audit.py` 설계 명세
- 새 audit flag 목록과 판정 규칙

### D-1. `quality_state` 기준 재정의

#### `strong`

- 필수 section이 모두 채워짐
- `identity_core`가 generic fallback이 아닌 item-specific 서술임
- profile-relative strong 최소선을 충족함
- cross-layer support가 들어온 경우 보강으로만 작동함
- 4계층 흡수 없음
- acquisition이 body를 지배하지 않음

#### `adequate`

- 핵심 정보 유형 2개 이상 커버
- `identity_core + 최소 1개 추가 section`이 의미 있게 서술됨
- 일부 필수 section이 비어 있을 수 있음
- 차용은 합헌이나 정보 밀도가 부족함

#### `weak`

- `identity_core`만 있거나 정보 유형 커버리지 `1개 이하`
- generic fallback 수준
- 4계층 열거
- acquisition 지배
- identity 재복제
- 2계층 echo 반복

### 기계 판정 규칙

상위 정의 아래의 direct machine rule은 아래처럼 고정한다.

- `strong`
  - profile이 요구하는 필수 section이 모두 emitted 상태다.
  - `identity_core`가 generic fallback이 아니라 item-specific 서술이다.
  - profile별 strong 최소선 조합을 충족한다.
  - 위반형 audit flag가 없다.
- `adequate`
  - `identity_core`가 emitted 상태다.
  - 최소 1개 추가 section이 emitted 상태다.
  - profile별 adequate 최소선 조합을 충족한다.
  - 위반형 audit flag가 없다.
- `weak`
  - 위반형 audit flag가 1개 이상 있거나,
  - emitted section이 사실상 `identity_core` 하나뿐이다.

슬롯 수와 connector 개수는 `strong/adequate`를 직접 나누는 기준으로 쓰지 않는다.

- section 내부 슬롯이 `0`개면 해당 section은 미완성으로 판정한다.
- connector는 서술 정합성 보조 규칙이지 quality scoring proxy가 아니다.

### profile별 adequate 최소선

`adequate`는 전역 공통 조건과 profile별 최소선을 모두 통과해야 한다.

1. 전역 공통 조건
   - `identity_core`가 emitted 상태다.
   - 위반형 audit flag가 없다.
   - 최소 1개 추가 section이 emitted 상태다.
2. profile별 최소선
   - 아래 조합을 충족하지 못하면 `adequate`가 아니라 `weak`으로 내린다.

| 프로파일 | adequate 최소 emitted section |
|---|---|
| `tool_body` | `identity_core + use_core` |
| `material_body` | `identity_core + context_support` |
| `consumable_body` | `identity_core + use_core` |
| `wearable_body` | `identity_core + (limitation_tail 또는 context_support)` |
| `container_body` | `identity_core + use_core` |
| `output_body` | `identity_core + context_support` |

### profile별 strong 최소선

`strong`은 전역 공통 조건과 profile별 strong 최소선을 모두 통과해야 한다.

1. 전역 공통 조건
   - profile이 요구하는 필수 section이 모두 emitted 상태다.
   - `identity_core`가 item-specific 서술이다.
   - 위반형 audit flag가 없다.
2. profile별 strong 최소선
   - 아래 조합 중 하나를 충족해야 한다.

| 프로파일 | strong 최소 emitted section |
|---|---|
| `tool_body` | 필수 section + 선택 section `1개 이상` |
| `material_body` | 필수 section + 선택 section `1개 이상` |
| `consumable_body` | 필수 section 모두 |
| `wearable_body` | 필수 section 모두 |
| `container_body` | 필수 section + 선택 section `1개 이상` |
| `output_body` | 필수 section + 선택 section `1개 이상` |

즉, `핵심 정보 유형 3개 이상`은 universal hard rule이 아니라 **default expectation** 으로만 읽는다.

- profile 구조상 필수 section만으로도 충분히 완결되는 경우 profile override가 우선한다.
- strong 판단의 authoritative 기준은 profile-relative minimum이다.

### `quality_state -> publish_state` 매핑

기존 매핑은 유지한다.

- `weak -> internal_only`
- `adequate` 이상 -> `exposed` 후보

이번 라운드에서는 `617` 연쇄 이동을 직접 제어하지 않는다.

### D-2. structural audit 재설계

#### 폐기 플래그

- `LAYER4_ABSORPTION`
  - 세분화 규칙으로 대체
- `BODY_LACKS_ITEM_SPECIFIC_USE`
  - coverage 판정으로 흡수
- `FUNCTION_NARROW`
  - `quality_state adequate/weak` 판정으로 흡수
- `ACQ_DOMINANT`
  - `ACQUISITION_OVERRUN`과 coverage deficit 규칙으로 대체

#### 새 허용형 신호

- `HEALTHY_LAYER1_SUPPORT`
  - 1계층 기초 성격 보강
- `HEALTHY_LAYER2_ANCHOR`
  - 2계층 anchor/공통 의미 보강
- `HEALTHY_LAYER4_CONTEXT`
  - 4계층 대표 작업 맥락 보강

#### 새 위반형 플래그

- `INTERACTION_LIST_DUPLICATION`
  - 실질 기준은 `나열 방식`과 `맥락화 방식`의 구분이다.
  - Phase D preview calibration default는 explicit list delimiter만 잡는다.
  - 단일 compound context 예: `보관 및 휴대 작업`은 합헌 맥락화로 본다.
  - explicit delimiter 예: `,`, `/`, `;`, `·`
- `CROSS_LAYER_RAW_COPY`
  - overlay hint를 3계층 맥락화 없이 복제
- `SECTION_COVERAGE_DEFICIT`
  - profile 요구 최소 커버리지 미달
- `BODY_COLLAPSES_TO_ACQUISITION`
  - `acquisition_support`가 emitted되어 있고, 동시에 `identity_core` 외의 다른 의미 있는 section이 하나도 emitted되지 않음
- `BODY_LOSES_ITEM_CENTRICITY`
  - item-specific 서술 없이 generic 문장만 남음

### review oracle과 audit proxy 분리

review oracle은 아래 한 문장으로만 유지한다.

> 3계층을 읽은 뒤에도 4계층 탭을 열 이유가 남아 있는가?

이 문장은 audit spec에 직접 넣지 않는다.

audit는 아래 proxy 규칙만 사용한다.

- `INTERACTION_LIST_DUPLICATION`
- `CROSS_LAYER_RAW_COPY`
- `BODY_COLLAPSES_TO_ACQUISITION`
- `BODY_LOSES_ITEM_CENTRICITY`

즉, audit는 proxy로 판정하고, adversarial review는 oracle 문장으로 재확인한다.

### audit의 역할 경계

- structural audit는 non-writer sensor다.
- 결과는 `surface_contract_signal.jsonl`에 기록한다.
- audit는 `quality_state`나 `publish_state`를 직접 기록하지 않는다.
- `HEALTHY_*` 허용형 신호는 보고용 meta 전용이다.
- `HEALTHY_*` 신호는 `quality/publish decision stage`의 direct input이 아니다.

### Gate

- `dvf_3_3_quality_contract_v2.md` adversarial review 통과
- structural audit spec review 통과
- `INTERACTION_LIST_DUPLICATION` proxy calibration 결과 문서 반영 완료
- profile별 adequate 최소선 테이블 review 통과
- profile별 strong 최소선 테이블 review 통과
- 새 플래그 규칙이 sample corpus에서 일관되게 재현됨

---

## Phase E-0 — migration shim

### 목적

`sentence_plan`을 끄고 `body_plan`을 켜는 전환을 big-bang으로 수행하지 않고, 기존 corpus/preview/regression fixture를 흔들지 않는 shim 단계에서 먼저 검증한다.

### 산출물

- old `sentence_plan -> new body_plan` compatibility emitter
- dual preview 비교 산출물
  - 구 corpus preview
  - 신 corpus preview
- golden subset seed 중 `10개 이하` sample에 대한 body-plan 우선 적용 비교 리포트
- blocker inventory 산출물
  - `dvf_3_3_body_plan_v2_blockers*.jsonl`
  - `dvf_3_3_body_plan_v2_blockers*.summary*.json`

### 핵심 작업

- 기존 출력 형식은 유지한 채 신규 engine을 시험한다.
- dual preview로 drift를 비교한다.
- golden subset seed의 소규모 subset에서만 body_plan 우선 적용을 먼저 켠다.
- explained weak regression row에는 `publish compatibility shim`을 적용할 수 있다.
  - 조건: legacy `publish_state=exposed`이며, 새 `quality_state=weak`가 유지되거나 설명 가능한 drift로 내려간 경우
  - 목적: E-0에서 publish churn을 막고, 최종 publish remap은 Phase E로 넘긴다.

### Gate

- compatibility emitter가 기존 preview contract를 깨지 않는다.
- delta를 `예상 delta / 비예상 delta`로 분류한다.
- 비예상 delta가 남는 동안 blocker inventory로 원인을 아래 두 축에서 분리한다.
  - blocker type: `identity_use_collapse_only / identity_use_collapse_plus_context_gap / context_gap_only`
  - context provenance: `no_positive_usecase / positive_usecase_policy_excluded / representative_context_available`
- 예상 delta만 존재한다.
  - section 추가/삭제로 인한 본문 길이 변화
  - section 간 구분자 삽입으로 인한 형식 변화
  - profile 재분류로 인한 section 구성 변화
  - shim 적용으로 인한 legacy publish 유지
- 비예상 delta가 `0`건이다.
  - 기존 `identity_core` 문장 내용 변화
  - 기존 emitted section의 슬롯 값 변화
  - 설명 불가능한 `quality_state` 이동
  - `publish_state` 역행
- sample subset에서 deterministic output과 validator alignment가 확인된다.

---

## Phase E — 구현, 회귀 검증, 동결

### 목적

Phase A~D와 `Phase E-0`에서 닫은 설계를 실제 코드와 데이터에 반영하고, regression과 in-game validation을 거쳐 이번 라운드를 동결한다.

### 구현 순서

1. overlay 생성 스크립트 구현
2. 새 profiles 정의
3. `compose_layer3_text.py` 재작성
   - `body_plan`
   - section 조합
   - connector 확장
4. `quality_state` 판정 로직 재작성
5. structural audit 규칙 재작성
6. validator 갱신
   - overlay 정합성 검증 추가
7. rendered flat string 단락 구분 제한 반영
   - emitted section `2+`이면 section 사이마다 항상 `\n\n`
8. Lua bridge 확인
   - 변경 최소 예상
   - contract drift 검증은 필수

### 검증 3층 구조

#### authoring regression

- Phase C에서 고정한 golden subset seed + full pilot corpus 병행
- 과잉 차용 탐지
- acquisition 과잉 탐지
- 4계층 흡수 탐지
- `quality_state` 분포 변화 리포트

#### contract regression

- single-writer 위반 없음 확인
- validator drift 없음 확인
- `publish_state` 역행 없음 확인
- bridge contract drift 없음 확인
- 결정론 검증
  - 동일 입력 2회 실행
  - SHA 일치

#### in-game validation

설명창 스크롤 환경에서 실제 읽힘을 확인한다.

- item-centric 본문이 살아 있는가
- 4계층을 열기 전에도 위키처럼 읽히는가
- 4계층을 눌러볼 이유가 여전히 남아 있는가

### 동결 산출물

- 새 quality baseline 동결
- `docs/DECISIONS.md`
  - v1 양적 계약 폐기
  - v2 정보 유형 계약 채택 기록
- `docs/ARCHITECTURE.md`
  - 새 compose pipeline 반영
- `docs/ROADMAP.md`
  - 이번 라운드 완료 및 후행 항목 정리

### 이번 라운드 밖의 후행 항목

- `identity_fallback 617` 새 contract 기준 재측정
- `role_fallback hollow 37` source expansion handoff 소비
  - `existing_cluster_reuse 20`
  - `policy_revisit 2`
  - `net_new_source_expansion 15`
  - `reuse_candidate_facts 20`
  - `policy_revisit_inventory 2`
  - `C1-B reuse package 20`
  - `policy review lane 2`
  - `C1-B reuse promotion preview 20/20 strong, 20/20 exposed`
  - `post-C1-B residual 17`
  - `net_new package 15`
  - `policy review memo 2`
  - `policy resolution packet maintain_exclusion 2`
  - `policy outcome projection default closeout 2 / override reopen C1-G 2`
  - `policy default closeout closed 2 / remaining tail 3`
  - `residual tail handoff parked 3 (C1-F 1 / C1-G 2)`
  - `residual tail source-discovery round 3 (C1-F 1 -> C1-G 2)`
  - `residual tail discovery status executed 3 / pending 0`
  - `residual tail round closeout complete -> carry-forward hold 3`
  - `terminal status 17 -> promoted 12 / policy closed 2 / carry-forward hold 3 / active unresolved 0`
  - `terminal handoff 37 -> reuse preview 20 / promoted 12 / policy closed 2 / carry-forward hold 3`
  - `C1-F local discovery executed 1 -> reopen_ready 0 / remain_parked 1`
  - `C1-G local discovery executed 2 -> reopen_ready 0 / remain_parked 2`
  - `C1-F tool_use_recovery 6`
  - `C1-G material_context_recovery 9`
  - `follow-up runbook reuse 20 -> policy projection 2 -> net_new 15`
  - `block_c seed packages C1-F 6 / C1-G 9`
  - `local evidence targeted 7 / manual 8`
  - `manual second-pass upgrades 5 -> remaining manual 3`
  - `source authoring queue targeted 12 / manual 3`
  - `targeted authoring pack 12`
  - `targeted authoring drafts 12`
  - `source promotion drafts 12`
  - `manual search pack 3`
  - `manual residual blocker memo parked 3`
  - `source merge preview pass 12`
  - `source authority candidates 15 (promotion ready 12 / parked 3)`
  - `source replacement candidates 15 (ready 12 / carry-forward parked 3)`
  - `source replacement delta review 15 (semantic upgrade 12 / parked carry-forward 3)`
  - `source promotion manifest 15 (apply ready 12 / carry-forward parked 3)`
  - `source promotion applied package 2 (ready 12 / carry-forward parked 3)`
  - `post-block-c apply status 17 (promoted 12 / parked 3 / policy 2, default maintain_exclusion 2)`
  - `post-policy default closeout status 17 (promoted 12 / policy closed 2 / parked 3)`
  - `final carry-forward tail 3 (SteelAndFlint / Yarn / ConcretePowder)`
  - `post-apply ready preview index 2 (ready 12 / parked 3 / direct_use preserved 12 / special_context preserved 11 / gate pass 2)`
  - `post-C projection replacement delta role_fallback -12 / direct_use +12`
  - `integrated runtime handoff path counts cluster_summary 1275 / identity_fallback 718 / role_fallback 100 / direct_use 12`
  - `projection_comparison match true`
- source expansion lane reopen
- rendered 구조화 출력
  - section-aware 구조화
  - Lua consumer 단락 렌더
- 한국어 문법 엔진
  - `josa_adaptive`
  - v2 계열

---

## 6. 의존 관계

아래 의존 그래프로 실행 순서를 고정한다.

```text
Phase A (계약 재개방 + 정보 유형 계약)
        ↓
Phase B (overlay 설계) ──────────────────┐
        ↓                                │ 설계 수준 병렬 가능
Phase C (compose 엔진 교체) ◄────────────┘
        ↓
Phase D (audit/quality 재설계)
        ↓
Phase E-0 (migration shim)
        ↓
Phase E (구현/검증/동결)
```

규칙은 아래처럼 읽는다.

- `Phase A`가 닫히기 전에는 `B/C`를 실행하지 않는다.
- `Phase B`와 `Phase C`는 `A` 종료 후 설계 수준에서 병렬 가능하다.
- `Phase D`는 `A/B/C` 설계가 모두 닫힌 뒤에만 연다.
- `Phase E-0`는 `D`가 닫힌 뒤에만 시작한다.
- `Phase E`는 `E-0` gate가 닫힌 뒤에만 시작한다.

---

## 7. 최종 판정 문구

이번 라운드의 성공 조건은 `문장이 더 자연스러워졌다` 하나가 아니다.  
성공 조건은 아래 네 줄이 동시에 참이 되는 것이다.

- 3계층이 정보 유형 기준으로 자기 역할을 다시 설명할 수 있다.
- cross-layer support가 overlay seam 안에서만 합헌적으로 작동한다.
- compose가 `body_plan` 기반 section 조합으로 결정론적으로 동작한다.
- `quality_state`와 structural audit가 정보 유형 커버리지 기준으로 일관되게 판정된다.

즉, 이번 round는 lexical polish나 runtime tweak가 아니라, **DVF 3-3 본문을 mini-wiki contract로 다시 정의하는 설계 migration round** 다.
