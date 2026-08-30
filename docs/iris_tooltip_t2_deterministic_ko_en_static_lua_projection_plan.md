# Implementation Plan — Iris Tooltip T2 결정적 KO/EN 정적 Lua Projection

## 문서 상태

- 상태: 2026-08-30 실행 채택; 구현 작성, 필수 검증 대기
- 목적: 확정된 T1 handoff를 완성된 KO/EN 0~4줄 정적 Lua staging 데이터로 변환
- 선행 보완: 현재 T1 S1에 누락된 대분류 표제를 기존 승인 surface로 완성
- 검증 원칙: 필수 성질은 유지하고 중복 테스트·독립 증명 절차는 제거
- 완료 범위: static staging 및 T3 입력 전달; 실제 Tooltip runtime 채택은 T3
- 이번 문서 개정은 실행 결과나 검증 PASS를 발행하지 않는다.

## 1. Objective

T2의 semantic input은 current로 채택된 T1 strict production handoff뿐이다.

```text
T1 확정 handoff
→ subject/hash/schema admission
→ S1~S4의 고정 순서 projection
→ FullType별 KO/EN 0~4줄
→ 결정적 Lua serialization
→ 최소 provenance manifest
→ repository-external staging
```

T2는 Classification·DVF·QG를 다시 판정하지 않는다. 후보 선택, 번역, 요약, fallback 또는 runtime 조합 사항을 만들지 않는다.

T3에 제공할 데이터 계약은 다음뿐이다.

```text
exact FullType + explicit ko|en locale → complete string array
```

S1의 요구 형식은 이미 다음으로 고정한다.

```text
[approved category surface - approved primary-subcategory surface]
```

현재 subcategory-only 문자열을 최종 형식으로 채택하는 선택지는 제거한다. 필요한 것은 새 제품 결정이 아니라 기존 승인 label의 전달 누락을 바로잡는 일이다.

## 2. 현재 입력과 선행 결손

### 2.1 Predecessor T1 binding

아래는 보완 전 입력의 계보다. S1 보완 후에는 새 current route와 successor manifest가 가리키는 exact binding을 사용하며 이 값을 successor acceptance 상수로 재사용하지 않는다.

```text
machine commit:
b30aaff2da6172ab5137c55bb460889aa527ad04

machine tree:
7cdd52fd61f739b5018a62d8bffe84461dfea50c

final root:
C:/Users/MW/Downloads/coding/PZ-tooltip-t1-d6-final-b30aaff2

subject_binding SHA-256:
22cb4ef4fc461285b8262d151b791f44235cc2a4dda7f99e9b466b1c973754f9

handoff input SHA-256:
138b6f4ef85a2235fa41e6d60d88e885c6f6f93a8bb0458a7d6ac4dce7af56ac

handoff manifest SHA-256:
15a4a089fdde7eeb70fd0f1e21d77872b90fdaec8130d45605edac52d67fb892

support count:
2,280

support ordered-set SHA-256:
3a6cc24b9ad64e06a0a6c0408821201e35bbd1d8558e6245809b5d3c34265ce6
```

Predecessor observation: S1 1,406 / S2 1,314 / S3 415 / S4 115; 0~4줄 분포 367 / 825 / 895 / 137 / 56. 이 수치는 이전 입력의 관찰이며 생성기는 실제 accepted input에서 다시 집계한다.

### 2.2 S1 결손의 정확한 범위

현재 T1 audit은 D1 owner row의 primary_subcategory_surface만 S1 localized_surfaces에 전달한다. D1 row에는 category_surface와 primary_subcategory_surface가 이미 모두 존재한다.

따라서 다음만 보완한다.

- 적용 대상: 기존 applicable 1,406개 FullType의 S1 KO/EN 표시 문자열
- 입력: D1이 이미 승인한 category/primary-subcategory locale surface
- 결과: 위 고정 형식의 완성된 S1 문자열
- 유지: classification identity, applicable/silence partition, Menu relation, S2~S4 identity/order/surface
- 금지: raw tag 해석, identity 문자열 분해를 통한 label 복원, 새 분류·번역·후보 선택

현재 T1 완료 기록을 소급 수정하지 않는다. 보완된 입력은 기존 T1 successor 경로로 발행한다.

## 3. 실행 범위와 책임 경계

### 포함

- Change 0의 bounded S1 handoff 보완 및 기존 T1 successor 채택
- T1 strict handoff reader와 subject/hash/schema 검증
- 동일 slot vector에서 KO/EN line array 생성
- cause-neutral present/omitted slot provenance
- 고정된 금지 표현 검사와 문자열 보존 검사
- 단일 정적 Lua 및 최소 manifest 생성
- T2 installed CLI와 좁은 결과 finalization
- 기존 full gate의 test-source 등록과 environment binding
- 최소 focused tests, 반복 생성, Lua syntax, 기존 canonical regression gate
- external staging 결과 및 T3 조회 계약 전달
- 필요한 command/contract/생태계 문서의 사실 기반 갱신

