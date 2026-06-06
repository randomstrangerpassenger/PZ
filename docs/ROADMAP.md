# ROADMAP.md

> 상태: canonical summary + deduplicated consolidated addendum ledger through 2026-06-05
> 기준일: 2026-06-05
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

## Phase 1 — 실제 모드로더화

## Next
- 외부 모드 발견 구조 정리
- 외부 mixin 등록 경로 정리
- entrypoint 체계 설계
- 모드 메타데이터 / 의존성 / 충돌 처리 최소선 확정

### 이유
- 자기 자신만 부팅하는 수준을 넘어서, 실제로 외부 모드를 태울 수 있어야 플랫폼이 된다.

## Phase 2 — 플랫폼 성숙화

## Next
- 이벤트/콜백 예외 격리
- mixin 충돌 및 실패 진단
- API stable surface 초안 정리
- DevMode / 고급 로깅 / 디버그 오버레이 훅 정리
- Pulse public surface diversification 정리
  - Product surface
  - Stable Core surface
  - Starter surface
  - Guided surface
  - Raw/Internal surface

### 이유
- 단순 구동 성공만으로는 생태계를 받칠 수 없고, 실패 원인 가시화와 안정성이 필요하다. 동시에 현재 공개 전략의 핵심은 기능 추가보다 public surface 재설계다.

## Phase 3 — 1st-party 모드 지지 기반 완성

### Backlog
- profiler / engine optim / lua optim 이 필요로 하는 공용 capability 최소선 정리
- 거리 / 상태 / tick / phase 같은 측정·상태 노출 capability 의 최소선 정리
- Network / Registry / Scheduler / Config / EventBus / DataAttachments / GameAccess 중 실제 공용 surface 봉인
- 리소스팩 지원 capability 후보군 정리
- 바닐라 `기반 기능 후보군` 목록화

## Next
- API 확장 절차를 `기반 후보 추출 → 기반성 판정 → 중립 노출 가능성 검증 → surface 봉인` 순서로 문서화
- helper / thin wrapper / policy를 capability 후보에서 배제하는 판정 기준 정리
- 외부 공개 승격 조건을 `기술 가능 시점`이 아니라 **spoke 수요 형성 뒤의 gate** 로 문서화

## Hold
- 범용 DataBus / shared state / pub-sub 같은 모드 간 실시간 중개 채널 도입
- Pulse를 coordinator나 정책 허브처럼 비대화시키는 capability 확장
- `근거리면 FULL` 같은 정책 fast-path, recommendation, pressure 판단을 Core에 넣는 확장
- 하위 모듈의 snapshot/update 주기를 Core가 호출하거나 통제하는 구조
- 기반 후보 추출 이전의 무차별 API 증설
- helper / 편의 / 가이드 성격 기능의 Core 편입
- Pulse를 지금 당장 빈 플랫폼 형태로 전면 공개하는 것

### 이유
- 1st-party 모드의 정당성은 플랫폼이 먼저 성립할 때 생기지만, 현재 공개 전략의 병목은 기능 수보다 채택 마찰과 표면 설계다.

---

# 2. Echo

## 목표

병목 지점을 관찰하고 계측하는 프로파일링 모드. 현재 최우선 기준은 **observer-only 경계 유지 + 핫패스 무해성 동결**이며, 운영 전략은 **soft-freeze** 에 가깝다.

## Done
- Bundle A — Echo 핫패스 무해화 완료
  - 핫패스 4종과 금지 API 목록 확정
  - `EchoConfigSnapshot` + `EchoRuntimeState` + `volatile` 단일 참조 구조 반영
  - LifecyclePhase 기반 초기화/종료 구간 차단과 safe default 반영
  - `debugMode` 기반 듀얼 모드(릴리즈 무음 / 디버그 원샷 경고) 반영
  - `logSpike()` 조건부 호출, `safeContextCapture()` 옵션화, CAS rate-limit 반영
  - 코드 검토 기준 `non-invasive observer` 판정 확보

## Doing
- 최상위 기준은 **`Philosophy.md` 하나**이며, 과거 핸드오버/세션 요약은 작업 문서로만 취급
- 공개 전략상 후순위 유지
- Core capability와 분리된 관찰 모드 정체성 유지
- category / targetId / severity 같은 raw observation 중심 계약 유지
- recommendation / priority / under-pressure 판단을 Echo 공용 surface에 올리지 않기
- Bundle A 종료 후 핫패스 변경 동결 규칙 유지
- Echo를 **확장 전선이 아니라 soft-freeze / 유지보수 / 표면 보수 중심 모듈**로 운용

## Next
- Iris 이후 실제 blind spot이 확인될 때만 국소적 profiling 확장 재개 기준 정리
- observer-only 경계를 깨지 않는 범위에서만 유지보수/표면 보수 원칙 문서화

## Hold
- 플랫폼 성숙 이전의 과도한 공개 준비
- Echo를 recommendation 엔진이나 정책 라우터처럼 키우는 확장
- 다른 모듈이나 Core가 Echo 내부 `updateSnapshot()` 주기를 호출/통제하는 구조
- Bundle A에서 Pulse SPI / ProfilerSink 계약까지 함께 바꾸는 확장
- A를 ns 단위 벤치마크/JMH 중심 과제로 재프레이밍하는 것
- 핫패스 내 StackWalker / 풍부한 컨텍스트 / 일반 로그 유지
- Echo를 당장 다시 메인 개발축으로 승격하는 것
- 정밀 profiling 확장을 선제적으로 대규모 재개하는 것
- Echo severity / top_target / hint / insight를 Fuse 행동 입력으로 고착시키는 구조

---

# 3. Fuse

## 목표

Mixin 기반 엔진 안정화 모드. 평균 FPS 상승 약속보다 **엔진 비용 질서화, 평균 FPS 방어, 프레임타임 꼬리/스파이크 완화, 프레임 붕괴 방지**를 중심에 둔다. 특히 경로탐색/충돌/물리 축에서도 `더 똑똑한 결과`가 아니라 **게임이 무너지지 않게 하는 안전장치**를 목표로 한다.

## Done
- Area 7 — Pathfinding / Collision / Physics Stability 완료
  - `DuplicatePathRequestFilter`, `PathfindingBudgetGovernor`, `PathRequestDeferQueue`, defer-only `NavMeshQueryGuard`, `FrameLocalCollisionMemo(TTL=1)`, `PhysicsVelocityClamp`, `PathfindingPanicProtocol` 구현 및 합헌 감사 완료
- Area 8 — Save / IO Stall 계측 기반 완료
  - 저장 구간 감지용 state / event / mixin 실배선 완료
- Area 10 — GC / Allocation Pressure 계측 기반 완료
  - GC/heap pressure 관측·판정 계층과 동일 save clean-pair 기반 완충 검증 완료
- C 실전형 IO/GC 검증 종료
  - 실전형 OFF/ON 비교를 통해 mainline IO/GC Guard의 책임 경계와 한계를 충분히 판별

## Doing
- 최상위 기준은 **`Philosophy.md` 하나**이며, 과거 핸드오버/세션 요약은 작업 문서로만 취급
- 엔진 포크 금지 원칙 유지
- semantic-preserving 최소 개입 원칙 유지
- Core와 분리된 안정성 레이어 정체성 유지
- 핵심 가치 축을 Area 1 / Area 7에 두고, IO/GC는 `removed/동결 가능 + 계측 잔존` 부차 축으로 다루기
- 현재 Fuse 문제를 `기능 부족`이 아니라 **실제 tick time 입력 버그 수정 이후 검증·동결 단계에 들어간 안정성 레이어**로 해석하기
- Fuse는 현재 `개발 대상`보다 **동결·회귀 검증 대상**에 가깝다는 전략 판정 유지
- 다만 이를 `영구 동결`로 해석하지 않고, 필요 시 **Area 1 / Area 7 봉인 상태 점검을 위한 보수적 정산 재진입** 가능성은 열어둠
- Fuse를 `Burst stabilizer`로 보고, sustained load optimizer처럼 설명하지 않기
- 실시간 Echo-반응 튜너화 금지 유지
- Echo raw observation을 보더라도 임계값 판단 / recommendation 생성 / optimization 적용은 Fuse 내부 소유 유지
- 5개 구역 전담 원칙 유지
  - 좀비 AI / 업데이트 스텝
  - 라이팅 / 가시성 / 렌더 스파이크
  - 경로탐색 / 충돌 / 물리
  - 세이브 / 로드 / IO 스톨
  - GC / 할당 압력
- 경로탐색/충돌/물리 축에서는 `guard / limit / defer / deduplicate / stabilize`만 허용하고 결과 의미 변화는 금지


## Next
- Bundle C 회귀 검증과 재잠금
  - 실제 tick duration 입력 경로가 다시 퇴행하지 않는지 확인
  - OFF / ON(B) / ON(B+C) 비교에서 ACTIVE → Early Exit → COOLDOWN 구조가 일관되게 읽히는지 점검
  - `deep analysis 0` 해석 오류가 재발하지 않도록 판독 규칙 고정
- Fuse 검증 시나리오를 **Stress / Baseline / MP 2+1 체계**로 문서화
  - Stress = sustained 압박 + burst 포함, Bundle C 검증 전용
  - Baseline = UI/컨테이너/저부하 비개입 확인
  - MP = 2~3인 혼합 부하 검증
- 기존 약부하 OFF/ON 데이터의 `격하 보관` 규칙 정리
  - 공식 Stress 기준선에서는 제외
  - Baseline / Non-Interference 참고 자료로 유지
- 압축형 Fuse 운영 테스트 프로토콜 정리
  - 현실적 재현성 있는 시나리오만 Golden 후보로 인정
  - 시나리오 3개 이하
  - OFF 1회 + ON 1회 중심
  - 전체 6~8런 수준
  - 동일 세이브 정밀 복제보다 `Gate가 확실히 켜질 실전형 압박 패턴`을 우선
- 공개/README/핸드오버용 Fuse 포지셔닝 정리
  - `AI 최적화 모드`가 아니라 `AI 부하 폭주로 인한 엔진 붕괴 상태를 차단하는 안정성 레이어` 문구 사용
- Fuse 동결 선언을 지원하는 최소 문서 묶음 정리
  - 검증선
  - 판독 규칙
  - 금지선
  - README 설명 문구
- 생태계 다음 확장 우선순위는 **Fuse 추가 고도화보다 Nerve**라는 전략 정렬 유지
- 필요 시 Fuse 재진입은 `새 기능 개척`이 아니라 **Area 1 / Area 7 봉인 상태 점검·문서 정산** 범위로만 별도 판정


## Hold
- 근사/공격적 알고리즘 교체를 기본 레인에 포함
- 엔진 포크나 구조 재작성 전제의 확장
- B42 라이팅/가시성/렌더 스파이크 본격 대응
- 세이브/로드/IO, GC/할당 압력에 대한 과도한 성능 약속
- IO/GC Guard를 Fuse의 핵심 판매 포인트로 다시 밀어붙이기
- IO/GC Guard 튜닝 반복(threshold/minMult/hard/forced 재조정)
- C 실전형 시나리오를 추가 반복해 주 검증선으로 유지
- B42 가능성만을 근거로 IO/GC Guard를 메인라인에 존치
- Scenario B 같은 비현실적 병목 시나리오를 Golden 기준으로 유지
- `IPathfindingPolicy`류의 Pulse 정책 인터페이스
- `/fuse status` 같은 Fuse 상태창/명령/편의 기능
- `LOSThrottleGuard` 같은 AI 인지 타이밍 개입을 Area 7 1차에 포함
- Echo 관측값을 실시간 정책 입력으로 연결하는 구조
- sustained load에서 더 강하게 오래 개입하는 방향
- `deep analysis 0 = Fuse 미작동`으로 단정한 상태에서 정책을 손보는 것
- 동일 세이브 / 동일 행동 완전 재현을 필수 전제로 거는 실험실형 검증
- legacy `OptimizationHint` 같은 구경로를 메인 자동 최적화 경로로 복귀시키는 변경
- 학술형 대규모 반복 실험(30~50런 수준)을 현재 단계의 기본 검증 방식으로 채택
- `기준이 너무 높다`는 추정만으로 Bundle C 정책을 다시 뜯는 것
- Fuse를 `AI 최적화 모드`나 `평균 FPS 모드`로 재포지셔닝하는 것
- 실전 증명 이후 곧바로 Fuse 미세 최적화를 메인 우선순위로 승격하는 것
- Area 1 / Area 7 신규 고도화를 현 시점의 메인라인 개발축으로 다시 승격하는 것
- Fuse를 다시 `더 만들 대상`으로 되돌리는 것

---

# 4. Nerve

## 목표

100% Lua 기반 **선택적 안정성 Guard**. 현재 제품 기준선은 **Area 6 완료 + Area 5 v0.1 Final 동결**이며, 지금 단계의 강점은 `무작정 더 많이 넣기`보다 **자기 전장을 닫고 다음 전장을 합헌적으로 여는 것**이다. 동시에 Nerve는 `성공 기법 확장 모듈`이 아니라 **실패 축적과 회복 시간 검증을 위한 연구 장치**이며, **완전한 무의 공백지대가 아니라 기존 기법 조각은 있으나 완성형 답안을 직접 이식할 수 없는 공백지대**라는 점을 유지한다. 특히 Area 6은 **모드팩/멀티 타겟의 책임형 안정성 레이어**로 두며, 전수 래핑과 SelfRecursionGuard 같은 고위험 요소는 금지보다 **관리 가능성** 기준으로 평가한다. Fuse가 실전 증명 단계에 들어간 현재, Nerve는 Area 9까지 포함한 안정화 코어를 확보했고 **추가 고도화보다 동결·운용 판단**을 우선한다. 다음 생산적 이동은 Iris 쪽에 둔다.

## Doing
- 최상위 기준은 **`Philosophy.md` 하나**이며, 과거 핸드오버/세션 요약은 작업 문서로만 취급
- `Lua 병목 해결 모드`가 아니라는 정체성 유지
- Core와 분리된 Lua 안정화 레이어 정체성 유지
- 필수 모듈이 아니라 선택적 활성화 / dormant guard 포지션 유지
- **Area 6 긴급 수정 기준 동결**
  - 전수 커버를 목표로 할 때 `Events.*.Add` 전수 래핑은 사실상 필수라는 제품 판단 유지
  - 고위험은 제거보다 **관리 가능성(침묵 금지 / 피해 반경 제한 / 원인 분해 / OFF 즉시 복구)** 기준으로 다룸
  - 하이브리드는 `전부 섞기`가 아니라 **단일 트리거 / 단일 행동 / 보조 증거 결합** 원칙을 따른다
  - 기본값 `enabled = false`, `strict = false`
  - Default에서는 바닐라와 의미 동일
  - `EventDeduplicator` 사고방식 폐기, `EventRecursionGuard` 같은 최후 가드만 허용
  - 기본은 report-only / warn / back-off
  - `strict` opt-in에서만 `[!] LAST-RESORT DROP` 예외 허용
  - 래핑 충돌 시 해결보다 철수(back-off)
  - 현재 구현은 `완성 기능`보다 **임시 방파제 / incident 수집 도구**로 해석
  - `enabled = true`는 디버그성 임시 운용으로 보고, incident 리스너 개별 수정 전까지는 기술적 부채 상태를 숨기지 않음
- **Area 5 v0.1 Final 동결**
  - 데이터 즉시 반영
  - 같은 틱 안의 시각 갱신 coalescing
  - weak registry
  - snapshot 순회
  - executeFn optional fail-soft
  - overflow는 bypass 고정
- Area 5/6은 개념상 연속되더라도 **코드 직접 의존 없이** 각각 독립된 최소 안정화로 유지
- **일반 플레이 + 단일 고정 세이브 누적** 기반 연구 구조 유지
- `성공 기법 탐색`보다 **실패 귀속 / 금지 규칙 축적 / 회복 시간 판독**을 우선하는 연구 방법 유지
- Area 5·6의 9개 실패 축은 `제거 실험 대상`이 아니라 **Failure Atlas 분류 좌표계**로 취급
- `OFF가 더 안전`하다는 말은 **baseline safety / 책임 귀속 기준선**이라는 의미로만 사용
- Nerve에서 허용되는 정책은 **자기 제한 정책(back-off / retreat / non-intervention)** 뿐이고, 게임 행동 변경 정책은 금지
- **Echo ON / Fuse OFF / Nerve OFF** 연구 세팅 유지
- 세션 후 체감 태그를 먼저 남기고 Echo 로그를 AI와 함께 복기하는 분업 구조 유지
- 멀티는 있으면 가속 수단이지만 필수 전제는 아니라는 운영 원칙 유지
- 현재는 **기능 추가보다 전장 동결과 증명 강화가 우선**이라는 운영 판결 유지
- **Area 9 구현·검진 완료 후 동결**
  - 멀티/네트워크를 제어하는 기능이 아니라 **네트워크 경계 same-tick 철수형 보험 장치**로 유지
  - 1~7 가드는 관측·표시·계수만 수행하고, 행동은 마지막 `동일 틱 철수` 하나로만 연결
  - 기본 동작은 기본 OFF / 네트워크 경계 한정 / 대상 opt-in + 행동 opt-in 분리 / 동일 틱 철수 / 다음 틱 자동 복귀 유지
  - guarded path는 상시 `pcall`이 아니라 incident-gated `pcall` only 원칙 유지
  - 사건이 없고 로그가 조용한 상태를 `기능 부족`이 아니라 정상 성공으로 해석
