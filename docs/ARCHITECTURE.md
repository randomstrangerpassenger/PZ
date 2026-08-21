# ARCHITECTURE.md

> 상태: 초안 v0.4
> 기준일: 2026-08-10
> 상위 기준: `Philosophy.md`, `DECISIONS.md`  
> 목적: Pulse 생태계의 구조 지도, 역할 경계, 의존 방향을 고정한다.

---

# 1. 구조 원칙

## 1-1. 최상위 원칙

- Pulse는 하위 모듈을 참조하거나 의존하지 않는다.
- 하위 모듈 간 직접 참조도 금지한다.
- 하위 모듈 간 협력이 필요하면 Pulse capability 또는 SPI를 경유한다.
- 타 모드와의 호환성을 최우선으로 둔다.
- 각 모듈은 자기 역할을 고수하고, 타 모듈 역할을 침범하지 않는다.

## 1-2. 아키텍처 패턴

Pulse 생태계는 **Hub & Spoke + SPI** 구조를 따른다.

- **Hub**: Pulse Core
- **Spokes**: Echo, Fuse, Nerve family(Nerve Core / Nerve Pulse Adapter / Nerve+), Iris, Frame, Cortex, Canvas
- **확장 방식**: SPI, 공용 capability, 이벤트/레지스트리/유틸 등 Core surface

핵심은 **Core는 기반만 제공하고, 제품적 의미와 정책은 하위 모듈에서 구현한다**는 점이다. 또한 Core는 범용 DataBus나 coordinator가 아니라, hook/state/DTO/event/SPI 같은 capability surface를 제공하는 얇은 허브로 남는다.


## 1-3. 관측 / 판단 / 정책 분리

이 생태계에서는 다음 분리가 핵심 구조 규칙이다.

- **Pulse**: 측정값 / 상태 / hook / DTO / event / SPI 같은 capability만 제공한다.
- **Echo**: 병목의 사실을 관측하고 raw observation을 제공한다.
- **Fuse / Nerve**: 자기 영역의 임계값 판단, recommendation 생성, optimization 적용을 내부에서 수행한다.

따라서 `targetId`, `category`, `magnitude`, `duration`, `sampleCount`, `spikeRatio`, `observedCost`, `frequency` 같은 관측값은 공유될 수 있어도, `severity`, `under pressure`, `priority`, `이 모듈이 처리해야 함`, `근거리면 FULL` 같은 해석·정책 신호는 Core나 Echo의 공용 계약이 되어서는 안 된다.

특히 `severity`는 측정값처럼 보이더라도 우선순위나 개입 필요성으로 오해되기 쉬우므로 공용 observation surface에서는 피한다. 필요하다면 각 모듈 내부의 local report label로만 사용하고, Pulse / Echo의 공용 계약으로 승격하지 않는다.

---

# 2. 모듈 지도

## 2-1. Pulse Core

### 정체성

얇고 중립적인 JVM 기반 모드로더 겸 플랫폼.

### 하는 일

- Java Agent / Mixin bootstrap
- 외부 모드 발견 및 로딩
- 모드 메타데이터 / 의존성 / 충돌 처리
- EventBus / Config / Scheduler / Registry / Network / DataAttachments / AccessWidener / GameAccess 같은 공용 capability 제공
- 거리 / 상태 / tick / phase 같은 측정·상태 노출 capability 제공 가능
- 예외 격리, 진단, 로깅, DevMode 등 플랫폼 안정성 기능 제공
- 바닐라의 `기반 기능 후보` 중 **중립적으로 노출 가능한 것만** API surface로 승격
- 향후 리소스팩 관련 기반 capability 제공 가능

### 하지 않는 일

- 프로파일링 로직
- 엔진 최적화 로직
- Lua 최적화 로직
- 게임 규칙 변경
- 특정 1st-party 모드 특혜 정책
- `근거리면 FULL` 같은 fast-path 정책
- `under pressure`, `priority`, recommendation 같은 해석 신호 제공
- helper / 편의 / 가이드 성격 기능 수용
- 하위 모듈 snapshot/update 주기 호출·통제
- 범용 모드 간 실시간 중개 채널(DataBus) 제공
- 하위 모듈 참조

### 설계 의도

Pulse Core의 유일한 정체성은 `자유도`다. 즉, 아무 정책도 강제하지 않으면서 무너지지 않는 기반을 제공하는 플랫폼이다. 이 플랫폼은 `새 Java 로더`로 전면 경쟁하는 제품이 아니라, **킬러앱이 먼저 가치를 증명한 뒤 뒤늦게 기반으로 드러나는 공통 지반**을 지향한다. 따라서 성공 조건은 기능 과시보다 **오염 방지 / 채택 마찰 최소화 / 기존 Lua 생태계와의 융합**에 둔다.

### API 성장 규칙

- API 확장은 `기반 후보 추출 → 기반성 판정 → 중립 노출 가능성 검증` 순서로만 진행한다.
- `있으면 편하다`는 이유만으로 Core surface를 늘리지 않는다.
- helper, 안전 래퍼, 사용성 편의는 가능하면 Cortex나 개별 제품 모듈에 남긴다.

---

## 2-2. Echo

### 정체성

병목 지점을 관찰하는 프로파일링 모드. Echo의 핵심 정체성은 `더 많이 재는 모드`가 아니라, **게임 실행을 흔들지 않는 순수 관측자**다.

Echo는 성능 문제를 직접 해결하거나 다른 모듈의 행동을 지시하지 않는다. Echo가 제공하는 것은 관측 가능한 사실, 진단 상태, 리포트 표면이며, 해석·처방·정책 결정은 각 모듈의 내부 책임으로 남긴다.

### 하는 일

- tick / scope / spike / phase 등 병목 관찰에 필요한 계측
- 통계 수집
- 오버레이 / 리포트 / 관찰 결과 제공
- `category`, `targetId`, `magnitude`, `duration`, `sampleCount`, `spikeRatio`, `observedCost`, `frequency` 같은 raw observation 생성
- 하위 모듈이나 provider가 노출한 상태를 관측 가능한 형태로 기록
- 무개입 / 비활성 / 미등록 / 조회 실패 / 오류 같은 상태 차이를 리포트에서 구분 가능하게 남김
- 운영 경로를 흔들지 않는 방식으로 필요한 진단 정보를 수집

### 하지 않는 일

- 게임 동작 자체의 변경
- 엔진 최적화 또는 Lua 안정화 로직 수행
- recommendation / priority / under-pressure 같은 정책 신호의 공용 노출
- Fuse / Nerve / Iris 같은 하위 모듈의 처리 여부 결정
- 다른 하위 모듈의 실시간 정책 입력원 역할
- provider가 보고한 상태를 추천, 처방, 우선순위, 개입 지시로 변환
- `0`, `inactive`, `missing`, `error` 같은 리포트 값을 Echo가 정책적으로 확정
- Echo 관측값을 근거로 Fuse governor, Nerve guard, Iris 출력 정책을 직접 조정
- 운영 경로를 정밀 분석, 디버그, 무거운 context capture, 외부 서비스 조회의 기본 장소로 삼는 것
- `severity` 같은 판단성 label을 공용 observation 계약으로 승격하는 것

### Core와의 관계

Pulse capability를 소비하지만, 프로파일링 로직은 Echo 내부에 남긴다.

- Pulse는 Echo가 사용할 수 있는 capability / SPI / registry 같은 중립 surface만 제공한다.
- Echo의 계측, 진단, 리포트 생성 경로는 Echo 내부 책임이다.
- Core나 다른 하위 모듈은 Echo 내부 갱신 주기나 분석 경로를 호출하거나 통제하지 않는다.
- Echo는 Fuse, Nerve, Iris 같은 하위 모듈을 직접 import하거나 내부 정책에 의존하지 않는다.
- 하위 모듈의 존재 여부나 상태 관측이 필요할 경우 Pulse SPI / registry / provider surface를 경유한다.
- Echo가 공용 계약으로 노출하는 것은 관측 가능한 사실과 진단 상태이며, 정책 판단이나 처리 지시는 아니다.

---

## 2-3. Fuse

### 정체성

Mixin 기반 엔진 비용 질서화 / 안정화 모드.

Fuse의 기본 레인은 **동일 결과를 더 싸게 만드는 semantic-preserving 최소 개입**이다. 목표는 모든 상황에서 평균 FPS를 끌어올리는 것이 아니라, 엔진 부하가 연쇄적으로 커져 게임이 오래 무너지는 상태를 줄이고, 프레임타임 꼬리와 붕괴 순간을 완화하는 데 있다.

따라서 Fuse는 `AI 자체를 더 똑똑하게 만드는 모드`가 아니다. AI 업데이트, 경로탐색, 충돌, 물리, 렌더, IO, GC 같은 엔진 비용 축에서 **게임 규칙과 결과 의미를 유지한 채 비용 폭주를 완화하는 안정성 레이어**다.

### 하는 일

