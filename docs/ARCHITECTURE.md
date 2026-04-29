# ARCHITECTURE.md

> 상태: 초안 v0.1 + addenda through 2026-04-24  
> 기준일: 2026-04-24  
> 상위 기준: `Philosophy.md`, `DECISIONS.md`  
> 목적: Pulse 생태계의 구조 지도, 역할 경계, 의존 방향을 고정한다.
> 읽기 규칙: 상단의 모듈 지도는 current canonical summary로 읽고, 뒤쪽의 날짜/라운드별 세부 섹션은 historical trace와 superseding detail로 읽는다.

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

병목 지점을 관찰하는 프로파일링 모드. 현재 1순위 설계 목표는 `더 많이 재는 것`이 아니라, **핫패스에서 시스템을 절대 흔들지 않는 순수 관측자**로 남는 것이다.

### 하는 일

- 계측
- 통계 수집
- 오버레이/리포트/관찰 결과 제공
- category / targetId / severity 같은 raw observation snapshot 생성
- 느린 경로에서만 설정/상태를 갱신하고, 핫패스에는 safe default를 주입

### 하지 않는 일

- 게임 동작 자체의 변경
- recommendation / priority / under-pressure 같은 정책 신호의 공용 노출
- 처리 모듈 라우팅 결정
- 다른 하위 모듈의 실시간 정책 입력원 역할
- Core 오염
- 타 하위 모듈 역할 흡수
- 핫패스에서 `PulseServices`, `EchoConfig`, DI / ServiceLocator, StackWalker, MXBean, blocking queue, 일반 로그, 풍부한 문자열 포매팅에 직접 의존하는 구조

### Bundle A 기준선

- 핫패스는 다음 4종으로 봉인한다.
  - tick 계측 entry / exit
  - scope push / pop
  - `SpikeLog.logSpike`
  - deep analysis 훅 콜백 수신부
- 이 경로의 표준은 **No-Throw / Fast-Exit / Fail-Soft / Safe Default** 다.
- 디버깅은 운영 경로를 오염시키지 않는 범위에서만 허용한다.
  - 릴리즈: 무음
  - 디버그: 세션당 1회 원샷 경고
- context capture는 옵션적 느린 경로로 격리하고, CAS 기반 rate-limit과 완전 무음 실패를 기본으로 둔다.
- Bundle A가 끝난 뒤에는 핫패스 변경을 쉽게 다시 열지 않는다.

### Bundle B / C 경계

- **Bundle B**: 증명 파이프 복구
  - Fuse가 왜 개입했는지 / 왜 개입하지 않았는지 / `0`이 실제 무개입인지 읽기 실패인지 구분 가능하게 만드는 리포트·provider·deep analysis 복구까지만 담당한다.
  - 핵심 증명 필드는 `present / active / snapshot_ok / total_interventions / reason_counts / error_code`로 고정한다.
  - `present`는 Echo가 registry 조회 결과로만 결정하고, provider는 `active / snapshot_ok / total_interventions / reason_counts / error_code` 같은 자기 상태만 보고한다.
  - `providers` 섹션은 deepAnalysis 옵션과 무관한 **항상-기록 증명 파이프**로 취급하고, `echo_profilers` 같은 부가 분석과 섞지 않는다.
  - Bundle B는 `증명 레이어`로 종료하며, 이 스키마와 필드 의미는 Bundle C에서 다시 흔들지 않는다.
  - Echo는 `severity / top_target / hint / insight` 같은 관측값으로 Fuse 행동을 간접 유도하지 않는다.
  - 정책 변경, 성능 개선, Fuse governor 조정은 포함하지 않는다.
- **Bundle C**: Fuse 정책 고도화
  - PASSTHROUGH / ACTIVE / Burst / Sustained 같은 정책 계층 수정은 Bundle C에서만 다룬다.
  - Bundle C의 기본 방향은 `더 강한 개입`이 아니라 `Sustained 감지 + Early Exit + ACTIVE 상한 + COOLDOWN + PASSTHROUGH 강제 복귀`다.
  - Bundle C는 `성능 기능`이 아니라 **자기규제형 safety layer**로 취급한다. sustained에서 Fuse ON이 더 끊기는 구조를 끊는 것이 목적이지, 개입 강화를 통해 더 많은 상황을 해결하는 것이 목적이 아니다.
  - sustained 감지는 v1에서 `ACTIVE 지속 시간 상한 + hard limit streak`의 최소 신호만 사용한다. 외부 원인 해석, 복합 윈도우, 적응형 추론은 넣지 않는다.
  - 기존 상태 의미는 유지한다. `isPassthrough()`는 평시 의미를 보존하고, COOLDOWN은 `isInterventionBlocked()` 같은 별도 의미로만 노출한다.
  - 상태 전이는 `transitionTo()` 단일 관문으로만 수행한다. 직접 상태 대입, 분산 타이머 초기화, 보조 경로의 임의 전이는 허용하지 않는다.
  - `hardLimitHitThisTick`는 `beginTick reset → hit에서 set → endTick에서 hit가 없을 때만 miss`의 3점 불변식을 유지한다. 이 지표는 성공 판정의 핵심 증명 신호다.
  - Bundle C의 공식 성공 판정은 `ACTIVE 장시간 유지 감소`, `PASSTHROUGH 강제 복귀 확인`, `hard_limit 연속 발생 감소` 같은 **리포트 기반 구조 변화**이며, `p50 / FPS / 평균 성능`은 참고 지표일 뿐이다.
  - Bundle B가 끝나 `0`의 의미를 분해할 수 있기 전에는 Bundle C를 열지 않는다.
- A/B/C는 순차·독립 단계다. A를 끝내기 전 B를 열지 않고, B를 하면서 C를 끼워 넣지 않는다.

### Core와의 관계

Pulse capability를 소비하지만, 프로파일링 로직은 Echo 내부에 남긴다. Snapshot 갱신 주기(`updateSnapshot()` 같은 경로)도 Echo 내부 tick 경로가 소유하며, Core나 다른 하위 모듈이 이를 호출·통제하지 않는다. 핫패스는 외부 서비스/설정 조회 대신 **`EchoConfigSnapshot` + `EchoRuntimeState` + `volatile` 단일 참조** 구조로 필요한 상태를 주입받는다. Bundle A의 범위는 **Echo 내부 수술**까지만이며, Pulse SPI 계약 변경이나 다른 번들 범위 선반영은 여기서 다루지 않는다. Bundle B의 Fuse 증명도 **Pulse SPI를 경유한 관측**이어야 하며, Echo가 Fuse를 직접 import하거나 정책 판단을 대신하지 않는다. 또한 Bundle B에서 Echo는 provider map을 직접 mutate하거나 `0`을 해석해 추천·처방으로 바꾸지 않고, **존재(present) 증명과 snapshot 기록**까지만 담당한다.

---

## 2-3. Fuse

### 정체성

Mixin 기반 엔진 비용 질서화 / 안정화 모드. **동일 결과를 더 싸게 만드는 semantic-preserving 최소 개입**을 기본 레인으로 두며, 목표는 전면 가속보다 **지속 붕괴 상태 차단, 평균 FPS 방어, 프레임 붕괴 방지**에 가깝다. 특히 Fuse는 `AI 자체를 최적화하는 모드`가 아니라 **AI 부하 폭주 때문에 엔진이 오래 무너지는 상태를 차단하는 엔진 안정성 레이어**다. 경로탐색/충돌/물리 축에서도 `더 잘 찾는 모드`가 아니라 **찾는 동안 게임이 무너지지 않게 하는 안정성 레이어**다.

### 하는 일

- 엔진 레벨 병목/스파이크 완화
- 구조적 비용 절감
- 프레임타임 꼬리 완화
- pressure signal 감지와 governor / backoff / cooldown / fail-soft 기반 통제
- Echo 실시간 수치 주입이 아니라 **자기 pressure signal과 내부 상태**를 기준으로 한 판단
- 핵심 실전 가치는 Area 1 / Area 7에 두고, IO/GC는 우선 `관측·분류·보험성` 축으로 다룸
- 현재 메인라인에서는 IO/GC Guard 동작 코드보다 **계측·분류·호환 흔적 유지**를 우선하며, Guard 자체는 제거/동결 가능한 부차 기능으로 본다
- Fuse는 **Burst stabilizer**이지 sustained load optimizer가 아니다. 지속 과부하에서는 더 오래 버티는 것보다 `retreat / PASSTHROUGH / vanilla 복귀`가 우선이다.
- Bundle C에서도 이 원칙은 유지된다. Sustained 감지는 Fuse 내부의 자기 상태와 상한 신호만으로 보수적으로 수행하며, 외부 해석이나 Echo-driven control로 확대하지 않는다.
- 현재 Fuse는 A/B/C와 tick duration 입력 경로 수정까지 닫힌 뒤 **확장 중심이 아니라 동결·회귀 검증·설명 정리 중심**으로 운영한다.
- 다만 이는 `영구 동결`이 아니라 현 시점의 **전략적 보류**이며, 필요하면 Area 1 / Area 7의 누락·봉인 상태를 점검하는 **보수적 정산 재진입**은 허용한다.
- 따라서 `autoOptimize` 같은 자동 판단 / 자동 적용 경로는 메인라인에서 다시 살리지 않으며, 남아 있더라도 `AUTO_OPTIMIZE_FROZEN` 수준의 봉인 또는 정리 대상으로 본다.
- raw observation을 읽더라도 임계값 판단 / recommendation 생성 / optimization 적용은 Fuse 내부에서만 수행
- 다음 5개 구역의 비용 폭주 통제
  - 좀비 AI / 업데이트 스텝
  - 라이팅 / 가시성 / 렌더 스파이크
  - 경로탐색 / 충돌 / 물리
  - 세이브 / 로드 / IO 스톨
  - GC / 할당 압력
- 단, 세이브/로드/IO와 GC/할당 압력은 현재 제품 포지션상 `반드시 체감 고점을 내야 하는 핵심 축`이 아니다. 렌더/타일/세이브/DB commit 같은 **엔진 비분할 덩어리 프리즈**는 Fuse가 반드시 이겨야 할 대상이 아니며, 이 축은 필요 시 동작 가드를 제거/동결하고도 관측/분류 surface를 남길 수 있는 보조 영역으로 본다
- 경로탐색 / 충돌 / 물리 축에서는 `guard / limit / defer / deduplicate / stabilize`만 허용
- defer-only NavMesh query guard, tick-local duplicate filter, TTL=1 collision memo, fail-safe panic protocol 같은 **의미 보존형 안전장치** 적용

### 하지 않는 일

- 엔진 포크
- 알고리즘 재작성 / 구조 재작성 전제의 전면 최적화
- 결과가 달라질 수 있는 근사/공격적 알고리즘 교체의 기본화
- `모든 엔진 영역을 빠르게 만드는` 거대 모드 지향
- 경로 알고리즘 변경
- 충돌 판정 규칙 변경
- 물리 결과 변경
- AI 의미 변화나 인지 타이밍 개입을 1차 범위에 포함
- 모든 대형 프리즈를 Fuse가 반드시 해결해야 한다는 식의 과잉 약속
- sustained overload에서 상시 분산 개입을 유지해 잔렉을 깔아버리는 정책
- `deep analysis 0` 상태를 Fuse 미작동으로 단정한 채 정책을 조정하는 설계
- Pulse 정책 인터페이스나 Fuse UX/명령 체계 도입
- Core 내부화
- Lua 안정화 역할 흡수

### Core와의 관계

Pulse capability를 소비하지만, 엔진 안정화 로직 자체는 Fuse에 둔다. Pulse는 사실과 capability만 제공하며, `IPathfindingPolicy` 같은 정책 인터페이스를 품지 않는다. Fuse는 Pulse capability 위에서 defer / budget / memo / clamp / fail-safe를 조합해 자기 governor를 구성한다. Echo가 관측한 데이터는 Fuse가 참고할 수 있지만, 그 해석과 조치 결정은 Fuse 내부 계약으로 다시 닫힌다. legacy `OptimizationHint` 같은 구경로가 남더라도 중심 경로가 되어서는 안 된다. 또한 Fuse는 `건드릴 수 없는 프리즈를 모두 떠안는 레이어`가 아니며, 큰 비분할 스톨은 관측/분류에 머무를 수 있다.

---

## 2-4. Nerve

### 정체성

100% Lua 기반 **선택적 안정성 Guard**. **Lua 자체를 고치는 모드가 아니라, Lua를 제어면으로 사용해 멀티/모드팩 환경의 상위 레이어 지연과 충돌을 완화하는 모드**다. 또한 Nerve는 **완전한 무의 공백지대**가 아니라, coalesce·dirty flag·읽기 전용 캐싱 같은 기법 조각은 있으나 이를 **완성형 답안처럼 직접 이식할 수 없는 공백지대**를 다루는 연구 모듈로 본다.

### 하는 일

- 이벤트 디스패치 / 모드 훅 / 네트워크 동기화 레이어의 완충
- 스파이크 / 프리즈 완화와 작업 겹침 감소
- 기본값 기준으로는 **바닐라와 동일한 의미를 유지**하고, 위험 징후를 관측·경고·철수하는 Lua control-plane 안전장치 제공
- 기능 모드가 아니라 **실패 축적과 회복 시간 검증**을 위한 연구 장치 성격 유지
- 연구의 기본 출력은 `더 좋은 기법 목록`이 아니라 **Failure Atlas / 금지 규칙 / 철수 조건 / 비개입 조건**이다
- Nerve에 허용되는 정책은 **자기 제한 정책**뿐이며, 게임 행동을 바꾸는 정책·중요도 판단·주기 변경·스킵 정책은 허용하지 않는다
- `OFF가 더 안전`하다는 말은 체감 우열이 아니라 **baseline safety / 책임 귀속 기준선**을 뜻한다
- 멀티/모드팩 환경에서 선택적으로 켜둘 수 있는 안정성 Guard 역할
- Fuse가 직접 다루기 어려운 프리즈의 **Lua 측 트리거 조건**(이벤트 폭주, 재귀, 충돌, UI/컨테이너 계열의 열차형 스파이크)을 드러내고 마지막 순간에만 보수적으로 막는 상위 완충 가능성
- **Area 6**은 `이벤트를 정리하는 최적화`가 아니라 **문제 발생 시 리스너 단위로 격리하고 곧바로 철수하는 보수적 안전 레이어**다. 제어 트리거는 same-tick self-recursion 또는 listener exception으로 한정하고, `EventRecursionGuard` / `SelfRecursionGuard` 같은 최후 가드만 남긴다.
- 전수 커버가 목표라면 `Events.*.Add` 전수 래핑은 사실상 필요하다고 본다. 이는 미관이 아니라 **제품 책임과 커버리지**의 문제이며, 대체 불가능한 만큼 제거보다 관리 가능성을 우선한다.
- Area 6의 고위험은 `기술적으로 불가능`해서가 아니라 **호환성 충돌과 책임 귀속**이 집중되기 때문에 생긴다. 따라서 평가는 `침묵 금지 / 피해 반경 제한 / 원인 분해 / Nerve OFF 즉시 복구`의 네 조건으로 한다.
- Area 6의 하이브리드는 `전부 섞기`가 아니라 **단일 트리거 / 단일 행동 / 보조 증거 결합** 원칙을 뜻한다. 행동은 `listener-unit fail-soft isolation + same-tick pass-through retreat` 하나로 봉인하고, 깊이/fan-out/반복/동일성은 incident 후 보조 증거로만 쓴다.
- **Area 5 v0.1**에서는 UI / 인벤토리 영역에서 `데이터 즉시 + 같은 틱 시각 coalescing + 의미 불변 + fail-soft bypass`를 만족하는 최소 안정화
- **Area 9**는 `멀티 최적화`가 아니라 **멀티/네트워크 경계 Lua 자폭을 같은 틱 안에서 끊는 안정성 레이어**다. 역할은 `네트워크를 해결`하는 것이 아니라 **멀티에서 Lua가 자폭하려는 순간 1틱만 물러나는 보험**에 가깝다. 허용되는 재료는 `재진입 가드`, `중복 가드`, `Shape Guard`, `Chain Depth Guard`, `incident-gated guarded pcall`, `틱 단위 철수`, `최소 포렌식` 같은 좁은 방어 프로그래밍 조각뿐이다.
- Area 9의 기본 봉인선은 **기본 OFF / 네트워크 진입 훅 한정 / 대상 opt-in + 행동 opt-in 분리 / 동일 틱 철수 / 다음 틱 자동 복귀 / incident-gated pcall only**다.
- Area 9의 구현 안전핀은 `tickId 단일 진실의 소스`, `endpoints 폐쇄 목록`, `incident 단일 플래그`, `quarantine 최소 key 범위` 네 가지로 둔다.
- Area 9의 1~7 가드는 먼저 **관측·표시·계수**로만 연결하고, 실제 행동은 마지막의 **same-tick retreat 하나**로만 연결한다. Duplicate/Shape/Depth의 결과를 점수화·가중치화·다틱 격리로 연결하지 않는다.
- 다른 Lua 모드가 활용 가능한 라이브러리성 기능 제공 가능

### 하지 않는 일

- 바닐라 싱글 평균 FPS 향상을 주 목적으로 하는 성능 모듈화
- 바닐라 Lua 자체를 상시 병목으로 가정한 전면 최적화
- 성공적인 S5를 근거로 한 필수 모듈화
- Mixin 기반 엔진 최적화 흡수
- Core 내부화
- 위키/팩 관리/리소스 관리 역할 흡수
- Area 6에서 `priority / governor / throttler` 같은 정책 엔진화
- Area 6에서 의미 기반 allowlist / whitelist / AlwaysAllow 같은 예외 정책
- Area 6에서 `coalesce + flush`, 지연·재정렬·넓은 global fallback으로 의미를 바꾸는 개입
- Area 6에서 래퍼 체인 고도화로 충돌을 이기려 드는 설계
- Area 9를 `핑 개선`, `패킷 최적화`, `서버 부하 분산`, `엔진 동기화 수정`으로 설명하거나 구현하는 것
- Area 9에서 전역 상시 `pcall`, 자동 우선순위 판단, 영구 차단, 지연/병합/재정렬을 기본 경로로 두는 것
- `defer` / 틱 넘김 캐시 / 시간 기반 debounce를 전제로 한 UI 안정화
- `drop` 같은 의미 손실 정책
- `isVisible()` / visibility 기반 flush 판단
- Area 5와 Area 6의 상태 공유 또는 코드 직접 의존
- Pulse로의 기능 상향 이동
- 공격적인 batching, 조기 `ItemTransferBatcher` 투입 같은 범위 외 확장

### Core와의 관계

Pulse capability를 소비하지만, Lua 안정화 로직은 Nerve 내부에 남긴다. 같은 모듈 내부 공유는 Nerve 내부에서 처리하고, **타 모듈 공유가 실제로 필요할 때만** Pulse SPI를 경유한다. Echo의 일반 카테고리 관측은 참조할 수 있어도, **분석 리포트의 소유자는 Echo**로 유지하며 Nerve는 별도 리포트 시스템을 만들지 않는다. Nerve 고유 상태는 Echo Deep Analysis 계약으로 승격하지 않고, 운영상 필요한 최소 상태 노출/사건 표식/에러 서명만 Nerve 표면에 남긴다.

### 계열 / 배포 경계

- **Nerve**: Pulse 비의존 핵심 기능 스탠드얼론. `안정성 코어`가 여기에 있다.
- **Nerve+**: Pulse 의존 핵심 + 편의 계열. 더 강한 정답판이 아니라, 배포/운영 편의를 얹은 상위 오버레이로 취급한다.
- 이 구분의 목적은 기능 우열이 아니라 **채택 마찰 제어와 Core 오염 방지**다. 따라서 `Lite vs Full` 같은 제품 서사는 구조적으로 피한다.

### 현재 연구 단계

- 현재 Nerve는 **Failure Atlas를 구축하는 단계**이면서, 그 atlas를 바탕으로 **Area 6 완료 / Area 5 v0.1 Final 동결**까지 확보한 상태다. 동시에 생태계 전략상으로는, Fuse가 실전 증명 단계에 들어간 뒤 **다음 확장 축으로 다시 검토되는 모듈**이다. 최상위 판정 기준은 과거 핸드오버가 아니라 **`Philosophy.md` 하나**로 둔다.
- Area 5·6에서 정리한 실패 축들은 `검증 후 제거할 가설 목록`이 아니라, 자연 발현 실패를 빠르게 **어느 칸에 귀속할지 결정하는 좌표계(axis)** 로 취급한다
- 따라서 현재 연구 방법은 `성공 사례를 확장`하는 방식이 아니라, 실패를 축에 귀속시키고 그 축별 **금지 규칙 / 철수 조건 / 비개입 조건**을 축적하는 방식이다
- 그러나 현재의 **실질 상태는 Area 5·6 실행 복구와 증명 강화**, 그리고 **Area 9 구현·코드 검진까지 마친 뒤 동결·운용 판단 단계**에 가깝다. Area 9는 더 이상 `열 수 있는가`를 묻는 기초공사 문서가 아니라, **같은 틱 1회 철수형 보험 장치가 실제 멀티에서 유지 가치가 있는지 판단하는 코어**로 본다.
- 기본 관측 세팅은 **Echo ON / Fuse OFF / Nerve OFF**이며, 멀티 검증은 실제 친구들과의 플레이, 실제 모드팩, 실제 동시 행동에서 Echo 리포트를 조용히 수집하는 방식으로 둔다.
- **Area 9(네트워크/멀티)** 는 `관측만 허용` 단계도 아니고 `멀티를 해결하는 기능`도 아니다. 대신 **멀티/네트워크 경계에서 Lua 레벨 자폭을 동일 틱 한정으로 끊는 100% Lua 안정성 레이어**로 유지하고, 역할은 `세션 자폭을 같은 틱에 끊고 다음 틱 바로 복귀하는 보험`으로 한정한다.
- 따라서 현재 Area 9의 성공 기준은 `더 똑똑한 판단`이 아니라 **사건이 없으면 조용하고, 사건이 터지면 1틱만 물러나며, 그 이상으로 커지지 않는 것**이다.
- 이후 단계는 새 기능을 붙이는 것이 아니라 **운영 데이터 수집 → 유지/폐기 판정 → 다음 생산적 이동(Iris)** 이다. Duplicate early-skip, Echo 분석 재사용, 다틱 격리, 네트워크 의미 해석은 다시 열지 않는다.
- Nerve Area 5·6의 설계 토론은 **로드맵 v2.1에서 닫힌 상태**로 본다. 현 단계에서 v2.1은 더 다듬는 설계 문서가 아니라, 구현 충실도와 런타임 증명을 묶는 **구현 기준서 / 집행 헌법**이다.
- 따라서 현재 Nerve의 고도화는 새 기능 추가보다 **개입 경로 증명 / 의미 불변 증명 / 재현성 강화 / 구현 전·후 기초 안정성 결함 정리 / 실패 축적과 회복 시간 검증**을 뜻한다.
- Nerve Area 5·6의 실행 기준은 로드맵 **v2.1 구현 기준서**에 두며, classifier 제약·`os.clock()` 위상·SharedFlags 범위·후속 이벤트 정의를 그 기준선으로 유지한다.
- 단, **Area 6은 긴급 수정 기준으로 더 보수적으로 재잠금**한다. 기본값은 `enabled = false`, `strict = false`이며, default에서는 바닐라와 의미가 같아야 한다. `EventDeduplicator` 계열은 폐기하고, `EventRecursionGuard` / `SelfRecursionGuard` 같은 자기-재귀 자폭 방지 가드와 listener-unit fail-soft 격리만 남긴다.
- Area 6에서 충돌이 감지되면 해결보다 철수가 기본이다. `Events.Add` 래핑 충돌은 체인 정교화보다 **Area 6 OFF back-off**로 처리한다. 현재 구현은 Kahlua 제약 때문에 `pcall` 기반 listener-unit 격리를 사용하되, incident / passthrough / rate-limited log를 남겨 `숨긴 오류`가 아니라 `가둔 오류`로 설명 가능해야 한다. Strict 차단은 `[!] LAST-RESORT DROP`처럼 명시적으로 노출한다.
- 현재 운용 중인 Area 6은 `근본 해결이 완료된 기능`이 아니라 **incident 수집과 외부 붕괴 차단을 위한 임시 방파제**로 해석한다. 따라서 구현 승인과 운영 지속 가능성 승인을 동일시하지 않고, incident 리스너 수정과 `enabled=false` 복구 여부 판정이 후속 과제로 남는다.
- 현재 Area 6의 직접 과업은 새 기능 설계가 아니라 **실행 가능 상태 복구**다. 즉, Lua vararg/문자열 결합 오류 제거, Java 문법 오류 제거, `OnTick` 단일 진입점 정리 같은 최소 수정만 허용된다.
- same-tick 판정과 incident 귀속은 진입점이 하나일 때만 설명 가능하므로, `OnTick` / `OnTickEven` / start-end 이중 등록 혼선은 기능 미세조정보다 우선해 정리한다.
- 구현 착수 전에는 기능 로드맵과 별도로 **레포 신뢰성 / 재현성 게이트(P0~P2)** 를 먼저 통과한다.
  - **P0**: conflict marker 제거, `NerveUtils.lua` 실코드 문법 확인
  - **P1**: `OnTickEven`이 의도인지 실수인지 고정
  - **P2**: fail-soft / 예외 전파 정책을 코드와 문장 수준에서 통일
- Area 5/6 이후의 확장은 자동으로 열지 않고, 반드시 **전장 판결 → 외부 조건 충족 확인 → 최소 스코프 → v0.x 범위 결정** 순서로만 연다.
- Area 5와 Area 6은 개념상 연속될 수 있지만, 현재 기준선에서는 **코드 의존 없이 독립된 최소 안정화 축**으로 유지한다. 역할은 `Area 6 = 원인 차단`, `Area 5 = 결과 체감 보호`로 분리한다.
- 멀티는 유용한 가속 수단이지만 구조상 필수 전제는 아니다.

---

## 2-5. Iris

### 정체성

100% Lua 기반 위키형 정보 모드.

### 하는 일

- Alt 툴팁 확장
- Iris 메뉴 기반 세부 정보 제공
- 증거 시스템 기반 분류/설명
- 실용 정보 제공
- 구조화된 외부 모드 데이터를 정규화해 위키 표면으로 렌더링

Iris는 단순한 `정보 추가 모드`가 아니라, **게임 코드와 데이터에 숨어 있는 행동·용도·관계 의미를 유저 언어로 드러내는 구조적 위키 시스템**으로 본다. 경쟁력도 개별 레시피/우클릭 기능보다 이 전체 구조에서 나온다.

### 하지 않는 일

- 해석
- 권장
- 비교
- 설명 단계의 의미 보정
- Core 내부화

### 내부 구조

Iris 내부는 최소 다섯 계층으로 나눠서 본다.

- **1단계: Source 추출 계층**
  - Recipe source extractor
  - Right-click source extractor
  - Static capability source extractor
- **2단계: Evidence / outcome 정규화 계층**
  - Source별 신호를 outcome / field / recipe relation 같은 원자 증거로 정리
- **3단계: Layer 3 production 계층**
  - `facts -> decisions -> compose -> normalizer -> style linter -> rendered -> Lua bridge`
  - `compose_layer3_text.py`가 본문 조합과 style normalizer 연결을 맡고, style linter는 advisory report만 생성하며, `export_dvf_3_3_lua_bridge.py`가 최종 rendered를 Lua 소비자 표면으로 넘긴다.
  - current default compose authority는 `compose_profiles_v2.json + body_plan`이며, legacy `sentence_plan` path는 explicit compatibility/diagnostic mode로만 남는다.
- **4단계: Review / freeze 운영 계층**
  - packet 생성
  - review.jsonl 수동 판정
  - freeze / action queue / coverage summary 생성
- **5단계: Runtime 소비 계층**
  - `IrisWikiSections.lua`, `IrisBrowser.lua`, `IrisWikiPanel.lua` 같은 기존 Iris 소비자가 Layer 3를 실제로 렌더링한다.

여기서 중요한 점은 **Right-click source가 Recipe source의 변주가 아니라 독립 추출 트랙**이라는 것이다. 다만 이 분리는 추출 단계에만 머문다. Iris 내부의 canonical Evidence 모델과 Rule 소비 구조는 **Outcome 중심 단일 프레임**을 유지하며, `right-click 전용 분류기`를 따로 만들지 않는다.

또한 Layer 3는 `수동 문장 저장소`가 아니라, **오프라인에서 facts/decisions/rendered를 생산하고 Lua bridge를 통해 게임에 올리는 생산 시스템**으로 본다.

### Layer 3-3과 interaction cluster의 관계

interaction cluster는 4계층의 상세 상호작용 목록을 3계층으로 그대로 끌어오는 계층이 아니다. 역할은 **4계층이 담는 상세 구조에서 대표 작업 맥락만 추출해 3-3의 `primary_use`를 보강하는 요약층**에 있다.

