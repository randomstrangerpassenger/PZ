# Implementation Plan

> **문제명:** Iris DVF 기본 설명의 실용성·일관성 개선과 Tooltip·Menu 반영
> **작성일:** 2026-08-31
> **입력:** 사용자 제공 「Iris DVF 기본 설명의 실용성·일관성 개선과 Tooltip·Menu 반영 Roadmap — 종합안」
> **수정 근거:** 사용자 제공 「Iris DVF Shared Composition / Usefulness / Menu·Tooltip Implementation Plan — Integrated Review」 및 후속 가독성·baseline·관찰 주체 보완 의견. 이후 사용자 요청에 따라 유지 사유와 실제 개선 범위, single-core와 복수 기본 용도의 구분, 묶음 문장 검토 및 테스트·Gate 최소화를 반영했다. 실행 조건은 §4.5에 정리한다.
> **양식:** [PLAN_TEMPLATE.md](PLAN_TEMPLATE.md)
> **상태:** 구현 진행 중 / 사용자 owner 사전 승인 적용 / 기존 T1 필수 full A/B 예외는 §7 실행 정정 참조
> **실행 분류:** Heavy — Authority / Sealed Artifact / Public-Facing Output 변경. 단계별 전체 회귀 반복을 뜻하지 않는다.
> **조사 기준:** repository HEAD `e3bef7d656d89fb9a4417647db3a7cbb072ff953`와 작성 시점 working tree. 실행 시작 시 exact subject를 다시 결속한다.

---

## 1. Objective

기존 DVF Body Compiler 안에서 **source-bound semantic material과 표현·조합을 분리**하고, 같은 의미 구조에 적용하는 공통 표현을 한 번 수정하면 해당 아이템의 KO/EN 기본 설명에 결정적으로 반영되는 생산 경로를 만든다. 아이템별 대상·효과·조건·예외를 보존하며, 공통화가 부적합한 항목은 explicit item body 또는 명시적 current surface retention으로 유지한다.

완료 대상은 compiler 구현에 그치지 않는다. 검토된 successor candidate를 채택하고, immutable Layer 3 generation, Menu KO/EN 본문, 같은 승인 core를 사용하는 Tooltip S2, strict T1, T2 fixed data, matching Recipe companion과 설치 가능한 package까지 연결한다.

실용성은 사용자가 “이 아이템은 무엇에 쓰이며 어떤 효과가 있는가?”를 근거 범위 안에서 이해할 수 있는지로 판단한다. 어미 교체·문장 길이 감소·공통화율만으로 개선을 주장하지 않는다. 새로운 게임 사실을 추론하는 시스템이나 별도 description engine은 만들지 않는다.

공유 표현의 전파 시연은 생산 구조가 동작한다는 증거이며 전체 설명 개선을 대신하지 않는다. 보존 경계 밖에서 근거가 충분하고 개선 필요성이 확인된 설명은 shared 또는 explicit 경로로 개선한다. 공통화의 어려움·구현 편의·미작업을 이유로 기존 문장 유지에 포함하지 않으며, 변경 개수나 공통화율 목표는 두지 않는다.

---

## 2. Scope

- Current DVF exact FullType universe의 생산 경로와 source binding을 조사하고, 공통 조합·부분 block 공유·개별 조합·retention·semantic correction dependency를 구분한다.
- 기존 `body_plan` / Body Compiler에 선택적 shared composition, item별 binding, truth-critical condition, 명시적 exception과 KO/EN rendering을 추가한다.
- 현재 scalar source만으로 안전한 구조화가 불가능한 항목은 source를 추가 확인하거나 기존 승인 표면을 보존한다. 문장을 파싱해 새 fact를 만들지 않는다.
- Approved candidate의 생산·채택과 generation identity 계약을 필요한 최소 범위에서 연결한다.
- Menu EN과 Tooltip S2 owner projection도 같은 successor composition 결과를 사용하도록 조정한다.
- 기존 T1/T2 및 Recipe companion 생산·검증 경로를 재사용하여 successor package를 만든다.
- 기존 focused tests, 최종 current required regression, 제한된 사람의 문장 검토와 실제 runtime 관찰로 변경 범위를 검증한다.

### Explicitly Out Of Scope

- Pulse 또는 다른 모듈 변경, Hub & Spoke / SPI 구조 변경, Iris runtime의 JVM 도입.
- Classification 및 S1 선택 정책, QG·Layer 4 Recipe / Right-click 의미·우선순위·요구조건 체계 재설계.
- Browser 검색 본문 색인, 용도·효과 검색, fuzzy/semantic search, 설명군 기반 navigation.
- Alt 활성화, 최대 4 logical rows, Tooltip 위치·Recipe opening lifecycle의 정책 변경.
- 외부 모드 adapter, raw mod format / load-order / overwrite / version 해석, Build 42 대응.
- Runtime 문장 생성·번역·요약·template expansion, 게임 상태나 아이템·행동 변경.
- 기존 sealed history 삭제·재작성, 새 독립 validator framework / governance gate 도입.
- 실제 게임 설치 폴더의 무단 교체, Workshop 게시·release·deployment 승인.

---

## 3. Non-Goals

- 모든 아이템을 shared pattern에 넣거나 특정 공통화율을 달성하지 않는다.
- 기존 273개 source `review_hold`, 6개 silent row, 175개 explicit owner absence를 해소하는 작업이 아니다.
- 현재 승인된 prose의 의미 정확성을 전수 재보증하거나, 이름·classification·현실 용도로 부족한 근거를 채우지 않는다.
- Menu의 모든 질문에 대한 답이나 Layer 4 전체 정보 완비를 보장하지 않는다.
- 모든 2,105개 문장의 인간 전수 승인, 전체 해상도·UI scale 시각 QA, 임의 모드 조합·멀티·장시간·성능 인증을 수행하지 않는다.
- 이번 계획 작성만으로 구현 완료, 제품 PASS, owner adoption 또는 공개 준비 완료를 선언하지 않는다.

---

## 4. Assumptions

### 4.1 Authority와 실행 경계

1. [Philosophy.md](Philosophy.md)의 Iris 정보·중립성·침묵 원칙이 최상위다. Menu와 Alt Tooltip은 같은 사실을 다른 깊이로 표시하며 runtime은 100% Lua다.
2. [DECISIONS.md](DECISIONS.md)의 DVF optional role-material, 2026-08-31 실용성 교정, installed tooling, stateless generation, T1/T2/T3 결정과 [ARCHITECTURE.md](ARCHITECTURE.md)의 semantic staging → composition → adoption → generation 분리를 따른다.
3. [EXECUTION_CONTRACT.md](EXECUTION_CONTRACT.md) §3–7에 따라 실행을 Heavy로 분류하고 evidence와 claim ceiling을 기록한다. Heavy라는 이유로 full suite 반복, 별도 gate 또는 과거 작업의 절차를 추가하지 않는다.
4. 이 요청의 실행 범위는 **계획 문서 작성**이다. 아래 adoption/install/package는 후속 구현 시의 작업이며, 과거 candidate에 대한 `user_execution_request_preapproval`을 새 candidate의 승인으로 재사용하지 않는다. 후속 실행 지시에 포함된 권한은 중복 확인하지 않는다.
5. 명령과 import owner는 installed `iris_tooling` 및 실제 CLI/script 구현이다. 퇴역한 `Iris/AGENTS.md`, `Iris/build/ENTRYPOINTS.md`를 복구하거나 새 bootstrap authority를 만들지 않는다.
6. Human/public-text acceptance는 기존 Publish Boundary의 책임 중 **이번 작업의 문장 수용 범위**로 한정하며 issuer는 owner(사용자) 또는 owner가 지정한 사람이다. 실행 AI의 family 목록·source binding·대표 출력·평가와 자동 evaluator 결과는 판정 입력일 뿐 acceptance가 아니다. 일반적인 실행 허가를 아직 검토하지 않은 문장의 human acceptance로 읽지 않는다. 기본 진행은 **채택 전 candidate 문장 묶음 검토 1회와 최종 package의 PZ 표본 관찰 1회**로 모으며, pilot·family·item마다 별도 승인을 요청하지 않는다. 최종 문장 묶음은 필요한 자료와 자동 확인 결과를 준비한 뒤 제공한다. 결함 수정 후에는 영향받은 문장이나 관찰 범위만 보완하며, 횟수를 맞추기 위해 미승인 결과를 통과시키지 않는다. 이 수용 판정은 publication/release acceptance나 Publish 전체 PASS를 뜻하지 않는다.

### 4.2 작성 시점에서 직접 확인한 baseline

다음은 JSON/Lua 파일을 읽어 집계한 관측값이다. Compiler·generation·runtime 검증 PASS가 아니며, 실행 시작 시 exact key set / content identity를 다시 결속한다. 실행 시 재도출 결과가 아래 값과 다르면 차이의 원인과 current subject 관계를 확인한 뒤 **Change 1에서 확정한 재도출 집합·수치를 실제 control로 사용**한다. 작성 시점 숫자를 고정 목표나 통과 조건으로 강제하지 않는다.

| 집합 | 관측값 | 확인한 readpoint |
|---|---:|---|
| Current Layer 3 generation | `dvf33-103dd029d58267ffa696fcb9fa197d5564d14716f12f6ae3ee398b4fb3b41d83` | `IrisLayer3DataCurrent.lua`, Layer 3 owner input의 `generation_id` |
| Adopted candidate universe | 2,105 | `approved_upstream/candidate_rendered.json`의 exact `entries` |
| KO public / silent | 2,099 / 6 | 위 candidate의 `text_ko` 유무 |
| EN public | 2,099 | `Data/Layer3English/Chunk*.lua`의 entry 수. KO와의 exact-set parity는 실행 시 검사 |
| Single-core role-material / S2 owner entries | 2,048 / 2,048 | candidate `core_source_fact_ids`와 `tooltip_t1_layer3_owner_input.json` |
| DVF universe 내부 empty-core | 57 — Menu public 51 / silent 6 | 검토 반영 시 candidate의 **명시적 빈** `core_source_fact_ids`를 직접 추출. 57개 모두 S2 owner `entries`에 없고 explicit `absence_entries`와도 교집합 0 |
| Explicit owner absence | 175 | 위 owner input의 별도 `absence_entries` |
| Tooltip T1 Layer 3 owner input rows | 2,223 | `tooltip_t1_layer3_owner_input.json`의 `2,048` core + `175` absence. Tooltip support universe와 다름 |
| Tooltip support | 2,280 | `IrisTooltipStaticData.lua`의 exact key entries |
| Recipe companion | 349 FullTypes / 781 variants | `IrisTooltipRecipeVariants.lua`의 item / variant entries |
| 최근 기본 설명 교정 / 보호 context | 1,541 / 12 | candidate의 `meta.usefulness_integration` 기록값 |
| Source review hold | 273 | `dvf_3_3_input_manifest.json`의 `usefulness_correction.review_hold_count` 기록값 |

