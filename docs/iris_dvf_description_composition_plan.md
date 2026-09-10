# Implementation Plan — DVF-COMPOSITION-2

## 1. Objective

문제 1의 의미 블록을 받아 **무엇을 어떻게 한국어·영어 문장으로 표현할지에 관한 공통 규칙과 생성기**를 구현한다. 같은 의미 입력에서 Tooltip 둘째 줄용 compact와 Menu용 expanded를 각각 구성하고, 2,105개 아이템의 원문·의미 연결·부재/실패 사유를 문제 3이 그대로 읽을 수 있게 제공한다.

- 기준일: 2026-09-10. 상태: 공통 조합기 구현 및 §7 집중 검사·대표 원문 검토 완료. [Closeout](iris_dvf_description_composition_closeout.md)에 결과와 검토 한계를 기록한다. 전체 언어 품질 수락과 실제 PZ 표시 검증은 후속 범위다.
- 근거: [문제 2 v2](iris_dvf_description_composition_problem.md), [문제 1 Walkthrough](iris_layer3_composition_walkthrough.md), [의미 계약](iris_dvf_semantic_block_integration_contract.md), 사용자의 계획 평가 반영 및 테스트/Gate 최소화 지시.
- [PLAN_TEMPLATE.md](PLAN_TEMPLATE.md)의 12개 절을 유지한다.
- 이번 개정은 이전 Review/Cycle 2 선택 중 사용자 요구와 충돌하는 logical-slot 해석, 광범위한 first-contact 자격 재판정, 필수 측정기 및 두 프로세스 전체 비교를 대체한다. 과거 검토 결과를 새 PASS로 재발행하지 않는다.

완료 범위는 공통 문장 조합기와 문제 3 검수용 전체 결과다. 제품 current 전환, 전체 언어 품질 수락, 실제 PZ 표시 검증까지 완료했다고 하지 않는다.

---

## 2. Scope

- 기존 `composition_results.read_result()`로 의미 구조를 읽고 실제 입력 identity를 기록한다.
- compact/expanded의 내용 배치와 문장 골격·병렬 연결·반복 생략·조건 위치·언어별 문법 규칙을 구현한다.
- 근거 있는 내용 배치로 compact의 간결성과 expanded의 충분한 설명을 함께 확보한다.
- 실제 KO/EN 문장을 전체 대상에 생성하고, 발견한 공통 생성 결함은 수정한 뒤 인계한다.
- 동일 결과를 저장·읽어 문제 3에서 원문과 의미를 대조할 수 있게 한다.

### Explicitly Out Of Scope

- 의미 관계 재판정, first-contact 조사 체계 복구·axis 재설계, 문제 1 전체 재수락.
- r6 원본·adoption·current route·L3-05/L3-06 제품 채택 변경.
- Tooltip S1/S3/S4, Alt, 폭, wrap 정책, Menu UI, Lua runtime, T1/T2 adapter, package/install 변경.
- 새 폰트 metric 수집 체계·offline layout 엔진·viewport/profile framework 구축.
- 저장소 전체 Run A/B + comparator, historical replay, 정규 validation registry, 새 seal/receipt/proof/adoption lifecycle.
- 전체 문장 최종 품질 수락(문제 3), 실제 Tooltip/Menu 표시·PZ 검증(기존 B/C).

---

## 3. Non-Goals

- 모든 fact 또는 block에 문장 하나를 배정하고 전부 이어 붙이는 것.
- 대표 용도 하나만 고르기, 글자 수 절단, 길이나 빈도로 의미의 중요도를 결정하기.
- 내부 식별자·Profile·조사 메모를 직역해 사용자 설명으로 출력하기.
- 일부 표현 근거가 부족하다는 이유만으로 설명 가능한 아이템 전체를 자동 공백 처리하기.
- 간결성 문제를 Tooltip 폭 확대나 logical_rows=1 표기로 가리기.
- 개별 FullType별 수작업 문장 DB, 외부 번역 서비스, runtime 요약.

