# Iris DVF 용도 설명 조사 보고서

2026-09-11 · 현재 checkout의 읽기 전용 조사와 보고서 작성. 구현·corpus 재생성·테스트·채택·상태 문서 변경은 수행하지 않았다. 기존 dirty/deleted/untracked 작업은 보존했다. 아래 예시는 교정 원칙을 설명하는 제안이며 생성·인게임 검증 완료 문안이 아니다.

## 판단

> 구현 단계의 근거 정정(2026-09-11): 아래 `scripts/recipes.txt:207`의 Make Pot of Soup 예시는 `:194`에서 시작하는 주석 구간에 들어 있다. 활성 미개봉 직접 조리 근거로 사용할 수 없다. 활성 TinnedBeans의 Make Bowl of Beans와 구분한다. 조사 당시 기록은 아래에 남기며, 이 정정은 보고서 전체를 구현 완료 기록으로 바꾸지 않는다.

핵심 결함은 **사실의 보존을 공개 문장 전량 출력으로 해석하는 것**이다. 양말의 세척 대상 사실, 세척 결과와 점화 절차는 근거가 있어도 양말의 용도가 되지는 않는다. 반대로 양말의 연료·불쏘시개 역할은 실제 용도이므로 남겨야 한다. 수동태를 능동형으로 바꾸거나 모든 대상 사실을 삭제하는 방식으로 해결할 수 없다.

현재 A의 source rule과 기능 키는 세척 대상/세척제, 불쏘시개/점화 도구를 상당 부분 구분한다. 문제 1은 그 사실과 관계를 보존한다. 문제 2가 이를 공개용 의미로 선택하지 않고 expanded에 거의 전량 문장화하고, 문제 3의 기존 수락 기준도 그 결과를 보존 대상으로 취급한다. 통조림에는 별도의 상류 정보 전달 결함이 있다. 개봉 결과와 도구를 원본에서 확인하지만 공개 조합 입력에 구체적인 관계·이름으로 전달하지 않는다.

판단 기준은 [Philosophy.md](Philosophy.md)의 근거 기반 게임 내 위키, 중립성, 같은 사실의 다른 깊이, Alt 최대 4줄과 이번 사용자 지시다. DVF는 L3 용도 설명을 맡는다. 멀티 프로필을 `primary_use` 하나로 환원하지 않는다. 메뉴는 용도 중심 확장 설명이며, 툴팁에서 빠진 절차의 수납처가 아니다.

## 읽은 범위와 한계

- 직접 출력 대조: `Socks_Ankle`, `Socks_Long`, `Soap2`, `CleaningLiquid2`, `Lighter`, `CannedCorn`, `CannedCornOpen`, `CannedBolognese`, `CannedSardines`, `CannedCornedBeef`, `TinnedBeans`, `TinOpener`, `Hammer`, `Notebook`. 특히 앞의 양말·비누·라이터·옥수수 사례는 blocks의 사실 키까지 추적했다.
- 데이터: `Iris/build/description/composition/{blocks,descriptions}.json`, r6 `semantic.json`. 큰 JSON은 PowerShell `ConvertFrom-Json`으로 파싱하여 필요한 item/field만 읽었다. 전체 item을 읽는 파싱 자체를 전면 품질 감사로 계산하지 않는다.
- 코드: A의 `recovery_sources.py`와 관련 migration 경계, 문제 1의 composition 모델·규칙, 문제 2의 planner/families/results/lexicon/model, 기존 문제 2 검사 중 보존 조건. 바닐라 scripts와 관련 세척·점화 Lua도 대조했다.
- 기존 문서: A·1·2 walkthrough, 문제 1 contract, 문제 3 plan/closeout 및 `docs/review/prose/review.json`의 검수 범위, B의 실제 Tooltip 표시 코드, C closeout·projection의 필요한 부분.
- 미확인: 나머지 item의 개별 문장 품질, 모든 역할 조합, 모든 영어 출력, 모든 점화 서버 경로의 재조사, 실제 PZ 폰트·해상도·UI scale, 외부 버전. 기존 미확정 native 효과와 실행 한계도 이번에 해소한 것으로 보지 않는다. 모드는 정규화 어댑터를 거쳐 유사 DVF/QG 입력이 된다는 전제를 따른다.

## 사례 추적

이하 코드 경로의 `layer3/`는 `Iris/tooling/src/iris_tooling/domains/layer3/`를 뜻한다. JSON 좌표는 `items[item_id=…]`로 표기한다. 해시형 ID는 해당 파일에서 항목을 찾는 좌표이며 새 증명 artifact가 아니다.

### 양말: 세척 대상은 세척 도구가 아니다

1. **원본 사실.** `scripts/clothing/clothing_shoes.txt:3,18`의 두 양말은 `Type=Clothing`, `BodyLocation=Socks`, `FabricType=Cotton`이다. `lua/client/TimedActions/ISWashClothing.lua:71`은 물 10단위, `:74` 이후는 `self.soaps` 사용, `:94` 이후는 `self.item`의 피·때 제거와 `setWetness(100)`, `:143`은 이동 중단을 기록한다. 처리 대상 item과 소모 세척제는 서로 다른 인자다.
2. **A 역할.** `layer3/recovery_sources.py:2718` 이후는 Clothing/Weapon/Container에 `wash_carried_equipment`를 `washing_target` rule로 부여한다. 옷에는 혈흔·때 제거와 젖음 결과가 붙는다. `Soap2`/`CleaningLiquid2`는 별도의 `washing_supplies` rule 아래 `wash_body`, `wash_equipment`를 얻는다(`:2730` 이후). 대상이라는 뜻은 rule/function에 남아 있으나, `direct_function` kind만으로는 행위 주체를 구분할 수 없다.
3. **문제 1 블록.** 양말 `block:875466eca2beb336d81d257e4a5656a691ae0487a76fc23961ceddad4bf41d6d`에는 세척 대상 기능과 세 결과가 들어간다. `wash_carried_equipment`의 실제 fact는 `fact:7dc32ef5b0f00c158983cd979a932f9e6ba9449b743d0dc5b93a48e86cc51872`다. r6에서도 같은 ID와 `admission.rule_ref=washing_target`을 확인했다. `composition_rules.py`의 `FUNCTION_EFFECT_RESULTS`는 이 기능에서 해당 결과로 가는 방향을 명시한다. 이는 사실 관계로서 맞으며 삭제할 이유가 없다.
4. **문제 2 문장.** `description_composition_planner.py:12` 및 `:121` 부근은 세척 기능·결과를 `detail_reason`으로 보낸다. `_expanded()`는 이를 배제하지 않는다. `description_composition_results.py:166`의 세척 합성, `description_composition_lexicon.py:185`의 `WASH_TARGET` 조건으로 현재 문장이 만들어진다.

> 물로 피와 옷의 때를 씻어낼 수 있다. 세척한 옷은 완전히 젖는다. 이때 접근 가능한 물 공급원과 세척당 물 10단위가 필요하다. 세제는 선택 사항이며 이동하면 중단된다.

실제 expanded segment가 위 block과 세척 function/effect/condition refs를 갖는다. 참조 연결 오류가 아니라 **공개 목적 선택 오류**다. “양말을 물로 씻을 수 있다”로 바꿔도 양말의 용도 설명에 세척 대상 관리가 남는다. 세척 사실은 내부 근거로 보존하고 양말의 DVF 공개 용도에서는 제외하는 것이 타당하다.

패치도 `recovery_sources.py:2706` 이후가 양말의 `receive_garment_patch`/`remove_garment_patch`와 바늘·실·천의 `apply_garment_patch`/`unpick_garment_patch`를 구분한다. 현재 양말 문장의 “의류의 구멍에 천을 덧대거나 패딩을 추가할 수 있다”는 대상의 관리 가능성을 도구 능력처럼 읽히게 한다. 대상 사실의 보존과 문장 선택을 분리해야 한다. 착용 자체와 `worn_location=Socks`는 실제 용도·정체성으로 남기되, 소지 여부·이동 중단·중복 착용 설명은 제거한다.

추가 발견: Cotton 양말 compact에도 “데님·가죽을 찢을 때는 가위가 필요하다”가 붙는다. 선언은 이미 Cotton을 식별한다. 일반 fabric 조건을 정확한 적용 재질에 맞춰 선택하지 않은 문제이며, 모든 직물의 조건을 양말 설명에 나열해서는 안 된다.

### 비누: 세척제 용도는 유지하고 행동 전체의 결과는 분리

`Base.Soap2`에는 `wash_equipment` fact `fact:964b4077b4e9592a527187c078224979762ed0075cb17fdff7e7b1c5a541e8d4`, `wash_body` fact `fact:84c8cac63bfaf4156472776442d5357058d25c6b302c424130d58e89fdabe2d4`가 있다. 각각 세척제 rule에 근거한다. 양말의 `washing_target`과 혼동할 필요가 없다.

문제 1은 몸 세척과 혈흔 제거를 result로 연결하지만 때 제거는 별도 block으로 보존한다. `description_composition_families.py:342` 이후는 몸 세척과 두 결과를 요약하고 장비 세척은 expanded로 둔다. planner의 `DETAIL_FUNCTIONS`에는 **대상의 관리뿐 아니라 세척제의 실제 용도인 `wash_equipment`도 포함**되어 있다. 그 결과 비누 compact는 다음처럼 몸 세척을 앞세우고 의류는 결과절로만 나타난다.

> 물을 쓰는 몸 세척의 세척제다. 처리한 신체·의류 부위의 피·때를 지우며 세제 없이도 씻을 수 있고 물이 부족하면 일부만 씻긴다.

교정은 “몸과 의류·장비를 물로 씻을 때 쓰는 세척제다”처럼 두 확인된 용도를 역할로 묶는 방향이다. 물 부족 시 일부만 씻김, 젖음, 부위당 물·세제 소비, 화장 제거, 이동 중단은 행동의 처리 정보다. 비누의 기능 결과로 과장하거나 의류 전체에 같은 물 부족 결과를 확장하지 않는다. `CleaningLiquid2`도 동일 세척 family 출력을 확인했으나 다른 독립 역할까지 이번에 전부 감사한 것은 아니다.

### 양말과 라이터: 불쏘시개 재료와 점화 도구

원본 `lua/server/Camping/camping_fuel.lua:34,60`은 Clothing을 연료/불쏘시개 분류에 등록한다. `lua/client/Camping/ISUI/ISCampingMenu.lua:46–62`는 착용·직물 조건을 검사하고 `:129`는 StartFire 태그 또는 Lighter/Matches를 별도로 선택한다. `lua/client/Camping/TimedActions/ISLightFromLiterature.lua:46–52`는 `self.item` 제거, `self.lighter:Use()`, lightFire 요청을 구별한다. 바비큐/벽난로의 대응 timed action도 `ISBBQLightFromLiterature.lua:45–46`, `ISFireplaceLightFromLiterature.lua:49–50`에서 이 구분을 유지한다.

| 항목 | A의 실제 의미 | 문제 1 좌표/관계 | 현재 문장 결함 |
| --- | --- | --- | --- |
| 양말 연료 | `supply_campfire_fuel`, `supply_hearth_fuel` | `block:08c7161872441a6d7cbac492efc2b6a4f43ea95465157cbbd1872408d2e38c93`; 대상별 variant | 같은 연료 용도를 나눠 쓰며 착용·용기·이동 조건을 반복 |
| 양말 불쏘시개 | `provide_campfire_tinder`, `provide_hearth_tinder`, `provide_industrial_tinder` | `block:77c682a2097dc2ad845a2697642f728a1ae785ef222f80db33a2a7ac8d8290b8`; 대상별 variant | 발화 도구, 꺼진 대상, 소모, 드럼 상태 등 행동 전체 조건을 대상마다 출력 |
| 라이터 | `light_campfire`, `ignite_hearth_with_tinder/petrol`, `ignite_industrial_tinder/fire_with_petrol`, `request_corpse_burning`; 초 점화의 `tool` | 예: `light_campfire` fact `fact:3cc8ff94fe97a3f591cc747aa91e501fd8853853163e1b76a6eb9fbf3d6b8115`; 초 점화 role은 별도 context branch | 점화 도구 역할은 맞지만 expanded가 수단·대상별 절차를 모두 설명 |

A `recovery_sources.py:3272` 이후의 heat operation 선택과 `:3320` 부근 캠핑 함수, 문제 1의 `FUNCTION_VARIANT_GROUPS`는 역할 분리를 보존한다. 문제 2 `description_composition_results.py:184–254`는 compact에서 연료/불쏘시개를 합성하지만 expanded는 `_expanded()`의 동일 qualifier 기준으로 나뉘어 조건마다 문장화된다. 같은 용도의 다른 대상이 같은 문장으로 묶이려면 조건 문자열까지 같아야 하는 구조가 반복을 만든다.

공개 용도는 “연료”, “불쏘시개”, “점화 도구”로 각각 보존하고 메뉴에서 확인된 대상 범위를 설명하면 된다. 비프로판 바비큐, 통나무가 든 드럼 등 **대상의 의미를 한정하는 조건**은 남길 수 있다. 걷기 중단·인벤토리 이전·반복 validity·일회 사용은 생략한다. 기존 화로 클라이언트 비활성 등 A의 근거 한계를 지우고 “모든 화로에 불을 붙인다”로 확대해서는 안 된다. 라이터의 확인된 휴대 조명 역할도 점화에 흡수하지 않는다.

### 통조림: 개봉 입력 → 결과 식품 → 요리 재료

원본의 관계는 다음과 같다.

| 원래 item | 제작법 근거 | 도구 | 결과 선언과 내용물 근거 |
| --- | --- | --- | --- |
| `CannedCorn` | `scripts/recipes.txt:1916` Open Canned Corn | `keep [Recipe.GetItemTypes.CanOpener]` | `CannedCornOpen`; `scripts/items_food.txt:158–169`의 Food, EvolvedRecipe 목록, 활성 `EvolvedRecipeName=Corn` |
| `CannedSardines` | `scripts/recipes.txt:1988` | 도구 입력 없음 | `CannedSardinesOpen`; `items_food.txt:269` 이후 `EvolvedRecipeName=Sardine`와 요리 목록 |
| `CannedCornedBeef` | `scripts/recipes.txt:1906` | 도구 입력 없음 | `CannedCornedBeefOpen`; `items_food.txt:49` 이후 `EvolvedRecipeName=Corned Beef`와 요리 목록 |

`scripts/items.txt:533–543`의 `Base.TinOpener`는 `DisplayName=Can Opener`, `Tags=CanOpener`다. 이 파일의 CanOpener 태그 선언은 하나다. `lua/server/recipecode.lua:35–36`은 바로 이 태그 집합을 조회한다. 한국어 `ItemName_KO.txt:1499`의 실제 표기는 “깡통 따개”다. 사용자가 말한 “통조림 따개”와 같은 식별 대상이며, 제품 문안에서는 기존 표시명 정책에 맞춰 통일하면 된다. 다른 버전·미래 태그 집합까지 단일 도구라고 일반화하지 않는다.

**정보가 좁아지는 위치:** `recovery_sources.py:4490–4538`은 consumed item과 Result를 FullType으로 해석하고 선언·callback을 확인한다. `package_opening_results[item]`에 `result_item`, clauses, evidence를 보관하며 결과의 EvolvedRecipe와 실제 evolved recipe record를 확인한 경우에만 `prepare_opened_food_ingredient`를 만든다. 이 guard는 정확하므로 보존한다. 그러나 공개 facts에는 일반 `unpack_canned_food`, package_opening의 `material`, `prepare_opened_food_ingredient`와 포괄 조건이 남는다. `result_item`, 식품의 내용물 이름, 도구 집합이 구조화된 인자로 전달되지 않는다. `recovery_migration.py:3394` 부근도 일부 output_identity를 declared Result와 native 생성 보장 사이의 경계로 보관한다. 선언된 결과 정체성과 실제 결과 전달 성공 보장을 구분해야 하며, 전자를 이름으로 설명하는 것까지 막을 이유는 없다.

`blocks.json`의 CannedCorn은 개봉 block `block:b5efabd605512413004932f8a25678784d6d3ce702384ddbbd1abebd2c1c34ab`, package material/context block, 개봉 후 조리 block `block:df1f8945bd486af7356d0214b17676c98cc9aaea2050859a5e830e454367fc7e`로 나뉜다. 마지막 fact는 `fact:f4c22fc36801d06112401a98edaddaf713514c75a60836a9b0dc3d3548c0e10c`다. 결과 식품 이름은 이 블록들에 없다.

`description_composition_families.py:782–785`는 OPENING/CAN_OPENING을 구분하되 각각 “개봉해 내용물을…”/“맞는 개봉 도구로 내용물을…”라는 고정 일반문으로 만든다. CannedCorn compact의 두 문장은 이 개봉 frame과 별도 개봉 후 재료 기능에서 나온다. 정어리·콘비프 출력에는 “맞는 개봉 도구”가 없으므로 **도구 유무 분기는 이미 정확하다**. 부족한 것은 명시적 도구명·내용물명과 관계의 합성이다.

CannedCornOpen에는 실제 `food_preparation/ingredient` block `block:3aa66b1536e159e91dd7ce76a2d1e5f6623561fcaa03362685f02ab62d8b83cc`, 별도 `eat_food`, `supply_trap_bait`가 있다. 원래 통조림의 현재 block에는 먹기·미끼가 복사되어 있지 않다. 이 경계를 보존한다. “포만 상태가 허용하면”, “추가 재료가 없는 날음식을 받는 덫”은 열린 식품의 별도 사용 조건이며, 개봉 전 통조림 문장으로 전이시키지 않는다. 특히 미끼는 동물·덫 적합성이 있으므로 무조건적인 모든 덫의 미끼로 축약하지 않는다.

**내용물 명명 규칙:** 이름의 Open/Canned 접두사를 잘라 추측하지 않는다. 개봉 Result의 exact item을 먼저 확정하고, 그 결과의 활성 `EvolvedRecipeName` 등 명시된 식품 의미와 locale 이름을 연결한다. 옥수수는 주석 처리된 `Canned Corn`이 아니라 활성 `Corn`을 사용한다. 한국어 `EvolvedRecipeName_KO.txt:5–9`는 여전히 “옥수수 통조림/소고기 통조림/정어리 통조림”이므로, 기존 localized item label과 식품 내용물 명칭은 별개임을 처리해야 한다. 공통 식품 명칭 매핑은 가능하지만 FullType별 최종 문장 패치는 아니다. 명칭 근거가 부족한 다른 결과에는 확인된 결과 표시명을 쓰거나 해당 구절을 보류한다.

**개봉 전 직접 요리도 보존:** `TinnedBeans`의 현재 compact에는 개봉 후 재료와 직접 `food_preparation` 역할이 함께 있다. `recovery_sources.py:1841,1880`은 통조림 상태로 Bowl 및 kept CanOpener와 참여하는 Make Bowl of Beans를 별도 취급한다. `scripts/recipes.txt:207`의 Make Pot of Soup도 CannedMushroomSoup를 직접 입력으로 받는다. 따라서 “통조림은 반드시 먼저 개봉해야 조리 가능”이라는 공통 규칙은 틀리다. 직접 제작 참여와 개봉 결과의 재료 용도를 서로 다른 관계로 유지해야 한다.

## A·1·2·3별 수정과 보존

| 단계 | 직접 교정에 필요한 부분 | 이미 맞아 보존할 부분 |
| --- | --- | --- |
| A: source·사실 | 통조림의 기존 exact opening result/tool 정보를 후속 조합이 읽을 수 있는 관계로 전달. 대상 기능 키의 participant 의미를 명시적으로 전달하거나 source-rule 기반 역할 해석에 사용. 선언된 내용물과 native 성공 보장을 구별 | `washing_target`/`washing_supplies`, provide/ignite 구분, patch target/tool 구분, 결과 요리 근거 guard, 조건 적용 refs, 미확정 경계, 여러 용도. 세척 사실 삭제·r6 덮어쓰기 불필요 |
| 1: 의미 블록 | 보존된 사실에서 공개 용도 단위를 구성할 역할 해석을 지원. 개봉 입력→결과→내용물/재료의 방향 관계 수용. 보존 block과 공개 block 선택을 구분 | 정확한 role/context binding, result 방향, target variant, qualifier scope, stable ID, unresolved 관계. 세척 결과 block은 오류가 아니며 삭제하지 않음 |
| 2: 문장 조합 | `detail_reason` 이분법을 공개 용도/의미 한정/비공개 근거로 분리. expanded 전량 출력 해제. 재료·도구·대상별 주어와 목적어 선택. target variant의 공통 용도 합성, 실제 적용 재질 조건 선택, 이름 있는 통조림 관계 합성. KO/EN 동일 의미 적용 | 문장과 refs 연결, 조건이 다른 claim으로 번지지 않도록 하는 제한, 도구 유무 분기, 연료/불쏘시개 구분, family 기반 공통 교정, 다중 용도·부재/실패 구분 |
| 3: 품질 판단 | 사실 전량 공개를 수락 조건으로 삼은 부분을 바꿈. 역할이 맞는지, 용도인가 관리 절차인가, 짧은 요약인가를 실제 전후 출력에서 확인. 기존 검사 기대도 같은 의미로 조정 | 과거 읽기·실패·교정 이력, 일부 건축/제작과 독립 가구 이동 구분, Notebook 다중 용도 압축 등 유효한 교정. 이전 수락 기록은 이번 결함의 반증이 아님 |

문제 1 contract의 “모든 accepted fact를 anchor/qualifier로 보존”은 맞다. “independent block을 discard하지 말라”는 조건은 내부 자료 유지에 적용해야 하며 모든 block의 문장화를 요구해서는 안 된다. contract는 block이 문장/화면 block을 강제하지 않는다고도 명시한다.

문제 2 검사 `Iris/build/description/v2/tests/test_layer3_description_composition.py:53–74`는 expanded segment의 represented refs가 all_refs와 같아야 한다고 요구한다. 이는 **사실 보존과 문장 출력의 결합을 실제로 강제하는 지점**이다. 공개에서 빠진 근거를 무관한 문장의 refs에 붙여 이 조건만 통과시키면 안 된다. 후속에는 내부 보존된 사실과 실제 문장이 주장한 사실을 구별하도록 기존 검사 의미를 고쳐야 한다. 이번에는 검사 실행·수정 모두 하지 않았다.

문제 3 plan은 compact를 두 번째 물리적 한 줄로 정의하면서도 실제 expanded에 없는 정보를 audit/ref 보존으로 계산하지 못하게 한다. 기존 `review.json`은 673 조합/2105 items 등을 읽었다고 기록하며, closeout도 offline complete다. 이 기록을 삭제할 필요는 없지만, 현재 확인된 문장이 위키의 용도 설명인지에 대한 새 증거를 대신할 수 없다. 이번에는 상태를 변경하지 않았다.

## 공통 교정 원칙과 전후 예시

공통 순서는 **근거 보존 → 해당 item의 참여 역할 → 독립 용도와 필수 의미 한정 선택 → 이름 있는 관계 합성 → 표면별 문장**이다. 문장 수·문자 수를 먼저 자르거나 primary_use를 선택하지 않는다. 실행당 소모량·동작 순서와, 재사용 도구인지 변환·소모되는 재료인지는 다르다. 후자는 용도의 성격이므로 보존한다. “소모” 표현을 일괄 제거하지 않는다. DVF 양쪽에서 제외할 관리 절차와 compact에서는 묶어 요약하되 expanded에서 보존할 실제 독립 용도도 구분한다. 길이가 길다는 이유만으로 독립 용도를 비공개로 분류하지 않는다.

| 사례 | 현재 핵심 표현 | 제안하는 방향 |
| --- | --- | --- |
| 양말 compact | 착용, 직물 회수, 데님·가죽 가위 조건, 로프, 연료·불쏘시개 조건을 여러 문장으로 나열 | “착용하거나 천·시트 로프의 재료, 연료·불쏘시개로 쓸 수 있다.” 모든 확인된 용도는 유지하고 적용되지 않는 재질 조건과 실행 절차는 제외 |
| 양말 menu | 세척·완전 젖음·물 10단위·패치·점화 절차·착용 관리 | “양말 자리에 착용한다. 천을 회수하거나 시트 로프를 만드는 재료로 쓸 수 있다. 모닥불·비프로판 바비큐·벽난로의 연료와 불쏘시개로 쓰며, 통나무가 든 드럼의 불쏘시개로도 쓸 수 있다.” 범위 제한은 보존하며 실제 행동 절차는 출력하지 않음 |
| 비누 compact | 몸 세척 + 세제 선택 + 물 부족 결과 | “몸과 의류·장비를 물로 씻을 때 쓰는 세척제다.” 세척 대상과 구별되는 두 공급 용도를 유지 |
| 라이터 | compact의 점화/조명 개요는 있으나 menu에 대상별 실행 조건이 반복 | 점화 도구와 휴대 조명의 복합 역할 유지. 메뉴에서는 확인된 점화 대상·수단 차이만 확장하고 소모 횟수·이동 중단·재검사 절차는 제외. 미확정 화로 효과를 확정하지 않음 |
| 옥수수 통조림 | “맞는 개봉 도구로 내용물을… 개봉한 내용물을 허용하는 요리…” | “깡통 따개로 개봉해 옥수수를 요리 재료로 쓸 수 있다.” 도구·Result·Corn·요리 근거를 한 관계로 표현. 사용자의 “통조림 따개” 표기를 채택하더라도 동일 TinOpener를 가리켜야 함 |
| 정어리/콘비프 통조림 | “개봉해 내용물을… 개봉한 내용물을 허용하는 요리…” | “개봉해 정어리를 요리 재료로 쓸 수 있다.” / “개봉해 콘비프를 요리 재료로 쓸 수 있다.” 도구를 추가하지 않음. 콘비프의 최종 KO 명칭은 기존 “소고기 통조림” 표시와 공통 내용물 명칭 정책을 맞춘 뒤 결정 |
| 열린 옥수수 | 음식 준비 일반문 + 포만 조건 + 미끼 조건 | 먹기·옥수수 요리 재료·조건부 미끼를 각각 보존. 이번 조사만으로 동물/덫 후보를 전부 특정하지 않았으므로 미끼의 최종 단문은 미확정. 이것을 원래 통조림의 용도로 복사하지 않음 |

표의 짧은 문안은 물리적 fit을 측정한 결과가 아니다. 메뉴에 모든 “허용된/지정된/맞는” 조건을 다른 말로 되풀이하는 것도 해결이 아니다. 용도 범위에 필요한 대상·도구는 근거에 있는 이름을 쓰고, 사용 가능 상태를 반복하는 실행 조건은 공개 문장 자체에서 제외한다. 여러 대안 도구가 실제로 있으면 그 집합 또는 근거 있는 공통 명칭을 표현하고 단일 도구로 좁히지 않는다.

## 적용 범위와 후속 직접 교정의 최소 범위

양말만의 개별 오류가 아니다. `washing_target`은 Clothing/Weapon/Container 전체에, 세척제 frame은 Soap2/CleaningLiquid2에, 불쏘시개/연료 규칙은 같은 함수·조건 조합에, 개봉 frame은 해당 opening family에 적용된다. 따라서 후속 검토 대상은 **수정한 공통 규칙에 실제로 매칭되는 항목**이다. 현 조사에서 모든 해당 항목 수나 품질을 확정하지 않았으며 새 census나 2105개 전면 재감사를 요구하지 않는다. 별개 role은 매칭에서 분리하고, 복합 역할 조합은 보존 여부를 확인한다.

최소 변경은 다음과 같다.

