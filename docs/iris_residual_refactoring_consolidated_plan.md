# Iris 잔여 리팩토링 종합 실행 계획

> 상태: Third Revised Draft — 운영 보강 및 N1~N5 반영
>
> 기준 시점: 2026-08-03
>
> 양식: [`PLAN_TEMPLATE.md`](PLAN_TEMPLATE.md)
>
> 선행 계획: [`iris_core_refactoring_consolidated_plan.md`](iris_core_refactoring_consolidated_plan.md)
>
> 입력안: `Iris 리팩토링 후보 종합 제안`
>
> 수정 근거: `Iris 잔여 리팩토링 종합 실행 계획 — 최종 종합 검토`

## 1. Objective

이미 완료된 Iris 코어 리팩토링의 계약을 유지하면서, 코드베이스에서 실제로 확인된 잔여 구조 부채를 다음 두 트랙으로 정리하고 단계적으로 해소한다.

1. Lua 런타임 트랙은 분류 체계 중복, Browser 대표 항목의 비결정성, 공개 API의 동결 배열 노출, Wiki 단위 표현, Tooltip 번역 경계, 불필요한 디버그 문자열 생성을 작고 검증 가능한 변경으로 다룬다.
2. Python 빌드 도구 트랙은 `Iris/build/description/v2`의 실행 경로와 산출물 계약을 먼저 목록화한 뒤, 패키지·import 기반과 공통 I/O의 안전한 최소 단위를 파일럿으로 확립한다. 이후 도메인별 분리는 별도 승인 게이트를 통과한 묶음에만 적용한다.

이 계획의 핵심 성공 조건은 파일 수 감소가 아니라 다음과 같다.

- 동일 입력에 대한 런타임 표시와 빌드 산출물의 의미·바이트 계약이 유지된다.
- Browser의 대표 항목 선택이 입력 순서와 Lua `pairs()` 순회 순서에 의존하지 않는다.
- 공개 API 호출자가 내부 동결 데이터를 변경할 수 없다.
- Python 도구를 clean checkout에서 문서화된 방식으로 import·실행할 수 있다.
- 현재·과거·진단 검증 경로와 봉인 증거의 역할이 섞이지 않는다.
- 후속 분리 작업의 허용 범위와 중단 조건이 명시된다.

이 문서는 선행 계획을 대체하거나 완료 판정을 다시 여는 문서가 아니다. [`DECISIONS.md`](DECISIONS.md)와 [`ROADMAP.md`](ROADMAP.md)에 기록된 2026-08-03 Iris 코어 리팩토링 완료 상태를 기준선으로 삼는 후속 계획이다.

이전 검토의 taxonomy ownership, closure 적격성, Tooltip 줄 수, nested mutation 지적은 해소 상태를 유지한다. 후속 종합 검토의 현재 Critical은 다음 위치에서 닫는다.

| 후속 종합 검토 Critical | 해소 위치 |
|---|---|
| C-01 receipt와 Python interpreter 불일치 | Section 7의 receipt-bound `-B -s` full-gate 명령 |
| C-02 diagnostic raw nonzero와 advisory 충돌 | Change 7 및 Section 7의 raw report + disposition adapter |
| C-03 필수 수동 검증의 completion 연결 누락 | Section 7 manual report row와 Section 12 필수 증거 |

후속 운영·일관성 피드백은 다음 위치에서 닫는다.

| 후속 항목 | 해소 위치 |
|---|---|
| Full-gate 직전 clean exact subject 확인 | Section 7의 `HEAD == targetCommit`·working-tree clean preflight와 binding report 규약 |
| Diagnostic traceback fingerprint 안정화 | Change 7의 path/slash/line-ending/temporary-name 정규화 순서와 동치·비동치 fixture |
| Manual report case class 및 N1 범주 오류 | Section 7의 `runtime_ui`·`operator_contract` class별 metadata·case·완료 판정 |
| N2 planned Python test 목록 불일치 | Section 5 Tests와 Section 7 Validation Assets의 동일한 다섯 test 목록 |
| N3 validation support asset 누락 | Section 5 Tests와 Section 7 Validation Assets의 `report_inventory.py`·`write_evidence_index.py` 등록 |
| N4 `IrisModuleBootstrap.lua` 조건부 상태 누락 | Section 7 Conditional item의 per-file `application_status` 행 |
| N5 Historical route 축에 전체 partial 규칙 혼입 | Section 7 축 셀은 route 상태만 유지하고 Section 12가 missing dependency의 전체 `partial`을 소유 |

## 2. Scope

### In Scope

#### A. 기준선 및 계약 인벤토리

- 현재 실행되는 Python 진입점, module 실행 경로, bare import 호환 경로, subprocess 호출 관계를 목록화한다.
- JSON·JSONL·텍스트 직렬화의 정렬, 들여쓰기, 개행, 인코딩, BOM, 원자적 교체, 누락 파일 처리, 해시 계산 차이를 계약 행렬로 기록한다.
- Python 도구를 `active`, `legacy-required`, `completed-but-reproducible`, `historical`, `diagnostic`, `test-only`, `unknown` 역할로 분류하되, 역할 미확정 파일을 이동하거나 삭제하지 않는다.
- 현재 코어 12개 모듈과 허용 tooling 4개 경계를 구현 전후에 확인한다.
- 런타임 출력과 공개 API의 현재 동작을 characterization test로 고정한다.

#### B. Lua 런타임의 국소 리팩토링

- classification/taxonomy 의미 권위와 presentation-order projection을 분리하고, Browser UI 밖의 중립 projection에서 표시 순서만 공유한다.
- Browser의 display-name 그룹, 대표 항목, recipe 연결 여부를 결정론적으로 계산하고 캐시 수명과 함께 관리한다.
- `Tags`, `UseCases` 등 공개 API에서 배열·목록을 copy-on-read로 반환한다.
- Wiki 수치 표현을 명시적 포맷터와 단위 프로필로 분리한다.
- Tooltip의 사실 조회와 번역·표시 결정을 분리하되 기존 hot path와 현재 네 개 삽입 지점에서 파생되는 줄 수 조합을 유지한다.
- debug 비활성 상태에서 비싼 문자열 조합과 순회를 생략한다.

#### C. Python 빌드 도구의 기반 정비와 파일럿

- 현재의 혼합된 `tools.build.*`·bare import·직접 스크립트 실행 계약을 깨지 않는 패키지/import 전략을 확정한다.
- 서로 다른 직렬화 계약을 하나로 합치지 않고, 계약별 작은 helper 또는 기존 owner 내부 helper로 중복을 줄인다.
- `public_text_quality_acceptance.py`, `export_dvf_3_3_lua_bridge.py`, `_dvf_3_3_vnext_common.py`, compose 계열을 대상으로 의존성·직렬화·오류 계약을 분석한다.
- 새 stem을 만들지 않는 in-place 파일럿을 먼저 수행하고, closure 외부 비-hub 후보가 owner 승인을 받은 경우에만 leaf-first extraction 한 묶음을 수행한다. 기존 CLI·import 이름은 adapter로 유지한다.
- UTF-8 BOM 정규화는 hash 소비자 조사가 통과한 경우에만 의미 변경과 분리된 전용 변경 묶음으로 수행한다.

#### D. 증거물과 검증 경로의 역할 명시

- 새로 생성하는 증거물에 `current`, `historical`, `diagnostic` 역할과 manifest를 부여한다.
- 기존 staging·sealed evidence는 보존 우선 정책을 적용한다.
- subprocess는 실패·환경·권위 경계를 담당하는 경우 유지하고, 동일 프로세스 함수 호출로 바꿀 후보는 별도 증거로 판정한다.

### Explicitly Out of Scope

- `dvf_3_3_registry_authority_canonical_closure.py`의 대규모 분해
- DVF System, Artifact Registry, Publish Boundary의 권위 재설계 또는 통합
- 생성된 Lua chunk나 `IrisLayer3Data.lua`의 수동 편집
- staging, sealed evidence, historical artifact의 삭제·이동·tracking 해제
- 참조 검색만을 근거로 한 Python 스크립트 삭제
- 모든 subprocess 호출의 일괄 함수 호출 전환
- 모든 Python 도구의 일괄 패키지 이동 또는 전면 재작성
- Lua 공개 API 이름, CLI 옵션, exit code, 오류 유형의 의도적 변경
- Browser의 이미 구현된 build-state 모델 재설계
- `Iris/media/lua/client/Pulse/Iris/Logic/IrisDesc` 호환 wrapper 제거
- 외부 모드 정규화와 미지원 외부 데이터의 의미 추론
- packaging/release 자체의 정책 변경
- core 12개 및 allowed tooling 4개 정원의 확장
- closure owner 판정 없는 새 Python module stem 추가
- Tooltip에 새로운 명시적 줄 수 상한 또는 절단 규칙 도입
- evidence용 `current` pointer를 Artifact Registry, seal, cutover 또는 다른 authority pointer로 승격

## 3. Non-Goals

- 리팩토링을 이유로 게임 데이터의 의미를 보정하거나 추천·평가·추론을 추가하지 않는다.
- 파일 수, 모듈 수, 함수 길이를 단독 성공 지표로 사용하지 않는다.
- 공통 helper를 만들기 위해 서로 다른 JSON 바이트 계약을 강제로 통일하지 않는다.
- 현재 검증을 통과한다는 이유로 historical reproduction 경로를 축소하지 않는다.
- 과거 문서의 수치와 현재 checkout의 수치가 다를 때 과거 수치를 최신 사실로 덮어쓰지 않는다.
- Wiki 단위가 불명확한 상태에서 사용자 표시값을 임의로 환산하지 않는다.
- debug 최적화를 이유로 warning·error·실패 증거를 누락하지 않는다.
- 런타임 hot path에서 전체 Detail ViewModel을 생성하도록 Tooltip을 확장하지 않는다.
- 현재 성공 경로에서 파생되는 3~4줄과 API 로드 실패 경로의 2줄을 “최대 4줄”이라는 새 강제 계약으로 바꾸지 않는다.

## 4. Assumptions

### 4.1 권위와 기준선

- [`Philosophy.md`](Philosophy.md)가 최상위 설계 권위이다. Iris는 오프라인 정규화·컴파일 결과를 Lua 런타임에서 표시하는 spoke이며 다른 spoke의 내부 구현에 의존하지 않는다.
- [`DECISIONS.md`](DECISIONS.md), [`ARCHITECTURE.md`](ARCHITECTURE.md), [`ROADMAP.md`](ROADMAP.md)의 최신 판정이 이 계획보다 우선한다.
- 현재 Iris 코어 리팩토링 Change 1~6과 closeout은 완료 상태이다. Change 7 build-tool decomposition은 `deferred_by_design`, Change 8 cleanup은 `no_op`으로 닫혀 있으므로 새 구현은 별도 후속 승인과 기준선을 사용한다.
- `Iris/build/package/Iris`는 읽기 전용 projection이며 source authority가 아니다.
- 생성 산출물과 봉인 증거는 source와 다른 수명주기를 가진다.

### 4.2 2026-08-03 코드베이스 조사 기준점

다음 값은 계획 작성 중 얻은 **예비 정적 감사값**이며 closeout authority가 아니다. Change 1에서 build closure 밖의 validation support인 `Iris/validation/residual_refactor/report_inventory.py`를 추가하고 아래 단일 명령으로 검색 root, 제외 규칙, 줄 수 정의, regex를 manifest에 함께 기록해 재측정한다.

```powershell
uv run python -B Iris\validation\residual_refactor\report_inventory.py `
  --v2-root Iris\build\description\v2 `
  --build-tools-root Iris\build\description\v2\tools\build `
  --closure Iris\_docs\round3\round3_active_core_closure.json `
  --out Iris\_docs\refactor\residual_refactor\phase0_inventory.json
```

