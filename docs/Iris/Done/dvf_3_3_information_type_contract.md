# DVF 3-3 Information Type Contract

> 상태: draft v0.1  
> 기준일: 2026-04-10  
> 상위 기준: `docs/Philosophy.md`, `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`  
> 실행 계획: `docs/iris-dvf-3-3-compose-contract-migration-execution-plan.md`

---

## 1. 목적

이 문서는 `Layer 3 mini-wiki contract migration` 라운드에서 3계층 본문이 무엇을 담당해야 하는지와, 어떤 정보를 어떤 선까지 합헌적으로 다룰 수 있는지를 고정한다.

핵심은 아래 두 가지다.

- 3계층은 더 이상 양적 슬롯 계약으로 읽지 않는다.
- 3계층은 정보 유형 계약에 따라 item-centric mini-wiki body를 구성한다.

이 문서는 section 이름이나 compose 조합 순서를 정의하지 않는다.  
그 책임은 후속 `compose_v2` spec에 있다.  
이 문서는 어디까지나 **3계층이 어떤 정보 유형을 담당하는가**를 규정한다.

---

## 2. 헌법선 재확인

이 계약은 아래 상위 원칙을 전제로 한다.

1. 오프라인 결정론
2. runtime Lua render-only
3. compose 외부 repair 금지
4. single-writer decision stage
5. 해석·권장·비교 금지

즉, 3계층 본문은 위키형 설명이어야 하지만 추천, 비교, 전략 조언으로 미끄러지면 안 된다.

---

## 3. 정보 유형 축

3계층이 다루는 정보 유형은 아래 다섯 축으로 고정한다.

| 정보 유형 | 정의 | 필수 여부 |
|---|---|---|
| `identity` | 이 아이템이 무엇인가 | 전체 필수 |
| `classification_context` | 소분류 안에서 어디에 놓이는가 | profile 결정 |
| `primary_use` | 무엇을 할 수 있는가 | profile 결정 |
| `acquisition` | 어디서 어떻게 얻는가 | profile 결정 |
| `limitation_characteristic` | 사실 기반 제약 및 물리적/게임 메카닉 특성 | 선택 |

운영 원칙은 아래처럼 읽는다.

- `identity`는 모든 item에서 빠질 수 없다.
- 나머지 축은 item 성격과 profile에 따라 채워진다.
- 모든 item이 다섯 축을 전부 채워야 하는 것은 아니다.
- quality 평가는 분량이 아니라 실제 커버된 정보 유형을 기준으로 읽는다.

---

## 4. 축별 허용 범위

### 4-1. `identity`

- 아이템의 정체를 item-centric하게 밝힌다.
- generic label 반복으로 끝나면 안 된다.
- 최소한 동일 아이템을 다른 동종 item과 구분할 수 있는 수준의 정체성은 살아 있어야 한다.

### 4-2. `classification_context`

- 2계층 anchor를 3계층 본문 맥락으로 재서술할 수 있다.
- 단순한 분류 라벨 echo가 아니라, 아이템이 그 분류 안에서 어떤 자리에 놓이는지 드러나야 한다.

### 4-3. `primary_use`

- 이 아이템이 실제로 무엇에 쓰이는지를 item-centric하게 말한다.
- 작업 맥락은 허용되지만 행동 목록, 절차 설명, 비교 평가는 허용하지 않는다.

### 4-4. `acquisition`

- 획득/발견/입수 경로는 보조 축이다.
- 획득 정보만으로 body가 붕괴하면 안 된다.
- acquisition은 identity 또는 다른 핵심 축을 보강할 때만 합헌적이다.

### 4-5. `limitation_characteristic`

허용 범위:

- 사실 기반 제약
- 물리적 특성
- 게임 메카닉 특성

허용 예시:

- `내구도가 낮아 빠르게 소모된다.`

금지 범위:

- 플레이어 행동 조언
- 권장 사용법
- 비교 기반 평가

금지 예시:

- `내구도가 낮으므로 수리 재료를 미리 챙기는 것이 좋다.`

---

## 5. cross-layer support 허용 범위

3계층은 1·2·4계층 정보를 제한적으로 차용할 수 있다.  
단, 원문 복제나 계층 흡수는 허용하지 않는다.

허용되는 cross-layer support는 아래 세 종류다.

- 1계층 기초 정체성 보강
- 2계층 anchor/소분류 맥락 보강
- 4계층 대표 작업 맥락 보강

공통 조건은 아래와 같다.

- 원문 복사가 아니라 3계층 맥락 안에서의 재서술이어야 한다.
- item-centric body를 보강하는 수준이어야 한다.
- 목록화된 상세, 절차, 요구 조건을 가져오면 안 된다.

---

## 6. 4계층 흡수 금지선

3계층은 4계층과 경계를 유지해야 한다.

허용 예시는 아래처럼 고정한다.

- `이 아이템은 ~ 작업의 재료로 쓰이기도 한다.`
- `이 아이템은 ~ 작업 맥락에서 자주 쓰인다.`
- `근접 무기로 사용할 수 있으며, 주로 ~ 맥락에서 쓰인다.`

위 예시는 모두 **목록화 없는 단일 맥락 서술**일 때만 합헌이다.

- 레시피명 나열 금지
- 재료명 나열 금지
- 행동 목록 나열 금지
- 상호작용 탭 축약본처럼 읽히는 서술 금지

즉, `~의 재료로 쓰인다`는 문장은 일반 활용 맥락을 한 번 언급하는 수준에서만 허용된다.  
그 문장이 recipe list의 축약판처럼 증식하면 위반이다.

금지 예시는 아래와 같다.

- 4계층 레시피 목록을 그대로 나열
- 재료 목록, 행동 목록, 대상 목록을 연쇄 나열
- 4계층 설명을 맥락화 없이 복제

---

## 7. review oracle

아래 문장은 audit direct rule이 아니라 adversarial review oracle이다.

> 3계층을 읽은 뒤에도 4계층 탭을 열 이유가 남아 있는가?

이 문장의 역할은 아래처럼 제한한다.

- 4계층 흡수 여부를 사람 검토에서 재확인하는 상위 질문
- audit proxy 규칙의 타당성을 점검하는 review 기준

이 문장을 audit direct rule로 사용하면 안 된다.  
audit는 이 oracle을 대체하는 proxy flag만 사용한다.

---

## 8. 금지된 본문 톤

3계층 본문은 아래 톤으로 넘어가면 안 된다.

- 해석
- 권장
- 비교
- 전략 조언

허용:

- `주로 ~ 맥락에서 쓰인다.`
- `내구도가 낮아 오래 버티지 않는다.`

금지:

- `이 경우에 쓰는 편이 낫다.`
- `다른 무기보다 효율적이다.`
- `미리 준비해 두는 것이 좋다.`

---

## 9. downstream 책임 분리

이 문서를 직접 소비하는 downstream 책임은 아래처럼 나뉜다.

- overlay spec
  - 어떤 cross-layer hint가 합헌적인지 규정
- compose v2 spec
  - 어떤 정보 유형을 어떤 section으로 옮길지 규정
- quality contract v2
  - 어떤 정보 유형 커버리지를 strong/adequate/weak로 읽을지 규정
- structural audit spec
  - 어떤 위반을 proxy flag로 감지할지 규정

즉, 이 문서는 의미 계약이고, 구체 조합 규약은 후속 spec이 맡는다.

---

## 10. 비목표

이 문서는 아래를 하지 않는다.

- section 이름 확정
- connector 규칙 확정
- quality_state 기계 규칙 확정
- publish_state 매핑 변경
- runtime Lua consumer 변경
