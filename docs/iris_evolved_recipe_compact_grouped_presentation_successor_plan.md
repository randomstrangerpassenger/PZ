# Iris EvolvedRecipe 간결 표현·고밀도 그룹화 구현 계획

- 상태: 완료 — v7 `observed_pass / adopted`, 2026-09-03
- 대상 문제: EvolvedRecipe 설명의 장문 반복, 저밀도 맥락 부족, 고밀도 탐색성 저하
- 기준선: 현재 채택된 EvolvedRecipe v6 owner/candidate/runtime
- 원칙: 의미 보존, 기존 경로 재사용, 최소 검증 Gate

## 1. Objective

EvolvedRecipe 행을 긴 문장형 설명에서 짧고 자립적인 표현으로 바꾸고, 관계가 많은 아이템은 역할과 조건이 같은 관계를 묶어 빠르게 훑을 수 있게 한다.

이번 변경은 다음 결과를 동시에 달성해야 한다.

- 저밀도 화면: 각 행만 읽어도 대상·역할·조건을 이해할 수 있다.
- 고밀도 화면: 역할·조건별 제목 아래 대상만 나열하여 반복 문구를 제거한다.
- 검색 화면: 실제로 일치한 exact relation만 같은 규칙으로 다시 구성한다.
- KO/EN 전환, 줄바꿈, 펼침 상태, 아이템 전환에서도 의미와 상태가 섞이지 않는다.
- fixed Recipe, Right-click, Tooltip, recipe navigation은 현재 동작을 유지한다.
- 기존 EvolvedRecipe producer와 candidate/adoption 경로를 확장하고 별도 권위 체계나 새 CLI를 만들지 않는다.

## 2. Scope

### In Scope

- 38개 EvolvedRecipe target의 KO/EN 표시명 확정
- `role × condition` 5종 action phrase 확정
- relation별 구조화된 presentation field 생성
- 저밀도 flat row와 고밀도 grouped row 투영
- 고밀도 검색 결과의 matched-only 재그룹화
- canonical ordinal 및 exact relation identity 보존
- 현재 EvolvedRecipe candidate/package/adoption 흐름을 통한 실제 PZ 검증과 채택
- 변경 범위에 직접 대응하는 기존 producer test와 Lua harness 보강

### Explicitly Out of Scope

- 새 `domains/menu` producer 또는 별도 Menu CLI
- 별도 presentation authority JSON
- source-closure/custody/finalizer 프레임워크
- fixed Recipe, Right-click, Tooltip 의미·데이터·밀도 정책 변경
- EvolvedRecipe 행의 클릭 또는 recipe navigation 추가
- 게임의 조리 가능성 판정 로직 변경
- 전 아이템·전 해상도·전 언어의 수동 전수 검사
- 이번 변경과 무관한 기존 테스트 실패 수정

## 3. Non-Goals

- 관계 수를 줄이거나 합성 관계를 만드는 것
- 서로 다른 target을 하나의 일반명으로 뭉개는 것
- `base_item`, `ingredient`, `spice`, `cooked` 의미를 추론으로 재분류하는 것
- dense 화면에서도 기존 flat traversal 순서를 그대로 보이게 하는 것
- 이번 표현 변경을 계기로 새 범용 UI 아키텍처를 도입하는 것
- 문구 선호도를 별도 사람 검토 Gate로 운영하는 것

## 4. Assumptions and Locked Contract

### 4.1 Verified Baseline

현재 owner 기준선은 다음과 같다.

- relation: 2,203
- source FullType: 252
- role: `base_item` 38, `ingredient` 1,553, `spice` 612
- cooked condition: ingredient 132, spice 7
- density: single 29, small 108, dense 115
- item별 최대 relation: 21
- dense item의 `role × condition` 그룹 수: 92개는 1그룹, 23개는 2그룹

현재 채택 runtime SHA-256은 `0b86cb8a2638df627f94bbb27af759b9b46e54c55081504da04aefcc8e353088`이다. 구현 시작 시 이 값과 실제 repository runtime이 다르면 기준선이 이동한 것이므로 Gate 1을 다시 기록한다.

### 4.2 Density Boundary

현재 정책을 유지한다.

- single: relation 1개
- small: relation 2~8개
- dense: relation 9개 이상

single과 small은 같은 compact flat row 문법을 사용한다. dense만 group heading과 target child로 표시한다.

### 4.3 Canonical Order

`canonical order 보존`은 모든 화면에서 동일한 flat 순서를 강제한다는 뜻이 아니다.

