# DECISIONS.md

> 상태: current decision ledger / compact trace-dedup edition
> 기준일: 2026-06-21
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

### Iris — 검증된 compiler-viewer형 위키 시스템

- 상태: current readpoint / pre-ledger imported + 2026-03-25 system seal
- 결정: Iris는 단순 정보 모드나 웹/위키 수동 보강형 위키가 아니라, 오프라인 빌드가 증거·분류·상호작용·설명 산출물을 컴파일하고 런타임 Lua가 이를 재구성해 보여주는 검증된 위키형 지식 시스템으로 둔다.
- 현재 기준:
  - 런타임 모드는 100% Lua 기반 위키형 viewer로 유지한다.
  - Iris는 실용 정보를 제공하되 해석·권장·비교는 금지한다.
  - Iris는 전체 아이템 위키 표면 위에 Evidence / 분류 / 설명 / 상호작용 정보를 얹는 구조다.
  - 장기 방향은 "compiler -> viewer" 순도를 높이는 쪽이다.
  - QG는 증거 시스템과 파생 산출물의 운영 검문 체계, DVF는 Layer 3 본문 검증 체계로 분리한다.
  - tooltip은 DVF와 동급의 독립 지식원이 아니라 메뉴 본문의 핵심 추출 요약본이다.
  - 외부 모드 데이터는 "원본 mod file -> 정규화 adapter/compiler -> 내부 Iris 표준 산출물 -> QG/DVF 소비" 순서로만 들어온다.
  - QG와 DVF는 raw mod file parser가 되지 않는다.
  - 여러 모드가 같은 아이템을 수정하는 경우 Iris는 엔진 최종 적용값 기준으로 사실만 표시하며, 어떤 모드가 맞는지 중재하지 않는다.
  - Iris의 1차 해자는 위키 대체가 아니라 인게임 접근성이다.
  - 첫 공개는 vanilla-first로 두고, 모드 확장 시스템은 내부적으로 개발하더라도 전면 기능으로 홍보하지 않는다.
- 영향: Iris는 AI식 해석 위키가 아니라, 정규화된 정적 산출물을 런타임에서 보여주는 compiler-viewer형 위키 시스템으로 유지한다.
- Trace:
  - ledgered: 2026-03-16 ~ 2026-03-25
  - COMMON-EVIDENCE-TRACE.

### Iris — Evidence / Source / Outcome 모델

- 상태: current readpoint
- 결정: Iris가 Rule에서 소비하는 Evidence는 행동이 아니라, 그 아이템이 없으면 존재할 수 없는 normalized outcome facts로 고정한다.
- 현재 기준:
  - Source는 Recipe / Right-click / Static capability로 분리한다.
  - Evidence는 Source 자체가 아니라 Source에서 정규화된 outcome facts다.
  - Recipe와 Right-click은 서로의 하위가 아니라 독립 Source다.
  - Iris 분류기는 Source별 rule engine이 아니라 outcome 중심 단일 Evidence 프레임을 소비한다.
  - "open_canned_food", "stitch_wound" 같은 행동 의미형 표현은 Evidence 기본형이 아니다.
  - "equip_back", "toggle_activate", "place_world", "fill_container", "empty_container", "transform_replace" 같은 상태형 outcome을 중심으로 둔다.
  - Equip effect / Use only / Passive function은 기본 evidence 축으로 승격하지 않고, 필요 시 개별 설명층의 후행 정보로 처리한다.
  - "CustomContextMenu = "Smoke"" 같은 행동 문자열 / 메뉴 문자열 / 클릭 경로를 읽어 outcome을 자동 생성하지 않는다.
- Context Outcome 추출기:
  - Context Outcome 추출기는 의미 해석기나 분류기가 아니라, 동결 문서가 이미 허용한 outcome만 생성하는 오프라인 사실 테이블 생성기다.
  - 파이프라인은 "스캐너 -> IR(signal only) -> 매퍼(Signal -> Outcome) -> 수동 주입기 -> 검증기 -> 진단기" 경계로 둔다.
  - Context Outcome 추출기는 Iris Core 바깥의 외부 공급자이며, Iris Core와 Description은 동결된 결과만 소비한다.
  - Fail-loud 사유는 Allowlist 밖 Outcome / 비결정성 / 출력 포맷 위반 세 가지로 제한한다.
  - 금지 토큰 탐지, 문서 SHA 불일치, "smoke_item" 자동 경로 탐지 같은 위험 신호는 숨기지 않되 진단으로만 남긴다.
  - "smoke_item"은 자동 추출기의 기본 산출 대상이 아니며, Option B 수동 주입 모듈만이 유일한 진입점이다.
  - Fixing과 Moveables의 역인덱스·도구 정의는 기존 evidence / predicate 경로에 남기고 Context Outcome으로 승격하지 않는다.
- 오독 금지:
  - 이 항목은 행동명 기반 Evidence 생성, Right-click의 Recipe 하위화, Source별 Rule 이원화, Iris 내부 추론·재판정, 설명 엔진 고도화, 입력 스키마 전면 개편을 승인한 것이 아니다.
- Trace:
  - sealed: 2026-03-24 ~ 2026-03-25
  - COMMON-EVIDENCE-TRACE.

### Iris Right-click — Gate-0 v2.4 / PASS-then-uniqueness overlay

- 상태: current readpoint / code-output reconciled
- 결정: Iris Right-click source의 current 기준은 Gate-0 v2.4 / PASS-then-uniqueness overlay / item-dependent state-change proof로 읽는다.
- 현재 기준:
  - Right-click source는 메뉴명이나 UI 구조가 아니라, 아이템 X를 보유했을 때만 수행 가능하고 그 수행 결과로 컨텍스트 대상의 상태 변화가 실제로 발생하는지를 본다.
  - Gate-0의 핵심 proof는 "executing_tool + external_target + persistent_change"가 모두 성립하는가다.
  - unknown proof는 REVIEW로 격리한다.
  - PASS / NO / REVIEW가 primary decision이다.
  - STRONG / WEAK는 PASS 이후 uniqueness overlay로 계산되는 보조 판정이다.
  - Field Registry는 "decision == PASS"인 결과를 등록하며, STRONG_ONLY 필터로 WEAK를 제거하지 않는다.
  - WEAK는 실패가 아니며, current output/runtime에 보존될 수 있다.
  - Right-click pipeline은 "source_index_v2.4 -> evidence_candidates -> evidence_decisions -> uniqueness_overlay -> field_registry -> usecases/runtime" 계열로 읽는다.
  - FullType 단위의 직접 실행 도구 Evidence를 기본 단위로 둔다.
  - property-based / 조건 기반 필드는 item-by-item STRONG/WEAK 선별보다 먼저 필드 자체가 Gate-0 실행 도구 구조를 만족하는지 판정한다.
  - 미매칭은 Evidence:NO가 아니라 scope 밖이다.
  - REVIEW는 수동 승격 통로가 아니라 허용된 정적 근거만으로 닫히지 않은 자동 체계의 미확정 상태다.
  - 웹/위키 기반 수동 검증은 채택하지 않고, 허용된 정적 근거와 automatic-only 결과를 사용한다.
- Predecessor trace:
  - "아이템이 없으면 타겟 우클릭 메뉴 항목 자체가 생성되는가"라는 좁은 메뉴 생성 기준은 강한 보수 모델이었으나 current canonical 기준이 아니다.
  - "Strong만 canonical outcome fact 후보로 채택하고 Weak는 제외한다"는 과거 문구는 current code/output readpoint와 충돌하므로 current에서 격하한다.
  - "can_*" capability-first 구조, 바닐라 5개 축소 구조, 메뉴명/행동명 중심 Evidence는 current 기준이 아니다.
- 오독 금지:
  - 이 항목은 Strong-only 파이프라인, Weak 실패 처리, capability-first 복귀, 웹/위키 수동 PASS 승격, scope 밖의 Evidence:NO 처리, 메뉴 문자열 기반 outcome 생성을 승인한 것이 아니다.
- Trace:
  - Gate-0 v2 predecessor: 2026-03-25
  - current code/output readpoint: Gate-0 v2.4
  - COMMON-EVIDENCE-TRACE.

### Iris — 자동 분류 / Taxonomy / Allowlist 경계

- 상태: current readpoint
- 결정: Iris 자동 분류는 Evidence Allowlist에 명시된 증거만 누적하는 인덱싱 시스템으로 둔다.
- 현재 기준:
  - Allowlist 밖 필드·문자열·연산·해석은 자동 분류 근거로 쓰지 않는다.
  - 자동 분류의 근거 세계는 바닐라 scripts/client 선언 데이터까지다.
  - Java 디컴파일로 엔진 내부 의미를 끌어와 자동 분류 근거로 쓰지 않는다.
  - 이름 / 설명 / 표시카테고리 기반 추론, 수치 비교, 무제한 contains, 임의 태그 확장은 자동 분류 루트에 들어오지 못한다.
  - 자동 분류가 바닐라 선언 증거로 닫히지 않으면 미분류 태그를 억지 생성하지 않고 침묵하거나 수동 오버라이드로 봉인한다.
  - "MoveablesTag" 네임스페이스와 Item Script의 일반 "Tags"는 혼용하지 않는다.
  - 대량 미분류 문제는 Evidence Table / DSL 부족이 아니라 대분류·소분류 설계와 phase2_rules 운영의 문제로 본다.
  - Iris 대분류 아키텍처는 Tool / Combat / Consumable / Resource / Literature / Wearable / Furniture / Vehicle / Misc 9개 축과 경계 규칙을 기준선으로 둔다.
  - Furniture는 Furniture.7-A 단일 소분류로 고정한다.
  - Vehicle은 Vehicle.8-A / Vehicle.8-B 최소 2분할로 유지한다.
  - Misc.9-A는 rule_executor가 아니라 output-stage fallback이다.
  - Tool.1-K(Security)와 Tool.1-L(Storage)는 정식 소분류다.
  - Tool.1-L(Storage)는 비착용 휴대 컨테이너, Wearable.6-F는 착용 가능한 배낭으로 분리한다.
  - Consumable 3-B 음료 기준은 체감상 마시는가나 수치 비교가 아니라 Drink / Drainable 구조다.
- 오독 금지:
  - 이 항목은 Evidence 레이어 억지 확장, Java 내부 의미 기반 분류, 미분류 태그 생성, Furniture 재세분화, Vehicle 과분할, Resource 쓰레기통화, Wearable의 장착·휴대 확장을 승인한 것이 아니다.
- Trace:
  - sealed: 2026-03-23 ~ 2026-03-25
  - COMMON-EVIDENCE-TRACE.

### Iris — 설명 / 표시 / 브라우징 정책

