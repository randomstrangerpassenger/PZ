# Iris 오프라인 빌드·검증 도구 및 잔여 런타임 구조개선 실행 계획

> 상태: Draft — 3차 WARN 및 후속 정밀 검토 수정 반영 / fresh review 대기
>
> 기준 시점: 2026-08-03
>
> 양식: [`PLAN_TEMPLATE.md`](PLAN_TEMPLATE.md)
>
> 입력 로드맵: `Iris 오프라인 빌드·검증 도구 및 잔여 런타임 구조개선 종합 로드맵`
>
> 선행 기준: [`iris_residual_refactoring_consolidated_plan.md`](iris_residual_refactoring_consolidated_plan.md), [`iris_clean_checkout_full_repository_validation_reproducibility_authority_closure_plan.md`](iris_clean_checkout_full_repository_validation_reproducibility_authority_closure_plan.md)

## 1. Objective

Iris의 가장 큰 잔여 구조 부채인 오프라인 Python 빌드·검증 도구 계층을 먼저 안정화하고, 그 이후에만 Lua 런타임의 실제 잔여 책임을 국소적으로 분리한다.

구체적 목표는 다음과 같다.

1. current-required validation, full-gate가 호출하는 producer와 본 계획에서 실제 migration하는 active producer의 모든 임시 출력이 repository 밖의 명시적 disposable root에만 기록되도록 한다.
2. 정확한 tracked commit을 입력으로 하는 clean-checkout 실행에서 성공·실패 어느 경로에서도 source checkout mutation과 실행 잔여물이 발생하지 않게 한다.
3. helper migration 전에 JSON·JSONL·해시·timestamp·CLI·subprocess·receipt의 현재 계약을 바이트, 오류, exit-code 단위로 고정한다.
4. 이미 존재하는 `Iris/build/description/v2/tools/common/paths.py`를 우선 채택하고, 직접 `parents[N]` 계산과 `sys.path` bootstrap을 leaf batch 단위로 줄인다.
5. 직렬화 구현은 하나의 전역 writer로 강제하지 않고 동일 byte contract를 공유하는 producer family 안에서만 공통화한다.
6. 반복 pipeline, validator, evidence producer, one-shot, historical/diagnostic 도구와 산출물 수명주기를 분류하되, 분류만으로 기존 evidence를 이동하거나 삭제하지 않는다.
7. 런타임에서는 이미 완료된 Browser query/index 분해와 `IrisData` adapter 경계를 보존하고, 코드에 실제로 남은 Wiki current/legacy renderer 공존과 protected-call 차이만 characterization 이후 국소적으로 정리한다.

이 계획의 성공 지표는 전체 Python 파일 수나 staging 용량의 즉시 감소가 아니다. 성공은 **명시된 execution denominator의 write containment, byte/hash determinism, 기존 CLI·import·Lua API 호환성, current/historical/diagnostic 권위 분리, 재현 가능한 clean-checkout 검증**으로 판단한다. inventory-only historical/one-shot 도구 전체를 자동 실행·격리 범위로 확대하지 않는다.

이 문서는 선행 리팩토링 계획의 완료 항목을 재개방하지 않는다. 특히 이미 수용된 Browser index/query/filter/variant 모듈, `StaticData.getLegacyIrisData()` adapter, copy-on-read, deterministic presentation projection, Tooltip 분리와 `compose_layer3_io` 계약을 현재 기준선으로 사용한다.

---

## 2. Scope

### In Scope

#### A. 실행 격리와 현재 계약 고정

- exact tracked commit 기반 producer/test inventory
- producer별 read set, write set, 기본 output 경로와 mutation 권한 분류
- current-required validation, full-gate producer와 migration 대상으로 선택된 active producer에 repository-external work/result/output root 강제
- 성공·실패 경로의 source checkout status 및 ignored-state 불변 검증
- JSON·JSONL·text·hash·timestamp·stdout·stderr·exit code golden characterization
- Run A/B deterministic result 비교

#### B. Python 공통 기반의 점진 채택

- `tools/common/paths.py`의 anchor 보강과 leaf batch 채택
- 직접 `Path(__file__).resolve().parents[N]` 및 개별 `sys.path.insert` 축소
- 동일 계약 family 내부의 JSON·JSONL·hash helper 공통화
- CLI bootstrap, subprocess 실행, receipt 생성의 중복 조사와 제한적 공통화
- 기존 direct-script, `python -m`, package import, 필요한 bare import 계약 보존
- current core 12개와 allowed tooling 4/4 경계에 대한 변경 전 preflight

#### C. 도구 및 산출물 역할 분류

- current/active pipeline
- validator
- report/evidence producer
- one-shot migration 또는 cutover 도구
- historical reproduction 도구
- diagnostic/advisory 도구
- test fixture/tooling
- owner 미확정 도구
- disposable intermediate, reproducibility fixture, sealed/closeout evidence, current-authority artifact, package projection, backup/sandbox/probe 산출물 분류

#### D. Lua 런타임의 잔여 국소 분리

- `IrisWikiSections.lua`의 legacy/current renderer family 내부 분리와 기존 facade 유지
- `IrisBrowserData.lua`에 남은 candidate build와 build-state 책임의 추가 분리 필요성 판정
- 직접 `pcall(buildCandidateCache)`과 `IrisProtectedCall.data()`의 return/log/fallback 동등성 고정 및 조건부 전환
- 기존 `StaticData.getLegacyIrisData()`와 `IrisBrowserVariantIndex.getGroupVariants()` adapter 경계 보존
- supported module path, 함수명, 서명, 반환 shape와 렌더링 순서 보존

### Explicitly Out Of Scope

- `dvf_3_3_registry_authority_canonical_closure.py` giant 분해
- Registry Authority, Registry Runtime Compatibility, DVF Body Compiler, Publish Boundary의 책임 재설계 또는 통합
- generated Lua chunk, `IrisData.lua`, `IrisClassifications.lua`, index data, package projection의 직접 편집
- current core 12개 또는 allowed tooling 4개의 편의상 무승인 확장
- `Iris/build/package/Iris`의 현재 ignored read-only projection 정책 변경
- 기존 staging, sealed evidence, historical artifact의 삭제·이동·Git tracking 해제
- artifact store와 Git LFS 중 하나의 즉시 채택
- repository-wide UTF-8 BOM 정규화
- repository-wide `.gitattributes` 또는 newline 정책 변경
- historical evidence 재직렬화 또는 봉인 산출물 일괄 재생성
- 모든 Python 스크립트의 일괄 이동, 일괄 import 변경 또는 일괄 helper 교체
- 모든 subprocess의 함수 호출 전환
- legacy compatibility surface의 즉시 삭제
- 런타임 taxonomy, evidence, description, quality 또는 publish 정책 변경
- release, Workshop, B42 또는 deployment readiness 선언

---

## 3. Non-Goals

- 구조를 보기 좋게 만들기 위해 현재 authority 또는 evidence lifecycle을 변경하지 않는다.
- 서로 다른 JSON/JSONL 바이트 계약을 하나의 “표준 포맷”으로 강제하지 않는다.
- helper 함수 수 감소나 디렉터리 이동 수를 단독 성공 기준으로 삼지 않는다.
- current 검증의 성공을 이유로 historical/diagnostic 분모를 축소하지 않는다.
- staging 용량 문제를 해결한다는 이유로 owner와 retention 근거가 없는 파일을 삭제하지 않는다.
- package mirror를 source writer 또는 reverse-merge authority로 사용하지 않는다.
- 런타임에서 source를 재검증하거나 설명을 재생성하지 않는다.
- Iris를 의미 추론, 추천, 비교 또는 품질 판정 UI로 확장하지 않는다.
- 기존 public Lua API, Python CLI, exit code와 오류 유형을 의도적으로 변경하지 않는다.
- raw `pcall()`의 존재 자체를 결함으로 간주하지 않는다. boundary별 정책 동등성이 확인된 호출만 전환한다.
- 이미 분리된 Browser query/index/filter/variant 책임을 다시 설계하지 않는다.

---

## 4. Assumptions

### 4.1 Authority and Execution Assumptions

- [`Philosophy.md`](Philosophy.md)가 최상위 권위이며 Iris는 100% Lua runtime viewer와 offline producer/validator를 가진 독립 spoke로 남는다.
- [`DECISIONS.md`](DECISIONS.md), [`ARCHITECTURE.md`](ARCHITECTURE.md), [`ROADMAP.md`](ROADMAP.md), 모듈 authority 문서와 승인된 선행 계획이 이 계획보다 우선한다.
- `Iris Repository Validation / Clean-Checkout Reproducibility Authority`는 DVF/QG/Registry/Publish Boundary와 별개의 repository-level validation authority다.
- 현재 residual refactoring 상태는 `partial`이다. `c1fa281e` exact subject의 receipt-bound full-gate와 수동 Project Zomboid UI evidence가 결속되기 전에는 해당 선행 계획을 `complete`로 승격하지 않는다.
- `c1fa281e` full-gate는 predecessor residual-refactor claim만 닫는다. 이 계획의 successor full-gate는 별도 subject·result root·receipt·claim ID를 가지며 predecessor 검증을 자동 대체하지 않는다.
- plan authoring 시점의 primary working tree는 기존 사용자 변경으로 dirty하다. 따라서 Phase 0의 authoritative baseline과 이후 producer 실행은 dirty primary tree가 아니라 exact commit의 disposable clean checkout에서 얻는다.
- 기존 sealed evidence는 수정하지 않는다. 새 검증 근거는 append-only successor 또는 별도 closeout evidence로 기록한다.

### 4.2 Codebase Inspection Readpoint

다음 값은 2026-08-03의 sealed residual inventory와 현재 checkout 재조사를 분리한 계획 작성 기준값이다. 서로 다른 subject·root·inclusion rule의 숫자는 합산하거나 대체하지 않는다. Phase 0은 각 집합에 denominator ID, subject commit/tree, root, inclusion/exclusion rule과 scan method를 부여해 다시 측정한다.

| 항목 | 조사값 | 계획 해석 |
|---|---:|---|
| sealed Phase 0 `tools/build` recursive Python | 496개 | `phase0_inventory.json`의 subject `c8b96e4`, 모든 descendant 포함 |
| sealed final `tools/build` root-direct Python | 484개 | `final_inventory.json`의 `counts.build_tools_python_root_direct` 값. sealed `tools` row 집합은 recursive 497행이고 root-direct 484는 그 subset |
| 현재 dirty-tree physical probe | recursive 497개 / root-direct 484개 | untracked/ignored 파일을 포함한 비권위 관찰값이며 exact clean subject 분모가 아님 |
| 현재 `c1fa281e` tracked probe | recursive 250개 / root-direct 237개 | Git tree 기준 분모. physical probe나 sealed predecessor inventory를 대체하지 않음 |
| current closure | core 12개 / allowed tooling 4개 | recursive 도구 분모의 권위 subset이지 `496 - 484 = 12` 같은 산술 partition이 아님 |
| sealed final `tools/build` physical line | recursive 240,057줄 | blank/comment 포함. 별도 root-direct probe 231,132줄과 집합이 다름 |
| `sys.path` 조작 파일 | sealed final 151개 | 분산 bootstrap 후보 분모이며 shared-module consumer와 함께 판정 |
| `argparse` 사용 파일 | sealed final 273개 | 기존 CLI surface 보존 대상 |
| `subprocess` 사용 파일 | inventory 51개 / text mention 52개 / direct import 50개 | scan method에 따라 달라지므로 Phase 0 AST denominator를 기준으로 사용 |
| 직접 `parents[N]` 계산 파일 | 285개 | path migration 후보 분모 |
| `main()` 정의 파일 | 427개 | entrypoint/role 분류 필요 |
| `load_json` 정의 | 147개 | 계약 family census 필요 |
| `write_json` 정의 | 112개 | byte/hash 변경 위험 surface |
| `load_jsonl` 정의 | 102개 | BOM/duplicate/empty-line/error 계약 조사 대상 |
| `now_iso` 정의 | 35개 | timestamp 결정성 및 receipt 의미 조사 대상 |
| `tools/common/paths.py` 정적 importer | 1개 | `compose_layer3_text.py`만 직접 import |
| sibling path helper | 1개 | `export_registry_runtime_records.py`는 별도 `registry_runtime_record_paths.py`를 소비 |
| `clean_checkout_test_paths` importer | 현재 text scan 22개 | 접근 불가 ignored 경로 등 관찰 ceiling을 함께 기록하고 Phase 0에서 재확정 |
| primary ignored-path probe | `tests/tmpg_zgo695`에 관찰자·권한별 성공/`UnauthorizedAccessException` 결과가 모두 보고됨 | lock이 지속될 수 있으므로 매 run preflight와 exclusion receipt 필요. 현재 접근 성공을 전제하지 않음 |
| 기존 common/path support rows | sealed final inventory 15개 | 13개 `*_common.py`와 output/path support 2개. 검토안은 consumer 96/max fan-in 48, final-inventory 재합성은 all-caller 98/max 49 및 tools-only 92/max 48로 scan 차이가 있어 Phase 0 exact census에서 재결속 |
| sealed unknown-role seed | 55행 | Phase 0/final inventory의 `unknown_paths` 및 `primary_roles.unknown` 기준선. Change 6 threshold가 유지·축소·확대되는 이유를 owner decision에 기록 |
| `tools/build` 하위 디렉터리 | 도메인 1개 + `__pycache__` | 대부분의 root-direct 스크립트가 flat root에 존재 |
| registry giant | 553,718 bytes / 13,220 physical lines | 본 계획에서 분해 금지 |
| `staging/` | 5,212 files / 4,586,335,137 bytes | 약 4.27 GiB, Iris 전체의 약 96.8% |
| tracked staging | 3,405 files | retention 분류 없이 삭제·이동 금지 |
| tracked bytecode / temp-cache probe | tracked `.pyc` 1개, `v2/.tmp_tests` 및 여러 `__pycache__` | Change 6에서 owner·tracked·sealed 상태를 구분하며 일괄 cleanup 근거로 사용하지 않음 |

