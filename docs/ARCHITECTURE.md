# ARCHITECTURE.md

> 상태: 초안 v0.2 + addenda consolidated through 2026-05-18
> 기준일: 2026-05-18
> 상위 기준: `Philosophy.md`, `DECISIONS.md`  
> 목적: Pulse 생태계의 구조 지도, 역할 경계, 의존 방향을 고정한다.
> 읽기 규칙: 1~8장은 current canonical architecture로 읽고, 9장은 중복 addendum을 압축한 historical trace ledger로 읽는다. 세부 원문이 필요한 엄격 감사에서는 원본 addendum archive 또는 VCS history를 참조한다.

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
  - Runtime guarded-call boundary는 `Iris/Util/IrisProtectedCall.lua`가 소유한다.
  - `Iris/Data/IrisUseCaseDescriptions.lua`는 public facade이며, 실제 generated use-case payload는 `Iris/Data/UseCaseDescriptions/Chunk001..009.lua`에 분산된다.
  - Layer 3 runtime data의 deployable authority는 `Iris/Data/IrisLayer3DataChunks.lua` manifest와 `Iris/Data/IrisLayer3DataChunks/Chunk001..011.lua` chunk files다.
  - `Iris/Data/IrisLayer3Data.lua` monolith는 active runtime deployable source가 아니며, PZ auto-load 대상에 chunk files와 동시에 남겨 두지 않는다.
  - `Iris/Logic/IrisDesc/*`가 current description implementation namespace이며, `Pulse/Iris/Logic/IrisDesc/*`는 compatibility wrapper다.

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
- chunked Layer 3 runtime Lua data 원문 유지
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

---

# 9. Addendum consolidation ledger

## 9-1. 정리 원칙

이 장은 기존 `# 9`, `# 10`, `# 11-*` addendum 본문을 그대로 반복하지 않는다. 이미 current canonical architecture에 흡수된 내용은 앞의 모듈 지도와 경계 규칙에서 읽고, 이 장은 **어떤 historical addendum이 어떤 current read로 흡수되었는지**만 남긴다.

원칙은 다음과 같다.

- 중복 normative 문장은 제거한다.
- 기존 addendum의 ID / 제목 / 순서 / closeout 성격은 ledger로 보존한다.
- parent addendum 내부의 하위 heading도 historical trace 단위로 의미가 있으면 별도 ledger row로 보존한다. 단, current normative 본문은 반복하지 않고 disposition으로만 연결한다.
- 이 ledger는 새 설계 권한을 만들지 않는다.
- 충돌 시 `Philosophy.md`가 최상위 기준이고, 그다음 `DECISIONS.md`, 그다음 이 문서의 current canonical section을 따른다.
- 엄격한 증거 감사가 필요하면 원본 addendum archive 또는 VCS history를 읽는다. 이 파일은 working prompt용 current architecture 문서다.

## 9-2. Consolidated current readpoints

### Iris taxonomy / Evidence / Description

- Iris는 전체 아이템 위키 위에 Evidence 기반 구조를 얹는 정보 모드다.
- 자동 분류는 의미 추론기가 아니라 바닐라가 텍스트로 선언한 증거를 누적하는 인덱서다.
- Evidence Table은 의미론 사전이 아니라 자동/수동 경계 계약이다.
- Description 계층은 분류를 재판정하지 않고, 이미 고정된 facts / decisions / rendered surface를 사람이 읽을 수 있게 출력한다.
- 문서화 담당자는 후행 서술자이며, evidence / rule / classification authority를 새로 만들지 않는다.

### Right-click / Recipe / Context Outcome

- Recipe source와 Right-click source는 동급의 독립 추출 트랙이다.
- 두 트랙 모두 최종적으로는 action이 아니라 outcome fact로 정규화되어야 한다.
- Right-click Gate-0는 `FullType 기반 직접 실행 도구 Evidence`를 확인하는 source 검증 단계이며, 메뉴명 / 행동명 / UI 존재 자체는 canonical evidence가 아니다.
- Strong / Weak 구분은 source 검증과 capability 등록 경계에만 쓰고, 설명 계층이 이를 다시 해석하지 않는다.
- Recipe requirements, use_case, color layer, UI integration은 모두 offline 산출물 소비 / runtime render-only 경계 안에서 읽는다.