- 상태: current readpoint
- 결정: Iris 설명층은 문장 생성기나 요약기가 아니라, 증거와 분류가 먼저 닫힌 뒤 정적 위키 문장을 조합·표시하는 계층으로 둔다.
- 현재 기준:
  - 설명 출력은 기본 정보 -> 의미(주 소분류) -> 활용(레시피/상호작용) -> 메타 순서의 정보 위계 기반 출력기다.
  - 설명란의 각 계층은 선행 계층의 필터 결과물이 아니라 독립 정보층이다.
  - Iris 분류 데이터는 유지하되, 기본 UI에서는 전면 노출하지 않고 메타 영역에 격리한다.
  - "primary_subcategory"는 브라우징·탐색을 위한 주 anchor이지, 설명 문장의 자동 근거로 전면 승격하지 않는다.
  - 주 소분류 설명 문장은 모든 아이템에 기본 적용되는 자동 설명이 아니라 조건이 맞을 때만 쓰는 후보 템플릿이다.
  - 설명 왜곡이 보이면 우선 설명 엔진 고도화가 아니라 태그 생성 정합성, Rule/Recipe predicate, 구현 일치성을 의심한다.
  - 개별 아이템 설명은 분류/증거/Source 검증 뒤에 온다.
  - 문서화 담당자는 분류·규칙·증거 체계를 바꾸는 사람이 아니라 이미 확정된 사실을 위키식 정적 문장으로 풀어쓰는 후행 서술자다.
  - 개별 설명은 소분류 설명이나 레시피만으로 충분히 드러나지 않고, 실제 구현된 특별 행동/기능이 초보자에게 놓치기 쉬울 때만 필요하다.
  - 소분류 설명은 분류 안내문이나 분류명 재진술이 아니라 실제 용도·시스템적 의미·적용 범위를 자연스러운 한국어로 풀어쓴다.
  - 추천·효율 평가·비교는 하지 않는다.
- UI 접기:
  - 중복 아이템 목록 문제는 빌드 타임의 전역 기능 동등성 그룹화가 아니라 UI 목록 단계의 DisplayName 중심 접기로 처리한다.
  - 접힌 목록 항목에는 "(xN)" 수량 배지를 붙이지 않고 개념명만 표시한다.
  - 변형 수나 실체 차이는 상세 패널에서만 확인한다.
- 오독 금지:
  - 이 항목은 설명 엔진의 의미 추론 강화, 개별 설명 전수 작성, 분류 ID 삭제, 기능 동등성 빌드 그룹화, 추천/효율 평가를 승인한 것이 아니다.
- Trace:
  - sealed: 2026-03-16 ~ 2026-03-25
  - COMMON-EVIDENCE-TRACE.

### Iris — Recipe / use_case / requirements / Right-click UI 통합

- 상태: current readpoint
- 결정: Iris의 상호작용 계층은 Recipe와 Right-click을 동급 Source로 보고, use_case 단위의 구조화된 오프라인 렌더링 위키 레이어로 둔다.
- 현재 기준:
  - Recipe와 Right-click은 잔여 필터 관계가 아니라 동급 2트랙 증거다.
  - 같은 아이템이 두 트랙에 동시에 걸릴 수 있다.
  - "classification_recipe"는 중심 경로에서 내리고, "rule_id" 중심 "recipe_evidence" 체계를 표준 경로로 사용한다.
  - PASS evidence에는 input/output 참여만 올리고, keep/require는 행동 증거로 승격하지 않는다.
  - consumed와 keep은 role 필드로 구분하고, "recipe_evidence" source에서만 필수 필드로 둔다.
  - DescriptionGenerator는 정적 use_case 렌더러로만 동작한다.
  - "use_case_label_map"은 FAIL-LOUD build contract다.
  - dynamic_recipe_expr 잔여는 PERMANENT_REVIEW 정책으로 봉인한다.
  - recipe requirements는 recipe 단위로만 붙으며 fulltype 전체 공유 정보가 아니다.
  - recipe requirements color layer는 상호작용 탭 안에서 requirement atom 단위 상태표시만 수행한다.
  - Python이 kind별 check 구조를 만들고, Lua는 이를 읽어 색상만 매핑한다.
  - color layer 결과는 다른 탭·모듈·정렬·표시 정책으로 전파하지 않는다.
  - Right-click 계열 라인은 "line_kind = evidence | exclusion"으로 구조 분리한다.
  - "[우클릭]" 문자열을 기존 목록에 끼워 넣고 역파싱하지 않는다.
  - Python이 구조화 블록에서 display_text를 만들고 Lua는 렌더만 한다.
  - UI에는 능력 기반 use_case만 올라가고, exclusion 라인은 행동 블록 후보군에서 먼저 제거된다.
  - Iris UI는 "ISUIHandler.toggleUI"를 override하지 않고 독립 버튼과 독립 블록 구조로 통합한다.
- 오독 금지:
  - 이 항목은 Recipe-only / RightClick-only 잔여 필터화, Lua role 기반 텍스트 보정, Requirements와 Actions 혼합, 레시피 전체 SAT/UNSAT 추천·정렬·숨김 UI, Right-click 문자열 역파싱, exclusion 라인의 UI 행동 근거화를 승인한 것이 아니다.
- Trace:
  - sealed: 2026-03-25
  - COMMON-EVIDENCE-TRACE.

### Iris DVF 3-3 — current authority / production contract

* 상태: current readpoint / successor current authority sealed / production contract consolidated
* 결정: DVF 3-3의 current authority는 legacy manual registry / T-Gate / active-silent 모델이 아니라, `facts -> decisions -> compose -> rendered -> Lua bridge -> chunk runtime data`로 이어지는 successor chain으로 고정한다.
* 현재 기준:

  * current source chain은 `data/dvf_3_3_input_manifest.json -> data/dvf_3_3_facts.jsonl -> data/dvf_3_3_decisions.jsonl -> data/dvf_3_3_overlay_support.jsonl`이다.
  * `data/dvf_3_3_overlay_support.jsonl`은 `compose_support_not_source_authority` 역할이며 source authority가 아니다.
  * current rendered authority는 `output/dvf_3_3_rendered.json`이다.
  * runtime deployable authority는 `IrisLayer3DataChunks.lua` manifest와 `IrisLayer3DataChunks/*.lua` chunk files 단일 bundle이다.
  * `IrisLayer3Data.lua` monolith는 current runtime authority로 복귀하지 않는다.
  * current DVF 3-3 계약 표면은 `docs/dvf_contract_current_reseal.md`다.
  * `body-plan v2`는 별도 권한면이 아니라 `compose_profiles_v2.json + body_plan` 구현 표면의 alias label이다.
  * current runtime vocabulary는 `adopted / unadopted`이며, legacy `active / silent`는 historical / diagnostic / import alias로만 남긴다.
  * runtime은 sealed Lua payload를 렌더링만 하며, compose / repair / source validation / semantic quality judgment / publish policy 판단을 수행하지 않는다.
  * Browser / Wiki / Tooltip은 quality 판단을 badge, copy, sorting, filtering, hiding, recommendation, trust/confidence 표시로 소비하지 않는다.
  * Layer 3-3 DVF는 수동 문장 묶음이 아니라 `facts -> decisions -> compose -> rendered -> Lua bridge -> chunk manifest + chunk files`로 이어지는 오프라인 생산 파이프라인이다.
  * `compose_layer3_text.py`는 본문 조합의 중심 경로다.
  * `export_dvf_3_3_lua_bridge.py`는 rendered 산출물을 Iris 소비자 표면으로 넘기는 정적 export 경로다.
  * 런타임 Lua는 본문 생성 논리를 맡지 않는다.
  * facts와 decisions는 별도 JSONL 파일로 분리한다.
  * 본문 조합은 sentence_plan 블록 단위로 수행한다.
  * DVF 입력은 facts / decisions / profiles로 고정하고, 산출물은 rendered 계열로 둔다.
  * decisions validator는 rendered를 보지 않는다.
  * 3계층 본문의 줄바꿈은 compose-time이나 Lua bridge 단계가 아니라 UI 표시 직전 render-time formatting으로만 처리한다.
  * Phase D는 별도 stub UI가 아니라 기존 Iris 소비자(`IrisWikiSections.lua`, `IrisBrowser.lua`, `IrisWikiPanel.lua`)에 Layer 3를 연결하는 production runtime 통합 경로다.
  * acquisition / style / body-role 계열은 facts 재판정이 아니라 compose / post-compose / decisions overlay / validator-gated production flow 안에서 처리한다.
  * `acquisition_hint`는 삭제되지 않지만 선두를 차지하지 않으며, 3-3의 중심은 아이템 자기 시점의 용도 본문이다.
  * style normalization은 facts 재판정이 아니라 post-compose surface layer다.
  * body-role 개편은 facts 슬롯 확장이 아니라 decisions overlay로 처리한다.
  * `quality_flag`는 rendered 진단 메타데이터일 뿐 상태 축으로 승격하지 않는다.
  * historical runtime의 `active / silent`는 semantic quality가 아니라 `primary_use` output availability 기준의 predecessor vocabulary로만 읽는다.
* 최소 결과 trace:

  * current authority reconciliation inventory: `50 surfaces / classified 50 / unclassified 0`
  * stale current-FINAL surfaces: `0`
  * lexical disposition coverage: `T-Gate 112/112, manual registry 95/95, active-silent 876/876`
  * legacy active/silent current-surface guard: `pass / hard_fail 0 / unclassified 0`
  * source promotion / rendered regeneration / runtime replacement / consumer migration / final chain validation / current route contract: `PASS`
  * sealed successor count: `2105 entries`
  * runtime successor bundle: `11 chunks`
  * current route contract at cutover seal: `98 tests / closure_enforced true / required validations PASS`
  * full pytest / package route / Lua syntax / external validation bundle: `PASS`
  * predecessor runtime/status trace: `2105 rows / active 2084 / silent 21 / residual hold inventory 34 / manual validation pass_with_note`
  * 세부 command와 산출물은 `COMMON-EVIDENCE-TRACE`로 흡수한다.
* 후속 input artifact:

  * current surface: `docs/dvf_contract_current_reseal.md`
  * inventory: `docs/dvf_current_authority_inventory.json`
  * evidence root: `Iris/build/description/v2/staging/dvf_3_3_vnext_current_authority_cutover/`
  * plan: `docs/dvf_3_3_vnext_current_authority_implementation_2105_consumer_migration_plan.md`
  * ledger packet: `docs/dvf_3_3_vnext_current_authority_implementation_2105_consumer_migration_ledger_packet.md`
  * final report: `Iris/build/description/v2/staging/dvf_3_3_vnext_current_authority_cutover/phase10/final_current_authority_cutover_report.json`