### 제외

- D1~D5의 분류·설명·interaction 의미 재설계
- T2 내부의 raw owner source reader 또는 T1 audit 실행
- Layer 3/4 문장 수정, 요약, 번역, fallback, reselection
- absence reason 복원 및 독립 Menu parity 증거 생산
- IrisAltTooltip/IrisTooltipSummary 및 runtime Lua 변경
- 실제 PZ 실행, UI, Alt 입력, wrapping, 시각·성능 검증
- runtime install, package/current runtime pointer 전환, release

Change 0에서만 기존 T1 producer가 기존 D1 output을 읽는다. 이후 T2 generator는 successor handoff만 읽는다. 두 책임을 한 generator에 섞지 않는다.

## 4. Change 0 — S1 표제 입력의 bounded correction

### 4.1 수행 조건과 수정

먼저 current handoff가 이미 요구 형식을 만족하는 successor인지 확인한다. 승인된 두 label로 표제를 완성했다는 기존 successor 근거가 있으면 이 단계 전체를 재실행하지 않는다.

현재 predecessor를 사용하는 경우 이 계획의 선행 보완 범위에서 다음을 수행한다.

1. 기존 T1 S1 producer에서 locale별로 아래 formatting만 적용한다.
2. 기존 T1 display/input contract와 정책 문서에 fixed template를 반영한다.
3. 수정된 contract bundle을 기존 binding 방식으로 연결한다.
4. S1 semantic identity와 source label 값 자체는 바꾸지 않는다.

```text
S1(locale) = "[" + category_surface[locale] + " - " + primary_subcategory_surface[locale] + "]"
```

T2 row schema를 늘리지 않고 완성된 문자열을 기존 localized_surfaces에 전달하는 방식이 기본값이다. 기존 schema로 처리할 수 있는데 component용 별도 입력 체계를 만들지 않는다.

### 4.2 최소 확인

기존 T1 parameterized family 안에서 다음을 확인한다. 새 T1 test file/function은 만들지 않으며 추가 parameter case는 합계 최대 2개다.

- applicable KO/EN 표제가 승인된 두 label과 고정 formatting의 정확한 결합인지
- display-silence에서 S1이 없고 S2~S4가 그대로 유지되는지

동일 확인을 1,406개의 독립 test case로 펼치지 않는다. 실제 candidate 감사에서 전수 data invariant를 한 번 계산한다.

### 4.3 기존 successor lifecycle 재사용

- clean exact subject에서 필요한 D2 relation과 T1 candidate를 기존 route로 재생성한다.
- support 2,280, applicable 1,406 / silence 874와 blocker 0을 유지한다.
- S1 표제 외의 semantic delta가 있으면 이 범위를 넘어 수정하지 않고 원인을 보고한다.
- 기존 T1 fresh installed environment, canonical Run A/Run B/comparator/finalizer 요구를 그대로 충족한다.
- 기존 finalizer의 네 파일을 새 repository-external final root에 발행하고 current T1 route를 successor로 채택한다.
- 과거 handoff를 in-place 편집하거나 기존 receipt를 새 subject에 재결속하지 않는다.

새 T1 lifecycle·검증기·승인 증빙은 만들지 않는다. 이 단계에 필요한 기존 gate는 T2 테스트 예산을 줄인다는 이유로 생략하지 않는다.

표제 보완의 scope를 벗어나는 source 결손, 분류 변경 또는 문장 수정이 필요하면 그 항목만 보고한다. 단순히 이전 계획의 S1 선택지가 미확정이었다는 이유로 다시 owner 결정 절차를 열지 않는다.

## 5. T2 admission과 입력 계약

### 5.1 유일한 의미 입력

```text
subject_binding.json
t2_handoff_input.jsonl
t2_handoff_manifest.json
```

current route와 T1 final closeout은 출처·완료 상태 확인용이며 문장 source가 아니다.

Admission은 다음을 요구한다.

- adopted / complete / complete / OPEN / present인 current T1 handoff
- current locator의 exact root 및 artifact hashes와 실제 bytes의 일치
- subject binding, manifest, input의 일관성
- 2,280 exact case-sensitive FullType의 count 및 ordered-set hash 일치
- duplicate/missing/extra FullType 0
- inherited strict row schema, slot 순서, KO/EN completeness
- S1 보완을 마친 successor binding
- canonical JSONL, valid UTF-8, no file-prefix BOM

T1의 stable row validator와 canonical helpers를 재사용한다. T1 whole audit나 원본 Classification/DVF/QG reader를 호출하지 않는다.

