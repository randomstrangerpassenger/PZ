# ROADMAP.md

> 상태: current canonical roadmap  
> 기준일: 2026-09-01 (이번 갱신 범위: Iris DVF 설명·Tooltip·Menu, 기술서 획득 정보, Browser/Wiki 장문 표시, 내부 패키징·검증 적용 범위)\
> 최상위 기준: `Philosophy.md`  
> 결정 기준: `DECISIONS.md`  
> 목적: Pulse 생태계의 현재 상태, 진행 방향, 다음 게이트와 Hold 경계를 고정한다.

---

## 운영 규칙

- 이 문서는 Pulse 생태계의 **현재 상태와 다음 과제**를 보여주는 방향판이다.
- `왜 그렇게 정해졌는가`와 decision history는 `DECISIONS.md`에 남긴다.
- 항목 상태는 `Done / Doing / Next / Backlog / Hold` 중심으로 관리한다.
- `Done`에는 과거 작업의 실행 이력이 아니라 **현재까지 유효한 완료 상태와 그 결과로 확립된 구조**를 남긴다.
- `Doing`에는 현재 유지·정리·구현 중인 전선을, `Next`에는 실제로 남아 있는 다음 gate를 기록한다.
- `Backlog`에는 방향은 유효하지만 현재 전선이 아닌 장기 후보를 두고, `Hold`에는 현재 열지 않거나 금지한 방향을 둔다.
- 본 문서는 구현 세부 로그, validation ledger, closeout ledger 또는 provenance index로 사용하지 않는다.
- attempt / commit / hash / validation count / evidence root / terminal receipt와 개별 작업의 상세 closeout은 `DECISIONS.md` 또는 각 plan / review / closeout 산출물에서 추적한다.
- historical artifact나 과거 작업 결과를 ROADMAP에 남겨야 할 경우에는 작업 이력 자체가 아니라 **현재에도 유효한 상태·경계·다음 gate**로 요약해서 반영한다.

---

# 1. Pulse Core

## 목표

얇고 중립적인 JVM 기반 모드로더 / 플랫폼으로서, **정책이나 제품 로직을 소유하지 않고** Spoke와 외부 모드가 각자의 기능을 자유롭게 구성할 수 있는 공용 기반 capability를 제공한다.

Pulse의 핵심 가치는 특정 first-party 모드를 특별히 지원하는 것이 아니라, 기존 Lua 기반 모딩 생태계와 새로운 Mixin 기반 모딩 생태계를 함께 수용할 수 있는 **자유도 높은 샌드박스형 기반**을 제공하는 데 둔다.

## Current Position

- Pulse Core는 단순 self-boot 수준을 넘어 외부 모드 로딩을 위한 기반 기능을 상당 부분 갖춘 상태다.
- 현재 병목은 기능 부재보다 **모드로더 계약 봉인, 플랫폼 실패 진단, public capability surface 경계 정리**에 있다.
- Phase 1은 구현상 완료 후보에 가깝지만 ROADMAP상 Done 선언 전 최소 loader contract와 검증선을 봉인해야 한다.
- Phase 2는 안정화 / 진단 기반은 존재하지만 외부에 의존 가능한 surface와 내부 구현 경계가 아직 충분히 분리되지 않았다.
- Phase 3은 capability 후보가 이미 넓게 존재하므로 새 기능 추가보다 **어떤 기능이 실제 Core 기반 capability인지 판정하고 surface를 정리하는 작업**이 우선이다.

## Roadmap Phases

### Phase 1 — 실제 모드로더화

**진행도:** 80~90%  
**상태:** Done 후보 / seal pending

#### Current Read

- `ModLoader`는 `mods/` JAR 스캔, `pulse.mod.json` 파싱, 의존성 위상 정렬, 순환 감지, 모드별 Mixin config 등록, `PulseMod.onInitialize()` 호출, 역순 unload와 상태 머신을 이미 포함한다.
- 따라서 Phase 1은 새 로더를 처음부터 만드는 단계가 아니라 **현재 구현을 외부 모드가 실제로 의존할 수 있는 최소 loader contract로 봉인하는 단계**에 가깝다.

#### Remaining Gate

- discovery / resolve / register / initialize / unload 흐름을 공식 최소 계약으로 문서화한다.
- metadata parsing / dependency resolution / incompatibility detection / failure semantics의 최소 계약을 확정한다.
- 외부 모드 sample 또는 smoke 기준으로 실제 loadable platform 여부를 확인한다.
- Mixin registration 실패를 loader-level fatal condition으로 볼지 Phase 2 diagnostic boundary로 넘길지 최소선을 확정한다.
- loader가 dependency / incompatibility를 탐지하더라도 모드 간 정책 판단이나 자동 해결 authority를 갖지 않도록 경계를 명확히 한다.

#### Exit Criteria

- 외부 모드 discovery의 최소 구조가 성립한다.
- 외부 Mixin registration 경로가 boot flow에 연결된다.
- entrypoint 계약이 정의된다.
- metadata / dependency resolution / incompatibility / failure semantics의 최소 계약이 봉인된다.
- 외부 모드 1개 이상을 기준으로 load → initialize → unload 흐름을 설명하고 검증할 수 있다.
- loader가 충돌 상황을 탐지·보고할 수는 있지만 임의의 우선순위나 해결 정책을 결정하지 않는다.

### Phase 2 — 플랫폼 성숙화

**진행도:** 60~70%  
**상태:** Doing

#### Current Read

- EventBus는 우선순위 정렬, 예외 격리, ClassLoader fallback, async post, 모드별 자동 정리 등 플랫폼 안정화 기능을 이미 갖고 있다.
- CrashReporter, DevConsole, EventMonitor, DebugOverlayRenderer, MixinDiagnostics, ThreadGuard 등 진단 / DX 계열 기반도 상당히 존재한다.
- 다만 이 기능들이 **외부 계약 / 확장 경계 / 진단 surface / raw internal implementation**으로 충분히 정리됐다고 보기는 어렵다.

#### Remaining Gate

- 이벤트 / callback 실패가 다른 모드나 Core 전체로 확산되지 않는 격리 규칙을 외부 모드 계약 수준으로 정리한다.
- Mixin 충돌과 적용 실패는 자동 해결보다 **원인 가시화 / 실패 위치 식별 / 복구 가능성 설명** 중심으로 봉인한다.
- DevMode / logging / debug overlay / diagnostics를 제품 기능이 아니라 플랫폼 diagnostic capability로 분리한다.
- 외부 노출 surface를 역할별로 구분한다.
  - Stable Platform Surface
  - SPI / Extension Surface
  - Starter / Guided Surface
  - Diagnostic Surface
  - Raw / Internal Surface
- Starter / Guided 계층에 존재하는 helper가 단순 편의 기능으로 커질 경우 Cortex 책임인지 다시 판정한다.
- 타 모드와의 호환성을 우선하고, Pulse가 충돌의 승자나 정답 구성을 결정하는 구조를 만들지 않는다.

#### Exit Criteria

- 이벤트 / callback 실패가 Core 전체나 다른 모드로 불필요하게 전파되지 않는다.
- Mixin 충돌과 적용 실패를 최소 원인 단위로 진단할 수 있다.
- 외부 모드가 장기적으로 의존할 수 있는 stable platform / SPI surface 초안이 분리된다.
- DevMode / logging / diagnostic hook의 외부 노출 경계가 정리된다.
- Raw / Internal 기능이 stable external contract처럼 오해되지 않는다.
- 진단 capability가 recommendation / automatic resolution / policy engine으로 확장되지 않는다.

### Phase 3 — 공용 Core capability surface 정립

**진행도:** 40~50%  
**상태:** capability inventory는 풍부하지만 Core surface 판정 미완

#### Current Read

- Network, Scheduler, Config, Content Registry, DataAttachments, GameAccess, ResourceLoader, I18n, PermissionManager, SPI Registry, EngineBindings, Lua ecosystem integration 관련 기능, PulseMetrics, ProfilerScope 등 플랫폼 후보 재료는 이미 넓게 존재한다.
- 따라서 Phase 3의 핵심은 “기능을 더 만든다”가 아니라 **기존 기능을 플랫폼 기반 capability / extension surface / diagnostic / helper / convenience / policy / raw-internal로 재분류하는 것**이다.
- 특히 GameAccess, MixinHelper, profiler / metrics, Network, Registry 계열은 유용하지만 구현되어 있다는 이유만으로 stable Core surface에 올리면 Pulse가 얇은 플랫폼이 아니라 비대한 SDK가 될 위험이 있다.
- first-party Spoke의 수요는 capability 후보를 발견하는 중요한 evidence지만, 그 자체가 Core 승격 권한은 아니다.

#### Remaining Gate

- 기존 capability 후보를 inventory로 정리한다.
- 각 후보를 `platform capability / SPI-extension / diagnostic / helper / convenience / policy / raw-internal`로 분류한다.
- Core 승격은 다음 기준을 함께 만족하는 경우에만 검토한다.
  - 플랫폼 기반성이 있다.
  - 특정 Spoke의 제품 로직이나 정책에 종속되지 않는다.
  - first-party 전용이 아니라 외부 소비자에게도 중립적으로 설명할 수 있다.
  - 안정적인 contract로 봉인할 수 있다.
  - Pulse가 소비자의 판단이나 동작 정책을 대신 결정하지 않는다.
- 특정 Spoke 수요는 후보 발견 / 실제 필요성의 evidence로 사용하되 first-party 전용 API 승격 근거로 사용하지 않는다.
- helper / convenience 성격이 강한 기능은 Cortex 후보로 보내고, 제품 고유 로직은 해당 Spoke에 남긴다.
- 중립 노출이 불가능한 기능은 Spoke-local 또는 Raw / Internal로 유지한다.
- Lua 생태계와의 연결 capability는 **Pulse 자체의 JVM+Lua 혼용을 만들지 않는 경계**에서만 허용 가능한지 판정한다.
- 리소스팩 지원도 Canvas의 ResourceState 판단 로직이 아니라 조회 / 식별 / reload / fingerprint 등 중립 capability만 Core 후보로 둔다.

#### Exit Criteria

- profiling / engine stability / Lua stability / information / PackState / ResourceState 계열 소비자가 공통으로 사용할 수 있는 최소 기반 capability가 정리된다.
- 거리 / 상태 / tick / phase 같은 측정·상태 노출 후보의 중립성과 contract 안정성이 판정된다.
- Network / Registry / Scheduler / Config / EventBus / DataAttachments / GameAccess 등 주요 후보의 Core surface disposition이 확정된다.
- Lua 생태계 연결 기능이 Pulse의 JVM-only 책임 경계를 침범하는지 여부가 정리된다.
- 리소스팩 지원 capability와 Canvas가 소유해야 할 ResourceState 계산 / 충돌 분석 / 정책 영역이 분리된다.
- first-party 전용 product logic / DTO / policy가 Core surface에 남지 않는다.
- API 확장 절차가 **후보 발견 → 플랫폼 기반성 판정 → 소비자 중립성 검증 → stable contract 가능성 검토 → surface 봉인**으로 정리된다.

## Hold

- 범용 DataBus / shared state / pub-sub 같은 Spoke 간 실시간 중개 채널을 도입하는 것
- Pulse를 coordinator / mediator / policy hub처럼 비대화하는 것
- recommendation / pressure 판단 / 최적화 정책 / 게임 행동 결정을 Core에 넣는 것
- 하위 모듈의 snapshot / update 주기나 내부 lifecycle을 Pulse가 호출·통제하는 것
- 특정 first-party Spoke의 요구만을 이유로 전용 API / DTO / state / policy를 Core에 넣는 것
- first-party에서 사용한다는 사실만으로 capability를 stable Core surface로 승격하는 것
- 기반성 / 중립성 판정 이전에 public API를 무차별적으로 확대하는 것
- helper / convenience / guide 성격 기능을 Cortex 판정 없이 Core에 누적하는 것
- Spoke의 제품 로직이나 판단 책임을 공용화 명분으로 Core로 끌어올리는 것
- Pulse 자체에 Lua-side product logic을 넣거나 JVM+Lua 혼용 모듈로 만드는 것
- 타 모드 충돌에서 Pulse가 승자 / 정답 / 최적 구성을 결정하거나 자동 해결하는 것
- Echo / Fuse / Nerve / Iris / Frame / Canvas / Cortex를 Pulse가 직접 참조하거나 그 구현에 의존하는 것

---

# 2. Echo

## 목표

병목 지점을 **관찰·계측하는 observer-only 프로파일링 모드**.

Echo는 성능 문제를 분석하거나 해결 정책을 결정하는 엔진이 아니라, 다른 모더와 사용자가 실제 병목을 확인할 수 있도록 **관찰 사실과 측정 데이터를 비침습적으로 노출하는 것**을 목표로 한다.

## Done

- Echo의 **non-invasive observer** 기준과 핫패스 안전 경계를 확립했다.
  - profiling이 대상 runtime의 동작과 의미를 불필요하게 변경하지 않는 관찰 전용 구조를 유지한다.
  - 핫패스에서는 무거운 context capture, 일반 logging 등 관측 자체의 비용을 크게 만드는 동작을 제한한다.
  - 실패하거나 사용할 수 없는 관측 경로는 safe default로 후퇴한다.
  - release 환경은 기본적으로 조용하게 유지하고 debug 진단도 bounded하게 노출한다.

