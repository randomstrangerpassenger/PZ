# Implementation Plan — DVF-COMPOSITION-1

## 1. Objective

Iris의 채택된 r6 Layer 3 사실에서 재사용 가능한 **의미 통합 규칙**을 구현하고, 전체 대상에 적용한 의미 구조와 판단 한계를 문제 2의 설명 조합기가 사용할 수 있도록 제공한다. Profile 이름이나 기존 문장 유사도로 묶지 않고 기능·역할·대상·맥락·조건·결과의 관계로 판단한다.

- 문제 ID: `DVF-COMPOSITION-1`
- 개정 기준일: 2026-09-10
- 근거: [문제 정의](iris_dvf_semantic_block_integration_problem.md), [PLAN_TEMPLATE.md](PLAN_TEMPLATE.md), 사용자 계획 검토와 검증 축소 지시.
- 입력: `Iris/_docs/authority/dvf/layer3_expression/successors/r6/adoption.json`, SHA-256 `7dded22fad93b7eeff8debf56205cb9ee84220758d53ecb41396889fb49bd799`.
- 기록상 입력 규모: exact FullType 2,105개, semantic facts 28,145개, acquisition facts 1,057개. 실제 정상 reader가 읽은 값과 대조한다. 수치는 통합률·해결률 quota가 아니다.
- 예상 종료: **문제 1 complete — 의미 통합 규칙·적용 결과·문제 2 인계 완료**. 최종 문장 품질, 제품 채택, Tooltip/Menu 연결 완료는 주장하지 않는다.

이 개정은 이전 candidate-only subplan을 대체한다. 규칙과 결과를 문제 2의 개발·검증 입력으로 확정하는 일까지 이번 범위에서 끝낸다. runtime/current 전환을 하지 않는다는 이유로 문제 1을 별도 adoption 작업까지 자동으로 열어 두지 않는다. 기존 제품 authority를 대체하는 채택은 후속 제품 적용 범위에서 다룬다.

---

## 2. Scope

- 기존 정상 r6 reader로 structured facts와 필요한 관계·근거 참조를 읽는다.
- 중복/동일, 포함/세분, 공통 기능의 맥락 변형, 대안, 독립 용도, 판단 불가를 구분하는 일반 규칙을 실제 사례에서 도출한다. enum·자료구조·파일 수는 이 의미 의무를 만족하는 범위에서 구현자가 정한다.
- 역할·대상·결과·맥락의 충돌을 유사성보다 먼저 고려한다. 다른 맥락이 항상 충돌인 것은 아니며, 정당한 변형 관계와 양립 불가를 구분한다.
- 조건을 공통 조건, 특정 분기 조건, 적용 범위 미확정으로 구분한다. 공통화는 해당 분기들에 대한 근거가 있을 때만 허용한다.
- 기존 근거로 확인할 수 있는 최소 관계 정보 부족은 이번 범위에서 보완한다. r6 원본을 수정하지 않고 파생 관계 또는 최소 overlay로 표현할 수 있다.
- 전체 대상에 적용하고, 근거로 해결 가능한 공통 규칙 누락을 수정한다. 남는 불확실성과 표현에 미치는 영향을 인계한다.
- 문제 2가 문장을 파싱하거나 사실 관계를 재판정하지 않고 사용할 수 있는 결과와 읽기 경로를 제공한다.

### Explicitly Out Of Scope

- r6 원본·adoption·current route의 수정/재채택, 과거 미해결 주장 4,223개의 전수 재조사, 새 게임 사실 추론.
- KO/EN 최종 문장 조합기, 전체 설명 품질 수락, Tooltip/Menu/Lua 수정, 패키지·설치·배포.
- 저장소 전체 Run A/B + comparator, clean checkout/worktree/외부 실행 환경, 기존 D6나 A/B의 재채택 검증.
- 기존 loader의 historical replay 재검증, 전체 provenance chain의 독립 재인증, validation registry·분류 정책 변경.
- 범용 ontology/validator, 새 seal·receipt·proof 체계, 별도 candidate adoption 절차 신설.
- 전체 아이템의 인간 의미 전수 검수 및 모든 입력 사실의 게임 진위 재검증. 전체 설명 품질 검수는 문제 3의 책임이다.

---

## 3. Non-Goals

