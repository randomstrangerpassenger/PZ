# ROADMAP.md

> 상태: canonical summary + deduplicated consolidated addendum ledger through 2026-06-21
> 기준일: 2026-06-21
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
오프라인에서 봉인한 evidence / outcome / source fact를 런타임에서 해석·추천·비교 없이 안정적으로 표시한다.

## Done

* Iris의 정보 표시 위계를 **기본 정보 → 의미(주 소분류) → 활용(레시피/상호작용) → 메타**로 고정했다.

  * 분류 데이터는 기본 UI 전면이 아니라 메타 영역에 격리한다.
  * `primary_subcategory`는 정렬 기준이 아니라 브라우징 anchor로 사용한다.
  * 주 소분류 설명 문장은 자동 기본값이 아니라 후보 템플릿으로 취급한다.

* Iris의 최상위 기준을 `Philosophy.md`로 재고정했다.

  * 핸드오버 / 세션 요약 / 과거 작업 문서는 current authority가 아니라 작업 참고물로만 읽는다.

* Evidence / Source / Description 책임 분리를 봉인했다.

  * Evidence 모델은 행동 모델이 아니라 **결과 상태 모델**로 유지한다.
  * Recipe / Right-click / Static capability는 서로 다른 Source로 유지한다.
  * 런타임은 의미를 추론하지 않고, 오프라인에서 봉인한 fact / outcome / source를 소비한다.
  * 설명 왜곡 문제는 설명 엔진이 아니라 태그 생성 단계와 tuple integrity 문제로 재판정했다.

* Context Outcome을 **문서 1:1 기계화용 오프라인 사실 테이블 생성기**로 고정했다.

  * Iris 엔진과의 관계는 외부 공급자 / 내부 소비자로 분리한다.
  * 런타임 분석, 자동 의미 추론, smoke/debug artifact의 authority 승격은 허용하지 않는다.

* Right-click 계열 정보는 **item-dependence + state-change proof** 기준으로 재정리했다.

  * current canonical 기준은 메뉴 존재가 아니라 `executing_tool + external_target + persistent_change`다.
  * PASS / NO / REVIEW가 primary decision이고, STRONG / WEAK는 PASS 이후 uniqueness overlay로만 읽는다.
  * 메뉴명 / UI 구조 / 비활성 표시 여부는 보조 관찰 정보로 강등한다.

* 의미 기반 capability 확장을 중단하고, 상태 변화 유형 중심으로 재정리했다.

  * `can_scrap_moveables` 같은 넓은 의미 필드는 단일 결과 상태 단위로 해체 / 재정의해야 한다.
  * `can_stitch`, `can_repair`, `can_attach_weapon_mod`, Equip / Use / Passive 정보는 기본 evidence 축으로 확장하지 않는다.

* Recipe / 목록 UI 정책과 개별 아이템 정보 작업 순서를 고정했다.

  * Recipe 기반 evidence 시스템은 현 단계에서 안정적인 축으로 유지한다.
  * 연관 레시피 표시 기본 단위는 행동 문장 묶음이 아니라 레시피명 단위 접기 / 펼치기다.
  * 전역 기능 동등성 그룹화는 중단하고, UI 목록 단계의 DisplayName 중심 접기로 제한한다.
  * 개별 아이템 정보 작업은 `분류 / 증거 체계 고정 → Outcome source 검증 → 결과 상태 fact 고정 → 필요 시 설명 문장화` 순서로 진행한다.

* DVF 3-3 runtime authority를 current 기준으로 재봉인했다.

  * current runtime vocabulary는 `adopted / unadopted`로 유지한다.
  * legacy `active / silent`는 current runtime vocabulary가 아니라 historical / diagnostic / import alias로만 읽는다.
  * runtime deployable authority는 monolith가 아니라 Lua chunk manifest + chunk files 기준으로 유지한다.