- 분석 리포트는 **Echo 소유**, Nerve는 최소 상태 노출/사건 표식/에러 서명만 허용
- Frame은 Nerve와 기능 결합하지 않지만, 환경 계약/로드 순서/재현성으로 **Area 6 관리 가능성**을 끌어올리는 운영 도구로 취급


## Next
- **현재 단계는 새 설계가 아니라 실행 가능 상태 복구**
  - Area 6 설계 토론 재개방 금지
  - 새 트리거 / 새 행동 / 새 정책 추가 금지
  - 문법 / 진입점 / 실행 가능성 정리만 허용
- **Nerve Area 5·6 실행계획 v2.1 문서 수정은 종료**
  - 이제 이 문서는 설계 토론 표면이 아니라 **구현 기준서 / 집행 헌법**으로 취급
  - 새 아이디어 추가보다 구현 충실도와 런타임 증명이 우선
- **구현 착수 전 레포 신뢰성 / 재현성 게이트(P0~P2) 통과**
  - **P0**: conflict marker 제거, Lua vararg / 문자열 결합 / `NerveUtils.lua` 실코드 문법 확인, Java 문법 오류 제거
  - **P1**: `OnTick` 단일 진입점 원칙 확정 (`OnTick` / `OnTickEven` / start-end 이중 등록 혼선 제거)
  - **P2**: fail-soft / 예외 전파 정책을 문장과 주석 수준까지 통일
- **v2.1 기준 구현 착수**
  - classifier는 sustained 판단 입력 전용
  - `os.clock()`은 추세 판단용
  - SharedFlags는 내부 공유 범위만 허용
  - `후속 이벤트`는 동일 틱 + 동일 contextKey 재진입 경로로 정의
- **Area 6 긴급 수정 실행계획(vFinal)** 구현/검수
  - EventDeduplicator 삭제 또는 역할 교체
  - default OFF / strict OFF 기준 반영
  - same-tick self-recursion / listener exception만 제어 트리거로 봉인
  - wrapper 충돌 시 Area 6 OFF back-off 반영
  - 현재 Kahlua 제약 하의 `pcall` 기반 listener-unit 격리 경로를 incident / passthrough / rate-limited log와 함께 정직하게 문서화
  - Strict 예외는 `[!] LAST-RESORT DROP` 로그로 명시
- **현재 운용 상태의 기술적 부채 정리**
  - incident가 찍히는 문제 리스너 특정
  - 개별 리스너 수정 또는 격리 정책 재판정
  - `enabled=false` 복구 가능 여부 판단
  - stale xpcall/DEBUG 주석 정리
- Area 5/6 개입 경로의 **발동 증명** 강화
- ON/OFF에서 **의미 불변**이 유지되는지 검증 규칙 정리
- **S1 기본값 검증선** 정리
  - 설치 상태이더라도 Area 6 default에서는 바닐라와 동일해야 함
- 현재 개입이 **재현 가능**한지 보여주는 최소 증명 시나리오 정리
- 자연 발현 실패 리포트 누적
- 실패 축적용 연구 장치로서 **회복 시간 검증 기준** 정리
- 9개 원인 축 기준의 Failure Atlas 초안 구축
- Failure Atlas는 `축 제거 실험표`가 아니라 **실패 귀속 좌표계**라는 설명 문구 고정
- Nerve 자기 제한 정책(개입 조건 / 철수 조건 / 비개입 조건) 문장화
- Out-of-scope / A5 후보 / A6 후보 같은 1차 귀속 규칙 정리
- 세션 후 최소 태그 템플릿(`정상/불편`, 메모 1~2줄) 정리
- `다음은 왜 Nerve인가`를 README/핸드오버/로드맵 언어로 고정
- **배포 경계 문서화**
  - Nerve = standalone core
  - Nerve+ = Pulse 의존 core + convenience
  - `Lite / Full` 오해를 부르는 제품 언어 금지
- **Area 9는 기술 개발 단계보다 운용 검증 단계로 이동**
  - 실제 멀티 플레이와 실제 모드팩에서 조용히 Echo 리포트를 수집해 유지/폐기 판단 자료로 사용
  - 사건이 발생하면 `보험 장치가 실제로 세션 지속성에 기여했는가`만 본다
  - 사건이 거의 없고 로그가 조용하면 성공으로 해석하며, 억지로 기능을 더 붙이지 않는다
  - Duplicate / Shape / Depth / Forensic을 다시 행동 엔진으로 승격하지 않는다
  - 같은 틱 1회 철수보다 긴 격리나 더 똑똑한 판단은 열지 않는다
- **다음 생산적 이동은 Iris**
  - Nerve는 동결·데이터 수집·존폐 판단만 남기고, 새 기능 추가 대신 Iris 설계/구현 축으로 이동
- **Area 6 기초공사 종료 후 후속 검증**
  - `xpcall -> pcall` Kahlua 대응 수정이 바닐라 즉사 상태를 넘겼는지 재확인
  - 모드팩 환경에서 incident가 실제로 의미 있게 잡히는지 검증


## Hold
- 바닐라 Lua 자체를 상시 병목으로 전제한 최적화 축
- 성공적인 S5를 근거로 `필수 최적화 모듈` 포지션 채택
- MP 데이터 없이 이벤트별 임계값과 세부 동작 확정
- 사례가 희박한 인벤/컨테이너/UI 축의 과도한 확대
- Nerve+를 `진짜 버전`으로 오해하게 만드는 배포/홍보 언어
- 새 시작 반복 기반 연구
- 특화 테스트 시나리오 중심 실험 설계
- 플레이 중 실시간 실패 캐치 의무화
- Failure Atlas 축적 이전의 Fuse ON/Nerve ON 비교 실험 기본화
- Fuse가 못한 프리즈를 Nerve가 그대로 인수한다는 식의 역할 확장
- Area 6에서의 `EventPriority` / `Governor` / `Throttler` 조기 도입
- Area 6에서 의미 기반 allowlist / whitelist / AlwaysAllow 같은 예외 정책
- Area 6에서 `coalesce + flush` 같은 시점 변경형 우회안
- Area 6에서 지연·재정렬·넓은 global fallback 같은 의미 변화 위험 경로
- Area 6 래퍼 체인 고도화나 공존 전략을 기본 방향으로 채택하는 것
- `관측형 Nerve` 또는 `리포트 생성형 Nerve` 방향으로 되돌아가는 것
- 전수 래핑 없는 동등 Area 6 대체안을 계속 탐색하는 것
- 하이브리드를 `모든 조건을 한 엔진에 묶는 방식`으로 설계하는 것
- Nerve 자체 리포트 시스템 구축
- 현재 Area 6을 `근본 해결 완료 기능`으로 오해하는 문구나 포지셔닝
- Area 5에서의 시간 기반 debounce / `defer` / tick 넘김 캐시
- `drop` 정책
- `isVisible()` / visibility 기반 flush 판단
- UI 상태 기반 정책/편의 로직
- Area 5와 Area 6의 상태 공유 또는 코드 직접 의존
- Pulse로의 기능 상향 이동
- `ItemTransferBatcher` 조기 투입과 더 공격적인 batching
- **Area 8(IO/Save) 기능 개시**
- **Area 10(GC/메모리) 기능 개시**
- Area 9를 `멀티 최적화`, `네트워크 엔진 수정`, `패킷/핑 개선` 전장으로 여는 것
- Area 9에서 전역 상시 `pcall`이나 영구 차단, 자동 블랙리스트/화이트리스트를 기본화하는 것
- Area 9를 네트워크 진입 훅 밖의 일반 이벤트 / OnTick / UI / 렌더 축으로 확장하는 것
- Area 9에서 Duplicate를 기초공사 단계부터 early-skip 가드로 연결하는 것
- Area 9에서 Shape hard-fail을 기본 차단기로 승격하는 것
- Area 9 incident 조건을 비율/빈도/가중치/추세 기반으로 고도화하는 것
- Area 9 quarantine을 전역 키 / 다중 틱 지속 / 장기 상태 저장으로 키우는 것
- Nerve Area 9를 `멀티 최적화`, `네트워크 제어`, `다틱 격리`, `Echo 분석 재사용`, `중복 스킵 일반화` 방향으로 다시 여는 것
- Area 5/6 기초 안정성 결함 정리 전에 새 기능 축을 여는 것
- 타 게임/타 모드 안정화 기법을 `가져와 붙이기` 식으로 직접 이식하는 것
- 성공 사례를 일반화해 현재 연구의 기본 방법론으로 삼는 것
- Failure Atlas 축을 `하나씩 제거할 가설 목록`처럼 다루는 것
- v2.1 구현 기준서를 다시 설계 문서처럼 재개방하는 것
- Area 6 문법/진입점 정리 전에 새 트리거·새 행동·새 정책을 다시 여는 것
- `기능 더 넣는 고도화`를 현재 단계의 기본 방향으로 채택
- Fuse 자동정책 경로(`autoOptimize` 등)를 재활성화하는 것

---


# 4.5. 리팩토링 가드레일

## 목표

헌법·핫패스·외부 계약·실제 코드 상태를 깨지 않는 범위에서만 보수적으로 정리한다.

## Doing
- 최상위 기준은 **`Philosophy.md` 하나**이며, 과거 핸드오버/세션 요약은 작업 문서로만 취급
- 리팩토링을 `구조 미학`이 아니라 **실제 코드 상태 기반 보수 정리**로 취급
- 실제 코드 기준으로 `축소 / 스킵 / 보류` 가능한 로드맵 규칙 유지
- 외부 API / 스키마 / 핫패스 접근 경로를 리팩토링 명분보다 상위에 둠


## Next
- **Phase 0 기준선 확보**
  - Echo hot-path 회귀 기준선
  - Report 스키마 / Map 계약 기준선
  - FuseThrottle 동작·경계 기준선
  - EventBus fire/register 경로 회귀 기준선
- **EventBus 현실 경로 정리**
  - direct class lookup → FQCN O(1) fallback → 제한적 reflection/호환 호출의 3계층 경로를 구현 언어로 고정
  - 단일 `CopyOnWriteArrayList` 유지 + 등록 시점 `add + sort`를 기본 경로로 정리
  - 완전 순수화(FQCN/reflection 완전 제거)는 목표로 두지 않음
- 안전한 quick win 우선 정리
  - JsonConfigManager / 설정·직렬화 중복
  - 상수 / 로깅 / 포맷터 / 유틸 중복 정리
- 기존 인프라 강화
  - 새 GuardTest보다 기존 `HubSpokeBoundaryTest` 강화
  - 새 Locator보다 기존 `PulseServiceLocator` 확대 적용
  - 새 snapshot infra보다 하드코딩 기대값 테스트 유지
- 실제 코드 진단 후 선택 작업
  - EchoProfiler: hot-path 동등성 증명 시에만 조건부 분해 검토
  - ReportDataCollector: Map 반환 유지 전제의 내부 유틸/포맷터 추출 검토
  - FuseThrottleController: 이미 존재하는 메서드 경계 확인 후 추가 클래스 분리 필요 여부만 판단
  - DI: 전환이 아니라 규약 정리 / 누락 보완 / fallback 공존 규칙 정리


## Hold
- Phase 0 기준선 없이 EchoProfiler / Report / Fuse hot-path 구조를 여는 것
- `큰 클래스니까 일단 쪼갠다` 식의 기계적 분해
- 외부 Map 계약 / API / 스키마를 깨는 Report 재설계
- `DI 전환` 명목의 getInstance 전면 제거 / ServiceLocator 철거 / fallback 금지
- 실제 코드 확인 없이 문서상 Stage 1/2를 강행하는 리팩토링
- 핫패스에 추상 레이어 / 간접 호출 / facade 접근을 미학만으로 추가하는 것
- EventBus를 `엄격 타입 동일성만 허용`하는 이상형으로 즉시 순수화하는 것
- immutable list 교체 / compute 내부 새 리스트 생성 / 이진 삽입 중심 구현으로 COW 직관성을 깨는 것
- 새 ServiceLocator / 새 Guard 체계 / 대형 snapshot infra / 성급한 BaseConfig 공통 모듈을 선도입하는 것
- 실존하지 않거나 현재 대상이 아닌 spoke를 전제로 경계 테스트를 늘리는 것

# 5. Iris

## 목표

100% Lua 기반 위키형 정보 모드.

## Done
- 설명 출력 구조를 **기본 정보 → 의미(주 소분류) → 활용(레시피/상호작용) → 메타** 위계로 고정
- 분류 데이터는 유지하되, 기본 UI에서는 전면 노출하지 않고 메타 영역에 격리하는 정책 고정
- 다중 태그/교집합 문제의 해결 위치를 `정렬`이 아니라 **primary_subcategory 메타 anchor**로 확정
- Consumable 3-B(음료) 탭 문제를 `정렬 이슈`가 아니라 **anchor 데이터 부족 문제**로 판정하고, `primary_subcategory` 보강으로 UI 개선 확인
- Consumable 3-B(음료) 기준을 체감/수치가 아니라 **Drink / Drainable 구조 기준**으로 고정
- `Philosophy.md`만을 최상위 기준으로 다시 고정하고, 핸드오버/세션 요약은 작업 문서로만 취급
- 설명 왜곡 이슈의 책임 위치를 **설명 엔진**이 아니라 **태그 생성 단계(Core / Rule / predicate)** 로 재판정
- Tool 1-A / 1-B 왜곡 이슈를 **DSL 부족이 아니라 tuple integrity 구현 버그**로 정리
- 이번 이슈에 대해 코드 수정과 Walkthrough 최신화까지 마쳐, **문서 / 코드 / 설명 일치** 상태로 복구 완료
- Context Outcome 추출기 로드맵을 **단일안 채택 문서가 아니라 3안 병렬 보존형 통합 로드맵**으로 재정리
- Context Outcome 추출기를 **문서 1:1 기계화용 오프라인 사실 테이블 생성기**로 재정의
- Context Outcome 추출기와 Iris 엔진의 경계를 **외부 공급자 / 내부 소비자**로 다시 고정
- Context Outcome 문서 개정 단계 종료
  - Allowlist / DSL / Evidence Table에 Context Outcome을 반영하고, 문서 간 동기화 문제 없음을 재확인
- 우클릭 계열 정보의 허용 형태를 **행동이 아니라 항상 성립하는 결과(Context Outcome)** 로 고정
- 설명 엔진을 건드리지 않고도 우클릭 계열 실용 정보를 수용하는 철학적 경계까지 정리 완료
- Context Outcome 추출기의 내부 경계를 `스캐너 / IR(signal only) / 매퍼(Signal → Outcome) / 수동 주입기 / 검증기 / 진단기`로 고정
- Context Outcome의 Fail-loud 범위를 **Allowlist 밖 Outcome / 비결정성 / 출력 포맷 위반** 3종으로 제한
- `smoke_item`을 **Option B 수동 주입 전용**으로 격리하고, 자동 경로 탐지는 진단으로만 남기기로 확정
- Fixing / Moveables를 Context Outcome 소스로 승격하지 않고 기존 evidence / predicate 경로에 남기기로 확정
- `equip_back`를 Wearable.6-F의 **핵심 증거**로 바로잡아 문서 1:1 기계화 기준 재확인
- Context Outcome 실행계획 v3를 **FINAL 승인 / 동결 가능한 실행 계약** 상태로 종료
- Iris Evidence를 **행동 모델이 아니라 결과 상태 모델**로 재정의하고, Recipe / Right-click / Static capability를 서로 다른 **Source**로 정리
- 실제 바닐라 데이터 적용을 통해 상태형 outcome(`equip_back`, `toggle_activate`, `place_world`, `fill_container`, `empty_container`, `transform_replace`) 중심 구조가 맞음을 확인
- `우클릭 행동 증거 시스템 도입` 단계를 **Source 분리 + Evidence 통합 + Rule 통합** 상태로 닫음
- Right-click을 Recipe의 변주가 아니라 **레시피로 잡히지 않는 기능적 용도용 독립 Source 트랙**으로 재정리
- Right-click source의 canonical 기준을 `메뉴 존재`가 아니라 **아이템 의존 + 상태 변화**로 재설계
- 메뉴 존재 / 메뉴명 / UI 구조 / 비활성 표시 여부는 핵심 판정 기준이 아니라 **보조 관찰 정보**로 강등
- Right-click source를 **Strong / Weak Evidence** 이원 구조로 운용하기로 확정
- `can_scrap_moveables`는 현재 의미 그대로 유지하지 않고, 단일 결과 상태 단위로 해체/재정의해야 한다는 점을 유지 확인
- 의미 기반 capability(`can_stitch`, `can_repair`, `can_attach_weapon_mod` 등) 대신 **상태 변화 유형** 중심으로 정리하기로 확정
- `Source 분리 / Outcome 중심 단일 Evidence 프레임`은 유지하고, Right-click source coverage는 **item-dependence + state-change** 기준으로 다시 고정
- 바닐라 5개 capability 축소 구조는 최종 체계가 아니라 임시 축소 결과로만 남긴다는 점을 재확인
- Recipe 기반 evidence 시스템은 현 단계에서 안정적이며, 재설계 초점이 **Right-click source**에만 있음을 확인
- Source extractor는 병렬화하되, Evidence 모델과 Rule 소비 구조는 **Outcome 중심 단일 프레임**으로 유지하기로 확정
- Equip / Use / Passive 정보는 기본 evidence 축으로 올리지 않고 **개별 설명층 후행 정보**로 남기기로 정리
- `primary_subcategory`의 역할을 **브라우징 anchor**로 재정의하고, 주 소분류 설명 문장을 자동 기본값이 아니라 **후보 템플릿**으로 강등
- 연관 레시피 표시 기본 단위를 `[레시피:n]` 또는 행동 문장 묶음이 아니라 **레시피명 단위 접기/펼치기**로 정리
- 전역 기능 동등성 그룹화 로드맵을 중단하고, **UI 목록 단계에서만 DisplayName 중심 접기**로 방향 전환
- 접힌 목록의 `(xN)` 표기를 제거하고, **목록은 개념 / 상세는 실체** 원칙으로 정리
- 개별 아이템 정보 작업 순서를 **분류/증거 체계 고정 → Outcome source 검증 → 결과 상태 fact 고정 → 필요 시 설명 문장화**로 고정
- 여기서 Right-click은 **Evidence가 아니라 Outcome source**이며, `우클릭 행동`은 walkthrough용 작업 용어로만 제한
- 지금 단계의 1차 산출물을 개별 설명문이 아니라 **source 확인 + outcome fact table** 정리로 재정의