* 오독 금지:

  * 이 항목은 runtime Lua 본문 생성, 수동 문장 저장소, separate demo/stub UI, Lua bridge payload 임의 변경, rendered-Lua 일치 기준 완화를 승인한 것이 아니다.
  * 이 항목은 acquisition 삭제, facts 재판정, postproc 기반 표면형 땜질, acquisition-led 본문화, style linter hard gate 승격, body-role facts 확장, runtime-side repair opening을 승인한 것이 아니다.
  * 이 항목은 package release readiness, Workshop readiness, B42 readiness, deployment readiness, manual in-game validation, semantic quality completion, public-facing text quality acceptance를 승인한 것이 아니다.
  * manifest-derived `2105`는 sealed successor entry count로만 허용되며, predecessor hard gate 숫자 치환으로 읽지 않는다.
  * 이 seal 이후 prior current readpoint 복원은 새 additive rollback 또는 correction plan 없이는 허용하지 않는다.
  * COMMON-RELEASE-NONDECISION.
  * COMMON-RUNTIME-SURFACE-NONMUTATION.
* Predecessor trace:

  * production pipeline sealed: 2026-03-25 ~ 2026-03-28
  * acquisition / style / body-role rules sealed: 2026-03-25 ~ 2026-04-05
  * runtime/status closeout trace closed: 2026-03-28 ~ 2026-04-02
  * current authority reconciliation sealed: 2026-06-12
  * successor current authority cutover sealed: 2026-06-19
  * predecessor `2105 / 2084 / 21` baseline은 복구 대상 current authority가 아니라 historical / comparison / migration input이다.

### Iris DVF 3-3 — predecessor / prerequisite evidence chain

* 상태: predecessor evidence chain / consumed by current authority cutover seal
* 결정: Layer3 reconstruction, 2105 baseline consumption audit, vNext pre-cutover authority evidence, consumer migration input normalization, cutover tooling readiness는 current authority 자체가 아니라 successor current authority seal을 가능하게 한 prerequisite / predecessor chain으로 보존한다.
* 현재 기준:

  * 2026-06-12 reconstruction checkout은 2105-key source universe 일부를 제공했지만, sealed full body-plan v2 source path에서 current runtime chunk text를 결정론적으로 재생성할 수 있는 current 입력 세트를 제공하지 못했다.
  * reconstruction readpoint는 current source authority가 아니라 후속 vNext current authority 작업의 predecessor failure / scope boundary trace로 읽는다.
  * 6-entry `data/dvf_3_3_facts.jsonl`, `data/dvf_3_3_decisions.jsonl`, `output/dvf_3_3_rendered.json`은 full-scale reconstruction authority가 아니라 fixture / non-authority로 남긴다.
  * `canonical rendered output promotion status = INELIGIBLE`은 partial reconstruction output의 current 승격 금지 근거로 유지한다.
  * `2105 / 2084 / 21` 및 legacy/current vocabulary 소비처는 2105 baseline consumption audit에서 occurrence 단위로 분류됐으며, 후속 vNext migration / denominator lock / terminal disposition 계열은 이 audit ledger를 read-only 입력으로 삼는다.
  * `active / silent`는 current writer / validator / runtime payload vocabulary가 아니라 historical / diagnostic / import alias로만 읽는다.
  * `adopted / unadopted`는 current runtime vocabulary일 뿐 quality-pass, publish_state, deletion, suppression 의미로 승격하지 않는다.
  * vNext는 frozen `2105 / 2084 / 21` 복구가 아니라 successor authority model이다.
  * `vNext-CAB`는 cutover 전 roadmap / authority-model label이며 actual sealed baseline identity가 아니다.
  * runtime-derived seed는 non-authority bootstrap material이며 source / facts / decisions / rendered / bridge / chunks / ledger authority가 될 수 없다.
  * staging execution Phase 0-11 산출물은 staging evidence이며 canonical current data / output / runtime payload가 아니다.
  * regeneration parity는 frozen 2105 복구 증명이 아니라 vNext successor candidate와 predecessor runtime의 delta 측정이다.
  * rejected delta correction / re-parity는 `108 rejected` blocker를 `54` key의 state alignment 문제로 해소하고, corrected staging input에서 cutover input usability를 회복한 prerequisite gate다.
  * raw audit index, raw migration matrix, dry-run output은 read-only provenance이며 downstream direct entrypoint는 `phase6/consumer_migration_reconciled_input_manifest.json`이다.
  * `change-required 311`은 executor-safe input contract 안에서 `actual_apply_eligible 163 / no_op 148`로 정규화됐다.
  * consumer migration executor는 sandbox copy에서만 apply evidence를 만들고, main repo / live current authority surface를 변경하지 않는다.
  * current-route tooling allowlist cap은 `1`, current core closure는 `12`로 유지하며 새 tools는 자동 allowlist 편입 대상이 아니다.
* 최소 결과 trace:

  * reconstruction provenance branch: `B4_mixed_partial`
  * reconstruction closeout state: `partial`
  * reconstruction parity: `L0 PASS / L1 FAIL / L2 FAIL / L3 FAIL`
  * 2105 audit occurrence rows: `198815 raw / 27869 accepted`
  * 2105 audit executing consumer count: `1062`
  * 2105 audit migration disposition input: `311 change-required / 27558 change-forbidden / ambiguous 0`
  * 2105 audit validation: `Gate A PASS / Gate B PASS / validation PASS`
  * vNext staging execution contract: `PASS / Lua bridge 2105 entries / 11 chunks / protected surface changed_count 0`
  * vNext regeneration parity: `predecessor 2105 / vNext 2105 / missing 0 / additional 0 / determinism PASS`
  * initial delta disposition: `2125 total / 2017 approved / 0 deferred / 108 rejected / cutover_input_usable=false`
  * rejected correction / re-parity: `54 rejected keys corrected / state deltas 0 / approved 2071 / rejected 0 / cutover_input_usable=true`
  * normalization contract: `PASS / 311 rows / actual_apply_eligible 163 / no_op 148`
  * missing path rows / missing apply-eligible: `125 / 0`
  * tooling readiness contract: `PASS`
  * command surface mapping: `PASS / mapped families 6 / unmapped 0`
  * runtime mirror apply / restore probe: `PASS`
  * row-level migration ledger: `311 rows / 163 mutation rows / 148 non-apply rows`
  * actual diff-to-ledger: `PASS / mapped 163 / unmapped 0 / orphan 0`
  * protected surface no-mutation: `PASS / changed_count 0`
  * 세부 command matrix, focused tests, package route, Lua syntax route는 `COMMON-EVIDENCE-TRACE`로 흡수한다.
* 후속 input artifact:

  * reconstruction scope: `docs/layer3-current-authority-reconstruction-scope-lock.md`
  * reconstruction provenance: `docs/layer3_current_authority_reconstruction_provenance.json`
  * reconstruction parity: `Iris/build/description/v2/staging/layer3_current_authority_reconstruction/rendered_runtime_equivalence.json`
  * 2105 audit plan: `docs/2105_baseline_consumption_audit_plan.md`
  * 2105 audit ledger: `Iris/build/description/v2/staging/2105_baseline_consumption_audit/classified_ledger.jsonl`
  * 2105 migration input: `Iris/build/description/v2/staging/2105_baseline_consumption_audit/change_required_index.md`
  * vNext roadmap: `docs/dvf_3_3_vnext_current_authority_roadmap.md`
  * vNext authority plan: `docs/dvf_3_3_vnext_current_authority_plan.md`
  * vNext execution plan: `docs/dvf_3_3_vnext_execution_plan.md`
  * regeneration parity plan: `docs/dvf_3_3_vnext_regeneration_parity_plan.md`
  * delta disposition policy: `docs/dvf_3_3_vnext_delta_disposition_policy.md`
  * guard contract: `docs/dvf_3_3_vnext_guard_seal_contract.md`
  * current-route integration handoff: `docs/dvf_3_3_vnext_current_authority_handoff_packet.md`
  * correction / re-parity ledger packet: `docs/dvf_3_3_vnext_rejected_delta_correction_reparity_ledger_packet.md`
  * required validation manifest: `Iris/_docs/round3/current_route_required_validations.json`
  * reconciled manifest: `Iris/build/description/v2/staging/dvf_3_3_vnext_consumer_migration_input_normalization/phase6/consumer_migration_reconciled_input_manifest.json`
  * row disposition bridge: `Iris/build/description/v2/staging/dvf_3_3_vnext_consumer_migration_input_normalization/phase6/row_disposition_ledger.for_readiness.jsonl`
  * tooling compatibility manifest: `Iris/build/description/v2/staging/dvf_3_3_vnext_cutover_tooling_readiness/phase6/tool_contract_compatibility_manifest.json`
  * tooling final report: `Iris/build/description/v2/staging/dvf_3_3_vnext_cutover_tooling_readiness/phase6/final_tooling_readiness_contract_report.json`
* 오독 금지:

  * 이 항목은 frozen 2105 byte-level recovery, current source authority 복원, canonical rendered promotion, successor baseline identity final seal, current cutover, live runtime chunk replacement, old chunks replacement, package readiness, release readiness, Workshop readiness, deployment readiness, manual in-game validation, public-facing text quality acceptance를 승인한 것이 아니다.
  * staging rendered output, staging Lua bridge, staging chunks, approved delta manifest, corrected approved manifest는 deployable current authority가 아니다.
  * `parent_problem_unlock=true`는 후속 cutover 실행을 여는 prerequisite gate 값이지 parent problem 완료나 live migration execution이 아니다.
  * `handoff_usable=true`는 downstream tooling-readiness input usability predicate이며 cutover authorization이나 migration completion이 아니다.
  * consumer migration sandbox diff는 row-level tooling evidence이지 current consumer migration completion이나 live source / runtime mutation이 아니다.
  * historical / diagnostic / generated / false-positive / no-op rows는 별도 승인 없이 current migration 대상으로 승격하지 않는다.
  * COMMON-RELEASE-NONDECISION.
  * COMMON-RUNTIME-SURFACE-NONMUTATION.
* Predecessor trace:

  * current authority reconstruction negative readpoint: 2026-06-12
  * 2105 baseline consumption audit ledger sealed: 2026-06-12
  * vNext authority model definition: 2026-06-13
  * vNext staging execution contract: 2026-06-13
  * vNext regeneration parity evidence: 2026-06-15
  * delta disposition guard evidence: 2026-06-16
  * delta guard current-route integration: 2026-06-16
  * rejected delta correction / re-parity gate: 2026-06-17
  * consumer migration input normalization: 2026-06-18
  * cutover tooling readiness: 2026-06-18
  * actual current authority adoption, live runtime replacement, old chunk replacement, 2105 consumer migration completion은 successor current authority cutover seal이 우선한다.

### Iris DVF 3-3 — runtime payload / write / export / artifact boundary

