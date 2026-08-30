# Implementation Plan — Iris Tooltip T3 검증된 T2 정적 데이터의 Alt Tooltip Runtime 통합

>
> 상태: 실행 전 계획. 이번 작성 범위는 코드·입력 조사와 본 문서 추가이며, runtime 구현·package·설치·게임 검증은 수행하지 않았다.
>
> 양식: `docs/PLAN_TEMPLATE.md`의 12개 절 및 Change별 Purpose / Files / Implementation Notes / Validation 구조.
>
> 입력: 사용자 제공 「Iris Tooltip T3 — 검증된 T2 정적 데이터의 Alt Tooltip Runtime 통합 종합 ROADMAP」. 로드맵의 보류·owner-reserved 항목은 이 계획으로 자동 승인하지 않는다.
> 개정: 2026-08-30 Integrated Review 반영. 검증 선행 순서, L3 관측·필수 범위의 사전 결정, fault-path trap과 운영 관찰 조건을 보강했다. 검토 verdict 또는 T3 실행 완료를 새로 선언하는 개정은 아니다.
> 후속 개정: 2026-08-30 사용자 요청 반영. L3의 별도 EN consumer 경로를 명시하고, reader/Alt 구현을 묶어 실제 legacy 삭제 직전의 최소 replacement 검증과 최종 검증으로 실행을 축소했다. 게임 내 수정 후 최종 gate를 수행하며 일반 구현 선택에는 새 승인 대기를 만들지 않는다. 기존 필수 검증·독립 증거·미검증 상태의 정직한 보고는 유지한다.

## 1. Objective

검증된 단일 T2 completion bundle의 KO/EN 정적 문자열 배열을 Iris 제품 경로에 내용 보존 상태로 포함하고, 실제 Alt Tooltip을 다음 경로로 전환한다.

```text
verified T2 Lua
→ repository product copy
→ thin Lua lookup boundary
→ Alt ON: exact FullType + explicit ko/en
→ atomic 0~4 logical rows validation
→ Iris Tooltip presentation
→ package / installed copy / actual loaded module identity
→ 실제 PZ 기능·시각·실패 격리 확인
```

Alt OFF에서는 Tooltip data lookup·record validation·의미 조립을 시작하지 않는다. Alt ON에서는 T2의 완성된 문자열과 순서를 그대로 표시하며, 정상 0줄·missing·unsupported·malformed·load failure는 Iris section 미표시로 수렴한다. Iris 실패가 기존 vanilla Tooltip을 중단해서는 안 된다.

Menu와 Tooltip의 같은 사실에 대한 관계는 실제 Menu consumer에서 확인한다. 특히 T1의 Layer 3 independent Menu evidence gap을 T2 자기 출력으로 닫지 않는다. 구현, 자동검증, package, 설치, 실제 loaded module, Menu relation, in-game 기능, visual fit, failure isolation을 각각 별도 증거 축으로 기록한다.

---

## 2. Scope

- 단일 exact T2 bundle admission과 repository product copy의 byte identity 보존.
- 현재 Tooltip hook·초기화·locale·legacy summary/cache·supported API·validation consumer 조사.
- 얇은 static loader/reader와 exact FullType·locale lookup, atomic record validation.
- `IrisAltTooltip`의 정적 데이터 전환, Alt fast path, item/locale lifecycle, 0줄·중복 삽입·실패 격리 처리.
- T2 문장을 바꾸지 않는 Tooltip geometry·measurement·wrapping·spacing 보완.
- actual consumer census에 따른 legacy 경로의 제거 후보·보존·thin adapter 구분.
- L2 inherited relation 확인, L3 실제 consumer evidence 가능 범위 확인, L4 selected identity relation 확인.
- 기존 validation owner 아래 focused runtime 검증·관련 회귀·package/install identity·대표 PZ 검증.
- 최종 결과가 생긴 경우에만 실제 증거 범위에 맞춘 문서와 current route의 후속 동기화.

### Explicitly Out Of Scope

- T1/T2 재생성, S1 표제 재작성, Classification/DVF/QG 의미 판정 및 source owner 수정.
- T2 문자열 번역·요약·truncation·정렬·중복 문자열 제거·후보 재선택·locale fallback.
- Tooltip 전용 Registry, seal framework, mutable latest pointer, artifact lifecycle, chunking, result-cache architecture, hot reload.
- Browser/Detail/Wiki 기능 확장, Menu layout 재설계, context-menu 진입 방식 변경.
- unrelated public API refactor, 다른 Spoke 또는 JVM/Java/Mixin product logic 도입.
- 일반 사용자 설치본을 손상시키는 failure injection, Workshop 게시, release/deployment.

이번 문서 작성이 위 구현·설치 작업의 실행 완료나 owner-reserved 선택의 승인을 뜻하지 않는다.

---

## 3. Non-Goals

T3는 이미 생성된 정보의 제품 연결을 검증하는 단계다. T2 semantic quality·번역 품질을 재인증하거나 모든 2,280개 아이템을 사람이 게임에서 전수 검증하지 않는다. Menu가 더 많은 정보를 보여주는 정상적인 깊이 차이를 없애지 않으며, 독립 Menu 증거를 얻기 위해 Menu semantic architecture를 새로 만들지 않는다.

모든 외부 모드 조합, multiplayer, long-session soak, 모든 해상도·font·UI scale 조합, RTC certification, DVF freeze readiness, Publish Boundary, release/Workshop readiness는 이 계획의 완료 대상이 아니다. FPS·latency·memory 개선도 주장하지 않는다. T2 입력 결함은 upstream correction으로 반환하며 runtime 보정으로 숨기지 않는다.

---

## 4. Assumptions

### 4.1 설계 authority와 조사 기준

- 최상위 authority는 `docs/Philosophy.md`다. Iris는 근거 기반 정보만 표시하고, 메뉴와 Alt Tooltip만 사용자 표면으로 가지며, PZ runtime은 100% Lua다.
- `docs/DECISIONS.md`의 Menu/Tooltip, public API, locale, lazy loading, global non-interference, evidence/closeout, T1/T2 결정을 따른다.
- `docs/ARCHITECTURE.md`의 Tooltip T1/T2와 runtime presentation 구조, `docs/ROADMAP.md`의 Iris T3 Next가 현재 위치다.
- `docs/EXECUTION_CONTRACT.md`의 claim-evidence binding, validation ceiling과 closeout 규율을 따른다. 기존 state vocabulary는 이 문서의 §7-1을 참조하며 T3 전용 목록으로 복제하지 않는다.
- command literal owner는 `Iris/build/ENTRYPOINTS.md`, current locator는 `Iris/_docs/authority/iris_current_route_index.json`이다. 과거 실행 문서의 command를 current route로 재채택하지 않는다.
- 조사한 workspace HEAD는 `b9d7ae289b226082c191b1f6a23e6b363c6d99a6`, tree는 `c5d1d1c4ed9d4142e1cdb7dfdc854255c19ecb0b`다. T2 machine subject와 다른 값이며, 미래 T3 실행 subject도 별도로 결속해야 한다.
- 작업 시작 시 `b/`, `g/`, `i/`의 기존 test checkout 상태 변경이 관찰됐다. 이를 T3 변경으로 취급하거나 정리하지 않는다. terminal 검증은 기존 clean-checkout 절차가 정한 exact subject를 사용한다.

### 4.2 직접 확인한 T2 입력

Current route의 `tooltip_t2_static_staging`은 `state: complete`, `runtime_adopted: false`다. 다음 external bundle이 실제 존재하며 세 파일의 SHA-256이 current route와 일치하는 것을 이번 작성 중 확인했다. 이는 read-only 입력 조사이며 T3 runtime validation이 아니다.

```text
final root: C:/Users/MW/Downloads/coding/PZ2/t2-final
T2 machine commit: d64692ac26cdc21e4c7f558a0fe93278f64b16d1
T2 machine tree:   850e0af81af9b9fda8ee7df26847f88a4b32b142

IrisTooltipT2Data.lua
  bytes: 979485
  SHA-256: 4d9d109eaaf0f61e638ebf94cee33c8c306e88f322143c74c8eecdb8131646fd
tooltip_t2_projection_manifest.json
  bytes: 1931373
  SHA-256: 2b4bee6ce9a262e727b57d7c254e7c2f2211780100cf1c222468a93419ef3efe
tooltip_t2_closeout.json
  bytes: 4758
  SHA-256: 98c70b8e667a31c588d938cd4c7bf6923da1b1147712a2b20366f0de2aac8327
```

T2 Lua는 별도 metadata wrapper 없이 `return { [exactFullType] = { ko = {...}, en = {...} } }` 형태다. Manifest에는 FullType별 `line_count`, `present_slots`, `omitted_slots`, 각 line의 `slot_id`, `semantic_identity`, `surface_sha256`가 있다. Manifest/closeout은 offline identity·relation 증거이며 runtime 의미 입력이 아니다.

| Universe | 관찰/상속 값 | 사용 한계 |
| --- | ---: | --- |
| Exact support | 2,280 | case-sensitive FullType 집합 |
| Layer 2 applicable / display silence | 1,406 / 874 | T1의 분류 표시 partition |
| Layer 3 selected fact | 1,314 | independent Menu evidence가 남은 별도 분모 |
| T2 0/1/2/3/4줄 | 367 / 825 / 895 / 137 / 56 | manifest에서 읽은 완성 배열 분포 |

각 분모를 서로 차감하거나 대체하지 않는다. T2 closeout의 generation A/B·syntax·focused·canonical gate 완료 기록은 입력의 과거 증거이며 T3의 새 subject나 PZ 동작 증거로 재결속하지 않는다.

### 4.3 코드 조사로 확인한 전환 지점

아래 행의 경로는 `Iris/media/lua/client/` 기준이다.

| Readpoint | 현재 관찰 | 계획에 미치는 영향 |
| --- | --- | --- |
| `Iris/IrisMain.lua` | Step 5a가 `IrisAltTooltip`을 load하고 `hookTooltip()` 호출 | 새 bootstrap 체계 없이 기존 진입점을 유지 |
| `Iris/UI/Tooltip/IrisAltTooltip.lua` | 기존 `ISToolTipInv.render`를 보관한 wrapper, 매 render `_irisRendered` 초기화, 원본 render 뒤 overlay | wrapper 자체가 현재 존재함을 전제로 재진입·실패 경계를 점검. 원본을 생략하는 대체 renderer로 바꾸지 않음 |
| 같은 파일 `addIrisOverlay` | Alt 판정이 summary load·FullType resolution보다 앞섬 | 기존 inactive fast path를 보존하고 static lookup까지 차단 |
| 같은 파일 `buildDetailLines` | `tooltipFacts`가 있으면 동적 수치 최대 4줄, 없으면 tag·connections·UseCase count | raw-tag branch만 제거해서는 부족. Detail model을 만드는 상위 summary 호출까지 Alt에서 끊음 |
| 같은 파일 `getDetailLines` | FullType별 locale/revision cache, `getLangKey("EN")`, 문자열 조립 | 완성된 T2 배열용 cache를 다시 만들지 않는 방향. legacy cache·metric consumer는 별도 조사 |
| 같은 파일 draw 경로 | `lineHeight = 16`, `drawText`, 기존 height 아래 box를 그리고 `setHeight` | 긴 KO/EN wrapping·실제 font 높이·Tooltip 재사용 시 높이 누적을 별도 해결 |
| `Iris/UI/Tooltip/IrisTooltipSummary.lua` | classification·Recipe/Moveables/Fixing·UseCase line count, `DetailViewModel.fromItem`, fallback body load, summary cache | Alt에서 통째로 도달 불가화. 공유 source/index까지 삭제하지 않음 |
| `Iris/Util/ItemKey.lua` | item의 `getFullType`, `getFullName`, `fullType` 접근. case folding/trim 없음 | exact 결과만 reader에 전달. 일반 ItemKey 계약은 불필요하게 변경하지 않음 |
| `Iris/Util/IrisTranslationResolver.lua`, `Iris/IrisTranslationLoader.lua` | loader가 locale key를 캐시하고 `init()`에서 갱신. 문자열 번역에는 EN fallback, key 조회 실패에도 EN 기본값 존재 | T2 text에 번역 함수를 호출하지 않음. 실제 unsupported key와 locale 취득 실패가 EN으로 위장되지 않게 별도 점검 |
| `Iris/UI/Detail/IrisItemDetailModelAssembler.lua` | `layer3Payload`는 `raw/display/publishState` 등을 전달하고 `fact_id`는 노출하지 않음 | 현재 경로만으로 L3 independent identity closure를 보장할 수 없음 |
| `Iris/Data/layer3_renderer.lua`, `Iris/Data/IrisLayer3EnglishLookup.lua` | KO는 조회한 entry의 `text_ko`, EN은 별도 `Layer3English/Index`와 chunk를 통한 lookup 결과를 반환 | L3 검증은 KO record와 EN 실제 선택 record를 각각 관찰. 기본 Layer3 lookup 성공만으로 EN consumer를 검증했다고 주장하지 않음 |
| `Iris/UI/Browser/IrisBrowserInteractionProjection.lua` | `line.label_key`, `surface`, `recipe_id`, `recipe_nav_ref`에서 `identity/source`를 가진 row 생성 | L4 actual Menu structured comparison readpoint로 사용 가능 |

Source search에서 product의 summary 직접 호출은 Alt에서 확인됐지만, 이것만으로 제거 결정을 완료하지 않는다. 테스트·instrumentation·초기화·지원 계약 및 offline source inventory도 consumer다.

특히 `Iris/_docs/refactor/residual_refactor/phase0_supported_api_manifest.json`에는 20개 listed surface와 tooltip summary copy-on-read를 언급하는 상위 delta가 있다. Listed symbol에 없다는 이유만으로 이 호환성 이력을 무시하지 않는다. Current 결정과 successor evidence를 함께 대조한다.

### 4.4 실행자가 정할 구현 선택과 별도 판단이 필요한 경계

