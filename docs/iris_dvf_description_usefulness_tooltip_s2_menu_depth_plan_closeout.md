# DVF 설명 실용성 / Tooltip S2 / Menu depth 실행 기록

2026-08-31. 상태: **partial — 기술서 Menu 표시 구현, 2,105개 전수 제안 판정 기록; 보류 273개 및 Layer 3/Tooltip 채택·생성·최종 검증 미완료**.

대상 계획: [implementation plan](iris_dvf_description_usefulness_tooltip_s2_menu_depth_plan.md).
이 기록은 이번 작업의 단일 closeout이자 미채택 내용 검토 기록이다. 새 validator, facts authority, approval registry, canonical audit ledger 또는 seal이 아니다.

## 실제 결과와 남은 범위

- 기술서 Menu presentation을 수정했다. `IrisWikiSections.renderLiteratureSection`이 기존 reader/assembler의 알려진 skill/level/count를 표시하고 Browser와 실제 Wiki panel이 이 함수를 사용한다. KO/EN label을 추가하고 기존 locale harness에 unknown bound 및 magazine 제외 사례를 보완했다. 기존 detail acceptance 3개와 Lua syntax 명령은 exit 0이다. 실제 화면은 미관찰이다. canonical facts/decisions/candidate, EN producer/output, current generation pointer, T1 owner, fixed/Recipe companion, QG authority binding은 변경하지 않았다. 문구 후보를 작성한 것을 Layer 3 제품 교정으로 세지 않는다.
- 저장소 내부의 predecessor/current 기준 귀속, 현재 입력 대조, 아래 exact item의 용도·KO/EN·Menu 후속 질문 검토를 수행했다. UI 번역 생성과 위 두 기존 검사만 실행했다. Layer 3 generation, finalize, package/install, PZ 화면 관찰은 실행하지 않았다.
- **2,105개 모두의 개별 제안 disposition/readiness·이유·후보/유지·Menu 상태를 마지막 절에 기록했다.** 최신 판정은 keep 291, revise 1,529, reduce 12, review_hold 273이다. 착용 446개의 새 core 후보 준비 뒤 남은 306개를 검토해 추가로 31개 수정 후보와 2개 안전한 정체성 keep을 준비했다. 현재 제안 readiness는 description_ready 1,792 / acquisition_only 40 / review_required 273이다. source 준비와 현행 채택·generation 미실행을 분리하며 전체 semantic acceptance 완료는 아니다.
- owner approval은 사용자 사전 승인으로 처리했다. 현재 차단 사유는 같은 owner approval의 재요청이 아니라 **명시적 filesystem 실행 경계와 현행 외부 생성/검증 계약의 충돌**이다.
- 현재 Menu depth의 unresolved actionable gap을 0이라고 주장하지 않는다. 후보 설명의 Tooltip 전파도 0이다. overall complete 또는 implemented_only가 아니다.

## 실행 경계

사용자는 현재 저장소와 계획이 명시한 경로만 허용하고, 명시되지 않은 외부 로컬 경로의 읽기·탐색·수정·전송을 금지했다. 계획은 외부 output과 installed producer를 요구하지만 이번 실행의 외부 절대 경로를 지정하지 않았다. [ENTRYPOINTS](../Iris/build/ENTRYPOINTS.md)는 repository-external output과 installed wheel을 요구한다. 이를 내부 임시 환경, source import, 새 wrapper 또는 guard 완화로 대체하지 않았다.

외부 내용을 읽지 않고 **내부 locator에서 확인한 문자열**은 다음과 같다. 존재 여부, 실제 설치 내용, hash 일치 또는 현재 사용 가능성은 확인하지 않았다.

| 내부 locator | 외부 경로 | 필요한 용도 / 현재 처리 |
|---|---|---|
| `Iris/validation/clean_checkout/authority/responsibility_refactor_environment_naming_v1.json` | `C:/Users/MW/PZ-N/e` | 현행 환경·installed tooling 읽기/실행. 접근하지 않음. source successor에 맞는 wheel/environment binding 여부는 별도 확인 필요 |
| 같은 environment locator | `C:/Users/MW/PZ-N/er/environment_receipt.json` | immutable environment receipt 읽기. 접근하지 않음 |
| 같은 environment locator | `C:/Users/MW/PZ-N/w/iris_tooling-0.1.0-py3-none-any.whl` | 정확한 producer wheel 읽기. 접근하지 않음 |
| `Iris/_docs/authority/iris_current_route_index.json` | `C:/Users/MW/Downloads/coding/PZ2/t3d1/a2/t1-final` | current predecessor handoff binding/rollback 참조. 접근하지 않음. 새 subject의 handoff로 재사용 불가 |
| 같은 route index | `C:/Users/MW/Downloads/coding/PZ2/t3d1/a2/t2-final` | predecessor T2 manifest/closeout 참조. 접근하지 않음. 새 subject의 validation으로 재사용 불가 |

신규 output의 짧고 얕은 **미승인 후보**는 `C:/Users/MW/PZ-U` 하나다. 이 경로는 제안만 했으며 열거·존재 확인·생성하지 않았다. 승인되는 경우 그 아래에서 같은 subject의 audit/correction ledger, generation/T1/T2/canonical 결과, 격리 candidate checkout, package/install을 contract 단위로 묶는다. 서로 다른 A/B 실행 경계는 유지하지만 검사마다 별도 workspace를 만들지 않는다. 기존 사용 설치본과 save는 제외한다. 경로를 이 문서에 적었다는 사실 자체는 접근 권한이 아니다.

차단되는 현행 command 단계는 `build layer3`의 external generation, `build/finalize tooltip-t1`, `build/finalize tooltip-t2`, receipt-bound `validate full` Run A/B와 comparator, package producer 및 격리 설치다. 파라미터/검사 membership은 ENTRYPOINTS와 기존 launcher가 계속 소유한다. 본 기록에는 실행하지 않은 command를 성공한 literal/receipt로 만들지 않는다.

## 기준 귀속 — read-only 관측

- 시작 HEAD: `54ab73dcec6160f6ee8d776096f6e013148588cb`; tree: `b9daf704a8b0f1ececea8e53786fa9ea733df60a`.
- 시작 시 untracked: 계획 문서와 `docs/dvf_b41_full_item_first_pass_2026-08-30/`. 해당 기존 자료는 수정하지 않았다.
- 계획 §4.2의 세 rendered payload hash가 현재 파일과 일치한다. exact universe는 각각 2,105이며 ordered set hash는 `122ca07c483ff8e4af9ef83bfb8d28c950802a124aba1668c234bce3477b2fdb`다.
- `028a3968… → dfdef534…`에서 empty→public은 보호된 12개와 정확히 같고, public→empty·universe added/removed·보호 집합 밖 entry delta는 없다. `dfdef534… → 05d76b51…`은 같은 12개 내용 교정이며 public membership 변화는 없다. 귀속은 계획 §4.2, DECISIONS의 existing-context 및 Build 41 correction, current candidate integration entries와 연결했다.
- 보호 집합: `Base.BarbedWire`, `Base.CarBatteryCharger`, `Base.Hinge`, `Base.Jack`, `Base.LeatherStrips`, `Base.LugWrench`, `Base.Paintbrush`, `Base.Pipe`, `Base.Scotchtape`, `Base.ScrapMetal`, `Base.TirePump`, `Base.Toolbox`. exact set hash는 계획에 있는 `aff222df71e1cdb6684ac9ee06cc19f4820ccc0d0f818a7961f7dba0200ded10`과 같다.
- current descriptor의 canonical input 7개 raw hash 및 기존 first-pass summary의 input 8개 hash가 모두 현재 파일과 일치한다. 같은 입력의 census/hash 검사를 반복하지 않았다.
- 독립 관측: KO public 2,084 / empty 21, EN chunk keys 2,084 및 KO public과 양방향 차집합 없음, owner core 1,314, empty-core 791, explicit owner absence 175, fixed top-level keys 2,280, companion keys 349 / concrete variants 781. Lua source 형태의 key 관측은 runtime lookup/decoder validation을 대신하지 않는다.
- JSON의 `Base.LemonGrass` / `Base.Lemongrass`를 보존하기 위해 case-sensitive `ConvertFrom-Json -AsHashtable`을 사용했다. 최초 일반 JSON conversion은 casing collision 오류로 폐기했다. 최초 unquoted Git tree 인수도 PowerShell에서 잘못 해석되어 폐기하고 `git rev-parse 'HEAD^{tree}'`로 tree를 읽었다. 이 조사 command들은 제품 validation PASS가 아니다.

이 범위에서 미귀속 predecessor entry delta는 발견하지 않았다. 다만 Change 1 전체의 producer/wheel, 외부 handoff, actual Menu/installed-subject binding까지 완료했다는 뜻은 아니다.

## 직접 추적한 교정 후보

아래 `new`는 모두 **미채택 초안**이다. frozen expected tuple, 실제 successor fact ID 또는 current input으로 발행하지 않았다. 기존 owner scalar/source identity는 `tooltip_t1_layer3_owner_input.json#entries/<FullType>`와 pointer-selected `role_material`에 그대로 남아 있다. 새 assertion의 source-bound fact successor와 KO/EN mapping을 기존 경로로 함께 채택해야 한다. source가 준비된 후보를 owner 승인 대기로 재분류하지 않는다.

### 탄약 상자

| exact item | old KO / EN | new KO / EN |
|---|---|---|
| `Base.223Box` | 장전 준비 작업에서 탄약을 상자나 클립에 담거나 꺼낼 때 다룬다 / Handled when putting ammunition into or taking it out of boxes and clips. | 상자를 열어 .223 탄약을 꺼낼 수 있다 / Open the box to take out .223 ammunition. |
| `Base.308Box` | 같은 old KO/EN | 상자를 열어 .308 탄약을 꺼낼 수 있다 / Open the box to take out .308 ammunition. |

각각 `scripts/recipes.txt:747`, `:756`의 exact input→result를 직접 읽었다. 상자를 clip이나 모든 탄약의 동일 역할로 일반화하지 않는다. Menu 질문은 “어떤 제작 항목으로 꺼내는가?”이며 기존 QG `uc.recipe.open_box_of_223_ammo`, `uc.recipe.open_box_of_308_ammo`가 관련 답이다. 실제 표시·전환은 `not_observed`다. S2에 수량·recipe 목록을 추가하지 않는다.

### 조리 재료

`Base.BakingSoda`:

- old KO: `조리 준비 작업에서 재료를 담거나 섞고 익히기 전에 다룰 때 쓴다`
- old EN: `Cookware used to hold or mix ingredients before cooking.`
- new KO: `일부 반죽과 튀김 요리에 넣는 재료다`
- new EN: `An ingredient used in some doughs and fried dishes.`

`scripts/recipes.txt:1010, 3861, 3872, 4335, 4366, 4397, 4428`의 BakingSoda input을 직접 대조했다. EN의 cookware 단정은 재료 역할과 맞지 않는다. 초안은 현실의 팽창·세척 효과를 주장하지 않는다. 상세한 음식 목록은 S2에 나열하지 않는다. Menu 질문 “어떤 요리에, 무엇과 함께 쓰는가?”의 답은 기존 7개 recipe와 각각의 재료/learn 조건이다. 그 데이터가 실제 Menu detail에 표시되는지는 미관찰이다.

### 건전지

`Base.Battery`:

- old KO: `전자 장비를 조립하거나 정비·분해하는 과정에서 다룬다`
- old EN: `Handled while assembling, maintaining, or dismantling electronic equipment.`
- new KO: `손전등 등 건전지를 사용하는 기기에 전원을 공급한다`
- new EN: `Supplies power to battery-operated devices such as flashlights.`

직접 읽은 범위는 `scripts/recipes.txt:599, 611, 623`의 `Rubberducky2`, `Torch`, `HandTorch`와 `lua/server/recipecode.lua:436–456`의 삽입 조건/usedDelta 전달이다. 자동차 배터리나 임의 전자기기로 확대하지 않는다. Menu의 “어디에 넣고 어떤 상태에서 교체하는가?”는 기존 삽입 recipe 및 `usedDelta == 0` 조건과 연결해야 한다. recipe ID 존재만으로 그 조건이 표시됐다고 할 수 없다. 조건 detail은 미확인 상태다.

### 목공 도구

`Base.Hammer`:

- old KO: `건축 준비 작업에서 자재를 가공하거나 맞출 때 쓴다`
- old EN: `Used to shape or fit materials while preparing construction work.`
- new KO 초안: `못을 사용하는 목공 구조물을 만드는 데 쓰는 도구다`
- new EN 초안: `A tool used to build wooden structures with nails.`

`scripts/items_weapons.txt:1101`의 Hammer tag와 `lua/client/BuildingObjects/ISUI/ISBuildMenu.lua`의 tag 선택, `buildMiscMenu`/`requireHammer` 및 `onWoodenCross`의 Plank/Nails 요구를 읽었다. 건축 가능성이 있다고 모든 건축·금속 작업을 지원한다고 하지 않는다. 기존 QG `uc.action.construction`은 관련 identity이지만 “어느 구조물과 재료/조건인가?”에 대한 구체 답 자체는 아니다. Menu detail 결손 여부는 아직 열려 있으며 수정 완료로 세지 않는다.

### 기술서

`Base.BookCarpentry1`:

- old KO: `학습 작업에서 기술이나 제작법을 익히려고 읽거나 참고할 때 본다`
- old EN: `Read or referenced to learn a skill or crafting recipe.`
- new KO: `적용 수준에서 읽으면 목공 경험치 획득 배율을 높이는 기술서다`
- new EN: `A skill book that increases Carpentry XP gain when read at the applicable level.`

`scripts/items_literature.txt:169`의 Carpentry / level 1 / two levels, `lua/server/XpSystem/XPSystem_SkillBook.lua`의 Carpentry→Woodwork, `ISReadABook.lua:30–58, 84–96`의 수준/Illiterate 조건과 독서 진행에 따른 배율 적용을 읽었다. 읽기 자체로 XP를 직접 받거나 recipe를 배운다는 문구로 바꾸지 않는다.

후속 질문은 “어느 수준에 적용되며 얼마나 읽어야 하는가?”다. `IrisItemFactReader`는 `skillTrained`, `level`, `levelCount`, `numberOfPages`를 읽고 assembler가 보존한다. 그러나 살펴본 current Browser/Wiki presentation에는 이 literature 필드를 출력하는 경로가 없다. 따라서 **필드가 존재해도 Menu의 답은 확보되지 않았다**. 이는 source inspection으로 찾은 presentation 결손 후보이며 화면 관찰 결과가 아니다. 정확한 적용 조건은 기존 허용 context/owner 경로 또는 승인된 Menu correction으로 전달해야 한다.

### 본문 없는 빗자루

`Base.Broom`:

- old S2 KO/EN: `null / null`; current public body도 없음.
- new KO 후보: `불탄 자리에 남은 재를 치우는 데 쓰는 도구다`
- new EN 후보: `A tool used to clear ashes from burned areas.`

`scripts/items_weapons.txt:2002`의 ClearAshes tag → `ISWorldObjectContextMenu.lua:104, 325, 521, 3060`의 nonbroken tool/탄 자리 sprite 선택·queue → `ISClearAshes.lua:perform`의 square object 제거를 직접 추적했다. “일반 바닥 청소”나 질병/위생 효과로 확대하지 않는다. current candidate의 empty core와 silent source는 그대로다. 새 source material을 owner 경로로 채택하지 않고 S2만 채우지 않는다.

Menu 질문은 “무엇을 어디서 치우며 어떤 도구 상태가 필요한가?”다. 기존 first-pass/current QG 조사에서는 positive usecase가 없었다. 읽은 동작 경로는 관련 QG/Menu correction의 근거 후보다. 정확한 owner admission 및 후속 답은 미구현이며 legitimate silence로 종결하지 않는다.

### 식재료 사과

`Base.Apple`:

- old KO: `조리나 식사 준비 작업에서 먹거나 나눠 먹을 때 쓴다`
- old EN: `Food used while preparing or eating a meal.`
- new KO 후보: `섭취하면 허기와 갈증을 줄일 수 있고 요리 재료로도 사용할 수 있다`
- new EN 후보: `Eating it can reduce hunger and thirst; it can also be used as a cooking ingredient.`

초기 과일/재료 역할 위주 초안은 기본 섭취 효과를 빠뜨려 위처럼 보완했다. `scripts/items_food.txt:1630`과 기존 `Iris/input/items_itemscript.json`의 **이 exact Apple**에 있는 `HungerChange=-16`, `ThirstChange=-7`을 근거로 한다. `ISEatFoodAction:perform/eat`은 선택한 food와 섭취 비율을 `character:Eat`에 전달하고, vanilla `ISInventoryPaneContextMenu`의 food delta 표시는 같은 hunger/thirst change와 비율을 사용하며 음수 thirst를 감소 방향으로 취급한다. 기존 source index도 이 필드를 consumption 판별 field로 소유한다. 이 관측은 새 health/food axis나 모든 음식의 효과 규칙을 만드는 것이 아니다. 수치와 항상 동일한 효과, 부패/조리/섭취량과 무관한 보장은 문구에 넣지 않는다. 기존 public field 의미와 소비 경로 이상의 독립 Java 재검증은 요구하지 않는다.

재료 역할은 exact EvolvedRecipe와 `scripts/evolvedrecipes.txt:107, 115`의 Bowl→Salad/FruitSalad를 읽었다. 이어 `ISInventoryPaneContextMenu.doEvorecipeMenu`, `onAddItemInEvoRecipe`의 eligible-item 선택과 queue, `ISAddItemInRecipe:isValid/perform`의 `getItemsCanBeUse`/`recipe:addItem` 호출까지 확인했다. Java 구현 내부와 실제 플레이 결과는 관찰하지 않았다. 단순 lexical hit를 동작 전체의 증거로 승격하지 않는다.

Menu 질문은 “어떤 요리에 어떻게 넣는가?”다. current QG positive와 `IrisRecipeIndexData`에는 Apple 연결을 찾지 못했다. 획득처나 hunger 수치는 이 질문의 답이 아니다. evolved relation의 기존 QG admission/결과 projection을 해결해야 하며, 표시 누락인지 source owner material 결손인지 최종 adjudication은 미완료다. QG 부재를 게임 조리 기능 부재로 바꾸지 않는다.

후속 원인 확인에서 Apple의 QG row에는 `consumption_food` 및 `consumption_displaycategory_food` exclusion이 있고 BookCarpentry1에는 `consumption_literature` exclusion이 있다. 이 exclusion은 식사/독서를 Right-click QG positive로 승격하지 않는 계약이지 Layer 3에 섭취 효과/독서 효과를 설명하지 못한다는 규칙이 아니다. Apple의 조리 relation은 별도 Recipe owner 경로로 다뤄야 하고, 기술서 수준/진행 조건은 Menu/context owner로 연결해야 한다. exclusion을 삭제하거나 느슨하게 만드는 식으로 gap을 메우지 않는다.

### 보존 및 보류 사례

- `Base.Toolbox`: current approved KO `도구나 기타 물건을 넣어 운반하는 휴대용 보관함이다.` / EN `A portable container for carrying tools or other items.`는 기본 쓰임을 전달한다. 이전 12개 승인 set의 이 문구를 고치지 않았다. 별도 동작/효율 설명을 억지로 추가하지 않는다.
- `Base.Bag_Schoolbag`: public body는 acquisition-only, current S2 owner entry 없음. raw Container / Capacity / Back 선언만으로 기존 `identity_fallback`을 core로 승격하지 않았다. ordinary container 동작·owner source admission을 더 추적해야 한다. 미검토 부분을 legitimate absence로 판정하지 않았다.
- `Base.Toothbrush`: old KO `이를 닦을 때 쓰는 칫솔이다` / EN `A toothbrush used to brush teeth.`. raw item 및 조사된 locator에 기능을 입증하는 행동 경로가 확인되지 않았다. 이를 모든 게임 경로의 부재 증명으로 바꾸지 않으며 “쓸모없다”로 교정하지 않았다. 새 core text는 미작성/미채택이다.

## 조리 문구 32개 — exact 역할을 구분한 추가 검토

같은 old KO 및 EN cookware 문구를 쓰지만 다음의 실제 역할은 다르다. 각 item의 raw definition과 해당 exact recipe input/result/keep 선언을 대조했다. 아래는 교정 방향 및 후속 질문의 **검토 기록**이며 최종 bilingual adjudication이나 전체 source callback 검증 완료가 아니다. 원본 source owner는 `scripts/recipes.txt`; current QG presentation을 Layer 3 source로 역사용하지 않는다.

| exact FullType | 확인한 역할 / 교정 방향 | Menu에 이어져야 할 답 |
|---|---|---|
| Base.BakingSoda | 일부 반죽·튀김 재료 | 위 7개 recipe 및 개별 조건 |
| Base.Bowl | 조리/분할 용기; 반죽 recipe에서는 keep 도구이기도 함 | food를 담는 recipe와 keep recipe를 혼동하지 않음 |
| Base.CannedBolognese | 개봉해 내용물을 쓰는 통조림 | Open Canned Bolognese / can-opener group |
| Base.CannedCarrots2 | 개봉 대상 | Open Canned Carrots / can-opener group |
| Base.CannedChili | 개봉 대상 | Open Canned Chili / can-opener group |
| Base.CannedCorn | 개봉 대상 | Open Canned Corn / can-opener group |
| Base.CannedCornedBeef | 개봉 대상 | Open Canned Corned Beef; 이 선언에는 can-opener keep 없음 |
| Base.CannedFruitBeverage | 과일 음료 통조림 개봉 | Open Canned Fruit Beverage / can-opener group |
| Base.CannedFruitCocktail | 개봉 대상 | Open Canned Fruit Cocktail / can-opener group |
| Base.CannedMilk | 연유 통조림 개봉 | Open Condensed Milk / can-opener group |
| Base.CannedMushroomSoup | 개봉 또는 냄비 수프 재료 | Open Canned Mushroom Soup / Make Pot of Soup |
| Base.CannedPeaches | 개봉 대상 | Open Canned Peaches / can-opener group |
| Base.CannedPeas | 개봉 대상 | Open Canned Peas / can-opener group |
| Base.CannedPineapple | 개봉 대상 | Open Canned Pineapple / can-opener group |
| Base.CannedPotato2 | 개봉 대상 | Open Canned Potato / can-opener group |
| Base.CannedSardines | 개봉 대상 | Open Canned Sardines; 이 선언에는 can-opener keep 없음 |
| Base.CannedTomato2 | 개봉 대상 | Open Canned Tomato / can-opener group |
| Base.EggCarton | 포장을 열어 달걀을 꺼냄 | Open Egg Carton / exact result 및 callback |
| Base.EmptyJar | 채소 병조림 용기 | Make Jar of …의 JarLid/채소/물/식초/설탕 |
| Base.Flour | 반죽·튀김 재료 | exact Flour input 또는 Flour group resolution |
| Base.Frog | 손질해 FrogMeat를 얻는 대상 | Slice Frog / sharp-knife group 또는 MeatCleaver |
| Base.GravyMix | 물과 함께 그레이비를 만드는 재료 | Make Gravy / Bowl·stirring utensil |
| Base.JarLid | 채소 병조림의 뚜껑 재료 | jar/채소 등과 함께 쓰는 input; 용기 자체와 구분 |
| Base.PancakeMix | 팬케이크 반죽 재료 | Make Pancake / 물·Bowl·utensil |
| Base.Pot | 수프를 담아 만드는 냄비 | Make Pot of Soup의 open/closed canned variants |
| Base.TinnedBeans | 개봉 또는 그릇에 담는 콩 통조림 | Open Canned Beans / Make Bowl of Beans |
| Base.TinnedSoup | 개봉 또는 냄비 수프 재료 | Open Canned Soup / Make Pot of Soup |
| Base.TunaTin | 개봉 대상 | Open Canned Tuna; 이 선언에는 can-opener keep 없음 |
| Base.Vinegar | 채소 병조림에 넣는 재료 | Make Jar of …; 현실의 세척/살균 효과를 추가하지 않음 |
| Base.WaterPot | 물이 담긴 냄비; 쌀/파스타 및 의료 recipe에 쓰임 | 조리와 bandage/rag 소독의 Heat 조건을 따로 확인 |
| Base.WaterSaucepan | 물이 담긴 소스팬; 역할은 exact 자체 input으로 확인 | WaterPot과 의료 recipe 소비량이 다르므로 복사 금지 |
| Base.Yeast | 빵/피자/케이크 반죽 재료 | exact recipe 및 learn 조건; 현실 발효 효과를 추정하지 않음 |

후속 검토에서 이 exact 32개에 대해 다음의 bilingual 초안까지 작성했다. old KO/EN은 위 공통 문구이며 source와 Menu 질문은 위 item별 표를 재사용한다. 소비 효과가 따로 확인되지 않은 물건에 hunger/thirst 감소를 복사하지 않는다. 이 목록은 source-bound authoring 초안이며 producer에 채택한 target set이 아니다.

| exact FullType | new KO 후보 | new EN 후보 |
|---|---|---|
| Base.BakingSoda | 일부 반죽과 튀김 요리에 넣는 재료다 | An ingredient used in some doughs and fried dishes. |
| Base.Bowl | 음식을 담거나 반죽을 섞는 데 쓰는 그릇이다 | A bowl used to hold food or mix dough. |
| Base.CannedBolognese | 개봉해 볼로네제 내용물을 꺼낼 수 있는 통조림이다 | A can opened to obtain its bolognese contents. |
| Base.CannedCarrots2 | 개봉해 당근을 꺼낼 수 있는 통조림이다 | A can opened to obtain its carrots. |
| Base.CannedChili | 개봉해 칠리를 꺼낼 수 있는 통조림이다 | A can opened to obtain its chili. |
| Base.CannedCorn | 개봉해 옥수수를 꺼낼 수 있는 통조림이다 | A can opened to obtain its corn. |
| Base.CannedCornedBeef | 개봉해 콘비프를 꺼낼 수 있는 통조림이다 | A can opened to obtain its corned beef. |
| Base.CannedFruitBeverage | 개봉해 과일 음료를 꺼낼 수 있는 통조림이다 | A can opened to obtain its fruit beverage. |
| Base.CannedFruitCocktail | 개봉해 과일 칵테일을 꺼낼 수 있는 통조림이다 | A can opened to obtain its fruit cocktail. |
| Base.CannedMilk | 개봉해 연유를 꺼낼 수 있는 통조림이다 | A can opened to obtain its condensed milk. |
| Base.CannedMushroomSoup | 개봉하거나 냄비에 담아 수프를 준비하는 데 쓰는 버섯 수프 통조림이다 | Canned mushroom soup opened or put in a pot to prepare soup. |
| Base.CannedPeaches | 개봉해 복숭아를 꺼낼 수 있는 통조림이다 | A can opened to obtain its peaches. |
| Base.CannedPeas | 개봉해 완두콩을 꺼낼 수 있는 통조림이다 | A can opened to obtain its peas. |
| Base.CannedPineapple | 개봉해 파인애플을 꺼낼 수 있는 통조림이다 | A can opened to obtain its pineapple. |
| Base.CannedPotato2 | 개봉해 감자를 꺼낼 수 있는 통조림이다 | A can opened to obtain its potatoes. |
| Base.CannedSardines | 개봉해 정어리를 꺼낼 수 있는 통조림이다 | A can opened to obtain its sardines. |
| Base.CannedTomato2 | 개봉해 토마토를 꺼낼 수 있는 통조림이다 | A can opened to obtain its tomatoes. |
| Base.EggCarton | 포장을 열어 달걀을 꺼낼 수 있다 | Open the carton to take out its eggs. |
| Base.EmptyJar | 채소를 병조림으로 담는 데 쓰는 빈 병이다 | An empty jar used to can vegetables. |
| Base.Flour | 반죽과 일부 튀김 요리에 들어가는 재료다 | An ingredient used in doughs and some fried dishes. |
| Base.Frog | 손질하면 개구리 고기를 얻을 수 있다 | It can be cut up to obtain frog meat. |
| Base.GravyMix | 물과 섞어 그레이비를 만드는 데 쓰는 재료다 | An ingredient mixed with water to make gravy. |
| Base.JarLid | 채소 병조림을 만들 때 빈 병과 함께 쓰는 뚜껑이다 | A lid used with an empty jar when canning vegetables. |
| Base.PancakeMix | 물과 섞어 팬케이크를 만드는 데 쓰는 재료다 | An ingredient mixed with water to make pancakes. |
| Base.Pot | 수프를 만들거나 담는 데 쓰는 냄비다 | A pot used to prepare or hold soup. |
| Base.TinnedBeans | 개봉하거나 그릇에 담아 콩 요리를 준비하는 데 쓰는 통조림이다 | Canned beans opened or put in a bowl to prepare a bean dish. |
| Base.TinnedSoup | 개봉하거나 냄비에 담아 수프를 준비하는 데 쓰는 통조림이다 | Canned soup opened or put in a pot to prepare soup. |
| Base.TunaTin | 개봉해 참치를 꺼낼 수 있는 통조림이다 | A can opened to obtain its tuna. |
| Base.Vinegar | 채소 병조림을 만드는 데 들어가는 재료다 | An ingredient used to can vegetables. |
| Base.WaterPot | 쌀이나 파스타 요리를 준비하는 데 쓰는 물이 든 냄비다 | A water-filled cooking pot used to prepare rice or pasta dishes. |
| Base.WaterSaucepan | 쌀이나 파스타 요리를 준비하는 데 쓰는 물이 든 소스팬이다 | A water-filled saucepan used to prepare rice or pasta dishes. |
| Base.Yeast | 빵 등의 반죽을 만드는 데 들어가는 재료다 | An ingredient used to make doughs such as bread dough. |

따라서 “cookware”를 하나의 다른 공통 EN 문장으로 교체하는 것만으로 이 32개를 해결할 수 없다. 모든 통조림에 can opener가 필요하다는 일괄 assertion도 근거와 맞지 않는다. Recipe variants가 구체 이름을 보여줄 수 있으므로 fixed S3의 generic 문구를 actual Alt의 표시 결함이라고 단정하지 않는다.

## 학습 문구 87개 — 기술서와 제작법·지식 구분

현재 공통 문구는 읽어서 기술이나 제작법을 익힌다는 범위로 XP 배율과 제작법 학습을 섞는다. 각 exact item의 SkillTrained/LvlSkillTrained/NumLevelsTrained/TeachedRecipes를 대조했다. 아래 기술서 60개의 KO/EN은 미채택 후보다. source는 scripts/items_literature.txt의 각 exact item 선언, lua/server/XpSystem/XPSystem_SkillBook.lua의 skill binding 및 lua/client/TimedActions/ISReadABook.lua:30–58,84–96이다. 같은 Literature 타입만으로 잡지에 이 문구를 전파하지 않는다.

| exact FullType set | new KO 후보 | new EN 후보 |
|---|---|---|
| Base.BookCarpentry1, Base.BookCarpentry2, Base.BookCarpentry3, Base.BookCarpentry4, Base.BookCarpentry5 | 적용 수준에서 읽으면 목공 경험치 획득 배율을 높이는 기술서다 | A skill book that increases Carpentry XP gain when read at the applicable level. |
| Base.BookCooking1, Base.BookCooking2, Base.BookCooking3, Base.BookCooking4, Base.BookCooking5 | 적용 수준에서 읽으면 요리 경험치 획득 배율을 높이는 기술서다 | A skill book that increases Cooking XP gain when read at the applicable level. |
| Base.BookFarming1, Base.BookFarming2, Base.BookFarming3, Base.BookFarming4, Base.BookFarming5 | 적용 수준에서 읽으면 농사 경험치 획득 배율을 높이는 기술서다 | A skill book that increases Farming XP gain when read at the applicable level. |
| Base.BookFishing1, Base.BookFishing2, Base.BookFishing3, Base.BookFishing4, Base.BookFishing5 | 적용 수준에서 읽으면 낚시 경험치 획득 배율을 높이는 기술서다 | A skill book that increases Fishing XP gain when read at the applicable level. |
| Base.BookTrapping1, Base.BookTrapping2, Base.BookTrapping3, Base.BookTrapping4, Base.BookTrapping5 | 적용 수준에서 읽으면 덫 사냥 경험치 획득 배율을 높이는 기술서다 | A skill book that increases Trapping XP gain when read at the applicable level. |
| Base.BookBlacksmith1, Base.BookBlacksmith2, Base.BookBlacksmith3, Base.BookBlacksmith4, Base.BookBlacksmith5 | 적용 수준에서 읽으면 대장장이 경험치 획득 배율을 높이는 기술서다 | A skill book that increases Blacksmithing XP gain when read at the applicable level. |
| Base.BookMetalWelding1, Base.BookMetalWelding2, Base.BookMetalWelding3, Base.BookMetalWelding4, Base.BookMetalWelding5 | 적용 수준에서 읽으면 금속 용접 경험치 획득 배율을 높이는 기술서다 | A skill book that increases Metalworking XP gain when read at the applicable level. |
| Base.BookFirstAid1, Base.BookFirstAid2, Base.BookFirstAid3, Base.BookFirstAid4, Base.BookFirstAid5 | 적용 수준에서 읽으면 응급처치 경험치 획득 배율을 높이는 기술서다 | A skill book that increases First Aid XP gain when read at the applicable level. |
| Base.BookElectrician1, Base.BookElectrician2, Base.BookElectrician3, Base.BookElectrician4, Base.BookElectrician5 | 적용 수준에서 읽으면 전기공학 경험치 획득 배율을 높이는 기술서다 | A skill book that increases Electrical XP gain when read at the applicable level. |
| Base.BookForaging1, Base.BookForaging2, Base.BookForaging3, Base.BookForaging4, Base.BookForaging5 | 적용 수준에서 읽으면 채집 경험치 획득 배율을 높이는 기술서다 | A skill book that increases Foraging XP gain when read at the applicable level. |
| Base.BookMechanic1, Base.BookMechanic2, Base.BookMechanic3, Base.BookMechanic4, Base.BookMechanic5 | 적용 수준에서 읽으면 차량정비 경험치 획득 배율을 높이는 기술서다 | A skill book that increases Mechanics XP gain when read at the applicable level. |
| Base.BookTailoring1, Base.BookTailoring2, Base.BookTailoring3, Base.BookTailoring4, Base.BookTailoring5 | 적용 수준에서 읽으면 재봉술 경험치 획득 배율을 높이는 기술서다 | A skill book that increases Tailoring XP gain when read at the applicable level. |

각 family의 1~5권은 성장 레벨 1–2, 3–4, 5–6, 7–8, 9–10을 선언한다. 이를 현재 플레이어 레벨 범위로 표시하지 않는다. ISReadABook은 현재 perk level + 1과 책의 bounds를 비교한다. Menu에서는 성장 레벨과 별개로 독서 배율이 적용되는 현재 레벨 0–1, 2–3, 4–5, 6–7, 8–9를 표시한다. 문맹 조건과 읽은 분량에 따른 배율도 같은 실행 경로에 존재한다. 이 후보는 기술 레벨 직접 상승이나 XP 직접 지급, 새 제작법 학습을 주장하지 않는다.

`Base.BookBlacksmith1`, `Base.BookBlacksmith2`, `Base.BookBlacksmith3`, `Base.BookBlacksmith4`, `Base.BookBlacksmith5`의 위 문구는 채택 준비 후보에서 **보류**한다(`review_hold / review_required` 제안). 선언과 SkillBook binding만으로 현재 Build 41에서 사용하는 perk/경험치 경로가 확정됐다고 하지 않는다. 이 상태와 일치하도록 Menu의 지원 skill label에서 Blacksmith를 제외했다. 자연 스폰을 못 보았기 때문에 기능이 없다고 판정한 것이 아니며, 기능 부재를 공개 문구로 출력하지 않는다. 나머지 기술서 55개와 이 5개의 준비 상태를 합치지 않는다.

기술서 Menu 결손은 reader/assembler 이후 presentation 누락이었다. IrisWikiSections.renderLiteratureSection을 추가하고 IrisBrowserDetail 및 실제 IrisWikiPanel 호출부를 연결했다. 기존 known 값만 표시하며, skill이 없거나 지원하지 않는 경우는 이 섹션을 만들지 않는다. range가 unknown이면 범위를 만들지 않고 range-dependent 조건도 표시하지 않는다. S2, QG exclusion/selection, runtime item-method reader 경계는 그대로다. EN/KO Iris_*.txt와 기존 생성기의 IrisTranslationData.lua가 같은 label을 제공한다. 최초 focused/syntax 성공 뒤 받은 가독성·Blacksmith 피드백을 반영했으므로 그 이전 exit 0을 수정 후 subject의 최종 결과로 소급하지 않는다. 실제 화면과 full canonical 검증은 여전히 미완료다.

제작법 잡지 27개는 TeachedRecipes 선언과 ISReadABook:perform의 ReadLiterature 호출을 연결한다. 아래 표는 source-bound 초안이며 기존 QG learn/requirement와 Menu의 실제 학습목록 표시는 별도다. 주석 처리된 옛 직접 recipe-list 조작 코드를 실행 증거로 쓰지 않는다.

| exact FullType | new KO 후보 | new EN 후보 |
|---|---|---|
| Base.CookingMag1 | 케이크·파이와 쿠키 반죽 제작법을 배우는 잡지다 | A magazine that teaches recipes for cake, pie and cookie doughs. |
| Base.CookingMag2 | 빵 반죽·비스킷과 피자 제작법을 배우는 잡지다 | A magazine that teaches recipes for bread dough, biscuits and pizza. |
| Base.ElectronicsMag1 | 원격 조종기 제작법을 배우는 잡지다 | A magazine that teaches how to craft remote controllers. |
| Base.ElectronicsMag2 | 타이머 제작과 부착 방법을 배우는 잡지다 | A magazine that teaches how to craft and attach timers. |
| Base.ElectronicsMag3 | 동작 감지기 부착 방법을 배우는 잡지다 | A magazine that teaches how to attach motion sensors. |
| Base.ElectronicsMag4 | 발전기 연결과 수리에 필요한 지식을 배우는 잡지다 | A magazine that teaches knowledge needed to connect and repair generators. |
| Base.ElectronicsMag5 | 원격 격발 장치 제작과 부착 방법을 배우는 잡지다 | A magazine that teaches how to craft and attach remote triggers. |
| Base.EngineerMagazine1 | 소음 발생 장치 제작법을 배우는 잡지다 | A magazine that teaches how to craft a noise maker. |
| Base.EngineerMagazine2 | 연막탄 제작법을 배우는 잡지다 | A magazine that teaches how to craft a smoke bomb. |
| Base.FarmingMag1 | 작물의 흰가루병과 해충을 처리하는 분무액 제작법을 배우는 잡지다 | A magazine that teaches recipes for mildew and pest treatment sprays for crops. |
| Base.FishingMag1 | 낚싯대 제작과 수리 방법을 배우는 잡지다 | A magazine that teaches how to craft and repair fishing rods. |
| Base.FishingMag2 | 통발 제작과 철사 회수 방법을 배우는 잡지다 | A magazine that teaches how to craft a fishing net trap and reclaim its wire. |
| Base.HerbalistMag | 야생 열매와 버섯의 독성을 구별하는 지식을 배우는 잡지다 | A magazine that teaches how to identify poisonous wild berries and mushrooms. |
| Base.HuntingMag1 | 올가미 덫 제작법을 배우는 잡지다 | A magazine that teaches how to craft a snare trap. |
| Base.HuntingMag2 | 나무 상자 덫과 막대 덫 제작법을 배우는 잡지다 | A magazine that teaches how to craft wooden box and stick traps. |
| Base.HuntingMag3 | 상자 덫과 철창 덫 제작법을 배우는 잡지다 | A magazine that teaches how to craft box and cage traps. |
| Base.MechanicMag1 | 일반 차량의 정비 작업에 필요한 지식을 배우는 잡지다 | A magazine that teaches knowledge required for work on standard vehicles. |
| Base.MechanicMag2 | 상용 차량의 정비 작업에 필요한 지식을 배우는 잡지다 | A magazine that teaches knowledge required for work on commercial vehicles. |
| Base.MechanicMag3 | 고성능 차량의 정비 작업에 필요한 지식을 배우는 잡지다 | A magazine that teaches knowledge required for work on performance vehicles. |
| Base.MetalworkMag1 | 금속 벽과 지붕 제작법을 배우는 잡지다 | A magazine that teaches how to build metal walls and roofs. |
| Base.MetalworkMag2 | 금속 보관함 제작법을 배우는 잡지다 | A magazine that teaches how to build metal containers. |
| Base.MetalworkMag3 | 금속 울타리 제작법을 배우는 잡지다 | A magazine that teaches how to build metal fences. |
| Base.MetalworkMag4 | 금속판 가공법을 배우는 잡지다 | A magazine that teaches recipes for making metal sheets. |
| Base.SmithingMag1 | 금속 식기와 조리 용기 제작법을 배우는 잡지다 | A magazine that teaches recipes for metal cutlery and cookware. |
| Base.SmithingMag2 | 못·경첩과 작은 금속 도구 제작법을 배우는 잡지다 | A magazine that teaches recipes for nails, hinges and small metal tools. |
| Base.SmithingMag3 | 여러 금속 도구와 용기 제작법을 배우는 잡지다 | A magazine that teaches recipes for metal tools and containers. |
| Base.SmithingMag4 | 탄약·주형과 일부 금속 무기 제작법을 배우는 잡지다 | A magazine that teaches recipes for ammunition, molds and some metal weapons. |

Generator knowledge의 사용처는 ISWorldObjectContextMenu.lua:1416,1430의 연결·수리 조건이고 Herbalist는 ISInventoryPane.lua:1934의 actual poison power에 따른 이름 구분이다. Mechanics는 scripts/vehicles의 각 install/uninstall recipes requirement다. 어느 것도 기술 경험치 배율 잡지라는 뜻이 아니다. Smithing recipe 선언/학습 후보와 실제 제작 가능 화면의 관찰을 구분한다. 현재 literature reader에는 TeachedRecipes 자체가 없으므로 기술서 레벨 표시 보완이 이 27개의 학습목록 질문까지 해결한 것은 아니다.

## 의료 아이템 — 게임 내 효과와 일반 처치 문구 구분

추가로 의료 항목의 raw item 선언과 HealthPanel/TimedAction을 추적했다. 아래는 게임 내 동작에 대한 미채택 후보이며 현실 의료 조언이나 게임 효과의 전수 검증이 아니다.

| exact item | old S2 KO / EN | new KO / EN 후보 | source 및 Menu 질문 |
|---|---|---|---|
| Base.AlcoholWipes | 의료 처치에 쓰이는 물품이다 / An item used in medical treatment. | 상처를 소독하는 데 쓰는 소모품이다 / A consumable used to disinfect wounds. | `scripts/newitems.txt:2205` AlcoholPower → `ISHealthPanel.HDisinfect` → `ISDisinfect:perform` alcohol-level 갱신. “어느 상처에 어떻게 적용하는가?”에 current positive QG 답이 확인되지 않음 |
| Base.Disinfectant | null / null (Menu는 acquisition-only) | 상처를 소독하는 데 쓰는 소독제다 / A disinfectant used to disinfect wounds. | `scripts/newitems.txt:2189` 및 같은 HDisinfect 경로. identity_fallback을 근거 없이 core로 바꾸지 않으며 source-bound successor 필요 |
| Base.Bandage | 의료 처치에 쓰이는 물품이다 / An item used in medical treatment. | 상처에 감아 사용하는 붕대다 / A bandage applied to wounds. | `scripts/newitems.txt:1607` CanBandage 및 `ISApplyBandage:perform` SetBandaged. 기존 QG의 Disinfect Bandage는 “상처에 어떻게 감는가?”의 답을 대신하지 않음 |
| Base.SutureNeedle | 의료 처치에 쓰이는 물품이다 / An item used in medical treatment. | 깊은 상처를 봉합하는 데 쓰는 바늘이다 / A needle used to stitch deep wounds. | `ISHealthPanel.HStitch`의 exact SutureNeedle 선택, deep-wound/glass 조건 → `ISStitch:perform` setStitched. 기존 `uc.action.wound_suturing`은 관련 identity이며 조건 표시/consumer는 미관찰 |
| Base.Splint | null / null (Menu는 acquisition-only) | 골절 부위를 고정하는 데 쓰는 부목이다 / A splint used to immobilize a fracture. | `ISHealthPanel.HSplint`의 Splint item/골절/신체 부위 선택 → `ISSplint:perform` setSplint. 머리·몸통은 적용 대상에서 제외하는 조건을 Menu에 보존해야 함. current positive QG가 비어 있어 관련 후속 답은 미구현 |

AlcoholWipes/Disinfectant의 소독을 좀비 감염 치료·예방 보장으로 확대하지 않는다. 붕대의 부착 상태를 즉시 회복·감염 방지 보장으로 바꾸지 않는다. dirty bandage 계열은 `ISApplyBandage`에서 life를 0으로 처리하는 별도 분기가 있으므로 동일 문구 일괄 전파 대상이 아니다.

`Base.PlantainCataplasm`은 exact 항목 → HealthPanel poultice handler → `setPlantainFactor`까지 읽었으나 factor가 실제 회복에 미치는 엔진 효과를 확인하지 않았다. `Base.Pills`, `Base.PillsAntiDep`, `Base.PillsBeta`, `Base.PillsSleepingTablets`, `Base.PillsVitamins`도 `ISTakePillAction`의 `JustTookPill` 호출만으로 개별 효과·시간·부작용을 확정하지 않았다. 이름이나 현실 약효로 새 문구를 채우지 않고 해당 assertion을 미확인으로 남긴다. 이 보류는 item의 게임 용도 부재나 legitimate silence 판정이 아니다.

## 추가 내용 검토 — 음식·착용물·혼합 역할

current primary 문구 176개(빈 문구 포함)의 exact member 목록을 읽고, 주요 문구 그룹의 raw 선언·기존 recipe input/keep 관계를 대조했다. 아래는 당시의 구체적 설계 결과이며 최신 개별 제안 판정은 마지막 절에 있다. source가 없거나 assertion 검토가 끝나지 않은 항목을 `keep`으로 채우지 않았다. 전수 제안 disposition/readiness 작성과 canonical source adjudication 완료는 구분한다.

음식 공통 문구 317개와 acquisition-only 음식 88개는 item별 `HungerChange`, `ThirstChange`, `EvolvedRecipe`, 조리·교체·독성 선언을 대조했다. 조합 규칙의 안전한 재사용 범위는 다음처럼 분리한다. 이는 first-pass를 authority로 채택한 것이 아니며 source-bound successor 발행 전의 내용 설계다.

| exact 사례 / 범위 | 새 KO / EN 후보 또는 필요한 구분 | 근거와 후속 질문 |
|---|---|---|
| Base.Apple, Base.Banana, Base.Orange, Base.Pear | 섭취하면 허기와 갈증을 줄일 수 있고 요리 재료로도 사용할 수 있다 / Eating it can reduce hunger and thirst; it can also be used as a cooking ingredient. | 각 exact item의 음수 HungerChange/ThirstChange와 EvolvedRecipe. 어떤 요리인지는 해당 evolved recipe 관계로 답해야 함 |
| Base.Crisps, Base.Crisps2, Base.Crisps3, Base.Crisps4 | 먹으면 허기를 줄일 수 있는 간식이다 / A snack that can reduce hunger when eaten. | 각 HungerChange=-15. 갈증 감소·조리 재료·영양 우열을 추가하지 않음 |
| Base.DriedBlackBeans, Base.DriedChickpeas, Base.DriedKidneyBeans, Base.DriedLentils, Base.DriedSplitPeas, Base.DriedWhiteBeans | 수프·스튜 등에 넣는 말린 콩류 재료다 / Dried legumes used in dishes such as soups and stews. | 각각 EvolvedRecipe Soup/Stew/RicePot/PastaPot, ThirstChange=60. 물을 공급하는 음식이라는 일괄 문구 금지 |
| Base.Rice, Base.Pasta | 쌀 요리를 준비하는 데 쓰는 재료다 / An ingredient used to prepare rice dishes. ; 파스타 요리를 준비하는 데 쓰는 재료다 / An ingredient used to prepare pasta dishes. | 각각 Place Rice/Pasta in Cooking Pot/Saucepan input, ThirstChange=60. 냄비·물·조리 조건은 Menu recipe 답 |
| Base.CocoaPowder, Base.Pepper, Base.Salt, Base.Soysauce, Base.Wasabi | 각각 음료/요리에 넣는 재료와 양념 역할로 분리 | 양수 ThirstChange가 있으므로 과일과 같은 갈증 감소 문구를 전파하지 않음. 수치 자체는 Menu detail 역할 |
| Base.BaitFish | 낚시 미끼 용도와 음식 속성을 분리해 추가 판단 | `DangerousUncooked`, Food 선언만으로 일반 간식 대표 문구를 만들지 않음. 낚시 bait 선택 근거 채택 필요 |
| Base.Chicken, Base.Steak, Base.FishFillet, Base.FrogMeat, Base.Rabbitmeat, Base.Smallanimalmeat, Base.Smallbirdmeat, farming.Bacon, farming.BaconBits, farming.BaconRashers | 조리해 먹거나 요리 재료로 사용하는 고기다 / Meat used for cooking and as an ingredient in dishes. | 각 IsCookable/DangerousUncooked 및 EvolvedRecipe. Cooked 조건이 붙은 샌드위치·샐러드와 그 외 요리를 분리; 모든 recipe에 생것/익힌 것 조건을 동일하게 붙이지 않음 |
| Base.MushroomGeneric1–7 | 일반 음식 효과와 독성 조건을 별도로 유지 | `OnEat_WildFoodGeneric`은 실제 poison power가 양수이면 food-sickness를 증가시킨다(`recipecode.lua:1041`). FullType만으로 무독성 보장 금지 |
| Base.Maggots2 | Maggots와 별도 위험 assertion 판단 | exact item의 PoisonPower=3. 이름·공통 먹기 문구만으로 두 item을 동일 취급하지 않음 |
| Base.Comfrey, Base.Plantain | 각각 컴프리 찜질약 / 질경이 찜질약을 만드는 재료다 / An ingredient used to make a comfrey / plantain poultice. | `scripts/newitems.txt:2049,2027`, Make Comfrey/Plantain Poultice input. 허기 감소 선언이 없어 일반 음식 효과를 추가하지 않음. 완성 약재의 회복 효과와 원료 역할도 분리 |
| Base.LemonGrass / Base.Lemongrass | 별도 exact identity 유지; 후자의 source 공백을 전자로 메우지 않음 | 기존 D5 collision disposition 보존. case-insensitive join 금지 |
| Base.BaguetteDough, Base.PancakesCraft, Base.BreadSlices | 반죽/준비물과 조리 후 결과를 분리 | 각각 ReplaceOnCooked Baguette/PancakesRecipe/Toast. 지금 완성 음식이라는 assertion이나 조리 불필요 주장을 만들지 않음 |
| Base.Beer, Base.Beer2, Base.Beverage, Base.Beverage2, Base.WineInGlass 및 CannedBellPepper 등 병조림 | 생성 callback을 통하는 내용물과 정적 기본 값을 구분 | 선언에 Hunger/Thirst 값이 없다는 이유로 효과가 없다고 하거나 임의 완성값을 채우지 않음. 현재 acquisition-only 보존; 새 core·조건은 해당 source owner 채택 전 |

이 405개를 같은 후보 문장으로 바꾸지 않았다. 음식 표의 영양 수치를 실사용 item의 부패·조리·부분 섭취 상태와 무관한 고정 효과로 발행하지 않는다. 보존 기간이나 조리 온도를 새로운 S2 assertion으로 늘리지 않는다. 현재 Recipe owner의 일반 recipe index에 evolved recipe가 없으면 그 결손은 실제 게임에서 조리할 수 없다는 뜻이 아니다. 이번 목적에 해당하는 Menu relation 보완은 아직 actionable gap으로 남는다.

착용 identity 문구 448개(액세서리 194, 의류 254)는 `Type`, `BodyLocation`, 방어·보온 선언을 item별로 열람했다. 현재 primary origin은 identity_fallback이고 공개 본문은 대부분 acquisition-only이므로 그 identity 문구를 그대로 core로 승격하지 않는다. GasMask/DustMask 이름에서 독가스 방호를, HazmatSuit/NBCmask에서 감염 면역을, Fireman 옷에서 화염 면역을 추론하지 않는다. `Base.DigitalWatch`, `Base.Earrings`, `Base.Necklacepearl`, `Base.Ring`, `Base.WeddingRing_Man`, `Base.WeddingRing_Woman`은 이 목록에서도 Type=Normal이므로 주변 Clothing 항목의 착용 기능을 전파하지 않는다. 값이 없는 방어 필드는 무방어라는 음성 assertion의 근거도 아니다. 이 검토는 정당한 S2 absence의 새로운 일괄 승인이나 448개 keep 판정이 아니다.

| exact 사례 | old assertion의 문제 | new KO / EN 후보와 source |
|---|---|---|
| Base.AssaultRifle, Base.AssaultRifle2, Base.HuntingRifle, Base.VarmintRifle | 소총과 소총 보관 장비를 하나의 용도로 혼합 | 사격에 쓰는 소총이다 / A rifle used for shooting. `scripts/items_weapons.txt:6083,6173,5209,5119`의 Ranged/AmmoType. 탄약·탄창 호환성은 Menu 질문 |
| Base.RifleCase1, Base.RifleCase2, Base.RifleCase3 | 위와 같은 공통 문구 | 물건을 넣어 운반하는 소총용 케이스다 / A rifle case used to carry items. `scripts/newBags.txt:188,205,222` Container/Capacity=7. 소총만 넣을 수 있다고 제한하지 않음 |
| Base.SpearCrafted 및 SpearBreadKnife/SpearButterKnife/SpearFork/SpearHandFork/SpearHuntingKnife/SpearIcePick/SpearKnife/SpearLetterOpener/SpearMachete/SpearScalpel/SpearScissors/SpearScrewdriver/SpearSpoon | 완성된 무기를 창 끝 보강 재료로만 설명 | 찌르는 근접 공격에 쓰는 창이다 / A spear used for thrusting melee attacks. 각 Weapon/Spear 선언. reclaim recipe의 원료 역할이 완성 창의 기본 역할을 대체하지 않음 |
| Base.HuntingKnife 등 위 그룹의 분리된 부착 도구 | 완성 창과 같은 문구이지만 도구 자체 용도가 다름 | knife/도구의 기존 기본 용도와 spear attachment input을 분리. 전체 27개를 같은 창 문구로 바꾸지 않음 |
| Base.FishingRodBreak | 다른 장비를 수리하는 도구처럼 표현 | 낚싯줄을 달아 다시 사용할 수 있는 낚싯대다 / A fishing rod that can be restored by attaching a line. `items_weapons.txt:2536` 및 Fix Fishing Rod input; 결과·대체 줄/낚싯바늘 조건은 recipe detail |
| Base.PlasticCup | 물건 보관 가방과 같은 문구 | 물을 담는 데 쓰는 컵이다 / A cup used to hold water. exact CanStoreWater/WaterSource→PlasticCupWater 선언. 일반 inventory Container로 오인하지 않음 |
| Base.PaperclipBox | 문서 작성·수정 문구 | 상자를 열어 종이클립을 꺼낼 수 있다 / Open the box to take out paperclips. Open Box of Paperclip input/result |
| Base.GardenSaw | 자재를 가공하거나 맞춘다는 일반 문구 | 통나무를 톱질해 판자를 만드는 데 쓰는 도구다 / A tool used to saw logs into planks. Saw Logs2 keep GardenSaw/input Log/result Plank |

차량 item은 선언상 Normal이라는 이유만으로 무용도 판정을 하지 않는다. `scripts/vehicles/template_*.txt`의 itemType 및 install/uninstall 조건이 source다. 1/2/3 suffix를 임의 품질 순위로 해석하지 않으며, 브레이크·배기·서스펜션·타이어·엔진 부품의 서로 다른 목적을 “주행 부품 복구” 하나로 동결하지 않았다. Moveable의 `WorldObjectSprite`가 있어도 모든 장비를 실제 가전 기능으로 설명할 수 없다. 장식/배치 설명을 바꾸려면 sprite-bound 용도 근거가 필요하다. `VHS_Home`, `VHS_Retail`, `Disc_Retail`의 MediaCategory가 없는 일반 VHS/Disc와도 구분한다.

명확한 기존 기본 역할을 강제 변경할 필요가 없는 사례로 Nails, FishingLine, Twine/Wire, Stone, BlowTorch, PropaneTank, ScrewsBox, NailsBox, BoxOfJars, BrokenFishingNet 및 보호된 Toolbox를 검토했다. 기존 admitted input과 recipe input/keep/result가 각각 건축 재료·낚싯줄·덫 재료·도구·충전 연료·개봉/회수 역할을 설명한다. 레시피 목록 전체나 수량을 S2에 더하는 것으로 변경 수를 늘리지 않는다. 이 사례의 유지 판단도 모든 기본 용도/actual Menu 답을 전수 검증했다는 뜻은 아니다.

`Base.Radio`(Normal), `Base.NoiseMaker` 및 `Base.Bag_PistolCase`(이번 locator의 raw item 연결 없음), sports/toy·생활 잡동사니의 현실 기능 문구는 별도 근거가 필요하다. source 연결이 없거나 plain Normal이라는 이유로 그 기능이 없다고 단정하지 않았다. 원본 기능 확인 전에는 새 문구/음성 assertion을 발행하지 않는다. 이것을 이미 해결된 Menu N/A나 legitimate_unresolved의 일괄 집합으로 세지 않는다.

## 후속 item별 판정 — 운반·읽기·청소의 실제 역할

이 절은 외부 생성 차단과 독립적으로 진행한 내용 판정이다. 아래 항목은 전부 이번 source 검토를 거친 `revise` 제안이며, 새 core/condition의 기존 owner 채택 후 `description_ready`로 만드는 경로 B에 해당한다. 현재 준비 상태를 일괄 성공으로 바꾸는 선언은 아니다. 새 fact identity와 registered source lineage, KO/EN successor binding은 아직 발행하지 않았다.

| exact FullType set | old KO / EN | new KO / EN 후보 |
|---|---|---|
| Base.AmmoStrap_Bullets | 탄약 휴대에 쓰는 장비다 / Equipment used to carry ammunition. | 산탄이 아닌 탄약을 사용하는 총기의 장전 속도를 높이는 착용 장비다 / Worn gear that increases reload speed for guns using non-shotgun ammunition. |
| Base.AmmoStrap_Shells | 위와 같은 old | 산탄총 탄약을 사용하는 총기의 장전 속도를 높이는 착용 장비다 / Worn gear that increases reload speed for guns using shotgun shells. |
| Base.Book, Base.ComicBook | 독서 작업에서 읽거나 훑어보며 내용을 살필 때 본다 / Read or skimmed to examine its contents. | 읽으면 지루함·스트레스·불행을 줄일 수 있는 읽을거리다 / Reading material that can reduce boredom, stress and unhappiness. |
| Base.HottieZ, Base.Magazine, Base.MagazineCrossword1, Base.MagazineCrossword2, Base.MagazineCrossword3, Base.MagazineWordsearch1, Base.MagazineWordsearch2, Base.MagazineWordsearch3, Base.Newspaper, Base.TVMagazine | 위와 같은 독서 old | 읽으면 지루함과 스트레스를 줄일 수 있는 읽을거리다 / Reading material that can reduce boredom and stress. |
| Base.Doodle, Base.Journal | 위와 같은 독서 old | 필기구가 있으면 내용을 적어 보관할 수 있는 기록물이다 / A document in which notes can be written and kept using a writing tool. |
| Base.Coffee2 | 음료 섭취 작업에서 마시거나 나눠 마실 때 쓴다 / Used to drink or share a beverage. | 커피 음료를 만드는 데 넣는 재료다 / An ingredient used to prepare coffee drinks. |
| Base.Bleach | 일반 소비 작업에 쓰는 생활 소모품이다 / A household consumable used in ordinary consumption. | 청소 도구와 함께 혈흔을 지우는 데 쓰는 유독성 표백제다 / Toxic bleach used with cleaning tools to remove blood stains. |
| Base.Mop | 생활 관리 작업에서 몸과 주변을 닦고 정리하거나 실내에 필요한 소모품을 챙길 때 다룬다 / Handled while cleaning the body or surroundings and gathering household consumables. | 표백제와 함께 혈흔을 지우는 데 쓰는 도구다 / A tool used with bleach to remove blood stains. |
| Base.BathTowel, Base.DishCloth | 위와 같은 생활 관리 old | 몸의 물기를 닦거나 표백제와 함께 혈흔을 지우는 데 쓴다 / Used to dry the body or to remove blood stains with bleach. |
| Base.Broom | null / null | 재를 치우거나 표백제와 함께 혈흔을 지우는 데 쓰는 도구다 / A tool used to clear ashes or remove blood stains with bleach. |
| Base.Cigarettes | 기호품으로 소비하며 기분을 달랠 때 쓴다 / Consumed recreationally to improve mood. | 흡연가라면 스트레스와 불행을 줄일 수 있지만 비흡연가의 식중독 수치를 높인다 / For smokers, it can reduce stress and unhappiness; for non-smokers, it increases food sickness. |

- AmmoStrap 두 item은 `scripts/clothing/clothing_others.txt:773,784`의 exact ClothingItem/ReloadFast tag와 `lua/client/TimedActions/ISReloadWeaponAction.lua:69–103`을 연결했다. 장착 상태와 주 손 총기의 AmmoType 대응 시 ReloadSpeed에 1.15를 곱한다. **전체 장전 시간이 15% 감소한다**는 assertion은 하지 않는다. `Base.AmmoStraps` WeaponPart와 다른 identity이며 새 효과를 그 item으로 전파하지 않는다. Menu 질문은 대상 탄약·착용 조건이며 추가 보관 용량으로 대신 답할 수 없다.
- 일반 읽을거리 12개는 `scripts/items_literature.txt`의 각 exact BoredomChange/StressChange/UnhappyChange를 읽었고 기존 `ISReadABook:update`와 `ReadLiterature` 경로를 재사용했다. Doodle/Journal에는 이 효과 선언이 없으므로 제외했다. 두 기록물의 `CanBeWrite`, `PageToWrite`와 `ISInventoryPaneContextMenu.lua:760–768,2097–2115`의 필기구 태그/잠금/페이지 저장을 연결했다. Menu 질문 “무엇이 있어야 쓸 수 있는가?”에는 필기구와 잠금 조건이 필요하다.
- Coffee2는 `scripts/items_food.txt:4877`의 HotDrink 계열 EvolvedRecipe 입력이며 ThirstChange=60이다. 마시기만 하면 갈증을 줄이는 완성 음료처럼 표현하지 않는다. FatigueChange=-50도 선언되어 있으나 이를 현재 prepared S2 tuple에 자동 추가하지 않았다. 기본 재료 역할과 효과 assertion의 별도 채택 범위를 구분한다.
- 청소 5개는 `ISWorldObjectContextMenu.canCleanBlood/doCleanBlood:4268–4300`의 혈흔/표백제/도구 선택과 `ISCleanBlood:perform`의 bleach 소비·square.removeBlood를 추적했다. BathTowel/DishCloth는 `ISInventoryPaneContextMenu:130,715,1968`, `ISDryMyself:update`의 body wetness 감소에도 연결된다. **BathTowelWet/DishClothWet, CleaningLiquid/Soap/Sponge를 같은 기능으로 전파하지 않는다.** Broom의 이 표는 앞서 재 제거만 기록한 후보를 보완하며 새 후보 개수를 중복 합산하지 않는다. Menu에는 표백제·도구·혈흔 조건이 필요하다. 일반 잡동사니 소비 exclusion을 삭제하는 것으로 이 답을 만든 척하지 않는다.
- Bleach의 유독성은 `scripts/items_food.txt:2859`의 Poison=true/PoisonPower=120 선언에 따른다. 음수 ThirstChange만으로 유익한 음료라고 설명하지 않는다. 신체·상처 소독이나 감염 치료 용도는 주장하지 않는다.
- Cigarettes는 `scripts/items.txt:620` OnEat binding과 `recipecode.lua:1010–1037`의 Smoker trait 분기를 직접 읽었다. 비흡연가의 불행 증가를 처리하던 주석 코드는 현재 효과 근거로 쓰지 않는다. Menu에는 trait별 조건을 남기며 현실의 흡연 효능을 설명하는 문구로 확대하지 않는다.

탄약 16개도 상자/낱알을 분리했다. 8개 상자는 `scripts/recipes.txt:710–781`의 exact Open Box input→result이고, 낱알 8개는 `scripts/items_weapons.txt` 각 총기의 AmmoType 선언과 대응한다. 수량은 S2에 추가하지 않는다.

| exact FullType | new KO 후보 | new EN 후보 |
|---|---|---|
| Base.223Box | 상자를 열어 .223 탄약을 꺼낼 수 있다 | Open the box to take out .223 ammunition. |
| Base.308Box | 상자를 열어 .308 탄약을 꺼낼 수 있다 | Open the box to take out .308 ammunition. |
| Base.556Box | 상자를 열어 .556 탄약을 꺼낼 수 있다 | Open the box to take out .556 ammunition. |
| Base.Bullets38Box | 상자를 열어 .38 Special 탄약을 꺼낼 수 있다 | Open the box to take out .38 Special ammunition. |
| Base.Bullets44Box | 상자를 열어 .44 Magnum 탄약을 꺼낼 수 있다 | Open the box to take out .44 Magnum ammunition. |
| Base.Bullets45Box | 상자를 열어 .45 Auto 탄약을 꺼낼 수 있다 | Open the box to take out .45 Auto ammunition. |
| Base.Bullets9mmBox | 상자를 열어 9mm 탄약을 꺼낼 수 있다 | Open the box to take out 9mm ammunition. |
| Base.ShotgunShellsBox | 상자를 열어 산탄총 탄약을 꺼낼 수 있다 | Open the box to take out shotgun shells. |
| Base.223Bullets, Base.308Bullets, Base.556Bullets, Base.Bullets38, Base.Bullets44, Base.Bullets45, Base.Bullets9mm, Base.ShotgunShells | 해당 탄종을 사용하는 총기의 장전에 쓰는 탄약이다 | Ammunition used to load guns that accept this ammunition type. |

게임 source의 `.556` 표기를 임의로 현실 탄약 명칭으로 바꾸지 않았다. 낱알의 후속 질문 “어떤 총기와 탄창에 맞는가?”는 AmmoType/MagazineType owner 관계가 필요하며, 상자를 여는 Recipe relation으로 대신 충족하지 않는다.

위 일부 신규 Right-click 질문은 current source index에 identity가 없고 current capability allowlist에도 그대로 추가할 수 없다. `rightclick_capability_allowlist_v1.md`의 닫힌 7개 목록을 완화하지 않았다. 기존 owner가 허용하는 core/context의 source-bound 조건 또는 기존 QG projection 범위에서 답을 채택해야 한다. source가 확인됐다는 이유로 새 capability/interaction을 만들거나, 허용되는 교정 경로를 정하지 않은 상태에서 해당 gap을 해결 또는 N/A로 세지 않는다.

## 농사·낚시·덫 — 무본문/획득-only 행의 source-bound 후보

이 항목들은 현재 source가 없다는 이유로 포기한 것이 아니라, 기존 primary에 반영되지 않은 실제 작동 근거를 확인한 경우다. 아래는 `revise` 및 owner 채택 뒤 `description_ready` 제안이며 현행 absence/readiness를 직접 덮어쓰지 않았다. 새 S2 presence는 T1/T2 successor에서 따로 검증해야 한다.

| exact FullType set | new KO 후보 | new EN 후보 | 근거 / Menu 질문 |
|---|---|---|---|
| Base.Fertilizer, Base.CompostBag | 작물의 다음 성장 단계까지 걸리는 시간을 줄이는 데 쓰는 비료다 | Fertilizer used to shorten the time to a crop's next growth stage. | ISFarmingMenu의 exact item 선택 → ISFertilizeAction → SPlantGlobalObject:fertilize. 살아 있는 식물/현재 시비 횟수 조건, 과다 사용 시 rottenThis를 Menu에서 구분 |
| farming.GardeningSprayMilk | 작물의 흰가루병 수준을 낮추는 데 쓰는 분무액이다 | A spray used to reduce mildew in crops. | ISFarmingMenu:228–266,439–440 → cureMildew의 mildewLvl 감소. 해충·다른 병 전체 치료로 일반화하지 않음 |
| farming.GardeningSprayCigarettes | 작물의 해충 수준을 낮추는 데 쓰는 분무액이다 | A spray used to reduce flies affecting crops. | ISFarmingMenu:234–295,447–448 → cureFlies의 fliesLvl 감소. 사용량/대상 상태는 Menu 조건 |
| Base.TrapBox, Base.TrapCrate, Base.TrapCage, Base.TrapSnare | 미끼와 함께 설치해 토끼나 다람쥐를 잡는 데 쓰는 덫이다 | A baited trap used to catch rabbits or squirrels. | TrapDefinition의 rabbit/squirrel.traps exact keys → STrapGlobalObject:checkForAnimal. 미끼·지역·시간·플레이어 근접/스트리밍·신선도 조건으로 포획 성공을 보장하지 않음 |
| Base.TrapStick | 미끼와 함께 설치해 새를 잡는 데 쓰는 덫이다 | A baited trap used to catch birds. | bird.traps의 exact TrapStick. 포유류 덫의 대상/미끼를 전파하지 않음 |
| Base.TrapMouse | 미끼와 함께 설치해 쥐를 잡는 데 쓰는 덫이다 | A baited trap used to catch mice and rats. | mouse/rat.traps의 exact TrapMouse. 모든 작은 동물 포획으로 일반화하지 않음 |
| Base.FishingNet | 물에 설치해 미끼용 작은 물고기를 잡는 데 쓰는 통발이다 | A fishing net trap placed in water to catch bait fish. | ISWorldObjectContextMenu의 물 타일/FishingNet 선택 → fishingNet.checkTrap:73–88의 BaitFish 결과. 대기시간·파손 가능성은 Menu detail, 무조건 포획/큰 물고기 주장 금지 |
| Base.BaitFish | 낚싯대 낚시에 미끼로 쓰는 작은 물고기다 | A small fish used as bait when fishing with a rod. | fishing_properties의 exact BaitFish lure → ISFishingAction:getFishByLure의 실제 item:getType 비교. 음식 그룹에서 분리; 허기 감소만으로 기본 용도를 대신하지 않음 |
| Base.FishingTackle, Base.FishingTackle2 | 낚싯대 낚시에 쓰는 인공 미끼다 | An artificial lure used when fishing with a rod. | newitems exact items와 fishing_properties lure → 같은 선택 경로. lure별 대상/소모·파손 조건은 별도 |
| Base.FishingRod, Base.FishingRodTwineLine, Base.CraftedFishingRod, Base.CraftedFishingRodTwineLine | 미끼를 달아 물고기를 잡는 데 쓰는 낚싯대다 | A fishing rod used with bait to catch fish. | items_weapons exact FishingRod tags → predicateFishingRodOrSpear/getFishingLure → ISFishingAction. 제작품·일반 낚싯대의 파손 후 결과 차이를 보존 |

시비는 SPlantGlobalObject.lua:339–351에서 nextGrowing 감소와 과다 사용의 부패 분기가 직접 확인된다. S2에 성장 시간의 고정 감소량이나 수확량 증가·병 치료를 추가하지 않는다. 분무액 두 종류의 감소는 같은 파일의 cureMildew/cureFlies로 확인되지만 `farming.GardeningSprayFull`로 전파하지 않는다. 이 generic Full 항목의 실제 역할은 별도 `review_hold / review_required` 제안이다.

덫은 `lua/server/Traps/TrapDefinition.lua`의 exact trap/animal/bait 관계와 `STrapGlobalObject.lua:237–275`를 연결했다. 숫자만 읽고 포획 확률을 합산해 보장하거나, live state를 읽어 효율 추천을 하지 않는다. 위 기본 목적은 source로 준비됐지만 Iris Menu에 모든 대상 미끼·조건이 표시된 것은 아니다.

낚시의 `getFishByLure`에는 재귀 선택이 있다. 이번에는 source를 읽었을 뿐 게임 함수를 시험 실행하지 않았고, 이를 새로운 테스트나 현재 작업의 무한루프 수정 과제로 확대하지 않았다. `fishingNet.checkTrap`의 실제 반환 item은 BaitFish이며 단순한 이름 번역으로 통발 대상을 추정하지 않았다.

## 남은 혼합 역할의 추가 판정

아래도 current fact 채택이 아닌 correction design이다. `revise`는 기존 owner 절차로 해당 source를 채택한 뒤의 `description_ready` 제안과 구분한다. `review_hold / review_required`는 기능이 없다는 판정이 아니다. first-pass의 raw 선언은 조사 locator로만 사용했고 새 동작 주장은 아래 원본 파일에서 확인한 범위로 제한했다.

| exact item/set | disposition / KO·EN 제안 또는 유지 이유 | 관련 source와 Menu 후속 질문 |
|---|---|---|
| Base.Torch, Base.HandTorch | revise: 건전지를 사용해 주변을 비추는 손전등이다 / A battery-powered flashlight used to illuminate the surroundings. | scripts/items.txt:1252 및 newitems.txt:4336의 LightDistance/LightStrength/UseBattery, 앞서 확인한 건전지 삽입/제거 recipe. 분해 가능한 대상이라는 설명만으로 기본 조명 기능을 대신하지 않음. 건전지 교체 조건은 Menu 질문 |
| Base.LightBulb, Base.LightBulbBlue, Base.LightBulbCyan, Base.LightBulbGreen, Base.LightBulbMagenta, Base.LightBulbOrange, Base.LightBulbPink, Base.LightBulbPurple, Base.LightBulbRed, Base.LightBulbYellow | revise: 교체 가능한 조명에 끼워 사용하는 전구다 / A bulb used in lights that accept replacement bulbs. | ISWorldObjectContextMenu:894–915의 LightBulb prefix 선택 → onLightBulb → ISLightActions:performAddLightBulb. getCanBeModified 및 기존 전구 없음 조건. 조명 개조의 전기 기술 5 조건을 전구 교체에 잘못 붙이지 않음 |
| Radio.CDplayer | revise: 녹음된 CD를 재생해 듣는 기기다 / A device used to play recorded CDs. | scripts/items_radio.txt:253–278의 AcceptMediaType=0, RWMMedia:91의 recorded-media/type 일치. 일반 Base.Disc에 같은 주장을 전파하지 않음 |
| Radio.RadioRed | revise: 라디오 방송을 듣거나 녹음된 CD를 재생하는 기기다 / A radio used to listen to broadcasts or play recorded CDs. | items_radio:285–310의 수신/TwoWay=false/AcceptMediaType=0. 주파수·전원·매체 호환 조건을 Menu에서 확인해야 함 |
| Radio.RadioBlack | revise: 주파수를 맞춰 라디오 방송을 듣는 기기다 / A radio used to tune in to broadcasts. | items_radio:313–336. CD 기능이 명시된 RadioRed에서 이 item으로 복사하지 않음 |
| Radio.WalkieTalkie1, Radio.WalkieTalkie2, Radio.WalkieTalkie3, Radio.WalkieTalkie4, Radio.WalkieTalkie5, Radio.HamRadio1, Radio.HamRadio2 | revise: 주파수를 맞춰 무선 신호를 송수신하는 기기다 / A two-way radio used to transmit and receive on a tuned frequency. | items_radio 각 exact item의 TwoWay=true 및 TransmitRange, RWMMicrophone:45의 getIsTwoWay 조건. 단순 분해 대상 문구와 구분. 숫자별 송신 범위를 다른 기기에 전파하지 않음 |
| Radio.TvAntique | revise: TV 방송을 시청하는 기기다 / A television used to watch broadcasts. | items_radio:369–391의 IsTelevision=true. VHS를 지원하는 다른 TV와 구분 |
| Radio.TvBlack, Radio.TvWideScreen | revise: TV 방송을 보거나 녹화된 VHS를 재생하는 기기다 / A television used to watch broadcasts or play recorded VHS tapes. | items_radio:393–441의 IsTelevision/AcceptMediaType=1, RWMMedia의 exact media type 일치. 매체 내용별 기술 획득을 모든 테이프의 기본 효과로 추가하지 않음 |
| Base.BarBell | revise: 바벨 컬 운동에 사용하는 운동기구다 / Exercise equipment used for barbell curls. | FitnessExercises.lua:36–45의 exact item, ISFitnessAction의 exerciseRepeat 경로. 힘 상승량·최적 운동·성공 보장 주장은 추가하지 않음 |
| Base.DumbBell | revise: 덤벨 프레스와 바이셉스 컬 운동에 사용하는 운동기구다 / Exercise equipment used for dumbbell presses and biceps curls. | FitnessExercises.lua:46–66의 exact item. 일반 스포츠 소품·악기 전체에 운동이나 연주 기능을 전파하지 않음 |
| Base.Hairgel | keep: 모양을 정돈하는 기본 용도가 이미 명확함 | ISCharacterScreen:434–438 및 ISCutHair:61의 특정 Mohawk 선택·소모 조건. 모든 머리 모양에 필요하다고 바꾸지 않음 |
| Base.HairDyeBlack, Base.HairDyeBlonde, Base.HairDyeBlue, Base.HairDyeGinger, Base.HairDyeGreen, Base.HairDyeLightBrown, Base.HairDyePink, Base.HairDyeRed, Base.HairDyeWhite, Base.HairDyeYellow | keep: 머리색을 바꾸는 기본 용도 명확 | 각 exact HairDye 선언, ISDyeHair:perform의 hair/beard color 설정 및 Use. 수염 염색은 별도 detail로 전달 가능하지만 새 S2 변경을 강제하지 않음 |
| Base.Razor | keep: 면도 용도 명확 | ISCharacterScreen의 predicateRazor 및 beard 선택/queue. 전투 피해나 다른 의료 효과를 추가하지 않음 |
| Base.Comb, Base.Cologne, Base.Perfume, Base.Toothpaste, Base.Toothbrush, Base.Leash | review_hold / review_required 제안 | 각 current primary는 현실 용도를 게임 행동처럼 읽게 할 수 있으나 이번에 해당 게임 기능의 source를 결속하지 못함. 검색 미발견으로 기능 부재·정당한 silence를 선언하지 않음 |
| Base.BackgammonBoard, Base.Bricktoys, Base.CardDeck, Base.CheckerBoard, Base.ChessBlack, Base.ChessWhite, Base.Dice, Base.GamePieceBlack, Base.GamePieceRed, Base.GamePieceWhite, Base.PokerChips, Base.Yoyo | review_hold / review_required 제안 | exact Normal 선언과 current 놀이 문구 사이의 gameplay assertion이 미결속. 게임 플레이·지루함 감소를 추정하지 않음 |
| Base.Bag_ALICEpack, Base.Bag_ALICEpack_Army, Base.Bag_BigHikingBag, Base.Bag_DuffelBag, Base.Bag_DuffelBagTINT, Base.Bag_FannyPackFront, Base.Bag_FoodCanned, Base.Bag_FoodSnacks, Base.Bag_GolfBag, Base.Bag_MedicalBag, Base.Bag_Military, Base.Bag_NormalHikingBag, Base.Bag_Satchel, Base.Bag_Schoolbag, Base.Bag_ShotgunBag, Base.Bag_ShotgunDblBag, Base.Bag_ShotgunDblSawnoffBag, Base.Bag_ShotgunSawnoffBag, Base.Bag_ToolBag | primary 표현 keep 제안: 담아 운반하는 용도가 명확함. 현재 identity_fallback/empty-core는 그대로 유지 | 각 exact Container/Capacity 선언을 읽었다. 문구의 실용성과 S2 eligibility는 독립. 이름으로 내용물 제한을 만들거나 identity primary를 자동 core로 승격하지 않음. 실제 public body가 acquisition-only인 문제까지 해결했다는 뜻은 아님 |

차량의 배터리·연료탱크·좌석/적재·주행 부품·패널/창문도 exact 선언을 다시 읽어 동일 그룹 내 역할 차이를 구분했다. VehicleType 1/2/3은 성능 등급이 아니며 MaxCapacity는 실제 상태와 무관한 일률적 보장 수치가 아니다. source 상한을 지키면서도 모든 부품의 current “정비 작업에서 다룸” 문구를 실용적이라고 일괄 keep하지 않는다. weapon part의 MountOn/PartType 및 탄창 AmmoType은 실제 호환 질문에 필요한 데이터지만 이를 Menu에서 확인했다는 관측은 없다.

이 시점의 대표 항목 검토 이후, 마지막 절에 2,105개 전수 제안 판정표를 추가했다. source successor의 canonical old/new tuple·owner admission은 미발행이며 보류 사유는 각 행에 남겼다. 이를 검사나 receipt를 추가해 해결할 문제로 취급하지 않는다.

## 후속 조합 규칙 연구에 재사용할 수 있는 관측

아직 채택·검증된 교정 결과가 아니라 위 미채택 후보의 구조 분석이다. 현재 작업을 조합기 재설계로 확대하지 않는다.

| 표현 구조 | 적용에 필요한 사실 조건 | 일반화하면 안 되는 예외 |
|---|---|---|
| 개봉 → 내용물 확보 | exact item이 개봉 recipe의 input이고 result가 확인됨 | 상자/clip 혼용, 모든 통조림의 opener 필요를 추정하지 않음 |
| 재료 → 활동/요리 종류 | 해당 recipe의 실제 input 역할과 범위 확인 | cookware, keep 도구, 원료, 완성 음식은 분리; 현실 효과를 덧붙이지 않음 |
| 도구 → 대상에 대한 동작 | exact tag/type 선택 → callback → 결과 변화 연결 | 빗자루의 재 제거를 일반 청소로 확장하지 않음 |
| 독서 → 적용 수준의 XP 배율 | 해당 SkillBook binding, 수준 조건, 실행되는 배율 갱신 경로 | magazine/knowledge token, XP 직접 획득, 비활성 콘텐츠는 별도 |
| 기기 소모품 → 기능 공급 | exact 입력/대상과 charge 전달 등의 실행 근거 | 전자 부품 전체나 자동차 배터리에 전파하지 않음 |

공통 문장 모양만 추출해서는 부족하다. `facts.primary_use` 및 adopted candidate를 실제 생성·채택하는 경로에 사실 조건과 예외가 연결되어야 한다. profile만 바꾸거나 기존 candidate를 다시 패키징하는 것으로 semantic 개선을 선언할 수 없다. 후속 작업은 위 old/new·source·Menu 질문 기록을 재사용할 수 있으며 별도 schema나 검증 authority를 만들 필요는 없다.

## Validation ceiling 및 남은 실행

| 축 | 이번 실행의 상태 |
|---|---|
| read-only 기준 귀속 | 위 exact 파일/입력/집합 비교만 수행. formal PASS 아님 |
| Layer 3 전수 usefulness audit | 제안 판정 2,105개 작성; 최신 273개 보류. 착용 후보 446개 및 후속 33개 해소와 미실행 채택을 분리. semantic acceptance incomplete |
| source-bound bilingual 후보 | 마지막 절의 exact item별 후보/앞 절 참조 또는 유지·보류 처리. canonical 채택/전체 translation acceptance 아님 |
| generation / T1 strict / T2 fixed / matching companion | blocked, 미실행. 기존 세트 보존 |
| canonical regression / inspect / full propagation | blocked, 미실행. 최종 채택 subject 없음; 검사 수를 늘리기 위한 predecessor suite도 실행하지 않음 |
| 기술서 Menu focused / syntax | 아래 두 명령 exit 0. 실제 게임 화면이나 전체 Menu gap 해소를 인증하지 않음 |
| package / isolated install | blocked, 미실행 |
| actual Menu / Alt / PZ 화면 | not_observed, incomplete |

최초 Menu 구현의 두 검사도 exit 0이었으나, 그 뒤 성장 레벨/현재 독서 레벨 구분과 Blacksmith 제외를 수정했다. 최초 결과는 수정 후 코드의 근거로 재사용하지 않았다. 마지막 코드 수정과 번역 재생성이 끝난 뒤 같은 두 기존 검사를 한 묶음으로 다시 실행했고 모두 exit 0이었다. 두 실행 모두 첫 반환에서 종료해 장기 실행·중단은 없었다. 같은 subject에서 추가 confidence만을 위한 반복은 하지 않았다.

| 실제 command literal | 종료 / 결과 | 한계 |
|---|---|---|
| `uv run --no-project --offline python .\Iris\build\tools\pipeline\build_iris_translation_data.py` | 최초 exit 0, 149 keys/locale | 수정 전 생성. no-project 경고는 프로젝트가 없다는 알림. 이후 결과로 대체됨 |
| `uv run --offline python .\Iris\build\tools\pipeline\build_iris_translation_data.py` | 최종 생성 exit 0, 147 keys/locale | UI 번역의 기존 producer. validation suite가 아니며 Layer 3/EN producer를 대체하지 않음 |
| `uv run --offline python .\Iris\build\description\v2\tests\test_iris_detail_view_model_acceptance.py` | 최종 exit 0, 기존 3 tests OK (0.307s) | standalone reader/model/locale harness 및 source guards. PZ/Kahlua UI 관찰 아님. 최초 수정 전 결과는 0.164s |
| `powershell -ExecutionPolicy Bypass -File .\tools\check_lua_syntax.ps1` | 최종 exit 0, 154 Lua files OK | 기존 script의 default roots. Python/semantic/installed payload 검증 아님 |

Java/JS/Python 제품 코드는 변경하지 않았다. 새 독립 테스트 파일·검사기·중간 proof tree·receipt를 생성하지 않았다. 자료 탐색에서 잘못된 경로/glob이나 출력 잘림이 있었던 범위는 해당 결과를 complete evidence로 사용하지 않았다.

남은 작업은 마지막 절 273개 보류의 명시된 sprite/source/조건/identity 관계 해결, 준비된 exact KO/EN·Menu correction의 기존 owner 경로 채택, 일관된 generation/EN→strict T1→T2 fixed/companion 전파, 허용된 실행 경계에서의 최소 필수 validation, 격리 package/install과 최소 대표 PZ 관찰이다. source가 준비된 후보를 채택 미실행만으로 자료 부족으로 되돌리지 않는다. 실제 관찰은 자동 harness로 대체할 수 없으며 stale predecessor receipt를 새 subject에 소급 적용하지 않는다.

bare Public Text Quality PASS, semantic-quality acceptance, full Menu parity, RTC, DVF freeze, Publish Boundary, release/Workshop readiness 또는 deployment는 주장하지 않는다.

## 2,105개 exact item의 미채택 제안 판정

이 절은 위 후속 조사 뒤 작성한 **전수 item별 authoring 기록**이다. 기존 exact universe를 재사용했으며 새 census·validation·receipt·canonical ledger를 생성하지 않았다. 최신 판정은 keep 291, revise 1,529, reduce 12, review_hold 273이다. 제안 readiness는 description_ready 1,792, acquisition_only 40, review_required 273이다. 착용 446개 준비 및 뒤이은 33개 보류 해소를 반영했으며, 현행 body/core 열과 제품 입력은 변경하지 않았다.

**미판정 item 행은 없지만 전수 semantic acceptance는 완료되지 않았다.** 각 행의 근거는 원문 선언, 기존 승인 사실, 앞 절의 직접 동작 추적 중 기록된 수준에 한정된다. 각 item의 모든 handler나 Java/PZ 실행을 읽고 검증했다고 주장하지 않는다. 미열람·미확정인 동작 관계는 해당 행의 보류 이유/후속 질문으로 남겨 두었으며 keep·legitimate silence·기능 부재로 치환하지 않았다. source-bound 후보가 준비된 행은 owner 승인 대기로 재분류하지 않는다.

- `현행`은 앞서 관측한 public/empty body 및 core/no-core의 보존 상태다. 제안 readiness나 문구가 실제 현행 owner entry를 변경했다는 뜻이 아니다. acquisition_only·no-core를 수정만으로 자동 승격하지 않는다.
- `disposition / readiness`는 **제안**이다. description_ready는 해당 문구의 확인된 역할을 기존 source owner로 채택할 준비 방향이며 새 fact ID·expected tuple·T1 admission 완료가 아니다. review_hold는 유지 승인도 부정적 기능 판정도 아니다.
- old KO/EN은 위 기준 generation `dvf33-05d76b51…`의 exact item과 `Iris/build/description/v2/data/tooltip_t1_layer3_owner_input.json#entries/<FullType>`, current pointer-selected role_material을 참조한다. 기존 first-pass item_audit/source_evidence는 locator이며 validation authority가 아니다.
- C/M 번호는 이 문서에서 반복되는 후보와 후속 질문을 줄이기 위한 참조다. 아래 C의 `같은 절`, `§학습`, `§후속 item별 판정`, `§농사·낚시·덫`, `§남은 혼합 역할`은 위 같은 FullType 행의 KO/EN/조건을 가리킨다. 별도 스키마·규칙 registry·proof artifact가 아니다.
- Menu의 `not_observed`는 실제 게임 화면 미관찰이다. `actionable_gap`은 기존 source/owner/presentation 조사에서 남은 구체적 질문이며 자동으로 N/A가 되지 않는다. 기술서의 표시 코드 구현과 화면 미관찰을 분리한다.

후속 원문 검토로 기존 후보를 좁힌 사례: `Muffintray_Biscuit`, `BakingTray_Muffin`, `BakingTray_Muffin_Recipe`는 `CantEat=TRUE`라 직접 섭취 후보를 철회했다. 머핀은 cooked 조건의 분리 후보, 비스킷 틀은 분리 경로 미확정 hold다. `Watermelon`도 자르기/쪼개기를 거친다. `SackCabbages/Carrots/Onions/Potatoes`는 Container 선언이며 SackProduce 식품과 구분한다. `Base.MetalDrum`은 기존 world drum 기능과 재고 item binding을 바로 동일시하지 않고 hold로 남겼다. 비활성 forge 건설 route를 모든 기존 forge/world action의 부재로 확대하지 않았다.

### 기본 착용 재판정 — 후보 준비와 현행 채택 분리

기존 447개 착용 hold에서 core 유무를 게임 내 기본 착용 사실의 충분성 기준으로 삼은 판정은 철회한다. exact Clothing/BodyLocation 선언과 공통 실행 경로를 연결해 446개를 **revise / description_ready인 새 source-bound core 후보**로 작성했다. 일반 Wear 425개와 추가 Wear 메뉴의 동일 FullType 선택 21개를 구분했다. 현재 no-core/admission은 보존하며, 남은 것은 기존 owner 경로 채택·generation 실행이지 착용 근거 부족이나 owner 재승인 요청이 아니다.

- 일반 경로: `lua/client/ISUI/ISInventoryPaneContextMenu.lua:127,685,1292,2233,2263`에서 Clothing 선택 → 미착용 시 Wear → onWearItems/wearItem → `ISWearClothing` queue. `lua/client/TimedActions/ISWearClothing.lua:9,68`은 inventory 소지, 중복 착용 여부와 비어 있지 않은 Clothing BodyLocation을 확인해 `setWornItem`을 적용한다. 각 행의 슬롯은 `lua/shared/NPCs/BodyLocations.lua`의 Human 선언과 연결한다.
- 추가 경로: ClothingExtraSubmenu가 있는 21개는 일반 doWearClothingMenu가 return하므로 별도로 다뤘다. `ISInventoryPaneContextMenu.lua:3664–3704`의 extra menu는 현재 FullType을 선택할 수 있고 `ISClothingExtraAction`을 queue에 넣는다. `lua/client/TimedActions/ISClothingExtraAction.lua:9,48`은 inventory 소지 후 해당 FullType을 만들어 같은 BodyLocation에 `setWornItem`한다. 다른 좌우·방향·후드 변형으로 바꿔야만 기본 착용이 가능하다고 주장하지 않는다.
- `Base.Male_Undies`만 **review_hold / review_required**로 남긴다. `scripts/clothing/clothing_shoes.txt:33`에 Clothing/UnderwearInner와 `OBSOLETE=TRUE`가 함께 선언되어 정상 B41에서 이 exact item 및 슬롯을 사용할 수 있는지 미확정이다. no-core 또는 외부 생산 미실행 때문이 아니며 기능 부재도 단정하지 않는다.
- Normal 소품 6개와 Container 장비는 이 Clothing 경로 적용 대상에 넣지 않았다. 새 후보는 기본 착용 위치·역할만 설명하며 방어·감염 면역·보온·위장·치료 효과를 추가하지 않는다. 수술 장갑/마스크도 손·얼굴의 기본 착용만 후보로 준비했다.

| 비교 사례 | 개별 판정과 이유 |
|---|---|
| Base.Hat_BaseballCap / Base.Hat_BaseballCap_Reverse | hats.txt:78/94의 Clothing/Hat와 ForwardCap/ReverseCap의 self FullType 착용. 전자는 새 core 후보 revise/ready, 후자는 과도한 보호 문구를 줄이는 기존 reduce/ready 유지. 차이는 교정 대상이지 착용 근거 충분성이 아님 |
| Base.Bracelet_BangleRightGold / Base.Bracelet_BangleLeftGold | jewellery.txt:1110/1125의 Clothing/Cosmetic/RightWrist·LeftWrist와 extra self FullType 착용. 오른쪽은 새 core 후보 revise/ready, 왼쪽은 기본 목적 keep/ready 유지. 현재 admission 차이를 source 부족으로 해석하지 않음 |

**Menu는 별도 판정한다.** M017의 일괄 actionable_gap을 철회하고 슬롯의 착용/교체 조건에 대한 `not_observed`로 수정했다. 원문 `doWearClothingTooltip`(1188)은 같은 슬롯/배타 슬롯의 교체 대상을 계산하며, 관련 없는 상황에는 tooltip을 만들지 않을 수 있다. 추가 Wear 행은 방향·좌우·후드 선택이라는 후속 질문을 따로 기록했다. source 동작을 Iris의 실제 표시 완료로 세지도 않고, core 부재만으로 Iris 표시 결손이나 N/A를 만들지도 않는다.

착용 재판정 시점에는 기존 source/조건/identity 미확정 305개와 obsolete 예외 1개로 hold가 306개였다. 이 중 뒤이은 추가 보류 검토에서 33개를 해소했고 최신 잔여는 273개다. 착용 446개의 source 준비와 canonical 채택 미실행은 계속 분리한다. 기존 C/M 번호는 보존하고 더 이상 쓰지 않는 보류 문구만 제거했으며 새 파일·검사·gate·schema·제품 채택은 추가하지 않았다.

### 추가 보류 재판정 — 306개 중 33개 해소

착용 재판정 뒤 남았던 306개를 다시 살펴 31개는 source가 준비된 revise/description_ready 후보로, 2개는 keep/description_ready로 수정했다. 아래 원문 관계는 해당 exact 행들이 공유하는 authoring 근거이며 새로운 validator나 authority가 아니다. 이전 절의 대표 사례에서 보류로 적었던 항목도 **현재 판정은 아래 exact item 표를 따른다**. 제품 채택·generation은 여전히 미실행이다.

| 해소한 exact 범위 | 재사용한 근거와 한계 |
|---|---|
| Base.Camera / CameraDisposable / CameraExpensive | Tags=Camera → recipecode.lua:1515 selector → recipes.txt:4239 ElectronicsScrap. 드라이버·즐겨찾기 제외 조건. 촬영 기능을 확인한 것이 아님 |
| Base.Mattress | ISBuildMenu.lua:1358–1374/1415의 침대 제작 need:Base.Mattress. 독립 sprite 배치나 수면 효과와 분리 |
| farming.GardeningSprayEmpty / GardeningSprayFull | farming.txt:661/675 물 저장·채우기/비우기, :717/730 빈 용기의 치료액 recipe 입력. Full 물을 치료액으로 동일시하지 않음 |
| Base.KeyRing | newitems.txt:2954 Container/OnlyAcceptCategory=Key + inventory menu canMoveTo/isItemAllowed. 일반 가방이나 모든 item 수납으로 확대하지 않음 |
| Base.Muffintray_Biscuit | recipes.txt:1027 Get 6 Biscuits; recipecode.lua:1390 cooked/burnt 조건과 틀 회수. 직접 섭취 불가와 분리 경로를 구분 |
| Base.Beer / Beer2 / Beverage / Beverage2 / WineInGlass | evolvedrecipes.txt:298–362 exact 용기→결과, Food/Drink/ReplaceOnUse와 기존 소비 경로. 동적 내용물에 고정 H/T·안전성 효과를 만들지 않음 |
| Base.LeafRake / Rake / Football2 | exact Weapon·SwingAnim·damage/PhysicsObject 선언. 갈퀴는 근접 공격, Football2는 투척 역할만 후보로 준비. 재배·경기 규칙·무해함을 추가하지 않음 |
| Base.Pinecone / ToiletPaper / Money / CardDeck / Tissue / PaperNapkins | camping_fuel.lua의 exact 연료/점화 재료 키와 기존 ISCampingMenu 경로. 결제·놀이·세척·재채기 기능을 입증한 것이 아님 |
| Base.Pills / PillsAntiDep / PillsBeta / PillsSleepingTablets / PillsVitamins / Antibiotics | 각 선언의 Tooltip key → vanilla Translate/EN/Tooltip_EN.txt:77–80,153,156의 명시적 게임 사용 안내와 실제 Pills/식품 복용 경로. 약 이름이나 현실 약효로 추정하지 않음. 기본 목적만 준비하며 효과량·정확한 발현 시간·치료 보장·좀비 감염 치료는 추가하지 않음 |
| Base.ComfreyCataplasm / PlantainCataplasm / WildGarlicCataplasm | ISHealthPanel.lua:1193–1273 exact item/부상/기존 factor=0 → 각 timed action의 부위 factor 설정·item 소비. 부상 부위에 바르는 처치 목적만 준비하고 개별 회복 효과/속도는 주장하지 않음 |
| Base.Rubberducky / String | exact Normal/DisplayName·WorldStaticModel 및 String의 Material 선언과 기존 안전한 정체성 문구가 일치. 계획 Change 2의 제한된 근거에서 정체성 유지 기준 적용. 새 gameplay 기능을 쓰지 않는 keep에 미확인 engine 동작을 추가 선행 조건으로 요구하지 않음 |

남은 273개는 원문 근거 또는 실제 적용 조건이 부족한 hold이며 채택 미실행과 구분한다. 같은 sprite/handler/producer 관계는 한 번 검토해 공유했고, 아래 필요한 입력을 얻기 위한 외부 접근이나 신규 추출 파일은 만들지 않았다.

| 남은 사유 | 항목 수 | 다음에 필요한 구체적 입력 / 현재 한계 |
|---|---:|---|
| Moveable sprite 귀속 | 139 | 각 행의 WorldObjectSprite에 대응하는 B41 sprite 속성(IsMoveAble, MoveType, PlaceTool 및 관련 위치/객체 속성). InvContextMovable/ISMoveableCursor:628은 실제 sprite 속성을 요구하므로 Type=Moveable만으로 기본 배치나 가전 기능을 확정하지 못함. 유리 4개는 실제 IsoBrokenGlass 연결도 필요. 기존 IrisMoveablesIndex는 도구/tag 등록 자료라 이를 대신하지 않음 |
| obsolete exact item | 17 | 각 원문 OBSOLETE 선언을 보존. 정상 B41에서 해당 exact item의 생성/사용·슬롯 등록이 유효한지 또는 기존 authority가 인정하는 명시적 identity 연결이 필요. Coal의 addFuel action은 확인했지만 obsolete 가용성까지 해결된 것은 아님 |
| legacy 단조/기술/드럼통 | 14 | 정상 B41의 Anvil·Blacksmith·BSFurnace 또는 재고 드럼통 활성 경로. Bellows의 heat 증가 handler는 확인했지만 용광로 정상 가용성이 별개. MetalDrum은 건설 블록 비활성 및 need:Base.MetalDrum 주석 상태를 보존 |
| exact identity 불명확 | 3 | Base.NoiseMaker, Base.Bag_PistolCase, Base.Lemongrass의 exact 원본 선언 또는 기존 lineage의 명시적 귀속. NoiseTrap/PistolCase variants/LemonGrass로 자동 alias하지 않음 |
| 동적 데이터 binding | 3 | Base.Map의 MapID 부여 producer와 Init/지도 데이터, Base.Disc·VHS의 recorded-media ID/type 부여 관계. generic item을 지역 지도·Retail/Home media와 동일시하지 않음 |
| 기타 exact 사용/효과 관계 | 97 | 각 행에 적힌 행동·재료·효과를 해당 FullType에 결속하는 vanilla 선언/recipe/handler 관계. 예: Corkscrew selector만 있고 실제 호출 recipe는 미확정, CampingTent는 CampingTentKit 선택 경로로 대신할 수 없음, UnusableMetal의 해체 실패 산출은 전면적인 사용 불가의 증거가 아님. 미열람·미확정인 모든 handler를 없다고 단정하지 않음 |

위 입력의 물리적 외부 경로는 아직 승인되지 않았다. 경로를 추측해 열거·읽기·생성하지 않았고 owner 사전 승인을 추가 filesystem 권한으로 해석하지 않았다. 이는 후보에 대한 새 승인 Gate가 아니라 남은 fact/실행 조건의 구체적 공백이다. 추가 confidence 확보용 검사 없이 이번 저장소 내부 판정을 마무리한다.

| exact item | 현행 body / core | 제안 disposition / readiness | 이유·근거 및 미확정 범위 | 후보 | Menu |
|---|---|---|---|---|---|
| Base.223Box | public / core | revise / description_ready | §후속 item별 판정: exact 상자 input/result 또는 낱알 AmmoType 관계를 확인했다. | C001 | M001 |
| Base.223Bullets | public / core | revise / description_ready | §후속 item별 판정: exact 상자 input/result 또는 낱알 AmmoType 관계를 확인했다. | C001 | M001 |
| Base.223BulletsMold | public / core | review_hold / review_required | scripts/newitems.txt:3964: 탄약 주조 recipe의 exact keep 관계는 읽었으나 legacy forge/Blacksmith의 활성 사용 조건을 결속하지 못했다. 남은 입력은 정상 B41에서 이 legacy 단조 recipe/Anvil·Blacksmith 기술을 사용할 수 있는 근거 또는 실제 활성 대체 경로다. source successor 미발행이나 기존 core 부재 자체를 보류 사유로 삼지 않음. | C002 | M216 |
| Base.223Clip | public / core | keep / description_ready | 각 exact 탄창 AmmoType과 장전 용도를 대조했다. .308Clip과 M14Clip을 같은 탄창으로 합치지 않는다. | C003 | M003 |
| Base.308Box | public / core | revise / description_ready | §후속 item별 판정: exact 상자 input/result 또는 낱알 AmmoType 관계를 확인했다. | C001 | M001 |
| Base.308Bullets | public / core | revise / description_ready | §후속 item별 판정: exact 상자 input/result 또는 낱알 AmmoType 관계를 확인했다. | C001 | M001 |
| Base.308BulletsMold | public / core | review_hold / review_required | scripts/newitems.txt:3953: 탄약 주조 recipe의 exact keep 관계는 읽었으나 legacy forge/Blacksmith의 활성 사용 조건을 결속하지 못했다. 남은 입력은 정상 B41에서 이 legacy 단조 recipe/Anvil·Blacksmith 기술을 사용할 수 있는 근거 또는 실제 활성 대체 경로다. source successor 미발행이나 기존 core 부재 자체를 보류 사유로 삼지 않음. | C002 | M216 |
| Base.308Clip | public / core | keep / description_ready | 각 exact 탄창 AmmoType과 장전 용도를 대조했다. .308Clip과 M14Clip을 같은 탄창으로 합치지 않는다. | C003 | M003 |
| Base.44Clip | public / core | keep / description_ready | 각 exact 탄창 AmmoType과 장전 용도를 대조했다. .308Clip과 M14Clip을 같은 탄창으로 합치지 않는다. | C003 | M003 |
| Base.45Clip | public / core | keep / description_ready | 각 exact 탄창 AmmoType과 장전 용도를 대조했다. .308Clip과 M14Clip을 같은 탄창으로 합치지 않는다. | C003 | M003 |
| Base.556Box | public / core | revise / description_ready | §후속 item별 판정: exact 상자 input/result 또는 낱알 AmmoType 관계를 확인했다. | C001 | M001 |
| Base.556Bullets | public / core | revise / description_ready | §후속 item별 판정: exact 상자 input/result 또는 낱알 AmmoType 관계를 확인했다. | C001 | M001 |
| Base.556Clip | public / core | keep / description_ready | 각 exact 탄창 AmmoType과 장전 용도를 대조했다. .308Clip과 M14Clip을 같은 탄창으로 합치지 않는다. | C003 | M003 |
| Base.9mmBulletsMold | public / core | review_hold / review_required | scripts/newitems.txt:3931: 탄약 주조 recipe의 exact keep 관계는 읽었으나 legacy forge/Blacksmith의 활성 사용 조건을 결속하지 못했다. 남은 입력은 정상 B41에서 이 legacy 단조 recipe/Anvil·Blacksmith 기술을 사용할 수 있는 근거 또는 실제 활성 대체 경로다. source successor 미발행이나 기존 core 부재 자체를 보류 사유로 삼지 않음. | C002 | M216 |
| Base.9mmClip | public / core | keep / description_ready | 각 exact 탄창 AmmoType과 장전 용도를 대조했다. .308Clip과 M14Clip을 같은 탄창으로 합치지 않는다. | C003 | M003 |
| Base.Acorn | public / core | revise / description_ready | scripts/items_food.txt:8456의 exact H=-10, T=미선언; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C004 | M004 |
| Base.Aerosolbomb | public / core | revise / description_ready | scripts/newitems.txt:2969의 exact ExplosionPower=70. 원격/센서/타이머는 각 선언대로 별도 조건이며 모든 장치를 같은 투척/폭발 효과로 묶지 않는다. Java 내부·PZ 실제 효과는 미관찰. | C005 | M005 |
| Base.AerosolbombRemote | public / core | revise / description_ready | scripts/newitems.txt:3117의 exact ExplosionPower=70. 원격/센서/타이머는 각 선언대로 별도 조건이며 모든 장치를 같은 투척/폭발 효과로 묶지 않는다. Java 내부·PZ 실제 효과는 미관찰. | C005 | M005 |
| Base.AerosolbombSensorV1 | public / core | revise / description_ready | scripts/newitems.txt:3027의 exact ExplosionPower=70. 원격/센서/타이머는 각 선언대로 별도 조건이며 모든 장치를 같은 투척/폭발 효과로 묶지 않는다. Java 내부·PZ 실제 효과는 미관찰. | C005 | M005 |
| Base.AerosolbombSensorV2 | public / core | revise / description_ready | scripts/newitems.txt:3057의 exact ExplosionPower=70. 원격/센서/타이머는 각 선언대로 별도 조건이며 모든 장치를 같은 투척/폭발 효과로 묶지 않는다. Java 내부·PZ 실제 효과는 미관찰. | C005 | M005 |
| Base.AerosolbombSensorV3 | public / core | revise / description_ready | scripts/newitems.txt:3087의 exact ExplosionPower=70. 원격/센서/타이머는 각 선언대로 별도 조건이며 모든 장치를 같은 투척/폭발 효과로 묶지 않는다. Java 내부·PZ 실제 효과는 미관찰. | C005 | M005 |
| Base.AerosolbombTriggered | public / core | revise / description_ready | scripts/newitems.txt:2998의 exact ExplosionPower=70. 원격/센서/타이머는 각 선언대로 별도 조건이며 모든 장치를 같은 투척/폭발 효과로 묶지 않는다. Java 내부·PZ 실제 효과는 미관찰. | C005 | M005 |
| Base.AlarmClock | public / core | keep / description_ready | scripts/newitems.txt:3684의 NoiseRange=10/ExplosionTimer=10/CanBeReused=true가 현재 지연 소리 장치 설명과 일치한다. AlarmClock2와 다른 Weapon이다. | C006 | M006 |
| Base.AlarmClock2 | public / core | revise / description_ready | scripts/newitems.txt:3671; exact AlarmClock/AlarmSound와 현재 시계 역할. Normal DigitalWatch나 Weapon AlarmClock에 전파하지 않는다. | C007 | M007 |
| Base.AlcoholBandage | public / core | revise / description_ready | scripts/newitems.txt:1639: exact CanBandage 및 ISApplyBandage:SetBandaged. Alcohol 여부는 source의 item:isAlcoholic 전달에 한정하며 치료/감염 예방 보장 없음. | C008 | M008 |
| Base.AlcoholRippedSheets | public / core | revise / description_ready | scripts/items.txt:436: exact CanBandage 및 ISApplyBandage:SetBandaged. Alcohol 여부는 source의 item:isAlcoholic 전달에 한정하며 치료/감염 예방 보장 없음. | C008 | M008 |
| Base.AlcoholWipes | public / core | revise / description_ready | §의료: AlcoholPower → HDisinfect/ISDisinfect | C009 | M009 |
| Base.AlcoholedCottonBalls | public / core | revise / description_ready | scripts/newitems.txt:2260: newitems:2260의 AlcoholPower=4 및 기존 HDisinfect/ISDisinfect 경로 재사용. | C010 | M010 |
| Base.Allsorts | public / core | revise / description_ready | scripts/items_food.txt:8401의 exact H=-10, T=미선언; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C004 | M004 |
| Base.Aluminum | public / core | revise / description_ready | scripts/newitems.txt:15; input:Make Aerosol bomb; input:Make Tin Foil Hat; input:Craft Makeshift Radio; input:Craft Makeshift HAM Radio; input:Craft Makeshift Walkie Talkie; recipes_radio.txt:72–125 exact 제작 입력. 독립 기기 기능 없음. | C011 | M011 |
| Base.AmericanLadyCaterpillar | public / core | revise / description_ready | scripts/items_food.txt:8765의 exact H=-5, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C012 | M012 |
| Base.AmmoStrap_Bullets | public / core | revise / description_ready | §후속 item별 판정: 해당 ReloadFast tag/ClothingItem과 shotgun 여부 분기를 확인했다. | C013 | M013 |
| Base.AmmoStrap_Shells | public / core | revise / description_ready | §후속 item별 판정: 해당 ReloadFast tag/ClothingItem과 shotgun 여부 분기를 확인했다. | C013 | M013 |
| Base.AmmoStraps | public / core | keep / description_ready | scripts/newitems.txt:2513; exact WeaponPart/PartType=Sling/MountOn=HuntingRifle; VarmintRifle; Shotgun. 총기 개조 부품이라는 current 목적은 구체적. 실제 성능·조명/총검 공격은 추가하지 않는다. | C014 | M014 |
| Base.Amplifier | public / core | revise / description_ready | scripts/newitems.txt:231; input:Make Noise Maker; input:Craft Makeshift Radio; input:Craft Makeshift HAM Radio; input:Craft Makeshift Walkie Talkie; recipes_radio.txt:72–125 exact 제작 입력. 독립 기기 기능 없음. | C011 | M011 |
| Base.Antibiotics | public / core | revise / description_ready | scripts/newitems.txt:2245; exact item의 Tooltip_Antibiotics 선언→lua/shared/Translate/EN/Tooltip_EN.txt:156 게임 원문 사용 안내. Food/ReduceInfectionPower/Take 및 기존 ISEatFoodAction 경로. 기본 목적의 명시적 게임 안내와 실제 복용 경로를 결속; 수치·발현 시간·성공 보장은 추가하지 않고 엔진 효과 증명으로 범위를 키우지 않음. | C222 | M217 |
| Base.Apple | public / core | revise / description_ready | §식재료 사과: exact H=-16/T=-7와 EvolvedRecipe·AddItemInRecipe | C016 | M016 |
| Base.Apron_Black | public / no-core | revise / description_ready | scripts/clothing/clothing_others.txt:3: Clothing/BodyLocation=TorsoExtra. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C178 | M017 |
| Base.Apron_IceCream | public / no-core | revise / description_ready | scripts/clothing/clothing_others.txt:15: Clothing/BodyLocation=TorsoExtra. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C178 | M017 |
| Base.Apron_Jay | public / no-core | revise / description_ready | scripts/clothing/clothing_others.txt:27: Clothing/BodyLocation=TorsoExtra. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C178 | M017 |
| Base.Apron_PileOCrepe | public / core | keep / description_ready | scripts/clothing/clothing_others.txt:39의 Clothing/BodyLocation=TorsoExtra와 현재 착용 목적 일치. 수치 추가나 감염/위장 효과를 강제하지 않는다. | C018 | M018 |
| Base.Apron_PizzaWhirled | public / core | keep / description_ready | scripts/clothing/clothing_others.txt:51의 Clothing/BodyLocation=TorsoExtra와 현재 착용 목적 일치. 수치 추가나 감염/위장 효과를 강제하지 않는다. | C018 | M018 |
| Base.Apron_Spiffos | public / no-core | revise / description_ready | scripts/clothing/clothing_others.txt:63: Clothing/BodyLocation=TorsoExtra. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C178 | M017 |
| Base.Apron_White | public / no-core | revise / description_ready | scripts/clothing/clothing_others.txt:75: Clothing/BodyLocation=TorsoExtra. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C178 | M017 |
| Base.Apron_WhiteTEXTURE | public / no-core | revise / description_ready | scripts/clothing/clothing_others.txt:87: Clothing/BodyLocation=TorsoExtra. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C178 | M017 |
| Base.AssaultRifle | public / core | revise / description_ready | scripts/items_weapons.txt:6083 exact ranged Weapon 및 소총 AmmoType. RifleCase와 섞인 current 문구를 분리한다. | C019 | M019 |
| Base.AssaultRifle2 | public / core | revise / description_ready | scripts/items_weapons.txt:6173 exact ranged Weapon 및 소총 AmmoType. RifleCase와 섞인 current 문구를 분리한다. | C019 | M019 |
| Base.Avocado | public / core | revise / description_ready | scripts/items_food.txt:1065의 exact H=-16, T=-7; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C020 | M004 |
| Base.Axe | public / core | keep / description_ready | scripts/items_weapons.txt:2624; exact ChopTree tag, ISWorldObjectContextMenu:439/1297 및 ISChopTreeAction queue. 현재 벌목 역할이 구체적. | C014 | M020 |
| Base.AxeStone | public / core | keep / description_ready | scripts/items_weapons.txt:1634; exact ChopTree tag, ISWorldObjectContextMenu:439/1297 및 ISChopTreeAction queue. 현재 벌목 역할이 구체적. | C014 | M020 |
| Base.BackgammonBoard | public / core | review_hold / review_required | scripts/newitems.txt:4914: §남은 혼합 역할: 현재 놀이 assertion을 실제 게임 플레이/지루함 감소에 결속하지 못했다. Normal 소품과 실제 놀이 기능을 구분한다. 필요한 추가 근거는 이 exact item의 해당 행동/재료 입력 또는 효과를 명시하는 vanilla source 관계이며, current admission 부재를 해소할 승인만으로 대체하지 않음. | C002 | M021 |
| Base.BadmintonRacket | public / no-core | revise / description_ready | scripts/items_weapons.txt:843; exact Type=Weapon/damage=0.1–0.2. 연주·경기·배관 수리 같은 현실 기능을 추정하지 않는다. | C021 | M022 |
| Base.Bag_ALICEpack | public / no-core | revise / description_ready | scripts/clothing/clothing_bags.txt:113의 exact Container/Capacity=27. 보관·운반 역할이 명확하며 이름에 따른 내용물 제한/냉장 효과는 추가하지 않는다. 기존 identity-only 표현은 자동 승격하지 않고 source-bound core 추가를 제안한다. | C022 | M023 |
| Base.Bag_ALICEpack_Army | public / no-core | revise / description_ready | scripts/clothing/clothing_bags.txt:135의 exact Container/Capacity=28. 보관·운반 역할이 명확하며 이름에 따른 내용물 제한/냉장 효과는 추가하지 않는다. 기존 identity-only 표현은 자동 승격하지 않고 source-bound core 추가를 제안한다. | C022 | M023 |
| Base.Bag_BigHikingBag | public / no-core | revise / description_ready | scripts/clothing/clothing_bags.txt:69의 exact Container/Capacity=22. 보관·운반 역할이 명확하며 이름에 따른 내용물 제한/냉장 효과는 추가하지 않는다. 기존 identity-only 표현은 자동 승격하지 않고 source-bound core 추가를 제안한다. | C022 | M023 |
| Base.Bag_BowlingBallBag | public / core | keep / description_ready | scripts/clothing/clothing_bags.txt:774의 exact Container/Capacity=8. 보관·운반 역할이 명확하며 이름에 따른 내용물 제한/냉장 효과는 추가하지 않는다. | C023 | M023 |
| Base.Bag_DoctorBag | public / core | keep / description_ready | scripts/newBags.txt:338의 exact Container/Capacity=8. 보관·운반 역할이 명확하며 이름에 따른 내용물 제한/냉장 효과는 추가하지 않는다. | C023 | M023 |
| Base.Bag_DuffelBag | public / no-core | revise / description_ready | scripts/clothing/clothing_bags.txt:237의 exact Container/Capacity=18. 보관·운반 역할이 명확하며 이름에 따른 내용물 제한/냉장 효과는 추가하지 않는다. 기존 identity-only 표현은 자동 승격하지 않고 source-bound core 추가를 제안한다. | C022 | M023 |
| Base.Bag_DuffelBagTINT | public / no-core | revise / description_ready | scripts/clothing/clothing_bags.txt:258의 exact Container/Capacity=18. 보관·운반 역할이 명확하며 이름에 따른 내용물 제한/냉장 효과는 추가하지 않는다. 기존 identity-only 표현은 자동 승격하지 않고 source-bound core 추가를 제안한다. | C022 | M023 |
| Base.Bag_FannyPackBack | public / core | keep / description_ready | scripts/clothing/clothing_bags.txt:514의 exact Container/Capacity=1. 보관·운반 역할이 명확하며 이름에 따른 내용물 제한/냉장 효과는 추가하지 않는다. | C023 | M023 |
| Base.Bag_FannyPackFront | public / no-core | revise / description_ready | scripts/clothing/clothing_bags.txt:492의 exact Container/Capacity=1. 보관·운반 역할이 명확하며 이름에 따른 내용물 제한/냉장 효과는 추가하지 않는다. 기존 identity-only 표현은 자동 승격하지 않고 source-bound core 추가를 제안한다. | C022 | M023 |
| Base.Bag_FoodCanned | public / no-core | revise / description_ready | scripts/newBags.txt:3의 exact Container/Capacity=18. 보관·운반 역할이 명확하며 이름에 따른 내용물 제한/냉장 효과는 추가하지 않는다. 기존 identity-only 표현은 자동 승격하지 않고 source-bound core 추가를 제안한다. | C022 | M023 |
| Base.Bag_FoodSnacks | public / no-core | revise / description_ready | scripts/newBags.txt:23의 exact Container/Capacity=18. 보관·운반 역할이 명확하며 이름에 따른 내용물 제한/냉장 효과는 추가하지 않는다. 기존 identity-only 표현은 자동 승격하지 않고 source-bound core 추가를 제안한다. | C022 | M023 |
| Base.Bag_GolfBag | public / no-core | revise / description_ready | scripts/clothing/clothing_bags.txt:4의 exact Container/Capacity=18. 보관·운반 역할이 명확하며 이름에 따른 내용물 제한/냉장 효과는 추가하지 않는다. 기존 identity-only 표현은 자동 승격하지 않고 source-bound core 추가를 제안한다. | C022 | M023 |
| Base.Bag_InmateEscapedBag | public / core | keep / description_ready | scripts/clothing/clothing_bags.txt:177의 exact Container/Capacity=18. 보관·운반 역할이 명확하며 이름에 따른 내용물 제한/냉장 효과는 추가하지 않는다. | C023 | M023 |
| Base.Bag_JanitorToolbox | public / core | keep / description_ready | scripts/clothing/clothing_bags.txt:678의 exact Container/Capacity=8. 보관·운반 역할이 명확하며 이름에 따른 내용물 제한/냉장 효과는 추가하지 않는다. | C023 | M023 |
| Base.Bag_MedicalBag | public / no-core | revise / description_ready | scripts/newBags.txt:43의 exact Container/Capacity=18. 보관·운반 역할이 명확하며 이름에 따른 내용물 제한/냉장 효과는 추가하지 않는다. 기존 identity-only 표현은 자동 승격하지 않고 source-bound core 추가를 제안한다. | C022 | M023 |
| Base.Bag_Military | public / no-core | revise / description_ready | scripts/newBags.txt:66의 exact Container/Capacity=18. 보관·운반 역할이 명확하며 이름에 따른 내용물 제한/냉장 효과는 추가하지 않는다. 기존 identity-only 표현은 자동 승격하지 않고 source-bound core 추가를 제안한다. | C022 | M023 |
| Base.Bag_MoneyBag | public / core | keep / description_ready | scripts/clothing/clothing_bags.txt:197의 exact Container/Capacity=18. 보관·운반 역할이 명확하며 이름에 따른 내용물 제한/냉장 효과는 추가하지 않는다. | C023 | M023 |
| Base.Bag_NormalHikingBag | public / no-core | revise / description_ready | scripts/clothing/clothing_bags.txt:47의 exact Container/Capacity=20. 보관·운반 역할이 명확하며 이름에 따른 내용물 제한/냉장 효과는 추가하지 않는다. 기존 identity-only 표현은 자동 승격하지 않고 source-bound core 추가를 제안한다. | C022 | M023 |
| Base.Bag_PistolCase | public / core | review_hold / review_required | exact 원본 선언을 찾지 못했다. PistolCase1/2/3의 Container 사실을 이 key에 복사하지 않는다. 필요한 입력은 해당 exact casing/namespace의 원본 선언 또는 기존 lineage가 인정하는 명시적 identity 귀속이다. 비슷한 이름을 임의 alias로 채택하지 않음. | C024 | M024 |
| Base.Bag_Satchel | public / no-core | revise / description_ready | scripts/clothing/clothing_bags.txt:553의 exact Container/Capacity=15. 보관·운반 역할이 명확하며 이름에 따른 내용물 제한/냉장 효과는 추가하지 않는다. 기존 identity-only 표현은 자동 승격하지 않고 source-bound core 추가를 제안한다. | C022 | M023 |
| Base.Bag_Schoolbag | public / no-core | revise / description_ready | scripts/clothing/clothing_bags.txt:25의 exact Container/Capacity=15. 보관·운반 역할이 명확하며 이름에 따른 내용물 제한/냉장 효과는 추가하지 않는다. 기존 identity-only 표현은 자동 승격하지 않고 source-bound core 추가를 제안한다. | C022 | M023 |
| Base.Bag_ShotgunBag | public / no-core | revise / description_ready | scripts/clothing/clothing_bags.txt:694의 exact Container/Capacity=18. 보관·운반 역할이 명확하며 이름에 따른 내용물 제한/냉장 효과는 추가하지 않는다. 기존 identity-only 표현은 자동 승격하지 않고 source-bound core 추가를 제안한다. | C022 | M023 |
| Base.Bag_ShotgunDblBag | public / no-core | revise / description_ready | scripts/clothing/clothing_bags.txt:734의 exact Container/Capacity=18. 보관·운반 역할이 명확하며 이름에 따른 내용물 제한/냉장 효과는 추가하지 않는다. 기존 identity-only 표현은 자동 승격하지 않고 source-bound core 추가를 제안한다. | C022 | M023 |
| Base.Bag_ShotgunDblSawnoffBag | public / no-core | revise / description_ready | scripts/clothing/clothing_bags.txt:754의 exact Container/Capacity=18. 보관·운반 역할이 명확하며 이름에 따른 내용물 제한/냉장 효과는 추가하지 않는다. 기존 identity-only 표현은 자동 승격하지 않고 source-bound core 추가를 제안한다. | C022 | M023 |
| Base.Bag_ShotgunSawnoffBag | public / no-core | revise / description_ready | scripts/clothing/clothing_bags.txt:714의 exact Container/Capacity=18. 보관·운반 역할이 명확하며 이름에 따른 내용물 제한/냉장 효과는 추가하지 않는다. 기존 identity-only 표현은 자동 승격하지 않고 source-bound core 추가를 제안한다. | C022 | M023 |
| Base.Bag_SurvivorBag | public / core | keep / description_ready | scripts/clothing/clothing_bags.txt:91의 exact Container/Capacity=27. 보관·운반 역할이 명확하며 이름에 따른 내용물 제한/냉장 효과는 추가하지 않는다. | C023 | M023 |
| Base.Bag_ToolBag | public / no-core | revise / description_ready | scripts/newBags.txt:86의 exact Container/Capacity=18. 보관·운반 역할이 명확하며 이름에 따른 내용물 제한/냉장 효과는 추가하지 않는다. 기존 identity-only 표현은 자동 승격하지 않고 source-bound core 추가를 제안한다. | C022 | M023 |
| Base.Bag_WeaponBag | public / core | keep / description_ready | scripts/clothing/clothing_bags.txt:157의 exact Container/Capacity=18. 보관·운반 역할이 명확하며 이름에 따른 내용물 제한/냉장 효과는 추가하지 않는다. | C023 | M023 |
| Base.Bag_WorkerBag | public / core | keep / description_ready | scripts/clothing/clothing_bags.txt:217의 exact Container/Capacity=18. 보관·운반 역할이 명확하며 이름에 따른 내용물 제한/냉장 효과는 추가하지 않는다. | C023 | M023 |
| Base.BagelPlain | public / core | revise / description_ready | scripts/items_food.txt:5688의 exact H=-10, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C012 | M012 |
| Base.BagelPoppy | public / core | revise / description_ready | scripts/items_food.txt:5706의 exact H=-10, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C012 | M012 |
| Base.BagelSesame | public / core | revise / description_ready | scripts/items_food.txt:5724의 exact H=-10, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C012 | M012 |
| Base.Baguette | public / core | revise / description_ready | scripts/items_food.txt:5742의 exact H=-23, T=미선언; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C004 | M004 |
| Base.BaguetteDough | public / no-core | revise / description_ready | scripts/items_food.txt:5766의 exact H=-15, T=15; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음; ReplaceOnCooked=Base.Baguette, 다른 상태 item과 구분. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C025 | M012 |
| Base.BaguetteSandwich | public / no-core | revise / description_ready | scripts/items_food.txt:5534의 exact H=-10, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C012 | M012 |
| Base.BaitFish | public / core | revise / description_ready | §농사·낚시·덫: 해당 exact source 선택·조건 및 실제 결과 변화 연결 | C026 | M025 |
| Base.BakingPan | public / core | revise / description_ready | scripts/newitems.txt:1429; recipes.txt:928/1065 케이크·파이 반죽 넣기 입력. | C027 | M026 |
| Base.BakingSoda | public / core | revise / description_ready | §조리 문구 32개: 이 exact item의 input/result/keep 역할과 원본 recipe를 분리 검토했다. | C026 | M027 |
| Base.BakingTray | public / core | revise / description_ready | scripts/items.txt:32; recipes.txt:4339–4462 쿠키 반죽 준비의 destroy input. | C028 | M026 |
| Base.BakingTrayBread | public / no-core | revise / description_ready | scripts/items_food.txt:4406의 exact H=-15, T=20; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음; ReplaceOnCooked=Base.BakingTray;Base.Dough, 다른 상태 item과 구분. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C025 | M012 |
| Base.BakingTray_Muffin | public / no-core | revise / description_ready | scripts/items_food.txt:7637; CantEat=TRUE; recipes.txt:4002 Get 6 Muffins 및 recipecode.GetMuffin 조건. 기존 섭취 후보를 철회. | C029 | M028 |
| Base.BakingTray_Muffin_Recipe | public / no-core | revise / description_ready | scripts/items_food.txt:7663; CantEat=TRUE; recipes.txt:4002 Get 6 Muffins 및 recipecode.GetMuffin 조건. 기존 섭취 후보를 철회. | C029 | M028 |
| Base.BallPeenHammer | public / core | revise / description_ready | scripts/items_weapons.txt:968; exact Hammer tag → 기존 ISBuildMenu 경로. 활성 경로가 미결속인 단조-only 문구에서 확인된 역할로 교정. | C030 | M029 |
| Base.Baloney | public / core | revise / description_ready | scripts/items_food.txt:7138의 exact H=-30, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C012 | M012 |
| Base.BaloneySlice | public / no-core | revise / description_ready | scripts/items_food.txt:7158의 exact H=-5, T=미선언; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C004 | M004 |
| Base.Banana | public / core | revise / description_ready | scripts/items_food.txt:1652의 exact H=-16, T=-5; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C020 | M004 |
| Base.Bandage | public / core | revise / description_ready | §의료: CanBandage → SetBandaged | C009 | M030 |
| Base.BandageDirty | public / core | revise / description_ready | scripts/newitems.txt:1624: exact CanBandage 및 ISApplyBandage:perform의 Dirty type은 bandageLife=0으로 분기. 깨끗한 재료와 같은 지속/치료 효과를 주지 않는다. | C031 | M031 |
| Base.Bandaid | public / no-core | revise / description_ready | scripts/newitems.txt:1593: exact CanBandage 및 ISApplyBandage:SetBandaged. Alcohol 여부는 source의 item:isAlcoholic 전달에 한정하며 치료/감염 예방 보장 없음. | C008 | M008 |
| Base.BandedWoolyBearCaterpillar | public / core | revise / description_ready | scripts/items_food.txt:8785의 exact H=-5, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C012 | M012 |
| Base.Banjo | public / no-core | revise / description_ready | scripts/items_weapons.txt:1549; exact Type=Weapon/damage=0.3–0.6. 연주·경기·배관 수리 같은 현실 기능을 추정하지 않는다. | C021 | M022 |
| Base.BarBell | public / no-core | revise / description_ready | scripts/items_weapons.txt:2768; exact Type=Weapon/damage=1.8–2.8. 연주·경기·배관 수리 같은 현실 기능을 추정하지 않는다. | C021 | M022 |
| Base.BarbedWire | public / core | keep / description_ready | 보호된 BarbedWire의 기존 구조물 제작 역할을 유지한다. | C003 | M032 |
| Base.Baseball | public / core | review_hold / review_required | scripts/newitems.txt:265: 현재 경기 규칙에 맞춘 놀이 assertion을 실제 경기/투척 기능과 결속하지 못했다. Normal 소품이라는 선언은 경기 실행 근거가 아니다. 필요한 추가 근거는 이 exact item의 해당 행동/재료 입력 또는 효과를 명시하는 vanilla source 관계이며, current admission 부재를 해소할 승인만으로 대체하지 않음. | C002 | M033 |
| Base.BaseballBat | public / core | keep / description_ready | 각 exact Weapon의 근접 전투 역할이 현재 기본 목적과 일치한다. identity_fallback인 행은 그대로 S2 core로 승격하지 않는다. | C003 | M034 |
| Base.BaseballBatNails | public / core | keep / description_ready | 각 exact Weapon의 근접 전투 역할이 현재 기본 목적과 일치한다. identity_fallback인 행은 그대로 S2 core로 승격하지 않는다. | C003 | M034 |
| Base.Basil | public / core | revise / description_ready | scripts/items_food.txt:8517의 exact H=-1, T=미선언; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C004 | M004 |
| Base.Basketball | public / core | review_hold / review_required | scripts/newitems.txt:275: 현재 경기 규칙에 맞춘 놀이 assertion을 실제 경기/투척 기능과 결속하지 못했다. Normal 소품이라는 선언은 경기 실행 근거가 아니다. 필요한 추가 근거는 이 exact item의 해당 행동/재료 입력 또는 효과를 명시하는 vanilla source 관계이며, current admission 부재를 해소할 승인만으로 대체하지 않음. | C002 | M033 |
| Base.Bass | public / core | revise / description_ready | scripts/items_food.txt:1704의 exact H=-26, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음; DangerousUncooked=TRUE. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C032 | M012 |
| Base.BathTowel | public / core | revise / description_ready | §후속 item별 판정: exact drying 및 blood cleaning 선택 | C033 | M035 |
| Base.BathTowelWet | public / core | revise / description_ready | scripts/newitems.txt:1565; Wet=true, ItemWhenDry=Base.BathTowel; 젖은 상태와 기존 건조 수건 역할 구분. | C034 | M011 |
| Base.Battery | public / core | revise / description_ready | §건전지: exact 삽입 recipe 및 usedDelta 전달/교체 조건 | C035 | M036 |
| Base.Bayonnet | public / core | keep / description_ready | scripts/newitems.txt:2619; exact WeaponPart/PartType=Canon/MountOn=VarmintRifle; HuntingRifle. 총기 개조 부품이라는 current 목적은 구체적. 실제 성능·조명/총검 공격은 추가하지 않는다. | C014 | M014 |
| Base.BeanBowl | public / no-core | revise / description_ready | scripts/items_food.txt:4432의 exact H=-24, T=미선언; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C004 | M004 |
| Base.BeautyBerry | public / core | revise / description_ready | scripts/items_food.txt:8475의 exact H=-10, T=-1; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C020 | M004 |
| Base.BeefJerky | public / core | revise / description_ready | scripts/items_food.txt:2255의 exact H=-20, T=미선언; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C004 | M004 |
| Base.Beer | public / no-core | revise / description_ready | undefined; scripts/evolvedrecipes.txt:336 exact BaseItem→ResultItem 관계와 items_food Food/CustomContextMenu=Drink/ReplaceOnUse. inventory menu:124/414/2976 및 기존 소비 경로. 정적 H/T 부재는 동적 결과의 무효가 아니며 고정 효과량을 후보에 넣지 않음. | C223 | M218 |
| Base.Beer2 | public / no-core | revise / description_ready | undefined; scripts/evolvedrecipes.txt:345 exact BaseItem→ResultItem 관계와 items_food Food/CustomContextMenu=Drink/ReplaceOnUse. inventory menu:124/414/2976 및 기존 소비 경로. 정적 H/T 부재는 동적 결과의 무효가 아니며 고정 효과량을 후보에 넣지 않음. | C224 | M218 |
| Base.BeerBottle | public / core | revise / description_ready | scripts/items_food.txt:3553; Alcoholic=TRUE, H/T 음수 Food 및 EvolvedRecipe; 기분 개선을 일괄 보장하는 기존 문구 축소. | C037 | M038 |
| Base.BeerCan | public / core | revise / description_ready | scripts/items_food.txt:3523; Alcoholic=TRUE, H/T 음수 Food 및 EvolvedRecipe; 기분 개선을 일괄 보장하는 기존 문구 축소. | C037 | M038 |
| Base.BeerCanEmpty | public / core | review_hold / review_required | scripts/newitems.txt:4076: 이 빈 item의 재사용/처리 목적을 실제 전환·상호작용에 결속하지 못했다. 빈 용기라는 이름만으로 물 저장 가능성을 추가하지 않는다. 필요한 추가 근거는 이 exact item의 해당 행동/재료 입력 또는 효과를 명시하는 vanilla source 관계이며, current admission 부재를 해소할 승인만으로 대체하지 않음. | C002 | M039 |
| Base.BeerEmpty | public / core | keep / description_ready | 각 exact CanStoreWater 및 ReplaceOnUseOn=WaterSource 관계를 확인했다. 물의 안전성이나 소독 효과는 주장하지 않는다. | C003 | M040 |
| Base.BeerWaterFull | public / no-core | revise / description_ready | scripts/items_food.txt:2763: CanStoreWater=TRUE, ReplaceOnUseOn=WaterSource-BeerWaterFull. §빈 물 용기와 같은 exact 물 저장/전환 사실을 재사용하며 음용 안전성·현재 내용물은 추정하지 않는다. | C038 | M041 |
| Base.Bell | public / core | review_hold / review_required | scripts/newitems.txt:285: Normal Bell의 소리 발생/상호작용 경로를 결속하지 못했다. 이름이 효과를 증명하지 않는다. 필요한 추가 근거는 이 exact item의 해당 행동/재료 입력 또는 효과를 명시하는 vanilla source 관계이며, current admission 부재를 해소할 승인만으로 대체하지 않음. | C002 | M042 |
| Base.BellPepper | public / core | revise / description_ready | scripts/items_food.txt:1043의 exact H=-8, T=-2; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C020 | M004 |
| Base.Bellows | public / core | review_hold / review_required | scripts/newitems.txt:4007; ISBlacksmithMenu:316/338/480/785의 기존 불붙은 BSFurnace·heat<100 선택→ISUseBellows.update의 열 증가·지구력 소모는 확인. 근거 공백은 풀무 효과 자체가 아니라 disableFurnaceAnvil=true 상태의 정상 B41 용광로 가용성/내용 범위다. | C002 | M216 |
| Base.BellyButton_DangleGold | public / no-core | revise / description_ready | scripts/clothing/clothing_jewellery.txt:1260: Clothing/BodyLocation=BellyButton. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C179 | M017 |
| Base.BellyButton_DangleGoldRuby | public / no-core | revise / description_ready | scripts/clothing/clothing_jewellery.txt:1271: Clothing/BodyLocation=BellyButton. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C179 | M017 |
| Base.BellyButton_DangleSilver | public / no-core | revise / description_ready | scripts/clothing/clothing_jewellery.txt:1282: Clothing/BodyLocation=BellyButton. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C179 | M017 |
| Base.BellyButton_DangleSilverDiamond | public / no-core | revise / description_ready | scripts/clothing/clothing_jewellery.txt:1293: Clothing/BodyLocation=BellyButton. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C179 | M017 |
| Base.BellyButton_RingGold | public / no-core | revise / description_ready | scripts/clothing/clothing_jewellery.txt:1304: Clothing/BodyLocation=BellyButton. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C179 | M017 |
| Base.BellyButton_RingGoldDiamond | public / no-core | revise / description_ready | scripts/clothing/clothing_jewellery.txt:1315: Clothing/BodyLocation=BellyButton. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C179 | M017 |
| Base.BellyButton_RingGoldRuby | public / no-core | revise / description_ready | scripts/clothing/clothing_jewellery.txt:1326: Clothing/BodyLocation=BellyButton. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C179 | M017 |
| Base.BellyButton_RingSilver | public / no-core | revise / description_ready | scripts/clothing/clothing_jewellery.txt:1337: Clothing/BodyLocation=BellyButton. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C179 | M017 |
| Base.BellyButton_RingSilverAmethyst | public / no-core | revise / description_ready | scripts/clothing/clothing_jewellery.txt:1348: Clothing/BodyLocation=BellyButton. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C179 | M017 |
| Base.BellyButton_RingSilverDiamond | public / no-core | revise / description_ready | scripts/clothing/clothing_jewellery.txt:1359: Clothing/BodyLocation=BellyButton. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C179 | M017 |
| Base.BellyButton_RingSilverRuby | public / no-core | revise / description_ready | scripts/clothing/clothing_jewellery.txt:1370: Clothing/BodyLocation=BellyButton. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C179 | M017 |
| Base.BellyButton_StudGold | public / no-core | revise / description_ready | scripts/clothing/clothing_jewellery.txt:1381: Clothing/BodyLocation=BellyButton. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C179 | M017 |
| Base.BellyButton_StudGoldDiamond | public / no-core | revise / description_ready | scripts/clothing/clothing_jewellery.txt:1392: Clothing/BodyLocation=BellyButton. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C179 | M017 |
| Base.BellyButton_StudSilver | public / no-core | revise / description_ready | scripts/clothing/clothing_jewellery.txt:1403: Clothing/BodyLocation=BellyButton. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C179 | M017 |
| Base.BellyButton_StudSilverDiamond | public / no-core | revise / description_ready | scripts/clothing/clothing_jewellery.txt:1414: Clothing/BodyLocation=BellyButton. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C179 | M017 |
| Base.Belt | public / core | review_hold / review_required | scripts/items.txt:68: Base.Belt는 Normal이며 착용 슬롯이 결속되지 않았다. 다른 착용형 belt의 행동을 복사하지 않는다. 필요한 추가 근거는 이 exact item의 해당 행동/재료 입력 또는 효과를 명시하는 vanilla source 관계이며, current admission 부재를 해소할 승인만으로 대체하지 않음. | C002 | M044 |
| Base.Belt2 | public / no-core | revise / description_ready | scripts/clothing/clothing_others.txt:735: Clothing/BodyLocation=Belt. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C180 | M017 |
| Base.BerryBlack | public / core | revise / description_ready | scripts/items_food.txt:1261의 exact H=-10, T=-1; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C020 | M004 |
| Base.BerryBlue | public / core | revise / description_ready | scripts/items_food.txt:1284의 exact H=-10, T=-1; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C020 | M004 |
| Base.BerryGeneric1 | public / core | revise / description_ready | scripts/items_food.txt:1307의 exact H=-5, T=-1; EvolvedRecipe 재료 선언 확인; OnEat_WildFoodGeneric와 recipecode:1041의 실제 독성 분기. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C039 | M004 |
| Base.BerryGeneric2 | public / core | revise / description_ready | scripts/items_food.txt:1331의 exact H=-10, T=-1; EvolvedRecipe 재료 선언 확인; OnEat_WildFoodGeneric와 recipecode:1041의 실제 독성 분기. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C039 | M004 |
| Base.BerryGeneric3 | public / core | revise / description_ready | scripts/items_food.txt:1355의 exact H=-5, T=-1; EvolvedRecipe 재료 선언 확인; OnEat_WildFoodGeneric와 recipecode:1041의 실제 독성 분기. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C039 | M004 |
| Base.BerryGeneric4 | public / core | revise / description_ready | scripts/items_food.txt:1379의 exact H=-10, T=-1; EvolvedRecipe 재료 선언 확인; OnEat_WildFoodGeneric와 recipecode:1041의 실제 독성 분기. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C039 | M004 |
| Base.BerryGeneric5 | public / core | revise / description_ready | scripts/items_food.txt:1403의 exact H=-10, T=-1; EvolvedRecipe 재료 선언 확인; OnEat_WildFoodGeneric와 recipecode:1041의 실제 독성 분기. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C039 | M004 |
| Base.BerryPoisonIvy | public / core | revise / description_ready | scripts/items_food.txt:1427의 exact H=-5, T=-1; EvolvedRecipe 재료 선언 확인; OnEat_WildFoodGeneric와 recipecode:1041의 실제 독성 분기. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C039 | M004 |
| Base.Beverage | public / no-core | revise / description_ready | undefined; scripts/evolvedrecipes.txt:298 exact BaseItem→ResultItem 관계와 items_food Food/CustomContextMenu=Drink/ReplaceOnUse. inventory menu:124/414/2976 및 기존 소비 경로. 정적 H/T 부재는 동적 결과의 무효가 아니며 고정 효과량을 후보에 넣지 않음. | C225 | M218 |
| Base.Beverage2 | public / no-core | revise / description_ready | undefined; scripts/evolvedrecipes.txt:307 exact BaseItem→ResultItem 관계와 items_food Food/CustomContextMenu=Drink/ReplaceOnUse. inventory menu:124/414/2976 및 기존 소비 경로. 정적 H/T 부재는 동적 결과의 무효가 아니며 고정 효과량을 후보에 넣지 않음. | C226 | M218 |
| Base.BigGasTank1 | public / core | revise / description_ready | scripts/vehicles/vehiclesitems.txt:523; exact VehicleType=1/MaxCapacity, template_gastank의 Gasoline container·conditionAffectsCapacity. 1/2/3을 성능 등급으로 보지 않는다. | C040 | M045 |
| Base.BigGasTank2 | public / core | revise / description_ready | scripts/vehicles/vehiclesitems.txt:571; exact VehicleType=2/MaxCapacity, template_gastank의 Gasoline container·conditionAffectsCapacity. 1/2/3을 성능 등급으로 보지 않는다. | C040 | M045 |
| Base.BigGasTank3 | public / core | revise / description_ready | scripts/vehicles/vehiclesitems.txt:619; exact VehicleType=3/MaxCapacity, template_gastank의 Gasoline container·conditionAffectsCapacity. 1/2/3을 성능 등급으로 보지 않는다. | C040 | M045 |
| Base.BigTrunk1 | public / core | revise / description_ready | scripts/vehicles/vehiclesitems.txt:724; exact VehicleType=1/MaxCapacity와 seat/trunk container 선언. 수납 부품을 모두 자유롭게 탈착 가능한 물건으로 묶지 않는다. | C041 | M046 |
| Base.BigTrunk2 | public / core | revise / description_ready | scripts/vehicles/vehiclesitems.txt:784; exact VehicleType=2/MaxCapacity와 seat/trunk container 선언. 수납 부품을 모두 자유롭게 탈착 가능한 물건으로 묶지 않는다. | C041 | M046 |
| Base.BigTrunk3 | public / core | revise / description_ready | scripts/vehicles/vehiclesitems.txt:829; exact VehicleType=3/MaxCapacity와 seat/trunk container 선언. 수납 부품을 모두 자유롭게 탈착 가능한 물건으로 묶지 않는다. | C041 | M046 |
| Base.Bikini_Pattern01 | public / no-core | revise / description_ready | scripts/clothing/clothing_others.txt:471: Clothing/BodyLocation=Underwear. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C181 | M017 |
| Base.Bikini_TINT | public / no-core | revise / description_ready | scripts/clothing/clothing_others.txt:460: Clothing/BodyLocation=Underwear. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C181 | M017 |
| Base.Biscuit | public / core | revise / description_ready | scripts/items_food.txt:7178의 exact H=-5, T=미선언; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C004 | M004 |
| Base.BlackSage | public / core | revise / description_ready | scripts/items_food.txt:4096의 exact H=-1, T=미선언; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C004 | M004 |
| Base.Blackbeans | public / core | revise / description_ready | scripts/items_food.txt:5789의 exact H=-10, T=미선언; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C004 | M004 |
| Base.Bleach | public / core | revise / description_ready | §후속 item별 판정: Poison/PoisonPower와 혈흔 제거 경로 | C042 | M047 |
| Base.BleachEmpty | public / core | keep / description_ready | 각 exact CanStoreWater 및 ReplaceOnUseOn=WaterSource 관계를 확인했다. 물의 안전성이나 소독 효과는 주장하지 않는다. | C003 | M040 |
| Base.BlowTorch | public / core | keep / description_ready | 현재 승인 금속 접합 도구의 용도가 구체적이다. Refill Blow Torch 관계를 재사용하며 숫자나 전 기능 목록을 강제하지 않는다. | C003 | M048 |
| Base.BluePen | public / core | revise / description_ready | scripts/items_weapons.txt:3994; exact Write/pen tags, 기존 문서 작성 경로 및 ISWorldMapSymbols:canWrite의 type/tag 선택. | C043 | M049 |
| Base.BobPic | public / core | review_hold / review_required | scripts/items.txt:211; 사진의 Normal 정체성/원문 locator 확인; 보기·놀이·수집 action 의 실제 사용 경로는 미확정. 유사 매체의 재생·학습 기능을 전이하지 않음. 필요한 추가 근거는 이 exact item의 해당 행동/재료 입력 또는 효과를 명시하는 vanilla source 관계이며, current admission 부재를 해소할 승인만으로 대체하지 않음. | C015 | M050 |
| Base.Boilersuit | public / no-core | revise / description_ready | scripts/clothing/clothing_suits.txt:76: Clothing/BodyLocation=Boilersuit. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C182 | M017 |
| Base.Boilersuit_BlueRed | public / no-core | revise / description_ready | scripts/clothing/clothing_suits.txt:95: Clothing/BodyLocation=Boilersuit. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C182 | M017 |
| Base.Boilersuit_Flying | public / no-core | revise / description_ready | scripts/clothing/clothing_suits.txt:127: Clothing/BodyLocation=Boilersuit. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C182 | M017 |
| Base.Boilersuit_Prisoner | public / no-core | revise / description_ready | scripts/clothing/clothing_suits.txt:143: Clothing/BodyLocation=Boilersuit. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C182 | M017 |
| Base.Boilersuit_PrisonerKhaki | public / no-core | revise / description_ready | scripts/clothing/clothing_suits.txt:159: Clothing/BodyLocation=Boilersuit. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C182 | M017 |
| Base.Boilersuit_Yellow | public / no-core | revise / description_ready | scripts/clothing/clothing_suits.txt:111: Clothing/BodyLocation=Boilersuit. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C182 | M017 |
| Base.BoobTube | public / no-core | revise / description_ready | scripts/clothing/clothing_shirts.txt:1222: Clothing/BodyLocation=Tshirt. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C183 | M017 |
| Base.BoobTubeSmall | public / no-core | revise / description_ready | scripts/clothing/clothing_shirts.txt:1234: Clothing/BodyLocation=Tshirt. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C183 | M017 |
| Base.Book | public / core | revise / description_ready | §후속 item별 판정: exact 읽기 효과 선언 또는 CanBeWrite/페이지·필기구 조건을 구분했다. | C044 | M051 |
| Base.BookBlacksmith1 | public / core | review_hold / review_required | §학습: legacy Blacksmith 선언만으로 활성 B41 perk/XP 효과를 결속하지 못했다. 다른 기술서에서 전파하지 않는다. 남은 입력은 정상 B41에서 이 legacy 단조 recipe/Anvil·Blacksmith 기술을 사용할 수 있는 근거 또는 실제 활성 대체 경로다. source successor 미발행이나 기존 core 부재 자체를 보류 사유로 삼지 않음. | C045 | M216 |
| Base.BookBlacksmith2 | public / core | review_hold / review_required | §학습: legacy Blacksmith 선언만으로 활성 B41 perk/XP 효과를 결속하지 못했다. 다른 기술서에서 전파하지 않는다. 남은 입력은 정상 B41에서 이 legacy 단조 recipe/Anvil·Blacksmith 기술을 사용할 수 있는 근거 또는 실제 활성 대체 경로다. source successor 미발행이나 기존 core 부재 자체를 보류 사유로 삼지 않음. | C045 | M216 |
| Base.BookBlacksmith3 | public / core | review_hold / review_required | §학습: legacy Blacksmith 선언만으로 활성 B41 perk/XP 효과를 결속하지 못했다. 다른 기술서에서 전파하지 않는다. 남은 입력은 정상 B41에서 이 legacy 단조 recipe/Anvil·Blacksmith 기술을 사용할 수 있는 근거 또는 실제 활성 대체 경로다. source successor 미발행이나 기존 core 부재 자체를 보류 사유로 삼지 않음. | C045 | M216 |
| Base.BookBlacksmith4 | public / core | review_hold / review_required | §학습: legacy Blacksmith 선언만으로 활성 B41 perk/XP 효과를 결속하지 못했다. 다른 기술서에서 전파하지 않는다. 남은 입력은 정상 B41에서 이 legacy 단조 recipe/Anvil·Blacksmith 기술을 사용할 수 있는 근거 또는 실제 활성 대체 경로다. source successor 미발행이나 기존 core 부재 자체를 보류 사유로 삼지 않음. | C045 | M216 |
| Base.BookBlacksmith5 | public / core | review_hold / review_required | §학습: legacy Blacksmith 선언만으로 활성 B41 perk/XP 효과를 결속하지 못했다. 다른 기술서에서 전파하지 않는다. 남은 입력은 정상 B41에서 이 legacy 단조 recipe/Anvil·Blacksmith 기술을 사용할 수 있는 근거 또는 실제 활성 대체 경로다. source successor 미발행이나 기존 core 부재 자체를 보류 사유로 삼지 않음. | C045 | M216 |
| Base.BookCarpentry1 | public / core | revise / description_ready | §학습 문구 87개: 해당 exact SkillTrained 또는 TeachedRecipes/knowledge token의 source를 구분했다. | C026 | M053 |
| Base.BookCarpentry2 | public / core | revise / description_ready | §학습 문구 87개: 해당 exact SkillTrained 또는 TeachedRecipes/knowledge token의 source를 구분했다. | C026 | M053 |
| Base.BookCarpentry3 | public / core | revise / description_ready | §학습 문구 87개: 해당 exact SkillTrained 또는 TeachedRecipes/knowledge token의 source를 구분했다. | C026 | M053 |
| Base.BookCarpentry4 | public / core | revise / description_ready | §학습 문구 87개: 해당 exact SkillTrained 또는 TeachedRecipes/knowledge token의 source를 구분했다. | C026 | M053 |
| Base.BookCarpentry5 | public / core | revise / description_ready | §학습 문구 87개: 해당 exact SkillTrained 또는 TeachedRecipes/knowledge token의 source를 구분했다. | C026 | M053 |
| Base.BookCooking1 | public / core | revise / description_ready | §학습 문구 87개: 해당 exact SkillTrained 또는 TeachedRecipes/knowledge token의 source를 구분했다. | C026 | M053 |
| Base.BookCooking2 | public / core | revise / description_ready | §학습 문구 87개: 해당 exact SkillTrained 또는 TeachedRecipes/knowledge token의 source를 구분했다. | C026 | M053 |
| Base.BookCooking3 | public / core | revise / description_ready | §학습 문구 87개: 해당 exact SkillTrained 또는 TeachedRecipes/knowledge token의 source를 구분했다. | C026 | M053 |
| Base.BookCooking4 | public / core | revise / description_ready | §학습 문구 87개: 해당 exact SkillTrained 또는 TeachedRecipes/knowledge token의 source를 구분했다. | C026 | M053 |
| Base.BookCooking5 | public / core | revise / description_ready | §학습 문구 87개: 해당 exact SkillTrained 또는 TeachedRecipes/knowledge token의 source를 구분했다. | C026 | M053 |
| Base.BookElectrician1 | public / core | revise / description_ready | §학습 문구 87개: 해당 exact SkillTrained 또는 TeachedRecipes/knowledge token의 source를 구분했다. | C026 | M053 |
| Base.BookElectrician2 | public / core | revise / description_ready | §학습 문구 87개: 해당 exact SkillTrained 또는 TeachedRecipes/knowledge token의 source를 구분했다. | C026 | M053 |
| Base.BookElectrician3 | public / core | revise / description_ready | §학습 문구 87개: 해당 exact SkillTrained 또는 TeachedRecipes/knowledge token의 source를 구분했다. | C026 | M053 |
| Base.BookElectrician4 | public / core | revise / description_ready | §학습 문구 87개: 해당 exact SkillTrained 또는 TeachedRecipes/knowledge token의 source를 구분했다. | C026 | M053 |
| Base.BookElectrician5 | public / core | revise / description_ready | §학습 문구 87개: 해당 exact SkillTrained 또는 TeachedRecipes/knowledge token의 source를 구분했다. | C026 | M053 |
| Base.BookFarming1 | public / core | revise / description_ready | §학습 문구 87개: 해당 exact SkillTrained 또는 TeachedRecipes/knowledge token의 source를 구분했다. | C026 | M053 |
| Base.BookFarming2 | public / core | revise / description_ready | §학습 문구 87개: 해당 exact SkillTrained 또는 TeachedRecipes/knowledge token의 source를 구분했다. | C026 | M053 |
| Base.BookFarming3 | public / core | revise / description_ready | §학습 문구 87개: 해당 exact SkillTrained 또는 TeachedRecipes/knowledge token의 source를 구분했다. | C026 | M053 |
| Base.BookFarming4 | public / core | revise / description_ready | §학습 문구 87개: 해당 exact SkillTrained 또는 TeachedRecipes/knowledge token의 source를 구분했다. | C026 | M053 |
| Base.BookFarming5 | public / core | revise / description_ready | §학습 문구 87개: 해당 exact SkillTrained 또는 TeachedRecipes/knowledge token의 source를 구분했다. | C026 | M053 |
| Base.BookFirstAid1 | public / core | revise / description_ready | §학습 문구 87개: 해당 exact SkillTrained 또는 TeachedRecipes/knowledge token의 source를 구분했다. | C026 | M053 |
| Base.BookFirstAid2 | public / core | revise / description_ready | §학습 문구 87개: 해당 exact SkillTrained 또는 TeachedRecipes/knowledge token의 source를 구분했다. | C026 | M053 |
| Base.BookFirstAid3 | public / core | revise / description_ready | §학습 문구 87개: 해당 exact SkillTrained 또는 TeachedRecipes/knowledge token의 source를 구분했다. | C026 | M053 |
| Base.BookFirstAid4 | public / core | revise / description_ready | §학습 문구 87개: 해당 exact SkillTrained 또는 TeachedRecipes/knowledge token의 source를 구분했다. | C026 | M053 |
| Base.BookFirstAid5 | public / core | revise / description_ready | §학습 문구 87개: 해당 exact SkillTrained 또는 TeachedRecipes/knowledge token의 source를 구분했다. | C026 | M053 |
| Base.BookFishing1 | public / core | revise / description_ready | §학습 문구 87개: 해당 exact SkillTrained 또는 TeachedRecipes/knowledge token의 source를 구분했다. | C026 | M053 |
| Base.BookFishing2 | public / core | revise / description_ready | §학습 문구 87개: 해당 exact SkillTrained 또는 TeachedRecipes/knowledge token의 source를 구분했다. | C026 | M053 |
| Base.BookFishing3 | public / core | revise / description_ready | §학습 문구 87개: 해당 exact SkillTrained 또는 TeachedRecipes/knowledge token의 source를 구분했다. | C026 | M053 |
| Base.BookFishing4 | public / core | revise / description_ready | §학습 문구 87개: 해당 exact SkillTrained 또는 TeachedRecipes/knowledge token의 source를 구분했다. | C026 | M053 |
| Base.BookFishing5 | public / core | revise / description_ready | §학습 문구 87개: 해당 exact SkillTrained 또는 TeachedRecipes/knowledge token의 source를 구분했다. | C026 | M053 |
| Base.BookForaging1 | public / core | revise / description_ready | §학습 문구 87개: 해당 exact SkillTrained 또는 TeachedRecipes/knowledge token의 source를 구분했다. | C026 | M053 |
| Base.BookForaging2 | public / core | revise / description_ready | §학습 문구 87개: 해당 exact SkillTrained 또는 TeachedRecipes/knowledge token의 source를 구분했다. | C026 | M053 |
| Base.BookForaging3 | public / core | revise / description_ready | §학습 문구 87개: 해당 exact SkillTrained 또는 TeachedRecipes/knowledge token의 source를 구분했다. | C026 | M053 |
| Base.BookForaging4 | public / core | revise / description_ready | §학습 문구 87개: 해당 exact SkillTrained 또는 TeachedRecipes/knowledge token의 source를 구분했다. | C026 | M053 |
| Base.BookForaging5 | public / core | revise / description_ready | §학습 문구 87개: 해당 exact SkillTrained 또는 TeachedRecipes/knowledge token의 source를 구분했다. | C026 | M053 |
| Base.BookMechanic1 | public / core | revise / description_ready | §학습 문구 87개: 해당 exact SkillTrained 또는 TeachedRecipes/knowledge token의 source를 구분했다. | C026 | M053 |
| Base.BookMechanic2 | public / core | revise / description_ready | §학습 문구 87개: 해당 exact SkillTrained 또는 TeachedRecipes/knowledge token의 source를 구분했다. | C026 | M053 |
| Base.BookMechanic3 | public / core | revise / description_ready | §학습 문구 87개: 해당 exact SkillTrained 또는 TeachedRecipes/knowledge token의 source를 구분했다. | C026 | M053 |
| Base.BookMechanic4 | public / core | revise / description_ready | §학습 문구 87개: 해당 exact SkillTrained 또는 TeachedRecipes/knowledge token의 source를 구분했다. | C026 | M053 |
| Base.BookMechanic5 | public / core | revise / description_ready | §학습 문구 87개: 해당 exact SkillTrained 또는 TeachedRecipes/knowledge token의 source를 구분했다. | C026 | M053 |
| Base.BookMetalWelding1 | public / core | revise / description_ready | §학습 문구 87개: 해당 exact SkillTrained 또는 TeachedRecipes/knowledge token의 source를 구분했다. | C026 | M053 |
| Base.BookMetalWelding2 | public / core | revise / description_ready | §학습 문구 87개: 해당 exact SkillTrained 또는 TeachedRecipes/knowledge token의 source를 구분했다. | C026 | M053 |
| Base.BookMetalWelding3 | public / core | revise / description_ready | §학습 문구 87개: 해당 exact SkillTrained 또는 TeachedRecipes/knowledge token의 source를 구분했다. | C026 | M053 |
| Base.BookMetalWelding4 | public / core | revise / description_ready | §학습 문구 87개: 해당 exact SkillTrained 또는 TeachedRecipes/knowledge token의 source를 구분했다. | C026 | M053 |
| Base.BookMetalWelding5 | public / core | revise / description_ready | §학습 문구 87개: 해당 exact SkillTrained 또는 TeachedRecipes/knowledge token의 source를 구분했다. | C026 | M053 |
| Base.BookTailoring1 | public / core | revise / description_ready | §학습 문구 87개: 해당 exact SkillTrained 또는 TeachedRecipes/knowledge token의 source를 구분했다. | C026 | M053 |
| Base.BookTailoring2 | public / core | revise / description_ready | §학습 문구 87개: 해당 exact SkillTrained 또는 TeachedRecipes/knowledge token의 source를 구분했다. | C026 | M053 |
| Base.BookTailoring3 | public / core | revise / description_ready | §학습 문구 87개: 해당 exact SkillTrained 또는 TeachedRecipes/knowledge token의 source를 구분했다. | C026 | M053 |
| Base.BookTailoring4 | public / core | revise / description_ready | §학습 문구 87개: 해당 exact SkillTrained 또는 TeachedRecipes/knowledge token의 source를 구분했다. | C026 | M053 |
| Base.BookTailoring5 | public / core | revise / description_ready | §학습 문구 87개: 해당 exact SkillTrained 또는 TeachedRecipes/knowledge token의 source를 구분했다. | C026 | M053 |
| Base.BookTrapping1 | public / core | revise / description_ready | §학습 문구 87개: 해당 exact SkillTrained 또는 TeachedRecipes/knowledge token의 source를 구분했다. | C026 | M053 |
| Base.BookTrapping2 | public / core | revise / description_ready | §학습 문구 87개: 해당 exact SkillTrained 또는 TeachedRecipes/knowledge token의 source를 구분했다. | C026 | M053 |
| Base.BookTrapping3 | public / core | revise / description_ready | §학습 문구 87개: 해당 exact SkillTrained 또는 TeachedRecipes/knowledge token의 source를 구분했다. | C026 | M053 |
| Base.BookTrapping4 | public / core | revise / description_ready | §학습 문구 87개: 해당 exact SkillTrained 또는 TeachedRecipes/knowledge token의 source를 구분했다. | C026 | M053 |
| Base.BookTrapping5 | public / core | revise / description_ready | §학습 문구 87개: 해당 exact SkillTrained 또는 TeachedRecipes/knowledge token의 source를 구분했다. | C026 | M053 |
| Base.BorisBadger | public / core | review_hold / review_required | scripts/newitems.txt:4791; 장난감의 Normal 정체성/원문 locator 확인; 보기·놀이·수집 action 의 실제 사용 경로는 미확정. 유사 매체의 재생·학습 기능을 전이하지 않음. 필요한 추가 근거는 이 exact item의 해당 행동/재료 입력 또는 효과를 명시하는 vanilla source 관계이며, current admission 부재를 해소할 승인만으로 대체하지 않음. | C015 | M054 |
| Base.BouillonCube | public / core | keep / description_ready | scripts/items_food.txt:8418; Food EvolvedRecipe 조리 재료로 확인; 현행 조리 재료 목적 유지. H/T/맛을 추가 보장하지 않음. | C046 | M055 |
| Base.Bowl | public / core | revise / description_ready | §조리 문구 32개: 이 exact item의 input/result/keep 역할과 원본 recipe를 분리 검토했다. | C026 | M027 |
| Base.BoxOfJars | public / core | keep / description_ready | 병 상자 개봉 input/result와 현재 개봉 용도가 일치한다. | C003 | M056 |
| Base.Boxers_Hearts | public / no-core | revise / description_ready | scripts/clothing/clothing_underwear.txt:108: Clothing/BodyLocation=UnderwearBottom. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C184 | M017 |
| Base.Boxers_RedStripes | public / no-core | revise / description_ready | scripts/clothing/clothing_underwear.txt:144: Clothing/BodyLocation=UnderwearBottom. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C184 | M017 |
| Base.Boxers_Silk_Black | public / no-core | revise / description_ready | scripts/clothing/clothing_underwear.txt:120: Clothing/BodyLocation=UnderwearBottom. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C184 | M017 |
| Base.Boxers_Silk_Red | public / no-core | revise / description_ready | scripts/clothing/clothing_underwear.txt:132: Clothing/BodyLocation=UnderwearBottom. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C184 | M017 |
| Base.Boxers_White | public / no-core | revise / description_ready | scripts/clothing/clothing_underwear.txt:156: Clothing/BodyLocation=UnderwearBottom. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C184 | M017 |
| Base.Bra_Strapless_AnimalPrint | public / no-core | revise / description_ready | scripts/clothing/clothing_underwear.txt:387: Clothing/BodyLocation=UnderwearTop. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C185 | M017 |
| Base.Bra_Strapless_Black | public / no-core | revise / description_ready | scripts/clothing/clothing_underwear.txt:3: Clothing/BodyLocation=UnderwearTop. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C185 | M017 |
| Base.Bra_Strapless_FrillyBlack | public / no-core | revise / description_ready | scripts/clothing/clothing_underwear.txt:423: Clothing/BodyLocation=UnderwearTop. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C185 | M017 |
| Base.Bra_Strapless_FrillyPink | public / no-core | revise / description_ready | scripts/clothing/clothing_underwear.txt:447: Clothing/BodyLocation=UnderwearTop. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C185 | M017 |
| Base.Bra_Strapless_FrillyRed | public / no-core | revise / description_ready | scripts/clothing/clothing_underwear.txt:471: Clothing/BodyLocation=UnderwearTop. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C185 | M017 |
| Base.Bra_Strapless_RedSpots | public / no-core | revise / description_ready | scripts/clothing/clothing_underwear.txt:18: Clothing/BodyLocation=UnderwearTop. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C185 | M017 |
| Base.Bra_Strapless_White | public / no-core | revise / description_ready | scripts/clothing/clothing_underwear.txt:30: Clothing/BodyLocation=UnderwearTop. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C185 | M017 |
| Base.Bra_Straps_AnimalPrint | public / no-core | revise / description_ready | scripts/clothing/clothing_underwear.txt:399: Clothing/BodyLocation=UnderwearTop. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C185 | M017 |
| Base.Bra_Straps_Black | public / no-core | revise / description_ready | scripts/clothing/clothing_underwear.txt:42: Clothing/BodyLocation=UnderwearTop. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C185 | M017 |
| Base.Bra_Straps_FrillyBlack | public / no-core | revise / description_ready | scripts/clothing/clothing_underwear.txt:411: Clothing/BodyLocation=UnderwearTop. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C185 | M017 |
| Base.Bra_Straps_FrillyPink | public / no-core | revise / description_ready | scripts/clothing/clothing_underwear.txt:435: Clothing/BodyLocation=UnderwearTop. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C185 | M017 |
| Base.Bra_Straps_FrillyRed | public / no-core | revise / description_ready | scripts/clothing/clothing_underwear.txt:459: Clothing/BodyLocation=UnderwearTop. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C185 | M017 |
| Base.Bra_Straps_White | public / no-core | revise / description_ready | scripts/clothing/clothing_underwear.txt:57: Clothing/BodyLocation=UnderwearTop. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C185 | M017 |
| Base.Bracelet_BangleLeftGold | public / core | keep / description_ready | scripts/clothing/clothing_jewellery.txt:1125의 Clothing/BodyLocation=LeftWrist와 현재 착용 목적 일치. 수치 추가나 감염/위장 효과를 강제하지 않는다. §기본 착용 재판정의 추가 Wear/self FullType 경로를 동일하게 적용; existing core 유무를 source 충분성 기준으로 삼지 않음. | C018 | M214 |
| Base.Bracelet_BangleLeftSilver | public / core | keep / description_ready | scripts/clothing/clothing_jewellery.txt:1185의 Clothing/BodyLocation=LeftWrist와 현재 착용 목적 일치. 수치 추가나 감염/위장 효과를 강제하지 않는다. | C018 | M018 |
| Base.Bracelet_BangleRightGold | public / no-core | revise / description_ready | scripts/clothing/clothing_jewellery.txt:1110: Clothing/BodyLocation=RightWrist. §기본 착용 재판정의 추가 Wear(RightWrist)→동일 FullType 착용 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C186 | M214 |
| Base.Bracelet_BangleRightSilver | public / no-core | revise / description_ready | scripts/clothing/clothing_jewellery.txt:1170: Clothing/BodyLocation=RightWrist. §기본 착용 재판정의 추가 Wear(RightWrist)→동일 FullType 착용 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C186 | M214 |
| Base.Bracelet_ChainLeftGold | public / core | keep / description_ready | scripts/clothing/clothing_jewellery.txt:1155의 Clothing/BodyLocation=LeftWrist와 현재 착용 목적 일치. 수치 추가나 감염/위장 효과를 강제하지 않는다. | C018 | M018 |
| Base.Bracelet_ChainLeftSilver | public / core | keep / description_ready | scripts/clothing/clothing_jewellery.txt:1215의 Clothing/BodyLocation=LeftWrist와 현재 착용 목적 일치. 수치 추가나 감염/위장 효과를 강제하지 않는다. | C018 | M018 |
| Base.Bracelet_ChainRightGold | public / no-core | revise / description_ready | scripts/clothing/clothing_jewellery.txt:1140: Clothing/BodyLocation=RightWrist. §기본 착용 재판정의 추가 Wear(RightWrist)→동일 FullType 착용 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C186 | M214 |
| Base.Bracelet_ChainRightSilver | public / no-core | revise / description_ready | scripts/clothing/clothing_jewellery.txt:1200: Clothing/BodyLocation=RightWrist. §기본 착용 재판정의 추가 Wear(RightWrist)→동일 FullType 착용 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C186 | M214 |
| Base.Bracelet_LeftFriendshipTINT | public / no-core | revise / description_ready | scripts/clothing/clothing_jewellery.txt:1245: Clothing/BodyLocation=LeftWrist. §기본 착용 재판정의 추가 Wear(LeftWrist)→동일 FullType 착용 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C187 | M214 |
| Base.Bracelet_RightFriendshipTINT | public / core | keep / description_ready | scripts/clothing/clothing_jewellery.txt:1230의 Clothing/BodyLocation=RightWrist와 현재 착용 목적 일치. 수치 추가나 감염/위장 효과를 강제하지 않는다. | C018 | M018 |
| Base.Bread | public / core | revise / description_ready | scripts/items_food.txt:4461의 exact H=-30, T=미선언; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C004 | M004 |
| Base.BreadDough | public / core | revise / description_ready | scripts/items_food.txt:5179의 exact H=-24, T=15; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C025 | M012 |
| Base.BreadKnife | public / core | revise / description_ready | scripts/items_weapons.txt:3846; exact Weapon/damage=0.1–0.4, 해당 Attach … to Spear input. 칼/식기·도구의 이름만으로 다른 작동을 추정하지 않음. | C047 | M057 |
| Base.BreadSlices | public / no-core | revise / description_ready | scripts/items_food.txt:5469의 exact H=-10, T=미선언; EvolvedRecipe 재료 선언 확인; ReplaceOnCooked=Toast, 다른 상태 item과 구분. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C004 | M004 |
| Base.Bricktoys | public / core | review_hold / review_required | scripts/newitems.txt:955: §남은 혼합 역할: 현재 놀이 assertion을 실제 게임 플레이/지루함 감소에 결속하지 못했다. Normal 소품과 실제 놀이 기능을 구분한다. 필요한 추가 근거는 이 exact item의 해당 행동/재료 입력 또는 효과를 명시하는 vanilla source 관계이며, current admission 부재를 해소할 승인만으로 대체하지 않음. | C002 | M021 |
| Base.Briefcase | public / core | revise / description_ready | scripts/clothing/clothing_bags.txt:535의 exact Container/Capacity=7. 보관·운반 역할이 명확하며 이름에 따른 내용물 제한/냉장 효과는 추가하지 않는다. | C022 | M023 |
| Base.Briefs_AnimalPrints | public / no-core | revise / description_ready | scripts/clothing/clothing_underwear.txt:180: Clothing/BodyLocation=UnderwearBottom. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C184 | M017 |
| Base.Briefs_SmallTrunks_Black | public / no-core | revise / description_ready | scripts/clothing/clothing_underwear.txt:192: Clothing/BodyLocation=UnderwearBottom. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C184 | M017 |
| Base.Briefs_SmallTrunks_Blue | public / no-core | revise / description_ready | scripts/clothing/clothing_underwear.txt:204: Clothing/BodyLocation=UnderwearBottom. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C184 | M017 |
| Base.Briefs_SmallTrunks_Red | public / no-core | revise / description_ready | scripts/clothing/clothing_underwear.txt:216: Clothing/BodyLocation=UnderwearBottom. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C184 | M017 |
| Base.Briefs_SmallTrunks_WhiteTINT | public / no-core | revise / description_ready | scripts/clothing/clothing_underwear.txt:228: Clothing/BodyLocation=UnderwearBottom. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C184 | M017 |
| Base.Briefs_White | public / no-core | revise / description_ready | scripts/clothing/clothing_underwear.txt:168: Clothing/BodyLocation=UnderwearBottom. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C184 | M017 |
| Base.Broccoli | public / core | revise / description_ready | scripts/items_food.txt:1151의 exact H=-9, T=-4; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C020 | M004 |
| Base.BrokenFishingNet | public / core | keep / description_ready | 현재 고장 난 통발의 상태 설명을 유지한다. 다시 포획 가능한 정상 FishingNet과 구분한다. | C003 | M058 |
| Base.Broom | empty / no-core | revise / description_ready | §후속 item별 판정: ClearAshes 및 bleach+도구 혈흔 제거 경로 | C048 | M059 |
| Base.BucketConcreteFull | public / no-core | review_hold / review_required | scripts/items.txt:672; Drainable 선언만으로 현행 제작·수리 소비 경로 미확정; exact recipe/action 입력 관계 필요. 필요한 추가 근거는 이 exact item의 해당 행동/재료 입력 또는 효과를 명시하는 vanilla source 관계이며, current admission 부재를 해소할 승인만으로 대체하지 않음. | C049 | M060 |
| Base.BucketEmpty | public / no-core | revise / description_ready | scripts/items.txt:92: CanStoreWater=TRUE, ReplaceOnUseOn=WaterSource-BucketWaterFull. §빈 물 용기와 같은 exact 물 저장/전환 사실을 재사용하며 음용 안전성·현재 내용물은 추정하지 않는다. | C038 | M041 |
| Base.BucketPlasterFull | public / no-core | revise / description_ready | scripts/items.txt:688; ISPaintMenu.lua:58; ISPaintCursor 경유, plaster 가능대상·목공 level4 조건. | C050 | M011 |
| Base.BucketWaterFull | public / no-core | revise / description_ready | scripts/items.txt:704: CanStoreWater=TRUE, ReplaceOnUseOn=WaterSource-BucketWaterFull. §빈 물 용기와 같은 exact 물 저장/전환 사실을 재사용하며 음용 안전성·현재 내용물은 추정하지 않는다. | C038 | M041 |
| Base.Bullets38 | public / core | revise / description_ready | §후속 item별 판정: exact 상자 input/result 또는 낱알 AmmoType 관계를 확인했다. | C001 | M001 |
| Base.Bullets38Box | public / core | revise / description_ready | §후속 item별 판정: exact 상자 input/result 또는 낱알 AmmoType 관계를 확인했다. | C001 | M001 |
| Base.Bullets44 | public / core | revise / description_ready | §후속 item별 판정: exact 상자 input/result 또는 낱알 AmmoType 관계를 확인했다. | C001 | M001 |
| Base.Bullets44Box | public / core | revise / description_ready | §후속 item별 판정: exact 상자 input/result 또는 낱알 AmmoType 관계를 확인했다. | C001 | M001 |
| Base.Bullets45 | public / core | revise / description_ready | §후속 item별 판정: exact 상자 input/result 또는 낱알 AmmoType 관계를 확인했다. | C001 | M001 |
| Base.Bullets45Box | public / core | revise / description_ready | §후속 item별 판정: exact 상자 input/result 또는 낱알 AmmoType 관계를 확인했다. | C001 | M001 |
| Base.Bullets9mm | public / core | revise / description_ready | §후속 item별 판정: exact 상자 input/result 또는 낱알 AmmoType 관계를 확인했다. | C001 | M001 |
| Base.Bullets9mmBox | public / core | revise / description_ready | §후속 item별 판정: exact 상자 input/result 또는 낱알 AmmoType 관계를 확인했다. | C001 | M001 |
| Base.BunnySuitBlack | public / no-core | revise / description_ready | scripts/clothing/clothing_others.txt:834: Clothing/BodyLocation=Underwear. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C181 | M017 |
| Base.BunnySuitPink | public / no-core | revise / description_ready | scripts/clothing/clothing_others.txt:845: Clothing/BodyLocation=Underwear. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C181 | M017 |
| Base.BunnyTail | public / no-core | revise / description_ready | scripts/clothing/clothing_others.txt:824: Clothing/BodyLocation=Tail. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C188 | M017 |
| Base.Burger | public / core | revise / description_ready | scripts/items_food.txt:5551의 exact H=-25, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C012 | M012 |
| Base.BurgerRecipe | public / no-core | revise / description_ready | scripts/items_food.txt:5571의 exact H=-20, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C012 | M012 |
| Base.Burrito | public / core | revise / description_ready | scripts/items_food.txt:5809의 exact H=-25, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C012 | M012 |
| Base.BurritoRecipe | public / no-core | revise / description_ready | scripts/items_food.txt:7086의 exact H=-5, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C012 | M012 |
| Base.Butter | public / core | revise / description_ready | scripts/items_food.txt:4481의 exact H=-24, T=미선언; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C004 | M004 |
| Base.ButterKnife | public / core | revise / description_ready | scripts/items_weapons.txt:3750; exact Weapon/damage=0.1–0.4, 해당 Attach … to Spear input. 칼/식기·도구의 이름만으로 다른 작동을 추정하지 않음. | C047 | M057 |
| Base.Button | public / core | review_hold / review_required | scripts/newitems.txt:296: Normal Button의 의류 부착/수선 사용 경로를 결속하지 못했다. 필요한 추가 근거는 이 exact item의 해당 행동/재료 입력 또는 효과를 명시하는 vanilla source 관계이며, current admission 부재를 해소할 승인만으로 대체하지 않음. | C002 | M061 |
| Base.CakeBatter | public / core | revise / description_ready | scripts/newitems.txt:1401; recipes.txt:928 Place Cake in Baking Pan 입력. | C051 | M026 |
| Base.CakeBlackForest | public / core | revise / description_ready | scripts/items_food.txt:5827의 exact H=-10, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C012 | M012 |
| Base.CakeCarrot | public / core | revise / description_ready | scripts/items_food.txt:5846의 exact H=-7, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C012 | M012 |
| Base.CakeCheeseCake | public / core | revise / description_ready | scripts/items_food.txt:5865의 exact H=-8, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C012 | M012 |
| Base.CakeChocolate | public / core | revise / description_ready | scripts/items_food.txt:5884의 exact H=-10, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C012 | M012 |
| Base.CakePrep | public / no-core | revise / description_ready | scripts/items_food.txt:5037의 exact H=-30, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C012 | M012 |
| Base.CakeRaw | public / no-core | revise / description_ready | scripts/items_food.txt:5409의 exact H=-15, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C012 | M012 |
| Base.CakeRedVelvet | public / core | revise / description_ready | scripts/items_food.txt:5903의 exact H=-8, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C012 | M012 |
| Base.CakeSlice | public / core | revise / description_ready | scripts/items_food.txt:5202의 exact H=-7, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C012 | M012 |
| Base.CakeStrawberryShortcake | public / core | revise / description_ready | scripts/items_food.txt:5922의 exact H=-8, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C012 | M012 |
| Base.Camera | public / no-core | revise / description_ready | scripts/newitems.txt:4526; Tags=Camera; recipecode.lua:1515 DismantleCamera selector→recipes.txt:4239 ElectronicsScrap. OnTest:444 favorite 제외·screwdriver 조건. 촬영 기능은 미확정이지만 분해 역할은 준비됨. | C071 | M219 |
| Base.CameraDisposable | public / no-core | revise / description_ready | scripts/newitems.txt:4537; Tags=Camera; recipecode.lua:1515 DismantleCamera selector→recipes.txt:4239 ElectronicsScrap. OnTest:444 favorite 제외·screwdriver 조건. 촬영 기능은 미확정이지만 분해 역할은 준비됨. | C071 | M219 |
| Base.CameraExpensive | public / no-core | revise / description_ready | scripts/newitems.txt:4548; Tags=Camera; recipecode.lua:1515 DismantleCamera selector→recipes.txt:4239 ElectronicsScrap. OnTest:444 favorite 제외·screwdriver 조건. 촬영 기능은 미확정이지만 분해 역할은 준비됨. | C071 | M219 |
| Base.CameraFilm | empty / no-core | review_hold / review_required | scripts/newitems.txt:4559 Type=Normal; 촬영·필름 소모/사진 결과 경로가 미결속이다. 같은 이름의 다른 item/현실 용도를 복사하지 않는다. 필요한 추가 근거는 이 exact item의 해당 행동/재료 입력 또는 효과를 명시하는 vanilla source 관계이며, current admission 부재를 해소할 승인만으로 대체하지 않음. | C052 | M062 |
| Base.Candle | public / core | revise / description_ready | scripts/items.txt:728; recipes.txt:566 Light Candle→CandleLit, 기존 CandleLit 발광/점화 경로 재사용. | C053 | M011 |
| Base.CandleLit | public / no-core | revise / description_ready | scripts/items.txt:741: StartFire tag 및 ISCampingMenu:129의 exact 선택→점화 메뉴. CandleLit의 기존 조명 성질과 별개로 불이 켜진 상태를 전제로 하며 임의 연료가 단독 점화된다고 하지 않는다. | C054 | M063 |
| Base.CandyCorn | public / core | revise / description_ready | scripts/items_food.txt:8439의 exact H=-10, T=미선언; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C004 | M004 |
| Base.CandyFruitSlices | public / core | revise / description_ready | scripts/items_food.txt:9185의 exact H=-5, T=미선언; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C004 | M004 |
| Base.CandyPackage | public / core | revise / description_ready | scripts/items_food.txt:3959; CantEat=TRUE; recipes.txt:440 Open Candy Package→OpenCandyPackage callback. | C055 | M064 |
| Base.Candycane | public / core | revise / description_ready | scripts/items_food.txt:3800의 exact H=-10, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C012 | M012 |
| Base.CannedBellPepper | public / no-core | revise / description_ready | scripts/newitems.txt:2809; scripts/recipes.txt:1598–1822의 해당 exact Open Jar input/result. 정적 HungerChange가 없으므로 섭취 수치를 생성하지 않는다. | C056 | M065 |
| Base.CannedBolognese | public / core | revise / description_ready | §조리 문구 32개: 이 exact item의 input/result/keep 역할과 원본 recipe를 분리 검토했다. | C026 | M027 |
| Base.CannedBologneseOpen | public / core | revise / description_ready | scripts/items_food.txt:103의 exact H=-24, T=미선언; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C004 | M004 |
| Base.CannedBroccoli | public / no-core | revise / description_ready | scripts/newitems.txt:2843; scripts/recipes.txt:1598–1822의 해당 exact Open Jar input/result. 정적 HungerChange가 없으므로 섭취 수치를 생성하지 않는다. | C056 | M065 |
| Base.CannedCabbage | public / core | revise / description_ready | scripts/newitems.txt:2826; recipes.txt:1787 Open Jar of Cabbage exact input→Cabbage. 내용물 직접 섭취 주장 없음. | C057 | M064 |
| Base.CannedCarrots | public / no-core | revise / description_ready | scripts/newitems.txt:2724; scripts/recipes.txt:1598–1822의 해당 exact Open Jar input/result. 정적 HungerChange가 없으므로 섭취 수치를 생성하지 않는다. | C056 | M065 |
| Base.CannedCarrots2 | public / core | revise / description_ready | §조리 문구 32개: 이 exact item의 input/result/keep 역할과 원본 recipe를 분리 검토했다. | C026 | M027 |
| Base.CannedCarrotsOpen | public / core | revise / description_ready | scripts/items_food.txt:130의 exact H=-12, T=-4; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C020 | M004 |
| Base.CannedChili | public / core | revise / description_ready | §조리 문구 32개: 이 exact item의 input/result/keep 역할과 원본 recipe를 분리 검토했다. | C026 | M027 |
| Base.CannedChiliOpen | public / core | revise / description_ready | scripts/items_food.txt:76의 exact H=-16, T=미선언; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C004 | M004 |
| Base.CannedCorn | public / core | revise / description_ready | §조리 문구 32개: 이 exact item의 input/result/keep 역할과 원본 recipe를 분리 검토했다. | C026 | M027 |
| Base.CannedCornOpen | public / core | revise / description_ready | scripts/items_food.txt:158의 exact H=-16, T=-4; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C020 | M004 |
| Base.CannedCornedBeef | public / core | revise / description_ready | §조리 문구 32개: 이 exact item의 input/result/keep 역할과 원본 recipe를 분리 검토했다. | C026 | M027 |
| Base.CannedCornedBeefOpen | public / core | revise / description_ready | scripts/items_food.txt:49의 exact H=-24, T=미선언; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C004 | M004 |
| Base.CannedEggplant | public / no-core | revise / description_ready | scripts/newitems.txt:2758; scripts/recipes.txt:1598–1822의 해당 exact Open Jar input/result. 정적 HungerChange가 없으므로 섭취 수치를 생성하지 않는다. | C056 | M065 |
| Base.CannedFruitBeverage | public / core | revise / description_ready | §조리 문구 32개: 이 exact item의 input/result/keep 역할과 원본 recipe를 분리 검토했다. | C026 | M027 |
| Base.CannedFruitBeverageOpen | public / core | revise / description_ready | scripts/items_food.txt:717의 exact H=-15, T=-85; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C020 | M004 |
| Base.CannedFruitCocktail | public / core | revise / description_ready | §조리 문구 32개: 이 exact item의 input/result/keep 역할과 원본 recipe를 분리 검토했다. | C026 | M027 |
| Base.CannedFruitCocktailOpen | public / core | revise / description_ready | scripts/items_food.txt:671의 exact H=-15, T=미선언; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C004 | M004 |
| Base.CannedLeek | public / no-core | revise / description_ready | scripts/newitems.txt:2775; scripts/recipes.txt:1598–1822의 해당 exact Open Jar input/result. 정적 HungerChange가 없으므로 섭취 수치를 생성하지 않는다. | C056 | M065 |
| Base.CannedMilk | public / core | revise / description_ready | §조리 문구 32개: 이 exact item의 input/result/keep 역할과 원본 recipe를 분리 검토했다. | C026 | M027 |
| Base.CannedMilkOpen | public / core | revise / description_ready | scripts/items_food.txt:2829; 원문 Food H<0/T<0 및 EvolvedRecipe 선언. §사과의 소비·재료 해석 재사용; 보존/안전/효과량 보장 없음. | C058 | M066 |
| Base.CannedMushroomSoup | public / core | revise / description_ready | §조리 문구 32개: 이 exact item의 input/result/keep 역할과 원본 recipe를 분리 검토했다. | C026 | M027 |
| Base.CannedMushroomSoupOpen | public / core | revise / description_ready | scripts/items_food.txt:186; 원문 Food H<0/T<0 및 EvolvedRecipe 선언. §사과의 소비·재료 해석 재사용; 보존/안전/효과량 보장 없음. | C058 | M066 |
| Base.CannedPeaches | public / core | revise / description_ready | §조리 문구 32개: 이 exact item의 input/result/keep 역할과 원본 recipe를 분리 검토했다. | C026 | M027 |
| Base.CannedPeachesOpen | public / core | revise / description_ready | scripts/items_food.txt:764의 exact H=-15, T=미선언; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C004 | M004 |
| Base.CannedPeas | public / core | revise / description_ready | §조리 문구 32개: 이 exact item의 input/result/keep 역할과 원본 recipe를 분리 검토했다. | C026 | M027 |
| Base.CannedPeasOpen | public / core | revise / description_ready | scripts/items_food.txt:213의 exact H=-16, T=-3; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C020 | M004 |
| Base.CannedPineapple | public / core | revise / description_ready | §조리 문구 32개: 이 exact item의 input/result/keep 역할과 원본 recipe를 분리 검토했다. | C026 | M027 |
| Base.CannedPineappleOpen | public / core | revise / description_ready | scripts/items_food.txt:810의 exact H=-15, T=미선언; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C004 | M004 |
| Base.CannedPotato | public / no-core | revise / description_ready | scripts/newitems.txt:2741; scripts/recipes.txt:1598–1822의 해당 exact Open Jar input/result. 정적 HungerChange가 없으므로 섭취 수치를 생성하지 않는다. | C056 | M065 |
| Base.CannedPotato2 | public / core | revise / description_ready | §조리 문구 32개: 이 exact item의 input/result/keep 역할과 원본 recipe를 분리 검토했다. | C026 | M027 |
| Base.CannedPotatoOpen | public / core | revise / description_ready | scripts/items_food.txt:241의 exact H=-18, T=-7; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C020 | M004 |
| Base.CannedRedRadish | public / no-core | revise / description_ready | scripts/newitems.txt:2792; scripts/recipes.txt:1598–1822의 해당 exact Open Jar input/result. 정적 HungerChange가 없으므로 섭취 수치를 생성하지 않는다. | C056 | M065 |
| Base.CannedSardines | public / core | revise / description_ready | §조리 문구 32개: 이 exact item의 input/result/keep 역할과 원본 recipe를 분리 검토했다. | C026 | M027 |
| Base.CannedSardinesOpen | public / core | revise / description_ready | scripts/items_food.txt:269의 exact H=-14, T=미선언; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C004 | M004 |
| Base.CannedTomato | public / no-core | revise / description_ready | scripts/newitems.txt:2707; scripts/recipes.txt:1598–1822의 해당 exact Open Jar input/result. 정적 HungerChange가 없으므로 섭취 수치를 생성하지 않는다. | C056 | M065 |
| Base.CannedTomato2 | public / core | revise / description_ready | §조리 문구 32개: 이 exact item의 input/result/keep 역할과 원본 recipe를 분리 검토했다. | C026 | M027 |
| Base.CannedTomatoOpen | public / core | revise / description_ready | scripts/items_food.txt:296의 exact H=-12, T=-8; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C020 | M004 |
| Base.CanoePadel | public / no-core | revise / description_ready | scripts/items_weapons.txt:2224; exact Type=Weapon/damage=0.5–1.3. 연주·경기·배관 수리 같은 현실 기능을 추정하지 않는다. | C021 | M022 |
| Base.CanoePadelX2 | public / no-core | revise / description_ready | scripts/items_weapons.txt:2267; exact Type=Weapon/damage=0.8–1.9. 연주·경기·배관 수리 같은 현실 기능을 추정하지 않는다. | C021 | M022 |
| Base.CarBattery1 | public / core | revise / description_ready | scripts/vehicles/vehiclesitems.txt:636; exact VehicleType/CarBattery 및 template_battery, Vehicles.Update.Battery/Headlight/Lightbar의 충전 소모·전원 조건. 완전 복구/자동 충전 보장 없음. | C059 | M067 |
| Base.CarBattery2 | public / core | revise / description_ready | scripts/vehicles/vehiclesitems.txt:655; exact VehicleType/CarBattery 및 template_battery, Vehicles.Update.Battery/Headlight/Lightbar의 충전 소모·전원 조건. 완전 복구/자동 충전 보장 없음. | C059 | M067 |
| Base.CarBattery3 | public / core | revise / description_ready | scripts/vehicles/vehiclesitems.txt:674; exact VehicleType/CarBattery 및 template_battery, Vehicles.Update.Battery/Headlight/Lightbar의 충전 소모·전원 조건. 완전 복구/자동 충전 보장 없음. | C059 | M067 |
| Base.CarBatteryCharger | public / core | keep / description_ready | 보호된 CarBatteryCharger의 자동차 배터리 충전 용도를 유지한다. | C003 | M068 |
| Base.CarKey | public / core | revise / description_ready | scripts/vehicles/vehiclesitems.txt:49; ISVehicleMenu.lua:98/117 vehicle keyId 대응. 핫와이어·점화장치 열쇠 등 대체 경로 별도. | C060 | M064 |
| Base.CardDeck | public / core | revise / description_ready | scripts/newitems.txt:1746; lua/server/Camping/camping_fuel.lua의 exact CardDeck 키가 연료/점화 재료에 모두 등록됨. 앞 절 ISCampingMenu의 유효 연료/점화 선택과 보충·점화 경로 재사용. 청소·게임·결제 등의 미확인 기능과 분리. | C227 | M220 |
| Base.Carrots | public / core | revise / description_ready | scripts/items_food.txt:1129의 exact H=-8, T=-4; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C020 | M004 |
| Base.CarvingFork | public / core | review_hold / review_required | scripts/newitems.txt:4721; Normal 선언은 확인되나 exact 사용/조리 입력이 미확정; 유사 도구·Teabag2·Flour의 기능 전이 금지. 필요한 추가 근거는 이 exact item의 해당 행동/재료 입력 또는 효과를 명시하는 vanilla source 관계이며, current admission 부재를 해소할 승인만으로 대체하지 않음. | C049 | M069 |
| Base.CaseyPic | public / core | review_hold / review_required | scripts/items.txt:221; 사진의 Normal 정체성/원문 locator 확인; 보기·놀이·수집 action 의 실제 사용 경로는 미확정. 유사 매체의 재생·학습 기능을 전이하지 않음. 필요한 추가 근거는 이 exact item의 해당 행동/재료 입력 또는 효과를 명시하는 vanilla source 관계이며, current admission 부재를 해소할 승인만으로 대체하지 않음. | C015 | M050 |
| Base.CatToy | public / core | review_hold / review_required | scripts/newitems.txt:306; 장난감의 Normal 정체성/원문 locator 확인; 보기·놀이·수집 action 의 실제 사용 경로는 미확정. 유사 매체의 재생·학습 기능을 전이하지 않음. 필요한 추가 근거는 이 exact item의 해당 행동/재료 입력 또는 효과를 명시하는 vanilla source 관계이며, current admission 부재를 해소할 승인만으로 대체하지 않음. | C015 | M054 |
| Base.Catfish | public / core | revise / description_ready | scripts/items_food.txt:1676의 exact H=-15, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음; DangerousUncooked=TRUE. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C032 | M012 |
| Base.Centipede | public / core | revise / description_ready | scripts/items_food.txt:8805의 exact H=-5, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음; DangerousUncooked=TRUE. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C032 | M012 |
| Base.Centipede2 | public / core | revise / description_ready | scripts/items_food.txt:8826의 exact H=-5, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음; DangerousUncooked=TRUE. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C032 | M012 |
| Base.Cereal | public / core | revise / description_ready | scripts/items_food.txt:3830의 exact H=-40, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C012 | M012 |
| Base.CerealBowl | public / no-core | revise / description_ready | scripts/items_food.txt:3846의 exact H=-8, T=-20; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C061 | M012 |
| Base.Chainsaw | public / core | keep / description_ready | 각 exact Weapon 선언과 근접 공격 역할을 대조했다. Chainsaw도 작동하는 엔진톱의 벌목 기능을 추가하지 않는다. | C003 | M070 |
| Base.ChairLeg | public / core | keep / description_ready | 각 exact Weapon 선언과 근접 공격 역할을 대조했다. Chainsaw도 작동하는 엔진톱의 벌목 기능을 추가하지 않는다. | C003 | M070 |
| Base.Charcoal | public / no-core | revise / description_ready | scripts/items.txt:1119; lua/server/Camping/camping_fuel.lua:4 Charcoal=.5; ISCampingMenu.isValidFuel/getFuelDurationForItem 및 ISBBQMenu:287–298 비프로판 BBQ에 연료 추가. forge 가용성과 독립. | C062 | M071 |
| Base.CheckerBoard | public / core | review_hold / review_required | scripts/newitems.txt:4904: §남은 혼합 역할: 현재 놀이 assertion을 실제 게임 플레이/지루함 감소에 결속하지 못했다. Normal 소품과 실제 놀이 기능을 구분한다. 필요한 추가 근거는 이 exact item의 해당 행동/재료 입력 또는 효과를 명시하는 vanilla source 관계이며, current admission 부재를 해소할 승인만으로 대체하지 않음. | C002 | M021 |
| Base.Cheese | public / core | revise / description_ready | scripts/items_food.txt:4502의 exact H=-15, T=미선언; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C004 | M004 |
| Base.CheeseSandwich | public / core | revise / description_ready | scripts/items_food.txt:4522의 exact H=-15, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음; ReplaceOnCooked=GrilledCheese, 다른 상태 item과 구분. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C012 | M012 |
| Base.Cherry | public / core | revise / description_ready | scripts/items_food.txt:1494의 exact H=-3, T=-1; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C020 | M004 |
| Base.ChessBlack | public / core | review_hold / review_required | scripts/newitems.txt:316: §남은 혼합 역할: 현재 놀이 assertion을 실제 게임 플레이/지루함 감소에 결속하지 못했다. Normal 소품과 실제 놀이 기능을 구분한다. 필요한 추가 근거는 이 exact item의 해당 행동/재료 입력 또는 효과를 명시하는 vanilla source 관계이며, current admission 부재를 해소할 승인만으로 대체하지 않음. | C002 | M021 |
| Base.ChessWhite | public / core | review_hold / review_required | scripts/newitems.txt:326: §남은 혼합 역할: 현재 놀이 assertion을 실제 게임 플레이/지루함 감소에 결속하지 못했다. Normal 소품과 실제 놀이 기능을 구분한다. 필요한 추가 근거는 이 exact item의 해당 행동/재료 입력 또는 효과를 명시하는 vanilla source 관계이며, current admission 부재를 해소할 승인만으로 대체하지 않음. | C002 | M021 |
| Base.Chicken | public / core | revise / description_ready | scripts/items_food.txt:2415의 exact H=-36, T=미선언; EvolvedRecipe 재료 선언 확인; DangerousUncooked=TRUE. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C063 | M004 |
| Base.ChickenFoot | public / core | revise / description_ready | scripts/items_food.txt:5941의 exact H=-12, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C012 | M012 |
| Base.ChickenFried | public / core | revise / description_ready | scripts/items_food.txt:2208의 exact H=-15, T=미선언; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C004 | M004 |
| Base.ChickenNuggets | public / core | revise / description_ready | scripts/items_food.txt:7862의 exact H=-10, T=미선언; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C004 | M004 |
| Base.Chives | public / core | revise / description_ready | scripts/items_food.txt:8535의 exact H=-1, T=미선언; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C004 | M004 |
| Base.ChocoCakes | public / core | revise / description_ready | scripts/items_food.txt:9463의 exact H=-10, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C012 | M012 |
| Base.Chocolate | public / core | revise / description_ready | scripts/items_food.txt:4013의 exact H=-20, T=미선언; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C004 | M004 |
| Base.ChocolateChips | public / core | revise / description_ready | scripts/items_food.txt:5958의 exact H=-6, T=미선언; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C004 | M004 |
| Base.ChocolateCoveredCoffeeBeans | public / core | revise / description_ready | scripts/items_food.txt:9203의 exact H=-5, T=미선언; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C004 | M004 |
| Base.ChokeTubeFull | public / core | keep / description_ready | scripts/newitems.txt:2635; exact WeaponPart/PartType=Canon/MountOn=Shotgun. 총기 개조 부품이라는 current 목적은 구체적. 실제 성능·조명/총검 공격은 추가하지 않는다. | C014 | M014 |
| Base.ChokeTubeImproved | public / core | keep / description_ready | scripts/newitems.txt:2652; exact WeaponPart/PartType=Canon/MountOn=Shotgun. 총기 개조 부품이라는 current 목적은 구체적. 실제 성능·조명/총검 공격은 추가하지 않는다. | C014 | M014 |
| Base.Chopsticks | public / core | review_hold / review_required | scripts/newitems.txt:4569; Normal 선언은 확인되나 exact 사용/조리 입력이 미확정; 유사 도구·Teabag2·Flour의 기능 전이 금지. 필요한 추가 근거는 이 exact item의 해당 행동/재료 입력 또는 효과를 명시하는 vanilla source 관계이며, current admission 부재를 해소할 승인만으로 대체하지 않음. | C049 | M069 |
| Base.ChrisPic | public / core | review_hold / review_required | scripts/items.txt:191; 사진의 Normal 정체성/원문 locator 확인; 보기·놀이·수집 action 의 실제 사용 경로는 미확정. 유사 매체의 재생·학습 기능을 전이하지 않음. 필요한 추가 근거는 이 exact item의 해당 행동/재료 입력 또는 효과를 명시하는 vanilla source 관계이며, current admission 부재를 해소할 승인만으로 대체하지 않음. | C015 | M050 |
| Base.Cigarettes | public / core | revise / description_ready | scripts/items.txt:620; Alcoholic=TRUE, H/T 음수 Food 및 EvolvedRecipe; 기분 개선을 일괄 보장하는 기존 문구 축소. | C037 | M038 |
| Base.Cilantro | public / core | revise / description_ready | scripts/items_food.txt:8553의 exact H=-1, T=미선언; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C004 | M004 |
| Base.CinnamonRoll | public / core | revise / description_ready | scripts/items_food.txt:7897의 exact H=-12, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C012 | M012 |
| Base.CleaningLiquid | public / core | review_hold / review_required | scripts/newitems.txt:349: exact Type=Normal, OBSOLETE=TRUE. 정상 B41에서 이 exact item의 생성·사용 가능성/등록이 미확정이다. 작동하는 별도 FullType으로 대체하거나 기존 no-core 때문에 보류하는 것이 아님. | C015 | M221 |
| Base.CleaningLiquid2 | public / core | revise / description_ready | scripts/newitems.txt:336; ISWorldObjectContextMenu.lua:3331/3337 exact wash soap 목록; ISWashYourself/ISWashClothing 소비·blood/dirt 제거. | C064 | M011 |
| Base.ClosedUmbrellaBlack | public / core | revise / description_ready | scripts/items_weapons.txt:4273; Weapon 선언 + recipes.txt:3653–3712 동일 색 Open Umbrella; 열린 결과의 ProtectFromRainWhenEquipped=true. | C065 | M011 |
| Base.ClosedUmbrellaBlue | public / core | revise / description_ready | scripts/items_weapons.txt:4183; Weapon 선언 + recipes.txt:3653–3712 동일 색 Open Umbrella; 열린 결과의 ProtectFromRainWhenEquipped=true. | C065 | M011 |
| Base.ClosedUmbrellaRed | public / core | revise / description_ready | scripts/items_weapons.txt:4228; Weapon 선언 + recipes.txt:3653–3712 동일 색 Open Umbrella; 열린 결과의 ProtectFromRainWhenEquipped=true. | C065 | M011 |
| Base.ClosedUmbrellaWhite | public / core | revise / description_ready | scripts/items_weapons.txt:4318; Weapon 선언 + recipes.txt:3653–3712 동일 색 Open Umbrella; 열린 결과의 ProtectFromRainWhenEquipped=true. | C065 | M011 |
| Base.ClubHammer | public / no-core | revise / description_ready | scripts/items_weapons.txt:922; exact Weapon/damage=0.5–1. 구체 작업 source가 미결속인 부분을 일반 '작업'으로 확대하지 않는다. | C066 | M073 |
| Base.Coal | public / core | review_hold / review_required | scripts/items.txt:1133: exact Type=Drainable, OBSOLETE=TRUE. 정상 B41에서 이 exact item의 생성·사용 가능성/등록이 미확정이다. 작동하는 별도 FullType으로 대체하거나 기존 no-core 때문에 보류하는 것이 아님. ISBlacksmithMenu:314/476→ISAddCoalInFurnace의 addFuel/Use는 확인했지만 obsolete Coal의 정상 사용 범위를 해결하지 못함. | C002 | M221 |
| Base.Cockroach | public / core | revise / description_ready | scripts/items_food.txt:4244의 exact H=-5, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C012 | M012 |
| Base.CocoaPowder | public / core | revise / description_ready | scripts/items_food.txt:5976의 exact H=-30, T=50; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C067 | M004 |
| Base.Coffee2 | public / core | revise / description_ready | §후속 item별 판정: exact HotDrink EvolvedRecipe·ThirstChange=60 | C068 | M075 |
| Base.ColdCuppa | public / no-core | revise / description_ready | scripts/items_food.txt:3498의 exact H=-5, T=-50; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C061 | M012 |
| Base.ColdDrinkRed | public / no-core | revise / description_ready | scripts/items_food.txt:3027의 exact H=-5, T=-50; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C061 | M012 |
| Base.ColdDrinkSpiffo | public / no-core | revise / description_ready | scripts/items_food.txt:3115의 exact H=-5, T=-50; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C061 | M012 |
| Base.ColdDrinkWhite | public / no-core | revise / description_ready | scripts/items_food.txt:3071의 exact H=-5, T=-50; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C061 | M012 |
| Base.Coldpack | public / core | keep / description_ready | Make Smoke Bomb의 exact Coldpack input으로 현재 재료 역할이 명확하다. | C003 | M076 |
| Base.Cologne | public / core | review_hold / review_required | scripts/newitems.txt:359: §남은 혼합 역할: 향수 사용·캐릭터 효과의 exact 게임 경로가 미확인이다. 필요한 추가 근거는 이 exact item의 해당 행동/재료 입력 또는 효과를 명시하는 vanilla source 관계이며, current admission 부재를 해소할 승인만으로 대체하지 않음. | C002 | M077 |
| Base.Comb | public / core | review_hold / review_required | scripts/newitems.txt:1756: §남은 혼합 역할: 빗질/머리 정돈의 exact 게임 경로가 미확인이다. 필요한 추가 근거는 이 exact item의 해당 행동/재료 입력 또는 효과를 명시하는 vanilla source 관계이며, current admission 부재를 해소할 승인만으로 대체하지 않음. | C002 | M078 |
| Base.CombinationPadlock | public / core | revise / description_ready | scripts/newitems.txt:2917; ISWorldObjectContextMenu.lua:584/2994 설치·암호 설정, 지원 구조물 조건. | C069 | M026 |
| Base.Comfrey | public / core | revise / description_ready | scripts/newitems.txt:2049 Type=Normal; scripts/recipes.txt:1192–1209의 exact poultice input 확인. 섭취 효과/완성 습포의 치료 효과와 분리. | C070 | M079 |
| Base.ComfreyCataplasm | public / no-core | revise / description_ready | scripts/newitems.txt:2060; ISHealthPanel.lua:1193–1273 exact poultice selector/부상/세 factor=0→각 timed action. perform에서 부상 부위 factor 설정·item 소비. 일반적인 처치 목적은 준비되며 개별 회복 효과·속도는 미확정으로 범위 밖에 둠. | C228 | M222 |
| Base.ComicBook | public / core | revise / description_ready | §후속 item별 판정: exact 읽기 효과 선언 또는 CanBeWrite/페이지·필기구 조건을 구분했다. | C044 | M051 |
| Base.CommonMallow | public / core | revise / description_ready | scripts/items_food.txt:4054의 exact H=-1, T=미선언; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C004 | M004 |
| Base.CompostBag | public / no-core | revise / description_ready | §농사·낚시·덫: 해당 exact source 선택·조건 및 실제 결과 변화 연결 | C026 | M025 |
| Base.ConcretePowder | public / core | review_hold / review_required | scripts/items.txt:109; Normal 선언만으로 현행 제작·수리 소비 경로 미확정; exact recipe/action 입력 관계 필요. 필요한 추가 근거는 이 exact item의 해당 행동/재료 입력 또는 효과를 명시하는 vanilla source 관계이며, current admission 부재를 해소할 승인만으로 대체하지 않음. | C049 | M081 |
| Base.Cone | public / core | revise / description_ready | scripts/items_food.txt:7714의 exact H=-5, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C012 | M012 |
| Base.ConeIcecream | public / no-core | revise / description_ready | scripts/items_food.txt:7729의 exact H=-15, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C012 | M012 |
| Base.ConeIcecreamMelted | public / core | revise / description_ready | scripts/items_food.txt:7771의 exact H=-15, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C012 | M012 |
| Base.ConeIcecreamToppings | public / no-core | revise / description_ready | scripts/items_food.txt:7750의 exact H=-15, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C012 | M012 |
| Base.CookieChocolateChip | public / core | revise / description_ready | scripts/items_food.txt:3867의 exact H=-5, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C012 | M012 |
| Base.CookieChocolateChipDough | public / no-core | revise / description_ready | scripts/items_food.txt:9574의 exact H=-23, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C012 | M012 |
| Base.CookieJelly | public / core | revise / description_ready | scripts/items_food.txt:3887의 exact H=-5, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C012 | M012 |
| Base.CookiesChocolate | public / core | revise / description_ready | scripts/items_food.txt:5997의 exact H=-5, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C012 | M012 |
| Base.CookiesChocolateDough | public / no-core | revise / description_ready | scripts/items_food.txt:9597의 exact H=-23, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C012 | M012 |
| Base.CookiesOatmeal | public / core | revise / description_ready | scripts/items_food.txt:6017의 exact H=-5, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C012 | M012 |
| Base.CookiesOatmealDough | public / no-core | revise / description_ready | scripts/items_food.txt:9620의 exact H=-23, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C012 | M012 |
| Base.CookiesShortbread | public / core | revise / description_ready | scripts/items_food.txt:6037의 exact H=-5, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C012 | M012 |
| Base.CookiesShortbreadDough | public / no-core | revise / description_ready | scripts/items_food.txt:9644의 exact H=-23, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C012 | M012 |
| Base.CookiesSugar | public / core | revise / description_ready | scripts/items_food.txt:9334의 exact H=-5, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C012 | M012 |
| Base.CookiesSugarDough | public / no-core | revise / description_ready | scripts/items_food.txt:9667의 exact H=-23, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C012 | M012 |
| Base.CookingMag1 | public / core | revise / description_ready | §학습 문구 87개: 해당 exact SkillTrained 또는 TeachedRecipes/knowledge token의 source를 구분했다. | C026 | M053 |
| Base.CookingMag2 | public / core | revise / description_ready | §학습 문구 87개: 해당 exact SkillTrained 또는 TeachedRecipes/knowledge token의 source를 구분했다. | C026 | M053 |
| Base.Cooler | public / core | revise / description_ready | scripts/clothing/clothing_bags.txt:573의 exact Container/Capacity=8. 보관·운반 역할이 명확하며 이름에 따른 내용물 제한/냉장 효과는 추가하지 않는다. | C022 | M023 |
| Base.CordlessPhone | public / core | revise / description_ready | scripts/newitems.txt:26; recipes.txt:2040/2055 Dismantle→ElectronicsScrap, screwdriver·OnTest 조건. | C071 | M011 |
| Base.Cork | public / core | review_hold / review_required | scripts/newitems.txt:1379: 주방 소품의 현실 사용을 actual 조리/상차림 interaction에 결속하지 못했다. exact 역할이 확인된 식재료/도구와 분리한다. 필요한 추가 근거는 이 exact item의 해당 행동/재료 입력 또는 효과를 명시하는 vanilla source 관계이며, current admission 부재를 해소할 승인만으로 대체하지 않음. | C002 | M082 |
| Base.Corkscrew | public / core | review_hold / review_required | scripts/newitems.txt:1389: 주방 소품의 현실 사용을 actual 조리/상차림 interaction에 결속하지 못했다. exact 역할이 확인된 식재료/도구와 분리한다. Tags=Corkscrew 및 Recipe.GetItemTypes.Corkscrew selector는 확인했으나 selector를 사용하는 실제 recipe/handler 입력 관계가 아직 없음. | C002 | M082 |
| Base.Corn | public / core | revise / description_ready | scripts/items_food.txt:1172의 exact H=-14, T=-4; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C020 | M004 |
| Base.CornFrozen | public / core | revise / description_ready | scripts/items_food.txt:9352의 exact H=-20, T=-5; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C020 | M004 |
| Base.Cornbread | public / core | revise / description_ready | scripts/items_food.txt:7242의 exact H=-10, T=미선언; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C004 | M004 |
| Base.Corndog | public / core | revise / description_ready | scripts/items_food.txt:2274의 exact H=-12, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C012 | M012 |
| Base.Cornflour | public / core | revise / description_ready | scripts/newitems.txt:1366; Tags=Flour; recipecode.lua:189 flour selector + recipes.txt:913/945 반죽 입력. | C072 | M026 |
| Base.Cornmeal | public / core | review_hold / review_required | scripts/items.txt:778; Drainable 선언은 확인되나 exact 사용/조리 입력이 미확정; 유사 도구·Teabag2·Flour의 기능 전이 금지. 필요한 추가 근거는 이 exact item의 해당 행동/재료 입력 또는 효과를 명시하는 vanilla source 관계이며, current admission 부재를 해소할 승인만으로 대체하지 않음. | C049 | M083 |
| Base.Corset | public / no-core | revise / description_ready | scripts/clothing/clothing_underwear.txt:363: Clothing/BodyLocation=UnderwearTop. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C185 | M017 |
| Base.Corset_Black | public / no-core | revise / description_ready | scripts/clothing/clothing_underwear.txt:339: Clothing/BodyLocation=UnderwearTop. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C185 | M017 |
| Base.Corset_Medical | public / no-core | revise / description_ready | scripts/clothing/clothing_underwear.txt:375: Clothing/BodyLocation=UnderwearTop. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C185 | M017 |
| Base.Corset_Red | public / no-core | revise / description_ready | scripts/clothing/clothing_underwear.txt:351: Clothing/BodyLocation=UnderwearTop. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C185 | M017 |
| Base.CortmanPic | public / core | review_hold / review_required | scripts/items.txt:201; 사진의 Normal 정체성/원문 locator 확인; 보기·놀이·수집 action 의 실제 사용 경로는 미확정. 유사 매체의 재생·학습 기능을 전이하지 않음. 필요한 추가 근거는 이 exact item의 해당 행동/재료 입력 또는 효과를 명시하는 vanilla source 관계이며, current admission 부재를 해소할 승인만으로 대체하지 않음. | C015 | M050 |
| Base.CottonBalls | public / core | revise / description_ready | scripts/newitems.txt:2221; recipes.txt:1563/1572 CottonBalls→AlcoholedCottonBalls; 소독전 원료와 구분. | C073 | M064 |
| Base.Crackers | public / core | revise / description_ready | scripts/items_food.txt:7224의 exact H=-5, T=미선언; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C004 | M004 |
| Base.CraftedFishingRod | public / no-core | revise / description_ready | §농사·낚시·덫: 해당 exact source 선택·조건 및 실제 결과 변화 연결 | C026 | M025 |
| Base.CraftedFishingRodTwineLine | public / no-core | revise / description_ready | §농사·낚시·덫: 해당 exact source 선택·조건 및 실제 결과 변화 연결 | C026 | M025 |
| Base.Crappie | public / core | revise / description_ready | scripts/items_food.txt:1759의 exact H=-15, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음; DangerousUncooked=TRUE. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C032 | M012 |
| Base.Crayfish | public / core | revise / description_ready | scripts/items_food.txt:7689의 exact H=-10, T=미선언; EvolvedRecipe 재료 선언 확인; DangerousUncooked=TRUE. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C063 | M004 |
| Base.CreditCard | public / core | review_hold / review_required | scripts/newitems.txt:380: 현금/카드/지갑 identity 외 사용·수납 상호작용이 미결속이다. Normal 지갑을 Container나 결제 기능으로 설명하지 않는다. 필요한 추가 근거는 이 exact item의 해당 행동/재료 입력 또는 효과를 명시하는 vanilla source 관계이며, current admission 부재를 해소할 승인만으로 대체하지 않음. | C002 | M084 |
| Base.Cricket | public / core | revise / description_ready | scripts/items_food.txt:4264의 exact H=-5, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C012 | M012 |
| Base.Crisps | public / core | revise / description_ready | scripts/items_food.txt:4543의 exact H=-15, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C012 | M012 |
| Base.Crisps2 | public / core | revise / description_ready | scripts/items_food.txt:4561의 exact H=-15, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C012 | M012 |
| Base.Crisps3 | public / core | revise / description_ready | scripts/items_food.txt:4579의 exact H=-15, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C012 | M012 |
| Base.Crisps4 | public / core | revise / description_ready | scripts/items_food.txt:4597의 exact H=-15, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C012 | M012 |
| Base.Croissant | public / core | revise / description_ready | scripts/items_food.txt:6057의 exact H=-8, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C012 | M012 |
| Base.Crowbar | public / no-core | revise / description_ready | scripts/items_weapons.txt:1455; exact RemoveBarricade/Crowbar tags 및 기존 바리케이드 제거 역할. 모든 가구 분해/금속 작업으로 확대하지 않는다. | C074 | M085 |
| Base.Cupcake | public / core | revise / description_ready | scripts/items_food.txt:3996의 exact H=-20, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C012 | M012 |
| Base.CuttingBoardPlastic | public / core | review_hold / review_required | scripts/newitems.txt:4855; Normal 선언은 확인되나 exact 사용/조리 입력이 미확정; 유사 도구·Teabag2·Flour의 기능 전이 금지. 필요한 추가 근거는 이 exact item의 해당 행동/재료 입력 또는 효과를 명시하는 vanilla source 관계이며, current admission 부재를 해소할 승인만으로 대체하지 않음. | C049 | M069 |
| Base.CuttingBoardWooden | public / core | review_hold / review_required | scripts/newitems.txt:4864; Normal 선언은 확인되나 exact 사용/조리 입력이 미확정; 유사 도구·Teabag2·Flour의 기능 전이 금지. 필요한 추가 근거는 이 exact item의 해당 행동/재료 입력 또는 효과를 명시하는 vanilla source 관계이며, current admission 부재를 해소할 승인만으로 대체하지 않음. | C049 | M069 |
| Base.Daikon | public / core | revise / description_ready | scripts/items_food.txt:6076의 exact H=-12, T=-5; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C020 | M004 |
| Base.Dandelions | public / core | revise / description_ready | scripts/items_food.txt:8497의 exact H=-5, T=미선언; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C004 | M004 |
| Base.Dart | public / core | review_hold / review_required | scripts/newitems.txt:390: 현재 경기 규칙에 맞춘 놀이 assertion을 실제 경기/투척 기능과 결속하지 못했다. Normal 소품이라는 선언은 경기 실행 근거가 아니다. 필요한 추가 근거는 이 exact item의 해당 행동/재료 입력 또는 효과를 명시하는 vanilla source 관계이며, current admission 부재를 해소할 승인만으로 대체하지 않음. | C002 | M033 |
| Base.DeadBird | public / core | revise / description_ready | scripts/items_food.txt:2000의 exact H=-15, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음; DangerousUncooked=TRUE. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C032 | M012 |
| Base.DeadMouse | public / core | revise / description_ready | scripts/items_food.txt:1921의 exact H=-10, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음; DangerousUncooked=TRUE. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C032 | M012 |
| Base.DeadRabbit | public / core | revise / description_ready | scripts/items_food.txt:1946의 exact H=-45, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음; DangerousUncooked=TRUE. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C032 | M012 |
| Base.DeadRat | public / core | revise / description_ready | scripts/items_food.txt:1896의 exact H=-22, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음; DangerousUncooked=TRUE. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C032 | M012 |
| Base.DeadSquirrel | public / core | revise / description_ready | scripts/items_food.txt:1973의 exact H=-32, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음; DangerousUncooked=TRUE. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C032 | M012 |
| Base.DehydratedMeatStick | public / core | revise / description_ready | scripts/items_food.txt:7882의 exact H=-10, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C012 | M012 |
| Base.DenimStrips | public / core | revise / description_ready | scripts/newitems.txt:4276: exact CanBandage와 Make Stone Axe/Hammer/Knife/Splint input, ISApplyBandage 경로. 보호된 LeatherStrips의 별도 수선 문구는 변경하지 않는다. | C075 | M086 |
| Base.DenimStripsDirty | public / core | revise / description_ready | scripts/newitems.txt:4292: exact CanBandage 및 ISApplyBandage:perform의 Dirty type은 bandageLife=0으로 분기. 깨끗한 재료와 같은 지속/치료 효과를 주지 않는다. | C031 | M031 |
| Base.Dice | public / core | review_hold / review_required | scripts/newitems.txt:1766: §남은 혼합 역할: 현재 놀이 assertion을 실제 게임 플레이/지루함 감소에 결속하지 못했다. Normal 소품과 실제 놀이 기능을 구분한다. 필요한 추가 근거는 이 exact item의 해당 행동/재료 입력 또는 효과를 명시하는 vanilla source 관계이며, current admission 부재를 해소할 승인만으로 대체하지 않음. | C002 | M021 |
| Base.DigitalWatch | public / no-core | review_hold / review_required | scripts/newitems.txt:1440: exact Type=Normal, OBSOLETE=TRUE. 정상 B41에서 이 exact item의 생성·사용 가능성/등록이 미확정이다. 작동하는 별도 FullType으로 대체하거나 기존 no-core 때문에 보류하는 것이 아님. | C076 | M221 |
| Base.DigitalWatch2 | public / no-core | revise / description_ready | scripts/newitems.txt:1451; exact AlarmClock/AlarmSound와 현재 시계 역할. Normal DigitalWatch나 Weapon AlarmClock에 전파하지 않는다. | C007 | M007 |
| Base.Dirtbag | public / no-core | revise / description_ready | scripts/items.txt:1207; FireFighting.isExtinguisher의 exact Dirtbag/잔여 사용량. 흙 살포의 구체 경로는 별도 미확인. | C077 | M088 |
| Base.Disc | public / core | review_hold / review_required | scripts/newitems.txt:1356; Normal base item과 runtime recorded-media 데이터 binding 미확인; MediaCategory가 있는 Retail/Home variant의 재생 기능 복사 금지. 필요한 입력은 이 generic FullType에 recorded-media ID/type을 부여하는 producer 또는 실제 인스턴스 binding; Retail/Home 선언을 복사하지 않음. | C015 | M089 |
| Base.Disc_Retail | public / core | revise / description_ready | scripts/newitems.txt:4468; MediaCategory 선언; RWMMedia.lua:91 isRecordedMedia/MediaType와 ISRadioAction.lua:174/StartPlayMedia. 실제 녹화 내용은 인스턴스별로 다름. | C078 | M090 |
| Base.DishCloth | public / core | revise / description_ready | §후속 item별 판정: exact drying 및 blood cleaning 선택 | C033 | M035 |
| Base.DishClothWet | public / core | revise / description_ready | scripts/items.txt:5; Wet=true, ItemWhenDry=Base.DishCloth; 젖은 상태와 기존 건조 수건 역할 구분. | C034 | M011 |
| Base.Disinfectant | public / no-core | revise / description_ready | §의료: exact 소독제와 HDisinfect/ISDisinfect | C009 | M009 |
| Base.DogChew | public / core | review_hold / review_required | scripts/newitems.txt:401: 개에게 씹게 하는 게임 동작/대상 선택을 결속하지 못했다. DogChew 명칭을 반려견 상호작용 근거로 쓰지 않는다. 필요한 추가 근거는 이 exact item의 해당 행동/재료 입력 또는 효과를 명시하는 vanilla source 관계이며, current admission 부재를 해소할 승인만으로 대체하지 않음. | C002 | M091 |
| Base.Dogfood | public / no-core | revise / description_ready | scripts/recipes.txt:341–350 exact Dogfood→DogfoodOpen 및 can-opener keep. 원래 캔의 섭취 효과로 혼동하지 않는다. | C079 | M092 |
| Base.DogfoodOpen | public / core | revise / description_ready | scripts/items_food.txt:5의 exact H=-30, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C012 | M012 |
| Base.Doll | public / core | review_hold / review_required | scripts/newitems.txt:1346; 장난감의 Normal 정체성/원문 locator 확인; 보기·놀이·수집 action 의 실제 사용 경로는 미확정. 유사 매체의 재생·학습 기능을 전이하지 않음. 필요한 추가 근거는 이 exact item의 해당 행동/재료 입력 또는 효과를 명시하는 vanilla source 관계이며, current admission 부재를 해소할 승인만으로 대체하지 않음. | C015 | M054 |
| Base.Doodle | public / core | revise / description_ready | §후속 item별 판정: exact 읽기 효과 선언 또는 CanBeWrite/페이지·필기구 조건을 구분했다. | C044 | M051 |
| Base.Doorknob | public / core | revise / description_ready | scripts/items.txt:119; ISBuildMenu.lua:1664/1678 문 제작 need:Base.Doorknob; recipes.txt:663 서랍 재료. | C080 | M026 |
| Base.DoubleBarrelShotgun | public / core | keep / description_ready | exact ranged shotgun 선언 및 절단 recipe가 현재 산탄총 기본 용도를 뒷받침한다. | C003 | M093 |
| Base.DoubleBarrelShotgunSawnoff | public / no-core | keep / acquisition_only | 각 exact ranged Weapon 선언과 사격 목적을 대조했다. empty-core를 문구만으로 채우지 않는다. | C003 | M094 |
| Base.Dough | public / core | revise / description_ready | scripts/items_food.txt:4366의 exact H=-15, T=20; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음; DangerousUncooked=TRUE. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C081 | M012 |
| Base.DoughRolled | public / no-core | revise / description_ready | scripts/items_food.txt:4389의 exact H=-15, T=20; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C025 | M012 |
| Base.DoughnutChocolate | public / core | revise / description_ready | scripts/items_food.txt:6097의 exact H=-7, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C012 | M012 |
| Base.DoughnutFrosted | public / core | revise / description_ready | scripts/items_food.txt:6116의 exact H=-7, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C012 | M012 |
| Base.DoughnutJelly | public / core | revise / description_ready | scripts/items_food.txt:6135의 exact H=-7, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C012 | M012 |
| Base.DoughnutPlain | public / core | revise / description_ready | scripts/items_food.txt:6154의 exact H=-7, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C012 | M012 |
| Base.Drawer | public / core | revise / description_ready | scripts/items.txt:130; ISBuildMenu.lua:1247–1262/1443 서랍 달린 작은 탁자의 exact 필요재료. | C082 | M026 |
| Base.DressKnees_Straps | public / no-core | revise / description_ready | scripts/clothing/clothing_suits.txt:189: Clothing/BodyLocation=Dress. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C189 | M017 |
| Base.Dress_Knees | public / no-core | revise / description_ready | scripts/clothing/clothing_suits.txt:175: Clothing/BodyLocation=Dress. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C189 | M017 |
| Base.Dress_Long | public / no-core | revise / description_ready | scripts/clothing/clothing_suits.txt:273: Clothing/BodyLocation=Dress. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C189 | M017 |
| Base.Dress_Normal | public / no-core | revise / description_ready | scripts/clothing/clothing_suits.txt:303: Clothing/BodyLocation=Dress. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C189 | M017 |
| Base.Dress_SatinNegligee | public / no-core | revise / description_ready | scripts/clothing/clothing_suits.txt:259: Clothing/BodyLocation=Dress. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C189 | M017 |
| Base.Dress_Short | public / no-core | revise / description_ready | scripts/clothing/clothing_suits.txt:333: Clothing/BodyLocation=Dress. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C189 | M017 |
| Base.Dress_SmallBlackStrapless | public / no-core | revise / description_ready | scripts/clothing/clothing_suits.txt:203: Clothing/BodyLocation=Dress. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C189 | M017 |
| Base.Dress_SmallBlackStraps | public / no-core | revise / description_ready | scripts/clothing/clothing_suits.txt:217: Clothing/BodyLocation=Dress. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C189 | M017 |
| Base.Dress_SmallStrapless | public / no-core | revise / description_ready | scripts/clothing/clothing_suits.txt:231: Clothing/BodyLocation=Dress. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C189 | M017 |
| Base.Dress_SmallStraps | public / no-core | revise / description_ready | scripts/clothing/clothing_suits.txt:245: Clothing/BodyLocation=Dress. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C189 | M017 |
| Base.Dress_Straps | public / no-core | revise / description_ready | scripts/clothing/clothing_suits.txt:318: Clothing/BodyLocation=Dress. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C189 | M017 |
| Base.Dress_long_Straps | public / no-core | revise / description_ready | scripts/clothing/clothing_suits.txt:288: Clothing/BodyLocation=Dress. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C189 | M017 |
| Base.DriedBlackBeans | public / core | revise / description_ready | scripts/items_food.txt:8252의 exact H=-60, T=60; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C067 | M004 |
| Base.DriedChickpeas | public / core | revise / description_ready | scripts/items_food.txt:8274의 exact H=-60, T=60; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C067 | M004 |
| Base.DriedKidneyBeans | public / core | revise / description_ready | scripts/items_food.txt:8296의 exact H=-60, T=60; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C067 | M004 |
| Base.DriedLentils | public / core | revise / description_ready | scripts/items_food.txt:8318의 exact H=-60, T=60; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C067 | M004 |
| Base.DriedSplitPeas | public / core | revise / description_ready | scripts/items_food.txt:8340의 exact H=-60, T=60; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C067 | M004 |
| Base.DriedWhiteBeans | public / core | revise / description_ready | scripts/items_food.txt:8362의 exact H=-60, T=60; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C067 | M004 |
| Base.Drumstick | public / no-core | revise / description_ready | scripts/items_weapons.txt:562; exact Type=Weapon/damage=0.1–0.2. 연주·경기·배관 수리 같은 현실 기능을 추정하지 않는다. | C021 | M022 |
| Base.DuctTape | public / core | revise / description_ready | scripts/newitems.txt:1731; recipes.txt Add Timer/Motion/Trigger 및 Attach ... to Spear exact input. | C083 | M011 |
| Base.DumbBell | public / no-core | revise / description_ready | scripts/items_weapons.txt:1326; exact Type=Weapon/damage=0.5–1. 연주·경기·배관 수리 같은 현실 기능을 추정하지 않는다. | C021 | M022 |
| Base.Dungarees | public / no-core | revise / description_ready | scripts/clothing/clothing_pants.txt:669: Clothing/BodyLocation=Pants. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C190 | M017 |
| Base.Earbuds | public / core | revise / description_ready | scripts/newitems.txt:965; RWMVolume.lua:79 exact selector; ISRadioAction.lua:147–153 addHeadphones; 분해 입력도 존재. | C084 | M011 |
| Base.Earring_Dangly_Diamond | public / no-core | revise / description_ready | scripts/clothing/clothing_jewellery.txt:527: Clothing/BodyLocation=Ears. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C191 | M017 |
| Base.Earring_Dangly_Emerald | public / no-core | revise / description_ready | scripts/clothing/clothing_jewellery.txt:503: Clothing/BodyLocation=Ears. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C191 | M017 |
| Base.Earring_Dangly_Pearl | public / no-core | revise / description_ready | scripts/clothing/clothing_jewellery.txt:539: Clothing/BodyLocation=Ears. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C191 | M017 |
| Base.Earring_Dangly_Ruby | public / no-core | revise / description_ready | scripts/clothing/clothing_jewellery.txt:515: Clothing/BodyLocation=Ears. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C191 | M017 |
| Base.Earring_Dangly_Sapphire | public / no-core | revise / description_ready | scripts/clothing/clothing_jewellery.txt:491: Clothing/BodyLocation=Ears. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C191 | M017 |
| Base.Earring_LoopLrg_Gold | public / no-core | revise / description_ready | scripts/clothing/clothing_jewellery.txt:315: Clothing/BodyLocation=Ears. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C191 | M017 |
| Base.Earring_LoopLrg_Silver | public / no-core | revise / description_ready | scripts/clothing/clothing_jewellery.txt:327: Clothing/BodyLocation=Ears. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C191 | M017 |
| Base.Earring_LoopMed_Gold | public / no-core | revise / description_ready | scripts/clothing/clothing_jewellery.txt:351: Clothing/BodyLocation=Ears. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C191 | M017 |
| Base.Earring_LoopMed_Silver | public / no-core | revise / description_ready | scripts/clothing/clothing_jewellery.txt:339: Clothing/BodyLocation=Ears. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C191 | M017 |
| Base.Earring_LoopSmall_Gold_Both | public / no-core | revise / description_ready | scripts/clothing/clothing_jewellery.txt:377: Clothing/BodyLocation=Ears. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C191 | M017 |
| Base.Earring_LoopSmall_Gold_Top | public / no-core | revise / description_ready | scripts/clothing/clothing_jewellery.txt:391: Clothing/BodyLocation=EarTop. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C192 | M017 |
| Base.Earring_LoopSmall_Silver_Both | public / no-core | revise / description_ready | scripts/clothing/clothing_jewellery.txt:363: Clothing/BodyLocation=Ears. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C191 | M017 |
| Base.Earring_LoopSmall_Silver_Top | public / no-core | revise / description_ready | scripts/clothing/clothing_jewellery.txt:405: Clothing/BodyLocation=EarTop. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C192 | M017 |
| Base.Earring_Pearl | public / no-core | revise / description_ready | scripts/clothing/clothing_jewellery.txt:479: Clothing/BodyLocation=Ears. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C191 | M017 |
| Base.Earring_Stone_Emerald | public / no-core | revise / description_ready | scripts/clothing/clothing_jewellery.txt:455: Clothing/BodyLocation=Ears. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C191 | M017 |
| Base.Earring_Stone_Ruby | public / no-core | revise / description_ready | scripts/clothing/clothing_jewellery.txt:467: Clothing/BodyLocation=Ears. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C191 | M017 |
| Base.Earring_Stone_Sapphire | public / no-core | revise / description_ready | scripts/clothing/clothing_jewellery.txt:443: Clothing/BodyLocation=Ears. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C191 | M017 |
| Base.Earring_Stud_Gold | public / no-core | revise / description_ready | scripts/clothing/clothing_jewellery.txt:419: Clothing/BodyLocation=Ears. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C191 | M017 |
| Base.Earring_Stud_Silver | public / no-core | revise / description_ready | scripts/clothing/clothing_jewellery.txt:431: Clothing/BodyLocation=Ears. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C191 | M017 |
| Base.Earrings | public / no-core | review_hold / review_required | scripts/newitems.txt:975: exact Type=Normal, OBSOLETE=TRUE. 정상 B41에서 이 exact item의 생성·사용 가능성/등록이 미확정이다. 작동하는 별도 FullType으로 대체하거나 기존 no-core 때문에 보류하는 것이 아님. | C076 | M221 |
| Base.Edamame | public / core | revise / description_ready | scripts/items_food.txt:6173의 exact H=-5, T=미선언; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C004 | M004 |
| Base.Egg | public / core | revise / description_ready | scripts/items_food.txt:2390의 exact H=-7, T=미선언; EvolvedRecipe 재료 선언 확인; DangerousUncooked=TRUE. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C063 | M004 |
| Base.EggBoiled | public / no-core | revise / description_ready | scripts/items_food.txt:6192의 exact H=-10, T=미선언; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C004 | M004 |
| Base.EggCarton | public / core | revise / description_ready | §조리 문구 32개: 이 exact item의 input/result/keep 역할과 원본 recipe를 분리 검토했다. | C026 | M027 |
| Base.EggOmelette | public / core | revise / description_ready | scripts/items_food.txt:6231의 exact H=-20, T=미선언; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C004 | M004 |
| Base.EggPoached | public / no-core | revise / description_ready | scripts/items_food.txt:6212의 exact H=-10, T=미선언; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C004 | M004 |
| Base.EggScrambled | public / core | revise / description_ready | scripts/items_food.txt:6250의 exact H=-20, T=미선언; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C004 | M004 |
| Base.Eggplant | public / core | revise / description_ready | scripts/items_food.txt:1193의 exact H=-16, T=-9; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C020 | M004 |
| Base.ElectronicsMag1 | public / core | revise / description_ready | §학습 문구 87개: 해당 exact SkillTrained 또는 TeachedRecipes/knowledge token의 source를 구분했다. | C026 | M053 |
| Base.ElectronicsMag2 | public / core | revise / description_ready | §학습 문구 87개: 해당 exact SkillTrained 또는 TeachedRecipes/knowledge token의 source를 구분했다. | C026 | M053 |
| Base.ElectronicsMag3 | public / core | revise / description_ready | §학습 문구 87개: 해당 exact SkillTrained 또는 TeachedRecipes/knowledge token의 source를 구분했다. | C026 | M053 |
| Base.ElectronicsMag4 | public / core | revise / description_ready | §학습 문구 87개: 해당 exact SkillTrained 또는 TeachedRecipes/knowledge token의 source를 구분했다. | C026 | M053 |
| Base.ElectronicsMag5 | public / core | revise / description_ready | §학습 문구 87개: 해당 exact SkillTrained 또는 TeachedRecipes/knowledge token의 source를 구분했다. | C026 | M053 |
| Base.ElectronicsScrap | public / core | revise / description_ready | scripts/newitems.txt:108; input:Make Remote Controller V1; input:Make Remote Controller V2; input:Make Remote Controller V3; input:Make Remote Trigger; input:Make Timer; input:Add Timer; input:Add Motion Sensor V1; input:Add Motion Sensor V2; input:Add Motion Sensor V3; input:Add Crafted Trigger; input:Add Timer; input:Add Motion Sensor V1; input:Add Motion Sensor V2; input:Add Motion Sensor V3; input:Add Crafted Trigger; input:Add Timer; input:Add Motion Sensor V1; input:Add Motion Sensor V2; input:Add Motion Sensor V3; input:Add Crafted Trigger; input:Add Timer; input:Add Motion Sensor V1; input:Add Motion Sensor V2; input:Add Motion Sensor V3; input:Add Crafted Trigger; input:Add Timer; input:Add Motion Sensor V1; input:Add Motion Sensor V2; input:Add Motion Sensor V3; input:Add Crafted Trigger; input:Make Noise Maker; input:Make Pipe bomb; input:Craft Makeshift Radio; input:Craft Makeshift HAM Radio; input:Craft Makeshift Walkie Talkie; recipes_radio.txt:72–125 exact 제작 입력. 독립 기기 기능 없음. | C011 | M011 |
| Base.EmptyJar | public / core | revise / description_ready | §조리 문구 32개: 이 exact item의 input/result/keep 역할과 원본 recipe를 분리 검토했다. | C026 | M027 |
| Base.EmptyPetrolCan | public / no-core | revise / description_ready | scripts/newitems.txt:47; exact EmptyPetrol tag·빈 연료통 역할. 현재 내용물이 이미 있다고 하지 않는다. | C085 | M095 |
| Base.EmptySandbag | public / core | revise / description_ready | scripts/clothing/clothing_bags.txt:342의 exact Container/Capacity=15. 보관·운반 역할이 명확하며 이름에 따른 내용물 제한/냉장 효과는 추가하지 않는다. | C022 | M023 |
| Base.EngineDoor1 | public / core | keep / description_ready | scripts/vehicles/vehiclesitems.txt:1186; exact VehicleType=1와 해당 door/window/windshield part 관계. 현재 패널/유리 탈착 목적은 이미 구체적이며 방탄·방호 효과를 추가하지 않는다. | C014 | M096 |
| Base.EngineDoor2 | public / core | keep / description_ready | scripts/vehicles/vehiclesitems.txt:1200; exact VehicleType=2와 해당 door/window/windshield part 관계. 현재 패널/유리 탈착 목적은 이미 구체적이며 방탄·방호 효과를 추가하지 않는다. | C014 | M096 |
| Base.EngineDoor3 | public / core | keep / description_ready | scripts/vehicles/vehiclesitems.txt:1214; exact VehicleType=3와 해당 door/window/windshield part 관계. 현재 패널/유리 탈착 목적은 이미 구체적이며 방탄·방호 효과를 추가하지 않는다. | C014 | M096 |
| Base.EngineParts | public / core | revise / description_ready | scripts/vehicles/vehiclesitems.txt:37; VehicleCommands.repairEngine의 Engine condition 증가 및 exact Base.EngineParts 소모. 엔진 품질/출력 회복과 구분 | C086 | M097 |
| Base.EngineerMagazine1 | public / core | revise / description_ready | §학습 문구 87개: 해당 exact SkillTrained 또는 TeachedRecipes/knowledge token의 source를 구분했다. | C026 | M053 |
| Base.EngineerMagazine2 | public / core | revise / description_ready | §학습 문구 87개: 해당 exact SkillTrained 또는 TeachedRecipes/knowledge token의 source를 구분했다. | C026 | M053 |
| Base.Eraser | public / core | revise / description_ready | scripts/newitems.txt:411; ISWorldMapSymbols:canErase의 exact Base.Eraser 또는 Eraser tag; 종이 전체를 지우는 기능으로 확대하지 않는다. | C087 | M098 |
| Base.Extinguisher | empty / no-core | revise / description_ready | scripts/newitems.txt:1971: FireFighting.isExtinguisher exact Extinguisher/잔여 사용량 및 isSquareToExtinguish의 대상 선택. 영구 불은 제외한다. | C088 | M099 |
| Base.FarmingMag1 | public / core | revise / description_ready | §학습 문구 87개: 해당 exact SkillTrained 또는 TeachedRecipes/knowledge token의 source를 구분했다. | C026 | M053 |
| Base.Fertilizer | public / no-core | revise / description_ready | §농사·낚시·덫: 해당 exact source 선택·조건 및 실제 결과 변화 연결 | C026 | M025 |
| Base.FertilizerEmpty | public / core | review_hold / review_required | scripts/items.txt:1288: 이 빈 item의 재사용/처리 목적을 실제 전환·상호작용에 결속하지 못했다. 빈 용기라는 이름만으로 물 저장 가능성을 추가하지 않는다. 필요한 추가 근거는 이 exact item의 해당 행동/재료 입력 또는 효과를 명시하는 vanilla source 관계이며, current admission 부재를 해소할 승인만으로 대체하지 않음. | C002 | M039 |
| Base.FiberglassStock | public / core | keep / description_ready | scripts/newitems.txt:2541; exact WeaponPart/PartType=Stock/MountOn=HuntingRifle; VarmintRifle. 총기 개조 부품이라는 current 목적은 구체적. 실제 성능·조명/총검 공격은 추가하지 않는다. | C014 | M014 |
| Base.FireWoodKit | public / no-core | review_hold / review_required | scripts/newitems.txt:2389: exact Type=Normal, OBSOLETE=true. 정상 B41에서 이 exact item의 생성·사용 가능성/등록이 미확정이다. 작동하는 별도 FullType으로 대체하거나 기존 no-core 때문에 보류하는 것이 아님. | C052 | M221 |
| Base.FirstAidKit | public / core | revise / description_ready | scripts/clothing/clothing_bags.txt:409의 exact Container/Capacity=4. 보관·운반 역할이 명확하며 이름에 따른 내용물 제한/냉장 효과는 추가하지 않는다. | C022 | M023 |
| Base.FishFillet | public / no-core | revise / description_ready | scripts/items_food.txt:2027의 exact H=-25, T=미선언; EvolvedRecipe 재료 선언 확인; DangerousUncooked=TRUE. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C063 | M004 |
| Base.FishFried | public / core | revise / description_ready | scripts/items_food.txt:7263의 exact H=-30, T=미선언; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C004 | M004 |
| Base.FishRoe | public / no-core | revise / description_ready | scripts/items_food.txt:6269의 exact H=-10, T=미선언; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C004 | M004 |
| Base.FishingLine | public / core | keep / description_ready | Make/Fix Fishing Rod input인 낚싯줄 역할이 현재 문구와 일치한다. | C003 | M101 |
| Base.FishingMag1 | public / core | revise / description_ready | §학습 문구 87개: 해당 exact SkillTrained 또는 TeachedRecipes/knowledge token의 source를 구분했다. | C026 | M053 |
| Base.FishingMag2 | public / core | revise / description_ready | §학습 문구 87개: 해당 exact SkillTrained 또는 TeachedRecipes/knowledge token의 source를 구분했다. | C026 | M053 |
| Base.FishingNet | public / no-core | revise / description_ready | §농사·낚시·덫: 해당 exact source 선택·조건 및 실제 결과 변화 연결 | C026 | M025 |
| Base.FishingRod | public / no-core | revise / description_ready | §농사·낚시·덫: 해당 exact source 선택·조건 및 실제 결과 변화 연결 | C026 | M025 |
| Base.FishingRodBreak | public / core | revise / description_ready | scripts/items_weapons.txt:2536; recipes:1168–1190의 exact broken rod 입력. 수리 재료 자체로만 표현하던 current 범위를 교정. | C089 | M102 |
| Base.FishingRodTwineLine | public / no-core | revise / description_ready | §농사·낚시·덫: 해당 exact source 선택·조건 및 실제 결과 변화 연결 | C026 | M025 |
| Base.FishingTackle | public / no-core | revise / description_ready | §농사·낚시·덫: 해당 exact source 선택·조건 및 실제 결과 변화 연결 | C026 | M025 |
| Base.FishingTackle2 | public / no-core | revise / description_ready | §농사·낚시·덫: 해당 exact source 선택·조건 및 실제 결과 변화 연결 | C026 | M025 |
| Base.FlameTrap | public / core | revise / description_ready | scripts/newitems.txt:3146의 exact FirePower=97. 원격/센서/타이머는 각 선언대로 별도 조건이며 모든 장치를 같은 투척/폭발 효과로 묶지 않는다. Java 내부·PZ 실제 효과는 미관찰. | C090 | M005 |
| Base.FlameTrapRemote | public / no-core | revise / description_ready | scripts/newitems.txt:3287의 exact FirePower=97. 원격/센서/타이머는 각 선언대로 별도 조건이며 모든 장치를 같은 투척/폭발 효과로 묶지 않는다. Java 내부·PZ 실제 효과는 미관찰. | C090 | M005 |
| Base.FlameTrapSensorV1 | public / no-core | revise / description_ready | scripts/newitems.txt:3200의 exact FirePower=97. 원격/센서/타이머는 각 선언대로 별도 조건이며 모든 장치를 같은 투척/폭발 효과로 묶지 않는다. Java 내부·PZ 실제 효과는 미관찰. | C090 | M005 |
| Base.FlameTrapSensorV2 | public / no-core | revise / description_ready | scripts/newitems.txt:3229의 exact FirePower=97. 원격/센서/타이머는 각 선언대로 별도 조건이며 모든 장치를 같은 투척/폭발 효과로 묶지 않는다. Java 내부·PZ 실제 효과는 미관찰. | C090 | M005 |
| Base.FlameTrapSensorV3 | public / no-core | revise / description_ready | scripts/newitems.txt:3258의 exact FirePower=97. 원격/센서/타이머는 각 선언대로 별도 조건이며 모든 장치를 같은 투척/폭발 효과로 묶지 않는다. Java 내부·PZ 실제 효과는 미관찰. | C090 | M005 |
| Base.FlameTrapTriggered | public / no-core | revise / description_ready | scripts/newitems.txt:3172의 exact FirePower=97. 원격/센서/타이머는 각 선언대로 별도 조건이며 모든 장치를 같은 투척/폭발 효과로 묶지 않는다. Java 내부·PZ 실제 효과는 미관찰. | C090 | M005 |
| Base.Flightcase | public / core | revise / description_ready | scripts/clothing/clothing_bags.txt:458의 exact Container/Capacity=5. 보관·운반 역할이 명확하며 이름에 따른 내용물 제한/냉장 효과는 추가하지 않는다. | C022 | M023 |
| Base.FlintKnife | public / no-core | revise / description_ready | scripts/items_weapons.txt:3420; exact Type=Weapon/damage=0.4–0.6. 연주·경기·배관 수리 같은 현실 기능을 추정하지 않는다. | C021 | M022 |
| Base.Flour | public / core | revise / description_ready | §조리 문구 32개: 이 exact item의 input/result/keep 역할과 원본 recipe를 분리 검토했다. | C026 | M027 |
| Base.FluffyfootBunny | public / core | review_hold / review_required | scripts/newitems.txt:4836; 장난감의 Normal 정체성/원문 locator 확인; 보기·놀이·수집 action 의 실제 사용 경로는 미확정. 유사 매체의 재생·학습 기능을 전이하지 않음. 필요한 추가 근거는 이 exact item의 해당 행동/재료 입력 또는 효과를 명시하는 vanilla source 관계이며, current admission 부재를 해소할 승인만으로 대체하지 않음. | C015 | M054 |
| Base.Flute | public / no-core | revise / description_ready | scripts/items_weapons.txt:640; exact Type=Weapon/damage=0.1–0.2. 연주·경기·배관 수리 같은 현실 기능을 추정하지 않는다. | C021 | M022 |
| Base.Football | public / core | review_hold / review_required | scripts/newitems.txt:422: 현재 경기 규칙에 맞춘 놀이 assertion을 실제 경기/투척 기능과 결속하지 못했다. Normal 소품이라는 선언은 경기 실행 근거가 아니다. 필요한 추가 근거는 이 exact item의 해당 행동/재료 입력 또는 효과를 명시하는 vanilla source 관계이며, current admission 부재를 해소할 승인만으로 대체하지 않음. | C002 | M033 |
| Base.Football2 | public / core | revise / description_ready | scripts/newitems.txt:3647; scripts/newitems.txt:3647 Weapon/SwingAnim=Throw/UseSelf/PhysicsObject=Ball. Normal Football과 별개 exact item이며 foraging source에도 참조됨. 경기 규칙·무해함·데미지 효과는 주장하지 않음. | C229 | M223 |
| Base.Fork | public / core | revise / description_ready | scripts/items_weapons.txt:3569; exact Weapon/damage=0.1–0.1, 해당 Attach … to Spear input. 칼/식기·도구의 이름만으로 다른 작동을 추정하지 않음. | C047 | M057 |
| Base.FountainCup | public / core | review_hold / review_required | scripts/newitems.txt:4781: 이 빈 item의 재사용/처리 목적을 실제 전환·상호작용에 결속하지 못했다. 빈 용기라는 이름만으로 물 저장 가능성을 추가하지 않는다. 필요한 추가 근거는 이 exact item의 해당 행동/재료 입력 또는 효과를 명시하는 vanilla source 관계이며, current admission 부재를 해소할 승인만으로 대체하지 않음. | C002 | M039 |
| Base.Frame | public / core | review_hold / review_required | scripts/newitems.txt:986: Normal Frame을 실제 사진/그림 넣기 상호작용에 결속하지 못했다. Container로 가정하지 않는다. 필요한 추가 근거는 이 exact item의 해당 행동/재료 입력 또는 효과를 명시하는 vanilla source 관계이며, current admission 부재를 해소할 승인만으로 대체하지 않음. | C002 | M103 |
| Base.FreddyFox | public / core | review_hold / review_required | scripts/newitems.txt:4809; 장난감의 Normal 정체성/원문 locator 확인; 보기·놀이·수집 action 의 실제 사용 경로는 미확정. 유사 매체의 재생·학습 기능을 전이하지 않음. 필요한 추가 근거는 이 exact item의 해당 행동/재료 입력 또는 효과를 명시하는 vanilla source 관계이며, current admission 부재를 해소할 승인만으로 대체하지 않음. | C015 | M054 |
| Base.FriedOnionRings | public / core | revise / description_ready | scripts/items_food.txt:7413의 exact H=-10, T=미선언; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C004 | M004 |
| Base.FriedOnionRingsCraft | public / no-core | revise / description_ready | scripts/items_food.txt:7433의 exact H=-10, T=미선언; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C004 | M004 |
| Base.Fries | public / core | revise / description_ready | scripts/items_food.txt:5652의 exact H=-10, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C012 | M012 |
| Base.FrillyUnderpants_Black | public / no-core | revise / description_ready | scripts/clothing/clothing_underwear.txt:495: Clothing/BodyLocation=UnderwearBottom. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C184 | M017 |
| Base.FrillyUnderpants_Pink | public / no-core | revise / description_ready | scripts/clothing/clothing_underwear.txt:507: Clothing/BodyLocation=UnderwearBottom. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C184 | M017 |
| Base.FrillyUnderpants_Red | public / no-core | revise / description_ready | scripts/clothing/clothing_underwear.txt:519: Clothing/BodyLocation=UnderwearBottom. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C184 | M017 |
| Base.Frog | public / core | revise / description_ready | §조리 문구 32개: 이 exact item의 input/result/keep 역할과 원본 recipe를 분리 검토했다. | C026 | M027 |
| Base.FrogMeat | public / no-core | revise / description_ready | scripts/items_food.txt:2312의 exact H=-10, T=미선언; EvolvedRecipe 재료 선언 확인; DangerousUncooked=TRUE. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C063 | M004 |
| Base.FrontCarDoor1 | public / core | keep / description_ready | scripts/vehicles/vehiclesitems.txt:1059; exact VehicleType=1와 해당 door/window/windshield part 관계. 현재 패널/유리 탈착 목적은 이미 구체적이며 방탄·방호 효과를 추가하지 않는다. | C014 | M096 |
| Base.FrontCarDoor2 | public / core | keep / description_ready | scripts/vehicles/vehiclesitems.txt:1101; exact VehicleType=2와 해당 door/window/windshield part 관계. 현재 패널/유리 탈착 목적은 이미 구체적이며 방탄·방호 효과를 추가하지 않는다. | C014 | M096 |
| Base.FrontCarDoor3 | public / core | keep / description_ready | scripts/vehicles/vehiclesitems.txt:1143; exact VehicleType=3와 해당 door/window/windshield part 관계. 현재 패널/유리 탈착 목적은 이미 구체적이며 방탄·방호 효과를 추가하지 않는다. | C014 | M096 |
| Base.FrontWindow1 | public / core | keep / description_ready | scripts/vehicles/vehiclesitems.txt:918; exact VehicleType=1와 해당 door/window/windshield part 관계. 현재 패널/유리 탈착 목적은 이미 구체적이며 방탄·방호 효과를 추가하지 않는다. | C014 | M096 |
| Base.FrontWindow2 | public / core | keep / description_ready | scripts/vehicles/vehiclesitems.txt:974; exact VehicleType=2와 해당 door/window/windshield part 관계. 현재 패널/유리 탈착 목적은 이미 구체적이며 방탄·방호 효과를 추가하지 않는다. | C014 | M096 |
| Base.FrontWindow3 | public / core | keep / description_ready | scripts/vehicles/vehiclesitems.txt:1030; exact VehicleType=3와 해당 door/window/windshield part 관계. 현재 패널/유리 탈착 목적은 이미 구체적이며 방탄·방호 효과를 추가하지 않는다. | C014 | M096 |
| Base.FruitSalad | public / no-core | revise / description_ready | scripts/items_food.txt:5056의 exact H=-60, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C012 | M012 |
| Base.FullKettle | public / no-core | revise / description_ready | scripts/items.txt:789: CanStoreWater=TRUE, ReplaceOnUseOn=WaterSource-FullKettle. §빈 물 용기와 같은 exact 물 저장/전환 사실을 재사용하며 음용 안전성·현재 내용물은 추정하지 않는다. | C038 | M041 |
| Base.FurbertSquirrel | public / core | review_hold / review_required | scripts/newitems.txt:4845; 장난감의 Normal 정체성/원문 locator 확인; 보기·놀이·수집 action 의 실제 사용 경로는 미확정. 유사 매체의 재생·학습 기능을 전이하지 않음. 필요한 추가 근거는 이 exact item의 해당 행동/재료 입력 또는 효과를 명시하는 vanilla source 관계이며, current admission 부재를 해소할 승인만으로 대체하지 않음. | C015 | M054 |
| Base.GamePieceBlack | public / core | review_hold / review_required | scripts/newitems.txt:4874: §남은 혼합 역할: 현재 놀이 assertion을 실제 게임 플레이/지루함 감소에 결속하지 못했다. Normal 소품과 실제 놀이 기능을 구분한다. 필요한 추가 근거는 이 exact item의 해당 행동/재료 입력 또는 효과를 명시하는 vanilla source 관계이며, current admission 부재를 해소할 승인만으로 대체하지 않음. | C002 | M021 |
| Base.GamePieceRed | public / core | review_hold / review_required | scripts/newitems.txt:4884: §남은 혼합 역할: 현재 놀이 assertion을 실제 게임 플레이/지루함 감소에 결속하지 못했다. Normal 소품과 실제 놀이 기능을 구분한다. 필요한 추가 근거는 이 exact item의 해당 행동/재료 입력 또는 효과를 명시하는 vanilla source 관계이며, current admission 부재를 해소할 승인만으로 대체하지 않음. | C002 | M021 |
| Base.GamePieceWhite | public / core | review_hold / review_required | scripts/newitems.txt:4894: §남은 혼합 역할: 현재 놀이 assertion을 실제 게임 플레이/지루함 감소에 결속하지 못했다. Normal 소품과 실제 놀이 기능을 구분한다. 필요한 추가 근거는 이 exact item의 해당 행동/재료 입력 또는 효과를 명시하는 vanilla source 관계이며, current admission 부재를 해소할 승인만으로 대체하지 않음. | C002 | M021 |
| Base.Garbagebag | public / core | revise / description_ready | scripts/clothing/clothing_bags.txt:294의 exact Container/Capacity=20. 보관·운반 역할이 명확하며 이름에 따른 내용물 제한/냉장 효과는 추가하지 않는다. | C022 | M023 |
| Base.GardenFork | public / no-core | revise / description_ready | scripts/items_weapons.txt:4363; exact DigPlow tag → ISFarmingMenu:20의 not-broken 도구 선택. 다른 작업의 가능/불가능을 추정하지 않는다. | C091 | M104 |
| Base.GardenHoe | public / no-core | revise / description_ready | scripts/items_weapons.txt:1823; exact DigPlow tag → ISFarmingMenu:20의 not-broken 도구 선택. 다른 작업의 가능/불가능을 추정하지 않는다. | C091 | M104 |
| Base.GardenSaw | public / core | revise / description_ready | scripts/items.txt:463; exact Saw Logs2 keep 및 Saw tag. 모든 톱의 총열 절단 기능을 복사하지 않는다. | C092 | M105 |
| Base.Garter | public / no-core | revise / description_ready | scripts/clothing/clothing_underwear.txt:328: Clothing/BodyLocation=UnderwearExtra2. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C193 | M017 |
| Base.Generator | public / core | keep / description_ready | 기존 승인 발전기 설치·전력 공급 기본 목적을 유지한다. 연료/연결 지식·실내 위험은 별도 조건이다. | C003 | M106 |
| Base.Ghillie_Top | public / no-core | revise / description_ready | scripts/clothing/clothing_jacket.txt:22: Clothing/BodyLocation=FullTop. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C194 | M017 |
| Base.Ghillie_Trousers | public / no-core | revise / description_ready | scripts/clothing/clothing_pants.txt:232: Clothing/BodyLocation=Pants. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C190 | M017 |
| Base.GingerPickled | public / core | revise / description_ready | scripts/items_food.txt:6289의 exact H=-5, T=미선언; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C004 | M004 |
| Base.GingerRoot | public / core | revise / description_ready | scripts/items_food.txt:8702의 exact H=-5, T=미선언; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C004 | M004 |
| Base.Ginseng | public / core | revise / description_ready | scripts/items_food.txt:4117의 exact H=-1, T=미선언; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C004 | M004 |
| Base.GlassTumbler | public / no-core | revise / description_ready | scripts/newitems.txt:4579: CanStoreWater=TRUE, ReplaceOnUseOn=WaterSource-GlassTumblerWater. §빈 물 용기와 같은 exact 물 저장/전환 사실을 재사용하며 음용 안전성·현재 내용물은 추정하지 않는다. | C038 | M041 |
| Base.GlassTumblerWater | public / no-core | revise / description_ready | scripts/items_food.txt:9714: CanStoreWater=TRUE, ReplaceOnUseOn=WaterSource-GlassTumblerWater. §빈 물 용기와 같은 exact 물 저장/전환 사실을 재사용하며 음용 안전성·현재 내용물은 추정하지 않는다. | C038 | M041 |
| Base.GlassWine | public / no-core | revise / description_ready | scripts/newitems.txt:4595: CanStoreWater=TRUE, ReplaceOnUseOn=WaterSource-GlassWineWater. §빈 물 용기와 같은 exact 물 저장/전환 사실을 재사용하며 음용 안전성·현재 내용물은 추정하지 않는다. | C038 | M041 |
| Base.GlassWineWater | public / no-core | revise / description_ready | scripts/items_food.txt:9690: CanStoreWater=TRUE, ReplaceOnUseOn=WaterSource-GlassWineWater. §빈 물 용기와 같은 exact 물 저장/전환 사실을 재사용하며 음용 안전성·현재 내용물은 추정하지 않는다. | C038 | M041 |
| Base.Glasses | public / no-core | revise / description_ready | scripts/clothing/clothing_others.txt:99: Clothing/BodyLocation=Eyes. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C195 | M017 |
| Base.Glasses_Aviators | public / no-core | revise / description_ready | scripts/clothing/clothing_others.txt:112: Clothing/BodyLocation=Eyes. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C195 | M017 |
| Base.Glasses_Eyepatch_Left | public / core | keep / description_ready | scripts/clothing/clothing_others.txt:209의 Clothing/BodyLocation=LeftEye와 현재 착용 목적 일치. 수치 추가나 감염/위장 효과를 강제하지 않는다. | C018 | M018 |
| Base.Glasses_Eyepatch_Right | public / core | keep / description_ready | scripts/clothing/clothing_others.txt:224의 Clothing/BodyLocation=RightEye와 현재 착용 목적 일치. 수치 추가나 감염/위장 효과를 강제하지 않는다. | C018 | M018 |
| Base.Glasses_Normal | public / no-core | revise / description_ready | scripts/clothing/clothing_others.txt:124: Clothing/BodyLocation=Eyes. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C195 | M017 |
| Base.Glasses_Reading | public / no-core | revise / description_ready | scripts/clothing/clothing_others.txt:136: Clothing/BodyLocation=Eyes. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C195 | M017 |
| Base.Glasses_SafetyGoggles | public / no-core | revise / description_ready | scripts/clothing/clothing_others.txt:148: Clothing/BodyLocation=Eyes. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C195 | M017 |
| Base.Glasses_Shooting | public / core | keep / description_ready | scripts/clothing/clothing_others.txt:160의 Clothing/BodyLocation=Eyes와 현재 착용 목적 일치. 수치 추가나 감염/위장 효과를 강제하지 않는다. | C018 | M018 |
| Base.Glasses_SkiGoggles | public / no-core | revise / description_ready | scripts/clothing/clothing_others.txt:173: Clothing/BodyLocation=Eyes. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C195 | M017 |
| Base.Glasses_Sun | public / no-core | revise / description_ready | scripts/clothing/clothing_others.txt:185: Clothing/BodyLocation=Eyes. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C195 | M017 |
| Base.Glasses_SwimmingGoggles | public / no-core | revise / description_ready | scripts/clothing/clothing_others.txt:197: Clothing/BodyLocation=Eyes. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C195 | M017 |
| Base.GloveBox1 | public / core | revise / description_ready | scripts/vehicles/vehiclesitems.txt:1272; exact VehicleType=1/MaxCapacity와 seat/trunk container 선언. 수납 부품을 모두 자유롭게 탈착 가능한 물건으로 묶지 않는다. | C041 | M046 |
| Base.GloveBox2 | public / core | revise / description_ready | scripts/vehicles/vehiclesitems.txt:1285; exact VehicleType=2/MaxCapacity와 seat/trunk container 선언. 수납 부품을 모두 자유롭게 탈착 가능한 물건으로 묶지 않는다. | C041 | M046 |
| Base.GloveBox3 | public / core | revise / description_ready | scripts/vehicles/vehiclesitems.txt:1298; exact VehicleType=3/MaxCapacity와 seat/trunk container 선언. 수납 부품을 모두 자유롭게 탈착 가능한 물건으로 묶지 않는다. | C041 | M046 |
| Base.Gloves_BoxingBlue | public / no-core | revise / description_ready | scripts/clothing/clothing_others.txt:810: Clothing/BodyLocation=Hands. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C196 | M017 |
| Base.Gloves_BoxingRed | public / no-core | revise / description_ready | scripts/clothing/clothing_others.txt:796: Clothing/BodyLocation=Hands. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C196 | M017 |
| Base.Gloves_FingerlessGloves | public / no-core | revise / description_ready | scripts/clothing/clothing_others.txt:239: Clothing/BodyLocation=Hands. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C196 | M017 |
| Base.Gloves_LeatherGloves | public / no-core | revise / description_ready | scripts/clothing/clothing_others.txt:253: Clothing/BodyLocation=Hands. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C196 | M017 |
| Base.Gloves_LeatherGlovesBlack | public / no-core | revise / description_ready | scripts/clothing/clothing_others.txt:270: Clothing/BodyLocation=Hands. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C196 | M017 |
| Base.Gloves_LongWomenGloves | public / no-core | revise / description_ready | scripts/clothing/clothing_others.txt:287: Clothing/BodyLocation=Hands. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C196 | M017 |
| Base.Gloves_Surgical | empty / no-core | revise / description_ready | scripts/clothing/clothing_others.txt:317: Clothing/BodyLocation=Hands. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C196 | M017 |
| Base.Gloves_WhiteTINT | public / no-core | revise / description_ready | scripts/clothing/clothing_others.txt:302: Clothing/BodyLocation=Hands. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C196 | M017 |
| Base.Glue | public / no-core | revise / description_ready | scripts/newitems.txt:1704; recipes.txt:2172–2243 Remote/Trigger/Timer 소비 입력. | C094 | M011 |
| Base.GolfBall | public / core | review_hold / review_required | scripts/newitems.txt:432: 현재 경기 규칙에 맞춘 놀이 assertion을 실제 경기/투척 기능과 결속하지 못했다. Normal 소품이라는 선언은 경기 실행 근거가 아니다. 필요한 추가 근거는 이 exact item의 해당 행동/재료 입력 또는 효과를 명시하는 vanilla source 관계이며, current admission 부재를 해소할 승인만으로 대체하지 않음. | C002 | M033 |
| Base.Golfclub | public / no-core | revise / description_ready | scripts/items_weapons.txt:1412; exact Type=Weapon/damage=0.5–1. 연주·경기·배관 수리 같은 현실 기능을 추정하지 않는다. | C021 | M022 |
| Base.GrahamCrackers | public / core | revise / description_ready | scripts/items_food.txt:7284의 exact H=-5, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C012 | M012 |
| Base.GranolaBar | public / core | revise / description_ready | scripts/items_food.txt:7788의 exact H=-15, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C012 | M012 |
| Base.GrapeLeaves | public / core | revise / description_ready | scripts/items_food.txt:4175의 exact H=-4, T=미선언; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C004 | M004 |
| Base.Grapefruit | public / core | revise / description_ready | scripts/items_food.txt:6309의 exact H=-20, T=-50; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C020 | M004 |
| Base.Grapes | public / core | revise / description_ready | scripts/items_food.txt:1585의 exact H=-15, T=-5; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C020 | M004 |
| Base.Grasshopper | public / core | revise / description_ready | scripts/items_food.txt:4284의 exact H=-5, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C012 | M012 |
| Base.Gravelbag | public / no-core | revise / description_ready | scripts/items.txt:811; ISBuildMenu:856/877의 exact need material 및 FireFighting.isExtinguisher. 소화/장벽 역할별 조건 분리. | C095 | M108 |
| Base.Gravy | public / core | revise / description_ready | scripts/items_food.txt:7300의 exact H=-8, T=미선언; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C004 | M004 |
| Base.GravyMix | public / core | revise / description_ready | §조리 문구 32개: 이 exact item의 input/result/keep 역할과 원본 recipe를 분리 검토했다. | C026 | M027 |
| Base.GriddlePanFriedVegetables | public / no-core | revise / description_ready | scripts/items_food.txt:5261의 exact H=-10, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C012 | M012 |
| Base.GridlePan | public / no-core | revise / description_ready | scripts/items_weapons.txt:1281; evolvedrecipes.txt:54/63 BaseItem=GridlePan→볶음 요리 결과. | C096 | M011 |
| Base.GrillBrush | public / core | review_hold / review_required | scripts/newitems.txt:4710; Normal 선언은 확인되나 exact 사용/조리 입력이 미확정; 유사 도구·Teabag2·Flour의 기능 전이 금지. 필요한 추가 근거는 이 exact item의 해당 행동/재료 입력 또는 효과를 명시하는 vanilla source 관계이며, current admission 부재를 해소할 승인만으로 대체하지 않음. | C049 | M069 |
| Base.GrilledCheese | public / no-core | revise / description_ready | scripts/items_food.txt:4306의 exact H=-16, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C012 | M012 |
| Base.GroceryBag1 | public / core | keep / description_ready | scripts/newBags.txt:123의 exact Container/Capacity=8. 보관·운반 역할이 명확하며 이름에 따른 내용물 제한/냉장 효과는 추가하지 않는다. | C023 | M023 |
| Base.GroceryBag2 | public / core | keep / description_ready | scripts/newBags.txt:136의 exact Container/Capacity=8. 보관·운반 역할이 명확하며 이름에 따른 내용물 제한/냉장 효과는 추가하지 않는다. | C023 | M023 |
| Base.GroceryBag3 | public / core | keep / description_ready | scripts/newBags.txt:149의 exact Container/Capacity=8. 보관·운반 역할이 명확하며 이름에 따른 내용물 제한/냉장 효과는 추가하지 않는다. | C023 | M023 |
| Base.GroceryBag4 | public / core | keep / description_ready | scripts/newBags.txt:162의 exact Container/Capacity=8. 보관·운반 역할이 명확하며 이름에 따른 내용물 제한/냉장 효과는 추가하지 않는다. | C023 | M023 |
| Base.GroceryBag5 | public / core | keep / description_ready | scripts/newBags.txt:175의 exact Container/Capacity=8. 보관·운반 역할이 명확하며 이름에 따른 내용물 제한/냉장 효과는 추가하지 않는다. | C023 | M023 |
| Base.Guacamole | public / no-core | revise / description_ready | scripts/items_food.txt:7912의 exact H=-8, T=미선언; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C004 | M004 |
| Base.GuitarAcoustic | public / no-core | revise / description_ready | scripts/items_weapons.txt:1590; exact Type=Weapon/damage=0.3–0.8. 연주·경기·배관 수리 같은 현실 기능을 추정하지 않는다. | C021 | M022 |
| Base.GuitarElectricBassBlack | public / no-core | revise / description_ready | scripts/items_weapons.txt:2966; exact Type=Weapon/damage=0.9–1.4. 연주·경기·배관 수리 같은 현실 기능을 추정하지 않는다. | C021 | M022 |
| Base.GuitarElectricBassBlue | public / no-core | revise / description_ready | scripts/items_weapons.txt:3010; exact Type=Weapon/damage=0.9–1.4. 연주·경기·배관 수리 같은 현실 기능을 추정하지 않는다. | C021 | M022 |
| Base.GuitarElectricBassRed | public / no-core | revise / description_ready | scripts/items_weapons.txt:3054; exact Type=Weapon/damage=0.9–1.4. 연주·경기·배관 수리 같은 현실 기능을 추정하지 않는다. | C021 | M022 |
| Base.GuitarElectricBlack | public / no-core | revise / description_ready | scripts/items_weapons.txt:3142; exact Type=Weapon/damage=0.8–1.2. 연주·경기·배관 수리 같은 현실 기능을 추정하지 않는다. | C021 | M022 |
| Base.GuitarElectricBlue | public / no-core | revise / description_ready | scripts/items_weapons.txt:3187; exact Type=Weapon/damage=0.8–1.2. 연주·경기·배관 수리 같은 현실 기능을 추정하지 않는다. | C021 | M022 |
| Base.GuitarElectricRed | public / no-core | revise / description_ready | scripts/items_weapons.txt:3232; exact Type=Weapon/damage=0.8–1.2. 연주·경기·배관 수리 같은 현실 기능을 추정하지 않는다. | C021 | M022 |
| Base.Guitarcase | public / core | revise / description_ready | scripts/clothing/clothing_bags.txt:475의 exact Container/Capacity=5. 보관·운반 역할이 명확하며 이름에 따른 내용물 제한/냉장 효과는 추가하지 않는다. | C022 | M023 |
| Base.Gum | public / core | revise / description_ready | scripts/items_food.txt:7323의 exact H=-1, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C012 | M012 |
| Base.GummyBears | public / core | revise / description_ready | scripts/items_food.txt:9223의 exact H=-5, T=미선언; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C004 | M004 |
| Base.GummyWorms | public / core | revise / description_ready | scripts/items_food.txt:9242의 exact H=-5, T=미선언; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C004 | M004 |
| Base.GunLight | public / core | keep / description_ready | scripts/newitems.txt:2603; exact WeaponPart/PartType=Canon/MountOn=Pistol; Pistol2; Pistol3. 총기 개조 부품이라는 current 목적은 구체적. 실제 성능·조명/총검 공격은 추가하지 않는다. | C014 | M014 |
| Base.GunPowder | public / core | revise / description_ready | scripts/newitems.txt:164; recipes.txt:2666 Make Pipe bomb input. Blacksmith 탄약 recipe 가용성은 별도 보류하므로 탄약 제작 일반 주장 축소. | C097 | M064 |
| Base.HairDyeBlack | public / core | keep / description_ready | 각 exact HairDye 선언과 ISDyeHair의 머리/수염 색 변경 경로가 일치한다. | C003 | M109 |
| Base.HairDyeBlonde | public / core | keep / description_ready | 각 exact HairDye 선언과 ISDyeHair의 머리/수염 색 변경 경로가 일치한다. | C003 | M109 |
| Base.HairDyeBlue | public / core | keep / description_ready | 각 exact HairDye 선언과 ISDyeHair의 머리/수염 색 변경 경로가 일치한다. | C003 | M109 |
| Base.HairDyeGinger | public / core | keep / description_ready | 각 exact HairDye 선언과 ISDyeHair의 머리/수염 색 변경 경로가 일치한다. | C003 | M109 |
| Base.HairDyeGreen | public / core | keep / description_ready | 각 exact HairDye 선언과 ISDyeHair의 머리/수염 색 변경 경로가 일치한다. | C003 | M109 |
| Base.HairDyeLightBrown | public / core | keep / description_ready | 각 exact HairDye 선언과 ISDyeHair의 머리/수염 색 변경 경로가 일치한다. | C003 | M109 |
| Base.HairDyePink | public / core | keep / description_ready | 각 exact HairDye 선언과 ISDyeHair의 머리/수염 색 변경 경로가 일치한다. | C003 | M109 |
| Base.HairDyeRed | public / core | keep / description_ready | 각 exact HairDye 선언과 ISDyeHair의 머리/수염 색 변경 경로가 일치한다. | C003 | M109 |
| Base.HairDyeWhite | public / core | keep / description_ready | 각 exact HairDye 선언과 ISDyeHair의 머리/수염 색 변경 경로가 일치한다. | C003 | M109 |
| Base.HairDyeYellow | public / core | keep / description_ready | 각 exact HairDye 선언과 ISDyeHair의 머리/수염 색 변경 경로가 일치한다. | C003 | M109 |
| Base.Hairgel | public / core | keep / description_ready | 기존 헤어 젤 문구와 ISCharacterScreen/ISCutHair의 Mohawk 선택·소모를 연결했다. | C003 | M110 |
| Base.Hairspray | public / core | revise / description_ready | scripts/newitems.txt:119; exact Make Aerosol bomb input. 머리 모양 변경 효과는 source가 없어 추가하지 않는다. | C098 | M111 |
| Base.HalloweenPumpkin | public / no-core | revise / description_ready | scripts/items_food.txt:7845의 exact H=-40, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C012 | M012 |
| Base.Ham | public / core | revise / description_ready | scripts/items_food.txt:2441의 exact H=-60, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C012 | M012 |
| Base.HamSlice | public / no-core | revise / description_ready | scripts/items_food.txt:2462의 exact H=-10, T=미선언; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C004 | M004 |
| Base.Hammer | public / core | revise / description_ready | §목공 도구: Hammer tag·ISBuildMenu의 못 쓰는 목공 구조물 | C099 | M112 |
| Base.HammerStone | public / core | revise / description_ready | scripts/items_weapons.txt:1147; exact Hammer tag와 §Hammer에서 읽은 ISBuildMenu tag 선택. RemoveBarricade tag는 이 item에 복사하지 않는다. | C100 | M113 |
| Base.HandAxe | public / core | keep / description_ready | scripts/items_weapons.txt:267; exact ChopTree tag, ISWorldObjectContextMenu:439/1297 및 ISChopTreeAction queue. 현재 벌목 역할이 구체적. | C014 | M020 |
| Base.HandFork | public / core | revise / description_ready | scripts/items_weapons.txt:3324; exact Weapon/damage=0.2–0.4, 해당 Attach … to Spear input. 칼/식기·도구의 이름만으로 다른 작동을 추정하지 않음. | C047 | M057 |
| Base.HandScythe | public / no-core | revise / description_ready | scripts/items_weapons.txt:311; exact Weapon/damage=0.6–1.2. 구체 작업 source가 미결속인 부분을 일반 '작업'으로 확대하지 않는다. | C066 | M073 |
| Base.HandTorch | public / core | revise / description_ready | §남은 혼합 역할: 해당 exact 조명/무선·매체/운동 source 조건을 분리했다. | C026 | M114 |
| Base.Handbag | public / core | keep / description_ready | scripts/clothing/clothing_bags.txt:375의 exact Container/Capacity=8. 보관·운반 역할이 명확하며 이름에 따른 내용물 제한/냉장 효과는 추가하지 않는다. | C023 | M023 |
| Base.Handle | public / core | review_hold / review_required | scripts/newitems.txt:4017; recipes.txt:3237/3254의 Anvil·Blacksmith·learned smithing recipe 입력은 확인되나 ISBlacksmithMenu의 건설 route disable과 정상 B41 획득/실행 관계 미해결; 일반 목공 가공 용도로 확장 불가. 남은 입력은 정상 B41에서 이 legacy 단조 recipe/Anvil·Blacksmith 기술을 사용할 수 있는 근거 또는 실제 활성 대체 경로다. source successor 미발행이나 기존 core 부재 자체를 보류 사유로 삼지 않음. | C049 | M216 |
| Base.HankPic | public / core | review_hold / review_required | scripts/items.txt:171; 사진의 Normal 정체성/원문 locator 확인; 보기·놀이·수집 action 의 실제 사용 경로는 미확정. 유사 매체의 재생·학습 기능을 전이하지 않음. 필요한 추가 근거는 이 exact item의 해당 행동/재료 입력 또는 효과를 명시하는 vanilla source 관계이며, current admission 부재를 해소할 승인만으로 대체하지 않음. | C015 | M050 |
| Base.HardCandies | public / core | revise / description_ready | scripts/items_food.txt:9261의 exact H=-5, T=미선언; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C004 | M004 |
| Base.Hat_Antlers | public / no-core | revise / description_ready | scripts/clothing/clothing_hats.txt:1410: Clothing/BodyLocation=Hat. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C197 | M017 |
| Base.Hat_Army | public / no-core | revise / description_ready | scripts/clothing/clothing_hats.txt:3: Clothing/BodyLocation=Hat. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C197 | M017 |
| Base.Hat_BalaclavaFace | public / no-core | revise / description_ready | scripts/clothing/clothing_hats.txt:19: Clothing/BodyLocation=Mask. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C198 | M017 |
| Base.Hat_BalaclavaFull | public / no-core | revise / description_ready | scripts/clothing/clothing_hats.txt:33: Clothing/BodyLocation=Mask. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C198 | M017 |
| Base.Hat_Bandana | public / no-core | revise / description_ready | scripts/clothing/clothing_hats.txt:48: Clothing/BodyLocation=Hat. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C197 | M017 |
| Base.Hat_BandanaMask | public / core | reduce / description_ready | scripts/clothing/clothing_hats.txt:1248의 Clothing/BodyLocation=Mask. 현재 '보호'는 방어 종류/조건을 특정하지 않아 제거 제안; 별도 방어/면역을 추정하지 않는다. | C101 | M116 |
| Base.Hat_BandanaMaskTINT | public / core | reduce / description_ready | scripts/clothing/clothing_hats.txt:1232의 Clothing/BodyLocation=Mask. 현재 '보호'는 방어 종류/조건을 특정하지 않아 제거 제안; 별도 방어/면역을 추정하지 않는다. | C101 | M116 |
| Base.Hat_BandanaTINT | public / no-core | revise / description_ready | scripts/clothing/clothing_hats.txt:63: Clothing/BodyLocation=Hat. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C197 | M017 |
| Base.Hat_BandanaTied | public / core | reduce / description_ready | scripts/clothing/clothing_hats.txt:1202의 Clothing/BodyLocation=Hat. 현재 '보호'는 방어 종류/조건을 특정하지 않아 제거 제안; 별도 방어/면역을 추정하지 않는다. | C101 | M116 |
| Base.Hat_BandanaTiedTINT | public / core | reduce / description_ready | scripts/clothing/clothing_hats.txt:1217의 Clothing/BodyLocation=Hat. 현재 '보호'는 방어 종류/조건을 특정하지 않아 제거 제안; 별도 방어/면역을 추정하지 않는다. | C101 | M116 |
| Base.Hat_BaseballCap | public / no-core | revise / description_ready | scripts/clothing/clothing_hats.txt:78: Clothing/BodyLocation=Hat. §기본 착용 재판정의 추가 Wear(ForwardCap)→동일 FullType 착용 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C197 | M214 |
| Base.Hat_BaseballCapArmy | public / no-core | revise / description_ready | scripts/clothing/clothing_hats.txt:254: Clothing/BodyLocation=Hat. §기본 착용 재판정의 추가 Wear(ForwardCap)→동일 FullType 착용 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C197 | M214 |
| Base.Hat_BaseballCapArmy_Reverse | public / core | reduce / description_ready | scripts/clothing/clothing_hats.txt:270의 Clothing/BodyLocation=Hat. 현재 '보호'는 방어 종류/조건을 특정하지 않아 제거 제안; 별도 방어/면역을 추정하지 않는다. | C101 | M116 |
| Base.Hat_BaseballCapBlue | public / no-core | revise / description_ready | scripts/clothing/clothing_hats.txt:158: Clothing/BodyLocation=Hat. §기본 착용 재판정의 추가 Wear(ForwardCap)→동일 FullType 착용 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C197 | M214 |
| Base.Hat_BaseballCapBlue_Reverse | public / core | reduce / description_ready | scripts/clothing/clothing_hats.txt:174의 Clothing/BodyLocation=Hat. 현재 '보호'는 방어 종류/조건을 특정하지 않아 제거 제안; 별도 방어/면역을 추정하지 않는다. | C101 | M116 |
| Base.Hat_BaseballCapGreen | public / no-core | revise / description_ready | scripts/clothing/clothing_hats.txt:222: Clothing/BodyLocation=Hat. §기본 착용 재판정의 추가 Wear(ForwardCap)→동일 FullType 착용 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C197 | M214 |
| Base.Hat_BaseballCapGreen_Reverse | public / core | reduce / description_ready | scripts/clothing/clothing_hats.txt:238의 Clothing/BodyLocation=Hat. 현재 '보호'는 방어 종류/조건을 특정하지 않아 제거 제안; 별도 방어/면역을 추정하지 않는다. | C101 | M116 |
| Base.Hat_BaseballCapKY | public / no-core | revise / description_ready | scripts/clothing/clothing_hats.txt:110: Clothing/BodyLocation=Hat. §기본 착용 재판정의 추가 Wear(ForwardCap)→동일 FullType 착용 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C197 | M214 |
| Base.Hat_BaseballCapKY_Red | public / no-core | revise / description_ready | scripts/clothing/clothing_hats.txt:142: Clothing/BodyLocation=Hat. §기본 착용 재판정의 추가 Wear(ForwardCap)→동일 FullType 착용 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C197 | M214 |
| Base.Hat_BaseballCapKY_Reverse | public / core | reduce / description_ready | scripts/clothing/clothing_hats.txt:126의 Clothing/BodyLocation=Hat. 현재 '보호'는 방어 종류/조건을 특정하지 않아 제거 제안; 별도 방어/면역을 추정하지 않는다. | C101 | M116 |
| Base.Hat_BaseballCapRed | public / no-core | revise / description_ready | scripts/clothing/clothing_hats.txt:190: Clothing/BodyLocation=Hat. §기본 착용 재판정의 추가 Wear(ForwardCap)→동일 FullType 착용 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C197 | M214 |
| Base.Hat_BaseballCapRed_Reverse | public / core | reduce / description_ready | scripts/clothing/clothing_hats.txt:206의 Clothing/BodyLocation=Hat. 현재 '보호'는 방어 종류/조건을 특정하지 않아 제거 제안; 별도 방어/면역을 추정하지 않는다. | C101 | M116 |
| Base.Hat_BaseballCap_Reverse | public / core | reduce / description_ready | scripts/clothing/clothing_hats.txt:94의 Clothing/BodyLocation=Hat. 현재 '보호'는 방어 종류/조건을 특정하지 않아 제거 제안; 별도 방어/면역을 추정하지 않는다. §기본 착용 재판정의 추가 Wear/self FullType 경로를 동일하게 적용; existing core 유무를 source 충분성 기준으로 삼지 않음. | C101 | M214 |
| Base.Hat_BaseballHelmet_KY | public / no-core | revise / description_ready | scripts/clothing/clothing_hats.txt:286: Clothing/BodyLocation=Hat. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C197 | M017 |
| Base.Hat_BaseballHelmet_Rangers | public / no-core | revise / description_ready | scripts/clothing/clothing_hats.txt:302: Clothing/BodyLocation=Hat. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C197 | M017 |
| Base.Hat_BaseballHelmet_Z | public / no-core | revise / description_ready | scripts/clothing/clothing_hats.txt:318: Clothing/BodyLocation=Hat. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C197 | M017 |
| Base.Hat_Beany | public / no-core | revise / description_ready | scripts/clothing/clothing_hats.txt:334: Clothing/BodyLocation=Hat. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C197 | M017 |
| Base.Hat_Beret | public / no-core | revise / description_ready | scripts/clothing/clothing_hats.txt:349: Clothing/BodyLocation=Hat. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C197 | M017 |
| Base.Hat_BeretArmy | public / no-core | revise / description_ready | scripts/clothing/clothing_hats.txt:363: Clothing/BodyLocation=Hat. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C197 | M017 |
| Base.Hat_BicycleHelmet | public / no-core | revise / description_ready | scripts/clothing/clothing_hats.txt:377: Clothing/BodyLocation=Hat. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C197 | M017 |
| Base.Hat_BonnieHat | public / no-core | revise / description_ready | scripts/clothing/clothing_hats.txt:1121: Clothing/BodyLocation=Hat. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C197 | M017 |
| Base.Hat_BonnieHat_CamoGreen | public / no-core | revise / description_ready | scripts/clothing/clothing_hats.txt:1136: Clothing/BodyLocation=Hat. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C197 | M017 |
| Base.Hat_BoxingBlue | public / no-core | revise / description_ready | scripts/clothing/clothing_hats.txt:1355: Clothing/BodyLocation=FullHat. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C199 | M017 |
| Base.Hat_BoxingRed | public / no-core | revise / description_ready | scripts/clothing/clothing_hats.txt:1339: Clothing/BodyLocation=FullHat. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C199 | M017 |
| Base.Hat_BucketHat | public / no-core | revise / description_ready | scripts/clothing/clothing_hats.txt:1107: Clothing/BodyLocation=Hat. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C197 | M017 |
| Base.Hat_BunnyEarsBlack | public / no-core | revise / description_ready | scripts/clothing/clothing_hats.txt:1371: Clothing/BodyLocation=Hat. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C197 | M017 |
| Base.Hat_BunnyEarsWhite | public / no-core | revise / description_ready | scripts/clothing/clothing_hats.txt:1384: Clothing/BodyLocation=Hat. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C197 | M017 |
| Base.Hat_ChefHat | public / no-core | revise / description_ready | scripts/clothing/clothing_hats.txt:391: Clothing/BodyLocation=Hat. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C197 | M017 |
| Base.Hat_Cowboy | public / no-core | revise / description_ready | scripts/clothing/clothing_hats.txt:403: Clothing/BodyLocation=Hat. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C197 | M017 |
| Base.Hat_CrashHelmet | public / no-core | revise / description_ready | scripts/clothing/clothing_hats.txt:417: Clothing/BodyLocation=Hat. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C197 | M017 |
| Base.Hat_CrashHelmetFULL | public / no-core | revise / description_ready | scripts/clothing/clothing_hats.txt:433: Clothing/BodyLocation=FullHat. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C199 | M017 |
| Base.Hat_CrashHelmet_Police | public / no-core | revise / description_ready | scripts/clothing/clothing_hats.txt:450: Clothing/BodyLocation=Hat. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C197 | M017 |
| Base.Hat_CrashHelmet_Stars | public / no-core | revise / description_ready | scripts/clothing/clothing_hats.txt:467: Clothing/BodyLocation=Hat. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C197 | M017 |
| Base.Hat_DustMask | public / no-core | revise / description_ready | scripts/clothing/clothing_hats.txt:484: Clothing/BodyLocation=Mask. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C198 | M017 |
| Base.Hat_EarMuff_Protectors | public / no-core | revise / description_ready | scripts/clothing/clothing_hats.txt:513: Clothing/BodyLocation=Hat. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C197 | M017 |
| Base.Hat_EarMuffs | public / no-core | revise / description_ready | scripts/clothing/clothing_hats.txt:498: Clothing/BodyLocation=Hat. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C197 | M017 |
| Base.Hat_FastFood | public / no-core | revise / description_ready | scripts/clothing/clothing_hats.txt:528: Clothing/BodyLocation=Hat. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C197 | M017 |
| Base.Hat_FastFood_IceCream | public / no-core | revise / description_ready | scripts/clothing/clothing_hats.txt:540: Clothing/BodyLocation=Hat. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C197 | M017 |
| Base.Hat_FastFood_Spiffo | public / core | reduce / description_ready | scripts/clothing/clothing_hats.txt:552의 Clothing/BodyLocation=Hat. 현재 '보호'는 방어 종류/조건을 특정하지 않아 제거 제안; 별도 방어/면역을 추정하지 않는다. | C101 | M116 |
| Base.Hat_Fedora | public / no-core | revise / description_ready | scripts/clothing/clothing_hats.txt:564: Clothing/BodyLocation=Hat. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C197 | M017 |
| Base.Hat_Fedora_Delmonte | public / no-core | revise / description_ready | scripts/clothing/clothing_hats.txt:578: Clothing/BodyLocation=Hat. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C197 | M017 |
| Base.Hat_Fireman | public / no-core | revise / description_ready | scripts/clothing/clothing_hats.txt:593: Clothing/BodyLocation=Hat. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C197 | M017 |
| Base.Hat_FootballHelmet | public / no-core | revise / description_ready | scripts/clothing/clothing_hats.txt:611: Clothing/BodyLocation=FullHat. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C199 | M017 |
| Base.Hat_FurryEars | public / no-core | revise / description_ready | scripts/clothing/clothing_hats.txt:1435: Clothing/BodyLocation=Hat. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C197 | M017 |
| Base.Hat_GasMask | public / no-core | revise / description_ready | scripts/clothing/clothing_hats.txt:630: Clothing/BodyLocation=MaskEyes. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C200 | M017 |
| Base.Hat_GoldStar | public / no-core | revise / description_ready | scripts/clothing/clothing_hats.txt:1397: Clothing/BodyLocation=Hat. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C197 | M017 |
| Base.Hat_GolfHat | public / no-core | revise / description_ready | scripts/clothing/clothing_hats.txt:645: Clothing/BodyLocation=Hat. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C197 | M017 |
| Base.Hat_GolfHatTINT | public / no-core | revise / description_ready | scripts/clothing/clothing_hats.txt:657: Clothing/BodyLocation=Hat. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C197 | M017 |
| Base.Hat_HardHat | public / no-core | revise / description_ready | scripts/clothing/clothing_hats.txt:669: Clothing/BodyLocation=Hat. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C197 | M017 |
| Base.Hat_HardHat_Miner | public / no-core | revise / description_ready | scripts/clothing/clothing_hats.txt:685: Clothing/BodyLocation=Hat. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C197 | M017 |
| Base.Hat_HockeyHelmet | public / no-core | revise / description_ready | scripts/clothing/clothing_hats.txt:700: Clothing/BodyLocation=Hat. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C197 | M017 |
| Base.Hat_HockeyMask | public / no-core | revise / description_ready | scripts/clothing/clothing_hats.txt:1323: Clothing/BodyLocation=MaskEyes. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C200 | M017 |
| Base.Hat_Jay | public / no-core | revise / description_ready | scripts/clothing/clothing_hats.txt:1423: Clothing/BodyLocation=Hat. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C197 | M017 |
| Base.Hat_JockeyHelmet01 | public / no-core | revise / description_ready | scripts/clothing/clothing_hats.txt:713: Clothing/BodyLocation=Hat. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C197 | M017 |
| Base.Hat_JockeyHelmet02 | public / no-core | revise / description_ready | scripts/clothing/clothing_hats.txt:726: Clothing/BodyLocation=Hat. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C197 | M017 |
| Base.Hat_JockeyHelmet03 | public / no-core | revise / description_ready | scripts/clothing/clothing_hats.txt:739: Clothing/BodyLocation=Hat. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C197 | M017 |
| Base.Hat_JockeyHelmet04 | public / no-core | revise / description_ready | scripts/clothing/clothing_hats.txt:752: Clothing/BodyLocation=Hat. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C197 | M017 |
| Base.Hat_JockeyHelmet05 | public / no-core | revise / description_ready | scripts/clothing/clothing_hats.txt:765: Clothing/BodyLocation=Hat. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C197 | M017 |
| Base.Hat_JockeyHelmet06 | public / no-core | revise / description_ready | scripts/clothing/clothing_hats.txt:778: Clothing/BodyLocation=Hat. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C197 | M017 |
| Base.Hat_JokeArrow | public / no-core | revise / description_ready | scripts/clothing/clothing_hats.txt:1448: Clothing/BodyLocation=Hat. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C197 | M017 |
| Base.Hat_JokeKnife | public / no-core | revise / description_ready | scripts/clothing/clothing_hats.txt:1461: Clothing/BodyLocation=Hat. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C197 | M017 |
| Base.Hat_NBCmask | public / no-core | revise / description_ready | scripts/clothing/clothing_hats.txt:791: Clothing/BodyLocation=FullHat. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C199 | M017 |
| Base.Hat_NewspaperHat | public / no-core | revise / description_ready | scripts/clothing/clothing_hats.txt:1264: Clothing/BodyLocation=Hat. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C197 | M017 |
| Base.Hat_PartyHat_Stars | public / no-core | revise / description_ready | scripts/clothing/clothing_hats.txt:1278: Clothing/BodyLocation=Hat. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C197 | M017 |
| Base.Hat_PartyHat_TINT | public / no-core | revise / description_ready | scripts/clothing/clothing_hats.txt:1293: Clothing/BodyLocation=Hat. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C197 | M017 |
| Base.Hat_PeakedCapArmy | public / no-core | revise / description_ready | scripts/clothing/clothing_hats.txt:1187: Clothing/BodyLocation=Hat. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C197 | M017 |
| Base.Hat_Police | public / no-core | revise / description_ready | scripts/clothing/clothing_hats.txt:809: Clothing/BodyLocation=Hat. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C197 | M017 |
| Base.Hat_Police_Grey | public / no-core | revise / description_ready | scripts/clothing/clothing_hats.txt:821: Clothing/BodyLocation=Hat. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C197 | M017 |
| Base.Hat_Raccoon | public / no-core | revise / description_ready | scripts/clothing/clothing_hats.txt:833: Clothing/BodyLocation=Hat. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C197 | M017 |
| Base.Hat_Ranger | public / core | reduce / description_ready | scripts/clothing/clothing_hats.txt:849의 Clothing/BodyLocation=Hat. 현재 '보호'는 방어 종류/조건을 특정하지 않아 제거 제안; 별도 방어/면역을 추정하지 않는다. | C101 | M116 |
| Base.Hat_RidingHelmet | public / no-core | revise / description_ready | scripts/clothing/clothing_hats.txt:864: Clothing/BodyLocation=Hat. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C197 | M017 |
| Base.Hat_RiotHelmet | public / no-core | revise / description_ready | scripts/clothing/clothing_hats.txt:877: Clothing/BodyLocation=FullHat. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C199 | M017 |
| Base.Hat_SPHhelmet | public / no-core | revise / description_ready | scripts/clothing/clothing_hats.txt:937: Clothing/BodyLocation=FullHat. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C199 | M017 |
| Base.Hat_SantaHat | public / no-core | revise / description_ready | scripts/clothing/clothing_hats.txt:895: Clothing/BodyLocation=Hat. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C197 | M017 |
| Base.Hat_SantaHatGreen | public / no-core | revise / description_ready | scripts/clothing/clothing_hats.txt:910: Clothing/BodyLocation=Hat. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C197 | M017 |
| Base.Hat_ShowerCap | public / no-core | revise / description_ready | scripts/clothing/clothing_hats.txt:925: Clothing/BodyLocation=Hat. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C197 | M017 |
| Base.Hat_Spiffo | public / no-core | revise / description_ready | scripts/clothing/clothing_hats.txt:955: Clothing/BodyLocation=FullHat. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C199 | M017 |
| Base.Hat_SummerHat | public / no-core | revise / description_ready | scripts/clothing/clothing_hats.txt:970: Clothing/BodyLocation=Hat. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C197 | M017 |
| Base.Hat_SurgicalCap_Blue | empty / no-core | revise / description_ready | scripts/clothing/clothing_hats.txt:984: Clothing/BodyLocation=Hat. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C197 | M017 |
| Base.Hat_SurgicalCap_Green | empty / no-core | revise / description_ready | scripts/clothing/clothing_hats.txt:996: Clothing/BodyLocation=Hat. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C197 | M017 |
| Base.Hat_SurgicalMask_Blue | empty / no-core | revise / description_ready | scripts/clothing/clothing_hats.txt:1008: Clothing/BodyLocation=Mask. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C198 | M017 |
| Base.Hat_SurgicalMask_Green | empty / no-core | revise / description_ready | scripts/clothing/clothing_hats.txt:1019: Clothing/BodyLocation=Mask. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C198 | M017 |
| Base.Hat_Sweatband | public / no-core | revise / description_ready | scripts/clothing/clothing_hats.txt:1030: Clothing/BodyLocation=Hat. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C197 | M017 |
| Base.Hat_TinFoilHat | public / no-core | revise / description_ready | scripts/clothing/clothing_hats.txt:1308: Clothing/BodyLocation=Hat. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C197 | M017 |
| Base.Hat_VisorBlack | public / no-core | revise / description_ready | scripts/clothing/clothing_hats.txt:1151: Clothing/BodyLocation=Hat. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C197 | M017 |
| Base.Hat_VisorRed | public / no-core | revise / description_ready | scripts/clothing/clothing_hats.txt:1163: Clothing/BodyLocation=Hat. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C197 | M017 |
| Base.Hat_Visor_WhiteTINT | public / no-core | revise / description_ready | scripts/clothing/clothing_hats.txt:1175: Clothing/BodyLocation=Hat. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C197 | M017 |
| Base.Hat_WeddingVeil | public / no-core | revise / description_ready | scripts/clothing/clothing_hats.txt:1045: Clothing/BodyLocation=Hat. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C197 | M017 |
| Base.Hat_WinterHat | public / no-core | revise / description_ready | scripts/clothing/clothing_hats.txt:1076: Clothing/BodyLocation=Hat. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C197 | M017 |
| Base.Hat_WoolyHat | public / no-core | revise / description_ready | scripts/clothing/clothing_hats.txt:1092: Clothing/BodyLocation=Hat. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C197 | M017 |
| Base.HazmatSuit | public / no-core | revise / description_ready | scripts/clothing/clothing_suits.txt:58: Clothing/BodyLocation=FullSuitHead. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C201 | M017 |
| Base.Headphones | public / core | revise / description_ready | scripts/newitems.txt:996; RWMVolume.lua:79 exact selector; ISRadioAction.lua:147–153 addHeadphones; 분해 입력도 존재. | C084 | M011 |
| Base.HerbalistMag | public / core | revise / description_ready | §학습 문구 87개: 해당 exact SkillTrained 또는 TeachedRecipes/knowledge token의 source를 구분했다. | C026 | M053 |
| Base.HiHis | public / core | revise / description_ready | scripts/items_food.txt:9479의 exact H=-10, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C012 | M012 |
| Base.Hinge | public / core | keep / description_ready | 최근 보호된 Hinge의 문·게이트 제작 용도/기존 source lineage를 유지한다. | C003 | M117 |
| Base.HockeyStick | public / no-core | revise / description_ready | scripts/items_weapons.txt:2046; exact Type=Weapon/damage=0.3–0.7. 연주·경기·배관 수리 같은 현실 기능을 추정하지 않는다. | C021 | M022 |
| Base.HolePuncher | public / core | review_hold / review_required | scripts/newitems.txt:4954; Normal 선언과 문구류 정체성만으로 작성·수정·종이 정리 action을 뒷받침할 수 없음; 이 exact item의 사용 handler/input 관계 필요. 필요한 추가 근거는 이 exact item의 해당 행동/재료 입력 또는 효과를 명시하는 vanilla source 관계이며, current admission 부재를 해소할 승인만으로 대체하지 않음. | C049 | M118 |
| Base.HollyBerry | public / core | revise / description_ready | scripts/items_food.txt:8661의 exact H=-10, T=-1; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C020 | M004 |
| Base.HolsterDouble | public / no-core | revise / description_ready | scripts/clothing/clothing_others.txt:761: Clothing/BodyLocation=BeltExtra. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C202 | M017 |
| Base.HolsterSimple | public / no-core | revise / description_ready | scripts/clothing/clothing_others.txt:748: Clothing/BodyLocation=BeltExtra. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C202 | M017 |
| Base.HomeAlarm | public / core | revise / description_ready | scripts/newitems.txt:130; recipes.txt:2088 Dismantle Home Alarm→MotionSensor; callback 조건. | C102 | M011 |
| Base.Honey | public / core | revise / description_ready | scripts/items_food.txt:5117의 exact H=-20, T=미선언; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C004 | M004 |
| Base.HoodieDOWN_WhiteTINT | public / no-core | revise / description_ready | scripts/clothing/clothing_jacket.txt:492: Clothing/BodyLocation=Sweater. §기본 착용 재판정의 추가 Wear(DownHoodie)→동일 FullType 착용 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C183 | M214 |
| Base.HoodieUP_WhiteTINT | public / core | keep / description_ready | scripts/clothing/clothing_jacket.txt:511의 Clothing/BodyLocation=SweaterHat와 현재 착용 목적 일치. 수치 추가나 감염/위장 효과를 강제하지 않는다. | C018 | M018 |
| Base.HospitalGown | public / no-core | revise / description_ready | scripts/clothing/clothing_suits.txt:363: Clothing/BodyLocation=Dress. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C189 | M017 |
| Base.HotDrink | public / no-core | revise / description_ready | scripts/items_food.txt:2987의 exact H=미선언, T=-20; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C103 | M012 |
| Base.HotDrinkRed | public / no-core | revise / description_ready | scripts/items_food.txt:3007의 exact H=미선언, T=-20; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C103 | M012 |
| Base.HotDrinkSpiffo | public / no-core | revise / description_ready | scripts/items_food.txt:3095의 exact H=미선언, T=-20; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C103 | M012 |
| Base.HotDrinkTea | public / no-core | revise / description_ready | scripts/items_food.txt:2966의 exact H=미선언, T=-20; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C103 | M012 |
| Base.HotDrinkWhite | public / no-core | revise / description_ready | scripts/items_food.txt:3051의 exact H=미선언, T=-20; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C103 | M012 |
| Base.Hotdog | public / core | revise / description_ready | scripts/items_food.txt:2054의 exact H=-20, T=미선언; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C004 | M004 |
| Base.Hotsauce | public / core | revise / description_ready | scripts/items_food.txt:6330의 exact H=-16, T=미선언; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C004 | M004 |
| Base.HottieZ | public / core | revise / description_ready | §후속 item별 판정: exact 읽기 효과 선언 또는 CanBeWrite/페이지·필기구 조건을 구분했다. | C044 | M051 |
| Base.HuntingKnife | public / core | revise / description_ready | scripts/items_weapons.txt:3369; exact Weapon/damage=0.6–1.2, 해당 Attach … to Spear input. 칼/식기·도구의 이름만으로 다른 작동을 추정하지 않음. | C047 | M057 |
| Base.HuntingMag1 | public / core | revise / description_ready | §학습 문구 87개: 해당 exact SkillTrained 또는 TeachedRecipes/knowledge token의 source를 구분했다. | C026 | M053 |
| Base.HuntingMag2 | public / core | revise / description_ready | §학습 문구 87개: 해당 exact SkillTrained 또는 TeachedRecipes/knowledge token의 source를 구분했다. | C026 | M053 |
| Base.HuntingMag3 | public / core | revise / description_ready | §학습 문구 87개: 해당 exact SkillTrained 또는 TeachedRecipes/knowledge token의 source를 구분했다. | C026 | M053 |
| Base.HuntingRifle | public / core | revise / description_ready | scripts/items_weapons.txt:5209 exact ranged Weapon 및 소총 AmmoType. RifleCase와 섞인 current 문구를 분리한다. | C019 | M019 |
| Base.IceHockeyStick | public / no-core | revise / description_ready | scripts/items_weapons.txt:2089; exact Type=Weapon/damage=0.3–0.7. 연주·경기·배관 수리 같은 현실 기능을 추정하지 않는다. | C021 | M022 |
| Base.IcePick | public / core | revise / description_ready | scripts/items_weapons.txt:3470; exact Weapon/damage=0.6–0.9, 해당 Attach … to Spear input. 칼/식기·도구의 이름만으로 다른 작동을 추정하지 않음. | C047 | M057 |
| Base.Icecream | public / core | revise / description_ready | scripts/items_food.txt:3761의 exact H=-30, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C012 | M012 |
| Base.IcecreamMelted | public / core | revise / description_ready | scripts/items_food.txt:3782의 exact H=-30, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C012 | M012 |
| Base.Icing | public / core | revise / description_ready | scripts/items_food.txt:6351의 exact H=-10, T=미선언; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C004 | M004 |
| Base.IronIngot | public / core | review_hold / review_required | scripts/newitems.txt:3885: 단조 recipe input 관계는 있으나 녹이기/두드리기라는 실제 B41 단조 경로의 활성 여부와 조건을 결속하지 못했다. 남은 입력은 정상 B41에서 이 legacy 단조 recipe/Anvil·Blacksmith 기술을 사용할 수 있는 근거 또는 실제 활성 대체 경로다. source successor 미발행이나 기존 core 부재 자체를 보류 사유로 삼지 않음. | C002 | M216 |
| Base.IronSight | public / core | keep / description_ready | scripts/newitems.txt:2446; exact WeaponPart/PartType=Scope/MountOn=HuntingRifle; VarmintRifle; Pistol; Pistol2; Pistol3; Revolver; Revolver_Long; AssaultRifle; AssaultRifle2. 총기 개조 부품이라는 current 목적은 구체적. 실제 성능·조명/총검 공격은 추가하지 않는다. | C014 | M014 |
| Base.Jack | public / core | keep / description_ready | 보호된 Jack의 차량 정비 용도와 source lineage를 유지한다. | C003 | M120 |
| Base.JacketLong_Doctor | public / no-core | revise / description_ready | scripts/clothing/clothing_jacket.txt:96: Clothing/BodyLocation=Jacket. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C203 | M017 |
| Base.JacketLong_Random | public / no-core | revise / description_ready | scripts/clothing/clothing_jacket.txt:134: Clothing/BodyLocation=Jacket. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C203 | M017 |
| Base.JacketLong_Santa | public / no-core | revise / description_ready | scripts/clothing/clothing_jacket.txt:155: Clothing/BodyLocation=Jacket. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C203 | M017 |
| Base.JacketLong_SantaGreen | public / no-core | revise / description_ready | scripts/clothing/clothing_jacket.txt:175: Clothing/BodyLocation=Jacket. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C203 | M017 |
| Base.Jacket_ArmyCamoDesert | public / no-core | revise / description_ready | scripts/clothing/clothing_jacket.txt:195: Clothing/BodyLocation=Jacket. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C203 | M017 |
| Base.Jacket_ArmyCamoGreen | public / no-core | revise / description_ready | scripts/clothing/clothing_jacket.txt:216: Clothing/BodyLocation=Jacket. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C203 | M017 |
| Base.Jacket_Black | public / no-core | revise / description_ready | scripts/clothing/clothing_jacket.txt:237: Clothing/BodyLocation=Jacket. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C203 | M017 |
| Base.Jacket_Chef | public / core | keep / description_ready | scripts/clothing/clothing_jacket.txt:258의 Clothing/BodyLocation=Jacket와 현재 착용 목적 일치. 수치 추가나 감염/위장 효과를 강제하지 않는다. | C018 | M018 |
| Base.Jacket_CoatArmy | public / no-core | revise / description_ready | scripts/clothing/clothing_jacket.txt:115: Clothing/BodyLocation=JacketSuit. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C203 | M017 |
| Base.Jacket_Fireman | public / no-core | revise / description_ready | scripts/clothing/clothing_jacket.txt:276: Clothing/BodyLocation=Jacket. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C203 | M017 |
| Base.Jacket_LeatherBarrelDogs | public / no-core | revise / description_ready | scripts/clothing/clothing_jacket.txt:683: Clothing/BodyLocation=Jacket. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C203 | M017 |
| Base.Jacket_LeatherIronRodent | public / no-core | revise / description_ready | scripts/clothing/clothing_jacket.txt:662: Clothing/BodyLocation=Jacket. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C203 | M017 |
| Base.Jacket_LeatherWildRacoons | public / no-core | revise / description_ready | scripts/clothing/clothing_jacket.txt:641: Clothing/BodyLocation=Jacket. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C203 | M017 |
| Base.Jacket_NavyBlue | public / no-core | revise / description_ready | scripts/clothing/clothing_jacket.txt:618: Clothing/BodyLocation=Jacket. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C203 | M017 |
| Base.Jacket_Padded | public / core | keep / description_ready | scripts/clothing/clothing_jacket.txt:296의 Clothing/BodyLocation=JacketHat_Bulky와 현재 착용 목적 일치. 수치 추가나 감염/위장 효과를 강제하지 않는다. | C018 | M018 |
| Base.Jacket_PaddedDOWN | public / no-core | revise / description_ready | scripts/clothing/clothing_jacket.txt:318: Clothing/BodyLocation=Jacket_Bulky. §기본 착용 재판정의 추가 Wear(DownHoodie)→동일 FullType 착용 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C203 | M214 |
| Base.Jacket_Police | public / no-core | revise / description_ready | scripts/clothing/clothing_jacket.txt:341: Clothing/BodyLocation=Jacket. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C203 | M017 |
| Base.Jacket_Ranger | public / core | keep / description_ready | scripts/clothing/clothing_jacket.txt:362의 Clothing/BodyLocation=Jacket와 현재 착용 목적 일치. 수치 추가나 감염/위장 효과를 강제하지 않는다. | C018 | M018 |
| Base.Jacket_Shellsuit_Black | public / no-core | revise / description_ready | scripts/clothing/clothing_jacket.txt:704: Clothing/BodyLocation=Jacket_Bulky. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C203 | M017 |
| Base.Jacket_Shellsuit_Blue | public / no-core | revise / description_ready | scripts/clothing/clothing_jacket.txt:719: Clothing/BodyLocation=Jacket_Bulky. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C203 | M017 |
| Base.Jacket_Shellsuit_Green | public / no-core | revise / description_ready | scripts/clothing/clothing_jacket.txt:734: Clothing/BodyLocation=Jacket_Bulky. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C203 | M017 |
| Base.Jacket_Shellsuit_Pink | public / no-core | revise / description_ready | scripts/clothing/clothing_jacket.txt:749: Clothing/BodyLocation=Jacket_Bulky. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C203 | M017 |
| Base.Jacket_Shellsuit_TINT | public / no-core | revise / description_ready | scripts/clothing/clothing_jacket.txt:779: Clothing/BodyLocation=Jacket_Bulky. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C203 | M017 |
| Base.Jacket_Shellsuit_Teal | public / no-core | revise / description_ready | scripts/clothing/clothing_jacket.txt:764: Clothing/BodyLocation=Jacket_Bulky. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C203 | M017 |
| Base.Jacket_Varsity | public / no-core | revise / description_ready | scripts/clothing/clothing_jacket.txt:79: Clothing/BodyLocation=Jacket. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C203 | M017 |
| Base.Jacket_WhiteTINT | public / no-core | revise / description_ready | scripts/clothing/clothing_jacket.txt:383: Clothing/BodyLocation=Jacket. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C203 | M017 |
| Base.JacquesBeaver | public / core | review_hold / review_required | scripts/newitems.txt:4800; 장난감의 Normal 정체성/원문 locator 확인; 보기·놀이·수집 action 의 실제 사용 경로는 미확정. 유사 매체의 재생·학습 기능을 전이하지 않음. 필요한 추가 근거는 이 exact item의 해당 행동/재료 입력 또는 효과를 명시하는 vanilla source 관계이며, current admission 부재를 해소할 승인만으로 대체하지 않음. | C015 | M054 |
| Base.JamFruit | public / core | revise / description_ready | scripts/items_food.txt:7339의 exact H=-30, T=미선언; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C004 | M004 |
| Base.JamMarmalade | public / core | revise / description_ready | scripts/items_food.txt:7357의 exact H=-30, T=미선언; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C004 | M004 |
| Base.JamesPic | public / core | review_hold / review_required | scripts/items.txt:161; 사진의 Normal 정체성/원문 locator 확인; 보기·놀이·수집 action 의 실제 사용 경로는 미확정. 유사 매체의 재생·학습 기능을 전이하지 않음. 필요한 추가 근거는 이 exact item의 해당 행동/재료 입력 또는 효과를 명시하는 vanilla source 관계이며, current admission 부재를 해소할 승인만으로 대체하지 않음. | C015 | M050 |
| Base.JarLid | public / core | revise / description_ready | §조리 문구 32개: 이 exact item의 input/result/keep 역할과 원본 recipe를 분리 검토했다. | C026 | M027 |
| Base.JellyBeans | public / core | revise / description_ready | scripts/items_food.txt:9279의 exact H=-5, T=미선언; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C004 | M004 |
| Base.Journal | public / core | revise / description_ready | §후속 item별 판정: exact 읽기 효과 선언 또는 CanBeWrite/페이지·필기구 조건을 구분했다. | C044 | M051 |
| Base.JuiceBox | public / core | revise / description_ready | scripts/items_food.txt:2881; 원문 Food H<0/T<0 및 EvolvedRecipe 선언. §사과의 소비·재료 해석 재사용; 보존/안전/효과량 보장 없음. | C058 | M066 |
| Base.Jujubes | public / core | revise / description_ready | scripts/items_food.txt:9297의 exact H=-5, T=미선언; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C004 | M004 |
| Base.Jumper_DiamondPatternTINT | public / no-core | revise / description_ready | scripts/clothing/clothing_jacket.txt:402: Clothing/BodyLocation=Sweater. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C183 | M017 |
| Base.Jumper_PoloNeck | public / no-core | revise / description_ready | scripts/clothing/clothing_jacket.txt:417: Clothing/BodyLocation=Sweater. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C183 | M017 |
| Base.Jumper_RoundNeck | public / no-core | revise / description_ready | scripts/clothing/clothing_jacket.txt:432: Clothing/BodyLocation=Sweater. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C183 | M017 |
| Base.Jumper_TankTopDiamondTINT | public / no-core | revise / description_ready | scripts/clothing/clothing_jacket.txt:447: Clothing/BodyLocation=Sweater. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C183 | M017 |
| Base.Jumper_TankTopTINT | public / no-core | revise / description_ready | scripts/clothing/clothing_jacket.txt:462: Clothing/BodyLocation=Sweater. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C183 | M017 |
| Base.Jumper_VNeck | public / no-core | revise / description_ready | scripts/clothing/clothing_jacket.txt:477: Clothing/BodyLocation=Sweater. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C183 | M017 |
| Base.Katana | public / no-core | keep / acquisition_only | 각 exact Weapon의 근접 전투 역할이 현재 기본 목적과 일치한다. identity_fallback인 행은 그대로 S2 core로 승격하지 않는다. | C003 | M034 |
| Base.KatePic | public / core | review_hold / review_required | scripts/items.txt:151; 사진의 Normal 정체성/원문 locator 확인; 보기·놀이·수집 action 의 실제 사용 경로는 미확정. 유사 매체의 재생·학습 기능을 전이하지 않음. 필요한 추가 근거는 이 exact item의 해당 행동/재료 입력 또는 효과를 명시하는 vanilla source 관계이며, current admission 부재를 해소할 승인만으로 대체하지 않음. | C015 | M050 |
| Base.Ketchup | public / core | revise / description_ready | scripts/items_food.txt:5302의 exact H=-20, T=미선언; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C004 | M004 |
| Base.Kettle | public / no-core | revise / description_ready | scripts/items.txt:231: CanStoreWater=TRUE, ReplaceOnUseOn=WaterSource-FullKettle. §빈 물 용기와 같은 exact 물 저장/전환 사실을 재사용하며 음용 안전성·현재 내용물은 추정하지 않는다. | C038 | M041 |
| Base.Key1 | public / core | revise / description_ready | scripts/newitems.txt:2862; Type=Key; ISWorldObjectContextMenu.lua:172/567 doorKeyId + haveThisKeyId 조건. 모든 문에 사용 가능하다고 주장하지 않음. | C104 | M064 |
| Base.Key2 | public / core | revise / description_ready | scripts/newitems.txt:2873; Type=Key; ISWorldObjectContextMenu.lua:172/567 doorKeyId + haveThisKeyId 조건. 모든 문에 사용 가능하다고 주장하지 않음. | C104 | M064 |
| Base.Key3 | public / core | revise / description_ready | scripts/newitems.txt:2884; Type=Key; ISWorldObjectContextMenu.lua:172/567 doorKeyId + haveThisKeyId 조건. 모든 문에 사용 가능하다고 주장하지 않음. | C104 | M064 |
| Base.Key4 | public / core | revise / description_ready | scripts/newitems.txt:2895; Type=Key; ISWorldObjectContextMenu.lua:172/567 doorKeyId + haveThisKeyId 조건. 모든 문에 사용 가능하다고 주장하지 않음. | C104 | M064 |
| Base.Key5 | public / core | revise / description_ready | scripts/newitems.txt:2906; Type=Key; ISWorldObjectContextMenu.lua:172/567 doorKeyId + haveThisKeyId 조건. 모든 문에 사용 가능하다고 주장하지 않음. | C104 | M064 |
| Base.KeyPadlock | public / core | revise / description_ready | scripts/newitems.txt:2943; ISPadlockAction.lua:27/35 KeyPadlock 발급·keyId로 자물쇠 제거; world menu:591. | C105 | M064 |
| Base.KeyRing | public / core | revise / description_ready | scripts/newitems.txt:2954; scripts/newitems.txt:2954 Container/Capacity1/OnlyAcceptCategory=Key; inventory menu:321 및 canMoveTo의 isItemAllowed. 일반 가방이 아닌 열쇠 수납으로 범위 확정. | C230 | M224 |
| Base.Keytar | public / no-core | revise / description_ready | scripts/items_weapons.txt:3098; exact Type=Weapon/damage=0.2–0.7. 연주·경기·배관 수리 같은 현실 기능을 추정하지 않는다. | C021 | M022 |
| Base.KitchenKnife | public / core | revise / description_ready | scripts/items_weapons.txt:3895; exact Weapon/damage=0.3–0.7, 해당 Attach … to Spear input. 칼/식기·도구의 이름만으로 다른 작동을 추정하지 않음. | C047 | M057 |
| Base.KitchenTongs | public / core | review_hold / review_required | scripts/newitems.txt:4742; Normal 선언은 확인되나 exact 사용/조리 입력이 미확정; 유사 도구·Teabag2·Flour의 기능 전이 금지. 필요한 추가 근거는 이 exact item의 해당 행동/재료 입력 또는 효과를 명시하는 vanilla source 관계이며, current admission 부재를 해소할 승인만으로 대체하지 않음. | C049 | M069 |
| Base.KnittingNeedles | empty / no-core | review_hold / review_required | scripts/newitems.txt:442 Type=Normal; 뜨개질 recipe/행동 경로가 미결속이다. 같은 이름의 다른 item/현실 용도를 복사하지 않는다. 필요한 추가 근거는 이 exact item의 해당 행동/재료 입력 또는 효과를 명시하는 vanilla source 관계이며, current admission 부재를 해소할 승인만으로 대체하지 않음. | C052 | M122 |
| Base.LaCrosseStick | public / no-core | revise / description_ready | scripts/items_weapons.txt:2132; exact Type=Weapon/damage=0.3–0.7. 연주·경기·배관 수리 같은 현실 기능을 추정하지 않는다. | C021 | M022 |
| Base.Lamp | empty / no-core | review_hold / review_required | scripts/newitems.txt:1986: exact Type=Normal, OBSOLETE=TRUE. 정상 B41에서 이 exact item의 생성·사용 가능성/등록이 미확정이다. 작동하는 별도 FullType으로 대체하거나 기존 no-core 때문에 보류하는 것이 아님. | C052 | M221 |
| Base.Lard | public / core | revise / description_ready | scripts/items_food.txt:9122의 exact H=-24, T=미선언; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C004 | M004 |
| Base.Laser | public / core | keep / description_ready | scripts/newitems.txt:2570; exact WeaponPart/PartType=Canon/MountOn=Pistol; Pistol2; Pistol3; AssaultRifle; AssaultRifle2. 총기 개조 부품이라는 current 목적은 구체적. 실제 성능·조명/총검 공격은 추가하지 않는다. | C014 | M014 |
| Base.LeadPipe | public / no-core | keep / acquisition_only | 각 exact Weapon의 근접 전투 역할이 현재 기본 목적과 일치한다. identity_fallback인 행은 그대로 S2 core로 승격하지 않는다. | C003 | M034 |
| Base.LeafRake | public / no-core | revise / description_ready | scripts/items_weapons.txt:2674; exact Weapon/MinDamage=.2/MaxDamage=.4/SwingAnim=Bat. 기존 긍정 melee source 계약 적용; 재배·갈퀴질 경로가 미확정이어도 기본 근접 공격 역할까지 보류하지 않음. | C231 | M225 |
| Base.Leash | public / core | review_hold / review_required | scripts/newitems.txt:453: §남은 혼합 역할: 반려견에게 매는 actual interaction이 미결속이다. 필요한 추가 근거는 이 exact item의 해당 행동/재료 입력 또는 효과를 명시하는 vanilla source 관계이며, current admission 부재를 해소할 승인만으로 대체하지 않음. | C002 | M125 |
| Base.LeatherStrips | public / core | keep / description_ready | 최근 보호된 LeatherStrips의 의류 수선/패치 용도를 유지한다. | C003 | M126 |
| Base.LeatherStripsDirty | public / core | revise / description_ready | scripts/newitems.txt:4322: exact CanBandage 및 ISApplyBandage:perform의 Dirty type은 bandageLife=0으로 분기. 깨끗한 재료와 같은 지속/치료 효과를 주지 않는다. | C031 | M031 |
| Base.Leek | public / core | revise / description_ready | scripts/items_food.txt:1214의 exact H=-12, T=-5; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C020 | M004 |
| Base.Lemon | public / core | revise / description_ready | scripts/items_food.txt:1237; 원문 Food H<0/T<0 및 EvolvedRecipe 선언. §사과의 소비·재료 해석 재사용; 보존/안전/효과량 보장 없음. | C058 | M066 |
| Base.LemonGrass | public / core | revise / description_ready | scripts/items_food.txt:4075의 exact H=-1, T=미선언; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C004 | M004 |
| Base.Lemongrass | public / core | review_hold / review_required | 이 exact FullType의 원본 item 선언을 결속하지 못했다. Base.LemonGrass와 casing이 다른 별도 key이며 그 source를 복사하지 않는다. 필요한 입력은 해당 exact casing/namespace의 원본 선언 또는 기존 lineage가 인정하는 명시적 identity 귀속이다. 비슷한 이름을 임의 alias로 채택하지 않음. | C108 | M127 |
| Base.LetterOpener | public / core | revise / description_ready | scripts/items_weapons.txt:3519; exact Weapon/damage=0.1–0.1, 해당 Attach … to Spear input. 칼/식기·도구의 이름만으로 다른 작동을 추정하지 않음. | C047 | M057 |
| Base.Lettuce | public / core | revise / description_ready | scripts/items_food.txt:1022의 exact H=-15, T=-7; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C020 | M004 |
| Base.LicoriceBlack | public / core | revise / description_ready | scripts/items_food.txt:7933의 exact H=-2, T=미선언; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C004 | M004 |
| Base.LicoriceRed | public / core | revise / description_ready | scripts/items_food.txt:7950의 exact H=-2, T=미선언; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C004 | M004 |
| Base.LightBulb | public / core | revise / description_ready | §남은 혼합 역할: 해당 exact 조명/무선·매체/운동 source 조건을 분리했다. | C026 | M114 |
| Base.LightBulbBlue | public / no-core | revise / description_ready | §남은 혼합 역할: 해당 exact 조명/무선·매체/운동 source 조건을 분리했다. | C026 | M114 |
| Base.LightBulbCyan | public / no-core | revise / description_ready | §남은 혼합 역할: 해당 exact 조명/무선·매체/운동 source 조건을 분리했다. | C026 | M114 |
| Base.LightBulbGreen | public / core | revise / description_ready | §남은 혼합 역할: 해당 exact 조명/무선·매체/운동 source 조건을 분리했다. | C026 | M114 |
| Base.LightBulbMagenta | public / no-core | revise / description_ready | §남은 혼합 역할: 해당 exact 조명/무선·매체/운동 source 조건을 분리했다. | C026 | M114 |
| Base.LightBulbOrange | public / no-core | revise / description_ready | §남은 혼합 역할: 해당 exact 조명/무선·매체/운동 source 조건을 분리했다. | C026 | M114 |
| Base.LightBulbPink | public / no-core | revise / description_ready | §남은 혼합 역할: 해당 exact 조명/무선·매체/운동 source 조건을 분리했다. | C026 | M114 |
| Base.LightBulbPurple | public / no-core | revise / description_ready | §남은 혼합 역할: 해당 exact 조명/무선·매체/운동 source 조건을 분리했다. | C026 | M114 |
| Base.LightBulbRed | public / no-core | revise / description_ready | §남은 혼합 역할: 해당 exact 조명/무선·매체/운동 source 조건을 분리했다. | C026 | M114 |
| Base.LightBulbYellow | public / no-core | revise / description_ready | §남은 혼합 역할: 해당 exact 조명/무선·매체/운동 source 조건을 분리했다. | C026 | M114 |
| Base.Lighter | public / no-core | revise / description_ready | scripts/items.txt:827: StartFire tag 및 ISCampingMenu:129의 exact 선택→점화 메뉴. CandleLit의 기존 조명 성질과 별개로 불이 켜진 상태를 전제로 하며 임의 연료가 단독 점화된다고 하지 않는다. | C054 | M063 |
| Base.Lime | public / core | revise / description_ready | scripts/items_food.txt:6371; 원문 Food H<0/T<0 및 EvolvedRecipe 선언. §사과의 소비·재료 해석 재사용; 보존/안전/효과량 보장 없음. | C058 | M066 |
| Base.Lipstick | public / core | keep / description_ready | scripts/newitems.txt:1776: exact MakeUpType 또는 Clothing/BodyLocation=; ISMakeUpUI의 category/type 선택·setWornItem 경로가 현재 외형 변경 목적과 일치한다. 위장/인식 감소는 주장하지 않는다. | C109 | M128 |
| Base.Lobster | public / core | revise / description_ready | scripts/items_food.txt:6395의 exact H=-40, T=미선언; EvolvedRecipe 재료 선언 확인; DangerousUncooked=TRUE. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C063 | M004 |
| Base.Locket | empty / no-core | review_hold / review_required | scripts/newitems.txt:1799 Type=Normal; 실제 착용 슬롯/행동 경로가 미결속이다. 같은 이름의 다른 item/현실 용도를 복사하지 않는다. 필요한 추가 근거는 이 exact item의 해당 행동/재료 입력 또는 효과를 명시하는 vanilla source 관계이며, current admission 부재를 해소할 승인만으로 대체하지 않음. | C052 | M129 |
| Base.Log | public / core | revise / description_ready | scripts/items.txt:247; 기존 exact Saw Logs/Saw Logs2 및 Make Campfire Kit input. 손잡이 제작 재료와 섞인 current 문구를 분리. | C110 | M130 |
| Base.LogStacks2 | public / core | revise / description_ready | scripts/newitems.txt:837; recipes:1867–1905의 exact Unstack Logs input/result. 건축 도구와 포장된 재료를 구분. | C111 | M131 |
| Base.LogStacks3 | public / core | revise / description_ready | scripts/newitems.txt:847; recipes:1867–1905의 exact Unstack Logs input/result. 건축 도구와 포장된 재료를 구분. | C111 | M131 |
| Base.LogStacks4 | public / core | revise / description_ready | scripts/newitems.txt:857; recipes:1867–1905의 exact Unstack Logs input/result. 건축 도구와 포장된 재료를 구분. | C111 | M131 |
| Base.Lollipop | public / core | revise / description_ready | scripts/items_food.txt:3943의 exact H=-5, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C012 | M012 |
| Base.LongCoat_Bathrobe | public / no-core | revise / description_ready | scripts/clothing/clothing_suits.txt:17: Clothing/BodyLocation=BathRobe. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C204 | M017 |
| Base.LongJohns | public / no-core | revise / description_ready | scripts/clothing/clothing_suits.txt:3: Clothing/BodyLocation=Torso1Legs1. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C205 | M017 |
| Base.LongJohns_Bottoms | public / no-core | revise / description_ready | scripts/clothing/clothing_pants.txt:3: Clothing/BodyLocation=Legs1. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C206 | M017 |
| Base.LouisvilleMap1 | public / no-core | keep / acquisition_only | scripts/newitems.txt:1103; Map=LouisvilleMap1; ISMap.lua:321 + ISMapDefinitions.lua:257/267–451의 해당 Init. 지역 지도 확인 목적이 구체적이며 유지 가능. | C046 | M055 |
| Base.LouisvilleMap2 | public / no-core | keep / acquisition_only | scripts/newitems.txt:1114; Map=LouisvilleMap2; ISMap.lua:321 + ISMapDefinitions.lua:257/267–451의 해당 Init. 지역 지도 확인 목적이 구체적이며 유지 가능. | C046 | M055 |
| Base.LouisvilleMap3 | public / no-core | keep / acquisition_only | scripts/newitems.txt:1125; Map=LouisvilleMap3; ISMap.lua:321 + ISMapDefinitions.lua:257/267–451의 해당 Init. 지역 지도 확인 목적이 구체적이며 유지 가능. | C046 | M055 |
| Base.LouisvilleMap4 | public / no-core | keep / acquisition_only | scripts/newitems.txt:1136; Map=LouisvilleMap4; ISMap.lua:321 + ISMapDefinitions.lua:257/267–451의 해당 Init. 지역 지도 확인 목적이 구체적이며 유지 가능. | C046 | M055 |
| Base.LouisvilleMap5 | public / no-core | keep / acquisition_only | scripts/newitems.txt:1147; Map=LouisvilleMap5; ISMap.lua:321 + ISMapDefinitions.lua:257/267–451의 해당 Init. 지역 지도 확인 목적이 구체적이며 유지 가능. | C046 | M055 |
| Base.LouisvilleMap6 | public / no-core | keep / acquisition_only | scripts/newitems.txt:1158; Map=LouisvilleMap6; ISMap.lua:321 + ISMapDefinitions.lua:257/267–451의 해당 Init. 지역 지도 확인 목적이 구체적이며 유지 가능. | C046 | M055 |
| Base.LouisvilleMap7 | public / no-core | keep / acquisition_only | scripts/newitems.txt:1169; Map=LouisvilleMap7; ISMap.lua:321 + ISMapDefinitions.lua:257/267–451의 해당 Init. 지역 지도 확인 목적이 구체적이며 유지 가능. | C046 | M055 |
| Base.LouisvilleMap8 | public / no-core | keep / acquisition_only | scripts/newitems.txt:1180; Map=LouisvilleMap8; ISMap.lua:321 + ISMapDefinitions.lua:257/267–451의 해당 Init. 지역 지도 확인 목적이 구체적이며 유지 가능. | C046 | M055 |
| Base.LouisvilleMap9 | public / no-core | keep / acquisition_only | scripts/newitems.txt:1191; Map=LouisvilleMap9; ISMap.lua:321 + ISMapDefinitions.lua:257/267–451의 해당 Init. 지역 지도 확인 목적이 구체적이며 유지 가능. | C046 | M055 |
| Base.LugWrench | public / core | keep / description_ready | 보호된 LugWrench의 타이어 탈착 역할과 source lineage를 유지한다. | C003 | M132 |
| Base.Lunchbag | public / core | keep / description_ready | scripts/items_food.txt:9107의 exact Container/Capacity=5. 보관·운반 역할이 명확하며 이름에 따른 내용물 제한/냉장 효과는 추가하지 않는다. | C023 | M023 |
| Base.Lunchbox | public / core | keep / description_ready | scripts/clothing/clothing_bags.txt:427의 exact Container/Capacity=4. 보관·운반 역할이 명확하며 이름에 따른 내용물 제한/냉장 효과는 추가하지 않는다. | C023 | M023 |
| Base.Lunchbox2 | public / core | keep / description_ready | scripts/clothing/clothing_bags.txt:444의 exact Container/Capacity=4. 보관·운반 역할이 명확하며 이름에 따른 내용물 제한/냉장 효과는 추가하지 않는다. | C023 | M023 |
| Base.M14Clip | public / core | keep / description_ready | 각 exact 탄창 AmmoType과 장전 용도를 대조했다. .308Clip과 M14Clip을 같은 탄창으로 합치지 않는다. | C003 | M003 |
| Base.Macandcheese | public / core | revise / description_ready | scripts/items_food.txt:5101의 exact H=-40, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C012 | M012 |
| Base.Machete | public / core | revise / description_ready | scripts/items_weapons.txt:354; exact Weapon/damage=2–3, 해당 Attach … to Spear input. 칼/식기·도구의 이름만으로 다른 작동을 추정하지 않음. | C047 | M057 |
| Base.Magazine | public / core | revise / description_ready | §후속 item별 판정: exact 읽기 효과 선언 또는 CanBeWrite/페이지·필기구 조건을 구분했다. | C044 | M051 |
| Base.MagazineCrossword1 | public / core | revise / description_ready | §후속 item별 판정: exact 읽기 효과 선언 또는 CanBeWrite/페이지·필기구 조건을 구분했다. | C044 | M051 |
| Base.MagazineCrossword2 | public / core | revise / description_ready | §후속 item별 판정: exact 읽기 효과 선언 또는 CanBeWrite/페이지·필기구 조건을 구분했다. | C044 | M051 |
| Base.MagazineCrossword3 | public / core | revise / description_ready | §후속 item별 판정: exact 읽기 효과 선언 또는 CanBeWrite/페이지·필기구 조건을 구분했다. | C044 | M051 |
| Base.MagazineWordsearch1 | public / core | revise / description_ready | §후속 item별 판정: exact 읽기 효과 선언 또는 CanBeWrite/페이지·필기구 조건을 구분했다. | C044 | M051 |
| Base.MagazineWordsearch2 | public / core | revise / description_ready | §후속 item별 판정: exact 읽기 효과 선언 또는 CanBeWrite/페이지·필기구 조건을 구분했다. | C044 | M051 |
| Base.MagazineWordsearch3 | public / core | revise / description_ready | §후속 item별 판정: exact 읽기 효과 선언 또는 CanBeWrite/페이지·필기구 조건을 구분했다. | C044 | M051 |
| Base.Maggots | public / core | revise / description_ready | scripts/items_food.txt:8847의 exact H=-1, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C012 | M012 |
| Base.Maggots2 | public / core | revise / description_ready | scripts/items_food.txt:8864의 exact H=-1, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음; PoisonPower=3. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C112 | M012 |
| Base.MakeUp_BraveHeart | public / core | keep / description_ready | scripts/clothing/clothing_others.txt:560: exact MakeUpType 또는 Clothing/BodyLocation=MakeUp_FullFace; ISMakeUpUI의 category/type 선택·setWornItem 경로가 현재 외형 변경 목적과 일치한다. 위장/인식 감소는 주장하지 않는다. | C109 | M128 |
| Base.MakeUp_CamoEyes1 | public / core | keep / description_ready | scripts/clothing/clothing_others.txt:616: exact MakeUpType 또는 Clothing/BodyLocation=MakeUp_Eyes; ISMakeUpUI의 category/type 선택·setWornItem 경로가 현재 외형 변경 목적과 일치한다. 위장/인식 감소는 주장하지 않는다. | C109 | M128 |
| Base.MakeUp_CamoEyes2 | public / core | keep / description_ready | scripts/clothing/clothing_others.txt:623: exact MakeUpType 또는 Clothing/BodyLocation=MakeUp_Eyes; ISMakeUpUI의 category/type 선택·setWornItem 경로가 현재 외형 변경 목적과 일치한다. 위장/인식 감소는 주장하지 않는다. | C109 | M128 |
| Base.MakeUp_CamoFullFace1 | public / core | keep / description_ready | scripts/clothing/clothing_others.txt:546: exact MakeUpType 또는 Clothing/BodyLocation=MakeUp_FullFace; ISMakeUpUI의 category/type 선택·setWornItem 경로가 현재 외형 변경 목적과 일치한다. 위장/인식 감소는 주장하지 않는다. | C109 | M128 |
| Base.MakeUp_CamoFullFace2 | public / core | keep / description_ready | scripts/clothing/clothing_others.txt:553: exact MakeUpType 또는 Clothing/BodyLocation=MakeUp_FullFace; ISMakeUpUI의 category/type 선택·setWornItem 경로가 현재 외형 변경 목적과 일치한다. 위장/인식 감소는 주장하지 않는다. | C109 | M128 |
| Base.MakeUp_CamoStripes | public / core | keep / description_ready | scripts/clothing/clothing_others.txt:630: exact MakeUpType 또는 Clothing/BodyLocation=MakeUp_Eyes; ISMakeUpUI의 category/type 선택·setWornItem 경로가 현재 외형 변경 목적과 일치한다. 위장/인식 감소는 주장하지 않는다. | C109 | M128 |
| Base.MakeUp_ClownFace1 | public / core | keep / description_ready | scripts/clothing/clothing_others.txt:567: exact MakeUpType 또는 Clothing/BodyLocation=MakeUp_FullFace; ISMakeUpUI의 category/type 선택·setWornItem 경로가 현재 외형 변경 목적과 일치한다. 위장/인식 감소는 주장하지 않는다. | C109 | M128 |
| Base.MakeUp_ClownFace2 | public / core | keep / description_ready | scripts/clothing/clothing_others.txt:574: exact MakeUpType 또는 Clothing/BodyLocation=MakeUp_FullFace; ISMakeUpUI의 category/type 선택·setWornItem 경로가 현재 외형 변경 목적과 일치한다. 위장/인식 감소는 주장하지 않는다. | C109 | M128 |
| Base.MakeUp_Crow | public / core | keep / description_ready | scripts/clothing/clothing_others.txt:595: exact MakeUpType 또는 Clothing/BodyLocation=MakeUp_Eyes; ISMakeUpUI의 category/type 선택·setWornItem 경로가 현재 외형 변경 목적과 일치한다. 위장/인식 감소는 주장하지 않는다. | C109 | M128 |
| Base.MakeUp_EyesShadowBlue | public / core | keep / description_ready | scripts/clothing/clothing_others.txt:658: exact MakeUpType 또는 Clothing/BodyLocation=MakeUp_EyesShadow; ISMakeUpUI의 category/type 선택·setWornItem 경로가 현재 외형 변경 목적과 일치한다. 위장/인식 감소는 주장하지 않는다. | C109 | M128 |
| Base.MakeUp_EyesShadowGreen | public / core | keep / description_ready | scripts/clothing/clothing_others.txt:679: exact MakeUpType 또는 Clothing/BodyLocation=MakeUp_EyesShadow; ISMakeUpUI의 category/type 선택·setWornItem 경로가 현재 외형 변경 목적과 일치한다. 위장/인식 감소는 주장하지 않는다. | C109 | M128 |
| Base.MakeUp_EyesShadowLightBlue | public / core | keep / description_ready | scripts/clothing/clothing_others.txt:651: exact MakeUpType 또는 Clothing/BodyLocation=MakeUp_EyesShadow; ISMakeUpUI의 category/type 선택·setWornItem 경로가 현재 외형 변경 목적과 일치한다. 위장/인식 감소는 주장하지 않는다. | C109 | M128 |
| Base.MakeUp_EyesShadowPink | public / core | keep / description_ready | scripts/clothing/clothing_others.txt:672: exact MakeUpType 또는 Clothing/BodyLocation=MakeUp_EyesShadow; ISMakeUpUI의 category/type 선택·setWornItem 경로가 현재 외형 변경 목적과 일치한다. 위장/인식 감소는 주장하지 않는다. | C109 | M128 |
| Base.MakeUp_EyesShadowRed | public / core | keep / description_ready | scripts/clothing/clothing_others.txt:665: exact MakeUpType 또는 Clothing/BodyLocation=MakeUp_EyesShadow; ISMakeUpUI의 category/type 선택·setWornItem 경로가 현재 외형 변경 목적과 일치한다. 위장/인식 감소는 주장하지 않는다. | C109 | M128 |
| Base.MakeUp_EyesShadowWhite | public / core | keep / description_ready | scripts/clothing/clothing_others.txt:644: exact MakeUpType 또는 Clothing/BodyLocation=MakeUp_EyesShadow; ISMakeUpUI의 category/type 선택·setWornItem 경로가 현재 외형 변경 목적과 일치한다. 위장/인식 감소는 주장하지 않는다. | C109 | M128 |
| Base.MakeUp_EyesShadowYellow | public / core | keep / description_ready | scripts/clothing/clothing_others.txt:686: exact MakeUpType 또는 Clothing/BodyLocation=MakeUp_EyesShadow; ISMakeUpUI의 category/type 선택·setWornItem 경로가 현재 외형 변경 목적과 일치한다. 위장/인식 감소는 주장하지 않는다. | C109 | M128 |
| Base.MakeUp_Football | public / core | keep / description_ready | scripts/clothing/clothing_others.txt:637: exact MakeUpType 또는 Clothing/BodyLocation=MakeUp_Eyes; ISMakeUpUI의 category/type 선택·setWornItem 경로가 현재 외형 변경 목적과 일치한다. 위장/인식 감소는 주장하지 않는다. | C109 | M128 |
| Base.MakeUp_GreenCamo | public / core | keep / description_ready | scripts/clothing/clothing_others.txt:537: exact MakeUpType 또는 Clothing/BodyLocation=MakeUp_FullFace; ISMakeUpUI의 category/type 선택·setWornItem 경로가 현재 외형 변경 목적과 일치한다. 위장/인식 감소는 주장하지 않는다. | C109 | M128 |
| Base.MakeUp_LipsBlack | public / core | keep / description_ready | scripts/clothing/clothing_others.txt:714: exact MakeUpType 또는 Clothing/BodyLocation=MakeUp_Lips; ISMakeUpUI의 category/type 선택·setWornItem 경로가 현재 외형 변경 목적과 일치한다. 위장/인식 감소는 주장하지 않는다. | C109 | M128 |
| Base.MakeUp_LipsBlue | public / core | keep / description_ready | scripts/clothing/clothing_others.txt:707: exact MakeUpType 또는 Clothing/BodyLocation=MakeUp_Lips; ISMakeUpUI의 category/type 선택·setWornItem 경로가 현재 외형 변경 목적과 일치한다. 위장/인식 감소는 주장하지 않는다. | C109 | M128 |
| Base.MakeUp_LipsGreen | public / core | keep / description_ready | scripts/clothing/clothing_others.txt:721: exact MakeUpType 또는 Clothing/BodyLocation=MakeUp_Lips; ISMakeUpUI의 category/type 선택·setWornItem 경로가 현재 외형 변경 목적과 일치한다. 위장/인식 감소는 주장하지 않는다. | C109 | M128 |
| Base.MakeUp_LipsLightBlue | public / core | keep / description_ready | scripts/clothing/clothing_others.txt:700: exact MakeUpType 또는 Clothing/BodyLocation=MakeUp_Lips; ISMakeUpUI의 category/type 선택·setWornItem 경로가 현재 외형 변경 목적과 일치한다. 위장/인식 감소는 주장하지 않는다. | C109 | M128 |
| Base.MakeUp_LipsPink | public / core | keep / description_ready | scripts/clothing/clothing_others.txt:728: exact MakeUpType 또는 Clothing/BodyLocation=MakeUp_Lips; ISMakeUpUI의 category/type 선택·setWornItem 경로가 현재 외형 변경 목적과 일치한다. 위장/인식 감소는 주장하지 않는다. | C109 | M128 |
| Base.MakeUp_LipsRed | public / core | keep / description_ready | scripts/clothing/clothing_others.txt:693: exact MakeUpType 또는 Clothing/BodyLocation=MakeUp_Lips; ISMakeUpUI의 category/type 선택·setWornItem 경로가 현재 외형 변경 목적과 일치한다. 위장/인식 감소는 주장하지 않는다. | C109 | M128 |
| Base.MakeUp_RedStripes1 | public / core | keep / description_ready | scripts/clothing/clothing_others.txt:602: exact MakeUpType 또는 Clothing/BodyLocation=MakeUp_Eyes; ISMakeUpUI의 category/type 선택·setWornItem 경로가 현재 외형 변경 목적과 일치한다. 위장/인식 감소는 주장하지 않는다. | C109 | M128 |
| Base.MakeUp_RedStripes2 | public / core | keep / description_ready | scripts/clothing/clothing_others.txt:609: exact MakeUpType 또는 Clothing/BodyLocation=MakeUp_Eyes; ISMakeUpUI의 category/type 선택·setWornItem 경로가 현재 외형 변경 목적과 일치한다. 위장/인식 감소는 주장하지 않는다. | C109 | M128 |
| Base.MakeUp_SkullFace1 | public / core | keep / description_ready | scripts/clothing/clothing_others.txt:581: exact MakeUpType 또는 Clothing/BodyLocation=MakeUp_FullFace; ISMakeUpUI의 category/type 선택·setWornItem 경로가 현재 외형 변경 목적과 일치한다. 위장/인식 감소는 주장하지 않는다. | C109 | M128 |
| Base.MakeUp_SkullFace2 | public / core | keep / description_ready | scripts/clothing/clothing_others.txt:588: exact MakeUpType 또는 Clothing/BodyLocation=MakeUp_FullFace; ISMakeUpUI의 category/type 선택·setWornItem 경로가 현재 외형 변경 목적과 일치한다. 위장/인식 감소는 주장하지 않는다. | C109 | M128 |
| Base.MakeupEyeshadow | public / core | keep / description_ready | scripts/newitems.txt:583: exact MakeUpType 또는 Clothing/BodyLocation=; ISMakeUpUI의 category/type 선택·setWornItem 경로가 현재 외형 변경 목적과 일치한다. 위장/인식 감소는 주장하지 않는다. | C109 | M128 |
| Base.MakeupFoundation | public / core | keep / description_ready | scripts/newitems.txt:594: exact MakeUpType 또는 Clothing/BodyLocation=; ISMakeUpUI의 category/type 선택·setWornItem 경로가 현재 외형 변경 목적과 일치한다. 위장/인식 감소는 주장하지 않는다. | C109 | M128 |
| Base.Maki | public / core | revise / description_ready | scripts/items_food.txt:6420의 exact H=-8, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C012 | M012 |
| Base.Male_Undies | public / no-core | review_hold / review_required | scripts/clothing/clothing_shoes.txt:33: exact Type=Clothing, OBSOLETE=TRUE. 정상 B41에서 이 exact item의 생성·사용 가능성/등록이 미확정이다. 작동하는 별도 FullType으로 대체하거나 기존 no-core 때문에 보류하는 것이 아님. | C207 | M221 |
| Base.Mango | public / core | revise / description_ready | scripts/items_food.txt:7805의 exact H=-20, T=-13; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C020 | M004 |
| Base.Map | public / core | review_hold / review_required | scripts/newitems.txt:1093; Type=Map이나 Map ID 미선언; ISMapDefinitions.lua:257의 Init dispatch에 필요한 runtime mapID/데이터 귀속 미확인. 필요한 입력은 실제 인스턴스의 MapID를 부여하는 producer와 대응 Init/지도 데이터의 귀속. | C015 | M133 |
| Base.MapleSyrup | public / core | revise / description_ready | scripts/items_food.txt:6437의 exact H=-45, T=미선언; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C004 | M004 |
| Base.MarchRidgeMap | public / no-core | keep / acquisition_only | scripts/newitems.txt:1202; Map=MarchRidgeMap; ISMap.lua:321 + ISMapDefinitions.lua:257/267–451의 해당 Init. 지역 지도 확인 목적이 구체적이며 유지 가능. | C046 | M055 |
| Base.Margarine | public / core | revise / description_ready | scripts/items_food.txt:9143의 exact H=-24, T=미선언; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C004 | M004 |
| Base.MariannePic | public / core | review_hold / review_required | scripts/items.txt:181; 사진의 Normal 정체성/원문 locator 확인; 보기·놀이·수집 action 의 실제 사용 경로는 미확정. 유사 매체의 재생·학습 기능을 전이하지 않음. 필요한 추가 근거는 이 exact item의 해당 행동/재료 입력 또는 효과를 명시하는 vanilla source 관계이며, current admission 부재를 해소할 승인만으로 대체하지 않음. | C015 | M050 |
| Base.Marinara | public / core | revise / description_ready | scripts/items_food.txt:5323의 exact H=-10, T=미선언; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C004 | M004 |
| Base.Marshmallows | public / core | revise / description_ready | scripts/items_food.txt:7375의 exact H=-5, T=미선언; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C004 | M004 |
| Base.Matches | public / no-core | revise / description_ready | scripts/items.txt:847: StartFire tag 및 ISCampingMenu:129의 exact 선택→점화 메뉴. CandleLit의 기존 조명 성질과 별개로 불이 켜진 상태를 전제로 하며 임의 연료가 단독 점화된다고 하지 않는다. | C054 | M063 |
| Base.Mattress | public / core | revise / description_ready | scripts/newitems.txt:944; ISBuildMenu.lua:1358–1374 침대 제작 exact mattress requirement, :1415 onBed need:Base.Mattress=1. sprite placement 미확정과 별개인 source-bound 제작 재료 역할. | C232 | M226 |
| Base.MeatCleaver | public / core | revise / description_ready | scripts/items_weapons.txt:224; Weapon min .4 max .8; Slice·Butcher keep 입력. 강도/효율 수치 주장 없음. | C114 | M026 |
| Base.MeatDumpling | public / core | revise / description_ready | scripts/items_food.txt:6458의 exact H=-10, T=미선언; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C004 | M004 |
| Base.MeatPatty | public / core | revise / description_ready | scripts/items_food.txt:2228의 exact H=-40, T=미선언; EvolvedRecipe 재료 선언 확인; DangerousUncooked=TRUE. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C063 | M004 |
| Base.MeatSteamBun | public / core | revise / description_ready | scripts/items_food.txt:6477의 exact H=-15, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C012 | M012 |
| Base.MechanicMag1 | public / core | revise / description_ready | §학습 문구 87개: 해당 exact SkillTrained 또는 TeachedRecipes/knowledge token의 source를 구분했다. | C026 | M053 |
| Base.MechanicMag2 | public / core | revise / description_ready | §학습 문구 87개: 해당 exact SkillTrained 또는 TeachedRecipes/knowledge token의 source를 구분했다. | C026 | M053 |
| Base.MechanicMag3 | public / core | revise / description_ready | §학습 문구 87개: 해당 exact SkillTrained 또는 TeachedRecipes/knowledge token의 source를 구분했다. | C026 | M053 |
| Base.MetalBar | public / core | revise / description_ready | scripts/items_weapons.txt:138; ISWorldObjectContextMenu:1018의 exact MetalBar 및 용접 조건. legacy 주조 recipe만으로 기본 용도를 제한하지 않는다. | C115 | M135 |
| Base.MetalDrum | public / core | review_hold / review_required | ISBlacksmithMenu:101/110은 Base.MetalDrum을 조회하지만 disableFurnaceAnvil=true인 건설 블록이다. onMetalDrum:817의 need:Base.MetalDrum 소비도 주석 처리됨. 기존 world drum의 물/숯 기능만으로 재고 item의 실제 설치 입력을 확정하지 못함. | C116 | M216 |
| Base.MetalPipe | public / core | keep / description_ready | MetalPipe의 Make Pipe bomb/Make Metal Bar input이 금속 제작 재료 역할을 뒷받침한다. | C003 | M137 |
| Base.MetalworkMag1 | public / core | revise / description_ready | §학습 문구 87개: 해당 exact SkillTrained 또는 TeachedRecipes/knowledge token의 source를 구분했다. | C026 | M053 |
| Base.MetalworkMag2 | public / core | revise / description_ready | §학습 문구 87개: 해당 exact SkillTrained 또는 TeachedRecipes/knowledge token의 source를 구분했다. | C026 | M053 |
| Base.MetalworkMag3 | public / core | revise / description_ready | §학습 문구 87개: 해당 exact SkillTrained 또는 TeachedRecipes/knowledge token의 source를 구분했다. | C026 | M053 |
| Base.MetalworkMag4 | public / core | revise / description_ready | §학습 문구 87개: 해당 exact SkillTrained 또는 TeachedRecipes/knowledge token의 source를 구분했다. | C026 | M053 |
| Base.Milk | public / core | revise / description_ready | scripts/items_food.txt:2784; 원문 Food H<0/T<0 및 EvolvedRecipe 선언. §사과의 소비·재료 해석 재사용; 보존/안전/효과량 보장 없음. | C058 | M066 |
| Base.Millipede | public / core | revise / description_ready | scripts/items_food.txt:8885의 exact H=-5, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음; DangerousUncooked=TRUE. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C032 | M012 |
| Base.Millipede2 | public / core | revise / description_ready | scripts/items_food.txt:8906의 exact H=-5, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음; DangerousUncooked=TRUE. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C032 | M012 |
| Base.MincedMeat | public / core | revise / description_ready | scripts/items_food.txt:6494의 exact H=-40, T=미선언; EvolvedRecipe 재료 선언 확인; DangerousUncooked=TRUE. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C063 | M004 |
| Base.MintCandy | public / core | revise / description_ready | scripts/items_food.txt:3927의 exact H=-2, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C012 | M012 |
| Base.Mirror | public / core | revise / description_ready | scripts/newitems.txt:1810: ISInventoryPaneContextMenu:3593 이후 exact Mirror 소지로 화장 조건을 충족한다. World mirror/vehicle/Foundation 대안도 있어 항상 필수라고 하지 않는다. | C117 | M138 |
| Base.MixedVegetables | public / core | revise / description_ready | scripts/items_food.txt:9374의 exact H=-20, T=-5; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C020 | M004 |
| Base.ModernBrake1 | public / core | revise / description_ready | scripts/vehicles/vehiclesitems.txt:268; template_brake 및 exact brakeForce 선언. 현재 일반 구동 복구 문구를 제동 역할로 특정 | C118 | M139 |
| Base.ModernBrake2 | public / core | revise / description_ready | scripts/vehicles/vehiclesitems.txt:316; template_brake 및 exact brakeForce 선언. 현재 일반 구동 복구 문구를 제동 역할로 특정 | C118 | M140 |
| Base.ModernBrake3 | public / core | revise / description_ready | scripts/vehicles/vehiclesitems.txt:364; template_brake 및 exact brakeForce 선언. 현재 일반 구동 복구 문구를 제동 역할로 특정 | C118 | M141 |
| Base.ModernCarMuffler1 | public / core | revise / description_ready | scripts/vehicles/vehiclesitems.txt:1390; template_muffler 및 exact EngineLoudness 선언. 모든 형식이 같은 양만큼 소음을 줄인다고 하지 않음 | C119 | M139 |
| Base.ModernCarMuffler2 | public / core | revise / description_ready | scripts/vehicles/vehiclesitems.txt:1438; template_muffler 및 exact EngineLoudness 선언. 모든 형식이 같은 양만큼 소음을 줄인다고 하지 않음 | C119 | M140 |
| Base.ModernCarMuffler3 | public / core | revise / description_ready | scripts/vehicles/vehiclesitems.txt:1486; template_muffler 및 exact EngineLoudness 선언. 모든 형식이 같은 양만큼 소음을 줄인다고 하지 않음 | C119 | M141 |
| Base.ModernSuspension1 | public / core | revise / description_ready | scripts/vehicles/vehiclesitems.txt:400; template_suspension 및 SuspensionDamping/Compression, Vehicles.Update.Suspension. 엔진/구동 복구 보장을 제거하고 교체 부위를 특정 | C120 | M139 |
| Base.ModernSuspension2 | public / core | revise / description_ready | scripts/vehicles/vehiclesitems.txt:436; template_suspension 및 SuspensionDamping/Compression, Vehicles.Update.Suspension. 엔진/구동 복구 보장을 제거하고 교체 부위를 특정 | C120 | M140 |
| Base.ModernSuspension3 | public / core | revise / description_ready | scripts/vehicles/vehiclesitems.txt:472; template_suspension 및 SuspensionDamping/Compression, Vehicles.Update.Suspension. 엔진/구동 복구 보장을 제거하고 교체 부위를 특정 | C120 | M141 |
| Base.ModernTire1 | public / core | revise / description_ready | scripts/vehicles/vehiclesitems.txt:110; template_tire 및 exact WheelFriction, Vehicles.Update.Tire의 공기/상태 분기. 정상 주행이나 고정 성능을 보장하지 않음 | C121 | M139 |
| Base.ModernTire2 | public / core | revise / description_ready | scripts/vehicles/vehiclesitems.txt:164; template_tire 및 exact WheelFriction, Vehicles.Update.Tire의 공기/상태 분기. 정상 주행이나 고정 성능을 보장하지 않음 | C121 | M140 |
| Base.ModernTire3 | public / core | revise / description_ready | scripts/vehicles/vehiclesitems.txt:218; template_tire 및 exact WheelFriction, Vehicles.Update.Tire의 공기/상태 분기. 정상 주행이나 고정 성능을 보장하지 않음 | C121 | M141 |
| Base.Modjeska | public / core | revise / description_ready | scripts/items_food.txt:5454의 exact H=-10, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C012 | M012 |
| Base.MoleyMole | public / core | review_hold / review_required | scripts/newitems.txt:4827; 장난감의 Normal 정체성/원문 locator 확인; 보기·놀이·수집 action 의 실제 사용 경로는 미확정. 유사 매체의 재생·학습 기능을 전이하지 않음. 필요한 추가 근거는 이 exact item의 해당 행동/재료 입력 또는 효과를 명시하는 vanilla source 관계이며, current admission 부재를 해소할 승인만으로 대체하지 않음. | C015 | M054 |
| Base.Molotov | public / no-core | revise / description_ready | scripts/items_weapons.txt:6264의 exact FirePower=90. 원격/센서/타이머는 각 선언대로 별도 조건이며 모든 장치를 같은 투척/폭발 효과로 묶지 않는다. Java 내부·PZ 실제 효과는 미관찰. | C090 | M005 |
| Base.MonarchCaterpillar | public / core | revise / description_ready | scripts/items_food.txt:8927의 exact H=-5, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C012 | M012 |
| Base.Money | public / core | revise / description_ready | scripts/newitems.txt:5; lua/server/Camping/camping_fuel.lua의 exact Money 키가 연료/점화 재료에 모두 등록됨. 앞 절 ISCampingMenu의 유효 연료/점화 선택과 보충·점화 경로 재사용. 청소·게임·결제 등의 미확인 기능과 분리. | C227 | M220 |
| Base.Mop | public / core | revise / description_ready | §후속 item별 판정: exact blood cleaning 도구 선택 | C122 | M142 |
| Base.MortarPestle | public / core | revise / description_ready | scripts/newitems.txt:2015; Tags=MortarPestle; recipes.txt:1194–1225 keep selector 약초 찜질제 제작. | C123 | M026 |
| Base.MotionSensor | public / core | revise / description_ready | scripts/newitems.txt:140; recipes.txt Add Motion Sensor V1/V2/V3 exact input. | C124 | M011 |
| Base.Mov_AirConditioner | public / core | review_hold / review_required | scripts/newMoveables.txt:1063: Type=Moveable, WorldObjectSprite=industry_01_4. InvContextMovable/ISMoveableCursor→ISMoveableSpriteProps.new는 getWorldSprite의 실제 IsMoveAble·MoveType·배치/도구 속성을 요구한다. 이 sprite의 B41 속성 입력이 미확정이라 기본 배치/설비 기능을 확정하지 못함; 기존 admission 유무 때문이 아님. | C113 | M227 |
| Base.Mov_AntiqueStove | public / core | review_hold / review_required | scripts/newitems.txt:4368: Type=Moveable, WorldObjectSprite=appliances_cooking_01_16. InvContextMovable/ISMoveableCursor→ISMoveableSpriteProps.new는 getWorldSprite의 실제 IsMoveAble·MoveType·배치/도구 속성을 요구한다. 이 sprite의 B41 속성 입력이 미확정이라 기본 배치/설비 기능을 확정하지 못함; 기존 admission 유무 때문이 아님. | C113 | M227 |
| Base.Mov_ArcadeMachine1 | public / core | review_hold / review_required | scripts/newMoveables.txt:653: Type=Moveable, WorldObjectSprite=recreational_01_16. InvContextMovable/ISMoveableCursor→ISMoveableSpriteProps.new는 getWorldSprite의 실제 IsMoveAble·MoveType·배치/도구 속성을 요구한다. 이 sprite의 B41 속성 입력이 미확정이라 기본 배치/설비 기능을 확정하지 못함; 기존 admission 유무 때문이 아님. | C113 | M227 |
| Base.Mov_ArcadeMachine2 | public / core | review_hold / review_required | scripts/newMoveables.txt:663: Type=Moveable, WorldObjectSprite=recreational_01_20. InvContextMovable/ISMoveableCursor→ISMoveableSpriteProps.new는 getWorldSprite의 실제 IsMoveAble·MoveType·배치/도구 속성을 요구한다. 이 sprite의 B41 속성 입력이 미확정이라 기본 배치/설비 기능을 확정하지 못함; 기존 admission 유무 때문이 아님. | C113 | M227 |
| Base.Mov_BeachChair | public / core | review_hold / review_required | scripts/newMoveables.txt:1073: Type=Moveable, WorldObjectSprite=furniture_seating_outdoor_01_25. InvContextMovable/ISMoveableCursor→ISMoveableSpriteProps.new는 getWorldSprite의 실제 IsMoveAble·MoveType·배치/도구 속성을 요구한다. 이 sprite의 B41 속성 입력이 미확정이라 기본 배치/설비 기능을 확정하지 못함; 기존 admission 유무 때문이 아님. | C113 | M227 |
| Base.Mov_BinRound | public / core | review_hold / review_required | scripts/newMoveables.txt:1153: Type=Moveable, WorldObjectSprite=trashcontainers_01_20. InvContextMovable/ISMoveableCursor→ISMoveableSpriteProps.new는 getWorldSprite의 실제 IsMoveAble·MoveType·배치/도구 속성을 요구한다. 이 sprite의 B41 속성 입력이 미확정이라 기본 배치/설비 기능을 확정하지 못함; 기존 admission 유무 때문이 아님. | C113 | M227 |
| Base.Mov_Birdbath | public / core | review_hold / review_required | scripts/newMoveables.txt:1163: Type=Moveable, WorldObjectSprite=vegetation_ornamental_01_50. InvContextMovable/ISMoveableCursor→ISMoveableSpriteProps.new는 getWorldSprite의 실제 IsMoveAble·MoveType·배치/도구 속성을 요구한다. 이 sprite의 B41 속성 입력이 미확정이라 기본 배치/설비 기능을 확정하지 못함; 기존 admission 유무 때문이 아님. | C113 | M227 |
| Base.Mov_BlueComfyChair | public / core | review_hold / review_required | scripts/newMoveables.txt:323: Type=Moveable, WorldObjectSprite=furniture_seating_indoor_03_25. InvContextMovable/ISMoveableCursor→ISMoveableSpriteProps.new는 getWorldSprite의 실제 IsMoveAble·MoveType·배치/도구 속성을 요구한다. 이 sprite의 B41 속성 입력이 미확정이라 기본 배치/설비 기능을 확정하지 못함; 기존 admission 유무 때문이 아님. | C113 | M227 |
| Base.Mov_BluePlasticChair | public / core | review_hold / review_required | scripts/newMoveables.txt:53: Type=Moveable, WorldObjectSprite=furniture_seating_indoor_02_13. InvContextMovable/ISMoveableCursor→ISMoveableSpriteProps.new는 getWorldSprite의 실제 IsMoveAble·MoveType·배치/도구 속성을 요구한다. 이 sprite의 B41 속성 입력이 미확정이라 기본 배치/설비 기능을 확정하지 못함; 기존 admission 유무 때문이 아님. | C113 | M227 |
| Base.Mov_BlueRattanChair | public / core | review_hold / review_required | scripts/newMoveables.txt:383: Type=Moveable, WorldObjectSprite=furniture_seating_indoor_02_41. InvContextMovable/ISMoveableCursor→ISMoveableSpriteProps.new는 getWorldSprite의 실제 IsMoveAble·MoveType·배치/도구 속성을 요구한다. 이 sprite의 B41 속성 입력이 미확정이라 기본 배치/설비 기능을 확정하지 못함; 기존 admission 유무 때문이 아님. | C113 | M227 |
| Base.Mov_BrownComfyChair | public / core | review_hold / review_required | scripts/newMoveables.txt:343: Type=Moveable, WorldObjectSprite=furniture_seating_indoor_02_44. InvContextMovable/ISMoveableCursor→ISMoveableSpriteProps.new는 getWorldSprite의 실제 IsMoveAble·MoveType·배치/도구 속성을 요구한다. 이 sprite의 B41 속성 입력이 미확정이라 기본 배치/설비 기능을 확정하지 못함; 기존 admission 유무 때문이 아님. | C113 | M227 |
| Base.Mov_BrownLowTable | public / core | review_hold / review_required | scripts/newMoveables.txt:463: Type=Moveable, WorldObjectSprite=furniture_tables_low_01_13. InvContextMovable/ISMoveableCursor→ISMoveableSpriteProps.new는 getWorldSprite의 실제 IsMoveAble·MoveType·배치/도구 속성을 요구한다. 이 sprite의 B41 속성 입력이 미확정이라 기본 배치/설비 기능을 확정하지 못함; 기존 admission 유무 때문이 아님. | C113 | M227 |
| Base.Mov_CabinetMedical | public / core | review_hold / review_required | scripts/newMoveables.txt:1033: Type=Moveable, WorldObjectSprite=fixtures_bathroom_01_28. InvContextMovable/ISMoveableCursor→ISMoveableSpriteProps.new는 getWorldSprite의 실제 IsMoveAble·MoveType·배치/도구 속성을 요구한다. 이 sprite의 B41 속성 입력이 미확정이라 기본 배치/설비 기능을 확정하지 못함; 기존 admission 유무 때문이 아님. | C113 | M227 |
| Base.Mov_CabinetTool | public / core | review_hold / review_required | scripts/newMoveables.txt:593: Type=Moveable, WorldObjectSprite=location_business_machinery_01_32. InvContextMovable/ISMoveableCursor→ISMoveableSpriteProps.new는 getWorldSprite의 실제 IsMoveAble·MoveType·배치/도구 속성을 요구한다. 이 sprite의 B41 속성 입력이 미확정이라 기본 배치/설비 기능을 확정하지 못함; 기존 admission 유무 때문이 아님. | C113 | M227 |
| Base.Mov_CardboardBox | public / core | review_hold / review_required | scripts/newMoveables.txt:513: Type=Moveable, WorldObjectSprite=trashcontainers_01_24. InvContextMovable/ISMoveableCursor→ISMoveableSpriteProps.new는 getWorldSprite의 실제 IsMoveAble·MoveType·배치/도구 속성을 요구한다. 이 sprite의 B41 속성 입력이 미확정이라 기본 배치/설비 기능을 확정하지 못함; 기존 admission 유무 때문이 아님. | C113 | M227 |
| Base.Mov_ChromeSink | public / core | review_hold / review_required | scripts/newMoveables.txt:93: Type=Moveable, WorldObjectSprite=fixtures_sinks_01_9. InvContextMovable/ISMoveableCursor→ISMoveableSpriteProps.new는 getWorldSprite의 실제 IsMoveAble·MoveType·배치/도구 속성을 요구한다. 이 sprite의 B41 속성 입력이 미확정이라 기본 배치/설비 기능을 확정하지 못함; 기존 admission 유무 때문이 아님. | C113 | M227 |
| Base.Mov_CoffeeMaker | public / core | review_hold / review_required | scripts/newMoveables.txt:993: Type=Moveable, WorldObjectSprite=appliances_cooking_01_56. InvContextMovable/ISMoveableCursor→ISMoveableSpriteProps.new는 getWorldSprite의 실제 IsMoveAble·MoveType·배치/도구 속성을 요구한다. 이 sprite의 B41 속성 입력이 미확정이라 기본 배치/설비 기능을 확정하지 못함; 기존 admission 유무 때문이 아님. | C113 | M227 |
| Base.Mov_ConcreteMixer | public / core | review_hold / review_required | scripts/newMoveables.txt:613: Type=Moveable, WorldObjectSprite=construction_01_6. InvContextMovable/ISMoveableCursor→ISMoveableSpriteProps.new는 getWorldSprite의 실제 IsMoveAble·MoveType·배치/도구 속성을 요구한다. 이 sprite의 B41 속성 입력이 미확정이라 기본 배치/설비 기능을 확정하지 못함; 기존 admission 유무 때문이 아님. | C113 | M227 |
| Base.Mov_CorkBoard | public / core | review_hold / review_required | scripts/newMoveables.txt:713: Type=Moveable, WorldObjectSprite=location_business_office_generic_01_7. InvContextMovable/ISMoveableCursor→ISMoveableSpriteProps.new는 getWorldSprite의 실제 IsMoveAble·MoveType·배치/도구 속성을 요구한다. 이 sprite의 B41 속성 입력이 미확정이라 기본 배치/설비 기능을 확정하지 못함; 기존 admission 유무 때문이 아님. | C113 | M227 |
| Base.Mov_DarkBlueChair | public / core | review_hold / review_required | scripts/newMoveables.txt:293: Type=Moveable, WorldObjectSprite=furniture_seating_indoor_03_49. InvContextMovable/ISMoveableCursor→ISMoveableSpriteProps.new는 getWorldSprite의 실제 IsMoveAble·MoveType·배치/도구 속성을 요구한다. 이 sprite의 B41 속성 입력이 미확정이라 기본 배치/설비 기능을 확정하지 못함; 기존 admission 유무 때문이 아님. | C113 | M227 |
| Base.Mov_DarkWoodenChair | public / core | review_hold / review_required | scripts/newMoveables.txt:193: Type=Moveable, WorldObjectSprite=furniture_seating_indoor_02_0. InvContextMovable/ISMoveableCursor→ISMoveableSpriteProps.new는 getWorldSprite의 실제 IsMoveAble·MoveType·배치/도구 속성을 요구한다. 이 sprite의 B41 속성 입력이 미확정이라 기본 배치/설비 기능을 확정하지 못함; 기존 admission 유무 때문이 아님. | C113 | M227 |
| Base.Mov_DegreeDoctor | public / core | review_hold / review_required | scripts/newMoveables.txt:733: Type=Moveable, WorldObjectSprite=location_community_medical_01_14. InvContextMovable/ISMoveableCursor→ISMoveableSpriteProps.new는 getWorldSprite의 실제 IsMoveAble·MoveType·배치/도구 속성을 요구한다. 이 sprite의 B41 속성 입력이 미확정이라 기본 배치/설비 기능을 확정하지 못함; 기존 admission 유무 때문이 아님. | C113 | M227 |
| Base.Mov_DegreeSurgeon | public / core | review_hold / review_required | scripts/newMoveables.txt:743: Type=Moveable, WorldObjectSprite=location_community_medical_01_31. InvContextMovable/ISMoveableCursor→ISMoveableSpriteProps.new는 getWorldSprite의 실제 IsMoveAble·MoveType·배치/도구 속성을 요구한다. 이 sprite의 B41 속성 입력이 미확정이라 기본 배치/설비 기능을 확정하지 못함; 기존 admission 유무 때문이 아님. | C113 | M227 |
| Base.Mov_DesktopComputer | public / core | review_hold / review_required | scripts/newMoveables.txt:503: Type=Moveable, WorldObjectSprite=appliances_com_01_72. InvContextMovable/ISMoveableCursor→ISMoveableSpriteProps.new는 getWorldSprite의 실제 IsMoveAble·MoveType·배치/도구 속성을 요구한다. 이 sprite의 B41 속성 입력이 미확정이라 기본 배치/설비 기능을 확정하지 못함; 기존 admission 유무 때문이 아님. | C113 | M227 |
| Base.Mov_Doghouse | public / core | review_hold / review_required | scripts/newMoveables.txt:1123: Type=Moveable, WorldObjectSprite=location_farm_accesories_01_9. InvContextMovable/ISMoveableCursor→ISMoveableSpriteProps.new는 getWorldSprite의 실제 IsMoveAble·MoveType·배치/도구 속성을 요구한다. 이 sprite의 B41 속성 입력이 미확정이라 기본 배치/설비 기능을 확정하지 못함; 기존 admission 유무 때문이 아님. | C113 | M227 |
| Base.Mov_Espresso | public / core | review_hold / review_required | scripts/newMoveables.txt:1003: Type=Moveable, WorldObjectSprite=appliances_cooking_01_61. InvContextMovable/ISMoveableCursor→ISMoveableSpriteProps.new는 getWorldSprite의 실제 IsMoveAble·MoveType·배치/도구 속성을 요구한다. 이 sprite의 B41 속성 입력이 미확정이라 기본 배치/설비 기능을 확정하지 못함; 기존 admission 유무 때문이 아님. | C113 | M227 |
| Base.Mov_FancyBlackChair | public / core | review_hold / review_required | scripts/newMoveables.txt:273: Type=Moveable, WorldObjectSprite=furniture_seating_indoor_03_41. InvContextMovable/ISMoveableCursor→ISMoveableSpriteProps.new는 getWorldSprite의 실제 IsMoveAble·MoveType·배치/도구 속성을 요구한다. 이 sprite의 B41 속성 입력이 미확정이라 기본 배치/설비 기능을 확정하지 못함; 기존 admission 유무 때문이 아님. | C113 | M227 |
| Base.Mov_FancyDarkTable | public / core | review_hold / review_required | scripts/newMoveables.txt:453: Type=Moveable, WorldObjectSprite=furniture_tables_high_01_16. InvContextMovable/ISMoveableCursor→ISMoveableSpriteProps.new는 getWorldSprite의 실제 IsMoveAble·MoveType·배치/도구 속성을 요구한다. 이 sprite의 B41 속성 입력이 미확정이라 기본 배치/설비 기능을 확정하지 못함; 기존 admission 유무 때문이 아님. | C113 | M227 |
| Base.Mov_FancyLowTable | public / core | review_hold / review_required | scripts/newMoveables.txt:403: Type=Moveable, WorldObjectSprite=furniture_tables_low_01_3. InvContextMovable/ISMoveableCursor→ISMoveableSpriteProps.new는 getWorldSprite의 실제 IsMoveAble·MoveType·배치/도구 속성을 요구한다. 이 sprite의 B41 속성 입력이 미확정이라 기본 배치/설비 기능을 확정하지 못함; 기존 admission 유무 때문이 아님. | C113 | M227 |
| Base.Mov_FancyTable | public / core | review_hold / review_required | scripts/newMoveables.txt:443: Type=Moveable, WorldObjectSprite=furniture_tables_high_01_15. InvContextMovable/ISMoveableCursor→ISMoveableSpriteProps.new는 getWorldSprite의 실제 IsMoveAble·MoveType·배치/도구 속성을 요구한다. 이 sprite의 B41 속성 입력이 미확정이라 기본 배치/설비 기능을 확정하지 못함; 기존 admission 유무 때문이 아님. | C113 | M227 |
| Base.Mov_FancyToilet | public / core | review_hold / review_required | scripts/newMoveables.txt:123: Type=Moveable, WorldObjectSprite=fixtures_bathroom_01_0. InvContextMovable/ISMoveableCursor→ISMoveableSpriteProps.new는 getWorldSprite의 실제 IsMoveAble·MoveType·배치/도구 속성을 요구한다. 이 sprite의 B41 속성 입력이 미확정이라 기본 배치/설비 기능을 확정하지 못함; 기존 admission 유무 때문이 아님. | C113 | M227 |
| Base.Mov_FancyWhiteChair | public / core | review_hold / review_required | scripts/newMoveables.txt:263: Type=Moveable, WorldObjectSprite=furniture_seating_indoor_01_37. InvContextMovable/ISMoveableCursor→ISMoveableSpriteProps.new는 getWorldSprite의 실제 IsMoveAble·MoveType·배치/도구 속성을 요구한다. 이 sprite의 B41 속성 입력이 미확정이라 기본 배치/설비 기능을 확정하지 못함; 기존 admission 유무 때문이 아님. | C113 | M227 |
| Base.Mov_FitnessContraption | public / core | review_hold / review_required | scripts/newMoveables.txt:523: Type=Moveable, WorldObjectSprite=recreational_sports_01_41. InvContextMovable/ISMoveableCursor→ISMoveableSpriteProps.new는 getWorldSprite의 실제 IsMoveAble·MoveType·배치/도구 속성을 요구한다. 이 sprite의 B41 속성 입력이 미확정이라 기본 배치/설비 기능을 확정하지 못함; 기존 admission 유무 때문이 아님. | C113 | M227 |
| Base.Mov_FlagAdmin | public / core | review_hold / review_required | scripts/newMoveables.txt:583: Type=Moveable, WorldObjectSprite=walls_decoration_01_18. InvContextMovable/ISMoveableCursor→ISMoveableSpriteProps.new는 getWorldSprite의 실제 IsMoveAble·MoveType·배치/도구 속성을 요구한다. 이 sprite의 B41 속성 입력이 미확정이라 기본 배치/설비 기능을 확정하지 못함; 기존 admission 유무 때문이 아님. | C113 | M227 |
| Base.Mov_FlagUSA | public / core | review_hold / review_required | scripts/newMoveables.txt:563: Type=Moveable, WorldObjectSprite=walls_decoration_01_16. InvContextMovable/ISMoveableCursor→ISMoveableSpriteProps.new는 getWorldSprite의 실제 IsMoveAble·MoveType·배치/도구 속성을 요구한다. 이 sprite의 B41 속성 입력이 미확정이라 기본 배치/설비 기능을 확정하지 못함; 기존 admission 유무 때문이 아님. | C113 | M227 |
| Base.Mov_FlagUSALarge | public / core | review_hold / review_required | scripts/newMoveables.txt:573: Type=Moveable, WorldObjectSprite=location_military_knox_01_8. InvContextMovable/ISMoveableCursor→ISMoveableSpriteProps.new는 getWorldSprite의 실제 IsMoveAble·MoveType·배치/도구 속성을 요구한다. 이 sprite의 B41 속성 입력이 미확정이라 기본 배치/설비 기능을 확정하지 못함; 기존 admission 유무 때문이 아님. | C113 | M227 |
| Base.Mov_FoldingChair | public / core | review_hold / review_required | scripts/newMoveables.txt:3: Type=Moveable, WorldObjectSprite=furniture_seating_indoor_01_60. InvContextMovable/ISMoveableCursor→ISMoveableSpriteProps.new는 getWorldSprite의 실제 IsMoveAble·MoveType·배치/도구 속성을 요구한다. 이 sprite의 B41 속성 입력이 미확정이라 기본 배치/설비 기능을 확정하지 못함; 기존 admission 유무 때문이 아님. | C113 | M227 |
| Base.Mov_FridgeMini | public / core | review_hold / review_required | scripts/newMoveables.txt:1023: Type=Moveable, WorldObjectSprite=appliances_refrigeration_01_25. InvContextMovable/ISMoveableCursor→ISMoveableSpriteProps.new는 getWorldSprite의 실제 IsMoveAble·MoveType·배치/도구 속성을 요구한다. 이 sprite의 B41 속성 입력이 미확정이라 기본 배치/설비 기능을 확정하지 못함; 기존 admission 유무 때문이 아님. | C113 | M227 |
| Base.Mov_GardenGnome | public / core | review_hold / review_required | scripts/newMoveables.txt:983: Type=Moveable, WorldObjectSprite=vegetation_ornamental_01_48. InvContextMovable/ISMoveableCursor→ISMoveableSpriteProps.new는 getWorldSprite의 실제 IsMoveAble·MoveType·배치/도구 속성을 요구한다. 이 sprite의 B41 속성 입력이 미확정이라 기본 배치/설비 기능을 확정하지 못함; 기존 admission 유무 때문이 아님. | C113 | M227 |
| Base.Mov_GraveArched | public / core | review_hold / review_required | scripts/newMoveables.txt:1093: Type=Moveable, WorldObjectSprite=location_community_cemetary_01_2. InvContextMovable/ISMoveableCursor→ISMoveableSpriteProps.new는 getWorldSprite의 실제 IsMoveAble·MoveType·배치/도구 속성을 요구한다. 이 sprite의 B41 속성 입력이 미확정이라 기본 배치/설비 기능을 확정하지 못함; 기존 admission 유무 때문이 아님. | C113 | M227 |
| Base.Mov_GraveRound | public / core | review_hold / review_required | scripts/newMoveables.txt:1083: Type=Moveable, WorldObjectSprite=location_community_cemetary_01_0. InvContextMovable/ISMoveableCursor→ISMoveableSpriteProps.new는 getWorldSprite의 실제 IsMoveAble·MoveType·배치/도구 속성을 요구한다. 이 sprite의 B41 속성 입력이 미확정이라 기본 배치/설비 기능을 확정하지 못함; 기존 admission 유무 때문이 아님. | C113 | M227 |
| Base.Mov_GraveSquare | public / core | review_hold / review_required | scripts/newMoveables.txt:1103: Type=Moveable, WorldObjectSprite=location_community_cemetary_01_4. InvContextMovable/ISMoveableCursor→ISMoveableSpriteProps.new는 getWorldSprite의 실제 IsMoveAble·MoveType·배치/도구 속성을 요구한다. 이 sprite의 B41 속성 입력이 미확정이라 기본 배치/설비 기능을 확정하지 못함; 기존 admission 유무 때문이 아님. | C113 | M227 |
| Base.Mov_GraveWorn | public / core | review_hold / review_required | scripts/newMoveables.txt:1113: Type=Moveable, WorldObjectSprite=location_community_cemetary_01_8. InvContextMovable/ISMoveableCursor→ISMoveableSpriteProps.new는 getWorldSprite의 실제 IsMoveAble·MoveType·배치/도구 속성을 요구한다. 이 sprite의 B41 속성 입력이 미확정이라 기본 배치/설비 기능을 확정하지 못함; 기존 admission 유무 때문이 아님. | C113 | M227 |
| Base.Mov_GreenChair | public / core | review_hold / review_required | scripts/newMoveables.txt:203: Type=Moveable, WorldObjectSprite=furniture_seating_indoor_01_57. InvContextMovable/ISMoveableCursor→ISMoveableSpriteProps.new는 getWorldSprite의 실제 IsMoveAble·MoveType·배치/도구 속성을 요구한다. 이 sprite의 B41 속성 입력이 미확정이라 기본 배치/설비 기능을 확정하지 못함; 기존 admission 유무 때문이 아님. | C113 | M227 |
| Base.Mov_GreenComfyChair | public / core | review_hold / review_required | scripts/newMoveables.txt:303: Type=Moveable, WorldObjectSprite=furniture_seating_indoor_01_9. InvContextMovable/ISMoveableCursor→ISMoveableSpriteProps.new는 getWorldSprite의 실제 IsMoveAble·MoveType·배치/도구 속성을 요구한다. 이 sprite의 B41 속성 입력이 미확정이라 기본 배치/설비 기능을 확정하지 못함; 기존 admission 유무 때문이 아님. | C113 | M227 |
| Base.Mov_GreenOven | public / core | review_hold / review_required | scripts/newMoveables.txt:163: Type=Moveable, WorldObjectSprite=appliances_cooking_01_1. InvContextMovable/ISMoveableCursor→ISMoveableSpriteProps.new는 getWorldSprite의 실제 IsMoveAble·MoveType·배치/도구 속성을 요구한다. 이 sprite의 B41 속성 입력이 미확정이라 기본 배치/설비 기능을 확정하지 못함; 기존 admission 유무 때문이 아님. | C113 | M227 |
| Base.Mov_GreyChair | public / core | review_hold / review_required | scripts/newMoveables.txt:23: Type=Moveable, WorldObjectSprite=furniture_seating_indoor_01_54. InvContextMovable/ISMoveableCursor→ISMoveableSpriteProps.new는 getWorldSprite의 실제 IsMoveAble·MoveType·배치/도구 속성을 요구한다. 이 sprite의 B41 속성 입력이 미확정이라 기본 배치/설비 기능을 확정하지 못함; 기존 admission 유무 때문이 아님. | C113 | M227 |
| Base.Mov_GreyComfyChair | public / core | review_hold / review_required | scripts/newMoveables.txt:333: Type=Moveable, WorldObjectSprite=furniture_seating_indoor_03_4. InvContextMovable/ISMoveableCursor→ISMoveableSpriteProps.new는 getWorldSprite의 실제 IsMoveAble·MoveType·배치/도구 속성을 요구한다. 이 sprite의 B41 속성 입력이 미확정이라 기본 배치/설비 기능을 확정하지 못함; 기존 admission 유무 때문이 아님. | C113 | M227 |
| Base.Mov_GreyOven | public / core | review_hold / review_required | scripts/newMoveables.txt:143: Type=Moveable, WorldObjectSprite=appliances_cooking_01_5. InvContextMovable/ISMoveableCursor→ISMoveableSpriteProps.new는 getWorldSprite의 실제 IsMoveAble·MoveType·배치/도구 속성을 요구한다. 이 sprite의 B41 속성 입력이 미확정이라 기본 배치/설비 기능을 확정하지 못함; 기존 admission 유무 때문이 아님. | C113 | M227 |
| Base.Mov_HotdogMachine | public / core | review_hold / review_required | scripts/newMoveables.txt:1247: Type=Moveable, WorldObjectSprite=location_shop_fossoil_01_10. InvContextMovable/ISMoveableCursor→ISMoveableSpriteProps.new는 getWorldSprite의 실제 IsMoveAble·MoveType·배치/도구 속성을 요구한다. 이 sprite의 B41 속성 입력이 미확정이라 기본 배치/설비 기능을 확정하지 못함; 기존 admission 유무 때문이 아님. | C113 | M227 |
| Base.Mov_HuntingTrophy | public / core | review_hold / review_required | scripts/newMoveables.txt:693: Type=Moveable, WorldObjectSprite=camping_01_18. InvContextMovable/ISMoveableCursor→ISMoveableSpriteProps.new는 getWorldSprite의 실제 IsMoveAble·MoveType·배치/도구 속성을 요구한다. 이 sprite의 B41 속성 입력이 미확정이라 기본 배치/설비 기능을 확정하지 못함; 기존 admission 유무 때문이 아님. | C113 | M227 |
| Base.Mov_IndustrialSink | public / core | review_hold / review_required | scripts/newMoveables.txt:103: Type=Moveable, WorldObjectSprite=fixtures_sinks_01_16. InvContextMovable/ISMoveableCursor→ISMoveableSpriteProps.new는 getWorldSprite의 실제 IsMoveAble·MoveType·배치/도구 속성을 요구한다. 이 sprite의 B41 속성 입력이 미확정이라 기본 배치/설비 기능을 확정하지 못함; 기존 admission 유무 때문이 아님. | C113 | M227 |
| Base.Mov_Lamp1 | public / core | review_hold / review_required | scripts/newitems.txt:4378: Type=Moveable, WorldObjectSprite=lighting_indoor_01_8. InvContextMovable/ISMoveableCursor→ISMoveableSpriteProps.new는 getWorldSprite의 실제 IsMoveAble·MoveType·배치/도구 속성을 요구한다. 이 sprite의 B41 속성 입력이 미확정이라 기본 배치/설비 기능을 확정하지 못함; 기존 admission 유무 때문이 아님. | C113 | M227 |
| Base.Mov_Lamp2 | public / core | review_hold / review_required | scripts/newitems.txt:4388: Type=Moveable, WorldObjectSprite=lighting_indoor_01_9. InvContextMovable/ISMoveableCursor→ISMoveableSpriteProps.new는 getWorldSprite의 실제 IsMoveAble·MoveType·배치/도구 속성을 요구한다. 이 sprite의 B41 속성 입력이 미확정이라 기본 배치/설비 기능을 확정하지 못함; 기존 admission 유무 때문이 아님. | C113 | M227 |
| Base.Mov_Lamp3 | public / core | review_hold / review_required | scripts/newitems.txt:4398: Type=Moveable, WorldObjectSprite=lighting_indoor_01_10. InvContextMovable/ISMoveableCursor→ISMoveableSpriteProps.new는 getWorldSprite의 실제 IsMoveAble·MoveType·배치/도구 속성을 요구한다. 이 sprite의 B41 속성 입력이 미확정이라 기본 배치/설비 기능을 확정하지 못함; 기존 admission 유무 때문이 아님. | C113 | M227 |
| Base.Mov_Lamp4 | public / core | review_hold / review_required | scripts/newitems.txt:4408: Type=Moveable, WorldObjectSprite=lighting_indoor_01_11. InvContextMovable/ISMoveableCursor→ISMoveableSpriteProps.new는 getWorldSprite의 실제 IsMoveAble·MoveType·배치/도구 속성을 요구한다. 이 sprite의 B41 속성 입력이 미확정이라 기본 배치/설비 기능을 확정하지 못함; 기존 admission 유무 때문이 아님. | C113 | M227 |
| Base.Mov_Lamp5 | public / core | review_hold / review_required | scripts/newitems.txt:4418: Type=Moveable, WorldObjectSprite=lighting_indoor_01_12. InvContextMovable/ISMoveableCursor→ISMoveableSpriteProps.new는 getWorldSprite의 실제 IsMoveAble·MoveType·배치/도구 속성을 요구한다. 이 sprite의 B41 속성 입력이 미확정이라 기본 배치/설비 기능을 확정하지 못함; 기존 admission 유무 때문이 아님. | C113 | M227 |
| Base.Mov_Lamp6 | public / core | review_hold / review_required | scripts/newitems.txt:4428: Type=Moveable, WorldObjectSprite=lighting_indoor_01_13. InvContextMovable/ISMoveableCursor→ISMoveableSpriteProps.new는 getWorldSprite의 실제 IsMoveAble·MoveType·배치/도구 속성을 요구한다. 이 sprite의 B41 속성 입력이 미확정이라 기본 배치/설비 기능을 확정하지 못함; 기존 admission 유무 때문이 아님. | C113 | M227 |
| Base.Mov_LightConstruction | public / core | review_hold / review_required | scripts/newMoveables.txt:603: Type=Moveable, WorldObjectSprite=lighting_outdoor_01_49. InvContextMovable/ISMoveableCursor→ISMoveableSpriteProps.new는 getWorldSprite의 실제 IsMoveAble·MoveType·배치/도구 속성을 요구한다. 이 sprite의 B41 속성 입력이 미확정이라 기본 배치/설비 기능을 확정하지 못함; 기존 admission 유무 때문이 아님. | C113 | M227 |
| Base.Mov_LightRoundTable | public / core | review_hold / review_required | scripts/newMoveables.txt:493: Type=Moveable, WorldObjectSprite=furniture_tables_high_01_7. InvContextMovable/ISMoveableCursor→ISMoveableSpriteProps.new는 getWorldSprite의 실제 IsMoveAble·MoveType·배치/도구 속성을 요구한다. 이 sprite의 B41 속성 입력이 미확정이라 기본 배치/설비 기능을 확정하지 못함; 기존 admission 유무 때문이 아님. | C113 | M227 |
| Base.Mov_LongTable | public / core | review_hold / review_required | scripts/newMoveables.txt:423: Type=Moveable, WorldObjectSprite=furniture_tables_high_01_4. InvContextMovable/ISMoveableCursor→ISMoveableSpriteProps.new는 getWorldSprite의 실제 IsMoveAble·MoveType·배치/도구 속성을 요구한다. 이 sprite의 B41 속성 입력이 미확정이라 기본 배치/설비 기능을 확정하지 못함; 기존 admission 유무 때문이 아님. | C113 | M227 |
| Base.Mov_Mailbox | public / core | review_hold / review_required | scripts/newMoveables.txt:1143: Type=Moveable, WorldObjectSprite=street_decoration_01_21. InvContextMovable/ISMoveableCursor→ISMoveableSpriteProps.new는 getWorldSprite의 실제 IsMoveAble·MoveType·배치/도구 속성을 요구한다. 이 sprite의 B41 속성 입력이 미확정이라 기본 배치/설비 기능을 확정하지 못함; 기존 admission 유무 때문이 아님. | C113 | M227 |
| Base.Mov_MannequinFemale | public / core | review_hold / review_required | scripts/newMoveables.txt:543: Type=Moveable, WorldObjectSprite=location_shop_mall_01_66. InvContextMovable/ISMoveableCursor→ISMoveableSpriteProps.new는 getWorldSprite의 실제 IsMoveAble·MoveType·배치/도구 속성을 요구한다. 이 sprite의 B41 속성 입력이 미확정이라 기본 배치/설비 기능을 확정하지 못함; 기존 admission 유무 때문이 아님. | C113 | M227 |
| Base.Mov_MannequinMale | public / core | review_hold / review_required | scripts/newMoveables.txt:533: Type=Moveable, WorldObjectSprite=location_shop_mall_01_69. InvContextMovable/ISMoveableCursor→ISMoveableSpriteProps.new는 getWorldSprite의 실제 IsMoveAble·MoveType·배치/도구 속성을 요구한다. 이 sprite의 B41 속성 입력이 미확정이라 기본 배치/설비 기능을 확정하지 못함; 기존 admission 유무 때문이 아님. | C113 | M227 |
| Base.Mov_MapUSA | public / core | review_hold / review_required | scripts/newMoveables.txt:553: Type=Moveable, WorldObjectSprite=location_community_school_01_22. InvContextMovable/ISMoveableCursor→ISMoveableSpriteProps.new는 getWorldSprite의 실제 IsMoveAble·MoveType·배치/도구 속성을 요구한다. 이 sprite의 B41 속성 입력이 미확정이라 기본 배치/설비 기능을 확정하지 못함; 기존 admission 유무 때문이 아님. | C113 | M227 |
| Base.Mov_MetalLocker | public / core | review_hold / review_required | scripts/newMoveables.txt:83: Type=Moveable, WorldObjectSprite=furniture_storage_02_8. InvContextMovable/ISMoveableCursor→ISMoveableSpriteProps.new는 getWorldSprite의 실제 IsMoveAble·MoveType·배치/도구 속성을 요구한다. 이 sprite의 B41 속성 입력이 미확정이라 기본 배치/설비 기능을 확정하지 못함; 기존 admission 유무 때문이 아님. | C113 | M227 |
| Base.Mov_MetalStool | public / core | review_hold / review_required | scripts/newMoveables.txt:63: Type=Moveable, WorldObjectSprite=location_community_medical_01_10. InvContextMovable/ISMoveableCursor→ISMoveableSpriteProps.new는 getWorldSprite의 실제 IsMoveAble·MoveType·배치/도구 속성을 요구한다. 이 sprite의 B41 속성 입력이 미확정이라 기본 배치/설비 기능을 확정하지 못함; 기존 admission 유무 때문이 아님. | C113 | M227 |
| Base.Mov_Microphone | public / core | review_hold / review_required | scripts/newMoveables.txt:683: Type=Moveable, WorldObjectSprite=appliances_com_01_70. InvContextMovable/ISMoveableCursor→ISMoveableSpriteProps.new는 getWorldSprite의 실제 IsMoveAble·MoveType·배치/도구 속성을 요구한다. 이 sprite의 B41 속성 입력이 미확정이라 기본 배치/설비 기능을 확정하지 못함; 기존 admission 유무 때문이 아님. | C113 | M227 |
| Base.Mov_Microwave | public / core | review_hold / review_required | scripts/newitems.txt:4438: Type=Moveable, WorldObjectSprite=appliances_cooking_01_24. InvContextMovable/ISMoveableCursor→ISMoveableSpriteProps.new는 getWorldSprite의 실제 IsMoveAble·MoveType·배치/도구 속성을 요구한다. 이 sprite의 B41 속성 입력이 미확정이라 기본 배치/설비 기능을 확정하지 못함; 기존 admission 유무 때문이 아님. | C113 | M227 |
| Base.Mov_Microwave2 | public / core | review_hold / review_required | scripts/newitems.txt:4448: Type=Moveable, WorldObjectSprite=appliances_cooking_01_28. InvContextMovable/ISMoveableCursor→ISMoveableSpriteProps.new는 getWorldSprite의 실제 IsMoveAble·MoveType·배치/도구 속성을 요구한다. 이 sprite의 B41 속성 입력이 미확정이라 기본 배치/설비 기능을 확정하지 못함; 기존 admission 유무 때문이 아님. | C113 | M227 |
| Base.Mov_MirrorLarge | public / core | review_hold / review_required | scripts/newMoveables.txt:793: Type=Moveable, WorldObjectSprite=walls_decoration_01_5. InvContextMovable/ISMoveableCursor→ISMoveableSpriteProps.new는 getWorldSprite의 실제 IsMoveAble·MoveType·배치/도구 속성을 요구한다. 이 sprite의 B41 속성 입력이 미확정이라 기본 배치/설비 기능을 확정하지 못함; 기존 admission 유무 때문이 아님. | C113 | M227 |
| Base.Mov_MirrorSmall | public / core | review_hold / review_required | scripts/newMoveables.txt:783: Type=Moveable, WorldObjectSprite=walls_decoration_01_10. InvContextMovable/ISMoveableCursor→ISMoveableSpriteProps.new는 getWorldSprite의 실제 IsMoveAble·MoveType·배치/도구 속성을 요구한다. 이 sprite의 B41 속성 입력이 미확정이라 기본 배치/설비 기능을 확정하지 못함; 기존 admission 유무 때문이 아님. | C113 | M227 |
| Base.Mov_MirrorTall | public / core | review_hold / review_required | scripts/newMoveables.txt:763: Type=Moveable, WorldObjectSprite=walls_decoration_01_9. InvContextMovable/ISMoveableCursor→ISMoveableSpriteProps.new는 getWorldSprite의 실제 IsMoveAble·MoveType·배치/도구 속성을 요구한다. 이 sprite의 B41 속성 입력이 미확정이라 기본 배치/설비 기능을 확정하지 못함; 기존 admission 유무 때문이 아님. | C113 | M227 |
| Base.Mov_MirrorWood | public / core | review_hold / review_required | scripts/newMoveables.txt:773: Type=Moveable, WorldObjectSprite=walls_decoration_01_7. InvContextMovable/ISMoveableCursor→ISMoveableSpriteProps.new는 getWorldSprite의 실제 IsMoveAble·MoveType·배치/도구 속성을 요구한다. 이 sprite의 B41 속성 입력이 미확정이라 기본 배치/설비 기능을 확정하지 못함; 기존 admission 유무 때문이 아님. | C113 | M227 |
| Base.Mov_MobileBloodbag | public / core | review_hold / review_required | scripts/newMoveables.txt:963: Type=Moveable, WorldObjectSprite=location_community_medical_01_25. InvContextMovable/ISMoveableCursor→ISMoveableSpriteProps.new는 getWorldSprite의 실제 IsMoveAble·MoveType·배치/도구 속성을 요구한다. 이 sprite의 B41 속성 입력이 미확정이라 기본 배치/설비 기능을 확정하지 못함; 기존 admission 유무 때문이 아님. | C113 | M227 |
| Base.Mov_MobileCounter | public / core | review_hold / review_required | scripts/newMoveables.txt:73: Type=Moveable, WorldObjectSprite=location_community_medical_01_49. InvContextMovable/ISMoveableCursor→ISMoveableSpriteProps.new는 getWorldSprite의 실제 IsMoveAble·MoveType·배치/도구 속성을 요구한다. 이 sprite의 B41 속성 입력이 미확정이라 기본 배치/설비 기능을 확정하지 못함; 기존 admission 유무 때문이 아님. | C113 | M227 |
| Base.Mov_ModernOven | public / core | review_hold / review_required | scripts/newMoveables.txt:153: Type=Moveable, WorldObjectSprite=appliances_cooking_01_13. InvContextMovable/ISMoveableCursor→ISMoveableSpriteProps.new는 getWorldSprite의 실제 IsMoveAble·MoveType·배치/도구 속성을 요구한다. 이 sprite의 B41 속성 입력이 미확정이라 기본 배치/설비 기능을 확정하지 못함; 기존 admission 유무 때문이 아님. | C113 | M227 |
| Base.Mov_NapkinDispenser | public / core | review_hold / review_required | scripts/newMoveables.txt:1277: Type=Moveable, WorldObjectSprite=location_shop_accessories_01_10. InvContextMovable/ISMoveableCursor→ISMoveableSpriteProps.new는 getWorldSprite의 실제 IsMoveAble·MoveType·배치/도구 속성을 요구한다. 이 sprite의 B41 속성 입력이 미확정이라 기본 배치/설비 기능을 확정하지 못함; 기존 admission 유무 때문이 아님. | C113 | M227 |
| Base.Mov_OakRoundTable | public / core | review_hold / review_required | scripts/newMoveables.txt:483: Type=Moveable, WorldObjectSprite=furniture_tables_high_01_6. InvContextMovable/ISMoveableCursor→ISMoveableSpriteProps.new는 getWorldSprite의 실제 IsMoveAble·MoveType·배치/도구 속성을 요구한다. 이 sprite의 B41 속성 입력이 미확정이라 기본 배치/설비 기능을 확정하지 못함; 기존 admission 유무 때문이 아님. | C113 | M227 |
| Base.Mov_OfficeChair | public / core | review_hold / review_required | scripts/newMoveables.txt:13: Type=Moveable, WorldObjectSprite=furniture_seating_indoor_01_50. InvContextMovable/ISMoveableCursor→ISMoveableSpriteProps.new는 getWorldSprite의 실제 IsMoveAble·MoveType·배치/도구 속성을 요구한다. 이 sprite의 B41 속성 입력이 미확정이라 기본 배치/설비 기능을 확정하지 못함; 기존 admission 유무 때문이 아님. | C113 | M227 |
| Base.Mov_OrangeFuton | public / core | review_hold / review_required | scripts/newMoveables.txt:373: Type=Moveable, WorldObjectSprite=furniture_seating_indoor_01_46. InvContextMovable/ISMoveableCursor→ISMoveableSpriteProps.new는 getWorldSprite의 실제 IsMoveAble·MoveType·배치/도구 속성을 요구한다. 이 sprite의 B41 속성 입력이 미확정이라 기본 배치/설비 기능을 확정하지 못함; 기존 admission 유무 때문이 아님. | C113 | M227 |
| Base.Mov_OrangeModernChair | public / core | review_hold / review_required | scripts/newMoveables.txt:363: Type=Moveable, WorldObjectSprite=furniture_seating_indoor_01_12. InvContextMovable/ISMoveableCursor→ISMoveableSpriteProps.new는 getWorldSprite의 실제 IsMoveAble·MoveType·배치/도구 속성을 요구한다. 이 sprite의 B41 속성 입력이 미확정이라 기본 배치/설비 기능을 확정하지 못함; 기존 admission 유무 때문이 아님. | C113 | M227 |
| Base.Mov_PaintingBetty | public / core | review_hold / review_required | scripts/newMoveables.txt:823: Type=Moveable, WorldObjectSprite=walls_decoration_01_48. InvContextMovable/ISMoveableCursor→ISMoveableSpriteProps.new는 getWorldSprite의 실제 IsMoveAble·MoveType·배치/도구 속성을 요구한다. 이 sprite의 B41 속성 입력이 미확정이라 기본 배치/설비 기능을 확정하지 못함; 기존 admission 유무 때문이 아님. | C113 | M227 |
| Base.Mov_PaintingElisa | public / core | review_hold / review_required | scripts/newMoveables.txt:833: Type=Moveable, WorldObjectSprite=walls_decoration_01_46. InvContextMovable/ISMoveableCursor→ISMoveableSpriteProps.new는 getWorldSprite의 실제 IsMoveAble·MoveType·배치/도구 속성을 요구한다. 이 sprite의 B41 속성 입력이 미확정이라 기본 배치/설비 기능을 확정하지 못함; 기존 admission 유무 때문이 아님. | C113 | M227 |
| Base.Mov_PaintingGreen | public / core | review_hold / review_required | scripts/newMoveables.txt:803: Type=Moveable, WorldObjectSprite=walls_decoration_01_35. InvContextMovable/ISMoveableCursor→ISMoveableSpriteProps.new는 getWorldSprite의 실제 IsMoveAble·MoveType·배치/도구 속성을 요구한다. 이 sprite의 B41 속성 입력이 미확정이라 기본 배치/설비 기능을 확정하지 못함; 기존 admission 유무 때문이 아님. | C113 | M227 |
| Base.Mov_PaintingLibrary | public / core | review_hold / review_required | scripts/newMoveables.txt:813: Type=Moveable, WorldObjectSprite=walls_decoration_01_57. InvContextMovable/ISMoveableCursor→ISMoveableSpriteProps.new는 getWorldSprite의 실제 IsMoveAble·MoveType·배치/도구 속성을 요구한다. 이 sprite의 B41 속성 입력이 미확정이라 기본 배치/설비 기능을 확정하지 못함; 기존 admission 유무 때문이 아님. | C113 | M227 |
| Base.Mov_PalletEmpty | public / core | review_hold / review_required | scripts/newMoveables.txt:623: Type=Moveable, WorldObjectSprite=construction_01_5. InvContextMovable/ISMoveableCursor→ISMoveableSpriteProps.new는 getWorldSprite의 실제 IsMoveAble·MoveType·배치/도구 속성을 요구한다. 이 sprite의 B41 속성 입력이 미확정이라 기본 배치/설비 기능을 확정하지 못함; 기존 admission 유무 때문이 아님. | C113 | M227 |
| Base.Mov_PileOCrepeChair | public / core | review_hold / review_required | scripts/newMoveables.txt:253: Type=Moveable, WorldObjectSprite=location_restaurant_pileocrepe_01_41. InvContextMovable/ISMoveableCursor→ISMoveableSpriteProps.new는 getWorldSprite의 실제 IsMoveAble·MoveType·배치/도구 속성을 요구한다. 이 sprite의 B41 속성 입력이 미확정이라 기본 배치/설비 기능을 확정하지 못함; 기존 admission 유무 때문이 아님. | C113 | M227 |
| Base.Mov_PinballMachine | public / core | review_hold / review_required | scripts/newMoveables.txt:643: Type=Moveable, WorldObjectSprite=recreational_01_25. InvContextMovable/ISMoveableCursor→ISMoveableSpriteProps.new는 getWorldSprite의 실제 IsMoveAble·MoveType·배치/도구 속성을 요구한다. 이 sprite의 B41 속성 입력이 미확정이라 기본 배치/설비 기능을 확정하지 못함; 기존 admission 유무 때문이 아님. | C113 | M227 |
| Base.Mov_PinkFlamingo | public / core | review_hold / review_required | scripts/newMoveables.txt:973: Type=Moveable, WorldObjectSprite=vegetation_ornamental_01_25. InvContextMovable/ISMoveableCursor→ISMoveableSpriteProps.new는 getWorldSprite의 실제 IsMoveAble·MoveType·배치/도구 속성을 요구한다. 이 sprite의 B41 속성 입력이 미확정이라 기본 배치/설비 기능을 확정하지 못함; 기존 admission 유무 때문이 아님. | C113 | M227 |
| Base.Mov_PlasticChair | public / core | review_hold / review_required | scripts/newMoveables.txt:43: Type=Moveable, WorldObjectSprite=furniture_seating_outdoor_01_17. InvContextMovable/ISMoveableCursor→ISMoveableSpriteProps.new는 getWorldSprite의 실제 IsMoveAble·MoveType·배치/도구 속성을 요구한다. 이 sprite의 B41 속성 입력이 미확정이라 기본 배치/설비 기능을 확정하지 못함; 기존 admission 유무 때문이 아님. | C113 | M227 |
| Base.Mov_PlasticLowTable | public / core | review_hold / review_required | scripts/newMoveables.txt:413: Type=Moveable, WorldObjectSprite=furniture_tables_low_01_20. InvContextMovable/ISMoveableCursor→ISMoveableSpriteProps.new는 getWorldSprite의 실제 IsMoveAble·MoveType·배치/도구 속성을 요구한다. 이 sprite의 B41 속성 입력이 미확정이라 기본 배치/설비 기능을 확정하지 못함; 기존 admission 유무 때문이 아님. | C113 | M227 |
| Base.Mov_PopcornMachine | public / core | review_hold / review_required | scripts/newMoveables.txt:1257: Type=Moveable, WorldObjectSprite=location_entertainment_theatre_01_17. InvContextMovable/ISMoveableCursor→ISMoveableSpriteProps.new는 getWorldSprite의 실제 IsMoveAble·MoveType·배치/도구 속성을 요구한다. 이 sprite의 B41 속성 입력이 미확정이라 기본 배치/설비 기능을 확정하지 못함; 기존 admission 유무 때문이 아님. | C113 | M227 |
| Base.Mov_PosterDroids | public / core | review_hold / review_required | scripts/newMoveables.txt:843: Type=Moveable, WorldObjectSprite=walls_decoration_01_33. InvContextMovable/ISMoveableCursor→ISMoveableSpriteProps.new는 getWorldSprite의 실제 IsMoveAble·MoveType·배치/도구 속성을 요구한다. 이 sprite의 B41 속성 입력이 미확정이라 기본 배치/설비 기능을 확정하지 못함; 기존 admission 유무 때문이 아님. | C113 | M227 |
| Base.Mov_PosterElement | public / core | review_hold / review_required | scripts/newMoveables.txt:873: Type=Moveable, WorldObjectSprite=location_entertainment_theatre_01_84. InvContextMovable/ISMoveableCursor→ISMoveableSpriteProps.new는 getWorldSprite의 실제 IsMoveAble·MoveType·배치/도구 속성을 요구한다. 이 sprite의 B41 속성 입력이 미확정이라 기본 배치/설비 기능을 확정하지 못함; 기존 admission 유무 때문이 아님. | C113 | M227 |
| Base.Mov_PosterMedical | public / core | review_hold / review_required | scripts/newMoveables.txt:753: Type=Moveable, WorldObjectSprite=location_community_medical_01_11. InvContextMovable/ISMoveableCursor→ISMoveableSpriteProps.new는 getWorldSprite의 실제 IsMoveAble·MoveType·배치/도구 속성을 요구한다. 이 sprite의 B41 속성 입력이 미확정이라 기본 배치/설비 기능을 확정하지 못함; 기존 admission 유무 때문이 아님. | C113 | M227 |
| Base.Mov_PosterOmega | public / core | review_hold / review_required | scripts/newMoveables.txt:863: Type=Moveable, WorldObjectSprite=walls_decoration_01_50. InvContextMovable/ISMoveableCursor→ISMoveableSpriteProps.new는 getWorldSprite의 실제 IsMoveAble·MoveType·배치/도구 속성을 요구한다. 이 sprite의 B41 속성 입력이 미확정이라 기본 배치/설비 기능을 확정하지 못함; 기존 admission 유무 때문이 아님. | C113 | M227 |
| Base.Mov_PosterPaws | public / core | review_hold / review_required | scripts/newMoveables.txt:853: Type=Moveable, WorldObjectSprite=location_entertainment_theatre_01_83. InvContextMovable/ISMoveableCursor→ISMoveableSpriteProps.new는 getWorldSprite의 실제 IsMoveAble·MoveType·배치/도구 속성을 요구한다. 이 sprite의 B41 속성 입력이 미확정이라 기본 배치/설비 기능을 확정하지 못함; 기존 admission 유무 때문이 아님. | C113 | M227 |
| Base.Mov_PosterPieBlue | public / core | review_hold / review_required | scripts/newMoveables.txt:893: Type=Moveable, WorldObjectSprite=location_restaurant_pie_01_57. InvContextMovable/ISMoveableCursor→ISMoveableSpriteProps.new는 getWorldSprite의 실제 IsMoveAble·MoveType·배치/도구 속성을 요구한다. 이 sprite의 B41 속성 입력이 미확정이라 기본 배치/설비 기능을 확정하지 못함; 기존 admission 유무 때문이 아님. | C113 | M227 |
| Base.Mov_PosterPieGreen | public / core | review_hold / review_required | scripts/newMoveables.txt:913: Type=Moveable, WorldObjectSprite=location_restaurant_pie_01_58. InvContextMovable/ISMoveableCursor→ISMoveableSpriteProps.new는 getWorldSprite의 실제 IsMoveAble·MoveType·배치/도구 속성을 요구한다. 이 sprite의 B41 속성 입력이 미확정이라 기본 배치/설비 기능을 확정하지 못함; 기존 admission 유무 때문이 아님. | C113 | M227 |
| Base.Mov_PosterPiePink | public / core | review_hold / review_required | scripts/newMoveables.txt:903: Type=Moveable, WorldObjectSprite=location_restaurant_pie_01_59. InvContextMovable/ISMoveableCursor→ISMoveableSpriteProps.new는 getWorldSprite의 실제 IsMoveAble·MoveType·배치/도구 속성을 요구한다. 이 sprite의 B41 속성 입력이 미확정이라 기본 배치/설비 기능을 확정하지 못함; 기존 admission 유무 때문이 아님. | C113 | M227 |
| Base.Mov_PosterPieRed | public / core | review_hold / review_required | scripts/newMoveables.txt:883: Type=Moveable, WorldObjectSprite=location_restaurant_pie_01_56. InvContextMovable/ISMoveableCursor→ISMoveableSpriteProps.new는 getWorldSprite의 실제 IsMoveAble·MoveType·배치/도구 속성을 요구한다. 이 sprite의 B41 속성 입력이 미확정이라 기본 배치/설비 기능을 확정하지 못함; 기존 admission 유무 때문이 아님. | C113 | M227 |
| Base.Mov_Projector | public / core | review_hold / review_required | scripts/newMoveables.txt:1013: Type=Moveable, WorldObjectSprite=appliances_com_01_85. InvContextMovable/ISMoveableCursor→ISMoveableSpriteProps.new는 getWorldSprite의 실제 IsMoveAble·MoveType·배치/도구 속성을 요구한다. 이 sprite의 B41 속성 입력이 미확정이라 기본 배치/설비 기능을 확정하지 못함; 기존 admission 유무 때문이 아님. | C113 | M227 |
| Base.Mov_PurpleRattanChair | public / core | review_hold / review_required | scripts/newMoveables.txt:393: Type=Moveable, WorldObjectSprite=furniture_seating_indoor_01_33. InvContextMovable/ISMoveableCursor→ISMoveableSpriteProps.new는 getWorldSprite의 실제 IsMoveAble·MoveType·배치/도구 속성을 요구한다. 이 sprite의 B41 속성 입력이 미확정이라 기본 배치/설비 기능을 확정하지 못함; 기존 admission 유무 때문이 아님. | C113 | M227 |
| Base.Mov_PurpleWoodenChair | public / core | review_hold / review_required | scripts/newMoveables.txt:243: Type=Moveable, WorldObjectSprite=furniture_seating_indoor_03_45. InvContextMovable/ISMoveableCursor→ISMoveableSpriteProps.new는 getWorldSprite의 실제 IsMoveAble·MoveType·배치/도구 속성을 요구한다. 이 sprite의 B41 속성 입력이 미확정이라 기본 배치/설비 기능을 확정하지 못함; 기존 admission 유무 때문이 아님. | C113 | M227 |
| Base.Mov_RedBBQ | public / core | review_hold / review_required | scripts/newMoveables.txt:133: Type=Moveable, WorldObjectSprite=appliances_cooking_01_35. InvContextMovable/ISMoveableCursor→ISMoveableSpriteProps.new는 getWorldSprite의 실제 IsMoveAble·MoveType·배치/도구 속성을 요구한다. 이 sprite의 B41 속성 입력이 미확정이라 기본 배치/설비 기능을 확정하지 못함; 기존 admission 유무 때문이 아님. | C113 | M227 |
| Base.Mov_RedChair | public / core | review_hold / review_required | scripts/newMoveables.txt:283: Type=Moveable, WorldObjectSprite=furniture_seating_indoor_01_41. InvContextMovable/ISMoveableCursor→ISMoveableSpriteProps.new는 getWorldSprite의 실제 IsMoveAble·MoveType·배치/도구 속성을 요구한다. 이 sprite의 B41 속성 입력이 미확정이라 기본 배치/설비 기능을 확정하지 못함; 기존 admission 유무 때문이 아님. | C113 | M227 |
| Base.Mov_RedOven | public / core | review_hold / review_required | scripts/newMoveables.txt:173: Type=Moveable, WorldObjectSprite=appliances_cooking_01_9. InvContextMovable/ISMoveableCursor→ISMoveableSpriteProps.new는 getWorldSprite의 실제 IsMoveAble·MoveType·배치/도구 속성을 요구한다. 이 sprite의 B41 속성 입력이 미확정이라 기본 배치/설비 기능을 확정하지 못함; 기존 admission 유무 때문이 아님. | C113 | M227 |
| Base.Mov_RedWoodenChair | public / core | review_hold / review_required | scripts/newMoveables.txt:213: Type=Moveable, WorldObjectSprite=furniture_seating_indoor_02_9. InvContextMovable/ISMoveableCursor→ISMoveableSpriteProps.new는 getWorldSprite의 실제 IsMoveAble·MoveType·배치/도구 속성을 요구한다. 이 sprite의 B41 속성 입력이 미확정이라 기본 배치/설비 기능을 확정하지 못함; 기존 admission 유무 때문이 아님. | C113 | M227 |
| Base.Mov_RoadBarrier | public / core | review_hold / review_required | scripts/newMoveables.txt:633: Type=Moveable, WorldObjectSprite=construction_01_8. InvContextMovable/ISMoveableCursor→ISMoveableSpriteProps.new는 getWorldSprite의 실제 IsMoveAble·MoveType·배치/도구 속성을 요구한다. 이 sprite의 B41 속성 입력이 미확정이라 기본 배치/설비 기능을 확정하지 못함; 기존 admission 유무 때문이 아님. | C113 | M227 |
| Base.Mov_RoadCone | public / core | review_hold / review_required | scripts/newMoveables.txt:1183: Type=Moveable, WorldObjectSprite=street_decoration_01_26. InvContextMovable/ISMoveableCursor→ISMoveableSpriteProps.new는 getWorldSprite의 실제 IsMoveAble·MoveType·배치/도구 속성을 요구한다. 이 sprite의 B41 속성 입력이 미확정이라 기본 배치/설비 기능을 확정하지 못함; 기존 admission 유무 때문이 아님. | C113 | M227 |
| Base.Mov_RoadCone2 | public / core | review_hold / review_required | scripts/newMoveables.txt:1193: Type=Moveable, WorldObjectSprite=street_decoration_01_27. InvContextMovable/ISMoveableCursor→ISMoveableSpriteProps.new는 getWorldSprite의 실제 IsMoveAble·MoveType·배치/도구 속성을 요구한다. 이 sprite의 B41 속성 입력이 미확정이라 기본 배치/설비 기능을 확정하지 못함; 기존 admission 유무 때문이 아님. | C113 | M227 |
| Base.Mov_RoundTable | public / core | review_hold / review_required | scripts/newMoveables.txt:473: Type=Moveable, WorldObjectSprite=furniture_tables_high_01_14. InvContextMovable/ISMoveableCursor→ISMoveableSpriteProps.new는 getWorldSprite의 실제 IsMoveAble·MoveType·배치/도구 속성을 요구한다. 이 sprite의 B41 속성 입력이 미확정이라 기본 배치/설비 기능을 확정하지 못함; 기존 admission 유무 때문이 아님. | C113 | M227 |
| Base.Mov_SatelliteDish | public / core | review_hold / review_required | scripts/newMoveables.txt:1173: Type=Moveable, WorldObjectSprite=appliances_com_01_20. InvContextMovable/ISMoveableCursor→ISMoveableSpriteProps.new는 getWorldSprite의 실제 IsMoveAble·MoveType·배치/도구 속성을 요구한다. 이 sprite의 B41 속성 입력이 미확정이라 기본 배치/설비 기능을 확정하지 못함; 기존 admission 유무 때문이 아님. | C113 | M227 |
| Base.Mov_ScaleMedical | public / core | review_hold / review_required | scripts/newMoveables.txt:723: Type=Moveable, WorldObjectSprite=location_community_medical_01_9. InvContextMovable/ISMoveableCursor→ISMoveableSpriteProps.new는 getWorldSprite의 실제 IsMoveAble·MoveType·배치/도구 속성을 요구한다. 이 sprite의 B41 속성 입력이 미확정이라 기본 배치/설비 기능을 확정하지 못함; 기존 admission 유무 때문이 아님. | C113 | M227 |
| Base.Mov_ShoppingBaskets | public / core | review_hold / review_required | scripts/newMoveables.txt:1133: Type=Moveable, WorldObjectSprite=location_shop_greenes_01_37. InvContextMovable/ISMoveableCursor→ISMoveableSpriteProps.new는 getWorldSprite의 실제 IsMoveAble·MoveType·배치/도구 속성을 요구한다. 이 sprite의 B41 속성 입력이 미확정이라 기본 배치/설비 기능을 확정하지 못함; 기존 admission 유무 때문이 아님. | C113 | M227 |
| Base.Mov_SignArmy | public / core | review_hold / review_required | scripts/newMoveables.txt:933: Type=Moveable, WorldObjectSprite=location_military_generic_01_18. InvContextMovable/ISMoveableCursor→ISMoveableSpriteProps.new는 getWorldSprite의 실제 IsMoveAble·MoveType·배치/도구 속성을 요구한다. 이 sprite의 B41 속성 입력이 미확정이라 기본 배치/설비 기능을 확정하지 못함; 기존 admission 유무 때문이 아님. | C113 | M227 |
| Base.Mov_SignCitrus | public / core | review_hold / review_required | scripts/newMoveables.txt:923: Type=Moveable, WorldObjectSprite=location_shop_accessories_01_27. InvContextMovable/ISMoveableCursor→ISMoveableSpriteProps.new는 getWorldSprite의 실제 IsMoveAble·MoveType·배치/도구 속성을 요구한다. 이 sprite의 B41 속성 입력이 미확정이라 기본 배치/설비 기능을 확정하지 못함; 기존 admission 유무 때문이 아님. | C113 | M227 |
| Base.Mov_SignRestricted | public / core | review_hold / review_required | scripts/newMoveables.txt:943: Type=Moveable, WorldObjectSprite=location_military_generic_01_19. InvContextMovable/ISMoveableCursor→ISMoveableSpriteProps.new는 getWorldSprite의 실제 IsMoveAble·MoveType·배치/도구 속성을 요구한다. 이 sprite의 B41 속성 입력이 미확정이라 기본 배치/설비 기능을 확정하지 못함; 기존 admission 유무 때문이 아님. | C113 | M227 |
| Base.Mov_SignWarning | public / core | review_hold / review_required | scripts/newMoveables.txt:953: Type=Moveable, WorldObjectSprite=location_military_generic_01_21. InvContextMovable/ISMoveableCursor→ISMoveableSpriteProps.new는 getWorldSprite의 실제 IsMoveAble·MoveType·배치/도구 속성을 요구한다. 이 sprite의 B41 속성 입력이 미확정이라 기본 배치/설비 기능을 확정하지 못함; 기존 admission 유무 때문이 아님. | C113 | M227 |
| Base.Mov_SmallTable | public / core | review_hold / review_required | scripts/newMoveables.txt:433: Type=Moveable, WorldObjectSprite=furniture_storage_01_52. InvContextMovable/ISMoveableCursor→ISMoveableSpriteProps.new는 getWorldSprite의 실제 IsMoveAble·MoveType·배치/도구 속성을 요구한다. 이 sprite의 B41 속성 입력이 미확정이라 기본 배치/설비 기능을 확정하지 못함; 기존 admission 유무 때문이 아님. | C113 | M227 |
| Base.Mov_SodaMachine | public / core | review_hold / review_required | scripts/newMoveables.txt:1267: Type=Moveable, WorldObjectSprite=location_shop_accessories_01_8. InvContextMovable/ISMoveableCursor→ISMoveableSpriteProps.new는 getWorldSprite의 실제 IsMoveAble·MoveType·배치/도구 속성을 요구한다. 이 sprite의 B41 속성 입력이 미확정이라 기본 배치/설비 기능을 확정하지 못함; 기존 admission 유무 때문이 아님. | C113 | M227 |
| Base.Mov_TVCamera | public / core | review_hold / review_required | scripts/newMoveables.txt:673: Type=Moveable, WorldObjectSprite=appliances_com_01_44. InvContextMovable/ISMoveableCursor→ISMoveableSpriteProps.new는 getWorldSprite의 실제 IsMoveAble·MoveType·배치/도구 속성을 요구한다. 이 sprite의 B41 속성 입력이 미확정이라 기본 배치/설비 기능을 확정하지 못함; 기존 admission 유무 때문이 아님. | C113 | M227 |
| Base.Mov_Toaster | public / core | review_hold / review_required | scripts/newitems.txt:4458: Type=Moveable, WorldObjectSprite=appliances_cooking_01_32. InvContextMovable/ISMoveableCursor→ISMoveableSpriteProps.new는 getWorldSprite의 실제 IsMoveAble·MoveType·배치/도구 속성을 요구한다. 이 sprite의 B41 속성 입력이 미확정이라 기본 배치/설비 기능을 확정하지 못함; 기존 admission 유무 때문이 아님. | C113 | M227 |
| Base.Mov_TowelDispenser | public / core | review_hold / review_required | scripts/newMoveables.txt:1043: Type=Moveable, WorldObjectSprite=fixtures_bathroom_01_16. InvContextMovable/ISMoveableCursor→ISMoveableSpriteProps.new는 getWorldSprite의 실제 IsMoveAble·MoveType·배치/도구 속성을 요구한다. 이 sprite의 B41 속성 입력이 미확정이라 기본 배치/설비 기능을 확정하지 못함; 기존 admission 유무 때문이 아님. | C113 | M227 |
| Base.Mov_Urinal | public / core | review_hold / review_required | scripts/newMoveables.txt:1053: Type=Moveable, WorldObjectSprite=fixtures_bathroom_01_8. InvContextMovable/ISMoveableCursor→ISMoveableSpriteProps.new는 getWorldSprite의 실제 IsMoveAble·MoveType·배치/도구 속성을 요구한다. 이 sprite의 B41 속성 입력이 미확정이라 기본 배치/설비 기능을 확정하지 못함; 기존 admission 유무 때문이 아님. | C113 | M227 |
| Base.Mov_WallClock | public / core | review_hold / review_required | scripts/newMoveables.txt:703: Type=Moveable, WorldObjectSprite=location_community_school_01_32. InvContextMovable/ISMoveableCursor→ISMoveableSpriteProps.new는 getWorldSprite의 실제 IsMoveAble·MoveType·배치/도구 속성을 요구한다. 이 sprite의 B41 속성 입력이 미확정이라 기본 배치/설비 기능을 확정하지 못함; 기존 admission 유무 때문이 아님. | C113 | M227 |
| Base.Mov_WaterDispenser | public / core | review_hold / review_required | scripts/newMoveables.txt:1287: Type=Moveable, WorldObjectSprite=location_business_office_generic_01_49. InvContextMovable/ISMoveableCursor→ISMoveableSpriteProps.new는 getWorldSprite의 실제 IsMoveAble·MoveType·배치/도구 속성을 요구한다. 이 sprite의 B41 속성 입력이 미확정이라 기본 배치/설비 기능을 확정하지 못함; 기존 admission 유무 때문이 아님. | C113 | M227 |
| Base.Mov_WhiteComfyChair | public / core | review_hold / review_required | scripts/newMoveables.txt:313: Type=Moveable, WorldObjectSprite=furniture_seating_indoor_02_20. InvContextMovable/ISMoveableCursor→ISMoveableSpriteProps.new는 getWorldSprite의 실제 IsMoveAble·MoveType·배치/도구 속성을 요구한다. 이 sprite의 B41 속성 입력이 미확정이라 기본 배치/설비 기능을 확정하지 못함; 기존 admission 유무 때문이 아님. | C113 | M227 |
| Base.Mov_WhiteSimpleChair | public / core | review_hold / review_required | scripts/newMoveables.txt:233: Type=Moveable, WorldObjectSprite=furniture_seating_indoor_03_57. InvContextMovable/ISMoveableCursor→ISMoveableSpriteProps.new는 getWorldSprite의 실제 IsMoveAble·MoveType·배치/도구 속성을 요구한다. 이 sprite의 B41 속성 입력이 미확정이라 기본 배치/설비 기능을 확정하지 못함; 기존 admission 유무 때문이 아님. | C113 | M227 |
| Base.Mov_WhiteSink | public / core | review_hold / review_required | scripts/newMoveables.txt:113: Type=Moveable, WorldObjectSprite=fixtures_sinks_01_12. InvContextMovable/ISMoveableCursor→ISMoveableSpriteProps.new는 getWorldSprite의 실제 IsMoveAble·MoveType·배치/도구 속성을 요구한다. 이 sprite의 B41 속성 입력이 미확정이라 기본 배치/설비 기능을 확정하지 못함; 기존 admission 유무 때문이 아님. | C113 | M227 |
| Base.Mov_WhiteWoodenChair | public / core | review_hold / review_required | scripts/newMoveables.txt:223: Type=Moveable, WorldObjectSprite=furniture_seating_indoor_02_56. InvContextMovable/ISMoveableCursor→ISMoveableSpriteProps.new는 getWorldSprite의 실제 IsMoveAble·MoveType·배치/도구 속성을 요구한다. 이 sprite의 B41 속성 입력이 미확정이라 기본 배치/설비 기능을 확정하지 못함; 기존 admission 유무 때문이 아님. | C113 | M227 |
| Base.Mov_WoodenChair | public / core | review_hold / review_required | scripts/newMoveables.txt:183: Type=Moveable, WorldObjectSprite=furniture_seating_indoor_02_5. InvContextMovable/ISMoveableCursor→ISMoveableSpriteProps.new는 getWorldSprite의 실제 IsMoveAble·MoveType·배치/도구 속성을 요구한다. 이 sprite의 B41 속성 입력이 미확정이라 기본 배치/설비 기능을 확정하지 못함; 기존 admission 유무 때문이 아님. | C113 | M227 |
| Base.Mov_WoodenStool | public / core | review_hold / review_required | scripts/newMoveables.txt:33: Type=Moveable, WorldObjectSprite=location_restaurant_bar_01_26. InvContextMovable/ISMoveableCursor→ISMoveableSpriteProps.new는 getWorldSprite의 실제 IsMoveAble·MoveType·배치/도구 속성을 요구한다. 이 sprite의 B41 속성 입력이 미확정이라 기본 배치/설비 기능을 확정하지 못함; 기존 admission 유무 때문이 아님. | C113 | M227 |
| Base.Mov_YellowModernChair | public / core | review_hold / review_required | scripts/newMoveables.txt:353: Type=Moveable, WorldObjectSprite=furniture_seating_indoor_03_28. InvContextMovable/ISMoveableCursor→ISMoveableSpriteProps.new는 getWorldSprite의 실제 IsMoveAble·MoveType·배치/도구 속성을 요구한다. 이 sprite의 B41 속성 입력이 미확정이라 기본 배치/설비 기능을 확정하지 못함; 기존 admission 유무 때문이 아님. | C113 | M227 |
| Base.MuffinFruit | public / core | revise / description_ready | scripts/items_food.txt:6521의 exact H=-7, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C012 | M012 |
| Base.MuffinGeneric | public / core | revise / description_ready | scripts/items_food.txt:6539의 exact H=-7, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C012 | M012 |
| Base.MuffinTray | public / no-core | revise / description_ready | scripts/newitems.txt:4689; recipes.txt:3985 Prepare Muffins destroy input. | C125 | M011 |
| Base.Muffintray_Biscuit | public / no-core | revise / description_ready | undefined; scripts/recipes.txt:1027 Get 6 Biscuits→Biscuit6; recipecode.lua:1390 cooked 또는 burnt, OnCreate 틀 회수. CantEat 직접 섭취 주장은 계속 제외. | C233 | M228 |
| Base.MugRed | public / no-core | revise / description_ready | scripts/items.txt:272: CanStoreWater=TRUE, ReplaceOnUseOn=WaterSource-WaterMugRed. §빈 물 용기와 같은 exact 물 저장/전환 사실을 재사용하며 음용 안전성·현재 내용물은 추정하지 않는다. | C038 | M041 |
| Base.MugSpiffo | public / no-core | revise / description_ready | scripts/items.txt:302: CanStoreWater=TRUE, ReplaceOnUseOn=WaterSource-WaterMugSpiffo. §빈 물 용기와 같은 exact 물 저장/전환 사실을 재사용하며 음용 안전성·현재 내용물은 추정하지 않는다. | C038 | M041 |
| Base.MugWhite | public / no-core | revise / description_ready | scripts/items.txt:287: CanStoreWater=TRUE, ReplaceOnUseOn=WaterSource-WaterMugWhite. §빈 물 용기와 같은 exact 물 저장/전환 사실을 재사용하며 음용 안전성·현재 내용물은 추정하지 않는다. | C038 | M041 |
| Base.Mugfull | public / no-core | revise / description_ready | scripts/items_food.txt:3472의 exact H=-5, T=-50; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C061 | M012 |
| Base.Mugl | public / no-core | revise / description_ready | scripts/items.txt:257: CanStoreWater=TRUE, ReplaceOnUseOn=WaterSource-WaterMug. §빈 물 용기와 같은 exact 물 저장/전환 사실을 재사용하며 음용 안전성·현재 내용물은 추정하지 않는다. | C038 | M041 |
| Base.MuldraughMap | public / no-core | keep / acquisition_only | scripts/newitems.txt:1213; Map=MuldraughMap; ISMap.lua:321 + ISMapDefinitions.lua:257/267–451의 해당 Init. 지역 지도 확인 목적이 구체적이며 유지 가능. | C046 | M055 |
| Base.MushroomGeneric1 | public / core | revise / description_ready | scripts/items_food.txt:839의 exact H=-13, T=-1; EvolvedRecipe 재료 선언 확인; OnEat_WildFoodGeneric와 recipecode:1041의 실제 독성 분기. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C039 | M004 |
| Base.MushroomGeneric2 | public / core | revise / description_ready | scripts/items_food.txt:862의 exact H=-13, T=-1; EvolvedRecipe 재료 선언 확인; OnEat_WildFoodGeneric와 recipecode:1041의 실제 독성 분기. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C039 | M004 |
| Base.MushroomGeneric3 | public / core | revise / description_ready | scripts/items_food.txt:885의 exact H=-15, T=-1; EvolvedRecipe 재료 선언 확인; OnEat_WildFoodGeneric와 recipecode:1041의 실제 독성 분기. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C039 | M004 |
| Base.MushroomGeneric4 | public / core | revise / description_ready | scripts/items_food.txt:908의 exact H=-13, T=-1; EvolvedRecipe 재료 선언 확인; OnEat_WildFoodGeneric와 recipecode:1041의 실제 독성 분기. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C039 | M004 |
| Base.MushroomGeneric5 | public / core | revise / description_ready | scripts/items_food.txt:931의 exact H=-15, T=-1; EvolvedRecipe 재료 선언 확인; OnEat_WildFoodGeneric와 recipecode:1041의 실제 독성 분기. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C039 | M004 |
| Base.MushroomGeneric6 | public / core | revise / description_ready | scripts/items_food.txt:954의 exact H=-13, T=-1; EvolvedRecipe 재료 선언 확인; OnEat_WildFoodGeneric와 recipecode:1041의 실제 독성 분기. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C039 | M004 |
| Base.MushroomGeneric7 | public / core | revise / description_ready | scripts/items_food.txt:977의 exact H=-13, T=-1; EvolvedRecipe 재료 선언 확인; OnEat_WildFoodGeneric와 recipecode:1041의 실제 독성 분기. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C039 | M004 |
| Base.Mustard | public / core | revise / description_ready | scripts/items_food.txt:5281의 exact H=-20, T=미선언; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C004 | M004 |
| Base.MuttonChop | public / core | revise / description_ready | scripts/items_food.txt:2075의 exact H=-30, T=미선언; EvolvedRecipe 재료 선언 확인; DangerousUncooked=TRUE. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C063 | M004 |
| Base.Nails | public / core | keep / description_ready | 못을 쓰는 목공/제작 재료라는 현재 승인 용도가 명확하다. 개별 제작물·수량은 본문에 나열하지 않는다. | C003 | M144 |
| Base.NailsBox | public / core | keep / description_ready | 못 상자 개봉 input/result와 현재 개봉 용도가 일치한다. | C003 | M056 |
| Base.NecklaceLong_Amber | public / core | keep / description_ready | scripts/clothing/clothing_jewellery.txt:207의 Clothing/BodyLocation=Necklace_Long와 현재 착용 목적 일치. 수치 추가나 감염/위장 효과를 강제하지 않는다. | C018 | M018 |
| Base.NecklaceLong_Gold | public / no-core | revise / description_ready | scripts/clothing/clothing_jewellery.txt:135: Clothing/BodyLocation=Necklace_Long. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C208 | M017 |
| Base.NecklaceLong_GoldDiamond | public / no-core | revise / description_ready | scripts/clothing/clothing_jewellery.txt:147: Clothing/BodyLocation=Necklace_Long. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C208 | M017 |
| Base.NecklaceLong_Silver | public / no-core | revise / description_ready | scripts/clothing/clothing_jewellery.txt:159: Clothing/BodyLocation=Necklace_Long. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C208 | M017 |
| Base.NecklaceLong_SilverDiamond | public / no-core | revise / description_ready | scripts/clothing/clothing_jewellery.txt:195: Clothing/BodyLocation=Necklace_Long. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C208 | M017 |
| Base.NecklaceLong_SilverEmerald | public / no-core | revise / description_ready | scripts/clothing/clothing_jewellery.txt:171: Clothing/BodyLocation=Necklace_Long. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C208 | M017 |
| Base.NecklaceLong_SilverSapphire | public / no-core | revise / description_ready | scripts/clothing/clothing_jewellery.txt:183: Clothing/BodyLocation=Necklace_Long. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C208 | M017 |
| Base.Necklace_Choker | public / no-core | revise / description_ready | scripts/clothing/clothing_jewellery.txt:219: Clothing/BodyLocation=Neck. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C209 | M017 |
| Base.Necklace_Choker_Amber | public / no-core | revise / description_ready | scripts/clothing/clothing_jewellery.txt:243: Clothing/BodyLocation=Neck. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C209 | M017 |
| Base.Necklace_Choker_Diamond | public / no-core | revise / description_ready | scripts/clothing/clothing_jewellery.txt:255: Clothing/BodyLocation=Neck. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C209 | M017 |
| Base.Necklace_Choker_Sapphire | public / no-core | revise / description_ready | scripts/clothing/clothing_jewellery.txt:231: Clothing/BodyLocation=Neck. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C209 | M017 |
| Base.Necklace_Crucifix | public / no-core | revise / description_ready | scripts/clothing/clothing_jewellery.txt:99: Clothing/BodyLocation=Necklace. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C210 | M017 |
| Base.Necklace_DogTag | public / no-core | revise / description_ready | scripts/clothing/clothing_jewellery.txt:3: Clothing/BodyLocation=Necklace. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C210 | M017 |
| Base.Necklace_Gold | public / no-core | revise / description_ready | scripts/clothing/clothing_jewellery.txt:15: Clothing/BodyLocation=Necklace. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C210 | M017 |
| Base.Necklace_GoldDiamond | public / no-core | revise / description_ready | scripts/clothing/clothing_jewellery.txt:39: Clothing/BodyLocation=Necklace. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C210 | M017 |
| Base.Necklace_GoldRuby | public / no-core | revise / description_ready | scripts/clothing/clothing_jewellery.txt:27: Clothing/BodyLocation=Necklace. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C210 | M017 |
| Base.Necklace_Pearl | public / no-core | revise / description_ready | scripts/clothing/clothing_jewellery.txt:123: Clothing/BodyLocation=Necklace. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C210 | M017 |
| Base.Necklace_Silver | public / no-core | revise / description_ready | scripts/clothing/clothing_jewellery.txt:51: Clothing/BodyLocation=Necklace. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C210 | M017 |
| Base.Necklace_SilverCrucifix | public / no-core | revise / description_ready | scripts/clothing/clothing_jewellery.txt:75: Clothing/BodyLocation=Necklace. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C210 | M017 |
| Base.Necklace_SilverDiamond | public / no-core | revise / description_ready | scripts/clothing/clothing_jewellery.txt:87: Clothing/BodyLocation=Necklace. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C210 | M017 |
| Base.Necklace_SilverSapphire | public / no-core | revise / description_ready | scripts/clothing/clothing_jewellery.txt:63: Clothing/BodyLocation=Necklace. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C210 | M017 |
| Base.Necklace_YingYang | public / no-core | revise / description_ready | scripts/clothing/clothing_jewellery.txt:111: Clothing/BodyLocation=Necklace. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C210 | M017 |
| Base.Necklacepearl | public / no-core | review_hold / review_required | scripts/newitems.txt:1006: exact Type=Normal, OBSOLETE=TRUE. 정상 B41에서 이 exact item의 생성·사용 가능성/등록이 미확정이다. 작동하는 별도 FullType으로 대체하거나 기존 no-core 때문에 보류하는 것이 아님. | C076 | M221 |
| Base.Needle | public / core | keep / description_ready | SewingNeedle tag와 기존 승인 재봉 용도를 유지한다. | C003 | M145 |
| Base.Nettles | public / core | revise / description_ready | scripts/items_food.txt:8683의 exact H=-4, T=미선언; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C004 | M004 |
| Base.Newspaper | public / core | revise / description_ready | §후속 item별 판정: exact 읽기 효과 선언 또는 CanBeWrite/페이지·필기구 조건을 구분했다. | C044 | M051 |
| Base.Nightstick | public / no-core | keep / acquisition_only | 각 exact Weapon의 근접 전투 역할이 현재 기본 목적과 일치한다. identity_fallback인 행은 그대로 S2 core로 승격하지 않는다. | C003 | M034 |
| Base.NoiseMaker | public / core | review_hold / review_required | :: exact 원본 item 선언이 미결속이다. NoiseTrap 또는 다른 이름의 장치로 대체하지 않는다. 필요한 입력은 해당 exact casing/namespace의 원본 선언 또는 기존 lineage가 인정하는 명시적 identity 귀속이다. 비슷한 이름을 임의 alias로 채택하지 않음. | C002 | M146 |
| Base.NoiseTrap | public / core | revise / description_ready | scripts/newitems.txt:3481의 exact NoiseRange=17/NoiseDuration=30/CanBeReused. 원격/센서/타이머는 각 선언대로 별도 조건이며 모든 장치를 같은 투척/폭발 효과로 묶지 않는다. Java 내부·PZ 실제 효과는 미관찰. | C126 | M005 |
| Base.NoiseTrapRemote | public / no-core | revise / description_ready | scripts/newitems.txt:3620의 exact NoiseRange=17/NoiseDuration=30/CanBeReused. 원격/센서/타이머는 각 선언대로 별도 조건이며 모든 장치를 같은 투척/폭발 효과로 묶지 않는다. Java 내부·PZ 실제 효과는 미관찰. | C126 | M005 |
| Base.NoiseTrapSensorV1 | public / no-core | revise / description_ready | scripts/newitems.txt:3536의 exact NoiseRange=17/NoiseDuration=30/CanBeReused. 원격/센서/타이머는 각 선언대로 별도 조건이며 모든 장치를 같은 투척/폭발 효과로 묶지 않는다. Java 내부·PZ 실제 효과는 미관찰. | C126 | M005 |
| Base.NoiseTrapSensorV2 | public / no-core | revise / description_ready | scripts/newitems.txt:3564의 exact NoiseRange=17/NoiseDuration=30/CanBeReused. 원격/센서/타이머는 각 선언대로 별도 조건이며 모든 장치를 같은 투척/폭발 효과로 묶지 않는다. Java 내부·PZ 실제 효과는 미관찰. | C126 | M005 |
| Base.NoiseTrapSensorV3 | public / no-core | revise / description_ready | scripts/newitems.txt:3592의 exact NoiseRange=17/NoiseDuration=30/CanBeReused. 원격/센서/타이머는 각 선언대로 별도 조건이며 모든 장치를 같은 투척/폭발 효과로 묶지 않는다. Java 내부·PZ 실제 효과는 미관찰. | C126 | M005 |
| Base.NoiseTrapTriggered | public / no-core | revise / description_ready | scripts/newitems.txt:3509의 exact NoiseRange=17/NoiseDuration=30/CanBeReused. 원격/센서/타이머는 각 선언대로 별도 조건이며 모든 장치를 같은 투척/폭발 효과로 묶지 않는다. Java 내부·PZ 실제 효과는 미관찰. | C126 | M005 |
| Base.NoodleSoup | public / core | revise / description_ready | scripts/items_food.txt:6557의 exact H=-10, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C012 | M012 |
| Base.NormalBrake1 | public / core | revise / description_ready | scripts/vehicles/vehiclesitems.txt:252; template_brake 및 exact brakeForce 선언. 현재 일반 구동 복구 문구를 제동 역할로 특정 | C118 | M139 |
| Base.NormalBrake2 | public / core | revise / description_ready | scripts/vehicles/vehiclesitems.txt:300; template_brake 및 exact brakeForce 선언. 현재 일반 구동 복구 문구를 제동 역할로 특정 | C118 | M140 |
| Base.NormalBrake3 | public / core | revise / description_ready | scripts/vehicles/vehiclesitems.txt:348; template_brake 및 exact brakeForce 선언. 현재 일반 구동 복구 문구를 제동 역할로 특정 | C118 | M141 |
| Base.NormalCarMuffler1 | public / core | revise / description_ready | scripts/vehicles/vehiclesitems.txt:1374; template_muffler 및 exact EngineLoudness 선언. 모든 형식이 같은 양만큼 소음을 줄인다고 하지 않음 | C119 | M139 |
| Base.NormalCarMuffler2 | public / core | revise / description_ready | scripts/vehicles/vehiclesitems.txt:1422; template_muffler 및 exact EngineLoudness 선언. 모든 형식이 같은 양만큼 소음을 줄인다고 하지 않음 | C119 | M140 |
| Base.NormalCarMuffler3 | public / core | revise / description_ready | scripts/vehicles/vehiclesitems.txt:1470; template_muffler 및 exact EngineLoudness 선언. 모든 형식이 같은 양만큼 소음을 줄인다고 하지 않음 | C119 | M141 |
| Base.NormalCarSeat1 | public / core | revise / description_ready | scripts/vehicles/vehiclesitems.txt:1312; exact VehicleType=1/MaxCapacity와 seat/trunk container 선언. 수납 부품을 모두 자유롭게 탈착 가능한 물건으로 묶지 않는다. | C127 | M046 |
| Base.NormalCarSeat2 | public / core | revise / description_ready | scripts/vehicles/vehiclesitems.txt:1327; exact VehicleType=2/MaxCapacity와 seat/trunk container 선언. 수납 부품을 모두 자유롭게 탈착 가능한 물건으로 묶지 않는다. | C127 | M046 |
| Base.NormalCarSeat3 | public / core | revise / description_ready | scripts/vehicles/vehiclesitems.txt:1342; exact VehicleType=3/MaxCapacity와 seat/trunk container 선언. 수납 부품을 모두 자유롭게 탈착 가능한 물건으로 묶지 않는다. | C127 | M046 |
| Base.NormalGasTank1 | public / core | revise / description_ready | scripts/vehicles/vehiclesitems.txt:507; exact VehicleType=1/MaxCapacity, template_gastank의 Gasoline container·conditionAffectsCapacity. 1/2/3을 성능 등급으로 보지 않는다. | C040 | M045 |
| Base.NormalGasTank2 | public / core | revise / description_ready | scripts/vehicles/vehiclesitems.txt:555; exact VehicleType=2/MaxCapacity, template_gastank의 Gasoline container·conditionAffectsCapacity. 1/2/3을 성능 등급으로 보지 않는다. | C040 | M045 |
| Base.NormalGasTank3 | public / core | revise / description_ready | scripts/vehicles/vehiclesitems.txt:603; exact VehicleType=3/MaxCapacity, template_gastank의 Gasoline container·conditionAffectsCapacity. 1/2/3을 성능 등급으로 보지 않는다. | C040 | M045 |
| Base.NormalSuspension1 | public / core | revise / description_ready | scripts/vehicles/vehiclesitems.txt:382; template_suspension 및 SuspensionDamping/Compression, Vehicles.Update.Suspension. 엔진/구동 복구 보장을 제거하고 교체 부위를 특정 | C120 | M139 |
| Base.NormalSuspension2 | public / core | revise / description_ready | scripts/vehicles/vehiclesitems.txt:418; template_suspension 및 SuspensionDamping/Compression, Vehicles.Update.Suspension. 엔진/구동 복구 보장을 제거하고 교체 부위를 특정 | C120 | M140 |
| Base.NormalSuspension3 | public / core | revise / description_ready | scripts/vehicles/vehiclesitems.txt:454; template_suspension 및 SuspensionDamping/Compression, Vehicles.Update.Suspension. 엔진/구동 복구 보장을 제거하고 교체 부위를 특정 | C120 | M141 |
| Base.NormalTire1 | public / core | revise / description_ready | scripts/vehicles/vehiclesitems.txt:92; template_tire 및 exact WheelFriction, Vehicles.Update.Tire의 공기/상태 분기. 정상 주행이나 고정 성능을 보장하지 않음 | C121 | M139 |
| Base.NormalTire2 | public / core | revise / description_ready | scripts/vehicles/vehiclesitems.txt:146; template_tire 및 exact WheelFriction, Vehicles.Update.Tire의 공기/상태 분기. 정상 주행이나 고정 성능을 보장하지 않음 | C121 | M140 |
| Base.NormalTire3 | public / core | revise / description_ready | scripts/vehicles/vehiclesitems.txt:200; template_tire 및 exact WheelFriction, Vehicles.Update.Tire의 공기/상태 분기. 정상 주행이나 고정 성능을 보장하지 않음 | C121 | M141 |
| Base.NormalTrunk1 | public / core | revise / description_ready | scripts/vehicles/vehiclesitems.txt:709; exact VehicleType=1/MaxCapacity와 seat/trunk container 선언. 수납 부품을 모두 자유롭게 탈착 가능한 물건으로 묶지 않는다. | C041 | M046 |
| Base.NormalTrunk2 | public / core | revise / description_ready | scripts/vehicles/vehiclesitems.txt:769; exact VehicleType=2/MaxCapacity와 seat/trunk container 선언. 수납 부품을 모두 자유롭게 탈착 가능한 물건으로 묶지 않는다. | C041 | M046 |
| Base.NormalTrunk3 | public / core | revise / description_ready | scripts/vehicles/vehiclesitems.txt:814; exact VehicleType=3/MaxCapacity와 seat/trunk container 선언. 수납 부품을 모두 자유롭게 탈착 가능한 물건으로 묶지 않는다. | C041 | M046 |
| Base.NoseRing_Gold | public / no-core | revise / description_ready | scripts/clothing/clothing_jewellery.txt:267: Clothing/BodyLocation=Nose. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C211 | M017 |
| Base.NoseRing_Silver | public / no-core | revise / description_ready | scripts/clothing/clothing_jewellery.txt:279: Clothing/BodyLocation=Nose. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C211 | M017 |
| Base.NoseStud_Gold | public / no-core | revise / description_ready | scripts/clothing/clothing_jewellery.txt:291: Clothing/BodyLocation=Nose. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C211 | M017 |
| Base.NoseStud_Silver | public / core | keep / description_ready | scripts/clothing/clothing_jewellery.txt:303의 Clothing/BodyLocation=Nose와 현재 착용 목적 일치. 수치 추가나 감염/위장 효과를 강제하지 않는다. | C018 | M018 |
| Base.Notebook | empty / no-core | revise / description_ready | scripts/items_literature.txt:1277: items_literature:1277/1367의 exact CanBeWrite, §기록물의 기존 필기구·잠금/페이지 저장 경로 재사용. | C128 | M147 |
| Base.Oatmeal | public / no-core | revise / description_ready | scripts/items_food.txt:5076의 exact H=-8, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C012 | M012 |
| Base.OatsRaw | public / core | revise / description_ready | scripts/items_food.txt:5343의 exact H=-50, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C012 | M012 |
| Base.OilOlive | public / core | revise / description_ready | scripts/items_food.txt:6581의 exact H=-30, T=미선언; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C004 | M004 |
| Base.OilVegetable | public / core | revise / description_ready | scripts/items_food.txt:6603의 exact H=-30, T=미선언; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C004 | M004 |
| Base.OldBrake1 | public / core | revise / description_ready | scripts/vehicles/vehiclesitems.txt:236; template_brake 및 exact brakeForce 선언. 현재 일반 구동 복구 문구를 제동 역할로 특정 | C118 | M139 |
| Base.OldBrake2 | public / core | revise / description_ready | scripts/vehicles/vehiclesitems.txt:284; template_brake 및 exact brakeForce 선언. 현재 일반 구동 복구 문구를 제동 역할로 특정 | C118 | M140 |
| Base.OldBrake3 | public / core | revise / description_ready | scripts/vehicles/vehiclesitems.txt:332; template_brake 및 exact brakeForce 선언. 현재 일반 구동 복구 문구를 제동 역할로 특정 | C118 | M141 |
| Base.OldCarMuffler1 | public / core | revise / description_ready | scripts/vehicles/vehiclesitems.txt:1358; template_muffler 및 exact EngineLoudness 선언. 모든 형식이 같은 양만큼 소음을 줄인다고 하지 않음 | C119 | M139 |
| Base.OldCarMuffler2 | public / core | revise / description_ready | scripts/vehicles/vehiclesitems.txt:1406; template_muffler 및 exact EngineLoudness 선언. 모든 형식이 같은 양만큼 소음을 줄인다고 하지 않음 | C119 | M140 |
| Base.OldCarMuffler3 | public / core | revise / description_ready | scripts/vehicles/vehiclesitems.txt:1454; template_muffler 및 exact EngineLoudness 선언. 모든 형식이 같은 양만큼 소음을 줄인다고 하지 않음 | C119 | M141 |
| Base.OldTire1 | public / core | revise / description_ready | scripts/vehicles/vehiclesitems.txt:74; template_tire 및 exact WheelFriction, Vehicles.Update.Tire의 공기/상태 분기. 정상 주행이나 고정 성능을 보장하지 않음 | C121 | M139 |
| Base.OldTire2 | public / core | revise / description_ready | scripts/vehicles/vehiclesitems.txt:128; template_tire 및 exact WheelFriction, Vehicles.Update.Tire의 공기/상태 분기. 정상 주행이나 고정 성능을 보장하지 않음 | C121 | M140 |
| Base.OldTire3 | public / core | revise / description_ready | scripts/vehicles/vehiclesitems.txt:182; template_tire 및 exact WheelFriction, Vehicles.Update.Tire의 공기/상태 분기. 정상 주행이나 고정 성능을 보장하지 않음 | C121 | M141 |
| Base.OmeletteRecipe | public / no-core | revise / description_ready | scripts/items_food.txt:7611의 exact H=-14, T=미선언; EvolvedRecipe 재료 선언 확인; DangerousUncooked=true. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C063 | M004 |
| Base.Onigiri | public / core | revise / description_ready | scripts/items_food.txt:6626의 exact H=-10, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C012 | M012 |
| Base.Onion | public / core | revise / description_ready | scripts/items_food.txt:1000의 exact H=-10, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C012 | M012 |
| Base.OnionRings | public / no-core | revise / description_ready | scripts/items_food.txt:7459의 exact H=-5, T=미선언; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C004 | M004 |
| Base.OpenBeans | public / core | revise / description_ready | scripts/items_food.txt:587의 exact H=-24, T=미선언; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C004 | M004 |
| Base.Orange | public / core | revise / description_ready | scripts/items_food.txt:1607의 exact H=-12, T=-8; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C020 | M004 |
| Base.Oregano | public / core | revise / description_ready | scripts/items_food.txt:8571의 exact H=-1, T=미선언; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C004 | M004 |
| Base.OvenMitt | public / core | review_hold / review_required | scripts/newitems.txt:4700; Normal 선언은 확인되나 exact 사용/조리 입력이 미확정; 유사 도구·Teabag2·Flour의 기능 전이 금지. 필요한 추가 근거는 이 exact item의 해당 행동/재료 입력 또는 효과를 명시하는 vanilla source 관계이며, current admission 부재를 해소할 승인만으로 대체하지 않음. | C049 | M069 |
| Base.Oysters | public / core | revise / description_ready | scripts/items_food.txt:6643의 exact H=-5, T=미선언; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C004 | M004 |
| Base.OystersFried | public / core | revise / description_ready | scripts/items_food.txt:7393의 exact H=-6, T=미선언; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C004 | M004 |
| Base.Padlock | public / no-core | revise / description_ready | scripts/newitems.txt:2930; ISWorldObjectContextMenu.lua:201/579/3044 canBeLockByPadlock 대상의 설치 action. | C129 | M026 |
| Base.Painauchocolat | public / core | revise / description_ready | scripts/items_food.txt:7967의 exact H=-2, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C012 | M012 |
| Base.PaintBlack | public / no-core | keep / acquisition_only | scripts/items.txt:876; ISPaintMenu.lua:9–23 PaintMenuItems의 exact 색상, paintbrush/paintable 조건 및 ISPaintAction. 칠하기/표식이라는 현행 목적 유지. | C046 | M055 |
| Base.PaintBlue | public / no-core | keep / acquisition_only | scripts/items.txt:891; ISPaintMenu.lua:9–23 PaintMenuItems의 exact 색상, paintbrush/paintable 조건 및 ISPaintAction. 칠하기/표식이라는 현행 목적 유지. | C046 | M055 |
| Base.PaintBrown | public / no-core | keep / acquisition_only | scripts/items.txt:906; ISPaintMenu.lua:9–23 PaintMenuItems의 exact 색상, paintbrush/paintable 조건 및 ISPaintAction. 칠하기/표식이라는 현행 목적 유지. | C046 | M055 |
| Base.PaintCyan | public / no-core | keep / acquisition_only | scripts/items.txt:921; ISPaintMenu.lua:9–23 PaintMenuItems의 exact 색상, paintbrush/paintable 조건 및 ISPaintAction. 칠하기/표식이라는 현행 목적 유지. | C046 | M055 |
| Base.PaintGreen | public / no-core | keep / acquisition_only | scripts/items.txt:936; ISPaintMenu.lua:9–23 PaintMenuItems의 exact 색상, paintbrush/paintable 조건 및 ISPaintAction. 칠하기/표식이라는 현행 목적 유지. | C046 | M055 |
| Base.PaintGrey | public / no-core | keep / acquisition_only | scripts/items.txt:951; ISPaintMenu.lua:9–23 PaintMenuItems의 exact 색상, paintbrush/paintable 조건 및 ISPaintAction. 칠하기/표식이라는 현행 목적 유지. | C046 | M055 |
| Base.PaintLightBlue | public / no-core | keep / acquisition_only | scripts/items.txt:966; ISPaintMenu.lua:9–23 PaintMenuItems의 exact 색상, paintbrush/paintable 조건 및 ISPaintAction. 칠하기/표식이라는 현행 목적 유지. | C046 | M055 |
| Base.PaintLightBrown | public / no-core | keep / acquisition_only | scripts/items.txt:981; ISPaintMenu.lua:9–23 PaintMenuItems의 exact 색상, paintbrush/paintable 조건 및 ISPaintAction. 칠하기/표식이라는 현행 목적 유지. | C046 | M055 |
| Base.PaintOrange | public / no-core | keep / acquisition_only | scripts/items.txt:996; ISPaintMenu.lua:9–23 PaintMenuItems의 exact 색상, paintbrush/paintable 조건 및 ISPaintAction. 칠하기/표식이라는 현행 목적 유지. | C046 | M055 |
| Base.PaintPink | public / no-core | keep / acquisition_only | scripts/items.txt:1011; ISPaintMenu.lua:9–23 PaintMenuItems의 exact 색상, paintbrush/paintable 조건 및 ISPaintAction. 칠하기/표식이라는 현행 목적 유지. | C046 | M055 |
| Base.PaintPurple | public / no-core | keep / acquisition_only | scripts/items.txt:1026; ISPaintMenu.lua:9–23 PaintMenuItems의 exact 색상, paintbrush/paintable 조건 및 ISPaintAction. 칠하기/표식이라는 현행 목적 유지. | C046 | M055 |
| Base.PaintRed | public / no-core | keep / acquisition_only | scripts/items.txt:861; ISPaintMenu.lua:9–23 PaintMenuItems의 exact 색상, paintbrush/paintable 조건 및 ISPaintAction. 칠하기/표식이라는 현행 목적 유지. | C046 | M055 |
| Base.PaintTurquoise | public / no-core | keep / acquisition_only | scripts/items.txt:1041; ISPaintMenu.lua:9–23 PaintMenuItems의 exact 색상, paintbrush/paintable 조건 및 ISPaintAction. 칠하기/표식이라는 현행 목적 유지. | C046 | M055 |
| Base.PaintWhite | public / no-core | keep / acquisition_only | scripts/items.txt:1056; ISPaintMenu.lua:9–23 PaintMenuItems의 exact 색상, paintbrush/paintable 조건 및 ISPaintAction. 칠하기/표식이라는 현행 목적 유지. | C046 | M055 |
| Base.PaintYellow | public / no-core | keep / acquisition_only | scripts/items.txt:1071; ISPaintMenu.lua:9–23 PaintMenuItems의 exact 색상, paintbrush/paintable 조건 및 ISPaintAction. 칠하기/표식이라는 현행 목적 유지. | C046 | M055 |
| Base.Paintbrush | public / core | keep / description_ready | 보호된 Paintbrush의 기존 도색 역할을 유지한다. | C003 | M148 |
| Base.PaintbucketEmpty | public / core | revise / description_ready | scripts/newitems.txt:4037: CanStoreWater=TRUE, ReplaceOnUseOn=WaterSource-WaterPaintbucket. §빈 물 용기와 같은 exact 물 저장/전환 사실을 재사용하며 음용 안전성·현재 내용물은 추정하지 않는다. | C038 | M041 |
| Base.Pan | public / no-core | revise / description_ready | scripts/items_weapons.txt:1236; evolvedrecipes.txt:54/63 BaseItem=Pan→볶음 요리 결과. | C096 | M011 |
| Base.PanFriedVegetables | public / no-core | revise / description_ready | scripts/items_food.txt:5221의 exact H=-10, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C012 | M012 |
| Base.PanFriedVegetables2 | public / no-core | revise / description_ready | scripts/items_food.txt:5241의 exact H=-10, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C012 | M012 |
| Base.PancakeHedgehog | public / core | review_hold / review_required | scripts/newitems.txt:4818; 장난감의 Normal 정체성/원문 locator 확인; 보기·놀이·수집 action 의 실제 사용 경로는 미확정. 유사 매체의 재생·학습 기능을 전이하지 않음. 필요한 추가 근거는 이 exact item의 해당 행동/재료 입력 또는 효과를 명시하는 vanilla source 관계이며, current admission 부재를 해소할 승인만으로 대체하지 않음. | C015 | M054 |
| Base.PancakeMix | public / core | revise / description_ready | §조리 문구 32개: 이 exact item의 input/result/keep 역할과 원본 recipe를 분리 검토했다. | C026 | M027 |
| Base.Pancakes | public / no-core | revise / description_ready | scripts/items_food.txt:3661의 exact H=-16, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C012 | M012 |
| Base.PancakesCraft | public / no-core | revise / description_ready | scripts/items_food.txt:3683의 exact H=-20, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음; ReplaceOnCooked=Base.PancakesRecipe, 다른 상태 item과 구분. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C012 | M012 |
| Base.PancakesRecipe | public / core | revise / description_ready | scripts/items_food.txt:3706의 exact H=-20, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C012 | M012 |
| Base.Panfish | public / core | revise / description_ready | scripts/items_food.txt:1787의 exact H=-15, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음; DangerousUncooked=TRUE. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C032 | M012 |
| Base.PaperBag | public / core | keep / description_ready | scripts/newitems.txt:2125의 exact Container/Capacity=5. 보관·운반 역할이 명확하며 이름에 따른 내용물 제한/냉장 효과는 추가하지 않는다. | C023 | M023 |
| Base.PaperNapkins | public / core | revise / description_ready | scripts/newitems.txt:4732; lua/server/Camping/camping_fuel.lua의 exact PaperNapkins 키가 연료/점화 재료에 모두 등록됨. 앞 절 ISCampingMenu의 유효 연료/점화 선택과 보충·점화 경로 재사용. 청소·게임·결제 등의 미확인 기능과 분리. | C227 | M220 |
| Base.Paperbag_Jays | public / core | keep / description_ready | scripts/newitems.txt:2110의 exact Container/Capacity=5. 보관·운반 역할이 명확하며 이름에 따른 내용물 제한/냉장 효과는 추가하지 않는다. | C023 | M023 |
| Base.Paperbag_Spiffos | public / core | keep / description_ready | scripts/newitems.txt:2095의 exact Container/Capacity=5. 보관·운반 역할이 명확하며 이름에 따른 내용물 제한/냉장 효과는 추가하지 않는다. | C023 | M023 |
| Base.Paperclip | public / core | revise / description_ready | scripts/newitems.txt:1335; recipes:1142–1190의 exact Paperclip input. 현실 문서 정리 기능을 추정하지 않는다. | C130 | M149 |
| Base.PaperclipBox | public / core | revise / description_ready | scripts/newitems.txt:1669; recipes:702의 exact 개봉 input/result. | C131 | M056 |
| Base.Parsley | public / core | revise / description_ready | scripts/items_food.txt:8589의 exact H=-1, T=미선언; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C004 | M004 |
| Base.Pasta | public / core | revise / description_ready | scripts/items_food.txt:4808의 exact H=-60, T=60; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C025 | M012 |
| Base.PastaBowl | public / no-core | revise / description_ready | scripts/items_food.txt:4993의 exact H=-12, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C012 | M012 |
| Base.PastaPan | public / core | revise / description_ready | scripts/items_food.txt:4826; input:Make 2 Bowls of Pasta; input:Make 4 Bowls of Pasta; dynamic Food 내용물 수치는 고정하지 않음; bowls로 나누는 exact 입력 경로. | C132 | M150 |
| Base.PastaPot | public / core | revise / description_ready | scripts/items_food.txt:4915; input:Make 2 Bowls of Pasta; input:Make 4 Bowls of Pasta; dynamic Food 내용물 수치는 고정하지 않음; bowls로 나누는 exact 입력 경로. | C132 | M150 |
| Base.Peach | public / core | revise / description_ready | scripts/items_food.txt:1451의 exact H=-12, T=-5; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C020 | M004 |
| Base.PeanutButter | public / core | revise / description_ready | scripts/items_food.txt:4615의 exact H=-25, T=미선언; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C004 | M004 |
| Base.PeanutButterSandwich | public / core | revise / description_ready | scripts/items_food.txt:4634의 exact H=-17, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C012 | M012 |
| Base.Peanuts | public / core | revise / description_ready | scripts/items_food.txt:4687의 exact H=-8, T=미선언; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C004 | M004 |
| Base.Pear | public / core | revise / description_ready | scripts/items_food.txt:6666의 exact H=-16, T=-7; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C020 | M004 |
| Base.Peas | public / core | revise / description_ready | scripts/items_food.txt:1107의 exact H=-20, T=-5; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C020 | M004 |
| Base.Pen | public / core | revise / description_ready | scripts/items_weapons.txt:4042; exact Write/pen tags, 기존 문서 작성 경로 및 ISWorldMapSymbols:canWrite의 type/tag 선택. | C043 | M049 |
| Base.Pencil | public / core | revise / description_ready | scripts/items_weapons.txt:4087; exact Write/pen tags, 기존 문서 작성 경로 및 ISWorldMapSymbols:canWrite의 type/tag 선택. | C043 | M049 |
| Base.Pepper | public / core | revise / description_ready | scripts/items_food.txt:4348의 exact H=-10, T=20; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C067 | M004 |
| Base.PepperHabanero | public / core | revise / description_ready | scripts/items_food.txt:6687의 exact H=-2, T=미선언; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C004 | M004 |
| Base.PepperJalapeno | public / core | revise / description_ready | scripts/items_food.txt:6707의 exact H=-2, T=미선언; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C004 | M004 |
| Base.Peppermint | public / core | revise / description_ready | scripts/items_food.txt:3815의 exact H=-10, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C012 | M012 |
| Base.Pepperoni | public / core | revise / description_ready | scripts/items_food.txt:6810의 exact H=-20, T=미선언; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C004 | M004 |
| Base.PercedWood | public / no-core | revise / description_ready | scripts/newitems.txt:2399: ISCampingMenu의 PercedWood/TreeBranch/WoodenStick 선택→ISLightFromKindle:update의 lightFire/실패·파손 분기. | C133 | M151 |
| Base.Perch | public / core | revise / description_ready | scripts/items_food.txt:1732의 exact H=-15, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음; DangerousUncooked=TRUE. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C032 | M012 |
| Base.Perfume | public / core | review_hold / review_required | scripts/newitems.txt:615: §남은 혼합 역할: 향수 사용·캐릭터 효과의 exact 게임 경로가 미확인이다. 필요한 추가 근거는 이 exact item의 해당 행동/재료 입력 또는 효과를 명시하는 vanilla source 관계이며, current admission 부재를 해소할 승인만으로 대체하지 않음. | C002 | M077 |
| Base.Perogies | public / core | revise / description_ready | scripts/items_food.txt:7984의 exact H=-7, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C012 | M012 |
| Base.PetrolBleachBottle | public / core | keep / description_ready | scripts/newitems.txt:4964; exact Petrol tag와 현재 연료 운반/급유 역할은 이미 구체적이다. 용기 종류를 물이나 소독제로 해석하지 않는다. | C014 | M152 |
| Base.PetrolCan | public / core | keep / description_ready | scripts/items.txt:1086; exact Petrol tag와 현재 연료 운반/급유 역할은 이미 구체적이다. 용기 종류를 물이나 소독제로 해석하지 않는다. | C014 | M152 |
| Base.PetrolPopBottle | public / core | keep / description_ready | scripts/newitems.txt:4982; exact Petrol tag와 현재 연료 운반/급유 역할은 이미 구체적이다. 용기 종류를 물이나 소독제로 해석하지 않는다. | C014 | M152 |
| Base.PickAxe | public / core | revise / description_ready | scripts/items_weapons.txt:2175; exact DigPlow tag → ISFarmingMenu:20의 not-broken 도구 선택. 다른 작업의 가능/불가능을 추정하지 않는다. | C091 | M104 |
| Base.PickAxeHandle | public / core | keep / description_ready | 각 exact Weapon 선언과 근접 공격 역할을 대조했다. Chainsaw도 작동하는 엔진톱의 벌목 기능을 추가하지 않는다. | C003 | M070 |
| Base.PickAxeHandleSpiked | public / core | keep / description_ready | 각 exact Weapon 선언과 근접 공격 역할을 대조했다. Chainsaw도 작동하는 엔진톱의 벌목 기능을 추가하지 않는다. | C003 | M070 |
| Base.Pickles | public / core | revise / description_ready | scripts/items_food.txt:5670의 exact H=-5, T=미선언; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C004 | M004 |
| Base.Pie | public / core | revise / description_ready | scripts/items_food.txt:4652의 exact H=-30, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C012 | M012 |
| Base.PieApple | public / core | revise / description_ready | scripts/items_food.txt:9395의 exact H=-30, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C012 | M012 |
| Base.PieBlueberry | public / core | revise / description_ready | scripts/items_food.txt:9412의 exact H=-30, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C012 | M012 |
| Base.PieDough | public / core | revise / description_ready | scripts/newitems.txt:1415; recipes.txt:1065 Place Pie in Baking Pan 입력. | C134 | M026 |
| Base.PieKeyLime | public / core | revise / description_ready | scripts/items_food.txt:9429의 exact H=-30, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C012 | M012 |
| Base.PieLemonMeringue | public / core | revise / description_ready | scripts/items_food.txt:9446의 exact H=-30, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C012 | M012 |
| Base.PiePrep | public / no-core | revise / description_ready | scripts/items_food.txt:5018의 exact H=-15, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C012 | M012 |
| Base.PiePumpkin | public / core | revise / description_ready | scripts/items_food.txt:4670의 exact H=-30, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C012 | M012 |
| Base.PieWholeRaw | public / no-core | revise / description_ready | scripts/items_food.txt:5359의 exact H=-15, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C012 | M012 |
| Base.PieWholeRawSweet | public / no-core | revise / description_ready | scripts/items_food.txt:5384의 exact H=-15, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C012 | M012 |
| Base.Pike | public / core | revise / description_ready | scripts/items_food.txt:1814의 exact H=-15, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음; DangerousUncooked=TRUE. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C032 | M012 |
| Base.Pillbug | public / core | revise / description_ready | scripts/items_food.txt:8947의 exact H=-1, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C012 | M012 |
| Base.Pillow | public / core | revise / description_ready | scripts/items.txt:342; recipes.txt:1553–1555 Make Mattress input. | C135 | M064 |
| Base.Pills | public / no-core | revise / description_ready | scripts/items.txt:1147; exact item의 Tooltip_Painkillers 선언→lua/shared/Translate/EN/Tooltip_EN.txt:77 게임 원문 사용 안내. ISInventoryPaneContextMenu:223/674/3046의 Pills 접두 exact 타입→ISTakePillAction.perform의 JustTookPill 호출. 기본 목적의 명시적 게임 안내와 실제 복용 경로를 결속; 수치·발현 시간·성공 보장은 추가하지 않고 엔진 효과 증명으로 범위를 키우지 않음. | C234 | M217 |
| Base.PillsAntiDep | public / no-core | revise / description_ready | scripts/items.txt:1162; exact item의 Tooltip_PillsAntidepressant 선언→lua/shared/Translate/EN/Tooltip_EN.txt:78 게임 원문 사용 안내. ISInventoryPaneContextMenu:223/674/3046의 Pills 접두 exact 타입→ISTakePillAction.perform의 JustTookPill 호출. 기본 목적의 명시적 게임 안내와 실제 복용 경로를 결속; 수치·발현 시간·성공 보장은 추가하지 않고 엔진 효과 증명으로 범위를 키우지 않음. | C235 | M217 |
| Base.PillsBeta | public / no-core | revise / description_ready | scripts/items.txt:1177; exact item의 Tooltip_PillsBetablocker 선언→lua/shared/Translate/EN/Tooltip_EN.txt:79 게임 원문 사용 안내. ISInventoryPaneContextMenu:223/674/3046의 Pills 접두 exact 타입→ISTakePillAction.perform의 JustTookPill 호출. 기본 목적의 명시적 게임 안내와 실제 복용 경로를 결속; 수치·발현 시간·성공 보장은 추가하지 않고 엔진 효과 증명으로 범위를 키우지 않음. | C236 | M217 |
| Base.PillsSleepingTablets | public / no-core | revise / description_ready | scripts/items.txt:1192; exact item의 Tooltip_PillsSleeping 선언→lua/shared/Translate/EN/Tooltip_EN.txt:80 게임 원문 사용 안내. ISInventoryPaneContextMenu:223/674/3046의 Pills 접두 exact 타입→ISTakePillAction.perform의 JustTookPill 호출. 기본 목적의 명시적 게임 안내와 실제 복용 경로를 결속; 수치·발현 시간·성공 보장은 추가하지 않고 엔진 효과 증명으로 범위를 키우지 않음. | C237 | M217 |
| Base.PillsVitamins | public / no-core | revise / description_ready | scripts/newitems.txt:1865; exact item의 Tooltip_Vitamins 선언→lua/shared/Translate/EN/Tooltip_EN.txt:153 게임 원문 사용 안내. ISInventoryPaneContextMenu:223/674/3046의 Pills 접두 exact 타입→ISTakePillAction.perform의 JustTookPill 호출. 기본 목적의 명시적 게임 안내와 실제 복용 경로를 결속; 수치·발현 시간·성공 보장은 추가하지 않고 엔진 효과 증명으로 범위를 키우지 않음. | C238 | M217 |
| Base.Pineapple | public / core | revise / description_ready | scripts/items_food.txt:1473의 exact H=-24, T=-13; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C020 | M004 |
| Base.Pinecone | public / core | revise / description_ready | scripts/newitems.txt:625; camping_fuel.lua:17 Pinecone=.5 및 앞 절 ISCampingMenu.isValidFuel/getFuelDurationForItem→연료 추가 경로. 생물학적 정체성보다 실제 연료 역할. | C239 | M229 |
| Base.Pipe | public / core | keep / description_ready | 보호된 Pipe의 기존 사실·문구/lineage를 유지한다. MetalPipe와 합치지 않는다. | C003 | M155 |
| Base.PipeBomb | public / core | revise / description_ready | scripts/newitems.txt:3713의 exact ExplosionPower=90. 원격/센서/타이머는 각 선언대로 별도 조건이며 모든 장치를 같은 투척/폭발 효과로 묶지 않는다. Java 내부·PZ 실제 효과는 미관찰. | C005 | M005 |
| Base.PipeBombRemote | public / no-core | revise / description_ready | scripts/newitems.txt:3855의 exact ExplosionPower=90. 원격/센서/타이머는 각 선언대로 별도 조건이며 모든 장치를 같은 투척/폭발 효과로 묶지 않는다. Java 내부·PZ 실제 효과는 미관찰. | C005 | M005 |
| Base.PipeBombSensorV1 | public / no-core | revise / description_ready | scripts/newitems.txt:3768의 exact ExplosionPower=90. 원격/센서/타이머는 각 선언대로 별도 조건이며 모든 장치를 같은 투척/폭발 효과로 묶지 않는다. Java 내부·PZ 실제 효과는 미관찰. | C005 | M005 |
| Base.PipeBombSensorV2 | public / no-core | revise / description_ready | scripts/newitems.txt:3797의 exact ExplosionPower=90. 원격/센서/타이머는 각 선언대로 별도 조건이며 모든 장치를 같은 투척/폭발 효과로 묶지 않는다. Java 내부·PZ 실제 효과는 미관찰. | C005 | M005 |
| Base.PipeBombSensorV3 | public / no-core | revise / description_ready | scripts/newitems.txt:3826의 exact ExplosionPower=90. 원격/센서/타이머는 각 선언대로 별도 조건이며 모든 장치를 같은 투척/폭발 효과로 묶지 않는다. Java 내부·PZ 실제 효과는 미관찰. | C005 | M005 |
| Base.PipeBombTriggered | public / no-core | revise / description_ready | scripts/newitems.txt:3740의 exact ExplosionPower=90. 원격/센서/타이머는 각 선언대로 별도 조건이며 모든 장치를 같은 투척/폭발 효과로 묶지 않는다. Java 내부·PZ 실제 효과는 미관찰. | C005 | M005 |
| Base.PipeWrench | public / no-core | revise / description_ready | scripts/items_weapons.txt:403; exact Weapon/damage=0.5–1. 구체 작업 source가 미결속인 부분을 일반 '작업'으로 확대하지 않는다. | C066 | M073 |
| Base.Pistol | public / no-core | keep / acquisition_only | 각 exact ranged Weapon 선언과 사격 목적을 대조했다. empty-core를 문구만으로 채우지 않는다. | C003 | M094 |
| Base.Pistol2 | public / no-core | keep / acquisition_only | 각 exact ranged Weapon 선언과 사격 목적을 대조했다. empty-core를 문구만으로 채우지 않는다. | C003 | M094 |
| Base.Pistol3 | public / no-core | keep / acquisition_only | 각 exact ranged Weapon 선언과 사격 목적을 대조했다. empty-core를 문구만으로 채우지 않는다. | C003 | M094 |
| Base.PistolCase1 | public / core | revise / description_ready | scripts/clothing/clothing_bags.txt:588의 exact Container/Capacity=4. 보관·운반 역할이 명확하며 이름에 따른 내용물 제한/냉장 효과는 추가하지 않는다. | C022 | M023 |
| Base.PistolCase2 | public / core | revise / description_ready | scripts/clothing/clothing_bags.txt:603의 exact Container/Capacity=4. 보관·운반 역할이 명확하며 이름에 따른 내용물 제한/냉장 효과는 추가하지 않는다. | C022 | M023 |
| Base.PistolCase3 | public / core | revise / description_ready | scripts/clothing/clothing_bags.txt:618의 exact Container/Capacity=4. 보관·운반 역할이 명확하며 이름에 따른 내용물 제한/냉장 효과는 추가하지 않는다. | C022 | M023 |
| Base.Pizza | public / core | revise / description_ready | scripts/items_food.txt:5591의 exact H=-25, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C012 | M012 |
| Base.PizzaRecipe | public / core | revise / description_ready | scripts/items_food.txt:5628의 exact H=-80, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C012 | M012 |
| Base.PizzaWhole | public / core | revise / description_ready | scripts/items_food.txt:5609의 exact H=-150, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C012 | M012 |
| Base.Plank | public / core | keep / description_ready | exact Plank 제작 input/keep 관계가 목공·여러 제작 재료라는 목적을 뒷받침한다. | C003 | M156 |
| Base.PlankNail | public / no-core | revise / description_ready | scripts/items_weapons.txt:1914; exact Type=Weapon/damage=0.5–0.8. 연주·경기·배관 수리 같은 현실 기능을 추정하지 않는다. | C021 | M022 |
| Base.Plantain | public / core | revise / description_ready | scripts/newitems.txt:2027 Type=Normal; scripts/recipes.txt:1192–1209의 exact poultice input 확인. 섭취 효과/완성 습포의 치료 효과와 분리. | C136 | M079 |
| Base.PlantainCataplasm | public / no-core | revise / description_ready | scripts/newitems.txt:2038; ISHealthPanel.lua:1193–1273 exact poultice selector/부상/세 factor=0→각 timed action. perform에서 부상 부위 factor 설정·item 소비. 일반적인 처치 목적은 준비되며 개별 회복 효과·속도는 미확정으로 범위 밖에 둠. | C228 | M222 |
| Base.PlasterPowder | public / core | revise / description_ready | scripts/items.txt:353; recipes.txt:650 Make Bucket of Plaster 입력→BucketPlasterFull. | C137 | M026 |
| Base.PlasticCup | public / core | revise / description_ready | scripts/newitems.txt:4511: CanStoreWater=TRUE, ReplaceOnUseOn=WaterSource-PlasticCupWater. §빈 물 용기와 같은 exact 물 저장/전환 사실을 재사용하며 음용 안전성·현재 내용물은 추정하지 않는다. | C038 | M041 |
| Base.PlasticCupWater | public / no-core | revise / description_ready | scripts/items_food.txt:9738: CanStoreWater=TRUE, ReplaceOnUseOn=WaterSource-PlasticCupWater. §빈 물 용기와 같은 exact 물 저장/전환 사실을 재사용하며 음용 안전성·현재 내용물은 추정하지 않는다. | C038 | M041 |
| Base.PlasticTray | public / core | review_hold / review_required | scripts/newitems.txt:4771: 주방 소품의 현실 사용을 actual 조리/상차림 interaction에 결속하지 못했다. exact 역할이 확인된 식재료/도구와 분리한다. 필요한 추가 근거는 이 exact item의 해당 행동/재료 입력 또는 효과를 명시하는 vanilla source 관계이며, current admission 부재를 해소할 승인만으로 대체하지 않음. | C002 | M082 |
| Base.Plasticbag | public / core | keep / description_ready | scripts/clothing/clothing_bags.txt:280의 exact Container/Capacity=8. 보관·운반 역할이 명확하며 이름에 따른 내용물 제한/냉장 효과는 추가하지 않는다. | C023 | M023 |
| Base.Plate | public / core | review_hold / review_required | scripts/newitems.txt:4611: 주방 소품의 현실 사용을 actual 조리/상차림 interaction에 결속하지 못했다. exact 역할이 확인된 식재료/도구와 분리한다. 필요한 추가 근거는 이 exact item의 해당 행동/재료 입력 또는 효과를 명시하는 vanilla source 관계이며, current admission 부재를 해소할 승인만으로 대체하지 않음. | C002 | M082 |
| Base.PlateBlue | public / core | review_hold / review_required | scripts/newitems.txt:4621: 주방 소품의 현실 사용을 actual 조리/상차림 interaction에 결속하지 못했다. exact 역할이 확인된 식재료/도구와 분리한다. 필요한 추가 근거는 이 exact item의 해당 행동/재료 입력 또는 효과를 명시하는 vanilla source 관계이며, current admission 부재를 해소할 승인만으로 대체하지 않음. | C002 | M082 |
| Base.PlateFancy | public / core | review_hold / review_required | scripts/newitems.txt:4641: 주방 소품의 현실 사용을 actual 조리/상차림 interaction에 결속하지 못했다. exact 역할이 확인된 식재료/도구와 분리한다. 필요한 추가 근거는 이 exact item의 해당 행동/재료 입력 또는 효과를 명시하는 vanilla source 관계이며, current admission 부재를 해소할 승인만으로 대체하지 않음. | C002 | M082 |
| Base.PlateOrange | public / core | review_hold / review_required | scripts/newitems.txt:4631: 주방 소품의 현실 사용을 actual 조리/상차림 interaction에 결속하지 못했다. exact 역할이 확인된 식재료/도구와 분리한다. 필요한 추가 근거는 이 exact item의 해당 행동/재료 입력 또는 효과를 명시하는 vanilla source 관계이며, current admission 부재를 해소할 승인만으로 대체하지 않음. | C002 | M082 |
| Base.Plonkies | public / core | revise / description_ready | scripts/items_food.txt:9495의 exact H=-10, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C012 | M012 |
| Base.Plunger | empty / no-core | revise / description_ready | scripts/items_weapons.txt:600; exact Type=Weapon/damage=0.3–0.5. 연주·경기·배관 수리 같은 현실 기능을 추정하지 않는다. | C021 | M022 |
| Base.PokerChips | public / core | review_hold / review_required | scripts/newitems.txt:4924: §남은 혼합 역할: 현재 놀이 assertion을 실제 게임 플레이/지루함 감소에 결속하지 못했다. Normal 소품과 실제 놀이 기능을 구분한다. 필요한 추가 근거는 이 exact item의 해당 행동/재료 입력 또는 효과를 명시하는 vanilla source 관계이며, current admission 부재를 해소할 승인만으로 대체하지 않음. | C002 | M021 |
| Base.PonchoGreen | public / core | keep / description_ready | scripts/clothing/clothing_jacket.txt:529의 Clothing/BodyLocation=JacketHat와 현재 착용 목적 일치. 수치 추가나 감염/위장 효과를 강제하지 않는다. | C018 | M018 |
| Base.PonchoGreenDOWN | public / no-core | revise / description_ready | scripts/clothing/clothing_jacket.txt:551: Clothing/BodyLocation=Jacket_Down. §기본 착용 재판정의 추가 Wear(DownHoodie)→동일 FullType 착용 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C212 | M214 |
| Base.PonchoYellow | public / core | keep / description_ready | scripts/clothing/clothing_jacket.txt:574의 Clothing/BodyLocation=JacketHat와 현재 착용 목적 일치. 수치 추가나 감염/위장 효과를 강제하지 않는다. | C018 | M018 |
| Base.PonchoYellowDOWN | public / no-core | revise / description_ready | scripts/clothing/clothing_jacket.txt:596: Clothing/BodyLocation=Jacket_Down. §기본 착용 재판정의 추가 Wear(DownHoodie)→동일 FullType 착용 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C212 | M214 |
| Base.PoolBall | public / core | review_hold / review_required | scripts/items.txt:365: 현재 경기 규칙에 맞춘 놀이 assertion을 실제 경기/투척 기능과 결속하지 못했다. Normal 소품이라는 선언은 경기 실행 근거가 아니다. 필요한 추가 근거는 이 exact item의 해당 행동/재료 입력 또는 효과를 명시하는 vanilla source 관계이며, current admission 부재를 해소할 승인만으로 대체하지 않음. | C002 | M033 |
| Base.Poolcue | public / no-core | revise / description_ready | scripts/items_weapons.txt:1960; exact Type=Weapon/damage=0.2–0.4. 연주·경기·배관 수리 같은 현실 기능을 추정하지 않는다. | C021 | M022 |
| Base.Pop | public / core | revise / description_ready | scripts/items_food.txt:3365; 원문 Food H<0/T<0 및 EvolvedRecipe 선언. §사과의 소비·재료 해석 재사용; 보존/안전/효과량 보장 없음. | C058 | M066 |
| Base.Pop2 | public / core | revise / description_ready | scripts/items_food.txt:3392; 원문 Food H<0/T<0 및 EvolvedRecipe 선언. §사과의 소비·재료 해석 재사용; 보존/안전/효과량 보장 없음. | C058 | M066 |
| Base.Pop2Empty | public / core | review_hold / review_required | scripts/newitems.txt:4096: 이 빈 item의 재사용/처리 목적을 실제 전환·상호작용에 결속하지 못했다. 빈 용기라는 이름만으로 물 저장 가능성을 추가하지 않는다. 필요한 추가 근거는 이 exact item의 해당 행동/재료 입력 또는 효과를 명시하는 vanilla source 관계이며, current admission 부재를 해소할 승인만으로 대체하지 않음. | C002 | M039 |
| Base.Pop3 | public / core | revise / description_ready | scripts/items_food.txt:3419; 원문 Food H<0/T<0 및 EvolvedRecipe 선언. §사과의 소비·재료 해석 재사용; 보존/안전/효과량 보장 없음. | C058 | M066 |
| Base.Pop3Empty | public / core | review_hold / review_required | scripts/newitems.txt:4106: 이 빈 item의 재사용/처리 목적을 실제 전환·상호작용에 결속하지 못했다. 빈 용기라는 이름만으로 물 저장 가능성을 추가하지 않는다. 필요한 추가 근거는 이 exact item의 해당 행동/재료 입력 또는 효과를 명시하는 vanilla source 관계이며, current admission 부재를 해소할 승인만으로 대체하지 않음. | C002 | M039 |
| Base.PopBottle | public / core | revise / description_ready | scripts/items_food.txt:3446; 원문 Food H<0/T<0 및 EvolvedRecipe 선언. §사과의 소비·재료 해석 재사용; 보존/안전/효과량 보장 없음. | C058 | M066 |
| Base.PopBottleEmpty | public / core | keep / description_ready | 각 exact CanStoreWater 및 ReplaceOnUseOn=WaterSource 관계를 확인했다. 물의 안전성이나 소독 효과는 주장하지 않는다. | C003 | M040 |
| Base.PopEmpty | public / core | review_hold / review_required | scripts/newitems.txt:4086: 이 빈 item의 재사용/처리 목적을 실제 전환·상호작용에 결속하지 못했다. 빈 용기라는 이름만으로 물 저장 가능성을 추가하지 않는다. 필요한 추가 근거는 이 exact item의 해당 행동/재료 입력 또는 효과를 명시하는 vanilla source 관계이며, current admission 부재를 해소할 승인만으로 대체하지 않음. | C002 | M039 |
| Base.Popcorn | public / core | revise / description_ready | scripts/items_food.txt:3975; Food H=-10/T=+10, IsCookable=true; CantEat 선언 없음. 갈증 감소로 오인 금지. | C138 | M157 |
| Base.PorkChop | public / core | revise / description_ready | scripts/items_food.txt:2102의 exact H=-30, T=미선언; EvolvedRecipe 재료 선언 확인; DangerousUncooked=TRUE. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C063 | M004 |
| Base.Pot | public / core | revise / description_ready | §조리 문구 32개: 이 exact item의 input/result/keep 역할과 원본 recipe를 분리 검토했다. | C026 | M027 |
| Base.PotOfSoup | public / core | revise / description_ready | scripts/items_food.txt:3278; 원문 H/T 음수 Food 및 2/4 bowls 입력; 실제 재료에 따른 내용물 변동은 보존. | C139 | M064 |
| Base.PotOfSoupRecipe | public / core | revise / description_ready | scripts/items_food.txt:3307; 원문 H/T 음수 Food 및 2/4 bowls 입력; 실제 재료에 따른 내용물 변동은 보존. | C139 | M064 |
| Base.PotOfStew | public / core | revise / description_ready | scripts/items_food.txt:3336; 원문 H/T 음수 Food 및 2/4 bowls 입력; 실제 재료에 따른 내용물 변동은 보존. | C139 | M064 |
| Base.PotatoPancakes | public / core | revise / description_ready | scripts/items_food.txt:8001의 exact H=-15, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C012 | M012 |
| Base.Pretzel | public / core | revise / description_ready | scripts/items_food.txt:8384의 exact H=-5, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C012 | M012 |
| Base.Processedcheese | public / core | revise / description_ready | scripts/items_food.txt:5433의 exact H=-5, T=미선언; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C004 | M004 |
| Base.PropaneTank | public / core | keep / description_ready | Refill Blow Torch의 exact PropaneTank input으로 기본 충전 용도가 명확하다. | C003 | M158 |
| Base.Pumpkin | public / core | revise / description_ready | scripts/items_food.txt:7826의 exact H=-40, T=미선언; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C004 | M004 |
| Base.Purse | public / core | keep / description_ready | scripts/clothing/clothing_bags.txt:325의 exact Container/Capacity=12. 보관·운반 역할이 명확하며 이름에 따른 내용물 제한/냉장 효과는 추가하지 않는다. | C023 | M023 |
| Base.QuaggaCakes | public / core | revise / description_ready | scripts/items_food.txt:9528의 exact H=-10, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C012 | M012 |
| Base.Rabbitmeat | public / no-core | revise / description_ready | scripts/items_food.txt:2129의 exact H=-30, T=미선언; EvolvedRecipe 재료 선언 확인; DangerousUncooked=TRUE. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C063 | M004 |
| Base.Radio | public / core | review_hold / review_required | scripts/newitems.txt:1821: exact Type=Normal, OBSOLETE=TRUE. 정상 B41에서 이 exact item의 생성·사용 가능성/등록이 미확정이다. 작동하는 별도 FullType으로 대체하거나 기존 no-core 때문에 보류하는 것이 아님. | C002 | M221 |
| Base.Rake | public / no-core | revise / description_ready | scripts/items_weapons.txt:2720; exact Weapon/MinDamage=.2/MaxDamage=.4/SwingAnim=Bat. 기존 긍정 melee source 계약 적용; 재배·갈퀴질 경로가 미확정이어도 기본 근접 공격 역할까지 보류하지 않음. | C231 | M225 |
| Base.Ramen | public / core | revise / description_ready | scripts/items_food.txt:4706의 exact H=-10, T=40; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C067 | M004 |
| Base.RamenBowl | public / no-core | revise / description_ready | scripts/items_food.txt:4727의 exact H=-10, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C012 | M012 |
| Base.Razor | public / core | keep / description_ready | Razor tag와 ISCharacterScreen의 면도 선택 경로가 현재 용도와 일치한다. | C003 | M160 |
| Base.RearCarDoor1 | public / core | keep / description_ready | scripts/vehicles/vehiclesitems.txt:1073; exact VehicleType=1와 해당 door/window/windshield part 관계. 현재 패널/유리 탈착 목적은 이미 구체적이며 방탄·방호 효과를 추가하지 않는다. | C014 | M096 |
| Base.RearCarDoor2 | public / core | keep / description_ready | scripts/vehicles/vehiclesitems.txt:1115; exact VehicleType=2와 해당 door/window/windshield part 관계. 현재 패널/유리 탈착 목적은 이미 구체적이며 방탄·방호 효과를 추가하지 않는다. | C014 | M096 |
| Base.RearCarDoor3 | public / core | keep / description_ready | scripts/vehicles/vehiclesitems.txt:1157; exact VehicleType=3와 해당 door/window/windshield part 관계. 현재 패널/유리 탈착 목적은 이미 구체적이며 방탄·방호 효과를 추가하지 않는다. | C014 | M096 |
| Base.RearCarDoorDouble1 | public / core | keep / description_ready | scripts/vehicles/vehiclesitems.txt:1087; exact VehicleType=1와 해당 door/window/windshield part 관계. 현재 패널/유리 탈착 목적은 이미 구체적이며 방탄·방호 효과를 추가하지 않는다. | C014 | M096 |
| Base.RearCarDoorDouble2 | public / core | keep / description_ready | scripts/vehicles/vehiclesitems.txt:1129; exact VehicleType=2와 해당 door/window/windshield part 관계. 현재 패널/유리 탈착 목적은 이미 구체적이며 방탄·방호 효과를 추가하지 않는다. | C014 | M096 |
| Base.RearCarDoorDouble3 | public / core | keep / description_ready | scripts/vehicles/vehiclesitems.txt:1171; exact VehicleType=3와 해당 door/window/windshield part 관계. 현재 패널/유리 탈착 목적은 이미 구체적이며 방탄·방호 효과를 추가하지 않는다. | C014 | M096 |
| Base.RearWindow1 | public / core | keep / description_ready | scripts/vehicles/vehiclesitems.txt:932; exact VehicleType=1와 해당 door/window/windshield part 관계. 현재 패널/유리 탈착 목적은 이미 구체적이며 방탄·방호 효과를 추가하지 않는다. | C014 | M096 |
| Base.RearWindow2 | public / core | keep / description_ready | scripts/vehicles/vehiclesitems.txt:988; exact VehicleType=2와 해당 door/window/windshield part 관계. 현재 패널/유리 탈착 목적은 이미 구체적이며 방탄·방호 효과를 추가하지 않는다. | C014 | M096 |
| Base.RearWindow3 | public / core | keep / description_ready | scripts/vehicles/vehiclesitems.txt:1044; exact VehicleType=3와 해당 door/window/windshield part 관계. 현재 패널/유리 탈착 목적은 이미 구체적이며 방탄·방호 효과를 추가하지 않는다. | C014 | M096 |
| Base.RearWindshield1 | public / core | keep / description_ready | scripts/vehicles/vehiclesitems.txt:904; exact VehicleType=1와 해당 door/window/windshield part 관계. 현재 패널/유리 탈착 목적은 이미 구체적이며 방탄·방호 효과를 추가하지 않는다. | C014 | M096 |
| Base.RearWindshield2 | public / core | keep / description_ready | scripts/vehicles/vehiclesitems.txt:960; exact VehicleType=2와 해당 door/window/windshield part 관계. 현재 패널/유리 탈착 목적은 이미 구체적이며 방탄·방호 효과를 추가하지 않는다. | C014 | M096 |
| Base.RearWindshield3 | public / core | keep / description_ready | scripts/vehicles/vehiclesitems.txt:1016; exact VehicleType=3와 해당 door/window/windshield part 관계. 현재 패널/유리 탈착 목적은 이미 구체적이며 방탄·방호 효과를 추가하지 않는다. | C014 | M096 |
| Base.Receiver | public / no-core | revise / description_ready | scripts/newitems.txt:152; input:Make Remote Trigger; recipes.txt:2215/2231 입력→TriggerCrafted. | C140 | M011 |
| Base.RecoilPad | public / core | keep / description_ready | scripts/newitems.txt:2555; exact WeaponPart/PartType=RecoilPad/MountOn=HuntingRifle; VarmintRifle; AssaultRifle; AssaultRifle2. 총기 개조 부품이라는 current 목적은 구체적. 실제 성능·조명/총검 공격은 추가하지 않는다. | C014 | M014 |
| Base.RedDot | public / core | keep / description_ready | scripts/newitems.txt:2586; exact WeaponPart/PartType=Scope/MountOn=Pistol; Pistol2; Pistol3; Revolver; Revolver_Long; AssaultRifle; AssaultRifle2; HuntingRifle; VarmintRifle. 총기 개조 부품이라는 current 목적은 구체적. 실제 성능·조명/총검 공격은 추가하지 않는다. | C014 | M014 |
| Base.RedPen | public / core | revise / description_ready | scripts/items_weapons.txt:3946; exact Write/pen tags, 기존 문서 작성 경로 및 ISWorldMapSymbols:canWrite의 type/tag 선택. | C043 | M049 |
| Base.RefriedBeans | public / core | revise / description_ready | scripts/items_food.txt:6727의 exact H=-10, T=미선언; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C004 | M004 |
| Base.Remote | public / core | revise / description_ready | scripts/newitems.txt:1017; recipes.txt:2172–2214 Make Remote Controller V1–V3 input. | C141 | M011 |
| Base.RemoteCraftedV1 | public / no-core | revise / description_ready | scripts/newitems.txt:645; RemoteController=true; ISInventoryPaneContextMenu.lua:577/1722/1736 연결 ID·범위로 trap trigger 실행. | C142 | M161 |
| Base.RemoteCraftedV2 | public / no-core | revise / description_ready | scripts/newitems.txt:659; RemoteController=true; ISInventoryPaneContextMenu.lua:577/1722/1736 연결 ID·범위로 trap trigger 실행. | C142 | M161 |
| Base.RemoteCraftedV3 | public / no-core | revise / description_ready | scripts/newitems.txt:673; RemoteController=true; ISInventoryPaneContextMenu.lua:577/1722/1736 연결 ID·범위로 trap trigger 실행. | C142 | M161 |
| Base.Revolver | public / no-core | keep / acquisition_only | 각 exact ranged Weapon 선언과 사격 목적을 대조했다. empty-core를 문구만으로 채우지 않는다. | C003 | M094 |
| Base.RevolverCase1 | public / core | revise / description_ready | scripts/clothing/clothing_bags.txt:633의 exact Container/Capacity=4. 보관·운반 역할이 명확하며 이름에 따른 내용물 제한/냉장 효과는 추가하지 않는다. | C022 | M023 |
| Base.RevolverCase2 | public / core | revise / description_ready | scripts/clothing/clothing_bags.txt:648의 exact Container/Capacity=4. 보관·운반 역할이 명확하며 이름에 따른 내용물 제한/냉장 효과는 추가하지 않는다. | C022 | M023 |
| Base.RevolverCase3 | public / core | revise / description_ready | scripts/clothing/clothing_bags.txt:663의 exact Container/Capacity=4. 보관·운반 역할이 명확하며 이름에 따른 내용물 제한/냉장 효과는 추가하지 않는다. | C022 | M023 |
| Base.Revolver_Long | public / no-core | keep / acquisition_only | 각 exact ranged Weapon 선언과 사격 목적을 대조했다. empty-core를 문구만으로 채우지 않는다. | C003 | M094 |
| Base.Revolver_Short | public / no-core | keep / acquisition_only | 각 exact ranged Weapon 선언과 사격 목적을 대조했다. empty-core를 문구만으로 채우지 않는다. | C003 | M094 |
| Base.Rice | public / core | revise / description_ready | scripts/items_food.txt:4790의 exact H=-60, T=60; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C025 | M012 |
| Base.RiceBowl | public / no-core | revise / description_ready | scripts/items_food.txt:4968의 exact H=-12, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C012 | M012 |
| Base.RicePan | public / core | revise / description_ready | scripts/items_food.txt:4852; input:Make 4 Bowls of Rice; input:Make 2 Bowls of Rice; dynamic Food 내용물 수치는 고정하지 않음; bowls로 나누는 exact 입력 경로. | C132 | M150 |
| Base.RicePaper | public / core | revise / description_ready | scripts/items_food.txt:6748의 exact H=-4, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C012 | M012 |
| Base.RicePot | public / core | revise / description_ready | scripts/items_food.txt:4942; input:Make 4 Bowls of Rice; input:Make 2 Bowls of Rice; dynamic Food 내용물 수치는 고정하지 않음; bowls로 나누는 exact 입력 경로. | C132 | M150 |
| Base.RiceVinegar | public / core | revise / description_ready | scripts/items_food.txt:6764의 exact H=-20, T=미선언; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C004 | M004 |
| Base.RifleCase1 | public / core | revise / description_ready | scripts/newBags.txt:188의 exact Container/Capacity=7. 보관·운반 역할이 명확하며 이름에 따른 내용물 제한/냉장 효과는 추가하지 않는다. | C022 | M023 |
| Base.RifleCase2 | public / core | revise / description_ready | scripts/newBags.txt:205의 exact Container/Capacity=7. 보관·운반 역할이 명확하며 이름에 따른 내용물 제한/냉장 효과는 추가하지 않는다. | C022 | M023 |
| Base.RifleCase3 | public / core | revise / description_ready | scripts/newBags.txt:222의 exact Container/Capacity=7. 보관·운반 역할이 명확하며 이름에 따른 내용물 제한/냉장 효과는 추가하지 않는다. | C022 | M023 |
| Base.Ring | public / no-core | review_hold / review_required | scripts/newitems.txt:1028: exact Type=Normal, OBSOLETE=TRUE. 정상 B41에서 이 exact item의 생성·사용 가능성/등록이 미확정이다. 작동하는 별도 FullType으로 대체하거나 기존 no-core 때문에 보류하는 것이 아님. | C076 | M221 |
| Base.Ring_Left_MiddleFinger_Gold | public / core | keep / description_ready | scripts/clothing/clothing_jewellery.txt:566의 Clothing/BodyLocation=Left_MiddleFinger와 현재 착용 목적 일치. 수치 추가나 감염/위장 효과를 강제하지 않는다. | C018 | M018 |
| Base.Ring_Left_MiddleFinger_GoldDiamond | public / core | keep / description_ready | scripts/clothing/clothing_jewellery.txt:806의 Clothing/BodyLocation=Left_MiddleFinger와 현재 착용 목적 일치. 수치 추가나 감염/위장 효과를 강제하지 않는다. | C018 | M018 |
| Base.Ring_Left_MiddleFinger_GoldRuby | public / core | keep / description_ready | scripts/clothing/clothing_jewellery.txt:746의 Clothing/BodyLocation=Left_MiddleFinger와 현재 착용 목적 일치. 수치 추가나 감염/위장 효과를 강제하지 않는다. | C018 | M018 |
| Base.Ring_Left_MiddleFinger_Silver | public / core | keep / description_ready | scripts/clothing/clothing_jewellery.txt:626의 Clothing/BodyLocation=Left_MiddleFinger와 현재 착용 목적 일치. 수치 추가나 감염/위장 효과를 강제하지 않는다. | C018 | M018 |
| Base.Ring_Left_MiddleFinger_SilverDiamond | public / core | keep / description_ready | scripts/clothing/clothing_jewellery.txt:686의 Clothing/BodyLocation=Left_MiddleFinger와 현재 착용 목적 일치. 수치 추가나 감염/위장 효과를 강제하지 않는다. | C018 | M018 |
| Base.Ring_Left_RingFinger_Gold | public / no-core | revise / description_ready | scripts/clothing/clothing_jewellery.txt:596: Clothing/BodyLocation=Left_RingFinger. §기본 착용 재판정의 추가 Wear(LeftRingFinger)→동일 FullType 착용 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C213 | M214 |
| Base.Ring_Left_RingFinger_GoldDiamond | public / core | keep / description_ready | scripts/clothing/clothing_jewellery.txt:836의 Clothing/BodyLocation=Left_RingFinger와 현재 착용 목적 일치. 수치 추가나 감염/위장 효과를 강제하지 않는다. | C018 | M018 |
| Base.Ring_Left_RingFinger_GoldRuby | public / core | keep / description_ready | scripts/clothing/clothing_jewellery.txt:776의 Clothing/BodyLocation=Left_RingFinger와 현재 착용 목적 일치. 수치 추가나 감염/위장 효과를 강제하지 않는다. | C018 | M018 |
| Base.Ring_Left_RingFinger_Silver | public / no-core | revise / description_ready | scripts/clothing/clothing_jewellery.txt:656: Clothing/BodyLocation=Left_RingFinger. §기본 착용 재판정의 추가 Wear(LeftRingFinger)→동일 FullType 착용 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C213 | M214 |
| Base.Ring_Left_RingFinger_SilverDiamond | public / core | keep / description_ready | scripts/clothing/clothing_jewellery.txt:716의 Clothing/BodyLocation=Left_RingFinger와 현재 착용 목적 일치. 수치 추가나 감염/위장 효과를 강제하지 않는다. | C018 | M018 |
| Base.Ring_Right_MiddleFinger_Gold | public / core | keep / description_ready | scripts/clothing/clothing_jewellery.txt:551의 Clothing/BodyLocation=Right_MiddleFinger와 현재 착용 목적 일치. 수치 추가나 감염/위장 효과를 강제하지 않는다. | C018 | M018 |
| Base.Ring_Right_MiddleFinger_GoldDiamond | public / core | keep / description_ready | scripts/clothing/clothing_jewellery.txt:791의 Clothing/BodyLocation=Right_MiddleFinger와 현재 착용 목적 일치. 수치 추가나 감염/위장 효과를 강제하지 않는다. | C018 | M018 |
| Base.Ring_Right_MiddleFinger_GoldRuby | public / core | keep / description_ready | scripts/clothing/clothing_jewellery.txt:731의 Clothing/BodyLocation=Right_MiddleFinger와 현재 착용 목적 일치. 수치 추가나 감염/위장 효과를 강제하지 않는다. | C018 | M018 |
| Base.Ring_Right_MiddleFinger_Silver | public / core | keep / description_ready | scripts/clothing/clothing_jewellery.txt:611의 Clothing/BodyLocation=Right_MiddleFinger와 현재 착용 목적 일치. 수치 추가나 감염/위장 효과를 강제하지 않는다. | C018 | M018 |
| Base.Ring_Right_MiddleFinger_SilverDiamond | public / core | keep / description_ready | scripts/clothing/clothing_jewellery.txt:671의 Clothing/BodyLocation=Right_MiddleFinger와 현재 착용 목적 일치. 수치 추가나 감염/위장 효과를 강제하지 않는다. | C018 | M018 |
| Base.Ring_Right_RingFinger_Gold | public / core | keep / description_ready | scripts/clothing/clothing_jewellery.txt:581의 Clothing/BodyLocation=Right_RingFinger와 현재 착용 목적 일치. 수치 추가나 감염/위장 효과를 강제하지 않는다. | C018 | M018 |
| Base.Ring_Right_RingFinger_GoldDiamond | public / no-core | revise / description_ready | scripts/clothing/clothing_jewellery.txt:821: Clothing/BodyLocation=Right_RingFinger. §기본 착용 재판정의 추가 Wear(RightRingFinger)→동일 FullType 착용 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C214 | M214 |
| Base.Ring_Right_RingFinger_GoldRuby | public / no-core | revise / description_ready | scripts/clothing/clothing_jewellery.txt:761: Clothing/BodyLocation=Right_RingFinger. §기본 착용 재판정의 추가 Wear(RightRingFinger)→동일 FullType 착용 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C214 | M214 |
| Base.Ring_Right_RingFinger_Silver | public / core | keep / description_ready | scripts/clothing/clothing_jewellery.txt:641의 Clothing/BodyLocation=Right_RingFinger와 현재 착용 목적 일치. 수치 추가나 감염/위장 효과를 강제하지 않는다. | C018 | M018 |
| Base.Ring_Right_RingFinger_SilverDiamond | public / no-core | revise / description_ready | scripts/clothing/clothing_jewellery.txt:701: Clothing/BodyLocation=Right_RingFinger. §기본 착용 재판정의 추가 Wear(RightRingFinger)→동일 FullType 착용 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C214 | M214 |
| Base.RippedSheets | public / core | revise / description_ready | scripts/items.txt:407: exact CanBandage와 Make Stone Axe/Hammer/Knife/Splint input, ISApplyBandage 경로. 보호된 LeatherStrips의 별도 수선 문구는 변경하지 않는다. | C075 | M086 |
| Base.RippedSheetsDirty | public / core | revise / description_ready | scripts/items.txt:423: exact CanBandage 및 ISApplyBandage:perform의 Dirty type은 bandageLife=0으로 분기. 깨끗한 재료와 같은 지속/치료 효과를 주지 않는다. | C031 | M031 |
| Base.RiversideMap | public / no-core | keep / acquisition_only | scripts/newitems.txt:1249; Map=RiversideMap; ISMap.lua:321 + ISMapDefinitions.lua:257/267–451의 해당 Init. 지역 지도 확인 목적이 구체적이며 유지 가능. | C046 | M055 |
| Base.RoastingPan | public / core | revise / description_ready | scripts/items.txt:452; evolvedrecipes.txt:72 BaseItem=RoastingPan→PanFriedVegetables2. | C143 | M011 |
| Base.RockCandy | public / core | revise / description_ready | scripts/items_food.txt:9316의 exact H=-5, T=미선언; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C004 | M004 |
| Base.RollingPin | public / core | revise / description_ready | scripts/items_weapons.txt:1192; recipes.txt:1067 및 Pizza/Bread/Cookie keep 입력. | C144 | M026 |
| Base.Rope | public / core | keep / description_ready | 현재 direct_use의 결속 재료 역할을 유지한다. 새 구조물 종류를 유추하지 않는다. | C003 | M162 |
| Base.Rosehips | public / core | revise / description_ready | scripts/items_food.txt:4155의 exact H=-6, T=미선언; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C004 | M004 |
| Base.Rosemary | public / core | revise / description_ready | scripts/items_food.txt:8607의 exact H=-1, T=미선언; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C004 | M004 |
| Base.RosewoodMap | public / no-core | keep / acquisition_only | scripts/newitems.txt:1237; Map=RosewoodMap; ISMap.lua:321 + ISMapDefinitions.lua:257/267–451의 해당 Init. 지역 지도 확인 목적이 구체적이며 유지 가능. | C046 | M055 |
| Base.RubberBand | public / core | review_hold / review_required | scripts/newitems.txt:687; Normal 선언과 문구류 정체성만으로 작성·수정·종이 정리 action을 뒷받침할 수 없음; 이 exact item의 사용 handler/input 관계 필요. 필요한 추가 근거는 이 exact item의 해당 행동/재료 입력 또는 효과를 명시하는 vanilla source 관계이며, current admission 부재를 해소할 승인만으로 대체하지 않음. | C049 | M118 |
| Base.Rubberducky | public / core | keep / description_ready | scripts/newitems.txt:1039 Normal/DisplayName=Rubber Duck/WorldStaticModel=Rubberducky와 현행 오리 장난감 정체성이 일치. 계획 Change 2의 '근거가 제한된 물건은 안전한 정체성 유지'를 적용; 소리/놀이 action을 설명하지 않으므로 그 engine 경로를 keep의 선행 조건으로 요구하지 않음. | C240 | M230 |
| Base.Rubberducky2 | public / core | keep / description_ready | 전지 삽입/제거라는 exact recipe 관계와 현재 기본 용도가 일치한다. 고무 오리의 소리 효과는 추가하지 않는다. | C003 | M164 |
| Base.SackCabbages | public / core | revise / description_ready | scripts/newBags.txt:273; newBags.txt:273–337 Type=Container Capacity15, empty_sack tooltip, HoldDirt. SackProduce_*의 식품 포장과 다름. | C145 | M064 |
| Base.SackCarrots | public / core | revise / description_ready | scripts/newBags.txt:289; newBags.txt:273–337 Type=Container Capacity15, empty_sack tooltip, HoldDirt. SackProduce_*의 식품 포장과 다름. | C145 | M064 |
| Base.SackOnions | public / core | revise / description_ready | scripts/newBags.txt:321; newBags.txt:273–337 Type=Container Capacity15, empty_sack tooltip, HoldDirt. SackProduce_*의 식품 포장과 다름. | C145 | M064 |
| Base.SackPotatoes | public / core | revise / description_ready | scripts/newBags.txt:305; newBags.txt:273–337 Type=Container Capacity15, empty_sack tooltip, HoldDirt. SackProduce_*의 식품 포장과 다름. | C145 | M064 |
| Base.SackProduce_Apple | public / core | revise / description_ready | scripts/items_food.txt:8018; recipes:4023–4238의 input:Open Sack of Apples; 해당 input/result를 기준으로 포장 개봉 역할을 특정. | C146 | M165 |
| Base.SackProduce_BellPepper | public / core | revise / description_ready | scripts/items_food.txt:8031; recipes:4023–4238의 input:Open Sack of Bell Peppers; 해당 input/result를 기준으로 포장 개봉 역할을 특정. | C146 | M165 |
| Base.SackProduce_Broccoli | public / core | revise / description_ready | scripts/items_food.txt:8044; recipes:4023–4238의 input:Open Sack of Broccoli; 해당 input/result를 기준으로 포장 개봉 역할을 특정. | C146 | M165 |
| Base.SackProduce_Cabbage | public / core | revise / description_ready | scripts/items_food.txt:8057; recipes:4023–4238의 input:Open Sack of Cabbages; 해당 input/result를 기준으로 포장 개봉 역할을 특정. | C146 | M165 |
| Base.SackProduce_Carrot | public / core | revise / description_ready | scripts/items_food.txt:8070; recipes:4023–4238의 input:Open Sack of Carrots; 해당 input/result를 기준으로 포장 개봉 역할을 특정. | C146 | M165 |
| Base.SackProduce_Cherry | public / core | revise / description_ready | scripts/items_food.txt:8083; recipes:4023–4238의 input:Open Sack of Cherries; 해당 input/result를 기준으로 포장 개봉 역할을 특정. | C146 | M165 |
| Base.SackProduce_Corn | public / core | revise / description_ready | scripts/items_food.txt:8096; recipes:4023–4238의 input:Open Sack of Corn; 해당 input/result를 기준으로 포장 개봉 역할을 특정. | C146 | M165 |
| Base.SackProduce_Eggplant | public / core | revise / description_ready | scripts/items_food.txt:8109; recipes:4023–4238의 input:Open Sack of Eggplants; 해당 input/result를 기준으로 포장 개봉 역할을 특정. | C146 | M165 |
| Base.SackProduce_Grapes | public / core | revise / description_ready | scripts/items_food.txt:8122; recipes:4023–4238의 input:Open Sack of Grapes; 해당 input/result를 기준으로 포장 개봉 역할을 특정. | C146 | M165 |
| Base.SackProduce_Leek | public / core | revise / description_ready | scripts/items_food.txt:8135; recipes:4023–4238의 input:Open Sack of Leeks; 해당 input/result를 기준으로 포장 개봉 역할을 특정. | C146 | M165 |
| Base.SackProduce_Lettuce | public / core | revise / description_ready | scripts/items_food.txt:8148; recipes:4023–4238의 input:Open Sack of Lettuce; 해당 input/result를 기준으로 포장 개봉 역할을 특정. | C146 | M165 |
| Base.SackProduce_Onion | public / core | revise / description_ready | scripts/items_food.txt:8161; recipes:4023–4238의 input:Open Sack of Onions; 해당 input/result를 기준으로 포장 개봉 역할을 특정. | C146 | M165 |
| Base.SackProduce_Peach | public / core | revise / description_ready | scripts/items_food.txt:8174; recipes:4023–4238의 input:Open Sack of Peaches; 해당 input/result를 기준으로 포장 개봉 역할을 특정. | C146 | M165 |
| Base.SackProduce_Pear | public / core | revise / description_ready | scripts/items_food.txt:8187; recipes:4023–4238의 input:Open Sack of Pears; 해당 input/result를 기준으로 포장 개봉 역할을 특정. | C146 | M165 |
| Base.SackProduce_Potato | public / core | revise / description_ready | scripts/items_food.txt:8200; recipes:4023–4238의 input:Open Sack of Potatoes; 해당 input/result를 기준으로 포장 개봉 역할을 특정. | C146 | M165 |
| Base.SackProduce_RedRadish | public / core | revise / description_ready | scripts/items_food.txt:8213; recipes:4023–4238의 input:Open Sack of Radishes; 해당 input/result를 기준으로 포장 개봉 역할을 특정. | C146 | M165 |
| Base.SackProduce_Strawberry | public / core | revise / description_ready | scripts/items_food.txt:8226; recipes:4023–4238의 input:Open Sack of Strawberries; 해당 input/result를 기준으로 포장 개봉 역할을 특정. | C146 | M165 |
| Base.SackProduce_Tomato | public / core | revise / description_ready | scripts/items_food.txt:8239; recipes:4023–4238의 input:Open Sack of Tomatoes; 해당 input/result를 기준으로 포장 개봉 역할을 특정. | C146 | M165 |
| Base.Sage | public / core | revise / description_ready | scripts/items_food.txt:8625의 exact H=-1, T=미선언; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C004 | M004 |
| Base.Salami | public / core | revise / description_ready | scripts/items_food.txt:7479의 exact H=-20, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C012 | M012 |
| Base.SalamiSlice | public / no-core | revise / description_ready | scripts/items_food.txt:7499의 exact H=-4, T=미선언; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C004 | M004 |
| Base.Salmon | public / core | revise / description_ready | scripts/items_food.txt:2365의 exact H=-30, T=미선언; EvolvedRecipe 재료 선언 확인; DangerousUncooked=TRUE. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C063 | M004 |
| Base.Salt | public / core | revise / description_ready | scripts/items_food.txt:4330의 exact H=-10, T=20; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C067 | M004 |
| Base.Sandbag | public / no-core | revise / description_ready | scripts/items.txt:1223; ISBuildMenu:856/877의 exact need material 및 FireFighting.isExtinguisher. 소화/장벽 역할별 조건 분리. | C095 | M108 |
| Base.Sandwich | public / no-core | revise / description_ready | scripts/items_food.txt:5516의 exact H=-10, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C012 | M012 |
| Base.Saucepan | public / no-core | revise / description_ready | scripts/items_weapons.txt:5: CanStoreWater=TRUE, ReplaceOnUseOn=WaterSource-WaterSaucepan. §빈 물 용기와 같은 exact 물 저장/전환 사실을 재사용하며 음용 안전성·현재 내용물은 추정하지 않는다. | C038 | M041 |
| Base.Sausage | public / core | revise / description_ready | scripts/items_food.txt:6785의 exact H=-20, T=미선언; EvolvedRecipe 재료 선언 확인; DangerousUncooked=TRUE. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C063 | M004 |
| Base.Saw | public / core | keep / description_ready | Saw tag 및 산탄총 절단 exact keep 관계로 현재 용도가 명확하다. | C003 | M166 |
| Base.SawflyLarva | public / core | revise / description_ready | scripts/items_food.txt:8964의 exact H=-5, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C012 | M012 |
| Base.Saxophone | public / no-core | revise / description_ready | scripts/items_weapons.txt:444; exact Type=Weapon/damage=0.4–0.8. 연주·경기·배관 수리 같은 현실 기능을 추정하지 않는다. | C021 | M022 |
| Base.Scalpel | public / core | revise / description_ready | scripts/items_weapons.txt:3700; exact Weapon/damage=0.1–0.4, 해당 Attach … to Spear input. 칼/식기·도구의 이름만으로 다른 작동을 추정하지 않음. | C047 | M057 |
| Base.Scarf_StripeBlackWhite | public / no-core | revise / description_ready | scripts/clothing/clothing_others.txt:412: Clothing/BodyLocation=Scarf. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C215 | M017 |
| Base.Scarf_StripeBlueWhite | public / no-core | revise / description_ready | scripts/clothing/clothing_others.txt:428: Clothing/BodyLocation=Scarf. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C215 | M017 |
| Base.Scarf_StripeRedWhite | public / no-core | revise / description_ready | scripts/clothing/clothing_others.txt:444: Clothing/BodyLocation=Scarf. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C215 | M017 |
| Base.Scarf_White | public / no-core | revise / description_ready | scripts/clothing/clothing_others.txt:396: Clothing/BodyLocation=Scarf. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C215 | M017 |
| Base.Scissors | public / core | revise / description_ready | scripts/items_weapons.txt:3614; exact Weapon/damage=0.1–0.1, 해당 Attach … to Spear input. 칼/식기·도구의 이름만으로 다른 작동을 추정하지 않음. | C047 | M057 |
| Base.Scotchtape | public / core | keep / description_ready | 최근 보호된 Scotchtape의 기존 제작 재료 용도와 lineage를 유지한다. | C003 | M167 |
| Base.ScrapMetal | public / core | keep / description_ready | scripts/newitems.txt:697: 보호된 source-bound ScrapMetal의 금속 제작 역할을 유지한다. | C147 | M168 |
| Base.Screwdriver | public / core | revise / description_ready | scripts/items_weapons.txt:4132; exact Weapon/damage=0.3–0.7, 해당 Attach … to Spear input. 칼/식기·도구의 이름만으로 다른 작동을 추정하지 않음. | C047 | M057 |
| Base.Screws | public / core | keep / description_ready | 현재 승인 나사못의 조립/수리 재료 역할을 유지한다. 개별 fixture를 유추하지 않는다. | C003 | M169 |
| Base.ScrewsBox | public / core | keep / description_ready | 나사못 상자 개봉 input/result와 현재 개봉 용도가 일치한다. | C003 | M056 |
| Base.Seaweed | public / core | revise / description_ready | scripts/items_food.txt:6829의 exact H=-3, T=미선언; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C004 | M004 |
| Base.SeedBag | public / core | revise / description_ready | scripts/newitems.txt:2140의 exact Container/Capacity=5. 보관·운반 역할이 명확하며 이름에 따른 내용물 제한/냉장 효과는 추가하지 않는다. | C022 | M023 |
| Base.SewingKit | public / core | revise / description_ready | scripts/newitems.txt:2156의 exact Container/Capacity=5. 보관·운반 역할이 명확하며 이름에 따른 내용물 제한/냉장 효과는 추가하지 않는다. | C022 | M023 |
| Base.SharpedStone | public / core | revise / description_ready | scripts/newitems.txt:924; exact Make Stone Axe/Knife input 및 Create Spear/Drill Plank keep를 구분. | C148 | M170 |
| Base.Sheet | public / core | revise / description_ready | scripts/items.txt:491; recipes.txt Make Mattress/Campfire Kit input; 다른 쓰임은 배제하지 않음. | C149 | M064 |
| Base.SheetMetal | public / core | keep / description_ready | exact Make Small Metal Sheet input 역할이 현재 판재 변환 용도와 일치한다. | C003 | M171 |
| Base.SheetPaper2 | empty / no-core | revise / description_ready | scripts/items_literature.txt:1367: items_literature:1277/1367의 exact CanBeWrite, §기록물의 기존 필기구·잠금/페이지 저장 경로 재사용. | C128 | M147 |
| Base.SheetRope | public / core | revise / description_ready | scripts/items.txt:502; ISWorldObjectContextMenu:975/1036 및 onAddSheetRope/onClimbSheetRope의 exact SheetRope·위치/수량/못 조건. | C150 | M172 |
| Base.Shirt_Baseball_KY | public / no-core | revise / description_ready | scripts/clothing/clothing_shirts.txt:3: Clothing/BodyLocation=ShortSleeveShirt. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C183 | M017 |
| Base.Shirt_Baseball_Rangers | public / no-core | revise / description_ready | scripts/clothing/clothing_shirts.txt:17: Clothing/BodyLocation=ShortSleeveShirt. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C183 | M017 |
| Base.Shirt_Baseball_Z | public / no-core | revise / description_ready | scripts/clothing/clothing_shirts.txt:31: Clothing/BodyLocation=ShortSleeveShirt. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C183 | M017 |
| Base.Shirt_Bowling_Blue | public / no-core | revise / description_ready | scripts/clothing/clothing_shirts.txt:1246: Clothing/BodyLocation=ShortSleeveShirt. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C183 | M017 |
| Base.Shirt_Bowling_Brown | public / no-core | revise / description_ready | scripts/clothing/clothing_shirts.txt:1260: Clothing/BodyLocation=ShortSleeveShirt. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C183 | M017 |
| Base.Shirt_Bowling_Green | public / no-core | revise / description_ready | scripts/clothing/clothing_shirts.txt:1274: Clothing/BodyLocation=ShortSleeveShirt. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C183 | M017 |
| Base.Shirt_Bowling_LimeGreen | public / no-core | revise / description_ready | scripts/clothing/clothing_shirts.txt:1288: Clothing/BodyLocation=ShortSleeveShirt. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C183 | M017 |
| Base.Shirt_Bowling_Pink | public / no-core | revise / description_ready | scripts/clothing/clothing_shirts.txt:1302: Clothing/BodyLocation=ShortSleeveShirt. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C183 | M017 |
| Base.Shirt_Bowling_White | public / no-core | revise / description_ready | scripts/clothing/clothing_shirts.txt:1316: Clothing/BodyLocation=ShortSleeveShirt. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C183 | M017 |
| Base.Shirt_CamoDesert | public / no-core | revise / description_ready | scripts/clothing/clothing_shirts.txt:45: Clothing/BodyLocation=Shirt. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C183 | M017 |
| Base.Shirt_CamoGreen | public / no-core | revise / description_ready | scripts/clothing/clothing_shirts.txt:59: Clothing/BodyLocation=Shirt. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C183 | M017 |
| Base.Shirt_CamoUrban | public / no-core | revise / description_ready | scripts/clothing/clothing_shirts.txt:73: Clothing/BodyLocation=Shirt. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C183 | M017 |
| Base.Shirt_CropTopNoArmTINT | public / no-core | revise / description_ready | scripts/clothing/clothing_shirts.txt:1210: Clothing/BodyLocation=Tshirt. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C183 | M017 |
| Base.Shirt_CropTopTINT | public / no-core | revise / description_ready | scripts/clothing/clothing_shirts.txt:1198: Clothing/BodyLocation=Tshirt. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C183 | M017 |
| Base.Shirt_Denim | public / no-core | revise / description_ready | scripts/clothing/clothing_shirts.txt:87: Clothing/BodyLocation=Shirt. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C183 | M017 |
| Base.Shirt_FormalTINT | public / no-core | revise / description_ready | scripts/clothing/clothing_shirts.txt:302: Clothing/BodyLocation=Shirt. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C183 | M017 |
| Base.Shirt_FormalWhite | public / no-core | revise / description_ready | scripts/clothing/clothing_shirts.txt:316: Clothing/BodyLocation=Shirt. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C183 | M017 |
| Base.Shirt_FormalWhite_ShortSleeve | public / no-core | revise / description_ready | scripts/clothing/clothing_shirts.txt:330: Clothing/BodyLocation=ShortSleeveShirt. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C183 | M017 |
| Base.Shirt_FormalWhite_ShortSleeveTINT | public / no-core | revise / description_ready | scripts/clothing/clothing_shirts.txt:344: Clothing/BodyLocation=ShortSleeveShirt. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C183 | M017 |
| Base.Shirt_HawaiianRed | public / no-core | revise / description_ready | scripts/clothing/clothing_shirts.txt:372: Clothing/BodyLocation=ShortSleeveShirt. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C183 | M017 |
| Base.Shirt_HawaiianTINT | public / no-core | revise / description_ready | scripts/clothing/clothing_shirts.txt:386: Clothing/BodyLocation=ShortSleeveShirt. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C183 | M017 |
| Base.Shirt_Jockey01 | public / core | keep / description_ready | scripts/clothing/clothing_shirts.txt:103의 Clothing/BodyLocation=Shirt와 현재 착용 목적 일치. 수치 추가나 감염/위장 효과를 강제하지 않는다. | C018 | M018 |
| Base.Shirt_Jockey02 | public / core | keep / description_ready | scripts/clothing/clothing_shirts.txt:117의 Clothing/BodyLocation=Shirt와 현재 착용 목적 일치. 수치 추가나 감염/위장 효과를 강제하지 않는다. | C018 | M018 |
| Base.Shirt_Jockey03 | public / core | keep / description_ready | scripts/clothing/clothing_shirts.txt:131의 Clothing/BodyLocation=Shirt와 현재 착용 목적 일치. 수치 추가나 감염/위장 효과를 강제하지 않는다. | C018 | M018 |
| Base.Shirt_Jockey04 | public / core | keep / description_ready | scripts/clothing/clothing_shirts.txt:145의 Clothing/BodyLocation=Shirt와 현재 착용 목적 일치. 수치 추가나 감염/위장 효과를 강제하지 않는다. | C018 | M018 |
| Base.Shirt_Jockey05 | public / core | keep / description_ready | scripts/clothing/clothing_shirts.txt:159의 Clothing/BodyLocation=Shirt와 현재 착용 목적 일치. 수치 추가나 감염/위장 효과를 강제하지 않는다. | C018 | M018 |
| Base.Shirt_Jockey06 | public / core | keep / description_ready | scripts/clothing/clothing_shirts.txt:173의 Clothing/BodyLocation=Shirt와 현재 착용 목적 일치. 수치 추가나 감염/위장 효과를 강제하지 않는다. | C018 | M018 |
| Base.Shirt_Lumberjack | public / no-core | revise / description_ready | scripts/clothing/clothing_shirts.txt:187: Clothing/BodyLocation=Shirt. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C183 | M017 |
| Base.Shirt_OfficerWhite | public / no-core | revise / description_ready | scripts/clothing/clothing_shirts.txt:201: Clothing/BodyLocation=Shirt. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C183 | M017 |
| Base.Shirt_PoliceBlue | public / no-core | revise / description_ready | scripts/clothing/clothing_shirts.txt:215: Clothing/BodyLocation=Shirt. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C183 | M017 |
| Base.Shirt_PoliceGrey | public / no-core | revise / description_ready | scripts/clothing/clothing_shirts.txt:229: Clothing/BodyLocation=Shirt. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C183 | M017 |
| Base.Shirt_Priest | public / core | keep / description_ready | scripts/clothing/clothing_shirts.txt:257의 Clothing/BodyLocation=Shirt와 현재 착용 목적 일치. 수치 추가나 감염/위장 효과를 강제하지 않는다. | C018 | M018 |
| Base.Shirt_PrisonGuard | public / no-core | revise / description_ready | scripts/clothing/clothing_shirts.txt:243: Clothing/BodyLocation=Shirt. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C183 | M017 |
| Base.Shirt_Ranger | public / core | keep / description_ready | scripts/clothing/clothing_shirts.txt:274의 Clothing/BodyLocation=Shirt와 현재 착용 목적 일치. 수치 추가나 감염/위장 효과를 강제하지 않는다. | C018 | M018 |
| Base.Shirt_Scrubs | public / no-core | revise / description_ready | scripts/clothing/clothing_shirts.txt:288: Clothing/BodyLocation=Shirt. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C183 | M017 |
| Base.Shirt_Workman | public / no-core | revise / description_ready | scripts/clothing/clothing_shirts.txt:358: Clothing/BodyLocation=Shirt. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C183 | M017 |
| Base.Shoes_ArmyBoots | public / no-core | revise / description_ready | scripts/clothing/clothing_shoes.txt:42: Clothing/BodyLocation=Shoes. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C216 | M017 |
| Base.Shoes_ArmyBootsDesert | public / no-core | revise / description_ready | scripts/clothing/clothing_shoes.txt:63: Clothing/BodyLocation=Shoes. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C216 | M017 |
| Base.Shoes_Black | public / no-core | revise / description_ready | scripts/clothing/clothing_shoes.txt:84: Clothing/BodyLocation=Shoes. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C216 | M017 |
| Base.Shoes_BlackBoots | public / no-core | revise / description_ready | scripts/clothing/clothing_shoes.txt:105: Clothing/BodyLocation=Shoes. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C216 | M017 |
| Base.Shoes_BlueTrainers | public / no-core | revise / description_ready | scripts/clothing/clothing_shoes.txt:126: Clothing/BodyLocation=Shoes. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C216 | M017 |
| Base.Shoes_Bowling | public / no-core | revise / description_ready | scripts/clothing/clothing_shoes.txt:297: Clothing/BodyLocation=Shoes. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C216 | M017 |
| Base.Shoes_Brown | public / no-core | revise / description_ready | scripts/clothing/clothing_shoes.txt:145: Clothing/BodyLocation=Shoes. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C216 | M017 |
| Base.Shoes_Fancy | public / no-core | revise / description_ready | scripts/clothing/clothing_shoes.txt:318: Clothing/BodyLocation=Shoes. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C216 | M017 |
| Base.Shoes_FlipFlop | public / no-core | revise / description_ready | scripts/clothing/clothing_shoes.txt:281: Clothing/BodyLocation=Shoes. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C216 | M017 |
| Base.Shoes_Random | public / no-core | revise / description_ready | scripts/clothing/clothing_shoes.txt:165: Clothing/BodyLocation=Shoes. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C216 | M017 |
| Base.Shoes_RedTrainers | public / no-core | revise / description_ready | scripts/clothing/clothing_shoes.txt:185: Clothing/BodyLocation=Shoes. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C216 | M017 |
| Base.Shoes_RidingBoots | public / no-core | revise / description_ready | scripts/clothing/clothing_shoes.txt:204: Clothing/BodyLocation=Shoes. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C216 | M017 |
| Base.Shoes_Sandals | public / no-core | revise / description_ready | scripts/clothing/clothing_shoes.txt:339: Clothing/BodyLocation=Shoes. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C216 | M017 |
| Base.Shoes_Slippers | public / no-core | revise / description_ready | scripts/clothing/clothing_shoes.txt:225: Clothing/BodyLocation=Shoes. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C216 | M017 |
| Base.Shoes_Strapped | public / no-core | revise / description_ready | scripts/clothing/clothing_shoes.txt:360: Clothing/BodyLocation=Shoes. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C216 | M017 |
| Base.Shoes_TrainerTINT | public / no-core | revise / description_ready | scripts/clothing/clothing_shoes.txt:241: Clothing/BodyLocation=Shoes. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C216 | M017 |
| Base.Shoes_Wellies | public / no-core | revise / description_ready | scripts/clothing/clothing_shoes.txt:260: Clothing/BodyLocation=Shoes. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C216 | M017 |
| Base.Shorts_BoxingBlue | public / core | keep / description_ready | scripts/clothing/clothing_pants.txt:104의 Clothing/BodyLocation=Pants와 현재 착용 목적 일치. 수치 추가나 감염/위장 효과를 강제하지 않는다. | C018 | M018 |
| Base.Shorts_BoxingRed | public / core | keep / description_ready | scripts/clothing/clothing_pants.txt:91의 Clothing/BodyLocation=Pants와 현재 착용 목적 일치. 수치 추가나 감염/위장 효과를 강제하지 않는다. | C018 | M018 |
| Base.Shorts_CamoGreenLong | public / no-core | revise / description_ready | scripts/clothing/clothing_pants.txt:17: Clothing/BodyLocation=Pants. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C190 | M017 |
| Base.Shorts_CamoUrbanLong | public / no-core | revise / description_ready | scripts/clothing/clothing_pants.txt:32: Clothing/BodyLocation=Pants. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C190 | M017 |
| Base.Shorts_LongDenim | public / no-core | revise / description_ready | scripts/clothing/clothing_pants.txt:47: Clothing/BodyLocation=Pants. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C190 | M017 |
| Base.Shorts_LongSport | public / no-core | revise / description_ready | scripts/clothing/clothing_pants.txt:63: Clothing/BodyLocation=Pants. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C190 | M017 |
| Base.Shorts_LongSport_Red | public / no-core | revise / description_ready | scripts/clothing/clothing_pants.txt:77: Clothing/BodyLocation=Pants. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C190 | M017 |
| Base.Shorts_ShortDenim | public / no-core | revise / description_ready | scripts/clothing/clothing_pants.txt:117: Clothing/BodyLocation=Pants. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C190 | M017 |
| Base.Shorts_ShortFormal | public / no-core | revise / description_ready | scripts/clothing/clothing_pants.txt:133: Clothing/BodyLocation=Pants. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C190 | M017 |
| Base.Shorts_ShortSport | public / no-core | revise / description_ready | scripts/clothing/clothing_pants.txt:147: Clothing/BodyLocation=Pants. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C190 | M017 |
| Base.Shotgun | public / core | keep / description_ready | exact ranged shotgun 선언과 현재 기본 사격 용도가 일치한다. | C003 | M093 |
| Base.ShotgunCase1 | public / core | revise / description_ready | scripts/newBags.txt:106의 exact Container/Capacity=7. 보관·운반 역할이 명확하며 이름에 따른 내용물 제한/냉장 효과는 추가하지 않는다. | C022 | M023 |
| Base.ShotgunCase2 | public / core | revise / description_ready | scripts/newBags.txt:256의 exact Container/Capacity=7. 보관·운반 역할이 명확하며 이름에 따른 내용물 제한/냉장 효과는 추가하지 않는다. | C022 | M023 |
| Base.ShotgunSawnoff | public / no-core | keep / acquisition_only | 각 exact ranged Weapon 선언과 사격 목적을 대조했다. empty-core를 문구만으로 채우지 않는다. | C003 | M094 |
| Base.ShotgunShells | public / core | revise / description_ready | §후속 item별 판정: exact 상자 input/result 또는 낱알 AmmoType 관계를 확인했다. | C001 | M001 |
| Base.ShotgunShellsBox | public / core | revise / description_ready | §후속 item별 판정: exact 상자 input/result 또는 낱알 AmmoType 관계를 확인했다. | C001 | M001 |
| Base.ShotgunShellsMold | public / core | review_hold / review_required | scripts/newitems.txt:3942: 탄약 주조 recipe의 exact keep 관계는 읽었으나 legacy forge/Blacksmith의 활성 사용 조건을 결속하지 못했다. 남은 입력은 정상 B41에서 이 legacy 단조 recipe/Anvil·Blacksmith 기술을 사용할 수 있는 근거 또는 실제 활성 대체 경로다. source successor 미발행이나 기존 core 부재 자체를 보류 사유로 삼지 않음. | C002 | M216 |
| Base.Shovel | public / no-core | revise / description_ready | scripts/items_weapons.txt:1727; exact DigPlow tag → ISFarmingMenu:20의 not-broken 도구 선택. 다른 작업의 가능/불가능을 추정하지 않는다. | C091 | M104 |
| Base.Shovel2 | public / no-core | revise / description_ready | scripts/items_weapons.txt:1775; exact DigPlow tag → ISFarmingMenu:20의 not-broken 도구 선택. 다른 작업의 가능/불가능을 추정하지 않는다. | C091 | M104 |
| Base.Shrimp | public / core | revise / description_ready | scripts/items_food.txt:6848의 exact H=-10, T=미선언; EvolvedRecipe 재료 선언 확인; DangerousUncooked=TRUE. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C063 | M004 |
| Base.ShrimpDumpling | public / core | revise / description_ready | scripts/items_food.txt:6873의 exact H=-15, T=미선언; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C004 | M004 |
| Base.ShrimpFried | public / core | revise / description_ready | scripts/items_food.txt:6894의 exact H=-15, T=미선언; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C004 | M004 |
| Base.ShrimpFriedCraft | public / no-core | revise / description_ready | scripts/items_food.txt:6913의 exact H=-15, T=미선언; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C004 | M004 |
| Base.SilkMothCaterpillar | public / core | revise / description_ready | scripts/items_food.txt:8984의 exact H=-5, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C012 | M012 |
| Base.Skirt_Knees | public / no-core | revise / description_ready | scripts/clothing/clothing_pants.txt:161: Clothing/BodyLocation=Skirt. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C217 | M017 |
| Base.Skirt_Long | public / no-core | revise / description_ready | scripts/clothing/clothing_pants.txt:189: Clothing/BodyLocation=Skirt. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C217 | M017 |
| Base.Skirt_Mini | public / no-core | revise / description_ready | scripts/clothing/clothing_pants.txt:175: Clothing/BodyLocation=Skirt. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C217 | M017 |
| Base.Skirt_Normal | public / no-core | revise / description_ready | scripts/clothing/clothing_pants.txt:204: Clothing/BodyLocation=Skirt. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C217 | M017 |
| Base.Skirt_Short | public / no-core | revise / description_ready | scripts/clothing/clothing_pants.txt:219: Clothing/BodyLocation=Skirt. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C217 | M017 |
| Base.Sledgehammer | public / no-core | revise / description_ready | scripts/items_weapons.txt:2868; exact Sledgehammer tag/type, ISBuildMenu:265–270의 onDestroy 및 서버 AllowDestructionBySledgehammer 조건. | C151 | M173 |
| Base.Sledgehammer2 | public / no-core | revise / description_ready | scripts/items_weapons.txt:2917; exact Sledgehammer tag/type, ISBuildMenu:265–270의 onDestroy 및 서버 AllowDestructionBySledgehammer 조건. | C151 | M173 |
| Base.Sling | public / core | keep / description_ready | scripts/newitems.txt:2528; exact WeaponPart/PartType=Sling/MountOn=HuntingRifle; VarmintRifle; Shotgun. 총기 개조 부품이라는 current 목적은 구체적. 실제 성능·조명/총검 공격은 추가하지 않는다. | C014 | M014 |
| Base.Slug | public / core | revise / description_ready | scripts/items_food.txt:9044의 exact H=-5, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음; DangerousUncooked=TRUE. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C032 | M012 |
| Base.Slug2 | public / core | revise / description_ready | scripts/items_food.txt:9065의 exact H=-5, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음; DangerousUncooked=TRUE. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C032 | M012 |
| Base.SmallGasTank1 | public / core | revise / description_ready | scripts/vehicles/vehiclesitems.txt:491; exact VehicleType=1/MaxCapacity, template_gastank의 Gasoline container·conditionAffectsCapacity. 1/2/3을 성능 등급으로 보지 않는다. | C040 | M045 |
| Base.SmallGasTank2 | public / core | revise / description_ready | scripts/vehicles/vehiclesitems.txt:539; exact VehicleType=2/MaxCapacity, template_gastank의 Gasoline container·conditionAffectsCapacity. 1/2/3을 성능 등급으로 보지 않는다. | C040 | M045 |
| Base.SmallGasTank3 | public / core | revise / description_ready | scripts/vehicles/vehiclesitems.txt:587; exact VehicleType=3/MaxCapacity, template_gastank의 Gasoline container·conditionAffectsCapacity. 1/2/3을 성능 등급으로 보지 않는다. | C040 | M045 |
| Base.SmallSheetMetal | public / core | keep / description_ready | exact Make Metal Sheet input 역할이 작은 금속판의 현재 용도와 일치한다. | C003 | M174 |
| Base.SmallTrunk1 | public / core | revise / description_ready | scripts/vehicles/vehiclesitems.txt:694; exact VehicleType=1/MaxCapacity와 seat/trunk container 선언. 수납 부품을 모두 자유롭게 탈착 가능한 물건으로 묶지 않는다. | C041 | M046 |
| Base.SmallTrunk2 | public / core | revise / description_ready | scripts/vehicles/vehiclesitems.txt:754; exact VehicleType=2/MaxCapacity와 seat/trunk container 선언. 수납 부품을 모두 자유롭게 탈착 가능한 물건으로 묶지 않는다. | C041 | M046 |
| Base.SmallTrunk3 | public / core | revise / description_ready | scripts/vehicles/vehiclesitems.txt:799; exact VehicleType=3/MaxCapacity와 seat/trunk container 선언. 수납 부품을 모두 자유롭게 탈착 가능한 물건으로 묶지 않는다. | C041 | M046 |
| Base.Smallanimalmeat | public / no-core | revise / description_ready | scripts/items_food.txt:2156의 exact H=-15, T=미선언; EvolvedRecipe 재료 선언 확인; DangerousUncooked=TRUE. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C063 | M004 |
| Base.Smallbirdmeat | public / no-core | revise / description_ready | scripts/items_food.txt:2182의 exact H=-15, T=미선언; EvolvedRecipe 재료 선언 확인; DangerousUncooked=TRUE. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C063 | M004 |
| Base.SmashedBottle | public / no-core | revise / description_ready | scripts/items_weapons.txt:3279; exact Type=Weapon/damage=0.2–0.5. 연주·경기·배관 수리 같은 현실 기능을 추정하지 않는다. | C021 | M022 |
| Base.SmithingMag1 | public / core | revise / description_ready | §학습 문구 87개: 해당 exact SkillTrained 또는 TeachedRecipes/knowledge token의 source를 구분했다. | C026 | M053 |
| Base.SmithingMag2 | public / core | revise / description_ready | §학습 문구 87개: 해당 exact SkillTrained 또는 TeachedRecipes/knowledge token의 source를 구분했다. | C026 | M053 |
| Base.SmithingMag3 | public / core | revise / description_ready | §학습 문구 87개: 해당 exact SkillTrained 또는 TeachedRecipes/knowledge token의 source를 구분했다. | C026 | M053 |
| Base.SmithingMag4 | public / core | revise / description_ready | §학습 문구 87개: 해당 exact SkillTrained 또는 TeachedRecipes/knowledge token의 source를 구분했다. | C026 | M053 |
| Base.SmokeBomb | public / core | revise / description_ready | scripts/newitems.txt:3315의 exact SmokeRange=5. 원격/센서/타이머는 각 선언대로 별도 조건이며 모든 장치를 같은 투척/폭발 효과로 묶지 않는다. Java 내부·PZ 실제 효과는 미관찰. | C152 | M005 |
| Base.SmokeBombRemote | public / no-core | revise / description_ready | scripts/newitems.txt:3343의 exact SmokeRange=5. 원격/센서/타이머는 각 선언대로 별도 조건이며 모든 장치를 같은 투척/폭발 효과로 묶지 않는다. Java 내부·PZ 실제 효과는 미관찰. | C152 | M005 |
| Base.SmokeBombSensorV1 | public / no-core | revise / description_ready | scripts/newitems.txt:3370의 exact SmokeRange=5. 원격/센서/타이머는 각 선언대로 별도 조건이며 모든 장치를 같은 투척/폭발 효과로 묶지 않는다. Java 내부·PZ 실제 효과는 미관찰. | C152 | M005 |
| Base.SmokeBombSensorV2 | public / no-core | revise / description_ready | scripts/newitems.txt:3398의 exact SmokeRange=5. 원격/센서/타이머는 각 선언대로 별도 조건이며 모든 장치를 같은 투척/폭발 효과로 묶지 않는다. Java 내부·PZ 실제 효과는 미관찰. | C152 | M005 |
| Base.SmokeBombSensorV3 | public / no-core | revise / description_ready | scripts/newitems.txt:3426의 exact SmokeRange=5. 원격/센서/타이머는 각 선언대로 별도 조건이며 모든 장치를 같은 투척/폭발 효과로 묶지 않는다. Java 내부·PZ 실제 효과는 미관찰. | C152 | M005 |
| Base.SmokeBombTriggered | public / no-core | revise / description_ready | scripts/newitems.txt:3454의 exact SmokeRange=5. 원격/센서/타이머는 각 선언대로 별도 조건이며 모든 장치를 같은 투척/폭발 효과로 묶지 않는다. Java 내부·PZ 실제 효과는 미관찰. | C152 | M005 |
| Base.Smore | public / no-core | revise / description_ready | scripts/items_food.txt:7519의 exact H=-10, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C012 | M012 |
| Base.Snail | public / core | revise / description_ready | scripts/items_food.txt:9086의 exact H=-5, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음; DangerousUncooked=TRUE. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C032 | M012 |
| Base.SnoGlobes | public / core | revise / description_ready | scripts/items_food.txt:9512의 exact H=-10, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C012 | M012 |
| Base.SnowShovel | public / no-core | revise / description_ready | scripts/items_weapons.txt:1681; exact DigPlow tag → ISFarmingMenu:20의 not-broken 도구 선택. 다른 작업의 가능/불가능을 추정하지 않는다. | C091 | M104 |
| Base.Soap | public / core | review_hold / review_required | scripts/newitems.txt:1061: exact Type=Normal, OBSOLETE=true. 정상 B41에서 이 exact item의 생성·사용 가능성/등록이 미확정이다. 작동하는 별도 FullType으로 대체하거나 기존 no-core 때문에 보류하는 것이 아님. | C015 | M221 |
| Base.Soap2 | public / core | revise / description_ready | scripts/newitems.txt:1496; ISWorldObjectContextMenu.lua:3331/3337 exact wash soap 목록; ISWashYourself/ISWashClothing 소비·blood/dirt 제거. | C064 | M011 |
| Base.SoccerBall | public / core | review_hold / review_required | scripts/newitems.txt:721: 현재 경기 규칙에 맞춘 놀이 assertion을 실제 경기/투척 기능과 결속하지 못했다. Normal 소품이라는 선언은 경기 실행 근거가 아니다. 필요한 추가 근거는 이 exact item의 해당 행동/재료 입력 또는 효과를 명시하는 vanilla source 관계이며, current admission 부재를 해소할 승인만으로 대체하지 않음. | C002 | M033 |
| Base.Socks_Ankle | public / no-core | revise / description_ready | scripts/clothing/clothing_shoes.txt:3: Clothing/BodyLocation=Socks. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C218 | M017 |
| Base.Socks_Long | public / no-core | revise / description_ready | scripts/clothing/clothing_shoes.txt:18: Clothing/BodyLocation=Socks. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C218 | M017 |
| Base.SoupBowl | public / no-core | revise / description_ready | scripts/items_food.txt:3225의 exact H=-15, T=-15; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C061 | M012 |
| Base.Soysauce | public / core | revise / description_ready | scripts/items_food.txt:6938의 exact H=-10, T=40; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C067 | M004 |
| Base.Sparklers | public / core | keep / description_ready | Make Aerosol bomb의 exact Sparklers input으로 현재 재료 역할이 명확하다. | C003 | M076 |
| Base.Spatula | public / core | revise / description_ready | scripts/newitems.txt:4761; recipes.txt 반죽/omelette/muffin 등의 keep 입력; exact 목록은 기존 first-pass locator. | C153 | M026 |
| Base.Speaker | public / core | revise / description_ready | scripts/newitems.txt:219; recipes.txt:2071 Dismantle Speaker→Amplifier; 성공/반환량 조건은 callback 소유. | C154 | M011 |
| Base.SpearBreadKnife | public / core | revise / description_ready | scripts/items_weapons.txt:4456; exact Weapon/damage=1–1.6, Spear category. 완성 창을 보강 재료로만 설명하지 않음. | C155 | M057 |
| Base.SpearButterKnife | public / core | revise / description_ready | scripts/items_weapons.txt:4503; exact Weapon/damage=1–1.6, Spear category. 완성 창을 보강 재료로만 설명하지 않음. | C155 | M057 |
| Base.SpearCrafted | public / core | revise / description_ready | scripts/items_weapons.txt:5023; exact Weapon/damage=1–1.5, Spear category. 완성 창을 보강 재료로만 설명하지 않음. | C155 | M057 |
| Base.SpearFork | public / core | revise / description_ready | scripts/items_weapons.txt:4550; exact Weapon/damage=1–1.6, Spear category. 완성 창을 보강 재료로만 설명하지 않음. | C155 | M057 |
| Base.SpearHandFork | public / core | revise / description_ready | scripts/items_weapons.txt:4786; exact Weapon/damage=1.1–1.6, Spear category. 완성 창을 보강 재료로만 설명하지 않음. | C155 | M057 |
| Base.SpearHuntingKnife | public / core | revise / description_ready | scripts/items_weapons.txt:4881; exact Weapon/damage=1.2–1.7, Spear category. 완성 창을 보강 재료로만 설명하지 않음. | C155 | M057 |
| Base.SpearIcePick | public / core | revise / description_ready | scripts/items_weapons.txt:4976; exact Weapon/damage=1–1.6, Spear category. 완성 창을 보강 재료로만 설명하지 않음. | C155 | M057 |
| Base.SpearKnife | public / core | revise / description_ready | scripts/items_weapons.txt:5070; exact Weapon/damage=1–1.6, Spear category. 완성 창을 보강 재료로만 설명하지 않음. | C155 | M057 |
| Base.SpearLetterOpener | public / core | revise / description_ready | scripts/items_weapons.txt:4598; exact Weapon/damage=1–1.6, Spear category. 완성 창을 보강 재료로만 설명하지 않음. | C155 | M057 |
| Base.SpearMachete | public / core | revise / description_ready | scripts/items_weapons.txt:4928; exact Weapon/damage=1.3–2, Spear category. 완성 창을 보강 재료로만 설명하지 않음. | C155 | M057 |
| Base.SpearScalpel | public / core | revise / description_ready | scripts/items_weapons.txt:4645; exact Weapon/damage=1–1.6, Spear category. 완성 창을 보강 재료로만 설명하지 않음. | C155 | M057 |
| Base.SpearScissors | public / core | revise / description_ready | scripts/items_weapons.txt:4739; exact Weapon/damage=1–1.6, Spear category. 완성 창을 보강 재료로만 설명하지 않음. | C155 | M057 |
| Base.SpearScrewdriver | public / core | revise / description_ready | scripts/items_weapons.txt:4834; exact Weapon/damage=1.2–1.6, Spear category. 완성 창을 보강 재료로만 설명하지 않음. | C155 | M057 |
| Base.SpearSpoon | public / core | revise / description_ready | scripts/items_weapons.txt:4692; exact Weapon/damage=1–1.6, Spear category. 완성 창을 보강 재료로만 설명하지 않음. | C155 | M057 |
| Base.Spiffo | public / core | review_hold / review_required | scripts/newitems.txt:1953; 장난감의 Normal 정체성/원문 locator 확인; 보기·놀이·수집 action 의 실제 사용 경로는 미확정. 유사 매체의 재생·학습 기능을 전이하지 않음. 필요한 추가 근거는 이 exact item의 해당 행동/재료 입력 또는 효과를 명시하는 vanilla source 관계이며, current admission 부재를 해소할 승인만으로 대체하지 않음. | C015 | M054 |
| Base.SpiffoBig | public / core | review_hold / review_required | scripts/newitems.txt:1962; 장난감의 Normal 정체성/원문 locator 확인; 보기·놀이·수집 action 의 실제 사용 경로는 미확정. 유사 매체의 재생·학습 기능을 전이하지 않음. 필요한 추가 근거는 이 exact item의 해당 행동/재료 입력 또는 효과를 명시하는 vanilla source 관계이며, current admission 부재를 해소할 승인만으로 대체하지 않음. | C015 | M054 |
| Base.SpiffoSuit | public / no-core | revise / description_ready | scripts/clothing/clothing_suits.txt:33: Clothing/BodyLocation=FullSuit. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C219 | M017 |
| Base.SpiffoTail | public / no-core | revise / description_ready | scripts/clothing/clothing_suits.txt:48: Clothing/BodyLocation=Tail. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C188 | M017 |
| Base.Splint | public / no-core | revise / description_ready | §의료: HSplint exact 선택 → setSplint | C009 | M175 |
| Base.Sponge | public / core | review_hold / review_required | scripts/newitems.txt:731; Normal item의 세척 selector 연결 미확인; 확인된 Soap2/CleaningLiquid2 기능을 이 ID에 복사하지 않음. 필요한 추가 근거는 이 exact item의 해당 행동/재료 입력 또는 효과를 명시하는 vanilla source 관계이며, current admission 부재를 해소할 승인만으로 대체하지 않음. | C015 | M072 |
| Base.Spoon | public / core | revise / description_ready | scripts/items_weapons.txt:3659; exact Weapon/damage=0.1–0.1, 해당 Attach … to Spear input. 칼/식기·도구의 이름만으로 다른 작동을 추정하지 않음. | C047 | M057 |
| Base.Springroll | public / core | revise / description_ready | scripts/items_food.txt:6960의 exact H=-20, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C012 | M012 |
| Base.Squid | public / core | revise / description_ready | scripts/items_food.txt:7536의 exact H=-30, T=미선언; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C004 | M004 |
| Base.SquidCalamari | public / core | revise / description_ready | scripts/items_food.txt:7555의 exact H=-10, T=미선언; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C004 | M004 |
| Base.Stake | public / core | revise / description_ready | scripts/items_weapons.txt:3799; exact input:Make Tent Kit에서 해당 Make Tent Kit input 확인. item 자체를 완성 텐트로 보지 않는다. | C156 | M176 |
| Base.Stapler | public / core | review_hold / review_required | scripts/newitems.txt:4944; Normal 선언과 문구류 정체성만으로 작성·수정·종이 정리 action을 뒷받침할 수 없음; 이 exact item의 사용 handler/input 관계 필요. 필요한 추가 근거는 이 exact item의 해당 행동/재료 입력 또는 효과를 명시하는 vanilla source 관계이며, current admission 부재를 해소할 승인만으로 대체하지 않음. | C049 | M118 |
| Base.Staples | public / core | review_hold / review_required | scripts/newitems.txt:4934; Normal 선언과 문구류 정체성만으로 작성·수정·종이 정리 action을 뒷받침할 수 없음; 이 exact item의 사용 handler/input 관계 필요. 필요한 추가 근거는 이 exact item의 해당 행동/재료 입력 또는 효과를 명시하는 vanilla source 관계이며, current admission 부재를 해소할 승인만으로 대체하지 않음. | C049 | M118 |
| Base.Steak | public / core | revise / description_ready | scripts/items_food.txt:2339의 exact H=-40, T=미선언; EvolvedRecipe 재료 선언 확인; DangerousUncooked=TRUE. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C063 | M004 |
| Base.StewBowl | public / no-core | revise / description_ready | scripts/items_food.txt:3252의 exact H=-15, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C012 | M012 |
| Base.StockingsBlack | public / no-core | revise / description_ready | scripts/clothing/clothing_underwear.txt:240: Clothing/BodyLocation=UnderwearExtra1. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C220 | M017 |
| Base.StockingsBlackSemiTrans | public / no-core | revise / description_ready | scripts/clothing/clothing_underwear.txt:262: Clothing/BodyLocation=UnderwearExtra1. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C220 | M017 |
| Base.StockingsBlackTrans | public / no-core | revise / description_ready | scripts/clothing/clothing_underwear.txt:251: Clothing/BodyLocation=UnderwearExtra1. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C220 | M017 |
| Base.StockingsWhite | public / no-core | revise / description_ready | scripts/clothing/clothing_underwear.txt:317: Clothing/BodyLocation=UnderwearExtra1. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C220 | M017 |
| Base.Stone | public / core | keep / description_ready | Make Stone Hammer input이 돌망치 재료라는 현재 목적을 직접 뒷받침한다. | C003 | M177 |
| Base.Straw | public / core | review_hold / review_required | scripts/newitems.txt:4751: 주방 소품의 현실 사용을 actual 조리/상차림 interaction에 결속하지 못했다. exact 역할이 확인된 식재료/도구와 분리한다. 필요한 추가 근거는 이 exact item의 해당 행동/재료 입력 또는 효과를 명시하는 vanilla source 관계이며, current admission 부재를 해소할 승인만으로 대체하지 않음. | C002 | M082 |
| Base.String | public / core | keep / description_ready | scripts/newitems.txt:1845 Normal/DisplayCategory=Material/DisplayName=String/WorldStaticModel=String과 현행 끈 형태의 재료라는 정체성 일치. 계획 Change 2의 제한된 근거에서 안전한 정체성 유지; Twine/Wire의 recipe·기능을 추가하지 않음. | C240 | M230 |
| Base.Sugar | public / core | revise / description_ready | scripts/items_food.txt:5137의 exact H=-30, T=미선언; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C004 | M004 |
| Base.SugarBrown | public / core | revise / description_ready | scripts/items_food.txt:6977의 exact H=-30, T=미선언; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C004 | M004 |
| Base.SugarPacket | public / core | revise / description_ready | scripts/items_food.txt:9164의 exact H=-1, T=미선언; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C004 | M004 |
| Base.Suit_Jacket | public / no-core | revise / description_ready | scripts/clothing/clothing_jacket.txt:41: Clothing/BodyLocation=JacketSuit. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C203 | M017 |
| Base.Suit_JacketTINT | public / no-core | revise / description_ready | scripts/clothing/clothing_jacket.txt:60: Clothing/BodyLocation=JacketSuit. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C203 | M017 |
| Base.Suitcase | public / core | revise / description_ready | scripts/clothing/clothing_bags.txt:358의 exact Container/Capacity=16. 보관·운반 역할이 명확하며 이름에 따른 내용물 제한/냉장 효과는 추가하지 않는다. | C022 | M023 |
| Base.SunflowerSeeds | public / core | revise / description_ready | scripts/items_food.txt:3906의 exact H=-5, T=미선언; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C004 | M004 |
| Base.SushiEgg | public / core | revise / description_ready | scripts/items_food.txt:6998의 exact H=-12, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C012 | M012 |
| Base.SushiFish | public / core | revise / description_ready | scripts/items_food.txt:7015의 exact H=-12, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C012 | M012 |
| Base.SutureNeedle | public / core | revise / description_ready | §의료: HStitch exact 선택·deep wound/glass 조건 | C009 | M179 |
| Base.SutureNeedleHolder | public / core | revise / description_ready | scripts/newitems.txt:880; ISStitch.lua:76/136 소지 시 봉합 pain/time 분기; ISHealthPanel.lua:1456/1645 유리·탄환 제거 도구. 바늘 자체와 구분. | C157 | M026 |
| Base.SwallowtailCaterpillar | public / core | revise / description_ready | scripts/items_food.txt:9004의 exact H=-5, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C012 | M012 |
| Base.SwimTrunks_Blue | public / no-core | revise / description_ready | scripts/clothing/clothing_others.txt:482: Clothing/BodyLocation=Underwear. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C181 | M017 |
| Base.SwimTrunks_Green | public / no-core | revise / description_ready | scripts/clothing/clothing_others.txt:493: Clothing/BodyLocation=Underwear. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C181 | M017 |
| Base.SwimTrunks_Red | public / no-core | revise / description_ready | scripts/clothing/clothing_others.txt:504: Clothing/BodyLocation=Underwear. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C181 | M017 |
| Base.SwimTrunks_Yellow | public / no-core | revise / description_ready | scripts/clothing/clothing_others.txt:515: Clothing/BodyLocation=Underwear. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C181 | M017 |
| Base.Swimsuit_TINT | public / no-core | revise / description_ready | scripts/clothing/clothing_others.txt:526: Clothing/BodyLocation=Underwear. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C181 | M017 |
| Base.TVDinner | public / core | revise / description_ready | scripts/items_food.txt:4753의 exact H=-23, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음; DangerousUncooked=TRUE. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C032 | M012 |
| Base.TVMagazine | public / core | revise / description_ready | §후속 item별 판정: exact 읽기 효과 선언 또는 CanBeWrite/페이지·필기구 조건을 구분했다. | C044 | M051 |
| Base.TableLeg | public / core | keep / description_ready | 각 exact Weapon 선언과 근접 공격 역할을 대조했다. Chainsaw도 작동하는 엔진톱의 벌목 기능을 추가하지 않는다. | C003 | M070 |
| Base.Taco | public / core | revise / description_ready | scripts/items_food.txt:7032의 exact H=-25, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C012 | M012 |
| Base.TacoRecipe | public / no-core | revise / description_ready | scripts/items_food.txt:7594의 exact H=-5, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C012 | M012 |
| Base.TacoShell | public / core | revise / description_ready | scripts/items_food.txt:7577의 exact H=-5, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C012 | M012 |
| Base.Tarp | public / core | revise / description_ready | scripts/newitems.txt:934; exact input:Make Tent Kit; input:Make Tent Kit에서 해당 Make Tent Kit input 확인. item 자체를 완성 텐트로 보지 않는다. | C156 | M176 |
| Base.Teabag | public / core | review_hold / review_required | scripts/items.txt:523: exact Type=Normal, OBSOLETE=true. 정상 B41에서 이 exact item의 생성·사용 가능성/등록이 미확정이다. 작동하는 별도 FullType으로 대체하거나 기존 no-core 때문에 보류하는 것이 아님. | C049 | M221 |
| Base.Teabag2 | public / core | keep / description_ready | scripts/items_food.txt:4898; Food EvolvedRecipe=HotDrink:5; 차를 우려내는 재료라는 현행 용도 유지. generic Teabag과 구분. | C046 | M055 |
| Base.Teacup | public / no-core | revise / description_ready | scripts/newitems.txt:4651: CanStoreWater=TRUE, ReplaceOnUseOn=WaterSource-WaterTeacup. §빈 물 용기와 같은 exact 물 저장/전환 사실을 재사용하며 음용 안전성·현재 내용물은 추정하지 않는다. | C038 | M041 |
| Base.TennisBall | public / core | review_hold / review_required | scripts/newitems.txt:741: 현재 경기 규칙에 맞춘 놀이 assertion을 실제 경기/투척 기능과 결속하지 못했다. Normal 소품이라는 선언은 경기 실행 근거가 아니다. 필요한 추가 근거는 이 exact item의 해당 행동/재료 입력 또는 효과를 명시하는 vanilla source 관계이며, current admission 부재를 해소할 승인만으로 대체하지 않음. | C002 | M033 |
| Base.TennisRacket | public / no-core | revise / description_ready | scripts/items_weapons.txt:882; exact Type=Weapon/damage=0.3–0.5. 연주·경기·배관 수리 같은 현실 기능을 추정하지 않는다. | C021 | M022 |
| Base.Termites | public / core | revise / description_ready | scripts/items_food.txt:9024의 exact H=-1, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C012 | M012 |
| Base.Thistle | public / core | revise / description_ready | scripts/items_food.txt:8724의 exact H=-4, T=미선언; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C004 | M004 |
| Base.Thread | public / core | revise / description_ready | scripts/items.txt:43; Make Mattress input 및 ISHealthPanel.lua:1340–1379 Needle+Thread 봉합 입력. | C158 | M064 |
| Base.Thyme | public / core | revise / description_ready | scripts/items_food.txt:8643의 exact H=-1, T=미선언; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C004 | M004 |
| Base.Tie_BowTieFull | public / no-core | revise / description_ready | scripts/clothing/clothing_others.txt:331: Clothing/BodyLocation=Neck. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C209 | M017 |
| Base.Tie_BowTieWorn | public / no-core | revise / description_ready | scripts/clothing/clothing_others.txt:341: Clothing/BodyLocation=Neck. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C209 | M017 |
| Base.Tie_Full | public / no-core | revise / description_ready | scripts/clothing/clothing_others.txt:352: Clothing/BodyLocation=Neck. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C209 | M017 |
| Base.Tie_Full_Spiffo | public / no-core | revise / description_ready | scripts/clothing/clothing_others.txt:363: Clothing/BodyLocation=Neck. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C209 | M017 |
| Base.Tie_Worn | public / no-core | revise / description_ready | scripts/clothing/clothing_others.txt:374: Clothing/BodyLocation=Neck. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C209 | M017 |
| Base.Tie_Worn_Spiffo | public / no-core | revise / description_ready | scripts/clothing/clothing_others.txt:385: Clothing/BodyLocation=Neck. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C209 | M017 |
| Base.TightsBlack | public / no-core | revise / description_ready | scripts/clothing/clothing_underwear.txt:273: Clothing/BodyLocation=UnderwearExtra1. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C220 | M017 |
| Base.TightsBlackSemiTrans | public / no-core | revise / description_ready | scripts/clothing/clothing_underwear.txt:295: Clothing/BodyLocation=UnderwearExtra1. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C220 | M017 |
| Base.TightsBlackTrans | public / no-core | revise / description_ready | scripts/clothing/clothing_underwear.txt:284: Clothing/BodyLocation=UnderwearExtra1. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C220 | M017 |
| Base.TightsFishnets | public / no-core | revise / description_ready | scripts/clothing/clothing_underwear.txt:306: Clothing/BodyLocation=UnderwearExtra1. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C220 | M017 |
| Base.Timer | public / core | revise / description_ready | scripts/newitems.txt:242; input:Make Timer; recipes.txt:2215/2231 입력→TimerCrafted. | C159 | M011 |
| Base.TimerCrafted | public / no-core | revise / description_ready | scripts/newitems.txt:253; recipes.txt:2247 이후 Add Timer exact input. | C160 | M011 |
| Base.TinCanEmpty | public / core | review_hold / review_required | scripts/newitems.txt:3908: 이 빈 item의 재사용/처리 목적을 실제 전환·상호작용에 결속하지 못했다. 빈 용기라는 이름만으로 물 저장 가능성을 추가하지 않는다. 필요한 추가 근거는 이 exact item의 해당 행동/재료 입력 또는 효과를 명시하는 vanilla source 관계이며, current admission 부재를 해소할 승인만으로 대체하지 않음. | C002 | M039 |
| Base.TinOpener | public / core | revise / description_ready | scripts/items.txt:533; Tags=CanOpener; recipecode.lua:35 selector, recipes.txt:210 이후 canned opening keep. | C161 | M026 |
| Base.TinnedBeans | public / core | revise / description_ready | §조리 문구 32개: 이 exact item의 input/result/keep 역할과 원본 recipe를 분리 검토했다. | C026 | M027 |
| Base.TinnedSoup | public / core | revise / description_ready | §조리 문구 32개: 이 exact item의 input/result/keep 역할과 원본 recipe를 분리 검토했다. | C026 | M027 |
| Base.TinnedSoupOpen | public / core | revise / description_ready | scripts/items_food.txt:513; 원문 Food H<0/T<0 및 EvolvedRecipe 선언. §사과의 소비·재료 해석 재사용; 보존/안전/효과량 보장 없음. | C058 | M066 |
| Base.TirePump | public / core | keep / description_ready | 보호된 TirePump의 타이어 공기 주입 역할을 유지한다. | C003 | M180 |
| Base.Tissue | public / core | revise / description_ready | scripts/items.txt:1239; lua/server/Camping/camping_fuel.lua의 exact Tissue 키가 연료/점화 재료에 모두 등록됨. 앞 절 ISCampingMenu의 유효 연료/점화 선택과 보충·점화 경로 재사용. 청소·게임·결제 등의 미확인 기능과 분리. | C227 | M220 |
| Base.Toast | public / no-core | revise / description_ready | scripts/items_food.txt:5493의 exact H=-8, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C012 | M012 |
| Base.Tofu | public / core | revise / description_ready | scripts/items_food.txt:2292의 exact H=-10, T=미선언; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C004 | M004 |
| Base.TofuFried | public / core | revise / description_ready | scripts/items_food.txt:7050의 exact H=-15, T=미선언; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C004 | M004 |
| Base.ToiletPaper | public / core | revise / description_ready | scripts/newitems.txt:751; lua/server/Camping/camping_fuel.lua의 exact ToiletPaper 키가 연료/점화 재료에 모두 등록됨. 앞 절 ISCampingMenu의 유효 연료/점화 선택과 보충·점화 경로 재사용. 청소·게임·결제 등의 미확인 기능과 분리. | C227 | M220 |
| Base.TomatoPaste | public / core | revise / description_ready | scripts/items_food.txt:9807의 exact H=-15, T=미선언; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C004 | M004 |
| Base.Tongs | public / core | review_hold / review_required | scripts/newitems.txt:3920: 단조 recipe의 exact keep 관계는 있으나 legacy Blacksmith의 활성 작업/기술 경로와 이번 범위의 실제 사용 조건을 결속하지 못했다. 남은 입력은 정상 B41에서 이 legacy 단조 recipe/Anvil·Blacksmith 기술을 사용할 수 있는 근거 또는 실제 활성 대체 경로다. source successor 미발행이나 기존 core 부재 자체를 보류 사유로 삼지 않음. | C002 | M216 |
| Base.Toolbox | public / core | keep / description_ready | 보호된 Toolbox의 운반/보관 목적은 명확하고 exact Container 선언과 일치한다. | C003 | M183 |
| Base.Toothbrush | public / core | review_hold / review_required | scripts/newitems.txt:1476: §남은 혼합 역할: Toothbrush의 양치 actual interaction이 미결속이다. 필요한 추가 근거는 이 exact item의 해당 행동/재료 입력 또는 효과를 명시하는 vanilla source 관계이며, current admission 부재를 해소할 승인만으로 대체하지 않음. | C002 | M184 |
| Base.Toothpaste | public / core | review_hold / review_required | scripts/newitems.txt:1486: §남은 혼합 역할: Toothpaste의 양치 actual interaction이 미결속이다. 필요한 추가 근거는 이 exact item의 해당 행동/재료 입력 또는 효과를 명시하는 vanilla source 관계이며, current admission 부재를 해소할 승인만으로 대체하지 않음. | C002 | M185 |
| Base.Torch | public / core | revise / description_ready | §남은 혼합 역할: 해당 exact 조명/무선·매체/운동 source 조건을 분리했다. | C026 | M114 |
| Base.Tortilla | public / core | revise / description_ready | scripts/items_food.txt:7069의 exact H=-5, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C012 | M012 |
| Base.TortillaChips | public / core | revise / description_ready | scripts/items_food.txt:7103의 exact H=-15, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C012 | M012 |
| Base.Tote | public / core | keep / description_ready | scripts/clothing/clothing_bags.txt:308의 exact Container/Capacity=12. 보관·운반 역할이 명확하며 이름에 따른 내용물 제한/냉장 효과는 추가하지 않는다. | C023 | M023 |
| Base.ToyBear | public / core | review_hold / review_required | scripts/newitems.txt:1855; 장난감의 Normal 정체성/원문 locator 확인; 보기·놀이·수집 action 의 실제 사용 경로는 미확정. 유사 매체의 재생·학습 기능을 전이하지 않음. 필요한 추가 근거는 이 exact item의 해당 행동/재료 입력 또는 효과를 명시하는 vanilla source 관계이며, current admission 부재를 해소할 승인만으로 대체하지 않음. | C015 | M054 |
| Base.ToyCar | public / core | review_hold / review_required | scripts/newitems.txt:776; 장난감의 Normal 정체성/원문 locator 확인; 보기·놀이·수집 action 의 실제 사용 경로는 미확정. 유사 매체의 재생·학습 기능을 전이하지 않음. 필요한 추가 근거는 이 exact item의 해당 행동/재료 입력 또는 효과를 명시하는 vanilla source 관계이며, current admission 부재를 해소할 승인만으로 대체하지 않음. | C015 | M054 |
| Base.TrailerTrunk1 | public / core | revise / description_ready | scripts/vehicles/vehiclesitems.txt:844; exact VehicleType=1/MaxCapacity와 seat/trunk container 선언. 수납 부품을 모두 자유롭게 탈착 가능한 물건으로 묶지 않는다. | C041 | M046 |
| Base.TrailerTrunk2 | public / core | revise / description_ready | scripts/vehicles/vehiclesitems.txt:859; exact VehicleType=2/MaxCapacity와 seat/trunk container 선언. 수납 부품을 모두 자유롭게 탈착 가능한 물건으로 묶지 않는다. | C041 | M046 |
| Base.TrailerTrunk3 | public / core | revise / description_ready | scripts/vehicles/vehiclesitems.txt:874; exact VehicleType=3/MaxCapacity와 seat/trunk container 선언. 수납 부품을 모두 자유롭게 탈착 가능한 물건으로 묶지 않는다. | C041 | M046 |
| Base.TrapBox | public / no-core | revise / description_ready | §농사·낚시·덫: 해당 exact source 선택·조건 및 실제 결과 변화 연결 | C026 | M025 |
| Base.TrapCage | public / no-core | revise / description_ready | §농사·낚시·덫: 해당 exact source 선택·조건 및 실제 결과 변화 연결 | C026 | M025 |
| Base.TrapCrate | public / no-core | revise / description_ready | §농사·낚시·덫: 해당 exact source 선택·조건 및 실제 결과 변화 연결 | C026 | M025 |
| Base.TrapMouse | public / no-core | revise / description_ready | §농사·낚시·덫: 해당 exact source 선택·조건 및 실제 결과 변화 연결 | C026 | M025 |
| Base.TrapSnare | public / no-core | revise / description_ready | §농사·낚시·덫: 해당 exact source 선택·조건 및 실제 결과 변화 연결 | C026 | M025 |
| Base.TrapStick | public / no-core | revise / description_ready | §농사·낚시·덫: 해당 exact source 선택·조건 및 실제 결과 변화 연결 | C026 | M025 |
| Base.TreeBranch | public / core | revise / description_ready | scripts/newitems.txt:904; exact Stone Axe/Hammer/Knife, Create Spear, Make Splint input. 기능이 명확한 제작 역할로 특정. | C162 | M186 |
| Base.TriggerCrafted | public / no-core | revise / description_ready | scripts/newitems.txt:186; recipes.txt Add Crafted Trigger exact inputs; standalone radio 수신기로 확장하지 않음. | C163 | M011 |
| Base.Trousers | public / no-core | revise / description_ready | scripts/clothing/clothing_pants.txt:250: Clothing/BodyLocation=Pants. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C190 | M017 |
| Base.TrousersMesh_DenimLight | public / no-core | revise / description_ready | scripts/clothing/clothing_pants.txt:264: Clothing/BodyLocation=Pants. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C190 | M017 |
| Base.TrousersMesh_Leather | public / no-core | revise / description_ready | scripts/clothing/clothing_pants.txt:281: Clothing/BodyLocation=Pants. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C190 | M017 |
| Base.Trousers_ArmyService | public / no-core | revise / description_ready | scripts/clothing/clothing_pants.txt:687: Clothing/BodyLocation=Pants. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C190 | M017 |
| Base.Trousers_Black | public / core | keep / description_ready | scripts/clothing/clothing_pants.txt:702의 Clothing/BodyLocation=Pants와 현재 착용 목적 일치. 수치 추가나 감염/위장 효과를 강제하지 않는다. | C018 | M018 |
| Base.Trousers_CamoDesert | public / no-core | revise / description_ready | scripts/clothing/clothing_pants.txt:315: Clothing/BodyLocation=Pants. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C190 | M017 |
| Base.Trousers_CamoGreen | public / no-core | revise / description_ready | scripts/clothing/clothing_pants.txt:331: Clothing/BodyLocation=Pants. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C190 | M017 |
| Base.Trousers_CamoUrban | public / no-core | revise / description_ready | scripts/clothing/clothing_pants.txt:348: Clothing/BodyLocation=Pants. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C190 | M017 |
| Base.Trousers_Chef | public / core | keep / description_ready | scripts/clothing/clothing_pants.txt:365의 Clothing/BodyLocation=Pants와 현재 착용 목적 일치. 수치 추가나 감염/위장 효과를 강제하지 않는다. | C018 | M018 |
| Base.Trousers_DefaultTEXTURE | public / no-core | revise / description_ready | scripts/clothing/clothing_pants.txt:379: Clothing/BodyLocation=Pants. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C190 | M017 |
| Base.Trousers_DefaultTEXTURE_HUE | public / no-core | revise / description_ready | scripts/clothing/clothing_pants.txt:393: Clothing/BodyLocation=Pants. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C190 | M017 |
| Base.Trousers_DefaultTEXTURE_TINT | public / no-core | revise / description_ready | scripts/clothing/clothing_pants.txt:407: Clothing/BodyLocation=Pants. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C190 | M017 |
| Base.Trousers_Denim | public / no-core | revise / description_ready | scripts/clothing/clothing_pants.txt:421: Clothing/BodyLocation=Pants. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C190 | M017 |
| Base.Trousers_Fireman | public / no-core | revise / description_ready | scripts/clothing/clothing_pants.txt:438: Clothing/BodyLocation=Pants. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C190 | M017 |
| Base.Trousers_JeanBaggy | public / no-core | revise / description_ready | scripts/clothing/clothing_pants.txt:456: Clothing/BodyLocation=Pants. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C190 | M017 |
| Base.Trousers_LeatherBlack | public / no-core | revise / description_ready | scripts/clothing/clothing_pants.txt:298: Clothing/BodyLocation=Pants. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C190 | M017 |
| Base.Trousers_NavyBlue | public / no-core | revise / description_ready | scripts/clothing/clothing_pants.txt:720: Clothing/BodyLocation=Pants. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C190 | M017 |
| Base.Trousers_Padded | public / no-core | revise / description_ready | scripts/clothing/clothing_pants.txt:473: Clothing/BodyLocation=Pants. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C190 | M017 |
| Base.Trousers_Police | public / no-core | revise / description_ready | scripts/clothing/clothing_pants.txt:490: Clothing/BodyLocation=Pants. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C190 | M017 |
| Base.Trousers_PoliceGrey | public / no-core | revise / description_ready | scripts/clothing/clothing_pants.txt:504: Clothing/BodyLocation=Pants. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C190 | M017 |
| Base.Trousers_PrisonGuard | public / no-core | revise / description_ready | scripts/clothing/clothing_pants.txt:519: Clothing/BodyLocation=Pants. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C190 | M017 |
| Base.Trousers_Ranger | public / core | keep / description_ready | scripts/clothing/clothing_pants.txt:534의 Clothing/BodyLocation=Pants와 현재 착용 목적 일치. 수치 추가나 감염/위장 효과를 강제하지 않는다. | C018 | M018 |
| Base.Trousers_Santa | public / no-core | revise / description_ready | scripts/clothing/clothing_pants.txt:550: Clothing/BodyLocation=Pants. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C190 | M017 |
| Base.Trousers_SantaGReen | public / no-core | revise / description_ready | scripts/clothing/clothing_pants.txt:565: Clothing/BodyLocation=Pants. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C190 | M017 |
| Base.Trousers_Scrubs | public / no-core | revise / description_ready | scripts/clothing/clothing_pants.txt:580: Clothing/BodyLocation=Pants. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C190 | M017 |
| Base.Trousers_Shellsuit_Black | public / no-core | revise / description_ready | scripts/clothing/clothing_pants.txt:738: Clothing/BodyLocation=Pants. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C190 | M017 |
| Base.Trousers_Shellsuit_Blue | public / no-core | revise / description_ready | scripts/clothing/clothing_pants.txt:752: Clothing/BodyLocation=Pants. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C190 | M017 |
| Base.Trousers_Shellsuit_Green | public / no-core | revise / description_ready | scripts/clothing/clothing_pants.txt:766: Clothing/BodyLocation=Pants. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C190 | M017 |
| Base.Trousers_Shellsuit_Pink | public / no-core | revise / description_ready | scripts/clothing/clothing_pants.txt:780: Clothing/BodyLocation=Pants. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C190 | M017 |
| Base.Trousers_Shellsuit_TINT | public / no-core | revise / description_ready | scripts/clothing/clothing_pants.txt:808: Clothing/BodyLocation=Pants. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C190 | M017 |
| Base.Trousers_Shellsuit_Teal | public / no-core | revise / description_ready | scripts/clothing/clothing_pants.txt:794: Clothing/BodyLocation=Pants. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C190 | M017 |
| Base.Trousers_Suit | public / no-core | revise / description_ready | scripts/clothing/clothing_pants.txt:594: Clothing/BodyLocation=Pants. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C190 | M017 |
| Base.Trousers_SuitTEXTURE | public / no-core | revise / description_ready | scripts/clothing/clothing_pants.txt:609: Clothing/BodyLocation=Pants. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C190 | M017 |
| Base.Trousers_SuitWhite | public / no-core | revise / description_ready | scripts/clothing/clothing_pants.txt:624: Clothing/BodyLocation=Pants. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C190 | M017 |
| Base.Trousers_WhiteTEXTURE | public / no-core | revise / description_ready | scripts/clothing/clothing_pants.txt:639: Clothing/BodyLocation=Pants. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C190 | M017 |
| Base.Trousers_WhiteTINT | public / no-core | revise / description_ready | scripts/clothing/clothing_pants.txt:654: Clothing/BodyLocation=Pants. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C190 | M017 |
| Base.Trout | public / core | revise / description_ready | scripts/items_food.txt:1841의 exact H=-15, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음; DangerousUncooked=TRUE. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C032 | M012 |
| Base.Trumpet | public / no-core | revise / description_ready | scripts/items_weapons.txt:484; exact Type=Weapon/damage=0.4–0.8. 연주·경기·배관 수리 같은 현실 기능을 추정하지 않는다. | C021 | M022 |
| Base.TrunkDoor1 | public / core | keep / description_ready | scripts/vehicles/vehiclesitems.txt:1229; exact VehicleType=1와 해당 door/window/windshield part 관계. 현재 패널/유리 탈착 목적은 이미 구체적이며 방탄·방호 효과를 추가하지 않는다. | C014 | M096 |
| Base.TrunkDoor2 | public / core | keep / description_ready | scripts/vehicles/vehiclesitems.txt:1243; exact VehicleType=2와 해당 door/window/windshield part 관계. 현재 패널/유리 탈착 목적은 이미 구체적이며 방탄·방호 효과를 추가하지 않는다. | C014 | M096 |
| Base.TrunkDoor3 | public / core | keep / description_ready | scripts/vehicles/vehiclesitems.txt:1257; exact VehicleType=3와 해당 door/window/windshield part 관계. 현재 패널/유리 탈착 목적은 이미 구체적이며 방탄·방호 효과를 추가하지 않는다. | C014 | M096 |
| Base.Tshirt_ArmyGreen | public / no-core | revise / description_ready | scripts/clothing/clothing_shirts.txt:400: Clothing/BodyLocation=Tshirt. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C183 | M017 |
| Base.Tshirt_BusinessSpiffo | public / no-core | revise / description_ready | scripts/clothing/clothing_shirts.txt:572: Clothing/BodyLocation=Tshirt. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C183 | M017 |
| Base.Tshirt_CamoDesert | public / no-core | revise / description_ready | scripts/clothing/clothing_shirts.txt:417: Clothing/BodyLocation=Tshirt. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C183 | M017 |
| Base.Tshirt_CamoGreen | public / no-core | revise / description_ready | scripts/clothing/clothing_shirts.txt:431: Clothing/BodyLocation=Tshirt. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C183 | M017 |
| Base.Tshirt_CamoUrban | public / no-core | revise / description_ready | scripts/clothing/clothing_shirts.txt:445: Clothing/BodyLocation=Tshirt. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C183 | M017 |
| Base.Tshirt_DefaultDECAL | public / no-core | revise / description_ready | scripts/clothing/clothing_shirts.txt:600: Clothing/BodyLocation=Tshirt. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C183 | M017 |
| Base.Tshirt_DefaultDECAL_TINT | public / no-core | revise / description_ready | scripts/clothing/clothing_shirts.txt:614: Clothing/BodyLocation=Tshirt. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C183 | M017 |
| Base.Tshirt_DefaultTEXTURE | public / no-core | revise / description_ready | scripts/clothing/clothing_shirts.txt:628: Clothing/BodyLocation=Tshirt. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C183 | M017 |
| Base.Tshirt_DefaultTEXTURE_TINT | public / no-core | revise / description_ready | scripts/clothing/clothing_shirts.txt:642: Clothing/BodyLocation=Tshirt. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C183 | M017 |
| Base.Tshirt_Fossoil | public / core | keep / description_ready | scripts/clothing/clothing_shirts.txt:459의 Clothing/BodyLocation=Tshirt와 현재 착용 목적 일치. 수치 추가나 감염/위장 효과를 강제하지 않는다. | C018 | M018 |
| Base.Tshirt_Gas2Go | public / core | keep / description_ready | scripts/clothing/clothing_shirts.txt:476의 Clothing/BodyLocation=Tshirt와 현재 착용 목적 일치. 수치 추가나 감염/위장 효과를 강제하지 않는다. | C018 | M018 |
| Base.Tshirt_IndieStoneDECAL | public / no-core | revise / description_ready | scripts/clothing/clothing_shirts.txt:740: Clothing/BodyLocation=Tshirt. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C183 | M017 |
| Base.Tshirt_McCoys | public / core | keep / description_ready | scripts/clothing/clothing_shirts.txt:527의 Clothing/BodyLocation=Tshirt와 현재 착용 목적 일치. 수치 추가나 감염/위장 효과를 강제하지 않는다. | C018 | M018 |
| Base.Tshirt_PileOCrepe | public / no-core | revise / description_ready | scripts/clothing/clothing_shirts.txt:544: Clothing/BodyLocation=Tshirt. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C183 | M017 |
| Base.Tshirt_PizzaWhirled | public / no-core | revise / description_ready | scripts/clothing/clothing_shirts.txt:558: Clothing/BodyLocation=Tshirt. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C183 | M017 |
| Base.Tshirt_PoliceBlue | public / no-core | revise / description_ready | scripts/clothing/clothing_shirts.txt:656: Clothing/BodyLocation=Tshirt. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C183 | M017 |
| Base.Tshirt_PoliceGrey | public / no-core | revise / description_ready | scripts/clothing/clothing_shirts.txt:670: Clothing/BodyLocation=Tshirt. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C183 | M017 |
| Base.Tshirt_PoloStripedTINT | public / no-core | revise / description_ready | scripts/clothing/clothing_shirts.txt:684: Clothing/BodyLocation=Tshirt. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C183 | M017 |
| Base.Tshirt_PoloTINT | public / no-core | revise / description_ready | scripts/clothing/clothing_shirts.txt:698: Clothing/BodyLocation=Tshirt. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C183 | M017 |
| Base.Tshirt_Profession_FiremanBlue | public / no-core | revise / description_ready | scripts/clothing/clothing_shirts.txt:1034: Clothing/BodyLocation=Tshirt. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C183 | M017 |
| Base.Tshirt_Profession_FiremanRed | public / no-core | revise / description_ready | scripts/clothing/clothing_shirts.txt:1051: Clothing/BodyLocation=Tshirt. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C183 | M017 |
| Base.Tshirt_Profession_FiremanRed02 | public / no-core | revise / description_ready | scripts/clothing/clothing_shirts.txt:1068: Clothing/BodyLocation=Tshirt. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C183 | M017 |
| Base.Tshirt_Profession_FiremanWhite | public / no-core | revise / description_ready | scripts/clothing/clothing_shirts.txt:1085: Clothing/BodyLocation=Tshirt. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C183 | M017 |
| Base.Tshirt_Profession_PoliceBlue | public / core | keep / description_ready | scripts/clothing/clothing_shirts.txt:1099의 Clothing/BodyLocation=Tshirt와 현재 착용 목적 일치. 수치 추가나 감염/위장 효과를 강제하지 않는다. | C018 | M018 |
| Base.Tshirt_Profession_PoliceWhite | public / core | keep / description_ready | scripts/clothing/clothing_shirts.txt:1116의 Clothing/BodyLocation=Tshirt와 현재 착용 목적 일치. 수치 추가나 감염/위장 효과를 강제하지 않는다. | C018 | M018 |
| Base.Tshirt_Profession_RangerBrown | public / core | keep / description_ready | scripts/clothing/clothing_shirts.txt:1130의 Clothing/BodyLocation=Tshirt와 현재 착용 목적 일치. 수치 추가나 감염/위장 효과를 강제하지 않는다. | C018 | M018 |
| Base.Tshirt_Profession_RangerGreen | public / core | keep / description_ready | scripts/clothing/clothing_shirts.txt:1147의 Clothing/BodyLocation=Tshirt와 현재 착용 목적 일치. 수치 추가나 감염/위장 효과를 강제하지 않는다. | C018 | M018 |
| Base.Tshirt_Profession_VeterenGreen | public / no-core | revise / description_ready | scripts/clothing/clothing_shirts.txt:1164: Clothing/BodyLocation=Tshirt. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C183 | M017 |
| Base.Tshirt_Profession_VeterenRed | public / no-core | revise / description_ready | scripts/clothing/clothing_shirts.txt:1181: Clothing/BodyLocation=Tshirt. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C183 | M017 |
| Base.Tshirt_Ranger | public / core | keep / description_ready | scripts/clothing/clothing_shirts.txt:712의 Clothing/BodyLocation=Tshirt와 현재 착용 목적 일치. 수치 추가나 감염/위장 효과를 강제하지 않는다. | C018 | M018 |
| Base.Tshirt_Rock | public / no-core | revise / description_ready | scripts/clothing/clothing_shirts.txt:510: Clothing/BodyLocation=Tshirt. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C183 | M017 |
| Base.Tshirt_Scrubs | public / no-core | revise / description_ready | scripts/clothing/clothing_shirts.txt:726: Clothing/BodyLocation=Tshirt. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C183 | M017 |
| Base.Tshirt_SpiffoDECAL | public / no-core | revise / description_ready | scripts/clothing/clothing_shirts.txt:754: Clothing/BodyLocation=Tshirt. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C183 | M017 |
| Base.Tshirt_Sport | public / no-core | revise / description_ready | scripts/clothing/clothing_shirts.txt:768: Clothing/BodyLocation=Tshirt. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C183 | M017 |
| Base.Tshirt_SportDECAL | public / no-core | revise / description_ready | scripts/clothing/clothing_shirts.txt:782: Clothing/BodyLocation=Tshirt. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C183 | M017 |
| Base.Tshirt_ThunderGas | public / core | keep / description_ready | scripts/clothing/clothing_shirts.txt:493의 Clothing/BodyLocation=Tshirt와 현재 착용 목적 일치. 수치 추가나 감염/위장 효과를 강제하지 않는다. | C018 | M018 |
| Base.Tshirt_ValleyStation | public / no-core | revise / description_ready | scripts/clothing/clothing_shirts.txt:586: Clothing/BodyLocation=Tshirt. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C183 | M017 |
| Base.Tshirt_WhiteLongSleeve | public / no-core | revise / description_ready | scripts/clothing/clothing_shirts.txt:796: Clothing/BodyLocation=Tshirt. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C183 | M017 |
| Base.Tshirt_WhiteLongSleeveTINT | public / no-core | revise / description_ready | scripts/clothing/clothing_shirts.txt:810: Clothing/BodyLocation=Tshirt. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C183 | M017 |
| Base.Tshirt_WhiteTINT | public / no-core | revise / description_ready | scripts/clothing/clothing_shirts.txt:824: Clothing/BodyLocation=Tshirt. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C183 | M017 |
| Base.TunaTin | public / core | revise / description_ready | §조리 문구 32개: 이 exact item의 input/result/keep 역할과 원본 recipe를 분리 검토했다. | C026 | M027 |
| Base.TunaTinOpen | public / core | revise / description_ready | scripts/items_food.txt:561의 exact H=-18, T=미선언; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C004 | M004 |
| Base.Tweezers | public / core | keep / description_ready | RemoveBullet/RemoveGlass exact tags와 ISHealthPanel 선택이 현재 의료 도구 용도와 일치한다. | C003 | M187 |
| Base.Twigs | public / core | keep / description_ready | exact Make Campfire Kit input 역할을 재사용한다. | C003 | M188 |
| Base.Twine | public / core | keep / description_ready | 각 exact input의 덫/어망 관계를 확인했다. Twine과 Wire의 서로 다른 recipe set을 하나로 합치지 않는다. | C003 | M189 |
| Base.Umbrella | public / core | review_hold / review_required | scripts/newitems.txt:1261: exact Type=Normal, OBSOLETE=TRUE. 정상 B41에서 이 exact item의 생성·사용 가능성/등록이 미확정이다. 작동하는 별도 FullType으로 대체하거나 기존 no-core 때문에 보류하는 것이 아님. | C015 | M221 |
| Base.UmbrellaBlack | public / core | revise / description_ready | scripts/newitems.txt:1271; ProtectFromRainWhenEquipped=true; recipes.txt:3653–3712 동일 색 접기/펼치기 연결. | C164 | M011 |
| Base.UmbrellaBlue | public / core | revise / description_ready | scripts/newitems.txt:1303; ProtectFromRainWhenEquipped=true; recipes.txt:3653–3712 동일 색 접기/펼치기 연결. | C164 | M011 |
| Base.UmbrellaRed | public / core | revise / description_ready | scripts/newitems.txt:1319; ProtectFromRainWhenEquipped=true; recipes.txt:3653–3712 동일 색 접기/펼치기 연결. | C164 | M011 |
| Base.UmbrellaWhite | public / core | revise / description_ready | scripts/newitems.txt:1287; ProtectFromRainWhenEquipped=true; recipes.txt:3653–3712 동일 색 접기/펼치기 연결. | C164 | M011 |
| Base.Underpants_AnimalPrint | public / no-core | revise / description_ready | scripts/clothing/clothing_underwear.txt:483: Clothing/BodyLocation=UnderwearBottom. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C184 | M017 |
| Base.Underpants_Black | public / no-core | revise / description_ready | scripts/clothing/clothing_underwear.txt:69: Clothing/BodyLocation=UnderwearBottom. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C184 | M017 |
| Base.Underpants_RedSpots | public / no-core | revise / description_ready | scripts/clothing/clothing_underwear.txt:84: Clothing/BodyLocation=UnderwearBottom. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C184 | M017 |
| Base.Underpants_White | public / no-core | revise / description_ready | scripts/clothing/clothing_underwear.txt:96: Clothing/BodyLocation=UnderwearBottom. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C184 | M017 |
| Base.Underwear1 | empty / no-core | review_hold / review_required | scripts/newitems.txt:786: exact Type=Normal, OBSOLETE=TRUE. 정상 B41에서 이 exact item의 생성·사용 가능성/등록이 미확정이다. 작동하는 별도 FullType으로 대체하거나 기존 no-core 때문에 보류하는 것이 아님. | C052 | M221 |
| Base.Underwear2 | empty / no-core | review_hold / review_required | scripts/newitems.txt:796: exact Type=Normal, OBSOLETE=TRUE. 정상 B41에서 이 exact item의 생성·사용 가능성/등록이 미확정이다. 작동하는 별도 FullType으로 대체하거나 기존 no-core 때문에 보류하는 것이 아님. | C052 | M221 |
| Base.UnusableMetal | public / core | review_hold / review_required | scripts/newitems.txt:87: 해체 잔재의 identity와 별개로 '재료로 쓸 수 없음'이라는 전면 부정의 범위를 입증하지 못했다. ISMoveableDefinitions.lua:353–366의 금속 해체 실패 산출물은 확인. 이것은 모든 제작 사용이 불가능하다는 증거가 아니므로 전면 부정을 채택하지 않음. | C002 | M191 |
| Base.UnusableWood | public / core | keep / description_ready | 기존 승인 모닥불 연료 용도를 유지한다. 다른 제작재료 가능성이나 전면적 기능 부재를 추가하지 않는다. | C003 | M192 |
| Base.VHS | public / core | review_hold / review_required | scripts/newitems.txt:4479; Normal base item과 runtime recorded-media 데이터 binding 미확인; MediaCategory가 있는 Retail/Home variant의 재생 기능 복사 금지. 필요한 입력은 이 generic FullType에 recorded-media ID/type을 부여하는 producer 또는 실제 인스턴스 binding; Retail/Home 선언을 복사하지 않음. | C015 | M089 |
| Base.VHS_Home | public / core | revise / description_ready | scripts/newitems.txt:4500; MediaCategory 선언; RWMMedia.lua:91 isRecordedMedia/MediaType와 ISRadioAction.lua:174/StartPlayMedia. 실제 녹화 내용은 인스턴스별로 다름. | C078 | M090 |
| Base.VHS_Retail | public / core | revise / description_ready | scripts/newitems.txt:4489; MediaCategory 선언; RWMMedia.lua:91 isRecordedMedia/MediaType와 ISRadioAction.lua:174/StartPlayMedia. 실제 녹화 내용은 인스턴스별로 다름. | C078 | M090 |
| Base.VanSeatsTrunk2 | public / core | revise / description_ready | scripts/vehicles/vehiclesitems.txt:739; exact VehicleType=2/MaxCapacity와 seat/trunk container 선언. 수납 부품을 모두 자유롭게 탈착 가능한 물건으로 묶지 않는다. | C041 | M046 |
| Base.VarmintRifle | public / core | revise / description_ready | scripts/items_weapons.txt:5119 exact ranged Weapon 및 소총 AmmoType. RifleCase와 섞인 current 문구를 분리한다. | C019 | M019 |
| Base.Vest_BulletArmy | public / no-core | revise / description_ready | scripts/clothing/clothing_shirts.txt:880: Clothing/BodyLocation=TorsoExtraVest. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C221 | M017 |
| Base.Vest_BulletCivilian | public / no-core | revise / description_ready | scripts/clothing/clothing_shirts.txt:896: Clothing/BodyLocation=TorsoExtraVest. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C221 | M017 |
| Base.Vest_BulletPolice | public / no-core | revise / description_ready | scripts/clothing/clothing_shirts.txt:912: Clothing/BodyLocation=TorsoExtraVest. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C221 | M017 |
| Base.Vest_DefaultTEXTURE | public / no-core | revise / description_ready | scripts/clothing/clothing_shirts.txt:928: Clothing/BodyLocation=TankTop. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C183 | M017 |
| Base.Vest_DefaultTEXTURE_TINT | public / no-core | revise / description_ready | scripts/clothing/clothing_shirts.txt:942: Clothing/BodyLocation=TankTop. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C183 | M017 |
| Base.Vest_Foreman | public / no-core | revise / description_ready | scripts/clothing/clothing_shirts.txt:1008: Clothing/BodyLocation=TorsoExtraVest. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C221 | M017 |
| Base.Vest_HighViz | public / no-core | revise / description_ready | scripts/clothing/clothing_shirts.txt:1021: Clothing/BodyLocation=TorsoExtraVest. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C221 | M017 |
| Base.Vest_Hunting_Camo | public / no-core | revise / description_ready | scripts/clothing/clothing_shirts.txt:982: Clothing/BodyLocation=TorsoExtraVest. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C221 | M017 |
| Base.Vest_Hunting_CamoGreen | public / no-core | revise / description_ready | scripts/clothing/clothing_shirts.txt:995: Clothing/BodyLocation=TorsoExtraVest. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C221 | M017 |
| Base.Vest_Hunting_Grey | public / no-core | revise / description_ready | scripts/clothing/clothing_shirts.txt:956: Clothing/BodyLocation=TorsoExtraVest. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C221 | M017 |
| Base.Vest_Hunting_Orange | public / no-core | revise / description_ready | scripts/clothing/clothing_shirts.txt:969: Clothing/BodyLocation=TorsoExtraVest. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C221 | M017 |
| Base.Vest_Waistcoat | public / no-core | revise / description_ready | scripts/clothing/clothing_shirts.txt:838: Clothing/BodyLocation=TorsoExtra. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C178 | M017 |
| Base.Vest_WaistcoatTINT | public / no-core | revise / description_ready | scripts/clothing/clothing_shirts.txt:852: Clothing/BodyLocation=TorsoExtra. §기본 착용 재판정의 일반 Wear→ISWearClothing 경로 및 Human 슬롯 선언을 exact item에 연결. 기존 no-core는 채택 상태로 보존; 확인된 기본 착용 새 core 후보의 source 준비와 채택·generation 미실행을 분리. | C178 | M017 |
| Base.Vest_Waistcoat_GigaMart | public / core | keep / description_ready | scripts/clothing/clothing_shirts.txt:866의 Clothing/BodyLocation=TorsoExtra와 현재 착용 목적 일치. 수치 추가나 감염/위장 효과를 강제하지 않는다. | C018 | M018 |
| Base.VideoGame | public / core | revise / description_ready | scripts/newitems.txt:36; recipes.txt:2040/2055 Dismantle→ElectronicsScrap, screwdriver·OnTest 조건. | C071 | M011 |
| Base.Vinegar | public / core | revise / description_ready | §조리 문구 32개: 이 exact item의 input/result/keep 역할과 원본 recipe를 분리 검토했다. | C026 | M027 |
| Base.Violets | public / core | revise / description_ready | scripts/items_food.txt:4193의 exact H=-2, T=미선언; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C004 | M004 |
| Base.Violin | public / no-core | revise / description_ready | scripts/items_weapons.txt:524; exact Type=Weapon/damage=0.2–0.4. 연주·경기·배관 수리 같은 현실 기능을 추정하지 않는다. | C021 | M022 |
| Base.Waffles | public / no-core | revise / description_ready | scripts/items_food.txt:3724의 exact H=-15, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C012 | M012 |
| Base.WafflesRecipe | public / core | revise / description_ready | scripts/items_food.txt:3743의 exact H=-15, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C012 | M012 |
| Base.Wallet | public / core | review_hold / review_required | scripts/newitems.txt:1881: 현금/카드/지갑 identity 외 사용·수납 상호작용이 미결속이다. Normal 지갑을 Container나 결제 기능으로 설명하지 않는다. 필요한 추가 근거는 이 exact item의 해당 행동/재료 입력 또는 효과를 명시하는 vanilla source 관계이며, current admission 부재를 해소할 승인만으로 대체하지 않음. | C002 | M084 |
| Base.Wallet2 | public / core | review_hold / review_required | scripts/newitems.txt:1891: 현금/카드/지갑 identity 외 사용·수납 상호작용이 미결속이다. Normal 지갑을 Container나 결제 기능으로 설명하지 않는다. 필요한 추가 근거는 이 exact item의 해당 행동/재료 입력 또는 효과를 명시하는 vanilla source 관계이며, current admission 부재를 해소할 승인만으로 대체하지 않음. | C002 | M084 |
| Base.Wallet3 | public / core | review_hold / review_required | scripts/newitems.txt:1901: 현금/카드/지갑 identity 외 사용·수납 상호작용이 미결속이다. Normal 지갑을 Container나 결제 기능으로 설명하지 않는다. 필요한 추가 근거는 이 exact item의 해당 행동/재료 입력 또는 효과를 명시하는 vanilla source 관계이며, current admission 부재를 해소할 승인만으로 대체하지 않음. | C002 | M084 |
| Base.Wallet4 | public / core | review_hold / review_required | scripts/newitems.txt:1911: 현금/카드/지갑 identity 외 사용·수납 상호작용이 미결속이다. Normal 지갑을 Container나 결제 기능으로 설명하지 않는다. 필요한 추가 근거는 이 exact item의 해당 행동/재료 입력 또는 효과를 명시하는 vanilla source 관계이며, current admission 부재를 해소할 승인만으로 대체하지 않음. | C002 | M084 |
| Base.Wasabi | public / core | revise / description_ready | scripts/items_food.txt:7122의 exact H=-10, T=20; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C067 | M004 |
| Base.WaterBleachBottle | empty / no-core | revise / description_ready | scripts/items_food.txt:2484: CanStoreWater=TRUE, ReplaceOnUseOn=WaterSource-WaterBleachBottle. §빈 물 용기와 같은 exact 물 저장/전환 사실을 재사용하며 음용 안전성·현재 내용물은 추정하지 않는다. | C038 | M041 |
| Base.WaterBottleEmpty | public / core | revise / description_ready | scripts/items.txt:546; CanStoreWater/WaterSource 전환과 §물 용기의 기본 역할. 폭발물 제작 input만으로 기본 용도를 제한하지 않는다. | C165 | M193 |
| Base.WaterBottleFull | public / no-core | revise / description_ready | scripts/items_food.txt:2506: CanStoreWater=TRUE, ReplaceOnUseOn=WaterSource-WaterBottleFull. §빈 물 용기와 같은 exact 물 저장/전환 사실을 재사용하며 음용 안전성·현재 내용물은 추정하지 않는다. | C038 | M041 |
| Base.WaterBottlePetrol | public / core | keep / description_ready | scripts/newitems.txt:4997; exact Petrol tag와 현재 연료 운반/급유 역할은 이미 구체적이다. 용기 종류를 물이나 소독제로 해석하지 않는다. | C014 | M152 |
| Base.WaterBowl | empty / no-core | revise / description_ready | scripts/items_food.txt:2527: CanStoreWater=TRUE, ReplaceOnUseOn=WaterSource-WaterBowl. §빈 물 용기와 같은 exact 물 저장/전환 사실을 재사용하며 음용 안전성·현재 내용물은 추정하지 않는다. | C038 | M041 |
| Base.WaterDish | public / core | review_hold / review_required | scripts/newitems.txt:806: Normal WaterDish 선언만으로 물 담기/섭취의 실제 CanStoreWater·전환 경로가 결속되지 않았다. 필요한 추가 근거는 이 exact item의 해당 행동/재료 입력 또는 효과를 명시하는 vanilla source 관계이며, current admission 부재를 해소할 승인만으로 대체하지 않음. | C002 | M194 |
| Base.WaterMug | public / no-core | revise / description_ready | scripts/items_food.txt:2550: CanStoreWater=TRUE, ReplaceOnUseOn=WaterSource-WaterMug. §빈 물 용기와 같은 exact 물 저장/전환 사실을 재사용하며 음용 안전성·현재 내용물은 추정하지 않는다. | C038 | M041 |
| Base.WaterMugRed | public / no-core | revise / description_ready | scripts/items_food.txt:2598: CanStoreWater=TRUE, ReplaceOnUseOn=WaterSource-WaterMugRed. §빈 물 용기와 같은 exact 물 저장/전환 사실을 재사용하며 음용 안전성·현재 내용물은 추정하지 않는다. | C038 | M041 |
| Base.WaterMugSpiffo | public / no-core | revise / description_ready | scripts/items_food.txt:2646: CanStoreWater=TRUE, ReplaceOnUseOn=WaterSource-WaterMugSpiffo. §빈 물 용기와 같은 exact 물 저장/전환 사실을 재사용하며 음용 안전성·현재 내용물은 추정하지 않는다. | C038 | M041 |
| Base.WaterMugWhite | public / no-core | revise / description_ready | scripts/items_food.txt:2622: CanStoreWater=TRUE, ReplaceOnUseOn=WaterSource-WaterMugWhite. §빈 물 용기와 같은 exact 물 저장/전환 사실을 재사용하며 음용 안전성·현재 내용물은 추정하지 않는다. | C038 | M041 |
| Base.WaterPaintbucket | empty / no-core | revise / description_ready | scripts/newitems.txt:4054: CanStoreWater=TRUE, ReplaceOnUseOn=WaterSource-WaterPaintbucket. §빈 물 용기와 같은 exact 물 저장/전환 사실을 재사용하며 음용 안전성·현재 내용물은 추정하지 않는다. | C038 | M041 |
| Base.WaterPopBottle | public / no-core | revise / description_ready | scripts/items_food.txt:2670: CanStoreWater=TRUE, ReplaceOnUseOn=WaterSource-WaterPopBottle. §빈 물 용기와 같은 exact 물 저장/전환 사실을 재사용하며 음용 안전성·현재 내용물은 추정하지 않는다. | C038 | M041 |
| Base.WaterPot | public / core | revise / description_ready | §조리 문구 32개: 이 exact item의 input/result/keep 역할과 원본 recipe를 분리 검토했다. | C026 | M027 |
| Base.WaterPotPasta | public / core | revise / description_ready | scripts/items_food.txt:2935; Food IsCookable=true 및 2/4 bowls exact 입력; Rice의 EvolvedRecipe &#124;Cooked는 재료 조건이며 DangerousUncooked 값 아님. | C166 | M195 |
| Base.WaterPotRice | public / core | revise / description_ready | scripts/items_food.txt:2904; Food IsCookable=true 및 2/4 bowls exact 입력; Rice의 EvolvedRecipe &#124;Cooked는 재료 조건이며 DangerousUncooked 값 아님. | C166 | M195 |
| Base.WaterSaucepan | public / core | revise / description_ready | §조리 문구 32개: 이 exact item의 input/result/keep 역할과 원본 recipe를 분리 검토했다. | C026 | M027 |
| Base.WaterSaucepanPasta | public / core | revise / description_ready | scripts/items_food.txt:3169; Food IsCookable=true 및 2/4 bowls exact 입력; Rice의 EvolvedRecipe &#124;Cooked는 재료 조건이며 DangerousUncooked 값 아님. | C166 | M195 |
| Base.WaterSaucepanRice | public / core | revise / description_ready | scripts/items_food.txt:3140; Food IsCookable=true 및 2/4 bowls exact 입력; Rice의 EvolvedRecipe &#124;Cooked는 재료 조건이며 DangerousUncooked 값 아님. | C166 | M195 |
| Base.WaterTeacup | public / no-core | revise / description_ready | scripts/items_food.txt:2574: CanStoreWater=TRUE, ReplaceOnUseOn=WaterSource-WaterTeacup. §빈 물 용기와 같은 exact 물 저장/전환 사실을 재사용하며 음용 안전성·현재 내용물은 추정하지 않는다. | C038 | M041 |
| Base.Watermelon | public / core | revise / description_ready | scripts/items_food.txt:1516; CantEat=TRUE; recipes.txt:304/317 slice/smash→WatermelonSliced/Smashed. 직접 섭취 문구 금지. | C167 | M064 |
| Base.WatermelonSliced | public / no-core | revise / description_ready | scripts/items_food.txt:1540의 exact H=-6, T=-20; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C020 | M004 |
| Base.WatermelonSmashed | public / no-core | revise / description_ready | scripts/items_food.txt:1563의 exact H=-12, T=-25; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C020 | M004 |
| Base.WeddingDress | public / core | keep / description_ready | scripts/clothing/clothing_suits.txt:347의 Clothing/BodyLocation=FullSuit와 현재 착용 목적 일치. 수치 추가나 감염/위장 효과를 강제하지 않는다. | C018 | M018 |
| Base.WeddingJacket | public / core | keep / description_ready | scripts/clothing/clothing_jacket.txt:3의 Clothing/BodyLocation=JacketSuit와 현재 착용 목적 일치. 수치 추가나 감염/위장 효과를 강제하지 않는다. | C018 | M018 |
| Base.WeddingRing_Man | public / no-core | review_hold / review_required | scripts/newitems.txt:1921: exact Type=Normal, OBSOLETE=TRUE. 정상 B41에서 이 exact item의 생성·사용 가능성/등록이 미확정이다. 작동하는 별도 FullType으로 대체하거나 기존 no-core 때문에 보류하는 것이 아님. | C076 | M221 |
| Base.WeddingRing_Woman | public / no-core | review_hold / review_required | scripts/newitems.txt:1932: exact Type=Normal, OBSOLETE=TRUE. 정상 B41에서 이 exact item의 생성·사용 가능성/등록이 미확정이다. 작동하는 별도 FullType으로 대체하거나 기존 no-core 때문에 보류하는 것이 아님. | C076 | M221 |
| Base.WeldingMask | empty / no-core | revise / description_ready | scripts/clothing/clothing_hats.txt:1058; exact WeldingMask tag 및 ISBlacksmithMenu.predicateWeldingMask. 해당 선택은 소지 요구와 실제 착용을 혼동하지 않는다. | C168 | M196 |
| Base.WeldingRods | public / no-core | revise / description_ready | scripts/newitems.txt:3992; ISBlacksmithMenu.lua:644 및 metal fence/crate/door use:Base.WeldingRods; disableFurnaceAnvil과 별도인 용접 경로. | C169 | M011 |
| Base.WestpointMap | public / no-core | keep / acquisition_only | scripts/newitems.txt:1225; Map=WestpointMap; ISMap.lua:321 + ISMapDefinitions.lua:257/267–451의 해당 Init. 지역 지도 확인 목적이 구체적이며 유지 가능. | C046 | M055 |
| Base.WhiskeyEmpty | public / core | keep / description_ready | 각 exact CanStoreWater 및 ReplaceOnUseOn=WaterSource 관계를 확인했다. 물의 안전성이나 소독 효과는 주장하지 않는다. | C003 | M040 |
| Base.WhiskeyFull | public / core | revise / description_ready | scripts/items_food.txt:3196; Alcoholic=TRUE, H/T 음수 Food 및 EvolvedRecipe; 기분 개선을 일괄 보장하는 기존 문구 축소. | C037 | M038 |
| Base.WhiskeyPetrol | public / core | keep / description_ready | scripts/newitems.txt:5012; exact Petrol tag와 현재 연료 운반/급유 역할은 이미 구체적이다. 용기 종류를 물이나 소독제로 해석하지 않는다. | C014 | M152 |
| Base.WhiskeyWaterFull | public / no-core | revise / description_ready | scripts/items_food.txt:2741: CanStoreWater=TRUE, ReplaceOnUseOn=WaterSource-WhiskeyWaterFull. §빈 물 용기와 같은 exact 물 저장/전환 사실을 재사용하며 음용 안전성·현재 내용물은 추정하지 않는다. | C038 | M041 |
| Base.WildEggs | public / core | revise / description_ready | scripts/items_food.txt:4212의 exact H=-7, T=미선언; EvolvedRecipe 재료 선언 확인; DangerousUncooked=TRUE. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C063 | M004 |
| Base.WildGarlic | public / core | review_hold / review_required | scripts/newitems.txt:2071: scripts/recipes.txt:1211 이후 Wild Garlic Poultice 선언은 obsolete 주석 경계다. 직접 소독/약효도 미결속이며 WildGarlic2를 복사하지 않는다. 필요한 추가 근거는 이 exact item의 해당 행동/재료 입력 또는 효과를 명시하는 vanilla source 관계이며, current admission 부재를 해소할 승인만으로 대체하지 않음. | C002 | M197 |
| Base.WildGarlic2 | public / core | revise / description_ready | scripts/items_food.txt:4034의 exact H=-1, T=미선언; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C004 | M004 |
| Base.WildGarlicCataplasm | public / no-core | revise / description_ready | scripts/newitems.txt:2082; ISHealthPanel.lua:1193–1273 exact poultice selector/부상/세 factor=0→각 timed action. perform에서 부상 부위 factor 설정·item 소비. 일반적인 처치 목적은 준비되며 개별 회복 효과·속도는 미확정으로 범위 밖에 둠. | C228 | M222 |
| Base.Windshield1 | public / core | keep / description_ready | scripts/vehicles/vehiclesitems.txt:890; exact VehicleType=1와 해당 door/window/windshield part 관계. 현재 패널/유리 탈착 목적은 이미 구체적이며 방탄·방호 효과를 추가하지 않는다. | C014 | M096 |
| Base.Windshield2 | public / core | keep / description_ready | scripts/vehicles/vehiclesitems.txt:946; exact VehicleType=2와 해당 door/window/windshield part 관계. 현재 패널/유리 탈착 목적은 이미 구체적이며 방탄·방호 효과를 추가하지 않는다. | C014 | M096 |
| Base.Windshield3 | public / core | keep / description_ready | scripts/vehicles/vehiclesitems.txt:1002; exact VehicleType=3와 해당 door/window/windshield part 관계. 현재 패널/유리 탈착 목적은 이미 구체적이며 방탄·방호 효과를 추가하지 않는다. | C014 | M096 |
| Base.Wine | public / core | revise / description_ready | scripts/items_food.txt:3581; Alcoholic=TRUE, H/T 음수 Food 및 EvolvedRecipe; 기분 개선을 일괄 보장하는 기존 문구 축소. | C037 | M038 |
| Base.Wine2 | public / core | revise / description_ready | scripts/items_food.txt:3631; Alcoholic=TRUE, H/T 음수 Food 및 EvolvedRecipe; 기분 개선을 일괄 보장하는 기존 문구 축소. | C037 | M038 |
| Base.WineEmpty | public / core | keep / description_ready | 각 exact CanStoreWater 및 ReplaceOnUseOn=WaterSource 관계를 확인했다. 물의 안전성이나 소독 효과는 주장하지 않는다. | C003 | M040 |
| Base.WineEmpty2 | public / core | keep / description_ready | 각 exact CanStoreWater 및 ReplaceOnUseOn=WaterSource 관계를 확인했다. 물의 안전성이나 소독 효과는 주장하지 않는다. | C003 | M040 |
| Base.WineInGlass | public / no-core | revise / description_ready | undefined; scripts/evolvedrecipes.txt:354 exact BaseItem→ResultItem 관계와 items_food Food/CustomContextMenu=Drink/ReplaceOnUse. inventory menu:124/414/2976 및 기존 소비 경로. 정적 H/T 부재는 동적 결과의 무효가 아니며 고정 효과량을 후보에 넣지 않음. | C241 | M218 |
| Base.WinePetrol | public / core | keep / description_ready | scripts/newitems.txt:5027; exact Petrol tag와 현재 연료 운반/급유 역할은 이미 구체적이다. 용기 종류를 물이나 소독제로 해석하지 않는다. | C014 | M152 |
| Base.WineWaterFull | public / no-core | revise / description_ready | scripts/items_food.txt:3609: CanStoreWater=TRUE, ReplaceOnUseOn=WaterSource-WineWaterFull. §빈 물 용기와 같은 exact 물 저장/전환 사실을 재사용하며 음용 안전성·현재 내용물은 추정하지 않는다. | C038 | M041 |
| Base.WinterBerry | public / core | revise / description_ready | scripts/items_food.txt:8743의 exact H=-10, T=-1; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C020 | M004 |
| Base.Wire | public / core | keep / description_ready | 각 exact input의 덫/어망 관계를 확인했다. Twine과 Wire의 서로 다른 recipe set을 하나로 합치지 않는다. | C003 | M189 |
| Base.WoodAxe | public / core | keep / description_ready | scripts/items_weapons.txt:2816; exact ChopTree tag, ISWorldObjectContextMenu:439/1297 및 ISChopTreeAction queue. 현재 벌목 역할이 구체적. | C014 | M020 |
| Base.WoodenLance | public / core | keep / description_ready | exact Weapon/Spear 선언이 찌르는 근접 무기라는 현재 목적과 일치한다. 실전 효율·거리 수치를 새로 주장하지 않는다. | C003 | M198 |
| Base.WoodenMallet | public / no-core | revise / description_ready | scripts/items_weapons.txt:1014; exact Weapon/damage=0.4–0.9. 구체 작업 source가 미결속인 부분을 일반 '작업'으로 확대하지 않는다. | C066 | M073 |
| Base.WoodenStick | public / core | revise / description_ready | scripts/newitems.txt:2379; exact input:Make Tent Kit; input:Make Tent Kit; input:Make Fishing Rod; input:Make Fishing Rod; input:Make Splint; input:Make Stick Trap에서 해당 Make Tent Kit input 확인. item 자체를 완성 텐트로 보지 않는다. | C156 | M176 |
| Base.Woodglue | public / no-core | revise / description_ready | scripts/newitems.txt:1550; scripts/fixing.txt:7 이후 exact Fixer Woodglue+skill/수리대상 계약. | C170 | M011 |
| Base.Worm | public / core | revise / description_ready | scripts/items_food.txt:4138의 exact H=-2, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C012 | M012 |
| Base.Wrench | public / no-core | revise / description_ready | scripts/items_weapons.txt:1060; exact Weapon/damage=0.5–1. 구체 작업 source가 미결속인 부분을 일반 '작업'으로 확대하지 않는다. | C066 | M073 |
| Base.WristWatch_Left_ClassicBlack | public / core | revise / description_ready | scripts/clothing/clothing_jewellery.txt:870; exact AlarmClockClothing/AlarmSound와 현재 시계 역할. Normal DigitalWatch나 Weapon AlarmClock에 전파하지 않는다. | C007 | M007 |
| Base.WristWatch_Left_ClassicBrown | public / core | revise / description_ready | scripts/clothing/clothing_jewellery.txt:906; exact AlarmClockClothing/AlarmSound와 현재 시계 역할. Normal DigitalWatch나 Weapon AlarmClock에 전파하지 않는다. | C007 | M007 |
| Base.WristWatch_Left_ClassicGold | public / core | revise / description_ready | scripts/clothing/clothing_jewellery.txt:978; exact AlarmClockClothing/AlarmSound와 현재 시계 역할. Normal DigitalWatch나 Weapon AlarmClock에 전파하지 않는다. | C007 | M007 |
| Base.WristWatch_Left_ClassicMilitary | public / core | revise / description_ready | scripts/clothing/clothing_jewellery.txt:942; exact AlarmClockClothing/AlarmSound와 현재 시계 역할. Normal DigitalWatch나 Weapon AlarmClock에 전파하지 않는다. | C007 | M007 |
| Base.WristWatch_Left_DigitalBlack | public / core | revise / description_ready | scripts/clothing/clothing_jewellery.txt:1015; exact AlarmClockClothing/AlarmSound와 현재 시계 역할. Normal DigitalWatch나 Weapon AlarmClock에 전파하지 않는다. | C007 | M007 |
| Base.WristWatch_Left_DigitalDress | public / core | revise / description_ready | scripts/clothing/clothing_jewellery.txt:1091; exact AlarmClockClothing/AlarmSound와 현재 시계 역할. Normal DigitalWatch나 Weapon AlarmClock에 전파하지 않는다. | C007 | M007 |
| Base.WristWatch_Left_DigitalRed | public / core | revise / description_ready | scripts/clothing/clothing_jewellery.txt:1053; exact AlarmClockClothing/AlarmSound와 현재 시계 역할. Normal DigitalWatch나 Weapon AlarmClock에 전파하지 않는다. | C007 | M007 |
| Base.WristWatch_Right_ClassicBlack | public / no-core | revise / description_ready | scripts/clothing/clothing_jewellery.txt:852; exact AlarmClockClothing/AlarmSound와 현재 시계 역할. Normal DigitalWatch나 Weapon AlarmClock에 전파하지 않는다. | C007 | M007 |
| Base.WristWatch_Right_ClassicBrown | public / no-core | revise / description_ready | scripts/clothing/clothing_jewellery.txt:888; exact AlarmClockClothing/AlarmSound와 현재 시계 역할. Normal DigitalWatch나 Weapon AlarmClock에 전파하지 않는다. | C007 | M007 |
| Base.WristWatch_Right_ClassicGold | public / no-core | revise / description_ready | scripts/clothing/clothing_jewellery.txt:960; exact AlarmClockClothing/AlarmSound와 현재 시계 역할. Normal DigitalWatch나 Weapon AlarmClock에 전파하지 않는다. | C007 | M007 |
| Base.WristWatch_Right_ClassicMilitary | public / core | revise / description_ready | scripts/clothing/clothing_jewellery.txt:924; exact AlarmClockClothing/AlarmSound와 현재 시계 역할. Normal DigitalWatch나 Weapon AlarmClock에 전파하지 않는다. | C007 | M007 |
| Base.WristWatch_Right_DigitalBlack | public / no-core | revise / description_ready | scripts/clothing/clothing_jewellery.txt:996; exact AlarmClockClothing/AlarmSound와 현재 시계 역할. Normal DigitalWatch나 Weapon AlarmClock에 전파하지 않는다. | C007 | M007 |
| Base.WristWatch_Right_DigitalDress | public / no-core | revise / description_ready | scripts/clothing/clothing_jewellery.txt:1072; exact AlarmClockClothing/AlarmSound와 현재 시계 역할. Normal DigitalWatch나 Weapon AlarmClock에 전파하지 않는다. | C007 | M007 |
| Base.WristWatch_Right_DigitalRed | public / no-core | revise / description_ready | scripts/clothing/clothing_jewellery.txt:1034; exact AlarmClockClothing/AlarmSound와 현재 시계 역할. Normal DigitalWatch나 Weapon AlarmClock에 전파하지 않는다. | C007 | M007 |
| Base.Yarn | public / core | review_hold / review_required | scripts/newitems.txt:817; Normal 선언만으로 현행 제작·수리 소비 경로 미확정; exact recipe/action 입력 관계 필요. 필요한 추가 근거는 이 exact item의 해당 행동/재료 입력 또는 효과를 명시하는 vanilla source 관계이며, current admission 부재를 해소할 승인만으로 대체하지 않음. | C049 | M081 |
| Base.Yeast | public / core | revise / description_ready | §조리 문구 32개: 이 exact item의 input/result/keep 역할과 원본 recipe를 분리 검토했다. | C026 | M027 |
| Base.Yoghurt | public / core | revise / description_ready | scripts/items_food.txt:5159의 exact H=-10, T=미선언; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C004 | M004 |
| Base.Yoyo | public / core | review_hold / review_required | scripts/newitems.txt:1943: §남은 혼합 역할: 현재 놀이 assertion을 실제 게임 플레이/지루함 감소에 결속하지 못했다. Normal 소품과 실제 놀이 기능을 구분한다. 필요한 추가 근거는 이 exact item의 해당 행동/재료 입력 또는 효과를 명시하는 vanilla source 관계이며, current admission 부재를 해소할 승인만으로 대체하지 않음. | C002 | M021 |
| Base.Zucchini | public / core | revise / description_ready | scripts/items_food.txt:1086의 exact H=-10, T=-10; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C020 | M004 |
| Base.brokenglass_1_0 | public / core | review_hold / review_required | scripts/newMoveables.txt:1203: Type=Moveable, WorldObjectSprite=brokenglass_1_0. InvContextMovable/ISMoveableCursor→ISMoveableSpriteProps.new는 getWorldSprite의 실제 IsMoveAble·MoveType·배치/도구 속성을 요구한다. 이 sprite의 B41 속성 입력이 미확정이라 기본 배치/설비 기능을 확정하지 못함; 기존 admission 유무 때문이 아님. 유리 위험·제거는 재고 item의 sprite와 실제 IsoBrokenGlass 객체 연결도 필요. | C049 | M227 |
| Base.brokenglass_1_1 | public / core | review_hold / review_required | scripts/newMoveables.txt:1214: Type=Moveable, WorldObjectSprite=brokenglass_1_1. InvContextMovable/ISMoveableCursor→ISMoveableSpriteProps.new는 getWorldSprite의 실제 IsMoveAble·MoveType·배치/도구 속성을 요구한다. 이 sprite의 B41 속성 입력이 미확정이라 기본 배치/설비 기능을 확정하지 못함; 기존 admission 유무 때문이 아님. 유리 위험·제거는 재고 item의 sprite와 실제 IsoBrokenGlass 객체 연결도 필요. | C049 | M227 |
| Base.brokenglass_1_2 | public / core | review_hold / review_required | scripts/newMoveables.txt:1225: Type=Moveable, WorldObjectSprite=brokenglass_1_2. InvContextMovable/ISMoveableCursor→ISMoveableSpriteProps.new는 getWorldSprite의 실제 IsMoveAble·MoveType·배치/도구 속성을 요구한다. 이 sprite의 B41 속성 입력이 미확정이라 기본 배치/설비 기능을 확정하지 못함; 기존 admission 유무 때문이 아님. 유리 위험·제거는 재고 item의 sprite와 실제 IsoBrokenGlass 객체 연결도 필요. | C049 | M227 |
| Base.brokenglass_1_3 | public / core | review_hold / review_required | scripts/newMoveables.txt:1236: Type=Moveable, WorldObjectSprite=brokenglass_1_3. InvContextMovable/ISMoveableCursor→ISMoveableSpriteProps.new는 getWorldSprite의 실제 IsMoveAble·MoveType·배치/도구 속성을 요구한다. 이 sprite의 B41 속성 입력이 미확정이라 기본 배치/설비 기능을 확정하지 못함; 기존 admission 유무 때문이 아님. 유리 위험·제거는 재고 item의 sprite와 실제 IsoBrokenGlass 객체 연결도 필요. | C049 | M227 |
| Base.x2Scope | public / core | keep / description_ready | scripts/newitems.txt:2462; exact WeaponPart/PartType=Scope/MountOn=HuntingRifle; VarmintRifle; AssaultRifle; AssaultRifle2. 총기 개조 부품이라는 current 목적은 구체적. 실제 성능·조명/총검 공격은 추가하지 않는다. | C014 | M014 |
| Base.x4Scope | public / core | keep / description_ready | scripts/newitems.txt:2479; exact WeaponPart/PartType=Scope/MountOn=HuntingRifle; VarmintRifle; AssaultRifle; AssaultRifle2. 총기 개조 부품이라는 current 목적은 구체적. 실제 성능·조명/총검 공격은 추가하지 않는다. | C014 | M014 |
| Base.x8Scope | public / core | keep / description_ready | scripts/newitems.txt:2496; exact WeaponPart/PartType=Scope/MountOn=HuntingRifle; VarmintRifle; AssaultRifle; AssaultRifle2. 총기 개조 부품이라는 current 목적은 구체적. 실제 성능·조명/총검 공격은 추가하지 않는다. | C014 | M014 |
| Radio.CDplayer | public / core | revise / description_ready | §남은 혼합 역할: 해당 exact 조명/무선·매체/운동 source 조건을 분리했다. | C026 | M114 |
| Radio.ElectricWire | public / core | revise / description_ready | scripts/items_radio.txt:446; input:Craft Makeshift Radio; input:Craft Makeshift HAM Radio; input:Craft Makeshift Walkie Talkie; recipes_radio.txt:72–125 exact 제작 입력. 독립 기기 기능 없음. | C011 | M011 |
| Radio.HamRadio1 | public / core | revise / description_ready | §남은 혼합 역할: 해당 exact 조명/무선·매체/운동 source 조건을 분리했다. | C026 | M114 |
| Radio.HamRadio2 | public / core | revise / description_ready | §남은 혼합 역할: 해당 exact 조명/무선·매체/운동 source 조건을 분리했다. | C026 | M114 |
| Radio.HamRadioMakeShift | public / no-core | revise / description_ready | scripts/items_radio.txt:226; items_radio exact TwoWay=true 및 transmit 범위, §무선기기의 RWMMicrophone 경로. | C171 | M200 |
| Radio.RadioBlack | public / core | revise / description_ready | §남은 혼합 역할: 해당 exact 조명/무선·매체/운동 source 조건을 분리했다. | C026 | M114 |
| Radio.RadioMag1 | public / no-core | revise / description_ready | scripts/items_radio.txt:494; items_radio의 exact TeachedRecipes=Craft Makeshift Radio, §학습의 ReadLiterature 경로. 실제 조립과 독서 습득을 구분. | C172 | M201 |
| Radio.RadioMag2 | public / no-core | revise / description_ready | scripts/items_radio.txt:507; items_radio의 exact TeachedRecipes=Craft Makeshift Walkie Talkie, §학습의 ReadLiterature 경로. 실제 조립과 독서 습득을 구분. | C172 | M202 |
| Radio.RadioMag3 | public / no-core | revise / description_ready | scripts/items_radio.txt:520; items_radio의 exact TeachedRecipes=Craft Makeshift HAM Radio, §학습의 ReadLiterature 경로. 실제 조립과 독서 습득을 구분. | C172 | M203 |
| Radio.RadioMakeShift | public / no-core | revise / description_ready | scripts/items_radio.txt:340; items_radio exact TwoWay=false/IsTelevision=false. 송신/CD/VHS 기능을 다른 기기에서 복사하지 않는다. | C173 | M204 |
| Radio.RadioReceiver | public / core | revise / description_ready | scripts/items_radio.txt:459; input:Make Remote Trigger; input:Craft Makeshift Radio; input:Craft Makeshift HAM Radio; input:Craft Makeshift Walkie Talkie; recipes_radio.txt:72–125 exact 제작 입력. 독립 기기 기능 없음. | C011 | M011 |
| Radio.RadioRed | public / core | revise / description_ready | §남은 혼합 역할: 해당 exact 조명/무선·매체/운동 source 조건을 분리했다. | C026 | M114 |
| Radio.RadioTransmitter | public / core | revise / description_ready | scripts/items_radio.txt:472; input:Craft Makeshift HAM Radio; input:Craft Makeshift Walkie Talkie; recipes_radio.txt:72–125 exact 제작 입력. 독립 기기 기능 없음. | C011 | M011 |
| Radio.ScannerModule | public / no-core | review_hold / review_required | scripts/items_radio.txt:485; Normal 선언은 확인되나 actual scan/assembly input 연결 미확인; 이름을 근거로 신호 확인 기능 주장 금지. 필요한 추가 근거는 이 exact item의 해당 행동/재료 입력 또는 효과를 명시하는 vanilla source 관계이며, current admission 부재를 해소할 승인만으로 대체하지 않음. | C015 | M205 |
| Radio.TvAntique | public / core | revise / description_ready | §남은 혼합 역할: 해당 exact 조명/무선·매체/운동 source 조건을 분리했다. | C026 | M114 |
| Radio.TvBlack | public / core | revise / description_ready | §남은 혼합 역할: 해당 exact 조명/무선·매체/운동 source 조건을 분리했다. | C026 | M114 |
| Radio.TvWideScreen | public / core | revise / description_ready | §남은 혼합 역할: 해당 exact 조명/무선·매체/운동 source 조건을 분리했다. | C026 | M114 |
| Radio.WalkieTalkie1 | public / core | revise / description_ready | §남은 혼합 역할: 해당 exact 조명/무선·매체/운동 source 조건을 분리했다. | C026 | M114 |
| Radio.WalkieTalkie2 | public / core | revise / description_ready | §남은 혼합 역할: 해당 exact 조명/무선·매체/운동 source 조건을 분리했다. | C026 | M114 |
| Radio.WalkieTalkie3 | public / core | revise / description_ready | §남은 혼합 역할: 해당 exact 조명/무선·매체/운동 source 조건을 분리했다. | C026 | M114 |
| Radio.WalkieTalkie4 | public / core | revise / description_ready | §남은 혼합 역할: 해당 exact 조명/무선·매체/운동 source 조건을 분리했다. | C026 | M114 |
| Radio.WalkieTalkie5 | public / core | revise / description_ready | §남은 혼합 역할: 해당 exact 조명/무선·매체/운동 source 조건을 분리했다. | C026 | M114 |
| Radio.WalkieTalkieMakeShift | public / no-core | revise / description_ready | scripts/items_radio.txt:145; items_radio exact TwoWay=true 및 transmit 범위, §무선기기의 RWMMicrophone 경로. | C171 | M200 |
| camping.CampfireKit | public / no-core | revise / description_ready | scripts/camping.txt:12: ISCampingMenu:142 및 onPlaceCampfire 경로. 점화/연료와 설치를 구분한다. | C174 | M206 |
| camping.CampingTent | public / no-core | review_hold / review_required | scripts/camping.txt:52 Type=Normal; Kit과 다른 item의 설치/수면 관계 경로가 미결속이다. 같은 이름의 다른 item/현실 용도를 복사하지 않는다. ISCampingMenu:144는 CampingTentKit를 선택하므로 CampingTent 자체의 설치 경로가 별도로 필요. | C052 | M207 |
| camping.CampingTentKit | public / no-core | revise / description_ready | scripts/camping.txt:61: ISCampingMenu:144 및 onAddTent 경로. camping.CampingTent라는 별도 item으로 전파하지 않는다. | C175 | M208 |
| camping.Flint | public / core | review_hold / review_required | scripts/camping.txt:22: Flint의 exact 점화 선택/소모 경로가 미결속이다. SteelAndFlint나 다른 점화재로 추론하지 않는다. 필요한 추가 근거는 이 exact item의 해당 행동/재료 입력 또는 효과를 명시하는 vanilla source 관계이며, current admission 부재를 해소할 승인만으로 대체하지 않음. | C002 | M209 |
| camping.SteelAndFlint | public / core | review_hold / review_required | scripts/camping.txt:42: SteelAndFlint의 exact 점화 선택/소모 경로를 결속하지 못했다. Lighter/Matches나 이름이 다른 Flint와 합치지 않는다. 필요한 추가 근거는 이 exact item의 해당 행동/재료 입력 또는 효과를 명시하는 vanilla source 관계이며, current admission 부재를 해소할 승인만으로 대체하지 않음. | C002 | M210 |
| camping.TentPeg | public / core | revise / description_ready | scripts/camping.txt:71; exact input:Make Tent Kit에서 해당 Make Tent Kit input 확인. item 자체를 완성 텐트로 보지 않는다. | C156 | M176 |
| farming.Bacon | public / core | revise / description_ready | scripts/farming.txt:143의 exact H=-12, T=미선언; EvolvedRecipe 재료 선언 확인; DangerousUncooked=true. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C063 | M004 |
| farming.BaconBits | public / no-core | revise / description_ready | scripts/farming.txt:196의 exact H=-1, T=미선언; EvolvedRecipe 재료 선언 확인; DangerousUncooked=true. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C063 | M004 |
| farming.BaconRashers | public / no-core | revise / description_ready | scripts/farming.txt:170의 exact H=-4, T=미선언; EvolvedRecipe 재료 선언 확인; DangerousUncooked=true. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C063 | M004 |
| farming.BloomingBroccoli | public / core | revise / description_ready | scripts/farming.txt:12의 exact H=-10, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C012 | M012 |
| farming.BroccoliBagSeed | public / core | revise / description_ready | scripts/farming.txt:492; scripts/farming.txt:740–809의 해당 exact seed packet input/result. 현재 'input:Open Packet of Broccoli Seeds' 관계. | C176 | M211 |
| farming.BroccoliSeed | public / core | keep / description_ready | scripts/farming.txt:411; 현재 재배용 씨앗이라는 기본 목적과 exact seed identity를 유지한다. 봉지 개봉과 파종하는 낱알 역할을 구분한다. | C014 | M212 |
| farming.Cabbage | public / core | revise / description_ready | scripts/farming.txt:117의 exact H=-24, T=-10; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C020 | M004 |
| farming.CabbageBagSeed | public / core | revise / description_ready | scripts/farming.txt:547; scripts/farming.txt:740–809의 해당 exact seed packet input/result. 현재 'input:Open Packet of Cabbage Seeds' 관계. | C176 | M211 |
| farming.CabbageSeed | public / core | keep / description_ready | scripts/farming.txt:466; 현재 재배용 씨앗이라는 기본 목적과 exact seed identity를 유지한다. 봉지 개봉과 파종하는 낱알 역할을 구분한다. | C014 | M212 |
| farming.CarrotBagSeed | public / core | revise / description_ready | scripts/farming.txt:481; scripts/farming.txt:740–809의 해당 exact seed packet input/result. 현재 'input:Open Packet of Carrot Seeds' 관계. | C176 | M211 |
| farming.CarrotSeed | public / core | keep / description_ready | scripts/farming.txt:400; 현재 재배용 씨앗이라는 기본 목적과 exact seed identity를 유지한다. 봉지 개봉과 파종하는 낱알 역할을 구분한다. | C014 | M212 |
| farming.GardeningSprayCigarettes | public / no-core | revise / description_ready | §농사·낚시·덫: 해당 exact source 선택·조건 및 실제 결과 변화 연결 | C026 | M025 |
| farming.GardeningSprayEmpty | public / core | revise / description_ready | scripts/farming.txt:661; scripts/farming.txt:661 CanStoreWater/WaterSource 전환, :717/:730 Make Mildew Cure/Flies Cure exact 입력. 빈 용기의 기본 목적 근거 준비. | C242 | M231 |
| farming.GardeningSprayFull | public / no-core | revise / description_ready | scripts/farming.txt:675; scripts/farming.txt:675 IsWaterSource/CanStoreWater/ReplaceOnDeplete, 기존 물 운반 source 적용. generic 물과 치료액 variant는 구분. | C243 | M232 |
| farming.GardeningSprayMilk | public / no-core | revise / description_ready | §농사·낚시·덫: 해당 exact source 선택·조건 및 실제 결과 변화 연결 | C026 | M025 |
| farming.HandShovel | public / no-core | revise / description_ready | scripts/farming.txt:562; exact DigPlow tag → ISFarmingMenu:20의 not-broken 도구 선택. 다른 작업의 가능/불가능을 추정하지 않는다. | C091 | M104 |
| farming.MayonnaiseEmpty | public / core | keep / description_ready | 각 exact CanStoreWater 및 ReplaceOnUseOn=WaterSource 관계를 확인했다. 물의 안전성이나 소독 효과는 주장하지 않는다. | C003 | M040 |
| farming.MayonnaiseFull | public / core | revise / description_ready | scripts/farming.txt:224의 exact H=-30, T=미선언; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C004 | M004 |
| farming.MayonnaiseHalf | public / core | revise / description_ready | scripts/farming.txt:250의 exact H=-10, T=미선언; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C004 | M004 |
| farming.MayonnaiseWaterFull | public / no-core | revise / description_ready | scripts/farming.txt:285: CanStoreWater=true, ReplaceOnUseOn=WaterSource-MayonnaiseWaterFull. §빈 물 용기와 같은 exact 물 저장/전환 사실을 재사용하며 음용 안전성·현재 내용물은 추정하지 않는다. | C038 | M041 |
| farming.Potato | public / core | revise / description_ready | scripts/farming.txt:97의 exact H=-18, T=-7; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C020 | M004 |
| farming.PotatoBagSeed | public / core | revise / description_ready | scripts/farming.txt:536; scripts/farming.txt:740–809의 해당 exact seed packet input/result. 현재 'input:Open Packet of Potato Seeds' 관계. | C176 | M211 |
| farming.PotatoSeed | public / core | keep / description_ready | scripts/farming.txt:455; 현재 재배용 씨앗이라는 기본 목적과 exact seed identity를 유지한다. 봉지 개봉과 파종하는 낱알 역할을 구분한다. | C014 | M212 |
| farming.RedRadish | public / core | revise / description_ready | scripts/farming.txt:30의 exact H=-3, T=-1; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C020 | M004 |
| farming.RedRadishBagSeed | public / core | revise / description_ready | scripts/farming.txt:503; scripts/farming.txt:740–809의 해당 exact seed packet input/result. 현재 'input:Open Packet of Radish Seeds' 관계. | C176 | M211 |
| farming.RedRadishSeed | public / core | keep / description_ready | scripts/farming.txt:422; 현재 재배용 씨앗이라는 기본 목적과 exact seed identity를 유지한다. 봉지 개봉과 파종하는 낱알 역할을 구분한다. | C014 | M212 |
| farming.RemouladeEmpty | public / core | keep / description_ready | 각 exact CanStoreWater 및 ReplaceOnUseOn=WaterSource 관계를 확인했다. 물의 안전성이나 소독 효과는 주장하지 않는다. | C003 | M040 |
| farming.RemouladeFull | public / core | revise / description_ready | scripts/farming.txt:305의 exact H=-10, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C012 | M012 |
| farming.RemouladeHalf | public / core | revise / description_ready | scripts/farming.txt:329의 exact H=-10, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C012 | M012 |
| farming.RemouladeWaterFull | public / no-core | revise / description_ready | scripts/farming.txt:360: CanStoreWater=true, ReplaceOnUseOn=WaterSource-RemouladeWaterFull. §빈 물 용기와 같은 exact 물 저장/전환 사실을 재사용하며 음용 안전성·현재 내용물은 추정하지 않는다. | C038 | M041 |
| farming.Salad | public / no-core | revise / description_ready | scripts/farming.txt:379의 exact H=-60, T=미선언; EvolvedRecipe 재료 역할은 이 후보에 추가하지 않음. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C012 | M012 |
| farming.Strewberrie | public / core | revise / description_ready | scripts/farming.txt:51의 exact H=-5, T=-1; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C020 | M004 |
| farming.StrewberrieBagSeed | public / core | revise / description_ready | scripts/farming.txt:514; scripts/farming.txt:740–809의 해당 exact seed packet input/result. 현재 'input:Open Packet of Strawberries Seeds' 관계. | C176 | M211 |
| farming.StrewberrieSeed | public / core | keep / description_ready | scripts/farming.txt:433; 현재 재배용 씨앗이라는 기본 목적과 exact seed identity를 유지한다. 봉지 개봉과 파종하는 낱알 역할을 구분한다. | C014 | M212 |
| farming.Tomato | public / core | revise / description_ready | scripts/farming.txt:75의 exact H=-12, T=-8; EvolvedRecipe 재료 선언 확인. §식재료 사과의 기존 소비 경로/값 의미를 재사용하며 안전성·효과량을 보장하지 않는다. | C020 | M004 |
| farming.TomatoBagSeed | public / core | revise / description_ready | scripts/farming.txt:525; scripts/farming.txt:740–809의 해당 exact seed packet input/result. 현재 'input:Open Packet of Tomato Seeds' 관계. | C176 | M211 |
| farming.TomatoSeed | public / core | keep / description_ready | scripts/farming.txt:444; 현재 재배용 씨앗이라는 기본 목적과 exact seed identity를 유지한다. 봉지 개봉과 파종하는 낱알 역할을 구분한다. | C014 | M212 |
| farming.WateredCan | public / no-core | revise / description_ready | scripts/farming.txt:631: CanStoreWater=true, ReplaceOnUseOn=WaterSource-WateredCanFull. §빈 물 용기와 같은 exact 물 저장/전환 사실을 재사용하며 음용 안전성·현재 내용물은 추정하지 않는다. | C038 | M041 |
| farming.WateredCanFull | empty / no-core | revise / description_ready | scripts/farming.txt:607: CanStoreWater=true, ReplaceOnUseOn=WaterSource-WateredCanFull. §빈 물 용기와 같은 exact 물 저장/전환 사실을 재사용하며 음용 안전성·현재 내용물은 추정하지 않는다. | C038 | M041 |

### 반복 후보 참조

| 참조 | KO/EN 후보 또는 유지·보류 처리 |
|---|---|
| C001 | 같은 절의 탄약 exact KO/EN 후보 |
| C002 | 현행 기능 문구의 확대/재발행 보류; KO/EN successor 미확정 |
| C003 | 현행 primary 유지; S2 presence는 현행 eligibility 보존 |
| C004 | KO: 섭취하면 허기를 줄일 수 있다. 요리 재료로도 쓰인다. / EN: Consuming it can reduce hunger. It is also used as a cooking ingredient. |
| C005 | KO: 기폭해 폭발을 일으키는 무기다 / EN: A weapon that produces an explosion when triggered. |
| C006 | 현행 지연 소리 장치 KO/EN 유지 |
| C007 | KO: 시간을 확인하거나 알람을 설정하는 데 쓰는 시계다 / EN: A clock used to check the time or set an alarm. |
| C008 | KO: 상처에 감거나 붙이는 데 쓰는 붕대 재료다 / EN: Bandaging material used to cover wounds. |
| C009 | §의료 exact KO/EN 후보 |
| C010 | KO: 상처를 소독하는 데 쓰는 소모품이다 / EN: A consumable used to disinfect wounds. |
| C011 | KO: 라디오나 무전기를 만드는 데 쓰는 재료·부품이다. / EN: A material or component used to craft radios or two-way radios. |
| C012 | KO: 섭취하면 허기를 줄일 수 있다. / EN: Consuming it can reduce hunger. |
| C013 | 같은 절의 탄약띠 exact KO/EN 후보 |
| C014 | 현행 KO/EN 유지 |
| C015 | 교정 문구 보류 — 현행 유지 승인/기능 부재 판정이 아님 |
| C016 | §식재료 사과 KO/EN 후보 |
| C018 | 현행 KO/EN 기본 착용 목적 유지 |
| C019 | KO: 사격에 쓰는 소총이다 / EN: A rifle used for shooting. |
| C020 | KO: 섭취하면 허기와 갈증을 줄일 수 있다. 요리 재료로도 쓰인다. / EN: Consuming it can reduce hunger and thirst. It is also used as a cooking ingredient. |
| C021 | KO: 근접 공격에 사용할 수 있는 물건이다 / EN: An item that can be used for melee attacks. |
| C022 | KO: 물건을 담아 운반하는 휴대용 보관함이다 / EN: A portable container used to carry items. |
| C023 | 현행 기본 보관/운반 KO·EN 유지 |
| C024 | 기능 문구 확대 보류; exact source 필요 |
| C025 | KO: 섭취하면 허기를 줄일 수 있지만 갈증은 높인다. / EN: Consuming it can reduce hunger but increases thirst. |
| C026 | 같은 절의 exact KO/EN 후보 |
| C027 | KO: 케이크나 파이 반죽을 담아 굽기 준비를 하는 틀이다. / EN: A pan used to prepare cake or pie dough for baking. |
| C028 | KO: 쿠키 반죽을 준비할 때 쓰는 베이킹 트레이다. / EN: A baking tray used to prepare cookie dough. |
| C029 | KO: 머핀을 구운 뒤 나누어 꺼내는 데 쓰는 반죽이 든 틀이다. / EN: A tray of batter used to bake muffins and remove them as portions. |
| C030 | KO: 못을 사용하는 목공 구조물을 만드는 데 쓸 수 있는 망치다 / EN: A hammer usable for building wooden structures with nails. |
| C031 | KO: 상처에 감을 수 있는 오염된 붕대 재료다 / EN: Dirty bandaging material that can be applied to wounds. |
| C032 | KO: 섭취하면 허기를 줄일 수 있다. 날것으로 먹으면 위험할 수 있다. / EN: Consuming it can reduce hunger. Eating it raw can be dangerous. |
| C033 | 같은 절의 몸 건조/혈흔 제거 KO/EN 후보 |
| C034 | KO: 말린 뒤 몸의 물기를 닦는 데 다시 쓸 수 있는 젖은 수건이다. / EN: A wet towel that can be used to dry the body again once it has dried. |
| C035 | §건전지 KO/EN 후보 |
| C037 | KO: 마시거나 요리 재료로 쓰는 알코올 음료다. / EN: An alcoholic drink that can be consumed or used as a cooking ingredient. |
| C038 | KO: 물을 담아 운반하는 데 쓰는 용기다 / EN: A container used to carry water. |
| C039 | KO: 섭취하면 허기와 갈증을 줄일 수 있다. 요리 재료로도 쓰인다. 독성이 있으면 식중독 수치가 오른다. / EN: Consuming it can reduce hunger and thirst. It is also used as a cooking ingredient. If poisonous, it increases food sickness. |
| C040 | KO: 차량에 장착해 연료를 저장하는 탱크다 / EN: A tank fitted to a vehicle to store fuel. |
| C041 | KO: 차량에서 물건을 보관하는 수납 부품이다 / EN: A vehicle storage component used to hold items. |
| C042 | 같은 절의 유독성 표백제 KO/EN 후보 |
| C043 | KO: 기록물에 글을 쓰거나 지도에 주석을 남기는 필기구다 / EN: A writing tool used for documents or map annotations. |
| C044 | 같은 절의 읽기/기록물 exact KO/EN 후보 |
| C045 | 교정 유보; KO/EN 효과 tuple 미확정 |
| C046 | 현행 KO/EN 유지 제안 |
| C047 | KO: 근접 공격이나 창 끝에 붙이는 용도로 쓸 수 있다 / EN: Usable for melee attacks or as a spear attachment. |
| C048 | 같은 절의 재/혈흔 제거 KO/EN 후보(초기 재-only 초안을 대체) |
| C049 | 교정 문구 보류 — 현행 유지 승인이 아니며 기능 부재 판정이 아님 |
| C050 | KO: 석고 마감이 가능한 구조물에 바르는 반죽이다. / EN: Plaster used to finish structures that support plastering. |
| C051 | KO: 틀에 담아 케이크를 준비하는 반죽이다. / EN: Batter placed in a baking pan to prepare a cake. |
| C052 | 신규 기능 KO/EN 보류; 현재 부재를 기능 없음으로 해석하지 않음 |
| C053 | KO: 불을 붙여 빛을 내는 양초다. / EN: A candle that provides light when lit. |
| C054 | KO: 점화 재료와 함께 모닥불에 불을 붙이는 데 쓴다 / EN: Used with tinder or fuel to light a campfire. |
| C055 | KO: 포장을 열어 사탕을 꺼내는 식품이다. / EN: A package opened to obtain candy. |
| C056 | KO: 병을 열어 담긴 채소를 꺼낼 수 있다 / EN: Open the jar to take out its vegetables. |
| C057 | KO: 병을 열어 양배추를 꺼내는 식품이다. / EN: A jar opened to obtain cabbage. |
| C058 | KO: 섭취하면 허기와 갈증을 줄일 수 있으며, 요리 재료로도 쓰인다. / EN: Consuming it can reduce hunger and thirst. It is also used as a cooking ingredient. |
| C059 | KO: 차량의 시동과 전기 장치에 전원을 공급하는 배터리다 / EN: A battery that supplies power for starting a vehicle and operating its electrical devices. |
| C060 | KO: 열쇠가 맞는 차량을 사용하는 데 쓴다. / EN: Used to operate the matching vehicle. |
| C061 | KO: 섭취하면 허기와 갈증을 줄일 수 있다. / EN: Consuming it can reduce hunger and thirst. |
| C062 | KO: 모닥불이나 숯불 바비큐에 보충하는 연료다. / EN: Fuel added to campfires or charcoal barbecues. |
| C063 | KO: 섭취하면 허기를 줄일 수 있다. 요리 재료로도 쓰인다. 날것으로 먹으면 위험할 수 있다. / EN: Consuming it can reduce hunger. It is also used as a cooking ingredient. Eating it raw can be dangerous. |
| C064 | KO: 몸이나 옷의 피와 때를 씻는 데 쓰는 세정제다. / EN: A cleanser used when washing blood and dirt from the body or clothing. |
| C065 | KO: 펼쳐 손에 들면 비를 막는 우산으로 쓸 수 있다. / EN: Can be opened and held to provide protection from rain. |
| C066 | KO: 근접 공격에 사용할 수 있는 도구다 / EN: A tool that can be used for melee attacks. |
| C067 | KO: 섭취하면 허기를 줄일 수 있지만 갈증은 높인다. 요리 재료로도 쓰인다. / EN: Consuming it can reduce hunger but increases thirst. It is also used as a cooking ingredient. |
| C068 | 같은 절의 커피 재료 KO/EN 후보 |
| C069 | KO: 번호 자물쇠를 달 수 있는 구조물을 잠그는 데 쓴다. / EN: Used to secure structures that support combination padlocks. |
| C070 | KO: 컴프리 습포를 만드는 데 쓰는 재료다 / EN: An ingredient used to make a comfrey poultice. |
| C071 | KO: 분해해 전자 부품을 얻을 수 있다. / EN: Can be dismantled to recover electronic scrap. |
| C072 | KO: 케이크나 파이 등의 반죽을 만드는 데 쓰는 가루 재료다. / EN: A flour ingredient used to make dough or batter for foods such as cakes and pies. |
| C073 | KO: 소독용 솜을 만드는 데 쓰는 재료다. / EN: A material used to make alcohol-soaked cotton balls. |
| C074 | KO: 바리케이드를 제거하는 데 쓸 수 있는 도구다 / EN: A tool usable for removing barricades. |
| C075 | KO: 상처에 감거나 일부 도구와 부목을 만드는 데 쓰는 천 재료다 / EN: Cloth material used to bandage wounds or make some tools and splints. |
| C076 | 기능 문구 확대 보류; 착용/시계 KO·EN 미확정 |
| C077 | KO: 불을 끄는 데 사용할 수 있는 흙 포대다 / EN: A bag of dirt that can be used to put out fires. |
| C078 | KO: 호환되는 재생 장치에서 기록된 내용을 재생하는 매체다. / EN: Recorded media that can be played on a compatible device. |
| C079 | KO: 개봉해 내용물을 꺼낼 수 있는 사료 통조림이다 / EN: Canned pet food that can be opened to obtain its contents. |
| C080 | KO: 문이나 서랍을 만드는 데 쓰는 손잡이 부품이다. / EN: A handle component used to build doors or drawers. |
| C081 | KO: 섭취하면 허기를 줄일 수 있지만 갈증은 높인다. 날것으로 먹으면 위험할 수 있다. / EN: Consuming it can reduce hunger but increases thirst. Eating it raw can be dangerous. |
| C082 | KO: 서랍 달린 작은 탁자를 만드는 데 쓰는 부품이다. / EN: A component used to build a small table with a drawer. |
| C083 | KO: 장치를 조립하거나 도구를 창에 붙일 때 쓰는 접착 재료다. / EN: An adhesive material used to assemble devices or attach tools to spears. |
| C084 | KO: 호환되는 라디오 장치에 연결해 소리를 듣는 데 쓴다. / EN: Used with compatible radio devices to listen through headphones. |
| C085 | KO: 연료를 담아 운반하는 데 쓰는 빈 용기다 / EN: An empty container used to carry fuel. |
| C086 | KO: 차량 엔진의 상태를 수리하는 데 쓰는 부품이다 / EN: Parts used to repair the condition of a vehicle engine. |
| C087 | KO: 지도에 남긴 주석을 지우는 데 쓰는 도구다 / EN: A tool used to erase map annotations. |
| C088 | KO: 불이 붙은 곳이나 캐릭터의 불을 끄는 데 쓰는 소화기다 / EN: An extinguisher used to put out fires on squares or characters. |
| C089 | KO: 낚싯줄을 연결해 낚싯대로 수리할 수 있다 / EN: It can be repaired into a fishing rod by attaching line. |
| C090 | KO: 불을 일으키는 데 쓰는 화염 무기다 / EN: An incendiary weapon used to start fires. |
| C091 | KO: 땅을 파서 경작할 자리를 만드는 데 쓰는 도구다 / EN: A tool used to dig soil for cultivation. |
| C092 | KO: 통나무를 판자로 켜는 데 쓰는 톱이다 / EN: A saw used to cut logs into planks. |
| C094 | KO: 원격 조종기나 타이머 같은 장치를 조립할 때 쓰는 접착제다. / EN: An adhesive used to assemble devices such as remote controllers and timers. |
| C095 | KO: 포대 장벽을 만들거나 불을 끄는 데 쓰는 재료다 / EN: A material used to build bag barriers or put out fires. |
| C096 | KO: 재료를 넣어 볶음 요리를 준비하는 팬이다. / EN: A pan used to prepare stir-fries by adding ingredients. |
| C097 | KO: 파이프 폭탄을 만드는 데 쓰는 재료다. / EN: A material used to make pipe bombs. |
| C098 | KO: 에어로졸 폭탄을 만드는 데 쓰는 재료다 / EN: A material used to make an aerosol bomb. |
| C099 | §목공 도구 KO/EN 후보 |
| C100 | KO: 못을 사용하는 목공 구조물을 만드는 데 쓰는 도구다 / EN: A tool used to build wooden structures with nails. |
| C101 | KO: 머리나 얼굴에 착용하는 의류다 / EN: Clothing worn on the head or face. |
| C102 | KO: 분해해 동작 감지 부품을 회수하는 데 쓸 수 있다. / EN: Can be dismantled to recover a motion sensor. |
| C103 | KO: 마시면 갈증을 줄일 수 있다. / EN: Drinking it can reduce thirst. |
| C104 | KO: 열쇠가 맞는 문의 잠금을 조작하는 데 쓴다. / EN: Used to operate the lock of a matching door. |
| C105 | KO: 열쇠가 맞는 자물쇠를 푸는 데 쓴다. / EN: Used to unlock a matching padlock. |
| C108 | 현행 기능 assertion 보류; 신규 KO/EN 미확정 |
| C109 | 현행 얼굴/눈/입술 색·무늬 목적 유지 |
| C110 | KO: 톱으로 판자를 만들거나 모닥불 키트를 만드는 데 쓰는 통나무다 / EN: A log used to make planks with a saw or to craft a campfire kit. |
| C111 | KO: 묶음을 풀어 통나무를 꺼낼 수 있다 / EN: Untie the bundle to take out logs. |
| C112 | KO: 섭취하면 허기를 줄일 수 있다. 독성이 있다. / EN: Consuming it can reduce hunger. It is poisonous. |
| C113 | 현재 배치 문구의 표현만 바꾸어 해결 처리하지 않음; 기본 기능/조건의 KO·EN 미확정 |
| C114 | KO: 식재료를 자르거나 작은 동물을 손질하며, 근접 무기로도 쓸 수 있다. / EN: Used to cut ingredients or butcher small animals, and can also serve as a melee weapon. |
| C115 | KO: 금속 바리케이드를 만드는 데 쓰는 금속봉이다 / EN: A metal bar used to make metal barricades. |
| C116 | 채택/교정 보류; 실제 드럼통의 기능을 재고 item에 바로 전이하지 않음 |
| C117 | KO: 화장을 적용할 때 쓸 수 있는 거울이다 / EN: A mirror used when applying makeup. |
| C118 | KO: 차량 제동에 쓰는 브레이크 부품이다 / EN: A brake component used for vehicle braking. |
| C119 | KO: 차량의 엔진 소음에 영향을 주는 소음기 부품이다 / EN: A muffler component that affects vehicle engine noise. |
| C120 | KO: 차량 서스펜션을 교체하는 데 쓰는 부품이다 / EN: A replacement component for a vehicle's suspension. |
| C121 | KO: 차량 바퀴에 장착하며 접지력에 영향을 주는 타이어다 / EN: A tire fitted to a vehicle wheel that affects traction. |
| C122 | 같은 절의 표백제와 혈흔 제거 KO/EN 후보 |
| C123 | KO: 약초를 찧어 찜질제를 만드는 데 쓰는 도구다. / EN: A tool used to grind herbs into poultices. |
| C124 | KO: 호환되는 장치에 동작 감지 기능을 붙이는 부품이다. / EN: A component used to add motion sensing to compatible devices. |
| C125 | KO: 머핀 반죽을 준비하는 데 쓰는 틀이다. / EN: A tray used to prepare muffin batter. |
| C126 | KO: 작동하면 소리를 내는 장치다 / EN: A device that produces noise when triggered. |
| C127 | KO: 차량에 설치해 앉거나 물건을 놓는 좌석이다 / EN: A vehicle seat used for sitting or holding items. |
| C128 | KO: 필기구가 있으면 내용을 적어 보관할 수 있는 기록물이다 / EN: A document in which notes can be written and kept using a writing tool. |
| C129 | KO: 자물쇠를 달 수 있는 구조물을 잠그는 데 쓴다. / EN: Used to lock structures that support padlocks. |
| C130 | KO: 낚싯대 제작과 수리에 쓰는 재료다 / EN: A material used to make and repair fishing rods. |
| C131 | KO: 상자를 열어 종이 클립을 꺼낼 수 있다 / EN: Open the box to take out paperclips. |
| C132 | KO: 그릇에 나누어 담아 먹을 수 있는 조리 음식이다. / EN: Prepared food that can be divided into bowls for eating. |
| C133 | KO: 나뭇가지나 막대와 함께 모닥불에 불을 붙이는 데 쓴다 / EN: Used with a branch or stick to kindle a campfire. |
| C134 | KO: 틀에 담아 파이를 준비하는 반죽이다. / EN: Dough placed in a baking pan to prepare a pie. |
| C135 | KO: 매트리스를 만드는 데 쓰는 재료다. / EN: A material used to make a mattress. |
| C136 | KO: 질경이 습포를 만드는 데 쓰는 재료다 / EN: An ingredient used to make a plantain poultice. |
| C137 | KO: 물과 섞어 석고 반죽이 든 양동이를 만드는 재료다. / EN: A material mixed with water to make a bucket of plaster. |
| C138 | KO: 허기를 줄일 수 있지만 갈증을 늘릴 수 있는 식품이다. / EN: A food that can reduce hunger but may increase thirst. |
| C139 | KO: 먹거나 그릇에 나누어 담을 수 있는 국물 요리다. / EN: A soup or stew that can be eaten or divided into bowls. |
| C140 | KO: 원격 방아쇠 장치를 만드는 전자 부품이다. / EN: An electronic component used to make a remote trigger. |
| C141 | KO: 원격 조종기를 만드는 데 쓰는 전자 부품이다. / EN: An electronic component used to make a remote controller. |
| C142 | KO: 호환되는 장치와 연결해 원격으로 작동시키는 조종기다. / EN: A controller used to remotely trigger compatible linked devices. |
| C143 | KO: 재료를 넣어 구울 요리를 준비하는 팬이다. / EN: A pan used to prepare ingredients for roasting. |
| C144 | KO: 반죽을 펴서 파이·피자·빵 등을 준비할 때 쓰는 도구다. / EN: A tool used to roll dough when preparing foods such as pies, pizzas and bread. |
| C145 | KO: 물건을 담아 운반하는 자루다. / EN: A sack used to carry items. |
| C146 | KO: 자루를 열어 담긴 농산물을 꺼낼 수 있다 / EN: Open the sack to take out its produce. |
| C147 | 최근 보호된 현행 KO/EN 유지 |
| C148 | KO: 석기 도구를 만들거나 창을 깎는 데 쓰는 돌이다 / EN: A stone used to make stone tools or carve a spear. |
| C149 | KO: 매트리스나 모닥불 키트를 만드는 데 쓰는 천이다. / EN: Fabric used to make a mattress or campfire kit. |
| C150 | KO: 창문이나 난간 등에 설치해 오르내리는 데 쓰는 천 로프다 / EN: A sheet rope installed at suitable windows or railings for climbing. |
| C151 | KO: 구조물을 파괴하는 데 사용하는 도구다 / EN: A tool used to destroy structures. |
| C152 | KO: 작동하면 연기를 발생시키는 장치다 / EN: A device that produces smoke when triggered. |
| C153 | KO: 반죽이나 오믈렛 등을 준비할 때 쓰는 조리 도구다. / EN: A cooking utensil used to prepare foods such as dough and omelettes. |
| C154 | KO: 분해해 증폭기 부품을 회수하는 데 쓸 수 있다. / EN: Can be dismantled to recover an amplifier component. |
| C155 | KO: 찌르는 근접 공격에 쓰는 창이다 / EN: A spear used for thrusting melee attacks. |
| C156 | KO: 텐트 키트를 만드는 데 쓰는 재료다 / EN: A material used to make a tent kit. |
| C157 | KO: 상처 봉합을 돕고, 박힌 유리나 탄환을 제거하는 데 쓰는 의료 도구다. / EN: A medical tool that assists with stitching wounds and removing embedded glass or bullets. |
| C158 | KO: 천 물품을 제작하거나 바늘과 함께 상처를 봉합할 때 쓰는 실이다. / EN: Thread used to craft fabric items or stitch wounds together with a needle. |
| C159 | KO: 타이머 장치를 만드는 전자 부품이다. / EN: An electronic component used to make a timer. |
| C160 | KO: 호환되는 폭발물 등에 타이머를 붙이는 데 쓰는 부품이다. / EN: A component used to add a timer to compatible devices such as explosives. |
| C161 | KO: 통조림을 여는 데 쓰는 도구다. / EN: A tool used to open cans of food. |
| C162 | KO: 즉석 도구와 창 또는 부목을 만드는 데 쓰는 나뭇가지다 / EN: A branch used to make improvised tools, spears or splints. |
| C163 | KO: 호환되는 장치를 원격 조종할 수 있게 개조하는 부품이다. / EN: A component used to modify compatible devices for remote triggering. |
| C164 | KO: 손에 들고 비를 막으며, 접어 둘 수 있는 우산이다. / EN: An umbrella that protects from rain when held and can be folded. |
| C165 | KO: 물을 담아 운반하는 데 쓰는 빈 병이다 / EN: An empty bottle used to carry water. |
| C166 | KO: 쌀이나 파스타를 익혀 그릇에 나누어 담는 조리 준비물이다. / EN: Rice or pasta prepared for cooking and serving in bowls. |
| C167 | KO: 잘라내거나 쪼개서 먹을 부분을 준비하는 과일이다. / EN: A fruit that is sliced or smashed into portions for eating. |
| C168 | KO: 일부 금속 작업에 필요한 용접 마스크다 / EN: A welding mask required for some metalworking tasks. |
| C169 | KO: 금속 울타리·문 등 용접 제작에 쓰는 소모 재료다. / EN: A consumable material used when welding structures such as metal fences and doors. |
| C170 | KO: 호환되는 도구나 무기를 수리하는 데 쓰는 접착제다. / EN: An adhesive used to repair compatible tools or weapons. |
| C171 | KO: 주파수를 맞춰 무선 신호를 송수신하는 기기다 / EN: A two-way radio used to transmit and receive on a tuned frequency. |
| C172 | KO: 읽으면 해당 임시 무선기기의 제작법을 배운다 / EN: Reading it teaches the corresponding makeshift radio recipe. |
| C173 | KO: 주파수를 맞춰 라디오 방송을 듣는 기기다 / EN: A radio used to tune in to broadcasts. |
| C174 | KO: 모닥불 자리를 설치하는 데 쓰는 키트다 / EN: A kit used to place a campfire. |
| C175 | KO: 텐트를 설치하는 데 쓰는 키트다 / EN: A kit used to pitch a tent. |
| C176 | KO: 봉지를 열어 재배용 씨앗을 꺼낼 수 있다 / EN: Open the packet to obtain seeds for planting. |
| C178 | KO: 몸통 위에 걸쳐 입는 의류다. / EN: Clothing worn over the torso. 새 source-bound core 후보이며 현행 identity_fallback/admission을 수정하지 않음. |
| C179 | KO: 배꼽에 착용하는 장신구다. / EN: An accessory worn at the navel. 새 source-bound core 후보이며 현행 identity_fallback/admission을 수정하지 않음. |
| C180 | KO: 허리에 착용하는 벨트다. / EN: A belt worn around the waist. 새 source-bound core 후보이며 현행 identity_fallback/admission을 수정하지 않음. |
| C181 | KO: 몸에 착용하는 속옷류다. / EN: Underwear worn on the body. 새 source-bound core 후보이며 현행 identity_fallback/admission을 수정하지 않음. |
| C182 | KO: 상하체를 함께 덮어 입는 의류다. / EN: Clothing worn over the upper and lower body. 새 source-bound core 후보이며 현행 identity_fallback/admission을 수정하지 않음. |
| C183 | KO: 상체에 입는 의류다. / EN: Clothing worn on the upper body. 새 source-bound core 후보이며 현행 identity_fallback/admission을 수정하지 않음. |
| C184 | KO: 하의로 착용하는 속옷이다. / EN: Underwear worn on the lower body. 새 source-bound core 후보이며 현행 identity_fallback/admission을 수정하지 않음. |
| C185 | KO: 상의로 착용하는 속옷이다. / EN: Underwear worn on the upper body. 새 source-bound core 후보이며 현행 identity_fallback/admission을 수정하지 않음. |
| C186 | KO: 오른쪽 손목에 착용하는 장신구다. / EN: An accessory worn on the right wrist. 새 source-bound core 후보이며 현행 identity_fallback/admission을 수정하지 않음. |
| C187 | KO: 왼쪽 손목에 착용하는 장신구다. / EN: An accessory worn on the left wrist. 새 source-bound core 후보이며 현행 identity_fallback/admission을 수정하지 않음. |
| C188 | KO: 몸에 착용하는 꼬리 장식이다. / EN: A decorative tail worn on the body. 새 source-bound core 후보이며 현행 identity_fallback/admission을 수정하지 않음. |
| C189 | KO: 몸에 입는 원피스형 의류다. / EN: A one-piece garment worn on the body. 새 source-bound core 후보이며 현행 identity_fallback/admission을 수정하지 않음. |
| C190 | KO: 하체에 입는 의류다. / EN: Clothing worn on the lower body. 새 source-bound core 후보이며 현행 identity_fallback/admission을 수정하지 않음. |
| C191 | KO: 귀에 착용하는 장신구다. / EN: An accessory worn on the ears. 새 source-bound core 후보이며 현행 identity_fallback/admission을 수정하지 않음. |
| C192 | KO: 귀 윗부분에 착용하는 장신구다. / EN: An accessory worn on the upper ear. 새 source-bound core 후보이며 현행 identity_fallback/admission을 수정하지 않음. |
| C193 | KO: 다리에 착용하는 속옷 장식이다. / EN: An underwear accessory worn on the leg. 새 source-bound core 후보이며 현행 identity_fallback/admission을 수정하지 않음. |
| C194 | KO: 상체에 착용하는 의류다. / EN: Clothing worn on the upper body. 새 source-bound core 후보이며 현행 identity_fallback/admission을 수정하지 않음. |
| C195 | KO: 눈 부위에 착용하는 안경류다. / EN: Eyewear worn over the eyes. 새 source-bound core 후보이며 현행 identity_fallback/admission을 수정하지 않음. |
| C196 | KO: 손에 끼는 의류다. / EN: Clothing worn on the hands. 새 source-bound core 후보이며 현행 identity_fallback/admission을 수정하지 않음. |
| C197 | KO: 머리에 쓰는 의류나 장신구다. / EN: Clothing or an accessory worn on the head. 새 source-bound core 후보이며 현행 identity_fallback/admission을 수정하지 않음. |
| C198 | KO: 얼굴에 착용하는 의류나 장비다. / EN: Clothing or equipment worn on the face. 새 source-bound core 후보이며 현행 identity_fallback/admission을 수정하지 않음. |
| C199 | KO: 머리에 착용하는 장비다. / EN: Equipment worn on the head. 새 source-bound core 후보이며 현행 identity_fallback/admission을 수정하지 않음. |
| C200 | KO: 얼굴과 눈 부위에 착용하는 장비다. / EN: Equipment worn over the face and eyes. 새 source-bound core 후보이며 현행 identity_fallback/admission을 수정하지 않음. |
| C201 | KO: 전신에 착용하는 의류다. / EN: Clothing worn over the whole body. 새 source-bound core 후보이며 현행 identity_fallback/admission을 수정하지 않음. |
| C202 | KO: 허리에 착용하는 장비다. / EN: Equipment worn at the waist. 새 source-bound core 후보이며 현행 identity_fallback/admission을 수정하지 않음. |
| C203 | KO: 상체에 걸쳐 입는 겉옷이다. / EN: Outerwear worn on the upper body. 새 source-bound core 후보이며 현행 identity_fallback/admission을 수정하지 않음. |
| C204 | KO: 몸에 걸쳐 입는 가운이다. / EN: A robe worn on the body. 새 source-bound core 후보이며 현행 identity_fallback/admission을 수정하지 않음. |
| C205 | KO: 상하체에 함께 입는 내의다. / EN: Long underwear worn on the upper and lower body. 새 source-bound core 후보이며 현행 identity_fallback/admission을 수정하지 않음. |
| C206 | KO: 하체에 입는 내의다. / EN: Long underwear worn on the lower body. 새 source-bound core 후보이며 현행 identity_fallback/admission을 수정하지 않음. |
| C207 | 착용 후보 보류 — obsolete item 및 실제 슬롯 가용성 관계를 확인하기 전 기본 착용 core를 제안하지 않음 |
| C208 | KO: 목에 착용하는 긴 목걸이다. / EN: A long necklace worn around the neck. 새 source-bound core 후보이며 현행 identity_fallback/admission을 수정하지 않음. |
| C209 | KO: 목에 착용하는 장신구다. / EN: An accessory worn around the neck. 새 source-bound core 후보이며 현행 identity_fallback/admission을 수정하지 않음. |
| C210 | KO: 목에 착용하는 목걸이다. / EN: A necklace worn around the neck. 새 source-bound core 후보이며 현행 identity_fallback/admission을 수정하지 않음. |
| C211 | KO: 코에 착용하는 장신구다. / EN: An accessory worn on the nose. 새 source-bound core 후보이며 현행 identity_fallback/admission을 수정하지 않음. |
| C212 | KO: 몸에 걸쳐 입는 겉옷이다. / EN: Outerwear worn on the body. 새 source-bound core 후보이며 현행 identity_fallback/admission을 수정하지 않음. |
| C213 | KO: 왼손 약지에 착용하는 반지다. / EN: A ring worn on the left ring finger. 새 source-bound core 후보이며 현행 identity_fallback/admission을 수정하지 않음. |
| C214 | KO: 오른손 약지에 착용하는 반지다. / EN: A ring worn on the right ring finger. 새 source-bound core 후보이며 현행 identity_fallback/admission을 수정하지 않음. |
| C215 | KO: 목에 두르는 의류다. / EN: Clothing worn around the neck. 새 source-bound core 후보이며 현행 identity_fallback/admission을 수정하지 않음. |
| C216 | KO: 발에 신는 신발류다. / EN: Footwear worn on the feet. 새 source-bound core 후보이며 현행 identity_fallback/admission을 수정하지 않음. |
| C217 | KO: 하체에 입는 치마다. / EN: A skirt worn on the lower body. 새 source-bound core 후보이며 현행 identity_fallback/admission을 수정하지 않음. |
| C218 | KO: 발에 신는 양말류다. / EN: Socks worn on the feet. 새 source-bound core 후보이며 현행 identity_fallback/admission을 수정하지 않음. |
| C219 | KO: 몸에 입는 일체형 의류다. / EN: A full-body garment. 새 source-bound core 후보이며 현행 identity_fallback/admission을 수정하지 않음. |
| C220 | KO: 다리에 착용하는 속옷류다. / EN: Underwear worn on the legs. 새 source-bound core 후보이며 현행 identity_fallback/admission을 수정하지 않음. |
| C221 | KO: 몸통에 걸쳐 입는 조끼류다. / EN: A vest worn over the torso. 새 source-bound core 후보이며 현행 identity_fallback/admission을 수정하지 않음. |
| C222 | KO: 상처 감염을 치료하는 데 쓰는 약이다. / EN: Medicine used to treat wound infections. |
| C223 | KO: 텀블러에 따라 마시는 맥주다. / EN: Beer poured into a tumbler for drinking. |
| C224 | KO: 컵에 따라 마시는 맥주다. / EN: Beer poured into a cup for drinking. |
| C225 | KO: 텀블러에 재료를 섞어 만들어 마시는 음료다. / EN: A drink mixed from ingredients in a tumbler. |
| C226 | KO: 컵에 재료를 섞어 만들어 마시는 음료다. / EN: A drink mixed from ingredients in a cup. |
| C227 | KO: 불을 붙이는 재료나 연료로 태워 쓸 수 있다. / EN: Can be burned as tinder or fuel. |
| C228 | KO: 다친 부위에 바르는 약초 찜질제다. / EN: An herbal poultice applied to an injured body part. |
| C229 | KO: 던져 사용하는 공이다. / EN: A ball used for throwing. |
| C230 | KO: 열쇠를 담아 휴대하는 보관함이다. / EN: A container used to carry keys. |
| C231 | KO: 근접 공격에 쓸 수 있는 도구다. / EN: A tool that can be used for melee attacks. |
| C232 | KO: 침대를 만드는 데 쓰는 재료다. / EN: A material used to build a bed. |
| C233 | KO: 비스킷을 구운 뒤 나누어 꺼내는 데 쓰는 반죽이 든 틀이다. / EN: A tray of dough used to bake biscuits and remove them as portions. |
| C234 | KO: 통증 완화를 위해 복용하는 약이다. / EN: Medicine taken to relieve pain. |
| C235 | KO: 시간을 두고 불행감을 줄이는 데 쓰는 약이다. / EN: Medicine used to reduce unhappiness over time. |
| C236 | KO: 공포를 줄이기 위해 복용하는 약이다. / EN: Medicine taken to reduce panic. |
| C237 | KO: 잠드는 것을 돕기 위해 복용하는 약이다. / EN: Medicine taken to help with falling asleep. |
| C238 | KO: 피로를 줄이기 위해 복용한다. / EN: Taken to reduce fatigue. |
| C239 | KO: 모닥불 등에 보충하는 연료로 쓴다. / EN: Used as fuel for fires such as campfires. |
| C240 | 현행 KO/EN의 안전한 정체성 설명 유지; 새 기능·core·admission 추가 없음 |
| C241 | KO: 와인잔에 따라 마시는 와인이다. / EN: Wine poured into a wine glass for drinking. |
| C242 | KO: 물을 담거나 작물용 치료 분무액을 만드는 데 쓰는 빈 용기다. / EN: An empty container used to hold water or prepare crop-treatment sprays. |
| C243 | KO: 물을 담아 보관하고 공급하는 분무 용기다. / EN: A spray container used to store and supply water. |

### 반복 Menu 후속 질문 참조

| 참조 | 현재 판단 / 남은 질문 |
|---|---|
| M001 | not_observed — 상자는 개봉 recipe, 낱알은 총기/탄창 호환 |
| M003 | not_observed — 탄종·해당 총의 MagazineType 호환 |
| M004 | not_observed — 이 item의 evolved recipe·재료/조리/섭취 상태 조건 |
| M005 | not_observed — exact 원격/센서/타이머·투척/설치 조건; 피해량·유인/차폐 효율은 주장하지 않음 |
| M006 | not_observed — 설치/타이머 조건; 일반 알람시계와 구분 |
| M007 | not_observed — 알람 설정/소리·착용 여부 |
| M008 | not_observed — 상처 부착·교체/알코올 상태 조건 |
| M009 | actionable_gap / not_observed — 상처 소독 적용 조건 |
| M010 | not_observed — 상처 소독 대상/사용 조건 |
| M011 | not_observed — 실제 대상·상태·입력 조건 |
| M012 | not_observed — 해당 음식의 조리·부패/내용물·부분 섭취 조건 |
| M013 | actionable_gap / not_observed — 착용·탄약 조건을 Menu에서 확인해야 함 |
| M014 | not_observed — 호환 총기/부착 슬롯·도구 조건 |
| M016 | actionable_gap / not_observed — evolved recipe 관계가 현재 일반 RecipeIndex에서 미해결 |
| M017 | not_observed — 해당 슬롯의 착용/교체 조건이 후속 질문. 원문 Wear/교체 tooltip 경로는 확인; Iris 표시 결손은 미확정이며 core 부재만으로 actionable gap/N/A를 정하지 않음. |
| M018 | not_observed — 착용 슬롯·속성; 추가 효과는 exact source가 있는 경우만 |
| M019 | not_observed — 탄약·탄창/총기 속성 |
| M020 | not_observed — 나무·파손되지 않은 도구 조건 |
| M021 | not_observed — §남은 혼합 역할: 현재 놀이 assertion을 실제 게임 플레이/지루함 감소에 결속하지 못했다. Normal 소품과 실제 놀이 기능을 구분한다. |
| M022 | not_observed — 무기 속성/상태; 별도 연주·운동·작업 기능은 미확인 |
| M023 | not_observed — 용량·무게/착용 슬롯; 별도 수납 제한은 source가 있을 때만 |
| M024 | not_observed — exact identity/수납 기능 |
| M025 | actionable_gap / not_observed — 같은 절의 item별 대상·미끼·시간/상태 조건 |
| M026 | not_observed — 해당 action의 입력·대상·상태 조건 |
| M027 | not_observed — 같은 절의 item별 recipe/도구·재료 조건 |
| M028 | not_observed — GetMuffin cooked predicate·내용물/부패·틀 회수 |
| M029 | not_observed — 목공 구조물/재료 조건 |
| M030 | actionable_gap / not_observed — 상처 부착/교체 조건 |
| M031 | not_observed — 오염·bandageLife=0/교체 조건 |
| M032 | not_observed — 대상 구조물/재료 requirement |
| M033 | not_observed — 현재 경기 규칙에 맞춘 놀이 assertion을 실제 경기/투척 기능과 결속하지 못했다. Normal 소품이라는 선언은 경기 실행 근거가 아니다. |
| M034 | not_observed — 무기 속성·해당 제작 관계 |
| M035 | actionable_gap / not_observed — 잔여 사용량·표백제 조건 |
| M036 | not_observed — 기기별 삽입/제거·빈 전지 조건 |
| M038 | not_observed — 섭취량·알코올 효과·요리 조건 |
| M039 | not_observed — 이 빈 item의 재사용/처리 목적을 실제 전환·상호작용에 결속하지 못했다. 빈 용기라는 이름만으로 물 저장 가능성을 추가하지 않는다. |
| M040 | not_observed — 물 채우기·내용물 상태 |
| M041 | not_observed — 물 채우기·내용물/오염 상태; 조리/관수 등 추가 역할은 별도 |
| M042 | not_observed — Normal Bell의 소리 발생/상호작용 경로를 결속하지 못했다. 이름이 효과를 증명하지 않는다. |
| M044 | not_observed — Base.Belt는 Normal이며 착용 슬롯이 결속되지 않았다. 다른 착용형 belt의 행동을 복사하지 않는다. |
| M045 | not_observed — 차종·상태에 따른 실제 용량·탈착/급유 조건 |
| M046 | not_observed — 차종/슬롯·실제 용량·해당 수리 또는 탈착 가능 조건 |
| M047 | actionable_gap / not_observed — 청소 도구·혈흔 대상 |
| M048 | not_observed — 토치 충전과 작업별 요구 재료 |
| M049 | not_observed — 기록물·지도·잠금/색상 조건 |
| M050 | not_observed — 사진의 Normal 정체성/원문 locator 확인; 보기·놀이·수집 action 또는 public identity-core 근거는 미확정. 유사 매체의 재생·학습 기능을 전이하지 않음. |
| M051 | not_observed — 읽기 효과·조건 또는 필기구/잠금 조건 |
| M053 | not_observed — 기술서는 구현한 범위/독서 조건; 잡지는 배우는 recipe/지식의 실제 조건 |
| M054 | not_observed — 장난감의 Normal 정체성/원문 locator 확인; 보기·놀이·수집 action 또는 public identity-core 근거는 미확정. 유사 매체의 재생·학습 기능을 전이하지 않음. |
| M055 | not_observed — 해당 기능의 실제 표시/상태 조건 |
| M056 | not_observed — 개봉 recipe |
| M057 | not_observed — 무기 속성·제작/회수 recipe; 부착 재료와 완성 창 구분 |
| M058 | not_observed — 수리/교체 가능성은 미관찰 |
| M059 | actionable_gap / not_observed — 대상·파손/표백제 조건 |
| M060 | not_observed — Drainable 선언만으로 현행 제작·수리 소비 경로 미확정; exact recipe/action 입력 관계 필요. |
| M061 | not_observed — Normal Button의 의류 부착/수선 사용 경로를 결속하지 못했다. |
| M062 | not_observed — 촬영·필름 소모/사진 결과 |
| M063 | not_observed — 점화 재료·연료·잔여 사용량/불 상태 |
| M064 | not_observed — 해당 기능의 대상·입력·상태 조건 |
| M065 | not_observed — 해당 개봉 recipe·결과/상태 보존 |
| M066 | not_observed — 내용물·섭취량·부패·호환 evolved recipe 조건 |
| M067 | not_observed — 차종·잔량·엔진 작동/충전 조건 |
| M068 | not_observed — 전원·배터리 호환/충전 조건 |
| M069 | not_observed — Normal 선언은 확인되나 exact 사용/조리 입력이 미확정; 유사 도구·Teabag2·Flour의 기능 전이 금지. |
| M070 | not_observed — 무기 속성; 별도 작업 기능은 미확인 |
| M071 | not_observed — 연료량·점화·지원 장치 상태 |
| M072 | not_observed — Normal item의 세척 selector 연결 미확인; 확인된 Soap2/CleaningLiquid2 기능을 이 ID에 복사하지 않음. |
| M073 | not_observed — 무기 속성; 해당 도구의 추가 정비/작업 역할 미확인 |
| M075 | actionable_gap / not_observed — 커피 조리법/재료 조건 |
| M076 | not_observed — 해당 제작 recipe |
| M077 | not_observed — §남은 혼합 역할: 향수 사용·캐릭터 효과의 exact 게임 경로가 미확인이다. |
| M078 | not_observed — §남은 혼합 역할: 빗질/머리 정돈의 exact 게임 경로가 미확인이다. |
| M079 | not_observed — 해당 습포 recipe·절구/재료 조건 |
| M081 | not_observed — Normal 선언만으로 현행 제작·수리 소비 경로 미확정; exact recipe/action 입력 관계 필요. |
| M082 | not_observed — 주방 소품의 현실 사용을 actual 조리/상차림 interaction에 결속하지 못했다. exact 역할이 확인된 식재료/도구와 분리한다. |
| M083 | not_observed — Drainable 선언은 확인되나 exact 사용/조리 입력이 미확정; 유사 도구·Teabag2·Flour의 기능 전이 금지. |
| M084 | not_observed — 현금/카드/지갑 identity 외 사용·수납 상호작용이 미결속이다. Normal 지갑을 Container나 결제 기능으로 설명하지 않는다. |
| M085 | not_observed — 대상 바리케이드·도구 조건 |
| M086 | not_observed — 붕대/제작 role별 대상과 recipe 조건 |
| M088 | not_observed — 소화 대상·잔여 사용량; 흙 살포 질문은 미해결 |
| M089 | not_observed — Normal base item과 runtime recorded-media 데이터 binding 미확인; MediaCategory가 있는 Retail/Home variant의 재생 기능 복사 금지. |
| M090 | not_observed — 인스턴스의 녹화 데이터·media type·기기 전원/재생·내용별 학습 조건 |
| M091 | not_observed — 개에게 씹게 하는 게임 동작/대상 선택을 결속하지 못했다. DogChew 명칭을 반려견 상호작용 근거로 쓰지 않는다. |
| M092 | not_observed — 개봉 recipe·따개 조건 |
| M093 | not_observed — 탄약 호환/절단 recipe |
| M094 | not_observed — 총별 탄약/탄창·무기 속성 |
| M095 | not_observed — 연료 채우기/급유 조건 |
| M096 | not_observed — 차종/차체 슬롯·도구/정비 조건 |
| M097 | not_observed — exact 차종 해당 엔진·도구/기술·상태 조건 |
| M098 | not_observed — 주석 제거/편집 조건 |
| M099 | not_observed — 잔량·소화 대상/영구 불 제외 |
| M101 | not_observed — 해당 낚싯대 제작·수리 recipe |
| M102 | not_observed — 수리 recipe·줄/클립 조건 |
| M103 | not_observed — Normal Frame을 실제 사진/그림 넣기 상호작용에 결속하지 못했다. Container로 가정하지 않는다. |
| M104 | not_observed — 흙/경작 위치·파손 상태 |
| M105 | not_observed — Saw Logs2 recipe/도구 조건 |
| M106 | not_observed — 연결 지식·연료·작동 조건 |
| M108 | not_observed — 장벽 재료·잔여 사용량·소화 대상 |
| M109 | not_observed — 염색 대상·색상/소모 조건 |
| M110 | not_observed — 지원 머리 모양/소모 조건 |
| M111 | not_observed — 제작 recipe |
| M112 | actionable_gap / not_observed — 구조물별 재료·도구 조건 |
| M113 | not_observed — 목공 구조물·못/재료 조건 |
| M114 | not_observed — 같은 절의 전원·매체/주파수·운동 조건 |
| M116 | not_observed — 착용 슬롯·해당 실제 방어/보온 값 |
| M117 | not_observed — 문·게이트별 requirement |
| M118 | not_observed — Normal 선언과 문구류 정체성만으로 작성·수정·종이 정리 action을 뒷받침할 수 없음; 이 exact item의 사용 handler/input 관계 필요. |
| M120 | not_observed — 대상 차량·탈착 작업 조건 |
| M122 | not_observed — 뜨개질 recipe/행동 |
| M125 | not_observed — §남은 혼합 역할: 반려견에게 매는 actual interaction이 미결속이다. |
| M126 | not_observed — 의류·바늘·기술별 수선 조건 |
| M127 | not_observed — exact item identity/source 미확인 |
| M128 | not_observed — 화장 종류·거울/도구 조건 |
| M129 | not_observed — 실제 착용 슬롯/행동 |
| M130 | not_observed — 판자/키트 recipe와 도구 |
| M131 | not_observed — 묶음 해체 recipe |
| M132 | not_observed — 차량/잭/정비 조건 |
| M133 | not_observed — Type=Map이나 Map ID 미선언; ISMapDefinitions.lua:257의 Init dispatch에 필요한 runtime mapID/데이터 귀속 미확인. |
| M135 | not_observed — 창문/대상·토치/보호구 조건 |
| M137 | not_observed — 해당 제작 recipe와 input 조건 |
| M138 | not_observed — 화장 도구·거울 대안 조건 |
| M139 | not_observed — exact 차종 1·도구/기술·상태 조건 |
| M140 | not_observed — exact 차종 2·도구/기술·상태 조건 |
| M141 | not_observed — exact 차종 3·도구/기술·상태 조건 |
| M142 | actionable_gap / not_observed — 표백제·혈흔 조건 |
| M144 | not_observed — 사용 제작물과 재료/도구 requirement |
| M145 | not_observed — 수선 대상/실·기술 조건 |
| M146 | not_observed — exact 원본 item 선언이 미결속이다. NoiseTrap 또는 다른 이름의 장치로 대체하지 않는다. |
| M147 | not_observed — 필기구·잠금/페이지 조건 |
| M148 | not_observed — 도료·벽면/표식 조건 |
| M149 | not_observed — 낚싯대 recipe와 다른 재료 |
| M150 | not_observed — 실제 내용물·조리 완료·그릇 수/나누기 callback |
| M151 | not_observed — 가지/막대·체력·점화 실패/파손 조건 |
| M152 | not_observed — 급유 대상/잔량/화재 위험 조건 |
| M155 | not_observed — 기존 연결 detail와 작업 조건 |
| M156 | not_observed — 관련 목공·제작 requirement |
| M157 | not_observed — 조리·부패·섭취량 |
| M158 | not_observed — 토치 충전 requirement |
| M160 | not_observed — 면도/수염 선택 조건 |
| M161 | not_observed — 연결 가능한 장치·ID·작동 범위, 실제 서버/장치 동작 |
| M162 | not_observed — 결속에 필요한 제작/설치 requirement |
| M164 | not_observed — 전지 삽입 조건·제거 recipe |
| M165 | not_observed — 해당 개봉 recipe·내용물/상태 보존 |
| M166 | not_observed — 목재/총열 절단 recipe와 requirement |
| M167 | not_observed — 기존 연결 제작 requirement |
| M168 | not_observed — 구조물/제작 requirement |
| M169 | not_observed — 해당 조립·수리 requirement |
| M170 | not_observed — 제작/깎기 recipe와 keep 여부 |
| M171 | not_observed — 작은 금속판 제작 recipe/조건 |
| M172 | not_observed — 높이·대상·못/개수·등반 조건 |
| M173 | not_observed — 파괴 가능한 대상·도구 상태·서버 허용 |
| M174 | not_observed — 큰 금속판 제작 recipe/조건 |
| M175 | actionable_gap / not_observed — 골절 부위·제외 부위 조건 |
| M176 | not_observed — 텐트 키트 recipe와 재료 |
| M177 | not_observed — 돌망치 제작 recipe |
| M179 | not_observed — 봉합 interaction과 대상 조건 |
| M180 | not_observed — 타이어 상태·압력 조건 |
| M183 | not_observed — 보관 용량/무게 정보; 화면 not_observed |
| M184 | not_observed — §남은 혼합 역할: Toothbrush의 양치 actual interaction이 미결속이다. |
| M185 | not_observed — §남은 혼합 역할: Toothpaste의 양치 actual interaction이 미결속이다. |
| M186 | not_observed — 각 제작 recipe·재료/도구 |
| M187 | not_observed — 유리/총알 제거의 대상·조건 |
| M188 | not_observed — 모닥불 키트 recipe |
| M189 | not_observed — 각 item에 연결된 덫/어망 recipe |
| M191 | not_observed — 해체 잔재의 identity와 별개로 '재료로 쓸 수 없음'이라는 전면 부정의 범위를 입증하지 못했다. |
| M192 | not_observed — 모닥불 연료 투입 관계 |
| M193 | not_observed — 물 채우기·추가 제작 관계 |
| M194 | not_observed — Normal WaterDish 선언만으로 물 담기/섭취의 실제 CanStoreWater·전환 경로가 결속되지 않았다. |
| M195 | not_observed — cooked 상태·그릇 나누기·추가 재료 조건 |
| M196 | not_observed — 작업별 소지·토치/용접봉 조건 |
| M197 | not_observed — scripts/recipes.txt:1211 이후 Wild Garlic Poultice 선언은 obsolete 주석 경계다. 직접 소독/약효도 미결속이며 WildGarlic2를 복사하지 않는다. |
| M198 | not_observed — 무기 속성과 사용 조건 |
| M200 | not_observed — 전원·주파수·송신/수신 조건 |
| M201 | not_observed — 배우는 exact recipe: Craft Makeshift Radio |
| M202 | not_observed — 배우는 exact recipe: Craft Makeshift Walkie Talkie |
| M203 | not_observed — 배우는 exact recipe: Craft Makeshift HAM Radio |
| M204 | not_observed — 전원·주파수/수신 조건 |
| M205 | not_observed — Normal 선언은 확인되나 actual scan/assembly input 연결 미확인; 이름을 근거로 신호 확인 기능 주장 금지. |
| M206 | not_observed — 설치 가능 위치·별도 연료/점화 |
| M207 | not_observed — Kit과 다른 item의 설치/수면 관계 |
| M208 | not_observed — 설치 공간·수면/휴식 조건 |
| M209 | not_observed — Flint의 exact 점화 선택/소모 경로가 미결속이다. SteelAndFlint나 다른 점화재로 추론하지 않는다. |
| M210 | not_observed — SteelAndFlint의 exact 점화 선택/소모 경로를 결속하지 못했다. Lighter/Matches나 이름이 다른 Flint와 합치지 않는다. |
| M211 | not_observed — 해당 씨앗의 개봉/재배 조건 |
| M212 | not_observed — 작물별 파종 수량·물/성장 조건 |
| M214 | not_observed — 추가 Wear의 현재 방향/좌우·후드 선택과 교체 대상이 후속 질문. 원문 extra menu/self FullType 경로는 확인; Iris 표시 결손은 미확정이며 core 부재만으로 actionable gap/N/A를 정하지 않음. |
| M216 | not_observed — 정상 B41의 legacy 단조/기술·용광로 또는 재고 드럼통 경로 가용성 미확정. 존재하는 handler를 기능 부재로 바꾸지 않고 활성 경로 입력을 기다림. |
| M217 | not_observed — 복용 조건·발현/효과량·상태와 실제 Menu 답. 기본 목적은 vanilla의 exact 안내이며 추가 효과·좀비 감염 치료 주장은 없음 |
| M218 | not_observed — 해당 evolved recipe의 재료·용기·실제 내용물과 섭취량; 고정 H/T 효과는 발행하지 않음 |
| M219 | not_observed — 드라이버·즐겨찾기 제외·분해 결과; 촬영/필름 기능은 추가하지 않음 |
| M220 | not_observed — 지원되는 불/장치·라이터 등 점화 도구·잔량/소모 조건. 원래 주장한 청소·놀이·결제 기능은 추가하지 않음. |
| M221 | not_observed — obsolete exact item의 정상 B41 가용성·대체 ID와의 구분이 필요; 부재/무용도/N/A로 확정하지 않음. |
| M222 | not_observed — 부상 부위·기존 찜질제 없음·소지/환자 이동 조건; 어떤 회복을 얼마나 빠르게 하는지는 이 후보에 추가하지 않음 |
| M223 | not_observed — 투척·회수와 PhysicsObject 상태; 실제 경기나 harmless/공격 성능을 추정하지 않음 |
| M224 | not_observed — Key category 수납 제한과 용량; 실제 Menu 표시 미관찰 |
| M225 | not_observed — 무기 상태·공격 속성; 미확인 재배/흙 작업은 후보에서 제외 |
| M226 | not_observed — 침대 제작 재료·도구/목공 조건; 독립 Moveable 배치/수면 효과는 미확정 |
| M227 | not_observed — 해당 sprite의 배치 가능/필요 도구·방향/위치 조건. B41 sprite 속성과 실제 객체 귀속이 먼저 필요하며 Menu 결손/N/A를 단정하지 않음. |
| M228 | not_observed — cooked/burnt 분리 조건·비스킷 6개/틀 회수; 굽지 않아도 먹을 수 있다는 주장 없음 |
| M229 | not_observed — 지원되는 불/장치·연료량·점화 조건 |
| M230 | not_observed — 현행 정체성 설명만으로 새 gameplay 질문/결손을 강제하지 않음. 기능 확대나 실제 Menu N/A 판정은 하지 않음. |
| M231 | not_observed — 물 채우기 및 치료액별 recipe 입력/학습 조건 |
| M232 | not_observed — 물의 잔량·채우기/비우기·대상 조건; 치료 분무액 효과로 확장하지 않음 |

전수 제안 작성과 후속 보류 재판정에서 새 테스트, baseline 재검사, proof 파일, canonical 채택 또는 외부 경로 접근은 수행하지 않았다. 다음 내용 작업은 273개 보류의 명시된 입력·적용 조건 해결이며, 이미 source가 준비된 후보의 채택·generation 미실행과 구분한다. 기존 후보에 추가 봉인/검증 체계를 만들지 않는다.
