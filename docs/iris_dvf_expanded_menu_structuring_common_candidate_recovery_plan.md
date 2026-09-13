# Implementation Plan

**문제 ID:** `DVF-RECOVERY-C`

**제목:** 검수된 DVF expanded의 Menu 구조화와 B/C 동일 제품 입력 연결

**작성일:** 2026-09-11

**상태:** implemented_only — 2026-09-11 C 구현·자동 통합 완료 / 실제 PZ 관찰 대기. [실행 결과](iris_dvf_expanded_menu_structuring_common_candidate_recovery_closeout.md) 참조. 아래 작성 시점 조사·검토 이력은 보존한다.

**후속 개정:** 사용자 요청에 따라 필수 표시·보존 결과는 유지하면서 테스트와 Gate를 최소화했다. 아래 Change는 독립 승인 단계가 아니며 같은 후보와 결과를 공유해 마지막 한 묶음으로 검증한다. 기존 Review의 절차 요구와 충돌하면 이 개정 본문을 따른다.

**입력:** 사용자 제공 「DVF-RECOVERY-C Roadmap」 v3 및 현재 Iris checkout

**양식:** [PLAN_TEMPLATE.md](PLAN_TEMPLATE.md)

이 문서는 실행 계획이다. 아래 저장소 조사와 입력 readback은 수행했지만 C projection 구현, 후보 생성, 자동 통합 검사, 실제 PZ 관찰은 아직 수행하지 않았다.

**검토 반영:** 사용자 제공 Implementation Plan Review의 검토 대상 SHA-256 `8e096c1ed400560eabb228a2bc1943b6804123d53cc5c1b1129a88f9f94a94be`가 수정 전 파일과 일치함을 확인했다. 이번 수정에서는 R-1~R-4를 모두 채택한다. R-1은 C 범위의 terminal state를 확정하면서 범위 밖 활성화·release를 완료 조건에 끌어들이지 않기 위한 선택이고, R-2~R-4는 기존 보존 의도를 실제 candidate admission과 검사 변경 기준으로 구체화한 것이다. 검토자들이 이 판정에 합의했다거나 수정된 계획이 재검토 PASS를 받았다는 뜻은 아니다. N-1~N-7도 반영하며 N-8의 상태 선택 요구는 §12의 직접적인 상태 정의로 충족한다. 원 로드맵 A-6의 충돌 이력은 보존하되 이 실행 계획의 추가 closeout gate로 사용하지 않는다.

---

## 1. Objective

검수된 `Iris/build/description/composition/descriptions.json`의 KO/EN expanded를 구조와 관계를 보존한 Menu product로 투영하고, 실제 Browser Detail과 우클릭 Wiki까지 연결한다. 같은 corpus의 compact를 사용하는 수락된 B Tooltip과 하나의 후보에서 공존하도록 한다.

사용자가 독립적인 용도·조건·특성·획득·대안을 구별하면서 선행 설명에 의존하는 후속 문장도 함께 읽을 수 있어야 한다. 원문을 하나의 장문으로 합치거나 모든 segment를 독립 카드로 나누는 것만으로 목표를 충족했다고 보지 않는다. Layer 2와 Recipe / Right-click / EvolvedRecipe의 독립적인 정보 접근도 유지한다.

완료 증거는 source conservation, product/package integrity, Lua presentation model, 실제 PZ 관찰을 구분한다. B의 실제 게임 수락을 C Menu의 표시 증거로 승계하지 않는다.

## 2. Scope

- 현재 Menu의 call/require/data 경로와 B 후보 assembly 경계를 확인한다.
- canonical expanded와 blocks의 관계를 offline display/product projection으로 전달한다.
- 내부 Lua lookup과 Detail ViewModel에 구조화된 표시 자료를 연결한다.
- Browser Detail 및 Wiki의 Layer 3 표시·높이·스크롤·상태 전환을 수정한다.
- B 수락 component와 C Menu를 동일 corpus에 결속한 후보 디렉터리/ZIP을 만든다.
- 변경 범위의 자동 검사, 동일 후보의 KO/EN PZ 관찰, closeout 및 후속 current 전환 인계를 수행한다.

### Explicitly Out Of Scope

- 저장소 current 공동 활성화, 일반 strict production finalization, release/Workshop 게시.
- r6 adoption·sealed predecessor의 수정 또는 재발행, 기존 corpus의 전수 문체 교정. C의 정확한 표시 연결에 꼭 필요한 metadata 또는 실제 표현 결함의 공통 owner 최소 환류는 예외로 허용한다.
- 독립 clone/worktree나 외부 validation workspace 생성, 외부 게임 폴더 탐색·자동 설치. 본 계획의 기본 실행 위치는 저장소 내부 `.tmp`이며 게임 관찰은 후보 인계 후 확보한다.
- 관련 없는 리팩토링, Java/JVM 추가, 타 spoke 모듈 변경, 웹 UI나 세 번째 정보 surface 추가.

## 3. Non-Goals

- A 복구, DVF-COMPOSITION-1/2, Problem 3 전수 품질 검수의 재실행.
- 새 fact 조사, acquisition 전수 재조사, unresolved 의미 전수 해결, 표현 polish 선행 수행.
- B S1~S4 역할·Alt·최대 네 화면 줄 정책 재설계 또는 B 전체 실제 PZ 재수락.
- Layer 2 taxonomy, Recipe / Right-click / EvolvedRecipe 의미·선택 계약의 재설계.
- 고정 카드/탭/접기 형식이나 섹션 개수 강제, 대표 용도 선택, 런타임 요약·번역·의미 재분류.
- 새 validator framework, proof/seal/receipt 체계, 전역 historical suite 및 freeze/release readiness 재판정.

## 4. Assumptions

### 입력과 회계 기준

| 입력 | SHA-256 |
|---|---|
| `Iris/build/description/composition/descriptions.json` | `ba0fc047b3a613e7ef98d2d762cfbd10c1996a02ad4e6f96d1bffa61878262d0` |
| `Iris/build/description/composition/blocks.json` | `b0b1f8b402c74c48efa0d3ef5bb9413709e38e4582cdbffe8ea74749304d5796` |

직접 reader는 `description_composition_results.read_result(root)`다. 현재 구현은 저장된 JSON을 `description_composition_model.validate_result`로 검사하며 producer를 실행하지 않는다. 파일 SHA 검사는 호출 측에서 함께 수행해야 한다. `items[].locales[ko/en].expanded`는 이전 expression의 block 배열과 달리 `state`, `reason`, `text`, `segments`를 가진 객체다. item에는 `qualifiers`, `relations`, `unresolved_relations`가 있고 compact에는 `detail_links`가 있다.

| 회계 축 | 기준 |
|---|---|
| DVF 대상 | exact FullType 2,105 items |
| C 직접 분모 | 4,210 expanded states = 2,105 × KO/EN |
| C 상태 | present 4,086 / absent 124 / failed 0 |
| locale별 expanded | present 2,043 / absent 62 |
| locale별 compact | present 1,984 / absent 121 |
| acquisition-only | compact absent / expanded present 59 items |
| 참고 축 | 전체 corpus 8,420 states / present 8,054; B support 2,280 |

