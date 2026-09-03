# Build 41 EvolvedRecipe candidate closeout

## 상태

`observed_pass / adopted`. 사용자는 2026-09-03에 v6 실제 PZ 관찰 체크리스트 전 항목의 통과를 명시적으로 보고했다. 관찰된 runtime SHA-256, candidate/package manifest와 owner 결속을 재확인한 뒤 guarded updater가 정확히 그 v6 lookup을 저장소 runtime에 채택했다. v1~v4의 실제 실패와 v5의 관찰 전 superseded 상태는 predecessor 이력이며 v6 결과로 소급 변경하지 않는다.

## Source accounting

- Build 41 source root: `G:/Program Files (x86)/Steam/steamapps/common/ProjectZomboid`
- lexical occurrence `347`; active property row `226`; raw token `2,185`
- PASS property source token `2,175`; property-side deduplicated relation `2,165`
- definition `BaseItem` relation `38` occurrence / `32` unique FullType; non-Food `17` / `13`
- 전체 public relation `2,203`; public FullType `252`; property REVIEW `0`; definition-base REVIEW `0`; obsolete non-target token `10`
- 계획 기준선과의 차이: raw token `-2`; lexical/active/definition delta `0`
- `zombie/core/Translator.class` SHA-256 `b09aeeb6d473eacd2cc4bc1ce0176a1aed29b4f3d0bf56203fc2c90e9d54fdbf`; `parseFile`의 first-definition-wins 동작에 결속해 EN/KO 중복 key의 유효값을 선택했다.
- Owner output: `Iris/build/description/v2/data/evolved_recipe_owner.b41.json`

각 public relation은 exact FullType, food type ID, `ingredient`/`spice`/`base_item`, relation-local 조건, stable identity, KO/EN display와 provenance를 가진다. `base_item`은 definition `BaseItem` field의 별도 참여 역할이고 conditions는 비어 있으며 provenance에 `definition_base_item` source role과 definition/field line을 기록한다. Fixed Recipe의 `rule_id`, `recipe_id`, `recipe_nav_ref`, `ResultItem`이나 합성 결과물은 runtime projection에 없다.

Definition side는 Food/비Food를 가리지 않고 38개 definition occurrence 전부를 포함한다. Item inventory Type은 `Food 21`, `Normal 8`, `Drainable 7`, `Weapon 2`이며 type은 census에만 쓰고 public role을 바꾸지 않는다. 같은 FullType의 양쪽 관계도 보존한다. 예를 들어 `Base.BreadSlices`는 Salad/Soup/Stew `ingredient`와 Sandwich/Burger `base_item`이 공존한다. `Base.Bowl`은 Salad/FruitSalad, `Base.WaterPot`은 Soup/Stew의 `base_item`이다. Definition side를 item `EvolvedRecipe` property로 역합성하거나 Food/ingredient/spice로 바꾸지 않는다.

## Candidate와 package

