# ROADMAP.md

> 상태: canonical summary + deduplicated consolidated addendum ledger through 2026-08-10
> 기준일: 2026-08-10
> 상위 기준: `Philosophy.md`, `DECISIONS.md`  
> 목적: Pulse 생태계의 현재 진행 방향과 다음 게이트를 짧게 고정한다.

---

## 운영 규칙

- 이 문서는 현재 상태와 다음 과제를 보여주는 문서다.
- `왜 그렇게 정해졌는가`는 `DECISIONS.md`에 남긴다.
- 항목 상태는 `Done / Doing / Next / Backlog / Hold` 중심으로 관리한다.
- 본 문서는 구현 세부 로그가 아니라 방향판이다.
- 상단 모듈 섹션은 **current canonical summary** 로 읽고, 뒤의 consolidated addendum ledger는 **historical trace / provenance index** 로 읽는다.
- Addendum 본문은 중복 제거를 위해 ledger로 압축하며, 세부 사유와 decision history는 `DECISIONS.md` 또는 각 round 산출물을 우선한다.

---

# 1. Pulse Core

## 목표

얇고 중립적인 JVM 기반 모드로더/플랫폼으로서, 하위 모듈과 외부 모드를 안정적으로 받칠 공용 capability를 제공한다.

## Current Position

- Pulse Core는 단순 self-boot 수준을 넘어, 외부 모드 로딩 기반 기능을 상당 부분 갖춘 상태다.
- 현재 Pulse의 병목은 기능 부재가 아니라 **모드로더 계약 봉인, 플랫폼 실패 진단, public surface/capability 경계 정리**다.
- Phase 1은 구현상 완료 후보에 가깝지만, ROADMAP상 Done 선언 전 최소 계약과 검증선 봉인이 필요하다.
- Phase 2는 기능 기반은 존재하나, stable/public/internal surface 분리가 아직 핵심 과제로 남아 있다.
- Phase 3은 capability 재료가 이미 넓게 존재하므로, 새 기능 추가보다 **Core surface 승격/강등 판정**이 우선이다.

## Roadmap Phases

### Phase 1 — 실제 모드로더화

**진행도:** 80~90%  
**상태:** Done 후보 / seal pending

#### Current Read
- `ModLoader`는 `mods/` JAR 스캔, `pulse.mod.json` 파싱, 의존성 위상 정렬, 순환 감지, 모드별 Mixin config 등록, `PulseMod.onInitialize()` 호출, 역순 unload, 상태 머신을 이미 포함한다.
- 따라서 Phase 1은 “처음부터 만들어야 하는 단계”가 아니라, **현재 구현을 외부 모드 로딩 계약으로 봉인하는 단계**에 가깝다.

#### Remaining Gate
- discovery / resolve / register / initialize / unload 흐름을 공식 최소 계약으로 문서화한다.
- metadata / dependency / conflict 처리의 최소선을 확정한다.
- 외부 모드 샘플 또는 smoke 기준으로 실제 loadable platform 여부를 확인한다.
- Mixin registration 실패 시 진단/실패 경계를 Phase 2로 넘길지, Phase 1의 최소 요구로 볼지 분리한다.

#### Exit Criteria
- 외부 모드 discovery 최소 구조가 성립한다.
- 외부 mixin registration 경로가 부팅 흐름에 연결된다.
- entrypoint 계약이 정의된다.
- metadata / dependency / conflict 최소 정책이 봉인된다.
- 외부 모드 1개 이상을 기준으로 load → initialize → unload 흐름을 설명 가능하다.

---

### Phase 2 — 플랫폼 성숙화

**진행도:** 60~70%  
**상태:** Doing

#### Current Read
- EventBus는 우선순위 정렬, 예외 격리, ClassLoader fallback, async post, 모드별 자동 정리 같은 플랫폼 안정화 기능을 이미 갖고 있다.
- CrashReporter, DevConsole, EventMonitor, DebugOverlayRenderer, MixinDiagnostics, ThreadGuard 등 진단/DX 계열도 상당히 존재한다.
- 다만 이것들이 **제품 surface / stable API / guided surface / raw-internal surface**로 정리됐다고 보긴 어렵다.

#### Remaining Gate
- 이벤트/콜백 예외 격리 규칙을 외부 모드 계약 수준으로 정리한다.
- mixin 충돌과 실패 진단을 “자동 해결”이 아니라 “원인 가시화” 중심으로 봉인한다.
- DevMode / logging / debug overlay / diagnostics를 사용자 기능이 아니라 진단 capability로 분리한다.
- public surface 등급을 나눈다.
  - Product surface
  - Stable Core surface
  - Starter surface
  - Guided surface
  - Raw/Internal surface

#### Exit Criteria
- 이벤트/콜백 실패가 Core 전체나 다른 모드로 전파되지 않는다.
- mixin 충돌과 적용 실패를 최소 원인 단위로 진단할 수 있다.
- 외부 모드가 의존해도 되는 stable API surface 초안이 분리된다.
- DevMode / logging / debug hook의 공개 경계가 정리된다.
- Raw/Internal 기능이 외부 계약처럼 오해되지 않는다.

---

### Phase 3 — 1st-party 모드 지지 기반 완성

**진행도:** 40~50%  
**상태:** capability inventory는 풍부하지만, Core surface 판정 미완

#### Current Read
- Network, Scheduler, Config, Content Registry, DataAttachments, GameAccess, ResourceLoader, I18n, PermissionManager, SPI Registry, EngineBindings, LuaBridge, LuaBudgetManager, PulseMetrics, ProfilerScope 등 1st-party 모드를 지지할 수 있는 재료는 이미 넓게 존재한다.
- 그래서 Phase 3의 문제는 “기능이 없어서 못 한다”가 아니라, **어떤 기능이 진짜 Core 기반 capability이고, 어떤 기능이 helper / convenience / policy / raw-internal인지 재분류해야 한다**는 점이다.
- 특히 GameAccess, MixinHelper, profiler/metrics, Network, Registry 계열은 편리하지만, 그대로 stable Core surface로 올리면 Pulse가 얇은 플랫폼이 아니라 비대한 SDK가 될 위험이 있다.

#### Remaining Gate
- capability 후보를 먼저 inventory로 정리한다.
- 각 후보를 `기반 capability / helper / policy / convenience / raw-internal`로 분류한다.
- spoke 수요가 확인된 항목만 Core surface 승격 후보로 둔다.
- 중립 노출이 불가능한 기능은 spoke-local 또는 Raw/Internal로 강등한다.
- 외부 공개 승격은 “구현되어 있음”이 아니라 “spoke 수요 + 중립성 + stable contract 가능성”을 기준으로 한다.

#### Exit Criteria
- profiler / engine optim / lua optim / data-info 계열이 공통으로 필요로 하는 최소 capability가 정리된다.
- 거리 / 상태 / tick / phase 같은 측정·상태 노출 capability의 중립 노출 가능성이 판정된다.
- Network / Registry / Scheduler / Config / EventBus / DataAttachments / GameAccess 중 실제 Core surface 후보가 봉인된다.
- 리소스팩 지원 capability와 바닐라 기반 기능 후보군의 Core 편입 여부가 분리된다.
- API 확장 절차가 `후보 추출 → 기반성 판정 → 중립 노출 검증 → surface 봉인`으로 정리된다.

## Hold

- 범용 DataBus / shared state / pub-sub 같은 모드 간 실시간 중개 채널 도입
- Pulse를 coordinator나 정책 허브처럼 비대화시키는 capability 확장
- `근거리면 FULL` 같은 정책 fast-path, recommendation, pressure 판단을 Core에 넣는 확장
- 하위 모듈의 snapshot/update 주기를 Core가 호출하거나 통제하는 구조
- 기반 후보 추출 이전의 무차별 API 증설
- helper / 편의 / 가이드 성격 기능의 Core 편입
- Pulse를 지금 당장 빈 플랫폼 형태로 전면 공개하는 것

---

# 2. Echo

## 목표

병목 지점을 관찰하고 계측하는 observer-only 프로파일링 모드. 현재 기준은 **핫패스 무해성 유지, 관측 전용 경계 보존, soft-freeze 운영**이다.

## Done

- Bundle A 기준 Echo 핫패스 무해화 완료.
  - 핫패스 금지 API와 safe default 경계 봉인
  - `EchoConfigSnapshot` / `EchoRuntimeState` / `volatile` 단일 참조 구조 반영
  - release silent / debug one-shot warning 운영 구조 반영
  - `non-invasive observer` 기준 통과

## Doing

- Echo는 확장 전선이 아니라 **soft-freeze / 유지보수 / 표면 보수 중심 모듈**로 운용한다.
- Core capability와 분리된 관찰 모드 정체성을 유지한다.
- 공용 surface는 category / targetId / severity 같은 raw observation 중심으로 제한한다.
- recommendation / priority / under-pressure 판단은 Echo surface에 올리지 않는다.
- Bundle A 이후 핫패스 변경은 기본 동결 상태로 취급한다.

## Next

- Iris 이후 실제 blind spot이 확인될 때만 국소적 profiling 확장 재개 기준을 정리한다.
- observer-only 경계를 깨지 않는 유지보수 / 표면 보수 원칙을 문서화한다.
- Echo 공개 시 설명 문구를 `분석/권장 엔진`이 아니라 `관측/계측 모듈` 기준으로 정리한다.

## Hold

- Echo를 recommendation 엔진, 정책 라우터, 자동 최적화 판단기로 확장하는 것
- Echo severity / top_target / hint / insight를 Fuse 행동 입력으로 고착시키는 구조
- 다른 모듈이나 Core가 Echo 내부 snapshot/update 주기를 호출하거나 통제하는 구조
- 핫패스에 StackWalker, 풍부한 컨텍스트 캡처, 일반 로그를 되살리는 것
- Bundle A를 ns 단위 벤치마크/JMH 중심 과제로 재프레이밍하는 것
- Pulse SPI / ProfilerSink 계약 변경을 Echo 핫패스 보수와 한 라운드에 묶는 것
- 정밀 profiling 확장을 선제적으로 대규모 재개하는 것
- Echo를 당장 메인 개발축으로 재승격하는 것
- 플랫폼 성숙 이전의 과도한 공개 준비

---

# 3. Fuse

## 목표

Mixin 기반 엔진 안정화 모드. Fuse는 평균 FPS 상승을 약속하는 최적화 모드가 아니라, **엔진 비용 질서화 / 프레임타임 꼬리 완화 / 스파이크 완충 / 프레임 붕괴 방지**를 목표로 하는 안정성 레이어다. 경로탐색·충돌·물리 축에서도 `더 똑똑한 결과`가 아니라 **게임이 무너지지 않게 하는 guard / limit / defer / deduplicate / stabilize**만 허용한다.

## Done