B support와 C 분모를 합치지 않는다. B의 DVF 대상 밖 175개를 C 정상 absent 62개로 재분류하지 않는다. 이 수치는 현재 고정 입력에 대한 기준이며 후속 corpus가 바뀌면 기존 검증을 자동 승계하지 않는다.

### 2026-09-11 checkout 조사 결과

아래 경로는 `PZ/` 기준이다. 구현 시 변경 전 상태를 다시 기록하되 과거 문서를 current 증거로 대체하지 않는다.

| 조사 지점 | 확인된 구현과 계획상 의미 |
|---|---|
| `Iris/.../UI/Wiki/IrisContextMenu.lua` | 우클릭 항목에서 `IrisWikiPanel`을 여는 경로가 존재한다. Browser만 수정하면 Menu consumer가 남는다. |
| `Iris/.../UI/Detail/IrisItemDetailModelAssembler.lua: layer3Payload/fromItem` | `layer3_renderer.getText(fullType, {locale=locale})` → `IrisLayer3DisplayFormatter.format(raw)` → `model.layer3.display`의 문자열 경로다. locale와 FullType이 revision에 들어가며 L4 state는 별도로 조립된다. |
| `Iris/.../UI/Wiki/IrisWikiSections.lua: renderLayer3Section` | `model.layer3.display`를 반환한다. Browser와 Wiki의 공통 문자열 경계다. |
| `Iris/.../UI/Browser/IrisBrowserDetail.lua` | 위 문자열을 `addSeparatedMultilineSection`으로 추가하고 `detailContentHeight` 및 scroll 범위를 계산한다. |
| `Iris/.../UI/Wiki/IrisWikiPanel.lua` | 같은 section 문자열을 wrapped label로 배치한다. Browser와 별도 표시 소비자다. |
| `Iris/.../UI/Layer3/IrisLayer3DisplayFormatter.lua` | 문장부호와 두 문장 단위로 줄을 나눈다. 관계 metadata를 소비하지 않으므로 C grouping 판단기로 사용할 수 없다. |
| `Iris/.../Data/IrisLayer3DataLookup.lua` | `IrisLayer3DataCurrent`의 schema로 generation/product 경로를 선택한다. product의 `getLocale`도 현재 `blocks` 문자열 배열과 합친 `text` 계약을 검사한다. |
| `Iris/.../Data/IrisLayer3EnglishLookup.lua`, `layer3_renderer.lua` | EN 별도 lookup 및 product locale 경로가 있다. renderer는 successor 오류 시 predecessor 부활을 막는 분기가 있으나 C 상태 전파까지 보장하는 것은 아니다. |
| `Iris/.../Data/IrisLayer3DataCurrent.lua` | 현재 `iris_layer3_generation_pointer_v1`, generation `dvf33-ed92fa5c9ed4a1ed367f5d79365d04e1996e36a05d76a33bd7b8dd2176e7f82f`다. `IrisLayer3ProductCurrent.lua`는 현재 source에 없다. |
| `domains/layer3/product_projection.py` | `build_product`는 고정 `BINDING`으로 `expression.load(..., mode="adopted")`를 호출한다. `menu_projection`은 expanded block text를 합치고 `preserved_slots`/`tooltip_projection`은 Tooltip도 재구성한다. 새 corpus를 그대로 넣을 수 없다. |
| `domains/layer3/product_install.py` | `runtime_overlay`, `stage`, `promote`, `recover`가 있다. stage는 media/tools를 복사하고 product facade를 쓴다. promote에는 `IrisTooltipOwner.json`이 있는 대상에 대한 overwrite 방지가 있다. |
| `Iris/tools/Layer3PackageProjection.psm1`, `RuntimeLookupIndexIdentity.psm1`, `package_iris.ps1` | product descriptor, Tooltip owner, 선택 generation 및 package parity 경계가 이미 있다. C 후보에서도 이를 확장·재사용한다. |
| `Iris/build/description/v2/tests/test_layer3_product_integration.py` | `test_product_contract`가 이전 expression·통합 Tooltip·평탄화 Menu를 전제로 한다. 그대로 실행한 성공은 C 검증이 아니다. |

검토 후 추가 조사에서 `product_install.facades()`가 두 Tooltip Lua facade를 만들고 `stage()`가 `runtime_overlay()`의 파일을 복사한 media 위에 쓰는 것을 확인했다. 이 경로에는 accepted B component와의 byte identity admission이 없다. `promote`의 guard가 stage에도 적용된다고 간주하지 않으며 Change 4에서 직접 보호한다.

현재 필수 검증 목록은 `Iris/validation/execution/required_validations.json`이다. 여기에 `role=layer3_product_consumption`, `required=true`, `test_id=test_layer3_product_integration.test_product_contract`가 등록되어 있다. 검토안에서 지칭한 `_docs/round3/current_route_required_validations.json`은 historical 목록이며 현재 node의 membership 근거로 대체하지 않는다. 검사 수정은 Change 5의 assertion 처분 기준을 따른다.

표의 `Iris/...`는 `Iris/media/lua/client/Iris/`, `domains/`는 `Iris/tooling/src/iris_tooling/domains/`를 줄인 표기다.

`Base.Plank` KO expanded의 첫 설명과 “앞의 조건에서” 후속 segment, 복수 branch를 포함한 segment를 확인했다. 현재 segment에는 refs와 qualifier applications가 있으나 별도 명시적 predecessor segment 필드는 없다. 따라서 metadata 충분성은 **일부 구조 확인 / 전체 표시 계약 판정 전**이다. shared branch라는 이유만으로 모든 문장을 같은 의미로 합치거나 문장 검색으로 continuity를 결정하지 않는다.

`Base.Baseball`, `Base.Basketball`, `Base.BeerCanEmpty`는 acquisition-only 사례이고 `Base.BackgammonBoard`, `Base.Bag_PistolCase`, `Base.BathTowelWet`는 expanded absent 사례다. 이는 구조 검사 시작점이며 고정 수작업 분류표가 아니다.

### B 복원 기준

[B 최종 수락 기록](iris_tooltip_supply_closeout.md)의 기준을 사용한다. 작성 중 ZIP의 실제 SHA도 일치함을 확인했다.

- ZIP: `.tmp/tooltip/preview/Iris.zip`
- SHA-256: `33b5927127442b16dca917c6f49f3e661743123c0cbd3d5890d47cb6fca96860`
- product: `ttp-5a90c7d3844be93670e1b0f6c9f30db41bc0d17a026caf6f70bb797789ebc163`
- corpus: 위 `ba0fc047...`와 동일.
- B 수락 근거: 사용자 실제 PZ 확인 보고. 게임 버전·해상도·배율은 미제공이며 추정하지 않는다.

ZIP을 덮어쓰지 않는다. 내부 owner/descriptor와 Tooltip Lua member의 실제 binding 확인은 Change 1의 admission 작업으로 남는다. 기존 dirty/untracked/deleted 파일은 이 계획의 변경으로 간주하거나 정리하지 않는다.

## 5. Repository Areas Affected

아래는 향후 구현 영향 후보이며 모든 파일의 변경을 요구하지 않는다.

### Code

