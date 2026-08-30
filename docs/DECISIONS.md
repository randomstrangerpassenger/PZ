# DECISIONS.md

> 상태: current decision ledger / compact trace-dedup edition through 2026-08-25
> 기준일: 2026-08-25
> 상위 기준: `Philosophy.md`
> 목적: Pulse 생태계에서 이미 사실상 고정된 결정을 짧게 봉인하고, 같은 논쟁의 반복을 줄인다.

> 편집 노트: 이 문서는 날짜순 회의록, closeout report, 실행 로그, ARCHITECTURE 대체물이 아니라 **current decision ledger**다. 기존 항목은 원래 heading 수를 보존하지 않고, 모듈별 decision family 중심으로 압축한다. 반복 evidence/hash/validation ceiling/non-decision 상세는 공통 앵커와 retained predecessor evidence로 흡수한다.

## 문서 규칙

- 이 문서는 **할 일 목록**이 아니라 **이미 내려진 결정**을 기록한다.
- 이 문서의 기본 정렬 기준은 날짜가 아니라 **모듈 → decision family → current readpoint → predecessor trace**다.
- 날짜는 삭제하지 않되, 항상 실제 결정일로 단정하지 않는다. 특히 2026-03-16 이후 문서화 과정에서 과거 판단이 한 날짜에 import되었을 수 있으므로, 날짜는 `origin / ledgered / imported / refined / sealed` 성격의 trace metadata로 읽는다.
- 동일 decision family 안에서는 가장 나중 날짜가 아니라, 항목에 명시된 **current readpoint**를 authoritative 기준으로 읽는다.
- 같은 round lifecycle은 하나로 합치고, 같은 날짜라도 decision family가 다르면 분리한다.
- superseded / reopened / blocked / rejected 항목은 삭제하지 않고, current readpoint 아래의 **Predecessor trace**로 격하한다.
- 각 항목은 가능하면 `상태 / 결정 / 현재 기준 / 영향 / Predecessor trace / Non-decision / Trace` 구조로 적는다. 필요 없는 필드는 생략할 수 있다.
- 구현 세부 실험 로그, 반복 hash 목록, 전체 validation command, closeout 전문은 여기 넣지 않는다.
- 검증 수치·hash·command는 current decision을 이해하는 데 필요한 **최소 결과 trace**로만 남긴다.
- 후속 작업의 input이 되는 artifact path는 보존한다.
- release readiness, runtime rollout, Workshop/public exposure, publish/runtime state mutation 오독 금지는 적극적으로 남긴다. 단, 반복 문구는 COMMON anchor로 흡수한다.
- `Philosophy.md`와 충돌할 경우, `Philosophy.md`가 우선한다.

## Compact Trace Anchors

- 목적: 반복 evidence, validation ceiling, non-decision, hash/path 목록을 공통 앵커와 retained predecessor evidence로 흡수해 token cost를 낮춘다.
- 보존: decision family heading / 날짜 trace / 상태 / 핵심 결정 / 현재 기준 / 최소 결과 trace / 후속 input artifact path / 특수 non-decision label.
- 생략: 반복 artifact path/hash 목록, 전체 validation ceiling, 반복 비결정 문구, 세부 실행 로그, closeout 전문.
- `COMMON-RELEASE-NONDECISION`: runtime rollout, deployed closeout, manual/in-game QA, Workshop/release readiness, public exposure, `ready_for_release` 선언 아님.
- `COMMON-RUNTIME-SURFACE-NONMUTATION`: source facts/decisions, rendered text, runtime Lua, packaged Lua, bridge/runtime payload, `quality_state`, `publish_state`, `runtime_state` mutation 아님.
- `COMMON-EVIDENCE-TRACE`: 상세 artifact/hash/validation command는 해당 결정 당시의 retained artifact path, Git history 및 predecessor evidence에 보존된 것으로 읽는다. 이 ledger 자체는 상세 evidence archive가 아니다.

---

## Pulse

### Pulse Core — 얇고 중립적인 플랫폼

- 상태: current readpoint / pre-ledger imported
- 결정: Pulse Core는 **얇고 중립적인 모드로더 겸 플랫폼**으로 유지한다.
- 현재 기준:
  - Pulse는 특정 프로파일러, 최적화 모드, 킬러앱 전용 런처가 아니다.
  - Pulse Core는 Echo, Fuse, Nerve, Iris, Frame, Cortex, Canvas 같은 하위 모듈을 참조하거나 의존하지 않는다.
  - 하위 모듈 간 직접 참조도 금지한다.
  - 하위 모듈 간 협력이 필요하면 Pulse capability 또는 SPI를 경유한다.
  - Core는 공용 기반만 제공하고, 실제 관측/안정화/최적화/위키/팩 관리 로직은 각 모듈 내부에 둔다.
  - Core에는 프로파일링, 엔진 최적화, Lua 최적화 로직을 넣지 않는다.
- 영향: Pulse Core는 하위 모듈의 역할을 먹지 않고, 플랫폼 품질·호환성·진단 능력으로 1st-party 모드와 외부 모드를 받치는 기반층으로 남는다.
- Trace:
  - ledgered: 2026-03-16 documentation consolidation
  - COMMON-EVIDENCE-TRACE.

### Pulse — Hub & Spoke / SPI / 모듈 분리 원칙

- 상태: current readpoint
- 결정: Pulse 생태계의 기본 구조는 **Hub & Spoke + SPI 우선 구조**로 둔다.
- 현재 기준:
  - Pulse는 Hub이며, 하위 모듈은 Spoke다.
  - 하위 모듈은 Pulse 기능을 참조할 수 있지만, Pulse는 하위 모듈을 참조하지 않는다.
  - Echo는 관측, Fuse는 엔진 안정화, Nerve는 Lua 안정화, Iris는 위키형 정보 계층, Frame은 팩 상태 관리, Canvas는 리소스 적용 상태 관리로 분리한다.
  - Core와 1st-party 모드는 `Pulse Core / pulse-profiler / pulse-engine-optim / pulse-lua-optim` 식으로 역할을 분리한다.
  - 공용 확장 경로는 SPI 중심으로 설계한다.
  - 구체 정책, helper, 편의 기능은 Core가 아니라 하위 모듈 또는 Cortex 같은 격리 구역으로 보낸다.
- 영향: Pulse Core는 안정적인 surface를 제공하고, 구체 정책은 하위 모듈이나 외부 모드가 담당한다.
- Trace:
  - ledgered: 2026-03-16
  - COMMON-EVIDENCE-TRACE.

### Pulse — 호환성 / 성숙도 / Core 오염 방지

- 상태: current readpoint
- 결정: Pulse Core의 최우선 가치는 기능 수가 아니라 **호환성, 안정성, 진단 능력, 오염 방지**다.
- 현재 기준:
  - 타 모드와의 호환성을 1순위 원칙으로 둔다.
  - Core 설계는 공격적인 정책/판단보다 충돌 완화, 진단, 안정성에 우선권을 둔다.
  - 예외 격리, mixin 진단, API 안정성, DevMode/로깅은 상위 우선순위를 가진다.
  - Pulse Core에는 helper/편의/가이드 성격 기능을 넣지 않는다.
  - helper성 기능은 `Pulse에 있어도 되지 않나`라는 이유만으로 Core에 승격하지 않는다.
  - 플랫폼 실패 회피의 핵심은 기능 수 보강이 아니라 **플랫폼 오염 방지와 설치·실행 마찰 제어**다.
- 영향: Core는 끝까지 빈 기반에 가깝게 유지하고, 설치/실행 UX는 새 플랫폼을 강요하는 느낌보다 기존 플레이 흐름을 거의 바꾸지 않는 방향으로 설계한다.
- Trace:
  - ledgered: 2026-03-16
  - refined: 2026-03-23 Core 오염 방지 재확정
  - COMMON-EVIDENCE-TRACE.

### Pulse — capability와 policy 분리

- 상태: current readpoint
- 결정: Pulse는 **측정값과 capability는 제공할 수 있지만, 정책·판단·편의 fast-path는 보유하지 않는다.**
- 현재 기준:
  - 허용: 거리, 상태, tick, phase, hook, state, DTO, observation event 같은 기반 surface.
  - 금지: `근거리면 FULL`, `under pressure`, `이 모듈이 처리해야 함`, `이게 중요함` 같은 정책/판단.
  - 실제 governor 정책은 Fuse/Nerve 같은 하위 모듈이 가진다.
  - `IPulseDataBus`류의 범용 모드 간 실시간 중개 채널은 채택하지 않는다.
  - 허용 가능한 것은 필요 시 observation event 표준화 수준까지다.
- 영향: Pulse는 정책 주입이나 실시간 조정의 중심이 아니라, 모듈들이 자기 판단을 수행할 수 있게 하는 최소 기반 surface만 제공한다.
- Trace:
  - ledgered: 2026-03-17
  - COMMON-EVIDENCE-TRACE.

### Pulse — Primitive Data Sharing v3 / Echo-Fuse 경계

- 상태: current readpoint
- 결정: Primitive Data Sharing 리팩토링은 **객체 공유 제거 + Echo/Fuse 경계 고정**이라는 의미로 v3를 채택한다.
- 현재 기준:
  - `updateSnapshot()` 호출은 Echo 내부 tick 경로에서만 수행한다.
  - 공용 계약은 raw observation 최소선으로 제한한다.
  - `targetId`, `severity` 같은 snapshot 필드는 관측 계약으로만 사용한다.
  - recommendation 생성과 실제 적용은 Fuse 내부 책임으로 남긴다.
  - 기존 `OptimizationHint`류 경로가 남더라도 legacy 호환용이지 중심 경로가 되어서는 안 된다.
- 영향: Echo는 관측자, Fuse는 판단자로 유지되며, Pulse는 양쪽을 실시간 정책 채널로 연결하지 않는다.
- Trace:
  - ledgered: 2026-03-17
  - COMMON-EVIDENCE-TRACE.

### Pulse — API 확장 원칙

- 상태: current readpoint
- 결정: Pulse API 확장은 API를 늘리기 위한 작업이 아니라, **바닐라의 기반 기능 후보 추출 → 진짜 기반인지 판정 → 중립적으로 노출 가능한 것만 API화**하는 순서로 진행한다.
- 현재 기준:
  - 초기 Pulse Core는 거대한 고레벨 정책 API보다 얇고 안정적인 공용 API를 우선한다.
  - 기반 후보 추출 이전의 무차별 API 증설은 열지 않는다.
  - API surface 평가는 언제나 `중립 노출 가능한가`를 마지막 게이트로 둔다.
  - 구체 정책, 헬퍼, 편의 기능은 가능한 한 하위 모듈 또는 Cortex 격리 구역으로 미룬다.
- 영향: Pulse API는 기반 capability로만 확장하며, 모듈별 정책이나 편의성 기능을 Core에 흡수하지 않는다.
- Trace:
  - ledgered: 2026-03-16
  - refined: 2026-03-23
  - COMMON-EVIDENCE-TRACE.

### Pulse — 보수적 리팩토링 원칙

- 상태: current readpoint
- 결정: Pulse 생태계의 리팩토링은 아키텍처를 새로 그리는 작업이 아니라, **헌법·핫패스·외부 계약·실제 코드 상태를 깨지 않는 범위에서만 수행하는 보수적 정리 작업**으로 한정한다.
- 현재 기준:
  - 모든 리팩토링 로드맵은 `실제 코드 확인 후 축소/스킵 가능`을 전제로 한다.
  - 핫패스·구조·DI·리포트 경계에 손대는 작업은 Phase 0 기준선 확보 없이는 착수하지 않는다.
  - EchoProfiler는 `큰 클래스`라는 이유만으로 분해하지 않으며, hot-path field/method access 동등성이 증명될 때만 조건부로 연다.
  - ReportDataCollector 계열은 외부 `Map<String, Object>` 반환 계약을 유지한다.
  - FuseThrottleController는 이미 추출된 경계가 있으면 해당 stage를 스킵할 수 있으며, 추가 분해보다 실제 경계 확인을 우선한다.
  - DI는 전면 전환 프로젝트가 아니라, 기존 `ServiceLocator / PulseServices / 생성자 주입 / fallback` 공존 현실을 규약화하고 누락을 정리하는 과제다.
  - 새 GuardTest, 새 ServiceLocator, 새 snapshot infra, 성급한 BaseConfig 공통 모듈보다 기존 `HubSpokeBoundaryTest`, `PulseServiceLocator`, 하드코딩 기대값 테스트, 인터페이스 통일을 우선 강화한다.
  - 경계 테스트는 실제 존재하고 현재 리팩토링 대상인 Echo, Fuse, Nerve 기준으로만 고정한다.
- 영향: 과잉 구조 개편, `getInstance()` 전면 철거, fallback 전면 제거, 미래 모듈을 가정한 경계 규칙 확대는 기본값으로 금지한다.
- Trace:
  - sealed: 2026-03-20
  - COMMON-EVIDENCE-TRACE.

### Pulse EventBus — 3계층 현실 경로와 COW 등록 구조

- 상태: current readpoint
- 결정: EventBus 리팩토링은 이상적 타입 순수성을 목표로 하지 않고, **핫패스를 빠르게 만들면서도 ClassLoader/모드 호환성을 유지하는 현실 경로**로 진행한다.
- 현재 기준:
  - 호출 경로 우선순위는 `direct class lookup → FQCN O(1) fallback → 제한적 reflection/호환 호출` 순서다.
  - FQCN/reflection 완전 제거는 현재 목표가 아니다.
  - 리스너 저장 구조는 단일 `CopyOnWriteArrayList`를 유지한다.
  - 정렬은 등록 시점 `add + sort`로 끝내는 방향을 우선한다.
  - immutable list 교체, compute 내부 새 리스트 생성, 이진 삽입 중심 복잡 구현은 기본 노선으로 채택하지 않는다.
- 영향: EventBus 작업은 기본 경로 비용 절감과 fallback 비용 제한을 우선하며, 기존 COW 성질을 깨는 구조 개편은 피한다.
- Trace:
  - sealed: 2026-03-20
  - COMMON-EVIDENCE-TRACE.

### Pulse — 공개 전략과 플랫폼 후노출

- 상태: current readpoint
- 결정: Pulse의 채택 전략은 플랫폼 선공개가 아니라, **제품이 먼저 가치를 입증하고 플랫폼은 그 기반으로 후노출되는 방식**으로 둔다.
- 현재 기준:
  - Pulse는 Leaf/Avrix/Storm류의 전면형 Java 로더 경쟁 구도로 자신을 정의하지 않는다.
  - Pulse는 킬러앱이 먼저 가치를 입증한 뒤 나중에 기반으로 드러나는 **샌드박스형 공통 지반**으로 남는다.
  - 플랫폼 서사는 제품보다 앞서지 않는다.
  - 공개/README/배포 문구는 `새 표준 선언`보다 `기반 품질이 결과물을 받친다`는 방향으로 정리한다.
  - 공개 전략은 **Iris → Nerve → Fuse → Pulse+Echo → Nerve+ / Fuse Pulse 의존 전환** 순의 역방향 공개를 기본선으로 둔다.
  - `플랫폼 먼저 공개` 루트는 기본 전략에서 닫는다.
- 영향: Pulse는 검증된 결과물 묶음의 공통 기반으로 소개하며, 플랫폼 자체를 먼저 홍보하거나 특정 킬러앱 전용 런처처럼 보이게 하지 않는다.
- Trace:
  - ledgered: 2026-03-16
  - refined: 2026-03-23
  - COMMON-RELEASE-NONDECISION.

### Pulse — Philosophy.md와 공개 전략 문서 분리

- 상태: current readpoint
- 결정: `Philosophy.md`는 구조 원칙, 금지선, 역할 경계 중심의 **헌법 문서**로 유지하고, 킬러앱/가능 구역/홍보 문구 같은 공개 기대 관리 요소는 별도 `ReleaseStrategy` 계열 문서로 분리한다.
- 영향: 향후 공개 메시지는 헌법 본문이 아니라 별도 전략 문서에서 관리하고, 헌법은 `무엇을 하지 않는가`를 더 또렷하게 유지한다.
- Trace:
  - ledgered: 2026-03-17
  - COMMON-EVIDENCE-TRACE.

### Pulse — 브랜드 후보

- 상태: working name / unresolved legal-final
- 결정: 브랜드 후보군 중 현재 기준 최우선 후보는 `Pulse`다.
- 영향: 최종 확정 전까지는 Pulse를 작업명/우세 후보로 사용하되, 법적 검토나 최종 확정으로 취급하지 않는다.
- Trace:
  - ledgered: 2026-03-16
  - COMMON-EVIDENCE-TRACE.

---

## Echo

### Echo — 순수 관측자 원칙

- 상태: current readpoint
- 결정: Echo는 Fuse/Nerve를 움직이는 정책 엔진이 아니라, **시스템을 흔들지 않는 순수 관측자**로 둔다.
- 현재 기준:
  - Echo는 병목과 상태를 기록하지만, Fuse/Nerve의 행동을 실시간으로 유도하지 않는다.
  - Echo가 `severity / top_target / insight / hint / recommendation`류 값을 통해 Fuse 행동을 실질적으로 유도하는 구조는 직접 추천 API가 아니더라도 금지한다.
  - Echo 관측값은 사후 분석과 리포트 판독 자료로만 쓰며, Fuse/Nerve는 각자 자기 내부 pressure signal, governor, guard 판단으로 동작한다.
- 영향: Echo는 사실을 기록하고, Fuse/Nerve는 자기 내부 정책만으로 행동을 결정한다.
- Trace:
  - ledgered: 2026-03-17
  - COMMON-EVIDENCE-TRACE.

### Echo — 핫패스 무해화 원칙

- 상태: current readpoint
- 결정: Echo 핫패스는 **No-Throw / Fast-Exit / Fail-Soft / Safe Default**를 기본 계약으로 유지한다.
- 현재 기준:
  - Echo 핫패스는 다음 4종으로 고정한다.
    - tick 계측 entry/exit
    - scope push/pop
    - `SpikeLog.logSpike`
    - deep analysis 훅 콜백 수신부
  - 이 경로에서는 `PulseServices`, `EchoConfig` 직접 조회, ServiceLocator/DI, 파일/JSON/문자열 포매팅, `synchronized`/blocking queue, MXBean/Thread/StackWalker, throw/catch 남용을 금지한다.
  - 핫패스는 외부 설정/서비스를 직접 읽지 않고, 느린 경로에서 갱신되는 `EchoConfigSnapshot` + `EchoRuntimeState` 구조를 사용한다.
  - `volatile` 단일 스냅샷 참조를 기본으로 두며, `current()`는 null/throw를 허용하지 않는다.
  - release 운영 경로는 완전 무음이어야 하며, debug mode에서만 세션당 1회 원샷 경고를 허용한다.
  - Spike context capture는 옵션적 느린 경로로 격리하고, CAS 기반 rate-limit와 완전 무음 실패를 기본으로 둔다.
- Predecessor trace:
  - 2026-03-17 Bundle A는 이 핫패스 무해화 원칙을 회복한 closed implementation round였다.
  - Bundle A는 current architecture나 후속 작업 순서가 아니다.
- 영향: Echo 핫패스는 문서로 봉인된 감사 대상이며, 이후 변경은 기존 무해화 계약을 깨지 않는 범위에서만 허용한다.
- Trace:
  - closed predecessor round: 2026-03-17 Bundle A
  - COMMON-EVIDENCE-TRACE.

### Echo — 느린 경로 / 디버그 경로 격리

- 상태: current readpoint
- 결정: Echo의 운영 경로와 느린 진단 경로는 의식적으로 분리한다.
- 현재 기준:
  - 릴리즈에서는 운영 경로가 완전 무음이어야 한다.
  - 디버그 모드에서만 제한적 원샷 경고를 허용한다.
  - `safeContextCapture()`는 실패를 절대 전파하지 않는다.
  - 느린 경로의 진단 기능은 핫패스 안정성을 침해하지 않는 범위에서만 허용한다.
- 영향: 개발 단서는 제한적으로 제공하되, Echo가 관측 과정에서 게임 실행이나 Fuse/Nerve 동작을 흔들지 않도록 한다.
- Trace: COMMON-EVIDENCE-TRACE.

### Echo — provider 증명 파이프와 `0` 분해 규약

- 상태: current readpoint
- 결정: Echo 리포트는 Fuse가 실제로 동작했는지, 왜 동작했는지, 왜 아무 개입이 없었는지, `0`이 실제 무개입인지 provider/snapshot/read 실패인지 구분할 수 있어야 한다.
- 현재 기준:
  - 최소 증명 단위는 `present / active / snapshot_ok / total_interventions / reason_counts`로 고정한다.
  - `0`은 단일 숫자가 아니라, 위 필드와 `error_code`를 통해 무개입 / 비활성 / 미등록 / 조회 실패 / snapshot 실패로 분해되어야 한다.
  - `present`는 provider가 보고하지 않고, **Echo가 registry 조회 결과로만 결정**한다.
  - `active`, `snapshot_ok`, `total_interventions`, `reason_counts`, `error_code`는 provider snapshot이 자기 상태로 보고한다.
  - `providers` 섹션은 deep analysis 옵션과 무관하게 항상 기록한다.
  - `echo_profilers` 같은 부가 분석은 옵션일 수 있지만, provider 증명 파이프는 옵션화하지 않는다.
- Predecessor trace:
  - 2026-03-17 Bundle B는 Echo/Fuse 증명 파이프를 복구한 closed implementation round였다.
  - Bundle B 명칭은 current 설계 단위나 후속 작업 순서가 아니다.
- 영향: Echo는 “부재의 증명은 관측자만 할 수 있다”는 원칙 아래, provider와 Echo의 책임을 리포트 필드 단위로 분리한다.
- Trace:
  - closed predecessor round: 2026-03-17 Bundle B
  - COMMON-EVIDENCE-TRACE.

---

## Fuse

### Fuse — 엔진 안정성 레이어

- 상태: current readpoint / frozen-mainline
- 결정: Fuse는 `AI 최적화 모드`, `평균 FPS 향상 모드`, `정책 엔진`, `엔진 포크`가 아니라, **AI 부하 폭주로 인한 엔진 붕괴 상태를 차단하는 semantic-preserving 엔진 안정성 레이어**로 둔다.
- 현재 기준:
  - 기본 레인은 **semantic-preserving**이다. 즉, 동일 결과를 더 싸게 만들거나 붕괴 상태에서 빠져나오는 최소 안정화만 허용한다.
  - 결과나 규칙이 달라질 수 있는 근사, 공격적 알고리즘 교체, 엔진 포크, AI 의미 변화는 기본 레인에서 제외한다.
  - 외부 메시지는 `평균 FPS 상승`보다 `평균 FPS 방어`, `끊김 감소`, `프레임 붕괴 방지`, `더 안정적인 플레이`를 우선한다.
  - Fuse는 PZ 전체 최적화기가 아니라, 비용 폭주가 확인된 구역에서 pressure signal, governor, backoff, cooldown, fail-soft를 이용해 붕괴 상태를 줄이는 모드다.
  - sustained overload에서는 더 강하게 개입하는 대신 **ACTIVE 상한 / hard-limit streak / COOLDOWN / PASSTHROUGH 철수**를 이용해 개입을 스스로 제한한다.
  - COOLDOWN은 평시 동작 상태가 아니라 개입 금지 상태로 취급한다.
  - sustained overload 대응의 성공은 평균 FPS가 아니라 `장시간 ACTIVE 감소`, `PASSTHROUGH 복귀`, `hard-limit 연속 발생 감소`, 정상적인 상태 전이로 판정한다.
- Predecessor trace:
  - 2026-03-20 Bundle C는 sustained overload 자기규제를 닫은 closed implementation / validation round였다.
  - 해당 round에서 Fuse는 Burst stabilizer로 재정의됐고 sustained overload 시 retreat가 채택됐다.
  - AdaptiveGate가 Fuse 내부 처리 시간에 가까운 값이 아니라 실제 tick duration을 보도록 입력 경계가 교정됐다.
  - Bundle C는 current architecture 명칭이나 후속 고도화 단계가 아니다.
- 영향: README, 공개 문구, 테스트 설명은 `AI를 최적화한다`보다 `붕괴 상태를 차단한다`, `계속 망가진 상태를 오래 끌지 않게 한다`는 방향으로 정리한다.
- Trace:
  - ledgered: 2026-03-17
  - proven / refined: 2026-03-20
  - COMMON-EVIDENCE-TRACE.

### Fuse — 현재 운영 상태: 확장보다 동결 / 회귀 검증 / 설명 정리