- 각 relation의 `canonical_ordinal` 값은 생성 전후 동일해야 한다.
- single/small flat row는 `canonical_ordinal` 오름차순이다.
- dense 화면은 flat traversal을 의도적으로 대체한다.
- dense group 순서는 각 그룹에 속한 첫 relation의 `canonical_ordinal` 오름차순이다.
- 한 group 안의 child 순서는 relation의 `canonical_ordinal` 오름차순이다.
- 따라서 dense 화면의 전체 child flat 순서는 기존 전체 flat 순서와 달라질 수 있다.
- 검증은 dense 전체 flat parity가 아니라 ordinal 값, group 순서, group 내부 child 순서를 확인한다.

이 계약은 실제 기준선에서 역할·조건 그룹이 서로 끼어 있는 dense item 23개와 모순되지 않는다.

### 4.4 Exact Relation Identity

표현이 묶여도 relation 자체는 합치지 않는다. 각 child는 최소한 다음 의미를 계속 가리켜야 한다.

- stable relation identity
- source FullType
- evolved target ID
- role
- condition
- canonical ordinal
- KO/EN target label

동일한 표시명이 존재하더라도 target ID 또는 relation identity가 다르면 별도 child로 남긴다. heading의 수는 표시명 종류 수가 아니라 포함된 exact relation 수다.

### 4.5 Compact Grammar

#### Action phrase matrix

| Role | Condition | KO | EN |
|---|---|---|---|
| `ingredient` | none | 재료로 추가 가능 | Can be added as an ingredient |
| `ingredient` | cooked | 익힌 뒤 재료로 추가 가능 | Can be added as an ingredient after cooking |
| `spice` | none | 양념으로 추가 가능 | Can be added as seasoning |
| `spice` | cooked | 익힌 뒤 양념으로 추가 가능 | Can be added as seasoning after cooking |
| `base_item` | none | 조리 시작에 사용 | Used to start preparation |

지원되지 않는 role/condition 조합은 임의 문구로 fallback하지 않고 producer validation을 실패시킨다.

#### Low-density row

- KO/EN 공통 구조: `{target label} · {action phrase}`
- 예: `버거 · 재료로 추가 가능`
- 예: `Burger · Can be added as an ingredient`

#### Dense group

- heading: `{action phrase} ({exact relation count})`
- child: `{target label}`
- heading과 child를 함께 읽으면 low-density row와 같은 의미가 복원되어야 한다.
- child만 tooltip 또는 보조기술에 노출될 가능성이 있으면 접근성용 full text는 `{target label} · {action phrase}`로 유지한다.

### 4.6 Target Label Matrix

아래 38개 target label이 이번 구현의 최종 문구다. 구현 세션에서 문구를 다시 설계하지 않는다.

| # | Target ID | KO | EN |
|---:|---|---|---|
| 1 | `Beer` | 텀블러에 담긴 맥주 | Beer in a tumbler |
| 2 | `Beer2` | 컵에 담긴 맥주 | Beer in a cup |
| 3 | `Beverage` | 텀블러에 담긴 음료 | Beverage in a tumbler |
| 4 | `Beverage2` | 컵에 담긴 음료 | Beverage in a cup |
| 5 | `Bread` | 빵 | Bread |
| 6 | `Burger` | 버거 | Burger |
| 7 | `Burrito` | 부리토 | Burrito |
| 8 | `Cake` | 케이크 | Cake |
| 9 | `ConeIcecream` | 아이스크림 콘 | Ice cream cone |
| 10 | `FruitSalad` | 과일 샐러드 | Fruit salad |
| 11 | `HotDrink` | 머그잔에 담긴 음료 | Drink in a mug |
| 12 | `HotDrinkRed` | 빨간 머그잔에 담긴 음료 | Drink in a red mug |
| 13 | `HotDrinkSpiffo` | 스피포 머그잔에 담긴 음료 | Drink in a Spiffo mug |
| 14 | `HotDrinkTea` | 찻잔에 담긴 음료 | Drink in a teacup |
| 15 | `HotDrinkWhite` | 하얀 머그잔에 담긴 음료 | Drink in a white mug |
| 16 | `Muffin` | 머핀 | Muffins |
| 17 | `Oatmeal` | 오트밀 한 그릇 | Bowl of oatmeal |
| 18 | `Omelette` | 오믈렛 | Omelette |
| 19 | `Pancakes` | 팬케이크 | Pancakes |
| 20 | `PastaPan` | 소스팬에 담긴 파스타 | Pasta in a saucepan |
| 21 | `PastaPot` | 냄비에 담긴 파스타 | Pasta in a cooking pot |
| 22 | `Pie` | 세이보리 파이 | Savory pie |
| 23 | `PieSweet` | 달콤한 파이 | Sweet pie |
| 24 | `Pizza` | 피자 | Pizza |
| 25 | `RicePan` | 소스팬에 담긴 밥 | Rice in a saucepan |
| 26 | `RicePot` | 냄비에 담긴 밥 | Rice in a cooking pot |
| 27 | `Roasted Vegetables` | 구운 채소 | Roasted vegetables |
| 28 | `Salad` | 샐러드 | Salad |
| 29 | `Sandwich` | 식빵 샌드위치 | Sandwich |
| 30 | `Sandwich Baguette` | 바게트 샌드위치 | Baguette sandwich |
| 31 | `Soup` | 수프 | Soup |
| 32 | `Stew` | 스튜 | Stew |
| 33 | `Stir fry` | 프라이팬 볶음 | Stir-fry in a frying pan |
| 34 | `Stir fry Griddle Pan` | 그리들 팬 볶음 | Stir-fry on a griddle pan |
| 35 | `Taco` | 타코 | Taco |
| 36 | `Toast` | 토스트 | Toast |
| 37 | `Waffles` | 와플 | Waffles |
| 38 | `WineInGlass` | 와인잔에 담긴 와인 | Wine in a glass |