- Right-click Evidence의 Strong 판정에 `직접 실행 주체 + 비대체성` 조건을 추가로 고정
- Strong / Weak를 UI 등급이 아니라 **채택 / 제외 필터**로 재정의
- `can_attach_weapon_mod` 개별 검수 완료: Bayonet만 Strong, 나머지 파츠류는 기본 Weak 패턴으로 정리
- `can_extinguish_fire` 샘플 구조 판정 완료: 컨테이너 계열은 전반 Weak 패턴으로 정리
- 기존 등록 `can_*` Right-click 필드의 개정 정의 기준 재검수 단계 종료

- DVF 3-3 second-pass execution / manual validation closeout을 완료하고, current runtime baseline을 `2105 rows / adopted 2084 / unadopted 21` 기준으로 재봉인. Legacy `active/silent`는 runtime_state 문맥에서 `adopted/unadopted`로 읽음
- three-axis contract migration과 `publish_state` visibility contract를 current user-facing 기준으로 닫음
- surface contract authority migration / Korean lexical hardening / identity_fallback source-expansion current cycle / distribution remeasurement gate를 모두 close 상태로 정리
- future reopen round sizing governance를 **subset-bounded single-authority rule** 로 고정
- compose authority migration과 Phase D/E staged rollout을 `ready_for_in_game_validation` 상태까지 닫음
- EDPAS 기준으로 shipped body_plan artifact authority와 direct default compose entrypoint authority의 불일치를 해결 완료
- `DVF 3-3 Runtime-State Vocabulary Remap and Three-Axis Readpoint Seal` round를 docs-only readpoint seal로 닫음. Current authoritative readpoints use `adopted/unadopted`; historical sealed decision bodies are preserved and legacy `active/silent` runtime_state wording is read through the terminology migration note
- 2026-05-08 Iris refactor roadmap v2.0을 **코드 구현 기준으로 완료**했다.
  - P0-P7 정리 완료
  - deferred 항목을 policy-only close가 아니라 runtime/build code로 구현 완료
  - `Iris/Util/IrisProtectedCall.lua`로 protected-call boundary 중앙화 완료
  - `IrisUseCaseDescriptions.lua`를 facade로 축소하고 `Iris/Data/UseCaseDescriptions/Chunk001..009.lua`로 Lua chunk externalization 완료
  - `IrisDesc` 구현을 `Iris/Logic/IrisDesc/*`로 이동하고 old `Pulse/Iris/Logic/IrisDesc/*`는 compatibility wrapper로 유지
  - Browser requirement display policy를 `Iris/UI/Browser/IrisRequirementPolicy.lua`로 분리
  - `IrisConfig.MAP_ICON_BUTTON`으로 MapIcon 위치 설정화 완료
  - root `Iris/build` Python entrypoint surface를 `ENTRYPOINTS.md` 기준으로 정리
- 2026-05-08 item selection runtime regression을 수정했다.
  - 원인: 새 `Iris/Logic/IrisDesc/*.lua` 구현 파일의 UTF-8 BOM이 PZ Kahlua compiler에서 `Generator.lua` require 실패를 유발
  - 조치: BOM 제거, `IrisAPI`의 description generator load를 session당 1회 시도 guard로 제한
  - targeted in-game smoke: Iris 메뉴 item selection error accumulation fixed
- 2026-05-08 `Iris Refactoring Final Roadmap v1.4`를 구현/테스트/콘솔 검증 기준으로 닫았다.
  - closeout record: `Iris/_docs/refactor/iris_refactoring_final_roadmap_closeout.md`
  - Phase 1부터 Phase 5-9까지 planned implementation scope 종료
  - 최신 전체 테스트: `376 tests / OK`
  - 최신 KO runtime smoke: `Iris/Util/IrisModuleBootstrap.lua` 로드, `[Iris] Bootstrap complete`, Iris error pattern 0건, `TestHarness` 0건
  - Phase 5-8 English detail fallback validation은 optional follow-up evidence로만 남김
- 2026-05-12 `최종 리팩토링 로드맵 v4.1`을 구현/정적 검증/인게임 콘솔 검증 기준으로 닫았다.
  - source plan: `C:/Users/MW/Downloads/1.txt`
  - closeout record: `Iris/_docs/refactor/iris_refactoring_final_roadmap_closeout.md`
  - T0-A/T0-B/T0-C, T1-A, T1-B 1단계, T2-A/T2-B/T2-C, T3-C 완료
  - T3-A/T3-B는 Pre-Gate 기준 stale/no-op으로 처리
  - 최신 전체 테스트: `380 tests / OK`
  - `test_require_render.py`: PASS
  - `quality_gates.py`: PASS
  - latest in-game validation: `IrisLayer3Data.lua` 0 loads, `IrisLayer3DataChunks.lua` 1 load, chunk file 11 loads
  - installed runtime monolith path absent, CheatMenu context-menu regression markers 0 matches

- 2026-05-17 selected-role native resolver authority redefinition을 current readpoint로 흡수했다.
  - Diagnostic-only isolation은 frozen-baseline prerequisite 기준 `A1_sufficient`로 유지
  - Complete-removal은 current selected-role / resolver cleanup 목표에서 제외
  - selected-role bridge는 non-zero finding으로 유지하되, `selected_role`은 legacy fallback 제거 대상이 아니라 native resolver authority로 채택
  - Frozen 2105 byte-level reconstruction / AI-trace authority rebaseline은 current diagnostic-only guard path의 blocker가 아님
- 2026-05-17 `Diagnostic-only Resolver Compatibility Guard Round`를 `closed_with_diagnostic_only_resolver_guard`로 닫았다.
  - default resolver는 native v2 authority로 해석할 수 없는 legacy compatibility label fallback을 `DEFAULT_RESOLVER_REJECTED_LEGACY_COMPAT_LABEL`로 fail-loud
  - explicit diagnostic resolver mode는 `--mode diagnostic_resolver` / `resolver_authority_mode='diagnostic'`로만 열림
  - rendered preview text delta `0`, default path legacy fallback reach `0`, selected-role AI-trace/native influence stability `264 / 642` 유지
  - 전체 Python validation: `386 tests / OK`
  - runtime Lua regeneration, adapter removal, deployed closeout, `ready_for_release` 선언 없음
- 2026-05-17 residual resolver compatibility debt를 adapter / diagnostic compatibility disposition debt로 재정의했다.
  - active resolver correctness debt는 닫힌 상태로 읽음
  - legacy compatibility mapping은 default authority가 아니라 managed diagnostic-only surface로 격리됨
  - 남은 decision surface는 adapter diagnostic-only 유지/제거, diagnostic legacy mapping 보존/물리 삭제 여부
  - 두 surface 모두 별도 disposition round 없이 current blocker나 필수 removal 목표로 읽지 않음
- 2026-05-18 `Adapter / Diagnostic Compatibility Final Disposition Round`를 `closed_with_adapter_removed_mapping_permanently_diagnostic_only`로 닫았다.
  - `Residual Resolver Compatibility Final Disposition Debt`는 resolved / closed
  - legacy compatibility mapping은 permanent diagnostic-only non-authority fixture로 보존
  - post-migration exposed legacy adapter entrypoint modes는 제거
  - 두 잔여 표면 모두 `removed` 또는 `permanently retained as diagnostic-only non-authority surface` 결론 보유
  - adapter dynamic reach `0`, default/writer adapter dependency `0`, rendered delta `0`
  - 전체 Python validation: `386 tests / OK`
  - runtime Lua regeneration, deployed closeout, manual in-game QA, Workshop readiness, `ready_for_release` 선언 없음
- 2026-05-18 `Silent Metadata Intake / Cleanup Round` opening attempt는 authority gate에서 blocked로 기록했다.
  - original expected `silent_metadata_inventory.21.jsonl` 및 `migration_manifest.2084.jsonl`은 current checkout/local git history에서 확인되지 않음
  - AI-trace inventory와 dry-run payload는 supporting trace로만 유지
  - shape-only 2084/21 candidate는 silent 21 authority 후보로 승격하지 않음
  - source metadata mutation, runtime Lua regeneration, rendered rebaseline, top-doc cleanup closeout 없음
- 2026-05-18 `Silent 21 Replacement Authority Reconstruction Round`를 `closed_with_replacement_authority_adopted`로 닫았다.
  - missing original sealed artifacts는 provenance gap으로 봉인
  - sprint7 2105-row payload와 dry-run post-migration decisions의 silent set 21/21 identity match를 primary reconstruction basis로 채택
  - AI-trace inventory는 supporting trace only, shape-only 2084/21 candidate는 rejected non-authority
  - silent 21 replacement allowlist와 silent-only `interaction_tool -> tool_body` mapping authority adopted
  - cleanup input rule은 `historical sealed authority OR adopted replacement reconstruction authority`를 받을 수 있도록 amended
  - cleanup rewrite, runtime Lua regeneration, rendered rebaseline, deployed closeout, Workshop readiness, `ready_for_release` 선언 없음
- 2026-05-18 `Silent Metadata Intake / Cleanup Round`를 Branch B로 닫았다.
  - adopted replacement authority의 21-row allowlist만 target으로 소비
  - target 21개 row에서 `compose_profile`만 `interaction_tool -> tool_body`로 rewrite
  - `persisted_old_profile_count = 0`
  - `silent_old_profile_count = 0`
  - active 2084 unchanged
  - row_count 2105 unchanged
  - rendered/Lua/runtime/state surfaces unchanged
  - 전체 Python validation: `386 tests / OK`
  - runtime rollout, deployed closeout, Workshop release, manual in-game QA pass, `ready_for_release` 선언 없음
- 2026-05-19 `Runtime Payload Enum Rename Scope Round`를 Branch B/B1로 구현했다.
  - current canonical payload enum: `adopted / unadopted`
  - legacy `active / silent`는 diagnostic / import / historical read-only alias로만 허용
  - default current writer / validator path는 legacy enum을 `DEFAULT_RUNTIME_STATE_REJECTED_LEGACY_ENUM`로 fail-loud
  - source decisions: `active->adopted` 2084 rows, `silent->unadopted` 21 rows
  - runtime/package chunks: `source="silent"` 21 tokens -> `source="unadopted"`
  - row_count 2105, row identity, rendered text, quality_state, publish_state unchanged
  - Browser/Wiki/Tooltip static consumer scan: enum dependency 없음
  - hash / payload delta evidence: `runtime_payload_delta_report.json`
  - 전체 Python validation: `388 tests / OK`
  - Lua syntax validation: `powershell -ExecutionPolicy Bypass -File .\tools\check_lua_syntax.ps1` -> `183 files / OK`
  - implementation/static-validation 기준 해결 완료
  - runtime rollout, deployed closeout, Workshop release, manual in-game QA pass, `ready_for_release` 선언 없음
- 2026-05-20 `Static Report Label Cleanup Round`를 `closed_with_no_current_operator_residue_found`로 닫았다.
  - Surface C rewrite-disposition `active/silent` current report/operator label residue `0`
  - Phase 3 mutation count `0`
  - sealed evidence hash gate pass
  - source decisions, rendered text, runtime Lua, chunk topology, quality_state, publish_state unchanged
  - 전체 Python validation: `388 tests / OK`
  - Lua syntax validation: `183 files / OK`
  - runtime rollout, deployed closeout, manual in-game QA pass, Workshop readiness, `ready_for_release`, repo-wide `active/silent` zero 선언 없음
- Generated report / operator label cleanup 문제를 preflight-gated cleanup으로 재정의했다.
  - 기존 문제 매핑: terminology migration과 cleanup mutation 단계에서 분리
  - 재정의: generated report/operator artifact의 `active/silent` 표기가 current label처럼 보일 수 있는지는 먼저 occurrence-level inventory와 Surface C 분리로 확인해야 함
  - 현재 닫힌 것: canonical read 문구, terminology migration note, runtime payload enum rename, Static Report Label Cleanup preflight / scope lock
  - 실제 미해결: current artifact mutation은 target `0`으로 열리지 않았으며, future builder output guard만 별도 hardening 후보
  - 다음 라운드 범위: 새 residue 의심이나 새 generated/operator artifact가 생기면 `Static Report Label Cleanup Preflight / Scope Lock Round`부터 열고, target이 있을 때만 mutation manifest로 넘김
  - 완료 조건: Surface C rewrite target occurrence count 봉인; target `0`이면 `closed_with_no_current_operator_residue_found`, target 존재 시 Phase 3 mutation으로 진행; historical sealed body 직접 치환 금지
- Static Report Label Cleanup no-residue closeout을 원래 cleanup 의도에 대한 해결로 보지 않도록 정정했다.
  - 원래 의도: 실제 있던 generated report / operator label의 `active/silent` current-label 표기 치환
  - 이번 closeout의 실제 의미: current checkout Surface C preflight에서 rewrite target `0`
  - 문제점: 리팩토링 / artifact 이동 / artifact 소멸로 원래 문제 artifact referent가 사라졌거나 current Surface C 정의 밖으로 밀렸을 수 있음
  - 실제 미해결: 원래 문제 artifact referent 식별, 복구/재생성 가능성 확인, referent 기준 label cleanup
  - 다음 라운드 범위: `Static Report Label Cleanup Referent Recovery Round`
  - 완료 조건: 원래 artifact referent 기준 residue `0` 증명 또는 실제 치환/재생성; referent가 사라졌다면 cleanup 완료가 아니라 blocked/obsoleted closeout으로 닫음
- 2026-05-20 `Static Report Label Cleanup Referent Recovery Round` Branch A closeout을 reopened/superseded로 정정했다.
  - 보존되는 좁은 사실: prior Surface C 3개 runtime payload enum round diagnostic/operator evidence artifact는 회수됐고 diagnostic-only non-authority로 분류됨
  - 해당 3개 artifact 기준 current operator label residue `0`
  - Phase 5 mutation count `0`
  - 이전 검증 사실: Python validation `388 tests / OK`, Lua syntax validation `183 files / OK`
  - 정정된 current state: `blocked_absence_proof_incomplete`
  - 이유: approved plan의 원래 대상은 prior Surface C 3개가 아니라 original generated report/operator artifact referent였고, outside-prior-Surface-C candidates full adjudication이 끝나지 않았음
  - cleanup complete, no-residue closeout, repo-wide `active/silent` zero, diagnostic/import/historical alias removal 선언 없음
- 2026-05-20 `Static Report Label Cleanup Referent Recovery Round`를 Branch D `blocked_missing_original_operator_artifact_referent`로 닫았다.
  - four-lane discovery/adjudication 완료
  - candidate_count `187`
  - primary_referent_set `[]`
  - prior Surface C 3개는 diagnostic-only evidence로만 보존
  - outside-prior-Surface-C current candidates 3개는 historical worksheet / legacy metric key surface로 분리
  - confirmed referent 부재로 current_operator_label_residue count는 `null / not_applicable`
  - mutation count `0`
  - adversarial review `PASS`, blocker `0`, major `0`
  - 전체 Python validation: `388 tests / OK`
  - Lua syntax validation: `183 files / OK`
  - round builder command 자체는 blocked closeout 표현으로 exit code `1`
  - cleanup complete, no-residue closeout, repo-wide `active/silent` zero, active/silent 일괄 삭제 선언 없음
- 2026-05-21 `Legacy Active/Silent Current-Surface Guard Round`를 후속 hardening 문제로 분리했다.
  - 기존 cleanup/referent recovery chain의 선행작업이 아니라 Branch D 이후 future reintroduction guard 후보로 읽음
  - 목표: current authority path에 legacy `active/silent`가 current-label로 재유입되는 것을 fail-loud
  - hard-fail surface와 allow surface를 manifest로 분리해야 함
  - historical sealed body, staging evidence, diagnostic/import alias, legacy metric key, test fixture는 직접 치환하지 않음
  - original artifact cleanup success, repo-wide `active/silent` zero, alias removal 선언 없음