- 상태: current readpoint
- 결정: Fuse는 과거 구현 라운드와 tick duration 입력 버그 수정이 끝난 현재, **추가 기능을 키우는 개발축이 아니라 동결·회귀 검증·설명 정리의 대상**으로 본다.
- 현재 기준:
  - 후속 변경은 새 정책 추가보다 regression guard, 문서화, README/포지셔닝, 판독 규칙 유지에 한정한다.
  - `autoOptimize` 같은 자동 판단 / 자동 적용 / 임계값 결정 경로는 남겨두지 않는다. 필요하면 `AUTO_OPTIMIZE_FROZEN`처럼 다시 켜기 어렵게 봉인한다.
  - tick-local cache, dedup, early-out, 자료구조 정리 같은 합헌적 미세 최적화는 이론상 열려 있으나, 현 시점 메인라인 우선순위로 채택하지 않는다.
  - Fuse 동결은 영구 폐쇄가 아니라 전략적 보류다.
  - 재진입은 Area 1·7의 봉인 상태, 명백한 회귀, 누락된 contract 정산처럼 범위가 좁고 기존 semantic-preserving 원칙을 유지하는 경우에만 허용한다.
- 영향: Fuse는 `미지 탐사 재개`가 아니라 **이미 알고 있는 위험 지대의 봉인 상태 확인** 범위에서만 재진입한다.
- Trace:
  - sealed: 2026-03-20
  - COMMON-EVIDENCE-TRACE.

### Fuse — Echo와의 경계: 관측은 Echo, 판단은 Fuse

- 상태: current readpoint
- 결정: Echo는 병목의 **관측치와 provider 상태 증명만** 제공하고, Fuse는 임계값 판단 / recommendation 생성 / optimization 적용을 자기 내부에서만 수행한다.
- 현재 기준:
  - Echo는 category / targetId / severity 같은 raw observation에 머문다.
  - Echo가 `severity / top_target / insight / hint / recommendation`류 값을 통해 Fuse 행동을 실질적으로 유도하는 구조는 직접 추천 API가 아니더라도 금지한다.
  - Echo 관측값을 Fuse의 실시간 정책 입력으로 직접 사용하는 구조는 채택하지 않는다.
  - Fuse는 자기 pressure signal과 내부 상태를 기준으로 동작한다.
  - Echo 리포트의 `present / active / snapshot_ok / total_interventions / reason_counts / error_code`는 Fuse 정책 입력이 아니라 **사후 증명과 판독 surface**다.
  - `0 interventions`는 단독으로 무개입을 뜻하지 않으며 provider registration / active / snapshot / error 상태와 함께 판독한다.
- Predecessor trace:
  - 2026-03-17 Bundle B의 증명 파이프 복구 결과는 이 current Echo/Fuse 경계에 흡수한다.
  - 과거 A/B/C 라운드명은 Fuse의 current 작업 순서나 architecture identifier가 아니다.
- 영향: Echo는 사실을 기록하고, Fuse는 자기 내부 정책만으로 행동을 결정한다.
- Trace:
  - ledgered: 2026-03-17
  - COMMON-EVIDENCE-TRACE.

### Fuse — Area 1 / Area 7 중심축

- 상태: current readpoint / conservative re-entry candidate
- 결정: Fuse의 핵심 실전 가치와 보수적 재진입 후보는 **Area 1(좀비 AI / 업데이트 스텝)** 과 **Area 7(경로탐색 / 충돌 / 물리)** 축에 둔다.
- 현재 기준:
  - Area 7은 `guard / limit / defer / deduplicate / stabilize`만 허용하는 semantic-preserving 안정화 축으로 완료 판정한다.
  - Area 7은 신규 탐색 축이 아니라 유지·회귀 관리 대상으로 전환한다.
  - 경로 알고리즘 변경, 충돌 규칙 변경, 물리 결과 변경, AI 의미 변화는 기본 레인에서 제외한다.
  - Area 7 1차 범위에서는 `IPathfindingPolicy`류의 Pulse 정책 인터페이스, `/fuse status` 같은 UX/명령 체계, `LOSThrottleGuard`, 결과 변화로 이어질 수 있는 `NavMeshQueryGuard` null 반환, TTL 2틱 이상의 collision memo를 채택하지 않는다.
  - Pulse는 capability만 제공하고, Fuse Area 7은 defer-only / TTL=1 / fail-safe 중심의 안정화 설계로 고정한다.
- 영향: Fuse 재진입이 필요하다면 미지 탐사가 아니라 Area 1·7의 봉인 상태 확인, 회귀 방지, 누락 정산으로 한정한다.
- Trace:
  - Area 7 completed: 2026-03-17
  - Area 1/7 priority sealed: 2026-03-17
  - COMMON-EVIDENCE-TRACE.

### Fuse — Area 8 / Area 10은 메인라인 Guard가 아니라 종료·계측 잔존 surface

- 상태: current readpoint / completed then demoted
- 결정: Fuse의 Area 8(Save / IO Stall Guard)과 Area 10(GC / Allocation Pressure)은 완료 흔적을 인정하되, **메인라인 핵심 Guard로 유지하지 않고 제거/동결 방향을 기본 방침**으로 둔다.
- 현재 기준:
  - Area 8은 `SaveEventMixin`, `PreSaveEvent / PostSaveEvent`, `SaveEventState`, mixin 등록까지 실배선이 닫힌 상태를 완료 기준으로 인정한다.
  - Area 10은 GC를 제거하는 모드가 아니라, GC/heap pressure가 시스템을 무너뜨리는지 관측·판정·완충 가능한 상태를 만드는 것으로 완료 판정했다.
  - 그러나 IO/GC Guard는 mainline 핵심 기능으로 유지하지 않는다.
  - enum, reason, removed 표기, 리포트/로그용 계측·분류 흔적은 보수적으로 유지할 수 있다.
  - 재도입은 실험 브랜치에서 좁은 조건을 충족할 때만 검토한다.
- 영향: Area 8/10은 신규 구현 축이 아니라 책임 경계 확인 후 종료된 영역이며, mainline에서는 IO/GC 튜닝 반복보다 제거 실행과 계측 유지 범위 확정을 우선한다.
- Predecessor trace:
  - 실전형 IO/GC OFF/ON 비교는 추가 반복 없이 종료됐다.
  - 종료 이유는 효과가 없어서 포기한 것이 아니라 Fuse가 직접 책임질 수 없는 surface가 충분히 드러났기 때문이다.
- Trace:
  - completed: 2026-03-17
  - demoted: 2026-03-17
  - COMMON-EVIDENCE-TRACE.

### Fuse — validation interpretation / 운영형 회귀 검증 원칙

- 상태: current validation principle / historical scenario labels demoted
- 결정: Fuse 검증은 학술형 대규모 반복 실험이 아니라, **폭주 재현 가능성이 높은 소수 시나리오에서 OFF/ON 중심으로 개입 경로·의미 보존·철수·회귀를 확인하는 운영형 검증**으로 해석한다.
- 현재 기준:
  - 공식 판정은 평균 성능보다 구조 변화, 개입 경로 발동, 의미 보존, 철수 조건, 회귀 여부에 둔다.
  - 시나리오 수는 소수로 압축하고 재현성과 regression evidence를 우선한다.
  - S1~S5, Golden, Stress/Baseline/MP, 과거 OFF/ON pair는 **historical validation label**이며 current task queue가 아니다.
  - 과거 역할을 참조할 경우:
    - S1은 구조적 개입 증명
    - S2는 스트리밍/이동 경계 비개입
    - S3는 바닐라 Lua 상시 병목 부정선
    - S4는 회귀/안정성 게이트
    - S5는 멀티 범위 검증
    로 읽는다.
  - Golden evidence는 실제 인게임 플레이로 재현·유지 가능한 시나리오만 인정한다.
  - 억지 치트 구성이나 플레이 불가능한 고정 병목은 Golden evidence로 사용하지 않는다.
  - Stress / Baseline / MP의 2+1 구분은 predecessor validation framework이며, weak A-series OFF/ON data를 official Stress baseline으로 승격하지 않는다.
  - 과거 시나리오를 다시 사용할 경우에도 새 연구 캠페인을 여는 것이 아니라 봉인된 guard의 의미 불변·회귀 없음·책임 경계를 검증하는 데 한정한다.
- Predecessor trace:
  - S1~S4 role sealed: 2026-03-17
  - S5 / MP scope reduced: 2026-03-17
  - 2+1 framework refined: 2026-03-20
  - Stress proof completed: 2026-03-20
- Trace:
  - COMMON-EVIDENCE-TRACE.

### Fuse / Nerve — 프리즈 책임 경계

- 상태: current readpoint
- 결정: `Fuse가 못한 프리즈를 Nerve가 대신 해결한다`는 식으로 역할을 잇지 않는다.
- 현재 기준:
  - Fuse는 엔진 측에서 분산 가능한 연쇄 폭주와 sustained overload 대응을 다룬다.
  - Nerve는 Lua 이벤트 폭주 / 중첩 / 중복 트리거 조건을 줄일 수 있지만, IO/GC 자체를 직접 흡수하거나 Fuse의 실패를 대체하는 역할로 두지 않는다.
  - 현재 Nerve의 `research / Failure Atlas` 프레이밍은 폐기되었으므로, Fuse/Nerve 경계 설명에서도 이를 current 근거로 쓰지 않는다.
- 영향: Fuse와 Nerve는 서로의 실패를 메우는 관계가 아니라, 각자 다른 failure surface를 보수적으로 제한하는 별도 안정성 축으로 읽는다.
- Trace:
  - ledgered: 2026-03-17
  - Nerve research framing rejected: later readpoint
  - COMMON-EVIDENCE-TRACE.

---

## Nerve

### Nerve — Lua 제어면 기반 선택적 안정성 Guard

- 상태: current readpoint / pre-ledger imported + 2026-03-20 refinements
- 결정: Nerve는 `Lua 병목 해결 모드`, `주력 성능 모듈`, `연구 장치`, `Failure Atlas 구축 프로젝트`가 아니라, **Lua를 제어면으로 사용해 이벤트 / 모드 상호작용 / 동기화 레이어의 스파이크와 작업 겹침을 완충하는 선택적 안정성 Guard**로 둔다.
- 현재 기준:
  - 목표는 Lua 자체를 깎는 것이 아니라, Lua 레벨에서 시스템적 지연·충돌·중첩 트리거를 줄이는 것이다.
  - 평균 FPS 향상보다 멀티/모드팩 환경의 선택적 완충, fail-soft, guard, same-tick retreat, 의미 불변을 우선한다.
  - 성공적인 S5가 나오더라도 필수 최적화 모듈로 승격하지 않으며, 조용한 환경에서는 dormant/selective 구조를 유지한다.
  - `Fuse가 못한 프리즈를 Nerve가 대신 해결한다`는 식으로 역할을 잇지 않는다.
  - Fuse는 엔진 측 분산 가능한 연쇄 폭주를 다루고, Nerve는 그런 프리즈를 유발할 수 있는 Lua 이벤트 폭주 / 중첩 / 중복의 트리거 조건을 줄이는 쪽으로 한정한다.
- 영향: Nerve 로드맵과 공개 전략은 성능 약속이 아니라 선택적 안정성, 보수적 개입, 의미 불변, 비개입 기준, 멀티/모드팩 환경의 guard 성격에 맞춘다.
- Rejected predecessor trace:
  - 2026-03-17 ~ 2026-03-20: `Failure Atlas 구축`, `연구 단계`, `연구 장치`, `자연 발현 실패 수집`, `성공 기법이 아니라 실패 귀속` 계열 표현은 현재 Nerve의 목적성과 맞지 않으므로 current readpoint에서 폐기한다.
  - `Nerve는 완전한 무의 공백지대가 아니라 직접 이식 가능한 답안이 없는 공백지대`라는 표현도 current 제품 정의가 아니라 폐기된 연구 프레이밍의 predecessor trace로만 남긴다.
- Trace:
  - origin: pre-ledger conversation, exact date unresolved
  - ledgered: 2026-03-17 documentation consolidation
  - refined: 2026-03-20 Area 5/6/9 sealing rounds
  - COMMON-EVIDENCE-TRACE.

### Nerve — 검증과 기준선 운용

- 상태: current readpoint
- 결정: Nerve의 검증은 실패 축적이나 연구 목적의 관측이 아니라, **봉인된 Area가 의미 불변 / fail-soft / 철수 조건 / 재현성을 만족하는지 확인하는 제품 검증**으로 둔다.
- 현재 기준:
  - 기본 기준선은 OFF다.
  - `OFF가 더 안전`하다는 표현은 체감이 더 낫다는 뜻이 아니라, OFF가 더 단순하고 책임이 명확한 baseline이어야 한다는 뜻이다.
  - Echo 로그는 실시간 정책 입력이 아니라 사후 확인 자료로만 쓴다.
  - Echo 관측값을 Fuse/Nerve의 실시간 정책 입력으로 직접 사용하는 구조는 채택하지 않는다.
  - Fuse/Nerve ON 비교는 새 연구 축을 여는 수단이 아니라, 봉인된 guard가 의도한 범위 안에서만 동작하는지 확인하는 검증 자료다.
  - 멀티 세션 데이터는 Area 9를 연구 프로젝트로 키우기 위한 재료가 아니라, 유지/폐기 판단과 비개입 확인을 위한 운영 증거로만 쓴다.
- 영향: Nerve의 산출물은 Failure Atlas가 아니라 `의미 불변 증명`, `발동 조건 증명`, `철수 조건 증명`, `비개입 증명`, `유지/폐기 판단`이다.
- Rejected predecessor trace:
  - 2026-03-17 ~ 2026-03-20: `Failure Atlas`, `연구 단계`, `자연 발현 실패 수집`, `실패 귀속 좌표계`는 current 목표에서 폐기한다.
- Trace: COMMON-EVIDENCE-TRACE.

### Nerve — 전장 개시 / 동결 / 고도화 규칙

- 상태: current readpoint
- 결정: Nerve는 Area 5 v0.1 Final 동결과 Area 6 v2.1 집행 기준을 중심으로 하며, 새 전장은 자동으로 열지 않는다.
- 현재 기준:
  - 새 전장의 개시는 `전장 판결 → 외부 조건 충족 확인 → 최소 스코프 정의 → v0.x 범위 결정`이 모두 성립한 경우에만 허용한다.
  - current `고도화`는 새 기능 추가가 아니라, 기존 Area 5/6 개입 경로가 실제로 트리거되고 의미 불변으로 동작하며 재현 가능한지를 증명하는 **증명 강화**로 한정한다.
  - Area 8(IO/Save)과 Area 10(GC/메모리)은 헌법을 지키며 안정화하기 어려운 전장으로 보아 현 시점 제품 전장에서 제외한다.
  - Area 9는 네트워크 제어기가 아니라 same-tick scoped stability guard로만 허용한다.
  - 새 기능 추가보다 문법, 재현성, fail-soft, 소스 청결성과 validation reproducibility를 우선한다.
- 영향: Nerve의 메인라인은 기능 확장보다 Area 5/6/9의 봉인된 스코프 유지, 런타임 증명, 유지/폐기 판단에 집중한다.
- Trace: COMMON-EVIDENCE-TRACE.

### Nerve Area 5 — UI / 인벤토리 안정화 v0.1 Final

- 상태: current readpoint / frozen
- 결정: Area 5는 **`데이터 즉시 반영 + 같은 틱 안의 시각 갱신 coalescing + 의미 불변 + fail-soft bypass`** 를 만족하는 합헌적 최소 구현(v0.1 Final)으로 동결한다.
- 현재 기준:
  - 채택: weak registry, snapshot 순회, executeFn optional fail-soft, bypass 고정.
  - 금지: `defer`, `drop`, `isVisible()`/visibility 기반 flush 판단, UI 상태 기반 정책 판단, Pulse로의 기능 상향 이동, 틱 넘김 캐시, 조기 `ItemTransferBatcher`, 공격적 batching.
  - v0.1은 현재 틱 안에서만 중복을 접는 최소 안정화로 유지한다.
- 영향: Area 5는 완료보다 **동결** 상태로 읽으며, 이후 확장은 별도 전장 판결과 v0.x 정의 없이는 열지 않는다.
- Trace:
  - ledgered: 2026-03-17
  - COMMON-EVIDENCE-TRACE.

### Nerve Area 6 — 이벤트 디스패치 / 모드 훅 폭주 안전 레이어

- 상태: current readpoint / v2.1 execution constitution
- 결정: Area 6은 이벤트를 더 똑똑하게 정리하는 최적화 기능이나 실패 축적용 연구 장치가 아니라, **문제 발생 시 리스너 단위로 격리하고 곧바로 철수하는 보수적 안전 레이어**로 둔다.
- 현재 기준:
  - 기본값은 `enabled = false`, `strict = false`이며, 설치만으로 `drop / delay / reorder / auto policy`가 발생해서는 안 된다.
  - 기본 기준선은 **설치 전/후 의미 동일**이다.
  - `EventDeduplicator` 계열은 폐기하고, 핵심 가드는 `EventRecursionGuard` 같은 재귀/폭주 방지용 최후 가드로 축소한다.
  - 기본은 report-only이며, `strict` opt-in에서만 last-resort drop을 예외적으로 허용한다.
  - `Events.Add` 래핑 충돌이 감지되면 공존 체인 고도화보다 즉시 Area 6을 OFF하는 back-off를 택한다.
  - 위험한 예외는 숨기지 않는다. incident / passthrough / rate-limited 로그를 남기며, fail-soft는 무음 은폐가 아니라 격리 사실의 명시적 노출을 뜻한다.
  - 실제 트리거는 same-tick self-recursion 또는 listener exception으로 한정한다.
  - 깊이, fan-out, 동일성 반복 같은 신호는 상시 제어 트리거가 아니라 incident 이후 근거를 보강하는 제한적 forensic surface로만 쓴다.
  - 행동은 `리스너 단위 격리 후 same-tick pass-through 철수` 하나로 봉인한다.
- 금지선:
  - `EventPriority`, `Governor`, `Throttler`, 의미 기반 allowlist/whitelist
  - `coalesce + flush`, 지연/재정렬
  - Echo/Fuse와 연결된 자동 제어
  - 넓은 global fallback
  - 래퍼 체인 고도화
  - Echo 힌트 기반 동적 조정
  - 자동 threshold 튜닝
  - Java strong reference/GC 방어
  - 같은 모듈 내부 공유까지 Pulse SPI로 강제하는 구조
- 현재 구현 해석:
  - Area 6 v2.1은 합헌이고 실행 가능하지만, 전수 래핑과 listener-unit 격리 비용을 의식적으로 감수한 고위험 설계다.
  - 승인은 안전 인증이 아니라 **책임을 인지한 실행 허가**다.
  - incident가 발생한 경우 허용되는 대응 경로는 `문제 리스너 특정 → 개별 수정 또는 정리 → enabled=false 복구 여부 판정`으로 제한한다.
- 영향: Area 6 검토의 질문은 `무엇을 더 연구할 것인가`가 아니라 `봉인된 안전 레이어가 의미 불변 / fail-soft / 철수 조건을 지키는가`다.
- Rejected predecessor trace:
  - 2026-03-20: `Area 6은 실패 축적용 연구 장치` 해석은 current 목적성과 맞지 않아 폐기한다.
- Trace:
  - refined: 2026-03-20 Area 6 v2.1 sealing
  - COMMON-EVIDENCE-TRACE.

### Nerve Area 5·6 — mutation / re-entry reproducibility gate

- 상태: current policy / predecessor implementation gate generalized
- 결정: Area 5·6의 후속 mutation이나 재진입은 기능 추가보다 먼저 **레포 신뢰성 / 재현성 / fail-soft contract가 깨지지 않았음을 확인하는 gate**를 요구한다.
- 현재 기준:
  - 2026-03-20 v2.1 implementation 당시의 최소 gate는 다음이었다.
    - P0: conflict marker 제거, `NerveUtils.lua` 실코드 문법 확인
    - P1: `OnTickEven`이 의도인지 실수인지 문서/주석/코드 중 하나로 고정
    - P2: fail-soft / 예외 전파 정책을 코드 주석과 문장 수준에서 통일
  - 위 P0~P2는 이미 지난 구현 전 체크리스트 자체를 current task로 유지하는 것이 아니라, **후속 mutation에서 source integrity / intent / exception policy를 먼저 닫아야 한다는 precedent**로 읽는다.
  - 후속 재진입 시 동일 이름의 P0~P2를 기계적으로 재현할 필요는 없지만, 동등하거나 더 강한 reproducibility evidence가 필요하다.
  - Area 5·6 execution plan v2.1은 historical implementation 기준서이며 current 제품 방향을 새로 여는 authority가 아니다.
- 영향: Area 5·6 후속 변경은 새 방향 발명이 아니라 current contract 보존과 재현 가능성 확인을 선행 조건으로 갖는다.
- Trace:
  - predecessor gate adopted: 2026-03-20
  - COMMON-EVIDENCE-TRACE.

### Nerve Area 9 — 네트워크 제어기가 아니라 same-tick 철수형 보험 장치

- 상태: current readpoint
- 결정: Area 9는 멀티/네트워크를 제어하는 기능이 아니라, **네트워크 경계에서 Lua가 자폭하려는 순간 같은 틱 안에서만 물러나는 100% Lua 안정성 레이어**로 둔다.
- 현재 기준:
  - Area 9가 상대할 수 있는 붕괴는 호출 순서/타이밍 붕괴, 데이터 형태(shape) 붕괴, 중복/재진입 붕괴의 세 갈래다.
  - 핑, 패킷, 재전송, 큐잉, 우선순위, 병합, 재정렬, 서버 CPU, 엔진 동기화 수정을 다루지 않는다.
  - 기본 OFF를 유지한다.
  - `네트워크 경계 한정`, `대상 opt-in / 행동 opt-in 분리`, `동일 틱 한정 철수`, `다음 틱 자동 복귀`, `incident-gated pcall only`를 봉인선으로 둔다.
  - 구현 구조는 `켜도 아무 일도 안 하는 스캐폴딩 → observe → guarded path → quarantine`의 단계적 책임 분리를 따른다.
  - 재진입, 중복, shape, depth, guarded pcall, tick retreat, 최소 포렌식의 1~7 가드는 우선 관측·표시·계수 surface로 취급한다.
  - 실제 행동은 단일 `reasonCode`와 same-tick retreat 하나로만 귀결한다.
  - `이상 징후 = 즉시 차단` 구조는 금지한다.
  - Area 9의 유지/폐기 판정은 실제 multiplayer session evidence와 비개입/철수 결과에 결속한다.
- 안전핀:
  - `tickId` 단일 진실의 소스
  - endpoints 폐쇄 목록
  - incident 조건 단일 플래그
  - quarantine key 범위 강제
- 금지선:
  - 핑 개선, 패킷 최적화, 서버 부하 분산, 엔진 동기화 수정
  - 전역 상시 `pcall`
  - 중요도/우선순위 판단
  - 자동 블랙리스트/화이트리스트
  - 영구 차단
  - 지연/병합/재정렬
  - Duplicate early-skip
  - Shape hard-fail 기본 차단
  - 비율/빈도/가중치 incident 계산
  - quarantine 지속시간 확장
  - 일반 이벤트/OnTick/UI/렌더 확장
- 영향: Area 9는 기능 확장 축이 아니라 동결된 same-tick scoped stability guard이며, 존속 여부는 실제 multiplayer evidence에 따라 판단한다.
- Predecessor trace:
  - 2026-03-20: `Area 9는 관측·분류 단계까지만 허용` 해석은 same-tick scoped stability guard 정의로 대체됐다.
  - 2026-03-20: `Area 9는 지금 개발하면 안 되는 영역` 해석은 멀티 협업·재현 인프라 없이 네트워크 제어기로 키우지 않는다는 금지선으로 격하됐다.
  - 2026-03-20: `Area 9는 연구 프로젝트가 아니라 기초공사형 방어 프로그래밍으로 시작`이라는 표현은 current same-tick stability contract로 흡수한다.
- Non-decision: Area 9 동결은 release readiness, runtime rollout, public exposure, Workshop readiness 선언이 아니다.
- Trace: COMMON-EVIDENCE-TRACE.

### Nerve — 내부 전장 독립성과 자기 제한 정책