이미 발견한 조합 규칙 결함을 문제 3에 떠넘기지 않는다. 문제 1의 실제 관계 결함은 해당 책임의 최소 수정으로 환류하되, 이번 작업에서 조용히 사실을 바꾸지 않는다.

---

## 4. Assumptions

### 입력과 책임

- 입력은 `Iris/build/description/composition/blocks.json`, schema `iris-layer3-composition-v1`, contract version `1`이다. `item_id`는 exact FullType이며 정규화/추측 join을 하지 않는다.
- 기록상 입력 hash는 `b0b1f8b402c74c48efa0d3ef5bb9413709e38e4582cdbffe8ea74749304d5796`이며 source는 r6 adoption `7dded22fad93b7eeff8debf56205cb9ee84220758d53ecb41396889fb49bd799`다. 실제 읽은 입력을 확인·기록하고 정정으로 달라졌다면 이유를 명시한다. 과거 검증 결과를 새 입력으로 승계하지 않는다.
- 입력은 2,105개 대상, accepted facts 29,202개, 의미/획득 block 10,304개를 보존한다. 숫자는 문장 수·품질 점수·공백 목표가 아니다.
- 조건은 item-level qualifier와 exact application refs에 있다. `block_common`이라는 이름만으로 적용 사실을 확대하지 않는다.
- refinement/variant/result/compound/alternative의 관계와 방향을 소비한다. 창낚시·내구도 감소의 미확정 14건은 인과 없이 별도로 표현한다.
- 기존 r6 prose와 compact 부재/포함 결과는 새 표현의 정답이 아니다. 과거 825/121개 공백과 조사 상태를 새 compact eligibility로 승계하지 않는다.

### Tooltip 요구와 현재 구현의 차이

사용자가 확정한 Tooltip은 **최대 4줄: 1줄 소분류, 2줄 DVF 설명, 3줄 획득 장소, 4줄 랜덤 상호작용**이다. [Philosophy.md](Philosophy.md)의 최대 4줄 원칙을 따른다.

현재 `IrisAltTooltip.lua`는 `UIFont.Small`, engine `MeasureStringX`, 폭·padding·화면 배치와 wrap을 사용하며 하나의 logical slot도 여러 화면 줄이 될 수 있다. 이는 현재 구현의 동작이지 사용자 요구를 logical 4 slots로 완화하는 근거가 아니다.

문제 2는 둘째 줄용 간결한 설명을 생산한다. 실제 표시 확인은 B가 수행한다. 측정하지 않은 결과는 physical fit 미확인으로 남기며, 신뢰할 수 있는 관찰로 여러 줄이 되는 것을 확인했다면 단순 비차단 진단으로 무시하지 않고 관련 설명을 수정하거나 부적합 잔여로 명시한다. 모든 UI 조건의 물리 적합성을 이 문제의 offline 완료와 혼동하지 않는다.

### 환경과 검증 적용

Windows/PowerShell, 현재 저장소 `C:\Users\MW\Downloads\coding\PZ`에서 작업한다. Python은 `uv run --project .\Iris\tooling python ...`을 사용한다. 기존 dirty 변경을 보존하며 새 checkout·외부 경로·자동 commit을 만들지 않는다.

[EXECUTION_CONTRACT.md](EXECUTION_CONTRACT.md) §4-4에 따라 실제 접점에 맞는 검증만 수행한다. Public text 후보를 만든다는 사실은 표현 품질 책임을 발생시키지만 저장소 전체 Gate나 과거 재채택 절차를 자동 추가하지 않는다. 문서상 owner approval은 사용자 사전 승인 지시를 적용하며 플랫폼 권한은 우회하지 않는다.

---

## 5. Repository Areas Affected

### Code