### DVF 3-3 production / body_plan

- Layer 3-3은 item-centric body layer이며, Layer 3-4의 상세 interaction list를 흡수하지 않는다.
- current default compose authority는 `compose_profiles_v2.json + body_plan`이다.
- legacy `sentence_plan` path는 explicit compatibility / diagnostic mode로만 남는다.
- compose writer는 단일 writer이고, validator / linter / bridge / runtime consumer는 writer가 아니다.
- shipping artifact는 계속 flat string이며, `body_plan` section trace는 internal meta 또는 build-time authority branch로만 읽는다.

### DVF status / quality / publish axes

- `active / silent`는 semantic quality 완료가 아니라 runtime에 올릴 수 있는 row 상태에 가깝다.
- runtime_state, quality_state, publish_state는 분리된 세 축으로 읽는다.
- `ready_for_in_game_validation`, `release_eligible`, `blocked`, `partial`, `implemented_only` 같은 closeout vocabulary는 evidence-bounded 상태 표현이며, public release 완료 선언이 아니다.
- style normalization은 post-compose deterministic layer이고, style linter는 advisory / diagnostics 역할을 유지한다.

### Identity fallback / source expansion / cluster budget

- identity_fallback 관련 closeout들은 taxonomy reopen이 아니라 bounded source-expansion / closure-admissibility / terminal accounting trace로 읽는다.
- A-4-1 / cluster-budget reopen은 future subset reopen이며, 이미 닫힌 terminal policy authority를 자동으로 흔들지 않는다.
- artifact chain은 provenance로 남기되, current consumer는 terminal snapshot과 current canonical readpoint를 우선한다.

### Public strategy / external mods / spoke-led demand

- Pulse는 먼저 로더로 전면 경쟁하기보다 Echo / Fuse / Nerve / Iris / Frame / Canvas 같은 spoke가 가치를 증명한 뒤 공통 지반으로 드러나는 전략을 유지한다.
- Iris의 외부 모드 확장은 모든 모드를 추론하는 AI 위키가 아니라, 표준 구조를 제공한 모드 데이터를 정규화해 렌더링하는 방식이다.
- 공개 순서 / B42 대응 / 시장 포지션 관련 addendum은 현재 architecture boundary를 바꾸는 새 권한이 아니라 product surface strategy trace로 읽는다.

### Runtime / build refactor / packaging

- Iris refactor 계열 addendum은 runtime/build boundary와 workspace-copy runtime structure를 닫은 것으로 읽는다.
- 이는 release 완료나 public readiness 선언이 아니다.
- runtime Lua deployable authority는 chunk manifest / chunk files 중심이며, monolith와 chunk files를 동시에 PZ auto-load 대상으로 두지 않는다.
- BOM-free guard는 PZ Kahlua compatibility를 위한 runtime artifact hygiene로 유지한다.

### Resolver cleanup / residual disposition debt

- `selected_role`, `selected_role_precedence`, `selected_role_target`은 native resolver authority / trace다. 이 값들은 removal target도 아니고 legacy fallback authority도 아니다.
- Diagnostic-only legacy compatibility guard debt는 `closed_with_diagnostic_only_resolver_guard`로 닫혔다. Legacy label은 forward/default input에서 조용히 default authority로 받아들여지지 않는다.
- Default resolver가 native v2 authority로 해석할 수 없는 `interaction_tool`, `interaction_component`, `interaction_output`, 또는 malformed `interaction_*` label을 fallback authority로 사용하려 하면 `DEFAULT_RESOLVER_REJECTED_LEGACY_COMPAT_LABEL`로 fail-loud한다. Explicit diagnostic resolver mode는 diagnostic output root guard 아래에서만 legacy compatibility mapping을 연다.
- selected-role influence `0`은 더 이상 completion condition이 아니다. selected-role non-zero finding은 selected-role이 native resolver authority에 속한다는 evidence로 읽는다.
- Active resolver correctness debt는 닫힌 상태다. `Residual Resolver Compatibility Final Disposition Debt`도 2026-05-18 final disposition round로 닫힌 상태로 읽는다.
- Final disposition은 두 잔여 표면을 모두 명시적으로 처분한다: legacy compatibility mapping은 permanent diagnostic-only non-authority fixture로 보존하고, post-migration exposed legacy adapter entrypoint modes는 제거한다.
- Legacy compatibility mapping은 permanent diagnostic-only non-authority fixture로 보존한다. Default resolver authority가 아니며, 보존하는 동안 diagnostic-only / non-writer / non-default authority boundary와 fail-loud tests를 유지해야 한다.
- Post-migration exposed legacy adapter entrypoint modes는 제거됐다. Historical/offline legacy sentence-plan tooling fixture는 active default/writer/diagnostic adapter surface로 읽지 않는다.
- Complete-removal은 더 이상 selected-role / resolver cleanup goal에 포함하지 않는다. Frozen 2105 byte-level recovery는 별도 future deletion/removal goal이 명시적으로 열릴 때만 historical trace에서 다시 검토한다.
- Diagnostic mapping deletion, runtime Lua regeneration, deployed closeout, `ready_for_release`는 이 architecture readpoint에서 선언하지 않는다.

