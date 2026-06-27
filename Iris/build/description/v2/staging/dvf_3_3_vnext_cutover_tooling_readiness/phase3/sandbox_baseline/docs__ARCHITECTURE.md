# ARCHITECTURE.md

> 상태: 초안 v0.2 + addenda trace-dedup through 2026-06-21
> 기준일: 2026-06-21
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
- **Spokes**: Echo, Fuse, Nerve, Iris, Frame, Cortex, Canvas
- **확장 방식**: SPI, 공용 capability, 이벤트/레지스트리/유틸 등 Core surface

핵심은 **Core는 기반만 제공하고, 제품적 의미와 정책은 하위 모듈에서 구현한다**는 점이다. 또한 Core는 범용 DataBus나 coordinator가 아니라, hook/state/DTO/event/SPI 같은 capability surface를 제공하는 얇은 허브로 남는다.


## 1-3. 관측 / 판단 / 정책 분리

이 생태계에서는 다음 분리가 핵심 구조 규칙이다.

- **Pulse**: 측정값 / 상태 / hook / DTO / event / SPI 같은 capability만 제공한다.
- **Echo**: 병목의 사실을 관측하고 raw observation을 제공한다.
- **Fuse / Nerve**: 자기 영역의 임계값 판단, recommendation 생성, optimization 적용을 내부에서 수행한다.

따라서 `targetId`, `category`, `severity` 같은 관측치는 공유될 수 있어도, `under pressure`, `priority`, `이 모듈이 처리해야 함`, `근거리면 FULL` 같은 해석·정책 신호는 Core나 Echo의 공용 계약이 되어서는 안 된다.


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
- `category`, `targetId`, `severity` 같은 raw observation 생성
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
- Core 오염
- 타 하위 모듈 역할 흡수
- 운영 경로를 정밀 분석, 디버그, 무거운 context capture, 외부 서비스 조회의 기본 장소로 삼는 것

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
- Echo 같은 관측 모듈의 raw observation을 참고할 수는 있으나, 임계값 판단 / recommendation 생성 / optimization 적용은 Fuse 내부에서 수행
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
- Core 내부화
- Lua 안정화 역할 흡수

### Core와의 관계

Pulse capability를 소비하지만, 엔진 안정화 로직 자체는 Fuse 내부에 남긴다.

- Pulse는 사실, hook, state, DTO, event, SPI 같은 중립 capability만 제공한다.
- Pulse는 Fuse의 정책 인터페이스나 governor를 소유하지 않는다.
- Fuse는 Pulse capability 위에서 자기 판단과 자기 안전장치를 구성한다.
- Echo가 관측한 데이터는 참고할 수 있지만, 해석과 조치 결정은 Fuse 내부 책임이다.
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
- Core 내부화
- Pulse로 기능을 상향 이동

### Core와의 관계

Pulse capability를 소비할 수 있지만, Lua 안정화 로직은 Nerve 내부에 남긴다.

- Nerve 내부 상태 공유는 Nerve 내부에서 처리한다.
- 타 모듈과 공유가 실제로 필요할 때만 Pulse SPI / capability를 경유한다.
- Pulse는 Nerve의 guard 정책, 예외 처리, 철수 조건, Lua 안정화 판단을 소유하지 않는다.
- Echo의 일반 관측이나 카테고리 신호는 참고할 수 있지만, 분석 리포트의 소유자는 Echo로 유지한다.
- Nerve는 별도 리포트 시스템을 만들어 Echo 역할을 흡수하지 않는다.
- Nerve 고유 상태는 Echo Deep Analysis 계약으로 승격하지 않는다.
- 외부로 노출되는 Nerve 표면은 최소 상태, 사건 표식, 에러 서명 수준에 머문다.

### 계열 / 배포 경계

