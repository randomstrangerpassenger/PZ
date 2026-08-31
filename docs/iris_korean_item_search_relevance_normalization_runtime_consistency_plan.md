# Iris 한국어 아이템 검색 관련성·입력 정규화·런타임 상태 정합성 Implementation Plan

> 상태: implemented_only — source 구현 및 focused acceptance/Lua syntax 완료; full gate·package·실제 PZ 검증은 실행 경계상 미완료
>
> 작성일: 2026-08-31
>
> 대상: Iris 메뉴의 전체 아이템 검색과 목록 내 아이템 검색
>
> 기준: 사용자 제공 「Iris 한국어 아이템 검색 관련성·입력 정규화·런타임 상태 정합성 개선 Roadmap — 종합안」
>
> 양식: `docs/PLAN_TEMPLATE.md`의 12개 항목
>
> 조사 기준 HEAD: `f8da88748b09c67f0adb89daa6b28f543500bc48`
>
> 구현 검증 깊이: heavy — runtime / compatibility / determinism / regression / public-facing behavior
>
> 검토 반영: 4.1·4.2 및 N1~N6 — corpus/locale 분모, decision authority, 증상 추적, local tie-break, 사용성/성능 구분, script 경로 확인

> 사용자 후속 요청 반영: 최소 검색 개선 범위 확정, 범위 내 구현 판단 위임, 검색 품질 수용 기준 보강, 테스트·Gate 최소화. 변경 대상은 이 계획 문서뿐이며 구현·검증 착수를 뜻하지 않는다.

이 문서는 로드맵을 현재 코드에 연결한 실행 계획이다. 최초 작성은 계획 문서만 변경했으며, 2026-08-31 사용자 실행 요청으로 source 구현과 계획 내 focused 검증을 수행했다. 결과·실패 이력·미검증 범위는 `docs/iris_korean_item_search_relevance_normalization_runtime_consistency_closeout.md` 한 곳에 기록한다. full gate·package·실제 PZ 관찰을 완료한 것으로 주장하지 않는다. Change 2에서 필수 결과와 구현 담당자의 재량 범위를 구분했다. 이전 미판정 목록 전체에 대한 별도 승인이나 단계별 Gate는 요구하지 않으며, 상위 authority 변경·필수 목표 축소·범위 밖 변경은 이 위임에 포함하지 않는다.

---

## 1. Objective

현재 locale의 이름을 알고 있는 사용자가 Iris Browser에 실제 존재하는 exact item에 도달하도록 lexical 검색 계약을 정하고, 전체 검색과 목록 내 검색에 일관되게 적용한다.

1. 현재 표시 이름의 정확 일치를 그 문자열을 포함할 뿐인 표시 이름보다 먼저 표시한다.
2. 일반 공백의 앞뒤 삽입, 연속 삽입, 한국어 표시 이름 내부의 띄어쓰기 유무 때문에 같은 항목을 찾지 못하는 문제를 반드시 해소한다. 최소 대상은 U+0020이며 구체적인 구현은 열어 둔다. `망치`, `  망치  ` 및 `대형 망치`, `대형  망치`, `대형망치`에서 각각 같은 target에 도달해야 한다. 공백만 있는 입력은 빈 검색과 같은 UI 상태로 돌아간다.
3. 현재 전체 검색의 internal-ID 검색을 유지한다. 코드에서 이 필드는 별도 ID가 아니라 `fullType` 문자열이다.
4. 검색 의미의 구현 owner를 하나로 만들고, surface의 차이는 candidate 범위와 명시한 field scope로 제한한다.
5. 검색 문서·후보·결과를 현재 Browser generation, normalized locale, snapshot 및 query에 귀속시킨다.
6. incremental 결과의 exact identity와 관련성 순서가 같은 조건의 fresh search와 일치하도록 한다.
7. 동일 DisplayName을 가진 서로 다른 FullType과 기존 variant 관계를 보존한다.
8. 실제 PZ에서 한국어 입력·삭제·붙여넣기·clear 및 관련 상태 전환을 관찰한 범위로 완료 주장을 제한한다.
9. 정확한 이름과 필수 공백 변형뿐 아니라 대표 부분 검색과 관련 없는 결과도 함께 평가한다. 필수 증상을 남긴 채 optional로 재분류하여 완료하지 않는다.

검색 관련성은 입력 문자열과 searchable text의 관계다. 아이템의 효율·유용성·인기도·semantic quality를 평가하거나 Classification / DVF / QG의 사실을 변경하지 않는다.

---

## 2. Scope

### 2.1 실행 범위

- `ISTextEntryBox`에서 Iris callback으로 들어온 raw query부터 결과 목록·선택까지의 Browser 검색 경로.
- active `getAllItems()` index에서 유래한 current display name / exact FullType의 검색용 표현.
- 초기 snapshot 생성과 locale 교체 시 동일하게 적용할 search-document 생성.
- 공통 normalization / matching / relation / relevance ordering과 두 surface의 adapter.
- 검색창 clear, append, backspace, paste, surface 전환 및 locale / generation 무효화.
- 기존 Browser acceptance, snapshot / identity / copy-on-read 검사에 필요한 사례 보강.
- 후보 package 생성, 실제 PZ 관찰, 검색 외 surface 비변경 확인 및 단일 closeout.

### 2.2 코드에서 확인한 현재 경로

아래 Browser 파일의 공통 경로는 `Iris/media/lua/client/Iris/UI/Browser/`다. 함수명은 조사 시점 locator이며 실행 시 변경 여부를 다시 확인한다.

| 영역 | 현재 코드와 실제 동작 | 계획에 반영할 사항 |
|---|---|---|
| 입력 연결 | `IrisBrowserLayout.lua`의 `searchBar.onTextChange` / `itemSearchBar.onTextChange`가 ListController를 호출한다. | Iris로 전달된 문자열과 IME 내부 상태를 동일시하지 않는다. |
| 전체 검색 | `IrisBrowserListController.onGlobalSearchChange → IrisBrowserData.searchAll → IrisBrowserQuery.searchAll`. | 기존 `searchAll(query)` 호출과 반환 row 계약을 보존한다. |
| 전체 matcher | `IrisBrowserQuery`가 `displayName:lower() .. "\0" .. fullType:lower()`인 `folded`에 literal `find(..., 1, true)`를 적용한다. | display / ID를 분리해 relation을 판정한다. 정규화된 문자열을 identity로 사용하지 않는다. |
| 전체 순서 | ProjectionBuilder와 Query의 `searchRowLess`: `displayName`, 이어 exact `fullType`. 검색은 정렬된 source를 필터링한다. | 현재 exact-name 우선 보장은 없다. query별 relevance와 snapshot 기본 정렬을 구분한다. |
| 목록 내 검색 | `loadItems`가 `BrowserData.getItems`의 결과를 `displayName:lower():find(...)`로 다시 필터링한다. | 전체와 별도 matcher다. 공통 core에 연결하되 local field scope를 명시한다. |
| local source의 성격 | `IrisBrowserVariantIndex.getItems`는 같은 DisplayName의 item type / Recipe 연결 유무가 같으면 접고 `variants`에 exact FullType을 보존한다. 기본 순서는 `isPrimary → displayName → fullType`. | local은 raw 전체 row 목록이 아니다. grouping과 검색을 분리하고 검색 중 `isPrimary`가 lexical tier를 앞서지 않게 한다. |
| 활성 아이템 | `IrisBrowserItemIndex.build`가 `getAllItems()`를 exact FullType map으로 만든다. `IrisItemAccess.getDisplayName`은 item의 `getDisplayName()`을 읽고 값이 없으면 FullType을 사용한다. | 저장소 번역 파일을 production 검색 corpus로 대체하지 않는다. 미분류 아이템도 global 검색 대상일 수 있다. |
| 초기 snapshot | `IrisBrowserProjectionBuilder.build`가 private row, `folded`, 정렬된 `searchSnapshot`을 함께 만든다. | 초기 생성과 locale 갱신의 중복 정규화가 다시 갈라지지 않게 한다. |
| lifecycle | `IrisBrowserLifecycle`은 build 성공 시 Browser generation을 증가시키고 `resetForReload`에서 cache를 버린다. | 이 정수 generation은 DVF의 `dvf33-*` semantic generation ID와 다르다. 검색 변경에 DVF 재발행은 필요하지 않다. |
| locale snapshot | `Query.ensureLocale`가 generation / locale 불일치 시 이름을 다시 읽고 정렬한 뒤 row map과 snapshot을 publish한다. prefix state, display-name group, folded-count cache도 폐기한다. | 기존 atomic publish와 관련 cache 무효화를 search document까지 확장한다. |
| locale 전달 | `BrowserData`는 `TranslationResolver.getLangKey("EN")`을 호출한다. `IrisTranslationLoader`는 감지한 uppercase 언어 키를 캐시하며 `init()`에서 갱신한다. | Query는 locale을 독자적으로 정규화하지 않는다. 실제 언어 전환이 loader 갱신으로 연결되는지는 별도 관찰한다. |
| prefix 최적화 | 같은 generation / locale이고 소문자 query가 이전 문자열의 더 긴 prefix 연장일 때만 이전 결과를 재검색한다. | 새 입력 family의 monotonicity와 query별 재순위 조건을 다시 검증한다. |
| global clear | `onGlobalSearchChange`는 `query == ""`이면 `loadCategories()`만 호출하고 return한다. Query의 empty-query prefix 초기화는 호출되지 않으며 기존 item / subcategory / detail을 이 분기에서 정리하지 않는다. | API 단위 clear 검사만으로 UI clear를 검증할 수 없다. controller 전환 사례가 필요하다. |
| supported surface | `phase0_supported_api_manifest.json` 두 readpoint에는 `BrowserData.build`, `getGroupVariants`, `Browser.openSearch`, `openForItem`이 있다. `searchAll` / `getItems`는 listed entry가 아니다. | 검색 함수를 새 supported API로 승격하지 않는다. 현재 consumer의 signature, row shape와 복사 격리는 여전히 보존한다. |