- profiling data와 product policy의 책임을 분리했다.
  - Echo는 측정값 / category / target identity 등 **관찰 사실 중심의 정보**를 제공한다.
  - recommendation / priority / optimization decision / pressure policy를 Echo의 책임으로 두지 않는다.
  - 관찰 결과를 다른 Spoke의 행동 정책으로 직접 변환하지 않는다.

## Doing

- Echo는 현재 신규 기능 확장보다 **soft-freeze / 유지보수 / 관찰 surface 보수** 중심으로 운용한다.
  - 기존 profiling path의 무해성과 안정성을 우선한다.
  - 실제 필요가 확인되지 않은 정밀 profiling 축을 선제적으로 추가하지 않는다.
  - 핫패스 변경은 명확한 필요성과 안전성 근거가 있을 때만 연다.

- Pulse의 기반 capability만 의존하고 profiling logic과 observation ownership은 Echo 내부에 유지한다.
  - Echo가 다른 Spoke의 내부 state / implementation / lifecycle에 직접 의존하지 않는다.
  - Pulse 역시 Echo 내부 snapshot / update lifecycle을 호출하거나 통제하지 않는다.
  - 공통으로 필요한 기반 capability가 있으면 Echo 전용 결합이 아니라 Pulse의 중립 surface 후보로 별도 판정한다.

- JVM + Lua 혼용은 **presentation 범위에 제한적으로** 사용한다.
  - profiling 수집 / aggregation / 판단 책임은 Echo 본체에 유지한다.
  - Lua 사용은 Echo HUD 등 사용자-facing presentation 보조 범위로 제한한다.
  - UI 편의를 이유로 profiling 핵심 책임을 Lua 계층으로 이전하지 않는다.

## Next

- 실제 운영 / profiling 검증에서 명확한 blind spot이 확인될 때만 **국소적 profiling 확장**을 검토한다.
  - 기존 관찰 surface로 설명할 수 없는 실제 문제인지 먼저 확인한다.
  - 새 계측이 핫패스 비용과 observer-only 경계를 침범하지 않는지 판정한다.
  - broad instrumentation보다 최소한의 추가 observation을 우선한다.

- soft-freeze 상태에서 허용되는 유지보수 / surface 변경 기준을 문서화한다.
  - 허용 변경 범위를 bug fix / compatibility correction / bounded diagnostic improvement / evidence-qualified blind-spot coverage로 제한한다.

- Echo의 public surface와 설명 문구를 **관측 / 계측 모듈**이라는 정체성에 맞게 정리한다.
  - 분석 엔진 / 추천 엔진 / 자동 최적화 도구처럼 표현하지 않는다.
  - raw observation과 해석 / 정책의 경계를 외부 consumer가 오해하지 않게 한다.
  - 주요 수요층이 모더라는 특성을 반영해 플랫폼과 핵심 사용자-facing 제품보다 공개 우선순위를 낮게 유지한다.

## Hold

- Echo를 recommendation engine / policy router / automatic optimization decision engine으로 확장하는 것
- Echo observation을 Fuse나 다른 Spoke의 직접적인 행동 / recommendation / optimization policy 입력 계약으로 고착시키는 것
- 다른 Spoke의 내부 API / state / implementation에 직접 의존하는 것
- Pulse나 다른 모듈이 Echo 내부 snapshot / update 주기와 lifecycle을 호출하거나 통제하는 구조
- 핫패스에 StackWalker, 풍부한 context capture, 일반 logging 등 고비용 관측을 기본적으로 되살리는 것
- 명확한 blind spot 없이 정밀 profiling 범위를 선제적으로 대규모 확장하는 것
- observer-only 기능 보수와 Pulse SPI / Core contract 변경을 불필요하게 하나의 작업 범위로 결합하는 것
- microbenchmark 자체를 제품 목표로 삼아 실사용 관측 가치보다 ns 단위 성능 수치를 우선하는 것
- Echo를 현재 soft-freeze 상태에서 다시 메인 개발축으로 전환하는 것
- Lua presentation 계층에 profiling 수집 / aggregation / policy 책임을 이전하는 것
- 플랫폼과 주요 사용자-facing 제품보다 Echo 공개를 선행시키는 것

---

# 3. Fuse

## 목표

Mixin 기반 **엔진 안정성 레이어**.

Fuse는 평균 FPS 상승을 약속하는 최적화 모드가 아니라, **엔진 비용 질서화 / 프레임타임 꼬리 완화 / 스파이크 완충 / 프레임 붕괴 방지**를 목표로 한다.

경로탐색 / 충돌 / 물리 등에서도 더 똑똑한 결과를 만드는 것이 아니라, 게임 결과 semantics를 보존하는 범위에서 **guard / limit / defer / deduplicate / stabilize** 방식의 최소 개입만 허용한다.

## Done

- Pathfinding / Collision / Physics 안정화 축을 current 기능으로 확립했다.
  - 순간적인 경로탐색 비용 폭주를 제한하는 budget / defer 구조를 적용했다.
  - 중복 요청과 반복 비용을 줄이는 deduplication / memoization 계열 guard를 적용했다.
  - 충돌 / 물리 경로에서는 결과 로직을 교체하지 않고 비정상적인 비용 또는 상태 폭주를 완충하는 안전장치를 둔다.
  - 해당 축은 엔진 알고리즘을 더 영리하게 만드는 optimization이 아니라 **붕괴 방지용 안정화**로 유지한다.

- Save / IO Stall과 GC / Allocation Pressure 축의 관측과 한계 확인을 완료했다.
  - 두 영역은 덩어리형 스파이크 특성 때문에 Fuse의 핵심 안정화 전선으로 두지 않는다.
  - 적극적인 해결 / 최적화 대상이 아니라 필요 시 관찰·진단할 수 있는 비핵심 축으로 유지한다.
  - IO / GC를 Fuse의 주요 판매 포인트나 기본 검증선으로 사용하지 않는다.

- Fuse의 semantic-preserving 개입 경계를 확립했다.
  - 엔진 포크나 기존 게임 로직의 구조적 재작성 없이 최소 개입만 허용한다.
  - 안정화 개입은 guard / limit / defer / deduplicate / stabilize 범위를 벗어나지 않는다.
  - 개입 결과가 새로운 gameplay policy나 더 나은 AI 판단으로 변질되지 않게 한다.

## Doing

- Fuse는 현재 신규 기능 개척보다 **soft-freeze / 회귀 검증 / 안정화 경계 유지** 중심으로 운용한다.
  - 핵심 가치는 좀비 AI / update step과 Pathfinding / Collision / Physics에서 발생하는 burst와 tail spike 완충에 둔다.
  - 이미 봉인된 안정화 경로의 의미와 비개입 baseline을 보존한다.
  - 실제 회귀나 명확한 blind spot이 없는 한 새로운 안정화 축을 선제적으로 추가하지 않는다.

- 엔진 포크 없이 **semantic-preserving 최소 개입 원칙**을 유지한다.
  - sustained load 전체를 지속적으로 최적화하는 optimizer로 확장하지 않는다.
  - 근사 알고리즘이나 공격적 결과 변경보다 burst 완충과 fail-soft 방어를 우선한다.
  - 안정화가 필요 없는 상황에서는 가능한 한 개입하지 않는다.

- observation input과 Fuse의 안정화 판단 책임을 분리한다.
  - 필요한 observation input은 Pulse의 중립 capability / surface를 통해서만 소비한다.
  - Echo나 다른 Spoke의 내부 state / implementation / lifecycle에 직접 의존하지 않는다.
  - 개입 조건, threshold, cooldown과 실제 안정화 동작은 Fuse 내부 책임으로 유지한다.
  - 외부 observation을 그대로 recommendation이나 automatic tuning authority로 사용하지 않는다.

- IO / GC는 비핵심 축으로 유지한다.
  - 새로운 Guard 개발의 기본 전선으로 되돌리지 않는다.
  - 실제로 새로운 evidence가 생기지 않는 한 계측 / 관찰 이상의 책임을 추가하지 않는다.

## Next

- 핵심 안정화 경로의 **회귀 검증과 재잠금**을 수행한다.
  - tick / update 입력 경로가 current contract와 일치하는지 확인한다.
  - activation / early-exit / cooldown 상태 전이가 의도한 비개입·복귀 의미를 유지하는지 확인한다.
  - 안정화가 필요 없는 baseline에서 불필요한 개입이 발생하지 않는지 확인한다.

- Fuse의 current validation boundary를 정리한다.
  - sustained pressure와 burst를 함께 포함한 stress scenario를 둔다.
  - UI / container / 저부하 상황에서는 비개입 baseline을 확인한다.
  - multiplayer 환경에서는 소수 인원의 현실적인 혼합 부하를 대표 scenario로 사용한다.
  - 개입 발생 여부뿐 아니라 세션 지속성과 프레임 붕괴 완충 여부를 본다.

- 운영 검증은 **현실적이고 재현 가능한 소수의 representative scenario** 중심으로 유지한다.
  - OFF / ON 비교로 실제 개입과 baseline 차이를 확인한다.
  - 동일 세이브 / 동일 행동의 완전 재현보다 실사용 수준의 의미 보존과 안정성을 우선한다.
  - 통계적 certification을 별도로 목표로 하지 않는 한 대규모 반복 실험을 기본 방식으로 사용하지 않는다.

- Fuse 동결 상태를 설명하는 최소 문서를 정리한다.
  - current stabilization scope
  - validation boundary
  - activation / recovery 판독 기준
  - 금지선
  - public positioning

- 공개 포지셔닝은 **엔진 부하 폭주와 순간적인 스파이크로 인한 프레임 붕괴를 완충하는 안정성 레이어**로 유지한다.
  - AI optimization 또는 평균 FPS 상승 모드로 설명하지 않는다.
  - Pathfinding / Collision / Physics를 포함한 안정화 범위를 특정 AI 기능 하나로 축소해서 설명하지 않는다.

## Hold

- Fuse를 AI optimization mod / 평균 FPS 상승 모드 / sustained-load optimizer로 재포지셔닝하는 것
- 엔진 포크, 구조적 engine rewrite, 근사 또는 공격적 알고리즘 교체
- gameplay semantics나 AI 판단 결과를 바꾸는 방식으로 성능을 확보하는 것
- Echo나 다른 Spoke의 observation을 직접 의존하거나 실시간 행동 / recommendation / optimization policy 입력 계약으로 고착시키는 것
- Pulse를 거치지 않고 다른 Spoke의 내부 API / state / lifecycle을 직접 참조하는 것
- Fuse를 observation-driven automatic tuner로 확장하는 것
- IO / GC Guard를 핵심 판매 포인트나 메인 안정화 전선으로 복귀시키는 것
- B42 가능성만을 이유로 lighting / rendering / IO / GC 대응을 메인라인에 계속 유지하는 것
- Fuse 전용 policy interface / convenience command / product-specific state를 Pulse Core surface로 승격하는 것
- 동일 세이브 / 동일 행동 완전 재현이나 대규모 학술형 반복 실험을 기본 검증 방식으로 삼는 것
- 단일 metric이나 단일 diagnostic signal만으로 Fuse의 작동 / 실패 / 정책 변경을 판정하는 것
- 실전 검증 직후 미세 optimization이나 신규 고도화를 다시 메인 개발축으로 전환하는 것
- 안정화가 필요하지 않은 baseline에서도 지속적으로 개입하는 것

---

# 4. Nerve

## 목표

100% Lua 기반 **선택적 안정성 Guard**.

Nerve는 이벤트 재진입 / listener exception / network boundary incident가 세션 전체로 번지는 것을 **same-tick retreat / fail-soft / back-off / non-intervention** 방식으로 제한한다.

Nerve는 Lua 병목을 최적화하거나 게임 행동을 조정하는 모드가 아니라, 실제 사고가 발생했을 때 피해 반경을 줄이고 필요하면 즉시 철수하는 **dormant stability layer**로 둔다. 현재 active scope는 **Area 6 Event Dispatch와 Area 9 Network / Multiplayer boundary**이며, Area 5 Item / Inventory / Container / UI 축은 폐기된 영역으로 유지한다.

## Done

- Nerve의 **선택적 / dormant guard** 제품 경계를 확립했다.
  - 설치되어 있다는 이유만으로 상시 개입하지 않는다.
  - incident가 없는 상태와 조용한 로그를 정상 상태로 해석한다.
  - 개입은 문제를 더 영리하게 해결하는 것이 아니라 피해 반경을 제한하고 안전하게 후퇴하는 방향으로 제한한다.
  - `back-off / retreat / non-intervention`을 기본 행동 원칙으로 유지한다.

- Area 5 — Item / Inventory / Container / UI 안정화 축을 current scope에서 퇴역시켰다.
  - 해당 영역은 사례가 극히 드문 축으로 보고 active product development 대상에서 제외한다.
  - 과거 Area 5 구현 / 검증 흔적이 존재하더라도 current 기능 확장 근거로 사용하지 않는다.
  - Area 5를 Area 6의 보조 기능이나 재사용 가능한 일반 안정화 계층으로 되살리지 않는다.