- 엔진 레벨 병목 / 스파이크 완화
- 구조적 비용 절감
- 프레임타임 꼬리와 장시간 붕괴 상태 완화
- 의미 보존 가능한 범위에서 guard / limit / defer / deduplicate / stabilize 계열의 안전장치 적용
- 자기 pressure signal과 내부 상태를 기준으로 한 보수적 개입 판단
- fail-soft / backoff / retreat 기반의 안전한 철수
- Pulse capability / SPI / provider surface를 통해 노출된 raw observation을 참고할 수는 있으나, 임계값 판단 / recommendation 생성 / optimization 적용은 Fuse 내부에서 수행
- 엔진 비용 축별로 개입 가능성과 책임 범위를 분리해 다룸
- 개입하기 어려운 비분할 스톨이나 외부 원인성 프리즈는 필요 시 관측 / 분류 / 설명 표면에 머무름

### 하지 않는 일

- 엔진 포크
- 게임 규칙 변경
- 결과 의미가 달라질 수 있는 근사 / 공격적 알고리즘 교체의 기본화
- `모든 엔진 영역을 빠르게 만드는` 거대 최적화 모드 지향
- 경로 알고리즘 변경
- 충돌 판정 규칙 변경
- 물리 결과 변경
- AI 의미 변화나 인지 타이밍 개입을 기본 범위에 포함
- 모든 대형 프리즈를 Fuse가 반드시 해결해야 한다는 식의 과잉 약속
- 지속 과부하에서 상시 개입을 유지해 잔렉을 깔아버리는 정책
- Echo 관측값을 실시간 정책 입력으로 직접 연결하는 구조
- Echo 리포트 값을 Fuse 미작동 / Fuse 개입 필요로 단정하는 설계
- Pulse 정책 인터페이스나 Fuse 전용 UX / 명령 체계를 Core로 끌어올리는 것
- Lua 안정화 역할 흡수

### Core와의 관계

Pulse capability를 소비하지만, 엔진 안정화 로직 자체는 Fuse 내부에 남긴다.

- Pulse는 사실, hook, state, DTO, event, SPI 같은 중립 capability만 제공한다.
- Pulse는 Fuse의 정책 인터페이스나 governor를 소유하지 않는다.
- Fuse는 Pulse capability 위에서 자기 판단과 자기 안전장치를 구성한다.
- Pulse capability / SPI / provider surface를 통해 전달된 관측 데이터는 참고할 수 있지만, 해석과 조치 결정은 Fuse 내부 책임이다.
- Fuse는 Nerve의 Lua 안정화 역할이나 Echo의 프로파일링 역할을 흡수하지 않는다.
- Fuse가 다루기 어려운 엔진 프리즈는 관측 / 분류 / 설명에 머무를 수 있으며, 이를 Core 책임으로 올리지 않는다.

---

## 2-4. Nerve

### 정체성

100% Lua 기반 **선택적 안정성 Guard**.

Nerve는 Lua 자체를 전면 최적화하는 모드가 아니라, Lua를 제어면으로 사용해 멀티 / 모드팩 / 이벤트 / UI / 네트워크 경계에서 발생할 수 있는 상위 레이어 지연과 충돌을 완충하는 모드다.

기본 방향은 `더 빠르게 만들기`가 아니라 **망가지기 쉬운 순간에 피해 반경을 줄이고, 위험하면 즉시 물러나는 것**이다. 따라서 Nerve는 필수 성능 모듈이 아니라, 필요한 환경에서 선택적으로 켜는 안정성 레이어로 본다.

### 하는 일

- 이벤트 디스패치 / 모드 훅 / UI / 인벤토리 / 네트워크 경계에서 발생하는 Lua 레벨 충돌과 작업 겹침 완충
- 멀티 / 모드팩 환경에서 선택적으로 켜둘 수 있는 Lua control-plane 안전장치 제공
- 기본값 기준으로 바닐라와 동일한 의미 유지
- 위험 징후를 관측하고, 필요 시 fail-soft / back-off / retreat 방식으로 피해 반경 제한
- same-tick 재진입, listener 예외, 중복 호출, 과도한 호출 연쇄 같은 Lua 레벨 자폭 징후 완화
- 의미 보존 가능한 범위에서 coalescing, guard, dirty flag, 읽기 전용 캐싱, incident-gated 보호 같은 보수적 기법 사용
- 다른 Lua 모드가 활용할 수 있는 제한적 라이브러리성 기능 제공 가능
- 운영상 필요한 최소 상태, 사건 표식, 에러 서명만 외부 표면에 노출

### 하지 않는 일

- 바닐라 싱글 평균 FPS 향상을 주 목적으로 하는 성능 모듈화
- 바닐라 Lua 자체를 상시 병목으로 가정한 전면 최적화
- 필수 모듈 포지션 채택
- 게임 행동 의미 변경
- 이벤트 우선순위 판단, 중요도 판단, 자동 스케줄링, 자동 throttling 같은 정책 엔진화
- 지연 / 재정렬 / 병합 / drop처럼 결과 의미가 달라질 수 있는 개입의 기본화
- 전역 상시 보호 래퍼나 영구 차단을 기본 경로로 삼는 것
- 멀티 최적화, 핑 개선, 패킷 최적화, 서버 부하 분산, 엔진 동기화 수정 역할 수행
- Mixin 기반 엔진 최적화 흡수
- Echo의 분석 리포트 역할 흡수
- Iris의 위키 / 정보 표현 역할 흡수
- Frame의 팩 관리 역할 흡수

### Core와의 관계

Nerve Core는 Pulse 비의존 Lua-only 안정성 코어로 유지할 수 있다. Pulse 생태계 안에서 Pulse capability를 소비하는 것은 Nerve+ 또는 Nerve Pulse Adapter다.

- Nerve Core의 Lua 안정화 로직은 Nerve 내부에 남긴다.
- Nerve 내부 상태 공유는 Nerve 내부에서 처리한다.
- 타 모듈과 공유가 실제로 필요할 때만 Pulse SPI / capability를 경유한다.
- Pulse는 Nerve의 guard 정책, 예외 처리, 철수 조건, Lua 안정화 판단을 소유하지 않는다.
- Pulse capability / SPI / provider surface를 통해 노출된 일반 관측이나 카테고리 신호는 참고할 수 있지만, 분석 리포트의 소유자는 해당 provider로 유지한다.
- Nerve는 별도 리포트 시스템을 만들어 Echo 역할을 흡수하지 않는다.
- Nerve 고유 상태는 Echo Deep Analysis 계약으로 승격하지 않는다.
- 외부로 노출되는 Nerve 표면은 최소 상태, 사건 표식, 에러 서명 수준에 머문다.

### 계열 / 배포 경계

- **Nerve Core**: Pulse 비의존 Lua-only 안정성 코어. 독립 모듈로 배포 가능하며, 안정성 핵심 로직은 여기에 둔다.
- **Nerve Pulse Adapter**: Nerve Core를 Pulse capability / SPI와 연결하는 선택적 연결층.
- **Nerve+**: Pulse 의존 핵심 + 편의 계열. 더 강한 정답판이 아니라, 배포 / 운영 편의를 얹은 상위 오버레이로 취급한다.

이 구분의 목적은 기능 우열이 아니라 **채택 마찰 제어와 Core 오염 방지**다.

따라서 `Lite / Full`처럼 Nerve+가 진짜 버전처럼 보이는 제품 서사는 피한다.

---

## 2-5. Iris

### 정체성

Iris는 오프라인에서 확정된 정보를 **정적 산출물로 유지하고, 런타임에서는 이를 렌더링하는 위키 시스템**이다.

### 하는 일

* 대분류 / 소분류 / 아이템 목록 / 아이템 설명 구조 제공
* Evidence 기반 정보 분류
* 레시피, 우클릭 source, static capability 등 허용된 입력 정규화
* 외부 오프라인 생산 경로가 만든 fact / outcome 산출물 소비
* 표준 구조를 제공한 외부 모드 데이터를 Iris 입력 계약으로 정규화

### 하지 않는 일

* 설명 / 표시 / 런타임 단계에서 이미 확정된 fact / outcome / classification / Evidence를 보정하거나 재판정하는 것
* 표준 입력 계약을 제공하지 않은 외부 모드 데이터를 표시 문자열 해석이나 의미 추론으로 Iris 입력에 승격하는 것
* 표시 편의나 historical / diagnostic 산출물을 근거로 artifact의 role / lifecycle / authority / identity를 대체하거나 재정의하는 것

### 정보 구조

Iris가 다루는 정보는 다섯 층위로 구분한다.

1. **1계층 - 바닐라 툴팁 계층**

   * PZ가 기본 제공하는 아이템 정보로, Iris 정보가 놓이는 기준 정보층이다.

2. **2계층 - 주 소분류 / 카테고리 계층**

   * 아이템의 기본 탐색 의미와 브라우징 anchor를 제공한다.
   * `primary_subcategory`는 탐색 anchor로 유지하되, 상세 설명의 자동 생성 권한으로 승격하지 않는다.

