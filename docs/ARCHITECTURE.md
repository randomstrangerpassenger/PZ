# ARCHITECTURE.md

> 상태: 초안 v0.7
> 기준일: 2026-09-05 (이번 갱신 범위: Iris L3-05 교정된 표현 readpoint·독립 S2 합성·L3-06 제품 통합 경계)
> 상위 기준: `Philosophy.md`, `DECISIONS.md`  
> 목적: Pulse 생태계의 구조 지도, 역할 경계, 의존 방향을 고정한다.  
> 구현 상태 표기: 별도 표시가 없는 모듈은 current architecture를 기술하며, `설계 단계` 표시는 아직 구현되지 않은 target architecture를 뜻한다.

---

# 1. 구조 원칙

## 1-1. 생태계 토폴로지

- **허브**: Pulse Core
- **퍼스트파티 Spoke**: Echo, Fuse, Nerve Pulse Adapter / Nerve+, Iris, Frame, Cortex, Canvas
- **퍼스트파티 독립 모듈**: Nerve Core
- **외부 소비자**: Pulse의 capability / API / SPI를 사용하는 외부 모드
- **공용 표면**: SPI, capability, hook, state, DTO, event, registry, utility 등

Pulse Core는 퍼스트파티 Spoke와 외부 소비자가 각자의 제품 로직을 독립적으로 구성할 수 있도록 중립적인 공용 기능을 제공하는 얇은 허브다.

퍼스트파티 Spoke와 외부 소비자는 모두 Pulse Core의 소비자이며 서로를 경유하는 계층 관계를 형성하지 않는다. Nerve Core는 이 토폴로지 밖에서 독립적으로 존재하며 Pulse 연동이 필요한 기능만 Nerve Pulse Adapter 또는 Nerve+를 통해 연결한다.

## 1-2. 관측 / 판단 / 정책 분리

공용 capability / SPI에는 관측 가능한 사실과 상태만 제공하며, 그 사실의 해석과 그에 따른 판단·정책은 각 소비 모듈이 소유한다.

대상, 범주, 크기, 시간, 횟수, 비용처럼 직접 관측하거나 계산할 수 있는 값은 공용 계약으로 제공할 수 있지만, 심각도, 우선순위, 개입 필요성이나 특정 모듈이 취해야 할 행동 같은 판단은 공용 계약으로 승격하지 않는다.

`severity`처럼 측정값의 형태를 가지더라도 우선순위나 개입 필요성을 포함하는 값은 공용 관측 표면에 두지 않고 필요한 모듈 내부의 표시·판단 정보로만 유지한다.

---

# 2. 모듈 지도

## 2-1. Pulse Core

### 하는 일

- Java Agent / Mixin 초기화를 제공한다.
- 외부 모드를 발견하고 로드한다.
- 모드 메타데이터, 의존성과 충돌 정보를 처리한다.
- `EventBus`, `Config`, `Scheduler`, `Registry`, `Network`, `DataAttachments`, `AccessWidener`, `GameAccess` 등 공용 기능을 제공한다.
- 소비 모듈이 사용할 수 있는 중립적인 관측·상태 기능을 제공한다.
- 예외 격리, 진단, 로깅, `DevMode` 등 플랫폼 안정성 기능을 제공한다.

### 실행 / 공용 기능 구조

Pulse Core는 모드 로딩과 공용 기능 제공을 분리하여 각 소비 모듈이 Pulse 위에서 독립적인 제품 로직을 구성할 수 있게 한다.

```text
Java Agent / Mixin 초기화
-> 모드 발견 / 로딩
-> 메타데이터 / 의존성 / 충돌 처리
-> 공용 capability 등록
-> 퍼스트파티 Spoke / 외부 소비자
```

- 초기화와 모드 로딩은 공용 기능을 사용할 수 있는 실행 기반을 준비한다.
- 공용 capability는 각 소비 모듈이 필요한 기반 기능을 선택적으로 사용할 수 있는 표면을 제공한다.
- 소비 모듈의 제품 로직이나 갱신 주기는 Pulse Core의 실행 흐름에 포함하지 않는다.

### 서비스 접근 구조

Pulse Core의 공용 서비스 접근은 특정 호출 방식 하나를 공용 계약으로 강제하지 않는다.

- 내부 서비스 접근 방식은 달라질 수 있지만 동일한 공용 서비스 책임과 계약에 연결된다.
- 호환을 위한 접근 경로는 정상 접근 경로를 대체하는 기본 방식으로 사용하지 않는다.

### `EventBus` 구조

`EventBus`는 정상적인 클래스 조회와 호환 조회를 서로 다른 단계로 분리한다.

```text
직접 클래스 조회
-> FQCN 기반 호환 조회
-> 제한적 reflection 호환 조회
```

- 직접 클래스 조회를 정상적인 기본 경로로 사용한다.
- 직접 조회로 해결할 수 없는 경우 이름 기반 호환 조회를 사용한다.
- 앞선 경로로도 해결할 수 없는 경우에만 제한적인 reflection 기반 호환 경로를 사용한다.
- 호환 경로는 정상 실행 경로와 분리하여 사용 범위와 비용이 정상 경로 전체에 확산되지 않도록 한다.
- Listener의 우선순위는 등록 단계에서 확정하고 이벤트 실행 경로는 확정된 순서를 소비하는 단순한 구조로 유지한다.

### 하지 않는 일

- 퍼스트파티 Spoke의 갱신 주기나 실행 시점을 호출·통제하는 것
- 모드 간 동작을 실시간으로 조정하는 범용 중개자나 중앙 조정자 역할을 소유하는 것

---

## 2-2. Echo

### 하는 일

- 병목 관찰에 필요한 실행 계측과 관찰값 수집을 담당한다.
- 수집한 관찰값을 집계하여 통계와 진단 정보를 구성한다.
- 관찰 결과를 오버레이, 리포트와 외부 소비 가능한 형태로 제공한다.
- 관찰 과정에서 발생하는 서로 다른 상태를 구분하여 보존한다.

### 관측 구조

Echo는 게임 실행에서 필요한 지점을 계측하고, 그 결과를 관찰 자료로 수집한 뒤 통계와 사용자 표시 정보로 투영한다.

```text
실행 지점
-> 계측
-> 관찰값
-> 집계 / 통계
-> 오버레이 / 리포트
```

- 계측 단계는 병목 분석에 필요한 실행 정보를 관찰 가능한 값으로 만든다.
- 관찰값의 집계와 통계 구성은 Echo 내부에서 수행한다.
- 오버레이와 리포트는 수집된 관찰 결과를 표시·소비 가능한 형태로 투영한다.
- 운영 경로에서 필요한 관찰과 무거운 정밀 분석 작업을 같은 기본 실행 경로에 결합하지 않는다.

### 관찰 상태 구조

Echo는 값 자체와 그 값을 얻은 상태를 구분한다.

```text
관찰 요청
-> 정상 관찰값
 | 비활성
 | 미등록
 | 정상적인 값의 부재
 | 조회 실패
 | 오류
-> 상태를 보존한 관찰 결과
```

- 값이 없거나 `0`이라는 사실만으로 비활성, 미등록, 조회 실패 또는 오류를 동일한 상태로 취급하지 않는다.
- 관찰할 대상이 존재하지 않는 상태와 관찰 과정 자체가 실패한 상태를 구분한다.
- 리포트는 이러한 상태 차이를 보존하여 소비자가 관찰 결과와 관찰 실패를 구별할 수 있게 한다.