- **Area 7 — Pathfinding / Collision / Physics Stability 완료**
  - 경로탐색 예산제, 중복 요청 필터, defer queue, collision memo, velocity clamp, panic protocol 기반 안정화 축을 구현·봉인했다.
- **Area 8 / Area 10 계측 기반 완료**
  - Save / IO Stall, GC / Allocation Pressure 관측·판정 기반을 마련했다.
- **C 실전형 IO/GC 검증 종료**
  - IO/GC Guard는 핵심 판매 포인트가 아니라 책임 경계와 한계가 확인된 부차 축으로 둔다.

## Doing

- Fuse는 현재 `새 기능 개발 대상`보다 **동결·회귀 검증·재잠금 대상**에 가깝게 운용한다.
- 핵심 가치는 **Area 1 / Area 7 중심의 burst stabilizer**에 둔다.
- IO/GC는 `removed / 동결 가능 / 계측 잔존` 후보로 다루며, Fuse의 중심축으로 되돌리지 않는다.
- 엔진 포크 없이 semantic-preserving 최소 개입 원칙을 유지한다.
- Echo 관측값을 보더라도 임계값 판단, recommendation 생성, optimization 적용은 Fuse 내부 책임으로 둔다.
- 필요 시 재진입은 새 기능 개척이 아니라 **Area 1 / Area 7 봉인 상태 점검·문서 정산** 범위로 제한한다.

## Next

- **Bundle C 회귀 검증과 재잠금**
  - tick duration 입력 경로 퇴행 여부 확인
  - `ACTIVE → Early Exit → COOLDOWN` 판독 규칙 고정
- **Fuse 검증선 정리**
  - Stress: sustained 압박 + burst 포함
  - Baseline: UI / 컨테이너 / 저부하 비개입 확인
  - MP: 2~3인 혼합 부하 확인
- **압축형 운영 테스트 프로토콜 정리**
  - 현실적 재현성 있는 시나리오만 Golden 후보로 인정
  - 시나리오 3개 이하
  - OFF 1회 + ON 1회 중심
  - 전체 6~8런 수준
- **Fuse 동결 선언용 최소 문서 묶음 정리**
  - 검증선
  - 판독 규칙
  - 금지선
  - README / 공개 설명 문구
- 공개 포지셔닝을 `AI 최적화 모드`가 아니라 **AI 부하 폭주로 인한 엔진 붕괴를 차단하는 안정성 레이어**로 고정한다.

## Hold

- Fuse를 `AI 최적화 모드`, 평균 FPS 상승 모드, sustained load optimizer로 재포지셔닝하는 것
- 엔진 포크, 구조 재작성, 근사/공격적 알고리즘 교체
- Echo 관측값을 실시간 정책 입력으로 연결하는 자동 튜너화
- IO/GC Guard를 핵심 판매 포인트나 메인 검증선으로 복귀시키는 것
- B42 가능성만으로 라이팅/렌더/IO/GC 대응을 메인라인에 존치하는 것
- `IPathfindingPolicy`, `/fuse status` 같은 정책 인터페이스·편의 기능을 Pulse/Core surface로 올리는 것
- 동일 세이브 / 동일 행동 완전 재현이나 30~50런 규모의 학술형 반복 실험을 기본 검증 방식으로 삼는 것
- `deep analysis 0 = Fuse 미작동`처럼 단일 판독 오류를 근거로 정책을 다시 뜯는 것
- 실전 증명 직후 Fuse 미세 최적화나 Area 1 / Area 7 신규 고도화를 메인 우선순위로 되돌리는 것

---

# 4. Nerve

## 목표

100% Lua 기반 **선택적 안정성 Guard**. 이벤트 재진입·리스너 예외·네트워크 경계 사고를 **동일 틱 철수 / fail-soft / back-off** 방식으로 제한한다. 현재 기준은 **Area 5 v0.1 Final 동결, Area 6 실행 가능 상태 복구, Area 9 운용 검증 전환**이며, 추가 고도화보다 동결·증명·존폐 판단을 우선한다.

## Done

- **Area 5 v0.1 Final 동결**
  - 데이터 즉시 반영, same-tick 시각 갱신 coalescing, weak registry, snapshot 순회, optional fail-soft, overflow bypass 기준을 봉인했다.
- **Area 6 기준선 동결**
  - default OFF / strict OFF / report-only / warn / back-off / same-tick passthrough 원칙을 기준선으로 둔다.
  - `EventDeduplicator`식 사고방식은 폐기하고, self-recursion / listener exception 중심의 최후 Guard로 제한한다.
- **Area 9 구현·검진 후 운용 검증 단계로 이동**
  - 멀티 최적화가 아니라 네트워크 경계 same-tick 철수형 보험 장치로 유지한다.
  - 사건이 없고 로그가 조용한 상태를 정상 성공으로 해석한다.

## Doing

- Nerve는 필수 모듈이 아니라 **선택적 활성화 / dormant guard** 포지션으로 운용한다.
- Core와 분리된 Lua 안정화 레이어 정체성을 유지한다.
- 허용 정책은 **back-off / retreat / non-intervention**뿐이며, 게임 행동 변경 정책은 금지한다.
- Area 5 / Area 6은 개념상 연속되더라도 코드 직접 의존 없이 독립된 최소 안정화로 유지한다.
- Area 6은 완성 기능이라기보다 **incident 수집과 피해 반경 제한을 위한 임시 방파제**로 읽는다.
- 분석 리포트는 Echo 소유로 두고, Nerve는 최소 상태 노출 / 사건 표식 / 에러 서명만 허용한다.
- 현재 단계는 새 설계가 아니라 **문법 / 진입점 / 실행 가능성 / 런타임 증명 복구**다.
- 다음 생산적 이동은 Nerve 추가 고도화가 아니라 Iris 쪽에 둔다.

## Next

- **레포 신뢰성 / 재현성 게이트 통과**
  - P0: conflict marker, Lua 문법, Java 문법, `NerveUtils.lua` 실코드 상태 확인
  - P1: `OnTick` 단일 진입점 원칙 확정
  - P2: fail-soft / 예외 전파 정책을 문장과 주석 수준까지 통일
- **Area 6 vFinal 구현 / 검수**
  - default OFF / strict OFF 반영
  - same-tick self-recursion / listener exception만 제어 트리거로 봉인
  - wrapper 충돌 시 해결보다 Area 6 OFF back-off 우선
  - Kahlua 제약에 맞춘 `pcall` 기반 listener-unit 격리 경로 정리
- **현재 운용 부채 정리**
  - incident가 찍히는 문제 리스너 특정
  - 개별 리스너 수정 또는 격리 정책 재판정
  - `enabled=false` 복구 가능 여부 판단
  - stale `xpcall` / DEBUG 주석 정리
- **검증선 정리**
  - Area 5/6 개입 경로 발동 증명
  - ON/OFF 의미 불변 검증
  - S1 기본값 검증선: 설치 상태에서도 Area 6 default는 바닐라와 동일해야 함
  - 최소 재현 시나리오와 회복 시간 판독 기준 정리
- **운용 문서 정리** 
  - Failure Atlas / 연구 단계 / 실패 귀속 좌표계 계열 표현을 current 설명에서 제거하고, 필요 시 rejected predecessor trace로만 보존한다.
  - Nerve 자기 제한 정책을 문장화한다. - Nerve / Nerve+ 배포 경계를 정리한다.
  - `Lite / Full` 오해를 부르는 제품 언어를 폐기한다.
- **Area 9 운용 검증**
  - 실제 멀티 / 모드팩 환경에서 조용히 incident 여부를 관찰한다.
  - 사건 발생 시 보험 장치가 세션 지속성에 기여했는지만 본다.
  - 사건이 거의 없으면 기능 부족이 아니라 정상 성공으로 읽는다.

## Hold

- Nerve를 Lua 병목 최적화 모드나 필수 성능 모듈로 재포지셔닝하는 것
- `drop / delay / defer / reorder / queue` 정책
- 의미 기반 allowlist / whitelist / AlwaysAllow 정책
- Area 6에서 `EventPriority` / `Governor` / `Throttler`를 조기 도입하는 것
- Area 6 래퍼 체인 고도화나 공존 전략을 기본 방향으로 삼는 것
- Area 5에서 시간 기반 debounce, tick 넘김 캐시, visibility 기반 flush 판단을 도입하는 것
- Area 5와 Area 6의 상태 공유 또는 코드 직접 의존
- Nerve 자체 리포트 시스템 구축
- Pulse로 기능을 상향 이동하는 것
- Area 8(IO/Save), Area 10(GC/Memory) 기능 개시
- Area 9를 멀티 최적화, 네트워크 제어, 패킷/핑 개선 전장으로 여는 것
- Area 9에서 전역 상시 `pcall`, 영구 차단, 자동 blacklist/whitelist를 기본화하는 것
- Area 9를 네트워크 진입 훅 밖의 일반 이벤트 / UI / 렌더 축으로 확장하는 것
- Area 9 incident 조건을 비율 / 빈도 / 가중치 / 추세 기반으로 고도화하는 것
- Failure Atlas / 연구 단계 / 실패 귀속 좌표계 계열 표현을 current 제품 설명으로 되살리는 것
- v2.1 구현 기준서를 다시 설계 문서처럼 재개방하는 것
- Area 6 문법 / 진입점 정리 전에 새 트리거·새 행동·새 정책을 추가하는 것
- Fuse 자동정책 경로를 재활성화하는 것

---

# 5. Iris

## 목표

100% Lua 기반 위키형 정보 모드.
오프라인에서 봉인한 fact / outcome / source / description을 런타임에서 해석·추천·비교 없이 안정적으로 표시한다.

## Done

* Iris의 제품 정체성과 정보 표시 위계를 고정했다.

  * 표시 위계는 **기본 정보 → 의미(주 소분류) → 활용(레시피/상호작용) → 메타**로 유지한다.
  * 분류 데이터는 기본 UI 전면이 아니라 메타 영역에 격리한다.
  * `primary_subcategory`는 정렬 / 추천 기준이 아니라 browsing anchor로 사용한다.
  * 주 소분류 설명 문장은 자동 기본값이 아니라 후보 템플릿으로 취급한다.

* current authority와 정보 모델의 책임 경계를 고정했다.

  * 최상위 기준은 `Philosophy.md`로 둔다.
  * 핸드오버 / 세션 요약 / 과거 작업 문서는 current authority가 아니라 참고물로만 읽는다.
  * current source / rendered / runtime chunk chain만 current authority로 읽고 staging / fixture / diagnostic / historical / predecessor artifact는 비교·진단·provenance 용도로만 유지한다.
  * Evidence는 행동 가능성 모델이 아니라 **결과 상태 모델**로 유지한다.
  * Recipe / Right-click / Static capability / Context Outcome은 서로 다른 Source 계열로 유지한다.
  * 런타임은 오프라인에서 봉인한 fact / outcome / source / description을 표시만 한다.