- `Iris/tooling/src/iris_tooling/domains/layer3/product_projection.py`, `product_install.py`: canonical 입력, 구조화 payload, B component와 공동 stage.
- `Iris/tooling/src/iris_tooling/domains/layer3/description_composition_results.py`, `description_composition_model.py`, `composition_results.py`: reader/구조 확인. 기존 의미를 운반하는 metadata가 정말 부족할 때만 제한적 조정 후보.
- `Iris/tooling/src/iris_tooling/domains/layer3/tooltip_s2_supply.py`, `domains/tooltip_t1/s2_candidate.py`, `domains/tooltip_static_data_projection/` 하위 projection/install: B binding과 재사용 경계 조사; B 정책 변경 대상은 아니다.
- `Iris/media/lua/client/Iris/Data/IrisLayer3DataLookup.lua`, `IrisLayer3EnglishLookup.lua`, `IrisLayer3DataChunks.lua`, `layer3_renderer.lua`.
- `Iris/media/lua/client/Iris/UI/Detail/IrisItemDetailModelAssembler.lua`, `IrisItemDetailViewModel.lua`, `IrisTextLayout.lua`.
- `Iris/media/lua/client/Iris/UI/Layer3/IrisLayer3DisplayFormatter.lua`, `UI/Wiki/IrisWikiSections.lua`, `IrisWikiPanel.lua`, `UI/Browser/IrisBrowserDetail.lua`.
- `Iris/tools/Layer3PackageProjection.psm1`, `RuntimeLookupIndexIdentity.psm1`, `package_iris.ps1`.
- 기존 검사 확장: `Iris/build/description/v2/tests/test_layer3_product_integration.py`, `Iris/tooling/tests/test_tooltip_t2_projection.py`, `Iris/test/lua/detail_view_model_locale_harness.lua`, `browser_state_acceptance_harness.lua`, `browser_interaction_density_acceptance_harness.lua`, `tooltip_static_data_runtime_harness.lua`.

### Docs

- 본 계획과 `docs/iris_layer3_product_walkthrough.md`: C source/consumer/projection 계약 및 current와 후보의 차이.
- 구현 종료 시 `docs/iris_dvf_expanded_menu_structuring_common_candidate_recovery_closeout.md` 작성 예정.
- `docs/iris_tooltip_supply_closeout.md`는 B 복원·수락 근거로 참조한다. 기존 이력을 다시 쓰지 않는다.
- `docs/DECISIONS.md`, `ARCHITECTURE.md`, `ROADMAP.md`는 실제 결정·구현 상태가 달라진 범위만 후속 반영한다.
- 후속 문서 정합화 대상에는 필수 검증 locator 차이도 포함한다. `DECISIONS.md`의 이전 governance 문구는 `current_route_required_validations.json`을 current-required binding surface로 지칭하지만, 같은 문서의 naming successor/정정과 실제 코드는 `Iris/validation/execution/required_validations.json`을 current로 사용한다. closeout에 이전 명칭 → naming successor → 실제 locator의 대응을 남기고 필요한 현재 안내만 보완한다. 봉인된 과거 기록·schema/프로토콜 이름을 소급 수정하거나 새 membership 변경으로 취급하지 않는다.

### Config

기본적으로 current authority/route/validation membership 변경은 없다. 기존 product schema나 package binding의 변화가 필요하면 해당 consumer/serializer와 함께 명시적으로 version 처리한다. 누락된 과거 contract 문서를 임의로 복원해 새 권위로 사용하지 않는다.

### Generated Artifacts

- canonical `descriptions.json`, `blocks.json`은 기본적으로 재사용하는 입력이다. C가 새로 유발한 단절·중복·누락은 우선 projection/UI에서 해결한다. 정확한 전달에 꼭 필요한 metadata 또는 source 표현 결함만 기존 공통 owner에서 최소 수정할 수 있다. 그때는 원본 수락 이력을 보존하고 영향 결과를 확인하며 B/C가 같은 새 입력을 사용하게 한다. 예정된 전수 설명 polish를 자동 편입하지 않는다.
- 저장소 `.tmp/menu/` 아래 신규 실행 폴더에 C product, 공동 stage, package `Iris/` 및 `Iris.zip`, 기존 도구의 manifest/identity 출력.
- 후보의 `IrisLayer3ProductGenerations/<product-id>/`, index/descriptor/chunks, compatibility facade와 package identity.
- 후보 내부 `IrisLayer3ProductCurrent.lua`와 `IrisLayer3DataCurrent.lua`, `IrisLayer3DataChunkIndex.lua`, `IrisLayer3DataChunks.lua` facade. product pointer → descriptor/index → C product ID의 실제 선택을 구성한다. source checkout의 동명 current 파일과 구분한다.
- 후보의 B `IrisTooltipStaticData.lua`, `IrisTooltipRecipeVariants.lua`, `IrisTooltipOwner.json` 및 수락 runtime component.
- 정확한 candidate/ZIP ID는 생성 후 기록한다. source current pointer와 기존 B ZIP은 수정하지 않는다.

## 6. Planned Changes

### Change 1 — 현재 소비 경로·후보 결속과 metadata 충분성 확정

**Purpose:** 교체 지점과 보존 경계를 실제 checkout 및 B ZIP에 결속한다.

**Files:** §4의 lookup/renderer/ViewModel/두 Menu consumer, product/package 도구, canonical 입력, B ZIP.

**Implementation Notes:**

1. 두 입력 SHA, reader 결과, exact FullType·locale·상태 분모를 기록한다. reader가 canonical 파일을 재생성하지 않게 한다.
2. B ZIP의 owner/product/corpus 및 실제 Lua member hash를 확인하고 현재 source runtime과의 차이를 식별한다. C stage가 어느 B component를 재사용하는지 명시한다.
   `stage/runtime_overlay/facades`의 쓰기 순서와 Tooltip owner 보호를 확인한다. 실제 require closure와 C 변경 closure를 대조해 B 고유 immutable component, 변경 없는 공유 component, C가 의도적으로 변경하는 공유 component로 구분하고 파일별 비교/검증 방식을 확정한다. 현재 확인된 보호 부재를 Change 4에서 보완하고 stage 완료 및 ZIP 인계 직전 모두 확정된 byte-preservation 대상의 accepted B byte identity를 강제한다.
   정상 실행에서는 기존 stage/package 검사 안에서 accepted B와 보존 대상 결과의 raw bytes 일치를 확인하고 같은 결과를 공유한다. 모든 중간 복사 경계의 hash·BOM·EOL 표나 별도 사전 조사는 만들지 않는다. 실제 불일치가 생겼을 때만 해당 복사/overlay/package 경계를 좁혀 원인을 조사한다. EOL-only 차이도 보존 성공이 아니며, 정규화 비교는 원인 분류에만 사용한다. 원본 bytes를 보존하는 복사 경로를 고치고 owner/hash를 바꿔 불일치를 숨기지 않는다.
3. Browser와 Wiki, KO와 EN, generation과 product 분기를 구분한 source → product → lookup → 화면 경로를 작성한다.
4. 단일/복수 용도, multi-branch, 선행 의존, acquisition-only, absent, long detail, unresolved 사례를 구조에서 선택한다. source segment 순서와 refs/qualifier scope/relations/detail link의 실제 해석 가능 범위를 판정한다.
5. metadata로 증명되는 관계만 presentation으로 옮긴다. 부족하면 기존 관계 운반용 최소 sidecar/projection metadata를 우선 검토하고, 새로운 semantic 판단이 필요한 사례는 해당 owner의 미해결 작업으로 분리한다. UI 추측으로 통과시키지 않는다.
   grouping 근거가 부족한 범위의 기본 표시는 새 group/heading/독립 접기를 만들지 않는 원본 segment 순서의 연속 표시다. 이는 predecessor 데이터 fallback이 아니다. 이 기본값으로도 안전한 연결이 안 되면 허용된 최소 metadata/owner 수정부터 진행한다. 실제 관계 근거·입력·도구 부재로 진행할 수 없는 범위만 blocked로 남기며, 모든 독립 용도까지 장문으로 합쳐 전체 구조화 요건을 회피하지 않는다.