S1의 `1,406 applicable / 874 display silence`는 로드맵·기존 결정의 값으로, 이번 문서 작성에서 집합을 재도출하지 않았다. T2 0–4줄 분포와 predecessor의 `selected-unverified 1,314 / correction 175 / not-applicable 791`도 current 값으로 상속하지 않는다.

`public`, `silent`, S2 eligibility, protection, source hold, owner absence는 서로 다른 axis다. 보호 12개나 hold 273개를 2,105에서 일괄 차감하거나, owner 2,223을 support 2,280의 대체 분모로 사용하지 않는다. `Base.LemonGrass`와 `Base.Lemongrass`처럼 대소문자가 다른 FullType을 구분해야 하므로 집계에서도 case-insensitive map / normalization을 사용하지 않는다.

Empty-core 57개는 `2,105 - 2,048`이라는 산술 차만으로 정의하지 않는다. 명시적 빈 core 목록에서 exact 집합을 추출한 뒤 이 수치와 대조하며, field 누락·malformed row는 empty-core가 아닌 결손으로 처리한다. Source hold / protection과의 교집합은 Change 1에서 원래 owner membership으로 결속한다. Empty-core를 silent 6개 또는 universe 밖의 explicit owner absence 175개와 같은 상태로 취급하지 않는다.

### 4.3 코드 조사에서 확인한 결합점

아래 Python 경로의 `build/`와 `domains/`는 별도 표시가 없으면 `Iris/tooling/src/iris_tooling/` 아래다.

| 현재 구현 | 확인한 동작 | 계획에 미치는 영향 |
|---|---|---|
| `build/compose_layer3_body_profile.py`, `compose_layer3_item.py`, `compose_layer3_render.py` | Profile / section 기반 `body_plan`, candidate 조합, source field trace가 이미 있음 | 별도 engine 대신 이 책임을 확장하되 diagnostic/legacy path만 바꾸고 끝내지 않음 |
| `Iris/build/description/v2/tools/build/layer3_body_role_realign.py:compose_role_material` | Source-bound `source_value` 문장을 결합하고 core/acquisition fact IDs를 분리함 | 현재 material은 완전한 typed value/condition model이 아님. prose에서 slot을 역추출하지 않음 |
| 같은 파일의 `scalar_fact_id` | Item / source slot / source-value hash / origin으로 identity를 생성함 | 문구가 담긴 source slot을 바꾸면 ID도 바뀔 수 있음. expression-only를 무조건 “동일 ID”로 처리하지 않음 |
| `build/compose_layer3_role_material.py` | 위 role helper를 상대 import 후 top-level import로 시도함. 대응 helper는 조사 시 description-tree에 있음 | 새 current production에서 이 wrapper를 사용하면 실제 wheel import closure부터 확인. source-tree `sys.path` fallback에 기대지 않음 |
| `build/build_dvf_3_3_complete_generation.py:build_complete_generation` | `CANONICAL_INPUTS[6]`의 이미 채택된 candidate를 읽어 Lua로 materialize함 | `compose_*` 수정이나 generation 재실행만으로 새 문장이 채택되지 않음. successor candidate 생산·adoption을 명시적으로 연결 |
| `build/dvf_3_3_generation_contract.py` | Canonical seven-input과 명시적 generator file 목록으로 identity를 계산함 | 새 composition data / renderer dependency가 identity에서 빠지지 않게 함. 기존 seven-input 내 수용을 우선 |
| `build/build_layer3_english_localization.py:build_english_entries` | Current pointer/input을 확인하고 scalar 번역 및 일부 채택된 bilingual overrides로 EN을 작성함 | 새로운 KO composition만 추가하면 EN이 뒤처질 수 있음. same semantic binding의 EN 출력을 우선 소비하도록 연결 |
| 같은 파일의 `build_tooltip_t1_owner_entries` | Core fact ID는 1개만 허용하며 `primary_use`와 번역 mapping으로 S2를 별도 발행함 | Menu 완성 본문을 잘라 쓰지 말고 승인된 core의 KO/EN 표면을 공통으로 공급. Single-core는 identity 제약이며 기본 용도를 하나로 제한하지 않음 |
| `Data/IrisLayer3DataCurrent.lua`, `IrisLayer3EnglishLookup.lua` | KO는 generation pointer, EN은 별도 `Layer3English/Index.lua`를 읽음 | Pointer 한 번으로 EN/T2까지 atomic switch된다고 가정할 수 없음 |
| `domains/tooltip_static_data_projection/recipe_variants.py` | Fixed 배열의 L2/L3 prefix를 보존한 완성 variant와 base를 생성함 | S2 변경 시 fixed와 companion 모두 재생성. Companion CLI는 repository 내부 output을 요구하므로 격리 checkout에서 수행 |
| `Iris/tools/package_iris.ps1` | Current pointer가 선택한 Layer 3 generation 하나만 package에 포함함 | KO generation 검증 외에 EN / fixed / companion의 exact pair identity도 확인 |

실제 Menu consumer는 `Data/layer3_renderer.lua` → `UI/Detail/IrisItemDetailModelAssembler.lua` → formatter / Browser·Wiki presentation이다. Tooltip은 `IrisAltTooltip.lua` → `IrisTooltipStaticDataLookup.lua` → fixed / Recipe companion을 읽는다. Runtime 생성·추론 코드를 추가할 필요는 없다.

현재 `Base.Apple`은 하나의 `core_source_fact_ids` 항목으로 “섭취하면 허기와 갈증을 줄일 수 있고 요리 재료로도 사용할 수 있다.”라는 기본 설명을 운반한다. 이는 단일 core에 복수 기본 용도·효과를 담을 수 있다는 현재 구조의 사례다. 다른 아이템의 기능 근거로 전이하지 않으며, 이 문장을 고정 정답으로 삼지도 않는다.

### 4.4 종합 로드맵의 판정 필요 항목에 대한 실행 선택

| 쟁점 | 이 계획의 선택 | 근거·제한 |
|---|---|---|
| Heavy / Standard | **Heavy** | EXECUTION_CONTRACT §4-3의 Authority / Sealed / Public output trigger가 적용됨. 신규 독립 gate 0, 기존 T1 finalizer의 최종 필수 full A/B 묶음 밖에 추가 전체 회귀를 부과하지 않음 |
| 수직 pilot | **작은 off-live 연결 확인을 compiler 개발에 통합 가능** | 실제 generation은 adopted candidate를 복사하고 EN/S2는 별도 producer이므로 확대 전에 연결 가능성은 확인한다. Change 2–3을 합칠 수 있으며 별도 보고서·사람 승인·전체 회귀 gate를 만들지 않음 |
| Human text acceptance | **새 표현 구조와 의미에 영향을 주는 변형을 대표 출력으로 묶어 검토** | 최종 candidate의 KO/EN 구조·조건·exception을 채택 전에 한 묶음으로 제공한다. 동일 구조의 값 치환마다 사람 검토를 반복하지 않으며 실제 PZ 관찰은 최종 package 표본 확인으로 모음 |
| Compatibility 분류 | **Offline producer/consumer I/O에 조건부 영향, runtime API는 보존** | `body_plan` / candidate / installed tooling의 입력 변경 가능성을 숨기지 않음. 기존 schema나 호출이 그대로면 그 부분은 영향 없음으로 종료 |
| 보존 집합 | **재판정 대상에서 제외한 invariant set으로 관리** | Universe 대장에는 원래 상태와 membership만 표시하여 누락을 방지. 새로운 shared/explicit 판단이나 hold 해제 대상이 아님 |
| Current 수치 재도출 | **Change 1의 한 번의 bounded census에 포함** | 실행에 필요한 key sets·pointer·분포만 재도출. 별도 전면 source 재감사나 신규 상설 집합 registry는 만들지 않음 |
| Installed package 확인 | **채택** | Current import owner가 installed package이며 role helper의 source-tree 결합도 확인 필요 |
| 공통 표현 변경 시연 | **기존 compiler 확인에 통합** | 최소 2개 FullType이 공유하는 표현 1건의 전파와 non-target 불변을 확인. 별도 gate를 만들거나 이를 전체 설명 실용성 개선의 대체 증거로 쓰지 않음 |

이 표는 충돌 항목을 숨긴 절충안이나 과거 authority의 인용이 아니라, 상위 계약과 현재 코드에 근거한 **이번 실행 계획의 선택**이다. Human coverage와 pilot의 구체 대상은 Change 1–2에서 실제 source binding을 보고 정한다.

### 4.5 반영된 실행 조건

아래 Change 1–7은 책임과 의존 관계를 설명하는 단위이며, 7개의 독립 실행·승인 Gate가 아니다. 실제 입력 의존성이 허용하면 조사·pilot·구현·검증을 묶거나 순서를 조정할 수 있다. Source 승인 → candidate 채택 → generation → 허용된 T1/T2 소비처럼 기존 계약이 정한 순서는 유지한다. Reviewer별 판정·독립성 이력은 입력 Integrated Review에 남기고, 이 절에는 실행 조건만 둔다. 계획 문서 자체는 acceptance나 검증 PASS를 발급하지 않는다.

