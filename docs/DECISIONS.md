# DECISIONS.md

> 상태: current decision ledger / compact trace-dedup edition through 2026-08-10
> 기준일: 2026-08-10
> 상위 기준: `Philosophy.md`
> 목적: Pulse 생태계에서 이미 사실상 고정된 결정을 짧게 봉인하고, 같은 논쟁의 반복을 줄인다.

> 편집 노트: 이 문서는 날짜순 회의록, closeout report, 실행 로그, ARCHITECTURE 대체물이 아니라 **current decision ledger**다. 기존 항목은 원래 heading 수를 보존하지 않고, 모듈별 decision family 중심으로 압축한다. 반복 evidence/hash/validation ceiling/non-decision 상세는 공통 앵커와 원본 archive read point로 흡수한다.

## 문서 규칙

* 이 문서는 **할 일 목록**이 아니라 **이미 내려진 결정**을 기록한다.
* 이 문서의 기본 정렬 기준은 날짜가 아니라 **모듈 → decision family → current readpoint → predecessor trace**다.
* 날짜는 삭제하지 않되, 항상 실제 결정일로 단정하지 않는다. 특히 2026-03-16 이후 문서화 과정에서 과거 판단이 한 날짜에 import되었을 수 있으므로, 날짜는 `origin / ledgered / imported / refined / sealed` 성격의 trace metadata로 읽는다.
* 동일 decision family 안에서는 가장 나중 날짜가 아니라, 항목에 명시된 **current readpoint**를 authoritative 기준으로 읽는다.
* 같은 round lifecycle은 하나로 합치고, 같은 날짜라도 decision family가 다르면 분리한다.
* superseded / reopened / blocked / rejected 항목은 삭제하지 않고, current readpoint 아래의 **Predecessor trace**로 격하한다.
* 각 항목은 가능하면 `상태 / 결정 / 현재 기준 / 영향 / Predecessor trace / Non-decision / Trace` 구조로 적는다. 필요 없는 필드는 생략할 수 있다.
* 구현 세부 실험 로그, 반복 hash 목록, 전체 validation command, closeout 전문은 여기 넣지 않는다.
* 검증 수치·hash·command는 current decision을 이해하는 데 필요한 **최소 결과 trace**로만 남긴다.
* 후속 작업의 input이 되는 artifact path는 보존한다.
* release readiness, runtime rollout, Workshop/public exposure, publish/runtime state mutation 오독 금지는 적극적으로 남긴다. 단, 반복 문구는 COMMON anchor로 흡수한다.
* `Philosophy.md`와 충돌할 경우, `Philosophy.md`가 우선한다.

## Compact Trace Anchors

* 목적: 반복 evidence, validation ceiling, non-decision, hash/path 목록을 공통 앵커와 원본 archive read point로 흡수해 token cost를 낮춘다.
* 보존: decision family heading / 날짜 trace / 상태 / 핵심 결정 / 현재 기준 / 최소 결과 trace / 후속 input artifact path / 특수 non-decision label.
* 생략: 반복 artifact path/hash 목록, 전체 validation ceiling, 반복 비결정 문구, 세부 실행 로그, closeout 전문.
* `COMMON-RELEASE-NONDECISION`: runtime rollout, deployed closeout, manual/in-game QA, Workshop/release readiness, public exposure, `ready_for_release` 선언 아님.
* `COMMON-RUNTIME-SURFACE-NONMUTATION`: source facts/decisions, rendered text, runtime Lua, packaged Lua, bridge/runtime payload, `quality_state`, `publish_state`, `runtime_state` mutation 아님.
* `COMMON-EVIDENCE-TRACE`: 상세 artifact/hash/validation command는 원본 `DECISIONS.md` archive read point에 보존된 것으로 읽는다.

---
## Pulse

### Pulse Core — 얇고 중립적인 플랫폼

* 상태: current readpoint / pre-ledger imported
* 결정: Pulse Core는 **얇고 중립적인 모드로더 겸 플랫폼**으로 유지한다.
* 현재 기준:

  * Pulse는 특정 프로파일러, 최적화 모드, 킬러앱 전용 런처가 아니다.
  * Pulse Core는 Echo, Fuse, Nerve, Iris, Frame, Cortex, Canvas 같은 하위 모듈을 참조하거나 의존하지 않는다.
  * 하위 모듈 간 직접 참조도 금지한다.
  * 하위 모듈 간 협력이 필요하면 Pulse capability 또는 SPI를 경유한다.
  * Core는 공용 기반만 제공하고, 실제 관측/안정화/최적화/위키/팩 관리 로직은 각 모듈 내부에 둔다.
  * Core에는 프로파일링, 엔진 최적화, Lua 최적화 로직을 넣지 않는다.
* 영향: Pulse Core는 하위 모듈의 역할을 먹지 않고, 플랫폼 품질·호환성·진단 능력으로 1st-party 모드와 외부 모드를 받치는 기반층으로 남는다.
* Trace:

  * ledgered: 2026-03-16 documentation consolidation
  * COMMON-EVIDENCE-TRACE.

### Pulse — Hub & Spoke / SPI / 모듈 분리 원칙

* 상태: current readpoint
* 결정: Pulse 생태계의 기본 구조는 **Hub & Spoke + SPI 우선 구조**로 둔다.
* 현재 기준:

  * Pulse는 Hub이며, 하위 모듈은 Spoke다.
  * 하위 모듈은 Pulse 기능을 참조할 수 있지만, Pulse는 하위 모듈을 참조하지 않는다.
  * Echo는 관측, Fuse는 엔진 안정화, Nerve는 Lua 안정화, Iris는 위키형 정보 계층, Frame은 팩 상태 관리, Canvas는 리소스 적용 상태 관리로 분리한다.
  * Core와 1st-party 모드는 `Pulse Core / pulse-profiler / pulse-engine-optim / pulse-lua-optim` 식으로 역할을 분리한다.
  * 공용 확장 경로는 SPI 중심으로 설계한다.
  * 구체 정책, helper, 편의 기능은 Core가 아니라 하위 모듈 또는 Cortex 같은 격리 구역으로 보낸다.
* 영향: Pulse Core는 안정적인 surface를 제공하고, 구체 정책은 하위 모듈이나 외부 모드가 담당한다.
* Trace:

  * ledgered: 2026-03-16
  * COMMON-EVIDENCE-TRACE.

### Pulse — 호환성 / 성숙도 / Core 오염 방지

* 상태: current readpoint
* 결정: Pulse Core의 최우선 가치는 기능 수가 아니라 **호환성, 안정성, 진단 능력, 오염 방지**다.
* 현재 기준:

  * 타 모드와의 호환성을 1순위 원칙으로 둔다.
  * Core 설계는 공격적인 정책/판단보다 충돌 완화, 진단, 안정성에 우선권을 둔다.
  * 예외 격리, mixin 진단, API 안정성, DevMode/로깅은 상위 우선순위를 가진다.
  * Pulse Core에는 helper/편의/가이드 성격 기능을 넣지 않는다.
  * helper성 기능은 `Pulse에 있어도 되지 않나`라는 이유만으로 Core에 승격하지 않는다.
  * 플랫폼 실패 회피의 핵심은 기능 수 보강이 아니라 **플랫폼 오염 방지와 설치·실행 마찰 제어**다.
* 영향: Core는 끝까지 빈 기반에 가깝게 유지하고, 설치/실행 UX는 새 플랫폼을 강요하는 느낌보다 기존 플레이 흐름을 거의 바꾸지 않는 방향으로 설계한다.
* Trace:

  * ledgered: 2026-03-16
  * refined: 2026-03-23 Core 오염 방지 재확정
  * COMMON-EVIDENCE-TRACE.

### Pulse — capability와 policy 분리

* 상태: current readpoint
* 결정: Pulse는 **측정값과 capability는 제공할 수 있지만, 정책·판단·편의 fast-path는 보유하지 않는다.**
* 현재 기준:

  * 허용: 거리, 상태, tick, phase, hook, state, DTO, observation event 같은 기반 surface.
  * 금지: `근거리면 FULL`, `under pressure`, `이 모듈이 처리해야 함`, `이게 중요함` 같은 정책/판단.
  * 실제 governor 정책은 Fuse/Nerve 같은 하위 모듈이 가진다.
  * `IPulseDataBus`류의 범용 모드 간 실시간 중개 채널은 채택하지 않는다.
  * 허용 가능한 것은 필요 시 observation event 표준화 수준까지다.
* 영향: Pulse는 정책 주입이나 실시간 조정의 중심이 아니라, 모듈들이 자기 판단을 수행할 수 있게 하는 최소 기반 surface만 제공한다.
* Trace:

  * ledgered: 2026-03-17
  * COMMON-EVIDENCE-TRACE.

### Pulse — Primitive Data Sharing v3 / Echo-Fuse 경계

* 상태: current readpoint
* 결정: Primitive Data Sharing 리팩토링은 **객체 공유 제거 + Echo/Fuse 경계 고정**이라는 의미로 v3를 채택한다.
* 현재 기준:

  * `updateSnapshot()` 호출은 Echo 내부 tick 경로에서만 수행한다.
  * 공용 계약은 raw observation 최소선으로 제한한다.
  * `targetId`, `severity` 같은 snapshot 필드는 관측 계약으로만 사용한다.
  * recommendation 생성과 실제 적용은 Fuse 내부 책임으로 남긴다.
  * 기존 `OptimizationHint`류 경로가 남더라도 legacy 호환용이지 중심 경로가 되어서는 안 된다.
* 영향: Echo는 관측자, Fuse는 판단자로 유지되며, Pulse는 양쪽을 실시간 정책 채널로 연결하지 않는다.
* Trace:

  * ledgered: 2026-03-17
  * COMMON-EVIDENCE-TRACE.

### Pulse — API 확장 원칙

* 상태: current readpoint
* 결정: Pulse API 확장은 API를 늘리기 위한 작업이 아니라, **바닐라의 기반 기능 후보 추출 → 진짜 기반인지 판정 → 중립적으로 노출 가능한 것만 API화**하는 순서로 진행한다.
* 현재 기준:

  * 초기 Pulse Core는 거대한 고레벨 정책 API보다 얇고 안정적인 공용 API를 우선한다.
  * 기반 후보 추출 이전의 무차별 API 증설은 열지 않는다.
  * API surface 평가는 언제나 `중립 노출 가능한가`를 마지막 게이트로 둔다.
  * 구체 정책, 헬퍼, 편의 기능은 가능한 한 하위 모듈 또는 Cortex 격리 구역으로 미룬다.
* 영향: Pulse API는 기반 capability로만 확장하며, 모듈별 정책이나 편의성 기능을 Core에 흡수하지 않는다.
* Trace:

  * ledgered: 2026-03-16
  * refined: 2026-03-23
  * COMMON-EVIDENCE-TRACE.

### Pulse — 보수적 리팩토링 원칙

* 상태: current readpoint
* 결정: Pulse 생태계의 리팩토링은 아키텍처를 새로 그리는 작업이 아니라, **헌법·핫패스·외부 계약·실제 코드 상태를 깨지 않는 범위에서만 수행하는 보수적 정리 작업**으로 한정한다.
* 현재 기준:

  * 모든 리팩토링 로드맵은 `실제 코드 확인 후 축소/스킵 가능`을 전제로 한다.
  * 핫패스·구조·DI·리포트 경계에 손대는 작업은 Phase 0 기준선 확보 없이는 착수하지 않는다.
  * EchoProfiler는 `큰 클래스`라는 이유만으로 분해하지 않으며, hot-path field/method access 동등성이 증명될 때만 조건부로 연다.
  * ReportDataCollector 계열은 외부 `Map<String, Object>` 반환 계약을 유지한다.
  * FuseThrottleController는 이미 추출된 경계가 있으면 해당 stage를 스킵할 수 있으며, 추가 분해보다 실제 경계 확인을 우선한다.
  * DI는 전면 전환 프로젝트가 아니라, 기존 `ServiceLocator / PulseServices / 생성자 주입 / fallback` 공존 현실을 규약화하고 누락을 정리하는 과제다.
  * 새 GuardTest, 새 ServiceLocator, 새 snapshot infra, 성급한 BaseConfig 공통 모듈보다 기존 `HubSpokeBoundaryTest`, `PulseServiceLocator`, 하드코딩 기대값 테스트, 인터페이스 통일을 우선 강화한다.
  * 경계 테스트는 실제 존재하고 현재 리팩토링 대상인 Echo, Fuse, Nerve 기준으로만 고정한다.
* 영향: 과잉 구조 개편, `getInstance()` 전면 철거, fallback 전면 제거, 미래 모듈을 가정한 경계 규칙 확대는 기본값으로 금지한다.
* Trace:

  * sealed: 2026-03-20
  * COMMON-EVIDENCE-TRACE.

### Pulse EventBus — 3계층 현실 경로와 COW 등록 구조

* 상태: current readpoint
* 결정: EventBus 리팩토링은 이상적 타입 순수성을 목표로 하지 않고, **핫패스를 빠르게 만들면서도 ClassLoader/모드 호환성을 유지하는 현실 경로**로 진행한다.
* 현재 기준:

  * 호출 경로 우선순위는 `direct class lookup → FQCN O(1) fallback → 제한적 reflection/호환 호출` 순서다.
  * FQCN/reflection 완전 제거는 현재 목표가 아니다.
  * 리스너 저장 구조는 단일 `CopyOnWriteArrayList`를 유지한다.
  * 정렬은 등록 시점 `add + sort`로 끝내는 방향을 우선한다.
  * immutable list 교체, compute 내부 새 리스트 생성, 이진 삽입 중심 복잡 구현은 기본 노선으로 채택하지 않는다.
* 영향: EventBus 작업은 기본 경로 비용 절감과 fallback 비용 제한을 우선하며, 기존 COW 성질을 깨는 구조 개편은 피한다.
* Trace:

  * sealed: 2026-03-20
  * COMMON-EVIDENCE-TRACE.

### Pulse — 공개 전략과 플랫폼 후노출

* 상태: current readpoint
* 결정: Pulse의 채택 전략은 플랫폼 선공개가 아니라, **제품이 먼저 가치를 입증하고 플랫폼은 그 기반으로 후노출되는 방식**으로 둔다.
* 현재 기준:

  * Pulse는 Leaf/Avrix/Storm류의 전면형 Java 로더 경쟁 구도로 자신을 정의하지 않는다.
  * Pulse는 킬러앱이 먼저 가치를 입증한 뒤 나중에 기반으로 드러나는 **샌드박스형 공통 지반**으로 남는다.
  * 플랫폼 서사는 제품보다 앞서지 않는다.
  * 공개/README/배포 문구는 `새 표준 선언`보다 `기반 품질이 결과물을 받친다`는 방향으로 정리한다.
  * 공개 전략은 **Iris → Nerve → Fuse → Pulse+Echo → Nerve+ / Fuse Pulse 의존 전환** 순의 역방향 공개를 기본선으로 둔다.
  * `플랫폼 먼저 공개` 루트는 기본 전략에서 닫는다.
* 영향: Pulse는 검증된 결과물 묶음의 공통 기반으로 소개하며, 플랫폼 자체를 먼저 홍보하거나 특정 킬러앱 전용 런처처럼 보이게 하지 않는다.
* Trace:

  * ledgered: 2026-03-16
  * refined: 2026-03-23
  * COMMON-RELEASE-NONDECISION.

### Pulse — Philosophy.md와 공개 전략 문서 분리

* 상태: current readpoint
* 결정: `Philosophy.md`는 구조 원칙, 금지선, 역할 경계 중심의 **헌법 문서**로 유지하고, 킬러앱/가능 구역/홍보 문구 같은 공개 기대 관리 요소는 별도 `ReleaseStrategy` 계열 문서로 분리한다.
* 영향: 향후 공개 메시지는 헌법 본문이 아니라 별도 전략 문서에서 관리하고, 헌법은 `무엇을 하지 않는가`를 더 또렷하게 유지한다.
* Trace:

  * ledgered: 2026-03-17
  * COMMON-EVIDENCE-TRACE.

### Pulse — 브랜드 후보

* 상태: working name / unresolved legal-final
* 결정: 브랜드 후보군 중 현재 기준 최우선 후보는 `Pulse`다.
* 영향: 최종 확정 전까지는 Pulse를 작업명/우세 후보로 사용하되, 법적 검토나 최종 확정으로 취급하지 않는다.
* Trace:

  * ledgered: 2026-03-16
  * COMMON-EVIDENCE-TRACE.

---
## Echo

### Echo — 순수 관측자 원칙

* 상태: current readpoint
* 결정: Echo는 Fuse/Nerve를 움직이는 정책 엔진이 아니라, **시스템을 흔들지 않는 순수 관측자**로 둔다.
* 현재 기준:

  * Echo는 병목과 상태를 기록하지만, Fuse/Nerve의 행동을 실시간으로 유도하지 않는다.
  * Echo가 `severity / top_target / insight / hint / recommendation`류 값을 통해 Fuse 행동을 실질적으로 유도하는 구조는 직접 추천 API가 아니더라도 금지한다.
  * Echo 관측값은 사후 분석과 리포트 판독 자료로만 쓰며, Fuse/Nerve는 각자 자기 내부 pressure signal, governor, guard 판단으로 동작한다.
* 영향: Echo는 사실을 기록하고, Fuse/Nerve는 자기 내부 정책만으로 행동을 결정한다.
* Trace:

  * ledgered: 2026-03-17
  * COMMON-EVIDENCE-TRACE.

### Echo — 핫패스 무해화 원칙

* 상태: current readpoint / closed implementation round trace
* 결정: 과거 Bundle A 라운드는 current 설계 단위가 아니라, Echo 핫패스에서 **No-Throw / Fast-Exit / Fail-Soft / Safe Default** 원칙을 회복한 무해화 라운드로만 보존한다.
* 현재 기준:

  * Echo 핫패스는 다음 4종으로 고정한다.

    * tick 계측 entry/exit
    * scope push/pop
    * `SpikeLog.logSpike`
    * deep analysis 훅 콜백 수신부
  * 이 경로에서는 `PulseServices`, `EchoConfig` 직접 조회, ServiceLocator/DI, 파일/JSON/문자열 포매팅, `synchronized`/blocking queue, MXBean/Thread/StackWalker, throw/catch 남용을 금지한다.
  * 핫패스는 외부 설정/서비스를 직접 읽지 않고, 느린 경로에서 갱신되는 `EchoConfigSnapshot` + `EchoRuntimeState` 구조를 사용한다.
  * `volatile` 단일 스냅샷 참조를 기본으로 두며, `current()`는 null/throw를 허용하지 않는다.
  * release 운영 경로는 완전 무음이어야 하며, debug mode에서만 세션당 1회 원샷 경고를 허용한다.
  * Spike context capture는 옵션적 느린 경로로 격리하고, CAS 기반 rate-limit와 완전 무음 실패를 기본으로 둔다.
* 영향: Echo 핫패스는 문서로 봉인된 감사 대상이며, Bundle A 이후 핫패스 변경은 PR 수준 사유 없이는 다시 열지 않는다.
* Trace:

  * closed round: 2026-03-17 Bundle A
  * COMMON-EVIDENCE-TRACE.

### Echo — 느린 경로 / 디버그 경로 격리

* 상태: current readpoint
* 결정: Echo의 운영 경로와 느린 진단 경로는 의식적으로 분리한다.
* 현재 기준:

  * 릴리즈에서는 운영 경로가 완전 무음이어야 한다.
  * 디버그 모드에서만 제한적 원샷 경고를 허용한다.
  * `safeContextCapture()`는 실패를 절대 전파하지 않는다.
  * 느린 경로의 진단 기능은 핫패스 안정성을 침해하지 않는 범위에서만 허용한다.
* 영향: 개발 단서는 제한적으로 제공하되, Echo가 관측 과정에서 게임 실행이나 Fuse/Nerve 동작을 흔들지 않도록 한다.
* Trace: COMMON-EVIDENCE-TRACE.

### Echo — provider 증명 파이프와 `0` 분해 규약

* 상태: current readpoint / closed implementation round trace
* 결정: 과거 Bundle B 라운드는 current 설계 단위가 아니라, **Fuse 개입 리포트에서 `0`의 의미를 구조적으로 분해 가능하게 만든 증명 파이프 복구 라운드**로만 보존한다.
* 현재 기준:

  * Echo 리포트는 Fuse가 실제로 동작했는지, 왜 동작했는지, 왜 아무 개입이 없었는지, `0`이 실제 무개입인지 provider/snapshot/read 실패인지 구분 가능해야 한다.
  * 최소 증명 단위는 `present / active / snapshot_ok / total_interventions / reason_counts`로 고정한다.
  * `0`은 단일 숫자가 아니라, 위 필드와 `error_code`를 통해 무개입 / 비활성 / 미등록 / 조회 실패 / snapshot 실패로 분해되어야 한다.
  * `present`는 provider가 보고하지 않고, **Echo가 registry 조회 결과로만 결정**한다.
  * `active`, `snapshot_ok`, `total_interventions`, `reason_counts`, `error_code`는 provider snapshot이 자기 상태로 보고한다.
  * `providers` 섹션은 deep analysis 옵션과 무관하게 항상 기록한다.
  * `echo_profilers` 같은 부가 분석은 옵션일 수 있지만, provider 증명 파이프는 옵션화하지 않는다.
* 영향: Echo는 “부재의 증명은 관측자만 할 수 있다”는 원칙 아래, provider와 Echo의 책임을 리포트 필드 단위로 분리한다.
* Trace:

  * closed round: 2026-03-17 Bundle B
  * COMMON-EVIDENCE-TRACE.

### Echo — 과거 Bundle A/B/C 명칭 처리

* 상태: closed lifecycle trace
* 결정: Bundle A/B/C는 현재 Echo의 모듈 구조나 진행 중인 설계 단위가 아니라, **이미 끝난 구현·검증 라운드의 명칭**으로만 보존한다.
* 현재 읽기:

  * Bundle A는 Echo 핫패스 무해화 라운드였다.
  * Bundle B는 Echo/Fuse 리포트 증명 파이프 복구 라운드였다.
  * Bundle C는 Echo의 current 설계 단위가 아니라 Fuse 쪽 sustained overload 자기규제 라운드의 명칭으로만 읽는다.
  * `A 다음 B`, `B 다음 C`, `C를 고도화` 같은 식으로 현재 작업 순서를 열지 않는다.
* 영향: Echo 섹션에서 Bundle 명칭은 current heading이 아니라 predecessor trace로만 남기며, current readpoint는 순수 관측자 원칙과 핫패스/리포트 계약이다.
* Trace:

  * closed lifecycle: 2026-03-17 ~ 2026-03-20
  * COMMON-EVIDENCE-TRACE.


---
## Fuse

### Fuse — 엔진 안정성 레이어

* 상태: current readpoint / frozen-mainline
* 결정: Fuse는 `AI 최적화 모드`, `평균 FPS 향상 모드`, `정책 엔진`, `엔진 포크`가 아니라, **AI 부하 폭주로 인한 엔진 붕괴 상태를 차단하는 semantic-preserving 엔진 안정성 레이어**로 둔다.
* 현재 기준:

  * 기본 레인은 **semantic-preserving**이다. 즉, 동일 결과를 더 싸게 만들거나 붕괴 상태에서 빠져나오는 최소 안정화만 허용한다.
  * 결과나 규칙이 달라질 수 있는 근사, 공격적 알고리즘 교체, 엔진 포크, AI 의미 변화는 기본 레인에서 제외한다.
  * 외부 메시지는 `평균 FPS 상승`보다 `평균 FPS 방어`, `끊김 감소`, `프레임 붕괴 방지`, `더 안정적인 플레이`를 우선한다.
  * Fuse는 PZ 전체 최적화기가 아니라, 비용 폭주가 확인된 구역에서 pressure signal, governor, backoff, cooldown, fail-soft를 이용해 붕괴 상태를 줄이는 모드다.
* 영향: README, 공개 문구, 테스트 설명은 `AI를 최적화한다`보다 `붕괴 상태를 차단한다`, `계속 망가진 상태를 오래 끌지 않게 한다`는 방향으로 정리한다.
* Trace:

  * ledgered: 2026-03-17
  * refined: 2026-03-20 실전 증명 이후 엔진 안정성 레이어로 재봉인
  * COMMON-EVIDENCE-TRACE.

### Fuse — 현재 운영 상태: 확장보다 동결 / 회귀 검증 / 설명 정리

* 상태: current readpoint
* 결정: Fuse는 과거 구현 라운드와 tick duration 입력 버그 수정이 끝난 현재, **추가 기능을 키우는 개발축이 아니라 동결·회귀 검증·설명 정리의 대상**으로 본다.
* 현재 기준:

  * 후속 작업은 새 정책 추가보다 regression guard, 문서화, README/포지셔닝, 판독 규칙 고정에 집중한다.
  * `autoOptimize` 같은 자동 판단 / 자동 적용 / 임계값 결정 경로는 남겨두지 않는다. 필요하면 `AUTO_OPTIMIZE_FROZEN`처럼 다시 켜기 어렵게 봉인한다.
  * tick-local cache, dedup, early-out, 자료구조 정리 같은 합헌적 미세 최적화는 이론상 열려 있으나, 현 시점 메인라인 우선순위로 채택하지 않는다.
  * Fuse 동결은 영구 폐쇄가 아니라 전략적 보류다. 필요하면 Area 1·7의 누락/봉인 상태 점검을 위한 **보수적 정산 작업**으로만 재진입할 수 있다.
* 영향: Fuse는 `미지 탐사 재개`가 아니라 **이미 알고 있는 위험 지대의 봉인 상태 확인** 범위에서만 후속 재진입을 검토한다.
* Trace:

  * sealed: 2026-03-20
  * COMMON-EVIDENCE-TRACE.

### Fuse — Echo와의 경계: 관측은 Echo, 판단은 Fuse

* 상태: current readpoint
* 결정: Echo는 병목의 **관측치만** 제공하고, Fuse는 임계값 판단 / recommendation 생성 / optimization 적용을 자기 내부에서만 수행한다.
* 현재 기준:

  * Echo는 category / targetId / severity 같은 raw observation에 머문다.
  * Echo가 `severity / top_target / insight / hint / recommendation`류 값을 통해 Fuse 행동을 실질적으로 유도하는 구조는 직접 추천 API가 아니더라도 금지한다.
  * Echo 관측값을 Fuse의 실시간 정책 입력으로 직접 사용하는 구조는 채택하지 않는다.
  * Fuse는 자기 pressure signal과 내부 상태를 기준으로 동작한다.
* 영향: Echo는 사실을 기록하고, Fuse는 자기 내부 정책만으로 행동을 결정한다.
* Trace:

  * ledgered: 2026-03-17
  * COMMON-EVIDENCE-TRACE.

### Fuse — 과거 구현 라운드 A/B/C는 current 설계 단위가 아니라 closed lifecycle trace다

* 상태: closed implementation round trace
* 결정: 과거의 Bundle A/B/C 명칭은 현재 Fuse의 설계 단위가 아니라, **이미 끝난 구현·검증 라운드의 명칭**으로만 보존한다.
* 현재 읽기:

  * A/B/C는 새 작업 순서나 current architecture가 아니라, 과거에 `무해화 → 증명 파이프 복구 → sustained overload 자기규제`를 순차적으로 닫기 위해 사용한 라운드명이다.
  * 이 명칭들은 후속 작업을 여는 근거가 아니라, 현재 Fuse가 왜 동결·회귀 검증·설명 정리 상태인지 설명하는 predecessor trace다.
  * `A/B/C를 다시 연다`, `B 다음 C를 해야 한다`, `C를 고도화한다`는 식으로 읽지 않는다.
* 영향: DECISIONS.md에서 Bundle A/B/C는 current readpoint heading으로 승격하지 않고, 닫힌 라운드의 최소 결과 trace로만 남긴다.
* Trace:

  * closed lifecycle: 2026-03-17 ~ 2026-03-20
  * COMMON-EVIDENCE-TRACE.

### Fuse — 과거 증명 파이프 복구 라운드의 결과만 보존한다

* 상태: predecessor trace / closed proof layer
* 결정: 과거 증명 파이프 복구 라운드는 **Fuse가 실제로 동작했는지, 왜 동작했는지, 왜 아무 개입이 없었는지, `0`이 실제 무개입인지 provider/snapshot/read 실패인지**를 Echo 리포트로 구분 가능하게 만든 라운드로 닫는다.
* 보존할 결과:

  * 최소 증명 단위는 `present / active / snapshot_ok / total_interventions / reason_counts`였다.
  * `0`은 단일 숫자가 아니라, `present / active / snapshot_ok / total_interventions / reason_counts / error_code`를 통해 무개입 / 비활성 / 미등록 / 조회 실패 / snapshot 실패로 분해되어야 한다는 규약을 남긴다.
  * `providers` 섹션과 핵심 증명 필드(`present / active / snapshot_ok / error_code / reason_stats`)는 후속 행동 레이어가 재설계하지 않는 동결 계약으로 취급한다.
* 현재 읽기:

  * 이 라운드는 current 개발축이 아니라, Fuse 리포트 판독을 가능하게 만든 닫힌 증명 계층이다.
  * 행동 정책 수정이나 새 개입 설계는 이 라운드의 current 의미가 아니다.
* 영향: 이후 Fuse 리포트에서 `0`을 단정적으로 해석하지 않고, provider/snapshot/read 상태와 함께 판독한다.
* Trace:

  * closed: 2026-03-17
  * COMMON-EVIDENCE-TRACE.

### Fuse — 과거 sustained overload 자기규제 라운드의 결과만 보존한다