### 4.3 Existing Infrastructure and Already-Completed Boundaries

- `Iris/validation/clean_checkout/contracts/output_policy.json`은 repository-local generated output을 금지하고 external subroot와 환경 격리를 정의한다.
- `Iris/validation/clean_checkout/run_iris_clean_checkout_validation.py`는 external `work_root`, `result_root`, source status snapshot, ignored-state 비교, disposable checkout cleanup, receipt를 이미 구현한다.
- `validate_external_environment()`은 orchestrator `sys.executable`, `--python`, immutable receipt interpreter path/hash, dedicated venv와 package manifest identity를 fail-close 비교한다. 또한 outer process의 `PYTHONNOUSERSITE=1`과 cleared `PYTHONPATH`를 요구한다.
- `output_policy.json`은 child execution에 `GIT_OPTIONAL_LOCKS=0`, `PIP_NO_INDEX=1`, `PYTHONDONTWRITEBYTECODE=1`, `PYTHONHASHSEED=0`, `PYTHONNOUSERSITE=1`을 요구하고 `PYTHONHOME`, `PYTHONPATH`, `PYTEST_ADDOPTS`를 clear한다.
- `Iris/build/description/v2/tests/clean_checkout_test_paths.py`는 external test root helper를 제공하며 현재 text scan importer는 22개다. 접근 불가 ignored 경로를 포함한 관찰 ceiling을 기록한 뒤 Phase 0 exact census에서 분모를 재확정한다. 나머지 테스트가 모두 unsafe하다는 뜻은 아니며, TemporaryDirectory 사용과 write-free test를 별도 분류한다.
- `Iris/build/description/v2/tools/common/paths.py`는 stdlib-only leaf로 `V2_ROOT`, `BUILD_ROOT`, `DATA_DIR`, `OUTPUT_DIR`, `STAGING_DIR`를 제공한다.
- sealed `final_inventory.json`은 `tools/build` 안에 15개의 common/path support row를 기록한다. 여기에는 13개 `*_common.py`, `guard_dvf_3_3_vnext_output_paths.py`와 `registry_runtime_record_paths.py`가 포함된다. 다수 row의 owner는 `unconfirmed`이고 current/historical/diagnostic 관계와 static fan-in은 subject·test 포함 여부에 따라 달라진다.
- `registry_runtime_record_paths.py`는 `export_registry_runtime_records.py`가 소비하는 sibling path helper이며 `tools/common/paths.py` importer로 계산하지 않는다.
- 신규 `tools/common/` helper는 이 기존 sibling support 계층의 대체물로 자동 간주하지 않는다. provider/consumer, owner, current-route 관계와 contract overlap을 먼저 결정한다.
- `compose_layer3_io.py`는 `unsorted-json-platform-newline-with-trailer`와 8192-byte SHA-256 chunk 계약을 가진 contract-specific helper다. 이를 repository-wide canonical writer로 승격하지 않는다.
- current route import closure는 core 12개와 allowed tooling 4/4다. 새 current-route module stem은 별도 owner/closure 판정 없이는 추가하지 않는다.
- `Iris/build/package/Iris`는 현재 Git 추적 파일 0개의 ignored read-only projection이다. 이 계획은 해당 정책을 변경하지 않는다.
- Browser는 이미 `CategoryIndex`, `Filters`, `ItemIndex`, `ClassificationIndex`, `Query`, `VariantIndex`로 분리되어 있다. 이 계획은 이 분리를 다시 수행하지 않는다.
- legacy `IrisData` 접근은 이미 `StaticData.getLegacyIrisData()`와 `IrisBrowserVariantIndex.getGroupVariants()` adapter 뒤에 있다. `IrisData.lua` 직접 분해는 필요 조건이 아니다.
- `IrisWikiSections.lua`에는 legacy family와 current family가 한 facade 구현 파일에 공존한다. public inventory는 둘 모두 supported wrapper로 기록한다.
- `IrisBrowserData.ensureReady()`에는 candidate build 전체를 감싸는 직접 `pcall(buildCandidateCache)`이 남아 있다. 반면 per-item data call은 `ProtectedCall.data()`를 사용한다. 두 경계는 로그와 fallback을 비교한 뒤에만 통합한다.

### 4.4 Roadmap Conflict Resolutions

| 로드맵 미결 항목 | 본 계획의 판정 |
|---|---|
| C-01 output 격리와 golden characterization의 선후 | 둘을 Phase 0/1 공동 진입 게이트로 둔다. exact pre-change commit의 disposable clone에서 characterization과 write-set census를 먼저 기록하고, 즉시 output containment를 고친다. 두 근거가 모두 없으면 광범위 helper migration을 시작하지 않는다. |
| C-02 기존 path helper와 신규 common module 순서 | `tools/common/paths.py` 채택을 독립 선행 change로 둔다. 신규 I/O module은 path/import/closure 검증 뒤, 동일 byte contract family와 owner가 고정된 경우에만 추가한다. |
| C-03 newline/BOM/`.gitattributes` 범위 | producer별 기존 byte contract 보존이 기본이다. writer 내부 newline 변경도 golden/hash 승인이 있을 때만 수행한다. repository-wide BOM 및 `.gitattributes` 변경은 계속 HOLD다. |
| C-04 `build/package` tracking | 현재 ignored read-only projection 정책을 그대로 유지한다. 이동·tracking 변경 없음. |
| C-05 staging 장기 저장 위치 | 본 계획은 role/retention inventory와 owner decision packet까지만 만든다. artifact store, LFS, repository retention, 삭제 중 하나를 임의로 선택하지 않는다. |
| C-06 기존 sibling support와 신규 `tools/common/` 관계 | Change 1에서 기존 common/path provider·consumer·fan-in·owner·contract를 먼저 고정한다. Changes 3–4는 어느 계층이 각 contract를 소유하는지 owner decision이 나오기 전에는 source-changing migration을 시작하지 않는다. |
| C-07 Change 2 착수 자격 | revised plan의 fresh review가 source-changing scope를 승인하고 Change 1이 exact denominator, shared-module census, write-set과 golden을 생성한 뒤 output isolation을 시작할 수 있다. Change 2는 새 shared helper나 owner 변경을 도입하지 않으며, 해당 변경이 필요해지는 순간 Changes 3–4 gate로 되돌아간다. |
| C-08 Public-Facing Output Surface | `Conditional touch — no intentional semantic change`로 판정한다. Change 7은 renderer code path를 수정하므로 surface는 touch되지만 equality와 manual UI evidence 없이 의미 보존을 주장하지 않는다. |
| C-09 full-gate interpreter/environment | 직전 Critical을 receipt interpreter direct execution, required/cleared environment와 exact runner/common identity entry gate로 해소한다. `uv run python`을 terminal full-gate orchestrator에 사용하지 않는다. |
| C-10 compare evidence writer | 직전 Critical을 stdout/stderr byte-preserving 분리, BOM 없는 JSON, 즉시 input/execution hash binding과 focused writer determinism test로 해소한다. PowerShell `2>&1` object capture와 `Set-Content -Encoding utf8` receipt 작성은 금지한다. Windows PowerShell 5.1의 `1>`/`2>`만으로 byte preservation을 가정하지 않는다. |
| C-11 predecessor/successor 상태 표현 | 새 status axis를 만들지 않는다. 서로 다른 `claim_id` row가 기존 `closeout_state` enum과 각 validation ceiling/non-claims를 사용한다. |
| C-12 launcher failure receipt | 직전 Critical을 all-path failure receipt 설계로 해소한다. success, preflight failure, Python 실행 전 exception과 gate nonzero 모든 경로에서 environment 복원 뒤 receipt를 먼저 기록하고 원래 실패를 전파한다. receipt write failure는 gate failure와 별도 상태로 보존하며, 구현·fixture 반영은 §4.5 Change 2 진입 게이트로 남긴다. |
| C-13 runtime/Lua/package driver identity | 직전 Major 지적을 exact-subject driver binding 설계로 해소한다. E/F와 manual package는 해당 predecessor/successor checkout의 absolute driver path를 사용하고 driver/harness/package blob과 working materialization hash를 함께 기록하며, 구현·fixture 반영은 §4.5 Change 2 진입 게이트로 남긴다. |

### 4.5 Change Entry Gates

- Change 1은 read-only inspection과 validation support authoring 범위로 시작할 수 있다.
- Change 1B는 **pre-Change-2 support-only hardening**이다. Receipt-bound launcher, deterministic compare launcher/writer, all-path failure/environment fixture, byte comparison과 actual-import identity fixture는 Change 2의 producer/output mutation이 아니라 이 선행 단위에서 구현·검토한다.
- source-changing Change 2 이후 작업은 Change 1B의 receipt-bound launcher all-path failure receipt, required/cleared environment 복원, exact runner/common actual-import identity와 deterministic compare writer의 구현·fixture가 반영되고 이 수정본 및 Change 1B implementation의 fresh review가 승인되기 전에는 시작하지 않는다. Exact runtime/Lua/package driver binding은 Change 7의 pre-entry gate에서 구현·검증한다.
- Change 2는 위 Critical gate, review 승인과 exact commit baseline, denominator IDs, shared-module provider/consumer census, write-set과 golden contract가 모두 생성되고 `output_isolation_batch_registry.json`의 선택 row 전부가 owner-bound/role-known으로 닫힌 뒤에 시작한다. 이 gate는 registry가 승인한 output-isolation mutation만 허용한다.
- Changes 3~5의 helper migration은 Change 2에서 대상 producer의 output-root containment와 source non-mutation이 확인된 뒤에만 시작한다.
- Changes 3–4는 기존 `tools/build/*_common.py`/path support와 `tools/common/`의 owner·current-route·contract-overlap decision이 추가로 닫히기 전에는 source-changing migration을 시작하지 않는다.
- 새 Python module stem이 current route에 들어갈 가능성이 있으면 `round3_active_core_closure.json`의 owner/slot 결정을 먼저 받는다. 편의상 core 12 또는 tooling 4/4를 확장하지 않는다.
- Change 5의 receipt consolidation mutation은 Change 1에서 owner/caller/role이 결속되고 Changes 2–4를 통과한 선택 batch에만 적용한다. inventory에서 탐지한 subprocess 파일 전체를 일괄 migration 분모로 삼지 않는다.
- Change 6의 물리적 파일 이동이나 retention mutation은 역할 분류만으로 승인되지 않는다. 별도 owner 결정이 없는 경우 inventory-only로 닫는다.
- Change 7의 runtime mutation은 exact pre-change subject에서 자동 Baseline 2종, supported API/protected/package manifest와 pre-mutation 수동 UI 5-case가 external baseline bundle에 결속된 뒤에만 시작한다. post-mutation baseline 재생성은 predecessor baseline을 대체할 수 없다.

---

## 5. Repository Areas Affected

### Code

기본 수정 후보는 다음과 같다. 각 batch의 exact 파일은 Change 1 manifest에서 먼저 고정한다.

- `Iris/validation/clean_checkout/`
- `Iris/validation/clean_checkout/contracts/output_policy.json` 또는 additive successor contract
- `Iris/validation/clean_checkout/run_iris_clean_checkout_validation.py`
- `Iris/validation/clean_checkout/iris_clean_checkout_validation_common.py`
- owner 승인 후 additive `Iris/validation/clean_checkout/invoke_receipt_bound_full_gate.ps1`
- owner 승인 후 additive `Iris/validation/clean_checkout/invoke_deterministic_compare.ps1`
- `Iris/_docs/round3/round3_run_contract_tests.py`
- `Iris/build/description/v2/tests/clean_checkout_test_paths.py`
- `Iris/build/description/v2/tools/common/paths.py`
- `Iris/build/description/v2/tools/build/`의 Change 1에서 선택된 leaf producer/validator/entrypoint
- `Iris/media/lua/client/Iris/UI/Wiki/IrisWikiSections.lua`
- 계획 승인 후 추가할 수 있는 internal Wiki renderer module
- `Iris/media/lua/client/Iris/UI/Browser/IrisBrowserData.lua`
- 계획 승인 후 추가할 수 있는 internal Browser candidate/state module
- `Iris/media/lua/client/Iris/Util/IrisProtectedCall.lua` (정책 변경이 아니라 characterization에서 필요가 입증된 최소 수정만)
- `Iris/media/lua/client/Iris/API/StaticData.lua` 및 `IrisBrowserVariantIndex.lua` (기본값은 no-change 검증)

### Tests

- `Iris/validation/clean_checkout/tests/test_iris_clean_checkout_validation.py`
- receipt interpreter/environment/runner identity 및 compare stdout/stderr/BOM/determinism fixture
- `Iris/build/description/v2/tests/`
- exact pilot producer별 golden/negative fixture test
- `Iris/test/lua/pre_refactor_characterization_harness.lua`
- `Iris/test/lua/residual_refactor_acceptance_harness.lua`
- `Iris/test/run_residual_refactor_acceptance.ps1`
- `Iris/test/validate_residual_refactor_surfaces.ps1`
- `Iris/build/description/v2/tests/test_protected_call_boundary_contract.py`
- `Iris/build/description/v2/tests/test_iris_legacy_surface_acceptance.py`
- `Iris/build/description/v2/tests/test_iris_browser_state_selection_search_acceptance.py`
- `Iris/build/description/v2/tests/test_iris_core_refactor_closeout.py`