보고서는 재귀 전체와 root-direct를 분리하고, Python 코드량은 blank/comment를 포함한 physical line으로 정의한다. `tests`는 v2 전체 수치에 포함되는지 별도 boolean으로, `staging`은 코드 검색에서 제외하되 evidence inventory에는 포함되는지 별도 boolean으로 기록한다. `subprocess` 사용 파일은 AST의 `import subprocess`, `from subprocess import ...`, alias 호출을 기준으로 판정한다. 경로 계산과 유사 helper는 보고서에 사용한 AST node 종류와 함수명 집합을 저장한다.

| 항목 | 예비 감사값 | 확인된 측정 기준값 | Change 1 disposition |
|---|---:|---:|---|
| `tools/build`의 Python 파일 | 재귀 496개, root-direct 483개 | 동일 | 동일 기준 재측정 후 authoritative inventory에 기록 |
| `tools/build`의 Python line | 비공백 220,214줄 | physical 240,005줄 | 두 값을 별도 field로 기록하고 혼합 금지 |
| `sys.path.insert/append` 사용 파일 | `tools/build` 151개, v2 전체 357개 | Phase 0 재측정 대상 | AST 및 text 결과를 함께 기록 |
| 루트/부모 경로 계산 | 304개 파일, 430회 | Phase 0 재측정 대상 | AST 기준 확정 전에는 파일럿 분모로 사용 금지 |
| JSON/JSONL/text/hash 유사 helper 정의 | 219개 파일, 623개 정의 | Phase 0 재측정 대상 | 함수명 집합과 계약 ID를 함께 재생성 |
| `argparse` 사용 파일 | 273개 | Phase 0 재측정 대상 | parser 생성과 import-only를 구분 |
| `subprocess` 사용 파일 | 49개 | Phase 0 재측정 대상 | 위 AST 판정 기준으로 재생성 |
| UTF-8 BOM 파일 | 16개 | Phase 0 재측정 대상 | 파일 path와 Git tracking 상태를 함께 기록 |
| registry giant line | 비공백 12,798줄 | physical 13,219줄 | 두 값을 기록하되 본 계획에서 분해 제외 |
| 현재 closure | core 12개, allowed tooling 4개 | manifest 확인값 동일 | `round3_active_core_closure.json`에서 owner·확장 규칙까지 기록 |

재현 도구가 아직 존재하지 않거나 해당 도구의 contract test가 실패하면 위 수치는 `unreproduced_preliminary`로 남기며, 수치 자체를 구현 성공 근거로 사용하지 않는다.

### 4.3 확인된 계약 차이

- `_dvf_3_3_vnext_common.write_json`은 key 정렬, 후행 개행, `newline="\n"`을 사용하고, JSONL 쓰기는 Windows 교체 실패 재시도와 임시 파일 교체를 포함한다.
- `export_dvf_3_3_lua_bridge.dump_json`은 key를 정렬하지 않고 후행 개행도 추가하지 않으며 파일 open의 `newline`을 지정하지 않아 Windows 개행 변환 가능성을 계약에 포함해야 한다.
- `compose_layer3_io.write_jsonl`은 `ensure_ascii=False`를 사용하지만 key 정렬과 file-open `newline`을 강제하지 않아 Windows의 `\r\n` 가능성을 별도 축으로 가진다.
- `public_text_quality_acceptance.sha256_file`은 long-path-safe 검증과 전용 오류 계약을 가진다.
- `Iris/build/tools/common/io.py`는 `Iris/build/description/v2/tools/common`과 다른 package tree에 속한다. 동일한 `tools.common` 이름을 가정하면 실행 위치에 따른 namespace 충돌 위험이 있다.

따라서 “공통 I/O”는 단일 범용 함수가 아니라 **동일 계약을 공유하는 호출자 묶음**을 뜻한다. 계약 ID는 최소한 encoding, BOM, `ensure_ascii`, key order, indentation, trailing newline, file-open newline conversion, atomicity, retry, missing-file, error type, hash chunking을 포함한다. 계약이 다르면 helper도 분리한다.

### 4.4 입력안의 미결정 사항에 대한 본 계획의 판정

| 입력안 쟁점 | 본 계획의 판정 |
|---|---|
| D1. 런타임과 Python 중 무엇을 먼저 할지 | Phase 0 인벤토리를 먼저 수행한 뒤 mutation은 Lua의 작고 확인 가능한 잔여 항목부터 한다. Python 분석은 Phase 0에 포함하지만 구조 변경은 closure·import 게이트 이후에 한다. |
| D2. registry giant 포함 여부 | `deferred_by_design`을 유지한다. 별도 승인 계획 없이는 분해하지 않는다. |
| D3. staging 정책 | 기존 자료는 보존한다. 새 증거물에만 역할 manifest와 불변 bundle 규칙을 적용한다. |
| D4. 참조 없는 스크립트 | `unknown` 또는 `completed-but-reproducible`로 분류할 수 있으나 본 계획에서 이동·삭제하지 않는다. |
| D5. subprocess 전환 | 기본값은 유지이다. 동일 인터프리터 leaf이며 환경·실패·권위 경계가 없다는 증거가 있는 호출만 후보가 된다. |

### 4.5 실행 자격과 판정 상태

- Change 1은 **production read-only inspection + validation asset authoring + no production mutation** 범위로 즉시 수행할 수 있다.
- Changes 2~4C의 production mutation은 Change 1의 runtime baseline, supported API baseline, protected surface baseline, evidence-role schema가 모두 `passed`이고 각 Change의 선행조건이 충족된 뒤에만 시작한다.
- Change 5의 module extraction은 closure 슬롯 owner 판정과 적격 후보 선정이 모두 `passed`이기 전에는 시작하지 않는다.
- Change 6C 도메인 이동은 `Change 5.validation_status=passed`이고 exact 대상과 owner가 승인된 뒤에만 수행한다.
- 적용 여부와 검증 결과를 한 field에 혼합하지 않는다.
  - `application_status = applied | deferred | not_applicable`
  - `validation_status = passed | failed | blocked | not_applicable`
- `deferred`는 적용 상태일 뿐 검증 성공이 아니다. 예를 들어 Change 6B가 보류되면 `application_status=deferred`, `validation_status=not_applicable`로 기록한다.
- 필수 축의 `failed|blocked`는 전체 `complete`를 금지한다. 조건부 축의 `not_applicable`은 근거와 owner를 함께 기록한다.

## 5. Repository Areas Affected

### Code

예상 수정 영역은 다음과 같다. 실제 파일 목록은 각 변경의 사전 인벤토리에서 고정한다.

- `Iris/media/lua/client/Iris/UI/Browser/IrisBrowserCategoryIndex.lua`
- `Iris/media/lua/client/Iris/UI/Browser/IrisBrowserVariantIndex.lua`
- `Iris/media/lua/client/Iris/UI/Browser/IrisBrowserData.lua`
- `Iris/media/lua/client/Iris/Logic/CategoryPresentationOrder.lua` (planned neutral projection)
- `Iris/media/lua/client/Iris/Logic/IrisDesc/Ordering.lua`
- `Iris/media/lua/client/Iris/API/Tags.lua`
- `Iris/media/lua/client/Iris/API/UseCases.lua`
- `Iris/media/lua/client/Iris/UI/Wiki/IrisWikiSections.lua`
- `Iris/media/lua/client/Iris/UI/Tooltip/IrisTooltipSummary.lua`
- `Iris/media/lua/client/Iris/UI/Tooltip/IrisAltTooltip.lua`
- `Iris/media/lua/client/Iris/Logic/IrisDesc/Generator.lua`
- `Iris/media/lua/client/Iris/Logic/IrisDesc/TagParser.lua`
- `Iris/media/lua/client/Iris/Logic/IrisDesc/Templates.lua`
- `Iris/media/lua/client/Iris/Util/IrisModuleBootstrap.lua`
- `Iris/build/description/v2/tools/build/`
- `Iris/build/description/v2/tools/common/`
- 선택된 파일럿의 기존 CLI wrapper와 내부 leaf module

`Iris/Logic/IrisDesc/Ordering.lua` 등 실제 경로는 구현 시작 전 `rg --files` 결과와 require 이름을 함께 확인한다. 같은 이름의 compatibility wrapper와 source owner를 혼동하지 않는다.

### Tests

- `Iris/build/description/v2/tests/`
- `Iris/test/lua/`
- 기존 pre-refactor characterization harness
- `Iris/test/lua/residual_refactor_acceptance_harness.lua` (planned)
- `Iris/test/run_residual_refactor_acceptance.ps1` (planned)
- `Iris/test/validate_residual_refactor_surfaces.ps1` (planned)
- `Iris/validation/residual_refactor/report_inventory.py` (planned validation support)
- `Iris/validation/residual_refactor/run_diagnostic_disposition.py` (planned)
- `Iris/validation/residual_refactor/validate_evidence_roles.py` (planned)
- `Iris/validation/residual_refactor/write_evidence_index.py` (planned non-authority writer)
- `Iris/build/description/v2/tests/test_iris_residual_runtime_acceptance.py` (planned current-route test)
- `Iris/build/description/v2/tests/test_iris_residual_contract_surfaces.py` (planned current-route test)
- `Iris/build/description/v2/tests/test_iris_residual_python_import_matrix.py` (planned current-route test)
- `Iris/build/description/v2/tests/test_iris_residual_diagnostic_disposition.py` (planned current-route test)
- `Iris/build/description/v2/tests/test_iris_residual_evidence_roles.py` (planned current-route test)
- 새 presentation-order, Browser permutation, public API nested mutation-isolation, unit profile, Tooltip branch, lazy-debug 테스트
- 선택된 Python 파일럿의 direct-script/module/import/CLI/byte-contract 테스트

### Docs

- 본 계획 문서
- 구현 완료 시 [`DECISIONS.md`](DECISIONS.md), [`ARCHITECTURE.md`](ARCHITECTURE.md), [`ROADMAP.md`](ROADMAP.md)의 관련 readpoint
- Python 도구 역할·실행 경로·직렬화 계약 manifest 또는 inventory 문서
- 새 evidence role manifest 규칙
- `Iris/_docs/refactor/residual_refactor/`의 plan-specific baseline·acceptance·closeout evidence
- manual runtime validation schema/report와 diagnostic raw/disposition report

### Config

- `Iris/_docs/round3/round3_active_core_closure.json`
- `Iris/_docs/round3/round3_test_taxonomy.json`
- `Iris/_docs/round3/current_route_required_validations.json`
- `Iris/_docs/refactor/core_refactor/phase0_supported_api_manifest.json`
- `Iris/_docs/refactor/core_refactor/phase0_protected_surface_manifest.json`
- 선택한 파일럿에 새 내부 모듈이 생길 경우의 closure 허용 정책
- package marker를 추가할 경우 clean-checkout import 경로

### Generated Artifacts

- 빌드·검증 중 생성되는 JSON, JSONL, Lua, hash, validation report
- packaging smoke test 산출물
- current/historical/diagnostic evidence bundle

생성 파일은 source와 분리하고, 테스트용 산출물은 명시적으로 정한 임시 output root에 기록한다. 생성된 Lua를 source 수정처럼 수동 편집하지 않는다.

## 6. Planned Changes

### Change Dependency Gates