1. A→1에서 이미 추출하는 개봉·가공·분해 결과와 도구 집합, 결과의 명시적 이름 및 원래 item의 용도를 설명하는 활용 관계를 조합 입력에 연결한다. 추가 조사에서 확인한 탄약 상자·농산물 자루·씨앗 봉지·전자 기기 분해까지 같은 전달 원칙을 적용한다. 개구리처럼 이미 qualifier에 정보가 전달된 경우는 표현 단계의 누락부터 고친다. 일반 raw source 재조사나 QG 재설계로 넓히지 않는다. 양말의 맞는 사실은 그대로 둔다.
2. 1→2에서 대상/도구/재료/공급 역할을 공개 용도 선택에 사용한다. 새 전역 역할 체계보다 현재 function/rule/context_role에서 확정 가능한 최소 구분으로 시작한다. 비공개 근거 유지와 공개 claim refs의 차이를 표현하고, expanded를 무조건 남은 사실 전부로 만드는 흐름을 고친다.
3. 문제 2의 공통 planner·family·lexicon·results에서 위 사례를 교정한다. 기존 검사 중 all_refs=expanded 조건과 compact→expanded 링크의 의미도 변경에 맞춘다. 새 validator·seal·receipt·manifest·proof 체계는 필요하지 않다.
4. B/C는 교정된 같은 자료를 공급받는 기존 경로를 유지한다. C `product_projection.py:86` 이후는 segment를 온전히 유지하고 관계를 기준으로 묶을 뿐 문장 의미를 고치지 않는다. 이곳에서 문장을 숨기는 해결은 피한다. B `IrisAltTooltip.lua:81–90`은 모든 행의 원문을 측정해 폭을 늘린다. 길어진 문장을 한 줄에 그리는 것과 간결한 DVF 요약은 별개이므로 producer 교정이 선행되어야 한다.

완료 판단은 교정된 실제 자료에서 양말의 관리/세척 절차가 빠지고 용도는 남는지, 비누·라이터가 각각 공급/도구와 복합 역할을 유지하는지, 통조림 이름·도구·개봉 전후 관계가 근거와 맞는지, 공통 규칙의 영향 항목에 같은 오류가 재발하지 않는지로 한다. 공개에서 빠진 사실은 내부 근거에 남고, 새 주장이 근거 없이 생기지 않아야 한다. KO/EN의 의미·조건 범위도 맞아야 한다. 후속 구현 시 필요한 기존 검증은 정확한 관련 명령 exit 0일 때만 PASS라고 하며, 이번 보고서 작성에는 테스트를 실행하지 않았다.

실제 Tooltip 완료는 Alt에서 최대 **4개 물리적 화면 줄**, 1 L2 소분류 / 2 DVF 간결한 용도 요약 / 3 획득 장소 / 4 유효한 L4 레시피·우클릭·자유 조리 후보 무작위 표시를 확인해야 한다. 폭 확장·여러 문장 공백 연결만으로 용도 요약 완료를 주장하지 않는다. B의 연결·표시는 사용자 인게임 통과 사실을 보존하되 설명 품질 수락으로 확대하지 않는다. C는 기존 `implemented_only`이며 메뉴 의미 품질은 미통과다.

구조적으로 필요한 변화는 개봉 관계 정보 전달과 내부 보존/공개 claim 분리다. 현재 owner 경계 안에서 직접 교정할 수 있는 위치를 찾았으므로 **별도 문제·계획·Gate 수립이 선행되어야 할 사유는 발견하지 못했다**. 실제 구현 중 기존 schema가 관계나 비공개 구분을 담지 못하면 해당 모델/consumer의 최소 변경을 함께 수행할 사안이며, 이를 전체 워크플로우 재시작의 근거로 삼지 않는다.

## 추가 조사: 통조림 밖의 구체적 관계 전달

같은 날짜에 수행한 보고서 개정 조사다. 새 파일·검사·생성물은 만들지 않았다. 추상 표현을 만드는 `description_composition_families.py`, `description_composition_lexicon.py`를 출발점으로 아래 사례만 선정했다. **통조림 밖에서도 발생하지만 원인은 하나가 아니다.** 상류 정보의 구조화된 전달 누락, 이미 전달된 qualifier의 표현 손실, 실제 근거 해석 한계, 동적 대상·복수 대안의 정당한 일반화를 구별해야 한다.

추가로 실제 KO compact/expanded와 blocks를 함께 읽은 항목은 `Base.223Box`, `Base.SackProduce_Carrot`, `farming.CarrotBagSeed`, `Base.Frog`, `Base.Remote`, `Base.BrokenFishingNet`, `Base.Key1`이다. `Base.Scissors`, `Base.Battery`, `Base.FishingNet`의 출력은 비교용으로 읽었다. `Base.Radio`와 `Base.DigitalWatch2`에서 이 분해 결함의 양성 사례를 확인하지 못했으므로 전자제품 전체에 같은 결함이 있다고 집계하지 않았다. 이 추가 조사는 카테고리 전수 감사, 새 census, 모든 영어 문장 확인이 아니다.

### 공통 경로에서 확인한 구분

- `lexicon.core()`(`:341` 이후)는 direct_function 이름으로 고정 문구를 조회한다. 결과 item·도구 집합을 받는 일반 인자가 없다. planner는 전달받은 fact/context/qualifier를 유지하지만 source observation의 recipe clauses를 다시 해석하지 않는다. 따라서 provenance에 정보가 있다는 사실만으로 문장 조합 입력에 관계가 전달됐다고 할 수 없다.
- `families.packaging_frames()`(`:774` 이후)는 function/activity/predicate 일치로 고정 문구를 선택한다. 탄약은 “탄약”, 자루는 “농산물”, 개구리는 “허용된 칼…고기”다. 일부 predicate를 `complete`로 취급해 expanded에서도 조건문을 생략하고 “complete condition을 포함한 wording”으로 기록한다. 개구리의 실제 도구 대안·재사용 의미를 생략하는 데에도 이 경로가 적용된다. refs 보유와 표현의 충실성은 다르다.
- “허용된 재료/지정된 물품”은 어휘 자체만으로 결함을 판정할 수 없다. 결과물 이름이 사라진 경우, 실제 복수 재료의 공통 명칭인 경우, 현재 상태에 따라 대상이 정해지는 경우가 섞여 있다. 불필요한 관리 조건은 공개하지 않되, 실제 용도 대상을 설명하는 관계는 구체화해야 한다.

### 대표 사례의 사실 → A → 블록 → 문장

#### 1. 탄약 상자 — 결과 정체성 전달 누락 확인

`scripts/recipes.txt:747`의 Open Box of .223 Ammo는 `223Box`를 입력으로, `223Bullets=8`을 결과로 선언하며 kept 도구는 없다. `scripts/items_weapons.txt:6463–6470`은 해당 결과의 표시명을 `.223 Ammo`로 선언한다. 이름 접두사를 추측할 필요가 없다.

A `recovery_sources.py:4467–4512`는 이 recipe를 `unpack_ammunition`으로 분류하고 exact result 선언과 Ammo category를 확인하여 `package_opening_results`에 `Base.223Bullets`를 기록한다. 문제 1의 `block:cebc92f09b13266febd5a1d42691c0cdd4cbd63796dd02e7d2d5e22c8d77572e`에는 `unpack_ammunition`만 있고, `block:546cad8d5d567f0a4da8917e5287f92fe2832e502eec9d03d6ee54a8307b9e28`에는 package_opening/material이 있다. 결과 탄종과 도구 없음은 구체적 관계 필드로 전달되지 않는다.

현재 compact는 “탄약이 든 상자이며 개봉해 탄약을 꺼낼 수 있다.”, expanded는 여기에 “해당 개봉법에서 요구하는 도구와 제작 조건”을 붙인다. **탄종 정체성이 사라지고 도구 없는 경로에도 포괄적인 도구 조건이 붙는 결함**이다. “개봉해 .223 탄약을 꺼낼 수 있다”는 방향은 선언된 결과에 근거한다. 8발은 recipe 선언 수량이지만 요약에 반드시 넣어야 할 정보는 아니며 native 전달 성공을 새로 보장하지 않는다. 호환 총기 목록이나 발사 성능을 상자에 복사할 근거는 이번에 확인하지 않았다.

#### 2. 당근 자루 — 통조림과 같은 결과 활용 관계 누락 확인

`scripts/recipes.txt:4071`은 `SackProduce_Carrot → Carrots=12`, `OpenSackProduce` callback을 선언한다. `scripts/items_food.txt:1129` 이후의 `Carrots`는 Food이며 Soup/Stew/Pie 등 EvolvedRecipe가 있다. A는 exact Result와 결과의 요리 참여를 확인하고 `package_opening_results` 및 `produce_sack_sources`에 opened item을 저장한다(`recovery_sources.py:4515` 이후).

문제 1에는 `unpack_produce` block `block:9f123554e453cb323118f21bf9bdc6132225c1f417fdff0b5bb8630aa31a8af9`, `prepare_opened_food_ingredient` block `block:f81b435063bacba3073e9057f269d44ef512b63871630e16868bc2c79b5ad78c`가 있지만 Carrots 정체성이 없다. 현재 compact는 “농산물을 꺼내는 자루이며 개봉해도 신선도가 회복되지는 않는다. 개봉한 내용물을 허용하는 요리의 재료로 쓸 수 있다.”다.

“자루를 열어 꺼낸 당근을 요리 재료로 쓸 수 있다”로 관계를 설명할 근거가 있다. freshness 복사 경계는 내부에 유지하되 자루의 주용도를 대신하는 첫 설명으로 둘 필요가 없다. A에 있는 역포장 recipe를 추정하지 말라는 제한도 유지한다. 당근의 모든 먹기·미끼·기타 활용을 자루에 복사하는 교정은 아니다.

#### 3. 씨앗 봉지 — 결과와 파종의 연결은 있으나 작물 정체성 누락 확인

`scripts/farming.txt:740–747`은 `farming.CarrotBagSeed → farming.CarrotSeed=50`을 선언한다. `lua/server/Farming/farming_vegetableconf.lua:514,524`는 Carrots의 `seedsRequired=12`, `seedName=farming.CarrotSeed`를 연결한다. A `recovery_sources.py:2590–2599`는 `seed_sources`에 crop과 count를 저장하고, `:4535` 이후는 개봉 결과가 seed_forms에 있을 때만 `sow_extracted_seeds`를 추가한다.

문제 1의 해당 item에는 `unpack_seeds`, package_opening/material, `sow_extracted_seeds`, “12 loose seeds per furrow” 조건이 전달된다. 그러나 crop=Carrots와 result_item 관계는 명시적 의미 인자로 없다. 문제 2 `families.py:354–369`는 수량을 읽어 “봉지를 개봉해 꺼낸 **이 작물**의 낱알 씨앗 12개…”라고 한다. 즉 **개봉 봉지와 낱알 소비의 구분은 이미 정확하지만 작물 이름 대신 지시어만 남는 전달 결함**이다.

“봉지를 열어 꺼낸 당근 씨앗을 파종하는 데 쓸 수 있다”는 방향으로 활용을 표현할 수 있다. 50개는 포장 결과 수량, 12개는 고랑당 소비량으로 서로 다른 관계다. 숫자를 옮겨 적거나 봉지 자체를 파종에 소모한다고 표현하면 안 된다. 성장·수확 성공은 이 관계로부터 도출되지 않는다. 씨앗의 결과 활용을 봉지 용도로 연결하는 A의 guard는 다른 결과 활용 관계에도 참고할 수 있다.

#### 4. 개구리 손질 — 입력 전달 후 표현 단계의 일반화 확인

`scripts/recipes.txt:1130`의 Slice Frog는 `keep [Recipe.GetItemTypes.SharpKnife]/MeatCleaver`, `Frog`, `Result:FrogMeat`를 선언한다. `recipecode.lua:57–58`은 SharpKnife 태그를 조회한다. `scripts/items_weapons.txt`의 태그 선언에서 Machete(`:395`), Hunting Knife(`:3417`), Stone Knife(`:3467`), Kitchen Knife(`:3943`)를 확인했다. 이들과 별도의 MeatCleaver 대안을 단일 “식칼 하나”로 좁히면 틀리다.

A `recovery_sources.py:3933–3969`는 exact clauses를 확인하고 material/tool 참여를 분리한다. `FROG_PREPARATION` predicate에는 SharpKnife-group **또는** MeatCleaver, keep, FrogMeat가 들어 있다. 문제 1의 material/context block `block:14899531c3411220e675aead4a25d4f691efb84c9f1feb4eb980699afc05e39e`와 function block `block:f93659b6e5b436e9e2ec8d9dc1a3b3d0e299a2e45365e517627ea33d36795bb6`에 붙은 qualifier에서 이 문자열을 실제로 확인했다.

현재 compact/expanded는 모두 “허용된 칼로 손질해 고기를 꺼내는 개구리 재료다.”다. **상세 정보가 완전히 전달되지 않은 통조림과 달리, 여기서는 도구 대안·결과·재사용 정보가 qualifier에 있으나 packaging frame이 일반화한다.** 구조화된 인자를 추가하면 공통 처리가 쉬워지지만, 기존 정보가 없는 것처럼 재조사할 사안은 아니다.

교정 방향은 compact에서 “칼로 손질해 개구리 고기를 얻는 재료다”처럼 실제 변환 용도를 요약하고, expanded에서 확인된 칼 집합 또는 정확한 공통 명칭과 식칼 대안, 도구가 보존된다는 차이를 설명하는 것이다. 최종 locale 명칭은 선언/번역에서 연결한다. 이번에는 FrogMeat의 모든 후속 요리·섭취 관계를 추적하지 않았으므로 원래 Frog에 “요리 재료로 쓴다”까지 전이하는 문안은 확정하지 않는다.

#### 5. 리모컨 분해 — 결과 정체성 누락과 정당한 확률 한정이 함께 존재

`scripts/recipes.txt:2024–2034`의 Dismantle TV Remote는 Remote, kept Screwdriver group, **Result:Receiver**를 선언한다. `recipecode.lua:840`의 DismantleTVRemote callback은 ElectronicsScrap을 추가하고 확률 조건 아래 Battery를 생성·추가한다. `Recipe.GetItemTypes.Screwdriver`는 `recipecode.lua:47–48`에서 태그를 조회하며 저장소 item 태그 검색에서는 `items_weapons.txt:4178`의 Screwdriver 선언을 확인했다.

A `recovery_sources.py:4372–4412`는 이 recipe/callback/도구 group과 exact output 선언을 읽는다. 그러나 output participant는 건너뛰고 입력에 `dismantle_electronics` 및 transformation_target을 부여한다. 결과가 scrap이거나 해당 callback인 경우에는 `SCRAP_RECOVERY`를 추가한다. 이로써 **Receiver는 observation의 Result로만 남고, 공개 의미 입력은 generic 분해와 scrap 조건으로 축소된다.** 문제 1의 function block은 `block:654dddd6022615bf8d6dc27fb3c579701e3d22aad89500c24054f0432d7390f8`, transformation context block은 `block:05e261f724c0802c956bd7cc013e9578a86da073905a59258fbf5dab3d19e0ba`다. 별도 electronic_assembly/material block도 남아 있다.

현재 compact는 제작 재료 용도 다음에 “전자 기기 분해에 쓰는 가공 대상이다. 분해해 전자 부품을 회수할 수 있다.”, expanded는 전자 스크랩과 “추가 부품은 보장되지 않는다”를 설명한다. 결과 Receiver를 명시하지 않는 것은 확인된 누락이다. 다만 **건전지를 항상 회수한다고 바꾸면 오류**다. 결과 관계를 declared result / unconditional callback addition / conditional callback addition으로 구별해야 한다. “드라이버로 분해해 수신기와 전자 스크랩을 얻는 재료이며, 건전지도 나올 수 있다”는 방향은 각 관계의 근거와 가능성을 분리하는 예시다. 정확한 KO 표시명과 실제 native 결과 전달 보장은 별개다.

리모컨은 해체 대상이지만 회수 재료를 공급하는 실제 용도가 있다. 양말의 관리 세척과 달리 transformation_target이라는 이유만으로 공개에서 제외하면 안 된다. 또한 타이머·원격 조작 부품 제작의 독립 material 역할을 분해 용도에 흡수하지 않는다. Receiver나 Battery의 모든 용도를 원래 리모컨에 전이하지 않는다.

#### 6. 부서진 어망 — 근거 해석 한계로 남겨야 하는 반례

`scripts/recipes.txt:1428`의 Get Wire Back은 `Result:Wire;3`라는 원문을 갖는다. A `recovery_sources.py:3953–3956`은 이 semicolon 결과를 opaque로 명시하고 예외적으로 입력 참여만 수용한다. 문제 1의 wire_recovery/material 및 `process_broken_fish_net` 블록과 qualifier도 “native parser 없이 Wire identity/count를 확정하지 않음”을 보존한다.

현재 “철사 회수 제조법에 쓰는 부서진 어망이다”는 이 bounded 사실을 설명한다. 이름이 구체적이지 않아서 생긴 통조림형 전달 누락으로 분류하지 않는다. **철사 3개를 확정 획득**한다고 교정해서는 안 된다. 결과 해석의 범위를 바꾸는 조사는 이번에 하지 않았으며, 원문의 세미콜론을 등호로 고쳐 읽지 않았다.

#### 7. 열쇠 — 동적 일치 관계의 정당한 일반화와 소모 역할 구분

`lua/client/TimedActions/ISLockDoor.lua:11`은 key ID 일치를 검사한다. `ISPadlockAction.lua:35–38`은 맞는 key를 찾아 제거한다. A `DOOR_KEY_USE`/`PADLOCK_KEY_USE`(`recovery_sources.py:1624,1626`)는 문 잠금에는 열쇠가 소모되지 않지만 자물쇠 제거에는 해당 열쇠를 소모함을 구별한다. 문제 1의 `Base.Key1`에는 `operate_door_lock`와 `remove_matching_padlock`가 별도 block으로, 이 qualifier와 함께 전달된다.

현재 “맞는 닫힌 문의 잠금을 조작하며 소모되지 않는다”와 “맞는 구조물 자물쇠를 제거할 때 소모하는 열쇠다”는 이 차이를 유지한다. “맞는”은 숨겨진 고정 FullType 이름이 아니라 플레이 상태의 key ID 관계다. 특정 차종이나 문 이름으로 바꾸지 않는다. 이 사례는 실행당 숫자를 생략하더라도 **재사용/소모의 용도 차이는 반드시 남겨야 한다**는 반례다. 전체 compact가 긴 문제와 해당 한정 표현의 의미 타당성은 별개다.

### 확인 후보와 미확인 후보

양말·가위의 “직물 회수”는 추가 구체화 후보다. `recipecode.lua:1110` 이후는 exact clothing definition 또는 FabricType→material을 선택하고, 오염 상태에 따른 Dirty 결과 및 기술·확률에 따른 수량/실 추가를 별도로 처리한다. A `recovery_sources.py:2753` 이후가 fabric context에 `FABRIC_ACTION`을 부여하고 현재 문장이 이를 일반 조건으로 출력하는 것은 확인했다. 그러나 이번에는 `ClothingRecipesDefinitions`의 모든 재질·아이템 override와 A에서 해석한 relation을 끝까지 대조하지 않았다. **Cotton 양말에 Denim/Leather 조건이 붙는 기존 결함은 확정, 정확한 회수 결과 집합의 전달 누락은 추가 확인 후보**로 구분한다. “회수 재료·양은 달라진다”를 전부 거짓이라고 하거나 하나의 무조건적 결과로 바꾸지 않는다.

차량 부품의 “지정 도구”, 가구 이동의 “해당 도구”, 낚시의 “맞는 미끼”, 수납의 “허용된 물품”도 표현 검색에서 발견했다. 이들이 source-specific 관계 전달 누락인지 실제 동적/복수 대상인지 이번에는 각 원본까지 추적하지 않았다. 따라서 결함 확정 목록에 넣거나 각 카테고리 전면 교정을 요구하지 않는다. Battery의 여러 전원 대상이 이미 family에서 합성되는 출력도 확인했으나 모든 대상의 입력 근거를 이번에 재감사하지 않았다.

### 공통 교정의 범위와 의미별 경계

추가 조사로 후속 직접 교정 범위는 **통조림 전용 이름 보완에서, 확인된 입력·도구·변환 결과·제한된 결과 활용 관계를 전달하는 공통 경로 보완으로 넓어진다.** 기존 A/1/2 owner 안에서 다룰 수 있다는 판단은 유지한다. 별도 계획·Gate·검증 체계가 필요한 새 구조 경계는 발견하지 못했다.

| 공통으로 전달·표현할 정보 | 의미별로 반드시 구분할 것 |
| --- | --- |
| source input과 role, exact result item, named tool/material set, 근거 refs | tool keep / 소모·변환 input / 결과 output을 서로 바꾸지 않음 |
| 실제 관계에 연결된 locale 명칭 | FullType 문자열의 접두사 제거, 이름만으로 결과나 용도 추정 금지 |
| 도구·재료의 대안 집합과 결합 관계 | SharpKnife **또는** MeatCleaver, 도구 **및** 재료를 같은 연결어로 처리하지 않음. 대안 집합을 단일 도구로 축소하지 않음 |
| 선언된 변환 결과와 callback 결과 | declared result, 무조건 추가 요청, 확률/상태 조건 결과, 해석 미확정 결과를 구별 |
| 원래 item의 활용을 설명하는 제한된 결과 관계 | 자루→당근→요리, 봉지→낱알→파종은 근거 guard로 연결. 결과의 임의 용도까지 재귀적으로 복사하지 않음 |
| 공개 설명과 내부 근거의 구분 | 관리 절차만 비공개로 둘 수 있으며 실제 독립 용도는 길이 때문에 비공개로 돌리지 않음 |

구조화된 관계가 이미 있는 경우 이를 보존하고, 자연어 qualifier에만 확정 정보가 있는 경우 해당 source rule의 의미를 인자로 전달하는 최소 보완을 검토한다. 문장 조합기가 임의로 raw recipe나 기존 prose를 재해석하는 별도 사실 생산자가 되어서는 안 된다. 모든 raw 조건을 구조화하는 대규모 사업으로 넓힐 필요도 없다.

compact는 확인된 용도의 공통 명칭과 핵심 관계를 짧게 요약하고, expanded는 실제 독립 용도·대안·대상 범위를 이해할 만큼 보존한다. 예를 들어 리모컨의 제작 재료/분해 회수, 라이터의 점화/조명은 실제 복합 역할이다. 세척 대상 관리와 같은 이유로 제외할 수 없다. “소모” 또한 연료·불쏘시개·변환 재료의 성격 또는 도구 재사용 여부를 설명하는 경우 유지하고, 실행당 횟수·작업 순서와 구분한다.

후속 확인은 보고서의 예시 몇 개가 맞는지에 그치지 않는다. **수정한 공통 규칙의 실제 적용 항목과 그 항목의 복합 역할 조합**, 도구 없음/단일/복수 대안, 확정/조건부/미확정 결과, 직접 사용/결과를 거친 활용을 함께 확인해야 한다. 영향 없는 저장소 전체의 재검증, 새로운 전면 품질 감사, 별도 census/proof artifact로 확대하지 않는다. 이번 조사에서는 이 확인을 실행한 것으로 주장하지 않는다.

## 2026-09-12 전환 corpus 자체 검토 완료

이 절은 위 조사/구현 중 상태 이후의 현재 기록이다. `docs/review/uses/items.json`은 현재 descriptions `fc8c11d0e4e375fdf3449e7ae9141779bcf00023ba2537751579cf243b8ebb05`, blocks `0c806c345cbe512129c8a4af27ecd85a965607d8feeb8d14587335a0ab6ccb03`에 대한 누적 원문·근거 대조를 기록한다. 2,105개·8,420좌표 전수 자체 검토를 마쳤으며 미독 0, 확인된 미해결 표현 결함 0이다. 외부 Reviewer의 독립 판정은 아니다. 전체 native 효과나 게임의 모든 용도를 확정한 것은 아니며 항목별 upstream evidence gap은 별도로 남겼다.

네 표면 각각 present 1,981 / absent 124다. 원래 121 부재와 비교해 BucketConcreteFull, Cornmeal, Rubberducky2의 3개가 늘었다. 자체 관리만 남은 이 품목은 공개 목적의 근거 부족으로 기록하며 부재 증가를 품질 개선 실적으로 계산하지 않는다. 약품 6종과 발전기의 중간 부재는 최종 상태가 아니다. 약품은 실제 선언 Tooltip의 명시적 약효, 발전기는 야외 주유기 급전 설명과 메뉴 조건을 기존 owner에서 보완했다. 열린 우산 4종을 포함한 보완은 20 facts이며 원래 semantic 28,145 + acquisition 1,057에 더해 총 29,222 facts를 보존한다.

공통 public plan은 독립 활용을 compact와 expanded 모두에 남기고 자체 관리/실행 bookkeeping을 내부 처리한다. 재료·결과·도구 대안은 실제 관계의 범위로 묶고 고랑당 씨앗 소비량 및 자동 ‘도구 없이’ 문장은 공개하지 않는다. 검토 보조 코드는 기존 자료를 전사·집계한 일회성 수단이며 canonical validator가 아니다. 전환 직전 dirty bytes는 `docs/review/uses/before.zip`, 전체 원문 비교는 `docs/iris_dvf_description_review.html`에 있다.

이 시점의 자동 검사/B·C 후보 생성 결과는 아래 후속 closeout에 기록한다. 실제 PZ 표시는 미관찰이며 수락하지 않는다.

## 2026-09-12 player-use 전환 closeout — implemented_only

계획 `iris_dvf_player_use_description_transition_plan.md`의 공통 용도 표현·제한적 기존 owner 보완·전수 자체 원문 검토·새 B→C 후보 연결을 구현했다. 실제 PZ 관찰은 **unvalidated_but_in_scope**다. 사용자 사전 owner approval은 적용했으나 이전 후보의 실제 표시 수락을 새 ZIP에 승계하지 않았다. live/current 활성화, 게임 설치, commit/push/release는 하지 않았다.

최종 descriptions SHA256은 `ffde6886d117482336159de49dd1ddc8ff075df2499217b09400542a895246b0`, blocks는 `0c806c345cbe512129c8a4af27ecd85a965607d8feeb8d14587335a0ab6ccb03`다. 직전 `fc8c11...` 원문에서 봉합의 ‘붕대가 감기지 않은’ 조건 누락을 복구했다. 영향을 받은 Needle/SutureNeedle/Thread 3개·12좌표를 다시 읽고 항목 기록과 HTML에 반영했다. 총 2,105개·8,420좌표, 각 surface present 1,981 / absent 124, 미독 0·확인된 잔여 표현 결함 0이라는 자체 판정이다. 근거 부족과 native 효과 완전성의 한계는 개별 uncertainty에 남겼다.

### 기존 검사 실행 결과

모든 명령은 repository 루트 PowerShell에서 실행했다. 아래 첫 묶음의 전체 종료 상태는 실패이며 성공으로 바꾸어 기록하지 않는다. 변경 없는 블록 node의 성공 결과는 계획 §7에 따라 공유하고, 설명 수정의 영향을 받은 설명/B만 다시 실행했다. 별도 validation-of-validation이나 추가 confidence 검사는 실행하지 않았다.

```powershell
uv run --project .\Iris\tooling python -I -B -m pytest --noconftest -c .\Iris\tooling\pyproject.toml .\Iris\build\description\v2\tests\test_layer3_composition.py::test_layer3_composition_contract .\Iris\build\description\v2\tests\test_layer3_description_composition.py::test_layer3_description_composition .\Iris\tooling\tests\test_tooltip_t2_projection.py::test_s2_supply_and_owner_integration --basetemp .\.tmp\v -q -s --tb=short
# exit 1: 1 failed, 2 passed in 121.45s. 블록/B node 성공, 설명 node 봉합 조건 누락 실패.

uv run --project .\Iris\tooling python -I -B -m pytest --noconftest -c .\Iris\tooling\pyproject.toml .\Iris\build\description\v2\tests\test_layer3_description_composition.py::test_layer3_description_composition --basetemp .\.tmp\w -q --tb=short
# exit 0: 1 passed in 6.57s.

uv run --project .\Iris\tooling python -I -B -m pytest --noconftest -c .\Iris\tooling\pyproject.toml .\Iris\tooling\tests\test_tooltip_t2_projection.py::test_s2_supply_and_owner_integration --basetemp .\.tmp\x -q -s --tb=short
# exit 0: 1 passed in 102.42s.

$env:IRIS_MENU_TOOLTIP_CANDIDATE = '.tmp/tooltip/run-frlycdx2/s/.tmp/package/Iris.zip'
uv run --project .\Iris\tooling python -I -B -m pytest --noconftest -c .\Iris\tooling\pyproject.toml .\Iris\build\description\v2\tests\test_layer3_product_integration.py::test_product_contract --basetemp .\.tmp\y -q -s --tb=short
# exit 0: 1 passed in 79.60s.
```

