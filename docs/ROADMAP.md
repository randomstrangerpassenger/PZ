# ROADMAP.md

> 상태: 초안 v0.1 + addenda through 2026-04-24  
> 기준일: 2026-04-24  
> 상위 기준: `Philosophy.md`, `DECISIONS.md`  
> 목적: Pulse 생태계의 현재 진행 방향과 다음 게이트를 짧게 고정한다.

---

## 운영 규칙

- 이 문서는 현재 상태와 다음 과제를 보여주는 문서다.
- `왜 그렇게 정해졌는가`는 `DECISIONS.md`에 남긴다.
- 항목 상태는 `Done / Doing / Next / Backlog / Hold` 중심으로 관리한다.
- 본 문서는 구현 세부 로그가 아니라 방향판이다.
- 상단 모듈 섹션은 **current canonical summary** 로 읽고, 날짜가 붙은 addendum 섹션은 **historical trace** 로 읽는다.

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

## Doing
- 해석/권장/비교 금지 원칙 유지
- 증거 시스템 2트랙과 설명층 독립 원칙 유지
- vanilla-first MVP를 **DVF + Tooltip** 본체 검증 중심으로 유지
- current runtime / user-facing contract를 **three-axis model** 기준으로 읽고, blanket `no_ui_exposure`가 아니라 `publish_state` visibility contract로 해석
- compose default authority를 **`compose_profiles_v2.json + body_plan`** 으로 유지하고, legacy sentence_plan path는 explicit compatibility/diagnostic mode로만 제한
- future reopen round는 **subset-bounded single-authority sizing rule** 아래에서만 연다
- 외부 모드 확장은 **structure-only / normalization-first** 원칙으로만 검토한다

## Next
- body_plan default authority가 실제 Project Zomboid runtime 표면에서도 문제없이 보이는지 확인하는 **manual in-game validation QA round**
- 선택적 후속 라운드로서 **v2 resolver legacy label compatibility mapping cleanup** 여부 판단
- future explicit reopen이 필요할 경우, current frozen authority를 깨지 않는 범위에서만 **isolated inventory reduction / quality-exposed review / subset-bounded source-expansion reopen** 중 무엇을 열지 별도 scope lock으로 결정
- Walkthrough / 구현 체크리스트 / 검증 절차 문서 간 최신 상태 일치 유지

## Hold
- deployed closeout / ready_for_release 선언
- manual in-game validation 결과를 확인하기 전의 shipped-closeout 표현
- `quality_baseline_v4 -> v5` cutover
- `adopted`를 quality-pass proxy로 읽는 해석
- `unadopted`를 `publish_state`나 deletion/suppression으로 읽는 해석
- historical sealed decision body의 `active/silent` 직접 치환
- `quality_exposed` 활성화 또는 semantic quality UI exposure
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

# 11. Iris Taxonomy / phase2_rules addendum

## 성격

이번 단계의 핵심은 `Evidence를 더 늘려서 906개 미분류를 줄이는 것`이 아니라, **Iris가 전체 아이템 위키라는 전제 위에서 Phase 2 구조를 최소 형태로 닫는 것**이다. 즉 `Evidence 있는 분할만 남기고, Evidence 없는 분할은 제거한다`가 이번 단계의 설계 원칙이다.

## Done
- `Evidence 없음 ≠ 기능 없음` 원칙 고정
- 미분류 906 문제의 책임 위치를 Evidence / DSL이 아니라 **Taxonomy / phase2_rules**로 재판정
- `게임플레이에 실질적인 도움이 되는 정보`를 **설명 품질 규칙**으로 재해석하고, 포함 범위 규칙으로 쓰지 않기로 확정
- 내부 전용 / 시스템 표현용 아이템만 blocklist 대상으로 두고, Furniture는 범위 안의 대분류로 유지하기로 확정
- Wearable 정의 확장 금지, Resource 쓰레기통화 금지, Storage 10번째 대분류 신설 보류 후 **Tool.Storage** 흡수 방향 정리
- Furniture를 **Furniture.7-A 단일 소분류**로 고정
- Vehicle을 **Vehicle.8-A(Drivetrain) / Vehicle.8-B(Body)** 최소 2분할로 고정
- Misc를 **output-stage fallback 단일 구조(Misc.9-A)** 로 고정
- Tool.Security / Tool.Storage 편입 완료
- Allowlist / 설명 템플릿 / Implementation Plan / Walkthrough 정합 완료
- Storage vs Backpack 중복 0건 확인
- 대분류 9개 축과 경계 규칙을 기준선으로 두고, **Phase 2 구조 설계 자체는 종료**라고 판정

## Doing
- 닫힌 Phase 2 구조에 대한 회귀 감시
- Tool.Storage vs Wearable.6-F 경계 재오염 방지
- Vehicle 8-A / 8-B 수동 오버라이드 유지 검증
- Misc output fallback / blocklist 작동 안정성 유지

## Next
- phase2_rules 구현 유지보수와 회귀 검증
- Tool.Security / Tool.Storage 실제 코드 배정과 후속 정리
- Vehicle 수동 오버라이드 목록 운영
- Misc output fallback / blocklist 회귀 체크
- Furniture / Vehicle / Misc 설명 품질 보강은 구조 변경 없이 진행

## Hold
- Furniture 5분할(Appliance / Seating / Surface / Storage / Fixture) 같은 추가 세분화
- Misc 내부 의미 분류(Toys / Photos / Decoration / Trash 등)
- Vehicle 3분할 이상 과분할(Door / Window / Trunk / Seat 등)
- Misc 폴백을 `rule_executor`에 넣는 접근
- Tool.Storage를 단순 `Type = Container`로 두는 접근
- Container를 Wearable로 흡수하는 접근
- 애매한 잔여군을 Resource에 몰아넣는 접근
- Storage를 10번째 대분류로 바로 고정하는 접근
- `Evidence 없는 기능 아이템은 Iris 밖`이라는 해석


---

# 12. Iris Description writing addendum

## 성격

이번 단계의 핵심은 소분류 설명을 `분류 체계 안내문`이 아니라 **위키형 정적 설명층**으로 고정하는 것이다. 문제의 본체는 구조 확대가 아니라, 설명문이 실제 용도·시스템 정보·적용 범위를 얼마나 자연스럽고 안정적으로 전달하느냐에 있다.

## Done
- 소분류 설명의 역할을 `분류명 재진술`이 아니라 **실제 용도와 시스템 의미 설명**으로 재고정
- 번역체·추상어(`관여한다`, `관련된다`, `다루며`, `특성` 등)를 기본 문체에서 배제
- 바닐라 기준으로 쓰되 모드 확장에도 깨지지 않도록 **기능 중심 일반화** 원칙 고정
- 전투/총기/통신/광원·점화/배낭 등 오해가 쉬운 영역은 필요한 시스템 정보를 설명문에 포함할 수 있다는 기준 고정
- 기타/가구 계열은 구조 세분화보다 **설명 품질 개선**을 우선한다는 방향 확정
- 개별 아이템 설명 작업은 소분류 설명 작업과 분리해 다음 세션으로 넘기기로 확정

## Doing
- 소분류 설명을 짧고 단정한 한국어 위키 문체로 정리
- 추천/전술/효율 평가는 배제하고, 시스템 사실만 필요한 만큼 포함
- 바닐라 특정 대상명/장착 위치에 과도하게 묶인 문장 줄이기

## Next
- 개별 아이템 설명 전용 세션 착수
  - 소분류 설명 동결본을 기준선으로 사용
  - 아이템별 사실성·문체·정보 밀도 규칙 별도 적용
- 차량 소분류명 재검토
  - `구동계` → `주행계` 후보 검토
  - 다른 차량 하위 명칭도 실제 포함 범위 기준으로 재확인
- `Movable` 계열 한국어 명칭 재검토
- 소분류 설명 최종 문체 체크리스트 작성
  - 번역체 금지어
  - 시스템 정보 포함 허용 기준
  - 바닐라/모드 공용 표현 기준

## Hold
- 소분류 설명을 `이 분류는 이런 분류다` 식의 안내문으로 되돌리는 접근
- 추천/공략/효율 문구를 소분류 설명에 섞는 접근
- `쓸모없는 아이템` 같은 의미 기준으로 기타 대분류를 더 쪼개는 접근
- 개별 아이템 설명과 소분류 설명을 한 세션에서 동시에 대량 처리하는 접근

---

# 13. Iris Right-click Gate-0 v2 evidence-first addendum

## 성격

이번 단계의 핵심은 `더 많은 can_* 필드를 고정하는 것`이 아니라, **Gate-0 Right-click 파이프라인을 capability-first에서 evidence-first로 갈아엎는 것**이다. Gate-0는 미리 capability를 선언하고 아이템을 채워 넣는 구조가 아니라, **근거를 모으고(candidate) → 판정(decision) → 그 결과로 필드를 생성(registry)** 하는 구조로 동작해야 한다.

## Done
- 기존 `capability allowlist → source index → capability_by_fulltype` 중심 사고를 폐기하고, `source_index_v2 → evidence_candidates → evidence_decisions → field_registry_v2` 흐름으로 재설계
- 문서 A~F(v2) 책임 재정렬 완료
  - `field_registry_v2`: 필드는 결과로만 생성/갱신
  - `source_index_v2`: source → candidate 추출 규칙
  - `fail_conditions_v2`: 금지 근거 / 비결정성 / 출력 계약 위반만 Fail
  - `resolution_rules_v2`: candidate 병합 → decision → field update
  - `evidence_source_allowlist_v2`: 허용 근거 타입 목록
  - `track_boundaries_v2`: Gate-0 / Recipe / Excluded / REVIEW 라우팅 계약
- Gate-0 Right-click의 판정 순서를 `직접 실행 주체 → 외부 대상 → 지속 상태 변화 → 그 다음 Strong / Weak`로 재고정
- `미매칭 = Evidence 없음`을 금지하고, 기본 해석을 `현재 rule로는 candidate 추출 불가 = scope 밖`으로 고정
- `property_based`를 즉시 NO로 고정하지 않고 REVIEW 격리 상태로 유지
- execution plan rev.3 승인 및 walkthrough 1차 검증(결정성 / 회귀 / 분포) 통과
- 문서 수정 로드맵을 사실상 종료하고, 다음 판단 재료를 실행 결과 분포로 전환

## Doing
- Gate-0 Right-click v2.1 baseline(Run D) 봉인 상태 유지
- 실행 결과의 `scope 밖 / REVIEW / PASS` 분포를 기준으로 잔여 쟁점 정리
- `recipe exclusion` 범위가 Strong 기대 사례(Tin Opener류)와 충돌하는지 재검토
- property_based REVIEW가 실제로 추가 rule 후보인지, 장기 scope 밖인지 사례 축적
- scope 밖 항목을 다른 증거 축과 어떻게 교차할지 운영 규칙 구체화

## Next
- REVIEW 항목의 자동-only 잔류 분포와 후속 규칙 후보 정리
- scope 밖 항목을 Recipe / 다른 자동 증거 축과 교차하는 automatic-only 운영 절차 명문화
- `recipe exclusion`, `positive rule`, `property_based REVIEW` 삼각 충돌 지점 정리
- 실행 결과 분포를 기반으로 다음 rule wave 범위 확정
- 남은 잔여 rule 발굴은 `coverage 실험`과 `baseline 운영 규칙`을 분리한 상태에서 진행

## Hold
- `can_* capability`를 먼저 고정하고 아이템을 끼워 넣는 capability-first 접근
- candidate-only 규칙을 baseline 운영 규칙으로 켜두는 접근
- Moveable prove rule을 baseline pipeline에 편입하는 접근
- scope 밖을 곧바로 Right-click 수동 검증 대상으로 넘기는 접근
- 미매칭 항목을 곧바로 `NO`나 `Evidence 없음`으로 확정하는 접근
- property_based를 자동으로 `NO`로 내리는 접근
- 이름 패턴 / 메뉴 문자열 / DisplayName / 설명문 / 런타임 함수 결과를 근거로 쓰는 접근
- Strong / Weak를 Gate-0 통과 이전에 사용하는 접근



# 14. Iris automatic-only knowledge-base addendum

## 성격

이번 단계의 핵심은 `REVIEW를 사람이 웹/위키로 닫아주는 위키`가 아니라, **오프라인에서 컴파일된 증거/행동/분류 산출물을 런타임 Lua가 재구성해 보여주는 automatic-only 지식베이스**로 Iris를 고정하는 것이다. Right-click 기반 증거도 Recipe의 잔여 필터가 아니라 동급 2트랙 중 하나로 유지한다.

## Done
- Recipe / Right-click을 동급·겹침 허용 2트랙으로 재고정
- TinOpener를 상징 사례로 삼아 `Recipe UI only 제외 / context-menu surfaced recipe 허용` 방향 확인
- 웹/위키 기반 수동 검증 로드맵 폐기
- PASS / NO / REVIEW, Strong / Weak를 automatic-only 결과 상태로 고정
- Q1~Q5, expected_diff / allowed_changes, role_profile_by_rule_id, build_report를 자동-only 공신력 장치로 승격
- Iris를 `오프라인 컴파일러 -> 런타임 뷰어`형 위키로 재해석
- Gate-0 Right-click 자동 확장(candidate-only / prove anchor)의 운영 baseline 채택 종료

## Doing
- v2.1 baseline(Run D) 유지
- REVIEW / scope 밖 / PASS 분포를 자동-only 운영 지표로 관찰
- 현재 하이브리드(일부 런타임 인덱스 build)를 장기적으로 더 순수한 compile-viewer 구조로 내릴 경계 정리
- Recipe / Right-click 겹침 사례가 품질 게이트와 충돌하지 않는지 회귀 감시

## Next
- REVIEW를 수동 승격 버킷이 아니라 `후속 rule 발굴 / 분포 분석` 버킷으로 운영하는 절차 정리
- scope 밖을 다른 자동 증거 축과 교차하는 절차와 우선순위 명문화
- RecipeIndex / MoveablesIndex / FixingIndex 중 런타임 build를 오프라인 산출물로 더 내릴 수 있는지 검토
- 개별 설명 / 툴팁 / 위키 레이어가 automatic-only Evidence 모델 위에 어떻게 얹히는지 정리

## Hold
- 웹/위키 기반 수동 검증 재도입
- Right-click을 `비-Recipe 잔여 필터`로 되돌리는 접근
- 근거 없는 수동 PASS / Strong 조정
- candidate-only / prove anchor를 baseline 운영 규칙으로 되살리는 접근


---

# 15. Iris recipe requirements display addendum

## 성격

이번 단계의 핵심은 `레시피 라인에 요구사항을 보여주자`가 아니라, **소비 방향의 `uc.recipe.*` 라인과 생산 방향의 `rp.recipe.*` 요구사항을 런타임 gsub로 억지 연결하지 않고, 오프라인 피벗 산출물로 닫는 것**이다. 즉 관심사는 UI 한 줄 추가가 아니라 `recipe_nav_ref`와 독립된 requirements 파이프라인을 만드는 데 있다.

## Done
- `recipe_requirements`를 `recipe_nav_ref`와 분리된 독립 필드/산출물로 고정
- `requirements_by_fulltype -> recipe_id pivot -> recipe_requirements_index.<BUILD>` 오프라인 빌드 방향 확정
- 런타임 Lua를 충족 체크 없이 `display` 텍스트 렌더 전용으로 봉인
- kind allowlist(`perk`, `near_item` 등)와 출력 계약을 FAIL-LOUD 빌드 규칙으로 고정
- SHA-suffixed 매핑 실패를 `dangling / suffix-drift` 2종으로 분리하고 base-slug fallback 2단계 검증 방향 확정
- 빈 배열을 런타임 산출물에 무조건 넣지 않고 생략하는 정책 확정
- 설계 v3를 구현 단계 이관 가능 상태로 동결

## Doing
- `req_base_slug_fallback_count`를 추적만 하고 래칫 방향은 보류
- 요구사항 2~3개 이상일 때 레이아웃 과밀 기준과 줄바꿈 정책 정리

## Next
- recipe requirements 인덱스를 실제 빌드 파이프라인과 Lua 렌더 경로에 연결
- kind allowlist 위반 / 출력 계약 위반 / suffix-drift 분포를 초기 구현 런에서 계수해 baseline 수립
- requirements 표시가 recipe navigation 유무와 독립적으로 동작하는지 회귀 검증

## Hold
- 플레이어 충족 여부를 런타임에서 판정하거나 색으로 보조하는 접근
- `recipe_nav_ref` 안에 requirements를 끼워 넣는 접근
- 웹/위키 또는 사람 판정으로 requirements 매핑을 보정하는 접근
- 빈 배열을 Lua 산출물에 강제로 넣는 접근


# 16. Iris automatic-only use_case pipeline addendum

## 성격

이번 단계의 핵심은 기능을 더 붙이는 것이 아니라, **Evidence -> use_case -> Description -> Runtime render** 전체를 automatic-only 파이프라인으로 닫는 것이다. Right-click과 Recipe는 동급 2트랙이며, 설명층도 판정 엔진이 아니라 정적 use_case를 렌더하는 독립 정보층으로 유지한다.

## Done
- Right-click + Recipe를 `use_case` 단위로 통합하고 `surface=context_menu / recipe_ui / both`를 행동 근거 수준에서 정리
- `classification_recipe`를 중심 경로에서 내리고 `rule_id` 중심 `recipe_evidence` 체계로 승격
- keep 재료도 `uc.recipe.*`에 연결하되 `role` 필드로 consumed/keep을 분리
- `by_fulltype = {"rule_ids": [{rule_id, role}, ...]}` 단일 스키마로 고정
- role 분기와 display_text 분화를 오프라인에서 끝내고 Lua는 렌더 전용으로 봉인
- DescriptionGenerator에 use_case / Requirements 블록을 연결하고 Actions와 keep/require를 분리
- `use_case_label_map`을 FAIL-LOUD build contract로 고정
- `dynamic_recipe_expr`를 33 -> 9 -> 5까지 줄이고 잔여 5건을 PERMANENT_REVIEW 정책으로 봉인
- `legacy_count 0 / Q3 exempt 0`까지 정리해 legacy 승격 면제를 닫음