### Explicitly Out Of Scope

- 소분류 검색창 `subcategorySearchBar`와 Layer 4 interaction 검색의 의미 변경.
- Iris 메뉴 전체 레이아웃, Detail / Wiki / Alt Tooltip 표시 정책 재설계.
- Classification membership / primary, semantic fact, Layer 3 body, Layer 4 use case, Tooltip T1/T2 데이터의 수정·재발행.
- 다른 Pulse spoke의 기능, Java / Mixin 검색 component, 게임 전역 입력 함수 교체.
- 사용자 설치 폴더·save의 임의 수정, Workshop 게시, release / RTC / Publish 승인.
- 기존 사용자 변경인 `docs/PROBLEM_TEMPLATE.md`, `docs/iris_menu_display_interaction_stability_problem.md`의 수정·편입.

---

## 3. Non-Goals

- 모든 한국어 표현·오타·초성·어순·영문 별칭을 이해하는 검색.
- semantic embedding, 인터넷 / 외부 Wiki 연동, 추천·인기·이용 이력 기반 순위.
- 번역 전체 교정, normalized name을 기준으로 한 FullType 병합.
- 범용 검색 framework, 별도 영속 search database, 새 regular search-validation authority.
- 모든 외부 모드·번역팩·IME·PZ 버전의 호환성 인증.
- 측정 없는 속도 개선 주장이나 검색 개선을 Iris 전체 release readiness로 확대하는 것.

초성·단어 순서·영문 별칭 등의 추가 지원은 필수 결과가 아니다. 구현 담당자가 Change 2의 위임 범위와 품질 기준 안에서 채택하거나 보류할 수 있다. 모든 후보의 비교·구현·승인 기록을 요구하지 않는다. Typo / edit-distance와 새 안내 UI, local ID 검색 확대, 별도 formal search authority는 이번 최소 실행에서 보류하며 그 검토 자체를 선행 Gate로 만들지 않는다.

---

## 4. Assumptions

### 4.1 권한·구현 전제

- `docs/Philosophy.md`가 최상위 설계 원칙이다. `docs/DECISIONS.md`의 Browser/API, cache ownership, regular validation, clean-checkout 및 evidence-integrity 경계를 따른다.
- 현재 PZ runtime은 Lua로 유지한다. 기존 PZ item / UI API를 읽는 것과 새 JVM component를 도입하는 것은 구분한다.
- public row는 내부 mutable state와 격리한다. SearchDocument / QueryView / MatchRelation은 내부 구현 표현이며 새로운 사용자 정보 계층이 아니다.
- baseline 지원 대상은 저장소의 current Build 41 맥락으로 출발하되 실제 시험한 PZ build 번호, OS, locale, 활성 모드·번역 환경을 Change 1/6에서 기록한다. Build 42 지원을 추정하지 않는다.
- 같은 locale에서 item 이름·활성 데이터가 바뀌는 경우 기존 reload/rebuild로 새 Browser snapshot을 만들 수 있어야 한다. 지원되지 않는 hot reload를 이번 계획으로 보장하지 않는다.

### 4.2 corpus 수치와 증거 한계

이번 작성에서 `lua/shared/Translate/KO/ItemName_KO.txt`의 `ItemName_<key> = "<name>"` 항목을 read-only로 집계했다. exact key 비교는 case-sensitive ordinal로 수행했다.

| 모집단 | 조사 결과 / 로드맵 값 | 해석 |
|---|---:|---|
| KO 번역 파일 항목 줄 | 2,017 | 이번 정적 집계와 로드맵 corpus 표기가 일치한다. 고유 item 수는 아니다. |
| 위 파일의 distinct exact FullType | 2,007 | 10개 key가 각각 두 번 나온다. 이번 검사에서 같은 key의 중복 값은 동일했다. |
| 항목 줄 기준 distinct DisplayName / 동명 그룹 | 1,661 / 191 | 191은 중복 key 줄도 포함한 집계다. 서로 다른 FullType만의 동명 그룹 수로 쓰지 않는다. |
| 실제 Browser snapshot의 exact item 수 | 미측정 | active `getAllItems`와 build 결과에서 별도로 산출한다. |
| Tooltip T1 support / DVF exact / KO·EN public body | 2,280 / 2,105 / 각 2,099 | 다른 제품 모집단이다. 검색 검증의 분모로 대체하지 않는다. |

KO 파일 SHA-256: `0ea2f9f5747a5845347ccdbb02e48948f3b3b6218d971800dd8d77afe4f2c5de`.

이 집계는 번역 항목 텍스트의 관찰이며 PZ translation parser의 실행 결과가 아니다. 기존 2,017 corpus harness가 중복 key를 어떻게 처리했는지는 아직 확인하지 않았다. Change 1에서 원 관찰 입력과 집계 방식을 결속하며 기존 증거를 임의로 2,007 사례의 PASS로 고치지 않는다.

현재 파일에는 `Base.Hammer = 망치`, `Base.Sledgehammer` / `Base.Sledgehammer2 = 대형 망치`, `Base.ClubHammer = 클럽 해머`가 있다. 따라서 KO에서 `Hammer`가 검색되는 것은 ID 일치일 수 있다. `Club Hammer`의 EN 표시 이름 검색 성공과 혼동하지 않는다.

### 4.3 아직 관찰하지 않은 것

실제 설치 package와 분석 source의 일치, Kahlua에서의 문자열 동작, IME composing 전달, locale 전환 callback, 활성 모드의 표시 이름, before/after latency는 이번 문서 작성에서 검증하지 않았다. standalone fixture의 locale 인자 변경만으로 실제 loader·UI 전환을 입증하지 않는다.

---

## 5. Repository Areas Affected

### Code

| 경로 | 예정 역할 |
|---|---|
| `Iris/media/lua/client/Iris/UI/Browser/IrisBrowserSearch.lua` **신규 예정** | 순수 Lua 검색 core. document/query 파생, matching relation, lexical tier 및 공통 tie-break. generation이나 UI lifecycle의 별도 owner는 만들지 않는다. |
| `Iris/media/lua/client/Iris/UI/Browser/IrisBrowserQuery.lua` | snapshot locale 갱신, 검색 실행, private prefix state, public result projection의 연결. |
| `Iris/media/lua/client/Iris/UI/Browser/IrisBrowserProjectionBuilder.lua` | 초기 snapshot에도 동일 document 생성 경로를 사용. classification 로직은 보존. |
| `Iris/media/lua/client/Iris/UI/Browser/IrisBrowserData.lua` | 기존 facade 유지, 필요한 범위의 내부 scoped search adapter 연결. 새 supported public contract로 자동 승격하지 않음. |
| `Iris/media/lua/client/Iris/UI/Browser/IrisBrowserListController.lua` | local 중복 matcher 제거, global/local 입력과 clear·선택·surface 전환 정합성. |
| `Iris/media/lua/client/Iris/UI/Browser/IrisBrowserVariantIndex.lua` | 우선 read-only 회귀 대상. local group을 검색 core에 연결하는 데 꼭 필요한 내부 adapter만 조건부 수정. grouping 기준·대표 identity 유지. |
| `Iris/media/lua/client/Iris/UI/Browser/IrisBrowserLifecycle.lua` | 우선 기존 owner 재사용. reload / invalidation 연결이 부족한 것으로 확인될 때만 제한 수정. |
| `Iris/media/lua/client/Iris/UI/Browser/IrisBrowserLayout.lua`, `IrisBrowser.lua` | 기존 callback/open 흐름 확인. UI refresh가 필요한 경우에만 제한 수정. |
| `Iris/media/lua/client/Iris/Util/IrisTranslationResolver.lua`, `Iris/media/lua/client/Iris/IrisTranslationLoader.lua` | locale lifecycle 조사. shared owner 수정이 필요하면 검색 외 consumer 영향을 먼저 판정하고 변경 범위를 추가 기록. |
| `Iris/test/lua/browser_state_acceptance_harness.lua` | 실제 production Query / Data / controller의 normalization, 순위, owner 교체, clear 및 reference 동등성 사례 보강. |
| `Iris/build/description/v2/tests/test_iris_browser_state_selection_search_acceptance.py` | 기존 Browser/Lua·facade acceptance 연결과 assertion 유지·보강. |
| `Iris/build/description/v2/tests/test_iris_browser_single_pass_cache_contract.py` | snapshot 단일 파생과 public 격리, locale owner 검사. 기존 소스 형태 assertion과 새 relevance 구현의 관계 검토. |
| `Iris/test/lua/runtime_optimization_metrics_harness.lua` | 필요한 경우 기존 search 계측 활용. 과거 cache shape fixture를 실제 production 경로의 증거로 혼동하지 않음. |