* Context Outcome과 Right-click evidence의 판정 기준을 고정했다.

  * Context Outcome은 문서 기반 사실을 기계화하는 오프라인 공급자로 두고 Iris 런타임은 이를 소비한다.
  * Right-click 계열 정보는 `item-dependence + state-change proof`를 기준으로 판정한다.
  * canonical 기준은 메뉴 존재가 아니라 `executing_tool + external_target + persistent_change`다.
  * PASS / NO / REVIEW를 primary decision으로 두고 STRONG / WEAK는 PASS 이후 uniqueness overlay로만 사용한다.
  * 메뉴명 / UI 구조 / 비활성 표시 여부는 보조 관찰 정보로만 둔다.

* evidence 축을 결과 상태 중심으로 정리하고 의미 기반 capability 확장을 중단했다.

  * 넓은 capability label은 단일 결과 상태 단위로 해체하거나 evidence 축에서 제외한다.
  * Equip / Use / Passive와 느슨한 행동 가능성 일반화는 기본 evidence 체계로 확장하지 않는다.
  * Recipe 기반 evidence는 안정적인 축으로 유지한다.
  * 개별 아이템 정보는 `분류 / 증거 체계 → Outcome source → 결과 상태 fact → 필요 시 설명` 순서로 다룬다.
  * 설명 왜곡은 런타임 설명 엔진이 아니라 upstream fact / tag / tuple integrity 문제로 다룬다.

* DVF System / Iris Artifact Registry / Publish Boundary의 책임 경계를 봉인했다.

  * DVF System / DVF Body Compiler는 승인된 `facts / decisions / profile / body_plan`으로 개별 아이템 본문을 결정론적으로 생성·검증하는 오프라인 body compiler로 제한한다.
  * Iris Artifact Registry는 source / rendered / runtime / package identity와 artifact lifecycle, validation, seal, cutover, stale reentry guard, runtime compatibility를 관리한다.
  * Publish Boundary는 public text acceptance, semantic quality acceptance, package publication, release / Workshop readiness, manual QA를 별도로 관리한다.
  * DVF Body Compiler / Registry Authority / Registry Runtime Compatibility / Publish Boundary의 완료 상태는 서로 대체하지 않는다.
  * `DVF Core`와 Legacy Combined DVF Governance Route는 historical predecessor로만 유지한다.

* compose / resolver / runtime / bridge contract를 current 기준으로 봉인했다.

  * compose default authority는 `compose_profiles_v2.json + body_plan`으로 유지한다.
  * `selected_role`은 native resolver authority / trace로 유지한다.
  * runtime vocabulary는 `adopted / unadopted`를 canonical로 사용하고 `active / silent`는 historical / diagnostic alias로만 유지한다.
  * runtime deployable authority는 Lua chunk manifest + chunk files로 유지한다.
  * Lua bridge exporter의 default route도 chunk authority를 따르며 monolith export는 historical / diagnostic 용도로만 허용한다.
  * legacy compatibility mapping과 predecessor bridge는 current fallback이나 default authority로 사용하지 않는다.

* Iris의 주요 runtime / build refactor와 current contract 정리를 완료했다.

  * protected-call boundary를 `IrisProtectedCall`로 중앙화했다.
  * UseCaseDescriptions를 facade + Lua chunk 구조로 외부화했다.
  * `IrisDesc` compatibility wrapper와 기존 public require contract를 보존하면서 내부 구현을 정리했다.
  * Browser state/cache, Browser/Wiki shared detail model, scroll behavior와 compatibility adapter 경계를 current 구조로 정리했다.
  * current / historical / diagnostic route와 package identity, disposable execution, stale artifact reentry 방어를 current contract에 맞게 정리했다.
  * 추가 build-tool decomposition과 repository cleanup은 실제 필요성이 없는 범위에서 deferred / no-op으로 닫았다.

* Naturalization 평가와 current runtime adoption을 완료했다.

  * reusable public-text evaluator와 assessment를 current route에 통합했다.
  * 검증된 candidate를 current rendered / Lua runtime payload에 채택하고 canonical package identity와 current-route closure를 완료했다.
  * current runtime payload와 RTC-certified payload의 applicability는 분리해서 유지한다.
  * 이 완료를 RTC certification, package publication, release / Workshop / B42 readiness로 확대하지 않는다.

* Manual In-Game Validation QA를 current contract 기준으로 완료했다.

  * Iris Browser는 all-item Browser로 유지하며 item-entry visibility와 Layer 3 body / source quality를 분리한다.
  * raw token / raw nil / table address / broken placeholder가 사용자 표면에 노출되지 않는 기준으로 practical in-game validation을 닫았다.
  * 이 검증만으로 release readiness / Workshop readiness / tooltip completion을 선언하지 않는다.

* Semantic UI Exposure를 no-exposure disposition으로 닫았다.

  * `quality_state`는 offline / internal authoritative signal로 유지한다.
  * `quality_exposed`는 reserved inactive로 둔다.
  * Browser / Wiki / Tooltip은 quality 판정을 badge, copy, sorting, filtering, hiding, recommendation, trust / confidence 표시에 사용하지 않는다.

* closed readpoint의 production 승격과 future reopen 경계를 봉인했다.

  * Structural Signal / Layer4 / Acquisition Lexical 계열 readpoint는 production / publish / runtime input으로 승격하지 않는다.
  * 재개방은 새 입력 authority, 명시적 successor / correction scope, 또는 별도 approved plan이 있을 때만 허용한다.
  * readiness evidence나 개별 closeout / 검증 PASS를 live completion, release / Workshop / B42 / deployment readiness 또는 semantic quality acceptance로 확대하지 않는다.

## Doing

* Iris는 vanilla-first MVP를 **DVF Body Compiler 기반 3-3 body production + Browser / Wiki / Tooltip 표시 안정화** 중심으로 유지한다.

  * 새 evidence 축이나 의미 기능 확장보다 현재 body 생성과 all-item Browser / Wiki / Tooltip 동작의 안정성을 우선한다.
  * Browser item-entry visibility와 Layer 3 body / source quality를 별도 문제로 다룬다.
  * Iris를 AI 위키, 의미 추론기, 추천 엔진, 품질 판단 UI로 확장하지 않는다.

* 봉인된 authority / runtime / responsibility contract를 유지하면서 현재 표시 경로의 안정성을 보존한다.

  * 런타임은 오프라인에서 봉인된 fact / outcome / source / description을 소비하는 표시 계층으로 유지한다.
  * current source / rendered / runtime chunk chain과 Lua chunk manifest + chunk files 기반 deployable authority를 유지한다.
  * public require contract와 current compatibility surface를 보존하고 legacy / historical / diagnostic artifact를 current fallback으로 되살리지 않는다.
  * DVF Body Compiler / Iris Artifact Registry / Publish Boundary의 책임과 완료 상태를 서로 대체하지 않는다.
  * 이미 닫힌 readpoint나 authority reconstruction은 새 입력 authority 또는 명시적 successor / correction scope 없이 현재 작업으로 되돌리지 않는다.

## Next

* 현재 Iris codebase optimization follow-up의 남은 `partial` 경계를 정리한다.

  * 실제 PZ Kahlua engine-object binding evidence가 없는 `IrisObjectAccess` generic fast-path는 검증 없이 production route로 채택하지 않는다.
  * 추가 runtime optimization 후보는 측정 또는 안전성 근거가 있을 때만 별도 scope로 평가한다.
  * optional benchmark나 deferred / no-op 후보를 이미 완료된 functional validation의 blocker로 소급하지 않는다.
  * 남은 항목은 구현 강행보다 `adopt / defer / no-op` 중 하나로 disposition을 명확히 닫는 것을 우선한다.

* 현재 Iris를 packaging / release preparation 단계로 넘길지 별도 release scope에서 결정한다.

  * package 검증 기준은 `Iris/tools/package_iris.ps1 -Clean -Zip`로 둔다.
  * packaging을 source / rendered / Lua bridge / runtime authority 재구축이나 새 migration 권한으로 확대하지 않는다.
  * release-note / publication / Workshop 배포 여부는 packaging 완료와 별도로 판정한다.

* 실제 release를 진행할 경우 **release checklist / full manual QA**를 별도 scope로 수행한다.

  * Browser / Wiki / Tooltip 동작과 package ZIP / install path / in-game visibility를 확인한다.
  * raw token / raw nil / table address / broken placeholder가 사용자 표면에 노출되지 않는지 확인한다.
  * 기존 practical in-game validation과 functional closeout만으로 release / Workshop / B42 readiness를 선언하지 않는다.
  * PZ latency / heap / FPS / frame-time 개선은 별도 raw measurement가 있을 때만 주장한다.

* ROADMAP과 구현 / 검증 문서의 current-state 정합성을 유지한다.

  * ROADMAP에는 현재 상태와 다음 게이트만 남긴다.
  * round별 attempt / hash / commit / validation count / evidence root는 각 산출물이나 `DECISIONS.md`에서 추적한다.
  * docs sync는 current authority를 다시 정의하는 작업이 아니라 현재 상태와 책임 경계를 일치시키는 작업으로 제한한다.
  * 새 후속 작업은 해결하려는 책임 축과 `rollback / correction / optimization / package-release readiness` 등의 scope를 먼저 명시해서 연다.

## Hold

* release / 배포 readiness를 과대 선언하는 것

  * targeted validation, manual in-game validation, roadmap / refactor closeout, governance seal을 release readiness / Workshop readiness / B42 readiness / packaging / deployment 완료로 확대 해석하지 않는다.
  * 각 validation / review / seal / closeout은 승인된 scope 안에서만 유효하며 다른 readiness 축을 자동으로 대체하지 않는다.

* non-current evidence를 current authority나 mutation 권한으로 승격하는 것

  * staging / generated / diagnostic / fixture / historical / predecessor / rollback artifact는 비교·진단·provenance 용도로만 유지한다.
  * rendered-only output, runtime chunk, bridge output, package projection을 source authority로 역승격하지 않는다.
  * tracked / ignored 상태, 숫자 일치, vocabulary 치환, parity / dry-run evidence만으로 authority migration이나 cutover approval을 선언하지 않는다.
  * legacy bridge / monolith / stale artifact / predecessor payload를 current runtime / package / compose fallback으로 되살리지 않는다.
  * 서로 다른 runtime generation을 동시에 current authority로 유지하지 않는다.

* DVF System / Iris Artifact Registry / Publish Boundary의 책임 경계를 다시 합치는 것

  * DVF Body Compiler / Registry Authority / Registry Runtime Compatibility / Publish Boundary의 PASS나 closeout을 서로 대체하지 않는다.
  * body generation, artifact authority / runtime compatibility, publication / release 판단의 책임 축을 하나의 통합 PASS로 축소하지 않는다.
  * retired `DVF Core`, 단독 `DVF PASS`, Legacy Combined DVF Governance Route를 current 통합 권위로 되살리지 않는다.