- **Nerve**: Pulse 비의존 핵심 기능 스탠드얼론. 안정성 코어는 여기에 둔다.
- **Nerve+**: Pulse 의존 핵심 + 편의 계열. 더 강한 정답판이 아니라, 배포 / 운영 편의를 얹은 상위 오버레이로 취급한다.
- 이 구분의 목적은 기능 우열이 아니라 **채택 마찰 제어와 Core 오염 방지**다.
- 따라서 `Lite / Full`처럼 Nerve+가 진짜 버전처럼 보이는 제품 서사는 피한다.

---

## 2-5. Iris

### 정체성

100% Lua 기반 위키형 정보 모드.

Iris는 단순한 `정보 추가 모드`가 아니라, **게임 코드와 데이터에 숨어 있는 행동·용도·관계 정보를 근거 기반으로 정리해 유저 언어로 보여주는 구조적 위키 시스템**이다.

Iris의 목표는 `모든 것을 추론하는 AI 위키`가 아니라, **허용된 source와 evidence를 바탕으로 검증 가능한 정보를 정적 산출물로 만들고, 런타임에서는 이를 안전하게 렌더링하는 위키 엔진**이다.

Iris의 설명은 질문마다 다를 수 있지만, 대답의 태도는 동일해야 한다. 즉, 근거가 있는 정보만 말하고, 해석·권장·비교는 하지 않는다.

### 하는 일

- Alt 툴팁 확장
- Iris 메뉴 기반 세부 정보 제공
- 대분류 / 소분류 / 아이템 목록 / 아이템 설명 구조 제공
- Evidence 기반 분류와 정적 설명 산출물 렌더링
- 레시피, 우클릭 source, static capability 등 허용된 입력을 정규화
- 외부 오프라인 생산 경로가 만든 fact / outcome 산출물을 소비
- 표준 구조를 제공한 외부 모드 데이터를 Iris 입력 형식으로 정규화해 위키 표면으로 렌더링
- 검증된 정보를 툴팁보다 상세한 위키형 문장과 구조로 보여줌

### 하지 않는 일

- 근거 없는 의미 추론
- 권장 / 추천 / 비교
- 설명 단계에서 분류나 evidence를 보정하는 것
- UI 표시 편의를 이유로 source / outcome / evidence를 재판정하는 것
- 표준 구조를 제공하지 않은 외부 모드 데이터를 텍스트 해석이나 추론으로 억지로 위키화하는 것
- 런타임에서 새 설명을 생성하거나, source 검증 / 의미 품질 판단 / 표시 정책 판단을 수행하는 것
- source / rendered / runtime 권위 경계를 표시 편의나 이력 산출물로 재정의하는 것
- Core 내부화
- JVM+Lua 혼용

Iris는 확정된 정보를 사람이 읽을 수 있는 위키식 문장으로 보여줄 수는 있다. 그러나 그 문장은 새 판단을 만드는 장소가 아니라, 이미 검증된 fact / classification / outcome을 렌더링하는 장소다.

### 정보 구조

Iris가 사용자에게 제공하는 정보는 최소 다섯 층위로 나눈다.

1. **1계층 - 바닐라 툴팁 계층**
   - PZ가 기본 제공하는 아이템 정보.
   - Iris는 이를 대체하지 않고 Alt 툴팁과 Iris 메뉴로 추가 정보를 얹는다.

2. **2계층 - 주 소분류 / 카테고리 계층**
   - 아이템의 기본 탐색 의미와 브라우징 anchor를 제공한다.
   - `primary_subcategory`는 유지하되, 설명 문장의 자동 권한으로 승격하지 않는다.
   - 이 계층은 탐색 안정화를 위한 anchor이지, 모든 아이템 설명을 자동 생성하는 근거가 아니다.

3. **3계층 - 상세 설명 계층**
   - 아이템 중심의 작은 위키형 설명을 담당한다.
   - 특히 3-3 개별 아이템 본문은 DVF를 통해 오프라인에서 생산·검증·봉인하고, 런타임은 렌더링만 한다.
   - 1·2계층만으로 충분하거나 안전한 본문을 만들 수 없으면 침묵할 수 있다.