Production admission을 건너뛰는 옵션은 만들지 않는다. 재정렬 fixture는 테스트 안에서만 독립 binding을 가진다.

### 5.2 텍스트 계약

- non-empty/non-whitespace surface
- inherited logical-line 규칙에 따른 CR/LF 금지
- malformed UTF-8/lone surrogate 및 실제 lossless serialization 불가능 거부
- source 문자열 trim, punctuation fix, Unicode normalization, 번역 금지
- 일반 non-ASCII나 유효한 control character의 존재만으로 새 공개 금지 정책을 만들지 않음

문자별 통계·발생 횟수·영향 surface census는 manifest와 테스트 대상에서 제거한다. 대표 escaping fixture로 보존 성질만 확인한다.

### 5.3 omission과 오류

handoff는 emit할 slot만 전달한다. T2는 다음만 기록한다.

```text
present_slots = accepted slots
omitted_slots = SLOT_ORDER - present_slots
```

누락 slot을 legitimate absence, display silence 또는 다른 semantic cause로 재분류하지 않는다. 해당 사유는 T1에 남아 있다.

정상 0줄 row는 explicit empty entry다. Row 누락, malformed schema, 잘못된 locale 또는 handoff에 허용되지 않은 readiness/correction field는 입력 실패다. 실패를 정상 omission으로 바꾸지 않는다.

## 6. 고정 projection과 Lua serialization

### 6.1 Projection

각 FullType에 대해 동일한 selected slot vector로 KO/EN 배열을 생성한다.

```text
S1: successor가 완성한 classification 표제
S2: 승인된 Layer 3 surface
S3: 첫 번째 selected Layer 4 surface
S4: 두 번째 selected Layer 4 surface
```

- 존재하는 slot의 S1→S4 상대 순서를 유지한다.
- T2는 S1 표제를 다시 조립하거나 wrapper를 추가하지 않는다.
- KO/EN role·identity vector와 줄 수가 같아야 한다.
- 모든 emitted logical string은 successor input의 해당 locale surface와 정확히 같아야 한다.
- 4줄 초과·locale 결손·identity mismatch는 전체 generation 실패다.
- 줄을 자르거나 중복 text를 임의로 제거하지 않는다. 서로 다른 selected identity가 같은 문장을 가지더라도 재선택하지 않는다.

### 6.2 Lua shape

```lua
return {
    ["Exact.FullType"] = {
        ko = {
            "...",
        },
        en = {
            "...",
        },
    },
    ["Supported.Empty"] = {
        ko = {},
        en = {},
    },
}
```

Supported-empty와 unsupported lookup을 구분하기 위해 2,280개 key를 모두 유지한다.

### 6.3 Canonical serialization

- exact FullType ordinal ascending
- locale 순서 ko, en
- UTF-8, LF, no BOM, 고정 indentation/trailing comma/final LF
- quote/backslash escaping 및 byte 기반 escape의 단일 표현
- 실행 시각, PID, hostname, 임시 경로를 canonical bytes에서 제외
- Lua에는 완성된 줄 배열만 포함하고 provenance/quality/selection 후보를 넣지 않음

기존 제안의 byte escaping을 재사용한다면 printable ASCII의 quote/backslash 이외는 그대로 쓰고, quote/backslash는 short escape, 나머지는 UTF-8 byte별 3자리 decimal escape로 고정한다. 다른 lossless serialization을 채택할 경우 구현 초기에 contract에 한 가지 방식으로 고정하며 두 출력 모드를 병행하지 않는다.

Escaping의 정확성은 작은 test-local decoder의 round-trip과 기존 Lua syntax 명령으로 확인한다. 이를 별도 production parser 또는 canonical validator로 승격하지 않는다.

단일 Lua 파일을 기본으로 한다. 실제 parser/storage 제약이 확인되지 않으면 chunk/index를 구현하지 않는다. 크기는 기존 manifest의 Lua byte count로 보고하며 별도 크기 판정 체계를 만들지 않는다.

## 7. 금지 표현과 문자열 보존의 분리

Source/final equality는 “문자열을 바꾸지 않았다”는 증거이지 “금지 표현이 없다”는 증거가 아니다.

현재 T1 lexical fixture는 KO 추천/최고, EN recommended/best를 포함하며 audit의 Layer 4 경로에서 사용된다. 이 범위만으로 S1~S4 전체 출력의 금지 표현 검사가 끝났다고 주장하지 않는다.

### 7.1 작은 고정 guard

기존 규칙을 우선 재사용하고 이 작업의 명시적 금지 표현을 T2 physical projection contract에 고정된 literal/pattern 목록으로만 연결한다.

검사 대상은 모든 emitted KO/EN logical line이다.