* DVF 3-3 current authority reconciliation, vNext regeneration, rejected delta correction, current authority cutover, 2105 consumer migration을 완료했다.

  * successor source / rendered / runtime chunk authority를 current로 승격했다.
  * frozen 2105, prior staging, 6-entry fixture, legacy bridge, monolith output은 current authority가 아니라 historical / comparison / diagnostic / prerequisite trace로만 보존한다.
  * 이 완료는 package release readiness, Workshop readiness, B42 readiness, deployment readiness, manual in-game validation, semantic quality completion, public-facing text quality acceptance를 의미하지 않는다.

* DVF 3-3 Live Migration Readiness Authorization을 봉인했다.

  * `phase4_live_apply_allowed=true`, `downstream_predecessor_status=ready_for_phase4_live_apply`다.
  * authorization row split은 `153 = 109 live_mutation_eligible + 44 evidence_only + 0 blocked`다.
  * hard-forbidden runtime / package / Lua bridge surface는 live mutation target이 아니라 evidence-only proof로 닫았다.
  * dirty target overlap은 committed baseline + isolated non-overlap proof 기준으로 row blocker에서 제거했다.
  * 이 완료는 실제 Phase 4 live mutation 실행, live migration completion, release/package/Workshop readiness가 아니다.

* DVF 3-3 Live Migration Readiness Execution evidence root를 구현했다.

  * `docs/dvf_3_3_live_migration_readiness_execution_plan.md`가 요구한 `phase0`~`phase10` pre-apply gate artifacts를 `Iris/build/description/v2/staging/dvf_3_3_live_migration_readiness_execution/`에 materialize한다.
  * execution runner는 authorization verdict를 live apply로 실행하지 않고, execution plan이 소비할 canonical evidence root / artifact names / validation surface로 투영한다.
  * execution verdict도 `phase4_live_apply_allowed=true`, `downstream_predecessor_status=ready_for_phase4_live_apply`, `no_live_mutation_changed_count=0`이다.
  * execution validation은 `run_dvf_3_3_live_migration_readiness_execution.py --mode all`, `validate_dvf_3_3_live_migration_readiness_execution.py --require-complete`, focused unittest 기준 PASS다.

* compose / resolver / compatibility authority를 current readpoint 기준으로 정리했다.

  * default compose authority는 `compose_profiles_v2.json + body_plan`으로 유지한다.
  * `selected_role`은 legacy fallback 제거 대상이 아니라 native resolver authority / trace로 채택했다.
  * legacy compatibility mapping은 default authority가 아니라 diagnostic-only non-authority fixture로 격리했다.

* Lua bridge export와 build / test contract를 current route 기준으로 재정렬했다.

  * Lua bridge exporter의 default route는 monolith가 아니라 chunk manifest + chunk files를 생성한다.
  * monolith export는 explicit historical / diagnostic mode에서만 허용한다.
  * current / historical / diagnostic test route를 분리하고, current route closure guard를 유지한다.

* Silent 21 / runtime enum / legacy label 계열 부채를 current readpoint 기준으로 정리했다.

  * runtime payload enum은 `adopted / unadopted`가 canonical이다.
  * `active / silent` 재유입은 current writer / validator path에서 fail-loud 처리한다.
  * missing original sealed artifacts는 provenance gap으로 봉인하고, original authority 복원으로 표현하지 않는다.

* Iris refactor v2.0 / Final Roadmap v1.4 / 최종 리팩토링 v4.1 계열 구현을 current code 기준으로 완료했다.

  * protected-call boundary를 `IrisProtectedCall`로 중앙화했다.
  * UseCaseDescriptions를 facade + Lua chunk 구조로 외부화했다.
  * `IrisDesc` 구현을 새 경로로 이동하고 compatibility wrapper를 유지했다.
  * Browser requirement display policy, MapIcon 설정화, build entrypoint surface 정리를 완료했다.
  * item selection runtime regression은 BOM 제거와 generator load guard로 수정했다.