### 하지 않는 일

- 게임 동작 자체를 변경하는 것
- 운영 경로를 무거운 정밀 분석, 디버그용 맥락 수집이나 외부 서비스 조회의 기본 실행 장소로 사용하는 것

---

## 2-3. Fuse

### 정체성

Fuse는 엔진 비용 폭주를 결과 의미를 보존하는 최소 개입으로 완화하는 안정화 계층이다.

### 하는 일

- 엔진 수준의 병목과 순간적인 비용 급증을 완화한다.
- 결과 의미를 유지할 수 있는 범위에서 구조적인 실행 비용을 줄인다.
- 프레임타임의 긴 꼬리와 장시간 지속되는 성능 붕괴를 완화한다.
- 내부 부하 신호와 상태를 바탕으로 개입 필요성과 범위를 판단한다.
- 개입 대상은 Fuse에 배정된 엔진 비용 영역 안에서 구분한다.
- 엔진 비용 축마다 개입 가능 범위와 책임을 독립적으로 구분한다.
- 직접 완화하기 어려운 비분할 정지나 외부 원인의 멈춤은 무리하게 개입하지 않고 관찰·설명 가능한 상태로 남긴다.

### 개입 구조

Fuse의 개입은 엔진 비용 상태의 관찰, 제한된 개입과 안전한 철수를 분리한다.

```text
엔진 비용 상태
-> 내부 부하 판단
-> 의미 보존 가능한 개입 선택
-> 제한된 개입
-> 상태 재확인
-> 유지 / 축소 / 철수
```

- 개입은 동일한 게임 규칙과 결과 의미를 유지할 수 있는 경우에만 적용한다.
- 의미 보존이 가능한 범위에서 보호 조건, 제한, 지연, 중복 제거와 안정화 기법을 사용할 수 있다.
- 개입의 조건과 강도는 Fuse 내부 상태에 귀속되며 각 비용 축의 특성에 맞게 독립적으로 관리한다.
- 부하가 완화되거나 개입의 안전성을 유지할 수 없으면 개입을 축소하거나 철수한다.
- 지속적인 과부하는 더 강한 개입을 자동으로 정당화하지 않으며, 안전한 완화가 불가능하면 상시 개입 상태를 유지하지 않는다.

### 하지 않는 일

- 엔진 전 영역의 평균 성능 향상을 목표로 하는 범용 최적화 모드로 확장하는 것
- 개입 가능성이 확인되지 않은 대형 정지나 외부 원인의 멈춤까지 반드시 해결해야 할 대상으로 간주하는 것

---

## 2-4. Nerve

### 정체성

Nerve는 Lua 상위 경계의 충돌과 호출 폭주를 사건 기반 보호와 안전한 철수로 완충하는 선택적 안정화 계층이다.

### 하는 일

- 이벤트 디스패치, 모드 훅과 네트워크 경계에서 발생하는 Lua 수준의 충돌과 작업 겹침을 완화한다.
- 같은 틱의 재진입, 수신자 예외, 중복 호출과 과도한 호출 연쇄 같은 위험 징후를 관찰한다.
- 결과 의미를 유지할 수 있는 범위에서 보호 조건, 호출 병합, 변경 표식, 읽기 전용 캐시와 사건 한정 보호를 적용한다.
- 필요한 최소한의 운영 상태, 사건 표식과 오류 서명을 외부 관찰 표면에 제공한다.

### 보호 구조

Nerve의 보호는 정상 실행 경로를 상시 감싸는 방식이 아니라 위험 사건을 기준으로 제한적으로 활성화하고 필요하면 철수하는 구조를 사용한다.

```text
Lua 실행 경계
-> 위험 징후 관찰
-> 사건 상태 판정
-> 의미 보존 가능한 보호 선택
-> 제한적 보호
-> 상태 재확인
-> 유지 / 해제 / 철수
```

- 보호는 관찰된 사건과 해당 실행 경계에 한정하여 적용한다.
- 같은 호출의 중복, 재진입과 일시적인 호출 연쇄처럼 결과 의미를 유지하면서 완화할 수 있는 상태만 보호 대상으로 삼는다.
- 보호 상태는 정상 실행과 구분하여 관리하고 전역적인 상시 보호 상태로 확대하지 않는다.
- 보호의 안전성을 유지할 수 없거나 결과 의미가 달라질 가능성이 생기면 개입을 확대하지 않고 해제하거나 철수한다.
- 지속적인 부하나 반복 사건 자체가 더 강한 개입을 자동으로 정당화하지 않는다.

### 하지 않는 일

- 이벤트의 중요도나 우선순위를 판정하고 자동으로 실행 순서나 처리량을 결정하는 정책 엔진으로 확장하는 것
- 결과 의미를 바꿀 수 있는 호출 지연, 재정렬, 폐기 또는 의미 변경형 병합을 기본 보호 방식으로 사용하는 것
- 전역 상시 보호나 영구 차단을 정상 실행 경로로 만드는 것
- 네트워크 경계를 다룬다는 이유로 지연시간 개선, 패킷 최적화, 서버 부하 분산이나 엔진 동기화 수정까지 책임을 확장하는 것

### 계열 구조

- **Nerve Core**
  - 안정성 핵심 로직과 내부 보호 상태를 소유한다.
  - 독립 배포와 독립 실행이 가능한 핵심 제품이다.

- **Nerve Pulse Adapter**
  - Nerve Core의 상태와 기능을 Pulse의 capability / SPI에 연결하는 선택적 연결 계층이다.
  - 안정성 핵심 로직을 별도로 복제하거나 소유하지 않는다.

- **Nerve+**
  - Pulse 연동 기능과 운영 편의를 추가하는 상위 제품 계층이다.
  - Nerve Core의 안정성 핵심을 대체하거나 별도의 호환 상위판으로 재정의하지 않는다.

---

## 2-5. Iris

### 정체성

Iris는 사용자 표시용 의미 정보를 오프라인에서 확정·정적화하고 런타임에서 조회·표시하는 구조다.

### 하는 일

- `Recipe`, `Right-click`, `Static capability`와 외부 생산 산출물을 Iris 입력 계약에 맞게 정규화한다.
- 정규화된 입력과 오프라인 생산 경로가 제공한 사실·결과 상태를 각 정보 생산 책임의 입력으로 공급한다.
- 런타임에서 직접 관찰해야 하는 PZ 사실은 읽기 전용으로 소비하고 새로운 의미 판단을 추가하지 않는다.

### 정보 구조

Iris의 정보 모델은 다섯 계층으로 구분한다.

계층 번호는 정보의 종류와 표시 위치를 구분하기 위한 것이며, 의미 권위의 서열이나 생산 파이프라인의 처리 순서를 뜻하지 않는다. 한 계층의 정보만으로 다른 계층의 사실 자격이나 내용을 자동으로 생성하지 않는다.

1. **1계층 - 바닐라 툴팁 계층**
   - PZ가 기본 제공하는 아이템 정보로, Iris 정보와 함께 사용자가 확인하는 기준 정보층이다.

2. **2계층 - 주 소분류 / 카테고리 계층**
   - 아이템의 기본 탐색 의미와 `Browser`의 탐색 기준점을 제공한다.
   - `primary_subcategory`는 탐색 기준점이며 Layer 3 설명을 자동 생성하는 의미 원천으로 사용하지 않는다.