4. **4계층 - 상호작용 정보 계층**
   - 레시피, 우클릭 source, 요구조건, 사용 맥락 등 아이템이 연결되는 상호작용 정보를 구조화한다.
   - Recipe 기반 증거와 Right-click 기반 증거는 서로의 변주가 아니라 독립 입력 트랙이다.
   - 이 계층은 행동을 추천하거나 의미를 과장하지 않고, 관련 경로를 탐색 가능하게 보여준다.

5. **5계층 - 내부 정보 계층**
   - PZ 내부 아이템 정보와 Iris 내부 분류 / 처리 정보를 담는다.
   - 기본 설명을 대신하지 않으며, 필요 시 메타 영역에 격리해 보여준다.

이 다섯 계층은 기술 파이프라인 순서가 아니라 **사용자에게 제공되는 정보의 층위**다.

### 생산 책임 분리

Iris의 정보 생산과 표시는 다음 책임으로 분리한다.

- **Iris Core / 분류 계층**
  - 허용된 source, Evidence Allowlist, DSL, Rule을 기준으로 fact / outcome / classification을 고정한다.
  - 의미를 임의로 해석하거나 설명 품질을 이유로 분류를 보정하지 않는다.

- **Iris Description / 표현 계층**
  - 이미 확정된 사실과 결정을 정적 문장으로 변환한다.
  - 새 evidence를 만들거나 source를 재검증하거나 outcome을 재판정하지 않는다.
  - 3-3 개별 아이템 본문은 오프라인 생산 경로에서 생성·검증·봉인한다.

- **Browser / Tooltip / Wiki / 표시 계층**
  - 정렬, 접기, 패널 배치, 표시 밀도, 기본 노출 범위를 담당한다.
  - 표시 정책으로 데이터 계약이나 분류 의미를 바꾸지 않는다.

- **외부 산출물 / 추출기 계층**
  - Iris Core가 소비할 fact / outcome 산출물을 공급하는 외부 오프라인 생산 경로다.
  - 외부 산출물은 정규화와 검증을 거쳐 Iris 입력 계약으로 들어온다.

즉, **분류는 Core, 문장화는 Description, 표시는 Browser / Tooltip / Wiki, 외부 fact 생산은 추출기 계층**이 맡는다.

### Source / Action / Outcome / Evidence 원칙

Iris는 행동 자체를 canonical evidence로 쓰지 않는다.

- **Source**는 사실을 관찰한 경로다. Recipe, Right-click, Static capability는 source다.
- **Action**은 메뉴 노출, 클릭 경로, 행동명 같은 실행 표면 정보다.
- **Outcome**은 그 아이템이 없으면 성립할 수 없는 결과 상태다.
- **Evidence**는 source를 통해 정규화되어 Rule이 소비할 수 있는 fact / outcome 형태다.

Rule이 최종적으로 소비하는 것은 Source나 Action 자체가 아니라, 정규화된 **Outcome fact / Evidence**다.

따라서 `우클릭하면 ~할 수 있다`, `메뉴에 특정 항목이 뜬다`, `버튼이 있다` 같은 정보는 source 검증에는 쓰일 수 있어도 그 자체로 canonical evidence가 되지는 않는다.

### 자동 분류의 경계

Iris 자동 분류는 `아이템의 의미를 알아내는 시스템`이 아니라, **허용된 선언 증거를 누적하는 인덱싱 시스템**이다.

- 자동 분류의 canonical gate는 Evidence Allowlist다.
- 허용되지 않은 필드 / 문자열 / 연산은 자동 분류 근거가 아니다.
- `DisplayName`, `Description`, `DisplayCategory` 같은 표현용 텍스트는 분류 계약이 아니라 표시 표면으로 취급한다.
- Java 디컴파일, 런타임 추측, 표시 문자열 의미 복원은 canonical evidence world에 넣지 않는다.
- 수치 비교나 의미 추론은 기본 자동 분류 루트에 넣지 않는다.
- 증거가 부족한 축은 `unknown` 태그를 만들기보다 침묵한다.
- 반복적으로 필요한 예외만 manual override로 봉인한다.