3. **3계층 - 상세 설명 계층**

   * 아이템 중심의 위키형 상세 설명을 담당한다.

4. **4계층 - 상호작용 정보 계층**

   * 레시피, 우클릭 source, 요구조건, 사용 맥락 등 아이템과 연결된 상호작용 정보를 구조화한다.

5. **5계층 - 내부 정보 계층**

   * PZ 내부 아이템 정보와 Iris 내부 분류 / 처리 정보를 담는다.
   * 사용자 설명을 대신하지 않으며, 필요 시 별도의 메타 영역에 격리한다.

이 다섯 계층은 기술 파이프라인의 처리 순서가 아니라 **Iris 정보 모델의 층위**다.

### Evidence 모델

Iris는 정보 근거를 다음 네 개념으로 구분한다.

* **Source**: 사실을 관찰한 경로. Recipe, Right-click, Static capability 등이 이에 해당한다.
* **Action**: 메뉴 노출, 클릭 경로, 행동명 등 실행 표면에 나타나는 정보.
* **Outcome**: 해당 아이템이 없으면 성립할 수 없는 결과 상태.
* **Evidence**: Source를 통해 관찰된 fact / outcome을 Rule이 소비할 수 있도록 정규화한 정보.

Rule은 Source나 Action 자체가 아니라 정규화된 **fact / outcome Evidence**를 소비한다. Action은 Source 검증에 사용될 수는 있어도 그 자체로 canonical Evidence가 되지 않는다.

표시용 텍스트와 기존 fact에서 새로운 의미를 도출하는 추론·연산은 automatic Evidence로 승격하지 않는다.

자동 Evidence 경로로 처리할 수 없는 예외는 implicit inference로 보완하지 않고, 명시적인 manual override 경로로 분리한다.

### 책임 구조

Iris는 정보의 생산, artifact 관리, 검증, 표시와 배포를 서로 구분된 책임 영역으로 나눈다. 각 영역은 자신이 소유한 판단과 상태만 관리하며, 다른 영역의 생산 결과나 검증 결과를 근거로 그 책임을 대신하거나 확장하지 않는다.

* **Classification / Rule**

  * 허용된 source와 Evidence Allowlist를 통해 정규화된 Evidence를 DSL / Rule에 누적하여 fact / outcome / classification을 고정한다.
  * 자동 분류는 아이템의 의미를 새로 추론하는 체계가 아니라, 허용된 Evidence를 인덱싱하는 체계다.

* **DVF Core / DVF System**

  * Iris 3계층의 설명 생성 파이프라인을 소유한다.
  * 특히 3-3 개별 아이템 본문은 `approved facts / decisions / profile / body_plan -> rendered 3-3 body` 경로로 생산한다.
  * **DVF Body Compiler**는 compiler determinism, `body_plan` 반영, 설명 블록 조합과 rendered body shape 검증을 담당한다.
  * DVF Core의 책임은 3계층 설명 artifact의 생산에서 끝난다.

* **QG**

  * Iris 4계층의 상호작용 정보 생산·검문 파이프라인을 소유한다.

* **Iris Artifact Registry (IAR) — retired product architecture / retained history and governance**

  * IAR의 attempt, candidate, nonce, receipt, adoption, predecessor/successor lifecycle은 더 이상 Iris 1~5계층의 활성 제품 dependency가 아니다. Active product IAR consumer count는 모든 계층에서 0이다.
  * 기존 sealed attempt, source correction/cutover evidence, RTC bundle과 repository-validation receipt는 historical trace 또는 독립 governance evidence로 보존한다. 이 보존은 IAR product architecture의 존속을 뜻하지 않는다.
  * Source authority 변경은 reviewed Git-authored source diff와 해당 owner 경계가 담당한다. Derived Layer 3 runtime은 stateless complete-generation contract가 생산·검증하며 descriptor 자체는 authority/adoption token이 아니다.
  * Runtime Compatibility, Publish Boundary, package applicability와 Repository Validation은 계속 서로 다른 owner를 가진다. 어느 축의 PASS도 다른 축의 authority나 acceptance를 생성하지 않는다.
  * Reusable public-text assessment는 DVF/QG subject에 적용되는 오프라인 evidence producer로 유지하며 Publish Boundary가 그 결과의 acceptance를 별도로 판단한다.

* **Publish Boundary**

  * public-text acceptance와 publication / release acceptance를 소유한다.
  * 개별 생산 파이프라인의 성공이나 IAR의 adoption / compatibility 성공을 public-text acceptance로 대신하지 않는다.

* **Browser / Tooltip / Wiki**

  * 정렬, 접기, 패널 배치, 표시 밀도, 기본 노출 범위 등 user-facing 표시를 담당한다.

* **외부 산출물 / 추출기**

  * Iris가 소비할 fact / outcome을 오프라인에서 생산한다.
  * 산출물은 Iris 입력 계약으로 정규화되어 해당 생산·분류 경로에 공급된다.

* **Repository Validation**

  * exact tracked commit의 required validation surface가 격리된 clean checkout에서도 재현되는지를 검사하는 repository-level validation 책임이다.
  * repository validation 결과는 Iris artifact authority나 다른 책임 영역의 acceptance를 생성하지 않는다.

Assessment 또는 validation의 **subject finding**은 evaluator / validator의 **execution / orchestration failure**와 구분한다.

각 생산·authority·compatibility·acceptance claim은 자신이 속한 책임 영역에 한정되며, 한 영역의 PASS는 다른 영역의 PASS를 의미하지 않는다.

### Runtime core 구조

Iris runtime core는 public compatibility surface와 내부 state / fact model, runtime consumer를 분리한다.

```text
supported API / public require surface
-> thin facade or named compatibility adapter
-> explicit Browser / Detail / Description state and fact model
-> renderer / widget / chunk runtime consumers
```

* Description의 string output은 별도 병렬 구현이 아니라 canonical block API의 projection이다.
* Browser는 selection, cache, build 상태를 암묵적인 table 존재 여부가 아니라 명시적인 state로 관리한다.
* Browser와 Wiki detail은 동일한 read-only fact model을 소비한다.
* 유지되는 public contract는 thin facade 또는 이름 있는 compatibility adapter를 통해 내부 core에 연결한다.
* compatibility adapter는 core state를 복제하거나 runtime 의미를 재해석하지 않는다.

Runtime data는 consumer 요구 시점에 materialize한다.

```text
Browser boot
-> module / API surface 등록
-> first open에서 Browser data build
-> generation cache로 이후 재사용

Layer3 / UseCase consumer
-> range / count routing index
-> internal lookup router
-> 필요한 target chunk 로드
-> session cache

direct compatibility facade
-> 전체 chunk materialization
-> 기존 public contract 유지
```

* Browser의 lazy build는 기존 public `build()` 계약과 open entrypoint를 변경하지 않는다.
* range / count index는 key boundary, target module, row count와 identity만 보존하는 routing metadata이며 source fact나 semantic authority를 소유하지 않는다.
* 전체 chunk materialization은 기존 public contract를 위한 compatibility 경로이며 normal demand-loading 경로와 구분한다.
* lookup routing failure와 compatibility fallback은 정상 lookup 경로와 구분하여 관측 가능하게 유지한다.

## 2-6. Frame

### 정체성

Project Zomboid 모드팩의 상태를 시간축 위에서 **기록·비교·되돌리는 버전 관리 레이어**.

Frame은 개별 모드 관리자라기보다 **팩 상태(pack state)** 를 1급 객체로 다루는 환경 통제 모듈이다. 관리 최소 단위는 모드 하나가 아니라 모드 목록, 순서, 출처, 설정, 사용자 오버라이드, fingerprint를 포함한 팩 상태 전체다.

Frame은 게임 실행 중 성능·안정성에 개입하는 런타임 레이어가 아니다.

### 하는 일

- 모드 목록 / 순서 / 출처 / 설정 / fingerprint를 포함한 팩 상태 기록
- baseline / overrides / manifest / fingerprint 기반 상태 비교
- 원본 설정 보존과 사용자 오버라이드 레이어 관리
- 수동 기준점과 자동 안전망 스냅샷 운영
- 상태 A ↔ 상태 B diff, rollback, restore
- ZIP + JSON 기반 공개 공유 포맷 제공
- 필요 시 import 단계의 내부 `.frame` 검증 캐시 사용
- 설치 전 / 운영 단계에서 재현 가능한 팩 상태 관리

### 하지 않는 일

- 개별 모드 관리자처럼 ON/OFF와 정렬을 중심 UX로 삼는 것
- 문제 모드 지목
- 정상 / 비정상 판정
- 추천 / 정답 제시 / 자동 해결
- devkit / 로그 분석기 중심 제품화
- 월드 / 세이브 관리
- 모드 원본 파일 저장·배포형 완전 복원
- Frame 내부 설정 에디터
- `변화 없으면 저장 생략` 같은 해석적 자동 저장 정책
- 성능 개입 / 안정화 / Lua 실행 제어
- Fuse / Nerve와의 기능 결합
- 외부 런처 / 관리자 툴을 메인라인으로 삼는 것
- `.frame`을 외부 공유 표준으로 강제하는 것