`IrisBrowserItemIndex.lua`, `IrisItemAccess.lua`, `IrisBrowserCategoryIndex.lua`, `IrisBrowserClassificationIndex.lua`는 기본적으로 조사·회귀 확인 대상이며 검색을 이유로 재설계하지 않는다.

### Docs

- 이 계획과 실행 후 단일 `docs/iris_korean_item_search_relevance_normalization_runtime_consistency_closeout.md` **신규 예정**. baseline·채택 동작·품질 사례·결과는 이 기록의 표로 합칠 수 있으며 단계별 보고서, 별도 decision receipt나 finalizer를 만들지 않는다.
- `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`: 실제 채택한 contract / 내부 owner / 제품 상태를 남길 필요가 있을 때만 좁게 갱신한다. 이번 계획 작성으로 current 구현 상태를 바꾸지 않는다.
- 이 계획의 Automated Validation 절: 실제 채택할 focused 실행 명령을 기록한다. 별도 명령 안내 문서나 runner를 만들지 않는다.

### Config

- 기본 변경 없음. 사용자 설정·새 feature flag·전역 locale 설정을 추가하지 않는다.
- `Iris/validation/execution/required_validations.json`, `current_environment.json`과 current source closure는 읽고 적용성을 확인한다. 필요 시 기존 contract의 dependency binding만 정당한 successor 절차로 갱신한다. 테스트 개수나 membership을 보존·확대하는 것이 목표는 아니다.

### Generated Artifacts

- runtime search document는 메모리 파생 데이터다. 저장소의 semantic generated artifact가 아니다.
- 실행 시 baseline/result 표, source/package binding, 실제 PZ 관찰 자료와 candidate/current package는 명시한 repository-external 실행 루트에 둔다. 기존 출력이나 installed package를 덮어쓰지 않는다.
- `IrisLayer3DataCurrent.lua`, `IrisLayer3Generations/**`, Layer3English, `IrisClassifications.lua`, UseCaseDescriptions, Tooltip fixed/Recipe variant payload는 그대로 보존한다. 검색 개선을 위해 T1/T2 또는 DVF producer를 재실행하지 않는다.

---

## 6. Planned Changes

Change 번호는 책임과 근거를 찾기 위한 구분이며 7개의 독립 Gate나 승인 단계를 뜻하지 않는다. baseline과 품질 기대값은 candidate 결과를 보기 전에 정하고, 문서 생성·매칭·UI 연결은 함께 구현할 수 있다. 최종 완료에는 동일 구현을 대상으로 한 검증과 실제 PZ 관찰이 필요하다. 이 의존성을 지키는 한 작업 묶음·순서·focused 검사 시점은 구현 담당자가 정한다. 각 Change의 Validation과 결과는 제7절의 통합 검증·단일 closeout에 포함하며 별도 suite나 sign-off를 추가하지 않는다.

### Change 1 — Current search baseline 및 결함 경계 확정

**Purpose:** source·corpus·입력 전달·API 범위와 실제 결함을 구현 전에 분리한다.

**Files:** Query, Data, ProjectionBuilder, Lifecycle, ListController, VariantIndex, TranslationLoader/Resolver, 기존 Browser harness; read-only KO/EN ItemName 파일과 supported API manifest.

**Implementation Notes:**

1. HEAD / 변경 파일 상태와 실제 시험할 package의 source identity를 기록한다. 기존 dirty 문서 변경은 이 구현 subject와 분리한다.
2. global / local 별 candidate source, searchable field, 기본 순서, grouping, empty-query 동작을 표로 고정한다. `getItems`의 visible row 수와 `variants`를 펼친 exact identity 수를 구분한다.
3. 번역 파일 corpus, 중복 key 처리 후 corpus, 실제 Browser snapshot을 서로 다른 입력으로 기록한다. Change 4의 필수 sweep 입력은 KO·EN 각각의 중복 exact FullType key 처리 후 번역 corpus로 고정한다. locale별 source hash, 중복 key 처리 규칙, exact FullType 수와 unique DisplayName 수를 candidate 평가 전에 기록하고 두 locale을 합치거나 교집합으로 축소하지 않는다. `itemIndex.itemCount`는 삽입 시 증가하므로 실제 snapshot의 exact map cardinality도 별도로 센다.
4. 기존 관찰 입력 `망치`, `대형 망치`, `대형망치`, `망치 대형`, `ㅁㅊ`, `  망치  `, `Hammer`, `Club Hammer`와 필수 연속 공백·공백만 입력을 동일 source/locale에서 한 묶음으로 관찰한다. 없는 target을 이름으로 추정해 만들어 넣지 않는다. Change 2의 품질 기대값을 같은 사례에 결속하여 별도 baseline suite를 만들지 않는다.
5. 표에는 observation ID, raw query, locale, field/surface, corpus identity, target FullType set, target presence·rank, 결과 수·상위 그룹과 실제 display name을 기록한다. source와 fixture에 존재하는 target에 대해서만 retrieval을 평가한다. 관찰된 각 실패 입력은 이 ID로 Change 2의 family/disposition 및 closeout의 해소 여부와 연결한다.
6. 가능하면 실제 PZ에서 callback이 받는 문자열을 bounded debug 관찰한다. 저장소 `lua/client/ISUI/ISTextEntryBox.lua`는 `UITextBox2`에 위임하므로 Lua source만으로 IME composing 상태를 단정하지 않는다.
7. 발견 사항은 matching / input delivery / corpus·naming / unresolved로 분류한다. 미채택 입력이 안 되는 것을 모두 bug라고 부르지 않는다.

**Validation:** 기존 harness로 baseline을 확보하고 최종 비교의 입력으로 재사용한다. 초기 미구축, empty/unusable `getAllItems`, retryable failure / recovery의 기존 사례는 유지하며 별도 baseline 반복 Gate를 추가하지 않는다. 현재 item index의 빈 engine collection은 정상 empty-ready가 아니라 retryable failure라는 상태 계약을 유지한다.

**기록할 결과:** baseline 입력·target·품질 기대값, KO·EN별 corpus 분모/중복 처리, source와 검색 범위·관찰 한계를 단일 실행 기록에 남긴다. 기존 원본 관찰과 새 관찰의 subject는 구분하되 owner/source/API별 별도 보고서는 만들지 않는다.

---

### Change 2 — 필수 검색 동작과 제한된 구현 재량

**Purpose:** 체감 개선의 최소 범위를 확정하고, 통상적인 구현 선택 때문에 사용자 결정을 반복해서 기다리지 않게 한다.

**Files:** 이 계획의 아래 기준과 기존 Browser harness의 사례. 실제 지원 범위와 판단 이유는 단일 closeout에 합쳐 기록한다. 별도 search contract schema·승인 문서·Gate는 만들지 않는다.

**확정 결과와 위임 범위:** 이번 사용자 요청은 아래 필수 결과의 반영과 범위 내 기술 판단의 위임 근거다. 별도 기능 승인으로 다시 확인하지 않는다. 상위 계약 변경, 필수 결과의 유예, 범위 밖 기능·외부 설치·게시 권한까지 부여한 것으로 해석하지 않는다.