- direct use가 충분하면 cluster는 끼어들지 않는다.
- direct use가 너무 약하거나 role fallback이 공허할 때만 cluster summary가 `primary_use` 후보가 된다.
- 목록 / 재료 / 조건 / 행동명은 여전히 4계층에 남는다.

즉, cluster는 3-3이 4계층을 먹게 만드는 장치가 아니라, **3-3이 item-centric 본문을 유지하면서도 과추상을 피하게 하는 중간 요약층**이다.

### current historical runtime의 active / silent 의미

current historical runtime 경로에서 `active / silent`는 **cluster 보유 여부**로 갈리지 않는다. 실제 스위치는 최종 `primary_use` 존재 여부다.

- `direct_use`, `cluster_summary`, `role_fallback`, `identity_fallback` 중 하나로 `primary_use`가 채워지면 active
- 끝까지 `primary_use`를 만들지 못하면 `demote_missing_primary_use_rows()`가 `state = silent`, `reason_code = MISSING_PRIMARY_USE`로 강등

따라서 current `active_composed` 수치는 semantic quality 완료 수치가 아니라, **runtime에 올릴 수 있는 row 수**에 가깝다. `hard_fail_codes`, `v9_warn`, `policy_excluded`는 지금 당장 silent를 만드는 직접 스위치가 아니며, 현재 active 안에는 identity fallback 같은 salvage row도 포함될 수 있다.

### UI formatting과 데이터 계약의 분리

Layer 3 줄바꿈은 current 구조에서 **render-time only** 로 처리한다.

- `rendered.json` 원문 유지
- `IrisLayer3Data.lua` 원문 유지
- UI 소비자에서만 line formatting 적용

즉, display formatting은 Browser / Wiki 표면 책임이고, production 산출물 계약(`rendered ↔ Lua`) 자체는 그대로 유지한다. 이 때문에 current validation도 데이터 일치 규약은 유지하고, UI formatter 존재 / panel 개행 렌더만 별도 회귀로 관리한다.

### 헌법과 하위 명세

Iris 관련 판정의 최상위 기준은 **`Philosophy.md` 하나**다. Allowlist, Evidence Table, DSL, 입력 계약, 설명 파이프라인, 구현 체크리스트는 모두 이 철학을 기계화한 **하위 명세**로 취급한다. 따라서 충돌이 생기면 `Philosophy.md`를 우선하고, 하위 문서는 `왜 그렇게 해석해야 하는가`를 새로 발명하지 않는다.

### 자동 분류의 경계

Iris 자동 분류는 `아이템의 의미를 알아내는 시스템`이 아니라, **바닐라가 텍스트로 선언한 증거만 누적하는 인덱싱 시스템**으로 둔다.

- 자동 분류의 canonical gate는 **Evidence Allowlist**다.
- 허용되지 않은 필드/문자열/연산은 자동 분류 근거가 아니다.
- `DisplayName` / `Description` / `DisplayCategory` 같은 표현용 텍스트는 설명 표면일 뿐, 분류 계약이 아니다.
- 수치 비교는 평가·판정 시스템으로 미끄러지기 쉬우므로 기본 자동 분류 루트에 넣지 않는다.
- 아이템은 여러 태그를 누적할 수 있지만, 태그 제거·우선순위 부여·의미 재해석은 하지 않는다.

즉, Iris는 `더 많이 맞히는 분류기`보다 **경계를 안 넘는 인덱서**를 우선한다.

### 자동 분류가 보는 세계

Iris가 자동 분류 근거로 인정하는 세계는 **바닐라가 외부에 텍스트로 선언한 데이터**까지다.

- 주 근거: `media/scripts/*.txt`, `media/lua/client/*` 같은 선언형 텍스트 surface
- 비근거: Java 디컴파일로 얻은 엔진 내부 의미, 런타임 추측, 표시 문자열 의미 복원

이는 `더 파면 알 수 있는가`와 `Iris가 자동 분류해야 하는가`를 분리하기 위한 경계다. 엔진 내부는 사람이 이해하는 참고가 될 수는 있어도, Iris 자동 분류의 canonical evidence world는 아니다.

### 침묵과 수동 오버라이드

Iris는 `모름`을 새 태그로 만드는 쪽보다, **아는 것만 누적하고 나머지는 침묵하거나 수동 오버라이드로 봉인하는 쪽**을 택한다.

- `4-UNK` 같은 미분류 태그는 두지 않는다.
- 바닐라 선언 증거가 충분하지 않은 축은 silence가 기본이다.
- 반복적으로 필요한 예외만 manual override로 닫는다.
- manual override는 자동 분류를 대체하는 제2 엔진이 아니라, **텍스트 선언 바깥의 예외를 봉인하는 안전핀**이다.

### 대분류 Evidence Table의 역할

Tool / Combat / Consumable / Resource / Literature / Wearable Evidence Table은 `더 잘 나누는 의미론 사전`이 아니라, **전 대분류 수준의 자동/수동 경계 계약**이다.

- 각 대분류는 의미를 추정하는 온톨로지가 아니라 **연결 인덱스**다.
- 하나의 아이템은 여러 대분류/소분류에 동시에 속할 수 있다.
- 분류기는 누적만 하고, UI가 컨텍스트에 따라 무엇을 먼저 보여줄지 조절할 수는 있어도 **분류 간 우선권은 정의하지 않는다**.
- 증거표를 더 만지는 대신, 철학 위반 없이 자동화할 수 없는 축은 침묵 또는 수동 오버라이드로 넘긴다.

### Tag 네임스페이스 경계

`MoveablesTag`와 Item Script의 일반 `Tags`는 같은 네임스페이스로 합치지 않는다.

- 둘은 선언 위치와 의미 범위가 다르다.
- allowlist를 느슨하게 만들수록 규칙 작성자가 임의 태그를 자동 분류 근거로 확대할 수 있다.
- 따라서 Tag 허용은 **허용 필드 + 허용값 조합**으로만 닫고, Moveables 계열은 별도 계약으로 유지한다.

### 계층 분리 원칙
### 문서화 담당자의 역할

Iris의 문서화/설명 담당자는 **분류·규칙·증거를 바꾸는 사람**이 아니라, 이미 확정된 사실을 위키식 정적 문장으로 풀어쓰는 **후행 서술자**다.

- 설명은 새 evidence를 만들지 않는다.
- 설명은 분류를 재판정하지 않는다.
- 설명은 확정된 사실을 사람이 바로 이해할 언어로 바꾸는 역할만 맡는다.

즉, 문서화는 `설명을 멋있게 쓰는 작업`이 아니라 **확정된 사실을 안전하게 인간 언어로 변환하는 작업**이다.

### 정보 작업의 선후 관계

Iris의 개별 아이템 정보 작업은 다음 순서로 고정한다.

1. 분류/증거 체계 고정
2. **Outcome source 사실 검증**
3. 필요한 결과 상태(Outcome) 고정
4. 필요 시 개별 설명 문장화

핵심은 설명을 먼저 쓰지 않는 것이다. Source 사실과 outcome fact가 잠기기 전에 설명을 먼저 쓰면 추측과 재작업이 발생하기 쉽다. 따라서 현재 단계의 1차 산출물은 source 확인과 outcome fact table이며, 개별 설명은 이 테이블을 바탕으로 후행 파생물처럼 작성한다.


Iris 내부는 적어도 세 층으로 나눠서 본다.

- **Iris Core(분류 계층)**: Evidence 기반 분류만 수행한다. 여기서 하는 일은 관측된 증거를 분류 결과로 고정하는 것이지, 의미를 해석하거나 사용자 친화적으로 재설명하는 것이 아니다.
- **Iris Description(표현 계층)**: 문장 생성기나 요약기가 아니라, 이미 고정된 정보를 템플릿 순서대로 출력하는 계층이다. 책임은 **출력 순서와 블록 조합**까지이며, 분류 기준을 바꾸지 않는다.
- **Iris Browser(탐색/UI 계층)**: 정렬, 표시 정책, 기본 노출 범위를 다룰 수 있지만, 분류 로직이나 Evidence 판단에는 개입하지 않는다.

즉, **분류는 Core, 표현은 Description, 표시 정책은 Browser**가 맡는다.

### 설명 출력 규칙

Iris 설명은 소분류 블록 중심 출력이 아니라, 다음의 정보 위계로 고정한다.

1. 기본 정보
2. 의미(주 소분류)
3. 활용(레시피/상호작용)
4. 메타

이는 UI 취향 문제가 아니라 **설명 생성 파이프라인의 출력 규칙**이다. 따라서 Description 계층은 문장을 새로 해석·요약하지 않고, 이 위계에 맞춰 템플릿을 조합한다.


### 주 소분류(anchor)와 설명 템플릿의 권한 분리

`primary_subcategory`는 유지한다. 다만 역할은 **설명의 자동 근거**가 아니라, 우선 **브라우징과 탐색을 안정화하는 anchor**다.

- Browser는 이를 탭 기본 정렬, 기본 진입 의미, 메타 노출에 사용할 수 있다.
- Description은 이를 모든 아이템에 자동 적용되는 기본 문장 권한으로 쓰지 않는다.
- 따라서 주 소분류 설명 문장은 `삭제 대상`이 아니라 **후보 템플릿**이며, 맞는 경우에만 제한적으로 소비된다.

즉, 이번 경계선은 `주 소분류를 버린다`가 아니라 **`anchor 권한과 설명 권한을 분리한다`** 쪽에 있다.

### 분류 노출과 메타 정책

분류 데이터는 삭제하지 않는다. 다만 기본 UI에서는 이를 전면 노출하지 않고, 필요 시 **메타 영역에 격리**한다. 이는 관측 데이터와 사용자 기본 노출을 분리하는 정책이며, `분류를 숨긴다 = 분류를 지운다`를 뜻하지 않는다.

### 교집합 / 다중 태그 해결 원칙

다중 태그 문제는 브라우저 정렬만으로 해결하지 않는다. 해결 위치는 **primary_subcategory 메타 anchor**다.

- Evidence와 DSL은 유지한다.
- 분류 자체를 다시 해석하지 않는다.
- 수치 비교나 휴리스틱을 넣지 않는다.
- Browser는 이 anchor를 소비해 표시 순서와 기본 의미 노출을 안정화할 수 있지만, anchor를 스스로 만들어내지 않는다.

즉, 교집합 문제의 본질은 `정렬 문제`가 아니라 **주 소분류(anchor) 명시 문제**다.

### 목록 중복과 표현 접기

중복 아이템 목록 문제는 **기능 동등성 판정 엔진**으로 풀지 않는다. 이번 세션에서 실제로 필요한 것은 `같은 아이템인지 최종 판정`하는 일이 아니라, **목록의 가독성을 높이기 위한 표현 접기**였다.

- 빌드 타임 전역 그룹화(`equivalence_key`, `ItemGroups`, `ItemToGroup`)는 기본 해법에서 제외한다.
- UI 목록에서는 **DisplayName 중심 접기**를 사용할 수 있다.
- 다만 Type, 서브카테고리, 레시피/우클릭 존재 유무 같은 차단 가드를 둬서 오접기를 막는다.
- 데이터·분류·빌드 산출물은 바꾸지 않고, **표현 레이어에서만** 접는다.

또한 접힌 목록은 `감자칩 (x4)`처럼 수량 배지를 붙이지 않고 **개념명만** 보여준다. 변형 수와 실체 차이는 상세 패널에서만 본다. 즉, `목록은 개념 / 상세는 실체`가 이 계층의 원칙이다.

### 책임 위치와 디버깅 우선순위

Iris의 표현 왜곡은 우선 **표현 계층의 지능 부족**으로 보지 않는다. 책임 우선순위는 다음처럼 둔다.

- **Iris Description**: 태그 렌더러다. 태그 존재 시 블록을 출력하며, Evidence 재검사·문장 단위 승인제·조건부 의미 보정은 여기서 하지 않는다.
- **Iris Core / Rule / predicate**: 태그 생성의 책임층이다. Tool 1-A / 1-B 분기, `recipe_matches(role, category)`의 같은 relation tuple 검사, Evidence Table 요구조건 구현 정합성은 여기서 보장해야 한다.
- **Iris Browser**: 보여주는 방식만 다룬다. 오분류 자체를 브라우저 정렬이나 숨김으로 해결하지 않는다.

따라서 설명 왜곡 이슈의 1차 디버깅 초점은 `rule_executor / predicates / tool_rules` 같은 구현 계층이며, Description 쪽 문장 로직 추가는 기본 해법이 아니다.

### 문서와 구현의 책임 경계

Iris에서는 **Evidence Table / DSL / pipeline-spec이 기준 문서**이고, 구현은 이를 따라야 한다. 설명 왜곡이 발생했을 때 기준 문서가 이미 충분히 강하다면 먼저 문서를 늘리거나 바꾸지 않고, 구현이 문서와 어긋났는지부터 본다.

즉, `문서 수정으로 봉합`보다 `구현 정합성 복구`가 우선이다.

### Consumable 3-B 기준선

Consumable 3-B(음료)의 기준은 `체감상 마시는가`나 `갈증/배고픔 수치 비교`가 아니라, **Drink / Drainable 구조를 갖는가**로 고정한다. 스프/머그/알코올처럼 반복 논쟁이 예상되는 사례도 이 구조 기준으로만 다루며, 의미 해석으로 확장하지 않는다.


### 연관 레시피 표시 단위

Iris의 연관 레시피 계층은 **행동 문장을 세분화해 설명하는 층**이 아니라, 사용자가 관련 제작 경로를 탐색할 수 있게 하는 층이다.

- 기본 표시 단위는 `[레시피:n]` 같은 개수 압축보다 **레시피명 단위**에 둔다.
- UI는 필요하면 접기/펼치기를 사용할 수 있지만, 기본 단위를 `행동 문장`까지 잘게 쪼개지 않는다.
- Description이 레시피를 설명한다는 이유로 행동 의미를 과도하게 덧붙이지 않는다.

즉, 레시피 계층의 책임은 `행동 해설`보다 **탐색 가능한 관련 레시피 표면 제공**에 있다.

### Outcome source 검증과 개별 설명의 경계

개별 아이템 설명을 위한 검증은 Description 단계가 아니라, 설명 이전의 **source fact table 작성 단계**로 본다. 과거에 `우클릭 행동 검증`이라고 부르던 범주는 현재 문서에서는 **Right-click source 검증**으로 정리한다. 이 단계에서 중요한 점은, `Right-click source`의 Gate-0 단위가 **FullType 기반 직접 실행 도구**로 재고정되었다는 것이다. 남은 것은 coverage 철학 자체가 아니라, 어떤 필드가 이 Gate-0 단위에 적합한지의 감사다.

현재 확정된 구조는 다음이다.

- `아이템 자체 우클릭` 여부가 아니라, **그 아이템의 소지 여부가 어떤 컨텍스트 상호작용을 실제로 가능하게 하는가**를 본다.
- Right-click source의 Gate-0 단위는 **FullType 기반 직접 실행 도구 Evidence**다. 즉, 아이템 X를 보유했을 때에만 실행 가능하고, 그 아이템이 직접 실행 주체로서 외부 대상의 지속 상태 변화를 발생시켜야 한다.
- Strong 판정에서는 여기에 **비대체성**까지 요구한다. 따라서 조건 장비, 소모 재료, 제작 재료, 속성 기반 컨테이너는 기본적으로 Gate-0 핵심 후보가 아니다.
- 실제 실행 게이트가 `Tag / Property / Type / Drainable 상태`에 걸린 **property-based 필드**는 item-by-item Weak 적재 대상이 아니라, 먼저 `Gate-0 적합 필드인지`를 다시 감사해야 한다.
- 최종적으로 Rule이 소비하는 것은 언제나 **Outcome fact**다.
- 설명·추천·기능 해석은 여기서 하지 않는다.

이 정의는 과거의 `좁은 메뉴 생성 기준`을 대체한다.

- 메뉴 존재 여부, 메뉴명, UI 구조, 비활성 메뉴 표시는 canonical 기준이 아니다. B42와 모드 환경에서는 이것들이 구현 방식에 가까워 안정적 근거가 되지 못한다.
- `의료`, `수리`, `차량`, `요리` 같은 행동 의미 분류도 canonical 기준이 아니다. Right-click source는 **상태 변화 유형**으로만 정리한다.
- 상태 변화 유형의 예시는 `State Add / State Remove / State Modify / Content Change / Item Consume / World Change` 같은 수준에서 다룬다.

이 위에서 Right-click source는 Strong / Weak 이원 구조로 운용한다.

- **Strong Evidence**: 아이템 의존성, 외부 대상 존재, 지속 상태 변화가 분명할 뿐 아니라, **그 아이템이 직접 실행 주체**이고 **대체 경로가 없다**고 볼 수 있는 경우. Strong만 canonical dataset과 Capability 등록 후보가 된다.
- **Weak Evidence**: 위 조건 중 하나 이상이 불명확하거나, 컨테이너/조건 장비/소모재/대체 슬롯 파트처럼 실행 주체성과 비대체성이 흐린 경우. Weak는 검토 기록은 남기되 기본 출력·설명·Capability 등록에서는 제외한다.
- 따라서 `A OR B` 대체 구조, `A + B` 조합 구조, `Gasoline container` 같은 타입 기반 구조, `Attach/Upgrade` 같은 시스템 메뉴 기반 상호작용은 기본적으로 **Weak 또는 재검토 후보**로 본다.
- 이 구조에서 Strong이 극소수로 남는 것은 실패가 아니라 정상이다. Right-click Evidence는 `쓸만한 도구 모음`이 아니라 **전용 실행 도구만 남기는 구조 필터**이기 때문이다.
- 따라서 한 필드에서 Weak가 대량으로 쌓이면 `애매한 아이템이 많다`보다 **필드 게이트 단위가 FullType Gate-0와 어긋난다**고 먼저 의심한다. `can_add_generator_fuel`류는 이런 구조 감사 대상의 대표 예시다.

운영 순서도 함께 고정한다.

- 새 정의는 먼저 **기존 86개 candidate**에 우선 적용해 검증한다.
- 기존 등록 `can_*` 필드 검수는 이 단계에서 일단락된 것으로 보고, 다음 단계는 **남은 필드의 Gate-0 적합성 감사와 잔여 67개 사례 정리**로 넘어간다.
- 전 아이템 재적용은 Discovery 규칙과 Strong / Weak 필터가 문서 수준에서 안정화된 뒤에 수행한다.

변하지 않는 나머지 경계는 아래와 같다.

- Static capability source 검증 기준: ItemScript 정적 필드만으로도 결과 상태가 결정적으로 고정되는 경우 독립 source로 인정한다.
- Equip effect / Use only / Passive function 같은 항목은 기본 evidence 축이 아니라, 필요할 경우 **개별 설명층에서 후행적으로 풀어쓰는 정보**로 둔다.
- 이 검증 테이블은 `개별 설명이 필요한가`를 판정하는 입력이며, Iris 엔진의 의미 해석 계층을 뜻하지 않는다. 즉, 여기서 하는 일은 **설명을 쓰기 전에 source를 확인하고, 최종적으로는 결과 상태 fact를 잠그는 것**이다.

### Source와 Evidence의 분리

Iris는 `행동`을 Evidence로 쓰지 않는다. Canonical한 Evidence 형태는 **Outcome 중심의 결과 상태 fact**다. Recipe와 Right-click, Static capability는 모두 **Source**일 뿐이며, Rule에서 최종적으로 소비되는 것은 정규화된 Evidence다.

- Source는 `어떤 경로에서 사실을 관찰했는가`를 뜻한다.
- Evidence는 `그 아이템이 없으면 존재할 수 없는 결과 상태가 무엇인가`를 뜻한다.
- 따라서 `우클릭 행동 검증 테이블`은 source 검증 산출물이고, `Context Outcome 산출물`은 normalized evidence 산출물이다.
- `우클릭 행동`이라는 말은 walkthrough나 수동 검증 단계에서는 쓸 수 있지만, 설계 기준어로는 `Right-click source`와 `outcome fact`를 우선한다.

### Action vs Outcome 경계

Iris가 Recipe / Right-click / Static capability를 수용하더라도, 허용되는 것은 **행동(Action)** 이 아니라 **항상 성립하는 결과 상태(Outcome)** 다.

- `우클릭하면 ~할 수 있다`, 메뉴에 `Smoke`가 뜬다, 버튼이 있다 같은 **행동/입력/UI 정보**는 Iris의 canonical evidence가 아니다.
- `착용 변형 옵션 존재`, `사용 시 다른 아이템으로 교체`, `비소비 상태 전환 가능`, `월드 배치 가능`, `채우기/비우기 상태 전환`처럼 **아이템 단독 결과로 환원된 정적 사실**만 Context Outcome으로 승격할 수 있다.
- `open_canned_food`, `stitch_wound`, `disassemble_electronics` 같은 **행동 의미형 outcome**은 현재 모델의 기본형으로 채택하지 않는다.
- 따라서 `행동명 → 의미 → outcome` 식의 자동 해석기를 Description이나 Core 안에 넣지 않는다.

즉, Right-click은 Evidence 그 자체가 아니라 **Outcome source**일 수 있을 뿐이며, Iris가 최종적으로 받아들이는 형태는 언제나 **정적 결과 산출물**이어야 한다.

### Context Outcome 추출 파이프라인

Context Outcome 추출기는 Iris 엔진 내부의 의미 해석기가 아니라, **동결 문서를 1:1로 기계화해 outcome 사실 테이블을 만드는 외부 추출 파이프라인**으로 본다.

- **스캐너(scanner)**: Lua·script 같은 원천 데이터에서 **정적 구조 단서만** 수집한다. 현재 main path는 ItemScript 정적 필드 중심이고, Lua 스캐너는 diagnostics/reference 성격이 더 강하다.
- **IR(intermediate representation)**: 행동 의미를 적지 않고, 허용된 **signal만 저장**한다.
- **매퍼(mapper)**: `Signal → Outcome`의 **단방향 매핑**만 수행한다.
- **수동 주입기(manual injector)**: 자동 경로로 다루지 않는 민감 outcome을 별도 진입점으로 주입한다. 현재 대표 사례는 `smoke_item`이다.
- **검증기(validator)**: 문서가 허용한 Fail-loud 3종만 강제한다.
- **진단기(diagnostics)**: 즉사 대상이 아닌 위험 신호를 보고서로 남긴다.

핵심은 추출기가 **행동을 이해하지 못하게** 만드는 것이다. 스캐너는 수집만 하고, IR은 의미를 붙이지 않으며, 매퍼는 허용된 enum 수준의 signal만 outcome으로 바꾼다. 검증기와 진단기도 역할을 나눠서, 안전장치가 임의의 추가 헌법을 만들지 않게 한다.

### Context Outcome의 허용 입력과 비허용 입력

- 허용 입력: ItemScript 정적 필드, recipe 정의, 정적 capability 선언, 그리고 필요한 범위의 Lua/reference 스캔을 포함한 **원천 데이터의 오프라인 정적 분석 산출물**
- 비허용 입력: 런타임 컨텍스트 메뉴 상태, 클릭 경로, 행동 문자열, 메뉴 라벨을 읽고 그 자리에서 해석하는 방식

특히 `CustomContextMenu = "Smoke"` 같은 값은 정적 필드이더라도 **행동명**이므로, 필요하면 관측치·보조 표면으로는 남길 수 있어도 그것만으로 `smoke_item` 같은 outcome을 자동 생성하는 기본 경로로 쓰지 않는다. 구현 단계에서 편의상 쓰고 싶어져도 마지막 질문은 늘 같다. **"이건 행동을 읽는가, 결과를 읽는가?"**

또한 Fixing / Moveables 같은 관계형 정의는 이번 파이프라인에서 outcome 소스로 승격하지 않는다. 그것들은 기존 evidence / predicate 경로에 남기고, Context Outcome은 **아이템 단독 결과 상태**만 다루는 별도 계열로 유지한다. Source를 추가로 인정하더라도 canonical Evidence 모델은 outcome 중심으로 닫는다.

현재 미결 재검토 항목도 구분해서 본다. `can_scrap_moveables`는 `단일 결과 상태 단위로 다시 쪼갤 수 있는가`라는 **구조 이슈**에 가깝고, `can_extinguish_fire`는 `같은 capability 아래 어디까지를 Strong/Weak로 묶을 것인가`라는 **범위 이슈**에 가깝다. 둘 다 source coverage 재검토 대상이지만 같은 수정 루트로 취급하지 않는다.

또한 `can_scrap_moveables`는 현 상태 그대로 canonical capability로 유지하지 않는다. 이 필드에는 범용 도구(`Hammer`), 조합 도구(`BlowTorch` + `WeldingMask`), 재료/부산물(`UnusableMetal`, `UnusableWood`)이 섞여 있어 **단일 결과 상태**로 볼 수 없다. 따라서 이 필드는 해체/재정의가 필요하다. 다만 `Saw`, `Screwdriver` 같은 항목을 어떤 canonical outcome fact로 살릴지는 새 `item-dependence + state-change` 기준 아래에서 다시 판단한다.

같은 이유로 `can_remove_embedded_object`, `can_stitch_wound`, `can_add_generator_fuel`, `can_attach_weapon_mod`, `can_extinguish_fire`도 이제 `좁은 메뉴 모델 기준 잠정 제거/재검토`가 아니라, **새 정의로 86개 candidate 집합 안에서 Strong/Weak를 다시 가르는 대상**으로 본다. 특히 attach/fuel/medical 계열은 `메뉴 존재 여부`가 아니라 `아이템 의존성 + 실제 상태 변화`를 먼저 검증해야 한다.
현재까지의 검수 결과에서 드러난 대표 패턴도 기록한다. `can_attach_weapon_mod`는 대체 슬롯 파트가 대부분이라 전반 Weak 패턴으로 수렴하고, 현재 기준상 **Bayonet만 Strong 예외**로 남는다. 반대로 `can_extinguish_fire`는 불 끄기라는 World Change가 있어도 실행 주체가 용기 자체라기보다 내용물/소화 로직에 가깝고 대체 가능한 용기 구조가 너무 넓어, 샘플 검증 기준 **전반 Weak 패턴**으로 본다. 같은 이유로 `Needle` 같은 항목도 사용 구조에 따라 `Tailoring에서는 Strong / Stitch에서는 Weak`처럼 **아이템 단위가 아니라 사용 구조 단위**로 갈릴 수 있다.


### Context Outcome 추출기와 Iris 엔진의 경계

Iris는 Context Outcome을 스스로 해석해서 즉석에서 만들어내지 않는다. 추출기는 **외부 공급자**, Iris Core는 **소비자**다.

- 추출기는 오프라인 / 정적 분석 중심으로 outcome 산출물을 만든다.
- Iris Core는 그 산출물을 기존 입력 소스와 함께 소비한다.
- `has_outcome(...)` 같은 기존 DSL 소비 지점은 유지한다.
- Description 계층은 이 산출물의 존재를 렌더링할 뿐, outcome 근거를 재판정하지 않는다.

즉, 이번 확장은 `Iris 엔진을 더 똑똑하게 만들기`보다 **입력 공급 경로를 늘리고 검증을 공통화하는 쪽**으로 닫는다.

### Fail-loud와 diagnostics의 분리

Context Outcome 추출기에서 즉시 중단할 수 있는 사유는 세 가지뿐이다.

1. Allowlist 밖 Outcome
2. 비결정성
3. 출력 포맷 위반

금지 토큰 탐지, 문서 SHA 불일치, `smoke_item` 자동 경로 탐지 같은 신호는 중요하지만 **diagnostics**로만 남긴다. 이 구분의 목적은 안전장치를 약하게 만드는 것이 아니라, 구현자가 문서가 정하지 않은 처벌 체계를 임의로 추가하지 못하게 하는 데 있다.

### 민감 outcome의 별도 진입점

`smoke_item`은 자동 추출기 안에서 처리하지 않는다. 현재 구조에서 이 outcome은 **Option B 수동 주입 전용**으로 격리한다.

- 자동 경로에서 감지되면 진단만 남긴다.
- 실제 outcome 생성은 수동 주입기만 담당한다.
- 따라서 `smoke_item`은 자동 추출기의 완전성 문제가 아니라, **행동 의미 추론을 차단하기 위한 구조적 격리 사례**로 본다.

### Outcome 위계와 Evidence Table 우선

Outcome의 핵심/보조 위계는 일반 규칙으로 정하지 않는다. 문서가 적은 그대로만 반영한다.

- 예: `equip_back`는 Wearable.6-F에서 **핵심 증거**다.
- 하지만 이것을 근거로 다른 outcome까지 일괄 승격하는 일반론은 만들지 않는다.

즉, 위계 판정도 `더 안전해 보이는 해석`보다 **Evidence Table 1:1 기계화**가 우선이다.

### 현재 열어둔 비결정 영역

다만 이번 단계에서 아래 항목들은 아직 아키텍처 수준의 최종 판정으로 닫지 않는다.