- UX/regression FAIL candidate A: `C:/Users/MW/PZ-U/candidate/relation-a`
- UX/regression FAIL candidate B: `C:/Users/MW/PZ-U/candidate/relation-b`
- UX/regression FAIL package: `C:/Users/MW/PZ-U/package/iris-qg/Iris`
- Current owner SHA-256: `d6e4832d7d9960761acbee2c8eedfa48ad584528335b9013896f4e0ec94d647e`
- FAIL runtime lookup SHA-256: `044810f842d45ddb97f1c5b561c5e22ec5f2675e77e24a2fcfbda04d8e3e8111`
- FAIL candidate manifest SHA-256: `c942077eb435056084f784f683ee6a7d39d5fa10b90f4be42a4530a6ca4ce166`
- FAIL package manifest SHA-256: `27b48ddee7728357f10f2ed9da9bdb219c391d6826c8d9fd48974a606986867c`
- KO rendering FAIL v2 candidate: `C:/Users/MW/PZ-U/candidate/evolved-v2`
- KO rendering FAIL v2 package: `C:/Users/MW/PZ-U/package/iris-v2/Iris`
- KO rendering FAIL v2 runtime lookup SHA-256: `551deff13e508cb79526e22a6513e1a988b95ba6ba9d77b41e3c22f233c7b40d`
- KO rendering FAIL v2 candidate manifest SHA-256: `8acfd1fc3cc593410a61bbfcea72d30c1ce23521ac607de4696a3d33ca8fd523`
- KO rendering FAIL v2 package manifest SHA-256: `25a92012827856ee8196305dd7f3ce4ee4c7b6ed2a0b84a7497fdc489fb9cbcb`
- Scope-review v3 candidate A/B: `C:/Users/MW/PZ-U/candidate/evolved-v3-a`, `C:/Users/MW/PZ-U/candidate/evolved-v3-b`
- Scope-review v3 package source(설치 금지): `C:/Users/MW/PZ-U/package/iris-v3/Iris`
- Successor v3 runtime lookup SHA-256: `60b0d023a29c1613384b33b9b2d287b90bee37d49fdf8fbeec509893603dd1e6`
- Successor v3 candidate manifest SHA-256: `5c54e229f56da6d900a92887af4bf960c1ebbaa92e2e53fa176903d57f684014`
- Successor v3 package manifest SHA-256: `57e9bf9088b0a57a866e6844d0cfb39a5b02bdd5a0e0992334db990a837ac4ed`
- Observation v4 candidate A/B: `C:/Users/MW/PZ-U/candidate/evolved-v4-a`, `C:/Users/MW/PZ-U/candidate/evolved-v4-b`
- Observation v4 package source: `C:/Users/MW/PZ-U/package/iris-v4/Iris`
- Observation v4 runtime lookup SHA-256: `5ed5773ba2da2e6dfb13eb853a9b219204cea396607a3399add15a5b64f8ad91`
- Observation v4 candidate manifest SHA-256: `8624f7461d5b29d69601f653916cc1fd15a2776a5994c0053dc2c755b51868dd`
- Observation v4 package manifest SHA-256: `9460d7b574bf371b6a3f52dc6bd83fdea46f17db781b0654a299893c8b1e19ba`
- Observation v5 candidate A/B: `C:/Users/MW/PZ-U/candidate/evolved-v5-a`, `C:/Users/MW/PZ-U/candidate/evolved-v5-b`
- Observation v5 package source: `C:/Users/MW/PZ-U/package/iris-v5/Iris`
- Observation v5 runtime lookup SHA-256: `5d3e890e30f51d60efdbb69b59c4862221dcfbef7a586b19eb6a6cfb0d3b2e81`
- Observation v5 candidate manifest SHA-256: `79e1d20893d96fd2be5c6d58cc2dda47779eefd4a7e859212675504446493e50`
- Observation v5 package manifest SHA-256: `f94b63ed09d5ccac7032a5970e415caaff86cdde265e0bbd09165b077765de8b`
- Observation v6 candidate A/B: `C:/Users/MW/PZ-U/candidate/evolved-v6-a`, `C:/Users/MW/PZ-U/candidate/evolved-v6-b`
- Observation v6 package source: `C:/Users/MW/PZ-U/package/iris-v6/Iris`
- Observation v6 runtime lookup SHA-256: `0b86cb8a2638df627f94bbb27af759b9b46e54c55081504da04aefcc8e353088`
- Observation v6 candidate manifest SHA-256: `af2ca7fe5ce2943fe3f5b64decd02ff279a42ec883977885d06aaad74ccf0491`
- Observation v6 package manifest SHA-256: `510f6dba14bcd328d70cea06eb4bbf6de8541f03f07b216d4a5bd4f739bd6d2b`
- Adopted repository runtime: `Iris/media/lua/client/Iris/Data/IrisEvolvedRecipeLookup.lua`
- Adopted repository runtime SHA-256: `0b86cb8a2638df627f94bbb27af759b9b46e54c55081504da04aefcc8e353088`