- KO: 주로 사용된다, 가장 많이 사용된다, 대표적으로 사용된다, 중요한 용도다, 유용하다, 효율적이다, 더 좋다, 덜 좋다, 권장된다, 최적이다, 우선 사용해야 한다 및 기존 추천/최고
- EN: mainly used, primarily used, most commonly used, representative use, important use, useful, efficient, better, worse, recommended, optimal, should prioritize 및 기존 best

기존 규칙의 matching semantics를 보존하고, 새 EN literal은 대소문자를 무시하되 단어 경계를 적용해 다른 단어 내부의 우연한 부분 일치를 피한다. 출력 문자열 자체는 바꾸지 않는다. 검사 규칙과 버전/hash는 T2 contract에 결속한다.

- hit이면 exact FullType/slot/locale/rule을 기존 failure reporting에 기록하고 generation 실패
- 자동 삭제·문장 교체·정상 omission 처리 없음
- 동의어 생성, NLP, 모델 판정, 품질 점수, 추천 순위 없음
- 고정 목록 검사 PASS를 모든 가능한 평가 표현의 semantic 부재 증명으로 확대하지 않음

기존 상류 검사가 동일 subject·모든 emitted slot·동일 규칙을 실제로 검사했다는 evidence가 충분하면 그 결과를 참조할 수 있다. 현재 소수 Layer 4 fixture만으로 이 조건을 충족했다고 간주하지 않는다.

새 scanner framework나 guard 전용 report/schema/test file은 만들지 않는다. positive/negative fixture는 기존 T2 serialization/contract family에 통합한다.

## 8. Provenance와 산출물 최소화

### 8.1 Dataset manifest

최소한 다음만 포함한다.

- schema/generator version 및 projection contract hash
- T1 subject commit/tree와 input/manifest/subject-binding hash
- support count/ordered-set hash
- 0/1/2/3/4줄 분포, generation success/failure 수
- KO/EN projection hash
- Lua file name/byte count/hash
- contract violation 및 고정 금지 표현 hit 수
- FullType별 line provenance

Manifest는 자신의 hash/byte count를 포함하지 않는다. 해당 값은 기존 run receipt/closeout에서 기록한다.

### 8.2 FullType provenance

- generated_empty 또는 generated_nonempty
- KO/EN 줄 수
- present/omitted slot vector
- 각 줄 position/role/semantic identity
- KO/EN source 및 final logical surface hash

선택되지 않은 QG 후보, omission cause, 중복 owner census와 원본 본문을 복제하지 않는다.

### 8.3 Output root

각 T2 Run A/B:

```text
IrisTooltipT2Data.lua
tooltip_t2_projection_manifest.json
run_receipt.json
```

최종 staging:

```text
IrisTooltipT2Data.lua
tooltip_t2_projection_manifest.json
tooltip_t2_closeout.json
```

모든 root는 caller가 지정한 새 repository-external 경로다. repository/runtime/package/PZ auto-load 아래 출력과 기존 성공 root 덮어쓰기를 거부한다.

필요한 임시 output은 이 작업의 external root 안에 둔다. 실패 시 완료 marker를 쓰지 않으며 partial output을 final로 채택하지 않는다.

## 9. 구현 구성과 CLI

### 9.1 작은 T2 domain

기본 구조는 다음으로 제한한다. 단순 helper 때문에 파일을 반드시 분리하지 않는다.

```text
Iris/tooling/src/iris_tooling/domains/tooltip_t2/
    __init__.py
    contract.py
    projection.py
    serialization.py
    cli.py
```

- contract: admission, inherited constraints, fixed lexical guard
- projection: slot→line 및 최소 provenance
- serialization: deterministic Lua/JSON
- cli: build와 좁은 artifact finalization

기존 CLI dispatcher에 두 명령을 연결한다.

```powershell
iris-tooling --repository-root <repo> build tooltip-t2 `
  --handoff-root <current-successor-t1-root> `
  --output-root <external-empty-run-root>

iris-tooling --repository-root <repo> finalize tooltip-t2 `
  --run-a-root <external-run-a-root> `
  --run-b-root <external-run-b-root> `
  --output-root <external-empty-final-root>