### 4.7 Search Contract

- 검색은 source item의 relation set에서 현재와 같은 검색 정규화 규칙으로 exact relation을 거른다.
- single/small item은 일치한 relation만 compact flat row로 표시한다.
- dense item은 일치한 relation만 `role × condition`으로 다시 묶는다.
- dense 검색은 일치 relation이 1개여도 heading과 child를 모두 표시한다. 검색 중만 문법이 flat으로 바뀌지 않는다.
- heading count는 전체 group 수가 아니라 현재 검색에 일치한 exact relation 수다.
- 빈 group은 만들지 않는다.
- 검색 해제 시 원래 item의 전체 projection으로 돌아간다.
- source item 전환, locale 전환, collapse/expand 후 이전 item의 relation 또는 query 결과가 남지 않는다.

## 5. Repository Areas Affected

### Existing Producer and Generated Data

- `Iris/tooling/src/iris_tooling/domains/layer4/evolved_recipe.py`
- `Iris/tooling/tests/test_evolved_recipe.py`
- `Iris/build/description/v2/data/evolved_recipe_owner.b41.json`
- `Iris/media/lua/client/Iris/Data/IrisEvolvedRecipeLookup.lua`

`evolved_recipe.py`가 현재 source parsing, owner generation, validation, candidate, package, adoption을 이미 소유하므로 이 경로를 확장한다.

### Existing Menu Projection and Rendering

- EvolvedRecipe relation을 Iris Menu model로 조립하는 기존 assembler/projection
- EvolvedRecipe section을 그리는 기존 renderer
- 필요한 경우에만 EvolvedRecipe 전용 state shape
- 기존 density policy 상수

정확한 파일은 구현 시작 시 `IrisEvolvedRecipeLookup` 소비 지점을 역추적해 확정한다. 독립된 새 subsystem은 만들지 않는다.

### Existing Validation

- `Iris/test/test_adaptive_interaction_presentation.py`
- 이 테스트가 호출하는 기존 Lua 집중 harness
- `tools/check_lua_syntax.ps1`

### Closeout Documentation

- `docs/evolved_recipe_candidate_closeout.md`
- 실제 채택 후 현재 상태가 바뀌는 경우에만 `DECISIONS.md`, `ARCHITECTURE.md`, `ROADMAP.md`

## 6. Planned Changes

### Change 1 — Baseline and Presentation Contract Seal

구현 직전에 현재 owner/runtime/code 소비 경로를 읽고 다음만 기록한다.

1. repository HEAD와 dirty 상태
2. owner relation census
3. 채택 runtime SHA-256
4. EvolvedRecipe lookup 소비 파일
5. 현재 density threshold와 검색 정규화 함수

기준선이 이 문서의 4.1과 다르면 의미 변경 여부를 판단한다. 숫자나 경로만 이동했고 계약이 같으면 계획의 기준선 기록을 갱신한다. relation 의미나 UI 소유권이 바뀌었으면 구현 전에 이 계획을 수정한다.