**Validation:** reader와 SHA 일치, 두 Menu call chain, B package binding, source current 보존, 관계별 충분성 근거 및 남은 gap 목록.

### Change 2 — Expanded display/product projection

**Purpose:** Lua가 관계를 재추론하지 않고 소비할 deterministic 표시 계약을 만든다.

**Files:** `product_projection.py`, 필요한 serializer/내부 schema 및 기존 product 검사. metadata 운반 변경이 필요하면 Change 1의 근거를 먼저 기록한다.

**Implementation Notes:**

- 새 reader를 사용하는 명시적 candidate 경로를 둔다. 기존 `expression.load/BINDING`을 조용히 새 canonical로 간주하거나 예전 `expanded` 배열 형식을 강제하지 않는다.
- exact item/locale, state/reason, 원문 text와 ordered segments, block/branch/fact/qualifier/relation refs, unresolved, compact detail link destination, source identity를 보존한다.
- 표시 단위는 원본 segment 위치와 연결된다. source의 0-based `detail_links[].segment`와 Lua 1-based 배열 변환을 명시적으로 관리하고, 하나의 segment가 여러 branch를 포함해도 문장을 복제하거나 절단하지 않는다.
- 연속성과 독립성이 확인된 범위에서 group 및 순서를 offline으로 확정한다. dependent segment와 선행 설명은 하나의 visibility 단위로 읽히게 한다. 구체 필드명은 충분성 판정 후 고정하며 section 수/카드 종류를 미리 강제하지 않는다.
- exact 원문과 debug trace는 유지하되 fact ID/profile/provenance를 사용자 제목·본문으로 노출하지 않는다. 일반 UI label은 표시 책임이며 새 설명을 생성하지 않는다.
- 전체 block/branch/fact/qualifier/relation 연결은 offline conservation/debug trace에 둔다. Lua에는 원문, 상태, 표시 단위 순서 및 visibility 재현에 필요한 최소 identity/relationship metadata만 보낸다. offline trace와 runtime unit의 대응은 검증 가능하게 유지한다.
- source absent와 malformed/failed를 별도 상태로 보존한다. 선택적 `qualifier_dispositions` 등은 현재 reader 계약에 따라 처리하며 생략을 오류로 만들지 않는다.
- acquisition-only는 compact가 없어도 투영한다. KO/EN fallback, 대표 용도 선정, 임의 truncation은 없다.
- 이전 product의 `preserved_slots/tooltip_projection`을 C 생성에 그대로 호출하지 않는다. B component 보존/공동 binding은 Change 4에서 다룬다.

**Validation:** 4,210 상태 전수 conservation, 추가/누락/중복/순서 변경 검출, refs와 detail link 도착점, qualifier scope 비확대, unresolved 비확정, generation/serialization byte 결정성.

### Change 3 — Lua lookup과 두 Menu의 구조화 표시

**Purpose:** 현재 문자열 경계를 구조화 표시 모델로 연결하고 실제 정보 접근을 보존한다.

**Files:** Layer3 lookup/renderer, Detail assembler/ViewModel, formatter, WikiSections/WikiPanel, BrowserDetail, 필요 시 TextLayout.

**Implementation Notes:**

- 내부 구조화 lookup API를 추가하거나 명시적으로 version 처리한다. public facade의 기존 signature/result shape는 유지하고, 기존 문자열 API가 필요해도 새 구조를 다시 추론하는 입력으로 사용하지 않는다.
- `IrisLayer3DataChunks`는 기존 봉인 계약의 stable public facade 보존 대상이다. candidate의 pointer/schema 전환을 지원하더라도 전체 exact FullType table과 `IrisLayer3Data` 공개 경계의 관찰 가능한 계약을 유지한다. 내부 schema가 바뀐다는 이유로 facade의 보호 검사를 제거하지 않는다.
- `available/adoptionState/raw/display`로만 축약되던 내부 경계에서 normal absent와 payload fault를 구분해 전달한다. UI에는 잘못된 설명을 표시하지 않되 fault를 정상 침묵으로 집계하지 않는다.
- product identity/index/member/schema/locale 불일치에는 stale global/generation/다른 locale fallback을 하지 않는다. exact FullType와 KO/EN precompiled payload만 사용한다.
- C 경로는 `Formatter.format`의 문장부호 분할을 grouping 근거로 사용하지 않는다. 실제 폰트 wrap, 간격, heading, scroll은 presentation에서 처리한다.
- Browser와 Wiki가 같은 구조 모델을 사용하되 각 화면의 높이/child positioning/scroll 접근을 확인한다. 접기를 도입한다면 선행·후속 전체에 같은 visibility를 적용한다.
- item/locale/재개방 및 필요한 product identity 변화에 맞춰 model/layout state를 갱신한다. 오래된 text, 선택 상태, scroll offset이 잘못 재사용되지 않게 한다.
- Layer 2 및 기존 interaction/evolvedRecipe state의 병합 경계를 유지한다. Tooltip S4 하나의 선택 결과로 Menu 전체 L4 목록을 대체하지 않는다.
- 기존 readonly ViewModel과 facade의 객체/복사 동작은 변경 필요가 입증되지 않는 한 보존한다. 이를 새로운 전역 정책으로 확대하지 않는다.

**Validation:** 기존 Lua/UI harness에서 구조·순서·상태·visibility·scroll reachability·두 consumer·locale/item reset·L2/L4 공존을 검사한다. 모델 검사를 실제 폰트의 가독성 증거로 사용하지 않는다.

### Change 4 — B/C 공동 candidate와 package/install 경계

**Purpose:** 동일 corpus의 B Tooltip과 C Menu가 하나의 설치 가능한 후보에 들어가도록 한다.

**Files:** product_install, B install/binding 경로, 세 PowerShell package/identity 도구, 기존 통합 검사.

**Implementation Notes:**