아래는 역할별 후보 배치다. 파일 수·내부 schema·함수 분해는 구현에 맞게 줄이거나 합칠 수 있다. 공통 경로는 `Iris/tooling/src/iris_tooling/domains/layer3/`이다.

- `description_composition_model.py`: 문장 계획/결과 및 소비 계약.
- `description_composition_planner.py`: compact/expanded 배치, 문장 단위와 조건 연결.
- `description_composition_ko.py`, `description_composition_en.py`: 언어별 자연스러운 실현.
- `description_composition_results.py`: 생성·저장·원문 reader와 필요한 CLI.
- `Iris/build/description/v2/tests/test_layer3_description_composition.py`: 계획된 집중 검사 한 진입점.

기존 composition reader/model과 필요한 표현 어휘·Tooltip 소스는 읽기 전용 참고 대상이다. r6 private producer 실행이나 기존 출력 wrapper로 구현하지 않는다. 측정 전용 모듈은 필수로 만들지 않는다.

### Docs

- 본 계획.
- `docs/iris_dvf_description_composition_contract.md`: 내용 배치·문장 조합·조건 보존·reader의 실제 규칙과 예시.
- `docs/iris_dvf_description_composition_closeout.md`: 실제 결과·검사·대표 원문·잔여·문제 3 인계.

별도 review receipt나 문서별 봉인을 요구하지 않는다. 공유 current-state 문서·문제 1 Walkthrough를 자동 갱신하지 않는다.

### Config

새 budget_contract/font_metrics, validation registry, dependency/package 설정 변경을 기본 요구하지 않는다.

### Generated Artifacts

- `Iris/build/description/composition/descriptions.json`: 전체 KO/EN 원문, 최소 의미 연결, 상태와 진단을 담을 결과 위치.
- 별도 diagnostics 파일은 실제 가독성/크기상 필요할 때만 사용한다. 요약은 결과 또는 closeout에 합칠 수 있다.
- 임시 파일이 필요하면 `.tmp/expression/`의 짧은 역할 기반 경로를 사용한다. Gate별 디렉터리 tree를 만들지 않는다.
- 기존 blocks 및 r6 결과는 덮어쓰지 않는다. 후속 검수에 필요한 최종 결과를 보존하되 새 authority 봉인으로 취급하지 않는다.

---

## 6. Planned Changes

### Change 1 — 내용 배치와 문장 조합 규칙

**Purpose:** 확보된 의미를 짧은 첫 설명과 충분한 상세 설명으로 옮기는 공통 규칙을 만든다.

**Files:** planner/model, contract 및 필요한 어휘.

**Implementation Notes:**

- 기본 입력은 blocks와 관계·조건이다. Compact와 expanded는 같은 입력에서 각각 구성하며 서로의 완성 문장을 절단/복제하지 않는다.
- 어떤 기능을 이해시키는 말인지, 상세 대상·결과·절차 중 무엇을 expanded에 둘지 설명 가능한 공통 배치 규칙을 정한다. 모든 block을 compact에 반드시 열거하지 않되, 이 선택으로 대표 용도 하나만 남기거나 독립 용도를 전체 설명에서 삭제하지 않는다.
- Compact에는 첫 이해에 필요한 기능 의미와 그 주장을 성립시키는 조건을 남긴다. 대상별 상세·부수 결과 등을 expanded에 배치할 때 같은 언어의 실제 상세 문장으로 연결한다. 의미를 바꾸는 조건은 삭제하지 않으며 세부를 생략한 상위 표현 자체도 입력 근거가 뒷받침해야 한다.
- 문장 골격, 기능의 병렬화, 공통 주어/서술어 생략, 조건 위치, 문장 종결을 명시한다. 출력 순서는 읽기와 수식 관계를 위한 표현 선택이며 용도 중요도나 추천 순위가 아니다.
- 판자·Notebook·의류의 실제 입력에서 compact에 남길 내용, expanded로 보낼 내용과 이유, 짧은/상세 문장 예시를 contract에 정리한다. 이는 별도 선행 Gate나 고정 정답 문장이 아니며 구현 과정에서 수정할 수 있다.
- 문제 1의 relation을 보존한 문장 병합·분할은 허용한다. 독립 의미를 허위 상위 기능으로 합치거나 같은 조건만으로 인과를 생성하지 않는다.
- qualifier 반복 생략은 exact 적용 범위를 유지할 때만 한다. 쓰기 조건을 노트 잠금 전체에 확대하거나 repair_target을 tool로 바꾸지 않는다.
- 획득은 상세에서 경로·조건을 유지하고 Tooltip 획득 장소의 S3 책임과 구분한다. 정확한 레시피·우클릭·자유 조리 절차의 소유권은 Layer 4에 남긴다. 실제 열람 가능한 내용 없이 이관 완료라고 하지 않는다.