| 항목 | 이 계획의 제안/처리 | 확정 시점과 경계 |
| --- | --- | --- |
| Census 이전 product placement 허용 | admission과 read-only census를 모두 마친 뒤 mutation | 선행 placement 예외를 사용하지 않으며 별도 미결정 항목을 만들지 않음 |
| T3 validation의 `determinism` 명칭 | 검증 내용은 copy/package/install content identity로 기술 | 명칭 결정과 무관하게 T1/T2 generation 재인증 금지 |
| Final closeout label | §12와 기존 state 정의를 실제 결과에 적용 | 실행자가 근거와 validation ceiling을 기록. 기존 authority가 별도 결정을 요구할 때만 해당 절차 적용 |
| Canonical gate를 T3 전용 terminal gate로 추가 | 새 gate는 만들지 않음. current-required applicability를 확인 | 기존 authority가 요구하는 gate는 이 보류를 이유로 생략할 수 없음 |
| Independent review 문구/eligibility | 기존 governance를 참조하고 별도 T3 자격 체계를 만들지 않음 | 계획 작성자를 자동 independent reviewer로 간주하지 않음 |
| Product file / module name | 기본 경로는 `Iris/Data/IrisTooltipT2Data`와 `Iris/Data/IrisTooltipT2Lookup` | 실행자가 기존 require/package 경계와 충돌 여부를 확인해 확정. 경계 안의 경로 선택만으로 별도 승인 대기를 만들지 않음 |
| Legacy 항목별 disposition | §6 Change 2의 근거표를 작성 | 사용 중이거나 supported인 API의 변경은 기존 owner 절차 유지. 소비자·지원 계약이 없는 항목의 처분은 계획의 삭제 전 검증 조건 안에서 수행 |
| L3 필수 evidence 범위·관측 수단의 인정 여부 | Change 2에서 exact 대상·coverage 의무·KO/EN 각각의 admissible observable 후보를 제시 | 본 검증 전에 기존 Menu evidence owner 기준으로 고정. 기존 결정/실행 승인으로 해결되는 사항은 재사용하고 새 승인 artifact를 만들지 않음. 관찰 성공분으로 범위를 재정의하지 않음 |
| Menu evidence 상태 갱신 | 사전에 고정한 범위와 실제 결과를 함께 제시 | 결과 상태 갱신은 owner-reserved; observable 부재나 gap을 검증 완료로 바꾸지 않음 |
| 지원 화면 환경·게임 대표 집합 | 요구 coverage 안에서 PZ build/mod/font/scale/resolution과 최소 대표 집합을 선택 | 실행자가 Change 9 관찰 전에 기록. 기존 authority의 명시적 별도 승인 요구가 없으면 표본 선택만으로 대기하지 않으며 claim을 관찰 환경 밖으로 확대하지 않음 |
| 기존 Tooltip hook / non-interference 해석 | Change 2에서 구현자가 current authority와 wrapper 동작을 대조 | 기존 결정으로 처리 가능하면 근거를 기록. 충돌·미결정은 Iris runtime/compatibility owner가 Change 4 전에 판정하며 unresolved 상태로 cutover하지 않음 |

일반 구현 선택은 실행자가 근거를 남기고 진행한다. 기존 authority가 실제로 요구하는 owner 결정, 지원 API 변경, 필수 L3 evidence 범위 또는 hook 충돌 판단이 빠졌을 때만 해당 단계/claim을 미완료로 남긴다. 해당 범위에 유효한 사용자 실행 승인과 기존 결정을 재사용하며 동일 사항의 재승인 문서·seal은 만들지 않는다. 플랫폼 보안·권한 확인은 별개다.

### 4.5 Integrated Review 반영 판단

| 피드백 | 이번 개정의 처리 |
| --- | --- |
| C-01 / R-01 | replacement 검증 전 legacy 삭제 금지는 유지한다. 후속 사용자 요청에 따라 Change 3/4 사이의 개별 PASS 관문은 제거하고, 구현을 묶은 뒤 실제 삭제·adapter 전환 직전에 필요한 replacement subset을 한 번 실행한다. |
| C-02 / R-02 | 현재 구조에서 closure가 반드시 불가능하다고 단정하지 않는다. 다만 admissible observable과 필수 범위를 사후 결정할 여지는 제거한다. Change 2 사전 결정, Change 6 고정 범위 검증, observable 부재 시 L3 미해결·전체 T3 완료 불가를 명시한다. |
| R-03 / N-02 | 정상뿐 아니라 load failure·malformed record·unknown FullType에서 legacy trap `0`을 확인한다. 실제 삭제/adapter 변경 시에만 삭제 전 subset과 최종 변경 후 focused로 나누며, legacy 보존이면 가상의 삭제 전후 실행을 만들지 않는다. |
| L2 inheritance / L3 unresolved 구분 | Inheritance의 source·consumer·diff 근거를 기록하고, L3 source relation 부재와 independent identity 관찰 한계를 구분한다. |
| Visual / N-01 / N-04 / N-05 | 환경 결속, 실제 module load timing 검증, locale 취득 실패의 no-result, hook 판단 책임·시점을 보강한다. |
| N-03 closeout label | 최초 검토의 label 사전 선택 요구는 미채택했고 후속 검토에서 철회됐다. 기존 vocabulary와 §12 증거 조건을 실제 결과에 적용하며, 별도 owner 판단이 요구되지 않는 상태 기록은 실행자가 수행한다. |
| N-06 L3 universe exact-set 대조 | 비차단 보강으로 채택한다. Universe 고정 전에 admitted T2 manifest의 S2-present exact set을 해당 T2 입력에 결속된 봉인 T1 selected Layer 3 set과 missing/extra `0`으로 대조한다. 개수 일치만으로 집합 일치를 인정하지 않는다. |
| 후속 검토 4.1 / 4.2 | 기존 처리 유지로 확인한다. L3 observable/owner 결정이 확보되지 않아 미해결 상태가 남는 것은 정직한 execution 결과이며 full T3 completion은 보류한다. First-use/boot-load 선택과 Alt OFF lookup·record validation·semantic processing 금지의 분리 관찰도 유지한다. 두 항목은 추가 수정 요구로 취급하지 않는다. |
| 이번 사용자 검토 반영 | L3 EN의 실제 lookup/index/chunk 경로를 포함한다. 일반 구현 선택의 불필요한 유보를 제거하고 §7의 최소 실행 규칙을 적용한다. 최종 canonical gate는 package/game에서 발생한 수정이 끝난 뒤 기존 요구 횟수만 수행한다. |

위 수정은 실행 절차와 증거 조건의 모호성을 줄이는 변경이다. 두 원검토의 PASS/WARN/FAIL을 덮어쓰거나 수정본의 independent review를 대신하지 않는다. 이미 합의된 semantic scope·authority·sealed input·claim ceiling은 재개방하지 않는다.

---

## 5. Repository Areas Affected

### Code

**직접 수정 예정**

- `Iris/media/lua/client/Iris/UI/Tooltip/IrisAltTooltip.lua`: static consumer, lifecycle, protected rendering, layout.
- `Iris/media/lua/client/Iris/Data/IrisTooltipT2Lookup.lua`: 신규 thin reader 기본 경로. 기존 경계 안의 경로 조정은 실행자가 근거를 기록한다.

**Census 또는 구현 필요성 확인 후에만 수정**

- `Iris/media/lua/client/Iris/UI/Tooltip/IrisTooltipSummary.lua`: 제거·보존·adapter 후보.
- `Iris/media/lua/client/Iris/Util/IrisTranslationResolver.lua`, `Iris/media/lua/client/Iris/IrisTranslationLoader.lua`: 기존 locale lifecycle 안에서 취득 실패를 식별하는 최소 additive accessor가 필요한 경우만 변경. 기존 호출자의 fallback semantics는 보존.
- `Iris/media/lua/client/Iris/IrisMain.lua`, `Iris/media/lua/client/Iris/Util/IrisProtectedCall.lua`: 기존 초기화와 보호 경계로 충분하면 무변경.
- `Iris/tools/package_iris.ps1`, `Iris/test/validate_disposable_package.ps1`: 기존 media projection에 T2가 자동 포함되는지 먼저 확인. 추가 identity assertion이 필요한 경우만 수정.
- `Iris/test/lua/`의 Tooltip 관련 harness 및 이를 실행하는 `Iris/build/description/v2/tests/`의 current test owner.
- `Iris/tooling/src/iris_tooling/domains/tooltip_t1/audit.py`: legacy 파일 제거 시 `MENU_TOOLTIP_SOURCES` inventory의 current applicability 영향만 검토. T1 의미·과거 receipt 수정은 금지.

**기본 read-only**

- `Iris/media/lua/client/Iris/UI/Detail/`, `Iris/media/lua/client/Iris/UI/Browser/`, `Iris/media/lua/client/Iris/UI/Wiki/`: Menu source relation과 회귀 확인.
- `Iris/media/lua/client/Iris/Util/ItemKey.lua`, `Iris/media/lua/client/Iris/API/`, 기존 Classification·Layer3·UseCase data/index.
- `Iris/media/lua/client/Iris/Data/IrisLayer3EnglishLookup.lua`, `Iris/media/lua/client/Iris/Data/Layer3English/Index.lua`와 그 chunk: L3 EN의 실제 선택 record·기존 fact mapping 관찰 대상. Tooltip 검증용 fact ID를 production Menu에 추가하지 않는다.
- `Iris/tooling/src/iris_tooling/domains/tooltip_t1/`, `Iris/tooling/src/iris_tooling/domains/tooltip_t2/`: 기존 입력 계약/readpoint 재사용. generator를 T3 runtime helper로 끌어오지 않음.

### Docs

- `docs/iris_tooltip_t3_static_data_alt_runtime_integration_plan.md`: 이번 변경 파일.
- 실행 후 필요한 경우 `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`: 확인된 runtime·증거·남은 gap만 동기화.
- `Iris/build/ENTRYPOINTS.md`: 실제 current command가 추가/변경될 경우에만 갱신.
- Consumer disposition과 evidence 결과는 기존 보고 경로 또는 명시적 external execution root에 기록한다. 새 문서 트리를 runtime authority로 만들지 않는다.

### Config

- `.gitattributes`: 확정된 T2 product 파일 한 개의 raw bytes를 Git checkout에서도 유지해야 하는 경우 path-scoped `-text` 규칙 검토. 저장소 전체 줄바꿈 정책은 변경하지 않음.
- `Iris/_docs/round3/current_route_required_validations.json` 및 `Iris/validation/clean_checkout/contracts/`: 새 focused coverage 또는 legacy assertion 대체의 current 등록이 필요한 경우에만 기존 owner 절차로 변경.
- `Iris/_docs/authority/iris_current_route_index.json`: 실제 T3 adoption 결과가 나온 후에만 후속 상태 반영. 현 T2 source binding을 덮어쓰지 않음.
- 신규 user 설정, feature toggle, locale 목록, 의존성은 기본적으로 추가하지 않음.

### Generated Artifacts

- `Iris/media/lua/client/Iris/Data/IrisTooltipT2Data.lua`: T2 원본의 byte-identical product copy 후보. T3에서 재생성하지 않음.
- `C:/Users/MW/Downloads/coding/PZ2/t2-final/`의 세 파일: read-only 원본으로 보존.
- External T3 실행 root: package inventory, payload/runtime hash, install readback, Menu relation, 실행 command·exit code·subject와 게임 관찰 자료. 경로는 실행 시 명시하며 저장소 안 `.tmp`나 mutable latest 포인터를 사용하지 않음.
- Manifest/closeout은 기본적으로 `media/lua` 밖의 verification evidence로 유지. 게임 runtime에서 읽거나 require하지 않음.

---

## 6. Planned Changes

Change 번호는 책임 구분이며 아래 의존 순서가 실행 기준이다. Harness 준비와 테스트 실행은 구분한다. Change 3/4는 함께 구현할 수 있고 사이에 개별 PASS 관문을 두지 않는다.

```text
Change 1 + Change 2: admission / census / hook 판단 / L3 사전 범위·관측 수단 판정
→ Change 7 준비: 기존 owner 아래 focused harness·spy·trap·실행 command 준비
→ Change 3 + Change 4: reader / Alt cutover / lifecycle / layout 구현
  (legacy 구현 파일은 보존; 단계별 focused 실행 없음)
→ Change 5: 실제 삭제·adapter 변경이 있을 때만 replacement subset 1회 exit 0 → 변경
  (보존이면 이 선행 테스트를 생략; 변경 후 전체 focused는 마지막에 합침)
→ Change 6: 사전 고정한 KO/EN Menu relation 본 검증, 공통 fixture로 묶어 실행
→ Change 8: package / install identity + 게임 진입에 필요한 최소 syntax/lookup smoke
→ Change 9: 실제 PZ loaded-module / functional / visual / failure isolation 및 필요한 수정
→ Change 7 종합: 최종 코드의 focused / 관련 regression / 기존 필수 canonical gate
→ Change 10: evidence-bounded closeout
```

Read-only 조사는 앞당길 수 있다. 실제 삭제·adapter 변경은 replacement subset의 exit `0` 없이 수행하지 않는다. 단순 보존에는 이 선행 실행을 요구하지 않는다. 게임 전에 필요한 검사와 최종 검증의 재사용은 §7을 따르며, 기존 authority가 명시한 선행 gate 순서가 있으면 그것은 유지한다. L3 사전 결정이 없거나 admissible observable이 없으면 independent identity 본 검증과 전체 완료 claim은 열리지 않지만 다른 독립 작업은 진행할 수 있다. 이 순서는 새 gate authority나 별도 에이전트 병렬 실행을 요구하지 않는다.

### Change 1 — Exact T2 Input Admission

**Purpose:** 하나의 T2 completion bundle과 실제 product copy의 출처를 고정한다.

**Files:** current route index, T2 external 세 파일, 기존 `tooltip_t2` contract/manifest schema.

**Implementation Notes:**

1. 실행 시 current locator를 다시 읽어 §4.2와 동일 subject/bundle인지 확인한다. 이동·변경됐으면 silent latest selection이나 파일 혼합 없이 차이를 기록한다.
2. Closeout의 implementation subject, artifact hash·byte count, manifest의 Lua hash와 T1 input binding, support/locale/row distribution의 일관성을 확인한다.
3. Lua 자체가 완성된 KO/EN 배열을 반환함을 offline readback한다. FullType 목록과 배열 전수 비교는 migration invariant 확인이며 fact 의미 재판정이 아니다.
4. Bundle을 복사할 때 `Copy-Item` 또는 binary copy를 사용한다. `Get-Content`/`Set-Content`로 Lua를 재저장해 encoding·newline·escape bytes를 바꾸지 않는다.
5. Manifest의 exact keys를 보존하는 decoder를 사용한다. 이번 조사에서 기본 PowerShell `ConvertFrom-Json`은 `Base.LemonGrass` / `Base.Lemongrass` 때문에 오류가 났으며 PowerShell 7의 `-AsHashtable`로 두 key 보존을 확인했다. Windows PowerShell 5 경로에는 그 옵션을 가정하지 않고 기존 Python JSON reader 등 case-sensitive 경로를 사용한다.