- 2026-05-23 `DVF 3-3 Current Runtime Baseline Seal Round`를 `sealed_with_inventory_findings`로 닫았다.
  - current deployable runtime baseline: manifest + `Chunk001..011`, row_count `2105`, `adopted 2084 / unadopted 21`, monolith `absent`
  - missing `publish_state 19` / nil `text_ko 19`는 finding-aware handoff target으로 보존
  - duplicate runtime key `0`, legacy `active/silent` payload residue `0`
  - runtime/source/consumer mutation count `0`, unclassified delta `0`
  - Python unittest `394 tests / OK`, Lua syntax `183 files / OK`
  - MIGV-QA Phase 1 identity pre-gate는 `current_runtime_hash_manifest.json` sha256 `790b5689097a8856e6213074fda25b723060073206a7ca44bd26d9f6f08c9171`를 사용하며 historical `0390272b...`를 current gate로 쓰지 않음
  - manual in-game validation, deployed closeout, runtime rollout, release/Workshop readiness, tooltip validation 선언 없음
- 2026-05-24 `Iris DVF 3-3 Manual In-Game Validation QA Round`를 `closed_with_manual_in_game_validation_complete_revised_contract`로 닫았다.
  - current runtime baseline seal을 identity pre-gate로 소비
  - project default playtest baseline을 practical in-game validation environment로 수용
  - evidence root: `Iris/Playtest/`
  - Browser screenshots: `.223 탄약 상자`, `스크류드라이버`, `철조망`, `서류 가방`, `앞치마`, `빗자루`
  - revised contract: Iris Browser는 all-item Browser이며 item-entry visibility와 Layer 3 body/source quality는 분리
  - `앞치마` internal_only item entry visibility와 `빗자루` nil `text_ko` item entry visibility는 raw token / raw nil / table address / broken placeholder가 없으므로 pass
  - separate Wiki/detail 및 default bounded baseline captures는 이번 user-supplied in-game closeout에서 별도 필수 증거로 보지 않음
  - `jq empty` over updated MIGV-QA JSON artifacts -> exit code `0`
  - Lua syntax validation: `Lua syntax validation OK: 183 files`
  - release readiness, Workshop readiness, B42 readiness, tooltip completion, packaging/release-note/commit/Workshop publish 선언 없음
- 2026-05-25 `Semantic UI Exposure / quality_exposed` 문제를 no-exposure disposition으로 닫았다.
  - `quality_exposed`는 활성화하지 않고 reserved inactive로 유지
  - `quality_state`는 offline/internal authoritative contract로만 유지
  - Browser / Wiki / Tooltip consumer는 quality 판정을 badge, copy, sorting, filtering, hiding, recommendation, trust/confidence 표시, quality proxy로 소비하지 않음
  - user-facing quality copy는 정의하지 않음
  - raw quality token 또는 quality judgment wording의 user-facing 노출은 contract violation
  - runtime Lua mutation, consumer implementation change, leak guard validator/test 구현 완료, release readiness 선언 없음
- 2026-05-30 `ACQ_DOMINANT Current Baseline Remeasurement Round`를 `closed_with_acq_dominant_current_baseline_sealed_no_publish_candidate`로 닫았다.
  - occurrence_count `1283`
  - authority class counts: `diagnostic 936 / historical 236 / observer_only 94 / test 17`
  - `writer_input_count = 0`, `forbidden_writer_reach_count = 0`, `publish_candidate_count = 0`
  - 후속 publish review는 열지 않는다.
  - source/rendered/runtime/state mutation, semantic quality completion, runtime rollout, release readiness 선언 없음
- 2026-05-31 `Layer4 Boundary Current Corpus Lock Round`를 `closed_with_layer4_boundary_current_corpus_locked_no_count_inheritance_design_preflight`로 닫았다.
  - `LAYER4_ABSORPTION_CONFIRMED` 후속 측정용 current artifact universe / measurement corpus / excluded surface classes / no-inheritance rule을 봉인했다.
  - included corpus는 body-role lint substrate 4개 path로 고정된다.
  - `inventory_count = 21914`, `classified_count = 21914`, `excluded_surface_count = 460`
  - `unknown_count = 0`, `unclassified_count = 0`, `excluded_unknown_count = 0`, `writer_input_class_count = 0`
  - manifest sha256 `d394f95f5f2a157679238e005a90929349eb807a8180824d8f0ed30240290402`
  - design-only preflight로 닫았고 machine-enforced preflight는 구현하지 않았다.
  - `LAYER4_ABSORPTION_CONFIRMED` current count 산출, Layer4 resolved, source/rendered/runtime/state mutation, runtime rollout, release readiness 선언 없음
- 2026-05-31 `Layer4 Confirmed Detector Field Map Seal Round`를 `closed_with_confirmed_measurement_unavailable_trace_absent`로 닫았다.
  - detector closeout branch: `TRACE_EDGE_ABSENT_MEASUREMENT_UNAVAILABLE`
  - current locked corpus에는 explicit Layer4 source object -> Layer3 body slot trace-edge field가 없다.
  - candidate field path count `188`, explicit trace-edge field path count `0`, ambiguous field path count `0`
  - downstream count disposition은 `not_applicable_under_current_corpus`
  - current count 산출, live-corpus occurrence count, zero-occurrence closeout, Layer4 resolved, source/rendered/runtime/state mutation, runtime rollout, release readiness 선언 없음
- 2026-06-01 `Layer4 Trace-Edge Authority Admission Round`를 `EDGE_AUTHORITY_PRODUCED_AND_ADMITTED`로 닫았다.
  - 기존 explicit trace-edge recovery count는 `0`이고, build-time/body_plan generation relation sidecar를 생산했다.
  - generated edge artifact rows `24`
  - produced artifact: `Iris/build/description/v2/staging/compose_contract_migration/layer4_trace_edge_authority_admission_round/layer4_trace_edges.v1.jsonl`
  - admission partition은 `current_detector_input`
  - detector readiness dry-run은 `pass`
  - `confirmed_measurement_executed = false`, `confirmed_count = not_computed`
  - current count 산출, live-corpus occurrence count, zero-occurrence closeout, Layer4 resolved, source/rendered/runtime/state mutation, runtime rollout, release readiness 선언 없음
- 2026-06-02 `Layer4 Confirmed Detector Field Map Reseal Round`를 `closed_with_layer4_confirmed_detector_field_map_resealed`로 닫았다.
  - admitted trace-edge artifact 기준 confirmed detector field map을 봉인했다.
  - input artifact sha256 `44a863a288bb1debf570a1d1b63a35f31a29661f09e3175003939d364496c1ca`
  - field map roles: `source_ref / row_id / destination_slot / edge_type`
  - `edge_basis`는 explicit relation tuple support로 보존한다.
  - admitted edge row count `24`는 artifact shape metric이며 confirmed count가 아니다.
  - `confirmed_measurement_executed = false`, `confirmed_count = not_computed`
  - current count 산출, live-corpus occurrence count, zero-occurrence closeout, Layer4 resolved, source/rendered/runtime/state mutation, runtime rollout, release readiness 선언 없음
- 2026-06-02 `Layer4 Confirmed Current Count Remeasurement Round`를 `closed_with_layer4_confirmed_current_count_measured_positive`로 닫았다.
  - sealed current corpus lock, admitted trace-edge authority, sealed detector field map을 함께 소비했다.
  - detector executed: `true`
  - confirmed_count `24`
  - confirmed_count_basis `detector_execution`
  - confirmed_count_scope `row-level qualified admitted generated generation-time trace-edge rows`
  - input_edge_row_count `24`는 artifact shape metric이며 count shortcut이 아니다.
  - rejected_fallback / ambiguous / unavailable / malformed / out_of_corpus counts: `0 / 0 / 0 / 0 / 0`
  - prior zero-count inheritance, Layer4 resolved, source/rendered/runtime/state mutation, publish review, runtime rollout, release readiness 선언 없음
- 2026-06-03 `Layer4 Confirmed Measurement Canonicalization Boundary Seal Round`를 `closed_with_layer4_confirmed_measurement_canonicalized_as_readpoint_only`로 닫았다.
  - confirmed_count `24`는 current canonical measurement readpoint only로 봉인됐다.
  - count_source는 `sealed_detector_execution`이고 measurement_readpoint `true`, canonical_resolved_state `false`다.
  - validation_ceiling `docs_governance_boundary_only`
  - COMMON-RELEASE-NONDECISION / COMMON-RUNTIME-SURFACE-NONMUTATION 유지
  - Layer4 resolved, publish/runtime/source/state mutation, public exposure, runtime rollout, release readiness 선언 없음
- 2026-06-03 `Layer4 Boundary Namespace Reseal Round`를 `closed_with_layer4_boundary_namespace_resealed_b3_dual_axis`로 닫았다.
  - `LAYER4_ABSORPTION_CONFIRMED`는 independent `layer_boundary_hard_block_namespace`로 읽는다.
  - `FUNCTION_NARROW / ACQ_DOMINANT`와의 관계는 `separated`
  - M1 confirmed_count `24`는 measurement readpoint only
  - M2 current build application target axis는 별도 축이며 이 round에서는 current `0` reseal을 주장하지 않았다.
- 2026-06-03 `Layer4 Current Build Application Target Remeasurement / Zero Reseal Round`를 `closed_with_layer4_m2_current_build_application_target_zero_resealed`로 닫았다.
  - basis_status `available_by_current_surface_absence_scan`
  - zero_reseal_basis `no current production/build/runtime path consumes LAYER4_ABSORPTION_CONFIRMED`
  - current production build consumer count `0`
  - m2_current_build_application_target_count `0`
  - current zero reseal claimed `true`
  - M1 confirmed_count `24`는 measurement readpoint only로 유지
  - M2 positive count, M1 count inheritance, Layer4 resolved, publish/runtime/source/state mutation, public exposure, runtime rollout, release readiness 선언 없음
- 2026-06-04 `Layer4 Absorption Current Surface Guard`를 추가했다.
  - guard token `UNAUTHORIZED_LAYER4_ABSORPTION_CONFIRMED_CURRENT_SURFACE_CONSUMPTION`
  - hard-fail current surfaces: data, output, tools/build, tools/style/rules, packaged Lua, runtime Data, runtime UI
  - allowed references: docs, staging evidence, tests, historical Round A/B predecessor script
  - validator status `pass`, rejected occurrence count `0`, targeted unittest `5` tests pass, py_compile pass
  - future approved consumer는 별도 successor/correction readpoint로 열어야 하며 current `0` reseal을 조용히 무효화하지 못한다.
- 2026-06-05 `Acquisition Lexical Current Inventory / Readpoint Audit Round`를 `closed_with_followup_suppress_disposition_required`로 닫았다.
  - current checkout 기준 acquisition lexical logical surface `507`, raw occurrence `8828`, classified `507`, `UNCLASSIFIED_BLOCKED 0`
  - writer/import closure residue `0`, protected mutation `0`, current gate surface count `0`
  - suppress current validator surface count `3`; suppress retirement은 실행하지 않고 follow-up disposition 후보로 남긴다.
  - stale suppress-dependent acquisition plans are read as historical/stale premises, not current blockers.
- 2026-06-05 `Acquisition Lexical Current Readpoint Reconciliation Round`를 `closed_with_acquisition_lexical_current_readpoint_reconciled`로 닫았다.
  - 기존 `acquisition lexical input contract 미완` 문제 매핑은 current 기능 구현 미완이 아니라 readpoint reconciliation 문제로 재정의됐다.
  - 선행 Branch D inventory readpoint tuple을 입력으로 잠갔다.
  - reconciliation document universe `508`, document/claim unclassified `0/0`, read-state coverage `100%`
  - blocked ambiguous `0`, current-vs-stale contradiction `0`
  - suppress current blocker `0`, suppress crosswalk violation `0`, live suppress cross-manifest mismatch `0`
  - live suppress validator surface `3`은 current blocker/resolved state가 아니라 `followup_disposition_candidate`로 유지된다.
  - source/rendered/runtime/package/state mutation, suppress retirement/removal, contract expansion, runtime-side repair, rollout/release readiness 선언 없음

## Doing
- 해석/권장/비교 금지 원칙 유지
- 증거 시스템 2트랙과 설명층 독립 원칙 유지
- vanilla-first MVP를 **DVF + Tooltip** 본체 검증 중심으로 유지
- current runtime / user-facing contract를 **three-axis model** 기준으로 읽고, Browser item-entry visibility와 Layer 3 body/source quality를 분리한다.
- Semantic UI Exposure는 닫힌 no-exposure disposition으로 유지한다.
  - `quality_state`는 internal/offline 운영 신호이며 아이템 용도 정보가 아니다.
  - `quality_exposed`는 reserved inactive이고, user-facing copy surface가 없다.
  - Browser / Wiki / Tooltip은 quality 판정을 표시/정렬/필터/숨김/추천/신뢰도 표시로 소비하지 않는다.
- compose default authority를 **`compose_profiles_v2.json + body_plan`** 으로 유지하고, legacy sentence_plan path는 historical/offline tooling fixture로만 남긴다. Exposed legacy adapter entrypoint modes는 removed state로 읽는다.
- future reopen round는 **subset-bounded single-authority sizing rule** 아래에서만 연다
- 외부 모드 확장은 **structure-only / normalization-first** 원칙으로만 검토한다
- Iris refactor 이후 runtime/build contract를 현재 shape로 유지한다.
  - public require contract는 유지한다.
  - runtime JSON parser 도입 없이 Lua facade/chunk 구조를 유지한다.
  - direct protected-call policy는 `IrisProtectedCall`을 통해서만 조정한다.
  - logger/safeRequire module bootstrap은 `Iris/Util/IrisModuleBootstrap.lua`를 통해서만 공통화한다.
  - Layer 3 runtime data는 chunk manifest + chunk files를 deployable authority로 유지하고, active monolith/chunks 동시 배포를 금지한다.

- Resolver cleanup 문제는 `selected_role` removal 문제가 아니며, current readpoint에서는 active correctness debt와 residual final disposition debt가 모두 닫힌 상태로 유지된다.
  - `selected_role` / `selected_role_precedence` / `selected_role_target`: native resolver authority / trace
  - default guard: legacy compatibility mapping이 fallback authority가 되려는 순간 fail-loud
  - diagnostic boundary: explicit diagnostic resolver mode + diagnostic output root guard
  - residual final disposition: legacy compatibility mapping permanent diagnostic-only non-authority fixture, exposed legacy adapter entrypoint modes removed
  - complete-removal / frozen 2105 byte-level recovery: current selected-role cleanup 목표에서 제외
- Silent 21 metadata cleanup debt는 active resolver/adapter debt가 아니라 unadopted source metadata disposition debt였고, 현재 Branch B cleanup closeout으로 닫힌 상태로 읽는다.
  - active 2084 old-profile migration은 closed
  - 이전 `persisted_old_profile_count = 21` deferred inventory는 disposed
  - `Silent 21 Replacement Authority Reconstruction Round`는 `closed_with_replacement_authority_adopted`
  - adopted replacement authority는 silent 21 cleanup 전용이며, original sealed authority 복원 선언으로 읽지 않는다.
  - `Silent Metadata Intake / Cleanup Round`는 adopted replacement authority를 input authority로 소비해 Branch B로 닫힘
  - current cleanup counts: `persisted_old_profile_count = 0`, `silent_old_profile_count = 0`
- Runtime payload enum rename은 current writer/runtime surfaces에서 implemented state로 읽는다.
  - canonical enum은 `adopted / unadopted`
  - `active / silent`는 diagnostic/import/historical read-only alias
  - Lua syntax validation exact command는 pass 상태다.
  - Manual/runtime QA는 release/runtime smoke로 별도 취급하며, enum rename issue closeout의 blocker로 읽지 않는다.
- Generated report / operator label cleanup은 preflight-gated 작업으로 읽는다.
  - current label residue 여부는 repo-wide lexical zero가 아니라 Surface C occurrence disposition으로 판정한다.
  - mutation은 Phase 2 manifest가 target을 봉인한 경우에만 열린다.
  - future builder output guard는 release hardening 후보이며, 현재 no-residue closeout의 blocker가 아니다.
- Static Report Label Cleanup Referent Recovery Round는 Branch D `blocked_missing_original_operator_artifact_referent`로 읽는다.
  - all four discovery lanes는 완료됐지만 original generated report/operator referent는 회수되지 않았다.
  - prior Surface C 3개와 outside-prior current candidates는 historical/diagnostic/metric surfaces로 분리됐다.
  - cleanup 완료나 no-residue 성공으로 읽지 않는다.
- Legacy `active/silent` current-surface risk는 cleanup 문제가 아니라 guard hardening으로 닫힌 상태로 읽는다.
  - `Legacy Active/Silent Current-Surface Guard Round`는 GUARD-A `closed_with_no_current_surface_residue_found_and_guarded`로 닫혔다.
  - current checkout 기준 allowlist 밖 current-label occurrence `0`, unclassified occurrence `0`, validator/test fail-loud guard installed.
  - original artifact cleanup success, repo-wide lexical zero, alias removal, runtime rollout, release readiness 선언은 아니다.