B 자식의 repository Lua syntax, supply runtime, package 명령은 각각 exit 0이었다. C 자식의 source/stage Lua syntax(388 files), Browser/Wiki expanded 모델(4,210 locale 상태), Tooltip runtime(2,280 keys), Layer 4 모델, package admission fault, package 및 actual ZIP pointer 명령도 각각 exit 0이었다. 검사에서 출력된 Fixture.Layout fit failure는 의도된 화면 용량 실패 fixture이며 실제 PZ fit 관찰이 아니다. C node 안에서 두 build 일치, 원문/refs/scope/order/detail links, B 106개 retained member bytes, 중단·rollback·idempotence·source pointer 보존을 검사했다. 실행 중 상태/진행을 확인했으며 비정상 장기 실행이나 강제 중단은 없었다. Python 생성 중 잘못된 write_result 인자 호출은 실패로 끝났고 정상 호출로 생성했으며 테스트 성공으로 집계하지 않는다.

### 최종 후보와 인계

- 새 B: `.tmp/tooltip/run-frlycdx2/s/.tmp/package/Iris.zip`
  - SHA256 `b6af414a583f75573e5eac308f655564aa3e0348266ad4d9a2474222396dddaa`
  - owner `ttp-d01c54c44ceac5664796b746038c8127dc678f8345ea5e04c5a6204b0369d6e8`
  - supply `ada0ac7184397440565bfc22bb5bd652f1275365804e0b75134f4e357347a488`
- 새 공통 C: `.tmp/menu/run-7ztpp37i/p/Iris.zip`
  - SHA256 `db2174e72e5acc50db8651c538343e6adc432950015d04d44b4da5c7145a9796`
  - product `l3p-7514d54f6f3d27e727a3b78b14f38e9f9c7d74d49a185c938b709c5f2d53d414`

C는 위 새 B ZIP을 명시적 tooltip_ref로 받아 동일 corpus와 독립 owner를 결속했다. 소스의 과거 ACCEPTED_TOOLTIP/ACCEPTED_DESCRIPTION 상수는 historical 수락값이며 이 successor 후보의 기본값으로 재해석하지 않는다. 재생성 시 `build_menu_product(root, output, tooltip_ref=binding(root, 새_B_경로))` 또는 위 기존 통합 node의 명시적 환경 입력을 사용한다. 첫 B `run-b7nrzztu`는 봉합 교정 전 후보이므로 최종 인계 대상이 아니다.

실제 PZ에서 확인할 남은 범위는 계획 Change 7의 같은 C ZIP에 대한 KO/EN 긴 compact·복수 활용·부재·Alt 및 S1/S3/S4 공존, Browser/Wiki 긴 expanded·좁은 폭·스크롤 끝·Layer 4 접근이다. PZ 버전/해상도/UI scale/관찰자는 unknown / not reported이며 표시 수락을 주장하지 않는다. 추가 proof artifact나 검사기 신설 없이 implemented_only로 closeout한다.

## 2026-09-12 의미 판정 재개 — partial

후속 실제 원문 검토에서 공통 점화 frame의 내부 지원 문구, 도구 설명의 수행 요건 나열, 음식 미끼의 추상적 주어, 차량 부품 목적의 미확정 문제가 확인되었다. 위 ‘잔여 표현 결함 0 / 실제 PZ만 남음’ 판단을 철회한다. ledger의 읽기 이력과 자동 검사 결과는 보존하지만 의미 적합성 수락으로 사용하지 않는다. 기존 ffde6886... corpus와 run-7ztpp37i C ZIP은 당시 자동 검사 통과 후보이며 의미 품질 승인 후보가 아니다. 공통 규칙과 같은 의미/조합 범위를 교정하고 재판정할 때까지 partial이다.

## 2026-09-12 공통 목적군 교정 후 후보 — implemented_only

의미 판정 재개 이후 확인된 공통 표현을 교정했다. 이번 상태는 구현·누적 전수 자체 원문 검토 및 영향 범위 재판정·기존 자동 검사·동일 corpus B/C 후보 연결까지다. 실제 PZ 표시는 미관찰이다. 이전의 포괄적인 ‘표현 결함 0’ 선언은 복원하지 않으며, 자동 검사의 성공을 의미 품질 승인으로 해석하지 않는다. 외부 Reviewer의 독립 판정은 수행하지 않았다.

최신 descriptions는 `2301a4a4b8d24a28447ea53e3e47dd7143b362fb9e3b3b2531cf3152e4491e30`, blocks는 `0c806c345cbe512129c8a4af27ecd85a965607d8feeb8d14587335a0ab6ccb03`다. 2,105개/8,420좌표와 각 표면 present 1,981 / absent 124를 유지한다. 원래 semantic 28,145 + acquisition 1,057 + 기존 owner correction 20 = 29,222 facts이며 재개 후 사실 보완을 더하지 않았다. 항목 기록과 HTML은 이 원문으로 갱신했다.

### 의미 교정과 재판정의 범위

- 점화: 라이터·성냥 등 점화 도구와 휘발유 공급자의 역할을 분리했다. 같은 점화 방법이 실제로 연결된 대상만 묶고 화로에 불쏘시개 지원을 전이하지 않는다. 내부 지원 범위 문장과 반복 수행 요건은 용도를 대신하지 않는다.
- 음식 미끼: 음식 자체를 먹기/요리/미끼 활용의 주어로 삼았다. 익히지 않고 섞지 않았다는 조건은 미끼 절에만 적용한다. 특정 동물의 미끼 수용이나 포획을 새로 보장하지 않는다.
- 복합 도구: 전자기기와 라디오/TV 제작·분해, 금속 단조, 목공·건축·가구 작업 등 실제 활동 집합에서 목적군을 만든다. 같은 용도의 하위 나열을 줄이며, 차량/무기 부품 작업·창 부착·근접 공격 같은 독립 활용을 없애지 않는다. 마지막 교정의 실제 40개 도구 compact 조합과 변경 expanded를 다시 읽었다. 반죽 세부 종류는 expanded에 남고 compact에서는 반죽 준비로 묶인다. 드라이버 expanded는 ‘드라이버 필요’를 반복하지 않고 회수 결과 및 기기/기술에 따른 차이를 설명한다.
- 다른 공통 적용 범위: 보관/운반, 포장/음식 분배, 배관, 바리케이드, 마찰 점화, 발전기/엔진 수리, 판재 변환의 손실 범위를 같은 역할·대상·관계 조합으로 재판정했다. 재개 중 670개 영향 범위의 검토 뒤 40개 도구 조합을 추가 교정한 누적 기록이며 두 수를 독립 항목으로 더하지 않는다.
- 차량 부품: 브레이크 9, 서스펜션 6, 머플러 9, 배터리 3, 타이어 9, 앞/뒤 유리 6의 총 42개는 설치·관리 사실만으로 제동/승차감/소음/시동 전원/접지/보호 목적을 확정할 수 없다. 해당 이유를 개별 uncertainty 및 purpose_unresolved에 기록했다. 이들은 ‘용도 설명 적합’으로 수락하거나 구현된 활용으로 계산하지 않는다. 연료 저장/공급, 수납, 개폐/잠금 등 별도 명시 기능이 있는 부품에는 이 결론을 일괄 적용하지 않는다.

이전 ledger의 일반적 이유는 refs 보존과 실제 이해 가능성을 충분히 구별하지 못했다. 새 기록은 전체 원문의 기존 읽기 이력과 재개 후 실제 변경 범위의 의미 재판정을 구분한다. 자동 분류/문장 수/refs 수를 자체 판정의 증명으로 쓰지 않는다. 전체 native 효과나 모든 잠재 활용을 조사했다는 뜻도 아니다. 근거 부족 항목을 표현 실패의 대체 분류로 사용하지 않았다.

### 마지막 필수 검사와 후보

재개 후 중간 테스트는 실행하지 않았다. 정상 producer로 원문을 교정·검토한 다음 아래 기존 node만 마지막에 실행했다. 변경 없는 블록 node는 위 역사적 실행의 성공 결과를 재사용했다. 실행 중 약 20–30초 간격으로 상태를 확인했고 정체나 강제 중단은 없었다.

```powershell
uv run --project .\Iris\tooling python -I -B -m pytest --noconftest -c .\Iris\tooling\pyproject.toml .\Iris\build\description\v2\tests\test_layer3_description_composition.py::test_layer3_description_composition .\Iris\tooling\tests\test_tooltip_t2_projection.py::test_s2_supply_and_owner_integration --basetemp .\.tmp\aa -q -s --tb=short
# exit 0: 2 passed in 91.80s

$env:IRIS_MENU_TOOLTIP_CANDIDATE = '.tmp/tooltip/run-cr4yy73j/s/.tmp/package/Iris.zip'
uv run --project .\Iris\tooling python -I -B -m pytest --noconftest -c .\Iris\tooling\pyproject.toml .\Iris\build\description\v2\tests\test_layer3_product_integration.py::test_product_contract --basetemp .\.tmp\ab -q -s --tb=short
# exit 0: 1 passed in 72.08s
```

B 자식의 Lua 문법, supply runtime, package는 각 exit 0이다. C 자식의 388개 Lua 문법, Browser/Wiki 4,210상태 모델(font stub), Tooltip 2,280 keys, Layer 4 모델, package admission, package 및 실제 ZIP pointer도 각 exit 0이다. 같은 node가 원문/refs/scope/order/detail links, 두 build 결정성, B 106개 member 보존, rollback/idempotence/source pointer를 다뤘다. Fixture.Layout fit failure 출력은 의도된 실패 fixture이며 실제 PZ 폰트/4줄 수락은 아니다. 추가 검사기·proof artifact·별도 봉인 단계를 만들지 않았다.

| 후보 | 경로 | SHA256 |
| --- | --- | --- |
| B | `.tmp/tooltip/run-cr4yy73j/s/.tmp/package/Iris.zip` | `f340096061541584b5b5a92542cb249c399ff40bd729df1103b3ba61b3bb6254` |
| C | `.tmp/menu/run-5b363prk/p/Iris.zip` | `a55538e4cdaf47c771258a2c75d33dce0f93ba66cc524eb465873d1fa0086080` |

B owner는 `ttp-d910564eb9b6a034f2df5220ae14bb3b43d03345725320d8ab7252f79bdf98dd`, supply는 `07b5a19aa9caef9d1576df06c78da3e4a87b1d485059e912dc735f62c1d5a912`다. C product는 `l3p-8c05e8f0fdaf60a23e47984a2e1e53f13795fa4d6c5340a48c5ff01d37dceee7`이며 위 B를 명시적 tooltip_ref로 소비했다. 과거 ACCEPTED_* 상수는 historical binding으로 유지한다. 이전 ffde corpus/C 후보는 역사적 자동 검사 결과이며 새 후보의 품질 근거가 아니다.

실제 PZ에서의 Tooltip 네 물리적 줄, KO/EN 실제 폰트, Alt 및 S1/S3/S4 공존, Browser/Wiki 좁은 폭·긴 expanded·스크롤 끝·Layer 4 접근은 계획의 남은 관찰 범위다. 버전/해상도/UI scale/관찰자는 미보고다. 저장소 밖을 탐색하거나 게임 설치·live/current 전환·배포를 하지 않았다. 새 후보를 complete 또는 strict production 수락으로 선언하지 않는다.


## 2026-09-13 공통 공개 문장 경로 재적용

이번 시작 시점 `c3dfca3d4843d321899e624ba4150d994c3410a5bd289e1f289788819a45174e` 대비 **726개 아이템 / 2,429개 표면**이 바뀌었다. 이전 670개/40개/통조림/ingredient21개 등의 교정 건수와 합산하지 않는다. 전체 2,105개/8,420좌표와 각 표면 present1,981 / absent124를 유지한다.

2,105개 × KO/EN × compact/expanded의 실제 문면을 네 문자열 조합 679개와 공유 segment 사전으로 펼쳐 읽은 뒤, 후속 변경된 기술책/물/지면작업/역할 주어/의료/패치/조리 포함/순서 문면을 다시 읽었다. 문자열 중복은 읽기 분량만 줄였으며 서로 다른 관계의 의미 판정을 자동 공유하지 않았다. 지적 경로는 실제 payload, 적용 qualifier, role 및 result_consumption/recipe result 관계와 대조했다. 모든 관계의 원천 재조사나 독립 품질 승인은 수행하지 않았으며 refs 보존·건수·자동검사는 문장 품질의 증거로 대체하지 않는다.

- 특수 도구 요약과 context-role continuation에도 admitted target refinement를 전달한다. 몰드 탄종을 보존하고 다목적 단조 도구는 상위 목적을 유지한다.
- 탄띠는 실제 reload_speed_setting multiply_1_15와 산탄/비산탄 착용 범위를 효과 문장으로 표현한다. 장전 시간 감소를 추론하지 않는다.
- 개조부품 장착/제거와 탄창 삽입/탄약 채움/잔탄 회수를 보존하며 다른 도구의 비소모 설명을 제거한다.
- 붕대11개 감염 위험을 붕대 용도와 결합하고 화상6개 시술 강도/통증을 공개 목적에서 제외한다. 패치5개는 다른 투입물 요구와 잘못된 재료 역할을 제거한다.
- 같은 무조건 tool 역할의 음식 준비가 반죽 준비를 포함하는 4개와 Bowl container 목적을 검토해 포함 처리한다. 기존 ingredient21개와 별도 범위이며 서로 더해 변화량으로 쓰지 않는다.
- 변환 전후 주어, 낚싯줄 파손 후 실제 잔류물, 돌망치 건축 마모 범위, 물 사용 표적과 오염수 위험을 유지한다.
- 상위 compact material 문장을 작성한 순서의 fact traversal을 expanded에 전달한다. 전역 품목 우선순위나 Lua 문구 재작성을 추가하지 않는다.

CannedMilk는 원본 generic eat dispatch와 개봉 결과의 실제 `drink_food_contents`가 충돌할 때 확인된 result_consumption을 우선해 “통조림 따개로 개봉해 내용물을 마실 수 있다”로 표현한다. CannedMilkOpen의 실제 음용 용도 및 조리 용도와 일치한다. CannedFruitBeverageOpen은 admitted `eat_food`이므로 이름만으로 drink를 새로 만들지 않았다. 개봉 도구, 확인된 결과, 요리 포함, 원본/결과 구분과 기존 통조림 소비 교정은 유지했다.

RippedSheets expanded의 붕대 용도와 감염 위험은 한 use_unit이며 화상 강도/시술 통증이나 패치의 다른 재료 요구를 별도 용도로 출력하지 않는다. RollingPin compact는 “음식 준비에 쓰는 도구. 근접 공격에 쓸 수 있다.”이며 expanded는 두 독립 용도다. Plank compact의 승인된 상위 목적을 유지하고 expanded도 목공/건축부터 전개한다. 이 작업에서 Tooltip의 최대 네 줄이나 폰트/폭은 바꾸지 않았고 Lua에 문장 합성기를 추가하지 않았다.

새 descriptions SHA256은 `ff2e93b65270c8d226dfcce5e9148fe7f5c5d69927f721d87394fccb9089443b`, blocks는 변경 없이 `9d68e982cd508b3a4beafc9d1a8892668c9470d4581f7db0d1761e602926e161`다. 기존 uses/structure JSON에 이전 locales/판정을 보존하고 현재 원문과 이번 기록을 추가했다. 이전 classification/axis 판단을 새 전체 품질 승인으로 자동 승계하지 않는다. `iris_dvf_descriptions.html`은 현재 8,420개 원문과 producer use_units로 갱신했고, `iris_dvf_description_review.html`에는 이번 시작 시점과 현재 네 표면을 비교할 수 있도록 기록했다.

문구를 고정한 뒤 아래 최소3노드를 한 묶음으로 실행했으며 **3 passed in 148.22s, exit 0**이다. 검사 중 producer를 바꾸지 않았고 추가 confidence 검사나 전체 Run A/B를 실행하지 않았다.

```powershell
$env:IRIS_SHARED_MENU_VALIDATION='1'
uv run --project .\Iris\tooling python -I -B -m pytest --noconftest -c .\Iris\tooling\pyproject.toml .\Iris\build\description\v2\tests\test_layer3_description_composition.py::test_layer3_description_composition .\Iris\tooling\tests\test_tooltip_t2_projection.py::test_s2_supply_and_owner_integration .\Iris\build\description\v2\tests\test_layer3_product_integration.py::test_product_contract --basetemp .\.tmp\common -q -s --tb=short
```

기존 제품 노드가 Lua 문법388파일, Browser/Wiki4,210상태(font stub), Tooltip2,280키, 공통 B/C stage와 ZIP 포인터, 복구/롤백/멱등성을 다뤘다. 명령 로그는 `.tmp/prose/final-tests.log`다.

- 공통 제품: `l3p-344df05eef9f14cb34a34e9bf46b28e3d83bd6b993c99abed2aec6ad16830660`
- ZIP: `.tmp/menu/run-6ipav47h/p/Iris.zip`
- ZIP SHA256: `129e30872e0a2326a17e4432a769eaf254315ff5f9d63a2c5bed5f8c71ea023c`
- 직접 mod root: `.tmp/menu/run-6ipav47h/p/Iris` (`mod.info`와 `media` 확인)
- S2 후보: `.tmp/tooltip/run-yftu78yd/s/.tmp/package/Iris.zip`

최종 상태는 **implemented_only**다. 전체 표현 결함0, 독립 품질 수락 또는 strict production 수락을 선언하지 않는다. absent124, 차량42개 구체 목적 미확정, unresolved 관계와 exact ID L4 공급 공백은 남긴다. 실제 PZ에서 KO/EN 폰트, Tooltip 네 물리줄/Alt/S1·S3·S4 공존, Browser/Wiki 좁은 폭·긴 설명·스크롤 끝·Layer4 접근은 미관찰이다. 저장소 밖 게임 설치나 current/live 전환, commit/push/배포는 하지 않았다.


## 사용자 후속 A~D 전체 조사 및 공통 교정 (2026-09-13)

상태: **implemented_only**. 실제 PZ 관찰·전체 품질 수락은 아니다.

기준 ff2e93 대비 기존 전체2105아이템/8420좌표 독해 기록과 679개 네문자열 조합 재독을 이어 A~D를 판단했다. 공통 수정 후 새로 나타난333개 localized segment를 읽고 그릇분배 continuation과 로프·찜질제의 최종5아이템 문면을 다시 읽었다. 원천 관계가 다른 항목은 같아 보이는 문구만으로 일괄 판정하지 않았다. 집계는 사람이 읽은 판정의 전사이며 자동 품질 증명·새 검증 권위가 아니다.

| 의미축 | 조사 아이템 | 조사 좌표 |
|---|---:|---:|
| A | 35 | 140 |
| B | 9 | 36 |
| C | 161 | 442 |
| D | 354 | 1280 |

중복 제외 조사547아이템/1850좌표. 조사 집계는 삭제목록이나 실제 변경수가 아니다.

배타적 교차집계(빈 축은 조사상 해당 없음):

{"items": {"": 1558, "D": 342, "C": 156, "A": 35, "B+D": 7, "B": 2, "C+D": 5}, "coordinates": {"": 6570, "D": 1232, "C": 422, "A": 140, "B+D": 28, "B": 8, "C+D": 20}}

실제 기준 대비 변경: 539아이템 / 1878좌표.

- A: 식품의 식사·조리 용도가 확인된 범위에서 개별 분할·그릇 분배 결과와 하위 팬 준비 절차를 공개 용도에서 제외했다. 결과 관계와 원천 사실은 유지한다.
- B: 선택적 식기와 차량 정비 열쇠 요건을 내부로 분류했다. 음식 준비 도구·창 부착·근접 공격, 맞는 문·차량 열쇠 사용은 공개 용도로 유지한다.
- C: 문해·현재 배율, 로프 수량·힘·회수 상태, 지도 편집 도구 조합, 일반 성공 비보장과 반복 실행 조건을 목적 문장에서 줄였다.
- D: 물 저장·급수·혈흔 세척·소화·음용, 도색·표식, 가구 이동·차량 수납·좌석·개폐, 매체·의료·설치 목적을 각각의 공통 함수와 역할 표현에서 간결하게 썼다.
- 수정 중 그릇 분배 직접 기능을 숨긴 뒤 재료 역할 문장이 남는 경로도 확인해 같은 의미 범위로 제외했다. 특정 FullType나 완성 문장 교체 규칙은 추가하지 않았다.
- 씨앗 봉투7의 실제 결과 수량50과 Wrench의 엔진 회수 한계·상태0 결과는 유지했다. 모든 숫자·변환·선택 기능·한계를 삭제하는 정책이 아니다.
- 로프2는 설치 후 상승·제거와 건축·통나무 묶기를 유지한다. 찜질제3은 다친 부위에 바르는 물품으로만 설명하며 새로운 치료 효과를 추정하지 않는다.

반례로 음식분할 도구13과 Bowl 용기 용도, 캔 개봉→소비·조리, 의류 회수·연료·시트 로프, 실제 탄약 호환 및 착용범위15% 효과, 낚싯줄 파손·미끼 소실, 봉합 보조 시간 단축·의료 감염/독성 위험을 유지했다.

- 124 absent 유지
- 차량42 구체 목적 미확정 유지
- Muffintray_Biscuit/Watermelon2 상위 식사·조리 근거 부재로 음식결과 숨김 일반화 보류
- 기술책 정확한 숫자 레벨 범위는 이번 admitted facts에 별도 확정되지 않아 일반 범위 문구 유지; 최대배율은 실제 state값 유지
- unresolved relations 및 L4 exact ID 공급 공백 유지
- 실제 PZ 폰트·툴팁4물리줄·Alt·메뉴 스크롤 미관찰
- 전체 표현 결함0·품질 수락 선언 아님

Descriptions SHA256: `cd695ac810d58443012686bd3bc029dbbd09468d2abbe49ccad1b944d2be9a25`

Blocks SHA256: `9d68e982cd508b3a4beafc9d1a8892668c9470d4581f7db0d1761e602926e161`

최종 검증과 신규 후보는 아래 완료 기록에 별도로 기재한다. 중단 실행은 F 출력 후 요약 전 종료됐으며 최종 PASS가 아니다. 기존 콩통조림 기대값 잔존을 코드에서 확인했으나 중단 로그만으로 실패 원인을 확정하지 않는다.


### 후속 최종 검증 및 후보

아래 정확한 명령은 종료 코드 **0**, **3 passed in 154.70s**로 완료됐다.

```powershell
$env:IRIS_SHARED_MENU_VALIDATION='1'
uv run --project .\Iris\tooling python -I -B -m pytest --noconftest -c .\Iris\tooling\pyproject.toml .\Iris\build\description\v2\tests\test_layer3_description_composition.py::test_layer3_description_composition .\Iris\tooling\tests\test_tooltip_t2_projection.py::test_s2_supply_and_owner_integration .\Iris\build\description\v2\tests\test_layer3_product_integration.py::test_product_contract --basetemp .\.tmp\common -q -s --tb=short
```

실행 로그: `.tmp/prose/followup-tests.log`. 검증은 기존 세 노드 묶음이며 추가 Gate나 전면 원천 재조사가 아니다. Lua 구문388파일, Browser/Wiki4210상태(font stub), Tooltip2280키, 패키지 수용·ZIP pointer·rollback/idempotence를 기존 노드에서 확인했다. 실제 PZ 관찰은 하지 않았다.

- 최종 변경: 기준 ff2e93 대비 **539아이템 / 1878좌표**. 조사547/1850과 별개다.
- product: `l3p-debcf5c477a0761d435d2e3945f6bb79c6bd26b046f591a217327483d1c82624`
- ZIP: `.tmp/menu/run-20rthxop/p/Iris.zip`
- ZIP SHA256: `f7aef9da4c24dede3fe0b234d3220f8bacd895f956cdd8078c792652fc1ea948`
- direct mod root: `.tmp/menu/run-20rthxop/p/Iris` (`mod.info`, `media` 확인)
- 상태: **implemented_only**. 이전 후보 보존, 라이브 설치·커밋·푸시 없음.

최종 로프 문면: “설치해 위층으로 올라가는 데 쓸 수 있는 로프다. 설치한 로프를 제거할 수 있다.” / “It is rope that can be installed for climbing to an upper floor. The installed rope can be removed.” 건축·통나무 묶기도 유지했다.

최종 찜질제 문면: “다친 부위에 바르는 약초 찜질제다.” / “It is an herbal poultice for application to an injured body part.” 적용 가능 조건은 내부 사실로 유지하고 치료 효과를 발명하지 않았다.


## 개봉 식품 결과명 공통 교정 (2026-09-13)

상태: **implemented_only**.

기준 cd695ac 대비 해당 개봉 관계29개와 결과명·섭취·조리·도구를 읽고, 재생성된29아이템의 KO/EN compact/expanded116좌표 실제 문면을 읽었다. 전체 원천 재조사나 새 Gate는 수행하지 않았다.

- 공통 개봉·섭취 문장의 내용물/its contents를 실제 declared 개봉 결과의 KO/EN 표시명으로 바꿨다. 요리 용도에서도 같은 결과명을 반복한다.
- 캔19·병식품9·달걀곽1의 기존 공통 문형 소비범위29아이템/116좌표를 확인했다. 각 관계는 단일 확정 결과명을 가지며 식별 미확정은 없다.
- 먹기27·마시기2, 조리28·조리 없음1, 따개16·도구 관계 없음13의 기존 구분을 유지했다. 개사료 조리, 원물 미끼, 그릇 콩 제작을 추가하지 않았다.
- 버섯스프/Mushroom Soup, 스프/Vegetable Soup 등 언어별 원본 표시명을 유지하고 번역이나 아이템 ID로 이름을 추정·축약하지 않았다.

기준 cd695ac 대비 **29아이템/116좌표** 변경. 전체2105/8420과 각 표면 present1981/absent124 유지.

**Base.CannedCarrots2**

KO 전: 통조림 따개로 개봉해 내용물을 먹을 수 있다. 꺼낸 당근을 요리 재료로도 쓸 수 있다.

KO 후: 통조림 따개로 개봉해 당근을 먹을 수 있다. 꺼낸 당근을 요리 재료로도 쓸 수 있다.

EN 전: It can be opened with a Can Opener to eat its contents. The extracted Carrots can also be used as a cooking ingredient.

EN 후: It can be opened with a Can Opener to eat the Carrots. The extracted Carrots can also be used as a cooking ingredient.

**Base.TinnedSoup**

KO 전: 통조림 따개로 개봉해 내용물을 마실 수 있다. 꺼낸 스프를 요리 재료로도 쓸 수 있다.

KO 후: 통조림 따개로 개봉해 스프를 마실 수 있다. 꺼낸 스프를 요리 재료로도 쓸 수 있다.

EN 전: It can be opened with a Can Opener to drink its contents. The extracted Vegetable Soup can also be used as a cooking ingredient.

EN 후: It can be opened with a Can Opener to drink the Vegetable Soup. The extracted Vegetable Soup can also be used as a cooking ingredient.

**Base.CannedMushroomSoup**

KO 전: 통조림 따개로 개봉해 내용물을 먹을 수 있다. 꺼낸 버섯스프를 요리 재료로도 쓸 수 있다.