## Doing
- Requirements 블록의 표시 품질과 라벨 치환 수준 정리
- recipe evidence와 rightclick evidence의 Strong/Weak overlay를 어디까지 병행할지 관찰
- compile-viewer 순도를 높이기 위한 남은 런타임 인덱스 정리 범위 확인

## Next
- `recipe_requirements_index`와 `recipe_evidence/use_case` 산출물을 실제 Lua 렌더 경로에서 함께 소비하는 회귀 검증
- Requirements 블록의 `requirement_key` 라벨 치환, 정렬, 줄바꿈 정책 정리
- automatic-only 파이프라인 기준에서 tooltip / 위키 / 브라우저 표면의 use_case 소비 일관성 검증
- RecipeIndex / MoveablesIndex / FixingIndex의 오프라인 이전 가능 범위 재평가

## Hold
- 웹/위키/사람 판정으로 use_case / evidence를 수동 승격하는 접근
- keep/require를 PASS evidence나 Actions 블록에 섞는 접근
- `classification_recipe`를 남긴 채 의미만 덧씌우는 접근
- `dynamic_recipe_expr` 잔여 5건을 추가 정적화로 억지 해결하려는 접근
- legacy 예외를 expected_diff 수동 조정으로 연명시키는 접근



# 17. Iris recipe requirements color layer addendum

## 성격

이번 단계의 핵심은 `레시피 요구사항을 색으로 보이게 하자`가 아니라, **상호작용 탭의 atom 단위 requirement를 오프라인 check 계약 + 런타임 색상 렌더 전용 구조로 닫는 것**이다. 핵심은 `레시피 전체 SAT/UNSAT`가 아니라 `perk / near_item / flag` atom 각각이 어떤 상태인지 드러내는 데 있다.

## Done
- recipe requirements color layer를 **atom 단위 개별 판정**으로 고정
- 레시피 통합 판정(`getNumberOfTimesRecipeCanBeDone`)을 기본 경로에서 제외
- requirement `check` 필드는 Python 오프라인 산출물만 생성/수정 가능하도록 경계 고정
- 지원 kind의 check 누락을 `atoms_without_check = 0` FAIL-LOUD 게이트로 격상
- `near_item`은 `{type, near_token}` 토큰-only 1단계 후 별도 커밋 활성화 구조로 고정
- `evalRequirementColor(check, player)` + 단일 pcall + 호출부 player 주입 패턴 확정
- color layer를 상호작용 탭 전용 레이어로 봉인

## Doing
- 2차 리뷰에서 도출된 수정 체크리스트 6개를 실행계획에 반영
- `near_item`의 엔진 API 시그니처와 fulltype 해소 경로 확인
- `Perks.FromString` vs `Perks[]` fallback 패턴을 구현 시점 확인 대상으로 유지

## Next
- `recipe_requirements_index` 산출물에 kind별 `check` 구조를 실제로 연결
- `keep-only` 16건 전량 검사와 `atoms_without_check` 0 확인
- 색상 레이어가 recipe navigation / use_case / requirements 렌더와 충돌하지 않는지 회귀 검증
- 6개 수정 체크리스트 반영 후 재리뷰로 conditional PASS를 해소

## Hold
- 레시피 이름 라인 자체를 SAT/UNSAT로 색칠하는 통합 판정 레이어
- 웹/위키/사람 판정으로 color layer check를 보정하는 접근
- `near_item` fulltype를 엔진 확인 없이 지금 즉시 확정하는 접근
- Lua가 `check` 구조를 생성/수정/override하거나 `role`을 해석해 문구를 붙이는 접근


# 18. Iris right-click capability UI integration addendum

## 성격

이번 단계의 핵심은 `[우클릭]`을 표면 문자열로 덧붙이는 것이 아니라, **exclusion과 evidence를 구조적으로 분리하고, 능력 기반 use_case만 UI 블록으로 통합하는 것**이다. 문자열 라인, regex 역파싱, 태그 fallback은 버리고 구조 데이터 + automatic-only 렌더 경로를 유지한다.

## Done
- rightclick 채널을 `line_kind = evidence | exclusion`으로 구조 분리
- `Strong / Weak / Exclude`를 evidence 라인 내부의 2차 판정으로 재정의
- 도구명 기반 `uc.action.*`를 능력 중심 use_case ID로 정리 시작
- `[우클릭]` 표면을 문자열 라인이 아니라 `items[] / debug_items[]` 구조화 블록으로 전환
- Python이 `display_text`를 생성하고 Lua는 렌더만 수행하는 경로 확정
- `uc.action.*`에 한정된 registry policy override로 UI 미노출 문제 복구
- `ISUIHandler.toggleUI` override 제거, 독립 버튼/독립 블록 구조 정리
- Q1~Q5 ALL PASS 상태에서 Right-click UI 통합 트랙 종료

## Doing
- Strong / Weak / Exclude 경계가 연관 블록 표시 품질과 충돌하지 않는지 회귀 감시
- 능력 기반 ID 리네이밍이 label map / use_case block / 브라우저 표면과 일관되는지 확인
- override가 정책 예외로만 사용되는지 Q1/Q5 감시 유지

## Next
- fuel / extinguish_fire / attach_weapon_part / stitch 재료류의 Strong/Weak/Exclude 경계 재점검
- 비-action prefix의 label_map fallback 허용 범위 정리
- 능력 기반 ID 체계를 모드 확장 시나리오까지 포함해 안정화
- [우클릭] 블록이 개별 설명/툴팁/브라우저 표면에서 동일 의미로 소비되는지 회귀 검증

## Hold
- rightclick 채널 전체를 우클릭 행동으로 취급하는 접근
- `uc.recipe.*`, `uc.craft.*`를 rightclick evidence prefix에 다시 섞는 접근
- 문자열 라인에 `[우클릭]`을 끼워 넣고 regex로 다시 파싱하는 접근
- 태그 fallback으로 모드 아이템을 억지 흡수하는 접근
- override를 근거 없는 PASS 주입 경로로 쓰는 접근



# 19. Iris recipe interaction wiki layer addendum

## 성격

이번 단계의 핵심은 `레시피 이름을 더 많이 보여주자`가 아니라, **레시피 상호작용 층을 navigation / per-recipe requirements / keep role / atom status display까지 포함한 구조화된 위키 레이어로 닫는 것**이다. 새 정보는 모두 오프라인 계약으로 만들고, 런타임은 fail-soft 렌더만 수행한다.

## Done
- `recipe_nav_registry` 기반 이동 버튼 경로를 오프라인 계약으로 편입
- `recipe_requirements_index`를 recipe 단위 인덱스로 도입해 fulltype 공유 오표시 경로 제거
- keep 재료를 `role=consume|keep`으로 분리해 `uc.recipe.*`에 연결
- 요구사항 색상 레이어를 atom 단위 check 기반으로 허용하고, display/check 분리 구조를 고정
- `recipe_name` 정합성, dangling/suffix-drift, keep_link_count, `atoms_without_check=0` 등을 Q4/Q5 운영 지표로 편입
- 상호작용 층 확장을 `오프라인 FAIL-LOUD + 런타임 FAIL-SOFT` 구조로 봉인

## Doing
- near_item 2단계 활성화 전까지 token-only + 회색 fallback 상태 유지
- keep/consume 역할의 UI 표현 품질과 과밀 레이아웃 기준 정리
- B41/B42 데이터 스코프 차이로 인한 오해 가능성 문구 관리

## Next
- near_item 엔진 API 확인 후 fulltype 해소 + handler 활성화 동시 커밋
- recipe interaction layer가 브라우저/툴팁/상세 위키 표면에서 같은 의미로 소비되는지 회귀 검증
- keep role과 requirement atom 색상 표현을 실제 표면에서 과잉 해석 없이 읽히도록 정리

## Hold
- 레시피 이름 문자열 역파싱으로 navigation/requirements를 붙이는 접근
- fulltype 전체 공유 requirements 배열 재도입
- keep 재료를 비표시 상태로 남기는 접근
- 충족 조건을 이용해 숨김/정렬/추천 UI로 확장하는 접근
- B41 오해를 피하려고 요구사항을 무음 삭제하는 접근

---

# 20. Frame philosophy reconfirmation addendum

## 성격

이번 단계의 Frame 작업은 구현 설계가 아니라 **정체성과 경계 재확인**에 가깝다. 따라서 기능 확장보다 `무엇이 아닌가`를 더 강하게 잠근다.

## Done
- Frame = 모드팩 상태를 시간축 위에서 기록·비교·되돌리는 관리자 레이어라는 해석 재확인
- 세이브 관리자 / 자동 해결기 / 원인 지목 도구 해석 재차 배제
- Pulse는 Frame을 참조하지 않고, Frame은 Pulse capability만 소비하는 Hub & Spoke 경계 재확인

## Next
- 스냅샷 스키마 / 객체 모델 / 상태 비교 UX를 철학과 충돌 없이 설계
- 자동 스냅샷과 수동 스냅샷의 표면 위계 표현 구체화

## Hold
- 세이브 포함형 Frame
- 자동 해결 / 추천 / 범인 지목 기능
- `.frame`을 외부 공개 표준으로 밀어붙이는 접근


---


# 21. Canvas philosophy and boundary addendum

## 성격

이번 단계의 Canvas 작업은 `리소스팩도 할까?`가 아니라, **한다면 어떤 제품 축으로 고정할까**를 닫는 단계에 가깝다. 따라서 기능 수보다 모듈 경계와 pain point 정의를 우선한다.

## Done
- Canvas는 리소스 제작 툴이 아니라 **리소스 적용 상태 관리 플랫폼**이라는 해석 고정
- `Canvas로 시작 / 아니면 폐기` 원칙 고정, Cortex 경유 서술 폐기
- Canvas / Frame 통합 설계 회피 원칙 고정
- 공개 공유 기본값을 ZIP + JSON(+ .pack)으로 두고, `.canvas`는 내부 캐시/정규화 번들 후보로 제한
- pain point 3개(적용 결과 가시화 / 제작 안전 / 배포 불일치) 고정

## Next
- Canvas v1에서 세 pain point를 각각 어디까지 얕게 덮을지 우선순위 정리
- Pulse capability 목록과 Canvas 해석·검증 UX 경계 구체화
- 외부 툴 산출물 기준 import / validation / compare / explain 흐름 초안 작성

## Hold
- Canvas 제작 툴화
- Cortex 임시 수용 후 Canvas 이관
- Frame과의 통합 제품 설계
- `.canvas`를 외부 공개 표준으로 강제하는 방향

---


# 22. Iris Layer 3 DVF body-only addendum

## 성격

이번 단계의 핵심은 3계층 본문을 `수동 완성문 저장소`에서 **구조화된 facts와 decisions를 입력으로 하는 결정론적 본문 조합 엔진**으로 전환하되, current DVF에서 tooltip 책임을 제거하는 것이다. Layer 3 current scope는 `facts -> decisions -> profiles -> rendered`의 automatic-only 본문 생성 경로만 갖고, tooltip은 후속 별도 시스템으로 이관한다.

## Done
- Layer 3 DVF를 본문 전용 automatic-only 조합 엔진으로 재정의
- facts / decisions 분리와 JSONL 채택, `build/description/v2/` 내부 병렬 공존 방향 확정
- sentence_plan 블록 단위 조합 채택, slot_sequence 제거
- v1 connector literal 고정, 블록 내 슬롯 수 상한 3 고정
- 슬롯 값 평문 string 통일 + slot_meta 분리
- 전역 필수는 identity_hint 1개만 유지, required_any와의 겹침 HARD FAIL 고정
- decisions validator가 rendered를 보지 않는 계층 분리 원칙 확정
- 결정론 검증 entries-only SHA / DVF 1회 검증 원칙 확정
- v1 한국어 처리 계약(`조사 완료 슬롯 + postproc 정리만`) 확정
- 죽은 필드 제거(`slot_version`, `decision_version`, `tooltip_extractable`) 확정
- tooltip 관련 스키마/생성기/검증기/테스트를 current DVF scope 밖으로 이관하는 로드맵 확정

## Next
- Phase 0: DVF 본문 전용 범위 재선언 문서 반영
- 스키마 4종(facts / decisions / profiles / rendered) 동결
- `forbidden_patterns.json` 작성
- 프로파일 6개 초안 작성 및 `required_any` 구성 점검
- `postproc_ko.py` 구현 + 단위 테스트
- `compose_layer3_text.py` 구현
- 테스트 아이템 48개(프로파일별 8케이스) 작성
- DVF 검증기 구현
- 기존 수동 본문과 신규 조합 본문 diff 비교
- tooltip 관련 코드/테스트를 `_archive/tooltip_v1/`로 이관

## Hold
- tooltip 후속 별도 시스템 설계 (DVF 산출물 소비 방식 포함)
- `acquisition_hint` 위상 승격 구현 (설계 Rev.3 조건부 통과, 필수 수정 3건 반영 후 착수)
- `josa_adaptive` connector 도입
- 종성 판별/조사 매핑 엔진 실구현
- E단계 1·2계층 경계 검증
- phrasebook_ko.json / ko_particles.json 활성화
- reason_code 배열화


# 23. Iris Layer 3 acquisition_hint elevation addendum

## 성격

이번 단계의 핵심은 `acquisition_hint`를 3계층에서 `있으면 넣는 선택 슬롯`이 아니라 **identity_hint / primary_use와 동급의 핵심 축**으로 승격하되, 스키마 구조는 유지하고 운영 규약·validator·프로파일 순서를 재정의하는 것이다. tooltip 제거 이후의 다음 본체 과제로서, 현재 상태는 **Rev.3 조건부 통과**이며 필수 수정 3건 반영 후 구현 착수 가능 단계다.

## Done
- `acquisition_hint`를 3계층 핵심 축으로 재정의
- 검토 대상을 active 한정이 아니라 전 아이템으로 통일
- `decisions.acquisition_null_reason` 도입 방향 확정
- null 허용 enum을 `UBIQUITOUS_ITEM` / `STANDARDIZATION_IMPOSSIBLE`로 봉인
- JSON Schema는 타입/enum만, cross-file 조건은 validator에서 강제하는 역할 분리 확정
- acquisition은 limitation/processing보다 앞에 둔다는 블록 순서 원칙 확정
- 슬롯 마침표 검증을 `비소수점 마침표 0개` 규칙으로 정밀화
- silent 아이템 facts 부재 시 교차 검증 skip 원칙 확정
- 배열형 acquisition 입력 대신 string + slot_meta 유지 원칙 확정

## Next
- Rev.3 필수 수정 3건 반영
  - `STANDARDIZATION_IMPOSSIBLE` 테스트 샘플 추가
  - `medical_consumable` 4블록 재조정 반영
  - facts 부재 silent의 교차 검증 skip 규칙 명시
- `validate_layer3_decisions.py`에 `acquisition_null_reason` 조건부 필수 구현
- 프로파일별 `required_any` / sentence_plan을 acquisition 격상 기준으로 재점검
- forbidden_patterns를 acquisition 공략화 방지 기준에 맞게 추가 보강
- 실데이터 샘플 검증을 통해 warning false positive 비율 점검

## Hold
- slot_meta 내부 값(mode enum, location_tags 값) 검증 로직
- 정적 데이터에서 장소/방식을 자동 추출하는 acquisition 정규화 입력층
- acquisition 검토 결과를 이용한 active/silent 자동 재판정
- acquisition 커버리지 전수 지표 집계
- acquisition_hint 배열화 및 조사 처리 엔진 연계 논의



# 24. Iris validated knowledge-system addendum

## 성격

이번 단계의 핵심은 Iris를 `좋은 정보 모드`가 아니라 **검증된 지식 생산 시스템**으로 다시 고정하는 것이다. 즉, 오프라인 컴파일된 증거·행동·설명 산출물을 런타임 Lua가 재구성해 보여주는 구조를 생태계 해자의 중심으로 두고, QG / DVF / tooltip / 외부 모드 확장 adapter의 책임을 다시 정렬한다.

## Done
- QG를 `증거 시스템 및 파생 산출물용 운영 검문 체계`로 재정의
- DVF를 `Layer 3 본문 전용 설명 검증 체계`로 재정의
- Layer 3을 한 줄 정의문이 아니라 아이템별 미니 본문층으로 보는 방향 고정
- Layer 2는 더 추상적·압축적인 공통 설명, Layer 4는 더 짧고 탐색형 구조층이라는 상대 역할 재확인
- tooltip을 독립 지식원이 아니라 메뉴 본문의 핵심 추출 요약본으로 재정의
- 모드 확장 구조를 `원본 mod file -> 정규화 adapter/compiler -> Iris 표준 산출물 -> QG/DVF 소비` 순서로 고정
- 여러 모드가 같은 아이템을 수정할 때 `엔진 최종 적용값 기준으로 사실만 표시` 원칙 확정
- Iris 전체 경쟁력을 `기능 묶음`보다 `검증 가능한 지식 생산 파이프라인` 전체에서 찾는 해석으로 전환

## Next
- Layer 3 미니 본문층에 맞는 DVF 조합 규칙 / profile 재조정
- tooltip이 `3-2 / 3-3` 핵심만 추출하는 후처리 계약 정리
- QG / DVF / tooltip / browser 표면 간 데이터 흐름 다이어그램 보강
- 외부 모드 정규화 adapter의 입력 계약(JSON / SQLite / 내부 `.Iris` 캐시) 문서화
- active/silent 실무 판정 세션 재개

## Hold
- 런타임 소형 AI 설명 생성
- QG가 raw mod file을 직접 읽는 구조
- tooltip을 독립 지식원으로 승격하는 방향
- 다중 모드 충돌에서 Iris가 우선순위/정답을 판정하는 방향


# 25. Ecosystem moat and peer-module alignment addendum

## 성격

이번 단계의 핵심은 Pulse 생태계 전체를 `플랫폼 위의 플랫폼들을 품는 구조 해자`로 해석하되, 그 안에서 Frame/Canvas를 다른 하위 모듈보다 특별대우하지 않고 **동등한 하위 모듈**로 다시 정렬하는 것이다.

