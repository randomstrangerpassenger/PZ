# 설명 생성 규칙 1차 통합

## 기준과 범위

규칙 수 자체를 최소화하는 것이 목적은 아니다. 바닐라의 특정 아이템을 우회적으로 식별하는 조합 대신, 같은 역할·기능 관계를 가진 새로운 아이템도 처리하는 경로를 사용한다. 모드 아이템 역시 근거가 채택된 이후에 이 공통 표현 경로를 사용할 수 있어야 한다. 이번 검증이 임의 모드의 원본 분석까지 지원한다는 뜻은 아니다.

이번 작업은 세션에서 추가한 목적 요약 14개와 표시명 예외 2개를 검토하고, 그중 재료·액체 용기의 중복과 이름 예외를 통합한 첫 단계다. 세션 전체의 모든 조건문을 정리한 것은 아니다.

## 규칙 증감과 목록

목적 요약 **14 → 10**: 기존 후처리 6개 제거, 공통 처리 2개 추가. 기존 재료 역할 조합 경로는 재사용하며 별도의 신설 규칙으로 세지 않는다. 표시명 예외 **2 → 0**. 이 숫자는 아래 의미 단위의 목록이며 Python if 수나 모든 설명 규칙의 총수가 아니다.

| 기존 규칙 | 처리 |
|---|---|
| 물·연료 용기의 특정 기능 조합 | 제거. 액체별로 확인된 기능을 조합하는 공통 처리로 대체 |
| 통나무의 건축·숯·묶기 조합 | 제거. 기존 재료 역할 경로 사용 |
| 못의 건축·수리·포장·로프 조합 | 제거. 기존 재료 역할 경로 사용 |
| 건축과 장비 제작의 조합 | 제거. 기존 재료 역할 경로 사용 |
| 전자 부품의 제작·개조·발전기 수리 조합 | 제거. 기존 재료 역할 경로 사용 |
| 통나무의 건축·야영·숯 제작 조합 | 제거. 기존 재료 역할 경로 사용 |
| 장비 제작 목적의 상위 범주 조합 | 신설. 확인된 장비 제작 용도가 3종 이상이면 상위 범주로 묶음 |
| 연료 공급·점화 연료 조합 | 유지 |
| 무기와 수박 쪼개기 요약 | 유지 |
| 전자 작업·목공·정비 도구 조합 | 유지 |
| 용접·건축·해체 도구 조합 | 유지 |
| 단조·목공·건축 도구 조합 | 유지 |
| 땅 파기·정리·포대 담기 조합 | 유지 |
| 음식·목재 손질·장비 제작 도구 조합 | 유지 |
| 후드 의류의 착용·재료 활용 조합 | 유지 |

유지 항목, 특히 작업 도구의 여러 분야 조합은 다음 통합 검토 대상이다. 이번에 단지 테이블로 옮겨놓고 통합했다고 세지 않았다.

## 구현

`description_composition_results.py`에서 `_compact_storage_materials`의 특정 조합 분기와 중복 재료 후처리를 제거했다. `_compact_liquid_containers`는 기능을 액체별 보관·담기·운반·공급으로 분류한다. 물 보관 기능이 있다는 이유로 연료 보관 기능까지 주장하지 않는다. 액체마다 기능 집합이 같을 때만 이름을 함께 묶는다. 알 수 없는 기능, 다른 용도와 섞인 segment, 공개 조건이 있는 segment는 기존 설명으로 남긴다.

`description_composition_uses.py`의 기존 `material_frames`가 모은 역할·제작 목적을 그대로 사용한다. 공통 문법으로 재료 역할을 한 번 표현하며, 아이템 ID나 특정 바닐라의 전체 기능 목록을 요구하지 않는다. 장비 제작 목적 3종 이상은 source activity가 장비 범주에 속할 때만 ‘장비 제작’으로 묶는다. 숯·부목 등 별도 범주와 모르는 결과를 임의로 장비로 취급하지 않는다. 구체적인 제작 분야는 Expanded에 유지한다.