| 실행 조건 | 적용 기준 | 실행 위치 |
|---|---|---|
| Acceptance / runtime 관찰 | Pilot 별도 승인은 없으며 채택 전 문장 묶음과 최종 PZ 표본 관찰로 모음. Owner 또는 지정 사람이 판정·관찰하고 실행 AI는 준비·분석·정리를 보조 | §4.1, Change 2 / 4–5 / 7, §7 Manual, §12 |
| Seven-input 확장 | 기존 7개 안에 수용되면 진행. 확장이 필요하면 채택 전 additive authority decision과 계약 정합성을 확보 | Change 3 종료 → Change 5 진입 |
| Core와 Menu detail | Single-core는 용도 수 제한이 아님. 승인된 복수 기본 용도·효과를 보존하고 필수 조건도 core에 유지. 구체 레시피·상세 조건은 Menu에서 제공하되 기본 용도를 identity 제약만으로 이동하지 않음 | Change 3, §7 / §12 |
| Retention과 실제 개선 | 이미 적절함·근거 결손·기존 보존 요구를 유지 사유로 구분. 공유 불가지만 개선 가능한 항목은 explicit로 개선하고 미작업은 미완료로 남김 | Change 1 / 4, §12 |
| 최소 검증 | 신규 독립 검사기·Gate 기본 0. 기존 test family의 미보호 실패 조건만 최소 보완하고 최종 required regression은 기존 strict T1 finalizer가 요구하는 독립 full A/B와 comparator 한 묶음으로 통합(전체 검사는 실제 두 번). 변경되지 않은 범위의 검사를 안심 목적으로 반복하지 않음 | Change 2–7, §7 |
| Empty-core / coverage | Change 1의 재도출 baseline을 control로 사용. 승격은 보존 집합 밖의 승인된 source correction에 한해 허용하고 expression과 coverage delta를 별도 집계 | Change 1–2 / 4 / 6 |
| Clean-Checkout | 실제 import / identity / contract delta가 확정되는 Change 3 종료 시 적용/미적용과 근거 기록 | Change 3, §7 Automated |
| Readpoint / 산출물 보존 | 최종 current readpoint를 동기화하되 historical identity 보존. 임시 integration 정리는 package·evidence·rollback set 보존 후 수행 | Change 7, §10 |

Owner acceptance가 없는 scope는 검토 대장에 `unvalidated_but_in_scope`로 기록하고 해당 범위의 usefulness/naturalness success 및 전체 `complete`를 주장하지 않는다. 이는 새로운 최상위 closeout 상태가 아니라 validation coverage 표기이며, closeout은 기존 `partial` / `implemented_only` / `blocked` 중 실제 상황에 맞춰 기록한다. 근거 있는 기존 `review_hold`와도 구별한다.

---

## 5. Repository Areas Affected

### Code

**주요 수정 후보:**

- `Iris/tooling/src/iris_tooling/build/compose_layer3_text.py`, `compose_layer3_render.py`, `compose_layer3_item.py`, `compose_layer3_body_profile.py`, `compose_layer3_role_material.py`: 기존 compiler 책임 안에서 successor composition 연결.
- `Iris/tooling/src/iris_tooling/build/build_layer3_english_localization.py`: 같은 승인 semantic bundle의 Menu EN / Tooltip core projection.
- `Iris/tooling/src/iris_tooling/build/dvf_3_3_generation_contract.py`: 실제 새 dependency의 identity 결속이 필요한 범위.
- `Iris/tooling/src/iris_tooling/domains/layer3/cli.py`: successor producer 접근이 기존 CLI로 불가능한 경우에만 thin adapter 추가.

**재사용·영향 확인 대상, 무조건 수정하지 않음:**

- `Iris/tooling/src/iris_tooling/build/build_dvf_3_3_complete_generation.py`, `validate_dvf_3_3_complete_generation.py`, `install_dvf_3_3_complete_generation.py`.
- `Iris/build/description/v2/tools/build/layer3_body_role_realign.py`와 해당 source-mapping contract: 기존 의미 판단의 readpoint. 새 package dependency를 historical fallback으로 연결하지 않는다.
- `Iris/tooling/src/iris_tooling/domains/tooltip_t1/`, `domains/tooltip_static_data_projection/`.
- `Iris/tools/package_iris.ps1`, `Iris/tools/Layer3PackageProjection.psm1`.
- `Iris/media/lua/client/Iris/Data/layer3_renderer.lua`, `IrisLayer3DataLookup.lua`, `IrisLayer3EnglishLookup.lua`, `IrisTooltipStaticDataLookup.lua`와 `UI/Detail/IrisItemDetailModelAssembler.lua`, `UI/Tooltip/IrisAltTooltip.lua`: 기본적으로 데이터 소비 확인만 수행.
- 기존 compiler / role-material / generation / Tooltip tests 및 `Iris/test/lua/tooltip_static_data_runtime_harness.lua`, `detail_view_model_locale_harness.lua`.

### Docs

- 본 계획: `docs/iris_dvf_shared_composition_usefulness_menu_tooltip_plan.md`.
- 실행 종료 시 같은 stem의 `_closeout.md` 하나에 subject·변경/보존 집합·결과·미관찰 범위를 기록.
- `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`의 변경은 두 시점으로 분리한다. Canonical input 계약 확장이 필요하면 **adoption 전에** 기존 authority 경로에서 additive decision과 관련 계약 readpoint를 확정한다. Adoption 이후에는 이미 확보한 결정의 실제 적용 결과·current generation·수치를 동기화한다. 과거 closeout을 덮어쓰거나 사후 문서 수정으로 미승인 확장을 정당화하지 않는다.
- `DECISIONS.md`에 언급된 `docs/iris_layer3_body_role_realignment_policy.md`는 작성 시점 checkout에 없다. 이를 현재 존재하는 필수 readpoint로 전제하거나 복구하지 않고, current DECISIONS의 optional role-material 결정과 `Iris/build/description/v2/data/layer3_body_role_realign/`의 실제 mapping/readiness 계약을 사용한다. 새 DVF governance 문서를 만들지 않는다.

### Config

- `Iris/build/description/v2/data/compose_profiles_v2.json`: shared expression 선언을 기존 profile 계약 안에 수용할 우선 위치.
- `Iris/build/description/v2/data/dvf_3_3_facts.jsonl`, `dvf_3_3_decisions.jsonl`, `dvf_3_3_overlay_support.jsonl`, `dvf_3_3_input_manifest.json`: 실제 필요한 binding / provenance / adoption 변경만 수행. 표현 편의를 위해 canonical source text를 대량 재작성하지 않음.
- `Iris/build/description/v2/data/layer3_body_role_realign/`의 기존 mapping / readiness / transformation 계약: successor input이 이 경계를 넘는 경우에만 additive amendment.
- `Iris/_docs/authority/tooltip_t1/`, `Iris/_docs/authority/tooltip_static_data_projection/`: 기존 admission / schema 재사용. Generation-qualified locator가 stale일 때만 승인된 기존 의미를 보존해 재결속.
- `Iris/validation/execution/required_validations.json`, `current_environment.json`, `Iris/tooling/pyproject.toml`: validation / installed package 계약 참조. PASS를 위한 검사 제외나 tooling dependency 완화 없음.

### Generated Artifacts

- `Iris/build/description/v2/data/layer3_body_role_realign/approved_upstream/candidate_rendered.json`: 검토 완료 후 채택하는 generation input. 단순 build output과 구별.
- `Iris/media/lua/client/Iris/Data/IrisLayer3Generations/<successor-id>/` 및 `IrisLayer3DataCurrent.lua`.
- `Iris/media/lua/client/Iris/Data/Layer3English/Index.lua`, `Chunk*.lua`.
- `Iris/build/description/v2/data/tooltip_t1_layer3_owner_input.json`, successor T1 handoff / T2 fixed manifest·receipt.
- `Iris/media/lua/client/Iris/Data/IrisTooltipStaticData.lua`, `IrisTooltipRecipeVariants.lua`.
- Generation·T1/T2의 외부 output root, 최종 package `Iris/` / `Iris.zip`. Package만 허용된 `.tmp/package/<run>/` staging을 사용할 수 있으며 다른 producer의 외부 root 제한과 혼동하지 않음.
- Census / membership / semantic-surface delta / 검토 결과는 task evidence로 보존하며 새로운 fact source·상설 validator·runtime payload로 넣지 않음.

---

## 6. Planned Changes

### Change 1 — Current subject와 composition 대상 결속

**Purpose:** 현재 승인된 의미와 표면을 분리해 조사하고, 후속 변경의 분모와 보존 경계를 확정한다.

**Files:** §5 Config의 current facts / decisions / manifest / approved candidate, pointer-selected generation, EN / Tooltip owner / fixed / companion, 기존 source review 자료.

**Implementation Notes:**

1. Exact HEAD·working-tree delta, pointer, canonical inputs와 generated output identity를 기록한다. 문서에 적힌 이전 generation보다 실제 pointer/input을 우선 확인하되 불일치를 자동 승인하지 않는다.
2. DVF universe, KO/EN public sets, silent, S2 core, **universe 내부 empty-core**, absence, support, S1 partition, T2 줄 수 분포, Recipe item/variant 집합을 한 번 추출한다. Empty-core는 명시적 빈 core 목록에서 직접 추출하고 S2 owner 부재 및 public/silent 분할을 대조한다. 보호·hold는 원래 owner record의 exact membership을 확인하고 empty-core와의 교집합을 기록한다.
3. FullType별로 `source slot/provenance → approved semantic material → current core/Menu body → 후보 production path → retain/exception reason → correction dependency`를 대조한다.
4. 비슷한 문구는 표현 후보를 찾는 데만 사용한다. 같은 의미 구조라는 판정은 source-bound target/effect/value/condition으로 확인한다. 현재 record가 scalar 문장·넓은 origin·검토 문서 링크만 제공하면 그것을 typed source value로 간주하지 않는다.
5. 보존 집합은 읽기 전용 invariant로 분리한다. 나머지는 shared / explicit / retained / correction-required로 나누되 기존 body disposition과 readiness를 덮어쓰지 않는다.
6. Retention 사유는 기존 대상표에서 **이미 적절한 설명 / 근거 결손으로 안전한 변경 불가 / 기존 보호·보류·부재 계약에 따른 보존**을 구분한다. 현재 정보로 개선이 가능하지만 공유 구조에 맞지 않는 항목은 explicit 개선 대상이다. 미작업·일정·구현 편의는 retention 사유가 아니며 남은 작업으로 기록한다. 이 구분은 작업 설명용이며 새 source 상태·schema·상설 registry를 추가하지 않는다.

**Validation:** duplicate / missing / unexpected exact keys, KO/EN 차집합, empty-core와 S2 core의 분할 및 malformed core field, preservation membership, source locator의 실제 존재 확인. 기존 2,105건 전체의 게임 source truth 재감사는 하지 않는다.