* Manual In-Game Validation QA를 revised contract 기준으로 닫았다.

  * Iris Browser는 all-item Browser이며, item-entry visibility와 Layer 3 body/source quality는 분리한다.
  * raw token / raw nil / table address / broken placeholder 노출이 없음을 기준으로 practical in-game validation을 통과한 상태로 읽는다.
  * release readiness / Workshop readiness / tooltip completion은 이 closeout만으로 선언하지 않는다.

* Semantic UI Exposure / `quality_exposed` 문제를 no-exposure disposition으로 닫았다.

  * `quality_state`는 offline / internal authoritative signal로만 유지한다.
  * `quality_exposed`는 reserved inactive로 둔다.
  * Browser / Wiki / Tooltip은 quality 판정을 badge, copy, sorting, filtering, hiding, recommendation, trust / confidence 표시로 소비하지 않는다.

* Structural signal / Layer4 / Acquisition Lexical 계열을 current 기능 미완이 아니라 readpoint / follow-up disposition 문제로 정리했다.

  * structural signal은 publish / quality / runtime / Lua bridge / default compose / source-row writer input이 아니다.
  * Layer4 readpoint는 resolved state, production target, publish target으로 승격하지 않는다.
  * Acquisition Lexical suppress 계열은 별도 approved plan 없이는 removal / contract expansion / runtime-side repair로 열지 않는다.

* future reopen governance를 **subset-bounded single-authority rule**로 고정했다.

  * closed readpoint를 재개방하려면 새 입력 authority, 명시적 successor / correction scope, 또는 별도 approved plan이 필요하다.
  * 개별 closeout 근거만으로 release readiness / Workshop readiness / B42 readiness를 선언하지 않는다.

## Doing

* Iris는 vanilla-first MVP를 **DVF + Tooltip / Browser 본체 검증** 중심으로 유지한다.

* 런타임은 오프라인 authority에서 생성된 Lua facade / chunk를 소비하는 표시 계층으로 유지한다.

  * public require contract는 유지한다.
  * runtime JSON parser는 도입하지 않는다.
  * Layer 3 runtime data는 chunk manifest + chunk files를 deployable authority로 유지한다.
  * monolith / chunks 동시 배포는 금지한다.
  * Lua bridge exporter의 default contract와 bridge report도 chunk authority 기준으로 유지한다.

* 설명 계층은 해석 / 권장 / 비교 / 재작성을 하지 않는다.

  * Evidence / Source / Description layer의 책임 분리를 유지한다.
  * 증거 시스템과 설명층은 독립적으로 운용한다.
  * Browser item-entry visibility와 Layer 3 body/source quality는 분리해서 읽는다.

* Semantic UI Exposure는 no-exposure disposition으로 유지한다.

  * `quality_state`는 internal / offline 운영 신호다.
  * `quality_exposed`는 reserved inactive다.
  * Browser / Wiki / Tooltip은 quality 판정을 표시, 정렬, 필터, 숨김, 추천, 신뢰도 표시로 소비하지 않는다.

* compose default authority는 **`compose_profiles_v2.json + body_plan`** 으로 유지한다.

  * legacy sentence_plan path는 historical / offline tooling fixture로만 남긴다.
  * exposed legacy adapter entrypoint modes는 removed state로 읽는다.
  * `body-plan v2`는 이 구현 표면의 alias label로만 읽고, 별도 second authority로 승격하지 않는다.

* current authority와 repository representation 경계를 분리해서 유지한다.

  * current source / rendered / runtime chunk chain만 current authority로 읽는다.
  * fixture / staging / generated / diagnostic output은 current authority가 아니다.
  * tracked status는 current authority 승격이 아니다.
  * ignored status는 삭제 가능성이나 비중요성의 증거가 아니다.
  * current-route tooling allowlist는 current core 우회면이나 core surface 확장이 아니다.

* legacy bridge / monolith / stale artifact 계열은 current runtime / package / compose path로 복귀시키지 않는다.

  * stale bridge와 legacy 6-entry payload는 current fallback이나 package authority로 사용하지 않는다.
  * monolith export는 explicit historical / diagnostic mode에서만 허용한다.
  * package route는 legacy bridge / monolith / current-looking stale artifact 재유입을 fail-loud로 막는다.