- Area 6 — Event Dispatch Guard의 제품 경계를 고정했다.
  - 일반적인 event optimization이나 deduplication engine이 아니라 **same-tick self-recursion / listener exception의 피해 확산을 제한하는 최후 Guard**로 둔다.
  - default OFF / strict OFF를 기본 안전선으로 유지한다.
  - report / warning보다 실제 행동 변경을 최소화하고 conflict 상황에서는 더 복잡한 공존보다 back-off를 우선한다.
  - event priority / throttling / scheduling 같은 정책 엔진으로 확장하지 않는다.

- Area 9 — Network / Multiplayer Boundary Guard를 운용 검증 단계로 이동했다.
  - multiplayer optimization / ping improvement / packet control이 아니라 **network boundary incident 발생 시 same-tick retreat하는 보험 장치**로 유지한다.
  - 사건이 거의 없거나 전혀 없는 상태를 기능 부족이 아니라 정상적인 dormant success로 해석한다.
  - network 경계를 넘어 일반 UI / render / event 최적화 기능으로 확대하지 않는다.

- Nerve와 Nerve+의 제품 경계를 분리했다.
  - Nerve 자체는 **100% Lua** 안정성 Guard로 유지한다.
  - JVM 기반 편의 기능이나 Pulse 의존 기능이 필요할 경우 Nerve 자체에 흡수하지 않고 별도 `Nerve+` 제품 축으로 다룬다.
  - Nerve가 Nerve+를 전제로 해야만 동작하는 구조로 만들지 않는다.

## Doing

- 현재 핵심 전선은 **Area 6 실행 가능성 / runtime proof 복구와 Area 9 운용 검증**이다.
  - 새 trigger / 행동 / 정책을 추가하기보다 기존 guard가 실제 PZ Lua 환경에서 안전하게 동작하는지 확인한다.
  - syntax / entrypoint / exception boundary / fail-soft semantics를 current contract와 일치시키는 데 우선순위를 둔다.
  - 구현 복구 과정에서 event optimization이나 새로운 policy layer를 추가하지 않는다.

- Area 6은 최소 incident guard로 유지한다.
  - same-tick self-recursion과 listener exception만 intervention trigger로 제한한다.
  - 정상 event flow는 가능한 한 그대로 통과시킨다.
  - wrapper conflict나 예상하지 못한 integration 문제가 발생하면 복잡한 coexistence mechanism보다 Guard OFF / back-off를 우선한다.
  - Kahlua 제약 안에서 listener 단위의 최소 exception isolation만 허용한다.

- Area 9은 실제 multiplayer / modpack 환경에서 **조용한 운용 검증**을 우선한다.
  - incident가 발생할 경우 세션 지속성과 피해 반경 제한에 실제로 기여했는지를 본다.
  - incident frequency를 높이거나 기능 발동을 보여주기 위해 인위적으로 aggressive하게 개입하지 않는다.
  - incident가 거의 없다면 새로운 trigger를 만들기보다 현재 dormant 상태를 유지한다.

- Nerve는 최소 상태와 incident evidence만 소유한다.
  - 최소 guard state / incident marker / error signature 정도만 노출한다.
  - 자체 분석 리포트 / recommendation / 원인 판정 시스템을 구축하지 않는다.
  - 다른 Spoke의 내부 state / implementation / lifecycle에 직접 의존하지 않는다.
  - 공통 기반 capability가 필요하면 Pulse의 중립 surface를 통해서만 소비한다.

## Next

- Area 6의 **실행 기준선과 진입점 계약**을 정리한다.
  - Lua syntax와 runtime loadability를 확인한다.
  - event guard의 canonical entrypoint를 하나의 명확한 경로로 정리한다.
  - fail-soft / exception propagation / back-off 의미를 코드와 문서에서 일치시킨다.
  - stale diagnostic / experimental residue가 current behavior처럼 읽히지 않도록 정리한다.

- Area 6의 current guard path를 최종 검수한다.
  - default OFF / strict OFF 의미를 보존한다.
  - same-tick self-recursion / listener exception 이외의 일반 event activity를 intervention trigger로 확대하지 않는다.
  - 정상 flow에서는 passthrough를 유지한다.
  - wrapper conflict에서는 automatic resolution보다 Area 6 OFF / retreat를 우선한다.
  - listener isolation은 PZ Kahlua 환경에서 가능한 최소 `pcall` 경계를 사용한다.

- current operational debt를 정리한다.
  - 실제 incident가 발생하는 listener / entrypoint를 식별할 수 있게 한다.
  - 반복 incident가 확인되면 Nerve 전체 정책 확대보다 해당 listener의 correction 또는 bounded isolation을 우선한다.
  - Guard를 다시 비활성 상태로 복구할 수 있는지를 확인한다.
  - obsolete debug / exception-handling residue를 current path에서 제거한다.

- Nerve validation boundary를 정리한다.
  - Guard trigger가 실제로 발동할 수 있음을 증명한다.
  - Guard OFF 상태에서는 설치 전과 동일한 기본 behavior를 유지하는지 확인한다.
  - intervention 이후 정상 상태로 후퇴 / 회복하는 의미를 확인한다.
  - 최소한의 reproducible incident scenario와 recovery 판독 기준을 정리한다.
  - validation을 일반적인 Lua performance benchmark나 optimization certification으로 확대하지 않는다.

- current 제품 문구와 Nerve / Nerve+ 경계를 정리한다.
  - Nerve를 incident research framework나 분석 시스템처럼 설명하지 않는다.
  - 자기 제한 / dormant guard / back-off 원칙을 public description에 반영한다.
  - Nerve와 Nerve+의 runtime / dependency / distribution 경계를 문서화한다.
  - `Lite / Full`처럼 하나의 제품이 단계적으로 확장되는 것처럼 보이는 표현을 사용하지 않는다.

- Area 9의 운용 검증을 계속한다.
  - 실제 multiplayer / modpack environment에서 incident 여부를 관찰한다.
  - incident 발생 시 same-tick retreat가 세션 지속성과 피해 제한에 기여했는지를 확인한다.
  - 사건이 거의 없으면 새로운 network policy나 trigger를 추가하지 않고 정상 성공으로 닫는다.

## Hold

- Nerve를 Lua performance optimizer / Lua bottleneck optimizer / 필수 성능 모듈로 재포지셔닝하는 것
- Area 5 Item / Inventory / Container / UI 안정화 축을 current product scope로 재개방하는 것
- `drop / delay / defer / reorder / queue`처럼 정상 event 또는 network behavior의 순서와 의미를 변경하는 정책
- 의미 기반 allowlist / denylist / whitelist / always-allow 같은 gameplay-aware policy를 도입하는 것
- event priority / governor / throttler / scheduler 등 일반적인 event-control framework로 확장하는 것
- wrapper chain의 복잡한 coexistence / interception architecture를 기본 방향으로 삼는 것
- same-tick incident containment을 넘어 시간 기반 debounce / cross-tick cache / visibility-driven intervention 같은 정책으로 확대하는 것
- 서로 다른 Guard 영역이 mutable state나 implementation을 직접 공유하도록 결합하는 것
- Nerve 자체에 분석 리포트 / recommendation / root-cause engine을 구축하는 것
- Nerve의 product-specific guard / policy logic을 Pulse Core로 상향 이동하는 것
- 다른 Spoke의 내부 API / state / implementation에 직접 의존하거나 다른 Spoke의 자동 정책과 Nerve를 직접 결합하는 것
- Nerve 자체에 JVM / Java / Mixin product logic을 추가해 Nerve+ 경계를 흡수하는 것
- Area 8 Save / IO 또는 Area 10 GC / Memory를 Nerve의 새로운 안정화 전선으로 여는 것
- Area 9를 multiplayer optimization / packet control / latency reduction / ping improvement 기능으로 확장하는 것
- Area 9에서 전역 상시 protected-call, 영구 차단, 자동 blacklist / whitelist를 기본 behavior로 만드는 것
- Area 9를 network boundary 밖의 일반 event / UI / render 안정화 축으로 확대하는 것
- incident frequency / ratio / weight / trend를 기반으로 intervention을 점점 공격적으로 만드는 policy engine을 도입하는 것
- historical research framework / rejected predecessor terminology를 current 제품 구조나 authority로 되살리는 것
- 실행 가능성 / entrypoint / fail-soft contract가 정리되기 전에 새 trigger / 행동 / 정책을 추가하는 것

---

# 5. Iris

## 목표

100% Lua 기반 **근거 기반 게임 내 위키형 정보 모드**.

오프라인에서 봉인한 fact / outcome / source / description을 런타임에서 해석·추천·비교하지 않고 안정적으로 표시한다. Iris는 아이템이 무엇이고 어떻게 쓰이는지는 설명하지만 사용자가 무엇을 선택해야 하는지는 판단하지 않으며, 충분한 근거가 없으면 추측해서 채우지 않는다.

## Done

- Browser 검색 관련성·공백 처리를 구현하고 입력·분류 탐색 후속을 사용자 확인 범위에서 완료했다. (2026-08-31)
  - 정확한 표시 이름을 부분 일치와 ID-only 결과보다 우선한다. U+0020 공백 차이를 흡수하며 global 표시 이름/ID 검색과 local 대표 표시 이름 검색의 범위, FullType identity와 기존 variants를 유지한다.
  - Generation/locale snapshot과 prefix 후보를 같은 비교 규칙으로 연결했다. Edit buffer 변경을 callback/update에서 반영해 이른·누락된 붙여넣기 callback을 보완하며 같은 입력은 재검색하지 않는다.
  - 정확한 이름·ID의 분류 위치가 명확하면 대분류·소분류를 자동 선택하고 전체 결과를 유지한다. 전체 검색어 삭제 시 대분류 목록만 있는 초기 화면으로 돌아오며 분류 직접 클릭으로 탐색을 이어갈 수 있다.
  - 기존 Browser 통합 검사(KO/EN exact-name sweep과 상태·선택 회귀 포함), Lua syntax와 package 자체 검사를 통과했다. 저장소 내부 `.tmp/package/` staging을 허용했고 최종 전달물은 `.tmp/package/4/Iris` / `Iris.zip`이다. Source 보호·기존 package 검사와 조건부 Clean-Checkout 계약은 유지했다.
  - 사용자가 package/4의 붙여넣기 후 분류 자동 선택, 삭제 후 초기화, 검색 중 분류 직접 탐색을 정상 확인했다. 앞서 검색어 확정 후 `망치` 결과 일치, 목록 내 검색·ID 검색·재열기·언어 변경 정상도 보고했다. 에이전트의 실제 게임 실행이나 전체 환경·성능 검증으로 확대하지 않는다.
  - 마지막 한글 음절의 조합 확정 지연은 미해결 입력 경계이며 초성·어순 변경·다른 언어 alias·fuzzy는 미채택이다. 이를 이번 후속의 재시험·새 Gate 의무로 늘리지 않는다. 최종 범위와 predecessor 판정은 [단일 검색 closeout](iris_korean_item_search_relevance_normalization_runtime_consistency_closeout.md)을 따른다.

- DVF 기본 설명 교정과 Tooltip S2 전파, 관련 Menu 보완을 원본 저장소에 반영했다. (2026-08-31)
  - 전체 2,105개를 판정하고 revise 1,529 + reduce 12 = **1,541개**의 기본 설명·KO/EN을 교정했다. Tooltip S2 core는 **1,314 → 2,048(+734)**, KO/EN public body는 각 2,099개다. 보호 12개와 explicit owner absence 175개를 보존했다.
  - 이름·현실 용도나 넓은 분류 label 대신 exact Build 41 source에 근거해 기본 용도·효과를 설명한다. 이번 구현은 개별 facts/decisions/approved candidate 교정이며 공통 설명 블록 조합 규칙의 재설계는 아니다.
  - 32개 Menu 항목의 후속 질문에 준비물·사용 조건·조리 단계 등을 보완했다. 조리·낚시는 기존 Menu context로 답하며 신규 QG/Recipe 구조를 만든 것은 아니다. 기술서 적용 레벨·독서 조건은 Browser/Wiki에 표시한다.
  - 새 generation과 EN → T1 → T2 fixed → matching Recipe companion → package/격리 runtime까지 전파하고 기존 필수 자동 검증을 완료했다. 옆 배치·구체적 Recipe 표시 후속도 새 패키지에 포함했다. 해당 DVF 작업의 전달물은 `C:/Users/MW/PZ-U/pkg2/Iris` / `Iris.zip`이며 이후 검색 수정 전달물과 구분한다.
  - 사용자가 위 폴더를 설치하고 **식품류**의 Alt·우클릭 상세 정보, KO/EN 장문 배치, Recipe 표시·Menu 전환이 정상이라고 보고했다. 비식품류 전체 관찰이나 모든 문장의 의미·유용성 승인으로 확대하지 않는다.
  - 추가 독립 Gate/검증기를 만들지 않고 기존 검사와 적합한 실행 결과를 재사용했다. 일회성 authoring/delta helper는 정규 검사기나 새 authority가 아니다.
  - 상세 판정·실행 결과·사용자 관찰은 [단일 closeout](iris_dvf_description_usefulness_tooltip_s2_menu_depth_plan_closeout.md)에 둔다. 아래 T1/T2/T3의 과거 수치·패키지는 해당 subject의 이력이며 현재 전달물과 구분한다.