| 항목 | 이번 실행 기준 | 구현 재량과 한계 |
|---|---|---|
| current display exact 우선 | 필수 | 같은 원본 표시 이름의 모든 exact item이 그 이름을 포함할 뿐인 항목보다 앞선다. |
| 앞뒤·연속 공백 및 한국어 이름의 띄어쓰기 차이 | 필수 | 최소 U+0020을 양쪽 검색창의 표시 이름 검색에서 처리한다. 기존 literal 조회를 보존하며 숫자·기호·ID 자체는 지우거나 합치지 않는다. 변환 방식·추가 공백 문자 지원은 구현 담당자가 정한다. |
| 공백만 있는 입력 | 필수 | 빈 검색과 같은 상태로 처리한다. global API는 빈 결과, UI는 browse 복귀; local은 원래 목록·browse 순서라는 기존 역할 차이를 유지한다. |
| ASCII case와 global internal ID 조회 | 기존 동작 유지 필수 | searchable ID key와 exact FullType identity를 분리한다. local은 기존 display-only 범위로 고정하여 별도 ID 기능 확장을 하지 않는다. |
| 이름과 ID의 관련성 순서 | 실행 기준 확정 | 일반 이름 입력에는 원본 표시 이름 exact → 필수 공백 처리 후 이름 exact → 다른 이름 일치 → ID-only 부분 일치 순서를 지킨다. 전체 FullType과 일치하는 명시적 ID 조회는 해당 identity를 먼저 표시할 수 있다. 중간 이름 relation의 분해와 자료구조는 구현 재량이다. |
| Unicode canonical equivalence, 단어 순서, 초성·혼합 입력, KO의 EN 이름 alias | 제한된 선택 지원 | 필수 결과를 훼손하지 않고 아래 품질 기준을 만족하는 경우 구현 담당자가 채택·보류한다. alias는 확인 가능한 해당 아이템의 이름 source에 한정하며 새 번역·사실 추론을 하지 않는다. 한 항목 때문에 나머지 구현을 멈추거나 모든 후보를 의무 평가하지 않는다. |
| typo/edit-distance, 새 안내·동명 식별자 UI, local ID 검색 확대, 별도 formal search authority | 이번 최소 실행에서는 보류 | 추가 검토·승인 자체를 선행 작업으로 만들지 않는다. 필요성이 드러나면 후속 제안으로 기록하며 몰래 구현하지 않는다. |

선택 지원을 채택할 때도 원본 이름 exact보다 약한 관계로 취급한다. local에 alias를 채택한다면 group의 실제 member별 일치와 기존 표시 row/variants의 관계를 보존한다. canonical Unicode 구현 가능성이 부족해도 일반 공백 처리까지 유예하지 않는다. 지원하지 않는 추가 입력은 알려진 한계로 남기되 필수 입력의 실패와 구분한다.

**검색 품질의 최소 수용 기준:** 별도 품질 평가 시스템이나 benchmark suite 대신 기존 harness의 소수 사례·데이터 행에 expected target, 허용되는 상위 결과 그룹, 관련 없는 결과를 표시한다. 처음부터 나열한 사례를 모두 별도 test function으로 만들 필요는 없다.

- Change 1의 baseline과 구현 전 확인한 아이템 데이터로 기대값을 정한다. 정확한 이름/필수 공백 변형 외에 실제 실패 사례, 짧은 유효 부분 검색, 무결과 입력, 충돌하기 쉬운 이름·ID 사례를 구별할 수 있는 최소 사례만 보강한다. 실사용 사례가 없으면 구성 사례임을 표시한다. 두 검색창의 후보 범위 차이도 반영한다.
- 필수 이름·공백 사례에서는 기대 exact FullType group이 누락되지 않고, 원본 exact 및 공백 처리 후 exact의 우선순위 위반이 없어야 한다. `망치`, `  망치  `, `대형 망치`, `대형  망치`, `대형망치`를 optional로 바꿔 통과시키지 않는다.
- 기대값에 표시한 관련 없는 항목은 금지한 상위 그룹에 새로 진입하지 않아야 한다. 무결과로 정한 입력은 무관한 항목으로 채우지 않는다. 기존 유효 부분 검색·ID 조회는 유지한다. 기대값은 production matcher/comparator를 호출해 생성하지 않는다.
- 추가 변환은 정해둔 기대 target을 실제로 더 찾게 하면서 위 회귀·오탐 조건을 만족할 때만 채택한다. 단순 결과 수 증가로 채택하지 않는다. 전역적인 의미 정답을 가정하거나 모든 아이템의 관련성을 수작업 라벨링하지 않는다.
- 측정 지표나 상위 범위에 추가 수치가 필요하면 baseline과 사례의 목적에 따라 candidate 평가 전에 구현 담당자가 정한다. 기존 기준을 candidate에 맞춰 완화하지 않는다. 기대값 자체의 오류가 발견되면 source 근거와 수정 이유를 보존하고 영향받는 사례만 다시 평가한다.

**Baseline 증상 추적:** 기존 관찰 입력에는 before/after의 target presence·rank·새 결과 및 해소 여부를 연결한다. 앞뒤 공백·띄어쓰기와 exact 순위는 필수 해소 대상이다. `망치 대형`, `ㅁㅊ`, KO의 `Club Hammer`는 선택 지원의 채택·보류와 실제 결과를 구분해 남긴다. 보류는 해소를 뜻하지 않는다. 같은 증상·사례·판단을 별도 표와 receipt에 중복 작성하지 않는다.

**Validation / 결과:** 아래 Change 3~5의 구현과 함께 기존 Browser harness에서 품질·상태를 확인하고, 지원 동작·기대값·결과·보류 이유를 하나의 기록으로 유지한다. 모든 선택 후보의 disposition이나 owner 서명이 있어야 다음 단계로 넘어간다는 조건은 없다. 기술적 미지원 때문에 필수 결과가 불가능하면 이를 `partial` 또는 구체적 차단 사유로 남기며, 필수 목표를 낮추는 변경은 사용자 결정 없이 하지 않는다.

---

### Change 3 — Snapshot-owned SearchDocument와 공통 core

**Purpose:** 검색용 표현의 생성과 수명을 기존 Browser owner 안에 둔다.

**Files:** 신규 예정 IrisBrowserSearch, Query, ProjectionBuilder, Data; 필요 시 Lifecycle의 좁은 연결.

**Implementation Notes:**

1. private SearchDocument는 exact `fullType`, 원본 current `displayName`, ID 비교 키와 필수 공백 처리·채택한 추가 지원에 필요한 파생 값만 가진다. normalized key를 map의 canonical identity로 삼지 않는다.
2. ProjectionBuilder의 최초 build와 Query의 locale refresh가 같은 document 생성 함수를 사용한다. UI 렌더링과 매 keystroke마다 전체 이름을 다시 정규화하지 않는다.
3. QueryView는 raw query를 보존하고 채택 변환만 파생한다. MatchRelation은 candidate별 내부 평가 결과로 두며 공유 row에 query별 score를 덮어쓰지 않는다.
4. 기존 `(Browser generation, normalized locale, snapshot)`이 document를 소유한다. 전역 search cache, 별도 epoch authority, normalized-name identity index를 도입하지 않는다.
5. 새 row/document map과 기본 정렬 source를 완성한 뒤 publish한다. 생성·정렬 중 예외나 재진입이 있어도 old/new table을 섞지 않는다. 교체 실패 시 이전 snapshot을 현재 locale의 성공 결과라고 반환하지 않는다.
6. owner 교체 시 documents, previous candidates/results, variant/display-name/folded-count 파생 cache를 함께 폐기한다. 같은 locale의 active data 교체도 generation reset을 통과한다.
7. global 반환은 기존 `{fullType, displayName, category, subcategory}` projection을 유지한다. local은 `{fullType, displayName, isPrimary, variants}`를 보존하며 내부 key·relation을 노출하지 않는다. caller mutation으로 다음 결과나 private state가 바뀌지 않아야 한다.
8. Query의 older cache-shape compatibility branch는 실제 fixture/caller를 확인한 뒤 얇은 adapter로 유지하거나 명시적으로 정리한다. 별도 predecessor matcher로 남기지 않는다.

SearchDocument / QueryView / MatchRelation은 책임 설명이다. 필수 동작·identity·수명 경계를 지키는 한 별도 class/table/module 수나 함수 이름을 고정하지 않는다. 기존 모듈에 합치거나 더 단순한 표현을 사용할 수 있으며 테스트가 구현 형태를 강제하지 않게 한다.

**Validation:** 정확 identity coverage, normalized collision, 동명 distinct row, deterministic document generation, copy-on-read, 초기 미구축/empty fixture, build 실패 복구, locale/generation 교체, 교체 중 예외·재진입 사례. `Base.LemonGrass` / `Base.Lemongrass` 같은 case-sensitive identity 쌍은 검색 키가 같아도 별개다.

**기록할 결과:** current snapshot에 귀속된 공통 core와 기존 lifecycle 회귀 결과. semantic payload와 public row shape delta는 0이며 별도 단계 승인 없이 Change 4~5와 통합할 수 있다.

---

### Change 4 — Lexical matching과 relevance ordering