KO 후: 통조림 따개로 개봉해 버섯스프를 먹을 수 있다. 꺼낸 버섯스프를 요리 재료로도 쓸 수 있다.

EN 전: It can be opened with a Can Opener to eat its contents. The extracted Mushroom Soup can also be used as a cooking ingredient.

EN 후: It can be opened with a Can Opener to eat the Mushroom Soup. The extracted Mushroom Soup can also be used as a cooking ingredient.

**Base.CannedSardines**

KO 전: 개봉해 내용물을 먹을 수 있다. 꺼낸 정어리를 요리 재료로도 쓸 수 있다.

KO 후: 개봉해 정어리를 먹을 수 있다. 꺼낸 정어리를 요리 재료로도 쓸 수 있다.

EN 전: It can be opened to eat its contents. The extracted Sardines can also be used as a cooking ingredient.

EN 후: It can be opened to eat the Sardines. The extracted Sardines can also be used as a cooking ingredient.

**Base.Dogfood**

KO 전: 통조림 따개로 개봉해 내용물을 먹을 수 있다.

KO 후: 통조림 따개로 개봉해 개 사료를 먹을 수 있다.

EN 전: It can be opened with a Can Opener to eat its contents.

EN 후: It can be opened with a Can Opener to eat the Dog Food.

Descriptions SHA256: `0b7d82d82209bf8b554eb186b6f057b3ed8e28be3d67d5531bcf05d52e0f1271`

Blocks SHA256(불변): `9d68e982cd508b3a4beafc9d1a8892668c9470d4581f7db0d1761e602926e161`

새로운 개봉·소비 관계나 요리 근거는 추가하지 않았다. 최종 검증과 후보는 아래 완료 기록에 기재한다.


### 개봉 결과명 교정 최종 검증 및 후보

문구 고정 뒤 기존 최소3노드 묶음 한 번 실행: **3 passed in 142.59s (0:02:22)**, 종료 코드 **0**.

```powershell
$env:IRIS_SHARED_MENU_VALIDATION='1'
uv run --project .\Iris\tooling python -I -B -m pytest --noconftest -c .\Iris\tooling\pyproject.toml .\Iris\build\description\v2\tests\test_layer3_description_composition.py::test_layer3_description_composition .\Iris\tooling\tests\test_tooltip_t2_projection.py::test_s2_supply_and_owner_integration .\Iris\build\description\v2\tests\test_layer3_product_integration.py::test_product_contract --basetemp .\.tmp\common -q -s --tb=short
```

로그: `.tmp/prose/opened-tests.log`. Blocks 불변으로 별도 block 검사를 추가하지 않았다. 새 Gate·전면 원천 재조사·추가 confidence 검사는 없다.

- product: `l3p-6b6682f524a190f6dc8114141aa0450023e6fb66856b4d848e5675f9ae4ec3f6`
- ZIP: `.tmp/menu/run-1z4n2zmh/p/Iris.zip`
- SHA256: `06edab60f62cce11fd2f85ae3f23e5584826bad8f4045721bf6b7836c01fc1b6`
- direct mod root: `C:\Users\MW\Downloads\coding\PZ\.tmp\menu\run-1z4n2zmh\p\Iris`
- 상태: **implemented_only**. 실제 PZ 미관찰. 이전 run-20rthxop 후보 보존. 라이브 설치·커밋·푸시 없음.


## 파스타 조리재료 및 물 보관 문형 공통 교정 (2026-09-13)

상태: **implemented_only**.

현재 exact ID와 채택된 Pasta eat_food의 원천 관측·normalized fact·공개 문장을 대조하고 grain 역할4개 및 물 공통함수49아이템을 확인했다. 변경51아이템/204좌표의 실제 KO/EN 네문자열 조합17개를 읽었다. 전면 원천 재조사·새 Gate는 수행하지 않았다.

- Base.Pasta는 원물의 native_eating accepted eat_food가 채택→normalized→공개 양표면에 이미 있었다. 섭취 근거 누락이 아니라 grain_preparation 재료 문장의 분리·자기명 반복 문제다.
- Pasta/Rice ingredient2를 요리 재료 상위 표현으로 정리했다. WaterPot/WaterSaucepan의 같은 활동에 속한 용기 역할은 유지한다. 원물과 조리 결과의 섭취를 혼동하거나 새로운 fact를 추가하지 않았다.
- 물 용기49의 store_water/carry_water/receive_poured_water 공통 요약을 공급 경로에 종속되지 않는 보관·운반 목적으로 썼다. WATER_STORAGE는 실제 수원 채우기 근거이고 WATER_TRANSFER는 별도 용기간 이송이다.
- 물받기 관계를 삭제하지 않고 특정 공급 경로만 필수처럼 읽히는 문구를 고쳤다. 물 옮기기·시설 및 작물 급수·차량 혈흔·소화·음용·오염수 위험과 다른 독립 용도를 보존한다. 모든 수원·자동 급수·정수 효과를 주장하지 않는다.

기준 0b7d82 대비 **51아이템/204좌표** 변경: ingredient2+water49. 전체2105/8420과 각 표면 present1981/absent124 유지.

원천 관측: `scripts/items_food.txt L4808-L4824`의 원물 Pasta(Type Food, CantEat 없음), 메뉴의 isCantEat 조건과 ISEatFoodAction의 Eat 호출이 채택 fact `fact:ad362bed7f802a635e26d823b7bfa378413b4e61f0a3ef568e3c3e30bf35790c`에 연결돼 있다. 공개 먹기 문장은 수정 전에도 존재했다.

**Base.Pasta**

KO 전: 먹을 수 있다. 덫의 미끼로도 쓸 수 있다. 파스타 요리 준비에 쓰는 재료.

KO 후: 먹거나 요리 재료로 쓸 수 있다. 덫의 미끼로도 쓸 수 있다.

EN 전: It can be eaten. It can also be used as trap bait. An ingredient for preparing dishes with Pasta.

EN 후: It can be eaten or used as a cooking ingredient. It can also be used as trap bait.

**Base.Rice**

KO 전: 먹을 수 있다. 덫의 미끼로도 쓸 수 있다. 쌀 요리 준비에 쓰는 재료.

KO 후: 먹거나 요리 재료로 쓸 수 있다. 덫의 미끼로도 쓸 수 있다.

EN 전: It can be eaten. It can also be used as trap bait. An ingredient for preparing dishes with Rice.

EN 후: It can be eaten or used as a cooking ingredient. It can also be used as trap bait.

**Base.Teacup**

KO 전: 다른 용기의 물을 받아 보관, 운반할 수 있다.

KO 후: 물을 담아 보관하거나 운반할 수 있다.

EN 전: It can store and carry water received from other containers.

EN 후: It can hold water for storage or carrying.

**Base.MugWhite**

KO 전: 다른 용기의 물을 받아 보관, 운반할 수 있다.

KO 후: 물을 담아 보관하거나 운반할 수 있다.

EN 전: It can store and carry water received from other containers.

EN 후: It can hold water for storage or carrying.

**Base.WaterBottleFull**

KO 전: 다른 용기의 물을 받아 보관, 운반하고 다른 용기로 옮길 수 있다. 담긴 물은 저장 시설 급수, 작물 급수, 차량 혈흔 세척, 소화, 음용에 쓸 수 있다 (오염수 음용은 중독 위험).

KO 후: 물을 담아 보관하거나 운반할 수 있다. 다른 용기로 물을 옮길 수도 있다. 담긴 물은 저장 시설 급수, 작물 급수, 차량 혈흔 세척, 소화, 음용에 쓸 수 있다 (오염수 음용은 중독 위험).

EN 전: It can store and carry water received from other containers and transfer it to other containers. Its water can be used for refilling water storage, watering crops, washing vehicle bloodstains, extinguishing fires, and drinking; drinking tainted water risks poisoning.

EN 후: It can hold water for storage or carrying. It can also transfer water to other containers. Its water can be used for refilling water storage, watering crops, washing vehicle bloodstains, extinguishing fires, and drinking; drinking tainted water risks poisoning.

Descriptions SHA256: `e18e90dc3091504284b0dcefcb779e810f28991fb0f1c76e14dd2ef58b01d560`

Blocks SHA256(불변): `9d68e982cd508b3a4beafc9d1a8892668c9470d4581f7db0d1761e602926e161`

기존 후보 run-1z4n2zmh와 앞선 승인 교정은 보존한다. 최종 검증·후보는 아래 완료 기록에 기재한다.


### 파스타·물 보관 문형 교정 최종 검증 및 후보

문구 고정 뒤 기존 최소3노드 묶음 한 번 실행: **3 passed in 169.15s (0:02:49)**, 종료 코드 **0**.

```powershell
$env:IRIS_SHARED_MENU_VALIDATION='1'
uv run --project .\Iris\tooling python -I -B -m pytest --noconftest -c .\Iris\tooling\pyproject.toml .\Iris\build\description\v2\tests\test_layer3_description_composition.py::test_layer3_description_composition .\Iris\tooling\tests\test_tooltip_t2_projection.py::test_s2_supply_and_owner_integration .\Iris\build\description\v2\tests\test_layer3_product_integration.py::test_product_contract --basetemp .\.tmp\common -q -s --tb=short
```

로그: `.tmp/prose/pasta-water-tests.log`. Blocks 불변으로 별도 block 검사를 추가하지 않았다. 새 Gate·전면 원천 재조사·추가 confidence 검사는 없다.

- product: `l3p-2a40ddc81a714c19299ae03fc2c5b7a7c083eaaaf55131cf61f2453dd5d1fb63`
- ZIP: `.tmp/menu/run-gannsp5q/p/Iris.zip`
- SHA256: `aa54b655bb0cb06eb9e1eab0b1f896e9ec0e3eee920c1388e63e7e0b4e32b684`
- direct mod root: `C:\Users\MW\Downloads\coding\PZ\.tmp\menu\run-gannsp5q\p\Iris`
- 상태: **implemented_only**. 실제 PZ 미관찰. 이전 run-1z4n2zmh 후보 보존. 라이브 설치·커밋·푸시 없음.


## 능력 중심 문형 및 도구 범위 조사 — 수정 전 (2026-09-13)

현재 655개 네문구 그룹과 2005개 고유 현지화 segment를 전부 읽고, 공통 문법·일반 및 특수 frame·compact 요약·expanded remaining·effect/state·qualifier·fallback 생성 경로를 대조했다. 읽기용 문형 색인은 수정 대상 후보의 좌표 전사이며 변경 수치나 통과 판정이 아니다.

기준: `e18e90dc3091504284b0dcefcb779e810f28991fb0f1c76e14dd2ef58b01d560`. 전체2105아이템/8420좌표.

- 문형: 1265아이템 / 4136좌표
- 문형만: 1245아이템 / 4056좌표
- 의미상세: 1아이템 / 2좌표
- 모호범위: 20아이템 / 80좌표
- 문형_의미상세: 1아이템 / 2좌표
- 문형_모호범위: 20아이템 / 80좌표
- 의미상세_모호범위: 1아이템 / 2좌표
- union: 1265아이템 / 4136좌표

문형만은 의미상세·모호범위를 제외한 좌표다. 축별 수는 중복을 포함한다. 문형 색인 수는 수정 전 후보 수이며 실제 변경 수는 재생성 후 별도로 기록한다.

- ko/en.role의 역할 명사형 및 passive 표현, results._compact_materials의 supplies/material 설명
- uses.frames의 도구 개요, 의복 위치, 의료/용기/필기구/점화/음식 등 독립 특수 문구
- families.FUNCTION_FRAMES/OVERVIEWS/frames/packaging_frames와 lexicon의 inherited direct function 및 qualifier fallback에 남은 역할형
- fabric_recovery의 FABRIC_ACTION을 tool/material에 공통 투영해 가위 자신의 필요 조건과 실 회수 결과가 재설명됨
- moving_furniture 활동명이 실제 PickUpTool/PlaceTool 검사와 결합되지 않아 이동/가구 작업으로 모호하게 요약됨
- 채택 r6 semantic: scripts/recipes.txt L3761–3819 Rip Clothing Denim/Leather, keep Scissors, Result DenimStrips/LeatherStrips; material 공통 결과/수량/실 qualifier는 내부에 유지
- 채택 ISMoveableDefinitions addToolDefinition + ISMoveableSpriteProps PickUpTool/PlaceTool, hasTool, canPickUp/canPlace 및 ISMoveablesAction. scrap은 별도 getScrapDefinition 분기라 moving_furniture에서 해체를 주장하지 않음
- 의복 material에는 데님/가죽 가위 조건과 실제 strips 결과를 유지한다. 가위 tool에만 관련 없는 조건/결과 상세를 제외한다.
- 가구 운반·모든 가구 지원·구체 가구 목록·해체는 추가하지 않는다. 별도 dismantle_built_object 기능은 기존 근거로 독립 보존한다.
- 장전15%의 탄종/착용 범위, 낚싯줄 파손의 실제 결과, 제작 마모, 엔진 상태>10→0, 시비4회 후 부패, 씨앗50개, 통조림 실제 결과명/섭취/요리 차이 등은 사실·조건을 가능성으로 약화하지 않는다.
- 타이어 중복처럼 보여도 설치/주행/공기·상태·손실 조건은 의미 구분이 있으므로 상세 삭제하지 않는다. 바늘 패치 회수 가능성과 의료 조건도 보존한다.
- 부서진 어망의 철사 회수량 미확정, 기존 음식 결과 보류2, 차량42 목적 미확정, absent124, unresolved 및 L4 공급 공백 유지.
- 이미 can/할 수 있다 중심인 통조림29와 Pasta/Rice 및 물49 등의 승인 교정은 의미를 유지한다. compact는 짧은 요약을 유지하되 명사 조각 종결을 능력 문장으로 바꾼다.

현재 단계는 조사 완료이며 producer·테스트·패키징 미실행. 실제 PZ 미관찰.


## 능력 중심 문형 공통 교정 — 구현 (2026-09-13)

상태: **implemented_only**.

수정 전 전체2105/8420 문구를 읽고 공통 생성 경로를 대조했다. 문형 색인1265/4136과 실제변경1302/4377을 분리한다. 최초 색인에 없던 보조도구/원격연결/일부 fallback 및 공통 문법의 파급은 실제 재생성 차이에 포함한다. 실제 대표13개의 KO/EN 네표면을 읽었고 재료 조사의 연결 오류와 가위 callback 목적 미적용, compact 길이를 발견해 교정했다. 키워드가 사라진 것만으로 전체 품질 PASS를 주장하지 않는다.

- 공통 role 문법, uses 특수 목적 및 compact 도구 개요, families 기능/학습/포장 fallback, results 재료 요약, lexicon 기능/qualifier를 능력 중심으로 작성했다. 출력 어미 일괄치환이나 FullType 문장 override는 없다.
- 가위 tool은 채택 FABRIC_ACTION+tool 역할로 데님/가죽 의류의 조각 회수 목적을 표현한다. callback 결과가 recipe_targets에 없는 경우도 이 닫힌 조건으로 처리한다. 실 회수와 가위 자기요건은 내부에 남고, 의복 material의 가위 조건 및 실제 strips 결과명은 유지한다.
- 가구20개: 개별선언 ID/Tag→parseItemTypes→공통 addToolDefinition; 같은 등록표를 PickUpTool/PlaceTool 양쪽 hasTool 검사에서 사용한다. 한쪽만 허용하는 도구 등록은 없다. 일부 가구의 집기/설치로 제한하며, 별도 scrap 및 운반 기능은 추론하지 않는다.
- compact의 재료·도구 묶음은 짧게 유지하고 expanded는 독립 목적을 나눈다. 창 부착물 회수/산탄총 총신 단축은 가공대상이라는 역할 설명을 해당 작업의 능력 문장으로 작성하고 기존 후속 조건·결과를 보존한다.
- 장전15%의 착용/탄종 범위, 장비 슬롯 제공, 낚싯줄 파손 결과, 창 제작 마모, 엔진>10→0, 씨앗50, 시비4회 후 부패, 항생제 좀비화불가 등은 확정값/조건/위험을 임의 가능성으로 약화하지 않는다.
- 통조림 실제 결과명·섭취와 요리 구분, Pasta/Rice 먹기·미끼·요리, 물49 보관/운반과 공급경로 구분, 낮은 음식결과 생략, 선택적 식기 내부화, 짧은 물기닦기, 가운데점 제거 등 앞선 승인 교정을 보존한다.

Descriptions SHA256: `1abe69a28130420aae4bd9da3f602202305fa950711c235db2139994bb6d263a`

Blocks SHA256(불변): `9d68e982cd508b3a4beafc9d1a8892668c9470d4581f7db0d1761e602926e161`

**Base.Scissors — 실제 생성 문구**

KO compact: 데님이나 가죽 의류의 조각 회수, 일부 가구 집기와 설치, 머리와 수염 손질에 사용할 수 있다. 제작한 창에 부착하거나 근접 공격에 사용할 수도 있다.

KO expanded: 데님이나 가죽 의류를 잘라 조각을 회수할 수 있다. / 일부 가구를 집어 들거나 설치하는 데 사용할 수 있다. / 머리를 손질할 수 있다. / 수염을 다듬거나 면도할 수 있다. / 제작한 창에 부착해 쓸 수 있다. / 근접 공격에 사용할 수 있다.

EN compact: It can be used for recovering strips from denim or leather clothing; picking up or placing certain furniture; hair and beard grooming. It can also be attached to a crafted spear or be used for melee attacks.

EN expanded: It can be used to cut denim or leather clothing into strips. / It can be used to pick up or place certain furniture. / It can be used to groom hair. / It can be used to trim or shave a beard. / It can be attached to a crafted spear. / It can be used for melee attacks.

**Base.Hammer — 실제 생성 문구**

KO compact: 금속을 단조하는 데 사용할 수 있다. 목공, 건축, 일부 가구 집기와 설치, 수박 쪼개기, 문과 창문의 판자 바리케이드 설치와 철거에 사용할 수 있다. 근접 공격에 사용할 수도 있다.

KO expanded: 금속을 단조하는 데 사용할 수 있다. / 목공 작업에 사용할 수 있다. / 건축 작업에 사용할 수 있다. / 일부 가구를 집어 들거나 설치하는 데 사용할 수 있다. / 문과 창문의 판자 바리케이드를 설치하거나 철거할 수 있다. / 수박 쪼개기에 사용할 수 있다. / 근접 공격에 사용할 수 있다.

EN compact: It can be used for metal forging. It can be used for woodworking and construction; picking up or placing certain furniture; breaking a watermelon; installing or removing plank barricades on doors and windows. It can also be used for melee attacks.

EN expanded: It can be used for metal forging. / It can be used for woodworking. / It can be used for construction. / It can be used to pick up or place certain furniture. / It can be used to install or remove plank barricades on doors and windows. / It can be used for breaking a watermelon. / It can be used for melee attacks.

**Base.DenimStrips — 실제 생성 문구**

KO compact: 응급처치와 의류 수선에 쓰거나 제작 재료로 사용할 수 있다.

KO expanded: 세척이 필요한 화상을 씻는 붕대 재료로 사용할 수 있다. / 상처에 붕대를 대는 재료로 사용할 수 있다. 재료가 감염되어 있으면 상처를 감염시킬 수 있다. / 부목 제작에 재료로 사용할 수 있다. / 의류의 구멍을 덧대거나 패딩을 추가할 수 있다. / 화염 장치 제작에 재료로 사용할 수 있다. / 석제 도구 제작에 재료로 사용할 수 있다.

EN compact: It can be used as material for first aid, clothing repairs, and crafting.

EN expanded: It can be used as bandaging material for cleaning burns that need washing. / It can be used as material for bandaging wounds. Infected material can infect the wound. / It can be used as a material for splint crafting. / It can be used to patch garment holes or add padding. / It can be used as a material for making incendiary devices. / It can be used as a material for stone-tool crafting.

**Base.Pills — 실제 생성 문구**

KO compact: 통증 완화를 위해 복용할 수 있다.

KO expanded: 통증 완화를 위해 복용할 수 있다.

EN compact: It can be taken for pain relief.

EN expanded: It can be taken for pain relief.

**Base.Socks_Ankle — 실제 생성 문구**

KO compact: 착용하거나 찢어서 천 조각을 얻을 수 있다. 양말을 시트 로프 제작 재료나 연료, 불쏘시개로도 쓸 수 있다.

KO expanded: 양말 자리에 착용할 수 있다. / 찢어서 찢어진 천 또는 찢어진 천 (오염됨)을 얻을 수 있다. / 양말을 시트 로프 제작 재료로 쓸 수 있다. / 모닥불, 비프로판 바비큐, 벽난로의 연료로 소모할 수 있다. / 모닥불, 비프로판 바비큐, 벽난로, 통나무가 든 드럼의 불쏘시개로 소모할 수 있다.

EN compact: It can be worn or ripped to obtain cloth scraps, used directly to make sheet rope, or used as fuel and tinder.

EN expanded: It can be worn in the socks equipment slot. / It can be ripped to obtain Ripped Sheets or Dirty Rag. / The Socks can be used as material for making sheet rope. / It can be consumed as fuel for campfires and non-propane barbecues and fireplaces. / It can be consumed as tinder for campfires, non-propane barbecues and fireplaces, and drums containing logs.

**Base.BookCarpentry1 — 실제 생성 문구**

KO compact: 책의 기술 범위에 맞는 독자의 목공 경험치 배율을 높일 수 있다. 완독 시 최대 3배다. 연료나 불쏘시개로 쓸 수 있다.

KO expanded: 책의 기술 범위에 맞는 독자의 목공 경험치 배율을 높일 수 있다. 완독 시 최대 3배다. / 모닥불, 비프로판 바비큐, 벽난로의 연료로 소모할 수 있다. / 모닥불, 비프로판 바비큐, 벽난로, 통나무가 든 드럼의 불쏘시개로 소모할 수 있다.

EN compact: It can raise carpentry XP multipliers within its supported skill range. Full reading reaches up to 3×. It can be used as fuel or tinder.

EN expanded: It can raise the carpentry XP multiplier for readers within its supported skill range. Full reading reaches up to 3×. / It can be consumed as fuel for campfires and non-propane barbecues and fireplaces. / It can be consumed as tinder for campfires, non-propane barbecues and fireplaces, and drums containing logs.

**Base.SpearScissors — 실제 생성 문구**

KO compact: 물가에서 미끼 없이 창낚시에 쓸 수 있다. 창의 부착물을 회수할 수 있다. 창 (가위)는 근접 공격에 쓸 수 있다.

KO expanded: 물가에서 미끼 없이 창낚시에 쓸 수 있다. / 창의 부착물을 회수할 수 있다. 이때 파괴된 창에서도 부착물과 제작한 창을 회수할 수 있다. / 창 (가위)는 근접 공격에 사용할 수 있다.

EN compact: Spear With Scissors can be used for spear fishing at water without bait. Its spear attachment can be recovered. Spear With Scissors can be used for melee attacks.

EN expanded: Spear With Scissors can be used for spear fishing at water without bait. / Its spear attachment can be recovered. The attachment and a crafted spear can be recovered even from a destroyed spear. / Spear With Scissors can be used for melee attacks.

**Base.CannedCorn — 실제 생성 문구**

KO compact: 통조림 따개로 개봉해 옥수수를 먹을 수 있다. 꺼낸 옥수수를 요리 재료로도 쓸 수 있다.

KO expanded: 통조림 따개로 개봉해 옥수수를 먹을 수 있다. / 꺼낸 옥수수를 요리 재료로도 쓸 수 있다.

EN compact: It can be opened with a Can Opener to eat the Corn. The extracted Corn can also be used as a cooking ingredient.

EN expanded: It can be opened with a Can Opener to eat the Corn. / The extracted Corn can also be used as a cooking ingredient.

**Base.Pasta — 실제 생성 문구**

KO compact: 먹거나 요리 재료로 쓸 수 있다. 덫의 미끼로도 쓸 수 있다.

KO expanded: 먹을 수 있다. / 덫의 미끼로 쓸 수 있다. / 요리 재료로 쓸 수 있다.

EN compact: It can be eaten or used as a cooking ingredient. It can also be used as trap bait.

EN expanded: It can be eaten. / It can be used as trap bait. / It can be used as a cooking ingredient.

이전 run-gannsp5q와 모든 이전 후보·교정 기록을 보존한다. 마지막 최소 검사·후보는 아래 완료 기록에 기재한다. 실제 PZ 미관찰.


검사 전 영향 문면 확인: 전체 4377 변경 좌표의 before/after 고유수정조각296개 및 주변문구를 읽고, 최초색인밖100아이템/241좌표의 전체문구를 읽었다. 신규37아이템+기존63아이템의 추가표면. Bowl의 divide 의미 약화를 발견해 검사 전 복원했다. 마지막 원문은 위 최종 SHA에 해당하며 대표13만으로 전수 품질 수락을 주장하지 않는다.


### 능력 중심 문형 공통 교정 최종 검증 및 후보

문구 고정 뒤 기존 최소3노드 묶음 한 번 실행: **3 passed in 139.11s (0:02:19)**, 종료 코드 **0**.

```powershell
$env:IRIS_SHARED_MENU_VALIDATION='1'
uv run --project .\Iris\tooling python -I -B -m pytest --noconftest -c .\Iris\tooling\pyproject.toml .\Iris\build\description\v2\tests\test_layer3_description_composition.py::test_layer3_description_composition .\Iris\tooling\tests\test_tooltip_t2_projection.py::test_s2_supply_and_owner_integration .\Iris\build\description\v2\tests\test_layer3_product_integration.py::test_product_contract --basetemp .\.tmp\common -q -s --tb=short
```

로그: `.tmp/prose/capability-tests.log`. Blocks 불변으로 별도 block 검사를 추가하지 않았다. 새 Gate·전면 원천 재조사·추가 confidence 검사는 없다.

- product: `l3p-066eb82436c04a645a94850605501323831b69e779db260ec09e2c376d315485`
- ZIP: `.tmp/menu/run-yp219v2y/p/Iris.zip`
- SHA256: `70fe2da4beb47f981d9c18c202fcb2517c8c777371a41c1c553580258702be96`
- direct mod root: `C:\Users\MW\Downloads\coding\PZ\.tmp\menu\run-yp219v2y\p\Iris`
- 상태: **implemented_only**. 실제 PZ 미관찰. 이전 run-gannsp5q 후보 보존. 라이브 설치·커밋·푸시 없음.


## 무기 용도 문형 공통 교정 — 구현 (2026-09-13)

상태: **implemented_only**.

수정 전 melee_attack 공개 참조로114아이템/456좌표를 확인했다. 실제 변경도 정확히114/456이며 전체 변경의17고유차이와 주변문구를 읽었다. 일반형, 도구 복합형, 창부착형, 재료 복합형 및 실제 이름 주어형을 확인했다.

- admitted melee_attack의 공개 용도를 무기로 쓸 수 있다 / It can be used as a weapon으로 표현한다. 일반 expanded/compact, 도구와 창부착의 복합compact, 재료와 골절고정의 복합compact에 공통 적용했다.
- 새로운 무기 역할이나 총기 기능을 추가하지 않았다. 114아이템의 원본 fact, qualifier, 독립 용도와 부착 관계를 보존했다. 복합 문장의 조사만 해당 의미 경로에서 작성하며 완성 문구 전역 치환은 없다.
- 기준1abe69와 이전 run-yp219v2y 후보 및 기존 교정 기록은 보존한다. 가운데점 제거, 가위/가구 범위와 수치·상태·실제 결과명·섭취/조리 구분도 유지한다.

Descriptions SHA256: `cc25b4596aa5d3d3ec0fd43a00da80ba9390ed3c31285a117465a6c7edad982c`

Blocks SHA256(불변): `9d68e982cd508b3a4beafc9d1a8892668c9470d4581f7db0d1761e602926e161`

**Base.BadmintonRacket — 실제 생성 문구**