### Docs

- 이 문서
- `docs/ROADMAP.md`, `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`는 closeout evidence가 해당 current state 변경을 실제로 뒷받침할 때만 additive update 후보가 된다.
- build-tool role manifest와 retention owner decision이 사용자-facing guidance가 필요한 경우 별도 docs packet을 추가한다.

### Config

- `Iris/_docs/round3/round3_active_core_closure.json`은 새 current-route dependency가 승인된 경우에만 변경한다.
- `Iris/_docs/round3/current_route_required_validations.json`은 새 required test/artifact를 current route에 채택하는 별도 reviewed step에서만 변경한다.
- `.gitignore`와 `.gitattributes`는 본 계획의 기본 수정 대상이 아니다.
- package projection tracking policy는 변경하지 않는다.

### Generated Artifacts

- repository 밖의 disposable work root와 result root
- helper behavior inventory
- producer read/write-set inventory
- CLI/import/caller topology manifest
- denominator registry와 shared-module provider/consumer/fan-in manifest
- `<external-phase0-result-root>/manifests/output_isolation_batch_registry.json`
- `<external-phase0-result-root>/manifests/receipt_migration_batch_registry.json`
- serialization contract matrix
- golden byte/hash/exit-code fixtures
- Run A/B canonical result와 receipt
- predecessor/successor full-gate의 성공·실패 경로 orchestration receipt, operator attempt log와 interpreter/environment/runner/common identity binding
- compare writer 채택·변경 시 focused attempt A/B의 분리된 stdout/stderr, BOM 없는 receipt와 determinism report
- tool role manifest
- output ownership/retention manifest
- exact pre-change runtime baseline bundle과 successor acceptance/closeout evidence 및 각 runtime/Lua driver·harness identity manifest
- 서로 분리된 pre-mutation/post-mutation package manifest와 Project Zomboid UI evidence
- closeout validation matrix와 claim-boundary report

Generated evidence를 tracked durable surface로 승격하려면 owner, role, hash mode와 authority effect를 별도로 기록한다. external result root의 존재만으로 authority가 생기지 않는다.

---

## 6. Planned Changes

### Change 1 — Phase 0: Exact Baseline, Producer Census, and Golden Contract Lock

**Purpose:**

helper나 output 경로를 변경하기 전에 현재 실행 경로, write surface와 byte/error 계약을 exact commit에 결속한다.

**Files:**

- `Iris/validation/clean_checkout/`의 inventory/characterization support
- `Iris/validation/clean_checkout/tests/test_iris_clean_checkout_validation.py`
- repository-external Phase 0 result root
- owner 승인을 받은 경우 additive inventory manifest

**Implementation Notes:**

1. primary dirty working tree에서는 producer를 실행하지 않는다. exact tracked commit의 짧은 disposable checkout을 사용한다.
2. `tools/build` Python 집합을 하나의 숫자로 고정하지 않고 최소한 `recursive_physical`, `root_direct_physical`, `recursive_tracked`, `current_core`, `allowed_tooling` denominator ID로 분리한다. 각 ID에 subject commit/tree, root, inclusion/exclusion rule, scan method와 값을 기록한다.
3. 각 tool row에 다음을 기록한다.
   - path, SHA-256, physical line, import/package form
   - direct-script/`-m`/bare import 필요 여부
   - caller, subprocess caller, test caller, 문서 command reference
   - current core/allowed tooling/current test/historical/diagnostic 관계
   - `sys.path`, `parents[N]`, argparse, subprocess, write API, local helper 정의
   - shared-module provider/consumer 여부, 소비 provider stem, static fan-in, tools-only/test caller 분리
   - provider owner, current-route 관계, serialization/path/receipt contract ID와 `tools/common/` overlap 후보
4. 각 executable producer를 `read-only validator`, `disposable producer`, `explicit authority writer`, `historical replay`, `unknown` 중 기존 권위 용어로 환원 가능한 역할에 매핑한다. 역할 미확정 항목은 실행·이동·삭제하지 않는다.
5. write-set은 tracked, nonignored untracked, ignored/local 상태를 분리하고 import-time write와 execution-time write를 구분한다.
6. representative contract family를 선택해 다음을 golden으로 기록한다.
   - encoding과 BOM
   - duplicate key 처리
   - `ensure_ascii`
   - key ordering, indentation, separator
   - LF/CRLF/platform newline
   - trailing newline
   - atomic replace/retry와 임시 파일
   - missing-file/error type
   - stdout/stderr와 exit code
   - hash chunking 및 final SHA-256
7. historical artifact를 현재 동작의 authority로 복귀시키지 않는다. golden은 exact pre-change implementation 실행 결과와 tracked fixture에 결속한다.
8. current core 12와 allowed tooling 4/4의 dependency closure를 별도 subset denominator로 기록하고 recursive/root-direct 수치와 산술적으로 혼합하지 않는다.
9. sealed inventory의 common/path support row를 seed로 사용하되 현재 exact subject에서 provider 존재, caller union과 fan-in을 다시 계산한다. scan 차이는 누락으로 숨기지 않고 method-specific result로 보존한다.
10. census 종료 후 owner가 Change 5 대상만 선택해 `<external-phase0-result-root>/manifests/receipt_migration_batch_registry.json`에 기록한다. 각 batch는 `batch_id`, owner, source denominator ID/hash, ordered row path/hash, 선택/제외 근거, current-route/authority 관계와 approved mutation scope를 가진다. 이 registry 자체는 current authority가 아니다.
11. Change 2 output-isolation 대상은 별도 `<external-phase0-result-root>/manifests/output_isolation_batch_registry.json`에 기록한다. 각 row는 path/Git blob/working SHA-256, caller boundary, source denominator ID/hash, owner, role, observed write-set, golden contract ID와 승인된 mutation scope를 가진다. 선택 row의 `owner_unknown`과 `unknown_role`은 모두 0이어야 하며 이 registry에 없는 producer는 Change 2에서 수정하지 않는다.
12. output isolation registry 전체는 schema ID, absolute external path, raw SHA-256, census/denominator manifest path/hash, decision owner와 owner 사전승인 근거를 가진 ratification receipt에 결속한다. Change 2 attempt는 사용한 exact registry path/hash와 ratification receipt path/hash를 기록하고, 승인 후 registry 또는 census/denominator hash가 달라지면 source mutation 전에 fail-close한다.

**Validation:**

- inventory rerun identity
- source census output의 schema, denominator ID, inclusion/exclusion rule과 subject binding 검사
- shared-module provider/consumer edge, tools-only/test fan-in과 owner 미확정 상태 검사
- representative producer Run A/B byte-for-byte 및 SHA-256 equality
- import-only 실행의 write count 0
- source checkout before/after status equality
- owner 미확정 파일 count와 이유 공개
- receipt migration batch registry의 owner, denominator hash, ordered row identity와 census rerun binding
- output isolation batch registry의 선택 row 전부에 owner/role/write-set/golden binding이 있고 `owner_unknown=0`, `unknown_role=0`인지 검사
- output isolation registry schema/path/raw hash, census/denominator hash와 owner-ratification receipt가 일치하며 registry drift injection이 mutation 전에 차단되는지 검사

---

### Change 1B — Pre-Change-2 Support-Only Receipt and Compare Hardening

**Purpose:**

Change 2의 producer/output mutation 전에 launcher와 compare evidence 자체가 모든 실행 경로를 재현 가능하게 기록하도록 구현하고 검토한다. 이 단계는 기존 producer의 output path, authority, current-route dependency를 변경하지 않는다.

**Files:**

- `Iris/validation/clean_checkout/invoke_receipt_bound_full_gate.ps1`
- `Iris/validation/clean_checkout/invoke_deterministic_compare.ps1`
- `Iris/validation/clean_checkout/run_iris_clean_checkout_validation.py`
- orchestration/compare receipt schema와 validation fixture
- `Iris/validation/clean_checkout/validate_iris_clean_checkout_validation.py`
- `Iris/validation/clean_checkout/tests/test_iris_clean_checkout_validation.py`

**Implementation Notes:**

1. raw parameter value만으로 최소 receipt state를 먼저 초기화한다. interpreter, repository, runner, policy, common module, planned argv 해석은 모두 launcher의 단일 `try/catch/finally` 안에서 수행한다. PowerShell parameter-binding 이전 실패는 all-path receipt claim 밖이며 validation ceiling에 명시한다.
2. native gate nonzero는 발생 즉시 primary outcome으로 고정한다. 이후 environment restore 또는 receipt 보조 수집이 실패해도 원래 native exit/failure가 primary이고 후속 실패는 `secondary_failures`에만 추가한다.
3. environment snapshot은 변수별 `absent|empty|value`를 구분한다. required/set 및 cleared variable 적용 도중의 부분 실패도 이미 저장된 전체 원상태로 복원한다.
4. environment는 `finally`에서 먼저 복원한다. 복원 완료/실패와 각 변수의 이전/복원 상태를 기록한 뒤 receipt를 쓴다. Receipt writer 실패는 primary outcome과 별도 `receipt_write_status=failed`로 operator stderr/log에 남기고 closeout을 `blocked`로 둔다.
5. inner runner는 실제 import된 `iris_clean_checkout_validation_common`의 `__file__`, working SHA-256와 exact subject Git blob을 run receipt에 기록한다. Launcher는 native exit 0 뒤 `verify_inner_receipt_identity` stage에서 inner receipt 존재/hash, subject, runner/common expected identity와 actual-import identity를 대조하며 이 검증이 끝나기 전에는 `succeeded`로 전환하지 않는다. 이 stage의 실패는 기존 primary가 있으면 secondary, 없으면 primary다.
6. `compare-results` validator는 JSON semantic equality 전에 raw bytes 및 SHA-256 equality를 fail-close한다. semantic-equal/byte-different, BOM, LF/CRLF와 trailing-newline 차이는 모두 실패 fixture다.
7. compare receipt는 Run A/B 각각의 orchestration receipt path/hash/claim ID, inner `full_run_receipt.json` path/hash, canonical result path/hash를 결속한다. Inner canonical hash와 orchestration subject/interpreter/environment/runner/common identity가 서로 일치하지 않으면 비교를 시작하지 않는다.
8. compare process stdout/stderr는 .NET raw base stream 또는 validator-owned binary sink로 분리 저장한다. PowerShell object pipeline이나 재인코딩 redirection을 사용하지 않는다.
9. compare writer의 path-independent canonical fingerprint는 attempt 물리 경로를 제외하고 logical artifact identity와 content hash만 포함한다.
10. Change 1B implementation과 fixture는 Codex Reviewer fresh review가 `APPROVE`가 되기 전에는 Change 2를 열지 않는다.
11. immutable predecessor `c1fa281e` runner에는 actual-import field가 없으므로 predecessor claim은 이 축에서 자동 승격하지 않고 `partial` ceiling을 유지한다. Predecessor 자체를 수정하지 않으며, 별도 exact external probe가 추가되더라도 predecessor runner receipt의 결손을 successor field로 소급 보완하지 않는다.

**Validation:**

- HEAD/dirty/interpreter/blob/pre-Python/native-nonzero 경로별 receipt 존재와 primary outcome 보존
- required/cleared environment 적용 중간 실패, restore 실패와 `absent|empty|value` round-trip fixture
- actual imported common-module path/blob/working hash binding fixture
- semantic-equal/byte-different, BOM/newline/trailing-newline compare negative fixture
- Run A/B orchestration → inner run receipt → canonical result chain mismatch negative fixture
- byte-preserving stdout/stderr와 BOM-free receipt writer focused attempt A/B determinism
- implementation read-only Codex Reviewer approval

---

### Change 2 — Phase 1: Validation and Producer Output Isolation

**Purpose:**

이미 존재하는 clean-checkout external execution 기반을 모든 current-required validation, full-gate가 호출하는 producer와 선택된 active producer 호출 경계로 확장한다.

**Files:**

- `Iris/validation/clean_checkout/contracts/output_policy.json` 또는 additive successor
- `Iris/validation/clean_checkout/iris_clean_checkout_validation_common.py`
- `Iris/validation/clean_checkout/run_iris_clean_checkout_validation.py`
- owner-reviewed `Iris/validation/clean_checkout/invoke_receipt_bound_full_gate.ps1` 또는 동등 launcher와 failure-path fixture
- `Iris/_docs/round3/round3_run_contract_tests.py`
- `Iris/build/description/v2/tests/clean_checkout_test_paths.py`
- Change 1에서 write leak가 확인된 test/producer leaf

**Implementation Notes:**