**보조 정보와 불확실성:**

- first-contact axis/state를 전체 corpus의 새 자격 심사로 재구축하지 않는다. 기존 정의가 필요한 구체적인 배치 판단이 있을 때만 먼저 blocks에서 빠진 정보가 무엇인지 밝힌다.
- 필요한 경우 저장소 내부의 `Iris/_docs/authority/dvf/layer3_investigation/contract.json` 또는 r6 `audit.json`의 관련 구조화 필드만 참고한다. 사용한 필드·근거·판단 목적을 contract에 간결히 적는다. 전체 metadata allowlist framework나 상태 교란 검사 체계를 만들지 않는다.
- 과거 prose·compact inclusion·blank 수·Profile 순서·관찰 state만으로 포함/제외를 결정하지 않는다. 추가 자료가 없어도 blocks로 확정할 수 있는 표현은 진행한다.
- 일부 내용 배치 근거가 부족하면 해당 의미의 상세 보존·중립적인 표현 가능성을 먼저 판단한다. 임의 대표 선택이나 불확실성을 감춘 일부 출력은 금지한다. Surface 전체를 만들 수 없을 때만 그 범위의 실패와 구체 원인을 기록한다.
- 필요한 정보가 있는데 구현하지 못한 규칙은 자체 결함이다. 이를 upstream 부재로 이름만 바꿔 넘기지 않는다.

**Validation:** §7에서 같은 실제 사례의 원문과 의미 연결을 확인한다. 단계별 별도 테스트/승인 Gate는 없다.

### Change 2 — KO/EN 실현과 상태·보존 계약

**Purpose:** 의미 목록을 자연스럽고 간결한 문장으로 생성하고, 표현되지 않은 내용을 숨기지 않는다.

**Files:** KO/EN realizer, model/results, contract.

**Implementation Notes:**

- KO는 조사·호응·자연스러운 동사/명사 병렬·수식 범위·조건 위치를, EN은 관사·수 일치·병렬 동사구·수식 부착을 다룬다. 서로의 생성 문장을 기계 번역 입력으로 사용하지 않는다.
- 같은 의미 계획을 언어별로 자연스럽게 실현한다. 문장 수/어순 차이는 허용하며 역할·조건·대안·부정·결과는 같아야 한다.
- 같은 의미와 적용 범위의 반복만 생략한다. 문자열이 같다는 이유로 다른 의미를 삭제하지 않는다. 내부 ID·조사 용어·불확실성 메모를 사용자 문장에 직접 내보내지 않는다.
- 결과는 exact item, locale, surface, 원문, 최소 block/branch/fact/qualifier/relation 연결, 필요한 배치 사유를 보존한다. 모든 code-point span이나 세분된 clause ID를 필수로 요구하지 않는다. 검수자가 실제 문장과 근거를 대조할 수 있는 정도로 구현한다.
- `present`는 정의된 surface 내용을 안전하게 실현한 상태, `absent`는 정당한 내용 부재, `failed`는 안전한 실현 불가로 구분한다. 정확한 enum은 구현자가 정할 수 있지만 의미·원인 구분은 유지한다. Malformed input은 reader 오류이며 정상 부재가 아니다.
- 빈 문자열·다른 locale·r6 원문으로 실패를 감추지 않는다. 문제 1의 14건은 두 사실의 독립 서술이며 인과 관계를 추가하지 않는다.
- expanded에는 채택된 사용자 의미가 실제 문장으로 접근 가능해야 한다. compact에서 생략한 상세가 refs/audit에만 남으면 보존 성공이 아니다. Expanded 실패와 연결된 상세를 보존 완료로 계산하지 않는다.