- 상태: current readpoint
- 결정: Nerve 내부 전장은 개념적으로 연속될 수 있어도 코드 차원의 직접 의존을 만들지 않으며, Nerve가 가질 수 있는 정책은 **자기 자신을 제한하는 정책**뿐이다.
- 현재 기준:
  - Area 5와 Area 6은 tick 경계 같은 최소 공통 개념만 공유할 수 있다.
  - 한 Area가 다른 Area의 존재를 가정하거나 직접 참조하는 구조는 채택하지 않는다.
  - 내부 공유는 Nerve 내부에서 처리하고, 타 모듈 공유만 Pulse SPI 경계를 따른다.
  - 허용되는 정책은 `개입 조건 / 철수 조건 / 이 상황에서는 아예 개입하지 않음` 같은 자기 제한 정책이다.
  - 게임 행동을 바꾸는 정책, 중요도 판단, FPS 기반 동작 변경, 스킵/주기 증가 같은 정책은 허용하지 않는다.
  - ON이 일부 구간에서 체감 개선을 보이더라도 문서와 검증의 기준선은 OFF에 둔다.
- 영향: Nerve는 자기 제약과 철수 조건만 가질 수 있으며, 게임 의미나 행동을 바꾸는 판단 엔진으로 확장하지 않는다.
- Trace: COMMON-EVIDENCE-TRACE.

### Nerve / Nerve+ — 배포 경계

- 상태: current readpoint
- 결정: Nerve는 Pulse 비의존 **핵심 기능 스탠드얼론**으로 유지하고, Nerve+만 Pulse 의존 **핵심 + 편의 계열**로 둔다.
- 영향: 문서/홍보/배포에서 Nerve는 core, Nerve+는 convenience overlay로 설명한다. Fuse의 Pulse 의존 전환도 이 배포 전략과 함께 정렬한다.
- Non-decision: 이 배포 경계는 즉시 release readiness, Workshop readiness, public exposure 선언이 아니다.
- Trace:
  - ledgered: 2026-03-23
  - COMMON-RELEASE-NONDECISION.

---

## Iris

### Iris — offline compiler / Lua viewer 원칙

- 날짜: 2026-03-16 ~ 2026-03-25

- 상태: current readpoint / Philosophy-bound system contract

- 결정: Iris는 확인된 정보를 오프라인에서 정적 산출물로 확정하고, PZ 런타임에서는 100% Lua 기반 viewer가 이를 표시·탐색하는 게임 내 위키형 정보 시스템으로 둔다.

- 현재 기준:

  - 증거, 분류, 상호작용 정보와 설명 산출물의 생성·검증은 오프라인에서 수행한다.
  - 런타임 Lua는 확정된 정적 산출물을 표시·탐색하며 사실을 새로 생성·판단·수정하지 않는다.
  - Iris는 확인된 사실을 이해하기 쉽게 설명할 수 있지만 해석·권장·효율 평가·우열 비교는 하지 않는다.
  - 충분한 근거가 없는 정보는 추측해서 채우지 않고 침묵한다.
  - Iris runtime은 아이템, 행동 또는 게임 상태를 직접 변경하지 않는다.
  - PZ에서 실행되는 Iris는 100% Lua surface로 유지한다.
  - offline production tooling의 구현 언어나 실행환경은 이 runtime 경계를 변경하지 않는다.

- 영향:

  - information production / validation과 runtime presentation을 분리하고 PZ runtime을 확정된 정적 정보의 read-only consumer로 유지한다.

- 오독 금지:

  - offline tooling의 존재를 runtime-side 사실 생성·추론·재판정 권한으로 읽지 않는다.
  - offline Python tooling을 Iris runtime의 JVM / Python 혼용으로 읽지 않는다.
  - COMMON-RUNTIME-SURFACE-NONMUTATION.
  - COMMON-RELEASE-NONDECISION.

- Trace:

  - ledgered / sealed: 2026-03-16 ~ 2026-03-25
  - COMMON-EVIDENCE-TRACE.

### Iris offline tooling — installed package / source-root independence boundary

- 날짜: 2026-08-25

- 상태: current readpoint / current tooling ownership adopted

- 결정: current Description v2 / Right-click production tooling은 repository source-layout이나 caller working directory에 의존하는 ad hoc import path가 아니라 설치된 `iris_tooling` package 경계에서 제공한다.

- 현재 기준:

  - current Description v2 / Right-click tooling owner는 installed `iris_tooling` package다.
  - current consumer는 source-root `tools.build` import에 의존하지 않는다.
  - current tooling 실행을 위해 cwd 또는 `sys.path` bootstrap에 의존하지 않는다.
  - right-click current production path는 predecessor version-mode flag에 의존하지 않는다.
  - tooling package boundary는 offline implementation ownership이며 source facts / Evidence / classification authority를 소유하지 않는다.
  - offline tooling refactor는 supported runtime API나 100% Lua runtime surface를 변경하지 않는다.

- 후속 input artifact:

  - `Iris/_docs/refactor/responsibility_repository_refactor/s0_baseline_adoption.json`
  - `Iris/_docs/refactor/responsibility_repository_refactor/successor_decision.json`
  - `Iris/_docs/refactor/responsibility_repository_refactor/current_migration_map.json`

- Predecessor trace:

  - predecessor Description / Right-click tooling은 repository source-root import와 execution-layout assumptions를 일부 소비했다.
  - 2026-08-25 responsibility refactor가 current owner를 installed `iris_tooling` package로 옮기고 source-root import, cwd / `sys.path` bootstrap과 predecessor mode flag 의존을 제거했다.
  - exact package-environment record, implementation commits와 CLI validation detail은 상세 evidence trace로 격하한다.

- 오독 금지:

  - tooling owner 변경을 facts authority나 semantic production authority의 임의 확장으로 읽지 않는다.
  - repository source-layout 제거를 supported runtime facade 제거로 확대하지 않는다.
  - installed package 사용을 PZ runtime에 Python / JVM component가 추가됐다는 뜻으로 읽지 않는다.
  - COMMON-RELEASE-NONDECISION.

- Trace:

  - tooling responsibility refinement: 2026-08-25
  - COMMON-EVIDENCE-TRACE.

### Iris — Menu / Tooltip presentation contract

- 상태: current readpoint / Philosophy-bound user-facing surface contract

- 결정: Iris가 사용자에게 정보를 보여주는 user-facing surface는 Iris Menu와 Iris Tooltip 두 가지로 한정하며 두 surface는 같은 확정 사실을 서로 다른 깊이로 표시한다.

- 현재 기준:

  - Iris의 user-facing information surface는 `Iris Menu`와 `Iris Tooltip` 두 가지다.
  - Iris Tooltip은 `Alt` 입력이 있을 때만 표시한다.
  - Iris Tooltip은 최대 `4줄`을 넘지 않는다.
  - Iris Menu는 Tooltip보다 상세한 정보를 제공한다.
  - Menu와 Tooltip은 서로 다른 facts authority를 갖지 않으며 같은 사실을 서로 다른 정보 깊이로 투영한다.
  - `same-authority`는 두 surface가 같은 fact source를 사용한다는 뜻이며 모든 layer의 coverage가 항상 동일해야 한다는 뜻이 아니다.
  - Tooltip Layer 2(S1)는 current Classification authority가 user-facing category와 admissible primary subcategory를 함께 제공할 때만 표시하는 optional navigation/display projection이다.
  - Layer 2가 applicable하지 않으면 S1을 placeholder나 빈 줄 없이 생략하고 S2~S4를 위로 당긴다. Menu가 같은 authority에서 더 상세한 정보를 표시하는 것은 이 계약과 모순되지 않는다.
  - Menu와 Tooltip이 같은 대상에 대해 서로 모순되는 사실을 표시하지 않는다.
  - Tooltip은 Menu와 별개의 지식원이나 독립 semantic authority가 아니라 같은 확정 사실의 제한된 요약 projection이다.
  - Browser / Wiki / Detail은 Iris Menu를 구성하는 implementation / presentation component이며 제3의 독립 user-facing knowledge surface가 아니다.
  - Menu / Tooltip의 표시 차이는 information depth와 presentation 차이이며 Source / Evidence / classification / Layer 3 / Layer 4 authority 차이를 만들지 않는다.

- 영향:

  - Iris의 사용자 경험은 상세 Menu surface와 제한된 quick-reference Tooltip surface로 나뉘면서도 동일한 사실 authority를 유지한다.

- 오독 금지:

  - Tooltip을 Menu와 독립된 semantic pipeline으로 읽지 않는다.
  - Tooltip의 4줄 제한을 runtime semantic summarization 또는 사실 재판정 권한으로 읽지 않는다.
  - Tooltip Layer 2 display silence를 Classification correction, semantic absence 판정 또는 raw ID 표시 권한으로 읽지 않는다.
  - Browser / Wiki / Detail을 제3·제4의 독립 Iris information surface로 확대하지 않는다.
  - COMMON-RUNTIME-SURFACE-NONMUTATION.
  - COMMON-RELEASE-NONDECISION.

- Trace:

  - Philosophy-bound surface contract
  - ledgered / imported: 2026-03-16 ~ 2026-03-25
  - COMMON-EVIDENCE-TRACE.

### Iris — Evidence / Source / Outcome 및 Context Outcome 추출 경계

- 상태: current readpoint / offline outcome contract sealed

- 결정: Iris가 Rule과 downstream information producer에서 소비하는 Evidence는 Source나 행동명이 아니라 허용된 Source에서 정규화된 **관찰 가능한 outcome facts**로 고정하며, Context Outcome extractor는 이 봉인된 outcome contract를 오프라인에서 materialize하는 fact-table producer로만 둔다.

- 현재 기준:

  - Source와 Evidence는 구분한다. Source는 사실의 출처이고 Evidence는 Source에서 정규화된 outcome fact다.
  - Recipe와 Right-click은 서로의 하위 체계가 아닌 독립적이고 동등한 Source다.
  - Static capability는 Recipe / Right-click과 동급인 제3 interaction track이 아니라 비상호작용 정적 사실을 공급하는 보조 source family다.
  - 자동 분류는 Source별 별도 rule engine이 아니라 normalized Evidence를 소비하는 단일 outcome 중심 프레임을 사용한다.
  - Evidence의 기본형은 행동명이나 UI 경로가 아니라 아이템과 결부된 관찰 가능한 상태 변화다.
  - 메뉴명, 행동 문자열, 클릭 경로 또는 표시 문구에서 의미를 추론해 outcome을 자동 생성하지 않는다.
  - Equip effect / Use only / Passive function은 기본 Evidence 축으로 자동 승격하지 않는다.
  - Context Outcome extraction은 runtime이 아니라 offline pipeline에서만 수행한다.
  - scanner / intermediate signal representation과 `Signal -> Outcome` mapping을 구분하며 intermediate signal 자체를 Evidence authority로 승격하지 않는다.
  - automatic extraction과 explicit manual injection은 서로 다른 provenance path다.
  - manual injection은 automatic extractor가 닫지 못한 의미를 임의 해석하는 일반 fallback이 아니다.
  - Allowlist 밖 Outcome, nondeterministic result, output-contract violation 또는 outcome-contract identity mismatch는 fail-loud한다.
  - diagnostic / suspicious signal은 관측할 수 있지만 그 자체를 automatic Evidence나 outcome authority로 승격하지 않는다.
  - extractor는 classification authority를 소유하지 않는다.

- 영향:

  - source-specific 표현과 extraction mechanics를 semantic authority에서 분리하고 검증 가능한 outcome fact를 공통 Evidence 계약으로 유지한다.

- Predecessor trace:

  - 초기 scanner / IR / mapper / validator sequence와 item-specific injection routing은 implementation evidence로 격하한다.
  - item-specific diagnostic token과 exact injection target은 영구 semantic taxonomy가 아니다.

- 오독 금지:

  - 행동명·메뉴 문자열 기반 Evidence 생성이나 unrestricted manual interpretation을 승인하지 않는다.
  - diagnostic signal을 automatic PASS Evidence로 승격하지 않는다.
  - COMMON-RUNTIME-SURFACE-NONMUTATION.
  - COMMON-RELEASE-NONDECISION.

- Trace:

  - sealed: 2026-03-24 ~ 2026-03-25
  - COMMON-EVIDENCE-TRACE.

### Iris Right-click — item-dependent state-change proof

- 상태: current readpoint / Gate-0 v2.4 / code-output reconciled

- 결정: Iris의 Right-click Evidence는 메뉴명이나 UI 존재 여부가 아니라 **아이템이 실행 도구로 결합되어 외부 대상에 관찰 가능한 상태 변화를 만드는가**를 기준으로 판정한다.

- 현재 기준:

  - 핵심 proof는 `executing_tool + external_target + persistent_change`다.
  - `persistent_change`는 메뉴 표시나 클릭 경로가 아니라 target / world / container / character에 발생하는 관찰 가능한 outcome state change를 뜻한다.
  - 기본 Evidence 단위는 FullType 단위의 직접 실행 도구다.
  - `PASS / NO / REVIEW`를 primary decision으로 사용한다.
  - `STRONG / WEAK`는 PASS 이후 Evidence uniqueness를 나타내는 보조 판정이다.
  - WEAK는 실패가 아니며 STRONG / WEAK 차이만으로 PASS Evidence의 downstream eligibility를 바꾸지 않는다.
  - property-based / 조건 기반 field는 개별 아이템 uniqueness 전에 field 자체가 Gate-0 실행 도구 구조를 만족하는지 먼저 판정한다.
  - Gate-0에 매칭되지 않는 대상은 Evidence `NO`가 아니라 Right-click Evidence scope 밖으로 둔다.
  - `REVIEW`는 수동 PASS 승격 통로가 아니라 허용된 정적 근거만으로 자동 판정이 닫히지 않은 상태다.
  - 웹·외부 위키를 이용한 수동 PASS 승격은 사용하지 않는다.

- Predecessor trace:

  - 2026-03-25 Gate-0 v2의 `아이템이 없으면 우클릭 메뉴가 생성되는가` 기준은 superseded됐다.
  - STRONG-only canonical 모델은 PASS-then-uniqueness 모델로 대체됐다.
  - `can_*` capability-first, 바닐라 5개 축소, 메뉴명·행동명 중심 모델은 current 기준이 아니다.

- 오독 금지:

  - capability-first 복귀, WEAK 실패 처리, 웹·위키 기반 수동 PASS 승격 또는 메뉴 문자열 기반 outcome 생성을 승인하지 않는다.
  - runtime Lua가 Right-click Evidence를 재판정하거나 proof를 생성하지 않는다.
  - COMMON-RUNTIME-SURFACE-NONMUTATION.
  - COMMON-RELEASE-NONDECISION.

- Trace:

  - current contract: Gate-0 v2.4 / PASS-then-uniqueness
  - COMMON-EVIDENCE-TRACE.

### Iris — 자동 분류 / Evidence Allowlist / capability hint 경계

- 날짜: 2026-03-23 ~ 2026-03-25 → 2026-08-11 refinement

- 상태: current readpoint / classification authority sealed / closed-negative capability inference rejected

- 결정: Iris 자동 분류는 Evidence Allowlist가 허용한 normalized evidence만 소비하며, category / type / method availability 같은 구조적 신호는 확인된 capability의 positive hint로 사용할 수 있지만 충분한 closed-negative authority 없이 capability의 부재나 불가능성을 단정하는 negative authority로 사용하지 않는다.

- 현재 기준:

  - Allowlist 밖의 필드, 문자열, 연산 또는 의미 해석은 자동 분류 근거로 사용하지 않는다.
  - vanilla-first current baseline에서 자동 분류가 직접 소비할 수 있는 근거는 바닐라 scripts / client 선언 데이터와 그로부터 허용된 방식으로 정규화된 Evidence까지다.
  - 외부 모드 데이터는 별도 adapter / compiler를 통해 Iris 내부 표준 산출물로 정규화된 뒤에만 소비하며 raw mod file이나 임의 문자열을 직접 분류 근거로 사용하지 않는다.
  - Java 디컴파일 등으로 획득한 엔진 내부 의미를 자동 분류 Evidence로 승격하지 않는다.
  - 이름, 설명, 표시 카테고리, 임의 문자열 contains, 수치 비교 또는 임의 태그 확장을 통해 의미를 추론하지 않는다.
  - 허용된 Evidence만으로 분류가 닫히지 않으면 임의의 분류 태그를 생성하지 않고 미분류 상태를 유지하거나 명시적인 manual override를 사용한다.
  - manual override도 approved source / provenance와 명시된 authority에 결속해야 하며 unsupported meaning을 보충하는 해석 통로로 사용하지 않는다.
  - `MoveablesTag`와 Item Script의 일반 `Tags`처럼 의미 계약이 다른 namespace는 서로 혼용하지 않는다.
  - 미분류 항목이 많다는 사실 자체를 Evidence Table / Allowlist / DSL 확장의 근거로 삼지 않는다.
  - category / type은 capability 후보를 좁히는 positive hint로 사용할 수 있다.
  - category / type에 특정 값이 없다는 사실만으로 해당 capability가 없다고 판정하지 않는다.
  - method / field presence가 item-instance fact인지 type-level structural hint인지 구분한다.
  - Item Detail의 capability hint는 item instance 범위에서 소비하며 instance에서 관찰된 fact를 같은 `fullType` 전체의 전역 fact로 자동 승격하지 않는다.
  - custom item, contradictory field 조합, same-canonical hybrid와 external-mod variation을 보존할 수 없는 capability mask는 authoritative closed set으로 사용하지 않는다.
  - capability hint는 Browser / Detail optimization에 사용할 수 있지만 Evidence, classification 또는 source fact를 새로 생성하지 않는다.
  - closed-negative inference를 도입하려면 false-negative가 없음을 증명하는 별도 authority contract가 필요하다.

- 영향:

  - 자동 분류의 coverage보다 근거 경계를 우선하면서 presentation / runtime optimization이 classification authority를 암묵적으로 확장하지 못하게 한다.

- 최소 결과 trace:

  - positive capability hint: `allowed`
  - closed-negative authority: `not established`
  - authoritative capability mask: `not adopted`
  - instance fact -> fullType promotion: `forbidden without evidence`

- Predecessor trace:

  - 2026-08-11 codebase optimization follow-up은 Item Detail capability hint를 item-instance scope에 고정하고 fullType 전역 cache 승격을 금지하는 기존 원칙을 재확인했다.
  - 같은 lifecycle의 authoritative capability-mask candidate는 closed-negative authority 부재로 no-op 처리됐다.
  - method-name constant화, per-item calculation 횟수와 exact implementation / validation detail은 상세 evidence trace로 격하한다.

- 오독 금지:

  - positive hint를 confirmed capability fact와 동일시하지 않는다.
  - category / type mismatch를 capability 부재 증거로 자동 사용하지 않는다.
  - method-name 존재 자체를 semantic meaning의 완전한 증명으로 읽지 않는다.
  - manual override를 추측 기반 분류의 우회 통로로 사용하지 않는다.
  - optimization shortcut을 Evidence Allowlist나 runtime-side semantic inference 확대 근거로 사용하지 않는다.
  - COMMON-RUNTIME-SURFACE-NONMUTATION.
  - COMMON-RELEASE-NONDECISION.

- Trace:

  - classification boundary sealed: 2026-03-23 ~ 2026-03-25
  - capability-hint boundary refined: 2026-08-11
  - COMMON-EVIDENCE-TRACE.

### Iris — Taxonomy baseline / category boundary

- 상태: current readpoint

- 결정: Iris의 current item taxonomy는 9개 대분류와 봉인된 소분류 경계를 기준선으로 사용하며 coverage 문제만을 이유로 별도 decision 없이 분류 구조를 재분할하거나 의미 범위를 확장하지 않는다.

- 현재 기준:

  - 대분류는 `Tool / Combat / Consumable / Resource / Literature / Wearable / Furniture / Vehicle / Misc` 9개 축이다.
  - Furniture는 `Furniture.7-A` 단일 소분류로 유지한다.
  - Vehicle은 `Vehicle.8-A / Vehicle.8-B` 2분할로 유지한다.
  - `Misc.9-A`는 일반 classification rule이 아니라 output-stage fallback이다.
  - `Tool.1-K (Security)`와 `Tool.1-L (Storage)`는 정식 소분류다.
  - `Tool.1-L (Storage)`는 비착용 휴대 컨테이너를, `Wearable.6-F`는 착용 가능한 배낭을 담당한다.
  - `Consumable.3-B`의 음료 판정은 체감적 용도나 임의 수치 비교가 아니라 `Drink / Drainable` 선언 구조를 기준으로 한다.

- 영향:

  - classification coverage나 편의를 이유로 기존 category 책임 범위를 임의로 넓히지 않는다.

- 오독 금지:

  - Furniture 재세분화, Vehicle 과분할, `Misc` 일반 catch-all화 또는 Storage / Wearable 경계 확대를 자동 승인하지 않는다.
  - 미분류 발생 자체는 taxonomy 재설계나 Evidence 확대 근거가 아니다.
  - COMMON-RUNTIME-SURFACE-NONMUTATION.
  - COMMON-RELEASE-NONDECISION.

- Trace:

  - sealed: 2026-03-23 ~ 2026-03-25
  - COMMON-EVIDENCE-TRACE.

### Iris — item information hierarchy / Layer 3–4 responsibility boundary

- 상태: current readpoint / presentation-responsibility boundary aligned

- 결정: Iris Menu는 여러 information layer를 하나의 자연스러운 item page로 표시하되 presentation order를 각 layer의 semantic responsibility나 authority ownership과 혼동하지 않는다.

- 현재 기준:

  - 기본 presentation 흐름은 `기본 정보 -> 의미 / 설명 -> 개별 설명(조건부) -> 활용 -> 메타`다.
  - 이 순서는 user-facing presentation hierarchy이며 upstream / downstream authority chain이 아니다.
  - Layer 3 body production / omission은 DVF System production contract를 따른다.
  - Recipe / Right-click `use_case`와 requirement는 Layer 4 QG responsibility다.
  - Layer 4가 Menu에서 Layer 3 뒤에 배치되더라도 Layer 3 body의 일부나 DVF System authority로 흡수되지 않는다.
  - 각 information layer는 자기 responsibility를 가진 독립 정보층이다.
  - 대분류 / 소분류 / 아이템 목록은 browsing anchor다.
  - `primary_subcategory`는 navigation anchor이며 Layer 3 문장의 자동 semantic authority가 아니다.
  - classification ID, predicate, provenance와 debug metadata는 필요 시 meta 영역에 두고 기본 설명과 구분한다.
  - 추천, 효율 평가와 우열 비교는 하지 않는다.

- 영향:

  - 사용자에게는 하나의 item page로 보이면서도 각 information layer의 responsibility와 authority를 유지한다.

- 오독 금지:

  - presentation hierarchy를 semantic authority hierarchy로 읽지 않는다.
  - `primary_subcategory`, UI placement 또는 preceding block의 결과를 새로운 facts authority로 승격하지 않는다.
  - Layer 4 placement를 DVF System responsibility 흡수로 읽지 않는다.
  - COMMON-RUNTIME-SURFACE-NONMUTATION.
  - COMMON-RELEASE-NONDECISION.

- Trace:

  - initial hierarchy: 2026-03-16 ~ 2026-03-25
  - Layer 3 / Layer 4 responsibility alignment: successor readpoint
  - COMMON-EVIDENCE-TRACE.

### Iris DVF System — Layer 3 body production / optional role-material contract

- 날짜: predecessor body-production contract → 2026-08-21 role realignment → 2026-08-22 source-bound material correction

- 상태: current readpoint / successor production contract / optional role-material model adopted

- 결정: DVF System은 approved facts / decisions / profile / body-plan과 채택된 upstream content input을 소비해 Iris Layer 3 body를 오프라인에서 결정론적으로 생성·검증하며, 확인된 description-eligible material이 없는 item에는 본문을 강제로 생성하지 않는다.