**Validation:** 세 파일 hash/binding, support 2,280 및 exact pair, explicit `ko/en`, 0~4줄 전체 shape를 확인한다. Admission 실패는 T3 adoption 중단이며 regeneration이나 runtime repair의 근거가 아니다.

### Change 2 — Runtime / Legacy Consumer Census

**Purpose:** Alt 의미 생산 경로와 보존해야 할 consumer를 분리한다.

**Files:** Alt/Summary, `IrisMain.lua`, ItemKey/locale/protected-call helper, public API manifests, 관련 Lua harness·Python test·T1 source inventory, package script.

**Implementation Notes:**

- `require`·direct call·전역 alias·registration·initialization·test preload·metrics·source hash/inventory reference를 구분해 조사한다. 과거 log의 문자열 출현은 현재 runtime consumer로 세지 않는다.
- 각 항목에 symbol/module, 실제 caller, product/test/tooling 구분, supported contract, 제거 후 대체 검증, disposition 후보를 기록한다.
- Change 4 이전에 구현자가 기존 `ISToolTipInv.render` wrapper의 원본 호출·overlay·global 변경 범위를 current non-interference 결정과 대조한다. 이미 적용되는 결정이 있으면 그 근거를 사용한다. 실제 충돌·해석 미결정이 있으면 기존 Iris runtime/compatibility owner의 판정을 해당 cutover 전에 결속하며, 실행 후 보고만으로 승인된 것으로 만들지 않는다.
- 현재 확인된 주의 대상은 다음과 같다.

| 대상 | 이미 확인된 참조 | 기본 처리 후보 |
| --- | --- | --- |
| `IrisTooltipSummary.get/_getCached/reset` 및 metrics | Alt, lazy/residual/pre-refactor harness | Alt edge 제거. 파일 자체는 supported/census 결과로 결정 |
| `resetDisplayLineCache`, `getDisplayLineCacheMetrics`, instrumentation | Browser state harness, optimization harness | production cache 요구와 test observation 요구를 분리 |
| `IrisItemDetailPresentation.tooltipFacts` | Summary와 Detail fact/locale harness | Alt에서 미사용이어도 Detail owner 기능을 자동 삭제하지 않음 |
| Recipe/Moveables/Fixing·UseCase index | Summary 외 Detail/API consumers | Menu/API용 구현 보존 |
| `IrisTooltipSummary.lua` 경로 literal | T1 `MENU_TOOLTIP_SOURCES`, legacy surface acceptance test | 삭제 시 offline inventory/current guard 영향까지 처리 |
| `tooltip_cache_hits=1` assertion | Browser state acceptance Python test | T3 static behavior assertion으로 bounded 대체; cache 유지 요구로 오독 금지 |

**L3 사전 판정 — Change 6의 item별 relation 본 검증 전에 수행:**

1. 구조·계약 조사로 admissible Menu-side observable의 존재 가능성을 확인한다. 후보는 실제 Menu가 소비한 record를 식별하는 existing `fact_id` 또는 immutable generation/module/record locator다. 후자는 Tooltip과 독립적인 기존 authority mapping으로 fact identity에 결속되고 실제 consumer의 record 선택을 관찰할 수 있어야 한다. 단순 FullType·공유 generation·동일 문자열·static call graph만으로는 부족하다.
2. Menu가 원래 읽는 정보를 test/dev 경계에서 관찰할 수 있는지 확인한다. Tooltip ID를 Menu에 주입하거나 rendered string에서 ID를 복원하는 수단, 새 Menu semantic architecture는 admissible하지 않다. 이 사전 조사는 item별 parity 성적에 따라 completion 범위를 고르는 절차가 아니다.

   - KO는 current generation의 실제 선택 entry와 `text_ko` 소비를, EN은 기본 entry의 공개 조건 확인 후 `IrisLayer3EnglishLookup → Layer3English/Index → selected chunk/FullType record` 소비를 구분한다. EN의 module/record와 기존 승인 fact를 연결할 독립 mapping도 조사한다. KO lookup 성공, 같은 FullType 또는 영어 문자열 일치만으로 EN fact relation을 인정하지 않는다.

3. Universe 고정 전에 admitted T2 manifest에서 도출한 S2-present exact FullType 집합을 해당 T2의 `t1_input` subject/hash에 결속된 봉인 T1 selected Layer 3 집합(기존 승인 handoff의 S2 selected set)과 대조해 missing/extra `0`을 확인한다. 개수 일치만으로 집합 일치를 인정하지 않으며, 개수가 같은 구성원 교체도 불일치로 남긴다. 비교 입력 locator/subject/hash와 missing/extra 결과를 기록하고, 입력 부재·binding 불일치·집합 차이가 있으면 universe를 고정하지 않는다. 이 대조는 기존 봉인 입력의 read-only 확인이며 T1/T2 재생성이나 의미 재판정을 수행하지 않는다. 대조가 성립한 S2 selected 1,314개를 전체 조사 universe로 고정하고, 기존 Menu evidence owner가 본 검증 전에 필수 exact FullType/fact-identity 집합, 적용 locale, 전수/대표 coverage 의무와 그 근거를 결정한다. 대상 목록·집합 identity/hash, source/consumer subject, observable/mapping readpoint와 기존 결정 reference를 같은 실행 기록에 남긴다. 승인된 sample 범위가 있다면 universe의 나머지는 별도로 계속 보고하며 sample 성공을 1,314개 전체 closure로 승격하지 않는다.
4. 이 기록이 없으면 필수 범위가 정해진 것으로 가정하지 않는다. 이후의 `필수 L3 범위`는 이 사전 기록만 뜻한다. 관찰 성공분·도구가 지원하는 부분집합으로 축소하거나 실패 후 coverage 의무를 낮추지 않는다. 범위 변경이 필요하면 기존 authority 아래 명시적 후속 scope decision으로 분리하며 원 실행의 실패·gap을 성공으로 소급 변경하지 않는다.
5. Admissible observable이 없으면 L3의 기존 `unverified_without_independent_consumer_evidence`를 유지하고 필수 범위를 미해결로 기록한다. Source relation 확인과 다른 독립 작업은 가능하지만 전체 T3 완료는 불가하다. Observable이 일부에만 있으면 없는 필수 항목도 같은 원칙으로 남긴다.
6. 사전 필수 집합에는 KO와 EN 각각의 관찰 readpoint·mapping·coverage를 명시한다. 한쪽 locale의 성공을 다른 쪽의 성공으로 계산하지 않는다. 기존 owner 결정과 해당 범위의 사용자 실행 승인을 재사용하고, 준비 기록은 기존 실행 보고에 합친다. 새 fact ID 체계나 별도 approval/closure artifact는 만들지 않는다.

**Validation:** pre-cutover call graph·source reference·hook 판단 근거·T2 S2-present/T1 selected exact-set missing/extra `0` 결과·L3 사전 범위/observable 결정을 기록한다. `no remaining consumer`, `non-Tooltip consumer remains`, `supported compatibility required`를 구분하며, 근거 없는 삭제 후보는 보존 상태로 남긴다. 현재 assembler가 `fact_id`를 노출하지 않는다는 사실만으로 observable 존재나 독립 closure를 선언하지 않는다.

### Change 3 — Product Copy와 Thin Exact Lookup

**Purpose:** T2 문자열을 의미 처리 없이 읽는 최소 runtime 경계를 만든다.

**Files:** 승인된 product data 경로와 lookup module, 필요 시 `.gitattributes`, 기존 require/locale helper.

**Implementation Notes:**

- 후보 배치는 `Iris/Data/IrisTooltipT2Data`와 `Iris/Data/IrisTooltipT2Lookup`이다. T2 파일이 이미 table을 반환하므로 payload rewrite나 wrapper 삽입이 기본 요구가 아니다. Adapter는 별도 파일에 둔다.
- Reader 입력은 exact string FullType과 explicit `ko` 또는 `en`이다. FullType의 lower/upper/trim/case-fold/alias replacement 및 unknown key 보정은 금지한다.
- Locale key는 기존 lifecycle의 `KO → ko`, `EN → en` 대응만 사용한다. `FR` 등 다른 key는 no-result이며 `ko ↔ en` fallback을 만들지 않는다.
- Locale 자체를 취득하지 못한 경우(nil·예외·유효 key 부재)에도 `no result → Iris section 미표시`로 처리하고 EN default substitution을 하지 않는다. Resolver/loader의 기본값이 이를 가리지 않도록 확인한다. 기존 helper만으로 구분할 수 없으면 같은 locale owner에 최소 additive status/accessor를 두고 기존 API 반환·Menu 동작을 보존한다. Tooltip에서 별도 `Translator` polling, 번역 엔진, live-switch 기반시설을 만들지 않는다.
- 일반 require cache를 사용한다. 첫 Alt 사용 시 load하는 것이 기본 후보이며 실제 first-use 또는 기존 lifecycle 내 boot-load 선택·이유·호출 readpoint를 구현 전에 기록한다. First-use이면 boot부터 최초 Alt 이전까지 payload materialization `0`, 최초 유효 Alt lookup에서 load, 후속 require cache 재사용을 관찰한다. Boot-load를 택하면 선언한 bootstrap 시점의 load와 Alt OFF lookup/validation `0`을 각각 확인한다. 우발적 eager load를 사후에 boot-load 선택으로 재분류하지 않는다.
- 반복 실패 재시도/로그를 막아야 할 때만 `unattempted/loaded/failed` 수준의 최소 module-load state를 둔다. FullType 결과 캐시·chunk index·manifest parser는 만들지 않는다.
- 선택된 locale record 전체를 draw 전에 검증한다. Table의 raw key/value를 조사해 정수 index `1..N` 이외 key, hole, non-string, 5개 이상, empty/whitespace-only, CR/LF를 거부한다. `#record`와 `ipairs`만으로 sparse/dictionary table을 정상으로 인정하지 않는다. `N=0`은 metadata key 없는 empty array일 때만 정상이다.
- 실패한 record에서 일부 row만 복구하지 않는다. Row를 trim·문자열화·정렬·재선택·삭제·자르지 않는다. Table mutation 없이 기존 순서로 소비한다.
- 한 FullType의 malformed/missing record를 전체 dataset corruption이나 다른 key의 실패로 확대하지 않는다. Module 자체 load failure와 정상 key miss의 내부 원인은 구분하되 사용자에게는 모두 Iris section 미표시다.

**Validation:** lookup/shape/locale/load timing/failure cases와 원본→product→Git checkout payload identity 검사를 Change 4의 renderer 사례와 같은 harness에 준비한다. 이 단계의 별도 테스트 실행이나 Change 4 진입용 PASS는 요구하지 않는다. 실제 삭제가 있으면 §7 replacement subset으로, 전체 coverage는 최종 focused로 확인한다. Module load failure·malformed record·unknown FullType에도 legacy trap `0`을 포함한다.

### Change 4 — Alt Cutover, Lifecycle, Layout, Failure Isolation

**Purpose:** 실제 Tooltip consumer를 T2 배열로 연결한다.

**Files:** `IrisAltTooltip.lua`; 필요한 경우에만 기존 locale/protected UI helper.

**Implementation Notes:**

착수 조건은 Change 2의 hook 판단과 Change 7 harness 준비다. Change 3과 함께 구현할 수 있으며 reader만의 선행 테스트는 요구하지 않는다. Alt의 summary 호출 edge를 static reader로 전환하되 legacy 구현 파일의 삭제·adapter 전환은 Change 5의 조건을 충족할 때까지 보류한다.

1. Alt OFF early return을 FullType/locale 해석, static lookup, record validation, temporary row array 생성보다 앞에 유지한다.
2. Alt ON에서 current item → exact FullType → 지원 locale → validated rows 순서로 읽는다. Summary, DetailViewModel, Classification/DVF/QG 및 Recipe/Moveables/Fixing 조회는 호출하지 않는다.
3. Change 2에서 근거 또는 owner 판정이 결속된 hook 범위 안에서 등록을 idempotent하게 유지하고 원본 render를 한 번 호출한다. 다른 global patch나 원본 동작을 대체하는 renderer는 추가하지 않는다. 구현 중 새로운 충돌이 드러나면 해당 cutover를 멈추고 판단을 갱신하며, 미해결 상태로 Change 5에 넘기지 않는다.
4. Iris lookup·measurement·overlay에 기존 보호 경계를 적용한다. Bootstrap 시 `ProtectedCall.ui`로 hook을 설치하는 것만으로 매-frame callback이 보호되는 것은 아니다. Vanilla error를 Iris error로 삼켜서도 안 된다.
5. `_irisRendered`는 frame의 이중 overlay 삽입을 막는 guard로 관리한다. Item A→B, supported→unsupported, Alt release, Menu 왕복, locale lifecycle 후 previous rows와 Iris height가 남지 않도록 base geometry 소유권과 reset 시점을 검증한다.
6. 정상 0줄·실패에서는 header/background/border/height padding을 만들지 않는다. Render 도중 실패 시 Iris가 바꾼 geometry를 되돌릴 수 있게 변경을 최소화한다. Partial invalid record는 draw 자체를 시작하지 않는다.
7. 현재 고정 `16px` 행 높이와 단일 `drawText`만으로 visual fit을 가정하지 않는다. PZ가 제공하는 기존 text measurement/wrapping surface를 확인해 physical height를 계산하고 viewport 경계·vanilla 영역을 존중한다. 해당 API의 동작은 실제 PZ에서 확인한다.
8. 최대 4는 logical row 수다. Wrapping에 따른 physical line 증가는 허용하지만 T2 row를 줄이거나 ellipsis로 자르지 않는다. 장문 KO/EN·화면 끝 배치 문제는 presentation 범위에서 해결한다.

**중복의 정확한 뜻:** T2 `Base.223Bullets`는 S3와 S4가 서로 다른 Recipe identity인데 동일한 사용자 문자열을 가진다. 이 두 row는 모두 보존한다. 중복 방지는 같은 frame에 Iris block을 두 번 붙이지 않는다는 뜻이며, 문자열 equality에 따른 deduplication이 아니다.