## Done
- Pulse를 얇은 기반 capability 플랫폼으로 재확인
- Iris를 검증된 지식 생산 시스템으로 재해석
- Frame을 모드팩 상태 관리자, Canvas를 리소스 적용 상태 관리자로 재정렬
- Echo / Fuse / Nerve / Iris / Frame / Canvas가 각자 다른 해자 형태를 갖는다는 정리 유지
- Frame/Canvas를 결과론적으로 중요할 수 있어도 구조적으로는 peer spoke로 본다는 기준 확정

## Next
- Frame v1 객체 모델 / 상태 스키마 압축
- Canvas v1 pain point 우선순위 및 adapter/UX 최소범위 압축
- Pulse capability 목록과 각 spoke가 실제로 소비하는 경계 재점검

## Hold
- Frame/Canvas를 Pulse보다 한 단계 위의 특권 축처럼 서술하는 문장
- 특정 하위 모듈을 `생태계 핵심축`으로 전제하는 위계 해석


# 26. Iris acquisition coverage closeout and candidate_state split addendum

## 성격

이번 단계의 핵심은 `acquisition_hint` 위상 격상 설계를 실제 운영 단계까지 밀어붙여 **전 아이템 획득성 review를 100% 닫는 것**이며, 동시에 그 결과를 이용한 `candidate_state` 재평가는 **다음 Phase 3 세션으로 분리**하는 것이다. 즉 `획득성 검토를 끝내는 일`과 `silent -> active 재판정`을 한 흐름으로 섞지 않는다.

## Done
- current DVF를 Layer 3 본문 전용 엔진으로 재봉인하고 tooltip을 current scope 밖으로 유지
- `acquisition_hint`를 Layer 3 핵심 축으로 승격한 운영 규약 확정
- acquisition coverage staging-first 인프라(`master / review / gate / report`) 구축
- disposition 체계 `UNREVIEWED / ACQ_HINT / ACQ_NULL / SYSTEM_EXCLUDED` 고정
- master / reviewable / system_blocklist 분모 잠금
- acquisition review 전량 완료
  - `closed = 2285 / 2285`
  - `unreviewed = 0`
  - `acquisition_review_completion_pct = 100.0`
  - `ACQ_HINT = 2037`
  - `ACQ_NULL = 42`
  - `SYSTEM_EXCLUDED = 206`
  - `top_remaining_buckets = []`
- Phase 2 목표를 `전 아이템 획득성 검토 닫기`로 달성

## Next
- Phase 3 전용 운영안/판정 규약 세션 시작
- candidate_state 재평가 기준 확정
  - `KEEP_SILENT`
  - `PROMOTE_ACTIVE`
  - `MANUAL_OVERRIDE_CANDIDATE`
- `acquisition_hint 존재 = active 승격 여부` 규칙 검토
- `UBIQUITOUS_ITEM` vs `STANDARDIZATION_IMPOSSIBLE` 재검토 기준 정리
- candidate_state 산출물 / gate / report 설계
- Phase 3 handoff prompt 기준으로 별도 세션 착수

## Hold
- 툴팁 후속 체계 구현
- acquisition 기반 active/silent 자동 재판정
- manual override 확대
- 3계층과 4계층 사이의 정보 경계 재조정
- acquisition 표현 세부 수준(장소/컨테이너/방식) 추가 세분화



# 27. Iris Phase 3 closeout, approval backlog operations, and DVF 3-3 runtime integration addendum

## 성격

이번 단계의 핵심은 세 가지를 동시에 닫는 것이었다.  
첫째, Phase 3를 `approval`과 분리된 `candidate_state` staging 판정으로 끝까지 운영하는 것.  
둘째, Wave 3 manual concentration을 규칙 수정 없이 `NO_RULE_CHANGE_BATCH_REVIEW`와 hotspot/cluster 운영으로 소진하는 것.  
셋째, DVF 3-3을 오프라인 batch 완료에서 멈추지 않고 **실제 Iris 메뉴 소비자 연결까지 포함해 freeze 기준을 다시 잠그는 것**이다.

## Done
- Phase 3의 `candidate_state`를 approval과 분리된 staging 판정 축으로 고정
  - `KEEP_SILENT`
  - `PROMOTE_ACTIVE`
  - `MANUAL_OVERRIDE_CANDIDATE`
- `acquisition review 완료 = active 승격` 자동 등치 해석 폐기
- candidate_state와 approval 단계를 분리한 상태로 Phase 3 closeout 운영
- reviewable universe 100% 평가 완료
- invalid combo 0 유지
- determinism pass 유지
- approval backlog 대응 전략을 `NO_RULE_CHANGE_BATCH_REVIEW`로 확정
- Wave 3 manual concentration을 rule patch가 아니라 hotspot/cluster 운영으로 처리
- hotspot을 JSON 명시 등록 + single source of truth 방식으로 관리
- backlog 수치 출처를 `evidence_decisions.v2.4.json`이 아니라 approval queue / HOLD queue 계열 산출물로 고정
- approval backlog closeout 달성
  - `OPEN / IN_REVIEW` cluster 소멸
  - 잔존 158건은 미해결 backlog가 아니라 정책적 `KEEP_HOLD`
  - `sync-ready complete = YES`
- DVF 3-3 production batch를 demo Layer 3 파일과 분리한 별도 계열로 고정
  - `dvf_3_3_facts`
  - `dvf_3_3_decisions`
  - `dvf_3_3_rendered`
- identity 축 입력을 규칙 기반 자동 생성 + 소수 override 구조로 정리
- DVF 3-3 오프라인 파이프라인 종료
  - 초기 approved subset 1050건
  - 후속 CPR 39 병합으로 1089건 확장
  - `gap_count = 0`
  - DVF 4단계 PASS
  - batch validation PASS
  - second-run determinism PASS
- DVF freeze를 한 차례 재오픈
  - 오프라인 산출 + Lua bridge만으로는 완료가 아니라고 재판정
  - dead hook 성격의 `IrisWikiSections` 경로를 재검토
  - 실제 소비자 `IrisBrowser.lua / IrisWikiPanel.lua` 연결 누락을 수정
  - 메뉴 내 3계층 본문 표시 확인 후에만 진짜 freeze 종료

## Next
- ACQ_ONLY 표면형 수정 이후의 후속 회귀 정리
  - item-centric reopen 기준에서 compose template 후속 수정 범위 재고정
  - 재빌드
  - validator / regression 재검증
- identity_hint 규칙 기반 생성과 override의 균형 재점검
- 3-3과 3-4 경계가 템플릿 수정 후에도 유지되는지 회귀 검증
- tooltip 후속 체계를 DVF와 분리된 다음 단계로 착수
- 모드 확장 시스템을 DVF 소비 레이어와 분리된 ingest/정규화 레이어로 문서화 강화

## Hold
- Phase 2 acquisition review 재오픈
- approval closeout 이후의 candidate_state 재판정 재오픈
- manual 수치 개선을 위한 rule patch
- `NARROW_KEEP_DOWNGRADE` 같은 keep 하향식 수치 정리
- DVF 완전 동결 전 모드 확장 시스템 개발 착수
- tooltip 시스템을 DVF current scope에 재혼합
- 템플릿 비문 문제를 이유로 facts / candidate_state / approval 규약을 다시 흔드는 접근

---

# 28. Iris ACQ_ONLY surface-form closeout, Layer 3 item-centric reopening, and vanilla-first release posture addendum

## 성격

이번 단계의 핵심은 두 층을 분리해서 닫는 것이다.  
첫째, ACQ_ONLY 3-3 본문의 한국어 표면형 문제를 **좁은 compose/template 수정 과제**로 끝내는 것.  
둘째, 그 수정이 끝난 뒤 드러난 더 큰 구조 문제, 즉 **3-3이 파밍 안내문이 아니라 아이템 자기 시점의 용도 본문이어야 한다는 재정의**를 새 과제로 여는 것이다.  
동시에 공개 전략도 다시 정리해, Iris의 첫 승부처를 `위키 대체`가 아니라 **인게임 접근성 / 즉시성 / 낮은 인지 비용**으로 고정하고 첫 공개는 `vanilla-first`로 유지한다.

## Done
- ACQ_ONLY 3-3 한국어 표면형 수정 종료
  - `identity_subject`를 compose-time에 생성
  - postproc 책임을 띄어쓰기 / 문장부호 정리로 제한
  - 조사 정확성 전수 확인
  - `rendered ↔ Lua` 일치 유지
  - 1089건 수량 보존
  - 다른 profile 영향 없음 확인
- 표면형 문제의 원인을 `identity_hint 품질`이 아니라 **명사구를 독립 문장처럼 출력한 결합 방식**으로 진단 완료
- Iris의 해자를 `위키 대체 정확도 총량 경쟁`이 아니라 **게임 안에서 먼저 열리게 만드는 접근성 해자**로 재정의
- 첫 공개 전략을 vanilla-first로 재정리
  - 프좀갤 / 워크숍 초기 공개는 바닐라 중심
  - 모드 확장 시스템은 내부 개발 가능하되 전면 홍보는 후속 단계로 유보

## Doing
- Layer 3-3을 `item-centric body`로 재정의하는 후속 로드맵 정리
- 3-3과 3-4의 경계가 다시 흔들리지 않도록 구조 언어 정리
- 접근성 해자 / vanilla-first 공개 메시지를 README/소개 문안에 반영할 기준 정리

## Next
- `item_subject` 생성 규칙 설계
  - 표시명 그대로 사용 / 정규화 / override 맵의 경계 결정
- 3-3 문장 순서 재설계
  - `item_subject`
  - 용도 / use
  - 아이템 자기 기준 변환·상호작용
  - acquisition(후행)
- 획득 문장을 삭제하지 않고 **항상 포함하되 뒤에 두는** 규약 확정
- 3-3이 3-4를 먹어버리지 않는 회귀 검증 기준 문서화
- 첫 공개 소개 문구를 `위키 대체물`이 아니라 `인게임 실용 정보 / 접근성` 중심으로 정리

## Hold
- Phase 3 재판정 재개
- approval backlog 재오픈
- HOLD / KEEP_SILENT 재분류
- 3-3 표면형 수정 과제를 3-4 구조 변경으로 번지게 하는 접근
- 첫 공개에서 모드 확장 시스템을 전면 기능으로 홍보하는 것
- Iris를 `위키 대체물`로 포지셔닝하는 것
- 모든 외부 모드를 다 지원하겠다고 약속하는 것
- Iris가 다중 모드 충돌의 심판/중재자가 되는 것


---

# 5-xx. Iris DVF 3-3 post-cleanup integrated roadmap addendum

## 성격

이번 addendum의 목적은 기존 Iris DVF 3-3 문서를 갈아엎는 것이 아니라, **weak-active cleanup 이후 열려 있던 post-cleanup integrated roadmap가 실제 runtime 운영 패스까지 어디 닫혔는지**를 현재 방향판에 반영하는 것이다.

## Done
- weak-active cleanup을 **완료된 판정/분류 단계**로 닫고 adoption / expansion과 분리
- `Phase 0` input freeze 완료
  - W-6 aggregate baseline을 후속 단계 authority로 봉인
  - `integrated_facts.post_cleanup_candidate.jsonl`을 candidate-only artifact로 고정
- `Phase 1` 2-stage status model closure 완료
  - 6셀 조합 규칙 closure 완료
  - 5개 핵심 결정 closure 완료
  - `generated::weak 133 / missing::strong 21 / missing::adequate 9 / missing::weak 45 / no_ui_exposure` 운영 계약 고정
- `Phase 2` runtime adoption 완료
  - adoption scope 확정
  - `missing::strong 21` adopt 완료
  - adopt validation `21 / 21 pass`
  - runtime snapshot `2105 rows / active 2051 / silent 54`
- `Phase 2` runtime reflection + 인게임 검증 완료
  - staged Lua가 실제 runtime 경로에 반영됨
  - 인게임 검증 `pass_with_note`
- `Phase 3` backlog `178` exploration / package split / first pass execution 완료
  - `46 promote / residual 132`
- `Phase 3` runtime integration / reflection / 인게임 검증 완료
  - integrated runtime snapshot `2105 rows / active 2060 / silent 45`
  - reflection `deployed_matches_staged = true`
  - 인게임 validation `pass`
- validation 전략을 **absolute gate -> baseline-delta gate** 로 교정
  - introduced hard fail `0`
  - resolved hard fail `36`
  - introduced warn `0`
  - resolved warn `36`

## Doing
- residual backlog `132`를 **second-pass expansion backlog** 로 운용
- residual bucket을 `cluster_absent / cluster_mismatch / net-new cluster 필요 lane` 관점에서 계속 정리
- current runtime contract와 semantic quality contract를 분리해 읽는 기준 유지
- `hold`를 semantic 상태가 아니라 **운영 상태**로 읽는 문서 언어 유지

## Next
- residual backlog `132` second-pass 우선순위 재정리
  - `painting`
  - `music instrument`
  - `multiuse tool`
  - `sports tool`
  - `gardening`
  - `handgun/firearm`
- net-new cluster가 필요한 lane의 패키지 설계와 source-expansion 재개
- `generated::weak 133` 장기 처리 정책 재검토 준비
  - 이번 round에서는 유지
  - future cleanup pressure / UI 정책 변화 시 재검토 가능성만 열어둠
- `missing::adequate 9`의 adopt 여부를 future round 의제로만 보관
- semantic quality UI exposure는 열지 않은 채, runtime contract 운영 안정성부터 계속 유지

## Hold
- weak-active cleanup 재오픈
- 2-stage status model 없는 adoption 선행
- model 이전 backlog 본실행
- backlog `178`이 전부 닫힌 것처럼 서술하는 것
- semantic strong/adequate/weak를 이번 round에서 UI에 바로 노출하는 것
- `integrated_facts.post_cleanup_candidate.jsonl`을 공식 runtime facts처럼 다루는 것

## 현재 읽기 규칙

이번 단계는 다음처럼 읽는다.

- weak-active cleanup은 **끝난 단계**다.
- 2-stage status model은 **설계 예정**이 아니라 **closure 완료 상태**다.
- runtime adoption과 backlog first pass는 **실제 runtime reflection / 인게임 검증까지 끝난 operational 결과**다.
- 현재 미완료 과제는 `모델 정의`가 아니라 **residual backlog 132 second-pass expansion** 이다.


# 5-xy. Iris DVF 3-3 second-pass execution closure addendum

## 성격

이번 addendum의 목적은 residual backlog `132` second pass가 어디까지 실제로 닫혔는지와, 그 이후 남은 일이 무엇인지 현재 방향판에 반영하는 것이다. 이번 round는 `생성 계획`이 아니라 **실제 build/runtime execution** 으로 읽는다.

## Done
- Phase 0~7 execution 완료
  - baseline freeze
  - package/theme split
  - selective net-new
  - late-candidate closure
- second-pass runtime reflection 완료
  - deployed runtime path와 staged Lua hash 일치 확인
  - current runtime path는 `IrisLayer3Data.lua` 최신 반영 상태
- second-pass final snapshot 고정
  - `2105 rows / active 2084 / silent 21`
  - `cluster_summary 1440 / identity_fallback 617 / role_fallback 48`
- residual backlog `132 -> 34` closeout 완료
  - final residual 34는 전부 hold taxonomy와 future promote condition 보유
- final hold taxonomy closure 완료
  - `HOLD_CLUSTER_DESIGN_PENDING 18`
  - `HOLD_DOMAIN_UNCLEAR 13`
  - `HOLD_STRUCTURAL 3`
- second-pass 산출물 루트와 closure artifact 생성 완료
  - `second_pass_final_residual_inventory.json`
  - `second_pass_closure_report.md`
  - `pkg6_tail_disposition.md`
- manual in-game validation `pass_with_note` 기록
  - 브라우저/위키 표면 smoke check 기준 정상 동작 확인
  - current round closeout blocker는 해소됨

## Doing
- second-pass는 더 이상 열린 build backlog가 아니라, **validation note까지 기록된 closed runtime round** 로 운영
- future reopen은 final residual 34 전체가 아니라 `future_promote_condition`이 충족되는 hold subset만 대상으로 한다

## Next
- current round의 즉시 후속 구현은 없음
- 다음 round는 final residual hold inventory 중 조건이 성숙한 소집합만 reopen
- full `pass`가 필요하면 `second_pass_in_game_validation_pack.md` 기준 exhaustive sample logging을 별도 QA round로 수행
- semantic quality UI exposure는 future decision으로 유지

## Hold
- second-pass 전체를 다시 열린 execution queue처럼 취급하는 것
- final residual 34를 `이번 round에서 미완료된 구현`처럼 서술하는 것
- second-pass closure 이후 final residual 34를 즉시 재오픈하는 것
- candidate/runtime 분리 원칙을 무시하고 post-closure patch를 즉흥 반영하는 것


---

# 5-xz. Iris DVF 3-3 style normalization first operational pass addendum

## 성격

이번 addendum의 목적은 second-pass closure 이후 새로 열린 style surface 과제가 어디까지 실제 운영 경로에 반영됐는지 방향판에 기록하는 것이다. 이 round는 **facts/decisions 재판정**이 아니라, `compose` 뒤 `rendered` 앞에서 문체 표면을 정리하는 **post-compose deterministic layer** 를 닫는 단계로 읽는다.

## Done
- style baseline authority를 second-pass closeout 산출물로 고정
  - `active 2084`
  - `cluster_summary 1440 / identity_fallback 617 / role_fallback 48`
- `Phase 0` baseline scan과 rule binding 완료
  - `P-01 겸용 18` -> `G-01` global candidate
  - `P-02A 함께 쓰는 8` -> `F-01` family candidate
  - `P-04 근접 전투 22` / `P-05A 에서 발견된다 607` / `P-06 반복 명사 743` -> lint-only
- family binding key를 `fact_origin + selected_cluster_contains`로 고정
  - `selected_cluster = null`은 `unknown` sentinel로 해석