- DVF shared composition successor와 기술서 획득 정보·장문 표시 후속을 구현했다. (2026-08-31 ~ 2026-09-01)
  - 기존 seven-input 안에서 source-bound shared / explicit / retained 경로와 KO/EN core 공동 소비를 연결했다. Shared 193개 + explicit 6개를 개선하고 1,906개는 근거에 따라 유지한다.
  - Universe 2,105, public 각 2,099, S2 core 2,048/empty-core 57, owner absence 175와 기존 보호·hold·silent를 유지한다. 이전 1,541개 교정이나 core 증가를 이번 성과로 중복 계상하지 않는다.
  - 같은 source slot에 결속된 기술서 55개 `Base.Book*`의 Menu 상세에 학교·서점·도서관·가정집 책장·책 상자·우체국·우편 차량 획득 장소를 KO/EN으로 추가했다. 이름·classification으로 다른 item family의 획득처를 추론하지 않았고 Tooltip S2 coverage도 바꾸지 않았다.
  - Browser detail은 폭 기준 줄바꿈의 실제 높이를 기존 scroll 범위에 반영하고, Wiki는 고정된 제목·닫기 버튼 아래의 본문 child panel이 누적 본문 높이를 스크롤하도록 변경했다. Alt Tooltip의 자동 크기·배치는 유지했다.
  - 최종 generation `dvf33-ed92fa5c9ed4a1ed367f5d79365d04e1996e36a05d76a33bd7b8dd2176e7f82f`를 T1/T2와 current-only package까지 채택했다. 사용자는 실제 PZ에서 최종 패키지의 KO/EN 장문이 모두 잘리지 않고 읽힌다고 확인했다. 이 관찰은 확인한 장문 surface와 locale에 한정한다.
  - T1/T2·패키지 검증의 실제 결과와 전달 경로는 [단일 closeout](iris_dvf_shared_composition_usefulness_menu_tooltip_plan_closeout.md)에 둔다. 실제 사람의 전체 exact-candidate 문장 검토는 수행하지 않았으며 이전 식품류 관찰을 이번 결과로 중복 승계하지 않는다. 일회성 authoring helper는 새 validator가 아니다.

- Iris의 제품 정체성과 사용자-facing 정보 원칙을 current 기준으로 고정했다.
  - 확인된 사실은 이해하기 쉽게 설명할 수 있지만 해석 / 추천 / 효율 평가 / 우열 비교는 하지 않는다.
  - 충분한 근거가 없는 정보는 추측해서 채우지 않고 침묵한다.
  - 사용자-facing surface는 **Iris 메뉴와 Iris 툴팁(Alt) 두 가지**로 제한한다.
  - Browser / Detail / Wiki는 Iris 메뉴 내부 view로 두며 독립된 product surface로 취급하지 않는다.
  - Iris 메뉴와 Iris 툴팁은 같은 사실을 서로 다른 깊이로 표시하며 서로 모순되지 않게 한다.
  - PZ에서 실행되는 Iris runtime은 **100% Lua**로 유지한다.

- 정보 표시 위계와 각 계층의 역할을 정리했다.
  - 기본 위계는 **기본 정보 → 의미 → 활용 → 메타**로 유지한다.
  - `primary_subcategory`와 분류 정보는 추천이나 우열 판단이 아니라 browsing / metadata 용도로 제한한다.
  - Layer 3는 confirmed description material이 있을 때만 제공하는 **선택적 설명 계층**으로 유지한다.
  - core description과 acquisition information은 서로 다른 source-bound fact로 관리한다.
  - Layer 4는 Recipe / Right-click 상호작용의 표시를 담당하며 정보량에 따라 presentation을 조정한다. Build 41 `EvolvedRecipe`는 item-property의 `ingredient`/`spice`와 전체 definition `BaseItem` 38개를 별도 `base_item` typed relation으로 구현했다. 공개 relation은 2,203개/252 FullType이며 definition base는 32 unique FullType, non-Food 17 occurrence/13 unique다. 첫 candidate의 fixed density 회귀, v2의 KO 손상·ID 노출, v3의 definition 누락, v4의 fragment display·EN Recipe click FAIL과 v5의 관찰 전 superseded 상태를 predecessor 이력으로 보존한다. Exact 38 target registry, action-oriented KO/EN 문장, Recipe section state와 item 전환 격리, 자연화한 KO `base_item`을 적용한 v6는 사용자 실제 PZ 대표 관찰과 guarded adoption을 완료한 `observed_pass / adopted` current runtime이다. 채택 SHA-256은 `0b86cb8a2638df627f94bbb27af759b9b46e54c55081504da04aefcc8e353088`이다.
  - Recipe와 Right-click은 서로 독립적이고 동등한 활용 정보 축으로 유지한다.

- Evidence / Source / Outcome 모델을 결과 상태 중심으로 고정했다.
  - Evidence는 느슨한 행동 가능성이나 capability 일반화가 아니라 **확인된 결과 상태를 뒷받침하는 근거 체계**로 유지한다.
  - Recipe / Right-click / Static capability / Context Outcome은 서로 다른 Source 계열로 유지한다.
  - Context Outcome은 문서 기반 사실을 기계화하는 오프라인 공급자로 두고 runtime은 그 결과만 소비한다.
  - Right-click evidence는 메뉴 존재가 아니라 `item-dependence + state-change proof`를 기준으로 판정한다.
  - canonical 상태 변화 기준은 `executing_tool + external_target + persistent_change`로 유지한다.
  - 넓은 capability label이나 느슨한 행동 가능성을 기본 evidence 축으로 확장하지 않는다.

- 오프라인 생성과 runtime 표시의 책임 경계를 current architecture로 고정했다.
  - 승인된 fact / decision / profile / body plan으로 public body를 결정론적으로 생성·검증하는 책임은 오프라인 생성 계층에 둔다.
  - current generation은 오프라인에서 완성한 뒤 stateless하게 검증하고 immutable generation으로 설치한다.
  - current generation 전환은 단일 pointer를 통해 수행한다.
  - runtime은 current generation에 봉인된 fact / outcome / source / description과 locale payload를 소비하고 표시하는 계층으로 제한한다.
  - runtime에서 사실을 다시 추론하거나 설명을 재작성하거나 사용자 행동을 추천하지 않는다.
  - 퇴역한 stateful artifact-registry 구조와 predecessor generation은 current product dependency로 사용하지 않는다.

- current runtime / package / responsibility 구조를 정리했다.
  - generated description payload는 chunk 기반 lazy lookup 구조로 유지한다.
  - Browser / Detail 등 Iris 메뉴 내부 view의 data ownership과 presentation responsibility를 분리했다.
  - public-text production, Right-click evidence pipeline, generation / package, menu presentation, compatibility의 current owner를 분리했다.
  - supported public / compatibility surface는 보존하면서 legacy implementation dependency를 격리했다.
  - current package는 current generation에 필요한 payload만 포함한다.
  - historical generation, legacy fixed payload와 predecessor artifact를 current package / runtime fallback으로 사용하지 않는다.

- Layer 3 / Layer 4와 KO / EN presentation을 current information pipeline에 통합했다.
  - Layer 3 current body와 locale companion payload는 같은 current public information set에 결속한다.
  - KO / EN은 같은 semantic source의 locale별 payload를 사용한다.
  - 지원 locale에서 알려진 정보를 숨기거나 다른 locale의 raw text를 fallback으로 노출하지 않는다.
  - adaptive presentation은 정보량에 맞는 표시 방식만 결정하며 interaction의 의미나 우선순위를 판단하지 않는다.
  - 알려진 Layer 3 material gap과 locale projection mismatch correction을 current generation에 반영했다.

- public-text / semantic quality / validation의 current 책임 경계를 정리했다.
  - public-text 생성·검증과 runtime presentation을 분리한다.
  - historical rendered output이나 predecessor public text를 current generation의 암묵적 입력으로 사용하지 않는다.
  - semantic quality는 offline / internal signal로 유지하며 사용자-facing recommendation / sorting / filtering / hiding / trust signal로 사용하지 않는다.
  - temporary / one-off / lifecycle-only validation executable을 regular authority에서 퇴역시켰다.
  - regular validation은 current product contract와 validation-system contract를 보호하는 최소 boundary로 정리했다.
  - 중복 execution을 통합하면서 contract identity와 failure attribution을 보존했다.
  - validation / tooling execution은 source working tree와 current product artifact를 암묵적으로 변경하지 않는 경계를 사용한다.

- current functional acceptance와 readiness의 책임 축을 분리했다.
  - supported Iris-only PZ 환경에서 boot / save load, Iris 메뉴 내부 Browser / Detail / Wiki view, Iris 툴팁과 주요 Recipe / Right-click 경로의 practical in-game acceptance를 완료했다.
  - 이 acceptance를 모든 외부 모드 compatibility의 증거로 확대하지 않는다.
  - architecture / validation / functional acceptance와 freeze / RTC / Publish / release / Workshop / deployment readiness는 서로 별도 축으로 유지한다.

- Build/validation execution과 current-authority 탐색 최적화를 `complete by owner disposition`으로 닫았다.
  - Supported execution boundary를 typed phase I/O, stable canonical semantic result와 volatile execution envelope로 분리하고 두 StageRunner를 thin package-owned `PhaseRunner`에 수렴했다.
  - Full-gate current-output seed producer invocation을 `6 → 3`으로 줄이면서 immutable seed, case-local clone과 fresh-process A/B isolation을 유지했다.
  - Predecessor accounting은 `31 substantive distinct basenames + nested D16 extra copies 2 = 33 concrete predecessor files`이며 live intersection `31 → 0`, concrete files `33 → 0`, `5 exact + 28 diverged`로 닫았다.
  - 당시 human command owner, current authority explanation owner와 최대 route hop은 각각 `4 → 1`; default current-context tracked bytes는 `170,476 → 149,600`이었다. 2026-08-31 사용자 요청으로 별도 AGENTS/ENTRYPOINTS 문서는 퇴역하고 핵심 문서·해당 계획·실제 명령 구현을 직접 참조한다. 앞의 수치는 이전 구조의 측정 기록이다.
  - Round3 routing membership은 `103 → 103`; canonical full gate는 pytest `211 → 211`, standalone `4 → 4`, recurring execution unit `215 → 215`다. 두 분모를 합치거나 regular test 108개 추가로 읽지 않는다.
  - G5 0016과 0017은 closure bytes/set 변경에 따른 append-only successor이며 과거 chain을 재번호링하지 않았다. Retention-list correction은 새 identity가 아니므로 0018을 만들지 않았다.
  - Exact wheel/fresh environment, Run A/B, comparator와 independent Reviewer가 PASS했고 product/runtime/Lua mutation은 0이다.
  - Pre-implementation W0 `ADMIT` artifact 미보존은 unresolved 사실로 남지만 owner가 disposition하여 plan-process closeout은 complete다. 새 owner instruction이나 새 current authority 없이 이를 후속 blocker 또는 재실행 항목으로 되살리지 않는다.
  - 상세 readpoint는 `docs/iris_build_validation_execution_current_authority_optimization_plan.md`, `docs/iris_build_validation_execution_current_authority_optimization_walkthrough.md`, `docs/iris_build_validation_execution_current_authority_optimization_closeout.md`다. Physical Git blob/context 감소는 runtime/token 성능이나 release readiness claim이 아니다.

