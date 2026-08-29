# ARCHITECTURE.md

> 상태: 초안 v0.4  
> 기준일: 2026-08-10  
> 상위 기준: `Philosophy.md`, `DECISIONS.md`  
> 목적: Pulse 생태계의 구조 지도, 역할 경계, 의존 방향을 고정한다.  
> 구현 상태 표기: 별도 표시가 없는 모듈은 current architecture를 기술하며, `설계 단계` 표시는 아직 구현되지 않은 target architecture를 뜻한다.

---

# 1. 구조 원칙

## 1-1. 생태계 토폴로지

- **Hub**: Pulse Core
- **First-party Spokes**: Echo, Fuse, Nerve Pulse Adapter / Nerve+, Iris, Frame, Cortex, Canvas
- **First-party Standalone**: Nerve Core
- **External Consumers**: Pulse capability / API / SPI를 사용하는 외부 모드
- **Core surface**: SPI, capability, hook, state, DTO, event, registry, utility 등

Pulse Core는 범용 DataBus나 coordinator가 아니라, first-party Spoke와 외부 모드가 독립적인 제품 로직을 구성할 수 있도록 중립 capability surface를 제공하는 얇은 허브다.

First-party Spoke와 External Consumer는 Pulse Core의 consumer이며 서로를 경유하는 계층 관계를 형성하지 않는다. Nerve Core는 이 topology 밖에서 독립적으로 존재하며, Pulse 연동이 필요할 때 Nerve Pulse Adapter 또는 Nerve+를 통해 연결된다.

## 1-2. 관측 / 판단 / 정책 분리

공용 capability / SPI surface에는 **관측 가능한 사실과 상태**만 올릴 수 있으며, 그 사실을 어떻게 해석하고 어떤 조치를 취할지는 소비 모듈이 소유한다.

따라서 `targetId`, `category`, `magnitude`, `duration`, `sampleCount`, `spikeRatio`, `observedCost`, `frequency` 같은 관측값은 공유할 수 있지만, `severity`, `under pressure`, `priority`, `이 모듈이 처리해야 함`, `근거리면 FULL` 같은 해석·정책 신호는 공용 계약으로 승격하지 않는다.

특히 `severity`는 측정값처럼 보이더라도 우선순위나 개입 필요성을 내포할 수 있으므로 공용 observation surface에서는 사용하지 않는다. 필요한 경우 해당 모듈 내부의 local report label로만 유지한다.

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
- 거리 / 상태 / tick / phase 같은 중립적인 측정·상태 capability 제공
- 예외 격리, 진단, 로깅, DevMode 등 플랫폼 안정성 기능 제공

### 하지 않는 일

- first-party Spoke의 snapshot / update 주기를 호출하거나 통제하는 것
- 범용 모드 간 실시간 중개 채널이나 coordinator 역할을 소유하는 것

### 서비스 접근 구조

Pulse Core의 서비스 접근은 단일 주입 방식으로 강제하지 않는다.

- 생성자 주입, `PulseServices`, `ServiceLocator`와 제한적인 `getInstance()` fallback이 공존할 수 있다.

### EventBus 구조

EventBus의 class resolution은 세 단계의 경로를 사용한다.

1. **Direct class lookup**
   - 정상적인 기본 경로다.

2. **FQCN O(1) fallback**
   - direct lookup으로 해결되지 않는 경우 사용하는 이름 기반 호환 경로다.

3. **제한적 reflection / compatibility fallback**
   - 앞선 두 경로로 해결할 수 없는 경우에만 사용하는 최종 호환 경로다.

정상 실행은 direct lookup을 우선하며, fallback 경로는 정상 경로와 분리해 그 사용 범위와 비용을 제한한다.

Listener 저장은 가능한 한 단일 `CopyOnWriteArrayList`를 유지한다. 우선순위 정렬은 등록 시점의 `add + sort`에서 완료하고, fire 경로는 이미 정렬된 listener를 순회하는 단순한 경로로 유지한다.

---

## 2-2. Echo

### 정체성

병목 지점을 관찰하는 프로파일링 모드. Echo의 핵심 정체성은 `더 많이 재는 모드`가 아니라, **게임 실행을 흔들지 않는 순수 관측자**다.

### 하는 일

- tick / scope / spike / phase 등 병목 관찰에 필요한 계측
- 통계 수집
- 오버레이 / 리포트 / 관찰 결과 제공
- provider가 노출한 상태를 관측 가능한 형태로 기록
- 무개입 / 비활성 / 미등록 / 조회 실패 / 오류 같은 상태 차이를 리포트에서 구분 가능하게 남김
- 운영 경로를 흔들지 않는 방식으로 필요한 진단 정보를 수집

### 하지 않는 일

- 게임 동작 자체를 변경하는 것
- `0`, `inactive`, `missing`, `error` 같은 리포트 값을 임의의 정책 의미로 확정하는 것
- 운영 경로를 정밀 분석, 디버그, 무거운 context capture, 외부 서비스 조회의 기본 장소로 삼는 것

### 외부 계약

- Report 계열의 public 반환 계약은 `Map<String, Object>`를 유지한다.

---

## 2-3. Fuse

### 정체성

Mixin 기반 엔진 비용 질서화 / 안정화 모드.

Fuse의 기본 레인은 **동일 결과를 더 싸게 만드는 semantic-preserving 최소 개입**이다. 모든 상황에서 평균 FPS를 최대화하는 것이 아니라, 엔진 부하가 연쇄적으로 커져 게임이 오래 무너지는 상태를 줄이고 프레임타임 꼬리와 붕괴 순간을 완화한다.

Fuse는 AI 자체를 더 똑똑하게 만드는 모드가 아니라, AI 업데이트, 경로탐색, 충돌, 물리, 렌더, IO, GC 같은 엔진 비용 축에서 게임 규칙과 결과 의미를 유지한 채 비용 폭주를 완화하는 안정성 레이어다.

### 하는 일

- 엔진 레벨 병목 / 스파이크 완화
- 구조적 비용 절감
- 프레임타임 꼬리와 장시간 붕괴 상태 완화
- 의미 보존 가능한 범위에서 guard / limit / defer / deduplicate / stabilize 계열의 안전장치 적용
- 자기 pressure signal과 내부 상태를 기준으로 한 보수적 개입 판단
- fail-soft / backoff / retreat 기반의 안전한 철수
- 엔진 비용 축별로 개입 가능성과 책임 범위를 분리
- 직접 개입하기 어려운 비분할 stall이나 외부 원인성 freeze는 필요 시 관측 / 분류 / 설명 표면에 머무름

### 하지 않는 일