### 설계 의도

Frame은 `문제를 해결하는 도구`보다 **되돌릴 수 있게 만드는 기록 도구**에 가깝다. 핵심 가치는 더 똑똑한 분석이 아니라, 실패를 리셋이 아닌 rollback 가능한 상태 변화로 바꾸는 데 있다.

Frame의 기록은 두 종류로 나눈다.

- **수동 기준점**: 사용자가 직접 선언한 공식 기록
- **자동 스냅샷**: 세션 복구와 변화 추적을 위한 보조 안전망

자동 스냅샷은 수동 기준점보다 품질이 낮은 기록이 아니라, 의도와 역할이 다른 시간축 안전망이다. 다만 Frame은 저장 생략 여부를 해석해서 결정하지 않고, 정해진 시간과 명시적 사용자 기준점을 우선한다.

Frame은 완전 복원 장치가 아니라 **재구성 + 동일성 확인 장치**다. Workshop 상태 변화, 삭제된 모드, 권리 문제 때문에 모드 원본 파일을 저장·배포하는 방식은 채택하지 않는다. 대신 목록, 순서, 출처, 설정, fingerprint를 통해 `그때와 지금이 같은가`를 확인한다.

Frame의 언어는 판단이 아니라 사실과 행동 중심이어야 한다. 따라서 `정상/비정상`, `원인/범인`, `권장/최적`, `해결/진단`, `문제 모드`보다 `기준점`, `자동 저장`, `달라짐`, `비교`, `되돌리기`, `포함됨`, `빠짐`, `순서 변경`, `설정 변경` 같은 표현을 우선한다.

Frame이 Echo / Fuse / Nerve와 함께 쓰일 수 있는 이유는 좋은 팩 상태가 런타임 모듈의 효과를 더 잘 드러나게 하기 때문이지, 기능적으로 결합되어 있기 때문이 아니다. Frame은 환경 계약과 재현 가능한 팩 상태를 제공하지만, 어디까지나 **환경 통제 레이어**로 남는다.

### Pulse와의 관계

Pulse는 Frame을 위해 활성 모드 목록, 모드 순서, 출처, 설정 위치, 파일 해시 / fingerprint, 파일 변경 이벤트, 저장 / 불러오기 기반 capability, SPI, 공통 진단 구조 같은 중립 capability만 제공한다.

Frame은 Pulse capability 위에서 PackState 모델링, 스냅샷 생성, 상태 비교, 오버라이드 관리, fingerprint 비교, 공유 패키지 생성, 가져오기 검증, 복원 UX를 담당한다.

Pulse는 Frame의 판단, 비교 정책, 복원 UX, 스냅샷 정책을 소유하지 않는다.

---

## 2-7. Cortex

### 정체성

다른 모듈에 넣기 부적절한 helper / 편의 / 가이드 성격 기능의 **격리 구역**. Core와 제품 모듈을 오염시키지 않기 위한 배출구로 본다.

Cortex는 다른 Spoke들이 의존하는 공용 유틸 라이브러리가 아니다. Cortex는 Pulse Core나 제품 모듈에 넣으면 오염되는 사용자-facing 편의 / 가이드 기능을 별도 제품 모듈로 격리하는 장소다.

### 하는 일

- Core 및 제품 모듈 비대화 방지
- helper / 편의 / 가이드 성격의 사용자-facing 기능 수용
- `Pulse에 넣고 싶어지는 기능`을 플랫폼 밖에서 흡수
- Pulse 기반 모딩을 이해하고 사용하는 데 필요한 가이드 / 보조 UX 제공 가능

### 하지 않는 일

- Core 정책화
- 다른 Spoke들이 import하는 shared utils 역할
- 하위 모듈 간 우회 의존 경로 제공
- 리소스팩 제품 축 수용
- 다른 제품 모듈 역할 흡수
- 플랫폼 채택 마찰 해소를 명분으로 Core에 들어갈 기능을 우회 수용한 뒤 다시 역이관하는 것
- Canvas / Frame 같은 별도 제품 축을 임시 운영하는 것

### Pulse와의 관계

Cortex는 Pulse capability를 소비할 수 있지만, Pulse capability를 재정의하거나 다른 Spoke를 대신해 조정하지 않는다.

Pulse는 Cortex를 위해 helper / 편의 / 가이드 기능을 Core로 끌어올리지 않는다. Cortex는 Core 오염을 줄이기 위한 제품 모듈이지, Core 확장의 예비 저장소가 아니다.

---

## 2-8. Canvas

### 정체성

외부 툴이 만든 리소스팩 산출물을 읽어 **최종 적용 상태를 계산·검증·비교·설명**하는 독립 모듈.

Canvas는 단순 리소스팩 로더나 제작 툴이 아니라, **리소스 적용 상태 관리 레이어**다. 사용자-facing 1급 객체는 ResourcePack이고, 구조적으로 다루는 최상위 상태는 여러 리소스팩이 합쳐져 실제 게임에 적용된 **ResourceState**다.

Canvas는 `무엇을 만들까`보다 **무엇이 최종 적용됐는지, 어디서 충돌하는지, 지금 상태로 배포 가능한지**를 드러내는 데 집중한다.

### 하는 일

- 리소스 인덱싱
- 최종 적용 상태 계산
- 충돌 분석
- 경로 / 구조 / ID / 패킹 검증
- 프리플라이트 검증
- 로컬 작업본 ↔ 빌드 산출물 비교
- 서버 ↔ 클라이언트 상태 비교
- 적용 결과 가시화와 설명형 리포트
- 외부 입력(ZIP / JSON / `.pack`)을 읽고 내부 정규화 캐시로 재구성

### 하지 않는 일

- 이미지 / 사운드 / 모델을 직접 만드는 제작 툴
- 단순 리소스팩 로더로 축소되는 것
- 자동 병합
- 정답 추천 / 최적 로드 순서 제시 / 정책 심판
- Frame 대체
- Cortex 대체
- `.cvb`를 외부 공유 표준으로 강제하는 것
- 외부 사례 구조를 그대로 복제하는 것

### 핵심 판정 축

Canvas의 판정 축은 세 가지로 나눈다.

1. **적용 상태 판정**
   - 현재 활성 리소스팩, 로드 순서, 출처를 바탕으로 최종 적용 상태와 충돌을 계산한다.

2. **제작 안전 판정**
   - 경로, 구조, ID, 중복, 패킹 문제를 검증하고 배포 전 프리플라이트를 제공한다.

3. **배포 일치 판정**
   - 로컬 작업본, 빌드 산출물, 서버 / 클라이언트 상태, manifest / fingerprint 차이를 비교한다.

이 세 축은 종합 리포트에서 함께 보여줄 수 있지만, 하나의 숨겨진 마스터 점수나 단일 합격 / 불합격 판정으로 압축하지 않는다.

### 포맷 / 공유 원칙

Canvas는 외부 파일, 프로젝트 폴더, `.pack`, ZIP + manifest / JSON을 입력으로 읽고, 필요하면 내부적으로 `.cvb` 같은 **정규화 캐시 / 분석 번들**을 사용할 수 있다.

다만 외부 공유 기본값은 열린 포맷을 우선한다.

- 기본 출력: `.pack`, `manifest.json`, 필요 시 ZIP 래핑
- 기본 공유: ZIP + JSON(+ `.pack`)
- 선택적 공유: 소스 ZIP + manifest, 문제 재현 / 분석용 `.cvb` 내부 정규화 번들

`.cvb`는 외부 공개 표준이 아니라 내부 처리, 검증, 캐시, 문제 공유를 위한 보조 포맷이다. 내부 기원 캐시 파일이라도 재로드 시 최소 검증을 거친다.

즉 `.cvb`는 Frame의 `.frame`과 유사하게 외부 입출력 표준이 아니라, 내부 처리와 문제 공유를 위한 보조 포맷으로 제한한다.

### Pulse와의 관계

Pulse는 Canvas를 위해 다음과 같은 중립 capability만 제공한다.

- 활성 리소스팩 / 순서 / 출처 조회
- 리소스 식별자 정규화
- 해시 / fingerprint 유틸
- 리소스 변경 / 리로드 이벤트
- Networking 기반 상태 교환
- SPI
- 공통 진단 출력 구조

Canvas는 Pulse capability 위에서 리소스 인덱싱, 내부 정규화, 최종 적용 상태 계산, 충돌 분석, 프리플라이트 검증, 상태 비교, 설명형 리포트, 사용자-facing UX를 담당한다.

Pulse는 Canvas의 판정 로직, 충돌 해석, 리포트 정책, UX를 소유하지 않는다.

### Frame / Cortex / 외부 툴과의 경계