- 현재 기준:

  - DVF System responsibility는 `approved inputs -> rendered Layer 3 body` production / verification으로 한정한다.
  - 의미 결정과 렌더링은 offline에서 수행하며 runtime Lua가 본문을 생성·판단·repair하지 않는다.
  - rendered body는 upstream facts와 decisions를 소비한 결과이며 DVF System이 새로운 facts authority를 생성하거나 upstream facts를 재판정하지 않는다.
  - Layer 3는 모든 item에 강제되는 상세 설명이 아니라 확인된 description-eligible material이 있을 때 제공하는 선택적 overview / explanation 계층이다.
  - 근거가 부족하면 identity, classification, acquisition, Layer 4 또는 rendered prose에서 의미를 보충하지 않고 침묵한다.
  - current existing body는 `keep / reduce / revise / hide / review_hold` 중 하나의 disposition을 가진다.
  - canonical FullType은 body 유무와 독립적으로 `description_ready / acquisition_only / omission_allowed / insufficient_material / review_required` 중 하나의 readiness를 가진다.
  - body disposition과 role-material readiness는 서로 다른 axis다.
  - fact kind와 role material은 exact source slot / provenance와 registered structured lineage를 기준으로 결정한다.
  - `cluster_summary`는 matching adopted Layer 3 decision lineage가 있을 때만 role material이 된다.
  - Layer 4 row나 rendered-string semantic parsing을 이용해 Layer 3 material을 새로 만들지 않는다.
  - `core_description`과 `acquisition_information`을 구분한다.
  - Source-bound acquisition conservation과 Menu public acquisition coverage는 서로 다른 set이다.
  - one-off item-page information sufficiency assessment는 Layer 3 semantic authority나 current sufficiency authority가 아니다.
  - predecessor assessment가 exact-current였던 시점에도 bounded per-item readiness prerequisite로만 사용할 수 있으며 top-level page disposition이나 Layer 4 axis를 Layer 3 body authority로 직접 변환하지 않는다.
  - successor generation 설치 뒤 predecessor sufficiency snapshot을 current claim으로 상속하지 않는다.
  - source-bound direct-use material이 확인되면 silent item을 public Layer 3 material로 전환할 수 있지만 Layer 4 row나 rendered prose를 새로운 source authority로 사용하지 않는다.

- 최소 결과 trace:

  - current Layer 3 universe: `2105`
  - current public Layer 3 bodies: `2072`
  - current silent rows: `33`
  - optional role-material model: `adopted`

- 후속 input artifact:

  - `Iris/build/description/v2/data/dvf_3_3_input_manifest.json`
  - current approved upstream candidate / generation input
  - `docs/iris_layer3_body_role_realignment_policy.md`

- Predecessor trace:

  - legacy manual registry / T-Gate / active-silent production model은 successor offline body-production contract에 의해 supersede됐다.
  - 2026-08-21 role realignment가 body disposition과 role-material readiness를 분리하고 Layer 3를 optional explanation layer로 재정렬했다.
  - one-off Item-Page Information Sufficiency 결과는 bounded predecessor snapshot으로만 소비됐다.
  - 2026-08-22 `Base.Bleach` / `Base.Rope`는 current repository의 직접 source evidence에 따라 `identity_fallback`에서 `direct_use` provenance로 보강됐다.
  - 두 correction은 non-target entry를 변경하지 않고 target 두 item만 silent에서 source-bound public role material로 전환해 public `2070 -> 2072`, silent `35 -> 33`을 만들었다.
  - exact branch token, source-specific predicate와 implementation / validation detail은 상세 evidence trace로 격하한다.

- 오독 금지:

  - optional Layer 3를 모든 item의 상세 설명 의무로 되돌리지 않는다.
  - body disposition과 role-material readiness를 같은 axis로 읽지 않는다.
  - acquisition information, Layer 4 row, classification 또는 rendered prose를 Layer 3 semantic authority로 승격하지 않는다.
  - two-item correction을 전체 Layer 3 facts truth audit로 확대하지 않는다.
  - predecessor sufficiency 분포를 successor generation의 current sufficiency 분포로 상속하지 않는다.
  - DVF System production / role-material completion을 RTC, Publish, package publication 또는 release readiness로 읽지 않는다.
  - COMMON-RUNTIME-SURFACE-NONMUTATION.
  - COMMON-RELEASE-NONDECISION.

- Trace:

  - successor body-production contract: predecessor cutover 이후
  - role realignment: 2026-08-21
  - source-bound material correction: 2026-08-22
  - COMMON-EVIDENCE-TRACE.

### Iris Layer 4 — Recipe / Right-click `use_case`, requirement / adaptive presentation contract

- 날짜: 2026-03-25 → 2026-08-21 adaptive presentation integration

- 상태: current readpoint / structured interaction contract retained / adaptive presentation adopted

- 결정: Layer 4는 Recipe와 Right-click을 독립적이고 동등한 Source로 유지하면서 확정된 Evidence를 구조화된 `use_case`와 requirement로 표현하고, status-bearing interaction state를 단일 Detail ViewModel 경계로 전달해 interaction density에 맞는 adaptive presentation으로 표시한다.

- 현재 기준:

  - Recipe와 Right-click은 잔여 필터 관계가 아닌 독립적이고 동등한 두 Source다.
  - 같은 item은 Recipe와 Right-click 양쪽의 `use_case`를 동시에 가질 수 있다.
  - Recipe Evidence는 `rule_id` 중심의 `recipe_evidence` 계약을 current 표준 경로로 사용한다.
  - UI에 행동 정보로 노출되는 `use_case`는 해당 Source에서 PASS로 확정된 Evidence를 기반으로 한다.
  - Right-click evidence와 exclusion은 구조적으로 분리하며 exclusion을 사용자 행동 정보로 승격하지 않는다.
  - Source 종류나 표시 문자열을 역파싱해 `use_case` 의미를 복원하지 않는다.
  - Recipe의 `consumed / keep / require`는 recipe-local role / requirement다.
  - `keep / require`는 item 자체의 행동 Evidence가 아니다.
  - recipe-local requirement를 FullType 전역 capability로 승격하지 않는다.
  - 동적으로 안전하게 확정할 수 없는 recipe expression은 임의 추론으로 닫지 않고 `review` 상태로 유지한다.
  - `use_case` 구조, requirement 상태와 표시문은 offline QG pipeline에서 확정한다.
  - 필수 label mapping이 없으면 fail-loud한다.
  - runtime Lua는 확정된 구조와 표시문을 UI state로 투영할 뿐 role이나 의미를 재해석하지 않는다.
  - status-bearing interaction state는 단일 Detail ViewModel 경계를 통해 presentation layer에 전달한다.
  - semantic interaction state와 compact / full / search 같은 presentation UI state는 분리한다.
  - 단일·소규모 interaction은 간결하게 표시하고, 고밀도 interaction은 compact / full 전환과 검색을 제공할 수 있다.
  - interaction density 차이는 표시 전략을 바꿀 수 있지만 Source / Evidence / `use_case` authority를 변경하지 않는다.
  - Recipe 제작 UI 이동은 existing recipe semantics를 변경하지 않는 presentation action이다.
  - item 전환 시 이전 item의 검색 / compact / full state를 새 item에 상속하지 않는다.
  - 기존 context menu / Wiki / Alt Tooltip surface 경계를 유지한다.
  - QG-only로 확인된 interaction도 Layer 4 contract가 충족되면 public row로 표시할 수 있다.

- 최소 결과 trace:

  - adaptive interaction presentation: `adopted`
  - semantic state / presentation state separation: `adopted`
  - QG-only current public rows: `3`
  - `Base.HammerStone` Right-click projection correction: `complete`

- Predecessor trace:

  - `classification_recipe` 중심 경로는 `rule_id` 중심 `recipe_evidence` 경로에 의해 supersede됐다.
  - Recipe-only / RightClick-only 잔여 필터 모델과 표시 문자열 역파싱 모델은 current 기준이 아니다.
  - 2026-08-21 adaptive-presentation lifecycle이 status-bearing interaction state를 Detail ViewModel 경계로 모으고 compact / full / search를 presentation concern으로 분리했다.
  - 같은 lifecycle에서 QG-only 세 item의 public Layer 4 row와 Stone Hammer의 누락된 Right-click projection이 반영됐다.
  - owner in-game acceptance와 exact manual-check item / merge / UI observation은 상세 evidence trace로 격하한다.

- 오독 금지:

  - adaptive presentation을 새로운 Evidence, `use_case` 또는 semantic authority 생성으로 읽지 않는다.
  - compact / full / search state를 classification, sorting 또는 다른 information layer의 policy input으로 전파하지 않는다.
  - QG-only public row를 Layer 3 fact나 일반 capability authority로 승격하지 않는다.
  - Recipe 제작 UI 이동을 Recipe semantics 변경으로 읽지 않는다.
  - owner in-game acceptance를 모든 fallback branch나 외부 모드 compatibility의 완전한 증명으로 확대하지 않는다.
  - 일회성 presentation 검사를 canonical validator나 regular validation authority로 승격하지 않는다.
  - COMMON-RUNTIME-SURFACE-NONMUTATION.
  - COMMON-RELEASE-NONDECISION.

- Trace:

  - QG structured interaction contract: 2026-03-25
  - adaptive presentation integration: 2026-08-21
  - COMMON-EVIDENCE-TRACE.

### Iris — Layer 2–3 locale projection contract

- 날짜: 2026-08-21 locale projection integration → 2026-08-22 current-generation key-set / material successor

- 상태: current readpoint / supported-locale projection adopted / current-generation key-set aligned

- 결정: 지원 locale에서는 번역 부재를 이유로 이미 알려진 Layer 2–3 정보를 숨기지 않으며, locale projection은 exact current semantic source와 pointer-selected current generation에 결속된 precompiled representation으로 제공한다.

- 현재 기준:

  - 지원 locale에서 번역 부재만을 이유로 확인된 Layer 2–3 정보를 숨기지 않는다.
  - predecessor EN-hide behavior는 current 기준이 아니다.
  - Layer 2는 동일한 `50`개 classification template ID에 KO / EN 문장을 제공한다.
  - locale 차이는 classification template identity나 classification semantics를 변경하지 않는다.
  - Layer 3 companion localization payload의 public-key owner는 predecessor rendered artifact가 아니라 pointer-selected current generation이다.
  - localization producer는 자신이 소비하는 current-generation canonical input과 approved candidate identity에 결속한다.
  - EN companion에는 current generation에서 non-empty KO public body를 가진 key만 포함한다.
  - current KO / EN Layer 3 public key set은 각각 `2072`다.
  - KO body와 source semantics는 localization projection 때문에 변경하지 않는다.
  - runtime은 요청 locale의 precompiled payload만 선택한다.
  - cross-locale raw-text fallback은 사용하지 않는다.
  - current Layer 3 entry가 없거나 current KO public body가 아닌 item은 stale EN entry가 존재하더라도 EN body를 독립적으로 공개하지 않는다.
  - EN lazy chunk / index는 presentation routing mechanics이며 semantic authority, fact inference 또는 별도 validation authority가 아니다.
  - item / locale 전환 시 이전 item의 interaction state나 이전 locale text를 다음 view에 남기지 않는다.

- 최소 결과 trace:

  - Layer 2 template identity: `50`
  - current KO public key set: `2072`
  - current EN public key set: `2072`
  - cross-locale raw-text fallback: `forbidden`

- Predecessor trace:

  - 2026-08-21 locale projection이 KO / EN presentation을 도입하고 EN-hide behavior를 폐기했다.
  - 2026-08-22 Blocker 6 correction은 EN public-key owner를 predecessor rendered artifact에서 pointer-selected current generation으로 이동했다.
  - stale EN-only `14`개 entry는 제거됐으며 correction 직후 KO / EN public set은 `2070`이었다.
  - 같은 날짜의 two-item Layer 3 material successor가 public Layer 3 set을 `2072`로 갱신했고 EN companion도 같은 key set으로 재생성됐다.
  - exact stale-entry list, package row / hash와 shell-specific validation result는 상세 evidence trace로 격하한다.

- 오독 금지:

  - predecessor `2070` key set을 current readpoint로 읽지 않는다.
  - locale projection을 새로운 사실 생성, 추천, 추론 또는 Layer 3 semantic authority 변경으로 읽지 않는다.
  - EN companion payload를 KO current source와 독립된 knowledge authority로 읽지 않는다.
  - key-set parity를 public-text quality acceptance나 번역 품질 PASS로 확대하지 않는다.
  - localization correction을 과거 Problem 4 `동결 불가` verdict의 소급 수정이나 새 freeze PASS로 읽지 않는다.
  - one-off localization producer / focused assertion을 canonical validator나 regular validation authority로 승격하지 않는다.
  - COMMON-RUNTIME-SURFACE-NONMUTATION.
  - COMMON-RELEASE-NONDECISION.

- Trace:

  - locale projection integration: 2026-08-21
  - current-generation key-set correction / material successor: 2026-08-22
  - COMMON-EVIDENCE-TRACE.

### Iris runtime — public API / Browser / Detail responsibility boundary

- 날짜: 2026-08-03 → 2026-08-11 projection refinement → 2026-08-25 responsibility refactor

- 상태: current readpoint / supported facade preserved / internal responsibility split adopted

- 결정: Iris runtime은 supported public API와 observable compatibility를 유지하면서 Browser, Detail, Description presentation과 legacy compatibility의 내부 책임을 분리한다.

- 현재 기준:

  - supported public API와 public `require` surface는 보존한다.
  - `phase0_supported_api_manifest.json`에 포함된 `IrisData`, `IrisBrowserData.build`, `IrisBrowserData.getGroupVariants`, Wiki render facade는 thin current compatibility surface다.
  - `StaticData.getLegacyIrisData`는 supported public surface가 아닌 internal implementation detail이며 current Iris product consumer는 없다.
  - `IrisData.lua`는 focused classification / variant group을 운반하는 thin table-identity adapter다.
  - Description, Browser, Detail과 legacy compatibility를 서로 다른 internal responsibility boundary로 유지한다.
  - Browser / Detail former monolith 책임은 projection / lifecycle / metrics와 fact-reader / assembler / presentation owner로 분리한다.
  - supported facade의 signature / observable result shape는 내부 책임 분리 때문에 변경하지 않는다.
  - item object identity와 supported public copy-on-read semantics를 보존한다.
  - Browser / Wiki Detail은 공통 read-only fact projection을 소비한다.
  - 같은 DisplayName에 대한 folding은 presentation-only이며 FullType, Source / Evidence 또는 artifact identity를 병합하지 않는다.
  - 같은 DisplayName이라는 이유만으로 variant가 semantic-equivalent하다고 추론하지 않는다.
  - Recipe / Moveables / Fixing의 unlisted no-op `build()` surface는 supported API로 승격하지 않고 제거할 수 있다.

- 최소 결과 trace:

  - supported public compatibility: `preserved`
  - Browser / Detail responsibility split: `adopted`
  - legacy internal helper public promotion: `none`

- 후속 input artifact:

  - `Iris/_docs/refactor/responsibility_repository_refactor/s0_baseline_adoption.json`
  - `Iris/_docs/refactor/responsibility_repository_refactor/successor_decision.json`
  - `Iris/_docs/refactor/responsibility_repository_refactor/current_migration_map.json`

- Predecessor trace:

  - 2026-08-03 runtime/API boundary와 public copy-on-read contract가 채택됐다.
  - 2026-08-11 Browser generation / locale projection owner와 presentation optimization boundary가 보강됐다.
  - 2026-08-25 responsibility refactor가 Browser / Detail owner를 추가 분리하고 `IrisData` thin adapter와 supported / unsupported surface 경계를 정리했다.
  - exact implementation commits와 facade-validation detail은 상세 evidence trace로 격하한다.

- 오독 금지:

  - DisplayName folding을 FullType / semantic identity 병합으로 읽지 않는다.
  - supported facade 보존을 deprecated internal helper의 public 승격으로 읽지 않는다.
  - internal responsibility refactor를 source facts / classification / semantic authority 변경으로 읽지 않는다.
  - COMMON-RUNTIME-SURFACE-NONMUTATION.
  - COMMON-RELEASE-NONDECISION.

- Trace:

  - runtime/API boundary: 2026-08-03
  - projection refinement: 2026-08-11
  - responsibility successor: 2026-08-25
  - COMMON-EVIDENCE-TRACE.

### Iris runtime — lazy-loading / cache / index integrity boundary

- 날짜: 2026-08-10 → 2026-08-11 refinement

- 상태: current readpoint / first-use and key-level loading adopted / index validity split

- 결정: Iris runtime은 public compatibility를 유지하면서 Browser, Layer 3, UseCase와 정적 데이터의 불필요한 eager / full-dataset materialization을 first-use와 key-level lookup으로 지연하고, 각 index가 자기 조회 계약에 필요한 validity를 독립적으로 유지하게 한다.

- 현재 기준:

  - Browser 전체 build는 실제 Browser consumer의 first-use에서 materialize할 수 있다.
  - Browser row / ordering source와 derived cache는 `(generation, normalizedLocale)` owner를 가진다.
  - locale / generation mismatch에서는 완성된 successor projection으로 교체하고 관련 derived cache를 함께 무효화한다.
  - prefix query마다 동일한 global ordering을 반복 계산하지 않는다.
  - Layer 3와 UseCase lookup은 deterministic index / router를 통해 필요한 key의 chunk만 demand-load한다.
  - boot 시 즉시 필요하지 않은 static information module은 supported compatibility contract를 보존하는 범위에서 first-use loading으로 이동할 수 있다.
  - normal absent key와 malformed / inconsistent package / index / target identity를 구분한다.
  - 검증된 absent key는 corruption이나 global facade fallback 조건이 아니다.
  - index / line-count / routing metadata는 presentation mechanics이며 semantic authority가 아니다.
  - UseCase ChunkIndex와 LineCountIndex는 module require 시 강제로 materialize하지 않고 first-use에서 validation state를 완성할 수 있다.
  - ChunkIndex validity와 LineCountIndex validity는 독립 state를 유지한다.
  - 두 index 사이 관계는 별도 cross-check / consistency state로 관리한다.
  - valid LineCountIndex는 unrelated ChunkIndex failure 때문에 정상 line-count 조회를 전역 차단하지 않는다.
  - UseCase line-count 조회는 description body materialization과 분리한다.
  - derived display cache는 current locale / revision ownership을 벗어난 stale entry를 authority처럼 유지하지 않는다.

- 최소 결과 trace:

  - Browser first-use loading: `adopted`
  - Layer 3 / UseCase key-level loading: `adopted`
  - generation / normalized-locale cache ownership: `adopted`
  - ChunkIndex / LineCountIndex independent validity: `adopted`

- Predecessor trace:

  - 2026-08-10 Browser eager build와 full-dataset lookup을 first-use / key-level routing으로 전환했다.
  - 2026-08-11 codebase optimization follow-up이 generation-local row, cache-owner invalidation과 UseCase index validity split을 보강했다.
  - 당시 session-reset candidate, Tooltip static projection, compact adapter 등 채택되지 않은 후보와 exact validation / byte proxy는 상세 evidence trace로 격하한다.

- 오독 금지:

  - lazy initialization을 validation 생략으로 읽지 않는다.
  - 하나의 index failure를 unrelated lookup contract 전체의 global invalidity로 자동 승격하지 않는다.
  - normal absent key를 corruption으로 읽지 않는다.
  - index / cache / routing metadata를 facts 또는 classification authority로 읽지 않는다.
  - first-use / allocation 감소를 PZ latency, heap, FPS / frame-time 향상으로 자동 승격하지 않는다.
  - COMMON-RELEASE-NONDECISION.

- Trace:

  - lazy-loading adoption: 2026-08-10
  - index / cache refinement: 2026-08-11
  - COMMON-EVIDENCE-TRACE.

### Iris runtime — pure-Lua engine-object access boundary

- 날짜: 2026-08-11

- 상태: current readpoint / pure-Lua eligibility surface adopted / generic production routing not adopted

- 결정: Iris runtime의 engine-object access는 Project Zomboid가 Kahlua의 표준 Lua 환경에 이미 노출한 객체를 Lua에서 소비하는 범위로 한정하며 JVM / JAR / Mixin / 직접 Java bridge를 추가하지 않는다.

- 현재 기준:

  - Iris runtime 구현은 Lua surface 안에서 유지한다.
  - `engine-bound object`는 Iris가 자체 Java bridge를 여는 객체가 아니라 PZ가 Kahlua 표준 Lua API로 이미 노출한 engine object를 뜻한다.
  - ScriptManager / Java collection 계열처럼 Lua에 노출된 object의 method / self binding을 다루는 pure-Lua helper를 둘 수 있다.
  - `IrisObjectAccess.call0/call1`은 eligibility / compatibility helper이며 JVM integration layer가 아니다.
  - helper의 존재만으로 모든 engine-object invocation을 generic production routing으로 전환하지 않는다.
  - generic production routing을 채택하려면 representative PZ Kahlua engine-object에 대한 actual functional evidence가 필요하다.
  - representative evidence가 없는 branch는 `unvalidated_but_in_scope`로 유지하며 existing production routing을 대체하지 않는다.
  - object-access helper는 source / Evidence / classification을 생성하지 않는다.
  - engine-object access abstraction은 runtime mechanics이며 semantic authority가 아니다.

- 최소 결과 trace:

  - pure-Lua object-access eligibility: `adopted`
  - direct JVM / JAR / Mixin bridge: `not adopted`
  - generic production routing: `not adopted`
  - representative PZ functional evidence: `pending`

- Predecessor trace:

  - 2026-08-11 codebase optimization follow-up이 `IrisObjectAccess.call0/call1`을 pure-Lua eligibility surface로 추가했다.
  - representative PZ engine-object functional evidence가 없어 generic production routing은 채택되지 않았다.
  - 당시 implementation lifecycle의 `partial` 상태는 이 미채택 branch를 포함한 round-local closeout 상태이며 current runtime family 전체의 상태가 아니다.

- 오독 금지:

  - Kahlua가 Java-backed object를 노출한다는 사실을 Iris가 JVM / Java bridge를 포함한다는 뜻으로 읽지 않는다.
  - helper eligibility를 generic production-routing validation으로 승격하지 않는다.
  - method availability를 item semantic capability의 완전한 증명으로 읽지 않는다.
  - COMMON-RUNTIME-SURFACE-NONMUTATION.
  - COMMON-RELEASE-NONDECISION.

- Trace:

  - pure-Lua object-access adoption: 2026-08-11
  - COMMON-EVIDENCE-TRACE.

### Iris runtime — global compatibility patch retirement / non-interference boundary

- 날짜: 2026-08-25

- 상태: current readpoint / behavior-changing global patches retired / compatibility claim bounded

- 결정: Iris가 설치하던 bullet reload replacement와 context-menu texture render wrapper는 대체 구현 없이 제거하고, current Iris runtime compatibility claim을 supported facade 보존과 Iris의 global-function non-interference 범위에 한정한다.

- 현재 기준:

  - bullet reload replacement는 Iris current runtime responsibility가 아니다.
  - context-menu texture render wrapper는 Iris current runtime responsibility가 아니다.
  - 두 global patch는 대체 구현 없이 제거한다.
  - 삭제한 기능을 Pulse, Nerve, 다른 spoke 또는 공통 helper로 이전하지 않는다.
  - current Iris runtime은 기존 게임 / 외부 모드 global function을 Iris가 덮어써서 compatibility를 보장하는 구조를 기본값으로 사용하지 않는다.
  - arbitrary external-mod combination compatibility는 `unvalidated_but_in_scope`다.
  - bounded Iris-only manual probe는 supported PZ surface의 명백한 회귀 탐지 evidence일 뿐 모든 외부 모드 조합의 compatibility certification이 아니다.

- 최소 결과 trace:

  - retired behavior-changing global patches: `2`
  - supported facade compatibility: `preserved`
  - arbitrary external-mod compatibility: `unvalidated_but_in_scope`

- Predecessor trace:

  - predecessor Iris는 bullet reload replacement와 context-menu texture render wrapper를 설치했다.
  - 2026-08-25 responsibility refactor가 두 patch를 제거하고 Iris compatibility scope를 non-interference 쪽으로 축소했다.
  - CheatMenuRebirth 동시 활성화에서는 vanilla `ISContextMenu.render`의 null `tickTexture` 오류가 관측됐지만 arbitrary external-mod compatibility verdict로 승격하지 않았고 삭제한 Iris render patch를 복원하는 근거로 사용하지 않았다.
  - exact manual-probe checklist와 implementation commits는 상세 evidence trace로 격하한다.

- 오독 금지:

  - external-mod coexistence incident를 모든 외부 모드 compatibility의 PASS 또는 FAIL로 일반화하지 않는다.
  - removed patch를 복원하거나 다른 Pulse spoke로 이전하는 decision으로 읽지 않는다.
  - manual probe를 multiplayer / long-session / arbitrary-mod compatibility completion으로 확대하지 않는다.
  - global patch retirement를 PZ 자체 defect 해결 claim으로 읽지 않는다.
  - COMMON-RELEASE-NONDECISION.

- Trace:

  - patch retirement / non-interference boundary: 2026-08-25
  - COMMON-EVIDENCE-TRACE.

### Iris — stateless generation / current runtime payload / package projection boundary