3. **3계층 - 용도·개요 설명 계층**
   - 확인된 근거가 있는 아이템의 복수 용도 맥락·맥락별 역할·기능·효과·상태·조건·제약·획득 정보를 typed fact로 보존하고 사용자가 이해할 수 있는 설명으로 제공한다.
   - exact case-sensitive FullType 하나는 대표 용도나 대표 역할 없이 `0..N`개의 Layer 3 facts를 가질 수 있다.
   - semantic fact, provenance, investigation/coverage, approved expression과 surface projection은 서로 다른 축이다.
   - 아이템과 관련된 모든 행동이나 조리법을 열거하는 계층은 아니다.

4. **4계층 - 상호작용 정보 계층**
   - `Recipe`, `Right-click`, `EvolvedRecipe` 관계, 요구조건, 사용 맥락 등 아이템과 연결된 상호작용 정보를 구조화한다.

5. **5계층 - 내부 정보 계층**
   - PZ 내부 아이템 정보와 Iris 내부 분류·처리 정보를 담는다.
   - 사용자 설명을 대신하지 않으며 필요한 경우 사용자 표시 정보와 분리된 메타 영역에 표시한다.

### 근거 모델

Iris의 근거 모델은 사실의 관찰 경로와 그 경로에서 얻은 정보를 구분하기 위해 다음 네 개념을 사용한다.

- **원천**: 사실을 관찰한 경로. `Recipe`, `Right-click`, `Static capability` 등이 이에 해당한다.
- **행동**: 메뉴 노출, 클릭 경로, 행동명 등 실행 표면에서 관찰되는 정보.
- **결과 상태**: 해당 아이템이 없으면 성립할 수 없는 결과 상태.
- **근거**: 원천을 통해 관찰된 사실·결과 상태를 규칙이 소비할 수 있도록 정규화한 정보.

규칙은 원천이나 행동 자체가 아니라 정규화된 사실·결과 상태의 근거를 소비한다. 행동은 원천을 확인하는 데 사용할 수 있지만 그 자체로 정식 근거가 되지 않는다.

표시용 문자열은 그 자체로 근거 원천이 아니며, 기존 사실에서 새로운 의미를 만들어 근거로 추가하지 않는다.

기능 범주나 유형의 존재는 보조 단서로 사용할 수 있지만, 그 부재를 곧바로 부정 근거로 사용하지 않는다.

자동 근거 경로로 정규화할 수 없지만 확인 가능한 근거가 존재하는 예외는 명시적인 수동 재정의 경로로 분리한다. 수동 재정의도 근거 요구를 대체하지 않는다.

### 식별자 구조

Iris의 의미 생산, 정적 투영, 런타임 조회와 탐색은 동일한 정확 일치 아이템 식별자를 기준으로 연결한다.

- 정확 일치 아이템 식별자는 의미 정보와 런타임 소비 경로를 연결하는 기준 식별자다.
- 정규화된 식별자는 검색과 충돌 진단 같은 보조 처리에만 사용하며 의미 권한이나 기준 식별자를 대체하지 않는다.
- 표시명, 언어별 문자열과 검색용 표현의 변화는 기준 아이템 식별자를 변경하지 않는다.

### 책임 구조

Iris는 의미 원천 권한, 정보 생산, 의미 준비, 의미 구성, 콘텐츠 채택, 산출물 생성, 런타임 호환성 검증, 설치, 표시 투영, 오프라인 도구, 런타임 표시와 패키지 투영을 서로 다른 책임 영역으로 구분한다.

각 영역은 자신이 소유한 판단과 상태만 관리하며, 한 영역의 산출물이나 검증 결과가 다른 영역의 권한을 자동으로 획득하지 않는다.

Layer 3의 주요 생산·적용 경로는 다음과 같다.

```text
정식 사실 + 출처 이력
-> 원천 결속 역할 자료
-> 의미 구성
-> 비활성 의미 후보
-> 소유자 승인 채택
-> 결정적 완전 생성
-> 런타임 호환성 검증
-> 불변 생성물 설치
-> 단일 현재 생성물 포인터
-> 패키지 투영
-> 런타임 조회 / 표시
```

- **의미 원천 권한**
  - 정식 사실과 출처 이력이 의미 원천 권한을 소유한다.
  - Iris 내부 또는 외부의 오프라인 생산자가 만든 정보는 Iris 입력 계약을 거쳐 정식 원천으로 채택되기 전까지 Iris의 의미 권한을 획득하지 않는다.

- **분류 / 규칙**
  - 사실, 결과 상태와 분류를 확정하는 의미 분류 책임을 소유한다.

- **Layer 3 의미 준비**
  - 정식 사실과 출처 이력을 Layer 3 의미 구성이 소비할 수 있는 원천 결속 typed facts와 investigation state로 분리한다.
  - 복수 `use_context`, context-local `context_role`, direct function/effect, state, fact-local condition/constraint와 acquisition result를 대표 선택 없이 보존한다.
  - acquisition은 모든 current Layer 3 대상에서 조사해야 한다. Resolved는 acquisition 축 완료만 뜻하며 item 전체 investigation 완료를 단독으로 보장하지 않고, unresolved와 uninvestigated는 item investigation-complete가 아니다.
  - 원천 식별자와 출처·변환 이력을 보존하며 준비 단계의 상태 메타데이터 자체를 의미 원천으로 사용하지 않는다.

- **`DVF System`**
  - Iris Layer 3의 의미 구성과 비활성 의미 후보 생산을 소유한다.
  - Layer 3 의미 준비 단계가 제공한 원천 결속 자료를 소비한다.
  - profile은 investigation/composition/first-contact axis scope를 제공할 수 있지만 importance·frequency·ordinal·profile label로 대표 fact·role을 선택하거나 semantic priority를 부여하지 않는다. S2 fact 결합·KO/EN 표현·omission tracking은 아래 L3-05 expression authority가 소유하며, S1/S3/S4와의 4줄 구성·실제 표시 통합은 L3-06 책임이다.
  - 의미 책임은 채택 이전의 후보 생산에서 끝난다.

- **`QG`**
  - Iris Layer 4의 상호작용 정보 생산과 검문을 소유한다.
  - Build 41 `EvolvedRecipe`는 fixed Recipe를 확장한 레시피가 아니라 exact item `FullType`과 음식 유형을 잇는 별도 typed relation으로 생산한다. Active item-property 참여는 `ingredient`/`spice`, definition `BaseItem` 참여는 `base_item`이며 같은 FullType에서도 독립적으로 공존한다. 역할과 조건은 관계에 귀속하고 근거 없는 결과물·navigation을 만들지 않는다. 내부 food type ID와 계층명은 identity/provenance에만 남기며 사용자 행은 locale 음식 라벨·역할·조건만 표시한다.

- **오프라인 도구**
  - Iris의 오프라인 생성과 검증을 실행할 도구를 제공한다.

- **채택 경계**
  - 명시적으로 승인된 의미 후보를 정식 생성 입력으로 채택하는 승인과 입력 결속을 소유한다.
  - 승인되지 않은 후보는 생성 입력으로 전달하지 않는다.
  - 채택은 런타임 산출물을 직접 만들거나 런타임 가시성을 변경하지 않는다.

- **Layer 3 생성**
  - 정식 생성 입력을 결정적이고 무상태인 경로를 통해 불변 런타임 산출물로 만든다.
  - 생성된 산출물이나 설치 상태를 생성의 의미 입력으로 역유입하지 않는다.