- normalizer/linter를 production path에 삽입
  - `facts -> decisions -> compose -> normalizer -> style linter -> rendered -> Lua bridge -> runtime`
  - `manual_override_text_ko`는 `style rules skip + legacy postproc only`
- `Phase 1` first rule activation 완료
  - `G-01`, `F-01` 활성화
  - active-rules dry run 변경 `18`건
  - applied rule counts `G-01 18 / F-01 8`
  - introduced hard fail `0`
  - introduced warn `0`
- normalized sprint7 baseline 재실행에서는 active-rules dry run `0 changed`로 멱등성 유지 확인
- postproc 흡수 검증 완료
  - `style rules off + legacy postproc only` 경로에서 byte-identical pass
- `Phase 2` advisory lint activation 완료
  - `L-01`, `L-02`, `L-04` 활성화
  - style linter는 별도 `style_lint_report.json`만 생성
  - baseline-delta gate와 분리 유지
- `Phase 6` first triage pass 완료
  - `L-02` repeated noun 구현을 `문장 전체`가 아니라 `문장 내 반복` 기준으로 교정
  - `Base.IronIngot` `metalwork_anvil` 문구를 `다른 금속 부품` -> `다른 부품`으로 조정해 마지막 `primary_use` 반복 1건 제거
  - `L-02` exact acquisition phrase exception(`장신구 취급 장소와 장신구 보관 장소, 채집으로 구할 수 있다`)을 `L-02`에 추가해 `seed_label_repeat` family 68건을 suppress
  - remaining `seed_discovery_phrase_with_label_repeat` family 36개도 exact acquisition phrase exception으로 정리해 `L-02` hit `657 -> 166 -> 98 -> 0`, `warn_row_count 922 -> 675 -> 607 -> 607`
  - `L-02` acquisition label repeat `166`건은 현재 exact exception으로 suppress되고, active dry run 기준 residual hit는 `0`
  - `L-04` `607`건은 전부 seed `acquisition_hint`였고, simple discovery shape exception(`^[^,]+에서 발견된다$`)을 적용해 `430`건 suppress 후 residual match `177`건, batch threshold `15%` 아래(`8.5%`)로 하향
  - triage 결과 `L-01 = ACCEPT`, `L-02 = ACCEPT`, `L-04 = ACCEPT`
  - `style_lint_sample_review.json/.md`를 추가해 lint dry run 수동 샘플 검토 기준을 `min(total_warn_rows, max(30, ceil(total_warn_rows * 0.1)))` + triggered rule당 최소 5건 + `item_id` dedupe로 고정
  - current baseline `warn_row_count = 0` 상태에서는 sample review `0 rows`가 정상으로 기록됨
  - `style_closeout_packet.json/.md`를 추가해 summary artifact inline / raw log reference-only 정책으로 current baseline closeout packet을 생성
  - `style_runtime_closeout.json/.md`를 추가해 full rendered authority 기준 `Lua bridge -> runtime` static closeout을 기록
  - `output/dvf_3_3_rendered.json`은 fixture로 유지하고, runtime authority는 `sprint7_overlay_preview.rendered.json`으로 명시
  - current deployed `IrisLayer3Data.lua`와 staged style runtime export hash 일치 확인
  - `style_runtime_in_game_validation_result.json/.md`를 추가해 in-game browser/wiki/context-menu 검증 `pass`를 기록
  - style runtime closeout을 `runtime_closed_pass`로 승격
  - `phase6_triage_summary.json/.md` 생성
  - `phase6_acquisition_phrase_breakdown.json/.md`는 current active WARN 기준 `0 phrase`로 닫힘
  - acquisition phrase family `214`개를 `seed_label_repeat 1 / seed_discovery_phrase 177 / seed_discovery_phrase_with_label_repeat 36`로 분해한 뒤, current active backlog를 `213` family 전량 `seed_discovery_phrase`로 수렴

## Doing
- style lint pressure를 facts/decisions 재오픈 신호가 아니라 **compose/style backlog** 로 읽는 운영 기준 유지
- `L-02`, `L-04` 경고를 즉시 hard gate로 승격하지 않고 advisory-only로 관리
- zero-hit hold 규칙(`G-03`, `G-04`, `G-05` 등)은 baseline hit가 생기기 전까지 비활성 상태 유지
- `L-02`, `L-04`는 current baseline에서 dormant regression sensor로 유지

## Next
- future hit가 생기면 `L-04` multi-source discovery phrase와 `G-03`, `G-04`, `G-05`, `L-03`, `N-01`, `N-02`, `N-03`를 다시 평가

## Hold
- style surface 문제를 이유로 facts / evidence / cluster 판정을 다시 여는 것
- style linter를 baseline-delta gate나 runtime gate로 승격하는 것
- `fact_origin + selected_cluster_contains` 밖의 새 semantic family 축을 만드는 것
- manual override 문장에 lexical replacement를 강제 적용하는 것


---

# 5-y0. Iris DVF 3-3 body-role roadmap closure addendum

## 성격

이번 addendum의 목적은 style normalization 이후 새로 열린 body-role round가 어디까지 실제 구현과 검증으로 닫혔는지 방향판에 반영하는 것이다. 이 round는 **facts 재판정**이 아니라, 3-3을 authoritative wiki body로 읽히게 만드는 `policy -> audit -> overlay -> compose repair -> lint feedback -> regression -> runtime/in-game closeout` 경로를 닫는 단계다.

## Done
- `Phase 0` body-role policy / boundary 문서 재봉인 완료
  - `dvf_3_3_body_role_policy.md`
  - `3_3_vs_3_4_boundary_examples.md`
- `Phase 1` read-only audit 완료
  - full audit `2105 rows`
  - `item_centric 1440 / function_locked 48 / identity_echo 617`
- `Phase 5` identity_fallback expansion plan 완료
  - `617 rows`
  - `bucket_1 11 / bucket_2 599 / bucket_3 7`
- `Phase 2` decisions overlay / validator / agreement 완료
  - `layer3_role_check`
  - `representative_slot`
  - `body_slot_hints`
  - `representative_slot_override`
  - agreement rate `1.0`
- `Phase 3` compose 내부 repair 경로 반영 완료
  - facts 슬롯 확장 없음
  - compose 외부 repair 단계 없음
  - `quality_flag`는 rendered 진단 메타데이터로만 사용
  - Lua bridge는 `quality_flag`를 소비하지 않음
- `Phase 4` structural lint feedback 경로 완료
  - `LAYER4_ABSORPTION` hard block 유지
  - `BODY_LACKS_ITEM_SPECIFIC_USE 617`
  - `SINGLE_FUNCTION_LOCK 27`
  - feedback은 fresh recompute 원칙으로 next-build 입력만 생성
- `Phase 6` semantic linkage report 완료
  - semantic axis auto update 없음
  - candidate는 future decision 입력으로만 유지
- `Phase 7` full preview / golden subset / regression closeout 완료
  - rendered `2105 rows`
  - introduced hard fail `0`
  - regression rejected `0`
  - golden subset `100`
  - golden changed `0`
- `Phase 8` regression pack / manual override policy 완료
- `Phase 9` closeout 문서와 in-game validation artifact 완료
  - browser/wiki/context-menu 기준 `pass`
- `SAPR` semantic weak carry policy closeout 완료
  - `structural feedback weak candidate` / `source-expansion post-round new weak`는 candidate-only explicit gate로 봉인
  - `quality_baseline_v4` 유지, current `v5` cutover 없음

## Doing
- current body-role round는 **closed operational pass** 로 유지
- `IDENTITY_ONLY` / `FUNCTION_NARROW`는 observer-only weak family로 유지하고, structural feedback / post-round new weak는 candidate-only explicit gate로 유지
- full preview authority를 fixture와 분리해서 읽는 기준 유지

## Next
- `identity_fallback 617` source expansion 실행
  - `bucket_1_existing_cluster_reusable 11`
  - `bucket_2_net_new_cluster_required 599`
- source expansion 이후 audit / overlay / lint 분포 재측정
- net-new cluster 설계가 필요한 lane부터 reopen subset 운영

## Hold
- facts 슬롯 확장
- compose 외부 repair stage 재도입
- `surface_quality / surface_active / runtime_only` 신규 상태 축 도입
- structural feedback을 같은 빌드에서 즉시 re-compose로 되감는 것
- 3-3 본문 문제를 이유로 3-4 상세를 흡수하는 것

## 현재 읽기 규칙

이번 단계는 다음처럼 읽는다.

- body-role roadmap은 **완료된 round** 다.
- 현재 빌드의 실제 수정 경로는 `Phase 2/3` 이다.
- `Phase 4/6`은 **진단·피드백 경로** 다.
- 남은 일은 body-role execution 자체가 아니라 **source expansion과 future semantic decision** 이다.
- 후속 compose authority migration addendum이 열리더라도, 그것은 body-role closure addendum의 재오픈이 아니다. 같은 3-3 layer의 authority migration을 **별도 lane** 에서 다룬다.


---

# 5-y1. Iris DVF 3-3 problem 2 semantic-quality feedback loop closeout addendum

## 성격

이번 addendum의 목적은 body-role closeout 이후 열린 problem 2 round가 어디까지 실제 구현과 검증으로 닫혔는지 현재 방향판에 반영하는 것이다. 이 round는 active 의미를 곧바로 재정의하는 단계가 아니라, **`active = runtime-adopted` baseline 위에 semantic-quality feedback loop를 올리는 운영 round** 로 읽는다.

## Done
- 출발점 고정 완료
  - `active`는 current runtime에서 quality-pass가 아니라 `runtime-adopted`
  - active/silent 외부 계약, Lua bridge, facts 슬롯, `no_ui_exposure` 유지
- Phase A 완료
  - active quality audit 완료
  - `active 2084 / semantic strong 1316 / adequate 0 / weak 768`
  - `generated::weak 133`와 body-role diagnostic 교차 분석 완료
  - `strong + FUNCTION_NARROW protected 20` 고정
- Phase B 완료
  - `semantic_quality`를 decisions overlay의 derived/cache field로 반영
  - validator drift hard fail 반영
  - compose가 `strong + FUNCTION_NARROW` representative repair, `weak + IDENTITY_ONLY/FUNCTION_NARROW/ACQ_DOMINANT` requeue/repair를 소비
- Phase C 완료
  - `quality_tracking_report.json` 자동 생성
  - `compose_requeue_candidates.jsonl` 자동 생성
  - `quality baseline v1` 동결
  - `quality_ratio 0.6315`
  - requeue `624`
  - `no_ui_exposure` 재검토 의제 등록
- Phase D 입력 산출물 생성 완료
  - `active_semantics_redefinition_simulation.json`
  - `phase_d_readiness_report.json`
  - `phase_d_gate_threshold_proposal.json`
- `quality_ratio` 2회 연속 동일 build 관측 완료
  - sustained gate `pass`
- 전체 회귀 검증 완료
  - full preview regression `0`
  - 전체 tests `197 pass`

- three-axis contract migration round의 Phase 1 완료
  - `requeue tolerability` threshold 채택
  - `lane stability` threshold 채택
  - current execution path `B-path` 고정
- `identity_fallback 617` explicit policy-isolation lane 관리 반영
  - `identity_fallback_policy_isolation_report.json`
  - `quality_baseline_v2_partial.json`
  - `quality_baseline_v2_partial_global_reference_delta.json`
- path-aware Phase D reopen 완료
  - iteration 2 기준 path-aware 5-gate 전부 `pass`
  - selected migration scenario = `Scenario X`
- `Phase 3A` guardrail seal 완료
  - post-compose `quality/publish decision stage` legality 봉인
  - single writer / validator drift-checker-only 봉인
  - `quality_state fail` reserved 봉인
  - `internal_only` bridge-preserved semantics 봉인
- `Phase 4` contract spec closeout 완료
  - `quality_state_ownership_spec.md`
  - `publish_state_spec.md`
  - `lua_bridge_publish_state_contract.md`
  - `philosophy_constitutionality_check.md`
- `Phase 5` bridge/runtime contract migration closeout 완료
  - `export_dvf_3_3_lua_bridge.py`가 `publish_state` merge 지원
  - deployed `IrisLayer3Data.lua`에 `publish_state` 반영
  - `layer3_renderer.lua`가 `internal_only` default surface suppression 지원
  - `quality_publish_decision_preview_validation_report.json = pass`
  - `quality_publish_runtime_report.json = ready_for_in_game_validation`
  - `quality_baseline_v3.json = quality_baseline_v3_frozen`
- `Phase 6` manual in-game validation 완료
  - `in_game_validation_result.json/.md = pass`
  - Browser/Wiki default surface `internal_only` suppression pass
  - `exposed` body render pass
  - context menu / other layer / perf regression pass
  - loose ammo right-click compatibility pass (`.223 탄약 / .308 탄약 / 9mm 탄약 / 산탄총 탄약`)
  - current full tests `203 pass`
- `Phase 7` closeout sync 완료
  - `DECISIONS.md / ARCHITECTURE.md / ROADMAP.md` current state 반영

## Doing
- current DVF 3-3 운영 계약은 three-axis post-migration model로 유지
  - `runtime_state = active / silent`
  - `active`는 runtime-adopted만 뜻하고 quality-pass를 암시하지 않음
  - post-migration `semantic_quality` 또는 `quality_state`는 offline authoritative contract로 유지
  - `publish_state = internal_only / exposed`가 current user-facing visibility contract로 동작
- `identity_fallback 617`은 current cycle에서 `internal_only` policy-isolation inventory로 남아 있음
  - row 삭제나 silent loss가 아니라 runtime-preserved backlog로 관리
- non-isolated lane expansion과 net-new cluster 설계는 계속 축적
  - current cycle의 reopen blocker가 아니라 post-migration quality improvement work로 읽음

## Next
- `identity_fallback` source expansion과 net-new cluster 설계 계속 진행
- non-isolated lane quality improvement는 current publish contract를 흔들지 않는 범위에서 축적
- `quality_exposed`는 별도 future round로만 검토

## Hold
- active/silent 외부 계약 선변경
- `semantic_quality`를 runtime state 축으로 다시 해석하는 것
- `publish_state = internal_only` row를 bridge/runtime artifact에서 제거하는 것
- `fact_origin`을 quality proxy로 읽히게 하는 surface 추가
- `quality_exposed`나 interpretive quality badge를 이번 round에 같이 여는 것

## 현재 읽기 규칙

이번 단계는 다음처럼 읽는다.

- problem 2 round의 직접 목표였던 **active 내부 품질 feedback loop 구축** 은 historical closeout으로 유지된다.
- old problem 2 Phase D는 threshold adoption 이전에는 자동 개방되지 않았고 실제로 closed였다.
- current cycle은 그 위에서 별도 **three-axis contract migration round** 로 열렸고, `B-path -> Phase D reopen -> Phase 3A seal -> contract spec -> bridge/runtime migration -> in-game validation pass` 순서로 닫혔다.
- current runtime/user-facing contract는 이제 blanket `no_ui_exposure`가 아니라 `publish_state` visibility contract로 읽는다.
- current 남은 일은 contract migration 미완료가 아니라, **isolated inventory reduction과 future `quality_exposed` 검토** 다.

---

## 2026-04-07 addendum — 공개 전략 / 우선순위 재정렬

### Pulse Core

#### Doing
- 현재 Pulse는 **외부 공개 플랫폼 추진보다 내부 기반 유지**를 우선하는 상태로 본다.
- `좋은 모드 먼저, 플랫폼은 나중` 원칙을 유지하되, 플랫폼 야망 자체를 버리지는 않는다.
- Core 확장보다 **공개 표면 다각화** 문제를 우선 과제로 본다.

#### Next
- Pulse public surface 설계 정리
  - Product surface
  - Stable Core surface
  - Starter surface
  - Guided surface
  - Raw/Internal surface
- Starter / Guided / Raw lane 기준의 문서 / 입구 / 안내 구조 정리
- Pulse 외부 공개 승격 조건 정의
  - spoke들이 실제 수요를 만든 뒤 어떤 기준에서 플랫폼을 전면에 세울지 문서화

#### Hold
- Pulse를 지금 당장 공개 플랫폼으로 밀어붙이는 것
- Core 안에 입문 편의 / 가이드 기능을 직접 넣는 것
- 기능 확장만으로 채택 문제를 풀려는 접근

### Echo

#### Doing
- Echo는 **확장 전선이 아니라 soft-freeze 상태**로 운용한다.
- 유지보수 / 표면 보수 / 관측 품질 유지 중심 운영을 우선한다.

#### Next
- Iris 이후 실제 blind spot이 확인될 때만 국소적 profiling 확장 재개 기준 정리

#### Hold
- Echo를 지금 메인 개발축으로 다시 키우는 것
- 정밀 profiling 확장을 선제적으로 대규모 재개하는 것

### Fuse

#### Doing
- Fuse는 자기 영역 안에서 headroom이 더 큰 안정화기라는 해석을 유지한다.
- 다만 `더 만들 대상`보다 `정교하게 다듬을 안정화기`라는 톤을 유지한다.

#### Hold
- Fuse가 Area 9를 공동 소유하거나 흡수하는 것

### Nerve

#### Doing
- Launch Nerve는 **100% Lua / Pulse 비의존 standalone** 경계를 유지한다.
- Area 9는 멀티 성능 최적화가 아니라 **same-tick insurance** 로 해석한다.

#### Next
- 후속 확장 필요 시 `Pulse capability -> Nerve+ 소비` 방향만 장기 옵션으로 정리

#### Hold
- 초기 Nerve를 Pulse 의존형으로 만드는 것

### Iris

#### Doing
- Iris 첫 공개는 **DVF + Tooltip** 본체 검증 중심으로 읽는다.
- 모드 시장 확장은 후속 과제로 남긴다.

#### Hold
- Iris 첫 공개에 모드 시장 확장 시스템을 포함하는 것

#### Backlog
- B42 포트 브랜치 준비
  - 메인라인 즉시 전환이 아니라 별도 포트 작업으로 천천히 대응
  - tooltip / menu / browser 표면 우선 점검

## 이번 addendum의 읽기 규칙