- 어떤 signal / outcome을 어떤 순서로 먼저 구현할지
- Item Script 기반 신호를 어디까지 추가할지
- `smoke_items` 초기 수동 주입 목록을 어떻게 운영할지

이들은 설계 리스크라기보다 **구현 순서와 운영 선택**의 문제로 남긴다.

### 이번 확장에서 건드리지 않는 층

Context Outcome 도입은 **설명 엔진을 더 똑똑하게 만드는 작업**이 아니다. 따라서 다음 층은 이번 단계에서 갈아엎지 않는다.

- 입력 계약 전체
- 설명 파이프라인 철학
- 구현 체크리스트의 상위 방향

이번 확장의 직접 수정 범위는 **Allowlist / DSL / Evidence Table** 같은 분류 단계의 증거 규약과, 이를 실제 산출물로 만드는 오프라인 추출기다.

### 외부 모드 확장 원칙

Iris의 외부 모드 확장은 **표준 구조를 제공한 모드 데이터를 정규화해 렌더링하는 방식**으로만 연다. 목표는 `모든 모드를 추론하는 AI 위키`가 아니라, **구조를 제공한 모드의 위키 엔진**이다.

따라서 모드 시장 확장을 이유로 설명 계층에 텍스트 해석이나 추론을 넣지 않는다.

## 2-6. Frame

### 정체성

Project Zomboid 모드팩의 상태를 시간축 위에서 **기록·비교·되돌리는 버전 관리 레이어**. 개별 모드 관리자라기보다 **PZ판 git**에 가깝고, 관리 최소 단위는 모드 하나가 아니라 **팩 상태(pack state)** 다. 게임 실행 중 성능·안정성에 개입하는 런타임 레이어가 아니다.

### 하는 일

- 모드 목록/순서/출처/설정/지문을 포함한 **팩 상태 기록**
- baseline / overrides / manifest / fingerprint 기반 상태 비교
- **원본 설정 보존 + 사용자 오버라이드 레이어 관리**
- 수동 공식 스냅샷과 자동 안전망 스냅샷 운영
- 상태 A ↔ 상태 B diff, rollback, restore
- **ZIP + JSON 공개 공유 포맷**
- 필요 시 import 단계의 **내부 `.frame` 검증 캐시**
- 설치 전/운영 단계에서의 재현 가능한 팩 상태 관리

### 하지 않는 일

- 개별 모드 관리자처럼 ON/OFF와 정렬을 중심 UX로 삼는 것
- 문제 모드 지목
- 추천 / 정답 제시 / 자동 해결
- devkit / 로그 분석기 중심 제품화
- 월드(세이브) 관리
- 모드 원본 파일 저장·배포형 완전 복원
- Frame 내부 설정 에디터
- `변화 없으면 저장 생략` 같은 해석적 자동 저장 정책
- 성능 개입 / 안정화 / Lua 실행 제어
- Fuse / Nerve와의 기능 결합
- 외부 런처/관리자 툴을 메인라인으로 삼는 것
- `.frame`을 외부 공유 표준으로 강제하는 것

### 설계 의도

Frame은 `문제를 해결하는 도구`보다 `되돌릴 수 있게 만드는 기록 도구`에 가깝다. 핵심 가치는 더 똑똑한 분석이 아니라 **실패를 리셋이 아니라 롤백으로 바꾸는 것**이며, 그 때문에 사실만 기록하고 판단은 하지 않는다. git과의 관계도 `기능 복붙`이 아니라 **의미 있는 상태는 사람이 선언하고(commit), 시스템은 자동 흔적(reflog)로 보조한다**는 철학을 가져오는 데 있다.

따라서 공식 스냅샷은 **수동**으로 만들고, 자동 스냅샷은 세션 내부 복구와 회귀 추적을 위한 **보조 안전망**으로만 둔다. 다만 자동 스냅샷을 품질 낮은 기록으로 보지 않고, **5/10/30/60분 고정 주기 + 최근 10개 롤링 보관** 같은 예측 가능한 시간축 기억 장치로 유지한다. Frame은 저장 생략 여부를 해석해서 결정하지 않고, 정해진 시간과 명시적 사용자 기준점을 우선한다.

또한 Frame은 `완전 복원 장치`보다 **재구성 + 동일성 확인 장치**에 가깝다. Workshop 옛 버전, 내려간 모드, 권리/약관 문제 때문에 원본 파일 저장·배포형 복원은 채택하지 않고, 목록/순서/설정 재구성과 fingerprint 검증을 통해 `그때와 지금이 같은가`를 다루는 쪽을 기본 모델로 둔다.

용어도 판단 대신 사실+행동 언어를 쓴다. 따라서 `정상/비정상`, `원인/범인`, `권장/최적`, `해결/진단`보다는 `기준점`, `자동 저장`, `달라짐`, `비교`, `되돌리기`, `계속` 같은 표현을 우선한다. 이는 제품이 devkit나 정책 도구처럼 보이는 것을 막기 위한 설계 장치다.

Frame이 Echo/Fuse/Nerve와 함께 언급될 수 있는 이유는 좋은 팩 상태가 런타임 모듈의 효과를 더 잘 드러나게 하기 때문이지, 기능적으로 결합되어 있기 때문이 아니다. Frame은 환경 계약, 로드 순서, 재현 가능한 팩 상태를 제공함으로써 운영의 관리 가능성을 높이지만, 어디까지나 **환경 통제 레이어**로 남는다.

또한 Frame은 CurseForge류 관리자처럼 모드를 직접 다루는 제품이 아니라, **팩 상태를 1급 객체로 다루는 제품**이어야 한다. 따라서 비교 단위도 `모드 A가 문제인가?`보다 `정상 상태 A와 문제 상태 B의 차이는 무엇인가?`에 둔다. 다만 이것이 Frame을 다른 하위 모듈보다 우선하는 특권 축으로 만든다는 뜻은 아니며, 생태계 전체는 각 모듈이 자기 문제를 풀면서 Pulse의 가능성을 증명하는 구조로 본다.

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

외부 툴이 만든 리소스팩 산출물을 읽어 **최종 적용 상태를 계산·검증·비교·설명**하는 독립 모듈. 단순 로더가 아니라 **리소스 적용 상태 관리 플랫폼**으로 본다. 시작한다면 처음부터 Canvas로 시작하고, 그럴 가치가 없으면 리소스팩 제품 축 자체를 열지 않는다.

### 하는 일

- 리소스 인덱싱
- 최종 적용 상태 계산
- 충돌 분석
- 경로 / 구조 / ID / 패킹 검증
- 프리플라이트 검증
- 로컬↔산출물 / 서버↔클라 상태 비교
- 적용 결과 가시화와 설명형 리포트
- 외부 입력(ZIP / JSON / `.pack`)을 읽고 내부 정규화 캐시로 재구성

### 하지 않는 일

- 리소스 제작 툴
- 자동 병합 / 정답 추천 / 정책 심판
- Frame 대체
- Cortex 대체
- `.canvas`를 외부 공유 표준으로 강제하는 것
- 외부 사례 구조를 그대로 복제하는 것

### 설계 의도

Canvas의 본업은 `무엇을 만들까`보다 **왜 안 먹는지 / 무엇이 최종 적용됐는지 / 지금 상태로 배포 가능한지**를 설명하는 데 있다. 따라서 Photoshop, GIMP, Blender, TileZed 같은 외부 툴과 경쟁하는 대신, 그 산출물을 읽어 관리·검증·비교·설명하는 플랫폼으로 좁힌다.

v1 pain point는 세 가지로 고정한다.

- **최종 적용 결과 / 충돌 / 로드 순서 가시성 부족**
- **패킹 / 경로 / 구조 / ID 민감성으로 제작 과정이 쉽게 깨지는 문제**
- **버전 / 서버 / 배포 불일치**

이 세 축을 모두 덮되, 중심 가치는 `최종 적용 상태와 충돌의 가시화`에 둔다. 게임 리소스를 1차 대상으로 삼고, 모드 리소스 확장은 후행 축으로 둔다.

### 포맷 / 공유 원칙

Canvas는 외부 파일과 `.pack`을 입력으로 읽고, 내부적으로 필요하면 `.canvas` 같은 **정규화 캐시 / 분석 번들**을 가질 수 있다. 그러나 외부 공유 기본값은 **ZIP + JSON(+ .pack)** 으로 두고, `.canvas`를 공개 표준으로 강제하지 않는다. 이는 `공유 표준은 열린 포맷, 내부 처리는 안전 캐시`라는 절충으로 본다.

### Core와의 경계

- **Pulse Core**: 활성 팩/순서/출처 조회, 식별자 정규화, 해시/fingerprint, 리소스 변경 이벤트, Networking 기반 상태 교환, SPI, 진단 레코드 구조 같은 기반 capability만 제공
- **Canvas**: 인덱싱, 최종 상태 계산, 충돌 분석, 구조/경로/ID/패킹 검증, 상태 비교, 설명형 리포트와 UX 담당

즉 Pulse는 읽고·식별하고·연결하는 기반만 맡고, Canvas가 해석·검증·비교·설명을 맡는다.

### Frame / Cortex / 외부 툴과의 경계

- **Frame**: 모드팩 환경 상태를 시간축 위에서 기록·비교·되돌리는 관리자 레이어
- **Canvas**: 리소스 적용 상태를 검증·비교·설명하는 레이어
- **Cortex**: 편의 / 가이드 / 제작 보조의 격리 구역
- **외부 툴**: 실제 리소스를 만드는 도구

Canvas와 Frame은 함께 쓸 수 있어도 통합 제품처럼 설계하지 않고, Frame은 시간축·스냅샷을, Canvas는 적용 결과·충돌·배포 검증을 담당한다. Cortex는 Canvas를 임시 수용하지 않으며, 제작 편의가 필요할 때만 보조 축으로 개입한다. 외부 사례(Vortex, packwiz, mrpack, Minecraft 리소스팩 stack)는 문제 해결 방식의 참고 대상일 뿐, 구조를 그대로 복제하지 않는다.

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


# 9. Iris Taxonomy addendum

## 9-1. Iris는 전체 아이템 위키 위에 Evidence를 얹는다

Iris는 `Evidence가 있는 아이템만 다루는 시스템`이 아니다. 기본 표면은 **전체 아이템 위키**이고, Recipe / Right-click / Static capability Evidence는 그 위에 얹히는 **1차 기능 레이어**다.

즉 다음이 고정된다.

- Evidence 없음 ≠ 기능 없음
- Evidence는 포함/제외의 최종 게이트가 아님
- 전체 아이템 수용 문제는 Evidence보다 **Taxonomy와 phase2_rules**에서 해결한다

## 9-2. 계층 역할 재고정

Iris 내부 계층은 아래처럼 다시 고정한다.

1. **Evidence layer**
   - Recipe / Right-click / Static capability 같은 기능 단서 수집
   - 무엇을 자동으로 말할 수 있는지 닫는 계층
2. **Taxonomy layer**
   - 대분류/소분류/경계 규칙/phase2_rules로 전체 아이템을 수용하는 계층
   - 미분류 해소의 1차 책임 위치
3. **Rule / residual layer**
   - positive match와 대분류 가드가 있는 residual만 처리하는 계층
   - `매칭 없음` 자체를 규칙으로 승격하지 않음
4. **Output layer**
   - blocklist 반영, Misc 폴백, 최종 출력 조립
   - 매칭 실패 기반 처리의 최종 위치
5. **Description layer**
   - 위 계층의 결과를 유저 언어로 노출하는 계층
   - `실질적 도움`, 비해석, 비권장 규칙이 여기서 작동

즉, Evidence(1단계)로 Taxonomy(2단계)와 Description(5단계)를 대신하지 않으며, `매칭 실패 기반 폴백`은 Rule이 아니라 Output 계층에 둔다.

## 9-3. 9개 대분류 기준선

현재 Iris의 대분류 기준선은 다음 9개 축으로 둔다.

- Tool
- Combat
- Consumable
- Resource
- Literature
- Wearable
- Furniture
- Vehicle
- Misc

이 단계에서의 핵심은 `더 예쁜 구조를 더 찾기`가 아니라, **Evidence 있는 분할만 남기고 없는 분할을 제거해 잔여군을 어디 축과 경계 규칙으로 받을지 닫는 것**이다.

## 9-4. 최소 구조 원칙

- **Furniture**: 현재 안정적인 자동 Evidence 축이 사실상 `Type = Moveable`뿐이므로, **Furniture.7-A 단일 소분류**로 둔다.
- **Vehicle**: 전용 필드 축이 남는 구동계 / 차체 정도만 분리하고, **Vehicle.8-A(Drivetrain) / Vehicle.8-B(Body)** 최소 2분할로 닫는다.
- **Misc**: 의미 분류가 아니라 **최종 폴백 단일 구조(Misc.9-A)** 로 둔다.
- 이 세 축은 `탐색성이 좋아 보이니까 더 쪼갠다`가 아니라, **전용 Evidence 축이 없으면 쪼개지 않는다**를 기준으로 한다.

## 9-5. 경계 규칙

- **Furniture**: 범위 밖이 아니라 별도 대분류. 실제 인벤토리 아이템이며 배치로 월드 상태를 바꾼다.
- **Vehicle**: 차량 부품/차량 시스템 귀속 구조를 가진 아이템군. `ConditionAffectsCapacity` 같은 공유 필드는 전용 증거로 쓰지 않고, 가스탱크/엔진 파츠는 manual override로 봉인한다.
- **Wearable**: 신체 슬롯 착용 구조만 다룬다. `장착·휴대`로 넓히지 않는다.
- **Tool**: 작업 도구 + 하위 `Security`, `Storage`를 수용할 수 있으나, `행동 인터페이스 허브`로 무제한 팽창하면 안 된다.
- **Tool.Storage**: **비착용 휴대 컨테이너**만 받는다.
- **Wearable.6-F**: `equip_back` outcome / BodyLocation으로 식별되는 **착용 가능한 배낭**을 받는다.
- **Resource**: 재료 축이며, 애매한 잔여군을 몰아넣는 기타통으로 쓰지 않는다.
- **Misc**: 기능 없음 + 상태 영향 없음 + Storage 없음 + Access 없음 + 배치 없음에 가까운 잔여군만 받는다.

## 9-6. blocklist와 Misc 폴백의 위치

blocklist는 `설명이 단조롭다`, `유저가 안 찾을 것 같다`를 이유로 범위를 자르는 장치가 아니다. blocklist는 **코드 내부 표현용 / 시스템용 / 실제 플레이 관찰 범위 밖**인 항목만 봉인하는 장치다.

예시:
- `ZedDmg`, `Wound`, `Bandage`, `Appearance`, `MaleBody`, `Corpse`, `Hidden` 등

또한 Misc.9-A는 `rule_executor` 안의 규칙이 아니다.

- **rule_executor**: 일반 규칙 + 대분류 가드가 있는 residual만 처리
- **output_generator**: blocklist 제외 후 태그 0개 아이템에만 Misc.9-A를 부여

즉, Misc는 `Evidence 매칭`이 아니라 `매칭 실패 기반 폴백`이므로 출력 계층에서만 닫는다.

## 9-7. Phase 2 구조 설계의 현재 상태

Phase 2는 다음이 동시에 확인된 시점에서 **동결 가능한 구조**로 본다.

- Furniture 단일 소분류
- Vehicle 최소 2분할
- Misc output-stage fallback 단일 구조
- Tool.Security / Tool.Storage 편입
- Allowlist / Template / Implementation Plan / Walkthrough 정합
- Tool.Storage vs Wearable.6-F 중복 0건

따라서 이 단계 이후 남은 일은 Architecture 대논쟁이 아니라 **회귀 감시 / manual override 운영 / 설명 품질 보강**이다.


# 10. Iris Description writing addendum

## 10-1. 소분류 설명의 역할

Iris의 소분류 설명은 `분류 체계 안내문`이 아니다. 역할은 **각 소분류가 담고 있는 실제 용도, 시스템적 의미, 적용 범위를 유저가 바로 이해할 수 있는 위키형 정적 문장으로 풀어쓰는 것**이다.

따라서 소분류 설명은 다음을 피한다.

- 분류명 재진술
- 추상적 정의문 반복
- 번역체 시스템 문장
- 추천/효율/전술 평가

## 10-2. 설명 계층의 문체 규약

소분류 설명의 기본 문체는 **짧고 단정한 한국어 위키 문체**다.

- `관여한다`, `관련된다`, `다루며`, `특성` 같은 추상어를 기본값으로 삼지 않는다.
- 가능하면 `~에 사용된다`, `~을 위한 도구다`, `~의 영향을 받는다`처럼 직접적 구조를 사용한다.
- 뒤에 군더더기 안내문을 덧붙이지 않는다.

즉, 설명의 자연스러움은 장식이 아니라 Iris 품질 계약의 일부다.

## 10-3. 시스템 정보 포함 기준

소분류 설명은 원칙적으로 위키형 정적 설명이지만, 사용자가 형태만 보고 오해하기 쉬운 그룹에서는 **시스템 정보를 필요한 만큼 포함할 수 있다**.

예를 들어:

- 전투 소분류: 해당 전투 스킬과의 연동
- 총기 소분류: 탄약 소모, 조준/재장전 레벨 영향
- 통신/미디어: 정보 송수신뿐 아니라 기록된 음성/음악 재생 같은 실제 기능
- 광원/점화: 시야 확보, 점화, 불 확산과의 관계
- 배낭/수납: 운반 부담 감소 같은 실제 효과

다만 이 정보도 어디까지나 **시스템 사실**이어야 하며, 추천/효율/공략 문장으로 넘어가면 안 된다.

## 10-4. 바닐라 기준과 모드 확장성

설명은 바닐라를 기준으로 사실을 쓰되, 장기적으로 불특정 모드에도 적용될 수 있도록 **행위·기능 중심 일반화**를 우선한다.

- 특정 바닐라 대상명에 과도하게 묶인 문장을 피한다.
- 특정 장착 위치나 구현 세부에 지나치게 고정된 표현을 피한다.
- 지금 바닐라에는 맞지만 모드에서 쉽게 깨질 표현은 가능한 한 상위 개념으로 정리한다.

## 10-5. 소분류 설명과 개별 아이템 설명의 경계

- **소분류 설명**: 그룹 수준의 공통 용도·시스템 의미·적용 범위
- **개별 아이템 설명**: 해당 아이템만의 고유 사실, 예외, 세부 기능

따라서 소분류 설명 동결과 개별 아이템 설명 작업은 같은 층위의 일이 아니다. 소분류 설명이 먼저 기준선을 만들고, 개별 아이템 설명은 그 다음 별도 단계에서 진행한다.

## 10-6. 구조보다 설명으로 해결하는 기본값

Furniture나 Misc처럼 내용이 넓거나 설명이 단조로운 그룹에서, 기본 대응은 소분류를 계속 쪼개는 것이 아니라 **설명 표현을 고치는 것**이다.

`쓸모없다`, `잡동사니다`, `장식용이다` 같은 의미 분류로 구조를 더 늘리면 Iris가 추천/해석 시스템처럼 보일 위험이 있다. 따라서 실제 기능 경계가 분명하지 않다면, 구조 확장보다 설명 개선을 우선한다.

---

# 11. Iris Right-click Gate-0 v2 evidence-first addendum

## 11-1. 목적

이번 단계의 핵심은 `Right-click capability 이름을 더 잘 짓는 것`이 아니라, **Gate-0가 어떤 증거 단위를 받아야 하는지 닫는 것**이다. 따라서 Right-click Gate-0는 `can_*`를 먼저 고정하는 capability-first가 아니라, **source에서 candidate를 모으고 → decision으로 판정하고 → 그 결과로 field를 생성하는 evidence-first** 구조로 운용한다.

## 11-2. Gate-0 판정 순서

Right-click Gate-0는 다음 순서로만 판정한다.

1. **직접 실행 주체인가**
   - 그 아이템이 실제 상태 변화를 일으키는 실행 도구인가
   - 입력 재료 / 조건 장비 / 속성 전달자 / 제작 재료면 여기서 탈락
2. **외부 대상이 존재하는가**
   - 다른 아이템, 월드 객체, 플레이어 상태, 환경 상태 등
3. **지속 상태 변화가 있는가**
   - State Add / Remove / Modify / Content Change / Item Consume / World Change
4. **그 다음 Strong / Weak**
   - Gate-0 통과 이후에만 유일성 / 대체성 여부를 본다

즉, Strong / Weak는 Gate-0 본판정이 아니라 **Gate-0 통과 후의 2차 등급**이다.

## 11-3. v2 파이프라인 책임 분리

- **source_index_v2**
  - `can_*` 목록을 고정하는 문서가 아니라 `source → candidate` 추출 규칙을 정의한다.
- **evidence_candidates**
  - source에서 수집된 후보 사실을 모은다.
- **evidence_decisions**
  - PASS / REVIEW / Excluded / scope 밖 등의 판정을 기록한다.
- **field_registry_v2**
  - field는 미리 존재하는 capability 이름이 아니라, decision 결과를 반영해 생성·갱신된다.
- **resolution_rules_v2**
  - candidate 병합 → decision → field update 흐름만 담당한다.
- **fail_conditions_v2**
  - 금지 근거 / 비결정성 / 출력 계약 위반만 Fail로 본다.
- **track_boundaries_v2**
  - Gate-0 / Recipe / Excluded / REVIEW 라우팅 계약을 담당한다.

핵심은 각 문서가 `추출`, `판정`, `필드 생성`, `라우팅`, `실패 조건`을 섞지 않는 것이다.

## 11-4. scope 밖 / REVIEW / NO의 의미

- **scope 밖**
  - 현재 rule로는 candidate 추출이 불가능한 상태
  - `Evidence 없음`이나 `NO`의 동의어가 아니다
- **REVIEW**
  - automatic-only 체계 안에서 허용된 정적 근거만으로는 아직 닫히지 않은 미확정 상태
  - 웹/위키 기반 수동 승격 통로가 아니며, 추가 rule 발굴 / 분포 분석 / 다른 증거 축과의 관계 검토 대상으로만 남긴다
  - `property_based`는 이 단계에서 즉시 NO로 고정하지 않고 REVIEW에 유지한다
- **NO / Excluded**
  - Gate-0 정의와 명시적으로 충돌하거나 다른 트랙으로 보내야 하는 경우

즉, `미매칭 = NO`도 틀리고, `property_based = 즉시 NO`도 틀리다.

## 11-5. property-based 필드의 취급

`Tag / Property / Type / State`에 실제 게이트가 걸린 필드는 item-by-item으로 Strong / Weak를 끝없이 쌓는 방식보다, 먼저 **이 필드가 Gate-0 FullType Evidence 단위에 맞는가**를 본다.

- 맞지 않으면 Gate-0 canonical PASS/NO가 아니라 REVIEW 또는 scope 밖으로 남긴다.
- 따라서 property-based는 generic 불확실성 쓰레기통이 아니라, **자동화가 과하게 결론 내리지 않기 위한 검토 격리대**다.
- `Food / Drainable`처럼 근거가 충분하면 exclusion으로 확정할 수 있지만, 근거가 부족하면 억지로 property_based 축에 몰아넣지 않는다.

## 11-6. Gate-0의 역할 제한

Gate-0 자동 분류는 `모든 용도 파악`을 대신하지 않는다. 역할은 어디까지나:

1. 정적 근거로 candidate를 추출하고
2. 그 candidate를 PASS / REVIEW / Excluded / scope 밖으로 라우팅하고
3. field_registry를 결과 기반으로 갱신하는 것

이다. 따라서 Gate-0는 설명 계층이나 의미 해석 계층을 먹지 않고, Evidence 1차 레이어로만 남는다.

## 11-7. 운영 단계 전환

문서 A~F(v2), implementation plan rev.3, walkthrough 1차 검증이 통과한 뒤에는 핵심 쟁점이 `문서를 더 어떻게 고칠까`가 아니다. 이후 단계는 실행 결과의 `scope 밖 / REVIEW / PASS` 분포를 기준으로 운영한다. 다만 이번 세션에서 한계선이 명확해졌다.

- candidate-only 규칙은 coverage 실험용 artefact이며 baseline 운영 규칙이 아니다.
- Moveable prove rule은 B/C 앵커를 올려도 A unknown이면 운영 승격 근거가 되지 않는다.
- REVIEW는 Right-click 내부의 automatic-only 미확정 상태로 유지하고, scope 밖은 먼저 Recipe / 다른 자동 증거 축과 교차한다.
- `우클릭 기능이 없다`는 부재 결론은 정적 앵커가 없는 한 자동 NO로 확정하지 않는다.

즉 이후 운영 단계는 `더 많은 후보를 끌어오자`가 아니라, **허용된 정적 근거 안에서 자동 분류 상한이 어디인지 인정한 상태에서 REVIEW와 scope 밖을 올바른 후속 경로로 보내는 단계**다.



## 11-8. candidate-only와 prove anchor의 지위

- **candidate-only 규칙**
  - coverage 상한선을 측정하는 실험 장치다.
  - baseline 기본값으로 켜두지 않는다.
  - REVIEW만 늘리고 결정력을 늘리지 못하면 운영 규칙으로 채택하지 않는다.
- **prove anchor 규칙**
  - A/B/C 중 일부 앵커를 올리는 실험 장치다.
  - 특히 B/C만 올리고 A를 올리지 못하는 경우, Phase D 정책상 결과는 여전히 REVIEW다.
  - 따라서 `앵커를 찾았다`와 `운영 승격 가치가 있다`를 동일시하지 않는다.

## 11-9. REVIEW와 scope 밖의 후속 경로

- **REVIEW**
  - Right-click 트랙 내부의 automatic-only 미확정 상태다.
  - 추가 정적 근거 발굴, 분포 분석, 다른 Evidence 축과의 관계 재평가 대상으로만 남기며 웹/위키 수동 승격 경로는 두지 않는다.
- **scope 밖**
  - Right-click 수동 검증 대상이 아니다.
  - 먼저 Recipe 및 다른 자동 증거 축과 교차한 뒤, 그 후에도 남는 잔여만 별도 문제로 본다.

이 구분은 Right-click 파이프라인이 `자기 트랙 밖의 일`까지 떠안지 않게 하기 위한 운영 경계다.


## 11-10. Recipe / Right-click 동급 2트랙과 automatic-only 운영

Iris 1단계 증거 시스템은 Recipe와 Right-click의 **동급 2트랙**으로 유지한다.

- Right-click은 `Recipe로 못 잡는 잔여물 필터`가 아니다.
- 같은 아이템이 두 트랙에 동시에 걸릴 수 있다.
- `Recipe UI only 제외 / context-menu surfaced recipe 허용` 같은 조정은 이 동급·겹침 구조를 보존하는 방향에서만 허용한다.

또한 이 트랙들은 `웹/위키 수동 검증으로 나중에 닫는 반자동 체계`가 아니라, **automatic-only Evidence pipeline** 위에서 운영한다.

- PASS / NO / REVIEW는 automatic-only 결과 상태다.
- Strong / Weak도 자동 유일성 결과 상태다.
- 웹/위키 기반 수동 승격은 두지 않는다.
- 공신력은 Q1~Q5, expected_diff / allowed_changes, role_profile_by_rule_id, build_report 같은 품질 게이트로 보장한다.

## 11-11. 컴파일러 -> 뷰어형 Iris

Iris는 장기적으로 `오프라인 컴파일러 -> 런타임 뷰어` 구조를 지향한다.

- **오프라인 Python build**
  - Evidence 수집
  - Right-click / Recipe 동급 2트랙 판정
  - use_case / outcome / 분류 / 설명 메타 산출물 생성
- **런타임 Lua**
  - 산출물 로드
  - 위키 / 툴팁 / 설명 / 브라우저 UI 재구성

현재는 Recipe / Moveables / Fixing 일부 인덱스를 런타임에서 직접 build하는 하이브리드가 남아 있지만, 이 구조는 과도기적이다. 해자 강화 방향은 런타임 Lua를 분석기로 만들기보다 **뷰어**에 더 가깝게 유지하는 것이다.

## 11-12. Gate-0 Right-click 자동 확장의 종료 조건

v2.1 이후 candidate-only와 prove-anchor 실험은 `더 많은 규칙 후보`를 찾는 시도가 아니라 **허용된 근거 타입 안에서 자동 분류의 상한선이 어디인지 확인하는 실험**으로 해석한다.

- candidate-only는 coverage 실험용 artefact이며 운영 baseline이 아니다.
- prove anchor는 A까지 올리지 못하면 운영 승격 근거가 아니다.
- 이 실험들로 남은 병목이 `규칙 설계 부족`이 아니라 `증명 가능한 정적 근거의 한계`라는 점이 확인되면, baseline은 v2.1 Run D에 봉인한다.

따라서 이후 단계는 `규칙을 더 넣자`보다,

1. REVIEW / scope 밖 / PASS 분포를 자동-only 운영 지표로 관찰하고
2. scope 밖을 다른 증거 축과 교차시키며
3. compile-viewer 순도를 높이는 방향으로 구조를 정리하는 것