* 상태: current guard family / write-export-artifact boundary sealed where specified / stale bridge review pending
* 결정: DVF 3-3 current authority 표면은 runtime payload shape, compose write boundary, Lua bridge export contract, stale artifact quarantine, VCS tracking policy를 통해 historical / staging / diagnostic / stale artifact가 current source / rendered / runtime / package authority로 재유입하지 못하게 한다.
* 현재 기준:

  * current-like runtime surfaces는 live current runtime, package peer, candidate bridge를 함께 검사한다.
  * current-compatible payload shape는 `2105` rows / unadopted `21` rows / current-like `publish_state` rows `0` / current-like forbidden or unclassified state rows `0`이다.
  * unadopted current rows의 display text fields는 `missing` 또는 explicit `nil`이어야 한다.
  * current-like surfaces에서는 renderer-visible `text_ko`가 모든 `unadopted` rows에서 absent이며, `publish_state`도 모든 current-like rows에서 absent다.
  * predecessor rollback snapshot의 `unadopted + exposed + non_nil text_ko` residues `2`는 legacy-only residue로 보존하며 current runtime mutation 근거가 아니다.
  * compose current rendered output 보호 경계는 CLI entrypoint가 아니라 `build_rendered()` shared write boundary다.
  * direct `build_rendered()` 호출과 `python -m tools.build.compose_layer3_text` CLI 호출은 같은 guard를 통과해야 한다.
  * 모든 direct `build_rendered()` write는 `compose_context`를 명시해야 하며 허용값은 `current`, `staging`, `historical`, `diagnostic`이다.
  * current write는 `profile_class=v2_current`, current data input contract, closed protected current-output set을 모두 통과해야 한다.
  * closed protected current-output set은 `output/dvf_3_3_rendered.json`, `output/style_normalization_changes.jsonl`, `output/compose_requeue_candidates.jsonl`이다.
  * output root 아래의 unlisted current-equivalent write target은 fail-loud reject 대상이다.
  * legacy / partial / ambiguous / unknown compose profile은 current-equivalent output write에 사용할 수 없다.
  * `export_dvf_3_3_lua_bridge.py`의 기본 export 계약은 monolith `IrisLayer3Data.lua`가 아니라 current chunk runtime authority를 직접 생성하는 계약으로 재정렬한다.
  * no-arg / default exporter route는 staging output root에 `IrisLayer3DataChunks.lua` manifest, `IrisLayer3DataChunks/*.lua` chunk files, chunk-authority 기반 bridge report를 생성한다.
  * default bridge context는 `staging`, default output format은 `chunk`다.
  * `IrisLayer3Data.lua` monolith export는 explicit `historical` / `diagnostic` context와 explicit output path를 요구하는 side-output mode로만 남긴다.
  * `current` / `staging` monolith export는 fail-loud reject 대상이다.
  * root `media/lua/shared/Iris/IrisDvfBridgeData.lua` 6-entry legacy bridge artifact는 current DVF bridge authority가 아니라 `stale` artifact로 분류한다.
  * 동일 6-entry legacy payload는 `Iris/build/description/v2/staging/stale_dvf_bridge_artifact_disposition/quarantine/IrisDvfBridgeData.legacy_6_entry.lua`로만 보존한다.
  * quarantine payload는 source authority, runtime authority, package / runtime allowlist, deployable payload가 아니다.
  * DVF 3-3 artifact의 VCS tracking 지위는 artifact authority와 독립된 role-based policy로 관리한다.
  * tracked 여부는 authority 승격이 아니며, ignored 여부는 삭제 가능성이나 비중요성을 뜻하지 않는다.
  * current runtime deployable authority는 `Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks.lua` 및 `IrisLayer3DataChunks/*.lua`다.
  * `Iris/build/description/v2/tools/build/export_dvf_3_3_lua_bridge.py`는 `regeneration-tooling / tracked_required`로 둔다.
  * `Iris/build/description/v2/data/dvf_3_3_input_manifest.json`은 `current_regeneration_manifest / tracked_required`로 둔다.
  * generated output, fixture, runtime deployable output, staging evidence, historical reproduction, diagnostic advisory, stale quarantine, forbidden current-looking stale surface는 `docs/dvf_vcs_tracking_policy.md`의 artifact class / expected VCS state matrix를 따른다.
  * Round 3 current core는 `12` modules로 유지한다.
  * `export_dvf_3_3_lua_bridge`는 current-route bridge export 검증을 위해서만 `current_regeneration_tooling` allowlist에 들어가며, current core module로 세지 않는다.
  * current-route tooling allowlist는 `1` module로 capped 상태이며, 확장은 별도 reviewed scope가 필요하다.
* 최소 결과 trace:

  * current-like payload guard: `PASS / rows 2105 / unadopted 21 / publish_state rows 0 / forbidden or unclassified state rows 0`
  * rollback residue inventory: `legacy-only / unadopted + exposed + non_nil text_ko residues 2`
  * current runtime collision: `closed for current-like surfaces`
  * production / tool `compose_context` omissions: `0`
  * default canonical `style_log_path` 의존 call: `0`
  * current / historical / diagnostic compose route validation: `PASS`
  * protected current compose set no-mutation: `PASS / unchanged`
  * bridge export contract validation: `PASS`
  * default / chunk route validation: `PASS`
  * package monolith-forbidden gate: `PASS`
  * protected surface no-mutation: `PASS / changed_count 0`
  * stale bridge classification: `stale`
  * stale bridge disposition: `quarantined_outside_current_looking_path`
  * stale bridge independent review gate: `review_pending`
  * VCS policy focused guard: `PASS`
  * current route closure after VCS addendum: `PASS / 57 tests / closure_enforced true`
  * package route: `PASS`
  * stale current-looking presence report: `PASS / violation_count 0`
  * package zip forbidden scan: `PASS / forbidden_hit_count 0`
  * 세부 command matrix는 `COMMON-EVIDENCE-TRACE`로 흡수한다.
* 후속 input artifact:

  * runtime payload evidence root: `Iris/build/description/v2/staging/runtime_payload_state_integrity/`
  * runtime payload plan: `docs/runtime_payload_state_integrity_plan.md`
  * runtime payload policy: `docs/runtime_payload_state_policy.md`
  * runtime payload shape contract: `docs/runtime_payload_shape_contract.md`
  * runtime payload guard report: `Iris/build/description/v2/staging/runtime_payload_state_integrity/phase4/current_route_payload_state_guard_report.json`
  * compose plan: `docs/compose_entrypoint_guard_hardening_plan.md`
  * compose evidence root: `Iris/build/description/v2/staging/compose_entrypoint_guard_hardening/`
  * compose protected set: `Iris/build/description/v2/staging/compose_entrypoint_guard_hardening/compose_protected_output_paths.json`
  * compose no-mutation verdict: `Iris/build/description/v2/staging/compose_entrypoint_guard_hardening/compose_entrypoint_guard_no_mutation_verdict.json`
  * bridge plan: `docs/lua_bridge_export_contract_realign_plan.md`
  * bridge evidence root: `Iris/build/description/v2/staging/lua_bridge_export_contract_realign/`
  * bridge final contract: `Iris/build/description/v2/staging/lua_bridge_export_contract_realign/final_contract_report.json`
  * bridge no-mutation verdict: `Iris/build/description/v2/staging/lua_bridge_export_contract_realign/no_mutation_verdict.json`
  * stale bridge plan: `docs/stale_dvf_bridge_artifact_disposition_plan.md`
  * stale bridge evidence root: `Iris/build/description/v2/staging/stale_dvf_bridge_artifact_disposition/`
  * stale bridge classification verdict: `Iris/build/description/v2/staging/stale_dvf_bridge_artifact_disposition/classification_verdict.json`
  * VCS policy plan: `docs/dvf_vcs_tracking_policy_plan.md`
  * VCS policy: `docs/dvf_vcs_tracking_policy.md`
  * VCS evidence root: `Iris/build/description/v2/staging/dvf_vcs_tracking_policy/`
  * VCS guard: `Iris/build/description/v2/tests/test_dvf_vcs_tracking_policy.py`
  * closure addendum: `Iris/_docs/round3/round3_active_core_closure.json`
* 오독 금지:

  * 이 항목은 source facts / decisions / rendered / runtime / package mutation을 승인한 것이 아니다.
  * 이 항목은 successor baseline cutover, live runtime chunk replacement, canonical rendered output promotion, Lua bridge mutation을 승인한 것이 아니다.
  * 이 항목은 package readiness, Workshop readiness, release readiness, manual in-game QA, Browser / Wiki / Tooltip behavior change를 승인한 것이 아니다.
  * `implemented guard pass`는 independent review complete seal이나 current-route 전체 재봉인이 아니다.
  * stale bridge 항목은 independent review gate를 통과한 sealed PASS가 아니다.
  * `IrisDvfBridgeData.legacy_6_entry.lua` quarantine retention은 historical evidence 보존이지 current bridge fallback 복구가 아니다.
  * default chunk export는 exporter behavior와 current authority contract의 정렬이지 새 baseline identity나 live deployable payload mutation이 아니다.
  * current-route tooling allowlist는 current core list의 우회 확장면이 아니다.
  * COMMON-RELEASE-NONDECISION.
  * COMMON-RUNTIME-SURFACE-NONMUTATION.
* Trace:

  * compose guard implemented / validated: 2026-06-13
  * compose guard ledgered: 2026-06-15
  * Lua bridge export contract implemented / validated: 2026-06-15
  * stale bridge disposition implemented: 2026-06-15
  * Artifact VCS Tracking Policy implemented / validated: 2026-06-15
  * runtime payload state integrity guard sealed: later current guard pass
  * closeout, full command matrix, focused test details는 `COMMON-EVIDENCE-TRACE`로 흡수한다.

### Iris DVF 3-3 — consumer denominator / terminal disposition governance