* 상태: predecessor trace / proven and sealed
* 결정: 과거 sustained overload 자기규제 라운드는 Fuse가 ACTIVE에 너무 오래 붙어 지속 잔렉을 만들 수 있을 때, **더 강하게 개입하지 않고 손을 떼는 안전장치**를 닫은 라운드로 보존한다.
* 보존할 결과:

  * Fuse는 Burst stabilizer로 정의하고, sustained overload에서는 개입 강화가 아니라 **PASSTHROUGH / retreat**를 기본 정책으로 둔다.
  * sustained overload 대응의 핵심은 `Sustained 감지 + Early Exit + ACTIVE 상한 + COOLDOWN + PASSTHROUGH 강제 복귀`였다.
  * sustained 감지는 **ACTIVE 지속 시간 상한**과 **hard limit streak** 두 축으로만 본다.
  * 좀비 수, AI 무게, 외부 원인 같은 해석 기반 신호는 v1 범위에서 제외했다.
  * `isPassthrough()` 같은 기존 상태 의미는 재정의하지 않는다.
  * COOLDOWN은 평시 상태가 아니라 **개입 금지 상태**로만 취급한다.
  * ACTIVE / COOLDOWN / PASSTHROUGH 전이는 `transitionTo()` 같은 단일 관문에서만 수행한다.
  * hard limit streak는 `beginTick reset → hard limit hit에서 set → endTick에서 hit가 없을 때만 miss`의 3점 규약으로 봉인한다.
* 보존할 성공 판정:

  * `ACTIVE 장시간 유지 감소`
  * `PASSTHROUGH 강제 복귀 확인`
  * `hard_limit 연속 발생 감소`
  * `rolling stats 축적 → ACTIVE 진입 → 개입 기록 → Early Exit → COOLDOWN 복귀`의 관측
  * `p50 / FPS / 평균 성능`은 참고 지표일 뿐 공식 판정 기준이 아니었다.
* 현재 읽기:

  * 이 라운드는 current 고도화 과제가 아니라 이미 증명·봉인된 predecessor trace다.
  * 이후 Fuse 운영은 새 sustained 정책 추가가 아니라, 이 자기규제 결과가 회귀하지 않는지 확인하는 쪽이다.
* Trace:

  * proven: 2026-03-20 Stress 전장 관측
  * input bug fixed: AdaptiveGate가 Fuse 내부 처리 시간에 가까운 값이 아니라 실제 tick duration을 보도록 수정 필요 판정
  * COMMON-EVIDENCE-TRACE.

### Fuse — Area 1 / Area 7 중심축

* 상태: current readpoint / conservative re-entry candidate
* 결정: Fuse의 핵심 실전 가치와 보수적 재진입 후보는 **Area 1(좀비 AI / 업데이트 스텝)** 과 **Area 7(경로탐색 / 충돌 / 물리)** 축에 둔다.
* 현재 기준:

  * Area 7은 `guard / limit / defer / deduplicate / stabilize`만 허용하는 semantic-preserving 안정화 축으로 완료 판정한다.
  * Area 7은 신규 탐색 축이 아니라 유지·회귀 관리 대상으로 전환한다.
  * 경로 알고리즘 변경, 충돌 규칙 변경, 물리 결과 변경, AI 의미 변화는 기본 레인에서 제외한다.
  * Area 7 1차 범위에서는 `IPathfindingPolicy`류의 Pulse 정책 인터페이스, `/fuse status` 같은 UX/명령 체계, `LOSThrottleGuard`, 결과 변화로 이어질 수 있는 `NavMeshQueryGuard` null 반환, TTL 2틱 이상의 collision memo를 채택하지 않는다.
  * Pulse는 capability만 제공하고, Fuse Area 7은 defer-only / TTL=1 / fail-safe 중심의 안정화 설계로 고정한다.
* 영향: Fuse 재진입이 필요하다면 미지 탐사가 아니라 Area 1·7의 봉인 상태 확인, 회귀 방지, 누락 정산으로 한정한다.
* Trace:

  * Area 7 completed: 2026-03-17
  * Area 1/7 priority sealed: 2026-03-17
  * COMMON-EVIDENCE-TRACE.

### Fuse — Area 8 / Area 10은 메인라인 Guard가 아니라 종료·계측 잔존 surface

* 상태: current readpoint / completed then demoted
* 결정: Fuse의 Area 8(Save / IO Stall Guard)과 Area 10(GC / Allocation Pressure)은 완료 흔적을 인정하되, **메인라인 핵심 Guard로 유지하지 않고 제거/동결 방향을 기본 방침**으로 둔다.
* 현재 기준:

  * Area 8은 `SaveEventMixin`, `PreSaveEvent / PostSaveEvent`, `SaveEventState`, mixin 등록까지 실배선이 닫힌 상태를 완료 기준으로 인정한다.
  * Area 10은 GC를 제거하는 모드가 아니라, GC/heap pressure가 시스템을 무너뜨리는지 관측·판정·완충 가능한 상태를 만드는 것으로 완료 판정했다.
  * 그러나 IO/GC Guard는 mainline 핵심 기능으로 유지하지 않는다.
  * enum, reason, removed 표기, 리포트/로그용 계측·분류 흔적은 보수적으로 유지할 수 있다.
  * 재도입은 실험 브랜치에서 좁은 조건을 충족할 때만 검토한다.
* 영향: Area 8/10은 신규 구현 축이 아니라 책임 경계 확인 후 종료된 영역이며, mainline에서는 IO/GC 튜닝 반복보다 제거 실행과 계측 유지 범위 확정을 우선한다.
* Closed validation trace:

  * C 실전형 IO/GC OFF/ON 비교는 추가 반복 없이 종료한다.
  * 종료 이유는 효과가 없어서 포기가 아니라, 무엇이 Fuse 책임 경계 밖인지 충분히 밝혀졌기 때문이다.
* Trace:

  * completed: 2026-03-17
  * demoted: 2026-03-17 IO/GC Guard mainline 종료
  * COMMON-EVIDENCE-TRACE.

### Fuse — 검증 시나리오는 current task가 아니라 closed validation trace다

* 상태: closed validation trace
* 결정: S1~S5, Golden, Stress/Baseline/MP, OFF/ON 쌍 검증은 현재 해야 할 작업 목록이 아니라, **Fuse의 성격과 책임 경계를 닫는 데 사용된 검증 프레임 / 증거 trace**로 읽는다.
* 현재 읽기:

  * S1~S4 싱글 시나리오는 단순 성능 측정이 아니라 구조 검증선으로 정의되었으나, 현재는 future task가 아니라 닫힌 검증 trace다.
  * S1은 Fuse의 구조적 개입 증명, S2는 스트리밍/이동 경계 비개입 확인, S3는 바닐라 Lua 상시 병목 부정선, S4는 회귀/안정성 게이트로 쓰인 predecessor trace다.
  * S5 중심 멀티 검증과 MP 데이터 수집/재잠금 순서는 현재 우선순위가 아니라, 당시 멀티 검증 범위 축소와 책임 경계 확인을 위한 닫힌 운영 trace다.
  * Golden 검증은 실제 인게임 플레이로 재현·유지 가능한 시나리오만 인정한다는 기준으로 남긴다.
  * 억지 치트 구성이나 플레이 불가능한 고정 병목은 Golden 증거로 채택하지 않는다.
  * Stress / Baseline / MP의 2+1 체계는 현재 새 실험 계획이 아니라, 기존 A/B/C식 분류를 정리한 closed validation framework다.
  * 약한 A 계열 OFF/ON 데이터는 공식 Stress 기준선이 아니라 Baseline / Non-Interference 참고 자료로 격하 보관한다.
* 영향: 앞으로 DECISIONS.md에서 S1/S4/S5 같은 시나리오를 `다음에 해야 할 일`처럼 읽지 않는다. 필요한 경우 regression evidence나 historical validation trace로만 참조한다.
* Trace:

  * S1~S4 role sealed: 2026-03-17
  * S5 / MP scope reduced: 2026-03-17
  * 2+1 framework refined: 2026-03-20
  * Stress proof completed: 2026-03-20
  * COMMON-EVIDENCE-TRACE.

### Fuse — 테스트 전략은 학술형 대규모 반복이 아니라 운영형 검증이었다

* 상태: predecessor/current validation principle
* 결정: Fuse 테스트 전략은 학술형 대규모 반복 실험이 아니라, **폭주 재현 가능성이 높은 소수 시나리오에서 OFF/ON 중심으로 개입 경로와 의미 보존을 확인하는 운영형 검증**으로 정리한다.
* 현재 기준:

  * 이 항목은 새 테스트 캠페인 지시가 아니라, 과거 검증을 해석하는 원칙으로 남긴다.
  * 공식 판정은 평균 성능보다 구조 변화, 개입 경로 발동, 의미 보존, 회귀 여부에 둔다.
  * 시나리오 수는 소수로 압축하고, 전체 테스트는 재현성과 회귀 감시에 초점을 둔다.
* 영향: 이후 Fuse 검증을 다시 열더라도, 목적은 학술적 유의성 확보가 아니라 봉인된 guard가 의미 불변·회귀 없음·책임 경계 준수를 만족하는지 확인하는 것이다.
* Trace: COMMON-EVIDENCE-TRACE.

### Fuse / Nerve — 프리즈 책임 경계

* 상태: current readpoint
* 결정: `Fuse가 못한 프리즈를 Nerve가 대신 해결한다`는 식으로 역할을 잇지 않는다.
* 현재 기준:

  * Fuse는 엔진 측에서 분산 가능한 연쇄 폭주와 sustained overload 대응을 다룬다.
  * Nerve는 Lua 이벤트 폭주 / 중첩 / 중복 트리거 조건을 줄일 수 있지만, IO/GC 자체를 직접 흡수하거나 Fuse의 실패를 대체하는 역할로 두지 않는다.
  * 현재 Nerve의 `research / Failure Atlas` 프레이밍은 폐기되었으므로, Fuse/Nerve 경계 설명에서도 이를 current 근거로 쓰지 않는다.
* 영향: Fuse와 Nerve는 서로의 실패를 메우는 관계가 아니라, 각자 다른 failure surface를 보수적으로 제한하는 별도 안정성 축으로 읽는다.
* Trace:

  * ledgered: 2026-03-17
  * Nerve research framing rejected: later readpoint
  * COMMON-EVIDENCE-TRACE.

---
## Nerve

### Nerve — Lua 제어면 기반 선택적 안정성 Guard

* 상태: current readpoint / pre-ledger imported + 2026-03-20 refinements
* 결정: Nerve는 `Lua 병목 해결 모드`, `주력 성능 모듈`, `연구 장치`, `Failure Atlas 구축 프로젝트`가 아니라, **Lua를 제어면으로 사용해 이벤트 / 모드 상호작용 / 동기화 레이어의 스파이크와 작업 겹침을 완충하는 선택적 안정성 Guard**로 둔다.
* 현재 기준:

  * 목표는 Lua 자체를 깎는 것이 아니라, Lua 레벨에서 시스템적 지연·충돌·중첩 트리거를 줄이는 것이다.
  * 평균 FPS 향상보다 멀티/모드팩 환경의 선택적 완충, fail-soft, guard, same-tick retreat, 의미 불변을 우선한다.
  * 성공적인 S5가 나오더라도 필수 최적화 모듈로 승격하지 않으며, 조용한 환경에서는 dormant/selective 구조를 유지한다.
  * `Fuse가 못한 프리즈를 Nerve가 대신 해결한다`는 식으로 역할을 잇지 않는다.
  * Fuse는 엔진 측 분산 가능한 연쇄 폭주를 다루고, Nerve는 그런 프리즈를 유발할 수 있는 Lua 이벤트 폭주 / 중첩 / 중복의 트리거 조건을 줄이는 쪽으로 한정한다.
* 영향: Nerve 로드맵과 공개 전략은 성능 약속이 아니라 선택적 안정성, 보수적 개입, 의미 불변, 비개입 기준, 멀티/모드팩 환경의 guard 성격에 맞춘다.
* Rejected predecessor trace:

  * 2026-03-17 ~ 2026-03-20: `Failure Atlas 구축`, `연구 단계`, `연구 장치`, `자연 발현 실패 수집`, `성공 기법이 아니라 실패 귀속` 계열 표현은 현재 Nerve의 목적성과 맞지 않으므로 current readpoint에서 폐기한다.
  * `Nerve는 완전한 무의 공백지대가 아니라 직접 이식 가능한 답안이 없는 공백지대`라는 표현도 current 제품 정의가 아니라 폐기된 연구 프레이밍의 predecessor trace로만 남긴다.
* Trace:

  * origin: pre-ledger conversation, exact date unresolved
  * ledgered: 2026-03-17 documentation consolidation
  * refined: 2026-03-20 Area 5/6/9 sealing rounds
  * COMMON-EVIDENCE-TRACE.

### Nerve — 검증과 기준선 운용

* 상태: current readpoint
* 결정: Nerve의 검증은 실패 축적이나 연구 목적의 관측이 아니라, **봉인된 Area가 의미 불변 / fail-soft / 철수 조건 / 재현성을 만족하는지 확인하는 제품 검증**으로 둔다.
* 현재 기준:

  * 기본 기준선은 OFF다.
  * `OFF가 더 안전`하다는 표현은 체감이 더 낫다는 뜻이 아니라, OFF가 더 단순하고 책임이 명확한 baseline이어야 한다는 뜻이다.
  * Echo 로그는 실시간 정책 입력이 아니라 사후 확인 자료로만 쓴다.
  * Echo 관측값을 Fuse/Nerve의 실시간 정책 입력으로 직접 사용하는 구조는 채택하지 않는다.
  * Fuse/Nerve ON 비교는 새 연구 축을 여는 수단이 아니라, 봉인된 guard가 의도한 범위 안에서만 동작하는지 확인하는 검증 자료다.
  * 멀티 세션 데이터는 Area 9를 연구 프로젝트로 키우기 위한 재료가 아니라, 유지/폐기 판단과 비개입 확인을 위한 운영 증거로만 쓴다.
* 영향: Nerve의 산출물은 Failure Atlas가 아니라 `의미 불변 증명`, `발동 조건 증명`, `철수 조건 증명`, `비개입 증명`, `유지/폐기 판단`이다.
* Rejected predecessor trace:

  * 2026-03-17 ~ 2026-03-20: `Failure Atlas`, `연구 단계`, `자연 발현 실패 수집`, `실패 귀속 좌표계`는 current 목표에서 폐기한다.
* Trace: COMMON-EVIDENCE-TRACE.

### Nerve — 전장 개시 / 동결 / 고도화 규칙

* 상태: current readpoint
* 결정: Nerve는 Area 5 v0.1 Final 동결과 Area 6 v2.1 집행 기준을 중심으로 하며, 다음 전장은 자동으로 열지 않는다.
* 현재 기준:

  * 후속 전장은 반드시 `전장 판결 → 외부 조건 충족 확인 → 최소 스코프 정의 → v0.x 범위 결정` 순서로만 연다.
  * 현재 단계의 `고도화`는 새 기능 추가가 아니라, 기존 Area 5/6 개입 경로가 실제로 트리거되고 의미 불변으로 동작하며 재현 가능한지를 증명하는 **증명 강화**다.
  * Area 8(IO/Save)과 Area 10(GC/메모리)은 헌법을 지키며 안정화하기 어려운 전장으로 보아 현 시점 제품 전장에서 제외한다.
  * Area 9는 네트워크 제어기가 아니라 same-tick scoped stability guard로만 열린다.
  * 새 기능 제안보다 문법, 재현성, fail-soft, 소스 청결성, 검증 환경 확보를 우선한다.
* 영향: Nerve의 메인라인은 기능 확장보다 Area 5/6/9의 봉인된 스코프 유지, 런타임 증명, 유지/폐기 판단에 집중한다.
* Trace: COMMON-EVIDENCE-TRACE.

### Nerve Area 5 — UI / 인벤토리 안정화 v0.1 Final

* 상태: current readpoint / frozen
* 결정: Area 5는 **`데이터 즉시 반영 + 같은 틱 안의 시각 갱신 coalescing + 의미 불변 + fail-soft bypass`** 를 만족하는 합헌적 최소 구현(v0.1 Final)으로 동결한다.
* 현재 기준:

  * 채택: weak registry, snapshot 순회, executeFn optional fail-soft, bypass 고정.
  * 금지: `defer`, `drop`, `isVisible()`/visibility 기반 flush 판단, UI 상태 기반 정책 판단, Pulse로의 기능 상향 이동, 틱 넘김 캐시, 조기 `ItemTransferBatcher`, 공격적 batching.
  * v0.1은 현재 틱 안에서만 중복을 접는 최소 안정화로 유지한다.
* 영향: Area 5는 완료보다 **동결** 상태로 읽으며, 이후 확장은 별도 전장 판결과 v0.x 정의 없이는 열지 않는다.
* Trace:

  * ledgered: 2026-03-17
  * COMMON-EVIDENCE-TRACE.

### Nerve Area 6 — 이벤트 디스패치 / 모드 훅 폭주 안전 레이어

* 상태: current readpoint / v2.1 execution constitution
* 결정: Area 6은 이벤트를 더 똑똑하게 정리하는 최적화 기능이나 실패 축적용 연구 장치가 아니라, **문제 발생 시 리스너 단위로 격리하고 곧바로 철수하는 보수적 안전 레이어**로 둔다.
* 현재 기준:

  * 기본값은 `enabled = false`, `strict = false`이며, 설치만으로 `drop / delay / reorder / auto policy`가 발생해서는 안 된다.
  * 기본 기준선은 **설치 전/후 의미 동일**이다.
  * `EventDeduplicator` 계열은 폐기하고, 핵심 가드는 `EventRecursionGuard` 같은 재귀/폭주 방지용 최후 가드로 축소한다.
  * 기본은 report-only이며, `strict` opt-in에서만 last-resort drop을 예외적으로 허용한다.
  * `Events.Add` 래핑 충돌이 감지되면 공존 체인 고도화보다 즉시 Area 6을 OFF하는 back-off를 택한다.
  * 위험한 예외는 숨기지 않는다. incident / passthrough / rate-limited 로그를 남기며, fail-soft는 무음 은폐가 아니라 격리 사실의 명시적 노출을 뜻한다.
  * 실제 트리거는 same-tick self-recursion 또는 listener exception으로 한정한다.
  * 깊이, fan-out, 동일성 반복 같은 신호는 상시 제어 트리거가 아니라 incident 이후 근거를 보강하는 제한적 forensic surface로만 쓴다.
  * 행동은 `리스너 단위 격리 후 same-tick pass-through 철수` 하나로 봉인한다.
* 금지선:

  * `EventPriority`, `Governor`, `Throttler`, 의미 기반 allowlist/whitelist
  * `coalesce + flush`, 지연/재정렬
  * Echo/Fuse와 연결된 자동 제어
  * 넓은 global fallback
  * 래퍼 체인 고도화
  * Echo 힌트 기반 동적 조정
  * 자동 threshold 튜닝
  * Java strong reference/GC 방어
  * 같은 모듈 내부 공유까지 Pulse SPI로 강제하는 구조
* 현재 구현 해석:

  * Area 6 v2.1은 합헌이고 실행 가능하지만, 전수 래핑과 listener-unit 격리 비용을 의식적으로 감수한 고위험 설계다.
  * 승인은 안전 인증이 아니라 **책임을 인지한 실행 허가**다.
  * 현재 구현이 문제 리스너 오류를 Nerve 내부에 가두고 incident를 수집하는 임시 방파제 상태라면, 다음 단계는 `incident 리스너 특정 → 개별 수정 또는 정리 → enabled=false 복구 여부 판정`이다.
* 영향: Area 6 검토의 질문은 `무엇을 더 연구할 것인가`가 아니라 `봉인된 안전 레이어가 의미 불변 / fail-soft / 철수 조건을 지키는가`다.
* Rejected predecessor trace:

  * 2026-03-20: `Area 6은 실패 축적용 연구 장치` 해석은 current 목적성과 맞지 않아 폐기한다.
* Trace:

  * refined: 2026-03-20 Area 6 v2.1 sealing
  * COMMON-EVIDENCE-TRACE.

### Nerve Area 5·6 — 구현 전 재현성 게이트와 집행 기준

* 상태: current readpoint
* 결정: Area 5·6 구현 착수 전에는 기능 로드맵과 별도로 **레포 신뢰성 / 재현성 게이트(P0~P2)** 를 먼저 통과해야 한다.
* 현재 기준:

  * P0: conflict marker 제거, `NerveUtils.lua` 실코드 문법 확인
  * P1: `OnTickEven`이 의도인지 실수인지 문서/주석/코드 중 하나로 고정
  * P2: fail-soft / 예외 전파 정책을 코드 주석과 문장 수준에서 통일
  * Area 5·6 실행계획 v2.1은 구현·리뷰·핸드오버의 공통 기준서로 사용한다.
* 영향: Area 5·6 논의는 새 방향 발명이 아니라 v2.1 구현 충실도, 런타임 재현성, 소스 청결성 검증으로 이동한다.
* Trace:

  * adopted: 2026-03-20 Nerve Area 5·6 execution plan v2.1
  * COMMON-EVIDENCE-TRACE.

### Nerve Area 9 — 네트워크 제어기가 아니라 same-tick 철수형 보험 장치

* 상태: current readpoint
* 결정: Area 9는 멀티/네트워크를 제어하는 기능이 아니라, **네트워크 경계에서 Lua가 자폭하려는 순간 같은 틱 안에서만 물러나는 100% Lua 안정성 레이어**로 둔다.
* 현재 기준:

  * Area 9가 상대할 수 있는 붕괴는 호출 순서/타이밍 붕괴, 데이터 형태(shape) 붕괴, 중복/재진입 붕괴의 세 갈래다.
  * 핑, 패킷, 재전송, 큐잉, 우선순위, 병합, 재정렬, 서버 CPU, 엔진 동기화 수정을 다루지 않는다.
  * 기본 OFF를 유지한다.
  * `네트워크 경계 한정`, `대상 opt-in / 행동 opt-in 분리`, `동일 틱 한정 철수`, `다음 틱 자동 복귀`, `incident-gated pcall only`를 봉인선으로 둔다.
  * 구현 순서는 `켜도 아무 일도 안 하는 스캐폴딩 → observe → guarded path → quarantine`이다.
  * 재진입, 중복, shape, depth, guarded pcall, tick retreat, 최소 포렌식의 1~7 가드는 먼저 관측·표시·계수로만 연결한다.
  * 실제 행동은 단일 `reasonCode`와 same-tick retreat 하나로만 귀결한다.
  * `이상 징후 = 즉시 차단` 구조는 금지한다.
* 안전핀:

  * `tickId` 단일 진실의 소스
  * endpoints 폐쇄 목록
  * incident 조건 단일 플래그
  * quarantine key 범위 강제
* 금지선:

  * 핑 개선, 패킷 최적화, 서버 부하 분산, 엔진 동기화 수정
  * 전역 상시 `pcall`
  * 중요도/우선순위 판단
  * 자동 블랙리스트/화이트리스트
  * 영구 차단
  * 지연/병합/재정렬
  * Duplicate early-skip
  * Shape hard-fail 기본 차단
  * 비율/빈도/가중치 incident 계산
  * quarantine 지속시간 확장
  * 일반 이벤트/OnTick/UI/렌더 확장
* 영향: Area 9는 추가 고도화가 아니라 동결·실전 운용 판단 단계로 넘긴다. 이후 우선순위는 실제 멀티 세션 데이터 수집과 유지/폐기 판정이다.
* Predecessor trace:

  * 2026-03-20: `Area 9는 관측·분류 단계까지만 허용` 해석은 same-tick scoped stability guard 정의로 대체됨.
  * 2026-03-20: `Area 9는 지금 개발하면 안 되는 영역` 해석은 멀티 협업·재현 인프라 없이 네트워크 제어기로 키우지 않는다는 금지선으로 격하.
  * 2026-03-20: `Area 9는 연구 프로젝트가 아니라 기초공사형 방어 프로그래밍으로 시작`이라는 표현은 current에서 `same-tick scoped stability guard 구현 기준`으로 흡수하고, 연구 대비 표현은 current readpoint에서 제거한다.
* Non-decision: Area 9 동결은 release readiness, runtime rollout, public exposure, Workshop readiness 선언이 아니다.
* Trace: COMMON-EVIDENCE-TRACE.

### Nerve — 내부 전장 독립성과 자기 제한 정책

* 상태: current readpoint
* 결정: Nerve 내부 전장은 개념적으로 연속될 수 있어도 코드 차원의 직접 의존을 만들지 않으며, Nerve가 가질 수 있는 정책은 **자기 자신을 제한하는 정책**뿐이다.
* 현재 기준:

  * Area 5와 Area 6은 tick 경계 같은 최소 공통 개념만 공유할 수 있다.
  * 한 Area가 다른 Area의 존재를 가정하거나 직접 참조하는 구조는 채택하지 않는다.
  * 내부 공유는 Nerve 내부에서 처리하고, 타 모듈 공유만 Pulse SPI 경계를 따른다.
  * 허용되는 정책은 `개입 조건 / 철수 조건 / 이 상황에서는 아예 개입하지 않음` 같은 자기 제한 정책이다.
  * 게임 행동을 바꾸는 정책, 중요도 판단, FPS 기반 동작 변경, 스킵/주기 증가 같은 정책은 허용하지 않는다.
  * ON이 일부 구간에서 체감 개선을 보이더라도 문서와 검증의 기준선은 OFF에 둔다.
* 영향: Nerve는 자기 제약과 철수 조건만 가질 수 있으며, 게임 의미나 행동을 바꾸는 판단 엔진으로 확장하지 않는다.
* Trace: COMMON-EVIDENCE-TRACE.

### Nerve / Nerve+ — 배포 경계

* 상태: current readpoint
* 결정: Nerve는 Pulse 비의존 **핵심 기능 스탠드얼론**으로 유지하고, Nerve+만 Pulse 의존 **핵심 + 편의 계열**로 둔다.
* 영향: 문서/홍보/배포에서 Nerve는 core, Nerve+는 convenience overlay로 설명한다. Fuse의 Pulse 의존 전환도 이 배포 전략과 함께 정렬한다.
* Non-decision: 이 배포 경계는 즉시 release readiness, Workshop readiness, public exposure 선언이 아니다.
* Trace:

  * ledgered: 2026-03-23
  * COMMON-RELEASE-NONDECISION.


---

## Iris

### Iris — offline compiler / Lua viewer 원칙

* 상태: current readpoint / pre-ledger imported + 2026-03-25 system seal

* 결정: Iris는 확인된 정보를 오프라인에서 정적 산출물로 확정하고, PZ 런타임에서는 100% Lua 기반 viewer가 이를 표시·탐색하는 게임 내 위키형 정보 시스템으로 둔다.

* 현재 기준:

  * 증거, 분류, 상호작용 정보와 설명 산출물의 생성·검증은 오프라인에서 수행한다.
  * 런타임 Lua는 확정된 정적 산출물을 표시·탐색하며, 사실을 새로 생성·판단·수정하지 않는다.
  * Iris는 확인된 사실을 이해하기 쉽게 설명할 수 있지만, 해석·권장·효율 평가·우열 비교는 하지 않는다.
  * 충분한 근거가 없는 정보는 추측해서 채우지 않는다.
  * Iris runtime은 아이템, 행동 또는 게임 상태를 직접 변경하지 않는다.

* 영향:

  * 정보의 생성·검증과 user-facing 표시 책임을 분리하고, 런타임을 정적 정보 소비자인 Lua viewer로 유지한다.

* 오독 금지:

  * 이 항목은 런타임 추론·생성·재판정·수정이나 게임 상태 변경을 승인한 것이 아니다.
  * 이 항목은 public-text quality acceptance, runtime rollout, package publication, release / Workshop readiness 또는 public exposure를 선언한 것이 아니다.
  * COMMON-RELEASE-NONDECISION.
  * COMMON-RUNTIME-SURFACE-NONMUTATION.

* Trace:

  * ledgered: 2026-03-16 ~ 2026-03-25
  * COMMON-EVIDENCE-TRACE.


### Iris — Menu / Tooltip presentation contract

* 상태: current readpoint / Philosophy-bound user-facing surface contract

* 결정: Iris가 사용자에게 정보를 보여주는 user-facing surface는 Iris Menu와 Iris Tooltip 두 가지로 한정하며, 두 surface는 같은 확정 사실을 서로 다른 깊이로 표시한다.

* 현재 기준:

  * Iris의 user-facing information surface는 `Iris Menu`와 `Iris Tooltip` 두 가지다.
  * Iris Tooltip은 `Alt` 입력이 있을 때만 표시한다.
  * Iris Tooltip은 최대 `4줄`을 넘지 않는다.
  * Iris Menu는 Tooltip보다 상세한 정보를 제공한다.
  * Menu와 Tooltip은 서로 다른 facts authority를 갖지 않으며 같은 사실을 서로 다른 정보 깊이로 투영한다.
  * Menu와 Tooltip이 같은 대상에 대해 서로 모순되는 사실을 표시하지 않는다.
  * Tooltip은 Menu와 별개의 지식원이나 독립 semantic authority가 아니라 같은 확정 사실의 제한된 요약 projection이다.
  * Browser / Wiki / Detail 같은 내부 UI 구성요소는 Iris Menu 또는 Tooltip을 구성하는 implementation / presentation component이며 제3의 독립 user-facing knowledge surface가 아니다.
  * Menu / Tooltip의 표시 차이는 정보 깊이와 presentation 차이이며 Source / Evidence / classification / Layer 3 / Layer 4 authority 차이를 만들지 않는다.

* 영향:

  * Iris의 사용자 경험은 상세 Wiki surface와 제한된 quick-reference surface로 나뉘면서도 동일한 사실 authority를 유지한다.

* 오독 금지:

  * Tooltip을 Menu와 독립된 사실 authority나 별도 semantic pipeline으로 읽지 않는다.
  * Menu가 더 상세하다는 이유로 Tooltip과 다른 사실을 생성하거나 재판정하지 않는다.
  * Browser / Wiki / Detail component를 제3·제4의 독립 Iris information surface로 확대하지 않는다.
  * Tooltip의 최대 4줄 제한을 runtime에서 사실을 임의 삭제·요약·재판정할 권한으로 읽지 않는다.
  * COMMON-RUNTIME-SURFACE-NONMUTATION.
  * COMMON-RELEASE-NONDECISION.