KO compact: 무기로 쓸 수 있다.

KO expanded: 무기로 쓸 수 있다.

EN compact: It can be used as a weapon.

EN expanded: It can be used as a weapon.

**Base.Scissors — 실제 생성 문구**

KO compact: 데님이나 가죽 의류의 조각 회수, 일부 가구 집기와 설치, 머리와 수염 손질에 사용할 수 있다. 제작한 창에 부착하거나 무기로 쓸 수도 있다.

KO expanded: 데님이나 가죽 의류를 잘라 조각을 회수할 수 있다. / 일부 가구를 집어 들거나 설치하는 데 사용할 수 있다. / 머리를 손질할 수 있다. / 수염을 다듬거나 면도할 수 있다. / 제작한 창에 부착해 쓸 수 있다. / 무기로 쓸 수 있다.

EN compact: It can be used for recovering strips from denim or leather clothing; picking up or placing certain furniture; hair and beard grooming. It can also be attached to a crafted spear or be used as a weapon.

EN expanded: It can be used to cut denim or leather clothing into strips. / It can be used to pick up or place certain furniture. / It can be used to groom hair. / It can be used to trim or shave a beard. / It can be attached to a crafted spear. / It can be used as a weapon.

**Base.Hammer — 실제 생성 문구**

KO compact: 금속을 단조하는 데 사용할 수 있다. 목공, 건축, 일부 가구 집기와 설치, 수박 쪼개기, 문과 창문의 판자 바리케이드 설치와 철거에 사용할 수 있다. 무기로도 쓸 수 있다.

KO expanded: 금속을 단조하는 데 사용할 수 있다. / 목공 작업에 사용할 수 있다. / 건축 작업에 사용할 수 있다. / 일부 가구를 집어 들거나 설치하는 데 사용할 수 있다. / 문과 창문의 판자 바리케이드를 설치하거나 철거할 수 있다. / 수박 쪼개기에 사용할 수 있다. / 무기로 쓸 수 있다.

EN compact: It can be used for metal forging. It can be used for woodworking and construction; picking up or placing certain furniture; breaking a watermelon; installing or removing plank barricades on doors and windows. It can also be used as a weapon.

EN expanded: It can be used for metal forging. / It can be used for woodworking. / It can be used for construction. / It can be used to pick up or place certain furniture. / It can be used to install or remove plank barricades on doors and windows. / It can be used for breaking a watermelon. / It can be used as a weapon.

**Base.Plank — 실제 생성 문구**

KO compact: 목공과 건축이나 다른 물품을 만드는 재료로 사용할 수 있다. 골절 고정에 쓸 수 있다. 무기로도 쓸 수 있다. 연료로도 쓸 수 있다.

KO expanded: 목공 작업에 재료로 사용할 수 있다. / 건축 작업에 재료로 사용할 수 있다. / 모닥불 키트 제작에 재료로 사용할 수 있다. / 가구 부품 제작에 재료로 사용할 수 있다. / 톱 제작 재료로 사용할 수 있다. / 창 제작에 재료로 사용할 수 있다. / 머리와 몸통을 제외한 부위의 골절에 부목을 대는 데 쓸 수 있다. / 부목 제작에 재료로 사용할 수 있다. / 덫 제작에 재료로 사용할 수 있다. / 수박 쪼개기에 사용할 수 있다. / 무기로 쓸 수 있다. / 모닥불, 비프로판 바비큐, 벽난로의 연료로 소모할 수 있다.

EN compact: It can be used as material for woodworking, construction, and crafting. It can also be used for splinting fractures. It can also be used as a weapon. It can also be used as fuel.

EN expanded: It can be used as a material for woodworking. / It can be used as a material for construction. / It can be used as a material for campfire-kit crafting. / It can be used as a material for furniture-part crafting. / It can be used as material for making Saw. / It can be used as a material for spear crafting. / It can help splint fractures outside the head and torso. / It can be used as a material for splint crafting. / It can be used as a material for trap crafting. / It can be used for breaking a watermelon. / It can be used as a weapon. / It can be consumed as fuel for campfires and non-propane barbecues and fireplaces.

**Base.SpearScissors — 실제 생성 문구**

KO compact: 물가에서 미끼 없이 창낚시에 쓸 수 있다. 창의 부착물을 회수할 수 있다. 창 (가위)는 무기로 쓸 수 있다.

KO expanded: 물가에서 미끼 없이 창낚시에 쓸 수 있다. / 창의 부착물을 회수할 수 있다. 이때 파괴된 창에서도 부착물과 제작한 창을 회수할 수 있다. / 창 (가위)는 무기로 쓸 수 있다.

EN compact: Spear With Scissors can be used for spear fishing at water without bait. Its spear attachment can be recovered. Spear With Scissors can be used as a weapon.

EN expanded: Spear With Scissors can be used for spear fishing at water without bait. / Its spear attachment can be recovered. The attachment and a crafted spear can be recovered even from a destroyed spear. / Spear With Scissors can be used as a weapon.

이전 run-yp219v2y와 모든 이전 후보·교정 기록을 보존한다. 마지막 최소 검사·후보는 아래 완료 기록에 기재한다. 실제 PZ 미관찰.


### 무기 용도 문형 공통 교정 최종 검증 및 후보

문구 고정 뒤 기존 최소3노드 묶음 한 번 실행: **3 passed in 143.71s (0:02:23)**, 종료 코드 **0**.

```powershell
$env:IRIS_SHARED_MENU_VALIDATION='1'
uv run --project .\Iris\tooling python -I -B -m pytest --noconftest -c .\Iris\tooling\pyproject.toml .\Iris\build\description\v2\tests\test_layer3_description_composition.py::test_layer3_description_composition .\Iris\tooling\tests\test_tooltip_t2_projection.py::test_s2_supply_and_owner_integration .\Iris\build\description\v2\tests\test_layer3_product_integration.py::test_product_contract --basetemp .\.tmp\common -q -s --tb=short
```

로그: `.tmp/prose/weapon-tests.log`. Blocks 불변으로 별도 block 검사를 추가하지 않았다. 새 Gate·전면 원천 재조사·추가 confidence 검사는 없다.

- product: `l3p-db1faa84039f1840c907f006be53e2ff9322befa8f6da4ca68f389597a6a8755`
- ZIP: `.tmp/menu/run-6bt0yuh8/p/Iris.zip`
- SHA256: `21bed8da7bda2b0c0cfd5e92b3e6719735f7ba283fedd90b47c98d0ea9719b4a`
- direct mod root: `C:\Users\MW\Downloads\coding\PZ\.tmp\menu\run-6bt0yuh8\p\Iris`
- 상태: **implemented_only**. 실제 PZ 미관찰. 이전 run-yp219v2y 후보 보존. 라이브 설치·커밋·푸시 없음.


## 2026-09-13 기존 공통 규칙 적용 누락 교정

상태: **implemented_only**. 최종 자동 검사는 아래에 별도 기록한다.

기준 cc25b459의 전체 2,105개 활동·기능·역할을 순회해 같은 합성 경로를 조사했다. 변경 전후의 KO/EN 고유 segment 715그룹과 후속 delta 140그룹을 읽고, 주요 복합 아이템의 네 전체 문면을 대조했다. 동일 문장에 들어가는 기존 원물 이름은 변수로 묶어 읽었다. 이는 기존 입력에 대한 공통 의미/문면 교정이며 원천 사실 전수 재감사, EN 독립 품질 수락 또는 인게임 수락이 아니다.

실제 문면 변경: **735아이템 / 2466좌표**. 변경 분모는 2,105아이템 / 8,420좌표다.

- 사용자 확정 지시를 기존 공통 uses/families/lexicon/results 경로에 적용했다. FullType 완성 문장 override나 생성 JSON 수동 패치, 런타임 의미 재작성기는 없다.
- 라디오12종과 TV3종은 주파수/채널 선택 대신 방송 청취/시청을 설명한다. 전원과 내용에 따른 효과 조건은 보존한다.
- 붕대 준비11종의 역할을 대조했다. 붕대 자체의 소독, 솜의 소독솜 제작, 소독 공급물과 물 용기, 이미 있는 세척 경로를 구별한다. 물 용기에 솜 소독이나 끓는 온도 보장을 발명하지 않는다. 생선7종은 손질 대상과 무게>0.6 조건을 보존하고 작은 동물5종은 고기 획득으로 표현한다. 수박 대상과 도구9종을 구별하며, Plank compact에 빠졌던 수박 쪼개기도 복원한다.
- 전자 제작의 여러 결과/버전은 전자 부품 등 확인된 목적군으로 묶는다. 단일 결과가 용도를 식별하는 경우와 원격제어 조정기만 만드는 경우의 이름은 보존한다. 달걀은 달걀곽 포장 용도를 직접 표현한다.
- 목공/건축의 같은 재료 역할과 분리 context를 함께 묶고, compact의 제작 및 호환 물품 수리 범위를 공유한다. 포장, 로프 고정, 손질 대상, 연료, 무기 등 독립 활용은 따로 남긴다. Shovel 계열은 밭 작업과 무덤 파기/메우기, 재 청소, 담기로 묶고 수확 제외를 보존한다.
- 조리 용기의 쌀/파스타/반죽 준비를 조리 활용 안에서 묶고, 반죽에 넣는 재료와 만드는 도구/용기 역할은 구별한다. 물 보관/운반 문장은 그대로 두며 다른 용기/저장 시설로 옮기는 공급 경로만 함께 표현한다.
- 낚싯대 파손 후 제작품/완제품별 남는 물품 산정은 삭제했다. 파손과 미끼 손실은 보존한다. 창 마모 인과관계, 통나무 반환, 신선도/보존, 타이어 등 기존 보류를 일괄 삭제하거나 새 관계로 확정하지 않았다.
- 의복의 슬롯식 표현과 착용 형태 변경, 기술서의 경험치 배율 문형, 지면 재료 깔기, 약초 찜질제의 도구/재료 문형을 고쳤다. 천/의복의 시트 로프 제작은 찢기 전 원물을 주어로 명시한다.
- 차량 좌석/연료탱크12종은 설치 대상이라는 공통 역할만 호환 차량에 장착할 수 있다로 표현한다. 구체 차량 기능42종의 미확정 범위를 해소했다고 주장하지 않는다.
- 통조림 실제 내용물과 개봉 도구/음용/식용/조리 구분, Pasta/Rice 식용/요리/미끼, 물 보관/운반, 가위 데님/가죽 및 가구 집기/설치, 무기 문형과 S3 획득/Acquisition 변경을 보존한다.
- 각 locale/surface present1981, absent124 유지. absent는 품질 수락 수가 아니다.
- 차량42 구체 목적, 기존 unresolved/보류 및 exact ID L4 공급 공백 유지.
- 실제 PZ의 KO/EN 글꼴, Tooltip 네 물리줄과 S1/S3/S4, Browser/Wiki 스크롤/메뉴 표시는 미관찰.
- 저장소 밖 설치, live/current 전환, commit/push, 전체 Run A/B, 새 validation authority는 수행하지 않는다.

Descriptions SHA256: `8ea9a317292ae25ce5ee0221c0fb5b8074707705950b492ee9b7694b34b0c1e1`

Blocks SHA256(불변): `9d68e982cd508b3a4beafc9d1a8892668c9470d4581f7db0d1761e602926e161`

**Radio.RadioBlack**

Before KO compact: 밸류테크 라디오는 전원이 공급되면 방송 주파수 선택에 쓸 수 있다. 내용에 따라 능력치, 경험치, 제작법 학습 효과를 얻을 수 있다. 드라이버로 분해해 전자 부품을 회수하는 데 쓸 수 있다.

After KO compact: 밸류테크 라디오는 전원이 공급되면 라디오 방송을 청취할 수 있다. 내용에 따라 능력치, 경험치, 제작법 학습 효과를 얻을 수 있다. 드라이버로 분해해 전자 부품을 회수하는 데 쓸 수 있다.

After EN compact: With power, ValuTech Radio can be used for listening to radio broadcasts. Depending on the content, it can affect stats, XP or recipe knowledge. It can be dismantled with a screwdriver to recover electronic parts.

**Base.Bandage**

Before KO compact: 화상 세척 재료로 쓸 수 있다. 상처에 붕대를 대는 재료로 사용할 수 있다. 재료가 감염되어 있으면 상처를 감염시킬 수 있다. 붕대 재료 소독에 재료로 사용할 수 있다.

After KO compact: 화상 세척에 쓸 수 있다. 상처에 붕대를 대는 재료로 사용할 수 있다. 재료가 감염되어 있으면 상처를 감염시킬 수 있다. 소독해 상처에 댈 수 있다.

After EN compact: It can be used for cleaning burns. It can be used as material for bandaging wounds. Infected material can infect the wound. It can be disinfected for bandaging wounds.

**Base.Splint**

Before KO compact: 부목 재료로 쓸 수 있다.

After KO compact: 골절 고정에 쓸 수 있다.

After EN compact: It can be used for splinting fractures.

**Base.Screwdriver**

Before KO compact: 간이 무전기 제작, 전자기기 분해 및 조명 개조, 목공 및 건축물 분해, 원격제어 조정기, 폭탄 타이머 (수제작), 원격 폭탄 격발기 (수제작) 제작, 일부 가구 집기와 설치, 차량, 무기 부품 장착, 제거에 사용할 수 있다. 제작한 창에 부착하거나 무기로 쓸 수도 있다.

After KO compact: 전자기기 제작과 분해 및 조명 개조, 목공 및 건축물 분해, 일부 가구 집기와 설치, 차량, 무기 부품 장착, 제거에 사용할 수 있다. 제작한 창에 부착하거나 무기로 쓸 수도 있다.

After EN compact: It can be used for making and dismantling electronic devices, plus lamp conversion to battery power; woodworking, plus structure disassembly; picking up or placing certain furniture; fitting and removing vehicle and weapon parts. It can also be attached to a crafted spear or be used as a weapon.

**Base.Nails**

Before KO compact: 호환되는 손상 물품의 수리 재료로 사용할 수 있다. 모아서 상자로 포장할 수 있다. 위층 창문 등에 탈출용 로프를 고정할 수 있다. 목공에 재료로 사용할 수 있다. 건축 작업에 재료로 사용할 수 있다. 문과 창문에 판자 바리케이드를 설치할 수 있다. 낚시 장비 제작, 가구 부품 제작, 덫 제작에 재료로 사용할 수 있다.

After KO compact: 목공, 건축, 물품 제작, 호환 물품 수리의 재료로 쓸 수 있다. 모아서 상자로 포장할 수 있다. 위층 창문 등에 탈출용 로프를 고정할 수 있다.

After EN compact: It can be used as material for woodworking, construction, crafting, and repairing compatible items. It can be collected and packed into a box. It can be used to anchor an escape rope at an upper-floor window or similar attachment.

**Base.WaterPot**

Before KO compact: 물을 담아 보관하거나 운반할 수 있다. 다른 용기로 물을 옮길 수도 있다. 담긴 물은 저장 시설 급수, 작물 급수, 차량 혈흔 세척, 소화, 음용에 쓸 수 있다. 재료를 더해 요리를 만들 수도 있다 (오염수 음용은 중독 위험). 붕대 재료 소독에 재료로 사용할 수 있다. 쌀, 파스타 준비에 용기로 사용할 수 있다.

After KO compact: 붕대 소독에 쓸 수 있다. 재료를 담아 요리할 수 있다. 물을 담아 보관하거나 운반할 수 있다. 다른 용기나 저장 시설로 물을 옮길 수 있다. 담긴 물은 작물 급수, 차량 혈흔 세척, 소화, 음용에 쓸 수 있다 (오염수 음용은 중독 위험).

After EN compact: It can be used to disinfect bandaging. It can hold ingredients for cooking. It can hold water for storage or carrying. It can transfer water to other containers or storage fixtures. Its water can be used for watering crops, washing vehicle bloodstains, extinguishing fires, and drinking; drinking tainted water risks poisoning.

**Base.Sheet**

Before KO compact: 찢어서 찢어진 천 또는 찢어진 천 (오염됨)을 얻을 수 있다. 천을 시트 로프 제작 재료로 쓸 수 있다. 커튼이 없는 대응 창문이나 문에 커튼으로 설치할 수 있다. 설치 후 열고 닫거나 떼어낼 수 있다. 모닥불 키트 제작, 매트리스 제작에 재료로 사용할 수 있다. 연료나 불쏘시개로 쓸 수 있다.

After KO compact: 찢어서 찢어진 천 또는 찢어진 천 (오염됨)을 얻을 수 있다. 찢기 전 천을 시트 로프 제작 재료로 쓸 수 있다. 커튼이 없는 대응 창문이나 문에 커튼으로 설치할 수 있다. 설치 후 열고 닫거나 떼어낼 수 있다. 모닥불 키트 제작, 매트리스 제작에 재료로 사용할 수 있다. 연료나 불쏘시개로 쓸 수 있다.

After EN compact: It can be ripped to obtain Ripped Sheets or Dirty Rag. The intact Sheet can be used as material for making sheet rope. It can be installed as a curtain on an eligible window or door without one; the installed curtain can be opened, closed or removed. It can be used as a material for campfire-kit crafting and mattress crafting. It can be used as fuel or tinder.

**Base.Bass**

Before KO compact: 먹을 수 있다. 덫의 미끼로도 쓸 수 있다. 생선 손질에 재료로 사용할 수 있다.

After KO compact: 먹을 수 있다. 덫의 미끼로도 쓸 수 있다. 생선을 손질해 살을 얻을 수 있다.

After EN compact: It can be eaten. It can also be used as trap bait. It can be filleted.

**Base.CraftedFishingRod**

Before KO compact: 물가에서 맞는 미끼와 함께 낚시할 수 있다. 낚싯줄이 끊어지면 낚싯대가 부러지거나 막대로 바뀌며 미끼를 잃는다. 무기로 쓸 수 있다.

After KO compact: 물가에서 맞는 미끼와 함께 낚시할 수 있다. 낚싯줄이 끊어지면 낚싯대가 부러지거나 막대로 바뀌며 미끼를 잃는다. 무기로 쓸 수 있다.

After EN compact: It can be used for rod fishing at water with matching bait. A broken line changes the rod into a broken rod or stick and loses the bait. It can be used as a weapon.

전체 Before/After는 기존 `iris_dvf_description_review.html`, 전체 최신 문장은 `iris_dvf_descriptions.html`에 갱신했다. 이전 `.tmp/menu/run-bcwd4x0i/p/Iris.zip`은 보존하며 최신 후보라고 재사용하지 않는다.


### 공통 규칙 교정 최종 검사와 새 후보

기존 최소 3노드 묶음: **3 passed in 131.14s (0:02:11)**, 정확한 명령 종료 코드 **0**.

```powershell
$env:IRIS_SHARED_MENU_VALIDATION='1'
uv run --project .\Iris\tooling python -I -B -m pytest --noconftest -c .\Iris\tooling\pyproject.toml .\Iris\build\description\v2\tests\test_layer3_description_composition.py::test_layer3_description_composition .\Iris\tooling\tests\test_tooltip_t2_projection.py::test_s2_supply_and_owner_integration .\Iris\build\description\v2\tests\test_layer3_product_integration.py::test_product_contract --basetemp .\.tmp\common -q -s --tb=short
```

로그: `.tmp/prose/common-tests.log`. Blocks/상류 생산자는 바꾸지 않아 별도 block 검사를 추가하지 않았다. Lua syntax와 런타임/메뉴/package 검사는 공통 product node의 같은 stage/ZIP 결과를 공유했다. 새 Gate, 전체 Run A/B, 추가 confidence 실행은 없다.

- 새 ZIP: `.tmp/menu/run-f2wnvz9w/p/Iris.zip`
- SHA256: `c9f8a5615caebf392d66c99fc6c9e98ca5e844820e7fbfa9a1953d40b40be011`
- product: `l3p-a420c7486a7a6dcba1e2ada08e8c09d7b5a25eb65b85046f3b600c0f488171f6`

최신 compact(S2)와 expanded(Menu)의 source 결속을 기존 제품 경로에서 검증했다. S3 획득/Acquisition 문형을 보존한 실제 ZIP의 static row를 읽었으며 Base.CannedMilk에는 S3가 없다. 이전 run-bcwd4x0i 후보는 보존한다. **implemented_only**, 실제 게임 미관찰. 설치/commit/push 없음.


## 2026-09-13 후속 문형 및 입력 역할 경계 교정

상태: **implemented_only**. 최종 자동 검사는 아래에 별도 기록한다.

직전 8ea9a317 결과를 기준으로 후속 교정의 KO/EN 고유 변경 segment 94그룹을 모두 읽었다. 역할별 내부/공개 경계를 대조했으며 자동 검사와 문면 검토, 실제 게임 수락을 구별한다.

실제 문면 변경: **84아이템 / 234좌표**. 변경 분모는 2,105아이템 / 8,420좌표다.

- Socks/Shoes는 발에 신기, 장갑은 손에 끼기, 목걸이/스카프/벨트/안경은 같은 공통 착용 경로의 신체 부위와 동사로 표현한다.
- 붕대는 상처에 감는 활용 안에 소독 대안을 합쳤다. 감염된 붕대의 상처 감염 조건은 보존하고 화상 세척은 독립 활용으로 유지한다.
- Sheet compact는 천 조각 회수와 찢기 전 원물의 시트 로프 제작을 대안으로 연결한다. expanded의 정확한 회수 결과는 보존한다. 같은 재료의 제작 활용을 compact에서 묶으며 설치한 커튼의 후속 조작은 내부에 둔다.
- 차량과 무기 부품의 장착과 제거는 명시적 접속사로 구별한다.
- 음식 분할/수박 쪼개기의 ingredient/material 입력 역할은 원물의 단순 가공 상세로 내부에 둔다. 이번 추가 대상은 Base.Watermelon과 Base.Muffintray_Biscuit이며 기존 미끼 용도를 유지한다. 식용/조리 용도를 추가하지 않는다.
- 실제 가공 도구 역할, 천 회수, 통조림 내용물 개봉 활용은 보존한다. Plank는 확인된 수박 쪼개기 도구 활용 그대로 두며 일반 음식 손질로 확대하지 않는다.
- 기존 공통 producer만 변경했다. FullType 완성 문장 override, 생성 JSON 수동 패치 또는 새 검증 권한을 도입하지 않았다.
- 각 locale/surface present1981, absent124 유지.
- 차량42 구체 목적, 기존 unresolved/보류 및 exact ID L4 공급 공백 유지.
- EN 독립 품질 수락 및 실제 PZ 글꼴/물리줄/메뉴 관찰은 수행하지 않았다.
- 기존 수정과 검사/후보 기록을 보존한다. 외부 설치, commit/push, 전체 Run A/B 또는 추가 confidence 실행 없음.

Descriptions SHA256: `1014c47c8596aa483ded11ca67440ad8c195fb04e00cf413c07c8fafa9fba36a`

Blocks SHA256(불변): `9d68e982cd508b3a4beafc9d1a8892668c9470d4581f7db0d1761e602926e161`

**Base.Socks_Ankle**

Before KO compact: 착용하거나 찢어서 천 조각을 얻을 수 있다. 양말을 시트 로프 제작 재료나 연료, 불쏘시개로도 쓸 수 있다.

After KO compact: 착용하거나 찢어서 천 조각을 얻을 수 있다. 양말을 시트 로프 제작 재료나 연료, 불쏘시개로도 쓸 수 있다.

After EN compact: It can be worn or ripped to obtain cloth scraps, used directly to make sheet rope, or used as fuel and tinder.

**Base.Bandage**

Before KO compact: 화상 세척에 쓸 수 있다. 상처에 붕대를 대는 재료로 사용할 수 있다. 재료가 감염되어 있으면 상처를 감염시킬 수 있다. 소독해 상처에 댈 수 있다.

After KO compact: 화상 세척에 쓸 수 있다. 상처에 감을 수 있다. 소독해서 쓸 수도 있다. 감염된 붕대를 쓰면 상처를 감염시킬 수 있다.

After EN compact: It can be used for cleaning burns. It can be wrapped around wounds. It can also be disinfected before use. An infected bandage can infect the wound.

**Base.Screwdriver**

Before KO compact: 전자기기 제작과 분해 및 조명 개조, 목공 및 건축물 분해, 일부 가구 집기와 설치, 차량, 무기 부품 장착, 제거에 사용할 수 있다. 제작한 창에 부착하거나 무기로 쓸 수도 있다.

After KO compact: 전자기기 제작과 분해 및 조명 개조, 목공 및 건축물 분해, 일부 가구 집기와 설치, 차량과 무기의 부품 장착과 제거에 사용할 수 있다. 제작한 창에 부착하거나 무기로 쓸 수도 있다.

After EN compact: It can be used for making and dismantling electronic devices, plus lamp conversion to battery power; woodworking, plus structure disassembly; picking up or placing certain furniture; fitting and removing parts on vehicles and weapons. It can also be attached to a crafted spear or be used as a weapon.

**Base.Sheet**

Before KO compact: 찢어서 찢어진 천 또는 찢어진 천 (오염됨)을 얻을 수 있다. 찢기 전 천을 시트 로프 제작 재료로 쓸 수 있다. 커튼이 없는 대응 창문이나 문에 커튼으로 설치할 수 있다. 설치 후 열고 닫거나 떼어낼 수 있다. 모닥불 키트 제작, 매트리스 제작에 재료로 사용할 수 있다. 연료나 불쏘시개로 쓸 수 있다.

After KO compact: 물품 제작의 재료로 쓸 수 있다. 찢어서 천 조각을 얻거나, 찢기 전 천을 시트 로프 재료로 쓸 수 있다. 커튼이 없는 대응 창문이나 문에 커튼으로 설치할 수 있다. 연료나 불쏘시개로 쓸 수 있다.

After EN compact: It can be used as material for crafting. It can be ripped for cloth scraps or used intact to make sheet rope. It can be installed as a curtain on an eligible window or door without one. It can be used as fuel or tinder.

**Base.Watermelon**

Before KO compact: 수박은 깨뜨려 박살난 수박을 얻을 수 있다. 나누어 수박 조각을 얻을 수 있다. 수박은 덫의 미끼로 쓸 수 있다.

After KO compact: 덫의 미끼로 쓸 수 있다.

After EN compact: It can be used as trap bait.

**Base.Muffintray_Biscuit**

Before KO compact: 나누어 비스킷을 얻을 수 있다. 익었거나 탄 트레이에서 꺼낸다. 나누기 전 음식은 덫의 미끼로 쓸 수 있다.

After KO compact: 덫의 미끼로 쓸 수 있다.

After EN compact: It can be used as trap bait.

**Base.Plank**

Before KO compact: 목공과 건축이나 다른 물품을 만드는 재료로 사용할 수 있다. 골절 고정이나 수박 쪼개기에 쓸 수 있다. 무기로도 쓸 수 있다. 연료로도 쓸 수 있다.

After KO compact: 목공과 건축이나 다른 물품을 만드는 재료로 사용할 수 있다. 골절 고정이나 수박 쪼개기에 쓸 수 있다. 무기로도 쓸 수 있다. 연료로도 쓸 수 있다.

After EN compact: It can be used as material for woodworking, construction, and crafting. It can also be used for splinting fractures and breaking a watermelon. It can also be used as a weapon. It can also be used as fuel.

전체 Before/After는 기존 `iris_dvf_description_review.html`, 전체 최신 문장은 `iris_dvf_descriptions.html`에 갱신했다. 이전 `.tmp/menu/run-f2wnvz9w/p/Iris.zip`은 보존하며 최신 후보라고 재사용하지 않는다.


### 후속 문형 및 역할 경계 교정 최종 검사와 새 후보

기존 최소 3노드 묶음: **3 passed in 133.73s (0:02:13)**, 정확한 명령 종료 코드 **0**.