**Validation:** Alt OFF 신규 lookup/legacy 호출 `0`, Alt ON exact rows, 반복 render·Alt release·item/locale 전이·0줄 geometry·원본 render 호출 수·Iris failure 격리를 Change 3과 함께 검증한다. Poisoned-call/trap은 정상 hit와 module load failure·malformed record·unknown FullType 각각을 포함한다. 실행은 §7의 실제 삭제 전 최소 subset과 최종 focused에 묶으며 이 단계만을 위한 추가 실행은 없다. Mock geometry는 실제 PZ 시각 증거를 대체하지 않는다.

### Change 5 — Legacy 경로 Disposition과 기존 Test 계약 조정

**Purpose:** Alt의 의미 생산을 실제로 끊으면서 관련 없는 기능을 보존한다.

**Files:** Change 2 disposition 대상과 관련 current harness/test owner.

**Implementation Notes:**

- **실제 삭제·adapter 변경의 진입 조건:** Change 2 census/항목별 disposition 근거와 실제로 필요한 owner 결정, §7 replacement subset command exit `0`이 모두 있어야 한다. Reader와 Alt 전환을 함께 구현한 뒤 legacy 파일을 보존한 subject에서 한 번 실행한다. 변경으로 결과가 stale해졌으면 영향받은 subset만 다시 수행한다. 도구 부재·skip·미실행은 PASS가 아니다. Disposition이 보존뿐이면 선행 subset 없이 진행하고 최종 focused에서 static-only Alt를 검증한다.
- Alt에서 raw tag, numeric `tooltipFacts`, Recipe/Moveables/Fixing composition, UseCase count, 내부 quality/error line, menu guidance, legacy fallback을 도달 불가하게 만든다. 화면에 숨긴 채 상위 호출을 남겨 두지 않는다.
- 소비자가 없고 지원 계약도 없는 항목만 제거 후보로 실행한다. Non-Tooltip consumer가 남으면 그 경로를 보존한다. Compatibility adapter가 필요하면 기존 signature/result/copy-on-read를 보존하되 independent semantic payload나 복제 state를 만들지 않는다.
- Thin adapter로 기존 계약을 보존할 수 없으면 무리하게 의미 구현을 바꾸지 않고 해당 제거를 보류한다. Alt에서 격리된 legacy 코드의 잔존과 Alt path retirement는 별개다.
- Current test가 summary existence/cache hit를 요구하는 경우 T3 의도 변경에 해당하는 assertion만 새 관찰 계약으로 교체한다. Browser state, shared lazy lookup, Detail fact isolation, supported API 검증을 함께 삭제하지 않는다.
- T1 audit의 source inventory와 current validation membership 영향은 기존 owner 아래 bounded하게 처리한다. 과거 manifest/receipt/hash를 소급 수정하거나 legacy 제거를 이유로 T1/T2 전체 생성 절차를 재실행하지 않는다.

**Validation:** 삭제·adapter 변경 후 coverage는 최종 focused에 포함한다. 정상 및 module load failure·malformed record·unknown FullType 모두에서 legacy 호출 `0`, post-change source graph와 보존 consumer·supported facade 회귀를 확인한다. 삭제 직후 전체 focused를 별도로 반복하지 않는다. 삭제 전 PASS는 삭제 후 증거가 아니며, 게임 진입 전 필요한 syntax/lookup smoke는 Change 8에서 수행한다. 보존이면 가상의 삭제 전후 검증을 만들지 않는다.

### Change 6 — Menu Source Relation 확인

**Purpose:** Tooltip과 Menu의 같은 사실에 대한 관계를 독립 consumer readpoint로 검증한다.

**Files:** T2 provenance manifest; T1 D2 relation reader/harness; Browser category/projection, Detail assembler, Layer3 lookup/renderer, `IrisLayer3EnglishLookup.lua`와 `Layer3English/Index.lua`/selected chunk, 기존 KO/EN fact mapping, interaction collector/projection/renderer와 Wiki consumer.

**Implementation Notes:**

- **진입과 범위:** L3 independent identity 본 검증은 Change 2에서 사전 고정한 필수 집합·coverage 의무·admissible observable/mapping으로만 수행한다. 해당 결정이나 observable이 없으면 L2/L4 및 L3 source relation 조사는 계속할 수 있으나 independent L3 closure는 미해결로 기록한다. 본 검증에서 성공한 항목을 새 필수 범위로 삼지 않는다.
- **L2:** `IrisClassifications → StaticData.get("classifications") → IrisBrowserProjectionBuilder → Browser row → IrisBrowserCategoryIndex`의 source/projection이 기존 relation과 같은지 확인한다. Applicable 1,406은 category/primary identity, silence 874는 N/A 관계다. 변경이 있으면 기존 `tooltip_t1/d2.py`와 `tags_public_surface_isolation_harness.lua`의 실제 consumer 관찰을 재사용한다. Inheritance 시 predecessor D2 evidence locator/subject, exact support identity, source·consumer 경로/해시, T3 subject와의 relevant diff 및 적용 근거를 남긴다. `unchanged`라는 단일 문장만으로 inheritance를 인정하지 않는다.
- **L3 KO:** `IrisLayer3DataCurrent → IrisLayer3DataLookup → selected entry.text_ko → layer3_renderer → IrisItemDetailModelAssembler → Menu`의 실제 소비를 관찰한다. 현재 assembler에는 `fact_id`가 없으므로 same generation/같은 text를 independent fact-identity evidence로 승격하지 않는다. 사전 인정된 Menu-side record observation과 Tooltip 독립 authority mapping이 있는 경우에만 T2 S2 identity와 exact join한다.
- **L3 EN:** `layer3_renderer`의 기본 entry/public 조건 확인 뒤 `IrisLayer3EnglishLookup → Layer3English/Index → selected chunk의 exact FullType record → assembler → Menu`로 이어지는 별도 영어 소비를 관찰한다. 실제 선택 module/record를 기존 승인 영어 surface/fact mapping에 연결하고 T2 S2의 동일 fact identity인지 확인한다. KO 경로 성공이나 단순 EN 문자열 비교로 대체하지 않는다. 기존 mapping이 없거나 관찰할 수 없으면 EN gap을 남기며 production Menu에 새 fact ID를 주입하지 않는다.
- KO/EN은 같은 harness와 대상 목록을 재사용하되 관찰·missing·mismatch를 locale별로 분리한다. Runtime이 실제 선택한 record 관찰 없이 source 파일끼리 비교한 결과는 shared-authority relation에 머문다. 한 locale의 성공만으로 bilingual closure를 주장하지 않는다.
- L3 결과는 전체 selected 1,314 universe, 사전 필수 집합, 실제 observed/missing/mismatch/unobservable 집합을 분리한다. Whole-set trace가 가능하면 전체 결과를 사용하되 sample 또는 관찰 가능 subset으로 미해결 항목을 차감하지 않는다. Tooltip fact ID를 Menu에 주입해서 되받거나 Menu 표시 문자열을 역분석하지 않는다.
- L3 미해결 원인은 최소 두 가지로 나눈다: **A. actual Menu source relation 자체가 확인되지 않음**, **B. source relation은 확인됐으나 independent fact identity observation ceiling이 남음**. 실제 identity mismatch는 관측 한계와 별도로 기록한다. B를 verified로 바꾸거나 A/B 구분을 새로운 product state enum으로 만들지 않는다.
- **L4:** `interactionState.lines → IrisBrowserInteractionCollector → IrisBrowserInteractionProjection.build`의 `identity=label_key`, `source`, Recipe `recipe_id/recipe_nav_ref`를 사용한다. T2 S3/S4 `semantic_identity`는 Menu structured set과 exact subset 관계로 비교한다. 실제 Menu가 소비하는 경로까지 확인하며 임의 fixture table에 같은 ID를 넣는 것으로 대체하지 않는다.
- Recipe-only / Right-click-only / both-source를 각각 포함한다. Richer Menu detail은 허용하지만 source substitution·다른 Recipe identity는 mismatch다. Locale별 generic T2 문장의 유사성으로 identity를 인정하지 않는다.

**Validation:** L2 inheritance binding, L3 사전 결정과 KO/EN별 실제 관찰의 exact-set reconciliation·원인별 unresolved, L4 selected identity/source relation을 공통 fixture로 묶어 확인한다. Menu source/consumer/mapping이 이후 바뀌지 않았으면 기존 관찰을 최종 보고에서 재사용하고 별도 suite를 반복하지 않는다. Self-evidence와 rendered-string parsing `0`. 필수 L3 항목의 어느 locale든 source relation 부재·관측 불가·missing/mismatch가 남거나 사전 범위 결정이 없으면 전체 T3 완료 조건은 충족하지 않는다.

### Change 7 — 공통 검증 도구 준비와 게임 수정 후 최종 Regression 종합

**Purpose:** Runtime 계약을 실제 Lua 경계에서 검증하고 기존 검증의 의미를 보존한다.

**Files:** 기존 `Iris/test/lua/` harness와 Python owners, 필요 시 신규 focused Tooltip harness 하나 및 이를 실행하는 최소 current test wrapper.

**Implementation Notes:**

- **선행 준비:** Change 1/2 이후, Change 3/4와 함께 사용할 최소 harness·lookup spy·poisoned legacy trap·wrapper/command를 준비한다. Reader와 renderer 사례를 함께 작성하되 작성 완료마다 테스트를 실행하지 않는다. 첫 실행은 실제 legacy 변경 직전의 replacement subset 또는 그 변경이 없을 때 계획된 후반 검증이다. 아직 없는 replacement 구현을 미리 PASS로 주장하지 않는다.
- 기존 harness를 활용할 수 있으면 중복 entrypoint를 만들지 않는다. Replacement 검증을 막는 기존 Tooltip 전용 cache/summary assertion은 이 준비 과정에서 static 계약 assertion으로 대체할 수 있다. Legacy production 파일 삭제는 Change 5까지 보류하고 공유 Browser/Detail 검증은 유지한다.
- **변경 후 종합:** Change 8/9의 package/game 검증과 필요한 presentation 수정이 끝난 뒤 최종 코드의 focused·관련 regression·current-required gate를 수행한다. 실제 삭제가 있었다면 최종 focused에 replacement subset도 포함한다. 삭제 전 결과는 삭제 후 증거를 대체하지 않지만, 삭제 직후와 최종 시점에 같은 전체 focused를 두 번 실행할 필요는 없다. 변경 없는 Menu 관찰·payload 전수검사·유효한 syntax/smoke는 §7의 입력 범위 재사용 규칙으로 참조한다.
- T2 production copy의 전수 structural/identity 검사는 한 번 집계하고 개별 2,280개 test function이나 locale×row×source×error Cartesian product로 펼치지 않는다.
- Poisoned legacy modules로 정상 hit와 load failure·malformed record·unknown FullType의 호출 비도달을 각각 확인한다. Lookup/load spy로 Alt OFF와 선언한 materialization 시점, 실제 production Lua reader/renderer로 shape·lifecycle·실패 동작을 검증한다. Test가 성공하도록 production admission bypass를 만들지 않는다.
- Standalone Lua와 PZ Kahlua의 차이 때문에 automated PASS를 actual game PASS로 기록하지 않는다.
- Current required validation의 등록/applicability와 선행 조건은 초기에 확인하되, final exact subject gate의 실행은 game 수정까지 끝난 뒤 한 번의 terminal sequence로 모은다. 기존 owner가 요구하는 Run A/B/comparator 등의 횟수·순서는 유지하며, 이미 current gate가 실행하는 동일 regression을 별도 수동 suite로 중복 실행하지 않는다. 필요한 installed tooling/environment는 최종 package source에 맞춰 기존 경로로 준비하고 성공한 동일 subject에 confidence 재실행을 하지 않는다.

**Validation:** §7의 최소 실행 단위·command·fixture·failure attribution 기준을 따른다. 실제 삭제가 있을 때의 선행 subset과 최종 focused/gate는 각각 실제 subject·command·exit를 기록한다. 필수 tooling 부재, skip, 수집 누락은 PASS가 아니며 해당 required 축을 BLOCKED로 남긴다. 새 seal/validator/검증 집계 플랫폼을 추가하지 않는다.

### Change 8 — Package / Install / Loaded-Module Identity

**Purpose:** 검증한 데이터가 실제 게임에서 선택되는 파일까지 동일함을 확인한다.

**Files:** `Iris/tools/package_iris.ps1`, `Iris/test/validate_disposable_package.ps1`, external candidate package/install, 실제 PZ load log/readback.

**Implementation Notes:**

1. 기존 package script는 explicit repository-external `OutputRoot`를 요구하며 일반 media 파일을 복사하고 Layer3만 current-generation projection으로 제한한다. 먼저 T2 새 파일이 이 경로에 그대로 포함되는지 확인한다. 필요 없는 installer·Registry는 추가하지 않는다.
2. `current_runtime_payload` package를 사용하고 기존 Layer3 pointer/current generation·lookup identity를 보존한다. T2를 넣는다는 이유로 RTC applicability를 요청하지 않는다.
3. Source T2 → repository working copy → clean checkout → package/ZIP 내부 copy → disposable installed copy의 exact path, byte count, SHA-256을 기록한다. Runtime reader/renderer의 코드 hash는 payload hash와 별도 기록한다.
4. 기존 disposable package validator는 검사 뒤 candidate를 삭제하므로 그 임시 결과를 그대로 game install evidence로 쓰지 않는다. 실제 PZ 확인용으로 보존되는 별도 candidate package와 install을 명시한다.
5. 기존 validation install 절차와 실제 destination을 먼저 확인한다. 일반 사용자 설치 경로를 임의로 가정하거나 덮어쓰지 않는다. 동일 mod id/module의 local·Workshop·다른 활성 copy가 load를 가로채는지 확인한다.
6. Installed Lua syntax와 exact lookup smoke를 수행한 뒤 실제 PZ log의 loaded path, 활성 mod set, 세션 identity와 readback을 결속한다. 디스크 hash만으로 loaded-module identity를 주장하지 않는다. 경로를 관측할 수 없으면 해당 축을 미확인으로 남긴다.
7. Package/game 진입 전 syntax와 installed lookup smoke는 필수이나 전체 focused·canonical gate를 미리 실행하는 이유로 확대하지 않는다. Package와 install의 검증 대상 Lua 집합·상대경로·bytes가 동일하고 기존 command owner가 허용하면 동일 syntax 결과를 참조한다. 설치 경로에서의 실제 module resolution smoke와 실제 PZ loaded-route 관찰은 생략하지 않는다. Game 확인 뒤 코드 수정이 생기면 영향받은 package/install을 갱신하고 필요한 smoke·관찰만 다시 수행한다.