```

Production reader와 test reader는 같은 decoding/model/serialization 경로를 사용하되 fixture용 admission bypass를 CLI에 공개하지 않는다.

### 9.2 Finalization

- Run A/B의 T1 accepted input binding 일치
- T2 implementation subject 및 contract/generator binding 일치
- violation 0, 2,280 full coverage
- Lua/manifest bytes 및 hashes 일치
- final root external/empty
- 검증된 Run A bytes를 복사하고 closeout을 마지막에 기록

artifact equality만으로 focused tests, Lua syntax 또는 full gate 통과를 추론하지 않는다. 전체 complete는 §12의 필수 검증이 성공한 뒤에만 기록한다.

검증 명령·exit·subject/artifact hash는 기존 run receipt/closeout 또는 최종 실행 보고 한 곳에 결속한다. Finalizer가 전체 machine complete를 발행한다면 이 선행 결과를 명시적 completion metadata로 받아야 한다. 누락되면 artifact 비교 성공만으로 complete를 쓰지 않는다.

새 증명 파일 묶음이나 검증 결과를 재검증하는 독립 도구는 만들지 않는다.

## 10. 기존 repository gate와 environment 연결

### 10.1 T2 test-source 등록

기존 full gate는 unclassified tracked test source를 fail 처리한다. 다음 T2 test file을 실제로 추가하는 경우 각각 기존 explicit_dedicated_route_sources에 등록한다.

```text
Iris/tooling/tests/test_tooltip_t2_projection.py
Iris/tooling/tests/test_tooltip_t2_serialization.py
Iris/tooling/tests/test_tooltip_t2_cli.py
```

등록 owner는 다음 기존 파일이다.

```text
Iris/validation/clean_checkout/contracts/full_repository_gate.json
```

- 기존 not_applicable_dedicated_route 방식 사용
- 실제 존재하는 파일만 등록
- mandatory denominator, taxonomy와 unclassified_source_policy 유지
- T2 focused command가 해당 검증을 소유함을 명시
- 이 등록을 이유로 같은 T2 suite를 full gate에서도 중복 실행하지 않음

### 10.2 Fresh installed environment binding

새 wheel을 만들기만 해서는 canonical gate가 새 environment receipt를 받아들이지 않는다.

기존 경로를 사용해 다음을 함께 처리한다.

1. clean implementation에서 fresh wheel build/install
2. 기존 environment receipt 형식으로 정확한 package tree/wheel/installed set 결속
3. immutable environment successor record 발행
4. 기존 responsibility_refactor_environment_current.json을 successor로 연결
5. CLI에 전달한 receipt path/hash가 locator의 record와 정확히 같은지 확인
6. final machine commit/tree 확정 후 모든 검증을 그 subject에 결속

환경 metadata를 기록하는 과정에서 source package tree가 바뀌지 않았다면 wheel을 반복 build하지 않는다. 바뀌었으면 이전 environment를 새 package의 증거로 재사용하지 않는다.

기존 record/receipt를 덮어쓰거나 environment check를 완화하지 않는다. 위 절차는 기존 authority 사용이며 새 환경 관리 시스템이 아니다.

### 10.3 Subject 운용

- 일반 working tree의 사용자 변경은 보존하고 clean isolated subject에서 실행한다.
- T1 successor subject와 T2 implementation subject는 각각 기록하며 서로 바꿔 쓰지 않는다.
- T2 Run A/B, installed CLI, focused tests, canonical regression은 동일 T2 machine subject에 결속한다.
- 후속 문서-only carrier는 machine subject/output hash를 참조하며 검증 결과를 새 subject로 재해석하지 않는다.
- same-subject·same-purpose의 기존 성공 evidence가 있으면 재사용할 수 있지만, T1 gate라는 이유만으로 다른 subject의 T2 gate를 대체하지 않는다.

## 11. 변경 가능 경로

이 목록은 허용 범위이지 모든 파일을 반드시 수정하라는 요구가 아니다.

### S1 선행 보완에 한함

- Iris/tooling/src/iris_tooling/domains/tooltip_t1/audit.py — S1 formatting
- Iris/tooling/src/iris_tooling/domains/tooltip_t1/contract.py — template contract 검사에 필요한 경우
- Iris/_docs/authority/tooltip_t1/tooltip_display_contract.json
- Iris/_docs/authority/tooltip_t1/layer2_tooltip_input_contract.json
- Iris/_docs/authority/tooltip_t1/tooltip_t1_decision_contract.json — 기존 bundle rebind에 필요한 부분
- Iris/tooling/tests/test_tooltip_t1_contract.py
- Iris/tooling/tests/test_tooltip_t1_projection.py
- Iris/tooling/tests/test_tooltip_t1_audit.py
- docs/iris_tooltip_t1_display_contract_policy.md

D1 source/owner output과 T1 row schema는 수정하지 않는 것이 기본값이다.

### T2 구현·등록

- Iris/tooling/src/iris_tooling/__main__.py
- §9의 tooltip_t2 domain 파일
- §10.1의 T2 test files
- Iris/_docs/authority/tooltip_t2/tooltip_t2_static_projection_contract.json
- Iris/_docs/authority/tooltip_t2/tooltip_t2_projection_manifest.schema.json
- Iris/validation/clean_checkout/contracts/full_repository_gate.json

### 기존 environment·navigation·문서

- Iris/validation/clean_checkout/authority/responsibility_refactor_environment_current.json
- 같은 디렉터리의 기존 형식 immutable environment successor record
- Iris/_docs/authority/iris_current_authority_manifest.json
- Iris/_docs/authority/iris_current_route_index.json
- Iris/build/ENTRYPOINTS.md
- docs/DECISIONS.md
- docs/ARCHITECTURE.md
- docs/ROADMAP.md
- 이 계획서

### 읽기 전용 보호 범위

- Iris/media/lua/**
- Iris/build/package/**
- D1/DVF/QG 의미 산출물
- 이미 발행된 T1 final root와 historical receipts
- 일반 작업 트리의 관련 없는 사용자 변경

외부 파일 접근은 명시된 predecessor final root, current route가 가리키는 required handoff/receipt, caller가 지정한 이 작업의 external work/environment/staging root로 제한한다. 다른 사용자 디렉터리를 탐색하지 않는다.

## 12. 최소 테스트 및 실행 검증

### 12.1 신규 테스트 예산

```text
T2 new test files                    <= 3
T2 new top-level test functions      <= 5
T2 collected independent cases      <= 20
T1 new test files/functions           = 0
T1 added parameter cases            <= 2, only if S1 correction is executed
new standalone validation scripts    = 0
```

기본 목표는 T2 약 16개 사례다. 20개는 채워야 할 목표가 아니라 상한이다. 같은 failure class의 JSON field별·locale별·slot별 조합을 전부 펼치지 않는다.

실제 독립 입력/실패 사례 기준으로 예산을 센다. 함수나 loop 하나 안에 다수 subtest를 숨겨 수만 줄이지 않는다. Whole-dataset exact-set/line invariant 순회는 test case 증식이 아니라 실제 산출물 검사다.

다섯 함수군 안에서 다음을 묶는다.

| 함수군 | 최소 coverage |
|---|---|
| Admission | valid input; subject/hash/state 오류; exact-set/case 손상; schema/locale 오류 |
| Projection | 작은 mixed dataset의 0~4줄, omission, 동일 KO/EN role·identity, successor S1 원문 보존 |
| Serialization/guard | UTF-8·quote·backslash·대표 control round-trip, invalid encoding/line 거부, 고정 금지 표현 hit/허용 대조 |
| Reader-order | 같은 fixture row 집합의 original/reversed/seeded-shuffled 파일→동일 Lua/projection provenance |
| CLI/finalization | success, external/nonempty root 거부, failure atomicity, output tamper 및 subject mismatch 거부 |

Coverage가 겹치면 기존 case에 통합한다. Test가 실제 결함을 드러내면 이를 없애지 말고 중복 case를 제거해 예산을 맞춘다. 예산을 늘려야만 다룰 수 있는 새로운 위험이 발견되면 필수 이유와 최소 추가 범위를 보고한다.

### 12.2 Focused test 실행

S1을 수정한 경우 기존 T1 3-file focused command를 선행 보완 완료 후 clean subject에서 한 번 실행한다. 기존 함수군에 최대 2개 case만 추가하며 D1/D3/D4/D5 suite 전체를 별도로 실행하지 않는다.

```powershell
uv run --project .\Iris\tooling python -B -m pytest `
  .\Iris\tooling\tests\test_tooltip_t1_contract.py `
  .\Iris\tooling\tests\test_tooltip_t1_projection.py `
  .\Iris\tooling\tests\test_tooltip_t1_audit.py `
  -q