에 둔다.


## 11-13. Recipe requirements display pipeline

레시피 라인에 요구사항을 붙이는 경로는 `recipe_nav_ref`의 부속 기능이 아니라 **별도 오프라인 산출물 파이프라인**으로 다룬다.

### 목표

- `uc.recipe.*` 라인(소비 방향)에 해당 recipe의 요구사항(`rp.recipe.*`, 생산 방향)을 연결한다.
- 런타임 gsub 매칭 없이, **오프라인 피벗 인덱스 + 런타임 렌더 전용** 구조로 닫는다. 단, requirement atom의 제한적 상태표시는 오프라인 `check` 계약을 읽는 범위 안에서만 허용한다.

### 오프라인 흐름

1. `requirements_by_fulltype`를 전체 fulltype 기준으로 수집한다.
2. 이를 `recipe_id` 기준으로 피벗하여 `recipe_requirements_index.<BUILD>.json`을 만든다.
3. 필요 시 Lua table 산출물로 추가 변환해 런타임 로드를 단순화한다.

핵심은 `recipe_nav_ref`와 `recipe_requirements`가 **독립 생명주기**를 가진다는 점이다.

- nav_ref가 null이어도 requirements 표시는 가능하다.
- requirements가 없어도 nav 동작은 가능하다.
- 따라서 두 필드는 같은 recipe line 근처에 표시될 수 있어도, 내부 모델에서는 별도 산출물로 유지한다.

### 런타임 역할

런타임 Lua는 requirements를 **구조화된 위키 레이어로 렌더**한다.

- `display` 텍스트 렌더
- atom 단위 `check`를 읽어 제한적 상태색 적용
- 레시피 전체 SAT/UNSAT 판정 없음
- 숨김/정렬/추천 없음
- 실패/예외/호환성 이슈는 회색 또는 조용한 실패

이 경로는 `런타임 Lua = 렌더 전용` 원칙의 직접 적용 사례다. Lua는 check를 새로 만들지 않고, 오프라인이 확정한 정보의 상태표시만 수행한다.

### 계약과 실패 처리

- 허용 kind는 allowlist로 명시한다. 예: `perk`, `near_item`
- kind 위반, 출력 계약 위반은 FAIL-LOUD로 처리한다.
- 빈 배열은 산출물에서 생략해 출력 비대와 패턴 불일치를 피한다.

### 매핑 실패 분류

매핑 실패는 한 덩어리 상한으로 봉인하지 않고 분리해 추적한다.

- **dangling**: 실제 대응 recipe를 찾지 못한 경우
- **suffix-drift**: base slug 매치는 가능하지만 SHA suffix가 어긋난 경우

필요 시 base-slug fallback 2단계 검증을 두되, 이는 실패를 숨기기 위한 우회가 아니라 실패 원인 분해를 위한 계측으로 본다.


## 11-14. Automatic-only use_case pipeline

Iris의 행동 계층은 `증거 -> 행동(use_case) -> 설명 -> 런타임 표시` 순서의 **automatic-only 정적 계약**으로 닫는다.

### 기본 원칙

- Recipe와 Right-click은 **동급 2트랙**이며, 어느 한쪽도 잔여 필터가 아니다.
- `use_case`는 분류 흉내가 아니라 실제 행동 근거를 묶는 표면이다.
- DescriptionGenerator는 판정기가 아니라 **정적 use_case 렌더러**다.
- Lua 런타임은 build 산출물을 읽고 표시만 하며, role / keep / recipe type을 다시 해석하지 않는다.

### 오프라인 흐름

1. Right-click evidence와 recipe evidence를 별도 source에서 수집한다.
2. Recipe 쪽은 `classification_recipe`가 아니라 `rule_id` 중심 `recipe_evidence`로 정규화한다.
3. keep 재료는 consumed와 함께 `uc.recipe.*`에 연결하되, `role` 필드로 분리한다.
4. `use_case` 블록, label map, requirements block용 산출물을 생성한다.
5. Lua는 JSON/Lua table 산출물을 읽어 렌더만 수행한다.

### 스키마와 경계

- `by_fulltype` 스키마는 `{ "rule_ids": [{rule_id, role}, ...] }`로 고정한다.
- `role`은 `recipe_evidence` source에서만 필수 허용 필드다.
- keep / require는 PASS evidence가 아니라 **Requirements 층** 정보다.
- Actions 블록과 Requirements 블록은 서로 다른 정보층이며, 런타임에서 합치지 않는다.

### 라벨/계약

- `use_case_label_map` 누락은 FAIL-LOUD다.
- 새 use_case는 라벨 없이 통과하지 못한다.
- 라벨맵은 UI 자원이라기보다 build contract에 가깝다.

## 11-15. dynamic recipe review / legacy closure

### dynamic_recipe_expr

`dynamic_recipe_expr`는 automatic-only 조건 아래 정적화 가능한 만큼만 줄이고, 남은 `group_def_dynamic` 잔여는 **PERMANENT_REVIEW**로 남긴다.

- 정적 alias, static filter, resolved catalog로 줄일 수 있는 것만 줄인다.
- 런타임 테이블 의존 케이스를 억지 정적화하지 않는다.
- REVIEW는 미봉책이 아니라 정책+산출물+테스트로 봉인된 상태다.

### legacy

legacy 승격 경로는 `legacy_count 0 / Q3 exempt 0`을 목표 상태로 둔다.

- legacy는 영구 면제가 아니라 제거 대상 기술부채다.
- anchor completeness, role profile, expected diff는 예외 연명 수단이 아니라 제거를 증명하는 장치다.
- 래칫 방향은 기존 패턴과 동일하게 `decrease_only`를 사용한다.


## 11-16. Recipe requirements color layer

Recipe requirements 색상 레이어는 `레시피 전체 제작 가능 여부`를 평가하는 기능이 아니라, **상호작용 탭에 이미 렌더되는 requirement atom 각각을 kind별 check 계약으로 색상 보조하는 레이어**다.

### 기본 원칙

- 판정 단위는 recipe 전체가 아니라 `perk / near_item / flag` 같은 **atom 개별 단위**다.
- check 구조는 **Python 오프라인 파이프라인이 생성**하고, Lua는 읽기만 한다.
- 지원 kind인데 check가 비어 있으면 회색 fallback으로 넘기지 않고 **FAIL-LOUD**다.
- 이 레이어는 **상호작용 탭 안에서만** 동작하며, 다른 탭/모듈/정렬 정책으로 전파하지 않는다.

### 오프라인 책임

Python은 requirement atom별로 kind 스키마에 맞는 `check` 필드를 산출한다.

예시 방향:
- `perk` -> `{type: "perk", perk_name: ..., required_level: ...}`
- `flag` -> `{type: "flag", flag_name: ...}`
- `near_item` -> 1단계에서는 `{type: "near_item", near_token: ...}`만 허용

핵심은 **Lua가 check를 만들지 않는다**는 점이다. `atoms_without_check = 0`은 품질 목표가 아니라 빌드 계약이다.

### near_item 2단계 활성화

`near_item`은 short name/fulltype/엔진 API 시그니처가 확정되지 않은 상태에서 억지로 닫지 않는다.

1. 1단계: token-only 산출 (`near_token`) + Lua handler 비활성(none/unknown)
2. 2단계: 엔진 API 확인 후 fulltype 해소와 handler 활성화를 동시에 커밋

이렇게 해야 SHA를 한 번 더 흔들지 않고, 직접 타일 순회 같은 범위 외 구현을 피할 수 있다.

### 런타임 책임

Lua는 `evalRequirementColor(check, player)` 형태로만 동작한다.

- handler는 plain function
- `evalRequirementColor` 바깥에서 pcall 1회
- player는 호출부에서 `getSpecificPlayer(self.playerNum or 0)`로 주입
- recipe 통합 SAT/UNSAT 판정 없음
- check 생성/수정/override 없음

즉 Lua는 **색상 렌더러**이지, requirements 판정 구조를 재구성하는 계층이 아니다.

### 스코프 밖

- 레시피 이름 라인 자체의 SAT/UNSAT 색상
- 웹/위키/사람 판정으로 check 보정
- near_item 엔진 미확인 상태에서 fulltype 강제 확정
- Lua가 role/kind를 해석해 display 텍스트를 변경하는 경로


## 11-17. Right-click capability UI integration

Right-click 행동 표면은 `문자열을 끼워 넣는 레이어`가 아니라, **정제된 능력 기반 구조 데이터**를 UI 블록으로 렌더하는 레이어로 본다.

### 채널 분리

Right-click 관련 산출물은 최소한 다음 구조를 가진다.

- `line_kind = evidence`
- `line_kind = exclusion`

즉, `rightclick 채널에 뭔가 있다`와 `진짜 우클릭 행동 증거가 있다`를 같은 사실로 취급하지 않는다. exclusion은 집계와 UI 후보군에서 먼저 빠지고, evidence 라인만 후속 분류 대상으로 간다.

### 2차 판정

`Strong / Weak / Exclude`는 채널 전체의 등급이 아니라, **evidence 라인 내부의 2차 판정**이다.

- Strong: 진짜 도구-게이트 행동
- Weak: 행동은 맞지만 속성/대체 가능성 때문에 증거가 약한 것
- Exclude: 행동 라인이지만 정의상 증거 주체로 세면 안 되는 것

이 구분은 `use_case 표면에 무엇을 올릴 것인가`를 정하는 정책이며, exclusion과 혼합하지 않는다.

### ID와 표면

`uc.action.*`는 가능하면 도구명보다 **능력 중심 ID**를 쓴다. 예를 들어 `hammer`보다 `construction` 같은 표현이 우선된다. 이유는 바닐라 특정 도구명보다 모드 확장 가능한 능력 카탈로그가 UI/분류 양쪽에 더 안정적이기 때문이다.

### UI 산출물

`[우클릭]` 블록은 문자열 라인을 다시 파싱하는 방식으로 만들지 않는다. 오프라인 Python은 구조화된 블록 데이터를 만든다.

예시 방향:
- `items[]`
- `debug_items[]`
- `display_text`

Lua는 이를 읽고 렌더만 한다. regex 역파싱, 문자열에서 능력을 복원하는 로직, label text를 다시 해체하는 로직은 금지한다.

### policy override

action_requirement_index가 비어 strength=None으로 떨어지는 문제는 evidence_decisions의 canonical 판정을 다시 쓰는 게 아니라, **registry policy override**로만 복구한다.

허용 조건:
- `uc.action.*`에 한정
- `decision == PASS`
- `override reason_code` 존재
- Q1/Q5 감시 대상

즉 override는 임의 PASS 주입이 아니라, automatic-only 계약 아래의 좁은 정책 예외다.

### 런타임 경계

Lua 런타임은 계속 렌더 전용이다.

- 문자열 해석 없음
- Strong/Weak/Exclude 재판정 없음
- line_kind 재분류 없음
- label fallback으로 의미 복원 없음

Right-click UI 통합은 `정제된 구조 데이터 -> 렌더` 경로 안에서만 일어난다.

### UI 충돌 경계

UI 통합은 `ISUIHandler.toggleUI` override보다 **독립 버튼 / 독립 블록 구조**를 우선한다. 이렇게 해야 다른 모드의 UI 수정과 기능적으로 독립한 상태를 유지할 수 있다.


## 11-18. Recipe interaction wiki layer

Iris의 레시피 상호작용 층은 단순한 레시피 이름 목록이 아니라, **navigation / per-recipe requirements / keep role / atom status display**를 포함한 구조화된 위키 레이어다.

### 기본 원칙

- recipe interaction은 설명 3-4층의 일부이며, 추천/정렬/숨김 UI가 아니다.
- `recipe_nav_ref`와 `recipe_requirements`는 같은 표면에 보일 수 있어도 내부적으로는 독립 산출물이다.
- keep 재료도 recipe line의 정당한 주체이며, consumed와 role로만 구분한다.
- 상태표시는 `display/check` 분리와 fail-soft를 지킬 때에만 허용된다.

### 오프라인 계약

- `recipe_nav_registry`가 점프 목표를 확정한다.
- `recipe_requirements_index`가 recipe 단위 requirements를 확정한다.
- `requirements.check`는 kind별 atom 상태표시 입력이다.
- keep 연결, dangling, suffix-drift, atoms_without_check, recipe_name 정합성은 전부 게이트 대상이다.

### 런타임 경계

- Lua는 navigation 버튼 렌더 + 점프 + atom 색상 렌더만 수행한다.
- `display`와 `check`는 오프라인이 확정하고, Lua는 둘을 해석해 새 구조를 만들지 않는다.
- 호환성 차이, 엔진 예외, near_item 미활성 등은 회색 또는 조용한 실패로 정리한다.

### 금지선

- 문자열 역파싱으로 recipe를 식별하는 경로
- fulltype 전체 공유 requirements
- keep 재료 비표시
- 요구사항 기반 숨김/정렬/추천 UI
- 데이터 스코프 오해를 막기 위한 무음 삭제

## 11-19. Frame reconfirmation

이번 단계에서 Frame은 새 기능 모듈이 아니라, 이미 잡혀 있던 철학을 다시 확인한 상태로 둔다.

- Frame은 세이브 관리자나 자동 해결기가 아니다.
- Frame은 모드팩 환경 상태를 시간축 위에서 관리하는 레이어다.
- Pulse는 Frame을 참조하지 않고, Frame은 Pulse capability만 소비한다.
- Hub & Spoke 구조 안에서 Frame은 상태/시간축을 담당하고, 다른 모듈 역할을 먹지 않는다.

따라서 Frame은 `기능을 더 붙일까`보다 `상태 스키마와 UX를 이 정체성 안에서 어떻게 닫을까`가 다음 단계의 본체다.



## 11-20. Layer 3 DVF body-only composition pipeline

Layer 3 DVF는 수동 완성문 모음이 아니라, **facts -> decisions -> profiles -> rendered**의 정적 계약을 따라 생성되는 결정론적 **본문 전용** 조합 파이프라인이다. tooltip은 current DVF 범위에 포함되지 않으며, 훗날 `layer3_facts.jsonl`이나 `layer3_rendered.json`을 소비하는 별도 시스템으로 분리한다.

### 기본 구조

1. **입력 검증**
   - 슬롯 값, origin, slot_meta, state, reason_code, compose_profile 계약을 검증한다.
2. **조합 실행**
   - profile이 sentence_plan, required_any, max_length를 정의하고 compose 경로는 이에 따라 rendered 본문을 만든다.
3. **rendered 검증**
   - 계층 경계, 길이, source mapping을 검증한다.
4. **결정론 검증**
   - entries-only SHA-256 비교를 1회 수행한다.

### 입력 / 산출 경계

- **입력**: `facts`, `decisions`, `profiles`
- **산출**: `layer3_rendered.json`
- **검증기**: `facts`, `decisions`, `rendered`
- **결정론 해시 대상**: `layer3_rendered.entries`

즉 current DVF는 본문 전용 엔진이며, tooltip 관련 스키마·생성기·검증기는 current scope 바깥이다.

### facts vs decisions 분리

- **facts**: identity_hint, primary_use, acquisition_hint, slot_meta 등 사실 데이터
- **decisions**: active/silent, reason_code, compose_profile, override, source mapping

두 파일은 변경 주기가 다르므로 분리한다. JSONL을 쓰되 `item_id` 유일성은 DVF에서 HARD FAIL로 강제한다.

### sentence_plan 규약

- 조합 단위는 전역 connector fallback이 아니라 **sentence_plan 블록**이다.
- 블록이 슬롯 순서까지 정의하므로 `slot_sequence`는 두지 않는다.
- 블록 내 슬롯 수는 최대 3개로 제한한다.
- 블록 간 구분자는 `문장 종결 + 공백 1개`다.
- `template_partial`은 블록 내부 일부 슬롯이 비었을 때만 사용한다.

### 슬롯과 메타

- 슬롯 값은 모두 템플릿 삽입용 **평문 string**이다.
- mode/text_ko 같은 부가 정보는 `slot_meta`로 분리한다.
- 전역 필수는 `identity_hint` 하나만 두고, 나머지 필수성은 profile의 `required_any`로 제어한다.
- `required_any ∩ global_required != ∅`는 설계 오류로 HARD FAIL이다.

### DVF 검증 경계

- decisions validator는 rendered를 보지 않는다.
- rendered 검증은 조합 이후 단계에서만 수행한다.
- 결정론 검증은 entries-only SHA-256 비교를 DVF에서 1회만 수행한다.
- `facts에 없는 사실 -> FAIL` 같은 항목은 두지 않는다.
- 대신 `active+compose -> composed`, `active+override -> override`, `silent -> silent` 같은 decision/rendered source mapping을 교차 검증한다.
- E단계 계층 경계 검증은 v1에서 4·5계층만 수행한다.

### v1 한국어 처리 계약

- 슬롯 값은 **조사까지 완료된 한국어 절/명사구**여야 한다.
- 조합기는 조사 처리나 종성 판별을 하지 않는다.
- `postproc_ko.py`는 이중공백, 마침표, 반복패턴 같은 후처리 정리만 담당한다.
- `{josa_xxx}` 토큰 잔류는 정상 기능이 아니라 비정상 데이터 탐지 규칙이다.

### tooltip 이관 계약

- current DVF에서 tooltip 관련 필드, 생성기, 검증기, 테스트는 제거하거나 `_archive/tooltip_v1/`로 이관한다.
- 후속 tooltip 시스템은 DVF 내부가 아니라 **DVF 산출물을 소비하는 별도 파이프라인**으로 설계한다.
- tooltip 시스템이 `layer3_facts.jsonl`, `layer3_rendered.json` 중 무엇을 입력으로 삼을지는 후속 설계 과제로 남긴다.

### v2 예약 항목

다음은 v1에서 열지 않고 v2로 이연한다.

- `josa_adaptive` connector
- 종성 판별/조사 매핑 엔진
- phrasebook_ko.json / ko_particles.json
- 1·2계층까지 포함한 E단계 경계 검증
- reason_code 복수 배열화


## 11-21. Layer 3 acquisition_hint elevation contract

tooltip 제거 이후 Layer 3 DVF의 다음 핵심 과제는 `acquisition_hint`를 **선택 슬롯**이 아니라 `identity_hint`, `primary_use`와 동급의 핵심 축으로 다루는 것이다. 이 격상은 새 파이프라인 단계를 추가하지 않고, 기존 `facts / decisions / profiles / rendered` 계약 위에서 **운영 규약과 validator 책임**을 강화하는 방식으로만 수행한다.

### 핵심 축 재정의

- Layer 3의 핵심 정보 축은 `identity_hint + primary_use + acquisition_hint`다.
- `acquisition_hint`는 더 이상 `있으면 넣는 부가 슬롯`이 아니다.
- 다만 이 승격은 새 계층(예: 2.5층) 추가를 뜻하지 않는다. 획득성은 계속 3계층 개별 설명 내부에서만 다룬다.

### facts / decisions 역할 분리

- **facts**: `acquisition_hint` 문자열과 `slot_meta.acquisition_hint` 같은 사실 데이터
- **decisions**: `acquisition_null_reason`, state, compose_profile 등 정책/운영 결정

`acquisition_hint = null` 자체는 facts에 남지만, 왜 null인지의 구조적 사유는 decisions가 가진다. current enum은 다음 둘만 허용한다.

- `UBIQUITOUS_ITEM`
- `STANDARDIZATION_IMPOSSIBLE`

### validator 계약

- JSON Schema는 `acquisition_null_reason`의 타입/enum까지만 검증한다.
- `facts.acquisition_hint == null -> decisions.acquisition_null_reason required`는 **cross-file validator**에서 강제한다.
- 단, silent 아이템은 facts 엔트리 자체가 없을 수 있으므로, **facts 부재 silent는 교차 검증 skip**이 current v1 규칙이다.

즉 acquisition 격상의 핵심은 스키마 확장이 아니라 **facts↔decisions 정합성 검문 강화**다.

### 프로파일 / sentence_plan 영향

- acquisition 블록은 limitation / processing보다 앞에 둔다.
- 그러나 3계층이 4계층처럼 불어나는 것은 금지한다.
- `medical_consumable` 등 acquisition 영향이 큰 프로파일도 current 기준은 **4블록/4문장 수준**이다.
- `required_any`는 프로파일별로 acquisition 격상 사실을 반영하되, 전역 필수(identity_hint 1개)와 중복되면 HARD FAIL이다.

### 문자열 계약

- `acquisition_hint`는 current v1에서 **단일 완성형 string**만 허용한다.
- 배열형 입력은 도입하지 않는다.
- 구조화 정보가 필요하면 `slot_meta.location_tags` 같은 메타를 사용한다.
- 슬롯 내부의 마침표는 `(?<!\d)\.(?!\d)` 기준의 **비소수점 마침표 0개** 원칙으로 HARD FAIL 처리한다.

### 후속 과제 경계

다음은 current 계약 바깥의 hold/v2 영역이다.

- acquisition 정규화 입력층(정적 데이터에서 장소/방식 자동 추출)
- acquisition 기반 active/silent 자동 재판정
- 전수 커버리지 지표 집계
- `slot_meta` 내부 값 검증 강화
- acquisition 배열화 + 조사 처리 엔진 연계

즉 current 단계는 **획득성의 위상을 올리는 설계와 validator 계약을 닫는 단계**이지, 정규화 파이프라인 전체를 새로 여는 단계가 아니다.



## 11-22. Iris as a validated knowledge production system

Iris는 `좋은 정보를 보여주는 위키 모드`를 넘어, **검증된 지식 생산 시스템**으로 해석한다. 핵심은 개별 기능 하나가 아니라 다음 전체 사슬이다.

1. 오프라인 evidence / outcome / use_case / Layer 3 facts 산출
2. QG / DVF를 통한 검문과 결정론 보장
3. 정적 산출물 생성
4. 런타임 Lua의 재구성·표시

따라서 Iris의 해자는 개별 레시피 버튼, 우클릭 라인, tooltip 한 줄보다 **검증 가능한 지식 파이프라인 전체**에서 나온다.

### QG / DVF / tooltip의 역할 분리

- **QG**: 증거 시스템과 그 파생 산출물의 운영 검문 체계
- **DVF**: Layer 3 본문 전용 설명 검증 체계
- **tooltip**: 독립 지식원이 아니라 메뉴 본문의 핵심 추출 요약층

즉 QG는 `evidence compiler` 쪽, DVF는 `Layer 3 body generator/validator` 쪽, tooltip은 그 뒤의 얕은 소비층이다.

### 3계층 / 2계층 / 4계층의 상대 역할

- **Layer 2**: 더 추상적이고 압축적인 공통 설명층
- **Layer 3**: 파밍 장소, 핵심 용도, 가공 맥락, 같은 군 안의 개별성을 담는 **미니 본문층**
- **Layer 4**: 짧고 탐색형인 구조층

따라서 3계층은 `한 줄 정의문`으로 축소하지 않고, tooltip은 3계층을 대체하지 않는다.

### tooltip의 위치

tooltip은 `메뉴와 경쟁하는 독립 본문`이 아니라, 메뉴 본문에서 핵심만 추출한 1차 표면이다. current 방향은 다음과 같다.

- tooltip은 주로 `3-2 / 3-3`의 핵심을 소비한다.
- `3-1 / 3-4 / 3-5`를 tooltip에 그대로 싣는 것은 기본값이 아니다.
- tooltip은 호기심과 1차 필터링을 담당하고, 메뉴는 더 깊은 본문을 담당한다.

즉 tooltip은 `더 작은 위키`가 아니라 **본문의 얕은 extractive view**다.

## 11-23. Iris external-mod normalization boundary

Iris의 외부 모드 확장은 raw mod file을 QG/DVF가 직접 읽는 구조가 아니라, **정규화 계층을 앞에 둔 compiler 구조**로만 연다.

### 정규화 경로

`원본 mod file -> normalization adapter/compiler -> Iris 표준 산출물 -> QG/DVF 소비`

여기서:

- adapter/compiler는 원본 모드 구조를 읽고
- 내부 표준 facts/evidence/use_case/DVF 입력 형태로 정규화하며
- QG와 DVF는 그 **정규화 산출물만** 소비한다.

### 포맷 경계

- 외부 입력/교환 형식은 JSON / SQLite 같은 열린 형식을 허용한다.
- 내부에서는 필요하면 `.Iris` 같은 정규화 캐시/포맷을 둘 수 있다.
- 그러나 QG/DVF가 raw parser이자 validator가 되는 구조는 금지한다.

### 이유

검증기(QG/DVF)가 parser 역할까지 먹으면, `검증 / 정규화 / 해석`의 경계가 무너져 역할 침범과 호환성 리스크가 커진다. 따라서 Iris는 `모든 모드를 추론하는 AI 위키`가 아니라, **구조를 제공한 모드를 정규화해 위키 표면으로 재구성하는 시스템**으로 남는다.

## 11-24. Final-applied fact rule for mod conflicts

여러 모드가 같은 아이템을 수정하는 경우, Iris는 **엔진 최종 적용값 기준의 사실만 표시**한다.

- 어떤 모드가 더 맞는지 판정하지 않는다.
- 무엇을 숨겨야 하는지 결정하지 않는다.
- 권장 병합안이나 정답 순서를 제시하지 않는다.

즉 Iris는 충돌의 심판이 아니라, **최종적으로 적용된 사실을 위키 형태로 보여주는 관찰자**다.

## 11-25. Ecosystem moat and peer-spoke interpretation

Pulse 생태계 전체는 `플랫폼 위의 플랫폼들을 품는 구조 해자`로 해석할 수 있지만, 이때도 Frame과 Canvas를 다른 하위 모듈보다 상위 지위로 읽지 않는다.

- **Pulse**: 얇은 기반 capability 플랫폼
- **Iris**: 검증된 지식 생산 시스템
- **Frame**: 모드팩 상태 관리자
- **Canvas**: 리소스 적용 상태 관리자
- **Echo / Fuse / Nerve**: 관찰 / 안정화 / Lua 안정성 축

여기서 Frame과 Canvas는 결과적으로 큰 영향력을 가질 수 있어도, 구조적으로는 다른 하위 모듈과 동일한 **peer spoke**다.

### 의미

- Frame/Canvas는 `특별대우 대상`이 아니다.
- Frame/Canvas를 Pulse보다 한 단계 위의 특권 축으로 설계하지 않는다.
- 생태계 해자는 개별 모듈의 우열보다, **각 spoke가 자기 문제를 풀면서 함께 만드는 구조와 데이터 자산**에서 생긴다.

따라서 Frame/Canvas는 `중요할 수는 있지만 특별한 모듈은 아닌` 상태로 문서화한다.


## 11-26. Acquisition coverage staging-first closeout and candidate_state separation

`acquisition_hint` 격상은 설계 문장으로만 끝나지 않고, **전 아이템 acquisition coverage를 staging-first 방식으로 닫는 운영 단계**까지 포함한다. 동시에 이 단계는 `candidate_state` 재평가와 구조적으로 분리한다.

### staging-first 운영 구조

acquisition coverage는 다음 네 층으로 운영한다.

1. **master**
   - 전체 대상 분모와 현재 disposition 상태를 보관한다.
2. **review**
   - 사람/배치가 실제 검토한 acquisition 결과를 쌓는다.
3. **gate**
   - disposition 허용값, 분모 잠금, remaining bucket 0 여부를 검문한다.
4. **report**
   - completion, bucket, disposition counts를 산출한다.

즉 canon facts/decisions를 바로 덮는 것이 아니라, staging 영역에서 먼저 review를 닫고 gate 이후에만 정식 산출물로 반영한다.

### disposition 계약

current acquisition coverage disposition은 다음 넷으로 고정한다.

- `UNREVIEWED`
- `ACQ_HINT`
- `ACQ_NULL`
- `SYSTEM_EXCLUDED`

이 구조는 `획득성 존재 여부`와 `null 사유`, `시스템 제외`를 운영적으로 구분하기 위한 것이며, candidate_state(active/silent)와는 별도 축이다.

### Phase 2 종료 조건

acquisition coverage Phase 2는 다음 조건을 만족할 때 종료로 본다.

- `closed = 2285 / 2285`
- `unreviewed = 0`
- `acquisition_review_completion_pct = 100.0`
- `ACQ_HINT = 2037`
- `ACQ_NULL = 42`
- `SYSTEM_EXCLUDED = 206`
- `top_remaining_buckets = []`

즉 Phase 2의 성공 기준은 `전 아이템 획득성 검토를 닫는 것`이지, active/silent를 바꾸는 것이 아니다.

## 11-27. Candidate_state reevaluation is a separate Phase 3 concern

acquisition coverage가 닫혔다고 해서 곧바로 `silent -> active` 재판정을 수행하지 않는다. `candidate_state` 재평가는 별도 Phase 3 책임으로 둔다.

### 분리 원칙