**Validation:** product/package/install hash equality, module locator 일치, stale load candidate 조사, installed lookup smoke, 실제 loaded route. Package success·설치 success·게임 load success를 각각 구분한다.

### Change 9 — 실제 PZ 기능·시각·실패 격리

**Purpose:** PZ Tooltip reuse와 실제 font/layout을 포함한 대표 동작을 확인한다.

**Files:** verified candidate install, existing game probe/checklist 경로, external observation 기록.

**Implementation Notes:**

- 실행자는 관찰 전에 PZ build, 활성 mod 목록, font/UI scale/resolution, KO/EN lifecycle과 요구 coverage를 만족하는 대표 집합을 기록한다. 기존 authority의 별도 승인 요구가 없다면 환경·표본 선택만으로 대기하지 않는다. 환경을 바꾸면 별도 관찰로 구분하고 claim을 확인한 환경 밖으로 확대하지 않는다. 게임이 언어 변경에 재시작을 요구하면 그 절차로 확인하며 live switching 지원을 발명하지 않는다.
- §7의 row count·source kind·exact pair·장문 후보 중 여러 축을 함께 충족하는 최소 집합을 선택한다. 실제 생성/접근 불가 item은 자동검증과 게임 검증 범위를 나눠 기록한다.
- Alt OFF/ON/release, repeated Alt, rapid item switch, supported→unsupported, 0줄, Menu open/return, KO/EN 문장과 순서, duplicate block·stale height를 확인한다.
- Wrapping, 행간, background 높이, vanilla overlap, clipping, off-screen expansion을 확인한다. 문제가 있으면 presentation만 수정하고 T2 내용은 바꾸지 않는다.
- Failure injection은 별도 disposable install 또는 기존 injection route에서만 수행한다. Malformed record/load failure의 대표 조건에서 Iris block 없음, vanilla 표시 유지, 사용자 오류 문구 없음, 반복 로그 폭주 없음, 게임 상호작용 지속을 확인한다.
- 주입 후 원래 verified package로 복원하고 정상 hash와 load를 다시 확인한다. 실패 주입 결과를 정상 install identity로 기록하지 않는다.
- 게임에서 발견한 presentation 문제의 수정·필요한 재관찰을 마친 뒤 Change 7의 최종 gate를 수행한다. 이후 다시 코드가 바뀌면 영향받은 증거를 갱신하고 기존 final exact-subject 요구도 충족한다. 같은 bytes의 package를 단순 재복사했거나 결과 문서만 작성했다는 이유로 전체 게임 시나리오를 반복하지 않는다. 실제 PZ를 실행할 수 없으면 해당 축을 미검증으로 남기며 자동 테스트를 추가 반복해 대신하지 않는다.

**Validation:** 각각의 관찰에 build/install/module identity, FullType, locale, 조작 순서, 실제 결과, screenshot/log locator를 결속한다. 대표 관찰을 전수 universe나 모든 외부 모드 호환성 증거로 확대하지 않는다.

### Change 10 — Evidence-Bounded Closeout

**Purpose:** 실제 수행·미수행 범위를 분리해 T3 결과를 남긴다.

**Files:** 기존 결과 보고 경로, 필요 시 ecosystem docs와 current route의 additive successor.

**Implementation Notes:** 최종 subject와 §12의 축별 결과를 기록한다. T1/T2 historical machine subject·closeout·실패 이력을 수정하지 않는다. 최종 state는 기존 정의와 증거에 따라 실행자가 기록하고, 실제로 owner-reserved인 evidence 상태 변경·승인 및 independent review만 기존 governance를 따른다. 구현만 끝났거나 게임·Menu 관찰이 부족하면 그 범위를 숨기지 않는다. 기록 자체를 위해 새 승인·봉인 절차를 만들지 않는다.

**Validation:** 필수 증거의 missing/stale/subject mismatch 여부와 실제 command exit를 확인한다. 필수 축이 모두 닫힌 경우에만 전체 T3 completion을 허용한다.

---

## 7. Validation Plan

검증 영역은 runtime, compatibility, migration/content identity, regression, public-facing behavior다. 범위가 넓다는 이유로 테스트 수나 중간 PASS 관문을 늘리지 않는다. 아래 필수 성질을 공통 table-driven 사례와 기존 gate로 충족하고, T2 generation 재인증·추가 confidence 검증은 수행하지 않는다.

### Automated Validation

| Family | 최소 필수 사례 | 확인할 결과 |
| --- | --- | --- |
| Input / migration | exact three-file binding, universe 고정 전 T2 S2-present/T1 selected exact-set 대조, product/checkout/package/install bytes | 단일 T2 출처, S2 집합 missing/extra `0`(개수만으로 대체 불가), strings/order/exact key 불변 |
| Load timing | 사전 기록한 first-use/boot-load 선택, boot→최초 Alt→반복 lookup | 선언한 시점 외 materialization 없음, module cache 재사용, OFF lookup/validation `0` |
| Lookup | KO/EN, 0·1·2·3·4줄, unknown FullType, collision pair | exact row equality, 0줄 no section, case identity 분리 |
| Locale | unsupported key, missing locale, nil/예외 등 locale 취득 실패, supported lifecycle | 취득 실패도 no-result, EN default substitution·타 언어 대체·stale row 없음 |
| Atomic shape | non-table, hole, keyed/mixed table, non-string, 5+줄, empty/whitespace-only, CR/LF | record 전체 거부, repair/salvage 없음 |
| Fault | absent module, require exception, invalid root, faulty selected record | Iris 미표시, vanilla 유지, repeated retry/log 제한, legacy trap `0` |
| Alt / lifecycle | OFF, press/release, 반복 render, A→B, known→unknown, Menu 왕복 | OFF lookup/semantic call 0, duplicate block·stale geometry 없음 |
| Legacy retirement | 모든 금지 호출에 trap을 건 공통 fixture에서 정상 hit·load failure·malformed record·unknown FullType의 대표 사례 | 각 사례의 모든 legacy semantic call `0`; 실제 삭제 때만 삭제 전 subset 추가, fault fallback 없음 |
| Row preservation | 같은 문자열·다른 selected identity의 S3/S4 | 문자열 deduplication 없음 |
| Menu relation | L2 inheritance binding, L3 사전 범위와 KO entry/EN lookup·index·chunk 각각의 actual observation, L4 structured subset | self-attestation `0`, locale별 필수 집합 대비 결과·unresolved, KO 성공으로 EN 대체 금지, 사후 범위 축소 없음 |

Runtime record check는 small array에 필요한 범위만 수행하고 매 frame full dataset을 순회하지 않는다. Dataset 전수 검사는 offline 검증에서만 수행한다.

**최소 테스트 구성과 실행 규칙**

위 matrix는 검증 의무 목록이지 각각의 신규 test function/file 목록이 아니다. 기존 harness를 우선 사용하고, 부족할 때만 Lua harness 최대 1개와 그 실행용 최소 wrapper 최대 1개를 추가한다. 사례는 세 공통 묶음으로 관리한다: **① input/lookup/locale/shape/load**, **② renderer/lifecycle/fault/legacy**, **③ Menu relation(KO/EN 포함)**. 이 묶음 수를 새 authority나 top-level test 수의 의무로 만들지 않는다.

- 정상 0·1·2·3·4줄은 각각 최소 한 사례로 확인하고 KO/EN·source kind·동일 문장 보존·exact pair가 가능한 한 같은 사례를 공유한다. 모든 row count를 두 locale 및 모든 source/error와 곱하지 않는다. Shape 오류들은 table-driven negative row로 묶되 hole/mixed key/non-string/5+줄/blank/CR·LF의 서로 다른 결함을 누락하지 않는다.
- Load failure·malformed record·unknown FullType과 정상 hit는 공통 poisoned fixture로 확인한다. 모든 금지 legacy 호출을 동시에 trap하되 source별로 별도 test suite를 만들지 않는다. 게임 전 installed smoke도 이 harness의 작은 선택 모드를 재사용한다.
- **최종 focused:** 기본 1회다. 최종 코드의 runtime coverage와 실제 legacy 변경 후 replacement 사례를 포함한다. 동일 입력 범위에서 이미 유효한 Menu 관찰·전수검사 결과는 참조하고, 누락·변경 영향이 있는 항목만 포함한다. 기존 final gate가 같은 focused 항목을 실제 실행해 필수 결과를 제공하면 별도 standalone 실행을 추가하지 않는다.
- **삭제 전 replacement subset:** 실제 legacy 삭제·adapter 변경이 있을 때만 기본 1회 추가한다. 최소 내용은 정상 exact rows, OFF 비도달, malformed atomic rejection, module-load 실패·unknown key, press/release·item 전환·vanilla 보존과 각 정상/fault 사례의 legacy trap `0`이다. Reader만·renderer만의 중간 실행, 전체 Menu 검사, canonical gate를 이 선행 실행에 포함하지 않는다. Legacy를 보존하면 이 추가 실행은 없다.
- **그 밖의 필수 확인:** admission·집합/shape 전수검사·Menu 관찰은 동일 입력에 대해 한 번 집계한다. Package/install identity, 게임 진입용 syntax/lookup smoke, 실제 게임 관찰은 각 소비 경계를 확인하는 데 필요한 최소 범위로 유지한다. 이미 같은 파일 집합/bytes에서 통과한 syntax 등은 command owner가 허용하는 한 재사용하고, copy identity가 actual load/lookup/game 검증을 대신하게 하지는 않는다.
- **최종 regression/gate:** 게임 수정 후 한 번의 terminal sequence로 모은다. 기존 mandatory denominator, required test identity, 정확한 command, Run A/B/comparator 등 명시된 반복 요구는 줄이지 않는다. Gate에 포함된 같은 regression은 별도 실행하지 않는다. 이 계획의 최소화는 기존 authority의 필수 검증 면제가 아니다.
- **재사용/재실행:** 한 실행 결과의 실제 subject·입력·command·exit는 그대로 기록한다. Changed subject에 과거 PASS를 옮겨 쓰지 않는다. 그 검사의 입력 code/data/test/config가 변하지 않고 기존 계약이 inheritance를 허용하는 경우에만 관련 diff/identity로 참조한다. 실패, 영향받는 변경, 도구/환경 변경, 명시된 same-subject 의무가 있을 때 필요한 범위만 재실행한다. 이를 위한 새 comparator·receipt·proof artifact는 만들지 않는다.
- 계획에 없는 중간 테스트나 성공 후 confidence 반복은 하지 않는다. 실행 중 60초를 넘기지 않는 간격으로 상태를 확인하고, 비정상 장기 실행·무한루프 징후가 있으면 중단해 원인을 확인한다. 단순 무출력만으로 실패 판정하지 않으며, 중단·timeout은 PASS가 아니다. 기존 timeout을 임의로 해제하지 않는다.

따라서 정상 진행의 runtime focused는 **최종 1회**, 실제 legacy 제거/adapter 변경이 있을 때만 **직전 최소 subset 1회**가 더해진다. 이것은 admission·설치 smoke·Menu/게임 관찰·기존 필수 gate까지 합친 총 명령 수가 1~2개라는 뜻이 아니다. 필요한 검증 성질은 유지하되 사례 공유와 실행 재사용으로 수를 줄인다.

**실행 command와 owner**

- Lua 필수 검증은 repository root에서 `powershell -ExecutionPolicy Bypass -File .\tools\check_lua_syntax.ps1`를 사용한다. Default roots는 runtime과 기존 package 경로이며 external package/install 검사에는 `-Roots`로 실제 대상을 지정한다. 동일 대상 집합/bytes의 결과 재사용이 기존 command owner 아래 허용되면 중복 실행하지 않는다. Script가 없는 root를 건너뛸 수 있으므로 대상 경로 존재와 검증 file count를 함께 확인한다.
- Focused T3 command는 Change 7 선행 준비에서 실제 harness/wrapper와 필요한 subset 선택 방식을 확정하고 기존 command owner에 등록한다. 실행 시점은 위 최소 실행 규칙을 따른다. 같은 경로로 subset/full/smoke를 선택할 수 있게 하되 T3 CLI/framework를 별도로 만들지 않는다. 실제 command·subject·exit code·도구 availability를 남기며 아직 없는 `validate tooltip-t3` command를 실행 가능한 것으로 기재하지 않는다.
- Python 검증은 `uv run python <script>` 또는 기존 프로젝트 환경을 사용하는 `uv run --project .\Iris\tooling python -B -m pytest ...`를 사용한다. Lua harness를 Python wrapper가 실행할 경우 wrapper와 내부 Lua exit 모두 0이어야 한다.
- 기존 회귀 후보는 아래와 같다. 실제 current membership을 대조하고 변경 경로의 owner family를 선택한다. 전부를 이름만으로 새 mandatory gate로 승격하거나 같은 harness를 불필요하게 반복 실행하지 않는다.

| 기존 test owner | 관련 검증 |
| --- | --- |
| `Iris/build/description/v2/tests/test_iris_browser_state_selection_search_acceptance.py` | Browser state와 기존 Tooltip cache assertion의 전환 |
| `Iris/build/description/v2/tests/test_iris_browser_single_pass_cache_contract.py` | 같은 Browser harness를 공유하는 owner 영향 |
| `Iris/build/description/v2/tests/test_iris_detail_view_model_acceptance.py` | Detail/Menu 모델 회귀 |
| `Iris/build/description/v2/tests/test_iris_legacy_surface_acceptance.py` | supported facade·legacy file source guard |
| `Iris/build/description/v2/tests/test_iris_residual_runtime_acceptance.py` | 기존 Lua runtime acceptance |
| `Iris/build/description/v2/tests/test_iris_session_cache_ownership.py` | summary/cache ownership inventory 변경 |
| `Iris/build/description/v2/tests/test_layer3_lazy_lookup_contract.py` | 공유 lazy lookup 보존 |
| `Iris/build/description/v2/tests/test_usecase_lazy_lookup_contract.py` | UseCase router/fallback의 non-Tooltip 회귀 |
| `Iris/test/test_layer4_runtime_projection.py` | Menu structured interaction projection |
| `Iris/test/validate_disposable_package.ps1` | package projection·syntax·기존 package 비변경 |