- 날짜: 2026-08-20 → 2026-08-21 role-material installation → 2026-08-22 successor generation → 2026-08-25 package projection refinement

- 상태: current readpoint / Stateful IAR product retirement complete / stateless generation model active / current-generation-only package projection adopted

- 결정: Iris의 current product artifact generation과 runtime visibility는 stateful Artifact Registry lifecycle이 아니라 **canonical raw-byte generation input + generation-qualified immutable module set + 단일 current pointer**로 관리한다.

- 현재 기준:

  - Layer 1–5 active product Stateful IAR consumer는 `0`이다.
  - product generation identity는 canonical compose input, adopted upstream content candidate의 raw bytes, generator / serializer / chunking identity와 ordered output universe에서 파생한다.
  - current rendered artifact, runtime payload 또는 descriptor를 generation input으로 사용하지 않는다.
  - descriptor는 authority / adoption token이 아니다.
  - authorization, installer state, attempt, transaction, nonce, receipt, owner seal, absolute path와 wall-clock time을 generation identity에 포함하지 않는다.
  - Layer 3 role-material successor는 approved upstream candidate로 canonical generation input에 명시적으로 포함한다.
  - current generation route는 기존 six compose input과 adopted upstream candidate를 결속한 canonical seven-input model을 따른다.
  - staging successor completion 자체는 current mutation이 아니다.
  - current mutation은 별도 authorization 아래 official generation / installer path가 exact adopted input을 소비하고 current pointer를 전환할 때만 성립한다.
  - runtime public module `Iris/Data/IrisLayer3DataChunks`는 stable facade로 유지한다.
  - generation-qualified immutable module set을 설치한 뒤 `IrisLayer3DataCurrent.lua` 하나를 visibility pointer로 사용한다.
  - stable facade와 chunk index는 같은 pointer를 소비한다.
  - installer는 pointer 전환 전 expected predecessor generation identity에 결속한다.
  - predecessor / inactive generation은 rollback / predecessor source로 보존할 수 있지만 active product dependency나 current package authority가 아니다.
  - same-generation reinstall은 protected content mutation이나 visibility switch가 필요하지 않으면 no-op이다.
  - `current_runtime_payload` package는 current pointer가 선택한 generation root와 canonical raw-byte universe를 소비한다.
  - package lookup identity는 canonical ordinal ordering에 결속한다.
  - legacy stateful descriptor fallback은 current package path에서 사용하지 않는다.
  - current pointer 부재, 오염, generation mismatch 또는 ambiguous applicability는 fail-closed한다.
  - current package projection은 current pointer가 선택한 Layer 3 generation 하나만 포함한다.
  - inactive generation과 legacy fixed payload source를 current package에서 제외할 수 있지만 그 자체로 predecessor source 삭제를 승인하지 않는다.

- 최소 결과 trace:

  - Stateful IAR active product consumers: `0`
  - product retirement state: `FULL_RETIREMENT`
  - canonical generation input: `7 inputs`
  - current generation: `dvf33-028a396886eee3ed9bbb6f610c64c8e886ac3e3aab7b8c7381d5d4a48d7145e9`
  - current visibility: `immutable generation + single pointer`
  - package projection: `current Layer 3 generation only`
  - legacy stateful fallback: `removed`

- 후속 input artifact:

  - `Iris/media/lua/client/Iris/Data/IrisLayer3DataCurrent.lua`
  - current approved upstream candidate / generation input
  - `Iris/_docs/round3/iar_stateful_architecture_retirement/`

- Predecessor trace:

  - 2026-08-20 Stateful IAR retirement가 stateful product consumers를 `0`으로 닫고 immutable-generation / pointer model을 채택했다.
  - 2026-08-21 role-material successor가 predecessor generation에서 새 generation으로 current pointer를 전환했다.
  - 2026-08-22 two-item material correction은 같은 seven-input model로 successor generation `dvf33-028a...`를 생성·검증하고 predecessor `dvf33-aa138...`에서 pointer를 전환했다.
  - EN companion과 package lookup identity도 이 successor generation의 public key set에 맞춰 갱신됐다.
  - 2026-08-25 responsibility / repository refactor는 package projection을 current generation 하나로 한정하고 inactive generations와 legacy fixed payload를 package에서 제외했다.
  - package exclusion은 source predecessor 삭제가 아니며 exact predecessor generation / lookup IDs와 validation result는 상세 evidence trace로 격하한다.

- 오독 금지:

  - staging candidate completion을 current mutation이나 adoption으로 읽지 않는다.
  - predecessor generation을 current runtime fallback authority로 읽지 않는다.
  - current generation / package identity PASS를 RTC certification으로 읽지 않는다.
  - current pointer switch의 관측 성공을 filesystem-level atomicity theorem으로 승격하지 않는다.
  - package projection 경량화를 repository-wide lightweighting이나 source predecessor retirement로 확대하지 않는다.
  - package identity / installation completion을 Publish PASS, release / Workshop / deployment readiness로 읽지 않는다.
  - COMMON-RELEASE-NONDECISION.

- Trace:

  - Stateful IAR retirement: 2026-08-20
  - role-material installation: 2026-08-21
  - current generation successor: 2026-08-22
  - package projection refinement: 2026-08-25
  - COMMON-EVIDENCE-TRACE.

### Iris — artifact role / repository placement / predecessor reentry boundary

- 날짜: predecessor artifact-governance lifecycle → 2026-08-10 repository placement adoption → 2026-08-20 Stateful IAR retirement → 2026-08-24 retirement-domain completion → 2026-08-25 repository refinement → 2026-08-26 current/historical physical separation

- 상태: current readpoint / authority-role and physical-representation separation retained / selected historical source hold replaced by verified external archive

- 결정: artifact의 authority / lifecycle role과 VCS / physical representation을 분리하고 Repository는 actual consumer와 reconstruction requirement를 기준으로 durability와 placement를 결정한다. Package placement는 stateless generation / package projection contract를 따르며, package 경량화를 repository-wide lightweighting이나 source predecessor retirement로 확대하지 않는다.

- 현재 기준:

  - `tracked / ignored / generated`는 VCS / representation state이며 artifact authority 자체가 아니다.
  - tracked artifact를 자동 current authority로 승격하지 않는다.
  - ignored / untracked artifact를 자동 deletable / non-current artifact로 판정하지 않는다.
  - current authority, current-required evidence, staging, historical reproduction, diagnostic, fixture, quarantine / predecessor role을 구분한다.
  - tracked repository, dirty-main ignored / untracked material과 external archive는 서로 다른 physical evidence domain이다.
  - physical representation 변경은 semantic / authority role을 자동 변경하지 않는다.
  - confirmed-current dirty-local source는 canonical tracked representation으로 정렬할 수 있다.
  - historical / evidence role은 executable source 형태의 영구 보존을 자동 요구하지 않는다.
  - current consumer나 reproduction obligation이 없으면 compact sealed evidence, external durable evidence 또는 reference representation을 사용할 수 있다.
  - discoverable locator가 없는 historical archive / restore reference를 current durable evidence로 간주하지 않는다.
  - owner waiver는 존재하지 않는 archive / source / restore evidence를 소급 생성하지 않는다.
  - dirty-main historical observation은 canonical tracked retirement metric에 합산하지 않는다.
  - current package placement / predecessor package exclusion은 stateless generation / package projection contract를 따른다.
  - inactive generation과 legacy fixed payload source는 package output authority가 아니더라도 predecessor / rollback / bootstrap source로 보존할 수 있다.
  - package에서 predecessor payload를 제외했다는 사실은 source deletion authority가 아니다.
  - package projection byte 감소와 repository 전체 tracked-byte 변화는 별도 metric domain이다.
  - repository-wide lightweighting은 net repository evidence가 실제 감소를 보일 때만 주장한다.
  - current clean-checkout closure는 current source/runtime/tooling/contracts와 bounded `current_required_v1` capsule만 보유하고 historical staging, predecessor attempts, inactive Layer 3 payload는 verified external content-addressed archive가 소유한다.
  - current gate와 package route는 external archive를 읽거나 자동 restore하지 않으며 historical reproduction만 explicit verify/restore command를 사용한다.
  - selected historical payload의 physical deletion은 archive create/verify/restore와 synthetic pre-delete gate가 먼저 PASS한 경우에만 허용한다.

- 최소 결과 trace:

  - authority role / VCS separation: `adopted`
  - tracked / dirty-main / external domain separation: `required`
  - selected predecessor source hold: `externalized_after_verified_archive`
  - repository-wide byte lightweighting claim: `established for the adopted Iris scope`

- Predecessor trace:

  - 2026-08-10 role-based physical placement과 external / compact representation 원칙이 채택됐다.
  - 2026-08-20 Stateful IAR retirement는 active product lifecycle을 제거했지만 repository governance와 predecessor evidence를 제거하지 않았다.
  - 2026-08-24 temporary-validation retirement는 tracked canonical state와 dirty-main historical domain을 분리해 완료됐다.
  - 2026-08-25 responsibility / repository refactor는 inactive generations와 legacy fixed chunks를 current package projection에서 제외했지만 source predecessor hold는 유지했다.
  - 같은 lifecycle에서 tracked repository 전체 blob은 순증가했으므로 repository-wide byte lightweighting이나 무차별 full-scan context 절감을 성과로 채택하지 않았다.
  - package-byte reduction, tracked-Lua byte / line delta와 repository-wide exact byte measurement은 상세 evidence trace로 격하한다.
  - 2026-08-26 physical separation은 verified external archive/restore를 먼저 고정한 뒤 tracked historical payload 3,804 files / 607,432,467 bytes와 별도 local-custody archived payload 1,266 files / 202,231,050 bytes를 제거했다. 두 domain은 중복 합산하지 않는다.
  - exact implementation subject `801f15f678fe9c5fd67be0f805f29ed3ba9db9b3`의 terminal current capsule은 133,094 bytes로 2,359,296-byte ceiling 이내이며 repository-local successor overhead는 1,653,400 bytes로 3,037,162-byte ceiling 이내다.
  - terminal local-custody correction은 W0 이후 변경되지 않은 ignored legacy 295 files / 4,273,310 bytes를 additive external archive successor에 create/verify/restore한 뒤 제거했고, regenerable pipeline log 2 files / 3,205 bytes도 별도 판정 후 제거했다. 기존 archive와 removal domain은 rewrite하거나 이 수치와 중복 합산하지 않는다.

- 오독 금지:

  - package payload 감소를 전체 repository, ZIP 또는 source footprint 감소율로 읽지 않는다.
  - package projection에서 제외됐다는 사실을 predecessor source 삭제 승인으로 확대하지 않는다.
  - repository-wide lightweighting이 성립하지 않은 상태에서 package byte 감소를 LLM / Codex context 절감으로 환산하지 않는다.
  - repository byte 감소를 실제 tokenizer 사용량, clone time, runtime timing, heap, FPS / frame-time 개선률로 환산하지 않는다.
  - physical-byte / LOC 감소를 PZ timing, heap, FPS / frame-time 또는 실제 GPT / Codex token 개선률로 자동 환산하지 않는다.
  - Git main integration이나 package generation을 Publish / release / Workshop / deployment readiness로 읽지 않는다.
  - COMMON-RUNTIME-SURFACE-NONMUTATION.
  - COMMON-RELEASE-NONDECISION.

- Trace:

  - repository placement adoption: 2026-08-10
  - Stateful IAR retirement alignment: 2026-08-20
  - retirement physical-domain completion: 2026-08-24
  - responsibility / repository refinement: 2026-08-25
  - current/historical physical separation: 2026-08-26
  - archive authority: `Iris/validation/clean_checkout/authority/iris_historical_archive_v1.json`
  - removal authority: `Iris/validation/clean_checkout/authority/iris_historical_removal_v1.json`
  - COMMON-EVIDENCE-TRACE.

### Iris — DVF / artifact identity / RTC / Publish claim separation

- 상태: current readpoint / responsibility boundaries retained after Stateful IAR retirement

- 결정: Layer 3 body production, product artifact generation / identity, runtime compatibility와 publish / release acceptance는 서로 독립된 responsibility와 claim axis로 유지하며 어느 하나의 PASS를 다른 축의 PASS로 확대하지 않는다.

- 현재 기준:

  - `DVF System`은 Layer 3 body-production system이다.
  - `DVF Body Compiler`는 DVF System의 body-production responsibility를 claim / validation 수준에서 좁게 지칭하는 canonical role name이다.
  - current product artifact identity / lifecycle은 stateless generation / current-pointer contract가 소유한다.
  - Stateful `Iris Artifact Registry`는 current active product component가 아니라 predecessor governance mechanism이다.
  - Registry Runtime Compatibility에서 유래한 runtime compatibility axis는 exact key / projection compatibility를 판정하는 별도 claim family로 유지한다.
  - Publish Boundary는 public-text acceptance, semantic-quality acceptance, package publication, release / Workshop readiness와 manual QA를 별도 claim axis로 관리한다.
  - `DVF Body Compiler PASS`, product artifact identity PASS, Runtime Compatibility PASS, Publish Boundary PASS는 서로 대체하지 않는다.
  - bare `DVF PASS`와 bare `DVF System PASS`는 current claim으로 사용하지 않는다.
  - `DVF System Body Compiler PASS`는 `DVF Body Compiler PASS`의 expanded alias일 뿐 system-wide completion claim이 아니다.
  - `Publish Boundary PASS`는 해당 readpoint가 요구하는 publish / acceptance component를 모두 충족한 conjunctive claim일 때만 사용한다.
  - current `current_route_required_validations.json`이 여러 responsibility 검사를 묶더라도 manifest membership을 responsibility ownership으로 읽지 않는다.
  - lexical / claim guard는 governance overclaim을 막을 수 있지만 semantic review나 public-text acceptance를 수행하지 않는다.

- 후속 input artifact:

  - `Iris/_docs/round3/current_route_required_validations.json`
  - `docs/dvf_3_3_dvf_system_naming_realignment_policy.md`
  - `docs/dvf_3_3_dvf_system_naming_realignment_claim_boundary.md`

- Predecessor trace:

  - Legacy Combined DVF Governance Route는 body production과 Registry governance가 함께 실려 있던 historical container다.
  - `DVF Core`는 predecessor terminology이며 current canonical name이 아니다.
  - Stateful IAR의 5-layer artifact-governance responsibility는 2026-08-20 product retirement 이후 current product architecture로 읽지 않는다.
  - 과거 Registry Authority / consumer migration / cutover lifecycle의 claim은 historical governance trace로 보존한다.

- 오독 금지:

  - body compiler PASS를 artifact adoption, compatibility, Publish 또는 release readiness로 읽지 않는다.
  - artifact generation identity PASS를 RTC certification이나 public-text acceptance로 읽지 않는다.
  - Runtime Compatibility PASS를 DVF body-production이나 Publish PASS로 읽지 않는다.
  - COMMON-RELEASE-NONDECISION.
  - COMMON-RUNTIME-SURFACE-NONMUTATION.

- Trace:

  - responsibility split predecessor lifecycle
  - DVF naming realignment successor
  - Stateful IAR retirement alignment: 2026-08-20
  - COMMON-EVIDENCE-TRACE.

### Iris Runtime Compatibility — exact-key identity / defect-attribution boundary

- 날짜: 2026-08-01 → 2026-08-20 stateless generation alignment

- 상태: current contract / exact-key compatibility boundary retained / stateless generation-key validation adopted / current RTC PASS not newly asserted

- 결정: Runtime Compatibility는 source에서 rendered / runtime / package projection까지 exact key identity를 보존하고 consumer별 comparison semantics 차이로 인한 병합·덮어쓰기·유실을 차단하는 독립 contract로 유지한다. Stateless generation의 key-identity validation은 이 contract를 보조하지만 full Runtime Compatibility certification과 동일하지 않다.

- 현재 기준:

  - source → rendered artifact → runtime payload → package projection은 동일한 exact key universe를 보존해야 한다.
  - Lua의 exact / case-sensitive identity와 Windows 계열 consumer의 case-insensitive comparison identity를 서로 다른 개념으로 취급한다.
  - case-insensitive collision은 기본적으로 fail-closed한다.
  - 의도적인 case-variant 공존은 explicit policy와 각 exact entry를 손실 없이 표현할 수 있는 consumer representation이 함께 있을 때만 허용한다.
  - 허용된 collision도 alias, rename, winner selection 또는 semantic equivalence를 뜻하지 않는다.
  - exact case-variant identity를 보존할 수 없는 consumer에서는 lossless record representation을 사용한다.
  - stateless `generation_key_identity_validation`은 exact key, ASCII-lower collision과 rendered / runtime payload projection identity를 검증한다.
  - `generation_key_identity_validation`은 product generation contract의 validation claim이며 기존 Registry Runtime Compatibility PASS나 current RTC certification을 대체하지 않는다.
  - package lookup identity의 ordering은 ordinal semantics로 고정한다.
  - package digest / identity는 shell culture, locale-sensitive sorting 또는 hash-set enumeration order에 의존하지 않는다.
  - 서로 다른 shell environment에서도 동일 exact-key universe가 같은 canonical ordering / identity를 가져야 한다.
  - compatibility violation은 downstream projection을 fail-closed할 수 있지만 source item spelling이나 semantic identity를 임의 수정할 권한을 만들지 않는다.
  - evidence / tooling freshness와 current identity defect는 별도로 판정한다.
  - temporary script, staging / worktree failure, implementation-toolchain freshness 문제 또는 단순 path / hash drift만으로 RTC debt를 선언하지 않는다.
  - successor RTC correction lifecycle은 canonical current runner / package failure와 current identity defect가 구체적인 runtime / package effect에 결속될 때만 연다.
  - defect attribution이 성립하지 않았다는 사실은 current RTC PASS가 아니다.
  - current coordination state `stale_requires_successor_rtc`는 별도 successor RTC claim이 닫히기 전까지 coordination marker로 유지한다.

- 최소 결과 trace:

  - exact-key compatibility contract: `retained`
  - stateless generation-key validation: `adopted`
  - package key ordering: `ordinal`
  - shell-dependent identity divergence: `forbidden`
  - canonical successor RTC defect attribution: `not established`
  - current RTC PASS: `not newly asserted`
  - RTC coordination: `stale_requires_successor_rtc`

- Predecessor trace:

  - 초기 RTC contract는 exact key universe와 case-insensitive collision fail-closed 원칙을 봉인했다.
  - 2026-07-29 Food Semantic Facts adoption 이후 successor RTC coordination 필요 상태가 기록됐다.
  - 2026-08-01 defect-attribution gate는 temporary tooling이나 path / hash drift만으로 current RTC debt를 선언하는 해석을 거부했다.
  - 2026-08-20 Stateful IAR retirement lifecycle에서 package lookup identity divergence가 발견됐고 shell별 culture-sensitive ordering 차이로 귀속됐다.
  - successor correction은 canonical ordinal ordering을 도입했지만 그 성공을 full RTC certification으로 승격하지 않았다.
  - exact implementation subject, reviewer finding, shell command와 digest evidence는 상세 evidence trace로 격하한다.

- 오독 금지:

  - `generation_key_identity_validation` PASS를 current RTC certification으로 읽지 않는다.
  - current-runtime package identity PASS를 RTC certification과 동일시하지 않는다.
  - temporary tooling failure나 predecessor bundle drift를 current RTC defect로 자동 승격하지 않는다.
  - canonical defect attribution이 없는 상태를 임의로 RTC PASS 또는 RTC debt로 판정하지 않는다.
  - predecessor RTC PASS를 current certification으로 재봉인하지 않는다.
  - ordinal package identity 정렬을 source semantic identity 수정 권한으로 읽지 않는다.
  - Runtime Compatibility contract를 Publish PASS, package publication 또는 release readiness와 동일시하지 않는다.
  - COMMON-RELEASE-NONDECISION.
  - COMMON-RUNTIME-SURFACE-NONMUTATION.

- Trace:

  - RTC contract predecessor seal
  - defect-attribution refinement: 2026-08-01
  - stateless generation / package-ordering alignment: 2026-08-20
  - COMMON-EVIDENCE-TRACE.

### Iris facts authority — Food Semantic Facts current adoption

- 날짜: 2026-07-29

- 상태: current facts readpoint / successor facts authority adopted

- 결정: 식품 의미 사실이 과도하게 단일 의미 조건으로 수렴하던 문제는 Evidence Allowlist, row-level lineage, closed food-semantic schema, automatic mapping과 explicit curated approval을 통해 successor facts로 재구축하고 해당 exact successor를 current facts authority로 채택한다.

- 현재 기준:

  - 대상 식품 `317`개에 대해 `718`개 approved proposition과 `17`개 meaningful semantic partition을 유지한다.
  - automatic proposition `84`개와 explicitly approved curated proposition `634`개는 provenance를 구분한다.
  - unsupported fact, arbitrary inference, Layer 4 automatic promotion, compiler-invented proposition과 dropped proposition을 허용하지 않는다.
  - successor generation과 current facts adoption은 서로 다른 lifecycle role이다.
  - adopted current facts를 downstream Layer 3 production이 소비할 수 있지만 임의 재구축하거나 재판정하지 않는다.
  - current facts / manifest에서 ambiguity, partial-current 또는 dual-current authority를 허용하지 않는다.
  - facts-authority completion은 rendered prose quality, RTC와 Publish acceptance에서 독립적이다.

- 최소 결과 trace:

  - target items: `317`
  - approved propositions: `718`
  - semantic partitions: `17`
  - automatic / curated: `84 / 634`
  - unsupported / arbitrary / invented / dropped: `0`

- Predecessor trace:

  - G2는 replacement facts candidate를 sealed non-current successor로 만들었다.
  - G3가 exact successor를 current facts로 채택했다.
  - 당시 Naturalization pending과 RTC coordination은 후속 lifecycle에 의해 소비됐다.
  - 당시 IAR adoption terminology는 product Stateful IAR retirement 이후 historical mechanism으로 읽는다.

- 오독 금지:

  - facts adoption을 rendered prose quality, RTC 또는 Publish PASS로 확대하지 않는다.
  - COMMON-RUNTIME-SURFACE-NONMUTATION.
  - COMMON-RELEASE-NONDECISION.

- Trace:

  - current facts adoption: 2026-07-29
  - COMMON-EVIDENCE-TRACE.

### Iris public-text assessment — reusable evaluator boundary

- 날짜: 2026-08-01

- 상태: current reusable assessment capability / authority effect none

- 결정: Iris의 public-text assessment는 특정 Naturalization attempt에 종속된 일회성 검사로 두지 않고 여러 subject가 재사용할 수 있는 generic no-write evaluator로 유지한다. Evaluator는 assessment evidence를 생성·검증할 뿐 public-text acceptance나 publication authority를 갖지 않는다.

- 현재 기준:

  - evaluator contract / runner / no-write validator는 reusable assessment capability로 관리한다.
  - subject-specific assessment result와 generic evaluator dependency를 분리한다.
  - downstream consumer가 기존 result를 재사용할 때는 exact result identity에 결속한다.
  - result 재사용을 위해 candidate를 재생성하거나 assessment를 재계산할 필요는 없다.
  - evaluator PASS는 assessment contract 만족을 뜻하며 semantic acceptance / publication decision이 아니다.
  - public-text assessment implementation은 product facts authority를 변경하지 않는다.

- 최소 결과 trace:

  - reusable evaluator: `validated / integrated`
  - authority effect: `none`

- Predecessor trace:

  - 2026-08-01 Naturalization quality lifecycle은 exact evaluator result를 no-write로 소비해 implementation / quality assessment를 닫았다.
  - 이후 Layer 3 runtime adoption과 role realignment는 별도 successor lifecycle이다.
  - attempt-specific Naturalization terminal / Publish clauses는 historical / non-executable로 격하됐다.

- 오독 금지:

  - evaluator PASS를 Publish Boundary PASS나 public-text acceptance로 읽지 않는다.
  - subject-specific result를 facts / rendered / runtime authority로 자동 승격하지 않는다.
  - COMMON-RUNTIME-SURFACE-NONMUTATION.
  - COMMON-RELEASE-NONDECISION.

- Trace:

  - reusable evaluator integration: 2026-08-01
  - COMMON-EVIDENCE-TRACE.

### Iris validation — regular authority boundary / historical evidence separation / executable retirement

- 날짜: 2026-06-11 → 2026-08-23 authority census / survival adjudication → 2026-08-24 physical retirement completion / main integration → 2026-08-25 boundary consolidation

- 상태: current readpoint / temporary-one-off physical retirement complete / regular authority boundary consolidated