| Change | Mandatory prerequisites | Mutation eligibility |
|---|---|---|
| 1 | 없음 | production read-only inspection과 validation asset 작성만 가능; production mutation 금지 |
| 2 | Change 1 runtime baseline, presentation owner DAG, supported/protected baseline의 `validation_status=passed` | 모두 충족 후 가능 |
| 3 | Change 1 API identity·nested-mutation baseline의 `validation_status=passed` | 충족 후 가능 |
| 4A | Change 1 Wiki unit/locale matrix의 `validation_status=passed` | 충족 후 가능 |
| 4B | Change 1 Tooltip branch/cache baseline 및 Change 3의 `validation_status=passed` | 모두 충족 후 가능 |
| 4C | Change 1 debug-only work inventory의 `validation_status=passed` | 충족 후 가능 |
| 5A | Change 1 closure-slot owner decision의 `validation_status=passed` | zero-new-stem in-place 파일럿만 가능 |
| 5B | Change 5A `validation_status=passed`, closure 외부 비-hub 적격 후보 1개 이상 | 후보가 없으면 5B와 전체 계획 `partial` |
| 6A | Change 1 inventory의 `validation_status=passed` | role manifest 정리 가능 |
| 6B | BOM consumer/hash 조사의 `validation_status=passed` | 아니면 `application_status=deferred` |
| 6C | Change 5 `validation_status=passed`, exact 대상·owner 승인 | 아니면 `application_status=deferred` |
| 7 | Change 1 최소 evidence schema의 `validation_status=passed` | validator 통합 가능 |
| 8 | 모든 필수 Change의 `validation_status=passed`와 조건부 application matrix 완료 | closeout 가능 |

Change 5 집계 규칙은 `Change 5A.validation_status=passed AND Change 5B.validation_status=passed → Change 5.validation_status=passed`이다. 5B가 `failed`, `blocked`, `not_applicable`이면 Change 5는 `passed`가 아니며 전체 계획은 `partial`이다. 적격 후보 부재를 `not_applicable`로 반올림하지 않는다.

### Change 1 — Phase 0 production read-only 기준선과 validation asset authoring

#### Purpose

production source는 변경하지 않은 채 실제 호출 방식과 바이트 계약을 기계 판독 가능한 형태로 고정하고 validation asset을 작성해, 이후 변경이 “정리”라는 이름으로 숨은 호환성을 제거하지 못하게 한다.

#### Files

- `Iris/build/description/v2/tools/build/INVENTORY.md`
- `Iris/validation/residual_refactor/report_inventory.py` (planned validation support; build closure 밖)
- `Iris/_docs/refactor/residual_refactor/phase0_inventory.json` (planned)
- `Iris/_docs/refactor/residual_refactor/phase0_contract_matrix.json` (planned)
- `Iris/_docs/refactor/residual_refactor/phase0_closure_slot_decision.json` (planned owner decision)
- `Iris/_docs/refactor/residual_refactor/phase0_supported_api_manifest.json` (planned successor baseline)
- `Iris/_docs/refactor/residual_refactor/phase0_protected_surface_manifest.json` (planned successor baseline)
- `Iris/_docs/refactor/residual_refactor/evidence_role.schema.json` (planned minimum schema)
- `Iris/_docs/refactor/residual_refactor/current_evidence_index.json` (optional, non-authoritative projection)
- `Iris/_docs/round3/round3_active_core_closure.json` (read-only gate input)
- `Iris/_docs/round3/round3_test_taxonomy.json` 및 `current_route_required_validations.json`
- `Iris/test/lua/residual_refactor_acceptance_harness.lua`, `Iris/test/run_residual_refactor_acceptance.ps1` (planned before first mutation)
- `Iris/test/validate_residual_refactor_surfaces.ps1` (planned before first mutation)
- `Iris/validation/residual_refactor/run_diagnostic_disposition.py`, `validate_evidence_roles.py` (planned before first mutation)
- `Iris/_docs/refactor/residual_refactor/manual_runtime_validation.schema.json` (planned before first mutation)
- Section 7의 다섯 planned current-route Python tests
- 관련 inventory/contract tests

#### Implementation Notes

1. Section 4.2의 단일 inventory 명령으로 파일·line·import·helper·BOM 수치와 측정 규칙을 함께 재생성한다.
2. 각 도구에 다음 필드를 기록한다.
   - repository-relative path
   - tracked 여부
   - 역할
   - direct script, `python -m`, package import, bare import 진입점
   - caller와 subprocess parent
   - 읽고 쓰는 artifact
   - serialization/hash/error/line-ending 계약 식별자
   - current/historical/diagnostic validation 소속
   - owner 또는 미확정 표시
3. 현재 `INVENTORY.md`에 남아 있는 과거 파일 수는 삭제하지 말고 “당시 snapshot”으로 표시한다. 현재 수치와 혼합하지 않는다.
4. `round3_active_core_closure.json`에서 `current_closure_count=12`, `current_route_allowed_tooling_modules` 4개, `current_route_allowed_tooling_policy.max_allowed_modules=4`, `core_closure_count_must_remain=12`, `expansion_requires`, owner class를 기록한다.
5. owner는 새 internal leaf의 stem이 `current_closure_modules` 또는 `current_route_allowed_tooling_modules` 슬롯을 소비하는지 `phase0_closure_slot_decision.json`에 `decision=consumes_slot|does_not_consume_slot`과 `validation_status=passed|failed|blocked`를 분리해 기록한다. 판정 주체·근거 manifest hash·후보별 소속을 포함한다.
6. Lua baseline은 출력값뿐 아니라 table identity와 nested mutation, Browser 대표 선택, Wiki 단위·locale, Tooltip 삽입 분기, debug-only 선행 계산을 기록한다.
7. Tooltip baseline은 `IrisAltTooltip`을 줄 조립 owner로 고정하고 Tags, Connections, 선택적 UseCase, More의 네 삽입 지점을 기록한다. 성공 경로는 UseCase 유무에 따라 3~4줄, API 로드 실패 경로는 2줄이며 명시적 상한은 없음을 fixture로 고정한다.
8. 기존 `Iris/_docs/refactor/core_refactor/phase0_supported_api_manifest.json`과 `phase0_protected_surface_manifest.json`을 입력으로 사용하되 수정하지 않는다. 현재 checkout successor baseline을 plan-specific evidence root에 생성한다.
9. 최소 evidence-role schema를 이 단계에서 고정한다. 모든 후속 evidence는 `role`, producer, input/output hash, command, subject commit/tree/overlay, mutable 여부, supersedes 관계를 가진다.
10. optional `current_evidence_index.json`은 검증 편의를 위한 projection일 뿐 Artifact Registry current authority, seal owner, cutover owner, 기존 authority manifest 대체물 또는 자동 갱신 권위가 아니다.
11. 첫 production mutation 전에 다음 baseline producer를 실행해 runtime, supported API, protected surface를 plan-specific evidence root에 결속한다.

```powershell
$repositoryRoot = (git rev-parse --show-toplevel).Trim()
powershell -ExecutionPolicy Bypass -File .\Iris\test\run_residual_refactor_acceptance.ps1 `
  -Mode Baseline `
  -RepositoryRoot $repositoryRoot `
  -OutputPath Iris\_docs\refactor\residual_refactor\runtime_behavior_baseline.jsonl
powershell -ExecutionPolicy Bypass -File .\Iris\test\validate_residual_refactor_surfaces.ps1 `
  -Mode Baseline `
  -RepositoryRoot $repositoryRoot `
  -EvidenceRoot Iris\_docs\refactor\residual_refactor
```

#### Validation

- 인벤토리의 모든 경로가 존재하거나 명시적 tombstone 상태이다.
- 역할 미확정 파일이 조용히 누락되지 않는다.
- tracked/untracked 수치와 Git index 조회 결과가 일치한다.
- 직렬화 계약별 fixture가 두 번 실행해 동일한 바이트와 hash를 생성한다.
- line-ending fixture가 `newline="\n"`과 Windows 기본 변환 가능 경로를 구분한다.
- current closure manifest의 core 12·allowed tooling 4와 확장 규칙이 정확한 path/hash에 결속된다.
- successor supported API·protected surface baseline과 runtime behavior baseline이 생성되고 validator가 `passed`이다.
- evidence-role schema가 역할 누락과 authority 오인을 fail-loud한다.
- diagnostic adapter가 raw exit 0, disposition된 exit 1, 신규 failure/error, raw exit 2, report 미생성 fixture를 구분한다.
- manual runtime schema와 다섯 current-route validation asset이 같은 activation change set에서 검증된다.

#### Exit Gate

인벤토리에서 `unknown`이 존재해도 Lua 트랙은 해당 파일과 무관한 경우 진행할 수 있지만, `unknown` 파일은 이동·삭제·공통화 대상이 될 수 없다. 실행 경로 또는 직렬화 계약이 하나라도 불명확한 파일은 Python 파일럿 대상에서 제외한다.

Change 5A로 진행하려면 새 module stem의 closure 슬롯 소비 여부에 대한 owner 판정이 `passed`이고 zero-new-stem 범위가 고정돼야 한다. Change 5B로 진행하려면 정원 확장 없이 실행할 수 있는 closure 외부 비-hub 후보가 최소 1개 선정돼야 한다.

owner 판정 미완료는 Change 5A를 차단한다. 적격 후보 부재는 5A의 계약 fixture 산출을 허용하더라도 Change 5B를 `blocked`로 만들며 전체 계획은 `partial`이다. 이를 extraction 도중 발견하는 stop condition으로 미루지 않는다.

### Change 2 — 중립 presentation-order projection과 Browser 결정론

#### Purpose

classification/taxonomy 의미 권위를 UI로 옮기지 않은 채 표시 순서 중복을 제거하고, Lua hash 순회 순서에 따라 같은 display-name 그룹의 대표 항목이 달라질 수 있는 문제를 없앤다.

#### Files

- `Iris/media/lua/client/Iris/UI/Browser/IrisBrowserCategoryIndex.lua`
- `Iris/media/lua/client/Iris/Logic/CategoryPresentationOrder.lua` (planned)
- `Iris/media/lua/client/Iris/Logic/IrisDesc/Ordering.lua`
- `Iris/media/lua/client/Iris/UI/Browser/IrisBrowserVariantIndex.lua`
- `Iris/media/lua/client/Iris/UI/Browser/IrisBrowserData.lua`
- 관련 Lua/Python contract tests

#### Implementation Notes

1. classification/taxonomy 의미 authority는 기존 Classification/Rule 계층에 남긴다. 새 모듈은 의미·membership를 결정하지 않는 presentation-order projection이다.
2. `Iris/Logic/CategoryPresentationOrder.lua`는 Browser와 IrisDesc 중 어느 한쪽의 소유로 보이지 않는 중립 consumer projection으로 다음 두 기존 계약을 분리해 제공한다.
   - Browser category display order: 현재 9개 순서
   - Description/primary selection priority: 현재 6개 순서와 나머지 category의 `999` fallback
3. `IrisBrowserCategoryIndex`는 category/subcategory label·translation fallback과 Browser presentation metadata의 owner로 남고 taxonomy authority로 승격되지 않는다. `BrowserCategoryIndex`, `Ordering`, `VariantIndex`가 중립 projection을 소비하며 Logic 계층은 Browser UI 모듈을 require하지 않는다.
4. 기존 lookup table과 공개 이름은 동일 shape로 유지한다. Furniture, Vehicle, Misc를 Description priority 1~9로 승격하지 않고 기존 `999` fallback을 보존한다.
5. `buildDisplayNameGroups` 결과는 category/subcategory 캐시 생성 시 한 번 계산한다.
6. fold 가능한 동일-displayName 그룹의 대표 항목은 non-empty `fullType`을 Lua의 locale-independent case-sensitive 문자열 `<`로 오름차순 정렬한 첫 항목으로 정한다. displayName은 그룹 안에서 동일하고 itemType·hasRecipe는 fold 가능성 조건이므로 comparator 필드가 아니다.
7. `fullType`은 `subData.items`의 map key이므로 nil key와 동일 map 내부 중복 key는 구조적으로 존재할 수 없다. empty-string key만 fail-loud fixture 대상으로 두며, nil·duplicate fixture를 만들지 않는다.
8. 원본 source index와 `pairs()` 순서는 comparator나 tie-break로 사용하지 않는다. 같은 `fullType` equality는 같은 identity이므로 별도 tie-break가 필요하지 않다.
9. recipe 연결 여부와 folded count는 같은 파생 그룹에서 계산한다.
10. 기존 `IrisBrowserData`의 `uninitialized`, `building`, `retryable_failed`, `ready`, `degraded_ready` 상태 모델은 유지한다. 파생 캐시는 이 상태와 같은 수명주기로 폐기·재구축한다.