Iris는 `더 많이 맞히는 분류기`보다 **경계를 넘지 않는 인덱서**를 우선한다.

### DVF / QG의 위치

DVF와 QG는 Iris의 정보 계층을 안전하게 생산·검문하기 위한 오프라인 체계다.

- **DVF**는 3계층, 특히 3-3 개별 아이템 본문을 생산·검증·봉인한다.
- **QG**는 자동 증거 / 분류 / 상호작용 산출물이 근거 없이 통과되거나 과장되거나 비결정적으로 바뀌지 않도록 막는 품질 게이트다.

DVF와 QG는 런타임에서 즉석 설명을 생성하는 장치가 아니다. 런타임은 봉인된 정보를 표시하는 역할에 머문다.

### DVF 3-3 생산 / 런타임 경계

DVF 3-3은 정보 생산 경로와 런타임 표시 경로를 분리한다.

```text
source -> facts -> decisions -> rendered -> Lua bridge -> runtime chunks
```

* source / facts / decisions는 정보 판단의 근거가 되는 생산 입력이다.
* rendered output은 확정된 정보를 사용자 문장으로 변환한 정적 산출물이다.
* Lua bridge와 runtime chunks는 런타임 표시를 위한 배포 산출물이다.
* 런타임은 배포 산출물을 표시할 뿐, source 검증이나 설명 재생성을 수행하지 않는다.
* current authority는 하나의 경로로만 유지하며, 생산 경로와 런타임 경로를 서로 대체하지 않는다.

Live Migration Readiness Authorization / Execution Readiness는 이 경로 위에 놓인 pre-apply gate이며, runtime mutation 계층이 아니다.

* `phase4_live_apply_allowed=true`는 Phase 4 live apply 실행 라운드를 열 수 있다는 뜻이다.
* `phase4_live_apply_allowed=true`는 source / rendered / Lua bridge / runtime chunk / package surface가 이미 live 변경됐다는 뜻이 아니다.
* readiness row는 `live_mutation_eligible`, `evidence_only`, `blocked` 중 하나로 분리한다.
* hard-forbidden runtime / package / Lua bridge surface는 live writer target이 될 수 없으며, successor source / rendered / authority proof가 있을 때만 evidence-only로 닫을 수 있다.
* future live apply는 sealed dry-run patch bundle과 같은 input identity를 가져야 하며, baseline hash / dirty target isolation / forbidden surface / writer capability gate를 실행 직전에 다시 통과해야 한다.
* readiness execution evidence root는 `phase0`부터 `phase10`까지의 machine-readable pre-apply gate evidence를 담는 staging surface다.
* readiness execution runner / validator는 authorization verdict를 execution plan이 소비할 artifact shape로 투영할 뿐, live writer sink를 열거나 current authority를 변경하지 않는다.
* `ready_for_phase4_live_apply`는 downstream predecessor status이며, live completion state나 release/package/Workshop/B42 readiness가 아니다.

Current-route required-validation manifest entries are governance gates, not runtime writers. A denominator guard can be adopted into `Iris/_docs/round3/current_route_required_validations.json` to fail-closed on denominator misuse in future closeouts. A shared disposition guard can also be adopted into the same manifest to make manifest / tools / docs / tests / validators consume the same disposition packet and to forbid raw audit / readiness / dry-run / predecessor artifacts as execution authority. These gates still leave runtime/source/rendered/package mutation, current authority cutover, release readiness, and canonical review status outside the manifest entry's authority.

`adopted` has two separate meanings in this area.

* `adopted_required_gate` is a governance manifest status for a required-validation gate.
* compose / runtime `adopted` is current-route row vocabulary. A runtime-adopted current-route row requires `body_source_overlay` before composition.