- **런타임 호환성 검증**
  - 생성된 산출물이 Iris 런타임 계약과 호환되는지를 생성과 독립된 경계에서 검증한다.

- **설치 경계**
  - 검증된 불변 생성물을 설치하고 단일 현재 생성물 포인터를 통해 런타임에서 보이는 생성물을 선택한다.
  - 설치된 생성물은 제자리에서 수정하지 않으며 설치 과정에서 원천 사실이나 설명 의미를 변경하지 않는다.

- **표시 투영**
  - 확정된 의미 정보와 상호작용 상태를 언어 설정, 표시 순서와 런타임 탐색 구조 등 사용자 표시 형태로 투영한다.
  - 현재 공개 정보 경계는 현재 생성물에서 사용자 표시가 승인된 정보 집합을 뜻한다.
  - 언어별 표시는 동일한 의미 식별자와 현재 공개 정보 경계에 결속된다.

- **패키지 경계**
  - 현재 생성물 포인터가 선택한 런타임 생성물과 유지해야 하는 공개 호환 표면을 배포 패키지에 투영한다.
  - 하나의 패키지에서 서로 다른 생성물의 런타임 자료가 혼합되지 않도록 경계를 유지한다.

- **`Menu` / `Tooltip`**
  - 확정된 정보를 각 표시 구조에 맞게 소비한다.
  - Menu Layer 3는 accepted facts와 resolved acquisition을 expanded detail로 보존한다. Tooltip S2는 같은 fact authority를 profile별 first-contact axis에 따라 낮은 해상도로 투영하며 represented fact와 truth-changing dependency reference를 유지한다.
  - S2는 importance·frequency·efficiency·첫 ordinal 또는 profile label로 대표 fact를 선택하지 않으며 runtime에서 요약·축약·재선택·추론하지 않는다.
  - `Browser`, `Detail ViewModel`, `Wiki` 관련 구성요소는 `Menu` 내부 표시 구조를 구성한다.
  - 런타임 소비자는 표시·탐색·배치와 UI 상태를 담당한다.

Layer 3 successor semantic contract의 current readpoint는 SHA-256 `6735c3eadafaf4c4fd51ae56c8d0748d32903ee996d53ed43bca38822cf0932a`인 `Iris/_docs/authority/dvf/layer3_successor/contract_manifest.json`이다. 이는 contract-only adoption이며 current corpus, generation, runtime과 package는 별도 migration 전까지 predecessor-compatible product로 유지한다.

이 readpoint는 human contract, `contract.json`, `casebook.json`, `predecessor_inventory.json`의 네 member를 묶으며 기존 current authority manifest와 route index에서 연결한다. 별도 producer나 runtime data path를 추가하지 않는다. 위 multi-fact·profile·Menu/S2 규칙은 채택된 successor 설계 계약이며, 현재 제품이 이미 그 표현·투영을 구현했다는 뜻은 아니다.

DVF-L3-01의 focused contract test는 계약 구조·사례·readpoint 결속과 보호 대상의 불변성을 검사한다. 실제 corpus의 의미 조사 완료를 판정하는 validator나 새로운 production validation authority가 아니다. 완료·검증 상세는 [단일 closeout](iris_dvf_layer3_multi_meaning_information_resolution_successor_contract_closeout.md)을 따른다.

DVF-L3-02는 2026-09-04 current investigation authority로 채택을 완료했다. Readpoint는 `Iris/_docs/authority/dvf/layer3_investigation/manifest.json`이다. `Iris/tooling/src/iris_tooling/domains/layer3/investigation.py`는 원본 script/Recipe/moveable predicate로 복수 프로필을 적용하고 `(FullType, axis_id, scope_ref)`별 contributor union, pending scope, gap과 item 완료를 계산한다. Global acquisition은 한 번만 요구하며 획득 해결은 item 전체 완료의 충분조건이 아니다. Native Type 배제는 해당 native channel만 닫고 다른 행동 가능성은 direct/gap 질문에 남긴다.

이 authority는 10개 프로필·5개 axis의 조사 질문/first-contact 기준과 2,105개 실제 application을 묶는다. `contract.json`은 정의·source/routing 규칙을, `evidence.jsonl`은 exact item별 원본 관찰·근거를, `applications.jsonl`은 적용 결과·필수 축·pending/gap/완료·first-contact 요구를 소유한다. Manifest는 이 세 machine member와 human contract, 상속 계약과 target source identity를 결속한다. 기존 current authority manifest와 route index가 이 readpoint를 가리킨다.

`--repository-root . build layer3 investigate` 진입점은 investigation root의 evidence/application/manifest만 작성한다. 기존 compose profile 선택기와 별개의 오프라인 책임이며 composer·publisher·Lua runtime 경로를 호출하지 않는다. 결과 소비자는 상속 bound JSON의 allowed kinds·negative binding·resolved 조건을 해석하고, 별도 adopted authority의 accepted result 및 exact subject/provenance가 없는 terminal claim을 거부한다. Source 관찰에서 semantic/acquisition fact를 생산하지 않는다.

Item 완료는 `scope_determined AND every_required_axis_terminal AND acquisition_state == resolved`다. L3-02 baseline에는 accepted semantic/acquisition 결과가 없으며 이를 보존한다. L3-03 단독 소비는 별도 비획득 결과만 공급하므로 acquisition이 미조사이고 item complete는 0개다. 현재 L3-04 결합은 acquisition 미수행을 0으로 닫지만 다른 open 질문이 남아 item complete는 여전히 0개다. First-contact obligation은 fact 미해결에도 남고 전역 acquisition 문장이나 대표 의미를 선택하지 않는다. 표현·투영은 아래 DVF-L3-05 authority로 채택됐으며 runtime/current product adoption은 DVF-L3-06의 책임이다. 기존 successor bundle·product corpus·composer·Menu/Tooltip·Lua·package와 product locator는 보존했다.

최종 adoption G1은 exit `0`으로 통과했다. 단일 focused source의 계약·전체 application·readpoint·명시적 보호 경계 검증이며 source 전수 의미 정확성·문장 품질·runtime/package readiness의 검증이 아니다. 정확한 명령·결과·잔여는 [DVF-L3-02 closeout](iris_dvf_layer3_multi_profile_investigation_completion_first_contact_closeout.md)에 기록했다. 임시 baseline과 작성 helper는 제거했고 별도 validator나 영구 validation authority로 남기지 않았다.

DVF-L3-03의 별도 result producer는 `iris_tooling.domains.layer3.semantic_results`이며 `build layer3 semantic-results --output <repository-local candidate directory>`로 동작한다. Source reader와 명시적 interpretation은 raw 선언·callback·action을 구별하고, `semantic_model`은 typed facts/provenance/results/partial bindings를 검사·소비한다. L3-02의 baseline writer·정의 revision은 그대로다. Readpoint는 `Iris/_docs/authority/dvf/layer3_semantic_results/manifest.json`이고 현재 상태는 **adopted — 최종 G1 exit 0**이다. 채택 판정은 [L3-03 closeout](iris_dvf_layer3_semantic_investigation_question_results_closeout.md)과 current route가 소유한다.