**간결성과 표시 경계:**

- 반복 생략·병렬화·더 짧은 동등 표현·정당한 상세 배치를 적용한다. `등/기타/다양한 용도`로 다른 의미를 모호하게 지우거나 문자수 절단으로 처리하지 않는다.
- Tooltip 둘째 줄용 간결성을 실제 원문에서 평가한다. 짧게 표현할 규칙이 미구현인 장문을 그대로 두고 문제 3에 넘기지 않는다.
- 기존에 즉시 재사용 가능한 신뢰할 만한 폭 측정이 있으면 필요한 대표 원문에만 활용할 수 있다. 없다면 폰트/폭/실제 화면 적합성을 미확인으로 명시하고 B에 전달한다. Byte 수·임의 글자 cap·측정 stub을 실제 PZ fit 증거로 쓰지 않는다.
- 측정기 개발·metric 확보는 이번 완료의 선행 조건이 아니다. 실제 overflow가 확인됐으면 관련 공통 문장 규칙을 수정하고, 해소하지 못한 부적합을 정상 fit으로 보고하지 않는다. 이 문제에서 UI 폭이나 wrap 정책을 바꾸지 않는다.
- 필요해서 `logical_rows`를 남기더라도 slot 유무 정보일 뿐이다. 값 1이 물리 한 줄이나 최대 네 줄 충족을 증명하지 않는다.

**Validation:** §7의 의미 보존·대표 언어 검토에 포함하며 독립 layout Gate를 만들지 않는다.

### Change 3 — 전체 생성·공통 결함 수정·문제 3 인계

**Purpose:** 대표 예시 성공을 넘어 전체 원문을 검수 가능한 상태로 전달한다.

**Files:** results/reader, 집중 검사, 실제 결과와 closeout.

**Implementation Notes:**

- 2,105개 × KO/EN × compact/expanded의 8,420 surface 상태를 빠짐없이 제공한다. 모든 상태에 비어 있지 않은 문장을 강제하는 것은 아니다. 정상 부재·입력 한계·규칙 실패를 구분한다.
- 전체 길이·반복·문장 경계·상태 분포는 공통 결함을 찾는 진단으로만 사용한다. 고정 품질 점수·감소 quota를 만들지 않는다. 필요할 때만 과거 r6 비교 자료를 읽고 새 입력으로 사용하지 않는다.
- 실제 전체 결과에서 조합되지 않은 반복 나열이나 공통 grammar 누락을 확인하면 수정한다. 대표 사례가 통과했다는 이유로 알려진 공통 결함을 남기지 않는다.
- 생성과 읽기를 분리한다. Reader는 저장된 원문/의미 연결을 반환하고 producer를 호출하지 않는다. 문제 3은 같은 결과를 재생성 없이 검수한다.
- 검사한 결과를 그대로 보존한다. 새 결과의 입력/생성기 식별 정보와 실제 검수 범위를 남기되 별도 copy/seal/receipt Gate를 만들지 않는다.
- 수정이 있으면 영향 범위의 결과를 다시 생성·확인한다. 전체 최종 파일 갱신에 전체 생산이 필요하면 한 번 갱신하되 수정마다 무조건 전체 suite나 두 번 비교를 요구하지 않는다. 변경 없는 결과는 재사용한다.