Gate를 늘리지 않기 위해 별도 baseline manifest는 만들지 않는다. 구현 commit/closeout에 위 값만 남긴다.

### Change 2 — Extend the Existing Producer

`evolved_recipe.py`의 기존 relation에 표시용 원자를 추가하거나, 이미 있는 필드를 명시적으로 소비 가능하게 만든다.

최소 출력 계약:

- `relation_id`
- `source_full_type`
- `target_id`
- `role`
- `condition`
- `canonical_ordinal`
- `target_label.ko`
- `target_label.en`
- 필요하면 `action_key`

producer는 다음을 fail-closed 검증한다.

- 38개 target label 완전성 및 미등록 target 거부
- 허용된 5개 role/condition 조합만 존재
- relation identity와 canonical ordinal의 유일성
- 기존 relation census 및 source accounting 보존
- KO/EN 모두 빈 문자열 없음
- candidate A/B deterministic byte parity

compact flat text와 dense heading은 Lua에서 조합해도 되고 producer가 미리 생성해도 된다. 다만 같은 phrase matrix를 두 곳에 복제하지 않는다. 기존 구조와 테스트 비용을 비교하여 한 곳만 authoritative formatter로 선택한다.

새 schema version은 payload shape가 실제로 바뀔 때만 올린다. target label의 값만 바뀌고 기존 필드로 충분하면 불필요한 schema bump를 하지 않는다.

### Change 3 — Compact and Grouped Menu Projection

기존 EvolvedRecipe projection/renderer를 다음처럼 변경한다.

#### Single/Small

1. relation을 canonical ordinal로 정렬한다.
2. locale에 맞는 target label과 action phrase를 결합한다.
3. `{target} · {action}` 한 행을 non-clickable row로 표시한다.

#### Dense

1. relation을 `(role, condition)`으로 묶는다.
2. 각 group의 첫 canonical ordinal로 group을 정렬한다.
3. 각 group 내부 relation을 canonical ordinal로 정렬한다.
4. `{action} (N)` heading을 표시한다.
5. 그 아래 target label child를 non-clickable row로 표시한다.

#### Dense Search

1. relation 단위로 query를 적용한다.
2. matched relation만 같은 dense 규칙으로 재그룹화한다.
3. matched count를 heading에 표시한다.
4. match가 없는 group은 생략한다.

기존 EvolvedRecipe 전용 expanded/query state를 재사용한다. 새 state가 필요하면 item identity와 locale에 결속된 최소 필드만 추가한다. fixed Recipe state, density, visible rows, navigation에는 EvolvedRecipe group 수를 섞지 않는다.

줄바꿈은 text를 자르지 않고 기존 width 기반 wrapping을 사용한다. 내부 target ID, role key, condition key는 사용자에게 노출하지 않는다.

### Change 4 — Candidate, Actual PZ Observation, and Adoption

기존 CLI로 owner/candidate A·B를 생성하고 각 candidate를 검증한다. A·B runtime byte가 동일한 후보 하나만 별도 package 경로에 stage한다.

현재 설치본을 자동으로 덮어쓰지 않는다. candidate package를 실제 PZ에서 관찰한 뒤 관찰한 runtime SHA-256을 기존 guarded adoption 명령에 전달한다.

대표 관찰은 다음 사례로 제한한다.

- `Base.Allsorts`: single/low-density 자립 행
- `Base.Salt`: dense 1그룹, target 구분, fixed Recipe 보존
- `farming.Bacon`: ingredient와 cooked ingredient 그룹 분리
- `farming.BaconBits`: cooked spice 문구
- `Base.Bowl` 또는 `Base.WaterPot`: `base_item` 문구

같은 사례를 재사용해 다음을 spot-check한다.

- 검색 matched-only group/count
- KO/EN 전환
- item 전환 후 query/relation 격리
- collapse/expand
- 줄바꿈과 tooltip 무회귀
- fixed Recipe 이름·navigation·density 보존

관찰이 실패하면 candidate를 채택하지 않고 원인을 source 또는 projection에서 수정한 뒤 Gate 2부터 다시 수행한다.

채택 후 closeout에는 최종 owner/runtime/candidate/package SHA-256, 자동 검증 결과, 관찰한 대표 사례, 알려진 한계를 기록한다.

## 7. Validation Plan

검증은 세 Gate만 사용한다. 개별 명령이나 사례를 별도 Gate로 승격하지 않는다.

### Gate 1 — Contract and Baseline

통과 조건:

- 4.5의 5개 action phrase와 4.6의 38개 target label이 구현 입력으로 고정됨
- current owner census와 runtime hash를 읽어 기록함
- 실제 lookup 소비 경로와 기존 density/search/state 소유자를 확인함
- fixed Recipe, Right-click, Tooltip 비변경 경계를 확인함

이 Gate는 문서/코드 readback이며 별도 테스트 프로그램이나 승인자를 요구하지 않는다.

### Gate 2 — Candidate Integrity

한 번의 focused Python invocation으로 producer 계약과 핵심 Lua interaction harness를 실행한다.

```powershell
$env:IRIS_CLEAN_CHECKOUT_LEGACY_OUTPUT_ROOT = (Resolve-Path '.\Iris\build\baseline\current_output_seed_v1').Path
$testExit = 0
try {
  uv run --project .\Iris\tooling --no-sync python -m pytest `
    .\Iris\tooling\tests\test_evolved_recipe.py `
    .\Iris\test\test_adaptive_interaction_presentation.py::test_standalone_projection_and_state_harness
  $testExit = $LASTEXITCODE
} finally {
  Remove-Item Env:IRIS_CLEAN_CHECKOUT_LEGACY_OUTPUT_ROOT -ErrorAction SilentlyContinue
}
if ($testExit -ne 0) { throw "Focused tests failed with exit code $testExit" }
```

Lua 변경 파일 전체의 parse 가능성은 기존 단일 명령으로 확인한다.

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\check_lua_syntax.ps1
```

같은 Gate 안에서 기존 CLI로 candidate A·B를 생성·검증하고 다음만 비교한다.

- A/B runtime bytes 동일
- A/B manifest의 owner hash와 relation census 동일
- package runtime bytes가 검증한 candidate와 동일

새 테스트 파일이나 테스트 함수를 만들지 않는다. 기존 producer 테스트 4개와 기존 Lua 통합 harness 1개만 사용하고, 필요한 assertion을 가장 가까운 기존 테스트에 합친다.

- producer 테스트 4개: 38 labels, 5 action combinations, source accounting/census, identity/ordinal, candidate determinism
- Lua 통합 harness 1개: low-density grammar, dense group/order/count, dense search, state/locale 전환, fixed 영역 무회귀

PASS는 위 5개 focused test, Lua syntax, A/B candidate validation이 모두 exit `0`일 때만 선언한다. 별도 collector/locale wrapper와 관련 없는 전체 `test_adaptive_interaction_presentation.py`의 기존 실패는 이 Gate에 포함하지 않는다. 필요한 collector/locale 회귀는 단일 Lua harness의 assertion으로 흡수한다.

### Gate 3 — Actual PZ Observation and Adoption

Change 4의 대표 사례를 실제 PZ에서 관찰한다. 모두 만족한 candidate만 채택한다.

채택 명령은 기존 guarded adoption을 사용한다.

```powershell
uv run --project .\Iris\tooling --no-sync iris-tooling --repository-root . layer4 evolved-recipe adopt `
  --owner '.\Iris\build\description\v2\data\evolved_recipe_owner.b41.json' `
  --candidate-root '<observed-candidate-root>' `
  --repository-root . `
  --observed-runtime-sha256 '<observed-runtime-sha256>'