* Iris refactor 이후 runtime / build contract를 현재 shape로 유지한다.

  * protected-call policy는 `IrisProtectedCall`을 통해서만 조정한다.
  * logger / safeRequire / module bootstrap 공통화는 `IrisModuleBootstrap.lua`를 통해서만 다룬다.

* closed readpoint는 현재 작업 대상으로 재개방하지 않는다.

  * Resolver / Silent 21 / runtime enum / legacy active-silent guard는 닫힌 current readpoint로 유지한다.
  * Structural Signal / ACQ_DOMINANT / Layer4 / Acquisition Lexical은 user-facing 기능 후보나 publish 후보로 승격하지 않는다.
  * 각 readpoint의 count, hash, branch, validation 세부값은 ROADMAP 본문이 아니라 산출물 / DECISIONS에서 추적한다.

* future reopen round는 닫힌 readpoint를 되돌리는 방식이 아니라, 새 입력 authority나 명시적 successor / correction scope가 있을 때만 별도 scope로 연다.

* 외부 모드 확장은 **structure-only / normalization-first** 원칙으로만 검토한다.

  * Iris를 AI 위키, 의미 추론기, 추천 엔진, 품질 판단 UI로 확장하지 않는다.

## Next

* Iris refactoring v4.1 완료본을 packaging / release-note / commit 단계로 넘길지 별도 scope로 결정한다.

  * package 검증 기준은 `Iris/tools/package_iris.ps1 -Clean -Zip`로 둔다.
  * dirty working tree에서는 의도한 Iris refactor 파일만 stage한다.

* release 전 추가 검증이 필요하면 targeted smoke가 아니라 **release checklist / full manual QA** 범위로 연다.

  * item selection error accumulation regression은 fixed 상태로 읽고, 재검증은 release-readiness 범위에서만 다룬다.
  * practical in-game validation closeout만으로 release readiness / Workshop readiness / tooltip completion을 선언하지 않는다.

* Walkthrough / 구현 체크리스트 / 검증 절차 문서 간 최신 상태 일치를 유지한다.

* Runtime Payload State Integrity Residual Seal을 별도 round로 연다.

  * 현재 current-like runtime collision은 guard와 payload shape로 닫혔으며, 남은 문제는 implementation blocker가 아니라 residual seal이다.
  * 완료 조건은 author decision으로 current-like `unadopted + text_ko` / `unadopted + exposed` 금지를 확정하고, rollback / predecessor residue가 historical-only residue로 남는다는 경계를 independent review 또는 명시 external gate로 닫는 것이다.
  * 이 residual seal은 새 runtime data mutation, enum 재정의, UI 노출, renderer policy 변경을 자동 승인하지 않는다.

* Consumer Universe Denominator Lock의 current-route denominator guard는 live required-validation manifest에 채택된 상태로 읽는다.

  * live manifest는 denominator final report를 required artifact로, denominator focused unittest를 required test로 요구한다.
  * denominator gate status는 `adopted_required_gate`이고 future closeout에서 denominator misuse를 fail-closed로 막는 guard다.
  * Terminal Disposition Adjudication은 terminal content와 hash seal이 닫힌 상태로 읽는다.
  * 이 adoption은 consumer migration execution, current authority cutover, runtime/source/rendered/package mutation, release/package/Workshop/B42 readiness를 자동으로 열지 않는다.
  * broad current-route runner의 이전 `CURRENT_FACTS=6` vs `2105` 및 `Base.CanOpener` overlay blocker는 Current-Route Baseline / Source-Overlay Repair에서 별도로 닫혔다. Denominator adoption PASS는 여전히 terminal/shared/current-route repair completion을 대체하지 않는다.