```powershell
$env:IRIS_SHARED_MENU_VALIDATION='1'
uv run --project .\Iris\tooling python -I -B -m pytest --noconftest -c .\Iris\tooling\pyproject.toml .\Iris\build\description\v2\tests\test_layer3_description_composition.py::test_layer3_description_composition .\Iris\tooling\tests\test_tooltip_t2_projection.py::test_s2_supply_and_owner_integration .\Iris\build\description\v2\tests\test_layer3_product_integration.py::test_product_contract --basetemp .\.tmp\common -q -s --tb=short
```

로그: `.tmp/prose/refine-tests.log`. Blocks/상류 생산자는 바꾸지 않아 별도 block 검사를 추가하지 않았다. Lua syntax와 런타임/메뉴/package 검사는 공통 product node의 같은 stage/ZIP 결과를 공유했다. 새 Gate, 전체 Run A/B, 추가 confidence 실행은 없다.

- 새 ZIP: `.tmp/menu/run-eek7qzgg/p/Iris.zip`
- SHA256: `01ca01730f67e2de24c101def308ce643f07c3828f035ef6283a16ba32543e73`
- product: `l3p-505c60d31143b06b96c05ee070f7971c33dd985492d86bcf868ad9d172a0d5cf`

최신 compact(S2)와 expanded(Menu)의 source 결속을 기존 제품 경로에서 검증했다. S3 획득/Acquisition 문형을 보존한 실제 ZIP의 static row를 읽었으며 Base.CannedMilk에는 S3가 없다. 이전 run-f2wnvz9w 후보는 보존한다. **implemented_only**, 실제 게임 미관찰. 설치/commit/push 없음.


## 2026-09-13 전체 자기 이름 반복 공통 문형 교정

상태: **implemented_only**. 최종 자동 검사는 아래에 별도 기록한다.

직전 1014c47c 결과를 기준으로 전체 이름 일치 98문형과 최종 잔여 44문형을 읽고, 변경 Before/After의 고유 segment 135그룹을 전부 대조했다. 긴 양말·티셔츠·Sheet·전자기기·창의 네 전체 문면을 읽었다. 문자열 일치 수는 검토 후보이며 오류 또는 품질 수락 수가 아니다.

실제 문면 변경: **279아이템 / 1012좌표**. 변경 분모는 2,105아이템 / 8,420좌표다.

- 전체 2,105개 아이템의 KO/EN compact/expanded 8,420좌표를 조사했다. 자기 이름 문자열이 있는 282개/98문형을 대조하고 display_names/subject_names를 사용하는 공통 producer 경로를 조사했다.
- 의류 compact에서 자기 이름을 생략하고 천 회수와 찢지 않은 상태의 로프 제작을 별개 대안으로 표현한다. expanded에서도 찢지 않은 원물 상태를 유지하고 자기 이름 대신 EN It을 사용한다. KO 이 아이템/이것/그것으로 대체하지 않는다.
- 분해/변형이 있는 아이템에 display name을 일괄 덧붙이던 공통 처리를 제거했다. 전자기기/탄약은 분해 전, 병은 깨기 전, 부착물 창은 분리 전 상태 관계로 표현한다. 결과물의 활용으로 읽히지 않도록 상태는 보존한다.
- 같은 기준으로 지도/거울/통나무/그릇/설치 자물쇠/로프와 낚싯대 파손/돌 도구 마모·손실/붕대 감염/골절 고정의 자기 이름 반복을 교정했다. 조건·결과·독립 활용의 사실 결속은 유지한다.
- 통조림 실제 내용물, 소독솜/개구리 고기/찢어진 천/제작 타이머 등의 결과, 드라이버·가위·통조림 따개, 호환 장착 위치, 운동명, 호박 조각 작업명은 보존했다. 최종 문자열 일치 51개/44문형은 이런 대상·결과·역할 및 부분 문자열 일치이며 일괄 삭제하지 않았다.
- 동일 공통 경로로 생성 JSON을 재생산했다. FullType 문장 override, 생성 JSON 수동 패치, 새 validator/authority/전체 Run A/B는 없다.
- 각 locale/surface present1981, absent124 유지.
- 가위 moving_furniture의 실제 가구 매핑 근거는 미확인 상태다. 기존 문장을 확정 수락하지 않으며 이번 자기 이름 교정에서 기능/가구명을 추가하지 않았다.
- 차량42 구체 목적, 기존 unresolved/보류 및 exact ID L4 공급 공백 유지.
- EN 독립 품질 수락과 실제 PZ 관찰은 수행하지 않았다. 기존 후보/검사 기록 보존. 외부 설치, commit/push 없음.

Descriptions SHA256: `3d25f5f28d98fa48d2676bb91ccf96c055c3a6d0959804b095b0a90ffdf77b94`

Blocks SHA256(불변): `9d68e982cd508b3a4beafc9d1a8892668c9470d4581f7db0d1761e602926e161`

**Base.Socks_Long**

Before KO compact: 착용하거나 찢어서 천 조각을 얻을 수 있다. 긴 양말을 시트 로프 제작 재료나 연료, 불쏘시개로도 쓸 수 있다.

After KO compact: 착용하거나 찢어서 천 조각을 얻을 수 있다. 찢지 않고 시트 로프 제작에 쓸 수도 있다. 연료나 불쏘시개로도 쓸 수 있다.

After EN compact: It can be worn or ripped to obtain cloth scraps, used intact to make sheet rope, or used as fuel and tinder.

**Base.Tshirt_DefaultTEXTURE_TINT**

Before KO compact: 착용하거나 찢어서 천 조각을 얻을 수 있다. 티셔츠를 시트 로프 제작 재료나 연료, 불쏘시개로도 쓸 수 있다.

After KO compact: 착용하거나 찢어서 천 조각을 얻을 수 있다. 찢지 않고 시트 로프 제작에 쓸 수도 있다. 연료나 불쏘시개로도 쓸 수 있다.

After EN compact: It can be worn or ripped to obtain cloth scraps, used intact to make sheet rope, or used as fuel and tinder.

**Base.Sheet**

Before KO compact: 물품 제작의 재료로 쓸 수 있다. 찢어서 천 조각을 얻거나, 찢기 전 천을 시트 로프 재료로 쓸 수 있다. 커튼이 없는 대응 창문이나 문에 커튼으로 설치할 수 있다. 연료나 불쏘시개로 쓸 수 있다.

After KO compact: 물품 제작의 재료로 쓸 수 있다. 찢어서 천 조각을 얻을 수 있다. 찢지 않고 시트 로프 제작에 쓸 수도 있다. 커튼이 없는 대응 창문이나 문에 커튼으로 설치할 수 있다. 연료나 불쏘시개로 쓸 수 있다.

After EN compact: It can be used as material for crafting. It can be ripped for cloth scraps or used intact to make sheet rope. It can be installed as a curtain on an eligible window or door without one. It can be used as fuel or tinder.

**Radio.RadioRed**

Before KO compact: 프리미엄 테크 라디오는 전원이 공급되면 기록 매체를 재생하거나 라디오 방송을 청취할 수 있다. 내용에 따라 능력치, 경험치, 제작법 학습 효과를 얻을 수 있다. 드라이버로 분해해 전자 부품을 회수하는 데 쓸 수 있다.

After KO compact: 분해하지 않고 전원이 공급되면 기록 매체를 재생하거나 라디오 방송을 청취할 수 있다. 내용에 따라 능력치, 경험치, 제작법 학습 효과를 얻을 수 있다. 드라이버로 분해해 전자 부품을 회수하는 데 쓸 수 있다.

After EN compact: While intact and powered, it can be used for playing recorded media and listening to radio broadcasts. Depending on the content, it can affect stats, XP or recipe knowledge. It can be dismantled with a screwdriver to recover electronic parts.

**Base.BeerEmpty**

Before KO compact: 깨뜨려 깨진 병을 얻을 수 있다. 맥주 병 (비어있음)은 물을 담아 보관하거나 운반할 수 있다. 맥주 병 (비어있음)은 화염병 제작에 재료로 사용할 수 있다.

After KO compact: 깨뜨려 깨진 병을 얻을 수 있다. 깨지 않은 상태로 물을 담아 보관하거나 운반할 수 있다. 깨지 않은 상태로 화염병 제작에 재료로 사용할 수 있다.

After EN compact: It can be broken to obtain Smashed Bottle. While unbroken, it can hold water for storage or carrying. While unbroken, it can be used as a material for making Molotov Cocktail.

**Base.SpearBreadKnife**

Before KO compact: 물가에서 미끼 없이 창낚시에 쓸 수 있다. 창의 부착물을 회수할 수 있다. 창 (빵칼)은 무기로 쓸 수 있다.

After KO compact: 물가에서 미끼 없이 창낚시에 쓸 수 있다. 창의 부착물을 회수할 수 있다. 부착물을 분리하지 않고 무기로 쓸 수 있다.

After EN compact: With its attachment still fitted, it can be used for spear fishing at water without bait. Its spear attachment can be recovered. With its attachment still fitted, it can be used as a weapon.

**Base.CannedMilk**

Before KO compact: 통조림 따개로 개봉해 연유를 마실 수 있다. 꺼낸 연유를 요리 재료로도 쓸 수 있다.

After KO compact: 통조림 따개로 개봉해 연유를 마실 수 있다. 꺼낸 연유를 요리 재료로도 쓸 수 있다.

After EN compact: It can be opened with a Can Opener to drink the Evaporated Milk. The extracted Evaporated Milk can also be used as a cooking ingredient.

전체 Before/After는 기존 `iris_dvf_description_review.html`, 전체 최신 문장은 `iris_dvf_descriptions.html`에 갱신했다. 이전 `.tmp/menu/run-eek7qzgg/p/Iris.zip`은 보존하며 최신 후보라고 재사용하지 않는다.


### 전체 자기 이름 반복 교정 최종 검사와 새 후보

기존 최소 3노드 묶음: **3 passed in 138.96s (0:02:18)**, 정확한 명령 종료 코드 **0**.

```powershell
$env:IRIS_SHARED_MENU_VALIDATION='1'
uv run --project .\Iris\tooling python -I -B -m pytest --noconftest -c .\Iris\tooling\pyproject.toml .\Iris\build\description\v2\tests\test_layer3_description_composition.py::test_layer3_description_composition .\Iris\tooling\tests\test_tooltip_t2_projection.py::test_s2_supply_and_owner_integration .\Iris\build\description\v2\tests\test_layer3_product_integration.py::test_product_contract --basetemp .\.tmp\common -q -s --tb=short
```

로그: `.tmp/prose/self-tests.log`. Blocks/상류 생산자는 바꾸지 않아 별도 block 검사를 추가하지 않았다. Lua syntax와 런타임/메뉴/package 검사는 공통 product node의 같은 stage/ZIP 결과를 공유했다. 새 Gate, 전체 Run A/B, 추가 confidence 실행은 없다.

- 새 ZIP: `.tmp/menu/run-5debqnfk/p/Iris.zip`
- SHA256: `3a9a31a04d59217e0e16d7d46e93c130bc77f5fb7db75136b55a9c96272db2e5`
- product: `l3p-f3aa38ae0288fa1cacfc0173cb3bd3ac01d8193ef8e08572059ae07944519d23`

최신 compact(S2)와 expanded(Menu)의 source 결속을 기존 제품 경로에서 검증했다. S3 획득/Acquisition 문형을 보존한 실제 ZIP의 static row를 읽었으며 Base.CannedMilk에는 S3가 없다. 이전 run-eek7qzgg 후보는 보존한다. **implemented_only**, 실제 게임 미관찰. 설치/commit/push 없음.


## 2026-09-13 독립 활용 문형의 불필요 상태절 제거

상태: **implemented_only**. 최종 자동 검사는 아래에 별도 기록한다.

직전 3d25f5f2 결과 대비 변경 문면 72개 고유 segment 그룹을 모두 읽었다. Socks_Long/BeerEmpty/SpearBreadKnife/Radio.RadioRed의 KO/EN compact/expanded 전체 문면과 독립 활용 배치를 대조했다.

실제 문면 변경: **221아이템 / 884좌표**. 변경 분모는 2,105아이템 / 8,420좌표다.

- 최신 사용자 지시: 용도끼리는 독립적으로 서술한다. 앞 설명과 이어질 것을 가정해 찢지 않고/깨지 않고 같은 상태절을 넣지 않는다. 이 지시는 앞선 자기 이름 교정 기록의 상태절 유지 설명을 대체한다. 이전 기록/후보 자체는 보존한다.
- self-name 후처리의 분해하지 않고/깨지 않은 상태로/부착물을 분리하지 않고 및 EN While intact/unbroken/attachment still fitted 접두어를 제거했다. 라디오 전원 등 실제 조건은 유지한다.
- 의류와 Sheet의 찢지 않고/used intact도 제거했다. 천 회수와 시트 로프 제작은 각각 현재 아이템의 독립 활용이다. KO/EN compact/expanded에 같은 기준을 적용했다.
- 병/탄약/부착물 창/전자기기의 독립 활용 단위를 회수·변형 단위 앞에 배치한다. 각 단위의 사실·조건·후속 결과 문장은 함께 보존하고 이름이나 상태 조건을 추가하지 않는다.
- 이번 self-name 변경에서 생긴 접두어와 관계 합성만 교정했다. FullType 문장 override, 생성 JSON 수동 패치, 새 광범위 감사/validator/authority/전체 Run A/B 없음.
- 각 locale/surface present1981, absent124 유지.
- 통조림 내용물·회수 결과·도구/대상 이름과 기존 실제 조건 보존.
- 가위 실제 가구 매핑 미확인, 차량42/기존 unresolved/보류/L4공급 공백 유지.
- EN 독립 품질 수락 및 실제 게임 관찰 없음. 외부 설치/commit/push 없음.

Descriptions SHA256: `e611c74cd18ed03d2ed8469d0b3dfb9897436d1e2f1209131bbd16fd0024eaff`

Blocks SHA256(불변): `9d68e982cd508b3a4beafc9d1a8892668c9470d4581f7db0d1761e602926e161`

**Base.Socks_Long**

Before KO compact: 착용하거나 찢어서 천 조각을 얻을 수 있다. 찢지 않고 시트 로프 제작에 쓸 수도 있다. 연료나 불쏘시개로도 쓸 수 있다.

After KO compact: 착용하거나 찢어서 천 조각을 얻을 수 있다. 시트 로프 제작에 쓸 수도 있다. 연료나 불쏘시개로도 쓸 수 있다.

After EN compact: It can be worn or ripped to obtain cloth scraps, used to make sheet rope, or used as fuel and tinder.

**Base.Tshirt_DefaultTEXTURE_TINT**

Before KO compact: 착용하거나 찢어서 천 조각을 얻을 수 있다. 찢지 않고 시트 로프 제작에 쓸 수도 있다. 연료나 불쏘시개로도 쓸 수 있다.

After KO compact: 착용하거나 찢어서 천 조각을 얻을 수 있다. 시트 로프 제작에 쓸 수도 있다. 연료나 불쏘시개로도 쓸 수 있다.

After EN compact: It can be worn or ripped to obtain cloth scraps, used to make sheet rope, or used as fuel and tinder.

**Base.Sheet**

Before KO compact: 물품 제작의 재료로 쓸 수 있다. 찢어서 천 조각을 얻을 수 있다. 찢지 않고 시트 로프 제작에 쓸 수도 있다. 커튼이 없는 대응 창문이나 문에 커튼으로 설치할 수 있다. 연료나 불쏘시개로 쓸 수 있다.

After KO compact: 물품 제작의 재료로 쓸 수 있다. 찢어서 천 조각을 얻을 수 있다. 시트 로프 제작에 쓸 수도 있다. 커튼이 없는 대응 창문이나 문에 커튼으로 설치할 수 있다. 연료나 불쏘시개로 쓸 수 있다.

After EN compact: It can be used as material for crafting. It can be ripped for cloth scraps or used to make sheet rope. It can be installed as a curtain on an eligible window or door without one. It can be used as fuel or tinder.

**Radio.RadioRed**

Before KO compact: 분해하지 않고 전원이 공급되면 기록 매체를 재생하거나 라디오 방송을 청취할 수 있다. 내용에 따라 능력치, 경험치, 제작법 학습 효과를 얻을 수 있다. 드라이버로 분해해 전자 부품을 회수하는 데 쓸 수 있다.

After KO compact: 전원이 공급되면 기록 매체를 재생하거나 라디오 방송을 청취할 수 있다. 내용에 따라 능력치, 경험치, 제작법 학습 효과를 얻을 수 있다. 드라이버로 분해해 전자 부품을 회수하는 데 쓸 수 있다.

After EN compact: With power, it can be used for playing recorded media and listening to radio broadcasts. Depending on the content, it can affect stats, XP or recipe knowledge. It can be dismantled with a screwdriver to recover electronic parts.

**Base.BeerEmpty**

Before KO compact: 깨뜨려 깨진 병을 얻을 수 있다. 깨지 않은 상태로 물을 담아 보관하거나 운반할 수 있다. 깨지 않은 상태로 화염병 제작에 재료로 사용할 수 있다.

After KO compact: 물을 담아 보관하거나 운반할 수 있다. 화염병 제작에 재료로 사용할 수 있다. 깨뜨려 깨진 병을 얻을 수 있다.

After EN compact: It can hold water for storage or carrying. It can be used as a material for making Molotov Cocktail. It can be broken to obtain Smashed Bottle.

**Base.SpearBreadKnife**

Before KO compact: 물가에서 미끼 없이 창낚시에 쓸 수 있다. 창의 부착물을 회수할 수 있다. 부착물을 분리하지 않고 무기로 쓸 수 있다.

After KO compact: 물가에서 미끼 없이 창낚시에 쓸 수 있다. 무기로 쓸 수 있다. 창의 부착물을 회수할 수 있다.

After EN compact: It can be used for spear fishing at water without bait. It can be used as a weapon. Its spear attachment can be recovered.

**Base.CannedMilk**

Before KO compact: 통조림 따개로 개봉해 연유를 마실 수 있다. 꺼낸 연유를 요리 재료로도 쓸 수 있다.

After KO compact: 통조림 따개로 개봉해 연유를 마실 수 있다. 꺼낸 연유를 요리 재료로도 쓸 수 있다.

After EN compact: It can be opened with a Can Opener to drink the Evaporated Milk. The extracted Evaporated Milk can also be used as a cooking ingredient.

전체 Before/After는 기존 `iris_dvf_description_review.html`, 전체 최신 문장은 `iris_dvf_descriptions.html`에 갱신했다. 이전 `.tmp/menu/run-5debqnfk/p/Iris.zip`은 보존하며 최신 후보라고 재사용하지 않는다.


### 독립 활용 상태절 제거 최종 검사와 새 후보

기존 최소 3노드 묶음: **3 passed in 132.15s (0:02:12)**, 정확한 명령 종료 코드 **0**.

```powershell
$env:IRIS_SHARED_MENU_VALIDATION='1'
uv run --project .\Iris\tooling python -I -B -m pytest --noconftest -c .\Iris\tooling\pyproject.toml .\Iris\build\description\v2\tests\test_layer3_description_composition.py::test_layer3_description_composition .\Iris\tooling\tests\test_tooltip_t2_projection.py::test_s2_supply_and_owner_integration .\Iris\build\description\v2\tests\test_layer3_product_integration.py::test_product_contract --basetemp .\.tmp\common -q -s --tb=short
```

로그: `.tmp/prose/prefix-tests.log`. Blocks/상류 생산자는 바꾸지 않아 별도 block 검사를 추가하지 않았다. Lua syntax와 런타임/메뉴/package 검사는 공통 product node의 같은 stage/ZIP 결과를 공유했다. 새 Gate, 전체 Run A/B, 추가 confidence 실행은 없다.

- 새 ZIP: `.tmp/menu/run-ms8p4gav/p/Iris.zip`
- SHA256: `63c125cc59db971f31928ce3f04ff3a4972378225978d9465b0430d713590e56`
- product: `l3p-c22fc3c5694e25ee5091ebd8243873f33294f9af352494163ace07204d16f8b8`

최신 compact(S2)와 expanded(Menu)의 source 결속을 기존 제품 경로에서 검증했다. S3 획득/Acquisition 문형을 보존한 실제 ZIP의 static row를 읽었으며 Base.CannedMilk에는 S3가 없다. 이전 run-5debqnfk 후보는 보존한다. **implemented_only**, 실제 게임 미관찰. 설치/commit/push 없음.


## 2026-09-13 발견사항 16개 공통 경로 교정 및 근거 보류

상태: **implemented_only**. 최종 자동 검사는 아래에 별도 기록한다.

전체 2,105개 입력을 위16개 발견사항의 공통 activity/function/role 경로에 대조했다. 각 범위와 변경/유지 항목을 기존 검수 자료에 기록하고, 실제 원문 및 조건·결과를 읽어 처리 여부를 판단했다. 변경 문면뿐 아니라 유지된 조리 재료·도구 부착물·독서/기술서·물 용기·금속 재료·착용 형태도 대조했다. 같은 기술서의 기술명·배율 등 반복 변수는 공통 문형으로 검토했다. 문면 읽기와 생성/자동 검사 성공은 전체 아이템의 모든 규칙 품질 수락을 뜻하지 않는다.

실제 문면 변경: **215아이템 / 811좌표**. 변경 분모는 2,105아이템 / 8,420좌표다.

- 1. 교정 — 낚싯대4의 compact 후속 변형 결과를 제거하고 파손·미끼 손실을 expanded와 일치시켰다. 줄 끊김 조건 유지.
- 2. 교정/해당 없음 — 조리 하위 활동29의 입력 역할을 대조했다. BakingTray/MuffinTray는 반죽을 담아 요리를 만드는 용도, Yeast는 반죽 제작 재료로 설명한다. 나머지는 이미 요리 재료/음식 준비로 묶이거나 독립 포장·미끼 활용이어서 불완전 문장이 없다.
- 3. 교정 — 관련24개 중 창 자체와 부착물, 장치 개조 대상과 부착 부품, 소모 재료, 도구를 구별했다. Add 계열 채택 recipe의 두 번째 입력이 작동 부품임을 사용했다. 기존 attachment 역할7개 등은 현재 문형을 유지하며 재료로 바꾸지 않았다.
- 4. 공개 경계 교정/장식 근거 보류 — Pumpkin의 pumpkin_carving material은 단순 원물 가공으로 내부화했다. 먹기·조리·미끼는 유지. 칼의 실제 조각 도구 활용6개는 보존했다. HalloweenPumpkin이라는 결과 이름으로 장식 기능을 발명하지 않았다.
- 5. 교정 — 소화28개를 바닥이나 몸에 붙은 불을 끌 수 있다로 표현했다. EN은 ground or characters를 유지하여 플레이어만으로 좁히지 않았다.
- 6. 교정 — 분무액 준비4개 중 물을 담는 분무기는 혼합 용기, 우유류·담배는 투입 재료로 구별했다. scripts/farming.txt의 두 제조법 입력·결과와 기존 store_water/소비 기능을 대조했다.
- 7. 교정 — 열쇠7개의 잠금/시동/최초 문 열기 경보 제한을 플레이어 동사로 표현했다. 처음 열기와 이미 울리는 경보를 끄지 못함, 맞는 열쇠 제한은 유지했다. 정비 열쇠 요구는 계속 내부다.
- 8. 교정 — 관련16개 모두 현재 원문을 대조했다. 자물쇠 설치 가능 대상/문 제외, 커튼 없는 창문·문, 매체 재생, 헤드폰 연결과 TV 제외, 원격 장치 연결 관계로 설명했다. 실제 가구명/기기명을 새로 지정하지 않았다.
- 9. 교정 — 벨트/홀스터3개를 물품을 걸거나 넣어 휴대하는 목적으로 표현했다. ISHotbarAttachDefinition.lua의 도구·무전기/홀스터 연결과 items_weapons.txt의 AttachmentType=Holster를 확인했다. 모든 물품 부착을 주장하지 않는다.
- 10. 문면 교정/학습 기능 근거 보류 — 독서102개를 분류했다. mood cap의 악화 방지 문형을 교정했으며 감소·치료로 바꾸지 않았다. 기술서의 조건·배율은 유지한다. CookingMag 등의 현재 L3 입력에는 제작법 학습 사실이 없어 읽을 수 있다를 남겼다. 소스의 recipe 학습/L4 공급과 L3 채택 공백은 기능이 없다는 판정도, 교정 완료 판정도 아니다.
- 11. 교정 — Battery1의 중복 대상은 호환 조명·휴대/건전지 기기로 묶고 남은 충전량으로 작동시키는 용도로 표현했다. 신규 기기 종류나 충전량 보장은 추가하지 않았다.
- 12. 교정/기존 보류 유지 — 현재 장착·탱크·문·좌석·타이어 경로42개를 대조했다. 좌석·탱크·문의 장착과 실제 사용을 묶고 타이어 손실 중복을 제거했다. 탱크 상태70·엔진 정지·타이어 손실 조건은 보존했다. 이 범위42는 과거 미확정 차량42를 해소했다는 뜻이 아니며 새로운 구체 기능/매핑을 추가하지 않았다.
- 13. 공통 묶음 교정/독립 목적 유지 — 목공·건축·용접, 음식 손질 도구, 재료 제작 목적, 의류 패치, 물 보관·운반·이동, 연료 이동, 밭/무덤 작업을 동일 역할/활용별로 묶었다. 명시된 긴 사례 모두 양표면을 대조했다. Log의 묶음·숯·수박 도구·연료, TreeBranch/WoodenStick의 골절·제작·점화·연료 등 독립 활용은 길이만을 이유로 삭제하지 않았다. primary_use/글자수 정책/expanded에만 이전 없음.
- 14. 교정/해당 없음 — BlowTorch/WeldingMask는 용접에 쓰는 역할로, BrokenFishingNet는 철사 회수로 표현했다. GardenFork 등의 동사와 수확 제외, 화장/제거, 수면 보조약 문형을 교정했다. SharpedStone의 실제 소모 가능성은 창 제작과 함께 유지했다. 금속판의 크기 전환 손실·기존 마모 보류 및 이미 간결한 진통/공포 약품 문형은 보존했다.
- 15. 교정/해당 없음 — 착용 형태·텐트 관련80개를 대조했다. 형태 변경은 착용과 함께 연료 앞에 배치했고 텐트 설치와 휴식/수면은 같은 활용으로 묶었다. 이미 올바른 순서인 장신구·모자 등의61개는 그대로다.
- 16. 공개 확정 보류 — moving_furniture20개 모두 내부에 근거를 보존하고 공개 확정을 제거했다. 등록표는 도구 종류만 제공하고 ISMoveableSpriteProps.lua는 실제 PickUpTool/PlaceTool 값을 읽는다. 현재 허용 저장소에서 구체 sprite 매핑을 찾지 못했다. 20개 모두 실제 불가능하다는 뜻이 아니며 가위만의 오류나 두 동작 모두의 존재를 추정하지 않는다. News_EN의 Shovel 언급은 채택된 구체 매핑을 대신하지 않는다.
- 상태 implemented_only. 각 locale/surface present1981, absent124 유지.
- 가구20 실제 매핑, L3 잡지 학습 사실 공백, 기존 차량 구체 목적/미해결 관계/L4 exact-ID 공급 공백은 보류다.
- 실제 게임 관찰과 EN 독립 품질 수락 없음. 사용자에게 문장 검수 의무를 넘기지 않는다.
- 기존 dirty/후보/기록 보존. FullType 완성 문장 override, 생성 JSON 수동 수정, 새 검증 authority/ledger/전체 Run A/B, 외부 접근/설치/commit/push 없음.

범위별 해당/변경/유지(항목 간 중복 포함):