### Silent 21 metadata cleanup / replacement authority

- Silent 21 metadata cleanup debt는 active resolver correctness debt나 adapter disposition debt가 아니다.
- Active 2084 row의 old `compose_profile` metadata migration은 닫힌 상태로 읽는다. 이전에 남아 있던 `persisted_old_profile_count = 21`은 silent/unadopted row에 한정된 source metadata disposition debt였다.
- 이 debt는 `Silent Metadata Intake / Cleanup Round` Branch B closeout으로 닫혔다. Silent/unadopted 21 row의 `compose_profile`만 `interaction_tool -> tool_body`로 rewrite했고, `persisted_old_profile_count = 0`, `silent_old_profile_count = 0`으로 검증했다.
- Current checkout에는 `Silent Metadata Intake / Cleanup Round`가 원래 요구한 historical sealed `silent_metadata_inventory.21.jsonl` 및 sealed `migration_manifest.2084.jsonl` authority artifacts가 없다. 이 부재는 original sealed authority 복원 실패로 보존한다.
- 따라서 cleanup rewrite 전 `Silent 21 Replacement Authority Reconstruction Round`가 필요했으며, 현재는 `closed_with_replacement_authority_adopted`로 닫힌 prerequisite다. 이 라운드는 original sealed authority 복원이 아니라, current repository artifacts를 교차검증해 silent 21 전용 replacement reconstruction authority를 새로 채택한 prerequisite closeout이다.
- Replacement authority는 silent 21 cleanup 전용이다. Active 2084 authority, resolver behavior, selected-role authority, adapter disposition, rendered output, staged/workspace Lua, runtime_state, quality_state, publish_state를 재정의하지 않는다.
- AI-trace inventory는 supporting trace로만 읽는다. Shape-only 2084/21 candidate는 authority로 승격하지 않는다.
- `Silent 21 Replacement Authority Reconstruction Round`는 `closed_with_replacement_authority_adopted`로 닫혔다. Sprint7 2105-row payload와 dry-run post-migration decisions가 primary reconstruction basis이고, AI-trace inventory는 supporting trace only, shape-only 2084/21 candidate는 rejected non-authority다.
- Adopted replacement authority는 silent 21 allowlist와 silent-only `interaction_tool -> tool_body` cleanup write mapping으로 제한된다. 이 mapping은 resolver compatibility mapping, adapter diagnostic disposition, default fallback behavior, 또는 full 2105 authority를 재정의하지 않는다.
- `Silent Metadata Intake / Cleanup Round`는 adopted replacement authority를 input으로 소비해 Branch B로 닫혔다. Active 2084 unchanged, row_count 2105 unchanged, rendered/Lua/runtime/state surfaces unchanged가 hard gate로 검증됐다.
- `silent_metadata_inventory` status는 sealed deferred inventory에서 disposed cleanup inventory로 이동한 것으로 읽는다.
- This architecture readpoint does not claim runtime rollout, deployed closeout, Workshop release, manual in-game QA pass, or `ready_for_release`.

## 9-3. Historical addendum trace ledger