- 결과 의미가 달라질 수 있는 근사 / 공격적 알고리즘 교체를 기본 전략으로 삼는 것
- 모든 엔진 영역을 빠르게 만드는 거대 최적화 모드로 확장하는 것
- 모든 대형 freeze를 Fuse가 반드시 해결할 수 있다고 전제하는 것
- 지속 과부하에서 상시 개입을 유지해 잔렉을 상시화하는 것

---

## 2-4. Nerve

### 정체성

100% Lua 기반 **선택적 안정성 Guard**.

Nerve는 Lua 자체를 전면 최적화하는 모드가 아니라, Lua를 제어면으로 사용해 멀티 / 모드팩 / 이벤트 / UI / 네트워크 경계에서 발생할 수 있는 상위 레이어 지연과 충돌을 완충하는 모드다.

기본 방향은 `더 빠르게 만들기`가 아니라 **망가지기 쉬운 순간에 피해 반경을 줄이고, 위험하면 즉시 물러나는 것**이다. 따라서 Nerve는 필수 성능 모듈이 아니라 필요한 환경에서 선택적으로 켜는 안정성 레이어다.

### 하는 일

- 이벤트 디스패치 / 모드 훅 / UI / 인벤토리 / 네트워크 경계에서 발생하는 Lua 레벨 충돌과 작업 겹침 완충
- 멀티 / 모드팩 환경에서 선택적으로 사용할 수 있는 Lua control-plane 안전장치 제공
- 기본값 기준으로 바닐라와 동일한 의미 유지
- 위험 징후를 관측하고 필요 시 fail-soft / back-off / retreat 방식으로 피해 반경 제한
- same-tick 재진입, listener 예외, 중복 호출, 과도한 호출 연쇄 같은 Lua 레벨 자폭 징후 완화
- 의미 보존 가능한 범위에서 coalescing, guard, dirty flag, 읽기 전용 캐싱, incident-gated 보호 같은 보수적 기법 사용
- 운영상 필요한 최소 상태, 사건 표식, 에러 서명만 외부 표면에 노출

### 하지 않는 일

- 이벤트 우선순위 판단, 중요도 판단, 자동 scheduling / throttling 같은 정책 엔진으로 확장하는 것
- 지연 / 재정렬 / 병합 / drop처럼 결과 의미가 달라질 수 있는 개입을 기본화하는 것
- 전역 상시 보호 wrapper나 영구 차단을 기본 경로로 삼는 것
- 네트워크 경계를 다룬다는 이유로 ping 개선, packet 최적화, 서버 부하 분산 또는 엔진 동기화 수정 역할로 확장하는 것

### 계열 / 의존 경계

- **Nerve Core**: Pulse 비의존 Lua-only 안정성 코어. 독립 배포가 가능하며 안정성 핵심 로직과 내부 상태를 소유한다.
- **Nerve Pulse Adapter**: Nerve Core를 Pulse capability / SPI와 연결하는 선택적 연결층.
- **Nerve+**: Pulse 의존 기능과 운영 편의를 얹는 상위 오버레이. Nerve Core를 대체하는 상위 호환판이 아니다.

Pulse capability가 필요한 연동은 Nerve Core에 직접 의존성을 추가하지 않고 Nerve Pulse Adapter 또는 Nerve+ 경로에서 처리한다.

---

## 2-5. Iris

### 정체성

Iris는 오프라인에서 확정된 정보를 **정적 산출물로 유지하고, 런타임에서는 이를 렌더링하는 위키 시스템**이다.

### 하는 일

- 레시피, 우클릭 source, static capability 등 허용된 입력 정규화
- 외부 오프라인 생산 경로가 만든 fact / outcome 산출물 소비
- 표준 구조를 제공한 외부 모드 데이터를 Iris 입력 계약으로 정규화

### 하지 않는 일

- 표준 입력 계약을 제공하지 않은 외부 모드 데이터를 표시 문자열 해석이나 의미 추론으로 Iris 입력에 승격하는 것

### 정보 구조

Iris의 정보 모델은 다섯 층위로 구분한다.

1. **1계층 - 바닐라 툴팁 계층**
   - PZ가 기본 제공하는 아이템 정보로, Iris 정보가 놓이는 기준 정보층이다.

2. **2계층 - 주 소분류 / 카테고리 계층**
   - 아이템의 기본 탐색 의미와 브라우징 anchor를 제공한다.
   - `primary_subcategory`는 탐색 anchor로 유지하되, 상세 설명의 자동 생성 권한으로 승격하지 않는다.

3. **3계층 - 상세 설명 계층**
   - 아이템 중심의 위키형 상세 설명을 담당한다.

4. **4계층 - 상호작용 정보 계층**
   - 레시피, 우클릭 source, 요구조건, 사용 맥락 등 아이템과 연결된 상호작용 정보를 구조화한다.

5. **5계층 - 내부 정보 계층**
   - PZ 내부 아이템 정보와 Iris 내부 분류 / 처리 정보를 담는다.
   - 사용자 설명을 대신하지 않으며, 필요 시 별도의 메타 영역에 격리한다.

이 다섯 계층은 기술 파이프라인의 처리 순서가 아니라 **Iris 정보 모델의 층위**다.

### Evidence 모델

Iris의 Evidence 모델은 다음 네 개념을 구분한다.

- **Source**: 사실을 관찰한 경로. Recipe, Right-click, Static capability 등이 이에 해당한다.
- **Action**: 메뉴 노출, 클릭 경로, 행동명 등 실행 표면에 나타나는 정보.
- **Outcome**: 해당 아이템이 없으면 성립할 수 없는 결과 상태.
- **Evidence**: Source를 통해 관찰된 fact / outcome을 Rule이 소비할 수 있도록 정규화한 정보.

Rule은 Source나 Action 자체가 아니라 정규화된 **fact / outcome Evidence**를 소비한다. Action은 Source 검증에 사용될 수는 있어도 그 자체로 canonical Evidence가 되지 않는다.

표시용 텍스트와 기존 fact에서 새로운 의미를 도출하는 추론·연산은 automatic Evidence로 승격하지 않는다.

Capability category / type은 positive hint로 사용할 수 있지만, 그 부재를 closed negative Evidence로 사용하지 않는다.

자동 Evidence 경로로 처리할 수 없는 예외는 implicit inference로 보완하지 않고, 명시적인 manual override 경로로 분리한다.

### 책임 구조

Iris는 semantic source authority, 정보 생산, semantic staging, semantic composition, content adoption, artifact generation / validation / install, presentation projection, offline tooling, publication acceptance, runtime 표시와 package projection을 서로 구분된 책임 영역으로 나눈다. 각 영역은 자신이 소유한 판단과 상태만 관리하며, 한 영역의 산출물이나 검증 결과가 다른 영역의 authority 또는 acceptance를 자동으로 생성하지 않는다.