- 1 scope 4 changed 4 unchanged 0
- 2 scope 29 changed 5 unchanged 24
- 3 scope 24 changed 17 unchanged 7
- 4 scope 7 changed 5 unchanged 2
- 5 scope 28 changed 28 unchanged 0
- 6 scope 4 changed 4 unchanged 0
- 7 scope 7 changed 7 unchanged 0
- 8 scope 16 changed 16 unchanged 0
- 9 scope 3 changed 3 unchanged 0
- 10 scope 102 changed 12 unchanged 90
- 11 scope 1 changed 1 unchanged 0
- 12 scope 42 changed 42 unchanged 0
- 13 scope 96 changed 66 unchanged 30
- 14 scope 30 changed 26 unchanged 4
- 15 scope 80 changed 19 unchanged 61
- 16 scope 20 changed 20 unchanged 0

Descriptions SHA256: `524f74b79d6d5d2b258b7f29435e34e16d901456bac98f2661a92f98819a172f`

Blocks SHA256(불변): `9d68e982cd508b3a4beafc9d1a8892668c9470d4581f7db0d1761e602926e161`

**Base.CraftedFishingRod**

Before KO compact: 물가에서 맞는 미끼와 함께 낚시할 수 있다. 낚싯줄이 끊어지면 부러지거나 막대로 바뀌며 미끼를 잃는다. 무기로 쓸 수 있다.

After KO compact: 물가에서 맞는 미끼와 함께 낚시할 수 있다. 낚싯줄이 끊어지면 파손되고 미끼를 잃는다. 무기로 쓸 수 있다.

After EN compact: It can be used for rod fishing at water with matching bait. If the line breaks, it breaks and the bait is lost. It can be used as a weapon.

**Base.BakingTray**

Before KO compact: 반죽을 담아 만들 수 있다.

After KO compact: 반죽을 담아 요리를 만드는 데 쓸 수 있다.

After EN compact: It can hold dough for preparing food.

**Base.MuffinTray**

Before KO compact: 반죽을 담아 만들 수 있다.

After KO compact: 반죽을 담아 요리를 만드는 데 쓸 수 있다.

After EN compact: It can hold dough or batter for preparing food.

**Base.Yeast**

Before KO compact: 반죽에 넣을 수 있다.

After KO compact: 반죽을 만드는 재료로 쓸 수 있다.

After EN compact: It can be used as an ingredient for preparing dough and batter.

**Base.SpearCrafted**

Before KO compact: 물가에서 미끼 없이 창낚시에 쓸 수 있다. 창 부착물 장착에 재료로 사용할 수 있다. 무기로 쓸 수 있다.

After KO compact: 부착물을 달아 쓸 수 있다. 무기로 쓸 수 있다. 물가에서 미끼 없이 창낚시에 쓸 수 있다.

After EN compact: It can be fitted with an attachment. It can be used as a weapon. It can be used for spear fishing at water without bait.

**Base.Aerosolbomb**

Before KO compact: 장치 작동 부품 장착에 재료로 사용할 수 있다. 투척 공격에 쓸 수 있다.

After KO compact: 작동 부품을 달아 개조할 수 있다. 투척 공격에 쓸 수 있다.

After EN compact: It can be modified by fitting triggering components. It can be used for throwing attacks.

**Base.Pumpkin**

Before KO compact: 먹거나 요리 재료로 쓸 수 있다. 덫의 미끼로도 쓸 수 있다. 호박 조각에 재료로 사용할 수 있다.

After KO compact: 먹거나 요리 재료로 쓸 수 있다. 덫의 미끼로도 쓸 수 있다.

After EN compact: It can be eaten or used as a cooking ingredient. It can also be used as trap bait.

**Base.WaterPot**

Before KO compact: 붕대 소독에 쓸 수 있다. 재료를 담아 요리할 수 있다. 물을 담아 보관하거나 운반할 수 있다. 다른 용기나 저장 시설로 물을 옮길 수 있다. 담긴 물은 작물 급수, 차량 혈흔 세척, 소화, 음용에 쓸 수 있다 (오염수 음용은 중독 위험).

After KO compact: 붕대 소독에 쓸 수 있다. 재료를 담아 요리할 수 있다. 물을 보관, 운반하거나 다른 용기나 물 저장 시설로 옮길 수 있다. 담긴 물은 작물 급수, 차량 혈흔 세척, 소화, 음용에 쓸 수 있다 (오염수 음용은 중독 위험).

After EN compact: It can be used to disinfect bandaging. It can hold ingredients for cooking. It can store and carry water or transfer it to other containers or water storage fixtures. Its water can be used for watering crops, washing vehicle bloodstains, extinguishing fires, and drinking; drinking tainted water risks poisoning.

**farming.GardeningSprayEmpty**

Before KO compact: 물을 담아 보관하거나 운반할 수 있다. 작물 치료제 준비에 재료로 사용할 수 있다.

After KO compact: 작물 치료용 분무액을 만드는 용기로 쓸 수 있다. 물을 담아 보관하거나 운반할 수 있다.

After EN compact: It can hold the mixture when making crop-treatment spray. It can hold water for storage or carrying.

**Base.CarKey**

Before KO compact: 맞는 차량의 첫 문 개방 경보를 피하지만 이미 울리는 경보는 끄지 않는다. 맞는 문의 잠금을 조작할 수 있다. 맞는 구조물 자물쇠를 제거할 수 있으며 이때 소모된다. 맞는 차량의 시동이나 점화장치를 조작할 수 있다.

After KO compact: 열쇠가 맞는 차량의 문을 처음 열 때 경보가 울리지 않게 한다. 이미 울리는 경보는 끄지 못한다. 열쇠가 맞는 문을 잠그거나 열 수 있다. 맞는 구조물 자물쇠를 제거할 수 있으며 이때 소모된다. 열쇠가 맞는 차량의 시동을 거는 데 쓸 수 있다.

After EN compact: It prevents the alarm from being triggered when first opening the matching vehicle. It cannot silence an alarm already ringing. It can lock or unlock a door with a matching lock. It can remove a matching structure padlock and is consumed in the process. It can be used to start the matching vehicle.

**Base.Sheet**

Before KO compact: 물품 제작의 재료로 쓸 수 있다. 찢어서 천 조각을 얻을 수 있다. 시트 로프 제작에 쓸 수도 있다. 커튼이 없는 대응 창문이나 문에 커튼으로 설치할 수 있다. 연료나 불쏘시개로 쓸 수 있다.

After KO compact: 물품 제작에 재료로 쓸 수 있다. 찢어서 천 조각을 얻을 수 있다. 시트 로프 제작에 쓸 수도 있다. 커튼이 없는 창문이나 문에 커튼으로 달아 쓸 수 있다. 연료나 불쏘시개로 쓸 수 있다.

After EN compact: It can be used as material for crafting. It can be ripped for cloth scraps or used to make sheet rope. It can be used as a curtain on an eligible window or door without one. It can be used as fuel or tinder.

**Base.Belt2**

Before KO compact: 허리에 착용할 수 있다. 착용하면 맞는 유형의 물품을 부착하는 좌우 벨트 슬롯을 제공한다. 불쏘시개로 소모할 수 있다.

After KO compact: 허리에 착용할 수 있다. 착용하면 허리 양쪽에 도구나 무전기를 걸어 휴대할 수 있다. 불쏘시개로 소모할 수 있다.

After EN compact: It can be worn at the waist. When worn, it can carry compatible tools or walkie-talkies on either side of the waist. It can be consumed as tinder.

**Base.Book**

Before KO compact: 독서할 수 있으며, 읽는 동안 지루함, 스트레스, 불행이 독서 시작 때보다 더 심해지지 않게 한다. 모닥불 키트 제작에 재료로 사용할 수 있다. 연료나 불쏘시개로 쓸 수 있다.

After KO compact: 독서 중 지루함, 스트레스, 불행이 더 심해지는 것을 막을 수 있다. 모닥불 키트 제작에 재료로 사용할 수 있다. 연료나 불쏘시개로 쓸 수 있다.

After EN compact: Reading can keep boredom, stress, and unhappiness from worsening beyond their starting levels. It can be used as a material for campfire-kit crafting. It can be used as fuel or tinder.

**Base.CookingMag1**

Before KO compact: 읽을 수 있다. 연료나 불쏘시개로 쓸 수 있다.

After KO compact: 읽을 수 있다. 연료나 불쏘시개로 쓸 수 있다.

After EN compact: It can be read. It can be used as fuel or tinder.

**Base.Battery**

Before KO compact: 남은 충전량을 호환되는 건전지형 조명, 기둥 조명, 휴대 기기, 배터리형 기기의 전원으로 공급할 수 있다.

After KO compact: 남은 충전량으로 호환되는 조명과 휴대 기기 등을 작동시킬 수 있다.

After EN compact: Its remaining charge can power compatible lights and portable or other battery-powered devices.

**Base.SmallGasTank1**

Before KO compact: 호환 차량에 장착할 수 있다. 차량에 장착해 연료를 보관한다. 엔진을 멈추면 맞는 용기로 연료를 넣거나 뺄 수 있고 작동 중에는 엔진에 공급한다. 탱크 상태가 70 미만이면 추가로 연료를 잃을 수 있다.

After KO compact: 호환 차량에 장착해 연료를 보관하고 엔진에 공급할 수 있다. 엔진을 끄면 맞는 용기로 연료를 넣거나 뺄 수 있다. 탱크 상태가 70 미만이면 연료가 추가로 줄 수 있다.

After EN compact: It can be installed in a compatible vehicle to store fuel and supply the engine. With the engine stopped, fuel can be added or siphoned with a compatible container. Tank condition below 70 can cause additional fuel loss.

**Base.Screwdriver**

Before KO compact: 전자기기 제작과 분해 및 조명 개조, 목공 및 건축물 분해, 일부 가구 집기와 설치, 차량과 무기의 부품 장착과 제거에 사용할 수 있다. 제작한 창에 부착하거나 무기로 쓸 수도 있다.

After KO compact: 전자기기 제작과 분해 및 조명 개조, 목공 및 건축물 분해, 차량과 무기의 부품 장착과 제거에 사용할 수 있다. 제작한 창에 부착하거나 무기로 쓸 수도 있다.

After EN compact: It can be used for making and dismantling electronic devices, plus lamp conversion to battery power; woodworking, plus structure disassembly; fitting and removing parts on vehicles and weapons. It can also be attached to a crafted spear or be used as a weapon.

**Base.BlowTorch**

Before KO compact: 금속 용접, 건축, 금속 바리케이드 설치와 철거, 불타거나 파손된 차량 분해에 사용할 수 있다.

After KO compact: 금속 용접, 건축, 금속 바리케이드 설치와 철거, 불타거나 파손된 차량 분해에 사용할 수 있다.

After EN compact: It can be used for metal welding and construction, installing or removing metal barricades, and dismantling burnt or smashed vehicles.

**camping.CampingTentKit**

Before KO compact: 설치한 텐트에서 쉬거나 잘 수 있다. 텐트를 설치할 수 있다.

After KO compact: 텐트를 설치해 쉬거나 잘 수 있다.

After EN compact: It can be pitched as a tent for resting or sleeping.

**Base.Scissors**

Before KO compact: 데님이나 가죽 의류의 조각 회수, 일부 가구 집기와 설치, 머리와 수염 손질에 사용할 수 있다. 제작한 창에 부착하거나 무기로 쓸 수도 있다.

After KO compact: 데님이나 가죽 의류의 조각 회수, 머리와 수염 손질에 사용할 수 있다. 제작한 창에 부착하거나 무기로 쓸 수도 있다.

After EN compact: It can be used for recovering strips from denim or leather clothing; hair and beard grooming. It can also be attached to a crafted spear or be used as a weapon.

전체 Before/After는 기존 `iris_dvf_description_review.html`, 전체 최신 문장은 `iris_dvf_descriptions.html`에 갱신했다. 이전 `.tmp/menu/run-ms8p4gav/p/Iris.zip`은 보존하며 최신 후보라고 재사용하지 않는다.


### 발견사항 16개 교정 최종 검사와 새 후보

기존 최소 3노드 묶음: **3 passed in 130.95s (0:02:10)**, 정확한 명령 종료 코드 **0**.

```powershell
$env:IRIS_SHARED_MENU_VALIDATION='1'
uv run --project .\Iris\tooling python -I -B -m pytest --noconftest -c .\Iris\tooling\pyproject.toml .\Iris\build\description\v2\tests\test_layer3_description_composition.py::test_layer3_description_composition .\Iris\tooling\tests\test_tooltip_t2_projection.py::test_s2_supply_and_owner_integration .\Iris\build\description\v2\tests\test_layer3_product_integration.py::test_product_contract --basetemp .\.tmp\common -q -s --tb=short
```

로그: `.tmp/prose/findings-tests.log`. Blocks/상류 생산자는 바꾸지 않아 별도 block 검사를 추가하지 않았다. Lua syntax와 런타임/메뉴/package 검사는 공통 product node의 같은 stage/ZIP 결과를 공유했다. 새 Gate, 전체 Run A/B, 추가 confidence 실행은 없다.

- 새 ZIP: `.tmp/menu/run-wi1iy1oy/p/Iris.zip`
- SHA256: `aae12ee19a9bcd1c0561affdbb1aa4d5e170a779fbe7efd57287aa1ff4eba513`
- product: `l3p-fc115dbf6ef0bc0dd8ad409ca944c0cc5fed222dac957f823ac750b4e075f7eb`

최신 compact(S2)와 expanded(Menu)의 source 결속을 기존 제품 경로에서 검증했다. S3 획득/Acquisition 문형을 보존한 실제 ZIP의 static row를 읽었으며 Base.CannedMilk에는 S3가 없다. 이전 run-ms8p4gav 후보는 보존한다. **implemented_only**, 실제 게임 미관찰. 설치/commit/push 없음.


## 2026-09-13 발견사항 잔여 교정과 부분해결 판정

상태: **implemented_only**. 최종 자동 검사는 아래에 별도 기록한다.

이번 잔여 공통 경로의 실제 전후 문면을 대조했다. 낚싯대4, 창 도구6의 조건 결속과 원문/제품 use unit 투영, 조종기3, 열쇠7, 이중 홀스터1, 물 용기24의 영향을 확인했다. KO/EN 양표면 45아이템/112좌표 변경은 변경 범위이며 전체 품질 수락이 아니다.

실제 문면 변경: **45아이템 / 112좌표**. 변경 분모는 2,105아이템 / 8,420좌표다.

- a / 지적9 해결 — 이중 홀스터의 양쪽에 홀스터에 중복을 허리 양쪽 홀스터에 맞는 총기를 넣어 휴대로 교정했다.
- b / 지적8 해결 — link_remote_device와 send_remote_trigger를 가진 조종기3개에서 함께 소지한 호환 장치 연결과 범위 내 원격 작동을 한 활용으로 합성했다. 연결만 가능한 장치는 이 경로로 합치지 않았다.
- c / 지적1·14·15 해결 — 낚싯대4의 낚시/줄 파손·미끼 손실, SharpedStone의 창 제작/소모, 칼5개의 창 제작/내구도 감소를 같은 활용 본문에 묶었다. 기존 continues_use가 원문·제품 투영에서는 줄바꿈으로 남던 차이를 바로잡았다. 독립 활용에는 줄바꿈을 유지하며 근거 없는 낚시 마모 연결은 추가하지 않았다.
- d / 지적7 해결 — 열쇠7개의 compact에서 문 잠금과 해제/구조물 자물쇠 제거/차량 시동을 나열하고 대상 일치를 한 번 명시한다. 경보 절차를 선두에서 빼고 첫 개방/이미 울리는 경보 제한을 요약했다. expanded는 차량 활용과 첫 개방 경보 제한을 같은 단위로, 문 잠금과 구조물 자물쇠 제거는 독립 단위로 유지한다. 자물쇠 제거 시 소모도 유지한다.
- d / 지적13 부분해결 — 물 용기24개의 compact 보관·운반·이동 문형을 줄였다. WaterPot에는 붕대 소독, 요리, 물 보관·운반·이동, 작물 급수·차량 혈흔 세척·소화·음용과 오염수 위험이 여전히 남는다. 이는 독립 활용과 의미를 바꾸는 제한이라 삭제하지 않았다. 기존 Screwdriver/Hammer/Shovel/Needle/WhiskeyEmpty/RippedSheetsDirty/Log/TreeBranch/WoodenStick의 앞선 공통 묶음 개선은 유지하지만 긴 목록 문제 전체가 해결됐다고 하지 않는다. WaterPot의 실제 남은 원문을 아래에 기록한다.
- 기존16개 판정 정정 — 1/2/3/5/6/7/8/9/11/14/15는 지적한 문면·구조 교정 범위에서 해결. 4는 원물 가공 경계 해결/장식 기능 근거 보류. 10은 감정 상한 문면 해결/잡지 학습 기능 근거 보류. 12는 근거 있는 부품 설명 개선/기존 미확정 차량 관계 보류. 13은 부분해결. 16은 구체 PickUpTool/PlaceTool 매핑 근거 보류. 모든16개 완료라는 앞선 총괄 표현을 대체한다.
- implemented_only. 실제 게임 미관찰, EN 독립 품질 승인 없음.
- 가구 매핑/잡지 학습/기존 차량·L4 공급 근거 공백 보류 유지.
- 독립 활용 삭제, FullType 완성 문장 override, 생성 JSON 수동 수정, 새 검증 체계나 전체 confidence 검사 없음. 기존 산출물 일치 검사는 같은 활용의 문장 결속을 반영하도록 갱신했다.

Descriptions SHA256: `6aa09cf681b5616da9812b3b6bdf457b7695b758ada771571c74b4bfa2801c70`

Blocks SHA256(불변): `9d68e982cd508b3a4beafc9d1a8892668c9470d4581f7db0d1761e602926e161`

**Base.HolsterDouble**

Before KO compact: 허리에 착용할 수 있다. 착용하면 양쪽에 홀스터에 맞는 총기를 넣어 휴대할 수 있다. 불쏘시개로 소모할 수 있다.

After KO compact: 허리에 착용할 수 있다. 허리 양쪽 홀스터에 맞는 총기를 넣어 휴대할 수 있다. 불쏘시개로 소모할 수 있다.

After EN compact: It can be worn at the waist. It can carry compatible firearms in holsters on both sides of the waist. It can be consumed as tinder.

**Base.RemoteCraftedV1**

Before KO compact: 조종 범위 안의 연결된 장치를 원격으로 작동시킬 수 있다. 함께 가지고 있는 호환 장치를 연결해 원격으로 작동시키도록 설정할 수 있다.

After KO compact: 함께 소지한 호환 장치를 연결해 조종 범위 안에서 원격으로 작동시킬 수 있다.

After EN compact: It can be linked to a compatible device carried together and remotely activate that device within range.

**Base.SharpedStone**

Before KO compact: 창 제작에 사용할 수 있다. 창을 만들 때 소모될 수 있다. 석제 도구 제작에 재료로 사용할 수 있다. 목공에 사용할 수 있다.

After KO compact: 창 제작에 사용할 수 있다. 창을 만들 때 소모될 수 있다. 석제 도구 제작에 재료로 사용할 수 있다. 목공에 사용할 수 있다.

After EN compact: It can be used for spear crafting. It may be consumed when used to craft a spear. It can be used as a material for stone-tool crafting. It can be used for woodworking.

**Base.FishingRod**

Before KO compact: 물가에서 맞는 미끼와 함께 낚시할 수 있다. 낚싯줄이 끊어지면 파손되고 미끼를 잃는다. 무기로 쓸 수 있다.

After KO compact: 물가에서 맞는 미끼와 함께 낚시할 수 있다. 낚싯줄이 끊어지면 파손되고 미끼를 잃는다. 무기로 쓸 수 있다.

After EN compact: It can be used for rod fishing at water with matching bait. If the line breaks, it breaks and the bait is lost. It can be used as a weapon.

**Base.HuntingKnife**

Before KO compact: 음식 손질, 목공, 낚시 장비, 창 제작, 호박 조각, 덤불, 덩굴 제거에 사용할 수 있다. 제작한 창에 부착하거나 무기로 쓸 수도 있다.

After KO compact: 음식 손질, 목공, 낚시 장비, 창 제작, 호박 조각, 덤불, 덩굴 제거에 사용할 수 있다. 제작한 창에 부착하거나 무기로 쓸 수도 있다.

After EN compact: It can be used for food preparation; woodworking; fishing-gear and spear crafting; pumpkin carving; removing bushes and vines. It can also be attached to a crafted spear or be used as a weapon.

**Base.CarKey**

Before KO compact: 열쇠가 맞는 차량의 문을 처음 열 때 경보가 울리지 않게 한다. 이미 울리는 경보는 끄지 못한다. 열쇠가 맞는 문을 잠그거나 열 수 있다. 맞는 구조물 자물쇠를 제거할 수 있으며 이때 소모된다. 열쇠가 맞는 차량의 시동을 거는 데 쓸 수 있다.

After KO compact: 문 잠금과 해제, 구조물 자물쇠 제거, 차량 시동에 쓸 수 있으며 대상과 열쇠가 맞아야 한다. 자물쇠 제거 시 소모된다. 차량 첫 개방 경보를 막지만 이미 울리는 경보는 끄지 못한다.

After EN compact: It can be used for locking and unlocking doors, removing structure padlocks, and starting vehicles, with a matching key required for each target. Removing a padlock consumes the key. It prevents the first-entry vehicle alarm but cannot silence an active alarm.

**Base.WaterPot**

Before KO compact: 붕대 소독에 쓸 수 있다. 재료를 담아 요리할 수 있다. 물을 보관, 운반하거나 다른 용기나 물 저장 시설로 옮길 수 있다. 담긴 물은 작물 급수, 차량 혈흔 세척, 소화, 음용에 쓸 수 있다 (오염수 음용은 중독 위험).

After KO compact: 붕대 소독에 쓸 수 있다. 재료를 담아 요리할 수 있다. 물을 보관, 운반하고 용기나 저장 시설에 부을 수 있다. 담긴 물은 작물 급수, 차량 혈흔 세척, 소화, 음용에 쓸 수 있다 (오염수 음용은 중독 위험).

After EN compact: It can be used to disinfect bandaging. It can hold ingredients for cooking. It can store, carry and pour water into containers or storage fixtures. Its water can be used for watering crops, washing vehicle bloodstains, extinguishing fires, and drinking; drinking tainted water risks poisoning.

전체 Before/After는 기존 `iris_dvf_description_review.html`, 전체 최신 문장은 `iris_dvf_descriptions.html`에 갱신했다. 이전 `.tmp/menu/run-wi1iy1oy/p/Iris.zip`은 보존하며 최신 후보라고 재사용하지 않는다.


### 발견사항 잔여 교정 최종 검사와 새 후보

실패한 제품 검사와 필수 S2 의존 검사 재실행: **2 passed in 122.38s (0:02:02)**, 정확한 명령 종료 코드 **0**.

```powershell
$env:IRIS_SHARED_MENU_VALIDATION='1'
uv run --project .\Iris\tooling python -I -B -m pytest --noconftest -c .\Iris\tooling\pyproject.toml .\Iris\tooling\tests\test_tooltip_t2_projection.py::test_s2_supply_and_owner_integration .\Iris\build\description\v2\tests\test_layer3_product_integration.py::test_product_contract --basetemp .\.tmp\common -q -s --tb=short
```

최초 최소3노드 실행은 1 failed, 2 passed in 80.32s / exit 1이었다. 제품 검사 기대값이 같은 활용의 문장을 줄바꿈으로 연결하도록 남아 있어 실패했고 공백 연결로 수정했다. 단독 제품 재실행은 S2 공유 입력이 없어 B corpus/owner mismatch로 exit 1, 1 failed in 2.80s였다. 이어 필수 S2와 제품2노드를 함께 실행했지만 Lua 로더의 기존 줄바꿈 결속 검사에서 1 failed, 1 passed in 91.00s / exit 1이었다. 로그는 `.tmp/prose/residual-dependent-tests.log`에 보존했다. IrisLayer3DataLookup.lua의 기존 일치 검사도 같은 활용 내부는 공백, 활용 사이는 줄바꿈으로 대조하도록 맞췄다. 문장 재작성이나 새 검증 체계를 런타임에 추가한 것이 아니다. 아래는 해당 수정 후 필수2노드 최종 재실행 결과다. 최초 설명 조합 노드는 성공했지만 최초 묶음 전체를 PASS로 표시하지 않는다. 로그: `.tmp/prose/residual-tests.log`, `.tmp/prose/residual-product-tests.log`.

로그: `.tmp/prose/residual-dependent-final-tests.log`. Blocks/상류 생산자는 바꾸지 않아 별도 block 검사를 추가하지 않았다. Lua syntax와 런타임/메뉴/package 검사는 공통 product node의 같은 stage/ZIP 결과를 공유했다. 새 Gate, 전체 Run A/B, 추가 confidence 실행은 없다.

- 새 ZIP: `.tmp/menu/run-fbgcwee9/p/Iris.zip`
- SHA256: `03aa80beabb1591c6f9dfe2aa60dc73796b7513eb738ef6a88afa6062c119f1f`
- product: `l3p-97a61bb9b62fcf86dfbb010a4c21884777b1acc55d7ea6059a4be2cf4985946e`

최신 compact(S2)와 expanded(Menu)의 source 결속을 기존 제품 경로에서 검증했다. S3 획득/Acquisition 문형을 보존한 실제 ZIP의 static row를 읽었으며 Base.CannedMilk에는 S3가 없다. 이전 run-wi1iy1oy 후보는 보존한다. **implemented_only**, 실제 게임 미관찰. 설치/commit/push 없음.


## 2026-09-13 긴 목록·중복 서술 교정 완료

상태: **implemented_only**. 최종 자동 검사는 아래에 별도 기록한다.

앞서 부분해결로 남긴 지적13의 명시 사례와 공통 생산 경로를 교정하고 실제 KO/EN compact/expanded 전후 문면을 대조했다. 같은 대상·역할의 반복은 합성하고 서로 다른 활용은 독립 문장으로 유지했다. 변경 수는 적용 범위이며 전체 게임 기능의 품질 수락 수가 아니다.

실제 문면 변경: **420아이템 / 837좌표**. 변경 분모는 2,105아이템 / 8,420좌표다.

- 지적13 긴 목록·중복 문장 교정 완료 — 전회 부분해결로 남긴 실제 문면을 공통 activity/function/role 경로에서 마무리했다. 아이템 용도 수 자체를 줄이는 목표로 바꾸지 않았으며 독립 활용을 삭제하지 않았다.
- WaterPot/물 용기 — compact는 조리·붕대 소독의 동일 용기 역할, 물 보관·운반·옮겨 붓기, 담긴 물의 급수·세척·소화·음용으로 구분한다. expanded에서는 각각의 독립 활용과 실제 조건을 유지한다. WaterMug 계열의 오염수 위험을 조리 뒤에서 음용 바로 뒤로 옮겨 잘못된 조건 연결도 제거했다.
- Screwdriver — 전자 부품·무전기 제작과 전자기기 분해·회수 및 조명 건전지 개조를 전자 작업 문장으로 묶었다. 목공·건축물 분해와 부품 탈부착, 창 부착·무기는 별도 문장으로 구분했다. 호환 무기 부착물과 차량 부품을 구별한다.
- Hammer/Shovel — Hammer의 건축·바리케이드 작업에 수박 손질을 끼워 넣던 목록을 분리했다. Shovel은 무덤·밭 조성과 재 청소·토사 담기 작업을 별도 문장으로 나눴다. 수확 제외, 무기 활용 등 실제 용도와 제한을 유지한다.
- Needle — 의류 덧대기·패딩·패치 제거 및 재료 회수 가능성을 같은 활용으로 묶었다. 깊은 상처 봉합의 붕대·유리 제한과 매트리스 제작은 각각 독립적으로 유지하며 문형을 간결하게 했다.
- WhiskeyEmpty/연료 용기 — 주유기 전력과 차량 엔진 정지 조건을 보존하며 급유·연료 이동의 반복 표현을 줄였다. 물 보관·운반, 화염병 재료, 깨진 병 회수는 각각 별도 활용이다.
- RippedSheetsDirty/재료 공통 경로 — 제작 결과마다 반복하던 제작 서술을 하나로 묶고 결과 이름을 보존했다. compact의 장치 제작/기타 제작도 하나의 제작 목적 안에서 설명한다. 상처 감염 위험과 천 세척은 유지한다.
- 연료·불쏘시개 — expanded에서 같은 시설을 두 번 열거하던 문장을 공유 대상과 한쪽 용도에만 해당하는 대상으로 합성했다. 통나무가 든 드럼에는 불쏘시개 용도만 적용해 연료 기능으로 넓히지 않는다.
- Log/TreeBranch/WoodenStick — Log의 목공·건축 및 숯 제작 재료 문형을 정리했다. 마찰 점화의 시설 목록은 compact에서 점화 목적과 방법으로 요약하고 expanded에서 시설별 대상 및 지구력·파손 조건을 보존한다. 골절 고정, 제작 재료, 연료, 묶기와 수박 손질 같은 독립 활용은 유지한다.
- 문면 교정은 완료했다. 이전 사실 근거 보류(가구의 구체 매핑, 잡지 학습 사실 채택, 기존 차량/L4 공급 공백)를 설명이 길다는 이유의 미완료와 섞지 않는다. 이를 새 기능이 확인되었다는 뜻으로 변경하지 않는다.
- 현재 문장 교정 범위 완료. 제품 상태 implemented_only, 실제 게임 미관찰.
- FullType 완성 문장 override, 생성 JSON 수동 수정, 글자 수 강제 절단, 독립 활용 삭제 없음.
- 기존 근거 보류는 별개 사실 공백으로 유지. 이전 기록과 후보 보존. 새 검증 체계/외부 접근/설치/commit/push 없음.