- Current runtime baseline seal은 MIGV-QA Phase 1 identity pre-gate의 input authority로 유지한다.
  - sealed referent는 `current_runtime_hash_manifest.json` sha256 `790b5689097a8856e6213074fda25b723060073206a7ca44bd26d9f6f08c9171`.
  - finding inventories(`publish_state` missing 19, nil `text_ko` 19)는 cleanup trigger가 아니라 finding-aware inventory다.
  - historical staged hash `0390272b...`는 comparison-only readpoint로 유지한다.
- Manual in-game validation closeout은 닫힌 상태로 유지한다.
  - closeout branch: `closed_with_manual_in_game_validation_complete_revised_contract`
  - Browser item-entry visibility는 publish_state visibility와 동일하지 않다.
  - future QA/release hardening이 필요하면 이번 closeout을 되돌리지 않고 별도 release-readiness scope로 연다.
- Structural Signal Current Readpoint Seal Round은 2026-05-28 Branch B reconstructed observer authority, 2026-05-29 scope split seal, 2026-05-29 authority classification seal을 live canonical document surface에 additive로 흡수한 docs-only readpoint로 읽는다.
  - structural signal occurrence는 publish / quality / runtime / Lua bridge / default compose / source-row writer input이 아니다.
  - `FUNCTION_NARROW` residual은 report / preview structural flag only이며 second rollout을 열지 않는다.
  - `ACQ_DOMINANT`는 current-baseline remeasurement 결과 publish candidate가 `0`이며, publish mutation review는 열리지 않는다.
  - 이 readpoint는 structural signal disposition completion, source/rendered/runtime/state mutation, deployment, release/Workshop readiness, `ready_for_release`를 선언하지 않는다.
- `ACQ_DOMINANT Current Baseline Remeasurement`는 measured no-candidate closeout으로 읽는다.
  - current artifact 기준 residual count / surface distribution / authority class baseline이 봉인됐다.
  - `publish_candidate_count = 0`이므로 후속 publish review 없이 닫힌 상태다.
- `Layer4 Boundary Current Corpus Lock`은 closed corpus-lock readpoint로 읽는다.
  - `LAYER4_ABSORPTION_CONFIRMED` measurement corpus membership은 locked manifest 또는 partition 기준으로만 읽는다.
  - historical / diagnostic / report-only / preview-only / staging residue / test fixture surface는 current measurement corpus로 승격하지 않는다.
  - 2026-04-29 Layer4 zero-count는 current count로 직접 승계하지 않는다.
- `Layer4 Confirmed Detector Field Map Seal`은 closed Branch B readpoint로 읽는다.
  - current locked corpus는 confirmed detector가 요구하는 explicit trace-edge field를 제공하지 않는다.
  - target row/item 및 body-slot hint field는 readable이지만 source object -> body slot relation이 없다.
  - confirmed measurement는 current corpus 기준 `not_applicable_under_current_corpus`이며, 이는 count `0`이나 Layer4 resolved가 아니다.
- `Layer4 Trace-Edge Authority Admission`은 closed successor readpoint로 읽는다.
  - explicit trace-edge는 current locked corpus에서 회수되지 않았고, current compose/body_plan generation-time relation sidecar로 생산됐다.
  - admitted artifact는 `current_detector_input` partition에 들어갔다.
  - 이 readpoint는 후속 count measurement opening prerequisite만 닫으며 count 산출이나 resolved claim이 아니다.
- `Layer4 Confirmed Detector Field Map Reseal`은 admitted trace-edge artifact 위의 closed field-map readpoint로 읽는다.
  - canonical field map은 `source_ref / row_id / destination_slot / edge_type`이고 `edge_basis`는 tuple support다.
  - 2026-05-31 Branch B field-map predecessor는 current locked corpus limit으로 보존하며 rewrite하지 않는다.
  - 이 readpoint는 후속 count measurement prerequisite만 닫으며 count 산출이나 resolved claim이 아니다.
- `Layer4 Confirmed Current Count Remeasurement`는 closed measured-positive readpoint로 읽는다.
  - confirmed_count는 `24`이며 detector execution과 row-level qualification으로만 봉인됐다.
  - admitted edge row count `24`는 shape metric으로만 남고, count shortcut이나 generated provenance alone confirmation으로 읽지 않는다.
  - 이 readpoint는 Layer4 resolved, policy redesign, publish review, runtime/source/rendered/state mutation, rollout/release readiness를 선언하지 않는다.
- `Layer4 Confirmed Measurement Canonicalization Boundary Seal`은 closed readpoint-only boundary로 읽는다.
  - confirmed_count `24`는 future Layer4 follow-up input이 될 수 있는 current canonical measurement readpoint only다.
  - 이 boundary는 Layer4 resolved, publish mutation review, runtime/source/rendered/state mutation, Browser/Wiki/Tooltip public exposure, rollout/release readiness를 열지 않는다.
  - validation ceiling은 `docs_governance_boundary_only`이며 protected-surface hash proof는 non-mutation claim support only로 읽는다.
- `Layer4 Current Build Application Target Remeasurement / Zero Reseal Round`는 closed current zero-reseal terminal로 읽는다.
  - current production/build/runtime surface scan에서 `LAYER4_ABSORPTION_CONFIRMED` 적용 경로 `0`을 확인했다.
  - M2 application target count는 `0`으로 봉인됐고, M1 confirmed_count `24`는 M2 target count로 상속되지 않는다.
- `Layer4 Absorption Current Surface Guard`는 이 zero-reseal readpoint의 silent drift를 막는 current guard로 읽는다.
  - source/rendered/runtime/package/build hard-fail surfaces에 승인되지 않은 namespace token이 들어오면 validator가 실패한다.
  - docs/staging/tests/historical predecessor references는 허용 reference다.
- `Acquisition Lexical Current Inventory / Readpoint Audit Round`는 acquisition lexical current source/validator/utility와 historical/staging/diagnostic/test/stale-plan surface를 분리하는 선행 readpoint로 읽는다.
  - 과거 suppress 의존 문구는 current blocker가 아니라 stale/historical premise다.
  - live suppress dependency는 current style-validator surface count `3`의 follow-up disposition 후보로만 남긴다.
- `Acquisition Lexical Current Readpoint Reconciliation Round`는 선행 inventory readpoint 위에서 top-doc closeout, lower/current plan, stale artifact, validator/utility readpoint의 current-vs-historical 읽기 순서를 정렬한 closed readpoint로 읽는다.
  - 따라서 `acquisition lexical input contract 미완`은 현 상태에서 기능 구현 미완으로 추적하지 않는다.
  - live suppress validator surface `3`은 current blocker가 아니며, resolved/retired state도 아니다.
  - future suppress disposition work는 별도 approved plan 없이는 열리지 않는다.

## Next
- `LAYER4_ABSORPTION_CONFIRMED` 이후 publish mutation review, semantic quality interpretation, public-facing exposure, production build-consumer wiring, 또는 Layer4 policy redesign은 별도 approved plan 없이는 열지 않는다.
- Acquisition lexical follow-up은 live suppress validator surface `3`의 disposition 여부를 별도 approved plan으로 열 때만 진행한다. 이 follow-up은 suppress retirement/removal, contract expansion, `josa_adaptive`, phrasebook, array acquisition, runtime-side repair 권한을 자동 상속하지 않는다.
- Iris refactoring v4.1 완료본을 packaging / release-note / commit 단계로 넘길지 별도 scope로 결정한다.
  - package command는 `Iris/tools/package_iris.ps1 -Clean -Zip` 기준으로 검증한다.
  - dirty working tree에서는 의도한 Iris refactor 파일만 stage한다.
- Static Report Label Cleanup Referent Recovery를 다시 열려면 original generated report/operator artifact path, staged artifact, VCS commit/path trace, 또는 regeneration recipe를 새 입력으로 제공해야 한다.
  - 새 referent input 없이 `active/silent` 문자열만으로 cleanup mutation을 열지 않는다.
- Legacy Active/Silent Current-Surface Guard는 닫힌 guard로 유지한다.
  - future reopen은 current authority path에서 새 legacy current-label residue가 발견되거나 hard-fail/allow surface 정의가 실제 current output과 어긋날 때만 별도 scope lock으로 연다.
  - historical/diagnostic/import alias, legacy metric key, test fixture 제거를 reopen 조건으로 삼지 않는다.
- release 전 별도 full manual QA가 필요하면 targeted smoke가 아니라 release checklist로 연다.
  - 현재 확인된 item selection error accumulation regression은 fixed로 읽는다.
- P2 ProtectedCall boundary policy를 열 경우 `engine/ui/data/compat` 라벨별 복구/log/fallback 정책표부터 별도 decision으로 봉인한다.
- P1 build script manifest화를 열 경우 PG-6 script count를 입력으로 별도 manifest scope와 ownership rule을 먼저 정한다.
- Adapter / Diagnostic Compatibility category는 닫힌 상태로 유지한다. Future reopen은 retained mapping default/writer 재진입, hidden adapter dependency, diagnostic fixture loss, selected-role authority redesign, diagnostic resolver retirement, new default legacy surface exposure, 또는 새 deletion/removal decision이 명시될 때만 연다.
- future explicit reopen이 필요할 경우, current frozen authority를 깨지 않는 범위에서만 **isolated inventory reduction / subset-bounded source-expansion reopen / optional quality leak guard hardening** 중 무엇을 열지 별도 scope lock으로 결정
- Walkthrough / 구현 체크리스트 / 검증 절차 문서 간 최신 상태 일치 유지

## Hold
- release readiness / Workshop readiness / B42 readiness / tooltip completion 선언
- historical staged hash `0390272b...`를 current runtime identity gate로 되돌리는 것
- missing `publish_state 19` / nil `text_ko 19` finding inventory를 same-round cleanup trigger로 해석하는 것
- P1/P2를 v4.1 implementation closeout에 묶어서 완료 또는 실패로 해석하는 것
- `IrisLayer3Data.lua` monolith를 active runtime deployable source로 되돌리는 것
- package-only exclusion만으로 T3-C를 닫았다고 해석하는 것
- targeted item-selection smoke fix를 full release QA pass로 확대 해석하는 것
- manual in-game validation closeout을 release readiness 또는 Workshop publish readiness로 확대 해석하는 것
- roadmap closeout을 packaging 완료, release note 작성 완료, git commit 완료 또는 Workshop 배포 완료로 확대 해석하는 것
- `quality_baseline_v4 -> v5` cutover
- `adopted`를 quality-pass proxy로 읽는 해석
- `unadopted`를 `publish_state`나 deletion/suppression으로 읽는 해석
- historical sealed decision body의 `active/silent` 직접 치환
- 별도 새 product decision 없이 `quality_exposed`를 활성화하거나 semantic quality UI exposure를 재개방하는 것
- `Layer4 Trace-Edge Authority Admission`의 generated edge row count를 `LAYER4_ABSORPTION_CONFIRMED` current count, zero-occurrence/positive-occurrence 판정, 또는 Layer4 resolved claim으로 읽는 것
- `runtime_state` reserved slot 추가
- Phase 1 runtime-facing branch 없이 staged Lua hash delta를 허용하는 해석
- implicit legacy fallback 복귀
- compose 외부 repair / runtime-side compose rewrite
- 갈증 vs 배고픔 같은 수치 비교 기반 분류
- “체감상 마시는 것” 같은 의미 기반 재해석
- 설명 생성 단계에서의 문장 재작성/조건부 요약
- 주 소분류 설명을 모든 아이템의 자동 기본 문장으로 되돌리는 접근
- 연관 레시피를 행동 문장 단위로 잘게 쪼개 기본 표시하는 접근
- 예외 아이템 침묵 리스트를 계속 늘려 템플릿 왜곡을 봉합하는 접근
- 이번 이슈를 해결하기 위한 Evidence Table / DSL / pipeline-spec 수정
- `count==1` 같은 집합 판정을 핵심 해법으로 승격하는 접근
- 분류 숨김이나 브라우저 정렬만으로 오분류를 해결하려는 접근
- 우클릭 행동 범위를 이번 Tool 1-A 오분류 이슈의 직접 해법으로 사용하는 접근
- Context Outcome 통합 요청에 대해 **특정 구현안을 우선 채택하는 판정문**으로 응답하는 방식
- Context Outcome 추출을 **단일 경로만 남기는 구조**로 성급히 축소하는 방식
- 이번 로드맵 정리를 이유로 Evidence / DSL / allowlist를 다시 여는 접근
- 런타임 분석·조건부 추론을 Context Outcome 기본 해법으로 승격하는 접근
- `CustomContextMenu` 같은 행동 문자열 / 메뉴 문자열을 읽어 outcome을 자동 생성하는 방식
- 금지 토큰 / 문서 SHA / `smoke_item` 자동 경로 탐지를 Fail-loud 사유로 승격하는 방식
- Fixing / Moveables 역인덱스를 편의상 outcome으로 승격하는 방식
- `equip_back` 같은 개별 outcome 위계를 일반 규칙으로 확장하는 방식
- 입력 스키마 전체나 설명 파이프라인을 이번 문제의 직접 해법으로 갈아엎는 접근
- 전역 기능 동등성 엔진(`equivalence_key`, ItemGroups 등)을 다시 기본 해법으로 되살리는 접근
- 접힌 목록에 `(xN)` 같은 수량 배지/통계 힌트를 기본 노출로 되돌리는 접근
- 우클릭 행동 검증 단계에서 설명문 집필을 동시에 진행하는 접근
- 섭취/장착/레시피/일반 무기 사용을 우클릭 행동 검증 테이블에 다시 섞는 접근
- `우클릭도 결국 행동이니 버리자`거나 반대로 `행동도 직접 아는 시스템으로 가자`는 양극단
- `아이템 자체를 우클릭해야만 인정`하는 좁은 우클릭 행동 정의
- `우클릭 행동`을 Evidence의 canonical 형태처럼 다시 쓰는 표현
- `재료/대상/조합 조건이면 인정`처럼 Right-click source 범위를 다시 느슨하게 넓히는 접근
- 범용 도구 기능 묶음을 Right-click evidence로 되살리는 접근
- `can_scrap_moveables`를 상위 capability 이름만 손봐서 유지하려는 접근
- 결과 상태만 고유하면 Right-click evidence를 통과시킬 수 있다는 접근
- `Tweezers OR SutureNeedleHolder`, `Needle + Thread`, `Gasoline container` 같은 대체/조합/타입 구조를 Right-click evidence로 되살리는 접근
- `Attach/Upgrade` 시스템 메뉴의 내부 선택지를 전용 메뉴 생성과 동일시하는 접근
- Right-click source를 별도 extractor가 아니라 **별도 분류기 / 별도 Rule 엔진**으로 분리하는 접근
- property-based / tag-based / type-based 게이트를 FullType Gate-0 Evidence로 억지 승격하는 접근
- Equip / Use / Passive 효과를 기본 evidence 축으로 끌어올리는 접근
- `can_scrap_moveables`를 현재 형태 그대로 구조 검토 없이 확정하는 접근
- `메뉴 존재 / 메뉴명 / UI 구조`만으로 Right-click evidence 전체를 최종 동결하는 접근
- Right-click evidence를 `전용 메뉴가 뜨는가`만으로 판정하는 바닐라-특화 축소 모델
- 반대로 `행동 가능하면 된다`는 식으로 추천/의미 해석까지 허용해 버리는 느슨한 확장
- 바닐라 5개 capability 축소 구조를 모드 호환성 검토 없이 최종 체계로 확정하는 접근
- `open_canned_food`, `stitch_wound`, `disassemble_electronics` 같은 행동 의미형 outcome을 현재 기본 모델에 다시 넣는 접근
- Lua 스캐너를 Context Outcome main path로 되돌리는 접근
- 레시피 분석만으로 우클릭 행동/기능적 용도 증거를 대체하려는 접근

- selected_role을 removal target 또는 legacy residue로 되돌리는 것
- selected_role influence `0`을 diagnostic-only guard completion condition으로 되돌리는 것
- Diagnostic-only path를 complete-removal frozen baseline debt에 묶는 것
- AI-trace `264 / 642` 값을 별도 supersession decision 없이 historical frozen baseline authority로 승격하는 것
- selected-role non-zero evidence를 cleanup-opening sealed pass로 해석하는 것
- complete-removal cleanup을 current selected-role / resolver guard goal로 되살리는 것
- Diagnostic-only resolver guard closeout을 selected-role cleanup completion 또는 complete-removal success로 확대하는 것
- managed diagnostic-only legacy compatibility mapping을 default authority debt로 되돌려 읽는 것
- exposed legacy adapter entrypoint removal을 runtime/deployed/readiness authority로 확대하는 것
- diagnostic mapping deletion을 별도 deletion decision 없이 current blocker로 승격하는 것
- silent 21 AI-trace inventory를 단독 authority로 승격하는 접근
- shape-only 2084/21 candidate를 replacement authority로 쓰는 접근
- `Silent 21 Replacement Authority Reconstruction Round` 없이 silent-only rewrite를 실행하는 접근
- replacement reconstruction authority를 original historical sealed authority 복원으로 표현하는 접근
- runtime Lua regeneration / deployed closeout / `ready_for_release` 선언

## Backlog
- 모드 시장 확장 시스템
- 내부 `.Iris` 정규화 및 외부 JSON/SQLite 입출력 정책 상세화