- 결정: Iris의 live validation authority는 독립적인 current product contract 또는 recurring validation-system contract를 보호하는 검사만 regular로 유지한다. Census, taxonomy, manifest, discovery와 predecessor membership은 discovery / classification evidence일 뿐 survival authority가 아니며 lifecycle-bound executable은 current execution obligation이 없으면 퇴역한다.

- 현재 기준:

  - current validation은 current authority와 production contract가 요구하는 surface를 검증한다.
  - historical / diagnostic 결과를 current 결과와 상호 대체하거나 세탁하지 않는다.
  - historical / diagnostic raw FAIL이나 finding을 current PASS로 rewrite하지 않는다.
  - predecessor census, sealed receipt와 Git history의 보존은 repository-local executable replay route 존속을 요구하지 않는다.
  - repository-local `historical / diagnostic / all` executable selector와 corpus materialization route는 retired다.
  - live validation surface는 `current` selector와 fail-closed current contract를 유지한다.
  - regular membership은 survival authority를 자기 승인할 수 없다.
  - taxonomy, required manifest, pytest discovery, regular gate, predecessor ledger와 기존 disposition은 discovery / binding evidence다.
  - regular test 존속은 exact current contract, recurring execution obligation, lifecycle independence와 non-duplication을 요구한다.
  - lifecycle-only / migration / roadmap / defect / closeout / one-off 검사는 membership만으로 존속하지 않는다.
  - regular / non-current contract가 한 source에 섞여 있으면 current contract를 보존하고 non-current callable은 독립 disposition할 수 있다.
  - dirty-local에만 존재해도 current product contract가 확인된 validation source는 retirement 대상이 아니라 canonical tracked representation으로 복구할 수 있다.
  - canonical-presence correction은 contract authority를 새로 생성하는 것이 아니라 이미 확인된 current contract의 physical representation을 정렬하는 작업이다.
  - predecessor denominator는 current preservation 목표값이 아니다.
  - consolidation 뒤 denominator는 surviving contract와 actual current registration에서 다시 생성한다.
  - 일회성 검사 / 검색 / correction command는 새 regular validator가 아니다.

- 최소 결과 trace:

  - current pytest identity: `192`
  - standalone validation: `4`
  - current execution units: `196`
  - current taxonomy identity: `102`
  - current required manifest identity: `61`
  - temporary / one-off physical retirement: `complete`
  - retired target current-authority registration: `0`

- 후속 input artifact:

  - `Iris/_docs/round3/current_route_required_validations.json`
  - `Iris/_docs/round3/temporary_validation_physical_retirement/retirement_summary.json`
  - `Iris/_docs/round3/temporary_validation_physical_retirement/closeout.json`

- Predecessor trace:

  - 2026-06-11 current / historical / diagnostic result separation이 봉인됐다.
  - 2026-08-23 census / survival lifecycle이 regular membership을 current contract 기준으로 재심사했다.
  - 2026-08-24 six-family correction은 dirty-local에만 있던 current product-contract source를 canonical tracked representation으로 복구했다.
  - successor owner decision이 P10을 PASS로 닫아 temporary / one-off physical retirement lifecycle을 완료했다.
  - owner waiver는 존재하지 않는 dirty-main archive / restore evidence를 발견·검증된 것으로 재작성하지 않았다.
  - main integration / origin publication은 repository Git closeout이며 current denominator나 product publication authority를 재정의하지 않는다.
  - 2026-08-25 boundary consolidation은 predecessor `238 / 123 / 70` execution / taxonomy / manifest readpoint를 `196 / 102 / 61`로 successor 정리했다.
  - exact merge hash, implementation baseline, intermediate denominator, review receipt와 validation command detail은 상세 evidence trace로 격하한다.

- 오독 금지:

  - predecessor `238 / 123 / 70`을 current denominator로 읽지 않는다.
  - Git `origin/main` publication을 Iris product Publish / release / deployment로 읽지 않는다.
  - owner P10 waiver를 존재하지 않는 archive evidence의 생성으로 읽지 않는다.
  - current validation PASS를 historical replay PASS, public-text acceptance 또는 runtime correctness로 확대하지 않는다.
  - execution / taxonomy / LOC / byte 감소를 wall-time이나 실제 GPT / Codex token 절감률로 환산하지 않는다.
  - COMMON-RUNTIME-SURFACE-NONMUTATION.
  - COMMON-RELEASE-NONDECISION.

- Trace:

  - route separation origin: 2026-06-11
  - authority census / survival: 2026-08-23
  - physical retirement / main integration: 2026-08-24
  - boundary consolidation: 2026-08-25
  - COMMON-EVIDENCE-TRACE.

### Iris Repository Validation — Clean-Checkout full-repository reproducibility contract

- 날짜: 2026-07-28 → successor validation readpoints

- 상태: current contract / exact-subject machine PASS binding / PASS inheritance forbidden

- 결정: Iris의 clean-checkout validation은 subset 또는 advisory 검증이 아니라 mandatory full-repository reproducibility gate로 유지하며 machine PASS는 exact tracked validation subject에만 귀속한다.

- 현재 기준:

  - validation subject, execution environment와 provenance를 명시적으로 결속한다.
  - Python execution은 repository 밖 dedicated environment를 사용한다.
  - hash-only identity를 provenance나 validated subject로 승격하지 않는다.
  - `partial`, `blocked`, advisory success 또는 incomplete evidence는 terminal PASS를 대체하지 않는다.
  - explicitly current-required source classification은 filename / historical heuristic보다 우선한다.
  - required dependency closure는 import graph뿐 아니라 direct contract / runner / validator dependency를 포함한다.
  - temporary checkout / work / result / virtual environment는 disposable execution surface이며 그 자체가 durable evidence archive가 아니다.
  - clean gate는 exact tracked subject의 Run A/B와 deterministic comparison을 요구한다.
  - denominator / dependency inventory / canonical result identity는 같은 validated subject에 결속해야 한다.
  - correction이 protected result나 execution-relevant source에 영향을 주면 corrected exact subject에서 affected validation을 다시 실행한다.
  - focused / current-runner / configured-collection 검증은 bounded evidence일 수 있지만 mandatory Clean-Checkout gate를 대체하지 않는다.
  - post-validation evidence pointer나 docs-only carrier는 validated subject를 재정의하지 않는다.
  - repository HEAD가 변경되면 predecessor machine PASS를 새 HEAD에 자동 상속하지 않는다.

- 최소 결과 trace:

  - exact-subject machine PASS model: `adopted`
  - correction-subject revalidation: `required when affected`
  - evidence-only carrier != validation subject: `adopted`
  - predecessor PASS inheritance: `forbidden`

- Predecessor trace:

  - 2026-07-28 initial Phase 0는 blocked였고 dedicated execution environment를 도입한 successor가 accepted 상태를 만들었다.
  - 2026-08-13 precision-preserving lightweighting lifecycle은 exact validated subject와 post-validation evidence carrier를 분리하는 precedent를 봉인했다.
  - 2026-08-21 Layer 3 staging / installation은 서로 다른 exact validation subject로 검증됐고 integrated product ancestry는 evidence로 확인됐다.
  - 2026-08-23~24 temporary / one-off retirement correction은 corrected exact subject에서 Clean-Checkout Run A/B와 deterministic comparison을 다시 수행했다.
  - 후속 validation consolidation과 responsibility refactor는 각각 자기 exact subject에서 successor evidence를 생성했다.
  - exact terminal commit / tree, run count, result SHA와 carrier path는 상세 evidence trace로 격하한다.

- 오독 금지:

  - focused / current-runner / configured checks를 mandatory full-repository PASS로 자동 승격하지 않는다.
  - evidence-only pointer / carrier를 새 machine-validation subject로 읽지 않는다.
  - predecessor subject PASS를 후속 repository HEAD의 PASS로 읽지 않는다.
  - clean-checkout PASS를 DVF Body Compiler, RTC, Publish 또는 release readiness PASS로 읽지 않는다.
  - COMMON-RUNTIME-SURFACE-NONMUTATION.
  - COMMON-RELEASE-NONDECISION.

- Trace:

  - initial contract: 2026-07-28
  - exact-subject / carrier refinements: 2026-08-13 onward
  - successor validation: per exact subject
  - COMMON-EVIDENCE-TRACE.

### Iris governance — evidence integrity / completion claim / review / owner seal / attempt integrity

- 상태: current governance contract / post-IAR product retirement retained

- 결정: validation evidence, completion claim, independent review, owner decision / seal과 execution attempt는 서로 다른 governance axis로 유지하고 exact subject / successor identity에 결속한다. 실패·blocked evidence를 삭제·덮어쓰거나 다른 lifecycle의 PASS로 세탁하지 않는다.

- 현재 기준:

  - `current_route_required_validations.json`을 current-required validation binding surface로 사용한다.
  - required evidence는 current authority reference, artifact identity / freshness, validation tooling과 preservation state를 같은 readpoint에 결속한다.
  - required surface의 missing / stale / dirty / unintended untracked / ignore 상태는 fail-closed할 수 있다.
  - protected-surface approval은 path 이름만으로 부여하지 않는다.
  - 승인된 protected delta는 exact successor identity에 결속하며 동일 path의 향후 변경이 과거 승인을 자동 상속하지 않는다.
  - `tracked / ignored / generated` 상태와 authority status를 구분한다.
  - machine validation PASS는 mutation authority를 만들지 않는다.
  - bare `complete` claim은 사용하지 않는다.
  - readiness, eligibility, authorization, execution, adoption, machine validation, review, owner seal과 publication은 서로 다른 lifecycle / claim axis다.
  - 한 axis의 PASS나 completion을 다른 axis의 completion으로 자동 승격하지 않는다.
  - machine-generated PASS는 independent review PASS가 아니다.
  - independent review는 exact review subject와 evidence identity에 결속한다.
  - owner approval / adoption / seal은 machine validation이나 independent review를 대체하지 않는다.
  - independent review 역시 owner-only decision이 필요한 claim의 owner seal을 자동 대체하지 않는다.
  - owner preapproval은 execution / disposition authority를 부여할 수 있지만 실제 functional / runtime / timing evidence를 합성하지 않는다.
  - historical authorization이나 owner approval은 후속 변경 subject에 자동 상속되지 않는다.
  - failure-bearing attempt와 successor attempt는 별도 identity로 관리한다.
  - 같은 attempt의 claim-bearing result / receipt / failure record는 write-once를 기본으로 한다.
  - FAIL을 삭제·덮어쓴 뒤 같은 attempt identity를 PASS에 재사용하지 않는다.
  - protected result에 영향을 주는 correction은 additive correction과 affected validation rerun을 요구한다.
  - predecessor FAIL / blocked state와 rejected candidate는 당시 사실로 additive preservation한다.
  - Stateful IAR가 product에서 퇴역했더라도 evidence integrity, review separation, exact-subject binding과 failure-preservation 원칙은 유지한다.

- 최소 결과 trace:

  - path-only protected approval: `forbidden`
  - exact successor / review-subject binding: `required`
  - bare completion claim: `forbidden`
  - machine / review / owner axes: `separate`
  - predecessor failure rewrite: `forbidden`
  - failure laundering: `forbidden`

- Predecessor trace:

  - 과거 IAR consumer denominator, migration readiness, authorization과 Registry Authority closure attempt는 lifecycle / completion axis를 분리하는 governance 원칙을 형성했다.
  - predecessor consumer `migrated` disposition은 live mutation execution과 동일하지 않았으며 subject-bound authorization도 후속 implementation에 자동 승계되지 않았다.
  - Registry closure의 failed attempt와 additive correction precedent는 failure preservation / attempt integrity 원칙으로 흡수한다.
  - 2026-08-13 precision-preserving lightweighting lifecycle은 machine validation, independent review, owner seal과 evidence carrier를 별도 axis로 결속하는 precedent를 남겼다.
  - exact attempt / commit / carrier / retrieval / review receipt와 round-local validation 수치는 상세 evidence trace로 격하한다.

- 오독 금지:

  - required-validation PASS를 writer authority로 읽지 않는다.
  - machine PASS, independent review와 owner seal을 서로 대체하지 않는다.
  - owner preapproval을 실제 PZ functional / timing evidence나 reviewer PASS로 읽지 않는다.
  - predecessor authorization이나 historical closure를 current runtime / package authority로 복원하지 않는다.
  - governance eligibility나 scoped completion을 Publish, runtime rollout, release / Workshop / B42 readiness로 확대하지 않는다.
  - COMMON-RUNTIME-SURFACE-NONMUTATION.
  - COMMON-RELEASE-NONDECISION.

- Trace:

  - predecessor IAR governance lifecycles
  - evidence / review / completion-vocabulary successors
  - post-IAR product retirement governance retained: 2026-08-20 onward
  - COMMON-EVIDENCE-TRACE.

### Iris Tooltip T1 — display contract / upstream input readiness boundary

- 날짜: 2026-08-27 → 2026-08-28 corrective refinement → 2026-08-29 T1-D1/D2/D3/D4/D5 workstream successors → T1-D6 integrated adoption

- 상태: current owner-ratified offline contract / integrated contract-and-audit complete / formal closeout complete / `T2_FULL_DATA_PROGRESSION=OPEN` / production T2 handoff present

- 최신 입력 기준: 2026-08-30 S1 표제 보완 successor `60796744`를 current로 채택했다. 아래 T1-D6 `b30aaff2`의 root/hash는 predecessor 실행 이력으로 보존하며, 현재 T1 입력과 T2 완료 상태는 아래 「Iris Tooltip T2 — deterministic KO/EN static staging」 및 current route를 따른다.

- 결정: Tooltip은 applicable한 Layer 2 classification, optional Layer 3 core description과 최대 두 개의 Layer 4 public interaction identity를 S1→S4 순서로 투영한다. Layer 2(S1)는 모든 support FullType의 필수 semantic fact가 아니라 current Classification authority가 user-facing category와 admissible primary subcategory를 안전하게 제공할 때만 표시하는 optional navigation/display projection이다. T1은 semantic/public eligibility와 identity selection을 먼저 닫고 selected identity의 KO/EN 및 Menu evidence readiness를 나중에 판정하는 offline contract/audit owner로 한정한다.

- 현재 기준:

  - owner-ratified support predicate는 current Layer 2, pointer-selected Layer 3와 current Layer 4 owner FullType의 case-sensitive explicit union이다.
  - Layer 2가 applicable하지 않은 support row는 system-level deterministic source-state rule에 따른 legitimate display silence다. S1 placeholder나 빈 줄을 만들지 않고 S2~S4를 위로 당기며, 이를 per-FullType semantic absence나 correction으로 승격하지 않는다.
  - D1 successor의 exact partition은 support `2,280` (`3a6cc24b9ad64e06a0a6c0408821201e35bbd1d8558e6245809b5d3c34265ce6`) = `layer2_applicable 1,406` (`c5a77d86eb875cecf03edf5ab67f29361f58947bd97493e522667b593130f264`) + `layer2_display_silence 874` (`d13fa6ac9072a3ab2c61bc59990bfb948010ce8b2fc3211aa1ecb7b5c6c121de`)다.
  - display silence `874`는 raw `Misc.9-A` fallback `408`, membership 없음 `201`, multi-membership이지만 admissible primary 없음 `265`의 exact partition이다. FullType 이름, Layer 3/4, presentation rank 또는 source order로 분류를 추론하지 않는다.
  - 기존 resolved `1,406` rows는 canonical hash `f36a6a6c72080bae8b28b9a1c419eff2ca2a15fc192be04edbfb5be40d31833f`로 byte/identity/surface를 보존했으며 Classification correction은 `874 → 0`으로 닫혔다.
  - 다른 layer의 legitimate absence display row는 compact할 수 있지만 semantic slot identity/order를 유지하며 defect row는 compact하지 않는다.
  - Layer 2 raw tag/runtime resolver 복제, Layer 3 body truncation·요약·재작성, Layer 4 importance/frequency/text-similarity/input-order selection을 금지한다.
  - both-source Layer 4 row는 Recipe 하나와 Right-click 하나를 선택하고 single-source row는 neutral stable structural order로 최대 둘을 선택한다.
  - Layer 4 identity source는 current authority로 분류된 `Iris/build/description/v2/data/upstream_usecases_by_fulltype.json`이며 `Iris/build/baseline/**` reproduction artifact를 semantic input으로 승격하지 않는다. Selected identity는 Browser가 소비하는 current runtime `UseCaseDescriptions/Chunk*.lua`의 `label_key` identity와 별도로 대조한다.
  - explicit QG order key가 없는 current subject의 tie-break는 versioned source/interaction identity bytes에서 파생하며 semantic rank가 아니다.
  - selected identity는 locale/Menu readiness 전에 freeze한다. KO/EN fallback, locale별 reselection과 readiness가 더 좋은 차순위 substitution을 금지한다.
  - Menu/Tooltip parity는 identity relation이며 independent consumer evidence가 없는 shared-authority 범위는 `unverified_without_independent_consumer_evidence`로 남긴다. `same-authority`는 동일 fact source를 뜻할 뿐 두 surface의 coverage가 항상 동일하다는 뜻은 아니다.
  - D1은 D2에 `layer2_applicable 1,406` / `layer2_display_silence 874` exact partition을 제공한다. Menu correction `2,280`의 실제 consumer relation과 applicable/N/A parity는 D2가 소유하며 D1이 산술 차감하거나 재귀속하지 않는다.
  - T1-D2는 support `2,280` 전체의 actual Lua consumer relation을 existing production Lua harness로 관찰해 exact coverage `2,280`을 확인했다. Terminal relation은 `verified 1,406` (`c5a77d86eb875cecf03edf5ab67f29361f58947bd97493e522667b593130f264`) + `not_applicable 874` (`d13fa6ac9072a3ab2c61bc59990bfb948010ce8b2fc3211aa1ecb7b5c6c121de`)이고 `correction_required=0`이다.
  - D2의 bounded Browser correction은 accepted explicit `IrisPrimarySubcategory`가 `primaryTag`와 `primaryLocation`을 함께 정렬하도록 한다. Malformed/non-membership explicit primary는 fail-loud하고 membership buckets는 보존하며, explicit primary가 없으면 기존 presentation-rank 선택을 보존한다. Actual navigation delta는 `26` (`aeaa96db07490dd7193080ec1e0ee6c66a9e3893504451677887cf6a1ce00791`)이고 display-silence Menu delta, owner-output self-comparison, rendered-string inference와 normalized-key join은 모두 `0`이다.
  - D2 audit는 artifact에 기록된 exact relation을 직접 소비한다. Applicable row는 exact Browser/Menu category-primary parity가 성립할 때 `verified`, D1 display-silence row는 consumer surface가 없을 때 `not_applicable`이며 missing/extra/mismatch는 fail-closed correction이다. D2 candidate whole-T1 audit의 correction `0`과 progression `OPEN`은 exact isolated subject의 결과일 뿐 global-current adoption, T2 runtime 시작 또는 production handoff authority가 아니다.
  - D2 admission에서 predecessor registry hash-bound text는 단일 LF corpus가 아니라 declared-byte-compatible mixed LF/CRLF corpus임을 확인했다. Isolated checkout에서 raw/LF/CRLF hash를 대조해 declared serialization의 line ending만 materialize했고 normalized Git/content delta는 `0`이었다. Registry hash, authority, source 의미와 tracked Git content는 변경하지 않았으며 이 preparation을 repository validator나 새 authority로 승격하지 않는다.
  - D2 final validation은 focused Tooltip suite `90 passed`, Browser owner direct unittest `2 tests OK`, Lua syntax `127 files OK`였다. Relation Run A/B artifact bytes는 동일했고 SHA-256은 `5e78c5616d14727c00585bd3671e9c0313b5490a1e6fc4b93af69b722ef4d7ce`, run receipt SHA-256은 `cffbd777030cc4ff2f8f7c6eaa0cd6fa5eee6d6f50f84e808638a4e01e82acea`다.
  - DVF owner output은 Menu consumer evidence를 스스로 발급하지 않는다. Layer 3 fact identity와 KO/EN surface readiness는 DVF owner가 소유하지만 `menu_consumer_fact_identity_refs` 같은 self-attestation을 Menu parity evidence로 사용할 수 없다.
  - current Layer 3 shared-authority relation은 pointer-selected `dvf_3_3_rendered.json`의 fact relation과 `IrisLayer3DataCurrent → IrisLayer3DataLookup → layer3_renderer → IrisItemDetailModelAssembler`의 동일 FullType 소비 경로로 추적한다. 이 relation만 있고 독립 Menu fact-identity observation이 없으면 selected Layer 3 parity는 `verified`가 아니라 `unverified_without_independent_consumer_evidence`다.
  - shared-authority relation이 성립한 Layer 3 consumer-evidence gap은 T3 재검증 대상으로 남기되 T2 blocker로 세지 않는다. relation 자체가 없거나 모순되면 Menu consumer owner correction과 T2 blocker로 fail-closed한다.
  - Layer 3 approved Tooltip fact identity/surface와 Layer 4 explicit selected-identity locale surface 결손은 각 owner workstream correction으로 귀속하며 D1이 보완하지 않는다.
  - `Base.LemonGrass` / `Base.Lemongrass` normalized collision은 case-sensitive exact identity 둘, support/readiness membership과 raw diagnostic observation을 그대로 보존한다. Owner-approved T1-D5 disposition은 이 exact pair에 한해 `SUPPORT_NORMALIZED_COLLISION` correction과 해당 T2 blocker만 제거하며 identity를 합치거나 denominator에서 제거하지 않는다.
  - T1-D5 적용 결과 support는 `2,280 → 2,280`, correction ledger는 `5,625 → 5,623`, target blocker는 `2 → 0`, non-target delta는 `0`이다. 이 국소 correction은 다른 owner blocker를 닫지 않으므로 전체 `T2_FULL_DATA_PROGRESSION`은 계속 `BLOCKED_BY_UPSTREAM_CORRECTIONS`이고 production T2 handoff는 없다.
  - T1-D5 frozen support binding은 case-sensitive exact FullType 집합을 중복 제거하고 ordinal ascending으로 정렬한 뒤 각 UTF-8 value 뒤에 LF를 붙여 연결한다. Final LF는 있고 BOM과 JSON encoding은 없다. Common predecessor의 2,280 exact set digest는 `3a6cc24b9ad64e06a0a6c0408821201e35bbd1d8558e6245809b5d3c34265ce6`이다.
  - 최초 D5 bundle의 `82cca317e95f308f2f9edad0adf2a3667b74aa92b31246dd7af1134e1852eed0`은 동일 exact set의 JSON-array 직렬화 hash였다. Independent predecessor re-derivation과 pre-mutation set 비교에서 missing/extra가 모두 0이므로 `serialization_only_corrected`로 disposition하고 corrected bundle의 `integration_impact.support_freeze_mismatch`는 `false`다. 최초 bundle은 superseded이며 D6 입력으로 사용하지 않는다.
  - contract/audit axis와 `T2_FULL_DATA_PROGRESSION`은 분리한다. D1 successor의 Classification correction은 `0`이고 그 isolated subject의 actual other-owner correction은 DVF `175`, Iris `2`, Menu `2,280`, QG `888`, total `3,345`다. 이 수치를 D3/D4/D5 candidate와 산술 결합하거나 integrated current ledger로 승격하지 않는다.
  - D1 successor의 task-specific/formal 상태는 `complete`지만 `current_ecosystem_adoption=pending_T1_D6`다. 이 workstream completion을 D2 implementation, D6 integration, canonical full gate/finalizer, global-current adoption 또는 production T2 handoff로 읽지 않는다.
  - correction 기반 progression, cause class, owner와 owner별 blocker count는 모두 `t2_blocking = true`인 동일 correction 집합에서만 파생한다. T3 재검증 관찰이나 non-blocking correction은 T2를 차단하지 않는다.
  - tracked contract/fixture와 installed package producer는 current authority지만 repository-external census/audit/ledger/receipt는 lifecycle evidence이며 regular validation authority가 아니다.
  - tracked decision contract는 ratification template이며, clean exact subject의 W1-A evidence hash와 subject identity를 adoption receipt가 결속한 뒤에만 G1 및 W1-B가 성립한다.
  - 2026-08-28 corrective subject에서 normalized collision correction 2건을 복원하고 Layer 3 owner-output self-comparison을 제거했다. 최종 correction은 `5,625`이며 owner 분포는 Classification `2,280`, DVF `175`, Iris presentation-contract `2`, Menu consumer `2,280`, QG/locale `888`이다.
  - 같은 corrective subject의 focused 6-family route, installed candidate invariant, canonical Run A/Run B와 deterministic comparator가 모두 exit 0이고 post-gate finalizer가 `complete/complete` closeout을 생성했다. 이 formal completion은 `T2_FULL_DATA_PROGRESSION = BLOCKED_BY_UPSTREAM_CORRECTIONS` 및 production T2 handoff `0`과 공존한다.
  - 2026-08-29 T1-D3 workstream은 current authoritative audit가 재구성한 exact `DVF_OWNER_ROW_MISSING` 175건을 frozen target으로 사용했다. Target ordered-set SHA-256은 `accbe1ae691e41b1697f080f26b8206a08e261039bb7919879f67f4b5d7ef238`이며 duplicate, denominator shrink와 exact-identity normalization은 `0`이다.
  - 해당 175건은 current item identity에는 존재하지만 current DVF facts, decisions와 approved role-material candidate에는 모두 부재했다. 171건은 Layer 4 exclusion-only support, 4건은 Layer 2-only support 경로였으며, owner 사전 승인과 producer-independent defect-exclusion verdict에 결속해 `A=0`, approved legitimate absence `B=175`, unresolved/blocked `0`으로 disposition했다.
  - T1-D3 Layer 3 owner projection successor는 기존 fact compatibility map `entries` 1,314건과 explicit `absence_entries` 175건을 구조적으로 분리한다. Explicit absence는 exact FullType, DVF owner decision, approved reason, applicable scope, re-audit condition과 independent technical/locale/quality/review defect-exclusion evidence가 모두 유효할 때만 소비한다. 단순 lookup miss, locale/review/quality defect 또는 producer self-report는 absence가 아니다.
  - T1-D3는 metadata-only path를 사용했다. Current generation ID, pointer, existing fact 1,314건, existing Layer 3 empty-core 791건, Layer3English와 Lua runtime bytes를 변경하지 않았고 generation-bearing path를 실행하지 않았다.
  - Same-subject candidate Run A/B는 support `2,280`, correction `5,450`, D3 target `DVF_OWNER_ROW_MISSING=0`과 동일 receipt hash를 냈다. Focused Tooltip T1 tests는 `65 passed`, independent absence/non-target comparator와 `git diff --check`는 exit `0`이었다. Test file/top-level function delta는 각각 `0`, parameter case delta는 `3`이다.
  - 위 결과의 terminal `complete`는 T1-D3 workstream correction bundle에만 적용한다. Global current manifest/route/environment/governance adoption은 T1-D6 전까지 `pending_T1_D6`이며, integrated current correction 기준은 계속 `5,625`다. Candidate `5,450`을 T2 `OPEN`, runtime adoption, full Menu parity, freeze, Publish 또는 release readiness로 읽지 않는다.
  - 2026-08-29 T1-D4 workstream은 common predecessor에서 선택된 Recipe instance 444건, exact Recipe identity 266개와 locale correction 888건을 freeze했다. QG owner registry/projection은 identity/public/source/selection authority를 바꾸지 않고 동일한 role-neutral Recipe-use fact의 explicit KO/EN pair만 발행한다.
  - D4의 `Layer4Candidate`와 selection API는 locale/Menu readiness field를 소유하지 않는다. Recipe locale owner output은 selection이 끝난 뒤 exact selected identity로만 조회하며, embedded identity-input locale field는 정상 fallback이 아니라 authority-ceiling violation이다. Cross-locale fallback, locale-dependent reselection, Recipe→Right-click substitution은 허용하지 않는다.
  - D4 candidate whole-T1 re-audit는 support `2,280`, correction `4,737`, D4 target `LOCALE_SELECTED_SURFACE_MISSING=0`을 산출했다. Selected tuple/source distribution과 other-owner correction delta는 `0`; runtime/static Tooltip, Right-click locale route, Browser consumer identity와 D6-exclusive current paths는 변경하지 않았다.
  - D4 frozen support exact set은 common predecessor 재도출 set과 missing `0`, extra `0`으로 동일하다. Common hash는 ordinal-ascending unique exact FullType 각각의 UTF-8 bytes 뒤에 LF를 붙이고 final LF를 포함하며 BOM/JSON encoding을 사용하지 않는 직렬화의 SHA-256 `3a6cc24b9ad64e06a0a6c0408821201e35bbd1d8558e6245809b5d3c34265ce6`이다. 선행 D4 bundle의 JSON-array 기반 `82cca317e95f308f2f9edad0adf2a3667b74aa92b31246dd7af1134e1852eed0` 표기는 serialization-only 오류로 폐기했고 `integration_impact.support_freeze_mismatch=false`인 corrected bundle을 재발행했다.
  - D4 focused Tooltip T1 tests는 `67 passed`; materializer Run A/B bytes와 digest는 동일했고 whole-T1 audit, exact reconciliation, protected-path check 및 corrected bundle validator는 exit `0`이었다. Support-hash 정정 시에는 source semantics, tests, materializer와 whole audit를 반복하지 않고 support-freeze/bundle binding만 최소 재검사했다.
  - D4 terminal `complete`도 isolated correction bundle에만 적용한다. D3와 D4 candidate ledger를 서로 산술 결합하거나 어느 한쪽을 current ledger로 채택하지 않으며, shared delta merge, bundle compatibility validation, integrated whole-T1 re-audit와 global status synchronization은 T1-D6가 소유한다.
  - D6용 corrected cumulative bundle은 T1-C common predecessor `6b7118dc229bf8138302696e1aa5e5b7454589dc` / tree `4eae6fbdb3d0b2cb532f875b96137335a403f2fc`에서 final D1 successor `8bbc40169e86bd2e818c440a823e497f852a1e69` / tree `e950a552797012e6e40523e75b93a1ed203e839b`까지의 누적 shared delta를 소유한다. Direct parent D1은 `81eb49b062137d5ae8b93cd5bfeb17d08f3d3a56` / tree `064cb1bd8c7c4bb2056410addd2f9b50e9505ee4`로 별도 lineage에 남기고, corrected cumulative bundle 하나만 active D6 input으로 사용한다.
  - T1-D6 integrated subject `b30aaff2da6172ab5137c55bb460889aa527ad04` / tree `7cdd52fd61f739b5018a62d8bffe84461dfea50c`에서 support `2,280`, Layer 2 `verified 1,406` / `not_applicable 874`, T2-blocking correction과 owner blocker 합계 `0`을 재확인했다. Strict handoff input은 exact `2,280` rows이고 SHA-256은 `138b6f4ef85a2235fa41e6d60d88e885c6f6f93a8bb0458a7d6ac4dce7af56ac`다.
  - Fresh installed environment에서 canonical Run A/Run B가 모두 exit `0`/`PASS`였고 canonical result SHA-256은 동일한 `9ff37bd36685373ab193017a5a2cef58e5e02573b19826d4aa28ba575d9444d8`이다. Deterministic comparator와 기존 finalizer도 exit `0`이며 final closeout은 `complete / complete / OPEN / present`다.
  - Final production root는 repository-external `C:/Users/MW/Downloads/coding/PZ-tooltip-t1-d6-final-b30aaff2`, closeout SHA-256은 `f8d6bcbef0e71d57fe36be36504a5ffcea1696953b7d8280deeba911fdcecab6`다. 이 경로와 hash는 current route의 explicit locator이며 별도 validation authority가 아니다. 선행 repository-internal `.tmp` materialization은 superseded ephemeral output이고 canonical current가 아니다.
  - Canonical gate를 막았던 Windows directory `Path.replace`는 semantic output과 manifest visibility switch를 보존한 채 `shutil.move`의 Windows-compatible fallback으로 교정했다. Regular-file manifest `os.replace` 선형화 지점, generation ID, owner authority와 DVF output bytes는 변경하지 않았다.