1. 기존 `ensure_external_root`, disjoint work/result root, disposable clone, status snapshot과 receipt를 재사용한다.
2. current/historical/diagnostic 실행은 caller-supplied external root 아래에서 서로 다른 subroot를 사용한다. 서로의 output을 읽거나 덮어쓰지 않는다.
3. test가 임시 파일을 필요로 하면 `clean_checkout_test_paths.external_test_path()` 또는 동등한 external TemporaryDirectory를 사용한다.
4. producer가 이미 explicit output argument를 갖는 경우 wrapper가 이를 강제한다. repository-relative default만 갖는 legacy producer는 먼저 execution adapter/overlay로 격리하고, CLI 변경은 별도 leaf batch로 미룰 수 있다.
5. validation-only route는 explicit authority writer/cutover 도구를 호출하지 않는다. authority mutation 도구는 기존 authorization/nonce/receipt contract 밖에서 generic producer로 실행하지 않는다.
6. source checkout은 가능하면 read-only로 실행하고, status만이 아니라 tracked/nonignored/ignored file identity snapshot을 비교한다.
7. 성공, expected failure, unexpected exception, subprocess nonzero의 모든 경로에서 repository write count와 disposable residue가 0이어야 한다.
8. 현재 dirty primary tree의 기존 변경을 자동 복원하거나 정리하지 않는다.
9. `c1fa281e` predecessor residual gate와 이 계획의 successor gate에 서로 다른 claim ID, subject, work/result root와 receipt를 사용한다. successor PASS는 predecessor 미검증 상태를 덮지 않는다.
10. full-gate launcher는 immutable receipt에서 interpreter path/hash를 읽고, `resolve_identity` stage에서 receipt interpreter SHA-256과 on-disk executable SHA-256이 다르면 Python 실행 전에 fail-close한다. 일치한 executable로 `-B -s <exact-checkout>/Iris/validation/clean_checkout/run_iris_clean_checkout_validation.py`를 직접 실행한다. `uv run python`, PATH-resolved `python` 또는 다른 checkout의 runner는 허용하지 않는다.
11. launcher는 exact checkout의 `output_policy.json`에서 required/cleared environment를 읽어 process environment에 적용하고, 적용 전 값을 `finally`에서 복원한다. 실제 set/cleared 결과와 policy Git blob/hash를 orchestration receipt에 기록한다.
12. orchestration receipt는 `sys.executable`/`--python`/receipt interpreter path/hash, exact subject commit/tree, runner path/Git blob/SHA-256, launcher가 기대한 `iris_clean_checkout_validation_common.py` path/Git blob/SHA-256와 inner runner가 실제 import한 common module의 `__file__`/Git blob/working SHA-256, environment receipt path/hash와 native exit code를 결속한다.
13. predecessor claim은 predecessor checkout의 launcher/runner/common blob만, successor claim은 successor checkout의 blob만 사용한다.
14. launcher는 raw parameter만 들어 있는 최소 receipt payload와 `native_exit_code=null`을 어떤 path/interpreter/argv 해석보다 먼저 초기화하고, HEAD/dirty/blob/interpreter/runner/policy/planned-argv 해석을 포함한 모든 작업을 하나의 `try/catch/finally` 안에서 수행한다. PowerShell parameter-binding 이전 실패는 all-path claim 밖이다.
15. native gate nonzero는 즉시 primary outcome으로 고정한다. `finally`는 `absent|empty|value`를 구분해 저장한 configured environment를 먼저 복원한 뒤 `launch_status`, `failure_reason`, exception type/message, nullable native exit, nullable planned argv, nullable actual argv, set/cleared environment, available identity field와 result receipt 존재/hash를 BOM 없는 orchestration receipt에 기록한다. Python이 시작되지 않은 경로는 actual argv와 native exit를 `null`로 둔다. 환경 복원 실패는 기존 primary가 있으면 secondary failure로만 기록하며, 그 다음에 원래 preflight/exception/native-nonzero 실패를 다시 전파한다.
16. receipt write failure는 `receipt_write_status=failed` 및 별도 writer exception으로 gate/preflight failure와 구분한다. receipt writer 실패 시 closeout은 `blocked`이며 gate 성공으로 해석하지 않고, launcher stderr/operator attempt log에 primary failure와 receipt-write failure를 모두 보존한다.
17. cross-run/cross-machine subject identity equality는 Git blob ID를 기준으로 한다. working-file SHA-256은 CRLF/LF 등 해당 checkout materialization 기록이며 Git blob과 byte equality를 요구하지 않는다.

**Validation:**

- output-root escape 및 repository-local output negative fixture
- pre-existing/non-empty output root rejection
- symlink/reparse/containment escape 검사
- subprocess failure injection 후 source mutation 0, work-root cleanup, result receipt 보존
- mismatched orchestrator/`--python`/receipt interpreter negative fixture와 receipt interpreter direct-execution positive fixture
- required/set 및 cleared ambient environment의 child visibility, outer restoration과 execution receipt field 검사
- predecessor/successor exact runner 및 imported common-module Git blob/hash binding 검사
- inner runner의 실제 imported common `__file__`/Git blob/working SHA-256와 launcher expected identity 일치 검사
- HEAD mismatch, dirty checkout, interpreter hash mismatch, Git blob lookup failure와 Python 실행 전 exception 각각에서 receipt 존재, `launch_status`, `failure_reason`, exception type/message와 `native_exit_code=null` 검사
- gate native nonzero에서 receipt의 exact exit, argv, environment, identity/result-existence field를 검사하고 receipt 작성 뒤 failure가 재전파되는지 확인
- receipt writer failure와 preflight/gate failure가 별도 상태·stderr/operator log에 보존되고 `complete`가 차단되는지 확인
- required/cleared environment 적용 중간 실패와 restore 실패에서 absent/empty/value 원상복원, 원래 native/preflight primary outcome 보존과 secondary failure 분리 확인
- Git blob은 cross-machine subject identity, working SHA-256은 checkout materialization identity로 비교되는지 CRLF/LF fixture로 확인
- predecessor claim: `c1fa281e` exact subject의 receipt-bound full-gate. 이 결과는 선행 residual-refactor 상태만 판정
- successor claim: 본 계획의 exact successor subject에 대한 full-gate Run A/B와 durable compare result identity
- primary working tree 관찰은 접근 가능한 dirty/ignored surface를 실행 전후 byte-for-byte 비교한다. 제외 경로가 있으면 path·사유·unlock 시도·관찰 ceiling을 receipt에 기록하며 clean checkout census에는 같은 제외를 자동 적용하지 않음

---

### Change 3 — Phase 2: Existing Path Infrastructure Adoption

**Purpose:**

새 path framework를 만들지 않고 `tools/common/paths.py`를 leaf batch로 채택해 root-depth 가정과 `sys.path` bootstrap을 줄인다.

**Files:**

- `Iris/build/description/v2/tools/common/paths.py`
- Change 1에서 선택한 low-fan-in leaf script batch
- 각 batch의 caller/test/import matrix

**Implementation Notes:**

1. 첫 batch는 current authority writer가 아니고, low fan-in이며, golden CLI/output을 가진 leaf로 제한한다.
2. low fan-in 판정은 script caller만 보지 않고 sibling common/path provider·consumer edge를 포함한다. 기존 support 계층과 `tools/common/paths.py`의 owner 관계가 미결이면 source-changing batch를 시작하지 않는다.
3. `paths.py`는 stdlib-only leaf를 유지하고 business logic, serialization, subprocess 또는 policy를 넣지 않는다.
4. 필요한 anchor는 repository fact와 기존 계산 결과가 동등한 경우에만 추가한다. `V2_ROOT`, `BUILD_ROOT`, `DATA_DIR`, `OUTPUT_DIR`, `STAGING_DIR`의 의미를 바꾸지 않는다.
5. `registry_runtime_record_paths.py`처럼 owner-bound sibling path helper를 `tools/common/paths.py`로 자동 흡수하지 않는다.
6. script-local `parents[N]`와 `sys.path.insert`를 제거하기 전에 direct script, `python -m`, repository package import, v2-root package import와 필요한 bare import를 모두 characterization한다.
7. 파일 위치는 이 단계에서 이동하지 않는다. 먼저 import/bootstrap 의존을 제거한 뒤 topology change의 적격성을 판정한다.
8. current core 또는 allowed tooling이 common path dependency를 새로 소비하면 preimport closure와 slot/owner 규칙을 먼저 확인한다.
9. 한 batch 실패는 해당 leaf만 기존 bootstrap으로 되돌릴 수 있어야 하며 다음 batch를 시작하지 않는다.

**Validation:**

- resolved-path manifest before/after equality
- direct-script `--help`, invalid argument, missing input, success exit-code equality
- package/`-m`/bare import matrix
- Windows long path, 다른 checkout depth와 census에서 관찰된 `parents[1]`~`parents[6]` 각 depth fixture. 희소 `parents[4]` anchor는 `_dvf_3_3_vnext_common.py`를 characterization 대상으로 명시하되 shared-owner gate 없이 migration하지 않음
- source/output containment 재검증
- current closure preimport 검사

---

### Change 4 — Phase 3: Contract-Family Deterministic I/O and Hash Helpers

**Purpose:**

JSON·JSONL·text·hash helper 중 **동일 계약**을 가진 중복만 공통화하고 byte identity와 sealed hash를 보존한다.

**Files:**

- `Iris/build/description/v2/tools/build/compose_layer3_io.py` (기존 owner 계약 유지)
- owner/closure 판정을 통과한 경우 `Iris/build/description/v2/tools/common/`의 contract-family helper
- 선택된 producer leaf와 golden fixture test
- serialization contract matrix

**Implementation Notes:**

1. Change 1의 sibling common/path provider·consumer·fan-in·owner·contract matrix를 읽고 기존 구현과 신규 `tools/common/` 후보의 overlap을 먼저 판정한다.
2. 각 contract family는 기존 sibling owner 유지, `tools/common/` owner 승격 또는 local owner 유지 중 하나의 explicit decision을 가져야 한다. owner 미확정 또는 중복 contract가 남으면 이 Change의 source mutation을 시작하지 않는다.
3. 전역 `load_json`/`write_json` 하나로 147/112개 정의를 일괄 교체하지 않는다.
4. contract ID는 encoding, BOM, duplicate key, `ensure_ascii`, key order, indentation, separators, newline, trailing newline, atomicity, retry, missing-file/error type, hash chunk size를 포함한다.
5. 서로 다른 contract ID는 서로 다른 helper 또는 기존 local owner 구현을 유지한다.
6. `compose_layer3_io`의 현재 JSONL platform-newline, unsorted key, direct-write, 8192-byte hash 계약은 승인 없이 변경하지 않는다.
7. 신규 common module stem이 current route dependency가 되면 별도 reviewed closure 결정을 요구한다. 승인이 없으면 non-current leaf pilot만 수행하거나 local owner helper를 유지한다.
8. newline 작업은 현행 producer별 byte contract의 관찰·고정일 뿐 repository-wide newline/BOM 정책 변경이 아니다.
9. timestamp는 claim identity에 포함되는 값과 informational metadata를 분리한다. deterministic payload에 wall-clock 값을 새로 넣지 않는다.
10. 기존 sealed/historical artifact는 새 writer로 재직렬화하지 않는다.
11. migration 단위는 한 contract family의 leaf batch이며, before/after golden이 다르면 일반 리팩터링으로 통과시키지 않는다.

**Validation:**

- golden bytes와 raw SHA-256 equality
- sibling support와 `tools/common/` contract overlap 0 또는 owner-bound intentional delegation
- LF/CRLF/BOM fixture
- duplicate-key allow/reject fixture
- sorted/unsorted key fixture
- final-newline 및 empty-file fixture
- atomic replace/retry/failure residue fixture
- deterministic Run A/B
- current source/rendered/runtime/package identity guard가 적용되는 batch의 기존 전용 검사

---

### Change 5 — Phase 4: CLI Bootstrap, Subprocess, and Receipt Consolidation

**Purpose:**

argparse 및 subprocess 전체 census를 compatibility inventory로 유지하되, owner·caller·role이 결속된 migration batch에서만 반복되는 bootstrap, child-process capture와 receipt 기록을 제한적으로 공통화한다.

**Files:**

- 선택된 CLI entrypoint/wrapper
- owner/closure 승인을 받은 common CLI/subprocess/receipt leaf
- clean-checkout runner와 result schema test
- CLI/import/caller topology manifest

**Implementation Notes:**

1. 기존 script path와 argument name, required/optional/default, stdout/stderr, exit code를 public compatibility surface로 취급한다.
2. 적용 분모는 Phase 0의 전체 subprocess 탐지 집합이 아니라 owner가 `receipt_migration_batch_registry.json`에서 확정한 `receipt_migration_batch_<id>` row다. Change 5는 registry path/hash, owner와 source denominator hash가 일치할 때만 시작한다. 첫 후보는 current-route 호출 중 output isolation과 owner/closure가 이미 확인된 low-fan-in boundary로 제한한다.
3. subprocess는 interpreter isolation, environment clearing, failure boundary, historical replay 또는 authority separation을 담당하면 유지한다.
4. 같은 interpreter의 순수 leaf 호출이고 환경/실패/authority 경계가 없다는 근거가 있는 호출만 함수 호출 전환 후보가 된다.
5. child process는 exact interpreter, cwd, argv, cleared/set environment, input hash, stdout/stderr hash, exit code와 output manifest를 receipt에 기록한다.
6. receipt writer는 external result root만 사용하고 claim-bearing output을 overwrite하지 않는다.
7. consumed nonce, closed attempt 또는 sealed receipt를 공통 helper adoption 명분으로 재실행하거나 다시 쓰지 않는다.
8. 각 batch는 기존 wrapper를 facade로 유지하고 내부 실행만 바꿀 수 있다.

**Validation:**

- `--help`, invalid args, missing file, controlled failure, success의 stdout/stderr/exit matrix
- environment clearing과 exact interpreter receipt 검사
- subprocess timeout/nonzero/partial-output fixture
- receipt hash와 output manifest binding
- caller inventory에서 dangling script path 0
- direct script와 `python -m` 동작 비교
- selected receipt migration batch registry path/hash와 ordered row denominator 전 행의 before/after coverage, 미선택 subprocess non-claim

---

### Change 6 — Phase 5: Tool Topology and Artifact Lifetime Classification

**Purpose:**

flat script inventory와 4.27 GiB staging을 역할과 수명주기로 분류해 후속 이동/retention 결정을 안전하게 만든다.

**Files:**