Neither meaning is QG quality pass / publish / delete / suppression semantics.

Full current-route closure depends on the current source baseline and source-overlay contract. The previous `CURRENT_FACTS=6` vs `2105` and missing `body_source_overlay` blocker for a runtime-adopted row was a Current-Route Baseline / Source-Overlay Repair issue, not a denominator, terminal disposition, shared disposition, or live migration readiness failure.

The repaired current-route contract uses `docs/dvf_3_3_current_route_baseline_source_overlay_repair_problem7_plan.md` as the canonical `primary_problem7_plan`. The predecessor repair plan is a `predecessor_contract_plan` only; it has no execution authority. The current-route build surface consumes the vNext source / overlay / rendered / runtime evidence contract consistently across compose, current-authority, and Layer4 trace consumers. `CURRENT_FACTS=6` is not the full current-route universe expectation, and predecessor `2105 / 2084 / 21` values do not become current hard gates, runtime authority, or current debt through this repair.

Closeout / Reentry Guard Seal is a governance-only current-route required gate. It keeps broad consumer completion, terminal disposition completion, cutover subset completion, pre-apply readiness, live apply authorization, and live migration execution completion as separate claim axes. Predecessor `2105 / 2084 / 21` may remain historical / comparison / provenance evidence, but cannot become current hard gate, runtime authority, current debt, package authority, release readiness, or raw predecessor direct execution authority. This gate does not mutate source, rendered, Lua bridge, runtime, or package authority surfaces. Its canonical seal is allowed after non-Claude independent review PASS and is represented by a hash-sealed primary review bundle that includes the final seal report, full current-route validation result, complete validation report, and claim-surface evidence. The live current-route manifest consumes this seal as a required validation gate rather than as runtime, package, release, or source authority.

Current Source Authority Drift Verification / Recovery Scope Retirement is a read-only verification and contingency-retirement boundary. The successor current source authority is `data/dvf_3_3_input_manifest.json -> data/dvf_3_3_facts.jsonl -> data/dvf_3_3_decisions.jsonl -> data/dvf_3_3_overlay_support.jsonl` under the vNext successor `2105` row identity, not an old predecessor recovery target. A stale `CURRENT_FACTS=6` premise cannot reopen source restoration when the live manifest, facts, decisions, and overlay support hashes/counts match the successor identity. Direct current compose verification must run through sandbox output sinks and may prove rendered parity / missing-overlay zero without mutating source, rendered, Lua bridge, runtime, or package surfaces. `Base.CanOpener` and the other 6-entry predecessor fixture payload members may remain historical / diagnostic / fixture trace, but cannot reenter current-looking source, rendered, runtime, or package paths. The old Recovery live-write plan is retained only as a future drift contingency that requires fresh drift evidence before any writer scope can be opened. Its canonical PASS seal records independent review and owner seal, but still does not claim current authority cutover, live migration completion, package/release readiness, manual in-game QA, semantic quality completion, or public text acceptance.

Current-Route Required Validation / Evidence Freshness Reseal is the governance seal that binds the current-route runner, live required-validation manifest, stored drift verification evidence, and round-local external validation bundle to one fresh readpoint. It consumes the successor `2105` source identity evidence and makes the live `current_route_required_validations.json` fail-closed on missing/skipped/failed required tests and required artifact field mismatches. Post-run external bundle and final closeout checks are not counted as current-route required tests; they are validated by the reseal wrapper, validator, and focused unittest surface. The official reseal wrapper does not expose a required-validation manifest override, while the lower-level runner keeps its override surface for sandbox fail-closed fixtures. This seal is canonical complete only after non-Claude independent review and owner seal PASS, and it remains governance-only: it does not mutate or authorize source, rendered, Lua bridge, runtime chunks, package payloads, release readiness, manual QA, semantic quality completion, or public-facing text acceptance.