- **Phase 2**: 획득성 review를 닫는다.
- **Phase 3**: 그 결과를 근거로 `KEEP_SILENT / PROMOTE_ACTIVE / MANUAL_OVERRIDE_CANDIDATE`를 판정한다.

두 단계를 한 흐름으로 섞으면, review 중간 상태가 곧바로 본문 상태 판정에 유입되어 기준이 오염된다. 따라서 acquisition review 100% 완료는 `후속 재평가의 입력 조건`일 뿐이며, active 승격을 자동으로 뜻하지 않는다.

### 현재 상태

current closeout 시점에서 candidate_state 재평가 수치는 아직 열리지 않았다.

- `promote_active_count = 0`
- `keep_silent_count = 0`
- `manual_override_candidate_count = 0`

즉 Phase 3는 **미착수 상태**이며, 다음 세션에서 운영 규약·산출물·gate를 먼저 설계한 뒤 착수해야 한다.

### 재논쟁 가능 지점

Phase 3에서 특히 다시 열릴 가능성이 큰 질문은 다음과 같다.

- `acquisition_hint가 있으면 active인가?`
- `UBIQUITOUS_ITEM`과 `STANDARDIZATION_IMPOSSIBLE`의 경계는 유지되는가?
- `MANUAL_OVERRIDE_CANDIDATE`를 어디까지 허용할 것인가?
- 3계층 본문과 4계층 관련 정보의 경계는 acquisition 승격 후에도 유지되는가?

따라서 current 단계의 올바른 해석은 `획득성 coverage closeout`이지 `candidate_state reclassification complete`가 아니다.



## 11-28. Phase 3 closeout treats candidate_state and approval as separate operational planes

Phase 3에서는 `candidate_state`와 `approval`을 같은 상태기계로 취급하지 않는다. 둘은 서로 영향을 주더라도 **분리된 운영 평면**이다.

### candidate_state 평면

Phase 3의 staging 판정은 다음 셋으로 고정한다.

- `KEEP_SILENT`
- `PROMOTE_ACTIVE`
- `MANUAL_OVERRIDE_CANDIDATE`

이 셋은 `본문을 어떻게 다룰 것인가`에 관한 staging disposition이며, acquisition review 완료나 approval closeout과 자동 동치가 아니다.

### approval 평면

approval은 backlog 운영과 sync-ready 상태를 다루는 별도 평면이다.  
즉 `approval done`은 운영 큐가 닫혔다는 뜻이지, 모든 candidate가 곧바로 active로 승격되었다는 뜻이 아니다.

### 분리 효과

이 분리를 유지해야만 다음이 가능하다.

- acquisition review 완료와 본문 상태 판정을 섞지 않기
- override 후보를 approval 잔여와 같은 것으로 오해하지 않기
- `KEEP_HOLD` 같은 운영상 잔여를 의미 체계 수정 없이 처리하기

따라서 Phase 3 closeout은 `candidate_state settled`와 `approval backlog closed`를 각각 별도 표면으로 보고해야 한다.

## 11-29. Approval backlog operations are no-rule-change, cluster-first, and queue-sourced

Wave 3에서 manual concentration이 치솟았을 때, current 구조는 규칙 패치가 아니라 **운영 레이어 강화**로 대응한다.

### 운영 원칙

- 기본 모드는 `NO_RULE_CHANGE_BATCH_REVIEW`
- backlog는 hotspot / cluster 단위로 관리
- hotspot은 자동 승격 규칙이 아니라 **JSON 명시 등록형**으로 유지
- 수치 출처는 `evidence_decisions`가 아니라 **approval queue / HOLD queue 계열 산출물**

### 왜 이렇게 두는가

manual 집중의 원인이 새 rule failure가 아니라 기존 `LAYER_COLLISION` backlog의 밀집이라면, 이를 규칙 변경으로 누르면 의미 체계가 오염된다. 따라서 current 운영 구조는 `규칙은 고정하고 backlog만 운영적으로 소진`하는 쪽을 택한다.

### 결과 해석

- `OPEN / IN_REVIEW` cluster 소멸은 운영 closeout이다.
- 잔존 `KEEP_HOLD`는 미처리 누수가 아니라 정책적 보류다.
- approval backlog 통계와 evidence 통계를 섞어 읽지 않는다.

즉 current approval closeout은 `rule rewrite success`가 아니라 `no-rule-change operations success`다.

## 11-30. DVF 3-3 production batch remains separate from demo outputs

DVF 3-3은 기존 demo Layer 3 산출물과 다른 위상의 production batch로 취급한다.

### 파일 계열 분리

production 3-3은 다음 계열로 분리한다.

- `dvf_3_3_facts`
- `dvf_3_3_decisions`
- `dvf_3_3_rendered`

이는 초기 demo용 `layer3_facts / layer3_decisions`와 섞지 않는다.

### 이유

demo 10건은 조합 규칙과 validator 실험을 위한 샘플이고, 1000건대 approved subset은 실제 운영 batch다. 둘을 합치면 회귀 범위와 determinism 문맥이 흐려진다.

### 결과

DVF 3-3의 batch 검증, diff 감시, determinism 검증은 별도 production 계열을 기준으로 수행한다.

## 11-31. DVF freeze requires both offline completion and actual runtime consumer hookup

DVF 3-3의 freeze 기준은 `오프라인 산출 완료` 하나로 닫지 않는다.

### 최소 완료 조건

1. 오프라인 batch 완료
   - facts / decisions / rendered 생성
   - validator PASS
   - determinism PASS
2. Lua bridge 존재
3. **실제 소비자 연결 확인**
   - `IrisBrowser.lua`
   - `IrisWikiPanel.lua`
4. 메뉴 표면에서 3계층 본문 렌더 확인

### 금지되는 오판

- dead hook를 소비자 연결로 오인하는 것
- `Lua bridge exists`를 `UI integrated`와 같은 말로 쓰는 것
- pipeline complete를 freeze complete로 성급히 등치하는 것

즉 current 구조에서 `offline complete != runtime integrated`다.

## 11-32. Identity generation and template naturalization belong to different layers

DVF 3-3의 자연어 품질 문제를 다룰 때는, **facts 생산층**과 **표면 template 층**을 분리해서 본다.

### identity 생산층

`identity_hint`는 current 구조에서 다음 방식으로 생산한다.

- 규칙 기반 자동 생성
- category mapping (`identity_category_ko.json` 계열)
- 소수 override

이 층의 책임은 scale과 일관성이다.

### template 표면층

`도구. ~에서 찾을 수 있다.` 같은 비문 문제는 facts 생산 실패나 candidate_state 오판이 아니라, **compose template 연결 방식의 표면형 문제**다.

### 영향

따라서 후속 자연화 작업은 다음 순서로 다룬다.

1. template 수정
2. 재빌드
3. validator / regression 재검증

반대로 다음은 current 기본 해법이 아니다.

- Phase 3 재판정 재오픈
- approval closeout 무효화
- acquisition / identity facts 재분류


## 11-33. Layer 3-3 remains a body layer and must not absorb Layer 3-4 interaction detail

3-3 개편 논의가 다시 열리더라도, current 헌법선은 **3-3과 3-4의 분리 유지**다.

### 3-3의 책임

- 아이템 자기 시점의 핵심 의미 압축
- 용도 / use 중심의 짧은 본문
- acquisition이 있더라도 후행 정보로 포함

### 3-4의 책임

- 레시피
- 우클릭 행동
- 관련 상호작용의 세부 목록과 구조화 정보

### 금지선

- 3-3에서 3-4 수준의 상세 상호작용을 전부 흡수하는 것
- 표면형 문제를 이유로 3-4를 3-3 안에 녹여버리는 것
- `개봉해 탄약을 얻는다`류의 문장을 무제한 확장해 3-4를 대체하는 것

## 11-34. ACQ_ONLY surface-form repair belongs to compose-time subject synthesis, not post-processing hacks

ACQ_ONLY 3-3 본문의 한국어 비문 문제는 `identity_hint` 사실값의 실패가 아니라, **명사구를 독립 문장처럼 출력한 compose 방식**의 실패로 본다.

### compose-time 책임

- `identity_subject`는 compose-time에 생성한다.
- 주어/조사 결합은 rendered 본문 생성 전에 닫는다.
- 이 단계는 facts 재판정이나 Phase 3 상태 재오픈을 뜻하지 않는다.

### postproc 책임

postproc은 다음만 담당한다.

- 띄어쓰기 정리
- 문장부호 정리
- 기계적 표면 정규화

즉 조사 선택이나 주어 복원 같은 문장 의미 작업을 postproc으로 미루지 않는다.

## 11-35. Layer 3-3 is an item-centric body, not an acquisition-led farming notice

표면형 수정이 끝난 뒤 current 구조는 더 큰 문제를 드러냈다. 3-3이 자연스럽더라도 **아이템 용도 설명보다 파밍 안내문에 가까우면** 헌법상 Layer 3-3의 역할과 어긋난다.

### 기본 순서

후속 3-3 본문은 다음 순서를 기본으로 삼는다.

1. `item_subject`
2. 용도 / use
3. 아이템 자기 기준 변환·상호작용
4. acquisition

### acquisition의 위치

획득 문장은 삭제하지 않는다. 다만 3-3의 선두를 점령하지 않게 **후행 슬롯**으로 둔다.

### Layer 3-4와의 경계

- 3-3은 아이템 자기 시점의 핵심 의미를 압축한다.
- 3-4는 레시피/우클릭 등 파고드는 상호작용 세부를 맡는다.
- 3-3이 3-4를 먹어버리면 안 된다.

## 11-36. Iris release posture is accessibility-first and vanilla-first; mod expansion stays downstream

Iris의 첫 공개 전략은 `지원 범위 최대화`가 아니라 **접근성 해자**를 먼저 증명하는 방향으로 둔다.

### moat 해석

Iris의 1차 해자는 `위키 대체 정확도 총량`이 아니라 다음에 둔다.

- 게임 안에서 바로 접근 가능함
- 아이템 시점의 용도 설명을 더 빨리 보여줌
- 위키를 열기 전에 먼저 보게 만드는 낮은 인지 비용

### 공개 순서

- 첫 공개는 `vanilla-first`
- 모드 확장 시스템은 내부적으로 개발할 수 있어도 전면 홍보는 후속 단계
- `모든 외부 모드 지원` 약속은 current 공개 범위 밖

### 구조 효과

이렇게 해야 Iris 본체의 문장 품질 / 정보 구조 / UI 검증보다, 지원 범위 문의와 호환성 논쟁이 앞서는 것을 피할 수 있다.


---

## 11-37. Iris DVF 3-3 post-cleanup operational architecture addendum

이번 addendum은 기존 Iris 구조 설명을 버리는 것이 아니라, **weak-active cleanup 이후 DVF 3-3이 실제 운영 시스템으로 어디까지 닫혔는지**를 구조 문서에 덧붙이는 것이다.

### 구조상 선행/후행 단계 분리

현재 Iris DVF 3-3 운영 구조에서는 다음 네 단계가 서로 다른 책임을 가진다.

1. **weak-active cleanup**
   - provenance / semantic split / disposition closure
   - 무엇이 strong / adequate / weak인지 판정하는 단계
2. **2-stage status model**
   - cleanup 결과를 runtime contract로 번역하는 해석 계약 단계
3. **runtime adoption**
   - candidate artifact 중 실제 runtime lane으로 채택할 대상을 반영하는 단계
4. **backlog expansion**
   - weak backlog와 net-new cluster 필요 lane을 후속 패키지 단위로 확장하는 제작 단계

이 네 단계는 더 이상 하나의 흐릿한 `후속 정리`로 취급하지 않는다.

### cleanup baseline과 adoption artifact의 경계

- `W-6 aggregate`는 post-cleanup 이후 단계의 **authority baseline**이다.
- `integrated_facts.post_cleanup_candidate.jsonl`은 adoption 이전까지 **candidate-only artifact** 다.
- 따라서 cleanup 완료와 runtime 채택 완료는 같은 상태가 아니다.

즉, 현재 아키텍처는 `분류 완료`와 `runtime 반영 완료`를 의도적으로 분리한다.

### 2-stage status model은 open gap이 아니라 구현된 운영 계약이다

기존 구조 문맥에서는 runtime availability와 semantic quality의 분리가 `다음 아키텍처 gap`처럼 보였지만, 이번 세션 기준으로는 **Phase 1에서 2-stage status model closure가 이미 완료**됐다.

현재 closure된 핵심 조합은 다음과 같다.

- `generated::weak 133` -> `keep_generated_no_indicator`
- `missing::strong 21` -> `adopt_in_phase2`
- `missing::adequate 9` -> `keep_missing`
- `missing::weak 45` -> `lower_than_generated_weak`
- UI quality exposure -> `no_ui_exposure`

즉, `runtime availability`와 `semantic quality`를 분리해야 한다는 문제 제기 단계는 지났고, **운영 가능한 상태 모델이 이미 닫힌 상태**다.

### runtime adoption은 실제 reflection과 인게임 검증까지 포함한다

현재 구조에서 runtime adoption은 단순 오프라인 rebuild가 아니다.

- adoption scope freeze
- validation
- rebuilt facts/rendered/Lua bridge 생성
- 실제 runtime reflection
- 인게임 validation

까지를 한 단계로 본다.

이번 세션에서는 `missing::strong 21` adoption이 이 경로를 끝까지 통과했고, Phase 2 결과는 runtime snapshot `2105 rows / active 2051 / silent 54`로 닫혔다.

### backlog expansion은 package execution + integrated runtime rebuild 구조다

backlog expansion 역시 단순 source 탐색이 아니라 다음 구조를 가진다.

- backlog exploration
- package split
- package first pass execution
- integrated runtime rebuild
- runtime reflection
- in-game validation

이번 세션 기준 first pass 결과는 다음과 같다.

- promoted rows: `46`
- residual backlog: `132`
- integrated runtime snapshot: `2105 rows / active 2060 / silent 45`

즉, backlog expansion은 더 이상 `언젠가 source를 넓힌다`는 추상 문장이 아니라 **runtime surface를 실제로 끌어올리는 운영 패스**다.

### validation은 absolute gate가 아니라 baseline-delta gate로 읽는다

Phase 3 통합 검증에서 중요한 구조 수정은 validation 해석 방식이다.

- absolute hard gate는 기존 salvage lane까지 절대값으로 다시 세는 문제가 있었다.
- 현재 운영 기준은 **baseline-delta gate** 다.

따라서 구조적으로 중요한 질문은
`절대 fail 수치가 몇 개인가`가 아니라,
`이번 pass가 새 fail을 추가했는가 / baseline 대비 무엇을 줄였는가`로 바뀌었다.

현재 기준에서는:

- introduced hard fail: `0`
- resolved hard fail: `36`
- introduced warn: `0`
- resolved warn: `36`

이다.

### runtime contract와 UI contract는 계속 분리된다

이번 세션 이후에도 다음 분리는 유지된다.

- **runtime contract**: 어떤 row를 runtime이 소비하고 반영하는가
- **UI contract**: semantic quality를 사용자 표면에 노출하는가

이번 round에서는 runtime contract가 먼저 닫혔고, semantic quality UI exposure는 계속 `no_ui_exposure` 상태로 남는다.

즉, status model이 생겼다고 해서 곧바로 UI quality indicator를 붙이지 않는다.

### 현재 남은 아키텍처 과제

이번 세션 이후의 주된 architectural gap은 더 이상 `2-stage status model 정의`가 아니다.
현재 남아 있는 것은 다음이다.

- residual backlog `132` second-pass expansion
- net-new cluster가 필요한 lane 정리
- `generated::weak 133` / `missing::adequate 9`의 future 운영 판단
- semantic quality를 UI contract로 승격할지 여부에 대한 장기 결정

즉, 현재 Iris DVF 3-3의 구조 문제는 `모델이 없어서 못 움직이는 상태`가 아니라, **운영 시스템이 이미 굴러가고 있고 남은 잔여 lane을 어떤 순서로 닫을지**의 문제로 옮겨갔다.

## 11-38. Iris DVF 3-3 second-pass closure는 더 이상 열린 execution architecture가 아니다

second-pass execution과 manual validation note까지 기록된 현재 기준에서, Iris DVF 3-3의 구조 상태는 다시 한 번 바뀌었다.

### 현재 닫힌 것

- residual backlog `132` second pass execution은 `Phase 0~7` build/runtime path까지 닫혔다.
- current runtime baseline은 `2105 rows / active 2084 / silent 21` 이다.
- final residual `34`는 execution backlog가 아니라 **hold inventory** 다.
- manual in-game validation은 **browser/wiki surface smoke check 기준 `pass_with_note`** 로 기록됐다.

즉, second pass는 더 이상 `아직 실행해야 하는 package architecture`가 아니다.

### 현재 구조에서의 의미

현재 아키텍처에서 second pass는 다음처럼 읽는다.

- runtime surface는 이미 reflected baseline으로 닫혀 있다.
- hold taxonomy는 미완료 sprint queue가 아니라 future reopen contract다.
- manual validation은 implementation blocker가 아니라 closeout note다.

따라서 current 구조에서 `second-pass expansion` 자체를 열린 architectural gap으로 다시 서술하지 않는다.

### 이후 남는 구조 과제

이후 남는 것은 second pass 자체가 아니라 다음 세 가지다.

- `future_promote_condition`이 성숙한 hold subset만 reopen하는 운영 구조
- `generated::weak 133` / `missing::adequate 9`의 장기 정책 판단
- semantic quality를 UI contract로 승격할지에 대한 별도 결정

즉, 현재 Iris DVF 3-3의 구조 문제는 `second pass를 끝내야 한다`가 아니라, **닫힌 current runtime 위에서 어떤 future subset만 다시 열 것인가**의 문제다.

## 11-39. Iris DVF 3-3 style surface normalization은 post-compose deterministic layer다

second-pass closure 이후 열린 별도 과제는 facts/decisions 재판정이 아니라, **compose 산출물의 표면형을 결정론적으로 정리하는 style surface layer** 다. 이 계층은 의미 판단기가 아니라 post-compose 정규화기이며, runtime/Lua 계약을 다시 열지 않는다.

### 현재 파이프라인 위치

현재 DVF 3-3의 본문 경로는 다음처럼 읽는다.

- `facts -> decisions -> compose -> normalizer -> style linter -> rendered -> Lua bridge -> runtime`
- normalizer는 compose 뒤, rendered 앞에서만 동작한다.
- style linter는 normalizer 이후에 실행되지만 산출물을 바꾸지 않고 report만 만든다.

### normalizer 책임

normalizer는 다음 책임만 가진다.

- literal/regex 기반의 **결정론적 어휘 치환**
- 기존 `postproc_ko.py`가 맡던 띄어쓰기/문장부호 정리의 최종 단계 흡수
- rule id / before-after를 남기는 change log 생성

반대로 normalizer는 다음을 하지 않는다.

- evidence / cluster / fact_origin 재판정
- candidate_state 재오픈
- rendered ↔ Lua 계약 재정의
- semantic quality 판정

### family rule 바인딩과 manual override

family rule scope는 새 semantic 축 없이 **`fact_origin + selected_cluster_contains`** 로만 바인딩한다.

- `selected_cluster = null`은 매칭 시 `unknown` sentinel로 해석한다.
- `tool 계열` 같은 설명어는 문서 표현으로 남기지 않고 실제 바인딩 키로 환원한다.

`manual_override_text_ko`는 작성자 의도를 보존하기 위해 **style rule은 건너뛰고 legacy postproc만 적용** 한다.

### style linter 책임

style linter는 quality gate가 아니라 **advisory report layer** 다.

- 출력: `style_lint_report.json`
- 역할: batch 빈도 이상치와 잔여 상투 표현을 관측
- 비역할: 자동 수정, baseline-delta gate 합류, runtime contract 판정

즉, `introduced hard fail / warn` 같은 생산 게이트는 기존 validator가 계속 맡고, style linter는 운영 backlog를 정리하는 보조 관측 계층으로만 남는다.

### 현재 운영 상태

2026-04-03 기준 first operational pass는 다음처럼 읽는다.

- Phase 0 baseline scan은 `active 2084` 기준으로 closure됐다.
- Phase 1에서는 `G-01`, `F-01`만 활성화됐고 active-rules dry run에서 `18`건만 변경됐으며 introduced hard fail/warn은 `0` 이었다.
- postproc 흡수 검증은 `style rules off + legacy postproc only` 경로에서 byte-identical로 통과했다.
- Phase 2에서는 `L-01`, `L-02`, `L-04`가 advisory WARN으로만 활성화됐다.

## 11-40. Iris DVF 3-3 body-role architecture closes through decisions overlay, compose-internal repair, and next-build feedback

style surface round 이후 열린 body-role round는 facts 재생산 아키텍처가 아니라, **기존 facts를 authoritative wiki body처럼 읽히게 만드는 운영 구조**로 닫혔다. 핵심은 facts를 늘리지 않고, decisions overlay와 compose 내부 repair로 3-3 body 역할을 고정한 점이다.

### 책임 분해

현재 body-role 구조에서 책임은 다음처럼 분리된다.

1. **facts**
   - `identity_hint / primary_use / acquisition_hint / fact_origin` 같은 기존 사실값만 유지한다.
   - `representative_use / secondary_use / distinctive_mechanic` 같은 새 facts 슬롯은 만들지 않는다.
2. **decisions overlay**
   - `layer3_role_check`
   - `representative_slot`
   - `body_slot_hints`
   - `representative_slot_override`
   - 무엇을 새 사실로 넣을지 결정하는 층이 아니라, **기존 사실을 어떻게 전면 배치할지 결정하는 층**이다.
3. **compose**
   - overlay를 읽고 sentence plan을 고른다.
   - 같은 함수 내부에서 repair 규칙을 수행한다.
   - `quality_flag`를 rendered 진단 메타데이터로만 남긴다.
4. **lint / semantic feedback**
   - 현재 빌드를 되감아 다시 compose하지 않는다.
   - 다음 빌드 overlay 재판정에 들어갈 feedback만 만든다.

즉, body-role round는 `facts 고도화`가 아니라 **결정과 조합 경로의 재봉인**이다.

### 현재 파이프라인 위치

현재 body-role 경로는 다음처럼 읽는다.

- `facts -> decisions -> body-role overlay -> compose(internal repair) -> rendered(+diagnostic meta) -> structural lint/feedback -> next-build overlay builder`

여기서 중요한 점은 두 가지다.

- repair는 compose 외부 stage가 아니다.
- lint feedback은 same-build rewrite를 하지 않는다.

따라서 `compose -> repair script -> re-compose` 같은 2중 조합 구조는 현재 아키텍처에서 금지된다.

### `quality_flag`와 상태 축의 분리

`quality_flag`는 rendered에 남지만 구조상 **상태 축이 아니다**.

- 허용값은 `function_narrow / identity_only / acq_dominant_reordered`로 고정한다.
- Lua bridge와 UI surface는 이를 소비하지 않는다.
- semantic quality나 runtime availability와 교차 조합을 만들지 않는다.

이렇게 해야 기존 2-stage status model과 body-role 진단 메타가 서로 오염되지 않는다.

### structural feedback의 시점 규칙

body-role structural lint와 semantic linkage는 다음 원칙으로 닫혔다.

- `LAYER4_ABSORPTION`만 hard block이다.
- `SINGLE_FUNCTION_LOCK`, `BODY_LACKS_ITEM_SPECIFIC_USE`, `REPRESENTATIVE_USE_MISSING` 같은 패턴은 **feedback-only** 다.
- feedback artifact는 매 빌드 fresh recompute 하며 누적 상태로 재사용하지 않는다.
- semantic weak candidate는 산출하되 semantic axis를 자동 갱신하지 않는다.

즉, 현재 구조에서 Phase 4/6은 **현재 빌드를 바꾸는 수정 경로**가 아니라 **다음 빌드 overlay builder에 들어갈 진단 경로**다.

### current authority와 closeout 상태

현재 body-role authority는 fixture가 아니라 full preview authority다.

- authority row count: `2105`
- audit/overlay/rendered row count: 모두 `2105`
- baseline/current hard fail: `663 / 663`
- introduced hard fail: `0`
- regression rejected: `0`
- golden subset: `100`
- in-game validation: `pass`

이 구조적 의미는 분명하다.

- body-role round는 열린 설계 실험이 아니라 **build/runtime/in-game closeout** 상태다.
- 남은 architectural gap은 body-role 조합 경로가 아니라 **identity_fallback source expansion** 과 **semantic axis future decision** 쪽이다.

### 이후 남는 구조 과제

현재 architecture 관점에서 남는 일과 policy-resolved hold는 다음 넷이다.

- `identity_fallback 617` source expansion
- `bucket_2_net_new_cluster_required 599`에 대한 net-new cluster 설계
- semantic weak candidate carry policy는 SAPR에서 닫혔다.
  - `structural feedback weak candidate`와 `source-expansion post-round new weak`는 operating-rule candidate family로만 유지한다.
  - `body-role mapping weak`, `adequate 유지군`, `legacy/generated weak reference`는 observer-only로 유지한다.
  - actual semantic axis carry와 baseline `v5` cutover는 future explicit decision + separate execution round가 있을 때만 연다.
- source expansion 이후 분포 재측정

즉, 현재 Iris DVF 3-3의 body-role 구조 문제는 `어떻게 compose를 다시 설계할까`가 아니라, **닫힌 compose/feedback 구조 위에서 어떤 source subset을 다시 열 것인가**의 문제다.

## 11-41. Iris DVF 3-3 current architecture uses a three-axis contract over the preserved runtime model

body-role closeout 이후 problem 2 round는 먼저 **internal semantic-quality feedback loop** 로 닫혔고, 그 다음 별도 contract migration round를 거쳐 current runtime/user-facing contract가 3축 모델로 재구성됐다. 핵심은 기존 2-stage runtime model을 폐기하지 않고, 그 위에 quality contract와 publish contract를 추가한 점이다.

### 현재 구조상 출발점

current authority baseline은 다음이다.

- total rows: `2105`
- runtime_state adopted: `2084` (legacy `active`)
- runtime_state unadopted: `21` (legacy `silent`)
- adopted origin: `cluster_summary 1440 / identity_fallback 617 / role_fallback 48`
- publish surface: `internal_only 617 / exposed 1467`

이 baseline은 구조적으로 다음을 뜻한다.

- `adopted`는 quality-pass 집합이 아니다.
- `identity_fallback 617`은 runtime에서 사라진 것이 아니라 `internal_only` policy-isolation inventory로 남아 있다.
- current user-facing default surface는 runtime availability와 publish visibility를 서로 다른 계약으로 읽는다.

### current 3축 모델

current architecture에서 authoritative axis는 다음 셋이다.

- `runtime_state = adopted / unadopted`
  - 의미: runtime adopted 여부
  - legacy: `active -> adopted`, `silent -> unadopted`
  - `adopted`는 quality-pass를 암시하지 않는다.
- post-migration `semantic_quality` 또는 `quality_state`
  - 의미: downstream publish decision까지 연결되는 authoritative quality contract
  - current values: `strong / adequate / weak`
  - reserved inactive: `fail`
- `publish_state = internal_only / exposed`
  - 의미: default consumer surface visibility
  - `quality_exposed`는 reserved inactive

즉, current 구조는 legacy `active/silent`를 quality 의미로 다시 쓰지 않고, `adopted/unadopted`, quality, visibility를 별도 축으로 분리해 관리한다.

### DVF 3-3 runtime_state vocabulary and three-axis readpoint

Current canonical runtime_state values are `adopted / unadopted`.

Legacy runtime_state wording is read as `active -> adopted`, `silent -> unadopted`.

This is terminology-only. `adopted` means runtime-adopted only and does not imply quality-pass. `unadopted` is not a `publish_state` and does not mean deletion. `internal_only` is not runtime deletion; it is default Browser/Wiki visibility suppression.

Historical DVF 3-3 sections may still say `active/silent`. Those terms are read through this terminology note when they refer to runtime_state. Historical bodies are preserved.

### 현재 파이프라인 위치

current 경로는 다음처럼 읽는다.

- `facts -> decisions -> body-role overlay -> compose(internal repair + requeue capture) -> quality/publish decision stage -> rendered + publish decision preview -> Lua bridge -> Browser/Wiki default consumer`

여기서 중요한 점은 네 가지다.

1. compose 외부 repair는 계속 금지된다.
2. post-compose stage는 rendered text를 바꾸지 않고 `quality_state`와 `publish_state`만 기록한다.
3. offline preview와 validator가 먼저 닫힌 뒤에만 bridge/runtime migration으로 넘어간다.
4. runtime Lua는 publish 판단을 하지 않고, 이미 계산된 `publish_state`를 읽어 렌더만 분기한다.

### quality contract의 구조적 성격

current architecture에서 quality contract는 다음처럼 해석한다.

- source: 기존 semantic axis + `layer3_role_check` + compose 이후 quality/publish decision stage
- owner: **quality/publish decision stage single writer**
- non-writer:
  - overlay builder
  - compose
  - validator
  - Lua bridge
  - Browser/Wiki consumer