# 6. Frame

## 목표

Project Zomboid 모드팩의 상태를 시간축 위에서 **기록·비교·되돌리는 버전 관리 레이어**. 개별 모드 관리자라기보다 **PZ판 git**에 가까운 운영 도구이며, 대상은 모드 하나가 아니라 **팩 상태(pack state)** 다.

## Doing
- 팩 상태(pack state)를 1급 객체로 다루는 방향 고정
- **환경만 다루고 월드/세이브는 제외**하는 범위 유지
- **수동 스냅샷 = 공식 기록 / 자동 스냅샷 = 안전망** 위계 유지
- 자동 저장은 **5/10/30/60분 주기 + 최근 10개 롤링** 원칙 유지
- `변화 없으면 저장 생략` 같은 해석적 스킵을 기본 정책에서 배제
- 원본 설정 보존 + **오버라이드 파일(내 설정)** 구조를 기본으로 유지
- 목록/순서/설정 재구성 + fingerprint 동일성 확인 모델 유지
- 문제 모드 지목·자동 추천·자동 정렬·자동 해결을 하지 않는 비정책 원칙 유지
- UI/용어는 판단보다 **기준점 / 자동 저장 / 달라짐 / 비교 / 되돌리기** 같은 사실+행동 언어를 우선
- 외부 툴화보다 **모드 내부 레이어**로 남기는 메인라인 유지

## Next
- 수동 스냅샷 / 자동 스냅샷 UI 위계 문서화
- baseline / overrides / manifest / fingerprint 최소 스펙 정리
- import 단계 검증 규칙과 복구 화면 UX 정리
- 공개 공유 포맷(ZIP + JSON)과 내부 `.frame` 캐시의 책임 경계 구체화
- `모드 개별 관리`가 아니라 `팩 상태 관리`로 읽히는 용어 체계 정리

## Hold
- 문제 모드 자동 지목
- 자동 추천 / 자동 정렬 / 자동 해결
- Frame 내부 설정 편집기
- 외부 런처/관리자 툴로의 메인라인 전환
- 모드 원본 파일 저장/배포를 통한 완전 복원
- `.frame`을 외부 공개 표준 포맷으로 강제하는 방식

## Backlog
- 첫 화면 / 복구 화면 등 `한 방`이 되는 메인 UX 다듬기
- 공유 UX와 권리/약관/재현성 리스크를 함께 고려한 전달 방식 정리
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

외부 툴이 만든 리소스팩 산출물을 읽어 **최종 적용 상태를 계산·검증·비교·설명**하는 독립 모듈. 리소스 제작 툴이 아니라 **리소스 적용 상태 관리 플랫폼**으로 둔다.

## Doing
- Canvas를 **독립 모듈로만 시작**한다는 기준 유지 (`Canvas로 시작 / 아니면 폐기`)
- 제작 툴 / 정책 도구 / Frame 대체물이 아님을 유지
- Pulse는 기반 capability만 제공하고, Canvas가 인덱싱·최종 상태 계산·충돌 분석·설명 UX를 맡는 경계 유지
- 게임 리소스를 1차 대상으로 하고, 모드 리소스 확장은 후행 축으로 두는 방향 유지
- v1 pain point 3개를 함께 다루되 중심 가치를 **적용 결과/충돌 가시화**에 두는 방향 유지
  - 최종 적용 결과 / 충돌 / 로드 순서 가시성 부족
  - 패킹 / 경로 / 구조 / ID 민감성으로 제작이 쉽게 깨지는 문제
  - 버전 / 서버 / 배포 불일치

## Next
- 최종 적용 상태 계산 모델 정리
- 충돌 분석 / 프리플라이트 검증 / 차이 리포트 최소 기능선 정리
- 입력 / 내부 캐시 / 출력 / 공유 포맷 구체화
- ZIP + JSON(+ .pack) 공개 포맷과 내부 `.canvas` 정규화 캐시의 책임 경계 명시
- 외부 툴 산출물 import → 검증 → 비교 → 설명 워크플로우 초안 작성

## Hold
- 리소스 제작 툴화
- 정책 심판 / 자동 병합 / 정답 추천 / 최적 순서 제시
- Frame과의 통합 설계
- `.canvas`를 외부 공유 표준으로 미는 방향
- 외부 사례 구조를 그대로 이식하는 방식

## Backlog
- 게임 리소스 대상 v1 이후 모드 리소스 확장 전략
- 서버↔클라 / 로컬↔배포 상태 비교 UX 정리
- 리소스팩 상태를 Frame 시간축과 느슨하게 연동할 가치가 있는지 장기 검토
# 9. 플랫폼 브랜딩 / 공개 전략

## 목표

플랫폼을 전면에 내세우기보다 **킬러앱이 먼저 가치를 증명하고, 기반은 뒤늦게 드러나는 구조**를 유지한다.

## Doing
- 최상위 기준은 **`Philosophy.md` 하나**이며, 과거 핸드오버/세션 요약은 작업 문서로만 취급
- `Pulse`를 최우선 브랜드 후보로 유지
- 킬러앱 우선 공개 전략 유지
- `새 Java 로더` 정면 경쟁 프레이밍을 피하고, **결과물 선공개 → 기반 후노출** 구조 유지
- 공개/배포 메시지의 핵심 리스크를 `기능 부족`보다 **플랫폼 오염 방지 / 채택 마찰 제어**로 둠
- Frame은 `PZ판 git` / 상태 기록·복원 레이어라는 정체성을 중심에 둠

## Next
- README / Architecture / 로고 / 모듈 네이밍과의 정합성 점검
- 최적화 모드 공개 순서와 플랫폼 인식 전략의 연결 정리
- 공개 순서를 `Iris → Nerve → Fuse → Pulse+Echo → Nerve+ / Fuse Pulse 의존 전환` 기준으로 문서화
- 설치/실행 마찰 최소화 문서화
  - PulseLauncher 체감 최소화 UX 원칙
  - Steam 실행 옵션 / 바로가기 / 번들 안내 구조
  - 유저가 `추가 플랫폼을 깐다`고 느끼지 않게 만드는 설치 문구
- `Philosophy.md`에는 금지선/역할 경계만 남기고, 기대치 문구는 별도 ReleaseStrategy 문서로 분리 검토

## Hold
- 법적/최종 브랜드 확정 선언
- 플랫폼 선공개 루트
- 자동 인스톨러를 현 단계 기본 해법으로 채택

---

# 10. 검증 / 게이트

## 목표

현재 단계의 의미와 다음 단계 진입 조건을 고정한다.

## Doing
- 최상위 기준은 **`Philosophy.md` 하나**이며, 과거 핸드오버/세션 요약은 작업 문서로만 취급
- S1~S4 싱글 시나리오의 역할 해석 유지
  - S1 = Fuse의 구조적 개입 증명
  - S2 = 스트리밍/이동 경계 비개입 확인
  - S3 = 바닐라 Lua 상시 병목 부정선
  - S4 = 회귀/안정성 게이트
- 멀티 OFF 데이터의 기준선 가치 유지


## Next
- Fuse는 압축형 운영 검증 유지
  - 학술형 대규모 반복 실험보다 재현 가능한 OFF/ON 쌍 검증을 우선
  - 현실적 재현성이 없는 시나리오는 Golden 검증 대상으로 채택하지 않음
  - Scenario A는 종료하고, Scenario B는 스킵, Scenario C는 C-lite와 실전형을 분리해 해석
  - C 실전형 OFF/ON은 반복보다 책임 경계 판별용 종료 게이트로 취급
- S5 중심 MP 검증 단계 진입
- 비공개 테스트에서 폭주 패턴 / 부작용 / 개입 타이밍 검증
- 필요 최소한의 멀티 보조 검증 수행
- MP 튜닝 후 S4 재잠금
- 필요 시 S1 재잠금


## Hold
- 멀티 S1/S2/S4 전면 완주를 필수 과제로 유지
- 현재 빌드 기준 S1~S4 전면 재계측
- MP 데이터 없이 Nerve 세부 동작 확정



---
---

# 11. Consolidated Addendum Ledger

## 성격

이 섹션은 기존 Addendum 본문을 반복 보관하지 않고, **historical trace / provenance index**만 남기는 압축 장부다. 현재 운영 판단은 위의 모듈별 canonical summary를 우선한다.

- 보존 단위: 원본 번호 / 날짜 / 제목 / 핵심 판정 / supersession 관계.
- 제거 단위: 이미 `#5 Iris` 등 상단 summary에 흡수된 Done / Doing / Next / Hold 반복, validation 수치의 반복, release non-claim의 반복.
- 상세 근거: `DECISIONS.md`, 각 round plan/review/closeout, staging 산출물을 따른다.
- 이 ledger는 새 정책을 만들지 않고, 기존 trace가 어떤 canonical 항목으로 흡수됐는지만 가리킨다.

## 11.1 전역 중복 제거 규칙

아래 문구는 개별 addendum마다 반복하지 않고 전역 규칙으로 읽는다.

- 이 문서는 release readiness / Workshop readiness / B42 readiness / deployed closeout / `ready_for_release` 선언이 아니다.
- runtime Lua regeneration, source/rendered/runtime mutation, publish mutation review, adapter removal, alias removal, repo-wide lexical zero는 별도 round가 명시하지 않는 한 선언하지 않는다.
- historical / diagnostic / staging / fixture / import surface는 current writer authority와 분리한다.
- `active/silent`는 current runtime authority가 아니며 current runtime vocabulary는 `adopted/unadopted`다.
- current user-facing surface에서 quality judgment를 badge/copy/sort/filter/hide/recommendation/trust/confidence로 노출하지 않는다.

## 11.2 Absorbed Addendum Provenance Index

| Trace bucket | Preserved original trace | Current absorption |
| --- | --- | --- |
| Iris taxonomy / evidence / interaction pipeline | Original #11~#19. Taxonomy responsibility, static description layer, Right-click evidence-first gate, automatic-only KB, recipe requirements, use_case unification, color layer, evidence/exclusion line split, recipe navigation registry. | `#5 Iris` Done/Hold의 taxonomy, evidence two-track, offline authority, runtime render-only, Layer 4 recipe/navigation contract. |
| Frame / Canvas / ecosystem boundary | Original #20, #21, #25, Inline 2026-04-07, Original #8. Frame as pack-state time-axis manager, Canvas as resource-state manager, Pulse thin platform, public order `Iris → Nerve → Fuse → Pulse/Echo`. | `#6 Frame`, `#8 Canvas`, `#7 Cortex`, `#9 플랫폼 브랜딩 / 공개 전략`, affected module summaries. |
| Iris DVF 3-3 body / acquisition / runtime integration | Original #22~#28, #5-xx, #5-xy, #5-xz, #5-y0, #5-y1. Layer 3 body-only engine, acquisition_hint elevation, QG/DVF split, candidate_state split, second-pass/runtime reflection, style normalization, body-role closure, semantic-quality feedback closure. | `#5 Iris` current runtime baseline, three-axis model, acquisition/source-expansion history, Korean lexical hardening, future subset-bounded reopen rule. |
| 2026-04 authority / source-expansion / compose migration | Original #9~#30. Surface contract authority migration, Korean lexical authority, identity_fallback closeout chain, distribution remeasurement gate, reopen sizing governance, compose authority migration, Phase D/E quarantine and staged rollout, EDPAS, structural observer signal preservation, canonical code-path convergence, adapter/native metadata migration, Layer4 hard block, FUNCTION_NARROW writer authority seal. | `#5 Iris` surface contract, identity_fallback cycle closeout, compose default authority, structural reclassification reporting, metadata migration, Layer 4 boundary, publish_state history. |
| 2026-05 refactor / resolver / runtime / quality | Original #31~#48. Refactor v2.0/v1.4/v4.1 closeouts, frozen 2105 reconstruction blocked path, selected-role bridge gates, diagnostic-only resolver guard, adapter/diagnostic final disposition, active/silent current-surface guard, current runtime baseline seal, MIGV-QA closeout, `quality_exposed` no-exposure disposition. | `#5 Iris` refactor done state, resolver debt split closed state, runtime baseline/MIGV-QA readpoint, quality no-exposure contract. |
| 2026-05-26/27 vocabulary and compose guard | 11.7~11.9. Historical runtime vocabulary anchor, historical/axis-external active mapping, default compose current authority source-path guard. | `#5 Iris` adopted/unadopted authority, historical active/silent non-current anchor, default current compose input root under `Iris/build/description/v2/data/`. |
| 2026-05-27/29 structural signal chain | 11.10~11.14. Current referent inventory blocked missing anchor, Branch B authoritative reconstruction, scope split seal, authority classification seal, docs-only current readpoint absorption. | `#5 Iris` Structural Signal Current Readpoint Seal. Structural occurrences are observer/readpoint signals, not publish/quality/runtime/Lua/default-compose/source-row writer inputs. |
| 2026-05-29 ACQ_DOMINANT mapping | 11.15. `ACQ_DOMINANT` residual remeasurement split from structural readpoint sealing as deferred measurement debt. | Superseded by 2026-05-30 measured no-candidate closeout; retained as predecessor mapping. |
| 2026-05-30 ACQ_DOMINANT remeasurement closeout | `ACQ_DOMINANT` current-baseline remeasurement closed as `closed_with_acq_dominant_current_baseline_sealed_no_publish_candidate`; occurrence_count `1283`; publish_candidate_count `0`. | `#5 Iris` Done/current closed state. No follow-up publish review opened. |
| 2026-05-31 Layer4 boundary current corpus lock | `Layer4 Boundary Current Corpus Lock Round` closed as `closed_with_layer4_boundary_current_corpus_locked_no_count_inheritance_design_preflight`; included corpus `4`; inventory/classification `21914 / 21914`; excluded surface count `460`; unknown/unclassified/excluded_unknown/writer input all `0`. | `#5 Iris` Done/current closed corpus-lock state. Locked manifest/partition is the measurement corpus membership readpoint; prior Layer4 zero-count is historical only. |
| 2026-05-31 Layer4 confirmed detector field-map seal | `Layer4 Confirmed Detector Field Map Seal Round` closed as `closed_with_confirmed_measurement_unavailable_trace_absent`; detector branch `TRACE_EDGE_ABSENT_MEASUREMENT_UNAVAILABLE`; candidate field path count `188`; explicit trace-edge field path count `0`; ambiguous field path count `0`; downstream count disposition `not_applicable_under_current_corpus`. | `#5 Iris` Done/current closed field-map-readiness state. Current locked corpus cannot support confirmed measurement under this readpoint; this is not count `0` and not Layer4 resolved. |
| 2026-06-01 Layer4 trace-edge authority admission | `Layer4 Trace-Edge Authority Admission Round` closed as `EDGE_AUTHORITY_PRODUCED_AND_ADMITTED`; recovery explicit trace-edge candidate count `0`; generated edge artifact rows `24`; admission partition `current_detector_input`; detector readiness dry-run `pass`; `confirmed_measurement_executed false`; `confirmed_count not_computed`. | `#5 Iris` Done/current closed trace-edge authority admission state. This is a prerequisite, not count or Layer4 resolved claim. |
| 2026-06-02 Layer4 confirmed detector field-map reseal | `Layer4 Confirmed Detector Field Map Reseal Round` closed as `closed_with_layer4_confirmed_detector_field_map_resealed`; canonical roles `source_ref / row_id / destination_slot / edge_type`; admitted row count `24` remains shape metric only; `confirmed_count not_computed`. | `#5 Iris` Done/current closed Layer4 field-map reseal state. This is a prerequisite, not count or Layer4 resolved claim. |
| 2026-06-02 Layer4 confirmed current count remeasurement | `Layer4 Confirmed Current Count Remeasurement Round` closed as `closed_with_layer4_confirmed_current_count_measured_positive`; detector executed over `24` admitted rows; confirmed_count `24`; rejected_fallback/ambiguous/unavailable/malformed/out_of_corpus `0/0/0/0/0`. | `#5 Iris` Done/current closed Layer4 confirmed count measurement state. Count is row-level detector qualification, not admitted row count shortcut, and not Layer4 resolved/release readiness. |
| 2026-06-03 Layer4 confirmed measurement canonicalization boundary seal | `Layer4 Confirmed Measurement Canonicalization Boundary Seal Round` closed as `closed_with_layer4_confirmed_measurement_canonicalized_as_readpoint_only`; input_confirmed_count `24`; count_source `sealed_detector_execution`; measurement_readpoint `true`; canonical_resolved_state `false`; validation ceiling `docs_governance_boundary_only`. | `#5 Iris` Done/current closed Layer4 confirmed measurement canonicalization boundary state. Count is a measurement readpoint only; no Layer4 resolved claim, no publish/runtime/source/state mutation, no public exposure, no rollout/release readiness. |
| 2026-06-03 Layer4 boundary namespace reseal | `Layer4 Boundary Namespace Reseal Round` closed as `closed_with_layer4_boundary_namespace_resealed_b3_dual_axis`; selected branch `B3_dual_axis_explicit_seal`; `LAYER4_ABSORPTION_CONFIRMED` is independent `layer_boundary_hard_block_namespace`; `FUNCTION_NARROW / ACQ_DOMINANT` relationships are `separated`; M1 confirmed_count `24` remains measurement readpoint only; M2 basis status is `application_target_measurement_unavailable`. | `#5 Iris` Done/current closed Layer4 boundary namespace reseal state. No Layer4 resolved claim, no publish/runtime/source/state mutation, no public exposure, no rollout/release readiness, no M2 current `0` reseal. |
| 2026-06-03 Layer4 current build application target remeasurement / zero reseal | `Layer4 Current Build Application Target Remeasurement / Zero Reseal Round` closed as `closed_with_layer4_m2_current_build_application_target_zero_resealed`; current production build consumer count `0`; basis_status `available_by_current_surface_absence_scan`; m2 target count `0`; current zero reseal claimed `true`. | `#5 Iris` Done/current closed M2 current zero-reseal state. This is not M2 positive count production, not M1 count inheritance, and not Layer4 resolved/release readiness. |
| 2026-06-04 Layer4 absorption current surface guard | `Layer4 Absorption Current Surface Guard` adopted with reject token `UNAUTHORIZED_LAYER4_ABSORPTION_CONFIRMED_CURRENT_SURFACE_CONSUMPTION`; validator status `pass`; rejected occurrence count `0`; targeted unittest exit code `0`, observed `5` tests; py_compile exit code `0`. | `#5 Iris` Done/current closed Layer4 current-surface guard state. This is a silent-drift guard, not a permanent ban on future approved consumer and not Layer4 resolved/release readiness. |
| 2026-06-05 acquisition lexical current inventory readpoint audit | `Acquisition Lexical Current Inventory / Readpoint Audit Round` closed as `closed_with_followup_suppress_disposition_required`; logical surface `507`; raw occurrence `8828`; classified `507`; blocked `0`; writer/import closure residue `0`; protected mutation `0`; current suppress validator surface count `3`. | `#5 Iris` Done/current acquisition lexical inventory readpoint state. It is a static readpoint and reconciliation prerequisite, not suppress retirement or contract expansion. |
| 2026-06-05 acquisition lexical current readpoint reconciliation | `Acquisition Lexical Current Readpoint Reconciliation Round` closed as `closed_with_acquisition_lexical_current_readpoint_reconciled`; document universe `508`; document/claim unclassified `0/0`; read-state coverage `100%`; blocked ambiguous `0`; current-vs-stale contradiction `0`; suppress current blocker `0`; live suppress validator surface `3` remains follow-up candidate. | `#5 Iris` Done/current acquisition lexical readpoint reconciliation state. It is docs/governance read-order reconciliation only, not suppress retirement/removal, contract expansion, runtime-side repair, source/rendered/runtime/state mutation, or release readiness. |