- 이번 재정렬의 핵심은 **기능 추가**가 아니라, 무엇을 지금 닫고 무엇을 나중으로 미룰지의 구조적 정리다.
- Pulse의 현재 해법은 Core 기능 확장이 아니라 **public surface redesign** 이다.
- Echo는 당분간 유지/보수 중심으로 묶고, Iris는 vanilla-first MVP로 먼저 닫는다.
---

# 8. 2026-04-07 Addendum — Iris 이후 우선순위 / Pulse 개방 순서 / 인지 전략 재잠금

## 이번 addendum의 상태 해석

- 이번 addendum은 구현 완료 보고가 아니라, **Iris 이후 무엇을 먼저 열고 무엇을 뒤로 미룰지에 대한 전략 재잠금**이다.
- 기준은 `덜 만든 모듈`이 아니라, **Iris 동결 뒤 어떤 한 수가 전체 기대값을 가장 크게 올리는가**다.

## Pulse Core

### Doing
- Pulse는 내부 구조상 플랫폼으로 유지하되, **외부 개방 순서를 뒤집는 전략**을 기본선으로 둔다.
- Stage B / 외부 모드 로딩은 구조상 가능한 단계로 남겨두되, **실제 공개 게이트는 spoke 수요 형성 뒤**로 미룬다.
- 공개 전략은 `빈 플랫폼 소개`가 아니라 **spoke가 Pulse의 의미를 넓히는 순차 구조**로 유지한다.

### Next
- Pulse public surface diversification 정리
  - Product surface
  - Stable Core surface
  - Starter surface
  - Guided surface
  - Raw/Internal surface
- 외부 개방 게이트를 `기술 가능 시점`이 아니라 **수요 개시형 게이트**로 읽는 설명 문구 정리
- `왜 Pulse를 써야 하는가`를 spoke workflow 기준으로 설명하는 공개 언어 정리

### Hold
- 빈 플랫폼을 먼저 공개하고 외부 모더 유입을 기다리는 방식
- `Pulse + Frame + Canvas` 동시 대형 공개
- Pulse를 지금 당장 순수 라이브러리로 격하하는 판정

## Echo

### Doing
- Echo는 확장 전선보다 **soft-freeze / 유지보수 / 표면 보수 중심 모듈**로 읽는다.
- 현재는 `더 많이 재기`보다 observer-only 경계와 자기 부하 억제가 더 중요하다는 해석을 유지한다.

### Next
- Iris 이후 실제 blind spot이 확인될 때만 정밀 profiling을 국소적으로 다시 여는 조건 문구 정리

### Hold
- Echo를 당장 다시 메인 개발축으로 승격하는 것

## Fuse

### Doing
- Fuse는 자기 영역 안에서 headroom이 큰 안정화기로 유지한다.
- 다만 `영역 확장`보다 `자기 영역 정교화` 쪽이 맞다는 해석을 유지한다.

## Nerve

### Doing
- Nerve는 더 좁고 보수적인 안정화기로 유지한다.
- Area 9는 계속 **멀티 성능 최적화가 아니라 same-tick Lua insurance**로 읽는다.

### Hold
- Fuse가 Area 9를 공동 소유하거나 흡수하는 것

## Iris

### Doing
- Iris 첫 공개는 계속 **DVF + Tooltip vanilla-first 본체 검증**으로 읽는다.
- 경쟁 리스크는 기능 부족보다 **인지/포지셔닝 부족**으로 우선 해석한다.

### Next
- Iris를 `설명 위키`가 아니라 **막히는 재료/상호작용을 바로 따라가는 도구**로도 인식시키는 표면/설명 포인트 정리

### Hold
- 경쟁 모드 출현을 이유로 Iris를 기능 부족 상태로 성급히 재판정하는 것

## Frame / Canvas

### Doing
- Echo / Frame / Canvas가 서로 다른 창작자 층의 **실사용 수요를 먼저 만들고**, 그 위에서 Pulse 개방이 의미를 갖는다는 전략 해석을 유지한다.
- 둘은 계속 peer spoke로 두고, 플랫폼 의미를 넓히는 spoke로서 읽는다.

---

# 9. 2026-04-08 Addendum — Iris DVF 3-3 surface contract authority migration

## 이번 addendum의 상태 해석

- 이번 addendum은 style normalization 재개가 아니라, **default surface exposure authority를 single-writer decision stage 안으로 명문화한 round** 다.
- 현재 상태는 `implementation + offline closeout + fresh round manual rerun pass` 로 읽는다.

## Iris

### Done
- `surface_contract_signal.jsonl` 분리
- structural audit와 advisory lint 경로 분리
- `quality/publish decision stage` single-writer 유지 상태로 structural contract input 연결
- `quality_baseline_v4.json` 동결
- `structural_audit_dry_run_delta.json` 생성
  - publish delta: `0`
  - lane stability: `pass`
  - introduced surface regression: `0`
- `2026-04-08` fresh manual in-game rerun pass 기록
  - Browser/Wiki default surface `internal_only` suppression pass
  - `exposed` body render pass
  - context menu / other layer / perf regression pass
- `identity_fallback_source_expansion_backlog.json` 생성
  - handoff alignment: `617 / 617 / 617`
  - bucket split: `11 / 599 / 7`
- walkthrough 문서 작성
  - `docs/iris-dvf-3-3-surface-contract-authority-migration-walkthrough.md`

### Doing
- current rollout 1은 authority만 명문화한 상태로 유지한다.
- current publish split은 계속 `internal_only 617 / exposed 1467` 이다.
- `FUNCTION_NARROW`는 direct execution lane 유지, `ACQ_DOMINANT`는 hold 유지로 읽는다.

### Next
- next `identity_fallback` source expansion round는 old `phase1_parallel` plan 단독 해석이 아니라 current `phaseE` handoff artifact `identity_fallback_source_expansion_backlog.json` 기준으로 연다.
- current `role_fallback hollow` lane는 terminalized 상태다. 새 source expansion round는 closed lane 연장이 아니라 `role_fallback_hollow_terminal_handoff.json` 기준의 새 라운드로만 연다.
  - terminal accounting: `37 = reuse preview 20 + promoted 12 + policy closed 2 + carry-forward hold 3`
  - active execution lane: `0`
  - future reopen start point: `future_new_source_discovery_hold`
  - downstream read point: `role_fallback_hollow_terminal_status.json`, `role_fallback_hollow_terminal_handoff.json`
  - dry-run preview: `C1-B reuse 20`은 current v2 contract 기준 `20/20 strong`, `20/20 exposed` projected recovery
  - post-C1-B residual handoff: `role_fallback_hollow_residual_after_c1b_reuse.json`
  - residual execution package: `role_fallback_hollow_net_new_package/` (`net_new 15 = material_body 9 / tool_body 6`)
  - residual policy memo: `role_fallback_hollow_policy_review/role_fallback_hollow_policy_review_memo.json`
  - policy resolution packet: `role_fallback_hollow_policy_review/role_fallback_hollow_policy_resolution_packet.json` (`maintain_exclusion 2`, phase-C precedent attached)
  - policy outcome projection: `role_fallback_hollow_policy_review/role_fallback_hollow_policy_outcome_projection.json` (`recommended maintain_exclusion`, override reopen `C1-G 2`)
  - policy default closeout: `role_fallback_hollow_policy_review/role_fallback_hollow_policy_default_closeout.json` (`policy closed 2`, runtime delta `0`)
  - residual tail handoff: `staging/compose_contract_migration/full_runtime/role_fallback_hollow_residual_tail_handoff.json` (`parked 3`, reopen only on new non-translation requirement evidence)
  - residual tail source-discovery round: `staging/compose_contract_migration/full_runtime/role_fallback_hollow_residual_tail_source_discovery_round.json` (`C1-F 1 -> C1-G 2`, runtime frozen until reopen)
  - residual tail source-discovery status: `staging/compose_contract_migration/full_runtime/role_fallback_hollow_residual_tail_source_discovery_status.json` (`executed remain-parked 3 / reopen_ready 0 / pending 0`)
  - residual tail round closeout: `staging/compose_contract_migration/full_runtime/role_fallback_hollow_residual_tail_round_closeout.json` (`round complete / carry-forward hold 3 / next lane future_new_source_discovery_hold`)
  - terminal status: `staging/compose_contract_migration/full_runtime/role_fallback_hollow_terminal_status.json` (`promoted 12 / policy closed 2 / carry-forward hold 3 / active unresolved 0`)
  - terminal handoff: `staging/compose_contract_migration/full_runtime/role_fallback_hollow_terminal_handoff.json` (`37 = reuse preview 20 + promoted 12 + policy closed 2 + carry-forward hold 3`)
  - net-new work packages: `role_fallback_hollow_net_new_work_packages.json` (`C1-F tool_use_recovery 6 / C1-G material_context_recovery 9`)
  - follow-up sequencing: `role_fallback_hollow_followup_runbook.json` (`reuse 20 -> policy projection 2 -> net_new 15`)
  - source-expansion seed packages: `staging/source_coverage/block_c/role_fallback_hollow_seed_package_index.json` (`C1-F 6 / C1-G 9`)
  - local evidence sweep: `staging/source_coverage/block_c/role_fallback_hollow_local_evidence_index.json`
  - manual second-pass upgrades: `staging/source_coverage/block_c/role_fallback_hollow_manual_second_pass_upgrades.json` (`upgrade 5 -> remaining manual 3`)
  - source authoring queue: `staging/source_coverage/block_c/role_fallback_hollow_source_authoring_queue.json` (`targeted 12 / manual 3`)
  - targeted authoring pack: `staging/source_coverage/block_c/role_fallback_hollow_targeted_authoring_pack.json` (`targeted 12 only`)
  - targeted authoring drafts: `staging/source_coverage/block_c/role_fallback_hollow_targeted_authoring_drafts_index.json`
  - source promotion drafts: `staging/source_coverage/block_c/role_fallback_hollow_targeted_source_promotion_drafts_index.json`
  - manual search pack: `staging/source_coverage/block_c/role_fallback_hollow_manual_search_pack.json` (`manual 3 = C1-F 1 / C1-G 2`)
  - manual residual blocker memo: `staging/source_coverage/block_c/role_fallback_hollow_manual_residual_blocker_memo.json` (`parked 3 pending new source discovery`)
  - source merge previews: `staging/source_coverage/block_c/role_fallback_hollow_targeted_source_merge_previews_index.json` (`pass 12`)
  - source authority candidates: `staging/source_coverage/block_c/role_fallback_hollow_targeted_source_authority_candidates_index.json` (`promotion ready 12 / parked 3`)
  - source replacement candidates: `staging/source_coverage/block_c/role_fallback_hollow_source_replacement_candidates_index.json` (`ready 12 / carry-forward parked 3`)
  - source replacement delta review: `staging/source_coverage/block_c/role_fallback_hollow_source_replacement_delta_review_index.json` (`semantic upgrade 12 / parked carry-forward 3`)
  - source promotion manifest: `staging/source_coverage/block_c/role_fallback_hollow_source_promotion_manifest.json` (`apply ready 12 / carry-forward parked 3`)
  - source promotion applied: `staging/source_coverage/block_c/role_fallback_hollow_source_promotion_applied.json` (`applied package 2 / ready 12 / carry-forward parked 3`)
  - post-block-c apply status: `staging/compose_contract_migration/full_runtime/role_fallback_hollow_post_block_c_apply_status.json` (`promoted 12 / parked 3 / policy 2`, default maintain_exclusion `2`)
  - post-policy default closeout status: `staging/compose_contract_migration/full_runtime/role_fallback_hollow_post_policy_default_closeout_status.json` (`promoted 12 / policy closed 2 / parked 3`)
  - current remaining unresolved tail: `camping.SteelAndFlint`, `Base.Yarn`, `Base.ConcretePowder`
  - C1-F executed discovery pass: `staging/source_coverage/block_c/role_fallback_hollow_residual_tail_source_discovery_round/c1-f/c1-f_residual_tail_discovery_pass.json` (`executed 1 / reopen_ready 0 / remain_parked 1`; generic StartFire context only, no direct non-translation requirement)
  - C1-G executed discovery pass: `staging/source_coverage/block_c/role_fallback_hollow_residual_tail_source_discovery_round/c1-g/c1-g_residual_tail_discovery_pass.json` (`executed 2 / reopen_ready 0 / remain_parked 2`; declaration/spawn context only, no direct non-translation requirement)
  - post-apply ready preview: `staging/source_coverage/block_c/role_fallback_hollow_post_apply_preview_index.json` (`ready 12 / parked 3 / direct_use preserved 12 / special_context preserved 11 / gate pass 2`)
  - downstream runtime handoff: `staging/source_coverage/post_c/post_c_projection_summary.json`, `staging/interaction_cluster/source_coverage_runtime/source_coverage_runtime_summary.json` (`role_fallback -12 / direct_use +12`, runtime path `1275 / 718 / 100 / 12`)
- source expansion 이후에만 `ACQ_DOMINANT` residual lane을 다시 측정한다.
- future separate decision 이후에만 `FUNCTION_NARROW` 2차 rollout 개방 여부를 판단한다.

### Hold
- style linter를 publish gate로 승격하는 것
- `FUNCTION_NARROW` blanket isolation
- `ACQ_DOMINANT` blanket isolation
- compose 외부 repair 재도입

## 읽기 규칙

- 이번 round의 성공은 warn 개수 감소가 아니라 **authority ownership 고정 + publish split 안정성 유지** 다.
- `2026-04-08` manual rerun pass가 current round의 closeout evidence다.
- `style lint가 publish를 막는다`는 해석은 current roadmap 기준으로 금지한다.

---

# 10. 2026-04-09 Addendum — Iris DVF 3-3 acquisition lexical authority and Korean surface hardening

## 이번 addendum의 상태 해석

- 이번 addendum은 새 한국어 엔진 roadmap이 아니라, **current sprint7 authority preview/runtime에 실제 반영된 acquisition lexical standardization + body-role lexical hardening** 의 진행 상태를 방향판에 반영하는 것이다.
- current phase는 `offline authority closeout + deployed runtime reflection + manual in-game validation loop` 로 읽는다.

## Iris

### Done
- acquisition lexical planning 문서 작성 및 scope lock 완료
  - `docs/iris-dvf-3-3-acquisition-hint-korean-standardization-execution-plan.md`
  - `docs/iris-dvf-3-3-acquisition-hint-scope-lock.md`
- acquisition lexical execution chain 완료
  - audit
  - bootstrap
  - phase 2 design bundle
  - phase 3 staging / canonical alignment pre-check
  - phase 4 validator extension
  - phase 5 promotion preview
- acquisition null reason backlog 구조화 완료
  - full decisions patch와 facts patch를 함께 묶어 current preview authority에 반영
- sprint7 authority promotion 및 runtime reflection 완료
  - preview promoted facts/decisions/rendered 생성
  - deployed `IrisLayer3Data.lua`와 staged Lua 일치 확인
- acquisition translationese family cleanup 완료
  - `보관 장소`
  - `취급 장소`
  - `작업 장소`
  - `작업 구역`
  - `판매 장소`
  - `작업 차량`
- body-role lexical cleanup 완료
  - `준비 작업`
  - `다루다 / 다룬다 / 다룰 때 / 다루거나`
  - generic `용기다 / 재료다 / 도구다` hardening
- current user-facing family override 반영 완료
  - 보호 기능 착용 아이템 `착용 시 (부위)를 보호할 수 있다.`
  - 화기 identity `소총 / 산탄총`
  - 식품 효과 phrasing
  - 가방 family generic backpack surface + `학생 가방` override
  - 원예/파밍 translationese cleanup

### Doing
- current 라운드는 **manual in-game validation + residual lexical polish** 상태로 유지한다.
- user validation에서 새 drift가 잡히면 `acquisition_lexical_utils.py` 또는 `body_role_lexical_cleanup.py` 같은 existing offline writer branch에서만 수정한다.
- runtime contract는 이미 닫혀 있으므로, 새 문제를 이유로 `active/silent`, `publish_state`, `compose external repair`를 재개방하지 않는다.

### Next
- current deployed runtime 기준으로 인게임 검증 계속 진행
  - inventory view more
  - Iris 위키 패널
  - browser/wiki surface
- 검증 축은 아래 넷으로 유지
  - acquisition 자연화
  - acquisition omission 유지
  - hold item 비승격 확인
  - 보호/화기/가방/식품 lexical family 확인
- residual issue가 다시 나오면 동일 authority path로만 재반영
  - offline cleanup
  - preview regeneration
  - runtime reflection

### Hold
- 한국어 엔진 개발
- runtime josa engine 도입
- style linter gate 승격
- compose 외부 repair/re-compose stage 재도입
- acquisition lexical 문제를 이유로 facts/evidence/state/publish contract를 다시 여는 것

## 현재 읽기 규칙

- 이번 round의 성공 기준은 `문장이 조금 자연스러워졌다`가 아니라, **offline authority branch -> preview gate -> deployed runtime reflection** 경로가 안정적으로 유지되는 것이다.
- current roadmap에서 남은 일은 새 구조 설계가 아니라 **실제 surface 검증과 보수적 잔여분 수정** 이다.
- current round를 `한국어 엔진 개발` 또는 `style gate 강화`로 읽는 해석은 금지한다.

---

# 11. 2026-04-15 Addendum — Iris DVF 3-3 identity_fallback source expansion round closeout at current cluster budget

## 이번 addendum의 상태 해석

- 이번 addendum은 새 cluster architecture round가 아니라, **current source expansion execution이 어디까지 실제로 닫혔는지와 그 이후 어떤 경계에서 다음 round를 열어야 하는지**를 방향판에 반영하는 것이다.
- current state는 `same-session implementation continuation`이 아니라 **`600 promote / residual 17` closeout + next residual round handoff** 로 읽는다.

## Iris

### Done
- `identity_fallback` source expansion executable subset을 `600`건까지 실제 build/runtime path로 밀어 올렸다.
  - executed promote subset:
    - `batch_1_clothing_surface_reuse 254`
    - `batch_2_accessory_headgear_reuse 194`
    - `batch_3_food_storage_reference_reuse 121`
    - `batch_4_medical_kitchen_explosive_reuse 20`
    - `batch_5a_electronics_partial_reuse 4`
    - `bucket_1_wrench_reuse_fast_lane 2`
    - `bucket_1_crowbar_reuse_fast_lane 1`
    - `batch_7_adhesive_repair_supply 2`
    - `batch_8_solid_fuel_material 1`
    - `batch_9_metalworking_consumable_supply 1`