* 상태: denominator live required-validation adopted / terminal canonical complete / independent review pass
* 결정: Denominator Governance가 분리한 `1062` executing-consumer member-row universe를 Terminal Disposition Adjudication의 공식 completion denominator로 소비하고, 모든 member row를 `migrated`, `no-op`, `diagnostic-only`, `historical-only` 중 정확히 하나의 evidence-backed terminal disposition으로 귀속한다.
* 현재 기준:

  * 공식 completion unit은 `executing_consumer_member_row`다.
  * unique path / semantic consumer object / source entry / runtime entry / accepted occurrence row / readiness mutation row는 completion unit이 아니다.
  * broad consumer universe, current cutover subset, readiness / sandbox subset은 서로 다른 denominator / lifecycle role로 남는다.
  * `1062`는 executing consumer universe denominator이고, `311`은 change-required audit subset이며, `163`은 readiness / sandbox actual mutation subset이다. 이 숫자들은 completion denominator로 서로 대체할 수 없다.
  * `59` / `252`는 `classified_ledger.jsonl`의 `change_needed_on_rebaseline == yes / conditional` predicate에 source-grounded된 값이며 terminal completion counts가 아니다.
  * `163 actual_apply_eligible`와 `163 readiness sandbox mutation`은 서로 다른 denominator IDs다. 둘의 관계는 row-identity match로만 잠그며 count-equality inference로 읽지 않는다.
  * bound universe는 `1062`이며 source predicate split은 `49 yes / 111 conditional / 902 no == 1062`로 고정한다.
  * terminal split은 `migrated=153`, `no-op=268`, `diagnostic-only=3`, `historical-only=638`, `blocked=0`, `conditional=0`, `unknown=0`, `pending=0`이다.
  * `153 migrated`는 readiness / cutover row evidence와 actual diff-to-ledger mapping을 가진 terminal projection이며, live migration completion이나 new cutover authorization이 아니다.
  * `actual_apply_eligible`와 readiness sandbox mutation은 그 자체만으로 `migrated` evidence가 아니며, positive row-level evidence class를 필요로 한다.
  * `902` audit-only bound members는 migration evidence 부재가 아니라 Gate A/B classification, executing route, classified ledger join, allowed audit terminal reason으로 terminalized된다.
  * Consumer Universe Denominator Lock은 live `Iris/_docs/round3/current_route_required_validations.json`에 required artifact / required test로 채택됐다.
  * denominator required gate status는 `adopted_required_gate`이며, denominator final report는 `complete_claim_allowed=true`, `future_closeout_blocking_claim_allowed=true`, `canonical_seal_allowed=false`, `governance_closeout_status=review_pending`으로 읽는다.
  * denominator required gate adoption은 future closeout에서 denominator misuse를 fail-closed로 막기 위한 live current-route validation이며, independent review나 canonical seal을 대체하지 않는다.
  * closeout state는 `canonical_complete`이고 independent review status는 `review_pass`다.
  * owner adoption status와 independent review status는 별도 필드이며, owner adoption은 independent review를 대체하지 않는다.
* 최소 결과 trace:

  * denominator generator / validator / claim guard validator / focused unittest: `PASS`
  * denominator live required manifest: `required_artifacts=14`, `required_tests=23`, denominator artifact/test present
  * denominator required gate: `adopted_required_gate / future_closeout_blocking_claim_allowed=true`
  * denominator broad current-route validation: `FAIL / existing source-overlay route blocker`
  * denominator broad current-route failure는 `CURRENT_FACTS=6` vs `2105` 및 `Base.CanOpener`의 missing `body_source_overlay` 문제이며, denominator-scope widening 근거가 아니다.
  * terminal adjudication generation / complete validator / focused unittest: `PASS`
  * terminal focused unittest: `PASS / 12 tests`
  * protected surface no-mutation: `PASS / changed_count 0`
  * independent review: `PASS / reviewed artifacts 19 / hash seal PASS / stable artifact hash mismatch hard-fail maintained`
  * terminal hash closure: `promotion_rewritten_count=5`, `self_referential_attestation_count=1`, `validation_rewritten_attestation_count=1`, `error_count=0`
* 후속 input artifact:

  * denominator evidence root: `Iris/build/description/v2/staging/consumer_universe_denominator_lock/`
  * denominator plan: `docs/consumer_universe_denominator_lock_plan.md`
  * denominator ledger packet: `docs/consumer_universe_denominator_lock_ledger_packet.md`
  * denominator final report: `Iris/build/description/v2/staging/consumer_universe_denominator_lock/phase8/final_consumer_universe_denominator_lock_report.json`
  * terminal evidence root: `Iris/build/description/v2/staging/dvf_3_3_terminal_disposition_adjudication/`
  * terminal plan: `docs/dvf_3_3_terminal_disposition_adjudication_plan.md`
  * terminal policy: `docs/dvf_3_3_terminal_disposition_policy.md`
  * terminal claim boundary: `docs/dvf_3_3_terminal_disposition_claim_boundary.md`
  * terminal ledger packet: `docs/dvf_3_3_terminal_disposition_ledger_packet.md`
  * terminal final report: `Iris/build/description/v2/staging/dvf_3_3_terminal_disposition_adjudication/phase5/final_terminal_disposition_machine_report.json`
  * terminal independent review report: `Iris/build/description/v2/staging/dvf_3_3_terminal_disposition_adjudication/phase6/independent_review_artifact_hash_report.json`
* 오독 금지:

  * 이 항목은 terminal disposition adjudication의 canonical completion만 승인한다.
  * 이 항목은 consumer migration, current authority cutover, runtime / source / rendered / package mutation을 승인한 것이 아니다.
  * 이 항목은 release readiness, package release readiness, Workshop readiness, B42 readiness, deployment readiness, manual in-game QA, semantic quality completion을 승인한 것이 아니다.
  * `153 migrated`를 live migration execution count나 new cutover authorization으로 읽지 않는다.
  * denominator required-validation adoption은 live required validation gate 채택으로 읽되, 그 효과는 denominator misuse 방지와 future closeout blocking에 한정한다.
  * denominator required-validation adoption을 terminal disposition, consumer migration execution, current authority cutover, runtime mutation, release readiness로 읽지 않는다.
  * `311`, `1062`, `163`, `148`, `27558`, `59`, `252`, `2105`, `2084`, `21`은 서로 다른 denominator / axis / lifecycle role로만 읽는다.
  * broad current-route failure를 denominator lock 실패나 denominator 확장 근거로 읽지 않는다.
  * COMMON-RELEASE-NONDECISION.
  * COMMON-RUNTIME-SURFACE-NONMUTATION.
* Predecessor trace:

  * Denominator Governance staged: prior denominator lock round
  * Terminal Disposition Adjudication consumed Denominator Governance의 `1062` executing-consumer member-row universe
  * `311`, `163`, readiness sandbox mutation, actual_apply_eligible, audit-only counts는 terminal completion denominator를 대체하지 않는다.
  * closeout, focused test, command 전문, 세부 hash report는 `COMMON-EVIDENCE-TRACE`로 흡수한다.

### Iris DVF 3-3 — shared disposition consumption / current-route source-overlay boundary

* 상태: shared disposition guard complete adopted / live required-validation gate adopted / current-route baseline-source-overlay repair PASS / closeout-reentry guard pending
* 결정: Shared Disposition Ledger Consumption은 terminal disposition, denominator identity, lifecycle role, provenance / readiness role을 하나의 shared disposition packet / report surface로 소비하는 live required-validation guard로 채택한다. Raw audit / readiness / dry-run / predecessor artifacts는 provenance evidence일 뿐 실행 authority가 아니다.
* 현재 기준:

  * live `Iris/_docs/round3/current_route_required_validations.json`은 shared disposition final report, divergence report, raw authority read report, value divergence report, predecessor reentry report, no-dual-authority-read report, protected-surface no-mutation report를 required artifact로 요구한다.
  * live manifest는 focused shared disposition unittest를 required test로 요구한다.
  * shared final report는 `status=PASS`, `closeout_state=complete_adopted`, `current_route_required_validation_adoption_state=adopted_required_gate`, `owner_adoption_status=adopted_required_gate`로 읽는다.
  * candidate manifest는 `superseded_by_live_required_gate`로 남기며, live manifest를 대체하는 authority가 아니다.
  * raw audit / readiness / dry-run / predecessor artifact를 직접 실행 authority로 읽는 surface는 `RAW_AUTHORITY_READ=0`, `DUAL_AUTHORITY_READ=0`이어야 한다.
  * shared guard는 `VALUE_DIVERGENCE=0`, `PREDECESSOR_REENTRY=0`, protected source / rendered / Lua / runtime / package mutation `changed_count=0`을 요구한다.
  * `adopted_required_gate`는 governance manifest adoption 상태다. compose / runtime failure의 `adopted item`은 current runtime row vocabulary이며 QG 용어가 아니다.
  * 이전 full current-route 실패인 `CURRENT_FACTS=6` vs `2105` 및 runtime-adopted `Base.CanOpener` missing `body_source_overlay`는 shared disposition 실패가 아니라 별도 Current-Route Baseline / Source-Overlay Repair 문제였으며, 해당 repair는 별도 evidence packet과 full current-route validation PASS로 닫혔다.
* 최소 결과 trace:

  * shared evidence root: `Iris/build/description/v2/staging/dvf_3_3_shared_disposition_ledger_consumption/`
  * shared final report: `Iris/build/description/v2/staging/dvf_3_3_shared_disposition_ledger_consumption/phase7/final_shared_disposition_consumption_report.json`
  * shared policy: `docs/dvf_3_3_shared_disposition_consumption_policy.md`
  * shared claim boundary: `docs/dvf_3_3_shared_disposition_claim_boundary.md`
  * shared ledger packet: `docs/dvf_3_3_shared_disposition_ledger_packet.md`
  * focused generation / validation: `PASS`
  * focused unittest: `PASS / 7 tests`
  * shared live gate contribution: `required_artifacts=7`, `required_tests=1`
* 오독 금지:

  * 이 항목은 terminal re-adjudication, denominator redefinition, live migration execution, current authority cutover, runtime / source / rendered / package mutation을 승인하지 않는다.
  * 이 항목은 release readiness, package readiness, Workshop readiness, B42 readiness, deployment readiness를 선언하지 않는다.
  * sandbox / readiness evidence를 live completion으로 세지 않는다.
  * raw audit / readiness / dry-run / predecessor artifact를 실행 authority로 승격하지 않는다.
  * 이전 full current-route runner 실패를 shared disposition incompletion이나 old 2105 baseline 재채택 근거로 읽지 않는다.
* 후속 문제:

  * Current-Route Baseline / Source-Overlay Repair는 닫혔지만 Closeout / Reentry Guard Seal은 별도 문제로 남는다.
  * Closeout / Reentry Guard Seal의 범위는 broad completion과 cutover subset completion 문구 분리, predecessor `2105 / 2084 / 21`의 current hard gate / runtime authority / current debt 재진입 방지다.

### Iris DVF 3-3 — current-route baseline / source-overlay repair