- B 수락 ZIP/component의 bytes와 provenance를 기준으로 재사용한다. B 고유 immutable component에 대해 accepted ZIP → stage → final ZIP의 **byte-identical**을 fail-closed admission 조건으로 강제한다. 최소 대상은 `IrisTooltipStaticData.lua`, `IrisTooltipRecipeVariants.lua`, `IrisTooltipOwner.json`이다. 실제 수락 runtime과 require closure도 목록화하되 파일별 B/C ownership·변경 이유·검증 방식을 붙인다. 동일 corpus SHA나 정규화된 텍스트 equality로 byte 검사를 대체하지 않는다.
- 변경 없는 공유 component도 byte-preservation 대상에 넣는다. C가 의도적으로 수정해야 하는 공유 runtime file은 predecessor bytes로 되돌리도록 강제하지 않는다. 해당 파일을 의도적 변경 대상으로 명시하고 변경 전후 hash, C 변경 필요성, B에 미치는 영향과 focused regression/PZ 관찰 근거로 검증한다. 이렇게 분류한 파일은 byte-preservation 성공에 포함하지 않는다. 분류되지 않은 mismatch는 거부하며, B 고유 세 artifact의 drift를 공유 파일 변경으로 재분류해 숨기지 않는다.
- stage가 C overlay를 모두 쓴 직후 비교하고, final ZIP의 실제 member bytes도 다시 비교한다. mismatch/누락/owner 불일치이면 후보를 거부하고 인계하지 않는다. 이전 facade로 덮어쓴 뒤 성공으로 기록하거나 owner hash를 새로 써서 불일치를 숨기지 않는다.
- B 재생성/수정이 필요하면 byte 재사용 성공으로 처리하지 않는다. 변경 이유·실제 B 영향을 기록하고 §7의 조건부 최소 회귀로 확인한다. C 통합 검사에 이미 포함된 확인은 반복하지 않는다. 기존 수락 ZIP을 보존하며 변경된 B component의 근거 없이 공동 후보 완료로 닫지 않는다.
- B corpus SHA와 C source SHA 일치를 stage/package admission 조건으로 삼는다. member를 모아 놓았다는 사실만으로 공동 candidate라고 부르지 않는다.
- B owner guard를 삭제해 통합하지 않는다. 기존 unified product descriptor가 Tooltip까지 소유하는 부분과 별도 Tooltip successor binding의 충돌을 명시적으로 해소하고 기존 hash/lock/drift 검사를 유지한다.
- 후보 overlay는 `.tmp/menu/` 내 신규 위치에만 쓴다. source current 전환용 `promote`는 호출하지 않는다.
- candidate 내부 `IrisLayer3ProductCurrent.lua`는 C product ID와 descriptor를 선택하고, `IrisLayer3DataCurrent.lua`는 product compatibility schema를 통해 같은 ID/index/chunks를 반환해야 한다. 현재 구현의 schema는 각각 `iris_layer3_product_pointer_v1`, `iris_layer3_product_compat_v1`이며 C에서 version을 바꾸면 producer/lookup/package 기대를 함께 갱신한다. candidate 내부 선택은 필수이고 source current promotion과는 별개다.
- 인계 직전 final ZIP을 저장소 내부 신규 경로에 풀어 fresh Lua process에서 실제 pointer → descriptor → index → lookup을 호출한다. KO/EN 결과의 product ID가 C manifest ID와 일치하고 Browser/Wiki 공통 모델이 이 payload를 소비하는지 확인한다. C 파일 존재나 pointer 문자열 검색만으로 통과시키지 않는다. predecessor 선택 및 pointer/descriptor 불일치 fixture는 거부되어야 한다.
- 패키저가 선택한 C generation과 B owner/runtime만 포함하는지 actual ZIP을 검사한다. 다른 generation, stale EN, predecessor Tooltip 또는 혼합 descriptor는 거부한다.
- 기존 stage/recover 패턴으로 후보 복원·중단 복구를 검증한다. live current promotion 성공을 주장하지 않는다.

**Validation:** same-corpus binding, B S1~S4/Alt/opening 보존, Menu L2/L4 보존, selected generation/member parity, package lookup smoke, writer lock·drift·오염 거부 및 격리 복원.

### Change 5 — 변경 범위 자동 통합 검사

**Purpose:** 실제 게임 인계 전에 데이터 손실·구조 결함·후보 혼합을 제거한다.

**Files:** 기존 product contract와 관련 B/Lua harness. 새 검사 framework나 정규 validation membership은 만들지 않는다.

**Implementation Notes:** §7의 검증을 실제 변경 범위로 묶는다. B 전체 producer를 매 검사마다 반복하지 않고 같은 후보를 재사용한다. 실패/수정이 있으면 영향 범위만 다시 확인하고 서로 다른 후보 결과를 합산하지 않는다.

실제 변경에 적용되는 current required-validation membership을 관련 부분만 확인한다. 기존 보호 목적은 유지하되 모든 assertion/negative case의 전후 inventory·처분표는 만들지 않는다. 변경하지 않은 검사는 기존 코드와 실행 결과를 재사용한다.

기록은 다음 경우에만 기존 closeout에 간결하게 남긴다.
- 의미가 달라진 기대값: 옛 수치·평탄화 배열 등을 무엇으로 교체했으며 같은 보호 목적을 어떻게 확인하는지.
- 삭제·이동한 보호 검사: 사유, 보호를 유지하는 실제 node/실행 경로와 실행 결과.
- required membership/실행 경로 변경: 실제 축소 여부와 영향. 일회 실행으로 이후 정규 보호 유지까지 주장하지 않는다.

기존 conservation·FullType/locale·member integrity·stable facade·경로 경계·pointer 보존·중단 복구/idempotence는 제품 형태가 바뀌어도 필요한 보호다. 옛 숫자를 없애면서 coverage를 없애거나 current 비활성화를 이유로 기존 격리 promote/recover 보호를 삭제하지 않는다. 기존 required 경로 안에서 유지하는 것을 기본으로 하고, 필요한 이전 검사는 같은 최종 묶음에서 실행한다. 이 확인을 새 검증 authority나 별도 승인 Gate로 만들지 않는다.

**Validation:** 최종 exact candidate의 명령/exit code/대상 identity/검증 한계를 기록한다. 성공한 자동 검사만으로 실제 Menu 성공을 선언하지 않는다.

### Change 6 — 실제 PZ 관찰과 후보 closeout

**Purpose:** 같은 후보의 실제 화면 가독성과 접근성을 확인하고 후속 상태를 분리한다.

**Files:** 검증된 후보 ZIP, product walkthrough, 예정 closeout 문서.

**Implementation Notes:** 고정 표본 수 대신 §7의 위험 유형을 Browser/Wiki와 KO/EN에서 확인한다. 관찰을 위해 이유 없이 후보를 다시 생성하지 않는다. defect 수정 시 corrected candidate identity와 재검사 범위를 기록한다. §12의 C 범위 완료 조건으로 상태를 선택하고 current/finalization/release는 별도 미수행 상태로 기록한다.

**Validation:** 사용자/실제 관찰 보고의 출처, candidate, locale, 위험 유형, defect/correction, 미관찰 범위를 함께 남긴다. 환경 수치가 없으면 미제공으로 기록한다.

## 7. Validation Plan

실행 변경의 검증 깊이는 **heavy**다. 이는 공개 표시·product 통합에 필요한 증거를 뜻하며 전체 historical suite 반복을 의미하지 않는다. 모든 machine/automated PASS는 실행한 exact command의 exit `0`과 대상 identity에 귀속한다. actual PZ evidence는 candidate identity·관찰 주체·범위·결과로 별도 기록한다. 필요한 `uv`, Python, pytest, PowerShell, Lua/문법 검사 도구가 없으면 해당 검증은 `BLOCKED`다.

### Automated Validation