* sealed closeout과 실패 증거를 세탁하거나 재작성하는 것

  * 기존 FAIL / receipt / review / seal / terminal evidence를 후속 PASS를 이유로 삭제하거나 덮어쓰지 않는다.
  * metadata correction이나 evidence repair를 명령 재실행, protected mutation, failure history 제거를 숨기는 우회로로 사용하지 않는다.
  * stale marker, temporary tooling failure, historical noncoverage 같은 단일 진단 신호만으로 current defect나 successor 실행 권한을 만들지 않는다.

* legacy adapter / fallback / runtime-side repair를 current path로 복귀시키는 것

  * implicit legacy fallback, runtime-side compose rewrite, external repair, hidden adapter dependency를 새 default path로 만들지 않는다.
  * legacy `sentence_plan`, diagnostic-only compatibility mapping, monolith export를 current compose / runtime authority로 복귀시키지 않는다.
  * `selected_role`을 legacy residue나 제거 대상으로 오해하지 않는다.
  * compatibility wrapper는 current contract 보호 범위를 넘어 새 authority로 확장하지 않는다.

* quality / publish / runtime vocabulary를 혼동하는 것

  * `adopted / unadopted`를 quality PASS, publish state, suppression, deletion 의미로 사용하지 않는다.
  * legacy `active / silent`를 current runtime vocabulary로 되살리지 않는다.
  * `quality_state`는 offline / internal signal로 유지하고 `quality_exposed`를 별도 product decision 없이 활성화하지 않는다.
  * Browser / Wiki / Tooltip에서 quality 판정을 badge, copy, sorting, filtering, hiding, recommendation, trust / confidence 표시에 사용하지 않는다.

* 설명 계층을 해석 / 추천 / 비교 / 재작성 엔진으로 확장하는 것

  * 런타임에서 fact / outcome / source / description의 의미를 다시 추론하거나 사용자 행동 권장으로 변환하지 않는다.
  * 수치 비교, 체감 의미 해석, 조건부 추천, 자동 설명 확대를 Iris의 기본 기능으로 도입하지 않는다.
  * 데이터 오분류나 설명 왜곡을 UI 숨김 / 정렬 / 예외 누적으로 봉합하지 않는다.
  * Iris를 AI 위키, 추천 엔진, 의미 추론기, 품질 판단 UI로 재포지셔닝하지 않는다.

* Evidence / Source / Outcome 모델을 느슨한 행동 가능성 모델로 되돌리는 것

  * Evidence는 결과 상태 모델로 유지하고 넓은 semantic capability를 기본 evidence 축으로 되살리지 않는다.
  * Context Outcome을 runtime inference나 메뉴 문자열 기반 자동 outcome 생성기로 바꾸지 않는다.
  * Right-click evidence를 메뉴 존재 / 메뉴명 / UI 구조만으로 채택하지 않고 `item-dependence + state-change proof` 기준을 유지한다.
  * PASS / NO / REVIEW decision과 STRONG / WEAK uniqueness overlay를 다시 혼합하지 않는다.
  * Equip / Use / Passive나 단일 결과 상태로 해체되지 않은 범용 capability label을 current evidence 축으로 승격하지 않는다.

* Recipe / 목록 UI 정책을 전역 semantic grouping으로 확대하는 것

  * 연관 레시피를 행동 문장 단위로 재구성하거나 전역 기능 동등성 엔진을 도입하지 않는다.
  * UI 목록 단계의 DisplayName 중심 접기를 semantic equivalence authority로 확대하지 않는다.
  * 레시피 / 섭취 / 장착 / 무기 사용 등 서로 다른 정보 축을 편의를 이유로 다시 혼합하지 않는다.

* closed readpoint를 production / publish target으로 승격하거나 새 authority 없이 재개방하는 것

  * Structural Signal / ACQ_DOMINANT / Layer4 / Acquisition Lexical / Silent 21 같은 closed readpoint를 current production authority나 user-facing 기능 후보로 승격하지 않는다.
  * 새 입력 authority, 명시적 successor / correction scope, 또는 별도 approved plan 없이 closed readpoint를 다시 열지 않는다.
  * 조건부 reopen 가능성을 자동 후속 작업, runtime mutation, policy expansion, publish 권한으로 해석하지 않는다.
  * 과거 count / hash / branch / validation 결과만으로 새 current work item을 만들지 않는다.
  * 재개방이 필요하면 기존 current authority를 보존하는 별도 bounded scope로 연다.

## Backlog

* 외부 모드 / 외부 데이터 생태계 연동을 structure-only / normalization-first 원칙으로 확장
* 내부 `.Iris` 정규화와 외부 JSON / SQLite import-export 정책 구체화

# 6. Frame

## 목표

Project Zomboid 모드팩의 상태를 시간축 위에서 **기록·비교·되돌리는 버전 관리 레이어**.  
대상은 개별 모드가 아니라 **팩 상태(pack state)** 이며, 일반 VCS처럼 브랜치/병합/자동 해결을 제공하는 것이 아니라 **snapshot / compare / rollback**에 집중한다.

## Doing

- Frame은 아직 구현 전선이 아니라 **제품 축 정의 / 범위 봉인 단계**로 둔다.
- 팩 상태(pack state)를 1급 객체로 다루는 방향을 유지한다.
- **환경만 다루고 월드/세이브는 제외**한다.
- **수동 스냅샷 = 공식 기록 / 자동 스냅샷 = 안전망** 위계를 유지한다.
- 자동 저장은 **5/10/30/60분 주기 + 최근 10개 롤링** 원칙을 기본값 후보로 둔다.
- 원본 설정 보존 + **오버라이드 파일(내 설정)** 구조를 기본으로 유지한다.
- 목록 / 순서 / 설정 재구성 + fingerprint 동일성 확인 모델을 유지한다.
- 문제 모드 지목, 자동 추천, 자동 정렬, 자동 해결을 하지 않는다.
- UI/용어는 판단보다 **기준점 / 자동 저장 / 달라짐 / 비교 / 되돌리기** 같은 사실+행동 언어를 우선한다.
- 외부 툴보다 **모드 내부 레이어**를 메인라인으로 유지한다.

## Next

- 수동 스냅샷 / 자동 스냅샷 UI 위계를 문서화한다.
- baseline / overrides / manifest / fingerprint 최소 스펙을 정리한다.
- import 단계 검증 규칙과 복구 화면 UX를 정리한다.
- 공개 공유 포맷(ZIP + JSON)과 내부 `.frame` 캐시의 책임 경계를 구체화한다.
- `모드 개별 관리`가 아니라 `팩 상태 관리`로 읽히는 용어 체계를 정리한다.

## Hold

- 문제 모드 자동 지목
- 자동 추천 / 자동 정렬 / 자동 해결
- Frame 내부 설정 편집기
- 외부 런처 / 관리자 툴로의 메인라인 전환
- 모드 원본 파일 저장 / 배포를 통한 완전 복원
- `.frame`을 외부 공개 표준 포맷으로 강제하는 방식
- 변화 감지 해석에 의존해 자동 스냅샷을 기본 생략하는 정책

## Backlog

- 첫 화면 / 복구 화면 등 `한 방`이 되는 메인 UX 다듬기
- 공유 UX와 권리 / 약관 / 재현성 리스크를 함께 고려한 전달 방식 정리
- 리소스팩 상태까지 시간축 위에 얹을 가치가 있는지 장기 검토

---

# 7. Cortex

## 목표

Pulse, Echo, Fuse, Nerve, Iris, Frame, Canvas에 넣기 부적절한 **편의 기능 / 제작 보조 / 가이드 성격 기능**의 격리 구역.

## Doing
- Core와 제품 모듈을 비대화시키지 않기 위한 격리 역할 유지
- helper / 편의 / 가이드 / 제작 보조를 Pulse가 아니라 Cortex로 보내는 기준 정리
- Canvas/Frame/Iris 같은 **실제 제품 축**을 Cortex가 임시 수용하지 않는다는 원칙 유지

## Next
- 실제로 Cortex에 들어갈 기능과 들어가면 안 되는 기능 분리 기준 작성
- 제품 축과 편의 축이 헷갈릴 때의 판정 체크리스트 문서화
- Canvas / Frame / Cortex 경계 문구를 최신 합의 기준으로 정리

## Hold
- 리소스팩 제품 축의 임시 수용
- 채택 마찰 해소를 명분으로 Core 기능을 우회 수용한 뒤 역이관하는 방식
- Canvas를 시작하기 전 Cortex에서 먼저 시험 운영하는 경로

# 8. Canvas

## 목표

외부 툴이 만든 리소스팩 산출물을 읽어 **로드 순서와 덮어쓰기 이후의 최종 적용 상태를 계산·검증·비교·설명**하는 독립 모듈.  
리소스 제작 툴이 아니라 **리소스 적용 상태 관리 플랫폼**으로 둔다.

## Doing

- Canvas는 아직 구현 전선이 아니라 **제품 축 정의 / v1 가치 검증 단계**로 둔다.
- Canvas를 **독립 모듈로만 시작**한다는 기준을 유지한다. (`Canvas로 시작 / 아니면 폐기`)
- 제작 툴 / 정책 도구 / Frame 대체물이 아님을 유지한다.
- Pulse는 기반 capability만 제공하고, Canvas가 인덱싱·최종 상태 계산·충돌 분석·설명 UX를 맡는 경계를 유지한다.
- 게임 리소스를 1차 대상으로 하고, 모드 리소스 확장은 후행 축으로 둔다.
- v1 pain point 3개를 함께 다루되, 중심 가치는 **적용 결과 / 충돌 가시화**에 둔다.
  - 최종 적용 결과 / 충돌 / 로드 순서 가시성 부족
  - 패킹 / 경로 / 구조 / ID 민감성으로 제작이 쉽게 깨지는 문제
  - 버전 / 서버 / 배포 불일치

## Next

- 최종 적용 상태 계산 모델을 정리한다.
- 충돌 분석 / 프리플라이트 검증 / 차이 리포트 최소 기능선을 정리한다.
- 입력 / 내부 캐시 / 출력 / 공유 포맷을 구체화한다.
- ZIP + JSON(+ `.pack`) 공개 포맷과 내부 `.canvas` 정규화 캐시의 책임 경계를 명시한다.
- 외부 툴 산출물 import → 검증 → 비교 → 설명 워크플로우 초안을 작성한다.

## Hold

- 리소스 제작 툴화
- 리소스 원본 파일 자동 수정 / 자동 재패킹
- 정책 심판 / 자동 병합 / 정답 추천 / 최적 순서 제시
- Frame과의 통합 설계
- `.canvas`를 외부 공유 표준으로 미는 방향
- 외부 사례 구조를 그대로 이식하는 방식