* Trace:

  * Philosophy-bound Menu / Tooltip contract
  * ledgered/imported surface policy: 2026-03-16 ~ 2026-03-25
  * COMMON-EVIDENCE-TRACE.


### Iris — Evidence / Source / Outcome 모델

* 상태: current readpoint

* 결정: Iris가 Rule에서 소비하는 Evidence는 Source나 행동명이 아니라, 허용된 Source에서 정규화된 **관찰 가능한 outcome facts**로 고정한다.

* 현재 기준:

  * Source와 Evidence는 구분한다. Source는 사실의 출처이고, Evidence는 Source에서 정규화된 outcome fact다.
  * Recipe와 Right-click은 서로의 하위 체계가 아닌 독립적이고 동등한 Source로 유지한다.
  * Static capability는 Recipe / Right-click과 동급인 제3 interaction track이 아니라 비상호작용 정적 사실을 공급하는 보조 source family로 둔다.
  * Iris의 자동 분류는 Source별 별도 rule engine이 아니라 정규화된 Evidence를 소비하는 단일 outcome 중심 프레임을 사용한다.
  * Evidence의 기본형은 행동명이나 UI 경로가 아니라 아이템과 결부된 관찰 가능한 상태 변화다.
  * 메뉴명, 행동 문자열, 클릭 경로 또는 표시 문구에서 의미를 추론해 outcome을 자동 생성하지 않는다.
  * Equip effect / Use only / Passive function은 기본 Evidence 축으로 승격하지 않고 필요한 경우 후행 설명 정보로 다룬다.
  * 허용된 Evidence로 닫히지 않는 의미를 Iris가 자체적으로 추론하거나 보충하지 않는다.

* 영향:

  * Source별 표현 차이를 분류 로직까지 전파하지 않고 검증 가능한 outcome fact를 공통 Evidence 계약으로 사용한다.

* 오독 금지:

  * 이 항목은 행동명·메뉴 문자열 기반 Evidence 생성, Right-click의 Recipe 하위화, Static capability의 제3 동급 interaction track화 또는 Source별 Rule 이원화를 승인한 것이 아니다.
  * 이 항목은 Iris 내부의 의미 추론·재판정이나 런타임 Lua의 사실 생성·판단·수정을 승인한 것이 아니다.
  * 이 항목은 source / rendered / runtime / package mutation, release readiness 또는 public exposure를 선언한 것이 아니다.
  * COMMON-RUNTIME-SURFACE-NONMUTATION.
  * COMMON-RELEASE-NONDECISION.

* Trace:

  * sealed: 2026-03-24 ~ 2026-03-25
  * COMMON-EVIDENCE-TRACE.


### Iris — Context Outcome 추출 경계

* 상태: current readpoint / offline extraction contract sealed

* 결정: Context Outcome extractor는 의미 해석기나 분류기가 아니라, 이미 봉인된 outcome contract가 허용한 outcome을 source signal에서 오프라인으로 materialize하는 fact-table producer로 둔다.

* 현재 기준:

  * Context Outcome extraction은 runtime이 아니라 offline pipeline에서만 수행한다.
  * extractor는 새로운 outcome 의미를 발명하거나 source signal을 semantic interpretation으로 확장하지 않는다.
  * scanner / intermediate signal representation과 `Signal -> Outcome` mapping은 구분하며 intermediate signal 자체를 Evidence authority로 승격하지 않는다.
  * automatic extraction과 explicit manual injection은 서로 다른 provenance path로 유지한다.
  * manual injection은 automatic extractor가 닫지 못한 의미를 임의 추론하는 일반 fallback이 아니다.
  * Allowlist 밖 Outcome, nondeterministic result, output-contract violation 또는 authority outcome-contract identity mismatch는 fail-loud한다.
  * diagnostic warning이나 suspicious signal은 숨기지 않되 그 자체를 outcome authority나 automatic Evidence로 승격하지 않는다.
  * Context Outcome output은 downstream Evidence / Rule / description consumer가 소비하는 정적 artifact이며 extractor 자체가 classification authority를 소유하지 않는다.

* 영향:

  * source-specific runtime/UI signal을 outcome fact로 변환하는 과정과 semantic authority를 분리해 extractor 편의를 이유로 Evidence 계약이 암묵적으로 확장되는 것을 막는다.

* 오독 금지:

  * Context Outcome extractor를 행동명·메뉴명·문자열 기반 semantic inference engine으로 읽지 않는다.
  * diagnostic signal을 automatic PASS Evidence로 승격하지 않는다.
  * manual injection path를 unrestricted manual interpretation lane으로 사용하지 않는다.
  * 이 항목은 runtime outcome generation, runtime classification 또는 source / rendered / runtime / package mutation을 승인한 것이 아니다.
  * COMMON-RUNTIME-SURFACE-NONMUTATION.

* Predecessor trace:

  * 초기 extractor implementation의 exact scanner / IR / mapper / validator sequence와 item-specific injection routing은 implementation evidence로 보존한다.
  * item-specific diagnostic token과 exact manual-injection target은 영구 semantic taxonomy가 아니라 predecessor implementation trace다.
  * COMMON-EVIDENCE-TRACE.


### Iris Right-click — item-dependent state-change proof

* 상태: current readpoint / Gate-0 v2.4 / code-output reconciled

* 결정: Iris의 Right-click Evidence는 메뉴명이나 UI 존재 여부가 아니라, **아이템이 실행 도구로 결합되어 외부 대상에 관찰 가능한 상태 변화를 만드는가**를 기준으로 판정한다.

* 현재 기준:

  * Right-click Evidence의 핵심 proof는 `executing_tool + external_target + persistent_change`다.
  * `persistent_change`는 메뉴 표시나 클릭 경로가 아니라 target / world / container / character에 발생하는 관찰 가능한 outcome state change를 뜻한다.
  * 기본 Evidence 단위는 FullType 단위의 직접 실행 도구다.
  * `PASS / NO / REVIEW`를 primary decision으로 사용한다.
  * `STRONG / WEAK`는 PASS 이후 해당 Evidence의 uniqueness를 나타내는 보조 판정이다.
  * WEAK는 실패가 아니며 STRONG / WEAK 차이만으로 PASS Evidence의 downstream eligibility를 변경하지 않는다.
  * property-based / 조건 기반 field는 개별 아이템의 uniqueness를 판정하기 전에 field 자체가 Gate-0 실행 도구 구조를 만족하는지 먼저 판정한다.
  * Gate-0에 매칭되지 않는 대상은 Evidence `NO`가 아니라 Right-click Evidence scope 밖으로 둔다.
  * `REVIEW`는 수동 PASS 승격 통로가 아니라 허용된 정적 근거만으로 자동 판정이 닫히지 않은 미확정 상태다.
  * 웹·외부 위키를 이용한 수동 PASS 승격은 사용하지 않는다.

* 영향:

  * Right-click Evidence는 UI 명칭이나 행동 표현이 아니라 아이템 의존적 상태 변화 proof를 기준으로 생성하며 uniqueness와 Evidence 성립 여부를 분리한다.

* Predecessor trace:

  * 2026-03-25 Gate-0 v2 predecessor의 `아이템이 없으면 우클릭 메뉴 항목 자체가 생성되는가` 기준은 current canonical proof가 아니다.
  * `STRONG만 canonical 후보로 인정하고 WEAK를 제외`하던 기준은 current PASS-then-uniqueness 모델로 supersede됐다.
  * `can_*` capability-first, 바닐라 5개 축소, 메뉴명·행동명 중심 Evidence 모델은 current 기준이 아니다.

* 오독 금지:

  * 이 항목은 STRONG-only 판정, WEAK 실패 처리, capability-first 복귀, 웹·위키 기반 수동 PASS 승격, scope 밖 대상을 Evidence `NO`로 처리하거나 메뉴 문자열에서 outcome을 생성하는 것을 승인한 것이 아니다.
  * 이 항목은 runtime Lua의 Evidence 재판정·proof 생성이나 source / rendered / runtime / package mutation을 승인한 것이 아니다.
  * 이 항목은 release readiness, public exposure 또는 Publish acceptance를 선언한 것이 아니다.
  * COMMON-RUNTIME-SURFACE-NONMUTATION.
  * COMMON-RELEASE-NONDECISION.

* Trace:

  * current contract: Gate-0 v2.4 / PASS-then-uniqueness overlay
  * COMMON-EVIDENCE-TRACE.


### Iris — 자동 분류 / Evidence Allowlist 경계

* 상태: current readpoint

* 결정: Iris 자동 분류는 Evidence Allowlist가 허용한 normalized evidence만 소비하며, 허용되지 않은 의미를 추론해 분류 근거를 확장하지 않는다.

* 현재 기준:

  * Allowlist 밖의 필드, 문자열, 연산 또는 의미 해석은 자동 분류 근거로 사용하지 않는다.
  * vanilla-first current baseline에서 자동 분류가 직접 소비할 수 있는 근거는 바닐라 scripts / client 선언 데이터와 그로부터 허용된 방식으로 정규화된 Evidence까지다.
  * 외부 모드 데이터는 별도 adapter / compiler를 통해 Iris 내부 표준 산출물로 정규화된 뒤에만 소비하며 raw mod file이나 임의 문자열을 직접 분류 근거로 사용하지 않는다.
  * Java 디컴파일 등으로 획득한 엔진 내부 의미를 자동 분류 Evidence로 승격하지 않는다.
  * 이름, 설명, 표시 카테고리, 임의 문자열 contains, 수치 비교 또는 임의 태그 확장을 통해 의미를 추론하지 않는다.
  * 허용된 Evidence만으로 분류가 닫히지 않으면 임의의 분류 태그를 생성하지 않고 미분류 상태를 유지하거나 명시적인 manual override로 처리한다.
  * `MoveablesTag`와 Item Script의 일반 `Tags`처럼 의미 계약이 다른 namespace는 서로 혼용하지 않는다.
  * 미분류 항목이 많다는 사실 자체를 Evidence Table / Allowlist / DSL 확장의 근거로 삼지 않는다.

* 영향:

  * 자동 분류의 coverage보다 근거 경계를 우선하며, 분류 결과가 부족하더라도 Evidence 계약 밖의 의미 추론으로 이를 메우지 않는다.

* 오독 금지:

  * 이 항목은 이름·설명·표시 카테고리·Java 내부 의미·임의 문자열을 이용한 추론, raw mod file 직접 분류 또는 미분류를 줄이기 위한 Evidence 임의 확장을 승인한 것이 아니다.
  * 이 항목은 runtime Lua의 분류 추론·재판정이나 source / rendered / runtime / package mutation을 승인한 것이 아니다.
  * 이 항목은 release readiness, Publish acceptance 또는 public exposure를 선언한 것이 아니다.
  * COMMON-RUNTIME-SURFACE-NONMUTATION.
  * COMMON-RELEASE-NONDECISION.

* Trace:

  * sealed: 2026-03-23 ~ 2026-03-25
  * COMMON-EVIDENCE-TRACE.


### Iris — Taxonomy baseline / category boundary

* 상태: current readpoint

* 결정: Iris의 current item taxonomy는 9개 대분류와 봉인된 소분류 경계를 기준선으로 사용하며, coverage 문제를 이유로 별도 decision 없이 분류 구조를 재분할하거나 의미 범위를 확장하지 않는다.

* 현재 기준:

  * 대분류는 `Tool / Combat / Consumable / Resource / Literature / Wearable / Furniture / Vehicle / Misc` 9개 축을 기준선으로 둔다.
  * Furniture는 `Furniture.7-A` 단일 소분류로 유지한다.
  * Vehicle은 `Vehicle.8-A / Vehicle.8-B` 2분할로 유지하며 별도 decision 없이 추가 세분화하지 않는다.
  * `Misc.9-A`는 일반 분류 rule이 아니라 output-stage fallback이다.
  * `Tool.1-K (Security)`와 `Tool.1-L (Storage)`는 정식 소분류로 유지한다.
  * `Tool.1-L (Storage)`는 비착용 휴대 컨테이너를, `Wearable.6-F`는 착용 가능한 배낭을 담당한다.
  * `Consumable.3-B`의 음료 판정은 체감적 용도나 수치 비교가 아니라 `Drink / Drainable` 선언 구조를 기준으로 한다.

* 영향:

  * 현재 taxonomy의 의미 경계를 안정적으로 유지하며 분류 coverage나 편의성을 이유로 기존 category의 책임 범위를 임의로 넓히지 않는다.

* 오독 금지:

  * 이 항목은 Furniture 재세분화, Vehicle 과분할, `Misc`의 일반 catch-all rule화 또는 Storage / Wearable 경계의 임의 확장을 승인한 것이 아니다.
  * 미분류 발생 자체는 taxonomy 재설계나 Evidence 확대를 자동 승인하는 근거가 아니다.
  * 이 항목은 runtime 분류 재판정, source / rendered / runtime / package mutation, release readiness 또는 public exposure를 승인한 것이 아니다.
  * COMMON-RUNTIME-SURFACE-NONMUTATION.
  * COMMON-RELEASE-NONDECISION.

* Trace:

  * sealed: 2026-03-23 ~ 2026-03-25
  * COMMON-EVIDENCE-TRACE.


### Iris — item information presentation hierarchy / Layer 3–4 경계

* 상태: current readpoint

* 결정: Iris Menu의 item information은 기본 사실, Layer 3 설명, Layer 4 활용 정보와 meta information을 하나의 presentation hierarchy에서 보여주되 presentation order를 각 information layer의 authority ownership과 혼동하지 않는다.

* 현재 기준:

  * Menu의 기본 presentation order는 `기본 정보 -> 의미 / 설명 -> 개별 설명(조건부) -> 활용 -> 메타` 흐름을 따른다.
  * 이 순서는 user-facing presentation hierarchy이며 upstream / downstream authority chain 자체가 아니다.
  * Layer 3 item body는 DVF System이 approved facts / decisions를 소비해 생성한 정적 설명 정보다.
  * Recipe / Right-click `use_case`와 requirement는 QG가 소유하는 Layer 4 interaction information이다.
  * Layer 4 활용 block은 Menu에서 Layer 3 설명 뒤에 배치될 수 있지만 Layer 3 body의 일부로 흡수되거나 DVF System authority로 전환되지 않는다.
  * 각 information layer는 앞선 UI block의 필터 결과가 아니라 자기 responsibility를 가진 독립 정보층이다.
  * 대분류 / 소분류 / 아이템 목록은 browsing anchor로 유지한다.
  * `primary_subcategory`는 browsing / navigation anchor이며 Layer 3 문장의 자동 semantic authority가 아니다.
  * 소분류 설명은 모든 소속 아이템에 자동 적용되는 문장이 아니라 해당 사실과 조건이 성립할 때만 사용하는 설명 기반이다.
  * 개별 설명은 upstream facts / Evidence / Source가 이미 확정된 뒤 실제 기능을 이해하는 데 필요한 경우에만 둔다.
  * 소분류와 개별 설명은 분류명을 반복하는 대신 확인된 용도·시스템적 의미·적용 범위를 이해하기 쉬운 정적 문장으로 표현한다.
  * 분류 ID, predicate, provenance와 debug metadata는 필요 시 meta 영역에서 제공하며 기본 설명 문장과 구분한다.
  * 추천, 효율 평가와 우열 비교는 하지 않는다.

* 영향:

  * 사용자에게는 하나의 자연스러운 item page로 보이면서도 DVF System Layer 3와 QG Layer 4의 authority ownership을 유지한다.

* 오독 금지:

  * UI에서 Layer 4가 Layer 3 뒤에 나온다는 이유로 QG output을 DVF body의 하위 산출물로 읽지 않는다.
  * presentation hierarchy를 semantic authority hierarchy로 읽지 않는다.
  * `primary_subcategory`나 UI placement를 새로운 facts authority로 승격하지 않는다.
  * 이 항목은 runtime semantic composition, source 재판정 또는 Publish Boundary PASS를 승인한 것이 아니다.
  * COMMON-RUNTIME-SURFACE-NONMUTATION.
  * COMMON-RELEASE-NONDECISION.

* Trace:

  * initial description hierarchy: 2026-03-16 ~ 2026-03-25
  * Layer 3 / Layer 4 responsibility split: successor architecture readpoint
  * COMMON-EVIDENCE-TRACE.


### Iris Browser — DisplayName presentation folding / identity 보존

* 상태: current readpoint

* 결정: 같은 DisplayName을 가진 아이템의 목록 중복은 build-time 기능 동등성 병합이 아니라 Browser presentation 단계의 접기로 처리하며 underlying FullType과 artifact identity는 그대로 보존한다.

* 현재 기준:

  * 목록 접기는 DisplayName을 기준으로 하는 presentation-only folding이다.
  * 접기는 FullType identity, Source / Evidence, rendered artifact authority 또는 runtime payload identity를 병합하지 않는다.
  * 같은 표시명 아래 접힌 variant가 실제로 같은 기능이나 의미를 가진다고 추론하지 않는다.
  * 접힌 목록에서는 개념명을 중심으로 표시하며 `(xN)` 형식의 수량 배지를 기본 표면에 붙이지 않는다.
  * variant 수, FullType 차이와 개별 기능 차이는 상세 표면에서 확인할 수 있게 한다.

* 영향:

  * Browser 목록의 시각적 중복은 줄이되 presentation 편의를 semantic identity 또는 artifact authority 병합으로 확대하지 않는다.

* 오독 금지:

  * 이 항목은 build-time 기능 동등성 그룹 생성, FullType 병합, Source / Evidence 병합 또는 하나의 대표 variant를 canonical item으로 승격하는 것을 승인한 것이 아니다.
  * DisplayName 동일성은 semantic equivalence나 동일 기능의 근거가 아니다.
  * 이 항목은 source / rendered / runtime / package authority mutation, release readiness 또는 public exposure를 선언한 것이 아니다.
  * COMMON-RUNTIME-SURFACE-NONMUTATION.
  * COMMON-RELEASE-NONDECISION.

* Trace:

  * sealed: 2026-03-16 ~ 2026-03-25
  * COMMON-EVIDENCE-TRACE.


### Iris QG — Recipe / Right-click use_case 모델

* 상태: current readpoint

* 결정: Iris의 Layer 4 상호작용 정보는 Recipe와 Right-click을 서로 독립적이고 동등한 Source로 유지하고 각 Source에서 확정된 Evidence를 구조화된 `use_case` 단위로 표현한다.

* 현재 기준:

  * Recipe와 Right-click은 잔여 필터 관계가 아닌 동등한 두 Source다.
  * 같은 아이템은 Recipe와 Right-click 양쪽의 use_case를 동시에 가질 수 있다.
  * Recipe Evidence는 `rule_id` 중심의 `recipe_evidence` 계약을 current 표준 경로로 사용한다.
  * UI에 행동 정보로 노출되는 use_case는 해당 Source에서 PASS로 확정된 Evidence를 기반으로 한다.
  * Right-click 정보는 구조적으로 evidence와 exclusion을 구분하며 exclusion을 사용자 행동 정보로 승격하지 않는다.
  * Source 종류나 표시 문자열을 역파싱해 use_case 의미를 복원하지 않는다.

* 영향:

  * Recipe와 Right-click의 독립성을 유지하면서도 user-facing Layer 4 정보는 공통 use_case 구조로 소비할 수 있게 한다.

* Predecessor trace:

  * `classification_recipe` 중심 경로는 `rule_id` 중심 `recipe_evidence` 경로에 의해 supersede됐다.
  * Recipe-only 또는 RightClick-only 잔여 필터 모델은 current 기준이 아니다.
  * `[우클릭]` 같은 표시 문자열을 기존 목록에 삽입한 뒤 역파싱하는 모델은 current 구조화 계약으로 대체됐다.

* 오독 금지:

  * 이 항목은 Recipe와 Right-click의 상하 관계, capability-first 복귀, exclusion의 행동 Evidence 승격 또는 표시 문자열 기반 의미 추론을 승인한 것이 아니다.
  * 이 항목은 runtime Lua의 use_case 재판정이나 Evidence 생성을 승인한 것이 아니다.
  * 이 항목은 source / rendered / runtime / package mutation, Publish acceptance, release readiness 또는 public exposure를 선언한 것이 아니다.
  * COMMON-RUNTIME-SURFACE-NONMUTATION.
  * COMMON-RELEASE-NONDECISION.

* Trace:

  * sealed: 2026-03-25
  * COMMON-EVIDENCE-TRACE.


### Iris QG — Recipe requirement / role 경계

* 상태: current readpoint

* 결정: Recipe의 `consumed / keep / require` 정보는 recipe 내부의 참여 역할과 requirement를 표현하는 Layer 4 정보로 사용하며 이를 아이템 자체의 행동 Evidence로 승격하지 않는다.

* 현재 기준:

  * Recipe PASS Evidence에는 아이템의 input / output 참여 사실을 사용한다.
  * `keep / require`는 행동 Evidence가 아니라 해당 recipe에서의 requirement / role 정보다.
  * `consumed`와 `keep`은 서로 다른 recipe role로 명시적으로 구분한다.
  * Recipe requirement는 해당 recipe 단위에만 귀속하며 FullType 전체의 공통 capability나 상태로 승격하지 않는다.
  * 동적으로 안전하게 확정할 수 없는 recipe expression은 자동 의미 추론으로 닫지 않고 review 상태로 보존한다.

* 영향:

  * Recipe 참여 사실, 소비 여부와 요구 조건을 분리해 표시하면서 recipe-local 정보를 아이템의 전역 행동 의미로 확대하지 않는다.

* 오독 금지:

  * 이 항목은 `keep / require`의 행동 Evidence 승격, Requirements와 Actions의 혼합 또는 recipe-local requirement의 FullType 전역 capability화를 승인한 것이 아니다.
  * unresolved dynamic recipe 표현을 임의 추론이나 런타임 판정으로 해소하지 않는다.
  * 이 항목은 recipe 전체의 SAT / UNSAT를 이용한 추천·정렬·숨김 정책을 승인한 것이 아니다.
  * COMMON-RUNTIME-SURFACE-NONMUTATION.

* Trace:

  * sealed: 2026-03-25
  * `dynamic_recipe_expr`: review-only current disposition
  * COMMON-EVIDENCE-TRACE.


### Iris QG — 구조화 interaction rendering / Lua presentation 경계

* 상태: current readpoint

* 결정: Layer 4 use_case와 requirement의 의미 구조와 표시문은 오프라인에서 확정하고 runtime Lua는 그 결과를 재판정하거나 의미 보정하지 않고 Iris Menu / Tooltip의 허용된 presentation block에 표시한다.

* 현재 기준:

  * 오프라인 QG pipeline은 use_case 구조, requirement 상태와 표시문을 확정한다.
  * 필수 label mapping 누락처럼 정상 표시를 결정할 수 없는 build-contract 위반은 fail-loud 처리한다.
  * Recipe requirement 상태표시는 requirement atom 단위의 presentation 정보로 한정한다.
  * requirement 상태표시 결과를 다른 tab, 정렬, classification 또는 다른 information layer의 policy input으로 전파하지 않는다.
  * runtime Lua는 오프라인에서 확정된 구조와 표시문을 읽어 UI state로 투영하며 role이나 의미를 재해석하지 않는다.
  * Layer 4 UI는 Philosophy가 허용한 Iris Menu / Tooltip 두 user-facing surface 내부의 Iris-owned block으로 제공한다.
  * 기존 게임 UI 전역 동작을 덮어쓰거나 Menu / Tooltip 밖의 독립 knowledge surface를 생성하지 않는다.

* 영향:

  * Layer 4의 semantic decision과 runtime presentation을 분리하면서 Iris의 user-facing surface contract도 유지한다.

* 오독 금지:

  * Lua에서의 role 기반 문구 보정, runtime use_case 재판정 또는 runtime 문장 생성을 승인한 것이 아니다.
  * QG block을 Menu / Tooltip과 독립된 제3 user-facing knowledge surface로 읽지 않는다.
  * UI 통합은 기존 게임 UI 전역 동작을 변경할 권한을 부여하지 않는다.
  * COMMON-RUNTIME-SURFACE-NONMUTATION.
  * COMMON-RELEASE-NONDECISION.

* Trace:

  * sealed: 2026-03-25
  * Menu / Tooltip surface contract aligned: current readpoint
  * COMMON-EVIDENCE-TRACE.


### Iris — DVF System / IAR / Runtime Compatibility / Publish Boundary claim separation

* 상태: current readpoint / responsibility boundary sealed / canonical terminology aligned / required-validation gate adopted / governance-only

* 결정: Iris의 Layer 3 body production, artifact authority / lifecycle, runtime consumer compatibility와 publish / release acceptance는 서로 다른 responsibility와 claim axis로 유지하며, 과거 Legacy Combined DVF Governance Route에서 함께 수행되던 사실을 각 책임의 소유권으로 확대하지 않는다.

* 현재 기준:

  * `DVF System`은 `facts / decisions / profile / body_plan -> rendered Layer 3 body` production 경로로 책임을 한정한다.
  * `DVF Body Compiler`는 DVF System의 body-production responsibility를 claim / validation 수준에서 좁게 지칭하는 current canonical role name이다.
  * Iris Artifact Registry는 Layer 3 전용 Registry가 아니라 Iris의 **5개 information layer 전반에서 artifact responsibility / authority / identity / lifecycle을 가로지르는 별도 Iris-side boundary**다.
  * 각 information layer의 semantic production responsibility는 해당 producer가 유지하며 IAR의 cross-layer artifact governance를 semantic production ownership으로 확대하지 않는다.
  * IAR는 source / rendered / runtime / package artifact identity, lifecycle, required validation, seal / cutover와 stale / predecessor reentry governance를 담당한다.
  * Registry Runtime Compatibility는 runtime consumer가 current registry / payload identity를 손실·충돌 없이 안전하게 소비할 수 있는지를 별도 claim axis로 판정한다.
  * Publish Boundary는 public-text acceptance, semantic-quality acceptance, package publication, release / Workshop readiness와 manual QA를 별도 claim axis로 관리한다.
  * `DVF Body Compiler PASS`, `Registry Authority PASS`, `Registry Runtime Compatibility PASS`, `Publish Boundary PASS`는 서로 대체하지 않는다.
  * `Publish Boundary PASS`는 해당 readpoint가 요구하는 publish / acceptance component를 모두 충족한 conjunctive claim으로만 사용하며, public-text assessment, semantic-quality assessment, package projection / publication, manual QA 또는 release-readiness 같은 일부 component의 PASS를 bare `Publish Boundary PASS`로 축약하지 않는다.
  * bare `DVF PASS`와 bare `DVF System PASS`는 current claim으로 사용하지 않는다.
  * `DVF System Body Compiler PASS`는 `DVF Body Compiler PASS`와 같은 body-production axis의 expanded alias이며 별도의 system-wide completion claim이 아니다.
  * Legacy Combined DVF Governance Route는 body production과 Registry governance 책임이 함께 실려 있던 historical governance surface이며 current canonical architecture가 아니다.
  * `Legacy Combined DVF Governance Route PASS`는 route-container claim일 뿐 `DVF Body Compiler PASS`, Registry Authority, Registry Runtime Compatibility 또는 Publish Boundary의 정의 권한이 아니다.
  * live `Iris/_docs/round3/current_route_required_validations.json`은 legacy combined governance route container로 유지될 수 있지만 manifest에 포함된 validation 사실을 DVF System의 책임 귀속으로 읽지 않는다.
  * responsibility / claim boundary gate는 live required-validation 경로에 adoption되어 후속 current claim에서 서로 다른 responsibility를 다시 혼합하는 overclaim을 fail-closed한다.
  * lexical / token-level claim guard는 governance overclaim을 차단하는 장치이며 semantic review, public-text quality judgment 또는 Publish acceptance를 수행하지 않는다.

* 영향:

  * DVF System은 Layer 3 body compiler / verifier 역할에 집중하고 IAR / Runtime Compatibility / Publish Boundary의 책임을 흡수하지 않는다.
  * IAR는 Iris 전 information layer의 artifact lifecycle을 가로지르지만 각 producer의 semantic responsibility를 흡수하지 않는다.
  * current-route governance container의 PASS나 required-validation adoption만으로 body compiler, artifact authority, runtime compatibility와 publish acceptance가 함께 완료됐다고 주장할 수 없다.

* 최소 결과 trace:

  * responsibility / claim boundary split: `PASS`
  * canonical body-production terminology: `DVF System / DVF Body Compiler`
  * standalone bare DVF / DVF System PASS: `forbidden`
  * live required-validation gate adoption: `complete`
  * forbidden current responsibility overclaim: `0`
  * protected source / rendered / Lua / runtime / package mutation: `0`

* 후속 input artifact:

  * live required-validation manifest: `Iris/_docs/round3/current_route_required_validations.json`
  * naming / responsibility policy: `docs/dvf_3_3_dvf_system_naming_realignment_policy.md`
  * naming / responsibility claim boundary: `docs/dvf_3_3_dvf_system_naming_realignment_claim_boundary.md`

