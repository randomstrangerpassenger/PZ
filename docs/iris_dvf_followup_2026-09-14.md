# DVF 추가 교정 및 재검수 결과

2026-09-14. 1차 완료 보고에 대한 재검수 지적 세 범위와 역할만으로 합치는 후처리 문제를 같은 worktree에서 수정했다. 이 문서가 최신 교정 결과다. 원본 디렉터리 수정, 배포, 정규화 어댑터 추가는 하지 않았다.

## 범위와 최종 산출물

- 추가 교정 기준 descriptions SHA-256: `625020e7e68ed9fcc7cd9c31fab3c529c2b72b53bd7e83a1ddc298b3ec819332`.
- 최종 descriptions SHA-256: `d2bf6b9ebfd12bf54f7b9fd88972d857e59b0823775de19996790588141d136f`.
- blocks SHA-256: `294b16ea0afcdd82652ea19ced1319bda1facd15335f1cf8ac84cccbfec52f3c`. 이미 확보된 근거 관계를 사용하는 이번 교정에서는 blocks 내용이 바뀌지 않았다.
- 추가 교정으로 **213 ID, 444좌표**의 문면이 바뀌었다. 변경된 동일 문면 묶음은 27개다.
- 최초 평가본 `c9e1d15d…`부터의 누적 차이는 **803 ID, 2,315좌표, 변경 문면 188묶음**이다. 총 2,105 ID·8,420좌표, 설명 있음 1,976 ID·absent 129 ID는 유지된다.
- 회수 관련 196 ID, 야영 제작 관련 16 ID, 포장·자루·씨앗 54 ID를 조사했다. 중복을 제외하면 265 ID이며 양 언어·양 깊이의 동일 문면 78묶음이다. 이 78묶음의 KO/EN Compact/Expanded를 읽었고, 회수·야영·포장 교정 재생성 후 변경된 21묶음을 다시 읽었다. 이후 아래 도구 결과 교정 9 ID의 네 문면을 모두 추가로 읽었으며, 6 ID가 기존 조사 범위 밖이므로 최종 검토 범위는 271 ID·84묶음이다. 목록은 모든 해당 ID를 포함하며 대표 아이템만의 점검이 아니다.

[추가 교정 전후 좌표·근거 결과명·전체 조사 목록](iris_dvf_followup_2026-09-14_scopes.json), [추가 조사 범위 전문](iris_dvf_followup_2026-09-14_fulltext.txt), [현재 전체 설명 HTML](iris_dvf_descriptions.html), [최초 평가본과 현재 전후 비교 HTML](iris_dvf_description_review.html).

두 HTML은 최종 descriptions 해시를 표시한다. 전체 8,420좌표와 변경 2,315좌표의 각 문장 및 접힌 대상 목록을 JSON과 대조했다. 누적 비교 자료 `iris_dvf_correction_2026-09-14_scopes.json`과 `_fulltext.txt`도 최종본으로 갱신했다.

## 1. 회수 재료의 정체와 역할별 용도

가죽을 직물로 분류한 것은 교정이 필요한 의미 오류였다. `ClothingRecipesDefinitions.lua`는 Cotton→RippedSheets, Denim→DenimStrips, Leather→LeatherStrips를 선언한다. 현재 source_traits에 있는 실제 fabric_result 관계와 결과 이름을 Compact에서도 사용한다. 원래 의류 ID·표시명이나 FabricType만으로 문구를 정하지 않는다. 소재의 일반 표현은 회수 결과 ID에 연결하고, 알려지지 않은 결과는 그 결과의 이름을 보존한다.

| 대상 | 이전 Compact의 문제 부분 | 최종 Compact의 해당 부분 |
| --- | --- | --- |
| 가죽 장갑·가죽 재킷 등 | 직물 재료로 재활용할 수 있다. / It can be reused as textile material. | 가죽 조각을 회수할 수 있다. / It can provide leather strips. |
| 데님 의류 | 동일한 직물 재료 문형 | 데님 조각을 회수할 수 있다. / It can provide denim strips. |
| 면 의류·시트 | 동일한 직물 재료 문형 | 천 조각을 회수할 수 있다. / It can provide cloth scraps. |
| 가위 | 직물과 머리, 수염을 손질하는 데 쓸 수 있다. | 데님이나 가죽 의류를 잘라 조각을 회수할 수 있다. 머리와 수염을 손질할 수 있다. |

면 의류의 최종 Compact는 “착용할 수 있다. 천 조각을 회수할 수 있다. 연료나 불쏘시개로도 쓸 수 있다.”이다. 독립적인 시트 로프 용도는 Expanded에 “시트 로프를 만들 때 재료로 쓸 수 있다.”로 남는다. 시트에는 이미 모닥불 도구·매트리스 제작을 설명하므로 Compact에 ‘제작 재료’라는 일반어를 덧붙이지 않는다. 가위의 창 부착과 무기 용도, 의류의 착용 위치·후드 조절, Expanded의 필요한 가위와 회수 재료는 보존한다.

