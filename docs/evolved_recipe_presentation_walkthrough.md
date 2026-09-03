# Iris EvolvedRecipe Presentation Walkthrough

- 작성일: 2026-09-03 KST
- 구현 계획: [`iris_evolved_recipe_compact_grouped_presentation_successor_plan.md`](./iris_evolved_recipe_compact_grouped_presentation_successor_plan.md)
- 실행 결과: [`evolved_recipe_candidate_closeout.md`](./evolved_recipe_candidate_closeout.md)
- 최종 상태: `v7 observed_pass / adopted / complete`
- 현재 런타임 SHA-256: `02c6d4b97a21285a393b873582dd9fa80bc6b25fa91d09fc7da89e89965ef47b`

## 1. 문서의 역할

이 문서는 이번 세션에서 EvolvedRecipe 데이터를 만들고, Iris 상세 화면에 간결하게 표시하고, 실제 Project Zomboid에서 발견된 문제를 고쳐 최종 채택하기까지의 흐름을 설명한다.

이 문서는 새 validator, validation authority, adoption gate, receipt, manifest가 아니다. 정확한 계약과 판정 근거는 구현 계획, owner, 기존 검사기, closeout 문서 및 `DECISIONS.md`에 있다. 여기서는 그 자료들을 다시 봉인하지 않고 구현자가 현재 구조와 문제 해결 경위를 빠르게 이해할 수 있도록 연결한다.

## 2. 시작점과 목표

직전 v6는 EvolvedRecipe 관계의 의미와 출처를 보존하고 있었지만, 상세 화면에서 같은 행동 문구가 관계마다 반복되어 정보량이 많은 항목을 읽기 어려웠다. 이번 계획의 핵심은 데이터 의미를 줄이는 것이 아니라 같은 관계를 더 간결한 형태로 투영하는 것이었다.

목표는 다음과 같았다.

- 관계가 적을 때는 대상과 행동이 한 줄에서 완결되는 compact row로 표시한다.
- 관계가 많을 때는 같은 행동을 공유하는 관계를 묶고, 대상 이름을 자식 행으로 표시한다.
- 검색 결과는 전체 그룹을 느슨하게 보여 주지 않고 실제로 일치한 관계만 다시 묶는다.
- Recipe 및 Right-click 같은 고정 상호작용 영역의 동작과 상태 소유권은 바꾸지 않는다.
- 내부 FullType이나 구현용 prefix를 사용자에게 노출하지 않는다.
- Build 41 런타임과 실제 한국어·영어 환경에서 같은 의미를 유지한다.

## 3. 데이터 생산과 source accounting

EvolvedRecipe producer는 Build 41 원본에서 공개 가능한 관계를 정확히 계산하고, 각 관계에 표시와 정렬에 필요한 정보를 함께 기록하도록 정리되었다.

최종 데이터의 주요 수치는 다음과 같다.

| 항목 | 최종 값 |
| --- | ---: |
| 공개 EvolvedRecipe 관계 | 2,203 |
| 공개 FullType | 252 |
| definition 기반 base item 발생 수 | 38 |
| definition 기반 base item 고유 수 | 32 |
| 그중 non-Food 발생 수 | 17 |
| 그중 non-Food 고유 수 | 13 |
| REVIEW 잔여 | 0 |
| 비대상 obsolete token | 10 |

공개 역할은 item property의 `ingredient`, `spice`와 definition의 `BaseItem`을 정규화한 `base_item`이다. 관계마다 다음 정보가 런타임까지 유지된다.

- 안정적인 관계 identity와 provenance
- 원본 순서를 보존하는 `canonical_ordinal`
- 한국어·영어 대상 이름인 `target_label_by_locale`
- 역할과 조건을 사람이 읽는 행동으로 바꾼 `action_by_locale`
- 대상과 행동을 결합한 완결형 `display_by_locale`

38개 식품 type에는 독립적으로 읽을 수 있는 대상 이름을 제공했고, 허용된 역할·조건 조합은 5개 행동 문구로 정규화했다. Lua 문자열은 Build 41 인코딩 경계를 안정적으로 통과하도록 UTF-8 바이트를 10진 escape로 직렬화한다.

관련 구현은 다음 파일에 있다.