## Backlog

- 게임 리소스 대상 v1 이후 모드 리소스 확장 전략
- 서버↔클라 / 로컬↔배포 상태 비교 UX 정리
- 리소스팩 상태를 Frame 시간축과 느슨하게 연동할 가치가 있는지 장기 검토

---

# 9. 플랫폼 브랜딩 / 공개 전략

## 목표

플랫폼을 전면에 내세우기보다 **킬러앱이 먼저 가치를 증명하고, 기반은 뒤늦게 드러나는 구조**를 유지한다.  
Pulse는 처음부터 “새 Java 로더”로 경쟁하는 브랜드가 아니라, 검증된 모듈들의 공통 기반으로 후노출한다.

## Doing

- 최상위 기준은 **`Philosophy.md` 하나**이며, 과거 핸드오버 / 세션 요약은 작업 문서로만 취급한다.
- `Pulse`를 최우선 브랜드 후보로 유지한다.
- 킬러앱 우선 공개 전략을 유지한다.
- `새 Java 로더` 정면 경쟁 프레이밍을 피하고, **결과물 선공개 → 기반 후노출** 구조를 유지한다.
- 공개 / 배포 메시지의 핵심 리스크를 `기능 부족`보다 **플랫폼 오염 방지 / 채택 마찰 제어**로 둔다.
- 각 모듈은 플랫폼 기능이 아니라 독립 가치로 먼저 설명한다.
  - Iris: 위키형 정보 모드
  - Nerve: 선택적 안정성 Guard
  - Fuse: 엔진 안정성 레이어
  - Frame: 팩 상태 기록·복원 레이어
  - Canvas: 리소스 적용 상태 관리 플랫폼

## Next

- README / Architecture / 로고 / 모듈 네이밍과의 정합성을 점검한다.
- 최적화 모드 공개 순서와 플랫폼 인식 전략의 연결을 정리한다.
- 공개 순서를 `Iris → Nerve → Fuse → Pulse+Echo → Nerve+ / Fuse Pulse 의존 전환` 기준으로 문서화한다.
- 설치 / 실행 마찰 최소화 원칙을 문서화한다.
  - PulseLauncher 체감 최소화 UX 원칙
  - Steam 실행 옵션 / 바로가기 / 번들 안내 구조
  - 유저가 `추가 플랫폼을 깐다`고 느끼지 않게 만드는 설치 문구
- `Philosophy.md`에는 금지선 / 역할 경계만 남기고, 기대치 문구는 별도 ReleaseStrategy 문서로 분리할지 검토한다.

## Hold

- 법적 / 최종 브랜드 확정 선언
- 플랫폼 선공개 루트
- 자동 인스톨러를 현 단계 기본 해법으로 채택
- Pulse를 Fabric / Forge 대체재처럼 직접 포지셔닝하는 것
- 킬러앱 가치를 증명하기 전에 Core capability를 먼저 홍보하는 것


---

# 10. Iris residual refactoring follow-up

## Done

- Phase 0 inventory, runtime characterization, API/protected-surface baseline, evidence-role schema를 생성했다.
- deterministic presentation projection, copy-on-read, Wiki unit profile, Tooltip 분리, lazy debug gate를 구현했다.
- `compose_layer3_io`의 기존 계약을 유지한 Windows strict-path 지원과 registry runtime record path leaf 추출을 구현했다.
- 다섯 current-route 테스트와 current/historical/diagnostic evidence 역할을 등록했다.
- standalone runtime acceptance, production Lua syntax, disposable package, supported API, Python import/CLI/byte matrix를 실행했다.
- Codex Reviewer finding 1건(UNC temp-root cleanup)을 수정했고 최종 재검토 finding 0건을 확인했다.
- historical pinned corpus와 current taxonomy의 denominator equality 결합을 제거하고, pinned historical set의 taxonomy 포함 관계만 유지했다.
- diagnostic fingerprint의 Windows doubled-separator/disposable-overlay 비결정성을 제거하고 raw `77 tests / 3 failures / 26 errors`의 29 findings를 22개 exact owner disposition으로 비차단 처리했다.
- protected surface의 EOL-only 차이와 optional ignored package projection 부재를 의미 mutation에서 분리했다.
- 272자 tracked staging 경로를 짧은 staging-only namespace로 100% rename해 tracked 상대 경로 최대치를 221자로 낮췄다. `_docs/round3`, owner/reviewer input과 문서 identity는 보존했다.
- short-path clean clone에서 protected surface, current `150/150`, historical `285/285`, diagnostic adapter, full discovery `529/529`, Lua syntax `97` files, disposable package `97` Lua / `12` Layer 3 files가 모두 exit `0`으로 통과했다.
- Codex Reviewer의 path-only approval P1을 exact LF-normalized successor SHA-256 결속으로 수정했다. 최종 `c1fa281e` clean clone surface는 supported `20` / protected `26` / package Lua `90`으로 재통과했다.

## Blocked / Partial

- 최종 reviewer-hardening commit `c1fa281e` exact subject에 대해 receipt interpreter와 결속된 clean-checkout full-gate 전체를 아직 다시 실행하지 않았다.
- Project Zomboid 인게임 Browser/Wiki/Tooltip/logging 검증과 screenshot/log 증거는 unattended 환경에서 수행할 수 없어 `runtime_ui=blocked`다.
- 원본 작업트리에서 일부 full-discovery producer가 tracked facts/evidence를 갱신하는 실행 부작용이 확인됐다. 사용자 변경과 혼재한 파일을 자동 복원하지 않았으며, 후속 validation execution isolation 범위에서 해결해야 한다.

## Next

- 별도 owner 세션에서 Project Zomboid runtime UI 5개 case를 실행하고 screenshot 또는 PZ log를 결속한다.
- `c1fa281e` exact subject를 receipt interpreter, no `PYTHONPATH`, `-B -s` 조건으로 clean-checkout full-gate 재검증한다.
- 테스트와 evidence producer의 모든 output을 disposable root로 격리하고, 성공·실패 어느 경로에서도 source working tree mutation과 residue가 0인지 검증한다.
- 추가 Iris 리팩터링의 필요성과 범위는 이 안정화 closeout과 별도로 평가한다. 이 항목의 `partial`, `Next`, `Hold` 상태를 구조 후보의 선제 배제 규칙으로 사용하지 않는다.

## Hold

- BOM 정규화
- 추가 도메인 package 이동
- registry giant 분해
- historical denominator 축소 또는 sealed evidence 재작성
- `complete`, release-ready, Workshop-ready, B42-ready 선언

현재 구현과 자동 closeout blocker correction은 수용됐지만 최종 상태는 `partial`이다. 남은 범위는 runtime/API 구조 개편이 아니라 validation execution isolation, final receipt-bound clean-checkout, manual runtime UI evidence다. 기존 근거는 `Iris/_docs/refactor/residual_refactor/final_validation_matrix.json`, successor 실행 근거는 `cfa9f0d5..c1fa281e` 구현 series와 short-path clean-clone validation log다.

---

# 11. Iris repository/runtime lightweighting

## Done

- Common Track의 lifecycle inventory, 외부 work/result root, output-isolation, producer migration, archive/restore, cleanup 및 closeout을 완료했다.
- physical inventory를 `4,842,336,252` bytes에서 `1,338,324,791` bytes로 줄였다. ignored giant는 `4 -> 0`, diagnostic-only bytes는 `3,505,238,016 -> 0`이며 current authority와 historical reproduction은 보존했다.
- Track Order를 `runtime_first`로 결정하고 Runtime Track Changes 5~7을 채택했다.
- Runtime adoption 뒤 Tooling Track Change 8을 별도 평가했다. Inventory는 `497 recursive / 484 root-direct`, archive/delete eligible candidate와 helper extraction은 각각 `0`이며 세 producer 공통화 gate가 성립하지 않아 구현·이동·삭제 없는 no-op으로 채택했다.
- Browser boot eager build를 제거하고 first-use build와 same-generation warm cache 재사용을 적용했다.
- Layer3 11개와 UseCase 9개 청크에 deterministic index/internal lookup router를 추가했다. 단일 조회는 최대 한 청크, Alt Tooltip line-count는 설명 청크 0개를 로드하며 direct compatibility facade는 전체 table 계약을 유지한다.
- automated current/historical/diagnostic/package/Lua/purity route와 receipt-bound full-gate Run A/B 및 deterministic compare를 PASS로 닫았다.
- 삭제된 격리 checkout과 무관하게 검토된 최종 소스 11개 파일을 `ae7b3172cc80b5bf3b2aaed15654d41f707c9134`로 복구해 `main`에 보존했다.
- protected-surface v2 successor는 삭제된 임시 subject를 durable v1 manifest blob으로 attestation하고, Change 8 exact successor current route `202/202`를 clean checkout에서 통과했다.
- 2026-08-10 owner가 계획 범위의 Project Zomboid Browser/Wiki/Tooltip/localization/log 인게임 검증을 완료했다고 attestation해 마지막 수동 runtime 축을 닫았다.

## Measurement limits

- 저장소 물리량은 `72.36%` 감소했지만 LLM prompt/token 사용량을 before/after로 계측하지 않았으므로 token 효율 향상률은 미측정이다.
- raw PZ before/after timing sample은 repository evidence로 첨부되지 않았으므로 성능 개선 수치는 승인하지 않는다.

## Next

- 계획 범위의 필수 후속 작업은 없다.
- PZ 성능 개선율이 필요할 때만 동일 build/machine/save/mod-set의 raw before/after timing sample을 별도 측정 범위로 연다.

## Hold

- 미측정 token 절감률이나 PZ timing 개선율 주장
- current authority 또는 historical reproduction input을 storage cleanup 대상으로 재분류
- public facade/global 제거, positional schema migration, registry giant split
- release-ready, Workshop-ready, multiplayer 또는 long-session 안정성 선언

근거는 `Iris/_docs/refactor/repository_runtime_lightweighting/`의 baseline/final inventory, track-order decision, runtime benchmark, selected-track/terminal receipt, validation checkpoint manifest와 2026-08-10 owner attestation이다.

---

# 12. Iris repository evidence/intermediate artifact lightweighting

## Done