* 오독 금지:

  * `DVF Body Compiler PASS`는 Registry Authority, Registry Runtime Compatibility, package safety, public-text acceptance 또는 release readiness를 뜻하지 않는다.
  * `Registry Authority PASS`는 DVF body-production 성공, public-text acceptance 또는 release readiness를 뜻하지 않는다.
  * `Registry Runtime Compatibility PASS`는 source authority mutation, DVF body-production completion 또는 semantic / public-text acceptance를 뜻하지 않는다.
  * `Publish Boundary PASS`는 DVF Body Compiler PASS나 Registry Authority PASS의 대체 claim이 아니다.
  * public-text assessment PASS, semantic-quality PASS, current-runtime package identity PASS 또는 manual QA의 단독 결과를 `Publish Boundary PASS`로 승격하지 않는다.
  * IAR의 5-layer artifact responsibility를 QG / DVF / classification / other producer의 semantic responsibility 흡수로 읽지 않는다.
  * Legacy Combined DVF Governance Route의 PASS를 현재 각 responsibility axis의 PASS로 분해·승격하지 않는다.
  * Iris Artifact Registry는 DVF System의 하위 구성요소가 아니다.
  * required-validation manifest가 legacy combined governance route container라는 사실은 Registry / Publish responsibility를 DVF System에 부여하지 않는다.
  * lexical claim guard PASS는 semantic review, public-facing text quality acceptance, Publish Boundary PASS 또는 release acceptance가 아니다.
  * COMMON-RELEASE-NONDECISION.
  * COMMON-RUNTIME-SURFACE-NONMUTATION.

* Predecessor trace:

  * 초기 boundary-separation lifecycle은 당시 `DVF Core`로 불리던 body compiler responsibility와 Iris-side Registry / Runtime Compatibility / Publish responsibility가 Legacy Combined Current Route에 혼재돼 있음을 분리했다.
  * boundary separation preflight -> claim-contract closure -> required-gate adoption은 같은 lifecycle로 소비됐으며 선행 `required_gate_adopted=false` 상태는 후속 adoption으로 supersede됐다.
  * 이 lifecycle에서 정립된 responsibility split의 의미는 유지되지만 `DVF Core`는 current canonical terminology가 아니다.
  * 후속 naming realignment가 `DVF Core`를 retired predecessor label로 격하하고 current canonical terminology를 `DVF System / DVF Body Compiler`로 봉인했다.
  * predecessor `DVF Core PASS`는 historical claim meaning 보존 용도로만 읽으며 새 current claim에 사용하지 않는다.
  * routing-preflight inventory, scan universe, intermediate adoption flags와 exact staging evidence는 `COMMON-EVIDENCE-TRACE`에 흡수한다.
  * COMMON-EVIDENCE-TRACE.

* Trace:

  * Core / Registry / Publish boundary claim gate: predecessor responsibility-split lifecycle
  * required-gate adoption: successor adoption within the same lifecycle
  * DVF System naming realignment: current canonical successor readpoint
  * COMMON-EVIDENCE-TRACE.


### Iris DVF System — Layer 3 body production contract

* 상태: current readpoint / successor production contract sealed

* 결정: DVF System은 approved facts / decisions / profile / body_plan을 소비해 Iris Layer 3의 개별 아이템 본문을 오프라인에서 결정론적으로 생성·검증하는 body-production system으로 둔다.

* 현재 기준:

  * DVF System의 책임은 `facts / decisions / profile / body_plan -> rendered Layer 3 body`로 한정한다.
  * 본문의 의미 결정과 렌더링은 오프라인에서 수행하며 runtime Lua가 본문을 생성·판단·보정하지 않는다.
  * rendered body는 upstream facts와 decisions를 소비한 결과이며 DVF System이 새로운 facts authority를 생성하거나 upstream facts를 재판정하지 않는다.
  * legacy manual registry / T-Gate / active-silent 모델은 current production contract가 아니라 predecessor / historical vocabulary로만 남긴다.
  * prior production model을 current로 복원하려면 별도 additive correction 또는 rollback decision이 필요하다.

* 영향:

  * DVF System은 Layer 3 body compiler / verifier 역할에 집중하며 artifact authority, runtime compatibility, package identity, publish 또는 release 책임을 소유하지 않는다.

* Predecessor trace:

  * legacy manual registry / T-Gate / active-silent production model은 successor offline body-production contract에 의해 supersede됐다.
  * predecessor vocabulary와 artifacts는 historical / diagnostic / compatibility trace로만 보존한다.

* 오독 금지:

  * 이 항목은 runtime Lua 본문 생성·재판정·repair, upstream facts 재판정 또는 DVF System authority 범위 확장을 승인한 것이 아니다.
  * DVF System production PASS는 Registry Authority, Registry Runtime Compatibility, Publish Boundary, package publication, release / Workshop readiness 또는 public-text acceptance를 뜻하지 않는다.
  * COMMON-RUNTIME-SURFACE-NONMUTATION.
  * COMMON-RELEASE-NONDECISION.

* Trace:

  * successor production contract sealed: predecessor cutover chain 이후 current readpoint
  * COMMON-EVIDENCE-TRACE.


### Iris Artifact Registry — Layer 3 artifact authority chain

* 상태: current readpoint / successor authority adopted

* 결정: Iris Layer 3의 source, rendered artifact와 runtime consumer payload는 successor authority chain으로 관리하며 각 artifact의 authority, identity와 lifecycle role은 Iris Artifact Registry가 소유한다.

* 현재 기준:

  * 이 항목은 IAR의 5개 information layer 전반 artifact governance 중 Layer 3 authority chain을 구체화한 contract다.
  * current source authority는 successor facts / decisions / overlay support / input manifest 계열로 구성한다.
  * rendered authority는 current source authority를 소비한 오프라인 production 결과다.
  * runtime consumer payload authority는 current rendered artifact에서 생성된 declared Lua chunk bundle이다.
  * source, rendered, runtime과 package projection은 서로 다른 artifact role로 구분하며 각 identity와 lifecycle을 독립적으로 관리한다.
  * historical / staging / diagnostic / fixture / provenance artifact는 별도 adoption 없이 current source / rendered / runtime / package authority로 승격하지 않는다.
  * runtime-derived seed, dry-run, sandbox output과 staging projection은 bootstrap 또는 evidence가 될 수 있지만 그 자체로 current authority가 되지 않는다.
  * predecessor current readpoint를 복원하려면 명시적인 additive rollback 또는 correction decision이 필요하다.
  * DVF System의 Layer 3 body-production 책임과 IAR의 artifact authority / identity 책임은 서로 대체하거나 흡수하지 않는다.
  * current facts / decisions / overlay support는 동일한 successor row universe와 identity contract를 소비해야 하며, 서로 다른 baseline이나 partial row universe를 current source authority로 함께 사용하지 않는다.
  * runtime-adopted Layer 3 compose 대상은 해당 row의 `body_source_overlay`를 포함한 current source-overlay contract를 만족해야 하며, source / overlay / compose / rendered / runtime validation은 같은 baseline identity에 결속한다.

* 최소 결과 trace:

  * successor authority chain adoption: `PASS`
  * sealed successor universe: `2105` entries
  * current runtime payload readpoint: chunk manifest + `11` chunks

* 후속 input artifact:

  * current regeneration manifest: `Iris/build/description/v2/data/dvf_3_3_input_manifest.json`
  * runtime payload manifest: `Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks.lua`
  * runtime chunk set: `Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks/*.lua`
  * live required-validation manifest: `Iris/_docs/round3/current_route_required_validations.json`

* 보존 predecessor input:

  * consumer audit provenance: `Iris/build/description/v2/staging/2105_baseline_consumption_audit/classified_ledger.jsonl`

* 오독 금지:

  * 이 Layer 3 chain을 IAR 전체 범위가 Layer 3에 한정된다는 뜻으로 읽지 않는다.
  * artifact authority adoption은 DVF System의 책임 확대나 DVF System의 Registry authority 소유를 뜻하지 않는다.
  * reconstruction output, runtime-derived seed, staging candidate, dry-run, sandbox 또는 diagnostic evidence를 current authority로 복원하지 않는다.
  * prerequisite / staging / required-gate PASS는 current cutover, live migration execution 또는 runtime payload replacement 자체를 뜻하지 않는다.
  * current runtime payload identity는 package publication, Publish Boundary PASS, public-text acceptance, manual QA completion 또는 release readiness를 뜻하지 않는다.
  * COMMON-RUNTIME-SURFACE-NONMUTATION.
  * COMMON-RELEASE-NONDECISION.
  * `body_source_overlay`를 단순 optional provenance metadata로 격하하거나, facts / decisions / overlay support의 서로 다른 row universe를 하나의 current authority로 혼합하지 않는다.

* Predecessor trace:

  * 2026-06-12 Layer 3 current-authority reconstruction은 partial readpoint로 닫혔다.
  * 2026-06-12 `2105` baseline consumption audit은 후속 consumer denominator / migration governance가 소비할 read-only provenance를 봉인했다.
  * 2026-06-13 vNext authority definition과 staging execution은 successor authority candidate lifecycle로 시작됐다.
  * 2026-06-15 regeneration parity는 successor candidate와 predecessor runtime 차이를 검증하는 prerequisite evidence로 닫혔다.
  * 2026-06-16 delta disposition과 current-route integration은 successor cutover input을 검증했다.
  * 2026-06-17 rejected-delta correction / re-parity는 successor cutover input usability를 회복했다.
  * 2026-06-18 consumer migration input normalization과 cutover tooling readiness는 후속 cutover prerequisite를 닫았다.
  * 이후 required-validation adoption reseal은 live required gate adoption을 완료했다.
  * 당시 `branch_a_required_gate_adopted`는 round-local predecessor metadata이며 current authority vocabulary가 아니다.
  * COMMON-EVIDENCE-TRACE.

* Trace:

  * predecessor lifecycle: 2026-06-12 ~ 2026-06-18
  * successor authority cutover: sealed
  * COMMON-EVIDENCE-TRACE.


### Iris Artifact Registry — runtime payload state boundary

* 상태: current readpoint / runtime payload residual seal complete

* 결정: IAR가 관리하는 current-like runtime surface는 동일한 payload state contract를 만족해야 하며 historical / staging / predecessor residue를 current runtime state로 재해석하지 않는다.

* 현재 기준:

  * live runtime, package projection과 current-compatible candidate는 같은 runtime payload state contract로 검증한다.
  * current payload에서 `publish_state`는 runtime row state로 노출하지 않는다.
  * `unadopted` row는 renderer-visible description text를 가지지 않는다.
  * forbidden 또는 분류되지 않은 current-like state를 runtime payload에 허용하지 않는다.
  * historical rollback snapshot이나 predecessor artifact에 남은 current-incompatible residue는 historical evidence로만 보존하며 current debt나 runtime mutation 근거로 사용하지 않는다.
  * payload-shape validation과 residual-seal completion은 구분해서 판정한다.
  * residual seal이 current mutation 없이 닫힐 수 있으면 seal을 위해 source / rendered / runtime / package surface를 변경하지 않는다.

* 최소 결과 trace:

  * current-like payload guard: `PASS`
  * sealed runtime universe: `2105` rows / `21` unadopted
  * current-like `publish_state`: `0`
  * forbidden / unclassified current-like state: `0`
  * historical-only incompatible residue: `2`
  * residual seal: `PASS / no current mutation required`

* 오독 금지:

  * historical rollback residue를 current cleanup target, runtime debt 또는 current authority로 승격하지 않는다.
  * residual-seal PASS는 source / rendered / runtime / package mutation이나 새 current-authority cutover를 뜻하지 않는다.
  * runtime payload state PASS는 package publication, Publish Boundary PASS, public-text acceptance, manual QA 또는 release readiness를 뜻하지 않는다.
  * COMMON-RUNTIME-SURFACE-NONMUTATION.
  * COMMON-RELEASE-NONDECISION.

* Predecessor trace:

  * predecessor rollback snapshot의 current-incompatible residue는 historical-only로 격하됐다.
  * residual-seal lifecycle은 current payload를 재작성하지 않고 governance-only seal로 닫혔다.

* Trace:

  * residual seal implemented / validated / sealed: 2026-06-27
  * COMMON-EVIDENCE-TRACE.


### Iris Artifact Registry — rendered write / Lua export boundary

* 상태: current readpoint / write-export boundary sealed

* 결정: current rendered artifact와 Lua runtime projection의 생성은 명시된 artifact role과 context를 통과하는 공용 write / export boundary에서만 허용하며 historical·partial·ambiguous output이 current-equivalent surface에 기록되지 못하게 한다.

* 현재 기준:

  * current rendered write 보호는 특정 CLI에만 걸지 않고 실제 공용 writer boundary에 적용한다.
  * rendered write는 `current / staging / historical / diagnostic` context를 명시적으로 구분한다.
  * current-equivalent write는 current profile, current input contract와 허용된 current output set을 모두 만족해야 한다.
  * legacy / partial / ambiguous / unknown context에서 current-equivalent output을 생성하지 않는다.
  * Lua bridge exporter의 기본 경로는 monolith가 아니라 chunk-based runtime payload projection을 생성한다.
  * 기본 exporter route는 staging context의 chunk-shaped output을 만들며 그 결과 자체를 current adoption이나 package authority로 읽지 않는다.
  * monolith export는 historical / diagnostic side-output으로만 허용하고 current / staging runtime projection으로 사용하지 않는다.
  * generated staging output은 current-compatible shape를 가질 수 있어도 별도 adoption 없이 live current authority가 되지 않는다.

* 최소 결과 trace:

  * rendered write boundary: `PASS`
  * protected current rendered outputs: unauthorized mutation `0`
  * default chunk export: `PASS`
  * current / staging monolith export rejection: `PASS`

* 후속 input artifact:

  * regeneration tool: `Iris/build/description/v2/tools/build/export_dvf_3_3_lua_bridge.py`
  * current regeneration manifest: `Iris/build/description/v2/data/dvf_3_3_input_manifest.json`

* 오독 금지:

  * default chunk export는 exporter contract 정렬이지 live current-authority adoption, runtime replacement 또는 cutover가 아니다.
  * staging chunk output을 current runtime payload나 deployable package authority로 승격하지 않는다.
  * historical / diagnostic monolith support는 current monolith runtime path의 복구를 뜻하지 않는다.
  * COMMON-RUNTIME-SURFACE-NONMUTATION.
  * COMMON-RELEASE-NONDECISION.

* Trace:

  * compose write guard implemented / validated: 2026-06-13
  * Lua bridge export contract implemented / validated: 2026-06-15
  * COMMON-EVIDENCE-TRACE.


### Iris Artifact Registry — artifact role / VCS / predecessor reentry boundary

* 상태: current readpoint / artifact-authority classification sealed / stale reentry guard adopted

* 결정: IAR는 artifact의 authority / lifecycle role과 VCS 상태를 분리하고 historical / staging / diagnostic / fixture / stale artifact가 경로나 tracking 상태만으로 current authority에 재진입하지 못하게 한다. Physical storage placement와 compaction 방식은 Repository policy가 별도로 소유한다.

* 현재 기준:

  * `tracked / ignored / generated`는 VCS / representation state이며 artifact authority 자체가 아니다.
  * tracked artifact를 자동 current authority로 승격하지 않는다.
  * ignored artifact를 자동 삭제 가능 / 비중요 artifact로 판정하지 않는다.
  * IAR는 artifact를 current authority, current-required evidence, staging, historical reproduction, diagnostic, fixture, quarantine / predecessor 등의 lifecycle role로 분류한다.
  * generated staging artifact는 별도 adoption 없이 current source / rendered / runtime / package authority가 아니다.
  * stale bridge, rollback snapshot, predecessor fixture와 historical staging evidence는 historical / diagnostic / provenance role로만 소비한다.
  * quarantine은 predecessor preservation role이며 current runtime fallback이나 package authority가 아니다.
  * current-like path에 존재한다는 사실만으로 stale artifact를 current authority로 재승격하지 않는다.
  * required artifact의 실제 durability / CAS / external archive / disposable placement는 Repository placement policy와 required-evidence policy가 소유한다.
  * physical representation의 변경은 IAR authority role 자체를 자동 변경하지 않는다.

* 최소 결과 trace:

  * artifact authority / VCS separation: `adopted`
  * predecessor / stale reentry guard: `PASS`
  * stale current-authority reentry: `0`

* 오독 금지:

  * tracking state를 authority state로 읽지 않는다.
  * quarantine을 current fallback으로 읽지 않는다.
  * generated staging shape parity를 current adoption으로 읽지 않는다.
  * physical storage 위치를 authority 승격 / 강등 근거로 사용하지 않는다.
  * COMMON-RUNTIME-SURFACE-NONMUTATION.
  * COMMON-RELEASE-NONDECISION.

* Predecessor trace:

  * legacy bridge가 stale / quarantine role로 격하됐다.
  * Artifact VCS Tracking Policy가 tracking과 authority를 분리했다.
  * required-artifact preservation lifecycle은 physical durability를 검증했지만 VCS 상태를 authority로 승격하지 않았다.
  * COMMON-EVIDENCE-TRACE.


### Iris Artifact Registry — consumer denominator / terminal disposition governance

* 상태: current readpoint / denominator gate adopted / terminal canonical complete / shared disposition guard adopted / governance-only

* 결정: IAR의 consumer disposition은 공식 consumer universe, migration / readiness subset과 terminal disposition을 서로 다른 lifecycle axis로 관리하며 하나의 shared disposition readpoint를 통해 provenance evidence가 실행 authority로 오인되지 않도록 봉인한다.

* 현재 기준:

  * 공식 completion unit은 `executing_consumer_member_row`다.
  * 공식 terminal denominator는 `1062` executing-consumer member rows다.
  * unique path, semantic consumer object, source / runtime entry, raw occurrence row 또는 readiness evidence row를 공식 completion unit으로 대체하지 않는다.
  * broad consumer universe, change-required subset과 readiness / sandbox subset은 서로 다른 denominator와 lifecycle role을 가진다.
  * `311`은 change-required audit subset이고 `163`은 readiness / sandbox apply-evidence subset이며 어느 쪽도 `1062` completion denominator를 대체하지 않는다.
  * terminal disposition은 `153 migrated / 268 no-op / 3 diagnostic-only / 638 historical-only`로 `1062` 전체 consumer universe를 닫는다.
  * terminal `migrated`는 disposition classification이며 live migration execution 또는 current-authority cutover 완료를 뜻하지 않는다.
  * denominator identity, terminal disposition, lifecycle role과 provenance / readiness role은 shared disposition contract를 통해 함께 소비한다.
  * raw audit, readiness, dry-run, sandbox 또는 predecessor artifact는 provenance evidence로만 소비하며 직접 execution authority로 사용하지 않는다.
  * consumer denominator / disposition governance는 live required-validation 경로에 결속해 denominator 교체, raw-authority reentry와 dual-authority consumption을 fail-closed한다.
  * 후속 Source-Overlay / current-route repair는 이 denominator나 terminal disposition을 재정의하거나 다시 adjudicate하지 않는다.

* 최소 결과 trace:

  * official denominator: `1062 executing_consumer_member_rows`
  * terminal disposition: `153 migrated / 268 no-op / 3 diagnostic-only / 638 historical-only / unresolved 0`
  * terminal adjudication: `PASS`
  * shared disposition guard: `PASS / required gate adopted`

* 오독 금지:

  * `1062`, `311`, `163`은 서로 다른 denominator / subset이며 서로 대체하지 않는다.
  * terminal `153 migrated`를 live migration execution count나 mutation completion으로 읽지 않는다.
  * sandbox / readiness / dry-run evidence를 live completion이나 execution authority로 승격하지 않는다.
  * 후속 Source-Overlay Repair PASS를 denominator lock이나 terminal disposition의 재개로 읽지 않는다.
  * COMMON-RELEASE-NONDECISION.
  * COMMON-RUNTIME-SURFACE-NONMUTATION.

* Predecessor trace:

  * Consumer Universe Denominator Lock은 `1062` universe를 공식 terminal denominator로 고정했다.
  * Terminal Disposition Adjudication은 전체 universe를 terminal disposition으로 닫았다.
  * Shared Disposition Ledger Consumption은 denominator identity, terminal disposition, lifecycle과 provenance role을 required-validation consumption contract로 결속했다.
  * COMMON-EVIDENCE-TRACE.


### Iris Artifact Registry — completion claim / predecessor reentry boundary

* 상태: current readpoint / closeout-reentry guard canonical complete / governance-only

* 결정: IAR의 completion claim은 lifecycle axis를 명시해야 하며 한 axis의 completion이나 historical predecessor evidence를 다른 lifecycle completion 또는 current authority로 확대하지 못하게 한다.

* 현재 기준:

  * bare `complete` claim은 허용하지 않는다.
  * terminal disposition, broad consumer completion, cutover subset completion, pre-apply readiness, live apply authorization, live migration execution, required-validation adoption과 historical predecessor trace는 서로 다른 claim axis다.
  * 한 axis의 PASS / completion을 다른 axis의 completion으로 자동 승격하지 않는다.
  * readiness / eligibility는 execution completion이 아니다.
  * cutover subset completion은 broad consumer completion이 아니다.
  * terminal `migrated` disposition은 live mutation execution completion이 아니다.
  * predecessor counts와 historical artifacts는 historical comparison / provenance 문맥에서만 소비하며 current hard gate, runtime / package authority, current debt 또는 migration-target expansion 근거로 재사용하지 않는다.
  * stale predecessor anchor가 current consumer에 필요하면 successor authority context 또는 explicit non-apply context에 다시 결속한다.
  * historical claim token이나 predecessor artifact를 current claim authority로 재진입시키는 해석은 fail-closed한다.

* 최소 결과 trace:

  * closeout / reentry guard: `PASS / canonical complete`
  * bare completion claim: `forbidden`
  * predecessor current-authority reentry: `0`

* 오독 금지:

  * terminal / broad / cutover / readiness / authorization / execution completion을 서로 대체하지 않는다.
  * predecessor counts나 artifacts를 current runtime / package authority, current debt 또는 fallback으로 복원하지 않는다.
  * 이 heading은 machine validation / independent review / owner seal의 completion 기준을 소유하지 않는다.
  * COMMON-RUNTIME-SURFACE-NONMUTATION.
  * COMMON-RELEASE-NONDECISION.

* Predecessor trace:

  * Problem 7과 후속 Closeout / Reentry Guard가 source-overlay repair, completion vocabulary와 predecessor reentry 문제를 분리했다.
  * predecessor current-like claims은 historical / provenance context로 격하됐다.
  * round-local branch token과 exact review artifact identity는 `COMMON-EVIDENCE-TRACE`에 보존한다.
  * COMMON-EVIDENCE-TRACE.


### Iris Artifact Registry — required-validation / evidence integrity

* 상태: current readpoint / required-evidence integrity closure canonical complete / governance-only

* 결정: IAR의 required-validation은 current authority를 증명하는 데 필요한 artifact와 validation evidence의 identity, freshness, durability와 재현성을 하나의 governance contract로 결속하며 validation evidence 자체를 source / rendered / runtime / package writer authority로 승격하지 않는다.

* 현재 기준:

  * live `current_route_required_validations.json`을 current-required validation surface의 기준 manifest로 사용한다.
  * required evidence는 current authority reference, artifact identity / freshness, deterministic rebuild, validation tooling과 VCS preservation 상태를 같은 readpoint에서 결속해야 한다.
  * current-required durable artifact는 해당 lifecycle role에 따라 실제로 보존되어야 한다.
  * required surface의 missing, stale, dirty, untracked 또는 unintended ignore 상태는 evidence-integrity 문제로 fail-closed한다.
  * protected-surface approval은 path 이름만으로 부여하지 않는다.
  * 승인된 protected-surface delta는 exact successor identity에 결속하며 같은 path의 후속 임의 변경이 이전 승인을 자동 상속하지 않는다.
  * line-ending / representation normalization은 semantic mutation과 구분하되 authority-bearing identity가 어떤 canonicalization을 사용하는지는 명시한다.
  * required artifact의 `tracked / ignored / generated` 상태와 authority status는 구분한다.
  * deterministic rebuild와 current-route validation은 evidence integrity를 증명하는 축이며 mutation 권한을 만들지 않는다.
  * intermediate preflight, disposition, correction 또는 reconciliation result는 parent closure의 input일 뿐 별도 authority가 아니다.
  * final command / validation matrix는 execution evidence binding이며 second authority가 아니다.

* 최소 결과 trace:

  * required-evidence integrity closure: `PASS / canonical complete`
  * protected-surface path-only approval: `forbidden`
  * protected successor identity binding: `required`
  * deterministic rebuild / evidence binding: `sealed`

* 오독 금지:

  * required-validation PASS나 canonical governance seal을 writer authority로 읽지 않는다.
  * protected path가 한 번 승인됐다는 이유로 같은 경로의 향후 내용을 자동 승인하지 않는다.
  * tracked 상태를 authority status로, ignored 상태를 deletable status로 읽지 않는다.
  * generated staging evidence를 live manifest adoption 없이 current-required durable evidence로 승격하지 않는다.
  * deterministic rebuild / current-route validation / Lua syntax PASS는 runtime rollout, package publication, manual QA 또는 public-text acceptance를 뜻하지 않는다.
  * COMMON-RELEASE-NONDECISION.
  * COMMON-RUNTIME-SURFACE-NONMUTATION.

* Predecessor trace:

  * required-evidence closure lifecycle은 current authority reference, required artifact identity / freshness와 VCS preservation을 하나의 hash-bound governance readpoint로 봉인했다.
  * 2026-08-03 residual refactoring의 path-only approval 문제는 successor exact-identity binding으로 수정됐다.
  * EOL normalization, Windows path shortening, BOM defer 같은 세부는 implementation evidence로 `COMMON-EVIDENCE-TRACE`에 보존한다.
  * COMMON-EVIDENCE-TRACE.


### Iris Artifact Registry — validation / independent review / owner seal 경계

* 상태: current readpoint / validation-review-seal axes split / governance-only

* 결정: machine validation, independent review, owner decision / seal과 canonical closure eligibility는 서로 다른 governance axis로 유지하며 어느 하나도 다른 축을 자동으로 대체하지 않는다.

* 현재 기준:

  * machine-generated PASS는 independent review PASS가 아니다.
  * external validation bundle의 존재나 freshness만으로 independent review가 완료되지 않는다.
  * independent review는 review subject와 evidence identity가 명시적으로 결속돼야 한다.
  * owner approval / adoption / seal은 independent review를 대체하지 않는다.
  * independent review 역시 owner decision이 필요한 claim의 owner seal을 자동 대체하지 않는다.
  * machine validation, independent review와 owner seal이 모두 필요한 closure에서는 각 axis를 별도로 충족해야 한다.
  * intermediate readiness와 `canonical_seal_allowed=true` 같은 eligibility는 canonical closure 자체가 아니다.
  * round-local temporary artifact filename 자체가 permanent review authority가 되지 않으며 review subject의 exact identity binding이 중요하다.

* 영향:

  * 자체 생성 PASS, external bundle 존재 또는 owner approval만으로 canonical completion을 세탁하는 것을 막는다.

* 오독 금지:

  * machine PASS를 independent review PASS로 읽지 않는다.
  * independent review PASS를 owner seal로 읽지 않는다.
  * owner seal을 validation / review의 대체 근거로 사용하지 않는다.
  * seal eligibility를 다른 decision family의 completion이나 release readiness로 확대하지 않는다.
  * COMMON-RUNTIME-SURFACE-NONMUTATION.
  * COMMON-RELEASE-NONDECISION.

* Predecessor trace:

  * Completion Vocabulary External Gate Split이 code-generated PASS, external validation, independent review, owner decision / seal을 별도 axis로 분리했다.
  * 특정 temporary review artifact path + SHA binding은 exact review identity principle을 확립한 implementation precedent이며 filename 자체는 current contract가 아니다.
  * COMMON-EVIDENCE-TRACE.


### Iris Artifact Registry — consumer migration authorization lineage

* 상태: current readpoint / predecessor pre-apply authorization preserved / no current live-apply authority

* 결정: 과거 consumer-migration pre-apply authorization은 봉인된 subject와 target identity에 결속된 historical authorization으로 보존하며 후속 source / runtime / repository 변경에 자동 상속하지 않는다. 현재 live apply는 fresh authorization 없이는 실행할 수 없다.

* 현재 기준:

  * predecessor terminal disposition의 `153 migrated` classification과 과거 pre-apply authorization은 서로 다른 lifecycle axis다.
  * predecessor authorization은 당시 `109 live_mutation_eligible + 44 evidence_only + 0 blocked` scope를 대상으로 봉인됐다.
  * `109`는 당시 authorization subject의 mutation-eligible subset이지 current HEAD의 executable mutation count가 아니다.
  * `44 evidence_only`는 당시에도 live mutation target이 아니었다.
  * predecessor authorization round에서는 live apply가 실행되지 않았다.
  * pre-apply authorization은 exact target identity, preimage, dirty-state isolation, writer capability, execution plan과 review evidence에 subject-bound된다.
  * 이후 implementation이 변경됐다고 해서 predecessor authorization이 새 subject에 자동 승계되지 않는다.
  * current live apply를 열려면 current subject에서 target universe, preimage, protected-surface relation과 execution evidence를 다시 결속한 fresh authorization이 필요하다.
  * fresh authorization이 없으면 live migration execution authority는 `not authorized`로 읽는다.

* 최소 결과 trace:

  * predecessor terminal migrated projection: `153`
  * predecessor live-mutation eligible subset: `109`
  * predecessor evidence-only subset: `44`
  * predecessor live apply execution: `not executed`
  * current live-apply authorization: `none`

* 오독 금지:

  * predecessor `phase4_live_apply_allowed=true`를 current subject의 execution permission으로 읽지 않는다.
  * `109`를 current executable mutation count로 읽지 않는다.
  * terminal `153 migrated`를 live execution count로 읽지 않는다.
  * predecessor readiness evidence를 current writer authority로 승격하지 않는다.
  * COMMON-RUNTIME-SURFACE-NONMUTATION.
  * COMMON-RELEASE-NONDECISION.