Descriptions SHA256: `f84b25cfc3dbfc947a3cd03e0ad5c66526328f97a5a345717d805ee75683eb78`

Blocks SHA256(불변): `9d68e982cd508b3a4beafc9d1a8892668c9470d4581f7db0d1761e602926e161`

**Base.WaterPot**

Before KO compact: 붕대 소독에 쓸 수 있다. 재료를 담아 요리할 수 있다. 물을 보관, 운반하고 용기나 저장 시설에 부을 수 있다. 담긴 물은 작물 급수, 차량 혈흔 세척, 소화, 음용에 쓸 수 있다 (오염수 음용은 중독 위험).

After KO compact: 조리와 붕대 소독에 쓸 수 있다. 물을 보관, 운반하거나 용기, 저장 시설에 부을 수 있다. 담긴 물은 작물 급수, 차량 혈흔 세척, 소화, 음용에 쓸 수 있다 (오염수 음용은 중독 위험).

After EN compact: It can be used for cooking and disinfecting bandaging. It can store, carry and pour water into containers or storage fixtures; its water serves for watering crops, washing vehicle bloodstains, extinguishing fires, and drinking; drinking tainted water risks poisoning.

**Base.WaterMug**

Before KO compact: 물을 보관, 운반하고 용기나 저장 시설에 부을 수 있다. 담긴 물은 작물 급수, 차량 혈흔 세척, 소화, 음용에 쓸 수 있다. 재료를 더해 요리를 만들 수도 있다 (오염수 음용은 중독 위험).

After KO compact: 물을 보관, 운반하거나 용기, 저장 시설에 부을 수 있다. 담긴 물은 작물 급수, 차량 혈흔 세척, 소화, 음용에 쓸 수 있다 (오염수 음용은 중독 위험). 재료를 더해 요리를 만들 수도 있다.

After EN compact: It can store, carry and pour water into containers or storage fixtures; its water serves for watering crops, washing vehicle bloodstains, extinguishing fires, and drinking; drinking tainted water risks poisoning. Ingredients can also be added to prepare food.

**Base.Screwdriver**

Before KO compact: 전자기기 제작과 분해 및 조명 개조, 목공 및 건축물 분해, 차량과 무기의 부품 장착과 제거에 사용할 수 있다. 제작한 창에 부착하거나 무기로 쓸 수도 있다.

After KO compact: 전자 부품, 무전기 제작과 전자기기 분해에 쓸 수 있다. 조명을 건전지용으로 개조할 수 있다. 목공, 건축물 분해, 차량 부품과 호환 무기 부착물의 탈부착에 쓸 수 있다. 제작한 창에 부착하거나 무기로 쓸 수도 있다.

After EN compact: It can make electronic components and radios or dismantle electronic devices. It can convert lamps to battery power. It can be used for woodworking, structure disassembly; fitting and removing vehicle parts and compatible weapon attachments. It can also be attached to a crafted spear or be used as a weapon.

**Base.Hammer**

Before KO compact: 금속을 단조하는 데 사용할 수 있다. 목공, 건축, 수박 쪼개기, 문과 창문의 판자 바리케이드 설치와 철거에 사용할 수 있다. 무기로도 쓸 수 있다.

After KO compact: 금속을 단조하는 데 사용할 수 있다. 목공, 건축, 문과 창문의 판자 바리케이드 설치와 철거에 쓸 수 있다. 수박을 쪼개는 데 쓸 수 있다. 무기로도 쓸 수 있다.

After EN compact: It can be used for metal forging. It can be used for woodworking and construction; installing or removing plank barricades on doors and windows. It can be used to break a watermelon. It can also be used as a weapon.

**Base.Shovel**

Before KO compact: 무덤 파기와 메우기, 밭 만들기와 정리(수확 제외), 재 청소, 흙이나 모래, 자갈 담기 작업에 쓸 수 있다. 무기로 쓸 수 있다.

After KO compact: 무덤 파기와 메우기, 밭 만들기와 정리(수확 제외)에 쓸 수 있다. 재 청소, 흙이나 모래, 자갈 담기에 쓸 수 있다. 무기로 쓸 수 있다.

After EN compact: It can be used for digging and filling graves and preparing and clearing planting beds without harvesting. It can be used for ash cleanup and bagging dirt, sand or gravel. It can be used as a weapon.

**Base.Needle**

Before KO compact: 의류의 구멍을 덧대거나 패딩을 붙이고, 패치를 뗄 수 있다. 뗀 패치 재료를 돌려받을 수도 있다. 붕대가 감기지 않고 유리가 없는 깊은 상처를 봉합하는 데 사용할 수 있다. 매트리스 제작에 사용할 수 있다.

After KO compact: 의류의 구멍을 덧대거나 패딩을 붙이고 패치를 제거할 수 있다. 제거 시 재료가 회수될 수 있다. 붕대를 감지 않았고 유리가 없는 깊은 상처를 봉합할 수 있다. 매트리스 제작에 사용할 수 있다.

After EN compact: It can mend garment holes, add padding and remove patches, with a chance to recover the removed material. It can stitch a deep wound that is unbandaged and free of glass. It can be used for mattress crafting.

**Base.WhiskeyEmpty**

Before KO compact: 전원이 공급되는 주유기에서 연료를 받거나 엔진이 꺼진 차량과 연료를 주고받을 수 있다. 물을 담아 보관하거나 운반할 수 있다. 화염병 제작에 재료로 사용할 수 있다. 깨뜨려 깨진 병을 얻을 수 있다.

After KO compact: 전원이 있는 주유기에서 급유받거나 시동이 꺼진 차량과 연료를 주고받을 수 있다. 물을 보관하거나 운반할 수 있다. 화염병 제작에 재료로 사용할 수 있다. 깨뜨려 깨진 병을 얻을 수 있다.

After EN compact: It can receive fuel from a powered pump or exchange fuel with a vehicle whose engine is off. It can hold water for storage or carrying. It can be used as a material for making Molotov Cocktail. It can be broken to obtain Smashed Bottle.

**Base.RippedSheetsDirty**

Before KO compact: 상처에 감을 수 있다. 감염된 상태로 쓰면 상처를 감염시킬 수 있다. 물로 씻어 깨끗한 붕대 재료로 바꿀 수 있다. 건축, 장치 제작, 그 밖의 물품 제작에 재료로 쓸 수 있다. 연료나 불쏘시개로 쓸 수 있다.

After KO compact: 상처에 감을 수 있다. 감염된 상태로 쓰면 상처를 감염시킬 수 있다. 물로 씻어 깨끗한 붕대 재료로 바꿀 수 있다. 건축, 장치 등 물품 제작에 재료로 쓸 수 있다. 연료나 불쏘시개로 쓸 수 있다.

After EN compact: It can be wrapped around wounds. If infected, it can infect the wound. It can be washed with water into clean bandaging material. It can be used as material for construction and crafting devices and other items. It can be used as fuel or tinder.

**Base.Log**

Before KO compact: 목공, 건축, 물품 제작에 재료로 쓸 수 있다. 모아서 묶을 수 있다. 빈 금속 드럼에서 숯을 만드는 재료로 사용할 수 있다. 수박 쪼개기에 사용할 수 있다. 연료로 소모할 수 있다.

After KO compact: 목공과 건축, 물품 제작에 재료로 쓸 수 있다. 모아서 묶을 수 있다. 빈 금속 드럼의 숯 제작 재료로 쓸 수 있다. 수박 쪼개기에 사용할 수 있다. 연료로 소모할 수 있다.

After EN compact: It can be used as material for woodworking and construction and crafting. It can be bundled with other logs. It can be made into charcoal in an empty metal drum. It can be used for breaking a watermelon. It can be consumed as fuel.

**Base.TreeBranch**

Before KO compact: 골절 고정에 쓸 수 있다. 목공, 물품 제작에 재료로 쓸 수 있다. 나무 마찰로 모닥불, 비프로판 바비큐, 벽난로, 통나무 드럼의 점화를 시도할 수 있다. 연료로 소모할 수 있다.

After KO compact: 골절 고정에 쓸 수 있다. 목공, 물품 제작에 재료로 쓸 수 있다. 나무 마찰로 불 피우기를 시도할 수 있다. 연료로 소모할 수 있다.

After EN compact: It can be used for splinting fractures. It can be used as material for woodworking and crafting. It can be used to attempt lighting fires by wood friction. It can be consumed as fuel.

**Base.WoodenStick**

Before KO compact: 골절 고정에 쓸 수 있다. 물품 제작에 재료로 쓸 수 있다. 나무 마찰로 모닥불, 비프로판 바비큐, 벽난로, 통나무 드럼의 점화를 시도할 수 있다. 연료로 소모할 수 있다.

After KO compact: 골절 고정에 쓸 수 있다. 물품 제작에 재료로 쓸 수 있다. 나무 마찰로 불 피우기를 시도할 수 있다. 연료로 소모할 수 있다.

After EN compact: It can be used for splinting fractures. It can be used as material for crafting. It can be used to attempt lighting fires by wood friction. It can be consumed as fuel.

전체 Before/After는 기존 `iris_dvf_description_review.html`, 전체 최신 문장은 `iris_dvf_descriptions.html`에 갱신했다. 이전 `.tmp/menu/run-fbgcwee9/p/Iris.zip`은 보존하며 최신 후보라고 재사용하지 않는다.


### 긴 목록·중복 서술 교정 최종 검사와 새 후보

기존 최소 3노드 묶음: **3 passed in 146.16s (0:02:26)**, 정확한 명령 종료 코드 **0**.

```powershell
$env:IRIS_SHARED_MENU_VALIDATION='1'
uv run --project .\Iris\tooling python -I -B -m pytest --noconftest -c .\Iris\tooling\pyproject.toml .\Iris\build\description\v2\tests\test_layer3_description_composition.py::test_layer3_description_composition .\Iris\tooling\tests\test_tooltip_t2_projection.py::test_s2_supply_and_owner_integration .\Iris\build\description\v2\tests\test_layer3_product_integration.py::test_product_contract --basetemp .\.tmp\common -q -s --tb=short
```

로그: `.tmp/prose/complete-tests.log`. Blocks/상류 생산자는 바꾸지 않아 별도 block 검사를 추가하지 않았다. Lua syntax와 런타임/메뉴/package 검사는 공통 product node의 같은 stage/ZIP 결과를 공유했다. 새 Gate, 전체 Run A/B, 추가 confidence 실행은 없다.

- 새 ZIP: `.tmp/menu/run-fffuyq8m/p/Iris.zip`
- SHA256: `01a2a68b4ca4f0bf0858321c85eeda877710dd9071a0e9f2ec7b797f60cb225d`
- product: `l3p-36d19f03c0b17a9cf8c726e23172275b9a66306b65d79c678dec65c42291dcef`

최신 compact(S2)와 expanded(Menu)의 source 결속을 기존 제품 경로에서 검증했다. S3 획득/Acquisition 문형을 보존한 실제 ZIP의 static row를 읽었으며 Base.CannedMilk에는 S3가 없다. 이전 run-fbgcwee9 후보는 보존한다. **implemented_only**, 실제 게임 미관찰. 설치/commit/push 없음.


## 2026-09-13 긴 목록·중복 서술 교정 완료

상태: **implemented_only**. 최종 자동 검사는 아래에 별도 기록한다.

앞서 부분해결로 남긴 지적13의 명시 사례와 공통 생산 경로를 교정하고 실제 KO/EN compact/expanded 전후 문면을 대조했다. 같은 대상·역할의 반복은 합성하고 서로 다른 활용은 독립 문장으로 유지했다. 변경 수는 적용 범위이며 전체 게임 기능의 품질 수락 수가 아니다.

실제 문면 변경: **401아이템 / 818좌표**. 변경 분모는 2,105아이템 / 8,420좌표다.

- 지적13 긴 목록·중복 문장 교정 완료 — 전회 부분해결로 남긴 실제 문면을 공통 activity/function/role 경로에서 마무리했다. 아이템 용도 수 자체를 줄이는 목표로 바꾸지 않았으며 독립 활용을 삭제하지 않았다.
- WaterPot/물 용기 — compact는 조리·붕대 소독의 동일 용기 역할, 물 보관·운반·옮겨 붓기, 담긴 물의 급수·세척·소화·음용으로 구분한다. expanded에서는 각각의 독립 활용과 실제 조건을 유지한다. WaterMug 계열의 오염수 위험을 조리 뒤에서 음용 바로 뒤로 옮겨 잘못된 조건 연결도 제거했다.
- Screwdriver — 전자 부품·무전기 제작과 전자기기 분해·회수 및 조명 건전지 개조를 전자 작업 문장으로 묶었다. 목공·건축물 분해와 부품 탈부착, 창 부착·무기는 별도 문장으로 구분했다. 호환 무기 부착물과 차량 부품을 구별한다.
- Hammer/Shovel — Hammer의 건축·바리케이드 작업에 수박 손질을 끼워 넣던 목록을 분리했다. Shovel은 무덤·밭 조성과 재 청소·토사 담기 작업을 별도 문장으로 나눴다. 수확 제외, 무기 활용 등 실제 용도와 제한을 유지한다.
- Needle — 의류 덧대기·패딩·패치 제거 및 재료 회수 가능성을 같은 활용으로 묶었다. 깊은 상처 봉합의 붕대·유리 제한과 매트리스 제작은 각각 독립적으로 유지하며 문형을 간결하게 했다.
- WhiskeyEmpty/연료 용기 — 주유기 전력과 차량 엔진 정지 조건을 보존하며 급유·연료 이동의 반복 표현을 줄였다. 물 보관·운반, 화염병 재료, 깨진 병 회수는 각각 별도 활용이다.
- RippedSheetsDirty/재료 공통 경로 — 제작 결과마다 반복하던 제작 서술을 하나로 묶고 결과 이름을 보존했다. compact의 장치 제작/기타 제작도 하나의 제작 목적 안에서 설명한다. 상처 감염 위험과 천 세척은 유지한다.
- 연료·불쏘시개 — expanded에서 같은 시설을 두 번 열거하던 문장을 공유 대상과 한쪽 용도에만 해당하는 대상으로 합성했다. 통나무가 든 드럼에는 불쏘시개 용도만 적용해 연료 기능으로 넓히지 않는다.
- Log/TreeBranch/WoodenStick — Log의 목공·건축 및 숯 제작 재료 문형을 정리했다. 마찰 점화의 시설 목록은 compact에서 점화 목적과 방법으로 요약하고 expanded에서 시설별 대상 및 지구력·파손 조건을 보존한다. 골절 고정, 제작 재료, 연료, 묶기와 수박 손질 같은 독립 활용은 유지한다.
- 문면 교정은 완료했다. 이전 사실 근거 보류(가구의 구체 매핑, 잡지 학습 사실 채택, 기존 차량/L4 공급 공백)를 설명이 길다는 이유의 미완료와 섞지 않는다. 이를 새 기능이 확인되었다는 뜻으로 변경하지 않는다.
- 현재 문장 교정 범위 완료. 제품 상태 implemented_only, 실제 게임 미관찰.
- FullType 완성 문장 override, 생성 JSON 수동 수정, 글자 수 강제 절단, 독립 활용 삭제 없음.
- 기존 근거 보류는 별개 사실 공백으로 유지. 이전 기록과 후보 보존. 새 검증 체계/외부 접근/설치/commit/push 없음.

Descriptions SHA256: `e8d6c3a2320f63b9ab75b9aeac3edc0977ebada5c9a698982b3e12b666aa859b`

Blocks SHA256(불변): `9d68e982cd508b3a4beafc9d1a8892668c9470d4581f7db0d1761e602926e161`

**Base.WaterPot**

Before KO compact: 붕대 소독에 쓸 수 있다. 재료를 담아 요리할 수 있다. 물을 보관, 운반하고 용기나 저장 시설에 부을 수 있다. 담긴 물은 작물 급수, 차량 혈흔 세척, 소화, 음용에 쓸 수 있다 (오염수 음용은 중독 위험).

After KO compact: 조리와 붕대 소독에 쓸 수 있다. 물을 보관, 운반하거나 용기, 저장 시설에 부을 수 있다. 담긴 물은 작물 급수, 차량 혈흔 세척, 소화, 음용에 쓸 수 있다 (오염수 음용은 중독 위험).

After EN compact: It can be used for cooking and disinfecting bandaging. It can store, carry and pour water into containers or storage fixtures; its water serves for watering crops, washing vehicle bloodstains, extinguishing fires, and drinking; drinking tainted water risks poisoning.

**Base.WaterMug**

Before KO compact: 물을 보관, 운반하고 용기나 저장 시설에 부을 수 있다. 담긴 물은 작물 급수, 차량 혈흔 세척, 소화, 음용에 쓸 수 있다. 재료를 더해 요리를 만들 수도 있다 (오염수 음용은 중독 위험).

After KO compact: 물을 보관, 운반하거나 용기, 저장 시설에 부을 수 있다. 담긴 물은 작물 급수, 차량 혈흔 세척, 소화, 음용에 쓸 수 있다 (오염수 음용은 중독 위험). 재료를 더해 요리를 만들 수도 있다.

After EN compact: It can store, carry and pour water into containers or storage fixtures; its water serves for watering crops, washing vehicle bloodstains, extinguishing fires, and drinking; drinking tainted water risks poisoning. Ingredients can also be added to prepare food.

**Base.Screwdriver**

Before KO compact: 전자기기 제작과 분해 및 조명 개조, 목공 및 건축물 분해, 차량과 무기의 부품 장착과 제거에 사용할 수 있다. 제작한 창에 부착하거나 무기로 쓸 수도 있다.

After KO compact: 전자 부품, 무전기 제작과 전자기기 분해에 쓸 수 있다. 조명을 건전지용으로 개조할 수 있다. 목공, 건축물 분해, 차량 부품과 호환 무기 부착물의 탈부착에 쓸 수 있다. 제작한 창에 부착하거나 무기로 쓸 수도 있다.

After EN compact: It can make electronic components and radios or dismantle electronic devices. It can convert lamps to battery power. It can be used for woodworking, structure disassembly; fitting and removing vehicle parts and compatible weapon attachments. It can also be attached to a crafted spear or be used as a weapon.

**Base.Hammer**

Before KO compact: 금속을 단조하는 데 사용할 수 있다. 목공, 건축, 수박 쪼개기, 문과 창문의 판자 바리케이드 설치와 철거에 사용할 수 있다. 무기로도 쓸 수 있다.

After KO compact: 금속을 단조하는 데 사용할 수 있다. 목공, 건축, 문과 창문의 판자 바리케이드 설치와 철거에 쓸 수 있다. 수박을 쪼개는 데 쓸 수 있다. 무기로도 쓸 수 있다.

After EN compact: It can be used for metal forging. It can be used for woodworking and construction; installing or removing plank barricades on doors and windows. It can be used to break a watermelon. It can also be used as a weapon.

**Base.Shovel**

Before KO compact: 무덤 파기와 메우기, 밭 만들기와 정리(수확 제외), 재 청소, 흙이나 모래, 자갈 담기 작업에 쓸 수 있다. 무기로 쓸 수 있다.

After KO compact: 무덤 파기와 메우기, 밭 만들기와 정리(수확 제외)에 쓸 수 있다. 재 청소, 흙이나 모래, 자갈 담기에 쓸 수 있다. 무기로 쓸 수 있다.

After EN compact: It can be used for digging and filling graves and preparing and clearing planting beds without harvesting. It can be used for ash cleanup and bagging dirt, sand or gravel. It can be used as a weapon.

**Base.Needle**

Before KO compact: 의류의 구멍을 덧대거나 패딩을 붙이고, 패치를 뗄 수 있다. 뗀 패치 재료를 돌려받을 수도 있다. 붕대가 감기지 않고 유리가 없는 깊은 상처를 봉합하는 데 사용할 수 있다. 매트리스 제작에 사용할 수 있다.

After KO compact: 의류의 구멍을 덧대거나 패딩을 붙이고 패치를 제거할 수 있다. 제거 시 재료가 회수될 수 있다. 붕대를 감지 않았고 유리가 없는 깊은 상처를 봉합할 수 있다. 매트리스 제작에 사용할 수 있다.

After EN compact: It can mend garment holes, add padding and remove patches, with a chance to recover the removed material. It can stitch a deep wound that is unbandaged and free of glass. It can be used for mattress crafting.

**Base.WhiskeyEmpty**

Before KO compact: 전원이 공급되는 주유기에서 연료를 받거나 엔진이 꺼진 차량과 연료를 주고받을 수 있다. 물을 담아 보관하거나 운반할 수 있다. 화염병 제작에 재료로 사용할 수 있다. 깨뜨려 깨진 병을 얻을 수 있다.

After KO compact: 전원이 있는 주유기에서 급유받거나 시동이 꺼진 차량과 연료를 주고받을 수 있다. 물을 담아 보관하거나 운반할 수 있다. 화염병 제작에 재료로 사용할 수 있다. 깨뜨려 깨진 병을 얻을 수 있다.

After EN compact: It can receive fuel from a powered pump or exchange fuel with a vehicle whose engine is off. It can hold water for storage or carrying. It can be used as a material for making Molotov Cocktail. It can be broken to obtain Smashed Bottle.

**Base.RippedSheetsDirty**

Before KO compact: 상처에 감을 수 있다. 감염된 상태로 쓰면 상처를 감염시킬 수 있다. 물로 씻어 깨끗한 붕대 재료로 바꿀 수 있다. 건축, 장치 제작, 그 밖의 물품 제작에 재료로 쓸 수 있다. 연료나 불쏘시개로 쓸 수 있다.

After KO compact: 상처에 감을 수 있다. 감염된 상태로 쓰면 상처를 감염시킬 수 있다. 물로 씻어 깨끗한 붕대 재료로 바꿀 수 있다. 건축, 장치 등 물품 제작에 재료로 쓸 수 있다. 연료나 불쏘시개로 쓸 수 있다.

After EN compact: It can be wrapped around wounds. If infected, it can infect the wound. It can be washed with water into clean bandaging material. It can be used as material for construction and crafting devices and other items. It can be used as fuel or tinder.

**Base.Log**

Before KO compact: 목공, 건축, 물품 제작에 재료로 쓸 수 있다. 모아서 묶을 수 있다. 빈 금속 드럼에서 숯을 만드는 재료로 사용할 수 있다. 수박 쪼개기에 사용할 수 있다. 연료로 소모할 수 있다.

After KO compact: 목공과 건축, 물품 제작에 재료로 쓸 수 있다. 모아서 묶을 수 있다. 빈 금속 드럼의 숯 제작 재료로 쓸 수 있다. 수박 쪼개기에 사용할 수 있다. 연료로 소모할 수 있다.

After EN compact: It can be used as material for woodworking and construction and crafting. It can be bundled with other logs. It can be made into charcoal in an empty metal drum. It can be used for breaking a watermelon. It can be consumed as fuel.

**Base.TreeBranch**

Before KO compact: 골절 고정에 쓸 수 있다. 목공, 물품 제작에 재료로 쓸 수 있다. 나무 마찰로 모닥불, 비프로판 바비큐, 벽난로, 통나무 드럼의 점화를 시도할 수 있다. 연료로 소모할 수 있다.

After KO compact: 골절 고정에 쓸 수 있다. 목공, 물품 제작에 재료로 쓸 수 있다. 나무 마찰로 불 피우기를 시도할 수 있다. 연료로 소모할 수 있다.

After EN compact: It can be used for splinting fractures. It can be used as material for woodworking and crafting. It can be used to attempt lighting fires by wood friction. It can be consumed as fuel.

**Base.WoodenStick**

Before KO compact: 골절 고정에 쓸 수 있다. 물품 제작에 재료로 쓸 수 있다. 나무 마찰로 모닥불, 비프로판 바비큐, 벽난로, 통나무 드럼의 점화를 시도할 수 있다. 연료로 소모할 수 있다.

After KO compact: 골절 고정에 쓸 수 있다. 물품 제작에 재료로 쓸 수 있다. 나무 마찰로 불 피우기를 시도할 수 있다. 연료로 소모할 수 있다.

After EN compact: It can be used for splinting fractures. It can be used as material for crafting. It can be used to attempt lighting fires by wood friction. It can be consumed as fuel.

전체 Before/After는 기존 `iris_dvf_description_review.html`, 전체 최신 문장은 `iris_dvf_descriptions.html`에 갱신했다. 이전 `.tmp/menu/run-fbgcwee9/p/Iris.zip`은 보존하며 최신 후보라고 재사용하지 않는다.


### 긴 목록·중복 서술 교정 최종 검사와 새 후보

기존 최소 3노드 묶음: **3 passed in 146.16s (0:02:26)**, 정확한 명령 종료 코드 **0**.

```powershell
$env:IRIS_SHARED_MENU_VALIDATION='1'
uv run --project .\Iris\tooling python -I -B -m pytest --noconftest -c .\Iris\tooling\pyproject.toml .\Iris\build\description\v2\tests\test_layer3_description_composition.py::test_layer3_description_composition .\Iris\tooling\tests\test_tooltip_t2_projection.py::test_s2_supply_and_owner_integration .\Iris\build\description\v2\tests\test_layer3_product_integration.py::test_product_contract --basetemp .\.tmp\common -q -s --tb=short
```

로그: `.tmp/prose/complete-tests.log`. Blocks/상류 생산자는 바꾸지 않아 별도 block 검사를 추가하지 않았다. Lua syntax와 런타임/메뉴/package 검사는 공통 product node의 같은 stage/ZIP 결과를 공유했다. 새 Gate, 전체 Run A/B, 추가 confidence 실행은 없다.

- 새 ZIP: `.tmp/menu/run-fffuyq8m/p/Iris.zip`
- SHA256: `01a2a68b4ca4f0bf0858321c85eeda877710dd9071a0e9f2ec7b797f60cb225d`
- product: `l3p-36d19f03c0b17a9cf8c726e23172275b9a66306b65d79c678dec65c42291dcef`

최신 compact(S2)와 expanded(Menu)의 source 결속을 기존 제품 경로에서 검증했다. S3 획득/Acquisition 문형을 보존한 실제 ZIP의 static row를 읽었으며 Base.CannedMilk에는 S3가 없다. 이전 run-fbgcwee9 후보는 보존한다. **implemented_only**, 실제 게임 미관찰. 설치/commit/push 없음.