- **Frame**: 모드팩 환경 상태를 시간축 위에서 기록·비교·되돌리는 레이어
- **Canvas**: 리소스 적용 상태를 계산·검증·비교·설명하는 레이어
- **Cortex**: 편의 / 가이드 / 제작 보조의 격리 구역
- **외부 툴**: 실제 리소스를 만드는 도구

Canvas와 Frame은 함께 쓸 수 있어도 통합 제품처럼 설계하지 않는다. Frame은 시간축과 팩 상태를, Canvas는 리소스 적용 결과와 배포 검증을 담당한다.

Cortex는 Canvas를 임시 수용하지 않으며, 제작 편의 기능이 필요할 때만 별도 보조 축으로 개입한다.

Canvas는 외부 사례를 참고할 수는 있지만, Vortex, packwiz, mrpack, Minecraft 리소스팩 stack 같은 사례의 구조를 그대로 복제하지 않는다.

### 구현 경계

Canvas는 JVM+Lua 혼용을 허용한다.

다만 최종 적용 상태 계산, 충돌 분석, 검증, 비교 같은 판정 로직은 Java 쪽이 소유하고, Lua는 그 결과를 표시·탐색하는 사용자-facing 표면으로 둔다.

# 3. 의존 방향

## 허용 방향

- Echo → Pulse
- Fuse → Pulse
- Nerve+ / Nerve Pulse Adapter → Pulse
- Iris → Pulse
- Frame → Pulse
- Cortex → Pulse
- Canvas → Pulse

## 독립 경계

- Nerve Core는 Pulse 비의존 Lua-only 안정성 코어로 유지할 수 있다.
- Nerve Core가 Pulse capability를 사용해야 하는 경우, 직접 의존이 아니라 Nerve Pulse Adapter 또는 Nerve+ 경로로 분리한다.

## 금지 방향

- Pulse → Echo/Fuse/Nerve/Iris/Frame/Cortex/Canvas
- Echo ↔ Fuse/Nerve/Iris/Frame/Cortex/Canvas
- Fuse ↔ Nerve/Iris/Frame/Cortex/Canvas
- Nerve ↔ Iris/Frame/Cortex/Canvas
- Iris ↔ Frame/Cortex/Canvas
- Frame ↔ Cortex/Canvas
- Cortex ↔ Canvas

즉, **하위 모듈 간 직접 참조는 금지**하며, 필요한 경우 Core capability 또는 SPI 계약으로 우회한다. 다만 이 우회는 범용 DataBus나 실시간 정책 주입 채널을 뜻하지 않으며, 필요 시의 observation event 표준화 정도만 허용 가능하다.

---

# 4. 계층 구조

## 4-1. 개념 계층

1. **Core Layer**
   - Pulse Core
2. **Product Modules Layer**
   - Echo / Fuse / Nerve / Iris / Frame / Cortex / Canvas
3. **External Mods Layer**
   - Pulse capability를 사용하는 외부 모드

## 4-2. 가치 흐름

- Core는 capability를 제공한다.
- Product Modules는 capability를 조합해 특정 사용자 가치를 만든다.
- External Mods는 Core surface를 사용해 자체 기능을 구현한다.

---

# 5. 플랫폼 성숙도 모델

## Stage A — Prototype Loader

- 자기 자신이 부팅됨
- 기본 bootstrap 동작

## Stage B — Real Mod Loader

- 외부 모드 발견
- 외부 mixin 등록
- entrypoint
- 메타데이터 / 의존성 / 충돌 처리

## Stage C — Mature Platform

- 예외 격리
- mixin 진단
- stable API surface
- DevMode / 로깅 / 디버그 오버레이 훅

## Stage D — Ecosystem Leverage

- 1st-party 모드와 외부 모드가 Core 위에서 안정적으로 동작
- 플랫폼 품질이 킬러앱 품질을 뒷받침

---

# 6. 로드맵과의 연결

- Phase 1은 `Stage B` 도달을 목표로 한다.
- Phase 2는 `Stage C` 도달을 목표로 한다.
- Phase 3은 `Stage D`에서 1st-party 모드 3종을 본격 전개하는 단계다.

즉, **1st-party 모드 개발 난이도와 로더 완성도는 강하게 연결되지만 동일 문제는 아니다.**  
로더가 성숙할수록 모드 개발은 쉬워지지만, 각 모드의 도메인 난이도는 별도로 남는다.

---

# 7. 현재 설계상 주의 구간

아래 항목들은 향후 구조 흔들림이 재발하기 쉬운 구간이다.

- Core 범위가 어디까지 얇아야 하는가
- 진단/디버그/헬퍼 기능 중 무엇을 Core에 둘 것인가
- engine optim 과 lua optim 의 경계
- stable API surface의 최소선과 최대선
- 중립 플랫폼과 1st-party 생태계의 긴장
- 브랜드 작업명(Pulse)과 최종 확정의 구분

이 구간의 변경은 반드시 `DECISIONS.md`에 재봉인한다.



# 8. 리팩토링 경계

## 8-1. 리팩토링의 기본 정의

Pulse 생태계에서 리팩토링은 `더 예쁜 구조 만들기`보다 **헌법, 핫패스, 외부 계약, 실제 코드 상태를 깨지 않는 보수적 정리 작업**이어야 한다. 문서상 이상형보다 현재 코드의 실제 경계를 우선한다.

## 8-2. 핫패스 우선 원칙

- EchoProfiler 같은 컴포넌트는 `큰 클래스`이기 전에 **핫패스 응집 단위**일 수 있다.
- `field access -> method call` 수준의 미세 변경도 핫패스에서는 누적 회귀 후보로 취급한다.
- 따라서 hot-path access 동등성이 증명되지 않으면, 구조 분리는 아키텍처 미학만으로 정당화되지 않는다.

## 8-3. 외부 계약 보존 원칙

- Report 계열의 외부 계약은 `Map<String, Object>` 반환을 유지한다.
- 내부 DTO, 포맷터, 어셈블러, 유틸은 허용 가능하지만, 외부 계약 변경은 허용하지 않는다.
- `내부를 더 타입 세이프하게 만든다`는 명분이 외부 API 파괴의 면허가 되지 않는다.

## 8-4. 실제 코드 우선 / Stage 스킵 허용

- FuseThrottleController처럼 이미 메서드 추출이 일부 끝난 영역은 `Stage 1부터 다시`를 기본으로 하지 않는다.
- 이미 존재하는 경계는 재사용하고, 추가 분리는 실익이 확인될 때만 선택적으로 연다.
- 즉 리팩토링 단계는 문서 고정 순서보다 **실제 코드 상태 진단**을 우선한다.

## 8-5. DI 현실주의

- 현재 생태계의 서비스 접근은 생성자 주입, `PulseServices`, `ServiceLocator`, `getInstance()` fallback이 공존할 수 있다.
- 목표는 순수 DI 체제로의 강제 전환이 아니라 **규약 정리, 일관성 확보, 누락 보완**이다.
- 패턴 순수주의 때문에 기존 동작 계약과 디버깅 경로를 무너뜨리지 않는다.

## 8-6. 기준선 없는 구조 개편 금지

- Echo hot-path, Report 스키마, Fuse governor/controller 경계 같은 고위험 리팩토링은 **Phase 0 기준선 확보** 없이는 열지 않는다.
- 기준선은 성능, 스키마, 행동 의미를 포함하며, 없으면 축소·보류가 기본값이다.


## 8-7. EventBus 현실주의

- EventBus는 `완전히 깨끗한 이상형`보다 **ClassLoader 현실과 모드 호환성을 감안한 3계층 경로**를 채택한다.
- 기본 경로는 **direct class lookup** 이고, 그 다음은 **FQCN O(1) fallback**, 마지막은 **제한적 reflection/호환 호출**이다.
- 목표는 fallback의 존재 자체를 부정하는 것이 아니라, **기본 경로를 빠르게 하고 호환 경로 비용을 제한하는 것**이다.

## 8-8. COW 직관성 유지

- EventBus 리스너 저장 구조는 가능하면 **단일 `CopyOnWriteArrayList`** 의 직관성을 유지한다.
- 리스트 객체를 갈아끼우는 immutable snapshot, compute 내부 새 리스트 생성, 과도한 이진 삽입 구조는 기본 전략으로 채택하지 않는다.
- 우선순위는 **등록 시점 `add + sort`로 정렬을 끝내고 fire 경로를 단순하게 두는 것**이다.

## 8-9. 새 인프라보다 기존 인프라 재사용

- 리팩토링은 새 시스템을 만드는 일보다 **기존 축을 덜 위험하게 확장하는 일**이어야 한다.
- 따라서 새 `ArchitectureGuardTest`, 새 `ServiceLocator`, 새 snapshot infra, 성급한 공통 `BaseConfig` 도입보다 기존 `HubSpokeBoundaryTest`, `PulseServiceLocator`, 기대값 테스트, 인터페이스 통일을 우선한다.
- `있는 것을 강화할 수 있는데도 새 것을 만든다`는 선택은 특별한 사유가 없으면 기본적으로 피한다.