`_compact_purposes`의 직물·미용 후처리 두 블록을 제거했다. material/tool이라는 역할만으로 같은 목적이라고 인정하는 경로가 사라졌다. 회수 요약에는 실제 fabric_recovery + material 역할과 fabric_result가 함께 필요하다. 이전 산출물의 placement_reason과 fact_refs를 추적한 실제 적용 범위는 직물 후처리 병합 0 ID, 미용 후처리 병합 Scissors 1 ID였다. 현재 출력에서 임의의 다른 용도가 이미 흡수되었다고 과장하지 않되, 잠재적으로 잘못 합칠 수 있는 조건은 제거했다.

## 2. 야영 제작의 실제 목적

`scripts/camping.txt`의 Make Campfire Kit 두 레시피는 Plank 또는 Log와 RippedSheets/RippedSheetsDirty/Sheet/Book/Magazine/Newspaper/Twigs를 투입해 camping.CampfireKit을 만든다. 결과 표시명은 Campfire Materials이며 KO 번역은 캠프파이어 도구다. Make Tent Kit는 Tarp, TentPeg 또는 Stake, WoodenStick으로 텐트 장비를 만든다. `scripts/recipes.txt`의 Make Mattress는 Needle을 도구로, Thread/Sheet/Pillow를 재료로 사용한다.

이렇게 이미 승인된 활동 관계에 대응하는 공통 목적 명사를 구별했다. 모닥불 도구·매트리스·텐트 제작을 하나의 ‘야영 장비’로 덮지 않는다. 여러 제작 목적이 함께 있으면 해당 목적들을 조합한다. 소모 재료와 도구 역할도 구별한다. 모닥불 제작 사실의 과거 관측에서 숫자 피연산자와 모듈 import가 별도로 보존되어 직접 recipe_targets가 비어 있는 경우에도, 승인된 campfire_kit_preparation 활동과 그 원본 레시피가 목적의 근거다. 수량이나 전체 투입 레시피를 새로 주장하지 않는다.

- Book/Magazine/Twigs: “야영 장비를 만드는 재료” → “모닥불 도구를 만드는 재료로 쓸 수 있다.” / “It can be used as material for making campfire kits.”
- Log Expanded: 같은 모닥불 도구 제작 목적을 밝히며 목공·건축, 숯, 묶기, 수박 손질, 연료를 보존한다.
- Sheet: “모닥불 도구 및 매트리스를 만드는 재료로 쓸 수 있다.” / “It can be used as material for making campfire kits and mattresses.”
- Pillow/Thread: 매트리스 제작을 명시한다. Needle의 매트리스 제작 도구 용도는 Expanded에 남는다.
- Tarp/Stake/TentPeg/WoodenStick: 텐트 제작 목적을 유지한다.

전체 출력에서 ‘야영 장비 / camping equipment’라는 잔존 문형은 없다. 모닥불 도구 제작과 연료·불쏘시개 역할은 별개로 읽힌다. 폭넓은 목공·건축 등의 유효한 상위 목적까지 일괄 금지하지는 않았다.

## 3. 포장 표시명과 내용물 이름

기존 영어 개봉 문제 26 ID를 포함하여 실제 개봉 관계 29 ID, 자루 18 ID, 씨앗 봉투 7 ID까지 총 54 ID의 표시명과 확정 결과명을 대조했다. 모든 자루와 씨앗 봉투는 표시명에 내용물의 정체가 충분히 드러나므로 기존 produce/seeds 문형을 유지한다. 단순 통조림도 일괄 원복하지 않는다.

실제 누락 사례는 Canned Bolognese → Opened Canned Spaghetti Bolognese였다. `scripts/items_food.txt`의 결과 이름을 사용하여 영어를 다음처럼 고쳤다.

> It can be opened with a can opener to eat the spaghetti bolognese inside.

공통 영어 규칙은 포장 표시명에 결과를 식별하는 단어가 모두 들어 있는 경우에만 결과 이름을 생략한다. 포장·개봉 상태어와 단순 단복수 차이만 처리하며, 누락되거나 모호하면 실제 관계의 결과명을 보존한다. 이것은 내용물의 사실을 이름에서 추론하는 기능이 아니라 이미 확정된 결과의 문면 중복 판단이다. 포장 이름을 Unmarked Package로 바꾼 통조림·자루·씨앗 사례에서도 실제 결과명이 남는지 검사했다.

## 4. 제작 목록의 상하위 중복 병렬