- tool role manifest
- output ownership manifest
- retention classification manifest
- owner decision packet
- 승인된 경우에만 선택적 leaf wrapper/문서 command update

**Implementation Notes:**

1. Change 1에서 고정한 `recursive`와 `root-direct` denominator ID별 모든 build Python row에 role, owner, caller, current/historical/diagnostic relationship과 disposition 근거를 기록한다. 숫자 484 하나를 전체 coverage 근거로 사용하지 않는다.
2. Role axis는 `classified_role`과 `unknown_role`만 배타적으로 사용한다. `classified_role`은 active/completed/diagnostic/historical/legacy-required/test-only 등 기존 role vocabulary를 세부값으로 보존한다.
3. Owner axis는 `owner_bound`와 `owner_unknown`만 배타적으로 사용하고 artifact owner와 unresolved-row disposition decision owner를 구분한다.
4. Caller axis는 `caller_observed`와 `no_caller_observed`만 배타적으로 사용한다. caller 미관찰을 role/owner unknown으로 추론하지 않는다.
5. 세 axis는 별도 denominator와 cross-tab으로 보고하며 서로 더하지 않는다. sealed `unknown_role=55`를 착수 seed로 사용하고 owner threshold가 이를 유지·축소·확대하는 근거를 기록한다.
6. owner 또는 role 미확정 row는 근거, unresolved question, escalation/decision owner와 `move/delete/consolidate forbidden` disposition을 반드시 가진다. unknown 허용 임계값은 owner decision이며 무제한 unknown을 `complete`로 자동 허용하지 않는다.
7. 산출물을 다음 최소 family로 분류한다.
   - disposable intermediate
   - reproducibility fixture/input
   - sealed/closeout evidence
   - current authority와 연결된 artifact
   - ignored read-only package projection
   - backup/sandbox/probe result
8. 기존 tracked staging 3,405개와 전체 5,212개는 inventory 단계에서 그대로 보존한다.
9. artifact store, LFS, repository retention 또는 deletion은 owner decision packet의 별도 선택으로 남긴다. 이 계획이 기본값을 정하지 않는다.
10. `pipeline/`, `validators/`, `oneshots/` 같은 물리적 디렉터리 이동은 path/bootstrap migration, full caller census, old-path wrapper, receipt identity 영향과 historical command 보존이 모두 승인된 leaf에만 수행한다.
11. physical move가 한 건도 승인되지 않아도 complete inventory와 decision packet은 이 Change의 유효한 closeout이다.
12. tracked `Iris/_docs/round3/__pycache__/round3_run_contract_tests.cpython-314.pyc`, `v2/.tmp_tests`와 `__pycache__`는 tracked/ignored/owner 상태를 각각 확인한다. cleanup은 별도 material change로 수행하고 staging 안의 sealed evidence와 함께 지우지 않는다.

**Validation:**

- Role: `total = classified_role + unknown_role`
- Owner: `total = owner_bound + owner_unknown`
- Caller: `total = caller_observed + no_caller_observed`
- 세 axis 각각의 total이 동일 subject denominator와 일치하고 cross-axis 중복 합산이 없는지 검사
- static-caller-observed denominator와 provider/consumer edge coverage
- `unknown_role` seed 55 대비 현재 값, owner-approved threshold/근거와 미확정 row의 escalation owner·금지 disposition 완전성
- caller/callee dangling reference 검사
- current authority artifact와 disposable output의 교집합 0
- retained/sealed artifact coverage
- old CLI path compatibility test(물리적 이동이 승인된 경우)
- clean-checkout replay 및 package/source identity

---

### Change 7 — Phase 6: Residual Runtime Responsibility Separation

**Purpose:**

빌드·검증 계층이 안정된 뒤, 현재 코드에 실제로 남은 Wiki renderer 공존과 Browser build boundary를 public behavior 변경 없이 국소 정리한다.

**Files:**

- `Iris/media/lua/client/Iris/UI/Wiki/IrisWikiSections.lua`
- 승인된 internal current/legacy Wiki section module
- `Iris/media/lua/client/Iris/UI/Browser/IrisBrowserData.lua`
- 필요성이 입증된 경우 internal candidate builder 또는 build-state module
- `Iris/media/lua/client/Iris/Util/IrisProtectedCall.lua`
- runtime characterization/acceptance harness와 supported API manifest
- `Iris/test/run_residual_refactor_acceptance.ps1`, `Iris/test/validate_residual_refactor_surfaces.ps1` 및 `tools/check_lua_syntax.ps1`
- `Iris/tools/package_iris.ps1`와 pre/post package identity manifest

**Implementation Notes:**

1. `IrisWikiSections.lua`는 public facade와 public wrapper 정의를 유지한다. legacy/current 함수는 현재 파일에서 교차 배치되어 있으므로 연속 블록 이동이 아니라 함수 단위 internal delegation만 허용한다.
2. `renderBasicInfoSection`, `renderTagsSection`, `renderFoodSection`, `renderWeaponSection`, `renderConnectionSection`, `renderMiscSection`, `getAllSections`, `renderReasonSection`, `renderFieldsSection`의 기존 return shape를 legacy supported wrapper로 유지한다.
3. `renderCoreInfoSection`, `renderLayer3Section`, `renderRecipeInfoSection`, `renderMetaInfoSection`, `renderUseCaseSection`의 순서, label, newline과 nil 조건을 유지한다.
4. Browser는 이미 분리된 `CategoryIndex`, `Filters`, `ItemIndex`, `ClassificationIndex`, `Query`, `VariantIndex`를 재작성하지 않는다.
5. `IrisBrowserData`에서 추가로 분리할 수 있는 것은 candidate assembly와 state transition뿐이다. `_cache`, `_built`, `build()`, `ensureReady()`, `getBuildState()`, `isReady()`, `resetForReload()`, retry/degraded 동작은 facade contract를 유지한다.
6. direct `pcall(buildCandidateCache)`의 success/failure tuple, release logging, debug logging, warning duplication, fallback과 retry state를 `ProtectedCall.data()`와 먼저 비교한다. 동등하지 않으면 raw call을 유지하거나 별도 policy 결정을 받는다.
7. ProtectedCall policy를 변경하려면 `engine/ui/data/compat`별 return, fallback, release log, debug log 표를 먼저 고정한다.
8. `StaticData.getLegacyIrisData()`와 `IrisBrowserVariantIndex.getGroupVariants()`는 이미 adapter 경계를 충족하므로 기본 disposition은 no-change verification이다.
9. `IrisData.lua`, generated classification/index/chunk와 package projection은 직접 수정하지 않는다.
10. 런타임은 계속 오프라인에서 봉인된 facts/description을 표시할 뿐 source나 quality를 재판정하지 않는다.
11. mutation 전에 exact predecessor commit/tree에서 runtime harness `Baseline`과 surface `Baseline`을 실행하고 output, binding, evidence manifest와 모든 baseline file hash를 하나의 external immutable baseline bundle manifest에 결속한다.
12. successor `Acceptance`/`Closeout`은 predecessor baseline surface files를 동일 external evidence bundle의 hash-locked input으로 소비한다. runner가 같은 `EvidenceRoot`를 요구하므로 baseline capture 뒤 bundle을 successor checkout 밖에 보존하고, closeout은 그 root를 그대로 지정해 `final_*` successor file만 additive write한다.
13. mutation 뒤 `-Mode Baseline`을 다시 실행해 predecessor file을 덮어쓰거나 대체하지 않는다. 재-baseline이 필요한 contract change는 새 plan/owner decision과 새 bundle ID를 요구한다.
14. predecessor baseline은 predecessor checkout 안의 exact absolute `run_residual_refactor_acceptance.ps1`/`validate_residual_refactor_surfaces.ps1`와 그 driver가 선택한 Lua harness만 사용한다. successor acceptance/closeout/syntax는 successor checkout 안의 exact absolute driver/harness만 사용한다.
15. 각 runtime/Lua invocation은 driver와 harness의 repository-relative logical path, Git blob ID, working-file SHA-256, subject commit/tree와 actual argv를 즉시 manifest에 결속한다. Git blob은 cross-run/cross-machine source identity이고 working SHA-256은 checkout materialization identity다.
16. 수동 UI baseline용 package와 successor package는 각각 predecessor/successor checkout의 exact absolute `package_iris.ps1`로 별도 output root에 생성한다. 두 package producer identity와 source subject를 섞거나 하나의 package를 양쪽 evidence로 재사용하지 않는다.

**Validation:**

- supported API/module path/signature manifest equality
- predecessor runtime/surface baseline subject commit/tree와 output/binding/evidence hash 완전성
- predecessor/successor runtime·surface·syntax driver와 selected Lua harness의 exact checkout path/Git blob/working SHA-256/actual argv binding
- Wiki renderer baseline/acceptance byte or normalized-text equality
- Browser category/search/fold/group/location result equality
- build success, retryable failure, degraded ready, `resetForReload()` 및 reload state transition equality
- protected-call success/error/log matrix
- legacy group present/missing/module-missing adapter fixture
- Lua syntax와 standalone harness
- pre/post disposable package의 분리된 output root, exact package driver Git blob/working SHA-256와 source subject identity
- candidate cleanup failure injection에서 `candidate cleanup failed` throw와 closeout failure state 확인
- successful Closeout 뒤 disposable candidate/package root residue 0 및 기존 ignored package projection 불변
- Project Zomboid Browser/Wiki/Tooltip/logging 5-case manual validation

---

### Change 8 — Phase 7: Integrated Closeout and Re-entry Guards

**Purpose:**

각 change의 claim을 exact evidence에 결속하고, helper migration·retention·runtime refactor가 authority 또는 release claim으로 과대 해석되지 않게 닫는다.

**Files:**

- closeout validation matrix
- exact subject/run receipt binding
- owner-reviewed compare launcher, validator, receipt schema/writer와 focused determinism fixture
- tool/helper residual inventory
- output mutation and residue report
- supported API/package identity report
- manual runtime validation report
- claim-boundary report
- evidence가 뒷받침하는 경우에만 top-level docs의 additive update

**Implementation Notes:**

1. predecessor `c1fa281e` full-gate를 별도 `claim_id`로 판정하고 결과가 없거나 실패하면 그 claim row의 기존 `closeout_state`만 `partial`로 둔다.
2. 이 계획의 exact successor subject에서 receipt-bound full-gate Run A/B를 수행하고 canonical result, dependency inventory, output hashes와 receipt를 비교한다.
3. deterministic compare launcher는 receipt interpreter로 exact successor checkout의 compare validator를 실행하고 stdout/stderr를 서로 다른 byte-preserving sink에 기록한다. Windows PowerShell 5.1의 `1>`/`2>`가 native process output을 재인코딩할 수 있으므로 이를 byte contract로 사용하지 않는다. owner-reviewed .NET process launcher 또는 validator-owned external output writer처럼 encoding/BOM을 명시적으로 통제하는 구현을 사용하고 `2>&1` object capture는 금지한다.
4. compare receipt는 생성 즉시 각 Run의 canonical result path/hash뿐 아니라 orchestration receipt path/hash/claim ID와 inner `full_run_receipt.json` path/hash를 결속한다. Canonical hash가 inner receipt와 같고 subject, interpreter, environment, runner/common expected 및 actual-import identity가 orchestration receipt와 일치하는지 preflight에서 확인한 뒤 `stdout_sha256`, `stderr_sha256`, native exit code, validator 및 imported common-module path/Git blob/SHA-256, interpreter path/SHA-256, environment policy/receipt identity와 successor commit/tree를 기록한다.
5. receipt JSON은 `System.IO.File.WriteAllText(..., UTF8Encoding(false))` 또는 검증된 동등 writer로 BOM 없는 canonical bytes를 기록한다. 계획 본문은 schema ID를 확정하지 않으며 schema/writer adoption은 Change 8의 owner-reviewed 산출물이다.
6. compare writer를 처음 채택하거나 writer blob/schema/canonicalization contract가 바뀔 때 focused implementation test에서 동일 Run A/B input과 execution identity로 writer를 분리된 disposable attempt root에서 두 번 실행한다. attempt-specific physical output path는 canonical receipt fingerprint에서 제외하거나 logical artifact name으로 정규화하고 stdout/stderr/receipt canonical hash가 각각 같아야 한다. 이 검증을 통과한 exact writer Git blob/schema에 한해 일반 successor closeout은 compare receipt를 한 번 생성한다.
7. predecessor와 successor는 closeout matrix의 별도 `claim_id` row이며 각 row는 기존 `closeout_state = complete|partial|implemented_only|blocked`, validation ceiling과 non-claims를 사용한다. successor PASS가 predecessor row를 대체하거나 소급 승격하지 않는다.
8. 각 migrated leaf에 before/after contract와 rollback unit을 연결한다.
9. 남은 `sys.path`, `parents[N]`, local helper와 flat script는 role/owner/contract별 residual로 기록한다. 단순 잔존 count를 실패로 만들지 않는다.
10. predecessor FAIL, historical evidence와 diagnostic raw nonzero를 삭제하거나 PASS로 덮어쓰지 않는다.
11. external result를 durable evidence로 채택할 경우 exact subject commit/tree, interpreter/environment receipt와 result hash를 결속한다.
12. source checkout mutation, output-root escape, unapproved authority write, sealed artifact rewrite가 하나라도 있으면 `complete`로 닫지 않는다.
13. runtime mutation이 적용된 경우 exact predecessor baseline bundle과 pre/post 수동 UI evidence가 없으면 해당 successor claim row는 `partial`이다.
14. closeout은 validation ceiling과 non-claims를 포함한다.

**Validation:**