## 8-10. 실존 모듈 기준 테스트

- 구조 가드와 경계 테스트는 **실제로 존재하고 현재 리팩토링 대상인 모듈**을 기준으로 작성한다.
- 현 단계의 중심은 Echo, Fuse, Nerve(Lua-only, `allowEmptyShould` 허용)이며, 실존 코드가 없거나 현재 Java 리팩토링 대상이 아닌 축을 전제로 규칙을 늘리지 않는다.
- 미래 spoke를 미리 상정한 규칙은 헌법 강화가 아니라 노이즈가 될 수 있으므로, 실제 코드 등장 후 별도 결정으로 연다.

## 8-11. Iris residual refactoring readpoint

Iris의 runtime 역할은 계속 **오프라인에서 확정된 사실을 Lua로 표시하는 viewer**다. 이번 후속 리팩토링은 의미 추론이나 taxonomy 권위를 runtime으로 옮기지 않고 다음 경계를 명시했다.

- `Classification/Rule authority -> CategoryPresentationOrder projection -> CategoryIndex/VariantIndex -> BrowserData` 방향만 허용한다. Logic은 Browser UI를 require하지 않는다.
- presentation-order projection은 표시 순서와 Description priority만 소유하며 category membership이나 의미를 소유하지 않는다.
- Variant 대표 선택은 locale과 `pairs()` 순회 순서가 아닌 `fullType` comparator로 결정하고, 파생 group cache는 generation과 함께 폐기한다.
- 공개 Tags, UseCases, Tooltip summary는 내부 동결 table을 직접 노출하지 않고 wrapper와 nested array를 복사한다.
- Wiki unit profile은 source field와 multiplier/format을 명시하지만 현재 사용자-visible output을 임의 환산하지 않는다.
- Alt Tooltip은 static fact projection, translation resolution, line assembly를 분리한다. 기존 cache와 분기 수를 유지하고 Detail ViewModel 생성이나 새 max-lines 정책을 도입하지 않는다.
- debug 문자열/집계는 기존 logger enablement 뒤에서만 계산한다. warning/error 및 failure evidence는 lazy 대상이 아니다.
- Python build 도구는 contract-specific I/O를 유지한다. `compose_layer3_io`는 기존 stem과 JSONL/hash/error 계약을 보존하고 Windows extended path를 처리하며, registry runtime record path projection만 stdlib-only leaf로 분리한다.
- validation evidence는 current, historical, diagnostic 역할을 분리하고 `current_evidence_index.json`을 비권위 projection으로만 취급한다.

초기 구현 readpoint는 `4f3699929ba838bf5b6a26f5924b3ee9d7066dff`이고, blocker correction / reviewer-hardening successor readpoint는 `c1fa281e`다. Successor는 다음 운영 경계를 추가한다.

- current taxonomy와 historical reproduction corpus는 서로 다른 denominator다. Historical pinned set은 current taxonomy의 subset이어야 하지만 전체 수가 같을 필요는 없다.
- diagnostic runner는 raw evidence producer이고 adapter가 terminal policy boundary다. Raw exit `1`을 숨기지 않으며 exact owner disposition과 stable fingerprint가 모두 일치할 때만 비차단으로 변환한다.
- protected-surface delta는 `path + exact LF-normalized successor SHA-256`으로 승인한다. Path 이름만으로 미래 변경 권한을 부여하지 않는다.
- Windows path budget은 checkout 환경을 완화하지 않고 staging namespace 하나를 짧게 재배치해 지킨다. Historical/docs/owner/reviewer identity namespace는 이동 대상이 아니다.
- clean-checkout에서 없는 ignored package peer와 EOL-only 차이는 source mutation이 아니다. Package identity는 disposable source projection으로 별도 검증한다.

Short-path clean clone에서 surface, current `150/150`, historical `285/285`, diagnostic adapter, full discovery `529/529`, Lua `97`, disposable package가 통과했다. 최종 exact-hash hardening 뒤 surface도 새 clean clone에서 재통과했다. 남은 architecture closeout 조건은 최종 `c1fa281e`의 receipt-bound full-gate와 수동 PZ UI evidence이며, 상태는 `partial`이다. 이 closeout의 잔여 범위는 validation execution isolation / clean-checkout stabilization으로 분류하며, 별도의 architecture 분석에서 발견될 리팩터링 후보를 배제하는 근거로 사용하지 않는다.

## 8-12. Iris repository evidence representation 경량화

Iris의 대형 검증 산출물은 내용 자체를 runtime/source authority로 승격하지 않고, 현재 소비자가 요구하는 복원 가능성과 역할을 기준으로 저장 표현을 줄인다.

- lifecycle baseline/final은 canonical dictionary + node stream + baseline selection + final delta로 저장하며 필요할 때 기존 JSONL을 byte-identical하게 재구성한다.
- 반복 historical payload는 repository-local content-addressed object와 original-path reference로 분리한다. 현재 실행 입력은 resolver가 원래 logical path를 유지한 채 object를 읽는다.
- consumer census는 ignored tooling도 포함해 Python AST/string fragment로 동적 Path 조립을 탐지한다. 탐지된 legacy ignored 도구 입력 하나는 11,381-byte 원경로 물리 예외로 유지하며 CAS reference도 복구 경로로 보존한다.
- CAS restore는 repository-relative POSIX `original_path`만 허용하고 absolute path, `..`, output escape와 reparse ancestor를 거부한다.
- `_archive`의 ignored historical payload는 검증·복원된 owner-managed 외부 ZIP으로 이동할 수 있지만 current/historical clean-checkout 입력에는 이 경계를 적용하지 않는다.
- repository, ignored working tree, CAS, 외부 archive, runtime Lua, runtime heap 측정은 서로 다른 domain이다. 겹치는 절감량을 하나의 합계로 주장하지 않는다.
- `OnGameBoot`는 Recipe/Moveables/Fixing/Classifications static payload를 미리 require하지 않는다. 기존 `StaticData` first-use cache와 실패 가시성을 유지하며 BrowserData registration은 측정 없이 제거하지 않는다.
- Layer3/UseCase full-table facade, `IrisData` global, LineCountIndex와 Browser allocation 후보는 외부 소비자·heap 증거 없이 변경하지 않는다.
- 현재 저장소 기준 lifecycle, repository evidence, current/historical, focused runtime, Lua syntax와 disposable package 검증은 통과했다. 2026-08-10 repository owner가 계획된 수동 PZ 인게임 검증 완료를 attestation했고, 실행 불가능한 raw diagnostic/full-gate 축은 성공으로 다시 쓰지 않은 채 scoped closeout의 non-blocking 범위 밖으로 disposition했으므로 전체 상태는 `complete`다.
- 동일 physical repository root에서 1차 baseline `4,842,336,252` bytes, 1차 final `1,338,324,791` bytes, 현재 file-length census `1,080,954,330` bytes를 비교한다. 2차는 1차 final에서 `257,370,461` bytes, `19.23%`를 추가로 줄였고 누적 감소는 `3,761,381,922` bytes, `77.68%`다.
- 전체 repository를 재귀적으로 읽는 workload의 입력량 대리 지표는 최초 대비 `4.48x`다. 이는 동일 토큰 예산의 처리 가능량을 바이트 비례로 환산한 값이며 실제 tokenizer, prompt selection, cache hit 또는 Codex token usage 측정값이 아니다.
- Codex Reviewer가 발견한 동적 CAS consumer 누락과 restore containment 결함은 AST/fragment census, 11,381-byte physical exception, canonical path/output/reparse guard로 수정했고 최종 review는 PASS다.

## 8-13. Iris runtime optimization boundary

Iris runtime lookup은 이제 `verified hit`, `verified miss`, `routing/target fault`를 구분한다. Verified miss는 정상적인 sparse-key 결과이며 compatibility facade를 적재하지 않는다. Index range/count/module identity 또는 target package 결함만 fault metric과 fail-closed fallback 대상이다. Package 단계는 Layer3/UseCase index와 `IrisRuntimeLookupPackageIdentity.json`을 함께 검증하므로 source와 packaged lookup surface가 서로 다른 generation을 조용히 섞을 수 없다.

Generated UseCase chunk는 nil optional field와 빈 `debug_lines`를 저장하지 않는다. 이 sparse representation은 source 의미를 바꾸지 않으며 public/direct facade가 기존 empty-table/nil shape를 재구성한다. Line-count index는 routing authority로 유지되고 runtime 의미 추론 권한을 얻지 않는다.

Browser/Tooltip/Ordering 최적화는 내부 materialization과 반복 호출만 줄인다. Public Browser row는 계속 copy-on-read이고, Tooltip public summary는 caller mutation으로부터 격리되며, Ordering public wrapper와 anchor/order semantics는 유지된다. Capability category/type은 positive hint일 뿐 closed negative evidence가 아니다. Custom·contradictory·same-canonical hybrid의 기존 field를 보존할 안전한 부정 authority가 없으므로 capability mask는 no-op이고 method-presence fallback을 유지한다. Instance state를 fullType 전역 cache로 승격하지 않는다.