- current canonical remeasurement를 `staging/identity_fallback_source_expansion/phase6_subset_rollout/exec_subset_600_wrench_crowbar_b7_b8_b9/subset_distribution_remeasurement.json` 기준으로 고정했다.
  - runtime path snapshot: `cluster_summary 2040 / identity_fallback 17 / role_fallback 48`
  - lane delta: `identity_fallback -600 / cluster_summary +600`
  - publish split: `internal_only 617 / exposed 1467`
  - remaining residual: `phase3_taxonomy_pending 10 / bucket_3_scope_hold 7`
- current residual inventory를 `phase3_residual_taxonomy_manifest.json`과 `phase3_residual_taxonomy_alignment_report.json` 기준으로 `10 = 10` 정합 상태로 재동결했다.
- interaction cluster seed budget은 current cycle에서 `30 / 30`에 도달했다.

### Doing
- current cycle은 **staged authority subset closeout 상태** 로 유지한다.
- workspace Lua overwrite, reflection apply, manual in-game validation은 필요 시 downstream validation lane에서 수행하되, **same-cycle net-new cluster execution 재개**와 섞지 않는다.
- current source expansion round는 `cluster cap이 닫힌 상태의 closeout baseline`으로만 소비한다.

### Next
- 다음 세션에서는 current closeout baseline 위에서 **별도 residual round opening** 을 연다.
  - baseline: `600 promoted / residual 17`
  - direct residual scope: `phase3_taxonomy_pending 10 + bucket_3_scope_hold 7`
- `30-cap 유지` 기준의 next round는 아래 셋 중 하나로만 이어진다.
  - existing-cluster absorption
  - 제한적 `direct_use` 예외 검토
  - `carry_forward_hold` 분류와 closeout
- `31번째 cluster`가 실제로 필요하다고 판단되면, 그것은 source expansion의 같은 연장이 아니라 **별도 `A-4-1 rework / cluster budget` round opening** 으로 다룬다.

### Hold
- current source expansion cycle 안에서 `31번째` net-new cluster를 추가하는 것
- `cluster_count_limit = 30`을 현재 round 안에서 조용히 올리는 것
- residual `17`을 same-session unfinished queue처럼 계속 이어서 해석하는 것
- `phase3_taxonomy_pending 10`을 current cycle의 자동 promote debt로 읽는 것

## 현재 읽기 규칙

- current success 기준은 `617 전체 완료`가 아니라, **frozen cluster budget 안에서 실제로 밀 수 있는 executable subset을 deterministic하게 승격시키고 residual inventory를 정확히 다시 재는 것**이다.
- current `30 / 30` 상태는 `더 열어도 된다`가 아니라 **current cycle terminal budget edge** 다.
- next work는 current round의 continuation이 아니라, **새 scope lock / 새 baseline / 새 execution manifest를 가진 후속 residual round** 로만 읽는다.

---

# 12. 2026-04-16 Addendum — Iris DVF 3-3 identity_fallback residual round closeout and frozen-budget hold branch

## 이번 addendum의 상태 해석

- 이번 addendum은 새 source expansion batch plan이 아니라, **residual round가 어디까지 실제로 닫혔고 closeout 이후 어떤 branch를 current default로 읽어야 하는지**를 방향판에 반영하는 것이다.
- current state는 `phase3_taxonomy_pending pending execution`이 아니라 **`governance path fixed 10 / frozen hold 11` closeout state** 로 읽는다.

## Iris

### Done
- residual round authority artifact를 current-state 기준으로 생성했다.
  - `residual_round_manifest.json`
  - `residual_round_status.md`
  - `residual_round_closeout_report.json`
  - `residual_round_closeout_note.md`
  - `residual_round_post_closeout_branch_decision.json` / `.md`
- `phase3_taxonomy_pending 10`에 대해 item-level governance path를 전량 확정했다.
  - `existing-cluster absorption 2`
  - `direct_use 4`
  - `carry_forward_hold 4`
- current baseline lineage를 `carry_forward_hold 4 + bucket_3_scope_hold 7 = frozen hold 11` 상태로 재고정했다.
- `30-cap`은 그대로 유지했고, current round에서도 same-cycle net-new cluster는 `0`이다.

### Doing
- current authority는 `maintain_frozen_budget_hold` branch를 기본으로 유지한다.
- downstream validation lane은 자동 개시하지 않는다.
- `A-4-1 rework / cluster budget` round도 current 시점에서는 열지 않는다.

### Next
- 다음 reopen은 아래 둘 중 하나일 때만 검토한다.
  - `future_new_source_discovery_hold`
  - 별도 `A-4-1 rework / cluster budget` round opening
- current default branch 아래에서는 `carry_forward_hold 4`와 `bucket_3_scope_hold 7`을 계속 봉인 상태로 계상한다.

### Hold
- residual round closeout을 이유로 publish exposure 변경, runtime Lua overwrite, manual in-game validation을 자동 downstream로 여는 것
- `carry_forward_hold 4`를 same-session unfinished queue로 다시 읽는 것
- current closeout 뒤에 `31번째 cluster` 필요 여부를 묻지 않은 채 A-4-1을 사실상 조용히 여는 것

---

# 13. 2026-04-16 Addendum — Iris DVF 3-3 identity_fallback closure policy expansion as a separate policy round

## 이번 addendum의 상태 해석

- 이번 addendum은 current residual round reopen이 아니라, **그 round를 닫은 뒤 hold의 일부가 왜 남았는지와 어떤 policy boundary를 separately widen할 것인지**를 방향판에 반영하는 것이다.
- current state는 `residual round unfinished`가 아니라 **`residual round closed + closure policy follow-up defined`** 로 읽는다.

## Iris

### Done
- current residual round closeout 이후 branch를 `maintain_frozen_budget_hold`로 고정했다.
- closure policy expansion amendment를 별도 authority 문서로 추가했다.
  - `docs/Iris/Done/iris-dvf-3-3-identity-fallback-closure-policy-expansion-amendment.md`
- policy widening의 네 축을 current authority로 확정했다.
  - `direct_use` non-cluster closure 재정의
  - dominant-context 허용 + structural dual-context convergence
  - declared transform/build chain evidence 허용
  - `policy widening -> 그래도 안 되면 A-4-1` 순서 원칙

### Doing
- current residual round execution artifact는 그대로 유지한다.
- policy amendment는 future closure policy round authority로만 읽는다.

### Next
- future reopen이 실제로 필요해지면, 다음 순서로 판단한다.
  1. closure policy widening 기준으로 item 재검토
  2. 그래도 canonical close가 안 되는 item만 `A-4-1`로 보냄
- expected first candidates:
  - `Base.Sledgehammer`
  - `Base.Sledgehammer2`
  - `Base.Rope`
  - `farming.WateredCan`

### Hold
- current residual round closeout artifact를 policy amendment로 덮어쓰는 것
- dominant/dual-context 허용을 style naturalness 판정으로 바꾸는 것
- declared chain evidence를 derived utility interpretation까지 넓히는 것

---

# 14. 2026-04-16 Addendum — Iris DVF 3-3 identity_fallback closure policy round closeout

## 이번 addendum의 상태 해석

- 이번 addendum은 새 taxonomy round가 아니라, **closure policy amendment를 실제 separate round로 실행했을 때 current authority가 어디까지 닫히는지**를 방향판에 반영하는 것이다.
- current state는 `policy follow-up planned`가 아니라 **`policy scope 4 closed / scope hold 7 only`** 로 읽는다.

## Iris

### Done
- separate closure policy round authority를 생성했다.
  - `closure_policy_round_manifest.json`
  - `closure_policy_round_status.md`
  - `closure_policy_round_closeout_report.json`
- `carry_forward_hold 4`를 expanded policy 기준으로 전량 `direct_use`로 닫았다.
  - `Base.Sledgehammer`
  - `Base.Sledgehammer2`
  - `Base.Rope`
  - `farming.WateredCan`
- selected branch after policy round를 `policy_resolved_scope_hold_only`로 고정했다.
- current remaining sealed hold를 `bucket_3_scope_hold 7` only 상태로 재고정했다.

### Doing
- current authority는 runtime mutation 없이 policy closeout 상태로 유지한다.
- cluster budget `30 / 30`은 계속 frozen이다.

### Next
- 이후 reopen은 scope-policy hold를 다시 열 때만 검토한다.
- runtime/publish adoption이 필요하다면 그것은 별도 downstream round로만 연다.

### Hold
- policy-level direct_use closeout을 곧바로 runtime path mutation으로 읽는 것
- `bucket_3_scope_hold 7`이 자동으로 해결된 것으로 읽는 것
- closure policy round closeout을 이유로 `A-4-1`이 필요하다고 역으로 읽는 것

---

# 15. 2026-04-16 Addendum — Iris DVF 3-3 identity_fallback terminal snapshot current-state read point

## 이번 addendum의 상태 해석

- 이번 addendum은 새 round opening이 아니라, **이미 닫힌 residual round + closure policy round를 current-state consumer가 어떻게 읽어야 하는지**를 terminal snapshot으로 고정하는 것이다.
- current state는 `follow-up still open`이 아니라 **`terminalized / no immediate next round planned`** 로 읽는다.

## Iris

### Done
- current-state terminal snapshot artifact를 추가했다.
  - `identity_fallback_terminal_status.json`
  - `identity_fallback_terminal_status.md`
  - `identity_fallback_terminal_handoff.json`
  - `identity_fallback_terminal_handoff.md`
- current canonical terminal aggregate를 `existing_cluster_absorption 2 / direct_use 8 / policy_review_closed_maintain_identity_fallback_isolation 7`로 고정했다.
- current `active_execution_lane_count = 0`과 `no_immediate_next_round_planned = true`를 명시했다.

### Doing
- round-specific artifact는 historical execution provenance로 유지한다.
- current-state consumer는 terminal snapshot을 우선 읽는다.

### Next
- immediate next round는 계획하지 않는다.
- future reopen이 필요하면 아래 둘 중 하나로만 연다.
  - `scope_policy_override_round`
  - `runtime_adoption_round`

### Hold
- residual round / closure policy round artifact를 각각 current-state first read point로 다시 해석하는 것
- sealed `scope_policy_hold 7`을 active execution debt처럼 읽는 것
- terminal snapshot closeout을 runtime mutation 완료 상태로 읽는 것

---

# 16. 2026-04-16 Addendum — Iris DVF 3-3 identity_fallback scope policy round closeout

## 이번 addendum의 상태 해석

- 이번 addendum은 새 source-expansion round가 아니라, **sealed `bucket_3_scope_hold 7`을 어떻게 current-state에서 닫아 읽을지**를 separate scope policy round로 확정하는 것이다.
- current state는 `scope hold remains`가 아니라 **`full residual lineage terminalized / no immediate next round planned`** 로 읽는다.

## Iris

### Done
- separate scope policy round authority를 생성했다.
  - `scope_policy_round_manifest.json`
  - `scope_policy_round_status.md`
  - `scope_policy_round_closeout_report.json`
- `bucket_3_scope_hold 7`을 전량 `policy_review_closed_maintain_identity_fallback_isolation`으로 닫았다.
  - `Base.Kettle`
  - `Base.MugRed`
  - `Base.MugSpiffo`
  - `Base.MugWhite`
  - `Base.Mugl`
  - `Base.Saucepan`
  - `Base.Teacup`
- selected branch after scope policy round를 `maintain_identity_fallback_isolation_confirmed`로 고정했다.
- current terminal aggregate를 `existing_cluster_absorption 2 / direct_use 8 / policy_review_closed_maintain_identity_fallback_isolation 7`로 재고정했다.

### Doing
- current authority는 runtime mutation 없이 fully terminalized policy closeout 상태로 유지한다.
- current-state consumer는 terminal status/handoff를 우선 읽는다.

### Next
- immediate next round는 계획하지 않는다.
- future reopen이 필요하면 아래 둘 중 하나로만 연다.
  - `scope_policy_override_round`
  - `runtime_adoption_round`

### Hold
- policy-closed isolation rows를 source-expansion backlog로 다시 읽는 것
- current terminal closeout을 publish/runtime mutation 완료 상태로 읽는 것
- already terminalized lane를 same-session unfinished queue로 다시 읽는 것

---

# 17. 2026-04-17 Addendum — Iris DVF 3-3 identity_fallback roadmap completion at terminal policy authority

## 이번 addendum의 상태 해석

- 이번 addendum은 새 round opening이 아니라, current `identity_fallback` roadmap이 **completed roadmap / no remaining execution debt** 상태라는 점을 canonical docs에 못 박는 것이다.
- current state는 `follow-up queue remains`가 아니라 **`roadmap complete / no immediate next round planned`** 로 읽는다.

## Iris

### Done
- current roadmap completion read point를 terminal snapshot/handoff로 고정했다.
  - `identity_fallback_terminal_status.json`
  - `identity_fallback_terminal_handoff.json`
- current completion aggregate를 `existing_cluster_absorption 2 / direct_use 8 / policy_review_closed_maintain_identity_fallback_isolation 7`로 재확인했다.
- current `scope_policy_hold_count = 0`, `active_unresolved_count = 0`, `active_execution_lane_count = 0`을 완료 기준으로 명시했다.
- current runtime/publish authority가 무변경 종결 상태라는 점을 재확인했다.
  - runtime: `cluster_summary 2040 / identity_fallback 17 / role_fallback 48`
  - publish: `internal_only 617 / exposed 1467`

### Doing
- current authority는 terminalized current-state snapshot으로 유지한다.
- round-specific artifact는 historical provenance로 보존한다.

### Next
- immediate next round는 계획하지 않는다.
- future reopen이 필요하면 아래 둘 중 하나로만 연다.
  - `scope_policy_override_round`
  - `runtime_adoption_round`

### Hold
- current roadmap completed state를 unfinished execution queue로 다시 읽는 것
- policy-closed isolation rows를 source-expansion backlog로 되돌리는 것
- runtime adoption이 아직 없다는 이유만으로 current roadmap을 미완료로 판정하는 것

---

# 18. 2026-04-19 Addendum — Iris DVF 3-3 source-expansion distribution remeasurement gate closeout

## 이번 addendum의 상태 해석

- 이번 addendum은 새 source expansion execution round가 아니라, **이미 닫힌 source expansion closeout 위에서 5축 분포를 다시 계측하고 adjudication한 observer gate closeout** 을 current roadmap에 반영하는 것이다.
- current state는 `source expansion next item`이 아니라 **`SDRG closed / PASS / no immediate next round planned`** 로 읽는다.

## Iris

### Done
- current SDRG root artifact chain을 생성했다.
  - `source_expansion_distribution_remeasurement_gate_manifest.json`
  - `source_expansion_distribution_remeasurement_gate_status.md`
- current session walkthrough provenance를 추가했다.
  - `iris-dvf-3-3-source-expansion-distribution-remeasurement-gate-walkthrough.md`
- `Phase 1` baseline authority freeze를 comparison baseline / current handoff authority 2층 구조로 고정했다.
  - comparison baseline: `cluster_summary 1440 / identity_fallback 617 / role_fallback 48`
  - current handoff authority: `cluster_summary 2040 / identity_fallback 17 / role_fallback 48`
- `Phase 2-3` trigger prerequisite authority를 별도 owner split으로 고정했다.
  - `source_expansion_closeout_authority.json`
  - `expected_expansion_scope_reference.json`
  - `source_expansion_trigger_prerequisites.json`
- `Phase 4-5` fresh recompute / 5축 재측정 / delta adjudication을 완료했다.
  - `post_expansion_remeasurement_v0.json`
  - `post_source_expansion_audit_distribution.json`
  - `post_source_expansion_overlay_distribution.json`
  - `post_source_expansion_lint_distribution.json`
  - `post_source_expansion_quality_distribution.json`
  - `post_source_expansion_publish_distribution.json`
  - `distribution_delta_report_v0.json`
  - `baseline_carry_decision_v0.json`
- 기존 `5-y0 Next`의 `source expansion 이후 audit / overlay / lint 분포 재측정` 항목을 current observer round에서 실제 artifact로 닫았다.
- 추가된 `quality / publish` 두 축도 같이 재측정해 current SDRG를 `3축 -> 5축 observer gate`로 확장했다.
- current axis adjudication을 `audit PASS / overlay PASS / lint PASS / quality PASS / publish PASS`로 고정했고, `round_exit_status = PASS`를 terminal snapshot과 root manifest 양쪽에 기록했다.
- `Phase 6` semantic decision input artifact를 생성했다.
  - `semantic_decision_input_packet.json`
  - `semantic_decision_review.md`
  - `decisions_md_patch_proposal.md`
- `Phase 6.5` retroactive first-application backfill을 supporting artifact로 생성했다.
  - `retroactive_axis_recoverability_precheck.json`
  - `pre_expansion_baseline_v0_retroactive.json`
  - `post_expansion_remeasurement_v0_retroactive.json`
  - `distribution_delta_report_v0_retroactive.json`
  - `baseline_carry_decision_v0_retroactive.json`
- `Phase 7` terminal snapshot closeout을 생성했다.
  - `source_expansion_remeasurement_terminal_status.json`
  - `source_expansion_remeasurement_terminal_handoff.json`
  - `source_expansion_remeasurement_closeout.md`
- `Phase 8` Group B `569` pre-wiring artifact를 생성했다.
  - `group_b_pre_wiring_runbook.md`
  - `sdrg_trigger_procedure.md`
  - `group_b_expected_delta_template.json`
- `SAPR` explicit semantic decision closeout을 추가했다.
  - `quality_baseline_v4`는 유지하고 current `v5` cutover는 채택하지 않았다.
  - `structural feedback weak candidate` / `source-expansion post-round new weak`만 candidate family로 인정했다.
  - runtime/publish contract와 `no_ui_exposure`는 그대로 유지했다.