Derived application은 corpus에 보존한 structured 입력을 같은 resolver로 계산한다. Partial facts를 open question에 연결하며 terminal fact로 승격하지 않는다. L3-03 단독 소비의 acquisition은 미조사이며, 현재는 아래 L3-04 독립 결과를 결합할 수 있다. 결합 후에도 item complete는 0이다. KO/EN 표현·S2는 아래 L3-05에서 off-live 채택을 완료했고, runtime/product adoption은 L3-06에 남는다. 이 corpus의 candidate lifecycle bytes는 G1 이후 바꾸지 않고 adopted loader가 성공한 readpoint의 논리 envelope를 제공한다.

이 경로의 책임은 다음과 같이 나뉜다. 모두 repository offline Python tooling이며 Iris의 Lua runtime 의존성은 추가하지 않는다.

| 구성요소 | 책임 |
|---|---|
| `source_reader.py` | 반복 선언·clause·case-sensitive FullType을 보존하고 raw 참여·group·선택 item predicate를 관찰 |
| `interpretations.py` | 실제 검토한 callback 집합과 caller→action 의미·조건·engine handoff를 기록; 함수 발견만으로 의미 조사 완료 처리 금지 |
| `semantic_results.py` | source-bound observation/provenance에서 사실·질문 결과·pending·key lineage와 partial binding 생산 |
| `semantic_model.py` | Content-derived fact identity, context/qualifier 참조, 전체 structured payload의 무결성과 소비 |
| `investigation.resolve_item()` | L3-02 질문 정의와 contributor union을 유지하며 별도 결과·partial binding을 application으로 계산 |
| `layer3_semantic_results/manifest.json` | Corpus·producer·human contract·G1 source와 definition readpoint 결속; current route와 성공 closeout이 채택 상태 소유 |

채택 corpus는 2,105 target, source binding 216개, accepted fact 4,233개와 non-acquisition 질문 9,982개를 포함한다. Fact ID는 semantic payload와 context/dependency를 반영하며 source locator·review timestamp·registry metadata는 identity에서 분리한다. 의미 정정은 새 ID와 의존 참조 재결속을 요구한다. Question key는 `(item_id, axis_id, scope_ref)`이고 revision은 metadata다. 별도 대용량 application 복제 없이 같은 corpus의 입력을 사용한다.

G1은 최종 subject 전체를 한 번 소비해 `exit 0`을 확인했다. 이 결과는 scoped N/A·unresolved·partial contribution과 명시적 보호 경계를 검사한 것이며 전수 의미 정확성·실게임 동작·package readiness 보증은 아니다. `.tmp/semantic/`의 작성 helper·baseline·실행 로그는 플랫폼 정책상 삭제가 보류된 일회성 자료로, runtime 의존성·adopted authority·통상 재사용 검사의 필수 입력이 아니다.

### 독립 획득 결과와 결합 소비

DVF-L3-04는 `layer3/acquisition_sources.py`의 source/consumer 조사, `acquisition_results.py`의 독립 corpus·admission·manifest loader, `acquisition_consumption.py`의 결합 소비로 나뉜다. 기존 L3-03 manifest가 결속한 모듈을 수정하지 않는다. 별도 명령 `python -m iris_tooling.domains.layer3.acquisition_results --repository-root . --output <empty repository-local acquisition directory>`는 composer fallback이나 product writer를 호출하지 않는다.

Adopted readpoint는 `Iris/_docs/authority/dvf/layer3_acquisition_results/manifest.json`이다. 여섯 family의 공유 원본 관찰·구체적 consumer 해석·item별 attempt가 12,630 pair에 연결된다. 문자열 hit/miss만으로 조사 완료를 허용하지 않으며 unreviewed trace, 미수행 pair와 source-member 누락을 거부한다. 확정 경로의 route/조건은 semantic ID를 구성하고 같은 의미의 provenance는 병합한다. Predecessor material 8,278건은 source-bound lead-only 자료로 남겨 truth 근거와 분리한다.

`acquisition_consumption.load(root, acquisition_manifest_binding, mode='adopted')`는 실제 L3-04/L3-03 loader와 L3-02 revision 1을 읽고 기존 resolver에 결과·partial bindings를 함께 전달한다. 반환값은 두 corpus/readpoint, fact-local 조건·provenance·open questions와 2,105 application이다. Candidate/adopted 혼합과 검증된 readpoint를 거치지 않은 임의의 in-memory adopted 소비를 거부한다. Acquisition은 resolved 1,025 / investigated_unresolved 1,080 / not_investigated 0이며 accepted positive facts 1,057개, negative 0개다. 비획득 projection과 item complete 0을 보존한다.

단일 G1의 candidate 검사와 실제 adopted 연결이 모두 exit 0이다. Manifest의 candidate bytes와 성공 subject를 current route가 결속하며 source policy/required registry의 기존 entry는 보존한다. 자세한 검증 범위와 원본 해석의 잔여 한계는 [acquisition closeout](iris_layer3_acquisition_closeout.md)을 따른다. `.tmp/acquisition/`의 baseline·이전 candidate·캐시는 일회성 실행 보조 자료이며 adopted 소비나 정규 validator의 입력이 아니다.

### Layer 3 expression readpoint — DVF-L3-05

`iris_tooling.domains.layer3.expression_results`는 adopted `acquisition_consumption.load()`의 네 입력과 5,290 qualified facts를 사용해 KO/EN expanded description과 compact S2를 만든다. `expression_rules`가 프로필별 조합과 semantic 표현을, `acquisition_expression`이 획득 경로별 표현을 소유한다. Profile scope는 모든 기여자를 함께 보존하며 의미 우선순위를 만들지 않는다. 조건은 claim에 붙고 context-local role과 residual facts를 보존한다.

Readpoint는 `Iris/_docs/authority/dvf/layer3_expression/manifest.json`이며 현재 SHA-256은 `cff8acd83715e70c6e7b82553d47e538c7f75131437491d7cf6781875f5435be`다. `load(root, binding, mode='adopted')`가 입력/member/rule/review/표현/ref/receipt를 검사하고 독립 description contract를 반환한다. `descriptions.json`은 fact/provenance, 10,580 fact-locale expression 대응, expanded/S2/omission/upstream obligation을 제공한다. 1,057 acquisition facts는 두 locale의 expanded에 모두 포함된다.

`description_projection.py`가 expanded 문장을 재사용하거나 자르지 않고 compact first-contact proposition을 독립적으로 합성한다. First-contact obligation에 결속된 accepted 기능·효과·활동·역할을 보존하고, 일반 실행 조건은 `detail_qualifier_refs`로 추적한다. 오염수·학습 범위 등 실제 첫 이해 조건만 짧게 표현한다. Acquisition은 사용자-facing 장소·방법·범위를 설명하고 내부 가중치·무작위 수식·등록/전달 절차는 원래 payload에만 보존한다. 선행 `0abd0d…`는 해상도 결함으로 superseded이며 receipt의 선행 이력과 closeout에 보존한다. 교정된 exact 후보에 동일 Gate를 한 번 다시 귀속했다.

Compact S2는 locale별 1,280개 item에 존재하고 825개 item에는 없다. KO p50/p95/max 12/39/44자와 EN 27/83/104자는 profile 합성의 관찰 결과이며 schema limit이나 semantic selection threshold가 아니다. 빈 S2는 accepted first-contact contributor가 없는 upstream 상태를 보존한 것으로, runtime consumer는 predecessor prose·다른 계층 output·번역 fallback으로 채우지 않는다. Menu expanded는 이와 독립적으로 locale별 accepted fact set 전체와 1,057 acquisition facts를 보존한다.