- lifecycle v1 full manifest pair를 exact reconstruction 가능한 v2 representation으로 교체했다.
- naturalization ignored historical payload를 repository-local CAS 237 objects + reference로 정규화하고 47개 current-bound tracked exception과 동적 ignored-tool consumer 입력 1개(11,381 bytes)는 physical exception으로 유지했다.
- `2105`의 byte-identical canonical pair를 한 CAS object로 합치고 기존 logical path consumer에 transparent resolver를 추가했다.
- `_archive` 86개 ignored file을 외부 deterministic ZIP으로 검증·복원 가능하게 보관한 뒤 local 원본을 제거했다.
- boot eager require에서 Recipe/Moveables/Fixing/Classifications 네 static module을 제거하고 first-use 실패 경고/cache/reset 계약을 유지했다.
- compatibility/full-materialization과 Browser allocation 후보의 repository consumer census를 만들고 source 변경 없이 deferred로 disposition했다.
- ignored tooling의 동적 Path consumer를 AST/string-fragment scan에 포함하고 누락 입력 1개를 11,381-byte physical exception으로 복원했다. CAS restore는 absolute/parent traversal/output escape/reparse path를 거부한다.
- Codex Reviewer의 원 finding과 closeout 정합성 finding을 모두 해소해 최종 PASS를 받았다.

## Measurement

- 1차 baseline `4,842,336,252` bytes에서 현재 `1,080,954,330` bytes로 누적 `3,761,381,922` bytes, `77.68%` 감소했다.
- 1차 final `1,338,324,791` bytes와 비교하면 이번 작업은 `257,370,461` bytes, `19.23%`를 추가로 줄였다.
- 최악의 전체 repository scan에서 동일 입력 밀도를 가정한 처리량 대리 지표는 `3.62x -> 4.48x`다. 실제 tokenizer와 Codex token usage는 미계측이므로 일반 작업의 확정 token 개선율로 사용하지 않는다.

## Complete / Non-claims

- 계획 범위의 terminal batch에서 lifecycle/repository evidence/current/historical/focused runtime/Lua/package PASS를 기록했고, 2026-08-10 repository owner가 수동 PZ 인게임 검증 완료를 attestation했다.
- raw diagnostic의 기존 overlay/tooling 결손 3 failures/9 errors는 보존한다. receipt-bound full-gate Run A/B와 deterministic compare는 실행 불가능한 경계를 사실대로 유지하고 owner closeout scope amendment로 non-blocking out-of-scope 처리했다.
- Change 4의 나머지 unique derived view 보존은 완료를 막지 않는 evidence-based defer다.
- Codex Reviewer final review는 PASS이며 추가 actionable finding이 없다.
- Project Zomboid/Kahlua heap과 first-use latency raw sample이 없으므로 정량 runtime 성능 개선은 claim하지 않는다.
- 실제 LLM prompt/token before-after corpus와 cache telemetry가 없어 token 효율은 physical-byte proxy까지만 승인한다.

## Hold

- deleted historical Git object 복구를 경량화 완료 조건으로 다시 도입
- 외부 mod consumer 조사 없는 public facade/global 변경
- heap/allocation sample 없는 Browser cache/search/variant 최적화
- 서로 다른 tracked/ignored/CAS/external/runtime domain 절감량의 합산

근거는 `Iris/_docs/refactor/repository_evidence_lightweighting/`과 `closeout/`의 machine-readable evidence 및 2026-08-10 owner manual-validation attestation이다. 전체 scoped 상태는 `complete`다.

---

# 13. Historical Trace

Historical trace / provenance index는 ROADMAP 본문에서 더 이상 관리하지 않는다.  
과거 Addendum과 closeout 근거는 `DECISIONS.md` 및 각 round plan/review/closeout 산출물을 따른다.

---

# 14. Iris codebase optimization

## Done

- configured pytest source classification과 exact current authority를 분리하고, mixed source 및 승인 exclusion/clean-checkout optional source를 fail-closed 정책으로 고정했다.
- lazy lookup의 verified miss와 routing/target fault를 분리하고 package identity validator를 추가했다.
- UseCase generated chunk에서 nil/empty field를 sparse화해 132,486 bytes를 줄이고 direct facade 1,631개 row shape를 보존했다.
- Alt Tooltip inactive temporary table `1000 -> 0`, warm line copy `404 -> 0`을 달성했다.
- Browser search target operation을 `66 -> 24`, Ordering key derivation을 `64 -> 12`로 줄이고 각 fixed-corpus signature parity를 보존했다. Capability mask는 custom·contradictory·same-canonical hybrid field를 안전하게 부정할 authority가 없어 `2200 -> 2200` no-op으로 닫았고, runtime counter는 기본 off로 전환했다.
- Git path 상태 조회를 batch화했다. CAS와 Python helper 공통화는 안전 후보가 없어 mutation 없는 no-op으로 닫았다.
- exact current `219/219`, terminal current `470 passed / 1 N/A skipped / 112 subtests`, Lua 103 files와 focused optimization rows를 통과했다.
- 2026-08-11 repository owner가 실제 Project Zomboid에서 정상 동작을 확인해 수동 functional in-game validation을 완료했다.
- Codex Reviewer가 hybrid compatibility, fail-closed source denominator, cache claim scope, endpoint/dependency classifier, default-off instrumentation과 protected-surface chain 수정을 확인했다. 구현 및 owner-attestation 경계의 최종 verdict는 모두 `APPROVE`, P0/P1/P2/P3 `0`이다.

## Runtime acceptance / Measurement limits

- `PZ-6C-SEARCH-01`, `PZ-6C-BUILD-01`, `PZ-7-TOOLTIP-01`, `PZ-7-LINECOUNT-01` raw timing sample은 비어 있다. 이는 기능 검증이 아니라 선택적 성능 benchmark이며 Search debounce, incremental Browser build, Tooltip static attribution, LineCount attribution의 정량 채택 판단은 deferred다.
- clean disposable checkout의 configured full advisory는 644 pass, 1 N/A skip, 1 historical failure다. Failing node, 34-artifact mismatch identity, sealed 83-path dependency manifest, exact `base..endpoint` modified/mandatory 교집합 0을 classifier receipt에 보존했다. Current/modified/mandatory failure는 없지만 full-suite PASS는 주장하지 않는다.
- standalone operation 감소를 PZ frame time, heap, release/Workshop/multiplayer/long-session 성능으로 해석하지 않는다.

## Optional benchmark follow-up

- 동일 PZ build/machine/save/mod-set에서 네 named receipt를 각각 10회 측정하고 median/p95/max와 raw sample을 결속한다.
- 측정할 경우 deferred candidate의 정량 채택 여부만 다시 판정하며, 이미 완료된 functional in-game validation을 소급해 미완료로 취급하지 않는다.

## Hold

- PZ sample 없는 debounce/incremental build/static attribution 채택
- 외부 consumer proof 없는 public facade/global 제거
- safe lifecycle candidate가 없는 CAS mutation 또는 exact-contract group이 없는 Python helper 강제 공통화
- configured full-suite PASS, release-ready, Workshop-ready 또는 정량 PZ 성능 개선 선언

근거는 `Iris/_docs/refactor/codebase_optimization/closeout_receipt.json`, 같은 디렉터리의 baseline/change receipts, 2026-08-11 repository owner attestation과 `fe4bb9f6 -> b33ed2ac -> 89f7499c -> 91259769` closeout/review chain이다. 수동 functional in-game validation은 `complete`, governing plan에 따른 통합 closeout 상태는 `partial`이다.

---

# 15. Iris codebase optimization comprehensive follow-up

## Implemented

- Browser item-index 이후 classification, primary location/tag, locale search source를 generation-local row 한 pass로 materialize하고 item identity와 public copy 계약을 보존했다.
- 검색 owner를 `(generation, normalizedLocale)`로 만들고 candidate 완성 뒤 row map/sorted snapshot을 교체하며 prefix와 locale display-name variant cache를 함께 무효화한다.
- ViewModel method lists와 single-method lists를 module constant로 이동하고 capability hint를 item당 한 번 계산한다.
- dynamic DEBUG message를 caller-side guard 뒤로 옮기고 Alt display cache를 fullType당 한 locale/revision entry로 제한했다.
- UseCase ChunkIndex/LineCountIndex의 top-level require/scan을 제거하고 first-demand independent validation/cross-check snapshot을 추가했다.
- `IrisObjectAccess.call0/call1` Lua eligibility를 추가하되 generic production routing은 실제 PZ Kahlua engine-object binding evidence가 없어 변경하지 않았다. Iris는 계속 JVM/JAR/Mixin/직접 Java bridge가 없는 100% Lua 모드다.

## Dispositions / Hold

- session-dependent cache candidate 0: production reset wiring diff 0, `complete/no-op`.
- legacy compact candidate: source `75,143 -> 40,470` bytes 후보는 측정됐지만 요구된 checkout 밖 promotion transaction을 실행하지 않아 `deferred_by_design`.
- Tooltip static projection과 PZ timing-dependent branches: raw PZ receipt 부재로 deferred.
- item 비보존, Alt LRU/active derived key, generated compact adapter, Recipe Set, Python I/O reuse, lifecycle/CAS: materiality 또는 safety candidate가 없어 no-op.
- ObjectAccess generic fast-path routing: `unvalidated_but_in_scope`; overall closeout ceiling은 `partial`.

## Token/context measurement

- Base `5b19a5fa58cb883f6b27f433371434a85b41ba0d` 대비 EOL-normalized 변경 production Lua 15개는 `108,545 -> 126,012` bytes(`+16.09%`), lexical units `14,492 -> 16,408`(`+13.22%`)다.
- Input plan을 제외한 구현 표면 45개는 `673,495 -> 773,605` bytes(`+14.86%`), lexical units `128,456 -> 141,164`(`+9.89%`)다. 동일 context 예산 수용량 proxy는 production에서 약 `11.68~13.86%`, 전체 구현 표면에서 약 `9.00~12.94%` 감소했다.
- 이번 작업의 token 효율 증가율은 `0%`이며 source proxy상 약 `9~14%` 악화다. 성과는 Browser/UseCase/Tooltip runtime operation·allocation 경량화이고 repository text 경량화가 아니다.
- Legacy compact `75,143 -> 40,470` bytes 후보는 미채택이므로 current token 성과에 포함하지 않는다. 실제 tokenizer와 Codex prompt/cache telemetry가 없어 exact GPT/Codex token 비용은 claim하지 않는다.

## Validation boundary

- 자동 검증은 focused `64 passed + 13 subtests`, exact current `219 passed`, configured current `486 passed / 1 N/A skipped / 504 deselected / 112 subtests`, Lua syntax `103 files`를 모두 exit `0`으로 완료했다. Codex Reviewer 최종 verdict는 `APPROVE`, P0/P1/P2/P3 `0`이며 `Iris/_docs/refactor/codebase_optimization_followup/{validation_matrix.json,closeout_receipt.json}`에 기록했다.
- configured full advisory는 repository-only execution boundary가 요구된 clean disposable checkout을 제공하지 않으므로 current authority PASS로 대체하지 않는다.
- PZ latency, heap, FPS/frame-time 및 release/Workshop/multiplayer/long-session 개선은 claim하지 않는다.

---

# 16. Iris test workflow consolidation and execution lightweighting

## Done