Runtime instrumentation은 기본 off다. RuntimeLookupDiagnostics의 normal-miss metric과 BrowserData/ItemIndex/Query, Detail ViewModel, Alt Tooltip/TooltipSummary, Ordering의 counter·clock read는 diagnostics harness가 각 module의 explicit enable API를 호출한 동안에만 갱신된다. Fault/fallback 가시성은 계측과 별개로 유지한다. Counter API는 operation evidence일 뿐 runtime authority나 일반 production state가 아니다.

Pytest의 configured discovery는 exact Round 3 current authority와 별도다. Source policy는 current/historical/diagnostic/excluded 및 mixed item override를 소유한다. Git-tracked policy source set과 approval 시점의 clean-checkout-absent policy source set은 각각 count/identity로 고정되므로 tracked source 삭제나 정책 분모 축소는 collection 전에 실패한다. 승인된 ignored historical source 두 개는 존재할 때만 실제 collection denominator에 들어간다. Exact current runner의 authority를 configured `all` 결과로 대체하지 않으며 advisory 역사 실패를 current PASS로 다시 쓰지도 않는다.

Advisory failure classification은 exact `base..endpoint` diff와 실패 source의 sealed dependency manifest를 함께 펼쳐 modified/mandatory 교집합을 판정한다. 이번 34-artifact historical hash 재현 실패는 83-path dependency manifest까지 포함해 두 교집합이 모두 0일 때만 optimization claim 밖으로 분류했으며, configured full-suite PASS로 승격하지 않았다. Reviewer protection successor v2는 수정된 RuntimeLookupDiagnostics, AltTooltip, TooltipSummary 및 residual contract surface의 predecessor tree와 before/after blob을 연쇄 결속한다.

Standalone Lua fixture는 operation count와 output parity만 승인한다. 2026-08-11 repository owner가 실제 Project Zomboid에서 정상 동작을 확인해 수동 functional runtime acceptance는 완료됐다. Raw timing sample이 없는 debounce, incremental build, Tooltip first-load 및 LineCount attribution은 계속 deferred benchmark candidate이고 정량 성능 claim을 만들지 않으며, governing plan에 따른 통합 closeout 상태는 `partial`이다. 이 상태는 별도로 기록된 기능 검증 완료를 무효화하지 않는다.

Closeout review authority는 implementation subject `fe4bb9f6`, endpoint-bound receipt `b33ed2ac`, owner-attestation correction `89f7499c`, review seal `91259769`로 분리한다. Codex Reviewer는 구현과 attestation 경계를 각각 재검토해 최종 P0/P1/P2/P3 모두 0으로 승인했다. Review seal은 성능 benchmark나 release 권위를 새로 만들지 않는다.

## 8-14. Iris follow-up row cache and lazy metadata boundary

Browser의 generation-local private row가 `fullType`, ScriptItem identity, locale display name/folded key, primary Browser location, primary classification tag를 함께 소유한다. Classification bucket은 fullType membership만 보존하고 private classification table/array를 cache graph나 public result에 연결하지 않는다. Public Tags export와 Browser item/search/list facade는 기존 shape와 copy-on-read/identity 계약을 유지한다.

Browser search owner는 `(generation, normalizedLocale)`다. Locale candidate를 만드는 동안 기존 snapshot은 그대로 유지되며, 새 row map과 정렬 snapshot이 완성된 뒤 publish한다. 같은 transaction에서 prefix state와 locale display-name 기반 variant cache를 폐기한다. Session reset은 이 owner와 별개이며 census에서 session-dependent engine object가 확인되지 않아 production lifecycle wiring을 추가하지 않는다.

UseCase index metadata는 module-load dependency가 아니다. First demand에서 ChunkIndex와 LineCountIndex의 `unloaded | valid | invalid(reason)` self-state를 각각 만들고, 둘 다 valid일 때만 entry-count cross-check를 `valid | invalid(index_content_mismatch)`로 판정한다. 어느 하나가 invalid이면 cross-check는 `not_applicable`이다. `get()`과 `getLineCount()`는 서로 다른 gate를 적용하며 LineCountIndex의 독립 negative authority `0, nil`을 유지한다.

ObjectAccess fixed-arity surface는 Lua eligibility와 engine adoption을 분리한다. Iris는 100% Lua 제품 경계를 유지하며 JVM bytecode, JAR, Mixin, `luajava`/`importClass` 같은 직접 Java bridge를 포함하지 않는다. `getScriptManager():getAllItems():size()`/`get(i)`처럼 PZ가 Kahlua에 표준 Lua API로 노출한 엔진 객체를 소비하는 것은 JVM+Lua 혼용 구현이 아니다. 여기서 필요한 engine evidence는 이 Lua-visible method의 self binding, argument coercion, object identity, nil/false/0, missing/error 반환 shape가 fixed-arity direct protected call에서도 보존되는지에 한정한다.

`call0/call1`이 존재해도 generic caller는 representative PZ Kahlua engine-object evidence 전까지 predecessor vararg path를 사용한다. Standalone Lua fixture는 eligibility만 승인하며 실제 engine-object adoption을 대체하지 않는다. 따라서 현재 architecture closeout은 pure-Lua adopted change와 engine-bound `unvalidated_but_in_scope` branch를 함께 가진 `partial`이다.

Runtime materialization 경량화와 repository context 경량화는 서로 다른 축이다. Base `5b19a5fa58cb883f6b27f433371434a85b41ba0d` 대비 current overlay의 EOL-normalized source proxy에서 변경 production Lua 15개는 bytes `+16.09%`, lexical units `+13.22%`이고, input plan을 제외한 45-file implementation surface는 bytes `+14.86%`, lexical units `+9.89%`다. 같은 context 예산의 수용량 proxy는 각각 약 `11.68~13.86%`, `9.00~12.94%` 감소한다. 이 architecture는 반복 순회·정렬·임시 table/closure 감소를 runtime operation 개선으로만 읽으며 token 효율 개선으로 전파하지 않는다. Exact tokenizer와 prompt-selection/cache telemetry가 없으므로 실제 GPT/Codex token 개선률은 미측정이다.

## 8-15. Iris test workflow consolidation boundary

Iris test execution 경량화의 기본 단위는 개별 assertion이나 pytest node가 아니라 **비싼 producer와 그 결과를 소비하는 contract family/lifecycle**이다.

```text
immutable seed / explicit isolated workspace
-> expensive producer or lifecycle execution once
-> immutable structured result and phase artifacts
-> named contract checkpoints A / B / C / D
-> cross-phase or final aggregation assertion E
```

- 같은 command/input으로 동일 producer를 반복 실행하고 결과의 서로 다른 field만 확인하는 test는 한 workflow execution의 named checkpoint로 통합할 수 있다.
- E가 A/B/C/D artifact를 소비하는 실제 pipeline이라면 각 phase와 final relationship을 같은 scenario 안에서 검증한다. A/B/C/D를 먼저 실행한 별도 test의 성공 여부나 mutable output에 E가 의존하게 만들지는 않는다.
- 공통 준비를 재사용하려면 seed/result가 immutable이거나 lifecycle owner가 명시돼야 한다. Test order, global mutation, 이전 failure residue 또는 cleanup 성공에 의존하는 hidden coupling은 금지한다.
- 정상 흐름과 같은 immutable seed에서 시작할 수 있는 negative case는 cheap isolated clone/snapshot을 사용할 수 있다. Tamper, crash, rollback, concurrent-owner, fresh-process/bootstrap과 standalone CLI semantics가 계약인 case는 독립 workspace/process 경계를 유지한다.
- 한 workflow test 안의 각 contract는 named `subTest`, checkpoint ID 또는 동등한 failure attribution을 가진다. 하나의 early assertion이 후속 독립 checkpoint 관측을 불필요하게 차단하지 않도록 producer failure와 consumer assertion failure를 구분한다.
- 단순히 여러 test body를 한 함수에 순서대로 호출하는 것은 architectural consolidation이 아니다. Subprocess, full-tree copy, Git initialization, hashing/materialization과 producer invocation의 실제 횟수가 줄어야 한다.
- Workflow integration은 required-validation/taxonomy/source-policy identity를 원자적으로 이관하며 protected contract, input partition, branch, fail-closed path와 failure localization을 보존한다.

성능 claim은 동일 환경의 before/after evidence가 있을 때만 허용한다. 최소 측정 축은 route wall time, expensive producer invocation, subprocess spawn, temporary workspace/materialization, copied bytes, node count와 repository-wide net test/tooling LOC다. 어느 한 축의 감소를 다른 축의 감소로 대신하지 않으며, 선행 precision-preserving closeout은 실행시간 개선의 증거로 사용하지 않는다.

현재 채택된 구조는 이 경계를 네 cost group에 적용한다.