2026-09-05 **해상도 교정본 complete / adopted (off-live)**. 교정 후보의 단일 focused Gate는 `1 passed in 14.17s`, exit `0`이며 exact candidate를 유지한 채 adoption 명령 안에서 adopted readback도 exit `0`으로 완료했다. 독립 `adoption.json`의 `superseded_result`는 선행 후보 이력을 보존하며 그 PASS를 교정본에 승계하지 않는다. 기존 current registry·route·Lua·product writer를 호출하거나 변경하지 않는다. Menu/Tooltip runtime과 S1/S3/S4의 실제 통합은 L3-06이다. [Consumer contract](iris_layer3_expression_contract.md), [closeout과 validation ceiling](iris_layer3_expression_closeout.md).

### 오프라인 도구 실행 구조

Iris의 오프라인 도구는 각 영역의 의미 판단과 이를 실행하는 공통 조정을 분리한다. 오프라인 도구는 저장소 측 생성·검증을 수행하며 런타임 의존성을 만들지 않는다.

```text
영역 소유 입력 / 자료 / 판정
-> PhaseInput / PhaseOutput
-> 얇은 PhaseRunner
-> CanonicalSemanticResult
 + ExecutionEnvelope
-> 영역 어댑터 / 정식 CLI 투영
```

- 각 영역 소유자가 생성·검증 입력, 자료와 의미 판정을 소유한다.
- `PhaseRunner`는 단계 의존 순서, 동일 실행 안에서의 결과 전달과 실행 관찰의 연결을 담당한다.
- `CanonicalSemanticResult`에는 동일한 입력과 판단에서 안정적으로 유지되어야 하는 의미 결과를 둔다.
- `ExecutionEnvelope`에는 특정 실행에만 귀속되는 환경, 시간, 프로세스와 경로 관찰을 분리해 둔다.
- CLI와 실행기는 영역 소유자의 기존 판단을 호출·투영하는 어댑터다.

#### 현재 저장소 / 과거 보관소 경계

현재 빌드·검증·패키징 경로와 과거 재현 자료의 보관 경로는 서로 분리한다.

```text
현재 저장소
-> 현재 소스 / 런타임 / 도구 / 계약
-> 현재 필요한 검증 자료
-> 빌드 / 검증 / 패키지

과거 보관소
-> 과거 준비 자료 / 재현 증거 / 이전 산출물
-> 명시적 검증 / 복원
```

- 현재 명령과 산출물 생성은 과거 보관소 없이 성립해야 한다.
- 현재 동작에 필요한 자료와 과거 재현만을 위한 자료는 저장 수명과 의존성을 구분한다.
- 과거 보관소는 현재 실행 경로의 암묵적인 입력이나 대체 경로로 사용하지 않는다.
- 과거 자료가 필요한 경우 명시적인 검증·복원 경로를 통해서만 접근한다.

#### 저장소 책임 분리

오프라인 도구와 검증 자료는 실제 책임에 따라 실행·환경, 소스 분석, 산출물 관리, 기준점, 시나리오와 테스트 보호 조건 영역으로 분리한다.

- `Iris/validation/execution/`: 검증 실행과 실행 환경
- `source_analysis/`: 소스 조사·분석
- `artifacts/`: 산출물 저장·복원
- `baseline/`: 기준점 채택
- `scenarios/`: 시나리오 모델
- `test_coverage/`: 테스트 보호 조건과 범위 비교

### `Tooltip` 정적 투영 구조

`Tooltip`의 오프라인 투영은 Layer 2 / Layer 3 / Layer 4의 기존 의미 권한과 런타임용 정적 생성 사이의 경계다. 현재 오프라인 구현은 `iris_tooling.domains.tooltip_static_data_projection`이 소유한다.

```text
Layer 2 / Layer 3 / Layer 4 승인 의미 산출물
-> Tooltip 적용 가능성 / 선택 투영
-> 순서가 고정된 슬롯 식별자
-> 승인된 표시 내용
-> 고정 투영 확정
-> 결정적 정적 생성
-> 런타임 정적 자료

고정 투영
+ 승인된 대체 표시 입력
-> 결정적 사전 생성 변형
-> 런타임 변형 자료
```

- 투영은 각 계층에서 `Tooltip`에 적용 가능한 승인 정보를 선택하고 표시 슬롯과 의미 식별자로 변환한다.
- Layer 2는 분류 권한이 표시 가능한 카테고리와 주 소분류를 제공할 때만 해당 슬롯을 만든다. 적용할 정보가 없으면 자리 채움 정보를 만들지 않고 이후 슬롯을 앞당겨 배치한다.
- Layer 3와 Layer 4의 사실, 승인된 부재 또는 상호작용 상태는 해당 의미 소유자가 확정한 상태를 소비한다.
- 슬롯 선택이 끝나면 슬롯 순서, 의미 식별자와 승인된 표시 내용을 고정하며 정적 생성은 이 투영을 기계적으로 산출한다.
- 생략된 슬롯은 정적 생성 단계에서 새로운 의미적 부재나 표시 의미로 재해석하지 않는다.
- 필요한 대체 표시는 고정 투영과 이미 승인된 의미 입력을 바탕으로 오프라인에서 완성된 배열로 사전 생성한다.
- 런타임은 사전 생성된 기본 표시나 변형 표시를 선택할 뿐 슬롯을 다시 구성하지 않는다.
- 런타임 정적 자료에는 표시에 필요한 식별자와 완성된 표시 내용만 투영하며 감사, 교정, 준비 상태, 소유자 작업 흐름 등 오프라인 관리 메타데이터를 포함하지 않는다.

### 런타임 적재 / 조회 구조

Iris 런타임 자료는 소비자가 요구하는 시점에 필요한 범위만 적재한다. 일반 요청 기반 적재와 공개 호환성을 위한 전체 적재는 서로 다른 경로로 유지한다.

```text
Browser
-> 최초 열기
-> Browser 자료 구성

StaticData 소비자
-> 최초 요청
-> 필요한 정적 자료 적재
-> 세션 캐시

Layer 3 소비자
-> 현재 생성물 포인터
-> 탐색 메타데이터
-> 포인터가 선택한 생성물 자료
-> 세션 캐시

Tooltip 소비자
-> 최초 요청
-> 고정 정적 자료
-> 선택적 사전 생성 변형 자료
-> 정확 일치 아이템 / 언어 설정 조회
-> 완성된 표시 뷰

직접 호환 표면
-> 현재 생성물 포인터
-> 포인터가 선택한 생성물 전체 적재
-> 기존 공개 계약
```

- 일반 런타임 경로는 시작 시 모든 런타임 자료를 미리 적재하지 않고 각 소비자의 요청에 따라 필요한 자료를 불러온다.
- `Browser`는 처음 필요한 시점에 자신의 런타임 자료를 구성하며 다른 소비자의 정적 자료 적재와 결합하지 않는다.
- Layer 3 일반 조회와 직접 호환 표면은 동일한 현재 생성물 선택을 따라 비활성 생성물의 자료가 현재 런타임 가시성에 섞이지 않도록 한다.
- `Tooltip`의 정적 자료 조회는 현재 `IrisTooltipStaticDataLookup`이 담당하며, 기준 아이템 식별자와 요청 언어를 사용해 오프라인에서 완성된 표시 내용을 찾는다.
- 사전 생성된 변형이 존재하면 기본 투영과 같은 아이템·투영 식별자에 결속된 완성된 뷰만 조회 대상으로 사용한다.
- 런타임 조회는 정상적으로 존재하는 값, 정상적인 부재와 조회 자료의 결함을 구분한다.
- 정상적인 희소 조회 실패는 호환성 전체 적재나 의미 대체 경로를 유발하지 않는다.
- 잘못된 자료, 식별자 불일치 또는 탐색·조회 결함을 기존 의미 추론이나 별도의 구형 의미 경로로 보완하지 않는다.
- 전체 생성물 적재는 유지되는 공개 호환 계약을 위한 별도 경로이며 일반 요청 기반 적재의 대체 경로로 사용하지 않는다.