```

T2 focused command:

```powershell
uv run --project .\Iris\tooling python -B -m pytest `
  .\Iris\tooling\tests\test_tooltip_t2_projection.py `
  .\Iris\tooling\tests\test_tooltip_t2_serialization.py `
  .\Iris\tooling\tests\test_tooltip_t2_cli.py `
  -q
```

T2 구현이 끝나고 clean exact subject가 확정된 뒤 한 번 실행한다. 테스트 파일을 합친 경우 해당 exact file list만 command와 dedicated registration에서 같이 조정한다.

계획에 없는 중간 테스트는 실행하지 않는다. 실패 후 수정했다면 관련 실패 범위만 확인하고 필요한 최종 command를 재실행한다. 정상 통과한 suite의 confidence 목적 반복은 금지한다.

### 12.3 순서 독립성은 한 함수군으로 검증

Production과 같은 reader→model→serializer 경로를 fixture 파일에 적용한다.

- original/reversed/고정 seed shuffled의 exact row 집합은 동일
- fixture별 물리적 input hash는 그 bytes에 맞게 계산
- Lua bytes와 line/provenance projection은 동일
- input-file hash가 다른 전체 manifest의 byte equality를 요구하지 않음
- slot order tamper를 정상 permutation으로 취급하지 않음
- production handoff나 current route는 수정하지 않음

이 검사는 focused suite 안에서 수행한다. 별도 model-only permutation test나 별도 permutation command/report를 추가하지 않는다.

### 12.4 T2 필수 실제 실행

다음은 실제 완성 산출물의 조건이므로 유지한다.

1. fresh wheel/install 및 기존 environment binding: exact package subject당 1회
2. installed inspect current: 1회
3. installed T2 generation Run A/Run B: 각 1회
4. Run A의 generated Lua에 기존 syntax checker: 1회
5. T2 exact subject의 기존 canonical repository full gate: 1회
6. T2 narrow finalizer: 1회
7. final candidate-byte equality와 필수 파일 확인: finalizer에서 1회
8. final diff/protected-path 확인: 1회

T2 Run A/B는 두 번의 **데이터 생성**이다. Canonical full gate를 두 번 실행하라는 뜻이 아니다. Full-gate 테스트를 같은 목적의 별도 suite로 다시 실행하지 않는다.

Change 0을 실제 수행하면 T1 successor에 필요한 기존 canonical A/B/comparator는 별도 필수 경로다. 이미 채택된 올바른 successor를 사용하면 그 경로와 T1 focused command는 모두 생략한다.

### 12.5 Lua syntax

기존 checker가 실제 external generated Lua를 검사하게 한다.

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\check_lua_syntax.ps1 `
  -Roots <repository-relative-external-run-a-root>