- validator role:
  - ownership 위반 감지
  - bridge contract drift 감지
  - emitted state inconsistency 감지
  - writer 역할은 하지 않음

즉, post-migration `semantic_quality`는 problem 2 round의 derived/cache semantics를 시간축 없이 뒤집는 것이 아니라, **contract migration round 이후에만** authoritative quality contract로 재정의된 상태다.

### publish contract와 bridge semantics

current publish contract는 다음처럼 고정한다.

- `internal_only`
  - row는 runtime artifact와 Lua bridge에 남는다.
  - 3-3 body도 nil 처리하지 않는다.
  - Browser/Wiki default consumer만 렌더를 억제한다.
- `exposed`
  - default surface 노출을 허용한다.
- `quality_exposed`
  - current round에서는 사용하지 않는다.

따라서 current architecture에서 `internal_only`는 runtime availability 축이 아니라 consumer visibility 축이다. row 삭제나 bridge 누락은 publish 정책이 아니라 contract drift다.

### current operating authority

three-axis contract migration 이후 current operating authority는 다음 artifact들로 읽는다.

- `quality_baseline_v2_partial.json`
- `phase_d_reopen_iteration_report.json`
- `phase_d_opening_evidence.json`
- `phase3a_guardrail_seal.json`
- `quality_publish_decision_preview_summary.json`
- `quality_publish_decision_preview_validation_report.json`
- `quality_publish_lua_bridge_report.json`
- `quality_publish_runtime_report.json`
- `quality_baseline_v3.json`
- `in_game_validation_result.json`

current 핵심 수치는 다음처럼 고정됐다.

- full runtime quality snapshot: `strong 1316 / adequate 0 / weak 768`
- full runtime quality ratio: `0.6314779270633397`
- publish surface split: `internal_only 617 / exposed 1467`
- exposed quality ratio: `0.8970688479890934`
- `quality_publish_runtime_report`: pre-in-game runtime gate pass, artifact status = `ready_for_in_game_validation`
- `in_game_validation_result = pass`

즉, current architecture는 단순히 preview를 만든 상태가 아니라, **offline decision -> bridge/runtime wiring -> manual in-game validation** 까지 닫힌 상태다.

### runtime consumer와 인게임 검증 경계

current architecture에서 validator와 runtime consumer의 경계는 다음처럼 고정한다.

- validator는 offline contract drift만 본다.
- Browser/Wiki default surface가 실제로 `internal_only`를 숨기고 `exposed`를 렌더하는지는 Phase 6 manual in-game validation이 본다.
- current cycle의 manual validation은 `internal_only` suppression, `exposed` render, context menu, other layer, performance, loose ammo right-click path를 모두 pass로 닫았다.

이 경계는 중요하다. UI surface rendering 결과를 validator 책임으로 넣으면 ownership 층이 다시 섞이고, 반대로 manual validation을 생략하면 contract migration closeout이 incomplete가 된다.

### current 구조에서 남는 과제

현재 architecture 관점에서 남는 일은 다음 셋이다.

- `identity_fallback 617` source expansion과 net-new cluster 설계
- non-isolated lane quality improvement의 지속적 축적
- future `quality_exposed` round의 별도 설계

즉, 현재 구조 문제는 더 이상 `no_ui_exposure를 언제 해제할까`가 아니라, **이미 닫힌 three-axis contract 위에서 isolated inventory를 얼마나 줄이고 future quality surface를 언제 별도 round로 열 것인가**의 문제다.

---

## 2026-04-07 addendum — 공개 순서와 표면 구조 재정렬

### Pulse Core의 현재 외부 포지션

Pulse Core는 구조적으로는 여전히 플랫폼이지만, **현재 외부 포지션은 전면 공개 플랫폼이 아니라 내부 기반 허브**에 가깝다.

- 내부 구조: 계속 Hub & Spoke + SPI 플랫폼
- 현재 공개 포지션: spoke들을 받치는 내부 기반
- 향후 공개 방식: spoke들이 실제 수요를 만든 뒤 기반으로 드러나는 구조

즉, 이번 단계의 재해석은 `Pulse를 라이브러리로 격하`가 아니라, **플랫폼 개방 순서를 뒤로 미루는 것**에 가깝다.

### Pulse의 표면 다각화

Pulse의 채택 문제는 Core 내부 capability 부족보다, **외부에서 어떤 입구로 시작해야 하는지가 불명확한 문제**로 본다. 따라서 현재 구조에서는 기능 다각화보다 **표면 다각화**가 더 중요하다.

권장되는 표면 층은 최소한 다음 다섯 가지다.

- **Product surface**: Echo / Fuse 같은 실제 결과물 표면
- **Stable Core surface**: 기존 모더용의 작은 공식 코어 표면
- **Starter surface**: 바이브코딩 / 입문 사용자용 시작점
- **Guided surface**: 문서, 디렉팅, 프롬프트, 가이드 표면
- **Raw/Internal surface**: 내부 구현과 실험층

핵심은 **같은 Core를 다른 사용자 workflow에 맞는 서로 다른 입구로 보여주는 것**이며, 이 다층 표면은 Core 기능을 늘린다는 뜻이 아니다.

### workflow lane 기준의 채택 구조

현재 구조에서 타깃은 `기존 모더 vs 바이브코더` 같은 사람 분류보다, **Starter / Guided / Raw lane** 같은 workflow 단계로 잡는다.

- Starter lane: 입문 / 바이브코딩 / 낮은 진입 장벽
- Guided lane: 구조를 조금 이해한 사용자
- Raw lane: 기존 모더 / 고급 사용자

이는 Core 안에 helper를 넣는 구조가 아니라, **Core 밖의 표면 설계**로 채택률 병목을 줄이는 접근이다.

### Echo / Fuse / Nerve 경계 재확인

이번 세션 기준 구조 경계는 다음처럼 다시 고정된다.

- **Echo**: 계속 observer-only. 당분간 soft-freeze 상태가 맞으며, 정밀 profiling 확장은 실제 blind spot 확인 뒤에만 국소적으로 연다.
- **Fuse**: 자기 담당 영역(1/4/7) 안에서 더 다듬을 여지가 있는 안정화기다. 그러나 Area 9로 넘어가면 구조 경계를 침범한다.
- **Nerve**: launch 기준은 계속 100% Lua / Pulse 비의존 standalone 이다. Area 9는 멀티 성능 최적화가 아니라 **같은 틱에 Lua 자폭을 끊는 보험 장치**다.
- **Nerve+**: Pulse capability를 소비할 수 있는 후속 편의/확장 overlay는 여기서만 검토한다.

따라서 `Fuse가 Area 9를 맡는다`는 경로는 구조적으로 닫히고, `Pulse capability -> Nerve+`만 장기 보조 경로로 남는다.

### Iris의 현재 제품 범위

현재 구조에서 Iris 첫 공개 범위는 **DVF + Tooltip** 의 vanilla-first 본체 검증으로 본다.

- 모드 시장 확장 시스템은 현재 architecture의 launch scope에 포함하지 않는다.
- 이유는 외부 모드 호환 요구가 초기 제품 피드백을 오염시키지 않게 하기 위해서다.
- 따라서 첫 공개의 핵심은 `Iris가 얼마나 많은 외부 모드를 덮느냐`가 아니라, **Iris 본체가 실제로 유의미한 위키 표면인가**를 검증하는 데 있다.

### B42 대응 구조

현재 architecture에서 B42 대응은 **즉시 메인라인 전환**이 아니라, 점진적 **포트 브랜치 준비**에 가깝다.

- Pulse → Echo/Fuse → Nerve 축은 구조 충돌 가능성이 상대적으로 큰 축
- Iris는 tooltip / menu / browser 같은 표면 충돌 가능성이 상대적으로 큰 축
- 따라서 현 단계의 대응은 `전체 개발축 교체`가 아니라 **표면 우선 점검 + 별도 포트 작업**으로 읽는다.
---

# 3. 2026-04-07 Addendum — Pulse 개방 순서 역전과 spoke-led demand 구조

## Pulse의 현재 전략적 위치

Pulse의 현재 위치는 `공개 플랫폼`과 `단순 라이브러리`의 중간이 아니라, **내부적으로는 플랫폼을 유지하되 외부 개방 순서를 뒤집은 허브**에 가깝다.

- 내부 구조: 계속 플랫폼
- 외부 공개: spoke 수요 형성 뒤
- 구조 원칙: Hub & Spoke + SPI 유지
- 의미: `플랫폼 포기`가 아니라 **플랫폼 개방 순서 역전**

즉, Stage B / 외부 모드 로딩은 구조상 폐기되지 않았지만, 현재 아키텍처 서술에서는 이를 **즉시 공개 기능**이 아니라 **수요 개시형 후속 게이트**로 읽는다.

## spoke-led demand 구조

현재 Pulse 생태계의 채택 구조는 `플랫폼이 먼저 수요를 만들고 spoke가 따라오는 구조`보다, **spoke가 먼저 수요를 만들고 Pulse가 그 위에서 기반으로 드러나는 구조**에 가깝다.

- Echo: 기술 모더 / 진단 수요
- Frame: 팩 관리자 / 운영 수요
- Canvas: 리소스 제작자 / 적용 상태 검증 수요

핵심은 외부 모더가 `Pulse라는 플랫폼 선언` 때문에 들어오는 것이 아니라, **Pulse 위에서 이미 돌고 있는 작업 흐름** 때문에 들어오게 만드는 것이다.

## public surface diversification

같은 Core를 하나의 얼굴로만 보여주지 않는 구조를 architecture 차원에서 인정한다. 이는 Core 기능 확장이 아니라 **공개 표면 다각화**다.

- **Product surface**: Echo, Fuse, Iris 같은 결과물 중심 표면
- **Stable Core surface**: 기존 모더용 작은 공식 surface
- **Starter surface**: 입문/바이브코딩용 시작점
- **Guided surface**: 문서, 디렉팅, 프롬프트, 가이드
- **Raw/Internal surface**: 내부 구현과 실험층

이 표면 분리는 helper를 Core에 넣는 방식이 아니라, **같은 Core를 서로 다른 workflow 입구로 번역하는 방식**이다.

## workflow lane 기준의 채택 구조 재강화

사람 분류보다 **Starter / Guided / Raw lane** 이라는 workflow 기준을 더 강하게 채택 구조로 본다.

- Starter lane: 낮은 진입 장벽 / 바이브코딩 / 입문
- Guided lane: 구조 이해가 약간 필요한 사용자
- Raw lane: 기존 모더 / 고급 사용자

이는 Pulse를 `누구를 위한 플랫폼인가`보다, **어떤 workflow에서 어떻게 들어오는가**로 설명해야 한다는 뜻이다.

## 공개 이벤트보다 순차적 의미 확장

Pulse는 `Pulse + Frame + Canvas`를 한 번에 전면 공개하는 구조보다, **spoke들이 순차적으로 Pulse의 의미를 넓혀가는 구조**가 더 적합하다.

- 한 번의 대형 데뷔보다
- spoke별 실사용 가치가 먼저 쌓이고
- 그 뒤에 Pulse의 존재가 공통 기반으로 더 분명해지는 방식

따라서 architecture 상 공개 전략도 `결과물 선공개 -> 기반 후노출`을 유지하되, 후노출의 방식은 **일회성 공개 이벤트보다 누적적 의미 확장**에 가깝다.

## Iris의 경쟁 리스크 재해석

현재 architecture에서 Iris의 경쟁 리스크는 기능 부재보다 **인지와 포지셔닝 문제**로 읽는다.

- Iris는 이미 상당수 실용 상호작용/재료 추적 기능을 가지고 있다.
- 따라서 위협은 “없어서 진다”보다 **있는데 그렇게 인식되지 못할 수 있다**는 데 있다.

이 해석은 Iris의 구조 자체를 바꾸는 것이 아니라, 앞으로의 product surface와 설명 설계가 **위키 + 즉시 추적 도구** 양쪽 정체성을 더 선명히 드러내야 함을 뜻한다.

---

## 11-42. Iris DVF 3-3 surface contract authority migration splits advisory sensing from structural contract input

2026-04-08 기준 current DVF 3-3 구조는 `style surface cleanup` 라운드가 아니라, **default surface exposure authority를 single-writer decision stage 안으로 옮겨 적는 라운드**로 읽는다.

핵심 분리는 다음과 같다.

- advisory sensor branch
  - style linter
  - non-writer
  - build/output authority 없음
- structural contract sensor branch
  - `layer3_structural_audit.py`
  - 출력: `surface_contract_signal.jsonl`
  - non-writer
- single writer
  - `quality/publish decision stage`
  - 입력: active quality audit + publish policy + structural contract recommendation
  - 출력: `quality_state`, `publish_state`

current pipeline은 아래처럼 읽는다.

- `facts -> decisions -> body-role overlay -> compose(internal repair + diagnostic quality_flag capture) -> normalizer`
- advisory sensor branch: `style linter`
- structural contract branch: `surface_contract_signal.jsonl`
- single writer: `quality/publish decision stage`
- downstream: `publish decision preview -> Lua bridge -> Browser/Wiki default consumer`

### pre-render contract candidate 주석

current implementation에서 structural audit는 역사적 파일명상 `*.rendered.json` 후보를 읽지만, 구조적 위치는 **final publish decision 이후 rendered artifact** 가 아니라 **decision stage 이전 pre-render contract candidate** 다.  
즉, 파일명과 authority 위치를 같은 것으로 읽지 않는다.

### ownership boundary

- style linter는 advisory-only다.
- structural audit는 `recommended_tier` recommendation만 만든다.
- `recommended_tier`는 direct write instruction이 아니다.
- `structural_flag`는 preview/report-only meta다.
- Lua bridge와 runtime consumer는 이미 계산된 `publish_state`만 소비한다.

### current round snapshot

- publish surface split: `internal_only 617 / exposed 1467`
- structural contract snapshot: `BODY_LACKS_ITEM_SPECIFIC_USE 617`, residual `FUNCTION_NARROW 7`, `hard_fail 0`
- authority migration round는 **publish split을 바꾸지 않고 authority ownership만 명문화한 상태**로 baseline v4에 동결됐다.

### follow-up handoff artifact

- `identity_fallback_source_expansion_backlog.json`은 current contract round를 다시 여는 artifact가 아니라, **next source expansion round용 canonical handoff input** 이다.
- 이 artifact는 legacy `identity_fallback_expansion_plan.json`을 current `quality_baseline_v4`, `quality_publish_decision_preview`, `identity_fallback_policy_isolation_report`와 다시 정렬한 read-only follow-up inventory다.
- current handoff alignment는 `plan 617 / policy isolation 617 / preview identity_fallback 617`이며, bucket split은 `11 / 599 / 7`로 유지된다.
- `role_fallback_hollow_source_expansion_backlog.json`도 같은 성격의 follow-up input이다.
- current compose-v2 handoff alignment는 `preview role_fallback 37 / BODY_LOSES_ITEM_CENTRICITY 37 / shim-applied 37`이며, split은 `identity_use_collapse_only 26 / identity_use_collapse_plus_context_gap 11`이다.
- follow-up split artifact `role_fallback_hollow_followup_split.json`은 이 lane를 `existing_cluster_reuse 20 / policy_revisit 2 / net_new_source_expansion 15`로 다시 나눈다.
- 위 세 artifact는 **planning baseline** 이고, current-state aggregate는 아니다. current-state consumer는 후행 `terminal_status` / `terminal_handoff`를 읽는다.
- 현재 deterministic reusable cluster는 `C1-B.container_storage 20`뿐이며, 나머지는 policy review 또는 net-new source work로 남는다.
- execution-input artifact `role_fallback_hollow_reuse_candidate_facts.jsonl`은 재사용 후보 20건을 `cluster_summary` candidate facts로 정렬해 두고, `role_fallback_hollow_policy_revisit_inventory.json`은 policy revisit 2건을 별도 review lane으로 유지한다.
- package-level handoff는 `role_fallback_hollow_c1b_reuse_package/`와 `role_fallback_hollow_policy_review/`에 각각 정리되며, 전자는 candidate facts와 decision proposal을, 후자는 review rows와 note를 담는다.
- `role_fallback_hollow_c1b_reuse_promotion_preview/` dry-run은 이 20건이 current v2 contract 기준에서 `weak/internal_only -> strong/exposed`로 전량 회복됨을 보여준다.
- `role_fallback_hollow_residual_after_c1b_reuse.json`은 이 20건이 실제로 소비된 뒤 residual debt가 정확히 `17`로 줄고, 구성이 `policy_revisit 2 / net_new_source_expansion 15`로 닫힌다는 점을 고정한다.
- `role_fallback_hollow_net_new_package/`는 residual 17 중 net-new lane 15건만 따로 떼어 둔 execution input이며, 현재 split은 `material_body 9 / tool_body 6`이다.
- `role_fallback_hollow_net_new_work_packages.json`은 이 net-new 15건을 다시 deterministic recovery-axis 기준으로 `C1-F tool_use_recovery 6 / C1-G material_context_recovery 9`로 쪼갠 planning artifact다.
- `role_fallback_hollow_policy_review/role_fallback_hollow_policy_review_memo.json`은 policy-excluded evidence 2건을 net-new lane과 섞지 않고 review question 단위로 유지하는 결정 입력이다.
- `role_fallback_hollow_followup_runbook.json`은 이 전체 lane의 소비 순서를 `existing_cluster_reuse 20 -> policy_revisit 2 -> net_new_source_expansion 15`로 고정하는 sequencing artifact다.
- `staging/source_coverage/block_c/role_fallback_hollow_seed_package_index.json`은 마지막 net-new lane를 실제 source-expansion seed package인 `C1-F`와 `C1-G`로 materialize한 handoff index다.
- `c1f_tool_use_recovery_package/`와 `c1g_material_context_recovery_package/`는 seed facts, source.raw seed, recovery requirements, smoke sample을 포함하지만 아직 cluster/compose decision은 갖지 않는다.
- `role_fallback_hollow_local_evidence_index.json`은 이 seed package들을 다시 로컬 repo signal 기준으로 sweep한 pre-authoring evidence index다.
- `role_fallback_hollow_manual_second_pass_upgrades.json`은 broader repo search로 `manual 8` 중 `5`건을 targeted lane로 승격하고 `3`건만 manual로 남긴 second-pass triage artifact다.
- `role_fallback_hollow_source_authoring_queue.json`은 현재 evidence sweep + second-pass upgrade 결과를 `targeted_source_writeup_now 12 / manual_repo_search_first 3`으로 묶은 착수 우선순위 artifact다.
- `role_fallback_hollow_targeted_authoring_pack.json`은 targeted 12건에 대해 high-signal evidence만 남긴 immediate authoring input이며, 이 중 `7`건은 local evidence, `5`건은 manual second-pass upgrade에서 왔다.
- `role_fallback_hollow_targeted_authoring_drafts_index.json`은 targeted 12건을 실제 초안 facts/review bundle로 옮긴 authoring 결과 묶음이다.
- `role_fallback_hollow_targeted_source_promotion_drafts_index.json`은 이 초안을 seed-only `source.raw`에 반영할 수 있는 promotion candidate로 다시 포장한 마지막 draft 단계다.
- `role_fallback_hollow_manual_search_pack.json`은 남은 manual 3건에 대해 deterministic query anchor와 top path를 묶어 둔 broader-search handoff다.
- `role_fallback_hollow_manual_residual_blocker_memo.json`은 final non-translation repo sweep 뒤에도 item-specific action/build evidence가 확인되지 않은 manual 3건을 `parked_pending_new_source_discovery` 상태로 고정한 blocker memo다.
- `role_fallback_hollow_targeted_source_merge_previews_index.json`은 promotion candidate 12건을 seed `source.raw` 위에 병합한 preview와 기계 검증 결과를 담는 마지막 review gate다.
- `role_fallback_hollow_targeted_source_authority_candidates_index.json`은 그 preview를 package-level authority candidate로 고정한 artifact이며, 현재 aggregate 상태는 `promotion_ready_authority_candidate 12 / parked_pending_new_source_discovery 3`이다.
- `role_fallback_hollow_source_replacement_candidates_index.json`은 authority candidate를 exact package-level `source.raw` replacement snapshot으로 다시 포장한 final handoff artifact이며, 현재 aggregate 상태는 `ready 12 / carry_forward_parked 3`이다.
- `role_fallback_hollow_source_replacement_delta_review_index.json`은 seed `source.raw`와 replacement candidate의 차이를 authorization review용으로 요약한 artifact이며, 현재 aggregate delta는 `semantic_upgrade 12 / parked_metadata_carry_forward 3`이다.
- `role_fallback_hollow_source_promotion_manifest.json`은 마지막으로 package별 적용 대상과 parked carry-forward 대상을 분리한 promotion handoff manifest이며, 현재 aggregate action은 `apply_ready_replacement 12 / carry_forward_parked 3`이다.
- `role_fallback_hollow_source_promotion_applied.json`은 reviewed replacement candidate를 실제 package `source.raw`에 반영한 apply log이며, post-apply parity를 SHA 기준으로 검증한다.
- `role_fallback_hollow_policy_resolution_packet.json`은 남은 `policy_review_pending 2`에 encoded use-case policy rule과 phase-C confirmed-excluded precedent를 붙인 review-ready handoff artifact이며, 현재 default resolution은 `maintain_exclusion 2`다.
- `role_fallback_hollow_policy_outcome_projection.json`은 그 handoff를 두 branch로 다시 고정한 planning artifact이며, recommended branch는 `maintain_exclusion_confirmed`, alternate explicit override branch는 `C1-G reopen 2`다.
- `role_fallback_hollow_post_block_c_apply_status.json`은 `residual_after_c1b_reuse 17`을 기준으로 block_c promotion 적용 뒤의 follow-up status를 다시 읽은 artifact이며, 현재 split은 `block_c_source_promoted 12 / parked_pending_new_source_discovery 3 / policy_review_pending 2`, attached policy handoff는 `maintain_exclusion 2 / historical precedent attached 2`다.
- `role_fallback_hollow_followup_runbook.json`의 step `2`는 이제 memo-only gate가 아니라 `policy_outcome_projection`을 입력으로 읽으며, `default_confirmed -> remaining unresolved 3`, `override -> reopen 2`를 동시에 들고 간다.
- `role_fallback_hollow_policy_default_closeout.json`은 recommended branch를 실제 closeout handoff로 확정한 artifact이며, `policy_review_closed_maintain_exclusion 2`를 기록하되 runtime delta는 계속 `0`으로 유지한다.
- `role_fallback_hollow_post_policy_default_closeout_status.json`은 그 closeout branch를 current post-block-c status 위에 적용한 status snapshot이며, current closeout split은 `block_c_source_promoted 12 / policy_review_closed_maintain_exclusion 2 / parked_pending_new_source_discovery 3`이다.
- `role_fallback_hollow_residual_tail_handoff.json`은 그 status snapshot에서 parked `3`만 다시 추출한 final carry-forward packet이며, split은 `C1-F 1 / C1-G 2`, reopen gate는 `non_translation item-specific requirement 발견 시에만 재개방`으로 고정된다.
- `role_fallback_hollow_residual_tail_source_discovery_round.json`은 그 tail을 future round 실행 입력으로 다시 묶은 artifact이며, execution order는 `C1-F 1 -> C1-G 2`, 모든 package는 `reopen gate 통과 전까지 runtime/source 동결` 원칙을 공유한다.
- `role_fallback_hollow_residual_tail_source_discovery_status.json`은 그 future round 안에서 현재까지 실행된 local discovery progress를 기록하는 non-mutating status artifact이며, 현재 상태는 `executed_remain_parked 3 / reopen_ready 0 / pending_execution 0`이다.
- `c1-f_residual_tail_discovery_pass.json`은 first-pass execution artifact로서 `camping.SteelAndFlint`에 generic StartFire context와 translation token은 남아 있지만, non-translation item-specific requirement가 없어 reopen gate를 통과하지 못했다는 점을 고정한다.
- `c1-g_residual_tail_discovery_pass.json`은 second-pass execution artifact로서 `Base.ConcretePowder`, `Base.Yarn` 모두 선언/분포 및 주변 concrete-sewing 맥락만 남아 있을 뿐 direct non-translation requirement가 없어 reopen gate를 통과하지 못했다는 점을 고정한다.
- `role_fallback_hollow_residual_tail_round_closeout.json`은 두 package 실행이 모두 끝난 뒤 tail round를 봉인하는 closeout artifact이며, `round_execution_complete = true`, `carry_forward_hold_count = 3`, `next_lane = future_new_source_discovery_hold`를 고정한다.
- `role_fallback_hollow_terminal_status.json`은 `residual_after_c1b_reuse 17` baseline 전체를 다시 합친 terminal snapshot이며, 현재 evidence round 기준 aggregate는 `block_c_source_promoted 12 / policy_review_closed_maintain_exclusion 2 / carry_forward_hold 3 / active_unresolved_count 0`이다.
- `role_fallback_hollow_terminal_handoff.json`은 최초 follow-up split `37` 전체를 current-state accounting으로 다시 닫은 condensed handoff artifact이며, 현재 aggregate는 `existing_cluster_reuse_preview_backed 20 / block_c_source_promoted 12 / policy_review_closed_maintain_exclusion 2 / carry_forward_hold 3`, runtime snapshot은 `2105`행으로 유지된다.
- `role_fallback_hollow_post_apply_preview_index.json`은 promoted `12`를 ready-only preview chain으로 다시 태워 parked `3`을 격리한 뒤, `direct_use 12/12`, `special_context 11/11`, `unexpected legacy hard fail 0`을 package gate로 확인한 downstream handoff artifact다.
- `post_c_projection_summary.json`은 이 ready-only replacement lane를 staged `C` additive projection 위에 다시 얹어, runtime row count를 늘리지 않은 채 `role_fallback -12 / direct_use +12` delta를 반영한 remeasurement artifact다.
- `source_coverage_runtime_summary.json`은 additive package merge 뒤 `C1-F/C1-G` replacement rows를 historical runtime에 deterministic replace로 적용한 integrated runtime artifact이며, 현재 path counts는 `cluster_summary 1275 / identity_fallback 718 / role_fallback 100 / direct_use 12`다.
- 따라서 후속 source expansion round는 old `phase1_parallel` plan 재해석이 아니라 current `phaseE` handoff artifact 기준으로 이어진다.
- companion walkthrough는 `docs/iris-dvf-3-3-surface-contract-authority-migration-walkthrough.md`다.

## 11-43. Iris DVF 3-3 acquisition lexical authority and body-role lexical cleanup are build-time authority branches, not runtime language systems

2026-04-09 기준 current Korean surface hardening은 `compose 이후 runtime에서 문장을 고치는 구조`가 아니라, **build-time authority branch에서 facts/rendered/runtime export를 다시 생성하는 구조**로 닫힌다. 이 round는 한국어 엔진 도입이 아니라 offline lexical authority 경로의 명문화다.

### 현재 구조의 두 lexical branch

current sprint7 authority 기준 lexical hardening branch는 아래 둘로 분리된다.

1. acquisition lexical branch
   - 책임:
     - acquisition translationese naturalization
     - canonical/semantic acquisition surface draft
     - `acquisition_null_reason` 구조화와 validator alignment
   - 대표 구현 경로:
     - `acquisition_lexical_utils.py`
     - `build_acquisition_facts_semantic_draft.py`
     - acquisition validator / promotion bundle / authority reflection scripts
2. body-role lexical cleanup branch
   - 책임:
     - body generic fallback hardening
     - translationese work-context cleanup
     - user-facing family override
   - 대표 구현 경로:
     - `body_role_lexical_cleanup.py`
     - `build_body_role_lexical_cleanup_authority.py`

핵심은 둘 다 **offline writer branch** 라는 점이다. compose/runtime consumer는 이 문구를 즉석 보정하지 않는다.

### current pipeline 위치

current authority path는 아래처럼 읽는다.

- `facts -> decisions -> body-role overlay -> compose -> rendered candidate`
- lexical authority branch A: `acquisition semantic draft / null-reason alignment`
- lexical authority branch B: `body-role lexical cleanup`
- `sprint7 authority promotion -> rendered authority -> Lua bridge export -> runtime reflection -> manual in-game validation`

여기서 중요한 점은 다음 넷이다.

1. lexical cleanup은 compose 외부 repair/re-compose stage가 아니다.
2. lexical cleanup은 runtime Lua 소비 단계가 아니라 **authority artifact 갱신 단계**다.
3. validator와 preview diff가 먼저 닫힌 뒤에만 runtime reflection으로 간다.
4. deployed runtime은 staged authority Lua와 같아야 한다.

### ownership boundary

- writer
  - acquisition semantic draft / lexical helper branch
  - body-role lexical cleanup branch
  - sprint7 authority promotion
- checker
  - validator
  - preview diff / regression reports
  - runtime reflection hash check
- non-writer consumer
  - Lua bridge consumer
  - Browser/Wiki/context-menu surface