- Tooltip T1 표시 계약과 upstream input readiness boundary를 owner-ratify했다.
  - 2026-08-29 successor amendment로 S1=optional applicable Layer 2, S2=optional Layer 3, S3/S4=Layer 4인 0~4 logical-row contract를 채택했다. Layer 2가 applicable하지 않으면 placeholder 없이 S1을 생략하고 S2~S4를 compact한다.
  - Layer 4 identity selection을 locale/Menu readiness보다 먼저 freeze하고 Recipe/Right-click source equivalence, identity-first KO/EN과 no-fallback을 고정했다.
  - Current support universe 전체를 같은 contract로 audit하는 installed `iris_tooling` producer와 minimal T2 handoff boundary를 추가했다.
  - D1 successor는 support `2,280`을 Layer 2 applicable `1,406` / legitimate display silence `874`로 exact partition했다. Silence는 raw fallback `408`, no membership `201`, no admissible primary `265`에서 deterministic하게 산출하며 semantic 분류 추론이나 per-row absence authority를 만들지 않는다.
  - 기존 resolved `1,406`은 byte/identity/surface 불변이며 Classification correction은 `874 → 0`으로 닫혔다. D1은 이 exact partition을 D2 consumer-relation 입력으로 제공한다.
  - T1-D2는 actual Lua full-set observation으로 support `2,280` coverage를 exact 확인하고 Menu relation을 `verified 1,406` / `not_applicable 874` / `correction_required 0`으로 닫았다. Applicable/N/A ordered-set hash는 각각 `c5a77d86eb875cecf03edf5ab67f29361f58947bd97493e522667b593130f264` / `d13fa6ac9072a3ab2c61bc59990bfb948010ce8b2fc3211aa1ecb7b5c6c121de`다.
  - D2 Browser correction은 accepted explicit primary의 tag/location 정렬에 한정된다. Actual navigation delta는 `26`, display-silence surface delta와 D1/D3/D4/D5 protected delta는 `0`; malformed/non-membership primary는 fail-loud하고 no-explicit-primary behavior는 보존한다.
  - D2 candidate whole-T1 re-audit는 correction `0`, progression `OPEN`을 산출했다. Focused Tooltip suite `90 passed`, Browser owner direct unittest `2 tests OK`, Lua syntax `127 files OK`, relation materializer Run A/B bytes 동일을 확인했지만 이 결과는 isolated subject에 한정되며 global current adoption과 production T2 handoff는 T1-D6 전까지 열지 않는다.
  - D1 successor subject `8bbc40169e86bd2e818c440a823e497f852a1e69` / tree `e950a552797012e6e40523e75b93a1ed203e839b`는 workstream `complete`다. T1-C common predecessor `6b7118dc229bf8138302696e1aa5e5b7454589dc`에서 final successor까지의 corrected cumulative external bundle 하나가 D6-ready active input이며 intermediate bundle은 inactive lineage다.
  - T1-D6 integrated subject `b30aaff2da6172ab5137c55bb460889aa527ad04` / tree `7cdd52fd61f739b5018a62d8bffe84461dfea50c`가 D1~D5/D2 결과를 same-subject whole-T1 audit로 재결속했다. Final current 상태는 correction/blocker `0`, `T2_FULL_DATA_PROGRESSION=OPEN`, production handoff present다.
  - T1-D5는 `Base.LemonGrass`와 `Base.Lemongrass`의 case-sensitive exact support identity와 raw normalized-collision observation을 보존하면서 target `SUPPORT_NORMALIZED_COLLISION` correction/T2 blocker만 `2 → 0`으로 닫았다. Support는 `2,280 → 2,280`, 전체 correction은 `5,625 → 5,623`, non-target delta는 `0`이다.
  - D5 support-freeze hash는 common LF-terminated UTF-8 ordered-set 규칙으로 `3a6cc24b9ad64e06a0a6c0408821201e35bbd1d8558e6245809b5d3c34265ce6`을 재도출했다. 최초 JSON-array hash mismatch는 exact set missing/extra 0인 serialization-only mismatch로 정정했으며 corrected bundle만 D6 입력 후보이고 최초 bundle은 superseded다.
  - T1 contract/audit completion은 static Tooltip Lua generation, runtime adoption/visual fit, package, compatibility 또는 release readiness가 아니다.
  - 2026-08-28 corrective subject `6b7118dc229bf8138302696e1aa5e5b7454589dc`에서 focused 6-family `62 passed`, installed candidate invariant, canonical Run A/Run B와 deterministic comparator가 모두 exit 0이었고 post-gate finalizer가 `complete/complete` closeout을 생성했다.
  - `Base.LemonGrass` / `Base.Lemongrass` normalized collision blocker 2건을 복원하고, DVF owner의 Menu consumer self-attestation을 제거했다. Layer 3 selected `1,314`건은 shared-authority relation만 확인된 `unverified_without_independent_consumer_evidence`이며 T3 재검증 대상으로 남는다.
  - 최초 correction `7,111` 중 authority가 실제로 닫은 범위는 DVF fact readiness `1,314`와 current right-click locale `172`, 합계 `1,486`이다. 최종 T2-blocking correction은 `5,625`이며 production T2 handoff input/manifest는 `0`이다.
  - T1-D3 parallel workstream은 frozen exact `DVF_OWNER_ROW_MISSING` 175건을 owner-approved legitimate absence로 닫았다. Workstream distribution은 `A=0`, `B=175`, blocked `0`이고 target SHA-256은 `accbe1ae691e41b1697f080f26b8206a08e261039bb7919879f67f4b5d7ef238`다.
  - D3 candidate whole-T1 re-audit는 support `2,280`, correction `5,450`, D3 owner-row missing `0`을 산출했다. 기존 fact `1,314`, empty-core `791`, current generation/pointer, Layer3English와 Lua runtime은 변경하지 않았다.
  - Focused Tooltip T1 tests `65 passed`, candidate Run A/B 동일 receipt, independent defect-exclusion/non-target invariance와 diff hygiene가 exit `0`이다. New test file/top-level test function delta는 `0`이다.
  - T1-D3 workstream bundle은 `complete`지만 current ecosystem adoption은 `pending_T1_D6`다. 따라서 integrated current blocker `5,625`, `BLOCKED_BY_UPSTREAM_CORRECTIONS`와 production handoff `0`은 D6 전까지 유지한다.
  - T1-D4 parallel workstream은 frozen selected Recipe instance 444건, exact identity 266개에 QG-approved KO/EN pair를 제공해 candidate `LOCALE_SELECTED_SURFACE_MISSING` 888건을 `0`으로 닫았다. Selection identity/order, source distribution, Right-click route와 other-owner ledger는 변경하지 않았다.
  - D4 candidate whole-T1 re-audit는 support `2,280`, correction `4,737`을 산출했다. Focused Tooltip T1 tests `67 passed`, materializer Run A/B bytes 동일, exact reconciliation/whole audit/protected-path/bundle validation exit `0`이다.
  - D4 support freeze는 predecessor exact set과 missing/extra `0`으로 같고 canonical ordered-set SHA-256은 `3a6cc24b9ad64e06a0a6c0408821201e35bbd1d8558e6245809b5d3c34265ce6`이다. 초기 JSON-array hash binding은 serialization-only 오류였으며 corrected external bundle/receipt로 교체했다.
  - T1-D4 bundle도 `complete`지만 current ecosystem adoption은 `pending_T1_D6`다. D3/D4 candidate correction 수치는 독립 predecessor 결과이므로 서로 합산하거나 current blocker `5,625`를 대체하지 않는다.
  - T1-D6 strict handoff는 exact `2,280` rows이며 input SHA-256 `138b6f4ef85a2235fa41e6d60d88e885c6f6f93a8bb0458a7d6ac4dce7af56ac`, manifest SHA-256 `15a4a089fdde7eeb70fd0f1e21d77872b90fdaec8130d45605edac52d67fb892`로 current route에 채택됐다.
  - Fresh wheel/installed CLI, canonical Run A/Run B, deterministic comparator와 기존 finalizer가 모두 exit `0`이다. Final closeout SHA-256은 `f8d6bcbef0e71d57fe36be36504a5ffcea1696953b7d8280deeba911fdcecab6`이고 상태는 `complete / complete / OPEN / present`다.
  - Canonical final root는 repository-external `C:/Users/MW/Downloads/coding/PZ-tooltip-t1-d6-final-b30aaff2`다. Path correction carrier `8e972950b7b699b435d9b21e54432af94fc42f53` 이후 installed current readback이 exit `0`으로 `adopted / complete / complete / OPEN / present`를 확인했으며, 선행 내부 `.tmp` materialization은 superseded ephemeral output이다.
  - Windows directory publish blocker는 generation bytes나 manifest visibility 의미를 바꾸지 않는 `shutil.move` fallback으로 닫았다. T1-D6 완료를 위해 사용한 exact machine subject와 canonical receipt chain은 경로 정정 과정에서 재실행하거나 재결속하지 않았다.
  - 이 T1-D6 당시 완료는 upstream input과 T2 handoff 경계만 열었다. 이후 static Lua staging은 아래 T2 successor에서 완료했으며, runtime/visual 검증과 release readiness는 여전히 별도 gate다.

- Tooltip S1 표제 보완과 T2 결정적 KO/EN static staging을 완료했다. (2026-08-30)
  - T1 successor `60796744`에서 승인 category/primary 표제 1,406개를 완성했다. Support 2,280, display silence 874, classification identity와 S2–S4를 보존했고 focused 95·canonical A/B·comparator·기존 finalizer가 exit `0`이다.
  - T2 machine subject `d64692ac`에서 2,280개 KO/EN 배열을 생성했다. 0~4줄 분포는 `367 / 825 / 895 / 137 / 56`; 생성 실패·contract 위반·고정 금지 표현 hit는 `0`이다.
  - T2 focused 18, fresh installed inspect, generation A/B, 생성 Lua syntax 1-file, canonical full gate (`211 passed, 109 subtests passed`)와 finalizer가 exit `0`이다. A/B 및 candidate/final bytes가 동일하다.
  - Final root는 `C:/Users/MW/Downloads/coding/PZ2/t2-final`이며 Lua·manifest·closeout 세 파일을 제공한다. `dd17d447` carrier로 선택 저장소에 반영했고 기존 사용자 변경, runtime/package 및 보호된 owner 데이터는 보존했다.
  - 환경·경로 실패와 초기 T2 physical hash 처리 교정은 실행 계획의 기록에 남겼다. 성공한 T1 gate를 T2 수정 때문에 반복하지 않았고, 새 validation authority나 추가 봉인 체계는 만들지 않았다.

- Tooltip T3 static-data Alt runtime 통합을 완료했다. (2026-08-30, `complete`, `runtime_adopted=true`)
  - 완료 후 **옆 배치 source 구현을 완료**했다. 오른쪽 우선·왼쪽 대안, 4px 간격/top alignment, 내용 기반 240~360px 읽기 폭이며 vanilla 크기·위치와 기존 font는 유지한다. 양옆에 읽기 폭이 없으면 아래/위 배치, 안전한 공간이 없으면 Iris만 생략한다. 기존 focused harness와 Lua syntax 153 files가 exit 0이었다. 사용자는 수정됐다고 응답했으며 에이전트의 PZ 시각 검증으로 기록하지 않는다.
  - 이어 **구체적 Recipe 표시 source 구현을 완료**했다. 양배추 전용이 아니라 현재 승인 Recipe 연결 아이템 **349개 전체 / 781개 아이템별 후보**에 적용한다. 새 opening마다 하나를 무작위 선택하고 열린 동안과 locale 전환 중에는 동일 identity를 유지한다. Alt 해제·item 전환·숨김·context menu 표시 뒤 다시 고른다. 후보 하나는 고정되고 연속 동일 선택도 허용한다.
  - Recipe companion은 L2/L3·선택된 Right-click·0~4줄과 옆 배치를 보존하며 concrete Recipe 이름 하나를 담은 완성 KO/EN 배열들을 제공한다. 사용자 승인 이름 결손 후보 3개만 양 언어 공통 제외했다. 기존 fixed static data는 변경하지 않았고 runtime은 QG/raw 의미를 재생성하지 않는다. 초기 T3의 무상태 fixed 조회는 이 opening 상태에 한해 변경했다. 전역 FullType display cache나 legacy semantic fallback은 없다.
  - Recipe 후속 당시의 projection 검사 `1 passed`, runtime harness(전체 349개/781개 KO/EN 후보 및 opening lifecycle), Lua syntax `154 files`는 모두 exit 0으로 완료했다. 당시에는 실제 게임 관찰 결과가 없었다. 현재는 위 2026-08-31 교정본의 별도 필수 검증과 식품류 사용자 관찰 결과를 사용하며 과거 PASS를 승계하지 않는다.
  - 두 후속의 최초 전달은 source-only였고 아래 기존 `p2/Iris.zip`에는 포함되지 않았다. 현재는 renderer·lookup·fixed/Recipe companion을 새 `PZ-U/pkg2/Iris`에 함께 반영했다. 최초 후속의 상세 기록은 T3 계획에, 현재 전파 결과는 위 DVF 교정 closeout에 둔다.
  - 실제 Alt 오류 보고 뒤 Kahlua에 없는 `next` 의존을 `pairs`로 수정하고 기존 harness에 해당 환경 조건을 반영했다. Final code `25318630`의 canonical A/B는 각각 211 tests·109 subtests 및 기존 standalone 4개가 통과했고 comparator도 PASS다. 수정본 설치 syntax 129 files와 lookup smoke 2,280 keys도 통과했다. 이전 subject의 PASS를 수정본에 승계하지 않았다.
  - 당시 정상 수정 ZIP은 `C:/Users/MW/PZ-T3/p2/Iris.zip`, 격리 설치본은 `C:/Users/MW/PZ-T3/game/mods/Iris`였다. 사용자는 안내 버전 설치·KO/EN Alt 열기·Alt 해제·빠른 전이·관찰한 장문/정보 순서를 확인했고, 이 범위로 인게임 검증을 종료했다. 실제 오류 상황 검증은 사용자 지시로 제외했으며 미실행을 PASS로 기록하지 않는다. 이 predecessor T3의 전수 QA·성능·release/Workshop readiness는 비주장이고 잔여 재검사 요구는 없다.
  - 2026-08-30 D1 C 구현으로 기존 12개 Menu body를 복구하고 final KO/EN required 1,314개를 모두 연결했다. EN method는 current deterministic derivability이며 resolved 1,314 / retained 0 / unresolved 0이다. 기존 1,302개, Tooltip surface와 absence 175개는 보존됐다. L4 selected 530개는 양 locale의 실제 structured consumer subset에 일치했다.
  - 이후 사용자 Build 41 수정안이 위 입력을 supersede했다. 최신 12개 source/core/S2 정정을 T1·T2 최종본과 product까지 전파했고, 두 단계 canonical A/B·comparator 및 최종 actual Menu relation이 모두 PASS해 **D1 complete**다. Initial 1,314 pair는 12개 fact-ID successor와 함께 resolved 1,314 / retained 0 / unresolved 0으로 닫혔으며 required FullType·비대상 S2·L2/L4·0~4줄 분포를 보존했다. 후속 T3에서 package/ZIP/격리 install의 byte identity 및 설치본 syntax/lookup은 확인했다. 최신 사용자 관찰과 인게임 범위 종료는 위 완료 상태를 따른다. 이전 partial/runtime_adopted=false는 predecessor 이력이며 성능·release readiness는 선언하지 않는다. 상세 current binding은 D1 계획과 `docs/iris_tooltip_t3_static_data_alt_runtime_integration_plan.md` 실행 기록을 따른다.