영어 표시명 예외 `Tin of Tuna → tuna`, `Strawberries Seeds → Strawberry Seeds`를 제거했다. 개봉 결과 이름을 목적어의 수식어로 가공하지 않고 다음 공통 문형에 그대로 넣는다.

- 식품: `It can be opened … to obtain [result name] for eating/drinking/consumption.`
- 씨앗: `It can be opened to obtain [result name] for sowing in a planting bed.`

원본 표시명을 바꾸지 않으며, 새로운 결과 이름을 가진 모드 아이템에도 동일한 문형을 적용할 수 있다.

## 문면 영향

직전 descriptions `f97b7168a0cba8c70b1c02303b4e1cc601855ce52a32ba65030ba56c141ecab1` 대비 **56개 항목, 108개 좌표**가 변경됐다: KO Compact 20, EN Compact 52, EN Expanded 36. KO Expanded 전체는 변경되지 않았다. EN Expanded 변경은 공통 개봉 결과 문형이다.

통나무·못 전용 요약을 제거하면서 묶기·수박 쪼개기·포장·로프 고정 등 일부 문장이 Compact에 다시 나타난다. 이는 특정 조합에 한정된 생략을 제거한 결과이며, 모든 Compact가 직전보다 짧아졌다고 주장하지 않는다. 이 깊이 문제를 다시 다듬을 때에도 항목별 예외를 복구하지 않고 역할·활용 관계 기준으로 처리해야 한다.

표백제 `Base.Bleach`와 수박 `Base.Watermelon`은 전체 항목 레코드가 동일하다. 모든 항목의 상태, Expanded 근거 참조와 대상 목록은 보존했다. 기존 부목·충전기의 언어별 조건 교정도 유지했다.

변경 전후 전문: `iris_dvf_rule_consolidation_2026-09-14_changes.json`.
최신 전문과 검토 HTML: `iris_dvf_descriptions.html`, `iris_dvf_description_review.html`.

## 검증

가상 모드 항목 검사 `test_layer3_rule_generalization.py`:

- 아이템 이름을 바꿔도 설명 동일.
- 바닐라의 전체 기능 조합 없이 물 보관·운반만 있는 용기 처리.
- 연료 이동 기능을 추가해도 물의 보관·운반 능력을 연료에 전이하지 않음.
- 알 수 없는 기능과 공개 조건은 기존 segment 보존.
- 건축+야영, 건축+낚시, 전자 기기+야영, 전자 기기+야영+사냥 재료 조합을 처리하고 모든 역할·용도 참조 보존.

최종 검사 명령 exit 0, **4 passed in 32.31s**:

```powershell
uv run --project .\Iris\tooling python -I -B -m pytest --noconftest -c .\Iris\tooling\pyproject.toml .\Iris\build\description\v2\tests\test_layer3_rule_generalization.py .\Iris\build\description\v2\tests\test_layer3_composition.py::test_layer3_composition_contract .\Iris\build\description\v2\tests\test_layer3_description_composition.py::test_layer3_description_composition --basetemp .\.tmp\consolidate-pytest-04 -q -s --tb=short
```

전체 재생성 `uv run --project .\Iris\tooling python .tmp/prose/depth_regenerate.py` exit 0. 검사와 재생성은 동일 출력 파일을 기록하므로 최종 검증은 순차 실행했다.

전후 보존 검사 `uv run --project .\Iris\tooling python .tmp/prose/consolidate-audit.py` exit 0. HTML 갱신 후 `uv run --project .\Iris\tooling python .tmp/prose/review-five-audit.py` exit 0: 원문 좌표·대상 식별자·목록 표현 보존.

현재 descriptions SHA256: `eae7521ff515c6276ae5d97f4a6a008a0fb11bc330cfa72574cfe07dfde053db`.
blocks SHA256: `e290c79b0f6d3b8738df5203926aa249309f8c14eaf6eebbed13e809a40ed455`（불변）.

Lua 실행 코드 변경, 게임 설치·패키징은 없다. 실제 게임 폰트의 4줄 제한과 실제 모드 원본에서의 전체 수집·표현 통합은 이번 검사 범위 밖이다.