- block 수·문장 수·unresolved 수를 임의 목표치에 맞추지 않는다.
- 모든 fact를 singleton으로 보존한 결과를 의미 통합 성공으로 처리하지 않는다.
- Profile을 사용자 블록, 대표 용도, 우선순위로 바꾸지 않는다. `primary_use`로 돌아가지 않는다.
- 의미 블록 하나를 화면 블록 하나 또는 문장 하나로 고정하지 않는다.
- 부족한 규칙을 기록하는 것만으로 해결했다고 하지 않는다.
- 문제 1 완료를 문장 가독성·Tooltip 최대 4줄·Menu 표시 완료로 확대하지 않는다.

---

## 4. Assumptions

- [Philosophy.md](Philosophy.md)가 최상위 기준이다. offline 의미 생산은 Iris 내부 책임이며 다른 모듈을 변경하지 않는다.
- Windows PowerShell, 저장소 루트 `C:\Users\MW\Downloads\coding\PZ`, Python 실행은 `uv run --project .\Iris\tooling python ...`을 사용한다.
- r6의 accepted fact identity, payload, context/qualifier 참조와 provenance를 사용한다. 모든 관계 정보가 이미 충분하다고 가정하지 않는다.
- 기존 `recovery.load_adopted`의 정상 소비 경로를 재사용한다. 이번 작업에서 historical replay나 과거 producer를 실행할 필요는 없다.
- 기존 KO/EN 설명은 실패 사례 탐색에만 쓰며 의미 관계의 판정 근거로 쓰지 않는다. audit 전체를 공개 의미로 승격하지 않는다.
- 기존 dirty 변경을 보존하고 reset·checkout·자동 커밋을 하지 않는다. 저장소 밖 입력·출력·새 checkout을 만들지 않는다.
- [EXECUTION_CONTRACT.md](EXECUTION_CONTRACT.md) §4-4에 따라 실제 변경 범위에 맞게 검사한다. 과거 Gate 기록이나 명령 목록만으로 이번 검증 의무를 늘리지 않는다.
- 문서상 owner approval은 사용자의 사전 승인 지시를 적용한다. 도구/플랫폼 권한 확인은 우회하지 않는다.

---

## 5. Repository Areas Affected

### Code

역할에 따른 배치 후보이며 기존 적합한 모듈을 재사용하거나 합칠 수 있다.

- `Iris/tooling/src/iris_tooling/domains/layer3/composition_model.py`: 의미 구조와 consumer 입력 계약.
- `Iris/tooling/src/iris_tooling/domains/layer3/composition_rules.py`: 관계 판정·조건 귀속·최소 관계 보완.
- `Iris/tooling/src/iris_tooling/domains/layer3/composition_results.py`: 정상 r6 입력, 적용 결과 저장·읽기.
- `Iris/tooling/src/iris_tooling/domains/layer3/cli.py`: 실제 인계/생산에 필요한 경우만 최소 연결.
- `Iris/build/description/v2/tests/test_layer3_composition.py`: 이번 범위의 집중 검사 한 진입점. 별도 정규 validation authority로 승격하지 않는다.
- `recovery.py`는 읽기 전용 소비 대상이다. 정상 입력 자체를 얻을 수 없는 결함이 있으면 관계 미해결로 숨기지 않고 입력 blocker로 보고한다.

### Docs

- 본 계획.
- `docs/iris_dvf_semantic_block_integration_contract.md`: 일반 규칙·허용 근거·조건 귀속·문제 2 인계 계약.
- `docs/iris_dvf_semantic_block_integration_closeout.md`: 실제 결과·대표 사례·잔여·검증 한계를 한곳에 기록.
- 문제 정의는 변경하지 않는다. current 제품 상태가 바뀌지 않으므로 ARCHITECTURE/DECISIONS/ROADMAP의 제품 채택 기록을 갱신하지 않는다.

### Config

새 repository Gate, required-validation 등록, 검사 분류 preflight를 추가하지 않는다. 기존 regular test discovery에 전체 자료 생산을 편입하지 않는다.

### Generated Artifacts