Layer 3 production flow는 다음과 같다.

```text id="6hxrjn"
canonical facts + provenance
-> source-bound role material
-> semantic composition
-> off-live semantic candidate
-> owner-authorized adoption
-> deterministic off-live complete generation
-> stateless generation / key validation
-> immutable generation install
-> single current-generation pointer switch
-> package projection
```

- **Semantic Source Authority**
  - Canonical fact와 provenance가 semantic source authority를 소유한다.
  - Adoption은 approved semantic candidate를 generation input으로 채택하지만 underlying source fact나 provenance authority를 재정의하지 않는다.

- **Classification / Rule**
  - 정규화된 Evidence를 소비하여 fact / outcome / classification을 고정하는 semantic classification 책임을 소유한다.

- **Layer 3 Semantic Staging**
  - Canonical fact와 provenance를 바탕으로 description-eligible fact와 acquisition fact를 역할별 material로 분리한다.
  - Acquisition-only material은 core description을 대신하지 않는다.
  - Staging은 source-bound fact identity와 provenance / transformation trace를 보존한다.
  - Readiness, disposition 또는 기타 staging metadata는 그 자체로 semantic source나 generation input이 되지 않는다.

- **DVF Core / DVF System**
  - Iris 3계층의 semantic composition과 off-live semantic candidate 생산을 소유한다.
  - 3-3 개별 아이템 본문은 `approved facts / decisions / profile / body_plan -> rendered 3-3 body` 경로로 구성한다.
  - **DVF Body Compiler**는 compiler determinism, `body_plan` 반영, 설명 블록 조합과 rendered body shape 검증을 담당한다.
  - DVF Core는 Semantic Staging이 준비한 source-bound role material을 소비하며 source fact나 provenance authority를 재정의하지 않는다.
  - DVF Core의 책임은 adoption 이전의 Layer 3 semantic candidate 생산에서 끝난다.

- **QG**
  - Iris 4계층의 상호작용 정보 생산·검문 파이프라인을 소유한다.

- **Offline Tooling**
  - `Iris/tooling`의 locked, installable `iris_tooling` package가 offline build tooling의 import / command authority를 소유한다.
  - Repository context는 명시적으로 주입하며 암묵적인 작업 디렉터리나 predecessor 경로에서 추론하지 않는다.
  - Legacy / predecessor build 경로는 reproduction 용도로 남을 수 있지만 current import / command authority를 소유하지 않는다.

- **Adoption Boundary**
  - 명시적으로 승인된 semantic candidate를 canonical generation input에 결속하는 authorization과 input binding을 소유한다.
  - Approved candidate만 generation input으로 전달한다.
  - Authorization, runtime readback, descriptor, receipt와 installer lifecycle state는 generation의 semantic input이 아니다.
  - Adoption은 generation artifact를 직접 생산하거나 runtime visibility를 전환하지 않는다.

- **Layer 3 Generation**
  - Canonical generation input을 deterministic하고 stateless한 complete-generation 경로를 통해 immutable runtime artifact로 materialize한다.
  - Rendered/runtime artifact, generation descriptor, receipt와 installer lifecycle state는 generation input으로 역유입되지 않는다.
  - Generation descriptor는 generation identity와 output structure를 기록한다.

- **Runtime Compatibility**
  - 생성된 artifact가 Iris runtime contract와 호환되는지를 검증한다.
  - Descriptor 자체를 권위로 신뢰하지 않고 input/output identity, key set, collision과 payload projection을 독립적으로 다시 검증한다.

- **Install Boundary**
  - 검증된 immutable generation을 설치하고 single current-generation pointer를 통해 runtime visibility를 전환하는 책임을 소유한다.
  - Installed generation은 제자리에서 수정하지 않는다.
  - 같은 generation의 재설치는 current visibility를 변경하지 않는 no-op으로 처리한다.
  - Install 과정은 source fact나 설명 의미를 새로 생성하거나 수정하지 않는다.

- **Presentation Projection**
  - 확정된 semantic source를 표시 순서, locale별 payload와 runtime 탐색 구조로 투영한다.
  - `CategoryPresentationOrder`는 표시 순서와 Description priority만 소유하며 category membership이나 의미를 소유하지 않는다.
  - Locale projection은 classification identity, fact authority 또는 interaction authority를 변경하지 않는다.
  - Layer 4 presentation projection은 QG가 생산한 interaction state를 표시 가능한 row와 UI state로 변환하며 interaction 의미 자체를 재정의하지 않는다.

- **Package Boundary**
  - Current-generation pointer가 선택한 runtime generation과 필요한 stable compatibility surface를 배포 package에 투영한다.
  - Package projection은 runtime payload와 generation identity의 일치를 검증하고 서로 다른 generation의 lookup surface가 하나의 package에 섞이지 않도록 한다.
  - Generation applicability를 확인할 근거가 없으면 fail-closed한다.
  - Package에는 stable facade / pointer와 pointer-selected generation 하나만 투영한다.

- **Publish Boundary**
  - public-text acceptance와 publication / release acceptance를 소유한다.

- **Browser / Tooltip / Wiki**
  - Layer 2 / Layer 3 / Layer 4 presentation을 Detail ViewModel에서 합성하고 정렬, 접기, 패널 배치, 표시 밀도, 검색, 기본 노출 범위 등 user-facing 표시를 담당한다.

- **외부 산출물 / 추출기**
  - Iris가 소비할 fact / outcome을 오프라인에서 생산한다.
  - 산출물은 Iris 입력 계약으로 정규화되어 해당 생산·분류 경로에 공급된다.

### Offline build / validation execution 구조

Iris의 offline build와 validation은 installed `iris_tooling` package를 current implementation owner로 사용한다. Runtime product는 계속 100% Lua이며 이 Python execution 구조는 repository-side generation/validation에만 존재한다.

```text
domain-owned input / payload / verdict
-> PhaseInput / PhaseOutput
-> thin PhaseRunner
-> CanonicalSemanticResult (stable meaning)
 + ExecutionEnvelope (run-local observation)
-> domain adapter / canonical CLI machine projection
-> package-bound clean-checkout gate
```