- Canonical full validation의 literal·인자·applicability·receipt 경계는 `Iris/build/ENTRYPOINTS.md`의 Receipt-bound full validation과 `Iris/validation/clean_checkout/contracts/canonical_gate.json`, `Iris/_docs/round3/current_route_required_validations.json`을 따른다. 선행 요구는 초기에 확인하되, 별도 명시가 없으면 Change 9의 수정 종료 후 final exact T3 subject에서 수행한다. T2 gate receipt로 대신하거나 membership/Run A·B/comparator 조건을 복제·완화하지 않는다. Gate 이후 코드가 바뀌면 기존 same-subject 규칙을 다시 충족해야 한다.
- Package command는 같은 ENTRYPOINTS의 Package output을 따른다. Explicit external root와 `current_runtime_payload`를 사용한다. `-Clean` 등 삭제를 수반하는 옵션은 검증된 disposable root에만 적용한다.
- Java/Gradle·JS/TS product 코드는 기본 scope에 없으므로 `.\gradlew test`나 `pnpm biome check .`를 T3 Lua 검증의 대체로 쓰지 않는다. 실제 해당 코드 변경이 생기면 사용자 지정 관련 command를 추가한다.

**판정:** 정확한 관련 command가 exit `0`인 경우만 PASS다. Tooling 부재는 BLOCKED, 비정상 exit는 원인별 실패, 미실행은 미검증이다. 기존 파일 existence·과거 report·테스트 skip은 실행 성공이 아니다. Current gate 실패가 T3 밖에서 발생해도 숨기지 않고 attribution과 미완료 축을 함께 기록한다.

### Manual Validation

아래는 manifest에서 확인한 **대표 후보**다. 실행자가 실제 접근 가능성과 요구 coverage를 확인해 최소 집합을 선택하며 기존 authority가 요구하지 않는 별도 표본 승인 절차를 추가하지 않는다.

| Logical rows | FullType 후보 | 추가 관찰 포인트 |
| ---: | --- | --- |
| 0 | `Base.BaguetteDough` | header/background/spacing 없음 |
| 1 | `Base.223Clip` | Layer3-only 한 줄 |
| 2 | `Base.223Box` | Layer3 + Recipe |
| 3 | `Base.223BulletsMold` | S1/S2/S3 order |
| 4 | `Base.223Bullets` | 같은 surface인 서로 다른 Recipe row 보존 |
| Exact pair | `Base.LemonGrass`, `Base.Lemongrass` | item identity 병합 없음 |

추가로 actual structured source에서 Recipe-only·Right-click-only·both-source coverage를 확정하고, 장문 KO/EN 및 unsupported item을 선택한다. 같은 item이 여러 축을 충족해도 된다. 모든 후보가 실제 PZ build에서 생성 가능하다고 가정하지 않는다.

각 supported 환경에서 Alt press/release·빠른 전이·반복 Alt·Menu 왕복·locale 재초기화/재시작, physical wrapping/height/overlap/clipping/화면 경계, disposable failure injection을 확인한다. Runtime module locator와 같은 세션의 관찰이어야 하며 PZ build·active mod set·font·UI scale·resolution을 각 관찰에 연결한다. Visual 결과는 이 환경 집합 밖으로 일반화하지 않는다.

### Validation Limits

- 이번 **계획 작성**에서는 코드/manifest/closeout/route와 실제 파일 hash만 읽었다. T3 implementation, Lua/focused/canonical regression, package 생성, install, PZ 실행은 하지 않았다.
- Standalone Lua는 PZ Kahlua·engine-bound object·실제 `ISToolTipInv` lifecycle 및 font renderer의 완전한 대체가 아니다.
- L3 현 consumer의 record 선택과 독립 fact mapping을 관찰하지 못하면 shared-authority relation만으로 1,314개 independent Menu 검증을 주장하지 않는다. KO 관찰이 EN의 별도 lookup/index/chunk 관찰을 대체하지 않는다.
- Change 2에서 admissible observable이 없다고 판정되거나 필수 L3 범위가 사전 결정되지 않으면, 다른 작업이 진행되더라도 전체 T3 완료는 불가하다. 검증 후 관찰 가능분만을 필수 범위로 바꾸어 이 한계를 제거하지 않는다.
- Representative game coverage는 2,280개 전수, 모든 L3 fact, 모든 외부 모드·화면 환경으로 확대하지 않는다.
- Multiplayer·long-session·release/deployment·RTC/DVF/Publish·성능 인증은 out of scope다.

---

## 8. Risk Surface Touch

### Authority Surface

제한적으로 접촉한다. Classification=L2, DVF/current approved facts=L3, QG=L4, T2=static projection의 의미 소유권을 보존한다. T3는 lookup/presentation/integration/evidence만 담당한다. Legacy 지원 계약·Menu evidence 상태·gate applicability·closeout 결정은 기존 owner를 따른다.

### Runtime Behavior Surface

직접 변경한다. Legacy summary와 dynamic `tooltipFacts` 대신 T2 배열을 사용하고 Alt/item/locale lifecycle, Iris-local failure handling, Tooltip layout을 변경한다.

### Compatibility Surface

Vanilla render wrapper, 지원 require/API, copy-on-read, locale helper, Browser/Detail/Wiki, package/install 경계를 접촉한다. 기존 원본 render 순서와 Menu 진입을 보존하며 관련 없는 global patch를 복원하지 않는다.

### Sealed Artifact Surface

T2 staging/manifest/closeout과 T1/owner 산출물은 read-only다. Product copy는 integration 대상이며 historical subject 대체물이 아니다. Git checkout 줄바꿈까지 포함한 payload identity를 확인한다.

### Public-Facing Output Surface

Alt Tooltip의 실제 정보 source를 교체한다. 최대 4 logical rows, T2 문자열·순서·동일 문자열의 복수 row를 보존한다. Invalid input은 Iris section 미표시이며 내부 오류·quality·guidance 문장을 새로 노출하지 않는다.

---

## 9. Risk Analysis

### Architecture Risk

- **높음 — semantic path 잔존:** tag branch만 제거하면 Summary가 여전히 Detail/Recipe/UseCase를 조회한다. Alt 상위 호출 edge와 fault fallback까지 비도달 검증한다.
- **높음 — Menu self-attestation/EN 경로 누락:** L3 `raw/display`나 T2 `semantic_identity`를 독립 증거로 오인하거나 KO lookup만 확인하고 EN도 성공 처리할 수 있다. KO record와 EN의 실제 lookup/index/chunk 관찰을 기존 독립 mapping에 각각 연결하고 관측 불가 범위를 locale별로 남긴다.
- **높음 — L3 완료 기준의 사후 축소:** 관찰된 subset을 필수 범위로 바꾸지 않도록 Change 2에서 owner의 exact 대상·coverage 의무·admissible observable/mapping 결정을 결속한다. Source relation 부재와 독립 identity 관찰 한계를 나누어 보고하며 어느 쪽도 자동 closure하지 않는다.
- **중간 — 불필요한 상태 계층:** 979,485-byte static 파일의 load 비용만으로 chunk/cache/Registry를 추가하지 않는다. 필요성의 실제 근거 없이 구조를 확장하지 않는다.

### Runtime Risk

- **높음 — vanilla 실패 전파:** hook 설치만 보호하고 frame callback을 보호하지 않는 경우를 검증한다. Iris 작업만 격리하고 원본 render는 보존한다.
- **높음 — malformed partial display:** `#`/`ipairs`만 사용한 sparse-array 오판을 막고 전 record를 draw 전 검증한다.
- **중간 — locale default 오인:** 실제 unsupported key 또는 취득 실패를 EN으로 대체하지 않는다. 같은 locale owner의 lifecycle/status 안에서 해결한다.
- **중간 — stale geometry/layout:** 현재 누적 height 조정과 고정 lineHeight가 PZ reuse·장문에서 문제를 낼 수 있다. Alt release/0줄/빠른 item 전이와 physical wrapping을 실제 게임에서 확인한다.
- **중간 — 반복 실패:** load miss를 매 render 재시도하거나 dev log를 무제한 출력하지 않는다.
- **중간 — 예상과 다른 eager load:** 실제 load timing 선택을 먼저 기록하고 boot/최초 Alt/후속 lookup 관찰로 대조한다. Alt OFF의 lookup 금지와 payload의 load 시점은 별도로 검증한다.

### Compatibility Risk

- **높음 — validated/loaded data divergence:** working tree hash만 같아도 checkout newline·package 누락·Workshop 우선 로드가 다를 수 있다. Copy chain과 loaded locator를 각각 확인한다.
- **높음 — exact identity 파손:** Lua뿐 아니라 PowerShell/JSON decoder와 검증 집합에서도 case-insensitive 병합을 금지한다.
- **중간 — hidden consumer 제거:** listed manifest·상위 compatibility delta·test/tooling source inventory를 함께 조사한다. 근거 불충분 항목은 보존한다.

### Regression Risk

- **높음 — replacement 검증 전 legacy 삭제:** Reader/Alt를 묶어 구현하되 실제 삭제·adapter 변경 직전에 최소 replacement subset exit `0`을 요구한다. 정상/fault legacy trap은 최종 focused에서도 확인한다. 보존 시 가상의 삭제 전후 실행은 만들지 않는다.
- **중간 — 게임 수정 전 전체 gate 반복:** 최종 전체 gate는 package/game 수정 종료 뒤 수행한다. 변경 영향이 없는 기존 결과는 허용 범위 안에서 재사용하되 최종 same-subject gate 의무를 오래된 PASS로 대체하지 않는다.
- **중간 — cache assertion의 잘못된 유지/삭제:** 기존 `tooltip_cache_hits=1` 때문에 새 cache를 만들거나 Browser 검증 전체를 삭제하지 않는다. 의도 변경 부분만 static contract로 대체한다.
- **중간 — 동일 문자열 row 삭제:** `Base.223Bullets`의 다른 Recipe identity 두 줄을 dedupe하지 않는다.
- **중간 — T1 source inventory drift:** Summary 파일 제거가 `MENU_TOOLTIP_SOURCES`와 current test source guard에 영향을 준다. 현재 참조만 owner 절차로 정리하고 historical seal은 수정하지 않는다.
- **낮음 — 0줄 padding·duplicate block·manifest miswiring:** direct no-display assertion, per-frame guard, runtime require inventory로 검증한다.

---

## 10. Rollback Plan

Rollback은 implementation/package 복원이며 정상 runtime에 T2 failure→legacy semantic fallback을 추가하는 기능이 아니다.

1. 실행 전 predecessor implementation subject, 관련 파일 diff, package inventory와 validation install identity를 기록한다. 기존 사용자 변경은 rollback 대상에서 제외한다.
2. T2 input defect이면 product adoption을 중단하고 upstream correction을 기다린다. External T2 staging이나 historical closeout을 수정하지 않는다.
3. Runtime 실패이면 T3 candidate reader/renderer/관련 config 변경을 predecessor known-good 구현으로 되돌린다. 새 product copy는 T3가 추가한 범위만 제거하며 공용 Menu data/index를 삭제하지 않는다.
4. Consumer 근거가 불충분하면 legacy 제거를 먼저 되돌리거나 보류한다. 정상 Alt path에 fallback을 재연결하지 않는다.
5. Package/install identity mismatch이면 그 candidate를 completion evidence에서 제외하고 검증된 package로 disposable install을 복구한다. 일반 사용자 설치·외부 모드 파일은 임의 삭제하지 않는다.
6. Failure injection 후 별도 validation copy를 폐기/복원하고 expected hash 및 load를 다시 확인한다. Recursive delete/move는 PowerShell 단일 경로로 수행하며 resolved absolute target이 명시한 disposable root 내부인지 먼저 확인한다.
7. Layout 문제는 T2 문장 축약이 아니라 presentation 수정 또는 candidate rollback으로 처리한다. 실패/blocked 기록은 덮어쓰지 않고 후속 결과와 함께 보존한다.

---

## 11. Governance Constraints

- `Philosophy.md`의 근거·중립성·정보 전용·Alt 최대 4줄·Lua-only·Hub & Spoke/SPI·호환성 원칙을 유지한다.
- T1/T2와 source owner의 의미·identity·locale·selected order를 재판정하지 않는다. Manifest/closeout을 runtime 정책 입력으로 사용하지 않는다.
- Existing authority ownership, supported public surface, current validation owner와 protected delta 절차를 우회하지 않는다. 기존 승인을 같은 경로의 미래 변경 전체 승인으로 확대하지 않는다.
- Additive amendment와 minimal diff를 우선하며 unrelated refactor, historical evidence rewrite, blanket authority/gate 수정은 하지 않는다.
- Runtime/build-time을 분리한다. 검증 도구는 Python/PowerShell을 사용할 수 있으나 PZ product logic은 Lua만 사용한다.
- 새로운 T3 seal/approval/state taxonomy, validation-of-validation, mutable latest pointer를 만들지 않는다. 외부 실행 경로와 command는 기존 owner에 결속한다.
- Current-required gate는 기존 applicability에 따라 수행한다. 로드맵에서 T3 전용 gate 문구가 보류됐다는 사실은 기존 요구 면제 사유가 아니다.
- L3 필수 대상·coverage 의무와 KO/EN 각각의 admissible observable은 본 relation 검증 전에 기존 Menu evidence owner 기준으로 고정한다. 기존 결정과 해당 범위의 실행 승인을 재사용하며, 관찰 성공분으로 범위를 축소하거나 Tooltip 자기 출력으로 독립 증거를 대체하지 않는다. 새 decision schema·Registry·승인 artifact는 만들지 않는다.
- 실제 legacy 삭제·adapter 변경은 최소 replacement subset 검증 이후에만 수행하며, 변경 후 검증은 최종 focused에 합친다. Hook/non-interference에 실제 충돌이 있으면 기존 Iris runtime/compatibility owner의 판단을 Change 4 전에 받으며, 기존 authority로 이미 처리 가능한 사항은 그 근거를 재사용한다.
- Product location, 지원 화면 환경/대표 집합, 정의된 최종 상태 기록 등 일반 구현 선택은 §4.4에 따라 실행자가 근거를 남기고 진행한다. Supported API 변경·필수 Menu evidence 범위·실제 hook 충돌 등 기존 authority의 별도 판단이 필요한 경우만 해당 경계를 보류한다. 문서상 owner 표현이 있다는 이유만으로 새 승인 대기·seal을 추가하지 않는다.
- Independent review가 요구되는 단계에서는 기존 eligibility를 따른다. 계획 공동 작성 또는 구현 참여 자체를 독립 검토 증거로 사용하지 않는다. 본 계획은 별도 agent 실행을 지시하지 않는다.
- Report의 `validated`, `out_of_scope`, `unvalidated_but_in_scope`는 증거 범위 구분이다. 새 product state enum으로 사용하지 않는다.