- Machine authority:

  - `Iris/_docs/authority/tooltip_t1/`
  - `docs/iris_tooltip_t1_display_contract_policy.md`
  - command owner: `Iris/build/ENTRYPOINTS.md`

- 오독 금지:

  - T1 contract/audit completion을 T2 static generation, runtime adoption, actual visual fit, full Menu parity, package/install, compatibility, freeze, Publish, release, Workshop 또는 deployment PASS로 읽지 않는다.
  - upstream gap ledger를 T1 semantic workaround나 correction mutation authority로 읽지 않는다.
  - display silence `874`를 새 semantic classification row, owner-approved absence record 또는 T2 blocker로 되돌리지 않는다.
  - historical partial/old successor bundle을 corrected cumulative bundle과 함께 적용하지 않는다.
  - one-off audit와 ad hoc probe를 canonical/regular validator로 승격하지 않는다.
  - post-gate finalizer를 semantic producer, 일반 workflow system 또는 T2 OPEN authority로 읽지 않는다.
  - COMMON-RUNTIME-SURFACE-NONMUTATION.
  - COMMON-RELEASE-NONDECISION.

- Trace:

  - owner preapproval and offline T1 contract adoption: 2026-08-27
  - corrective formal-complete subject: commit `6b7118dc229bf8138302696e1aa5e5b7454589dc`, tree `4eae6fbdb3d0b2cb532f875b96137335a403f2fc`
  - corrective environment authority: `Iris/validation/clean_checkout/authority/responsibility_refactor_environment_tooltip_t1c_corrective_d1d0c098.json`
  - external final closeout SHA-256: `6e255227b0aa8381453a563e3ede9e96c59be82c9bb3a7cb6eba8f488039b4a3`
  - owner-approved optional Layer 2 successor amendment and D1 completion: 2026-08-29
  - final D1 successor subject: `8bbc40169e86bd2e818c440a823e497f852a1e69` / tree `e950a552797012e6e40523e75b93a1ed203e839b`
  - corrected cumulative external bundle: `C:\Users\MW\Downloads\coding\PZ-t1d1-successor-cumulative-8bbc4016`; manifest SHA-256 `ae91527431f5d34d0ca7c6fc6b86082b9c7e6f33b7ceabc39741ad2093641c3e`, shared-delta SHA-256 `5dcf432e36ae5ff2d2b8469faca0b983b37c96380985f46cd1af490c0e2cbed4`, closeout SHA-256 `b1ac3157b04abada0bf153009022b7c4ee8118a160525fb129c5e2b8db27c7f3`
  - T1-D3 workstream subject: branch `codex/iris-tooltip-t1-d3`, commit `92583338`
  - T1-D3 immutable bundle: `C:/Users/MW/Downloads/coding/PZ-tooltip-t1-d3-bundle-92583338`
  - T1-D3 bundle receipt SHA-256: `cf7d6529f404494e23fbc1a6967ab75a52f065690f3b88e5a5560a78ecdcc202`
  - T1-D4 workstream subject: branch `codex/iris-tooltip-t1-d4`, commit `a8fddf747738045df08579ae34b0b727e3cf91ad`, tree `9b6b1831c18da58846d9d3c940133b2095de741d`
  - T1-D4 corrected external bundle: `C:/Users/MW/Downloads/coding/PZ-t1-d4-artifacts/d4-bundle-support-hash-corrected`
  - T1-D4 corrected bundle receipt SHA-256: `a2c8d8c3d5ed317fafa1483c44e429938d4b813ec73a08f00d40505668d6df96`; integration manifest SHA-256: `95fd303d4cab94d8fcee30bb7c2ba9b033dd1d7124b7d333dacfe40dde735264`
  - 선행 `C:/Users/MW/Downloads/coding/PZ-t1-d4-artifacts/d4-bundle`은 noncanonical support-hash binding 때문에 superseded이며 T1-D6 입력으로 사용하지 않는다.
  - T1-D5 implementation subject: `c86b4a747025aa593eddacd7d9c7de7c095ebad8` / tree `006acd132be465c6c5df7e832bd1a9c9c6925f5c`
  - corrected external D5 bundle receipt SHA-256: `c025e5d0f6b6c62a98dbeb54fa8aacbf572a3975c18869718c859d8aa4315046`; lifecycle evidence이며 canonical/regular validator authority가 아니다.
  - T1-D2 implementation subject: `0e959b3bd7055d58f319fa9d69a5b110bf48b8b7` / tree `5dbc1a830e5a911eece943102c6078102c3d9611`; exact direct parent `cb27591e3c6ef40a1b1f08a6e2ceee7047132cf8` / tree `b23103ace037aa62fc1e24d04901d534de5cc2e8`
  - T1-D2 external bundle manifest SHA-256: `25cc173f9b47effb23b0c4823cc33be82b012ba8e9f6c1281172bdf50e62b39d`; lifecycle evidence이며 canonical/regular validator authority가 아니다.
  - T1-D6 machine-validation subject: `b30aaff2da6172ab5137c55bb460889aa527ad04` / tree `7cdd52fd61f739b5018a62d8bffe84461dfea50c`
  - T1-D6 strict handoff manifest SHA-256: `15a4a089fdde7eeb70fd0f1e21d77872b90fdaec8130d45605edac52d67fb892`; final closeout SHA-256: `f8d6bcbef0e71d57fe36be36504a5ffcea1696953b7d8280deeba911fdcecab6`
  - Repository-external final-root correction carrier는 commit `8e972950b7b699b435d9b21e54432af94fc42f53`, tree `51cb94b963493411dd31dd3c4f21cb79797e2f69`다. Installed final current readback은 exit `0`으로 external root, exact machine subject와 `adopted / complete / complete / OPEN / present`를 확인했다.
  - 이 docs-only successor는 위 machine subject나 external receipt identity를 대체하거나 재귀속하지 않는다.
  - detailed policy: `docs/iris_tooltip_t1_display_contract_policy.md`
  - COMMON-EVIDENCE-TRACE.

### Iris Tooltip T2 — deterministic KO/EN static staging

- 날짜: 2026-08-30
- 상태: static staging complete; runtime adoption은 T3에 남는다.
- S1은 기존 승인 D1 category/primary surface를 `[{category_surface} - {primary_subcategory_surface}]`로 결합한다. D1 의미·surface·applicability와 S2–S4는 변경하지 않았다. Current T1 successor는 `60796744ffb889477161d243a1443c9de57d49b0`이며 기존 focused 95, canonical A/B, comparator와 finalizer가 exit `0`이다. 과거 T1 final root는 보존한다.
- T2 machine subject `d64692ac26cdc21e4c7f558a0fe93278f64b16d1` / tree `850e0af81af9b9fda8ee7df26847f88a4b32b142`는 이 successor handoff만 읽는다. Exact FullType과 explicit `ko|en`으로 완성된 배열을 제공하며 2,280개 key에 빈 배열도 명시한다. 번역·요약·fallback·재선택·omission cause 추론은 하지 않는다.
- T2 focused 18, installed generation A/B, 생성 Lua syntax 1-file, canonical full gate (`211 passed, 109 subtests passed`)와 finalizer가 exit `0`이다. A/B Lua·manifest와 candidate/final bytes가 동일하다. 고정 금지 표현 hit는 `0`이며 이를 semantic 품질 재인증으로 확대하지 않는다.
- 생성 결과의 0/1/2/3/4줄 분포는 `367 / 825 / 895 / 137 / 56`이며 생성 실패·contract 위반은 `0`이다. `Base.LemonGrass`와 `Base.Lemongrass`를 포함한 case-sensitive exact identity를 보존한다.
- Completion metadata가 없으면 finalizer는 기존 `partial` 상태와 남은 `unvalidated_but_in_scope`를 기록한다. `complete`는 명시적으로 결속된 focused/installed inspect/Lua/full-gate 성공 결과가 있을 때만 발행하며 artifact equality로 검사 성공을 추론하지 않는다.
- Final external staging은 `C:/Users/MW/Downloads/coding/PZ2/t2-final`이며 exact hashes는 current route와 `tooltip_t2_closeout.json`이 기록한다. Runtime/package pointer는 전환하지 않았다. Manifest schema 검사는 기존 projection test의 직렬화 fixture에 연결했으며 별도 validator·proof package를 만들지 않았다.
- 수정된 T2 package는 기존 environment successor record `responsibility_refactor_environment_tooltip_t2_6b471e48.json`에 결속했다. T2 전용 수정 이후에도 성공한 T1 successor handoff와 gate는 그대로 소비했다. 완료 carrier `dd17d447`은 선택 저장소에 fast-forward 반영됐으며, carrier를 T1/T2 machine subject와 바꿔 쓰지 않는다.
- 실행 명령·실패 재시도·validation ceiling은 `docs/iris_tooltip_t2_deterministic_ko_en_static_lua_projection_plan.md`의 execution 기록과 기존 closeout을 참조한다. 문서 carrier를 새 검증 subject로 해석하지 않는다.

### Iris validation — workflow / scenario execution consolidation boundary

- 날짜: 2026-08-13 → 2026-08-20 → 2026-08-25 refinement

- 상태: current readpoint / workflow execution-sharing boundary adopted

- 결정: Iris validation의 execution lightweighting은 test node 수 자체를 줄이는 작업이 아니라, 같은 canonical input에서 반복되는 비싼 producer / preparation workflow를 공유하면서 각 contract의 failure attribution, input isolation과 fresh-process semantics를 보존하는 방식으로 수행한다.

- 현재 기준:

  - consolidation의 기본 단위는 assertion 수가 아니라 반복되는 expensive producer / workflow다.
  - 하나의 producer result를 여러 checkpoint가 소비할 수 있으면 immutable preparation을 가능한 범위에서 한 번만 수행한다.
  - 공유 대상은 immutable baseline, immutable preparation result 또는 명시적인 read-only workflow state다.
  - test 간 실행 순서 의존성이나 predecessor test의 mutable output 재사용을 도입하지 않는다.
  - mutation, tamper, rollback, recovery, concurrency와 fresh-process semantics는 case-local clone / reset / namespace / process에서 유지한다.
  - 서로 다른 input state를 요구하는 case를 하나의 mutable workspace에 강제로 합치지 않는다.
  - `subTest` 또는 동등한 named checkpoint로 predecessor contract / failure identity를 보존한다.
  - node 감소를 위해 failure localization, fail-closed path, required-validation identity 또는 standalone CLI boundary를 숨기지 않는다.
  - consolidation은 repeated-cost가 실제로 존재하고 isolation / identity / fault contract를 보존할 수 있을 때만 채택한다.
  - 안전한 positive-cost candidate가 없으면 node 수를 줄이기 위한 추가 병합을 강제하지 않는다.
  - wall-time 개선률은 comparable before / after timing evidence가 있을 때만 별도로 주장한다.

- 최소 결과 trace:

  - 2026-08-20 adoption preserved consumer / subcase identity: `40 unique / 55 -> 55 concrete`
  - 2026-08-20 consolidatable producer invocation: `73 -> 6`
  - corresponding canonical Run A / B + deterministic comparison: `PASS`

- Predecessor trace:

  - 2026-08-13 successor direction이 repeated producer / workflow consolidation을 후속 전략으로 채택했다.
  - 2026-08-20 four-group implementation이 actual execution sharing을 적용하면서 55 concrete failure identities를 보존했다.
  - 2026-08-25 regular boundary consolidation은 named check / subtest, immutable shared seed와 case-local reset / clone으로 predecessor contract를 보존하면서 current validation denominator를 추가 정리했다.
  - exact producer names, Round 3 reduction counts와 validation commands는 상세 evidence trace로 격하한다.

- 오독 금지:

  - `40 / 55 / 73 -> 6`을 current validation denominator로 읽지 않는다. 이는 2026-08-20 execution-sharing adoption trace다.
  - node / runner / import 감소를 validation coverage나 failure localization 축소 권한으로 읽지 않는다.
  - producer invocation 감소를 suite 전체 wall-time 감소율로 읽지 않는다.
  - shared immutable preparation을 mutable workspace 공유나 fresh-process semantics 제거로 확대하지 않는다.
  - consolidation 수치를 실제 GPT / Codex token 또는 PZ runtime 성능 개선으로 환산하지 않는다.
  - COMMON-RUNTIME-SURFACE-NONMUTATION.
  - COMMON-RELEASE-NONDECISION.

- Trace:

  - successor direction: 2026-08-13
  - execution-sharing adoption: 2026-08-20
  - regular-boundary refinement: 2026-08-25
  - COMMON-EVIDENCE-TRACE.

---

## Frame

### Frame — PZ판 git형 팩 상태 버전 관리 레이어

- 상태: current readpoint / pre-ledger imported + 2026-03-25 refinement
- 결정: Frame은 `모드팩 관리자`, `문제 해결 도구`, `런처`, `설치기`, `devkit`가 아니라, **Project Zomboid 모드팩 상태를 기록·비교·되돌리는 버전 관리 레이어**로 둔다.
- 현재 기준:
  - Frame의 최소 관리 단위는 개별 모드가 아니라 **팩 상태(pack state)** 다.
  - Frame은 특정 시점의 모드 목록 / 순서 / 출처 / 설정 / 지문을 묶은 **환경 상태**를 1급 객체로 다룬다.
  - 제품 비유는 `CurseForge형 관리자`보다 **PZ판 git**에 가깝게 고정한다.
  - Frame은 월드/세이브 상태를 커버하지 않는다.
  - Frame은 성능 개입, 안정화, Lua 실행 제어, 런타임 정책 결정을 맡지 않는다.
  - Frame은 Fuse/Nerve와 기능적으로 엮이지 않는 **비런타임 모드팩 운영 레이어**로 둔다.
- 영향: Frame은 설치 전/운영 단계의 팩 구성·스냅샷·재현성 관리에 집중하고, 실제 실행 중 체감 변화나 안정화 개입은 Fuse/Nerve 같은 런타임 모듈의 책임으로 남긴다.
- Trace:
  - ledgered/imported: 2026-03-16 Frame 비정책 / 월드 비포함 원칙
  - ledgered/imported: 2026-03-17 Frame 비런타임 / 비안정화 원칙
  - refined: 2026-03-25 Frame은 PZ판 git 레이어 / 팩 상태 1급 객체 / 환경 상태 한정
  - COMMON-EVIDENCE-TRACE.

### Frame — 비정책 기록·비교·복원 원칙

- 상태: current readpoint
- 결정: Frame은 차이 표시와 상태 기록은 하되, **원인 지목 / 정답 추천 / 자동 해결 / 자동 정렬 / 문제 모드 지목**을 하지 않는다.
- 현재 기준:
  - Frame의 제품 가치는 `더 똑똑한 분석`이 아니라 **되돌림 가능한 기록**에 둔다.
  - UI와 문서는 판단보다 사실과 변화 표시를 우선한다.
  - Frame UI/문서/데이터는 `정상/비정상`, `원인/범인`, `권장/최적`, `해결/진단` 같은 판단 언어를 피한다.
  - 기본 언어는 `기준점`, `자동 저장`, `달라짐`, `비교`, `되돌리기`, `계속` 같은 **사실+행동 언어**로 둔다.
  - Frame은 진단 도구가 아니라 기록/복원 도구이며, 처방보다 복원, 진단보다 비교를 우선한다.
- 영향: Frame은 사용자가 상태 차이를 보고 되돌릴 수 있게 하지만, 어떤 모드가 문제인지 판단하거나 최적 상태를 추천하는 도구로 확장하지 않는다.
- Trace:
  - ledgered/imported: 2026-03-16 Frame 비정책 원칙
  - refined: 2026-03-25 Frame은 진단/추천 도구가 아니라 기록/복원 도구
  - refined: 2026-03-25 Frame의 언어는 사실+행동 언어
  - COMMON-EVIDENCE-TRACE.

### Frame — 스냅샷 / 자동 저장 / 설정 / 재현성 모델

- 상태: current readpoint
- 결정: Frame은 **수동 공식 스냅샷 + 자동 안전망 + 원본 보존/오버라이드 설정 + fingerprint 기반 동일성 확인**을 기본 운영 모델로 둔다.
- 현재 기준:
  - Frame의 공식 스냅샷은 수동으로 만든다.
  - 자동 스냅샷은 공식 기록과 같은 위상이 아니라, 복구와 회귀 추적을 위한 안전망으로만 둔다.
  - 자동 저장은 **5/10/30/60분 고정 주기 + 최근 10개 롤링 보관**을 기본으로 한다.
  - `변화 없으면 저장 생략` 같은 해석적 스킵은 기본 정책에서 배제한다.
  - 자동 저장은 공식 스냅샷과 역할은 다르지만, 기록 품질 자체가 낮은 임시 로그로 취급하지 않는다.
  - 설정은 직접 편집 UI보다 **원본 설정 보존 + 사용자 오버라이드 파일(내 설정)** 구조를 우선한다.
  - 설정 변경 UX는 `원본을 복사해 오버라이드 레이어를 만든 뒤 외부 편집기로 수정`하는 흐름을 기본으로 삼는다.
  - Frame 본체는 설정 편집기가 아니라 레이어 관리와 diff/restore에 집중한다.
  - Frame은 모드 원본 파일을 저장·배포하는 방식으로 완전 복원을 보장하지 않는다.
  - 재현성 모델은 **목록/순서/설정 재구성 + fingerprint 기반 동일성 확인**이다.
