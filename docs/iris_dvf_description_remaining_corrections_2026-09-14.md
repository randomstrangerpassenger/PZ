# 전체 평가 후 남은 문장 교정

2026-09-14. 사용자 요청에 따라 표백제와 수박을 제외하고 확인된 문장 문제를 교정했다. 기존 평가에서 두 항목의 설명 추가를 필수 수정으로 분류한 판단은 철회했다. 용도 설명은 모든 효과나 제작법을 반복하는 영역이 아니다.

## 결과

59개 항목, 117개 언어·길이 좌표의 문장이 변경되었다. KO Compact 10 / KO Expanded 1 / EN Compact 58 / EN Expanded 48이다. 공통 문형을 사용하므로 통조림·낚시 도구에 같은 교정이 적용된다.

| 대상 | 교정 |
|---|---|
| 부목 | KO Expanded에 기존 EN과 같은 머리·몸통 제외 범위를 반영 |
| 차량 배터리 충전기 | EN 양쪽 길이에 기존 KO와 같은 전력 공급 조건 반영 |
| 통나무 | Compact를 건축·야영·숯 제작 재료와 연료로 요약. 묶기·수박 쪼개기는 기존 Expanded에 보존 |
| 못 | Compact를 목공·건축·사냥과 낚시 장비 제작·무기 수리 재료로 묶음. 포장·로프 고정은 Expanded에 보존 |
| 물과 연료를 담는 빈 병 | 받기·운반·옮기기를 하나의 용도로 묶음. 화염 장치 재료와 병 깨기는 별도 용도로 유지 |
| 후드 의류 | 착용과 후드 조절을 묶고, 천 회수·시트 로프 제작의 문장을 연결. Expanded의 각 행동은 유지 |
| 통조림류 영어 | 두 번째 문장에서 표시명을 기계적으로 반복하는 `The extracted …` 대신 `Its contents …` 사용. 첫 문장의 내용물 식별은 유지하며 참치의 소비 문장에는 `tuna` 사용 |
| 딸기 씨앗 영어 | 문장 안의 `Strawberries Seeds`를 `Strawberry Seeds`로 교정. 원본 식별자는 유지 |
| 낚시 영어 | `fishing at water`를 물가에서 낚시하는 자연스러운 문형으로 변경. 미끼 조건 유지 |

대표 Compact:

- 통나무: “건축, 야영 준비와 숯 제작에 재료로 쓸 수 있다. 모닥불 등의 연료로 쓸 수 있다.”
- 못: “목공과 건축, 사냥과 낚시 장비 제작 및 무기 수리에 재료로 쓸 수 있다.”
- 빈 술병: “물이나 연료를 담아 운반하고 옮기는 데 쓸 수 있다. 화염 장치를 만들 때 재료로 쓸 수 있다. 깨뜨려 깨진 병을 얻을 수 있다.”
- 후드 의류: “후드를 조절해 착용할 수 있다. 천 조각을 얻거나 시트 로프를 만드는 데 쓸 수 있다. 연료나 불쏘시개로도 쓸 수 있다.”

Compact의 추가 요약이 Expanded의 기존 순서를 바꾸지 않도록 요약 이전의 용도 순서를 유지했다. 표백제 `Base.Bleach`와 수박 `Base.Watermelon`은 전체 항목 레코드가 교정 전과 동일하다. 빈 표백제병 `Base.BleachEmpty`는 빈 용기의 공통 요약 교정에 포함된다.

## 검증

- 최종 전체 재생성: `uv run --project .\Iris\tooling python .tmp/prose/depth_regenerate.py` — exit 0.
- 조합·설명 계약 검사: 아래 명령 exit 0, **2 passed in 30.47s**.

```powershell
uv run --project .\Iris\tooling python -I -B -m pytest --noconftest -c .\Iris\tooling\pyproject.toml .\Iris\build\description\v2\tests\test_layer3_composition.py::test_layer3_composition_contract .\Iris\build\description\v2\tests\test_layer3_description_composition.py::test_layer3_description_composition --basetemp .\.tmp\remainder-pytest-03 -q -s --tb=short
```

- 전후 보존 검사: `uv run --project .\Iris\tooling python .tmp/prose/remainder-audit.py` — exit 0. 2,105개 ID, 모든 설명 상태, 제외 항목, 모든 Expanded fact ref와 대상 그룹 보존.
- 두 HTML 검토 문서를 최신 생성물로 갱신한 뒤 `uv run --project .\Iris\tooling python .tmp/prose/review-five-audit.py` — exit 0. 전체 원문 8,420개 좌표, 886개 대상 식별자, 접힘 136 / 직접 노출 12 보존 확인.
- 변경된 문구를 읽고 용도·언어별 조건을 대조했다. 변경 전후 전문은 `iris_dvf_description_remaining_corrections_2026-09-14_changes.json`에 보존했다.
- 변경한 세 Python 생성 규칙 파일에 대한 `git -c core.whitespace=cr-at-eol diff --check` — exit 0.

현재 descriptions SHA256: `f97b7168a0cba8c70b1c02303b4e1cc601855ce52a32ba65030ba56c141ecab1`.
blocks SHA256는 변경 없이 `e290c79b0f6d3b8738df5203926aa249309f8c14eaf6eebbed13e809a40ed455`이다.

실제 게임 폰트의 툴팁 4줄 제한은 검증하지 않았다. Lua 실행 코드 변경과 게임 설치·패키징은 수행하지 않았다. 발전기·무전기·소음 장치 등의 추가 근거 조사 후보는 이번 문장 교정 범위에 포함하지 않았다.