**Purpose:** boolean 부분 일치를 relation과 deterministic 순위로 확장한다.

**Files:** IrisBrowserSearch, Query, 기존 Browser harness 및 관련 Python acceptance.

**Implementation Notes:**

1. display와 ID field에서 독립적으로 일치 관계를 계산하고, 한 item이 여러 관계를 만족하면 Change 2에서 확정한 최상위 relation 하나를 선택한다. FullType별 결과를 중복 삽입하지 않는다.
2. 원본 이름 exact와 필수 공백 처리 후 exact, 다른 이름 일치, ID-only의 순서는 Change 2를 따른다. 실제 relation 표현과 중간 계층은 구현 재량이며 채택하지 않은 추가 token/초성/alias/fuzzy relation은 만들지 않는다.
3. membership 판정과 ranking을 분리한다. 정렬 때문에 matched identity가 추가·제거되면 안 된다.
4. 동일 tier에서는 원본 display name, exact FullType 순으로 deterministic하게 정렬한다. Lua `pairs` 순서, locale 의존 외부 sort, popularity·primary classification을 검색 relevance에 넣지 않는다.
5. 정렬된 snapshot source를 tier bucket에 분배하는 방식을 우선 검토하여 매 키 입력마다 전체 기본 순서를 다시 sort하지 않는다. local bucket 분배에서도 tier 내 정렬 키는 `isPrimary`를 제외한 원본 display name → exact FullType이다. `getItems`의 primary 우선 순서를 그대로 bucket에 유지하지 말고, 위 순서를 보장하는 snapshot 후보 순서를 사용하거나 bucket 내부 순서를 정렬한다. query 변경 때 relation과 결과 순서는 반드시 재평가한다.
6. 기존 `test_iris_browser_single_pass_cache_contract.py`의 `table.sort(result` 부재 assertion은 원래 반복 global sort 방지 의도를 확인해 처리한다. 새 함수를 다른 파일로 옮겨 assertion만 통과시키거나 검사를 이유 없이 삭제하지 않는다.

**Validation:** Change 1에서 고정한 KO·EN 각각의 중복 exact FullType key 처리 후 번역 corpus로 exact-name 순위를 확인한다. KO는 조사 기준 2,007 exact key이며 EN 분모는 별도로 집계한다. 기존 Browser harness의 한 데이터 순회에서 각 locale의 unique display name `N`을 query로 넣고 전체 exact FullType group이 mere partial group보다 앞서는지 확인한다. 이와 함께 Change 2의 공백·부분 검색·오탐 사례를 같은 실행에 넣는다. 이름별 test function, locale별 Gate, 별도 원본 줄 sweep은 만들지 않는다.

번역 항목 줄 수·중복 처리 규칙은 입력 metadata로 한 번 기록한다. KO·EN의 실제 검사 수와 위반/미실행 수는 구분하며 한 locale의 성공으로 다른 locale을 대신하지 않는다. 실제 active snapshot은 Change 6에서 확인한 범위만 연결하고 정적 corpus 성공을 runtime 전수 검증으로 쓰지 않는다.

기존 사례에서 duplicate 이름의 distinct FullType, ID retrieval, rank-only 변경의 membership, deterministic 결과, local의 `isPrimary`가 lexical 순서에 개입하지 않는 조건을 함께 확인한다. core와 동일한 comparator를 oracle로 호출하는 자기비교로 순위 계약을 증명하지 않는다. 순위·품질·identity를 별도 suite로 분해하지 않는다.

**기록할 결과:** 같은 harness 실행의 exact-name/공백/부분 검색/오탐 결과와 baseline 대비 target presence·rank·결과 집합 변화. 필수 범위의 실패나 미실행은 최종 완료를 막지만, Change 4 전용 승인·Gate는 없으며 Change 3~5의 통합 구현을 허용한다.

---

### Change 5 — 두 검색 surface와 incremental / UI state 정합성

**Purpose:** 공통 core를 실제 두 callback에 연결하고 입력 전환에서 누락·stale 목록을 없앤다.

**Files:** Data, Query, ListController; 필요한 내부 local adapter와 기존 harness.

**Implementation Notes:**

1. global은 active snapshot 전체, local은 현재 category/subcategory에 해당하는 후보를 제공한다. controller 안의 display substring 구현을 제거하고 같은 normalization / matching / ranking을 사용한다.
2. local의 표시 folding은 VariantIndex가 계속 소유한다. 기존 display-only 범위에서 동명 그룹의 relation을 적용하고 `variants` 배열과 대표 FullType을 보존한다. 선택 지원인 alias를 local에 채택한다면 그룹의 각 exact member를 평가한 뒤 기존 표시 row로 projection하며 대표가 아닌 member 누락을 막는다. local ID 검색은 이번 범위에 추가하지 않는다.
3. 활성 query에는 공통 lexical tier를 적용하고 local `isPrimary`는 row metadata로 보존한다. empty local query에는 기존 browsing 순서를 되돌린다. 후보 범위·field scope·folding이 다른 global/local의 visible row equality를 요구하지 않는다.
4. 기준 경로는 같은 current snapshot·scope·field mask·query를 이전 결과 없이 평가한 fresh search다. 최적화와 기준 경로의 ordered exact identity 및 local projected row/variants를 비교한다.
5. prefix 재사용은 동일 owner와 동일 surface/scope/field 조건에서 membership 단조성이 입증된 입력 family/transition에만 허용한다. query raw byte 길이 증가만으로 정규화·IME 전환을 판단하지 않는다.
6. append라도 relation 순위는 달라질 수 있다. 이전 relevance 순서를 그대로 유지하지 않고 새 query로 재평가한다. 불명확하면 full snapshot 평가로 돌아간다.
7. backspace, clear, query replacement/paste, locale/generation, category/subcategory, surface 전환은 candidate universe를 재확인한다. 한 surface의 이전 좁힌 결과를 다른 surface의 source로 쓰지 않는다.
8. global clear 분기에서 Data/Query의 초기화 경로를 실제 호출하고, categories뿐 아니라 stale item/subcategory/selection/detail이 남지 않도록 전환한다. 유효한 browsing 선택을 복원하거나 선택이 없으면 하위 목록·detail을 비우는 명시적 상태를 사용한다. 공백만 있는 입력도 반드시 같은 규칙을 따른다.
9. UI에 보이는 목록의 owner도 확인한다. query를 바꾸지 않은 채 locale/rebuild가 발생한 경우와 창을 닫고 다시 여는 경우를 시험한다. 무조건 매 프레임 전체 검색이나 debounce를 도입하지 않는다.

**Validation:** `ㅁ → 망 → 망치`, `망치 → 망 → empty`, `대형 → 대형  → 대형 망치`, clear 후 재입력, 다른 문자열 paste, `KO → EN → KO`, generation A→B, global↔local 및 category 전환을 fresh 기준과 비교한다. 선택은 화면 index가 아닌 실제 payload의 FullType을 따라야 한다. 기존 harness의 `resolveSelectedPayload` 단위 검사에 더해 설치된 ListController callback 경로를 호출하는 사례가 필요하다.

**기록할 결과:** 두 surface의 공통 검색 의미, clear 상태 복구, incremental ordered-equivalence를 같은 harness 결과에 포함한다. 설명할 수 없는 divergence가 있으면 해당 최적화를 비활성화하며 별도 optimization 승인 Gate는 만들지 않는다.

---

### Change 6 — Actual PZ 한국어 입력·locale·활성 데이터 검증

**Purpose:** repository 결과를 실제 사용자가 보는 검색 동작에 연결한다.

**Files:** current runtime source와 외부 candidate package / 관찰 기록. 필요할 때만 기존 instrumentation에 bounded observation 추가.

**Implementation Notes:**