- 역할 기반의 짧은 저장소 내부 경로 `Iris/build/description/composition/`에 문제 2가 읽을 실제 결과를 보존한다. 결과 파일명은 `blocks.json` 등 내용의 역할에 따라 정한다.
- 입력 identity와 contract version 등 재사용에 필요한 최소 메타데이터는 결과 안에 둘 수 있다. 별도 manifest·casebook·audit 파일을 반드시 만들 필요는 없다.
- 사례와 잔여 요약은 contract/closeout 또는 같은 결과에 합친다. 테스트 기대값은 작은 fixture로 유지할 수 있다.
- 임시 출력이 필요하면 `.tmp/composition/`을 사용한다. Gate별 디렉터리 트리, 별도 durable 복사/봉인 체계를 요구하지 않는다. 기존 파일은 확인 없이 덮어쓰지 않는다.
- 후속 입력과 완료 근거는 보존하되 재생성 가능한 임시물을 영구 authority로 만들지 않는다.

---

## 6. Planned Changes

### Change 1 — 실제 사실에서 공통 의미 규칙 구현

Purpose:

어떤 사실을 함께 설명할 수 있고 어떤 의미·조건은 분리해야 하는지 일반 규칙으로 결정한다.

Files:

- composition 입력/규칙 모듈과 contract.

Implementation Notes:

- 정상 r6 reader가 확인한 같은 payload를 재사용한다. 기록상 대상/사실 수와 다른 경우 원인을 확인하고 입력을 임의 교체하지 않는다.
- 기능·역할·대상·결과·맥락·조건의 실제 구조를 확인한다. 동일/중복, 포함/세분, 변형, 대안, 독립, 판단 불가의 판정 근거와 충돌 시 처리 순서를 정의한다.
- 구조가 허용하는 한 동일 의미를 여러 Profile에서 발견한 중복은 통합한다. 포함·변형·대안의 방향과 분기는 보존한다.
- 조건은 원래 적용 대상을 유지한다. 모든 관련 분기를 덮는다고 확인된 경우만 공통 조건으로 올린다. 여러 block에 걸친 공통 표현에 필요한 적용 대상도 문제 2가 추측 없이 읽을 수 있도록 제공한다. 특정 필드명이나 item-global schema를 강제하지 않는다.
- acquisition은 기능 사실과 구별하고 기존 획득 방식·조건·근거를 보존한다. 획득 사실의 진위를 새로 판정하지 않는다.
- Hammer의 수리 대상/도구, Notebook의 작성/잠금 조건, Molotov의 조건, 판자의 중복 맥락/독립 용도, 연료·불쏘시개·마찰 점화의 공통점/차이를 실제 사실 참조와 함께 살핀다. 이름별 예외 규칙을 만들지 않는다.
- 반드시 통합되어야 하는 실제 사례와 통합하면 안 되는 사례를 모두 둔다. 사례 수 하한은 없고 의미 유형과 위험의 coverage로 정한다.
- 필요한 최소 관계 보완은 기존 근거·일반 규칙·보완 이유를 남긴다. 새 게임 사실이 필요한 부분은 추측하지 않는다.

Validation:

§7의 동일 집중 검사에서 작은 사례와 실제 적용 결과를 함께 확인한다. 단계별 별도 테스트/Gate를 실행하지 않는다.

### Change 2 — 전체 적용, 해결 가능한 누락 수정, 문제 2 인계

Purpose:

일반 규칙을 전체 자료에 적용하고 실제로 사용할 수 있는 의미 구조를 남긴다.

Files:

- composition 모델/생산·읽기 모듈, 결과, contract/closeout.

Implementation Notes:

- 각 입력 사실을 block에 표현, residual, 관계 미확정, 기존 비공개 disposition 중 추적 가능한 상태로 유지한다. 여러 사실이 한 의미로 합쳐져도 각 fact ref와 근거 연결은 잃지 않는다.
- 분기·대안·역할·조건·결과 관계를 consumer가 재추론하지 않아도 되게 한다. 별도의 전 provenance 재인증 체계는 만들지 않는다.
- 미해결 원인은 규칙 미구현, 최소 관계 정보 보완 필요, 현재 근거로 결정 불가를 구분한다. 명칭은 구현자가 정할 수 있다.
- **기존 근거와 이번 범위의 최소 보완으로 해결 가능한 공통 규칙 누락은 수정 후 종료한다.** 이를 unresolved/residual로 이름만 바꾸어 완료 처리하지 않는다. 전체 적용에서 드러난 반복 미통합과 규칙 공백을 검토하고, 동일 유형은 공통 규칙으로 처리한다.
- 관계를 확정할 수 없는 경우는 범위·부족 근거·문제 2에서 가능한 표현과 보류되는 표현을 남긴다. 광범위한 입력 부족으로 핵심 통합을 제공하지 못하면 부분 완료이며 성공으로 포장하지 않는다. 반대로 범위 밖 재조사가 필요한 국소 잔여를 모두 해결해야만 완료되는 것은 아니다.
- 순서에 의미가 없는 입력은 안정적으로 처리하고 출력 identity가 Profile/prose/입력 배열 순서에 의존하지 않게 한다. 단순 출력 정렬로 잘못된 의미 결정을 가리지 않는다.
- **문제 2에서 금지하는 것은 의미의 임의 변경이다.** 역할·조건·관계 재판정, 독립 용도 삭제, primary_use 복귀를 금지한다. 확정된 의미를 보존한 문장 병합/분할, 병렬 표현, 공통 표현 생략, compact/expanded의 서로 다른 구성은 허용한다. 중요 조건을 생략해 무조건 가능한 용도로 바꾸면 안 된다.
- 이번 결과는 문제 2의 개발·검증 입력으로 제공한다. 기존 current 제품의 채택 사실/표시 경로를 대체하지 않는다. 새 adoption record나 별도 승인 대기 lifecycle을 신설하지 않는다.

Validation:

§7에서 전체 적용 결과 하나를 공유해 사실 보존·관계/조건 범위·실제 통합·후속 읽기를 확인한다. 별도 인계 Gate나 원본 loader 재검증을 만들지 않는다.

---

## 7. Validation Plan

### Automated Validation

**필수 자동 수락 진입점은 아래 집중 명령 하나다.** 구현과 필요한 수정이 준비된 마지막에 실행한다. 계획에 없는 중간 테스트나 전체 suite를 실행하지 않는다. 실패 후 수정한 경우에만 관련 검사를 다시 수행한다.

```powershell
uv run --project .\Iris\tooling python -I -B -m pytest --noconftest -c .\Iris\tooling\pyproject.toml .\Iris\build\description\v2\tests\test_layer3_composition.py -q
```

검사는 다음 세 관점을 같은 입력/결과로 묶는다. 이는 별도 Gate 세 개나 고정된 test 함수 수를 뜻하지 않는다.

1. **의미 규칙:** 작은 근거 기반 사례로 정당한 통합과 독립/대안 보존, 역할 방향, 조건 범위를 확인한다. 통합 가능한 사례를 모두 singleton으로 두면 실패한다. 같은 작은 사례의 입력 순서를 바꿔 의미 관계와 ID의 안정성을 확인한다. 의미 훼손·누락을 잡는 데 필요한 최소 invalid fixture만 사용한다.
2. **전체 적용의 보존과 미해결:** 전체 대상에 producer를 한 번 적용하고 같은 결과에서 fact 누락/중복 disposition, 타 아이템 참조, 존재하지 않는 관계 참조, 조건 적용 대상의 구조적 이탈을 검사한다. actual positive grouping과 잔여 분류를 함께 확인한다. 구조 검사를 모든 관계의 인간 기준 의미 정확성이라고 주장하지 않는다.
3. **문제 2 인계:** 위에서 저장한 실제 결과를 제공된 reader로 한 번 읽어 관계·조건·잔여와 필요한 입력 identity가 보존되는지 확인한다. 별도 생산·복사·adoption/parity Gate를 만들지 않는다.

실행 제약:

- 정상 입력 loader가 이미 수행하는 identity 검사를 재사용한다. 같은 r6를 검사별로 다시 읽거나 독립적인 원본 hash census를 만들지 않는다.
- 전체 producer는 기본 한 번 실행하고 작은 사례/순서 변경/오류 fixture는 메모리에서 처리한다. 전체 corpus를 두 번 생산하는 A/B식 byte comparator를 요구하지 않는다. 검증 범위는 작은 사례의 순서 안정성과 실제 전체 결과의 불변식이며 모든 환경의 전 artifact 결정성을 인증하지 않는다.
- 검사는 저장소 내 결과를 직접 보존하거나 한 번 저장하고 그 결과를 읽는다. 임시 pytest 경로 자체를 authority로 취급하거나 경로가 사라졌다는 이유만으로 별도 계획·승인을 요구하지 않는다. 재생성 결과에 과거 PASS를 붙이지는 않는다.
- 실행 중 주기적으로 진행·경과 시간을 확인한다. 무진행·무한 반복·비정상 장기 실행이 의심되면 중단하고 원인을 고친다. 중단/실패를 PASS로 기록하지 않는다.
- 정확한 명령과 exit `0`일 때만 자동 검사 PASS를 기록한다. 도구 부재는 BLOCKED다. 성공 후 추가 confidence만을 위한 반복 검사를 하지 않는다.