---

## 12. Expected Closeout State

기대 목표는 **검증된 T2 static rows의 실제 Alt Tooltip 통합을 필수 증거 범위 안에서 완료하는 것**이다. 최종 state는 `docs/EXECUTION_CONTRACT.md` §7-1과 기존 module authority의 정의를 실제 결과에 적용해 실행자가 기록한다. 명시적인 owner-reserved adoption/상태 변경은 기존 절차를 따르되, label 기록만을 위한 새 승인 절차는 만들지 않는다. 아래 완료 조건과 사전 고정한 L3 범위를 결과에 맞춰 사후 변경하지 않는다.

| 증거 축 | 완료 판단에 필요한 결과 |
| --- | --- |
| Implementation | Static-only Alt graph, exact lookup, atomic 0~4줄, fast path, lifecycle/geometry, legacy disposition |
| Automated validation | 최종 코드의 focused 결과와 실제 삭제·adapter 변경이 있을 때만 선행 최소 subset 결과, 선언한 load timing·정상/fault legacy trap `0`, 유효한 Lua syntax·관련 regression 및 게임 수정 후 final exact subject의 기존 필수 gate 성공 |
| Package | T2 payload가 expected module path로 포함되고 raw-byte identity 유지 |
| Installation | 실제 validation install이 verified package와 동일하며 stale 경쟁 copy 조사 완료 |
| Runtime module | 실제 PZ가 선택한 module locator와 세션 readback이 위 install에 결속 |
| Menu evidence | L2 inheritance 근거, 사전 고정한 L3 필수 집합의 KO record와 EN 별도 lookup/index/chunk를 독립 mapping으로 확인해 각 locale의 coverage 충족, L4 selected identity/source relation 확인 |
| In-game functional | 대표 0~4줄·KO/EN·source kinds·Alt/item/Menu lifecycle 확인 |
| Visual | 실행 전 기록한 PZ build/mod/font/scale/resolution에 관찰을 결속하고 그 환경 안에서 wrapping·spacing·clipping·overlap·화면 경계 확인 |
| Failure isolation | Disposable 실제 failure 조건에서 Iris 미표시와 vanilla/게임 상호작용 유지 |

현재 계획 시점에는 T2 파일 identity를 제외한 T3 실행 증거가 없고 L3 independent Menu evidence도 미해결이다. 따라서 지금 전체 T3 완료를 선언할 수 없다. 실행 후에도 필수 runtime/package/install/Menu/game/visual/failure 축에 미검증 항목이 남으면 최종 보고는 구현 범위·통과한 검증·남은 정확한 gap을 구분하고 전체 완료 claim을 보류한다.

L3 admissible observable 부재, 필수 범위의 사전 결정 부재, 또는 사전 필수 집합의 unresolved/mismatch가 있는 경우에는 다른 축이 모두 성공해도 전체 T3 완료가 아니다. 이때 L3 기존 상태와 source relation 부재/independent observation ceiling을 구분한 exact gap을 유지한다. 관찰 성공분만 필수로 다시 정의하거나 필수 미검증 항목을 사후에 out of scope로 옮겨 완료 조건을 충족시키지 않는다.

허용되는 최대 claim은 검증된 T2 정적 KO/EN 배열이 제품→package→install→실제 PZ Alt 경로에 내용 보존 상태로 연결되고, exact FullType과 지원 locale로 legacy 의미 생산 없이 표시됨을 수행한 자동검증·Menu relation·대표 게임 관찰 범위에서 확인했다는 것이다.

이 결과는 T2 의미 품질 재인증, 2,280-item 전수 수동 확인, 1,314-fact 전수 독립 검증(실제 그 범위를 증명하지 않은 경우), 모든 외부 모드·multiplayer 호환성, RTC/DVF/Publish/release/Workshop/deployment 완료 또는 성능 향상을 의미하지 않는다.

## 실행 기록 — 2026-08-30

사용자 실행 승인에 따라 문서상 owner gate는 승인된 것으로 처리한다. 실행 경계는 현재 repository 및 계획이 요구하는 명시적 외부 입력으로 한정한다. 미지정 외부 output/install/game 경로를 탐색하거나 생성하지 않는다. 실행 기록은 이 절에 합치며 별도 seal/receipt/manifest/census artifact를 만들지 않는다.

### Cutover 이전 결정

- Predecessor: `b9d7ae289b226082c191b1f6a23e6b363c6d99a6`. 기존 `b/`, `g/`, `i/` 변경 및 사용자가 제공한 이 계획은 보존한다.
- Admission: §4.2의 세 파일 SHA/bytes와 current locator, closeout implementation/T1 binding 일치. 원본 Lua를 실제 Lua로 읽어 2,280 exact keys, explicit KO/EN, 모든 row의 순서와 manifest surface SHA, 0~4줄 분포를 확인했다. 입력 재생성은 하지 않았다.
- T1 required input은 current locator의 `C:/Users/MW/Downloads/coding/PZ-t2/t1-final/{subject_binding.json,t2_handoff_input.jsonl,t2_handoff_manifest.json}`이다. 세 SHA는 T2 `t1_input`에 일치한다. S2 present/selected pair 집합은 1,314개, missing/extra/identity mismatch 모두 0. Sorted `[FullType,fact_id]` pairs의 compact ASCII JSON SHA-256은 `c5db8a28892229df25f9b65b22e045515b3ac1fcc0d476bb8a1231131832cd28`이다.
- L3 필수 범위는 위 1,314 exact pairs 전부, KO와 EN 각각으로 고정한다. sample 성공으로 축소하지 않는다. KO 후보 mapping은 current generation `dvf_3_3_rendered.json`의 `role_material.core_source_fact_ids`, observable은 실제 assembler가 호출하는 lookup의 selected chunk entry다. EN은 별도 lookup/index/chunk의 실제 선택을 관찰한다. 기존 영어 producer는 FullType/primary-use로 문자열 payload를 만들지만 현재 EN chunk에는 fact identity나 그 record를 fact에 결속한 immutable mapping이 없다. 단순 문자열 동등성으로 이 gap을 닫지 않는다. KO/EN source 관찰과 independent identity closure를 구분하며 EN mapping gap은 유지한다.
- Hook: `DECISIONS.md`의 2026-08-25 non-interference 결정은 bullet reload/context-menu texture 두 patch retirement다. 기존 `IrisMain`의 Step 5a Alt hook은 보존 범위다. 원본 render는 보호 호출 밖에서 정확히 한 번 실행하고 Iris 작업에만 기존 `ProtectedCall.call`을 사용한다. 이 silent boundary는 반복 오류 로그도 만들지 않는다.
- Load timing: `Iris/Data/IrisTooltipT2Lookup` module 자체는 Alt module과 함께 load 가능하되 payload `Iris/Data/IrisTooltipT2Data`는 최초 valid FullType + explicit ko/en lookup에서 한 번만 require한다. 실패도 한 번만 시도한다. 별도 result cache/chunk/hot reload는 만들지 않는다.

| Consumer 대상 | 현재 caller / 계약 | Disposition |
| --- | --- | --- |
| Summary get/_getCached/reset 및 metrics | Alt, lazy/residual/pre-refactor harness; residual supported manifest의 copy-on-read delta; T1 audit source inventory | Summary 원본 보존, Alt edge만 제거. 삭제/adapter 변경 전 subset은 해당 없음 |
| Alt display cache 및 instrumentation | Browser state / optimization harness | 캐시 제거, 기존 관찰 함수명은 zero-retention metrics/reset 용도로 보존. 기존 cache-hit assertion만 static lookup 관찰로 교체 |
| Detail tooltipFacts 및 Recipe/Moveables/Fixing/UseCase | Detail/API와 fact/lazy harness | 전부 보존, Alt에서는 도달 불가 |
| Shared locale helper | Menu/Browser/Detail/Tooltip | fallback API 보존, 같은 lifecycle에 strict locale accessor만 추가 |
| Package media projection | `Copy-IrisMediaProjection`은 일반 media를 byte-copy하고 Layer3만 별도 projection | 새 T2 Lua 자동 포함 대상, package 구현 변경 불필요. 실제 package 실행과 동일시하지 않음 |

Focused 준비/구현 이후 검증은 마지막 terminal sequence에 모은다. 실제 삭제가 없으므로 선행 replacement subset은 실행하지 않는다. 외부 root를 필수로 요구하는 package/canonical gate 및 실제 install/game은 현재 실행 경계에서 수행하지 않으며 미검증 축으로 유지한다.

### 구현 및 검증 결과

최종 상태는 **`partial`**이다. Code는 위 predecessor 위의 미커밋 working tree이며 commit/push하지 않았다. 구현·standalone 관찰은 완료했지만 필수 Menu/package/install/PZ/canonical 축을 완료하지 않았으므로 전체 T3 completion/adoption은 선언하지 않는다. `tooltip_t2_static_staging.runtime_adopted`는 `false`로 유지한다. 이 기록은 sealed closeout, release/deployment 또는 performance certification이 아니다.

- Product payload: `Iris/media/lua/client/Iris/Data/IrisTooltipT2Data.lua`, 979,485 bytes, §4.2 SHA 그대로. Binary copy와 path-scoped `-text`만 적용했다. Final runtime wrapper도 이 SHA를 확인했다. 실제 clean checkout/package/ZIP/install copy는 아직 검증하지 않았다.
- Reader: `21cb84ceb4e29b392e5b35c8af04ff18c768377398e08bb81fef24be734d762d`.
- Alt renderer: `2443de4d2201ab50dcbb653370537e6518572b1615b390369be8409e80149497`.
- Translation loader: `30a141e4d79c0c643d2a389a0b396933296278f7f9bd22e2ba2fabe42ef69cc2`; resolver: `036363f244a5e81582a39f0aa0234451f535ea8bdb18757b29e697e188a15da3`.
- FullType는 exact lookup, locale는 기존 owner의 strict accessor로 KO/EN만 채택한다. Invalid selected record는 draw 전에 전체 거부하고 다른 locale/key에는 실패를 전파하지 않는다. Module require 실패는 한 번만 시도한다.
- PZ `MeasureStringX`/`getFontHeight`로 UTF-8 경계에서 physical wrapping한다. 문자열 bytes/순서와 동일 문자열의 별도 row를 유지한다. Vanilla 아래 공간이 부족하면 위쪽에 배치하고, 두 위치 모두 전체 block을 담을 수 없으면 생략한다. 이 presentation의 실제 PZ clipping/viewport 적합성은 미검증이다.
- Original render를 Iris 보호 밖에서 한 번 호출한다. 추가 geometry를 다음 frame 전에 복구하고 Iris lookup/measurement/draw 오류는 silent protected call로 격리한다. Mock renderer의 failure isolation은 실제 GPU/게임의 부분 draw 취소를 보증하지 않는다.
- 신규 Lua harness는 하나다. 최초 별도 Python wrapper는 기존 source classification에 등록되지 않아 pytest 수집 전에 거부됐다. 이를 정규 validator로 승격하지 않고 기존 `test_iris_browser_state_selection_search_acceptance.py`의 현재 test identity 안에 통합했다. 신규 Python source, taxonomy/required membership 변경, receipt/manifest/validator 추가는 최종 diff에 없다.

최종 실행 명령은 repository root 기준이다. 아래 PASS는 각각 실제 exit `0`이며, canonical gate PASS를 뜻하지 않는다.

| 실제 명령 | 결과 |
| --- | --- |
| `powershell -ExecutionPolicy Bypass -File .\tools\check_lua_syntax.ps1` | exit 0, runtime 129 files. 기존 default package root는 존재하지 않아 package syntax claim 없음. 마지막 loader whitespace 수정 후 1회 재실행 |
| `uv run python .\Iris\build\description\v2\tests\test_iris_browser_state_selection_search_acceptance.py` | exit 0, 2 tests. 기존 Browser 검증과 최종 T3 full Lua harness 포함; reader/shape/locale/load/Alt/lifecycle/fault/legacy trap 0, actual Menu source 관찰. Offline relation 전체 PASS는 아님 |
| `uv run python .\Iris\build\description\v2\tests\test_iris_session_cache_ownership.py` | exit 0, 3 tests. Historical census 원본 보존, current Alt zero-retention assertion 추가 |
| `uv run python .\Iris\build\description\v2\tests\test_layer3_lazy_lookup_contract.py` | exit 0, 1 test |
| `uv run python .\Iris\build\description\v2\tests\test_usecase_lazy_lookup_contract.py` | exit 0, 1 test |
| `uv run python .\Iris\build\description\v2\tests\test_iris_viewmodel_allocation_contract.py` | exit 0, 2 tests |
| `lua .\Iris\test\lua\residual_refactor_acceptance_harness.lua . Acceptance` | exit 0, 8 rows/failure 0. 최초 실행은 기존 ProtectedCall mock의 `call` 누락으로 exit 1; mock 보완 후 해당 harness만 재실행. Python/PowerShell external receipt wrapper PASS로 승격하지 않음 |
| `lua .\Iris\test\lua\runtime_optimization_metrics_harness.lua . tooltip` | exit 0. OFF 1,000회에 summary load/get·임시 detail table 0; ON 100 lookup, retained entries 0, payload load 1. 성능 개선률 claim 없음 |

실패/차단 이력은 다음과 같다.