첫 A/B의 manifest와 runtime bytes는 동일했지만 실제 PZ 관찰에서 fixed presentation 회귀가 발견되어 채택 대상이 아니다. v2는 fixed presentation을 분리했으나 raw UTF-8 Lua literal이 B41에서 손상되고 사용자 행에 내부 food type ID를 노출해 다시 FAIL했다. v3는 encoding/UI를 고쳤지만 definition side를 빠뜨린 scope-review 후보로 supersede됐다. v4는 전체 definition relation을 포함했지만 standalone 의미가 아닌 vanilla 문법 조각을 복사했고 EN Recipe section이 클릭되지 않아 not-adoptable이다. v5는 food type ID 38개 모두에 명시적인 standalone KO/EN target을 등록하고 role/condition별 행동 문장으로 생성했지만 관찰 전 `이 아이템으로 … 준비 가능`을 자연화할 필요가 확인되어 supersede됐다. v6는 KO `base_item`만 `… 준비에 사용할 수 있음`으로 바꾸고 EN과 나머지 의미 계약을 유지한다. 모든 candidate/package는 별도 경로에 staging했으며 자동화는 사용자의 일반 `Zomboid/mods/Iris` 설치본을 덮어쓰지 않았다.

## 실제 PZ 관찰 진행 메모

- 첫 candidate(`044810f8...e8111`)의 `Base.Salt` 화면에서 고정 Recipe `4`, EvolvedRecipe/자유 조리 `21`, 합계 `25`라는 데이터 로딩은 확인됐다.
- 그러나 Evolved 관계를 더한 combined total `25`로 기존 fixed presentation density까지 `dense`로 재계산하여, Evolved 도입 전 기본 표시돼야 할 Recipe 이름 4개와 navigation을 counts-only 상태로 숨겼다. 이는 기존 QG presentation 보존 회귀이자 사용자 목표 미충족이므로 첫 candidate는 FAIL이며 채택하지 않는다.
- v2는 fixed Recipe 4개와 navigation을 복원했지만 KO 행이 깨진 문자열로 보이고 `(Beer)`, `(Burger)`, `(Stir fry Griddle Pan)` 같은 내부 ID를 노출했다. v2는 KO rendering FAIL이며 채택하지 않는다.
- v4는 fixed Recipe/Right-click의 total·density·visible rows·navigation을 관계 유무와 무관하게 보존한다. 자유 조리는 별도 density·expanded·query state와 `+/- 자유 조리 (n)` control을 가지며 행은 계속 non-clickable이다.
- v4 KO Salt는 fixed Recipe 4와 자유 조리 21 전개/개수, KO Bowl/WaterPot, Bacon/Mushroom, EN relation 21, Tooltip 무회귀를 확인했다. 그러나 `텀블러 — 향신료`, `준비를 시작하는 아이템`, `in a Tumbler — spice`처럼 행동 의미가 완결되지 않았고 EN Recipe section 클릭이 동작하지 않아 partial FAIL이다.
- v6 사용자 관찰에서 KO `Base.Salt`의 fixed Recipe 4개는 이름과 navigation을 보존한 채 접기/펼치기가 동작했고, 자유 조리 21개는 별도 전개 상태와 행동형 문구로 표시됐다.
- KO `Base.Bowl`/`Base.WaterPot`의 `base_item` 행은 `… 준비에 사용할 수 있음`으로 자연스럽게 표시됐다. Bacon/Mushroom의 역할·조건 문구와 Salt→Mushroom 전환도 일치했고 이전 Salt relation/query가 남지 않았다.
- EN 전환 후 Recipe section 접기/펼치기, navigation 복원, 관계 수와 행동형 문구가 KO와 같은 relation set에 결속됐다. Evolved 행은 non-clickable 상태를 유지했고 Tooltip은 변경되지 않았다.
- 이 사용자 보고는 계획의 최대 네 대표 사례와 KO/EN 재사용 범위에 대한 Gate 3 실제 관찰 PASS다. 모든 게임 상태나 가능한 조리 조합 전수를 관찰했다는 뜻은 아니다.

## 실행한 검증