**Validation:** §7에서 전체 결과 하나의 보존·읽기·대표 원문을 공유한다.

---

## 7. Validation Plan

### Automated Validation

**필수 자동 수락 진입점은 다음 집중 명령 하나다.** 구현과 필요한 수정이 준비된 마지막에 실행한다. 계획 밖 중간 테스트나 전체 suite를 하지 않는다.

```powershell
uv run --project .\Iris\tooling python -I -B -m pytest --noconftest -c .\Iris\tooling\pyproject.toml .\Iris\build\description\v2\tests\test_layer3_description_composition.py -q
```

확인 범위는 아래를 같은 입력·출력으로 묶는다. 항목 수는 별도 Gate나 test 함수 수가 아니다.

- 작은 실제 의미 형태의 fixture에서 병렬화·반복 생략의 성공, 역할/조건 범위·인과·대안 보존과 필요한 최소 반례를 확인한다. 입력 순서를 바꾼 작은 사례로 안정성을 확인하며 전체 corpus의 별도 프로세스 두 번 생성은 요구하지 않는다.
- 기존 reader로 입력을 한 번 읽고 전체 생성기를 기본 한 번 실행한다. 그 결과에서 exact 대상/locale/surface, 의미의 표현·상세 배치·미실현 상태, qualifier의 정확한 적용 범위, KO/EN 의미 대응을 대조한다. 자동 검사가 자연어 의미 정확성을 전부 입증한다고 하지 않는다.
- 입력 참조와 출력 연결의 핵심 보존은 production validator의 성공 여부만 믿지 않고 검사에서 입력을 직접 대조한다. 필요한 오류 반례는 같은 fixture에 묶고 별도 검사기 검증 체계를 만들지 않는다.
- 같은 결과를 저장하고 reader로 한 번 읽는다. 원문·상태·의미 연결이 보존되고 읽기 때문에 재생성되지 않는지 확인한다. 별도 인계/parity Gate는 없다.

실행 중 진행·경과 시간을 주기적으로 확인하고 무한 반복·비정상 장기 실행이 의심되면 중단해 원인을 고친다. 실패/수정이 있으면 같은 진입점의 필요한 검사를 다시 수행하되 과거 PASS를 새 결과에 붙이지 않는다. 필수 도구 부재는 BLOCKED이고 실제 명령 exit `0`일 때만 해당 검사 PASS를 기록한다.

### Manual Validation

같은 전체 결과의 실제 KO/EN compact/expanded를 의미 연결과 나란히 읽는다. 대표는 판자, Notebook, Hammer, Molotov, 촛불·의류 및 기능 변형/결과/획득 대안/국소 조건을 덮도록 선택한다. 미확정 창낚시 관계에서 인과가 생성되지 않는지도 확인한다. 사례 수 하한이나 별도 reviewer Gate를 요구하지 않는다.

문법·조사·호응·수식 범위, 간결성·반복, 자연스러운 표현·번역체, 역할/조건 보존을 함께 판단한다. 사례·관찰·수정 규칙과 자체 검토 범위를 closeout에 간결하게 적는다. 원문은 결과를 재사용하고 별도 증명 묶음을 만들지 않는다. 외부 reviewer가 실제 필요하면 Codex Reviewer를 사용하며 필수로 추가하지 않는다.

전체 분포는 대표 검토를 보조한다. 광범위한 장문/반복이 있으면 공통 규칙 적용 누락을 확인하고 고친다. 발견된 결함을 수정한 뒤에는 영향받은 실제 원문을 다시 읽는다. 문제 3의 전체 품질 검수는 별도로 남긴다.

### Validation Limits