- automated matrix 전 항목의 exact exit code 확인
- predecessor `c1fa281e` claim과 successor Run A/B/compare claim의 독립 판정
- compare stdout/stderr byte-preserving 분리, BOM 없음, 즉시 Run A/B orchestration→inner receipt→canonical result 및 validator·interpreter·environment hash binding
- compare writer 채택·변경 focused test의 동일-input attempt A/B stdout/stderr/canonical receipt hash identity와 일반 closeout의 exact verified writer blob/schema 사용
- compare receipt schema/writer owner review와 current-route durable adoption 비자동성
- source tracked/nonignored/ignored state unchanged
- external work-root cleanup과 result-root receipt completeness
- denominator ID별 tool role/retention accounting과 unknown ceiling
- predecessor baseline bundle 및 Lua API/runtime/package pre/post manual evidence(해당 runtime mutation 시)
- independent read-only diff review

---

## 7. Validation Plan

### Validation Preconditions

- 검증 대상은 명시된 exact commit/tree여야 한다.
- full-gate 대상 checkout은 tracked 및 nonignored untracked state가 clean해야 한다.
- primary dirty working tree에서 full discovery producer를 직접 실행하지 않는다.
- `uv`는 focused test/current-route command에만 사용할 수 있다. terminal full-gate와 compare validator는 immutable receipt의 interpreter executable을 직접 사용한다.
- orchestrator `sys.executable`, `--python`과 immutable environment receipt의 interpreter path/hash가 모두 일치해야 한다.
- predecessor/successor 각각 exact checkout의 absolute runner/validator/common path를 사용하고 subject Git blob과 working-file SHA-256을 execution receipt에 기록한다.
- full-gate 전에 exact checkout `output_policy.json`의 required environment를 set하고 cleared ambient environment를 unset하며, 실제 값과 clear 상태를 receipt에 기록한다. operator environment는 `finally`에서 원래 상태로 복원한다.
- work root와 result root는 repository와 서로 disjoint한 빈 external directory여야 한다.
- current, historical, diagnostic route의 output root를 공유하지 않는다.
- predecessor `c1fa281e` result, successor Run A/B result, durable compare result와 runtime baseline bundle은 서로 다른 external path와 claim ID를 사용한다.
- primary-tree 전후 관찰 전에 접근 불가 ignored path를 probe한다. 잠금 해제할 수 없으면 자동 삭제하지 않고 path·오류·제외 사유와 관찰 ceiling을 receipt에 기록한다. disposable clean checkout census에는 그 제외를 자동 전파하지 않는다.
- runtime baseline bundle은 pre-mutation exact subject에서 생성한다. baseline files와 bundle manifest는 hash-locked immutable input으로 보존하고, 같은 evidence root에는 Closeout의 `final_*` successor file만 additive write한다. successor checkout 또는 repository 내부로 복사해 덮어쓰지 않는다.

### Automated Validation

다음은 계획된 명령 형태다. `<...>` 값은 실행 시 exact subject와 external root로 고정하고 receipt에 기록한다. 명령은 실제 exit code `0`을 확인한 경우에만 PASS로 기록한다.

#### A. Focused clean-checkout contract tests

```powershell
uv run python -B -s -m pytest -q -p no:cacheprovider `
  Iris\validation\clean_checkout\tests\test_iris_clean_checkout_validation.py
```

#### B. Current route contract

이 명령은 disposable clean checkout과 external test-output root 안에서 실행한다.

```powershell
uv run python -B -s Iris\_docs\round3\round3_run_contract_tests.py `
  --class current `
  --enforce-current-build-closure `
  --out <external-current-result.json>
```

#### C-0. Receipt-bound full-gate operator contract

아래 블록은 `invoke_receipt_bound_full_gate.ps1`의 **normative behavior specification**이며 operator가 그대로 복사해 실행하는 command가 아니다. reviewed launcher implementation은 C-1에 한 번, C-2 Run A/B에 각각 한 번 호출되며 `<exact-repository>` 안의 Python runner를 사용한다.

이 의사코드에서 PowerShell parameter-binding은 함수 본문 진입 전이므로 all-path receipt ceiling 밖이다. 본문 진입 뒤에는 raw parameter만으로 최소 receipt state를 먼저 만들고 path/interpreter/policy/argv 해석을 모두 `try` 안에서 수행한다. 아래 `$plannedArgv`의 실제 구성도 `try`의 `resolve_identity` 이후에만 일어나며, native nonzero는 즉시 primary outcome으로 저장한다. Environment snapshot은 각 변수의 `absent|empty|value`를 구분한다.

```powershell
$gateExit = $null
$primaryFailure = $null
$receiptWriteFailure = $null
$launchStatus = 'preflight_pending'
$launchStage = 'initialize'
$failureReason = $null
$exceptionType = $null
$exceptionMessage = $null
$receiptWriteStatus = 'pending'
$plannedArgv = $null
$actualArgv = $null
$environmentConfigured = $false
$environmentRestored = $false
$previousEnvironment = @{}
$setEnvironment = [ordered]@{}
$clearedEnvironment = @()
$identity = [ordered]@{}
$resultReceiptExists = $false
$resultReceiptHash = $null
$secondaryFailures = @()

try {
  $launchStage = 'resolve_head'
  $rawHead = git -C $repositoryRoot rev-parse HEAD
  if ($LASTEXITCODE -ne 0) { throw 'failed to resolve repository HEAD' }
  $head = $rawHead.Trim()
  if ($head -ne $targetCommit) { throw 'HEAD does not equal exact target commit' }

  $launchStage = 'check_clean'
  $dirtyRows = @(git -C $repositoryRoot status --porcelain=v1 --untracked-files=all)
  if ($LASTEXITCODE -ne 0) { throw 'working-tree clean check failed' }
  if ($dirtyRows.Count -ne 0) { throw 'full-gate source checkout is not clean' }

  $launchStage = 'resolve_identity'
  $rawRunnerBlob = git -C $repositoryRoot rev-parse "${targetCommit}:$runnerRelative"
  if ($LASTEXITCODE -ne 0) { throw 'failed to resolve runner Git blob' }
  $runnerBlob = $rawRunnerBlob.Trim()
  $rawCommonBlob = git -C $repositoryRoot rev-parse "${targetCommit}:$commonRelative"
  if ($LASTEXITCODE -ne 0) { throw 'failed to resolve common-module Git blob' }
  $commonBlob = $rawCommonBlob.Trim()
  $rawPolicyBlob = git -C $repositoryRoot rev-parse "${targetCommit}:$policyRelative"
  if ($LASTEXITCODE -ne 0) { throw 'failed to resolve output-policy Git blob' }
  $policyBlob = $rawPolicyBlob.Trim()
  # Resolve working-file materialization hashes and fail-close here if the
  # receipt interpreter SHA-256 differs from the on-disk executable SHA-256.
  # Resolve the interpreter/runner/common/policy paths here, then construct
  # plannedArgv. No fallible identity or argv work occurs before the try block.
  $plannedArgv = @(
    $pythonExe, '-B', '-s', $runner, 'full-gate',
    '--repo', $repositoryRoot, '--commit', $targetCommit,
    '--python', $pythonExe, '--environment-receipt', $environmentReceipt,
    '--work-root', $workRoot, '--result-root', $resultRoot
  )

  $launchStage = 'configure_environment'
  # Save every required/cleared process variable, then apply exact output policy.
  $environmentConfigured = $true

  $launchStage = 'invoke_gate'
  & $pythonExe -B -s $runner full-gate `
    --repo $repositoryRoot `
    --commit $targetCommit `
    --python $pythonExe `
    --environment-receipt $environmentReceipt `
    --work-root $workRoot `
    --result-root $resultRoot
  $gateExit = $LASTEXITCODE
  $actualArgv = @($plannedArgv)
  $launchStatus = if ($gateExit -eq 0) { 'gate_exit_zero_pending_inner_receipt' } else { 'gate_failed' }
  if ($gateExit -eq 0) {
    $launchStage = 'verify_inner_receipt_identity'
    # Require inner full_run_receipt presence/hash, subject, runner identity and
    # actual imported common __file__/Git blob/working SHA-256 to match the
    # launcher expectation. Only then set launchStatus='succeeded'.
    Verify-InnerReceiptIdentity
    $launchStatus = 'succeeded'
  }
  else {
    $failureReason = 'native_gate_exit_nonzero'
    $primaryFailure = [ordered]@{
      kind = 'native_gate_exit_nonzero'
      native_exit_code = $gateExit
    }
  }
}
catch {
  if ($null -eq $primaryFailure) {
    $primaryFailure = $_
    $launchStatus = if ($launchStage -eq 'invoke_gate') { 'exception' } else { 'preflight_failed' }
    $failureReason = $launchStage
    $exceptionType = $_.Exception.GetType().FullName
    $exceptionMessage = $_.Exception.Message
  }
  else {
    $secondaryFailures += [ordered]@{
      stage = $launchStage
      exception_type = $_.Exception.GetType().FullName
      exception_message = $_.Exception.Message
    }
  }
}
finally {
  try {
    # Restore every saved process environment value before writing the receipt.
    $environmentRestored = $true
  }
  catch {
    $environmentRestored = $false
    $secondaryFailures += [ordered]@{
      stage = 'restore_environment'
      exception_type = $_.Exception.GetType().FullName
      exception_message = $_.Exception.Message
    }
    if ($null -eq $primaryFailure) {
      $primaryFailure = $_
      $launchStatus = 'environment_restore_failed'
      $failureReason = 'restore_environment'
      $exceptionType = $_.Exception.GetType().FullName
      $exceptionMessage = $_.Exception.Message
    }
  }

  try {
    # Resolve result-receipt existence/hash without treating absence on a failed
    # preflight or gate as a second primary failure.
    # Atomically write BOM-free receipt with launch_status, launch_stage,
    # failure_reason, exception type/message, nullable native_exit_code,
    # planned argv, nullable actual argv, set/cleared environment, available identities,
    # environment_restored, secondary failures, receipt_write_status='succeeded',
    # and result-receipt existence/hash.
    $receiptWriteStatus = 'succeeded'
    Write-OrchestrationReceipt
  }
  catch {
    $receiptWriteFailure = $_
    $receiptWriteStatus = 'failed'
  }
}

if ($null -ne $receiptWriteFailure) {
  # Preserve receipt_write_status plus primary, restore, and receipt-writer
  # failures separately in the external stderr/operator attempt log.
  throw 'orchestration receipt write failed; closeout blocked'
}
if ($null -ne $primaryFailure) {
  if ($primaryFailure.kind -eq 'native_gate_exit_nonzero') { exit $gateExit }
  throw $primaryFailure
}
if ($gateExit -ne 0) { throw "clean-checkout full-gate failed: $gateExit" }
```

receipt의 cross-run/cross-machine subject identity 기준은 `runnerBlob/commonBlob/policyBlob`이다. `runnerHash/commonHash/policyHash`는 CRLF/LF를 포함한 현재 checkout materialization 기록이므로 Git blob과 byte equality를 요구하지 않는다. Receipt schema ID와 durable adoption은 launcher implementation review에서 확정한다.

실제 operator command는 reviewed launcher를 호출하며 launcher 자체의 path/Git blob 또는 owner-bound external hash도 orchestration receipt에 기록한다.

```powershell
powershell -NoProfile -ExecutionPolicy Bypass `
  -File <owner-reviewed-receipt-bound-launcher> `
  -RepositoryRoot <exact-repository> `
  -Commit <exact-commit> `
  -EnvironmentReceipt <immutable-environment-receipt> `
  -WorkRoot <external-empty-work-root> `
  -ResultRoot <external-empty-result-root> `
  -OrchestrationReceipt <external-orchestration-receipt>
```

#### C-1. Predecessor residual claim gate

`claim_id=residual_predecessor_c1fa281e`로 C-0을 실행한다.

- repository/runner/common: exact `c1fa281e0f9b25bb7e26c3d35755b08bb0ac6000` checkout
- work/result root: predecessor 전용 external empty roots
- effect: 선행 residual-refactor의 미결 full-gate만 판정

#### C-2. Successor plan claim Run A/B and deterministic comparison

`claim_id=offline_tool_successor_<commit>`로 exact successor checkout의 C-0을 서로 다른 empty work/result root에서 Run A/B 두 번 실행한다. C-1 결과를 대체하지 않는다.

compare는 owner-reviewed `invoke_deterministic_compare.ps1`가 C-0의 environment preparation/restoration을 재사용하고 receipt interpreter와 exact successor validator/common module을 사용해 두 attempt를 생성한다. 아래 블록은 launcher 내부의 **논리적 argv와 분리 sink 사양**이며, Windows PowerShell 5.1의 `1>`/`2>` operator를 구현 지시로 사용하는 예시가 아니다.

```powershell
$compareArgv = @(
  '-B', '-s',
  '<exact-successor-repository>\Iris\validation\clean_checkout\validate_iris_clean_checkout_validation.py',
  'compare-results',
  '--run-a', '<external-successor-result-a>\canonical_full_result.json',
  '--run-b', '<external-successor-result-b>\canonical_full_result.json'
)
$compareExit = Invoke-ReviewedBytePreservingProcess `
  -FilePath <receipt-matched-python> `
  -ArgumentList $compareArgv `
  -StdoutPath <external-compare-attempt>\compare-results.stdout.bin `
  -StderrPath <external-compare-attempt>\compare-results.stderr.bin