Current Source Authority Drift Verification / Adoption Reseal is the governance seal that adopts the drift verification readpoint into the current-route required-validation chain after re-deriving the sealed drift evidence, evidence-freshness live-manifest consumption, source identity, taxonomy non-writer model, and branch-selection predicates. Its selected branch is `branch_a_required_gate_adopted`, and its live manifest mutation is additive required-gate adoption only. It keeps taxonomy execution on the live required-manifest union surface rather than making taxonomy the writer for this round. The `_dvf_3_3_vnext_common.write_jsonl` retry / atomic temp fallback is a runner write-sink mechanics repair for Windows `OSError 22`; it cannot change required sets, validation predicates, PASS interpretation, or any source/rendered/runtime/package authority. It is canonical complete only after current-route PASS, implementation-compression guard artifacts, non-Claude independent review, owner seal PASS, and VCS preservation of the related tool/test/docs/evidence and live required-validation manifest diff. This seal remains governance-only and does not mutate or authorize source, rendered, Lua bridge, runtime chunks, package payloads, release readiness, manual QA, semantic quality completion, public-facing text acceptance, or the broader clean-checkout required-evidence reproducibility preflight.

Durable Current Authority Surface Alignment is the governance seal that narrows DVF 3-3 durable tracked surface to source authority chain paths, the live required-validation manifest, current runner/taxonomy/closure governance files, essential guard and regeneration tooling, deployable runtime chunk authority, and live-manifest required adopted evidence. It explicitly separates generated staging evidence from durable current-required evidence: staging location alone is not durable status, and only required-adopted artifacts receive a tracked/not-ignored durability requirement. The guard keeps broad staging unignore forbidden, derives runtime chunk membership from `IrisLayer3DataChunks.lua`, records `dvf_3_3_input_manifest.json` as one primary source-chain role with a regeneration-manifest tag, and resolves rendered output as non-writer with `authority_claim=false`. This alignment closes the Adoption Reseal VCS-preservation and taxonomy-disposition preflight gates in the bounded durable-surface sense, while still not claiming source/rendered/Lua bridge/runtime/package writer authority, release/package/Workshop/B42/deployment readiness, manual QA, semantic quality, public-facing text acceptance, full clean-checkout required-evidence reproducibility, or full historical byte reproducibility.

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

### 하는 일

- Core 및 제품 모듈 비대화 방지
- helper / 편의 / 가이드 기능 수용
- `Pulse에 넣고 싶어지는 기능`을 플랫폼 밖에서 흡수

### 하지 않는 일

- Core 정책화
- 리소스팩 제품 축 수용
- 다른 제품 모듈 역할 흡수
- 플랫폼 채택 마찰 해소를 명분으로 Core에 들어갈 기능을 우회 수용한 뒤 다시 역이관하는 것
- Canvas/Frame 같은 별도 제품 축을 임시 운영하는 것

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

Canvas는 외부 파일, 프로젝트 폴더, `.pack`, ZIP + manifest / JSON을 입력으로 읽고, 필요하면 내부적으로 `.canvas` 같은 **정규화 캐시 / 분석 번들**을 사용할 수 있다.

다만 외부 공유 기본값은 열린 포맷을 우선한다.

- 기본 출력: `.pack`, `manifest.json`, 필요 시 ZIP 래핑
- 기본 공유: ZIP + JSON(+ `.pack`)
- 선택적 공유: 소스 ZIP + manifest, 문제 재현 / 분석용 `.canvas` 내부 정규화 번들

`.canvas`는 외부 공개 표준이 아니라 내부 처리, 검증, 캐시, 문제 공유를 위한 보조 포맷이다. 내부 기원 캐시 파일이라도 재로드 시 최소 검증을 거친다.

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
- Nerve → Pulse
- Iris → Pulse
- Frame → Pulse
- Cortex → Pulse
- Canvas → Pulse

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
   - Echo / Fuse / Nerve / Iris / Frame / Canvas / Cortex
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