- `Iris/tooling/src/iris_tooling/domains/layer4/evolved_recipe.py`
- `Iris/build/description/v2/data/evolved_recipe_owner.b41.json`
- `Iris/media/lua/client/Iris/Data/IrisEvolvedRecipeLookup.lua`

## 4. 런타임 데이터 흐름

EvolvedRecipe 표시는 고정 상호작용의 개수나 밀도 상태에 기대지 않는 별도 projection 경로를 사용한다.

```text
Build 41 원본
    -> tooling producer와 source accounting
    -> evolved_recipe_owner.b41.json
    -> candidate IrisEvolvedRecipeLookup.lua
    -> Browser Detail의 item/locale/state 입력
    -> EvolvedRecipe relation 수집
    -> compact 또는 grouped projection
    -> Interaction Renderer
```

고정 Recipe/Right-click 영역과 EvolvedRecipe 영역은 같은 상세 화면에 렌더링되지만, 각자의 relation 집합과 표시 상태를 독립적으로 계산한다. 따라서 한 영역의 밀도나 검색 상태가 다른 영역의 표시 형식을 암묵적으로 바꾸지 않는다.

주요 런타임 파일은 다음과 같다.

- `Iris/media/lua/client/Iris/UI/Browser/IrisBrowserInteractionProjection.lua`
- `Iris/media/lua/client/Iris/UI/Browser/IrisBrowserInteractionRenderer.lua`
- `Iris/media/lua/client/Iris/UI/Browser/IrisBrowserDetail.lua`

## 5. compact와 grouped 표시

### 관계가 적을 때

각 관계는 대상 이름과 행동을 모두 포함한 한 개의 compact row가 된다. 행 하나만 읽어도 무엇을 어떻게 사용할 수 있는지 알 수 있다.

### 관계가 많을 때

projection은 locale별 action key, 즉 역할과 조건에서 파생된 행동을 기준으로 관계를 묶는다.

- 그룹 heading은 행동을 설명한다.
- 그룹의 자식 행은 대상 이름을 표시한다.
- 그룹 순서는 그룹에 속한 첫 관계의 `canonical_ordinal`을 따른다.
- 그룹 내부 대상도 `canonical_ordinal` 순서를 따른다.
- 모든 행은 정보 표시 전용이며 클릭 이동을 만들지 않는다.

긴 문장은 renderer에서 사용 가능한 폭에 맞춰 줄바꿈된다. 이로써 좁은 화면에서도 진단 메시지나 관계 설명의 뒤쪽이 잘려 원인을 읽을 수 없는 문제를 줄였다.

## 6. 자유 조리 검색의 실제 계약

자유 조리 검색은 각 관계의 완결형 display에 대해 대소문자를 무시한 literal substring 검사를 먼저 수행한다. 그 후 일치한 관계만 원래 canonical order를 유지한 채 다시 grouping한다.

이 순서에는 세 가지 효과가 있다.

1. 검색어와 무관한 자식 행이 같은 그룹이라는 이유로 따라오지 않는다.
2. 일치 관계가 없는 빈 그룹은 생성되지 않는다.
3. 결과 수는 그룹 수가 아니라 실제 일치 관계 수를 나타낸다.

자유 조리 검색과 Iris 메인 아이템 검색은 입력 경험의 일부를 공유하지만 같은 검색 엔진은 아니다.

| 구분 | Iris 메인 아이템 검색 | 자유 조리 검색 |
| --- | --- | --- |
| 검색 대상 | Browser item 목록 | 현재 item의 EvolvedRecipe 관계 |
| 매칭 | exact, 공백 축약, substring, FullType tier | display의 대소문자 무시 literal substring |
| 정렬 | relevance와 prefix narrowing 반영 | 기존 canonical/group 순서 유지 |
| 결과 투영 | item 결과 | 일치 relation만 compact/grouped 재구성 |
| 내부 ID 검색 | FullType tier에 사용 | 사용자 표시 문자열만 사용 |
| 공통점 | 지속되는 text entry와 내부 입력 text 사용 | 지속되는 text entry와 내부 입력 text 사용 |

따라서 이번 완료 상태는 자유 조리 검색을 메인 검색의 relevance ranking과 완전히 같게 만든다는 뜻이 아니다. 계획이 요구한 범위는 literal relation filtering, matched-only regrouping 및 안정적인 순서 보존이며, 그 계약이 채택되었다.