#### Validation

- 입력 항목 순서를 여러 permutation으로 바꾸어도 대표 `fullType`, 그룹 정렬, folded count가 동일하다.
- Browser 9개 display order, Description/primary 6개 priority, 나머지 `999` fallback이 각각 기존 fixture와 일치한다.
- require dependency 검사에서 Logic → `Iris/UI/Browser` edge가 0개이다.
- `Iris/UI/Browser` → `Iris/Logic/CategoryPresentationOrder` 한 edge만 owner-approved intended architecture delta로 기록하고, 그 외 신규 cross-layer edge는 0개이다.
- 검색 key와 기존 preferred location 동작이 바뀌지 않는다.
- retryable failure 이후 재빌드와 degraded-ready 경로가 기존 characterization을 통과한다.
- 공개 Browser 결과의 필드와 타입이 변하지 않는다.

#### Stop Conditions

- 대표 항목 규칙을 고정하려면 새로운 제품 의미 판단이 필요한 경우
- 중립 projection 도입이 기존 사용자 표시 순서 또는 6개/나머지 priority 경계를 바꾸는 경우

위 조건에서는 production mutation을 중단하고 presentation owner DAG와 fixture만 남긴다. taxonomy 의미 변화는 별도 결정으로 관리한다.

### Change 3 — 공개 동결 데이터의 copy-on-read 경계

#### Purpose

호출자가 반환 배열을 변경해 전역 정적 데이터나 다른 호출자의 결과를 오염시키지 못하게 한다.

#### Files

- `Iris/media/lua/client/Iris/API/Tags.lua`
- `Iris/media/lua/client/Iris/API/UseCases.lua`
- `Iris/media/lua/client/Iris/UI/Tooltip/IrisTooltipSummary.lua` (copy projection owner; line assembly는 Change 4B 소유)
- 기존 array utility 또는 작은 공용 copy helper
- `Iris/build/description/v2/tests/test_phase5_array_util_contract.py`
- 관련 Lua harness

#### Implementation Notes

1. public getter는 배열의 복사본을 반환한다.
2. `UseCases.getUseCaseLines()`는 새 wrapper를 만들지만 현재 `entry.lines`와 `entry.debug_lines`를 그대로 참조하는 **확정된 nested mutation 노출**이다. wrapper와 두 중첩 배열을 모두 새로 만들며 원소가 scalar라는 계약을 검증한다.
3. `getOutcomes`, `getCapabilities`, `Tags.getTags` 계열의 반환 배열도 copy-on-read로 전환한다.
4. `Tags.hasTag`, `UseCases.hasOutcome`, `UseCases.hasCapability` 같은 내부 predicate는 public copy getter를 재호출하지 않는다. module-private raw snapshot getter를 필수로 두어 predicate당 배열 할당을 방지한다.
5. `IrisTooltipSummary.get()`은 `summaryByFullType`의 공유 record와 `tags`, `connections` 배열을 참조로 반환하는 확정 사례다. Change 3에서 public consumer용 복사 projection을 반환하고, cache owner 내부만 raw record를 사용한다.
6. 결과의 nil/empty 구분, 배열 순서, 중복, public key 이름과 supported API signature/shape는 유지한다. 반환 table identity 변경은 의도된 isolation delta로 compatibility report에 기록하되 값·shape 호환성보다 큰 claim을 하지 않는다.
7. 현재 호출 문자열만 검사하는 테스트는 실제 mutation-isolation과 allocation counter 계약 테스트로 보강한다.

#### Validation

- 첫 번째 반환 wrapper, 최상위 배열, `lines`, `debug_lines`, Tooltip `tags`, `connections`의 원소를 각각 변경한 뒤 다시 호출해도 원본과 두 번째 반환값이 변하지 않는다.
- 동일 API의 반환 순서·길이·값이 변경 전 fixture와 같다.
- public API의 함수 이름과 인자 수가 유지된다.
- predicate 반복 harness에서 public copy helper 호출 수가 0이고 dataset 전체 복사가 발생하지 않는다.

### Change 4A — Wiki 단위 프로필과 순수 formatter

#### Purpose

서로 다른 Wiki 표시 단위를 코드에 명시하되 현재 사용자-visible 값을 바꾸지 않는다.

#### Files

- `Iris/media/lua/client/Iris/UI/Wiki/IrisWikiSections.lua`
- 새 순수 formatter 또는 기존 formatter owner
- 관련 locale/unit harness

#### Implementation Notes

1. hunger, thirst, stress, boredom 값에 대해 raw와 percent-scaled 프로필을 이름으로 분리한다.
2. 기존 food section의 `* 100` 결과와 core info section의 raw 결과를 먼저 고정한다.
3. characterization row는 `source_field`, `profile`, `multiplier`, `format_string`, `locale_key`, `input`, `current_output`을 모두 가진다. 두 프로필이 같은 locale key와 format을 공유하는 현재 상태도 명시한다.
4. 실제 PZ 데이터 단위와 사용자 표시 계약이 결정되기 전에는 두 프로필을 하나로 강제 통합하지 않는다. 첫 구현은 **현재 출력 보존 + 단위 의도 명시**이다.
5. 값 통합이 필요하다는 별도 결정이 내려지면 fixture, 문구, 사용자-visible 변경을 별도 변경 묶음으로 수행한다.

#### Validation

- raw/percent 프로필의 입력·출력 표와 EN/KO locale 문자열이 baseline과 일치한다.
- food/core section이 같은 locale key를 쓰되 각 multiplier를 보존함을 검증한다.
- formatter는 runtime 의미 추론이나 데이터 보정을 하지 않는다.

### Change 4B — Tooltip fact projection·번역·줄 조립 경계

#### Purpose

Tooltip의 정적 사실 cache와 locale-dependent 번역·줄 조립을 분리하면서 현재 조건 분기와 줄 순서를 보존한다.

#### Files

- `Iris/media/lua/client/Iris/UI/Tooltip/IrisTooltipSummary.lua`
- `Iris/media/lua/client/Iris/UI/Tooltip/IrisAltTooltip.lua`
- `Iris/media/lua/client/Iris/Util/IrisTranslationResolver.lua`
- 관련 Tooltip branch/cache harness

#### Implementation Notes

1. `IrisTooltipSummary`는 fullType별 비번역 사실 projection과 cache owner이고, `IrisAltTooltip`은 번역과 최종 `detailLines` 조립 owner이다.
2. `IrisTranslationResolver`를 사용해 표시 시점에 번역하며 번역된 문자열을 fact cache에 저장하지 않는다. locale 변경은 fact cache invalidation 없이 새 번역을 반영해야 한다.
3. 성공 경로의 삽입 지점은 Tags, Connections, 조건부 UseCase, More 순서이다. UseCase가 없으면 3줄, 있으면 4줄이다. API/summary load 실패 경로는 Tags failure와 More의 2줄이다.
4. 명시적 `maxLines`, 초과 절단, 새 줄 수 상한을 도입하지 않는다. 기존 tag text 50자 축약은 줄 수 계약과 구분해 그대로 보존한다.
5. Tooltip hot path에서 전체 Detail ViewModel을 만들지 않는다.
6. `IrisTooltipSummary.get()`의 공유 cache record 노출은 Change 3이 소유하고, Change 4B는 그 public copy projection을 소비한다.

#### Validation

- Tags/Connections/UseCase/More 삽입 지점별 조건 fixture를 실행한다.
- API 성공+UseCase 존재는 4줄, 성공+UseCase 부재는 3줄, API load 실패는 2줄이며 순서와 문구가 baseline과 일치한다.
- source contract는 `maxLines` 식별자, `#detailLines`와 상한 상수 비교, 줄 수 제한 목적의 `table.remove`, 초과 행 생략용 truncate helper가 모두 없음을 검사한다. tag text 50자 축약은 허용된 별도 계약이다.
- locale 변경 전후 fact cache identity는 유지되고 출력 번역만 갱신된다.
- summary cache 재사용과 Change 3 mutation isolation이 함께 통과한다.

### Change 4C — 기존 logger gate를 이용한 lazy debug

#### Purpose

debug가 꺼진 일반 실행에서 진단용 문자열 생성과 순회를 생략하되 warning·error 경계를 유지한다.

#### Files

- `Iris/media/lua/client/Iris/Logic/IrisDesc/Ordering.lua`
- `Iris/media/lua/client/Iris/Logic/IrisDesc/TagParser.lua`
- `Iris/media/lua/client/Iris/Logic/IrisDesc/Templates.lua`
- 실제 선행 계산이 확인된 Browser 파일
- `Iris/media/lua/client/Iris/Util/IrisModuleBootstrap.lua` (logger gate 전달 조사 대상)
- `Iris/media/lua/client/Iris/Logic/IrisDesc/Logger.lua` 및 `Iris/media/lua/client/Iris/Util/IrisLogger.lua` (existing API reference)
- 관련 debug harness

#### Implementation Notes

1. 새 logger 의미나 전역 flag를 만들지 않고 기존 `IrisLogger.isDebugEnabled()`와 IrisDesc `Logger.isDebugEnabled()`를 재사용한다.
2. Change 1 inventory에서 실제 선행 문자열 조합·반복 순회가 남은 callsite를 `debug_only`와 `user_visible_or_failure`로 구분한다. 현재 확인 대상에는 `Ordering`, `TagParser`, `Templates`가 포함된다.
3. `Generator`와 `Renderer`처럼 이미 gate를 쓰는 파일은 회귀 검증 대상이며 재작성 대상이 아니다.
4. Browser는 bootstrap이 기존 logger gate를 안전하게 전달할 수 있는지 확인하고, 새 API 추가 없이 가능한 경우에만 gate를 적용한다.
5. warning·error, 사용자 표시 문자열, 필수 failure evidence는 debug 상태와 무관하게 유지한다.
6. `IrisModuleBootstrap.lua` 수정이 불필요하면 `application_status=not_applicable`, inspection note `inspected_no_change`로 기록한다.

#### Validation

- debug off에서 각 `debug_only` 문자열 helper와 순회 counter가 0이다.
- debug on에서 기존 핵심 진단 field와 순서가 남는다.
- warning·error 및 사용자 표시 helper 호출 수는 debug on/off에서 동일하다.
- 기존 `Generator`·`Renderer` gate가 유지된다.

### Change 5 — Python package/import 및 I/O 계약 파일럿

#### Purpose

`sys.path` 조작과 중복 helper를 한 번에 제거하지 않고, closure 정원을 늘리지 않으면서 기존 진입점과 바이트 계약을 보존하는 최소 패턴을 증명한다.

#### Preconditions

- `phase0_closure_slot_decision.json.validation_status=passed`
- 5A는 zero-new-stem 파일럿으로 확정
- 5B는 적격 closure-external 비-hub 후보 1개 이상 확정
- core 12 / allowed tooling 4 정원 유지
- clean-checkout import baseline `passed`

#### Files

- `Iris/build/description/v2/tools/build/compose_layer3_io.py` (core 12; mandatory zero-new-stem pilot만 허용)
- `Iris/build/description/v2/tools/build/public_text_quality_acceptance.py` (allowed tooling 4; 분석·호환 fixture 대상)
- `Iris/build/description/v2/tools/build/export_dvf_3_3_lua_bridge.py` (allowed tooling 4; 분석·호환 fixture 대상)
- `Iris/build/description/v2/tools/build/_dvf_3_3_vnext_common.py` (closure 외부지만 high-fan-in hub; 첫 extraction 제외)
- `Iris/build/description/v2/tools/common/paths.py`
- Phase 0에서 선정한 closure-external 비-hub 파일 1개 (조건부 module-extraction pilot)
- 관련 Python tests와 byte fixtures

후보의 현재 소속은 다음과 같으며 이 표가 파일럿 선정 전제다.