## Doing

- DVF 교정의 구현 완료와 관찰·근거 한계를 분리해 유지한다.
  - 구현·자동 검증·최종 패키지의 식품류 사용자 확인은 완료 기록으로 유지한다. 단일 closeout의 overall 상태는 다른 major category의 대표 관찰 미보고 때문에 `partial`이며 제품 반영 실패를 뜻하지 않는다.
  - source review_hold 273개는 명시된 sprite/obsolete/legacy/identity 등의 근거 부족을 보존한다. 보류 수 자체는 미완료 사유가 아니며 keep·검증 완료·용도 없음으로 바꾸지 않는다.
  - 인게임 확인은 사용자가 진행한다. 관찰 범위를 문서화하되 이번 기록 갱신으로 재시험·설치 hash·추가 증빙 Gate를 만들지 않는다.

- 새 의미 기능을 확장하기보다 **current information pipeline과 사용자-facing surface의 안정성을 유지하는 것**을 우선한다.
  - fact / source / outcome / description의 정확성과 표시 일관성을 우선한다.
  - Iris 메뉴 내부 Browser / Detail / Wiki view와 Iris 툴팁이 같은 current information source를 각자의 깊이에 맞게 표시하도록 유지한다.
  - Layer 3 description quality와 item visibility, Layer 4 interaction presentation을 서로 다른 책임 축으로 다룬다.
  - Recipe와 Right-click의 독립성을 유지한다.

- current generation / runtime / package / validation boundary를 다음 제품 gate를 위한 안정된 기준선으로 유지한다.
  - **offline generation → stateless validation → immutable generation → pointer install → Lua runtime display** 흐름을 유지한다.
  - supported public / compatibility surface와 current-generation-only package를 보존한다.
  - regular validation의 contract identity, failure attribution과 fail-closed boundary를 유지한다.
  - 2026-08-31 조건부 검증 결정에 따라 작업별 계획에서 관련 검사·깨끗한 환경 검증·전체 회귀·A/B 비교의 필요성을 각각 정한다. 구체 적용 기준은 `DECISIONS.md`의 Clean-Checkout 계약을 따르며 모든 작업·단계에 외부 A/B Full gate를 자동 부과하지 않는다. 기존 테스트 목록·판정 기준과 별도 제품 gate는 유지한다.
  - 외부 실행 공간이 필요한 계획은 기존 실행 절에 정리 시점을 포함한다. 후속 소비가 끝난 임시 복사본·생성물을 영구 증거처럼 누적하지 않으며, 필요한 원본·실패 이력·현재 handoff/package는 보존한다. 과거 실행 기록은 이 결정으로 재평가하지 않는다.
  - 이미 완료된 architecture / refactor를 readiness 작업을 이유로 다시 설계 문제로 열지 않는다.

## Next

- 교정된 설명에서 **DVF 블록 조합 규칙으로 일반화할 범위**를 정리한다.
  - 문장 구조만 복사하지 않고 기본 용도·효과·복수 역할·정보 부족별 표현과 그 표현을 허용하는 source 조건을 함께 추출한다.
  - 이번에 채택한 개별 설명을 비교 사례로 쓰되 게임 사실의 source는 계속 원본 근거에 둔다. Menu 전용 조리 단계·수량을 Tooltip core 규칙에 섞지 않는다.
  - 공통 규칙 변경은 아직 미구현인 후속 과제다. 새 로드맵·계획 작성이나 제품 구현을 이 문서 갱신으로 실행한 것으로 간주하지 않는다.

- 최신 current product 상태를 기준으로 **DVF freeze readiness를 재판정한다.**
  - 과거 Problem 4의 `동결 불가` verdict는 historical evidence로 유지하고 직접 수정하거나 승계하지 않는다.
  - 이후 correction과 current responsibility / runtime / package 구조를 모두 포함한 새 exact subject에서 required hard-gate chain을 처음부터 다시 실행한다.
  - 이미 correction된 항목은 current state에서 확인하되 과거 finding 전체가 자동 해소됐다고 간주하지 않는다.
  - freeze verdict는 implementation completion, validation closeout 또는 functional in-game acceptance와 별개의 제품 readiness 판단으로 유지한다.

- Iris를 **packaging / release preparation** 단계로 넘길지 별도 release scope에서 결정한다.
  - current-generation-only package와 current installable tooling / environment를 기준으로 package를 생성·검증한다.
  - packaging을 source authority 재구축, predecessor generation 복구, stateful artifact-registry 재도입 또는 새 migration 권한으로 확대하지 않는다.
  - package 생성 성공과 Publish / Workshop / deployment 승인을 동일한 상태로 취급하지 않는다.
  - release-note, publication, Workshop 배포와 공식 지원 범위는 별도 release scope에서 결정한다.

- 실제 release를 진행할 경우 **release checklist와 full manual QA**를 별도 scope로 수행한다.
  - clean install에서 PZ boot / save load, Iris 메뉴 내부 Browser / Detail / Wiki view, Iris 툴팁, Recipe / Right-click 주요 경로를 확인한다.
  - KO / EN 전환, package install path, in-game visibility와 supported public surface를 확인한다.
  - raw token / raw nil / table address / broken placeholder / stale predecessor text가 사용자 표면에 노출되지 않는지 확인한다.
  - Iris-only functional acceptance를 모든 외부 모드 compatibility의 증거로 확대하지 않는다.
  - RTC / Publish / release / Workshop / deployment readiness는 각자의 승인 범위에서 별도로 판정한다.

- 추가 optimization은 기본 개발 전선으로 두지 않고 **evidence-qualified successor**가 있을 때만 연다.
  - 실제 PZ Kahlua engine-object binding evidence가 없는 `IrisObjectAccess` generic fast-path를 production route에 채택하지 않는다.
  - runtime / allocation / repository optimization은 측정 가능한 materiality와 safety 근거가 함께 있을 때만 평가한다.
  - 기존 deferred / no-op / optional benchmark 후보를 완료된 architecture나 functional acceptance의 잔여 blocker로 되살리지 않는다.
  - 새 후보는 구현 자체를 목표로 하지 않고 `adopt / defer / no-op` 중 하나로 명시적으로 disposition한다.

## Hold

- release / readiness 축을 과대 선언하거나 서로 대체하는 것
  - targeted validation, automated gate, functional in-game acceptance, refactor / validation closeout을 freeze / RTC / Publish / release / Workshop / deployment readiness로 확대하지 않는다.
  - package 생성이나 Iris-only 정상 동작을 모든 외부 모드 compatibility 또는 release 승인으로 간주하지 않는다.
  - PZ latency / heap / FPS / frame-time과 실제 GPT / Codex token 개선률은 raw before/after measurement 없이 주장하지 않는다.

- non-current artifact와 predecessor architecture를 current authority로 되살리는 것
  - staging / diagnostic / fixture / historical / predecessor / rollback artifact를 current source나 mutation authority로 사용하지 않는다.
  - rendered output, runtime chunk, package projection이나 installed copy를 upstream source authority로 역승격하지 않는다.
  - legacy descriptor / predecessor generation / stale payload를 current generation fallback으로 사용하지 않는다.
  - 여러 generation을 동시에 current runtime authority로 유지하지 않는다.

- 퇴역한 stateful artifact-registry / legacy governance / runtime-side fallback을 current architecture로 복귀시키는 것
  - generation 생성 / lifecycle / validation / install / runtime identity를 하나의 mutable stateful manager가 다시 소유하게 하지 않는다.
  - retired predecessor governance를 current 통합 권위로 되살리지 않는다.
  - historical reproduction이나 provenance 보존 필요성을 active product dependency 복구의 근거로 사용하지 않는다.
  - upstream source / generation 오류를 legacy fallback이나 runtime-side repair로 숨기지 않는다.

- Iris runtime에 JVM / Java / Mixin product logic을 도입하는 것
  - PZ에서 실행되는 Iris는 **100% Lua**라는 경계를 유지한다.
  - 성능이나 편의를 이유로 Java bridge, Mixin 또는 JVM-side product logic을 runtime 기본 경로에 추가하지 않는다.
  - Pulse의 기반 capability를 사용하더라도 Iris의 정보 판정·표시 책임을 다른 Spoke로 이전하거나 다른 Spoke에 직접 의존하지 않는다.

- Iris를 해석 / 추천 / 비교 / 품질 판단 엔진으로 확장하는 것
  - runtime에서 fact / outcome / source / description의 의미를 다시 추론하거나 사용자 행동 권장으로 변환하지 않는다.
  - 효율 평가, 우열 비교, 체감 의미 추론, 조건부 추천과 자동 설명 확대를 기본 기능으로 도입하지 않는다.
  - 근거가 부족한 정보는 추측해서 채우지 않는다.
  - 데이터 오분류나 설명 왜곡을 UI 예외 규칙으로 봉합하지 않고 upstream source integrity 문제로 처리한다.
  - internal quality signal을 사용자-facing recommendation / ranking / trust signal로 사용하지 않는다.

- Evidence / Source / Outcome 모델과 독립 정보 축을 과도하게 일반화하는 것
  - Context Outcome을 runtime inference나 메뉴 문자열 기반 자동 outcome 생성기로 바꾸지 않는다.
  - Right-click evidence를 메뉴 존재 / 메뉴명 / UI 구조만으로 채택하지 않는다.
  - `item-dependence + state-change proof`와 `executing_tool + external_target + persistent_change` 기준을 느슨하게 완화하지 않는다.
  - Recipe와 Right-click을 하나의 일반화된 행동 capability로 합치지 않는다.
  - 레시피 / 우클릭 행동 / 섭취 / 장착 / 무기 사용 등 서로 다른 source / outcome을 편의를 이유로 전역 semantic grouping으로 합치지 않는다.
  - Layer 3 description과 Layer 4 interaction presentation의 책임을 다시 혼합하지 않는다.

- closed assessment / retired validation / historical failure를 새 current authority 없이 재개방하는 것
  - 완료된 one-off assessment나 retired validation을 production / runtime / publish authority로 승격하지 않는다.
  - historical FAIL / review / terminal evidence를 후속 PASS를 이유로 삭제하거나 current PASS로 재작성하지 않는다.
  - 과거 freeze verdict를 successor correction만으로 수정하거나 자동 승계하지 않는다.
  - 과거 count / hash / commit / validation 결과만으로 새 current work item이나 mutation 권한을 만들지 않는다.
  - 재개방이 필요하면 기존 current authority를 보존하는 별도의 bounded successor scope로 연다.

---

# 6. Frame

## 목표

Project Zomboid 모드팩의 상태를 시간축 위에서 **기록·비교·되돌리는 팩 상태 관리 레이어**.

대상은 개별 모드가 아니라 **팩 상태(PackState)** 이며, 일반 VCS처럼 브랜치 / 병합 / 자동 해결을 제공하는 것이 아니라 **snapshot / compare / rollback**에 집중한다.

## Doing

- Frame은 아직 구현 전선이 아니라 **제품 축 정의 / 범위 봉인 단계**로 둔다.
- `PackState`를 사용자와 시스템이 다루는 1급 객체로 유지한다.
- 관리 범위는 **모드팩 환경**으로 제한하며 월드 / 세이브 상태는 포함하지 않는다.
- **수동 스냅샷 = 사용자가 선언한 기준점 / 자동 스냅샷 = 시간축 안전망**의 역할 구분을 유지한다.
- 자동 저장은 **5 / 10 / 30 / 60분 주기 + 최근 10개 롤링**을 기본값 후보로 둔다.
- 팩의 기본 설정은 원본으로 보존하고 사용자 변경은 **별도 override**로 관리하는 구조를 기본으로 한다.
- Frame이 제공하는 재현성은 **환경 재구성 + fingerprint 기반 동일성 확인**으로 제한한다.
- 삭제된 모드, 변경된 Workshop 버전 등 외부 조건 때문에 완전 복원이 불가능한 경우 이를 자동 해결하지 않고 현재 차이를 드러낸다.
- 문제 모드 지목, 정상 / 비정상 판정, 자동 추천, 자동 정렬, 자동 해결을 하지 않는다.
- UI / 용어는 판단보다 **기준점 / 자동 저장 / 달라짐 / 비교 / 되돌리기 / 포함됨 / 빠짐** 같은 사실+행동 언어를 우선한다.
- 외부 런처나 관리자 툴이 아니라 **PZ 내부의 모드팩 상태 관리 레이어**를 메인라인으로 유지한다.

## Next

- `PackState`의 최소 스키마를 정리한다.
  - 활성 모드 목록
  - 모드 순서
  - 모드 출처
  - baseline 설정
  - 사용자 overrides
  - fingerprint
  - snapshot metadata

- 수동 스냅샷 / 자동 스냅샷의 저장·표시·선택 UI 위계를 구체화한다.
  - 사용자가 선언한 공식 기준점과 자동 안전망을 명확히 구분한다.
  - 자동 스냅샷이 수동 스냅샷보다 낮은 품질의 기록처럼 표현되지 않게 한다.

- baseline / overrides / manifest / fingerprint의 최소 계약을 정리한다.
  - 원본 설정과 사용자 변경의 책임 경계를 고정한다.
  - fingerprint가 동일성 확인용 표식이지 정상 / 비정상 판정 점수가 아님을 명확히 한다.