## 7. 실제 PZ에서 발견한 문제와 수정

정적 데이터와 harness만으로는 드러나지 않은 문제가 실제 게임에서 순차적으로 확인되었다.

### 7.1 최초 v7 패키지: 상호작용 자료를 사용할 수 없음

최초 패키지는 모든 상호작용 영역에서 다음 fallback을 표시했다.

> 상호작용 자료를 사용할 수 없음; 재구성 시 다시 시도

처음에는 표시 결합에 쓰인 가운데점 문자를 `string.char(194, 183)`로 바꿨지만, 다음 진단 패키지에서도 `missing_evolved_display`가 확인되었다.

근본 원인은 Lua consumer가 producer가 만든 display를 다시 조합한 뒤 바이트 단위로 비교하던 데 있었다. 의미상 같은 문자열이어도 Build 41 경계에서 표현 바이트가 달라질 수 있어, 올바른 producer 결과까지 거부했다.

수정 후 consumer는 owner/producer가 이미 완전성 검증한 `display_by_locale`을 신뢰한다. 런타임에서는 display가 비어 있지 않은지와 action key가 유효한지만 확인한다. producer와 consumer가 서로 다른 인코딩 경계에서 동일 문자열을 재조합해 byte equality를 요구하지 않게 되었다.

### 7.2 수정 패키지: 입력과 locale 문제

표시 자체가 통과한 뒤 실제 관찰에서 세 가지 후속 문제가 발견되었다.

- 자유 조리 검색창에 한국어와 영어 모두 입력되지 않았다.
- 한국어 UI에서도 heading이 `Freeform Cooking`으로 보였다.
- 영어 UI의 Recipe 이동 버튼이 제작 화면은 열지만 검색을 성공시키지 못했다.

이 문제들은 EvolvedRecipe 관계 projection 자체가 아니라 주변 입력·번역·이동 경계에서 발생했다.

## 8. 검색창 입력, 번역, Recipe 이동 수정

### 8.1 검색창과 IME 유지

기존 detail rebuild는 검색 text entry를 제거하고 새로 만들었다. 키보드 focus와 한국어 IME 조합 상태가 그 과정에서 사라져 사용자가 입력할 수 없었다.

수정 후 Browser가 고정 상호작용 검색창과 자유 조리 검색창 객체를 지속적으로 소유한다. detail rebuild는 entry를 폐기하지 않고 위치, 가시성, scroll 좌표만 동기화한다. 프로그램 코드가 text를 설정할 때는 change callback을 잠시 억제하고, 검색에는 화면 표시용 text가 아니라 entry의 내부 text를 읽는다.

이 변경으로 상세 내용이 다시 만들어져도 같은 입력 객체, focus, IME composition이 유지된다.

### 8.2 한국어 heading

번역 원본에는 이미 다음 locale 값이 있었다.

- 한국어: `자유 조리`
- 영어: `Freeform Cooking`

문제는 생성된 런타임 번역 테이블이 오래되어 해당 key를 포함하지 않았다는 점이었다. 기존 translation data pipeline을 다시 실행해 `IrisTranslationData.lua`를 갱신했고, 양 locale에 EvolvedRecipe heading key가 포함되었다.

### 8.3 영어 Recipe 이동

Recipe 이동 코드는 locale과 관계없이 `translated_name`을 우선 사용했다. 그 결과 영어 UI에서도 한국어 번역명이 제작 화면 검색어로 전달되었다.

수정 후 한국어 locale은 번역명을 우선하고, 그 밖의 locale은 원본 이름을 우선한다. 이 선택은 `IrisBrowserRecipeNav.lua`에 있으며 자유 조리 검색 로직과는 별개의 고정 Recipe navigation 수정이다.

## 9. 검증과 실제 관찰

계획이 지정한 focused gate와 Lua syntax 검사는 모든 구현과 수정이 끝난 뒤 실행했다.

| 검증 | 결과 |
| --- | --- |
| EvolvedRecipe tooling tests + standalone projection/state harness | exit `0`, `5 passed` |
| Lua syntax 검사 | exit `0`, `265 files` |
| candidate A/B validate | 각각 exit `0` |
| candidate runtime byte parity | PASS |
| 실제 PZ compact/grouped·검색·locale·이동 관찰 | 사용자 전체 통과 보고 |
| guarded adoption | exit `0`, PASS |
| adoption 후 repository runtime/candidate parity | PASS |