1. 현행 package entrypoint로 격리 candidate를 준비하고, 시험한 Lua 파일·semantic payload·package identity를 source subject와 대조한다. 과거 `pkg2/Iris` 등이 자동으로 이번 검색 구현을 포함한다고 가정하지 않는다.
2. baseline 환경은 exact PZ build + Iris + KO + 해당 활성 아이템 집합으로 기록한다. extension은 시험 가능한 활성 mod item, translation override, duplicate name, locale 전환으로 분리한다.
3. exact 이름, 필수 공백 처리, 채택한 추가 입력과 typing/commit/backspace/paste/clear를 두 검색창에서 함께 확인한다. ID 조회는 global의 기존 범위에서 검사한다. composing이 callback에 오지 않으면 그 사실을 적고 composing 처리 성공은 주장하지 않는다.
4. TranslationLoader의 cached language가 실제 전환에서 언제 갱신되는지 확인한다. runtime에서 언어 변경이 지원되지 않으면 restart/reopen 등 실제 지원 경로와 harness 전환 결과를 구분해 남긴다. 관찰되지 않은 live switch를 PASS로 쓰지 않는다.
5. `getAllItems` 기반 active item 수와 실제 이름을 기록하고 알려진 mod item이 그 snapshot에 있을 때의 retrieval을 확인한다. translation override가 같은 locale에서 바뀌면 기존 reload/rebuild로 갱신하는 경로를 확인한다.
6. 같은 장비·환경·query 범위에서 snapshot build, 첫 query, 반복 키 입력, backspace, broad query의 before/after를 가능한 범위에서 관찰한다. 계측 enable 상태·반복 수·active item 수·단위·측정 위치를 기록한다. 기존 build 시간과 row scan 수만으로 query latency를 주장하지 않는다.
7. 정량 허용 범위는 baseline 관찰 뒤 candidate 결과를 보기 전에 기록한다. 정밀 timing을 얻지 못하면 그 한계를 남기고 최소한 입력/삭제 시 사용을 방해하는 frame hitch·silent omission 여부를 확인한다. 정성적 fallback은 usability 관찰이며 `성능 기준 PASS`가 아니다. timing이 없고 실제 관찰이 뒷받침되면 `관찰 범위에서 사용을 방해하는 명백한 hitch 미관찰`로만 기록한다. silent omission은 별도의 correctness 실패로 처리한다.

**Validation:** 제7절의 통합 PZ 확인을 같은 candidate subject에서 수행한다. 수정하면 영향받는 입력·locale·package 관찰을 corrected subject에서 다시 확인한다. 이번 계획에 없는 모든 모드 조합을 검사하려고 범위를 넓히지 않는다.

**기록할 결과:** 같은 PZ 확인 흐름에서 입력·선택·상태 전환·active data와 source/package 일치를 기록한다. 정량 timing 또는 `timing 미측정`과 usability 관찰은 구분하되 별도 성능 보고서를 요구하지 않는다. 정성 관찰로 performance PASS나 성능 개선을 주장하지 않으며 repository-only 성공으로 실제 PZ 확인을 대신하지 않는다.

---

### Change 7 — Current adoption 및 단일 closeout

**Purpose:** 실제 검증된 검색 동작만 제품 current 상태와 문서에 반영한다.

**Files:** 채택 source / 외부 current package, 필요한 current 문서, 단일 closeout.

**Implementation Notes:**

1. final source subject에 결속된 required 검증과 PZ 관찰을 확인한 뒤 current implementation/package를 정렬한다. 기존 결과를 새 subject의 PASS로 상속하지 않는다.
2. 중복 predecessor 검색 path와 임시 관찰 코드를 정리하고 facade / 필요한 compatibility adapter만 남긴다. optional 입력 family가 defer/reject이면 그 미완성 코드·key를 runtime에 남기지 않는다.
3. public-facing membership/ordering 변화, local/global 의도적 차이, 필수·선택 지원 범위를 같은 closeout에 기록한다. 별도 formal search authority나 contract 발행을 선행 조건으로 만들지 않는다.
4. Browser semantic row identity, variant grouping, Detail ViewModel, Menu factual body, Layer 4와 Alt Tooltip을 검색 전후 대조한다. search-derived key의 변화와 semantic artifact의 비변경을 구분한다.
5. baseline 입력과 필수/선택 범위, 실제 해소·오탐·순위 결과, validation command/exit/subject, corpus 분모, package/PZ 및 한계를 단일 closeout에 연결한다. 필수 실패는 완료를 막으며, 선택 입력의 미해소는 그대로 공개한다. 범위 내 기술 선택마다 decision receipt를 만들지 않는다. 상위 계약상 실제 필요한 review/owner-only 판정만 해당 evidence와 구분해 기록하며 추가 gate를 만들지 않는다.

**Validation:** required source closure와 package projection을 확인하고 제7절 최종 검증을 충족한다. semantic producer 재실행이나 새 validation authority 발행으로 검색 closeout을 확장하지 않는다.

**최종 결과:** current search implementation/package와 단일 scope-qualified closeout. 코드·자동검증·PZ·adoption 및 적용되는 review 상태를 구분하며 이 작업의 완료 판단은 제12절에서 한 번 수행한다.

---

## 7. Validation Plan

### 최소화 원칙

- **새 검색 전용 Gate·regular validator·단계별 승인: 추가하지 않는다.** 기존 계약의 필수 검증은 유지하고 이 작업의 완료 판단은 같은 최종 구현에 대한 결과를 한 번 모아 수행한다. Change별 Validation/Exit를 각각의 Gate로 읽지 않는다.
- **신규 test file·top-level test function·wrapper는 기본적으로 추가하지 않는다.** 기존 Browser harness의 사례/입력 행과 기존 assertion을 보강한다. 기존 구조로 보호할 수 없는 독립 동작이 확인된 경우에만 최소 추가하며, 이유는 같은 closeout에 짧게 남긴다. 숫자 상한 때문에 필요한 검증을 생략하지 않는다.
- 구현 중에는 수정한 동작을 확인하는 **하나의 focused 실행 경로**를 사용하고 시점·횟수는 구현 담당자가 정한다. 단계별 full-gate 반복, 같은 harness의 여러 wrapper를 통한 별도 반복, 별도 품질 suite·benchmark framework·finalizer는 추가하지 않는다.
- 최종 exact subject에서 기존 mandatory Clean-Checkout **Run A/B와 deterministic comparison 한 세트**를 수행한다. 이는 `DECISIONS.md`의 현행 계약이므로 축소하지 않는다. 그 실행에 포함된 current-required·Browser·비검색 회귀 결과는 재사용하며 동일 subject·scope의 별도 실행을 다시 요구하지 않는다. 포함되지 않은 필수 범위만 보충한다.
- 검증 관련 source나 protected result가 바뀌면 영향을 받는 검증을 새 subject에서 다시 수행한다. 이를 임의의 focused 검사로 mandatory full gate를 대체하는 근거로 삼지 않는다. 기존 테스트/등록 목록을 이 문서만으로 삭제·면제하지 않는다.

### Automated Validation

**Fail-closed:** exact relevant command가 exit `0`일 때만 해당 범위 PASS를 기록한다. 필요한 도구·환경·입력이 없으면 해당 검증은 BLOCKED이며 출력 marker나 과거 결과로 대신하지 않는다.