- `PhaseRunner`는 dependency ordering, run-local reuse, metric, issue/artifact association만 소유한다. Build/validation payload, success verdict와 semantic authority는 각 domain owner에 남는다.
- Canonical semantic result에는 deterministic stable meaning만 두고 run ID, elapsed, timestamp, process/environment와 path observation은 volatile envelope에 둔다.
- Canonical CLI는 existing validation authority의 thin adapter다. CLI, Python/PowerShell launcher와 pytest가 같은 semantic verdict를 중복 소유하지 않는다.
- Full-gate current-output seed는 producer 3개로 staging materialization을 한 번 수행하고 completeness/content identity 확인 뒤 immutable final seed와 case-local clone으로 공급한다. Mutation/tamper isolation과 Run A/B fresh-process independence는 공유하지 않는다.
- Iris planning/implementation bootstrap은 `docs/Philosophy.md` → `docs/DECISIONS.md` → `docs/ARCHITECTURE.md` → `docs/ROADMAP.md`이며 별도 human navigation projection을 두지 않는다. Current human command literal owner는 `Iris/build/ENTRYPOINTS.md`, machine route projection은 `Iris/_docs/authority/iris_current_route_index.json`이다. Description-tree predecessor source는 current import, command 또는 fallback authority가 아니다.
- Current denominator는 서로 다른 두 identity universe를 구분한다. Round3 current-route `103`은 routing membership이고 clean-checkout canonical full gate는 pytest 211개와 required standalone validation 4개, 즉 215 recurring execution unit을 소유한다.
- Same-name predecessor retirement는 31 substantive distinct basename identity와 33 concrete predecessor file을 구분한다. 두 extra file은 nested D16의 concrete copy이며 protected neutral fixture가 아니다.
- Exact package/environment subject가 달라질 때만 replacement terminal chain을 만든다. Unchanged subject를 confidence 확보만을 위해 반복하지 않으며 docs-only closeout은 machine PASS subject를 바꾸지 않는다.
- W0 admission artifact 미보존은 historical process fact로 유지한다. Owner disposition으로 closeout은 complete이며 새 owner instruction이나 새 current authority 없이 build/validation architecture work를 재개방하지 않는다.

### Tooltip T1 offline contract / T2 handoff 구조

Tooltip T1은 existing semantic owner와 mechanical static generation 사이의 offline projection/readiness boundary다.

```text
exact current subject
-> read-only W1-A adjacent-universe evidence
-> same-subject owner ratification
-> owner-ratified Tooltip support universe
-> Layer 2 resolved identity / Layer 3 approved fact / Layer 4 public candidate census
-> deterministic S1-S4 identity projection
-> selected identity freeze
-> KO/EN readiness
-> independent Menu evidence or shared-authority relation classification
-> whole-universe audit + owner correction ledger
-> T2 progression gate
-> OPEN only: minimal mechanical T2 handoff
```

Candidate closeout은 `partial/implemented_only` ceiling을 유지한다. 별도 installed-package finalizer는 candidate receipt와 동일 subject의 canonical Run A/Run B orchestration·inner result, deterministic comparator receipt만 검증하고 외부 빈 root에 final closeout 한 파일을 쓴다. 이 경계는 semantic input이나 T2 blocker를 다시 계산하지 않으며 receipt failure 또는 subject mismatch에서 아무 complete closeout도 생성하지 않는다.

- Classification, DVF System과 QG가 Layer 2/3/4 semantic authority를 계속 소유한다. T1은 projection/readiness metadata만 소유한다.
- Layer 3 DVF owner output은 `fact_id`, source/authority ref와 KO/EN surface readiness까지만 발행한다. Menu consumer identity ref나 parity verdict를 같은 owner output이 self-attest하지 않는다.
- T1-D3 candidate의 Layer 3 owner-output v2는 기존 fact compatibility projection인 `entries`와 explicit legitimate-absence projection인 `absence_entries`를 분리한다. Fact row는 기존 single-core fact/source/KO·EN identity를 유지하고, absence row는 exact FullType, owner, approved reason, independent evidence binding, scope와 re-audit condition만 운반한다. Absence는 semantic fact나 locale surface를 만들지 않는다.
- S2 소비 순서는 `valid approved fact -> valid approved explicit absence -> technical owner-row correction`이다. Fact/absence conflict, incomplete evidence, locale/review/quality defect 또는 unknown reason은 fail-loud correction으로 남고 compact되지 않는다. Existing pointer-selected empty-core 791건은 별도 current-generation role-material provenance를 유지하며 T1-D3 registry로 소급 rewrite하지 않는다.
- Layer 3 current shared-authority relation은 pointer-selected rendered fact relation에서 생성된 동일 FullType runtime text가 `IrisLayer3DataCurrent.lua → IrisLayer3DataLookup.lua → layer3_renderer.lua → IrisItemDetailModelAssembler.lua`로 소비되는 경로다. 이 경로는 fact/surface와 Menu surface가 같은 current generation을 공유함을 보이지만 독립 Menu fact-identity observation은 아니다.
- 따라서 selected Layer 3 row는 독립 consumer identity evidence가 추가되기 전까지 `unverified_without_independent_consumer_evidence`다. 이 상태는 full Menu parity와 T3 runtime-adoption claim을 보류하지만 shared relation이 성립하면 T2 blocker가 아니다. shared relation 부재/모순만 `correction_required`와 T2 blocker다.
- `menu_owner_output_self_comparison` invariant는 DVF owner output의 self-issued consumer-reference field를 직접 세며 canonical candidate에서 반드시 `0`이어야 한다.
- Layer 4 semantic identity input은 current owner data에서 읽고, reproduction baseline은 입력에서 제외한다. Current Browser consumer relation은 별도 runtime `label_key` identity set과 exact subset 비교한다.
- Layer 4 selection graph에는 locale/Menu readiness input edge가 없고 readiness graph에는 selected-identity writer edge가 없다.
- T1-D4 candidate는 이 분리를 type boundary로 강화한다. `Layer4Candidate`는 identity/public/source/structural-order 정보만 운반하고 locale surface 또는 Menu consumer ref를 보유하지 않는다. QG-owned Recipe locale registry/projection은 selection 이후 exact selected identity resolver에서만 결합된다.
- Current Layer 4 identity input의 embedded locale field는 Recipe surface authority로 소비하지 않는다. 발견 시 authority-ceiling violation으로 fail-loud하며, unselected-ready candidate substitution, Recipe→Right-click fallback, cross-locale fallback과 locale-dependent reselection 경로는 존재하지 않아야 한다.
- Recipe KO/EN surface는 동일 canonical interaction fact에 결속된 explicit pair다. D4는 logical-row single-line/NFC contract까지만 검증하고 pixel/font/UI-scale width fit은 기존 T3 presentation boundary에 남긴다.
- T2 handoff는 ordered `slot_id`, semantic identity와 KO/EN surface만 포함한다. Raw tags, unselected candidates, audit/parity/readiness/owner/reason metadata를 포함하지 않는다.
- T2는 requested locale surface read, legitimate absence compaction이 끝난 fixed-order rows의 concatenation과 static payload emit만 수행한다.
- Current upstream blocker가 남으면 cause-attributed progression record만 생성하고 T2 handoff를 생성하지 않는다.
- progression과 owner별 blocker distribution은 `t2_blocking = true` correction의 단일 filtered view를 공유한다.
- T1 run output은 repository-external immutable root에 두며 mutable latest pointer나 stateful registry를 만들지 않는다.
- 자세한 contract authority는 `Iris/_docs/authority/tooltip_t1/`, human policy는 `docs/iris_tooltip_t1_display_contract_policy.md`가 소유한다.