* Shared Disposition Ledger Consumption은 live required-validation manifest에 채택된 상태로 읽는다.

  * live manifest는 shared final report, divergence report, raw authority read report, value divergence report, predecessor reentry report, no-dual-authority-read report, protected-surface no-mutation report를 required artifact로 요구한다.
  * live manifest는 focused shared disposition unittest를 required test로 요구한다.
  * final shared report는 `complete_adopted`, `adopted_required_gate`, `RAW_AUTHORITY_READ=0`, `VALUE_DIVERGENCE=0`, `PREDECESSOR_REENTRY=0`, `DUAL_AUTHORITY_READ=0`, protected mutation `changed_count=0`으로 닫힌 상태다.
  * candidate manifest는 `superseded_by_live_required_gate`로 보관하며 execution authority가 아니다.
  * 이 adoption은 live migration execution, current authority cutover, runtime/source/rendered/package mutation, release/package/Workshop/B42 readiness, #7 Closeout / Reentry Guard Seal을 자동으로 열지 않는다.

* Current-Route Baseline / Source-Overlay Repair는 Problem 7 repair round로 닫힌 상태로 읽는다.

  * full current-route validation은 `uv run python -B Iris\_docs\round3\round3_run_contract_tests.py --class current --enforce-current-build-closure` 기준 `PASS / 103 tests`다.
  * repair runner는 `status=PASS`이며 final repair report는 `closeout_state=partial`, `implementation_plan_ready=true`, `stable_plan_provenance=true`다.
  * `docs/dvf_3_3_current_route_baseline_source_overlay_repair_problem7_plan.md`는 canonical `primary_problem7_plan`이고, 기존 `docs/dvf_3_3_current_route_baseline_source_overlay_repair_plan.md`는 execution authority 없는 `predecessor_contract_plan`이다.
  * `CURRENT_FACTS=6`은 full current-route universe expectation으로 쓰지 않는다. vNext `2105` row universe는 source / overlay / rendered / runtime evidence contract로 소비하지만 old predecessor authority 복구나 current debt로 재진입하지 않는다.
  * runtime-adopted current-route compose 대상 row의 `body_source_overlay` requirement, compose / current-authority / Layer4 trace shared contract, normalization stale anchor, cutover diff-to-ledger bijection은 focused tests와 full current-route validation으로 닫혔다.
  * 이 repair는 Terminal Disposition, Denominator Lock, Shared Disposition Consumption의 재개나 재채택이 아니다.

* Closeout / Reentry Guard Seal은 governance required gate로 채택된 상태로 읽는다.

  * broad consumer migration completion과 cutover subset completion의 문구를 분리한다.
  * predecessor `2105 / 2084 / 21`이 current hard gate, runtime authority, current debt로 재진입하지 못하도록 guard를 봉인한다.
  * Problem 7 full current-route PASS를 Problem 8 closeout completion으로 읽지 않는다.
  * final guard report는 `machine_contract_status=PASS`, `required_validation_gate_adoption_status=adopted_required_gate`, protected source / rendered / Lua bridge / runtime / package mutation `0`으로 닫힌다.
  * canonical seal은 non-Claude independent review PASS에 따라 `canonical_complete`로 닫힌다.
  * 이 gate는 live migration execution, live mutation, current authority cutover, release/package/Workshop/B42 readiness, manual QA, semantic quality completion, public-facing text acceptance를 열지 않는다.

* Phase 4 Live Migration Execution을 열 경우 sealed readiness authorization / execution evidence를 입력으로 삼는다.

  * 입력은 `109` live mutation eligible row와 sealed dry-run patch bundle로 제한한다.
  * `44` evidence-only row는 live writer 대상이 아니며, live execution ledger에서는 origin proof / evidence-only disposition으로만 소비한다.
  * 실행 직전에는 execution evidence root의 `phase10/downstream_predecessor_status.json`, sealed dry-run patch bundle, baseline hash, dirty non-overlap, hard-forbidden surface, writer capability, dry-run/live input identity를 다시 fail-closed로 검증한다.
  * readiness authorization의 sandbox/readiness mutation과 no-write probe는 live completion evidence가 아니다.
  * readiness execution phase artifacts도 pre-apply evidence이며 live completion evidence가 아니다.