| 검증 영역 | 필수 확인 |
|---|---|
| 입력 | 두 SHA, schema/version, reader 정상 반환, 2,105 exact IDs, KO/EN, 4,210 상태 및 59/62 구분 |
| conservation | 모든 present의 text/segment 순서와 coverage, 추가·누락·중복 없음, refs 해소, scope 비확대, unresolved 비확정 |
| projection | 원본 segment → display unit 전수 대응, 순서/continuity metadata, detail link destination, optional field 생략. payload 보존을 화면 접근성으로 주장하지 않음 |
| Lua | exact FullType, locale, normal absent/fault 구별, invalid schema/index/member/locale, predecessor fallback 부재 |
| 화면 모델 | Browser/Wiki, dependency visibility, 독립 용도 구별, content height, 모든 표시 단위와 scroll 끝 도달, 접기 도입 시 dependency, item/locale/재개방 stale-state |
| 회귀 | B S1~S4·Alt·opening, L2, Recipe/Right-click/EvolvedRecipe 전체 Menu 접근 |
| package/install | B/C 동일 corpus, 확정된 보존 대상의 accepted B → stage → ZIP raw byte identity와 실제 불일치 때만 복사/EOL 진단, 의도적 공유 component 변경의 필요한 회귀 근거, actual ZIP pointer/descriptor/index/lookup의 C product ID 일치, 혼합·source drift·lock 거부, 후보 복원 |
| 보호 검사 변경 | 실제 바뀐 기대값·삭제/이전된 보호·required 실행 경로 변경만 기록. 변경 없는 assertion은 재문서화하지 않고 기존 검사를 공유 |
| 결정성 | 직렬화·product ID가 바뀌는 이번 C 통합 검사 안에서 같은 입력의 필요한 두 생성 결과를 공유해 비교. 별도 결정성 Gate나 두 번의 전체 suite/ZIP 생산을 추가하지 않음 |

계획된 집중 실행 명령은 PZ 루트의 PowerShell 기준이다. 아래는 **기존 node/harness를 C 계약에 맞춰 확장한 후의 실행 형태**이며 지금 이 명령을 실행하면 C 검증이 완성된다는 뜻이 아니다. 아직 없는 C CLI 옵션을 가정하지 않는다.

```powershell
uv run --project .\Iris\tooling python -I -B -m pytest --noconftest -c .\Iris\tooling\pyproject.toml .\Iris\build\description\v2\tests\test_layer3_product_integration.py::test_product_contract --basetemp .\.tmp\menu\accept -q -s
```

B 회귀는 파일이 require closure에 속한다는 사실만으로 추가하지 않고 실제 변경 동작과 C 통합 검사의 coverage로 결정한다. B 고유 artifact와 변경 없는 runtime은 accepted B → stage → final ZIP의 원본 byte 보존을 기존 검사에서 확인한다. 의도적으로 바뀐 공유 파일은 보존 성공에서 제외하고 실제 B 영향을 확인한다.

공유 runtime을 바꿨어도 필요한 B 동작이 C 통합/Lua 검사에 포함되면 그 결과를 재사용한다. B producer·선택·표시·설치 동작이 바뀌고 C 검사에 필요한 보호가 없으면 우선 기존 focused 반례를 같은 C 묶음에 통합한다. 전체 공급/조립 경로 확인이 필요한 경우에만 기존 test_tooltip_t2_projection.py::test_s2_supply_and_owner_integration을 위 pytest 대상 목록에 추가한다. B 통합 node와 별도 focused 검사를 자동으로 둘 다 실행하거나 별도 b-regression workspace를 만들지 않는다. 실제 적용되는 기존 필수 검사는 우회하지 않는다.

공통 composition owner를 실제 수정한 경우에는 영향 결과의 원문을 다시 읽고 기존 test_layer3_description_composition.py 등 변경 owner의 필요한 기존 검사만 같은 최종 호출에 추가한다. 입력을 읽기만 한 경우 문제 1~3 재수락은 하지 않는다.

Lua 변경의 필수 문법 검사는 tools/check_lua_syntax.ps1이다. 아래 자식 실행으로 변경된 source와 후보 Lua 범위를 함께 확인하면 별도 동일 검사를 다시 실행하지 않는다.

후보 내부 검사는 위 product node에서 실제 stage 경로를 인수로 기존 Lua harness와 패키저를 호출해 묶는다. 각 자식 명령의 실패를 부모 실패로 전파하고 `input`, `conservation`, `stage-b-identity`, `lua-model`, `package`, `zip-c-pointer`, `recovery` 등의 named checkpoint 또는 동등한 기존 로그로 실패 단계·exact command·exit code·candidate ID를 보존한다. 부모 실패 한 줄로 원인을 덮지 않는다. 명령 예시는 아래와 같고 `$cStage`는 실제 신규 stage 위치로 결속한다.

```powershell
$cStage = '<실제 .tmp/menu 하위 stage 절대 경로>'
powershell -ExecutionPolicy Bypass -Command '& .\tools\check_lua_syntax.ps1 -Roots @("Iris/media/lua", "<실제 후보 Iris/media/lua의 저장소 상대 경로>")'
lua .\Iris\test\lua\detail_view_model_locale_harness.lua $cStage
powershell -ExecutionPolicy Bypass -File "$cStage/Iris/tools/package_iris.ps1" -OutputRoot "$cStage/.tmp/package" -Zip
```

stage와 basetemp는 기존 실행 산출물을 덮어쓰지 않는 경로로 선택한다. 기존 harness가 fixture/stub만 검사하는 부분과 actual product를 읽는 부분을 구별하고 C 통합 node가 실제 payload readback도 담당하도록 확장한다. Java/Gradle 및 JS/TS 변경은 예정하지 않으므로 `gradlew test`/`pnpm biome check .`는 본 변경의 필수 검사로 추가하지 않는다.

자동 테스트는 위 최소 통합 묶음을 마지막에 수행한다. 원문 읽기·실제 필요한 생성·차이 확인은 구현 중 가능하지만 계획에 없는 중간 테스트를 추가하지 않는다. 실패 수정이나 후속 코드 변경으로 기존 근거가 무효화된 경우에만 필요한 범위를 다시 실행한다. 30~60초 간격으로 프로세스 상태·출력·진행을 확인하고 무한 반복·진행 정체·비정상 장기 실행이면 해당 프로세스를 중단한다. 원인 확인 없이 재시도를 반복하거나 시간 초과를 PASS로 처리하지 않는다.

같은 input/producer/execution boundary의 검사와 산출물은 공유하며 checkpoint마다 디렉터리·receipt를 추가하지 않는다. 외부 reviewer가 필요하면 Codex Reviewer를 사용하되 별도 독립 검토는 기본 Gate가 아니다. 문서상 owner approval은 사용자의 사전 승인으로 처리하며 도구·플랫폼 자체의 별도 권한 확인은 우회하지 않는다.

### Manual Validation

최종 자동 검사를 통과한 **동일 ZIP**에서 다음을 확인한다.

- 단일 용도는 과도하게 분절되지 않고, 복수 용도는 구별된다.
- `Base.Plank` 같은 선행 조건/후속 설명은 순서와 적용 관계를 유지한다. multi-branch와 qualifier가 많은 항목의 조건이 다른 용도에 붙어 보이지 않는다.
- acquisition-only는 compact 없이도 expanded가 표시된다. expanded absent에서는 Layer 3만 없고 기존 L2/L4 정보는 그대로 접근 가능하다.
- 긴 KO/EN, 좁은 표시 폭, section 경계, 스크롤 끝에서 잘림·겹침·영구 접근 불가가 없다.
- L4가 많은 항목에서 Recipe / Right-click / EvolvedRecipe 접근을 막지 않는다.
- Browser와 우클릭 Wiki, item 변경, locale 변경 후 재구성, 닫기/재열기의 stale text/state를 확인한다.
- 같은 후보에서 B의 Alt/opening과 S1~S4를 확인한다. C가 건드린 경로의 회귀 관찰이며 B 전체 수락의 반복이 아니다.