2026-08-28 corrective formal-closeout snapshot:

- exact synthetic subject는 commit `6b7118dc229bf8138302696e1aa5e5b7454589dc`, tree `4eae6fbdb3d0b2cb532f875b96137335a403f2fc`다.
- package tree `d1d0c098fb6f06222194e7e032af80932780b275`는 immutable environment authority `responsibility_refactor_environment_tooltip_t1c_corrective_d1d0c098.json`과 일치한다.
- focused 6-family, installed candidate invariant, canonical Run A/Run B와 deterministic comparator가 모두 exit 0이며 final closeout은 `complete/complete`다.
- correction ledger는 `5,625`, Layer 3 parity 분포는 selected-unverified `1,314`, correction `175`, not-applicable `791`이다. normalized collision `2`건은 denominator에서 제거하지 않고 support-owner blocker로 남는다.
- current data progression은 `BLOCKED_BY_UPSTREAM_CORRECTIONS`이고 production T2 handoff는 `0`이다. static Tooltip Lua, IrisAltTooltip runtime, visual/release/deployment는 이 snapshot의 claim이 아니다.
- 뒤의 docs-only carrier는 이 exact machine-validation subject, external candidate/gate receipt 또는 closeout hash를 바꾸지 않는다.

2026-08-29 T1-D3 parallel-workstream snapshot:

- Common predecessor는 commit `6b7118dc229bf8138302696e1aa5e5b7454589dc`, tree `4eae6fbdb3d0b2cb532f875b96137335a403f2fc`이며, D3 clean workstream subject는 commit `92583338`이다.
- Frozen support는 `2,280`, frozen D3 target은 exact 175이며 target SHA-256은 `accbe1ae691e41b1697f080f26b8206a08e261039bb7919879f67f4b5d7ef238`다.
- Metadata flow는 `authoritative T1 target freeze -> owner-proposed absence -> producer-independent defect-exclusion verdict -> terminal DVF registry -> v2 owner projection -> whole-T1 re-audit -> independent non-target comparator -> immutable D6 bundle`이다.
- Terminal distribution은 `A=0`, `B=175`, blocked `0`이고 candidate correction ledger는 `5,450`이다. Existing fact `1,314`, empty-core `791`, current generation/pointer와 locale/runtime payload는 불변이다.
- 이 snapshot은 isolated workstream architecture다. Shared-path merge, global current adoption과 integrated whole-T1 gate는 T1-D6가 소유하며 그 전까지 current ecosystem correction ledger `5,625`, T2 blocked와 production handoff `0`을 유지한다.

2026-08-29 T1-D4 parallel-workstream snapshot:

- Common predecessor는 commit `6b7118dc229bf8138302696e1aa5e5b7454589dc`, tree `4eae6fbdb3d0b2cb532f875b96137335a403f2fc`이며 D4 clean workstream subject는 commit `a8fddf747738045df08579ae34b0b727e3cf91ad`, tree `9b6b1831c18da58846d9d3c940133b2095de741d`다.
- Frozen support `2,280`의 canonical ordered-set SHA-256은 `3a6cc24b9ad64e06a0a6c0408821201e35bbd1d8558e6245809b5d3c34265ce6`이다. D4 frozen exact set은 predecessor 재도출 set과 동일하며 missing/extra는 `0`; 초기 JSON-array hash는 serialization-only 오류로 supersede했다.
- Frozen target은 selected Recipe instance 444건, exact identity 266개, locale correction 888건이다. Owner projection은 explicit KO/EN pair를 post-selection exact lookup으로 제공하며 selected tuple/source distribution, Right-click route와 other-owner correction set을 바꾸지 않는다.
- Candidate whole-T1 ledger는 `4,737`, D4 target은 `0`이다. Corrected bundle은 `integration_impact.support_freeze_mismatch=false`, support set changed `false`, predecessor mismatch `false`로 hash-bound됐다.
- 이 snapshot도 isolated workstream architecture다. Corrected D4 bundle만 T1-D6 integration input으로 사용하며, D3/D4 결과의 병합, global current adoption, integrated audit와 T2 progression 판정은 T1-D6 전까지 보류한다.

### Runtime presentation 구조

Iris runtime의 classification / presentation 흐름은 다음 단방향 구조를 따른다.

```text id="iysd2n"
Classification / Rule authority
-> CategoryPresentationOrder projection
-> CategoryIndex / VariantIndex
-> BrowserData
-> Browser / Wiki / Tooltip consumers
```

Classification / presentation logic은 Browser UI를 require하지 않는다.

Browser detail은 동일한 semantic source를 locale과 정보 계층에 맞는 presentation으로 합성한다.

```text id="mzvoeu"
selected item + locale
-> Detail ViewModel
-> Layer 2 template projection
 + Layer 3 locale projection
 + Layer 4 interaction projection
-> Browser detail renderer
```

- Locale 변경은 classification identity, source fact 또는 interaction authority를 변경하지 않는다.
- Layer 2는 같은 semantic template identity를 locale별 presentation으로 투영한다.
- Layer 4 interaction projection은 status-bearing interaction state를 표시 row로 정규화하고 표시 밀도, compact / full 전환, 검색과 navigation 같은 UI presentation을 적용한다.
- Layer 4 UI state는 item과 locale에 귀속되며, 둘 중 하나가 바뀌면 이전 item / locale의 검색·확장 상태를 새 detail에 재사용하지 않는다.

Detail의 engine access, model composition과 presentation policy도 분리한다.

```text id="8m3juh"
PZ engine-visible data
-> tri-state IrisItemFactReader
-> immutable detail model assembler
-> shared unit / visibility presentation policy
-> Detail ViewModel / renderer
```

- `IrisItemFactReader`가 engine-facing fact access를 소유한다.
- Immutable model assembler가 읽은 fact를 Detail model로 결합한다.
- Unit / visibility 규칙은 공통 presentation policy가 소유하며 engine access나 model assembly에 흩어지지 않는다.