* 상태: Problem 7 repair sealed / full current-route validation PASS / Problem 8 closeout-reentry guard pending
* 결정: Current-Route Baseline / Source-Overlay Repair는 `docs/dvf_3_3_current_route_baseline_source_overlay_repair_problem7_plan.md`를 canonical `primary_problem7_plan`으로, 기존 `docs/dvf_3_3_current_route_baseline_source_overlay_repair_plan.md`를 execution authority가 없는 `predecessor_contract_plan`으로 분리해 소비한다. 이 repair는 terminal disposition 재판정, denominator 재정의, shared disposition 재채택이 아니라 current-route build surface가 vNext baseline / source-overlay contract를 일관되게 소비하도록 정렬한 것이다.
* 현재 기준:

  * `primary_problem7_plan`만 본 문제의 canonical plan이며 `predecessor_contract_plan`은 supporting contract / predecessor context로만 읽는다.
  * `CURRENT_FACTS=6`은 full current-route universe expectation으로 쓰지 않는다. vNext `2105` row universe는 current-route build validation의 source / overlay / rendered / runtime evidence contract로 소비하되 old predecessor authority 복구나 current debt로 재진입하지 않는다.
  * runtime-adopted current-route compose 대상 row는 `body_source_overlay`를 요구하며, source / overlay / compose / current-authority / Layer4 trace 계열은 같은 baseline/source-overlay contract를 소비한다.
  * stale predecessor anchor는 successor authority context 또는 stable non-apply context로 재바인딩한다. 이것은 row 재판정이 아니라 current checkout에서 anchor freshness를 유지하기 위한 downstream contract alignment다.
  * cutover tooling readiness의 actual diff-to-ledger mapping은 `163` mutation rows, mapped `163`, unmapped `0`, orphan `0`으로 닫힌다.
  * Layer4 trace는 diagnostic/readpoint/support role이며 current build/runtime hard namespace authority로 소비하지 않는다.
* 최소 결과 trace:

  * repair runner: `uv run python -B Iris\build\description\v2\tools\build\dvf_3_3_current_route_baseline_source_overlay_repair.py` / `PASS`
  * full current-route validation: `uv run python -B Iris\_docs\round3\round3_run_contract_tests.py --class current --enforce-current-build-closure` / `PASS / 103 tests`
  * current-route repair focused unittest: `PASS / 7 tests`
  * consumer migration input normalization focused unittest: `PASS / 9 tests`
  * cutover tooling readiness focused unittest: `PASS / 6 tests`
  * Layer4 absorption current-surface guard: `PASS`
  * repair final report: `closeout_state=partial`, `implementation_plan_ready=true`, `stable_plan_provenance=true`
* 오독 금지:

  * 이 항목은 live runtime / source / rendered / package mutation, release readiness, Workshop readiness, B42 readiness, deployment readiness, manual in-game QA를 승인하지 않는다.
  * 이 항목은 Terminal Disposition, Denominator Lock, Shared Disposition Ledger Consumption을 재개하거나 재채택하지 않는다.
  * 이 항목은 Closeout / Reentry Guard Seal 완료가 아니다. broad completion과 cutover subset completion 문구 분리, predecessor `2105` 재진입 guard 봉인은 별도 후속 문제로 남는다.

### Iris DVF 3-3 — closeout / reentry guard seal

* 상태: required-validation gate adopted / machine contract PASS / canonical seal PASS / closeout canonical complete
* 결정: Closeout / Reentry Guard Seal은 broad consumer completion, terminal disposition completion, cutover subset completion, pre-apply readiness, live apply authorization, live migration execution completion을 axis-qualified claim class로 분리하는 governance gate로 채택한다.
* 현재 기준:

  * 단독 `complete` claim은 허용하지 않는다. 모든 completion-bearing claim은 `terminal_disposition_complete`, `broad_consumer_completion`, `cutover_subset_completion`, `pre_apply_readiness_complete`, `phase4_live_apply_allowed`, `required_validation_gate_adopted`, `historical_predecessor_trace`, `source_overlay_repair_current_route_validation_pass`, `problem7_full_current_route_validation_pass` 같은 class로 축을 가져야 한다.
  * predecessor `2105 / 2084 / 21`은 historical predecessor trace, frozen comparison baseline, successor evidence contract denominator, migration provenance, terminal disposition provenance context에서만 허용한다.
  * predecessor `2105 / 2084 / 21`은 current hard gate, current runtime authority, package authority, release readiness, current debt, required migration target expansion, old chunks / monolith fallback, raw predecessor artifact direct execution authority read로 재진입할 수 없다.
  * Problem 7 full current-route validation PASS는 Problem 8 / Closeout Guard completion으로 승격되지 않는다.
  * live current-route required-validation manifest는 Closeout / Reentry Guard Seal의 taxonomy, predecessor guard, boundary guard, manifest adoption report, final no-mutation report, final seal report, independent review artifact hash report, focused unittest를 요구한다.
  * final guard report는 `machine_contract_status=PASS`, `closeout_state=canonical_complete`, `canonical_seal_allowed=true`, `independent_review_status=PASS`로 읽는다.
  * independent review artifact hash report는 `primary_review_artifact_count=17`, `primary_review_artifact_missing_count=0`, `status=PASS`, `canonical_seal_allowed=true`로 읽으며, final report / full current-route validation result / `validation_report.all.json` / claim surface scan manifest / claim surface inventory를 primary review bundle에 포함한다.
  * protected source / rendered / Lua bridge / runtime / package mutation count는 `0`이다.
  * current-route required gate는 `required_artifacts=28`, `required_tests=28`이며, approved successor pinned baseline은 `107` tests로 읽는다.
* 오독 금지:

  * 이 항목은 live migration execution, live mutation completion, current authority cutover, terminal disposition re-adjudication, denominator redefinition, package readiness, release readiness, Workshop readiness, B42 readiness, deployment readiness, manual in-game QA, semantic quality completion, public-facing text acceptance를 승인한 것이 아니다.
  * required-validation guard adoption은 governance-only이며 source / rendered / Lua bridge / runtime / package writer가 아니다.
  * owner adoption status는 independent review를 대체하지 않는다. 이 round의 canonical seal은 non-Claude independent review PASS와 hash-sealed primary review bundle을 근거로만 선언한다.

### Iris DVF 3-3 — current source authority drift verification / recovery scope retirement

* 상태: read-only verification sealed / recovery live-write scope retired / independent review PASS / owner seal PASS / canonical retirement seal PASS
* 결정: Current Source Authority Drift Verification / Recovery Scope Retirement round는 stale `CURRENT_FACTS=6 != 2105` premise를 현재 checkout 기준으로 폐기하고, source restoration이 아니라 successor current source authority 소비 경로 검증과 stale Recovery live-write scope retirement로 닫는다.
* 현재 기준:

  * vNext successor source manifest는 `successor_current_source_authority`를 선언하며, current baseline identity는 `dvf_3_3_vnext_current_authority_implementation_2105_consumer_migration`이다.
  * current `facts / decisions / overlay_support`는 모두 successor `2105` row identity와 count/hash가 일치한다. 여기서 `2105`는 old predecessor recovery target이 아니라 vNext successor universe count다.
  * direct current compose는 sandbox output sink에서 실행되며 live rendered/source/runtime/package writer sink를 열지 않는다.
  * direct current compose evidence는 `2105` entries, live rendered hash parity, missing overlay `0`으로 읽는다.
  * `Base.CanOpener` 같은 6-entry predecessor fixture/source payload는 current-looking source / rendered / runtime / package path로 재진입하지 않는다.
  * predecessor `2105 / 2084 / 21`은 historical / diagnostic / fixture trace로만 남으며 current authority, current hard gate, runtime authority, package authority, current debt로 승격하지 않는다.
  * 기존 Current Source Authority Drift Recovery live-write plan은 현재 실행 근거가 아니라 future drift가 새로 증명될 때만 열 수 있는 contingency로 격하한다.
  * primary review artifact manifest는 full evidence inventory `49` artifacts를 포함하며 missing count는 `0`이다.
  * independent review artifact hash report는 frozen hash 비교 `45`, comparison-exempt artifact `4`, mismatch `0`으로 닫힌다. self hash row는 `self_hash_not_representable_presence_only`로 분리한다.
  * final report는 `closeout_state=current_source_authority_drift_verification_recovery_scope_retirement_canonical_pass`, `canonical_retirement_seal_allowed=true`, `independent_review_status=PASS`, `owner_seal_status=PASS`로 읽는다.
* 최소 결과 trace:

  * evidence root: `Iris/build/description/v2/staging/dvf_3_3_current_source_authority_drift_verification_recovery_scope_retirement/`
  * plan: `docs/dvf_3_3_current_source_authority_drift_verification_recovery_scope_retirement_plan.md`
  * claim boundary: `docs/dvf_3_3_current_source_authority_drift_verification_claim_boundary.md`
  * ledger packet: `docs/dvf_3_3_current_source_authority_drift_verification_ledger_packet.md`
  * final report: `Iris/build/description/v2/staging/dvf_3_3_current_source_authority_drift_verification_recovery_scope_retirement/phase6/final_current_source_authority_drift_verification_report.json`
  * primary review manifest: `Iris/build/description/v2/staging/dvf_3_3_current_source_authority_drift_verification_recovery_scope_retirement/phase6/primary_review_artifact_manifest.json`
  * independent review hash report: `Iris/build/description/v2/staging/dvf_3_3_current_source_authority_drift_verification_recovery_scope_retirement/phase6/independent_review_artifact_hash_report.json`
  * focused generation/validation: `uv run python -B Iris\build\description\v2\tools\build\run_dvf_3_3_current_source_authority_drift_verification.py --mode all --require-complete` / `PASS`
  * focused validator: `uv run python -B Iris\build\description\v2\tools\build\validate_dvf_3_3_current_source_authority_drift_verification.py --require-complete` / `PASS`
  * focused unittest: `uv run python -B -m unittest discover -s Iris\build\description\v2\tests -p "test_dvf_3_3_current_source_authority_drift_verification*.py"` / `9 tests OK`
  * latest broad current-route rerun note: `uv run python -B Iris\_docs\round3\round3_run_contract_tests.py --class current --enforce-current-build-closure` was blocked by an unrelated `dvf_3_3_shared_disposition_ledger_consumption/phase2/shared_disposition_packet.json` Windows `OSError 22` write failure; this is not treated as source-authority drift evidence.
* 오독 금지:

  * 이 항목은 facts / decisions / overlay / rendered live write, source restoration, old predecessor recovery, current authority cutover, live migration execution completion, Lua bridge export, runtime chunk replacement, package readiness, release readiness, Workshop readiness, B42 readiness, deployment readiness, manual in-game QA, semantic quality completion, public-facing text acceptance를 승인한 것이 아니다.
  * current-route required-validation candidate는 live manifest adoption이 아니라 candidate / governance-only trace다.
  * Recovery plan retirement은 future drift contingency를 보존하는 것이며, 새 drift evidence 없이 live-write recovery scope를 다시 여는 근거가 아니다.

### Iris DVF 3-3 — current-route required validation / evidence freshness reseal