즉, current Korean surface 문제는 validator가 고치지 않고, runtime consumer도 고치지 않는다. 오직 offline authority writer branch만 수정 권한을 가진다.

### current user-facing contract examples

current lexical authority는 추상 작업 맥락보다 item-native / effect-first phrasing을 우선한다. 현재 고정된 family 예시는 아래와 같다.

- 보호 기능 착용 아이템
  - `착용 시 (부위)를 보호할 수 있다.`
- 화기 identity
  - `근접 무기` generic fallback 대신 `소총`, `산탄총` 같은 실제 계열 identity
- 식품 generic body
  - 기능 절차보다 효과 중심 phrasing
- 가방 family
  - generic backpack surface + `학생 가방` 별도 override
- acquisition discovery/location phrasing
  - `보관 장소`, `취급 장소`, `작업 장소`, `작업 구역`, `판매 장소`, `작업 차량` 같은 번역투 compound 제거

이 예시는 architecture 차원에서 `무슨 문장을 쓰느냐`의 취향 문제가 아니라, **current writer branch가 어떤 종류의 surface drift를 regressions로 보는가**를 뜻한다.

### current authority snapshot

current sprint7 authority snapshot은 아래처럼 읽는다.

- acquisition/decisions promotion patch
  - facts `1050`
  - decisions `1055`
- authority preview gate
  - `unexpected_rendered_changed_count = 0`
  - `introduced_rendered_hard_fail_count = 0`
- runtime reflection
  - deployed `IrisLayer3Data.lua`와 staged Lua hash 일치

즉, current 구조는 lexical cleanup이 로컬 preview 실험이 아니라 **preview authority -> deployed runtime reflection** 까지 닫힌 상태다.

### current 남은 구조 과제

현재 architecture 관점에서 남은 것은 새 한국어 엔진 설계가 아니다.

- manual in-game validation을 통해 consumer surface가 staged authority와 실제로 같은지 계속 확인
- user validation에서 나온 residual surface drift를 같은 offline lexical branch에서만 보수적으로 수정
- active/silent, publish_state, compose external repair 같은 별도 구조 라운드는 다시 열지 않기

따라서 current Korean surface round는 `언어 처리 시스템 개발`이 아니라, **닫힌 three-axis/runtime architecture 위에서 lexical authority branch를 안전하게 운영하는 post-closeout hardening phase** 로 읽는다.

## 11-44. Iris DVF 3-3 identity_fallback source expansion current closeout is bounded by the frozen A-4-1 cluster budget

2026-04-15 기준 current `identity_fallback` source expansion authority는 `617 전체를 한 번에 소거하는 무한 실행 큐`가 아니라, **frozen interaction-cluster budget 안에서 executable subset을 실제로 승격시키고 residual inventory를 다시 고정한 closeout 상태** 로 읽는다.

### current authoritative read points

current-state consumer는 아래 artifact를 우선 읽는다.

- `staging/identity_fallback_source_expansion/phase6_subset_rollout/exec_subset_600_wrench_crowbar_b7_b8_b9/subset_distribution_remeasurement.json`
- `staging/identity_fallback_source_expansion/phase6_subset_rollout/exec_subset_600_wrench_crowbar_b7_b8_b9/subset_rollout_report.json`
- `staging/identity_fallback_source_expansion/phase3_taxonomy_manifest/phase3_residual_taxonomy_manifest.json`
- `staging/identity_fallback_source_expansion/phase3_taxonomy_manifest/phase3_residual_taxonomy_alignment_report.json`

이 snapshot 기준 current aggregate는 아래처럼 읽는다.

- promoted executable subset: `600`
- current runtime path counts: `cluster_summary 2040 / identity_fallback 17 / role_fallback 48`
- current publish split: `internal_only 617 / exposed 1467`
- current residual split: `phase3_taxonomy_pending 10 / bucket_3_scope_hold 7`

즉, architecture 차원에서 current `identity_fallback` lane는 사라진 것이 아니라 `17`행의 residual inventory와 `internal_only` publish contract 안에서 계속 계상된다.

### cluster budget boundary

current interaction-cluster architecture는 여전히 `A-4-1` 정의를 따른다.

- cluster는 3-3 대표 작업 맥락 요약층이다.
- `cluster_count_limit = 30`은 current seed validator가 직접 강제한다.
- `30`을 초과하면 `granularity 기준이 잘못된 것으로 보고 A-4-1을 재작업한다`는 전제가 살아 있다.

따라서 current `30 / 30` 상태는 **same-cycle terminal budget edge** 다.  
이 상태에서 `31번째 cluster`를 추가하는 것은 source expansion round의 자연스러운 연장이 아니라, **interaction-cluster taxonomy와 granularity 기준을 다시 여는 별도 설계 행위** 로 읽는다.

### what the remaining residual means

현재 residual `17`은 동일한 종류의 debt가 아니다.

- `phase3_taxonomy_pending 10`
  - current budget 아래에서 아직 canonical path가 닫히지 않은 residual
  - `Rope`, `WateredCan`, `ClubHammer`, `WoodenMallet`, `Sledgehammer`, `Sledgehammer2`, `Katana`, `LeadPipe`, `Nightstick`, `HandScythe`
- `bucket_3_scope_hold 7`
  - current source expansion round 바깥의 scope-hold residual

이 residual은 `same-session execution backlog`가 아니라, **다음 round에서 어떤 governance 경로를 택할지 결정해야 하는 inventory** 다.

### follow-up branch separation

current architecture에서 후속 분기는 둘로만 읽는다.

1. frozen-budget residual round
   - current `cluster_count_limit = 30`을 유지한다.
   - 후속 작업은 `existing-cluster absorption`, 제한적 `direct_use`, `carry_forward_hold` 같은 경로만 다룬다.
   - current closeout baseline `600 / 17`을 새 round opening baseline으로 사용한다.

2. separate A-4-1 rework round
   - cluster taxonomy와 budget 자체를 다시 연다.
   - 이 경우 source expansion round의 same-cycle continuation이 아니라, interaction cluster 설계를 다시 검증하는 별도 round가 된다.

current authority path는 첫 번째 branch를 기본으로 둔다. 즉, **current source expansion cycle 안에서는 cluster budget을 더 열지 않고, next work는 새 round opening으로만 이어진다.**

## 11-45. Iris DVF 3-3 identity_fallback residual round closeout 이후 current architecture는 `phase3_taxonomy_pending 0 + frozen hold 11` 상태로 읽는다

2026-04-16 기준 current `identity_fallback` residual round authority는 planning 문서가 아니라 실제 closeout artifact까지 생성된 상태다.

### current post-closeout read points

current-state consumer는 아래 artifact를 우선 읽는다.

- `staging/identity_fallback_source_expansion/residual_round/residual_round_manifest.json`
- `staging/identity_fallback_source_expansion/residual_round/residual_round_status.md`
- `staging/identity_fallback_source_expansion/residual_round/closeout/residual_round_closeout_report.json`
- `staging/identity_fallback_source_expansion/residual_round/closeout/residual_round_closeout_note.md`
- `staging/identity_fallback_source_expansion/residual_round/closeout/residual_round_post_closeout_branch_decision.json`

이 snapshot 기준 current aggregate는 아래처럼 읽는다.

- residual round closing split: `absorption 2 / direct_use 4 / carry_forward_hold 4`
- in-scope residual after closeout: `phase3_taxonomy_pending 0`
- frozen hold accounting after closeout: `carry_forward_hold 4 + bucket_3_scope_hold 7 = 11`
- cluster budget: `30 / 30` 유지
- runtime path / publish split: 이번 round에서 무변경

즉 architecture 차원에서 current 상태는 `downstream validation ready`가 아니라, **in-scope governance closeout complete + frozen-budget hold retained** 로 읽는다.

### branch semantics after closeout

current closeout 이후 분기는 셋이 아니라 사실상 하나의 기본 branch와 두 개의 reopen gate로 정리된다.

- 기본 branch
  - `maintain_frozen_budget_hold`
  - `carry_forward_hold 4`는 unfinished execution queue가 아니라 governance hold다.
  - `bucket_3_scope_hold 7`은 계속 execution scope 밖에 둔다.

- reopen gate 1
  - `future_new_source_discovery_hold`
  - item-specific evidence가 추가로 발견된 경우에만 reopen한다.

- reopen gate 2
  - `A-4-1 rework / cluster budget`
  - current `30-cap` 자체를 다시 열어야 한다고 판단될 때만 연다.

따라서 current architecture는 `phase3_taxonomy_pending`이 `0`이 되었다는 이유만으로 자동으로 publish/runtime/in-game downstream lane으로 넘어가지 않는다. carry-forward hold가 남아 있는 동안 current branch는 **hold-maintained closeout state** 다.

## 11-46. Iris DVF 3-3 identity_fallback closure policy expansion은 taxonomy reopen이 아니라 closure admissibility boundary 조정이다

2026-04-16 기준 current architecture는 `maintain_frozen_budget_hold` 상태로 닫혀 있지만, carry-forward hold의 일부는 taxonomy absence보다 **closure admissibility boundary** 문제로 해석된다.

### direct_use is a non-cluster closure path

current architecture에서 `direct_use`는 더 이상 weapon-only 운영 관행으로 묶지 않는다. future policy round에서는 아래 조건을 모두 만족하면 `direct_use`를 non-cluster closure path로 사용할 수 있다.

- item-specific evidence `2`개 이상
- 같은 대표 작업 맥락으로 수렴
- one-sentence 3-3 body closure 가능
- downstream validation 불요구

즉 `direct_use`는 cluster taxonomy의 failure fallback이 아니라, **cluster를 열지 않고도 닫을 수 있는 item-specific closure lane** 이다.

### dominant / dual-context boundary is structural, not stylistic

다기능 item을 닫을 때 current architecture는 "문장이 자연스러운가"를 기준으로 삼지 않는다. 허용 기준은 아래 둘뿐이다.

- dominant-context
  - 주 맥락이 명확하고 부 맥락이 종속적이면 주 맥락으로 닫는다
- structural dual-context convergence
  - `compose_profile`과 `slot_sequence`가 두 맥락을 같은 대표 작업 맥락 안에서 구조적으로 수용할 때만 허용한다

따라서 `WateredCan`과 `HandScythe`의 future reopen은 style judgement가 아니라 **structure-level admissibility check** 로만 읽는다.

### declared chain vs derived interpretation

current architecture는 declared transform/build chain과 derived utility interpretation을 분리한다.

- 허용
  - recipe transform fact
  - build requirement fact
  - 짧고 deterministic한 declared transform/build chain
- 금지
  - chain 전체를 최종 용도로 해석하는 것
  - `Rope -> escape tool` 같은 derived utility interpretation

즉 `Rope`는 future policy round에서 "결속/건설 재료" 수준으로는 닫을 수 있지만, current architecture는 여전히 declared fact boundary를 넘는 semantic leap를 금지한다.

### sequencing principle

future reopen 순서는 아래처럼 고정한다.

1. closure policy widening
2. 그래도 canonical close 불가 시 `A-4-1 rework / cluster budget`

이 순서는 current architecture가 `31번째 cluster`를 먼저 여는 대신 **policy boundary와 taxonomy boundary를 분리해 판단** 하도록 강제한다.

## 11-47. Iris DVF 3-3 identity_fallback closure policy round closeout 이후 current architecture는 `policy_resolved_scope_hold_only` 상태다

2026-04-16 기준 separate closure policy round까지 닫힌 current architecture는 더 이상 `carry_forward_hold 4`를 active unresolved hold로 읽지 않는다.

### current post-policy-round read points

current-state consumer는 아래 artifact를 우선 읽는다.

- `staging/identity_fallback_source_expansion/closure_policy_round/closure_policy_round_manifest.json`
- `staging/identity_fallback_source_expansion/closure_policy_round/closure_policy_round_status.md`
- `staging/identity_fallback_source_expansion/closure_policy_round/closeout/closure_policy_round_closeout_report.json`

이 snapshot 기준 current aggregate는 아래처럼 읽는다.

- policy scope closing split: `direct_use 4 / carry_forward_hold 0`
- selected branch after policy round: `policy_resolved_scope_hold_only`
- remaining sealed hold: `bucket_3_scope_hold 7`
- runtime path counts: 이번 round에서 무변경
- publish split: 이번 round에서 무변경

즉 current architecture에서 `identity_fallback` residual의 unresolved active hold는 사라졌고, 남은 것은 **scope-policy hold only** 다.

### what changed and what did not

바뀐 것:

- `Sledgehammer`, `Sledgehammer2`, `Rope`, `WateredCan`은 expanded closure policy 아래 policy-level `direct_use`로 닫혔다
- carry-forward hold는 active execution queue가 아니라 resolved policy queue로 전환됐다

바뀌지 않은 것:

- cluster taxonomy
- runtime path counts
- publish split
- `bucket_3_scope_hold 7`

따라서 current architecture는 `runtime adopted 4 more rows`가 아니라, **policy authority now knows how these 4 rows should close if later adopted** 라고 읽어야 한다.

## 11-48. Iris DVF 3-3 identity_fallback current-state consumer는 terminal snapshot을 읽고, immediate next round는 계획하지 않는다

2026-04-16 기준 current architecture에서 `identity_fallback` lane는 separate residual round와 closure policy round를 모두 거친 뒤 **terminal snapshot consumer model** 로 전환됐다.

### current terminal read points

current-state consumer는 아래 artifact를 canonical read point로 사용한다.

- `staging/identity_fallback_source_expansion/identity_fallback_terminal_status.json`
- `staging/identity_fallback_source_expansion/identity_fallback_terminal_status.md`
- `staging/identity_fallback_source_expansion/identity_fallback_terminal_handoff.json`
- `staging/identity_fallback_source_expansion/identity_fallback_terminal_handoff.md`

이 snapshot 기준 current aggregate는 아래처럼 읽는다.

- terminalized lineage total: `17`
- final status counts: `existing_cluster_absorption 2 / direct_use 8 / policy_review_closed_maintain_identity_fallback_isolation 7`
- active execution lane count: `0`
- selected branch: `maintain_identity_fallback_isolation_confirmed`
- no immediate next round planned: `true`
- runtime path counts: `cluster_summary 2040 / identity_fallback 17 / role_fallback 48`

### round artifacts remain provenance, not the first consumer surface

`residual_round_manifest.json`과 `closure_policy_round_manifest.json`은 current architecture에서 계속 필요한 provenance artifact다. 다만 이 둘은 **how we got here** 를 설명하는 round authority이지, current-state consumer가 첫 번째로 읽어야 하는 aggregate snapshot은 아니다.

즉 current architecture는 이제 아래처럼 분리해서 읽는다.

- round authority
  - residual round closeout / branch decision
  - closure policy round closeout
- current-state consumer surface
  - terminal status / terminal handoff

### future reopen boundary

current architecture는 immediate next round를 계획하지 않는다. future reopen은 아래 둘 중 하나가 explicit하게 열릴 때만 시작한다.

- `scope_policy_override_round`
- `runtime_adoption_round`

따라서 current lane는 `unfinished execution`이 아니라, **terminalized governance state with no remaining hold** 로 읽어야 한다.

## 11-49. Iris DVF 3-3 identity_fallback scope policy round closeout 이후 current architecture는 unresolved hold 없이 fully terminalized 상태다

2026-04-16 기준 separate scope policy round까지 닫힌 current architecture는 더 이상 `bucket_3_scope_hold 7`을 remaining hold로 읽지 않는다.

### current scope-policy-round read points

current-state consumer는 아래 artifact를 provenance로 함께 참조한다.

- `staging/identity_fallback_source_expansion/scope_policy_round/scope_policy_round_manifest.json`
- `staging/identity_fallback_source_expansion/scope_policy_round/scope_policy_round_status.md`
- `staging/identity_fallback_source_expansion/scope_policy_round/closeout/scope_policy_round_closeout_report.json`

이 closeout 기준 current aggregate는 아래처럼 읽는다.

- scope policy closing split: `policy_review_closed_maintain_identity_fallback_isolation 7 / hold 0`
- selected branch after scope policy round: `maintain_identity_fallback_isolation_confirmed`
- runtime path counts: 이번 round에서 무변경
- publish split: 이번 round에서 무변경

### current terminal snapshot after scope policy closeout

current terminal snapshot은 아래처럼 다시 읽는다.

- final status counts: `existing_cluster_absorption 2 / direct_use 8 / policy_review_closed_maintain_identity_fallback_isolation 7`
- active execution lane count: `0`
- no immediate next round planned: `true`
- reopen gates: `scope_policy_override_round`, `runtime_adoption_round`

즉 current architecture에서 `identity_fallback` residual lineage는 unresolved hold 없이 fully terminalized됐다.

### what changed and what did not

바뀐 것:

- former `bucket_3_scope_hold 7`은 policy-closed isolation rows로 전환됐다
- current lane의 remaining hold count는 `0`이다

바뀌지 않은 것:

- runtime path counts
- publish split
- cluster taxonomy
- cluster budget `30 / 30`

따라서 current architecture는 `7 rows solved by source expansion`이 아니라, **7 rows governance-closed as maintain-isolation policy rows** 로 읽어야 한다.

## 11-50. Iris DVF 3-3 identity_fallback current roadmap is complete at terminal policy authority

2026-04-17 기준 current architecture에서 `identity_fallback`는 더 이상 실행 중 lane이나 follow-up debt inventory가 아니다. current roadmap은 terminal policy authority 기준으로 완료 상태다.

### current completion markers

canonical completion read point는 아래 artifact다.

- `staging/identity_fallback_source_expansion/identity_fallback_terminal_status.json`
- `staging/identity_fallback_source_expansion/identity_fallback_terminal_handoff.json`

이 completion snapshot 기준 current marker는 아래처럼 읽는다.

- final status counts: `existing_cluster_absorption 2 / direct_use 8 / policy_review_closed_maintain_identity_fallback_isolation 7`
- scope policy hold count: `0`
- active unresolved count: `0`
- active execution lane count: `0`
- next lane: `none`
- no immediate next round planned: `true`

### architectural implication

즉 current architecture에서 `identity_fallback`는 더 이상 `remaining execution scope`가 아니라, historical provenance artifact 위에 얹힌 terminalized current-state surface다.

future work가 필요하면 아래 둘 중 하나를 explicit하게 새로 열어야 한다.

- `scope_policy_override_round`
- `runtime_adoption_round`

## 11-51. Iris DVF 3-3 source-expansion distribution remeasurement gate는 source expansion closeout 위의 observer side branch다

2026-04-19 기준 current architecture에서 `SDRG(Source-Expansion Distribution Remeasurement Gate)`는 source expansion execution과 분리된 **observer side branch** 다. 이 gate는 upstream closeout 이후 5축 분포를 다시 계측하고, 그 결과를 semantic decision input과 terminal handoff로 넘긴다.

### responsibility boundary

current SDRG는 아래를 한다.

- comparison baseline / current handoff authority 2층 baseline freeze
- source expansion closeout artifact existence를 trigger prerequisite로 읽기
- fresh recompute observer snapshot 읽기
- audit / overlay / lint / quality / publish 5축 delta adjudication
- semantic decision input packet 생성
- retroactive first-application backfill artifact 생성
- terminal status / handoff / Group B pre-wiring 생성

current SDRG는 아래를 하지 않는다.

- source expansion inventory / batch execution 소유
- compose external repair
- runtime / bridge / publish mutation
- T-Gates / Q-Gates 판정 대체
- Phase 3A guardrail trigger

즉 current architecture에서 SDRG는 source expansion round의 후행 observer gate이지, batch owner나 enforcement authority가 아니다.

### artifact chain

current root read point는 아래 artifact다.

- `staging/source_expansion_distribution_remeasurement_gate/source_expansion_distribution_remeasurement_gate_manifest.json`
- `staging/source_expansion_distribution_remeasurement_gate/source_expansion_distribution_remeasurement_gate_status.md`

supporting implementation provenance는 아래 walkthrough를 참조한다.

- `docs/Iris/Done/iris-dvf-3-3-source-expansion-distribution-remeasurement-gate-walkthrough.md`

이 root 아래 current chain은 아래처럼 읽는다.

1. baseline freeze
   - `phase1_baseline_freeze/pre_expansion_baseline_v0.json`
   - `phase1_baseline_freeze/baseline_authority_snapshot.md`
2. trigger prerequisites
   - `phase2_3_trigger_prerequisites/source_expansion_closeout_authority.json`
   - `phase2_3_trigger_prerequisites/expected_expansion_scope_reference.json`
   - `phase2_3_trigger_prerequisites/source_expansion_trigger_prerequisites.json`
3. fresh recompute
   - `phase4_fresh_recompute/post_expansion_remeasurement_v0.json`
4. 5-axis distribution delta
   - `phase5_distribution_delta/distribution_delta_report_v0.json`
   - `phase5_distribution_delta/baseline_carry_decision_v0.json`
5. semantic decision input
   - `phase6_semantic_decision/semantic_decision_input_packet.json`
6. retroactive first application
   - `phase6_5_retroactive_backfill/retroactive_axis_recoverability_precheck.json`
   - `phase6_5_retroactive_backfill/distribution_delta_report_v0_retroactive.json`
7. terminal closeout
   - `closeout/source_expansion_remeasurement_terminal_status.json`
   - `closeout/source_expansion_remeasurement_terminal_handoff.json`
8. Group B pre-wiring
   - `group_b_pre_wiring/group_b_expected_delta_template.json`

### baseline layering and read points

current SDRG baseline은 하나의 "현재 값"이 아니라 두 layer를 같이 가진다.

- historical comparison baseline
  - `cluster_summary 1440 / identity_fallback 617 / role_fallback 48`
- current handoff authority
  - `cluster_summary 2040 / identity_fallback 17 / role_fallback 48`

current delta 계산 기준은 두 번째 layer인 current handoff authority다. 첫 번째 layer는 source expansion closeout의 historical context만 제공한다.

또한 current architecture는 status / handoff 역할을 분리한다.

- `terminal_status.json`: lane closeout authority
- `terminal_handoff.json`: downstream read authority

이 분리는 `identity_fallback` terminal snapshot과 SDRG terminal snapshot 모두에 동일하게 적용된다.

### current closeout reading

current SDRG closeout snapshot은 아래처럼 읽는다.

- axis adjudication: `audit PASS / overlay PASS / lint PASS / quality PASS / publish PASS`
- round exit status: `PASS`
- immediate next round planned: `false`
- retroactive backfill mode: `observer_only_first_application`
- Group B pre-wiring: `preferred_precondition`, `manual baseline freeze fallback allowed`

즉 current architecture에서 SDRG는 **closed observer authority with no automatic next round** 다. future work가 필요하면 explicit semantic decision이나 future Group B closeout 뒤의 새 SDRG run으로만 이어진다.

### current semantic decision authority after SAPR

current semantic decision authority는 아래 read point를 같이 본다.

- `phase6_semantic_decision/semantic_decision_input_packet.json`
- `docs/DECISIONS.md`의 2026-04-19 SAPR 항목
- `staging/semantic_axis_policy_round/phase4_selection/semantic_weak_carry_matrix.json`
- `staging/semantic_axis_policy_round/closeout/sapr_closeout_report.md`
- `quality_baseline_v4`

current provenance walkthrough는 아래를 사용한다.

- `docs/Iris/Done/iris-dvf-3-3-semantic-axis-policy-round-walkthrough.md`

current SAPR closeout은 weak family를 아래처럼 읽는다.

- `KEEP_OBSERVER_ONLY`
  - `body-role mapping weak`
  - `adequate 유지군`
  - `legacy/generated weak reference`
- `ADMIT_AS_AXIS_CANDIDATE`
  - `structural feedback weak candidate`
  - `source-expansion post-round new weak`
- `CARRY_TO_BASELINE_V5`
  - 없음

즉 current architecture에서 SAPR는 weak-family carry policy를 닫았지만, current build의 `quality_state`/`publish_state`를 바꾸지 않는다. future carry가 필요하면 `quality/publish decision stage` single writer 안에서 decision-stage input expansion으로만 연다. walkthrough는 provenance 설명용이고 authority write surface는 아니다.

## 11-52. Future A-4-1 / cluster-budget reopen은 bounded subset single-authority sizing governance를 전제로 한다

2026-04-20 기준 current architecture에서 future explicitly-opened `A-4-1 rework / cluster budget` reopen은 big-bang reopen default가 아니라, **subset-bounded single-authority sizing governance** 를 먼저 읽는 separate future round다.

### responsibility boundary

current architecture에서 이 amendment는 아래를 한다.

- future `A-4-1 / cluster-budget reopen`의 manifest sizing rule 고정
- `existing-cluster reuse`와 `net-new cluster design` authority 혼재 금지
- explicit reopen gate 이후 same wave 안의 `reusable 먼저 -> net-new subset sequential` ordering 고정
- subset admission을 representative task context / evidence-closure shape / validation path / authoring burden 기준으로 읽기

current architecture에서 이 amendment는 아래를 하지 않는다.

- current reopen gate 정의
- `future_new_source_discovery_hold` 판정
- closure policy widening 대체
- `30-cap` 재검토
- current terminal snapshot / runtime / publish mutation

### current read rule

current authority footing은 recent terminal-state decisions(`active_execution_lane_count = 0`, `no_immediate_next_round_planned = true`)와 explicit reopen gate다.

- current state는 여전히 `no immediate next round planned`다.
- amendment adoption 자체는 current `A-4-1` reopen opening을 뜻하지 않는다.
- `future_new_source_discovery_hold`는 item-level evidence gate이므로 이 amendment의 적용 대상이 아니다.

### reference read points

- `docs/DECISIONS.md`의 2026-04-20 sizing governance amendment 항목
- `docs/Iris/iris-dvf-3-3-reopen-round-sizing-governance-scope-lock.md`
- `docs/Iris/iris-dvf-3-3-reopen-round-sizing-governance.md`
- `docs/Iris/iris-dvf-3-3-reopen-round-sizing-governance-consistency-review.md`
- `docs/Iris/iris-dvf-3-3-reopen-round-sizing-governance-closeout.md`

## 11-53. Iris DVF 3-3 compose authority migration round는 body_plan을 forward compose authority로 재선언하되 single-writer runtime contract는 유지한다

2026-04-20 기준 current architecture에서 compose authority migration round는 body-role closeout의 재오픈이 아니라, **별도 authority lane에서 `sentence_plan` 중심 compose authority를 `body_plan` 중심 authority로 상위 교체하는 round** 다.

### relationship to prior sections

- `11-20`의 `sentence_plan` 규약은 current build의 **legacy v1 baseline** 으로 유지한다.
- `11-40`의 body-role closeout은 계속 closeout 상태로 유지한다.
- `11-42`의 surface contract authority migration과 `quality/publish decision stage` single writer는 그대로 유지한다.
- 즉 이번 round는 body-role repair 구조나 publish contract를 다시 여는 것이 아니라, **compose authority의 canonical forward read** 를 바꾸는 separate lane이다.

### forward compose authority

current forward compose authority는 아래처럼 읽는다.

- `facts + body_source_overlay + decisions + profiles -> body_plan -> rendered flat string -> quality/publish decision stage -> Lua bridge -> Browser/Wiki`

운영 규칙은 아래처럼 고정한다.

- `body_plan`은 아래 6개 section만 사용한다.
  - `identity_core`
  - `use_core`
  - `context_support`
  - `acquisition_support`
  - `limitation_tail`
  - `meta_tail`
- section ordering은 deterministic해야 한다.
- shipping artifact는 계속 flat string이다.
- section trace는 internal meta일 수 있지만 runtime consumer input은 아니다.

### writer and ownership boundary

- compose writer는 계속 **하나** 다.
- `quality/publish decision stage`는 계속 post-compose **single writer** 다.
- validator는 drift/legality checker이며 writer가 아니다.
- Lua bridge와 runtime consumer는 render-only다.
- Browser/Wiki는 이미 계산된 staged authority만 소비한다.

### compatibility adapter boundary

- Phase C compatibility adapter는 `compose_layer3_text.py` 내부에 위치하는 compose-internal non-writer bridge다.
- adapter는 legacy `sentence_plan` 필드를 `body_plan` section 자리에 배치만 하며 문장을 생성하지 않는다.
- 빈 section의 emission 또는 omission은 compose가 `body_plan` 규칙으로 결정한다.
- adapter는 기존 등록 row의 native `body_plan` 전환이 끝날 때까지 유지되지만, 신규 등록 row는 처음부터 native path를 사용한다.
- adapter row count는 migration progress inventory일 뿐 runtime gate가 아니다.

### Phase C contact-point reading

Phase C 동안의 contact-point read는 아래처럼 고정한다.

- `LAYER4_ABSORPTION`을 포함한 migration-time structural signal
  - Phase C validation에서는 read-only observer signal이다.
  - Phase C exit blocker가 아니다.
  - section 기준 semantic redesign은 Phase D 책임이다.
  - 이 원칙은 current surface contract authority를 소급 수정하지 않는다.