- `uv run --project .\Iris\tooling --no-sync pytest .\Iris\tooling\tests\test_evolved_recipe.py`: exit `0`, `4 passed`; canonical decimal byte escape/B41 Lua KO round-trip, definition base 38/32·non-Food 17/13, Bowl/WaterPot/BreadSlices 대표 관계, exact 38 standalone target registry와 action-oriented KO/EN surface 및 자연화한 KO `base_item` 문구를 포함한다.
- `Iris/test/test_adaptive_interaction_presentation.py`의 변경 관련 선택 3건: exit `0`, `3 passed`; 이 중 한 건이 집중 Lua harness를 한 번 실행했다.
- 집중 Lua harness는 fixed state가 `verified_empty`인 관계-only projection, `base_item`의 별도 role/행동 표시, 관계 유무 간 fixed density/identity/order/navigation parity, 동일 locale 라벨·role·condition grouping과 exact identity 보존, locale 전환 후 EN Recipe section click→forced rebuild→collapse/expand 및 navigation 복원, Salt형 fixed 4행과 `Freeform Cooking (21)`, Salt→Mushroom exact relation/query 격리, 별도 검색, non-clickable·prefix-free 행과 폭 기반 무손실 줄바꿈을 확인했다.
- candidate 단계 `powershell -ExecutionPolicy Bypass -File .\tools\check_lua_syntax.ps1`: exit `0`, `264 files`
- FAIL candidate A/B 생성·검증·byte 비교: exit `0`이었으나 실제 presentation 회귀로 reject
- Successor candidate v3 A/B 생성·각 validation·별도 package staging 및 A/B/package byte 비교: exit `0`; runtime/package manifest hash는 위에 기록
- Observation candidate v4 A/B 생성·각 validation·별도 package staging 및 A/B/package byte 비교: exit `0`; runtime/package manifest hash는 위에 기록
- Observation candidate v5 A/B 생성·각 validation·별도 package staging 및 A/B/package byte 비교: exit `0`; runtime/package manifest hash는 위에 기록
- Observation candidate v6 A/B 생성·각 validation·별도 package staging 및 A/B/package byte 비교: exit `0`; runtime/package manifest hash는 위에 기록
- Fixed Recipe/Right-click data와 Tooltip bounded owner input/runtime payload의 final no-diff: exit `0`
- v6 pre-adoption binding: exit `0`; owner `d6e483…d647e`, A/B runtime, candidate manifest와 package manifest가 관찰 runtime `0b86cb…3088`에 결속되고 A/B/package runtime bytes가 동일함을 확인했다.
- `uv run --project .\Iris\tooling --no-sync iris-tooling --repository-root . layer4 evolved-recipe adopt --owner '.\Iris\build\description\v2\data\evolved_recipe_owner.b41.json' --candidate-root 'C:\Users\MW\PZ-U\candidate\evolved-v6-a' --repository-root . --observed-runtime-sha256 '0b86cb8a2638df627f94bbb27af759b9b46e54c55081504da04aefcc8e353088'`: exit `0`, `PASS: EvolvedRecipe guarded adoption applied`
- 사후 owner/candidate projection validation: exit `0`; schema v6, owner/runtime hash와 relation metrics 일치
- 사후 adopted runtime/observed candidate byte parity와 fixed Recipe/Right-click·Tooltip bounded payload no-diff: exit `0`
- 사후 `powershell -ExecutionPolicy Bypass -File .\tools\check_lua_syntax.ps1`: exit `0`, `265 files`

v4 자동 검증은 predecessor 후보에 결속되고 실제 관찰에서 partial FAIL했다. v5는 관찰 전 supersede됐다. v6만 action-oriented semantic parity, item 전환과 EN Recipe section callback을 포함한 focused 자동 범위와 사용자 실제 관찰을 모두 통과했고, 관찰 hash와 byte-identical한 runtime으로 채택됐다.

참고로 `Iris/test/test_adaptive_interaction_presentation.py` 전체 7건 실행은 이번 변경과 무관한 기존 Layer 3 수치 assertion(`2072`)이 현재 projection의 `2099`와 달라 `6 passed, 1 failed`였다. 이번 범위를 벗어난 고정 수치는 수정하거나 새 Gate로 확대하지 않았다.

## 남은 한계

Gate 3와 v6 채택은 완료됐다. 실제 PZ 확인은 Salt, Bowl/WaterPot, Bacon/Mushroom을 KO/EN에서 재사용한 대표 관찰이며 모든 아이템·게임 상태·가능한 조리 조합 전수를 증명하지 않는다. 향후 source, standalone target, 표시 template 또는 runtime bytes가 달라지면 이번 관찰을 새 payload에 승계하지 않고 새 candidate/hash로 다시 관찰해야 한다.