### Runtime state / compatibility 구조

Iris runtime core는 public compatibility surface와 내부 state / fact model, runtime consumer를 분리한다.

```text id="qewmhf"
supported API / public require surface
-> thin facade or named compatibility adapter
-> explicit Browser / Detail / Description state and fact model
-> renderer / widget / chunk runtime consumers
```

- Description의 string output은 별도 병렬 구현이 아니라 canonical block API의 projection이다.
- Browser는 selection, cache, build 상태를 암묵적인 table 존재 여부가 아니라 명시적인 state로 관리한다.
- Browser와 Wiki detail은 동일한 read-only fact model을 소비한다.
- 유지되는 public contract는 thin facade 또는 이름 있는 compatibility adapter만을 통해 내부 core에 연결한다.
- Compatibility adapter는 독립 payload를 만들거나 core state를 복제하거나 runtime 의미를 재해석하지 않는다.
- 내부 payload representation은 필요에 따라 sparse / optimized 형태를 사용할 수 있지만 public compatibility shape와 의미는 유지한다.
- Public Browser row, Tags, UseCases, Tooltip summary와 Ordering projection은 내부 mutable state를 직접 노출하지 않으며 caller mutation으로부터 격리한다.
- Browser의 generation-local private row는 item identity와 locale별 presentation에 필요한 파생 값을 함께 소유한다.
- Classification bucket은 `fullType` membership만 보존하며 semantic classification state를 cache graph나 public result에 연결하지 않는다.
- Browser search snapshot은 generation과 normalized locale에 귀속되며 새 snapshot이 완성된 뒤 원자적으로 publish한다.
- Generation 또는 locale owner가 바뀌면 그 owner에 종속된 검색·variant cache를 함께 폐기한다.
- Variant 대표 선택은 locale이나 table iteration order가 아니라 stable `fullType` identity ordering으로 결정한다.
- Variant의 파생 group cache는 generation에 귀속되며 generation 변경과 함께 폐기한다.
- Instance-scoped state는 `fullType` 단위의 전역 state cache로 승격하지 않는다.
- Alt Tooltip은 static fact projection, translation resolution, line assembly를 분리하며 별도의 semantic fact model을 만들지 않는다.
- Iris runtime integration은 Project Zomboid의 전역 bullet-reload 또는 context-menu render 함수를 교체하지 않는다.
- Diagnostic counter와 clock instrumentation은 normal production state와 분리하며 explicit enable 상태에서만 갱신한다.
- Fault / fallback 가시성은 diagnostic instrumentation의 활성 여부와 독립적으로 유지하며, diagnostic output은 semantic authority나 일반 production state를 소유하지 않는다.

### Locale projection 구조

Layer 3 locale presentation은 current generation의 semantic source와 public entry set에 결속된 precompiled payload를 사용한다.

```text id="dfulsh"
current-generation pointer
-> current Layer 3 public entry set
-> locale-specific precompiled payload
-> locale renderer
```

- Locale projection producer는 current generation descriptor와 자신이 실제로 소비하는 semantic input에만 결속된다.
- Locale tooling 자체나 producer가 소비하지 않는 input의 변화가 Layer 3 generation identity를 재정의하지 않는다.
- KO는 pointer-selected generation의 current KO public body를 사용한다.
- EN companion payload는 같은 semantic facts에 결속되며 current generation에서 공개되는 entry set보다 넓은 정보를 노출하지 않는다.
- Runtime은 readiness, disposition, fact-kind, rewrite 또는 summarization을 새로 계산하지 않고 precompiled locale projection만 표시한다.
- 요청 locale의 payload만 표시하며 다른 locale의 raw text를 대신 노출하는 cross-locale fallback은 사용하지 않는다.
- Stale locale payload가 남아 있더라도 current-generation public entry set보다 넓은 정보를 노출하지 않는다.

### Runtime materialization / lookup 구조

Runtime data는 consumer 요구 시점에 materialize한다.

```text id="m7prn9"
Browser boot
-> module / API surface 등록
-> first open에서 Browser data build
-> generation cache로 이후 재사용

StaticData consumer
-> first use에서 필요한 static payload 로드
-> cache로 이후 재사용

Layer 3 consumer
-> current-generation pointer
-> routing metadata
-> internal lookup router
-> pointer-selected target chunk 로드
-> session cache

UseCase consumer
-> first demand에서 routing / count metadata 준비
-> internal lookup router
-> 필요한 target chunk 로드
-> session cache

direct compatibility facade
-> current-generation pointer
-> pointer-selected generation 전체 materialization
-> 기존 public contract 유지
```

- `OnGameBoot`는 Recipe / Moveables / Fixing / Classifications static payload를 선행 materialize하지 않는다.
- Browser의 lazy build는 기존 public `build()` 계약과 open entrypoint를 변경하지 않는다.
- Layer 3 stable facade와 routing index는 동일한 current-generation pointer를 따라가며 inactive generation이 현재 runtime visibility에 섞이지 않는다.
- UseCase routing / count metadata는 module-load dependency가 아니라 first demand에서 준비하고 각 metadata surface를 독립적으로 검증한다.
- 서로 다른 metadata 사이의 consistency 검증은 양쪽이 모두 유효할 때만 수행한다.
- Routing / count metadata는 key boundary, target module, row count와 identity 같은 lookup 정보만 소유하며 source fact나 semantic authority를 소유하지 않는다.
- 전체 generation materialization은 기존 public contract를 위한 compatibility 경로이며 normal demand-loading 경로와 구분한다.
- Runtime lookup은 `verified hit`, `verified miss`, `routing / target fault`를 구분한다.
- `verified miss`는 정상적인 sparse-key 결과이며 compatibility 전체 materialization이나 fault-triggered fallback을 유발하지 않는다.
- Routing metadata 또는 target payload의 결함만 fault / fallback 경로로 분류한다.
- Fault-triggered compatibility fallback은 정상 lookup 및 direct compatibility facade의 정상 full-materialization 경로와 구분하여 관측 가능하게 유지한다.

---

## 2-6. Frame

> 구현 상태: 설계 단계

### 정체성

Project Zomboid 모드팩의 상태를 시간축 위에서 **기록·비교·되돌리는 버전 관리 레이어**.

Frame은 개별 모드 관리자라기보다 **팩 상태(pack state)** 를 1급 객체로 다루는 환경 통제 모듈이다. 관리 최소 단위는 모드 하나가 아니라 모드 목록, 순서, 출처, 설정, 사용자 오버라이드, fingerprint를 포함한 팩 상태 전체다.