- 전체 Run A/B + comparator, 두 hash-seed process의 전체 결과 비교, import/flag/seed 인증, historical replay, 문제 1 재수락, validation registry/preflight, 새 budget profile 검사는 필수가 아니다.
- 폰트 metric 부재를 생성기 BLOCKED로 만들지 않는다. 실제 PZ fit을 확인하지 않았으면 그 주장을 하지 않는다.
- Lua/Java/JS·package·T1/T2·Menu·인게임 검사는 이번 코드 접점이 아니므로 실행하지 않는다. 기존 구현이 사용자 최대 네 줄 요구를 충족한다고 소급 주장하지 않는다.
- r6 private producer/authority를 변경하지 않는 구현을 기본으로 한다. 불가피한 변경이 실제 발생할 때만 적용 계약의 정확한 접점과 최소 검사를 명시한다. 어휘 참고·읽기·새 모듈 구현만으로 A의 장시간 focused gate를 자동 실행하지 않는다. 재채택을 이번 범위에 편의상 끌어들이지 않는다.
- 서식 확인은 관련 파일의 `git diff --check`로 할 수 있으며 별도 Gate나 artifact를 만들지 않는다.

---

## 8. Risk Surface Touch

### Authority Surface

기존 의미 관계·조건 authority를 소비한다. Compact/expanded 배치는 이번 표현 책임이며 새 조사 eligibility authority를 만들지 않는다. 실제 기존 정의가 필요한 부분만 최소 근거를 사용한다.

### Runtime Behavior Surface

없음. 현재 Tooltip의 logical wrap 동작을 사용자 요구의 변경으로 해석하지 않는다. Offline Python과 runtime Lua의 책임을 유지한다.

### Compatibility Surface

문제 3이 읽을 내부 결과/reader가 추가된다. 기존 r6 supplier와 자동 호환이라고 하지 않으며 B/C adapter는 후속 범위다.

### Sealed Artifact Surface

기존 r6·adoption·current·package를 변경하지 않는다. 새 결과는 검수 입력이며 별도 봉인 체계를 만들지 않는다.

### Public-Facing Output Surface

후보 KO/EN 사용자 문장을 생성하므로 실제 표현 품질 책임이 있다. 현재 제품 표시 변경 및 전체 품질 수락과는 구분한다.

---

## 9. Risk Analysis

### Architecture Risk

- 과거 first-contact 조사 재판정으로 범위가 커지는 위험: blocks를 기본 입력으로 유지하고 구체적인 배치 판단의 최소 보조 자료만 사용한다.
- r6 문장 join으로 돌아갈 위험: 실제 문장 규칙과 원문 사례에서 합성·반복 생략을 확인한다.

### Runtime Risk

- 장문을 logical slot 하나로 간주하는 위험: 최대 네 줄 요구를 유지하고 실제 표시 확인을 B에 인계한다.
- 표시 엔진 복제 위험: 별도 측정기/metric 구축을 필수 범위에서 제외한다.

### Compatibility Risk

- 새 결과를 기존 supplier에 바로 연결하는 위험: 문장/상태/의미 연결의 내부 인계와 제품 adapter를 구분한다.
- 기존 dirty 변경과 충돌: 관련 파일만 수정하고 원본 입력을 보존한다.

### Regression Risk

- 과도한 요약으로 역할·조건·독립 용도 누락: 실제 원문과 의미 연결을 함께 확인한다.
- 모든 상세를 짧은 문장으로 바꾼 뒤 누적: 내용 배치와 공통 문법 규칙을 실제 전체 결과에 적용한다.
- 미지원 문법/배치 판정을 upstream 사유로 회피: 원인과 책임을 구분하고 해결 가능한 공통 결함은 종료 전에 처리한다.
- refs만 같은 번역체 문장: KO/EN 실제 대표 문장을 읽고 문제 3에 전체 원문을 넘긴다.

---

## 10. Rollback Plan