* Predecessor trace:

  * Terminal Disposition lifecycle이 `153 migrated`를 terminal classification으로 닫았다.
  * predecessor Live Migration Readiness lifecycle은 이를 `109 mutation-eligible / 44 evidence-only`로 분해해 subject-bound pre-apply authorization을 봉인했다.
  * 해당 authorization round의 `live_apply_mode`는 disabled였고 실제 mutation execution은 수행되지 않았다.
  * 후속 Iris changes는 해당 authorization을 current permission으로 자동 갱신하지 않는다.
  * exact execution plan, authorization verdict, dirty-state proof와 review receipt는 `COMMON-EVIDENCE-TRACE`에 보존한다.
  * COMMON-EVIDENCE-TRACE.


### Iris Artifact Registry — Registry Authority closure protocol / attempt integrity guard

* 상태: current guard / predecessor canonical closure preserved / append-only attempt contract active

* 결정: Registry Authority closure는 실패 evidence의 삭제·덮어쓰기·replay를 허용하지 않는 append-only attempt protocol을 따른다. 이 protocol은 current governance rule로 유지하지만 과거 특정 attempt의 `canonical_complete` 상태를 이후 authority readpoint의 current identity로 자동 승계하지 않는다.

* 현재 기준:

  * `cycle`과 `attempt`는 서로 다른 lifecycle identity로 관리한다.
  * gate adoption 전이고 protected mutation이 없으면 같은 cycle에서 새로운 attempt를 열 수 있다.
  * 새 attempt는 predecessor failure evidence를 보존하고 새로운 attempt identity / output scope / one-use execution identity를 사용한다.
  * 같은 attempt의 claim-bearing result, receipt, failure record와 execution evidence는 write-once다.
  * FAIL을 삭제·덮어쓴 뒤 같은 attempt identity를 PASS에 재사용하지 않는다.
  * one-use execution receipt / nonce를 재소비하거나 replay하지 않는다.
  * gate adoption 뒤 execution result나 protected surface에 영향을 주는 correction은 additive correction record와 affected validation rerun을 요구한다.
  * execution 결과는 고정되어 있고 duplicate metadata projection만 누락된 경우에 한해 원래 FAIL을 보존하는 bounded same-attempt correction을 허용할 수 있다.
  * 기존 값이 충돌하거나 다른 identity를 가리키는 경우 bounded correction으로 PASS 처리하지 않는다.
  * 이후 Registry authority transition이 발생하면 새 current authority closure는 해당 current subject에 대해 별도 closure evidence를 가져야 한다.
  * 과거 `canonical_complete` attempt는 protocol precedent와 historical closure evidence이며 최신 Registry authority identity의 자동 current readpoint가 아니다.

* 영향:

  * failure laundering을 막는 protocol은 계속 유지하면서 특정 과거 closure attempt를 후속 authority transition 이후에도 current authority처럼 읽는 문제를 방지한다.

* 최소 결과 trace:

  * attempt-integrity protocol: `active`
  * predecessor practical Registry closure: `canonical_complete / historical`
  * predecessor failure evidence: `preserved`
  * same-attempt execution replay allowance: `none`

* 오독 금지:

  * predecessor canonical closure를 이후 facts / Registry adoption의 current authority identity로 읽지 않는다.
  * bounded verifier correction을 일반적인 same-attempt rerun이나 failed execution 재사용 권한으로 읽지 않는다.
  * reviewer / owner / attempt evidence를 source / rendered / runtime / package authority로 승격하지 않는다.
  * COMMON-RUNTIME-SURFACE-NONMUTATION.
  * COMMON-RELEASE-NONDECISION.

* Predecessor trace:

  * `attempt-0037-practical` failure는 보존된 predecessor failure다.
  * `attempt-0038-practical`은 post-matrix verifier FAIL을 삭제하지 않고 additive same-attempt correction으로 닫아 당시 Registry Authority closure를 `canonical_complete`로 봉인했다.
  * 후속 Food Semantic Facts Registry adoption 등 current authority transition이 발생했으므로 `attempt-0038-practical`은 current authority identity가 아니라 historical closure / protocol precedent로 읽는다.
  * exact attempt, commit, correction artifact, hash와 review / owner-seal evidence는 `COMMON-EVIDENCE-TRACE`에 보존한다.
  * COMMON-EVIDENCE-TRACE.


### Iris Artifact Registry — Registry Runtime Compatibility / defect-attribution boundary

* 날짜: 2026-08-01 current freshness readpoint 포함

* 상태: current readpoint / compatibility contract adopted / defect-attribution gate sealed / current RTC PASS not newly asserted

* 결정: Registry Runtime Compatibility는 source에서 runtime / package projection까지 exact key identity를 보존하면서 consumer별 comparison semantics 차이로 인한 병합·덮어쓰기·유실을 막는 독립 계약으로 둔다. RTC debt나 successor correction lifecycle은 temporary tooling / evidence-freshness 문제만으로 열지 않고 current Registry-to-runtime identity defect가 canonical evidence로 귀속된 경우에만 연다.

* 현재 기준:

  * source → rendered artifact → Lua bridge → runtime chunk → package projection은 동일한 exact key universe를 보존한다.
  * Lua의 exact·case-sensitive key identity와 Windows 계열 consumer의 case-insensitive comparison identity는 서로 다른 개념으로 취급한다.
  * case-insensitive collision은 기본적으로 fail-closed한다.
  * 의도적인 case-variant 공존은 명시적인 policy와 각 exact entry를 손실 없이 표현하는 consumer representation이 함께 있을 때만 허용한다.
  * 허용된 collision도 alias, rename, winner selection 또는 semantic equivalence를 뜻하지 않는다.
  * consumer representation이 case-variant identity를 안전하게 표현하지 못하는 경우 exact identity를 보존하는 record representation을 사용한다.
  * compatibility contract는 bridge materialization, runtime payload assembly와 package projection 같은 identity boundary에서 일관되게 검증한다.
  * compatibility violation은 downstream projection을 fail-closed할 수 있지만 source item spelling, 의미 또는 semantic identity를 임의 수정할 권한을 만들지 않는다.
  * compatibility authority는 live current-required evidence에 결속한다.
  * evidence / tooling freshness 문제와 current Registry-to-runtime identity defect는 별도 판정한다.
  * temporary script, staging / worktree failure, implementation-toolchain freshness failure 또는 predecessor bundle과 current checkout의 단순 path-hash drift만으로 RTC debt를 선언하지 않는다.
  * RTC successor correction lifecycle은 canonical Iris runner failure, clean-checkout reproduction, temporary orchestration 비의존성, current identity mismatch, runtime / package effect와 exact failure evidence가 결속된 경우에만 연다.
  * defect-attribution 조건 중 하나라도 false / missing / unknown이면 successor scope를 열지 않는다.
  * Lua renderer는 봉인된 offline identity와 payload를 소비해 표시할 뿐 identity를 재해석하거나 quality judgment를 수행하지 않는다.

* 영향:

  * RTC는 Registry Authority, DVF Body Compiler와 Publish Boundary에서 분리된 독립 claim axis다.
  * defect attribution이 성립하지 않았다는 사실은 current RTC PASS와 동일하지 않다.

* 최소 결과 trace:

  * compatibility contract: `adopted`
  * canonical RTC defect attribution: `not established`
  * successor RTC correction / adoption authorization: `not opened`
  * current RTC PASS: `not newly asserted`

* 오독 금지:

  * compatibility contract adoption 자체를 current RTC PASS로 읽지 않는다.
  * temporary tooling failure나 historical bundle drift를 current RTC defect로 자동 승격하지 않는다.
  * canonical defect attribution이 없는 상태를 RTC PASS로도 RTC debt로도 임의 판정하지 않는다.
  * predecessor RTC PASS를 current certification으로 재봉인하지 않는다.
  * current-runtime package identity PASS를 RTC certification과 동일시하지 않는다.
  * COMMON-RELEASE-NONDECISION.
  * COMMON-RUNTIME-SURFACE-NONMUTATION.

* Predecessor trace:

  * 초기 RTC contract는 exact key universe와 collision fail-closed 원칙을 봉인했다.
  * 2026-07-29 Food Semantic Registry adoption 직후 `stale_requires_successor_rtc` coordination state가 기록됐다.
  * 2026-08-01 defect-attribution gate는 temporary tooling / path-hash drift만으로 RTC debt를 선언하는 해석을 거부했다.
  * canonical defect attribution이 성립하지 않아 후속 RTC lifecycle은 열리지 않았다.
  * COMMON-EVIDENCE-TRACE.


### Iris Artifact Registry — Food Semantic Facts authority reconstruction / current adoption

* 날짜: 2026-07-29

* 상태: current readpoint / current adoption complete / food-semantic facts authority reconstruction resolved

* 결정: 317개 식품의 의미 사실이 과도하게 단일 의미 조건으로 수렴하던 facts-authority 문제는 Evidence Allowlist, row-level lineage, closed food-semantic schema, automatic mapping과 explicit curated approval을 통해 successor facts로 재구축하고 IAR가 봉인된 exact successor를 current facts authority로 채택한다.

* 현재 기준:

  * current food-semantic authority는 `317`개 대상 식품에 대해 `718`개 approved propositions와 `17`개 meaningful semantic partitions를 보존한다.
  * automatic proposition `84`개와 explicitly approved curated proposition `634`개는 provenance를 구분해 유지한다.
  * unsupported fact, arbitrary inference, Layer 4 automatic promotion, compiler-invented proposition과 dropped proposition을 허용하지 않는다.
  * successor generation과 Registry adoption은 서로 다른 lifecycle role이다.
  * Registry adoption은 봉인된 exact successor facts를 current facts authority로 채택하며 successor identity를 임의 재판정하거나 재작성하지 않는다.
  * current facts / manifest에서 ambiguity, partial-current 또는 dual-current authority를 허용하지 않는다.
  * facts-authority completion은 Naturalization, rendered prose quality, RTC와 Publish Boundary acceptance에서 독립된 axis다.
  * 후속 Naturalization은 adopted current facts를 소비하되 facts authority를 임의 재구축하거나 재판정하지 않는다.

* 최소 결과 trace:

  * target food items: `317`
  * approved propositions: `718`
  * meaningful semantic partitions: `17`
  * automatic / curated propositions: `84 / 634`
  * unsupported / arbitrary / compiler-invented / dropped propositions: `0`
  * Registry adoption: `current_adoption_complete`

* 오독 금지:

  * sealed successor handoff를 그 자체로 current adoption이나 Publish Boundary PASS로 읽지 않는다.
  * current adoption을 rendered prose quality completion이나 RTC PASS로 확대하지 않는다.
  * facts authority reconstruction 완료를 모든 public-facing 문장 품질 문제가 해결됐다는 뜻으로 읽지 않는다.
  * COMMON-RELEASE-NONDECISION.
  * COMMON-RUNTIME-SURFACE-NONMUTATION.

* Predecessor trace:

  * G2는 replacement facts-authority candidate를 sealed non-current successor로 구축했다.
  * G3가 exact successor facts를 current facts authority로 채택했다.
  * G3 직후의 Naturalization pending과 RTC coordination state는 후속 lifecycle에 의해 소비된 predecessor trace다.
  * COMMON-EVIDENCE-TRACE.


### Iris validation — current / historical / diagnostic route separation

* 상태: current readpoint / validation-route separation sealed

* 결정: Iris의 current, historical reproduction과 diagnostic validation은 서로 다른 목적, denominator와 판정 기준을 가진 독립 route로 유지하며, 한 route의 PASS / FAIL / advisory 결과를 다른 route의 결과로 대체하거나 세탁하지 않는다.

* 현재 기준:

  * current route는 현재 authority와 production contract가 요구하는 surface를 검증한다.
  * historical route는 봉인된 historical reproduction contract와 해당 readpoint의 보존된 입력을 검증한다.
  * current taxonomy나 current test universe가 확장되더라도 historical pinned denominator와 전체 equality를 요구하지 않는다.
  * diagnostic route는 current 또는 historical authority를 정의하지 않는 advisory / forensic surface로 별도 실행·판정한다.
  * diagnostic raw failure와 terminal disposition은 별도 상태다.
  * 승인된 diagnostic finding을 non-blocking으로 disposition할 수 있지만 raw FAIL / finding 자체를 PASS로 rewrite하지 않는다.
  * diagnostic adapter / classification success를 underlying raw diagnostic PASS로 표현하지 않는다.
  * current / historical / diagnostic route는 서로 다른 denominator와 lifecycle role을 가질 수 있으며 count equality를 요구하지 않는다.
  * current route PASS는 historical route PASS나 diagnostic 결과를 대체하지 않는다.
  * historical route PASS는 current authority adoption이나 current-route completion을 뜻하지 않는다.
  * historical / diagnostic test, fixture와 tooling은 current build surface에 존재한다는 이유만으로 current production authority가 되지 않는다.

* 최소 결과 trace:

  * current / historical / diagnostic route separation: `sealed`
  * raw diagnostic result / terminal disposition separation: `adopted`
  * historical denominator preservation: `required`
  * route-result cross-substitution: `forbidden`
  * diagnostic failure laundering: `forbidden`

* 오독 금지:

  * current route PASS를 historical reproduction, diagnostic PASS 또는 full historical byte reproducibility의 자동 증명으로 읽지 않는다.
  * historical route PASS를 current source / rendered / runtime / package authority로 승격하지 않는다.
  * diagnostic adapter success나 `blocking=false`를 raw diagnostic PASS로 읽지 않는다.
  * current PASS를 이용해 diagnostic finding을 삭제·재작성하지 않는다.
  * current taxonomy 증가를 이유로 sealed historical denominator를 소급 재작성하지 않는다.
  * COMMON-RELEASE-NONDECISION.
  * COMMON-RUNTIME-SURFACE-NONMUTATION.

* Predecessor trace:

  * 2026-06-11 current / historical / diagnostic contract split이 최초 route separation을 봉인했다.
  * 2026-08-03 residual refactoring은 historical denominator와 current taxonomy denominator를 분리하고 diagnostic raw failure와 terminal non-blocking disposition을 구분했다.
  * 후속 repository/runtime lightweighting도 diagnostic raw result를 PASS로 rewrite하지 않는 원칙을 재확인했다.
  * exact route counts, finding fingerprints와 disposition inventories는 `COMMON-EVIDENCE-TRACE`에 보존한다.
  * COMMON-EVIDENCE-TRACE.


### Iris validation — temporary/nonregular executable physical retirement authority

* 날짜: 2026-08-23

* 상태: current readpoint / owner-approved authority-only transition / destructive mutation not yet applied

* 결정: current product 또는 validation-system contract가 없는 historical reproduction과 diagnostic/evidence executable의 repository-local replay route를 종료하고, 불변 predecessor ledger·sealed receipt·Git history를 non-executing evidence로 보존한다. 실제 current contract가 다시 확인된 source는 기존 분류와 무관하게 current로 보존한다.

* 권한 binding:

  * owner authority: 2026-08-23 repository-owner prompt preapproval
  * governing roadmap attachment: `739c27fb-cef7-4206-a29e-0c99e722d55a`
  * roadmap raw SHA-256: `a379baf8be5563631c5d7c5ce00ea50d109600a344e3ca0d2c2407179a06b551`
  * P1~P10 table SHA-256: `c0cd36edbcf25706e2f3cdf0661933df6a3d6c3da758a600807ff3908f9f65bb`
  * predecessor decision blob: `9fc1a6863bb01fd142eda25f48e8c6da25eba818`
  * S0 commit/tree: `fd0504817af8c1031ac794391cf67d129c8db54c` / `395ec36de921987299fa9a9d9bb46118b74160a5`

* 적용 범위:

  * `round3_run_contract_tests.py --class historical|diagnostic|all`의 repository-local executable availability를 종료하고 `--class current`만 유지한다.
  * 심사 결과 `remove_executable` 또는 `externalize_nonexecuting_evidence`로 닫힌 source, mixed callable, exact membership을 제거한다.
  * full-gate conflict 7-source/56-identity 중 current compiler/constituent contract 3-source/39-identity는 current authority로 보존하고, lifecycle-bound 4-source/17-identity만 제거한다.
  * ignored/untracked local source 삭제는 exact path/hash archive·restore gate를 통과한 owner-approved set에만 적용한다.

* 보존 불변식:

  * sealed historical denominator/identity set, predecessor census ledger, historical corpus/receipt를 rewrite하지 않는다.
  * current/historical/diagnostic result cross-substitution 금지를 유지한다.
  * repository-local replay availability 종료는 과거 receipt의 historical 사실을 취소하지 않는다.
  * current runtime Lua, product data, public text, package output은 변경하지 않는다.
  * 삭제 transaction이 중단되면 source·membership·route를 같은 batch로 복구하고, 이 authority를 history에서 rewrite하지 않는다.

* claim ceiling: 이 결정은 승인된 validation executable의 물리 퇴역과 repository-local replay availability 종료만 권한화한다. Iris runtime correctness, release, Workshop, B42 readiness, public-text quality acceptance 또는 과거 historical replay PASS를 새로 주장하지 않는다.


### Iris validation — regular membership non-self-authorization and survival adjudication

* 날짜: 2026-08-23

* 상태: current readpoint / additive correction to the temporary/nonregular executable retirement authority / destructive mutation not authorized by membership alone

* 결정: regular membership은 survival authority를 자기 승인할 수 없다. Predecessor에서 regular로 분류된 모든 executable identity를 survival candidate로 다시 심사하고, registry 밖의 독립 current authority·반복 실행 필요성·lifecycle 독립성·비중복성이 확인된 경우에만 regular로 유지한다.

* 필수 판정 규칙:

  1. taxonomy, manifest, pytest discovery, regular gate, required-validation registration, predecessor ledger와 기존 regular disposition은 membership을 보여주는 discovery evidence일 뿐, 영구 regular authority 존속의 독립 근거가 아니다.
  2. predecessor regular identity 전체는 자동 `keep`이 아니라 survival candidate다.
  3. `keep`은 registry 밖의 정확한 current contract authority, recurring execution obligation, lifecycle independence와 duplicate/superset 부재를 모두 요구한다.
  4. migration, roadmap, defect reproduction, closeout, seal, snapshot 또는 legacy DVF 단계에 결속된 검사는 current registry membership만으로 regular authority를 유지할 수 없다.
  5. 다른 surviving test가 동일하거나 더 넓은 input/observable/failure contract를 보호하면, 중복 검사는 필요한 최소 contract migration 후 제거하거나 직접 제거한다.
  6. predecessor regular `599` identity의 blanket keep을 금지한다.
  7. baseline pytest `433`, standalone `4`, regular identity `599`는 보존 목표값이 아니다. Final denominator는 survival adjudication과 실제 cleanup 결과에서 다시 생성한다.
  8. historical denominator/evidence 보존은 sealed ledger, receipt, immutable corpus reference와 Git history 같은 non-executing evidence를 보존한다는 뜻이며, 모든 historical/diagnostic executable source나 repository-local replay route의 영구 보존을 뜻하지 않는다.
  9. historical executable removal만으로 current regular authority 오승격 cleanup이 완료되지 않는다.
  10. predecessor regular identity 전체의 survival adjudication이 닫히기 전에 taxonomy, manifest, discovery, gate를 final state로 변경하거나 대규모 source 삭제를 시작하지 않는다.

* terminal disposition: `keep_regular_product_contract`, `keep_regular_validation_system_contract`, `migrate_then_remove`, `remove_regularized_temporary`, `blocked_needs_owner_authority` 중 하나만 identity에 부여한다.

* transaction boundary: canonical tracked cleanup과 dirty workspace test cleanup은 같은 survival 기준을 사용하되 별도 transaction으로 실행·측정한다. Dirty workspace의 non-test 사용자 변경은 조사·수정·stage·commit하지 않는다.

* authority ordering: `a8b03729124f8b08eeacc75c27626a285036a5f9`의 historical-route transition은 이 survival adjudication을 대체하지 않으며, 교정된 identity disposition과 registration delta가 닫히기 전에 destructive authority로 사용하지 않는다.


### Iris validation — adjudicated survival and bounded executable retirement

* 날짜: 2026-08-23

* 상태: current readpoint / additive successor to `a8b03729124f8b08eeacc75c27626a285036a5f9` / authority-only before destructive mutation

* 판정: `fd0504817af8c1031ac794391cf67d129c8db54c`의 predecessor regular 599 identity를 registration 밖의 current contract 기준으로 전량 재심사했다. 그 결과 234개는 `keep_regular_product_contract`, 94개는 `keep_regular_validation_system_contract`, 271개는 `remove_regularized_temporary`다. 이 수치는 보존 목표 상수가 아니라 이번 exact-subject 판정 결과다.

* non-current 판정: predecessor reproduction/evidence/expired 568 identity 중 3개 source family에 속한 public-text constituent 20 identity, Korean-prose compiler 16 identity, naturalization compiler identity 3 identity는 독립 current product authority와 actual full-gate consumer가 있어 `keep_regular_product_contract`로 승격한다. 나머지 529 identity는 repository-local executable obligation이 없는 lifecycle evidence로 판정해 `remove_regularized_temporary`로 닫는다.

* 역사 route 교정: `a8b03729124f8b08eeacc75c27626a285036a5f9`는 위 survival 판정 전에는 destructive authority가 아니었다. 이 successor가 허용하는 historical/diagnostic route 종료 범위는 `reproduction_retention_overlay.index.json`에서 `remove_regularized_temporary`로 닫힌 identity와 그 exclusive support뿐이다. 3개 source family의 39 current-product 승격 identity와 `survival_overlay.index.json`의 328 surviving regular identity는 route 종료 범위에서 제외한다.

* 물리 퇴역 범위: clean tracked transaction은 48 regularized-temporary source family의 268 identity, non-current tracked pure source 34개의 177 identity, mixed callable 2 identity와 exact exclusive support를 대상으로 한다. Dirty-main transaction은 predecessor hash와 일치하는 present ignored/untracked removal source 163개의 335 identity만, 외부 복구 archive 검증 뒤 exact `LiteralPath` 단위로 처리한다. clean/S0에는 없고 dirty main에만 있는 6 surviving product source family의 13 identity는 removal transaction에서 명시적으로 제외한다. 이미 부재한 14 local candidate와 관련 17 identity는 삭제 성과로 계상하지 않는다.

* 물리 도메인 정정: clean/S0 부재를 곧 source 부재로 간주하지 않는다. `test_iris_classification_baseline_receipt.py`는 dirty-main ignored removal candidate로 재분류했고, 같은 도메인에 있는 6 product-contract survivor는 hash-matched 생존 대상으로 기록했다. 이 정정 뒤 clean tracked와 dirty-main transaction의 path 집합은 서로 겹치지 않는다.

* 보존: predecessor 1,167-row ledger, immutable denominator/identity, sealed receipt와 Git history는 rewrite하지 않는다. 이 보존은 repository-local historical/diagnostic Python replay route의 존속을 요구하지 않는다. Current/historical/diagnostic 결과의 상호 대체 금지는 유지한다.

* claim ceiling: 이 결정은 adjudicated executable과 exclusive support의 retirement만 승인한다. Product runtime 변경, release/Workshop/B42 readiness, historical replay PASS 또는 public-text quality acceptance를 새로 주장하지 않는다.


### Iris Repository Validation — Clean-Checkout full-repository reproducibility contract

* 날짜: 2026-07-28 → successor validation readpoints

* 상태: current contract / Phase 0 accepted / G1 validated-subject terminal PASS preserved / current HEAD PASS not implied

* 결정: Iris의 clean-checkout validation은 subset 또는 advisory 검증이 아니라 mandatory full-repository gate contract로 유지한다. PASS는 exact tracked validation subject에 결속하며 이전 subject의 PASS를 후속 repository HEAD에 자동 상속하지 않는다.

* 현재 기준:

  * terminal target은 canonical mandatory full-repository validation gate다.
  * validation subject, execution environment와 provenance를 명시적으로 결속한다.
  * Python execution은 repository 밖 dedicated environment와 durable provenance를 사용한다.
  * hash-only identity를 provenance나 validated subject로 승격하지 않는다.
  * `partial`, `blocked`, advisory success 또는 incomplete evidence는 terminal PASS를 대체하지 않는다.
  * explicitly current-required source 분류는 filename / historical heuristic보다 우선한다.
  * required dependency closure는 import graph뿐 아니라 direct contract / runner / validator dependency를 포함한다.
  * subject-specific assessment result는 generic validation dependency와 분리한다.
  * temporary result는 repository 밖 disposable execution surface에서 생성한다.
  * clean gate는 exact tracked subject를 disposable checkout의 Run A/B에서 검증하고 denominator / dependency inventory / canonical result identity가 일치해야 PASS를 허용한다.
  * clean-checkout evidence는 append-only successor record로 전진한다.
  * terminal PASS는 검증된 exact subject에만 귀속한다.
  * repository HEAD가 변경되면 predecessor terminal PASS만으로 새 subject의 clean-checkout PASS를 주장하지 않는다.

* 최소 결과 trace:

  * Phase 0 initial attempt: `blocked`
  * Phase 0 successor: `accepted`
  * G1 exact validated subject: `terminal PASS`
  * current HEAD full-repository PASS inheritance: `forbidden`

* 오독 금지:

  * G1 terminal PASS를 모든 후속 repository HEAD의 full-gate PASS로 읽지 않는다.
  * focused / current-route / Lua / package validation PASS를 full-repository PASS로 자동 승격하지 않는다.
  * historical failure를 current scope 밖으로 분류했다는 이유만으로 full-suite PASS라고 쓰지 않는다.
  * clean-checkout PASS를 Registry Authority, RTC 또는 Publish Boundary PASS로 읽지 않는다.
  * COMMON-RUNTIME-SURFACE-NONMUTATION.
  * COMMON-RELEASE-NONDECISION.

* Predecessor trace:

  * 2026-07-28 initial Phase 0는 blocked였다.
  * append-only successor가 dedicated environment requirement를 충족해 Phase 0를 accepted로 전환했다.
  * 2026-08-01 G1은 exact tracked subject에서 disposable Run A/B를 결속해 terminal PASS를 기록했다.
  * 후속 refactor / optimization validation은 각각 자기 subject의 결과이며 G1 PASS를 새로운 HEAD로 자동 이전하지 않는다.
  * COMMON-EVIDENCE-TRACE.


### Iris — reusable public-text evaluator integration

* 날짜: 2026-08-01

* 상태: current readpoint / reusable evaluator integrated / authority effect none

* 결정: Iris의 public-text assessment는 특정 Naturalization attempt에 종속된 일회성 검증이 아니라 여러 subject가 재사용할 수 있는 generic no-write evaluator로 유지한다. evaluator 자체는 assessment evidence를 생성·검증할 뿐 public-text acceptance나 publication authority를 갖지 않는다.

* 현재 기준:

  * generic evaluator의 contract / runner / no-write validator는 reusable assessment capability의 required dependency로 관리한다.
  * evaluator implementation과 required dependencies는 current-route validation surface에 결속한다.
  * subject-specific assessment result는 generic evaluator의 영구 dependency와 분리한다.
  * downstream consumer가 기존 assessment result를 재사용할 때는 exact result identity를 결속하며 candidate 재생성이나 assessment 재계산 없이 소비할 수 있다.
  * generic evaluator PASS는 assessment contract 만족을 뜻하며 semantic acceptance / publication decision이 아니다.
  * evaluator integration이나 tooling-scope 변경은 current reviewed scope를 기준으로 한다.

* 최소 결과 trace:

  * reusable evaluator validation / integration: `PASS`
  * completion claim: `reusable_public_text_quality_evaluator_validated_and_integrated`
  * authority effect: `none`

* 오독 금지:

  * evaluator PASS를 Publish Boundary PASS나 public-text acceptance로 읽지 않는다.
  * evaluator integration을 DVF System, QG, IAR 또는 Publish Boundary responsibility 확장으로 읽지 않는다.
  * subject-specific result를 authority source로 자동 승격하지 않는다.
  * COMMON-RELEASE-NONDECISION.
  * COMMON-RUNTIME-SURFACE-NONMUTATION.

* Predecessor trace:

  * 2026-08-01 amended scope가 generic evaluator와 downstream result consumption을 current executable path에 추가했다.
  * G4가 evaluator를 live current-route에 integration했다.
  * predecessor tooling allowlist cap은 supersede됐다.
  * COMMON-EVIDENCE-TRACE.


### Iris Layer 3 Naturalization — implementation / quality assessment completion

* 날짜: 2026-08-01

* 상태: current readpoint / implementation and quality assessment complete / runtime adoption separate

* 결정: Naturalization implementation의 품질 평가는 preserved candidate에 대해 reusable public-text evaluator가 생성·검증한 exact assessment result를 no-write로 소비해 닫는다.

* 현재 기준:

  * Naturalization lifecycle은 2026-08-01 amended current executable scope를 기준으로 해석한다.
  * 최초 계획의 conflicting terminal / freeze / owner-seal / attempt-specific Publish 조항은 historical / non-executable이다.
  * G5는 exact assessment result를 identity-bound, no-write 방식으로 소비한다.
  * candidate를 재생성하거나 assessment를 새로 계산하지 않는다.
  * completion claim은 `naturalization_implementation_and_quality_assessment_complete`로 한정한다.
  * quality-assessment completion의 authority effect는 `none`이다.
  * current rendered/runtime adoption은 별도 adoption decision이 소유한다.

* 최소 결과 trace:

  * Naturalization implementation / quality assessment: `PASS`
  * assessment findings: `0`
  * candidate regeneration: `0`
  * authority effect: `none`

* 오독 금지:

  * Naturalization assessment PASS를 Publish Boundary acceptance로 읽지 않는다.
  * G5 completion을 runtime adoption이나 package identity completion으로 읽지 않는다.
  * 후속 runtime adoption 성공을 이용해 이 lifecycle이 package publication이나 release readiness를 승인했던 것으로 소급 해석하지 않는다.
  * COMMON-RELEASE-NONDECISION.
  * COMMON-RUNTIME-SURFACE-NONMUTATION.

* Predecessor trace:

  * original Naturalization plan의 attempt-specific terminal workflow는 amended scope에 의해 일부 historical화됐다.
  * G4 evaluator integration 뒤 G5가 exact result를 consumed했다.
  * 후속 runtime adoption은 이 G5-validated candidate를 별도 authority contract에서 소비했다.
  * COMMON-EVIDENCE-TRACE.