- Artifact inventory Git seed, registry COMMON compile, registry Round 3 runner compile, artifact promotion Git seed의 네 독립 cost group을 immutable-prefix sharing 구조로 통합했다.
- 40개 unique consumer node의 55개 concrete node/subcase identity와 failure attribution을 `55 -> 55`로 보존했다. Mutation, rollback/recovery, concurrency와 fresh-process contract는 case-local clone/namespace/process에 남겼다.
- consolidatable producer invocation은 `73 -> 6`(`91.78%`), clone/configuration 등 공개된 부대 호출을 포함한 heterogeneous total은 `187 -> 126`(`32.62%`)으로 줄었다.
- 추적 workflow source의 full-gate taxonomy를 정합화했다. 미분류 source는 `10 -> 0`, multiple classification과 absent policy entry는 각각 `0`이며 10개 source는 exact-path `dedicated_route_validation`을 사용한다.
- 결합 subject의 canonical Run A/B는 각각 `424 passed / 0 failed / 2 deselected / 102 subtests passed`, standalone `4/4 PASS`로 끝났고 deterministic comparator도 통과했다. Required dependency inventory `63 sources / 40 paths`, configured/current node와 denominator, sealed artifact 및 source checkout이 변하지 않았다.
- Codex Reviewer 최종 판정은 `APPROVED`, P0/P1/P2/P3 모두 `0`이다. 구현과 canonical validation, authority closeout 및 기존 consolidation 문서 정합화가 main에 반영됐다.

## Completion boundary

- 상태는 `complete`다. 현재 조사 범위에서 isolation과 failure identity를 보존하면서 비용을 순감소시킬 추가 evidence-qualified candidate는 소진됐다.
- 네 채택 group은 configured denominator 645개 중 40 consumer node(`6.2%`)에 해당한다. 이는 전체 test 의미를 축소하지 않고 반복 setup/compile만 제거한 범위다.
- 이전 `991414ba` preflight failure와 sealed mismatch 관측은 superseded historical evidence로 보존하며 current PASS 근거로 재사용하지 않는다.

## Optional measurement follow-up / Non-claims

- 전체 suite 속도 개선률이 필요하면 같은 machine/environment/command의 comparable before/after full-gate wall time을 별도 campaign에서 측정한다. 이 측정은 완료된 구조 통합의 잔여 구현 gate가 아니다.
- `73 -> 6`과 `187 -> 126`은 invocation-count 구조 지표다. Heterogeneous total을 wall-time, removable cost, PZ runtime 성능 또는 release/Workshop readiness 수치로 해석하지 않는다.

근거는 `Iris/_docs/refactor/test_scenario_execution_consolidation/{candidate_ledger.json,identity_map.jsonl,final_summary.json,closeout.md}`와 clean-checkout authority/evidence successor `0012`/`0013`이다.

## Validation budget

- implementation 전 representative profiling 1회
- 모든 family 변경 완료 뒤 focused batch 1회
- final execution 전 Codex Reviewer 정적 검토
- configured-current 또는 full gate 최종 1회
- target assertion, semantic parity, timeout/process leak 또는 tracked source mutation 같은 Critical failure가 아니면 full long-run restart 금지
- 통계적 성능 certification을 별도로 요청하지 않는 한 68-position Q/Q, candidate, terminal 반복 session과 대형 hash carrier를 도입하지 않음

## Hold

- test order dependency 또는 mutable global scenario result 도입
- fresh-process/bootstrap 계약을 in-process fixture로 대체
- mutation/concurrency branch 사이의 writable state 공유
- case ID, negative contract 또는 failure attribution을 잃는 단일 거대 assertion
- 실질 consolidation code보다 큰 별도 measurement/governance framework 확장

근거는 `Iris/_docs/refactor/test_workflow_consolidation/`, `Iris/validation/baseline_admission/evidence/workflow_consolidation_reapplication_handoff.json`과 2026-08-17 owner validation-cost disposition이다. 현재 pilot transaction은 `complete`; broader consolidation은 이를 미완료로 되돌리는 잔여 gate가 아니라 별도 successor optimization이다.

## Iris Stateful Artifact Registry architecture retirement (2026-08-20)

현재 상태는 `complete`이며 제품 결과는 `FULL_RETIREMENT`다.

- 여섯 compose input과 adopted upstream content input, generator contract에 결속된 deterministic off-live complete-generation builder, stateless descriptor validator와 `generation_key_identity_validation`을 구현했다. Current output readback은 0이다.
- R2 owner decision B를 exact generation subject에 결속했고, immutable generation-qualified Lua set + shared current-generation pointer single-switch installer를 설치했다.
- Package current-runtime identity는 successor pointer와 stateless descriptor만 읽고 legacy descriptor fallback은 제거했다.
- successor tests와 source/dependency policy를 current required route에 추가했다.
- protected current install과 legacy IAR product consumer 제거를 완료했으며 Layer 1–5 active product IAR consumer는 0이다. Sealed history는 그대로 보존한다.
- clean-checkout full repository gate Run A/B와 deterministic comparator는 implementation subject `c924349e`에서 통과했다. 수동 인게임 QA는 owner-attested PASS다.
- Codex Reviewer가 current-runtime package identity 불일치 P1을 발견했다. Root cause는 case-collision key에 대한 Windows PowerShell 5.1/PowerShell 7의 culture-sensitive ordering 차이였고, `6f362b5e`에서 ordinal ordering으로 교정했다. 두 shell의 digest가 일치하며 계획된 current-runtime ZIP package가 exit `0`으로 완료됐다.
- 종료 기록은 `5ce69e2a`에 추가됐고 `a55a2999`에서 main에 병합됐다. 현재 main readpoint는 `c91d8f79`다.
- `stale_requires_successor_rtc`, Publish, release/Workshop/deployment, owner seal과 canonical sealed closure는 제품 retirement와 별도 축으로 남는다.

IAR retirement에 남은 구현 gate는 없다. Inactive predecessor generation cleanup은 rollback 필요성과 reader liveness를 다시 확인한 뒤에만 수행할 수 있는 선택적 post-closeout action이며, 수행하지 않은 현재 상태도 active product dependency가 아니다.

근거는 `Iris/_docs/round3/iar_stateful_architecture_retirement/{closeout.json,residual_report.json,codex_reviewer_final.json}`이다.

---

## Iris item-page information sufficiency assessment (2026-08-21)

Current state: one-off assessment complete.

- current vanilla denominator 2,285개를 평가했다.
- 결과는 `information_sufficient=2081`, `evidence_limited=180`, `known_information_missing=2`, `unresolved=22`다.
- 평가 결과와 gap inventory는 `Iris/build/description/v2/output/item_page_information_sufficiency/`에 보존한다.
- 임시 검증 코드는 작업 완료 후 제거했으며 정규 current route, authority, test suite 또는 Iris architecture에 편입하지 않는다.
- 이 평가로 인한 runtime, public text 또는 package 변경은 없다.

후속 정보 보강은 결과를 참고해 별도 작업으로 결정한다. 이 일회성 평가 자체에는 유지보수할 정규 검사기나 추가 architecture gate가 없다.

---

## Iris Layer 3 body-role realignment (2026-08-21)

Current state: staging closeout and Change 9 current installation complete.

- Layer 3를 confirmed description material이 있을 때만 제공하는 선택적 설명 계층으로 정렬하는 hash-bound policy/mapping/rule contract를 채택했다.
- exact current body denominator에는 5-state disposition, canonical FullType denominator에는 독립 5-state readiness를 생성하는 pure core를 추가했다.
- core description과 acquisition information을 source-bound fact ID로 분리하고, Menu는 `preserve_current_publicity` four-case projection을 사용하며 Tooltip은 input readiness까지만 다룬다.
- one-off IPS snapshot은 exact identity/current drift를 확인한 뒤 per-item Layer 3 axes만 advisory prerequisite로 소비한다. Page disposition과 Layer 4 axes는 disposition/readiness/Problem 5A로 직접 변환하지 않는다.
- attempt-0002 candidate replay A/B, protected-surface non-mutation, acquisition conservation, public-text blocking separation, exact Problem 5A projection과 read-only terminal validator가 exit `0`으로 완료됐다. Exact terminal subject `1197ccc99085666d336e3ed493555e26810104e5`의 replay도 같은 `current_snapshot`과 byte parity를 재현했다. Denominator는 item `2,285`, existing body `2,084`이며 Problem 5A projection은 `2`다.
- Full-repository blocker repair는 current-generation authority anchor의 exact semantic relocation, Markdown inline identifier의 closeout-claim false positive 제거, tracked historical overlay lifecycle recognition 복원, Windows clean-checkout raw-byte 보존과 current taxonomy identity 결속으로 한정했다. Layer 4 dedicated test route의 제품 구현은 변경하지 않았다.
- existing current compose, reusable public-text evaluator, runtime Lua와 package path는 이 staging implementation에서 변경하지 않았다.

Focused test `8 passed`, required manual review `33/33`, exact duplicate group representative review `184/184`를 완료했다. Exact staging terminal subject `1197ccc99085666d336e3ed493555e26810104e5` / tree `da2bf2e5ec595b8de1ea41ee2fafb7e433c058db`의 mandatory full-repository Clean-Checkout Run A/B는 각각 `433 passed, 2 deselected, 117 subtests passed`와 standalone `4/4`로 exit `0`이며 canonical result raw bytes가 일치한다. Deterministic comparator도 exit `0`이고 source checkout mutation은 `0`이다. Post-validation result pointer는 `Iris/_docs/round3/layer3_body_role_realign/evidence_carriers/1197ccc99085666d336e3ed493555e26810104e5/clean_checkout_result_pointer.json`에 분리했으며 validated terminal subject를 재정의하지 않는다. Staging closeout token은 `layer3_role_realign_staging_complete`다.

별도 승인된 Change 9 current installation도 완료했다.