- 당시 임시 wrapper 경로 `Iris/build/description/v2/tests/test_iris_tooltip_t3_runtime.py`에 대해 `uv run python <path> full C:/Users/MW/Downloads/coding/PZ2/t2-final/tooltip_t2_projection_manifest.json`은 exit 1이었다. 내부 Lua runtime subprocess는 exit 0이었지만 KO L3 source 12개 누락에서 offline join이 실패했다. 관찰 집계를 보완한 같은 경로의 `menu` 실행도 exit 1이며 아래의 두 locale/L4 결과를 산출했다. Reader/renderer 실패로 잘못 귀속하거나 이 실패를 후속 standalone PASS로 덮지 않는다. 현재 재현 command owner는 ENTRYPOINTS에 등록한 기존 Browser wrapper의 `full`/`menu` + manifest argument다.
- `uv run --project .\Iris\tooling python -B -m pytest`에 T3·Browser·session·Layer3/UseCase lazy·viewmodel 파일을 지정한 첫 실행은 unclassified new test source로 exit 1. 기존 owner에 coverage를 통합한 뒤 Browser/session/Layer3 lazy/UseCase lazy/viewmodel 5개 파일을 `-q -p no:cacheprovider`로 지정한 두 번째 실행도 `current-route output seed must be materialized externally by the canonical runner`로 exit 1이었다. 테스트 수집 이전 실패이므로 pytest test PASS는 0이다. Source policy나 output gate를 변경하지 않았다.
- Receipt-bound canonical Run A/B/comparator는 미실행/BLOCKED다. Current owner는 external seed/environment receipt/work/result/orchestration paths와 exact committed subject를 요구한다. 현재 요청의 execution boundary 아래에서 임의 외부 경로를 탐색/생성하거나 기존 T2 receipt를 T3에 재결속하지 않았다.
- Package command와 disposable install, installed smoke, 실제 PZ loaded module·Alt·Menu 왕복·visual·failure injection은 모두 미실행이다. 외부 경로를 새로 가정하거나 일반 사용자 설치를 조사하지 않았다.
- 모든 실행은 짧은 시간에 종료했고 장기 실행/무한루프 중단은 없었다. 실패 관련 수정/집계 외 confidence 재실행이나 별도 proof artifact는 만들지 않았다.

### Menu evidence와 남은 정확한 gap

L2 inheritance 기준은 T1 subject `60796744ffb889477161d243a1443c9de57d49b0` / tree `1182c6fbffc82f3d6aed3516fa0f1918ee60b248`, support SHA `3a6cc24b9ad64e06a0a6c0408821201e35bbd1d8558e6245809b5d3c34265ce6`이다. 위 bound `subject_binding.json`은 relation SHA `5e78c5616d14727c00585bd3671e9c0313b5490a1e6fc4b93af69b722ef4d7ce`, relation receipt SHA `e2e262b64c52befc1e65960a000284d184d79721b40a422aac29db7e53076278`를 가리킨다. 아래 네 source/consumer의 현재 내용을 그 T1 Git blob과 비교해 newline 정규화 외 diff 0을 확인했다. T3는 이 경로를 변경하지 않으므로 applicable 1,406/silence 874 관계를 상속한다. 신규 D2 실행 claim은 아니다.

| Source/consumer (`Iris/media/lua/client/` 기준) | 현재 raw SHA-256 |
| --- | --- |
| `Iris/Data/IrisClassifications.lua` | `98d9ce3162703333b02dd48d62f8739e4606eada321a7731a35e2e586f033563` |
| `Iris/API/StaticData.lua` | `ddfbd443edc04e9e7b90ef2bd89020bdf4a24159e895ce6088319a4925125d62` |
| `Iris/UI/Browser/IrisBrowserProjectionBuilder.lua` | `742931c4fc86349ac15e81d26a9faa3add819ea6d78fcfcb39387f0ae1a4b233` |
| `Iris/UI/Browser/IrisBrowserCategoryIndex.lua` | `1f347ac2febb02fe4b3e98f69fb8cdc7327d920cbdbe9efced9ff7ed75a2c6a4` |

L3는 실제 assembler→KO lookup selected entry와 EN lookup→Index→chunk record read를 dev/test 경계에서 관찰했다. Tooltip identity를 production Menu에 주입하지 않았다. Required selected 1,314개 중 **KO/EN 각각 1,302개 source 관찰, 12개 누락**이다. KO 관찰 1,302개는 실제 반환 entry의 chunk table identity와 current generation의 기존 `core_source_fact_ids` mapping을 연결해 일치했다. 이는 KO 1,314개 전체 closure가 아니다. EN은 1,302 source 관찰과 별개로 immutable per-record independent fact mapping이 없으므로 **1,314개 전체 identity 증거 gap**을 유지한다.

양 locale의 source 누락 exact set:

`Base.BarbedWire`, `Base.CarBatteryCharger`, `Base.Hinge`, `Base.Jack`, `Base.LeatherStrips`, `Base.LugWrench`, `Base.Paintbrush`, `Base.Pipe`, `Base.Scotchtape`, `Base.ScrapMetal`, `Base.TirePump`, `Base.Toolbox`.

누락 대표 `Base.BarbedWire`/`Base.Toolbox`의 actual pointer-selected Lua entry는 `source=layer3_role_realign_silent_v1`, `text_ko=nil`이다. Renderer는 KO public text 조건이 없는 entry에서 EN lookup도 진행하지 않는다. 이를 Tooltip reader 결함으로 보정하거나 owner source/선택된 T2 배열을 수정하지 않았다. Source 부재 12개와 EN independent observation ceiling은 별개 gap이다.

L4는 actual ViewModel의 `interactionState`→Collector→Projection을 양 locale에서 사용했다. Selected S3/S4 **530 identity/source rows씩 모두 actual structured set의 subset**, missing 0이며 Recipe-only/Right-click-only/both coverage를 확인했다. Menu의 더 자세한 문장과 Tooltip 문자열 동등성은 요구하지 않았다.

Validation ceiling: standalone Lua의 실제 product 함수와 bounded mock engine/renderer, offline admitted inputs 및 source inheritance까지다. Engine-bound PZ 객체, 실제 font renderer, 설치/로드 경쟁, 모든 mod/화면 조합 또는 2,280-item 수동 전수 증거는 아니다. 위 12개와 EN mapping gap은 필수 미완료 범위로 유지하며 사후 out-of-scope로 이동하지 않는다.

### 한정 후속 — EN 판정 보완 및 L3 원인 확인

지정 보고 작업 `01a026db-1b3f-7001-9a68-08700f242f40`의 후속 지시에 따라 repository 안에서만 판정 결함과 원인을 확인했다. Runtime/Lua, upstream data/producer, T2 row/selection, current route는 변경하지 않았다. 외부 입력 재접근, package/install/PZ, generation, commit/push와 새로운 증거 artifact 생성은 하지 않는다.

**EN 판정 결함:** 이전 `menu_relations()`는 EN independent mapping 미해결을 출력만 하고 실패 목록에는 넣지 않았다. 당시 source 누락 12개 때문에 command exit 1이었지만, source gap만 없어지면 잘못 exit 0이 될 수 있었다. 이제 기존에 독립적으로 확립된 `(observed module, core fact)` relation을 test-local 명시적 입력으로 비교한다. 입력 부재는 required EN identity unverified, 관찰된 module 또는 selected fact와 불일치는 identity mismatch로 실패에 포함한다. Source missing도 기존대로 실패다. 현재 caller는 독립 연결을 아직 확립하지 못한 결과인 빈 evidence를 명시적으로 전달한다. 영구 실패 상수나 per-record authority를 발급하지 않으며, 실제로 충분한 기존 evidence가 공급되면 비교가 성공할 수 있다. Standalone runtime PASS, Menu source observation 완료, 전체 Menu relation 판정을 출력에서도 구분한다.

기존 `test_browserdata_compatibility_and_logging_source_guards` 안에 같은 1,314개 selected identities의 공통 in-memory fixture를 추가했다. 모든 KO/EN source, KO identity와 L4 subset 비교가 성공하도록 고정한 뒤 EN evidence 없음/identity 불일치/충분한 evidence의 세 입력만 바꾼다. 앞의 두 경우 실패, 마지막 경우 성공을 요구해 다른 source 실패가 EN 결함을 가리는 것을 막는다. Fixture는 테스트 판정의 회귀 사례일 뿐 실제 Menu evidence가 아니며 파일을 생성하지 않는다. 새 test file/function/framework나 canonical membership은 추가하지 않았다.

**12개 원인:** 위 exact 12개 전부에 대해 existing facts, approved `candidate_rendered.json`, pointer-selected `dvf_3_3_rendered.json`, Tooltip owner row와 EN chunk source를 읽었다. 12개 모두 다음 조건이었다.

- Approved projection과 runtime record는 `source=layer3_role_realign_silent_v1`, `text_ko` 없음이다.
- 각 record에 core fact ID 1개와 facts의 nonempty `primary_use`가 남아 있고, 그 ID는 기존 Tooltip owner의 fact ID와 같다.
- `build_english_entries()`는 `text_ko`가 없으면 skip하므로 EN chunk에도 해당 exact record가 없다.
- `build_tooltip_t1_owner_entries()`는 `text_ko`를 표시 조건으로 검사하지 않고 단일 `core_source_fact_ids`와 `primary_use`를 기준으로 S2 fact를 발행한다.

따라서 12개는 이 두 producer 분기의 조건 차이에 모두 해당한다. 단순한 관측 실패가 아니라 **기존 Menu의 명시적 silence projection과 Tooltip S2 생산의 차이**다. 이 결과가 정당한 N/A인지, upstream 어느 조건을 바꿀지는 이번 범위에서 판단하지 않았다. 12개를 required 집합에서 제외하거나 T2 줄을 숨기지 않았다.

**EN 독립 연결의 정확한 한계:** 이전의 “chunk에 fact ID가 없으므로 mapping이 없다”는 설명만으로는 충분하지 않다. 계획상 허용된 immutable module/record→producer/input/generation 경로도 확인했다. 현재 `_current_projection()`은 pointer-selected generation descriptor의 facts/projection input identity를 확인한다. 실제 두 input의 raw SHA도 descriptor와 일치한다: facts `e784cf76d2f7d51273eda44906c202c0548f0043027f60cf1af817336c03a6e9`, approved projection `fe6d24a1cac362076db6c3ce895df02eb1ec407bab080aee437df88fc153b5c6`.

그러나 확인한 current generation descriptor의 14개 outputs는 rendered JSON/KO runtime index/pointer/chunks이고 `Layer3English/Index.lua`와 EN chunks를 포함하지 않는다. Descriptor의 generator implementation binding에도 영어 producer가 없다. 영어 `_write_runtime()`은 `first/last/module` range index와 문자열 chunks를 쓰며, 그 출력 bytes/record를 해당 producer version·facts/projection input identity에 결속한 relation은 이 현재 경로에서 제공하지 않는다. 즉 확인된 관계는 **producer의 입력→current generation 검사**까지이며, 실제 관찰한 **EN output module/record→그 immutable producer/input execution** 연결이 아직 확립되지 않았다. 단순 FullType, 같은 문자열, 공유 Git/generation 또는 Tooltip owner 출력으로 이 끊긴 연결을 채우지 않았다. 이는 가능한 모든 기존 증거의 부재를 전역적으로 증명한 claim이 아니라, 이번에 허용된 current producer/descriptor/source 범위에서 독립 연결을 확보하지 못했다는 제한이다. 새로운 mapping을 발급하거나 producer를 재실행하지 않고 여기서 멈춘다.

남은 blocker는 (1) 12개 Menu silence/S2 생산 차이에 대한 기존 owner의 별도 범위 판단, (2) EN output-record와 independent immutable producer/input 관계의 admissible existing evidence 확보, (3) 앞서 기록한 package/install/PZ/canonical 실행 경계다. `partial`, `runtime_adopted=false`와 기존 실패 이력은 그대로 유지한다.

후속의 유일한 테스트 실행: `uv run python .\Iris\build\description\v2\tests\test_iris_browser_state_selection_search_acceptance.py BrowserStateSelectionSearchAcceptanceTest.test_browserdata_compatibility_and_logging_source_guards` → **exit 0, 1 test, 0.051s**. 기존 source guard와 위 in-memory EN 판정 회귀를 확인했다. Lua/runtime suite, 실제 Menu 관찰/외부 manifest join, 전체 pytest/canonical gate, T1/T2 producer는 재실행하지 않았다. 이 PASS는 실제 EN evidence 확보나 전체 Menu relation 성공을 뜻하지 않는다.

### T3-D1 실행 인계 — 2026-08-30 / 진행 중

`docs/iris_tooltip_t3_d1_layer3_menu_tooltip_display_en_record_fact_relation_consistency_plan.md`의 실행 기록을 additive successor readpoint로 사용한다. 초기 selected 1,314 pair와 위 실패 기록은 유지한다. 현재까지 final S2 selected / Menu KO required / Menu EN required는 모두 initial 1,314 그대로이며, authority-backed non-required scope는 아직 공집합이다. 관측 성공한 1,302개로 acceptance를 줄이지 않는다.

D1 첫 검증 구간에서는 기존 focused fixture exit 0, 지정 Lua syntax exit 0(129 files), explicit current T2 manifest를 사용한 `menu` relation exit 1이었다. Actual KO/EN은 각각 selected 1,302개이며 같은 12개가 `no_public_body`; KO fact/text 1,302개는 current generation과 일치했지만 EN independent producer evidence는 미실행이다. Inherited partition은 resolved/retained 공집합, unresolved는 initial exact set 전체다. 상세 command·source hash·exact 12개·authority 근거는 D1 실행 기록에 한 번 기록했다.

기존 tuple-only EN 입력은 current producer/input/output/generation에 결속된 reconstruction 입력으로 보완했으며 CLI는 `--en-replay-root`를 받을 수 있다. 이 경로는 historical provenance를 발급하지 않고 current deterministic derivability만 주장할 수 있다. 아직 실행되지 않은 reconstruction이나 synthetic fixture를 actual evidence로 승격하지 않는다.

이후 사용자가 D1 §4.5의 `C:/Users/MW/Downloads/coding/PZ2/t3d1` 한정 외부 작업 예외를 승인해 같은 D1을 재개했다. 기존 외부 입력은 read-only이며 다른 외부 경로로 확대하지 않는다. Item 전체 review hold와 approved core의 공개 관계에 대한 한정 C 제안을 원 세션에 전달했고, 해당 판단 전에는 새로운 P1 branch를 채택하지 않았다. Final disposition/actual EN relation 및 필수 gate를 마친 후 이 acceptance의 final-required scope를 다시 동기화해야 한다. 현재는 D1 complete/handoff-ready가 아니며, 새 T3-D2나 별도 로드맵으로 넘기지 않는다.

T1/T2 final locator와 Menu generation은 아직 기존 값을 사용한다. `runtime_adopted=false`와 전체 T3 `partial`을 유지한다. Sealed T1 unverified 기록의 자동 갱신은 없으며 package/install/actual loaded module/PZ/Alt/visual/failure-isolation은 original T3에서 여전히 in-scope 미검증이다.