1. 잘못된 결과는 current 제품에 연결하지 않는다. 입력과 사용자 변경은 유지한다.
2. 표현 결함은 공통 규칙을 수정하고 필요한 결과·검사를 갱신한다. 출력 JSON만 손으로 바꾸지 않는다.
3. 의미 입력 결함은 해당 책임으로 반환하고 수정 전후 입력을 구분한다. 문장 편의로 관계를 조용히 바꾸지 않는다.
4. 실패/부재를 r6나 다른 locale로 대체하거나 원문을 절단해 숨기지 않는다.
5. 되돌릴 때 이번 작업의 변경만 대상으로 하고 기존 dirty/history를 reset·recursive cleanup하지 않는다.

---

## 11. Governance Constraints

- Philosophy와 사용자 확정 정의를 따른다. Tooltip 최대 네 줄을 logical slots로 완화하지 않는다.
- 대표 용도 단일화·추천·역할 전환·근거 없는 인과·조건 확대를 금지한다.
- 기존 의미 구조의 내용을 실제 사용자 설명에서 보존한다. 상세 refs만 남긴 것을 열람 가능한 문장으로 계산하지 않는다.
- 현재 저장소와 이 계획에 필요한 경로만 사용한다. 사전 owner 승인과 별개로 플랫폼 권한은 우회하지 않는다.
- 임시 검사/helper를 canonical validator로 승격하지 않는다. 검증·봉인 작업이 구현보다 커지지 않게 하고 필수 조건 충족 후 추가 confidence 검사 없이 닫는다.

---

## 12. Expected Closeout State

목표는 **complete — 문제 2 공통 문장 조합기와 문제 3 전체 검수 입력 확보**다.

| 완료 조건 | 필요한 결과 |
| --- | --- |
| 실제 공통 조합기 | Blocks에서 compact/expanded를 각각 구성하고 KO/EN 문장 골격·병렬화·반복 생략·조건 배치를 구현했다. 단순 join wrapper가 아니다. |
| 의미와 대표 언어 품질 | 실제 대표 원문에서 기능 구별·역할·조건·대안·인과 보존과 간결성·자연스러움을 확인했다. 전체에서 발견한 공통 생성 결함은 수정했다. |
| 전체 검수용 인계 | 2,105개/8,420 surface의 원문 또는 정당한 부재/실패 사유, 의미 연결, reader와 입력/생성기 정보가 있어 문제 3이 재생성 없이 읽는다. |

세 조건은 별도 Gate가 아니다. 계획된 집중 검사와 같은 결과의 대표 언어 검토를 공유한다. 원문 생성·읽기·필수 보존이 검증됐고 확인한 공통 결함이 해결됐을 때만 완료한다. 실패 record를 빠짐없이 만들었다는 이유로 미구현 조합기를 완료 처리하지 않는다.

실제 입력 근거가 부족한 국소 잔여는 원인·영향·가능한 표현과 함께 인계할 수 있다. 핵심 내용 배치·공통 문법·대표 언어 검토가 미완료면 partial/implemented_only, 필요한 입력/도구가 없어 진행할 수 없으면 blocked다. 필요한 의미를 보존하며 compact를 만들 수 없는 알려진 문제를 정당한 장문이라는 이름만으로 수락하지 않는다.

실제 폰트/폭의 적합성이 미확인이어도 offline 생성기/검수 인계 범위의 완료는 가능하다. 다만 physical fit 성공이나 제품 최대 네 줄 충족을 주장하지 않으며, 확인된 표시 부적합·미확인 조건은 B 인계에 명시한다. 실제 한 줄에 맞지 않는 설명의 최종 제품 수락은 남아 있다.

Closeout에는 실제 명령/exit, 결과 위치, 사용한 공통 규칙과 대표 원문 검토, 부재/실패/미확인 범위만 간결하게 기록한다. 문제 3의 전체 어색함·간결성·자연스러움·번역체/의미 검수와 기존 B/C의 제품 연결·인게임 확인은 별도 완료 조건이다. 추가 adoption/seal 또는 측정기 완성 작업을 자동으로 붙이지 않는다.