- Accepted staging successor를 raw bytes 그대로 approved upstream candidate로 승격하고 canonical seven-input complete-generation을 생성·검증했다.
- Current pointer는 predecessor `dvf33-2a44a0a8d9a2e7f0d9a533ad002b7f691c1bfccec9577fb3356967ec6fd8a00c`에서 generation `dvf33-aa138aa4896b68ac53609a4b1cb6e5346245e74f544db28eb2ee924dc7b3e814`로 한 번 전환됐다. 동일 generation 재설치는 protected mutation `0`의 no-op이다.
- Current package lookup identity를 `lookup-f088127352730047`로 정렬했다. Windows PowerShell 5.1과 PowerShell 7의 `current_runtime_payload` generation, lookup digest와 output universe가 일치하고 hash mismatch는 `0`이다.
- Current 전환으로 predecessor one-off IPS snapshot을 `predecessor_snapshot_stale_after_install`로 표시했다. Evaluator 재실행이나 predecessor sufficiency claim 상속은 없다.
- Install terminal subject `d006f6108093886751e538d36c92de3627a9e76f` / tree `5e2370f8e5720e830b8ef62c87b6c51c45bfaa4a`의 focused validation은 `23 passed, 14 subtests passed`, Lua syntax는 `157 files`로 PASS했다.
- Install terminal subject `d006f610`은 Layer 4 main merge `e7508c0c`와 Layer 2–3 EN locale projection `de146b73`을 모두 조상으로 포함하는 단일 통합 제품 readpoint다. Layer 3 current generation, Layer 4 adaptive presentation과 KO/EN projection은 동일한 실제 tree에 함께 존재하므로 별도 합성 merge는 필요하지 않다.
- Fresh Clean-Checkout Run A/B는 각각 `433 passed, 2 deselected, 117 subtests passed`, standalone `4/4 PASS`, external mutation `0`, cleanup PASS다. Comparator는 required execution unit `437`, test identity `433`, canonical raw-byte equality와 result SHA-256 `f110c14471bd5e8f3cd0d76afeaa8533ea6bb6deaf147b17764e192f377c37b6`을 확인했다.
- Full-gate source census가 드러낸 Layer 4 adaptive-presentation/runtime-projection test source 누락은 기존 interaction-presentation test와 같은 dedicated focused route로 분류했다. Adoption bindings만 current contract bytes로 갱신했으며 canonical denominator는 변경하지 않았다.
- Current-install closeout token은 `layer3_role_realign_current_install_complete`다.

Staging과 current installation에 남은 구현 gate는 없다. Tooltip UI, Problem 5A enrichment, RTC, Publish와 release/Workshop/deployment readiness는 별도 successor 범위다.

---

## Iris Layer 4 adaptive presentation and KO/EN detail localization (2026-08-21)

Current state: implementation and owner in-game acceptance complete on `main`.

- Layer 4 adaptive interaction presentation을 main에 통합했다. 단일·소규모·고밀도 row, compact/full 전환, 검색, Recipe 제작 UI 이동과 item/locale별 UI state ownership이 current runtime에 적용됐다.
- Recipe와 Right-click은 독립 surface로 유지되며 QG-only 수용 대상 Ball Peen Hammer, Garden Saw, Stone Hammer가 모두 표시된다. Stone Hammer의 우클릭 행동도 owner가 최종 확인했다.
- EN 전환 시 Layer 2–3 글자가 깨지던 문제를 교정했다. Layer 2는 KO와 ID parity를 갖는 EN template 50개를, Layer 3는 exact current facts에 결속된 EN payload 2,084개를 lazy chunk lookup으로 제공한다.
- 지원 locale에서 알려진 정보를 숨기는 방식은 채택하지 않는다. Runtime은 같은 semantic source의 locale payload를 선택하며 KO raw text를 EN 화면에 노출하는 fallback도 사용하지 않는다.
- Owner in-game 확인 결과는 부팅, Iris Browser, 223 Bullets Mold, Tongs compact/full/search, Recipe 제작 UI 이동, item 전환 상태, 세 QG-only 항목, 기존 context menu/Wiki/Alt Tooltip 동작과 화면 layout이 정상이다. 기존 surface의 fallback 분기 자체는 관찰 가능하지 않아 별도 PASS로 주장하지 않는다.
- 구현 중 focused test는 `9 passed, 5 deselected`, Lua syntax validation은 `145 files`에서 exit `0`이었다. 이 결과와 localization builder를 새로운 validation authority로 확장하지 않는다.
- Layer 4 통합 readpoint는 `e7508c0c`, current KO/EN detail localization readpoint는 `de146b73`다.

이 범위에 남은 구현 또는 인게임 수용 gate는 없다. Push, RTC, Publish, release/Workshop/deployment는 이번 완료 상태의 일부가 아니며 필요할 때 별도 successor로 다룬다.

---

## Iris regular validation authority census and temporary/legacy physical cleanup (2026-08-23)

Current state: authority census and validation baseline recovery complete; physical cleanup remains in progress.

### Done

- 1,167개 executable validation identity의 inventory, contract role과 disposition을 기록하고 current/non-current authority를 분리했다.
- Current regular composition을 pytest `433` + standalone `4`로 재확정했다.
- DVF closeout/reentry guard가 명시적 successor-scope 문장을 current-completion overclaim으로 오인하던 validation-system defect를 교정했다.
- Exact subject `18d0c2ff9de97a71ddf7aa6b03fb059ffbb35089` / tree `56250ea400511eaf84ff84ee19ee8550f89b8492`에서 Run A/B, standalone `4/4`, deterministic comparator가 PASS했고 Codex Reviewer의 P0/P1/P2/P3는 모두 `0`이다.
- Current contract가 없던 `test_tc8_full_pipeline_snapshot` 1개를 제거했다.
- Post-validation carrier `6a4cf63c001ec708929e57da64347e3e7a040d91`은 census와 baseline-recovery PASS를 기록한다. 이 carrier는 temporary-test cleanup 전체 완료 authority가 아니다.

### Remaining physical cleanup

- Regular contract가 하나도 없는 live source `37`개, executable identity `216`개, raw source `329,344 bytes`를 retention obligation 기준으로 재심사한다.
- `reproduction_only` `24 files / 153 identities / 268,519 bytes`는 현재도 필요한 exact reproduction obligation이 있는 경우에만 executable source로 유지한다.
- `evidence_only` `13 files / 63 identities / 60,825 bytes`는 compact sealed evidence 또는 repository-external durable evidence + hash-bound pointer를 기본 disposition으로 삼는다.
- Ledger상 mixed source 3개를 검토한다. 이미 TC8이 제거된 Right-click source를 제외한 두 live mixed source는 current/non-current callable을 분리하고 non-current 부분을 다시 disposition한다.
- 기존 1,167행 inventory를 재작성하지 않는다. 현재 대형 ledger는 successor 작업 입력으로 재사용하고, compact in-repo summary와 durable external hash-bound ledger로 전환해 중복 repository payload를 줄인다.

### Exit criteria

- 실제 removed source, executable identity와 raw bytes가 모두 양수다.
- Repository-wide tracked byte와 test/tooling LOC가 baseline보다 순감소한다.
- Current pytest `433`, standalone `4`, required manifest, taxonomy/source-policy binding과 failure localization이 보존된다.
- Exact terminal subject의 clean-checkout Run A/B와 deterministic comparator가 모두 exit `0`이고 source mutation은 `0`이다.
- 보존된 non-current executable source마다 taxonomy 순환 인용이 아닌 현재도 유효한 명시적 reproduction obligation과 consumer가 있다.
- 위 조건 전에는 temporary/legacy cleanup Problem 1을 `complete`로 닫지 않는다.

### Non-claims / Hold

- Current test count가 유지된다는 사실은 physical cleanup 실패 사유가 아니다. 제거 대상은 원래 current gate 밖에 있을 수 있다.
- Census/role-reclassification PASS를 repository lightweighting, wall-time 개선 또는 physical cleanup 완료로 표현하지 않는다.
- Historical evidence bytes를 무근거로 삭제하거나 current contract, fail-closed branch, standalone boundary를 감축하지 않는다.
- Comparable before/after timing이 없으므로 suite 속도 개선률은 claim하지 않는다.

근거는 `Iris/_docs/round3/validation_contract_reconfirmation/`의 기존 1,167행 census와 validated subject/carrier record다. 이 산출물은 앞으로 temporary-test cleanup 완료본이 아니라 physical cleanup을 위한 authority census 및 validation baseline으로 사용한다.

### Physical retirement successor (2026-08-23)

Current state: predecessor implementation and exact-subject validation PASS; survivor correction implemented, correction terminal validation and S0→new-S1 full-range P8 review pending; P10 withheld.

- Regular 599 identity의 blanket keep을 폐기하고 independent survival basis로 전량 심사했다. Current product 234와 validation-system 94를 보존하고 lifecycle-bound 271을 퇴역시켰다.
- Non-current 568 identity는 actual current consumer가 있는 39를 승격·보존하고 529를 퇴역시켰다. Full-gate 56 conflict는 current 39/retired 17로 닫혔다.
- Tracked tree에서 full source/exclusive support 92개와 mixed callable 2개를 제거했다. Dirty main에서는 archive verify와 fresh-root restore가 끝난 ignored/untracked 163 file/335 identity/901,270 bytes만 제거하고 product survivor 6 family/13 identity를 보존했다.
- `historical`, `diagnostic`, `all` repository-local replay selector는 종료됐고 `current` selector와 fail-closed current contract는 남는다. Predecessor ledger, sealed receipt와 Git history는 보존한다.
- Exact terminal subject `b0fe69b1` / tree `2e7f2c8e`에서 focused/current/collection 검증, Clean-Checkout Run A/B, comparator와 undeclared-source negative probe가 PASS했다. Canonical result SHA-256은 `1baca45c...07964`, pytest identity는 `230`, standalone은 `4`, required execution unit은 `234`, source/external mutation은 `0`이다.
- Exact `b0fe69b1` closeout-carrier commit review는 exit `0`, actionable finding `0`이었다. 이 결과는 부모 `4e527b84`의 destructive diff 전체를 formal subject로 삼지 않았으므로 P8 full-range PASS가 아니다.
- Exact gate는 `437` unit에서 `234` unit으로 `203` (`46.453%`), current taxonomy는 `228` identity에서 `118` identity로 `110` (`48.246%`) 감소했다. Tracked executable identity `447`과 full source/exclusive support file `92`를 제거했고 net tracked blob `8,228,685` bytes (`1.026%`), test/tooling LOC `24,074` (`9.278%`)를 줄였다.
- Correction pass에서 predecessor survivor `328` identity를 재심사해 lifecycle-only regular `12`와 predecessor inventory 밖 callable `1`을 추가 제거했다. Regular survivor는 product `224` + validation-system `92` = `316`, current taxonomy는 terminal execution 전 `110`이다.
- 남은 필수 작업은 correction terminal validation, S0→new-S1 full-range Codex Reviewer, 그리고 그 결과를 반영한 canonical closeout이다. Dirty-main archive/restore locator 부재가 해소되지 않으면 해당 domain과 P10은 blocked로 유지한다.
- 실제 GPT/Codex token 효율은 미측정이다. Repository bytes, test/tooling LOC와 gate/taxonomy 감소는 workload별 context proxy일 뿐이며 tokenizer, prompt selection, cache hit와 input/output/tool token telemetry가 없는 상태에서 token 절감률로 대체하지 않는다.
- Runtime Lua, product data/public text/package, in-game QA, RTC/Publish, release/Workshop/deployment/B42와 performance claim은 이 successor 범위가 아니다.

집계와 terminal state는 `Iris/_docs/round3/temporary_validation_physical_retirement/{retirement_summary.json,closeout.json}`에 둔다. Ad hoc cleanup 검사는 canonical validator나 새 validation authority가 아니다.
