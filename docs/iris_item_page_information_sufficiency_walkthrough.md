# Iris Item-Page Information Sufficiency Walkthrough

> Session date: 2026-08-21 KST
> Status: one-off assessment complete
> Result root: `Iris/build/description/v2/output/item_page_information_sufficiency/`

## 1. What This Work Did

이번 작업은 current vanilla item 2,285개에 대해 Iris item page의 정보 충분성을 한 번 평가했다.

평가는 다음 세 입력을 비교했다.

- ItemScript에 보존된 기본 정보
- current Layer 3 설명 정보
- current Layer 4 제작법·우클릭 상호작용 정보

각 FullType은 다음 네 결과 중 하나로 분류했다.

- `information_sufficient`
- `evidence_limited`
- `known_information_missing`
- `unresolved`

이 작업은 Iris runtime 기능을 추가하거나 item page 표시를 변경하는 작업이 아니다. 현재 데이터 상태를 읽어 결과 보고서를 만든 일회성 분석이다.

## 2. Result

| Disposition | Count |
| --- | ---: |
| `information_sufficient` | 2,081 |
| `evidence_limited` | 180 |
| `known_information_missing` | 2 |
| `unresolved` | 22 |
| Total | 2,285 |

보존한 결과 파일은 다음과 같다.

- `page_assessment.jsonl`: FullType별 전체 평가 결과
- `assessment_summary.json`: 분포와 주요 집계
- `information_gap_inventory.jsonl`: missing·unresolved 항목 목록
- `anchor_assessment.json`: 대표 item의 판정 경로
- `baseline_runtime_drift_report.json`: ItemScript baseline과 runtime 표시 가능 field의 차이
- `terminology_responsibility_mapping.json`: Menu·Tooltip 용어와 실제 정보 책임의 대응

평가 기준 설명은 `docs/iris_item_page_information_sufficiency_policy.md`에 남겼다.

## 3. How It Was Checked

작업 중에는 결과 계산과 비교를 위한 임시 Python 스크립트, fixture와 focused test를 사용했다. 전체 2,285개 row 수와 key set, disposition 합계, known missing·unresolved 분류, 대표 case, Run A/Run B 동일 결과를 확인했다. 기존 current-route 회귀도 당시 작업 상태에서 통과했다.

이 검증 코드는 결과를 확인하기 위한 작업 도구였으며 Iris의 정규 검사기나 유지보수 대상 아키텍처가 아니다. 확인이 끝난 뒤 다음 항목을 제거했다.

- 임시 evaluator, runner와 validator
- 임시 unittest와 fixture
- current-route와 active-core 등록
- current authority 등록
- 기존 회귀 테스트와 residual validator에 추가했던 결속
- canonical subject manifest, reviewer artifact, owner seal과 protected successor
- 봉인 전용 `.gitattributes` 규칙

따라서 이후 Iris의 정규 test suite는 이 일회성 assessment를 반복 실행하지 않는다.

## 4. Correction Made During This Session

초기 구현에서는 임시 검증 도구를 current route, authority, active core와 기존 회귀 테스트에 연결했다. 이는 요청받은 평가 범위를 넘어 Iris의 정규 검증 구조를 설계한 것이었다.

Owner 지시에 따라 그 승격을 되돌렸다. 평가 결과와 최소한의 정책·작업 기록만 남기고, 검증용 코드는 정규 제품 구조에서 제거했다.

이 정리는 평가 결과가 실패했거나 검증이 부족해서 수행한 것이 아니다. 결과를 확인하는 임시 수단과 Iris가 장기 유지할 정규 아키텍처를 분리하기 위한 범위 수정이다.

## 5. Repository Impact

남은 변경은 다음 범위로 제한한다.

- 일회성 평가 결과
- 평가 기준 문서
- `DECISIONS.md`의 간단한 결과 기록
- `ROADMAP.md`의 완료 기록
- 이 Walkthrough

다음 표면은 이 작업으로 변경하지 않는다.

- Iris runtime Lua
- Menu·Tooltip public text
- package payload
- 정규 current route
- current authority manifest
- active core closure
- 기존 regression test suite
- `ARCHITECTURE.md`

## 6. Reading the Result

`information_sufficient`는 현재 관찰한 근거로 해당 item page가 충분하다는 평가 결과다. `evidence_limited`, `known_information_missing`, `unresolved`는 각각 현재 evidence 범위, 확인된 누락, 미해결 상태를 구분한다.

이 분포는 후속 정보 보강 작업의 참고 자료다. 자동으로 설명을 생성하거나 우선순위·release 여부를 결정하지 않는다.