| Original line | Original addendum / section | Current disposition |
|---:|---|---|
| L982 | 9. Iris Taxonomy addendum | Iris taxonomy / Evidence boundary로 2-5에 흡수. Ledger만 보존. |
| L984 | 9-1. Iris는 전체 아이템 위키 위에 Evidence를 얹는다 | Iris taxonomy / Evidence boundary로 2-5에 흡수. Ledger만 보존. |
| L994 | 9-2. 계층 역할 재고정 | Iris taxonomy / Evidence boundary로 2-5에 흡수. Ledger만 보존. |
| L1016 | 9-3. 9개 대분류 기준선 | Iris taxonomy / Evidence boundary로 2-5에 흡수. Ledger만 보존. |
| L1032 | 9-4. 최소 구조 원칙 | Iris taxonomy / Evidence boundary로 2-5에 흡수. Ledger만 보존. |
| L1039 | 9-5. 경계 규칙 | Iris taxonomy / Evidence boundary로 2-5에 흡수. Ledger만 보존. |
| L1050 | 9-6. blocklist와 Misc 폴백의 위치 | Iris taxonomy / Evidence boundary로 2-5에 흡수. Ledger만 보존. |
| L1064 | 9-7. Phase 2 구조 설계의 현재 상태 | Iris taxonomy / Evidence boundary로 2-5에 흡수. Ledger만 보존. |
| L1078 | 10. Iris Description writing addendum | Iris Description / 표현 계층 경계로 2-5에 흡수. Ledger만 보존. |
| L1080 | 10-1. 소분류 설명의 역할 | Iris taxonomy / Evidence boundary로 2-5에 흡수. Ledger만 보존. |
| L1091 | 10-2. 설명 계층의 문체 규약 | Iris Description / 표현 계층 경계로 2-5에 흡수. Ledger만 보존. |
| L1101 | 10-3. 시스템 정보 포함 기준 | Iris Description / 표현 계층 경계로 2-5에 흡수. Ledger만 보존. |
| L1115 | 10-4. 바닐라 기준과 모드 확장성 | Iris Description / 표현 계층 경계로 2-5에 흡수. Ledger만 보존. |
| L1123 | 10-5. 소분류 설명과 개별 아이템 설명의 경계 | Iris taxonomy / Evidence boundary로 2-5에 흡수. Ledger만 보존. |
| L1130 | 10-6. 구조보다 설명으로 해결하는 기본값 | Iris Description / 표현 계층 경계로 2-5에 흡수. Ledger만 보존. |
| L1138 | 11. Iris Right-click Gate-0 v2 evidence-first addendum | Right-click / Recipe source pipeline 경계로 2-5에 흡수. 중복 세부는 압축. |
| L1140 | 11-1. 목적 | Iris addendum trace로 보존. 중복 본문은 current canonical readpoint에 흡수. |
| L1144 | 11-2. Gate-0 판정 순서 | Right-click / Recipe source pipeline 경계로 2-5에 흡수. 중복 세부는 압축. |
| L1160 | 11-3. v2 파이프라인 책임 분리 | Iris addendum trace로 보존. 중복 본문은 current canonical readpoint에 흡수. |
| L1179 | 11-4. scope 밖 / REVIEW / NO의 의미 | Iris addendum trace로 보존. 중복 본문은 current canonical readpoint에 흡수. |
| L1193 | 11-5. property-based 필드의 취급 | Right-click / Recipe source pipeline 경계로 2-5에 흡수. 중복 세부는 압축. |
| L1201 | 11-6. Gate-0의 역할 제한 | Right-click / Recipe source pipeline 경계로 2-5에 흡수. 중복 세부는 압축. |
| L1211 | 11-7. 운영 단계 전환 | Iris addendum trace로 보존. 중복 본문은 current canonical readpoint에 흡수. |
| L1224 | 11-8. candidate-only와 prove anchor의 지위 | Iris addendum trace로 보존. 중복 본문은 current canonical readpoint에 흡수. |
| L1235 | 11-9. REVIEW와 scope 밖의 후속 경로 | Iris addendum trace로 보존. 중복 본문은 current canonical readpoint에 흡수. |
| L1247 | 11-10. Recipe / Right-click 동급 2트랙과 automatic-only 운영 | Right-click / Recipe source pipeline 경계로 2-5에 흡수. 중복 세부는 압축. |
| L1262 | 11-11. 컴파일러 -> 뷰어형 Iris | Iris addendum trace로 보존. 중복 본문은 current canonical readpoint에 흡수. |
| L1276 | 11-12. Gate-0 Right-click 자동 확장의 종료 조건 | Right-click / Recipe source pipeline 경계로 2-5에 흡수. 중복 세부는 압축. |
| L1293 | 11-13. Recipe requirements display pipeline | Right-click / Recipe source pipeline 경계로 2-5에 흡수. 중복 세부는 압축. |
| L1342 | 11-14. Automatic-only use_case pipeline | Right-click / Recipe source pipeline 경계로 2-5에 흡수. 중복 세부는 압축. |
| L1374 | 11-15. dynamic recipe review / legacy closure | Right-click / Recipe source pipeline 경계로 2-5에 흡수. 중복 세부는 압축. |
| L1393 | 11-16. Recipe requirements color layer | Right-click / Recipe source pipeline 경계로 2-5에 흡수. 중복 세부는 압축. |
| L1444 | 11-17. Right-click capability UI integration | Right-click / Recipe source pipeline 경계로 2-5에 흡수. 중복 세부는 압축. |
| L1510 | 11-18. Recipe interaction wiki layer | Right-click / Recipe source pipeline 경계로 2-5에 흡수. 중복 세부는 압축. |
| L1542 | 11-19. Frame reconfirmation | Frame 정체성 재확인으로 2-6에 흡수. 별도 addendum 본문 제거. |
| L1555 | 11-20. Layer 3 DVF body-only composition pipeline | DVF 3-3 production/runtime/status 계약으로 2-5에 흡수. 현재 readpoint만 유지. |
| L1634 | 11-21. Layer 3 acquisition_hint elevation contract | DVF 3-3 production/runtime/status 계약으로 2-5에 흡수. 현재 readpoint만 유지. |
| L1690 | 11-22. Iris as a validated knowledge production system | Iris addendum trace로 보존. 중복 본문은 current canonical readpoint에 흡수. |
| L1727 | 11-23. Iris external-mod normalization boundary | 공개 전략 / 외부 모드 / 생태계 포지션 trace로 압축. 현재 포지션만 유지. |
| L1751 | 11-24. Final-applied fact rule for mod conflicts | 공개 전략 / 외부 모드 / 생태계 포지션 trace로 압축. 현재 포지션만 유지. |
| L1761 | 11-25. Ecosystem moat and peer-spoke interpretation | 공개 전략 / 외부 모드 / 생태계 포지션 trace로 압축. 현재 포지션만 유지. |
| L1782 | 11-26. Acquisition coverage staging-first closeout and candidate_state separation | DVF 운영 closeout / identity_fallback trace로 압축. artifact readpoint 중심 보존. |
| L1826 | 11-27. Candidate_state reevaluation is a separate Phase 3 concern | DVF 운영 closeout / identity_fallback trace로 압축. artifact readpoint 중심 보존. |
| L1860 | 11-28. Phase 3 closeout treats candidate_state and approval as separate operational planes | DVF 운영 closeout / identity_fallback trace로 압축. artifact readpoint 중심 보존. |
| L1889 | 11-29. Approval backlog operations are no-rule-change, cluster-first, and queue-sourced | DVF 운영 closeout / identity_fallback trace로 압축. artifact readpoint 중심 보존. |
| L1912 | 11-30. DVF 3-3 production batch remains separate from demo outputs | DVF 3-3 production/runtime/status 계약으로 2-5에 흡수. 현재 readpoint만 유지. |
| L1934 | 11-31. DVF freeze requires both offline completion and actual runtime consumer hookup | DVF 3-3 production/runtime/status 계약으로 2-5에 흡수. 현재 readpoint만 유지. |
| L1958 | 11-32. Identity generation and template naturalization belong to different layers | DVF 3-3 production/runtime/status 계약으로 2-5에 흡수. 현재 readpoint만 유지. |
| L1991 | 11-33. Layer 3-3 remains a body layer and must not absorb Layer 3-4 interaction detail | DVF 3-3 production/runtime/status 계약으로 2-5에 흡수. 현재 readpoint만 유지. |
| L2013 | 11-34. ACQ_ONLY surface-form repair belongs to compose-time subject synthesis, not post-processing hacks | DVF 3-3 production/runtime/status 계약으로 2-5에 흡수. 현재 readpoint만 유지. |
| L2033 | 11-35. Layer 3-3 is an item-centric body, not an acquisition-led farming notice | DVF 3-3 production/runtime/status 계약으로 2-5에 흡수. 현재 readpoint만 유지. |
| L2056 | 11-36. Iris release posture is accessibility-first and vanilla-first; mod expansion stays downstream | 공개 전략 / 외부 모드 / 생태계 포지션 trace로 압축. 현재 포지션만 유지. |
| L2081 | 11-37. Iris DVF 3-3 post-cleanup operational architecture addendum | DVF 3-3 production/runtime/status 계약으로 2-5에 흡수. 현재 readpoint만 유지. |
| L2199 | 11-38. Iris DVF 3-3 second-pass closure는 더 이상 열린 execution architecture가 아니다 | DVF 운영 closeout / identity_fallback trace로 압축. artifact readpoint 중심 보존. |
| L2232 | 11-39. Iris DVF 3-3 style surface normalization은 post-compose deterministic layer다 | DVF 3-3 production/runtime/status 계약으로 2-5에 흡수. 현재 readpoint만 유지. |
| L2287 | 11-40. Iris DVF 3-3 body-role architecture closes through decisions overlay, compose-internal repair, and next-build feedback | DVF 3-3 production/runtime/status 계약으로 2-5에 흡수. 현재 readpoint만 유지. |
| L2379 | 11-41. Iris DVF 3-3 current architecture uses a three-axis contract over the preserved runtime model | DVF 3-3 production/runtime/status 계약으로 2-5에 흡수. 현재 readpoint만 유지. |
| L2523 | 2026-04-07 addendum — 공개 순서와 표면 구조 재정렬 | 공개 전략 / 외부 모드 / 생태계 포지션 trace로 압축. 현재 포지션만 유지. |
| L2587 | 3. 2026-04-07 Addendum — Pulse 개방 순서 역전과 spoke-led demand 구조 | 공개 전략 / 외부 모드 / 생태계 포지션 trace로 압축. Parent addendum으로 보존하되, 내부 하위 heading은 아래 별도 row로 순서 보존. |
| L2589 | Pulse의 현재 전략적 위치 | 공개 전략 / spoke-led demand trace의 하위 섹션으로 보존. Parent readpoint에 흡수. |
| L2600 | spoke-led demand 구조 | 공개 전략 / spoke-led demand trace의 하위 섹션으로 보존. Parent readpoint에 흡수. |
| L2610 | public surface diversification | 공개 표면 다각화 trace로 보존. Core 기능 확장이 아니라 workflow surface 전략으로 흡수. |
| L2622 | workflow lane 기준의 채택 구조 재강화 | Starter / Guided / Raw workflow lane trace로 보존. Parent readpoint에 흡수. |
| L2632 | 공개 이벤트보다 순차적 의미 확장 | 결과물 선공개 → 기반 후노출 전략 trace로 보존. Parent readpoint에 흡수. |
| L2642 | Iris의 경쟁 리스크 재해석 | Iris product surface / positioning trace로 보존. Parent readpoint에 흡수. |
| L2653 | 11-42. Iris DVF 3-3 surface contract authority migration splits advisory sensing from structural contract input | DVF 3-3 production/runtime/status 계약으로 2-5에 흡수. 현재 readpoint만 유지. |
| L2753 | 11-43. Iris DVF 3-3 acquisition lexical authority and body-role lexical cleanup are build-time authority branches, not runtime language systems | DVF 3-3 production/runtime/status 계약으로 2-5에 흡수. 현재 readpoint만 유지. |
| L2855 | 11-44. Iris DVF 3-3 identity_fallback source expansion current closeout is bounded by the frozen A-4-1 cluster budget | DVF 운영 closeout / identity_fallback trace로 압축. artifact readpoint 중심 보존. |
| L2915 | 11-45. Iris DVF 3-3 identity_fallback residual round closeout 이후 current architecture는 &#96;phase3_taxonomy_pending 0 + frozen hold 11&#96; 상태로 읽는다 | DVF 운영 closeout / identity_fallback trace로 압축. artifact readpoint 중심 보존. |
| L2958 | 11-46. Iris DVF 3-3 identity_fallback closure policy expansion은 taxonomy reopen이 아니라 closure admissibility boundary 조정이다 | DVF 운영 closeout / identity_fallback trace로 압축. artifact readpoint 중심 보존. |
| L3007 | 11-47. Iris DVF 3-3 identity_fallback closure policy round closeout 이후 current architecture는 &#96;policy_resolved_scope_hold_only&#96; 상태다 | DVF 운영 closeout / identity_fallback trace로 압축. artifact readpoint 중심 보존. |
| L3045 | 11-48. Iris DVF 3-3 identity_fallback current-state consumer는 terminal snapshot을 읽고, immediate next round는 계획하지 않는다 | DVF 운영 closeout / identity_fallback trace로 압축. artifact readpoint 중심 보존. |
| L3088 | 11-49. Iris DVF 3-3 identity_fallback scope policy round closeout 이후 current architecture는 unresolved hold 없이 fully terminalized 상태다 | DVF 운영 closeout / identity_fallback trace로 압축. artifact readpoint 중심 보존. |
| L3134 | 11-50. Iris DVF 3-3 identity_fallback current roadmap is complete at terminal policy authority | DVF 운영 closeout / identity_fallback trace로 압축. artifact readpoint 중심 보존. |
| L3163 | 11-51. Iris DVF 3-3 source-expansion distribution remeasurement gate는 source expansion closeout 위의 observer side branch다 | DVF 운영 closeout / identity_fallback trace로 압축. artifact readpoint 중심 보존. |
| L3283 | 11-52. Future A-4-1 / cluster-budget reopen은 bounded subset single-authority sizing governance를 전제로 한다 | DVF 운영 closeout / identity_fallback trace로 압축. artifact readpoint 중심 보존. |
| L3320 | 11-53. Iris DVF 3-3 compose authority migration round는 body_plan을 forward compose authority로 재선언하되 single-writer runtime contract는 유지한다 | body_plan migration / observer / publish authority trace로 압축. current sealed boundary만 유지. |
| L3393 | 11-54. Iris DVF 3-3 same-session body_plan Phase D/E attempt is quarantined | body_plan migration / observer / publish authority trace로 압축. current sealed boundary만 유지. |
| L3408 | 11-55. Iris DVF 3-3 Phase D/E staged rollout override round is open as staged-only lane | body_plan migration / observer / publish authority trace로 압축. current sealed boundary만 유지. |
| L3430 | 11-56. Iris DVF 3-3 Phase D/E staged rollout override round is closed at ready_for_in_game_validation | body_plan migration / observer / publish authority trace로 압축. current sealed boundary만 유지. |
| L3477 | 11-57. CDPCR-AS diagnostic observer lane is closed as Branch B without authority seal execution | body_plan migration / observer / publish authority trace로 압축. current sealed boundary만 유지. |
| L3522 | 11-58. EDPAS seals the direct default compose entrypoint to body_plan authority | body_plan migration / observer / publish authority trace로 압축. current sealed boundary만 유지. |
| L3569 | 11-59. Phase D signal preservation patch is an additive dual-axis observer lane over the sealed staged baseline | body_plan migration / observer / publish authority trace로 압축. current sealed boundary만 유지. |
| L3632 | 11-60. Current default structural reclassification path is now converged onto the dual-axis canonical observer model | body_plan migration / observer / publish authority trace로 압축. current sealed boundary만 유지. |
| L3693 | 11-61. Adapter removal criterion seal is closed as readiness-only inventory | body_plan migration / observer / publish authority trace로 압축. current sealed boundary만 유지. |
| L3733 | 11-62. Adapter / Native Body Plan Metadata Migration closes active source-shape debt | body_plan migration / observer / publish authority trace로 압축. current sealed boundary만 유지. |
| L3769 | 11-63. Layer4 Absorption is sealed as a decision namespace, not a structural axis | body_plan migration / observer / publish authority trace로 압축. current sealed boundary만 유지. |
| L3821 | 11-64. Publish writer authority is layer/position correctness | body_plan migration / observer / publish authority trace로 압축. current sealed boundary만 유지. |
| L3866 | 11-65. Iris refactor v2.0 closes runtime/build boundary debt without changing product authority | Iris runtime/build refactor closeout trace로 압축. 릴리즈 완료로 읽지 않음. |
| L3909 | 11-66. Iris runtime Lua files must be BOM-free for PZ Kahlua compatibility | Iris runtime/build refactor closeout trace로 압축. 릴리즈 완료로 읽지 않음. |
| L3927 | 11-67. Iris final refactoring roadmap closes the runtime/build structure, not the release | Iris runtime/build refactor closeout trace로 압축. 릴리즈 완료로 읽지 않음. |
| L3969 | 11-68. Iris refactoring roadmap v4.1 seals workspace-copy runtime structure | Iris runtime/build refactor closeout trace로 압축. 릴리즈 완료로 읽지 않음. |
| L4021 | 11-69. Selected role bridge impact remains a resolver cleanup opening gate | Resolver cleanup / frozen 2105 evidence debt trace로 보존. diagnostic-only와 complete-removal을 분리. |
| L4133 | 11-70. Resolver cleanup and frozen baseline debt are split by cleanup kind | Resolver cleanup / frozen 2105 evidence debt trace로 보존. diagnostic-only와 complete-removal을 분리. |
| current | 2026-05-18 Adapter / Diagnostic Compatibility Final Disposition Round closeout | Current readpoint에 흡수. Legacy compatibility mapping은 permanent diagnostic-only non-authority fixture로 보존하고, post-migration exposed legacy adapter entrypoint modes는 제거. active resolver correctness debt와 residual adapter / diagnostic disposition debt는 닫힌 상태. |
| current | 2026-05-18 Silent 21 metadata cleanup prerequisite redefinition | Current readpoint에 흡수. Silent 21 cleanup debt는 unadopted source metadata disposition debt로 유지하되, original sealed authority artifact 부재는 provenance gap으로 보존하고 adopted replacement authority를 cleanup rewrite 입력 authority로 허용한다. |
| current | 2026-05-18 Silent 21 Replacement Authority Reconstruction Round closeout | Current readpoint에 흡수. Missing original sealed artifacts는 provenance gap으로 보존하고, silent 21 cleanup-only replacement allowlist 및 `interaction_tool -> tool_body` mapping authority를 adopted state로 읽는다. |
| current | 2026-05-18 Silent Metadata Intake / Cleanup Round Branch B closeout | Current readpoint에 흡수. Silent/unadopted 21 row의 `compose_profile`만 `interaction_tool -> tool_body`로 rewrite했고, `persisted_old_profile_count = 0`, `silent_old_profile_count = 0`, active 2084 unchanged, row_count 2105 unchanged, rendered/Lua/runtime/state surfaces unchanged로 닫았다. Runtime rollout, deployed closeout, Workshop release, manual in-game QA pass, `ready_for_release` 선언은 아니다. |

## 9-4. 중복 제거 판정

기존 addendum 본문에서 반복되던 내용은 다음 기준으로 제거한다.

- 이미 `2-5. Iris`에 현재 계약으로 반영된 문장: addendum 본문 반복 제거.
- 같은 내용을 더 늦은 addendum이 supersede한 경우: 늦은 addendum의 current readpoint만 유지.
- artifact 수치 / closeout 수치가 필요한 경우: ledger에 trace를 남기고, 상세 수치는 원본 archive / VCS history / 해당 artifact를 보게 한다.
- public strategy 문장처럼 architecture boundary가 아니라 제품 포지션에 가까운 내용: current strategy readpoint로만 압축.
- resolver / frozen baseline처럼 현 작업 gate에 직접 영향을 주는 내용: current readpoint에 별도 보존.

## 9-5. 사용 규칙

일반 작업 세션에서는 이 파일만 읽어도 된다. 특정 historical round의 수치, artifact 이름, 검증 로그, closeout 문장을 재검토해야 할 때만 원본 archive를 추가로 읽는다.

이 구조의 목적은 historical trace를 지우는 것이 아니라, current architecture prompt에서 중복 본문을 제거하고 **trace pointer만 남기는 것**이다.