### Manual Validation

같은 실제 적용 결과에서 §6의 의미 위험 사례와 전체 적용에서 드러난 공통 규칙 누락을 확인한다. fixed 24개, 새 표본 보고서, 별도 사람 승인 Gate를 요구하지 않는다. 대표 사례의 통합 전 사실 관계·통합 후 의미·조건 귀속을 contract/closeout에 설명하고, 해결 가능한 반복 누락은 고친다.

이 검토는 문장 가독성 전수 검수나 게임 검증이 아니다. 사례 밖 의미 정확성을 확인했다고 과장하지 않는다. 별도 외부 reviewer는 필수가 아니며 필요하면 Codex Reviewer를 사용한다.

### Validation Limits

- **저장소 전체 Run A/B + comparator, repository full gate, 전체 Python/Java/JS/Lua suite를 이번 필수 검증에 포함하지 않는다.** 일반 D6 재채택 경로를 건드리지 않으므로 그 경로의 검증을 복제하지 않는다.
- 역사 replay/Architecture bytes 변형 검사, 검사 분류 preflight, validator 자체의 검증, 정규 검사 승격·등록·retirement 검사를 하지 않는다.
- package/install, Tooltip 물리적 4줄, Menu, PZ 인게임, KO/EN 전체 문장 품질은 해당 후속 문제에서 검증한다. 전체 프로젝트의 최종 완료 조건에서 제거한 것은 아니다.
- 코드 변경 때문에 기존 필수 계약이 실제로 적용되는 경우에만 해당 조항·변경 접점·필요한 최소 검사를 명시한다. 과거 실행 관례를 이유로 범위를 늘리지 않는다. current/재채택까지 범위가 넓어지는 작업을 이번 문제에 편의상 끌어들이지 않는다.
- `git diff --check`는 문서/변경 파일의 서식 확인으로 사용할 수 있으나 별도 수락 Gate나 증명 artifact로 만들지 않는다.

---

## 8. Risk Surface Touch

### Authority Surface

사실 사이의 의미 통합 책임과 문제 2 입력 계약을 구현한다. 기존 semantic/acquisition truth를 정정하거나 r6/current authority를 대체하지 않는다. 문제 1의 규칙 수락과 제품 adoption을 구분한다.

### Runtime Behavior Surface

없음. Lua·Tooltip·Menu를 변경하지 않는다.

### Compatibility Surface

문제 2가 소비할 내부 결과/reader가 대상이다. 의미와 조건을 재추론 없이 읽을 수 있어야 하며 외부 API/SPI는 변경하지 않는다.

### Sealed Artifact Surface

기존 sealed/adopted 산출물은 읽기 전용이다. 새 결과에 별도 seal lifecycle을 신설하지 않는다.

### Public-Facing Output Surface

없음. 최종 KO/EN 설명이나 제품 표시를 생산·전환하지 않는다.

---

## 9. Risk Analysis

### Architecture Risk

- 의미 관계 규칙을 과도한 ontology로 키우지 않는다. 실제 필요한 관계와 최소 보완만 구현한다.
- 의미 블록을 고정 UI 단위로 만드는 위험은 문제 2의 표현 조합 자유를 명시해 막는다.
- 알려진 규칙 부족을 미해결로 넘기는 위험은 전체 적용에서 발견한 해결 가능한 공통 누락을 종료 전에 수정하는 조건으로 다룬다.

### Runtime Risk

직접 runtime 변경은 없다. 후속에서 이 결과를 현 제품에 자동 연결하지 않도록 인계 범위를 명시한다.

### Compatibility Risk

입력 구조 부족이 문제 2의 사용을 막을 수 있다. 작은 실제 소비 사례와 전체 결과 readback을 같은 집중 검사에 포함하고 한계를 공개한다.