### Grep-safe current anchors

11.3의 각 상세 trace 항목은 원본 번호/날짜/제목을 grep 가능한 형태로 유지하고, 끝에 `Current anchor:`를 붙여 해당 항목이 흡수된 canonical surface를 직접 추적할 수 있게 한다. `Current anchor`는 새 정책이나 새 판정이 아니라 11.2/11.4의 압축 맵을 항목 단위로 되붙인 추적 표식이다.

## 11.3 Detailed Historical Trace Index

### Iris taxonomy / evidence / interaction pipeline

- **Original #11 — Iris Taxonomy / phase2_rules addendum**: `Evidence 없음 ≠ 기능 없음`; 906 미분류 문제를 Taxonomy/phase2_rules 책임으로 재판정; 9개 대분류와 Furniture / Vehicle / Misc 최소 구조를 Phase 2 기준선으로 닫음 — Current anchor: `#5 Iris` evidence/taxonomy/offline authority/Layer 4 contract.
- **Original #12 — Iris Description writing addendum**: 소분류 설명을 위키형 정적 설명층으로 고정; 번역체/추상어/추천/공략/효율 문구 금지 — Current anchor: `#5 Iris` evidence/taxonomy/offline authority/Layer 4 contract.
- **Original #13 — Iris Right-click Gate-0 v2 evidence-first addendum**: capability-first 폐기; `source_index_v2 → evidence_candidates → evidence_decisions → field_registry_v2` 흐름 채택 — Current anchor: `#5 Iris` evidence/taxonomy/offline authority/Layer 4 contract.
- **Original #14 — Iris automatic-only knowledge-base addendum**: Recipe / Right-click 2트랙 유지; 웹/위키 수동 검증 폐기; runtime은 offline 산출물 표시 전용 — Current anchor: `#5 Iris` evidence/taxonomy/offline authority/Layer 4 contract.
- **Original #15 — Iris recipe requirements display addendum**: `recipe_requirements`를 `recipe_nav_ref`와 분리; runtime Lua는 충족 계산 없이 display render 전용 — Current anchor: `#5 Iris` evidence/taxonomy/offline authority/Layer 4 contract.
- **Original #16 — Iris automatic-only use_case pipeline addendum**: Right-click + Recipe를 `use_case`로 통합; `surface`와 `role=consume|keep` 분리 — Current anchor: `#5 Iris` evidence/taxonomy/offline authority/Layer 4 contract.
- **Original #17 — Iris recipe requirements color layer addendum**: requirement color를 atom 단위 offline `check` 필드로 고정; runtime-side 가능 횟수 계산 배제 — Current anchor: `#5 Iris` evidence/taxonomy/offline authority/Layer 4 contract.
- **Original #18 — Iris right-click capability UI integration addendum**: `line_kind = evidence | exclusion`; Strong/Weak/Exclude는 UI 등급이 아니라 evidence line 내부 판정 — Current anchor: `#5 Iris` evidence/taxonomy/offline authority/Layer 4 contract.
- **Original #19 — Iris recipe interaction wiki layer addendum**: `recipe_nav_registry`, `recipe_requirements_index`, keep/consume role split을 wiki layer 산출물로 편입 — Current anchor: `#5 Iris` evidence/taxonomy/offline authority/Layer 4 contract.

### Frame / Canvas / ecosystem boundary

- **Original #20 — Frame philosophy reconfirmation addendum**: Frame은 save manager나 auto-fixer가 아니라 modpack state time-axis record/compare/rollback layer — Current anchor: affected module summary + `#6 Frame`/`#8 Canvas`/`#9 플랫폼 브랜딩 / 공개 전략`.
- **Original #21 — Canvas philosophy and boundary addendum**: Canvas는 제작 툴이 아니라 resource applied-state manager; Cortex 경유/Frame 통합 출발 금지 — Current anchor: affected module summary + `#6 Frame`/`#8 Canvas`/`#9 플랫폼 브랜딩 / 공개 전략`.
- **Original #25 — Ecosystem moat and peer-module alignment addendum**: Pulse/Iris/Frame/Canvas를 peer module로 정렬 — Current anchor: affected module summary + `#6 Frame`/`#8 Canvas`/`#9 플랫폼 브랜딩 / 공개 전략`.
- **Inline 2026-04-07 — 공개 전략 / 우선순위 재정렬**: Pulse public surface redesign, Echo soft-freeze, Fuse stabilization, Nerve standalone Lua, Iris DVF+Tooltip, B42 별도 포트 축 — Current anchor: affected module summary + `#6 Frame`/`#8 Canvas`/`#9 플랫폼 브랜딩 / 공개 전략`.
- **Original #8 — 2026-04-07 Iris 이후 우선순위 / Pulse 개방 순서 / 인지 전략 재잠금**: 공개/인지 순서 `Iris → Nerve → Fuse → Pulse+Echo → Nerve+/Fuse Pulse 의존 전환`; 플랫폼 선공개 금지 — Current anchor: affected module summary + `#6 Frame`/`#8 Canvas`/`#9 플랫폼 브랜딩 / 공개 전략`.

### Iris DVF 3-3 body / acquisition / runtime integration

- **Original #22 — Iris Layer 3 DVF body-only addendum**: Layer 3 DVF를 body-only automatic 조합 엔진으로 재정의; facts/decisions JSONL 분리 — Current anchor: `#5 Iris` DVF runtime baseline/three-axis/source-expansion/future reopen rule.
- **Original #23 — Iris Layer 3 acquisition_hint elevation addendum**: `acquisition_hint`를 핵심 축으로 승격; 전 아이템 검토와 null reason 도입 — Current anchor: `#5 Iris` DVF runtime baseline/three-axis/source-expansion/future reopen rule.
- **Original #24 — Iris validated knowledge-system addendum**: QG와 DVF를 분리; Layer 3을 item-level mini body layer로 고정 — Current anchor: `#5 Iris` DVF runtime baseline/three-axis/source-expansion/future reopen rule.
- **Original #26 — Iris acquisition coverage closeout and candidate_state split addendum**: DVF body-only 재봉인; tooltip은 current scope 밖; `candidate_state`와 approval 분리 — Current anchor: `#5 Iris` DVF runtime baseline/three-axis/source-expansion/future reopen rule.
- **Original #27 — Iris Phase 3 closeout, approval backlog operations, and DVF 3-3 runtime integration addendum**: Phase 3 / approval backlog / runtime integration readpoint 형성 — Current anchor: `#5 Iris` DVF runtime baseline/three-axis/source-expansion/future reopen rule.
- **Original #28 — Iris ACQ_ONLY surface-form closeout, Layer 3 item-centric reopening, and vanilla-first release posture addendum**: ACQ_ONLY Korean surface closeout; accessibility/in-game exposure moat 재정의 — Current anchor: `#5 Iris` DVF runtime baseline/three-axis/source-expansion/future reopen rule.
- **Original #5-xx — Iris DVF 3-3 post-cleanup integrated roadmap addendum**: weak-active cleanup을 adoption/expansion과 분리; 2-stage status model과 source expansion 운영 축 통합 — Current anchor: `#5 Iris` DVF runtime baseline/three-axis/source-expansion/future reopen rule.
- **Original #5-xy — Iris DVF 3-3 second-pass execution closure addendum**: second-pass/runtime reflection/final snapshot closeout; later `2105 / adopted 2084 / unadopted 21` readpoint의 기반 — Current anchor: `#5 Iris` DVF runtime baseline/three-axis/source-expansion/future reopen rule.
- **Original #5-xz — Iris DVF 3-3 style normalization first operational pass addendum**: style normalization first pass closeout; authority는 second-pass closeout 산출물에 둠 — Current anchor: `#5 Iris` DVF runtime baseline/three-axis/source-expansion/future reopen rule.
- **Original #5-y0 — Iris DVF 3-3 body-role roadmap closure addendum**: body-role policy, boundary, read-only audit, identity_fallback expansion plan closeout — Current anchor: `#5 Iris` DVF runtime baseline/three-axis/source-expansion/future reopen rule.
- **Original #5-y1 — Iris DVF 3-3 problem 2 semantic-quality feedback loop closeout addendum**: semantic-quality feedback loop closed; future reopen은 subset-bounded single-authority rule 적용 — Current anchor: `#5 Iris` DVF runtime baseline/three-axis/source-expansion/future reopen rule.

### 2026-04 Iris authority / migration chain

- **Original #9 — 2026-04-08 surface contract authority migration**: `surface_contract_signal.jsonl`; structural audit/advisory lint 분리; publish writer single-authority 유지 — Current anchor: `#5 Iris` surface contract/compose authority/structural and Layer 4 boundary history.
- **Original #10 — 2026-04-09 acquisition lexical authority and Korean surface hardening**: acquisition lexical chain과 Korean surface hardening authority 봉인 — Current anchor: `#5 Iris` surface contract/compose authority/structural and Layer 4 boundary history.
- **Original #11~#17 — 2026-04-15 to 2026-04-17 identity_fallback closeout chain**: subset rollout / residual hold / closure policy / terminal snapshot / scope policy / completion; terminal aggregate `existing_cluster_absorption 2 / direct_use 8 / policy_review_closed_maintain_identity_fallback_isolation 7`; unresolved/execution lane 0 — Current anchor: `#5 Iris` surface contract/compose authority/structural and Layer 4 boundary history.
- **Original #18 — 2026-04-19 source-expansion distribution remeasurement gate closeout**: comparison baseline과 current handoff authority 2층 closeout — Current anchor: `#5 Iris` surface contract/compose authority/structural and Layer 4 boundary history.
- **Original #19 — 2026-04-20 reopen round sizing governance amendment**: future reopen에 subset-bounded single-authority sizing rule 적용 — Current anchor: `#5 Iris` surface contract/compose authority/structural and Layer 4 boundary history.
- **Original #20 — 2026-04-20 compose authority migration round**: default authority를 body_plan 방향으로 이동시키는 계열 시작 — Current anchor: `#5 Iris` surface contract/compose authority/structural and Layer 4 boundary history.
- **Original #21 — 2026-04-21 body_plan Phase D/E attempt quarantine**: Phase D/E attempt를 non-adopted diagnostic artifact로 격리 — Current anchor: `#5 Iris` surface contract/compose authority/structural and Layer 4 boundary history.
- **Original #22 — 2026-04-22 Phase D/E staged rollout override round**: shipped body_plan authority와 runtime-facing branch 정렬; `ready_for_in_game_validation` readpoint 형성 — Current anchor: `#5 Iris` surface contract/compose authority/structural and Layer 4 boundary history.
- **Original #23 — 2026-04-23 CDPCR-AS Branch B closeout**: branch-level plan/scope/probe evidence를 historical readpoint로 보존 — Current anchor: `#5 Iris` surface contract/compose authority/structural and Layer 4 boundary history.
- **Original #24 — 2026-04-23 EDPAS authority seal closeout**: compose entrypoint authority drift 해결 readpoint — Current anchor: `#5 Iris` surface contract/compose authority/structural and Layer 4 boundary history.
- **Original #25 — 2026-04-24 Phase D observer signal preservation patch round closeout**: observer lane 안에서 source/section signal 보존 — Current anchor: `#5 Iris` surface contract/compose authority/structural and Layer 4 boundary history.
- **Original #26 — 2026-04-24 Structural Reclassification Canonical Code-Path Convergence closeout**: dual-axis canonical model과 plain-name structural path authority — Current anchor: `#5 Iris` surface contract/compose authority/structural and Layer 4 boundary history.
- **Original #27 — 2026-04-25 Adapter / Native Body Plan Readiness closeout**: migration pass criteria와 readiness artifact 형성 — Current anchor: `#5 Iris` surface contract/compose authority/structural and Layer 4 boundary history.
- **Original #28 — 2026-04-25 Adapter / Native Body Plan Metadata Migration closeout**: metadata dry-run hard gate pass; active native profile count와 old-profile residue 제거 계열 authority — Current anchor: `#5 Iris` surface contract/compose authority/structural and Layer 4 boundary history.
- **Original #29 — 2026-04-29 Layer4 Absorption Policy closeout**: Layer4 absorption을 layer boundary hard block으로 봉인 — Current anchor: `#5 Iris` surface contract/compose authority/structural and Layer 4 boundary history.
- **Original #30 — 2026-04-29 FUNCTION_NARROW Disposition Closure and Publish Writer Authority Seal closeout**: publish writer authority와 `internal_only 617` reason inventory 형성; current operation은 later all-item Browser/body-state boundary와 #48 no-exposure disposition을 우선 — Current anchor: `#5 Iris` surface contract/compose authority/structural and Layer 4 boundary history.

### 2026-05 Iris refactor / resolver / runtime / quality chain