| 후보 | 현재 closure 소속 | 허용 작업 |
|---|---|---|
| `compose_layer3_io.py` | core 12 | 새 stem 없는 owner 내부 helper 정리·계약 명명·fixture만 가능 |
| `public_text_quality_acceptance.py` | allowed tooling 4/4 | 분석과 golden fixture만; 새 stem 추출 금지 |
| `export_dvf_3_3_lua_bridge.py` | allowed tooling 4/4 | 분석과 golden fixture만; 새 stem 추출 금지 |
| `_dvf_3_3_vnext_common.py` | closure 외부 | high-fan-in bare-import hub이므로 첫 추출 금지 |
| Phase 0 선정 후보 | closure 외부, 비-hub여야 함 | owner 승인 후 조건부 leaf extraction 가능 |

#### Implementation Notes

1. 먼저 다음 네 실행 형태를 working tree와 clean checkout에서 검증한다.
   - repository root에서 문서화된 `python -m tools.build...`
   - 기존 direct script 실행
   - `from tools.build import ...`
   - 기존 bare import caller
2. `Iris/build/tools/common`과 `Iris/build/description/v2/tools/common`의 namespace 충돌을 검증한다. 충돌 가능성이 남으면 `tools.common`에 새 범용 helper를 추가하지 않는다.
3. mandatory 파일럿 5A는 `compose_layer3_io.py` 안에서 동일 계약 helper의 이름·호출을 정리하고 golden fixture를 추가하되 새 module/package stem이나 import edge를 만들지 않는다.
4. 조건부 파일럿 5B는 Phase 0가 선정한 closure-external 비-hub 파일 하나에만 적용한다. 적격 후보가 없으면 임의로 named 후보를 승격하지 않고 Change 5를 `blocked`, 전체 계획을 `partial`로 닫는다.
5. 새 내부 package 이름은 Phase 0 결과와 owner 승인 후 확정한다. 이름보다 다음 조건이 우선한다.
   - stdlib-only import
   - import 시 filesystem mutation 없음
   - repository root·v2 root 어느 쪽에서도 동일 owner를 resolve
   - 기존 public module 이름 유지
6. 직렬화 helper는 `sorted-json-lf-trailing-newline`, `unsorted-json-platform-newline-no-trailer`, `atomic-jsonl`, `long-path-strict-hash`처럼 line-ending까지 계약별로 나눈다. 기존 출력을 공통 기본값에 맞추지 않는다.
7. 조건부 첫 extraction은 하나의 순수 경로 계산 또는 동일 계약 함수군으로 제한한다. 기존 큰 파일은 CLI와 public import adapter를 유지하고 구현을 내부 leaf에 위임한다.
8. `_dvf_3_3_vnext_common.py`는 호환성 검증 대상으로만 사용한다.
9. core 12 또는 allowed tooling 4를 늘리는 정원 확장은 본 계획에서 선택할 수 있는 stop-and-review가 아니라 명시적 out of scope다.

#### Validation

- 네 실행 형태가 동일 fixture에서 동일 exit code와 stdout/stderr 계약을 보인다.
- golden artifact의 바이트와 SHA-256이 변경 전과 동일하다.
- 예외 유형과 필수 오류 문구가 기존 contract test와 일치한다.
- Windows long path, missing file, atomic replace retry 경로를 개별 검증한다.
- LF/CRLF, trailing newline, BOM을 독립 fixture로 비교한다.
- clean checkout 검증은 개인 working tree의 임시 import 경로에 의존하지 않는다.
- 파일럿 전후 current·historical·full discovery 검증이 모두 성공해야 한다.

#### Stop Conditions

- 동일 함수명 아래 둘 이상의 바이트 계약이 발견되는데 호출자 분리가 불가능한 경우
- package marker 추가로 다른 `tools` package resolution이 바뀌는 경우
- adapter가 기존 subprocess 또는 direct-script 오류 경계를 재현하지 못하는 경우
- closure 슬롯 owner 판정이 `passed`가 아니거나 적격 closure-external 비-hub 후보가 없는 경우
- 어떤 extraction도 core 12 / allowed tooling 4 정원 확장을 요구하는 경우

중단 시 5A의 in-place 결과와 계약 행렬·실패 fixture만 유지할 수 있지만, module/import 파일럿 완료를 주장하지 않는다. Change 5는 `blocked`, 전체 계획은 `partial`로 기록한다.

### Change 6A — 도구 역할 manifest 확정

#### Purpose

파일명의 시기 표기나 참조 횟수로 도구를 추측하지 않고 재현 책임과 실행 역할을 mandatory manifest로 확정한다.

#### Files

- `Iris/build/description/v2/tools/build/INVENTORY.md`
- Phase 0 role manifest
- 관련 reproduction tests

#### Implementation Notes

1. 도메인 후보는 acquisition, dvf_3_3, public_text_quality, identity_fallback, source_coverage, post_cleanup, body_plan으로 분류한다.
2. `old`, `phase`, `closure`, `final` 같은 이름은 삭제 근거로 사용하지 않는다.
3. 참조가 없는 파일도 historical reproduction 또는 수동 운영 경로일 수 있으므로 상태만 기록한다.
4. subprocess 전환 후보는 함수 입력·출력, cwd, environment, exit code, stdout/stderr, timeout, partial artifact 동작을 모두 비교한다. 이 Change에서는 판정만 하고 전환하지 않는다.

#### Validation

- no-reference 파일 수와 상태는 보고하되 삭제 수를 성공 지표로 사용하지 않는다.
- subprocess 유지·전환 판정 근거가 manifest에 남는다.
- 모든 파일이 정확히 한 primary role과 0개 이상의 validation role을 가진다.

### Change 6B — UTF-8 BOM 정규화 (조건부)

#### Purpose

확인된 BOM 파일을 의미 변경과 분리해 정규화하되 외부 hash 소비자가 없다는 증거가 있을 때만 적용한다.

#### Files

- Phase 0에서 재확인한 UTF-8 BOM 파일 목록
- BOM consumer/hash report
- 관련 parse·artifact fixtures

#### Implementation Notes

1. 16개라는 예비 수치를 재측정하고 각 파일의 tracked 상태, caller, source-file hash 소비자를 기록한다.
2. 외부 또는 sealed hash 소비자가 하나라도 미확정이면 `application_status=deferred`, `validation_status=not_applicable`로 기록하고 파일을 수정하지 않는다.
3. 적용 시 UTF-8 without BOM 변경만 전용 change set으로 수행하며 AST/코드 변경과 섞지 않는다.

#### Validation

- 적용 시 Python AST, CLI 결과, 생성 artifact byte/hash가 허용된 source-file hash delta를 제외하고 동일하다.
- 미적용 시 `application_status=deferred|not_applicable`, `validation_status=not_applicable`과 근거가 closeout matrix에 존재한다.

### Change 6C — 한 개 도메인 묶음 이동 (조건부)

#### Purpose

Change 5에서 패턴이 증명되고 owner가 승인한 경우에만 한 개 도메인을 이동한다.

#### Files

- exact owner 승인을 받은 한 개 도메인 묶음
- 기존 경로 compatibility adapter
- 관련 reproduction tests

#### Implementation Notes

1. 다음 조건을 모두 만족해야 한다.
   - `Change 5.validation_status=passed`
   - owner와 역할 확정
   - caller와 artifact 계약 완전 목록화
   - current/historical validation 소속 확인
   - compatibility adapter 설계 완료
   - registry giant 미포함
2. 조건이 없으면 `application_status=deferred`, `validation_status=not_applicable`이며 이 계획 안에서 대체 대상을 임의 선정하지 않는다.

#### Validation

- 모든 이동 항목에 기존 경로 adapter 또는 명시적 caller migration이 있다.
- historical reproduction 명령이 이동 전후 동일 artifact를 만든다.
- closeout matrix에 `application_status=applied|deferred|not_applicable`과 대응 `validation_status`, 근거가 기록된다.

### Change 7 — 증거 역할 validator와 보존 우선 통합

#### Purpose

Change 1에서 먼저 고정한 최소 schema를 validator와 closeout에 연결해, 새로운 진단 출력이 현재 권위처럼 소비되거나 current 결과가 historical bundle에 덮어써지는 일을 막는다.

#### Files

- `Iris/_docs/refactor/residual_refactor/evidence_role.schema.json`
- `Iris/_docs/refactor/residual_refactor/current_evidence_index.json` (optional projection)
- `Iris/_docs/refactor/residual_refactor/diagnostic_advisory_dispositions.json` (planned owner-approved input)
- `Iris/_docs/refactor/residual_refactor/diagnostic_contract_raw_report.json` (planned raw output)
- `Iris/_docs/refactor/residual_refactor/diagnostic_contract_disposition_report.json` (planned adapter output)
- `Iris/validation/residual_refactor/run_diagnostic_disposition.py` (planned wrapper/adapter)
- `Iris/validation/residual_refactor/validate_evidence_roles.py` (planned validator)
- `Iris/validation/residual_refactor/write_evidence_index.py` (planned non-authority writer)
- `Iris/_docs/round3/round3_run_contract_tests.py` (read-only public runner; exit 의미 변경 금지)
- `Iris/_docs/round3/`의 existing current validation manifest (authority input; 자동 대체 금지)
- `Iris/build/description/v2/staging/`의 승인된 신규 evidence manifest
- 필요 시 문서화된 disposable output root 설정

#### Implementation Notes

1. Change 1 schema에 따라 새 evidence bundle은 최소한 다음 필드를 가진다.
   - role: `current`, `historical`, `diagnostic`
   - producer module과 version/readpoint
   - input manifest/hash
   - output manifest/hash
   - 생성 시각과 재현 명령
   - mutable 여부와 supersedes 관계
2. optional `current_evidence_index.json`과 immutable bundle을 분리한다. 이 index는 편의용 evidence projection이며 Artifact Registry current authority, seal/cutover owner, 기존 authority manifest 대체물 또는 기존 current pointer 자동 갱신 경로가 아니다.
3. `diagnostic` 결과는 판정 권위가 아니며 current closure 성공을 덮어쓰지 못한다.
4. sealed evidence는 생성 도구 수정의 회귀 비교 자료로만 읽고 수정·삭제하지 않는다.
5. tracking 정책 변경, 대용량 이관, 보존 기간 결정은 별도 owner 승인 계획으로 남긴다.
6. `run_diagnostic_disposition.py`는 raw child argv를 `[sys.executable, "-B", runner, "--class", "diagnostic", "--out", raw_out]`으로 고정하고 raw report와 raw exit code를 함께 캡처한다. raw runner의 public exit-code 의미나 구현은 바꾸지 않는다.
7. adapter는 `execution_status=passed|failed`, `finding_status=passed|advisory_failed|unexpected_failed`, `blocking=true|false`, `raw_exit_code`, matched/unmatched test IDs와 traceback fingerprint를 기록한다.
8. traceback fingerprint 계산 전 adapter는 순서를 고정한다. 먼저 `CRLF`와 단독 `CR`을 `LF`로 바꾸고 `\\`를 `/`로 통일한다. 다음으로 repository root와 materialized historical checkout·temporary overlay root의 canonical absolute path도 `/` 형식으로 만든 뒤 긴 prefix부터 각각 `<REPO>/`, `<OVERLAY>/`로 치환한다(Windows path 비교는 case-insensitive). 마지막으로 실행마다 달라지는 disposable temporary directory basename을 `<TEMP>/`로 치환한다. 이 정규화 UTF-8 text의 SHA-256을 fingerprint로 사용한다. test ID, exception type, 안정적인 message body는 제거하지 않아 실제 finding 변화가 같은 fingerprint로 축약되지 않게 한다.
9. raw exit `0`은 report schema와 `success=true`가 일치해야 한다. raw exit `1`은 모든 failure/error가 owner, reason, expected test ID, traceback fingerprint, expiry/readpoint를 가진 disposition과 정확히 일치할 때만 `blocking=false`가 될 수 있다. raw exit `2`, report 미생성·schema 오류·새 finding·stale disposition은 항상 adapter nonzero다.
10. current/historical raw reports와 diagnostic raw/disposition reports는 plan-specific evidence root에만 기록한다. 기존 round3 authority manifest를 각 실행에서 갱신하지 않는다. required route 등록 변경은 Change 1의 owner-approved manifest delta가 소유한다.

