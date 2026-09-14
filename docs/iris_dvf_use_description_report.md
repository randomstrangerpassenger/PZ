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

## 2026-09-13 감독 지적: 번역체·독립 서술·역할 합성 교정

상태: 공통 생성 규칙 구현과 변경 문구군 원문 대조를 수행했다. 통조림 섭취 방식과 잡지 학습 근거는 보류한다. 전체 아이템의 근거·누락 검토나 전체 문장 품질 완료를 뜻하지 않는다. 자동 검사 결과는 아래 별도 절에 기록한다.

### 검토 방법과 적용 범위

작업 시작의 현재 descriptions를 보존하고 전체 2,105개 항목의 KO Compact/Expanded를 지적 문구와 대조했다. 재생성 후에는 변경된 KO/EN 문장 85개 문구군을 직접 읽었다. 문구군은 같은 원문을 묶은 읽기 단위이며 별도 validator, authority 또는 품질 인증 산출물이 아니다. 각 적용 항목의 원천 근거와 모든 독립 용도 누락을 전수 재감사한 것으로 표현하지 않는다. 아래 수는 두 한국어 표면 중 해당 문구가 있는 **서로 다른 아이템 수**이며 좌표 수가 아니다.

| 지적 문구 또는 문형 | 시작 → 현재 | 판정 |
|---|---:|---|
| 착용하거나 찢어서 | 194 → 0 | 독립 서술어 분리 |
| 찢을 때 가위를 / 가위로 찢어서 | 각각 16 → 0 | 회수 용도에 절단 도구 결속 |
| 음식 준비와 조리에 재료로 | 215 → 0 | 요리 재료 역할로 합성 |
| 낚싯대 낚시의 미끼 | 23 → 0 | 도구와 미끼 역할 직접 서술 |
| 대응 미끼 | 6 → 0 | 동물과 미끼 적합 관계 유지 |
| 호환되는 손상 물품 | 20 → 0 | 수리 재료 역할 유지 |
| 알람 시각과 켜짐 여부 | 16 → 0 | 시간 지정 목적과 정지 행동 |
| 담은 채로 | 69 → 0 | 저장·운반의 같은 내용물 관계 |
| 전자 부품을 회수하는 데 | 18 → 0 | 가공 대상 → 회수 결과 |
| 오염수 음용 괄호 | 24 → 0 | 음용에 위험 문장 결속 |
| 호박 조각 | 6 → 0 | 확인된 단일 레시피 결과 이름 |
| 비프로판 바비큐 | 325 → 0 | 기능별 대상 제한 보존, 자연어 명칭 |
| 엔진 상태 >10 / 회수 후 0 | 1 → 0 | Compact에서 실행 수치 제거 |
| 총기의 탄 걸림이 없어야 | 14 → 0 | 사격 용도만 개요에 공개 |
| 낚싯줄이 끊어지면 파손 | 4 → 0 | 낚싯대 후속 상태 처리 내부 보존 |
| 오른쪽에 홀스터 | 1 → 0 | 착용 위치와 총기 적합 범위 분리 |
| 공기와 상태가 | 9 → 0 | 압력 감소와 마모·이탈 구별 |
| 호환 차량의 머플러를 / 서스펜션을 | 9 / 6 → 각각 0 | 장착되는 부품 역할 |
| 내용을 볼 수 있다 | 1 → 0 | 지도 표시 내용 열람 목적 |
| 과일 음료를 먹을 수 있다 | 1 → 1 | 근거상 보류 |

문구 소멸 자체가 해결 근거는 아니다. 각 수정은 아래 의미 규칙과 현재 문면으로 판단했다.

### 결함별 공통 규칙, 코드, 교차 확인

1. **착용과 회수의 결과 범위 오류 — 해결.** 서로 독립인 착용·회수·로프 재료·연소 활용은 각 서술어를 유지한다. 같은 어미라는 이유로 뒤 활용의 결과를 앞 활용에 공유하지 않는다. `description_composition_ko.py::parallel`에서 어미만을 이용한 생략을 제거했고, `description_composition_uses.py::frames`의 wearable+fabric 분기에서도 같은 원칙을 적용했다. `FabricType`과 admitted wear/fabric/rope/fuel/tinder facts로 적용하며 FullType 문장 예외가 아니다. Apron, Socks_Long, HoodieDOWN_WhiteTINT의 현재 문면과 194개 적용 항목을 대조했다. 대체 착용 형태와 로프 활용도 남았다.

2. **가위 조건의 이탈과 부적절한 가공 동사 — 해결.** 회수 도구는 가공 행위 앞에 붙이고 결과는 그 행위 뒤에 붙인다. Denim/Leather라는 정규화 속성에서 필요한 가위를 판단해 Compact/Expanded 모두 잘라서 회수하도록 합성한다. 손으로 찢는 Cotton 경로는 그대로 구별한다. `description_composition_uses.py::frames`의 wearable/fabric 분기. Dungarees, Gloves_LeatherGloves, Gloves_LeatherGlovesBlack 및 해당 16개를 대조했다. 도구로서 Scissors의 용도와 잘리는 의류의 역할을 섞지 않았다.

3. **번역체·설정 항목 중심 — 해결 범위를 구분.** 요리는 `food_preparation+ingredient` 역할을 요리 재료 용도로 합성한다. 이 규칙을 반죽 활용이 함께 있을 때만 적용하던 조건을 제거해 독립 요리 재료에도 적용했다(`uses.py::frames`, `results.py::_core`, `lexicon.py::CONTEXTS`). Acorn/Allsorts/Apple 등을 비롯한 기존 215개 문구가 모두 교체됐고, 기존 짧은 문형과 함께 새 재료 문장은 272개 표면에 나타난다. 낚시 미끼는 rod의 bait 역할로, 덫은 animal target와 fresh compatible bait 관계로, 수리 재료는 material acceptance 관계로 서술한다(`families.py` 기능별 문형과 trap 분기, `uses.py` repair 분기). Caterpillar/BaitFish, TrapBox/TrapMouse/TrapStick, 총기 수리 재료/테이프류의 같은 관계를 대조했다. 알람은 set+stop 조합에서 시각에 맞춰 울리게 하는 목적과 끄는 행동을 서술한다. 16개 알람 항목에 적용됐으며 확인되지 않은 시간 확인 기능을 추가하지 않았다.

4. **보관의 군더더기와 가공 대상의 도구화 — 해결.** 동일한 내용물을 보관·운반하는 관계는 한 번만 명시한다. 전자기기는 분해되는 대상이므로 도구(드라이버) → 분해 → 결과(전자 부품)의 구조로 쓴다. `uses.py::frames` storage, dismantled+salvage_targets 분기. 69개 가방과 18개 전자 회수 문형을 대조했다. Bag_ALICEpack/Bag_BigHikingBag, 디지털 시계와 Radio 계열에서 저장·재생·학습 효과·부품 회수의 기존 독립 활용을 유지했다.

5. **물의 명사 목록·보고서식 위험 괄호 — 해결, 전체 길이 수락은 주장하지 않음.** container의 저장/운반/받기/붓기와 contents인 물의 급수/세척/소화/음용을 분리한다. 각 function이 있는 경우에만 서술하며 음용 위험은 drinking+poison의 실제 관계에 붙인다. `families.py::water_overview`에서 방향성 receive/pour를 각각 합성하고, `uses.py`의 조리·붕대 소독 역할은 별도로 보존한다. WaterPot/WaterMug/BeerWaterFull 24개 채운 용기의 문구와 빈 용기의 받기 문형을 읽었다. Teacup/MugWhite는 받기만 가진 방향성도 남겼다. 현재 기능 수에 따른 문장 길이는 남으며 길이 gate나 문자 자르기를 도입하지 않았다.

6. **도구 Compact에서 제작 대상과 동작의 적용 범위 혼동 — 해결 범위: 이번 복합 도구 분기.** 기존 tool_purposes가 확인한 같은 목적군을 유지하면서 목적군 사이에는 서술어를 공유하지 않는다. woodworking+structure disassembly, fishing gear+spear crafting 등의 확인된 관계만 묶는다. 음식 손질, 잭 오 랜턴 만들기, 덤불 제거, 부착물, 무기는 각각 독립 문장/서술어다. `uses.py::tool_purposes`, `activity_labels`, tool Compact 분기. HuntingKnife/KitchenKnife/FlintKnife/BreadKnife/Saw/GardenSaw/Scissors/Screwdriver 등의 변경 문구를 읽었다. pumpkin_carving은 모든 recipe relation이 확인된 단일 declared result인 경우 그 결과 이름으로 표현한다. 채택 입력의 Make Halloween Pumpkin → HalloweenPumpkin 및 실제 결과 표시명 '잭 오 랜턴'을 사용했으며 장식 효과를 추측하지 않았다. 전자 부품 제작과 전자기기 분해는 결과 범위를 공유하지 않도록 각각 서술한다. 그 밖의 전체 제작 재료 목록까지 새로 전수 품질 판정한 것은 아니다.

7. **Expanded 연소 대상표 — 해결 범위: 연료/불쏘시개 공통 문형과 동일 명칭의 마찰 점화.** fuel/tinder의 대상 집합을 비교해 둘 다 가능한 대상과 역할이 다른 대상을 분리한다. 같은 대상에서는 두 역할을 묶되 통나무 드럼의 불쏘시개를 다른 곳의 연료와 혼동하지 않는다. `uses.py::FUEL/TINDER` 및 shared/remaining target 합성, `ko.py::alternatives`의 조사 처리. Apron/Log/Charcoal/Coal/HolsterSimple/PercedWood 등의 전체 대상 문형을 읽었다. 317개 표면은 연료와 불쏘시개 대상 분리, 354개 표면은 드럼 불쏘시개 단독 문형이다. 모든 연소 대상을 '불 피우기' 하나로 일반화하지 않았다. 프로판 제외와 드럼의 통나무 조건을 보존했다.

8. **실행 수치·후속 처리의 L3 과노출 — 해결 범위: 지적된 공통 기능.** 사격은 탄약을 장전해 사격하는 용도, 엔진 salvage는 부품을 회수하는 용도로 공개한다. 엔진 손실은 Expanded에서 사용 불가라는 플레이어 결과로 유지하고 수치 산정은 내부에 남겼다. 낚싯대 형태 변경은 독립 활용이 아니어서 internal property로 분류한다. `families.py::fire_ammunition`, `uses.py::INTERNAL_PROPERTIES`/engine_salvage, `lexicon.py::ENGINE_SALVAGE`. 14개 총기, Wrench, 4개 낚싯대에 대조했다. 원래 facts/qualifiers를 삭제하거나 파손 시 다른 이름의 아이템으로 바뀐다는 결과를 추측하지 않았다. 모든 L3 내부 정보 공개 필요성을 재판정한 것은 아니다.

9. **착용 위치·상태값·설치 부품 역할 — 해결 범위: 해당 기능 문형.** 위치는 착용에, 적합성은 들어갈 총기에 결속한다. tire air/condition은 공기압·마모로 구별하고 위험은 타이어 이탈로 서술한다. install_vehicle_*는 도구가 아니라 장착되는 부품이라는 역할에 맞춘다. `families.py` holster 문형, `uses.py` tires, `lexicon.py` brake/muffler/suspension 설치 기능. HolsterSimple, Modern/Normal/Old 타이어 및 브레이크/머플러/서스펜션의 실제 문면을 대조했다. 단독 설치 문형이 각각 9/9/6개 아이템에 적용된다. 연료 탱크 등 다른 설치 기능의 수치·문체까지 전면 교정한 것으로 보지 않는다.

10. **내용물 섭취와 읽기의 근거 — 부분해결/보류.** map의 view_item_map은 지도 내용/영역을 살펴보는 용도이므로 '내용'만 남기지 않는다. reveal 기능이 없으면 알려진 지역 표시 효과를 덧붙이지 않는다(`uses.py` maps). Base.Map과 reveal이 있는 MuldraughMap을 대조했다. CannedFruitBeverage는 현재 채택된 result_consumption이 eat이며 표시명은 과일 음료다. drink로 바꾸지 않았고 이 문면은 보류했다. CookingMag1/2를 포함해 '읽을 수 있다'가 남는 30개 학습 잡지의 L3 학습 fact 부재는 이전 보류대로 유지했다. L4 레시피 학습 근거를 L3로 채택하는 상류 변경 없이 학습 기능을 임의 공개하지 않는다. 짧은 문장만으로 용도 설명을 완료한 것으로 판정하지 않는다.

### 변경 경계와 남은 상태

수정은 offline Python 생성 규칙과 기존 consumer의 현재 descriptions SHA 결속이다. 런타임 의미 재작성기, FullType 완성 문장 override, 생성 JSON 수동 패치가 없다. source traits/function/activity/role/recipe relation이라는 현재 생성 입력의 의미를 기준으로 같은 구조의 현재 항목에 적용한다. 알 수 없는 새 기능이나 결과를 추측하는 범용 규칙을 추가하지 않았다.

Tooltip S1 L2 / S2 Compact / S3 Acquisition / S4 L4와 메뉴 Expanded 및 기존 use_units 소비 구조를 변경하지 않았다. UI·폰트·표시경로를 변경하지 않았고 사용자 인게임 검수를 요구하지 않는다. 문구군 원문 대조의 결과와 제품 검사 결과를 분리한다. 전체 8,420개 문장의 근거·누락·가독성을 전수 판정한 상태는 아니며, 통조림 섭취와 30개 학습 잡지의 근거 보류가 남아 있다. 기존 dirty/untracked, 과거 검사 실패·후보 기록은 보존했다. 설치·worktree·commit·push·외부 접근·새 자동화 없음.


현재 descriptions SHA256: `eac38f8fa16b75f870de552768cdb29d30592362a79060dc43cdb45ff6e046f3`. 작업 시작 SHA256: `e8d6c3a2320f63b9ab75b9aeac3edc0977ebada5c9a698982b3e12b666aa859b`. 감독 평가 당시 f84b25cfc3dbfc947a3cd03e0ad5c66526328f97a5a345717d805ee75683eb78과 구분한다.

실제 변경: 1140아이템 / 2285표면. 전체 2,105아이템 / 8,420표면. 네 locale/surface 각각 present 1,981, absent 124; 신규 실패/부재 없음. blocks는 이번 작업에서 변경하지 않았다.

### 실제 Before / After

다음은 공통 규칙의 효과 예시이며 완료 기준을 대체하지 않는다. 전체 시작 시점과 현재 표면은 `docs/iris_dvf_description_review.html`, 전체 최신 원문은 `docs/iris_dvf_descriptions.html`에서 읽을 수 있다.

**Base.Socks_Long**

Before KO Compact: 착용하거나 찢어서 천 조각을 얻을 수 있다. 시트 로프 제작에 쓸 수도 있다. 연료나 불쏘시개로도 쓸 수 있다.

After KO Compact: 착용할 수 있다. 찢어서 천 조각을 얻을 수 있다. 시트 로프 제작 재료로 쓸 수 있다. 연료나 불쏘시개로도 쓸 수 있다.

**Base.Dungarees**

Before KO Compact: 착용하거나 찢어서 데님 조각을 얻을 수 있다. 연료나 불쏘시개로도 쓸 수 있다. 찢을 때 가위를 쓴다.

After KO Compact: 착용할 수 있다. 가위로 잘라 데님 조각을 얻을 수 있다. 연료나 불쏘시개로도 쓸 수 있다.

**Base.Gloves_LeatherGloves**

Before KO Compact: 착용하거나 찢어서 가죽 조각을 얻을 수 있다. 연료나 불쏘시개로도 쓸 수 있다. 찢을 때 가위를 쓴다.

After KO Compact: 착용할 수 있다. 가위로 잘라 가죽 조각을 얻을 수 있다. 연료나 불쏘시개로도 쓸 수 있다.

**Base.Acorn**

Before KO Compact: 먹거나 요리 재료로 쓸 수 있다. 덫의 미끼로도 쓸 수 있다.

After KO Compact: 먹거나 요리 재료로 쓸 수 있다. 덫의 미끼로도 쓸 수 있다.

**Base.TrapStick**

Before KO Compact: 새 포획을 위해 신선한 대응 미끼와 함께 설치할 수 있다. 미끼, 포획물, 덫을 회수할 수 있다.

After KO Compact: 새를 잡는 덫으로 설치할 수 있다. 잡을 동물에 맞는 신선한 미끼가 필요하다. 미끼와 잡힌 동물, 덫을 회수할 수 있다.

**Base.Bag_ALICEpack**

Before KO Compact: 물건을 보관하고 담은 채로 운반할 수 있다. 등에 메어 착용할 수 있다.

After KO Compact: 물건을 담아 보관하거나 운반할 수 있다. 등에 메어 착용할 수 있다.

**Radio.RadioRed**

Before KO Compact: 전원이 공급되면 기록 매체를 재생하거나 라디오 방송을 청취할 수 있다. 내용에 따라 능력치, 경험치, 제작법 학습 효과를 얻을 수 있다. 드라이버로 분해해 전자 부품을 회수하는 데 쓸 수 있다.

After KO Compact: 전원이 공급되면 기록 매체를 재생하거나 라디오 방송을 청취할 수 있다. 내용에 따라 능력치, 경험치, 제작법 학습 효과를 얻을 수 있다. 드라이버로 분해해 전자 부품을 얻을 수 있다.

**Base.WaterPot**

Before KO Compact: 조리와 붕대 소독에 쓸 수 있다. 물을 보관, 운반하거나 용기, 저장 시설에 부을 수 있다. 담긴 물은 작물 급수, 차량 혈흔 세척, 소화, 음용에 쓸 수 있다 (오염수 음용은 중독 위험).

After KO Compact: 조리와 붕대 소독에 쓸 수 있다. 물을 담아 보관하거나 운반할 수 있다. 다른 용기에서 물을 받거나 다른 용기나 물 저장 시설로 물을 옮길 수 있다. 작물에 물을 줄 수 있다. 차량에 묻은 피를 씻을 수 있다. 불을 끌 수 있다. 담긴 물을 마실 수 있다. 오염된 물을 마시면 중독될 수 있다.

**Base.HuntingKnife**

Before KO Compact: 음식 손질, 목공, 낚시 장비, 창 제작, 호박 조각, 덤불, 덩굴 제거에 쓸 수 있다. 제작한 창에 부착하거나 무기로 쓸 수도 있다.

After KO Compact: 음식 손질에 쓸 수 있다. 목공에 쓸 수 있다. 낚시 장비와 창 제작에 쓸 수 있다. 잭 오 랜턴 만들기에 쓸 수 있다. 덤불과 덩굴 제거에 쓸 수 있다. 제작한 창에 부착하거나 무기로 쓸 수도 있다.

**Base.Screwdriver**

Before KO Compact: 전자 부품, 무전기 제작과 전자기기 분해에 쓸 수 있다. 조명을 건전지용으로 개조할 수 있다. 목공, 건축물 분해, 차량 부품과 호환 무기 부착물의 탈부착에 쓸 수 있다. 제작한 창에 부착하거나 무기로 쓸 수도 있다.

After KO Compact: 전자 부품과 무전기를 만들 수 있다. 전자기기를 분해할 수 있다. 조명을 건전지용으로 개조할 수 있다. 목공과 건축물 분해에 쓸 수 있다. 차량 부품과 호환 무기 부착물의 탈부착에 쓸 수 있다. 제작한 창에 부착하거나 무기로 쓸 수도 있다.

**Base.Wrench**

Before KO Compact: 손상된 차량 엔진을 수리하는 데 사용할 수 있다. 무기로 쓸 수 있다. 차량 엔진에서 예비 부품을 회수하는 데 쓸 수 있다. 이때 상태가 10을 넘는 엔진에서 회수할 수 있으며 회수하면 엔진 상태는 0이 된다.

After KO Compact: 엔진에서 부품을 회수할 수 있다. 손상된 차량 엔진을 수리하는 데 사용할 수 있다. 무기로 쓸 수 있다.

**Base.ModernCarMuffler1**

Before KO Compact: 호환 차량의 머플러를 장착할 수 있다.

After KO Compact: 맞는 차량에 머플러로 장착할 수 있다.

**Base.HolsterSimple**

Before KO Compact: 허리에 착용할 수 있다. 착용하면 오른쪽에 홀스터에 맞는 총기를 넣어 휴대할 수 있다. 불쏘시개로 소모할 수 있다.

After KO Compact: 허리에 착용할 수 있다. 오른쪽에 착용해 홀스터에 맞는 총기를 넣어 휴대할 수 있다. 불쏘시개로 소모할 수 있다.

**Base.Map**

Before KO Compact: 내용을 볼 수 있다. 필기구로 글, 기호를 남기고 지우개로 지울 수 있다.

After KO Compact: 지도에 그려진 지역을 살펴볼 수 있다. 필기구로 글, 기호를 남기고 지우개로 지울 수 있다.

**Base.CannedFruitBeverage**

Before KO Compact: 통조림 따개로 개봉해 과일 음료를 먹을 수 있다. 꺼낸 과일 음료를 요리 재료로도 쓸 수 있다.

After KO Compact: 통조림 따개로 개봉해 과일 음료를 먹을 수 있다. 꺼낸 과일 음료를 요리 재료로도 쓸 수 있다.

**Base.CookingMag1**

Before KO Compact: 읽을 수 있다. 연료나 불쏘시개로 쓸 수 있다.

After KO Compact: 읽을 수 있다. 연료나 불쏘시개로 쓸 수 있다.

Expanded 대표 원문: Base.Gloves_LeatherGloves — 손에 낄 수 있다.
가위로 잘라 가죽 조각 또는 가죽 조각 (오염됨)을 얻을 수 있다.
모닥불이나 프로판을 쓰지 않는 바비큐와 벽난로에서는 연료나 불쏘시개로 쓸 수 있다. 통나무가 든 드럼에서는 불쏘시개로 쓸 수 있다.

Base.ModernTire1 — 호환 차량에 타이어로 장착할 수 있다.
주행 중 공기압이 낮아지고 타이어가 닳을 수 있다. 공기압이 낮거나 많이 닳으면 타이어가 빠질 수 있다.


### 최종 검사 결과와 같은 설명의 제품 후보

최초 최소 관련 묶음은 **exit 1, 1 failed, 2 passed in 152.60s**다. 실패를 전체 PASS로 바꿔 기록하지 않는다.

```powershell
$env:IRIS_SHARED_MENU_VALIDATION='1'
uv run --project .\Iris\tooling python -I -B -m pytest --noconftest -c .\Iris\tooling\pyproject.toml .\Iris\build\description\v2\tests\test_layer3_description_composition.py::test_layer3_description_composition .\Iris\tooling\tests\test_tooltip_t2_projection.py::test_s2_supply_and_owner_integration .\Iris\build\description\v2\tests\test_layer3_product_integration.py::test_product_contract --basetemp .\.tmp\natural-final -q -s --tb=short
```

로그: `.tmp/prose/natural-tests.log`. 실패는 `test_layer3_description_composition.py:344`가 낚싯대 Expanded의 첫 줄에 '낚싯줄', '미끼를 잃는다'를 반드시 공개하도록 요구한 오래된 기대값 때문이다. 새 공개 깊이 규칙에 맞춰 낚시·미끼 용도와 2개 활용 유지, 파손 fact의 internal_uses 및 preserved_fact_refs 보존을 확인하도록 교정했다. 다른 두 노드(S2/owner, product)는 이 최초 묶음에서 성공했다.

수정 후 실패한 설명 조합 노드만 다시 실행했다. **exit 0, 1 passed in 9.91s**.

```powershell
uv run --project .\Iris\tooling python -I -B -m pytest --noconftest -c .\Iris\tooling\pyproject.toml .\Iris\build\description\v2\tests\test_layer3_description_composition.py::test_layer3_description_composition --basetemp .\.tmp\natural-description-retry -q -s --tb=short
```

로그: `.tmp/prose/natural-description-retry.log`. 재검사에서 descriptions의 bytes는 동일한 `eac38f8fa16b75f870de552768cdb29d30592362a79060dc43cdb45ff6e046f3`다. 따라서 이번 관련 검사 결과는 '최초 1실패/2성공 + 실패한 1노드 수정 후 성공'이며 하나의 3 passed 실행으로 합쳐 쓰지 않는다.

마지막 전체 재생성 명령도 exit 0이었다.

```powershell
uv run --project .\Iris\tooling python -I -B -m iris_tooling.domains.layer3.description_composition_results
```

문면 읽기와 HTML 갱신은 `uv run python .tmp/prose/natural_read.py ...`, `uv run python .tmp/prose/natural_scope.py`, `uv run python .tmp/prose/natural_publish.py`로 수행했고 exit 0이었다. 이 읽기·갱신은 품질 자동 판정이나 새 validator가 아니다. 검색 중 PowerShell의 경로 내 glob을 rg에 전달한 일부 탐색 명령은 exit 1이었고, 디렉터리+`-g` 방식으로 경로를 고쳐 읽었다. 이것은 검증 PASS 근거가 아니다.

기존 product node가 생성·검사한 후보:

- ZIP: `.tmp/menu/run-g8z8r456/p/Iris.zip`
- ZIP SHA256: `f063e994ed6dd878de155e13cd1f6ed89c18f8739c3fb451f66d1be70767ba0a`
- product: `l3p-dcd16727e02bcd6b79eb955b90ac68905ab82c14ad732e8ce03d1488771bd78e`
- 해당 node의 패키지·런타임·메뉴·Lua syntax 자식 실행은 같은 후보에서 exit 0이었다. 실제 폰트가 아닌 stub을 쓴 메뉴 검사이므로 인게임 가독성 수락을 뜻하지 않는다. 독립 Lua/Java/JS 소스 변경이 없어 별도 언어 검사 전체를 실행하지 않았다.
- product 내부 Lua 명령은 `powershell -NoProfile -ExecutionPolicy Bypass -Command "& .\tools\check_lua_syntax.ps1 -Roots @(\"Iris/media/lua\", \".tmp/menu/run-g8z8r456/s/Iris/media/lua\")"`이었다. 이 자식 실행을 다른 명령의 실행 기록으로 대체하지 않는다.

### 갱신 파일과 최종 범위 정정

- `Iris/tooling/src/iris_tooling/domains/layer3/description_composition_uses.py`
- `Iris/tooling/src/iris_tooling/domains/layer3/description_composition_families.py`
- `Iris/tooling/src/iris_tooling/domains/layer3/description_composition_ko.py`
- `Iris/tooling/src/iris_tooling/domains/layer3/description_composition_lexicon.py`
- `Iris/tooling/src/iris_tooling/domains/layer3/description_composition_results.py`
- `Iris/tooling/src/iris_tooling/domains/layer3/tooltip_s2_supply.py` 및 `product_projection.py`: 현재 descriptions SHA 결속만 변경.
- `Iris/build/description/v2/tests/test_layer3_description_composition.py`: 독립 술어, 한국어 조사, 물 받기, 엔진 공개 깊이, 낚싯대 내부 근거 보존 기대값.
- `Iris/build/description/composition/descriptions.json`: 공통 producer 재생성 결과.
- `docs/iris_dvf_descriptions.html`, `docs/iris_dvf_description_review.html`: 최신 원문 및 이번 시작 시점 Before/After.
- `docs/iris_dvf_use_description_report.md`, `docs/iris_dvf_description_structure_report.md`: 이번 기록 추가. 기존 review JSON은 과거 검토 기록으로 보존했으며 이번 HTML과 기록을 최신 읽기 대상으로 삼는다.

사용자 최종 정정을 적용한다. Generic Normalization Adapter 첨부의 사실 공급/레이어 소비 경계는 장기 배경이며 이번 설계·구현·검수 요구가 아니다. 현재 DVF 결함의 공통 원인을 교정하는 데 필요한 변경만 수행했다. 미래 모드 입력의 지원·검증이나 확장 계약을 성립시켰다는 주장을 하지 않는다. adapter 인터페이스, 스키마, 확장 지점, Generic Core/Dialect/Local Compatibility 계층, 캐시는 도입하지 않았다.

최종 판정: **현재 지적된 공통 문형의 구현·적용 대조는 수행, #10 통조림 섭취와 학습 잡지는 근거상 보류. 전체 DVF 문장 품질 완료는 주장하지 않는다.** 사용자의 추가 판단이 필요한 승인 장애는 없다. 보류 해소에는 실제 섭취/학습 근거의 상류 채택 작업이 필요하며 이번 문면 교정으로 임의 해결하지 않았다.


최신 HTML의 8,420개 `data-original` 원문을 현재 descriptions와 읽어 대조했으며 차이는 0이었다. 기존 HTML 머리말은 과거 f84b25… SHA가 남아 있어 현재 eac38f… 값으로 함께 갱신했다. 이 일치 확인은 문장 품질 판정이 아니다.


## 2026-09-13 감독 재지적: 생존자에게 필요한 용도와 공개 깊이

**판정: 부분 해결.** 실행 조건·내부 수치·후속 처리의 공통 공개 경로를 교정하고 실제 결과를 재생성했다. 그러나 모든 Compact가 목적 관계를 충분히 설명한다고 수락하지 않는다. 지도 표시 상태 문형, 일부 도구의 명사 중심 목적 연결, 현재 근거가 빠진 잡지 학습과 통조림 음료 섭취 방식은 아래에 남겨 둔다. 문자열 0건, 변경 개수, 테스트 통과는 문장 품질 완료의 대체 기준이 아니다.

이번 범위는 현재 출력 품질이다. 앞선 절의 미래 모드/정규화 재사용 설명을 이번 변경의 보장이나 완료 근거로 삼지 않는다. 미래 어댑터·확장 설계·새 스키마·정규화 프레임워크를 구현하지 않았다.

### 공통 원인과 수정

기존 경로는 알려진 qualifier를 공개 세부사항으로 취급했다. 주된 문형에서 조건을 줄여도 일반 fallback이 이를 다시 붙였고, Expanded에는 실행 조건과 내부 수치까지 설명해야 한다는 선택이 남아 있었다. 이제 `lexicon.public_qualifier`, `uses.prepare`, `results._links` 및 공통 fallback은 용도 판단에 필요한 결과/위험만 공개 qualifier로 허용한다. 나머지 실행 근거는 삭제하지 않고 원래 적용 범위와 함께 내부에 보존한다. Expanded도 이 공개 깊이 규칙을 따른다.

또한 행동과 상태를 같은 qualifier 문장으로 압축했던 치료 경로에서, 조건을 숨기자 상태 flag만 따로 공개되는 회귀가 드러났다. 기존에 허용된 정확한 적용 범위의 행동/상태 조합은 `families.condition_frames`가 실제 행동 문장으로 표현한다. 새로운 인과관계나 효과를 추론하지 않는다. 원래 분리된 범위를 같은 관계로 합치지 않는 기존 검사를 유지했다.

`uses.disposition`은 도구의 마모, 설치 부품의 내부 수치, 파손, 코드 효과 dispatch, 바닥 유리 정리 시 손 상태를 독립 용도로 공개하지 않는다. 실제 물품의 도구/재료/대상 역할은 기존 근거로 선택한다. 예를 들어 깨진 유리의 배치·회수와 손 상처는 유리가 제공하는 청소 용도가 아니다. 착용+휴대와 물 보관+이동처럼 같은 용도에 속하는 행동은 해당 의미 frame에서 합친다.

### 지적별 현재 결과

| 지적 | 현재 변경과 판정 |
|---|---|
| 붕대 유무, 유리 없는 봉합 상처 | 소독·봉합·박힌 이물 제거의 실행 상태를 양쪽 표면에서 제외했다. 실제 상처 치료 용도와 봉합 보조 도구는 유지했다. |
| 주유기 전원, 차량 엔진 정지, 꺼진 발전기 | 연료 받기·차량과 연료 교환·발전기 급유 용도로 바꾸고 해당 실행 상태는 공개하지 않는다. 충전기의 영어 전원 조건도 제거했다. |
| 다른 헤드폰, 탄약 여유 공간, 장치 함께 소지 | 연결 대상의 호환성은 유지하고 기존 장착물 부재·남는 공간·함께 소지 요구는 제거했다. 원격 기능의 실제 대상과 조종 범위는 남겼다. |
| 빈 자연 지형, 미파종 밭, 이미 잠긴 구조물, 커튼 없는 창 | 밭 만들기/정리, 씨앗 심기, 구조물 잠금, 커튼 부착 목적을 남긴다. 기존 상태 체크는 제외했다. 잠금 대상이 문을 제외한다는 실제 대상 범위는 유지한다. |
| 생선 0.6, 탱크 상태 70, 철판 손실, 수확 아님 | 무게·상태 수치와 손실·부정적인 작업 설명을 제외했다. 손질 도구로 생선살을 얻기, 차량 탱크의 연료 보관/공급, 재료의 용접 참여, 밭 정리 용도는 유지한다. |
| 마찰 점화, 도구 마모, 어망 파손/회수, 부러진 창, 병조림 보존, 엔진 불능, 차량 첫 경보 | 체력·마모·파손·보존 수치·후속 상태/경보 처리는 내부에 남긴다. 불 피우기, 미끼 물고기 잡기, 창 부착물 회수, 병조림, 엔진 부품 회수, 맞는 차량 시동을 공개한다. 어망 회수는 독립 용도로 보지 않았다. |
| 흡연 | stress/unhappiness/food-sickness 이름 대신 흡연가의 기분 완화와 비흡연가가 탈이 날 수 있다는 용도/위험으로 표현했다. 성냥/라이터라는 실제 도구와 작물 치료용 분무액 재료 역할은 유지했다. |
| 물통 Compact | 보관·운반·받기·붓기를 물 보관/이동으로 묶고 물의 사용처를 한 문장 안에서 연결했다. Kettle의 Compact에만 있던 받기 문장을 제거해 두 표면 모두 보관/운반 목적이 된다. WaterPot는 현재 Compact 114자/4문장, Expanded 181자/8문장이다. 이 수치는 관측값이며 합격 기준이 아니다. |
| 도구 Compact | 음식 손질, 목공/장비 제작, 부품 탈부착, 실제 무기/창 부착 역할로 묶고 Compact에서 제작 결과명 목록을 줄였다. Screwdriver의 전자기기 제작/분해와 조명 개조를 연결했다. **부분 해결:** Saw의 '목공과 장비 제작 및 건축물 해체' 등 명사 연결과 일반 '쓸 수 있다' fallback이 남는다. 문장 수만 줄인 것을 완성으로 취급하지 않는다. |
| 가위·봉합 보조·씨앗·항생제·작물 치료·메모 | 가위는 의류를 잘라 조각을 회수하는 동작으로, 봉합 보조는 시간값 없이 봉합/실밥 제거 보조로, 씨앗 봉지는 씨앗을 밭에 심는 용도로 표현한다. 씨앗 수량도 제외했다. 항생제는 상처 감염 치료, 분무액은 작물에 뿌려 흰가루병 감소, 필기구는 메모 작성으로 표현했다. 한국어 산탄총 총신 단축은 도구와 대상 모두 동사 '총신을 줄일 수 있다'를 쓴다. |
| 연료·불쏘시개 시설표, 통나무 드럼, Charcoal | 실제 공통 역할을 기준으로 '모닥불 등의 연료나 불쏘시개', 드럼만 있는 경우 '금속 드럼의 불쏘시개'로 표현했다. 등은 원천에서 실제 허용한 대표 대상이며 모든 연소 시설 지원을 주장하지 않는다. Charcoal은 모닥불/화로 연료다. 휘발유도 실행 상태를 가진 시설표를 제거했다. 시신 태우기는 일반 점화와 다른 대상 목적이라 별도 유지했다. |
| 천 조각의 청결/오염 변형 | 공개 회수 결과는 천/데님/가죽 조각 범주로 표현한다. 데님·가죽의 가위 도구를 유지한다. 착용과 회수의 독립 서술어, 이전 수정의 짧은 낚싯대, Wrench Compact 수치 제외를 유지했다. |
| Base.AlarmClock와 깨진 유리 | 정확히 Base.AlarmClock의 현재 사실은 설치·회수·타이머 설정이며 알람/소음 발생 용도 근거를 제공하지 않는다. AlarmClock2에서 복사하지 않았다. 깨진 유리 네 종은 정리되는 대상이다. 이 5종은 공개 용도 근거 부족으로 absent가 되며 '실제로 쓸모없다'는 판정은 아니다. |
| 유사 장치/폭발물 | 타이머/설치/회수를 내부 관리로 분류하고 현재 허용된 투척 공격·작동 부품 개조·원격 작동은 유지했다. 장치 기능 28종의 실제 KO/EN 표면을 공통 문구별로 대조했다. 센서나 이름만으로 소음/폭발 효과를 추가하지 않았다. |
| Holster/Belt, Battery | 착용 위치와 슬롯 휴대를 한 용도로 합쳤다. 세 종의 착용 위치와 실제 휴대 대상을 읽었다. Battery는 호환 조명/휴대 기기에 전력을 공급하는 부품 역할을 공개한다. |
| 지도·기록 매체 | 지도/메모 19종 및 기록 매체/기기 19종의 실제 표면을 문구별로 대조했다. 매체의 전원 요구와 일반 코드 처리 효과 나열을 제외하고 시청·청취·재생·근거 있는 분해 회수를 유지했다. **부분 해결:** 지역 지도에는 '알려진 지역으로 표시'라는 상태 표현이 아직 남는다. 매체별 실제 학습/기분 효과는 현재 generic code-outcome 사실만으로 확정하지 않는다. |
| CookingMag, CannedFruitBeverage | **보류.** 30개 학습 잡지의 현재 L3 학습 fact 공백을 고치지 않았다. 과일 음료의 현재 result_consumption은 eat이며 '과일 음료를 먹을 수 있다'가 여전히 출력된다. drink로 추측 변경하지 않았다. 현재 문장 품질 미해결 항목으로 유지한다. |

### 읽은 범위와 결과물

변경된 KO/EN segment 문구군 160개와 지적 대상 Compact/Expanded 원문을 읽고, 치료 9종·착용 휴대 3종·지도/메모 19종·장치 28종·매체 19종은 해당 기능을 가진 현재 아이템 전체를 찾아 중복 문장을 접어 대조했다. 조건/수치 문자열 검색은 빠진 공개 경로를 찾는 보조 작업이었다. 전체 8,420개 표면에 대해 원천 근거와 누락을 모두 판정한 전수 품질 수락은 아니다.

첫 교정 산출물 대비 1,090개 아이템 / 3,734개 표면이 변경됐다. 총 2,105개 아이템 / 8,420개 표면, 각 locale/surface present 1,976, absent 129, failed 0이다. 새 absent는 Base.AlarmClock와 Base.brokenglass_1_0/1/2/3 다섯 종이다.

최신 전체 원문과 use_units는 `iris_dvf_descriptions.html`, 이번 시작/현재 대조는 `iris_dvf_description_review.html`에 반영했다. `review/uses/items.json`과 `review/structure/items.json`은 과거 평가 기록으로 남겼고 이번 결과로 덮어쓰지 않았다. 두 HTML의 현재 SHA를 갱신했다.

UI·폰트·Tooltip S1/S3/S4·메뉴 표시 경로를 바꾸지 않았다. 런타임에서 문장을 다시 작성하지 않는다. 기존 dirty/untracked와 이전 실패 기록을 보존했으며 새 설치·worktree·commit·push·외부 조사·자동화가 없다.

현재 descriptions SHA256: `e836b12bca783988cb25dfac5a80bc53c9787c64360092f6095c3fdf09116bce`. 이번 시작 SHA256: `eac38f8fa16b75f870de552768cdb29d30592362a79060dc43cdb45ff6e046f3`.

### 현재 실제 문면 예시

**Base.WaterPot — KO Compact**

조리와 붕대 소독에 쓸 수 있다. 물을 담아 보관하거나 옮길 수 있다. 담긴 물은 마시거나 작물에 줄 수 있고, 차량에 묻은 피를 씻거나 불을 끄는 데도 쓸 수 있다. 오염된 물을 마시면 중독될 수 있다.

**Base.Kettle — KO Compact**

물을 담아 보관하거나 운반할 수 있다.

**Base.HuntingKnife — KO Compact**

음식 손질이나 목공과 장비 제작에 쓸 수 있다. 덤불과 덩굴을 제거할 수 있다. 제작한 창에 부착하거나 무기로 쓸 수도 있다.

**Base.Screwdriver — KO Compact**

전자기기를 만들거나 분해하고, 조명을 건전지용으로 개조할 수 있다. 목공 및 건축물 해체에 쓸 수 있다. 차량 부품과 호환 무기 부착물을 장착하거나 제거할 수 있다. 제작한 창에 부착하거나 무기로 쓸 수도 있다.

**Base.Scissors — KO Compact**

데님이나 가죽 의류를 잘라 조각을 회수할 수 있다. 머리와 수염을 손질할 수 있다. 제작한 창에 부착해 쓸 수 있다. 무기로 쓸 수 있다.

**Base.SutureNeedleHolder — KO Compact**

상처에 박힌 유리를 제거할 때 쓸 수 있다. 상처에 박힌 총알을 제거할 때 쓸 수 있다. 상처를 봉합하거나 실밥을 제거할 때 보조 도구로 쓸 수 있다.

**Base.HolsterSimple — KO Compact**

허리 오른쪽에 착용해 홀스터에 맞는 총기를 넣어 휴대할 수 있다. 금속 드럼의 불쏘시개로 쓸 수 있다.

**Base.PercedWood — KO Compact**

나무 마찰로 불 피우기를 시도할 수 있다. 모닥불 등의 연료로 쓸 수 있다.

**Base.CannedFruitBeverage — KO Compact**

통조림 따개로 개봉해 과일 음료를 먹을 수 있다. 꺼낸 과일 음료를 요리 재료로도 쓸 수 있다.


### 최종 최소 관련 검사와 최초 실패

이번 교정의 최초 최소 묶음은 다음 명령이다. PowerShell에서 `IRIS_SHARED_MENU_VALIDATION=1`을 설정했다.

```powershell
uv run --project .\Iris\tooling python -I -B -m pytest --noconftest -c .\Iris\tooling\pyproject.toml .\Iris\build\description\v2\tests\test_layer3_description_composition.py::test_layer3_description_composition .\Iris\tooling\tests\test_tooltip_t2_projection.py::test_s2_supply_and_owner_integration .\Iris\build\description\v2\tests\test_layer3_product_integration.py::test_product_contract --basetemp .\.tmp\survivor-final-tests -q -s --tb=short
```

**최초 결과: exit 1, 2 failed / 1 passed, 73.81초.** `.tmp/prose/survivor-tests.log`를 보존했다. 설명 검사는 내부로 이동한 `fact:load`/`fact:path`를 공개 segment의 refs에 요구했고, 제품 검사는 기존 present 3962 / absent 248을 고정했다. 이 두 기대값을 현재 공개 정책과 5종의 근거 부재에 맞게 고쳤다. qualifier/fact 보존, 적용 범위 분리, 소비 경로 검사 자체는 제거하지 않았다. 최초 묶음의 전체 성공을 주장하지 않는다.

실패했던 두 노드만 다시 실행했다. 최초 묶음에서 생성한 S2 후보 `.tmp/tooltip/run-texgmbdr/s/.tmp/package/Iris.zip`을 `IRIS_MENU_TOOLTIP_CANDIDATE`로 지정했다. 통과한 S2 노드와 전체 비교 파이프라인을 반복 실행하지 않았다.

```powershell
uv run --project .\Iris\tooling python -I -B -m pytest --noconftest -c .\Iris\tooling\pyproject.toml .\Iris\build\description\v2\tests\test_layer3_description_composition.py::test_layer3_description_composition .\Iris\build\description\v2\tests\test_layer3_product_integration.py::test_product_contract --basetemp .\.tmp\survivor-retry-tests -q -s --tb=short
```

**재실행 결과: exit 0, 2 passed, 71.32초.** `.tmp/prose/survivor-retry-tests.log`. 전체 설명의 원천 fact/scopes/relations 보존과 분리, 두 생성 결과의 동일성, 실제 Lua 모델 소비, 패키지 무결성/거부 경로, ZIP 소비와 복구 검사를 통과했다. 테스트의 폰트는 stub이며 실제 게임 폰트·미관 검수를 의미하지 않는다. Python 수정과 현재 제품 경로에 관련된 기존 검사만 실행했으며 별도 Java/JS 검사나 새 검증 체계를 만들지 않았다.

생성 제품: `.tmp/menu/run-d1zfcssw/p/Iris.zip`.

- product: `l3p-2b2cea9b95f684732baaf2f3601c5a7822830fa3c9b1d21cfb734519bf38d20d`
- ZIP SHA256: `4bb7fc2d42fd00f1bfc0b0bbb53428fc51bea30114f3709dbac3a500ded239d4`
- descriptions SHA256: `e836b12bca783988cb25dfac5a80bc53c9787c64360092f6095c3fdf09116bce`

앞선 교정의 최초 1 failed / 2 passed와 그 재시도 기록은 해당 역사 절에 그대로 남긴다. 현재 결과를 과거 PASS나 이전 후보 SHA와 혼동하지 않는다.

## 2026-09-13 잔여 후속: 학습 근거 채택과 용도 합성

감독이 요청한 잔여 6개 항목을 현재 로컬 원본 `scripts/`와 `lua/`까지 조사했다. 1–5는 아래 범위에서 교정했고, 6은 독립 용도 근거가 부족하여 보류한다. absent 자체를 해결 성과로 세지 않는다.

| 요청 | 현재 결과 | 근거와 한계 |
|---|---|---|
| 복합 도구 Compact | 교정 | Saw 등의 음식 손질·목재 가공·제작을 동사 문장으로 합성하고 건축물 해체·산탄총 총신 단축을 보존했다. 드라이버의 전자기기 제작·분해·조명 개조를 묶고 망치의 금속·목재 가공을 묶었다. 독립 용도와 Expanded의 실제 대상은 유지했다. |
| 지도 내부 상태 표현 | 교정 | 14종의 지역 지도에 세계 지도에서 해당 지역을 확인한다는 목적을 표현했다. `ISMap`의 revealKnownArea와 `ISMapDefinitions`의 영역 공개가 근거다. 방문 완료나 안전한 지역이라는 뜻을 추가하지 않았다. |
| 기록 매체 학습·기분 | 범주 수준에서 교정 | 등록 데이터 332개(CD 69, Retail VHS 135, Home VHS 128)의 실제 codes와 활성 처리기를 연결했다. CD는 지루함 완화, VHS는 내용에 따른 지루함 완화·기술 및 제작법 학습을 표현했다. 일부 VHS의 스트레스, Retail VHS의 공포 증가도 보존했다. 특정 녹화물 식별자가 없는 정적 FullType에 모든 내용의 동일 효과를 보장하지 않는다. |
| 학습 잡지 30종 | 상류 채택 교정 | TeachedRecipes 선언, 활성 읽기 호출, 학습 UI/툴팁, 제작법 분야 및 활성 지식 소비자를 연결하는 공통 규칙으로 30종 모두 학습 목적을 공급했다. 같은 이름의 제작법이 여러 개면 모든 일치 선언의 분야가 같을 때만 채택한다. CookingMag뿐 아니라 FishingMag1와 ElectronicsMag3의 중복 제작법 선언도 처리한다. |
| 과일 음료를 먹는 표현 | 교정 | 선언된 개봉 결과 `Base.CannedFruitBeverageOpen`의 `FoodType=Juice`를 관계에 연결하여 `섭취/consume`로 표현했다. 원본 Type=Food, EatType=can이며 기존 eat_food 사실은 그대로다. 표시명으로 drink 동작을 새로 만들지 않았다. |
| AlarmClock·깨진 유리 4종 | 조사 후 근거 보류 | 아래의 구체적인 근거 공백이 남았다. 설명 부재를 독립 용도 문제의 해결로 표시하지 않는다. |

`Base.AlarmClock`는 `scripts/newitems.txt`의 Type=Weapon, PhysicsObject=NoiseGenerator, NoiseRange·ExplosionTimer·배치/재사용 필드 및 옛 Trap 툴팁이 있으나 `OBSOLETE=true`다. 현재 활성 아이템 `Base.AlarmClock2`의 알람 기능을 옮기지 않았다. 기존 함정 배치 경로만으로 폐기된 정확한 FullType의 현재 생성·사용과 소음 실행을 확정할 수 없다. 보류 해제에는 현재 버전에서 이 폐기 선언을 가진 FullType이 실제 사용되는 근거와 NoiseGenerator/IsoTrap의 해당 소음 실행 근거가 필요하다. 제공된 로컬 자료에는 그 구현이 없다.

`Base.brokenglass_1_0`부터 `_1_3`까지는 `scripts/newMoveables.txt`에 Moveable 및 BrokenGlass 태그가 있다. `ISMoveableSpriteProps.lua`의 줍기 중 손 상처와 IsoBrokenGlass 배치, `recipecode.lua`의 BrokenGlass 태그 수집은 확인했다. 현재 scripts 제작법과 recipes_index_full에는 이 태그 그룹 또는 해당 4종을 실제 용도에 소비하는 제작법이 없다. 태그·획득·배치만으로 유용한 독립 효과를 만들지 않았다. 보류 해제에는 해당 4종을 실제 재료·대상으로 소비하는 동작/제작법이나 배치 후 유용한 효과를 입증하는 구현이 필요하다.

학습 교정은 기존 r6 역사 파일을 수정하지 않고 현재 composition 보정 단계에 최소 규칙을 추가했다. 새 사실은 학습 30개와 기록 매체 10개, 총 40개다. 기존 보정 20개를 포함하여 총 60개이며 사실 참조와 원본 해시를 유지한다. 주석 처리된 addKnownRecipes 루프를 실행 코드로 간주하지 않았다. TeachedRecipes, 활성 ReadLiterature 호출과 학습 UI의 선언된 능력이 근거이며, Lua에 없는 네이티브 상태 변경의 구현까지 검증했다고 주장하지 않는다.

직전 후보 `e836b12bca783988cb25dfac5a80bc53c9787c64360092f6095c3fdf09116bce` 대비 66개 아이템, 231개 표면이 바뀌었다. 학습 잡지 30종, 기록 매체 3종, 지역 지도 14종, 도구 17종, 과일 음료 봉인/개봉 2종이다. 해당 아이템의 KO/EN Compact/Expanded 전체 264개 표면을 동일 전문 기준 74개 문구군으로 읽고 변경 segment 68개 문구군도 대조했다. 2,105개 아이템·8,420개 표면 중 각 언어/표면은 present 1,976, absent 129, failed 0으로 유지된다. 이번 단계의 새 absent는 없다. 불필요한 실행 조건을 양쪽 깊이에서 제외하는 기존 교정과 실제 도구·대상·내용물 및 독립 용도를 보존했다.

현재 HTML 두 개를 재생성했다. `docs/review/uses/items.json`과 `docs/review/structure/items.json`은 역사 기록으로 유지했다. 전체 8,420개 표면의 모든 사실·가독성, 실제 게임 폰트/화면, 향후 어댑터를 새로 검증하거나 보장한 결과는 아니다.

검사는 관련 기존 노드만 실행했다. 최초 잔여 후보는 다음 명령으로 exit 0, **4 passed in 152.66s**였다(`.tmp/prose/remainder-tests.log`).

```powershell
$env:IRIS_SHARED_MENU_VALIDATION='1'
Remove-Item Env:IRIS_MENU_TOOLTIP_CANDIDATE -ErrorAction SilentlyContinue
uv run --project .\Iris\tooling python -I -B -m pytest --noconftest -c .\Iris\tooling\pyproject.toml .\Iris\build\description\v2\tests\test_layer3_composition.py::test_layer3_composition_contract .\Iris\build\description\v2\tests\test_layer3_description_composition.py::test_layer3_description_composition .\Iris\tooling\tests\test_tooltip_t2_projection.py::test_s2_supply_and_owner_integration .\Iris\build\description\v2\tests\test_layer3_product_integration.py::test_product_contract --basetemp .\.tmp\remainder-final-tests -q -s --tb=short
```

이후 전체 문장을 읽으며 확인한 드라이버 영어 반복과 망치 재료 가공 문장을 조정했다. 변경하지 않은 상류 composition 검사를 반복하지 않고, 변경된 설명 및 S2/현재 제품 경로의 아래 3개 기존 노드만 실행했다(`.tmp/prose/remainder-prose-tests.log`).

```powershell
$env:IRIS_SHARED_MENU_VALIDATION='1'
Remove-Item Env:IRIS_MENU_TOOLTIP_CANDIDATE -ErrorAction SilentlyContinue
uv run --project .\Iris\tooling python -I -B -m pytest --noconftest -c .\Iris\tooling\pyproject.toml .\Iris\build\description\v2\tests\test_layer3_description_composition.py::test_layer3_description_composition .\Iris\tooling\tests\test_tooltip_t2_projection.py::test_s2_supply_and_owner_integration .\Iris\build\description\v2\tests\test_layer3_product_integration.py::test_product_contract --basetemp .\.tmp\remainder-prose-final-tests -q -s --tb=short
```

검사에는 사실/조건 참조 보존, 상류 보정 및 제작법 중복 선언 회귀, 설명 생성, S2 공급, 현재 제품의 동일 입력 두 번 빌드 바이트 일치, 실제 Lua 소비자와 패키지/ZIP 소비 및 포인터 거부·복구가 포함된다. 제품 검사는 Lua 구문 검사 명령을 실행하고 exit 0을 확인한다. 실제 게임 폰트 측정은 없으며 소비자 폰트는 stub이다. 과거 단계의 최초 실패와 제한된 재시도 기록은 앞 절과 로그에 그대로 남겼다. 이번 두 묶음 검사 사이 문장 점검에서 발견한 중복 목재 문장은 최종 생성 전에 수정했다.

최종 문장 후보 검사는 exit 0, **3 passed in 147.09s**다. 이번 잔여 단계의 두 검사 묶음에서 실패한 테스트는 없다.

- descriptions SHA256: `17cc67517b12cafba4fe451659619cbde29d7ea274d31f705461e2f6e361c6e1`
- blocks SHA256: `14a3118fe8d51cc042ce8d7fc300da621d8d65911d4e2873ee97cd6916a4382a`
- product: `l3p-54ed4d30f413537ae4adf47e5e1c690865c1efd10fdf00075ec9712242a6c428`
- ZIP: `.tmp/menu/run-_sf_7xgu/p/Iris.zip`
- ZIP SHA256: `975cf7bf20219d2e617a1c5302c463df6081fa87222b6a1d45bee7af1d44108e`

두 HTML은 위 최종 descriptions에 결합되어 있다. `tooltip_s2_supply`와 `product_projection`의 현재 입력 해시만 갱신했으며 역사적 ACCEPTED 해시는 유지했다. 기존 dirty/untracked를 보존했고 worktree·설치·커밋·푸시·자동화·외부 조사는 수행하지 않았다.


## 2026-09-14 전체 문면 평가 후속: 정보 깊이와 공통 생성 규칙

이번 감독 지시는 현재 DVF의 문장 품질을 개선하고, Compact와 Expanded를 의도적인 정보 깊이로 구분하는 작업이다. 아래 7개 결함 유형에 공통 생성 규칙을 적용했다. 개별 아이템의 완성 문장 덮어쓰기, primary_use 축소, L4 레시피 목록 복사, 미래 정규화 어댑터용 구현·스키마·인터페이스·검사는 추가하지 않았다.

| 결함 유형 | 바꾼 공통 규칙 | 실제 적용 확인 |
|---|---|---|
| 작업명·명사구 문장화 | `description_composition_ko.role`에서 활동과 도구/재료/용기 역할을 동작 문형으로 생성한다. 제작·혼합·가공·단조·용접을 `만들 때 재료로`, `섞는 용기로`, `가공하는 데`처럼 표현한다. 복수 역할 문구를 단순 작업명 나열로 합치지 않는다. 직접 합성되는 점화·지도 지우기·회수·시트 로프·용접 프레임도 수정했다. | 음식 손질 도구, 석고 용기 2종, 마찰 점화 3종, 지우개, 전자 재료, 금속 재료, 시트 로프 재료 179종 등의 양쪽 출력에 적용했다. |
| Compact 과밀과 깊이 | 바늘은 의류 수선/덧댄 천 제거의 개요를 제공하며, Expanded가 구멍·패딩·천 회수 가능성을 설명한다. 덫은 Compact에 포획 대상 개요, Expanded에 맞는 신선한 미끼와 미끼·덫 회수를 둔다. 잡힌 동물을 꺼낸다는 당연한 후속 결과는 공개 설명에서 제외한다. | Needle 1종, 덫 6종. 의료·의류 복합 재료의 요약은 이 두 목적에만 적용하며 제작 분야를 덮지 않는다. 기술서 60종의 최대 경험치 배율은 Expanded에 유지하고 Compact는 배율 향상 목적을 설명한다. |
| Compact 추상화 | 도구의 제작 참여는 사냥·낚시 장비, 폭발 장치, 장식용 호박 가공 등의 실제 활용 범주로 합성한다. 재료는 목공/건축, 사냥·낚시 장비, 야영 장비, 도구, 부목 및 실제 장치 범주를 구분한다. 최종 `_compact_materials`가 이를 다시 `제작 재료/다른 물품`으로 덮던 동작을 제거했다. | Saw/GardenSaw, 칼류, Wire, Plank, Twine, 천 재료 등 전체 적용 출력 확인. 장치 범주는 기존 실제 결과 관계로 화염·연막·소음·폭발을 구분하며 소음 발생기를 폭발 장치로 설명하지 않는다. |
| 같은 목적 반복 | 유리/총알 제거 동작과 각각의 제거 결과를 하나의 의료 프레임으로 묶는다. 별도로 남는 `상태를 해제한다` 결과 문장도 함께 흡수한다. | Tweezers와 SutureNeedleHolder 2종, 양쪽 깊이. 봉합 보조의 독립 용도는 별도로 유지했다. |
| Expanded 제작 목록 | 복합 도구의 개별 낚시 장비/창/잭 오 랜턴/파이프 폭탄/덫 이름 나열을 활용 범주로 합성한다. 원본 참조는 유지한다. | 도구가 쓰이는 분야를 설명하고, 건축물 해체 후 재료 회수·전자기기 분해 후 부품 회수·실제 내용물/필요한 도구는 남겼다. 한 가지 변환 결과가 아이템 활용을 설명하는 경우 결과명 자체를 금지하지 않았다. |
| 내부 상태·실행 조건 | 비료의 살아 있음/파종/성장 시점/정확한 누적 횟수를 공개하지 않고 성장 촉진 및 과다 사용 시 부패 위험을 표현한다. 우산 손 슬롯, 화상 세척 필요 플래그, 삽의 자연 지면 적합성, 통나무 드럼 빈 상태, 살충제의 중복 대상 조건을 제거한다. | 비료 2종, 열린 우산 4종, 화상 세척 재료 6종, 지면 작업 도구, Log, 작물 살충제. 양쪽 깊이에서 지정된 불필요한 문구가 남지 않음을 실제 출력과 대조했다. 위험과 필요한 도구를 일괄 삭제하지 않았다. |
| 장착·연결 절차에 머묾 | 기존 채택된 차량 배터리 장착 사실과 활성 전력 소비 구현을 연결해 전력 공급 목적 3개를 상류 보정에 추가한다. 패널 Compact는 호환 차량에서의 실제 문/덮개/유리 역할과 잠금·개폐 가능성으로 표현하고, Expanded가 장착 후 조작을 설명한다. 헤드폰 연결 관계는 호환 기기 소리 청취 목적을 표현한다. | CarBattery 3종, 문/덮개 15종과 개폐 유리 6종, Earbuds/Headphones 2종. 호환성은 유지하며 후드·트렁크를 통로라고 설명하지 않는다. |

상류 추가는 `recovery_sources.supplement_player_uses`의 `installed_battery_power_purpose` 공통 규칙이다. 기존 `install_vehicle_battery`가 채택된 항목만 대상으로 삼으며 해당 원본 provenance와 `lua/server/Vehicles/Vehicles.lua`의 배터리 소비 구현을 결합한다. `Vehicles.Update.Battery`에는 시동 시 배터리 잔량 감소가 있고 전기 장치 갱신에는 배터리 충전량 검사와 소비가 있다. 시동 성공을 보장하거나 임의의 모든 장치에 호환된다는 뜻을 추가하지 않았다. 현재 보정 사실은 기존 60개에 전력 공급 3개를 더한 63개다. 이전 r6 채택 파일은 유지했다.

이어폰의 소리 청취 목적은 기존 헤드폰 연결 역할 및 `ISRadioAction.lua`/`RWMVolume.lua`의 오디오 기기 헤드폰 입출력에 따른 역할 해석이다. 소리를 완전히 차단한다거나 좀비에게 들리지 않는다는 효과는 이 자료로 확인하지 않았고 설명에도 추가하지 않았다. 이전의 폐기된 `Base.AlarmClock`와 깨진 유리 4종의 독립 용도 근거 보류는 유지한다. 이번 7개 지적 유형의 교정에 새로 남긴 근거 보류 항목은 없다.

직전 최종 후보 `17cc67517b12cafba4fe451659619cbde29d7ea274d31f705461e2f6e361c6e1` 대비 393개 아이템의 871개 표면이 변경되었다. 공통 문형의 시트 로프 재료 179종도 포함되므로 예시 아이템만 수정한 집계가 아니다. 적용 아이템의 KO/EN Compact/Expanded 전체 1,572개 표면을 실제 전문으로 읽었다. 같은 전문은 중복 읽기만 묶었고 최종 전문은 471개 문구군이다. 중간 후보 447개 전문군을 읽은 뒤 최종 차이 65개 전문군을 다시 읽었다. 변경 segment는 194개 문구군이다. 집계·재생성·검사 결과를 문장 품질 판정으로 대신하지 않았다.

실제 문면 검수에서 복합 도구의 어색한 한국어 활용, 제거 결과의 내부 상태 노출, 차량 후드에 잘못 붙는 통로 표현, 소음/화염/연막 장치의 과도한 폭발 범주화, 재료 Compact를 다시 추상화하는 최종 요약, 새 요약의 문장 마침표 누락을 발견해 최종 후보 전에 수정했다. 해당 규칙의 전체 출력과 후속 차이를 다시 읽었다. 단순 용도는 두 깊이가 같아도 유지했고, 물 냄비의 차량 혈흔 세척·몸/바닥 소화와 전자기기 분해의 부품 회수 등 추가 가치가 있는 구체성은 줄이지 않았다. 많은 독립 용도가 있는 재료는 여전히 상대적으로 길며, 이를 숨겨서 Compact를 짧게 만들지는 않았다.

전체 2,105개 아이템·8,420개 표면의 각 언어/깊이는 present 1,976, absent 129, failed 0이다. 이번 새 absent는 없다. 전체 DVF의 모든 사실·문체가 무결하다는 선언이나 실제 게임 폰트/레이아웃 검증은 아니다. 두 HTML은 현재 출력과 전후 대조로 갱신했고 역사적 review JSON은 수정하지 않았다.


대표 전후 문면은 아래와 같다. 표 안의 전문은 실제 생성 파일에서 읽었으며 사람이 별도 작성한 정답 문장이 아니다. 모든 변경 항목의 양쪽 언어/깊이는 갱신된 HTML 전후 대조에서 볼 수 있다.

| 아이템 | 깊이 | 이전 | 현재 |
|---|---|---|---|
| Base.Needle | compact | 의류의 구멍을 덧대거나 패딩을 붙이고 패치를 제거할 수 있다. 제거 시 재료가 회수될 수 있다. 깊은 상처를 봉합하는 데 쓸 수 있다. 매트리스 제작에 사용할 수 있다. | 의류를 수선하거나 덧댄 천을 떼는 데 쓸 수 있다. 깊은 상처를 봉합하는 데 쓸 수 있다. 매트리스를 만드는 데 쓸 수 있다. |
| Base.Needle | expanded | 의류의 구멍을 덧대거나 패딩을 붙이고 패치를 제거할 수 있다. 제거 시 재료가 회수될 수 있다. 깊은 상처를 봉합하는 데 쓸 수 있다. 매트리스 제작에 사용할 수 있다. | 의류의 구멍을 덧대거나 패딩을 붙이고, 덧댄 천을 떼어낼 수 있다. 떼어낸 천은 회수할 수도 있다. 깊은 상처를 봉합하는 데 쓸 수 있다. 매트리스를 만드는 데 쓸 수 있다. |
| Base.TrapBox | compact | 토끼, 다람쥐를 잡는 덫으로 설치할 수 있다. 잡을 동물에 맞는 신선한 미끼가 필요하다. 미끼와 잡힌 동물, 덫을 회수할 수 있다. | 토끼, 다람쥐를 잡는 덫으로 쓸 수 있다. |
| Base.TrapBox | expanded | 토끼, 다람쥐를 잡는 덫으로 설치할 수 있다. 잡을 동물에 맞는 신선한 미끼가 필요하다. 미끼와 잡힌 동물, 덫을 회수할 수 있다. | 토끼, 다람쥐를 잡는 덫으로 쓸 수 있다. 잡을 동물에 맞는 신선한 미끼가 필요하다. 넣어 둔 미끼와 설치한 덫은 회수할 수 있다. |
| Base.Saw | compact | 음식을 손질하고 목재를 가공할 수 있으며, 물품을 만드는 데도 쓸 수 있다. 건축물을 해체하거나 산탄총의 총신을 줄일 수 있다. | 사냥 장비를 만들거나 폭발 장치를 만드는 데 쓸 수 있다. 음식을 손질하고 목재를 가공할 수 있다. 건축물을 해체하거나 산탄총의 총신을 줄일 수 있다. |
| Base.Saw | expanded | 음식 나누기에 사용할 수 있다. 목공 작업에 사용할 수 있다. 분해 가능한 건축물을 해체하고 재료를 회수할 수 있다. 파이프 폭탄 제작에 사용할 수 있다. 산탄총의 총신을 줄일 수 있다. 덫 제작에 사용할 수 있다. | 사냥 장비를 만들거나 폭발 장치를 만드는 데 쓸 수 있다. 음식을 나누는 데 쓸 수 있다. 목재를 가공하는 데 쓸 수 있다. 분해 가능한 건축물을 해체하고 재료를 회수할 수 있다. 산탄총의 총신을 줄일 수 있다. |
| Base.HuntingKnife | compact | 음식을 손질하고 목재를 가공할 수 있으며, 물품을 만드는 데도 쓸 수 있다. 덤불과 덩굴을 제거할 수 있다. 제작한 창에 부착하거나 무기로 쓸 수도 있다. | 사냥과 낚시 장비를 만들거나 호박을 장식용으로 깎는 데 쓸 수 있다. 음식을 손질하고 목재를 가공할 수 있다. 덤불과 덩굴을 제거할 수 있다. 제작한 창에 부착하거나 무기로 쓸 수도 있다. |
| Base.HuntingKnife | expanded | 음식을 손질하는 데 쓸 수 있다. 목공 작업에 사용할 수 있다. 낚시 장비 제작에 사용할 수 있다. 창 제작에 사용할 수 있다. 잭 오 랜턴 만들기에 사용할 수 있다. 덤불이나 벽 덩굴을 제거할 수 있다. 제작한 창에 부착해 쓸 수 있다. 무기로 쓸 수 있다. | 사냥과 낚시 장비를 만들거나 호박을 장식용으로 깎는 데 쓸 수 있다. 음식을 손질하는 데 쓸 수 있다. 목재를 가공하는 데 쓸 수 있다. 덤불이나 벽 덩굴을 제거할 수 있다. 제작한 창에 부착해 쓸 수 있다. 무기로 쓸 수 있다. |
| Base.Wire | compact | 용접을 포함한 건축, 물품 제작에 재료로 쓸 수 있다. | 용접을 포함한 건축 작업을 할 때 재료로 쓸 수 있다. 사냥과 낚시 장비를 만들 때 재료로 쓸 수 있다. |
| Base.Wire | expanded | 용접을 포함한 건축, 덫, 낚시 장비 제작에 재료로 쓸 수 있다. | 용접을 포함한 건축 작업을 할 때 재료로 쓸 수 있다. 사냥과 낚시 장비를 만들 때 재료로 쓸 수 있다. |
| Base.Tweezers | compact | 상처에 박힌 유리를 제거할 때 쓸 수 있다. 상처에 박힌 총알을 제거할 때 쓸 수 있다. | 상처에 박힌 유리나 총알을 제거하는 데 쓸 수 있다. |
| Base.Tweezers | expanded | 상처에 박힌 유리를 제거할 때 쓸 수 있다. 상처에 박힌 총알을 제거할 때 쓸 수 있다. | 상처에 박힌 유리나 총알을 제거하는 데 쓸 수 있다. |
| Base.BucketEmpty | compact | 물을 담아 보관하거나 운반할 수 있다. 석고 혼합에 용기로 사용할 수 있다. | 물을 담아 보관하거나 운반할 수 있다. 석고를 섞는 용기로 쓸 수 있다. |
| Base.BucketEmpty | expanded | 물을 담아 보관하거나 운반할 수 있다. 석고 혼합에 용기로 사용할 수 있다. | 물을 담아 보관하거나 운반할 수 있다. 석고를 섞는 용기로 쓸 수 있다. |
| Base.Fertilizer | compact | 살아 있는 파종 작물에 시비해 다음 성장 시점을 앞당길 수 있다. 이미 네 번 이상 시비한 작물에 더 주면 부패한다. | 작물의 성장을 촉진할 수 있다. 비료를 너무 많이 주면 작물이 썩을 수 있다. |
| Base.Fertilizer | expanded | 살아 있는 파종 작물에 시비해 다음 성장 시점을 앞당길 수 있다. 이미 네 번 이상 시비한 작물에 더 주면 부패한다. | 작물의 성장을 촉진할 수 있다. 비료를 너무 많이 주면 작물이 썩을 수 있다. |
| Base.CarBattery1 | compact | 호환 차량에 배터리를 장착할 수 있다. | 호환 차량의 시동과 전기 장치에 전력을 공급할 수 있다. |
| Base.CarBattery1 | expanded | 호환 차량에 배터리를 장착할 수 있다. | 호환 차량의 시동과 전기 장치에 전력을 공급할 수 있다. |
| Base.Earbuds | compact | 헤드폰을 연결할 수 있는 휴대 기기에 꽂아 쓸 수 있다. 스크류드라이버로 분해해 전기 회로 부속을 얻을 수 있다. | 호환되는 휴대 기기의 소리를 듣는 데 쓸 수 있다. 스크류드라이버로 분해해 전기 회로 부속을 얻을 수 있다. |
| Base.Earbuds | expanded | 헤드폰을 연결할 수 있는 휴대 기기에 꽂아 쓸 수 있다. 스크류드라이버로 분해해 전기 회로 부속을 얻을 수 있다. | 호환되는 휴대 기기의 소리를 듣는 데 쓸 수 있다. 스크류드라이버로 분해해 전기 회로 부속을 얻을 수 있다. |
| Base.BookCooking1 | compact | 자신의 기술 수준에 맞을 때 읽으면 요리 경험치 배율을 높일 수 있다. 완독 시 최대 3배다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다. | 자신의 기술 수준에 맞을 때 읽으면 요리 경험치 배율을 높일 수 있다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다. |
| Base.BookCooking1 | expanded | 자신의 기술 수준에 맞을 때 읽으면 요리 경험치 배율을 높일 수 있다. 완독 시 최대 3배다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다. | 자신의 기술 수준에 맞을 때 읽으면 요리 경험치 배율을 높일 수 있다. 완독 시 최대 3배다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다. |

검사 기록은 실패를 포함해 다음과 같이 보존한다.

1. 최초 관련 4개 기존 노드: exit 1, **1 failed / 3 passed in 157.40s** (`.tmp/prose/depth-tests.log`). 상류 composition, S2 공급, 현재 제품 통합은 통과했고 설명 검사의 기존 `수박 쪼개기` 문자열 기대값이 실패했다. 현재 출력은 요청된 동작 문형 `수박을 쪼개는 데 쓸 수 있다`였으므로 기대값을 갱신했다. 검사 실행 중 소스는 변경하지 않았다.
2. 전체 문면에서 추가로 발견한 최종 Compact 요약·한국어 문형을 수정하고, 변경된 설명/S2/제품의 기존 3개 노드만 재실행했다. exit 0, **3 passed in 131.18s** (`.tmp/prose/depth-retry-tests.log`). 상류는 첫 실행 뒤 바꾸지 않아 반복하지 않았다.

첫 검사 명령:

```powershell
$env:IRIS_SHARED_MENU_VALIDATION='1'
Remove-Item Env:IRIS_MENU_TOOLTIP_CANDIDATE -ErrorAction SilentlyContinue
uv run --project .\Iris\tooling python -I -B -m pytest --noconftest -c .\Iris\tooling\pyproject.toml .\Iris\build\description\v2\tests\test_layer3_composition.py::test_layer3_composition_contract .\Iris\build\description\v2\tests\test_layer3_description_composition.py::test_layer3_description_composition .\Iris\tooling\tests\test_tooltip_t2_projection.py::test_s2_supply_and_owner_integration .\Iris\build\description\v2\tests\test_layer3_product_integration.py::test_product_contract --basetemp .\.tmp\depth-final-tests -q -s --tb=short
```

최종 후보 검사 명령:

```powershell
$env:IRIS_SHARED_MENU_VALIDATION='1'
Remove-Item Env:IRIS_MENU_TOOLTIP_CANDIDATE -ErrorAction SilentlyContinue
uv run --project .\Iris\tooling python -I -B -m pytest --noconftest -c .\Iris\tooling\pyproject.toml .\Iris\build\description\v2\tests\test_layer3_description_composition.py::test_layer3_description_composition .\Iris\tooling\tests\test_tooltip_t2_projection.py::test_s2_supply_and_owner_integration .\Iris\build\description\v2\tests\test_layer3_product_integration.py::test_product_contract --basetemp .\.tmp\depth-retry-tests -q -s --tb=short
```

로그에는 위 명령의 출력을 PowerShell 리디렉션으로 보존했다. 기존 검사에서 참조·조건·순서·상세 연결 보존, 실제 의미 대조, 두 번 빌드 바이트 일치, S2 공급, Lua 구문 검사, 실제 Lua 소비자의 패키지/ZIP 읽기와 거부·복구를 확인했다. 제품 검사 안의 Lua 구문 검사도 exit 0이며 실제 게임 폰트는 stub이다. 검사 성공은 문면 검수와 별도 증거다.

최종 산출물:

- descriptions SHA256: `b774e1d73adb037e0b041f37a6a0b2c4d600dd267eb39624b1eaaaef14f20c6f`
- blocks SHA256: `1eea2326e7c7ca60cf870ead66c245df99f910d1e62adaea0dbcc78e4b0fe5fe`
- product: `l3p-19e5cbba05edd7ea6c4db8bac6b362067e9fdc4fc3e1f94b133ba850fde4ed5b`
- ZIP: `.tmp/menu/run-bb5tsqf5/p/Iris.zip`
- ZIP SHA256: `95b183b72ead47bb87c40fddbf92fe9a83000bb8fd2c8a0656baa9573f8b5752`

현재 consumer binding만 갱신하고 역사적 ACCEPTED 해시는 유지했다. 기존 dirty/untracked와 이전 실패 기록을 보존했다. 설치·worktree·커밋·푸시·자동화·외부 조사·새 검수 프레임워크는 수행하지 않았다.



## 2026-09-14 전체 문면 재교정: 역할·목적·포괄 관계

이 절은 직전 `b774e1d73adb037e0b041f37a6a0b2c4d600dd267eb39624b1eaaaef14f20c6f` 후보에 대한 후속 교정이다. 이전 지적을 초기화하지 않고 원인 선택 경로와 최종 조립 경로를 함께 수정했다. 같은 작업에서 재생성 → 전체 한국어 전문 검수 → 잔존 및 새 부작용 재교정을 반복했다. 아래의 해결 판정은 이번 지적 유형에 대한 문면 판정이며, 테스트 수치나 특정 문자열 소멸을 품질 판정으로 삼지 않았다.

| 유형 | 원인 경로와 공통 규칙 | 전체 근거·검토 범위 | 판정 |
|---|---|---|---|
| 범주 접속과 긴 내포 명사구 | `activity_labels`와 `frames` 양쪽에서 장치 이름 목록을 기준으로 삼던 분기를 제거했다. 제작 결과의 선언 속성으로 화염·폭발·연막·소음·원격 조종기 범주를 고르고, 목공/건축·사냥/낚시처럼 같은 활용 분야 안에서 역할을 공유한다. 의료·야영·도구·장치는 독립 문장으로 구성한다. | 제작 재료 관련 근거 71개 아이템을 검토. 결과 범주는 `recovery_relations.named`의 해당 선언 observation에 묶인다. | 해결 |
| 상위 용도와 개별 결과 중복 | 목공과 건축을 동일 재료 역할로 묶고, 실제 결과가 `DisplayCategory=Tool`인 단조 관계만 도구 제작 범주에 포함한다. 이미 포함된 톱 결과를 다시 출력하지 않는다. 골절 고정과 부목 제작도 같은 목적에 결합한다. 나머지 역할·조건·독립 용도는 보존한다. | 재료 근거 71개 범위, 직접 골절 고정과 부목 제작을 함께 가진 4개. 최종 Compact 의료 요약 경로도 수정. | 해결 |
| 불명확한 장치 개조·수리·매체·요리 | 장치 개조는 실제 Add 레시피의 대상/두 번째 부품/후속 조립 재료 관계로 구분한다. 결과의 SensorRange/CanBeRemote/ExplosionTimer로 감지·원격·시간 지연을 구분하며 센서의 준비 지연을 별도 타이머 기능으로 중복 계산하지 않는다. 수리는 fixing Require의 실제 대상에서 무기·총기·차량 부품 범주를 얻는다. 매체 기기는 AcceptMediaType과 RWMMedia의 CD/VHS 분기를 연결한다. 요리 도구는 도구 역할과 반죽 용도를 유지한다. | 장치 개조 10개, 수리 재료 20개, 매체 조작 기기 4개, 요리/반죽 도구 전체. 원격 연결 경로는 조종기와 작동 대상의 주어를 따로 구성했다. | 표현 가능한 근거 범위 해결; 아래 설치·독서 효과 근거 보류 별도 |
| 내부 조건과 자기 관리 | 독서 시작 감정 상한을 `disposition`에서 internal로 분류한다. 골절의 머리/몸통 제외, 작물 파종 상태, 당연한 조종 범위, 설치 로프 제거를 효용 문장으로 재등장시키지 않는다. 로프 회수·재사용은 새로 추정하지 않는다. | 독서 보정 12개, 로프 2개 및 골절·급수의 공통 함수 범위. | 문면 해결; 실제 독서 감정 감소는 근거 보류 |
| 재료·도구·가공 대상 역할 | 토치는 용접 도구 사실과 레시피 소모를 함께 보되 소모만으로 재료라고 표현하지 않는다. 순수 용접 재료는 Compact에서도 재료 역할을 유지한다. 산탄총 대상은 총신을 짧게 개조하는 문장, 톱은 총신을 줄이는 도구 문장으로 구분한다. | 용접 참여 전체, 총신 단축 관계 3개. 기존 바리케이드·차량 해체 등의 독립 도구 용도 보존. | 해결 |
| 차량 및 설치 목적 | 모든 `install_vehicle_*` 관계를 재검토한다. 배터리·저장·좌석·문/잠금/창문 등의 독립 소비 근거가 있으면 장착과 목적을 함께 구성한다. Vehicles.Update.Headlight의 장착 전구/배터리 검사와 setLightActive 소비를 추가 채택한다. 독립 목적 근거가 없는 설치는 internal로 보류한다. | 직접 차량 장착 관계 76개. 차량 정비 분류의 차량 용도 관계를 포함한 100개를 검토했고 기존 보관 부품의 설명도 확인. 전조등 목적 신규 사실 1개. | 입증된 목적 해결; 설치만 확인된 목적은 근거 보류 |
| 형태·조사·관계 표현 | 한국어 조사 함수는 괄호 보충 표기 밖 명사를 기준으로 받침을 계산한다. 공통 `(수제작)` 보충 표기는 `수제` 수식어로 재배치한다. 연료의 받기/넣기를 각각 방향 있는 문장으로 구성한다. 차량 유리는 자리와 장착 후 여닫기를 분리한다. 탄창 충전과 총기 삽입은 연속 관계로 묶는다. 장전 속도는 완결 문장으로, 착용 변경은 선언된 메뉴 동작별 후드·방향·위치로 구성한다. | 착용 변경 79개, 연료 이동 13개, 탄창 삽입 6개, 장전 속도 2개 및 관련 명명 결과 전체. | 해결 |

가구·설치의 보류는 설명 개선으로 집계하지 않는다. 배치/이동 관계 140개 중 이전부터 다른 근거 또는 보류가 있는 범위를 제외한 135개가 이번에 새로 absent가 되었다. 독서 보정 제거도 새로운 감정 감소 효용을 발견했다는 뜻이 아니다.

`ISReadABook.update`는 음수 BoredomChange/UnhappyChange/StressChange 선언을 가진 비기술서를 읽는 동안 수치가 시작값보다 높아지면 시작값으로 되돌리는 보정이다. 원본에는 음수 선언 값과 장시간 하루 설정에 따른 효과 보정을 설명하는 주석이 실제로 있다. 그러나 `perform`의 `ReadLiterature(self.item)` 네이티브 적용 구현은 이 채택 소스 범위에서 확인되지 않는다. 따라서 상한 보정을 실제 감정 감소로 바꿔 쓰지 않았고, 감정 감소 효용·양·시점은 보류했다. 읽기, 실제 채택된 기술/제작법 학습, 연료/제작 등 독립 근거는 남겼다.

차량 타이어·브레이크·서스펜션·머플러·고정 유리 등에서 장착과 탈거, 공기 관리, 마모 콜백은 확인된다. `setTireRemoved`, 제동 중 마모, 속도/조향에 따른 마모만으로 접지력·제동력·충격 흡수·소음 감소·보호 효과를 만들지 않았다. 전조등은 이와 달리 실제 활성화 소비가 있어 조명 목적을 추가했다. 교체형 실내 조명은 `ISLightActions.performAddLightBulb`의 네이티브 `addLightBulb` 호출까지 확인되므로 설치 사실을 실제 조명 효과의 대체 설명으로 사용하지 않았다. 일반 가구도 배치 명령만으로 가구별 효용을 추정하지 않았다. 이전 AlarmClock 및 깨진 유리의 근거 보류는 유지한다.

전체 2,105개 × 한국어 두 깊이 4,210개 표면을 546개 전문군으로 펼쳐 읽었다. 동일 전문의 중복 읽기만 줄였고 모든 군의 적용 ID 및 C/E를 확인했다. 이후 부작용 재교정에서 99개 아이템의 한국어 C/E 전체를 42개 전문군으로 다시 읽고, 마지막 후드·원격 작동 대상 문면도 재확인했다. 최종 한국어 전문군은 542개다. 적용 범위의 실제 전문 검토에서 재료가 도구처럼 보이던 토치, 개별 차량 수리 대상의 과도한 나열, 의료 상위 용도와 부목 중복, 착용 위치 중복, 후드 용도가 다른 용도 뒤로 밀리는 문제를 재교정했다. 비료 과다 위험/성장 촉진, 우산 및 의료 내부 조건 제외, 핀셋 제거 대상 결합, 바늘·덫·기술서의 정보 깊이, 통조림 도구·내용물, 의류의 독립 용도는 전체 대조와 관련 기존 검사에서 보존을 확인했다.

최종 변경은 447개 아이템, 1,632개 KO/EN 표면이다(KO Compact 417, KO Expanded 420, EN Compact 407, EN Expanded 388). 2,105개 전체에서 각 언어/깊이마다 present 1,794, absent 311, failed 0이다. 신규 absent 182개는 근거 보류이며 완성된 효용 설명으로 계산하지 않는다. HTML 두 파일은 현재 전체 출력 및 직전 후보와의 실제 전후 대조로 갱신했다. 역사적 review JSON과 r6 원본을 고치지 않았다.

다음은 생성 JSON에서 그대로 옮긴 실제 한국어 전후 문면이다. 문장 예시를 별도 정답 override로 구현하지 않았다.

| 아이템 | 깊이 | 이전 | 현재 |
|---|---|---|---|
| Base.RippedSheets | compact | 응급처치나 의류 수선에 쓸 수 있다. 감염된 재료로 상처를 감으면 감염을 일으킬 수 있다. 건축할 때 재료로 쓸 수 있다. 화염 장치와 연막 장치나 야영 장비나 도구나 골절을 고정할 부목을 만들 때 재료로 쓸 수 있다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다. | 상처 처치와 골절 고정에 쓰거나 의류 수선 재료로 쓸 수 있다. 감염된 재료로 상처를 감으면 감염을 일으킬 수 있다. 건축 재료로 쓸 수 있다. 화염 장치를 만들 때 재료로 쓸 수 있다. 연막 장치를 만들 때 재료로 쓸 수 있다. 야영 장비를 만드는 재료로 쓸 수 있다. 도구를 만드는 재료로 쓸 수 있다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다. |
| Base.RippedSheets | expanded | 화상을 씻는 데 쓸 수 있다. 상처에 감을 수 있다. 소독해서 쓸 수도 있다. 감염된 상태로 쓰면 상처를 감염시킬 수 있다. 머리와 몸통을 제외한 골절 부위를 고정하는 데 쓸 수 있다. 건축할 때 재료로 쓸 수 있다. 화염 장치와 연막 장치나 야영 장비나 도구나 골절을 고정할 부목을 만들 때 재료로 쓸 수 있다. 의류의 구멍을 덧대거나 패딩을 추가할 수 있다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다. | 화상을 씻는 데 쓸 수 있다. 상처에 감을 수 있다. 소독해서 쓸 수도 있다. 감염된 상태로 쓰면 상처를 감염시킬 수 있다. 골절을 고정하는 부목 재료로 쓸 수 있다. 의류의 구멍을 덧대거나 패딩을 추가할 수 있다. 건축 재료로 쓸 수 있다. 화염 장치를 만들 때 재료로 쓸 수 있다. 연막 장치를 만들 때 재료로 쓸 수 있다. 야영 장비를 만드는 재료로 쓸 수 있다. 도구를 만드는 재료로 쓸 수 있다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다. |
| Base.Plank | compact | 골절 고정에 쓸 수 있다. 목재를 가공하거나 건축할 때 재료로 쓸 수 있다. 사냥 장비나 야영 장비나 골절을 고정할 부목을 만들 때 재료로 쓸 수 있다. 톱을 만들 때 재료로 쓸 수 있다. 수박을 쪼개는 데 쓸 수 있다. 무기로도 쓸 수 있다. 모닥불 등의 연료로 쓸 수 있다. | 골절을 고정하는 부목 재료로 쓸 수 있다. 목공과 건축 재료로 쓸 수 있다. 사냥 장비를 만드는 재료로 쓸 수 있다. 야영 장비를 만드는 재료로 쓸 수 있다. 도구를 만드는 재료로 쓸 수 있다. 수박을 쪼개는 데 쓸 수 있다. 무기로도 쓸 수 있다. 모닥불 등의 연료로 쓸 수 있다. |
| Base.Plank | expanded | 머리와 몸통을 제외한 골절 부위를 고정하는 데 쓸 수 있다. 목재를 가공할 때 재료로 쓸 수 있다. 건축할 때 재료로 쓸 수 있다. 사냥 장비나 야영 장비나 골절을 고정할 부목을 만들 때 재료로 쓸 수 있다. 톱을 만들 때 재료로 쓸 수 있다. 수박을 쪼개는 데 쓸 수 있다. 무기로 쓸 수 있다. 모닥불 등의 연료로 쓸 수 있다. | 골절을 고정하는 부목 재료로 쓸 수 있다. 목공과 건축 재료로 쓸 수 있다. 사냥 장비를 만드는 재료로 쓸 수 있다. 야영 장비를 만드는 재료로 쓸 수 있다. 도구를 만드는 재료로 쓸 수 있다. 수박을 쪼개는 데 쓸 수 있다. 무기로 쓸 수 있다. 모닥불 등의 연료로 쓸 수 있다. |
| Base.Log | compact | 목재를 가공하거나 건축할 때 재료로 쓸 수 있다. 야영 장비를 만들 때 재료로 쓸 수 있다. 모아서 묶을 수 있다. 금속 드럼에서 숯을 만드는 재료로 쓸 수 있다. 수박을 쪼개는 데 쓸 수 있다. 모닥불 등의 연료로 쓸 수 있다. | 목공과 건축 재료로 쓸 수 있다. 야영 장비를 만드는 재료로 쓸 수 있다. 모아서 묶을 수 있다. 금속 드럼에서 숯을 만드는 재료로 쓸 수 있다. 수박을 쪼개는 데 쓸 수 있다. 모닥불 등의 연료로 쓸 수 있다. |
| Base.Log | expanded | 목재를 가공할 때 재료로 쓸 수 있다. 건축할 때 재료로 쓸 수 있다. 야영 장비를 만들 때 재료로 쓸 수 있다. 모아서 묶을 수 있다. 금속 드럼에서 숯을 만드는 재료로 쓸 수 있다. 수박을 쪼개는 데 쓸 수 있다. 모닥불 등의 연료로 쓸 수 있다. | 목공과 건축 재료로 쓸 수 있다. 야영 장비를 만드는 재료로 쓸 수 있다. 모아서 묶을 수 있다. 금속 드럼에서 숯을 만드는 재료로 쓸 수 있다. 수박을 쪼개는 데 쓸 수 있다. 모닥불 등의 연료로 쓸 수 있다. |
| Base.MotionSensor | compact | 장치에 작동 부품으로 달아 쓸 수 있다. | 장치에 달아 움직임 감지 기능을 더하는 부품으로 쓸 수 있다. |
| Base.MotionSensor | expanded | 장치에 작동 부품으로 달아 쓸 수 있다. | 장치에 달아 움직임 감지 기능을 더하는 부품으로 쓸 수 있다. |
| Base.TimerCrafted | compact | 장치에 작동 부품으로 달아 쓸 수 있다. | 장치에 달아 시간 지연 기능을 더하는 부품으로 쓸 수 있다. |
| Base.TimerCrafted | expanded | 장치에 작동 부품으로 달아 쓸 수 있다. | 장치에 달아 시간 지연 기능을 더하는 부품으로 쓸 수 있다. |
| Base.DuctTape | compact | 창에 부착물을 다는 재료로 쓸 수 있다. 장치에 작동 부품을 다는 재료로 쓸 수 있다. 다른 물품을 수리하는 재료로 쓸 수 있다. | 창에 부착물을 다는 재료로 쓸 수 있다. 장치에 움직임 감지, 시간 지연, 원격 작동 기능을 더하는 재료로 쓸 수 있다. 무기를 수리하는 재료로 쓸 수 있다. 호환 차량 부품을 수리하는 재료로 쓸 수 있다. |
| Base.DuctTape | expanded | 창에 부착물을 다는 재료로 쓸 수 있다. 장치에 작동 부품을 다는 재료로 쓸 수 있다. 다른 물품을 수리하는 재료로 쓸 수 있다. | 창에 부착물을 다는 재료로 쓸 수 있다. 장치에 움직임 감지, 시간 지연, 원격 작동 기능을 더하는 재료로 쓸 수 있다. 무기를 수리하는 재료로 쓸 수 있다. 호환 차량 부품을 수리하는 재료로 쓸 수 있다. |
| Base.SheetMetal | compact | 용접을 포함한 건축 작업을 할 때 재료로 쓸 수 있다. 호환 물품을 수리할 때 재료로 쓸 수 있다. 금속 부품을 용접하는 데 쓸 수 있다. 금속 바리케이드를 설치하는 데 쓸 수 있다. | 용접 건축 재료로 쓸 수 있다. 호환 차량 부품을 수리하는 재료로 쓸 수 있다. 금속 부품을 용접할 때 재료로 쓸 수 있다. |
| Base.SheetMetal | expanded | 용접을 포함한 건축 작업을 할 때 재료로 쓸 수 있다. 다른 물품을 수리하는 재료로 쓸 수 있다. 금속 부품을 용접할 때 재료로 쓸 수 있다. 문과 창문에 금속 바리케이드를 설치하는 데 사용할 수 있다. | 용접 건축 재료로 쓸 수 있다. 문과 창문의 금속 바리케이드에도 재료로 쓸 수 있다. 호환 차량 부품을 수리하는 재료로 쓸 수 있다. 금속 부품을 용접할 때 재료로 쓸 수 있다. |
| Base.BlowTorch | compact | 금속을 용접해 건축하는 데 쓸 수 있다. 금속 바리케이드를 설치하거나 철거하는 데 쓸 수 있다. 불타거나 파손된 차량을 분해하는 데 쓸 수 있다. | 금속 부품을 용접하거나 용접으로 건축하는 도구로 쓸 수 있다. 금속 바리케이드를 설치하거나 철거하는 데 쓸 수 있다. 불타거나 파손된 차량을 분해하는 데 쓸 수 있다. |
| Base.BlowTorch | expanded | 금속 부품을 용접하거나 용접으로 건축하는 데 쓸 수 있다. 문과 창문에 금속 바리케이드를 설치하는 데 사용할 수 있다. 금속 바리케이드를 철거하는 데 사용할 수 있다. 불타거나 파손된 차량을 분해해 재료를 회수할 수 있다. | 금속 부품을 용접하거나 용접으로 건축하는 도구로 쓸 수 있다. 문과 창문에 금속 바리케이드를 설치하는 데 사용할 수 있다. 금속 바리케이드를 철거하는 데 사용할 수 있다. 불타거나 파손된 차량을 분해해 재료를 회수할 수 있다. |
| Base.Shotgun | compact | 다른 물품을 수리하는 재료로 쓸 수 있다. 탄약을 장전해 사격할 수 있다. 산탄총의 총신을 줄일 수 있다. | 총기를 수리하는 재료로 쓸 수 있다. 탄약을 장전해 사격할 수 있다. 총신을 짧게 개조할 수 있다. |
| Base.Shotgun | expanded | 다른 물품을 수리하는 재료로 쓸 수 있다. 탄약을 장전해 사격할 수 있다. 산탄총의 총신을 줄일 수 있다. | 총기를 수리하는 재료로 쓸 수 있다. 탄약을 장전해 사격할 수 있다. 총신을 짧게 개조할 수 있다. |
| Base.Saw | compact | 사냥 장비를 만들거나 폭발 장치를 만드는 데 쓸 수 있다. 음식을 손질하고 목재를 가공할 수 있다. 건축물을 해체하거나 산탄총의 총신을 줄일 수 있다. | 사냥 장비를 만들거나 폭발 장치를 만드는 데 쓸 수 있다. 음식을 손질하고 목재를 가공할 수 있다. 건축물을 해체하거나 산탄총의 총신을 줄일 수 있다. |
| Base.Saw | expanded | 사냥 장비를 만들거나 폭발 장치를 만드는 데 쓸 수 있다. 음식을 나누는 데 쓸 수 있다. 목재를 가공하는 데 쓸 수 있다. 분해 가능한 건축물을 해체하고 재료를 회수할 수 있다. 산탄총의 총신을 줄일 수 있다. | 사냥 장비를 만들거나 폭발 장치를 만드는 데 쓸 수 있다. 음식을 나누는 데 쓸 수 있다. 목재를 가공하는 데 쓸 수 있다. 분해 가능한 건축물을 해체하고 재료를 회수할 수 있다. 산탄총의 총신을 줄이는 도구로 쓸 수 있다. |
| Base.Book | compact | 독서 중 지루함, 스트레스, 불행이 더 심해지는 것을 막을 수 있다. 모닥불 키트를 만들 때 재료로 쓸 수 있다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다. | 야영 장비를 만드는 재료로 쓸 수 있다. 읽을 수 있다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다. |
| Base.Book | expanded | 독서 중 지루함, 스트레스, 불행이 더 심해지는 것을 막을 수 있다. 모닥불 키트를 만들 때 재료로 쓸 수 있다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다. | 야영 장비를 만드는 재료로 쓸 수 있다. 읽을 수 있다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다. |
| Base.Fertilizer | compact | 작물의 성장을 촉진할 수 있다. 비료를 너무 많이 주면 작물이 썩을 수 있다. | 작물의 성장을 촉진할 수 있다. 비료를 너무 많이 주면 작물이 썩을 수 있다. |
| Base.Fertilizer | expanded | 작물의 성장을 촉진할 수 있다. 비료를 너무 많이 주면 작물이 썩을 수 있다. | 작물의 성장을 촉진할 수 있다. 비료를 너무 많이 주면 작물이 썩을 수 있다. |
| Base.AmmoStrap_Shells | compact | 착용 시 산탄 사용 총기의 장전 속도 +15%. 금속 드럼의 불쏘시개로 쓸 수 있다. | 착용하면 산탄을 쓰는 총기의 장전 속도를 15% 높인다. 금속 드럼의 불쏘시개로 쓸 수 있다. |
| Base.AmmoStrap_Shells | expanded | 착용할 수 있다. 착용 중 산탄 사용 총기의 장전 속도를 15% 높인다. 금속 드럼의 불쏘시개로 쓸 수 있다. | 착용할 수 있다. 착용하면 산탄을 쓰는 총기의 장전 속도를 15% 높인다. 금속 드럼의 불쏘시개로 쓸 수 있다. |
| Base.EmptyPetrolCan | compact | 주유기에서 연료를 받거나 차량과 연료를 주고받을 수 있다. | 주유기나 차량에서 연료를 담을 수 있다. 담긴 연료를 차량에 넣을 수도 있다. |
| Base.EmptyPetrolCan | expanded | 주유기에서 연료를 받거나 차량과 연료를 주고받을 수 있다. | 주유기나 차량에서 연료를 담을 수 있다. 담긴 연료를 차량에 넣을 수도 있다. |
| Base.FrontWindow1 | compact | 호환 차량의 여닫는 앞문 유리로 쓸 수 있다. | 호환 차량의 앞문 유리 자리에 장착할 수 있다. 장착 후 여닫을 수 있다. |
| Base.FrontWindow1 | expanded | 호환 차량의 앞문 유리 자리에 장착할 수 있다. 장착 후 여닫을 수 있다. | 호환 차량의 앞문 유리 자리에 장착할 수 있다. 장착 후 여닫을 수 있다. |
| Base.HoodieDOWN_WhiteTINT | compact | 착용할 수 있다. 착용 모양을 바꿀 수도 있다. 찢어서 천 조각을 얻을 수 있다. 시트 로프를 만들 때 재료로 쓸 수 있다. 연료나 불쏘시개로도 쓸 수 있다. | 착용할 수 있다. 후드를 쓸 수 있다. 찢어서 천 조각을 얻을 수 있다. 시트 로프를 만들 때 재료로 쓸 수 있다. 연료나 불쏘시개로도 쓸 수 있다. |
| Base.HoodieDOWN_WhiteTINT | expanded | 착용할 수 있다. 착용 모양을 바꿀 수 있다. 찢어서 천 조각을 얻을 수 있다. 시트 로프를 만들 때 재료로 쓸 수 있다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다. | 착용할 수 있다. 후드를 쓸 수 있다. 찢어서 천 조각을 얻을 수 있다. 시트 로프를 만들 때 재료로 쓸 수 있다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다. |
| Radio.CDplayer | compact | 기록 매체 재생에 쓸 수 있다. | CD에 담긴 소리를 재생할 수 있다. |
| Radio.CDplayer | expanded | 기록 매체 재생에 쓸 수 있다. | CD에 담긴 소리를 재생할 수 있다. |
| Base.LightBulb | compact | 호환 차량의 전조등 자리에 장착할 수 있다. 전구를 교체할 수 있는 조명에 장착할 수 있다. 간이 무전기를 만들 때 재료로 쓸 수 있다. | 호환 차량의 전조등에 달아 빛을 낼 수 있다. 전자 기기를 만드는 재료로 쓸 수 있다. |
| Base.LightBulb | expanded | 호환 차량의 전조등 자리에 장착할 수 있다. 전구를 교체할 수 있는 조명에 장착할 수 있다. 간이 무전기를 만들 때 재료로 쓸 수 있다. | 호환 차량의 전조등에 달아 빛을 낼 수 있다. 전자 기기를 만드는 재료로 쓸 수 있다. |
| Base.ModernBrake1 | compact | 맞는 차량에 브레이크로 장착할 수 있다. | [absent] |
| Base.ModernBrake1 | expanded | 맞는 차량에 브레이크로 장착할 수 있다. | [absent] |
| Base.Mov_AirConditioner | compact | 배치하거나 옮길 수 있다. | [absent] |
| Base.Mov_AirConditioner | expanded | 배치하거나 옮길 수 있다. | [absent] |
| Base.308Clip | compact | 호환 총기에 끼워 사용할 수 있다. 호환 탄약을 넣어 총기에 장전할 수 있다. 탄창의 잔탄을 꺼낼 수 있다. | 호환 탄약을 담아 맞는 총기에 장전할 수 있다. 탄창의 잔탄을 꺼낼 수 있다. |
| Base.308Clip | expanded | 호환 총기에 끼워 사용할 수 있다. 호환 탄약을 넣어 총기에 장전할 수 있다. 탄창의 잔탄을 꺼낼 수 있다. | 호환 탄약을 담아 맞는 총기에 장전할 수 있다. 탄창의 잔탄을 꺼낼 수 있다. |

신규 absent의 실제 ID 범위는 다음과 같다.

- placement: 135개 — `Base.Mov_AirConditioner`, `Base.Mov_AntiqueStove`, `Base.Mov_ArcadeMachine1`, `Base.Mov_ArcadeMachine2`, `Base.Mov_BeachChair`, `Base.Mov_BinRound`, `Base.Mov_Birdbath`, `Base.Mov_BlueComfyChair`, `Base.Mov_BluePlasticChair`, `Base.Mov_BlueRattanChair`, `Base.Mov_BrownComfyChair`, `Base.Mov_BrownLowTable`, `Base.Mov_CabinetMedical`, `Base.Mov_CabinetTool`, `Base.Mov_CardboardBox`, `Base.Mov_ChromeSink`, `Base.Mov_CoffeeMaker`, `Base.Mov_ConcreteMixer`, `Base.Mov_CorkBoard`, `Base.Mov_DarkBlueChair`, `Base.Mov_DarkWoodenChair`, `Base.Mov_DegreeDoctor`, `Base.Mov_DegreeSurgeon`, `Base.Mov_DesktopComputer`, `Base.Mov_Doghouse`, `Base.Mov_Espresso`, `Base.Mov_FancyBlackChair`, `Base.Mov_FancyDarkTable`, `Base.Mov_FancyLowTable`, `Base.Mov_FancyTable`, `Base.Mov_FancyToilet`, `Base.Mov_FancyWhiteChair`, `Base.Mov_FitnessContraption`, `Base.Mov_FlagAdmin`, `Base.Mov_FlagUSA`, `Base.Mov_FlagUSALarge`, `Base.Mov_FoldingChair`, `Base.Mov_FridgeMini`, `Base.Mov_GardenGnome`, `Base.Mov_GraveArched`, `Base.Mov_GraveRound`, `Base.Mov_GraveSquare`, `Base.Mov_GraveWorn`, `Base.Mov_GreenChair`, `Base.Mov_GreenComfyChair`, `Base.Mov_GreenOven`, `Base.Mov_GreyChair`, `Base.Mov_GreyComfyChair`, `Base.Mov_GreyOven`, `Base.Mov_HotdogMachine`, `Base.Mov_HuntingTrophy`, `Base.Mov_IndustrialSink`, `Base.Mov_Lamp1`, `Base.Mov_Lamp2`, `Base.Mov_Lamp3`, `Base.Mov_Lamp4`, `Base.Mov_Lamp5`, `Base.Mov_Lamp6`, `Base.Mov_LightConstruction`, `Base.Mov_LightRoundTable`, `Base.Mov_LongTable`, `Base.Mov_Mailbox`, `Base.Mov_MannequinFemale`, `Base.Mov_MannequinMale`, `Base.Mov_MapUSA`, `Base.Mov_MetalLocker`, `Base.Mov_MetalStool`, `Base.Mov_Microphone`, `Base.Mov_Microwave`, `Base.Mov_Microwave2`, `Base.Mov_MirrorLarge`, `Base.Mov_MirrorSmall`, `Base.Mov_MirrorTall`, `Base.Mov_MirrorWood`, `Base.Mov_MobileBloodbag`, `Base.Mov_MobileCounter`, `Base.Mov_ModernOven`, `Base.Mov_NapkinDispenser`, `Base.Mov_OakRoundTable`, `Base.Mov_OfficeChair`, `Base.Mov_OrangeFuton`, `Base.Mov_OrangeModernChair`, `Base.Mov_PaintingBetty`, `Base.Mov_PaintingElisa`, `Base.Mov_PaintingGreen`, `Base.Mov_PaintingLibrary`, `Base.Mov_PalletEmpty`, `Base.Mov_PileOCrepeChair`, `Base.Mov_PinballMachine`, `Base.Mov_PinkFlamingo`, `Base.Mov_PlasticChair`, `Base.Mov_PlasticLowTable`, `Base.Mov_PopcornMachine`, `Base.Mov_PosterDroids`, `Base.Mov_PosterElement`, `Base.Mov_PosterMedical`, `Base.Mov_PosterOmega`, `Base.Mov_PosterPaws`, `Base.Mov_PosterPieBlue`, `Base.Mov_PosterPieGreen`, `Base.Mov_PosterPiePink`, `Base.Mov_PosterPieRed`, `Base.Mov_Projector`, `Base.Mov_PurpleRattanChair`, `Base.Mov_PurpleWoodenChair`, `Base.Mov_RedBBQ`, `Base.Mov_RedChair`, `Base.Mov_RedOven`, `Base.Mov_RedWoodenChair`, `Base.Mov_RoadBarrier`, `Base.Mov_RoadCone`, `Base.Mov_RoadCone2`, `Base.Mov_RoundTable`, `Base.Mov_SatelliteDish`, `Base.Mov_ScaleMedical`, `Base.Mov_ShoppingBaskets`, `Base.Mov_SignArmy`, `Base.Mov_SignCitrus`, `Base.Mov_SignRestricted`, `Base.Mov_SignWarning`, `Base.Mov_SmallTable`, `Base.Mov_SodaMachine`, `Base.Mov_TVCamera`, `Base.Mov_Toaster`, `Base.Mov_TowelDispenser`, `Base.Mov_Urinal`, `Base.Mov_WallClock`, `Base.Mov_WaterDispenser`, `Base.Mov_WhiteComfyChair`, `Base.Mov_WhiteSimpleChair`, `Base.Mov_WhiteSink`, `Base.Mov_WhiteWoodenChair`, `Base.Mov_WoodenChair`, `Base.Mov_WoodenStool`, `Base.Mov_YellowModernChair`

- vehicle_installed: 39개 — `Base.ModernBrake1`, `Base.ModernBrake2`, `Base.ModernBrake3`, `Base.ModernCarMuffler1`, `Base.ModernCarMuffler2`, `Base.ModernCarMuffler3`, `Base.ModernSuspension1`, `Base.ModernSuspension2`, `Base.ModernSuspension3`, `Base.ModernTire1`, `Base.ModernTire2`, `Base.ModernTire3`, `Base.NormalBrake1`, `Base.NormalBrake2`, `Base.NormalBrake3`, `Base.NormalCarMuffler1`, `Base.NormalCarMuffler2`, `Base.NormalCarMuffler3`, `Base.NormalSuspension1`, `Base.NormalSuspension2`, `Base.NormalSuspension3`, `Base.NormalTire1`, `Base.NormalTire2`, `Base.NormalTire3`, `Base.OldBrake1`, `Base.OldBrake2`, `Base.OldBrake3`, `Base.OldCarMuffler1`, `Base.OldCarMuffler2`, `Base.OldCarMuffler3`, `Base.OldTire1`, `Base.OldTire2`, `Base.OldTire3`, `Base.RearWindshield1`, `Base.RearWindshield2`, `Base.RearWindshield3`, `Base.Windshield1`, `Base.Windshield2`, `Base.Windshield3`

- lamp_bulb: 8개 — `Base.LightBulbBlue`, `Base.LightBulbCyan`, `Base.LightBulbMagenta`, `Base.LightBulbOrange`, `Base.LightBulbPink`, `Base.LightBulbPurple`, `Base.LightBulbRed`, `Base.LightBulbYellow`


검증은 필요한 기존 4개 노드만 한 번 실행했다. 이번 실행은 `4 passed in 149.93s`, 종료 코드 `0`이다. 정확한 명령과 전체 로그는 `.tmp/prose/relations-tests.log`에 남겼다.

```powershell
$env:IRIS_SHARED_MENU_VALIDATION='1'
Remove-Item Env:IRIS_MENU_TOOLTIP_CANDIDATE -ErrorAction SilentlyContinue
uv run --project .\Iris\tooling python -I -B -m pytest --noconftest -c .\Iris\tooling\pyproject.toml .\Iris\build\description\v2\tests\test_layer3_composition.py::test_layer3_composition_contract .\Iris\build\description\v2\tests\test_layer3_description_composition.py::test_layer3_description_composition .\Iris\tooling\tests\test_tooltip_t2_projection.py::test_s2_supply_and_owner_integration .\Iris\build\description\v2\tests\test_layer3_product_integration.py::test_product_contract --basetemp .\.tmp\relations-tests-01 -q -s --tb=short
```

검사 내에서 소스와 staging의 Lua 388개 구문 검사, Browser/Wiki 모델 소비(폰트 stub), S2 공급, 두 번 생성한 제품의 바이트 일치, 패키지/ZIP과 포인터, 중단·롤백·재진입 경로가 종료 코드 0으로 확인되었다. 실제 게임 폰트나 화면을 관찰한 결과는 아니다. 기존 계약 노드에 역할·대상·포괄 관계·근거 보류 재발 방지 확인을 넣고 오래된 문구/상태 집계 기대값을 현재 계약에 맞췄다. 새 검증 프레임워크는 만들지 않았다. 이전 `.tmp/prose/depth-tests.log`의 1 failed / 3 passed와 그 재실행 로그 등 기존 실패 이력은 지우지 않았다. 이번 실행에 재시도는 없었다.

- descriptions SHA-256: `fb71dfc5e78605427d978fa832967dc60b132eb5f61604e5ca96ceaa110b1a72`
- blocks SHA-256: `f15ebf1dd742d55fc9651f005067265adea127b86a92fa4b3acd15e4b765270d`
- product: `l3p-e06af35d26952ce892305b9a2fe916d71cb028af48613172f21ca09cfb906a4d`
- ZIP: `.tmp/menu/run-xszjof36/p/Iris.zip`
- ZIP SHA-256: `fdb358eda1abe61a1ac6dfb5b7b79fe85ca2801352aff961003814be7a488a2f`

소스/산출물/연결 해시/기존 검사/검토 HTML 및 이 기록 외에 설치·커밋·푸시·워크트리 생성·외부 조사·새 자동화는 수행하지 않았다. 개별 아이템 ID/이름별 문장 분기나 완성 문장 덮어쓰기를 추가하지 않았으며, 새 원본 어댑터를 위한 사전 구현도 하지 않았다.


## 2026-09-14 후속 전문 교정: 병렬 재료 역할·현재 착용·교체 용도

직전 `fb71dfc5e78605427d978fa832967dc60b132eb5f61604e5ca96ceaa110b1a72` 후보에 남았던 지적을 이어받았다. 이전의 “독립 목적마다 별도 문장” 규칙과 “네이티브 실제 효과가 없으면 설치 관계도 absent” 기준은 과도했다. 아래 내용으로 해당 판정을 정정한다. 특정 아이템 문구를 덮어쓰지 않고 근거의 역할·결과·설치 및 착용 관계를 조립하는 공통 경로를 수정했다.

| 유형 | 원인과 공통 교정 | 확인 범위·판정 |
|---|---|---|
| Compact 재료 역할 반복 | `frames`가 재료 목적을 구조화해 모으고 같은 역할 서술어를 공유한다. 작업과 제작 결과를 구분하되 병렬 용도로 연결한다. Expanded는 제작 범주를 묶으면서 장치 개조 방식·수리 대상·숯 제작 장소 같은 유효한 상세를 유지한다. 의료 위험·연료·도구·무기 등 독립 목적을 삭제하거나 재료로 오인하지 않는다. | 제작 재료 71개, 수리 재료 20개, 개조 10개 범위 대조. RippedSheetsDirty, Plank, Log뿐 아니라 ElectronicsScrap·DuctTape·Glue에 적용. 알려진 반복 원인 교정. |
| 형태 변경이 현재 착용을 삼킴 | 현재 BodyLocation/CanBeEquipped와 선언된 대체 아이템의 착용 위치를 observation에 연결한다. 두 위치를 함께 서술하거나 현재 착용과 전환 문장을 모두 남긴다. 메뉴 문자열만 효용으로 번역하지 않는다. | 형태 전환 79개 전체. 귀걸이 현재 귀/귀 위 착용, 반지 현재 손가락, 반다나 머리/얼굴 착용을 보존. 자기 이름 반복 제거. |
| 용접 장비와 작업 도구 혼동 | 채택된 착용 사실을 가진 용접 참여자는 얼굴에 착용하는 장비로 설명한다. 수행 도구인 토치와 구분하며 보호 효과는 추정하지 않는다. | 용접 관련 공통 도구 경로. WeldingMask의 별도 “얼굴에 착용” 중복도 통합. |
| Compact 차량 패널의 메뉴 깊이 | Compact는 호환 차량의 교체 부품 역할을 설명하고 Expanded에 실제 설치 위치와 여닫기·잠금 기능을 둔다. | 차량 설치 관계 76개 범위. 패널·문·유리 및 나머지 교체 부품 대조. |
| 과도한 absent | 장착 관계가 교체 부품 역할을 입증하는 경우 실제 물리 효과 구현을 추가 요구하지 않는다. 가구는 Type=Moveable, DisplayCategory=Furniture, WorldObjectSprite와 배치 관계가 확인되면 선언된 설치용 역할을 복원한다. | 직전 신규 absent 182개 전부 복원: 가구 135, 차량 부품 39, 전구 8. 교체 역할 복원과 가구 개별 기능의 근거 부족은 구분한다. |
| 일반 독서 목적 공백 | 음수 감정 선언과 ISReadABook의 morale-boosting 읽을거리 설명 및 실제 읽기 진입을 연결한 `declared_morale_reading_purpose`를 추가한다. 읽기 시작 상한 보정은 계속 내부 처리다. | 일반 읽을거리 12개에 기분 전환 목적 복원. 기술서의 수준·배율 및 제작법 학습은 보존. 감정 감소량·시점·보장까지 해결했다고 판정하지 않는다. |
| 장치·매체의 중복/모호 표현 | “작동 방식으로 작동”을 기능 개조로 정리한다. 매체 자체의 MediaCategory도 CD/VHS 재생 관계에 연결해 기기 설명과 같은 관계를 반대 역할에서 서술한다. | 개조 10개, 플레이어 4개, 매체 3개. 기존의 확인된 지루함·학습 효과와 스트레스·공포 가능성 보존. |

가구는 선언된 설치용 역할을 설명하는 수준이다. 이동 가구 140개 중 가구 선언과 배치 관계가 확인된 136개(새로 복원한 135개와 Mattress)의 역할을 반영하고 깨진 바닥 유리 4개는 이 분기에 넣지 않았다. 난방·보관·휴식 등 가구별 실제 기능은 해당 sprite의 속성 자료를 채택 소스에서 연결하지 못했으므로 여전히 근거 보류다. 차량의 제동력·접지력·충격 흡수·소음 감소도 교체 역할과 별개의 주장으로 남긴다. 독서의 기분 전환용 목적은 원본에 명시되지만 실제 감정 감소량·시점은 네이티브 적용 구현이 확인되지 않아 추가하지 않았다. 이 근거 보류를 문면 완료나 absent 개수 감소로 해결 처리하지 않는다.

전체 2,105개 한국어 Compact·Expanded 4,210개 표면을 572개 전문군으로 펼쳐 읽었다. 각 전문군의 적용 아이템과 깊이는 원본에 연결하며 동일 전문의 중복만 묶었다. 그 후 통나무의 숯 제작을 병렬 재료 목적에 통합하고 변경 325개 아이템의 한국어 양쪽 전문 107개 군을 다시 대조했다. 통합 중 기존 의류 문자열 변수와 새 함수 이름의 충돌로 Compact 194개가 실패한 중간 생성이 있었으며, `.tmp/prose/parallel-generation4.log`를 보존했다. 함수 이름 충돌을 수정한 `.tmp/prose/parallel-generation5.log`에서 모든 언어/깊이의 failed 0을 확인했다. 생성 명령 종료 0만으로 내용 실패가 없다고 판단하지 않았다.

최종 변경은 325개 아이템의 1,226개 표면(KO C 322, KO E 296, EN C 317, EN E 291)이다. 각 언어/깊이에서 present 1,976, absent 129, failed 0이며 새로운 absent는 없다. 이 집계는 문면의 의미·자연스러움·깊이 검수를 대신하지 않는다. 두 HTML을 현재 출력과 fb71 후보의 실제 전후 비교로 갱신했다. 역사적 review JSON과 원본 r6는 수정하지 않았다.

다음은 실제 생성 결과의 한국어 전문이다.

| 아이템 | 깊이 | 이전 | 현재 |
|---|---|---|---|
| Base.RippedSheetsDirty | compact | 건축 재료로 쓸 수 있다. 화염 장치를 만들 때 재료로 쓸 수 있다. 연막 장치를 만들 때 재료로 쓸 수 있다. 야영 장비를 만드는 재료로 쓸 수 있다. 도구를 만드는 재료로 쓸 수 있다. 상처에 감을 수 있다. 감염된 상태로 쓰면 상처를 감염시킬 수 있다. 물로 씻어 깨끗한 붕대 재료로 바꿀 수 있다. 골절을 고정할 부목을 만드는 재료로 쓸 수 있다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다. | 상처에 감을 수 있다. 감염된 상태로 쓰면 상처를 감염시킬 수 있다. 물로 씻어 깨끗한 붕대 재료로 바꿀 수 있다. 건축에 쓰거나 화염 장치, 연막 장치, 야영 장비, 도구 및 부목을 만드는 데 쓰는 재료다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다. |
| Base.RippedSheetsDirty | expanded | 건축 재료로 쓸 수 있다. 화염 장치를 만들 때 재료로 쓸 수 있다. 연막 장치를 만들 때 재료로 쓸 수 있다. 야영 장비를 만드는 재료로 쓸 수 있다. 도구를 만드는 재료로 쓸 수 있다. 상처에 감을 수 있다. 감염된 상태로 쓰면 상처를 감염시킬 수 있다. 물로 씻어 깨끗한 붕대 재료로 바꿀 수 있다. 골절을 고정할 부목을 만드는 재료로 쓸 수 있다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다. | 상처에 감을 수 있다. 감염된 상태로 쓰면 상처를 감염시킬 수 있다. 물로 씻어 깨끗한 붕대 재료로 바꿀 수 있다. 화염 장치, 연막 장치, 야영 장비, 도구 및 부목을 만드는 재료로 쓸 수 있다. 건축 재료로 쓸 수 있다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다. |
| Base.Plank | compact | 골절을 고정하는 부목 재료로 쓸 수 있다. 목공과 건축 재료로 쓸 수 있다. 사냥 장비를 만드는 재료로 쓸 수 있다. 야영 장비를 만드는 재료로 쓸 수 있다. 도구를 만드는 재료로 쓸 수 있다. 수박을 쪼개는 데 쓸 수 있다. 무기로도 쓸 수 있다. 모닥불 등의 연료로 쓸 수 있다. | 골절을 고정하는 부목 재료로 쓸 수 있다. 목공과 건축에 쓰거나 사냥 장비, 야영 장비 및 도구를 만드는 데 쓰는 재료다. 수박을 쪼개는 데 쓸 수 있다. 무기로도 쓸 수 있다. 모닥불 등의 연료로 쓸 수 있다. |
| Base.Plank | expanded | 골절을 고정하는 부목 재료로 쓸 수 있다. 목공과 건축 재료로 쓸 수 있다. 사냥 장비를 만드는 재료로 쓸 수 있다. 야영 장비를 만드는 재료로 쓸 수 있다. 도구를 만드는 재료로 쓸 수 있다. 수박을 쪼개는 데 쓸 수 있다. 무기로 쓸 수 있다. 모닥불 등의 연료로 쓸 수 있다. | 골절을 고정하는 부목 재료로 쓸 수 있다. 목공과 건축 재료로 쓸 수 있다. 사냥 장비, 야영 장비 및 도구를 만드는 재료로 쓸 수 있다. 수박을 쪼개는 데 쓸 수 있다. 무기로 쓸 수 있다. 모닥불 등의 연료로 쓸 수 있다. |
| Base.Log | compact | 목공과 건축 재료로 쓸 수 있다. 야영 장비를 만드는 재료로 쓸 수 있다. 모아서 묶을 수 있다. 금속 드럼에서 숯을 만드는 재료로 쓸 수 있다. 수박을 쪼개는 데 쓸 수 있다. 모닥불 등의 연료로 쓸 수 있다. | 목공과 건축에 쓰거나 야영 장비 및 숯을 만드는 데 쓰는 재료다. 모아서 묶을 수 있다. 수박을 쪼개는 데 쓸 수 있다. 모닥불 등의 연료로 쓸 수 있다. |
| Base.Log | expanded | 목공과 건축 재료로 쓸 수 있다. 야영 장비를 만드는 재료로 쓸 수 있다. 모아서 묶을 수 있다. 금속 드럼에서 숯을 만드는 재료로 쓸 수 있다. 수박을 쪼개는 데 쓸 수 있다. 모닥불 등의 연료로 쓸 수 있다. | 목공과 건축 재료로 쓸 수 있다. 야영 장비를 만드는 재료로 쓸 수 있다. 금속 드럼에서 숯을 만드는 재료로 쓸 수 있다. 모아서 묶을 수 있다. 수박을 쪼개는 데 쓸 수 있다. 모닥불 등의 연료로 쓸 수 있다. |
| Base.ElectronicsScrap | compact | 장치에 움직임 감지, 시간 지연, 원격 작동 기능을 더하는 재료로 쓸 수 있다. 전자 기기를 만드는 재료로 쓸 수 있다. 조명을 건전지로 작동하도록 개조할 수 있다. 소음 발생 장치를 만들 때 재료로 쓸 수 있다. 폭발 장치를 만들 때 재료로 쓸 수 있다. 손상된 발전기를 수리하는 데 사용할 수 있다. | 장치 개조, 조명의 건전지용 개조 및 발전기 수리에 쓰거나 전자 기기, 소음 발생 장치 및 폭발 장치를 만드는 데 쓰는 재료다. |
| Base.ElectronicsScrap | expanded | 장치에 움직임 감지, 시간 지연, 원격 작동 기능을 더하는 재료로 쓸 수 있다. 전자 기기를 만드는 재료로 쓸 수 있다. 조명을 건전지로 작동하도록 개조할 수 있다. 소음 발생 장치를 만들 때 재료로 쓸 수 있다. 폭발 장치를 만들 때 재료로 쓸 수 있다. 손상된 발전기를 수리하는 데 사용할 수 있다. | 장치에 움직임 감지, 시간 지연, 원격 작동 기능을 더하는 재료로 쓸 수 있다. 전자 기기, 소음 발생 장치 및 폭발 장치를 만드는 재료로 쓸 수 있다. 조명을 건전지용으로 개조하는 재료로 쓸 수 있다. 손상된 발전기를 수리하는 재료로 쓸 수 있다. |
| Base.DuctTape | compact | 창에 부착물을 다는 재료로 쓸 수 있다. 장치에 움직임 감지, 시간 지연, 원격 작동 기능을 더하는 재료로 쓸 수 있다. 무기를 수리하는 재료로 쓸 수 있다. 호환 차량 부품을 수리하는 재료로 쓸 수 있다. | 창 부착물 고정, 장치 개조, 무기 수리 및 호환 차량 부품 수리에 재료로 쓸 수 있다. |
| Base.DuctTape | expanded | 창에 부착물을 다는 재료로 쓸 수 있다. 장치에 움직임 감지, 시간 지연, 원격 작동 기능을 더하는 재료로 쓸 수 있다. 무기를 수리하는 재료로 쓸 수 있다. 호환 차량 부품을 수리하는 재료로 쓸 수 있다. | 창에 부착물을 다는 재료로 쓸 수 있다. 장치에 움직임 감지, 시간 지연, 원격 작동 기능을 더하는 재료로 쓸 수 있다. 무기 및 호환 차량 부품을 수리하는 재료로 쓸 수 있다. |
| Base.Glue | compact | 전자 기기를 만드는 재료로 쓸 수 있다. 무기를 수리하는 재료로 쓸 수 있다. 호환 차량 부품을 수리하는 재료로 쓸 수 있다. | 무기 수리 및 호환 차량 부품 수리에 쓰거나 전자 기기를 만드는 데 쓰는 재료다. |
| Base.Glue | expanded | 전자 기기를 만드는 재료로 쓸 수 있다. 무기를 수리하는 재료로 쓸 수 있다. 호환 차량 부품을 수리하는 재료로 쓸 수 있다. | 전자 기기를 만드는 재료로 쓸 수 있다. 무기 및 호환 차량 부품을 수리하는 재료로 쓸 수 있다. |
| Base.Earring_LoopSmall_Gold_Both | compact | 귀 위쪽에 착용할 수 있다. 금속 드럼의 불쏘시개로 쓸 수 있다. | 귀에 착용할 수 있다. 귀 위쪽으로 옮겨 달 수 있다. 금속 드럼의 불쏘시개로 쓸 수 있다. |
| Base.Earring_LoopSmall_Gold_Both | expanded | 귀 위쪽에 착용할 수 있다. 금속 드럼의 불쏘시개로 쓸 수 있다. | 귀에 착용할 수 있다. 귀 위쪽으로 옮겨 달 수 있다. 금속 드럼의 불쏘시개로 쓸 수 있다. |
| Base.Ring_Left_MiddleFinger_Gold | compact | 다른 손가락으로 옮겨 낄 수 있다. 금속 드럼의 불쏘시개로 쓸 수 있다. | 양손의 중지나 약지에 골라 낄 수 있다. 금속 드럼의 불쏘시개로 쓸 수 있다. |
| Base.Ring_Left_MiddleFinger_Gold | expanded | 다른 손가락으로 옮겨 낄 수 있다. 금속 드럼의 불쏘시개로 쓸 수 있다. | 왼손 중지에 착용할 수 있다. 다른 손가락으로 옮겨 낄 수 있다. 금속 드럼의 불쏘시개로 쓸 수 있다. |
| Base.Hat_BandanaMask | compact | 반다나를 묶어 머리에 쓸 수 있다. 반다나의 매듭을 풀 수 있다. 금속 드럼의 불쏘시개로 쓸 수 있다. | 머리에 쓰거나 얼굴을 가리는 형태로 바꿔 쓸 수 있다. 금속 드럼의 불쏘시개로 쓸 수 있다. |
| Base.Hat_BandanaMask | expanded | 반다나를 묶어 머리에 쓸 수 있다. 반다나의 매듭을 풀 수 있다. 금속 드럼의 불쏘시개로 쓸 수 있다. | 머리에 쓰거나 얼굴을 가리는 형태로 바꿔 쓸 수 있다. 금속 드럼의 불쏘시개로 쓸 수 있다. |
| Base.WeldingMask | compact | 금속 부품을 용접하거나 용접으로 건축하는 도구로 쓸 수 있다. 얼굴에 착용할 수 있다. 금속 드럼의 불쏘시개로 쓸 수 있다. | 금속 부품 용접과 용접 건축을 할 때 얼굴에 착용하는 장비다. 금속 드럼의 불쏘시개로 쓸 수 있다. |
| Base.WeldingMask | expanded | 금속 부품을 용접하거나 용접으로 건축하는 도구로 쓸 수 있다. 얼굴에 착용할 수 있다. 금속 드럼의 불쏘시개로 쓸 수 있다. | 금속 부품 용접과 용접 건축을 할 때 얼굴에 착용하는 장비다. 금속 드럼의 불쏘시개로 쓸 수 있다. |
| Base.FrontWindow1 | compact | 호환 차량의 앞문 유리 자리에 장착할 수 있다. 장착 후 여닫을 수 있다. | 호환 차량의 앞문 유리 교체 부품으로 쓸 수 있다. |
| Base.FrontWindow1 | expanded | 호환 차량의 앞문 유리 자리에 장착할 수 있다. 장착 후 여닫을 수 있다. | 호환 차량의 앞문 유리 자리에 장착할 수 있다. 장착 후 여닫을 수 있다. |
| Base.ModernBrake1 | compact | [absent] | 호환 차량의 브레이크 교체 부품으로 쓸 수 있다. |
| Base.ModernBrake1 | expanded | [absent] | 호환 차량의 브레이크 교체 부품으로 쓸 수 있다. |
| Base.LightBulbBlue | compact | [absent] | 호환 조명에 넣는 교체용 전구다. |
| Base.LightBulbBlue | expanded | [absent] | 호환 조명에 넣는 교체용 전구다. |
| Base.Mov_AirConditioner | compact | [absent] | 설치용 가구로 쓸 수 있다. |
| Base.Mov_AirConditioner | expanded | [absent] | 가구로 설치할 수 있으며, 필요하면 다른 곳으로 옮겨 배치할 수 있다. |
| Base.Book | compact | 야영 장비를 만드는 재료로 쓸 수 있다. 읽을 수 있다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다. | 기분 전환을 위한 읽을거리로 쓸 수 있다. 야영 장비를 만드는 재료로 쓸 수 있다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다. |
| Base.Book | expanded | 야영 장비를 만드는 재료로 쓸 수 있다. 읽을 수 있다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다. | 기분 전환을 위한 읽을거리로 쓸 수 있다. 야영 장비를 만드는 재료로 쓸 수 있다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다. |
| Base.Disc_Retail | compact | 호환 재생 기기에 넣어 기록된 내용을 재생할 수 있다. 내용에 따라 지루함을 달래는 데도 쓸 수 있다. | CD 플레이어로 녹음된 소리를 들을 수 있다. 내용에 따라 지루함을 달래는 데도 쓸 수 있다. |
| Base.Disc_Retail | expanded | 호환 재생 기기에 넣어 기록된 내용을 재생할 수 있다. 내용에 따라 지루함을 달래는 데도 쓸 수 있다. | CD 플레이어로 녹음된 소리를 들을 수 있다. 내용에 따라 지루함을 달래는 데도 쓸 수 있다. |
| Base.VHS_Home | compact | 호환 재생 기기에 넣어 기록된 내용을 재생할 수 있다. 내용에 따라 지루함을 달래거나 기술과 제작법을 배우는 데도 쓸 수 있다. 일부 내용은 스트레스를 느끼게 할 수 있다. | VHS 재생 기능이 있는 TV로 녹화된 영상을 볼 수 있다. 내용에 따라 지루함을 달래거나 기술과 제작법을 배우는 데도 쓸 수 있다. 일부 내용은 스트레스를 느끼게 할 수 있다. |
| Base.VHS_Home | expanded | 호환 재생 기기에 넣어 기록된 내용을 재생할 수 있다. 내용에 따라 지루함을 달래거나 기술과 제작법을 배우는 데도 쓸 수 있다. 일부 내용은 스트레스를 느끼게 할 수 있다. | VHS 재생 기능이 있는 TV로 녹화된 영상을 볼 수 있다. 내용에 따라 지루함을 달래거나 기술과 제작법을 배우는 데도 쓸 수 있다. 일부 내용은 스트레스를 느끼게 할 수 있다. |

검토 범위의 전체 ID는 다음과 같다.

- craft_material: `Base.AlarmClock2`, `Base.Aluminum`, `Base.Amplifier`, `Base.BarbedWire`, `Base.BaseballBat`, `Base.BeerEmpty`, `Base.BlowTorch`, `Base.Book`, `Base.Coldpack`, `Base.DenimStrips`, `Base.DenimStripsDirty`, `Base.Doorknob`, `Base.Drawer`, `Base.ElectronicsScrap`, `Base.FishingLine`, `Base.FishingRodBreak`, `Base.Garbagebag`, `Base.Glue`, `Base.Gravelbag`, `Base.GunPowder`, `Base.Hairspray`, `Base.Handle`, `Base.Hinge`, `Base.IronIngot`, `Base.Log`, `Base.Magazine`, `Base.Mattress`, `Base.MetalBar`, `Base.MetalPipe`, `Base.Nails`, `Base.Newspaper`, `Base.Paperclip`, `Base.PetrolBleachBottle`, `Base.PetrolCan`, `Base.PetrolPopBottle`, `Base.Pillow`, `Base.Plank`, `Base.Receiver`, `Base.Remote`, `Base.RippedSheets`, `Base.RippedSheetsDirty`, `Base.Rope`, `Base.Sandbag`, `Base.ScrapMetal`, `Base.SharpedStone`, `Base.Sheet`, `Base.SheetMetal`, `Base.SheetRope`, `Base.SmallSheetMetal`, `Base.Sparklers`, `Base.Stake`, `Base.Stone`, `Base.Tarp`, `Base.Thread`, `Base.Timer`, `Base.TreeBranch`, `Base.Twigs`, `Base.Twine`, `Base.WaterBottleEmpty`, `Base.WaterBottlePetrol`, `Base.WeldingRods`, `Base.WhiskeyEmpty`, `Base.WhiskeyFull`, `Base.WhiskeyPetrol`, `Base.WineEmpty`, `Base.WineEmpty2`, `Base.WinePetrol`, `Base.Wire`, `Base.WoodenStick`, `Radio.RadioReceiver`, `camping.TentPeg`

- repair_material: `Base.AssaultRifle`, `Base.AssaultRifle2`, `Base.DoubleBarrelShotgun`, `Base.DuctTape`, `Base.Glue`, `Base.HuntingRifle`, `Base.Nails`, `Base.Pistol`, `Base.Pistol2`, `Base.Pistol3`, `Base.Revolver`, `Base.Revolver_Long`, `Base.Revolver_Short`, `Base.Scotchtape`, `Base.SheetMetal`, `Base.Shotgun`, `Base.ShotgunSawnoff`, `Base.SmallSheetMetal`, `Base.VarmintRifle`, `Base.Woodglue`

- modification: `Base.Aerosolbomb`, `Base.DuctTape`, `Base.ElectronicsScrap`, `Base.FlameTrap`, `Base.MotionSensor`, `Base.NoiseTrap`, `Base.PipeBomb`, `Base.SmokeBomb`, `Base.TimerCrafted`, `Base.TriggerCrafted`

- clothing_form: `Base.Bag_FannyPackBack`, `Base.Bag_FannyPackFront`, `Base.Bracelet_BangleLeftGold`, `Base.Bracelet_BangleLeftSilver`, `Base.Bracelet_BangleRightGold`, `Base.Bracelet_BangleRightSilver`, `Base.Bracelet_ChainLeftGold`, `Base.Bracelet_ChainLeftSilver`, `Base.Bracelet_ChainRightGold`, `Base.Bracelet_ChainRightSilver`, `Base.Bracelet_LeftFriendshipTINT`, `Base.Bracelet_RightFriendshipTINT`, `Base.Earring_LoopSmall_Gold_Both`, `Base.Earring_LoopSmall_Gold_Top`, `Base.Earring_LoopSmall_Silver_Both`, `Base.Earring_LoopSmall_Silver_Top`, `Base.Glasses_Eyepatch_Left`, `Base.Glasses_Eyepatch_Right`, `Base.Hat_Bandana`, `Base.Hat_BandanaMask`, `Base.Hat_BandanaMaskTINT`, `Base.Hat_BandanaTINT`, `Base.Hat_BandanaTied`, `Base.Hat_BandanaTiedTINT`, `Base.Hat_BaseballCap`, `Base.Hat_BaseballCapArmy`, `Base.Hat_BaseballCapArmy_Reverse`, `Base.Hat_BaseballCapBlue`, `Base.Hat_BaseballCapBlue_Reverse`, `Base.Hat_BaseballCapGreen`, `Base.Hat_BaseballCapGreen_Reverse`, `Base.Hat_BaseballCapKY`, `Base.Hat_BaseballCapKY_Red`, `Base.Hat_BaseballCapKY_Reverse`, `Base.Hat_BaseballCapRed`, `Base.Hat_BaseballCapRed_Reverse`, `Base.Hat_BaseballCap_Reverse`, `Base.HoodieDOWN_WhiteTINT`, `Base.HoodieUP_WhiteTINT`, `Base.Jacket_Padded`, `Base.Jacket_PaddedDOWN`, `Base.PonchoGreen`, `Base.PonchoGreenDOWN`, `Base.PonchoYellow`, `Base.PonchoYellowDOWN`, `Base.Ring_Left_MiddleFinger_Gold`, `Base.Ring_Left_MiddleFinger_GoldDiamond`, `Base.Ring_Left_MiddleFinger_GoldRuby`, `Base.Ring_Left_MiddleFinger_Silver`, `Base.Ring_Left_MiddleFinger_SilverDiamond`, `Base.Ring_Left_RingFinger_Gold`, `Base.Ring_Left_RingFinger_GoldDiamond`, `Base.Ring_Left_RingFinger_GoldRuby`, `Base.Ring_Left_RingFinger_Silver`, `Base.Ring_Left_RingFinger_SilverDiamond`, `Base.Ring_Right_MiddleFinger_Gold`, `Base.Ring_Right_MiddleFinger_GoldDiamond`, `Base.Ring_Right_MiddleFinger_GoldRuby`, `Base.Ring_Right_MiddleFinger_Silver`, `Base.Ring_Right_MiddleFinger_SilverDiamond`, `Base.Ring_Right_RingFinger_Gold`, `Base.Ring_Right_RingFinger_GoldDiamond`, `Base.Ring_Right_RingFinger_GoldRuby`, `Base.Ring_Right_RingFinger_Silver`, `Base.Ring_Right_RingFinger_SilverDiamond`, `Base.WristWatch_Left_ClassicBlack`, `Base.WristWatch_Left_ClassicBrown`, `Base.WristWatch_Left_ClassicGold`, `Base.WristWatch_Left_ClassicMilitary`, `Base.WristWatch_Left_DigitalBlack`, `Base.WristWatch_Left_DigitalDress`, `Base.WristWatch_Left_DigitalRed`, `Base.WristWatch_Right_ClassicBlack`, `Base.WristWatch_Right_ClassicBrown`, `Base.WristWatch_Right_ClassicGold`, `Base.WristWatch_Right_ClassicMilitary`, `Base.WristWatch_Right_DigitalBlack`, `Base.WristWatch_Right_DigitalDress`, `Base.WristWatch_Right_DigitalRed`

- vehicle_installed: `Base.BigGasTank1`, `Base.BigGasTank2`, `Base.BigGasTank3`, `Base.CarBattery1`, `Base.CarBattery2`, `Base.CarBattery3`, `Base.EngineDoor1`, `Base.EngineDoor2`, `Base.EngineDoor3`, `Base.FrontCarDoor1`, `Base.FrontCarDoor2`, `Base.FrontCarDoor3`, `Base.FrontWindow1`, `Base.FrontWindow2`, `Base.FrontWindow3`, `Base.LightBulb`, `Base.ModernBrake1`, `Base.ModernBrake2`, `Base.ModernBrake3`, `Base.ModernCarMuffler1`, `Base.ModernCarMuffler2`, `Base.ModernCarMuffler3`, `Base.ModernSuspension1`, `Base.ModernSuspension2`, `Base.ModernSuspension3`, `Base.ModernTire1`, `Base.ModernTire2`, `Base.ModernTire3`, `Base.NormalBrake1`, `Base.NormalBrake2`, `Base.NormalBrake3`, `Base.NormalCarMuffler1`, `Base.NormalCarMuffler2`, `Base.NormalCarMuffler3`, `Base.NormalCarSeat1`, `Base.NormalCarSeat2`, `Base.NormalCarSeat3`, `Base.NormalGasTank1`, `Base.NormalGasTank2`, `Base.NormalGasTank3`, `Base.NormalSuspension1`, `Base.NormalSuspension2`, `Base.NormalSuspension3`, `Base.NormalTire1`, `Base.NormalTire2`, `Base.NormalTire3`, `Base.OldBrake1`, `Base.OldBrake2`, `Base.OldBrake3`, `Base.OldCarMuffler1`, `Base.OldCarMuffler2`, `Base.OldCarMuffler3`, `Base.OldTire1`, `Base.OldTire2`, `Base.OldTire3`, `Base.RearCarDoor1`, `Base.RearCarDoor2`, `Base.RearCarDoor3`, `Base.RearCarDoorDouble1`, `Base.RearCarDoorDouble2`, `Base.RearCarDoorDouble3`, `Base.RearWindow1`, `Base.RearWindow2`, `Base.RearWindow3`, `Base.RearWindshield1`, `Base.RearWindshield2`, `Base.RearWindshield3`, `Base.SmallGasTank1`, `Base.SmallGasTank2`, `Base.SmallGasTank3`, `Base.TrunkDoor1`, `Base.TrunkDoor2`, `Base.TrunkDoor3`, `Base.Windshield1`, `Base.Windshield2`, `Base.Windshield3`

- lamp_bulb: `Base.LightBulb`, `Base.LightBulbBlue`, `Base.LightBulbCyan`, `Base.LightBulbGreen`, `Base.LightBulbMagenta`, `Base.LightBulbOrange`, `Base.LightBulbPink`, `Base.LightBulbPurple`, `Base.LightBulbRed`, `Base.LightBulbYellow`

- placement: `Base.Mattress`, `Base.Mov_AirConditioner`, `Base.Mov_AntiqueStove`, `Base.Mov_ArcadeMachine1`, `Base.Mov_ArcadeMachine2`, `Base.Mov_BeachChair`, `Base.Mov_BinRound`, `Base.Mov_Birdbath`, `Base.Mov_BlueComfyChair`, `Base.Mov_BluePlasticChair`, `Base.Mov_BlueRattanChair`, `Base.Mov_BrownComfyChair`, `Base.Mov_BrownLowTable`, `Base.Mov_CabinetMedical`, `Base.Mov_CabinetTool`, `Base.Mov_CardboardBox`, `Base.Mov_ChromeSink`, `Base.Mov_CoffeeMaker`, `Base.Mov_ConcreteMixer`, `Base.Mov_CorkBoard`, `Base.Mov_DarkBlueChair`, `Base.Mov_DarkWoodenChair`, `Base.Mov_DegreeDoctor`, `Base.Mov_DegreeSurgeon`, `Base.Mov_DesktopComputer`, `Base.Mov_Doghouse`, `Base.Mov_Espresso`, `Base.Mov_FancyBlackChair`, `Base.Mov_FancyDarkTable`, `Base.Mov_FancyLowTable`, `Base.Mov_FancyTable`, `Base.Mov_FancyToilet`, `Base.Mov_FancyWhiteChair`, `Base.Mov_FitnessContraption`, `Base.Mov_FlagAdmin`, `Base.Mov_FlagUSA`, `Base.Mov_FlagUSALarge`, `Base.Mov_FoldingChair`, `Base.Mov_FridgeMini`, `Base.Mov_GardenGnome`, `Base.Mov_GraveArched`, `Base.Mov_GraveRound`, `Base.Mov_GraveSquare`, `Base.Mov_GraveWorn`, `Base.Mov_GreenChair`, `Base.Mov_GreenComfyChair`, `Base.Mov_GreenOven`, `Base.Mov_GreyChair`, `Base.Mov_GreyComfyChair`, `Base.Mov_GreyOven`, `Base.Mov_HotdogMachine`, `Base.Mov_HuntingTrophy`, `Base.Mov_IndustrialSink`, `Base.Mov_Lamp1`, `Base.Mov_Lamp2`, `Base.Mov_Lamp3`, `Base.Mov_Lamp4`, `Base.Mov_Lamp5`, `Base.Mov_Lamp6`, `Base.Mov_LightConstruction`, `Base.Mov_LightRoundTable`, `Base.Mov_LongTable`, `Base.Mov_Mailbox`, `Base.Mov_MannequinFemale`, `Base.Mov_MannequinMale`, `Base.Mov_MapUSA`, `Base.Mov_MetalLocker`, `Base.Mov_MetalStool`, `Base.Mov_Microphone`, `Base.Mov_Microwave`, `Base.Mov_Microwave2`, `Base.Mov_MirrorLarge`, `Base.Mov_MirrorSmall`, `Base.Mov_MirrorTall`, `Base.Mov_MirrorWood`, `Base.Mov_MobileBloodbag`, `Base.Mov_MobileCounter`, `Base.Mov_ModernOven`, `Base.Mov_NapkinDispenser`, `Base.Mov_OakRoundTable`, `Base.Mov_OfficeChair`, `Base.Mov_OrangeFuton`, `Base.Mov_OrangeModernChair`, `Base.Mov_PaintingBetty`, `Base.Mov_PaintingElisa`, `Base.Mov_PaintingGreen`, `Base.Mov_PaintingLibrary`, `Base.Mov_PalletEmpty`, `Base.Mov_PileOCrepeChair`, `Base.Mov_PinballMachine`, `Base.Mov_PinkFlamingo`, `Base.Mov_PlasticChair`, `Base.Mov_PlasticLowTable`, `Base.Mov_PopcornMachine`, `Base.Mov_PosterDroids`, `Base.Mov_PosterElement`, `Base.Mov_PosterMedical`, `Base.Mov_PosterOmega`, `Base.Mov_PosterPaws`, `Base.Mov_PosterPieBlue`, `Base.Mov_PosterPieGreen`, `Base.Mov_PosterPiePink`, `Base.Mov_PosterPieRed`, `Base.Mov_Projector`, `Base.Mov_PurpleRattanChair`, `Base.Mov_PurpleWoodenChair`, `Base.Mov_RedBBQ`, `Base.Mov_RedChair`, `Base.Mov_RedOven`, `Base.Mov_RedWoodenChair`, `Base.Mov_RoadBarrier`, `Base.Mov_RoadCone`, `Base.Mov_RoadCone2`, `Base.Mov_RoundTable`, `Base.Mov_SatelliteDish`, `Base.Mov_ScaleMedical`, `Base.Mov_ShoppingBaskets`, `Base.Mov_SignArmy`, `Base.Mov_SignCitrus`, `Base.Mov_SignRestricted`, `Base.Mov_SignWarning`, `Base.Mov_SmallTable`, `Base.Mov_SodaMachine`, `Base.Mov_TVCamera`, `Base.Mov_Toaster`, `Base.Mov_TowelDispenser`, `Base.Mov_Urinal`, `Base.Mov_WallClock`, `Base.Mov_WaterDispenser`, `Base.Mov_WhiteComfyChair`, `Base.Mov_WhiteSimpleChair`, `Base.Mov_WhiteSink`, `Base.Mov_WhiteWoodenChair`, `Base.Mov_WoodenChair`, `Base.Mov_WoodenStool`, `Base.Mov_YellowModernChair`, `Base.brokenglass_1_0`, `Base.brokenglass_1_1`, `Base.brokenglass_1_2`, `Base.brokenglass_1_3`

- reading_cap: `Base.Book`, `Base.ComicBook`, `Base.HottieZ`, `Base.Magazine`, `Base.MagazineCrossword1`, `Base.MagazineCrossword2`, `Base.MagazineCrossword3`, `Base.MagazineWordsearch1`, `Base.MagazineWordsearch2`, `Base.MagazineWordsearch3`, `Base.Newspaper`, `Base.TVMagazine`

- media: `Radio.CDplayer`, `Radio.RadioRed`, `Radio.TvBlack`, `Radio.TvWideScreen`


기존 관련 검사 네 개를 한 번 실행하여 `4 passed in 160.24s (0:02:40)`, 종료 코드 `0`을 확인했다. 현재 계약 기대값과 같은 노드 안의 재발 방지 확인만 수정했고, 새 검증 프레임워크는 만들지 않았다. 이전 테스트 실패 로그는 그대로 보존했다.

```powershell
$env:IRIS_SHARED_MENU_VALIDATION='1'
Remove-Item Env:IRIS_MENU_TOOLTIP_CANDIDATE -ErrorAction SilentlyContinue
uv run --project .\Iris\tooling python -I -B -m pytest --noconftest -c .\Iris\tooling\pyproject.toml .\Iris\build\description\v2\tests\test_layer3_composition.py::test_layer3_composition_contract .\Iris\build\description\v2\tests\test_layer3_description_composition.py::test_layer3_description_composition .\Iris\tooling\tests\test_tooltip_t2_projection.py::test_s2_supply_and_owner_integration .\Iris\build\description\v2\tests\test_layer3_product_integration.py::test_product_contract --basetemp .\.tmp\parallel-tests-01 -q -s --tb=short
```

로그: `.tmp/prose/parallel-tests.log`. 검사 안에서 Lua 소스와 staging 388개 구문, Browser/Wiki 소비 모델(폰트 stub), S2 공급, 두 제품 빌드의 바이트 일치, ZIP의 현재 포인터 및 중단·롤백·재진입 복구가 통과했다. 실제 PZ 화면이나 게임 폰트를 관찰한 검증은 아니다.

- descriptions SHA-256: `d0f790ca26e7fefa045760ff9d90357f3b57490a8302c3c6c9c0280d61f92f34`
- blocks SHA-256: `570e5b1d5dad33f2e5accd4e0217f406888937a7ad41667b210c12ea4b94093c`
- product: `l3p-15990417db28ff6a47d43a8bbb57c1ce7f424083f7e1082d40ba64efa96a338d`
- ZIP: `.tmp/menu/run-9q6owye7/p/Iris.zip`
- ZIP SHA-256: `064b09b84906ef192319dfb6c39963a15081c52f9dba1df702df30871a93acb1`

이 결과는 후속 검토용 후보다. 가구별 실제 기능과 독서의 구체 감정 적용은 위에 명시한 근거 보류로 남으며, 전체 설명의 완전한 사실성이나 품질 수락으로 계산하지 않는다. 설치·커밋·푸시·자동화는 수행하지 않았다.


## 2026-09-14 추가 교정: 재료 목적의 문법형과 VHS 깊이

`d0f790ca26e7fefa045760ff9d90357f3b57490a8302c3c6c9c0280d61f92f34` 검토에서 남은 세 유형을 이어받았다. 이미 개선된 착용·용접·차량 교체·장치·CD 목적 규칙은 보존했다.

1. **재료 역할의 중첩 정의문**: “...에 쓰거나 ... 만드는 데 쓰는 재료다”는 동작명 나열과 중첩 수식으로 되돌아간 부분해결이었다. 작업과 제작을 같은 목적 명사형으로 맞췄다. 네 목적 이하는 “수리·개조·제작에 재료로 쓸 수 있다”라는 공통 능력 문장을 사용하고, 더 긴 경우에는 작업군과 제작군 두 문장으로 나눈다. 각 제작 범주마다 완전한 재료 문장을 반복하지 않는다. Log·Glue·ElectronicsScrap뿐 아니라 동일 actions+crafting 조립 경로 전체에 적용했다.
2. **가구의 추상성**: “설치용/설치” 동어반복과 “필요하면” 조건은 제거했다. 그러나 “가구로 놓아 사용할 수 있다”는 확인된 설치 활용만 나타낸다. **설치 활용은 확인됨, 구체 기능 목적 미해결**이다. 이 문구 정리를 기능 목적 또는 문장 추상성의 완전한 해결로 집계하지 않는다. 이미 복원된 present를 일괄 absent로 되돌리지 않았다.
3. **VHS 깊이**: Compact는 영상 감상과 내용에 따른 지루함 완화·기술/제작법 학습, 확인된 스트레스/공포 가능성을 보존한다. Expanded는 VHS 재생 기능이 있는 TV 조건과 세부 효과를 풀어 쓴다. 단순 CD 문장에 억지로 차이를 만들지 않았다.

가구 136개는 선언된 WorldObjectSprite와 Lua 사용처를 대조했다. `scripts/newMoveables.txt`의 선언은 가구 분류와 sprite를 제공하지만 가구별 작동 속성은 제공하지 않는다. 연결 후보는 주로 외형 overlay, 전리품 분포, 디버그/튜토리얼 배치였다. 의미 있어 보이는 연결도 다음과 같이 배치 경로와 구분했다.

- 금속 사물함의 sprite는 `ISBlacksmithMenu.onSmallLocker`(943행)의 `ISWoodenContainer:new`와 연결된다. 해당 클래스는 `isContainer=true`로 별도 건축 객체를 만든다. 반면 이동 아이템의 배치는 `ISMoveableSpriteProps`(1970행)의 `createContainersFromSpriteProperties()`를 사용하므로, 건축 메뉴의 클래스 속성을 이동 아이템의 속성으로 옮기지는 않았다.
- 산업용 싱크 sprite는 튜토리얼의 물병 채우기 대상과 연결되지만, 다시 배치한 가구의 배관 가능 여부는 sprite의 waterPiped 속성에 의존한다. 원본 배치 조건과 재배치 후 기능을 동일시하지 않았다.
- 무덤 sprite 비교는 기존 무덤의 이름·modData와 함께 채워진 상태를 판정한다. 이 비교만으로 휴대 가구 아이템이 매장 기능을 제공한다고 추가하지 않았다. 바비큐 테스트·외형 overlay도 동일하게 실제 아이템 배치 후 기능의 대체 근거로 쓰지 않았다.

공통 배치 코드의 IsoStove/IsoFireplace 분기와 컨테이너 생성 소비까지 확인했으나 해당 아이템 sprite에 부여된 isoType/container/waterPiped 속성 자료를 채택 범위에서 연결하지 못했다. 발견된 `.tiles`는 별도 임시 MoreBuilds 모드의 자료라 원본 아이템 의미로 채택하지 않았다. 이번에는 새로운 기능 사실을 만들지 않았고 blocks 바인딩은 그대로다. 이 보류는 교체 부품의 활용까지 네이티브 효과로 재입증하라는 기준으로 확장하지 않는다.

검수는 재료 제작 71개·수리 재료 20개·장치 개조 10개·배치 140개·매체 3개의 합집합 237개 아이템을 대상으로 KO/EN C/E 948개 표면 전문을 대조했다. 동일 전문을 묶어 한국어 104개·영어 100개 전문군을 읽었고, 변경된 151개 아이템의 KO 두 깊이 전문 34개 군도 확인했다. 변하지 않은 동일 경로 출력도 범위에 포함했다. 전체 2,105개를 재생성했고 최종 변경은 151개 아이템·561개 표면(KO C 151, KO E 136, EN C 138, EN E 136)이다. 각 언어/깊이의 present 1,976, absent 129, failed 0은 유지된다. 생성 로그는 `.tmp/prose/purpose-generation1.log`다. 이 집계는 의미·문장 품질 해결 판정이 아니다.

| 아이템 | 깊이 | 이전 | 현재 |
|---|---|---|---|
| Base.Log | compact | 목공과 건축에 쓰거나 야영 장비 및 숯을 만드는 데 쓰는 재료다. 모아서 묶을 수 있다. 수박을 쪼개는 데 쓸 수 있다. 모닥불 등의 연료로 쓸 수 있다. | 목공과 건축, 야영 장비 제작 및 숯 제작에 재료로 쓸 수 있다. 모아서 묶을 수 있다. 수박을 쪼개는 데 쓸 수 있다. 모닥불 등의 연료로 쓸 수 있다. |
| Base.Log | expanded | 목공과 건축 재료로 쓸 수 있다. 야영 장비를 만드는 재료로 쓸 수 있다. 금속 드럼에서 숯을 만드는 재료로 쓸 수 있다. 모아서 묶을 수 있다. 수박을 쪼개는 데 쓸 수 있다. 모닥불 등의 연료로 쓸 수 있다. | 목공과 건축 재료로 쓸 수 있다. 야영 장비를 만드는 재료로 쓸 수 있다. 금속 드럼에서 숯을 만드는 재료로 쓸 수 있다. 모아서 묶을 수 있다. 수박을 쪼개는 데 쓸 수 있다. 모닥불 등의 연료로 쓸 수 있다. |
| Base.Glue | compact | 무기 수리 및 호환 차량 부품 수리에 쓰거나 전자 기기를 만드는 데 쓰는 재료다. | 무기 수리, 호환 차량 부품 수리 및 전자 기기 제작에 재료로 쓸 수 있다. |
| Base.Glue | expanded | 전자 기기를 만드는 재료로 쓸 수 있다. 무기 및 호환 차량 부품을 수리하는 재료로 쓸 수 있다. | 전자 기기를 만드는 재료로 쓸 수 있다. 무기 및 호환 차량 부품을 수리하는 재료로 쓸 수 있다. |
| Base.ElectronicsScrap | compact | 장치 개조, 조명의 건전지용 개조 및 발전기 수리에 쓰거나 전자 기기, 소음 발생 장치 및 폭발 장치를 만드는 데 쓰는 재료다. | 장치 개조, 조명의 건전지용 개조 및 발전기 수리에 재료로 쓸 수 있다. 전자 기기, 소음 발생 장치 및 폭발 장치 제작에도 쓸 수 있다. |
| Base.ElectronicsScrap | expanded | 장치에 움직임 감지, 시간 지연, 원격 작동 기능을 더하는 재료로 쓸 수 있다. 전자 기기, 소음 발생 장치 및 폭발 장치를 만드는 재료로 쓸 수 있다. 조명을 건전지용으로 개조하는 재료로 쓸 수 있다. 손상된 발전기를 수리하는 재료로 쓸 수 있다. | 장치에 움직임 감지, 시간 지연, 원격 작동 기능을 더하는 재료로 쓸 수 있다. 전자 기기, 소음 발생 장치 및 폭발 장치를 만드는 재료로 쓸 수 있다. 조명을 건전지용으로 개조하는 재료로 쓸 수 있다. 손상된 발전기를 수리하는 재료로 쓸 수 있다. |
| Base.Plank | compact | 골절을 고정하는 부목 재료로 쓸 수 있다. 목공과 건축에 쓰거나 사냥 장비, 야영 장비 및 도구를 만드는 데 쓰는 재료다. 수박을 쪼개는 데 쓸 수 있다. 무기로도 쓸 수 있다. 모닥불 등의 연료로 쓸 수 있다. | 골절을 고정하는 부목 재료로 쓸 수 있다. 목공과 건축, 사냥 장비 제작, 야영 장비 제작 및 도구 제작에 재료로 쓸 수 있다. 수박을 쪼개는 데 쓸 수 있다. 무기로도 쓸 수 있다. 모닥불 등의 연료로 쓸 수 있다. |
| Base.Plank | expanded | 골절을 고정하는 부목 재료로 쓸 수 있다. 목공과 건축 재료로 쓸 수 있다. 사냥 장비, 야영 장비 및 도구를 만드는 재료로 쓸 수 있다. 수박을 쪼개는 데 쓸 수 있다. 무기로 쓸 수 있다. 모닥불 등의 연료로 쓸 수 있다. | 골절을 고정하는 부목 재료로 쓸 수 있다. 목공과 건축 재료로 쓸 수 있다. 사냥 장비, 야영 장비 및 도구를 만드는 재료로 쓸 수 있다. 수박을 쪼개는 데 쓸 수 있다. 무기로 쓸 수 있다. 모닥불 등의 연료로 쓸 수 있다. |
| Base.RippedSheetsDirty | compact | 상처에 감을 수 있다. 감염된 상태로 쓰면 상처를 감염시킬 수 있다. 물로 씻어 깨끗한 붕대 재료로 바꿀 수 있다. 건축에 쓰거나 화염 장치, 연막 장치, 야영 장비, 도구 및 부목을 만드는 데 쓰는 재료다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다. | 상처에 감을 수 있다. 감염된 상태로 쓰면 상처를 감염시킬 수 있다. 물로 씻어 깨끗한 붕대 재료로 바꿀 수 있다. 건축에 재료로 쓸 수 있다. 화염 장치, 연막 장치, 야영 장비, 도구 및 부목 제작에도 쓸 수 있다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다. |
| Base.RippedSheetsDirty | expanded | 상처에 감을 수 있다. 감염된 상태로 쓰면 상처를 감염시킬 수 있다. 물로 씻어 깨끗한 붕대 재료로 바꿀 수 있다. 화염 장치, 연막 장치, 야영 장비, 도구 및 부목을 만드는 재료로 쓸 수 있다. 건축 재료로 쓸 수 있다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다. | 상처에 감을 수 있다. 감염된 상태로 쓰면 상처를 감염시킬 수 있다. 물로 씻어 깨끗한 붕대 재료로 바꿀 수 있다. 화염 장치, 연막 장치, 야영 장비, 도구 및 부목을 만드는 재료로 쓸 수 있다. 건축 재료로 쓸 수 있다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다. |
| Base.Mov_AirConditioner | compact | 설치용 가구로 쓸 수 있다. | 가구로 놓아 사용할 수 있다. |
| Base.Mov_AirConditioner | expanded | 가구로 설치할 수 있으며, 필요하면 다른 곳으로 옮겨 배치할 수 있다. | 가구로 놓아 사용하거나 다른 위치로 옮길 수 있다. |
| Base.Mov_MetalLocker | compact | 설치용 가구로 쓸 수 있다. | 가구로 놓아 사용할 수 있다. |
| Base.Mov_MetalLocker | expanded | 가구로 설치할 수 있으며, 필요하면 다른 곳으로 옮겨 배치할 수 있다. | 가구로 놓아 사용하거나 다른 위치로 옮길 수 있다. |
| Base.VHS_Home | compact | VHS 재생 기능이 있는 TV로 녹화된 영상을 볼 수 있다. 내용에 따라 지루함을 달래거나 기술과 제작법을 배우는 데도 쓸 수 있다. 일부 내용은 스트레스를 느끼게 할 수 있다. | 녹화 영상을 감상하고, 내용에 따라 지루함을 달래거나 기술과 제작법을 배울 수 있다. 일부 내용은 스트레스를 느끼게 할 수 있다. |
| Base.VHS_Home | expanded | VHS 재생 기능이 있는 TV로 녹화된 영상을 볼 수 있다. 내용에 따라 지루함을 달래거나 기술과 제작법을 배우는 데도 쓸 수 있다. 일부 내용은 스트레스를 느끼게 할 수 있다. | VHS 재생 기능이 있는 TV로 녹화된 영상을 볼 수 있다. 내용에 따라 지루함을 달래거나 기술과 제작법을 배우는 데도 쓸 수 있다. 일부 내용은 스트레스를 느끼게 할 수 있다. |
| Base.VHS_Retail | compact | VHS 재생 기능이 있는 TV로 녹화된 영상을 볼 수 있다. 내용에 따라 지루함을 달래거나 기술과 제작법을 배우는 데도 쓸 수 있다. 일부 내용은 스트레스나 공포를 느끼게 할 수 있다. | 녹화 영상을 감상하고, 내용에 따라 지루함을 달래거나 기술과 제작법을 배울 수 있다. 일부 내용은 스트레스나 공포를 느끼게 할 수 있다. |
| Base.VHS_Retail | expanded | VHS 재생 기능이 있는 TV로 녹화된 영상을 볼 수 있다. 내용에 따라 지루함을 달래거나 기술과 제작법을 배우는 데도 쓸 수 있다. 일부 내용은 스트레스나 공포를 느끼게 할 수 있다. | VHS 재생 기능이 있는 TV로 녹화된 영상을 볼 수 있다. 내용에 따라 지루함을 달래거나 기술과 제작법을 배우는 데도 쓸 수 있다. 일부 내용은 스트레스나 공포를 느끼게 할 수 있다. |
| Base.Disc_Retail | compact | CD 플레이어로 녹음된 소리를 들을 수 있다. 내용에 따라 지루함을 달래는 데도 쓸 수 있다. | CD 플레이어로 녹음된 소리를 들을 수 있다. 내용에 따라 지루함을 달래는 데도 쓸 수 있다. |
| Base.Disc_Retail | expanded | CD 플레이어로 녹음된 소리를 들을 수 있다. 내용에 따라 지루함을 달래는 데도 쓸 수 있다. | CD 플레이어로 녹음된 소리를 들을 수 있다. 내용에 따라 지루함을 달래는 데도 쓸 수 있다. |

실제 변경 아이템 전체: `Base.ElectronicsScrap`, `Base.Glue`, `Base.GunPowder`, `Base.Log`, `Base.Mattress`, `Base.MetalPipe`, `Base.Mov_AirConditioner`, `Base.Mov_AntiqueStove`, `Base.Mov_ArcadeMachine1`, `Base.Mov_ArcadeMachine2`, `Base.Mov_BeachChair`, `Base.Mov_BinRound`, `Base.Mov_Birdbath`, `Base.Mov_BlueComfyChair`, `Base.Mov_BluePlasticChair`, `Base.Mov_BlueRattanChair`, `Base.Mov_BrownComfyChair`, `Base.Mov_BrownLowTable`, `Base.Mov_CabinetMedical`, `Base.Mov_CabinetTool`, `Base.Mov_CardboardBox`, `Base.Mov_ChromeSink`, `Base.Mov_CoffeeMaker`, `Base.Mov_ConcreteMixer`, `Base.Mov_CorkBoard`, `Base.Mov_DarkBlueChair`, `Base.Mov_DarkWoodenChair`, `Base.Mov_DegreeDoctor`, `Base.Mov_DegreeSurgeon`, `Base.Mov_DesktopComputer`, `Base.Mov_Doghouse`, `Base.Mov_Espresso`, `Base.Mov_FancyBlackChair`, `Base.Mov_FancyDarkTable`, `Base.Mov_FancyLowTable`, `Base.Mov_FancyTable`, `Base.Mov_FancyToilet`, `Base.Mov_FancyWhiteChair`, `Base.Mov_FitnessContraption`, `Base.Mov_FlagAdmin`, `Base.Mov_FlagUSA`, `Base.Mov_FlagUSALarge`, `Base.Mov_FoldingChair`, `Base.Mov_FridgeMini`, `Base.Mov_GardenGnome`, `Base.Mov_GraveArched`, `Base.Mov_GraveRound`, `Base.Mov_GraveSquare`, `Base.Mov_GraveWorn`, `Base.Mov_GreenChair`, `Base.Mov_GreenComfyChair`, `Base.Mov_GreenOven`, `Base.Mov_GreyChair`, `Base.Mov_GreyComfyChair`, `Base.Mov_GreyOven`, `Base.Mov_HotdogMachine`, `Base.Mov_HuntingTrophy`, `Base.Mov_IndustrialSink`, `Base.Mov_Lamp1`, `Base.Mov_Lamp2`, `Base.Mov_Lamp3`, `Base.Mov_Lamp4`, `Base.Mov_Lamp5`, `Base.Mov_Lamp6`, `Base.Mov_LightConstruction`, `Base.Mov_LightRoundTable`, `Base.Mov_LongTable`, `Base.Mov_Mailbox`, `Base.Mov_MannequinFemale`, `Base.Mov_MannequinMale`, `Base.Mov_MapUSA`, `Base.Mov_MetalLocker`, `Base.Mov_MetalStool`, `Base.Mov_Microphone`, `Base.Mov_Microwave`, `Base.Mov_Microwave2`, `Base.Mov_MirrorLarge`, `Base.Mov_MirrorSmall`, `Base.Mov_MirrorTall`, `Base.Mov_MirrorWood`, `Base.Mov_MobileBloodbag`, `Base.Mov_MobileCounter`, `Base.Mov_ModernOven`, `Base.Mov_NapkinDispenser`, `Base.Mov_OakRoundTable`, `Base.Mov_OfficeChair`, `Base.Mov_OrangeFuton`, `Base.Mov_OrangeModernChair`, `Base.Mov_PaintingBetty`, `Base.Mov_PaintingElisa`, `Base.Mov_PaintingGreen`, `Base.Mov_PaintingLibrary`, `Base.Mov_PalletEmpty`, `Base.Mov_PileOCrepeChair`, `Base.Mov_PinballMachine`, `Base.Mov_PinkFlamingo`, `Base.Mov_PlasticChair`, `Base.Mov_PlasticLowTable`, `Base.Mov_PopcornMachine`, `Base.Mov_PosterDroids`, `Base.Mov_PosterElement`, `Base.Mov_PosterMedical`, `Base.Mov_PosterOmega`, `Base.Mov_PosterPaws`, `Base.Mov_PosterPieBlue`, `Base.Mov_PosterPieGreen`, `Base.Mov_PosterPiePink`, `Base.Mov_PosterPieRed`, `Base.Mov_Projector`, `Base.Mov_PurpleRattanChair`, `Base.Mov_PurpleWoodenChair`, `Base.Mov_RedBBQ`, `Base.Mov_RedChair`, `Base.Mov_RedOven`, `Base.Mov_RedWoodenChair`, `Base.Mov_RoadBarrier`, `Base.Mov_RoadCone`, `Base.Mov_RoadCone2`, `Base.Mov_RoundTable`, `Base.Mov_SatelliteDish`, `Base.Mov_ScaleMedical`, `Base.Mov_ShoppingBaskets`, `Base.Mov_SignArmy`, `Base.Mov_SignCitrus`, `Base.Mov_SignRestricted`, `Base.Mov_SignWarning`, `Base.Mov_SmallTable`, `Base.Mov_SodaMachine`, `Base.Mov_TVCamera`, `Base.Mov_Toaster`, `Base.Mov_TowelDispenser`, `Base.Mov_Urinal`, `Base.Mov_WallClock`, `Base.Mov_WaterDispenser`, `Base.Mov_WhiteComfyChair`, `Base.Mov_WhiteSimpleChair`, `Base.Mov_WhiteSink`, `Base.Mov_WhiteWoodenChair`, `Base.Mov_WoodenChair`, `Base.Mov_WoodenStool`, `Base.Mov_YellowModernChair`, `Base.Nails`, `Base.Plank`, `Base.RippedSheets`, `Base.RippedSheetsDirty`, `Base.Stone`, `Base.TreeBranch`, `Base.Twine`, `Base.VHS_Home`, `Base.VHS_Retail`, `Base.Wire`


이번 변경은 문장 조립과 출력 바인딩에 한정되어 의미 블록 생산 검사를 반복하지 않았다. 설명 계약·S2 공급·제품 통합의 기존 세 노드를 한 번 실행했다. 결과는 `3 passed in 128.77s (0:02:08)`, 종료 코드 `0`이다. 새 검증 프레임워크를 만들지 않았고 이전 실패 로그를 보존했다.

```powershell
$env:IRIS_SHARED_MENU_VALIDATION='1'
Remove-Item Env:IRIS_MENU_TOOLTIP_CANDIDATE -ErrorAction SilentlyContinue
uv run --project .\Iris\tooling python -I -B -m pytest --noconftest -c .\Iris\tooling\pyproject.toml .\Iris\build\description\v2\tests\test_layer3_description_composition.py::test_layer3_description_composition .\Iris\tooling\tests\test_tooltip_t2_projection.py::test_s2_supply_and_owner_integration .\Iris\build\description\v2\tests\test_layer3_product_integration.py::test_product_contract --basetemp .\.tmp\purpose-tests-01 -q -s --tb=short
```

로그 `.tmp/prose/purpose-tests.log`에 Lua 388개 구문, Browser/Wiki 소비(font stub), S2 공급, 제품 두 번 생성 바이트 일치, 패키지/ZIP 포인터 및 중단·롤백·재진입 복구 결과가 남는다. 실제 게임 화면 검증이나 설치는 수행하지 않았다. 두 HTML과 이 보고서는 현재 후보로 갱신했고 역사적 JSON과 r6, 기존 작업 파일은 보존했다.

- descriptions SHA-256: `5c6eb4f49d68d05be0816bb447ccee11598743535ce36930eb8c3b883afde6f1`
- blocks SHA-256(유지): `570e5b1d5dad33f2e5accd4e0217f406888937a7ad41667b210c12ea4b94093c`
- product: `l3p-ad099225984afdd6ca561cfbfcf3baeb55bf9a4eb13bb3f8e4b493f0e457a7a2`
- ZIP: `.tmp/menu/run-f5v12xv2/p/Iris.zip`
- ZIP SHA-256: `3d31b6356bc01aaca3ae63d658e6ebc9f518ba89105da16e66fecc81bb286919`

재료 정의문의 중첩과 VHS 깊이는 위 공통 규칙 및 전문 대조로 교정했다. 가구는 무의미 조건·동어반복만 정리했고 구체 기능 목적은 미해결이다. 이 부분을 문장 품질 전체 해결로 계산하지 않는 후속 검토 후보이며, 설치·커밋·푸시·자동화를 수행하지 않았다.


## 2026-09-14 재료 구 조립 마무리

직전 `5c6eb4f49d68d05be0816bb447ccee11598743535ce36930eb8c3b883afde6f1` 후보의 마지막 반복을 교정했다. 제작 대상 수에 따라 각 대상에 “제작”을 붙이던 분기를 없앴다. 모든 actions+crafting 조합은 작업군의 재료 능력 문장과 제작 대상 전체가 “제작”을 한 번 공유하는 능력 문장으로 구성한다. 복합 작업도 선언된 활동에서 목공·건축·금속 부품 용접을 개별 목적 구로 만들고 마지막 목록에서 한 번 연결한다. 기존 문자열의 접속사를 치환하거나 아이템별 예외를 추가하지 않았다.

해당 병렬 재료 조립 경로 전체 24개 아이템의 한국어 C/E 전문 48표면을 44개 전문군으로 대조했다. 실제 변경은 11개 아이템의 KO Compact 11표면뿐이며 KO Expanded 및 EN 두 깊이의 텍스트는 동일하다. 독립된 제작 대상·의료·연료·무기·기타 활용을 삭제하지 않았다. VHS의 수락된 깊이 차이와 가구 설치 활용/구체 기능 보류는 유지하고 조사도 반복하지 않았다.

기존 설명 조립 계약 노드만 실행하여 `1 passed in 9.00s`, 종료 코드 `0`을 확인했다. 로그 `.tmp/prose/phrases-tests.log`. 근거 블록·S2·제품 패키지 광범위 검사는 반복하지 않았으며 새 ZIP을 생성하지 않았다. 이전 패키지는 이전 후보의 검증 결과다. 현재 텍스트와 입력 해시 바인딩 및 두 HTML만 갱신했다.

```powershell
uv run --project .\Iris\tooling python -I -B -m pytest --noconftest -c .\Iris\tooling\pyproject.toml .\Iris\build\description\v2\tests\test_layer3_description_composition.py::test_layer3_description_composition --basetemp .\.tmp\phrases-tests-01 -q -s --tb=short
```

Descriptions SHA-256: `f4344d51287235a3c7ebb6a99d362b3371dc7f8561985f83ccb7359cb1d78c9d`. Blocks는 기존 `570e5b1d5dad33f2e5accd4e0217f406888937a7ad41667b210c12ea4b94093c` 유지. 아래는 해당 공통 경로 전체의 현재 한국어 C/E 전문이다.

| 아이템 | Compact | Expanded |
|---|---|---|
| Base.Aluminum | 전자 기기, 폭발 장치 및 모자를 만드는 재료로 쓸 수 있다. | 전자 기기, 폭발 장치 및 모자를 만드는 재료로 쓸 수 있다. |
| Base.Amplifier | 전자 기기 및 소음 발생 장치를 만드는 재료로 쓸 수 있다. | 전자 기기 및 소음 발생 장치를 만드는 재료로 쓸 수 있다. |
| Base.DenimStrips | 상처 처치나 의류 수선에 쓸 수 있다. 감염된 재료로 상처를 감으면 감염을 일으킬 수 있다. 화염 장치, 도구 및 부목을 만드는 재료로 쓸 수 있다. | 화상을 씻는 데 쓸 수 있다. 상처에 감을 수 있다. 감염된 상태로 쓰면 상처를 감염시킬 수 있다. 화염 장치, 도구 및 부목을 만드는 재료로 쓸 수 있다. 의류의 구멍을 덧대거나 패딩을 추가할 수 있다. |
| Base.DenimStripsDirty | 상처에 감을 수 있다. 감염된 상태로 쓰면 상처를 감염시킬 수 있다. 물로 씻어 깨끗한 붕대 재료로 바꿀 수 있다. 화염 장치, 도구 및 부목을 만드는 재료로 쓸 수 있다. | 상처에 감을 수 있다. 감염된 상태로 쓰면 상처를 감염시킬 수 있다. 물로 씻어 깨끗한 붕대 재료로 바꿀 수 있다. 화염 장치, 도구 및 부목을 만드는 재료로 쓸 수 있다. |
| Base.DuctTape | 창 부착물 고정, 장치 개조, 무기 수리 및 호환 차량 부품 수리에 재료로 쓸 수 있다. | 창에 부착물을 다는 재료로 쓸 수 있다. 장치에 움직임 감지, 시간 지연, 원격 작동 기능을 더하는 재료로 쓸 수 있다. 무기 및 호환 차량 부품을 수리하는 재료로 쓸 수 있다. |
| Base.ElectronicsScrap | 장치 개조, 조명의 건전지용 개조 및 발전기 수리에 재료로 쓸 수 있다. 전자 기기, 소음 발생 장치 및 폭발 장치 제작에도 쓸 수 있다. | 장치에 움직임 감지, 시간 지연, 원격 작동 기능을 더하는 재료로 쓸 수 있다. 전자 기기, 소음 발생 장치 및 폭발 장치를 만드는 재료로 쓸 수 있다. 조명을 건전지용으로 개조하는 재료로 쓸 수 있다. 손상된 발전기를 수리하는 재료로 쓸 수 있다. |
| Base.Glue | 무기 수리 및 호환 차량 부품 수리에 재료로 쓸 수 있다. 전자 기기 제작에도 쓸 수 있다. | 전자 기기를 만드는 재료로 쓸 수 있다. 무기 및 호환 차량 부품을 수리하는 재료로 쓸 수 있다. |
| Base.GunPowder | 금속 단조에 재료로 쓸 수 있다. 폭발 장치 제작에도 쓸 수 있다. | 폭발 장치를 만들 때 재료로 쓸 수 있다. 금속을 단조할 때 재료로 쓸 수 있다. |
| Base.IronIngot | 금속 부품 용접 및 금속 단조에 재료로 쓸 수 있다. | 금속 부품을 용접하는 재료로 쓸 수 있다. 금속 단조의 재료로 사용할 수 있다. |
| Base.Log | 목공 및 건축에 재료로 쓸 수 있다. 야영 장비 및 숯 제작에도 쓸 수 있다. 모아서 묶을 수 있다. 수박을 쪼개는 데 쓸 수 있다. 모닥불 등의 연료로 쓸 수 있다. | 목공과 건축 재료로 쓸 수 있다. 야영 장비를 만드는 재료로 쓸 수 있다. 금속 드럼에서 숯을 만드는 재료로 쓸 수 있다. 모아서 묶을 수 있다. 수박을 쪼개는 데 쓸 수 있다. 모닥불 등의 연료로 쓸 수 있다. |
| Base.MetalBar | 용접 건축 및 금속 단조에 재료로 쓸 수 있다. 무기로 쓸 수 있다. | 용접 건축 재료로 쓸 수 있다. 문과 창문의 금속 바리케이드에도 재료로 쓸 수 있다. 금속을 단조할 때 재료로 쓸 수 있다. 무기로 쓸 수 있다. |
| Base.MetalPipe | 금속 부품 용접 및 용접 건축에 재료로 쓸 수 있다. 폭발 장치 제작에도 쓸 수 있다. 무기로 쓸 수 있다. | 금속 부품 용접과 건축 재료로 쓸 수 있다. 폭발 장치를 만들 때 재료로 쓸 수 있다. 무기로 쓸 수 있다. |
| Base.Nails | 목공, 건축 및 무기 수리에 재료로 쓸 수 있다. 사냥 장비 및 낚시 장비 제작에도 쓸 수 있다. 모아서 상자로 포장할 수 있다. 위층 창문 등에 탈출용 로프를 고정할 수 있다. | 목공과 건축 재료로 쓸 수 있다. 문과 창문의 판자 바리케이드에도 재료로 쓸 수 있다. 사냥과 낚시 장비를 만드는 재료로 쓸 수 있다. 무기를 수리하는 재료로 쓸 수 있다. 모아서 상자로 포장할 수 있다. 위층 창문 등에 탈출용 로프를 고정할 수 있다. |
| Base.Newspaper | 기분 전환을 위한 읽을거리로 쓸 수 있다. 연막 장치, 야영 장비 및 모자를 만드는 재료로 쓸 수 있다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다. | 기분 전환을 위한 읽을거리로 쓸 수 있다. 연막 장치, 야영 장비 및 모자를 만드는 재료로 쓸 수 있다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다. |
| Base.Plank | 골절을 고정하는 부목 재료로 쓸 수 있다. 목공 및 건축에 재료로 쓸 수 있다. 사냥 장비, 야영 장비 및 도구 제작에도 쓸 수 있다. 수박을 쪼개는 데 쓸 수 있다. 무기로도 쓸 수 있다. 모닥불 등의 연료로 쓸 수 있다. | 골절을 고정하는 부목 재료로 쓸 수 있다. 목공과 건축 재료로 쓸 수 있다. 사냥 장비, 야영 장비 및 도구를 만드는 재료로 쓸 수 있다. 수박을 쪼개는 데 쓸 수 있다. 무기로 쓸 수 있다. 모닥불 등의 연료로 쓸 수 있다. |
| Base.RippedSheets | 상처 처치와 골절 고정에 쓰거나 의류 수선 재료로 쓸 수 있다. 감염된 재료로 상처를 감으면 감염을 일으킬 수 있다. 건축에 재료로 쓸 수 있다. 화염 장치, 연막 장치, 야영 장비 및 도구 제작에도 쓸 수 있다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다. | 화상을 씻는 데 쓸 수 있다. 상처에 감을 수 있다. 소독해서 쓸 수도 있다. 감염된 상태로 쓰면 상처를 감염시킬 수 있다. 골절을 고정하는 부목 재료로 쓸 수 있다. 의류의 구멍을 덧대거나 패딩을 추가할 수 있다. 건축 재료로 쓸 수 있다. 화염 장치, 연막 장치, 야영 장비 및 도구를 만드는 재료로 쓸 수 있다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다. |
| Base.RippedSheetsDirty | 상처에 감을 수 있다. 감염된 상태로 쓰면 상처를 감염시킬 수 있다. 물로 씻어 깨끗한 붕대 재료로 바꿀 수 있다. 건축에 재료로 쓸 수 있다. 화염 장치, 연막 장치, 야영 장비, 도구 및 부목 제작에도 쓸 수 있다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다. | 상처에 감을 수 있다. 감염된 상태로 쓰면 상처를 감염시킬 수 있다. 물로 씻어 깨끗한 붕대 재료로 바꿀 수 있다. 화염 장치, 연막 장치, 야영 장비, 도구 및 부목을 만드는 재료로 쓸 수 있다. 건축 재료로 쓸 수 있다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다. |
| Base.SheetMetal | 금속 부품 용접, 건축 및 호환 차량 부품 수리에 재료로 쓸 수 있다. | 용접 건축 재료로 쓸 수 있다. 문과 창문의 금속 바리케이드에도 재료로 쓸 수 있다. 금속 부품을 용접할 때 재료로 쓸 수 있다. 호환 차량 부품을 수리하는 재료로 쓸 수 있다. |
| Base.SmallSheetMetal | 금속 부품 용접, 용접 건축 및 호환 차량 부품 수리에 재료로 쓸 수 있다. | 용접 건축 재료로 쓸 수 있다. 금속 부품을 용접할 때 재료로 쓸 수 있다. 호환 차량 부품을 수리하는 재료로 쓸 수 있다. |
| Base.Stone | 건축에 재료로 쓸 수 있다. 도구 제작에도 쓸 수 있다. | 건축 재료로 쓸 수 있다. 도구를 만드는 재료로 쓸 수 있다. |
| Base.TreeBranch | 골절을 고정하는 부목 재료로 쓸 수 있다. 목공에 재료로 쓸 수 있다. 사냥 장비 및 도구 제작에도 쓸 수 있다. 나무를 마찰시켜 불을 피우는 데 쓸 수 있다. 모닥불 등의 연료로 쓸 수 있다. | 골절을 고정하는 부목 재료로 쓸 수 있다. 목공 재료로 쓸 수 있다. 사냥 장비 및 도구를 만드는 재료로 쓸 수 있다. 나무를 비벼 모닥불 등에 불을 피우는 데 쓸 수 있다. 모닥불 등의 연료로 쓸 수 있다. |
| Base.Twine | 건축에 재료로 쓸 수 있다. 폭발 장치, 사냥 장비, 낚시 장비 및 도구 제작에도 쓸 수 있다. | 건축 재료로 쓸 수 있다. 폭발 장치, 사냥과 낚시 장비 및 도구를 만드는 재료로 쓸 수 있다. |
| Base.Wire | 용접 건축에 재료로 쓸 수 있다. 사냥 장비 및 낚시 장비 제작에도 쓸 수 있다. | 용접 건축 재료로 쓸 수 있다. 사냥과 낚시 장비를 만드는 재료로 쓸 수 있다. |
| Base.WoodenStick | 골절을 고정하는 부목 재료로 쓸 수 있다. 사냥 장비, 낚시 장비 및 야영 장비를 만드는 재료로 쓸 수 있다. 나무를 마찰시켜 불을 피우는 데 쓸 수 있다. 모닥불 등의 연료로 쓸 수 있다. | 골절을 고정하는 부목 재료로 쓸 수 있다. 사냥과 낚시 장비 및 야영 장비를 만드는 재료로 쓸 수 있다. 나무를 비벼 모닥불 등에 불을 피우는 데 쓸 수 있다. 모닥불 등의 연료로 쓸 수 있다. |


## 2026-09-14 사용 관계·포함 중복 후속 교정

감독 측 전체 4,210개 한국어 표면 평가의 잔존 유형을 이어받았다. f434 후보에서 수락된 병렬 재료 구, VHS 깊이, 착용 역할, 용접 장비 구분과 교체 목적은 다시 설계하지 않았다. 수정은 열쇠/자물쇠, 착용 효과, 조리 도구, 단조 틀·생선 손질·세척, 배관 문형의 공통 경로에 한정한다.

| 결함 | 공통 규칙 변경과 근거 | 적용 범위·검수 판정 |
|---|---|---|
| 열쇠의 작업명 목록과 자명한 조건 꼬리 | Compact는 문 잠금, 구조물 자물쇠 제거, 차량 시동을 동사 구로 구성한다. 일치 관계는 문·자물쇠·차량과 연결한 표현으로 남기고 “대상과 열쇠가 맞아야 한다”라는 후행 설명을 제거했다. | 열쇠 기능 조합 7개. 전부 C/E 전문 대조. 독립된 세 기능 유지. |
| 자물쇠 후속 처리의 공개 필요성 | PADLOCK_USE의 열쇠 생성은 설치 완료 후의 처리 사실로서 효용 설명에서 제외했다. CODE_UNLOCK의 코드 일치→잠금 해제는 설치된 잠금 장치의 실제 기능이므로 유지하되, 제거 명령·새 아이템 생성·원래 물품 복원으로 설명하지 않는다. C는 비밀번호 잠금/해제 목적, E는 잠금 설정과 설정한 번호의 관계를 설명한다. | 자물쇠 2개. 문에는 쓸 수 없다는 실제 적용 제한을 양쪽 깊이에 유지했다. 단순히 후속 처리 문장을 E로 옮긴 변경이 아니다. |
| 착용+효과 포함 중복 | 효과가 이미 착용 조건을 명시하면 일반적인 “착용할 수 있다”를 별도 선행 문장으로 붙이지 않는다. 고유 착용 위치가 있는 경우는 별도 의미이므로 이 제거에 포함하지 않는다. | 장전 속도 효과 2개. 착용 조건, 적용 탄종, 15% 효과와 불쏘시개 활용 유지. |
| 상위 조리+하위 반죽 중복 | 동일 tool 역할의 food_preparation과 반죽 준비를 “반죽 만들기를 비롯한 요리에 도구로 쓸 수 있다”라는 포함 관계로 구성했다. scripts/recipes.txt에는 반죽 외에 Make Gravy(3849 부근), Prepare Omelette(3905 부근), Make Pizza(956 부근)도 도구를 keep 입력으로 사용한다. 따라서 반죽만 남기지 않았다. 개별 요리명/레시피 목록으로 되돌리지 않았다. | 해당 도구 4개. 다른 역할·공개 조건이 있는 조리 경로는 제외. 포크/숟가락의 창 부착 및 무기, 밀대의 무기 활용 보존. |
| 단조 틀의 명사구 | 채택된 metal_forging/tool 관계와 단일 선언 결과를 공유 함수로 문장화한다. 선언된 영어 이름의 Mold/Mould 역할 명칭을 함께 확인한 경우에만 틀로 표현하고, 나머지는 도구로 표현한다. 단일 결과라는 이유만으로 모든 단조 도구를 틀로 추정하지 않는다. | 틀 4개, 관련 단조 도구 경로 전체 대조. 첫 재생성에서 C의 이전 경로가 남은 것을 확인해 C/E가 동일 공통 함수를 사용하도록 재교정했다. 아이템 ID별 규칙 없음. |
| 생선 손질의 동작 생략 | fish_preparation의 ingredient 역할은 손질되는 대상이다. “도구로 손질해 생선살을 얻을 수 있다”로 도구·손질·결과 관계를 명시한다. | 생선 7개. 먹기·덫 미끼 독립 활용 유지. 손질 대상 자체를 손질 도구로 전환하지 않는다. |
| 세척을 결과물 분류 변경으로 표현 | wash_bandaging_material과 해당 세척 결과 관계를 “물로 씻어 다시 쓸 수 있다”로 표현한다. 이미 앞에 있는 상처에 감는 용도를 반복하지 않는다. 원래 깨끗한 결과 관계는 원본 근거와 detail links에 보존한다. | 세척 대상 4개. 상처 감기·감염 위험 및 다른 재료/연료 활용 보존. 세척 대상이 세척 도구로 읽히지 않게 하고 소독 보장·정량 결과를 추가하지 않는다. |
| 배관의 긴 내포 수식어 | 외부 수원을 받는 설비라는 중첩 정의 대신 “실내 설비가 외부 수원을 쓰도록 배관을 연결하는 데 쓸 수 있다”라는 목적과 작업을 연결한다. PLUMBING의 실내 대상/외부 수원 사용 연결 범위를 따른다. | 배관 기능 1개. 실제 물 공급 성공이나 정수 효과를 새로 주장하지 않는다. 무기 활용 유지. |

전체 2,105개를 재생성했다. 관련 기능·활동·역할로 선택한 공통 경로 합집합 36개 아이템의 KO/EN C/E 144표면 전문을 한국어 28군·영어 30군으로 읽었다. 첫 문면 대조에서 틀 Compact 잔존과 세척의 붕대 용도 재반복을 발견해 수정한 뒤 같은 범위 전체를 다시 대조했다. 현재 변경은 모두 이 36개 범위 안이며, 수락된 다른 문면과 과일 음료의 섭취 표현은 변경하지 않았다.

가구의 설치 활용 확인/구체 기능 목적 근거 보류, 독서의 구체 효과 근거 보류는 유지한다. 해당 조사와 삭제/복원을 반복하지 않았고 이를 품질 해결로 집계하지 않는다. 상태 집계는 각 언어/깊이 present 1,976·absent 129·failed 0으로 유지되지만, 이는 문면 검수를 대신하지 않는다.

기존 설명 조립 계약 노드만 실행하여 `1 passed in 9.06s`, 종료 코드 `0`을 확인했다. 로그 `.tmp/prose/utility-tests.log`. 이전 실패 기록은 보존했다. 근거 블록·제품 광범위 검사와 패키징을 반복하지 않았으며 새 검수 프레임워크는 만들지 않았다.

```powershell
uv run --project .\Iris\tooling python -I -B -m pytest --noconftest -c .\Iris\tooling\pyproject.toml .\Iris\build\description\v2\tests\test_layer3_description_composition.py::test_layer3_description_composition --basetemp .\.tmp\utility-tests-01 -q -s --tb=short
```

현재 descriptions SHA-256은 `81114e77b91b36e52afcb897786172c7acd7e080675ad81da4d2a99207b04b04`이다. Blocks는 `570e5b1d5dad33f2e5accd4e0217f406888937a7ad41667b210c12ea4b94093c` 유지. 최신 텍스트의 새 ZIP은 없다. 가장 최근 패키지 `.tmp/menu/run-f5v12xv2/p/Iris.zip`은 이전 5c6eb4 텍스트 후보에 해당하며, 현재 텍스트 검증과 구분한다. 현재 입력 해시 바인딩·두 HTML·보고서를 갱신했으며 설치·worktree·커밋·푸시·자동화는 수행하지 않았다.

아래는 해당 공통 경로 전체의 실제 한국어 전후 C/E 문면이다. 변경되지 않은 관련 도구도 함께 포함했다.

| 아이템 | 깊이 | 이전 | 현재 |
|---|---|---|---|
| Base.223BulletsMold | compact | .223 탄약 단조에 사용할 수 있다. | .223 탄약을 단조할 때 틀로 쓸 수 있다. |
| Base.223BulletsMold | expanded | .223 탄약 단조에 사용할 수 있다. | .223 탄약을 단조할 때 틀로 쓸 수 있다. |
| Base.308BulletsMold | compact | .308 탄약 단조에 사용할 수 있다. | .308 탄약을 단조할 때 틀로 쓸 수 있다. |
| Base.308BulletsMold | expanded | .308 탄약 단조에 사용할 수 있다. | .308 탄약을 단조할 때 틀로 쓸 수 있다. |
| Base.9mmBulletsMold | compact | 9mm 탄약 단조에 사용할 수 있다. | 9mm 탄약을 단조할 때 틀로 쓸 수 있다. |
| Base.9mmBulletsMold | expanded | 9mm 탄약 단조에 사용할 수 있다. | 9mm 탄약을 단조할 때 틀로 쓸 수 있다. |
| Base.AmmoStrap_Bullets | compact | 착용하면 산탄 이외의 탄종을 사용하는 총기의 장전 속도를 15% 높인다. 금속 드럼의 불쏘시개로 쓸 수 있다. | 착용하면 산탄 이외의 탄종을 사용하는 총기의 장전 속도를 15% 높인다. 금속 드럼의 불쏘시개로 쓸 수 있다. |
| Base.AmmoStrap_Bullets | expanded | 착용할 수 있다. 착용하면 산탄 이외의 탄종을 사용하는 총기의 장전 속도를 15% 높인다. 금속 드럼의 불쏘시개로 쓸 수 있다. | 착용하면 산탄 이외의 탄종을 사용하는 총기의 장전 속도를 15% 높인다. 금속 드럼의 불쏘시개로 쓸 수 있다. |
| Base.AmmoStrap_Shells | compact | 착용하면 산탄을 쓰는 총기의 장전 속도를 15% 높인다. 금속 드럼의 불쏘시개로 쓸 수 있다. | 착용하면 산탄을 쓰는 총기의 장전 속도를 15% 높인다. 금속 드럼의 불쏘시개로 쓸 수 있다. |
| Base.AmmoStrap_Shells | expanded | 착용할 수 있다. 착용하면 산탄을 쓰는 총기의 장전 속도를 15% 높인다. 금속 드럼의 불쏘시개로 쓸 수 있다. | 착용하면 산탄을 쓰는 총기의 장전 속도를 15% 높인다. 금속 드럼의 불쏘시개로 쓸 수 있다. |
| Base.BallPeenHammer | compact | 금속을 단조하거나 목재를 가공할 수 있다. 문과 창문의 판자 바리케이드 설치에 쓸 수 있다. 수박을 쪼개는 데 쓸 수 있다. 무기로도 쓸 수 있다. | 금속을 단조하거나 목재를 가공할 수 있다. 문과 창문의 판자 바리케이드 설치에 쓸 수 있다. 수박을 쪼개는 데 쓸 수 있다. 무기로도 쓸 수 있다. |
| Base.BallPeenHammer | expanded | 금속을 단조하는 데 사용할 수 있다. 목공과 건축 작업에 쓸 수 있다. 문과 창문에 판자 바리케이드를 설치할 수 있다. 수박을 쪼개는 데 쓸 수 있다. 무기로 쓸 수 있다. | 금속을 단조하는 데 사용할 수 있다. 목공과 건축 작업에 쓸 수 있다. 문과 창문에 판자 바리케이드를 설치할 수 있다. 수박을 쪼개는 데 쓸 수 있다. 무기로 쓸 수 있다. |
| Base.BandageDirty | compact | 상처에 감을 수 있다. 감염된 상태로 쓰면 상처를 감염시킬 수 있다. 물로 씻어 깨끗한 붕대 재료로 바꿀 수 있다. | 상처에 감을 수 있다. 감염된 상태로 쓰면 상처를 감염시킬 수 있다. 물로 씻어 다시 쓸 수 있다. |
| Base.BandageDirty | expanded | 상처에 감을 수 있다. 감염된 상태로 쓰면 상처를 감염시킬 수 있다. 물로 씻어 깨끗한 붕대 재료로 바꿀 수 있다. | 상처에 감을 수 있다. 감염된 상태로 쓰면 상처를 감염시킬 수 있다. 물로 씻어 다시 쓸 수 있다. |
| Base.Bass | compact | 먹을 수 있다. 덫의 미끼로도 쓸 수 있다. 손질 도구로 생선살을 얻을 수 있다. | 먹을 수 있다. 덫의 미끼로도 쓸 수 있다. 도구로 손질해 생선살을 얻을 수 있다. |
| Base.Bass | expanded | 먹을 수 있다. 덫의 미끼로 쓸 수 있다. 손질 도구로 생선살을 얻을 수 있다. | 먹을 수 있다. 덫의 미끼로 쓸 수 있다. 도구로 손질해 생선살을 얻을 수 있다. |
| Base.CarKey | compact | 문 잠금과 해제, 구조물 자물쇠 제거, 차량 시동에 쓸 수 있으며 대상과 열쇠가 맞아야 한다. | 맞는 문을 잠그거나 잠금을 풀 수 있다. 구조물의 자물쇠를 제거하거나 차량 시동을 걸 수도 있다. |
| Base.CarKey | expanded | 열쇠가 맞는 문을 잠그거나 열 수 있다. 맞는 구조물 자물쇠를 제거할 수 있다. 열쇠가 맞는 차량의 시동을 거는 데 쓸 수 있다. | 열쇠가 맞는 문을 잠그거나 열 수 있다. 맞는 자물쇠를 구조물에서 제거할 수 있다. 열쇠가 맞는 차량의 시동을 거는 데 쓸 수 있다. |
| Base.Catfish | compact | 먹을 수 있다. 덫의 미끼로도 쓸 수 있다. 손질 도구로 생선살을 얻을 수 있다. | 먹을 수 있다. 덫의 미끼로도 쓸 수 있다. 도구로 손질해 생선살을 얻을 수 있다. |
| Base.Catfish | expanded | 먹을 수 있다. 덫의 미끼로 쓸 수 있다. 손질 도구로 생선살을 얻을 수 있다. | 먹을 수 있다. 덫의 미끼로 쓸 수 있다. 도구로 손질해 생선살을 얻을 수 있다. |
| Base.CombinationPadlock | compact | 자물쇠를 달 수 있는 구조물에 비밀번호 잠금을 설정할 수 있다. 문에는 쓸 수 없다. 설치 후 맞는 번호로 제거할 수 있다. | 비밀번호로 구조물을 잠그거나 잠금을 해제할 수 있다. 문에는 쓸 수 없다. |
| Base.CombinationPadlock | expanded | 자물쇠를 달 수 있는 구조물에 비밀번호 잠금을 설정할 수 있다. 문에는 쓸 수 없다. 설치 후 맞는 번호로 제거할 수 있다. | 자물쇠를 달 수 있는 구조물에 비밀번호 잠금을 설정할 수 있다. 설정한 번호로 잠금을 해제할 수 있다. 문에는 쓸 수 없다. |
| Base.Crappie | compact | 먹을 수 있다. 덫의 미끼로도 쓸 수 있다. 손질 도구로 생선살을 얻을 수 있다. | 먹을 수 있다. 덫의 미끼로도 쓸 수 있다. 도구로 손질해 생선살을 얻을 수 있다. |
| Base.Crappie | expanded | 먹을 수 있다. 덫의 미끼로 쓸 수 있다. 손질 도구로 생선살을 얻을 수 있다. | 먹을 수 있다. 덫의 미끼로 쓸 수 있다. 도구로 손질해 생선살을 얻을 수 있다. |
| Base.DenimStripsDirty | compact | 상처에 감을 수 있다. 감염된 상태로 쓰면 상처를 감염시킬 수 있다. 물로 씻어 깨끗한 붕대 재료로 바꿀 수 있다. 화염 장치, 도구 및 부목을 만드는 재료로 쓸 수 있다. | 상처에 감을 수 있다. 감염된 상태로 쓰면 상처를 감염시킬 수 있다. 물로 씻어 다시 쓸 수 있다. 화염 장치, 도구 및 부목을 만드는 재료로 쓸 수 있다. |
| Base.DenimStripsDirty | expanded | 상처에 감을 수 있다. 감염된 상태로 쓰면 상처를 감염시킬 수 있다. 물로 씻어 깨끗한 붕대 재료로 바꿀 수 있다. 화염 장치, 도구 및 부목을 만드는 재료로 쓸 수 있다. | 상처에 감을 수 있다. 감염된 상태로 쓰면 상처를 감염시킬 수 있다. 물로 씻어 다시 쓸 수 있다. 화염 장치, 도구 및 부목을 만드는 재료로 쓸 수 있다. |
| Base.Fork | compact | 요리에 쓸 수 있으며 반죽을 만드는 도구로도 쓸 수 있다. 제작한 창에 부착해 쓸 수 있다. 무기로 쓸 수 있다. | 반죽 만들기를 비롯한 요리에 도구로 쓸 수 있다. 제작한 창에 부착해 쓸 수 있다. 무기로 쓸 수 있다. |
| Base.Fork | expanded | 요리에 쓸 수 있으며 반죽을 만드는 도구로도 쓸 수 있다. 제작한 창에 부착해 쓸 수 있다. 무기로 쓸 수 있다. | 반죽 만들기를 비롯한 요리에 도구로 쓸 수 있다. 제작한 창에 부착해 쓸 수 있다. 무기로 쓸 수 있다. |
| Base.Hammer | compact | 금속을 단조하거나 목재를 가공할 수 있다. 건축 작업에 쓸 수 있다. 문과 창문의 판자 바리케이드 설치와 철거에 쓸 수 있다. 수박을 쪼개는 데 쓸 수 있다. 무기로도 쓸 수 있다. | 금속을 단조하거나 목재를 가공할 수 있다. 건축 작업에 쓸 수 있다. 문과 창문의 판자 바리케이드 설치와 철거에 쓸 수 있다. 수박을 쪼개는 데 쓸 수 있다. 무기로도 쓸 수 있다. |
| Base.Hammer | expanded | 금속을 단조하는 데 사용할 수 있다. 목공과 건축 작업에 쓸 수 있다. 문과 창문의 판자 바리케이드를 설치하거나 철거할 수 있다. 수박을 쪼개는 데 쓸 수 있다. 무기로 쓸 수 있다. | 금속을 단조하는 데 사용할 수 있다. 목공과 건축 작업에 쓸 수 있다. 문과 창문의 판자 바리케이드를 설치하거나 철거할 수 있다. 수박을 쪼개는 데 쓸 수 있다. 무기로 쓸 수 있다. |
| Base.HammerStone | compact | 금속을 단조하거나 목재를 가공할 수 있다. 문과 창문의 판자 바리케이드 설치에 쓸 수 있다. 수박을 쪼개는 데 쓸 수 있다. 무기로도 쓸 수 있다. | 금속을 단조하거나 목재를 가공할 수 있다. 문과 창문의 판자 바리케이드 설치에 쓸 수 있다. 수박을 쪼개는 데 쓸 수 있다. 무기로도 쓸 수 있다. |
| Base.HammerStone | expanded | 금속을 단조하는 데 사용할 수 있다. 목공과 건축 작업에 쓸 수 있다. 문과 창문에 판자 바리케이드를 설치할 수 있다. 수박을 쪼개는 데 쓸 수 있다. 무기로 쓸 수 있다. | 금속을 단조하는 데 사용할 수 있다. 목공과 건축 작업에 쓸 수 있다. 문과 창문에 판자 바리케이드를 설치할 수 있다. 수박을 쪼개는 데 쓸 수 있다. 무기로 쓸 수 있다. |
| Base.Key1 | compact | 문 잠금과 해제, 구조물 자물쇠 제거, 차량 시동에 쓸 수 있으며 대상과 열쇠가 맞아야 한다. | 맞는 문을 잠그거나 잠금을 풀 수 있다. 구조물의 자물쇠를 제거하거나 차량 시동을 걸 수도 있다. |
| Base.Key1 | expanded | 열쇠가 맞는 문을 잠그거나 열 수 있다. 맞는 구조물 자물쇠를 제거할 수 있다. 열쇠가 맞는 차량의 시동을 거는 데 쓸 수 있다. | 열쇠가 맞는 문을 잠그거나 열 수 있다. 맞는 자물쇠를 구조물에서 제거할 수 있다. 열쇠가 맞는 차량의 시동을 거는 데 쓸 수 있다. |
| Base.Key2 | compact | 문 잠금과 해제, 구조물 자물쇠 제거, 차량 시동에 쓸 수 있으며 대상과 열쇠가 맞아야 한다. | 맞는 문을 잠그거나 잠금을 풀 수 있다. 구조물의 자물쇠를 제거하거나 차량 시동을 걸 수도 있다. |
| Base.Key2 | expanded | 열쇠가 맞는 문을 잠그거나 열 수 있다. 맞는 구조물 자물쇠를 제거할 수 있다. 열쇠가 맞는 차량의 시동을 거는 데 쓸 수 있다. | 열쇠가 맞는 문을 잠그거나 열 수 있다. 맞는 자물쇠를 구조물에서 제거할 수 있다. 열쇠가 맞는 차량의 시동을 거는 데 쓸 수 있다. |
| Base.Key3 | compact | 문 잠금과 해제, 구조물 자물쇠 제거, 차량 시동에 쓸 수 있으며 대상과 열쇠가 맞아야 한다. | 맞는 문을 잠그거나 잠금을 풀 수 있다. 구조물의 자물쇠를 제거하거나 차량 시동을 걸 수도 있다. |
| Base.Key3 | expanded | 열쇠가 맞는 문을 잠그거나 열 수 있다. 맞는 구조물 자물쇠를 제거할 수 있다. 열쇠가 맞는 차량의 시동을 거는 데 쓸 수 있다. | 열쇠가 맞는 문을 잠그거나 열 수 있다. 맞는 자물쇠를 구조물에서 제거할 수 있다. 열쇠가 맞는 차량의 시동을 거는 데 쓸 수 있다. |
| Base.Key4 | compact | 문 잠금과 해제, 구조물 자물쇠 제거, 차량 시동에 쓸 수 있으며 대상과 열쇠가 맞아야 한다. | 맞는 문을 잠그거나 잠금을 풀 수 있다. 구조물의 자물쇠를 제거하거나 차량 시동을 걸 수도 있다. |
| Base.Key4 | expanded | 열쇠가 맞는 문을 잠그거나 열 수 있다. 맞는 구조물 자물쇠를 제거할 수 있다. 열쇠가 맞는 차량의 시동을 거는 데 쓸 수 있다. | 열쇠가 맞는 문을 잠그거나 열 수 있다. 맞는 자물쇠를 구조물에서 제거할 수 있다. 열쇠가 맞는 차량의 시동을 거는 데 쓸 수 있다. |
| Base.Key5 | compact | 문 잠금과 해제, 구조물 자물쇠 제거, 차량 시동에 쓸 수 있으며 대상과 열쇠가 맞아야 한다. | 맞는 문을 잠그거나 잠금을 풀 수 있다. 구조물의 자물쇠를 제거하거나 차량 시동을 걸 수도 있다. |
| Base.Key5 | expanded | 열쇠가 맞는 문을 잠그거나 열 수 있다. 맞는 구조물 자물쇠를 제거할 수 있다. 열쇠가 맞는 차량의 시동을 거는 데 쓸 수 있다. | 열쇠가 맞는 문을 잠그거나 열 수 있다. 맞는 자물쇠를 구조물에서 제거할 수 있다. 열쇠가 맞는 차량의 시동을 거는 데 쓸 수 있다. |
| Base.KeyPadlock | compact | 문 잠금과 해제, 구조물 자물쇠 제거, 차량 시동에 쓸 수 있으며 대상과 열쇠가 맞아야 한다. | 맞는 문을 잠그거나 잠금을 풀 수 있다. 구조물의 자물쇠를 제거하거나 차량 시동을 걸 수도 있다. |
| Base.KeyPadlock | expanded | 열쇠가 맞는 문을 잠그거나 열 수 있다. 맞는 구조물 자물쇠를 제거할 수 있다. 열쇠가 맞는 차량의 시동을 거는 데 쓸 수 있다. | 열쇠가 맞는 문을 잠그거나 열 수 있다. 맞는 자물쇠를 구조물에서 제거할 수 있다. 열쇠가 맞는 차량의 시동을 거는 데 쓸 수 있다. |
| Base.LeatherStripsDirty | compact | 상처에 감을 수 있다. 감염된 상태로 쓰면 상처를 감염시킬 수 있다. 물로 씻어 깨끗한 붕대 재료로 바꿀 수 있다. | 상처에 감을 수 있다. 감염된 상태로 쓰면 상처를 감염시킬 수 있다. 물로 씻어 다시 쓸 수 있다. |
| Base.LeatherStripsDirty | expanded | 상처에 감을 수 있다. 감염된 상태로 쓰면 상처를 감염시킬 수 있다. 물로 씻어 깨끗한 붕대 재료로 바꿀 수 있다. | 상처에 감을 수 있다. 감염된 상태로 쓰면 상처를 감염시킬 수 있다. 물로 씻어 다시 쓸 수 있다. |
| Base.Padlock | compact | 자물쇠를 달 수 있는 구조물을 잠글 수 있다. 문에는 쓸 수 없으며, 설치하면 열쇠를 얻는다. | 자물쇠를 달 수 있는 구조물을 잠글 수 있다. 문에는 쓸 수 없다. |
| Base.Padlock | expanded | 자물쇠를 달 수 있는 구조물을 잠글 수 있다. 문에는 쓸 수 없으며, 설치하면 열쇠를 얻는다. | 자물쇠를 달 수 있는 구조물을 잠글 수 있다. 문에는 쓸 수 없다. |
| Base.Panfish | compact | 먹을 수 있다. 덫의 미끼로도 쓸 수 있다. 손질 도구로 생선살을 얻을 수 있다. | 먹을 수 있다. 덫의 미끼로도 쓸 수 있다. 도구로 손질해 생선살을 얻을 수 있다. |
| Base.Panfish | expanded | 먹을 수 있다. 덫의 미끼로 쓸 수 있다. 손질 도구로 생선살을 얻을 수 있다. | 먹을 수 있다. 덫의 미끼로 쓸 수 있다. 도구로 손질해 생선살을 얻을 수 있다. |
| Base.Perch | compact | 먹을 수 있다. 덫의 미끼로도 쓸 수 있다. 손질 도구로 생선살을 얻을 수 있다. | 먹을 수 있다. 덫의 미끼로도 쓸 수 있다. 도구로 손질해 생선살을 얻을 수 있다. |
| Base.Perch | expanded | 먹을 수 있다. 덫의 미끼로 쓸 수 있다. 손질 도구로 생선살을 얻을 수 있다. | 먹을 수 있다. 덫의 미끼로 쓸 수 있다. 도구로 손질해 생선살을 얻을 수 있다. |
| Base.Pike | compact | 먹을 수 있다. 덫의 미끼로도 쓸 수 있다. 손질 도구로 생선살을 얻을 수 있다. | 먹을 수 있다. 덫의 미끼로도 쓸 수 있다. 도구로 손질해 생선살을 얻을 수 있다. |
| Base.Pike | expanded | 먹을 수 있다. 덫의 미끼로 쓸 수 있다. 손질 도구로 생선살을 얻을 수 있다. | 먹을 수 있다. 덫의 미끼로 쓸 수 있다. 도구로 손질해 생선살을 얻을 수 있다. |
| Base.PipeWrench | compact | 외부 수원을 받을 수 있는 실내 설비의 배관을 연결할 수 있다. 무기로 쓸 수 있다. | 실내 설비가 외부 수원을 쓰도록 배관을 연결하는 데 쓸 수 있다. 무기로 쓸 수 있다. |
| Base.PipeWrench | expanded | 외부 수원을 받을 수 있는 실내 설비의 배관을 연결할 수 있다. 무기로 쓸 수 있다. | 실내 설비가 외부 수원을 쓰도록 배관을 연결하는 데 쓸 수 있다. 무기로 쓸 수 있다. |
| Base.Plank | compact | 골절을 고정하는 부목 재료로 쓸 수 있다. 목공 및 건축에 재료로 쓸 수 있다. 사냥 장비, 야영 장비 및 도구 제작에도 쓸 수 있다. 수박을 쪼개는 데 쓸 수 있다. 무기로도 쓸 수 있다. 모닥불 등의 연료로 쓸 수 있다. | 골절을 고정하는 부목 재료로 쓸 수 있다. 목공 및 건축에 재료로 쓸 수 있다. 사냥 장비, 야영 장비 및 도구 제작에도 쓸 수 있다. 수박을 쪼개는 데 쓸 수 있다. 무기로도 쓸 수 있다. 모닥불 등의 연료로 쓸 수 있다. |
| Base.Plank | expanded | 골절을 고정하는 부목 재료로 쓸 수 있다. 목공과 건축 재료로 쓸 수 있다. 사냥 장비, 야영 장비 및 도구를 만드는 재료로 쓸 수 있다. 수박을 쪼개는 데 쓸 수 있다. 무기로 쓸 수 있다. 모닥불 등의 연료로 쓸 수 있다. | 골절을 고정하는 부목 재료로 쓸 수 있다. 목공과 건축 재료로 쓸 수 있다. 사냥 장비, 야영 장비 및 도구를 만드는 재료로 쓸 수 있다. 수박을 쪼개는 데 쓸 수 있다. 무기로 쓸 수 있다. 모닥불 등의 연료로 쓸 수 있다. |
| Base.RippedSheetsDirty | compact | 상처에 감을 수 있다. 감염된 상태로 쓰면 상처를 감염시킬 수 있다. 물로 씻어 깨끗한 붕대 재료로 바꿀 수 있다. 건축에 재료로 쓸 수 있다. 화염 장치, 연막 장치, 야영 장비, 도구 및 부목 제작에도 쓸 수 있다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다. | 상처에 감을 수 있다. 감염된 상태로 쓰면 상처를 감염시킬 수 있다. 물로 씻어 다시 쓸 수 있다. 건축에 재료로 쓸 수 있다. 화염 장치, 연막 장치, 야영 장비, 도구 및 부목 제작에도 쓸 수 있다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다. |
| Base.RippedSheetsDirty | expanded | 상처에 감을 수 있다. 감염된 상태로 쓰면 상처를 감염시킬 수 있다. 물로 씻어 깨끗한 붕대 재료로 바꿀 수 있다. 화염 장치, 연막 장치, 야영 장비, 도구 및 부목을 만드는 재료로 쓸 수 있다. 건축 재료로 쓸 수 있다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다. | 상처에 감을 수 있다. 감염된 상태로 쓰면 상처를 감염시킬 수 있다. 물로 씻어 다시 쓸 수 있다. 화염 장치, 연막 장치, 야영 장비, 도구 및 부목을 만드는 재료로 쓸 수 있다. 건축 재료로 쓸 수 있다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다. |
| Base.RollingPin | compact | 요리에 쓸 수 있으며 반죽을 만드는 도구로도 쓸 수 있다. 무기로 쓸 수 있다. | 반죽 만들기를 비롯한 요리에 도구로 쓸 수 있다. 무기로 쓸 수 있다. |
| Base.RollingPin | expanded | 요리에 쓸 수 있으며 반죽을 만드는 도구로도 쓸 수 있다. 무기로 쓸 수 있다. | 반죽 만들기를 비롯한 요리에 도구로 쓸 수 있다. 무기로 쓸 수 있다. |
| Base.ShotgunShellsMold | compact | 산탄총 탄약 단조에 사용할 수 있다. | 산탄총 탄약을 단조할 때 틀로 쓸 수 있다. |
| Base.ShotgunShellsMold | expanded | 산탄총 탄약 단조에 사용할 수 있다. | 산탄총 탄약을 단조할 때 틀로 쓸 수 있다. |
| Base.Spatula | compact | 요리에 쓸 수 있으며 반죽을 만드는 도구로도 쓸 수 있다. | 반죽 만들기를 비롯한 요리에 도구로 쓸 수 있다. |
| Base.Spatula | expanded | 요리에 쓸 수 있으며 반죽을 만드는 도구로도 쓸 수 있다. | 반죽 만들기를 비롯한 요리에 도구로 쓸 수 있다. |
| Base.Spoon | compact | 요리에 쓸 수 있으며 반죽을 만드는 도구로도 쓸 수 있다. 제작한 창에 부착해 쓸 수 있다. 무기로 쓸 수 있다. | 반죽 만들기를 비롯한 요리에 도구로 쓸 수 있다. 제작한 창에 부착해 쓸 수 있다. 무기로 쓸 수 있다. |
| Base.Spoon | expanded | 요리에 쓸 수 있으며 반죽을 만드는 도구로도 쓸 수 있다. 제작한 창에 부착해 쓸 수 있다. 무기로 쓸 수 있다. | 반죽 만들기를 비롯한 요리에 도구로 쓸 수 있다. 제작한 창에 부착해 쓸 수 있다. 무기로 쓸 수 있다. |
| Base.Tongs | compact | 금속을 단조하는 데 사용할 수 있다. | 금속을 단조하는 데 사용할 수 있다. |
| Base.Tongs | expanded | 금속을 단조하는 데 사용할 수 있다. | 금속을 단조하는 데 사용할 수 있다. |
| Base.Trout | compact | 먹을 수 있다. 덫의 미끼로도 쓸 수 있다. 손질 도구로 생선살을 얻을 수 있다. | 먹을 수 있다. 덫의 미끼로도 쓸 수 있다. 도구로 손질해 생선살을 얻을 수 있다. |
| Base.Trout | expanded | 먹을 수 있다. 덫의 미끼로 쓸 수 있다. 손질 도구로 생선살을 얻을 수 있다. | 먹을 수 있다. 덫의 미끼로 쓸 수 있다. 도구로 손질해 생선살을 얻을 수 있다. |

실제 변경: 31개 아이템, 96개 표면. {'ko/compact': 29, 'ko/expanded': 31, 'en/compact': 17, 'en/expanded': 19}


## 2026-09-14 소비 위험 선택·총기 부착 목적·운동 깊이 후속 교정

81114e 후보에 대한 감독의 전체 한국어 문면 검수를 이어받았다. 이전 수락된 재료 조립, VHS 깊이, 열쇠/자물쇠, 조리 도구·틀·생선·세척·배관은 유지했다.

### 공통 규칙과 원본 근거

- 소비: recovery_relations의 선언 source_traits에 충돌 없는 Poison을 전달하고 description_composition_uses.prepare에서 선택한다. Poison=true이고 채택된 식중독 위험 해석이 없는 경우 eat_food/consume_edible_food/drink_food_contents dispatch만으로 중립적 섭취 효용을 공개하지 않는다. 아이템 ID 예외가 아니다. scripts 전체의 Poison=true 선언은 items_food.txt:2868의 한 항목이며 현재 영향도 Bleach 한 개다. recovery_migration.py의 기존 소비 위험 보류(2511 부근)는 유지했다. character:Eat 위임만으로 독성 결과나 용량을 계산하지 않았다. 소비 fact ref와 미확정 원인은 internal_uses에 남고, 독립된 혈흔 청소 기능은 공개된다. 다른 음식이나 이미 채택된 조건부 위험 해석을 삭제하지 않았다.
- 부착물: recovery_sources.supplement_attachment_purposes에서 원본 아이템 선언, 기존 attach_weapon_part의 관측 근거, 원본 Tooltip_EN.txt:88–96/162의 명시 목적을 결합했다. 툴팁 키와 정확한 원문, 대응 modifier의 방향을 함께 확인한다. ISUpgradeWeapon:perform(35–38)의 attachWeaponPart와 ISRemoveWeaponUpgrade:perform(26–27)의 detachWeaponPart는 실제 장착/분리 관계의 근거다. 동일 원본 선언을 여러 owner가 관측한 경우 source path/hash/span/원문으로 묶고 서로 다른 선언이나 충돌은 채택하지 않는다. 첫 생성에서 이 중복 관측 때문에 목적이 합류하지 않은 것을 실제 문면으로 발견하고 재교정했다.
- 부착물 14개 전체를 읽었다. 명시 목적이 있는 12개는 C에서 목적을 앞세우고 E에서는 같은 목적 뒤에 드라이버 장착/분리 절차를 둔다. 장전 시간, 사거리, 휴대 무게 부담, 정확도, 반동/발사 지연, 조준 속도, 산탄 퍼짐/피해 방향을 원문 범위대로 표현했다. 조준경의 근거리 정확도 저하와 Improved choke의 피해 감소는 C/E 모두 남긴다. 새 규칙 declared_attachment_purpose는 12개 사실을 추가하며 전체 semantic correction 사실은 76→88이다. 아이템 이름으로 목적을 추정하지 않는다.
- 운동: 같은 weight exercise 역할에 해당하는 두 운동을 C에서 중량 운동으로 묶는다. 문자 수 기준이 아니다. E는 바이셉스 컬·덤벨 프레스 두 동작을 유지하고 양쪽 깊이의 무기 활용도 보존한다. 같은 역할의 BarBell은 한 가지 운동이라 문면이 바뀌지 않았다.

### 근거 보류

Bayonnet와 GunLight 2개는 **HOLD: 구체 부착 목적 미확인**이다. 채택된 장착/분리 기능은 유지하지만 선언에 해당 목적 툴팁이 없으므로 성능 향상, 총검 공격, 조명 용도를 이름이나 modifier 수치만으로 채우지 않는다. 12개의 명시 목적도 네이티브 재계산의 정량 결과·실게임 성능 검증을 의미하지 않는다. Bleach의 네이티브 독성 결과/용량 해석은 **HOLD**이며 중립 소비 노출을 막은 것으로 독성 연구가 완료됐다고 집계하지 않는다. 기존 가구 구체 기능 및 독서 구체 효과 보류는 유지하고 재조사하지 않았다.

### 검수와 검증

전체 2,105개 재생성 후 관련 합집합 17개(부착물 14, 운동 도구 2, 독성 선언 소비 1)의 KO/EN C/E 68표면 전후 전문을 읽었다. 최초 생성과 수정 후 생성의 실제 문면을 대조했다. 전체 변경은 이 범위 안의 14개·54표면(KO C14/E13, EN C14/E13)이며 나머지 2,091개 문면은 이전 후보와 같다. 각 언어/깊이 present 1,976, absent 129, failed 0 유지.

기존 근거 조립 및 설명 조립 계약 노드만 실행했다. `2 passed in 29.33s`, 종료 코드 `0`, 로그 `.tmp/prose/supplied-tests.log`. 근거 추가 범위와 출처, 소비 사실의 내부 보존, 목적/절차 깊이, 불리한 효과 및 운동 세부 보존을 기존 검사에 연결했다. 제품·S2·ZIP 검증은 반복하지 않았다.

```powershell
uv run --project .\Iris\tooling python -I -B -m pytest --noconftest -c .\Iris\tooling\pyproject.toml .\Iris\build\description\v2\tests\test_layer3_composition.py::test_layer3_composition_contract .\Iris\build\description\v2\tests\test_layer3_description_composition.py::test_layer3_description_composition --basetemp .\.tmp\supplied-tests-01 -q -s --tb=short
```

Descriptions SHA-256: `0347b8a8937b1b69311be8476c57510a65b6dd849e0a606b6fc3835e1c80f492`. Blocks SHA-256: `2dec826b217062da7ee8ba5276312ad9b3fa2e43cbb2db303d7c1fd7c481ea2a`. 현재 입력 바인딩과 두 HTML을 갱신했다. 최신 텍스트의 새 ZIP은 없다. 기존 `.tmp/menu/run-f5v12xv2/p/Iris.zip`은 5c6eb4 후보이며 이번 텍스트 검증과 구분한다. 설치·worktree·커밋·푸시·자동화 및 외부 조사는 수행하지 않았다.

아래는 관련 17개 전체의 실제 한국어 전후 C/E 문면이다.

| 아이템 | 깊이 | 이전 | 현재 |
|---|---|---|---|
| Base.AmmoStraps | compact | 드라이버로 호환 총기에 장착하거나 떼어 회수할 수 있다. | 호환 총기의 장전 시간을 줄이는 부착물로 쓸 수 있다. |
| Base.AmmoStraps | expanded | 드라이버로 호환 총기에 장착하거나 떼어 회수할 수 있다. | 호환 총기의 장전 시간을 줄이는 부착물로 쓸 수 있다. 드라이버로 호환 총기에 장착하거나 떼어 회수할 수 있다. |
| Base.BarBell | compact | 바벨 컬 운동에 사용할 수 있다. 무기로 쓸 수 있다. | 바벨 컬 운동에 사용할 수 있다. 무기로 쓸 수 있다. |
| Base.BarBell | expanded | 바벨 컬 운동에 사용할 수 있다. 무기로 쓸 수 있다. | 바벨 컬 운동에 사용할 수 있다. 무기로 쓸 수 있다. |
| Base.Bayonnet | compact | 드라이버로 호환 총기에 장착하거나 떼어 회수할 수 있다. | 드라이버로 호환 총기에 장착하거나 떼어 회수할 수 있다. |
| Base.Bayonnet | expanded | 드라이버로 호환 총기에 장착하거나 떼어 회수할 수 있다. | 드라이버로 호환 총기에 장착하거나 떼어 회수할 수 있다. |
| Base.Bleach | compact | 바닥 혈흔을 지울 수 있다. 마실 수 있다. | 바닥 혈흔을 지울 수 있다. |
| Base.Bleach | expanded | 바닥 혈흔을 지울 수 있다. 마실 수 있다. | 바닥 혈흔을 지울 수 있다. |
| Base.ChokeTubeFull | compact | 드라이버로 호환 총기에 장착하거나 떼어 회수할 수 있다. | 호환 산탄총의 산탄 퍼짐을 좁히고 피해를 높이는 부착물로 쓸 수 있다. |
| Base.ChokeTubeFull | expanded | 드라이버로 호환 총기에 장착하거나 떼어 회수할 수 있다. | 호환 산탄총의 산탄 퍼짐을 좁히고 피해를 높이는 부착물로 쓸 수 있다. 드라이버로 호환 총기에 장착하거나 떼어 회수할 수 있다. |
| Base.ChokeTubeImproved | compact | 드라이버로 호환 총기에 장착하거나 떼어 회수할 수 있다. | 호환 산탄총의 산탄 퍼짐을 넓히는 부착물로 쓸 수 있다. 피해는 줄어든다. |
| Base.ChokeTubeImproved | expanded | 드라이버로 호환 총기에 장착하거나 떼어 회수할 수 있다. | 호환 산탄총의 산탄 퍼짐을 넓히는 부착물로 쓸 수 있다. 피해는 줄어든다. 드라이버로 호환 총기에 장착하거나 떼어 회수할 수 있다. |
| Base.DumbBell | compact | 바이셉스 컬 운동에 사용할 수 있다. 덤벨 프레스 운동에 사용할 수 있다. 무기로 쓸 수 있다. | 중량 운동에 쓸 수 있다. 무기로 쓸 수 있다. |
| Base.DumbBell | expanded | 바이셉스 컬 운동에 사용할 수 있다. 덤벨 프레스 운동에 사용할 수 있다. 무기로 쓸 수 있다. | 바이셉스 컬 운동에 사용할 수 있다. 덤벨 프레스 운동에 사용할 수 있다. 무기로 쓸 수 있다. |
| Base.FiberglassStock | compact | 드라이버로 호환 총기에 장착하거나 떼어 회수할 수 있다. | 호환 총기의 휴대 무게 부담을 줄이고 정확도를 높이는 부착물로 쓸 수 있다. |
| Base.FiberglassStock | expanded | 드라이버로 호환 총기에 장착하거나 떼어 회수할 수 있다. | 호환 총기의 휴대 무게 부담을 줄이고 정확도를 높이는 부착물로 쓸 수 있다. 드라이버로 호환 총기에 장착하거나 떼어 회수할 수 있다. |
| Base.GunLight | compact | 드라이버로 호환 총기에 장착하거나 떼어 회수할 수 있다. | 드라이버로 호환 총기에 장착하거나 떼어 회수할 수 있다. |
| Base.GunLight | expanded | 드라이버로 호환 총기에 장착하거나 떼어 회수할 수 있다. | 드라이버로 호환 총기에 장착하거나 떼어 회수할 수 있다. |
| Base.IronSight | compact | 드라이버로 호환 총기에 장착하거나 떼어 회수할 수 있다. | 호환 총기의 최대 사거리를 늘리는 부착물로 쓸 수 있다. |
| Base.IronSight | expanded | 드라이버로 호환 총기에 장착하거나 떼어 회수할 수 있다. | 호환 총기의 최대 사거리를 늘리는 부착물로 쓸 수 있다. 드라이버로 호환 총기에 장착하거나 떼어 회수할 수 있다. |
| Base.Laser | compact | 드라이버로 호환 총기에 장착하거나 떼어 회수할 수 있다. | 호환 총기의 정확도를 높이는 부착물로 쓸 수 있다. |
| Base.Laser | expanded | 드라이버로 호환 총기에 장착하거나 떼어 회수할 수 있다. | 호환 총기의 정확도를 높이는 부착물로 쓸 수 있다. 드라이버로 호환 총기에 장착하거나 떼어 회수할 수 있다. |
| Base.RecoilPad | compact | 드라이버로 호환 총기에 장착하거나 떼어 회수할 수 있다. | 호환 총기의 반동과 다음 발사까지의 지연을 줄이는 부착물로 쓸 수 있다. |
| Base.RecoilPad | expanded | 드라이버로 호환 총기에 장착하거나 떼어 회수할 수 있다. | 호환 총기의 반동과 다음 발사까지의 지연을 줄이는 부착물로 쓸 수 있다. 드라이버로 호환 총기에 장착하거나 떼어 회수할 수 있다. |
| Base.RedDot | compact | 드라이버로 호환 총기에 장착하거나 떼어 회수할 수 있다. | 호환 총기의 조준 속도를 높이는 부착물로 쓸 수 있다. |
| Base.RedDot | expanded | 드라이버로 호환 총기에 장착하거나 떼어 회수할 수 있다. | 호환 총기의 조준 속도를 높이는 부착물로 쓸 수 있다. 드라이버로 호환 총기에 장착하거나 떼어 회수할 수 있다. |
| Base.Sling | compact | 드라이버로 호환 총기에 장착하거나 떼어 회수할 수 있다. | 호환 총기를 휴대할 때 무게 부담을 줄이는 부착물로 쓸 수 있다. |
| Base.Sling | expanded | 드라이버로 호환 총기에 장착하거나 떼어 회수할 수 있다. | 호환 총기를 휴대할 때 무게 부담을 줄이는 부착물로 쓸 수 있다. 드라이버로 호환 총기에 장착하거나 떼어 회수할 수 있다. |
| Base.x2Scope | compact | 드라이버로 호환 총기에 장착하거나 떼어 회수할 수 있다. | 호환 총기의 최대 사거리를 늘리는 부착물로 쓸 수 있다. 근거리 정확도는 낮아진다. |
| Base.x2Scope | expanded | 드라이버로 호환 총기에 장착하거나 떼어 회수할 수 있다. | 호환 총기의 최대 사거리를 늘리는 부착물로 쓸 수 있다. 근거리 정확도는 낮아진다. 드라이버로 호환 총기에 장착하거나 떼어 회수할 수 있다. |
| Base.x4Scope | compact | 드라이버로 호환 총기에 장착하거나 떼어 회수할 수 있다. | 호환 총기의 최대 사거리를 늘리는 부착물로 쓸 수 있다. 근거리 정확도는 낮아진다. |
| Base.x4Scope | expanded | 드라이버로 호환 총기에 장착하거나 떼어 회수할 수 있다. | 호환 총기의 최대 사거리를 늘리는 부착물로 쓸 수 있다. 근거리 정확도는 낮아진다. 드라이버로 호환 총기에 장착하거나 떼어 회수할 수 있다. |
| Base.x8Scope | compact | 드라이버로 호환 총기에 장착하거나 떼어 회수할 수 있다. | 호환 총기의 최대 사거리를 늘리는 부착물로 쓸 수 있다. 근거리 정확도는 낮아진다. |
| Base.x8Scope | expanded | 드라이버로 호환 총기에 장착하거나 떼어 회수할 수 있다. | 호환 총기의 최대 사거리를 늘리는 부착물로 쓸 수 있다. 근거리 정확도는 낮아진다. 드라이버로 호환 총기에 장착하거나 떼어 회수할 수 있다. |


## 2026-09-14 용도 공개와 후속 결과의 경계 정정

사용자가 정정한 기준은 **확인된 플레이어 용도를 공개하되, 그로 인한 후속 결과를 설명하거나 네이티브 계산까지 입증하는 것을 용도 공개의 전제조건으로 삼지 않는다**는 것이다. 목적 자체(예: 부착물의 장전 시간 단축), 필요한 도구, 가공 대상·결과물 이름을 일괄 삭제하는 기준도 아니다.

앞선 감독 전달의 “표백제 중독·불행 설명 추가”는 사용자의 용도 범위를 확대 해석한 요구였고, 후속 전달에서 철회됐다. 그 전달로 임시 추가했던 소비 결과 사실과 독서 중 기분 수치 문면은 모두 되돌렸다. 이를 사용자 요구 또는 수락된 결과로 취급하지 않는다. 임시 생성·검사 로그는 감사 이력으로만 남긴다.

### 공통 규칙과 실제 최종 문면

description_composition_uses.prepare에서 Poison 선언과 위험 결과 해석 미확정을 이유로 eat_food/consume_edible_food/drink_food_contents를 internal로 제외하던 선택 규칙을 제거했다. 기존에 채택된 소비 동작을 일반적인 용도 조립 경로로 표현하며, 아이템 ID별 완성 문장 덮어쓰기는 없다. 현재 원본 선언의 해당 Poison=true 입력은 한 개이므로 최종 영향은 Bleach뿐이다.

- **확인한 용도:** Bleach의 혈흔 청소와 소비 동작. 소비는 scripts/items_food.txt 선언, 소비 메뉴와 ISEatFoodAction:perform의 실제 character:Eat 위임으로 확인한 구간이다.
- **공개 문장:** KO Compact는 “바닥 혈흔을 지울 수 있다. 마실 수 있다.”, Expanded는 같은 두 용도를 별도 줄에 표시한다. EN은 “It can be used to clean floor bloodstains. It can be drunk.”이다.
- **공개하지 않는 후속 결과:** 중독·불행 증가, 사망 여부·시점·섭취량·내부 수치를 새 설명으로 붙이지 않았다. 이러한 결과를 계산하지 못했다는 이유로 소비 동작을 지우지도 않는다. 원본 선언 및 기존 내부 위험 분석은 보존하되, 이를 용도 문면의 미완성으로 집계하지 않는다.
- **다른 경계:** Bayonnet·GunLight는 확인된 드라이버 장착/분리 범위를 유지한다. 자료와 연결되지 않은 총검 공격·조명 기능은 추가하지 않는다. 가구 136개도 기존 설치 사용/이동 범위를 유지한다. 원본 가구 재조사를 반복하지 않았으며, 실제 생성 문면은 두 군(일반 가구135, 건축 재료 역할도 있는 Mattress1)으로 확인했다. 명시 목적이 확인된 부착물12개와 운동 깊이 등 이전 수락 문면은 그대로다.
- **철회 변경의 복원:** Maggots2의 임시 중독/불행 문장과 읽을거리12개의 임시 기분 수치 제한 문장을 되돌렸다. 최종 Maggots2는 “먹을 수 있다”, 읽을거리는 기분 전환 용도와 기존 재료/연료 활용을 유지한다. 이 복원은 후속 결과 설명의 범위 정정이며, 해당 원본 사실이 없다는 판정이 아니다.

### 최종 검수·검증

전체 2,105개를 재생성했다. 0347b8 후보(`.tmp/prose/qualitative-before.json`)와 모든 KO/EN C/E 문면을 비교하여 **Bleach 1개·4표면만 변경**되고 나머지 2,104개는 동일함을 확인했다. 변경 항목의 실제 C/E 전후 전문과 철회 영향·경계 항목의 현재 문면을 읽었다. 각 언어/깊이 present 1,976, absent 129, failed 0 유지. Semantic correction은 이전 수락된 88개 사실이며 임시 소비 결과4개는 없다.

최종 기존 근거 조립·설명 조립 계약 검사: `2 passed in 29.24s`, 종료 코드 `0`. 로그 `.tmp/prose/use-boundary-tests.log`. 임시 기준으로 실행한 qualitative 로그들은 현재 후보의 검증으로 인용하지 않는다. 당시 설명 검사에는 이전 기대값과의 충돌이 있었고 그 기록도 보존했다. 정정 후의 계약 검사는 소비 용도 보존, 새 후속 결과 미추가, 기존 목적 표현 보존을 확인한다.

```powershell
uv run --project .\Iris\tooling python -I -B -m pytest --noconftest -c .\Iris\tooling\pyproject.toml .\Iris\build\description\v2\tests\test_layer3_composition.py::test_layer3_composition_contract .\Iris\build\description\v2\tests\test_layer3_description_composition.py::test_layer3_description_composition --basetemp .\.tmp\use-boundary-tests-01 -q -s --tb=short
```

Descriptions SHA-256: `528e8c70a4c6ee9752c97c00b211b1517e7213d263395e2a74a90984459e8902`. Blocks SHA-256: `2dec826b217062da7ee8ba5276312ad9b3fa2e43cbb2db303d7c1fd7c481ea2a`로 0347b8 후보와 동일하다. 두 HTML과 입력 바인딩을 갱신했다. 새 패키징·설치·커밋·푸시는 없으며 최신 기존 ZIP은 이전5c6eb4 텍스트 후보이다.

| 언어 | 깊이 | 이전 수락 문면 | 현재 문면 |
|---|---|---|---|
| ko | compact | 바닥 혈흔을 지울 수 있다. | 바닥 혈흔을 지울 수 있다. 마실 수 있다. |
| ko | expanded | 바닥 혈흔을 지울 수 있다. | 바닥 혈흔을 지울 수 있다. 마실 수 있다. |
| en | compact | It can be used to clean floor bloodstains. | It can be used to clean floor bloodstains. It can be drunk. |
| en | expanded | It can be used to clean floor bloodstains. | It can be used to clean floor bloodstains. It can be drunk. |


## 2026-09-14 용접 역할·해체 대상·학습 제작법 목록

최신 사용자 지시를 우선해, 용접 착용 장비를 공통 작업으로 묶고 해체 대상의 실체를 확인했으며 Expanded 학습 개요 아래 줄바꿈한 하이픈 제작법 목록을 추가했다. 기존의 목록 억제 방침을 이번 명시 요청의 거절 근거로 적용하지 않았다. 표백제 용도 공개 등 직전 수락 문면을 유지했다.

### 바닐라와 현재 Iris 메뉴의 정보

- 바닐라 `ISMoveableSpriteProps.fromObject`(lua/client/Moveables/ISMoveableSpriteProps.lua:31–44)는 일반 Moveables 해체와 별도로 `IsoThumpable` 해체 경로를 선택한다. 원문 주석은 **stairs and lamp-on-pillar**를 해당 경로의 예시로 명시한다. `ISThumpableSpriteProps:getInfoPanelDescription`(3113 부근)은 현재 가리킨 대상 이름과 Saw/Screwdriver 도구를 표시한다. `walkToAndEquip`은 두 도구를 선택하며 `scrapObjectViaCursor`는 해체와 재료 회수 작업을 수행한다. 이는 바닐라에서 현재 대상의 이름/도구를 알 수 있다는 근거이며, Iris에서 도구별 전체 대상 목록이 표시된다는 근거가 아니다.
- 현재 Iris `UseCases._getDescriptionState`를 실제 Lua로 읽은 결과, Saw/GardenSaw의 우클릭 문면은 **[우클릭] 톱질 해체**, Screwdriver는 **[우클릭] 나사 해체**였다. 대상 목록은 없다. 같은 읽기에서 EngineerMagazine2는 `verified_empty / positive_lines_empty`, 0행이었다. 명령 `lua .tmp/prose/targets_l4_read.lua`, 종료 코드0. `IrisBrowserInteractionProjection.build`는 이 sourceLine의 표시 문구를 행으로 보내며, `Index.getMoveablesInfoForItem`/`IrisMoveablesIndex`는 등록 여부·태그를 제공할 뿐 해체 대상 목록을 제공하지 않는다. 다른 계층이 대상을 설명한다고 추측하지 않았다.
- 바닐라 제작법 학습은 TeachedRecipes 선언, ISReadABook의 학습 처리, ISLiteratureUI의 알려진 제작법 확인 및 Teaches Recipe 툴팁을 기존 채택 근거로 사용한다. Iris에 해당 학습 목록이 이미 충분히 보인다고 간주하지 않고 DVF Expanded에 직접 추가했다.

### 공통 규칙과 범위

1. **용접 착용 역할 1개:** description_composition_uses의 welding 역할 분기에서 착용 장비를 “용접 작업을 할 때 착용하는 장비다.”로 구성한다. WeldingMask의 얼굴 위치와 용접 하위 작업을 개요에 중복하지 않는다. 금속 드럼의 불쏘시개 활용은 별도 용도로 보존했다. 비착용 용접 도구의 문형을 일괄 바꾸지 않았다.
2. **해체 도구 3개:** Saw, GardenSaw, Screwdriver의 기존 dismantle_built_object 사실에 recovery_relations가 실제 원본 해체 대상 예시를 결합한다. ISWoodenStairs의 setIsDismantable(true), ISLightSource의 dismantable 선언, 실제 fallback의 명시 예시·선택 동작을 소스 해시와 함께 기록한다. C는 “목제 계단 및 기둥 조명 같은 설치물을 해체해 재료를 회수하는 데 쓸 수 있다.”, E는 여기에 **톱과 드라이버로**를 명시한다. 도구의 다른 목공·제작·음식 손질·차량/무기 작업은 보존했다. 처음 검토한 나무 상자·퇴비통은 해체 가능 선언만으로 일반 Moveables와 이번 fallback 중 실제 도구 경로를 확정하기 어려워 최종 예시에서 제외했다. “분해 가능한”이라는 순환 수식어나 isValid 조건 열거로 대상을 대체하지 않는다.
3. **제작법 학습 25개, 목록82항목:** recovery_relations는 기존 learn_literature 사실의 provenance에 들어 있는 recipe 선언과 해당 책의 TeachedRecipes를 교차하고, 원본 순서·정확한 이름을 보존한다. 동일 이름의 recipe overload는 목록에서 한 제작법으로 취급하며 임의 결과 하나를 선택하지 않는다. 금속 건축의 학습 키도 기존 채택 관계를 사용한다. 차량 정비 지식·약초 식별·발전기 지식처럼 제작법 학습 역할이 아닌 기존5개는 이 제작법 목록으로 바꾸지 않는다. Compact는 짧은 개요, Expanded는 개요와 `- 이름` 목록을 한 용도 단위로 구성한다. 제작법 수가 하나면 단수, 둘 이상이면 복수로 설명한다. EngineerMagazine2의 실제 학습 목록은 **연막 폭탄 만들기 1개**이므로 “여러”를 붙이지 않는다. 요리는 자연스럽게 “여러 요리법”으로 표현한다.
4. 목록 이름은 Recipes_KO 번역을 우선한다. 원본 KO에 없는 `Make Wooden Box Trap` 하나는 제작법 이름 자체를 “나무 상자 덫 만들기”로 번역했다. 다른 덫 제작법으로 치환하지 않았으며 아이템별 완성 문장 덮어쓰기가 아니다. 나머지 원본 번역의 표기는 그대로 유지한다.

### 실제 메뉴 소비·검증

기존 `product_projection.expanded_projection`은 개요+목록의 내부 줄바꿈을 segment/unit 문자열에 보존한다. `IrisItemDetailModelAssembler`는 독립 unit 사이를 분리하고, `IrisWikiSections.getLayer3Units`를 거쳐 Browser와 Wiki가 각 용도를 별도 불릿으로 렌더링한다. `IrisTextLayout.wrapLines`는 원본 물리 줄바꿈을 유지하면서 폭에 맞춰 줄을 나눈다. 따라서 연료 활용은 마지막 제작법의 일부가 되지 않는다.

기존 `detail_view_model_locale_harness.lua`에 목록 시작 개수 보존 검사를 추가했다. 변경된29개 전체를 양언어의 실제 Browser/Wiki 소비 코드와 라벨·스크롤 계산으로 실행했다. 개요 아래 하이픈82항목, 줄바꿈, 폭에 따른 줄 나눔, 독립 연료 불릿을 확인했다. 전체2,105개의 양언어 메뉴 모델4,210상태도 기존 harness가 대조한다. 엔진 위젯과 글꼴 측정만 대체했으며 실제 PZ 게임 화면을 관찰한 결과는 아니다.

최종 검증 결과:

- 근거 조립·설명 조립의 기존 계약: **2 passed in32.43s, 종료 코드0**, `.tmp/prose/targets-tests-accepted.log`.
- 기존 실제 메뉴 harness: **IRIS_EXPANDED_MENU_PASS**, 종료 코드0, `.tmp/prose/targets-menu-final.log`. 임시 fixture 경로 `.tmp/menu/targets-runtime-03/runtime`, 식별자 `l3p-5e0a7544ab12aaa79a2e83ba8b9a86a7412ad12b074f332e7ca0031f549abeb0`.
- 사용자 지정 Lua 검사 `powershell -ExecutionPolicy Bypass -File .\tools\check_lua_syntax.ps1`: **Lua syntax validation OK:265 files**, 종료 코드0, `.tmp/prose/targets-lua-syntax.log`.

```powershell
uv run --project .\Iris\tooling python -I -B -m pytest --noconftest -c .\Iris\tooling\pyproject.toml .\Iris\build\description\v2\tests\test_layer3_composition.py::test_layer3_composition_contract .\Iris\build\description\v2\tests\test_layer3_description_composition.py::test_layer3_description_composition --basetemp .\.tmp\targets-tests-03 -q -s --tb=short
uv run --project .\Iris\tooling python .tmp/prose/targets_menu_fixture_final.py
powershell -ExecutionPolicy Bypass -File .\tools\check_lua_syntax.ps1
```

처음 제품 생성 경로는 기존 B ZIP의 corpus/owner가 최신 설명과 다르므로 정상적으로 거부됐다(`.tmp/prose/targets-menu.log`). 이 검사를 우회해 제품을 수락하거나 패키징하지 않았다. 최종 메뉴 검증은 기존 serializer/facade와 실제 메뉴 코드를 쓰는 임시 데이터 fixture이며 **배포 승인 제품이나 새 ZIP이 아니다**. 설치·새 프레임워크·미래 어댑터·커밋·푸시는 수행하지 않았다.

전체2,105개 재생성 후 공통 규칙 영향29개의 실제 KO/EN C/E를 전문 대조했다. 각 언어/깊이 present1,976·absent129·failed0 유지. 제작법 목록 이외의 기존 독립 용도가 보존되는지 기존 계약과 메뉴 unit 경계로 확인했다. 일반 가구 해체의 나머지 대상/도구 조합, 전체 월드 설치물의 완전한 목록, 실제 게임 글꼴 화면, 최신 B와 결합한 배포 제품은 이번 검증으로 확정하지 않는다. 확인된 두 해체 대상 예시는 충분한 구체 정보를 DVF 자체에 주기 위한 범위이며 전체 대상을 열거했다는 뜻이 아니다.

Descriptions SHA-256 `e9015b5c96b7625cf0679e974311659afac1544cf95cfbb84f82c31e130d3e1e`. Blocks SHA-256 `f841e0ba57e2823d45e07daaecdfc374951c48f58666142c068b6660fadddd95`. Semantic correction은 기존88개 유지이며 이번에 학습 결과 사실이나 새로운 게임 효과를 추가하지 않았다. 현재 입력 바인딩·두HTML을 갱신했다.

아래는 공통 규칙 영향29개의 실제 한국어 전후 C/E다. 목록의 줄바꿈은 셀 안의 줄바꿈으로 표시한다.

| 아이템 | 깊이 | 이전 | 현재 |
|---|---|---|---|
| Base.CookingMag1 | compact | 읽어서 요리법을 배울 수 있다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다. | 읽어서 여러 요리법을 배울 수 있다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다. |
| Base.CookingMag1 | expanded | 읽어서 요리법을 배울 수 있다.<br>모닥불 등의 연료나 불쏘시개로 쓸 수 있다. | 읽어서 여러 요리법을 배울 수 있다.<br>- 케이크 반죽 만들기<br>- 파이 반죽 만들기<br>- 초코칩 쿠키 도우 만들기<br>- 초콜릿 쿠키 도우 만들기<br>- 오트밀 쿠기 도우 만들기<br>- 설탕 쿠기 도우 만들기<br>- 쇼트브레드 쿠키 도우 만들기<br>모닥불 등의 연료나 불쏘시개로 쓸 수 있다. |
| Base.CookingMag2 | compact | 읽어서 요리법을 배울 수 있다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다. | 읽어서 여러 요리법을 배울 수 있다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다. |
| Base.CookingMag2 | expanded | 읽어서 요리법을 배울 수 있다.<br>모닥불 등의 연료나 불쏘시개로 쓸 수 있다. | 읽어서 여러 요리법을 배울 수 있다.<br>- 빵 반죽 만들기<br>- 비스킷 만들기<br>- 피자 만들기<br>모닥불 등의 연료나 불쏘시개로 쓸 수 있다. |
| Base.ElectronicsMag1 | compact | 읽어서 전자 장치 관련 제작법을 배울 수 있다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다. | 읽어서 여러 전자 장치의 제작법을 배울 수 있다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다. |
| Base.ElectronicsMag1 | expanded | 읽어서 전자 장치 관련 제작법을 배울 수 있다.<br>모닥불 등의 연료나 불쏘시개로 쓸 수 있다. | 읽어서 여러 전자 장치의 제작법을 배울 수 있다.<br>- 원격제어 조정기 (V1) 만들기<br>- 원격제어 조정기 (V2) 만들기<br>- 원격제어 조정기 (V3) 만들기<br>모닥불 등의 연료나 불쏘시개로 쓸 수 있다. |
| Base.ElectronicsMag2 | compact | 읽어서 전자 장치 관련 제작법을 배울 수 있다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다. | 읽어서 여러 전자 장치의 제작법을 배울 수 있다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다. |
| Base.ElectronicsMag2 | expanded | 읽어서 전자 장치 관련 제작법을 배울 수 있다.<br>모닥불 등의 연료나 불쏘시개로 쓸 수 있다. | 읽어서 여러 전자 장치의 제작법을 배울 수 있다.<br>- 수제작 타이머 만들기<br>- 타이머로 추가하기<br>모닥불 등의 연료나 불쏘시개로 쓸 수 있다. |
| Base.ElectronicsMag3 | compact | 읽어서 전자 장치 관련 제작법을 배울 수 있다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다. | 읽어서 여러 전자 장치의 제작법을 배울 수 있다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다. |
| Base.ElectronicsMag3 | expanded | 읽어서 전자 장치 관련 제작법을 배울 수 있다.<br>모닥불 등의 연료나 불쏘시개로 쓸 수 있다. | 읽어서 여러 전자 장치의 제작법을 배울 수 있다.<br>- 센서 (V1)로 추가 개조하기<br>- 센서 (V2)로 추가 개조하기<br>- 센서 (V3)로 추가 개조하기<br>모닥불 등의 연료나 불쏘시개로 쓸 수 있다. |
| Base.ElectronicsMag5 | compact | 읽어서 전자 장치 관련 제작법을 배울 수 있다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다. | 읽어서 여러 전자 장치의 제작법을 배울 수 있다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다. |
| Base.ElectronicsMag5 | expanded | 읽어서 전자 장치 관련 제작법을 배울 수 있다.<br>모닥불 등의 연료나 불쏘시개로 쓸 수 있다. | 읽어서 여러 전자 장치의 제작법을 배울 수 있다.<br>- 수제작 원격 폭탄 격발기 만들기<br>- 격발기 만들기<br>모닥불 등의 연료나 불쏘시개로 쓸 수 있다. |
| Base.EngineerMagazine1 | compact | 읽어서 전자 장치 관련 제작법을 배울 수 있다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다. | 읽어서 전자 장치의 제작법을 배울 수 있다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다. |
| Base.EngineerMagazine1 | expanded | 읽어서 전자 장치 관련 제작법을 배울 수 있다.<br>모닥불 등의 연료나 불쏘시개로 쓸 수 있다. | 읽어서 전자 장치의 제작법을 배울 수 있다.<br>- 소음 발생기 만들기<br>모닥불 등의 연료나 불쏘시개로 쓸 수 있다. |
| Base.EngineerMagazine2 | compact | 읽어서 장치를 만드는 방법을 배울 수 있다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다. | 읽어서 장치의 제작법을 배울 수 있다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다. |
| Base.EngineerMagazine2 | expanded | 읽어서 장치를 만드는 방법을 배울 수 있다.<br>모닥불 등의 연료나 불쏘시개로 쓸 수 있다. | 읽어서 장치의 제작법을 배울 수 있다.<br>- 연막 폭탄 만들기<br>모닥불 등의 연료나 불쏘시개로 쓸 수 있다. |
| Base.FarmingMag1 | compact | 읽어서 작물 치료제를 만드는 방법을 배울 수 있다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다. | 읽어서 여러 작물 치료제의 제작법을 배울 수 있다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다. |
| Base.FarmingMag1 | expanded | 읽어서 작물 치료제를 만드는 방법을 배울 수 있다.<br>모닥불 등의 연료나 불쏘시개로 쓸 수 있다. | 읽어서 여러 작물 치료제의 제작법을 배울 수 있다.<br>- 곰팡이 제거제 만들기<br>- 살충제 만들기<br>모닥불 등의 연료나 불쏘시개로 쓸 수 있다. |
| Base.FishingMag1 | compact | 읽어서 낚시 장비 관련 제작법을 배울 수 있다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다. | 읽어서 여러 낚시 장비의 제작법을 배울 수 있다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다. |
| Base.FishingMag1 | expanded | 읽어서 낚시 장비 관련 제작법을 배울 수 있다.<br>모닥불 등의 연료나 불쏘시개로 쓸 수 있다. | 읽어서 여러 낚시 장비의 제작법을 배울 수 있다.<br>- 낚싯대 만들기<br>- 낚싯대 수리하기<br>모닥불 등의 연료나 불쏘시개로 쓸 수 있다. |
| Base.FishingMag2 | compact | 읽어서 낚시 장비 관련 제작법을 배울 수 있다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다. | 읽어서 여러 낚시 장비의 제작법을 배울 수 있다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다. |
| Base.FishingMag2 | expanded | 읽어서 낚시 장비 관련 제작법을 배울 수 있다.<br>모닥불 등의 연료나 불쏘시개로 쓸 수 있다. | 읽어서 여러 낚시 장비의 제작법을 배울 수 있다.<br>- 어망 만들기<br>- 철사 회수하기<br>모닥불 등의 연료나 불쏘시개로 쓸 수 있다. |
| Base.GardenSaw | compact | 사냥 장비를 만들거나 폭발 장치를 만드는 데 쓸 수 있다. 음식을 손질하고 목재를 가공할 수 있다. 건축물을 해체할 수 있다. | 목재를 가공하는 데 쓸 수 있다. 목제 계단 및 기둥 조명 같은 설치물을 해체해 재료를 회수하는 데 쓸 수 있다. 사냥 장비를 만들거나 폭발 장치를 만드는 데 쓸 수 있다. 음식을 나누는 데 쓸 수 있다. |
| Base.GardenSaw | expanded | 사냥 장비를 만들거나 폭발 장치를 만드는 데 쓸 수 있다.<br>음식을 나누는 데 쓸 수 있다.<br>목재를 가공하는 데 쓸 수 있다.<br>분해 가능한 건축물을 해체하고 재료를 회수할 수 있다. | 목재를 가공하는 데 쓸 수 있다.<br>톱과 드라이버로 목제 계단 및 기둥 조명 같은 설치물을 해체해 재료를 회수하는 데 쓸 수 있다.<br>사냥 장비를 만들거나 폭발 장치를 만드는 데 쓸 수 있다.<br>음식을 나누는 데 쓸 수 있다. |
| Base.HuntingMag1 | compact | 읽어서 덫을 만드는 방법을 배울 수 있다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다. | 읽어서 덫의 제작법을 배울 수 있다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다. |
| Base.HuntingMag1 | expanded | 읽어서 덫을 만드는 방법을 배울 수 있다.<br>모닥불 등의 연료나 불쏘시개로 쓸 수 있다. | 읽어서 덫의 제작법을 배울 수 있다.<br>- 올가미 덫 만들기<br>모닥불 등의 연료나 불쏘시개로 쓸 수 있다. |
| Base.HuntingMag2 | compact | 읽어서 덫을 만드는 방법을 배울 수 있다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다. | 읽어서 여러 덫의 제작법을 배울 수 있다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다. |
| Base.HuntingMag2 | expanded | 읽어서 덫을 만드는 방법을 배울 수 있다.<br>모닥불 등의 연료나 불쏘시개로 쓸 수 있다. | 읽어서 여러 덫의 제작법을 배울 수 있다.<br>- 나무 상자 덫 만들기<br>- 막대 덫 만들기<br>모닥불 등의 연료나 불쏘시개로 쓸 수 있다. |
| Base.HuntingMag3 | compact | 읽어서 덫을 만드는 방법을 배울 수 있다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다. | 읽어서 여러 덫의 제작법을 배울 수 있다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다. |
| Base.HuntingMag3 | expanded | 읽어서 덫을 만드는 방법을 배울 수 있다.<br>모닥불 등의 연료나 불쏘시개로 쓸 수 있다. | 읽어서 여러 덫의 제작법을 배울 수 있다.<br>- 덫상자 만들기<br>- 철장 덫 만들기<br>모닥불 등의 연료나 불쏘시개로 쓸 수 있다. |
| Base.MetalworkMag1 | compact | 읽어서 금속 구조물을 만드는 방법을 배울 수 있다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다. | 읽어서 여러 금속 구조물의 제작법을 배울 수 있다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다. |
| Base.MetalworkMag1 | expanded | 읽어서 금속 구조물을 만드는 방법을 배울 수 있다.<br>모닥불 등의 연료나 불쏘시개로 쓸 수 있다. | 읽어서 여러 금속 구조물의 제작법을 배울 수 있다.<br>- 금속 벽 만들기<br>- 금속 지붕 만들기<br>모닥불 등의 연료나 불쏘시개로 쓸 수 있다. |
| Base.MetalworkMag2 | compact | 읽어서 금속 구조물을 만드는 방법을 배울 수 있다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다. | 읽어서 금속 구조물의 제작법을 배울 수 있다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다. |
| Base.MetalworkMag2 | expanded | 읽어서 금속 구조물을 만드는 방법을 배울 수 있다.<br>모닥불 등의 연료나 불쏘시개로 쓸 수 있다. | 읽어서 금속 구조물의 제작법을 배울 수 있다.<br>- 금속 보관함 만들기<br>모닥불 등의 연료나 불쏘시개로 쓸 수 있다. |
| Base.MetalworkMag3 | compact | 읽어서 금속 구조물을 만드는 방법을 배울 수 있다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다. | 읽어서 금속 구조물의 제작법을 배울 수 있다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다. |
| Base.MetalworkMag3 | expanded | 읽어서 금속 구조물을 만드는 방법을 배울 수 있다.<br>모닥불 등의 연료나 불쏘시개로 쓸 수 있다. | 읽어서 금속 구조물의 제작법을 배울 수 있다.<br>- 금속 울타리 만들기<br>모닥불 등의 연료나 불쏘시개로 쓸 수 있다. |
| Base.MetalworkMag4 | compact | 읽어서 금속 가공 방법을 배울 수 있다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다. | 읽어서 여러 금속 물품의 제작법을 배울 수 있다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다. |
| Base.MetalworkMag4 | expanded | 읽어서 금속 가공 방법을 배울 수 있다.<br>모닥불 등의 연료나 불쏘시개로 쓸 수 있다. | 읽어서 여러 금속 물품의 제작법을 배울 수 있다.<br>- 금속판 만들기<br>- 작은 금속판 만들기<br>모닥불 등의 연료나 불쏘시개로 쓸 수 있다. |
| Base.Saw | compact | 사냥 장비를 만들거나 폭발 장치를 만드는 데 쓸 수 있다. 음식을 손질하고 목재를 가공할 수 있다. 건축물을 해체하거나 산탄총의 총신을 줄일 수 있다. | 목재를 가공하는 데 쓸 수 있다. 목제 계단 및 기둥 조명 같은 설치물을 해체해 재료를 회수하는 데 쓸 수 있다. 사냥 장비를 만들거나 폭발 장치를 만드는 데 쓸 수 있다. 음식을 나누는 데 쓸 수 있다. 산탄총의 총신을 줄이는 도구로 쓸 수 있다. |
| Base.Saw | expanded | 사냥 장비를 만들거나 폭발 장치를 만드는 데 쓸 수 있다.<br>음식을 나누는 데 쓸 수 있다.<br>목재를 가공하는 데 쓸 수 있다.<br>분해 가능한 건축물을 해체하고 재료를 회수할 수 있다.<br>산탄총의 총신을 줄이는 도구로 쓸 수 있다. | 목재를 가공하는 데 쓸 수 있다.<br>톱과 드라이버로 목제 계단 및 기둥 조명 같은 설치물을 해체해 재료를 회수하는 데 쓸 수 있다.<br>사냥 장비를 만들거나 폭발 장치를 만드는 데 쓸 수 있다.<br>음식을 나누는 데 쓸 수 있다.<br>산탄총의 총신을 줄이는 도구로 쓸 수 있다. |
| Base.Screwdriver | compact | 전자기기를 만들거나 분해하고, 조명을 건전지용으로 개조할 수 있다. 목재를 가공하거나 건축물을 해체할 수 있다. 차량 부품과 호환 무기 부착물을 장착하거나 제거할 수 있다. 제작한 창에 부착하거나 무기로 쓸 수도 있다. | 목재를 가공할 수 있다. 차량 부품과 호환 무기 부착물을 장착하거나 제거할 수 있다. 제작한 창에 부착하거나 무기로 쓸 수도 있다. 목제 계단 및 기둥 조명 같은 설치물을 해체해 재료를 회수하는 데 쓸 수 있다. 전자기기를 만들거나 분해하고, 조명을 건전지용으로 개조할 수 있다. |
| Base.Screwdriver | expanded | 전자 부품과 무전기를 만들 수 있다. 라디오와 TV를 포함한 전자기기를 분해해 부품을 회수할 수 있다. 조명을 건전지용으로 개조할 수 있다.<br>목재를 가공하는 데 쓸 수 있다.<br>분해 가능한 건축물을 해체하고 재료를 회수할 수 있다.<br>차량 부품을 장착하거나 탈거하는 데 사용할 수 있다.<br>호환 무기의 부착물을 장착하거나 제거할 수 있다.<br>제작한 창에 부착해 쓸 수 있다.<br>무기로 쓸 수 있다. | 목재를 가공하는 데 쓸 수 있다.<br>톱과 드라이버로 목제 계단 및 기둥 조명 같은 설치물을 해체해 재료를 회수하는 데 쓸 수 있다.<br>차량 부품을 장착하거나 탈거하는 데 사용할 수 있다.<br>호환 무기의 부착물을 장착하거나 제거할 수 있다.<br>제작한 창에 부착해 쓸 수 있다.<br>무기로 쓸 수 있다.<br>전자 부품과 무전기를 만들 수 있다. 라디오와 TV를 포함한 전자기기를 분해해 부품을 회수할 수 있다. 조명을 건전지용으로 개조할 수 있다. |
| Base.SmithingMag1 | compact | 읽어서 금속을 단조해 물품을 만드는 방법을 배울 수 있다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다. | 읽어서 여러 금속 물품의 제작법을 배울 수 있다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다. |
| Base.SmithingMag1 | expanded | 읽어서 금속을 단조해 물품을 만드는 방법을 배울 수 있다.<br>모닥불 등의 연료나 불쏘시개로 쓸 수 있다. | 읽어서 여러 금속 물품의 제작법을 배울 수 있다.<br>- 포크 만들기<br>- 숟가락 만들기<br>- 조리용 냄비 만들기<br>- 오븐 쟁반 만들기<br>- 손잡이 냄비 만들기<br>- 빵 판 만들기<br>- 빵 굽는 팬 만들기<br>- 프라이팬 만들기<br>모닥불 등의 연료나 불쏘시개로 쓸 수 있다. |
| Base.SmithingMag2 | compact | 읽어서 금속을 단조해 물품을 만드는 방법을 배울 수 있다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다. | 읽어서 여러 금속 물품의 제작법을 배울 수 있다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다. |
| Base.SmithingMag2 | expanded | 읽어서 금속을 단조해 물품을 만드는 방법을 배울 수 있다.<br>모닥불 등의 연료나 불쏘시개로 쓸 수 있다. | 읽어서 여러 금속 물품의 제작법을 배울 수 있다.<br>- 편지 개봉칼 만들기<br>- 못 만들기<br>- 종이 집게 만들기<br>- 가위 만들기<br>- 문 손잡이 만들기<br>- 경첩 만들기<br>- 버터칼 만들기<br>- 둥근 망치 만들기<br>모닥불 등의 연료나 불쏘시개로 쓸 수 있다. |
| Base.SmithingMag3 | compact | 읽어서 금속을 단조해 물품을 만드는 방법을 배울 수 있다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다. | 읽어서 여러 금속 물품의 제작법을 배울 수 있다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다. |
| Base.SmithingMag3 | expanded | 읽어서 금속을 단조해 물품을 만드는 방법을 배울 수 있다.<br>모닥불 등의 연료나 불쏘시개로 쓸 수 있다. | 읽어서 여러 금속 물품의 제작법을 배울 수 있다.<br>- 집게 만들기<br>- 망치 만들기<br>- 금속판 만들기<br>- 봉합용 바늘 집개 만들기<br>- 핀셋 만들기<br>- 봉합용 바늘 만들기<br>- 드럼통 만들기<br>- 부엌칼 만들기<br>- 톱 만들기<br>- 사냥용 칼 만들기<br>- 삽 만들기<br>- 모종삽 만들기<br>모닥불 등의 연료나 불쏘시개로 쓸 수 있다. |
| Base.SmithingMag4 | compact | 읽어서 금속을 단조해 물품을 만드는 방법을 배울 수 있다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다. | 읽어서 여러 금속 물품의 제작법을 배울 수 있다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다. |
| Base.SmithingMag4 | expanded | 읽어서 금속을 단조해 물품을 만드는 방법을 배울 수 있다.<br>모닥불 등의 연료나 불쏘시개로 쓸 수 있다. | 읽어서 여러 금속 물품의 제작법을 배울 수 있다.<br>- 9mm 탄 틀 만들기<br>- .308 탄 틀 만들기<br>- .223 탄 틀 만들기<br>- 산탄 총탄 틀 만들기<br>- 9mm 탄 만들기<br>- 산탄 총탄 만들기<br>- .308 탄 만들기<br>- .223 탄 만들기<br>- 쇠지렛대 만들기<br>- 골프 클럽 만들기<br>- 도끼 만들기<br>- 대형 망치 만들기<br>모닥불 등의 연료나 불쏘시개로 쓸 수 있다. |
| Base.WeldingMask | compact | 금속 부품 용접과 용접 건축을 할 때 얼굴에 착용하는 장비다. 금속 드럼의 불쏘시개로 쓸 수 있다. | 용접 작업을 할 때 착용하는 장비다. 금속 드럼의 불쏘시개로 쓸 수 있다. |
| Base.WeldingMask | expanded | 금속 부품 용접과 용접 건축을 할 때 얼굴에 착용하는 장비다.<br>금속 드럼의 불쏘시개로 쓸 수 있다. | 용접 작업을 할 때 착용하는 장비다.<br>금속 드럼의 불쏘시개로 쓸 수 있다. |
| Radio.RadioMag1 | compact | 읽어서 전자 장치 관련 제작법을 배울 수 있다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다. | 읽어서 전자 장치의 제작법을 배울 수 있다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다. |
| Radio.RadioMag1 | expanded | 읽어서 전자 장치 관련 제작법을 배울 수 있다.<br>모닥불 등의 연료나 불쏘시개로 쓸 수 있다. | 읽어서 전자 장치의 제작법을 배울 수 있다.<br>- 수제작 라디오 만들기<br>모닥불 등의 연료나 불쏘시개로 쓸 수 있다. |
| Radio.RadioMag2 | compact | 읽어서 전자 장치 관련 제작법을 배울 수 있다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다. | 읽어서 전자 장치의 제작법을 배울 수 있다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다. |
| Radio.RadioMag2 | expanded | 읽어서 전자 장치 관련 제작법을 배울 수 있다.<br>모닥불 등의 연료나 불쏘시개로 쓸 수 있다. | 읽어서 전자 장치의 제작법을 배울 수 있다.<br>- 수제작 휴대용 무전기 만들기<br>모닥불 등의 연료나 불쏘시개로 쓸 수 있다. |
| Radio.RadioMag3 | compact | 읽어서 전자 장치 관련 제작법을 배울 수 있다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다. | 읽어서 전자 장치의 제작법을 배울 수 있다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다. |
| Radio.RadioMag3 | expanded | 읽어서 전자 장치 관련 제작법을 배울 수 있다.<br>모닥불 등의 연료나 불쏘시개로 쓸 수 있다. | 읽어서 전자 장치의 제작법을 배울 수 있다.<br>- 수제작 아마추어 무선통신기 만들기<br>모닥불 등의 연료나 불쏘시개로 쓸 수 있다. |

최종 실제 변경: 29개, 116표면. {'ko/compact': 29, 'ko/expanded': 29, 'en/compact': 29, 'en/expanded': 29}


## 2026-09-14 학습 공정·작업 구분 보존 및 Compact 묶기 복구

감독이 부분 수락한 용접 착용 문형, 해체 대상 근거, 학습 목록 구조를 유지하면서 과도한 일반화 세 항목을 교정했다. 목록이 확인된 학습 분야를 대체하거나, recipe 수가 물품 수를 뜻한다고 해석하지 않는다.

### 학습 개요의 공통 규칙

recovery_relations는 이미 채택된 학습 recipe 키의 명시 동작을 `make`(Make/Craft), `repair`(Fix), `modify`(Add), `recover`(Get … Back)로 전달한다. 아이템 ID나 책 제목으로 작업을 추정하지 않는다. 현재25개 학습 목록82항목은 제작75·개조5·수리1·회수1이며 미분류 동작은0이다. 원본 recipe 관측 ref, 책의 TeachedRecipes 교차 관계, 목록 이름과 순서는 유지했다.

uses의 학습 개요는 제작만 있는 경우 기존 채택 분야/공정 표현을 재사용한다. SmithingMag1–4는 C/E 모두 **읽어서 금속을 단조해 물품을 만드는 방법을 배울 수 있다.**를 복구했다. MetalworkMag4의 **금속 가공**, 금속 건축의 **금속 구조물**, 요리 등의 기존 분야도 유지한다. 전부 “금속 물품 제작”으로 합치지 않는다.

제작 이외 동작이 있는 경우 그 동작을 개요에 결합한다.

| 공통 작업 관계 | 실제 개요 |
|---|---|
| 낚시 장비 제작+수리 | 읽어서 낚시 장비 제작 및 수리 방법을 배울 수 있다. |
| 낚시 장비 제작+재료 회수 | 읽어서 낚시 장비 제작 및 재료 회수 방법을 배울 수 있다. |
| 전자 장치 개조 | 읽어서 전자 장치 개조 방법을 배울 수 있다. |
| 전자 장치 제작+개조 | 읽어서 전자 장치 제작 및 개조 방법을 배울 수 있다. |

“여러 물품”을 recipe 수로 자동 삽입하는 규칙을 제거했다. 영어도 make and repair fishing equipment처럼 목적어를 공유하고, 한 recipe인 경우 필요한 문법적 단수만 적용한다. recipe의 단복수와 물품의 복수성은 별개로 다룬다. EngineerMagazine2는 단일 장치 제작법 개요를 유지한다. 제작법 KO명의 오탈자를 이번에 광범위 재번역하지 않았다.

### 도구 Compact와 병렬 제작

해체 설명을 모든 표면에서 먼저 소비하던 경로를 E의 상세 설명에 한정했다. C에서는 기존 도구 목적 묶음이 해체 사실까지 함께 조립하면서 실제 대상인 **목제 계단 및 기둥 조명**을 삽입한다. 대상 근거를 새로 추정하거나 재조사하지 않았다.

Saw의 현재 C는 다음 세 문장이다.

> 사냥 장비나 폭발 장치를 만드는 데 쓸 수 있다. 음식을 손질하고 목재를 가공할 수 있다. 목제 계단 및 기둥 조명 같은 설치물을 해체하거나 산탄총의 총신을 줄일 수 있다.

GardenSaw는 같은 구조에서 산탄총 개조가 없으며, Screwdriver도 목재 가공과 구체 해체 대상을 다시 묶는다. E는 필요한 톱·드라이버와 재료 회수 설명, 다른 작업의 세부를 유지한다. C의 묶음 복구를 위해 학습 목록이나 E의 독립 용도를 합치지 않았다.

도구의 병렬 역할이 같은 제작 동사일 때 목적어를 먼저 결합한다. “사냥 장비를 만들거나 폭발 장치를 만드는 데”가 실제 노출된 전체 범위는 Saw/GardenSaw의 C/E4표면이었다. 모두 **사냥 장비나 폭발 장치를 만드는 데**로 바꿨다. 영어는 make hunting equipment and explosive devices처럼 make를 공유한다. 공통 동사가 다른 작업은 이 규칙으로 억지로 합치지 않는다.

### 검수·검증

전체2,105개 재생성 후 e9015b 후보 대비 변경28개(학습25+해체 도구3), KO/EN C/E112표면을 대조했다. 학습 목록82항목과 그 뒤의 연료 문장은 양언어 모두 전후 정확히 같음을 확인하고, 바뀐 개요와 도구 문면을 전문으로 읽었다. 용접 장비 문형은 부분 수락본 그대로다. 나머지2,077개 문면은 동일하다. 각언어/깊이 present1,976·absent129·failed0 유지.

- 기존 근거 조립+설명 조립 계약: **2 passed in30.63s, 종료 코드0**, `.tmp/prose/learning-tests.log`. 단조 분야, 제작/수리/회수/개조 구분, 구체 대상과 Compact 묶음, 목록/연료 보존을 검사한다.
- 기존 Browser/Wiki 실제 Lua 소비 harness: **IRIS_EXPANDED_MENU_PASS**, 종료 코드0, `.tmp/prose/learning-menu.log`. 전체4,210 모델 상태와 변경28개 양언어 표시를 실행해 내부 목록 줄바꿈과 독립 용도 불릿을 확인했다. 임시 fixture `.tmp/menu/learning-runtime-01/runtime`, 식별자 `l3p-b942520d8486e9ef427ed2386e2745ee2e92982a85cc503d3c62954c31741620`. 엔진 위젯/글꼴만 대체한 검증이며 실제 게임 화면 관찰이나 배포 제품 승인이 아니다.

```powershell
uv run --project .\Iris\tooling python -I -B -m pytest --noconftest -c .\Iris\tooling\pyproject.toml .\Iris\build\description\v2\tests\test_layer3_composition.py::test_layer3_composition_contract .\Iris\build\description\v2\tests\test_layer3_description_composition.py::test_layer3_description_composition --basetemp .\.tmp\learning-tests-01 -q -s --tb=short
uv run --project .\Iris\tooling python .tmp/prose/learning_menu_fixture.py
```

Descriptions SHA-256 `ade0673ec5e7523e9874214b2864cbb6433c3e13549fa24140643c3693c96c98`. Blocks SHA-256 `95df4cf33f94f86d99b699d1181a840bc4ccaa97c41291e95405b21827563e37`. Semantic correction88개 유지. 현재 바인딩과 두HTML을 갱신했다. 일반 가구 전체의 해체 대상 목록이나 새로운 물품 기능을 추가로 확정한 결과가 아니며, 기존 메뉴 fixture/실게임·제품 검증의 경계는 유지한다. 패키징·설치·커밋·푸시는 없다.

아래는 영향28개 전체의 실제 한국어 전후 C/E다. 목록과 다른 용도를 함께 남겨 개요만 비교할 때의 의미 손실을 피한다.

| 아이템 | 깊이 | 이전 | 현재 |
|---|---|---|---|
| Base.CookingMag1 | compact | 읽어서 여러 요리법을 배울 수 있다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다. | 읽어서 요리법을 배울 수 있다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다. |
| Base.CookingMag1 | expanded | 읽어서 여러 요리법을 배울 수 있다.<br>- 케이크 반죽 만들기<br>- 파이 반죽 만들기<br>- 초코칩 쿠키 도우 만들기<br>- 초콜릿 쿠키 도우 만들기<br>- 오트밀 쿠기 도우 만들기<br>- 설탕 쿠기 도우 만들기<br>- 쇼트브레드 쿠키 도우 만들기<br>모닥불 등의 연료나 불쏘시개로 쓸 수 있다. | 읽어서 요리법을 배울 수 있다.<br>- 케이크 반죽 만들기<br>- 파이 반죽 만들기<br>- 초코칩 쿠키 도우 만들기<br>- 초콜릿 쿠키 도우 만들기<br>- 오트밀 쿠기 도우 만들기<br>- 설탕 쿠기 도우 만들기<br>- 쇼트브레드 쿠키 도우 만들기<br>모닥불 등의 연료나 불쏘시개로 쓸 수 있다. |
| Base.CookingMag2 | compact | 읽어서 여러 요리법을 배울 수 있다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다. | 읽어서 요리법을 배울 수 있다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다. |
| Base.CookingMag2 | expanded | 읽어서 여러 요리법을 배울 수 있다.<br>- 빵 반죽 만들기<br>- 비스킷 만들기<br>- 피자 만들기<br>모닥불 등의 연료나 불쏘시개로 쓸 수 있다. | 읽어서 요리법을 배울 수 있다.<br>- 빵 반죽 만들기<br>- 비스킷 만들기<br>- 피자 만들기<br>모닥불 등의 연료나 불쏘시개로 쓸 수 있다. |
| Base.ElectronicsMag1 | compact | 읽어서 여러 전자 장치의 제작법을 배울 수 있다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다. | 읽어서 전자 장치 관련 제작법을 배울 수 있다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다. |
| Base.ElectronicsMag1 | expanded | 읽어서 여러 전자 장치의 제작법을 배울 수 있다.<br>- 원격제어 조정기 (V1) 만들기<br>- 원격제어 조정기 (V2) 만들기<br>- 원격제어 조정기 (V3) 만들기<br>모닥불 등의 연료나 불쏘시개로 쓸 수 있다. | 읽어서 전자 장치 관련 제작법을 배울 수 있다.<br>- 원격제어 조정기 (V1) 만들기<br>- 원격제어 조정기 (V2) 만들기<br>- 원격제어 조정기 (V3) 만들기<br>모닥불 등의 연료나 불쏘시개로 쓸 수 있다. |
| Base.ElectronicsMag2 | compact | 읽어서 여러 전자 장치의 제작법을 배울 수 있다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다. | 읽어서 전자 장치 제작 및 개조 방법을 배울 수 있다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다. |
| Base.ElectronicsMag2 | expanded | 읽어서 여러 전자 장치의 제작법을 배울 수 있다.<br>- 수제작 타이머 만들기<br>- 타이머로 추가하기<br>모닥불 등의 연료나 불쏘시개로 쓸 수 있다. | 읽어서 전자 장치 제작 및 개조 방법을 배울 수 있다.<br>- 수제작 타이머 만들기<br>- 타이머로 추가하기<br>모닥불 등의 연료나 불쏘시개로 쓸 수 있다. |
| Base.ElectronicsMag3 | compact | 읽어서 여러 전자 장치의 제작법을 배울 수 있다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다. | 읽어서 전자 장치 개조 방법을 배울 수 있다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다. |
| Base.ElectronicsMag3 | expanded | 읽어서 여러 전자 장치의 제작법을 배울 수 있다.<br>- 센서 (V1)로 추가 개조하기<br>- 센서 (V2)로 추가 개조하기<br>- 센서 (V3)로 추가 개조하기<br>모닥불 등의 연료나 불쏘시개로 쓸 수 있다. | 읽어서 전자 장치 개조 방법을 배울 수 있다.<br>- 센서 (V1)로 추가 개조하기<br>- 센서 (V2)로 추가 개조하기<br>- 센서 (V3)로 추가 개조하기<br>모닥불 등의 연료나 불쏘시개로 쓸 수 있다. |
| Base.ElectronicsMag5 | compact | 읽어서 여러 전자 장치의 제작법을 배울 수 있다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다. | 읽어서 전자 장치 제작 및 개조 방법을 배울 수 있다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다. |
| Base.ElectronicsMag5 | expanded | 읽어서 여러 전자 장치의 제작법을 배울 수 있다.<br>- 수제작 원격 폭탄 격발기 만들기<br>- 격발기 만들기<br>모닥불 등의 연료나 불쏘시개로 쓸 수 있다. | 읽어서 전자 장치 제작 및 개조 방법을 배울 수 있다.<br>- 수제작 원격 폭탄 격발기 만들기<br>- 격발기 만들기<br>모닥불 등의 연료나 불쏘시개로 쓸 수 있다. |
| Base.EngineerMagazine1 | compact | 읽어서 전자 장치의 제작법을 배울 수 있다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다. | 읽어서 전자 장치 관련 제작법을 배울 수 있다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다. |
| Base.EngineerMagazine1 | expanded | 읽어서 전자 장치의 제작법을 배울 수 있다.<br>- 소음 발생기 만들기<br>모닥불 등의 연료나 불쏘시개로 쓸 수 있다. | 읽어서 전자 장치 관련 제작법을 배울 수 있다.<br>- 소음 발생기 만들기<br>모닥불 등의 연료나 불쏘시개로 쓸 수 있다. |
| Base.EngineerMagazine2 | compact | 읽어서 장치의 제작법을 배울 수 있다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다. | 읽어서 장치 제작법을 배울 수 있다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다. |
| Base.EngineerMagazine2 | expanded | 읽어서 장치의 제작법을 배울 수 있다.<br>- 연막 폭탄 만들기<br>모닥불 등의 연료나 불쏘시개로 쓸 수 있다. | 읽어서 장치 제작법을 배울 수 있다.<br>- 연막 폭탄 만들기<br>모닥불 등의 연료나 불쏘시개로 쓸 수 있다. |
| Base.FarmingMag1 | compact | 읽어서 여러 작물 치료제의 제작법을 배울 수 있다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다. | 읽어서 작물 치료제를 만드는 방법을 배울 수 있다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다. |
| Base.FarmingMag1 | expanded | 읽어서 여러 작물 치료제의 제작법을 배울 수 있다.<br>- 곰팡이 제거제 만들기<br>- 살충제 만들기<br>모닥불 등의 연료나 불쏘시개로 쓸 수 있다. | 읽어서 작물 치료제를 만드는 방법을 배울 수 있다.<br>- 곰팡이 제거제 만들기<br>- 살충제 만들기<br>모닥불 등의 연료나 불쏘시개로 쓸 수 있다. |
| Base.FishingMag1 | compact | 읽어서 여러 낚시 장비의 제작법을 배울 수 있다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다. | 읽어서 낚시 장비 제작 및 수리 방법을 배울 수 있다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다. |
| Base.FishingMag1 | expanded | 읽어서 여러 낚시 장비의 제작법을 배울 수 있다.<br>- 낚싯대 만들기<br>- 낚싯대 수리하기<br>모닥불 등의 연료나 불쏘시개로 쓸 수 있다. | 읽어서 낚시 장비 제작 및 수리 방법을 배울 수 있다.<br>- 낚싯대 만들기<br>- 낚싯대 수리하기<br>모닥불 등의 연료나 불쏘시개로 쓸 수 있다. |
| Base.FishingMag2 | compact | 읽어서 여러 낚시 장비의 제작법을 배울 수 있다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다. | 읽어서 낚시 장비 제작 및 재료 회수 방법을 배울 수 있다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다. |
| Base.FishingMag2 | expanded | 읽어서 여러 낚시 장비의 제작법을 배울 수 있다.<br>- 어망 만들기<br>- 철사 회수하기<br>모닥불 등의 연료나 불쏘시개로 쓸 수 있다. | 읽어서 낚시 장비 제작 및 재료 회수 방법을 배울 수 있다.<br>- 어망 만들기<br>- 철사 회수하기<br>모닥불 등의 연료나 불쏘시개로 쓸 수 있다. |
| Base.GardenSaw | compact | 목재를 가공하는 데 쓸 수 있다. 목제 계단 및 기둥 조명 같은 설치물을 해체해 재료를 회수하는 데 쓸 수 있다. 사냥 장비를 만들거나 폭발 장치를 만드는 데 쓸 수 있다. 음식을 나누는 데 쓸 수 있다. | 사냥 장비나 폭발 장치를 만드는 데 쓸 수 있다. 음식을 손질하고 목재를 가공할 수 있다. 목제 계단 및 기둥 조명 같은 설치물을 해체할 수 있다. |
| Base.GardenSaw | expanded | 목재를 가공하는 데 쓸 수 있다.<br>톱과 드라이버로 목제 계단 및 기둥 조명 같은 설치물을 해체해 재료를 회수하는 데 쓸 수 있다.<br>사냥 장비를 만들거나 폭발 장치를 만드는 데 쓸 수 있다.<br>음식을 나누는 데 쓸 수 있다. | 사냥 장비나 폭발 장치를 만드는 데 쓸 수 있다.<br>음식을 나누는 데 쓸 수 있다.<br>목재를 가공하는 데 쓸 수 있다.<br>톱과 드라이버로 목제 계단 및 기둥 조명 같은 설치물을 해체해 재료를 회수하는 데 쓸 수 있다. |
| Base.HuntingMag1 | compact | 읽어서 덫의 제작법을 배울 수 있다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다. | 읽어서 덫을 만드는 방법을 배울 수 있다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다. |
| Base.HuntingMag1 | expanded | 읽어서 덫의 제작법을 배울 수 있다.<br>- 올가미 덫 만들기<br>모닥불 등의 연료나 불쏘시개로 쓸 수 있다. | 읽어서 덫을 만드는 방법을 배울 수 있다.<br>- 올가미 덫 만들기<br>모닥불 등의 연료나 불쏘시개로 쓸 수 있다. |
| Base.HuntingMag2 | compact | 읽어서 여러 덫의 제작법을 배울 수 있다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다. | 읽어서 덫을 만드는 방법을 배울 수 있다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다. |
| Base.HuntingMag2 | expanded | 읽어서 여러 덫의 제작법을 배울 수 있다.<br>- 나무 상자 덫 만들기<br>- 막대 덫 만들기<br>모닥불 등의 연료나 불쏘시개로 쓸 수 있다. | 읽어서 덫을 만드는 방법을 배울 수 있다.<br>- 나무 상자 덫 만들기<br>- 막대 덫 만들기<br>모닥불 등의 연료나 불쏘시개로 쓸 수 있다. |
| Base.HuntingMag3 | compact | 읽어서 여러 덫의 제작법을 배울 수 있다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다. | 읽어서 덫을 만드는 방법을 배울 수 있다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다. |
| Base.HuntingMag3 | expanded | 읽어서 여러 덫의 제작법을 배울 수 있다.<br>- 덫상자 만들기<br>- 철장 덫 만들기<br>모닥불 등의 연료나 불쏘시개로 쓸 수 있다. | 읽어서 덫을 만드는 방법을 배울 수 있다.<br>- 덫상자 만들기<br>- 철장 덫 만들기<br>모닥불 등의 연료나 불쏘시개로 쓸 수 있다. |
| Base.MetalworkMag1 | compact | 읽어서 여러 금속 구조물의 제작법을 배울 수 있다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다. | 읽어서 금속 구조물을 만드는 방법을 배울 수 있다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다. |
| Base.MetalworkMag1 | expanded | 읽어서 여러 금속 구조물의 제작법을 배울 수 있다.<br>- 금속 벽 만들기<br>- 금속 지붕 만들기<br>모닥불 등의 연료나 불쏘시개로 쓸 수 있다. | 읽어서 금속 구조물을 만드는 방법을 배울 수 있다.<br>- 금속 벽 만들기<br>- 금속 지붕 만들기<br>모닥불 등의 연료나 불쏘시개로 쓸 수 있다. |
| Base.MetalworkMag2 | compact | 읽어서 금속 구조물의 제작법을 배울 수 있다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다. | 읽어서 금속 구조물을 만드는 방법을 배울 수 있다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다. |
| Base.MetalworkMag2 | expanded | 읽어서 금속 구조물의 제작법을 배울 수 있다.<br>- 금속 보관함 만들기<br>모닥불 등의 연료나 불쏘시개로 쓸 수 있다. | 읽어서 금속 구조물을 만드는 방법을 배울 수 있다.<br>- 금속 보관함 만들기<br>모닥불 등의 연료나 불쏘시개로 쓸 수 있다. |
| Base.MetalworkMag3 | compact | 읽어서 금속 구조물의 제작법을 배울 수 있다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다. | 읽어서 금속 구조물을 만드는 방법을 배울 수 있다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다. |
| Base.MetalworkMag3 | expanded | 읽어서 금속 구조물의 제작법을 배울 수 있다.<br>- 금속 울타리 만들기<br>모닥불 등의 연료나 불쏘시개로 쓸 수 있다. | 읽어서 금속 구조물을 만드는 방법을 배울 수 있다.<br>- 금속 울타리 만들기<br>모닥불 등의 연료나 불쏘시개로 쓸 수 있다. |
| Base.MetalworkMag4 | compact | 읽어서 여러 금속 물품의 제작법을 배울 수 있다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다. | 읽어서 금속 가공 방법을 배울 수 있다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다. |
| Base.MetalworkMag4 | expanded | 읽어서 여러 금속 물품의 제작법을 배울 수 있다.<br>- 금속판 만들기<br>- 작은 금속판 만들기<br>모닥불 등의 연료나 불쏘시개로 쓸 수 있다. | 읽어서 금속 가공 방법을 배울 수 있다.<br>- 금속판 만들기<br>- 작은 금속판 만들기<br>모닥불 등의 연료나 불쏘시개로 쓸 수 있다. |
| Base.Saw | compact | 목재를 가공하는 데 쓸 수 있다. 목제 계단 및 기둥 조명 같은 설치물을 해체해 재료를 회수하는 데 쓸 수 있다. 사냥 장비를 만들거나 폭발 장치를 만드는 데 쓸 수 있다. 음식을 나누는 데 쓸 수 있다. 산탄총의 총신을 줄이는 도구로 쓸 수 있다. | 사냥 장비나 폭발 장치를 만드는 데 쓸 수 있다. 음식을 손질하고 목재를 가공할 수 있다. 목제 계단 및 기둥 조명 같은 설치물을 해체하거나 산탄총의 총신을 줄일 수 있다. |
| Base.Saw | expanded | 목재를 가공하는 데 쓸 수 있다.<br>톱과 드라이버로 목제 계단 및 기둥 조명 같은 설치물을 해체해 재료를 회수하는 데 쓸 수 있다.<br>사냥 장비를 만들거나 폭발 장치를 만드는 데 쓸 수 있다.<br>음식을 나누는 데 쓸 수 있다.<br>산탄총의 총신을 줄이는 도구로 쓸 수 있다. | 사냥 장비나 폭발 장치를 만드는 데 쓸 수 있다.<br>음식을 나누는 데 쓸 수 있다.<br>목재를 가공하는 데 쓸 수 있다.<br>톱과 드라이버로 목제 계단 및 기둥 조명 같은 설치물을 해체해 재료를 회수하는 데 쓸 수 있다.<br>산탄총의 총신을 줄이는 도구로 쓸 수 있다. |
| Base.Screwdriver | compact | 목재를 가공할 수 있다. 차량 부품과 호환 무기 부착물을 장착하거나 제거할 수 있다. 제작한 창에 부착하거나 무기로 쓸 수도 있다. 목제 계단 및 기둥 조명 같은 설치물을 해체해 재료를 회수하는 데 쓸 수 있다. 전자기기를 만들거나 분해하고, 조명을 건전지용으로 개조할 수 있다. | 전자기기를 만들거나 분해하고, 조명을 건전지용으로 개조할 수 있다. 목재를 가공하거나 목제 계단 및 기둥 조명 같은 설치물을 해체할 수 있다. 차량 부품과 호환 무기 부착물을 장착하거나 제거할 수 있다. 제작한 창에 부착하거나 무기로 쓸 수도 있다. |
| Base.Screwdriver | expanded | 목재를 가공하는 데 쓸 수 있다.<br>톱과 드라이버로 목제 계단 및 기둥 조명 같은 설치물을 해체해 재료를 회수하는 데 쓸 수 있다.<br>차량 부품을 장착하거나 탈거하는 데 사용할 수 있다.<br>호환 무기의 부착물을 장착하거나 제거할 수 있다.<br>제작한 창에 부착해 쓸 수 있다.<br>무기로 쓸 수 있다.<br>전자 부품과 무전기를 만들 수 있다. 라디오와 TV를 포함한 전자기기를 분해해 부품을 회수할 수 있다. 조명을 건전지용으로 개조할 수 있다. | 전자 부품과 무전기를 만들 수 있다. 라디오와 TV를 포함한 전자기기를 분해해 부품을 회수할 수 있다. 조명을 건전지용으로 개조할 수 있다.<br>목재를 가공하는 데 쓸 수 있다.<br>톱과 드라이버로 목제 계단 및 기둥 조명 같은 설치물을 해체해 재료를 회수하는 데 쓸 수 있다.<br>차량 부품을 장착하거나 탈거하는 데 사용할 수 있다.<br>호환 무기의 부착물을 장착하거나 제거할 수 있다.<br>제작한 창에 부착해 쓸 수 있다.<br>무기로 쓸 수 있다. |
| Base.SmithingMag1 | compact | 읽어서 여러 금속 물품의 제작법을 배울 수 있다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다. | 읽어서 금속을 단조해 물품을 만드는 방법을 배울 수 있다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다. |
| Base.SmithingMag1 | expanded | 읽어서 여러 금속 물품의 제작법을 배울 수 있다.<br>- 포크 만들기<br>- 숟가락 만들기<br>- 조리용 냄비 만들기<br>- 오븐 쟁반 만들기<br>- 손잡이 냄비 만들기<br>- 빵 판 만들기<br>- 빵 굽는 팬 만들기<br>- 프라이팬 만들기<br>모닥불 등의 연료나 불쏘시개로 쓸 수 있다. | 읽어서 금속을 단조해 물품을 만드는 방법을 배울 수 있다.<br>- 포크 만들기<br>- 숟가락 만들기<br>- 조리용 냄비 만들기<br>- 오븐 쟁반 만들기<br>- 손잡이 냄비 만들기<br>- 빵 판 만들기<br>- 빵 굽는 팬 만들기<br>- 프라이팬 만들기<br>모닥불 등의 연료나 불쏘시개로 쓸 수 있다. |
| Base.SmithingMag2 | compact | 읽어서 여러 금속 물품의 제작법을 배울 수 있다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다. | 읽어서 금속을 단조해 물품을 만드는 방법을 배울 수 있다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다. |
| Base.SmithingMag2 | expanded | 읽어서 여러 금속 물품의 제작법을 배울 수 있다.<br>- 편지 개봉칼 만들기<br>- 못 만들기<br>- 종이 집게 만들기<br>- 가위 만들기<br>- 문 손잡이 만들기<br>- 경첩 만들기<br>- 버터칼 만들기<br>- 둥근 망치 만들기<br>모닥불 등의 연료나 불쏘시개로 쓸 수 있다. | 읽어서 금속을 단조해 물품을 만드는 방법을 배울 수 있다.<br>- 편지 개봉칼 만들기<br>- 못 만들기<br>- 종이 집게 만들기<br>- 가위 만들기<br>- 문 손잡이 만들기<br>- 경첩 만들기<br>- 버터칼 만들기<br>- 둥근 망치 만들기<br>모닥불 등의 연료나 불쏘시개로 쓸 수 있다. |
| Base.SmithingMag3 | compact | 읽어서 여러 금속 물품의 제작법을 배울 수 있다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다. | 읽어서 금속을 단조해 물품을 만드는 방법을 배울 수 있다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다. |
| Base.SmithingMag3 | expanded | 읽어서 여러 금속 물품의 제작법을 배울 수 있다.<br>- 집게 만들기<br>- 망치 만들기<br>- 금속판 만들기<br>- 봉합용 바늘 집개 만들기<br>- 핀셋 만들기<br>- 봉합용 바늘 만들기<br>- 드럼통 만들기<br>- 부엌칼 만들기<br>- 톱 만들기<br>- 사냥용 칼 만들기<br>- 삽 만들기<br>- 모종삽 만들기<br>모닥불 등의 연료나 불쏘시개로 쓸 수 있다. | 읽어서 금속을 단조해 물품을 만드는 방법을 배울 수 있다.<br>- 집게 만들기<br>- 망치 만들기<br>- 금속판 만들기<br>- 봉합용 바늘 집개 만들기<br>- 핀셋 만들기<br>- 봉합용 바늘 만들기<br>- 드럼통 만들기<br>- 부엌칼 만들기<br>- 톱 만들기<br>- 사냥용 칼 만들기<br>- 삽 만들기<br>- 모종삽 만들기<br>모닥불 등의 연료나 불쏘시개로 쓸 수 있다. |
| Base.SmithingMag4 | compact | 읽어서 여러 금속 물품의 제작법을 배울 수 있다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다. | 읽어서 금속을 단조해 물품을 만드는 방법을 배울 수 있다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다. |
| Base.SmithingMag4 | expanded | 읽어서 여러 금속 물품의 제작법을 배울 수 있다.<br>- 9mm 탄 틀 만들기<br>- .308 탄 틀 만들기<br>- .223 탄 틀 만들기<br>- 산탄 총탄 틀 만들기<br>- 9mm 탄 만들기<br>- 산탄 총탄 만들기<br>- .308 탄 만들기<br>- .223 탄 만들기<br>- 쇠지렛대 만들기<br>- 골프 클럽 만들기<br>- 도끼 만들기<br>- 대형 망치 만들기<br>모닥불 등의 연료나 불쏘시개로 쓸 수 있다. | 읽어서 금속을 단조해 물품을 만드는 방법을 배울 수 있다.<br>- 9mm 탄 틀 만들기<br>- .308 탄 틀 만들기<br>- .223 탄 틀 만들기<br>- 산탄 총탄 틀 만들기<br>- 9mm 탄 만들기<br>- 산탄 총탄 만들기<br>- .308 탄 만들기<br>- .223 탄 만들기<br>- 쇠지렛대 만들기<br>- 골프 클럽 만들기<br>- 도끼 만들기<br>- 대형 망치 만들기<br>모닥불 등의 연료나 불쏘시개로 쓸 수 있다. |
| Radio.RadioMag1 | compact | 읽어서 전자 장치의 제작법을 배울 수 있다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다. | 읽어서 전자 장치 관련 제작법을 배울 수 있다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다. |
| Radio.RadioMag1 | expanded | 읽어서 전자 장치의 제작법을 배울 수 있다.<br>- 수제작 라디오 만들기<br>모닥불 등의 연료나 불쏘시개로 쓸 수 있다. | 읽어서 전자 장치 관련 제작법을 배울 수 있다.<br>- 수제작 라디오 만들기<br>모닥불 등의 연료나 불쏘시개로 쓸 수 있다. |
| Radio.RadioMag2 | compact | 읽어서 전자 장치의 제작법을 배울 수 있다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다. | 읽어서 전자 장치 관련 제작법을 배울 수 있다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다. |
| Radio.RadioMag2 | expanded | 읽어서 전자 장치의 제작법을 배울 수 있다.<br>- 수제작 휴대용 무전기 만들기<br>모닥불 등의 연료나 불쏘시개로 쓸 수 있다. | 읽어서 전자 장치 관련 제작법을 배울 수 있다.<br>- 수제작 휴대용 무전기 만들기<br>모닥불 등의 연료나 불쏘시개로 쓸 수 있다. |
| Radio.RadioMag3 | compact | 읽어서 전자 장치의 제작법을 배울 수 있다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다. | 읽어서 전자 장치 관련 제작법을 배울 수 있다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다. |
| Radio.RadioMag3 | expanded | 읽어서 전자 장치의 제작법을 배울 수 있다.<br>- 수제작 아마추어 무선통신기 만들기<br>모닥불 등의 연료나 불쏘시개로 쓸 수 있다. | 읽어서 전자 장치 관련 제작법을 배울 수 있다.<br>- 수제작 아마추어 무선통신기 만들기<br>모닥불 등의 연료나 불쏘시개로 쓸 수 있다. |


## 2026-09-14 대상 구체화·연료 역할·소독 묶음·표시명 교정

기준본 ade067의 잔여 지적과 사용자가 추가 승인한 원본 번역 오탈자 교정을 적용했다. 전체 2,105개를 재생성했다. 변경 42개, 121표면(KO C39/E36, EN C26/E20)이며 해당 42개의 KO/EN C/E 전부를 기준본과 대조했다. 항목별 public 상태는 모두 동일하고 각 언어/표면 present 1,976·absent 129·failed 0이다.

### 해결한 범위와 실제 대상 근거

| 공통 규칙 | 전체 문구 영향 범위 | 결과 |
|---|---|---|
| 페인트 대상 | 페인트 15개 + 붓 1개, KO/EN C/E | 벽·문틀·창틀·기둥 및 일부 문·의자·상자·탁자 범주를 제시. 벽 표식 용도 별도 보존 |
| 자물쇠 대상 | Padlock, CombinationPadlock, KO/EN C/E | 제작한 나무 상자 같은 보관함 예시. 문 제외와 비밀번호 해제 보존 |
| 점화 연료 | 휘발유 용기 6개, KO/EN C | E의 점화 연료 역할을 C에도 보존. 시신 소각·차량 연료 수집/급유·발전기·화염 장치 제작은 그대로 |
| 소독 목적 | Disinfectant, WhiskeyFull, KO/EN C/E | 천·솜·상처를 한 소독 문장으로 묶음. 위스키의 음용·요리·화염 장치 제작 유지 |
| 단조 재료 문형 | Handle KO C/E, IronIngot KO E | ‘금속을 단조할 때 재료로 쓸 수 있다’. IronIngot C의 용접+단조 묶음은 유지 |
| 동일 도구 이름 | 전자기기 분해 12개 KO C/E | Base.Screwdriver 표시명을 드라이버로 통일. 회수물·조건부 건전지·다른 목적 유지 |
| 원본 번역 오탈자 | CookingMag1, SmithingMag3 KO E | 오트밀/설탕 쿠키 도우, 봉합용 바늘 집게. 원본명·키 보존 |

페인트는 `PaintingReference.lua:11–141`의 wall/doorframe/windowsframe/pillar와 `:144–207`의 chair/crates/door/table 색 대응표를 확인했다. 실제 `ISPaintCursor.lua:210–223`와 `ISPaintMenu.lua:96–122`가 이 대응표를 적용하므로 단순 이름 추정이 아니다. 모든 가구를 대상으로 넓히지 않고 일부 가구 범주로 기술했다. 이미 채택된 surface painting과 wall sign 기능은 구분한다.

자물쇠는 `ISBuildMenu.lua:1203–1216`의 나무 상자 제작 → `ISWoodenContainer.lua:11–16,34–47` → `ISBuildUtil.lua:353–354`의 padlock 허용 전달 → `ISWorldObjectContextMenu.lua:199–201`의 비문(non-door) 대상 경로를 확인했다. 바닐라 전체 잠금 대상 목록을 새로 추정하지 않고 제작한 나무 상자를 예시로 쓴다. 조사한 7개 파일의 경로와 해시는 relation_adapter.paint_and_padlock_target_sources에 묶었다.

다른 계층도 실제 읽었다. 현재 L4 UseCases._getDescriptionState의 Paintbrush/PaintBlack/Padlock/CombinationPadlock은 모두 verified_empty/lookup_miss/0줄이었다(`.tmp/prose/residual-l4.lua`, lua 종료 코드 0). 다른 계층에 대상 안내가 있다고 가정하지 않았다.

### 공통화와 의미 보존

점화 도구와 연료는 기존 채택 기능 관계로 구분한다. 연료는 Compact에서 일반 점화 문장으로 축약하지 않고 기존 E 연료 프레임으로 처리한다. 점화 절차 전체나 필요 도구 나열로 확대하지 않았다.

소독은 bandaging_material_preparation의 재료 역할과 disinfect_wound가 함께 있는 경우에만 묶는다. 소독솜 제작 대상인 CottonBalls, 소독될 붕대, 물의 세척 역할을 소독제 역할로 바꾸지 않는다. 기존 CottonBalls/붕대 검사도 유지했다. 두 표면을 억지로 다르게 만들지 않는다.

표시명은 recovery_relations의 기존 ItemName/Recipes 번역 읽기 경로에서 최소 문자열 교정한다. 스크류드라이버→드라이버, 쿠기→쿠키, 봉합용 바늘 집개→봉합용 바늘 집게이며 동일 표기를 읽는 모든 관계에 적용한다. 원본 번역 파일은 변경하지 않았다. 관계의 source_names 및 학습 recipe의 source_names/key가 원래 이름과 대응을 보존한다. 제작법 자유 재번역이나 아이템별 완성 문장 덮어쓰기를 사용하지 않았다. 실제 공개 본문에는 이전 오탈자/도구명 변형 0건이다.

학습 목록 82개(제작75·개조5·수리1·회수1)는 원본 key/operation과 순서를 보존했다. KO 목록의 승인된 철자 교정 3곳 이외의 목록 문구와 모든 EN 목록은 동일하다. 톱·정원용 톱·드라이버의 기존 목적 묶음, 용접 마스크, 알려진 부착물 사용, 금속 가공/단조/건축의 구분은 유지했다. 수치·효과·조건은 일괄 삭제하지 않았다.

### 검사 및 판단의 한계

- 첫 기존 계약 실행: 1 passed / 1 failed. 기존 ‘천이나 솜을 소독’ 고정 문자열 검증이 의도된 통합 문장과 충돌했다. 천·솜·상처와 다른 용도 보존 및 소독 반복 감소를 확인하도록 기존 검증을 수정했다.
- 최종 기존 composition/description 계약 2개: **2 passed in 29.95s, 종료 코드 0** (`.tmp/prose/residual-tests-final.log`). 명령은 `uv run --project .\Iris\tooling python -I -B -m pytest --noconftest -c .\Iris\tooling\pyproject.toml .\Iris\build\description\v2\tests\test_layer3_composition.py::test_layer3_composition_contract .\Iris\build\description\v2\tests\test_layer3_description_composition.py::test_layer3_description_composition --basetemp .\.tmp\residual-tests-02 -q -s --tb=short`.
- 전후 대조 및 회귀 확인: `uv run --project .\Iris\tooling python .tmp/prose/residual-audit.py`, 종료 코드 0. 전체 영향 항목의 KO/EN C/E를 읽고 동일 전문은 16개 묶음으로 확인했다. 원본 42개 전후 전문은 아래에 보존한다.
- 실제 Browser/Wiki 소비 코드: `uv run --project .\Iris\tooling python .tmp/prose/residual_menu_fixture.py`, 종료 코드 0. 4,210 상태 및 변경42개 KO/EN 표시, 줄바꿈·목록·스크롤 검사. fixture `l3p-9c478761a15820b8a1b02170bda084917b15e524a2b2fc4f60acd892c0009e34`, `.tmp/menu/residual-runtime-01/runtime`.

판정: 이번 다섯 교정 범위는 구현 및 문장 대조 완료다. 페인트/잠금의 모든 월드 대상 개별 목록과 실제 게임 화면은 조사 완료로 주장하지 않는다. 임시 소비 검증은 엔진/폰트 stub를 사용하며 제품 ZIP, 설치 또는 실제 게임 화면 검증이 아니다. 가구와 목적 미확정 부착물의 근거 없는 목적 설명은 새로 만들지 않았다. 테스트 통과가 전체 문장 품질 수락을 대신하지 않는다.

현재 descriptions SHA-256: `952913e3cca7244d2a7a81a9eb574ff02c9de0991f0ab58f57670b9ef093e2d8`

현재 blocks SHA-256: `2b74f2bfe796268cb21b4c4af81b49bd6fcc9af580ba259e6824ad5911f0a37e`

### 영향 42개 전체 KO/EN C/E 전후 전문

```text
Base.Camera
ko/compact
BEFORE 스크류드라이버로 분해해 전기 회로 부속을 얻을 수 있다.
AFTER 드라이버로 분해해 전기 회로 부속을 얻을 수 있다.
ko/expanded
BEFORE 스크류드라이버로 분해해 전기 회로 부속을 얻을 수 있다.
AFTER 드라이버로 분해해 전기 회로 부속을 얻을 수 있다.
en/compact
BEFORE It can be dismantled with a Screwdriver to obtain Electronics Scrap.
AFTER It can be dismantled with a Screwdriver to obtain Electronics Scrap.
en/expanded
BEFORE It can be dismantled with a Screwdriver to obtain Electronics Scrap.
AFTER It can be dismantled with a Screwdriver to obtain Electronics Scrap.
Base.CameraDisposable
ko/compact
BEFORE 스크류드라이버로 분해해 전기 회로 부속을 얻을 수 있다.
AFTER 드라이버로 분해해 전기 회로 부속을 얻을 수 있다.
ko/expanded
BEFORE 스크류드라이버로 분해해 전기 회로 부속을 얻을 수 있다.
AFTER 드라이버로 분해해 전기 회로 부속을 얻을 수 있다.
en/compact
BEFORE It can be dismantled with a Screwdriver to obtain Electronics Scrap.
AFTER It can be dismantled with a Screwdriver to obtain Electronics Scrap.
en/expanded
BEFORE It can be dismantled with a Screwdriver to obtain Electronics Scrap.
AFTER It can be dismantled with a Screwdriver to obtain Electronics Scrap.
Base.CameraExpensive
ko/compact
BEFORE 스크류드라이버로 분해해 전기 회로 부속을 얻을 수 있다.
AFTER 드라이버로 분해해 전기 회로 부속을 얻을 수 있다.
ko/expanded
BEFORE 스크류드라이버로 분해해 전기 회로 부속을 얻을 수 있다.
AFTER 드라이버로 분해해 전기 회로 부속을 얻을 수 있다.
en/compact
BEFORE It can be dismantled with a Screwdriver to obtain Electronics Scrap.
AFTER It can be dismantled with a Screwdriver to obtain Electronics Scrap.
en/expanded
BEFORE It can be dismantled with a Screwdriver to obtain Electronics Scrap.
AFTER It can be dismantled with a Screwdriver to obtain Electronics Scrap.
Base.CombinationPadlock
ko/compact
BEFORE 비밀번호로 구조물을 잠그거나 잠금을 해제할 수 있다. 문에는 쓸 수 없다.
AFTER 제작한 나무 상자 같은 보관함을 비밀번호로 잠그거나 잠금을 해제할 수 있다. 문에는 쓸 수 없다.
ko/expanded
BEFORE 자물쇠를 달 수 있는 구조물에 비밀번호 잠금을 설정할 수 있다. 설정한 번호로 잠금을 해제할 수 있다. 문에는 쓸 수 없다.
AFTER 제작한 나무 상자 같은 보관함에 비밀번호 잠금을 설정할 수 있다. 설정한 번호로 잠금을 해제할 수 있다. 문에는 쓸 수 없다.
en/compact
BEFORE It can lock or unlock structures with a code, except doors.
AFTER It can lock or unlock storage containers such as crafted wooden crates with a code, except doors.
en/expanded
BEFORE It can secure structures that accept padlocks with a chosen code. The configured code can unlock them. It cannot be used on doors.
AFTER It can secure storage containers such as crafted wooden crates with a chosen code. The configured code can unlock them. It cannot be used on doors.
Base.CookingMag1
ko/compact
BEFORE 읽어서 요리법을 배울 수 있다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다.
AFTER 읽어서 요리법을 배울 수 있다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다.
ko/expanded
BEFORE 읽어서 요리법을 배울 수 있다.
- 케이크 반죽 만들기
- 파이 반죽 만들기
- 초코칩 쿠키 도우 만들기
- 초콜릿 쿠키 도우 만들기
- 오트밀 쿠기 도우 만들기
- 설탕 쿠기 도우 만들기
- 쇼트브레드 쿠키 도우 만들기
모닥불 등의 연료나 불쏘시개로 쓸 수 있다.
AFTER 읽어서 요리법을 배울 수 있다.
- 케이크 반죽 만들기
- 파이 반죽 만들기
- 초코칩 쿠키 도우 만들기
- 초콜릿 쿠키 도우 만들기
- 오트밀 쿠키 도우 만들기
- 설탕 쿠키 도우 만들기
- 쇼트브레드 쿠키 도우 만들기
모닥불 등의 연료나 불쏘시개로 쓸 수 있다.
en/compact
BEFORE It can be read to learn cooking recipes. It can be used as fuel or tinder, for example in campfires.
AFTER It can be read to learn cooking recipes. It can be used as fuel or tinder, for example in campfires.
en/expanded
BEFORE It can be read to learn cooking recipes.
- Make Cake Batter
- Make Pie Dough
- Make Chocolate Chip Cookie Dough
- Make Chocolate Cookie Dough
- Make Oatmeal Cookie Dough
- Make Sugar Cookie Dough
- Make Shortbread Cookie Dough
It can be used as fuel or tinder, for example in campfires.
AFTER It can be read to learn cooking recipes.
- Make Cake Batter
- Make Pie Dough
- Make Chocolate Chip Cookie Dough
- Make Chocolate Cookie Dough
- Make Oatmeal Cookie Dough
- Make Sugar Cookie Dough
- Make Shortbread Cookie Dough
It can be used as fuel or tinder, for example in campfires.
Base.CordlessPhone
ko/compact
BEFORE 스크류드라이버로 분해해 전기 회로 부속을 얻을 수 있다.
AFTER 드라이버로 분해해 전기 회로 부속을 얻을 수 있다.
ko/expanded
BEFORE 스크류드라이버로 분해해 전기 회로 부속을 얻을 수 있다.
AFTER 드라이버로 분해해 전기 회로 부속을 얻을 수 있다.
en/compact
BEFORE It can be dismantled with a Screwdriver to obtain Electronics Scrap.
AFTER It can be dismantled with a Screwdriver to obtain Electronics Scrap.
en/expanded
BEFORE It can be dismantled with a Screwdriver to obtain Electronics Scrap.
AFTER It can be dismantled with a Screwdriver to obtain Electronics Scrap.
Base.Disinfectant
ko/compact
BEFORE 천이나 솜을 소독하는 데 쓸 수 있다. 상처를 소독할 수 있다.
AFTER 천, 솜, 상처를 소독하는 데 쓸 수 있다.
ko/expanded
BEFORE 천이나 솜을 소독하는 데 쓸 수 있다.
상처를 소독할 수 있다.
AFTER 천, 솜, 상처를 소독하는 데 쓸 수 있다.
en/compact
BEFORE It can be used to disinfect cloth or cotton. It can be used to disinfect wounds.
AFTER It can be used to disinfect cloth, cotton or wounds.
en/expanded
BEFORE It can be used to disinfect cloth or cotton.
It can be used to disinfect wounds.
AFTER It can be used to disinfect cloth, cotton or wounds.
Base.Earbuds
ko/compact
BEFORE 호환되는 휴대 기기의 소리를 듣는 데 쓸 수 있다. 스크류드라이버로 분해해 전기 회로 부속을 얻을 수 있다.
AFTER 호환되는 휴대 기기의 소리를 듣는 데 쓸 수 있다. 드라이버로 분해해 전기 회로 부속을 얻을 수 있다.
ko/expanded
BEFORE 호환되는 휴대 기기의 소리를 듣는 데 쓸 수 있다.
스크류드라이버로 분해해 전기 회로 부속을 얻을 수 있다.
AFTER 호환되는 휴대 기기의 소리를 듣는 데 쓸 수 있다.
드라이버로 분해해 전기 회로 부속을 얻을 수 있다.
en/compact
BEFORE It can be used to listen to audio from compatible portable devices. It can be dismantled with a Screwdriver to obtain Electronics Scrap.
AFTER It can be used to listen to audio from compatible portable devices. It can be dismantled with a Screwdriver to obtain Electronics Scrap.
en/expanded
BEFORE It can be used to listen to audio from compatible portable devices.
It can be dismantled with a Screwdriver to obtain Electronics Scrap.
AFTER It can be used to listen to audio from compatible portable devices.
It can be dismantled with a Screwdriver to obtain Electronics Scrap.
Base.HandTorch
ko/compact
BEFORE 휴대 조명으로 쓸 수 있다. 스크류드라이버로 분해해 전기 회로 부속을 얻을 수 있다.
AFTER 휴대 조명으로 쓸 수 있다. 드라이버로 분해해 전기 회로 부속을 얻을 수 있다.
ko/expanded
BEFORE 휴대 조명으로 쓸 수 있다.
스크류드라이버로 분해해 전기 회로 부속을 얻을 수 있다.
AFTER 휴대 조명으로 쓸 수 있다.
드라이버로 분해해 전기 회로 부속을 얻을 수 있다.
en/compact
BEFORE It can be used as a portable light. It can be dismantled with a Screwdriver to obtain Electronics Scrap.
AFTER It can be used as a portable light. It can be dismantled with a Screwdriver to obtain Electronics Scrap.
en/expanded
BEFORE It can be used as a portable light.
It can be dismantled with a Screwdriver to obtain Electronics Scrap.
AFTER It can be used as a portable light.
It can be dismantled with a Screwdriver to obtain Electronics Scrap.
Base.Handle
ko/compact
BEFORE 금속을 단조하는 재료로 쓸 수 있다.
AFTER 금속을 단조할 때 재료로 쓸 수 있다.
ko/expanded
BEFORE 금속 단조의 재료로 사용할 수 있다.
AFTER 금속을 단조할 때 재료로 쓸 수 있다.
en/compact
BEFORE It can supply material for metal forging.
AFTER It can supply material for metal forging.
en/expanded
BEFORE It can be used as material for metal forging.
AFTER It can be used as material for metal forging.
Base.Headphones
ko/compact
BEFORE 호환되는 휴대 기기의 소리를 듣는 데 쓸 수 있다. 스크류드라이버로 분해해 전기 회로 부속을 얻을 수 있다.
AFTER 호환되는 휴대 기기의 소리를 듣는 데 쓸 수 있다. 드라이버로 분해해 전기 회로 부속을 얻을 수 있다.
ko/expanded
BEFORE 호환되는 휴대 기기의 소리를 듣는 데 쓸 수 있다.
스크류드라이버로 분해해 전기 회로 부속을 얻을 수 있다.
AFTER 호환되는 휴대 기기의 소리를 듣는 데 쓸 수 있다.
드라이버로 분해해 전기 회로 부속을 얻을 수 있다.
en/compact
BEFORE It can be used to listen to audio from compatible portable devices. It can be dismantled with a Screwdriver to obtain Electronics Scrap.
AFTER It can be used to listen to audio from compatible portable devices. It can be dismantled with a Screwdriver to obtain Electronics Scrap.
en/expanded
BEFORE It can be used to listen to audio from compatible portable devices.
It can be dismantled with a Screwdriver to obtain Electronics Scrap.
AFTER It can be used to listen to audio from compatible portable devices.
It can be dismantled with a Screwdriver to obtain Electronics Scrap.
Base.HomeAlarm
ko/compact
BEFORE 스크류드라이버로 분해해 동작 감지 센서를 얻을 수 있다.
AFTER 드라이버로 분해해 동작 감지 센서를 얻을 수 있다.
ko/expanded
BEFORE 스크류드라이버로 분해해 동작 감지 센서를 얻을 수 있다.
AFTER 드라이버로 분해해 동작 감지 센서를 얻을 수 있다.
en/compact
BEFORE It can be dismantled with a Screwdriver to obtain Motion Sensor.
AFTER It can be dismantled with a Screwdriver to obtain Motion Sensor.
en/expanded
BEFORE It can be dismantled with a Screwdriver to obtain Motion Sensor.
AFTER It can be dismantled with a Screwdriver to obtain Motion Sensor.
Base.IronIngot
ko/compact
BEFORE 금속 부품 용접 및 금속 단조에 재료로 쓸 수 있다.
AFTER 금속 부품 용접 및 금속 단조에 재료로 쓸 수 있다.
ko/expanded
BEFORE 금속 부품을 용접하는 재료로 쓸 수 있다.
금속 단조의 재료로 사용할 수 있다.
AFTER 금속 부품을 용접하는 재료로 쓸 수 있다.
금속을 단조할 때 재료로 쓸 수 있다.
en/compact
BEFORE It can supply material for metal-part welding and metal forging.
AFTER It can supply material for metal-part welding and metal forging.
en/expanded
BEFORE It can be used as material for metal-part welding.
It can be used as material for metal forging.
AFTER It can be used as material for metal-part welding.
It can be used as material for metal forging.
Base.Padlock
ko/compact
BEFORE 자물쇠를 달 수 있는 구조물을 잠글 수 있다. 문에는 쓸 수 없다.
AFTER 제작한 나무 상자 같은 보관함을 잠글 수 있다. 문에는 쓸 수 없다.
ko/expanded
BEFORE 자물쇠를 달 수 있는 구조물을 잠글 수 있다. 문에는 쓸 수 없다.
AFTER 제작한 나무 상자 같은 보관함을 잠글 수 있다. 문에는 쓸 수 없다.
en/compact
BEFORE It can lock structures that accept padlocks, except doors.
AFTER It can lock storage containers such as crafted wooden crates, except doors.
en/expanded
BEFORE It can lock structures that accept padlocks, except doors.
AFTER It can lock storage containers such as crafted wooden crates, except doors.
Base.PaintBlack
ko/compact
BEFORE 도색 가능한 표면을 칠할 수 있다. 벽에 표식을 그릴 수 있다.
AFTER 벽, 문틀, 창틀, 기둥과 일부 문, 의자, 상자, 탁자를 칠할 수 있다. 벽에 표식을 그릴 수 있다.
ko/expanded
BEFORE 도색 가능한 표면을 칠할 수 있다.
벽에 표식을 그릴 수 있다.
AFTER 벽, 문틀, 창틀, 기둥과 일부 문, 의자, 상자, 탁자를 칠할 수 있다.
벽에 표식을 그릴 수 있다.
en/compact
BEFORE It can be used to paint compatible surfaces. It can be used to paint signs on walls.
AFTER It can be used to paint walls, door frames, window frames and pillars, as well as some doors, chairs, crates and tables. It can be used to paint signs on walls.
en/expanded
BEFORE It can be used to paint compatible surfaces.
It can be used to paint signs on walls.
AFTER It can be used to paint walls, door frames, window frames and pillars, as well as some doors, chairs, crates and tables.
It can be used to paint signs on walls.
Base.PaintBlue
ko/compact
BEFORE 도색 가능한 표면을 칠할 수 있다. 벽에 표식을 그릴 수 있다.
AFTER 벽, 문틀, 창틀, 기둥과 일부 문, 의자, 상자, 탁자를 칠할 수 있다. 벽에 표식을 그릴 수 있다.
ko/expanded
BEFORE 도색 가능한 표면을 칠할 수 있다.
벽에 표식을 그릴 수 있다.
AFTER 벽, 문틀, 창틀, 기둥과 일부 문, 의자, 상자, 탁자를 칠할 수 있다.
벽에 표식을 그릴 수 있다.
en/compact
BEFORE It can be used to paint compatible surfaces. It can be used to paint signs on walls.
AFTER It can be used to paint walls, door frames, window frames and pillars, as well as some doors, chairs, crates and tables. It can be used to paint signs on walls.
en/expanded
BEFORE It can be used to paint compatible surfaces.
It can be used to paint signs on walls.
AFTER It can be used to paint walls, door frames, window frames and pillars, as well as some doors, chairs, crates and tables.
It can be used to paint signs on walls.
Base.PaintBrown
ko/compact
BEFORE 도색 가능한 표면을 칠할 수 있다. 벽에 표식을 그릴 수 있다.
AFTER 벽, 문틀, 창틀, 기둥과 일부 문, 의자, 상자, 탁자를 칠할 수 있다. 벽에 표식을 그릴 수 있다.
ko/expanded
BEFORE 도색 가능한 표면을 칠할 수 있다.
벽에 표식을 그릴 수 있다.
AFTER 벽, 문틀, 창틀, 기둥과 일부 문, 의자, 상자, 탁자를 칠할 수 있다.
벽에 표식을 그릴 수 있다.
en/compact
BEFORE It can be used to paint compatible surfaces. It can be used to paint signs on walls.
AFTER It can be used to paint walls, door frames, window frames and pillars, as well as some doors, chairs, crates and tables. It can be used to paint signs on walls.
en/expanded
BEFORE It can be used to paint compatible surfaces.
It can be used to paint signs on walls.
AFTER It can be used to paint walls, door frames, window frames and pillars, as well as some doors, chairs, crates and tables.
It can be used to paint signs on walls.
Base.PaintCyan
ko/compact
BEFORE 도색 가능한 표면을 칠할 수 있다. 벽에 표식을 그릴 수 있다.
AFTER 벽, 문틀, 창틀, 기둥과 일부 문, 의자, 상자, 탁자를 칠할 수 있다. 벽에 표식을 그릴 수 있다.
ko/expanded
BEFORE 도색 가능한 표면을 칠할 수 있다.
벽에 표식을 그릴 수 있다.
AFTER 벽, 문틀, 창틀, 기둥과 일부 문, 의자, 상자, 탁자를 칠할 수 있다.
벽에 표식을 그릴 수 있다.
en/compact
BEFORE It can be used to paint compatible surfaces. It can be used to paint signs on walls.
AFTER It can be used to paint walls, door frames, window frames and pillars, as well as some doors, chairs, crates and tables. It can be used to paint signs on walls.
en/expanded
BEFORE It can be used to paint compatible surfaces.
It can be used to paint signs on walls.
AFTER It can be used to paint walls, door frames, window frames and pillars, as well as some doors, chairs, crates and tables.
It can be used to paint signs on walls.
Base.PaintGreen
ko/compact
BEFORE 도색 가능한 표면을 칠할 수 있다. 벽에 표식을 그릴 수 있다.
AFTER 벽, 문틀, 창틀, 기둥과 일부 문, 의자, 상자, 탁자를 칠할 수 있다. 벽에 표식을 그릴 수 있다.
ko/expanded
BEFORE 도색 가능한 표면을 칠할 수 있다.
벽에 표식을 그릴 수 있다.
AFTER 벽, 문틀, 창틀, 기둥과 일부 문, 의자, 상자, 탁자를 칠할 수 있다.
벽에 표식을 그릴 수 있다.
en/compact
BEFORE It can be used to paint compatible surfaces. It can be used to paint signs on walls.
AFTER It can be used to paint walls, door frames, window frames and pillars, as well as some doors, chairs, crates and tables. It can be used to paint signs on walls.
en/expanded
BEFORE It can be used to paint compatible surfaces.
It can be used to paint signs on walls.
AFTER It can be used to paint walls, door frames, window frames and pillars, as well as some doors, chairs, crates and tables.
It can be used to paint signs on walls.
Base.PaintGrey
ko/compact
BEFORE 도색 가능한 표면을 칠할 수 있다. 벽에 표식을 그릴 수 있다.
AFTER 벽, 문틀, 창틀, 기둥과 일부 문, 의자, 상자, 탁자를 칠할 수 있다. 벽에 표식을 그릴 수 있다.
ko/expanded
BEFORE 도색 가능한 표면을 칠할 수 있다.
벽에 표식을 그릴 수 있다.
AFTER 벽, 문틀, 창틀, 기둥과 일부 문, 의자, 상자, 탁자를 칠할 수 있다.
벽에 표식을 그릴 수 있다.
en/compact
BEFORE It can be used to paint compatible surfaces. It can be used to paint signs on walls.
AFTER It can be used to paint walls, door frames, window frames and pillars, as well as some doors, chairs, crates and tables. It can be used to paint signs on walls.
en/expanded
BEFORE It can be used to paint compatible surfaces.
It can be used to paint signs on walls.
AFTER It can be used to paint walls, door frames, window frames and pillars, as well as some doors, chairs, crates and tables.
It can be used to paint signs on walls.
Base.PaintLightBlue
ko/compact
BEFORE 도색 가능한 표면을 칠할 수 있다. 벽에 표식을 그릴 수 있다.
AFTER 벽, 문틀, 창틀, 기둥과 일부 문, 의자, 상자, 탁자를 칠할 수 있다. 벽에 표식을 그릴 수 있다.
ko/expanded
BEFORE 도색 가능한 표면을 칠할 수 있다.
벽에 표식을 그릴 수 있다.
AFTER 벽, 문틀, 창틀, 기둥과 일부 문, 의자, 상자, 탁자를 칠할 수 있다.
벽에 표식을 그릴 수 있다.
en/compact
BEFORE It can be used to paint compatible surfaces. It can be used to paint signs on walls.
AFTER It can be used to paint walls, door frames, window frames and pillars, as well as some doors, chairs, crates and tables. It can be used to paint signs on walls.
en/expanded
BEFORE It can be used to paint compatible surfaces.
It can be used to paint signs on walls.
AFTER It can be used to paint walls, door frames, window frames and pillars, as well as some doors, chairs, crates and tables.
It can be used to paint signs on walls.
Base.PaintLightBrown
ko/compact
BEFORE 도색 가능한 표면을 칠할 수 있다. 벽에 표식을 그릴 수 있다.
AFTER 벽, 문틀, 창틀, 기둥과 일부 문, 의자, 상자, 탁자를 칠할 수 있다. 벽에 표식을 그릴 수 있다.
ko/expanded
BEFORE 도색 가능한 표면을 칠할 수 있다.
벽에 표식을 그릴 수 있다.
AFTER 벽, 문틀, 창틀, 기둥과 일부 문, 의자, 상자, 탁자를 칠할 수 있다.
벽에 표식을 그릴 수 있다.
en/compact
BEFORE It can be used to paint compatible surfaces. It can be used to paint signs on walls.
AFTER It can be used to paint walls, door frames, window frames and pillars, as well as some doors, chairs, crates and tables. It can be used to paint signs on walls.
en/expanded
BEFORE It can be used to paint compatible surfaces.
It can be used to paint signs on walls.
AFTER It can be used to paint walls, door frames, window frames and pillars, as well as some doors, chairs, crates and tables.
It can be used to paint signs on walls.
Base.PaintOrange
ko/compact
BEFORE 도색 가능한 표면을 칠할 수 있다. 벽에 표식을 그릴 수 있다.
AFTER 벽, 문틀, 창틀, 기둥과 일부 문, 의자, 상자, 탁자를 칠할 수 있다. 벽에 표식을 그릴 수 있다.
ko/expanded
BEFORE 도색 가능한 표면을 칠할 수 있다.
벽에 표식을 그릴 수 있다.
AFTER 벽, 문틀, 창틀, 기둥과 일부 문, 의자, 상자, 탁자를 칠할 수 있다.
벽에 표식을 그릴 수 있다.
en/compact
BEFORE It can be used to paint compatible surfaces. It can be used to paint signs on walls.
AFTER It can be used to paint walls, door frames, window frames and pillars, as well as some doors, chairs, crates and tables. It can be used to paint signs on walls.
en/expanded
BEFORE It can be used to paint compatible surfaces.
It can be used to paint signs on walls.
AFTER It can be used to paint walls, door frames, window frames and pillars, as well as some doors, chairs, crates and tables.
It can be used to paint signs on walls.
Base.PaintPink
ko/compact
BEFORE 도색 가능한 표면을 칠할 수 있다. 벽에 표식을 그릴 수 있다.
AFTER 벽, 문틀, 창틀, 기둥과 일부 문, 의자, 상자, 탁자를 칠할 수 있다. 벽에 표식을 그릴 수 있다.
ko/expanded
BEFORE 도색 가능한 표면을 칠할 수 있다.
벽에 표식을 그릴 수 있다.
AFTER 벽, 문틀, 창틀, 기둥과 일부 문, 의자, 상자, 탁자를 칠할 수 있다.
벽에 표식을 그릴 수 있다.
en/compact
BEFORE It can be used to paint compatible surfaces. It can be used to paint signs on walls.
AFTER It can be used to paint walls, door frames, window frames and pillars, as well as some doors, chairs, crates and tables. It can be used to paint signs on walls.
en/expanded
BEFORE It can be used to paint compatible surfaces.
It can be used to paint signs on walls.
AFTER It can be used to paint walls, door frames, window frames and pillars, as well as some doors, chairs, crates and tables.
It can be used to paint signs on walls.
Base.PaintPurple
ko/compact
BEFORE 도색 가능한 표면을 칠할 수 있다. 벽에 표식을 그릴 수 있다.
AFTER 벽, 문틀, 창틀, 기둥과 일부 문, 의자, 상자, 탁자를 칠할 수 있다. 벽에 표식을 그릴 수 있다.
ko/expanded
BEFORE 도색 가능한 표면을 칠할 수 있다.
벽에 표식을 그릴 수 있다.
AFTER 벽, 문틀, 창틀, 기둥과 일부 문, 의자, 상자, 탁자를 칠할 수 있다.
벽에 표식을 그릴 수 있다.
en/compact
BEFORE It can be used to paint compatible surfaces. It can be used to paint signs on walls.
AFTER It can be used to paint walls, door frames, window frames and pillars, as well as some doors, chairs, crates and tables. It can be used to paint signs on walls.
en/expanded
BEFORE It can be used to paint compatible surfaces.
It can be used to paint signs on walls.
AFTER It can be used to paint walls, door frames, window frames and pillars, as well as some doors, chairs, crates and tables.
It can be used to paint signs on walls.
Base.PaintRed
ko/compact
BEFORE 도색 가능한 표면을 칠할 수 있다. 벽에 표식을 그릴 수 있다.
AFTER 벽, 문틀, 창틀, 기둥과 일부 문, 의자, 상자, 탁자를 칠할 수 있다. 벽에 표식을 그릴 수 있다.
ko/expanded
BEFORE 도색 가능한 표면을 칠할 수 있다.
벽에 표식을 그릴 수 있다.
AFTER 벽, 문틀, 창틀, 기둥과 일부 문, 의자, 상자, 탁자를 칠할 수 있다.
벽에 표식을 그릴 수 있다.
en/compact
BEFORE It can be used to paint compatible surfaces. It can be used to paint signs on walls.
AFTER It can be used to paint walls, door frames, window frames and pillars, as well as some doors, chairs, crates and tables. It can be used to paint signs on walls.
en/expanded
BEFORE It can be used to paint compatible surfaces.
It can be used to paint signs on walls.
AFTER It can be used to paint walls, door frames, window frames and pillars, as well as some doors, chairs, crates and tables.
It can be used to paint signs on walls.
Base.PaintTurquoise
ko/compact
BEFORE 도색 가능한 표면을 칠할 수 있다. 벽에 표식을 그릴 수 있다.
AFTER 벽, 문틀, 창틀, 기둥과 일부 문, 의자, 상자, 탁자를 칠할 수 있다. 벽에 표식을 그릴 수 있다.
ko/expanded
BEFORE 도색 가능한 표면을 칠할 수 있다.
벽에 표식을 그릴 수 있다.
AFTER 벽, 문틀, 창틀, 기둥과 일부 문, 의자, 상자, 탁자를 칠할 수 있다.
벽에 표식을 그릴 수 있다.
en/compact
BEFORE It can be used to paint compatible surfaces. It can be used to paint signs on walls.
AFTER It can be used to paint walls, door frames, window frames and pillars, as well as some doors, chairs, crates and tables. It can be used to paint signs on walls.
en/expanded
BEFORE It can be used to paint compatible surfaces.
It can be used to paint signs on walls.
AFTER It can be used to paint walls, door frames, window frames and pillars, as well as some doors, chairs, crates and tables.
It can be used to paint signs on walls.
Base.PaintWhite
ko/compact
BEFORE 도색 가능한 표면을 칠할 수 있다. 벽에 표식을 그릴 수 있다.
AFTER 벽, 문틀, 창틀, 기둥과 일부 문, 의자, 상자, 탁자를 칠할 수 있다. 벽에 표식을 그릴 수 있다.
ko/expanded
BEFORE 도색 가능한 표면을 칠할 수 있다.
벽에 표식을 그릴 수 있다.
AFTER 벽, 문틀, 창틀, 기둥과 일부 문, 의자, 상자, 탁자를 칠할 수 있다.
벽에 표식을 그릴 수 있다.
en/compact
BEFORE It can be used to paint compatible surfaces. It can be used to paint signs on walls.
AFTER It can be used to paint walls, door frames, window frames and pillars, as well as some doors, chairs, crates and tables. It can be used to paint signs on walls.
en/expanded
BEFORE It can be used to paint compatible surfaces.
It can be used to paint signs on walls.
AFTER It can be used to paint walls, door frames, window frames and pillars, as well as some doors, chairs, crates and tables.
It can be used to paint signs on walls.
Base.PaintYellow
ko/compact
BEFORE 도색 가능한 표면을 칠할 수 있다. 벽에 표식을 그릴 수 있다.
AFTER 벽, 문틀, 창틀, 기둥과 일부 문, 의자, 상자, 탁자를 칠할 수 있다. 벽에 표식을 그릴 수 있다.
ko/expanded
BEFORE 도색 가능한 표면을 칠할 수 있다.
벽에 표식을 그릴 수 있다.
AFTER 벽, 문틀, 창틀, 기둥과 일부 문, 의자, 상자, 탁자를 칠할 수 있다.
벽에 표식을 그릴 수 있다.
en/compact
BEFORE It can be used to paint compatible surfaces. It can be used to paint signs on walls.
AFTER It can be used to paint walls, door frames, window frames and pillars, as well as some doors, chairs, crates and tables. It can be used to paint signs on walls.
en/expanded
BEFORE It can be used to paint compatible surfaces.
It can be used to paint signs on walls.
AFTER It can be used to paint walls, door frames, window frames and pillars, as well as some doors, chairs, crates and tables.
It can be used to paint signs on walls.
Base.Paintbrush
ko/compact
BEFORE 도색 가능한 표면을 칠할 수 있다. 벽에 표식을 그릴 수 있다.
AFTER 벽, 문틀, 창틀, 기둥과 일부 문, 의자, 상자, 탁자를 칠할 수 있다. 벽에 표식을 그릴 수 있다.
ko/expanded
BEFORE 도색 가능한 표면을 칠할 수 있다.
벽에 표식을 그릴 수 있다.
AFTER 벽, 문틀, 창틀, 기둥과 일부 문, 의자, 상자, 탁자를 칠할 수 있다.
벽에 표식을 그릴 수 있다.
en/compact
BEFORE It can be used to paint compatible surfaces. It can be used to paint signs on walls.
AFTER It can be used to paint walls, door frames, window frames and pillars, as well as some doors, chairs, crates and tables. It can be used to paint signs on walls.
en/expanded
BEFORE It can be used to paint compatible surfaces.
It can be used to paint signs on walls.
AFTER It can be used to paint walls, door frames, window frames and pillars, as well as some doors, chairs, crates and tables.
It can be used to paint signs on walls.
Base.PetrolBleachBottle
ko/compact
BEFORE 주유기나 차량에서 연료를 담을 수 있다. 담긴 연료를 차량에 넣을 수도 있다. 화염 장치를 만들 때 재료로 쓸 수 있다. 시신을 태우는 데 쓸 수 있다. 불을 붙이는 데 쓸 수 있다. 발전기에 휘발유를 보충할 수 있다.
AFTER 주유기나 차량에서 연료를 담을 수 있다. 담긴 연료를 차량에 넣을 수도 있다. 화염 장치를 만들 때 재료로 쓸 수 있다. 시신을 태우는 데 쓸 수 있다. 모닥불 등에 불을 붙이는 연료로 쓸 수 있다. 발전기에 휘발유를 보충할 수 있다.
ko/expanded
BEFORE 주유기나 차량에서 연료를 담을 수 있다. 담긴 연료를 차량에 넣을 수도 있다.
화염 장치를 만들 때 재료로 쓸 수 있다.
시신을 태우는 데 쓸 수 있다.
모닥불 등에 불을 붙이는 연료로 쓸 수 있다.
발전기에 휘발유를 보충할 수 있다.
AFTER 주유기나 차량에서 연료를 담을 수 있다. 담긴 연료를 차량에 넣을 수도 있다.
화염 장치를 만들 때 재료로 쓸 수 있다.
시신을 태우는 데 쓸 수 있다.
모닥불 등에 불을 붙이는 연료로 쓸 수 있다.
발전기에 휘발유를 보충할 수 있다.
en/compact
BEFORE It can collect fuel from a pump or vehicle. Its fuel can also be poured into a vehicle. It can be used as material for making incendiary devices. It can be used to burn corpses. It can be used for lighting fires. It can add petrol to a generator.
AFTER It can collect fuel from a pump or vehicle. Its fuel can also be poured into a vehicle. It can be used as material for making incendiary devices. It can be used to burn corpses. It can supply petrol for lighting campfires, for example. It can add petrol to a generator.
en/expanded
BEFORE It can collect fuel from a pump or vehicle. Its fuel can also be poured into a vehicle.
It can be used as material for making incendiary devices.
It can be used to burn corpses.
It can supply petrol for lighting campfires, for example.
It can add petrol to a generator.
AFTER It can collect fuel from a pump or vehicle. Its fuel can also be poured into a vehicle.
It can be used as material for making incendiary devices.
It can be used to burn corpses.
It can supply petrol for lighting campfires, for example.
It can add petrol to a generator.
Base.PetrolCan
ko/compact
BEFORE 주유기나 차량에서 연료를 담을 수 있다. 담긴 연료를 차량에 넣을 수도 있다. 화염 장치를 만들 때 재료로 쓸 수 있다. 시신을 태우는 데 쓸 수 있다. 불을 붙이는 데 쓸 수 있다. 발전기에 휘발유를 보충할 수 있다.
AFTER 주유기나 차량에서 연료를 담을 수 있다. 담긴 연료를 차량에 넣을 수도 있다. 화염 장치를 만들 때 재료로 쓸 수 있다. 시신을 태우는 데 쓸 수 있다. 모닥불 등에 불을 붙이는 연료로 쓸 수 있다. 발전기에 휘발유를 보충할 수 있다.
ko/expanded
BEFORE 주유기나 차량에서 연료를 담을 수 있다. 담긴 연료를 차량에 넣을 수도 있다.
화염 장치를 만들 때 재료로 쓸 수 있다.
시신을 태우는 데 쓸 수 있다.
모닥불 등에 불을 붙이는 연료로 쓸 수 있다.
발전기에 휘발유를 보충할 수 있다.
AFTER 주유기나 차량에서 연료를 담을 수 있다. 담긴 연료를 차량에 넣을 수도 있다.
화염 장치를 만들 때 재료로 쓸 수 있다.
시신을 태우는 데 쓸 수 있다.
모닥불 등에 불을 붙이는 연료로 쓸 수 있다.
발전기에 휘발유를 보충할 수 있다.
en/compact
BEFORE It can collect fuel from a pump or vehicle. Its fuel can also be poured into a vehicle. It can be used as material for making incendiary devices. It can be used to burn corpses. It can be used for lighting fires. It can add petrol to a generator.
AFTER It can collect fuel from a pump or vehicle. Its fuel can also be poured into a vehicle. It can be used as material for making incendiary devices. It can be used to burn corpses. It can supply petrol for lighting campfires, for example. It can add petrol to a generator.
en/expanded
BEFORE It can collect fuel from a pump or vehicle. Its fuel can also be poured into a vehicle.
It can be used as material for making incendiary devices.
It can be used to burn corpses.
It can supply petrol for lighting campfires, for example.
It can add petrol to a generator.
AFTER It can collect fuel from a pump or vehicle. Its fuel can also be poured into a vehicle.
It can be used as material for making incendiary devices.
It can be used to burn corpses.
It can supply petrol for lighting campfires, for example.
It can add petrol to a generator.
Base.PetrolPopBottle
ko/compact
BEFORE 주유기나 차량에서 연료를 담을 수 있다. 담긴 연료를 차량에 넣을 수도 있다. 화염 장치를 만들 때 재료로 쓸 수 있다. 시신을 태우는 데 쓸 수 있다. 불을 붙이는 데 쓸 수 있다. 발전기에 휘발유를 보충할 수 있다.
AFTER 주유기나 차량에서 연료를 담을 수 있다. 담긴 연료를 차량에 넣을 수도 있다. 화염 장치를 만들 때 재료로 쓸 수 있다. 시신을 태우는 데 쓸 수 있다. 모닥불 등에 불을 붙이는 연료로 쓸 수 있다. 발전기에 휘발유를 보충할 수 있다.
ko/expanded
BEFORE 주유기나 차량에서 연료를 담을 수 있다. 담긴 연료를 차량에 넣을 수도 있다.
화염 장치를 만들 때 재료로 쓸 수 있다.
시신을 태우는 데 쓸 수 있다.
모닥불 등에 불을 붙이는 연료로 쓸 수 있다.
발전기에 휘발유를 보충할 수 있다.
AFTER 주유기나 차량에서 연료를 담을 수 있다. 담긴 연료를 차량에 넣을 수도 있다.
화염 장치를 만들 때 재료로 쓸 수 있다.
시신을 태우는 데 쓸 수 있다.
모닥불 등에 불을 붙이는 연료로 쓸 수 있다.
발전기에 휘발유를 보충할 수 있다.
en/compact
BEFORE It can collect fuel from a pump or vehicle. Its fuel can also be poured into a vehicle. It can be used as material for making incendiary devices. It can be used to burn corpses. It can be used for lighting fires. It can add petrol to a generator.
AFTER It can collect fuel from a pump or vehicle. Its fuel can also be poured into a vehicle. It can be used as material for making incendiary devices. It can be used to burn corpses. It can supply petrol for lighting campfires, for example. It can add petrol to a generator.
en/expanded
BEFORE It can collect fuel from a pump or vehicle. Its fuel can also be poured into a vehicle.
It can be used as material for making incendiary devices.
It can be used to burn corpses.
It can supply petrol for lighting campfires, for example.
It can add petrol to a generator.
AFTER It can collect fuel from a pump or vehicle. Its fuel can also be poured into a vehicle.
It can be used as material for making incendiary devices.
It can be used to burn corpses.
It can supply petrol for lighting campfires, for example.
It can add petrol to a generator.
Base.Remote
ko/compact
BEFORE 원격 조종기를 만드는 재료로 쓸 수 있다. 스크류드라이버로 분해해 수신기, 전기 회로 부속을 얻을 수 있다. 건전지도 나올 수 있다.
AFTER 원격 조종기를 만드는 재료로 쓸 수 있다. 드라이버로 분해해 수신기, 전기 회로 부속을 얻을 수 있다. 건전지도 나올 수 있다.
ko/expanded
BEFORE 원격 조종기를 만드는 재료로 쓸 수 있다.
스크류드라이버로 분해해 수신기, 전기 회로 부속을 얻을 수 있다. 건전지도 나올 수 있다.
AFTER 원격 조종기를 만드는 재료로 쓸 수 있다.
드라이버로 분해해 수신기, 전기 회로 부속을 얻을 수 있다. 건전지도 나올 수 있다.
en/compact
BEFORE It can be used as material for making remote controllers. It can be dismantled with a Screwdriver to obtain Receiver and Electronics Scrap. Battery may also be recovered.
AFTER It can be used as material for making remote controllers. It can be dismantled with a Screwdriver to obtain Receiver and Electronics Scrap. Battery may also be recovered.
en/expanded
BEFORE It can be used as material for making remote controllers.
It can be dismantled with a Screwdriver to obtain Receiver and Electronics Scrap. Battery may also be recovered.
AFTER It can be used as material for making remote controllers.
It can be dismantled with a Screwdriver to obtain Receiver and Electronics Scrap. Battery may also be recovered.
Base.SmithingMag3
ko/compact
BEFORE 읽어서 금속을 단조해 물품을 만드는 방법을 배울 수 있다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다.
AFTER 읽어서 금속을 단조해 물품을 만드는 방법을 배울 수 있다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다.
ko/expanded
BEFORE 읽어서 금속을 단조해 물품을 만드는 방법을 배울 수 있다.
- 집게 만들기
- 망치 만들기
- 금속판 만들기
- 봉합용 바늘 집개 만들기
- 핀셋 만들기
- 봉합용 바늘 만들기
- 드럼통 만들기
- 부엌칼 만들기
- 톱 만들기
- 사냥용 칼 만들기
- 삽 만들기
- 모종삽 만들기
모닥불 등의 연료나 불쏘시개로 쓸 수 있다.
AFTER 읽어서 금속을 단조해 물품을 만드는 방법을 배울 수 있다.
- 집게 만들기
- 망치 만들기
- 금속판 만들기
- 봉합용 바늘 집게 만들기
- 핀셋 만들기
- 봉합용 바늘 만들기
- 드럼통 만들기
- 부엌칼 만들기
- 톱 만들기
- 사냥용 칼 만들기
- 삽 만들기
- 모종삽 만들기
모닥불 등의 연료나 불쏘시개로 쓸 수 있다.
en/compact
BEFORE It can be read to learn how to forge metal items. It can be used as fuel or tinder, for example in campfires.
AFTER It can be read to learn how to forge metal items. It can be used as fuel or tinder, for example in campfires.
en/expanded
BEFORE It can be read to learn how to forge metal items.
- Make Tongs
- Make Hammer
- Make Sheet Metal
- Make Suture Needle Holder
- Make Tweezers
- Make Suture Needle
- Make Metal Drum
- Make Kitchen Knife
- Make Saw
- Make Hunting Knife
- Make Shovel
- Make Hand Shovel
It can be used as fuel or tinder, for example in campfires.
AFTER It can be read to learn how to forge metal items.
- Make Tongs
- Make Hammer
- Make Sheet Metal
- Make Suture Needle Holder
- Make Tweezers
- Make Suture Needle
- Make Metal Drum
- Make Kitchen Knife
- Make Saw
- Make Hunting Knife
- Make Shovel
- Make Hand Shovel
It can be used as fuel or tinder, for example in campfires.
Base.Speaker
ko/compact
BEFORE 스크류드라이버로 분해해 증폭기를 얻을 수 있다.
AFTER 드라이버로 분해해 증폭기를 얻을 수 있다.
ko/expanded
BEFORE 스크류드라이버로 분해해 증폭기를 얻을 수 있다.
AFTER 드라이버로 분해해 증폭기를 얻을 수 있다.
en/compact
BEFORE It can be dismantled with a Screwdriver to obtain Amplifier.
AFTER It can be dismantled with a Screwdriver to obtain Amplifier.
en/expanded
BEFORE It can be dismantled with a Screwdriver to obtain Amplifier.
AFTER It can be dismantled with a Screwdriver to obtain Amplifier.
Base.Torch
ko/compact
BEFORE 휴대 조명으로 쓸 수 있다. 스크류드라이버로 분해해 전기 회로 부속을 얻을 수 있다.
AFTER 휴대 조명으로 쓸 수 있다. 드라이버로 분해해 전기 회로 부속을 얻을 수 있다.
ko/expanded
BEFORE 휴대 조명으로 쓸 수 있다.
스크류드라이버로 분해해 전기 회로 부속을 얻을 수 있다.
AFTER 휴대 조명으로 쓸 수 있다.
드라이버로 분해해 전기 회로 부속을 얻을 수 있다.
en/compact
BEFORE It can be used as a portable light. It can be dismantled with a Screwdriver to obtain Electronics Scrap.
AFTER It can be used as a portable light. It can be dismantled with a Screwdriver to obtain Electronics Scrap.
en/expanded
BEFORE It can be used as a portable light.
It can be dismantled with a Screwdriver to obtain Electronics Scrap.
AFTER It can be used as a portable light.
It can be dismantled with a Screwdriver to obtain Electronics Scrap.
Base.VideoGame
ko/compact
BEFORE 스크류드라이버로 분해해 전기 회로 부속을 얻을 수 있다.
AFTER 드라이버로 분해해 전기 회로 부속을 얻을 수 있다.
ko/expanded
BEFORE 스크류드라이버로 분해해 전기 회로 부속을 얻을 수 있다.
AFTER 드라이버로 분해해 전기 회로 부속을 얻을 수 있다.
en/compact
BEFORE It can be dismantled with a Screwdriver to obtain Electronics Scrap.
AFTER It can be dismantled with a Screwdriver to obtain Electronics Scrap.
en/expanded
BEFORE It can be dismantled with a Screwdriver to obtain Electronics Scrap.
AFTER It can be dismantled with a Screwdriver to obtain Electronics Scrap.
Base.WaterBottlePetrol
ko/compact
BEFORE 주유기나 차량에서 연료를 담을 수 있다. 담긴 연료를 차량에 넣을 수도 있다. 화염 장치를 만들 때 재료로 쓸 수 있다. 시신을 태우는 데 쓸 수 있다. 불을 붙이는 데 쓸 수 있다. 발전기에 휘발유를 보충할 수 있다.
AFTER 주유기나 차량에서 연료를 담을 수 있다. 담긴 연료를 차량에 넣을 수도 있다. 화염 장치를 만들 때 재료로 쓸 수 있다. 시신을 태우는 데 쓸 수 있다. 모닥불 등에 불을 붙이는 연료로 쓸 수 있다. 발전기에 휘발유를 보충할 수 있다.
ko/expanded
BEFORE 주유기나 차량에서 연료를 담을 수 있다. 담긴 연료를 차량에 넣을 수도 있다.
화염 장치를 만들 때 재료로 쓸 수 있다.
시신을 태우는 데 쓸 수 있다.
모닥불 등에 불을 붙이는 연료로 쓸 수 있다.
발전기에 휘발유를 보충할 수 있다.
AFTER 주유기나 차량에서 연료를 담을 수 있다. 담긴 연료를 차량에 넣을 수도 있다.
화염 장치를 만들 때 재료로 쓸 수 있다.
시신을 태우는 데 쓸 수 있다.
모닥불 등에 불을 붙이는 연료로 쓸 수 있다.
발전기에 휘발유를 보충할 수 있다.
en/compact
BEFORE It can collect fuel from a pump or vehicle. Its fuel can also be poured into a vehicle. It can be used as material for making incendiary devices. It can be used to burn corpses. It can be used for lighting fires. It can add petrol to a generator.
AFTER It can collect fuel from a pump or vehicle. Its fuel can also be poured into a vehicle. It can be used as material for making incendiary devices. It can be used to burn corpses. It can supply petrol for lighting campfires, for example. It can add petrol to a generator.
en/expanded
BEFORE It can collect fuel from a pump or vehicle. Its fuel can also be poured into a vehicle.
It can be used as material for making incendiary devices.
It can be used to burn corpses.
It can supply petrol for lighting campfires, for example.
It can add petrol to a generator.
AFTER It can collect fuel from a pump or vehicle. Its fuel can also be poured into a vehicle.
It can be used as material for making incendiary devices.
It can be used to burn corpses.
It can supply petrol for lighting campfires, for example.
It can add petrol to a generator.
Base.WhiskeyFull
ko/compact
BEFORE 천이나 솜을 소독하는 데 쓸 수 있다. 화염 장치를 만들 때 재료로 쓸 수 있다. 마실 수 있다. 요리 재료로 쓸 수 있다. 상처를 소독할 수 있다.
AFTER 천, 솜, 상처를 소독하는 데 쓸 수 있다. 화염 장치를 만들 때 재료로 쓸 수 있다. 마실 수 있다. 요리 재료로 쓸 수 있다.
ko/expanded
BEFORE 천이나 솜을 소독하는 데 쓸 수 있다.
화염 장치를 만들 때 재료로 쓸 수 있다.
마실 수 있다.
요리 재료로 쓸 수 있다.
상처를 소독할 수 있다.
AFTER 천, 솜, 상처를 소독하는 데 쓸 수 있다.
화염 장치를 만들 때 재료로 쓸 수 있다.
마실 수 있다.
요리 재료로 쓸 수 있다.
en/compact
BEFORE It can be used to disinfect cloth or cotton. It can be used as material for making incendiary devices. It can be drunk. It can be used as a cooking ingredient. It can be used to disinfect wounds.
AFTER It can be used to disinfect cloth, cotton or wounds. It can be used as material for making incendiary devices. It can be drunk. It can be used as a cooking ingredient.
en/expanded
BEFORE It can be used to disinfect cloth or cotton.
It can be used as material for making incendiary devices.
It can be drunk.
It can be used as a cooking ingredient.
It can be used to disinfect wounds.
AFTER It can be used to disinfect cloth, cotton or wounds.
It can be used as material for making incendiary devices.
It can be drunk.
It can be used as a cooking ingredient.
Base.WhiskeyPetrol
ko/compact
BEFORE 주유기나 차량에서 연료를 담을 수 있다. 담긴 연료를 차량에 넣을 수도 있다. 화염 장치를 만들 때 재료로 쓸 수 있다. 시신을 태우는 데 쓸 수 있다. 불을 붙이는 데 쓸 수 있다. 발전기에 휘발유를 보충할 수 있다.
AFTER 주유기나 차량에서 연료를 담을 수 있다. 담긴 연료를 차량에 넣을 수도 있다. 화염 장치를 만들 때 재료로 쓸 수 있다. 시신을 태우는 데 쓸 수 있다. 모닥불 등에 불을 붙이는 연료로 쓸 수 있다. 발전기에 휘발유를 보충할 수 있다.
ko/expanded
BEFORE 주유기나 차량에서 연료를 담을 수 있다. 담긴 연료를 차량에 넣을 수도 있다.
화염 장치를 만들 때 재료로 쓸 수 있다.
시신을 태우는 데 쓸 수 있다.
모닥불 등에 불을 붙이는 연료로 쓸 수 있다.
발전기에 휘발유를 보충할 수 있다.
AFTER 주유기나 차량에서 연료를 담을 수 있다. 담긴 연료를 차량에 넣을 수도 있다.
화염 장치를 만들 때 재료로 쓸 수 있다.
시신을 태우는 데 쓸 수 있다.
모닥불 등에 불을 붙이는 연료로 쓸 수 있다.
발전기에 휘발유를 보충할 수 있다.
en/compact
BEFORE It can collect fuel from a pump or vehicle. Its fuel can also be poured into a vehicle. It can be used as material for making incendiary devices. It can be used to burn corpses. It can be used for lighting fires. It can add petrol to a generator.
AFTER It can collect fuel from a pump or vehicle. Its fuel can also be poured into a vehicle. It can be used as material for making incendiary devices. It can be used to burn corpses. It can supply petrol for lighting campfires, for example. It can add petrol to a generator.
en/expanded
BEFORE It can collect fuel from a pump or vehicle. Its fuel can also be poured into a vehicle.
It can be used as material for making incendiary devices.
It can be used to burn corpses.
It can supply petrol for lighting campfires, for example.
It can add petrol to a generator.
AFTER It can collect fuel from a pump or vehicle. Its fuel can also be poured into a vehicle.
It can be used as material for making incendiary devices.
It can be used to burn corpses.
It can supply petrol for lighting campfires, for example.
It can add petrol to a generator.
Base.WinePetrol
ko/compact
BEFORE 주유기나 차량에서 연료를 담을 수 있다. 담긴 연료를 차량에 넣을 수도 있다. 화염 장치를 만들 때 재료로 쓸 수 있다. 시신을 태우는 데 쓸 수 있다. 불을 붙이는 데 쓸 수 있다. 발전기에 휘발유를 보충할 수 있다.
AFTER 주유기나 차량에서 연료를 담을 수 있다. 담긴 연료를 차량에 넣을 수도 있다. 화염 장치를 만들 때 재료로 쓸 수 있다. 시신을 태우는 데 쓸 수 있다. 모닥불 등에 불을 붙이는 연료로 쓸 수 있다. 발전기에 휘발유를 보충할 수 있다.
ko/expanded
BEFORE 주유기나 차량에서 연료를 담을 수 있다. 담긴 연료를 차량에 넣을 수도 있다.
화염 장치를 만들 때 재료로 쓸 수 있다.
시신을 태우는 데 쓸 수 있다.
모닥불 등에 불을 붙이는 연료로 쓸 수 있다.
발전기에 휘발유를 보충할 수 있다.
AFTER 주유기나 차량에서 연료를 담을 수 있다. 담긴 연료를 차량에 넣을 수도 있다.
화염 장치를 만들 때 재료로 쓸 수 있다.
시신을 태우는 데 쓸 수 있다.
모닥불 등에 불을 붙이는 연료로 쓸 수 있다.
발전기에 휘발유를 보충할 수 있다.
en/compact
BEFORE It can collect fuel from a pump or vehicle. Its fuel can also be poured into a vehicle. It can be used as material for making incendiary devices. It can be used to burn corpses. It can be used for lighting fires. It can add petrol to a generator.
AFTER It can collect fuel from a pump or vehicle. Its fuel can also be poured into a vehicle. It can be used as material for making incendiary devices. It can be used to burn corpses. It can supply petrol for lighting campfires, for example. It can add petrol to a generator.
en/expanded
BEFORE It can collect fuel from a pump or vehicle. Its fuel can also be poured into a vehicle.
It can be used as material for making incendiary devices.
It can be used to burn corpses.
It can supply petrol for lighting campfires, for example.
It can add petrol to a generator.
AFTER It can collect fuel from a pump or vehicle. Its fuel can also be poured into a vehicle.
It can be used as material for making incendiary devices.
It can be used to burn corpses.
It can supply petrol for lighting campfires, for example.
It can add petrol to a generator.
```


## 2026-09-14 활용 요약과 대상·내용 상세 구성

현재 수락본 952913e3 기준으로 구성 방식을 일반화했다. 작업 중 사용자가 수정한 Compact의 책임을 최종 기준으로 적용한다. **Expanded는 확인된 독립 용도와 필요한 구체성을 보존하는 본 설명이고, Compact는 그 설명을 빠르게 이해하도록 만든 유용한 요약이다.** Compact에서 모든 독립 용도·대상·조건을 일대일 명시할 필요는 없다. 그러나 Compact만 읽어도 실제 무엇에 쓸 수 있는지 알아야 하며, 빈약한 ‘여러 용도/제작 등에 사용’ 표현, 오해를 만드는 범주, primary_use 하나만 남기는 방식은 허용하지 않는다. 이 최신 합의가 앞선 절의 양 표면 전수 용도 보존 요구보다 우선한다.

### 공통 구성 규칙과 근거

uses.detail_text는 개수나 글자 수의 임계값 대신 관계의 성격으로 요약·목록·문장 구성을 선택한다. learning_content는 개별 학습 내용을 개요 밑에 유지한다. scoped_target_groups는 대상 범주별 수식 범위를 각 항목에 붙인다. compatibility_choices는 서로 다른 호환 물품을 실제 이름으로 제시한다. homogeneous_targets는 한 대상이나 동종 총기 계열처럼 한 행동으로 충분히 설명할 수 있는 관계를 문장으로 유지한다. 독립 용도는 목록 항목으로 집어넣지 않는다.

아이템 ID로 문면을 선택하거나 완성 문장을 덮어쓰는 새 분기를 만들지 않았다. 페인트의 action/role/category/groups/scope는 기존 recovery_relations에서 이미 조사한 PaintingReference의 실제 키를 읽고 확인해 전달한다. Painting의 wall/doorframe/windowsframe/pillar와 OtherPainting의 door/chair/crates/table을 교차 확인하며 소스 대응이 바뀌면 실패한다. 실제 적용 경로는 앞선 수락 절에 확인한 ISPaintCursor/ISPaintMenu이며 새 월드 조사로 확대하지 않았다.

페인트 Compact는 **벽이나 가구 등을 칠하고, 벽에 표식을 그릴 수 있다.** Expanded는 다음과 같다.

```text
다음 대상을 칠할 수 있다.
- 벽
- 문틀
- 창틀
- 기둥
- 일부 문
- 일부 의자
- 일부 상자
- 일부 탁자
벽에 표식을 그릴 수 있다.
```

‘일부’를 문·의자·상자·탁자 각각에 붙여 목록화로 수식 범위가 흐려지지 않도록 했다. Compact의 벽/가구는 활용을 알려 주는 대표 범주이며, 모든 벽/가구에 적용된다는 전수 보장이 아니다. 원본8범주와 표식 용도를 삭제하거나 한 목록의9번째 대상으로 바꾸지 않았다.

수리는 기존 admitted fixing 관계의 repair_targets를 재사용한다. 다른 물품의 실제 호환 대상이므로 제작 재료에 레시피 결과물 목록을 붙이는 것과 구분된다. DuctTape/Glue/Scotchtape/Woodglue/SheetMetal/SmallSheetMetal은 서로 다른 물품 종류의 호환 관계를 목록으로 명시한다. 동일 표시명으로 번역된 차량 등급 변형은 표시명 한 줄로 묶되 원래 item_id와 관측 refs는 입력 관계에 모두 보존한다. ‘호환되는 다음 물품’으로 같은 이름의 모든 차량 등급 호환을 보장하지 않는다. 단일 총기 및 같은 산탄총의 총열 변형은 한 문장, Nails는 ‘못 박은 야구 방망이를 수리할 때 재료로 쓸 수 있다’로 구체화한다. 모든 경우 수리 재료 역할을 유지하고 총기 자체의 사격·개조, 테이프의 부착물 고정·장치 개조, 금속판의 용접·건축 등은 독립 문장으로 보존한다. 수리20개 Compact는 기존 유용한 범주 요약 그대로다.

### 전체 후보 조사와 적용·예외

전체2,105개를 훑어 기존 source_traits의 배열 관계, use_relations의 역할/내용 관계와 관련 direct_function을 조사했다. 아래 수는 관계별이며 같은 아이템이 여러 행에 포함될 수 있다.

| 관계 | 항목 수 | 처리와 판단 |
|---|---:|---|
| 색상 매핑에 연결된 도색 대상 | 16 | 신규 요약/상세목록 적용. 페인트15+붓1 전체 |
| 실제 학습 내용 | 25 | 기존 목록82개를 같은 공통 구성 함수로 이관. 두 언어·표면 문구 전부 동일 |
| 여러 종류의 수리 호환 대상 | 6 | 실제 대상 목록 적용 |
| 단일 대상 또는 동종 총기 수리 | 14 | 구체 이름의 한 문장. 불필요한 목록 생성 안 함 |
| 착용 위치/형태 전환 | 79 | 행동별 기존 간결한 문장 유지. 위치 선택은 별도 긴 내용 목록이 아님 |
| 해체 대상 예시 | 3 | 목제 계단·기둥 조명의 기존 한 문장 유지. 대표 예시를 전수 대상으로 바꾸지 않음 |
| 상처 소독 기능 | 4 | 기존 문장 유지. Disinfectant/WhiskeyFull의 천·솜·상처는 한 행동으로 충분. 처리 대상/소독제 역할을 혼동하지 않음 |
| 일반 recipe 참가 관계 | 225 | 학습 내용과 구분. 제작 재료/도구/변환 대상의 레시피 결과를 일괄 공개 목록으로 옮기지 않음 |
| 총기 부착물 | 14 | 개별 총기 전수 호환 목록의 채택된 구조화 관계 없음. 확인된 호환 장착/해제 및 목적 설명 유지, 목록 형태로 구체성 부족을 감추지 않음 |
| 가구 배치 | 140 | 자기 자신을 배치하는 기능은 외부 대상 집합이 아님. 알려진 용도를 보존하고 근거 없는 새 기능/대상은 생성하지 않음 |

새 상세목록은22개(페인트16+수리6), 기존 학습 목록25개는 보존됐다. 수리20개의 모든 대상명·조건부 호환 문구를 대조했다. 일반 recipe 관계와 부착물/가구의 전체 native 기능·대상 복구는 이번 목록 구성으로 해결됐다고 주장하지 않는다. 미래 어댑터나 B42 준비를 추가하지 않았다.

### 재생성·문면 검수·검증

정식 composition/description 생산 경로로 전체2,105개를 재생성했다. 변경36개·104표면(KO C16/E36, EN C16/E36)이며 변경36개×KO/EN×C/E=144전문을 기준본과 대조했다. 동일 전문은21개 묶음으로 읽었다. 각 언어/표면 present1,976·absent129·failed0과 모든 상태는 동일하다. 영향 범위 밖2,069개는 네 표면 모두 본문이 동일하다. 학습25개/목록82개도 네 표면 전부 동일하며, 직전 연료 역할·소독 묶음·단조 재료·해체 대상·표시명 교정은 회귀하지 않았다.

Compact에는 줄바꿈 목록이나 ‘다음 대상/다음 물품’ 같은 목록 의존 표현이 없다. Expanded의 페인트 목록은 도색 한 용도에만 속하고 벽 표식은 별도 use_unit이다. 수리 목록의 실제 이름은 입력의 대상 집합과 일치하며 다른 제작/사격/개조 용도는 해당 목록 밖에 남았다. 내부 실행조건을 목록 항목에 재유입하지 않았다.

기존 검사 `_compare_meaning`의 독립 용도 전부를 Compact에도 강제하던 assertion을 제거했다. Expanded 전수 보존은 유지하고 Compact는 Expanded에 근거한 claim 집합이며 유효한 활용 내용을 갖는지 검사한다. 단순 참조 검사는 문장 유용성/정확성 판정을 대신하지 않으므로 실제 요약과 본 설명도 별도로 읽었다. 기존 예시 품질 검사를 전부 없애지는 않았다.

첫 검사에서 신규 검증이 Paint 이름 접두사로 빈 페인트 통까지 선택한 오류가 드러났다(1 failed/1 passed). 제품 생성 규칙은 기능 기반이었으며, 검사도 실제 action_targets 관계를 가진16개 전체를 고르도록 수정했다. 이후2개 기존 계약 통과 후 영어 단일 대상 문장의 관사를 다듬어 마지막으로 전체 재생성과 동일 최소 계약을 확인했다.

- 최종 계약: **2 passed in32.87s, 종료 코드0**, `.tmp/prose/layout-tests-accepted.log`.
- 명령: `uv run --project .\Iris\tooling python -I -B -m pytest --noconftest -c .\Iris\tooling\pyproject.toml .\Iris\build\description\v2\tests\test_layer3_composition.py::test_layer3_composition_contract .\Iris\build\description\v2\tests\test_layer3_description_composition.py::test_layer3_description_composition --basetemp .\.tmp\layout-tests-03 -q -s --tb=short`.
- 전체 영향/예외/대상/독립 용도 대조: `uv run --project .\Iris\tooling python .tmp/prose/layout-audit.py`, 종료 코드0.
- 정식 expanded_projection 및 직렬화를 사용한 실제 Browser/Wiki 소비 코드 검사: `uv run --project .\Iris\tooling python .tmp/prose/layout_menu_final.py`, 종료 코드0. 4,210상태, 변경36개 KO/EN 표시·하이픈 목록·줄바꿈·스크롤 확인.
- runtime fixture: `.tmp/menu/layout-runtime-02/runtime`, `l3p-28e8e176b76dfede82f429d2729020bb696e9002a97654effcbc87550d9bbc30`. 폰트/엔진만 stub이며 현재 제품 ZIP 교체나 실제 게임 화면 검증이 아니다.
- 현재 입력 해시를 product_projection/tooltip_s2_supply에 바인딩하고 두 정식 검토 HTML을 갱신했다. `layout_html_check.py` 종료 코드0, 현재해시 및36개 KO C/E 전문 포함 확인.

검사 성공과 문장 품질 판정은 구분한다. 이번 조사된 관계의 수정 가능한 구성 결함은 적용 범위 전체에서 처리했다. 개별 물품 전수 native 검증이나 실제 글꼴/게임 화면, 새로운 제품 패키지는 완료 범위에 넣지 않는다. 패키징/설치/커밋/푸시는 수행하지 않았다.

descriptions SHA-256: `32872f2239900807b721e196708c9f908841938c709286b38a99c76f307b2e96`

blocks SHA-256: `ac07107c1d376c59d1b1ce81d73f9b383327b89874e51991d8a28275628f28a2`

### 관계별 전체 후보 ID

```json
{
  "recipe_participants_not_learning_contents": [
    "Base.223Box",
    "Base.223Bullets",
    "Base.223BulletsMold",
    "Base.308Box",
    "Base.308Bullets",
    "Base.308BulletsMold",
    "Base.556Box",
    "Base.556Bullets",
    "Base.9mmBulletsMold",
    "Base.Aerosolbomb",
    "Base.AlarmClock2",
    "Base.Aluminum",
    "Base.Amplifier",
    "Base.Axe",
    "Base.AxeStone",
    "Base.BakingPan",
    "Base.BakingSoda",
    "Base.BakingTray_Muffin",
    "Base.BakingTray_Muffin_Recipe",
    "Base.BallPeenHammer",
    "Base.Baloney",
    "Base.Bandage",
    "Base.BandageDirty",
    "Base.BaseballBat",
    "Base.BaseballBatNails",
    "Base.Bass",
    "Base.BeerEmpty",
    "Base.BlowTorch",
    "Base.Bowl",
    "Base.Bread",
    "Base.BreadDough",
    "Base.BreadKnife",
    "Base.BucketEmpty",
    "Base.BucketWaterFull",
    "Base.Bullets38",
    "Base.Bullets38Box",
    "Base.Bullets44",
    "Base.Bullets44Box",
    "Base.Bullets45",
    "Base.Bullets45Box",
    "Base.Bullets9mm",
    "Base.Bullets9mmBox",
    "Base.ButterKnife",
    "Base.CakeBatter",
    "Base.CakeRaw",
    "Base.Camera",
    "Base.CameraDisposable",
    "Base.CameraExpensive",
    "Base.CannedBolognese",
    "Base.CannedCarrots2",
    "Base.CannedChili",
    "Base.CannedCorn",
    "Base.CannedCornedBeef",
    "Base.CannedFruitBeverage",
    "Base.CannedFruitCocktail",
    "Base.CannedMilk",
    "Base.CannedMilkOpen",
    "Base.CannedMushroomSoup",
    "Base.CannedPeaches",
    "Base.CannedPeas",
    "Base.CannedPineapple",
    "Base.CannedPotato2",
    "Base.CannedSardines",
    "Base.CannedTomato2",
    "Base.Catfish",
    "Base.Coldpack",
    "Base.Comfrey",
    "Base.CookieChocolateChipDough",
    "Base.CookiesChocolateDough",
    "Base.CookiesOatmealDough",
    "Base.CookiesShortbreadDough",
    "Base.CookiesSugarDough",
    "Base.CordlessPhone",
    "Base.Cornflour",
    "Base.CottonBalls",
    "Base.Crappie",
    "Base.DeadBird",
    "Base.DeadMouse",
    "Base.DeadRabbit",
    "Base.DeadRat",
    "Base.DeadSquirrel",
    "Base.DenimStrips",
    "Base.DenimStripsDirty",
    "Base.Disinfectant",
    "Base.Dogfood",
    "Base.Doorknob",
    "Base.DuctTape",
    "Base.Earbuds",
    "Base.Egg",
    "Base.ElectronicsScrap",
    "Base.FishingLine",
    "Base.FishingRodBreak",
    "Base.FlameTrap",
    "Base.FlintKnife",
    "Base.Flour",
    "Base.Fork",
    "Base.Frog",
    "Base.GardenSaw",
    "Base.Glue",
    "Base.GravyMix",
    "Base.GriddlePanFriedVegetables",
    "Base.GunPowder",
    "Base.Hairspray",
    "Base.Ham",
    "Base.Hammer",
    "Base.HammerStone",
    "Base.HandAxe",
    "Base.Headphones",
    "Base.HuntingKnife",
    "Base.IronIngot",
    "Base.KitchenKnife",
    "Base.LeatherStripsDirty",
    "Base.Log",
    "Base.Machete",
    "Base.MeatCleaver",
    "Base.MetalPipe",
    "Base.Milk",
    "Base.MortarPestle",
    "Base.MotionSensor",
    "Base.Muffintray_Biscuit",
    "Base.Nails",
    "Base.NailsBox",
    "Base.Needle",
    "Base.Newspaper",
    "Base.NoiseTrap",
    "Base.OmeletteRecipe",
    "Base.Onion",
    "Base.OnionRings",
    "Base.OpenBeans",
    "Base.Pan",
    "Base.PanFriedVegetables",
    "Base.PanFriedVegetables2",
    "Base.PancakeMix",
    "Base.Panfish",
    "Base.Paperclip",
    "Base.PaperclipBox",
    "Base.Perch",
    "Base.PetrolBleachBottle",
    "Base.PetrolCan",
    "Base.PetrolPopBottle",
    "Base.PieDough",
    "Base.PieWholeRaw",
    "Base.PieWholeRawSweet",
    "Base.Pike",
    "Base.Pillow",
    "Base.PipeBomb",
    "Base.PizzaRecipe",
    "Base.PizzaWhole",
    "Base.Plank",
    "Base.Plantain",
    "Base.PlasterPowder",
    "Base.Pumpkin",
    "Base.Receiver",
    "Base.Remote",
    "Base.RippedSheets",
    "Base.RippedSheetsDirty",
    "Base.RollingPin",
    "Base.Salami",
    "Base.Saw",
    "Base.Screwdriver",
    "Base.Screws",
    "Base.ScrewsBox",
    "Base.SharpedStone",
    "Base.Sheet",
    "Base.SheetMetal",
    "Base.ShotgunShells",
    "Base.ShotgunShellsBox",
    "Base.ShotgunShellsMold",
    "Base.Shrimp",
    "Base.Sledgehammer",
    "Base.Sledgehammer2",
    "Base.SmallSheetMetal",
    "Base.SmokeBomb",
    "Base.Sparklers",
    "Base.Spatula",
    "Base.Spoon",
    "Base.Squid",
    "Base.Stone",
    "Base.Thread",
    "Base.Timer",
    "Base.TimerCrafted",
    "Base.TinOpener",
    "Base.TinnedBeans",
    "Base.TinnedSoup",
    "Base.Tongs",
    "Base.TreeBranch",
    "Base.TriggerCrafted",
    "Base.Trout",
    "Base.TunaTin",
    "Base.Twine",
    "Base.VideoGame",
    "Base.WaterBottleEmpty",
    "Base.WaterBottlePetrol",
    "Base.Watermelon",
    "Base.WeldingMask",
    "Base.WhiskeyEmpty",
    "Base.WhiskeyFull",
    "Base.WhiskeyPetrol",
    "Base.WildEggs",
    "Base.WildGarlic",
    "Base.WildGarlic2",
    "Base.WineEmpty",
    "Base.WineEmpty2",
    "Base.WinePetrol",
    "Base.Wire",
    "Base.WoodAxe",
    "Base.WoodenStick",
    "Radio.RadioReceiver",
    "farming.Bacon",
    "farming.BaconRashers",
    "farming.BroccoliBagSeed",
    "farming.BroccoliSeed",
    "farming.CabbageBagSeed",
    "farming.CabbageSeed",
    "farming.CarrotBagSeed",
    "farming.CarrotSeed",
    "farming.GardeningSprayEmpty",
    "farming.PotatoBagSeed",
    "farming.PotatoSeed",
    "farming.RedRadishBagSeed",
    "farming.RedRadishSeed",
    "farming.StrewberrieBagSeed",
    "farming.StrewberrieSeed",
    "farming.TomatoBagSeed",
    "farming.TomatoSeed"
  ],
  "inline_disinfection": [
    "Base.AlcoholWipes",
    "Base.AlcoholedCottonBalls",
    "Base.Disinfectant",
    "Base.WhiskeyFull"
  ],
  "no_named_compatibility_set_attachments": [
    "Base.AmmoStraps",
    "Base.Bayonnet",
    "Base.ChokeTubeFull",
    "Base.ChokeTubeImproved",
    "Base.FiberglassStock",
    "Base.GunLight",
    "Base.IronSight",
    "Base.Laser",
    "Base.RecoilPad",
    "Base.RedDot",
    "Base.Sling",
    "Base.x2Scope",
    "Base.x4Scope",
    "Base.x8Scope"
  ],
  "inline_homogeneous_repair_targets": [
    "Base.AssaultRifle",
    "Base.AssaultRifle2",
    "Base.DoubleBarrelShotgun",
    "Base.HuntingRifle",
    "Base.Nails",
    "Base.Pistol",
    "Base.Pistol2",
    "Base.Pistol3",
    "Base.Revolver",
    "Base.Revolver_Long",
    "Base.Revolver_Short",
    "Base.Shotgun",
    "Base.ShotgunSawnoff",
    "Base.VarmintRifle"
  ],
  "existing_action_sentences_wearing": [
    "Base.Bag_FannyPackBack",
    "Base.Bag_FannyPackFront",
    "Base.Bracelet_BangleLeftGold",
    "Base.Bracelet_BangleLeftSilver",
    "Base.Bracelet_BangleRightGold",
    "Base.Bracelet_BangleRightSilver",
    "Base.Bracelet_ChainLeftGold",
    "Base.Bracelet_ChainLeftSilver",
    "Base.Bracelet_ChainRightGold",
    "Base.Bracelet_ChainRightSilver",
    "Base.Bracelet_LeftFriendshipTINT",
    "Base.Bracelet_RightFriendshipTINT",
    "Base.Earring_LoopSmall_Gold_Both",
    "Base.Earring_LoopSmall_Gold_Top",
    "Base.Earring_LoopSmall_Silver_Both",
    "Base.Earring_LoopSmall_Silver_Top",
    "Base.Glasses_Eyepatch_Left",
    "Base.Glasses_Eyepatch_Right",
    "Base.Hat_Bandana",
    "Base.Hat_BandanaMask",
    "Base.Hat_BandanaMaskTINT",
    "Base.Hat_BandanaTINT",
    "Base.Hat_BandanaTied",
    "Base.Hat_BandanaTiedTINT",
    "Base.Hat_BaseballCap",
    "Base.Hat_BaseballCapArmy",
    "Base.Hat_BaseballCapArmy_Reverse",
    "Base.Hat_BaseballCapBlue",
    "Base.Hat_BaseballCapBlue_Reverse",
    "Base.Hat_BaseballCapGreen",
    "Base.Hat_BaseballCapGreen_Reverse",
    "Base.Hat_BaseballCapKY",
    "Base.Hat_BaseballCapKY_Red",
    "Base.Hat_BaseballCapKY_Reverse",
    "Base.Hat_BaseballCapRed",
    "Base.Hat_BaseballCapRed_Reverse",
    "Base.Hat_BaseballCap_Reverse",
    "Base.HoodieDOWN_WhiteTINT",
    "Base.HoodieUP_WhiteTINT",
    "Base.Jacket_Padded",
    "Base.Jacket_PaddedDOWN",
    "Base.PonchoGreen",
    "Base.PonchoGreenDOWN",
    "Base.PonchoYellow",
    "Base.PonchoYellowDOWN",
    "Base.Ring_Left_MiddleFinger_Gold",
    "Base.Ring_Left_MiddleFinger_GoldDiamond",
    "Base.Ring_Left_MiddleFinger_GoldRuby",
    "Base.Ring_Left_MiddleFinger_Silver",
    "Base.Ring_Left_MiddleFinger_SilverDiamond",
    "Base.Ring_Left_RingFinger_Gold",
    "Base.Ring_Left_RingFinger_GoldDiamond",
    "Base.Ring_Left_RingFinger_GoldRuby",
    "Base.Ring_Left_RingFinger_Silver",
    "Base.Ring_Left_RingFinger_SilverDiamond",
    "Base.Ring_Right_MiddleFinger_Gold",
    "Base.Ring_Right_MiddleFinger_GoldDiamond",
    "Base.Ring_Right_MiddleFinger_GoldRuby",
    "Base.Ring_Right_MiddleFinger_Silver",
    "Base.Ring_Right_MiddleFinger_SilverDiamond",
    "Base.Ring_Right_RingFinger_Gold",
    "Base.Ring_Right_RingFinger_GoldDiamond",
    "Base.Ring_Right_RingFinger_GoldRuby",
    "Base.Ring_Right_RingFinger_Silver",
    "Base.Ring_Right_RingFinger_SilverDiamond",
    "Base.WristWatch_Left_ClassicBlack",
    "Base.WristWatch_Left_ClassicBrown",
    "Base.WristWatch_Left_ClassicGold",
    "Base.WristWatch_Left_ClassicMilitary",
    "Base.WristWatch_Left_DigitalBlack",
    "Base.WristWatch_Left_DigitalDress",
    "Base.WristWatch_Left_DigitalRed",
    "Base.WristWatch_Right_ClassicBlack",
    "Base.WristWatch_Right_ClassicBrown",
    "Base.WristWatch_Right_ClassicGold",
    "Base.WristWatch_Right_ClassicMilitary",
    "Base.WristWatch_Right_DigitalBlack",
    "Base.WristWatch_Right_DigitalDress",
    "Base.WristWatch_Right_DigitalRed"
  ],
  "list_learning_content_preserved": [
    "Base.CookingMag1",
    "Base.CookingMag2",
    "Base.ElectronicsMag1",
    "Base.ElectronicsMag2",
    "Base.ElectronicsMag3",
    "Base.ElectronicsMag5",
    "Base.EngineerMagazine1",
    "Base.EngineerMagazine2",
    "Base.FarmingMag1",
    "Base.FishingMag1",
    "Base.FishingMag2",
    "Base.HuntingMag1",
    "Base.HuntingMag2",
    "Base.HuntingMag3",
    "Base.MetalworkMag1",
    "Base.MetalworkMag2",
    "Base.MetalworkMag3",
    "Base.MetalworkMag4",
    "Base.SmithingMag1",
    "Base.SmithingMag2",
    "Base.SmithingMag3",
    "Base.SmithingMag4",
    "Radio.RadioMag1",
    "Radio.RadioMag2",
    "Radio.RadioMag3"
  ],
  "list_compatibility_choices": [
    "Base.DuctTape",
    "Base.Glue",
    "Base.Scotchtape",
    "Base.SheetMetal",
    "Base.SmallSheetMetal",
    "Base.Woodglue"
  ],
  "inline_examples_dismantling": [
    "Base.GardenSaw",
    "Base.Saw",
    "Base.Screwdriver"
  ],
  "placement_not_a_named_external_target_set": [
    "Base.Mattress",
    "Base.Mov_AirConditioner",
    "Base.Mov_AntiqueStove",
    "Base.Mov_ArcadeMachine1",
    "Base.Mov_ArcadeMachine2",
    "Base.Mov_BeachChair",
    "Base.Mov_BinRound",
    "Base.Mov_Birdbath",
    "Base.Mov_BlueComfyChair",
    "Base.Mov_BluePlasticChair",
    "Base.Mov_BlueRattanChair",
    "Base.Mov_BrownComfyChair",
    "Base.Mov_BrownLowTable",
    "Base.Mov_CabinetMedical",
    "Base.Mov_CabinetTool",
    "Base.Mov_CardboardBox",
    "Base.Mov_ChromeSink",
    "Base.Mov_CoffeeMaker",
    "Base.Mov_ConcreteMixer",
    "Base.Mov_CorkBoard",
    "Base.Mov_DarkBlueChair",
    "Base.Mov_DarkWoodenChair",
    "Base.Mov_DegreeDoctor",
    "Base.Mov_DegreeSurgeon",
    "Base.Mov_DesktopComputer",
    "Base.Mov_Doghouse",
    "Base.Mov_Espresso",
    "Base.Mov_FancyBlackChair",
    "Base.Mov_FancyDarkTable",
    "Base.Mov_FancyLowTable",
    "Base.Mov_FancyTable",
    "Base.Mov_FancyToilet",
    "Base.Mov_FancyWhiteChair",
    "Base.Mov_FitnessContraption",
    "Base.Mov_FlagAdmin",
    "Base.Mov_FlagUSA",
    "Base.Mov_FlagUSALarge",
    "Base.Mov_FoldingChair",
    "Base.Mov_FridgeMini",
    "Base.Mov_GardenGnome",
    "Base.Mov_GraveArched",
    "Base.Mov_GraveRound",
    "Base.Mov_GraveSquare",
    "Base.Mov_GraveWorn",
    "Base.Mov_GreenChair",
    "Base.Mov_GreenComfyChair",
    "Base.Mov_GreenOven",
    "Base.Mov_GreyChair",
    "Base.Mov_GreyComfyChair",
    "Base.Mov_GreyOven",
    "Base.Mov_HotdogMachine",
    "Base.Mov_HuntingTrophy",
    "Base.Mov_IndustrialSink",
    "Base.Mov_Lamp1",
    "Base.Mov_Lamp2",
    "Base.Mov_Lamp3",
    "Base.Mov_Lamp4",
    "Base.Mov_Lamp5",
    "Base.Mov_Lamp6",
    "Base.Mov_LightConstruction",
    "Base.Mov_LightRoundTable",
    "Base.Mov_LongTable",
    "Base.Mov_Mailbox",
    "Base.Mov_MannequinFemale",
    "Base.Mov_MannequinMale",
    "Base.Mov_MapUSA",
    "Base.Mov_MetalLocker",
    "Base.Mov_MetalStool",
    "Base.Mov_Microphone",
    "Base.Mov_Microwave",
    "Base.Mov_Microwave2",
    "Base.Mov_MirrorLarge",
    "Base.Mov_MirrorSmall",
    "Base.Mov_MirrorTall",
    "Base.Mov_MirrorWood",
    "Base.Mov_MobileBloodbag",
    "Base.Mov_MobileCounter",
    "Base.Mov_ModernOven",
    "Base.Mov_NapkinDispenser",
    "Base.Mov_OakRoundTable",
    "Base.Mov_OfficeChair",
    "Base.Mov_OrangeFuton",
    "Base.Mov_OrangeModernChair",
    "Base.Mov_PaintingBetty",
    "Base.Mov_PaintingElisa",
    "Base.Mov_PaintingGreen",
    "Base.Mov_PaintingLibrary",
    "Base.Mov_PalletEmpty",
    "Base.Mov_PileOCrepeChair",
    "Base.Mov_PinballMachine",
    "Base.Mov_PinkFlamingo",
    "Base.Mov_PlasticChair",
    "Base.Mov_PlasticLowTable",
    "Base.Mov_PopcornMachine",
    "Base.Mov_PosterDroids",
    "Base.Mov_PosterElement",
    "Base.Mov_PosterMedical",
    "Base.Mov_PosterOmega",
    "Base.Mov_PosterPaws",
    "Base.Mov_PosterPieBlue",
    "Base.Mov_PosterPieGreen",
    "Base.Mov_PosterPiePink",
    "Base.Mov_PosterPieRed",
    "Base.Mov_Projector",
    "Base.Mov_PurpleRattanChair",
    "Base.Mov_PurpleWoodenChair",
    "Base.Mov_RedBBQ",
    "Base.Mov_RedChair",
    "Base.Mov_RedOven",
    "Base.Mov_RedWoodenChair",
    "Base.Mov_RoadBarrier",
    "Base.Mov_RoadCone",
    "Base.Mov_RoadCone2",
    "Base.Mov_RoundTable",
    "Base.Mov_SatelliteDish",
    "Base.Mov_ScaleMedical",
    "Base.Mov_ShoppingBaskets",
    "Base.Mov_SignArmy",
    "Base.Mov_SignCitrus",
    "Base.Mov_SignRestricted",
    "Base.Mov_SignWarning",
    "Base.Mov_SmallTable",
    "Base.Mov_SodaMachine",
    "Base.Mov_TVCamera",
    "Base.Mov_Toaster",
    "Base.Mov_TowelDispenser",
    "Base.Mov_Urinal",
    "Base.Mov_WallClock",
    "Base.Mov_WaterDispenser",
    "Base.Mov_WhiteComfyChair",
    "Base.Mov_WhiteSimpleChair",
    "Base.Mov_WhiteSink",
    "Base.Mov_WhiteWoodenChair",
    "Base.Mov_WoodenChair",
    "Base.Mov_WoodenStool",
    "Base.Mov_YellowModernChair",
    "Base.brokenglass_1_0",
    "Base.brokenglass_1_1",
    "Base.brokenglass_1_2",
    "Base.brokenglass_1_3"
  ],
  "list_scoped_targets": [
    "Base.PaintBlack",
    "Base.PaintBlue",
    "Base.PaintBrown",
    "Base.PaintCyan",
    "Base.PaintGreen",
    "Base.PaintGrey",
    "Base.PaintLightBlue",
    "Base.PaintLightBrown",
    "Base.PaintOrange",
    "Base.PaintPink",
    "Base.PaintPurple",
    "Base.PaintRed",
    "Base.PaintTurquoise",
    "Base.PaintWhite",
    "Base.PaintYellow",
    "Base.Paintbrush"
  ]
}
```

### 변경36개 전체 KO/EN C/E 전후 전문

```text
Base.AssaultRifle
ko/compact
BEFORE 총기를 수리하는 재료로 쓸 수 있다. 탄약을 장전해 사격할 수 있다.
AFTER 총기를 수리하는 재료로 쓸 수 있다. 탄약을 장전해 사격할 수 있다.
ko/expanded
BEFORE 총기를 수리하는 재료로 쓸 수 있다.
탄약을 장전해 사격할 수 있다.
AFTER M16 자동소총을 수리할 때 재료로 쓸 수 있다.
탄약을 장전해 사격할 수 있다.
en/compact
BEFORE It can be used as repair material for firearms. It can be loaded with ammunition for shooting.
AFTER It can be used as repair material for firearms. It can be loaded with ammunition for shooting.
en/expanded
BEFORE It can be used as repair material for firearms.
It can be loaded with ammunition for shooting.
AFTER It can be used as repair material for the M16 Assault Rifle.
It can be loaded with ammunition for shooting.
Base.AssaultRifle2
ko/compact
BEFORE 총기를 수리하는 재료로 쓸 수 있다. 탄약을 장전해 사격할 수 있다.
AFTER 총기를 수리하는 재료로 쓸 수 있다. 탄약을 장전해 사격할 수 있다.
ko/expanded
BEFORE 총기를 수리하는 재료로 쓸 수 있다.
탄약을 장전해 사격할 수 있다.
AFTER M14 단발 자동소총을 수리할 때 재료로 쓸 수 있다.
탄약을 장전해 사격할 수 있다.
en/compact
BEFORE It can be used as repair material for firearms. It can be loaded with ammunition for shooting.
AFTER It can be used as repair material for firearms. It can be loaded with ammunition for shooting.
en/expanded
BEFORE It can be used as repair material for firearms.
It can be loaded with ammunition for shooting.
AFTER It can be used as repair material for the M14 Single Shot Assault Rifle.
It can be loaded with ammunition for shooting.
Base.DoubleBarrelShotgun
ko/compact
BEFORE 총기를 수리하는 재료로 쓸 수 있다. 탄약을 장전해 사격할 수 있다. 총신을 짧게 개조할 수 있다.
AFTER 총기를 수리하는 재료로 쓸 수 있다. 탄약을 장전해 사격할 수 있다. 총신을 짧게 개조할 수 있다.
ko/expanded
BEFORE 총기를 수리하는 재료로 쓸 수 있다.
탄약을 장전해 사격할 수 있다.
총신을 짧게 개조할 수 있다.
AFTER 더블 배럴 산탄총을 수리할 때 재료로 쓸 수 있다.
탄약을 장전해 사격할 수 있다.
총신을 짧게 개조할 수 있다.
en/compact
BEFORE It can be used as repair material for firearms. It can be loaded with ammunition for shooting. Its shotgun barrel can be shortened.
AFTER It can be used as repair material for firearms. It can be loaded with ammunition for shooting. Its shotgun barrel can be shortened.
en/expanded
BEFORE It can be used as repair material for firearms.
It can be loaded with ammunition for shooting.
Its shotgun barrel can be shortened.
AFTER It can be used as repair material for the Double Barrel Shotgun.
It can be loaded with ammunition for shooting.
Its shotgun barrel can be shortened.
Base.DuctTape
ko/compact
BEFORE 창 부착물 고정, 장치 개조, 무기 수리 및 호환 차량 부품 수리에 재료로 쓸 수 있다.
AFTER 창 부착물 고정, 장치 개조, 무기 수리 및 호환 차량 부품 수리에 재료로 쓸 수 있다.
ko/expanded
BEFORE 창에 부착물을 다는 재료로 쓸 수 있다.
장치에 움직임 감지, 시간 지연, 원격 작동 기능을 더하는 재료로 쓸 수 있다.
무기 및 호환 차량 부품을 수리하는 재료로 쓸 수 있다.
AFTER 창에 부착물을 다는 재료로 쓸 수 있다.
장치에 움직임 감지, 시간 지연, 원격 작동 기능을 더하는 재료로 쓸 수 있다.
호환되는 다음 물품을 수리할 때 재료로 쓸 수 있다.
- 도끼
- 배드민턴 라켓
- 둥근머리 망치
- 밴조
- 야구 방망이
- 못 박은 야구 방망이
- 빗자루
- 카누용 노
- 카누용 이중 노
- 클럽 해머
- 쇠스랑
- 괭이
- 글로브 박스
- 골프클럽
- 번철 팬
- 어쿠스틱 기타
- 전기 베이스 (검은색)
- 전기 베이스 (파란색)
- 전기 베이스 (빨간색)
- 전기 기타 (검은색)
- 전기 기타 (파란색)
- 전기 기타 (빨간색)
- 망치
- 손도끼
- 손갈퀴
- 손낫
- 하키 스틱
- 사냥용 칼
- 아이스하키 스틱
- 부엌칼
- 라크로스 스틱
- 갈퀴
- 마체테
- 중형 좌석
- 프라이팬
- 곡괭이
- 밀대
- 색소폰
- 삽
- 대형 망치
- 눈 삽
- 창 (빵칼)
- 창 (버터칼)
- 제작한 창
- 창 (손갈퀴)
- 창 (사냥용 칼)
- 창 (얼음 송곳)
- 창 (부엌칼)
- 창 (편지 칼)
- 창 (마체테)
- 창 (메스)
- 창 (가위)
- 창 (드라이버)
- 창 (숟가락)
- 테니스 라켓
- 트럼펫
- 바이올린
- 벌목 도끼
- 나무 망치
en/compact
BEFORE It can supply material for attaching items to spears, modifying devices, repairing weapons, and repairing compatible vehicle parts.
AFTER It can supply material for attaching items to spears, modifying devices, repairing weapons, and repairing compatible vehicle parts.
en/expanded
BEFORE It can be used as material for attaching items to spears.
It can be used as material for adding motion sensing, time delay, and remote activation to devices.
It can be used as repair material for weapons and compatible vehicle parts.
AFTER It can be used as material for attaching items to spears.
It can be used as material for adding motion sensing, time delay, and remote activation to devices.
It can be used as repair material for compatible items from the following list.
- Axe
- Badminton Racket
- Ball Peen Hammer
- Banjo
- Baseball Bat
- Spiked Baseball Bat
- Broom
- Canoe Paddle
- Canoe Paddle Double
- Club Hammer
- Garden Fork
- Garden Hoe
- Glove Box
- Golfclub
- Griddle Pan
- Acoustic Guitar
- Black Electric Bass
- Blue Electric Bass
- Red Electric Bass
- Black Electric Guitar
- Blue Electric Guitar
- Red Electric Guitar
- Hammer
- Hand Axe
- Hand Fork
- Hand Scythe
- Hockey Stick
- Hunting Knife
- Ice Hockey Stick
- Kitchen Knife
- LaCrosse Stick
- Leaf Rake
- Machete
- Standard Seat
- Frying Pan
- PickAxe
- Rake
- Rolling Pin
- Saxophone
- Shovel
- Sledgehammer
- Snow Shovel
- Spear With Bread Knife
- Spear With Butter Knife
- Crafted Spear
- Spear With Hand Fork
- Spear With Hunting Knife
- Spear With Ice Pick
- Spear With Knife
- Spear With Letter Opener
- Spear With Machete
- Spear With Scalpel
- Spear With Scissors
- Spear With Screwdriver
- Spear With Spoon
- Tennis Racket
- Trumpet
- Violin
- Wood Axe
- Wooden Mallet
Base.Glue
ko/compact
BEFORE 무기 수리 및 호환 차량 부품 수리에 재료로 쓸 수 있다. 전자 기기 제작에도 쓸 수 있다.
AFTER 무기 수리 및 호환 차량 부품 수리에 재료로 쓸 수 있다. 전자 기기 제작에도 쓸 수 있다.
ko/expanded
BEFORE 전자 기기를 만드는 재료로 쓸 수 있다.
무기 및 호환 차량 부품을 수리하는 재료로 쓸 수 있다.
AFTER 전자 기기를 만드는 재료로 쓸 수 있다.
호환되는 다음 물품을 수리할 때 재료로 쓸 수 있다.
- 도끼
- 야구 방망이
- 못 박은 야구 방망이
- 빗자루
- 카누용 노
- 카누용 이중 노
- 클럽 해머
- 쇠스랑
- 괭이
- 글로브 박스
- 번철 팬
- 망치
- 손도끼
- 손갈퀴
- 손낫
- 하키 스틱
- 사냥용 칼
- 아이스하키 스틱
- 부엌칼
- 라크로스 스틱
- 갈퀴
- 중형 좌석
- 프라이팬
- 곡괭이
- 밀대
- 삽
- 대형 망치
- 눈 삽
- 창 (빵칼)
- 창 (버터칼)
- 제작한 창
- 창 (손갈퀴)
- 창 (사냥용 칼)
- 창 (얼음 송곳)
- 창 (부엌칼)
- 창 (편지 칼)
- 창 (마체테)
- 창 (메스)
- 창 (가위)
- 창 (드라이버)
- 창 (숟가락)
- 벌목 도끼
- 나무 망치
en/compact
BEFORE It can supply material for repairing weapons and repairing compatible vehicle parts or for making electronic devices.
AFTER It can supply material for repairing weapons and repairing compatible vehicle parts or for making electronic devices.
en/expanded
BEFORE It can be used as material for making electronic devices.
It can be used as repair material for weapons and compatible vehicle parts.
AFTER It can be used as material for making electronic devices.
It can be used as repair material for compatible items from the following list.
- Axe
- Baseball Bat
- Spiked Baseball Bat
- Broom
- Canoe Paddle
- Canoe Paddle Double
- Club Hammer
- Garden Fork
- Garden Hoe
- Glove Box
- Griddle Pan
- Hammer
- Hand Axe
- Hand Fork
- Hand Scythe
- Hockey Stick
- Hunting Knife
- Ice Hockey Stick
- Kitchen Knife
- LaCrosse Stick
- Leaf Rake
- Standard Seat
- Frying Pan
- PickAxe
- Rake
- Rolling Pin
- Shovel
- Sledgehammer
- Snow Shovel
- Spear With Bread Knife
- Spear With Butter Knife
- Crafted Spear
- Spear With Hand Fork
- Spear With Hunting Knife
- Spear With Ice Pick
- Spear With Knife
- Spear With Letter Opener
- Spear With Machete
- Spear With Scalpel
- Spear With Scissors
- Spear With Screwdriver
- Spear With Spoon
- Wood Axe
- Wooden Mallet
Base.HuntingRifle
ko/compact
BEFORE 총기를 수리하는 재료로 쓸 수 있다. 탄약을 장전해 사격할 수 있다.
AFTER 총기를 수리하는 재료로 쓸 수 있다. 탄약을 장전해 사격할 수 있다.
ko/expanded
BEFORE 총기를 수리하는 재료로 쓸 수 있다.
탄약을 장전해 사격할 수 있다.
AFTER 사냥용 소총을 수리할 때 재료로 쓸 수 있다.
탄약을 장전해 사격할 수 있다.
en/compact
BEFORE It can be used as repair material for firearms. It can be loaded with ammunition for shooting.
AFTER It can be used as repair material for firearms. It can be loaded with ammunition for shooting.
en/expanded
BEFORE It can be used as repair material for firearms.
It can be loaded with ammunition for shooting.
AFTER It can be used as repair material for the MSR788 Rifle.
It can be loaded with ammunition for shooting.
Base.Nails
ko/compact
BEFORE 목공, 건축 및 무기 수리에 재료로 쓸 수 있다. 사냥 장비 및 낚시 장비 제작에도 쓸 수 있다. 모아서 상자로 포장할 수 있다. 위층 창문 등에 탈출용 로프를 고정할 수 있다.
AFTER 목공, 건축 및 무기 수리에 재료로 쓸 수 있다. 사냥 장비 및 낚시 장비 제작에도 쓸 수 있다. 모아서 상자로 포장할 수 있다. 위층 창문 등에 탈출용 로프를 고정할 수 있다.
ko/expanded
BEFORE 목공과 건축 재료로 쓸 수 있다. 문과 창문의 판자 바리케이드에도 재료로 쓸 수 있다.
사냥과 낚시 장비를 만드는 재료로 쓸 수 있다.
무기를 수리하는 재료로 쓸 수 있다.
모아서 상자로 포장할 수 있다.
위층 창문 등에 탈출용 로프를 고정할 수 있다.
AFTER 목공과 건축 재료로 쓸 수 있다. 문과 창문의 판자 바리케이드에도 재료로 쓸 수 있다.
사냥과 낚시 장비를 만드는 재료로 쓸 수 있다.
못 박은 야구 방망이를 수리할 때 재료로 쓸 수 있다.
모아서 상자로 포장할 수 있다.
위층 창문 등에 탈출용 로프를 고정할 수 있다.
en/compact
BEFORE It can supply material for woodworking and construction and repairing weapons or for making hunting equipment and fishing equipment. It can be collected and packed into a box. It can be used to anchor an escape rope at an upper-floor window or similar attachment.
AFTER It can supply material for woodworking and construction and repairing weapons or for making hunting equipment and fishing equipment. It can be collected and packed into a box. It can be used to anchor an escape rope at an upper-floor window or similar attachment.
en/expanded
BEFORE It can be used as material for woodworking and construction. It can also supply window and door barricades.
It can be used as material for making hunting and fishing equipment.
It can be used as repair material for weapons.
It can be collected and packed into a box.
It can be used to anchor an escape rope at an upper-floor window or similar attachment.
AFTER It can be used as material for woodworking and construction. It can also supply window and door barricades.
It can be used as material for making hunting and fishing equipment.
It can be used as repair material for the Spiked Baseball Bat.
It can be collected and packed into a box.
It can be used to anchor an escape rope at an upper-floor window or similar attachment.
Base.PaintBlack
ko/compact
BEFORE 벽, 문틀, 창틀, 기둥과 일부 문, 의자, 상자, 탁자를 칠할 수 있다. 벽에 표식을 그릴 수 있다.
AFTER 벽이나 가구 등을 칠하고, 벽에 표식을 그릴 수 있다.
ko/expanded
BEFORE 벽, 문틀, 창틀, 기둥과 일부 문, 의자, 상자, 탁자를 칠할 수 있다.
벽에 표식을 그릴 수 있다.
AFTER 다음 대상을 칠할 수 있다.
- 벽
- 문틀
- 창틀
- 기둥
- 일부 문
- 일부 의자
- 일부 상자
- 일부 탁자
벽에 표식을 그릴 수 있다.
en/compact
BEFORE It can be used to paint walls, door frames, window frames and pillars, as well as some doors, chairs, crates and tables. It can be used to paint signs on walls.
AFTER It can be used to paint walls or furniture, for example, and paint signs on walls.
en/expanded
BEFORE It can be used to paint walls, door frames, window frames and pillars, as well as some doors, chairs, crates and tables.
It can be used to paint signs on walls.
AFTER It can be used to paint the following targets.
- Walls
- Door frames
- Window frames
- Pillars
- Some doors
- Some chairs
- Some crates
- Some tables
It can be used to paint signs on walls.
Base.PaintBlue
ko/compact
BEFORE 벽, 문틀, 창틀, 기둥과 일부 문, 의자, 상자, 탁자를 칠할 수 있다. 벽에 표식을 그릴 수 있다.
AFTER 벽이나 가구 등을 칠하고, 벽에 표식을 그릴 수 있다.
ko/expanded
BEFORE 벽, 문틀, 창틀, 기둥과 일부 문, 의자, 상자, 탁자를 칠할 수 있다.
벽에 표식을 그릴 수 있다.
AFTER 다음 대상을 칠할 수 있다.
- 벽
- 문틀
- 창틀
- 기둥
- 일부 문
- 일부 의자
- 일부 상자
- 일부 탁자
벽에 표식을 그릴 수 있다.
en/compact
BEFORE It can be used to paint walls, door frames, window frames and pillars, as well as some doors, chairs, crates and tables. It can be used to paint signs on walls.
AFTER It can be used to paint walls or furniture, for example, and paint signs on walls.
en/expanded
BEFORE It can be used to paint walls, door frames, window frames and pillars, as well as some doors, chairs, crates and tables.
It can be used to paint signs on walls.
AFTER It can be used to paint the following targets.
- Walls
- Door frames
- Window frames
- Pillars
- Some doors
- Some chairs
- Some crates
- Some tables
It can be used to paint signs on walls.
Base.PaintBrown
ko/compact
BEFORE 벽, 문틀, 창틀, 기둥과 일부 문, 의자, 상자, 탁자를 칠할 수 있다. 벽에 표식을 그릴 수 있다.
AFTER 벽이나 가구 등을 칠하고, 벽에 표식을 그릴 수 있다.
ko/expanded
BEFORE 벽, 문틀, 창틀, 기둥과 일부 문, 의자, 상자, 탁자를 칠할 수 있다.
벽에 표식을 그릴 수 있다.
AFTER 다음 대상을 칠할 수 있다.
- 벽
- 문틀
- 창틀
- 기둥
- 일부 문
- 일부 의자
- 일부 상자
- 일부 탁자
벽에 표식을 그릴 수 있다.
en/compact
BEFORE It can be used to paint walls, door frames, window frames and pillars, as well as some doors, chairs, crates and tables. It can be used to paint signs on walls.
AFTER It can be used to paint walls or furniture, for example, and paint signs on walls.
en/expanded
BEFORE It can be used to paint walls, door frames, window frames and pillars, as well as some doors, chairs, crates and tables.
It can be used to paint signs on walls.
AFTER It can be used to paint the following targets.
- Walls
- Door frames
- Window frames
- Pillars
- Some doors
- Some chairs
- Some crates
- Some tables
It can be used to paint signs on walls.
Base.PaintCyan
ko/compact
BEFORE 벽, 문틀, 창틀, 기둥과 일부 문, 의자, 상자, 탁자를 칠할 수 있다. 벽에 표식을 그릴 수 있다.
AFTER 벽이나 가구 등을 칠하고, 벽에 표식을 그릴 수 있다.
ko/expanded
BEFORE 벽, 문틀, 창틀, 기둥과 일부 문, 의자, 상자, 탁자를 칠할 수 있다.
벽에 표식을 그릴 수 있다.
AFTER 다음 대상을 칠할 수 있다.
- 벽
- 문틀
- 창틀
- 기둥
- 일부 문
- 일부 의자
- 일부 상자
- 일부 탁자
벽에 표식을 그릴 수 있다.
en/compact
BEFORE It can be used to paint walls, door frames, window frames and pillars, as well as some doors, chairs, crates and tables. It can be used to paint signs on walls.
AFTER It can be used to paint walls or furniture, for example, and paint signs on walls.
en/expanded
BEFORE It can be used to paint walls, door frames, window frames and pillars, as well as some doors, chairs, crates and tables.
It can be used to paint signs on walls.
AFTER It can be used to paint the following targets.
- Walls
- Door frames
- Window frames
- Pillars
- Some doors
- Some chairs
- Some crates
- Some tables
It can be used to paint signs on walls.
Base.PaintGreen
ko/compact
BEFORE 벽, 문틀, 창틀, 기둥과 일부 문, 의자, 상자, 탁자를 칠할 수 있다. 벽에 표식을 그릴 수 있다.
AFTER 벽이나 가구 등을 칠하고, 벽에 표식을 그릴 수 있다.
ko/expanded
BEFORE 벽, 문틀, 창틀, 기둥과 일부 문, 의자, 상자, 탁자를 칠할 수 있다.
벽에 표식을 그릴 수 있다.
AFTER 다음 대상을 칠할 수 있다.
- 벽
- 문틀
- 창틀
- 기둥
- 일부 문
- 일부 의자
- 일부 상자
- 일부 탁자
벽에 표식을 그릴 수 있다.
en/compact
BEFORE It can be used to paint walls, door frames, window frames and pillars, as well as some doors, chairs, crates and tables. It can be used to paint signs on walls.
AFTER It can be used to paint walls or furniture, for example, and paint signs on walls.
en/expanded
BEFORE It can be used to paint walls, door frames, window frames and pillars, as well as some doors, chairs, crates and tables.
It can be used to paint signs on walls.
AFTER It can be used to paint the following targets.
- Walls
- Door frames
- Window frames
- Pillars
- Some doors
- Some chairs
- Some crates
- Some tables
It can be used to paint signs on walls.
Base.PaintGrey
ko/compact
BEFORE 벽, 문틀, 창틀, 기둥과 일부 문, 의자, 상자, 탁자를 칠할 수 있다. 벽에 표식을 그릴 수 있다.
AFTER 벽이나 가구 등을 칠하고, 벽에 표식을 그릴 수 있다.
ko/expanded
BEFORE 벽, 문틀, 창틀, 기둥과 일부 문, 의자, 상자, 탁자를 칠할 수 있다.
벽에 표식을 그릴 수 있다.
AFTER 다음 대상을 칠할 수 있다.
- 벽
- 문틀
- 창틀
- 기둥
- 일부 문
- 일부 의자
- 일부 상자
- 일부 탁자
벽에 표식을 그릴 수 있다.
en/compact
BEFORE It can be used to paint walls, door frames, window frames and pillars, as well as some doors, chairs, crates and tables. It can be used to paint signs on walls.
AFTER It can be used to paint walls or furniture, for example, and paint signs on walls.
en/expanded
BEFORE It can be used to paint walls, door frames, window frames and pillars, as well as some doors, chairs, crates and tables.
It can be used to paint signs on walls.
AFTER It can be used to paint the following targets.
- Walls
- Door frames
- Window frames
- Pillars
- Some doors
- Some chairs
- Some crates
- Some tables
It can be used to paint signs on walls.
Base.PaintLightBlue
ko/compact
BEFORE 벽, 문틀, 창틀, 기둥과 일부 문, 의자, 상자, 탁자를 칠할 수 있다. 벽에 표식을 그릴 수 있다.
AFTER 벽이나 가구 등을 칠하고, 벽에 표식을 그릴 수 있다.
ko/expanded
BEFORE 벽, 문틀, 창틀, 기둥과 일부 문, 의자, 상자, 탁자를 칠할 수 있다.
벽에 표식을 그릴 수 있다.
AFTER 다음 대상을 칠할 수 있다.
- 벽
- 문틀
- 창틀
- 기둥
- 일부 문
- 일부 의자
- 일부 상자
- 일부 탁자
벽에 표식을 그릴 수 있다.
en/compact
BEFORE It can be used to paint walls, door frames, window frames and pillars, as well as some doors, chairs, crates and tables. It can be used to paint signs on walls.
AFTER It can be used to paint walls or furniture, for example, and paint signs on walls.
en/expanded
BEFORE It can be used to paint walls, door frames, window frames and pillars, as well as some doors, chairs, crates and tables.
It can be used to paint signs on walls.
AFTER It can be used to paint the following targets.
- Walls
- Door frames
- Window frames
- Pillars
- Some doors
- Some chairs
- Some crates
- Some tables
It can be used to paint signs on walls.
Base.PaintLightBrown
ko/compact
BEFORE 벽, 문틀, 창틀, 기둥과 일부 문, 의자, 상자, 탁자를 칠할 수 있다. 벽에 표식을 그릴 수 있다.
AFTER 벽이나 가구 등을 칠하고, 벽에 표식을 그릴 수 있다.
ko/expanded
BEFORE 벽, 문틀, 창틀, 기둥과 일부 문, 의자, 상자, 탁자를 칠할 수 있다.
벽에 표식을 그릴 수 있다.
AFTER 다음 대상을 칠할 수 있다.
- 벽
- 문틀
- 창틀
- 기둥
- 일부 문
- 일부 의자
- 일부 상자
- 일부 탁자
벽에 표식을 그릴 수 있다.
en/compact
BEFORE It can be used to paint walls, door frames, window frames and pillars, as well as some doors, chairs, crates and tables. It can be used to paint signs on walls.
AFTER It can be used to paint walls or furniture, for example, and paint signs on walls.
en/expanded
BEFORE It can be used to paint walls, door frames, window frames and pillars, as well as some doors, chairs, crates and tables.
It can be used to paint signs on walls.
AFTER It can be used to paint the following targets.
- Walls
- Door frames
- Window frames
- Pillars
- Some doors
- Some chairs
- Some crates
- Some tables
It can be used to paint signs on walls.
Base.PaintOrange
ko/compact
BEFORE 벽, 문틀, 창틀, 기둥과 일부 문, 의자, 상자, 탁자를 칠할 수 있다. 벽에 표식을 그릴 수 있다.
AFTER 벽이나 가구 등을 칠하고, 벽에 표식을 그릴 수 있다.
ko/expanded
BEFORE 벽, 문틀, 창틀, 기둥과 일부 문, 의자, 상자, 탁자를 칠할 수 있다.
벽에 표식을 그릴 수 있다.
AFTER 다음 대상을 칠할 수 있다.
- 벽
- 문틀
- 창틀
- 기둥
- 일부 문
- 일부 의자
- 일부 상자
- 일부 탁자
벽에 표식을 그릴 수 있다.
en/compact
BEFORE It can be used to paint walls, door frames, window frames and pillars, as well as some doors, chairs, crates and tables. It can be used to paint signs on walls.
AFTER It can be used to paint walls or furniture, for example, and paint signs on walls.
en/expanded
BEFORE It can be used to paint walls, door frames, window frames and pillars, as well as some doors, chairs, crates and tables.
It can be used to paint signs on walls.
AFTER It can be used to paint the following targets.
- Walls
- Door frames
- Window frames
- Pillars
- Some doors
- Some chairs
- Some crates
- Some tables
It can be used to paint signs on walls.
Base.PaintPink
ko/compact
BEFORE 벽, 문틀, 창틀, 기둥과 일부 문, 의자, 상자, 탁자를 칠할 수 있다. 벽에 표식을 그릴 수 있다.
AFTER 벽이나 가구 등을 칠하고, 벽에 표식을 그릴 수 있다.
ko/expanded
BEFORE 벽, 문틀, 창틀, 기둥과 일부 문, 의자, 상자, 탁자를 칠할 수 있다.
벽에 표식을 그릴 수 있다.
AFTER 다음 대상을 칠할 수 있다.
- 벽
- 문틀
- 창틀
- 기둥
- 일부 문
- 일부 의자
- 일부 상자
- 일부 탁자
벽에 표식을 그릴 수 있다.
en/compact
BEFORE It can be used to paint walls, door frames, window frames and pillars, as well as some doors, chairs, crates and tables. It can be used to paint signs on walls.
AFTER It can be used to paint walls or furniture, for example, and paint signs on walls.
en/expanded
BEFORE It can be used to paint walls, door frames, window frames and pillars, as well as some doors, chairs, crates and tables.
It can be used to paint signs on walls.
AFTER It can be used to paint the following targets.
- Walls
- Door frames
- Window frames
- Pillars
- Some doors
- Some chairs
- Some crates
- Some tables
It can be used to paint signs on walls.
Base.PaintPurple
ko/compact
BEFORE 벽, 문틀, 창틀, 기둥과 일부 문, 의자, 상자, 탁자를 칠할 수 있다. 벽에 표식을 그릴 수 있다.
AFTER 벽이나 가구 등을 칠하고, 벽에 표식을 그릴 수 있다.
ko/expanded
BEFORE 벽, 문틀, 창틀, 기둥과 일부 문, 의자, 상자, 탁자를 칠할 수 있다.
벽에 표식을 그릴 수 있다.
AFTER 다음 대상을 칠할 수 있다.
- 벽
- 문틀
- 창틀
- 기둥
- 일부 문
- 일부 의자
- 일부 상자
- 일부 탁자
벽에 표식을 그릴 수 있다.
en/compact
BEFORE It can be used to paint walls, door frames, window frames and pillars, as well as some doors, chairs, crates and tables. It can be used to paint signs on walls.
AFTER It can be used to paint walls or furniture, for example, and paint signs on walls.
en/expanded
BEFORE It can be used to paint walls, door frames, window frames and pillars, as well as some doors, chairs, crates and tables.
It can be used to paint signs on walls.
AFTER It can be used to paint the following targets.
- Walls
- Door frames
- Window frames
- Pillars
- Some doors
- Some chairs
- Some crates
- Some tables
It can be used to paint signs on walls.
Base.PaintRed
ko/compact
BEFORE 벽, 문틀, 창틀, 기둥과 일부 문, 의자, 상자, 탁자를 칠할 수 있다. 벽에 표식을 그릴 수 있다.
AFTER 벽이나 가구 등을 칠하고, 벽에 표식을 그릴 수 있다.
ko/expanded
BEFORE 벽, 문틀, 창틀, 기둥과 일부 문, 의자, 상자, 탁자를 칠할 수 있다.
벽에 표식을 그릴 수 있다.
AFTER 다음 대상을 칠할 수 있다.
- 벽
- 문틀
- 창틀
- 기둥
- 일부 문
- 일부 의자
- 일부 상자
- 일부 탁자
벽에 표식을 그릴 수 있다.
en/compact
BEFORE It can be used to paint walls, door frames, window frames and pillars, as well as some doors, chairs, crates and tables. It can be used to paint signs on walls.
AFTER It can be used to paint walls or furniture, for example, and paint signs on walls.
en/expanded
BEFORE It can be used to paint walls, door frames, window frames and pillars, as well as some doors, chairs, crates and tables.
It can be used to paint signs on walls.
AFTER It can be used to paint the following targets.
- Walls
- Door frames
- Window frames
- Pillars
- Some doors
- Some chairs
- Some crates
- Some tables
It can be used to paint signs on walls.
Base.PaintTurquoise
ko/compact
BEFORE 벽, 문틀, 창틀, 기둥과 일부 문, 의자, 상자, 탁자를 칠할 수 있다. 벽에 표식을 그릴 수 있다.
AFTER 벽이나 가구 등을 칠하고, 벽에 표식을 그릴 수 있다.
ko/expanded
BEFORE 벽, 문틀, 창틀, 기둥과 일부 문, 의자, 상자, 탁자를 칠할 수 있다.
벽에 표식을 그릴 수 있다.
AFTER 다음 대상을 칠할 수 있다.
- 벽
- 문틀
- 창틀
- 기둥
- 일부 문
- 일부 의자
- 일부 상자
- 일부 탁자
벽에 표식을 그릴 수 있다.
en/compact
BEFORE It can be used to paint walls, door frames, window frames and pillars, as well as some doors, chairs, crates and tables. It can be used to paint signs on walls.
AFTER It can be used to paint walls or furniture, for example, and paint signs on walls.
en/expanded
BEFORE It can be used to paint walls, door frames, window frames and pillars, as well as some doors, chairs, crates and tables.
It can be used to paint signs on walls.
AFTER It can be used to paint the following targets.
- Walls
- Door frames
- Window frames
- Pillars
- Some doors
- Some chairs
- Some crates
- Some tables
It can be used to paint signs on walls.
Base.PaintWhite
ko/compact
BEFORE 벽, 문틀, 창틀, 기둥과 일부 문, 의자, 상자, 탁자를 칠할 수 있다. 벽에 표식을 그릴 수 있다.
AFTER 벽이나 가구 등을 칠하고, 벽에 표식을 그릴 수 있다.
ko/expanded
BEFORE 벽, 문틀, 창틀, 기둥과 일부 문, 의자, 상자, 탁자를 칠할 수 있다.
벽에 표식을 그릴 수 있다.
AFTER 다음 대상을 칠할 수 있다.
- 벽
- 문틀
- 창틀
- 기둥
- 일부 문
- 일부 의자
- 일부 상자
- 일부 탁자
벽에 표식을 그릴 수 있다.
en/compact
BEFORE It can be used to paint walls, door frames, window frames and pillars, as well as some doors, chairs, crates and tables. It can be used to paint signs on walls.
AFTER It can be used to paint walls or furniture, for example, and paint signs on walls.
en/expanded
BEFORE It can be used to paint walls, door frames, window frames and pillars, as well as some doors, chairs, crates and tables.
It can be used to paint signs on walls.
AFTER It can be used to paint the following targets.
- Walls
- Door frames
- Window frames
- Pillars
- Some doors
- Some chairs
- Some crates
- Some tables
It can be used to paint signs on walls.
Base.PaintYellow
ko/compact
BEFORE 벽, 문틀, 창틀, 기둥과 일부 문, 의자, 상자, 탁자를 칠할 수 있다. 벽에 표식을 그릴 수 있다.
AFTER 벽이나 가구 등을 칠하고, 벽에 표식을 그릴 수 있다.
ko/expanded
BEFORE 벽, 문틀, 창틀, 기둥과 일부 문, 의자, 상자, 탁자를 칠할 수 있다.
벽에 표식을 그릴 수 있다.
AFTER 다음 대상을 칠할 수 있다.
- 벽
- 문틀
- 창틀
- 기둥
- 일부 문
- 일부 의자
- 일부 상자
- 일부 탁자
벽에 표식을 그릴 수 있다.
en/compact
BEFORE It can be used to paint walls, door frames, window frames and pillars, as well as some doors, chairs, crates and tables. It can be used to paint signs on walls.
AFTER It can be used to paint walls or furniture, for example, and paint signs on walls.
en/expanded
BEFORE It can be used to paint walls, door frames, window frames and pillars, as well as some doors, chairs, crates and tables.
It can be used to paint signs on walls.
AFTER It can be used to paint the following targets.
- Walls
- Door frames
- Window frames
- Pillars
- Some doors
- Some chairs
- Some crates
- Some tables
It can be used to paint signs on walls.
Base.Paintbrush
ko/compact
BEFORE 벽, 문틀, 창틀, 기둥과 일부 문, 의자, 상자, 탁자를 칠할 수 있다. 벽에 표식을 그릴 수 있다.
AFTER 벽이나 가구 등을 칠하고, 벽에 표식을 그릴 수 있다.
ko/expanded
BEFORE 벽, 문틀, 창틀, 기둥과 일부 문, 의자, 상자, 탁자를 칠할 수 있다.
벽에 표식을 그릴 수 있다.
AFTER 다음 대상을 칠할 수 있다.
- 벽
- 문틀
- 창틀
- 기둥
- 일부 문
- 일부 의자
- 일부 상자
- 일부 탁자
벽에 표식을 그릴 수 있다.
en/compact
BEFORE It can be used to paint walls, door frames, window frames and pillars, as well as some doors, chairs, crates and tables. It can be used to paint signs on walls.
AFTER It can be used to paint walls or furniture, for example, and paint signs on walls.
en/expanded
BEFORE It can be used to paint walls, door frames, window frames and pillars, as well as some doors, chairs, crates and tables.
It can be used to paint signs on walls.
AFTER It can be used to paint the following targets.
- Walls
- Door frames
- Window frames
- Pillars
- Some doors
- Some chairs
- Some crates
- Some tables
It can be used to paint signs on walls.
Base.Pistol
ko/compact
BEFORE 총기를 수리하는 재료로 쓸 수 있다. 탄약을 장전해 사격할 수 있다.
AFTER 총기를 수리하는 재료로 쓸 수 있다. 탄약을 장전해 사격할 수 있다.
ko/expanded
BEFORE 총기를 수리하는 재료로 쓸 수 있다.
탄약을 장전해 사격할 수 있다.
AFTER M9 권총을 수리할 때 재료로 쓸 수 있다.
탄약을 장전해 사격할 수 있다.
en/compact
BEFORE It can be used as repair material for firearms. It can be loaded with ammunition for shooting.
AFTER It can be used as repair material for firearms. It can be loaded with ammunition for shooting.
en/expanded
BEFORE It can be used as repair material for firearms.
It can be loaded with ammunition for shooting.
AFTER It can be used as repair material for the M9 Pistol.
It can be loaded with ammunition for shooting.
Base.Pistol2
ko/compact
BEFORE 총기를 수리하는 재료로 쓸 수 있다. 탄약을 장전해 사격할 수 있다.
AFTER 총기를 수리하는 재료로 쓸 수 있다. 탄약을 장전해 사격할 수 있다.
ko/expanded
BEFORE 총기를 수리하는 재료로 쓸 수 있다.
탄약을 장전해 사격할 수 있다.
AFTER M1911 권총을 수리할 때 재료로 쓸 수 있다.
탄약을 장전해 사격할 수 있다.
en/compact
BEFORE It can be used as repair material for firearms. It can be loaded with ammunition for shooting.
AFTER It can be used as repair material for firearms. It can be loaded with ammunition for shooting.
en/expanded
BEFORE It can be used as repair material for firearms.
It can be loaded with ammunition for shooting.
AFTER It can be used as repair material for the M1911 Pistol.
It can be loaded with ammunition for shooting.
Base.Pistol3
ko/compact
BEFORE 총기를 수리하는 재료로 쓸 수 있다. 탄약을 장전해 사격할 수 있다.
AFTER 총기를 수리하는 재료로 쓸 수 있다. 탄약을 장전해 사격할 수 있다.
ko/expanded
BEFORE 총기를 수리하는 재료로 쓸 수 있다.
탄약을 장전해 사격할 수 있다.
AFTER D-E 권총을 수리할 때 재료로 쓸 수 있다.
탄약을 장전해 사격할 수 있다.
en/compact
BEFORE It can be used as repair material for firearms. It can be loaded with ammunition for shooting.
AFTER It can be used as repair material for firearms. It can be loaded with ammunition for shooting.
en/expanded
BEFORE It can be used as repair material for firearms.
It can be loaded with ammunition for shooting.
AFTER It can be used as repair material for the D-E Pistol.
It can be loaded with ammunition for shooting.
Base.Revolver
ko/compact
BEFORE 총기를 수리하는 재료로 쓸 수 있다. 탄약을 장전해 사격할 수 있다.
AFTER 총기를 수리하는 재료로 쓸 수 있다. 탄약을 장전해 사격할 수 있다.
ko/expanded
BEFORE 총기를 수리하는 재료로 쓸 수 있다.
탄약을 장전해 사격할 수 있다.
AFTER M625 리볼버를 수리할 때 재료로 쓸 수 있다.
탄약을 장전해 사격할 수 있다.
en/compact
BEFORE It can be used as repair material for firearms. It can be loaded with ammunition for shooting.
AFTER It can be used as repair material for firearms. It can be loaded with ammunition for shooting.
en/expanded
BEFORE It can be used as repair material for firearms.
It can be loaded with ammunition for shooting.
AFTER It can be used as repair material for the M625 Revolver.
It can be loaded with ammunition for shooting.
Base.Revolver_Long
ko/compact
BEFORE 총기를 수리하는 재료로 쓸 수 있다. 탄약을 장전해 사격할 수 있다.
AFTER 총기를 수리하는 재료로 쓸 수 있다. 탄약을 장전해 사격할 수 있다.
ko/expanded
BEFORE 총기를 수리하는 재료로 쓸 수 있다.
탄약을 장전해 사격할 수 있다.
AFTER 매그넘을 수리할 때 재료로 쓸 수 있다.
탄약을 장전해 사격할 수 있다.
en/compact
BEFORE It can be used as repair material for firearms. It can be loaded with ammunition for shooting.
AFTER It can be used as repair material for firearms. It can be loaded with ammunition for shooting.
en/expanded
BEFORE It can be used as repair material for firearms.
It can be loaded with ammunition for shooting.
AFTER It can be used as repair material for the Magnum.
It can be loaded with ammunition for shooting.
Base.Revolver_Short
ko/compact
BEFORE 총기를 수리하는 재료로 쓸 수 있다. 탄약을 장전해 사격할 수 있다.
AFTER 총기를 수리하는 재료로 쓸 수 있다. 탄약을 장전해 사격할 수 있다.
ko/expanded
BEFORE 총기를 수리하는 재료로 쓸 수 있다.
탄약을 장전해 사격할 수 있다.
AFTER M36 리볼버를 수리할 때 재료로 쓸 수 있다.
탄약을 장전해 사격할 수 있다.
en/compact
BEFORE It can be used as repair material for firearms. It can be loaded with ammunition for shooting.
AFTER It can be used as repair material for firearms. It can be loaded with ammunition for shooting.
en/expanded
BEFORE It can be used as repair material for firearms.
It can be loaded with ammunition for shooting.
AFTER It can be used as repair material for the M36 Revolver.
It can be loaded with ammunition for shooting.
Base.Scotchtape
ko/compact
BEFORE 무기를 수리하는 재료로 쓸 수 있다.
AFTER 무기를 수리하는 재료로 쓸 수 있다.
ko/expanded
BEFORE 무기를 수리하는 재료로 쓸 수 있다.
AFTER 호환되는 다음 물품을 수리할 때 재료로 쓸 수 있다.
- 도끼
- 배드민턴 라켓
- 둥근머리 망치
- 밴조
- 야구 방망이
- 못 박은 야구 방망이
- 빗자루
- 카누용 노
- 카누용 이중 노
- 클럽 해머
- 쇠스랑
- 괭이
- 골프클럽
- 번철 팬
- 어쿠스틱 기타
- 전기 베이스 (검은색)
- 전기 베이스 (파란색)
- 전기 베이스 (빨간색)
- 전기 기타 (검은색)
- 전기 기타 (파란색)
- 전기 기타 (빨간색)
- 망치
- 손도끼
- 손갈퀴
- 손낫
- 하키 스틱
- 사냥용 칼
- 아이스하키 스틱
- 부엌칼
- 마체테
- 프라이팬
- 곡괭이
- 밀대
- 색소폰
- 삽
- 대형 망치
- 눈 삽
- 창 (빵칼)
- 창 (버터칼)
- 제작한 창
- 창 (손갈퀴)
- 창 (사냥용 칼)
- 창 (얼음 송곳)
- 창 (부엌칼)
- 창 (편지 칼)
- 창 (마체테)
- 창 (메스)
- 창 (가위)
- 창 (드라이버)
- 창 (숟가락)
- 테니스 라켓
- 트럼펫
- 바이올린
- 벌목 도끼
- 나무 망치
en/compact
BEFORE It can be used as repair material for weapons.
AFTER It can be used as repair material for weapons.
en/expanded
BEFORE It can be used as repair material for weapons.
AFTER It can be used as repair material for compatible items from the following list.
- Axe
- Badminton Racket
- Ball Peen Hammer
- Banjo
- Baseball Bat
- Spiked Baseball Bat
- Broom
- Canoe Paddle
- Canoe Paddle Double
- Club Hammer
- Garden Fork
- Garden Hoe
- Golfclub
- Griddle Pan
- Acoustic Guitar
- Black Electric Bass
- Blue Electric Bass
- Red Electric Bass
- Black Electric Guitar
- Blue Electric Guitar
- Red Electric Guitar
- Hammer
- Hand Axe
- Hand Fork
- Hand Scythe
- Hockey Stick
- Hunting Knife
- Ice Hockey Stick
- Kitchen Knife
- Machete
- Frying Pan
- PickAxe
- Rolling Pin
- Saxophone
- Shovel
- Sledgehammer
- Snow Shovel
- Spear With Bread Knife
- Spear With Butter Knife
- Crafted Spear
- Spear With Hand Fork
- Spear With Hunting Knife
- Spear With Ice Pick
- Spear With Knife
- Spear With Letter Opener
- Spear With Machete
- Spear With Scalpel
- Spear With Scissors
- Spear With Screwdriver
- Spear With Spoon
- Tennis Racket
- Trumpet
- Violin
- Wood Axe
- Wooden Mallet
Base.SheetMetal
ko/compact
BEFORE 금속 부품 용접, 건축 및 호환 차량 부품 수리에 재료로 쓸 수 있다.
AFTER 금속 부품 용접, 건축 및 호환 차량 부품 수리에 재료로 쓸 수 있다.
ko/expanded
BEFORE 용접 건축 재료로 쓸 수 있다. 문과 창문의 금속 바리케이드에도 재료로 쓸 수 있다.
금속 부품을 용접할 때 재료로 쓸 수 있다.
호환 차량 부품을 수리하는 재료로 쓸 수 있다.
AFTER 용접 건축 재료로 쓸 수 있다. 문과 창문의 금속 바리케이드에도 재료로 쓸 수 있다.
금속 부품을 용접할 때 재료로 쓸 수 있다.
호환되는 다음 물품을 수리할 때 재료로 쓸 수 있다.
- 대형 연료탱크
- 대형 트렁크
- 차량 후드
- 차량 앞문
- 중형 연료탱크
- 중형 트렁크
- 차량 뒷문
- 차량 이중 뒷문
- 소형 연료탱크
- 소형 트렁크
- 트레일러 트렁크
- 차량 트렁크 후드
en/compact
BEFORE It can supply material for metal-part welding and construction and repairing compatible vehicle parts.
AFTER It can supply material for metal-part welding and construction and repairing compatible vehicle parts.
en/expanded
BEFORE It can be used as material for welded construction. It can also supply window and door barricades.
It can be used as a material for metal-part welding.
It can be used as repair material for compatible vehicle parts.
AFTER It can be used as material for welded construction. It can also supply window and door barricades.
It can be used as a material for metal-part welding.
It can be used as repair material for compatible items from the following list.
- Big Gas Tank
- Big Trunk
- Hood
- Front Door
- Standard Gas Tank
- Standard Trunk
- Rear Door
- Double Rear Door
- Small Gas Tank
- Small Trunk
- Trailer Trunk
- Trunk Lid
Base.Shotgun
ko/compact
BEFORE 총기를 수리하는 재료로 쓸 수 있다. 탄약을 장전해 사격할 수 있다. 총신을 짧게 개조할 수 있다.
AFTER 총기를 수리하는 재료로 쓸 수 있다. 탄약을 장전해 사격할 수 있다. 총신을 짧게 개조할 수 있다.
ko/expanded
BEFORE 총기를 수리하는 재료로 쓸 수 있다.
탄약을 장전해 사격할 수 있다.
총신을 짧게 개조할 수 있다.
AFTER JS-2000 산탄총 및 JS-2000 산탄총 (총열 자름)을 수리할 때 재료로 쓸 수 있다.
탄약을 장전해 사격할 수 있다.
총신을 짧게 개조할 수 있다.
en/compact
BEFORE It can be used as repair material for firearms. It can be loaded with ammunition for shooting. Its shotgun barrel can be shortened.
AFTER It can be used as repair material for firearms. It can be loaded with ammunition for shooting. Its shotgun barrel can be shortened.
en/expanded
BEFORE It can be used as repair material for firearms.
It can be loaded with ammunition for shooting.
Its shotgun barrel can be shortened.
AFTER It can be used as repair material for the JS-2000 Shotgun and the Sawn Off JS-2000 Shotgun.
It can be loaded with ammunition for shooting.
Its shotgun barrel can be shortened.
Base.ShotgunSawnoff
ko/compact
BEFORE 총기를 수리하는 재료로 쓸 수 있다. 탄약을 장전해 사격할 수 있다.
AFTER 총기를 수리하는 재료로 쓸 수 있다. 탄약을 장전해 사격할 수 있다.
ko/expanded
BEFORE 총기를 수리하는 재료로 쓸 수 있다.
탄약을 장전해 사격할 수 있다.
AFTER JS-2000 산탄총 및 JS-2000 산탄총 (총열 자름)을 수리할 때 재료로 쓸 수 있다.
탄약을 장전해 사격할 수 있다.
en/compact
BEFORE It can be used as repair material for firearms. It can be loaded with ammunition for shooting.
AFTER It can be used as repair material for firearms. It can be loaded with ammunition for shooting.
en/expanded
BEFORE It can be used as repair material for firearms.
It can be loaded with ammunition for shooting.
AFTER It can be used as repair material for the JS-2000 Shotgun and the Sawn Off JS-2000 Shotgun.
It can be loaded with ammunition for shooting.
Base.SmallSheetMetal
ko/compact
BEFORE 금속 부품 용접, 용접 건축 및 호환 차량 부품 수리에 재료로 쓸 수 있다.
AFTER 금속 부품 용접, 용접 건축 및 호환 차량 부품 수리에 재료로 쓸 수 있다.
ko/expanded
BEFORE 용접 건축 재료로 쓸 수 있다.
금속 부품을 용접할 때 재료로 쓸 수 있다.
호환 차량 부품을 수리하는 재료로 쓸 수 있다.
AFTER 용접 건축 재료로 쓸 수 있다.
금속 부품을 용접할 때 재료로 쓸 수 있다.
호환되는 다음 물품을 수리할 때 재료로 쓸 수 있다.
- 대형 연료탱크
- 대형 트렁크
- 차량 후드
- 차량 앞문
- 중형 연료탱크
- 중형 트렁크
- 차량 뒷문
- 차량 이중 뒷문
- 소형 연료탱크
- 소형 트렁크
- 트레일러 트렁크
- 차량 트렁크 후드
en/compact
BEFORE It can supply material for metal-part welding and construction and repairing compatible vehicle parts.
AFTER It can supply material for metal-part welding and construction and repairing compatible vehicle parts.
en/expanded
BEFORE It can be used as material for welded construction.
It can be used as a material for metal-part welding.
It can be used as repair material for compatible vehicle parts.
AFTER It can be used as material for welded construction.
It can be used as a material for metal-part welding.
It can be used as repair material for compatible items from the following list.
- Big Gas Tank
- Big Trunk
- Hood
- Front Door
- Standard Gas Tank
- Standard Trunk
- Rear Door
- Double Rear Door
- Small Gas Tank
- Small Trunk
- Trailer Trunk
- Trunk Lid
Base.VarmintRifle
ko/compact
BEFORE 총기를 수리하는 재료로 쓸 수 있다. 탄약을 장전해 사격할 수 있다.
AFTER 총기를 수리하는 재료로 쓸 수 있다. 탄약을 장전해 사격할 수 있다.
ko/expanded
BEFORE 총기를 수리하는 재료로 쓸 수 있다.
탄약을 장전해 사격할 수 있다.
AFTER 수렵총을 수리할 때 재료로 쓸 수 있다.
탄약을 장전해 사격할 수 있다.
en/compact
BEFORE It can be used as repair material for firearms. It can be loaded with ammunition for shooting.
AFTER It can be used as repair material for firearms. It can be loaded with ammunition for shooting.
en/expanded
BEFORE It can be used as repair material for firearms.
It can be loaded with ammunition for shooting.
AFTER It can be used as repair material for the MSR700 Rifle.
It can be loaded with ammunition for shooting.
Base.Woodglue
ko/compact
BEFORE 무기를 수리하는 재료로 쓸 수 있다.
AFTER 무기를 수리하는 재료로 쓸 수 있다.
ko/expanded
BEFORE 무기를 수리하는 재료로 쓸 수 있다.
AFTER 호환되는 다음 물품을 수리할 때 재료로 쓸 수 있다.
- 도끼
- 야구 방망이
- 못 박은 야구 방망이
- 빗자루
- 카누용 노
- 카누용 이중 노
- 클럽 해머
- 쇠스랑
- 괭이
- 망치
- 손도끼
- 손낫
- 하키 스틱
- 아이스하키 스틱
- 곡괭이
- 밀대
- 삽
- 대형 망치
- 눈 삽
- 창 (빵칼)
- 창 (버터칼)
- 제작한 창
- 창 (손갈퀴)
- 창 (사냥용 칼)
- 창 (얼음 송곳)
- 창 (부엌칼)
- 창 (편지 칼)
- 창 (마체테)
- 창 (메스)
- 창 (가위)
- 창 (드라이버)
- 창 (숟가락)
- 벌목 도끼
- 나무 망치
en/compact
BEFORE It can be used as repair material for weapons.
AFTER It can be used as repair material for weapons.
en/expanded
BEFORE It can be used as repair material for weapons.
AFTER It can be used as repair material for compatible items from the following list.
- Axe
- Baseball Bat
- Spiked Baseball Bat
- Broom
- Canoe Paddle
- Canoe Paddle Double
- Club Hammer
- Garden Fork
- Garden Hoe
- Hammer
- Hand Axe
- Hand Scythe
- Hockey Stick
- Ice Hockey Stick
- PickAxe
- Rolling Pin
- Shovel
- Sledgehammer
- Snow Shovel
- Spear With Bread Knife
- Spear With Butter Knife
- Crafted Spear
- Spear With Hand Fork
- Spear With Hunting Knife
- Spear With Ice Pick
- Spear With Knife
- Spear With Letter Opener
- Spear With Machete
- Spear With Scalpel
- Spear With Scissors
- Spear With Screwdriver
- Spear With Spoon
- Wood Axe
- Wooden Mallet
```


## 2026-09-14 긴 수리 대상 목록의 범주별 접기·펼치기

사용자가 승인한 긴 대상 목록의 접기·펼치기를 실제 Browser와 Wiki의 Expanded 소비 경로에 구현했다. 대상을 삭제하거나 범주명으로 바꾸지 않고 관심 있는 그룹만 펼쳐 실제 이름을 읽게 한다. Compact와 전체 Expanded 원문은 수락본32872f22의 **8,420문자열 모두 동일**하다. 전체2,105개 재생성 후 긴 수리목록6개×KO/EN=12표면에 표시용 구조만 추가했다.

### 적용 범위와 분류 근거

대상은 기존 compatibility_choices 관계로 목록화된 수리 재료6개다. 개별 아이템 분기 없이 repair_targets의 채택된 속성을 공통 규칙으로 분류한다. VehicleMaintenance/Instrument/Sports/Gardening 표시 범주와 DigPlow 태그, Spear/Axe/SmallBlade/LongBlade/Blunt/SmallBlunt 전투 분류를 사용한다. 이름에서 색상·기능·호환성을 추정하지 않는다. 원예 범주 또는 경작 태그를 전투 분류보다 우선한다. 모호하거나 같은 번역명이 상충된 범주에 걸리면 ‘그 밖의 대상’ 그룹으로 남기는 경로가 있다.

초기 분류 전문을 읽다가 쇠스랑이 창, 손갈퀴가 칼 아래에 놓이는 것을 발견해 이 범위 전체를 교정했다. 최종본은 쇠스랑·손갈퀴를 원예 도구에 배치하고, 손낫 등이 포함되는 작은 칼날 분류의 명칭은 ‘칼날 도구’로 표현한다. 색상별 악기는 실제 Instrument 속성으로 같은 악기 그룹, 부착물별 창은 실제 Spear 속성으로 같은 창 그룹에 넣되 모든 이름을 유지한다. 색상/부착물의 중첩 트리를 새로 만들지 않는다.

| 항목 | KO 표시명 수 | 대상 ID 수 | 기본 접힌 그룹 수 |
|---|---:|---:|---:|
| Base.DuctTape | 59 | 66 | 8 |
| Base.Glue | 43 | 50 | 7 |
| Base.Scotchtape | 55 | 57 | 7 |
| Base.SheetMetal | 12 | 37 | 1 |
| Base.SmallSheetMetal | 12 | 37 | 1 |
| Base.Woodglue | 34 | 36 | 6 |

같은 이름을 사용하는 차량 등급 등은 기존 표시명 중복 제거를 그대로 유지한다. 각 표시 항목에 해당하는 원본 item_ids를 함께 직렬화하며 그룹들을 펼친 ID 집합이 기존 대상 집합과 정확히 같고 각 ID는 한 번만 존재한다. KO의 Leaf Rake/Rake가 모두 ‘갈퀴’로 번역되는 경우처럼 KO/EN 표시명 수가 다를 수 있으나 원본 ID 집합은 같다. 헤더 수는 실제 펼쳐 보이는 표시명 수다.

짧은 페인트 목록16개, 학습 목록25개/82내용, 소독 문장, 단일·동종 총기 수리14개는 접기 대상에 넣지 않았다. 기존 일반 recipe 관계225개를 새 호환 목록으로 전환하지 않았다. 가구/총기 부착물의 알 수 없는 전수 대상이나 새 기능은 추정하지 않았다.

### 사용자가 보는 모습

접착 테이프 기본 접힘 상태의 실제 KO 구성은 다음과 같다. ‘목록:’은 해당 범주 전체가 호환된다는 의미가 아니라 아래 목록에 포함된 대상 묶음임을 나타낸다. +/- 버튼의 행 전체가 클릭 영역이며 제목이 길면 버튼 높이와 제목 줄바꿈을 함께 조정한다.

```text
• 창에 부착물을 다는 재료로 쓸 수 있다.
• 장치에 움직임 감지, 시간 지연, 원격 작동 기능을 더하는 재료로 쓸 수 있다.
• 호환되는 다음 물품을 수리할 때 재료로 쓸 수 있다.
  [+] 목록: 차량 부품 (2)
  [+] 목록: 악기 (11)
  [+] 목록: 스포츠 용품 (9)
  [+] 목록: 원예 도구 (7)
  [+] 목록: 창 (13)
  [+] 목록: 도끼 (3)
  [+] 목록: 칼날 도구 (4)
  [+] 목록: 둔기와 도구 (10)
```

원예 그룹만 펼치면 다른 그룹은 접힌 채 다음 이름들이 나타난다.

```text
[-] 목록: 원예 도구 (7)
  - 쇠스랑
  - 괭이
  - 손갈퀴
  - 갈퀴
  - 곡괭이
  - 삽
  - 눈 삽
```

악기 그룹은 밴조·어쿠스틱 기타·색상별 전기 베이스/기타·색소폰·트럼펫·바이올린의11개 이름을 모두 보여준다. 창 그룹은 제작한 창과 부착물별 창13개를 모두 보여준다. 단일 그룹인 금속판도 ‘목록: 차량 부품 (12)’를 펼쳐 실제 부품명을 확인한다.

### 실제 메뉴 연결과 상태

- Python 생성기는 원문 segment와 별도로 target_groups(개요, 범주 키/명, 표시 항목, 대상 IDs, 표시 수)를 만든다. Expanded projection은 해당 독립 용도의 unit에만 이를 전달한다. 원문은 완전한 평면 목록으로 계속 보존된다.
- IrisLayer3DataLookup은 선택적 그룹 구조를 로드 시 검증한다. 헤더/항목 배열·수, 원문 목록과 표시명의 중복·누락, 대상ID 중복·빈 배열이 잘못되면 데이터를 거부한다. 전체 대상ID 집합과 원천 관계의 일치는 생성 계약과 별도 전수 대조에서 검증한다. 기존 그룹 없는 산출물도 일반 텍스트로 표시한다.
- DetailModelAssembler는 그룹과 항목까지 읽기 전용 뷰로 전달한다. Browser/Wiki의 기존 getLayer3Units 문자열 API는 그대로 두고 구조를 읽는 getLayer3Records 경로를 추가했다.
- 새 IrisTargetGroupView를 두 메뉴가 공유한다. 표준 ISButton을 사용하고 클릭 행의 가로폭/최소26픽셀 높이와 줄바꿈 제목을 함께 구성한다. 내부 분류 키나 데이터 용어는 사용자에게 표시하지 않는다.
- Browser는 현재 아이템/언어/제품 revision의 상태만 보관한다. 같은 항목에서 그룹을 토글하거나 다른 영역을 다시 그릴 때 상태를 유지하며, 아이템 또는 언어 변경 시 접힘과 스크롤0으로 초기화한다. 토글 후 기존 detail 위치/스크롤 계산을 다시 적용하고 최대 범위를 넘지 않도록 제한한다.
- Wiki는 바깥 패널/닫기 버튼을 유지한 채 본문을 다시 그린다. 스크롤바 자식은 보존하고 실제 본문 높이 및 스크롤 범위를 갱신한다. 새 Wiki 패널을 열면 기본 접힘이며, 패널 이동과 닫기는 기존 경로를 쓴다.
- 독립 용도 개요는 항상 그룹 밖에 남는다. 학습/페인트 같은 짧은 목록에는 버튼을 생성하지 않는다. 중첩 분류와 ‘전체 펼치기’ 같은 추가 조작은 도입하지 않았다.

### 검토 HTML과 직접 확인

두 정식 검토 HTML에도 동일 그룹·수·이름을 native details/summary로 표시했다. 기본 접힘 상태이고 전체 원문 보기도 함께 제공한다. 정적 HTML에만 적용한 기능이 아니며, 실제 Lua 메뉴 소비 경로에도 위 구조와 버튼이 구현돼 있다.

`.tmp/prose/folds-preview.html`은 같은 렌더링으로 뽑은 접착 테이프 KO/EN 확인 페이지다. 로컬 브라우저에서 실제 접힘 헤더·악기 펼침·재접힘·교정된 원예 그룹 펼침을 클릭하고 화면과 접근성 상태를 읽었다. 원예 그룹의7개 표시명과 독립 용도 문장을 확인했다. 이 HTML 스크린샷은 실제 게임 화면이라고 주장하지 않는다. 임시 검토 탭과 로컬 서버는 종료했다.

### 실행 검증과 남은 한계

- 전체 composition/description 정식 경로 재생성: `uv run --project .\Iris\tooling python .tmp/prose/depth_regenerate.py`, 종료 코드0. 전체2,105, present1,976/absent129/failed0 유지. 원문8,420개 동일.
- 기존 계약2개: **2 passed in33.33s, 종료 코드0**, `.tmp/prose/folds-tests-final.log`. 명령은 `uv run --project .\Iris\tooling python -I -B -m pytest --noconftest -c .\Iris\tooling\pyproject.toml .\Iris\build\description\v2\tests\test_layer3_composition.py::test_layer3_composition_contract .\Iris\build\description\v2\tests\test_layer3_description_composition.py::test_layer3_description_composition --basetemp .\.tmp\folds-tests-02 -q -s --tb=short`.
- Lua 필수 문법: `powershell -ExecutionPolicy Bypass -File .\tools\check_lua_syntax.ps1`, **266 files / 종료 코드0**, `.tmp/prose/folds-lua-accepted.log`.
- 실제 Browser/Wiki 소비 harness: `uv run --project .\Iris\tooling python .tmp/prose/folds_menu_fixture.py`, **종료 코드0**, `.tmp/prose/folds-menu-accepted.log`. 전체4,210언어별상태와 적용6개+페인트/학습/소독 대조3개를 KO/EN으로 확인했다. 기본접힘/한그룹펼침/재접힘/전체그룹펼침, 클릭영역, 가변높이, 모든 이름의 접근 가능성, 목록 시작수, 스크롤경계, 아이템전환초기화, 새Wiki패널상태, 닫기, 읽기전용모델 및 잘못된 그룹데이터 로드거부를 검증한다.
- Browser 기존 상태/검색/전환: `lua Iris/test/lua/browser_state_acceptance_harness.lua .`, 종료 코드0. 기존 상호작용: `lua Iris/test/lua/browser_interaction_density_acceptance_harness.lua .`, 종료 코드0.
- 그룹/ID/표시명 및 HTML 검사: `uv run --project .\Iris\tooling python .tmp/prose/folds-audit.py`, 종료 코드0. 두 HTML 각각60개 그룹이 기본접힘이며 모든 대상ID를 보존. 전체설명 HTML의8,420원문도 대소문자 구분 ID로 입력과 일치.

추가로 실행한 `lua Iris/test/lua/detail_view_model_locale_harness.lua .`의 구형 경로는 종료 코드1이다(`.tmp/prose/folds-model-legacy.log`). 기존 HammerStone 영문에서 고정 단어 ‘construction’을 찾는 assertion에서 중단됐으며, 현재 frozen English lookup 실제 문구는 “A tool used to build wooden structures with nails.”다. 새 그룹 경로와 무관한 구형 문자열 기대를 이번 UI 작업에서 고치거나 구형 데이터를 패키징하지 않았다. 이 검사는 PASS로 합산하지 않는다. 위 Expanded 제품 fixture 경로는 따로 통과했다.

새 harness 작성 중에는 최소 스크롤 높이를 실제 본문 높이로 오인한 assertion과, 검증을 마친 캐시를 재로드 없이 변조해 검사한 가정을 발견했다. 본문 높이를 별도로 확인하고 새 로드 경로에서 손상 데이터를 확인하도록 검증을 수정했다. 실제 표시 분류에서 발견한 쇠스랑/손갈퀴 문제는 제품 공통 규칙을 수정한 뒤 다시 전체 재생성·검수했다.

검증 fixture는 `.tmp/menu/folds-runtime-04/runtime`, 제품ID `l3p-f977d05dcf32a68ef171f4b466aa6cc77f19cd114adf612c9c8a46cfd30d587a`다. 정식 Expanded projection/직렬화/Lookup/모델/Browser/Wiki 코드를 실행하지만 엔진·폰트 위젯은 stub다. 실제 PZ 폰트, 게임 창에서의 클릭/클리핑·스크롤 체감은 아직 별도 확인 대상이다. 메뉴 기능 구현과 자동검사 통과를 실제 게임 검증 또는 전체용도완전성 판정으로 바꾸지 않는다. 패키징·설치·커밋·푸시는 하지 않았다.

### 이번 변경 파일

- `description_composition_uses.py`: 공통 대상 분류 및 표시 그룹.
- `product_projection.py`, `tooltip_s2_supply.py`: 그룹 직렬화와 현재 입력 바인딩.
- `IrisLayer3DataLookup.lua`: 그룹 구조의 로드 검증.
- `IrisItemDetailModelAssembler.lua`, `IrisWikiSections.lua`: 읽기 전용 구조와 호환 문자열/구조 API.
- `IrisTargetGroupView.lua`(신규), `IrisBrowserDetail.lua`, `IrisWikiPanel.lua`: 공유 접기 UI와 높이/상태 처리.
- 기존 description 계약 및 `detail_view_model_locale_harness.lua`: 의미 있는 범위/상호작용 검증 추가.
- 정식 descriptions 및 두 검토 HTML, 두 보고서 갱신. blocks 내용 해시는 이전 수락본과 동일.

### 전체 적용 범위의 KO/EN 그룹과 실제 표시명

#### Base.DuctTape / KO

호환되는 다음 물품을 수리할 때 재료로 쓸 수 있다.

- **차량 부품 (2)**: 글로브 박스, 중형 좌석
- **악기 (11)**: 밴조, 어쿠스틱 기타, 전기 베이스 (검은색), 전기 베이스 (파란색), 전기 베이스 (빨간색), 전기 기타 (검은색), 전기 기타 (파란색), 전기 기타 (빨간색), 색소폰, 트럼펫, 바이올린
- **스포츠 용품 (9)**: 배드민턴 라켓, 야구 방망이, 카누용 노, 카누용 이중 노, 골프클럽, 하키 스틱, 아이스하키 스틱, 라크로스 스틱, 테니스 라켓
- **원예 도구 (7)**: 쇠스랑, 괭이, 손갈퀴, 갈퀴, 곡괭이, 삽, 눈 삽
- **창 (13)**: 창 (빵칼), 창 (버터칼), 제작한 창, 창 (손갈퀴), 창 (사냥용 칼), 창 (얼음 송곳), 창 (부엌칼), 창 (편지 칼), 창 (마체테), 창 (메스), 창 (가위), 창 (드라이버), 창 (숟가락)
- **도끼 (3)**: 도끼, 손도끼, 벌목 도끼
- **칼날 도구 (4)**: 손낫, 사냥용 칼, 부엌칼, 마체테
- **둔기와 도구 (10)**: 둥근머리 망치, 못 박은 야구 방망이, 빗자루, 클럽 해머, 번철 팬, 망치, 프라이팬, 밀대, 대형 망치, 나무 망치

#### Base.DuctTape / EN

It can be used as repair material for compatible items from the following list.

- **Vehicle parts (2)**: Glove Box, Standard Seat
- **Musical instruments (11)**: Banjo, Acoustic Guitar, Black Electric Bass, Blue Electric Bass, Red Electric Bass, Black Electric Guitar, Blue Electric Guitar, Red Electric Guitar, Saxophone, Trumpet, Violin
- **Sports equipment (9)**: Badminton Racket, Baseball Bat, Canoe Paddle, Canoe Paddle Double, Golfclub, Hockey Stick, Ice Hockey Stick, LaCrosse Stick, Tennis Racket
- **Gardening tools (8)**: Garden Fork, Garden Hoe, Hand Fork, Leaf Rake, PickAxe, Rake, Shovel, Snow Shovel
- **Spears (13)**: Spear With Bread Knife, Spear With Butter Knife, Crafted Spear, Spear With Hand Fork, Spear With Hunting Knife, Spear With Ice Pick, Spear With Knife, Spear With Letter Opener, Spear With Machete, Spear With Scalpel, Spear With Scissors, Spear With Screwdriver, Spear With Spoon
- **Axes (3)**: Axe, Hand Axe, Wood Axe
- **Bladed tools (4)**: Hand Scythe, Hunting Knife, Kitchen Knife, Machete
- **Blunt weapons and tools (10)**: Ball Peen Hammer, Spiked Baseball Bat, Broom, Club Hammer, Griddle Pan, Hammer, Frying Pan, Rolling Pin, Sledgehammer, Wooden Mallet

#### Base.Glue / KO

호환되는 다음 물품을 수리할 때 재료로 쓸 수 있다.

- **차량 부품 (2)**: 글로브 박스, 중형 좌석
- **스포츠 용품 (6)**: 야구 방망이, 카누용 노, 카누용 이중 노, 하키 스틱, 아이스하키 스틱, 라크로스 스틱
- **원예 도구 (7)**: 쇠스랑, 괭이, 손갈퀴, 갈퀴, 곡괭이, 삽, 눈 삽
- **창 (13)**: 창 (빵칼), 창 (버터칼), 제작한 창, 창 (손갈퀴), 창 (사냥용 칼), 창 (얼음 송곳), 창 (부엌칼), 창 (편지 칼), 창 (마체테), 창 (메스), 창 (가위), 창 (드라이버), 창 (숟가락)
- **도끼 (3)**: 도끼, 손도끼, 벌목 도끼
- **칼날 도구 (3)**: 손낫, 사냥용 칼, 부엌칼
- **둔기와 도구 (9)**: 못 박은 야구 방망이, 빗자루, 클럽 해머, 번철 팬, 망치, 프라이팬, 밀대, 대형 망치, 나무 망치

#### Base.Glue / EN

It can be used as repair material for compatible items from the following list.

- **Vehicle parts (2)**: Glove Box, Standard Seat
- **Sports equipment (6)**: Baseball Bat, Canoe Paddle, Canoe Paddle Double, Hockey Stick, Ice Hockey Stick, LaCrosse Stick
- **Gardening tools (8)**: Garden Fork, Garden Hoe, Hand Fork, Leaf Rake, PickAxe, Rake, Shovel, Snow Shovel
- **Spears (13)**: Spear With Bread Knife, Spear With Butter Knife, Crafted Spear, Spear With Hand Fork, Spear With Hunting Knife, Spear With Ice Pick, Spear With Knife, Spear With Letter Opener, Spear With Machete, Spear With Scalpel, Spear With Scissors, Spear With Screwdriver, Spear With Spoon
- **Axes (3)**: Axe, Hand Axe, Wood Axe
- **Bladed tools (3)**: Hand Scythe, Hunting Knife, Kitchen Knife
- **Blunt weapons and tools (9)**: Spiked Baseball Bat, Broom, Club Hammer, Griddle Pan, Hammer, Frying Pan, Rolling Pin, Sledgehammer, Wooden Mallet

#### Base.Scotchtape / KO

호환되는 다음 물품을 수리할 때 재료로 쓸 수 있다.

- **악기 (11)**: 밴조, 어쿠스틱 기타, 전기 베이스 (검은색), 전기 베이스 (파란색), 전기 베이스 (빨간색), 전기 기타 (검은색), 전기 기타 (파란색), 전기 기타 (빨간색), 색소폰, 트럼펫, 바이올린
- **스포츠 용품 (8)**: 배드민턴 라켓, 야구 방망이, 카누용 노, 카누용 이중 노, 골프클럽, 하키 스틱, 아이스하키 스틱, 테니스 라켓
- **원예 도구 (6)**: 쇠스랑, 괭이, 손갈퀴, 곡괭이, 삽, 눈 삽
- **창 (13)**: 창 (빵칼), 창 (버터칼), 제작한 창, 창 (손갈퀴), 창 (사냥용 칼), 창 (얼음 송곳), 창 (부엌칼), 창 (편지 칼), 창 (마체테), 창 (메스), 창 (가위), 창 (드라이버), 창 (숟가락)
- **도끼 (3)**: 도끼, 손도끼, 벌목 도끼
- **칼날 도구 (4)**: 손낫, 사냥용 칼, 부엌칼, 마체테
- **둔기와 도구 (10)**: 둥근머리 망치, 못 박은 야구 방망이, 빗자루, 클럽 해머, 번철 팬, 망치, 프라이팬, 밀대, 대형 망치, 나무 망치

#### Base.Scotchtape / EN

It can be used as repair material for compatible items from the following list.

- **Musical instruments (11)**: Banjo, Acoustic Guitar, Black Electric Bass, Blue Electric Bass, Red Electric Bass, Black Electric Guitar, Blue Electric Guitar, Red Electric Guitar, Saxophone, Trumpet, Violin
- **Sports equipment (8)**: Badminton Racket, Baseball Bat, Canoe Paddle, Canoe Paddle Double, Golfclub, Hockey Stick, Ice Hockey Stick, Tennis Racket
- **Gardening tools (6)**: Garden Fork, Garden Hoe, Hand Fork, PickAxe, Shovel, Snow Shovel
- **Spears (13)**: Spear With Bread Knife, Spear With Butter Knife, Crafted Spear, Spear With Hand Fork, Spear With Hunting Knife, Spear With Ice Pick, Spear With Knife, Spear With Letter Opener, Spear With Machete, Spear With Scalpel, Spear With Scissors, Spear With Screwdriver, Spear With Spoon
- **Axes (3)**: Axe, Hand Axe, Wood Axe
- **Bladed tools (4)**: Hand Scythe, Hunting Knife, Kitchen Knife, Machete
- **Blunt weapons and tools (10)**: Ball Peen Hammer, Spiked Baseball Bat, Broom, Club Hammer, Griddle Pan, Hammer, Frying Pan, Rolling Pin, Sledgehammer, Wooden Mallet

#### Base.SheetMetal / KO

호환되는 다음 물품을 수리할 때 재료로 쓸 수 있다.

- **차량 부품 (12)**: 대형 연료탱크, 대형 트렁크, 차량 후드, 차량 앞문, 중형 연료탱크, 중형 트렁크, 차량 뒷문, 차량 이중 뒷문, 소형 연료탱크, 소형 트렁크, 트레일러 트렁크, 차량 트렁크 후드

#### Base.SheetMetal / EN

It can be used as repair material for compatible items from the following list.

- **Vehicle parts (12)**: Big Gas Tank, Big Trunk, Hood, Front Door, Standard Gas Tank, Standard Trunk, Rear Door, Double Rear Door, Small Gas Tank, Small Trunk, Trailer Trunk, Trunk Lid

#### Base.SmallSheetMetal / KO

호환되는 다음 물품을 수리할 때 재료로 쓸 수 있다.

- **차량 부품 (12)**: 대형 연료탱크, 대형 트렁크, 차량 후드, 차량 앞문, 중형 연료탱크, 중형 트렁크, 차량 뒷문, 차량 이중 뒷문, 소형 연료탱크, 소형 트렁크, 트레일러 트렁크, 차량 트렁크 후드

#### Base.SmallSheetMetal / EN

It can be used as repair material for compatible items from the following list.

- **Vehicle parts (12)**: Big Gas Tank, Big Trunk, Hood, Front Door, Standard Gas Tank, Standard Trunk, Rear Door, Double Rear Door, Small Gas Tank, Small Trunk, Trailer Trunk, Trunk Lid

#### Base.Woodglue / KO

호환되는 다음 물품을 수리할 때 재료로 쓸 수 있다.

- **스포츠 용품 (5)**: 야구 방망이, 카누용 노, 카누용 이중 노, 하키 스틱, 아이스하키 스틱
- **원예 도구 (5)**: 쇠스랑, 괭이, 곡괭이, 삽, 눈 삽
- **창 (13)**: 창 (빵칼), 창 (버터칼), 제작한 창, 창 (손갈퀴), 창 (사냥용 칼), 창 (얼음 송곳), 창 (부엌칼), 창 (편지 칼), 창 (마체테), 창 (메스), 창 (가위), 창 (드라이버), 창 (숟가락)
- **도끼 (3)**: 도끼, 손도끼, 벌목 도끼
- **칼날 도구 (1)**: 손낫
- **둔기와 도구 (7)**: 못 박은 야구 방망이, 빗자루, 클럽 해머, 망치, 밀대, 대형 망치, 나무 망치

#### Base.Woodglue / EN

It can be used as repair material for compatible items from the following list.

- **Sports equipment (5)**: Baseball Bat, Canoe Paddle, Canoe Paddle Double, Hockey Stick, Ice Hockey Stick
- **Gardening tools (5)**: Garden Fork, Garden Hoe, PickAxe, Shovel, Snow Shovel
- **Spears (13)**: Spear With Bread Knife, Spear With Butter Knife, Crafted Spear, Spear With Hand Fork, Spear With Hunting Knife, Spear With Ice Pick, Spear With Knife, Spear With Letter Opener, Spear With Machete, Spear With Scalpel, Spear With Scissors, Spear With Screwdriver, Spear With Spoon
- **Axes (3)**: Axe, Hand Axe, Wood Axe
- **Bladed tools (1)**: Hand Scythe
- **Blunt weapons and tools (7)**: Spiked Baseball Bat, Broom, Club Hammer, Hammer, Rolling Pin, Sledgehammer, Wooden Mallet

현재 descriptions SHA-256: `72303dd1eba99ba1f16011d71bd2035d259123a9c804ea63566f5fe42ef9c490`

현재 blocks SHA-256: `ac07107c1d376c59d1b1ce81d73f9b383327b89874e51991d8a28275628f28a2`


## 2026-09-14 legacy 영문 조회 검증의 낡은 기대값 정리

앞 절에 기록한 legacy harness exit1을 감독 요청에 따라 좁게 마무리했다. 제품·영문 조회 코드·번역·생성 데이터를 수정하지 않았다.

원인 확인: `detail_view_model_locale_harness.lua`의 HammerStone 검사는 `construction`이라는 특정 단어를 요구했다. 이 assertion은 HEAD에도 같았다. `IrisLayer3EnglishLookup.lua`와 `Data/Layer3English/Chunk004.lua`에는 이번 diff가 없으며, HEAD와 현재 Chunk004의 HammerStone 원문은 모두 `A tool used to build wooden structures with nails.`였다. 따라서 접기·펼치기로 영문 용도가 사라진 문제가 아니라 이미 다른 표현을 사용하는 frozen 영문과 특정 동의어를 요구하는 기대값의 불일치였다.

최소 수정: 해당 assertion의 검색 구절만 `construction`에서 `build wooden structures with nails`로 바꾸고 이유 주석 한 줄을 추가했다. 실제 lookup 반환값이 있어야 하고 못을 사용하는 목제 구조물 건축 용도가 명시돼야 한다. 기대값을 반환값에서 자동 추출하거나 임의 ASCII 텍스트만 허용하지 않았다. 그 다음의 전체 문자열 ASCII 검사, KO/EN 템플릿 차이와 영문 템플릿 기대값을 그대로 유지했다. 앞선 locale 선택·가용성·레이블 차이·중첩 읽기전용·조회 횟수 검증도 그대로 실행한다. 따라서 영문 선택과 해당 use 의미라는 원래 목적을 약화하지 않았다.

요청한 정확한 명령 `lua Iris/test/lua/detail_view_model_locale_harness.lua .`을 실행해 **종료 코드0**으로 끝까지 통과했다. 후속 assertion 실패는 없었다. 실제 마지막 출력:

```text
IRIS_DETAIL_LOCALE_PASS localized_layer2=true localized_layer3=true availability_equal=true labels_differ=true nested_readonly=true interaction_lookup_once_per_build=true
```

앞 절의 exit1 기록은 수정 전 실행 이력이며, 최종 legacy 검증 상태는 PASS다. 제품/생성 데이터가 바뀌지 않았으므로 전체 재생성이나 패키징은 반복하지 않았다. descriptions SHA `72303dd1eba99ba1f16011d71bd2035d259123a9c804ea63566f5fe42ef9c490`, blocks SHA `ac07107c1d376c59d1b1ce81d73f9b383327b89874e51991d8a28275628f28a2`가 그대로임을 확인했다. 이번 후속 변경은 기존 Lua test의 assertion 한 곳/주석 한 줄 및 보고서뿐이다.


## 2026-09-14 — 범주 접기 적용 범위 전수 재검토: 학습 3개·페인트 16개 추가

기존 6개 수리 목록에만 머물지 않고 전체 2,105개 Expanded 구조화 목록을 다시 조사했다. KO/EN 본문 8,420개는 이전 수락본과 byte-equivalent 문자열이며, 이번 변경은 구조화된 분류와 동일 내용을 여닫는 표시에 한정된다. Compact의 유용한 요약 원칙과 Expanded의 확인된 독립 용도 보존 원칙은 그대로다. Compact에 Expanded 전체 사실을 넣는 동등성 요구를 복원하지 않았다.

### 전체 범위와 적용 판단

전체에서 실제 목록은 47개: 수리 6개, 페인트 16개, 학습 25개다. 기존 수리 6개 metadata는 직전 수락본과 정확히 같다. 학습 중 대장장이 잡지 2·3·4권을 추가했고 페인트 16개도 벽/일부 가구라는 이미 입증된 범위 구분을 그대로 접기로 옮겼다. 최종 25개/50 locale 목록, 148개 범주가 기본 접힘이다. 나머지 학습 22개는 접지 않는다.

학습은 기존에 인정된 `learned_recipes`의 각 원래 recipe key에 연결된 recipe observation의 선언된 Result와 item observation의 DisplayCategory로 분류한다. 입력 재료의 전체 제작 결과를 새 용도로 노출하는 관계가 아니다. callback의 효과를 확장하거나 결과 아이템 이름으로 원래 학습명을 대체하지 않는다. recipe key·source_names·operation·observation refs가 유지된다. 소스 결과가 불명확하거나 선언 범주가 Hidden이면 `Other lessons`로 남기고 이름에서 분류를 추측하지 않는다. 대장장이 3권의 드럼통·삽이 이에 해당한다.

분류 기준은 재료, 생활용품, 조리용품/음식, 응급처치 용품, 도구와 무기, 탄약 관련 물품, 스포츠 용품 등 선언 범주다. 서로 다른 명시 범주에 관련 학습 항목이 각각 여럿 모일 때 접기로 얻는 탐색 이점이 있다고 판단한다. 단일 범주나 서로 무관한 단일 항목들만 있으면 접지 않는다. 문자열 길이나 목록 개수만으로 접기를 켜지 않으며 아이템 ID 예외, 이름 추측, 완성 문장 예외는 없다. 대장장이 1권은 8개라도 모두 조리용품이고 조리 잡지 1권도 동질적 조리법이므로 그대로다.

페인트는 기존 `action_targets`의 `mapped` 벽/`some` 가구 관계를 재사용한다. 헤더와 개별 이름 모두 일부 가구 범위를 보존한다. 가구 종류 전체에 가능하다는 주장을 만들지 않고 가짜 외부 아이템 ID를 만들지 않는다. 벽 표식과 나머지 독립 용도는 접기 밖에 유지한다.

추가 적용 목록:

- 학습: `Base.SmithingMag2`, `Base.SmithingMag3`, `Base.SmithingMag4`
- 페인트: `Base.PaintBlack`, `Base.PaintBlue`, `Base.PaintBrown`, `Base.PaintCyan`, `Base.PaintGreen`, `Base.PaintGrey`, `Base.PaintLightBlue`, `Base.PaintLightBrown`, `Base.PaintOrange`, `Base.PaintPink`, `Base.PaintPurple`, `Base.PaintRed`, `Base.PaintTurquoise`, `Base.PaintWhite`, `Base.PaintYellow`, `Base.Paintbrush`

| 학습 목록 | 항목 수 | 표시 판단 |
|---|---:|---|
| `Base.CookingMag1` | 7 | 단일 범주이므로 원문 목록 유지 |
| `Base.CookingMag2` | 3 | 짧거나 동질적이며 개별 동작을 바로 읽도록 유지 |
| `Base.ElectronicsMag1` | 3 | 짧거나 동질적이며 개별 동작을 바로 읽도록 유지 |
| `Base.ElectronicsMag2` | 2 | 짧거나 동질적이며 개별 동작을 바로 읽도록 유지 |
| `Base.ElectronicsMag3` | 3 | 짧거나 동질적이며 개별 동작을 바로 읽도록 유지 |
| `Base.ElectronicsMag5` | 2 | 짧거나 동질적이며 개별 동작을 바로 읽도록 유지 |
| `Base.EngineerMagazine1` | 1 | 짧거나 동질적이며 개별 동작을 바로 읽도록 유지 |
| `Base.EngineerMagazine2` | 1 | 짧거나 동질적이며 개별 동작을 바로 읽도록 유지 |
| `Base.FarmingMag1` | 2 | 짧거나 동질적이며 개별 동작을 바로 읽도록 유지 |
| `Base.FishingMag1` | 2 | 짧거나 동질적이며 개별 동작을 바로 읽도록 유지 |
| `Base.FishingMag2` | 2 | 짧거나 동질적이며 개별 동작을 바로 읽도록 유지 |
| `Base.HuntingMag1` | 1 | 짧거나 동질적이며 개별 동작을 바로 읽도록 유지 |
| `Base.HuntingMag2` | 2 | 짧거나 동질적이며 개별 동작을 바로 읽도록 유지 |
| `Base.HuntingMag3` | 2 | 짧거나 동질적이며 개별 동작을 바로 읽도록 유지 |
| `Base.MetalworkMag1` | 2 | 짧거나 동질적이며 개별 동작을 바로 읽도록 유지 |
| `Base.MetalworkMag2` | 1 | 짧거나 동질적이며 개별 동작을 바로 읽도록 유지 |
| `Base.MetalworkMag3` | 1 | 짧거나 동질적이며 개별 동작을 바로 읽도록 유지 |
| `Base.MetalworkMag4` | 2 | 짧거나 동질적이며 개별 동작을 바로 읽도록 유지 |
| `Base.SmithingMag1` | 8 | 단일 범주이므로 원문 목록 유지 |
| `Base.SmithingMag2` | 8 | 복수의 반복 범주를 접기 |
| `Base.SmithingMag3` | 12 | 복수의 반복 범주를 접기 |
| `Base.SmithingMag4` | 12 | 복수의 반복 범주를 접기 |
| `Radio.RadioMag1` | 1 | 짧거나 동질적이며 개별 동작을 바로 읽도록 유지 |
| `Radio.RadioMag2` | 1 | 짧거나 동질적이며 개별 동작을 바로 읽도록 유지 |
| `Radio.RadioMag3` | 1 | 짧거나 동질적이며 개별 동작을 바로 읽도록 유지 |

### 추가 적용 목록 KO/EN 전문과 범주

**Base.Paintbrush — ko**

- 벽 (4): 벽 / 문틀 / 창틀 / 기둥
- 일부 가구 (4): 일부 문 / 일부 의자 / 일부 상자 / 일부 탁자

**Base.Paintbrush — en**

- walls (4): Walls / Door frames / Window frames / Pillars
- Some furniture (4): Some doors / Some chairs / Some crates / Some tables

**Base.SmithingMag2 — ko**

- 재료 (4): 못 만들기 / 종이 집게 만들기 / 문 손잡이 만들기 / 경첩 만들기
- 생활용품 (2): 편지 개봉칼 만들기 / 가위 만들기
- 조리용품 (1): 버터칼 만들기
- 도구와 무기 (1): 둥근 망치 만들기

**Base.SmithingMag2 — en**

- Materials (4): Make Nails / Make Paperclips / Make Door Knob / Make Hinge
- Household items (2): Make Letter Opener / Make Scissors
- Cooking items (1): Make Butter Knife
- Tools and weapons (1): Make Ball Peen Hammer

**Base.SmithingMag3 — ko**

- 재료 (1): 금속판 만들기
- 조리용품 (1): 부엌칼 만들기
- 응급처치 용품 (3): 봉합용 바늘 집게 만들기 / 핀셋 만들기 / 봉합용 바늘 만들기
- 도구와 무기 (5): 집게 만들기 / 망치 만들기 / 톱 만들기 / 사냥용 칼 만들기 / 모종삽 만들기
- 그 밖의 학습 항목 (2): 드럼통 만들기 / 삽 만들기

**Base.SmithingMag3 — en**

- Materials (1): Make Sheet Metal
- Cooking items (1): Make Kitchen Knife
- First-aid supplies (3): Make Suture Needle Holder / Make Tweezers / Make Suture Needle
- Tools and weapons (5): Make Tongs / Make Hammer / Make Saw / Make Hunting Knife / Make Hand Shovel
- Other lessons (2): Make Metal Drum / Make Shovel

**Base.SmithingMag4 — ko**

- 도구와 무기 (3): 쇠지렛대 만들기 / 도끼 만들기 / 대형 망치 만들기
- 탄약 관련 물품 (8): 9mm 탄 틀 만들기 / .308 탄 틀 만들기 / .223 탄 틀 만들기 / 산탄 총탄 틀 만들기 / 9mm 탄 만들기 / 산탄 총탄 만들기 / .308 탄 만들기 / .223 탄 만들기
- 스포츠 용품 (1): 골프 클럽 만들기

**Base.SmithingMag4 — en**

- Tools and weapons (3): Make Crowbar / Make Axe / Make Sledgehammer
- Ammunition-related items (8): Make 9mm Bullets Mold / Make 308 Bullets Mold / Make 223 Bullets Mold / Make Shotgun Shells Mold / Make 9mm Bullets / Make Shotgun Shells / Make 308 Bullets / Make 223 Bullets
- Sports equipment (1): Make Golfclub

### 공통 표시 계약과 보존 검증

기존 `target_groups` → projection → lookup → readonly model → `IrisTargetGroupView` 경로와 Browser/Wiki 위젯을 재사용했다. 새 별도 메뉴나 중첩 접기를 만들지 않았다. 공통 ordered bucket builder는 기존 수리 목록에도 적용된다. identity는 원래 의미에 맞게 `item_ids`, `recipe_keys`, `target_keys` 중 하나만 사용한다. lookup은 한 목록 안에서 identity 종류가 섞이거나, 비어 있거나, 중복되거나, 범주 count가 다르거나, 본문 명칭이 누락되는 자료를 거부한다. model은 typed identity 배열과 범위를 읽기 전용으로 유지한다.

기존 6개 수리 metadata 동일, 신규 학습 32 recipe keys/32 이름, 페인트 16×8 target keys/이름을 KO/EN에서 전수 비교했다. 전체 fold identity는 양언어 합계 886개(수리566 + 학습64 + 페인트256)이며 누락·중복 없다. 범주 순서는 공통 선언 순서로 고정되고 각 범주 안의 학습 순서는 원래 레시피 순서를 보존한다. original Expanded 평문 순서는 그대로다. 전체 학습 82개의 make/modify/repair/recover 동작과 본문도 그대로다.

Browser/Wiki 기본 접힘, 헤더 전체 클릭 영역, 펼침/재접힘 후 높이, 전체 펼침 이름 수, 스크롤 경계, 축소 시 clamp, 다른 아이템 전환 후 초기화, Wiki 재개방 초기화 및 닫기를 25개 적용 항목과 6개 비적용 대조 표본에서 양언어로 검증했다. HTML 양쪽은 동일한 metadata를 사용한다. 148개 `<details>` 기본 닫힘, typed identity 886개, 메인 HTML 원문 8,420개를 parser로 대조했다. 실제 HTML 브라우저에서 대장장이 3권의 KO/EN 접힘/응급처치 범주 펼침과 범주 외 연료 용도를 시각 확인했다.

### 실행 결과

다음 실행은 모두 exit 0이다.

- `uv run --project .\Iris\tooling python .tmp/prose/depth_regenerate.py` — 전체 blocks/descriptions 재생성.
- `uv run --project .\Iris\tooling python -I -B -m pytest --noconftest -c .\Iris\tooling\pyproject.toml .\Iris\build\description\v2\tests\test_layer3_composition.py::test_layer3_composition_contract .\Iris\build\description\v2\tests\test_layer3_description_composition.py::test_layer3_description_composition --basetemp .\.tmp\learning-folds-pytest-01 -q -s --tb=short` — 2 passed in 30.35s.
- `uv run --project .\Iris\tooling python .tmp/prose/learning-folds-menu.py` — `IRIS_EXPANDED_MENU_PASS`, 4,210 states, Browser/Wiki, 31 표본. 최신 projection/실제 Lua lookup·model·UI 코드를 disposable fixture에서 실행했다.
- `powershell -ExecutionPolicy Bypass -File .\tools\check_lua_syntax.ps1` — 266 files.
- `lua Iris/test/lua/detail_view_model_locale_harness.lua .` — `IRIS_DETAIL_LOCALE_PASS`.
- `lua Iris/test/lua/browser_state_acceptance_harness.lua .` — PASS.
- `lua Iris/test/lua/browser_interaction_density_acceptance_harness.lua .` — PASS.
- `uv run --project .\Iris\tooling python .tmp/prose/learning-folds-audit.py` — all 8,420 texts unchanged, typed ID/name coverage PASS, 양 HTML 기본 닫힘·원문 검증.

검증 로그: `.tmp/prose/learning-folds-tests.log`, `learning-folds-menu.log`, `learning-folds-lua.log`, `learning-folds-browser-state.log`, `learning-folds-browser-interaction.log`, `learning-folds-audit.log`. 전수 명칭/범주 자료: `.tmp/prose/learning-folds-summary.json`.

실제 PZ 게임 엔진/폰트는 관찰하지 않았다. Lua 위젯/폰트 stub과 실제 HTML 브라우저 확인의 한계를 구분한다. 제품 ZIP 재패키징·설치·커밋·푸시는 하지 않았다. 기존 dirty/untracked 및 이전 교정 기록을 보존했다. 미래 adapter 범위로 확장하지 않았다.

현재 산출물 바인딩:

- `descriptions.json`: `f076169ae7a02fc42c50cee54b366a123b6dc905c3e5865ba09c242d52d3b9ef`
- `blocks.json`: `6c215c8b553265e053c281f686fcea5c213dc4a06709ff3136d3a5542ad81d3a`
- 직전 수락 descriptions: `72303dd1eba99ba1f16011d71bd2035d259123a9c804ea63566f5fe42ef9c490`
- 검증 fixture: `l3p-8e9b93bd8eece83adcd2519988f1a0f82df030160f8ab5fdc15a2e4ac33194d3`


## 2026-09-14 다섯 항목 후속 교정 완료

Compact의 목적 요약, 공통 문형, 목록 제목, 단일 항목 노출, B41 배치물·총기 부착물의 확인된 용도를 교정했다. 전체 2,105개를 재생성했고 Compact/Expanded × KO/EN 각 좌표의 present 1,976 / absent 129 / failed 0 상태는 유지했다.

### 원인과 결과

| 지적 | 원인 | 교정과 범위 | 판정 |
|---|---|---|---|
| 복합 Compact의 상세 나열 | 활동별 문장을 결합하고 C에도 E의 상세 대상 전부를 요구하던 규칙 | 연료 공급, 물 공급, 제작 재료, 전자·목공·정비 도구, 타격·굴착·절삭 도구 등의 공통 의미 규칙으로 목적을 묶었다. 글자 수 제한이나 아이템 ID별 완성 문장 예외를 쓰지 않는다. | 해결 |
| 어색한 한국어 | 역할과 행위를 잇는 공통 조사·서술어 | 약초 찜질제 3종의 ‘다친 부위에 바르는 …’, BlowTorch의 금속 부품 제작·구조물 건축 문형, 마찰 점화의 ‘비벼’를 정리했다. | 해결 |
| 대표성이 부족한 그룹명 | 내부 분류명이 실제 대상 범위를 가림 | 페인트와 붓 16개: ‘벽·문틀·창틀·기둥’, ‘일부 문·의자·상자·탁자’. 전체 수리·도색·학습 그룹명을 확인했다. 차량/악기/스포츠/원예/창/도끼/칼날/둔기 및 재료/생활/조리/응급처치/도구/탄약/기타 학습 범주는 실제 목록과 대응한다. | 해결 |
| 한 항목도 클릭 필요 | 모든 그룹을 동일 disclosure로 렌더링 | 공통 presentation 메타데이터와 Lookup→읽기 전용 모델→Browser/Wiki 공통 뷰→HTML에 반영. 6개 단일 그룹 × 2언어는 바로 노출, 나머지 136개 언어별 그룹은 접힘 유지. | 해결 |
| 가구·부착물 용도 부재 | 배치/장착 경로만 읽고 타일 속성 및 실제 소비 코드를 연결하지 못함 | B41.78 원본 타일 로드 순서와 Lua/native 소비 경로를 연결해 확인된 기능을 추가. 아래에 항목별 결과와 남은 연결 공백을 기록한다. | 확인된 용도 반영, 나머지 부분 해결 |

전체 복합 후보는 기존 Expanded use_units 3개 이상인 632개를 추출해 동일 결과를 묶어 읽었다. 음식의 섭취/요리/미끼, 의류의 착용/천/로프/연료, 탄약의 포장/장전/분해처럼 짧고 독립적인 목적은 유지했다. 다른 조건이나 역할을 잃는 일괄 축약은 적용하지 않았다. 별도로 2개 용도의 제작 재료도 공통 의미 조건에 맞으면 묶는다. 변경된 64가지 고유 결과의 KO/EN C/E 전문을 모두 읽었고 목공만 확인된 TreeBranch에 건축을 확대하던 표현은 목공으로 바로잡았다.

기존 Expanded의 fact_refs는 모두 보존됐다. 기존 문장 변경은 약초 3종과 BlowTorch의 한국어 문형 교정뿐이며, 기존 독립 용도/조건/대상과 886개 언어별 대상·학습 식별자의 이름·순서·범위를 보존했다. C에 모든 E 세부 항목을 반복하도록 요구하던 테스트는 E 보존 검사로 옮겼다.

### 실제 전후 예

**Base.Plank**

- 이전 C: 골절을 고정하는 부목 재료로 쓸 수 있다. 목공 및 건축에 재료로 쓸 수 있다. 사냥 장비, 야영 장비 및 도구 제작에도 쓸 수 있다. 수박을 쪼개는 데 쓸 수 있다. 무기로도 쓸 수 있다. 모닥불 등의 연료로 쓸 수 있다.
- 현재 C: 골절을 고정하는 부목 재료로 쓸 수 있다. 건축과 장비 제작에 재료로 쓸 수 있다. 타격 도구나 무기로 쓸 수 있다. 모닥불 등의 연료로 쓸 수 있다.
- Current EN C: It can supply splinting material for fractures. It can supply material for construction and equipment making. It can serve as a striking tool or weapon. It can be used as fuel for campfires, for example.

**Base.WaterBottleFull**

- 이전 C: 물을 담아 보관하거나 옮길 수 있다. 담긴 물은 마시거나 작물에 줄 수 있고, 차량에 묻은 피를 씻거나 불을 끄는 데도 쓸 수 있다. 오염된 물을 마시면 중독될 수 있다.
- 현재 C: 물을 담아 마시거나 농사, 세척 등에 공급할 수 있다. 오염된 물을 마시면 중독될 수 있다.
- Current EN C: It can carry water for drinking, farming and tasks such as cleaning; drinking tainted water risks poisoning.

**Base.RippedSheets**

- 이전 C: 상처 처치와 골절 고정에 쓰거나 의류 수선 재료로 쓸 수 있다. 감염된 재료로 상처를 감으면 감염을 일으킬 수 있다. 건축에 재료로 쓸 수 있다. 화염 장치, 연막 장치, 야영 장비 및 도구 제작에도 쓸 수 있다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다.
- 현재 C: 응급처치와 의류 수선에 쓸 수 있다. 감염된 재료로 상처를 감으면 감염을 일으킬 수 있다. 건축과 장비 제작에 재료로 쓸 수 있다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다.
- Current EN C: It can be used for first aid or clothing repairs. Infected material can infect a wound when used as bandaging. It can supply material for construction and equipment making. It can be used as fuel or tinder, for example in campfires.

**Base.Screwdriver**

- 이전 C: 전자기기를 만들거나 분해하고, 조명을 건전지용으로 개조할 수 있다. 목재를 가공하거나 목제 계단 및 기둥 조명 같은 설치물을 해체할 수 있다. 차량 부품과 호환 무기 부착물을 장착하거나 제거할 수 있다. 제작한 창에 부착하거나 무기로 쓸 수도 있다.
- 현재 C: 전자기기 제작, 분해, 개조와 목공, 정비 작업에 쓸 수 있다. 무기로도 쓸 수 있다.
- Current EN C: It can be used for electronics work, woodworking and mechanical maintenance. It can also serve as a weapon.

**Base.PetrolCan**

- 이전 C: 주유기나 차량에서 연료를 담을 수 있다. 담긴 연료를 차량에 넣을 수도 있다. 화염 장치를 만들 때 재료로 쓸 수 있다. 시신을 태우는 데 쓸 수 있다. 모닥불 등에 불을 붙이는 연료로 쓸 수 있다. 발전기에 휘발유를 보충할 수 있다.
- 현재 C: 연료를 담아 차량, 발전기에 공급하거나 불을 붙이는 연료로 쓸 수 있다. 화염 장치를 만들 때 재료로 쓸 수 있다.
- Current EN C: It can carry fuel for vehicles and generators or supply fuel for lighting fires. It can be used as material for making incendiary devices.

**Base.ComfreyCataplasm**

- 이전 C: 다친 부위에 약초 찜질제로 바를 수 있다.
- 현재 C: 다친 부위에 바르는 약초 찜질제로 쓸 수 있다.
- Current EN C: It can be applied to an injured body part as an herbal poultice.

**Base.BlowTorch**

- 이전 C: 금속 부품을 용접하거나 용접으로 건축하는 도구로 쓸 수 있다. 금속 바리케이드를 설치하거나 철거하는 데 쓸 수 있다. 불타거나 파손된 차량을 분해하는 데 쓸 수 있다.
- 현재 C: 금속 제작, 건축과 금속 바리케이드나 불탄 차량 등의 해체에 용접 도구로 쓸 수 있다.
- Current EN C: It can serve as a welding tool for metalwork and construction, or dismantling metal barricades and burnt vehicles, for example.

**Base.Mov_BluePlasticChair**

- 이전 C: 가구로 놓아 사용할 수 있다.
- 현재 C: 배치해 잠을 자거나 쉬는 데 쓸 수 있다.
- Current EN C: It can be placed for sleeping or resting.

**Base.Mov_AirConditioner**

- 이전 C: 가구로 놓아 사용할 수 있다.
- 현재 C: 용접용 마스크와 프로판 토치를 써서 배치된 물체를 분해해 재료를 회수할 수 있다.
- Current EN C: A welding mask and propane torch can be used to dismantle the placed object for materials.

**Base.GunLight**

- 이전 C: 드라이버로 호환 총기에 장착하거나 떼어 회수할 수 있다.
- 현재 C: 호환 총기에 장착해 이동으로 인한 명중률 감소를 줄일 수 있다.
- Current EN C: On a compatible firearm, it can reduce the movement-related hit-chance penalty.

### B41 소스 연결과 남은 공백

읽기 전용 조사 위치는 `G:/Program Files (x86)/Steam/steamapps/common/ProjectZomboid`다. Core의 GameVersion(41,78), 저장소 newitems.txt와 설치본 SHA 일치, Lua 소비 파일 SHA 일치를 확인했다. 생산기는 이 설치 경로를 읽지 않고 `Iris/build/description/source_support/b41_placed_object_properties.json`의 한정된 추출 사실과 출처 해시를 검증한다. 게임 자산 전체나 native 클래스/디컴파일 전문을 저장소에 복제하지 않았다.

IsoWorld의 실제 순서대로 tiledefinitions → newtiledefinitions → erosion → apcom → overlays → noiseworks.patch를 적용했다. 로드되지 않는 legacy tiledefinitions_4는 제외했다. 136개 WorldObjectSprite가 모두 매핑됐다.

- `ISMoveableSpriteProps.lua`: 배치 객체 생성과 속성 보존, 물 연결·용기·조명·해체 경로. `ISMoveableDefinitions.lua`: 실제 재료별 해체 정의와 도구 및 결과 후보를 연결. 회수 수량·확률·품질을 일반화하지 않았다.
- `ISWorldObjectContextMenu.lua`: 침대의 수면/휴식, 급수의 물 받기/씻기, 조리·조명 조작. `ISInventoryPaneContextMenu.lua:doMakeUpMenu`: IsMirror를 화장 조건으로 소비한다. 머리 모양 변경 기능으로 확대하지 않았다.
- `ISPlace3DItemCursor.lua:getSurface` → `IsoObject.getSurfaceOffsetNoTable`: Surface 및 ItemHeight를 실제 배치 높이로 소비.
- `IsoObject.createContainersFromSpriteProperties`, `ItemContainer.getTemprature`: 보관 및 전원 조건의 냉장/조리. `IsoFireplace.getTemperature/updateHeatSource` 및 `ISFireplaceMenu`, `IsoBarbecue` 및 `ISBBQMenu`: 연료 조건의 난방/조리.
- `ISInventoryTransferAction.lua` → `IsoMannequin.wearItem`: 의류 입히기.
- `HandWeapon.attachWeaponPart`가 양의 AimingTimeModifier를 무기에 더하고 `SwipeStatePlayer`의 ranged hit-chance 계산이 이동 시간에서 AimingTime+AimingSkill을 뺀 벌점을 적용한다. 따라서 Bayonnet/GunLight에는 ‘이동으로 인한 명중률 감소를 줄일 수 있다’를 반영했다. 이름에 의한 찌르기/발광 효과나 조준 시간 단축으로 해석하지 않았다.

가구 136개 중 102개에 확인된 용도를 추가했다. 기능별 수(중복 포함): {'placed_purpose_sleep': 30, 'placed_purpose_surface': 71, 'placed_purpose_salvage_welding': 24, 'placed_purpose_hearth': 1, 'placed_purpose_salvage_screwdriver': 18, 'placed_purpose_storage': 8, 'placed_purpose_salvage_wood': 36, 'placed_purpose_mirror': 5, 'placed_purpose_water_piped': 4, 'placed_purpose_cooking': 9, 'placed_purpose_salvage_hammer': 7, 'placed_purpose_cold_storage': 1, 'placed_purpose_light': 7, 'placed_purpose_mannequin': 2, 'placed_purpose_barbecue': 1, 'placed_purpose_water_storage': 1}

남은 항목은 아래와 같다. 무기능임을 증명한 목록이 아니라 이번 조사에서 배치/이동 외 독립 기능의 연결을 확보하지 못한 목록이다. 원본 속성 전체는 위 스냅샷에서 sprite 키로 확인할 수 있다. 장식·벽걸이 객체에 임의의 능력치를 붙이지 않았다. CanScrap만 있는 경우에도 실제 material→scrap definition→result 경로가 없거나 채택된 도구 형태와 맞지 않으면 회수를 단정하지 않았다.

| 항목 | sprite | 남은 관계 |
|---|---|---|
| Base.Mov_Birdbath | vegetation_ornamental_01_50 | 배치/이동 속성 외 독립 행동 소비 연결 미확보 |
| Base.Mov_ConcreteMixer | construction_01_6 | 배치/이동 속성 외 독립 행동 소비 연결 미확보 |
| Base.Mov_CorkBoard | location_business_office_generic_01_7 | 배치/이동 속성 외 독립 행동 소비 연결 미확보 |
| Base.Mov_DegreeDoctor | location_community_medical_01_14 | 배치/이동 속성 외 독립 행동 소비 연결 미확보 |
| Base.Mov_DegreeSurgeon | location_community_medical_01_31 | 배치/이동 속성 외 독립 행동 소비 연결 미확보 |
| Base.Mov_FitnessContraption | recreational_sports_01_41 | 배치/이동 속성 외 독립 행동 소비 연결 미확보 |
| Base.Mov_FlagAdmin | walls_decoration_01_18 | 배치/이동 속성 외 독립 행동 소비 연결 미확보 |
| Base.Mov_FlagUSA | walls_decoration_01_16 | 배치/이동 속성 외 독립 행동 소비 연결 미확보 |
| Base.Mov_FlagUSALarge | location_military_knox_01_8 | 배치/이동 속성 외 독립 행동 소비 연결 미확보 |
| Base.Mov_GardenGnome | vegetation_ornamental_01_48 | 배치/이동 속성 외 독립 행동 소비 연결 미확보 |
| Base.Mov_HuntingTrophy | camping_01_18 | 배치/이동 속성 외 독립 행동 소비 연결 미확보 |
| Base.Mov_MapUSA | location_community_school_01_22 | 배치/이동 속성 외 독립 행동 소비 연결 미확보 |
| Base.Mov_MobileBloodbag | location_community_medical_01_25 | CanScrap → Material 없음 → 채택 가능한 해체 정의/도구/결과 연결 미확보 |
| Base.Mov_PaintingBetty | walls_decoration_01_48 | 배치/이동 속성 외 독립 행동 소비 연결 미확보 |
| Base.Mov_PaintingElisa | walls_decoration_01_46 | 배치/이동 속성 외 독립 행동 소비 연결 미확보 |
| Base.Mov_PaintingGreen | walls_decoration_01_35 | 배치/이동 속성 외 독립 행동 소비 연결 미확보 |
| Base.Mov_PaintingLibrary | walls_decoration_01_57 | 배치/이동 속성 외 독립 행동 소비 연결 미확보 |
| Base.Mov_PinkFlamingo | vegetation_ornamental_01_25 | 배치/이동 속성 외 독립 행동 소비 연결 미확보 |
| Base.Mov_PosterDroids | walls_decoration_01_33 | 배치/이동 속성 외 독립 행동 소비 연결 미확보 |
| Base.Mov_PosterElement | location_entertainment_theatre_01_84 | 배치/이동 속성 외 독립 행동 소비 연결 미확보 |
| Base.Mov_PosterMedical | location_community_medical_01_11 | 배치/이동 속성 외 독립 행동 소비 연결 미확보 |
| Base.Mov_PosterOmega | walls_decoration_01_50 | 배치/이동 속성 외 독립 행동 소비 연결 미확보 |
| Base.Mov_PosterPaws | location_entertainment_theatre_01_83 | 배치/이동 속성 외 독립 행동 소비 연결 미확보 |
| Base.Mov_PosterPieBlue | location_restaurant_pie_01_57 | 배치/이동 속성 외 독립 행동 소비 연결 미확보 |
| Base.Mov_PosterPieGreen | location_restaurant_pie_01_58 | 배치/이동 속성 외 독립 행동 소비 연결 미확보 |
| Base.Mov_PosterPiePink | location_restaurant_pie_01_59 | 배치/이동 속성 외 독립 행동 소비 연결 미확보 |
| Base.Mov_PosterPieRed | location_restaurant_pie_01_56 | 배치/이동 속성 외 독립 행동 소비 연결 미확보 |
| Base.Mov_RoadCone | street_decoration_01_26 | CanScrap → Material PlasticHard → 채택 가능한 해체 정의/도구/결과 연결 미확보 |
| Base.Mov_RoadCone2 | street_decoration_01_27 | CanScrap → Material PlasticHard → 채택 가능한 해체 정의/도구/결과 연결 미확보 |
| Base.Mov_SatelliteDish | appliances_com_01_20 | CanScrap → Material AluminumScrap → 채택 가능한 해체 정의/도구/결과 연결 미확보 |
| Base.Mov_SignArmy | location_military_generic_01_18 | 배치/이동 속성 외 독립 행동 소비 연결 미확보 |
| Base.Mov_SignCitrus | location_shop_accessories_01_27 | 배치/이동 속성 외 독립 행동 소비 연결 미확보 |
| Base.Mov_SignRestricted | location_military_generic_01_19 | 배치/이동 속성 외 독립 행동 소비 연결 미확보 |
| Base.Mov_SignWarning | location_military_generic_01_21 | 배치/이동 속성 외 독립 행동 소비 연결 미확보 |

### 검증 및 산출물

- 생성 설명 SHA-256: `d66a1b8cc6efa8ce58e2db5a27400824baf8a2ccec3dad3f8b2e36f86a6d94da`
- blocks SHA-256: `af04dc667d7dfe7867532dc3acf574b096b31b4c7080c05c8acab8ea3d7ec6ae`
- 소스 스냅샷 SHA-256: `b45f2dc61f2ed421d519ee6744298012a935b0308bc236b5f4ad719ead5679c9`
- 전문/영향 좌표/632개 후보/136개 가구 결과: `Iris/build/description/composition/quality_review/five_corrections/`.
- 두 HTML을 재생성하고 원문 8,420좌표 및 886개 식별자, 12 inline / 136 disclosure를 기계 검증했다.
- 실제 HTML 미리보기에서 KO/EN 금속판·부엌칼이 접힌 그룹 밖에 표시되고, 응급처치 3항목 펼치기/접기가 동작함을 확인했다.
- `powershell -ExecutionPolicy Bypass -File .\tools\check_lua_syntax.ps1`: exit 0, 266 files.
- `lua Iris/test/lua/detail_view_model_locale_harness.lua .`: exit 0.
- `lua Iris/test/lua/browser_state_acceptance_harness.lua .`: exit 0.
- `lua Iris/test/lua/browser_interaction_density_acceptance_harness.lua .`: exit 0.
- 상세 메뉴 fixture 검증은 실제 Lookup/모델/Browser/Wiki 공통 뷰로 4,210 상태와 35 표본의 클릭·접힘·단일 항목·중복·스크롤·언어 전환을 검증했다. 폰트는 stub이며 실제 PZ 화면 검증을 의미하지 않는다.

최종 pytest 및 최종 fixture의 명령/exit 결과는 아래 추가 기록에 따른다. 패키징, 게임 설치, 커밋, 푸시는 하지 않았다.

최종 검증 기록:

```powershell
uv run --project .\Iris\tooling python -I -B -m pytest --noconftest -c .\Iris\tooling\pyproject.toml .\Iris\build\description\v2\tests\test_layer3_composition.py::test_layer3_composition_contract .\Iris\build\description\v2\tests\test_layer3_description_composition.py::test_layer3_description_composition --basetemp .\.tmp\review-five-pytest-04 -q -s --tb=short
```

exit 0: 2 passed in 34.64s.

```powershell
uv run --project .\Iris\tooling python .tmp/prose/review-five-menu.py
uv run --project .\Iris\tooling python .tmp/prose/review-five-audit.py
```

두 명령 모두 exit 0. 최종 메뉴 fixture는 `.tmp/menu/review-five-runtime-04`이며 결과:

```text
fixture C:\Users\MW\Downloads\coding\PZ\.tmp\menu\review-five-runtime-04\runtime id l3p-095823d85f2835f9aeab0ff49693389914bb140f0e5b9902be44f6a7d5e23f17 samples 35
IRIS_EXPANDED_MENU_PASS product=l3p-095823d85f2835f9aeab0ff49693389914bb140f0e5b9902be44f6a7d5e23f17 states=4210 consumers=Browser,Wiki font=stub
```

최종 텍스트 변경은 166개 항목 / 551개 언어·표면 좌표다. 그룹 메타데이터까지 포함하면 191개 / 601개 좌표다. E 기존 근거·대상 보존, HTML 원문 일치, 886개 대상·학습 식별자 일치가 모두 통과했다. 초기 테스트의 C 상세 나열 기대 및 사실 목록 없는 입력 오류, 임시 fixture 목록 충돌은 수정 후 최종 명령으로 재검증했다.

추가 진단: 기본 git diff --check는 저장소의 CRLF 줄을 trailing whitespace로 판정해 exit 1이었다. cr-at-eol을 허용한 진단도 description_composition_uses.py 파일 끝 빈 줄 1건으로 exit 1이므로 이 진단은 PASS로 주장하지 않는다. 기능 검증 결과와 구분한다.



## 2026-09-14 가구 문형·독립 용도·타격 요약 재교정

앞 절의 완료 판단 이후 받은 A/B/C 피드백을 같은 교정에서 반영했다. 이전 전문과 문장 byte 보존 설명보다 이 절과 현재 생성물을 우선한다.

- A: 네 가지 해체 공통 문형의 ‘배치된 물체’를 제거했다. 현재 아이템이 가공 대상임을 유지하면서 E는 ‘배치한 뒤 드라이버로 분해해 재료를 회수할 수 있다’ 등으로 배치 전제와 도구를 보존한다. 회수만 요약할 때 C는 ‘분해해 재료를 회수할 수 있다’다. 영어도 ‘Once placed, it can be dismantled with … to recover materials’로 현재 아이템을 가리킨다.
- B: 가구의 모든 확인된 독립 용도를 E의 개별 use_unit으로 분리했다. 중복 generic 배치 문장을 제거하고 placement fact를 구체적인 배치 활용에 연결했으며, 이동은 ‘배치한 뒤에도 다른 위치로 옮길 수 있다’로 별도 보존했다. 해체 활용은 마지막에 배치해 분해 후에 수납·수면하는 것처럼 읽히지 않게 했다.
- C: 비전투 근거가 수박 쪼개기뿐인 경우 ‘타격 도구’라는 빈 범주를 C에 추가하지 않는다. BaseballBat/BaseballBatNails/Plank/Sledgehammer/Sledgehammer2의 공통 의미 조건에 적용했다. C의 다른 목적은 유지하고 수박 활용은 E에 보존했다. 금속 단조·목공·건축이라는 타격 목적이 확인된 Hammer 계열의 요약은 유지했다. primary_use나 아이템 ID 문장 예외를 쓰지 않았다.
- 페인트 제목의 중간점은 문서 축약이 아니라 실제 metadata label이었다. 이제 실제 제목은 ‘벽, 문틀, 창틀, 기둥’, ‘일부 문, 의자, 상자, 탁자’다. 16개 항목의 KO 그룹32개에 적용했으며 전체 그룹명에 중간점이 없는지 검사했다. 대상 이름·키·순서·some 범위는 그대로다.

구체 예: Mov_CabinetMedical E는 이제 아래 다섯 개 독립 항목이다.

1. 설치해 화장할 때 필요한 거울로 쓸 수 있다.
2. 배치해 물건을 보관하는 데 쓸 수 있다.
3. 배치한 뒤 물건을 올려둘 수 있다.
4. 배치한 뒤에도 다른 위치로 옮길 수 있다.
5. 배치한 뒤 망치와 톱을 써서 분해해 재료를 회수할 수 있다.

가구102개 전체와 같은 타격 문형 전체의 KO/EN C/E 36개 고유 전문을 끝까지 다시 읽었다. 이번 후속 텍스트 변경은107개다. 남은34개 가구 및 신규 근거 스냅샷은 변경하지 않았다. 기존 Expanded fact_refs 전부 보존, 각 가구 독립 역할의 단일 use_unit 분리, 이동 의미 보존, 전원/급수/연료/해체 도구 조건 보존을 검사했다. 문장 byte 보존 대신 해당 의미를 보존하면서 중복 문면을 통합했다.

최신 전문 및 범위: `Iris/build/description/composition/quality_review/five_corrections/furniture_followup/fulltext.txt`, `scope.json`. 상위 affected_bilingual_fulltext.txt도 현재 출력으로 갱신했다.

전체2,105개 재생성 및 projection/hash binding, 두 HTML 갱신 완료. 현재 descriptions SHA `ca19b03556890c86e7637bf27e2b17fbec3e9ceb272253459a5bdc882fb9f5c1`; blocks SHA `3e11c463c17d49f5518e862001a05b2ce1a33f141b5d6a5e1ee9b5aaa340730f`.

검증(각 exit0):

```powershell
uv run --project .\Iris\tooling python -I -B -m pytest --noconftest -c .\Iris\tooling\pyproject.toml .\Iris\build\description\v2\tests\test_layer3_composition.py::test_layer3_composition_contract .\Iris\build\description\v2\tests\test_layer3_description_composition.py::test_layer3_description_composition --basetemp .\.tmp\furniture-followup-pytest-01 -q -s --tb=short
powershell -ExecutionPolicy Bypass -File .\tools\check_lua_syntax.ps1
uv run --project .\Iris\tooling python .tmp/prose/furniture-followup-audit.py
uv run --project .\Iris\tooling python .tmp/prose/review-five-audit.py
uv run --project .\Iris\tooling python .tmp/prose/review-five-menu.py
```

pytest2passed37.20s, Lua266files, 전체 E근거/HTML원문8,420/886식별자/136disclosure+12inline보존 통과. 메뉴 결과:

```text
fixture C:\Users\MW\Downloads\coding\PZ\.tmp\menu\furniture-followup-runtime-02\runtime id l3p-18a1a85238915cf61da3d1526ec5d48218af2819fd7f4bcc62216453be2dae24 samples 135
IRIS_EXPANDED_MENU_PASS product=l3p-18a1a85238915cf61da3d1526ec5d48218af2819fd7f4bcc62216453be2dae24 states=4210 consumers=Browser,Wiki font=stub
```

이번 변경의 uses.py EOF 빈 줄을 제거했다. 저장소 CRLF 줄바꿈은 유지했고 다음 CRLF 인식 진단은 exit0이다. 이전의 기본 diffcheck CRLF 오탐과 EOF 실제 문제를 구분한다.

```powershell
git -c core.whitespace=blank-at-eol,blank-at-eof,space-before-tab,cr-at-eol diff --check -- Iris/tooling/src/iris_tooling/domains/layer3/recovery_sources.py Iris/tooling/src/iris_tooling/domains/layer3/description_composition_results.py Iris/tooling/src/iris_tooling/domains/layer3/description_composition_uses.py Iris/build/description/v2/tests/test_layer3_description_composition.py
```

폰트stub 검증이며 게임 실행/설치/패키징/커밋/푸시는 하지 않았다.


## 2026-09-14 동등 용도 요약·부착물 해석·가구 도입부 교정

기준 descriptions `ca19b03556890c86e7637bf27e2b17fbec3e9ceb272253459a5bdc882fb9f5c1`, blocks `3e11c463c17d49f5518e862001a05b2ce1a33f141b5d6a5e1ee9b5aaa340730f`에서 이어서 승인된 세 사항을 교정했다. 이전 절의 가구102보강/34연결미확보와129absent 경계는 그대로 유지한다.

### 1. 동등 의미에 대한 요약 적용

원인은 앞 단계의 단조 목적 묶음이 `metal_forging`, `shovel_smithing`, `smithing_parts`를 같은 목적으로 표현하지만, 뒤 Compact 목적 규칙은 `smithing_parts`를 허용하지 않아 그 근거가 포함된 문장 전체를 선택에서 제외한 것이다. BallPeenHammer의 추가 문 부품 단조 근거가 이 조건에 걸렸다.

공통 `FORGING_ACTIVITIES`를 앞 단계와 요약 단계가 공유하고, 목적 비교 때만 세 활동을 금속 단조로 정규화했다. 원본 활동/대상/조건/참여 역할은 바꾸지 않았다. 도구·재료·형틀 역할을 섞지 않았고 특정 아이템 ID에 완성 문장을 덮어쓰지 않았다.

전체2,105개에서 KO/EN Expanded 전문 동일군과 문장 순서만 다른 동등군을 모두 추출했다. 이전531개 고유 E 의미군 중166개가 다중 항목군이었다. C 차이 후보는 KO/EN 각각 BallPeenHammer–HammerStone, GridlePan–Pan 두 군뿐이었다. 망치 군의 단순 근거구조 차이는 교정했다. Pan은 별도 `food_preparation/container` 근거가 있고 GridlePan은 `food_ingredient_addition/base`만 있어서 ‘재료를 담아 요리’/‘재료를 더해 요리’의 같은 깊이 표현 차이는 유지했다. 동일 E 문자열만으로 모두 같은 C를 강제하지 않았다.

단조 관련13개 전체(미변경 포함)를 읽었다: 탄약 형틀4개, BallPeenHammer/Hammer/HammerStone, GunPowder, Handle, IronIngot, MetalBar, Plank, Tongs. 세 망치는 목적 요약을 공유하며 Hammer의 바리케이드 철거 추가 의미는 E에 그대로 있다. 나머지 재료/형틀/단일 도구는 각 역할과 범위를 유지했다. 전수 대조 뒤 남은 동일 E/C 차이 후보는 Pan–GridlePan뿐이다.

BallPeenHammer C 전후:

- 이전: 금속을 단조하거나 목재를 가공할 수 있다. 문과 창문의 판자 바리케이드 설치에 쓸 수 있다. 수박을 쪼개는 데 쓸 수 있다. 무기로도 쓸 수 있다.
- 현재: 금속 단조, 목공과 건축에 쓰는 타격 도구이며 무기로도 쓸 수 있다.
- EN: It can serve as a striking tool for metal forging, woodworking and construction, or as a weapon.

### 2. 같은 부착물 속성의 해석 일관성

채택 WeaponPart14개를 전부 조사했다. 양의 AimingTimeModifier는 RedDot/GunLight/Bayonnet에만 있고 셋 모두+5다. 나머지11개는 이 속성을 선언하지 않으므로 조준 관련 설명을 일괄 덧붙이지 않았으며 기존 장전/사거리/정확도/무게/반동/산탄 용도는 그대로다. MountOn 범위가 서로 다르므로 공통 문면은 ‘호환 총기’ 범위를 유지한다.

B41.78 동일 설치본의 Core와 기존 native/source SHA를 재검증했다. `scripts/newitems.txt` 및 EN Tooltip 원본이 저장소와 byte 일치한다. 설치본 zombie class 전체의 getAimingTime/AimingTimeModifier 참조를 검색했고 Item, WeaponPart, HandWeapon, IsoPlayer, SwipeStatePlayer 다섯 클래스가 해당한다. 직접 javap로 다음 연결을 확인했다.

1. Item의 AimingTimeModifier 파싱 → WeaponPart.aimingTime 초기화.
2. WeaponPart.getAimingTime은 해당 필드를 반환. HandWeapon.attachWeaponPart는 이를 더하고 detach는 뺀다.
3. SwipeStatePlayer의 원거리 명중 계산은 이동 시간과 무기의 AimingTime/기술에 따른 문턱값을 비교하여 벌점을 적용한다. 양의 modifier는 이 벌점을 줄일 수 있다.
4. IsoPlayer의 치명타 계산도 이동 문턱값에 같은 속성을 소비한다. 검사한 소비 경로는 별도 조준 동작 시간을 재거나 단축하는 계산이 아니다. Lua 검색 결과는 관리자 아이템 편집 UI만 있었다.

바닐라 Tooltip_RedDot은 aiming speed라고 표현한다. 이를 별도의 독립 속도 효과로 확정하거나 거짓이라고 단정하는 대신, 실제로 확인된 더 구체적인 이동 중 명중 관련 활용으로 공개 문면을 정리했다. native 경로의 Tooltip 없음 제한을 제거하여 같은 조건을 만족하는 세 부착물 모두에 증거를 연결한다. RedDot의 툴팁 근거도 보존하지만 native 근거가 함께 있을 때 속도 문장을 두 번째 독립 효과로 중복 출력하지 않는다. 이름에 따른 조명·찌르기 효과를 추정하지 않았다.

RedDot C/E 용도 문장 전후:

- 이전: 호환 총기의 조준 속도를 높이는 부착물로 쓸 수 있다.
- 현재: 호환 총기에 장착해 이동으로 인한 명중률 감소를 줄일 수 있다.
- EN: On a compatible firearm, it can reduce the movement-related hit-chance penalty.

세 항목 모두 E의 드라이버 장착/제거 활용은 유지했다. 숫자 계산은 플레이어 설명에 노출하지 않았다. 추출 스냅샷 `b41_placed_object_properties.json`의 attachment_scope_review에14개 속성/호환 범위/툴팁과 해석을 기록하고, 세 추가 native 클래스와 Tooltip 해시를 연결했다. 생산기는 여전히 설치 경로 없이 한정된 스냅샷+저장소 파일 해시를 검증한다.

### 3. 가구 도입부 반복

가구102개의 독립 use_unit과 해체 대상을 유지하면서 수면/수납/상판/이동/해체의 공통 문형을 다듬었다. 배치 전제는 각 활용에 남기되 모든 문장을 ‘배치한 뒤’로 시작하지 않는다. 이동은 집어 드는 동사로 배치된 가구를 옮기는 의미를 표현한다. 전원·물·연료 조건과 해체 도구·결과는 그대로다. 별개의 용도를 순차 작업으로 연결하지 않았고 해체는 마지막에 유지했다.

BluePlasticChair E 현재:

- 놓아서 잠을 자거나 쉬는 데 쓸 수 있다.
- 물건을 올려두는 용도로 놓아 쓸 수 있다.
- 집어 들어 다른 위치로 옮길 수 있다.
- 설치된 상태에서 용접용 마스크와 프로판 토치를 써서 분해해 재료를 회수할 수 있다.

EN 수면 문장은 검수 중 명령형을 제거해 ‘When set down, it provides a place to sleep or rest’로 정리했다. 수납은 ‘수납용으로 놓아 사용할 수 있다’, 상판은 ‘물건을 올려두는 용도로 놓아 쓸 수 있다’처럼 역할을 먼저 드러낸다. 34개 미확보 가구의 현재 설명에는 손대지 않았다.

### 검수와 검증

실제 텍스트 변경104개(가구102+BallPeenHammer+RedDot). 변경·미변경을 합친131개/56개 고유 KOEN C/E 전문을 끝까지 읽었다. 파일: `Iris/build/description/composition/quality_review/consistency_review/fulltext.txt`; 전체 항목 scope.json, before/after changes.json, 동등군 후보 equivalence_candidates_before.txt. 이는 자동 테스트 성공과 별도의 문면 검수다. 기존 E 근거 전부와 독립 용도/조건/목록 식별자·scope·순서·단일inline/접힘을 보존했고 RedDot의 기존 ‘속도’ 해석은 위 근거에 따라 구체화했다.

현재 결과:

- descriptions SHA `4687a618beb2a47d728157aafcb676652481c3cc3f098b15c21586ad07a2e876`
- blocks SHA `e290c79b0f6d3b8738df5203926aa249309f8c14eaf6eebbed13e809a40ed455`
- source snapshot SHA `9bad7eb46d3cea3dcef9e4368e73d33643e34105ce157f75982ec0d1b63cd74b`

전체2105 정식 재생성, 현재 projection 및 tooltip binding, 두 HTML 갱신 완료. present1976/absent129/failed0의 각 표면·언어 상태는 유지했다. 다음 각각 exit0:

```powershell
uv run --project .\Iris\tooling python -I -B -m pytest --noconftest -c .\Iris\tooling\pyproject.toml .\Iris\build\description\v2\tests\test_layer3_composition.py::test_layer3_composition_contract .\Iris\build\description\v2\tests\test_layer3_description_composition.py::test_layer3_description_composition --basetemp .\.tmp\consistency-pytest-02 -q -s --tb=short
powershell -ExecutionPolicy Bypass -File .\tools\check_lua_syntax.ps1
uv run --project .\Iris\tooling python .tmp/prose/consistency-audit.py
uv run --project .\Iris\tooling python .tmp/prose/review-five-audit.py
uv run --project .\Iris\tooling python .tmp/prose/review-five-menu.py
```

pytest2passed34.09s, Lua266files, 전체 E근거/조건 및 HTML8420좌표/886식별자/136disclosure+12inline 보존 통과. 최종 메뉴:

```text
fixture C:\Users\MW\Downloads\coding\PZ\.tmp\menu\consistency-runtime-01\runtime id l3p-eb972ab0fa435b40b007ce861a529377af8414fec9a2361d7925d0f6a2aa8168 samples 162
IRIS_EXPANDED_MENU_PASS product=l3p-eb972ab0fa435b40b007ce861a529377af8414fec9a2361d7925d0f6a2aa8168 states=4210 consumers=Browser,Wiki font=stub
```

변경한 다섯 Python 파일에 대한 `git -c core.whitespace=blank-at-eol,blank-at-eof,space-before-tab,cr-at-eol diff --check -- …`도 exit0이었다. CRLF를 유지했고 EOF 빈 줄을 재도입하지 않았다. 실제 PZ 화면의 폰트/배치 검증은 아니며 위 위젯 테스트는 font stub이다. 가구34개 연결공백,129absent,전체용도 완전성은 이번 세 사항으로 해결됐다고 주장하지 않는다. 패키징/설치/커밋/푸시는 하지 않았다.


## 2026-09-14 망치 Compact 분류어 제거

사용자 합의에 따라 공통 목적 문형에서 ‘타격 도구’라는 불필요한 분류를 제거했다. 용도와 행동이 이미 분명하면 분류를 덧붙이지 않는 원칙이며, 다른 역할 구분에 필요한 ‘도구’ 표현을 금지하거나 일괄 삭제한 변경이 아니다. 아이템별 덮어쓰기 없이 기존 공통 조건을 유지했다.

Hammer/HammerStone/BallPeenHammer 전체의 현재 Compact:

- KO: 금속 단조, 목공과 건축에 쓸 수 있다. 무기로도 쓸 수 있다.
- EN: It can be used for metal forging, woodworking and construction. It can also be used as a weapon.

세 항목의 KO/EN C/E를 모두 실제 대조했다. Hammer의 바리케이드 철거 추가 활용 등 차이를 포함해 전체4,210개 Expanded 레코드는 직전 결과와 완전히 같다. 텍스트 변경은 이3개 ×2언어 Compact6좌표뿐이다. 가구/부착물/목록의 추가 교정은 없다.

전체2,105개 정식 재생성, 현재 projection/tooltip binding과 두HTML 갱신 완료. descriptions SHA `8510f3003f7150ad034d83ef1496a2540b3fc5ac62acecb622d7c3bce7ba6ed3`; blocks SHA `e290c79b0f6d3b8738df5203926aa249309f8c14eaf6eebbed13e809a40ed455`(불변). 전문은 `Iris/build/description/composition/quality_review/hammer_direct/fulltext.txt`. 기존 consistency_review 및 전체 전문도 현재 출력으로 갱신했다. consistency-audit의 ca19 기준 누적 변경 수는 이제106개이며 이번 단계의 변경 수3개와 구분한다.

검증은 모두 exit0:

```powershell
uv run --project .\Iris\tooling python -I -B -m pytest --noconftest -c .\Iris\tooling\pyproject.toml .\Iris\build\description\v2\tests\test_layer3_composition.py::test_layer3_composition_contract .\Iris\build\description\v2\tests\test_layer3_description_composition.py::test_layer3_description_composition --basetemp .\.tmp\hammer-direct-pytest-01 -q -s --tb=short
uv run --project .\Iris\tooling python .tmp/prose/hammer-direct-audit.py
uv run --project .\Iris\tooling python .tmp/prose/review-five-audit.py
uv run --project .\Iris\tooling python .tmp/prose/review-five-menu.py
git -c core.whitespace=blank-at-eol,blank-at-eof,space-before-tab,cr-at-eol diff --check -- Iris/tooling/src/iris_tooling/domains/layer3/description_composition_results.py Iris/build/description/v2/tests/test_layer3_description_composition.py
```

pytest2passed34.49s. 세Compact쌍만변경/전체E동일 검사, HTML8,420원문 및886목록식별자/136disclosure+12inline 보존 검사, Browser/Wiki4,210상태·162표본 검증 통과. Lua 코드는 이번에 바꾸지 않았다. 패키징/설치/커밋/푸시 및 실제 게임 화면 검증은 하지 않았다.