**Deliverable / Exit:** 재현 가능한 baseline과 task-local 대상표. Source가 부족한 항목도 사유가 있는 retention 또는 correction dependency로 남기며 누락하지 않는다. 연결 경로와 표현 개선 필요성을 구분하여, shared로 연결했다는 사실만으로 품질 개선 완료를 표시하지 않는다. Current mutation은 0이다.

---

### Change 2 — 최소 composition 계약과 수직 pilot

**Purpose:** 실제 source → compiler → KO/EN core/Menu candidate 연결을 작은 범위에서 확인한다. Change 3의 개발·확인에 통합할 수 있으며, 이 절을 별도 승인 단계로 만들지 않는다.

**Files:** `compose_profiles_v2.json`, §5 compiler 파일, existing role-material input / fixture. 신규 작은 data/module이 필요하면 installed package 내부에만 두며 병렬 engine은 만들지 않는다.

**Implementation Notes:**

1. 계약에는 다음 개념만 둔다. 구체 field 이름과 version은 corpus에서 확인한 필요에 따라 정한다.
   - Optional shared composition identity와 source-bound applicability.
   - Item별 source fact / semantic value / target / effect binding.
   - Truth-critical condition / qualifier와 명시적 optional block.
   - Explicit item body와 근거·승인에 결속된 retention 경로.
   - 같은 semantic claim bundle을 소비하는 KO/EN renderer 및 Tooltip용 core와 Menu-only detail의 구분.
2. Membership은 승인된 binding으로 미리 확정한다. Compiler가 FullType 이름, classification, broad action label, source mod ID나 Build version으로 새로운 의미 분기를 만들지 않는다.
3. 예컨대 기술서는 기술·적용 레벨·읽기 조건·경험치 배율 효과가 source에서 구조적으로 확인될 때만 shared 후보로 삼는다. `BookCarpentry1`의 이름이나 현재 문장으로 레벨 숫자를 복원하지 않는다.
4. Pilot은 실제 공유군 하나에서 값이 다른 최소 2개 FullType의 KO/EN core와 필요한 조건 binding을 확인하는 작은 개발 사례로 시작한다. 독립된 모든 조건·exception·retention·empty-core·silent/absence 사례를 pilot에 다시 갖출 의무는 없다. 새 경로의 실제 위험은 기존 compiler 검사의 최소 사례로 보완하고, 이미 보호되는 경계와 전체 집합 보존은 기존 검사·최종 integration 결과로 확인한다.
5. Source 값과 의미는 고정한 채 공유 표현 1건을 변경하여 최소 2개 FullType에 전파되는 것을 확인한다. 차이는 두 locale의 표현과 serialization에 귀속하고, 비대상·조건·public decision은 보존한다.
6. Pilot은 off-live candidate와 owner projection 경계까지 수행한다. 전체 T1/T2/package/full regression은 최종 integration에서 수행한다.

**Validation:** unknown composition, missing/conflicting binding, condition 누락, invalid exception, locale 간 claim mismatch는 fail-loud. Explicit retention은 사전 결정된 정상 path이며 실패 후 자동 fallback이 아니다.

**Stop conditions:** prose/name/classification 추론 필요, truth-critical condition 유실, hidden semantic branch 필요, KO/EN 중 한쪽에 fact 추가·삭제 필요, 공통 표현 전파 없이 어미만 바뀌는 결과. 해당 공유군의 확대를 중단하고 계약을 수정하거나 explicit/retained로 전환한다. 근거 부족인 일부 항목을 이유로 안전한 다른 공유군까지 강제 보류하지 않는다.

**Deliverable / Exit:** 최소 successor contract, source-bound pilot comparison과 공유 표현 변경 시연. 전 corpus로 확장할 production path가 실제로 확인되어야 한다. 이때 실행 AI는 문장 초안과 문제점을 검토하되 human acceptance를 발급하지 않는다. 표현 선호의 확정은 Change 4의 묶음 검토에 포함하고, pilot을 이유로 별도 사람 승인이나 중단 조건을 추가하지 않는다.

---

### Change 3 — 기존 Body Compiler와 bilingual/core projection 연결

**Purpose:** 새 composition을 기존 production owner 안에서 구현하고, Menu와 Tooltip이 동일한 승인 core를 받을 수 있게 한다.

**Files:** §5 주요 compiler / EN / domain CLI / generation identity 파일 및 기존 관련 tests.

**Implementation Notes:**

1. Shared declaration과 source binding을 받아 **승인 전 candidate**를 만드는 경로를 기존 Body Compiler에 구현한다. `build_complete_generation`에 semantic inference를 넣거나 adopted candidate를 손으로 패치하는 것을 정상 생산 경로로 삼지 않는다.
2. KO/EN core는 같은 fact/effect/condition/exception bundle에서 생성한다. Menu context·acquisition은 별도 detail로 보존한다. **Menu-only detail은 생략해도 core의 사실성이 변하지 않는 정보에만 허용**하며, S2의 truth-critical condition은 Menu에 있다는 이유로 분리·생략하지 않는다.
3. `build_english_entries`와 `build_tooltip_t1_owner_entries`가 successor의 승인된 bilingual core를 명시적으로 소비하게 한다. Existing scalar translation은 명시된 retained/legacy-compatible item의 경로로만 유지하고, 새 composition 실패를 조용히 가리는 fallback으로 쓰지 않는다.
4. 기존 S2 single-core contract는 **공개 core identity가 하나라는 제약**으로 유지하며 기본 용도를 하나로 제한하지 않는다. 승인된 core에 포함된 복수 기본 용도·효과는 함께 보존한다. 예를 들어 승인 근거가 섭취 효과와 요리 재료 사용을 함께 뒷받침하면 이를 S2에 함께 표현할 수 있으며 구체 조리법은 Menu에서 제공한다. 복수 role/condition의 표현이 필요해도 source 없이 새 core ID를 합성하거나 `MULTIPLE_CORE_FACTS_FORBIDDEN` 검사를 제거하지 않는다. 새로운 기본 용도 추가는 필요한 source correction·승인 경로를 따르고, 실제 상세 정보만 Menu-only detail로 구분한다. Identity가 하나라는 이유만으로 기존 기본 용도를 Menu로 이동하지 않는다. Truth-critical condition을 안전하게 표현할 수 없으면 explicit core 표현 또는 correction dependency로 처리하며, Menu 본문에만 조건을 넣고 불완전한 S2를 공개하지 않는다.
5. 표현만 바뀌면 canonical fact/provenance/decision은 보존한다. Source-value-hash에 결속된 ID가 실제 source correction 때문에 달라질 때에는 old/new source와 ID relation을 owner 경로에서 기록한다. “같은 의미처럼 보인다”는 이유로 hash guard를 우회하지 않는다.
6. 현재 seven-input 안의 profile/overlay/candidate에 필요한 계약을 수용하는 것을 우선한다. 별도 composition 파일이 실제 canonical input이 되면 기존 7개 계약의 확장으로 분류하고, **successor candidate adoption 전에** 기존 authority 경로의 additive decision을 확보한 뒤 `CANONICAL_INPUTS` / 관련 validation / 계약 readpoint를 일치시킨다. Renderer 구현 closure 변경과 canonical input 추가는 구분하되, 어느 쪽도 실제 dependency identity에서 빠뜨리지 않는다. 미승인 확장은 off-live 실험에 한정한다.
7. `compose_layer3_role_material`의 helper를 사용할 경우 wheel에서의 실제 import를 확인하고 필요한 책임만 package owner로 옮기거나 기존 package-owned 함수로 연결한다. Description-tree 복사본을 current fallback으로 승격하지 않는다.

**Validation:** 기존 compiler tests가 보호하지 않는 실제 새 실패 조건과 semantic binding에 한해 최소 사례를 보완한다. Same-input off-live candidate A/B, 순서·경로 독립성, invalid binding, explicit exception, retained bytes, locale parity는 적용되는 기존 검사에서 함께 확인한다. 각 항목마다 새 test file·독립 실행을 만들거나 문장별 snapshot을 추가하지 않는다. 공유 표현 전파 사례에 복수 기본 용도 보존을 함께 확인할 수 있으며 동일 사례를 별도 Gate로 복제하지 않는다. Fixture와 source-root imports만 통과한 것을 installed path 검증으로 인정하지 않는다.

**Deliverable / Exit:** 설치 가능한 tooling의 successor producer, 최소 schema/fixture 변경, off-live bilingual candidate와 fail-loud 결과. 다음 분기를 기록한 뒤 진행한다. Current pointer는 아직 변경하지 않는다.

| 확정된 input delta | 후속 진행 조건 |
|---|---|
| 기존 seven-input 안에 수용 | 실제 dependency identity 누락이 없음을 확인하고 Change 4로 진행 |
| Seven-input 확장 필요 | 확장 사유·정확한 input/identity 영향과 **adoption 이전 additive authority decision**을 기존 DECISIONS 및 관련 계약에 결속한 뒤 진행 |
| 필요한 authority decision 미확보 | Seven-input 내부 방식으로 되돌리거나 해당 확장 경로를 `blocked`로 남김. 미승인 경로의 candidate 채택·current 설치·package 전달은 금지 |

이 종료 시점에 실제 import / compiler closure / input contract delta를 근거로 **Clean-Checkout 적용 또는 미적용과 이유**도 task evidence에 확정한다. 판정 불가를 N/A로 처리하지 않는다. 이후 실제 delta가 달라지면 영향받은 적용 판단만 갱신하며, 해당 검사 실행은 최종 integrated subject에 모은다. 새 독립 gate는 추가하지 않는다.

---

### Change 4 — Whole-universe 연결과 새 표현 검토

**Purpose:** Full-corpus를 누락 없이 적절한 생산 경로에 연결하고 adoption 가능한 candidate를 완성한다.

**Files:** §5 source/binding inputs와 compiler output, task-local exact disposition / delta 자료.

**Implementation Notes:**

1. Change 1의 대상 전부를 shared / partial block / explicit / retained / correction-required에 연결한다. 보존 집합은 상태를 재판정하지 않고 invariant membership을 병기한다.
   - 연결 상태와 실용성 개선 결과를 구분한다. 근거가 충분하고 개선 필요성이 확인된 항목은 shared 또는 explicit 경로로 실제 표현을 개선한다.
   - 공통화하기 어렵다는 이유만으로 기존 번역투를 유지하지 않는다. 근거 결손이나 보존 요구에 따른 retention은 이유와 영향 범위를 남기고, 아직 작업하지 못한 항목은 미완료로 기록한다.