- Artifact inventory와 artifact promotion은 canonical tracked scaffold의 Git seed까지만 class owner가 공유한다. 각 consumer는 독립 clone과 local Git identity를 소유하며 ignored giant, tamper, rollback/recovery, lock/journal/backup, collision과 concurrency tail을 서로 공유하지 않는다.
- Registry authority는 locked COMMON 또는 Round 3 runner source bytes를 한 번 읽고 compile descriptor를 immutable하게 보존한다. 각 consumer는 fresh module namespace에서 실행한다. 준비 실패 descriptor도 class, args, path/WinError field와 exact message를 보존해 consumer마다 새로운 예외로 재구성한다.
- Runtime payload의 writable root는 module global이 아니라 case-local ownership이다. 이 isolation correction은 materialization 감소 claim이 아니라 fresh-process/fresh-root 의미 보존이다.
- 40개 consumer node는 55개 concrete checkpoint identity로 매핑된다. Shared producer가 assertion/failure identity를 소유하지 않으며, node/subTest가 계속 진단 단위다.

Validation authority는 execution architecture와 source taxonomy를 함께 닫는다. 추적 workflow test source 10개는 exact-path `dedicated_route_validation`으로 분류되고 taxonomy, configured policy와 normalized pytest testpath ancestry가 fail-closed로 일치해야 한다. Exact/configured collection은 denominator와 route binding을 확인하지만 실행 PASS를 대신하지 않는다. 결합 subject `ea94c19789fd33799180c4cbf1e19bde26a3a482`의 clean-checkout canonical Run A/B가 각각 `424 passed / 0 failed / 2 deselected / 102 subtests passed`, standalone `4/4 PASS`를 기록하고 deterministic comparator가 같은 결과를 확인한 것이 current execution authority다.

현재 readpoint의 `public-text-phase7-dispatch`는 네 consumer의 동일 producer를 class-lifecycle immutable result 한 번으로 통합한 첫 적용이다. 이 pilot의 `4 -> 1`은 architecture pattern의 유효성을 보여주지만 Iris 전체 test consolidation 완료를 뜻하지 않는다. 나머지 family의 `deferred`/`must_isolate` 기록은 이 경계를 적용할 후속 profiling과 설계를 금지하지 않는다.

이 readpoint의 structural result는 consolidatable invocation `73 -> 6`과 disclosed heterogeneous total `187 -> 126`이다. 전자는 동일 producer signature의 반복 제거이고 후자는 clone/configuration을 포함한 투명한 총계다. Comparable full-gate before/after wall-time이 없으므로 architecture는 이 수치를 전체 suite 속도 개선률로 전파하지 않는다.

### DVF 3-3 stateless complete-generation successor

Layer 3 current successor는 다음 책임을 분리한다.

`canonical source + adopted upstream content input -> deterministic off-live complete generation -> stateless generation/key validation -> immutable generation install -> single generation-pointer switch -> package projection`

- Canonical input owner: Git-authored six-file compose input set과 현재 payload 의미를 만든 adopted upstream candidate. Current rendered/runtime/descriptor, receipt와 installer lifecycle state는 generation input으로 역유입되지 않는다.
- Generation owner: `dvf_3_3_generation_contract.py`와 `build_dvf_3_3_complete_generation.py`. Rendered JSON, generation-qualified Lua chunks, stable facade candidate와 identity-only descriptor를 external root에 완성한다.
- Validation owner: `validate_dvf_3_3_complete_generation.py`와 `dvf_3_3_runtime_compatibility.py`. Descriptor를 권위로 신뢰하지 않고 input/output identity, exact key, collision과 payload projection을 다시 계산한다.
- Install owner: `install_dvf_3_3_complete_generation.py` 하나만 protected runtime visibility를 바꿀 수 있다. Immutable set은 `IrisLayer3Generations/<generation_id>`에 두고 `IrisLayer3DataCurrent.lua` pointer를 마지막 `os.replace`로 바꾼다. Stable facade와 index는 같은 pointer를 읽고, same-generation install은 protected write가 0인 no-op이다.
- Package owner: `package_iris.ps1`. `current_runtime_payload`와 generation identity를 검증하며 RTC-certified applicability는 별도 exact-generation evidence 없이는 fail-closed한다. Lookup identity row는 ordinal exact-key ordering을 사용해 Windows PowerShell 5.1과 PowerShell 7에서 같은 digest를 만든다.
- Repository governance owner: `Iris/validation/clean_checkout/`. 실행 receipt와 exact-commit binding은 product generation state와 분리해 보존한다.

Runtime은 계속 100% Lua다. Python은 build/validation/install tooling에만 존재한다. Public Iris behavior, Layer 3 의미, Recipe/Right-click 독립성, Browser/Wiki와 Alt tooltip surface는 이 successor가 변경하지 않는다.

기존 fixed 11-chunk/stateful descriptor product 경로는 은퇴했다. Historical adoption 도구와 sealed evidence는 재현 전용이고, current package/runtime 소비자는 generation pointer와 immutable generation descriptor만 읽는다. Layer 1–5 active product IAR consumer가 0이므로 이 product architecture의 상태는 `FULL_RETIREMENT`다.

Clean-checkout canonical Run A/B와 deterministic compare의 validated implementation subject는 `c924349eae6ee7f2a077ca83899b0ec99131f6c2`다. Codex Reviewer가 발견한 cross-PowerShell package identity nondeterminism은 terminal implementation subject `6f362b5e284d9f05749c7f9dc6a11f13bb1fe322`에서 ordinal ordering으로 교정했고 실제 `current_runtime_payload` ZIP projection이 exit `0`으로 완료됐다. Closeout carrier는 `5ce69e2a3bbf02d453e874af740a312e37b74bff`다.

### Layer 3 optional-description role material

Layer 3 body-role realignment은 current producer/install architecture 위의 off-live semantic staging route다.

`current exact facts + exact provenance mapping + optional IPS Layer 3 snapshot axes -> readiness/disposition ledgers -> source-bound core/acquisition role material -> flat Menu candidate + Tooltip input readiness`

- `layer3_body_role_realign.py`는 source/provenance mapping, total readiness/disposition과 exact duplicate signal/blocking separation을 소유한다. Rendered text를 source fact로 읽지 않는다.
- `compose_layer3_role_material.py`는 confirmed description-eligible fact와 acquisition fact를 물리적으로 분리하고 fact IDs와 transformation trace를 보존한다. Acquisition-only projection은 core description이 아니다.
- `run_layer3_body_role_realign.py`는 pointer-selected current generation을 execution time에 읽고 isolated roots 두 곳에서 byte-identical candidate를 재생성한다. Current facts/rendered/runtime/package와 one-off predecessor evidence는 protected observation surface다.
- `validate_layer3_body_role_realign.py`는 staging subject만 read-only로 검증한다. Repository Clean-Checkout, current install, RTC, Publish 또는 release claim을 만들지 않는다.
- Repository validation owner는 `Iris/validation/clean_checkout/`다. Staging focused test와 candidate replay 뒤 exact tracked terminal subject를 fresh disposable checkout 두 곳에서 full-repository Run A/B로 실행하고 canonical result raw-byte identity와 deterministic comparison을 확인한다. 이 gate만 `layer3_role_realign_staging_complete`의 repository-validation axis를 닫을 수 있다.
- Runtime Lua는 계속 precompiled `text_ko`만 표시하고 readiness, disposition, fact-kind, rewrite 또는 summarization을 계산하지 않는다. Tooltip runtime consumer는 이 architecture change에 포함되지 않는다.

One-off Item-Page Information Sufficiency row는 exact snapshot이 current일 때 Layer 3 `fact_availability/contribution/requiredness/representation` axes만 readiness prerequisite에 보조적으로 제공한다. Page disposition과 Layer 4 axes는 semantic production input이 아니다. Drift 시 evidence를 stale로 격리하며 제거된 evaluator나 authority chain을 복원하지 않는다.

Validated staging terminal subject는 commit `1197ccc99085666d336e3ed493555e26810104e5`, tree `da2bf2e5ec595b8de1ea41ee2fafb7e433c058db`다. 이 subject의 candidate replay는 item `2,285`, existing body `2,084`, Problem 5A `2`와 successor entries identity `17789343f34bfc013d71460118819369913f85a073f319e93335c614cacaa200`을 재현했다. Mandatory Run A/B는 각각 pytest identity `433`, standalone validation `4`로 PASS했고 canonical result raw bytes가 일치했으며 source checkout mutation은 `0`이다.

`Iris/_docs/round3/layer3_body_role_realign/evidence_carriers/1197ccc99085666d336e3ed493555e26810104e5/clean_checkout_result_pointer.json`은 external receipt hash를 가리키는 post-validation evidence-only carrier다. `Iris/_docs/round3/layer3_body_role_realign/17789343f34bfc013d71460118819369913f85a073f319e93335c614cacaa200/axis_qualified_closeout.json`은 staging axes와 non-claim을 기록한다. 둘 다 validated terminal subject, current generation pointer, runtime/package authority 또는 새 validation authority가 아니다.