### Iris Artifact Registry — Layer 3 Naturalization runtime adoption / current package projection

* 날짜: 2026-08-01

* 상태: current readpoint / runtime adoption complete / current-runtime package projection identity PASS

* 결정: G5가 품질 검증한 exact Naturalization candidate를 current facts / input-manifest identity에 결속해 current rendered Layer 3 artifact와 Lua runtime payload로 채택한다. 같은 readpoint에서 current runtime payload의 package projection identity를 봉인하되 RTC certification과 package publication은 별도 axis로 유지한다.

* 현재 기준:

  * runtime adoption은 exact candidate와 current facts / input-manifest identity를 결속한 뒤 수행한다.
  * adoption은 candidate나 current facts를 source-authority 차원에서 다시 작성하지 않는다.
  * current generation은 rendered artifact, Lua chunk manifest, declared chunk set과 current generation descriptor를 하나의 transaction identity로 관리한다.
  * live adoption은 off-live generation / validation과 rollback proof를 거친 뒤 반영한다.
  * current generation descriptor는 adopted rendered / runtime payload identity의 current readpoint다.
  * package projection은 `current_runtime_payload`와 `rtc_certified_payload` applicability를 구분한다.
  * `current_runtime_payload` package는 current descriptor가 결속한 payload freshness와 identity를 검증한다.
  * RTC certification을 주장하는 package에만 별도 RTC evidence를 요구한다.
  * package applicability가 모호하면 artifact write 전에 fail-closed한다.
  * old monolith, stale bridge 또는 undeclared runtime entry를 current package fallback으로 허용하지 않는다.

* 최소 결과 trace:

  * Naturalization runtime adoption: `complete`
  * adopted public-text rows: `2084`
  * unadopted-without-text rows: `21`
  * current runtime payload: manifest + `11` chunks
  * current-runtime package identity: `PASS`

* 오독 금지:

  * runtime adoption completion을 source facts authority 재작성으로 읽지 않는다.
  * current-runtime package identity PASS를 RTC certification 또는 package publication으로 읽지 않는다.
  * candidate / rendered / runtime parity를 public-text acceptance나 Publish Boundary PASS로 읽지 않는다.
  * owner의 in-game observation을 IAR artifact-authority completion의 대체 근거로 사용하지 않는다.
  * COMMON-RELEASE-NONDECISION.

* Predecessor trace:

  * G5 quality-assessment lifecycle이 exact candidate를 검증했다.
  * runtime-adoption lifecycle은 그 candidate를 current rendered / Lua runtime payload에 채택했다.
  * full current-route Clean-Checkout와 owner in-game observation은 별도 validation axis로 기록됐다.
  * COMMON-EVIDENCE-TRACE.


### Iris — runtime API / compatibility boundary

* 날짜: 2026-08-03 → 2026-08-11 successor runtime refactors

* 상태: current readpoint / internal boundary refactor adopted / public compatibility preserved / Browser projection lifecycle explicit

* 결정: Iris의 public API와 기존 consumer compatibility를 유지하면서 Description, Browser, Detail, presentation과 legacy compatibility의 내부 책임을 분리한다. Browser row / ordering / cache는 명시적인 generation·locale lifecycle의 중립 presentation projection으로 관리한다.

* 현재 기준:

  * 지원되는 public API와 public `require` surface는 보존한다.
  * Description, Browser, Detail과 legacy compatibility는 서로 다른 internal responsibility boundary로 유지한다.
  * Description string output은 구조화된 internal representation에서 파생한다.
  * Browser 표시 순서, 대표 항목, folding, search와 variant projection은 taxonomy / classification 의미 authority와 분리된다.
  * Browser는 item index 뒤 generation-local row를 materialize할 수 있다.
  * classification 입력은 presentation에 필요한 최소 projection만 소비한다.
  * item object identity와 public copy-on-read 결과를 보존한다.
  * Browser / Wiki detail은 공통 read-only fact projection을 소비한다.
  * Browser search ordering source와 row/cache는 generation과 normalized locale에 귀속한다.
  * locale 변경 시 완성된 successor projection으로 교체하고 관련 derived cache를 함께 무효화한다.
  * cache와 ordering snapshot은 presentation optimization이며 semantic authority가 아니다.
  * legacy `IrisData`와 Browser variant compatibility는 compatibility boundary 뒤에 격리한다.
  * debug-only message / calculation은 caller-side debug enablement 뒤에서 수행한다.

* 영향:

  * internal representation을 최적화하면서도 public object identity와 copy semantics를 보존한다.

* 최소 결과 trace:

  * runtime/API internal boundary: `adopted`
  * Browser generation-local projection: `adopted`
  * generation / normalized-locale cache ownership: `adopted`
  * public compatibility: `preserved`

* 오독 금지:

  * Browser row / cache를 taxonomy authority나 source fact로 읽지 않는다.
  * classification 정보를 Browser가 소비한다는 사실을 classification authority 소유로 읽지 않는다.
  * instance-specific fact를 `fullType` 전역 사실로 승격하지 않는다.
  * internal cache refactor를 public compatibility 제거 승인으로 읽지 않는다.
  * COMMON-RELEASE-NONDECISION.
  * COMMON-RUNTIME-SURFACE-NONMUTATION.

* Predecessor trace:

  * 2026-08-03 refactor가 runtime/API boundary와 copy-on-read contract를 채택했다.
  * 2026-08-10 Browser eager build를 first-use 구조로 전환했다.
  * 2026-08-11 generation / locale projection-owner contract가 보강됐다.
  * 당시 deferred/no-op implementation 후보는 current policy가 아니다.
  * COMMON-EVIDENCE-TRACE.


### Iris Repository — durable / disposable artifact placement boundary

* 날짜: 2026-08-10 → successor repository-lightweighting readpoints

* 상태: current readpoint / role-based physical placement adopted / reconstructible representation adopted

* 결정: Iris Repository는 IAR가 분류한 artifact role과 실제 consumer / reconstruction requirement를 입력으로 받아 physical durability, compact representation, CAS / archive와 disposable placement를 결정한다. Physical placement는 artifact authority를 새로 정의하지 않는다.

* 현재 기준:

  * physical durability는 artifact role, consumer, historical reproduction requirement와 deterministic reconstruction 가능성을 기준으로 결정한다.
  * current authority / current-required evidence가 요구하는 durable identity는 보존한다.
  * historical consumer가 actual physical input을 요구하거나 deterministic reconstruction이 불가능하면 필요한 physical evidence를 보존한다.
  * exact reconstruction 가능한 duplicate / intermediate artifact는 compact representation, dictionary / delta, CAS, reference 또는 transparent resolver로 대체할 수 있다.
  * compact representation이 실제 절감을 만들지 않거나 consumer safety가 닫히지 않으면 migration을 defer한다.
  * dynamic consumer나 full-gate가 exact physical artifact를 요구하면 physical exception을 유지한다.
  * cold artifact는 deterministic archive와 verify / restore contract가 있을 때 repository 밖으로 이동할 수 있다.
  * execution scratch, temporary validation result와 regenerable projection은 disposable external work / result root에 둘 수 있다.
  * physical relocation, compaction 또는 deletion은 IAR authority role을 자동 변경하지 않는다.
  * Repository cleanup은 current authority / required evidence / historical reconstruction input 삭제 권한이 아니다.

* 영향:

  * authority semantics를 건드리지 않고 repository physical footprint와 duplicate representation을 줄일 수 있다.

* 최소 결과 trace:

  * role-based physical placement: `adopted`
  * reconstructible compact / CAS representation: `adopted`
  * deterministic cold archive: `adopted`
  * consumer-required physical exceptions: `supported`

* 오독 금지:

  * repository 안/밖 위치를 authority status로 읽지 않는다.
  * CAS / archive를 provenance 삭제로 읽지 않는다.
  * physical-byte 감소를 LLM token, PZ heap, latency 또는 FPS 개선으로 자동 환산하지 않는다.
  * historical cleanup을 historical denominator 축소로 확대하지 않는다.
  * COMMON-RELEASE-NONDECISION.

* Predecessor trace:

  * 2026-08-10 external scratch / generated projection boundary를 채택했다.
  * evidence-lightweighting successor가 compact representation, CAS / path reference와 deterministic cold archive를 채택했다.
  * 일부 current-required / dynamic-consumer artifact는 physical exception으로 유지됐다.
  * COMMON-EVIDENCE-TRACE.


### Iris runtime — lazy loading / compatibility facade boundary

* 날짜: 2026-08-10 → 2026-08-11 successor optimization

* 상태: current readpoint / lazy loading adopted / index integrity boundary refined / public compatibility preserved

* 결정: Iris runtime은 public compatibility facade를 유지하면서 Browser, Layer 3, UseCase와 정적 데이터의 불필요한 eager / full-dataset materialization을 실제 consumer의 first-use와 key-level lookup으로 지연한다. 각 lazy index는 자기 조회 계약에 필요한 validity를 독립적으로 유지하며 routing metadata를 semantic authority로 승격하지 않는다.

* 현재 기준:

  * Browser module surface와 supported public facade는 유지한다.
  * Browser 전체 build는 실제 Browser consumer의 first-use에서 materialize한다.
  * Layer 3와 UseCase lookup은 deterministic index / router를 이용해 필요한 key의 chunk만 demand-load한다.
  * boot 시 즉시 필요하지 않은 static information module은 compatibility contract를 보존하는 범위에서 first-use loading으로 이동할 수 있다.
  * normal lazy lookup miss와 malformed / inconsistent package / index / target identity를 구분한다.
  * 검증된 absent key는 corruption이나 full-facade fallback 조건이 아니다.
  * index는 routing / count metadata이며 semantic authority가 아니다.
  * UseCase ChunkIndex와 LineCountIndex는 first-use에서 validation state를 완성할 수 있다.
  * ChunkIndex validity와 LineCountIndex validity는 독립 state를 유지한다.
  * 두 index 사이 cross-check는 별도 consistency state로 관리한다.
  * `getLineCount()`는 유효한 LineCountIndex를 unrelated ChunkIndex failure 때문에 불필요하게 차단하지 않는다.
  * UseCase line-count 조회는 description body materialization과 분리한다.
  * internal optional field omission이나 compact representation은 public facade의 observable shape를 변경하지 않는다.

* 영향:

  * 개별 lookup의 정상 동작을 서로 무관한 index failure에 과도하게 결속하지 않으면서 lazy-loading integrity를 유지한다.

* 최소 결과 trace:

  * Browser first-use loading: `adopted`
  * Layer 3 / UseCase key-level loading: `adopted`
  * UseCase index first-use validation: `adopted`
  * ChunkIndex / LineCountIndex independent validity: `adopted`
  * public compatibility facade: `preserved`

* 오독 금지:

  * 하나의 index failure를 모든 lookup contract의 global invalidity로 자동 승격하지 않는다.
  * 정상 absent key를 index corruption으로 읽지 않는다.
  * index / cross-check / count metadata를 semantic authority로 읽지 않는다.
  * lazy initialization을 validation 생략으로 읽지 않는다.
  * demand-load 감소를 PZ heap, latency, FPS 또는 frame-time 향상으로 자동 승격하지 않는다.
  * COMMON-RELEASE-NONDECISION.

* Predecessor trace:

  * 2026-08-10 key-level chunk routing과 Tooltip line-count / description-body loading 분리를 채택했다.
  * 2026-08-11 absent-key와 routing corruption을 분리했다.
  * comprehensive follow-up에서 ChunkIndex / LineCountIndex 독립 validity contract를 보강했다.
  * COMMON-EVIDENCE-TRACE.


### Iris — capability hint / negative-evidence boundary

* 날짜: 2026-08-11

* 상태: current readpoint / closed-negative capability inference rejected

* 결정: item의 category / type / method availability 같은 구조적 신호는 확인된 capability의 positive hint로 사용할 수 있지만 충분한 closed-negative authority 없이 capability의 부재나 불가능성을 단정하는 negative authority로 사용하지 않는다.

* 현재 기준:

  * category / type은 capability 후보를 좁히는 positive hint로 사용할 수 있다.
  * category / type에 특정 값이 없다는 사실만으로 해당 capability가 없다고 판정하지 않는다.
  * custom item, contradictory field 조합, same-canonical hybrid와 external-mod variation을 보존할 수 없는 capability mask는 authoritative closed set으로 사용하지 않는다.
  * method / field presence가 item-instance fact인지 type-level structural hint인지 구분한다.
  * instance에서 관찰된 capability fact를 같은 `fullType`의 모든 instance에 자동 승격하지 않는다.
  * capability hint는 Browser / Detail optimization에 사용할 수 있지만 Evidence, classification 또는 source fact를 새로 생성하지 않는다.
  * closed-negative inference를 도입하려면 false-negative가 없음을 증명하는 별도 authority contract가 필요하다.

* 최소 결과 trace:

  * category / type positive-hint use: `allowed`
  * closed-negative authority: `not established`
  * authoritative capability mask: `not adopted`
  * instance fact → fullType promotion: `forbidden without evidence`

* 오독 금지:

  * positive hint를 confirmed capability fact와 동일시하지 않는다.
  * category / type mismatch를 capability 부재 증거로 자동 사용하지 않는다.
  * method-name 존재 자체를 semantic meaning의 완전한 증명으로 읽지 않는다.
  * optimization shortcut을 Evidence Allowlist나 runtime-side semantic inference 확대 근거로 사용하지 않는다.
  * COMMON-RUNTIME-SURFACE-NONMUTATION.

* Predecessor trace:

  * 2026-08-11 capability mask candidate는 closed-negative authority 부재로 no-op 처리됐다.
  * 후속 optimization은 instance scope capability hint 경계를 재확인했다.
  * COMMON-EVIDENCE-TRACE.


### Iris runtime — pure-Lua engine-object access boundary

* 날짜: 2026-08-11

* 상태: current readpoint / pure-Lua eligibility surface adopted / generic production routing not adopted

* 결정: Iris runtime의 engine-object access는 Project Zomboid가 Kahlua의 표준 Lua 환경에 이미 노출한 객체를 Lua에서 소비하는 범위로 한정한다. JVM / JAR / Mixin / 직접 Java bridge를 Iris runtime에 추가하지 않으며 공통 object-access helper는 검증된 pure-Lua eligibility surface로만 채택한다.

* 현재 기준:

  * Iris runtime 구현은 Lua surface 안에서 유지한다.
  * `engine-bound object`는 Iris가 자체 Java bridge를 여는 객체가 아니라 PZ가 Kahlua 표준 Lua API로 이미 노출한 engine object를 뜻한다.
  * ScriptManager / Java collection 계열처럼 Lua에 노출된 engine object의 method / self binding을 다루는 pure-Lua helper를 둘 수 있다.
  * `IrisObjectAccess.call0/call1`은 eligibility / compatibility helper이며 JVM integration layer가 아니다.
  * helper의 존재만으로 모든 engine-object invocation을 generic production routing으로 전환하지 않는다.
  * generic production routing을 채택하려면 representative PZ Kahlua engine-object에 대한 actual functional evidence가 필요하다.
  * representative evidence가 없는 branch는 `unvalidated_but_in_scope`로 유지하며 기존 production routing을 대체하지 않는다.
  * pure-Lua helper는 source / Evidence / classification을 생성하지 않는다.
  * object-access abstraction은 runtime mechanics이며 semantic authority가 아니다.

* 영향:

  * 반복되는 Kahlua object method-binding 처리를 공통 Lua helper로 정리할 수 있으면서도 Iris runtime의 Lua-only 경계를 유지한다.

* 최소 결과 trace:

  * pure-Lua object-access eligibility surface: `adopted`
  * JVM / JAR / Mixin / direct Java bridge: `not adopted`
  * generic production routing through new helper: `not adopted`
  * representative PZ engine-object functional evidence: `pending`

* 오독 금지:

  * Kahlua가 Java-backed object를 Lua에 노출한다는 사실을 Iris가 Java bridge / JVM component를 포함한다는 뜻으로 읽지 않는다.
  * `IrisObjectAccess`를 Java abstraction layer나 SPI implementation으로 읽지 않는다.
  * helper eligibility를 generic production-routing validation으로 승격하지 않는다.
  * unit / pure-Lua test만으로 representative PZ engine-object functional validation을 대체하지 않는다.
  * engine-object method availability를 item semantic capability의 완전한 증명으로 읽지 않는다.
  * COMMON-RELEASE-NONDECISION.

* Predecessor trace:

  * 2026-08-11 comprehensive optimization은 `IrisObjectAccess.call0/call1`을 pure-Lua eligibility surface로 추가했다.
  * representative PZ Kahlua engine-object functional evidence가 없어 generic production routing은 predecessor implementation을 유지했다.
  * 이 미검증 branch가 당시 optimization overall 상태를 `partial`로 제한했다.
  * COMMON-EVIDENCE-TRACE.

* Trace:

  * pure-Lua object-access eligibility adoption: 2026-08-11
  * generic engine-object production routing: pending explicit functional evidence
  * COMMON-EVIDENCE-TRACE.

---
## Frame

### Frame — PZ판 git형 팩 상태 버전 관리 레이어

* 상태: current readpoint / pre-ledger imported + 2026-03-25 refinement
* 결정: Frame은 `모드팩 관리자`, `문제 해결 도구`, `런처`, `설치기`, `devkit`가 아니라, **Project Zomboid 모드팩 상태를 기록·비교·되돌리는 버전 관리 레이어**로 둔다.
* 현재 기준:

  * Frame의 최소 관리 단위는 개별 모드가 아니라 **팩 상태(pack state)** 다.
  * Frame은 특정 시점의 모드 목록 / 순서 / 출처 / 설정 / 지문을 묶은 **환경 상태**를 1급 객체로 다룬다.
  * 제품 비유는 `CurseForge형 관리자`보다 **PZ판 git**에 가깝게 고정한다.
  * Frame은 월드/세이브 상태를 커버하지 않는다.
  * Frame은 성능 개입, 안정화, Lua 실행 제어, 런타임 정책 결정을 맡지 않는다.
  * Frame은 Fuse/Nerve와 기능적으로 엮이지 않는 **비런타임 모드팩 운영 레이어**로 둔다.
* 영향: Frame은 설치 전/운영 단계의 팩 구성·스냅샷·재현성 관리에 집중하고, 실제 실행 중 체감 변화나 안정화 개입은 Fuse/Nerve 같은 런타임 모듈의 책임으로 남긴다.
* Trace:

  * ledgered/imported: 2026-03-16 Frame 비정책 / 월드 비포함 원칙
  * ledgered/imported: 2026-03-17 Frame 비런타임 / 비안정화 원칙
  * refined: 2026-03-25 Frame은 PZ판 git 레이어 / 팩 상태 1급 객체 / 환경 상태 한정
  * COMMON-EVIDENCE-TRACE.

### Frame — 비정책 기록·비교·복원 원칙

* 상태: current readpoint
* 결정: Frame은 차이 표시와 상태 기록은 하되, **원인 지목 / 정답 추천 / 자동 해결 / 자동 정렬 / 문제 모드 지목**을 하지 않는다.
* 현재 기준:

  * Frame의 제품 가치는 `더 똑똑한 분석`이 아니라 **되돌림 가능한 기록**에 둔다.
  * UI와 문서는 판단보다 사실과 변화 표시를 우선한다.
  * Frame UI/문서/데이터는 `정상/비정상`, `원인/범인`, `권장/최적`, `해결/진단` 같은 판단 언어를 피한다.
  * 기본 언어는 `기준점`, `자동 저장`, `달라짐`, `비교`, `되돌리기`, `계속` 같은 **사실+행동 언어**로 둔다.
  * Frame은 진단 도구가 아니라 기록/복원 도구이며, 처방보다 복원, 진단보다 비교를 우선한다.
* 영향: Frame은 사용자가 상태 차이를 보고 되돌릴 수 있게 하지만, 어떤 모드가 문제인지 판단하거나 최적 상태를 추천하는 도구로 확장하지 않는다.
* Trace:

  * ledgered/imported: 2026-03-16 Frame 비정책 원칙
  * refined: 2026-03-25 Frame은 진단/추천 도구가 아니라 기록/복원 도구
  * refined: 2026-03-25 Frame의 언어는 사실+행동 언어
  * COMMON-EVIDENCE-TRACE.

### Frame — 스냅샷 / 자동 저장 / 설정 / 재현성 모델

* 상태: current readpoint
* 결정: Frame은 **수동 공식 스냅샷 + 자동 안전망 + 원본 보존/오버라이드 설정 + fingerprint 기반 동일성 확인**을 기본 운영 모델로 둔다.
* 현재 기준:

  * Frame의 공식 스냅샷은 수동으로 만든다.
  * 자동 스냅샷은 공식 기록과 같은 위상이 아니라, 복구와 회귀 추적을 위한 안전망으로만 둔다.
  * 자동 저장은 **5/10/30/60분 고정 주기 + 최근 10개 롤링 보관**을 기본으로 한다.
  * `변화 없으면 저장 생략` 같은 해석적 스킵은 기본 정책에서 배제한다.
  * 자동 저장은 공식 스냅샷과 역할은 다르지만, 기록 품질 자체가 낮은 임시 로그로 취급하지 않는다.
  * 설정은 직접 편집 UI보다 **원본 설정 보존 + 사용자 오버라이드 파일(내 설정)** 구조를 우선한다.
  * 설정 변경 UX는 `원본을 복사해 오버라이드 레이어를 만든 뒤 외부 편집기로 수정`하는 흐름을 기본으로 삼는다.
  * Frame 본체는 설정 편집기가 아니라 레이어 관리와 diff/restore에 집중한다.
  * Frame은 모드 원본 파일을 저장·배포하는 방식으로 완전 복원을 보장하지 않는다.
  * 재현성 모델은 **목록/순서/설정 재구성 + fingerprint 기반 동일성 확인**이다.
* 영향: Frame은 `그때의 상태를 다시 맞출 수 있는가`와 `지금 상태가 그때와 같은가`를 다루며, 모드 원본 자체를 보관·전달하는 시스템으로 확장하지 않는다.
* Trace:

  * refined: 2026-03-25 Frame 스냅샷의 위계는 수동 공식 기록 + 자동 안전망
  * refined: 2026-03-25 Frame 자동 저장은 고정 주기 안전망
  * refined: 2026-03-25 Frame 설정은 원본 보존 + 오버라이드 레이어
  * refined: 2026-03-25 Frame 재현성은 완전 복원이 아니라 재구성과 동일성 확인
  * COMMON-EVIDENCE-TRACE.

### Frame — 공유 포맷과 제품 경계

* 상태: current readpoint / external-tooling deferred
* 결정: Frame은 현재 메인라인에서 **모드 내부 레이어**로 남기고, 외부 공유 표준은 **ZIP + JSON**으로 둔다.
* 현재 기준:

  * Frame을 외부 런처/관리자 툴로 빼는 방향은 현재 메인라인으로 채택하지 않는다.
  * 외부 툴화는 장기 백로그 또는 후순위 옵션으로만 둔다.
  * 공개 공유 포맷은 열린 포맷인 **ZIP + JSON**을 기본으로 한다.
  * `.frame`을 공개 표준으로 강제하지 않는다.
  * 다만 import 단계의 보안/검증을 위해 ZIP을 내부 `.frame` 캐시로 변환하는 안은 유력한 내부 처리 전략으로 남긴다.
  * Frame은 기록·비교·복원 레이어를 넘어 런처, 설치기, 문제 진단기, 설정 에디터, devkit로 확장하지 않는다.
  * 팩 상태 기록/공유/복원과 직접 관련 없는 편의 기능은 기본적으로 Cortex나 별도 후순위 논의로 미룬다.
* 영향: 외부 공유는 열린 포맷을 유지하고, `.frame`은 필요할 때 내부 검증 캐시나 런타임 최적화 수단으로만 다룬다. Frame 본체는 상태 관리 경험에 집중한다.
* Non-decision:

  * 이 항목은 Frame의 즉시 외부 툴화, 공개 표준 `.frame` 강제, 런처/설치기/devkit 전환, 문제 진단기화를 승인한 것이 아니다.
* Trace:

  * refined: 2026-03-25 Frame 외부 툴화는 메인라인이 아님
  * refined: 2026-03-25 Frame 공개 공유 포맷은 ZIP+JSON, `.frame`은 내부 캐시 후보
  * refined: 2026-03-25 Frame은 런처/설치기/devkit로 키우지 않음
  * COMMON-EVIDENCE-TRACE.

---
## Canvas

### Canvas — 리소스팩 별도 제품 축 / 검증·비교·설명 플랫폼

* 상태: current readpoint / pre-ledger imported + 2026-03-25 refinement
* 결정: 리소스팩 축은 Pulse의 핵심 킬러축이나 Frame의 하위 기능이 아니라, 진행한다면 처음부터 **Canvas**로 시작하는 **생태계 확장용 별도 제품 축**으로 둔다.
* 현재 기준:

  * Canvas는 리소스 제작 툴이 아니다.
  * Canvas는 Photoshop, GIMP, Blender, TileZed 같은 외부 제작 툴을 대체하지 않는다.
  * Canvas는 외부 툴이 만든 리소스팩 산출물을 읽어 **최종 적용 상태 / 충돌 / 배포 불일치**를 검증·비교·설명하는 플랫폼이다.
  * 주요 작업은 인덱싱, 최종 상태 계산, 충돌 분석, 구조/경로/ID/패킹 검증, 프리플라이트 검증, 로컬↔산출물 비교, 서버↔클라 비교, 설명형 리포트다.
  * 리소스팩 축을 진행한다면 `Cortex에서 임시 운영 후 이관` 같은 경로를 쓰지 않고 처음부터 Canvas로 시작한다.
  * 시작하지 않기로 결정하면 해당 축은 보류가 아니라 Pulse 생태계에서 제거한 것으로 본다.
* Pain point:

  * 최종 적용 결과 / 충돌 / 로드 순서 가시성 부족
  * 패킹 / 경로 / 구조 / ID 민감성으로 인한 제작 붕괴
  * 버전 / 서버 / 배포 불일치
* 영향: Frame과 Pulse의 핵심 서사는 계속 `모드팩 상태 기록·복원`에 두고, 리소스팩 검증/비교/설명은 Canvas 독립 축으로 다룬다.
* Non-decision:

  * 이 항목은 Canvas를 제작 툴, 리소스 편집기, Pulse 핵심 킬러축, Cortex 임시 수용 축으로 승인한 것이 아니다.
* Trace:

  * ledgered/imported: 2026-03-16 Canvas 정체성 / 초기 진입 경로
  * refined: 2026-03-25 리소스팩 축은 Pulse 핵심축이 아니라 별도 제품 축
  * refined: 2026-03-25 Canvas는 제작 툴이 아니라 검증·비교·설명 플랫폼
  * refined: 2026-03-25 Canvas의 pain point는 적용 결과, 제작 안전, 배포 불일치
  * COMMON-EVIDENCE-TRACE.

### Canvas / Frame — 협력 가능하지만 통합 제품으로 설계하지 않는다

* 상태: current readpoint
* 결정: Canvas와 Frame은 함께 쓰일 수 있어도, 처음부터 하나의 통합 제품처럼 설계하지 않는다.
* 현재 기준:

  * Frame은 **모드팩 상태**를 다룬다.
  * Canvas는 **리소스 적용 상태**를 다룬다.
  * Frame은 시간축 / 스냅샷 / 롤백 중심으로 발전시킨다.
  * Canvas는 리소스팩 최종 상태 검증 / 비교 / 설명 중심으로 발전시킨다.
  * 두 모듈의 협력은 느슨한 연동 수준에 그치며, 서로의 정체성을 흡수하지 않는다.
* 영향: Frame은 팩 상태 버전 관리 레이어로, Canvas는 리소스 적용 상태 검증 플랫폼으로 분리해 읽는다.
* Non-decision:

  * 이 항목은 Frame+Canvas 통합 제품화, Frame의 리소스팩 검증 흡수, Canvas의 모드팩 상태 관리 흡수를 승인한 것이 아니다.
* Trace:

  * refined: 2026-03-25 Canvas와 Frame은 협력하되 통합 설계를 피함
  * COMMON-EVIDENCE-TRACE.

### Canvas — 공개 포맷과 내부 정규화 번들

* 상태: current readpoint
* 결정: Canvas의 외부 공유 기본값은 **ZIP + JSON(+ .pack)** 으로 두고, `.canvas`를 외부 공개 표준으로 강제하지 않는다.
* 현재 기준:

  * Canvas는 열린 입력·공유 포맷을 유지한다.
  * `.canvas`는 공개 표준이 아니라 내부 정규화 캐시 또는 분석 번들 후보로만 둔다.
  * 내부 검증·캐시 전략은 Canvas 독자 구조로 발전시킬 수 있다.
* 영향: 외부 공유는 접근 가능한 열린 포맷을 유지하고, 내부 처리에서는 필요 시 `.canvas`를 정규화 캐시·분석 번들로 사용할 수 있다.
* Non-decision:

  * 이 항목은 `.canvas` 공개 표준 강제, 폐쇄형 공유 포맷 전환, 외부 툴 산출물 직접 편집 기능을 승인한 것이 아니다.
* Trace:

  * refined: 2026-03-25 Canvas 공개 포맷은 ZIP+JSON(+.pack), `.canvas`는 내부 정규화 번들 후보
  * COMMON-EVIDENCE-TRACE.

---

## Iris codebase optimization comprehensive follow-up — structural adoption / partial closeout