Frame은 게임 실행 중 성능·안정성에 개입하는 런타임 레이어가 아니다.

### 하는 일

- PackState 단위의 모드팩 상태 기록
- 기준점과 현재 상태의 비교
- 수동 기준점과 자동 복구 snapshot 운영
- baseline 설정과 사용자 override의 분리 관리
- 저장된 상태를 기준으로 한 재구성, rollback, restore 지원
- fingerprint를 이용한 상태 동일성 확인
- 외부 공유 상태의 import / export와 내부 정규화

### 하지 않는 일

- 상태 비교 결과를 문제 원인, 정상 / 비정상, 추천 또는 정답 판정으로 승격하는 것
- 모드 원본 파일을 소유·배포하는 완전 복원 저장소로 확장하는 것
- Frame 내부에서 설정 값을 직접 편집하는 configuration authority가 되는 것
- `.frame`을 외부 공유 표준으로 강제하는 것

### PackState 구조

Frame의 핵심 domain object는 **PackState**다.

```text id="m7at3f"
mod list
+ load order
+ source
+ baseline configuration
+ user overrides
+ fingerprint
= PackState
```

- **mod list**는 해당 상태에 포함된 모드 집합을 나타낸다.
- **load order**는 모드의 적용 순서를 보존한다.
- **source**는 각 모드의 출처를 기록한다.
- **baseline configuration**은 팩이 제공한 기준 설정을 보존한다.
- **user overrides**는 기준 설정을 직접 덮어쓰지 않고 사용자 변경을 별도 레이어로 관리한다.
- **fingerprint**는 저장된 상태와 현재 상태의 동일성 비교에 사용한다.

PackState는 개별 모드의 상태를 모아놓은 단순 목록이 아니라, 특정 시점의 모드팩 환경 전체를 표현하는 하나의 상태 단위다.

### Snapshot 구조

Frame의 snapshot은 같은 PackState 표현을 사용할 수 있지만 역할에 따라 구분한다.

- **수동 기준점**
  - 사용자가 명시적으로 저장한 의도적 기준 상태다.
  - 비교, rollback, restore의 공식 기준점으로 사용한다.

- **자동 복구 snapshot**
  - 세션 또는 주기 기반으로 남기는 시간축 안전망이다.
  - 예상하지 못한 상태 변화에서 복구와 변화 추적을 돕는다.

수동 기준점과 자동 복구 snapshot은 품질 차이가 아니라 **의도와 lifecycle이 다른 기록**이다. UI와 상태 관리에서도 둘을 구분한다.

### 복원 / 재현 구조

Frame은 모드 원본 자체를 보존하는 완전 복원 시스템이 아니라 **재구성 + 동일성 확인** 구조를 사용한다.

```text id="2spghz"
saved PackState
-> available mods / configuration 재구성
-> baseline + user overrides 적용
-> current fingerprint 계산
-> saved fingerprint / structure와 비교
-> unresolved difference 노출
```

- 복원 가능한 모드와 설정은 저장된 PackState를 기준으로 재구성한다.
- baseline configuration과 user overrides는 서로 다른 레이어로 유지한다.
- 모드 삭제, 출처 변경, Workshop 업데이트 등으로 과거 상태를 완전히 재구성할 수 없는 경우 이를 숨기거나 임의 보정하지 않는다.
- 복원 이후 fingerprint와 구조 비교를 통해 현재 상태가 저장된 기준점과 같은지 확인한다.
- 완전 복원이 불가능한 차이는 unresolved difference로 남겨 사용자에게 드러낸다.

### 공유 / 내부 포맷 구조

Frame은 외부 공유 형식과 내부 정규화 형식을 분리한다.

#### 외부 공유

기본 공유는 열린 형식을 우선한다.

```text id="q0i3er"
ZIP
+ manifest.json
+ baseline configuration
+ optional user overrides
+ fingerprint metadata
```

- 외부 공유 상태는 다른 환경에서 가져올 수 있는 기대 상태 또는 기준점으로 취급한다.
- 사용자 override를 포함할 수 있지만 포함 여부와 범위를 명확하게 표현한다.

#### 내부 정규화

외부 공유 상태와 현재 로컬 상태는 검증 후 내부 PackState 표현으로 정규화한다.

- 내부 PackState model
- snapshot state
- comparison state
- fingerprint state
- 선택적 `.frame` cache

`.frame`은 외부 공개 표준이 아니라 Frame 내부의 정규화 / 검증 / cache를 위한 보조 형식이다.

---

## 2-7. Cortex

> 구현 상태: 설계 단계

### 정체성

다른 제품 도메인이나 Pulse Core에 두기 부적절한 user-facing helper / 편의 / 가이드 기능의 **격리 구역**.

Cortex는 다른 Spoke들이 의존하는 공용 유틸 라이브러리가 아니라, 독립적인 사용자-facing 제품 모듈이다.

### 하는 일

- 다른 제품 모듈의 고유 역할에 속하지 않는 helper / 편의 / 가이드 기능 수용
- Pulse 기반 모딩을 이해하고 사용하는 데 필요한 가이드 / 보조 UX 제공
- Core capability로 승격할 필요가 없는 사용자-facing 보조 기능 격리

### 하지 않는 일

- 다른 Spoke들이 import하는 shared utils / 공용 라이브러리 역할을 맡는 것
- 향후 Core로 옮길 기능을 임시 보관하는 staging area가 되는 것
- 별도 제품 축으로 분리해야 할 기능을 편의 기능이라는 이유로 Cortex 내부에 수용하는 것

---

## 2-8. Canvas

> 구현 상태: 설계 단계

### 정체성

외부 툴이 만든 리소스팩 산출물과 현재 활성 리소스 상태를 읽어 **최종 적용 상태를 계산·검증·비교·설명하는 리소스 적용 상태 관리 모듈**.

Canvas의 user-facing 1급 객체는 **ResourcePack**이고, 여러 ResourcePack이 합쳐져 실제 게임에 적용된 최종 상태는 **ResourceState**로 표현한다.

### 하는 일

- 외부 리소스 산출물과 runtime 활성 상태를 공통 내부 표현으로 정규화
- 활성 ResourcePack과 적용 순서를 바탕으로 최종 ResourceState 계산
- 리소스 충돌, 구조 / ID / 패킹 문제와 배포 전 상태 검증
- 로컬 작업본 / 빌드 산출물 / 서버 / 클라이언트 상태 비교
- 계산·검증·비교 결과의 user-facing projection과 설명형 리포트 제공

### ResourceState 처리 구조