```

채택 후 Gate 2의 focused pytest와 Lua syntax 명령만 한 번 재실행한다. candidate A/B 재생성, 새 finalizer, 별도 readability 승인, 전체 repository test는 요구하지 않는다.

Gate 3 PASS 조건:

- 대표 실제 PZ 사례가 계약과 일치
- guarded adoption exit `0`
- adopted runtime bytes가 관찰 candidate와 동일
- 사후 focused pytest exit `0`
- 사후 Lua syntax exit `0`

## 8. Risk Surface

### Authority Surface

낮음~중간. 기존 EvolvedRecipe owner가 그대로 권위 표면이다. 새 authority를 만들지 않으므로 split-brain 위험을 피한다.

### Runtime Behavior Surface

중간. relation 의미는 유지하지만 dense presentation order와 row shape가 바뀐다. 검색과 state 격리가 주된 위험이다.

### Compatibility Surface

중간. Lua payload shape를 바꾸면 기존 consumer와 함께 갱신해야 한다. schema bump는 실제 shape 변경에만 사용한다.

### Public-Facing Output Surface

높음. 38개 target label과 5개 action phrase가 KO/EN 사용자 화면에 직접 노출된다. 문구를 계획에서 미리 고정하여 구현자의 임의 결정을 줄인다.

## 9. Risk Analysis

| Risk | Consequence | Mitigation |
|---|---|---|
| grouping이 relation을 합침 | exact relation 손실, count 오류 | child마다 relation identity 유지, count를 exact relation 기준으로 계산 |
| canonical order를 flat parity로 잘못 구현 | 역할 그룹이 다시 섞이거나 모순 발생 | ordinal 보존과 dense 표시 순서를 분리한 4.3 계약 적용 |
| 검색이 전체 group을 노출 | false-positive 결과와 잘못된 count | relation 먼저 filter, matched-only 재그룹화 |
| Evolved density가 fixed Recipe에 전파 | 기존 이름/navigation이 숨겨짐 | 기존 두 projection의 density/state를 분리 유지 |
| KO/EN phrase drift | 의미 비대칭 | 단일 phrase matrix와 기존 locale completeness test |
| 새 인프라 도입 | 구현·회귀·Gate 증가 | 기존 producer/CLI/harness만 확장 |
| 실제 PZ와 harness 차이 | 자동 PASS 후 UI 실패 | 제한된 대표 실제 관찰을 최종 Gate로 유지 |

## 10. Rollback Plan

### Before Adoption

- 작업은 현재 채택 runtime을 직접 덮어쓰지 않는 branch/worktree와 외부 candidate/package 경로에서 진행한다.
- 실패 candidate는 채택하지 않는다.
- source와 test 변경은 일반 Git 수정으로 고치거나 되돌린다.

### After Adoption

- rollback 대상은 이번 adoption으로 바뀐 runtime 파일 집합으로 제한한다.
- rollback 전 현재 runtime hash가 채택 직후 기록과 같은지 확인한다. 이후 사용자 변경이 있으면 자동 덮어쓰기를 중단한다.
- 검증된 직전 runtime을 복원한 뒤 focused pytest와 Lua syntax를 실행한다.
- source, tests, docs, tooling 전체를 byte rollback하는 별도 시스템은 만들지 않는다.
- `git reset --hard` 같은 광범위한 파괴 명령을 사용하지 않는다. source 수정은 정상적인 corrective commit으로 남긴다.

## 11. Governance Constraints

- `Philosophy.md`의 truthful provenance, fail-closed validation, derived artifact 원칙을 유지한다.
- Build 41 source fact와 Iris가 만든 presentation label을 구분한다.
- existing EvolvedRecipe owner/producer/candidate/adoption이 단일 소유 경로다.
- 같은 문구 또는 grouping 규칙을 Python과 Lua에 독립적으로 중복 정의하지 않는다.
- runtime candidate는 관찰·hash 결속 전 repository current에 채택하지 않는다.
- 고밀도 그룹화는 presentation 변화이며 canonical relation 의미 변화로 기록하지 않는다.
- fixed Recipe, Right-click, Tooltip payload 변화가 감지되면 범위 밖 변경으로 실패 처리한다.
- 구현 편의를 이유로 새 authority JSON, 새 Menu CLI, custody manifest, readability reviewer Gate를 추가하지 않는다.
- 추가 테스트나 Gate는 기존 세 Gate로 잡을 수 없는 구체적 고위험 실패가 발견될 때만 허용한다. 추가 시 그 실패와 기존 검증으로 불충분한 이유를 closeout에 적는다.

## 12. Expected Closeout State

완료 시 다음 상태여야 한다.

- 저밀도 EvolvedRecipe가 `{target} · {action}` 형태로 짧고 자립적이다.
- 고밀도 EvolvedRecipe가 `role × condition` heading과 target child로 표시된다.
- dense search가 matched-only relation을 같은 문법으로 재그룹화한다.
- relation identity, census, role, condition, canonical ordinal이 보존된다.
- group 및 child order가 4.3 계약과 일치한다.
- 38개 target label과 5개 action phrase가 KO/EN에서 완전하다.
- fixed Recipe, Right-click, Tooltip, navigation에 회귀가 없다.
- focused 자동 검증, Lua syntax, 실제 PZ 대표 관찰, guarded adoption이 모두 PASS다.
- 최종 owner/runtime/candidate/package hash와 관찰 범위가 closeout에 남는다.

다음 주장은 하지 않는다.

- 모든 아이템·검색어·해상도·게임 상태를 수동 전수 검증했다.
- grouped child의 전체 flat 순서가 과거 flat traversal과 같다.
- EvolvedRecipe 행이 fixed recipe navigation을 제공한다.
- 이번 변경이 게임의 조리 판정 자체를 바꾼다.