2. Changed item마다 surface delta, semantic delta와 **coverage delta**를 구분한다. Fact/effect/value/condition/provenance/decision이 바뀌면 기존 source owner의 정정 → approved material → composition 순서로 처리한다. Empty-core → S2 core 출현은 문구 변경 수에 묻지 않고 exact gained/lost/unchanged key set으로 별도 집계한다.
3. Required condition은 짧은 문장을 위해 제거하지 않는다. Layer 4에 detail이 존재한다는 사실도 core의 truth-critical condition 생략 근거가 아니다.
4. Retained item은 승인된 input과 provenance를 명시적으로 이어받는다. Generated runtime/descriptor를 canonical semantic input으로 다시 투입하지 않는다. Retention은 새로운 semantic-quality 승인도 아니다.
5. 새 shared expression structure, 의미 또는 문법에 영향을 주는 condition/exception 변형, semantic correction, detected outlier를 대표 KO/EN 출력으로 묶는다. 같은 구조의 값 치환을 별도 family나 별도 사람 검사로 늘리지 않고 slot-value binding은 자동 대조한다. 다른 구조로 취급해야 하는 실제 차이는 숨기지 않는다. 이 범위와 Change 1의 유지·미완료 사유를 기존 대상표·차이 자료에 함께 정리하며 별도 보고서 체계를 만들지 않는다.
6. 실행 AI는 source binding·대표 before/after KO/EN 출력·검사 결과를 준비하고, **owner 또는 owner가 지정한 사람**에게 채택 전 exact candidate의 문장 묶음 수용을 한 번에 요청한다. 판정은 묶음 안의 범위별 채택/수정/보류를 구분할 수 있다. Pilot·family·item별 선행 승인은 요구하지 않으며, 이후 변경은 영향받은 표현·의미·binding 범위만 추가 검토한다. Candidate hash 변경만으로 동일한 검토 내용을 전부 재승인받지 않고, 변경 전후 내용과 이미 검토한 범위를 새 candidate에 추적 가능하게 연결한다. 미승인 family/item은 `unvalidated_but_in_scope`이며 해당 범위의 semantic-quality success나 전체 `complete`를 주장하지 않는다. LLM 평가·실행 허가·evaluator PASS를 human acceptance로 대신하지 않는다. 기존 public-text evaluator가 필요하면 기존 no-write 경로만 사용한다.

**Empty-core 승격 정책:** 57개를 채우는 것은 목표가 아니다. 기본 예상은 S2 coverage 불변이며, Change 1에서 확정한 **보존 집합 밖** empty-core에 한해 해당 FullType의 source-bound description-eligible material을 실제로 확인하고 기존 source/decision owner의 correction·approval과 위 human acceptance를 확보하면 successor S2 승격을 허용한다. Single-core·필수 조건·KO/EN·T1 admission 계약을 모두 만족해야 하며, 승인 범위에 exact 대상과 coverage 변화 이유를 포함한다. 이름·prose·classification 또는 compiler 자동 fallback에 의한 승격은 금지한다. Silent/hold/protected/explicit absence의 재판정은 이 분기로 허용하지 않는다. 조건 미충족 시 근거 있는 기존 상태/retention을 보존하고 발견한 source gap을 기록한다.

**Validation:** exact universe reconciliation, public/silent와 source-bound core/empty-core key sets, condition 보존, expression/semantic/coverage delta, KO/EN claim parity, placeholder/raw token/nil 누출, protected/absence/hold 불변. Gained core마다 source owner 승인과 human acceptance를 대조하고, 승인 밖 coverage 증감은 실패로 처리한다.

**Deliverable / Exit:** candidate set, semantic/surface/coverage diff, issuer·검토 범위·candidate identity에 결속된 public-text acceptance, retained/hold 및 unresolved 이유. 구조가 작동하는 시연과 실제 설명 개선 범위를 구분한다. 개선 가능한 미작업 항목을 retention으로 바꾸어 종료하지 않으며, 미승인 검토 대상이나 안전한 approved retention 없이 남은 scope 내 actionable gap이 있으면 adoption-ready라고 하지 않는다.

---

### Change 5 — Candidate adoption과 Layer 3 generation 준비

**Purpose:** 승인된 candidate를 official generation input에 연결하고 Menu용 successor KO/EN을 준비한다.

**Files:** `approved_upstream/candidate_rendered.json`, input manifest, complete-generation builder / validator / installer, EN producer, pointer와 generation payload.

**Implementation Notes:**

1. Change 3의 canonical-input 분기와 필요한 사전 authority decision, Change 4의 **owner/지정 사람에 의한 public-text acceptance**를 확인한 뒤 candidate의 exact bytes와 승인 범위를 기존 adoption boundary에 결속한다. 과거 승인 metadata나 descriptor를 새 승인으로 간주하지 않는다. 일반 실행 authorization, 문장 acceptance, source approval은 각각의 범위를 구분한다.
2. Approved input에서 외부 root로 complete generation A/B를 만들고 stateless/key validation을 수행한다. 기존 current generation은 제자리 수정하지 않는다.
3. 현재 EN producer는 pointer-selected generation/input을 요구하고 고정 `Layer3English/`에 쓴다. 따라서 **격리 integration checkout**에서 expected predecessor를 확인해 successor pointer를 설치한 뒤 EN과 owner projection을 생성한다. 이 중간 checkout을 사용자 설치용 package로 전달하지 않는다.
4. 이 순서의 pointer switch는 KO generation에 한정된다. EN/fixed/companion까지 원자적이라는 주장은 하지 않는다. 실제 사용 중인 게임 폴더를 작업 대상으로 삼지 않으며 live reload를 요구하지 않는다.
5. KO public와 EN public의 exact set·same semantic input relation을 대조하고, independent Menu consumer 경로에서 successor body가 읽히는지 확인한다. Owner가 자신이 생성한 output을 비교한 결과를 Menu observation으로 발급하지 않는다.

**Validation:** candidate/input hash binding, generation A/B, immutable install / expected-predecessor / pointer readback, KO/EN symmetry, exact FullType, cross-locale fallback 부재. Installer 검사를 재사용할 때에는 installer 및 관련 contract/의존 경로의 diff·identity로 `installer unchanged`와 기존 evidence의 적용 가능성을 기록한다. 근거가 유지되면 기존 failure injection 전부를 독립 단계로 다시 반복하지 않으며, install 의미에 영향이 있으면 해당 failure path를 검증한다.

**Deliverable / Exit:** approved successor input, validated immutable generation, isolated Menu KO/EN set. 사용자에게 전달하는 current coherent set의 확정은 Change 6 이후다.

---

### Change 6 — Strict T1 / T2 / Recipe companion / package 통합

**Purpose:** 같은 승인 core를 Alt Tooltip과 최종 설치 후보까지 전파한다.

**Files:** Layer 3 owner input, `domains/tooltip_t1/`, `domains/tooltip_static_data_projection/`, fixed / companion Lua, package tools와 기존 runtime harness.

**Implementation Notes:**

1. Successor core owner를 발행한다. `entries`와 `absence_entries`를 유지하고 core ID·locale surface·generation-qualified authority ref를 대조한다. S2 core / empty-core의 gained/lost 집합이 Change 4에서 승인된 coverage delta와 정확히 같아야 한다. 승인된 coverage 변화가 없으면 **Change 1에서 재도출·확정한 exact baseline**을 유지한다. 작성 시점 관측값과 다르더라도 Change 1에서 확정한 집합·수치가 control이다.
2. 기존 strict T1 admission / whole-audit 및 finalization 경로를 사용한다. S1/S3/S4 의미 선택은 그대로 두고, 현재 generation과 aggregate input hash로 인해 stale인 locator/binding만 필요한 범위에서 갱신한다. 기존 D5 exact-key correction 등도 의미 재판정과 locator 재결속을 구분한다.
3. T2가 요구하는 admitted/finalized handoff에서 fixed KO/EN을 생성한다. 기존 T2 A/B와 finalize receipt를 재사용 가능한 한 번의 실행 묶음으로 처리하며 `--completion-metadata-json`에 미실행 검사의 exit code를 넣지 않는다.
4. 격리 checkout에 successor fixed를 배치한 뒤 기존 `recipe_variants.py`로 companion을 생성한다. 각 variant의 base가 exact successor fixed와 대응하고 L2/L3 및 Right-click 보존 부분이 같아야 한다. 현재의 349/781은 control 값이며 QG input 미변경 상태의 예상 밖 증감을 조사한다.
5. KO pointer-selected generation + EN + fixed + companion + 현재 runtime source를 하나의 coherent 전달 set으로 준비한다. Package는 현재 generation 하나만 포함하고 stale `.tmp`/과거 package를 입력으로 사용하지 않는다.
6. Package builder의 기존 source 보호·current projection 검사와 final source/package identity를 확인한 뒤 `Iris/`와 `Iris.zip`을 만든다. 최종 source와 package 모두 같은 successor set이어야 하며 부분 반영 상태를 완료로 남기지 않는다.
7. 기존 strict T1 finalizer가 요구하는 동일 subject의 독립 canonical full Run A/B와 deterministic comparator를 최종화에 한 묶음으로 수행한다. 전체 회귀는 실제 두 번이며 한 번으로 기록하지 않는다. 이 필수 묶음 밖의 추가·단계별·안심 목적 full 반복은 하지 않는다. T2/fixed/companion/package의 후속 delta는 기존 계약상 영향받는 검사만 수행하고 이전 subject의 PASS를 최종 제품 전체에 상속하지 않는다.

**Validation:** strict T1 identity/readiness, T2 determinism, fixed/companion base parity, 0–4 logical rows, supported keys/locales, Menu와 S2 core relation, Lua syntax, existing Tooltip/Detail harness, package current-generation-only 및 EN/fixed/companion bytes. Search 구현 미변경 시 별도 search 전수 재검증을 추가하지 않는다. 기존 required suite에 포함된 검사는 임의 제외하지 않는다.

**Deliverable / Exit:** successor T1 handoff와 T2 결과, matching Recipe companion, coherent source/package, final integrated regression evidence. 이 단계는 게시·release certification이 아니다.

---

### Change 7 — 실제 표면 확인과 current closeout

**Purpose:** 최종 candidate에서 사용자가 읽는 의미와 consumer 연결을 확인하고 완료 범위를 닫는다.