- import / restore의 검증 규칙과 복구 UX를 정리한다.
  - 외부 공유 상태를 내부 `PackState`로 정규화하는 기준을 정한다.
  - **재구성 가능 / 일부 요소 누락 / 현재 상태와 불일치**를 구분해서 표시한다.
  - 삭제된 모드나 과거 버전 부재를 Frame이 자동 해결해야 하는 문제로 취급하지 않는다.
  - 완전 복원이 불가능하면 무엇이 달라졌는지를 사용자에게 명확히 보여준다.

- 공개 공유 포맷과 내부 캐시의 책임 경계를 구체화한다.
  - 외부 공유는 **ZIP + manifest.json + 설정 + 선택적 overrides + fingerprint** 같은 열린 형식을 우선한다.
  - `.frame`은 외부 생태계 표준이 아니라 Frame 내부 정규화 / 캐시 용도로 제한한다.
  - 사용자 overrides와 자동 스냅샷의 공유 여부는 명시적인 옵션으로 다룬다.

- `모드 개별 관리`가 아니라 **팩 상태 관리**로 읽히는 용어와 메인 UX를 정리한다.
  - 개별 모드 제어보다 기준점 / 비교 / 변화 / 복구 흐름이 중심이 되도록 한다.
  - 첫 화면과 복구 화면에서 현재 상태와 기준점의 관계를 빠르게 이해할 수 있게 한다.

## Hold

- 문제 모드나 원인을 자동으로 지목하는 것
- 정상 / 비정상 판정을 도입하는 것
- 추천 설정 / 최적 순서 / 정답 구성을 제시하는 것
- 자동 추천 / 자동 정렬 / 자동 해결을 도입하는 것
- Frame 내부에 설정 편집기를 중심 기능으로 구축하는 것
- 외부 런처 / 설치기 / 관리자 툴 / devkit으로 메인라인을 전환하는 것
- 모드 원본 파일을 직접 저장·배포해 완전 재현성을 보장하려는 것
- 월드 / 세이브 상태까지 Frame의 관리 책임으로 확장하는 것
- `.frame`을 외부 공개 표준이나 생태계 필수 포맷으로 강제하는 것
- 변화 감지 해석에 의존해 자동 스냅샷을 기본적으로 생략하는 것
- Fuse / Nerve 같은 runtime 안정화나 Canvas의 ResourceState 계산 책임을 Frame으로 흡수하는 것
- 외부 Spoke와 직접 의존해 Frame의 상태 모델을 결합하는 것

## Backlog

- 첫 화면 / 비교 화면 / 복구 화면의 핵심 UX를 더 단순하고 직관적으로 다듬는다.
- 공유 UX와 권리 / 약관 / 재현성 한계를 함께 고려한 전달 방식을 검토한다.
- Canvas의 ResourceState 책임을 침범하지 않는 범위에서, 리소스팩 상태의 **외부 snapshot reference를 PackState 시간축에 연계할 가치가 있는지** 장기 검토한다.
  - 실제 연계가 필요하더라도 Frame ↔ Canvas 직접 의존이 아니라 Pulse의 중립 capability / SPI 경계를 따른다.

---

# 7. Cortex

## 목표

Pulse 생태계의 Core나 독립 제품 모듈에 넣기 부적절한 **편의 기능 / 가이드 / 경량 제작 보조 기능**을 격리하는 보조 모듈.

Cortex는 애매한 기능을 임시로 쌓아두는 장소나 신규 제품의 인큐베이터가 아니라, **Pulse의 기반 capability도 아니고 다른 Spoke의 핵심 제품 책임도 아닌 보조 기능**을 수용하는 경계 모듈로 둔다.

## Doing

- Cortex는 아직 구현 전선이 아니라 **admission criteria와 역할 경계를 정의하는 단계**로 둔다.
- Pulse Core가 기반 capability만 유지할 수 있도록 helper / convenience / guide 성격 기능을 분리하는 역할을 유지한다.
- Cortex 후보는 기본적으로 다음 조건을 만족해야 한다.
  - Pulse 자체의 기반 capability가 아니다.
  - Iris / Frame / Canvas / Echo / Fuse / Nerve 등 기존 Spoke의 핵심 제품 책임이 아니다.
  - 없어도 Pulse 생태계와 각 제품의 기본 기능은 성립한다.
  - 사용자의 작업이나 모더의 사용 마찰을 줄이는 보조적 가치가 있다.
  - 정책 판단 / 추천 / 자동 의사결정 authority를 갖지 않는다.
  - 독립적인 제품 가치가 생기면 Cortex에 계속 수용하지 않고 별도 제품 축으로 재분류한다.
- Cortex를 **제품 축의 임시 수용소나 시험장**으로 사용하지 않는다.
- Pulse의 기반 capability여야 할 기능을 Cortex에서 먼저 구현한 뒤 Core로 역이관하는 incubation 방식도 기본 경로로 사용하지 않는다.
- Cortex는 Pulse capability / API / SPI에는 의존할 수 있지만 다른 Spoke를 직접 참조하거나 의존하지 않는 Hub & Spoke 경계를 유지한다.

## Next

- Cortex admission criteria를 명시적인 판정 규칙으로 문서화한다.
  - `Core capability`
  - `existing product responsibility`
  - `Cortex convenience / guide`
  - `independent product candidate`
  - `reject / unnecessary`
  - 위 분류를 기준으로 후보 기능의 owner와 disposition을 결정한다.

- Cortex에 들어갈 수 있는 기능과 들어가면 안 되는 기능의 대표 사례를 정리한다.
  - 사용 편의 helper
  - 모딩 workflow guide
  - 경량 제작 보조
  - 진입 마찰 감소 기능
  - 위 항목을 Cortex 후보군으로 검토한다.
  - runtime 안정화, 정보 제공, 팩 상태 관리, 리소스 상태 관리처럼 독립 제품 가치가 있는 기능은 제외한다.

- **경량 제작 보조**의 상한선을 정한다.
  - 작은 helper나 workflow 보조는 허용할 수 있다.
  - 프로젝트 관리, 빌드 시스템, 종합 제작 환경, devkit처럼 독립적인 workflow를 형성하면 Cortex 범위를 벗어난다.
  - 기능 규모가 커져 독립 product identity가 생기면 별도 모듈 후보로 재분류한다.

- 제품 축과 convenience 축이 헷갈릴 때 사용할 판정 체크리스트를 작성한다.
  - 이 기능이 없어도 해당 제품의 핵심 가치가 유지되는가
  - 특정 Spoke만을 위한 핵심 로직인가
  - Pulse에 들어가야 할 중립 기반 capability인가
  - Cortex가 정책이나 판단 authority를 새로 갖게 되는가
  - 독립 제품으로 설명할 수 있을 만큼 고유한 사용자 가치가 있는가

- Frame / Canvas / Iris 등 인접 제품과 Cortex의 경계 문구를 최신 설계 기준으로 정리한다.
  - Iris의 정보 제공 책임
  - Frame의 PackState 기록 / 비교 / 복원 책임
  - Canvas의 ResourceState 계산 / 검증 책임
  - 위 제품 책임을 Cortex convenience와 명확히 분리한다.

## Hold

- Iris / Frame / Canvas / Echo / Fuse / Nerve 등 기존 제품 모듈의 핵심 책임을 Cortex가 대신 수용하는 것
- 신규 제품 후보를 독립 모듈로 검토하기 전에 Cortex에서 임시 구현하거나 시험 운영하는 것
- 리소스팩 제품 축을 Canvas 대신 Cortex에 수용하는 것
- PackState / 정보 위키 / runtime 안정화처럼 독립 product identity가 있는 기능을 convenience라는 이유로 Cortex에 넣는 것
- 본질적으로 Pulse의 중립 기반 capability여야 하는 기능을 Cortex에서 먼저 구현한 뒤 Core로 역이관하는 방식
- 정책 판단 / 추천 / 자동 결정 / 자동 해결 기능을 convenience로 포장해 Cortex에 넣는 것
- 다른 Spoke의 내부 API / state / implementation에 직접 의존하는 helper를 만드는 것
- 여러 Spoke를 직접 연결하는 coordinator / mediator 역할을 Cortex가 맡는 것
- Cortex를 범용 devkit / IDE / launcher / project manager / build system으로 확대하는 것
- 기능의 소유권이 불명확하다는 이유만으로 Cortex를 기본 fallback destination으로 사용하는 것

---

# 8. Canvas

## 목표

외부 리소스팩 산출물과 현재 런타임 활성 상태를 읽어 **로드 순서와 덮어쓰기 이후의 최종 적용 상태를 계산·검증·비교·설명**하는 독립 모듈.

Canvas는 리소스 제작 툴이나 단순 리소스팩 로더가 아니라, 사용자가 다루는 `ResourcePack`과 실제 게임에 적용된 `ResourceState`를 연결하는 **리소스 적용 상태 관리 플랫폼**으로 둔다.

## Doing

- Canvas는 아직 구현 전선이 아니라 **제품 축 정의 / v1 가치 검증 단계**로 둔다.
- Canvas는 **독립 모듈로만 시작**한다는 기준을 유지한다. (`Canvas로 시작 / 아니면 폐기`)
- 제작 툴 / 정책 도구 / Frame 대체물이 아님을 유지한다.
- Canvas의 핵심 객체를 다음처럼 분리한다.
  - `AssetEntry`: 실제 리소스 파일 / 엔트리 / 대상 경로의 식별 단위
  - `ResourcePack`: 사용자가 만들고 불러오고 공유하고 비교하는 user-facing 1급 객체
  - `ResourceState`: 여러 ResourcePack과 로드 순서가 합쳐져 실제 게임에 최종 적용된 결과 상태
- Canvas의 핵심 책임은 `ResourcePack`을 관리하는 것 자체가 아니라 **그 결과로 형성되는 ResourceState를 계산·검증·비교·설명하는 것**에 둔다.
- 입력은 두 축으로 유지한다.
  - 외부 산출물 / 기대 상태 / 배포 대상
  - 현재 활성 리소스팩 / 로드 순서 / 출처 / 실제 적용 상태
- 이 두 입력은 각각 독립적으로 판정할 수 있고 필요할 때 서로 비교한다.
- Canvas의 v1 가치는 다음 세 독립 판정 축으로 유지한다.
  - **적용 상태 판정**: 최종 적용 결과 / 충돌 / 로드 순서 / 최종 winner 가시화
  - **제작 안전 판정**: 경로 / 구조 / ID / 중복 / 패킹 문제 검증
  - **배포 일치 판정**: 로컬↔빌드 / 서버↔클라 / 기대 상태↔실제 상태 비교
- 세 판정 축은 종합 리포트에서 함께 보여줄 수 있지만 하나의 숨겨진 master score나 단일 PASS / FAIL로 압축하지 않는다.
- Pulse는 리소스 조회 / 정규화 / fingerprint / reload event / networking / SPI 같은 **중립 기반 capability**만 제공하고, Canvas가 인덱싱 / ResourceState 계산 / 충돌 분석 / 검증 / 비교 / 설명 UX를 맡는다.
- JVM+Lua 혼용은 허용하되 책임을 분리한다.
  - 최종 적용 상태 계산 / 충돌 분석 / 검증 / 비교는 Java Core가 소유한다.
  - Lua는 그 결과를 표시·탐색하는 user-facing surface를 담당한다.
- 게임 리소스를 v1의 1차 대상으로 두고 모드 리소스 확장은 후행 축으로 둔다.

## Next

- `AssetEntry / ResourcePack / ResourceState`의 최소 모델과 관계를 구체화한다.
  - `AssetEntry` identity / source / target path / resource type
  - `ResourcePack` manifest / load-order identity / source / contained entries
  - `ResourceState` resolved winner / overridden entries / conflict state / provenance
  - 동일 리소스가 여러 pack에 존재할 때 최종 적용 결과를 결정하는 규칙
  - expected state와 actual state를 비교할 수 있는 identity / fingerprint 기준

- **적용 상태 판정**의 최소 기능선을 정리한다.
  - 활성 ResourcePack과 로드 순서 조회
  - AssetEntry 인덱싱
  - override chain 계산
  - 최종 winner 판정
  - conflict와 provenance 설명
  - 현재 runtime ResourceState와 외부 expected state 비교

- **제작 안전 판정**의 최소 기능선을 정리한다.
  - 경로 / 구조 검증
  - ID와 중복 충돌 탐지
  - `.pack` / manifest 일관성 검증
  - 배포 전 preflight report
  - 검증 결과를 자동 수정이나 정답 추천으로 확대하지 않는 경계

- **배포 일치 판정**의 최소 기능선을 정리한다.
  - 로컬 작업본 ↔ 빌드 산출물 비교
  - 서버 ↔ 클라이언트 상태 비교
  - expected ResourceState ↔ actual ResourceState 비교
  - manifest / fingerprint 기반 차이 설명

- 입력 / 내부 정규화 / 출력 / 공유 포맷의 책임 경계를 구체화한다.
  - 기본 출력은 `.pack + manifest.json`을 우선한다.
  - 필요하면 ZIP으로 wrapping한다.
  - 기본 공유는 **ZIP + `.pack` + `manifest.json`** 구조를 사용한다.
  - 선택적으로 source ZIP이나 분석 / 문제 재현용 `.cvb` 번들을 허용할 수 있다.
  - `.cvb`는 외부 공개 표준이나 신뢰 파일이 아니라 내부 정규화 / 캐시 / 비교 / 진단용 보조 포맷으로 제한한다.
  - `.cvb`를 다시 읽을 때도 최소 검증을 거친다.