### 런타임 상태 / 호환 구조

Iris 런타임은 외부에 유지되는 호환 표면과 내부 상태·사실 모델, 런타임 소비자를 분리한다.

```text
지원 API / 공개 모듈 호출 표면
-> 얇은 공개 어댑터 / 호환 어댑터
-> 명시적 런타임 상태 / 읽기 전용 사실 모델
-> 렌더러 / 위젯 / 런타임 소비자
```

- 유지되는 공개 계약은 얇은 공개 어댑터 또는 명시적인 호환 어댑터를 통해 내부 핵심 구조에 연결한다.
- 호환 어댑터는 독립적인 의미 자료를 만들거나 내부 상태를 복제·재해석하지 않는다.
- `Browser`와 `Menu` 상세 정보는 선택, 생성물, 언어 설정과 UI 상태를 명시적으로 관리하며 내부 자료 구조의 존재 여부 자체를 상태로 사용하지 않는다.
- 동일한 의미 정보를 사용하는 `Menu` 내부 소비자는 공통 읽기 전용 사실 모델을 소비한다.
- 내부 자료 표현은 필요에 따라 변경하거나 최적화할 수 있지만 공개 호환 형식과 의미는 유지한다.
- 공개 결과는 내부 변경 가능 상태를 직접 노출하지 않으며 외부 호출자의 변경이 내부 상태에 역영향을 주지 않도록 격리한다.
- 생성물 또는 언어 설정에 귀속된 캐시와 파생 상태는 해당 소유자가 변경되면 함께 폐기한다.
- 인스턴스 범위 상태는 아이템 식별자 단위의 전역 변경 가능 결과 상태로 승격하지 않는다.
- `Tooltip`은 하나의 열림 상태 동안 선택한 아이템 식별자와 사전 생성 표시 뷰를 인스턴스 상태로 유지한다. 열림 상태가 끝나거나 아이템 맥락이 바뀌면 해당 상태를 폐기한다.

### 런타임 표시 구조

런타임 표시는 확정된 의미 산출물과 완성된 정적 표시물을 `Menu`와 `Tooltip`의 표시 구조로 투영한다.

오프라인에서 생성된 의미 정보의 언어별 표시는 동일한 의미 원천과 현재 공개 정보 경계에 결속된 사전 생성 자료를 사용한다.

```text
현재 의미 정보 / 공개 정보
-> 언어별 표시 자료
-> Menu / Tooltip 표시
```

- 런타임은 요청 언어에 대해 이미 완성된 표시물을 소비한다.
- 한 언어의 원문 표시를 다른 언어의 의미 대체 경로로 사용하지 않는다.
- 이전 생성물이나 오래된 언어별 자료가 남아 있더라도 현재 공개 정보 경계보다 넓은 정보를 표시하지 않는다.

#### `Menu` 표시

```text
선택 아이템 + 언어 설정
-> Detail ViewModel
-> 적용 가능한 Layer 2 투영
 + Layer 3 투영
 + Layer 4 상호작용 투영
-> Menu 상세 표시
```

- 분류에서 파생된 표시 순서와 색인은 `Menu`의 탐색 구조를 구성한다.
- Layer 3 `Menu` 투영은 승인된 기본 설명과 같은 의미 원천에 결속된 추가 맥락·획득 정보를 조합할 수 있다.
- Layer 4 투영은 `QG`가 확정한 상호작용 상태를 표시 가능한 행과 탐색 상태로 변환한다. `EvolvedRecipe` lookup은 fixed Recipe/Right-click collection을 다시 쓰지 않고 Detail ViewModel에서 별도로 읽어 같은 표시 경계에 합성한다. Fixed collection의 total·density·visible rows는 Evolved 관계 수와 독립적으로 보존하고, Evolved collection은 자체 density·expanded·query state를 가진다.
- Evolved 저밀도 투영은 target과 행동을 한 compact flat row에 표시한다. 고밀도 투영은 locale별 역할·조건 action을 group heading으로, target label을 child로 표시한다. Group과 child는 각 relation의 `canonical_ordinal`에서 순서를 얻고 모든 exact identity와 원 relation count를 보존한다. 검색은 relation을 먼저 match한 뒤 일치한 child만 regroup하며 빈 group을 만들지 않는다.
- Food-type locale projection은 raw `ContextMenu_EvolvedRecipe_*` fragment가 아니라 exact ID별 standalone target registry와 role/condition template을 결합해 행동 의미가 완결된 KO/EN 문장을 만든다. Recipe source section state와 Freeform state는 별도이며, item·locale 전환 시 이전 relation/query를 새 모델에 상속하지 않는다. `Iris_Interaction_EvolvedRecipe`의 source translation과 생성 `IrisTranslationData`를 함께 유지해 사용자 surface에 KO `자유 조리` / EN `Freeform Cooking`을 표시한다.
- Freeform text entry는 Detail content child가 아니라 Browser-owned persistent UI child다. Detail 결과를 재구성해도 같은 engine text box와 IME focus를 유지하며, Detail scroll은 entry의 위치와 viewport 가시성만 동기화한다. Fixed Recipe 제작 UI 이동은 현재 locale에 맞춰 KO translated name 또는 original name을 filter input으로 선택한다.
- Build 41 current runtime은 자동 검증과 사용자 실제 PZ 대표 관찰 뒤 guarded adoption을 통과한 compact/grouped v7 `Iris/media/lua/client/Iris/Data/IrisEvolvedRecipeLookup.lua`이며 SHA-256은 `02c6d4b97a21285a393b873582dd9fa80bc6b25fa91d09fc7da89e89965ef47b`이다. 이 hash와 다른 재생성 결과는 새 candidate이고 자동으로 current가 되지 않는다.
- 이전 v6 SHA-256 `0b86cb8a2638df627f94bbb27af759b9b46e54c55081504da04aefcc8e353088`은 실제 PZ 관찰과 당시 adoption을 통과한 predecessor지만 v7 current와 동시에 runtime authority를 갖지 않는다.
- PZ runtime은 채택된 Lua lookup만 읽는다. Source-accounted owner JSON과 저장소 밖 candidate/package는 오프라인 생성·관찰·채택 입력이며 런타임 의미 입력으로 역유입하지 않는다.
- `Browser`, `Detail ViewModel`, `Wiki` 관련 구성요소는 `Menu` 내부 표시 구조를 구성한다.

`Menu`가 PZ 런타임에서 직접 읽는 사실의 표시 경로는 다음과 같이 분리한다.

```text
PZ에서 관찰 가능한 자료
-> 사실 판독기
-> 불변 상세 모델
-> 공통 표시 정책
-> Detail ViewModel / 렌더러
```