모닥불 목적을 구체화한 뒤 “모닥불 도구 및 도구”가 생긴 최종 재검수 지적도 반영했다. `scripts/recipes.txt`의 Make Saw(3045행)는 Plank를 소모 재료로 쓰고 Saw를 결과로 선언한다. Make Stone Axe/Knife/Hammer(1373–1404행)는 천·데님 조각·실끈과 가지·돌을 투입해 각각 AxeStone/FlintKnife/HammerStone을 만든다. 이미 연결된 recipe_targets에서 이 결과 관계를 확인했다.

공통 재료 문형은 모든 해당 용도의 결과가 확인됐을 때, 단일 결과는 그 결과명을 사용하고 돌칼·돌 도끼·돌 망치의 조합은 ‘돌 도구’로 묶는다. 투입 아이템이 돌처럼 보이는지로 분류하지 않는다. 결과가 확인되지 않은 임의 도구 용도를 이 범주로 바꾸지 않는다.

- Plank Expanded: “사냥 장비, 모닥불 도구 및 **톱**을 만드는 재료로 쓸 수 있다.”
- RippedSheets Expanded: “화염 장치, 연막 장치, 모닥불 도구 및 **돌 도구**를 만드는 재료로 쓸 수 있다.”
- RippedSheetsDirty Expanded: “화염 장치, 연막 장치, 모닥불 도구, **돌 도구** 및 부목을 만드는 재료로 쓸 수 있다.”
- 같은 규칙이 적용되는 DenimStrips/Dirty, SharpedStone, TreeBranch, Twine도 돌 도구를 명시한다. Stone의 단일 결과는 돌 망치로 명시한다.

직전 `f4481254…` 산출물 대비 마지막 수정은 **9 ID·24좌표·9문면 묶음**이다. 이 9 ID의 KO/EN Compact/Expanded를 전부 읽어 제작·처치·수선·불 피우기 등의 다른 용도가 유지됨을 확인했다. ‘기타 도구’로 대체하거나 실제 용도를 삭제하지 않았다. [마지막 추가 diff와 네 문면 전후 전문](iris_dvf_tool_refinement_2026-09-14.json)에 별도 기록했다.

## 검증과 한계

다음 명령은 최종 코드에서 모두 종료 코드 **0**이다. 회귀 테스트 통과와 위의 실제 문면 재검토는 별도로 수행했다.

```powershell
uv run --project ./Iris/tooling python -I -B -m pytest --noconftest -c ./Iris/tooling/pyproject.toml ./Iris/build/description/v2/tests/test_layer3_composition.py::test_layer3_composition_contract ./Iris/build/description/v2/tests/test_layer3_description_composition.py::test_layer3_description_composition ./Iris/build/description/v2/tests/test_layer3_rule_generalization.py ./Iris/build/description/v2/tests/test_layer3_dvf_purpose_review.py --basetemp ./.tmp/dvf/followup-final3 -q -s --tb=short
# 15 passed in 36.45s; blocks와 descriptions 전체 재생성 포함.

uv run --project ./Iris/tooling python -I -B -m pytest --noconftest -c ./Iris/tooling/pyproject.toml ./Iris/build/description/v2/tests/test_layer3_product_integration.py::test_current_menu_input_binding -q --tb=short
# 1 passed in 2.27s; 최종 descriptions 해시 바인딩 갱신 후 실행.

powershell -ExecutionPolicy Bypass -File .\tools\check_lua_syntax.ps1
# Lua syntax validation OK: 266 files

git -c core.safecrlf=false -c core.whitespace=cr-at-eol diff --check -- Iris/tooling/src/iris_tooling/domains/layer3 Iris/build/description/v2/tests
# exit 0
```

보조 전수 비교·HTML 대조도 exit 0이다. 최종본은 새 absent와 failed가 없고 가운데점이 없으며 최초 평가본의 preserved_fact_refs를 모두 유지한다. Expanded에서 사라진 참조는 내부 용도로 보존되는지 전수 대조했고 설명되지 않은 참조 손실은 없다. 중간 검사에서 이전 ‘야영’ 기대값과 제작 목적 조합의 KO 표현 문제가 드러났으며, 공통 명사구 조합을 바로잡고 기대값을 실제 목적에 맞춘 뒤 위 최종 검사에서 통과했다.

원본 descriptions의 최초 해시가 유지됨을 확인했다. 이번 작업은 현재 worktree의 생성 규칙·composition·메뉴 입력 바인딩·검토 자료까지다. 실제 게임 배포나 폰트·뷰포트에 따른 줄 수 검증은 하지 않았다. 이전 보고서의 B41 정적 근거, 외부 모드 및 실제 실행 검증 경계도 그대로 적용된다.