candidate/ZIP SHA, 관찰 주체, locale, 위험 유형, 결과, 수정·재관찰 범위를 기록한다. 실제 게임 버전·해상도·UI scale·폰트는 제공된 값만 기록한다.

### Validation Limits

다음 분류를 closeout 전에 고정한다. `unvalidated_but_in_scope` 항목은 이 계획의 필수 검증을 수행하고 근거를 확보하면 `validated`로 전환한다. 미실시를 이유로 closeout에서 임의로 `out_of_scope`로 바꾸지 않는다.

| 항목 | 사전 분류 | 완료 판정과 주장 경계 |
|---|---|---|
| §7 Automated Validation의 C 입력·conservation·projection·Lua·회귀·package/install·보호 검사·product 결정성 | `unvalidated_but_in_scope` — 구현 검증 전 | 조건부 검사는 실제 변경 closure로 적용 여부를 정하고 이유를 기록. 적용되는 필수 검증을 마쳐야 complete 가능 |
| §7 Manual Validation의 위험 유형별 KO/EN Browser/Wiki 및 동일 후보 B 공존 관찰 | `unvalidated_but_in_scope` — 실제 관찰 전 | 계획된 위험 유형과 두 consumer를 관찰하고 blocking defect를 해결해야 함. source/ref equality는 대체 증거가 아님 |
| 4,086 present 전수 인간 품질 검수, 2,105 items 전수 실제 게임 열람 | `out_of_scope` | 전수 자동 conservation과 위험 유형별 실제 관찰이 본 계획의 범위. 전수 게임 열람 미실시는 C complete를 막지 않음 |
| 멀티플레이·장시간 세션·모든 게임 버전/해상도/배율/폰트·외부 모드 전수 호환 | `out_of_scope` | 실제 관찰 환경과 유형에 한해 기록하며 전체 환경 보장으로 확대하지 않음 |
| unresolved 의미의 신규 해결, 후속 prose polish | `out_of_scope` | 기존 unresolved 상태와 문장의 올바른 전달은 C 범위 안이며 근거 부족으로 표시가 막히면 그 C 결함은 범위 밖으로 돌리지 않음 |
| current production activation, strict production finalization, deployment/release | `out_of_scope` | 미수행을 별도 non-claim으로 기록. 후보 내부 C pointer 선택 검사는 범위 안 |
| 전체 Clean-Checkout A/B reproducibility | `out_of_scope` | C product 두 생성의 byte 결정성은 범위 안. 그 결과를 전체 재현성 PASS로 명명하지 않음 |

### 계획 작성 시 실제 수행한 확인

2026-09-11 PowerShell에서 두 canonical 파일과 B ZIP의 `Get-FileHash -Algorithm SHA256` 결과를 §4와 대조했다. 아래 reader 호출은 **exit 0**이며 schema `iris-layer3-descriptions-v1`, version `1`, items `2105`, expanded `present=4086 / absent=124`를 반환했다. failed 항목은 없었다.

```powershell
uv run --project .\Iris\tooling python -I -B -c 'from pathlib import Path; from collections import Counter; from iris_tooling.domains.layer3.description_composition_results import read_result; d=read_result(Path.cwd()); c=Counter(x["locales"][l]["expanded"]["state"] for x in d["items"] for l in ("ko","en")); print({"schema":d["schema"],"version":d["version"],"items":len(d["items"]),"expanded":dict(c)}); print({"item_fields":list(d["items"][0])})'
```

이는 입력 readback과 계획 근거 조사다. 위에 제시한 향후 C 통합·Lua syntax·package·게임 검사를 실행한 결과가 아니다.

## 8. Risk Surface Touch

### Authority Surface

semantic/expression authority는 composition owner에 남는다. DVF-L3-06 product projection/install/consumption 경계는 변경 가능하다. 표시 metadata를 새 qualifier/relation 의미 결정이나 description writer로 승격하지 않는다.

### Runtime Behavior Surface

Menu의 데이터 입력과 구조 표시, 상태/fault 전달, locale/item 전환, 높이·스크롤이 바뀐다. Tooltip은 B 수락 동작 보존 대상이며 역할 정책을 C로 옮기지 않는다.

### Compatibility Surface

내부 product schema, lookup payload, package member/binding에 영향이 있다. 기존 지원 public facade 및 Layer 2/4 소비 계약은 유지한다. unsupported/malformed를 compatibility fallback으로 감추지 않는다.

### Sealed Artifact Surface

검수 corpus, adopted 역사, predecessor, B 수락 ZIP은 보존한다. 새 후보를 만들 뿐 current sealed pointer를 즉시 교체하지 않는다. canonical metadata 변경이 필요하면 원본 수정과 새로운 후보 identity의 관계를 먼저 명시한다.

### Public-Facing Output Surface

Menu Layer 3 원문 source와 배치·구조가 바뀐다. 실제 화면 관찰이 필수이며 debug refs를 사용자 본문에 노출하지 않는다.

## 9. Risk Analysis

### Architecture Risk

- shared branch/ref를 근거 이상으로 해석해 presentation이 semantic owner가 될 수 있다. 구조 충분성 판정과 unresolved 보존으로 제한한다.
- 기존 integrated writer를 재사용하면서 B S3/S4가 historical mapping으로 돌아갈 수 있다. C projection과 B component 보존 경계를 분리해 검사한다.
- 옛 문서/contract locator 또는 generation을 current로 오인할 수 있다. actual pointer와 candidate binding을 기준으로 삼는다.

### Runtime Risk

- 선행 설명을 접고 후속 설명만 표시하거나 순서를 바꾸면 원문이 같아도 의미가 달라진다. dependency visibility 단위를 검증한다.
- long text와 L4 증가로 계산된 높이 밖에 내용이 남을 수 있다. 두 consumer의 최종 row 접근을 검사한다.
- Lua의 nil/optional 처리, readonly 배열, locale cache로 부재/오류 또는 stale text가 섞일 수 있다. 유효 payload와 손상 fixture를 분리한다.

### Compatibility Risk

- 기존 facade 문자열 계약을 구조 객체로 대체하면 다른 consumer가 깨질 수 있다. 내부 additive 경로와 public 계약을 구분한다.
- product descriptor와 Tooltip owner의 결속이 충돌할 수 있다. lock/hash 검사를 우회하지 않고 공동 candidate admission을 명시한다.
- candidate failure가 predecessor fallback을 통해 다른 corpus를 보여줄 수 있다. 오류 상태와 fallback 부재를 actual lookup에서 확인한다.

### Regression Risk

- acquisition-only 59개를 compact visibility로 숨기거나 absent 62개를 오류로 취급할 수 있다.
- C 구조가 L2/L4 순서·탐색·높이에 영향을 주거나 Tooltip 한 후보로 Menu 목록을 축소할 수 있다.
- source와 ZIP member가 달라 검사한 것과 다른 후보를 인계할 수 있다. exact ZIP과 input/product/component identity를 함께 기록한다.