Canvas의 리소스 모델은 `AssetEntry`, `ResourcePack`, `ResourceState`의 세 수준으로 구분한다.

- **AssetEntry**
  - 개별 리소스의 identity, 대상 경로와 provenance를 표현하는 최소 단위다.

- **ResourcePack**
  - 사용자가 불러오고, 공유하고, 비교하는 user-facing 상태 단위다.
  - 하나 이상의 AssetEntry와 pack-level metadata를 포함한다.

- **ResourceState**
  - 활성 ResourcePack의 내용과 순서를 해석해 얻은 최종 적용 상태다.
  - 여러 pack의 중첩, 충돌과 최종 적용 결과를 표현한다.

처리 흐름은 다음과 같다.

```text id="wtfcvu"
external artifacts / runtime active state
-> validated / normalized AssetEntry set
-> ResourcePack representation
-> ordered ResourceState resolution
-> application / build-safety / deployment-comparison views
-> report / user-facing projection
```

- 외부 산출물과 runtime 활성 상태는 서로 다른 입력이지만 동일한 normalized resource model로 투영한다.
- 최종 적용 상태 계산은 ResourcePack의 활성 여부와 적용 순서를 반영한다.
- 충돌 분석, 구조 검증과 상태 비교는 동일한 normalized resource model을 소비하며 서로 독립적인 원본 해석 경로를 만들지 않는다.
- 적용 상태, 제작 안전과 배포 일치에 대한 결과는 각각의 판정 축을 유지하며 하나의 숨겨진 master score로 합치지 않는다.

### 입력 / 정규화 / 출력 구조

Canvas는 외부 배포 산출물과 현재 runtime 상태를 모두 입력으로 받을 수 있다.

```text id="x81tug"
external project / package / manifest
        \
         -> validation + normalization -> internal resource model
        /
runtime active resource state

internal resource model
-> ResourceState calculation / comparison
-> report projection
-> native or open-format output
```

- 외부 파일 형식은 Canvas의 내부 domain model 자체가 아니다.
- 외부 입력은 검증 후 AssetEntry / ResourcePack 구조로 정규화한다.
- Runtime 활성 상태도 동일한 내부 모델로 투영하여 외부 기대 상태와 비교할 수 있다.
- 내부 cache나 분석 bundle은 계산과 검증을 위한 보조 representation이며 authoritative input이나 외부 표준 역할을 소유하지 않는다.
- 출력은 가능한 한 PZ native 또는 열린 포맷으로 projection하며, 내부 representation을 외부 공유 계약으로 강제하지 않는다.

## Iris repository current / historical storage boundary

Iris의 current clean-checkout closure는 source, runtime, tooling, contract, current-required evidence capsule만 repository 안에 둔다. Historical staging, reproduction evidence, predecessor attempts, inactive Layer 3 rollback payload는 current route와 분리된 explicit external archive가 소유한다.

```text
current clean checkout
-> current source/runtime/tooling/contracts
-> bounded current_required_v1 capsule
-> canonical gate and package (archive-independent)

historical logical rows
-> content_addressed_zip_v2 objects + logical-path manifest
-> explicit verify/restore command only
```

- Current commands는 archive locator를 fallback dependency로 읽거나 payload를 자동 restore하지 않는다.
- Tracked archive bytes는 exact Git blob, custody-only bytes는 recorded custody filesystem identity를 authority로 사용한다.
- Archive는 deterministic ZIP deflate level 9, canonical member order/metadata, unique `objects/<sha256>` bodies와 logical path mapping을 사용한다.
- Current raw evidence availability를 유지할 row만 bounded capsule에 raw bytes로 남기고, 나머지는 versioned digest/summary attestation으로 전환한다.
- Generated output은 runtime authority가 아니며 explicit external candidate와 fail-closed install boundary를 거친다.
- W0 item inventories, residue selections와 ad hoc probes는 repository-external 실행 증거이며 regular validation authority가 아니다.
- Current/historical archive identity와 restore contract의 durable readpoint는 `Iris/validation/clean_checkout/authority/iris_historical_archive_v1.json`이다.
- Physical removal domain과 recovery link는 `Iris/validation/clean_checkout/authority/iris_historical_removal_v1.json`에 두고 tracked removal과 local-custody removal을 합산하지 않는다.
- Terminal local-custody에서 뒤늦게 드러난 historical unique row는 predecessor archive를 rewrite하지 않는다. Exact W0 identity와 current-tree absence를 확인하고 별도의 additive external `content_addressed_zip_v2` successor에 create/verify/restore한 뒤 literal path만 제거한다.
- Dirty-main custody subject는 repository 전체 status digest를 binding에 포함하되 W10의 Iris physical state를 별도로 측정한다. 다른 모듈의 dirty state는 Iris residue나 removal delta에 합산하지 않는다.
- Exact implementation `801f15f6`의 terminal W10은 clean tracked 1,753 files / 71,766,663 Git blob bytes, clean physical 1,753 files / 72,344,398 bytes, custody Iris physical 1,753 files / 72,154,554 bytes를 기록한다. Custody Iris ignored/untracked/filesystem-only/reparse는 모두 0이다.
- Terminal capsule은 133,094 bytes이고 successor overhead는 1,653,400 bytes로 각각 2,359,296-byte 및 3,037,162-byte ceiling 이내다.
- G5 compiler identity successor는 append-only다. 최초 0013·0014 blobs는 immutable historical evidence로 유지하고 schema-compatible aggregate 정정은 0015가 소유한다. Execution-boundary 변경으로 달라진 19-path closure는 0016, identity owner와 `execution.py`를 포함한 21-path closure는 0017이 소유한다. Current required paths는 0016 뒤에 0017을 누적 보존하며 과거 successor를 재작성하거나 전체 chain을 재번호링하지 않는다. Retention-list correction은 closure bytes를 바꾸지 않았으므로 0018을 만들지 않는다.
- Terminal aggregate, stable digests와 external locators의 documentary readpoint는 `docs/iris_lightweighting_terminal_closeout.json`이다. 이 파일과 external one-off producer/transaction은 canonical gate, regular validation schema 또는 새 claim ID가 아니다.
- Terminal closeout identity는 세 층으로 구분한다: machine/W10 implementation `801f15f6`, independent review가 확인한 docs carrier `9882ce6d`, review 결과를 반영해 local `main`에 통합한 completion carrier `28f95b63`. 뒤의 docs-only carrier는 앞선 machine result나 review subject를 대체하지 않는다.
- Local `main`의 다른 모듈 untracked build output은 Iris physical census와 분리된 workspace state다. Iris closeout이나 local-custody cleanup을 이유로 이를 탐색·삭제·합산하지 않는다.