repository root의 PowerShell을 사용한다. Python 실행은 사용자 지시의 `uv run python <script>` 원칙과 아래 실제 Browser 진입점을 따른다. Lua 수정 시 사용자 지정 syntax 명령은 유지한다.

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\check_lua_syntax.ps1
```

syntax script는 root의 `tools/check_lua_syntax.ps1`, package script는 `Iris/tools/package_iris.ps1`이다. 실제 실행 시 경로·selector·external output root를 확인하며 package 인자는 그 script의 parameter 정의를 따른다. 기본 syntax root에는 repository-external candidate가 자동 포함되지 않으므로 후보 package의 해당 coverage도 확인한다. 문법 성공은 Kahlua/runtime 성공이 아니다. Java/JS 변경을 예정하지 않아 Gradle/Biome을 추가하지 않는다.

아래 행은 **검증 결과의 범위**이며 별도 suite나 Gate를 각각 만들라는 뜻이 아니다.

| 재사용할 실행 | 함께 확인할 범위 | 수용 기준 |
|---|---|---|
| 기존 Browser harness와 현행 focused wrapper | Change 2의 최소 품질 사례, KO·EN deduplicated exact-name sweep, identity/copy, snapshot 초기·교체 경로, controller clear/선택, incremental/fresh 동등성 | 필수 target 누락·순위 위반·금지한 신규 오탐 없음. 기존 identity/variants·field scope 보존, stale 상태나 설명되지 않는 결과 차이 없음. |
| 최종 기존 `validate full`의 Run A/B·comparator 및 필수 Lua syntax | current-required 계약과 Browser/source guard, facade, Detail/Layer 4/Tooltip의 적용 범위 | exact tracked subject의 mandatory 결과 성공. full gate가 제공한 결과를 이 계획의 회귀 증거로 재사용. |
| 현행 package 생성·validation | 신규 runtime module 포함, current payload와 exact source/package 일치 | 기존 package 검사에 필요한 coverage를 합치고 별도 검색 package gate는 만들지 않음. |

**Browser 실제 진입점:** `test_iris_browser_state_selection_search_acceptance.py`의 `test_actual_standalone_lua_state_and_cache_contracts`와 `Iris/test/lua/browser_state_acceptance_harness.lua`를 우선 재사용한다. `test_iris_browser_single_pass_cache_contract.py`의 기존 보호 동작은 유지하되 같은 harness 실행을 추가한 독립 증거로 세지 않는다. search acceptance Python 파일의 `full` 모드는 현재 Tooltip harness를 실행하므로 Browser 검증으로 잘못 사용하지 않는다. 새 runner나 registration은 필요하지 않다.

```powershell
uv run python -B .\Iris\build\description\v2\tests\test_iris_browser_state_selection_search_acceptance.py BrowserStateSelectionSearchAcceptanceTest.test_actual_standalone_lua_state_and_cache_contracts
```

이 실행은 KO/EN deduplicated exact-name sweep과 whitespace·relevance·variant·state-transition 사례를 같은 Lua harness에서 확인하며 subprocess timeout은 60초다. 같은 subject의 full gate가 이미 이 범위를 실행했다면 해당 결과를 재사용하고 single-pass wrapper를 별도 증거로 반복하지 않는다.

**사례 통합:** exact-name sweep은 기존 harness 안에서 KO·EN 각각의 고정된 deduplicated corpus를 순회한다. 이름마다 test function을 만들거나 locale별 새 Gate를 만들지 않는다. raw 번역 항목 줄·중복 집계는 같은 입력의 metadata이며 별도 실행/전수 재검사를 요구하지 않는다. 품질·identity·snapshot·UI transition 사례도 같은 harness에 합치고 기존 사례를 재사용한다. 예상 결과는 production matcher/comparator의 자기비교로 생성하지 않는다. 새 정규 검증 authority로 등록하지 않는다.

source-text assertion은 보호하던 동작을 확인해 최소 수정할 수 있다. 특정 helper명·모듈 배치·정렬 함수 표기만 강제하는 검사를 추가하지 않는다. 기존 보호 동작을 없애거나 검사를 피하기 위한 코드 이동은 허용하지 않는다.

### Manual Validation

동일 candidate package의 **하나의 실제 PZ 확인 흐름**에서 아래 범위를 함께 관찰한다. 서로 다른 source/package 또는 실제로 다른 환경이 필요한 경우만 분리하며, 아래 행마다 별도 실행·승인·보고서를 요구하지 않는다.

| 확인 범위 | 최소 관찰 결과 |
|---|---|
| 검색 품질과 선택 | 실제 KO 표시 이름·필수 공백 변형·기존 ID·채택한 추가 입력을 양쪽 검색창에서 확인. scope 차이는 구분하고 결과 선택 시 실제 detail FullType·동명 variant가 맞아야 함. 짧은 부분 검색과 관련 없는 결과는 자동 검사와 같은 기대 사례를 재사용. |
| 입력·상태 전환 | typing/확정/backspace/paste/clear, global/local·category 이동, 실제 지원되는 locale/rebuild/reopen을 한 흐름에서 확인. stale 목록·선택·detail·silent omission 없음. callback에 오지 않은 composing이나 지원하지 않는 live locale switch를 성공으로 기록하지 않음. |
| 실제 환경과 사용성 | PZ build·locale·active count·mod/번역 환경·시험 package를 한 번 기록. 시험 가능한 mod item/translation override만 확인. 같은 흐름에서 입력 지연·명백한 hitch와 비검색 정보의 이상을 관찰하고 기존 package/회귀 결과와 연결. |

성능 timing은 기존 계측이나 같은 PZ 확인에서 얻을 수 있는 범위로 기록하며 별도 benchmark suite는 만들지 않는다. 수치 판정이 가능하면 baseline 뒤 candidate 평가 전에 기준을 정한다. timing이 없으면 `성능 PASS/개선`이 아니라 실제 관찰에 근거한 사용성 결과와 측정 한계를 기록한다. 실제 사용을 방해하는 지연이나 입력 누락은 완료를 막는 문제다.

### Validation Limits

- 최초 작성은 계획 문서만 대상으로 했다. 후속 실행 결과는 단일 closeout의 실제 command/exit와 미검증 범위로 한정한다.
- standalone Lua는 Kahlua·engine 이름 조회·실제 IME를 대신하지 않는다. 번역 corpus 결과도 모든 active item·모드·번역팩의 검증으로 확대하지 않는다.
- 모든 IME/PZ 버전/외부 모드 조합, multiplayer 전체, 장시간 soak, Workshop/배포 검증은 범위 밖이다. 채택하지 않은 추가 입력도 지원한다고 주장하지 않는다.
- 필수 이름·공백 결과나 범위 내 PZ/state 검증이 남으면 `unvalidated_but_in_scope`다. 새 Gate를 만들지 않는다는 이유로 이 조건을 생략하거나 out-of-scope로 바꾸지 않는다.
- 별도 registry·일회성 보고서·후보별 승인 의무를 줄이는 것이며, 검증 결과의 subject·실패 보존·정직한 완료 범위는 유지한다.

---

## 8. Risk Surface Touch

### Authority Surface

검색 의미의 단일 **구현 owner**는 변경한다. semantic authority는 변경하지 않으며 별도 formal search authority 발행은 이번 최소 범위에서 보류한다. 기존 API/cache ownership·full-gate/evidence 원칙은 유지한다. 구현 재량은 Change 2의 결과·품질·책임 경계 안에서만 행사한다.

### Runtime Behavior Surface

변경 있음: query normalization, membership, ordering, prefix 재사용, clear / surface 전환과 snapshot 파생 state. Lua runtime 안에 한정한다. shared TranslationLoader에 수정이 필요하면 해당 consumer의 영향까지 먼저 명시한다.

### Compatibility Surface

현재 manifest의 listed UI/API surface와 기존 observable row/copy 계약을 보존한다. `searchAll`이 listed entry가 아니라는 이유로 내부 consumer의 호출을 깨지 않는다. ID retrieval, variant selection, cached locale의 기존 consumer 영향을 회귀 확인한다.

### Sealed Artifact Surface

변경 없음이 원칙이다. semantic generation / Tooltip / Classification / DVF / QG / Recipe artifact를 검색 때문에 재생성하지 않는다. runtime source 변경에 따른 required source-closure/validation binding의 successor와 semantic payload 재발행을 구분한다.

### Public-Facing Output Surface

변경 있음: 결과 포함 여부, 정확 이름·공백 처리 후 exact의 노출 순서, clear 후 상태. 결과 없음 문구·새 secondary identifier UI는 이번 최소 범위에서 보류한다. 검색 순위를 추천이나 아이템 quality로 설명하지 않는다.

---

## 9. Risk Analysis

### Architecture Risk

- **높음 — identity 병합:** normalized name·lowercase FullType을 key로 쓰면 case-sensitive identity가 소실된다. exact map과 search key를 분리하고 collision fixture로 방지한다.
- **높음 — 새 owner 중복:** core가 별도 generation/locale나 전역 cache를 가지면 snapshot 책임이 갈라진다. 기존 Lifecycle/Query가 수명을 소유하게 한다.
- **중간 — semantic 경계 침범:** primary/Recipe 연결 정보를 ranking에 쓰거나 EN alias를 fact fallback으로 확장할 위험. lexical field/tier를 명시하고 semantic 비변경을 확인한다.

### Runtime Risk

- **높음 — incremental 누락·순서 divergence:** normalization과 composing은 raw prefix 확장과 다를 수 있다. 불확실하면 full search, 결과 ordered-equivalence로 검증한다.
- **높음 — stale locale/data/UI:** loader cache와 search snapshot, 화면 목록의 갱신 시점이 다르다. query가 변하지 않는 owner 전환과 clear/reopen까지 시험한다.
- **높음 — 과도한 broad matching:** 초성·어순·whitespace folding으로 결과와 정렬 비용이 증가할 수 있다. family별 품질·비용 관찰 후 판정한다.
- **중간 — build·allocation 비용:** document key 추가가 snapshot build와 retained memory를 늘릴 수 있다. 채택 key만 만들고 normal production에서는 진단 계측을 비활성화한다.
- **중간 — Kahlua 차이:** UTF-8 byte 조작, Unicode library/전역 함수 가용성을 추정하지 않는다. 실제 지원 환경에서 확인한다.

### Compatibility Risk

- **높음 — local folding 누락:** 대표 row만 alias 검색하면 group의 다른 member의 이름을 찾지 못할 수 있다. alias를 채택할 경우에만 member→표시 row projection을 확인한다. local ID 확대는 보류하고 기존 display-only·variants 계약을 유지한다.
- **중간 — 기존 ID 사용성 변화:** retrieval을 유지해도 위치가 달라질 수 있다. display/ID tier를 명시하고 baseline 대비 순서를 공개한다.
- **중간 — mod·번역 데이터 차이:** 저장소 이름과 active name이 다를 수 있다. 실제 snapshot을 검색 source로 유지하고 관찰 환경을 한정한다.

### Regression Risk

- **높음 — source/package 불일치:** 다른 package를 시험하면 source 테스트가 실제 입력 문제를 설명하지 못한다. final subject와 시험 package를 결속한다.
- **중간 — 허술한 test 근거:** `full` mode의 Tooltip 결과를 Browser 검색 PASS로 오독하거나 기존 source-text assertion만 만족시킬 수 있다. 기존 harness 안에서 실제 production 결과와 독립 기대값을 비교하며, 검사 수 감축을 보호 동작 누락으로 바꾸지 않는다.
- **중간 — stale 선택:** rank 변화/clear 뒤 list index로 선택을 유지하면 다른 detail을 열 수 있다. event payload의 exact identity와 selection 상태를 확인한다.
- **중간 — 범위 확대:** 검색 개선 중 분류·본문·Alt·전역 입력 처리를 수정할 위험. 명시한 파일 delta와 semantic bytes를 비교한다.

---

## 10. Rollback Plan

1. Change 1의 source / contract / package baseline을 보존하고 이 작업의 변경만 되돌린다. 다른 사용자 변경은 reset/revert 대상으로 삼지 않는다.
2. 특정 optional family가 원인이면 해당 key 생성·query 변환·relation만 독립적으로 제거하고 disposition과 검증 범위를 갱신한다.
3. incremental optimization이 원인이면 먼저 같은 contract의 full current-snapshot search를 사용한다. 성능을 위해 잘못된 후보 재사용을 유지하지 않는다.
4. ranking만 문제라면 membership을 유지한 채 predecessor ordering으로 돌릴 수 있게 구조를 분리한다. 다만 exact-name 목표를 충족하지 못하므로 그 상태를 개선 완료로 닫지 않는다.
5. 전체 rollback은 new matcher/ranking path를 제거하고 predecessor 검색 behavior와 필요한 UI 연결을 복구한 뒤 search-derived state를 폐기/rebuild한다. exact FullType map, semantic row, 기존 generation/locale owner는 유지한다.
6. 새 package가 전달됐다면 복구 package를 별도 identity로 만들고 시험한 subject를 기록한다. 설치 폴더를 자동 덮어쓰지 않는다.
7. 실패 evidence는 보존하고 corrected successor의 affected 검증을 다시 실행한다. 같은 실패 기록을 PASS로 덮어쓰지 않는다.

진행 중단 또는 해당 feature rollback 조건은 exact-name invariant 위반, 설명되지 않는 reference divergence, distinct FullType 손실, locale/generation stale 결과, 실제 한국어 입력 silent omission, 사용을 방해하는 상호작용 악화다. DVF / Classification / QG / Tooltip semantic data를 rollback 대상으로 만들지 않는다.

---

## 11. Governance Constraints

- `Philosophy.md` 준수: Iris는 근거 기반 정보 표시, 중립성, 100% Lua runtime과 메뉴/Alt 두 제품 surface를 유지한다.
- Pulse는 Iris에 의존하지 않는다. spoke 간 직접 참조·의존과 다른 모듈 책임 흡수를 도입하지 않는다. 필요한 플랫폼 capability는 기존 경계/SPI를 따른다.
- 검색 normalization은 presentation의 comparison representation일 뿐 FullType·사실·semantic equivalence의 authority가 아니다.
- Recipe와 우클릭 활용의 독립성과 동등성, Detail/Menu/Alt가 소비하는 사실의 정합성을 보존한다.
- public signature·row shape·item object identity·copy-on-read와 generation/locale owner를 보존한다.
- 기존 sealed payload·historical evidence를 덮어쓰지 않는다. 필요한 current 문서/contract 변경은 minimal additive successor로 남긴다.
- 신규 이름은 현재 책임을 표현하며 작업 단계명으로 durable module/test를 명명하지 않는다. 실행 명령은 이 계획의 검증 절과 실행 기록에 둔다.
- mandatory clean-checkout과 independent review / owner decision / runtime observation / adoption / publication은 서로 다른 축이다. 과거 PASS·owner 승인·hash 일치가 이번 실제 기능 증거를 대신하지 않는다.
- 필수 이름·공백 동작과 Change 2의 순위·scope는 이번 사용자 요청을 반영한 실행 기준이다. 범위 내 추가 입력·중간 구현·검증 묶음은 위임된 재량으로 결정하고 사용자 재승인을 반복하지 않는다. 상위 authority 변경·필수 범위 축소·범위 밖 기능은 별도 사용자 결정 없이 진행하지 않는다.
- 문서 작성 요청은 코드 구현·새 contract 승인·external package 설치·release 실행으로 확장하지 않는다. 향후 실행에서는 실제 사용자 범위와 이미 존재하는 권한을 먼저 확인하며 불필요한 재승인을 만들지 않는다.

---

## 12. Expected Closeout State

**이 문서의 현재 상태:** `implemented_only`. Source 구현과 기존 focused acceptance·필수 Lua syntax는 완료했다. 필수 Clean-Checkout A/B·comparison, candidate package, 실제 PZ 관찰은 미완료이며 세부 결과는 단일 closeout을 따른다.

**향후 실행 목표:** 아래 결과를 같은 최종 구현에서 충족한 경우에만 `complete`로 기록한다. 행마다 별도 Gate·승인·보고서를 만드는 것이 아니라 기존 검증과 단일 PZ 확인 결과를 최종 closeout 한 곳에서 연결한다.

| 완료 조건 | 필요한 결과 |
|---|---|
| 최소 검색 개선 | 원본 표시 이름 exact가 mere partial보다 앞선다. 앞뒤·연속 일반 공백과 한국어 표시 이름의 띄어쓰기 유무를 처리하여 `망치`/`  망치  ` 및 `대형 망치`/`대형  망치`/`대형망치`가 각각 기대 target에 도달한다. 공백만 입력하면 빈 검색 상태로 복귀한다. 하나라도 미해소이면 complete가 아니다. |
| 품질·기존 검색 보존 | KO·EN deduplicated corpus의 exact-name 결과, Change 2의 대표 부분 검색·금지한 신규 오탐·무결과 사례가 기준을 충족한다. 기존 global ID 조회, distinct FullType·동명 item·variants·public row/copy 계약을 보존한다. 지원 여부를 candidate 결과에 맞춰 낮추지 않는다. |
| 검색창·상태 일관성 | 의도한 global/local scope 차이를 제외하고 공통 의미·순위가 적용된다. clear/선택/locale/generation에서 stale 결과가 없고, 최적화 경로는 fresh 결과·순서와 일치한다. |
| 필요한 실행 증거 | 최종 exact subject의 mandatory Clean-Checkout Run A/B·comparison, 필수 Lua syntax, 현행 package validation 및 범위 내 실제 PZ 입력·선택·상태 관찰을 충족한다. 포함된 current-required·비검색 회귀 결과는 재사용한다. 새 suite나 Gate를 추가했는지는 완료 목표가 아니다. |
| 사용성과 범위 | 시험 PZ·언어·active data·package가 식별되고 사용을 방해하는 지연·입력 누락이 없다. timing이 없으면 성능 PASS/개선은 주장하지 않는다. 선택 지원의 채택·보류 및 실제 미해소 입력은 같은 기록에 공개한다. |
| 비간섭과 적용 | 검색 외 semantic payload·정보 의미는 보존되고 시험 source/package와 current 반영 상태가 일치한다. 적용되는 기존 review/owner-only 의무는 실제 근거와 구분하며 별도 release claim은 하지 않는다. |

코드만 구현하고 필수 검증이 남으면 `implemented_only` 또는 `partial`로 기록한다. 필요한 환경·도구나 상위 authority 결정이 없으면 해당 차단 사유를 기록한다. 최종 계약 검증을 없애거나 필수 이름·공백 실패를 optional로 재분류하여 완료를 만들지 않는다.

단어 순서·초성·영문 alias 등의 선택 지원은 미채택이어도 최소 실행을 막지 않는다. 이를 위해 모든 후보의 별도 disposition/승인표를 만들지는 않지만, 최초 관찰 입력 중 남은 실패와 지원 범위는 숨기지 않는다. 예를 들어 `ㅁㅊ`를 보류했다면 그 사실을 남기며 `최초 보고 증상 전체 해소` 또는 `모든 한국어 입력 지원`으로 표현하지 않는다.

허용되는 positive claim은 실제 근거 범위에서 다음처럼 제한한다.

> 검증한 PZ build·locale·활성 아이템 환경에서 Iris 검색이 정확한 표시 이름을 우선하고 기본 공백 차이로 인한 누락을 해소하며, 두 검색창의 정해진 범위와 exact item identity·현재 검색 상태를 보존한다. 추가 지원과 미지원 입력은 별도로 명시한다.

성능 개선은 실측 근거가 있을 때만 추가한다. 이 완료는 모든 외부 모드·번역팩·IME·PZ 버전의 호환성이나 Iris 전체 release / Workshop readiness를 뜻하지 않는다.