## 10. Rollback Plan

1. 실행 전 source pointer bytes/hash, B 수락 ZIP, 후보 입력과 수정 파일 범위를 기록한다. 현재 사용자의 dirty/deleted/untracked 상태를 복원 대상으로 오인하지 않는다.
2. projection 결함이면 해당 C 후보를 사용하지 않고 projection만 수정한다. canonical 원문은 손대지 않는다.
3. Lua 표시 결함이면 변경한 renderer/ViewModel/consumer 범위만 되돌리거나 수정한다. 수정된 bytes는 새 candidate로 식별하고 관련 검사를 다시 수행한다.
4. B 회귀이면 §4의 수락 ZIP/component와 owner binding으로 후보 B 부분을 복원하고 공동 corpus/member consistency를 재확인한다. 검증되지 않은 임의 혼합 ZIP을 전달하지 않는다.
5. source 표현 결함이면 composition owner로 최소 환류한다. UI/FullType별 replacement로 숨기지 않는다. corpus가 바뀌면 C projection과 관련 Menu, compact에 영향이 있을 경우 B 해당 surface도 재확인한다.
6. 격리 install 중단은 기존 journal/recover 흐름을 이용해 before 상태를 복원한다. source current는 전환하지 않았으므로 이 계획에서 live rollback 성공을 주장하지 않는다.

`git reset --hard`, 광범위 삭제, 기존 B ZIP 덮어쓰기를 rollback으로 사용하지 않는다. 후보 파일의 제거가 필요하면 실제 절대 경로가 의도한 `.tmp/menu/` 실행 폴더 안인지 먼저 확인한다.

## 11. Governance Constraints

- [Philosophy.md](Philosophy.md)를 최상위 설계 권위로 적용한다. Iris는 근거 기반·중립적 정보만 표시하며 근거가 없으면 침묵한다.
- PZ runtime은 100% Lua다. Pulse 역의존, spoke 간 직접 의존, 게임 상태 변경을 추가하지 않는다.
- Menu와 Tooltip은 같은 사실을 다른 깊이로 제공한다. Recipe와 Right-click은 독립적이고 동등한 관점이며 어느 한쪽을 Layer 3나 다른 관점의 하위 체계로 흡수하지 않는다.
- [DECISIONS.md](DECISIONS.md)의 DVF-COMPOSITION-3/B 수락 경계와 [EXECUTION_CONTRACT.md](EXECUTION_CONTRACT.md)의 claim-evidence/validation ceiling 구분을 적용한다.
- 기존 source/authority/readpoint와 새로운 candidate를 구분하고, 표시 metadata는 의미 authority 변경 없이 최소 범위로 추가한다.
- 기존 검증 framework를 사용하며 heavy라는 이유만으로 전체 재검사·새 seal·새 외부 workspace를 요구하지 않는다.
- 로드맵 Appendix A-5의 보류 사항은 새 전역 제약으로 승격하지 않는다. 본 계획은 현재 checkout 내부 후보 실행과 기존 객체 계약 보존을 기본 선택으로 삼는다. 별도 독립 reviewer/subagent 실행은 예정하지 않는다.
- 이번 요청의 산출물은 계획 문서다. 문서 작성 자체를 C 구현·게임 관찰·활성화 권한이나 완료 증거로 해석하지 않는다.

## 12. Expected Closeout State

검토 R-1을 반영해 이 계획의 목표 terminal state를 **`complete` — C 후보 구현·동일 corpus B/C 통합·자동 검증·실제 Menu 관찰 범위**로 확정한다. 원 로드맵 A-6의 별도 명명 판정을 추가 완료 gate로 두지 않는다. current 공동 활성화·strict finalization·release는 §2의 범위 밖이며 수행하지 않아도 아래 C 완료 조건을 충족할 수 있다.

**N2-5 원문 대조:** 사용자 제공 원 로드맵 v3의 Appendix A-6 전체를 확인했다. 원문에는 “이 충돌은 종합 과정에서 임의로 결정하지 않는다”와 “판정 전까지 본 로드맵은 … 별도 상태로 기록하는 데까지만 확정한다”라는 보류가 실제로 있다. 따라서 원 로드맵 자체가 판정안 A를 이미 확정했다고 읽지 않는다. 반면 “파생 계획은 별도 판정 전까지 terminal state를 확정하지 않는다” 또는 그에 해당하는 명시적인 파생 계획 금지 조항은 없다. 본 계획은 검토 반영 시 R-1을 채택한 판단으로 판정안 A에 해당하는 C 범위를 직접 정의한 것이며, 원 로드맵의 합의나 검토자 전원 승인으로 소급하지 않는다. N2-5의 조건부 우려 중 명시적 파생 계획 구속 조항의 존재 여부는 이 원문 대조로 닫고 현재 상태 정의를 유지한다. §7의 사전 ceiling 분류에 따라 완료 여부를 판정한다.

| 상태 | 선택 조건 |
|---|---|
| `complete` | C 구현, same-corpus B/C 통합, 필요한 자동 검증, 같은 exact candidate의 실제 PZ Menu 관찰을 마쳤고 C 범위 blocking defect 및 `unvalidated_but_in_scope`가 없음 |
| `implemented_only` | 구현·통합·필요한 자동 검증을 마쳤지만 실제 PZ 관찰이 미실시/미완료임. 관찰 범위는 `unvalidated_but_in_scope`로 남김 |
| `partial` | C 구현·통합·필수 검사 또는 관찰 후 correction 일부가 미완료이며 계속 진행 가능한 상태 |
| `blocked` | 필요한 입력·도구·관계 근거·실행 경로 부재로 해당 필수 작업을 진행할 수 없음. 원인과 재개 조건 및 이미 수행한 범위를 기록 |

실제 PZ 관찰을 단순 수행했다는 사실만으로 complete가 되지 않는다. 발견된 blocking defect를 수정하고 corrected exact candidate에 필요한 재검증·재관찰을 닫아야 한다. 근거 부족이나 payload fault를 정상 absent로 처리하지 않는다. 상태와 함께 다음 독립 축을 기록한다.

| 상태 축 | closeout에 남길 내용 |
|---|---|
| C candidate implementation | 구현 여부, exact input/product/ZIP identity |
| B/C integration | B 수락 component relation, corpus SHA 일치, assembly 검증 |
| Automated validation | exact 명령, exit code, 대상 identity, 실패/수정 이력 |
| Actual PZ | 관찰 여부/주체/locale/위험 유형, defect와 corrected candidate, 미관찰 범위 |
| Current joint activation | 본 계획에서는 미수행; 현재 pointer 및 후속 전환 인계 |
| Strict production finalization | 본 계획에서는 미수행 |
| Release / deployment | 본 계획에서는 미수행 |
| C closeout state | 위 조건에 따라 `complete / implemented_only / partial / blocked`를 직접 선택 |

후속 closeout은 `validated`, `unvalidated_but_in_scope`, `out_of_scope`를 구분한다. 전수 인간 검수, 모든 환경 호환, 후속 표현 polish, release readiness로 결과를 확대하지 않는다. 이번 계획 작성의 완료와 향후 C 실행의 완료는 별도다.