- **Original #31 — 2026-05-08 Iris refactor v2.0 closeout and item-selection regression fix**: protected-call boundary, use-case chunk externalization, `IrisDesc` namespace 정리, BOM/item-selection regression fix — Current anchor: `#5 Iris` refactor/resolver/runtime baseline/MIGV-QA/quality no-exposure state.
- **Original #32 — 2026-05-08 Iris final refactoring roadmap v1.4 closeout**: Phase 1~5-9 closeout; `376 tests / OK`; KO runtime smoke success — Current anchor: `#5 Iris` refactor/resolver/runtime baseline/MIGV-QA/quality no-exposure state.
- **Original #33 — 2026-05-12 Iris refactoring roadmap v4.1 closeout**: T0/T1/T2/T3-C closeout; `380 tests / OK`; chunk runtime topology; monolith active runtime path absent — Current anchor: `#5 Iris` refactor/resolver/runtime baseline/MIGV-QA/quality no-exposure state.
- **Original #34 — 2026-05-15 Frozen 2105 Baseline Reconstruction blocked closeout**: diagnostic-only isolation `A1_sufficient`; complete-removal blocked by missing byte-level post-migration 2105 baseline — Current anchor: `#5 Iris` refactor/resolver/runtime baseline/MIGV-QA/quality no-exposure state.
- **Original #35 — 2026-05-15 Selected Role Bridge Impact Seal gate**: diagnostic-only cleanup opening 전 selected-role bridge impact seal 필요 — Current anchor: `#5 Iris` refactor/resolver/runtime baseline/MIGV-QA/quality no-exposure state.
- **Original #36 — 2026-05-16 Selected Role Bridge Impact Seal inconclusive closeout**: sample delta 0이나 authority baseline 부재로 inconclusive — Current anchor: `#5 Iris` refactor/resolver/runtime baseline/MIGV-QA/quality no-exposure state.
- **Original #37 — 2026-05-16 2105 regeneration fallback blocked**: preview `2030 / 75`와 required `2084 / 21` 불일치; shape-only authority rejected — Current anchor: `#5 Iris` refactor/resolver/runtime baseline/MIGV-QA/quality no-exposure state.
- **Original #38 — 2026-05-16 Selected Role Bridge Impact AI-trace non-zero closeout**: selected-role influence non-zero; `264 / 642 / 0` readpoint — Current anchor: `#5 Iris` refactor/resolver/runtime baseline/MIGV-QA/quality no-exposure state.
- **Original #39 — 2026-05-16 Resolver cleanup Branch C selected-role default dependency**: selected-role removal is behavior-changing; no-delta cleanup branch blocked — Current anchor: `#5 Iris` refactor/resolver/runtime baseline/MIGV-QA/quality no-exposure state.
- **Original #40 — 2026-05-17 Resolver cleanup and frozen baseline debt split**: diagnostic-only guard debt와 complete-removal evidence-chain debt 분리 — Current anchor: `#5 Iris` refactor/resolver/runtime baseline/MIGV-QA/quality no-exposure state.
- **Original #41 — 2026-05-17 Selected-role native resolver authority redefinition**: `selected_role`, `selected_role_precedence`, `selected_role_target` adopted as native resolver authority/trace — Current anchor: `#5 Iris` refactor/resolver/runtime baseline/MIGV-QA/quality no-exposure state.
- **Original #42 — 2026-05-17 Diagnostic-only Resolver Compatibility Guard closeout**: default resolver legacy fallback fail-loud; explicit diagnostic mode output-root guarded — Current anchor: `#5 Iris` refactor/resolver/runtime baseline/MIGV-QA/quality no-exposure state.
- **Original #43 — 2026-05-17 Residual resolver compatibility debt redefinition**: active resolver correctness debt closed; remaining adapter/diagnostic disposition is not blocker — Current anchor: `#5 Iris` refactor/resolver/runtime baseline/MIGV-QA/quality no-exposure state.
- **Original #44 — 2026-05-18 Adapter / Diagnostic Compatibility Final Disposition closeout**: mapping retained as permanent diagnostic-only non-authority; exposed legacy adapter entrypoint modes removed — Current anchor: `#5 Iris` refactor/resolver/runtime baseline/MIGV-QA/quality no-exposure state.
- **Original #45 — 2026-05-21 Legacy Active/Silent Current-Surface Guard closeout**: GUARD-A no-current-surface-residue guarded; current-label occurrence 0, unclassified 0 — Current anchor: `#5 Iris` refactor/resolver/runtime baseline/MIGV-QA/quality no-exposure state.
- **Original #46 — 2026-05-23 Current Runtime Baseline Seal closeout**: `2105`, `adopted 2084 / unadopted 21`, monolith absent; missing `publish_state 19` and nil `text_ko 19` are findings, not same-round cleanup triggers — Current anchor: `#5 Iris` refactor/resolver/runtime baseline/MIGV-QA/quality no-exposure state.
- **Original #47 — 2026-05-24 Manual In-Game Validation QA closeout**: default playtest baseline accepted; `Iris/Playtest/` screenshots accepted; all-item Browser item-entry visibility separated from Layer 3 quality — Current anchor: `#5 Iris` refactor/resolver/runtime baseline/MIGV-QA/quality no-exposure state.
- **Original #48 — 2026-05-25 Semantic UI Exposure / quality_exposed no-exposure disposition**: `quality_exposed` reserved inactive; `quality_state` internal/offline only; no quality judgment user-facing copy/sort/filter/recommendation/trust surface — Current anchor: `#5 Iris` refactor/resolver/runtime baseline/MIGV-QA/quality no-exposure state.

### 2026-05-26/29 vocabulary, compose guard, structural signal chain

- **11.7 — 2026-05-26 Historical Runtime Vocabulary Readpoint Anchor**: historical/provenance/diagnostic/import/test `active/silent` anchored as non-current authority; occurrence_count `3968`, authority_relevant `3194`, secondary audit `774`, unknown 0, forbidden current authority 0 — Current anchor: `#5 Iris` adopted/unadopted authority and historical active/silent non-current anchor.
- **11.8 — 2026-05-27 Historical / Axis-External Active Readpoint Mapping**: historical `active` is not a live synonym for current `runtime_state = adopted`; no new execution lane opened — Current anchor: `#5 Iris` adopted/unadopted authority and historical active/silent non-current anchor.
- **11.9 — 2026-05-27 Default Compose Current Authority Source-Path Guard**: default current compose inputs restricted to `Iris/build/description/v2/data/`; fail-loud `DEFAULT_CURRENT_AUTHORITY_INPUT_REJECTED_NON_DATA_SOURCE` — Current anchor: `#5 Iris` default current compose authority source-path guard.
- **11.10 — 2026-05-27 Structural Signal Current Referent Inventory and Anchor Recovery**: closed `blocked_missing_anchor`; expected structural reclassification anchor pair missing; occurrence_count `1297`, candidate_count `68`; next path was restoration or explicit reconstruction — Current anchor: `#5 Iris` Structural Signal Current Readpoint Seal.
- **11.11 — 2026-05-28 Structural Signal Missing Anchor Authority Resolution**: Branch B `closed_with_authoritative_reconstruction_adopted`; current observer-only structural readpoint reconstructed from accepted 2105 chain and current runtime chunk identity; row_count `2105`, adopted/unadopted `2084/21`, forbidden writer fields 0, determinism pass — Current anchor: `#5 Iris` Structural Signal Current Readpoint Seal.
- **11.12 — 2026-05-29 Structural Signal Scope Split Seal**: structural observer/readpoint seal, `ACQ_DOMINANT` remeasurement, publish mutation review, and blanket isolation forbidden maintenance split into separate scope buckets — Current anchor: `#5 Iris` Structural Signal Current Readpoint Seal plus 2026-05-30 closed ACQ_DOMINANT measurement state.
- **11.13 — 2026-05-29 Structural Signal Authority Classification**: occurrence_count `40110`; authority classes `observer_only 15108`, `report_only 21`, `historical 1813`, `diagnostic 22822`, `test 346`; unknown/unclassified/forbidden writer reach/writer misread/mutation candidates all 0 — Current anchor: `#5 Iris` Structural Signal Current Readpoint Seal.
- **11.14 — 2026-05-29 Structural Signal Current Readpoint Seal**: docs-only absorption of reconstructed observer authority + scope split + authority classification into live canonical surface; structural occurrences remain non-writer authority — Current anchor: `#5 Iris` Structural Signal Current Readpoint Seal.
- **11.15 — 2026-05-29 ACQ_DOMINANT Current Baseline Remeasurement mapping**: remeasurement was deferred measurement debt only; this predecessor mapping is superseded by the 2026-05-30 measured no-candidate closeout — Current anchor: `#5 Iris` Done/current closed ACQ_DOMINANT remeasurement state.
- **11.16 — 2026-05-30 ACQ_DOMINANT Current Baseline Remeasurement closeout**: occurrence_count `1283`; authority classes `diagnostic 936`, `historical 236`, `observer_only 94`, `test 17`; `writer_input_count 0`, `forbidden_writer_reach_count 0`, `publish_candidate_count 0`; closeout branch `closed_with_acq_dominant_current_baseline_sealed_no_publish_candidate` — Current anchor: `#5 Iris` Done/current closed ACQ_DOMINANT remeasurement state.
- **11.17 — 2026-05-31 Layer4 Boundary Current Corpus Lock closeout**: current artifact universe and measurement corpus locked before any `LAYER4_ABSORPTION_CONFIRMED` count; included corpus `4`; inventory/classification `21914 / 21914`; excluded surface count `460`; unknown/unclassified/excluded_unknown/writer input all `0`; manifest sha256 `d394f95f5f2a157679238e005a90929349eb807a8180824d8f0ed30240290402`; closeout branch `closed_with_layer4_boundary_current_corpus_locked_no_count_inheritance_design_preflight` — Current anchor: `#5 Iris` Done/current closed Layer4 corpus-lock state.
- **11.18 — 2026-05-31 Layer4 Confirmed Detector Field Map Seal closeout**: confirmed detector field-map readiness sealed as Branch B; current locked corpus lacks explicit Layer4 source object -> Layer3 body slot trace-edge field; candidate field path count `188`; explicit trace-edge field path count `0`; ambiguous field path count `0`; downstream count disposition `not_applicable_under_current_corpus`; closeout branch `closed_with_confirmed_measurement_unavailable_trace_absent` — Current anchor: `#5 Iris` Done/current closed Layer4 field-map-readiness state.
- **11.19 — 2026-06-01 Layer4 Trace-Edge Authority Admission closeout**: trace-edge authority/admission successor readpoint sealed; existing explicit edge recovery count `0`; row-level sidecar produced from current compose/body_plan generation relation; generated edge artifact rows `24`; admission partition `current_detector_input`; detector readiness dry-run `pass`; `confirmed_measurement_executed false`; `confirmed_count not_computed`; closeout branch `EDGE_AUTHORITY_PRODUCED_AND_ADMITTED` — Current anchor: `#5 Iris` Done/current closed Layer4 trace-edge authority admission state.
- **11.20 — 2026-06-02 Layer4 Confirmed Detector Field Map Reseal closeout**: admitted trace-edge artifact field map sealed; canonical roles `source_ref / row_id / destination_slot / edge_type`; `edge_basis` tuple support retained; admitted edge row count `24` remains shape metric only; `confirmed_measurement_executed false`; `confirmed_count not_computed`; closeout branch `closed_with_layer4_confirmed_detector_field_map_resealed` — Current anchor: `#5 Iris` Done/current closed Layer4 field-map reseal state.
- **11.21 — 2026-06-02 Layer4 Confirmed Current Count Remeasurement closeout**: sealed corpus/trace-edge/field-map authorities consumed; detector executed over `24` admitted rows; confirmed_count `24` by row-level qualification; rejected_fallback/ambiguous/unavailable/malformed/out_of_corpus `0/0/0/0/0`; closeout branch `closed_with_layer4_confirmed_current_count_measured_positive` — Current anchor: `#5 Iris` Done/current closed Layer4 confirmed count measurement state.
- **11.22 — 2026-06-03 Layer4 Confirmed Measurement Canonicalization Boundary Seal closeout**: confirmed_count `24` canonicalized as current measurement readpoint only; count_source `sealed_detector_execution`; measurement_readpoint `true`; canonical_resolved_state `false`; validation ceiling `docs_governance_boundary_only`; closeout branch `closed_with_layer4_confirmed_measurement_canonicalized_as_readpoint_only` — Current anchor: `#5 Iris` Done/current closed Layer4 confirmed measurement canonicalization boundary state.
- **11.23 — 2026-06-03 Layer4 Boundary Namespace Reseal closeout**: `LAYER4_ABSORPTION_CONFIRMED` resealed as independent `layer_boundary_hard_block_namespace`; selected branch `B3_dual_axis_explicit_seal`; closeout branch `closed_with_layer4_boundary_namespace_resealed_b3_dual_axis`; relationship to `FUNCTION_NARROW / ACQ_DOMINANT` separated; M1 confirmed_count `24` remains detector-execution measurement readpoint only; M2 basis status `application_target_measurement_unavailable`; validation ceiling `docs_governance_boundary_only` — Current anchor: `#5 Iris` Done/current closed Layer4 boundary namespace reseal state.
- **11.24 — 2026-06-03 Layer4 Current Build Application Target follow-up mapping**: namespace reseal closed separation only; M2 current checkout build application target count remained unsealed until the successor zero-reseal round; no M1 count rewrite, no `FUNCTION_NARROW / ACQ_DOMINANT` reopen, no SUSPECT tier introduction — Current anchor: superseded by 11.25 current zero-reseal closeout.
- **11.25 — 2026-06-03 Layer4 Current Build Application Target Remeasurement / Zero Reseal closeout**: current production build consumer count `0`; basis_status `available_by_current_surface_absence_scan`; zero_reseal_basis `no current production/build/runtime path consumes LAYER4_ABSORPTION_CONFIRMED`; m2 target count `0`; current zero reseal claimed `true`; closeout branch `closed_with_layer4_m2_current_build_application_target_zero_resealed` — Current anchor: `#5 Iris` Done/current closed M2 current zero-reseal state.
- **11.26 — 2026-06-04 Layer4 Absorption Current Surface Guard**: added validator `Iris/build/description/v2/tools/validate_layer4_absorption_current_surface_guard.py` and unittest `Iris/build/description/v2/tests/test_layer4_absorption_current_surface_guard.py`; reject token `UNAUTHORIZED_LAYER4_ABSORPTION_CONFIRMED_CURRENT_SURFACE_CONSUMPTION`; hard-fail current surfaces cover source data, rendered output, build tools, style rules, packaged Lua, runtime Data, and runtime UI; validator status `pass`, rejected occurrence count `0`; targeted unittest `5` tests pass; py_compile passes — Current anchor: `#5 Iris` Done/current closed Layer4 current-surface guard state.
- **11.27 — 2026-06-05 Acquisition Lexical Current Inventory / Readpoint Audit closeout**: closes Branch D `closed_with_followup_suppress_disposition_required`; logical surface `507`; raw occurrence `8828`; classified `507`; blocked `0`; writer/import closure residue `0`; protected mutation `0`; current suppress validator surface count `3`; JSON/JSONL parse and helper py_compile pass — Current anchor: `#5 Iris` Done/current acquisition lexical inventory readpoint state.
- **11.28 — 2026-06-05 Acquisition Lexical Current Readpoint Reconciliation closeout**: closes `closed_with_acquisition_lexical_current_readpoint_reconciled`; consumes 11.27 Branch D as input; reconciliation document universe `508`; document/claim unclassified `0/0`; read-state coverage `100%`; blocked ambiguous `0`; current-vs-stale contradiction `0`; suppress current blocker `0`; suppress crosswalk violation `0`; live suppress cross-manifest mismatch `0`; live suppress validator surface count `3` remains follow-up candidate — Current anchor: `#5 Iris` Done/current acquisition lexical readpoint reconciliation state.

## 11.4 Supersession Map

- Right-click / Recipe / use_case / recipe_requirements addenda → `#5 Iris` evidence two-track, offline authority, runtime render-only, Layer 4 contract.
- DVF 3-3 / acquisition / identity_fallback / body_plan / runtime baseline / quality no-exposure addenda → `#5 Iris` current runtime baseline, compose authority, future reopen rule, MIGV-QA readpoint, quality no-exposure contract.
- Acquisition lexical current inventory / readpoint audit → consumed by 11.28 reconciliation. 11.27 remains the Branch D input readpoint: current acquisition lexical surfaces are classified by authority; stale suppress-dependent plans are historical/stale premises; live suppress dependency is limited to current style-validator surface follow-up. It is not suppress retirement/contract expansion.
- Acquisition lexical current readpoint reconciliation → latest state is 11.28 `closed_with_acquisition_lexical_current_readpoint_reconciled`. Top-doc closeout, lower/current plan, stale artifact, validator, and utility surfaces now read without current/stale contradiction. Live suppress validator surface `3` remains a follow-up disposition candidate, not current blocker/resolved state.
- 2026-04-07 public strategy addenda → `#9 플랫폼 브랜딩 / 공개 전략` and module summaries.
- Frame / Canvas / Cortex addenda → `#6 Frame`, `#8 Canvas`, `#7 Cortex`.
- Resolver / Frozen 2105 chain → latest current state is #44 final disposition plus #45 guard, while #34~#43 remain failed/gate/inconclusive/superseded path history.
- Structural signal chain → latest current state is 11.14 docs-only current readpoint seal, while 11.10 remains missing-anchor predecessor and 11.11~11.13 are consumed authority inputs.
- `ACQ_DOMINANT` → latest current state is 11.16 measured no-candidate closeout; no follow-up publish review opened.
- `LAYER4_ABSORPTION_CONFIRMED` corpus lock / field-map readiness / trace-edge admission / field-map reseal / current count remeasurement → latest current state is 11.21 measured-positive count closeout over the 11.17 locked corpus, 11.18 Branch B field-map-readiness predecessor, 11.19 trace-edge authority admission successor, and 11.20 field-map reseal. confirmed_count is `24` by detector execution; no Layer4 resolved claim, runtime mutation, publish review, rollout, or release readiness opened.
- `LAYER4_ABSORPTION_CONFIRMED` confirmed measurement canonicalization boundary seal → latest boundary state is 11.22 readpoint-only canonicalization over the 11.21 measured-positive closeout. confirmed_count `24` is current measurement readpoint only; no Layer4 resolved claim, runtime/source/state mutation, publish review, public exposure, rollout, or release readiness opened.
- `LAYER4_ABSORPTION_CONFIRMED` boundary namespace reseal → latest namespace placement state is 11.23 dual-axis namespace seal over 11.22. The namespace is independent `layer_boundary_hard_block_namespace`, separated from `FUNCTION_NARROW / ACQ_DOMINANT`; M1 count `24` and M2 application target axis are separate.
- `LAYER4_ABSORPTION_CONFIRMED` current build application target count / guard → latest state is 11.25 current zero-reseal closeout plus 11.26 current-surface guard. Current production/build/runtime surface scan found no application path consuming the namespace, so M2 target count is sealed as `0`; the guard rejects silent re-entry into source/rendered/runtime/package/build surfaces. Do not inherit M1 `24`, do not introduce SUSPECT without separate approval, and use a successor/correction readpoint for any future approved consumer.