#### Validation

- evidence validator가 역할 누락, hash 불일치, mutable bundle 덮어쓰기를 거부한다.
- current/historical raw runner와 diagnostic wrapper가 고정된 plan-specific output만 쓰고 기존 authority manifest를 갱신하지 않는다.
- diagnostic known advisory fixture는 adapter exit 0과 `blocking=false`, 신규 failure/error fixture는 adapter nonzero를 검증한다.
- repository·overlay 절대경로, slash 방향, `CRLF|LF`, 실행별 temporary directory 이름만 다른 동치 traceback fixture는 같은 fingerprint를 만들고, test ID·exception type·안정적인 message가 달라진 fixture는 다른 fingerprint를 만드는지 검증한다.
- 두 번 실행해 같은 입력에 대한 immutable content hash가 동일하다.
- 기존 sealed evidence의 Git hash와 파일 hash가 변경되지 않는다.
- evidence-role validator는 `validation_status`, current evidence index는 별도 `application_status`와 대응 `validation_status`를 closeout matrix에 기록한다.

### Change 8 — 통합 closeout과 후속 범위 판정

#### Purpose

각 변경의 국소 테스트만 통과한 상태를 완료로 오인하지 않고, 현재·과거·runtime·package 경계를 한 readpoint에서 검증한다.

#### Files

- `Iris/_docs/refactor/residual_refactor/final_validation_matrix.json`
- `Iris/_docs/refactor/residual_refactor/current_contract_report.json`
- `Iris/_docs/refactor/residual_refactor/historical_contract_report.json`
- `Iris/_docs/refactor/residual_refactor/diagnostic_contract_raw_report.json`
- `Iris/_docs/refactor/residual_refactor/diagnostic_contract_disposition_report.json`
- `Iris/_docs/refactor/residual_refactor/manual_runtime_validation_report.json`
- 기타 closeout evidence/report
- [`DECISIONS.md`](DECISIONS.md)
- [`ARCHITECTURE.md`](ARCHITECTURE.md)
- [`ROADMAP.md`](ROADMAP.md)
- 역할·계약 inventory 최종본

#### Implementation Notes

1. 각 Change는 독립적으로 되돌릴 수 있는 작은 변경 묶음으로 유지한다.
2. 전체 검증 결과와 hash delta를 closeout report에 묶는다.
3. intentional delta는 제품·권위 결정 링크가 없으면 허용하지 않는다.
4. registry giant, 대규모 evidence migration, no-reference 파일 삭제, 추가 도메인 이동은 후속 후보로만 기록한다.
5. 완료 판정은 “후속 후보가 0개”가 아니라 “본 계획의 필수 범위와 계약이 모두 닫힘”을 뜻한다.
6. manual runtime report가 `blocked`이거나 diagnostic disposition report가 `blocking=true`이면 `complete`를 금지한다.

#### Validation

- Section 7의 모든 terminal 필수 명령이 exit code 0이다. diagnostic raw runner의 내부 exit 1은 adapter가 exact known advisory로 disposition한 경우에만 허용되며 terminal adapter 자체는 0이어야 한다.
- Git diff에 생성 Lua 수동 편집, sealed evidence 변경, package projection 직접 편집이 없다.
- 문서의 실제 구현 상태와 `complete`/`partial` 표기가 일치한다.

## 7. Validation Plan

### Validation Assets and Route Registration

첫 production mutation 전에 다음 planned validation asset을 만든다.

- `Iris/test/lua/residual_refactor_acceptance_harness.lua`
- `Iris/test/run_residual_refactor_acceptance.ps1`
- `Iris/test/validate_residual_refactor_surfaces.ps1`
- `Iris/validation/residual_refactor/report_inventory.py`
- `Iris/validation/residual_refactor/run_diagnostic_disposition.py`
- `Iris/validation/residual_refactor/validate_evidence_roles.py`
- `Iris/validation/residual_refactor/write_evidence_index.py`
- `Iris/build/description/v2/tests/test_iris_residual_runtime_acceptance.py`
- `Iris/build/description/v2/tests/test_iris_residual_contract_surfaces.py`
- `Iris/build/description/v2/tests/test_iris_residual_python_import_matrix.py`
- `Iris/build/description/v2/tests/test_iris_residual_diagnostic_disposition.py`
- `Iris/build/description/v2/tests/test_iris_residual_evidence_roles.py`
- `Iris/_docs/refactor/residual_refactor/manual_runtime_validation.schema.json`

다섯 Python test를 `Iris/_docs/round3/round3_test_taxonomy.json`의 `current` class와 `Iris/_docs/round3/current_route_required_validations.json`의 required denominator에 등록한다. 두 protected manifest의 변경은 owner-approved exact delta로 사전 기록하고 final protected-surface report가 이를 검증해야 한다. manifest·test·harness·runner activation은 같은 change set에서 수행한다. standalone Lua harness만 실행하고 current route 등록을 생략한 상태는 closeout evidence가 아니다.

### Focused Validation

각 Change는 관련 focused test를 먼저 실행한다.

```powershell
uv run python -B -m unittest discover -s Iris\build\description\v2\tests -p "test_iris_residual_runtime_acceptance.py"
uv run python -B -m unittest discover -s Iris\build\description\v2\tests -p "test_iris_residual_contract_surfaces.py"
uv run python -B -m unittest discover -s Iris\build\description\v2\tests -p "test_iris_residual_python_import_matrix.py"
uv run python -B -m unittest discover -s Iris\build\description\v2\tests -p "test_iris_residual_diagnostic_disposition.py"
uv run python -B -m unittest discover -s Iris\build\description\v2\tests -p "test_iris_residual_evidence_roles.py"
```

runtime behavior evidence는 정확한 runner로 생성한다.

```powershell
$repositoryRoot = (git rev-parse --show-toplevel).Trim()
powershell -ExecutionPolicy Bypass -File .\Iris\test\run_residual_refactor_acceptance.ps1 `
  -Mode Acceptance `
  -RepositoryRoot $repositoryRoot `
  -OutputPath Iris\_docs\refactor\residual_refactor\runtime_behavior_acceptance.jsonl
```

이 harness는 다음을 behavior로 검증한다.

- Browser 9개 display order와 Description/primary 6개 priority·`999` fallback
- locale-independent fullType comparator, permutation별 대표 identity, folded count, cache lifecycle
- wrapper·nested arrays·Tooltip cache record mutation isolation 및 predicate allocation counter
- Wiki `source_field/profile/multiplier/format/locale_key/current_output` matrix
- Tooltip 4개 삽입 지점, 성공 3~4줄, failure 2줄, 기존 줄 순서·번역·tag text 축약
- debug off 선행 계산 0, debug on 진단 보존, warn/error 불변

### Track Closeout Validation

Lua/runtime 트랙은 다음 명령을 모두 실행한다.

```powershell
$repositoryRoot = (git rev-parse --show-toplevel).Trim()
powershell -ExecutionPolicy Bypass -File .\tools\check_lua_syntax.ps1 -Roots "Iris\media\lua"
powershell -ExecutionPolicy Bypass -File .\Iris\test\validate_disposable_package.ps1 -RepositoryRoot $repositoryRoot
powershell -ExecutionPolicy Bypass -File .\Iris\test\validate_residual_refactor_surfaces.ps1 `
  -Mode Closeout `
  -RepositoryRoot $repositoryRoot `
  -EvidenceRoot Iris\_docs\refactor\residual_refactor
```

`validate_residual_refactor_surfaces.ps1`는 Phase 0 successor baseline과 비교해 다음을 생성·검증한다.

- `final_supported_api_compatibility_report.json`
- `final_protected_surface_report.json`
- `final_package_identity_report.json`
- `final_claim_boundary_report.json`

supported API report는 predecessor의 20개 listed surface를 최소 denominator로 사용하고 새 plan-specific baseline과 final scan을 비교한다. protected report는 source facts/decisions/rendered output/generated runtime chunks, closure/validation manifest, 기존 package projection, sealed evidence의 before/after hash와 승인된 delta를 분리한다. package validator는 runtime source 변경 후 필수이며 packaging policy를 바꾸지 않았다는 이유로 생략하지 않는다.

Python 트랙은 direct-script, `python -m`, `from tools.build import`, bare import를 repository root와 v2 root에서 실행하고 stdout/stderr, exit code, exception type, artifact bytes/hash, line ending을 `python_import_matrix_report.json`에 기록한다.

### Full Plan Closeout Validation

저장소 root에서 다음을 모두 실행한다.

```powershell
$repositoryRoot = (git rev-parse --show-toplevel).Trim()
$evidenceRoot = 'Iris\_docs\refactor\residual_refactor'
uv run python -B Iris\_docs\round3\round3_run_contract_tests.py `
  --class current `
  --enforce-current-build-closure `
  --out "$evidenceRoot\current_contract_report.json"
if ($LASTEXITCODE -ne 0) { throw "current contract route failed: $LASTEXITCODE" }
uv run python -B Iris\_docs\round3\round3_run_contract_tests.py `
  --class historical `
  --out "$evidenceRoot\historical_contract_report.json"
if ($LASTEXITCODE -ne 0) { throw "historical contract route failed: $LASTEXITCODE" }
uv run python -B Iris\validation\residual_refactor\run_diagnostic_disposition.py `
  --runner Iris\_docs\round3\round3_run_contract_tests.py `
  --raw-out "$evidenceRoot\diagnostic_contract_raw_report.json" `
  --dispositions "$evidenceRoot\diagnostic_advisory_dispositions.json" `
  --out "$evidenceRoot\diagnostic_contract_disposition_report.json"