* 상태: 2026-08-11 implementation complete / terminal current validation PASS / Codex Reviewer `APPROVE` (P0/P1/P2/P3 `0`) / overall `partial`
* 결정:

  * Browser는 item index 뒤 generation-local row를 한 번 materialize한다. classification 입력은 private `StaticData` scope에서 scalar tag로만 소비하고, bucket과 검색/variant projection은 backing tag array를 보존하지 않는다. item object identity와 public copy-on-read 결과는 유지한다.
  * 검색의 정렬 source와 row map은 `(generation, normalizedLocale)` owner를 갖는다. locale mismatch에서는 완성된 candidate row map과 전역 정렬 snapshot을 교체하고 prefix/display-group/folded-count 파생 cache를 함께 무효화한다. prefix query마다 다시 정렬하지 않는다.
  * Item Detail method-name 목록은 module constant이며 capability hint는 item마다 한 번만 계산한다. instance fact를 fullType 전역 cache로 승격하지 않는다.
  * `IrisObjectAccess.call0/call1`은 pure-Lua eligibility surface로만 추가한다. Iris는 JVM/JAR/Mixin/직접 Java bridge를 포함하지 않으며, 여기서 engine-bound란 PZ가 Kahlua의 표준 Lua API에 노출한 ScriptManager·Java collection 계열 객체의 method/self binding을 뜻한다. representative PZ Kahlua engine-object functional evidence가 없으므로 generic production routing은 predecessor 구현을 유지한다. 이 branch는 `unvalidated_but_in_scope`이며 overall 상태를 `partial`로 제한한다.
  * dynamic DEBUG message는 caller-side enablement guard 뒤에서만 구성한다. Alt display-line cache는 fullType마다 현재 locale/revision 한 entry만 보존한다.
  * UseCase ChunkIndex/LineCountIndex는 module require 시 적재하지 않는다. 첫 `get()` 또는 `getLineCount()`가 두 index를 self-validate하고 독립 state와 cross-check state를 완성한 뒤 atomic publish한다. `getLineCount()`는 valid LineCountIndex와 non-invalid cross-check이면 malformed/missing ChunkIndex와 독립적으로 정상 count 또는 `0, nil`을 반환한다.
* 조건부 분기:

  * cache-owner census의 session-dependent candidate는 0이므로 production session reset wiring은 diff 0의 `complete/no-op`이다.
  * legacy IrisData compact candidate는 `75,143 -> 40,470` bytes를 보였지만 checkout 밖 clean source/package transaction의 exact in-scope path가 없어 live source 승격 없이 `deferred_by_design`이다.
  * Tooltip static projection은 PZ first-use timing과 generator admission 부재로 deferred다. item 비보존, Alt LRU/derived-key, generated compact adapter, Recipe Set, Python I/O cache, lifecycle/CAS는 각 materiality/safety gate에서 no-op이다.
* Token/context 측정:

  * base commit `5b19a5fa58cb883f6b27f433371434a85b41ba0d`와 current overlay를 EOL-normalized text로 비교했다. 변경된 production Lua 15개는 `108,545 -> 126,012` bytes(`+16.09%`), lexical units `14,492 -> 16,408`(`+13.22%`)다.
  * input plan을 제외한 구현 표면 45개는 `673,495 -> 773,605` bytes(`+14.86%`), lexical units `128,456 -> 141,164`(`+9.89%`)다. 동일 context 예산의 수용량 proxy는 production 기준 약 `11.68~13.86%`, 전체 구현 표면 기준 약 `9.00~12.94%` 감소했다.
  * 따라서 이번 follow-up의 채택 성과는 runtime 반복 순회·정렬·임시 allocation 경량화이지 repository/LLM-token 경량화가 아니다. 승인 가능한 token 효율 증가율은 `0%`이며 source proxy상 약 `9~14%` 악화다. legacy compact 후보의 `46.14%` byte 절감은 미채택이므로 current token 성과에 포함하지 않는다.
* Non-decision:

  * 이 결정은 PZ latency, heap, FPS/frame-time, release/Workshop/multiplayer/long-session 성능 향상을 주장하지 않는다.
  * tokenizer와 실제 Codex prompt selection/cache telemetry가 없으므로 byte/lexical proxy를 특정 GPT/Codex tokenizer의 exact token count나 실제 세션 비용으로 승격하지 않는다.
  * 사전 owner 승인은 destructive/conditional disposition을 진행할 권한이며, 실제 PZ functional 또는 timing evidence를 합성하지 않는다.
* Evidence: `Iris/_docs/refactor/codebase_optimization_followup/`의 baseline/census/disposition/validation/closeout receipts.
* 검증: focused `64 passed + 13 subtests`, exact current `219 passed`, configured current `486 passed / 1 N/A skipped / 504 deselected / 112 subtests`, Lua syntax `103 files`가 모두 exit `0`이다. Configured full advisory는 repository-only boundary 때문에 실행하지 않았고 PASS를 주장하지 않는다.

---

## Iris test precision-preserving lightweighting — terminal closeout supersession / scoped complete

* 상태: 2026-08-13 terminal machine closeout complete / governance ledger current
* 결정:

  * 기존 `blocked_before_terminal_validation` 기록은 당시 사실을 보존하는 predecessor trace로 유지하고 소급 수정하지 않는다.
  * terminal validation authority는 commit `730849134400311a2fa10588c9adb58a8bd037e0`, tree `99dead8b472fe4a8fa6cf8288c9676db287a75de`인 `S_terminal`이다. 이 subject에서 A1 감축 조건, precision과 fault contract를 보존한 채 focused, exact-current, configured-current, historical, diagnostic/all Run A/B와 tracked full-gate Run A/B가 통과했다.
  * Codex Reviewer의 독립 검토는 exact terminal subject에 대해 `PASS`, `P0=P1=P2=P3=0`이며 source/config 수정 요구가 없다. Owner seal은 사용자가 실행 요청에서 미리 부여한 owner 승인에 따라 machine manifest와 review를 결속한다.
  * evidence-only carrier는 commit `07b26f1bae394f4f7e08f51ad1bbb312dbc3a491`, tree `e3a749ba3ec76b5dd5f32347c12081c0cfa97bdb`이다. 유일한 parent는 `S_terminal`이고 delta는 carrier-aware-v2 pointer와 allowed-delta manifest 두 파일의 추가뿐이다. Carrier는 code/test/config, command 또는 denominator authority가 아니며 새 terminal validation subject가 아니다.
  * owner-managed durable bundle의 retrieval key는 `iris-test-precision-lightweighting-20260812-01`이다. External closeout receipt SHA-256은 `565831996175aa630258907f4e0f7275516b39c238edbb23f345ee474ae44f34`, fresh-root retrieval report SHA-256은 `4f65f3265af0136e5f96414de0df923cf6e59de957cbfc631380d2a4cc6ddec7`, fresh-root terminal replay receipt SHA-256은 `6d5a1efa0680ee5f1040e9620f6773eec5784c2103fb910fa9000469320287a8`이다.
  * fresh-root retrieval은 `carrier -> pointer -> external bundle -> S_terminal` DAG, single-parent/one-generation 관계와 exact two-file carrier delta를 검증했다. 이어진 replay는 `S_terminal`에서 12개 collection/execution 단계를 모두 exit `0`으로 완료했고 source checkout은 clean이었다. 사용자 원본 worktree pre/post inventory는 59개 항목으로 동일해 `user_worktree_delta=0`이다.
* Authority boundary:

  * 이 docs-only governance successor는 `S_terminal`의 machine PASS를 자신의 PASS로 상속하거나 새 terminal subject를 만들지 않는다. Terminal 결과 authority는 외부 durable bundle과 carrier pointer에 있다.
  * predecessor evidence, 실패 candidate와 기존 blocked 기록은 additive trace로 보존한다.
* Non-decision:

  * 이 closeout은 Iris 전체 runtime correctness, multiplayer/long-session 안정성, FPS/frame time/heap/latency 개선, release/Workshop/B42 readiness 또는 unrelated validation infrastructure 전체의 건전성을 의미하지 않는다.
  * declared detection scope 밖의 관측되지 않은 dynamic dependency 가능성을 배제하지 않는다.
* Evidence: `Iris/_docs/refactor/test_precision_lightweighting/terminal_closeout_recovery/{terminal_evidence_pointer.json,closeout_carrier_manifest.json}` 및 owner-managed external durable bundle retrieval key `iris-test-precision-lightweighting-20260812-01`.

---

## Iris test workflow consolidation — successor direction adopted / implementation pending

* 상태: 2026-08-13 architecture direction adopted / implementation and timing validation pending
* 결정:

  * 완료된 precision-preserving lightweighting은 테스트 보호 책임과 감축 판정 기반을 만들고 configured node `646 -> 645`, 중복 executed scenario `-1`, test-support LOC `27,709 -> 27,619`, 500+ LOC test file `10 -> 9`, 1,000+ LOC test file `2 -> 1`, 100+ LOC test method `22 -> 20`을 달성한 구조 정리로 해석한다.
  * 이 결과를 실행시간 개선으로 해석하지 않는다. Accepted before/after timing baseline이 없고 해당 계획은 execution-time improvement를 non-claim으로 두었으므로 현재 승인된 테스트 속도 개선 수치는 없다.
  * 후속 경량화의 우선 전략은 비슷한 assertion을 한 함수에 붙이는 단순 node 병합이 아니라, 같은 비싼 producer/workflow를 반복 실행하는 테스트를 contract family 또는 lifecycle 단위로 통합하는 것이다.
  * 하나의 producer 실행 결과를 A/B/C/D checkpoint가 읽고 E가 종합하는 관계라면 producer, repository materialization, subprocess와 immutable input preparation은 한 번만 수행하고 각 checkpoint 및 종합 관계를 같은 workflow test에서 검증한다.
  * 테스트 간 실행 순서 의존성이나 이전 test의 mutable output 재사용은 도입하지 않는다. 공유 대상은 immutable baseline 또는 명시적인 workflow state/result이며, 파괴·오염·crash/recovery·standalone-process semantics를 검증하는 case는 격리한다.
  * 통합 후에도 `subTest` 또는 동등한 named checkpoint를 사용해 어느 contract/failure condition이 실패했는지 보존한다. Node 수 감소만을 위해 failure localization, fail-closed path, required-validation identity 또는 standalone CLI boundary를 숨기지 않는다.
  * 후속 완료 판정은 node/LOC뿐 아니라 동일 환경의 before/after wall time, subprocess spawn count, temporary workspace/materialization count, copied bytes와 expensive producer invocation count의 실제 순감소를 요구한다.
* 후보 근거:

  * current test surface에는 subprocess 호출 지점, temporary-directory 생성과 tree-copy orchestration이 넓게 분포하며 반복 producer 통합 가능성이 있다.
  * `PublicTextQualityAcceptanceCurrentRouteTest._phase7_self_test()`는 동일 self-test producer를 여러 test가 다시 실행한 뒤 서로 다른 result case만 읽는 명시적 우선 후보다.
  * runtime payload, artifact lifecycle, registry authority 계열은 단계별 artifact와 final aggregation 관계를 가지므로 lifecycle integration 후보지만 mutable negative fixture와 recovery case의 격리 필요성을 먼저 판정해야 한다.
* Non-decision:

  * 이번 완료는 644개 Iris test 전체가 통합됐거나 전체 wall time이 75% 감소했다는 뜻이 아니다. 확정된 구조 개선은 pilot family의 producer invocation `4 -> 1`이며 repository-wide 시간 개선률은 accepted paired timing으로 봉인되지 않았다.
  * 기존 sealed precision-lightweighting terminal authority, source denominator, fresh-process semantics 또는 mutation isolation을 축소하지 않는다.
  * 이 결정은 특정 테스트의 즉시 병합·삭제, 목표 감축률, 예상 시간 개선률 또는 전체 suite PASS를 선언하지 않는다.
  * 서로 다른 입력 상태나 fresh-process 동작을 요구하는 테스트를 하나의 mutable workspace에 강제로 합치는 것을 승인하지 않는다.
  * 기존 round-scoped evidence tooling은 current claim의 재현 책임을 대체하는 successor evidence와 removal impact가 확정되기 전에는 자동 삭제하지 않는다.
* Evidence: `Iris/_docs/refactor/test_workflow_consolidation/`, `Iris/validation/baseline_admission/evidence/workflow_consolidation_reapplication_handoff.json`, implementation branch closeout `492ab29d`.

## Iris DVF 3-3 — Stateful Artifact Registry retirement successor disposition

* 상태: 2026-08-20 `FULL_RETIREMENT` / Layer 1–5 active product IAR consumers `0` / implementation and package validation complete
* 결정:

  * 제품 generation identity는 여섯 compose input과 이미 채택된 upstream content candidate의 raw bytes, generator/serializer/chunking identity, ordered output universe에서 파생한다. Current rendered/runtime/descriptor는 generation input으로 읽지 않는다. Descriptor는 authority/adoption token이 아니며 attempt, transaction, nonce, receipt, owner seal, absolute path와 wall-clock time을 포함하지 않는다.
  * R2 owner decision은 B다. Runtime public module `Iris/Data/IrisLayer3DataChunks`는 유지하고 generation-qualified immutable module set을 먼저 설치한 뒤 `IrisLayer3DataCurrent.lua` 한 파일만 visibility pointer로 교체한다. Stable facade와 chunk index는 같은 pointer를 소비한다.
  * `generation_key_identity_validation`은 exact key, ASCII-lower collision, rendered/runtime payload projection을 검증하는 stateless product claim이다. 기존 `Registry Runtime Compatibility PASS`, source authority, Publish, package/release readiness 또는 owner seal을 뜻하지 않는다.
  * `current_runtime_payload` package는 R2-B pointer가 가리키는 generation root의 stateless descriptor와 raw-byte universe만 소비한다. Legacy stateful descriptor fallback은 제거됐으며 pointer 부재·오염은 fail-closed한다.
  * Lookup package identity의 key ordering은 `[System.StringComparer]::Ordinal`로 고정한다. Windows PowerShell 5.1과 PowerShell 7의 culture-sensitive `Sort-Object` 차이가 같은 exact-key universe에서 서로 다른 digest를 만들 수 있으므로 package identity는 shell culture나 hash-set enumeration order에 의존하지 않는다.
  * 기존 sealed attempts, RTC bundle, source correction/cutover evidence와 repository-validation receipts는 수정하거나 삭제하지 않는다. Product retirement는 repository governance 또는 RTC history retirement가 아니다.
* 완료 근거:

  * clean-checkout full repository gate Run A/B와 deterministic compare는 subject `c924349eae6ee7f2a077ca83899b0ec99131f6c2`에서 exit `0`으로 완료됐다.
  * Codex Reviewer는 current-runtime package lookup identity 불일치 P1을 발견했다. 실제 원인은 stale manifest 자체가 아니라 PowerShell별 정렬 차이였으며 terminal implementation subject `6f362b5e284d9f05749c7f9dc6a11f13bb1fe322`에서 ordinal ordering과 identity를 함께 교정했다. Windows PowerShell 5.1/PowerShell 7 digest 일치와 계획된 `current_runtime_payload` ZIP package command exit `0`을 확인했고 남은 actionable finding은 `0`이다.
  * protected current install과 stateful product consumer 제거는 완료했다. Manual in-game QA는 `PASS_OWNER_ATTESTED`다. Inactive predecessor generation은 active product dependency가 아니라 bounded rollback target으로 보존하며 cleanup은 별도 post-closeout action이다.
  * 현재 RTC alignment `stale_requires_successor_rtc`는 유지한다.
  * terminal closeout carrier는 `5ce69e2a3bbf02d453e874af740a312e37b74bff`, main merge는 `a55a2999`, current main readpoint는 `c91d8f79`다.
* Non-decision:

  * `FULL_RETIREMENT`는 제품 Layer 1–5의 active IAR lifecycle dependency가 0이라는 뜻이다. RTC PASS, Publish PASS, release/Workshop/deployment, owner seal 또는 canonical sealed closure를 선언하지 않는다.
  * `switch_atomicity=observed_only`를 filesystem-level atomicity proof나 무조건적인 mixing-impossibility theorem으로 승격하지 않는다.
* Evidence: `Iris/_docs/round3/iar_stateful_architecture_retirement/{closeout.json,residual_report.json,codex_reviewer_final.json}`.

---

## Iris test scenario execution consolidation — four-group adoption / canonical closeout complete

* 상태: 2026-08-20 implementation complete / canonical Run A·B PASS / deterministic comparator PASS / Codex Reviewer `APPROVED` (P0/P1/P2/P3 `0`)
* 결정:

  * 비용 경량화의 단위는 test node 삭제가 아니라 같은 canonical input에서 반복되던 비싼 producer다. Artifact inventory Git seed, registry COMMON compile, registry Round 3 runner compile, artifact promotion Git seed의 네 독립 group을 채택했다.
  * 네 group은 40개 unique consumer node와 55개 concrete node/subcase identity를 포괄한다. Named checkpoint와 case/subTest mapping을 유지해 identity와 failure attribution을 `55 -> 55`로 보존했다.
  * 공유 경계는 immutable source/seed preparation까지만 허용한다. Mutation, tamper, rollback, recovery, lock/journal/backup, concurrency와 fresh-process 의미는 case-local clone, namespace 또는 process에서 유지한다. 공유 준비가 실패해도 각 consumer가 원래 예외 class와 message를 새 exception으로 다시 관측한다.
  * Git/compile producer의 consolidatable invocation은 `73 -> 6`(`91.78%`)이다. Clone/configuration 등 공개된 부대 호출을 포함한 heterogeneous total은 `187 -> 126`(`32.62%`)이다. 후자는 서로 다른 invocation signature의 구조적 합계이므로 wall-time proxy로 승격하지 않는다.
  * full gate가 추적 test source를 빠짐없이 분류하도록 기존 미분류 workflow source 10개를 exact-path `dedicated_route_validation`에 결속했다. 결과는 unclassified `10 -> 0`, multiple classification `0`, absent policy entry `0`이며 configured denominator와 node identity를 바꾸지 않는다.
  * 결합 validation subject `ea94c19789fd33799180c4cbf1e19bde26a3a482`에서 canonical Run A와 B가 각각 `424 passed / 0 failed / 2 deselected / 102 subtests passed`, standalone `4/4 PASS`로 종료했고 deterministic comparator가 동일 결과를 확인했다. Required dependency inventory는 `63 sources / 40 paths`, source checkout mutation과 sealed-artifact mismatch는 `0`이다.
  * main의 문서 정합화 readpoint는 `eaafed519afb7cd038af3d09443581957b3b478c`다. 이전 `991414ba` preflight failure는 당시의 historical evidence로만 보존하고 current PASS authority로 재사용하지 않는다.
* 완료 경계:

  * 이번 계획의 구현, isolation, identity, source classification, denominator, dependency inventory, canonical reproducibility와 reviewer 축은 complete다. 추가로 안전하면서 비용 양수인 evidence-qualified consolidation 후보는 현재 조사 범위에서 소진됐다.
  * configured/full-gate의 비교 가능한 before/after wall-time baseline은 없다. 따라서 suite 전체 속도 개선률, removable cost, PZ runtime 성능 또는 release/Workshop readiness는 결정하지 않는다.
* Evidence: `Iris/_docs/refactor/test_scenario_execution_consolidation/{candidate_ledger.json,identity_map.jsonl,final_summary.json,closeout.md}` 및 clean-checkout authority/evidence successor `0012`와 append-only correction `0013`.

---

## Iris — one-off item-page information sufficiency assessment

* 상태: 2026-08-21 평가 완료
* 결정:

  * current vanilla 2,285개 FullType에 대한 일회성 정보 충분성 평가 결과를 보존한다.
  * 결과 분포는 `information_sufficient=2081`, `evidence_limited=180`, `known_information_missing=2`, `unresolved=22`다.
  * 이 평가를 위해 사용한 임시 evaluator, validator와 fixture는 Iris의 정규 검사기나 제품 아키텍처로 채택하지 않는다.
  * current route, current authority, active core closure와 기존 회귀 테스트에는 이 평가를 등록하지 않는다.
  * Iris runtime, public text와 package에는 변경이 없다.
* Evidence: `Iris/build/description/v2/output/item_page_information_sufficiency/` 및 `docs/iris_item_page_information_sufficiency_walkthrough.md`.

---

## Iris Layer 3 — optional body role realignment, role-material staging and current installation

* 상태: 2026-08-21 staging closeout complete / Change 9 current installation complete
* 결정:

  * Layer 3는 모든 item에 강제되는 상세 설명이 아니라, 확인된 description-eligible material이 있을 때 제공하는 선택적 overview/explanation 계층이다. 근거가 부족하면 identity, classification, acquisition, Layer 4 또는 rendered prose에서 의미를 보충하지 않고 침묵한다.
  * 모든 current existing body는 `keep/reduce/revise/hide/review_hold` 중 하나를, 모든 canonical FullType은 body 유무와 독립적으로 `description_ready/acquisition_only/omission_allowed/insufficient_material/review_required` 중 하나를 갖는다.
  * fact kind는 exact source slot/provenance와 registered structured lineage로만 결정한다. `cluster_summary`는 matching adopted Layer 3 decision lineage가 있을 때만 role material이 되며 new Layer 4 promotion과 rendered-string semantic parsing은 금지한다.
  * canonical staging material은 `core_description`과 `acquisition_information`을 분리한다. Source-bound acquisition conservation과 Menu public acquisition coverage는 다른 set이다. Initial Menu branch는 `preserve_current_publicity`이고 Tooltip은 role-labeled input readiness까지만 다룬다.
  * 보존된 Item-Page Information Sufficiency 결과는 authority effect와 regular-gate role이 없는 one-off snapshot이다. Exact current snapshot일 때 per-item Layer 3 axes만 readiness prerequisite에 보조적으로 사용할 수 있고 top-level page disposition, Layer 4 axes 또는 gap inventory를 body disposition/readiness/Problem 5A로 직접 변환하지 않는다.
  * staging runner와 validator는 dedicated off-live route다. Existing compose entrypoint와 reusable public-text evaluator는 변경하지 않으며 Stateful Artifact Registry lifecycle/receipt/PASS를 복원하지 않는다.
  * staging focused test와 candidate replay는 mandatory repository validation을 대신하지 않는다. Exact terminal subject `1197ccc99085666d336e3ed493555e26810104e5` / tree `da2bf2e5ec595b8de1ea41ee2fafb7e433c058db`가 full-repository Clean-Checkout Run A/B와 deterministic comparison을 exit `0`으로 통과한 경우에만 staging closeout을 선언한다.
  * Run A/B result identity는 validated terminal subject에 역으로 넣지 않는다. `clean_checkout_result_pointer.json`은 post-validation evidence-only successor이며 terminal subject를 재정의하거나 자신의 machine PASS로 상속하지 않는다.
  * 이 범위의 완료 token은 `layer3_role_realign_staging_complete`다. 이는 disposition/readiness, role-material separation, deterministic staging successor, Problem 5A handoff, Menu candidate, Tooltip input readiness와 exact terminal repository validation까지만 의미한다.
  * Staging closeout 뒤 별도 owner authorization에 따라 Change 9를 실행했다. Exact staging successor를 `approved_upstream/candidate_rendered.json`으로 raw-byte 승격하고, 기존 six-file compose input과 합쳐 canonical generation input을 정확히 7개로 유지한다. Authorization과 installer lifecycle state는 generation input이 아니다.
  * Official complete-generation route가 immutable generation `dvf33-aa138aa4896b68ac53609a4b1cb6e5346245e74f544db28eb2ee924dc7b3e814`를 생성·검증했다. Installer는 시작 시 predecessor `dvf33-2a44a0a8d9a2e7f0d9a533ad002b7f691c1bfccec9577fb3356967ec6fd8a00c`를 다시 읽어 결속하고 current pointer를 한 번 전환했다. Predecessor는 inactive rollback generation으로 보존하며 same-generation reinstall은 protected mutation `0`, visibility switch `0`의 no-op이다.
  * `current_runtime_payload`는 새 generation과 lookup identity `lookup-f088127352730047`을 검증한다. Ordinal source digest는 Windows PowerShell 5.1과 PowerShell 7에서 동일하고 package hash mismatch는 `0`이다. 이는 RTC certification이나 package publication을 뜻하지 않는다.
  * Install terminal subject `d006f6108093886751e538d36c92de3627a9e76f` / tree `5e2370f8e5720e830b8ef62c87b6c51c45bfaa4a`는 focused regression, Lua syntax, package parity와 fresh full-repository Clean-Checkout Run A/B 및 deterministic comparison을 모두 exit `0`으로 통과했다. 이 별도 완료 token은 `layer3_role_realign_current_install_complete`다.
  * Install terminal source census에서 이미 tracked된 Layer 4 adaptive-presentation/runtime-projection test source는 기존 interaction-presentation test와 같은 dedicated focused route로 분류한다. 이 분류와 adoption binding 갱신은 current full-gate denominator `433`을 늘리거나 Layer 4 product semantics를 변경하지 않는다.
  * Current generation 전환으로 predecessor generation에 결속된 one-off IPS snapshot은 `predecessor_snapshot_stale_after_install`이다. 제거된 evaluator를 복원·재실행하지 않고 predecessor 결과를 current sufficiency claim으로 상속하지 않는다.
* Non-decision:

  * Tooltip UI/line allocation, RTC, Publish, release/Workshop/deployment 또는 Problem 5A enrichment를 완료로 결정하지 않는다.
  * Staging candidate completion 자체를 current mutation으로 읽지 않는다. Current mutation은 별도 Change 9 authorization, official installer와 install-subject validation에 의해서만 성립한다.
  * `layer3_role_realign_current_install_complete`는 Publish PASS, RTC, release/Workshop/deployment readiness 또는 owner-sealed canonical closure가 아니다.
* Evidence: `docs/iris_layer3_body_role_realignment_policy.md`, `docs/iris_layer3_body_role_realignment_walkthrough.md`, `Iris/build/description/v2/data/layer3_body_role_realign/`, `Iris/_docs/round3/layer3_body_role_realign/17789343f34bfc013d71460118819369913f85a073f319e93335c614cacaa200/axis_qualified_closeout.json`, `Iris/_docs/round3/layer3_body_role_realign/evidence_carriers/1197ccc99085666d336e3ed493555e26810104e5/clean_checkout_result_pointer.json`, `Iris/_docs/round3/layer3_body_role_realign/current_install/ips_predecessor_snapshot_disposition.json`, `Iris/_docs/round3/layer3_body_role_realign/current_install/current_install_closeout.json`.

---

### Iris — Layer 4 adaptive presentation and Layer 2–3 locale projection

* 상태: 2026-08-21 implementation complete / main integrated / owner in-game acceptance complete
* 결정:

  * Layer 4는 status-bearing interaction state를 단일 detail ViewModel 경계로 전달하고, presentation projection과 UI state를 분리한다. 단일·소규모·고밀도 row를 적응형으로 표시하며 고밀도 항목은 compact/full 전환과 검색을 제공한다.
  * Recipe와 Right-click은 독립된 동등 surface다. Recipe row의 제작 UI 이동, item 전환 시 상태 초기화, 기존 context menu/Wiki/Alt Tooltip 경계는 유지한다.
  * QG-only 수용 대상 `Base.BallPeenHammer`, `Base.GardenSaw`, `Base.HammerStone`은 public Layer 4 row를 제공한다. 특히 Stone Hammer의 우클릭 행동 누락은 current projection에서 교정됐다.
  * 지원 locale에서 번역 부재를 이유로 알려진 Layer 2–3 정보를 숨기지 않는다. 이 원칙에 어긋난 EN hide 동작은 폐기됐고, current behavior는 KO/EN 양쪽에 정보 계층을 표시한다.
  * Layer 2는 동일한 50개 classification template ID에 KO/EN 문장을 제공한다. Layer 3 EN payload는 exact current facts에 결속되고 pointer-selected generation의 non-empty KO 공개 키 집합과 일치하는 2,072개 companion localization entry이며 KO current body와 source semantics를 바꾸지 않는다.
  * Layer 3 runtime은 요청 locale의 precompiled payload만 선택한다. cross-locale raw-text fallback은 금지하며, EN lazy chunk/index는 presentation routing일 뿐 semantic authority, fact inference 또는 새 validator가 아니다.
  * item/locale 전환은 detail과 interaction UI state의 owner를 함께 바꾼다. 이전 item의 검색·compact/full 상태나 이전 locale의 text가 다음 화면에 남지 않는다.
  * Owner in-game acceptance에서 부팅, Iris Browser, 223 Bullets Mold, Tongs compact/full/search, Recipe 제작 UI 이동, item 전환, 세 QG-only 항목, 기존 context menu/Wiki/Alt Tooltip의 정상 동작과 화면 겹침/잘림 없음이 확인됐다. KO/EN 전환 뒤 Layer 2–3 EN 표시와 Stone Hammer 우클릭 행동도 별도로 확인됐다. 기존 surface의 fallback 분기 자체는 수동으로 구별해 검증한 것으로 주장하지 않는다.
* Non-decision:

  * locale projection은 새로운 사실 생성, 추천, 추론 또는 Layer 3 semantic authority 변경을 승인하지 않는다.
  * 일회성 localization producer나 이번 작업의 ad hoc 검사를 canonical validator, 정규 검사기 또는 후속 validation authority로 승격하지 않는다.
  * main 통합은 push, RTC, Publish, release/Workshop/deployment readiness를 뜻하지 않는다.
* 구현 readpoint: Layer 4 main merge `e7508c0c`, Layer 2–3 EN locale projection `de146b73`. EN Layer 2–3 hide 동작을 포함했던 `1524d72a`는 `de146b73`에 의해 superseded됐다.
* 통합 제품 readpoint: Layer 3 install terminal subject `d006f6108093886751e538d36c92de3627a9e76f` / tree `5e2370f8e5720e830b8ef62c87b6c51c45bfaa4a`는 `e7508c0c`와 `de146b73`을 모두 조상으로 포함한다. 세 결과는 별도 HEAD가 아니라 이 단일 tree에 동시에 존재하며, DVF 동결 검증의 Phase 0은 이 ancestry와 선택한 current observation subject를 확인해 통합 조건을 닫는다. 이미 선형 통합된 조상들을 대상으로 합성 merge commit이나 새 제품 authority를 만들지 않는다.