- 영향: Frame은 `그때의 상태를 다시 맞출 수 있는가`와 `지금 상태가 그때와 같은가`를 다루며, 모드 원본 자체를 보관·전달하는 시스템으로 확장하지 않는다.
- Trace:
  - refined: 2026-03-25 Frame 스냅샷의 위계는 수동 공식 기록 + 자동 안전망
  - refined: 2026-03-25 Frame 자동 저장은 고정 주기 안전망
  - refined: 2026-03-25 Frame 설정은 원본 보존 + 오버라이드 레이어
  - refined: 2026-03-25 Frame 재현성은 완전 복원이 아니라 재구성과 동일성 확인
  - COMMON-EVIDENCE-TRACE.

### Frame — 공유 포맷과 제품 경계

- 상태: current readpoint / external-tooling deferred
- 결정: Frame은 현재 메인라인에서 **모드 내부 레이어**로 남기고, 외부 공유 표준은 **ZIP + JSON**으로 둔다.
- 현재 기준:
  - Frame을 외부 런처/관리자 툴로 빼는 방향은 현재 메인라인으로 채택하지 않는다.
  - 외부 툴화는 장기 백로그 또는 후순위 옵션으로만 둔다.
  - 공개 공유 포맷은 열린 포맷인 **ZIP + JSON**을 기본으로 한다.
  - `.frame`을 공개 표준으로 강제하지 않는다.
  - 다만 import 단계의 보안/검증을 위해 ZIP을 내부 `.frame` 캐시로 변환하는 안은 유력한 내부 처리 전략으로 남긴다.
  - Frame은 기록·비교·복원 레이어를 넘어 런처, 설치기, 문제 진단기, 설정 에디터, devkit로 확장하지 않는다.
  - 팩 상태 기록/공유/복원과 직접 관련 없는 편의 기능은 기본적으로 Cortex나 별도 후순위 논의로 미룬다.
- 영향: 외부 공유는 열린 포맷을 유지하고, `.frame`은 필요할 때 내부 검증 캐시나 런타임 최적화 수단으로만 다룬다. Frame 본체는 상태 관리 경험에 집중한다.
- Non-decision:
  - 이 항목은 Frame의 즉시 외부 툴화, 공개 표준 `.frame` 강제, 런처/설치기/devkit 전환, 문제 진단기화를 승인한 것이 아니다.
- Trace:
  - refined: 2026-03-25 Frame 외부 툴화는 메인라인이 아님
  - refined: 2026-03-25 Frame 공개 공유 포맷은 ZIP+JSON, `.frame`은 내부 캐시 후보
  - refined: 2026-03-25 Frame은 런처/설치기/devkit로 키우지 않음
  - COMMON-EVIDENCE-TRACE.

---

## Canvas

### Canvas — 리소스팩 별도 제품 축 / 검증·비교·설명 플랫폼

- 상태: current readpoint / pre-ledger imported + 2026-03-25 refinement
- 결정: 리소스팩 축은 Pulse의 핵심 킬러축이나 Frame의 하위 기능이 아니라, 진행한다면 처음부터 **Canvas**로 시작하는 **생태계 확장용 별도 제품 축**으로 둔다.
- 현재 기준:
  - Canvas는 리소스 제작 툴이 아니다.
  - Canvas는 Photoshop, GIMP, Blender, TileZed 같은 외부 제작 툴을 대체하지 않는다.
  - Canvas는 외부 툴이 만든 리소스팩 산출물을 읽어 **최종 적용 상태 / 충돌 / 배포 불일치**를 검증·비교·설명하는 플랫폼이다.
  - 주요 작업은 인덱싱, 최종 상태 계산, 충돌 분석, 구조/경로/ID/패킹 검증, 프리플라이트 검증, 로컬↔산출물 비교, 서버↔클라 비교, 설명형 리포트다.
  - 리소스팩 축을 진행한다면 `Cortex에서 임시 운영 후 이관` 같은 경로를 쓰지 않고 처음부터 Canvas로 시작한다.
  - 시작하지 않기로 결정하면 해당 축은 보류가 아니라 Pulse 생태계에서 제거한 것으로 본다.
- Pain point:
  - 최종 적용 결과 / 충돌 / 로드 순서 가시성 부족
  - 패킹 / 경로 / 구조 / ID 민감성으로 인한 제작 붕괴
  - 버전 / 서버 / 배포 불일치
- 영향: Frame과 Pulse의 핵심 서사는 계속 `모드팩 상태 기록·복원`에 두고, 리소스팩 검증/비교/설명은 Canvas 독립 축으로 다룬다.
- Non-decision:
  - 이 항목은 Canvas를 제작 툴, 리소스 편집기, Pulse 핵심 킬러축, Cortex 임시 수용 축으로 승인한 것이 아니다.
- Trace:
  - ledgered/imported: 2026-03-16 Canvas 정체성 / 초기 진입 경로
  - refined: 2026-03-25 리소스팩 축은 Pulse 핵심축이 아니라 별도 제품 축
  - refined: 2026-03-25 Canvas는 제작 툴이 아니라 검증·비교·설명 플랫폼
  - refined: 2026-03-25 Canvas의 pain point는 적용 결과, 제작 안전, 배포 불일치
  - COMMON-EVIDENCE-TRACE.

### Canvas / Frame — 협력 가능하지만 통합 제품으로 설계하지 않는다

- 상태: current readpoint
- 결정: Canvas와 Frame은 함께 쓰일 수 있어도, 처음부터 하나의 통합 제품처럼 설계하지 않는다.
- 현재 기준:
  - Frame은 **모드팩 상태**를 다룬다.
  - Canvas는 **리소스 적용 상태**를 다룬다.
  - Frame은 시간축 / 스냅샷 / 롤백 중심으로 발전시킨다.
  - Canvas는 리소스팩 최종 상태 검증 / 비교 / 설명 중심으로 발전시킨다.
  - 두 모듈의 협력은 느슨한 연동 수준에 그치며, 서로의 정체성을 흡수하지 않는다.
- 영향: Frame은 팩 상태 버전 관리 레이어로, Canvas는 리소스 적용 상태 검증 플랫폼으로 분리해 읽는다.
- Non-decision:
  - 이 항목은 Frame+Canvas 통합 제품화, Frame의 리소스팩 검증 흡수, Canvas의 모드팩 상태 관리 흡수를 승인한 것이 아니다.
- Trace:
  - refined: 2026-03-25 Canvas와 Frame은 협력하되 통합 설계를 피함
  - COMMON-EVIDENCE-TRACE.

### Canvas — 공개 포맷과 내부 정규화 번들

- 상태: current readpoint
- 결정: Canvas의 외부 공유 기본값은 **ZIP + JSON(+ .pack)** 으로 두고, `.canvas`를 외부 공개 표준으로 강제하지 않는다.
- 현재 기준:
  - Canvas는 열린 입력·공유 포맷을 유지한다.
  - `.canvas`는 공개 표준이 아니라 내부 정규화 캐시 또는 분석 번들 후보로만 둔다.
  - 내부 검증·캐시 전략은 Canvas 독자 구조로 발전시킬 수 있다.
- 영향: 외부 공유는 접근 가능한 열린 포맷을 유지하고, 내부 처리에서는 필요 시 `.canvas`를 정규화 캐시·분석 번들로 사용할 수 있다.
- Non-decision:
  - 이 항목은 `.canvas` 공개 표준 강제, 폐쇄형 공유 포맷 전환, 외부 툴 산출물 직접 편집 기능을 승인한 것이 아니다.
- Trace:
  - refined: 2026-03-25 Canvas 공개 포맷은 ZIP+JSON(+.pack), `.canvas`는 내부 정규화 번들 후보
  - COMMON-EVIDENCE-TRACE.

---

## Iris repository current / historical physical separation

### W0 deterministic adoption — current closure와 historical archive 경계

- 상태: implementation adopted; destructive archive/removal은 후속 gate 대기
- 기준 subject: `9aa81249be7657a1e09a48d162fe96315cfd9748` / tree `c9137a3f0597b39c94000b2cc27ea28e9fab964a`
- 결정:
  - broken legacy `Iris/build/main.py`는 대체 entrypoint나 결손 phase 복구 없이 current authority에서 제거한다.
  - current route는 `current_capsule_attestation_v2`를 소유하고 historical raw recovery는 repository-external `content_addressed_zip_v2` archive가 소유한다. 두 claim을 parity로 표현하지 않는다.
  - current capsule raw bytes의 hard ceiling은 2,359,296 bytes다.
  - inactive Layer 3와 fixed chunks는 external archive create/verify/restore 및 ancestor evidence가 성립하기 전까지 physical hold를 유지한다.
  - `frozen_predecessor_inputs`와 `description/v2/data` 및 current `build/tests`는 보호한다. `owner_inputs` 37 rows와 `reviewer_inputs` 10 rows는 current operational binding을 successor owner로 옮긴 뒤 historical archive 대상으로 확정한다.
  - Change 2 residue manifest는 repository-external one-off execution input이며 Iris의 canonical schema나 validator가 아니다.
- machine binding: `Iris/validation/clean_checkout/authority/iris_current_historical_lightweighting_adoption_v1.json`
- progression: Checkpoint A와 W0 blocker-zero를 통과했으므로 Change 2 이후 progression은 open이다.
- Non-decision: archive 완료, physical deletion, terminal PASS 또는 release readiness를 이 adoption 자체로 주장하지 않는다.

### Terminal closeout — exact W10 및 local-custody correction

- 상태: complete — machine/W10/local-custody PASS; Reviewer remediation complete; independent terminal review PASS with actionable finding 0
- exact implementation subject: `801f15f678fe9c5fd67be0f805f29ed3ba9db9b3` / tree `1db498cabee54d1516e8dc0e78d6a99c8806a4a4`
- 결정:
  - terminal machine PASS는 `801f15f6`의 Run A/Run B/comparator에만 귀속한다. 후속 closeout carrier는 documentary-only이며 이 PASS를 새 implementation commit의 실행 결과로 표현하지 않는다.
  - 최초 0013과 0014 successor bytes를 복구하고 schema-compatible aggregate 정정은 append-only 0015 successor로 기록한다. Current full gate는 0015에 결속하며 predecessor records를 소급 재작성하지 않는다.
  - W10은 clean implementation과 dirty-main local custody를 별도 subject로 결속한다. local custody의 repository 전체 dirty status는 subject binding에 포함하되 Iris scope의 ignored/untracked/filesystem-only/reparse residue는 모두 0이어야 한다.
  - W0와 exact SHA-256이 같은 ignored legacy 295 rows는 predecessor archive에 소급 편입하지 않고 additive external `content_addressed_zip_v2` archive successor로 보존한다. Create/verify/restore PASS 전에는 삭제하지 않는다.
  - pipeline log 2 rows는 current clean tree와 terminal closure에 없는 regenerable generated residue로 판정하여 archive 없이 literal 제거한다.
  - one-off disposition, cleanup transaction, W10 raw inventory와 producer는 repository-external execution material이며 Iris regular validator/schema/claim authority가 아니다.
- final measurements:
  - clean tracked: 1,753 files / 71,766,663 Git blob bytes
  - clean physical: 1,753 files / 72,344,398 bytes
  - custody physical: 1,753 files / 72,154,554 bytes; Iris ignored/untracked/filesystem-only/reparse = 0
  - current capsule: 133,094 bytes / hard ceiling 2,359,296 bytes
  - successor overhead: 1,653,400 bytes / ceiling 3,037,162 bytes
  - unsupported keep / remaining eligible removal / unimplemented removal / unresolved blocker / retained exception: 모두 0
- compact documentary readpoint: `docs/iris_lightweighting_terminal_closeout.json`
- W10 packet: repository-external `C:/Users/MW/i/physical-capacity-iris-lightweighting-terminal-inv-terminal-w10-801f15f678fe-termin-6bf8179bacfa/terminal-inventory-result/w10_packet.json`, SHA-256 `d6015d4385f8da6625ebe14304775797db9c5c799398309d4164401a62ce012d`
- independent review: `c2b9514f..9882ce6d` 검토 결과 actionable finding 0; final `complete` 전환 조건 충족
- documentary integration:
  - machine validation과 W10의 implementation subject는 `801f15f6`으로 고정한다.
  - Reviewer가 확인한 documentary carrier는 `9882ce6d`이고, review 결과를 반영한 completion carrier `28f95b63`은 local `main`에 fast-forward 통합했다.
  - completion 이후의 문서 동기화는 docs-only이며 machine PASS, W10 또는 Reviewer PASS의 subject를 새 문서 commit으로 재귀속하지 않는다.
  - remote push는 수행하지 않았고 `Echo/bin`, `Pulse/bin`, `pulse-api/bin`, `pulse-api/build`의 기존 untracked state는 Iris 작업 범위 밖으로 보존한다.
- Non-decision: runtime 성능, 실제 token 절감률, release/publish/Workshop/deployment readiness를 주장하지 않는다.

### Iris build/validation — typed execution, current-authority convergence, owner-disposed closeout

- 날짜: 2026-08-27
- 상태: current adopted; implementation/machine validation complete; plan-process closeout complete by owner disposition
- 결정:
  - Installed `iris_tooling` package가 offline build/validation의 current import와 command implementation을 소유한다. Description-tree predecessor copy는 current import, command 또는 fallback authority가 아니다.
  - Supported execution boundary는 domain payload를 `PhaseInput` / `PhaseOutput`으로 운반하고, stable 의미는 `CanonicalSemanticResult`, run ID·elapsed·process/environment 같은 실행별 관측은 `ExecutionEnvelope`로 분리한다.
  - 공통 `PhaseRunner`는 dependency ordering, run-local reuse, metric, issue/artifact association만 담당하는 thin orchestration owner다. Build/validation domain verdict와 payload ownership은 각 domain에 남는다.
  - Canonical CLI는 existing validation authority의 thin adapter이며 unknown input과 identity mismatch를 fail-loud 처리한다.
  - 같은 clean-checkout full gate의 current-output seed는 staging에서 producer 3개를 한 번 실행한 뒤 completeness/content identity를 확인하고 immutable final seed와 case-local clone으로 공급한다. Producer invocation은 `6 → 3`이며 mutation/tamper isolation과 fresh-process A/B independence를 유지한다.
  - Human command literal owner는 `Iris/build/ENTRYPOINTS.md`로 수렴하고 static route index는 machine navigation projection으로 유지한다. 별도 human navigation projection은 두지 않으며 Iris planning/implementation bootstrap은 `docs/Philosophy.md`, `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`를 직접 읽는다.
  - Predecessor retirement denominator는 `32 distinct basename intersections - 1 non-substantive __init__.py = 31 substantive distinct basenames`, 그리고 두 basename의 nested D16 extra copy를 더한 `33 concrete predecessor files`다. Terminal 결과는 live substantive intersection `31 → 0`, concrete predecessor file `33 → 0`, 분류 `5 exact + 28 diverged`다. Nested D16 copy는 neutral protected fixture가 아니다.
  - Round3 current-route listing의 103은 routing membership이며 canonical full-gate pytest denominator가 아니다. Canonical gate는 pytest `211 → 211`, required standalone validation `4 → 4`, recurring execution unit `211 + 4 = 215 → 215`로 유지한다. Parameterized named case, `subTest` constituent assertion, migration-only script, external census, Reviewer-only check와 unregistered temporary validation은 이 identity denominator에 더하지 않는다.
  - G5 compiler identity는 append-only다. 0016은 execution-boundary 변경으로 달라진 19-path closure를 결속했고, 0017은 identity owner와 production dependency `execution.py`를 더한 21-path closure를 결속한다. 0013–0016을 재작성하거나 전체 chain을 재번호링하지 않으며 current required paths는 0016 뒤에 0017을 누적 보존한다. 그 retention-list correction은 compiler closure bytes를 바꾸지 않았으므로 0018을 만들지 않는다.
  - Exact package-source subject `c334ee97f0c01fb826309a6fb5388e99bde518d7`에서 wheel/fresh environment를 만들고 machine-validation subject `7a6e8ef9e9c29d5986872b08bdbeded5f086b536`에서 Run A/Run B/comparator가 PASS했다. Independent Reviewer의 actionable finding은 0이며 product/runtime/Lua mutation은 0이다.
  - W0 pre-implementation elapsed/projected-time `ADMIT` artifact는 external custody에 보존되지 않았다. `w0_census.json`은 admission evidence가 아니고 Reviewer PASS나 관측 timestamp도 이를 재구성하지 않는다. 이 사실은 unresolved record로 유지하되 owner disposition으로 plan-process closeout을 complete 처리했으므로, 새 owner instruction이나 새 current authority 없이 미래 작업 항목으로 재개방하지 않는다.
- Documentary identity:
  - adopted plan carrier: `e0d22781e0595abfd07da82150219d39969f6d4a`
  - final machine PASS subject: `7a6e8ef9e9c29d5986872b08bdbeded5f086b536`
  - reviewed closeout carrier: `b3045c82ea1b523fd27ecdf46528aaca61003ca4`
  - Walkthrough carrier: `7f94374546cd21bba29f70ed5b03821751bc586b`
  - denominator/admission correction carrier: `534671972b43ddd12a116a291d5471dacb1f24ab`
  - owner-disposition completion carrier: `65014b091951d2c152e6b9180a7da9f609f3f833`
  - 뒤의 docs-only carrier는 machine PASS나 Reviewer subject를 재귀속하지 않는다.
- Physical closeout snapshot, product S0 `e6310737` → Walkthrough carrier `7f943745`:
  - Iris: `1,753 files / 71,766,663 Git blob bytes → 1,731 / 70,970,753`, delta `-22 / -795,910`
  - whole repository: `6,935 files / 142,715,144 Git blob bytes → 6,917 / 142,003,274`, delta `-18 / -711,870`
  - source diff: `65 files changed, 3,259 insertions, 22,193 deletions`
- 상세 readpoint:
  - `docs/iris_build_validation_execution_current_authority_optimization_plan.md`
  - `docs/iris_build_validation_execution_current_authority_optimization_walkthrough.md`
  - `docs/iris_build_validation_execution_current_authority_optimization_closeout.md`
- 오독 금지:
  - Physical Git blob/context surface 감소를 PZ runtime, wall-clock 또는 실제 GPT/Codex token 성능 개선으로 읽지 않는다.
  - Build/validation closeout을 freeze, RTC, Publish, release, Workshop 또는 deployment readiness로 읽지 않는다.
  - W0 admission artifact 미보존 사실을 사후 evidence 생성, exemption, 새 validator/receipt/manifest/seal 또는 자동 재개방 권한으로 읽지 않는다.
  - Docs-only correction을 unchanged machine subject의 confidence rerun이나 새 validation authority로 읽지 않는다.

### Iris Tooltip T3-D1 — existing context integration

- 날짜: 2026-08-30, 사용자 명시적 콘텐츠 결정.
- 대상은 `docs/iris_tooltip_t3_d1_layer3_menu_tooltip_display_en_record_fact_relation_consistency_plan.md` §4.2의 exact 12개다. 현재 `dvf_3_3_facts.jsonl`의 non-empty `special_context` 기존 문구 **전체**와 기존 EN 대응을 일반 Menu 설명에 통합한다.
- 최종 사용자 편집 지시에 따라 primary-use를 의미의 중심으로 유지하고 context의 대상·상황·작업 디테일을 녹여 KO·EN 일반 설명을 자연스럽게 다듬는다. 원문을 기계적으로 연결하거나 context로 기본 용도를 대체하지 않는다. 기본 의미와 채택된 디테일은 보존하되 중복 문장은 정리한다. 기존 양언어 문구 범위 안의 bounded 편집은 허용하지만 새 게임 사실·추가 용도·추천·평가는 추가하지 않는다. source-bound public acquisition은 기존대로 보존한다.
- 이 exact 범위에서는 기존 `special_context/origin_missing` review hold를 기본 Menu body 전체의 공개 blocker로 사용하지 않는다. 과거 `L3R-MAP-008` 판정과 원본 `fact_origin`은 보존한다. 이번 결정은 기존 문구의 사용자 콘텐츠 채택이며 독립 게임 source 검증이나 과거 source approval의 소급 생성이 아니다. 다른 source 조합의 admission 원칙은 변경하지 않는다.
- 현재 approved `candidate_rendered.json`의 metadata에 이 채택 범위·기존 source fragment identity·편집된 KO/EN 일반 설명을 결속하고, 기존 complete-generation/EN producer로 output을 생성한다. EN producer는 이 채택된 통합 문장을 사용한 뒤 context를 다시 붙이지 않는다. Metadata는 해당 production input의 material/lineage이며 별도 Registry/validator가 아니다.
- primary-use scalar, single core fact ID와 Tooltip S2 KO/EN surface는 유지한다. Context는 Menu 설명의 추가 깊이로 제공하며 S2에 이어 붙이지 않는다. `special_context` 전역 schema/key/reader 폐기는 이번 범위 밖이다.
- Final actual EN producer/input/output/consumer 연결, preservation 및 기존 필수 gate는 별도로 검증한다. 이 결정만으로 independent Menu evidence 또는 D1/T3 completion을 선언하지 않는다. Sealed T1 unverified 이력과 original T3 package/install/PZ/visual 의무는 보존한다.

### Iris Tooltip T3-D1 — Build 41 content correction

- 2026-08-30 사용자가 exact 12개의 Build 41 정정 문구를 새로 지정했다. 이 지시는 직전 기존 primary-use 의미 보존 및 context 통합 결과보다 우선한다. `candidate_rendered.json`의 `general_description_integration.entries`에 채택된 KO/EN 문장과 predecessor/current scalar fact identity를 둔다.
- 같은 12개의 `primary_use`와 `special_context`를 정정 문구로 갱신한다. 잘못된 기존 일반 용도를 S2에 보존하지 않는다. EN은 동일 정정 의미를 번역하고 중복 출력하지 않는다. 다른 fact field·아이템, acquisition, Layer 2/4는 유지한다. `special_context` 전역 폐기는 하지 않는다.
- 제공된 PZwiki 링크는 사용자 참고자료다. 이번 채택은 사용자 콘텐츠 수정이며 독립 source/번역 품질 검증 claim이 아니다. 기존 origin category는 유지하되 이를 새 정정 문구의 독립 검증 provenance로 주장하지 않는다. Source manifest와 existing approved input의 current hash를 재결속하고 과거 raw/hash는 역사로 보존한다.
- 변경된 primary-use scalar ID는 owner·T1 strict handoff·T2 data·T3 product까지 기존 경로로 전파한다. Initial 1,314 pair ledger를 유지하면서 exact 12개 before/after fact 관계를 별도로 명시한다. Required FullType membership을 줄이거나 count로 성공을 대체하지 않는다. 기존 T1 P-1~P-12 선택은 불변이고 current input 때문에 바뀐 bundle hash만 재결속한다.
- 이전 `dvf33-dfdef534…`/`a1/menu-final-1.txt`의 성공은 superseded content subject의 결과이며 새 정정본의 final evidence가 아니다. 새 정정 후 필수 검증만 수행하며 gate/membership·승인 경계를 약화하지 않는다.

D1 generation 전환의 조건부 downstream binding: T1 strict admission에서 Layer 2 resolution registry의 pointer hash와 기존 D5 두 exact Lemongrass target의 generation-qualified locator/owner-row hash가 stale임이 드러났다. Layer 2의 모든 category/title/row 선택과 D5의 두 identity·support disposition·origin decision은 불변이다. 현재 입력 binding만 새 generation으로 재결속했다. D5의 `source_census_sha256`는 기존 코드가 정의하는 applicability material hash이며 새 source truth 조사 주장이 아니다. 두 target은 기존 generation row와 source/Layer2/Layer4 및 owner semantic/surface가 동일하고 owner authority-ref만 새 generation을 가리킨다. 최초 issuance/approval provenance는 원래 결정 이력으로 유지하며 current binding 갱신 권한은 이번 D1 owner 사전 승인이다. Historical 원본은 기존 commit에 보존되고 detector/predicate/validator는 수정하지 않는다. Existing decision contract의 P-1~P-12 선택도 그대로이며 aggregate input hash만 갱신한다.