```

`Invoke-ReviewedBytePreservingProcess`는 계획이 새 공용 helper 이름이나 구현을 확정한다는 뜻이 아니라 필요한 process-capture contract를 표시하는 placeholder다. 실제 구현은 owner-reviewed launcher 내부에 둘 수 있고 validator가 external output file을 직접 쓰게 할 수도 있다. 이 항목은 별도 entry gate나 실행 중단 조건을 추가하지 않으며, 이미 요구된 분리/BOM/input-binding/focused determinism/closeout 조건으로 판정한다.

launcher는 stdout/stderr를 object pipeline으로 다시 직렬화하지 않는다. Run A/B, byte-preserving stdout/stderr, validator, interpreter, environment identity와 native exit code를 즉시 hash-bind하고 BOM 없는 receipt를 쓴다. compare writer 채택·변경 focused test에서는 동일 input으로 attempt A/B를 생성해 canonical receipt fingerprint와 stdout/stderr hash가 같아야 한다. 일반 closeout은 그 test에 결속된 exact writer blob/schema로 receipt 한 개를 생성한다. 계획 본문은 compare receipt schema ID를 확정하지 않는다.

#### D. Pilot-specific Python tests

- path-resolution before/after manifest test
- CLI/import matrix test
- serialization byte-contract parameterized fixtures
- output containment and failure-injection test
- subprocess/receipt binding test
- receipt interpreter/direct-runner/environment restore 및 predecessor/successor runner identity test
- HEAD mismatch, dirty checkout, interpreter/hash/blob lookup, pre-Python exception, native gate nonzero 각각의 all-path orchestration receipt와 receipt-write-failure 분리 test
- compare byte-preserving stdout/stderr separation, BOM-free receipt, immediate input hash binding과 writer Run A/B determinism test
- predecessor/successor runtime·Lua·package driver/harness exact checkout path, Git blob, materialization hash와 actual argv binding test
- tool role/retention manifest schema and denominator test

각 pilot test는 `uv run python -B -s -m pytest -q -p no:cacheprovider <exact-test-path>` 형태로 개별 실행한 뒤 current/full gate에 편입한다.

#### E-1. Pre-mutation Lua/runtime baseline

Change 7 source mutation 전에 exact predecessor checkout에서 실행한다.

```powershell
$preRepository = [System.IO.Path]::GetFullPath('<exact-pre-change-repository>')
$preRuntimeDriver = Join-Path $preRepository 'Iris\test\run_residual_refactor_acceptance.ps1'
$preSurfaceDriver = Join-Path $preRepository 'Iris\test\validate_residual_refactor_surfaces.ps1'

powershell -NoProfile -ExecutionPolicy Bypass -File $preRuntimeDriver `
  -Mode Baseline `
  -RepositoryRoot $preRepository `
  -OutputPath <external-runtime-baseline-bundle>\runtime-baseline.jsonl

powershell -NoProfile -ExecutionPolicy Bypass -File $preSurfaceDriver `
  -Mode Baseline `
  -RepositoryRoot $preRepository `
  -EvidenceRoot <external-runtime-baseline-bundle>\surface-evidence
```

baseline bundle manifest는 predecessor commit/tree, actual argv, 두 PowerShell driver와 `Iris/test/lua/residual_refactor_acceptance_harness.lua`의 logical path/Git blob/working SHA-256, JSONL/binding/evidence manifest, surface baseline files와 각 SHA-256을 기록하고 이후 read-only로 취급한다. driver/harness blob lookup이나 checkout 소속 검증 실패는 baseline 생성 전 fail-close한다.

#### E-2. Post-mutation Lua acceptance, closeout, and syntax

```powershell
$successorRepository = [System.IO.Path]::GetFullPath('<exact-successor-repository>')
$successorRuntimeDriver = Join-Path $successorRepository 'Iris\test\run_residual_refactor_acceptance.ps1'
$successorSurfaceDriver = Join-Path $successorRepository 'Iris\test\validate_residual_refactor_surfaces.ps1'
$successorSyntaxDriver = Join-Path $successorRepository 'tools\check_lua_syntax.ps1'

powershell -NoProfile -ExecutionPolicy Bypass -File $successorRuntimeDriver `
  -Mode Acceptance `
  -RepositoryRoot $successorRepository `
  -OutputPath <external-runtime-successor-evidence>\runtime-acceptance.jsonl

powershell -NoProfile -ExecutionPolicy Bypass -File $successorSurfaceDriver `
  -Mode Closeout `
  -RepositoryRoot $successorRepository `
  -EvidenceRoot <external-runtime-baseline-bundle>\surface-evidence

powershell -NoProfile -ExecutionPolicy Bypass -File $successorSyntaxDriver
```

`Closeout`은 같은 external `surface-evidence` root의 predecessor baseline files를 소비한다. baseline capture 뒤 해당 파일의 hash가 달라졌다면 equivalence 검증은 FAIL이다. successor evidence manifest는 세 driver와 selected Lua harness의 logical path/Git blob/working SHA-256, successor commit/tree와 actual argv를 기록한다.

#### F. Disposable package identity

##### F-1. Pre-mutation manual-baseline package

```powershell
$preRepository = [System.IO.Path]::GetFullPath('<exact-pre-change-repository>')
$prePackageDriver = Join-Path $preRepository 'Iris\tools\package_iris.ps1'

powershell -NoProfile -ExecutionPolicy Bypass -File $prePackageDriver `
  -OutputRoot <external-pre-mutation-package-root> `
  -Clean `
  -Zip `
  -PackageApplicability current_runtime_payload
```

##### F-2. Post-mutation successor package

```powershell
$successorRepository = [System.IO.Path]::GetFullPath('<exact-successor-repository>')
$successorPackageDriver = Join-Path $successorRepository 'Iris\tools\package_iris.ps1'

powershell -NoProfile -ExecutionPolicy Bypass -File $successorPackageDriver `
  -OutputRoot <external-successor-package-root> `
  -Clean `
  -Zip `
  -PackageApplicability current_runtime_payload