- 사실 판독기가 PZ 엔진 자료 접근을 소유한다.
- 모델 조립기는 읽은 사실을 불변 상세 모델로 결합한다.
- 단위, 가시성, 텍스트 배치 등 공통 표시 규칙은 표시 정책이 소유한다.
- 긴 `Menu` 내용의 줄바꿈과 스크롤은 표시 계층에서 처리하며 의미 자료 자체를 수정하지 않는다.

#### `Tooltip` 표시

```text
아이템 + 언어 설정
-> 완성된 정적 기본 / 변형 뷰
-> 물리적 텍스트 배치
-> Tooltip 렌더러
```

- `Tooltip` 렌더러는 오프라인에서 완성된 논리 행을 소비한다.
- 물리적 줄바꿈과 화면 배치는 엔진에서 확인 가능한 공간과 글꼴 측정을 기준으로 표시 단계에서 계산한다.
- 배치 과정은 논리적 내용과 아이템 식별자를 변경하지 않는다.
- 표시할 수 없는 런타임 배치 상태를 의미 대체 경로나 새로운 설명 생성으로 보완하지 않는다.

### `Browser` 검색·탐색 구조

`Browser` 검색은 생성물·언어 설정에 귀속된 동일한 아이템 스냅샷을 기반으로 하며 검색 비교, 질의 상태와 UI 탐색을 서로 분리한다.

```text
아이템 원천
-> 검색 투영
-> 생성물 / 언어 설정 검색 스냅샷

검색 입력
-> 질의
-> 동일한 검색 스냅샷
-> 관련성 순위 결과

검색 결과
-> Browser 자료
-> 선택 / 카테고리 탐색
-> Menu 상세 정보
```

- 검색 투영은 표시 이름과 아이템 식별자에서 검색에 필요한 비교 표현을 미리 생성하되 원본 아이템과 기준 아이템 식별자를 함께 보존한다.
- 검색 투영과 질의는 동일한 생성물·언어 설정 스냅샷을 소비하며 서로 다른 검색용 아이템 집합을 만들지 않는다.
- 검색 비교 로직은 상태 없는 비교기가 소유하며 질의 상태, `Browser` 자료와 UI 상태에 중복 구현하지 않는다.
- 질의는 스냅샷 안의 후보를 관련성 기준으로 평가한다.
- 검색 스냅샷은 생성물과 언어 설정에 귀속된다.
- 변형이 존재하는 아이템은 `Browser`가 선택한 표시 대표 항목을 검색 대상으로 사용할 수 있지만 변형 식별자와 기준 아이템 구성원 관계는 보존한다.
- 검색 입력 상태와 결과 상태는 `Browser` UI에서 명시적으로 관리하며 동일한 입력의 반복 처리가 기존 선택이나 상세 정보를 불필요하게 다시 만들지 않도록 한다.
- 전체 검색 결과에서 카테고리 위치로 이동할 때는 해당 결과와 동일한 스냅샷·기준 아이템 식별자에 결속된 탐색 정보만 사용한다.
- 검색 결과에서 카테고리로 이동하는 동작은 카테고리 선택과 스크롤 상태를 변경할 수 있지만 원래 검색 질의나 결과 식별자를 다시 작성하지 않는다.
- 검색을 종료하거나 `Browser` 탐색 상태를 초기화할 때는 검색 종속 상태와 카테고리 탐색 상태의 소유 범위를 구분해 정리한다.

Layer 4 자유 조리 검색은 Browser item relevance search와 입력 처리 원칙만 공유하고 별도 relation projection에서 수행한다.

```text
Freeform 입력 버퍼
-> locale relation display의 대소문자 무시 literal 부분 일치
-> matched relation set
-> matched-only action group
-> canonical/group 순서 표시
```

- Freeform 검색은 현재 `IrisBrowserSearch`의 공백 compact key, FullType ID match, relevance tier, prefix candidate snapshot과 분류 자동 이동을 사용하지 않는다.
- Browser item 검색의 relevance 순위를 Freeform relation에 그대로 적용해 canonical/group 순서를 바꾸지 않는다. 향후 lexical matcher 일부를 공유하더라도 relation identity·ordinal·matched-only grouping은 Evolved projection이 계속 소유한다.

---

## 2-6. Frame

> 구현 상태: 설계 단계

### 내부 상태 구조

Frame은 현재 로컬 상태와 외부에서 가져온 상태를 검증·정규화한 뒤 `PackState`를 공통 내부 상태 단위로 사용한다. `PackState`의 구성과 의미는 `Philosophy.md`의 Frame 정의를 따른다.

```text
현재 로컬 상태 / 외부 공유 상태
-> 검증 / 정규화
-> PackState
-> 기준점 / 자동 복구 기록
-> 비교 / 복원 / 공유
```

- 현재 로컬 상태와 외부 공유 상태는 서로 다른 입력 경로를 가지지만 내부에서는 동일한 `PackState` 표현으로 연결한다.
- 기준점과 자동 복구 기록은 별도의 상태 모델을 만들지 않고 `PackState`를 공통 상태 표현으로 사용하며 수명과 용도로 구분한다.
- 비교는 저장된 `PackState`와 현재 상태의 구조·동일성 정보를 대조하여 차이를 산출한다.
- 복원은 저장된 상태를 기준으로 이용 가능한 모드와 설정을 재구성한 뒤 현재 상태와 저장 상태의 차이를 다시 확인하는 흐름으로 구성한다.
- 완전히 재구성할 수 없는 차이는 저장 상태를 임의로 수정하거나 숨기지 않고 미해결 차이로 유지한다.

### 입력 / 출력 경계

Frame의 외부 형식과 내부 상태 표현은 서로 분리한다.

```text
외부 공유 형식
-> 검증 / 정규화
-> PackState

PackState
-> 외부 공유 투영
-> 열린 공유 형식
```

- 외부 공유 파일은 검증을 거쳐 내부 `PackState`로 정규화한 뒤 사용한다.
- 내부 상태 표현이나 캐시는 외부 입력 자체를 권위 있는 내부 상태로 직접 사용하지 않는다.
- `.frame`은 내부 정규화·검증·캐시에 사용할 수 있는 보조 표현이며 외부 공유 계약을 소유하지 않는다.

---

## 2-7. Cortex

> 구현 상태: 설계 단계

### 정체성

Cortex는 다른 제품 영역이나 Pulse Core에 두기 부적절한 사용자 편의·가이드 기능을 격리하는 독립 제품 모듈이다.

### 하는 일

- 다른 제품 모듈의 고유 역할에 속하지 않는 사용자 편의·가이드 기능을 수용한다.
- Pulse 기반 모딩을 이해하고 사용하는 데 필요한 가이드와 보조 UX를 제공한다.
- Pulse Core의 공용 기능으로 승격할 필요가 없는 사용자 보조 기능을 격리한다.

### 하지 않는 일

- 다른 Spoke가 의존하는 공용 유틸리티나 공유 라이브러리 역할을 맡는 것
- 향후 Pulse Core로 이동할 기능을 임시로 보관하는 장소가 되는 것
- 독립 제품 영역으로 분리해야 할 기능을 편의 기능이라는 이유만으로 Cortex에 수용하는 것

---

## 2-8. Canvas

> 구현 상태: 설계 단계

### 설계 상태

Canvas의 `AssetEntry`, `ResourcePack`, `ResourceState`, 판정 책임과 입출력 원칙은 `Philosophy.md`에서 정의한다.

현재는 이를 구현하기 위한 구성요소의 책임 분리, 실행 경계와 상태·자료 흐름이 Architecture 수준에서 아직 확정되지 않았다.