```

검사 전 path resolution과 실제 대상 Lua 파일만 확인한다. No-files, luac missing 또는 다른 runtime 파일 검사 결과를 PASS로 사용하지 않는다.

Final/Run B bytes가 Run A와 같으면 Lua syntax를 다시 실행하지 않는다. 실제 PZ require/load는 T3이며 T2의 필수 테스트가 아니다.

### 12.6 Canonical full gate

```powershell
iris-tooling --repository-root <repo> validate full `
  --commit <exact-t2-machine-commit> `
  --claim-id <t2-claim-id> `
  --environment-receipt <current-bound-external-environment-receipt> `
  --work-root <external-empty-work-root> `
  --result-root <external-empty-result-root> `
  --orchestration-receipt <external-new-orchestration-receipt>
```

기존 launcher의 경로 길이·clean-subject·environment 요구를 미리 지키고 known-invalid 환경으로 실패 실행을 반복하지 않는다.

### 12.7 감축·재실행 규칙

- 별도 문자 census, exhaustive escape matrix, owner별 중복 audit, 중복 full-suite 금지
- runtime Lua 미변경이므로 Browser harness와 전체 runtime syntax 재검사는 추가하지 않음
- 문서-only carrier 수정에는 코드 test 재실행 없음
- 원인·영향이 없는 이미 성공한 명령은 반복하지 않음
- machine code/contract/input 변경 시 해당 evidence만 무효화하고 필요한 경로 재실행
- 정확한 relevant command exit 0만 PASS
- 장기 실행은 주기적으로 상태를 확인하고 비정상 장기 실행/무한 루프 징후가 있으면 중단
- 일회성 보조 검사를 canonical validator나 새 authority로 승격하지 않음

## 13. 완료·문서화·권한 경계

T2의 완료는 static machine staging 완료다. Required checks와 final bytes가 검증되면 이 범위에서 complete로 닫는다.

- finalizer가 runtime/current governance 문서를 자동 수정하지 않음
- 구현 계획이 채택된 범위의 ENTRYPOINTS/contract/완료 사실 문서화는 수행
- T1 successor current 채택과 environment successor 연결은 각각 Change 0/§10의 명시된 범위
- T2 staging locator를 기록하더라도 runtime adoption으로 표시하지 않음
- 별도 조직·승인 파일·미확정 review gate를 만들지 않음
- 실제 적용 규정에 명시된 추가 review가 있으면 그 조항과 대상만 적용; 단순히 필요 여부를 확정하지 않았다는 이유로 무기한 차단하지 않음
- 사용자의 실행 프롬프트에 owner 사전 승인이 있으면 해당 gate에 적용; 플랫폼 보안 확인은 별개

기존 EXECUTION_CONTRACT의 validated / unvalidated_but_in_scope / out_of_scope를 한 closeout에 기록한다. 수행하지 않은 봉인, runtime 또는 release 채택은 주장하지 않는다. 별도의 승인 작업을 static staging complete의 숨은 필수 조건으로 만들지 않는다.

## 14. 실패·복구

- admission 실패: final staging 없음, exact 원인 보고
- malformed input/금지 표현: 문자열 수정 없이 실패, 해당 upstream 문제 보고
- implementation defect: T2 범위 내 최소 수정 후 영향 있는 검증만 재실행
- S1 이외의 owner semantic 변경 필요: 이 계획에서 자동 확장하지 않음
- partial root: completion marker를 쓰지 않고 final로 채택하지 않음
- 성공 root: 덮어쓰지 않고 corrected subject의 새 external root 사용
- historical T1 input/receipt와 unrelated user changes 보존
- documentation/reference만 바뀌면 bytes를 재생성하지 않고 참조만 교정

필수 검증이 남았으면 implemented_only/partial, 외부 필수 입력이 없으면 blocked로 보고한다. 실패를 숨기거나 전체 complete로 확대하지 않는다.

## 15. 완료 조건

### 입력

- 요구한 S1 표제를 담은 current T1 successor handoff
- strict subject/input/manifest binding PASS
- support exact 2,280, duplicate/missing/extra 0
- T1 progression OPEN 및 production handoff present

### 생성

- 모든 FullType에 explicit KO/EN 0~4줄
- 동일 KO/EN role·identity vector
- S1~S4 상대 순서와 정상 omission 보존
- 모든 emitted surface가 accepted handoff의 해당 source와 동일
- 새 문장/번역/요약/fallback/reselection/truncation 0
- untraceable line, blank line, embedded newline 0
- 고정 금지 표현 규칙의 hit 0; semantic 품질 재인증 주장 없음
- omitted-slot cause 추론 0

### 결정성과 실행

- reader-inclusive fixture permutation PASS
- T2 Run A/B Lua 및 manifest byte equality
- focused test exact exit 0
- fresh installed CLI와 canonical full gate exit 0
- generated Lua syntax exit 0
- finalizer exit 0 및 validated candidate/final byte equality
- runtime/package/T1 역사적 artifact의 비허용 변경 0

### 전달

- final external root에 Lua, manifest, closeout의 세 파일
- exact T2 machine subject, T1 input binding, output hashes 기록
- validation ceiling 명시
- T3가 FullType과 locale만으로 완성된 배열을 얻을 수 있음
- 실제 PZ/runtime/visual/release 완료를 주장하지 않음

최종 보고는 위 결과와 실제 실행 명령·exit·필요한 hash를 기존 closeout/실행 보고에 모아 제시한다. 별도의 proof package를 추가하지 않는다.

## Execution location

User prompt preauthorizes document owner gates. The clean subject is on `codex/iris-tooltip-t2` in `C:/Users/MW/Downloads/coding/PZ-t2/w`; caller-selected external environment/work/staging roots are under `C:/Users/MW/Downloads/coding/PZ-t2/`. Unrelated working-tree changes and predecessor artifacts remain untouched.

### Change 0 execution

- Successor machine subject: `60796744ffb889477161d243a1443c9de57d49b0` / tree `1182c6fbffc82f3d6aed3516fa0f1918ee60b248`.
- T1 focused command (§12.2): exit `0`, `95 passed`.
- Installed D2 materialization and strict T1 candidate: exit `0`; support `2,280`, applicable `1,406`, silence `874`, correction `0`, progression `OPEN`.
- One candidate/predecessor comparison: exact S1 title `1,406`, classification identity and non-S1 delta `0`; no standalone validator or proof artifact added.
- Canonical A/B: exit `0` each, `211 passed, 109 subtests passed` each; orchestration receipts `C:/Users/MW/Downloads/coding/PZ2/oa/receipt.json` and `C:/Users/MW/Downloads/coding/PZ2/ob/receipt.json`. Existing comparator exit `0`: `C:/Users/MW/Downloads/coding/PZ2/compare/compare_receipt.json`.
- Existing T1 finalizer exit `0`; adopted final root `C:/Users/MW/Downloads/coding/PZ-t2/t1-final`, closeout SHA-256 `a5837d98201b100ca27e2de3940e33d9e4f07cade723fd8e71b25d5a8cbd9e4d`. Historical predecessor untouched.
- Earlier attempts remain failed: PowerShell module lookup (exit 1), checkout path budget (exit 2), DVF temporary directory path length (exit 1, 211 passed/one failed subtest), and unavailable C:/ output permission (exit 125 before tests). No validator or OS permission policy was weakened. Short caller-selected work/results now use `C:/Users/MW/Downloads/coding/PZ2/`; child Windows PowerShell uses its system module directory.
- Fresh wheel source `ee99c3f6` and existing environment writer produced `responsibility_refactor_environment_tooltip_t2_ee99c3f6.json`; environment receipt `C:/Users/MW/Downloads/coding/PZ-t2/receipt/environment_receipt.json` SHA-256 `dcd952d87931a4e1a9fb0057889949f954ca73237a55e328c1c002e669407e35`. Package tree is unchanged by this adoption, so no wheel rebuild is required.