```

두 package는 서로 다른 external output root에서 생성하고 각각 source/runtime Lua와 양방향 file-set 및 hash identity를 비교한다. 각 package manifest는 actual argv, exact producer logical path/Git blob/working SHA-256, source commit/tree와 output file/hash를 결속한다. Git blob이 cross-machine producer identity이고 working SHA-256은 해당 checkout materialization이다. 이 검증은 package publication이 아니다.

### Determinism and Mutation Checks

- 같은 exact commit과 environment receipt에서 Run A/B canonical result가 동일해야 한다.
- Run A/B canonical result는 semantic object equality뿐 아니라 raw bytes와 SHA-256도 동일해야 한다. BOM, key order, whitespace, LF/CRLF 또는 trailing newline 차이를 허용하지 않는다.
- full-gate orchestration receipt의 interpreter, environment policy, runner/common Git blob/hash가 claim subject와 일치해야 한다.
- compare writer 채택 또는 writer blob/schema 변경 focused test에서는 같은 Run A/B input으로 생성한 compare attempt 두 개의 byte-preserving stdout/stderr hash와 path-independent canonical receipt fingerprint가 동일해야 한다. 일반 closeout은 이 evidence에 결속된 exact writer blob/schema로 receipt 한 개를 생성한다.
- selected producer의 output file set, byte size와 SHA-256이 동일해야 한다.
- tracked, nonignored untracked, ignored/local source state를 실행 전후 비교한다.
- repository 내부의 새 `.pyc`, `__pycache__`, pytest cache, temp, package 또는 staging output count가 0이어야 한다.
- failure injection 뒤 partial output은 external result root 안에만 남고 receipt가 실패를 정확히 기록해야 한다.
- golden fixture 갱신은 구현 변화에 따라 자동 승인하지 않는다. contract 변화로 판정되면 해당 batch를 중단하고 별도 owner 결정을 받는다.

### Manual Validation

runtime mutation이 적용되는 경우 다음 다섯 Project Zomboid case를 F-1의 **pre-mutation exact package**에서 먼저 실행해 baseline을 만들고, 동일 조건의 F-2 **post-mutation successor package**에서 다시 실행한다. 두 run 모두 tested package hash, package producer Git blob/working SHA-256, source commit/tree, PZ build, Iris version, OS, locale, expected/observed result와 screenshot 또는 PZ log hash를 기록한다.

1. Browser category 순서, 검색, folded variant count, 대표 아이콘/이름, recipe 연결 표시
2. 동일 데이터에서 반복 진입·`resetForReload()`·reload·rebuild 후 대표 항목과 검색 결과의 안정성
3. Wiki core/food/current/legacy wrapper의 수치, label, section order와 nil suppression
4. Tooltip의 Tags → Connections → optional UseCase → More 순서 및 기존 성공/실패 줄 조합
5. debug on/off에서 runtime 결과와 필수 warning/error는 유지되고 진단 로그만 정책대로 달라지는지 확인

pre/post evidence는 case ID로 1:1 대응하며 post-only 관찰로 predecessor expected result를 소급 작성하지 않는다.

Python operator contract는 별도로 다음을 수동 확인한다.

- pilot CLI의 `--help`, invalid args, missing input, success/failure exit code와 메시지
- current/historical/diagnostic output root 상호 비침범
- external root cleanup 및 receipt에서 exact command를 재구성할 수 있는지

### Validation Limits

- 계획 작성 시점에는 구현이나 검증 명령을 실행하지 않았으므로 이 문서 자체는 어떤 PASS도 주장하지 않는다.
- static census는 dynamic import, shell caller, 외부 operator command를 완전히 찾지 못할 수 있다. owner 미확정 항목을 삭제 근거로 사용하지 않는다.
- clean-checkout Run A/B는 exact tracked inputs의 재현성을 검증하지만 모든 historical 외부 환경을 복원하지 않는다.
- golden byte equality는 선택된 producer family에 한정된다. 미이관 recursive/root-direct denominator 전체의 동등성을 자동으로 주장하지 않는다.
- standalone Lua harness와 Lua syntax 검사는 실제 Project Zomboid UI/engine 동작을 대체하지 않는다.
- manual UI 5-case는 전체 아이템·외부 모드 호환성 sweep가 아니다.
- retention inventory는 artifact store/LFS/삭제 정책 결정을 대신하지 않는다.
- package identity 검증은 package publication, install-path 검증, Workshop 또는 release readiness가 아니다.
- external mod compatibility와 장기 세션/멀티플레이는 본 계획의 검증 범위가 아니다.

---

## 8. Risk Surface Touch

### Authority Surface

**Touched.** Clean-checkout validation contract, receipt interpreter/environment, exact runner identity, current-route test dependency와 producer write boundary를 다룬다. DVF/Registry/Publish authority의 소유권은 변경하지 않는다. Launcher/compare receipt는 검증 evidence이지 새 authority가 아니며 explicit authority writer를 generic validation producer로 재분류하지 않는다.

### Runtime Behavior Surface

**Conditional touch.** Change 7이 적용되면 Wiki/Browser/protected-call 내부 구현을 수정한다. 의도된 public behavior 변화는 없지만 predecessor baseline, equivalence evidence와 pre/post manual UI validation 없이는 behavior-preserving을 주장하지 않는다.

### Compatibility Surface

**Touched.** Python direct-script/`-m`/package/bare import, CLI args/stdout/stderr/exit code와 Lua module path/API/return shape를 보존 대상으로 다룬다.

### Sealed Artifact Surface

**Read and validate; no predecessor rewrite.** 기존 sealed evidence와 historical artifact를 입력/근거로 읽을 수 있으나 재직렬화·덮어쓰기하지 않는다. 새 orchestration/compare receipt는 interpreter·environment·runner/common·input/output hash와 BOM-free byte contract를 통과한 additive successor로만 기록한다.

### Public-Facing Output Surface

**Conditional touch — no intentional semantic change.** Change 7은 Wiki/Browser renderer code path를 수정하므로 public-facing surface를 touch한다. 사용자-visible 문자열, 순서, 추천/품질 의미는 변경하지 않으며 equivalence와 pre/post manual UI evidence 없이 보존을 주장하지 않는다. 실제 차이가 발견되면 이 계획의 자동 리팩터링 범위가 아니라 별도 product decision 대상이다.

---

## 9. Risk Analysis

### Architecture Risk

- 공통 helper가 current core 12/allowed tooling 4/4 경계를 우회하는 숨은 hub가 될 수 있다.
- validation launcher/receipt schema가 owner review 없이 새 authority surface로 채택될 수 있다.
- launcher가 Python 진입 전 실패에서 receipt를 남기지 않아 실패 경로가 증거 밖에 놓일 수 있다.
- validation infrastructure가 Registry/DVF/Publish authority를 흡수할 수 있다.
- role manifest가 설명 자료를 넘어 새 authority taxonomy처럼 사용될 수 있다.
- BrowserData의 이미 분리된 책임을 다시 추출해 오히려 상태 ownership이 분산될 수 있다.

**Mitigation:** 기존 `paths.py` 우선, contract-family helper, closure preflight, environment 복원 후 all-path orchestration receipt, non-authority role manifest, receipt schema 별도 owner review와 runtime conditional gate를 사용한다.

### Runtime Risk

- Wiki renderer 분리에서 section order, newline, nil suppression 또는 unit formatting이 바뀔 수 있다.
- Browser candidate/state extraction에서 retry/degraded state나 generation/cache 수명이 바뀔 수 있다.
- raw `pcall`을 ProtectedCall로 바꾸면 release/debug 로그와 warning 수가 바뀔 수 있다.
- legacy wrapper 또는 global-only consumer가 누락될 수 있다.
- 다른 checkout의 runtime/Lua/package driver가 실행되어 predecessor/successor evidence가 섞일 수 있다.

**Mitigation:** public facade 유지, exact checkout absolute driver와 driver/harness/package producer Git blob binding, baseline/acceptance harness, protected-call policy table, legacy module-missing fixture, 분리된 pre/post package의 manual UI evidence를 요구한다.

### Compatibility Risk

- path bootstrap 제거로 direct script 또는 bare import가 깨질 수 있다.
- receipt와 다른 interpreter 또는 다른 checkout runner를 사용해 full-gate가 fail-close하거나 잘못된 identity를 기록할 수 있다.
- file move로 문서·PowerShell·external operator command가 깨질 수 있다.
- common writer가 encoding/newline/error type을 바꿀 수 있다.
- subprocess 함수화가 environment/failure isolation을 없앨 수 있다.

**Mitigation:** 파일 이동 전 import/CLI/caller matrix, old-path wrapper, receipt interpreter direct invocation, exact runner/common binding, exact byte/error golden과 subprocess 유지 기본값을 적용한다.

### Regression Risk

- source-relative producer가 current facts/evidence를 다시 쓸 수 있다.
- ignored/local output은 `git status` 기본 비교만으로 놓칠 수 있다.
- helper migration이 hash manifest와 receipt identity를 바꿀 수 있다.
- PowerShell object capture 또는 BOM이 compare stdout/stderr/receipt hash를 비결정적으로 만들 수 있다.
- Git blob byte와 CRLF/LF checkout materialization hash를 같은 identity로 오판할 수 있다.
- staging retention 오분류로 evidence가 손실될 수 있다.
- primary dirty tree의 사용자 변경과 validation side effect를 혼동할 수 있다.

**Mitigation:** disposable exact checkout, tracked/nonignored/ignored snapshot, Git blob 기반 cross-machine identity와 working SHA-256 기반 materialization identity 분리, byte-preserving stdout/stderr 분리, focused BOM-free writer Run A/B, failure injection, no-delete retention phase, batch rollback과 primary tree 비실행 원칙을 사용한다.

---

## 10. Rollback Plan

- 각 leaf migration은 독립 revert가 가능한 batch로 구현한다.
- output isolation adapter와 producer 내부 helper 변경을 같은 불가분 commit으로 묶지 않는다. adapter만 유지한 채 helper migration을 되돌릴 수 있어야 한다.
- path migration 실패 시 해당 script의 기존 `parents[N]`/`sys.path` bootstrap을 복원하고 `paths.py`의 기존 의미는 유지한다.
- common I/O helper migration 실패 시 producer를 이전 local helper로 복귀하고 golden fixture는 predecessor evidence로 보존한다.
- 공통 helper는 모든 신규 consumer가 revert될 때까지 제거하지 않는다.
- CLI wrapper와 old module path는 compatibility window 동안 유지한다.
- subprocess 전환 실패 시 기존 child-process boundary를 복원하고 실패 receipt를 삭제하지 않는다.
- receipt-bound launcher 또는 compare writer가 identity/encoding/determinism fixture를 통과하지 못하면 해당 support change를 되돌리고 기존 raw runner/validator는 유지한다. 실패한 full-gate/compare attempt를 PASS receipt로 재해석하지 않는다.
- physical topology move가 승인된 경우 old-path wrapper와 caller manifest를 먼저 마련하고, rollback은 원래 path 복원 + 새 wrapper 제거 순서로 한다.
- retention 분류 단계에서는 기존 artifact를 삭제하지 않으므로 데이터 복구 rollback이 필요하지 않다. 향후 deletion/move는 별도 계획과 복원 기간을 요구한다.
- runtime 분리 실패 시 facade를 유지한 채 internal delegation만 이전 구현으로 되돌린다. generated Lua와 package projection을 rollback source로 사용하지 않는다.
- sealed predecessor evidence, nonce, receipt와 terminal을 되돌리거나 덮어쓰지 않는다. 새 attempt가 필요하면 새 식별자와 output root를 사용한다.

---

## 11. Governance Constraints

- `Philosophy.md` 준수와 Hub & Spoke 경계를 유지한다.
- Iris는 다른 spoke를 직접 참조하지 않으며 Pulse도 Iris를 참조하지 않는다.
- build-time producer/validator와 runtime viewer 책임을 혼합하지 않는다.
- 런타임은 오프라인에서 봉인된 fact/description을 표시만 한다.
- DVF Body Compiler, Iris Artifact Registry, Registry Runtime Compatibility, Publish Boundary claim을 서로 대체하지 않는다.
- bare `DVF PASS` 또는 bare `DVF System PASS`를 사용하지 않는다.
- current, historical, diagnostic evidence 역할을 혼합하지 않는다.
- predecessor `c1fa281e` residual claim과 successor plan claim을 같은 PASS 행으로 합치지 않는다.
- 각 predecessor/successor 행은 새 status taxonomy가 아니라 기존 `closeout_state` enum을 사용한다.
- current authority writer를 validation helper로 우회 실행하지 않는다.
- sealed failure와 predecessor evidence를 삭제·덮어쓰기·재생성하지 않는다.
- core 12/allowed tooling 4/4를 편의상 확장하지 않는다.
- recursive, root-direct, tracked, current-core denominator를 count equality로 동일시하지 않는다.
- 기존 sibling common/path support의 owner와 contract를 판정하기 전에 신규 `tools/common/` helper를 중복 도입하지 않는다.
- 새 infrastructure보다 기존 `clean_checkout`, `tools/common/paths.py`, runtime facade와 adapter를 우선 재사용한다.
- generated Lua와 package projection을 직접 수정하지 않는다.
- package mirror는 source writer나 reverse-merge authority가 아니다.
- registry giant 분해, BOM 정규화, historical denominator 축소와 staging tracking 변경은 HOLD를 유지한다.
- minimal diff와 leaf batch를 사용하고 unrelated dirty changes를 보존한다.
- success claim은 exact evidence와 1:1로 결속한다.
- terminal full-gate와 compare validator는 receipt interpreter로 exact claim checkout의 script를 직접 실행한다. `uv run python` 또는 다른 checkout runner를 사용하지 않는다.
- full-gate launcher는 preflight 이전 receipt 상태를 초기화하고 모든 성공·실패 경로를 하나의 `try/catch/finally`로 감싼다. `finally`에서 environment를 먼저 복원하고 orchestration receipt를 쓴 뒤 원래 실패를 재전파하며, receipt writer 실패는 별도 상태로 기록해 closeout을 `blocked`로 둔다.
- runtime/Lua/package 검증은 각 claim checkout의 exact absolute driver와 selected harness만 실행하고 logical path, Git blob ID, working SHA-256, actual argv와 subject commit/tree를 결속한다.
- Git blob ID는 cross-run/cross-machine source identity이고 working-file SHA-256은 checkout materialization identity다. CRLF/LF 차이가 있는 working bytes와 Git blob bytes의 동일성을 요구하지 않는다.
- compare writer A/B는 writer 채택 또는 blob/schema/canonicalization 변경 시 focused determinism gate다. 일반 closeout은 그 gate를 통과한 exact writer blob/schema로 단일 compare receipt를 생성한다.
- orchestration/compare receipt schema ID와 durable current-route adoption은 계획 prose가 아니라 owner-reviewed implementation artifact에서 결정한다.
- closeout은 `validated`, `out_of_scope`, `unvalidated_but_in_scope` validation ceiling을 명시한다.
- runtime validation 없이 runtime success를, deployment 없이 deployed completion을, equivalence evidence 없이 behavior preservation을 주장하지 않는다.

---

## 12. Expected Closeout State

### Target State

이 계획 successor claim의 목표 `closeout_state`는 `complete`다. closeout report는 새 status axis를 만들지 않고 다음 독립 claim row를 기록한다.

| `claim_id` | scope | target `closeout_state` |
|---|---|---|
| `residual_predecessor_c1fa281e` | 선행 residual-refactor의 exact full-gate 및 기존 미결 수동 evidence | `complete` 또는 근거에 따른 `partial` |
| `offline_tool_successor_<commit>` | 이 계획의 output/tool/runtime 변경과 successor Run A/B/compare | `complete` |

각 row는 기존 `complete|partial|implemented_only|blocked` enum, 자체 validation ceiling과 non-claims를 가진다. predecessor 미결은 predecessor row만 `partial`로 유지하며 successor 결과로 소급 승격하지 않는다.

### Required Closeout Conditions

- exact subject의 denominator registry, shared-module provider/consumer/fan-in census와 representative golden contract가 결속되어 있다.
- Change 2 대상은 output isolation batch registry에 path/blob/hash/owner/role/write-set/golden contract가 결속되고 선택 row의 `owner_unknown=0`, `unknown_role=0`이다.
- current-required validation, full-gate producer와 migration 대상 active producer가 repository 밖에만 출력한다.
- success/failure 경로의 source checkout tracked/nonignored/ignored mutation이 0이다.
- full-gate의 성공과 HEAD/dirty/interpreter/blob/pre-Python/native-nonzero 실패를 포함한 모든 시도에 environment 복원 뒤 기록된 orchestration receipt가 있으며, launch/failure/exception/nullable native exit/planned argv/nullable actual argv/environment/identity/result-receipt 필드가 해당 경로에 맞게 완전하다.
- successor Run A/B canonical result raw bytes와 migrated producer output이 결정적이며 compare receipt가 각 Run의 orchestration→inner full-run receipt→canonical result chain, byte-preserving 분리 stdout/stderr, validator, interpreter, environment의 path/hash 및 native exit를 생성 시점에 결속한다.
- exact compare writer Git blob/schema에 대한 채택·변경 focused attempt A/B의 stdout/stderr hash와 path-independent canonical receipt fingerprint가 동일하고, 일반 closeout의 단일 receipt가 그 evidence 및 BOM 없는 writer bytes에 결속된다.
- `tools/common/paths.py` migration batch의 path/import/CLI 동등성이 확인된다.
- I/O/CLI/subprocess helper migration batch의 byte/error/exit/receipt 동등성이 확인된다.
- recursive/root-direct denominator ID별 role manifest와 staging output ownership/retention inventory가 완성된다. role, owner, caller axis의 독립 accounting이 각각 닫히고 `unknown_role`은 seed 55 대비 owner-approved ceiling·근거·이동/삭제 금지를 가진다.
- physical tool move 또는 retention mutation이 승인되지 않았다면 no-move/no-delete closeout으로 명확히 기록한다.
- runtime mutation이 적용된 경우 exact predecessor baseline bundle, supported API, Lua syntax, standalone behavior, predecessor/successor driver·harness Git blob/materialization identity, 분리된 pre/post package identity와 수동 UI 5-case가 모두 검증된다.
- exact successor subject의 receipt interpreter direct invocation, required/cleared environment, exact runner/common blob/hash가 결속된 full-gate Run A/B/compare가 완료되고 external work root가 정리된다.
- `c1fa281e` predecessor full-gate 결과는 별도 claim row에서 독립적으로 `complete` 또는 `partial`로 기록된다.
- closeout claim-boundary가 release/Workshop/B42/deployment readiness를 부정한다.

### Partial Closeout Conditions

다음 중 하나라도 발생하면 영향받은 `claim_id` row는 `partial` 또는 구현만 끝난 경우 `implemented_only`로 기록한다. 단, orchestration receipt writer 자체가 실패해 시도 증거를 보존할 수 없으면 해당 row는 `blocked`다.

- exact successor subject의 receipt-bound Run A/B/compare가 미실행 또는 실패
- 성공·실패 시도의 orchestration receipt 누락, environment 복원 전 receipt 작성, nullable native exit/actual argv/failure/exception/result-receipt field 누락 또는 primary failure 재전파 실패
- orchestration receipt writer 실패. primary failure와 writer failure를 구분해 operator log에 남기고 해당 row를 `blocked`로 유지
- output isolation batch registry의 선택 row에 owner/role/write-set/golden binding이 없거나 `owner_unknown`/`unknown_role`이 남음
- orchestrator/`--python`/receipt interpreter 불일치, required/cleared environment 미결속 또는 exact runner/common identity 누락
- compare stdout/stderr 미분리·재인코딩, BOM 포함, Run A/B raw-byte inequality, orchestration→inner receipt→canonical result chain 또는 immediate execution hash 누락, exact writer blob/schema의 focused determinism evidence 누락·stale 또는 일반 closeout receipt 불일치
- source mutation 또는 output-root escape가 남음
- migration 대상 helper의 byte/hash/error/exit 동등성 미확인
- current closure/owner 판정 없이 새 dependency가 필요함
- runtime mutation 전에 exact predecessor 자동 baseline 또는 F-1 pre-mutation Project Zomboid UI evidence가 없거나, F-2 successor evidence와 1:1 결속되지 않음
- runtime/Lua/package 명령이 해당 predecessor/successor checkout의 exact absolute driver를 쓰지 않았거나 driver/harness/package producer Git blob·working SHA-256·actual argv·subject identity가 누락됨
- runtime Closeout candidate cleanup failure 또는 disposable candidate/package residue
- role/retention manifest의 axis별 denominator accounting, current authority/disposable 구분 또는 `unknown_role` owner ceiling이 미완료
- 적용된 receipt migration batch의 registry path/hash/owner/row denominator binding 미완료
- `uv`(해당 focused route), receipt Python, Lua, `luac` 또는 필수 fixture 부재로 required validation이 blocked

### Non-Claims

이 계획의 `complete`도 다음을 선언하지 않는다.

- 모든 recursive/root-direct historical/one-shot script의 helper 통합 완료
- repository 전체 determinism 완성
- staging 4.27 GiB 정리 또는 Git history 크기 감소
- artifact store 또는 Git LFS 채택
- package publication 또는 deployment
- Registry giant 구조 개선
- 모든 외부 모드 호환성 검증
- release-ready, Workshop-ready 또는 B42-ready