- 외부 산출물과 runtime active state를 하나의 내부 모델로 정규화하는 workflow를 설계한다.
  - import
  - validation
  - normalization
  - ResourceState resolution
  - compare
  - explanation

- v1의 대표 UX를 정리한다.
  - 현재 ResourceState 요약
  - 어떤 AssetEntry가 최종 적용됐는지 확인
  - 어떤 pack이 어떤 리소스를 덮어썼는지 추적
  - 제작 / 배포 불일치를 세 판정 축별로 분리해 설명
  - 단일 점수보다 원인과 차이를 직접 보여주는 구조

## Hold

- Canvas를 이미지 / 사운드 / 모델 등을 직접 만드는 리소스 제작 툴로 확장하는 것
- Canvas를 단순 리소스팩 로더로 축소하는 것
- 리소스 원본 파일을 자동 수정하거나 자동 재패킹하는 것
- 자동 병합 / 정답 추천 / 최적 로드 순서 제안 같은 정책·심판 기능을 도입하는 것
- 적용 상태 / 제작 안전 / 배포 일치의 세 판정 축을 하나의 숨겨진 master score나 단일 PASS / FAIL로 압축하는 것
- ResourcePack과 ResourceState의 책임을 혼합해 user-facing pack 관리와 최종 적용 상태 계산을 같은 개념으로 취급하는 것
- Java Core가 소유해야 할 ResourceState 계산 / 충돌 분석 / 검증 / 비교 책임을 Lua presentation 계층으로 이전하는 것
- Frame의 PackState / snapshot / 복원 책임을 Canvas가 흡수하거나 Canvas를 Frame 대체물로 만드는 것
- Frame과의 직접 통합 설계나 Spoke 간 직접 의존을 도입하는 것
- `.cvb`를 외부 공개 표준, 신뢰 파일 또는 생태계 필수 포맷으로 만드는 것
- 외부 사례의 객체 모델 / 포맷 / workflow를 검증 없이 그대로 이식하는 것
- 게임 리소스 v1 가치가 검증되기 전에 모드 리소스까지 범위를 넓히는 것

## Backlog

- 게임 리소스 대상 v1 이후 모드 리소스 확장 전략을 검토한다.
- 서버↔클라이언트 / 로컬↔배포 / expected↔actual ResourceState 비교 UX를 고도화한다.
- Canvas의 ResourceState 책임을 침범하지 않고 Frame의 PackState 책임도 변경하지 않는 범위에서, **ResourceState snapshot / reference를 Frame 시간축과 느슨하게 연계할 가치가 있는지** 장기 검토한다.
  - 실제 연계가 필요하더라도 Canvas ↔ Frame 직접 의존이 아니라 Pulse의 중립 capability / SPI 경계를 따른다.

---

# 9. 플랫폼 브랜딩 / 공개 전략

## 목표

플랫폼을 전면에 내세우기보다 **독립 제품이 먼저 가치를 증명하고, 공통 기반은 뒤늦게 드러나는 구조**를 유지한다.

Pulse는 처음부터 `새 Java 로더`로 정면 경쟁하는 브랜드가 아니라, 실제 제품들이 사용하면서 가치와 안정성이 확인된 **자유도 높은 공통 모딩 기반**으로 후노출한다.

## Doing

- **킬러앱 / 독립 제품 우선 공개** 전략을 유지한다.
  - 사용자는 먼저 Iris / Nerve / Fuse 같은 독립 제품의 가치를 경험하도록 한다.
  - Pulse가 있다는 사실 자체보다 각 제품이 해결하는 실제 문제를 먼저 설명한다.
  - 플랫폼 adoption을 제품 사용의 전면 조건처럼 보이게 하지 않는다.

- `새 Java 로더` 정면 경쟁 프레이밍을 피하고 **결과물 선공개 → 기반 후노출** 구조를 유지한다.
  - Pulse를 Fabric / Forge 대체재처럼 직접 비교·포지셔닝하지 않는다.
  - first-party 제품이 잘 동작하는 이유를 전용 결합이 아니라 **공통 플랫폼의 기반 품질**로 설명할 수 있는 상태를 지향한다.
  - Pulse의 자유도 / 중립성 / 기존 Lua 생태계와 Mixin 생태계의 공존 가능성을 플랫폼 가치로 둔다.

- 각 모듈은 `Pulse 기능`이 아니라 **자기 고유의 독립 가치**로 먼저 설명한다.
  - Iris: **근거 기반 게임 내 위키**
  - Nerve: **선택적 dormant stability guard**
  - Fuse: **엔진 안정성 레이어**
  - Frame: **팩 상태 관리 레이어**
  - Canvas: **리소스 적용 상태 관리 플랫폼**
  - Echo: **관측 / 계측 프로파일링 모드**
  - Cortex는 독립 killer app보다는 convenience / guide 성격의 보조 모듈로 취급한다.

- 공개 / 배포 메시지의 주요 위험을 단순 기능 부족보다 **플랫폼 오염 방지와 채택 마찰 제어**에 둔다.
  - 사용자가 별도 플랫폼 설치를 강요받는다는 인상을 최소화한다.
  - 제품 설명에서 플랫폼 내부 구조를 필요 이상으로 전면에 내세우지 않는다.
  - Pulse 사용 여부보다 사용자가 얻게 되는 제품 가치를 먼저 전달한다.

- Spoke의 독립성을 공개 전략에서도 유지한다.
  - Pulse와 각 Spoke를 하나의 결합 제품처럼 설명하지 않는다.
  - Echo / Fuse / Nerve / Iris / Frame / Canvas / Cortex 간 직접 결합을 공개 가치처럼 홍보하지 않는다.
  - 공통 기반이 필요한 경우에도 Pulse의 중립 capability를 공유하는 독립 제품군으로 설명한다.

## Next

- README / Architecture / 로고 / 모듈 네이밍과 current 제품 정체성의 정합성을 점검한다.
  - 각 모듈의 canonical 역할 설명을 통일한다.
  - 플랫폼 기능과 제품 기능의 설명이 섞이지 않게 한다.
  - Hub & Spoke 구조가 bundle / suite / coordinator 구조처럼 오해되지 않게 한다.

- 초기 공개 순서를 **제품 readiness와 사용자 가치** 기준으로 구체화한다.
  - 현재 기본 순서는 `Iris → Nerve → Fuse → Pulse / Echo → Nerve+`를 후보로 둔다.
  - Pulse와 Echo는 같은 제품으로 묶지 않고 후행 공개 시점이 가까운 별도 모듈로 취급한다.
  - `Nerve+`는 Nerve의 의존성 전환이나 상위 edition이 아니라 **별도의 Pulse-dependent variant**로 취급한다.
  - Frame / Canvas는 현재 설계 단계이므로 초기 고정 공개 순서에 넣지 않고 각자의 product readiness 이후 별도로 판단한다.
  - 실제 readiness 변화가 있으면 공개 순서는 별도 release strategy에서 재판정할 수 있다.

- 설치 / 실행 마찰 최소화 원칙을 구체화한다.
  - launcher / bootstrap이 필요한 경우 사용자 체감과 추가 설치 마찰을 최소화한다.
  - Steam 실행 옵션 / 바로가기 / bundle 안내 흐름을 단순하게 유지한다.
  - 사용자가 `추가 플랫폼을 먼저 설치해야 한다`고 느끼기보다 제품 설치 과정에서 필요한 기반이 자연스럽게 제공되는 UX를 우선한다.
  - 설치 편의를 위해 Pulse와 Spoke의 구조적 독립성을 훼손하지 않는다.

- Pulse 후노출 시점의 메시지 기준을 정리한다.
  - 이미 공개된 제품들의 공통 기반이라는 실제 근거가 있을 때 Pulse를 설명한다.
  - Core capability 목록 자체보다 **모더 자유도 / 안정된 기반 / 생태계 공존성**을 중심으로 설명한다.
  - first-party 전용 플랫폼처럼 보이지 않도록 외부 모드에도 동일한 기반 surface가 열려 있다는 점을 전제로 한다.

- 공개 전략의 가변 요소를 별도 문서로 분리할지 정리한다.
  - `Philosophy.md`에는 장기적으로 유지할 역할 경계와 금지선을 우선한다.
  - 공개 순서 / 기대치 / 설치 UX / 메시지 / release timing 같은 가변 전략은 필요하면 별도 ReleaseStrategy 문서에서 관리한다.

## Hold

- 킬러앱 / 독립 제품의 가치가 검증되기 전에 Pulse를 플랫폼 자체로 선공개하는 것
- Pulse를 Fabric / Forge의 직접 대체재나 경쟁 로더로 정면 포지셔닝하는 것
- Core capability 목록이나 기술적 구조를 사용자-facing 제품 가치보다 먼저 홍보하는 것
- Pulse와 Echo 또는 다른 Spoke를 하나의 결합 제품 / 필수 bundle처럼 포지셔닝하는 것
- Nerve를 Nerve+로 전환하거나 기존 Nerve가 Pulse 의존 제품으로 바뀌는 것처럼 설명하는 것
- Fuse를 추후 Pulse-dependent 제품으로 전환하는 별도 migration 단계가 있는 것처럼 설명하는 것
- Frame / Canvas처럼 아직 설계 단계인 제품의 공개 시점을 readiness 없이 고정하는 것
- 설치 마찰을 해결하기 전에 복잡한 launcher / installer를 기본 전제로 만드는 것
- adoption을 높인다는 이유로 Pulse가 제품별 전용 기능이나 정책을 흡수하는 것
- 브랜드 편의를 위해 Hub & Spoke의 독립 제품 경계를 흐리거나 Spoke 간 직접 결합을 정상 구조처럼 홍보하는 것
- 법적 / 최종 브랜드, 공개 순서 또는 release timing을 충분한 제품 readiness 없이 조기 확정하는 것

## Iris repository lightweighting execution

- [x] terminal-v15 external environment admission과 baseline Checkpoint A Run A/Run B/comparator
- [x] W0 dual-subject census, broader staging closure, main.py C disposition, residue subject binding
- [x] deterministic Change 1B adoption authority
- [x] tracked residue와 custody-only residue를 subject별로 제거
- [x] current runtime/output/tooling/evidence bindings를 successor owner로 전환
- [x] deterministic external historical archive implementation과 restore evidence
- [x] ordinary canonical gate를 사용하는 synthetic pre-delete Checkpoint C
- [x] exact historical payload removal과 ignore/search/attribute 단순화
- [x] terminal Checkpoint D, W10 census, independent review
- [x] Reviewer PASS를 반영한 documentary completion carrier의 local `main` 통합

Closeout complete: exact implementation `801f15f6`의 terminal Run A/B/comparator와 W10은 PASS했고, independent Reviewer는 `c2b9514f..9882ce6d`에서 actionable finding 0을 확인했다. Reviewer가 확인했던 0013·0014 append-only 위반은 두 predecessor의 최초 committed blobs 복구와 새 0015 correction successor로 보정됐다. Review 결과를 반영한 completion carrier `28f95b63`은 local `main`에 통합했으며 remote push는 수행하지 않았다. Current clean-checkout route와 package는 external archive 없이 동작하며, historical reproduction은 verified content-addressed archive의 explicit restore route로만 수행한다. Tracked historical payload 3,804 files / 607,432,467 bytes와 prior custody-only archived payload 1,266 files / 202,231,050 bytes는 서로 겹치지 않는 domain으로 제거됐다. Terminal local-custody correction은 별도 additive archive에 295 files / 4,273,310 bytes를 보존한 뒤 regenerable logs 2개와 함께 literal 제거했고 Iris ignored/untracked/filesystem-only/reparse를 0으로 닫았다. Current capsule은 133,094 bytes, successor overhead는 1,653,400 / 3,037,162 bytes다. 범위 밖의 다른 모듈 untracked build output은 보존한다. Runtime/token 성능 개선률과 release readiness는 이 작업의 claim이 아니다.

### Iris current responsibility naming

- 2026-08-30 역할별 재명명: `TooltipStaticData`에 이어 사용자가 지목한 validation 여섯 폴더의 개별 코드·테스트·현재 설정 85개를 재명명/재배치했다. `execution`, `source_analysis`, `artifacts`, `baseline`, `scenarios`, `test_coverage`에 실제 책임을 드러내는 파일명으로 배치했고 사용처도 갱신했다. 기존 Tooltip 변경과 과거 기록은 보존한다.
- 사용자 최종 범위인 재명명·재배치·참조 갱신은 `complete`다. N7 `current_environment.json`과 기존 writer가 생성한 record까지 현재 폴더에 반영했다. 사용자가 추가 검증을 종료했으므로 production 재생성·full gate·package·PZ 관찰은 이번 완료의 잔여 조건이 아니다.
- 이전 T1/T2/T3 PASS를 상속하거나 이번 미실행 검사를 PASS로 주장하지 않는다. 추가 검증·봉인 작업을 요구하지 않는다. 상세 결과: `docs/iris_current_responsibility_naming_alignment_closeout.md`.