### Regression Risk

- 과잉 통합에 의한 역할 변경·조건 확대와 과소 통합에 의한 반복을 모두 살핀다.
- 판자 등 특정 사례만 통과하는 item별 예외 대신 동일 유형에 적용되는 일반 규칙을 사용한다.
- 기계적 보존과 사람의 의미 확인을 구분한다. sample 밖의 정확성을 검증했다고 하지 않는다.

---

## 10. Rollback Plan

1. 결과가 틀리면 문제 2에 수락 결과로 인계하지 않고 규칙을 수정한다. current 제품을 변경하지 않으므로 제품 rollback은 필요하지 않다.
2. 실패 출력은 성공 출력과 혼동하지 않게 기록한다. 수정 후 실제 검증한 결과를 인계하며 과거 PASS를 재사용하지 않는다.
3. 이 작업의 변경만 되돌릴 수 있게 유지하고 기존 사용자 변경·r6·historical 기록은 보존한다.
4. 실제 부족 근거 때문에 일부 관계를 결정할 수 없으면 해당 관계의 한계를 남기며 다른 해결 가능한 작업은 진행한다. 정상 입력 자체가 불가하거나 핵심 규칙/인계를 제공하지 못하면 partial/blocked로 보고한다.

---

## 11. Governance Constraints

- Philosophy의 근거성·중립성, 모듈 경계와 offline/runtime 책임을 지킨다.
- primary_use·대표 의미·추천/효율 순위를 도입하지 않는다. 정렬 순서는 중요도가 아니다.
- 기존 사실과 근거를 보존하고 역할·조건 범위를 확대하지 않는다.
- 미해결은 정직하게 남기되 이번 범위에서 가능한 해석을 미수행 상태로 방치하지 않는다.
- 사용자 실행 경계와 사전 승인 지시를 따른다. 모든 작업은 현재 저장소와 이 계획의 필요한 경로 안에서 수행한다.
- 일회성 검사/helper를 canonical validator나 새 validation authority로 승격하지 않는다. 추가 seal/receipt/proof artifact와 Gate별 workspace를 만들지 않는다.
- 기존 적용 계약은 지키되, 적용되지 않는 저장소 전체 검증을 자동 추가하지 않는다. 필수 조건 충족 후 추가 봉인이나 confidence 검증 없이 closeout한다.

---

## 12. Expected Closeout State

다음을 충족하면 **DVF-COMPOSITION-1 complete**로 닫는다.

- **M1 — 재사용 가능한 규칙:** 실제 사실의 중복·포함/변형·대안·독립 관계와 조건 귀속을 일반 규칙으로 판단하며 실제 통합 성공 사례가 있다.
- **M2 — 보존과 해결 범위:** 전체 대상에 적용해 사실·관계 참조의 보존을 확인했고, 대표 의미 위험을 검토했으며, 발견한 공통 규칙 누락 중 현재 근거/최소 보완으로 해결 가능한 부분을 처리했다. 결정 불가 잔여는 이유와 영향이 명확하다.
- **M3 — 사용 가능한 인계:** 문제 2가 사용할 실제 결과·reader·표현 책임 경계가 있고, 해당 결과의 읽기가 같은 집중 검사에서 확인됐다.

M1~M3는 별도 Gate가 아니다. §7의 집중 자동 검사 한 번과 같은 결과의 의미 검토를 공유한다. closeout에는 실제 명령/exit, 결과 위치, 규칙과 대표 사례, 잔여 영향과 검증 한계를 간결하게 기록한다.

구현만 있고 필수 검증이 없으면 `implemented_only`, 핵심 규칙 또는 인계가 일부만 되면 `partial`, 외부 입력/도구 문제로 진행할 수 없으면 `blocked`다. 후보 파일 생성과 사실 수 일치만으로 완료하지 않는다.

완료 후 문제 2는 이 규칙과 결과를 사용해 compact/expanded 조합기를 구현한다. 최종 문장 품질은 문제 3, 제품 연결은 기존 B/C에서 다룬다. 이 후속 작업을 남겼다는 이유로 문제 1을 다시 별도 adoption/seal 작업까지 열어 두지 않으며, 문제 1 완료를 제품 표시 품질 완료로 주장하지도 않는다.