* 상태: required-validation evidence freshness resealed / live manifest consumed / external bundle fresh / independent review PASS / owner seal PASS / canonical complete
* 결정: Current-Route Required Validation / Evidence Freshness Reseal round는 current checkout의 runner, live `Iris/_docs/round3/current_route_required_validations.json`, stored drift evidence, and round-local external validation bundle을 하나의 fresh readpoint로 다시 묶는 governance-only validation seal로 채택한다.
* 현재 기준:

  * final report는 `required_validation_gate_adopted=true`, `evidence_freshness_reseal_closeout_state=complete`, `machine_contract_status=PASS`, `canonical_complete_allowed=true`, `independent_review_status=PASS`, `owner_seal_status=PASS`로 읽는다.
  * current-route command는 `uv run python -B Iris\_docs\round3\round3_run_contract_tests.py --class current --enforce-current-build-closure` 기준 `PASS / 110 tests / closure_enforced true`다.
  * live required-validation manifest는 reseal round의 fresh drift-consumption, current source identity redrive, live manifest additive update, taxonomy separation, current-route freshness, external bundle freshness, and final seal evidence를 required artifacts로 소비한다.
  * live manifest의 reseal required tests는 pre-phase5/phase6 current-route surfaces only로 제한한다. post-run external bundle / final report checks는 wrapper final validation과 focused unittest surface에서 검증하며 current-route PASS test count로 과장하지 않는다.
  * external validation bundle은 fresh current-route run, live manifest hash, evidence root, and normalized content hash contract를 반영하며 `bundle_normalized_hash_matches_manifest=true`다.
  * negative fixture matrix는 stale bundle, skipped required test, failed artifact field check를 sandbox runner로 fail-closed 검증하고, candidate manifest override는 official reseal wrapper CLI surface에서 거부한다.
  * primary review artifact manifest는 `45` artifacts를 포함하며 missing count는 `0`이다. independent review artifact hash report는 frozen hash comparison `43`, comparison-exempt artifact `2`, mismatch `0`, `canonical_complete_allowed=true`로 닫힌다.
  * owner seal report는 `owner_seal_status=PASS`, `owner_seal_decision=approve_required_validation_gate_adopted_evidence_freshness_reseal_complete`, `direct_runner_candidate_rejection_requirement=not_required_for_this_seal`로 읽는다.
* 최소 결과 trace:

  * evidence root: `Iris/build/description/v2/staging/dvf_3_3_current_route_required_validation_evidence_freshness_reseal/`
  * plan: `docs/dvf_3_3_current_route_required_validation_evidence_freshness_reseal_plan.md`
  * claim boundary: `docs/dvf_3_3_current_route_required_validation_evidence_freshness_reseal_claim_boundary.md`
  * ledger packet: `docs/dvf_3_3_current_route_required_validation_evidence_freshness_reseal_ledger_packet.md`
  * final report: `Iris/build/description/v2/staging/dvf_3_3_current_route_required_validation_evidence_freshness_reseal/phase6/final_current_route_required_validation_evidence_freshness_reseal_report.json`
  * owner seal report: `Iris/build/description/v2/staging/dvf_3_3_current_route_required_validation_evidence_freshness_reseal/phase6/owner_seal_report.json`
  * primary review manifest: `Iris/build/description/v2/staging/dvf_3_3_current_route_required_validation_evidence_freshness_reseal/phase6/primary_review_artifact_manifest.json`
  * independent review hash report: `Iris/build/description/v2/staging/dvf_3_3_current_route_required_validation_evidence_freshness_reseal/phase6/independent_review_artifact_hash_report.json`
  * focused generation/validation: `uv run python -B Iris\build\description\v2\tools\build\run_dvf_3_3_current_route_required_validation_evidence_freshness_reseal.py --mode all` / `PASS`
  * focused validator: `uv run python -B Iris\build\description\v2\tools\build\validate_dvf_3_3_current_route_required_validation_evidence_freshness_reseal.py --require-complete` / `PASS`
  * focused unittest: `uv run python -B -m unittest discover -s Iris\build\description\v2\tests -p "test_dvf_3_3_current_route_required_validation_evidence_freshness_reseal.py"` / `5 tests OK`
* 오독 금지:

  * 이 항목은 release readiness, package readiness, Workshop readiness, B42 readiness, deployment readiness, manual in-game QA, semantic quality completion, public-facing text acceptance, live migration execution, source restoration, rendered regeneration, Lua bridge export, runtime chunk replacement, or package payload mutation을 승인한 것이 아니다.
  * required-validation reseal은 governance-only validation seal이며 source / rendered / Lua bridge / runtime / package writer authority가 아니다.
  * direct `round3_run_contract_tests.py --required-validations` override surface는 sandbox fail-closed fixture용 harness 기능이다. 이번 seal의 candidate manifest guard는 official reseal wrapper가 required-validation manifest override를 받지 않는다는 보증으로 한정한다.

### Iris DVF 3-3 — current source authority drift verification / adoption reseal

* 상태: Branch A required gate adopted / governance-only adoption reseal complete / independent review PASS / owner seal PASS / canonical complete
* 결정: Current Source Authority Drift Verification / Adoption Reseal round는 sealed drift verification PASS와 Evidence Freshness Reseal의 live-manifest consumption을 current-route required-validation governance chain의 하나의 fresh readpoint로 재봉인한다.
* 현재 기준:

  * selected branch는 `branch_a_required_gate_adopted`이며, final closeout은 `current_source_authority_drift_adoption_reseal_complete`다.
  * sealed-reseal/live-manifest re-derivation은 PASS이며, live manifest는 drift evidence를 Evidence Freshness Reseal required gate를 통해 소비한다.
  * direct drift adoption과 evidence-freshness drift-consumption은 구분되어 있고, Branch B / B-marked marker path는 `not_applicable_selected_branch_a`로 닫힌다.
  * taxonomy는 live required manifest union surface를 통해 소비하며, 이번 round에서는 `non_writer_required_manifest_union`으로 기록한다.
  * live required-validation manifest는 adoption reseal artifacts/tests를 additive로 채택했고, 기존 required artifact/test removal 또는 modification은 `0`이다.
  * current-route validation은 `PASS / 113 tests / closure_enforced true`로 읽는다.
  * final report는 `status=PASS`, `machine_contract_status=PASS`, `canonical_complete_allowed=true`, `independent_review_status=PASS`, `owner_seal_status=PASS`로 닫힌다.
  * primary review artifact manifest는 `37` artifacts를 포함하며 missing count는 `0`이다. independent review artifact hash report는 frozen hash comparison `33`, comparison-exempt artifact `4`, mismatch `0`으로 닫힌다.
  * final report는 `clean_checkout_reproducibility_proof_status=out_of_scope_not_claimed`, `original_required_evidence_reproducibility_preflight_status=not_closed_by_this_plan`을 보존한다.
* 최소 결과 trace:

  * evidence root: `Iris/build/description/v2/staging/dvf_3_3_current_source_authority_drift_verification_adoption_reseal/`
  * plan: `docs/dvf_3_3_current_source_authority_drift_verification_adoption_reseal_plan.md`
  * claim boundary: `docs/dvf_3_3_current_source_authority_drift_verification_adoption_reseal_claim_boundary.md`
  * ledger packet: `docs/dvf_3_3_current_source_authority_drift_verification_adoption_reseal_ledger_packet.md`
  * final report: `Iris/build/description/v2/staging/dvf_3_3_current_source_authority_drift_verification_adoption_reseal/phase6/final_current_source_authority_drift_verification_adoption_reseal_report.json`
  * owner seal report: `Iris/build/description/v2/staging/dvf_3_3_current_source_authority_drift_verification_adoption_reseal/phase6/owner_seal_report.json`
  * primary review manifest: `Iris/build/description/v2/staging/dvf_3_3_current_source_authority_drift_verification_adoption_reseal/phase6/primary_review_artifact_manifest.json`
  * independent review hash report: `Iris/build/description/v2/staging/dvf_3_3_current_source_authority_drift_verification_adoption_reseal/phase6/independent_review_artifact_hash_report.json`
  * focused generation/validation: `uv run python -B Iris\build\description\v2\tools\build\run_dvf_3_3_current_source_authority_drift_verification_adoption_reseal.py --mode all` / `PASS`
  * focused validator: `uv run python -B Iris\build\description\v2\tools\build\validate_dvf_3_3_current_source_authority_drift_verification_adoption_reseal.py --require-complete` / `PASS`
  * focused unittest: `uv run python -B -m unittest discover -s Iris\build\description\v2\tests -p "test_dvf_3_3_current_source_authority_drift_verification_adoption_reseal.py"` / `4 tests OK`
  * full current route: `uv run python -B Iris\_docs\round3\round3_run_contract_tests.py --class current --enforce-current-build-closure` / `PASS / 113 tests / closure_enforced true`
* 오독 금지:

  * 이 항목은 source restoration, old predecessor recovery, current authority cutover, live migration execution, rendered regeneration, Lua bridge export, runtime chunk replacement, package payload mutation, release readiness, Workshop readiness, B42 readiness, deployment readiness, manual in-game QA, semantic quality completion, public-facing text acceptance를 승인한 것이 아니다.
  * 이 adoption reseal은 plan-structure PASS를 empirical verification of manifest / taxonomy / tracking / `2105` / `OSError 22` state로 과장하지 않는다.
  * clean-checkout required evidence reproducibility / taxonomy disposition preflight는 이 round에서 닫지 않는다.

### Iris DVF 3-3 — live migration readiness authorization / execution seal

* 상태: pre-apply authorization sealed / execution readiness evidence sealed / Phase 4 live apply allowed / no live mutation executed
* 결정: Terminal Disposition Adjudication의 `migrated=153` consumer projection은 live migration completion이 아니라 Phase 4 live apply 실행 라운드를 열 수 있는 pre-apply authorization / execution-readiness input으로만 소비한다.
* 현재 기준:

  * final verdict는 `phase4_live_apply_allowed=true`, `downstream_predecessor_status=ready_for_phase4_live_apply`, `closeout_state=complete`다.
  * row taxonomy는 `153 = 109 live_mutation_eligible + 44 evidence_only + 0 blocked`로 봉인한다.
  * dry-run patch bundle은 `109` live mutation eligible row와 정확히 일치하며, `44` hard-forbidden runtime / package / Lua bridge row는 successor source / rendered / authority proof가 있는 evidence-only row로 내린다.
  * dirty target overlap은 VCS baseline commit과 isolation proof로 fail-closed blocker에서 해소했다. 남은 dirty overlap은 `dirty_isolated_non_overlap=true`인 isolated non-overlap으로만 허용한다.
  * live writer capability는 no-write probe 기준 `changed_count=0`, `live_repo_mutated=false`를 요구한다.
  * execution-readiness evidence는 `Iris/build/description/v2/staging/dvf_3_3_live_migration_readiness_execution/` 아래 `phase0`부터 `phase10`까지의 pre-apply gate artifacts로 materialize한다.
  * execution runner는 authorization verdict를 재해석하거나 live apply를 수행하지 않고, execution plan이 요구한 canonical evidence root / artifact names / validation surface로 투영한다.
  * execution writer identity contract는 dry-run mode와 mirror apply mode가 sink-only 차이를 가진다는 전제를 봉인하며, 이 round의 `live_apply_mode`는 `disabled`다.
  * final authorization은 execution plan seal과 review gate를 함께 요구하며, 현재 seal은 `execution_plan_review_status=sealed`, `review_gate_kind=external_gate`, `review_gate_pass=true`, `reviewed_artifact_hash_coverage=complete`다.
  * roadmap provenance SHA 비교는 hex case-insensitive normalization으로 판정한다.