* 이후 Iris 후속 작업은 rollback, correction, package/release readiness, manual QA, public text quality acceptance 중 하나로 명시해서 연다.

  * 닫힌 vNext current authority implementation / 2105 consumer migration을 다시 여는 방식으로 후속 작업을 정의하지 않는다.
  * historical-reference / diagnostic-only / false-positive / no-op row는 별도 승인 없이 변경 대상으로 승격하지 않는다.

### Conditional Reopen

* Acquisition Lexical follow-up은 live suppress validator surface의 disposition을 별도 approved plan으로 열 때만 진행한다.

  * 이 follow-up은 suppress retirement / removal, contract expansion, phrasebook, array acquisition, runtime-side repair 권한을 자동 상속하지 않는다.

* Layer4 후속 작업은 별도 approved plan이 있을 때만 연다.

  * publish mutation, semantic quality interpretation, public-facing exposure, production wiring, Layer4 policy redesign은 자동 후속 단계가 아니다.

* ProtectedCall boundary policy를 다시 열 경우, `engine / ui / data / compat` 라벨별 복구 / 로그 / fallback 정책표를 먼저 봉인한다.

* build script manifest화를 다시 열 경우, current / historical / diagnostic route와 non-destructive disposition boundary를 먼저 유지한다.

* Static Report Label Cleanup Referent Recovery를 다시 열 경우, original generated report / operator artifact path, staged artifact, VCS trace, regeneration recipe 중 하나를 새 입력으로 제공해야 한다.

  * 새 referent input 없이 `active / silent` 문자열만으로 cleanup mutation을 열지 않는다.

* closed readpoint를 재개방해야 할 경우, current authority를 깨지 않는 별도 scope lock으로만 연다.

  * 허용 후보는 isolated inventory reduction, subset-bounded source expansion, optional quality leak guard hardening처럼 범위가 닫힌 correction / guard hardening으로 제한한다.

## Hold

* release / 배포 readiness를 과대 선언하는 것

  * targeted smoke, manual in-game validation, roadmap closeout, refactor closeout을 release readiness / Workshop readiness / B42 readiness / tooltip completion / packaging 완료 / commit 완료 / 배포 완료로 확대 해석하지 않는다.

* generated / staging / diagnostic / fixture evidence를 current authority나 release state로 승격하는 것

  * runtime chunks, runtime-derived seed, rendered-only output, bridge-only output, chunk-generation-only output을 source authority로 읽지 않는다.
  * 숫자나 vocabulary를 기계적으로 치환해 authority migration으로 취급하지 않는다.
  * candidate predicate, regeneration parity evidence, dry-run, sandbox ledger, review_pending artifact를 cutover approval이나 release readiness로 읽지 않는다.

* current runtime authority를 과거 기준이나 임시 산출물로 되돌리는 것

  * historical staged hash, monolith runtime, staged Lua hash delta, package-only exclusion, finding inventory를 current runtime identity / deployable authority / cleanup trigger / closeout 근거로 쓰지 않는다.
  * legacy manual registry / T-Gate body를 current DVF contract로 되살리지 않는다.
  * `IrisDvfBridgeData.lua` legacy bridge artifact, staging quarantine payload, monolith export를 current bridge fallback / runtime authority / package allowlist로 되살리지 않는다.
  * old chunks와 successor chunks를 동시에 current로 두지 않는다.

* legacy adapter / fallback / compose repair 경로를 되살리는 것

  * implicit legacy fallback, runtime-side compose rewrite, external repair, hidden adapter dependency, retained mapping의 default / writer 재진입을 별도 reopen 없이 허용하지 않는다.
  * `selected_role`을 removal target / legacy residue로 읽지 않는다.
  * diagnostic-only compatibility mapping을 default authority debt나 complete-removal debt로 확대하지 않는다.