- current session walkthrough provenance를 추가했다.
  - `iris-dvf-3-3-semantic-axis-policy-round-walkthrough.md`

### Doing
- current SDRG authority는 observer-only closeout 상태로 유지한다.
- downstream consumer는 root manifest와 terminal status/handoff를 우선 읽는다.
- semantic/publish 판단은 `Phase 6` decision input, SAPR decision text, SAPR carry matrix/closeout report를 canonical read point로만 처리한다.

### Next
- immediate next round는 계획하지 않는다.
- SAPR가 아래 질문을 resolved 상태로 닫았다.
  - `quality_baseline_v4`를 `v5`로 승계할 것인가 -> current round는 `v4` 유지
  - weak signal을 semantic axis 후보로 다룰 것인가 -> family-differential candidate policy로 해결
- future Group B round가 열리면 current pre-wiring을 preferred precondition으로 사용한다.

### Hold
- SDRG를 source expansion execution owner나 enforcement gate로 읽는 것
- retroactive backfill을 terminalized lane reopen이나 runtime/publish mutation으로 읽는 것
- `round_exit_status = PASS`를 이유로 semantic decision이 자동 완료된 것으로 읽는 것

---

# 19. 2026-04-20 Addendum — Iris DVF 3-3 reopen round sizing governance amendment

## 이번 addendum의 상태 해석

- 이번 addendum은 새 `A-4-1` reopen을 여는 것이 아니라, **future explicitly-opened cluster-budget reopen round가 어떤 sizing rule을 먼저 읽어야 하는지**를 reference로 반영하는 것이다.
- current state는 `reopen started`가 아니라 **`sizing governance adopted / no immediate next round planned`** 로 읽는다.

## Iris

### Done
- reopen round sizing governance amendment를 채택했다.
  - `docs/Iris/iris-dvf-3-3-reopen-round-sizing-governance-scope-lock.md`
  - `docs/Iris/iris-dvf-3-3-reopen-round-sizing-governance.md`
  - `docs/DECISIONS.md` 2026-04-20 entry
- 적용 대상을 future explicitly-opened `A-4-1 / cluster-budget reopen`으로 고정했다.
- `future_new_source_discovery_hold`는 item-level evidence gate이므로 이번 amendment 비구속 대상으로 봉인했다.

### Doing
- current authority는 terminal snapshot consumer model과 explicit reopen gate read rule을 그대로 유지한다.
- amendment는 current state reference로만 추가됐고, current runtime/publish authority는 그대로 유지한다.

### Next
- immediate next round는 계획하지 않는다.
- future explicitly-opened `A-4-1 / cluster-budget reopen`이 실제로 열리면, round manifest는 `subset-bounded single-authority sizing rule`을 선행 제약으로 읽는다.

### Hold
- amendment adoption을 current reopen opening으로 읽는 것
- `future_new_source_discovery_hold`까지 amendment 범위를 넓히는 것
- `30-cap`, closure policy boundary, reopen gate 목록을 이번 addendum으로 다시 여는 것

---

# 20. 2026-04-20 Addendum — Iris DVF 3-3 compose authority migration round

## 이번 addendum의 상태 해석

- 이번 addendum은 body-role closure addendum을 재오픈하는 것이 아니다.
- 이번 addendum은 같은 3-3 layer 위에 **compose authority 교체 레이어** 를 별도 lane으로 올려, `sentence_plan -> body_plan` migration의 current roadmap read를 고정하는 것이다.
- current state는 Phase C closeout read다. `body_plan` compose authority migration은 A/B/C까지 닫혔고, `Phase D / E-0 / E`는 후속 lane으로 남아 있다. 같은 세션 D/E attempt는 #21 addendum에서 quarantine 처리한다.

## Iris

### Done
- compose authority migration round planning authority를 current docs tree에 추가했다.
  - `docs/Iris/iris-dvf-3-3-compose-authority-migration-round-final-integrated-plan.md`
- Phase A top-doc implementation을 시작했다.
  - `docs/DECISIONS.md`
  - `docs/ARCHITECTURE.md`
  - `docs/ROADMAP.md`
- Phase B closeout design artifact를 추가했다.
  - `docs/Iris/Done/dvf_3_3_cross_layer_overlay_spec.md` v0.2
  - `docs/Iris/forbidden_patterns.json`
  - `docs/Iris/seam_legality_checklist.md`
- Phase C preparation artifact의 current snapshot을 생성했다.
  - `compose_profile_migration_inventory.jsonl`
  - `compose_profile_migration_summary.json`
  - `compose_profile_precedence_draft.resolved.jsonl`
  - `compose_profile_precedence_draft.summary.json`
  - `compose_profile_resolution_preview.jsonl`
  - `compose_profile_resolution_preview.summary.json`
  - `profile_migration_table.json`
  - `profile_migration_inventory.json`
  - `manual_rebucket_candidates.json`
- Phase C writer authority를 preview lane에서 실제로 연결했다.
  - `Iris/build/description/v2/tools/build/compose_layer3_text.py`
  - `Iris/build/description/v2/tools/build/build_layer3_body_plan_v2_preview.py`
  - `Iris/build/description/v2/tests/test_compose_layer3_text_v2.py`
- current preview/full-runtime verification artifact를 compose-internal body_plan writer 기준으로 재생성했다.
  - `dvf_3_3_rendered_v2_preview.json`
  - `full_runtime/dvf_3_3_rendered_v2_preview.full.json`
  - `full_runtime/quality_publish_decision_v2_preview.full.jsonl`
  - `full_runtime/dvf_3_3_rendered_v2_delta.full.jsonl`
  - `full_runtime/dvf_3_3_body_plan_v2_pilot_corpus.full.jsonl`
  - `full_runtime/dvf_3_3_body_plan_v2_blockers.full.jsonl`
  - `compose_determinism_report.json`
- Phase C closeout artifact와 memo를 고정했다.
  - `golden_subset_seed.json`
  - `pilot_corpus_manifest.json`
  - `legacy_vs_bodyplan_diff_report.json`
  - `docs/Iris/profile_migration_spec.md`
  - `docs/Iris/phase_c_exit_gate.md`
  - `docs/Iris/phase_c_adversarial_review.md`
- Phase C golden seed wording reconciliation과 adversarial sign-off를 documented constraint 조건으로 닫았다.
- Phase C closeout 이후 top-doc reflected meaning을 2차 반영했다.
  - `docs/DECISIONS.md`
  - `docs/ARCHITECTURE.md`
  - `docs/ROADMAP.md`
- Round closeout drift check를 완료하고 closeout memo를 추가했다.
  - `docs/Iris/iris-dvf-3-3-compose-authority-migration-round-closeout.md`
- current round를 body-role closeout / surface contract migration과 분리된 authority lane으로 명시했다.
- current round scope를 `A + B + C`로, 후속 lane을 `D / E-0 / E`로 고정했다.
- body-role closure addendum과 current addendum의 cross-reference를 고정했다.

### Doing
- 없음. 이 addendum의 Phase C scope는 close 상태다.

### Next
- Phase D/E-0/E를 다시 열려면 `scope_policy_override_round` 또는 별도 후속 round opening이 먼저 필요하다.
- 후속 round는 `2105` runtime source, frozen `quality_baseline_v4`, `internal_only` row non-drop, in-game validation policy를 precondition으로 둔다.

### Hold
- facts 슬롯 확장
- compose 외부 repair 재도입
- runtime-side compose/rewrite
- `quality_state / publish_state` axis 변경

---

# 21. 2026-04-21 Addendum — Iris DVF 3-3 body_plan Phase D/E attempt quarantine

## 이번 addendum의 상태 해석

- 이번 addendum은 same-session Phase D/E-0/E execution attempt를 current roadmap에서 quarantine하는 correction addendum이다.
- current state는 `body_plan compose authority migration closed through Phase C only`로 읽는다.

## Iris

### Done
- Phase D/E-0/E attempt의 non-adoption 사유를 기록했다.
  - `docs/Iris/iris-dvf-3-3-body-plan-structural-violation-redesign-round.md`
  - `body_plan_structural_reclassification.full.jsonl`
  - `body_plan_structural_reclassification.summary.full.json`
- Phase E-0 regression gate report는 pass evidence가 아니라 quarantined diagnostic artifact로 내렸다.
  - `body_plan_v2_regression_gate_report.json`
- Phase E runtime rollout reports는 deployed authority가 아니라 quarantined diagnostic artifact로 내렸다.
  - `body_plan_v2_lua_bridge_report.json`
  - `body_plan_v2_runtime_validation_report.json`
  - `body_plan_v2_runtime_rollout_report.json`
- `Iris/media/lua/client/Iris/Data/IrisLayer3Data.lua`는 sealed `quality_publish` bridge baseline으로 복구했다.
- current top docs에 Phase D/E quarantine read를 반영했다.
  - `docs/DECISIONS.md`
  - `docs/ARCHITECTURE.md`
  - `docs/ROADMAP.md`

### Doing
- current adopted migration lane은 Phase C closeout 상태다.
- D/E-0/E는 current closeout이 아니다.

### Next
- Phase D/E-0/E를 다시 진행하려면 explicit opening decision을 먼저 작성한다.
- 후속 implementation은 `historical_snapshot/full_runtime`이 아니라 current `2105` runtime source를 사용해야 한다.
- quality/publish stage는 `quality_baseline_v4`와 existing `quality_publish_decision_preview`를 소비해야 하며 `adequate 130` 같은 새 axis 계산을 만들면 안 된다.
- runtime Lua rollout은 in-game validation policy까지 함께 닫는 경우에만 deployed closeout으로 읽는다.

### Hold
- compose 외부 repair 재도입
- runtime-side compose/rewrite
- `quality_state / publish_state` axis 재정의

---

# 22. 2026-04-22 Addendum — Iris DVF 3-3 Phase D/E staged rollout override round

## 이번 addendum의 상태 해석

- 이번 addendum은 Phase D/E-0/E를 `scope_policy_override_round`로 다시 여는 current-session execution addendum이다.
- 이 addendum은 1050-row same-session attempt를 되살리지 않는다.
- current execution baseline은 `2105 / active 2084 / silent 21`, publish split `internal_only 617 / exposed 1467`, quality split `strong 1316 / adequate 0 / weak 768`이다.
- closeout은 staged/static rollout과 `ready_for_in_game_validation`까지만 허용하며, deployed closeout은 제외한다.

## Iris

### Done

- v1.1 plan을 docs에 고정했다.
  - `docs/Iris/iris-dvf-3-3-phase-d-e-staged-rollout-override-round-plan.md`
- Phase 0 DECISIONS 3개를 기록했다.
  - `scope_policy_override_round opening`
  - Phase D pure observer writer boundary
  - Phase E staged/static-only closeout boundary
- `IrisLayer3Data.lua`가 sealed `quality_publish` bridge baseline hash와 일치함을 확인했다.
- `quality_baseline_v4` distribution이 `strong 1316 / adequate 0 / weak 768`임을 확인했다.
- Phase D observer-only structural reclassification을 04-15 subset rollout current baseline 위에서 재실행했다.
  - `row_count 2105`
  - `writer_role observer_only`
  - `hard_block_candidate_count 0`
  - row artifact 내 `quality_state` field 없음
- Phase E-0 full-runtime regression gate를 pass로 닫았다.
  - 9개 gate axis pass
  - quality distribution gate pass
  - runtime path `cluster_summary 2040 / identity_fallback 17 / role_fallback 48`
  - publish split `internal_only 617 / exposed 1467`
  - quality split `strong 1316 / adequate 0 / weak 768`
- Phase E staged/static rollout을 pass로 닫았다.
  - staged Lua artifact: `IrisLayer3Data.body_plan_v2.2105.staged.lua`
  - workspace Lua: `Iris/media/lua/client/Iris/Data/IrisLayer3Data.lua`
  - bridge source/runtime row count `2105 / 2105`
  - bridge publish split `internal_only 617 / exposed 1467`
  - artifact parity hash `0390272b93a933d7e53bba996b322ffbdd9fc905585bec03fc78d338f469f062`
  - static runtime status `ready_for_in_game_validation`
- 이번 round의 problem/fix/artifact mapping을 walkthrough로 고정했다.
  - `docs/Iris/iris-dvf-3-3-phase-d-e-staged-rollout-override-round-walkthrough.md`
  - 기록 범위: `1050 / adequate 130` quarantine, `2105` baseline 재진입, runtime path source mismatch correction, byte-level Lua parity, 검증 command/result

### Doing

- 없음. 이 override round의 staged/static scope는 close 상태다.

### Next

- 별도 manual in-game validation QA round를 열어 실제 Project Zomboid runtime 표면을 확인한다.
- QA round pass 전에는 `deployed closeout`, `runtime rollout closeout`, `ready_for_release`로 읽지 않는다.

### Hold

- manual in-game validation
- deployed closeout / ready_for_release 선언
- `quality_baseline_v4 -> v5` cutover
- runtime-side compose/rewrite
- facts 슬롯 확장

---

# 23. 2026-04-23 Addendum — Iris DVF 3-3 CDPCR-AS Branch B closeout

## 이번 addendum의 상태 해석

- 이번 addendum은 `CDPCR-AS`를 `implementation-drift verification + authority seal round`로 실행한 결과를 기록한다.
- closeout은 Branch B다: `closed without seal - entrypoint implementation drift, patch round reserved`.
- 상위 authority는 재심하지 않는다. adopted forward authority는 계속 `compose_profiles_v2.json + body_plan`이다.
- 이번 round는 Tier 1 observer lane과 read-only baseline integrity confirmation까지만 닫았고, Tier 2 seal patch는 실행하지 않았다.

## Iris

### Done

- v1.4 plan을 docs에 고정했다.
  - `docs/Iris/iris-dvf-3-3-compose-default-path-classification-authority-seal-round-plan.md`
- Phase 0 scope lock과 Tier 2 design review artifact를 작성했다.
  - `Iris/build/description/v2/staging/compose_default_path_classification_round/diagnostic/scope_lock.md`
  - `Iris/build/description/v2/staging/compose_default_path_classification_round/diagnostic/tier2_design_adversarial_review.md`
  - `Iris/build/description/v2/staging/compose_default_path_classification_round/diagnostic/phase0_opening_seal.json`
- Phase 1 probe pre-flight를 완료했다.
  - `probe_method = i`
  - existing preview wrapper CLI로 diagnostic body_plan artifact 생성 가능
  - original compose files unchanged
- Phase 2 branch trace를 완료했다.
  - `gating_coverage_status = complete`
  - `build_script.legacy_default_open = false`
  - `cli_direct.legacy_default_open = true`
  - context-only classes는 Branch 판정을 바꾸지 않음
- Phase 3 parity probe를 diagnostic lane 안에서만 실행했다.
  - diagnostic row count `2105`
  - diagnostic Lua hash `0390272b93a933d7e53bba996b322ffbdd9fc905585bec03fc78d338f469f062`
  - sealed staged Lua hash와 match
  - sealed staged Lua mtime/hash unchanged
- Phase 4 classification memo를 Branch B로 닫았다.
  - `Iris/build/description/v2/staging/compose_default_path_classification_round/diagnostic/compose_default_path_classification_memo.md`
- Phase 8은 Branch B scope로 read-only integrity confirmation만 수행했다.
  - canonical artifact regeneration 없음
  - staged/workspace Lua parity hash 유지
  - runtime rollout interpretation은 `ready_for_in_game_validation`까지만 유지

### Doing

- 없음. CDPCR-AS는 Branch B로 close 상태다.

### Next

- 후속 `entrypoint drift patch + authority seal round`를 별도로 연다.
- 그 round의 목표는 direct default compose entrypoint를 `compose_profiles_v2.json + body_plan` authority로 봉인하고, legacy access를 explicit compatibility/diagnostic mode로만 제한하는 것이다.
- manual in-game validation QA round는 deployed closeout을 위해 여전히 별도 pending이다.

Note: this Branch B follow-up was opened and closed by Addendum #24 (`EDPAS`). For current state, read #24.

### Hold

- CDPCR-AS 내부 Tier 2 Phase 5-7 즉시 실행
- implicit legacy fallback 유지
- deployed closeout / ready_for_release 선언
- runtime-side compose/rewrite
- `quality_baseline_v4 -> v5` cutover

---

# 24. 2026-04-23 Addendum — Iris DVF 3-3 EDPAS authority seal closeout

## 이번 addendum의 상태 해석

- 이번 addendum은 CDPCR-AS Branch B follow-up인 `EDPAS` closeout을 기록한다.
- closeout state는 `closed_with_authority_seal_executed`다.
- direct default compose entrypoint는 이제 `compose_profiles_v2.json + body_plan` authority를 기본값으로 집행한다.
- deployed closeout은 여전히 선언하지 않는다.

## Iris

### Done

- EDPAS plan/scope lock을 v0.3으로 고정했다.
  - `docs/Iris/iris-dvf-3-3-entrypoint-drift-patch-authority-seal-round-plan.md`
  - `docs/Iris/iris-dvf-3-3-entrypoint-drift-patch-authority-seal-round-scope-lock.md`
- Phase 0 opening verification과 design adversarial review를 닫았다.
  - `scope_lock_reflection.md`
  - `edpas_tier2_design_adversarial_review.md`
  - `phase0_opening_seal.json`
- Phase 1 pre-change snapshot과 guard plan을 작성했다.
  - `pre_change_snapshot.json`
  - `entrypoint_surface_scan.json`
  - `legacy_access_guard_plan.md`
- Phase 2 entrypoint patch를 완료했다.
  - `compose_layer3_text.py` direct default mode now opens `compose_profiles_v2.json`
  - explicit modes: `default`, `compat_legacy`, `diagnostic_legacy`
  - default mode rejects non-v2 profile sources
  - diagnostic legacy output is constrained to the EDPAS diagnostic root
- Phase 3 verification을 pass로 닫았다.
  - unit tests: `299` pass
  - direct default 2105 diagnostic run emitted body_plan v2 meta
  - diagnostic Lua hash matched sealed hash `0390272b93a933d7e53bba996b322ffbdd9fc905585bec03fc78d338f469f062`
  - design review guard violations: `0`