* 최소 결과 trace:

  * canonical plan: `docs/dvf_3_3_live_migration_readiness_authorization_plan.md`
  * canonical execution plan: `docs/dvf_3_3_live_migration_readiness_execution_plan.md`
  * evidence root: `Iris/build/description/v2/staging/dvf_3_3_live_migration_readiness_authorization/`
  * execution evidence root: `Iris/build/description/v2/staging/dvf_3_3_live_migration_readiness_execution/`
  * final report: `Iris/build/description/v2/staging/dvf_3_3_live_migration_readiness_authorization/phase10_final_authorization/final_live_migration_readiness_authorization_report.json`
  * execution final report: `Iris/build/description/v2/staging/dvf_3_3_live_migration_readiness_execution/phase10/final_live_migration_readiness_report.json`
  * execution final authorization verdict: `Iris/build/description/v2/staging/dvf_3_3_live_migration_readiness_execution/phase10/final_live_apply_authorization_verdict.json`
  * evidence manifest: `Iris/build/description/v2/staging/dvf_3_3_live_migration_readiness_authorization/phase10_final_authorization/pre_apply_authorization_evidence_manifest.json`
  * execution evidence manifest: `Iris/build/description/v2/staging/dvf_3_3_live_migration_readiness_execution/phase10/pre_apply_authorization_evidence_manifest.json`
  * focused validation: `uv run python -B Iris\build\description\v2\tools\build\run_dvf_3_3_live_migration_readiness_authorization.py --mode all` / `PASS`
  * focused unittest: `uv run python -B -m unittest discover -s Iris\build\description\v2\tests -p "test_live_migration_readiness_authorization.py"` / `7 tests OK`
  * execution focused validation: `uv run python -B Iris\build\description\v2\tools\build\run_dvf_3_3_live_migration_readiness_execution.py --mode all` / `PASS`
  * execution focused validator: `uv run python -B Iris\build\description\v2\tools\build\validate_dvf_3_3_live_migration_readiness_execution.py --require-complete` / `PASS`
  * execution focused unittest: `uv run python -B -m unittest discover -s Iris\build\description\v2\tests -p "test_live_migration_readiness_execution.py"` / `5 tests OK`
  * execution direct docs: `docs/dvf_3_3_live_migration_readiness_policy.md`, `docs/dvf_3_3_live_migration_readiness_claim_boundary.md`, `docs/dvf_3_3_live_migration_readiness_ledger_packet.md`
  * dirty baseline trace: commit `1a29a00 Track round3 evidence baseline files`
* 오독 금지:

  * 이 항목은 Phase 4 live apply 실행 허가만 봉인한다.
  * 이 항목은 live migration execution, live mutation completion, release readiness, package readiness, Workshop readiness, B42 readiness, deployment readiness를 선언하지 않는다.
  * sandbox/readiness mutation, dry-run patch bundle, no-write probe, evidence-only proof는 live completion으로 세지 않는다.
  * hard-forbidden surface는 live mutation target이 아니며, origin proof가 없으면 evidence-only로도 내릴 수 없다.
  * execution evidence root의 phase artifacts는 pre-apply readiness evidence이며 source / rendered / Lua bridge / runtime / package authority가 아니다.

### Iris DVF 3-3 — subordinate readpoint / current-vs-historical contract split

* 상태: final current readpoint / subordinate DVF-system reconciliation chain / closed current test contract split
* 결정: Layer4, Structural Signal, ACQ_DOMINANT, Acquisition Lexical은 독립 모듈 family가 아니라 Iris DVF 3-3 시스템 내부의 subordinate current readpoint / authority / stale artifact / docs-governance reconciliation 문제로 묶는다. description-v2 `tools.build`의 current test contract는 historical reproduction / diagnostic surface와 분리한다.
* 최종 current readpoint:

  * 최종 subordinate readpoint는 `Iris DVF 3-3 Acquisition Lexical inventory readpoint reconciled`다.
  * `Iris DVF 3-3 Acquisition Lexical Current Inventory / Readpoint Audit Round`는 Branch D input readpoint로 닫고, 이를 소비한 `Acquisition Lexical Current Readpoint Reconciliation Round`는 `closed_with_acquisition_lexical_current_readpoint_reconciled`로 닫는다.
  * 선행 inventory readpoint를 입력으로 top-doc closeout, lower / current plan, stale predecessor artifacts, validator / utility support의 current-vs-historical read order를 하나로 정렬한다.
* 현재 기준:

  * Acquisition Lexical의 schema / source / utility / validator / tool / test / doc / stale-plan surface는 current checkout 기준 분류 readpoint를 가진다.
  * 과거 suppress 의존 문구는 current blocker가 아니라 historical / stale premise로 읽는다.
  * live suppress validator surface `3`은 current blocker나 resolved state가 아니라 별도 `followup_disposition_candidate`로 남긴다.
  * Structural Signal 계열은 observer-only scope separation, occurrence authority classification, docs-only readpoint absorption 순서로 닫힌 subordinate observer-only readpoint다.
  * ACQ_DOMINANT는 current readpoint 기준 publish writer input, runtime input, quality input, default compose input, source-row writer input, blanket isolation candidate가 아니다.
  * Layer4 current corpus lock과 confirmed measurement disposition은 current locked corpus 기준의 후속 측정 전제와 measurement disposition으로만 읽는다.
  * 과거 Layer4 zero-count는 historical predecessor readpoint이며 current count로 직접 승계하지 않는다.
  * `confirmed_count = 24`는 detector-execution measurement readpoint input으로만 소비한다.
  * `LAYER4_ABSORPTION_CONFIRMED`는 `FUNCTION_NARROW / ACQ_DOMINANT` disposition row가 아니라 independent `layer_boundary_hard_block_namespace`로 읽는다.
  * M1 confirmed count와 M2 application target axis는 값 상속 관계를 갖지 않는다.
  * M2 basis absence는 `application_target_measurement_unavailable`로 fail-loud 기록되며, current target value나 `0` reseal로 읽지 않는다.
  * default current contract route는 `python -B Iris/_docs/round3/round3_run_contract_tests.py --class current --enforce-current-build-closure`다.
  * current route는 12-module active build closure로 guard된다.
  * DVF VCS Tracking Policy addendum 이후 current route는 `57 tests / OK / closure_enforced true`이며, 12-module active build closure는 유지된다.
  * `current_route_allowed_tooling_modules`는 current core와 분리된 regeneration tooling import allowlist다.
  * 해당 allowlist는 현재 `export_dvf_3_3_lua_bridge` 1개 module만 허용하며, current core count `12`와 tooling allowlist cap `1`을 guard한다.
  * `test_compose_layer3_text_overlay.py`는 current composer 동작 검증으로 manual audit promotion 처리한다.
  * `test_compose_entrypoint_guard_hardening.py`는 compose current write-boundary guard 검증으로 current / historical taxonomy에 반영한다.
  * historical route와 diagnostic route는 current route와 별도 실행·판정한다.
  * disposition은 non-destructive only다: `12 current core`, `173 historical reproduction`, `95 diagnostic advisory`, `1 manifest-only retained`, `archive/delete eligible 0`.
  * D3 historical preservation policy는 `pass_required`이며, sealed historical route는 현재 pass 상태다.
  * full historical artifact byte reproducibility는 fail-loud unresolved 상태이며, current route completion으로 대체하지 않는다.
* 최소 결과 trace:

  * Acquisition Lexical logical surfaces classified: `507 / 507`
  * Acquisition Lexical raw occurrence total: `8828`
  * Acquisition Lexical read-state coverage: `100%`
  * Acquisition Lexical adversarial review: `PASS`
  * live suppress validator surface count: `3 / followup_disposition_candidate`
  * ACQ_DOMINANT occurrence_count: `1283`
  * ACQ_DOMINANT publish_candidate_count: `0`
  * Layer4 confirmed_count: `24 / readpoint-only`
  * current route: `PASS / 57 tests / closure_enforced true / 12-module active build closure`
  * historical route: `PASS / separated route`
  * diagnostic route: `PASS / separated route`
  * package gate: `PASS`
  * archive/delete execution: `no-op / archive-delete eligible 0`
  * non-destructive disposition: `archive/delete eligible 0`
  * full historical byte reproducibility: `unresolved / fail-loud`
* 후속 input artifact:

  * current route closeout: `Iris/_docs/round3/round3_closeout_report.md`
  * closure addendum: `Iris/_docs/round3/round3_active_core_closure.json`
  * related policy: `docs/dvf_vcs_tracking_policy.md`
* 오독 금지:

  * 이 항목은 acquisition lexical wording improvement, suppress retirement / removal, current suppress validator surface disposition execution, acquisition contract expansion을 승인한 것이 아니다.
  * 이 항목은 `josa_adaptive`, phrasebook, array acquisition, runtime-side repair opening을 승인한 것이 아니다.
  * 이 항목은 Layer4 absorption resolved, semantic quality completion, publish mutation review opened, source / rendered / runtime / state mutation을 승인한 것이 아니다.
  * 이 항목은 Browser / Wiki / Tooltip public exposure, runtime rollout, manual in-game validation, deployment / Workshop / B42 / release readiness, coverage / quality / completion remeasurement를 승인한 것이 아니다.
  * 승인되지 않은 source / rendered / runtime / package / build current surface 소비는 fail-fast 대상이다.
  * 이 항목은 test move, destructive archive/delete, runtime equivalence, in-game manual QA, Workshop publication readiness를 승인한 것이 아니다.
  * 이 항목은 full historical artifact byte reproducibility, universal deletion safety, reviewed scope 없는 current-route tooling allowlist 확장을 승인한 것이 아니다.
  * `current_route_allowed_tooling_modules`는 current core list의 우회 확장면이 아니다.
  * COMMON-RELEASE-NONDECISION.
  * COMMON-RUNTIME-SURFACE-NONMUTATION.
* Predecessor trace:

  * Structural Signal sequence sealed: 2026-05-29
  * ACQ_DOMINANT no-candidate closeout: 2026-05-30
  * Layer4 corpus / measurement / namespace readpoint chain: 2026-05-31 ~ 2026-06-03
  * Acquisition Lexical final readpoint reconciliation: 2026-06-05
  * Current / Historical / Diagnostic Test Contract Split closed: 2026-06-11
  * DVF VCS Tracking Policy addendum 이후 current route count는 `50`에서 `57`로 갱신해 읽는다.
  * 라운드별 closeout, command, hash, 세부 artifact path는 `COMMON-EVIDENCE-TRACE`로 흡수한다.

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