**Files:** final package, 본 계획과 후속 closeout, 변경된 current authority readpoint만.

**Implementation Notes:**

1. §7의 representative runtime scope를 KO/EN에서 확인한다. Change 4의 expression-family text acceptance와 실제 게임에서의 표시 관찰을 따로 기록한다.
2. 확인하는 질문은 기본 용도·효과·필수 조건이 이해되는지, Menu가 같은 core에 기존 detail을 더하는지, S2/fixed/Recipe view에 이전 문장이 남지 않았는지다.
3. 최종 변경으로 새 expression variant가 생기면 그 variant의 review만 보완한다. Unchanged family 전체나 full suite를 자동 반복하지 않는다.
4. **이미 adoption 전에 확보한** contract decision의 실제 적용 결과·생산 경로·수치를 DECISIONS / ARCHITECTURE / ROADMAP에 최소 반영한다. 관련 decision family에서 predecessor를 아직 `current generation`으로 표기한 필드와 empty-core/S2 current 수치도 확인한다. Historical 결과·sealed identity 자체는 바꾸지 않는다. 부재한 policy path와 실제 사용한 successor readpoint의 관계를 closeout에 기록하며, 부재 문서를 복구해 authority를 만들지 않는다.
5. Closeout 하나에 exact subject, source-to-composition trace, current generation, fixed/companion/package identity, 자동 검증, acceptance issuer·범위·미승인 항목, observed/unobserved, coverage delta, retained/hold, 남은 제약을 기록한다. Final package·필요 evidence·rollback set을 보존한 뒤에만 §10의 소유권·경로 확인을 거쳐 임시 integration 산출물을 정리한다.

**Validation:** 필수 결과가 같은 final subject에 귀속되는지와 claim ceiling 확인. 미관찰·도구 부재·unresolved를 PASS로 바꾸지 않는다.

**Deliverable / Exit:** §12의 조건에 맞는 closeout. Owner가 실제 관찰하지 않은 내용을 대신 승인했다고 쓰지 않는다.

---

## 7. Validation Plan

### Automated Validation

**2026-08-31 실행 정정:** 지정 검토 작업 `01a05297-eb3f-78d3-a5bd-fc44c02dac71`에서 `tooltip_t1/audit.py:finalize_closeout` 및 T2 admission의 실제 필수 계약을 확인했다. 기존 제품 계약은 조건부 Clean-Checkout 결정으로 면제되지 않으므로 계획의 일률적인 full 1회 문구를 필수 독립 A/B 묶음에 한해 정정한다. 사용자 사전 승인으로 새 승인 대기는 만들지 않는다. 기존 launcher/finalizer/receipt/OPEN 요건은 완화하지 않으며 별도 validator나 gate는 추가하지 않는다. 같은 subject·scope의 regression/harness를 묶음 밖에서 중복 수행하지 않는다. 사전 승인과 실제 사람 문장 검토·PZ 관찰의 수행 사실은 구분한다.

검증은 변경된 책임에 귀속한다. Producer A/B는 candidate / complete generation / T2 등 결정성이 필요한 기존 경로에만 적용하며, 같은 final input으로 얻은 결과는 해당 계약이 허용하는 범위에서 재사용한다. 새로운 독립 validator/gate는 기본 0이다.

**최소 실행 원칙:** 아래 표는 보호할 책임과 기존 검증 위치를 연결한 것이며 각 행을 별도 실행·보고·승인 단계로 만들라는 목록이 아니다. 개발 중 focused 검사는 실제 변경·실패를 확인하는 데 필요한 범위만 실행하고, 최종 current required regression은 기존 strict T1 finalizer의 필수 동일-subject canonical full A/B와 comparator 한 묶음으로 모은다. 전체 두 번을 한 번으로 축소 기록하거나 같은 실행을 A/B로 이중 계상하지 않는다. Finalizer·package builder·최종 launcher가 이미 동일 입력·구현·환경·검사 범위에서 수행한 확인은 계약이 허용하면 재사용하며 같은 harness나 전체 suite를 바깥에서 다시 돌리지 않는다. 기존 검사로 보호되지 않는 실제 실패 조건만 기존 test family의 최소 사례로 보완하고, 문장마다 snapshot·테스트를 추가하거나 구현을 그대로 복제하는 검사는 만들지 않는다. Table·명령 예시·Change별 Validation 문구 자체는 추가 Gate가 아니다. 기존 제품 계약의 필수 검사·receipt·admission은 유지하고 새 결함은 영향받은 범위만 재검증한다.

| 검증 대상 | 재사용할 구현 | 핵심 확인 |
|---|---|---|
| Composition / source binding | `Iris/build/description/v2/tests/test_compose_layer3_text_v2.py`, `test_layer3_body_role_realign.py`와 기존 fixture | Missing/conflicting binding, 조건 보존, exact identity, explicit/retained 경로. Source-tree helper 테스트만으로 installed path를 보증하지 않음 |
| Generation / install | 같은 tests 디렉터리의 `test_dvf_3_3_complete_generation.py`, `test_dvf_3_3_generation_install.py` | Adopted input, dependency closure, deterministic output, predecessor guard |
| T1 | `Iris/tooling/tests/test_tooltip_t1_contract.py`, `test_tooltip_t1_projection.py`, `test_tooltip_t1_audit.py` | Core identity, strict admission, unchanged owner selection, absence 보존 |
| T2 / companion | `Iris/tooling/tests/test_tooltip_t2_projection.py`, `test_tooltip_t2_serialization.py`, `test_tooltip_t2_cli.py` | KO/EN 고정 배열, A/B, base correspondence, 0–4줄, stale pair 거부 |
| Runtime consumer | `Iris/test/lua/tooltip_static_data_runtime_harness.lua`, `detail_view_model_locale_harness.lua` | Actual Lua lookup, locale / empty-core / nil, Recipe opening view, Menu readback, Kahlua `next=nil` control |
| Package | `Iris/tools/package_iris.ps1`, `validate_layer3_package_projection.ps1` | Current generation 하나, EN/fixed/companion exact final payload, source 보호 |
| Final regression | `Iris/validation/execution/run_required_contract_tests.py` 및 current required manifest / 적용되는 canonical launcher | 최종 integrated input에 기존 required tests. 과거 test 수를 새로운 고정 분모로 복제하지 않음 |

실행은 PowerShell에서 한다. 아래는 실제 구현에서 확인한 interface이며, `$irisRepo`, `$irisRunRoot`, `$irisSubjectCommit` 등은 후속 실행의 검증된 실제 경로·subject로 설정한다. 아직 존재하지 않는 successor 입력이나 receipt를 현재 있는 것처럼 실행하지 않는다.

| 명령 변수 | 준비 단계와 의미 |
|---|---|
| `$irisRunRoot`, `$irisRepo` | Change 1의 task별 output 기준 root와 repository context. Change 5–6의 mutation 명령에서는 successor를 준비하는 **격리 integration checkout**을 `$irisRepo`로 사용하고 그 루트에서 실행 |
| `$irisSuccessorId` | Change 5에서 검증·설치한 generation descriptor/pointer의 실제 ID |
| `$irisT1Root`, `$irisDecisionHash`, `$irisMenuRelation` | Change 6의 새 T1 외부 output, 현재 decision-contract hash, 해당 입력과 일치하는 Menu relation |
| `$irisHandoffRoot`, `$irisT2RunA`, `$irisT2RunB` | 기존 T1 finalizer가 허용한 handoff와 서로 분리된 T2 외부 output roots |
| `$irisRecipeOutput` | Change 6의 격리 checkout 내부 companion output. 같은 checkout에 successor fixed가 먼저 배치되어야 함 |
| `$irisPackageRoot`, `$irisPackageDataRoot` | Change 6의 명시적 새 package output과 그 아래 `Iris/media/lua/client/Iris/Data` |
| `$irisSubjectCommit`, `$irisClaimId`, `$irisEnvironmentReceipt`, `$irisWorkRoot`, `$irisResultRoot`, `$irisOrchestrationReceipt` | Change 3에서 필요 여부를 판정하고 Change 6에서 실제 확정하는 canonical 검증 subject·식별자·환경 receipt·외부 작업/결과/receipt 경로. Placeholder나 과거 subject를 새 결과로 사용하지 않음 |

```powershell
# Python은 승인된 installed tooling 환경에서 uv run python을 사용한다.
uv run python -m iris_tooling --help

# 확정된 successor owner 입력에서 strict T1 생산.
uv run python -m iris_tooling --repository-root $irisRepo build layer3 publish-tooltip-t1-owner
uv run python -m iris_tooling --repository-root $irisRepo build tooltip-t1 --output-root $irisT1Root --decision-contract-sha256 $irisDecisionHash --verify-invariants --strict-production-handoff --layer2-menu-relation $irisMenuRelation

# 기존 T1 finalizer가 허용한 exact handoff에서 T2 A/B를 생성.
uv run python -m iris_tooling --repository-root $irisRepo build tooltip-t2 --handoff-root $irisHandoffRoot --output-root $irisT2RunA
uv run python -m iris_tooling --repository-root $irisRepo build tooltip-t2 --handoff-root $irisHandoffRoot --output-root $irisT2RunB

# successor fixed가 배치된 격리 checkout. Output은 이 checkout 내부여야 한다.
uv run python -m iris_tooling.domains.tooltip_static_data_projection.recipe_variants --repository-root $irisRepo --output $irisRecipeOutput

# 필수 Lua 구문 검사: 정확한 명령이 exit 0인 경우에만 PASS.
# 최종 실행기가 같은 subject에서 이미 이 명령을 수행했다면 해당 결과를 재사용한다.
powershell -ExecutionPolicy Bypass -File .\tools\check_lua_syntax.ps1

# 제품 전달 후보. 작업 checkout 루트에서 실행하고 새 명시적 output root를 사용.
powershell -ExecutionPolicy Bypass -File .\Iris\tools\package_iris.ps1 -OutputRoot $irisPackageRoot -Zip -PackageApplicability current_runtime_payload
# 같은 package/기대 generation에 대해 위 builder가 동일 검사를 이미 수행했다면 중복 실행하지 않는다.
powershell -ExecutionPolicy Bypass -File .\Iris\tools\validate_layer3_package_projection.ps1 -DataRoot $irisPackageDataRoot -ExpectedGenerationId $irisSuccessorId
```