---

## Iris regular validation authority census — baseline recovery complete / physical legacy cleanup pending

* 날짜: 2026-08-23
* 상태: authority census와 validation baseline recovery 완료 / temporary·legacy executable source cleanup 미완료
* 결정:

  * commit `18d0c2ff9de97a71ddf7aa6b03fb059ffbb35089`, tree `56250ea400511eaf84ff84ee19ee8550f89b8492`는 regular validation authority census, 역할 재분류와 DVF validation-system blocker 복구를 검증한 exact subject다. Post-validation carrier는 `6a4cf63c001ec708929e57da64347e3e7a040d91`이다.
  * 이 subject의 current pytest `433`과 standalone validation `4`는 Run A/B 및 deterministic comparator에서 PASS했다. 이 PASS는 current authority와 baseline 복구에 귀속하며 temporary·legacy physical cleanup 완료를 뜻하지 않는다.
  * 기존 `closeout.json`의 `state=complete`는 채택된 authority-reconfirmation 계획의 scoped closeout으로만 읽는다. 이를 repository lightweighting 또는 temporary-test cleanup Problem 1 전체의 완료로 승격하지 않는다.
  * 기존 1,167행 inventory/contract/disposition은 후속 physical cleanup의 입력 census로 재사용한다. 같은 대상을 다시 세는 대형 ledger나 validation-of-validation artifact를 만들지 않는다.
  * `historical` taxonomy 또는 `reproduction_only` 분류만으로 executable Python source의 물리 보존을 정당화하지 않는다. 보존에는 현재도 유효한 명시적 reproduction obligation, exact consumer와 input, 또는 source 형태가 필요한 실행 계약이 있어야 한다.
  * `evidence_only`의 기본 physical disposition은 executable source 보존이 아니라 compact sealed evidence 또는 repository-external durable evidence와 hash-bound pointer다. Executable source 보존은 현재 소비자나 재현 의무가 별도로 입증된 예외다.
  * regular contract와 non-current contract가 같은 source에 섞여 있으면 current contract를 독립 source로 보존하고 non-current contract는 split 후 같은 물리 disposition 기준으로 재심사한다.

* 관측된 successor input:

  * current regular composition은 pytest `433` + standalone `4`이며 census 전후 execution-unit 감소는 `0`이다.
  * 물리 제거는 current contract가 없던 `test_tc8_full_pipeline_snapshot` 1개뿐이다.
  * 현재 존재하면서 regular contract가 하나도 없는 source는 `37`개, executable identity는 `216`개, raw source bytes는 `329,344`다. `reproduction_only`는 `24 files / 153 identities / 268,519 bytes`, `evidence_only`는 `13 files / 63 identities / 60,825 bytes`다.
  * Ledger상 regular와 non-current disposition이 함께 있는 source는 3개다. 이 중 두 source에는 live non-current identity가 남아 있고, `Iris/test/test_rightclick_pipeline.py`의 non-current TC8은 이미 제거됐다.
  * Baseline `a570f34065fa96a459f946171330f080a8f1c8d1`에서 carrier까지 tracked tree는 약 `6.15 MiB` 증가했다. 따라서 이 lifecycle의 채택 성과는 authority census와 baseline recovery이며 repository byte/LOC lightweighting은 달성되지 않았다.

* 후속 완료 기준:

  * 37개 pure non-current source와 live mixed-source non-current identity를 개별 retention obligation으로 재심사한다.
  * 제거·외부화·compact sealed evidence 전환 뒤 실제 removed file, identity, byte와 repository-wide net byte/LOC를 기록한다.
  * Current pytest `433`, standalone `4`, source taxonomy/manifest binding과 fail-closed contract를 보존하고 exact-subject Run A/B 및 comparator가 exit `0`이어야 한다.
  * 대형 ledger를 외부화할 때 compact in-repo summary는 exact retrieval path, SHA-256와 claim boundary를 유지하되 external ledger 자체를 새 validation authority로 승격하지 않는다.

* Non-decision:

  * wall-time, CPU, memory 개선률은 comparable before/after benchmark가 없으므로 결정하지 않는다.
  * Historical evidence 삭제, current contract 축소, product runtime 변경, release/Workshop/deployment readiness를 승인하지 않는다.
  * Census PASS를 이용해 물리 cleanup residue를 숨기거나 Problem 1을 완료로 닫지 않는다.

* Evidence: `Iris/_docs/round3/validation_contract_reconfirmation/`의 inventory, disposition, final composition, route attribution, independent review와 closeout carrier.

---

## Iris temporary/one-off validation executable retirement — terminal validation PASS / independent review PASS

* 날짜: 2026-08-23
* Independent review 갱신: 2026-08-24
* 상태: survivor correction exact-subject terminal validation과 S0→S1 full-range P8 review PASS / dirty-main evidence-locator 부재로 P10 blocked
* 결정:

  * Corrective survival authority `9739b389f0076903a3494f3d78edc3193fded458`와 physical-domain authority `145b1dd2e21afa957be3ffe87ab8ea3bde069ce0`를 적용한다. Authority-only readpoint는 first destructive commit `4e527b845d2cb6e05a6694e425e607fc95b42ead`보다 앞선다.
  * Regular 599 identity는 survivor correction을 반영해 `keep_regular_product_contract=224`, `keep_regular_validation_system_contract=92`, `remove_regularized_temporary=283`으로 닫는다. Registration-only survivor, unfinished migration과 owner-blocked identity는 각각 `0`이다.
  * Non-current 568 identity 중 current consumer가 확인된 3 family/39 identity는 current product contract로 승격하고, repository-local executable obligation이 없는 529 identity는 퇴역한다. Full-gate conflict 56 identity는 current 39 보존/17 퇴역으로 닫는다.
  * Tracked transaction은 correction을 포함해 96개 full source/exclusive support file과 mixed callable 9개를 제거한다. Dirty-main transaction의 163 file/335 identity/901,270 raw bytes 수치는 historical report로만 보존하며, discoverable archive/restore locator가 없어 그 safety completion을 이 세션에서 독립 재주장하지 않는다. Current product survivor 6 family/13 identity는 보존한다.
  * Repository-local `historical`, `diagnostic`, `all` 실행 selector와 corpus materialization availability를 종료하고 `current` selector와 current fail-closed validation contract를 유지한다. Predecessor ledger, sealed receipt와 Git history는 rewrite하지 않는다.
  * Exact terminal subject `99585ff2a4738055d12aa2f7b42cf74d06f13860` / tree `944f7e66692ab30453f3ddf39ce71f2461f2e43d`에서 Python syntax, focused validation `33`, current runner `110`, configured collection `231`, Clean-Checkout Run A/B와 deterministic comparator가 PASS했다. Canonical result SHA-256은 `a1ce7cd24073f1b2383e0cdd3b12c18871ebb9ed436c9b19486e6b88d5a72f66`이고 source/external mutation은 `0`이다.
  * 첫 S0→S1 Codex review가 보고한 Medium stale-reference finding `2`건을 correction에 포함해 제거했다. Exact range `fd0504817af8c1031ac794391cf67d129c8db54c..99585ff2a4738055d12aa2f7b42cf74d06f13860` 최종 Codex Reviewer 결과는 exit `0`, actionable finding `0`, PASS다. 따라서 P8은 충족됐다.
  * 실행 부담은 predecessor exact gate의 pytest `433` + standalone `4` = `437` unit에서 terminal pytest `221` + standalone `4` = `225` unit으로 `212` unit (`48.513%`) 감소했다. Round 3 current taxonomy는 `228`에서 `110` identity로 `118` (`51.754%`) 감소했다.
  * Tracked tree에서는 executable identity 합계 `460`과 full source/exclusive support file `96`을 제거했다. Net tracked blob은 `8,217,910` bytes (`1.025%`), test/tooling LOC는 `25,973` (`10.010%`) 감소했다.
  * Survivor correction은 기존 keep `328` identity를 다시 열어 regular lifecycle-only `12`와 predecessor inventory 밖 subject-specific callable `1`을 추가 퇴역시켰다. 남는 regular authority는 product `224`, validation-system `92`, 합계 `316`이다. Full test source `3`, exclusive staging generator `1`, mixed callable `7`을 추가 제거했고 stale active contract reference `2`건도 제거했다.
  * Dirty-main outside-overlay validator-like source `32`개는 현재 taxonomy, required manifest, full gate와 두 retirement overlay 어디에도 속하지 않으므로 `not_regular_not_registered`로 기록한다. 다만 기존 archive manifest와 restore receipt의 discoverable locator가 없으므로 새 물리 삭제는 하지 않고 dirty-main archive/restore completion claim을 blocked로 낮춘다.
  * Correction terminal validation과 full-range P8 review는 PASS했다. 다만 dirty-main archive/restore locator가 discoverable하지 않으므로 해당 safety domain은 blocked로 유지하고 P10 completion token은 발행하지 않는다.

* Metric boundary: tracked repository, dirty-main ignored/untracked, external archive를 서로 다른 domain으로 유지한다. Comparable timing/CPU/memory benchmark와 S0/S1 prompt, cached-input, output, tool-output token telemetry가 없으므로 runtime 또는 실제 GPT/Codex token 개선률은 주장하지 않는다. Byte `1.025%`, test/tooling LOC `10.010%`, gate/taxonomy `48.513~51.754%` 감소는 workload별 정적 proxy이지 token usage 측정값이 아니다.
* Non-decision: runtime Lua/product data/public text/package 변경, historical replay PASS, in-game QA, RTC/Publish, release/Workshop/deployment/B42 readiness 또는 public-text quality acceptance가 아니다.
* Evidence: `Iris/_docs/round3/temporary_validation_physical_retirement/{retirement_summary.json,closeout.json}`.

### Iris validation — six-family canonical-presence successor correction (2026-08-24)

* 결정: dirty-main에서만 보존되던 exact 6 family/13 identity를 disposition A (`promote_tracked_regular_product_contract`)로 canonical tracked source에 승격한다. 승격 대상은 browser use-case, line-count CLI, object-access compatibility, session-cache, tag-precision, view-model contract이며 `.gitignore`에는 이 6개 source에 대한 exact allow rule만 추가한다.
* Exact implementation subject는 `052ef0e5c90282ef9afac830bb4491b36d4e92fc` / tree `9a952fab3442bea45cada05a4b660245f978a27e`다. Product/runtime code와 regular survivor 분류(product `224` + validation-system `92` = `316`)는 바뀌지 않는다. 물리적 canonical presence만 dirty-local `6/13`에서 tracked `6/13`으로 이동한다.
* Successor denominator는 taxonomy `123`, required manifest `70`, configured collection `244`, current runner `123`이다. Clean-checkout A/B와 comparator는 pytest identity `234` + standalone `4` = `238` unit으로 PASS했고 source/external mutation은 `0`이다.
* Dirty-main의 validator-like source `32`개는 계속 `not_regular_not_registered`다. Archive SHA-256 `c9638483...526`과 restore SHA-256 `7b05dd6e...bf6c`는 discoverable locator가 없는 `historical_unresolved_hash_reference`이므로 163-file archive/restore claim은 재주장하지 않는다.
* 따라서 canonical tracked correction과 exact S0→correction-carrier Codex Reviewer PASS(actionable finding `0`)로 P8은 닫는다. P10 completion은 여전히 withheld이고 completion token은 `null`이다. 이 correction의 일회성 검사나 검색은 새 validation authority가 아니다.

### Iris validation — P10 owner waiver and completion (2026-08-24)

* 상태: **P10 PASS / physical retirement complete**. 이 항목은 바로 위 successor correction의 P10 withheld 판정을 supersede한다.
* 소유자 결정: 이미 삭제된 dirty-main 임시 validation material은 복구 대상이 아니다. Archive manifest, 파일별 삭제 사유, 삭제 전 원문 보관과 fresh-root restore receipt를 완료 조건에서 명시적으로 면제한다. 존재하지 않는 증빙을 발견·검증된 것으로 간주하지 않으며 기존 hash와 `null` locator는 historical unresolved reference로만 남긴다.
* `163`은 ignored/untracked 로컬 파일 수, `335`는 그 안에서 과거 집계된 validation identity 수, `901,270`은 raw-byte 과거 관측치다. 이 값은 canonical tracked retirement metric이나 정규 테스트 제거 수가 아니며 tracked 성과 수치에 합산하지 않는다.
* 완료 기준은 canonical tracked state다. Exact successor baseline은 `052ef0e5c90282ef9afac830bb4491b36d4e92fc`; retired target의 current authority 등록은 `0`; current boundary는 pytest identity `234` + standalone `4` = `238`; terminal validation과 P8 independent review는 PASS다.
* 결정: P10을 PASS로 닫고 completion token `temporary_validation_physical_retirement__complete`를 발행한다. Archive/restore 요구나 dirty-main historical reduction 수치를 이후 test merge에서 다시 completion gate로 열지 않는다.
---

## Iris — DVF Problem 4 Blocker 6 Layer 3 locale key-set correction

* 상태: 2026-08-22 correction implementation complete
* 결정:

  * EN localization producer의 공개 키 owner를 predecessor `dvf_3_3_rendered.json`에서 pointer-selected current generation의 approved candidate로 옮긴다.
  * Producer는 자신이 실제 소비하는 current-generation canonical input인 facts와 approved candidate의 descriptor identity를 확인하고, non-empty `text_ko`가 있는 키만 EN companion payload에 포함한다. 그 결과 current KO/EN public Layer 3 key set은 각각 `2,070`개다.
  * Runtime은 EN lookup 결과만으로 본문을 공개하지 않는다. Current Layer 3 entry가 없거나 `text_ko`가 non-empty public body가 아니면 EN lookup에 stale 값이 남아 있어도 침묵한다.
  * 기존 EN-only 14개(`Base.BarbedWire`, `Base.Bleach`, `Base.CarBatteryCharger`, `Base.Hinge`, `Base.Jack`, `Base.LeatherStrips`, `Base.LugWrench`, `Base.Paintbrush`, `Base.Pipe`, `Base.Rope`, `Base.Scotchtape`, `Base.ScrapMetal`, `Base.TirePump`, `Base.Toolbox`)는 companion payload에서 제거한다.
  * Focused tests `8 passed`, Lua syntax `157 files`, PowerShell 5.1/7 `current_runtime_payload` package가 모두 exit `0`이다. 두 package의 file/path/hash/byte row는 `170`, delta는 `0`이다. Manifest raw bytes는 package root와 shell별 JSON formatting을 포함하므로 product-content identity로 사용하지 않는다.
* Non-decision:

  * 이 correction은 Layer 3 facts, KO body, role readiness/disposition, immutable current generation 또는 pointer를 변경하지 않는다.
  * Localization builder와 focused assertion을 canonical validator, 정규 validation authority 또는 새로운 seal/receipt 체계로 승격하지 않는다.
  * 과거 Problem 4 exact subject의 `동결 불가` verdict나 evidence를 수정하지 않으며, Blocker 6 correction을 새로운 subject의 freeze PASS로 해석하지 않는다. Freeze verdict가 필요하면 correction이 포함된 새 exact subject로 계획된 hard-gate chain을 다시 실행한다.

---

## Iris — DVF Problem 4 Blocker 11 two-item Layer 3 material resolution

* 상태: 2026-08-22 correction implementation and current installation complete
* 결정:

  * Problem 5A handoff의 exact two-item set인 `Base.Bleach`, `Base.Rope`만 보강한다. 기존 `primary_use` 문구는 유지하고 provenance를 `identity_fallback`에서 `direct_use`로 승격한다.
  * `Base.Bleach`의 근거는 ItemScript의 `CustomContextMenu=Drink`이고, `Base.Rope`의 근거는 `CraftLogStack` dynamic group이 `Rope` tag alias로 `Base.Rope`를 해석하는 current repository evidence다. Layer 4 row나 rendered prose를 새 facts authority로 사용하지 않는다.
  * 두 decision은 기존 direct-use branch와 같은 `cluster_absent_keep_direct_use`, `compose_profile_source=originating_profile`, `use_source=direct_use`를 사용한다. Approved candidate의 non-target 2,103개 entry는 유지하고 두 target만 silent에서 source-bound public role material로 전환한다.
  * Candidate public count는 `2,070 -> 2,072`, silent count는 `35 -> 33`이다. Canonical seven-input route가 generation `dvf33-028a396886eee3ed9bbb6f610c64c8e886ac3e3aab7b8c7381d5d4a48d7145e9`를 생성·검증하고 predecessor `dvf33-aa138aa4896b68ac53609a4b1cb6e5346245e74f544db28eb2ee924dc7b3e814`에서 current pointer를 한 번 전환했다.
  * EN companion은 같은 current public key set `2,072`개로 재생성한다. Package lookup identity는 `lookup-386573f6b917d499`로 갱신한다.
  * Complete-generation validation과 stateless runtime compatibility는 exit `0`, focused tests는 `3 passed / 6 subtests passed` 및 `7 passed`, Lua syntax는 `169 files`, PowerShell 5.1/7 package는 각각 exit `0`이다. 두 package의 content row는 `184`, delta는 `0`이다.
* Non-decision:

  * 이 correction은 과거 Problem 4 exact subject의 finding ledger나 `동결 불가` verdict를 다시 쓰지 않는다. 새 freeze verdict는 correction successor가 포함된 새 exact subject로 integrated hard-gate chain을 다시 실행할 때만 결정한다.
  * 두 항목 보강을 전체 Layer 3 facts truth audit, RTC, Publish, release/Workshop/deployment 또는 owner-sealed closure로 확대하지 않는다.
  * 이번 작업의 일회성 변환·비교 명령을 canonical validator나 새 validation authority로 채택하지 않는다.

---

## Iris — temporary/one-off validation physical retirement main integration closeout

* 상태: 2026-08-24 **complete and published**.
* 결정:

  * Canonical implementation baseline은 `052ef0e5c90282ef9afac830bb4491b36d4e92fc` / tree `9a952fab3442bea45cada05a4b660245f978a27e`로 고정한다. Dirty-local product-contract source 6 family/13 identity는 tracked canonical source로 승격됐고, current validation boundary는 pytest identity `234` + standalone `4` = `238`이다.
  * Terminal validation과 exact-range Codex Reviewer P8은 PASS이며 actionable finding은 `0`이다. Retired target의 current authority 등록은 `0`이다.
  * Project owner는 이미 삭제된 ignored/untracked dirty-main validation material의 archive manifest, 개별 삭제 사유, 삭제 전 원문 보관과 fresh-root restoration receipt를 P10 completion condition에서 면제했다. Locator는 계속 `null`이고 과거 hash를 발견·검증됐다고 주장하지 않는다.
  * Dirty-main `163` file / `335` identity / `901,270` bytes는 non-canonical historical observation이다. Tracked retirement metric이나 정규 test 제거 수에 합산하지 않는다.
  * P10은 PASS이며 completion token은 `temporary_validation_physical_retirement__complete`다. Owner-waived archive/restore 요구를 이후 test merge에서 다시 completion gate로 열지 않는다.
  * Successor는 merge commit `992f45645855830bb9c169827ae4bc60b7938f56`으로 `main`에 통합됐고 같은 commit이 `origin/main`에 publish됐다. Main의 기존 dirty 변경은 staged/committed하지 않았으며 세 top-document의 독립 section을 병합해 모두 보존했다.
* Non-decision:

  * Merge/publish carrier는 implementation baseline `052ef0e5`나 validation denominator `238`을 재정의하지 않는다.
  * 이 closeout을 runtime/in-game QA, RTC, Publish product action, release/Workshop/deployment, performance 또는 실제 GPT/Codex token 개선 claim으로 확대하지 않는다.
  * Owner decision·문서 통합 뒤 추가 테스트나 validation-of-validation을 실행하지 않았다.

## Iris regular validation boundary consolidation (2026-08-25 correction)

* 상태: **complete**. Machine PASS subject는 `b7c4fa54acd43b0d64b51089ed34357c18a6c469` / tree `d6a6a8feef9724482ca3e2004161a66bd6633f92`다.
* 결정:

  * S0의 pytest `234`, standalone `4`, execution `238`, taxonomy `123`, manifest `70`을 각각 `192/4/196/102/61`로 consolidation한다. Round 3는 pytest identity `5 -> 4`, runner import `5 -> 1`이다.
  * Predecessor contract는 named subtest/check, immutable shared seed와 case-local reset/clone으로 보존한다. Exact 238/123/70 row closure와 최종 검증·review locator는 compact implementation map을 따른다.
  * Focused `83 passed / 73 subtests`, Round 3 역순 동일-process 2회 `8 tests`, clean Run A/B와 deterministic comparator가 exit `0`이다. Codex Reviewer 결과는 actionable/unsupported/unimplemented/remaining eligible 모두 `0`이다.
  * Validation/tooling은 S0 대비 `15,151` bytes 순감소했다. 최종 documentation 증가와 `<= 0` context proxy는 compact map의 exact carrier 측정을 따른다.
* Non-decision: wall-clock·실제 tokenizer/Codex token 절감, product/runtime/public output, in-game, RTC/Publish, release/Workshop/deployment authority는 측정하거나 변경하지 않았다. 일회성 검사 명령은 새 validator가 아니다.
## Iris responsibility/repository refactor — W1 successor decisions adopted (2026-08-25)

* 상태: approved plan / `change_1_through_change_10_authorized`; W0 actual baseline `22e94077dd057a943ba2e6ff03f25f5880b3126c` owner-adopted.
* Iris가 설치하던 bullet reload replacement와 context-menu texture render wrapper는 대체 구현 없이 삭제한다. 두 patch가 방어하던 reload replacement 및 nil/invalid `tickTexture` defect는 기록하되, 삭제 뒤 Iris가 주장하는 범위는 전역 함수 non-interference까지다. 임의 외부 모드 조합의 compatibility는 `unvalidated_but_in_scope`이며 삭제 기능을 Nerve, Pulse, 다른 spoke 또는 공통 helper로 옮기지 않는다.
* `phase0_supported_api_manifest.json`에 listed된 `IrisData`, `IrisBrowserData.build`, `IrisBrowserData.getGroupVariants`, Wiki render facade는 thin current adapter로 보존한다. `StaticData.getLegacyIrisData`는 listed supported surface로 승격하지 않고 내부 implementation detail로만 유지한다.
* Layer 3 배포 package는 current pointer가 선택한 generation 하나만 포함한다. inactive generation과 legacy fixed chunks의 source는 이 계획에서 이동·수정·삭제하지 않고 rollback/bootstrap predecessor로 보존한다.
* 구현 checkpoint와 migration binding은 `Iris/_docs/refactor/responsibility_repository_refactor/{s0_baseline_adoption.json,successor_decision.json,current_migration_map.json}`을 따른다. Historical/staging/evidence/frozen payload의 기존 authority를 supersede하지 않는다.

## Iris responsibility/repository refactor — implementation adoption (2026-08-25)

* 상태: `complete` within the stated validation ceiling. W2–W10 implementation, exact subject `d3dfec94c45cb21d27ac54120e2551532ded3e9b`의 automated terminal validation과 bounded supported-PZ Iris-only manual probe를 adopted했다.
* Current Description v2/right-click owner는 installed `iris_tooling` package다. Current consumer의 `tools.build` import, cwd/sys.path bootstrap과 right-click version mode flag는 허용하지 않는다.
* Browser와 Detail의 former monolith 책임은 projection/lifecycle/metrics 및 fact-reader/assembler/presentation owners로 이관한다. Supported facade의 signature/result shape는 유지한다.
* `IrisData.lua`는 focused classifications/variant groups를 운반하는 thin table-identity adapter다. `StaticData.getLegacyIrisData`는 비공개 implementation detail로 남되 Iris product consumer는 없다. Recipe/Moveables/Fixing의 unlisted no-op `build()`는 제거한다.
* Package projection은 current Layer 3 generation-only다. Source predecessor hold는 유지되며 package output authority로 승격되지 않는다.
* W2–W9 implementation commits는 각각 `35a3a1f4`, `996724ba`, `3a02185a`, `c1128b96`, `96fec29b`, `bfd78aa5`, `05809f54`, `5e810430`이다. Environment authority는 W5까지 갱신했고 W6–W9는 package source/lock byte identity 조건으로 W5 record를 재사용했다.
* Terminal environment v4에 결속된 clean Run A/B, deterministic comparator, installed/arbitrary-cwd CLI, package tests와 Lua syntax는 PASS했다. 2026-08-25 repository owner는 Iris-only 환경의 boot/save load, Browser/Detail/Wiki/Alt Tooltip, firearm/ammunition reload와 inventory/world context menu에 Lua 오류나 명백한 회귀가 없음을 확인했다.
* CheatMenuRebirth 동시 활성화 실행에서는 vanilla `ISContextMenu.render`가 null `tickTexture`에 `getWidthOrig()`를 호출하는 반복 오류가 관찰됐다. 이는 모든 외부 모드 compatibility PASS가 아니며 계획의 `unvalidated_but_in_scope` ceiling에 남는다. 삭제한 Iris global render patch를 복원하거나 다른 모듈로 이전하는 decision은 아니다.
* Physical delta decision: package의 Layer 3 generation/fixed payload는 `10,650,501 -> 1,954,408` bytes, 즉 `8,696,093` bytes(`81.65%`) 줄었다. 이 수치는 inactive generation 3개와 legacy fixed chunk 11개가 package projection에서 제외된 범위이며 source predecessor 삭제나 전체 ZIP 감소율이 아니다. Tracked product Lua는 `78,464` bytes(`0.61%`)와 net `1,440` lines 감소했다.
* Metric boundary: W0 baseline `22e94077`에서 completed closeout carrier `09443685`까지 repository 전체 tracked blob은 installable package/authority/docs 추가로 `790,473,779 -> 791,495,072` bytes, 즉 `1,021,293` bytes(`0.13%`) 증가했다. 따라서 repository byte lightweighting이나 무차별 full-scan context 절감을 성과로 채택하지 않는다. 실제 runtime timing/CPU/memory/FPS와 GPT/Codex prompt/cache/input/output token은 미계측이며 package byte delta를 performance/token 개선률로 환산하지 않는다. 이 read-only 집계는 canonical validator나 새 validation authority가 아니다.
* Non-decision: PZ/외부 모드 전체 compatibility, release/freeze/RTC/Publish/deployment, 장시간 multiplayer와 실제 performance/token 개선은 이 adoption의 claim이 아니다.

## Iris responsibility/repository refactor — bounded correction adoption (2026-08-25)

* 상태: **complete**. Correction baseline은 `0311718b2334fc3b45908b2f0d2117c7dc57569a`, machine-validation subject는 `cbfb4f2e0067413f5334b1ca40c3cd89a090606a` / tree `afcf40cc7b4003571fc137c89d7b99d2042e9d9b`다.
* 결정:

  * W4에서 분리했지만 여전히 5,107줄과 4,095줄이던 두 public-text 파일은 compatibility façade로만 남긴다. Acceptance 구현은 context, infrastructure, contracts, rules, reporting, emission, foundation application, attempt context, policy, assurance, disposition, validation과 두 CLI를 포함한 14개 owner module이 소유한다. Naturalization 구현은 context, infrastructure, preparation, projection, transformation, review, handoff, application과 CLI owner가 소유한다.
  * `public_text_quality_acceptance.py`의 남은 책임은 기존 import surface 재수출뿐이며, `run_dvf_3_3_korean_prose_naturalization.py`는 기존 import surface와 script entrypoint를 domain application/CLI로 전달하는 역할만 유지한다. 기존 consumer 호환 때문에 이 façade를 삭제하지 않는다.
  * Package source path는 설치 wheel의 `__file__`에서 역산하지 않고 explicit repository context가 가리키는 `Iris/tooling/src/iris_tooling`에서 해석한다. Phase 0 provenance의 roadmap, plan review, cycle-2 review는 `--roadmap-input`, `--plan-review-input`, `--cycle2-review-input`으로만 받으며 사용자 attachment 경로를 default authority로 두지 않는다.
  * `domains/rightclick/capability.py`는 current v2.4 CLI consumer가 없고 과거 test만 소비하던 non-current 구현이므로 current wheel에서 제거한다. Current command는 계속 `pipeline_v24.py`만 사용하며 historical implementation/evidence는 기존 위치에서 보존한다.
  * Current rendered input에서 허용되는 `body_plan: null`은 빈 plan과 동일하게 census한다. 이는 legal input 처리 교정이며 product public-text schema나 runtime output 변경이 아니다.
* Validation adoption:

  * terminal-v9 environment receipt에 결속된 focused batch는 `24 passed`, Lua syntax는 `174 files` PASS, 설치 wheel의 repository 밖 `phase5-adversarial` 실행은 fixture `8/8`과 required reason `8/8` PASS다.
  * Exact clean Run A/B는 각각 pytest identity `205`, subtest `109`, standalone `4`로 exit `0`이며 canonical result SHA-256은 양쪽 모두 `ba7049aec35a76f175136996c6fb8cf1dc10140bb801dcea93d26db7f5b38819`다. Comparator는 `succeeded`, external mutation은 `0`, source/clone post-status는 clean이다.
* Non-decision:

  * 이 correction은 validation consolidation, 별도 repository lightweighting, runtime/UI/package/public-text content 변경, compatibility patch 복원, release/freeze/RTC/Publish/deployment를 열지 않는다.
  * CheatMenuRebirth 동시 활성화 조합은 계속 `unvalidated_but_in_scope`다. Iris-only owner probe의 기존 PASS나 retired global patch의 non-restoration 결정을 universal external-mod compatibility로 확대하지 않는다.
  * 두 façade의 line 감소와 package source의 net line 감소를 runtime performance나 실제 GPT/Codex token 절감률로 환산하지 않는다. 이번 일회성 집계는 validator나 metric authority가 아니다.