pytest는 `.pytest_cache` 권한 관련 warning 하나를 출력했지만 계획된 테스트 결과에는 영향을 주지 않았고 exit code는 `0`이었다.

실제 관찰은 최초 패키지, 진단 패키지, 수정 패키지를 거치며 이루어졌다. 최종 설치본은 다음 위치에 전달되었다.

- 설치 폴더: `C:/Users/MW/PZ-U/package/playtest/Iris`
- ZIP: `C:/Users/MW/PZ-U/package/playtest/Iris.zip`
- package manifest SHA-256: `cb1e724be73baec0fc1dde29158b611a379c693816d4c5cfa0ebd664fb188889`

이 경로들은 계획에서 명시적으로 허용된 외부 candidate/package 경계다. 저장소의 최종 authority는 외부 패키지가 아니라 채택된 owner와 runtime이다.

## 10. 채택 결과

사용자의 실제 게임 통과 보고 후 v7 candidate를 guarded adoption으로 저장소에 반영했다.

- owner SHA-256: `92a3f8da92462eced1c99aed0c3619a7938d82c0b53f2e3c49ed98483e2008b0`
- candidate manifest SHA-256: `45d983de70d2ee090e21bc0665793ba15e4cd3a3c534603f5f67fccb611f0e49`
- adopted runtime SHA-256: `02c6d4b97a21285a393b873582dd9fa80bc6b25fa91d09fc7da89e89965ef47b`

v7이 현재 `observed_pass / adopted / complete` 상태이며, v6는 의미가 틀린 실패본이 아니라 `observed_pass / superseded_current`인 직전 predecessor로 남는다.

## 11. 변경 파일 지도

| 역할 | 파일 |
| --- | --- |
| source accounting, locale label/action, candidate 생성 | `Iris/tooling/src/iris_tooling/domains/layer4/evolved_recipe.py` |
| producer 계약 회귀 검사 | `Iris/tooling/tests/test_evolved_recipe.py` |
| Build 41 owner | `Iris/build/description/v2/data/evolved_recipe_owner.b41.json` |
| 채택된 EvolvedRecipe runtime data | `Iris/media/lua/client/Iris/Data/IrisEvolvedRecipeLookup.lua` |
| compact/grouped/search projection | `Iris/media/lua/client/Iris/UI/Browser/IrisBrowserInteractionProjection.lua` |
| 그룹·자식·줄바꿈·검색창 렌더링 | `Iris/media/lua/client/Iris/UI/Browser/IrisBrowserInteractionRenderer.lua` |
| persistent search entry와 scroll 동기화 | `Iris/media/lua/client/Iris/UI/Browser/IrisBrowserDetail.lua` |
| locale별 Recipe 이동 검색어 선택 | `Iris/media/lua/client/Iris/UI/Browser/IrisBrowserRecipeNav.lua` |
| 생성된 locale runtime table | `Iris/media/lua/client/Iris/Data/IrisTranslationData.lua` |
| projection/state acceptance harness | `Iris/test/lua/browser_interaction_density_acceptance_harness.lua` |

## 12. 완료 범위와 비목표

이번 계획은 EvolvedRecipe 관계의 compact/grouped presentation, relation 검색, 입력 지속성, locale 표시 및 관찰 중 발견된 Recipe 이동 회귀까지 완료했다.

다음 사항을 새로 주장하지는 않는다.

- EvolvedRecipe 관계가 실제 조리 가능성이나 현재 캐릭터의 조건 충족을 판정한다는 주장
- 자유 조리 검색이 메인 Iris 검색의 전체 ranking·FullType 계약을 공유한다는 주장
- 이번 bounded actual observation이 Iris 전체 release readiness를 증명한다는 주장
- walkthrough 자체가 owner, validator 또는 adoption authority라는 주장

현재 구현과 문서의 최종 상태는 `DECISIONS.md`, `ROADMAP.md`, `ARCHITECTURE.md` 및 closeout에 반영되어 있으며, 계획에 남은 필수 gate는 없다.