위 명령표는 adoption·generation·T1/T2 finalize를 생략한 자동 실행 스크립트가 아니다. 이 단계들의 순서는 Change 5–6을 따르고 actual args/receipts는 기존 구현과 실행 기록에 남긴다. 특히 generation module은 repository context를 명시적으로 구성한 package invocation으로 호출하며 import-time repository context를 source-tree import로 우회하지 않는다.

Installed path 검증은 새 wheel을 격리 환경에 설치하고 import origin이 installed package인 상태에서 최소 하나의 실제 successor candidate를 생성해 source 결과와 대조한다. Pilot 또는 최종 생성이 이 조건을 충족하면 그 결과를 사용하며 별도 시연 실행을 추가하지 않는다. `--help` 성공이나 package import만으로 production 검증을 대신하지 않는다.

Canonical Clean-Checkout의 적용/미적용은 **Change 3 종료 시점**에 최신 DECISIONS와 실제 변경된 환경/import/identity 계약을 근거로 결정하고 이유를 남긴다. 이후 delta가 달라지면 그 적용 판단만 재확인한다. 적용되는 경우 실행은 Change 6의 final integrated subject에서 기존 launcher `Iris/validation/execution/invoke_repository_tests.ps1` 또는 다음 CLI로 수행하고, 그 안에 포함된 final required regression을 외부에서 중복 실행하지 않는다. 미적용이라고 판단해도 별도로 적용되는 기존 required regression을 생략하지 않는다.

```powershell
uv run python -m iris_tooling --repository-root $irisRepo validate full --commit $irisSubjectCommit --claim-id $irisClaimId --environment-receipt $irisEnvironmentReceipt --work-root $irisWorkRoot --result-root $irisResultRoot --orchestration-receipt $irisOrchestrationReceipt
```

Required tooling·입력·유효 receipt가 없으면 해당 검증은 **BLOCKED**다. 정확한 relevant command가 exit `0`인 경우에만 PASS를 기록한다. Java/Gradle·JS/TS 변경은 예정하지 않으므로 `.\gradlew test`와 `pnpm biome check .`는 현재 범위에 N/A이며, 실제로 해당 코드를 변경하면 사용자 지정 검증을 적용한다.

### Manual Validation

**문장 acceptance:** 판정 주체는 owner 또는 owner가 지정한 사람이며, 기존 Publish Boundary가 소유한 public-text acceptance 중 이번 candidate의 문장 수용만 다룬다. Change 4의 새 표현 구조와 의미·문법에 영향을 주는 조건/exception 변형, semantic correction, detected outlier를 대표 KO/EN before/after와 source binding으로 묶어 **채택 전 한 번의 검토 요청**으로 제공한다. 유지 사유와 개선 범위도 같은 자료에 포함한다. 값만 다른 동일 구조는 자동 binding 대조를 활용하고, 같은 아이템·표현을 다른 이름의 검사로 반복 제시하지 않는다. 별도 pilot 승인, item별 승인, 새 평가 점수·문장 품질 Gate는 만들지 않는다. 필요한 수정 뒤에는 영향받은 범위만 추가 검토하며 issuer·수용 범위·candidate identity 연결을 유지한다. 실행 AI의 자료 준비·검토 의견이나 자동 평가만 있는 범위는 `unvalidated_but_in_scope`다. Publication/release 승인까지 요청하거나 승인됐다고 주장하지 않는다.

**실제 consumer/UI observation:** 표본 범위의 확정과 실제 PZ 관찰은 **owner 또는 owner가 지정한 사람**이 담당하며, 실행 AI는 표본 후보·확인 항목 준비와 전달된 결과 정리만 보조한다. **최종 package의 한 번의 묶음 관찰**을 기본으로 하고, 수정 후에는 영향받은 표면만 다시 확인한다. 아래는 변경과 실제 겹치는 관찰 범위를 선택하기 위한 기준이며 항목별 별도 실행·Gate가 아니다. 같은 아이템으로 여러 범위를 확인하고 이미 자동으로 보호되는 미변경 경계는 관련 결과를 활용하여 수동 표본을 최소화한다. 최종 표본은 새 shared 표현의 아이템별 값 차이, 조건·KO/EN, 실제 Menu/S2 반영을 확인할 수 있어야 한다.

- 공통 표현을 공유하지만 기술/대상/내용물 등 값이 다른 아이템 2개 이상.
- 진위에 영향을 주는 조건이 있는 항목과 explicit exception.
- 승인된 복수 기본 용도가 S2에 함께 남고 Menu에는 구체 사용법이 더해지는 항목, 또는 Menu-only context/acquisition이 있는 항목.
- Retained item, legitimate silent / empty-core / explicit absence control.
- Recipe companion 대상과 비대상, KO/EN 장문 사례.

실제 Menu와 S2에서 새 기본 설명·필수 조건·기존 detail을 확인한다. Alt 활성화, 최대 4 logical rows, Recipe view 전환 중 core 보존은 변경 영향과 기존 runtime harness의 확인 범위를 고려해 같은 관찰에 필요한 부분만 포함하며 별도 수동 회귀 캠페인으로 확장하지 않는다. 새로운 화면 크기·모든 item·모든 언어를 관찰했다고 확대하지 않는다. 가능한 범위의 FullType/locale/package와 관찰 결과를 남기되 별도 증빙 체계를 만들지 않는다.

### Validation Limits

- 이 문서 작성에서는 코드·문서 읽기와 제한된 current file 집계만 수행했다. 제품 생산·adoption·테스트 suite·Lua 검사·package·게임 관찰은 실행하지 않았다.
- 새 expression-family review는 모든 2,105개 문장의 인간 전수 승인이나 retained prose의 source truth 재승인이 아니다.
- Automated source binding은 게임 기능의 독립 전수 검증이 아니며 public-text evaluator PASS도 semantic acceptance가 아니다.
- Runtime harness는 실제 PZ UI·사용자 관찰을 대체하지 않는다. 과거 식품류 관찰을 successor 전체에 상속하지 않는다.
- S2는 기존 single-core identity를 사용하지만 그 안의 승인된 복수 기본 용도·효과를 함께 표시할 수 있다. Single-core를 한 용도만 남기는 규칙으로 적용하지 않는다. Menu는 구체 레시피·조건 상세와 추가 맥락을 제공하며 S2가 모든 사용법을 완전하게 열거한다는 claim은 하지 않는다. 선택된 core 자체의 사실성을 결정하는 조건은 S2에서 생략할 수 없다.
- 임의 외부 모드, Build 42, 멀티, 장시간, 성능/latency, 모든 화면 배치, description-body search, Layer 4 완비, release/Workshop/deployment를 검증하지 않는다.

---

## 8. Risk Surface Touch

### Authority Surface

**변경 있음.** Body Compiler / `body_plan`과 source-bound composition input의 표현 생산 계약을 확장한다. Adoption 입력 및 필요한 identity dependency binding도 영향 범위다. Source facts / provenance owner, Classification, QG, Layer 4의 의미 판단 권한은 바꾸지 않는다.

### Runtime Behavior Surface

**변경 있음 — 표시 콘텐츠.** Menu Layer 3 KO/EN과 Tooltip S2가 달라진다. Exact lookup, Alt activation, locale failure handling, Recipe opening lifecycle, 최대 4줄과 vanilla render 비간섭은 보존한다. Runtime code 변경은 검증된 필수 결손이 있을 때만 좁혀 수행한다.

### Compatibility Surface

**Offline 계약에 조건부 영향.** 기존 `body_plan` / candidate JSON 또는 installed producer input shape의 변경은 소비자와 schema를 함께 확인한다. 지원 runtime/API, external-mod contract, FullType, Browser public row/search shape와 package 형식은 유지한다. 새 입력이 기존 계약 안에 수용된 부분은 compatibility 변화 없음으로 구분한다.

### Sealed Artifact Surface

**변경 있음.** 새 approved candidate, immutable generation, T1/T2 결과, companion/package를 만든다. Predecessor generation·원본 승인·closeout·hash 기록을 재작성하지 않는다. 표현 변화와 input/dependency bytes 변화에 따른 artifact identity 변화를 구별한다.

### Public-Facing Output Surface

**변경 있음.** 사용자가 읽는 기본 용도·효과 설명이 달라지므로 단순 서식 변경으로 축소하지 않는다. KO/EN의 의미·조건 parity와 사람이 확인한 범위에 evidence를 결속한다.

---

## 9. Risk Analysis

### Architecture Risk

- **Pattern의 fact authority화:** 비슷한 prose·classification을 membership 근거로 삼으면 의미가 확대된다. Source-bound binding만 허용하며 판정 불가 항목은 explicit/retained로 남긴다.
- **Compiler 책임 확대:** source extraction·mod/version branching·semantic approval을 compiler에 흡수하지 않는다. 기존 staging/adoption 책임을 유지한다.
- **실제 생산 경로 미연결:** `compose_*`만 수정하면 이미 채택된 candidate와 별도 EN/S2는 바뀌지 않는다. Pilot과 final propagation에서 실제 producer/consumer relation을 검사한다.
- **설치 package dependency 누락:** description-tree helper 또는 새 renderer file이 wheel/identity 밖에 남을 수 있다. Installed production 확인과 최소 dependency closure amendment로 방지한다.

### Runtime Risk

- **조건 손실 / KO·EN drift:** core에 필요한 condition은 양쪽 renderer의 필수 binding으로 유지한다. Menu 상세에 있다는 이유로 Tooltip의 필수 조건을 빼지 않는다.
- **Mixed-generation:** KO pointer와 별도 EN/fixed/companion을 함께 준비하고 검증한 set만 전달한다. Pointer atomicity를 제품 전체에 확대하지 않는다.
- **Stale lookup cache:** 현재 runtime은 live reload를 보장하지 않는다. 실제 게임 중 파일 hot-swap을 검증 방법으로 삼지 않고 fresh process에서 관찰한다.

### Compatibility Risk

- **Identity 오분류:** 현재 fact IDs가 source-value hash에 묶여 있다. 표현 output과 source correction을 분리하고 필요한 ID delta를 감추지 않는다.
- **FullType collision:** case normalization, item-name 기반 조합과 source mapping을 금지한다. 기존 Lemongrass exact-key control을 유지한다.
- **Offline input 변경:** 새 필드를 조용히 무시하는 old consumer로 인해 일부 표면만 바뀔 수 있다. Version/shape checks와 explicit retained compatibility path로 실패를 드러낸다.