- Phase 4 closeout을 기록했다.
  - `Iris/build/description/v2/staging/entrypoint_drift_patch_authority_seal_round/diagnostic/edpas_closeout.md`
- 기존 문제 1번, 즉 shipped body_plan artifact authority와 direct default compose entrypoint authority의 불일치는 EDPAS 기준으로 해결 완료다.

### Doing

- 없음. EDPAS는 close 상태다.

### Next

- 별도 manual in-game validation QA round를 열어 실제 Project Zomboid runtime 표면을 확인한다.
- 선택적으로 v2 resolver legacy label compatibility mapping cleanup round를 별도로 열 수 있다.

### Hold

- deployed closeout / ready_for_release 선언
- manual in-game validation 결과 선언
- `quality_baseline_v4 -> v5` cutover

---

# 28. 2026-04-25 Addendum — Adapter / Native Body Plan Metadata Migration Round closeout

## 이번 addendum의 상태 해석

- 이번 addendum은 `Adapter / Native Body Plan Metadata Migration Round` closeout을 기록한다.
- closeout state는 `closed_with_active_metadata_migration_only`다.
- 이 round는 decisions/source metadata rewrite only다. Adapter removal, resolver cleanup, runtime Lua rebaseline, manual QA pass, deployed closeout은 아니다.
- current runtime/staged state는 계속 `ready_for_in_game_validation`이다.

## Iris

### Done

- metadata migration plan을 `Draft v0.3-synthesis`로 고정했다.
  - `docs/Iris/Done/plan/iris-dvf-3-3-adapter-native-body-plan-metadata-migration-round-plan.md`
- migration executor를 추가했다.
  - `Iris/build/description/v2/tools/build/build_adapter_native_body_plan_metadata_migration.py`
- Phase 5 dry-run hard gate를 isolated simulation environment 방식으로 pass했다.
  - static legacy fallback residue: `0`
  - dynamic default path fallback reach: `0`
  - canonical write performed: `false`
- Phase 6 canonical apply를 완료했다.
  - Queue A `2006` consumed
  - Queue B `78` consumed
- Phase 7 post-apply verification을 pass했다.
  - active old profile count: `0`
  - active native profile count: `2084`
  - legacy fallback target count: `0`
  - default path legacy fallback reach count: `0`
  - default_adapter_dependency_count: `0`
    - derived alias of `default_path_legacy_fallback_reach_count`, not adapter removal
  - canonical row legacy field residue count: `0`
  - rendered output delta count: `0`
  - resolver source file hash unchanged
  - sealed staged Lua/workspace Lua unchanged
- Phase 8 adversarial review와 Phase 9 closeout pass artifact를 생성했다.
  - `adapter_native_body_plan_metadata_migration_round/phase9_closeout/closeout_pass.json`
- migration walkthrough를 traceability read point로 작성했다.
  - `docs/Iris/Done/Walkthrough/iris-dvf-3-3-adapter-native-body-plan-metadata-migration-round-walkthrough.md`
- migration walkthrough를 current session execution log 수준으로 확장했다.
  - v0.3 plan synthesis
  - executor implementation
  - baseline capture
  - dry-run isolated simulation
  - canonical apply
  - post-apply verification
  - adversarial review
  - closeout result
  - `307 tests / OK`

### Next

- 별도 manual in-game validation QA round를 연다.
- 선택적으로 Resolver Compatibility Mapping Cleanup Round를 별도 opening decision으로 연다.
- 선택적으로 Silent Metadata Intake / Cleanup Round를 별도 opening decision으로 연다.

### Hold

- adapter removal 선언
- persisted_old_profile_count 0 선언
- resolver cleanup complete 선언
- runtime rebaseline / ready_for_release / deployed closeout
- manual in-game validation 결과 선언
- `quality_baseline_v4 -> v5` cutover
- runtime-side compose/rewrite
- compose 외부 repair 재도입

---

# 25. 2026-04-24 Addendum — Iris DVF 3-3 Phase D observer signal preservation patch round closeout

## 이번 addendum의 상태 해석

- 이번 addendum은 `Phase D observer-only signal preservation patch round` closeout을 기록한다.
- closeout state는 `closed_with_observer_patch_applied`다.
- 이번 round는 기존 `ready_for_in_game_validation` staged/static 상태를 바꾸지 않는다.
- mismatch handoff는 발생하지 않았다. source preservation target check는 `match`다.

## Iris

### Done

- planning authority를 v0.3으로 고정했다.
  - `docs/Iris/iris-dvf-3-3-phase-d-observer-signal-preservation-patch-round-plan.md`
- baseline freeze artifact를 생성했다.
  - `phase_d_signal_preservation_baseline.json`
  - `phase_d_signal_preservation_baseline.md`
- source map / signal model / section derivation rule을 observer lane 안에서 봉인했다.
  - `source_signal_source_map.md`
  - `signal_model_design.md`
  - `section_signal_derivation_rule.md`
- additive observer row artifact와 분리 summary를 생성했다.
  - `body_plan_signal_preservation.2105.jsonl`
  - `body_plan_signal_preservation.source_distribution.json`
  - `body_plan_signal_preservation.section_distribution.json`
  - `body_plan_signal_preservation.crosswalk.json`
- observer integrity validator를 pass로 닫았다.
  - `phase_d_signal_preservation_validation_report.json`
  - `phase_d_signal_preservation_validation_report.md`
- old lossy observer view 대비 crosscheck를 생성했고 source target mismatch 없이 닫았다.
  - `signal_preservation_crosscheck_report.json`
  - target result: `BODY_LACKS_ITEM_SPECIFIC_USE 617 / FUNCTION_NARROW 7 / none 1481 = match`
- diagnostic packet을 생성했고 `overall_status = pass`로 닫았다.
  - `phase_d_signal_preservation_diagnostic_packet.json`
- additive-only seal을 유지했다.
  - existing structural artifact hash unchanged
  - staged/workspace Lua hash unchanged
  - `quality_state`, `publish_state` omitted from new row artifact

### Doing

- 없음. observer patch round는 close 상태다.

### Next

- 이 observer lane 내부에 immediate next는 없다.
- global current-state 기준 manual in-game validation QA round pending은 그대로 남아 있지만, 그것은 이번 observer patch round의 후속 실행 항목이 아니다.

### Hold

- `source_signal` / `section_signal` 전역 canonical term 승격
- same-build compose repair
- runtime-side rewrite
- source expansion execution
- `quality_baseline_v4 -> v5` cutover
- deployed closeout / ready_for_release 선언

---

# 26. 2026-04-24 Addendum — Iris DVF 3-3 Structural Reclassification Canonical Code-Path Convergence Round closeout

## 이번 addendum의 상태 해석

- 이번 addendum은 `Iris DVF 3-3 Structural Reclassification Canonical Code-Path Convergence Round` closeout을 기록한다.
- closeout state는 `closed_with_canonical_code_path_convergence_applied`다.
- additive `body_plan_signal_preservation.*` lane은 유지되지만 current default-path authority wording은 superseded된다.
- current runtime/staged state는 계속 `ready_for_in_game_validation`이다.
- distribution handoff는 발생하지 않았다. source/section/overlap exact-match gate는 모두 `match`다.

## Iris

### Done

- structural default observer path를 dual-axis canonical model로 수렴시켰다.
  - `Iris/build/description/v2/tools/build/report_layer3_body_plan_structural_reclassification.py`
- current default authority artifact set을 plain-name structural path로 재선언했다.
  - `phase_d_structural_reclassification_code_path_convergence_round/phase4_artifacts/body_plan_structural_reclassification.2105.jsonl`
  - `phase_d_structural_reclassification_code_path_convergence_round/phase4_artifacts/body_plan_structural_reclassification.2105.summary.json`
- source/section/overlap supplementary distributions, crosswalk, artifact validation report를 생성했다.
- stable `.summary.json` subset과 `legacy_compat_summary`를 current authority summary에 포함시켰다.
- legacy single-slot view를 explicit diagnostic path로 격리했다.
  - `phase_d_structural_reclassification_code_path_convergence_round/diagnostic/legacy_view/body_plan_structural_reclassification_legacy_single_slot.*`
- validation gate를 pass로 닫았다.
  - `convergence_validation_report.json`
  - `convergence_crosscheck_report.json`
  - `entrypoint_surface_guard_report.json`
  - `artifact_hash_guard_report.json`
  - `diagnostic_packet.json`
- exact-match targets를 모두 맞췄다.
  - source: `617 / 7 / 1481`
  - section: `1433 / 672`
  - overlap: `67 / 876 / 557 / 605`
- staged/workspace Lua hash unchanged, runtime status unchanged를 다시 확인했다.
- top docs current-state wording을 default structural convergence 기준으로 갱신했다.

### Doing

- 없음. convergence round는 close 상태다.

### Next

- 별도 manual in-game validation QA round를 연다.
- deployed closeout 또는 release readiness 판단은 그 이후 별도 round에서 다룬다.

### Hold

- deployed closeout / ready_for_release 선언
- manual in-game validation 결과 선언
- `quality_baseline_v4 -> v5` cutover
- runtime-side compose/rewrite
- semantic carry adoption
- source expansion execution
- writer/runtime authority migration

---

# 27. 2026-04-25 Addendum — Iris DVF 3-3 Adapter / Native Body Plan Readiness Round closeout

## 이번 addendum의 상태 해석

- 이번 addendum은 `Iris DVF 3-3 Adapter / Native Body Plan Readiness Round` closeout을 기록한다.
- closeout state는 `closed_with_persisted_old_profile_and_legacy_fallback_inventory_ready`다.
- 이 round는 readiness-only / observer-only다. Legacy count reduction, native metadata rewrite, resolver cleanup, rendered text mutation, Lua bridge mutation은 실행하지 않았다.
- current runtime/staged state는 계속 `ready_for_in_game_validation`이다.

## Iris

### Done

- adapter/native body_plan readiness plan을 `Draft v1.4-synthesis`로 고정했다.
  - `docs/Iris/iris-dvf-3-3-adapter-native-body-plan-readiness-round-plan.md`
- readiness round walkthrough를 traceability read point로 작성했다.
  - `docs/Iris/iris-dvf-3-3-adapter-native-body-plan-readiness-round-walkthrough.md`
- Phase 0 opening decision과 pass criteria contract를 생성했다.
  - `adapter_native_body_plan_readiness_round/phase0_opening/pass_criteria_contract.json`
  - `adapter_native_body_plan_readiness_round/phase0_opening/opening_decision_reflection.md`
- Phase 1 inventory를 생성했다.
  - `inventory_total 2105`
  - `persisted_old_profile_count 2105`
  - `active_old_profile_count 2084`
  - `silent_old_profile_count 21`
  - `legacy_fallback_target_count 78`
- Phase 2 legacy source shape definition과 resolver dependency taxonomy를 생성했다.
- Phase 3 adapter removal checklist와 resolver mode policy를 생성했다.
- Phase 4 active execution queues와 silent metadata inventory를 생성했다.
  - active queue A: `non_fallback_active_metadata_swap 2006`
  - active queue B: `fallback_dependent_active 78`
  - silent metadata inventory: `21`
  - sealed active execution queue total: `2084`
- 78 fallback-dependent row를 subclassification했다.
  - `mechanical_ready 78`
  - `schema_gap 0`
- Phase 5 observer invariant preservation을 pass로 닫았다.
  - staged/workspace Lua hash unchanged
  - runtime state unchanged
  - `quality_baseline_v4` frozen
  - bridge availability unchanged
- Phase 6 readiness report를 `overall_status = pass`로 생성했다.
  - Phase 6 status: `execution_queue_status = ready`
  - Phase 6 status: `silent_metadata_inventory_status = ready`
- Phase 7 adversarial review를 PASS로 닫았다.
- Closeout snapshot에서 active execution queue와 silent metadata inventory를 sealed로 읽는다.
- Status lifecycle을 명시했다.
  - Phase 6 report shape: `ready / ready`
  - closeout pass JSON and Phase 8 top-doc snapshot: `sealed / sealed`
  - Phase 6 JSON shape에 `sealed / sealed`가 있는 plan 사본은 stale로 보고 `ready / ready` backflow 대상이다.

### Doing

- 없음. readiness round는 close 상태다.

### Next

- Adapter / Native Body Plan Execution Round를 별도 opening decision으로 연다.
  - 입력: active execution queue `2084`
  - resolver code modification은 execution round scope 밖이다.
  - rendered output regression gate와 Lua bridge validation이 필요하다.
- Schema Extension Round는 `fallback_schema_gap_count > 0`일 때만 별도 opening decision으로 열 수 있다. 이번 readiness closeout 기준 count는 `0`이므로 자동 개방되지 않는다.
- Resolver Compatibility Mapping Cleanup Round는 execution round 완료 이후 별도 opening decision으로 연다.
- 별도 manual in-game validation QA round는 global pending으로 유지한다.

### Hold

- adapter removed 선언
- legacy count reduced 선언
- resolver compatibility mapping cleanup 실행
- deployed closeout / ready_for_release 선언
- manual in-game validation 결과 선언
- `quality_baseline_v4 -> v5` cutover

---

# 29. 2026-04-29 Addendum — Iris DVF 3-3 Layer4 Absorption Policy Round closeout

## 이번 addendum의 상태 해석

- 이번 addendum은 `Iris DVF 3-3 Layer4 Absorption Policy Round` closeout을 기록한다.
- closeout state는 `closed_with_policy_sealed_zero_count_production_safe`다.
- 이 round는 observer-only decision namespace round다. Source/section axis, publish/quality state, staged/runtime artifact는 변경하지 않았다.

## Iris

### Done

- Layer4 absorption policy round opening artifact를 생성했다.
  - `layer4_absorption_policy_round/phase0_opening/pass_criteria_contract.json`
  - `layer4_absorption_policy_round/phase0_opening/opening_decision_reflection.md`
- provenance detector를 실행했다.
  - row count `2105`
  - `confirmed_count 0`
  - `text_matching_used false`
  - `suspect_tier_defined false`
  - scalar `layer4_context_hint` candidates `452` were not promoted without list/cardinality edge
- `LAYER4_ABSORPTION_CONFIRMED`를 `layer_boundary_hard_block` decision namespace로 봉인했다.
- count = 0 branch를 `sealed_zero_count`로 닫았다.
  - production labeling count `0`
  - writer mutation count `0`
  - publish/quality/runtime delta `0`
- invariant verification을 pass로 닫았다.
  - source distribution `617 / 7 / 1481` unchanged
  - section distribution `1433 / 672` unchanged
  - overlap distribution `67 / 876 / 557 / 605` unchanged
  - bridge availability `internal_only 617 / exposed 1467` unchanged
- walkthrough를 traceability read point로 작성했다.
  - `docs/Iris/Done/Walkthrough/iris-dvf-3-3-layer4-absorption-policy-round-walkthrough.md`

### Next

- immediate next 없음.
- global current-state 기준 manual in-game validation QA round pending은 그대로 남아 있다.

### Hold

- activation round 자동 개방
- source/section axis mutation
- runtime-side compose/rewrite
- deployed closeout / ready_for_release 선언
- `quality_baseline_v4 -> v5` cutover

---

# 30. 2026-04-29 Addendum — FUNCTION_NARROW Disposition Closure and Publish Writer Authority Seal Round closeout

## 이번 addendum의 상태 해석

- 이번 addendum은 `FUNCTION_NARROW Disposition Closure and Publish Writer Authority Seal Round` closeout을 기록한다.
- closeout state는 `closed_with_publish_writer_authority_sealed_delta_0`다.
- 이 round는 publish writer authority를 layer/position correctness로 봉인하고, `FUNCTION_NARROW` / `ACQ_DOMINANT` blanket isolation을 forbidden으로 재분류했다.

## Iris

### Done

- publish writer authority opening artifact를 생성했다.
  - `function_narrow_disposition_closure_publish_writer_authority_seal_round/phase0_opening/pass_criteria_contract.json`
  - `function_narrow_disposition_closure_publish_writer_authority_seal_round/phase0_opening/opening_decision_reflection.md`
- Case 1/2/3 classification authority를 생성했다.
  - publish branch 기준은 semantic quality가 아니라 layer/position correctness
  - Case 1: content absent, `internal_only` justified
  - Case 2: correct-position narrow/acquisition-dominant content, publish unchanged
  - Case 3: layer boundary violation, `internal_only` justified
- `internal_only 617` reason inventory를 생성했다.
  - `case_1_count 617`
  - `case_2_count 0`
  - `case_3_count 0`
  - `publish_delta_expected 0`
- blanket isolation forbidden reclassification을 생성했다.
  - `FUNCTION_NARROW blanket isolation = forbidden`
  - `ACQ_DOMINANT blanket isolation = forbidden`
- build delta verification을 clean branch로 닫았다.
  - `function_narrow_compose_behavior_changed false`
  - rendered output delta `0`
  - publish delta `0`
  - quality delta `0`
  - staged/workspace Lua applied delta `unchanged`
- invariant verification을 pass로 닫았다.
  - bridge availability `internal_only 617 / exposed 1467` unchanged
  - source distribution `BODY_LACKS_ITEM_SPECIFIC_USE 617 / FUNCTION_NARROW 7 / none 1481` unchanged
  - Round B confirmed count `0` reference recorded
- walkthrough를 traceability read point로 작성했다.
  - `docs/Iris/Done/Walkthrough/iris-dvf-3-3-function-narrow-disposition-closure-and-publish-writer-authority-seal-round-walkthrough.md`

### Next

- 별도 manual in-game validation QA round는 global pending으로 유지한다.
- `ACQ_DOMINANT` residual remeasurement는 source expansion 이후 별도 scoped round에서만 연다.

### Hold

- `FUNCTION_NARROW` second rollout
- `FUNCTION_NARROW` blanket isolation 재후보화
- `ACQ_DOMINANT` blanket isolation 재후보화
- source expansion 실행
- runtime-side compose/rewrite
- deployed closeout / ready_for_release 선언
- `quality_baseline_v4 -> v5` cutover