if ($LASTEXITCODE -ne 0) { throw "diagnostic disposition failed: $LASTEXITCODE" }
uv run python -B -m unittest discover -s Iris\build\description\v2\tests -p "test_*.py"
if ($LASTEXITCODE -ne 0) { throw "full Python discovery failed: $LASTEXITCODE" }
powershell -ExecutionPolicy Bypass -File .\tools\check_lua_syntax.ps1 -Roots "Iris\media\lua"
if ($LASTEXITCODE -ne 0) { throw "production Lua syntax failed: $LASTEXITCODE" }
powershell -ExecutionPolicy Bypass -File .\Iris\test\validate_disposable_package.ps1 -RepositoryRoot $repositoryRoot
if ($LASTEXITCODE -ne 0) { throw "disposable package validation failed: $LASTEXITCODE" }
```

`diagnostic`는 runner가 실제 지원하는 정식 advisory class이므로 adapter 내부에서 반드시 실행한다. raw runner의 exit `1`을 shell에서 무조건 무시하지 않는다. adapter만 terminal command이며, raw report가 생성되고 모든 finding이 owner-approved disposition과 일치할 때만 exit `0`을 반환한다. raw runner exit `0|1|2`의 public 의미는 변경하지 않는다.

Python 파일럿은 commit된 exact subject를 외부 checkout에서 다음 기존 runner로 재검증한다. Full-gate 실행 직전 validation 대상이 exact committed subject이고 `HEAD == targetCommit`이며 tracked 및 non-ignored working tree가 clean인지 확인한다. 현재 검증된 immutable environment receipt 경로를 사용하며, receipt가 교체되면 새 경로와 hash를 먼저 owner 승인한다. working tree를 commit처럼 가장하지 않는다. 기존 runner도 이 preflight 조건을 fail-close하지만, 아래 순서를 operator contract로 명시한다.

```powershell
$repositoryRoot = (git rev-parse --show-toplevel).Trim()
$targetCommit = (git rev-parse HEAD).Trim()
$verifiedTargetCommit = (git -C $repositoryRoot rev-parse --verify "$targetCommit^{commit}").Trim()
if ($LASTEXITCODE -ne 0 -or $verifiedTargetCommit -ne $targetCommit) { throw 'validation target is not the exact committed subject' }
$headAtGate = (git -C $repositoryRoot rev-parse HEAD).Trim()
if ($LASTEXITCODE -ne 0 -or $headAtGate -ne $targetCommit) { throw 'HEAD does not equal targetCommit' }
$workingTreeRows = @(git -C $repositoryRoot status --porcelain=v1 --untracked-files=all)
if ($LASTEXITCODE -ne 0) { throw 'working-tree clean check failed' }
if ($workingTreeRows.Count -ne 0) { throw 'tracked or non-ignored working tree is not clean' }
$environmentReceipt = 'C:\Users\MW\iccv\receipts\env-v1\environment_receipt.json'
$receipt = Get-Content -LiteralPath $environmentReceipt -Raw | ConvertFrom-Json
$pythonExe = [System.IO.Path]::GetFullPath([string]$receipt.interpreter.path)
if (-not (Test-Path -LiteralPath $pythonExe -PathType Leaf)) { throw "receipt interpreter missing: $pythonExe" }
$expectedPythonHash = ([string]$receipt.interpreter.sha256).ToLowerInvariant()
$actualPythonHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $pythonExe).Hash.ToLowerInvariant()
if ($actualPythonHash -ne $expectedPythonHash) { throw 'receipt interpreter hash mismatch' }
$workRoot = Join-Path ([System.IO.Path]::GetTempPath()) ('iris-residual-clean-work-' + [guid]::NewGuid().ToString('N'))
$resultRoot = Join-Path ([System.IO.Path]::GetTempPath()) ('iris-residual-clean-result-' + [guid]::NewGuid().ToString('N'))
$previousNoUserSite = $env:PYTHONNOUSERSITE
$previousPythonPath = $env:PYTHONPATH
try {
  $env:PYTHONNOUSERSITE = '1'
  Remove-Item Env:PYTHONPATH -ErrorAction SilentlyContinue
  & $pythonExe -B -s Iris\validation\clean_checkout\run_iris_clean_checkout_validation.py full-gate `
    --repo $repositoryRoot `
    --commit $targetCommit `
    --python $pythonExe `
    --environment-receipt $environmentReceipt `
    --work-root $workRoot `
    --result-root $resultRoot
  if ($LASTEXITCODE -ne 0) { throw "clean-checkout full-gate failed: $LASTEXITCODE" }
}
finally {
  if ($null -eq $previousNoUserSite) { Remove-Item Env:PYTHONNOUSERSITE -ErrorAction SilentlyContinue } else { $env:PYTHONNOUSERSITE = $previousNoUserSite }
  if ($null -eq $previousPythonPath) { Remove-Item Env:PYTHONPATH -ErrorAction SilentlyContinue } else { $env:PYTHONPATH = $previousPythonPath }
}
```

terminal full-gate에서는 `uv run python`을 사용하지 않는다. orchestrator의 `sys.executable`, `--python`, receipt interpreter path/hash가 모두 같은 identity여야 한다. gate 이후 생성되는 `clean_checkout_binding_report.json`은 preflight를 통과한 exact subject commit/tree, canonical result, stdout, stderr, environment receipt hash, cleanup status와 해당 검증 결과를 결속하는 evidence이다. 이 report는 validation target을 사후 선택하거나 authority pointer를 대체하지 않는다.

### Evidence and Completion Matrix

검증축은 `validation_status`만 사용한다.

| Validation axis | Evidence path | `complete`에 필요한 `validation_status` |
|---|---|---|
| Runtime behavior harness | `runtime_behavior_acceptance.jsonl` 및 `.binding.json` | `passed` |
| Manual Project Zomboid runtime UI | `manual_runtime_validation_report.json`의 `class_summaries.runtime_ui` | `validation_status=passed` |
| Manual operator contract | `manual_runtime_validation_report.json`의 `class_summaries.operator_contract` | `validation_status=passed` |
| Production Lua syntax | `final_validation_matrix.json` command row | `passed` |
| Supported API compatibility | `final_supported_api_compatibility_report.json` | `passed`, incompatible count 0 또는 별도 승인 delta |
| Protected surface | `final_protected_surface_report.json` | `passed`, unauthorized changed count 0 |
| Disposable package identity | `final_package_identity_report.json` | `passed` |
| Python import/CLI/byte matrix | `python_import_matrix_report.json` | `passed` |
| Clean checkout full-gate | `clean_checkout_binding_report.json` | `passed`; receipt/orchestrator/`--python` identity 일치 |
| Current route | `current_contract_report.json` | `passed` 및 raw exit 0 |
| Historical route | `historical_contract_report.json` | `passed` 및 raw exit 0 |
| Diagnostic disposition | `diagnostic_contract_raw_report.json`, `diagnostic_contract_disposition_report.json` | adapter `passed`, `execution_status=passed`, `blocking=false`; raw exit 0 또는 disposition된 1만 허용 |
| Full Python discovery | `final_validation_matrix.json` | `passed` |
| Evidence-role validator | `final_validation_matrix.json` | `passed` |

조건부 적용 항목은 별도 field로 기록한다.

| Conditional item | 허용 `application_status` | 대응 `validation_status` |
|---|---|---|
| Change 4C `IrisModuleBootstrap.lua` logger-gate 수정 | `applied|not_applicable` | applied이면 `passed`; 수정 불필요이면 `not_applicable`과 `inspection_note=inspected_no_change` |
| Change 6B BOM normalization | `applied|deferred|not_applicable` | applied이면 `passed`, 나머지는 `not_applicable` |
| Change 6C domain move | `applied|deferred|not_applicable` | applied이면 `passed`, 나머지는 `not_applicable` |
| Evidence current index | `applied|deferred|not_applicable` | applied이면 `passed`와 `authority_claim=false`, 나머지는 `not_applicable` |

필수 축의 `failed|blocked|not_applicable`은 `complete`와 양립할 수 없다. Changes 2~4C와 Change 5는 target `complete`의 필수 범위이므로 해당 검증을 `not_applicable`로 처리할 수 없다.

### Manual Validation

`Iris/_docs/refactor/residual_refactor/manual_runtime_validation_report.json`은 한 report 안에서 `case_class=runtime_ui|operator_contract`를 구분하고 class별 schema validation을 통과해야 한다. 공통 binding은 subject commit/tree, reviewer, 실행 시각을 포함한다. `runtime_ui` case는 tested package hash, Project Zomboid build, Iris version, OS, locale, expected/observed/status, screenshot 또는 Project Zomboid log evidence reference/hash를 필수로 한다. `operator_contract` case는 Project Zomboid build·locale·인게임 screenshot을 요구하지 않고 OS, shell, Python/tool version, exact command, expected/observed status와 exit code, stdout/stderr 또는 생성 artifact evidence reference/hash를 필수로 한다.

#### `runtime_ui` cases — Changes 2~4C

- Browser에서 category 순서, 검색, folded variant count, 대표 아이콘·이름, recipe 연결 표시를 확인한다.
- 같은 데이터로 반복 진입·재빌드해 대표 항목이 바뀌지 않는지 확인한다.
- Wiki food/core section에서 수치와 locale 문자열이 기존 화면 계약과 일치하는지 확인한다.
- Tooltip이 Tags → Connections → 선택적 UseCase → More 순서를 유지하고 성공 3~4줄, failure 2줄 조합을 보이는지 확인한다. 새 상한·절단 규칙이 생기지 않았는지 함께 확인한다.
- debug on/off에서 필수 오류는 동일하게 보이고 진단 로그만 달라지는지 확인한다.

#### `operator_contract` cases — Changes 5·7

- Python 파일럿 CLI의 `--help`, 잘못된 인자, 누락 파일, 성공 경로의 exit code와 오류 문구를 비교한다.
- current·historical·diagnostic evidence가 서로의 디렉터리 또는 manifest를 덮어쓰지 않는지 확인한다.

각 class의 모든 case가 `passed`여야 `class_summaries.<case_class>.validation_status=passed`이고, 두 class summary가 모두 `passed`여야 report의 최상위 `validation_status=passed`이다. class별 필수 실행 환경 부재, case 미실행, class에 맞는 증거 누락은 해당 class summary의 `blocked`이며 전체 closeout은 `partial`이다. production mutation과 operator-contract 변경이 모두 없는 계획으로 범위가 재승인된 경우에만 report-level `not_applicable`을 쓸 수 있으나, 현재 target에는 Changes 2~4C·5·7이 포함되므로 적용되지 않는다.

### Validation Limits

- 정적 테스트만으로 실제 Project Zomboid 런타임의 모든 데이터 범위와 UI 성능을 증명할 수 없다.
- Lua `pairs()` 비결정성은 제한된 permutation test로 회귀 가능성을 크게 줄일 수 있지만 모든 VM 구현을 증명하지는 못한다.
- historical 도구 중 외부 원본이나 과거 환경이 사라진 항목은 완전 재현이 불가능할 수 있다. 이 경우 missing dependency를 명시하고 성공으로 기록하지 않는다.
- BOM 제거가 Python 의미에는 영향을 주지 않아도 외부 시스템이 원본 파일 hash를 참조한다면 hash 변화가 발생한다. 해당 참조를 확인하지 못하면 BOM 정규화를 보류한다.
- `uv`, Lua syntax checker 또는 필수 runtime fixture가 없으면 해당 검증은 `blocked`이며 `passed`로 보고하지 않는다.
- Wiki의 올바른 사용자-visible 단위는 코드 구조만으로 확정할 수 없다. 별도 권위 결정 전에는 현재 출력을 보존한다.
- standalone Lua behavior harness와 disposable package 검증도 실제 Project Zomboid 인게임 검증을 완전히 대체하지 않는다. 따라서 closeout claim은 listed fixtures와 supported surfaces에 한정한다.

## 8. Risk Surface Touch

### Authority Files

- DVF authority 자체는 변경하지 않는다.
- current closure manifest와 validation manifest는 검증 정책 변경이 필요한 경우에만 수정한다.
- registry authority giant는 읽기·계약 조사만 허용하고 구조 변경은 하지 않는다.
- category presentation-order projection은 taxonomy authority가 아니며 classification 의미·membership를 소유하지 않는다.
- evidence current index는 비권위 projection이며 Artifact Registry, seal, cutover의 pointer가 아니다.

### Runtime Files

- Browser category/group/cache, Wiki rendering, Tooltip, public API, logging 경계를 수정한다.
- generated data를 해석하는 규칙을 새로 만들지 않으며 표시·projection 구조만 다룬다.

### Compatibility Layers

- `Iris/media/lua/client/Pulse/Iris/Logic/IrisDesc`의 one-line wrapper를 유지한다.
- Python 기존 CLI path, module name, bare import caller는 adapter로 보존한다.
- public Lua API의 이름과 반환 shape를 유지한다.
- copy-on-read로 반환 table identity가 달라지는 범위는 successor supported API report에 명시한다.

### Sealed Artifacts

- 읽기와 hash 비교만 허용한다.
- 이동, 재포맷, 삭제, 재생성을 하지 않는다.

### Public Surface

- 사용자-visible Browser 순서·대표 항목, Wiki 수치, Tooltip 문구가 영향을 받을 수 있어 characterization과 manual validation이 필수이다.
- intentional 표시 변화는 이 계획의 리팩토링 범위가 아니며 별도 결정이 필요하다.

## 9. Risk Analysis

| Risk | Impact | Mitigation |
|---|---|---|
| presentation projection이 taxonomy authority로 오인됨 | 계층 역전·의미 권위 이동 | 9개 Browser display order와 6개 Description priority를 중립 projection에서 분리하고 Logic → Browser require를 금지한다. |
| 대표 항목 comparator가 아이콘·설명을 바꿈 | 사용자-visible 회귀 | non-empty fullType의 case-sensitive locale-independent 오름차순을 oracle로 고정하고 permutation fixture를 사용한다. |
| copy-on-read가 hot path 할당을 늘림 | 런타임 성능 저하 | public boundary에만 복사하고 내부 private read-only path를 분리한다. |
| `getUseCaseLines`·Tooltip cache의 중첩 배열이 남음 | 내부 데이터 오염 지속 | wrapper와 nested arrays를 함께 복사하고 후속 호출 오염 테스트를 수행한다. |
| Wiki unit 정리가 값 환산으로 번짐 | 수치 오표시 | 첫 변경은 현재 출력 보존과 프로필 명명만 수행한다. 값 변경은 별도 결정으로 분리한다. |
| Tooltip 공통화가 hot path를 무겁게 함 | hover 지연 | 정적 사실 projection과 기존 cache를 유지하고 Detail ViewModel 생성을 금지한다. |
| Tooltip에 존재하지 않던 4줄 상한을 도입함 | 조건 분기·표시 회귀 | 삽입 지점과 성공 3~4줄/실패 2줄을 검증하고 maxLines·절단 규칙을 금지한다. |
| lazy debug가 필수 실패 정보를 숨김 | 진단·운영 회귀 | debug와 warn/error 경계를 분리하고 failure evidence test를 둔다. |
| package marker가 다른 `tools` namespace를 가림 | import 실패 또는 잘못된 모듈 로드 | repository root/v2 root clean-checkout import 행렬을 먼저 실행하고 충돌 시 별도 namespace를 사용한다. |
| full-gate가 receipt와 다른 interpreter로 실행됨 | sealed environment gate가 수집 전 실패하거나 잘못된 환경을 검증 | receipt path/hash를 검증하고 동일 executable을 orchestrator와 `--python`에 사용하며 `-B -s`, no user site/path를 강제한다. |
| 공통 I/O가 개행을 포함한 바이트 계약을 통일함 | hash·봉인 증거 파손 | file-open newline, LF/CRLF, trailing newline까지 계약별 helper와 golden byte test로 분리한다. |
| adapter가 exit code·오류 문자열을 바꿈 | 자동화 caller 회귀 | CLI success/failure fixture와 subprocess caller test를 유지한다. |
| 명명된 파일럿이 이미 closure 정원 안에 있어 새 leaf를 추가함 | governance 위반·Change 5 착수 불가 | Change 1 owner 판정과 zero-new-stem 5A를 선행하고 적격 closure-external 비-hub 후보 없이는 전체를 partial로 닫는다. |
| historical 파일을 dead code로 오판 | 재현 불가 | no-reference를 삭제 근거로 사용하지 않고 역할만 기록한다. |
| BOM 제거가 외부 hash를 바꿈 | 과거 증거 불일치 | 별도 변경 묶음, 참조 검사, 산출물 hash 비교 후 적용한다. |
| 증거 구조 변경이 기존 bundle을 훼손 | 감사 가능성 상실 | 기존 자료 보존, 새 bundle부터 역할 manifest 적용, sealed hash 검사. |
| evidence current index가 authority pointer로 소비됨 | 권위 경계 혼동 | schema와 claim scan에서 비권위 projection임을 강제한다. |
| diagnostic raw exit 1을 무시하거나 필수 실패로만 취급함 | 신규 결함 은폐 또는 closeout 영구 차단 | public raw exit는 유지하고 exact owner disposition adapter만 terminal status를 결정한다. |
| 필수 인게임 검증이 evidence 없이 생략됨 | public-facing 회귀를 자동 fixture만으로 complete 처리 | schema-valid manual runtime report를 필수 completion row로 둔다. |
| dirty working tree와 충돌 | 사용자 변경 손실 | 관련 없는 기존 수정은 건드리지 않고 변경 전후 diff를 경로별로 검토한다. |

## 10. Rollback Plan

1. 각 Change는 독립 변경 묶음으로 유지한다. Lua runtime 변경과 Python package 변경, BOM 정규화, evidence metadata 변경을 한 묶음에 섞지 않는다.
2. Change 2는 중립 presentation projection과 Browser cache를 제거하고 기존 compatibility table·group builder로 돌아갈 수 있어야 한다. taxonomy authority나 새 public field를 추가하지 않는다.
3. Change 3은 public getter의 복사 경계만 되돌릴 수 있게 내부 데이터 구조 변경과 분리한다.
4. Changes 4A, 4B, 4C는 각각 별도 변경 묶음과 rollback 지점을 가진다. Wiki formatter, Tooltip projection, debug gate를 함께 되돌리지 않는다.
5. Changes 5와 6C는 기존 module path와 CLI wrapper를 유지하므로 내부 위임을 제거해 원래 구현으로 복귀할 수 있어야 한다.
6. Change 6B BOM 정규화는 전용 변경 묶음 전체를 되돌린다. 다른 코드 변경과 line-level로 혼합하지 않는다.
7. evidence 변경은 새 plan-specific manifest·bundle·비권위 index만 되돌린다. sealed artifact나 기존 authority pointer를 복원 대상으로 삼지 않는다.
8. diagnostic disposition adapter와 owner allowlist는 raw runner와 분리해 되돌릴 수 있어야 하며 raw runner의 exit 의미는 수정하지 않는다.
9. rollback 후 Section 7의 자동 검증과 manual `runtime_ui`·`operator_contract` validation을 모두 다시 실행한다. 이전 subject에 결속된 manual report를 재사용하지 않는다.
10. 사용자의 기존 working tree 변경에는 `git reset --hard`, `git checkout --` 같은 파괴적 명령을 사용하지 않는다.

## 11. Governance Constraints

- [`Philosophy.md`](Philosophy.md)의 hub/spoke, compiler/viewer, compatibility-first 원칙을 지킨다.
- DVF System, Artifact Registry, Publish Boundary의 책임을 합치지 않는다.
- Iris Lua runtime은 표시·조회 역할을 유지하고 build-time 의미 추론을 런타임으로 옮기지 않는다.
- 현재 readpoint와 historical readpoint를 혼합하지 않는다.
- 완료된 선행 리팩토링을 새 계획의 필요성을 이유로 다시 열지 않는다.
- public output, CLI, serialization, hash, 오류 계약 변경은 명시적인 승인과 fixture 없이는 허용하지 않는다.
- generated Lua와 package projection은 직접 편집하지 않는다.
- sealed evidence와 기존 staging 파일은 승인 없이 삭제·이동·재기록하지 않는다.
- registry giant 분해는 이 계획에 포함하지 않는다.
- 역할이 `unknown`인 도구는 삭제·이동·공통화하지 않는다.
- classification/taxonomy 의미 authority는 Classification/Rule 계층에 남기고 Logic이 Browser UI를 직접 require하지 않는다.
- closure core 12·allowed tooling 4의 정원 확장은 본 계획의 out of scope이며 별도 reviewed plan 없이는 수행하지 않는다.
- evidence current index를 authority pointer로 취급하거나 기존 current manifest를 자동 대체하지 않는다.
- Tooltip에 명시적 줄 수 상한이나 새 절단 규칙을 추가하지 않는다.
- clean-checkout terminal gate는 receipt에 결속된 interpreter를 orchestrator와 `--python` 양쪽에 사용하고 `PYTHONNOUSERSITE=1`, no `PYTHONPATH`, `-B -s`를 강제한다.
- terminal 검증 명령이 exit code 0이 아니거나 도구가 없으면 `passed`로 기록하지 않는다. diagnostic raw exit 1은 terminal adapter가 exact owner disposition을 검증해 exit 0인 경우에만 비차단 evidence가 된다.
- 구현 도중 새 권위 판단이 필요해지면 보수적인 기존 동작을 유지하고 해당 변경을 중단한다.

## 12. Expected Closeout State

### Target Status

`complete` — Change 1, 2, 3, 4A, 4B, 4C, 5A, 5B, 6A, 7, 8의 `validation_status=passed`이고 Section 7의 자동·수동 필수 검증축이 모두 `passed`인 경우에만 가능하다. Change 5는 5A와 5B가 모두 `passed`일 때만 `passed`이다. Changes 6B·6C는 조건부이며 별도의 `application_status`와 대응 `validation_status`가 있어야 한다. registry giant 분해, 기존 evidence 대이동, no-reference 파일 삭제, 모든 도메인 package 이동까지 완료했다는 뜻은 아니다.

### Required Closeout Evidence

- 재현 명령·측정 기준이 결속된 inventory와 역할·실행 경로·직렬화/line-ending 계약 matrix
- `phase0_closure_slot_decision.json.validation_status=passed`, core 12·allowed tooling 4 유지, 적격 파일럿 identity
- presentation owner DAG, Logic → Browser edge 0, owner-approved UI/Browser → neutral Logic projection 1개, 그 외 신규 cross-layer edge 0 증거
- runtime behavior baseline/acceptance와 Browser comparator permutation 결과
- public API wrapper·nested-array·Tooltip cache mutation-isolation 및 predicate allocation 결과
- Wiki 단위/locale matrix, Tooltip branch matrix, lazy-debug 결과
- Python direct-script/module/import/CLI/line-ending matrix와 exact subject·`HEAD == targetCommit`·clean working tree preflight 및 결과를 결속한 receipt-bound clean-checkout binding report
- final supported API compatibility, protected surface, disposable package identity report
- `current_contract_report.json`, `historical_contract_report.json`, diagnostic raw/disposition report, full discovery·production Lua syntax 결과와 정확한 실행 명령
- `manual_runtime_validation_report.json.validation_status=passed`, `class_summaries.runtime_ui.validation_status=passed`와 case별 인게임 증거, `class_summaries.operator_contract.validation_status=passed`와 command/exit/artifact 증거
- evidence-role validator 결과와 current index non-authority claim scan
- BOM, 도메인 이동, evidence index의 closeout disposition
- 기존 sealed evidence 무변경 확인
- 변경된 [`DECISIONS.md`](DECISIONS.md), [`ARCHITECTURE.md`](ARCHITECTURE.md), [`ROADMAP.md`](ROADMAP.md)의 readpoint

### Partial Closeout Conditions

다음 중 하나가 발생하면 전체를 억지로 `complete`로 닫지 않고 완료된 Change와 차단된 Change를 구분해 `partial`로 기록한다.

- Wiki 단위의 사용자-visible 계약에 별도 권위 결정이 필요함
- Python package namespace가 clean checkout에서 충돌함
- closure slot owner 판정이 완료되지 않거나 `blocked`임
- 정원 외부의 적격 비-hub 후보가 없고 module/import 파일럿을 완료할 수 없음
- historical reproduction에 필요한 외부 입력 또는 도구가 없음
- BOM 파일의 외부 hash 소비자를 배제할 수 없음
- 파일럿 adapter가 기존 exit/error/byte 계약을 재현하지 못함
- receipt interpreter path/hash와 orchestrator 또는 `--python` identity가 불일치함
- diagnostic adapter가 raw report를 만들지 못하거나 새·미승인 finding을 `blocking=true`로 판정함
- manual `runtime_ui` 또는 `operator_contract` validation이 미실행·class별 증거 누락·환경 부재로 `blocked`임
- runtime behavior, supported API, protected surface, disposable package, clean-checkout을 포함한 필수 축 하나라도 `failed|blocked|not_applicable`임

### Follow-up Candidates, Not Completion Requirements

- `dvf_3_3_registry_authority_canonical_closure.py` 전용 분해 계획
- 추가 도메인 subpackage migration
- 기존 staging의 보존 기간·tracking·archive 정책
- no-reference 스크립트의 owner 확인 후 별도 폐기 심사
- 검증된 subprocess 후보의 단계적 함수 호출 전환
- Wiki 단위 표시값의 의도적 통합 결정