### Regression Risk

- **보존 집합 침식 / 분모 혼동:** source hold, silent, protection, owner absence를 독립 axis로 기록하고 exact membership을 대조한다.
- **Coverage 변화 은폐:** empty-core 승격을 expression 개선으로 합산하지 않는다. 기본 control은 57개이며 승인된 source correction의 exact gained/lost sets만 별도 집계한다.
- **Exception 폭증:** 공유율을 목표로 삼지 않는다. Hidden branch보다 explicit item body를 정상 경로로 유지한다.
- **유용성 없는 대량 churn:** changed family의 이해 가능성·조건 보존과 실제 shared edit 전파를 확인한다. 좋은 기존 문장을 migration 숫자를 위해 바꾸지 않는다.
- **Retention으로 개선 회피:** 이미 적절함·근거 결손·보존 요구와 미작업을 구분한다. 공유 불가지만 개선 가능한 문장은 explicit 경로로 고치고, 2개 item 전파 시연을 전체 실용성 개선의 증거로 확대하지 않는다.
- **Single-core의 용도 수 제한 오독:** 기존 승인 core의 복수 기본 용도·효과를 유지한다. 기본 정보를 Menu로 옮겨 S2를 빈약하게 만들거나 반대로 상세 레시피를 S2에 모두 넣지 않는다.
- **검증 확대 / downstream 재개방:** S1/S3/S4 선택, search 또는 historical governance를 S2 표현 변경의 부수 과제로 만들지 않는다. 기존 required tests는 보존하되 새 독립 gate는 추가하지 않는다.

---

## 10. Rollback Plan

**Adoption 전:** off-live candidate/pilot만 수정하거나 폐기한다. Current input/pointer와 사용자 package는 유지한다. 실패한 공유군은 explicit body 또는 명시적 approved retention으로 다시 설계한다.

**Current 전환 전 중단 조건:** source binding 결손, truth-critical condition 표현 실패, KO/EN claim mismatch, unexpected universe/public/absence delta, protected/hold 변화, nondeterminism, fixed/companion mismatch가 남으면 전달용 current switch/package 확정을 중단한다.

**Adoption 이후:** 이전 input/adoption binding, KO generation pointer, matching EN, Tooltip owner/T1/T2 fixed, Recipe companion과 package를 하나의 known-good predecessor set으로 복원한다. Current successor generation을 제자리 수정하거나 pointer만 되돌리고 EN/Tooltip을 남기지 않는다. 기존 installer의 expected predecessor·immutable guard를 따른다.

**게임 관찰 이후 결함:** 사용자에게 전달하는 rollback도 검증된 predecessor package 단위로 한다. 사용자 게임 폴더를 자동 덮어쓰지 않는다. Pattern-specific failure는 다음 successor에서 pattern 수정 또는 explicit body 전환으로 처리하며 runtime semantic fallback을 추가하지 않는다.

Predecessor source와 sealed evidence를 삭제하지 않는다. Worktree 전체 reset/clean으로 다른 작업 변경을 지우지 않고 이 실행이 소유한 파일·산출물만 되돌린다.

**임시 integration 정리 시점:** 실패한 실험의 임시 출력은 필요한 원인 기록을 보존한 뒤 정리할 수 있다. Final integration checkout과 생성 root는 final package/evidence/rollback set이 보존되고 검토·전달에서 더 이상 필요하지 않은 시점에만 정리한다. 미승인·진행 중인 candidate 자료는 유지한다. Windows에서는 최종 절대 경로가 이 실행의 임시 workspace/root 안인지와 소유 파일 여부를 확인하고 native PowerShell로 처리한다. Cleanup은 별도 validation gate가 아니며 이번 계획 수정에서 실제 삭제를 수행하지 않는다.

---

## 11. Governance Constraints

- Philosophy의 정보·중립성·근거 부족 시 침묵, Menu/Alt 두 surface, Lua-only runtime을 유지한다.
- Pulse의 하위 모듈 의존과 Iris의 sibling 모듈 직접 참조를 도입하지 않는다. Runtime/build-time 경계를 지킨다.
- Canonical facts/provenance, semantic staging, composition, adoption, generation, install, consumer, package 각각의 책임을 보존한다.
- Existing profile 기반 표현 구조와 새로운 optional composition을 Layer 2 taxonomy 또는 game fact authority로 승격하지 않는다.
- `source review_hold`, body disposition, role readiness, runtime public state와 S2 eligibility를 하나의 상태로 합치지 않는다.
- 기존 보호 12개·hold·silent·absence의 원래 권한과 claim ceiling을 보존한다. 과거 승인이나 기존 prose에서 새로운 source approval을 소급 생성하지 않는다.
- Current seven-input / immutable-generation / single-pointer 모델 안의 최소 변경을 우선한다. Canonical input 확장이 필요하면 candidate adoption 이전에 기존 authority 경로의 additive decision과 계약 정합성을 확보하고, 없으면 내부 seven-input 방식으로 회귀하거나 해당 경로를 중단한다. Closeout의 문서 동기화로 이를 사후 정당화하지 않는다. Sealed history·G5 등의 기존 identity 이력을 재번호링하지 않는다.
- Installed tooling / current validation owner를 유지하고 task-local helper·census·평가 결과를 새 상설 authority나 독립 gate로 등록하지 않는다.
- 작업에 이미 부여된 실행 권한을 중복 요청하지 않는다. 새 candidate 채택 권한이 후속 지시에 포함되지 않았다면 concrete candidate와 검토 결과를 준비한 뒤 그 경계에서만 확인한다.
- Human/public-text acceptance issuer는 owner 또는 owner 지정 사람이다. 실행 AI는 acceptance 입력을 준비하며 스스로 인간 판정을 발급하지 않는다. 사람 검토는 채택 전 문장 묶음과 최종 package 관찰로 모으며 pilot·family·item별 승인을 추가하지 않는다. 미승인 범위는 `unvalidated_but_in_scope`로 공개하고 semantic-quality success 및 전체 `complete`를 금지한다. Task-level acceptance를 source authority나 publication/release acceptance로 확대하지 않는다.
- 검증 명령의 실제 exit와 exact subject에만 결과를 귀속한다. Missing tooling은 BLOCKED이며 docs-only 작성·code review·과거 PASS는 제품 validation evidence가 아니다.

---

## 12. Expected Closeout State

후속 실행의 목표는 명시된 validation ceiling 안의 **`complete`**다. 다음 조건을 모두 충족해야 한다.

1. Source-bound semantic material과 표현·조합이 분리되고 기존 Body Compiler의 실제 current production path에서 동작한다.
2. Shared / explicit / retained path가 공존하며 전 DVF universe와 보존 집합이 누락·중복 없이 reconcile된다. Retention은 이미 적절함·근거 결손·기존 보존 요구로 설명할 수 있고, 미작업을 유지 완료로 바꾸지 않는다. 공통화율은 조건이 아니다.
3. Item별 값·조건·qualifier·exception과 KO/EN semantic parity를 보존한다. 보존 경계 밖에서 근거가 충분하고 개선 필요성이 확인된 설명은 shared 또는 explicit로 실제 개선되며 before/after와 유지 이유에서 결과를 확인할 수 있다. Source correction, expression delta와 S2 core/empty-core coverage delta를 구분하고 coverage 변화는 승인된 exact 대상과 일치한다. 변경 개수 목표나 별도 품질 점수 Gate를 만들지 않는다.
4. 공통 표현 1건 변경이 같은 조합을 쓰는 최소 2개 FullType에 결정적으로 반영되고 non-target이 보존된다. 이는 compiler 연결 증거이며 3번의 실제 설명 개선을 대신하지 않는다.
5. 새로운 표현 구조 / 의미·문법에 영향을 주는 condition·exception 변형 / correction / outlier를 대표 KO/EN으로 묶어 **owner 또는 owner 지정 사람의** exact-candidate public-text acceptance를 확보한다. Pilot·family·item별 독립 승인은 없으며 변경 후에는 영향 범위만 보완한다. 필수 검토 범위에 `unvalidated_but_in_scope`가 남아 있으면 전체 `complete`를 선언하지 않는다.
6. Canonical input 확장이 필요했다면 **adoption 이전** additive authority decision을 확보했고, reviewed successor candidate가 채택되어 current Layer 3 generation이 된다. Menu와 Tooltip S2는 동일 승인 core를 소비하며 그 안의 복수 기본 용도·효과를 보존한다. Single-core는 identity 제약으로 유지하고 구체 사용법·추가 상세의 완전한 열거를 S2의 역할로 요구하지 않는다.
7. Matching EN / T2 fixed / Recipe companion / 최종 source·package가 coherent set이며 installed tooling과 실제 runtime consumer를 확인한다.
8. 기존 필수 자동 검증의 exact command가 성공하고 최종 package의 묶음 representative runtime 관찰과 미관찰 범위를 기록한다. 동일 범위의 기존 실행 결과는 적용 가능한 계약 안에서 재사용하며 새 독립 gate·항목별 수동 검사·중복 full regression을 완료 조건으로 삼지 않는다.
9. 실행 범위 안의 unresolved actionable gap은 없고, legitimate retained/hold/silence 및 검증 한계는 final closeout 하나에 명시한다.

| 실제 종료 상태 | 허용할 closeout |
|---|---|
| 위 조건 충족 | `complete` — 명시된 semantic / runtime 관찰 범위 안에서만 |
| Compiler/candidate는 구현했으나 owner public-text acceptance·adoption·downstream·package 또는 필수 관찰이 미완료 | `implemented_only` 또는 완료된 단계에 따른 `partial`. 미승인 검토 범위는 `unvalidated_but_in_scope`로 병기 |
| 필수 tooling/source/승인·계약 결손으로 다음 필수 단계를 수행할 수 없음 | `blocked` — 구체 원인과 확보된 산출물을 구분 |
| 이번 요청처럼 계획만 작성 | 계획 문서 완료. 제품 구현·검증·채택 상태는 미실행 |

완료 후에도 모든 문장의 완벽한 인간 품질, 모든 hold/silence 해소, description-body search, Layer 4 완비, raw external-mod 이해, Build 42·임의 모드 조합·성능 보증, freeze/RTC/Publish/Workshop/release/deployment readiness는 주장하지 않는다.