* quality / publish / runtime vocabulary를 혼동하는 것

  * `adopted / unadopted`를 quality-pass, publish_state, deletion, suppression 의미로 읽지 않는다.
  * `active / silent`를 current vocabulary로 되살리거나 sealed historical body를 직접 치환하지 않는다.
  * 별도 product decision 없이 `quality_exposed`, semantic quality UI exposure, quality baseline cutover, runtime_state slot 추가를 열지 않는다.

* 설명 계층을 해석 / 추천 / 비교 / 재작성 엔진으로 확장하는 것

  * 수치 비교, 체감 의미 해석, 조건부 요약, 자동 설명문 확대, 예외 침묵 리스트 누적, 브라우저 정렬 / 숨김만으로 오분류를 봉합하는 접근을 금지한다.
  * Iris를 AI 위키, 의미 추론기, 추천 엔진, 품질 판단 UI로 확장하지 않는다.

* Evidence / Source / Outcome 모델을 과거 방식으로 되돌리는 것

  * Evidence / DSL / allowlist / pipeline-spec을 닫힌 이슈 해결 명분으로 재개방하지 않는다.
  * `count==1`, property / tag / type gate, schema rewrite, 설명 파이프라인 재설계를 직접 해법으로 승격하지 않는다.
  * Context Outcome을 런타임 추론, 메뉴 문자열 기반 자동 outcome 생성, 단일 자동 경로, runtime analysis로 축소하지 않는다.
  * smoke / debug artifact를 fail-loud authority로 승격하지 않는다.

* Right-click source를 행동 의미 모델이나 느슨한 capability 모델로 되돌리는 것

  * 메뉴 존재 / 메뉴명 / UI 구조 / 전용 메뉴 여부만으로 evidence를 채택하지 않는다.
  * “행동 가능하면 된다”는 식의 추천 / 의미 해석을 허용하지 않는다.
  * `우클릭 행동`을 canonical evidence로 쓰거나, 조합 / 대체 / 타입 조건을 느슨하게 통과시키지 않는다.

* 의미 기반 capability를 기본 evidence 축으로 되살리는 것

  * `can_scrap_moveables`, `open_canned_food`, `stitch_wound`, `disassemble_electronics`, Equip / Use / Passive, 범용 도구 기능 묶음, 바닐라 5개 capability 축소 모델을 현 체계의 기본 evidence로 확정하지 않는다.

* Recipe / UI 목록 정책을 과거 방식으로 되돌리는 것

  * 연관 레시피를 행동 문장 단위로 쪼개 기본 표시하지 않는다.
  * 전역 기능 동등성 엔진, `(xN)` 수량 배지, 통계 힌트, 설명문 집필과 검증 동시 진행, 섭취 / 장착 / 레시피 / 무기 사용의 재혼합을 기본 해법으로 되살리지 않는다.

* closed readpoint를 resolved / publish / production target으로 과대 해석하는 것

  * Layer4 readpoint를 resolved state, current production target, publish mutation, public exposure, semantic quality interpretation, policy redesign 근거로 쓰지 않는다.
  * Structural Signal / ACQ_DOMINANT / Acquisition Lexical을 user-facing 기능 후보나 publish 후보로 승격하지 않는다.
  * Silent 21 / replacement reconstruction authority를 단독 authority나 original sealed authority 복원으로 표현하지 않는다.
  * 승인된 reconstruction 없이 silent-only rewrite를 실행하지 않는다.

* closed readpoint를 새 authority 없이 재개방하는 것

  * 새 입력 authority, 명시적 successor / correction scope, 또는 별도 approved plan 없이 닫힌 readpoint를 다시 열지 않는다.
  * isolated inventory reduction, subset-bounded source expansion, optional guard hardening을 넘어서는 재개방은 새 scope로 분리한다.

## Backlog
- 모드 시장 확장 시스템
- 내부 `.Iris` 정규화 및 외부 JSON/SQLite 입출력 정책 상세화

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

# 11. Historical Trace

Historical trace / provenance index는 ROADMAP 본문에서 더 이상 관리하지 않는다.  
과거 Addendum과 closeout 근거는 `DECISIONS.md` 및 각 round plan/review/closeout 산출물을 따른다.