- legacy `quality_flag` family
  - `function_narrow / identity_only / acq_dominant_reordered`
  - existing family frozen 상태로 유지한다.
  - writer input으로 승격하지 않는다.
- `quality_state / publish_state` post-compose decision stage
  - rendered flat string과 existing decision input shape를 계속 소비한다.
  - `body_plan` 내부 section trace는 stage input으로 승격하지 않는다.

### Phase C closeout current read

- `compose_profiles_v2` path에서 actual runtime compose authority는 `compose_layer3_text.py` 내부 `body_plan` writer로 닫혔다.
- `build_layer3_body_plan_v2_preview.py`는 독립 writer가 아니라 `build_rendered()` wrapper다.
- closeout 기준 artifacts는 `pilot_corpus_manifest.json`, `golden_subset_seed.json`, `compose_determinism_report.json`, `legacy_vs_bodyplan_diff_report.json`, `phase_c_exit_gate.md`, `phase_c_adversarial_review.md`로 읽는다.
- golden seed gate는 profile별 최소 `5`개와 overall observed-quality mix를 충족한다. current runtime에 없는 per-profile quality triad는 unavailable cell로 기록하며 exit blocker가 아니다.
- adapter는 계속 compose-internal non-writer bridge이며, row count threshold gate가 아니라 Phase D native-path migration inventory다.

따라서 11-53은 current adopted architecture read다. 이 시점에는 runtime writer authority, pilot/golden/determinism/diff verification, adversarial wording reconciliation이 닫혔고, Phase D structural redesign / Phase E-0 full-runtime regression gate / Phase E runtime Lua consumer rollout은 아직 별도 opening이 필요한 후속 lane으로 남는다. 같은 세션에서 생성된 D/E 산출물은 11-54에서 quarantine 처리한다.

## 11-54. Iris DVF 3-3 same-session body_plan Phase D/E attempt is quarantined

2026-04-21 기준 same-session Phase D/E execution attempt는 current architecture로 채택하지 않는다.

### Quarantine Reasons

- 사전 `scope_policy_override_round` opening decision이 없다.
- D/E attempt input은 `historical_snapshot/full_runtime`의 `1050` rows이며, current runtime baseline `2105 rows / active 2084 / silent 21`이 아니다.
- `quality_publish_decision_v2_preview.full.jsonl`은 `body_plan` section 기준으로 `quality_state / publish_state`를 재계산해 `adequate 130`을 만들었다. 이는 `quality_baseline_v4` 유지와 current `v5` cutover 없음 결정과 충돌한다.
- `IrisLayer3Data.lua`의 `1050` row generated parity는 deployed runtime authority가 아니다. runtime Lua data는 sealed `quality_publish` bridge baseline으로 복구한다.

### Current Architecture Boundary

Current adopted state는 Phase C closeout까지다. `body_plan` writer authority는 채택됐지만, structural accounting redesign, full-runtime regression gate, runtime Lua consumer rollout은 다시 열려면 별도 explicit round가 필요하다. Future D/E는 `2105` runtime source, `quality_baseline_v4` frozen decision stage, `internal_only` row non-drop contract, in-game validation policy를 선행 invariant로 검증해야 한다.

## 11-55. Iris DVF 3-3 Phase D/E staged rollout override round is open as staged-only lane

2026-04-22 기준 Phase D/E-0/E는 `scope_policy_override_round`로 다시 열렸다. 이 opening은 11-54의 quarantined same-session attempt를 되살리는 것이 아니라, `2105` sealed baseline 위에서 새 staged/static lane을 여는 것이다.

### Baseline invariants

- row count: `2105`
- runtime_state: `active 2084 / silent 21`
- runtime path: `cluster_summary 2040 / identity_fallback 17 / role_fallback 48`
- publish split: `internal_only 617 / exposed 1467`
- quality distribution: `strong 1316 / adequate 0 / weak 768`

Publish split과 quality distribution은 active rows 기준이다. Silent `21` rows는 두 split의 모수에서 제외한다. Runtime path의 `identity_fallback 17`과 publish split의 `internal_only 617`은 별도 계약이며, Phase E-0 gate는 두 수치를 독립 검증한다.

### Execution boundary

- Phase D는 pure observer structural reclassification이다.
- Phase D는 rendered text, `quality_state`, `publish_state`를 수정하지 않는다.
- Phase E-0은 `quality_baseline_v4`를 sealed regression axis로 검증한다.
- Phase E는 staged/static rollout과 `ready_for_in_game_validation`까지만 닫는다.
- Manual in-game validation과 deployed closeout은 별도 QA round 또는 사전 scope update 없이는 열지 않는다.

## 11-56. Iris DVF 3-3 Phase D/E staged rollout override round is closed at ready_for_in_game_validation

2026-04-22 기준 Phase D/E-0/E override round는 staged/static closeout 상태다. 이 closeout은 deployed closeout이 아니라, artifact-level parity와 static runtime readiness를 닫은 상태다.

### closed artifacts

- Phase D observer artifact:
  - `Iris/build/description/v2/staging/compose_contract_migration/phase_d_e_current_session/body_plan_structural_reclassification.2105.jsonl`
  - `Iris/build/description/v2/staging/compose_contract_migration/phase_d_e_current_session/body_plan_structural_reclassification.2105.summary.json`
- Phase E-0 regression gate:
  - `Iris/build/description/v2/staging/compose_contract_migration/phase_d_e_current_session/body_plan_v2_regression_gate_report.2105.json`
- Phase E staged/static rollout:
  - `Iris/build/description/v2/staging/compose_contract_migration/phase_d_e_current_session/IrisLayer3Data.body_plan_v2.2105.staged.lua`
  - `Iris/build/description/v2/staging/compose_contract_migration/phase_d_e_current_session/body_plan_v2_lua_bridge_report.2105.json`
  - `Iris/build/description/v2/staging/compose_contract_migration/phase_d_e_current_session/body_plan_v2_runtime_validation_report.2105.json`
  - `Iris/build/description/v2/staging/compose_contract_migration/phase_d_e_current_session/body_plan_v2_runtime_rollout_report.2105.json`

### validation read

- Phase D is pure observer:
  - `row_count 2105`
  - `writer_role observer_only`
  - `hard_block_candidate_count 0`
  - row artifact contains no `quality_state` field
- Phase E-0 is pass:
  - 9 gate axes pass
  - quality distribution gate pass
  - runtime path `cluster_summary 2040 / identity_fallback 17 / role_fallback 48`
  - publish split `internal_only 617 / exposed 1467`
  - quality distribution `strong 1316 / adequate 0 / weak 768`
- Phase E staged/static rollout is pass:
  - source/runtime bridge rows `2105 / 2105`
  - staged/workspace/expected Lua hash `0390272b93a933d7e53bba996b322ffbdd9fc905585bec03fc78d338f469f062`
  - static runtime status `ready_for_in_game_validation`

### boundary

This architecture section does not declare user-facing deployed verification. Manual in-game validation remains a separate QA round input, and `quality_baseline_v4 -> v5` cutover remains closed.

### traceability read point

The execution walkthrough for this closeout is:

- `docs/Iris/iris-dvf-3-3-phase-d-e-staged-rollout-override-round-walkthrough.md`

Use that walkthrough to reconstruct why the round uses the 2026-04-15 subset rollout baseline, why the `1050 / adequate 130` attempt remains quarantined, how the runtime path source mismatch was corrected, and how byte-level Lua artifact parity was verified. The walkthrough is traceability documentation only; architecture authority remains this section plus `DECISIONS.md` and `ROADMAP.md`.

## 11-57. CDPCR-AS diagnostic observer lane is closed as Branch B without authority seal execution

2026-04-23 기준 `CDPCR-AS`는 `implementation-drift verification + authority seal round`의 Tier 1 observer lane을 Branch B로 닫았다.

### classification read

- classification result: `Branch B - entrypoint_implementation_drift`
- closeout wording: `closed without seal - entrypoint implementation drift, patch round reserved`
- gating evidence:
  - `build_script.legacy_default_open = false`
  - `cli_direct.legacy_default_open = true`
- supplementary evidence:
  - `test_harness.legacy_default_open = false`
  - `preview_wrapper.legacy_default_open = false`
  - diagnostic body_plan Lua hash matches sealed staged Lua hash `0390272b93a933d7e53bba996b322ffbdd9fc905585bec03fc78d338f469f062`

### authority boundary

The canonical forward read remains:

- `compose_profiles_v2.json + body_plan -> rendered flat string -> quality/publish decision stage -> Lua bridge -> runtime consumer`

This section does not reopen the body_plan authority decision. It records that the direct default compose entrypoint implementation still drifts from that authority because `compose_layer3_text.py` direct `main()` opens legacy `compose_profiles.json` by default.

### path separation

- Default authority target remains `compose_profiles_v2.json + body_plan`.
- Legacy `sentence_plan` remains compatibility/diagnostic input only.
- Implicit legacy fallback is prohibited as the desired final state, but the patch to enforce that is reserved to the follow-up `entrypoint drift patch + authority seal round`.
- The Phase C compatibility adapter remains compose-internal and is not promoted to a default authority source.

### non-reopen clause

`CDPCR-AS - diagnostic observer lane closed as B`.

This does not automatically reopen:

- `11-53`
- `11-55`
- `11-56`

It also does not declare deployed closeout. Current runtime artifact state remains `ready_for_in_game_validation` pending a separate manual in-game validation QA round.

Historical note: this section records the pre-EDPAS drift observation. For current architecture, read 11-58 as the superseding state for direct default compose entrypoint authority.

## 11-58. EDPAS seals the direct default compose entrypoint to body_plan authority

2026-04-23 기준 `EDPAS`는 CDPCR-AS Branch B follow-up으로 실행되어 direct default compose entrypoint drift를 닫았다.

### default entrypoint authority

The direct default compose entrypoint now reads:

- `compose_profiles_v2.json + body_plan`

Default mode validates that loaded profiles use schema `compose-profiles-v2`. A legacy profile file can no longer be opened by default mode and silently dispatch to `sentence_plan`.

### explicit legacy access

Legacy direct writer access is explicit-only:

- `compat_legacy`
- `diagnostic_legacy`

`diagnostic_legacy` cannot write canonical staged/workspace authority artifacts outside the EDPAS diagnostic root.

### retained compatibility mapping

The v2 resolver legacy label -> body profile compatibility mapping remains in place:

- `interaction_tool -> tool_body`
- `interaction_component -> material_body`
- `interaction_output -> output_body`

This mapping is not a default authority source and does not execute `sentence_plan`. It remains only as a body_plan resolution compatibility bridge.

### validation read

- Unit tests passed: `299`
- Direct default entrypoint 2105 diagnostic run emitted `dvf-3-3-body-plan-v2-preview-v0`
- Diagnostic Lua hash matched sealed staged/workspace hash:
  - `0390272b93a933d7e53bba996b322ffbdd9fc905585bec03fc78d338f469f062`
- Design review guard violations: `0`

### boundary

EDPAS does not declare deployed closeout. Current runtime state remains `ready_for_in_game_validation` pending separate manual in-game validation QA.

### current issue status

The prior mismatch between shipped body_plan artifact authority and direct default compose entrypoint authority is closed. The shipped artifact remains body_plan-based, and the default compose entrypoint now opens the same body_plan authority source by default.

## 11-59. Phase D signal preservation patch is an additive dual-axis observer lane over the sealed staged baseline

2026-04-24 기준 current architecture에서 `Phase D observer signal preservation patch round`는 `11-56` staged/static closeout을 다시 쓰는 round가 아니다. 이 lane은 이미 닫힌 staged baseline 위에서 source-side explicit signal과 section-derived structural signal을 분리 보존하는 additive observer branch다.

### dual-axis observer read model

current row model은 두 축을 분리해 기록한다.

- `source_signal_*`
  - upstream field 이름은 그대로 `violation_type` / `violation_flags`를 읽는다.
  - explicit `violation_type`이 source axis primary authority다.
  - `violation_flags`는 승인된 closed allowlist fallback일 때만 source axis에 들어온다.
- `section_signal_*`
  - `body_plan` section trace에서 재계산한 observer axis다.
  - section family는 `SECTION_*` namespace를 사용한다.
  - source axis와 같은 row에 동시에 존재할 수 있으며 source axis를 덮어쓰지 않는다.
- overlap read
  - row field 이름은 `signal_overlap_state`다.
  - 값 공간은 `source_only / section_only / coexist / dual_none`이다.
  - generic `none` remainder는 `dual_none`에서만 읽는다.

### gate and seal boundary

Phase 1 gate는 `violation_type` schema existence와 usable source population을 분리해서 본다.

- `violation_type` field 자체가 없으면 `blocked_by_missing_violation_type_field`
- field는 있으나 row-level non-null population이 `0`이면 `blocked_by_empty_violation_type_population`
- field와 non-null population은 있으나 core source family를 실질적으로 운반하지 못하면 `closed_with_upstream_signal_gap_handoff`
- current sealed run은 `pass`

이 lane은 additive-only다. 기존 `body_plan_structural_reclassification.2105.jsonl` / `.summary.json`, staged Lua, workspace Lua, publish split, quality split, rendered text를 수정하지 않는다.

### artifact topology

current observer branch의 canonical artifact set은 아래 경로에 있다.

- `staging/compose_contract_migration/phase_d_signal_preservation_patch_round/body_plan_signal_preservation.2105.jsonl`
- `staging/compose_contract_migration/phase_d_signal_preservation_patch_round/body_plan_signal_preservation.source_distribution.json`
- `staging/compose_contract_migration/phase_d_signal_preservation_patch_round/body_plan_signal_preservation.section_distribution.json`
- `staging/compose_contract_migration/phase_d_signal_preservation_patch_round/body_plan_signal_preservation.crosswalk.json`
- `staging/compose_contract_migration/phase_d_signal_preservation_patch_round/phase_d_signal_preservation_validation_report.json`
- `staging/compose_contract_migration/phase_d_signal_preservation_patch_round/signal_preservation_crosscheck_report.json`
- `staging/compose_contract_migration/phase_d_signal_preservation_patch_round/phase_d_signal_preservation_diagnostic_packet.json`

보조 설계 read point는 같은 경로의 아래 문서를 사용한다.

- `source_signal_source_map.md`
- `signal_model_design.md`
- `section_signal_derivation_rule.md`

### current read

current sealed run에서 source preservation result는 다음처럼 읽는다.

- source total distribution target: `BODY_LACKS_ITEM_SPECIFIC_USE 617 / FUNCTION_NARROW 7 / none 1481`
- actual source target check: `match`
- section primary distribution: `SECTION_FUNCTION_NARROW 1433 / none 672`
- overlap distribution: `source_only 67 / section_only 876 / coexist 557 / dual_none 605`
- newly observed structural-only rows: `876`
- existence/no-overwrite targets `IDENTITY_ONLY`, `ACQ_DOMINANT`: observed replacement `0`

즉 current architecture에서 이 lane은 old structural observer artifact를 교체하지 않고, source-side preservation delta와 section-side structural delta를 함께 고정하는 observer-only read branch다. 이 section도 deployed closeout, manual in-game validation, `quality_baseline_v4 -> v5` cutover를 선언하지 않는다.

## 11-60. Current default structural reclassification path is now converged onto the dual-axis canonical observer model

`11-59` additive lane는 계속 adopted traceability baseline으로 남는다. 하지만 `2026-04-24` convergence closeout 이후 current default-path observer authority는 additive lane wording이 아니라 structural default path 자체의 converged plain-name artifact set으로 읽는다.

### current default read model

current default script는 `report_layer3_body_plan_structural_reclassification.py`다. 이 path는 이제 `dual_axis_canonical` read를 default로 집행한다.

- source axis
  - output fields: `source_signal_primary`, `source_signal_secondary`, `source_signal_origin`, `source_signal_present`
  - authority rule: `violation_type` explicit primary, `violation_flags` restricted fallback
- section axis
  - output fields: `section_signal_primary`, `section_signal_secondary`, `section_signal_origin`, `section_signal_present`
  - derivation rule: `body_plan` trace에서 `SECTION_*` namespace로 재계산
- overlap
  - output field: `signal_overlap_state`
  - value space: `source_only / section_only / coexist / dual_none`

이 field naming은 `11-59` additive lane row naming을 승계한다. 따라서 additive lane과 converged default path 사이에 translation namespace를 새로 만들지 않는다.

### current artifact topology

current default authority artifact set은 아래 경로다.

- `staging/compose_contract_migration/phase_d_structural_reclassification_code_path_convergence_round/phase4_artifacts/body_plan_structural_reclassification.2105.jsonl`
- `staging/compose_contract_migration/phase_d_structural_reclassification_code_path_convergence_round/phase4_artifacts/body_plan_structural_reclassification.2105.summary.json`
- `staging/compose_contract_migration/phase_d_structural_reclassification_code_path_convergence_round/phase4_artifacts/body_plan_structural_reclassification.source_distribution.json`
- `staging/compose_contract_migration/phase_d_structural_reclassification_code_path_convergence_round/phase4_artifacts/body_plan_structural_reclassification.section_distribution.json`
- `staging/compose_contract_migration/phase_d_structural_reclassification_code_path_convergence_round/phase4_artifacts/body_plan_structural_reclassification.overlap_distribution.json`
- `staging/compose_contract_migration/phase_d_structural_reclassification_code_path_convergence_round/phase4_artifacts/body_plan_structural_reclassification.crosswalk.json`
- `staging/compose_contract_migration/phase_d_structural_reclassification_code_path_convergence_round/phase4_artifacts/body_plan_structural_reclassification.artifact_validation_report.json`

plain-name `.summary.json`은 current authority summary다. summary는 stable subset을 유지한다.

- `current_read_model = dual_axis_canonical`
- `summary_schema_version = body-plan-structural-reclassification-summary-stable-v1`
- `linked_artifacts`
- `legacy_compat_summary`

diagnostic-only legacy single-slot view는 아래 explicit path로 격리된다.

- `staging/compose_contract_migration/phase_d_structural_reclassification_code_path_convergence_round/diagnostic/legacy_view/body_plan_structural_reclassification_legacy_single_slot.2105.jsonl`
- `staging/compose_contract_migration/phase_d_structural_reclassification_code_path_convergence_round/diagnostic/legacy_view/body_plan_structural_reclassification_legacy_single_slot.summary.json`

### current validation read

current converged run은 아래처럼 읽는다.

- source distribution: `BODY_LACKS_ITEM_SPECIFIC_USE 617 / FUNCTION_NARROW 7 / none 1481`
- section distribution: `SECTION_FUNCTION_NARROW 1433 / none 672`
- overlap distribution: `source_only 67 / section_only 876 / coexist 557 / dual_none 605`
- overwrite resolution count: `557`
- section-only newly visible rows: `876`
- lossy old artifact row count: `1500`
- entrypoint surface guard: `pass`
- artifact hash guard: `pass`

### current issue status

`11-59` closeout 시점에 남아 있던 "observer patch applied but default structural code path divergence remains" 문제는 닫혔다. current default structural path와 current authority artifact는 같은 dual-axis observer model을 읽는다.

## 11-61. Adapter removal criterion seal is closed as readiness-only inventory

2026-04-25 기준 `Iris DVF 3-3 Adapter / Native Body Plan Readiness Round`는 removal criterion을 sealed한 readiness-only round로 닫혔다. 이 section은 11-53의 `compatibility adapter boundary`를 수정하지 않고, 그 boundary 위에 execution 전제 조건이 봉인되었음을 기록한다.

### current read

- persisted old profile count: `2105`
- active old profile count: `2084`
- silent old profile count: `21`
- active resolver reach scope: `active_rendered_preview_only`
- legacy fallback target count: `78`
- active execution queue: `2084`
  - `non_fallback_active_metadata_swap 2006`
  - `fallback_dependent_active 78`
- silent metadata inventory: `21`
- fallback subclassification: `mechanical_ready 78 / schema_gap 0`
- readiness report status: `pass`

### boundary status

The compatibility adapter remains compose-internal and non-writer as described in 11-53. The adapter has not been removed, and persisted legacy labels have not been rewritten by this closeout.

The sealed criterion is: removal execution may only be opened by a separate execution round that consumes the active queues, preserves rendered/Lua/runtime gates, and keeps resolver code modification out of scope. Diagnostic-only isolation or complete removal of the resolver compatibility mapping remains a separate resolver cleanup round.

### status lifecycle

The Phase 6 readiness report is not the closeout snapshot. In Phase 6, `execution_queue_status` and `silent_metadata_inventory_status` are `ready`. After Phase 7 adversarial review PASS and Phase 8 top-doc closeout, the closeout snapshot reads both as `sealed`.

If a planning copy shows those two fields as `sealed` inside the Phase 6 report shape, that copy is stale against the adopted lifecycle and must be backflow-corrected to `ready / ready` for Phase 6. The `sealed / sealed` state belongs only to the closeout pass JSON and top-doc closeout read.

### traceability

The operational walkthrough is:

- `docs/Iris/iris-dvf-3-3-adapter-native-body-plan-readiness-round-walkthrough.md`

It is a traceability read point, not a new architecture authority. It records the readiness builder script hash, Phase 0-8 artifacts, measured counts, status lifecycle, and next-round handoff.

Current runtime/staged state remains `ready_for_in_game_validation`. This section does not declare deployed closeout, runtime QA pass, adapter removal, legacy count reduction, or `ready_for_release`.

## 11-62. Adapter / Native Body Plan Metadata Migration closes active source-shape debt

2026-04-25 기준 `Adapter / Native Body Plan Metadata Migration Round`는 active rendered-preview execution queue 2084 row의 persisted legacy `compose_profile` labels를 native `body_plan` metadata로 이전하고 `closed_with_active_metadata_migration_only`로 닫혔다.

### current read

- active old profile count: `0`
- active native profile count: `2084`
- silent old profile count: `21` (deferred)
- static legacy fallback target residue: `0`
- default path legacy fallback reach: `0`
- default_adapter_dependency_count: `0`
  - derived alias of `default_path_legacy_fallback_reach_count`, not adapter removal
- canonical row legacy field residue count: `0`
- rendered output delta count: `0`
- sealed staged/workspace Lua hashes: unchanged
- resolver source file hash: unchanged

### boundary

- compatibility adapter remains compose-internal and non-writer
- resolver compatibility mapping remains for explicit diagnostic/compat path
- resolver cleanup is a separate round
- silent 21 metadata intake/cleanup is a separate round
- manual in-game validation QA remains a separate round
- runtime state remains `ready_for_in_game_validation`

### artifact topology

- `Iris/build/description/v2/staging/compose_contract_migration/adapter_native_body_plan_metadata_migration_round/phase9_closeout/closeout_pass.json`
- `docs/Iris/Done/Walkthrough/iris-dvf-3-3-adapter-native-body-plan-metadata-migration-round-walkthrough.md`

The walkthrough is a traceability read point, not a new architecture authority. It records the v0.3 plan synthesis, deterministic executor, dry-run isolated simulation, canonical apply, post-apply verification, adversarial review, closeout artifact, and `307 tests / OK` verification result. Architecture authority remains this section plus `DECISIONS.md`, `ROADMAP.md`, and the generated phase artifacts.

This section does not declare adapter removal, resolver cleanup, runtime rebaseline, manual QA pass, deployed closeout, or `ready_for_release`.

## 11-63. Layer4 Absorption is sealed as a decision namespace, not a structural axis

2026-04-29 기준 `Iris DVF 3-3 Layer4 Absorption Policy Round`는 `closed_with_policy_sealed_zero_count_production_safe`로 닫혔다.

### current namespace read

`LAYER4_ABSORPTION_CONFIRMED`는 source axis family도 section axis family도 아니다. Current architecture에서는 아래처럼 읽는다.

- namespace: `layer_boundary_hard_block`
- family: `LAYER4_ABSORPTION_CONFIRMED`
- confidence values: `confirmed / none`
- `suspect` tier: 없음
- authority: `quality_publish_decision_stage_only_when_activated`

이 namespace는 제3 structural axis가 아니며, source distribution과 section distribution을 변경하지 않는다.

### detector contract

Detector는 rendered text를 읽지 않는다. 허용 입력은 아래뿐이다.

- `body_plan` section trace
- source provenance field
- source list/cardinality evidence
- destination layer/slot evidence

Current sealed run에서는 scalar `layer4_context_hint` source가 `452`건 관측됐지만, 3-4 interaction list/cardinality object가 3-3 body slot에 배치된 confirmed edge는 없었다. 따라서 `confirmed_count = 0`이다.

### current validation read

- row count: `2105`
- confirmed count: `0`
- production labeling path: `sealed_zero_count`
- writer mutation count: `0`
- publish delta: `0`
- quality delta: `0`
- runtime delta: `0`
- source axis mutation: `false`
- section axis mutation: `false`
- source distribution: `BODY_LACKS_ITEM_SPECIFIC_USE 617 / FUNCTION_NARROW 7 / none 1481`
- section distribution: `SECTION_FUNCTION_NARROW 1433 / none 672`
- overlap distribution: `source_only 67 / section_only 876 / coexist 557 / dual_none 605`

Artifact topology:

- `Iris/build/description/v2/staging/compose_contract_migration/layer4_absorption_policy_round/phase1_detection/layer4_absorption_provenance_detection.2105.jsonl`
- `Iris/build/description/v2/staging/compose_contract_migration/layer4_absorption_policy_round/phase1_detection/layer4_absorption_provenance_summary.json`
- `Iris/build/description/v2/staging/compose_contract_migration/layer4_absorption_policy_round/phase4_disposition/layer4_absorption_disposition_result.json`
- `Iris/build/description/v2/staging/compose_contract_migration/layer4_absorption_policy_round/phase5_invariants/layer4_absorption_invariant_verification_report.json`
- `Iris/build/description/v2/staging/compose_contract_migration/layer4_absorption_policy_round/phase7_closeout/closeout_pass.json`

This section does not declare activation, deployed closeout, runtime QA pass, source expansion, or `quality_baseline_v4 -> v5` cutover.

## 11-64. Publish writer authority is layer/position correctness

2026-04-29 기준 `FUNCTION_NARROW Disposition Closure and Publish Writer Authority Seal Round`는 `closed_with_publish_writer_authority_sealed_delta_0`으로 닫혔다.

### publish writer authority

Current Iris DVF 3-3 publish writer authority는 semantic quality strength가 아니라 layer/position correctness다.

- `quality_state`는 publish branch의 독립 writer가 아니다.
- `internal_only`는 Case 1 또는 Case 3처럼 위치/권한 사유가 있을 때만 정당화된다.
- `FUNCTION_NARROW`나 `ACQ_DOMINANT` 같은 semantic narrowness/acquisition dominance만으로 blanket isolation을 열 수 없다.

### case table

| Case | Situation | Publish treatment | Basis |
|---|---|---|---|
| Case 1 | correct-position required content absent | `internal_only` justified | content absence |
| Case 2 | correct-position content exists but narrow/acquisition-dominant | publish unchanged | no position violation |
| Case 3 | Layer 4 interaction content enters Layer 3 body slot | `internal_only` justified | layer/authority violation |

### current read

- `internal_only_total = 617`
- `case_1_count = 617`
- `case_2_count = 0`
- `case_3_count = 0`
- `publish_restore_decision_count = 0`
- applied publish delta: `0`
- applied quality delta: `0`
- bridge availability: `internal_only 617 / exposed 1467 unchanged`
- source distribution: `BODY_LACKS_ITEM_SPECIFIC_USE 617 / FUNCTION_NARROW 7 / none 1481 unchanged`
- runtime state: `ready_for_in_game_validation unchanged`

`FUNCTION_NARROW` blanket isolation and `ACQ_DOMINANT` blanket isolation are forbidden from this closeout onward. `ACQ_DOMINANT` residual remeasurement remains deferred until after source expansion.

Artifact topology:

- `Iris/build/description/v2/staging/compose_contract_migration/function_narrow_disposition_closure_publish_writer_authority_seal_round/phase2_inventory/internal_only_617_reason_inventory.json`
- `Iris/build/description/v2/staging/compose_contract_migration/function_narrow_disposition_closure_publish_writer_authority_seal_round/phase3_reclassification/blanket_isolation_forbidden_reclassification.json`
- `Iris/build/description/v2/staging/compose_contract_migration/function_narrow_disposition_closure_publish_writer_authority_seal_round/phase4_build_delta_verification/function_narrow_disposition_build_delta_verification_result.json`
- `Iris/build/description/v2/staging/compose_contract_migration/function_narrow_disposition_closure_publish_writer_authority_seal_round/phase5_invariants/function_narrow_disposition_invariant_verification_report.json`
- `Iris/build/description/v2/staging/compose_contract_migration/function_narrow_disposition_closure_publish_writer_authority_seal_round/phase7_closeout/closeout_pass.json`

This section does not declare `FUNCTION_NARROW` second rollout, source expansion, runtime-side compose/rewrite, deployed closeout, or release readiness.
