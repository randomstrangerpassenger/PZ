# Implementation Plan

> 상태: planned / 3차 종합 검토 WARN R-1~R-10 및 후속 N-1~N-3 반영 / fresh review required
> 작성일: 2026-08-04
> 최종 수정일: 2026-08-05
> 기준 readpoint: commit `af1d3c2727491eecaf7ac57b2396e278cb572315`, tree `7e2129e5027d015ff4d04d74a36ed1e489479ff3`
> 양식: `docs/PLAN_TEMPLATE.md`
> 상위 기준: `docs/Philosophy.md`, `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`
> 입력 로드맵: `Iris 저장소·런타임 경량화 종합 제안`
> 선행·병행 기준: `docs/iris_offline_build_validation_and_residual_runtime_structural_improvement_plan.md`
> 리뷰 반영: 3차 종합 plan-level WARN, Critical 5건 및 R-1~R-10

---

## 1. Objective

Iris의 의미 권위, 공개 Lua 계약, 사용자 표시 결과를 바꾸지 않으면서 다음 두 종류의 비용을 단계적으로 줄인다.

1. source checkout 안에 누적되는 대형 producer 산출물과 동일 payload의 반복 직렬화 비용
2. 실제 사용 전에 발생하는 Browser 전체 인덱스 구축과 UseCase / Layer3 전체 청크 병합 비용

선행·병행 계획은 clean-checkout output isolation, golden characterization, 제한적 helper migration을 다루지만 staging 삭제와 generated Lua chunk 변경은 명시적으로 제외한다. 이 계획은 그 범위를 소급 변경하거나 gate 한정 policy를 production authority로 간주하지 않는다. 현재 코드에 존재하는 clean-checkout `--work-root` / `--result-root` 기능을 implementation precedent로만 사용하고, 별도 approval / claim ID와 production-scoped successor output policy가 채택된 뒤 capacity disposition과 generated runtime lookup을 후속 실행 범위로 연다.

2026-08-04 readpoint의 측정 기준은 다음과 같다.

| Surface | Files | Size | Observation |
| --- | ---: | ---: | --- |
| `Iris/` | 7,735 | 4,737,960,614 bytes / 4.413 GiB | 전체 작업 트리의 대부분이 build evidence다. |
| `Iris/build/description/v2/staging/` | 5,212 | 4,586,335,137 bytes / 4.271 GiB | Iris 전체의 약 96.8%다. |
| tracked staging | 3,405 | 423.60 MiB | tracked 여부만으로 current authority 또는 보존 필요성을 판정할 수 없다. |
| ignored staging | 1,807 | 3,950.27 MiB | ignored 여부만으로 삭제 가능성을 판정할 수 없다. |
| Layer3 runtime chunks | 11 | 0.92 MiB | 현재 deployable runtime authority의 일부이며 보호 표면이다. |
| UseCase data directory | 10 | 1.24 MiB | 9개 description chunk와 `RequirementsLookup.lua`로 구성된다. |

가장 큰 단일 원인은 `legacy_active_silent_current_surface_guard_round`가 전체 occurrence payload를 다음 네 파일에 반복 기록하는 경로다.

| File role | Current size |
| --- | ---: |
| allowed occurrence inventory | 851.37 MiB |
| all occurrence JSONL | 788.75 MiB |
| phase 3 adjudication report | 851.37 MiB |
| phase 5 guard report | 851.37 MiB |

이 파일들은 현재 `.gitignore` 규칙상 ignored이지만, 과거 readpoint에서는 약 1.3-1.6 MiB의 tracked evidence였다. 현재 scanner에는 token-match 파일을 반환하는 `rg -l -i --no-ignore` backend와 suffix 대상 전체를 반환하는 Python `rglob` fallback backend가 있어 denominator도 서로 다르다. 어느 경로든 다른 staging / archive-like report를 다시 스캔하고 자기 round만 제외하기 때문에, repository evidence가 늘어날수록 입력 occurrence와 출력 report가 함께 커지는 증폭 구조가 있다.

완료 상태에서는 다음이 성립해야 한다.

* 신규 대형 producer의 transient construction / scratch는 source checkout 밖의 run-scoped work root에, retained object / receipt / manifest / package는 별도 result root에만 기록된다.
* Git에는 canonical manifest, hash, summary, final receipt, seal처럼 작고 검증 가능한 자료만 남는다.
* 동일 payload는 한 번만 직렬화하며 phase / attempt 간 이동은 content hash와 참조로 표현한다.
* 기존 staging은 authority / current-required / historical-reproduction / diagnostic / disposable 역할이 확정된 뒤에만 archive 또는 삭제한다.
* `OnGameBoot`에서는 Browser의 `getAllItems()` 전체 순회가 발생하지 않는다.
* 단일 tooltip 또는 detail 조회가 UseCase 9개 청크나 Layer3 11개 청크 전체를 강제로 병합하지 않는다.
* 기존 public facade의 반환 형태, `IrisBrowserData.build()` 계약, `IrisLayer3Data` compatibility global, UI 문구와 순서는 보존한다.

---

## 2. Scope

이 계획은 먼저 공통 storage lifecycle 변경을 수행하고, 그 closeout 뒤 Runtime Track과 Tooling Track의 실행 순서를 명시적으로 선택한다.

### Common Track - 반드시 먼저 수행

* 현재 코드에 존재하는 clean-checkout work / result root 기능의 contract characterization
* production producer용 additive successor output policy의 owner review와 adoption
* artifact role / producer / consumer / authority / size / hash census
* source checkout 밖의 producer work-root / result-root 계약
* content-addressed payload와 phase reference 계약
* 가장 큰 guard round의 단일 직렬화 pilot
* scan input census 고정과 generated report 재귀 유입 차단
* current-required / historical / diagnostic / disposable 분류
* archive, restore, delete eligibility gate
* staging과 `.gitignore`의 proof-backed 축소

### Runtime Track

* Browser cache build를 boot에서 `openSearch()` / `openForItem()` 최초 사용 시점으로 이동
* Browser cache field 및 search hot path 측정과 보수적 축소
* Layer3 / UseCase 생성기에 chunk range / count index 추가
* internal lookup router를 통한 per-key chunk demand loading
* tooltip final display-line cache와 search prefix cache의 조건부 적용
* 기존 public require facade와 copy-on-read 계약 유지

### Tooling Track

* Common Track에서 승인된 disposable package / temp / ignored producer output 정리
* current / historical / diagnostic 실행 경로와 evidence denominator 분리 유지
* 이번 계획에서 실제로 수정하는 producer에 한정한 path / JSON / hash helper 정리
* 기존 `tools.common.paths`와 residual-refactor inventory를 재사용한 최소 공통화
* zero-consumer가 입증된 파일만 archive / delete candidate로 승격

### Track Order Gate

Common Track closeout 이후 다음 자료를 보고 `runtime_first` 또는 `tooling_first` 중 하나를 durable decision record에 기록한다.

* source-checkout bytes와 producer별 증가량
* boot부터 main menu / game 진입까지 Browser build 호출 수와 시간
* 첫 Browser open, 첫 Alt tooltip, 첫 item detail의 load time과 loaded chunk 수
* current / historical / diagnostic route의 output-root 의존성
* manual Project Zomboid runtime 검증 가능 여부

두 후속 track은 같은 protected runtime / current-route surface를 동시에 수정하지 않는다. 순서가 기록되지 않으면 Common Track만 closeout하고 전체 계획 상태는 `partial`로 남긴다.

Change 5~8의 adopted implementation은 이 gate 이전의 Common commit에 포함하지 않는다. Track Order 전 조사가 필요하면 별도 비채택 experiment branch / external worktree에서만 수행하고 authority, adoption, closeout 근거로 사용하지 않는다. `runtime_first`는 Change 5~7을, `tooling_first`는 Change 8을 먼저 구현·채택한다. 나머지 track은 첫 선택 track의 adoption checkpoint가 닫힌 뒤 별도 commit / subject / receipt로만 시작한다.

### Subject Boundaries

* `physical_capacity_subject`는 ignored / untracked giant artifact가 실제로 존재하는 물리 checkout이다. lifecycle baseline, cleanup candidate, archive / delete 및 pre/post physical byte accounting은 이 subject만을 대상으로 하며 `physical_resolved_root`, HEAD commit / tree, working-tree state, run identity / timestamp를 함께 봉인한다.
* `validation_subject`는 exact successor commit의 clean disposable checkout이다. current / historical / diagnostic route, receipt-bound full-gate, package projection과 tracked source 재현성을 검증한다.
* `validation_subject`에 ignored giant artifact가 없다는 사실은 정상이며, 그 결과를 `physical_capacity_subject`의 byte denominator나 cleanup receipt로 대체하지 않는다. 반대로 dirty / ignored state를 가진 물리 checkout의 census는 exact clean-checkout validation PASS를 대체하지 않는다.
* archive / delete receipt는 exact `physical_capacity_subject`, original resolved path, baseline row identity, archive object identity와 post-delete verification을 결속한다. validation receipt는 별도의 `validation_subject` identity를 결속한다.

### Execution Entry Gates

* Change 1 이전의 ad hoc read-only size probe는 가능하지만 authoritative census, receipt, cleanup eligibility 근거로 사용할 수 없다.
* lifecycle producer, allocator, promotion / executor, native command wrapper와 orchestration support는 먼저 bootstrap commit으로 구현한다. 이 단계는 storage / runtime adoption이 아니며 bootstrap clean validation receipt가 PASS해야 한다.
* authoritative Change 1은 bootstrap 도구 PASS, `report_artifact_lifecycle.py`의 `physical_capacity_subject` support, external output, hash-preserving durable promotion commit, baseline-adoption clean subject의 focused tests와 current-route receipt가 모두 닫힌 뒤에만 성립한다.
* Change 1의 provisional producer output은 승인된 external result root에만 생성한다. 검증된 외부 bytes를 Git-visible durable sink로 승격하고 promotion receipt를 생성하기 전에는 authoritative baseline으로 부르지 않는다.
* Change 2~4 Common Track은 authoritative Change 1 baseline, 선행 output-isolation base contract adoption, `repository_runtime_lightweighting_output_policy.json` owner approval, existing-empty / never-reused root allocator와 diagnostic external-output adoption이 모두 완료되기 전에는 시작하지 않는다.
* Change 3 adoption은 `rg` / explicit Python scan backend의 denominator parity와 fail-loud backend disposition이 구현되기 전에는 시작하지 않는다.
* Change 4 archive / delete는 Change 1~3의 mandatory validation과 reference / restore gates가 모두 닫히기 전에는 시작하지 않는다.
* Change 4 archive / delete는 exact `common_pre_delete_validation_subject`에서 `pre_delete_current_route_receipt`가 PASS하고 machine-checkable delete prerequisites가 모두 닫힌 뒤에만 시작한다. 이 route는 tracked code / current contract를 증명하며 physical 삭제나 byte delta를 직접 증명하지 않는다.
* 첫 authoritative current route 전에 exact required-validation / selected-test closure의 output isolation audit가 별도 disposable audit checkout에서 PASS해야 한다. 이후 closure identity가 바뀌면 다음 current route 전에 audit를 다시 수행한다.
* Runtime / Tooling Track의 구현과 adoption은 Common Track closeout과 durable Track Order 결정 뒤에만 허용한다.
* receipt-bound full-gate는 exact `validation_subject` 안의 `invoke_receipt_bound_full_gate.ps1`와 `invoke_deterministic_compare.ps1`만 authoritative entrypoint로 사용한다. Python runner 직접 호출은 developer diagnostic일 뿐 closeout evidence가 아니다.

### Explicitly Out Of Scope

* Layer3 또는 UseCase의 positional array schema 전환
* `registry` giant script의 분할
* 484개 root-direct build script 전체의 일괄 모듈화
* `IrisData` global 또는 compatibility loader 삭제
* `IrisBrowserData.build`, `getGroupVariants`, `IrisBrowser.openSearch`, `openForItem` 삭제 또는 signature 변경
* `IrisContextMenuTextureCompat`, `IrisBulletReloadCompat`, protected-call wrapper 제거
* Layer3 2105-entry authority 내용, publish state, Korean prose 변경
* current / historical denominator 축소를 cleanup의 부산물로 처리하는 것
* 고정 staging 용량 cap 또는 고정 attempt 보존 개수 도입
* owner seal, reference graph, restore proof 없이 archive 또는 삭제하는 것
* package / release / Workshop readiness 주장
* semantic policy, recommendation, comparison, ranking 추가
* UI redesign 또는 tooltip 최대 4줄 계약 변경

---

## 3. Non-Goals

* runtime에서 source facts를 재해석하거나 description을 새로 생성하지 않는다.
* tracked 파일을 모두 authority로 간주하거나 ignored 파일을 모두 disposable로 간주하지 않는다.
* `Iris/build/package/Iris`를 canonical source로 승격하지 않는다.
* historical route를 current route와 합치지 않는다.
* artifact를 압축했다는 이유만으로 closure가 완료됐다고 주장하지 않는다.
* standalone Lua benchmark를 Project Zomboid / Kahlua runtime 성능의 대체 근거로 사용하지 않는다.
* Browser 또는 tooltip의 표시 결과를 줄여서 성능을 확보하지 않는다.
* 기존 grouping cache와 tooltip summary cache를 중복 구현하지 않는다.
* 측정 전에 임의의 MB, 파일 수, millisecond 목표를 승인 기준으로 고정하지 않는다.

---

## 4. Assumptions

* `docs/Philosophy.md`가 최상위 기준이며 runtime은 offline-sealed facts의 viewer다.
* current Layer3 runtime authority는 `IrisLayer3DataChunks.lua`와 정확히 11개 chunk다. monolith는 current runtime output으로 재도입하지 않는다.
* `IrisLayer3DataChunks.lua`를 직접 require하는 기존 소비자는 full table을 받을 수 있어야 한다. Lua 5.1 / Kahlua의 `pairs` 동작이 불확실한 metatable-only proxy로 이 계약을 대체하지 않는다.
* `IrisUseCaseDescriptions.lua`를 직접 require하는 기존 소비자도 full table과 `_requirementsLookup`을 받을 수 있어야 한다.
* `Iris/API/StaticData.lua`의 public-facing behavior와 session-stable cache semantics는 유지한다.
* `IrisBrowserData.build()`는 supported startup compatibility facade다. boot caller는 바꿀 수 있지만 함수 자체와 boolean adapter semantics는 유지한다.
* `Iris/UI/Browser/IrisBrowser.lua`의 `openSearch()`와 `openForItem()`은 이미 `BrowserBase.ensureBrowserDataBuilt()`를 호출하므로 demand-build 진입점으로 사용할 수 있다.
* generation-scoped `foldedCountsByGrouping` cache의 소유자는 `IrisBrowserData._cache`이며 `IrisBrowserVariantIndex`는 계산 consumer다. `IrisTooltipSummary`의 fullType summary cache도 이미 존재한다. 이 계획은 두 기능을 보존하고 중복 cache를 만들지 않는다.
* tooltip은 현재 Alt를 누른 frame에만 summary를 조회하지만 localized detail line과 배열은 매 frame 재구성한다.
* `build_legacy_active_silent_current_surface_guard_round.py`는 current active core 12개 중 하나다. output-root 변경은 Round 3 closure / allowed-tooling contract를 통과해야 한다.
* current Round 3 route는 `Iris/_docs/round3/round3_run_contract_tests.py --class current --enforce-current-build-closure`다. historical과 diagnostic route는 별도로 보존한다.
* `Iris/build/description/v2/tests/clean_checkout_test_paths.py`와 `IRIS_CLEAN_CHECKOUT_TEST_OUTPUT_ROOT`는 checkout 밖 test output의 선례지만, production producer root는 별도 명시 계약이 필요하다.
* `Iris/validation/residual_refactor/report_inventory.py`와 `Iris/_docs/refactor/residual_refactor/phase0_inventory.json`은 tool-role 기준선으로 재사용한다.
* `Iris/validation/clean_checkout/run_iris_clean_checkout_validation.py`에는 disjoint external `--work-root` / `--result-root` 기능이 구현되어 있다. 그러나 `output_policy.json`의 승인 범위는 `technical_debt_gate`이고 external subroot vocabulary도 `system-temp`, `system-temp/pycache`, `test-output`에 한정된다.
* 현행 runner의 `_require_empty_directory`는 호출 전에 work / result root가 존재하고 비어 있음을 요구한다. 이 계획의 root contract도 `newly allocated, existing, empty`로 맞추며, non-empty root와 이전 attempt가 사용한 normalized path의 재사용은 별도로 거부한다.
* authoritative full-gate launcher는 `Iris/validation/clean_checkout/invoke_receipt_bound_full_gate.ps1`이며 exact checkout 안에서만 실행된다. Run A / Run B 비교는 `invoke_deterministic_compare.ps1`의 orchestration / inner receipt chain을 사용한다.
* pinned interpreter와 immutable environment receipt의 owner authority는 exact checkpoint checkout의 `Iris/validation/clean_checkout/authority/phase0_ratification_attempt_0002.json` 내 `implementation_contract_delta.OR-06`이다. launcher와 command wrapper는 여기서 path / SHA-256를 해소하고 파일 / interpreter hash를 다시 검증한다. owner binding 미채택, missing path 또는 hash mismatch는 `environment_authority_unresolved` blocked다.
* authoritative checkpoint는 각각 새 exact clean checkout이다. bootstrap, baseline adoption, Common pre-delete, Common closeout, selected-track adoption과 terminal successor subject는 commit / tree / claim / receipt가 다르며 이전 checkpoint checkout을 재사용하지 않는다.
* focused pytest는 `-p no:cacheprovider`, 모든 Python은 `-B` / `PYTHONDONTWRITEBYTECODE=1`, test output / uv cache / uv environment는 checkout 밖 approved root를 사용한다. authoritative command는 가능하면 OR-06 pinned Python을 직접 사용하고, `uv`가 필요한 bootstrap command만 external `UV_CACHE_DIR` / `UV_PROJECT_ENVIRONMENT`와 command receipt를 요구한다.
* 2026-08-05 readpoint에서 `Iris/build/description/v2/tests`에는 `test_*.py` 254개가 있고 `clean_checkout_test_paths`를 참조하는 Python file은 22개다. current route는 selected IDs를 `unittest`로 in-process 실행하므로 helper 사용 여부만으로 output isolation을 추정하지 않고 exact selected closure를 전수 감사한다.
* 같은 readpoint의 physical checkout에는 ignored `Iris/build/description/v2/.tmp_tests/tmp*` directory 5개와 ignored `Iris/build/description/v2/tests/tmpg_zgo695` 1개가 보이며 후자는 unreadable이다. 이 잔재는 writer-risk 관찰값이자 lifecycle census 입력일 뿐, bootstrap이나 validation 절차가 임의 삭제하지 않는다. exact audit / validation checkout은 이 physical checkout과 분리한다.
* 선행·병행 계획은 여전히 Draft / fresh-review-pending이다. 이 계획은 그 output policy를 승인 완료된 production contract로 전제하지 않는다.
* production `objects`, `phases`, `logs`, `package` root를 허용하는 additive successor policy는 Change 2의 필수 선행 산출물이다.
* diagnostic adapter의 external output-root 전환과 모든 serialized path descriptor 수정은 predecessor가 아니라 이 계획의 successor claim 범위다. 적용 전 external diagnostic command는 `planned_change_not_adopted`로 blocked이며 실행하지 않는다.
* authoritative lifecycle sink는 external 생성 후 Git-visible durable path로 SHA-256을 보존해 승격하는 Option A다. external provisional output, promoted bytes, promotion receipt와 이를 포함한 commit / tree가 일치해야 Change 4 baseline으로 사용할 수 있다.
* `.gitignore`의 많은 exact unignore rule은 durable evidence 선택을 표현한다. broad staging unignore 또는 broad delete로 단순화하지 않는다.
* `Iris/output/`, `Iris/_archive/`, tracked playtest logs, `console_log.txt`에는 historical / diagnostic 소비자가 남아 있을 수 있다. consumer graph 없이 정리하지 않는다.
* `2105_baseline_consumption_audit/raw_occurrences.jsonl` 계열은 현재 여러 normalization / disposition 도구가 참조한다. consumer migration 전에는 archive / delete 불가다.
* 실행 시작 시 working tree가 clean이거나, unrelated user changes가 별도 baseline manifest에 기록되어 있어야 한다.

---

## 5. Repository Areas Affected

### Code

Common storage lifecycle:

* `Iris/validation/clean_checkout/allocate_repository_runtime_lightweighting_roots.ps1` new, mandatory claim-scoped root allocator
* `Iris/validation/clean_checkout/invoke_repository_runtime_lightweighting_command.ps1` new, mandatory fail-loud native command wrapper
* `Iris/validation/clean_checkout/audit_current_route_output_isolation.py` new, selected current-route closure / temp-write / checkout-delta auditor
* `Iris/validation/clean_checkout/invoke_receipt_bound_full_gate.ps1`
* `Iris/validation/clean_checkout/invoke_deterministic_compare.ps1`
* `Iris/validation/clean_checkout/run_iris_clean_checkout_validation.py`
* `Iris/validation/clean_checkout/authority/phase0_ratification_attempt_0002.json` read-only environment authority reference
* `Iris/validation/clean_checkout/contracts/output_policy.json` read-only predecessor reference
* `Iris/validation/clean_checkout/contracts/repository_runtime_lightweighting_output_policy.json` new, mandatory production-scoped successor contract
* `Iris/validation/residual_refactor/report_inventory.py`
* `Iris/validation/residual_refactor/report_artifact_lifecycle.py` new, mandatory stable artifact-census producer
* `Iris/validation/residual_refactor/promote_artifact_lifecycle_evidence.py` new, mandatory hash-preserving promotion tool
* `Iris/validation/residual_refactor/execute_artifact_lifecycle.py` new, mandatory archive / delete executor
* `Iris/validation/residual_refactor/run_diagnostic_disposition.py`
* `Iris/build/description/v2/tools/common/paths.py`
* `Iris/build/description/v2/tools/common/artifact_paths.py` new, only after the pilot proves a shared contract is needed by at least three current producers
* `Iris/build/description/v2/tools/validate_legacy_active_silent_current_surface_guard.py`
* `Iris/build/description/v2/tools/build/build_legacy_active_silent_current_surface_guard_round.py`
* exact producer scripts selected by the lifecycle census; no glob-based bulk mutation

Runtime:

* `Iris/media/lua/client/Iris/IrisMain.lua`
* `Iris/media/lua/client/Iris/UI/Browser/IrisBrowser.lua`
* `Iris/media/lua/client/Iris/UI/Browser/IrisBrowserBase.lua`
* `Iris/media/lua/client/Iris/UI/Browser/IrisBrowserData.lua`
* `Iris/media/lua/client/Iris/UI/Browser/IrisBrowserItemIndex.lua`
* `Iris/media/lua/client/Iris/UI/Browser/IrisBrowserQuery.lua`
* `Iris/media/lua/client/Iris/UI/Browser/IrisBrowserInteractionRenderer.lua`
* `Iris/media/lua/client/Iris/UI/Browser/IrisBrowserInteractionCollector.lua`
* `Iris/media/lua/client/Iris/UI/Tooltip/IrisTooltipSummary.lua`
* `Iris/media/lua/client/Iris/UI/Tooltip/IrisAltTooltip.lua`
* `Iris/media/lua/client/Iris/API/StaticData.lua`
* `Iris/media/lua/client/Iris/API/UseCases.lua`
* `Iris/media/lua/client/Iris/Data/layer3_renderer.lua`
* `Iris/media/lua/client/Iris/Data/IrisLayer3DataLookup.lua` new internal router
* `Iris/media/lua/client/Iris/Data/IrisUseCaseDescriptionsLookup.lua` new internal router

Generators and package tooling:

* `Iris/build/description/v2/tools/build/export_dvf_3_3_lua_bridge.py`
* `Iris/build/convert_descriptions_to_lua.py`
* `Iris/tools/package_iris.ps1`
* exact runtime adoption / package identity validators that enumerate the protected Layer3 file set

### Tests

* `Iris/validation/clean_checkout/tests/test_iris_clean_checkout_validation.py`
* `Iris/validation/clean_checkout/tests/test_repository_runtime_lightweighting_command_wrapper.py` new
* `Iris/validation/clean_checkout/tests/test_current_route_output_isolation_audit.py` new
* `Iris/build/description/v2/tests/test_legacy_active_silent_current_surface_guard.py`
* `Iris/build/description/v2/tests/test_artifact_work_root_contract.py` new
* `Iris/build/description/v2/tests/test_artifact_lifecycle_inventory.py` new
* `Iris/build/description/v2/tests/test_artifact_lifecycle_promotion.py` new
* `Iris/build/description/v2/tests/test_artifact_lifecycle_executor.py` new
* `Iris/build/description/v2/tests/test_iris_residual_diagnostic_disposition.py`
* `Iris/build/description/v2/tests/test_layer3_data_chunking_contract.py`
* `Iris/build/description/v2/tests/test_layer3_lazy_lookup_contract.py` new
* `Iris/build/description/v2/tests/test_usecase_lazy_lookup_contract.py` new
* `Iris/build/description/v2/tests/test_phase5_iris_main_function_specs_contract.py`
* `Iris/build/description/v2/tests/test_iris_browser_state_selection_search_acceptance.py`
* `Iris/build/description/v2/tests/test_iris_core_refactor_closeout.py`
* `Iris/build/description/v2/tests/test_iris_residual_contract_surfaces.py`
* `Iris/build/description/v2/tests/test_package_layer3_chunks_only_contract.py`
* `Iris/build/test_require_render.py`
* `Iris/test/lua/browser_state_acceptance_harness.lua`

### Docs

* `docs/iris_repository_runtime_lightweighting_plan.md`
* `docs/iris_repository_runtime_lightweighting_closeout.md` after execution
* `docs/DECISIONS.md` only through an approved durable decision packet
* `docs/ARCHITECTURE.md` only if the external producer root or internal lookup boundary becomes current architecture
* `docs/ROADMAP.md` only after validated adoption
* `Iris/build/description/v2/tools/build/INVENTORY.md`
* `Iris/build/ENTRYPOINTS.md`

### Config

* `.gitignore` only after role classification, archive proof, reference checks, and pre/post tracked-path-set sealing
* `Iris/_docs/round3/round3_active_core_closure.json` if a current core import is added
* `Iris/_docs/round3/round3_test_taxonomy.json` to admit adopted Browser / lazy-load / external-diagnostic focused tests
* `Iris/_docs/round3/current_route_required_validations.json` through its existing adoption contract before Runtime Track closeout

### Generated Artifacts

Durable, small, Git-visible artifacts:

* `Iris/_docs/refactor/repository_runtime_lightweighting/validation_checkpoint_manifest.json`
* `Iris/_docs/refactor/repository_runtime_lightweighting/bootstrap_validation_receipt.json`
* `Iris/_docs/refactor/repository_runtime_lightweighting/baseline_inventory.json`
* `Iris/_docs/refactor/repository_runtime_lightweighting/artifact_role_manifest.jsonl`
* `Iris/_docs/refactor/repository_runtime_lightweighting/baseline_promotion_receipt.json`
* `Iris/_docs/refactor/repository_runtime_lightweighting/baseline_adoption_receipt.json`
* `Iris/_docs/refactor/repository_runtime_lightweighting/work_root_contract.json`
* `Iris/_docs/refactor/repository_runtime_lightweighting/producer_migration_manifest.json`
* `Iris/_docs/refactor/repository_runtime_lightweighting/tracking_set_transition.json`
* `Iris/_docs/refactor/repository_runtime_lightweighting/final_inventory.json`
* `Iris/_docs/refactor/repository_runtime_lightweighting/final_artifact_role_manifest.jsonl`
* `Iris/_docs/refactor/repository_runtime_lightweighting/terminal_promotion_receipt.json`
* `Iris/_docs/refactor/repository_runtime_lightweighting/archive_restore_receipt.json`
* `Iris/_docs/refactor/repository_runtime_lightweighting/archive_operation_manifest.json`
* `Iris/_docs/refactor/repository_runtime_lightweighting/archive_promotion_receipt.json`
* `Iris/_docs/refactor/repository_runtime_lightweighting/pre_delete_current_route_receipt.json`
* `Iris/_docs/refactor/repository_runtime_lightweighting/common_closeout_receipt.json`
* `Iris/_docs/refactor/repository_runtime_lightweighting/track_order_decision.json`
* `Iris/_docs/refactor/repository_runtime_lightweighting/selected_track_adoption_receipt.json`
* `Iris/_docs/refactor/repository_runtime_lightweighting/terminal_current_route_receipt.json`
* `Iris/_docs/refactor/repository_runtime_lightweighting/current_route_coverage_map.json`
* `Iris/_docs/refactor/repository_runtime_lightweighting/runtime_benchmark_receipt.json`
* `Iris/_docs/refactor/repository_runtime_lightweighting/final_closeout_receipt.json`

Durable creation mapping:

| Durable file | Creation STEP | Creation / durability method |
| --- | --- | --- |
| `validation_checkpoint_manifest.json` | STEP 2 initial; STEP 5 / 8 / 14 / 17 / 18~20 append | post-purity checkpoint-local canonical writer, reviewed Git commit; prior checkpoint rows are immutable |
| `bootstrap_validation_receipt.json` | STEP 2 | post-purity checkpoint-local canonical writer, reviewed Git commit |
| `baseline_inventory.json` | STEP 4 | external provisional bytes imported by hash-preserving baseline promotion |
| `artifact_role_manifest.jsonl` | STEP 4 | external provisional bytes imported by hash-preserving baseline promotion |
| `baseline_promotion_receipt.json` | STEP 4 | promotion tool receipt proving source / durable SHA-256 identity, reviewed Git commit |
| `baseline_adoption_receipt.json` | STEP 5 | post-purity checkpoint-local canonical writer, reviewed Git commit |
| `work_root_contract.json` | STEP 6 | contract generator writes the reviewed canonical contract directly in the Common candidate commit |
| `producer_migration_manifest.json` | STEP 6 initial; STEP 13 final | Common migration writer updates exact producer rows directly; final reviewed Common commit seals the manifest |
| `tracking_set_transition.json` | STEP 13 | external terminal evidence imported by hash-preserving terminal promotion |
| `final_inventory.json` | STEP 13 | external terminal evidence imported by hash-preserving terminal promotion |
| `final_artifact_role_manifest.jsonl` | STEP 13 | external terminal evidence imported by hash-preserving terminal promotion |
| `terminal_promotion_receipt.json` | STEP 13 | terminal promotion tool receipt proving source / durable SHA-256 identity, reviewed Git commit |
| `archive_restore_receipt.json` | STEP 10 | STEP 9 external archive evidence imported by hash-preserving archive promotion |
| `archive_operation_manifest.json` | STEP 10 | STEP 9 external archive evidence imported by hash-preserving archive promotion |
| `archive_promotion_receipt.json` | STEP 10 | archive promotion tool receipt proving source / durable SHA-256 identity, reviewed Git commit |
| `pre_delete_current_route_receipt.json` | STEP 8 | post-purity checkpoint-local canonical writer, reviewed Git commit before archive starts |
| `common_closeout_receipt.json` | STEP 14 | post-purity checkpoint-local canonical writer, reviewed Git commit |
| `track_order_decision.json` | STEP 15 | owner-authored canonical decision record, schema validation and reviewed Git commit |
| `selected_track_adoption_receipt.json` | STEP 17, once per selected track | post-purity checkpoint-local canonical writer; each track uses a distinct reviewed Git commit / subject |
| `terminal_current_route_receipt.json` | STEP 19 | post-purity checkpoint-local canonical writer, reviewed Git commit before final full-gate closeout |
| `current_route_coverage_map.json` | STEP 5 initial; STEP 17 / 19 final | route-result canonicalizer writes exact direct / indirect coverage rows; reviewed Git commit |
| `runtime_benchmark_receipt.json` | STEP 17 Runtime measurement; STEP 20 manual seal | benchmark canonicalizer writes raw-sample identities and manual evidence binding directly; reviewed Git commit |
| `final_closeout_receipt.json` | STEP 20 | post-purity finalizer binds every durable receipt / command-set hash, then reviewed Git commit |

The ten lifecycle rows created by STEP 4 / 10 / 13 cross an external-to-Git boundary and therefore require the named hash-preserving promotion ceremony. The other thirteen rows are born directly at their Git-visible durable path after the applicable clean post-purity assertion; they use canonical schema validation, review and an ordinary commit rather than importing external bytes. Their `validated_subject_commit` / tree identifies the already-tested subject, while the later checkpoint-manifest row or final closeout records the evidence commit containing the receipt, avoiding a self-referential commit hash. If any of these thirteen files is instead constructed outside the checkout, it loses this exception and must pass the same hash-preserving promotion or a separately approved equivalent before consumption.

The first two lifecycle files become authoritative only after the external provisional bytes are promoted without content change, `baseline_promotion_receipt.json` proves external / durable SHA-256 identity, and the durable files are bound to an adopted commit / tree. Change 4 reads only this promoted durable baseline; it never consumes an unsealed temp path.

`validation_checkpoint_manifest.json` names these non-interchangeable subjects and receipts:

| Checkpoint | Subject | Required receipt |
| --- | --- | --- |
| Bootstrap support | `bootstrap_validation_subject` | `bootstrap_validation_receipt.json` |
| Baseline adoption | `baseline_adoption_validation_subject` | `baseline_adoption_receipt.json` |
| Common pre-delete | `common_pre_delete_validation_subject` | `pre_delete_current_route_receipt.json` |
| Common closeout | `common_closeout_validation_subject` | `common_closeout_receipt.json` |
| Selected track adoption | `selected_track_adoption_subject` | `selected_track_adoption_receipt.json` |
| Terminal successor | `terminal_successor_validation_subject` | `terminal_current_route_receipt.json` plus final closeout receipt |

Every row binds checkpoint ID, claim ID, exact commit / tree, clean-checkout receipt, taxonomy / required-validation identities, environment authority identity and command-receipt-set hash. A later checkpoint may consume an earlier receipt but cannot rewrite its subject or retroactively turn an experiment into adopted evidence.

Source-checkout-external physical locations:

* `<attempt-work-root>/*` for disposable execution checkout, transient construction and process scratch only
* `<attempt-result-root>/objects/sha256/*` for retained content-addressed objects
* `<attempt-result-root>/phases/*` for references and small summaries
* `<attempt-result-root>/logs/*` for retained stdout / stderr and diagnostic records
* `<attempt-result-root>/package/*` for package projection and ZIP
* `<external-append-only-allocation-ledger>` and per-attempt allocation / orchestration / compare receipts, outside every work / result root
* `<external-command-receipt-root>/<checkpoint-id>/*` containing one scalar JSON command-spec, its SHA-256, one receipt and stdout / stderr hashes for every native command

Physical location does not determine lifecycle role. Every external object is separately classified as one of:

* `retained_current_required`
* `retained_historical_reproduction`
* `archived`
* `disposable`
* `delete_eligible`

A durable manifest reference must resolve to a verified object in the active result root, approved cold archive, or another named durable store. Dangling hash references block cleanup and closeout.

Generated runtime support files:

* `Iris/media/lua/client/Iris/Data/IrisLayer3DataChunkIndex.lua`
* `Iris/media/lua/client/Iris/Data/UseCaseDescriptions/ChunkIndex.lua`
* `Iris/media/lua/client/Iris/Data/UseCaseDescriptions/LineCountIndex.lua`

The existing 11 Layer3 chunks and 9 UseCase chunks remain generated authority payloads; their content schema is not changed by this plan.

---

## 6. Planned Changes

### Change 1 - Baseline, Artifact Role Census, and Scope Lock

Purpose:

모든 cleanup과 producer migration 전에 실제 giant artifact를 보유한 `physical_capacity_subject`의 bytes, authority, producer, consumer, route, retention role을 reviewable denominator로 고정하고, 이를 별도의 clean `validation_subject`와 혼동하지 않는다.

Files:

* `Iris/validation/residual_refactor/report_inventory.py`
* `Iris/validation/residual_refactor/report_artifact_lifecycle.py` new, mandatory
* `Iris/validation/residual_refactor/promote_artifact_lifecycle_evidence.py` new, mandatory
* `Iris/build/description/v2/tests/test_artifact_lifecycle_inventory.py` new
* `Iris/build/description/v2/tests/test_artifact_lifecycle_promotion.py` new
* `Iris/_docs/round3/round3_test_taxonomy.json`
* `Iris/_docs/round3/current_route_required_validations.json`
* `Iris/_docs/refactor/repository_runtime_lightweighting/baseline_inventory.json`
* `Iris/_docs/refactor/repository_runtime_lightweighting/artifact_role_manifest.jsonl`
* `Iris/_docs/refactor/repository_runtime_lightweighting/baseline_promotion_receipt.json`

Implementation Notes:

* baseline에는 `subject_kind=physical_capacity_subject`, physical resolved root, commit, tree, working-tree state, inventory timestamp / run identity, physical bytes, file count, tracked / ignored / untracked state와 SHA-256를 포함한다.
* lifecycle `--repo`는 ignored giant 4개가 실제로 존재하는 physical checkout을 가리킨다. exact disposable checkout은 `validation_subject`로 별도 기록하며 lifecycle byte denominator로 사용하지 않는다.
* 이 census는 선행·병행 계획의 tool-role inventory를 대체하지 않는다. 해당 inventory의 subject / denominator를 참조하고 staging capacity와 artifact lifecycle axis만 additive하게 확장한다.
* `report_artifact_lifecycle.py`는 optional implementation branch가 아니라 stable CLI와 `artifact_role_manifest.jsonl` schema를 소유하는 필수 신규 producer다. mandatory CLI는 `--repo`, `--subject-kind physical_capacity_subject|validation_subject`, role row용 `--out`, summary / baseline용 `--summary-out`, subject receipt용 `--subject-receipt-out`, optional terminal comparison용 `--baseline`, `--tracking-transition-out`을 소유한다. 내부에서 `report_inventory.py` helper를 재사용할 수 있지만 command path는 바뀌지 않는다.
* producer는 provisional manifest / summary / subject receipt를 approved external result root에만 기록한다. physical subject identity, ignored giant row count, scoped byte partition, unreadable / unclassified denominator와 output SHA-256가 검증되기 전에는 authoritative가 아니다.
* `promote_artifact_lifecycle_evidence.py baseline`은 external provisional manifest / summary와 subject receipt를 입력으로 받아 동일 bytes를 Git-visible durable root에 승격하고 그 root에 canonical `baseline_promotion_receipt.json`을 생성한다. `--receipt-out`은 byte-identical external operator copy다. receipt는 source / destination descriptor, 각각의 SHA-256, byte length, physical subject identity와 destination repository-relative path를 기록하며 mismatch에서 fail-loud한다.
* 승격된 세 파일을 포함하는 commit / tree가 만들어지고 exact blob / working SHA-256가 promotion receipt와 일치한 뒤에만 Change 1 baseline이 authoritative가 된다. external provisional source는 terminal closeout까지 보존한다.
* authoritative Change 1 receipt는 promotion commit의 새 exact `baseline_adoption_validation_subject`에서 lifecycle / promotion focused tests와 current taxonomy / required-validation route가 PASS하고 `baseline_adoption_receipt.json`이 봉인된 뒤에만 생성한다. final successor까지 기다리거나 ad hoc result를 승격하지 않는다. 그 전 read-only probe는 `non_authoritative_observation`으로만 기록한다.
* 최소 inventory root는 `Iris/build/description/v2/staging`, `Iris/build/package`, `Iris/output`, `Iris/_archive`, `Iris/_docs/round3`, `Iris/_docs/refactor`, repository `docs`, tracked playtest / console logs, temp / cache root다.
* 각 row에는 `logical_artifact_id`, `path`, `producer`, `direct_consumers`, `transitive_consumers`, `route_class`, `authority_role`, `evidence_role`, `regenerable`, `restore_source`, `delete_preconditions`, `size_bytes`, `sha256`를 기록한다.
* `authority_role`은 최소 `current_authority`, `current_required_evidence`, `historical_reproduction`, `diagnostic_only`, `generated_projection`, `disposable`, `unclassified`로 닫는다.
* path access는 authority role과 별도로 `readable`, `missing_referenced`, `unreadable`로 기록한다. permission recovery 후 재실행을 우선하며, 계속 unreadable이면 error type과 available metadata를 `unreadable_hold`로 기록하고 hash / byte completeness를 주장하지 않는다.
* `unclassified_count`와 `unreadable_count`는 별도 denominator다. 둘 중 하나라도 0이 아니면 해당 root의 archive / delete와 complete accounting을 금지한다.
* path 문자열 검색만으로 zero-consumer를 주장하지 않는다. Python import, subprocess invocation, manifest path, package reachability, docs / owner seal references를 별도 축으로 기록한다.
* `git ls-files`, `git check-ignore --no-index`, current required validation manifest를 교차 검증한다.
* 현재 ignored giant 4개, tracked staging 423.60 MiB, `2105_baseline_consumption_audit`, package projection을 별도 high-risk row로 기록한다.
* recursive `tools/build` physical count는 현재 probe의 497과 sealed predecessor 496을 서로 다른 subject / denominator로 기록하고 exact Change 1 checkout에서 재측정한다. root-direct 484도 같은 방식으로 결속한다.
* runtime baseline은 boot build calls, first Browser open, first Alt tooltip, first detail open, loaded chunk module set, search query count를 포함한다.

Validation:

* 같은 tree에서 inventory를 두 번 생성했을 때 stable fields와 row ordering이 byte-identical해야 한다.
* physical checkout fixture에 ignored giant를 두고 clean disposable checkout에는 두지 않았을 때, 두 subject의 census 차이를 명시적으로 검출하고 giant row가 physical denominator에만 포함되어야 한다.
* ignored giant 4개의 exact path / size / SHA-256와 physical resolved root가 subject receipt에 존재해야 한다.
* physical file 합계와 role partition 합계가 같아야 한다.
* 모든 existing path와 missing-but-referenced path가 구분되어야 한다.
* permission-denied fixture는 `unreadable_count`를 증가시키고 archive / delete eligibility를 0으로 만들어야 한다.
* `unclassified_count`, `unreadable_count`, `current_required_count`, `delete_eligible_count`를 fail-loud summary로 제공해야 한다.
* external provisional manifest / summary와 promoted durable bytes의 SHA-256가 각각 같고, altered-source / altered-destination / wrong-subject fixture는 promotion을 차단해야 한다.
* lifecycle / promotion focused test IDs가 current taxonomy와 required-validation result에 존재해야 한다. 채택 전 ad hoc PASS는 implementation evidence일 뿐 Common Track closeout 근거가 아니다.

---

### Change 2 - External Work Root and Content-Addressed Producer Contract

Purpose:

대형 intermediate / phase / attempt payload의 기본 기록 위치를 source checkout 밖으로 이동하고, phase 간 duplicate copy를 hash reference로 대체한다.

Files:

* `Iris/validation/clean_checkout/allocate_repository_runtime_lightweighting_roots.ps1` new, mandatory
* `Iris/validation/clean_checkout/invoke_repository_runtime_lightweighting_command.ps1` new, mandatory
* `Iris/validation/clean_checkout/invoke_receipt_bound_full_gate.ps1`
* `Iris/validation/clean_checkout/invoke_deterministic_compare.ps1`
* `Iris/validation/clean_checkout/run_iris_clean_checkout_validation.py`
* `Iris/validation/clean_checkout/contracts/output_policy.json` read-only predecessor reference
* `Iris/validation/clean_checkout/contracts/repository_runtime_lightweighting_output_policy.json` new, mandatory
* `Iris/validation/residual_refactor/run_diagnostic_disposition.py`
* `Iris/build/description/v2/tools/common/paths.py`
* `Iris/build/description/v2/tools/common/artifact_paths.py` only if the existing clean-checkout contract cannot express the selected producer boundary and the reuse gate passes
* `Iris/build/description/v2/tests/test_artifact_work_root_contract.py`
* `Iris/build/description/v2/tests/test_iris_residual_diagnostic_disposition.py`
* `Iris/validation/clean_checkout/tests/test_iris_clean_checkout_validation.py`
* `Iris/_docs/round3/round3_test_taxonomy.json`
* `Iris/_docs/round3/current_route_required_validations.json`
* selected producer entrypoints from Change 1
* `Iris/_docs/refactor/repository_runtime_lightweighting/work_root_contract.json`

Implementation Notes:

* 현행 clean-checkout orchestrator의 required explicit `--work-root`와 `--result-root` 기능은 implementation precedent다. production authority는 새 successor policy가 owner-reviewed / adopted된 뒤에만 성립한다.
* successor policy는 production `objects`, `phases`, `logs`, `package` subroot, lifecycle role vocabulary, dangling-reference prohibition, terminal receipt fields를 명시한다.
* direct producer도 explicit approved root 없이는 대형 payload를 생성하지 않는다.
* `allocate_repository_runtime_lightweighting_roots.ps1`는 `-AllocationProfile physical-capacity|checkpoint|terminal-run-a|terminal-run-b`를 소유한다. `-Profile`은 PowerShell `$PROFILE`과 혼동되므로 사용하지 않는다. protected repository roots, claim / attempt ID, explicit external parent, external allocation ledger와 receipt output을 required input으로 받고 profile별 named root set을 원자적으로 할당한다.
* `terminal-run-b`는 full-gate compare에 필요한 work / result / orchestration root만 할당한다. 공통 schema 때문에 추가 axis가 생기면 각 row를 `not_used`, `not_required_for_run_b_profile`, `empty_verified`, `delete_eligible_after_closeout`로 disposition하고 terminal receipt에서 검증한다.
* Windows PowerShell 5.1의 external `powershell.exe -File` parameter binder에 `[string[]]` argv를 직접 넘기지 않는다. caller는 executable, ordered `argv` string array, cwd, subject / environment / claim identities, output assertion과 receipt path를 UTF-8 scalar JSON command-spec 하나에 기록하고, wrapper에는 scalar `-CommandSpec <path>`만 전달한다.
* `invoke_repository_runtime_lightweighting_command.ps1`는 command-spec schema / SHA-256를 검증하고 shell 재해석 없이 ordered argv를 실행한다. executable resolved path, decoded argv, command-spec path / hash, cwd, start / end timestamp, native exit, stdout / stderr path와 SHA-256, environment authority / delta, checkpoint subject, run / claim ID와 disposition을 command receipt에 기록한다. wrapped native exit가 nonzero이면 receipt를 먼저 봉인한 뒤 wrapper 자체도 nonzero로 종료한다. `empty_git_porcelain` output assertion은 `git status --porcelain=v1 -z`의 exact dirty entries와 raw SHA-256를 receipt에 기록하고, entry가 하나라도 있으면 semantic exit를 nonzero로 바꿔 checkpoint를 중단한다.
* argv serializer / launcher는 `Invoke-Expression`, script-text interpolation 또는 ambient shell tokenization을 사용하지 않는다. Windows quoting implementation은 `CommandLineToArgvW`-equivalent round trip으로 검증하며 empty string, whitespace, embedded quote, quote 직전 backslash, trailing backslash, non-ASCII, leading dash, semicolon과 wildcard를 byte-for-byte가 아닌 Unicode string sequence equality로 보존한다.
* `checkout_unchanged` output assertion은 `.git` metadata만 제외한 exact checkout path census를 command 전후에 비교하고 tracked / untracked / ignored path addition, removal 또는 content change와 unreadable entry를 receipt에 기록한다. delta나 unreadable entry가 하나라도 있으면 command의 native exit가 0이어도 semantic exit는 nonzero다.
* 매 attempt마다 collision-resistant run ID로 이전 attempt에서 사용하지 않은 normalized path를 할당한다. allocator는 생성 전 filesystem existence와 external append-only allocation ledger를 모두 검사하며, 존재하는 candidate 또는 ledger에 이미 기록된 candidate를 비어 있더라도 거부한다.
* 선택된 새 path는 launcher 호출 전에 allocator가 directory로 생성한다. launcher entry 시점의 work / result root는 `newly allocated, existing, empty`여야 하며, non-empty root는 fail-loud한다. 생성 직후 empty check는 defensive assertion이고 path reuse proof는 생성 전 검사와 allocation ledger가 소유한다.
* 이전 root를 삭제하거나 비운 뒤 같은 normalized path를 새 attempt로 재사용하지 않는다. allocation receipt는 claim ID, attempt ID, run ID, pre-create existence result, ledger lookup result와 모든 resolved root를 기록하며 terminal receipt가 그 hash를 결속한다.
* work root와 result root는 repository 및 서로와 disjoint한 external directory여야 한다. safe OS temp implicit default나 새 ambient environment variable을 추가하지 않는다.
* resolved root가 repository root와 같거나 그 아래이면 fail-loud한다. junction / symlink / reparse resolution failure도 fail-loud한다.
* work root는 disposable execution checkout, transient construction과 process scratch만 소유한다. result root는 retained content-addressed object, phase reference, receipt, manifest, log와 package를 소유한다.
* current, historical, diagnostic raw, diagnostic disposition, package, inventory, full-gate result는 동일 run root 아래에서도 서로 다른 exact subroot를 사용한다.
* payload는 result root의 `objects/sha256/<prefix>/<sha256>`에 한 번만 기록하고 phase artifact는 logical id, hash, size, media type, producer version을 참조한다.
* atomic temp-write + hash verification + rename을 사용한다. partially written object는 canonical object로 승격하지 않는다.
* cleanup은 manifest에 기록된 exact run root만 대상으로 하며 repository root, work-root 전체, unresolved glob을 대상으로 하지 않는다.
* producer가 repository-relative path를 evidence에 기록해야 할 때는 external payload path가 아니라 logical id와 content hash를 canonical reference로 사용한다.
* current core script가 shared helper를 import하면 exact closure manifest와 tests를 갱신한다. broad tooling allowlist는 추가하지 않는다.
* package는 기존 `-OutputRoot`를 사용해 result root 아래의 external package root에 생성한다.
* Windows path budget, non-ASCII path, read-only source checkout, two concurrent run의 충돌을 검증한다.
* Common Track pilot가 안정되기 전에는 모든 producer를 일괄 migration하지 않는다.
* existing `output_policy.json`은 `technical_debt_gate` 범위를 유지한다. 새 schema를 조용히 덧붙이지 않고 별도 successor contract를 채택한다.
* successor claim에서 `invoke_receipt_bound_full_gate.ps1`와 `invoke_deterministic_compare.ps1`는 새 output policy / approval blob identity도 receipt에 결속하도록 additive하게 변경한다. predecessor claim의 기존 policy 해석은 소급 변경하지 않는다.
* external object의 physical location과 lifecycle role을 별도 필드로 기록한다. retained object가 active result root에서 빠지기 전 archive / durable-store successor hash를 결속한다.
* diagnostic external-output 전환은 Change 2의 필수 successor 산출물이다. `run_diagnostic_disposition.py`의 external descriptor로 직렬화되는 모든 path field를 점검한다. 최소 raw report, disposition output, dispositions source identity와 향후 추가되는 recorded path가 대상이며 repository-relative source와 external absolute sink를 tagged descriptor로 구분한다.
* 현재 `raw_out.relative_to(repository_root)`와 `dispositions_path.relative_to(repository_root)` 가정은 descriptor serializer 하나로 대체한다. raw JSON, raw exit, dispositions content identity와 output identity를 보존하며 absolute path를 repository-relative인 것처럼 위장하지 않는다.
* diagnostic adapter의 terminal exit는 `blocking=false`이고 raw exit / report / owner disposition이 일치할 때만 0이다. raw diagnostic exit 1 자체는 승인된 advisory contract에서 정상적으로 보존될 수 있다.
* external raw / disposition focused case는 current taxonomy와 required-validation manifest에 채택된 뒤 Common Track closeout 근거로 사용한다.
* terminal receipt는 모든 resolved work / result / axis subroot, run ID, allocation receipt / ledger identity, pre-create existence check, post-create defensive empty assertion과 lifecycle disposition을 기록한다.

Validation:

* in-checkout root reject, path escape reject, reparse alias reject tests
* newly allocated existing-empty work / result root acceptance test
* pre-existing non-empty root reject와 previous-run ledger path reuse reject tests
* 이전 path를 삭제하거나 비운 뒤 같은 normalized root를 재할당하는 fixture의 fail-loud test
* collision-resistant Run A / Run B가 disjoint root set을 갖는 test
* same content deduplication과 different content separation tests
* interrupted write가 canonical object를 남기지 않는 test
* two-run isolation과 cleanup exact-target test
* manifest-only replay가 payload hash를 검증하는 test
* dangling hash reference가 cleanup과 closeout을 차단하는 test
* diagnostic external raw / disposition output, raw exit `1`, adapter exit `0`, raw identity preservation와 모든 serialized path descriptor test
* Change 2 미적용 상태에서는 external diagnostic step이 실행되지 않고 `planned_change_not_adopted` blocked receipt를 남기는 orchestration fixture
* current route import closure와 allowed tooling exact-set test
* lifecycle, work-root와 external diagnostic focused test IDs의 current taxonomy / required-validation adoption assertion
* launcher fixtures가 exact launcher path, successor policy blob, stdout / stderr 분리, all-path orchestration receipt, Run A / Run B chain과 compare receipt를 검증하고 predecessor policy fixture는 변하지 않아야 한다.
* Windows PowerShell 5.1 scalar command-spec round-trip fixture는 empty / spaced / quoted / backslash / trailing-backslash / Unicode / leading-dash / semicolon / wildcard argv corpus를 child probe가 받은 JSON array와 exact sequence equality로 비교한다. 단일 argument가 array에서 scalar로 축약되거나 empty argument가 사라지는 경우도 FAIL이다.
* command wrapper negative fixtures는 current route 실패 뒤 historical success, archive 실패 뒤 verify success, lifecycle producer 실패 뒤 Git inspection success, package 실패 뒤 ZIP inspection success, diagnostic adapter 실패 뒤 reader success를 주입한다. 첫 nonzero 뒤 후속 command는 `not_run_due_to_prior_failure`이고 checkpoint receipt는 FAIL이어야 한다.
* current-route output-isolation audit fixture는 required-validation selected IDs 전체, imported test module, detected temp / write site와 resolved sink를 매핑한다. separate exact audit checkout의 dynamic route에서 pre/post physical path census가 identical이어야 하며 ignored-path write와 unreadable path fixture는 fail-loud한다.

---

### Change 3 - Largest Guard Producer Single-Serialization Pilot

Purpose:

현재 약 3.26 GiB를 차지하는 네 duplicate occurrence payload를 하나의 canonical stream과 작은 phase summaries로 바꾸고, repository evidence를 입력으로 다시 흡수하는 증폭을 차단한다.

Files:

* `Iris/build/description/v2/tools/validate_legacy_active_silent_current_surface_guard.py`
* `Iris/build/description/v2/tools/build/build_legacy_active_silent_current_surface_guard_round.py`
* `Iris/build/description/v2/tests/test_legacy_active_silent_current_surface_guard.py`
* `Iris/build/description/v2/tests/test_artifact_work_root_contract.py`

Implementation Notes:

* 현재 scanner에는 denominator가 다른 두 경로가 있다. `rg -l -i --no-ignore` 경로는 token-match 파일만 반환하고, `rg` 부재 / 60초 timeout / 비정상 exit 때의 `rglob` fallback은 suffix가 맞는 모든 text file을 반환한다.
* census / role filter / token-match semantics를 `iter_scan_files()` 단일 지점에 적용해 backend와 무관한 canonical ordered file list를 만든다.
* validator / round CLI는 `--scan-backend rg|python`을 소유하고 backend를 receipt에 기록한다. default `rg`의 부재, timeout, 비정상 exit를 무음 fallback하지 않고 fail-loud `scan_backend_unavailable`로 기록한다.
* explicit Python backend는 parity / diagnostic 용도로만 선택할 수 있고, frozen corpus에서 `rg`와 byte-identical canonical path list를 만드는 것이 검증되어야 한다.
* generated report, report-only staging residue, current run output, configured work root, cold archive payload는 scan input에서 제외한다.
* current source, protected runtime, tests, build tool source, explicit historical substrate처럼 guard가 실제로 커버해야 하는 surface는 manifest에 열거한다.
* broad `Iris/build/description/v2/staging/**` allow rule을 그대로 scan denominator로 사용하지 않는다.
* occurrence는 canonical JSONL stream 하나로 기록한다. disposition을 row에 포함해 allowed / unclassified view를 별도 full copy로 만들지 않는다.
* phase 3과 phase 5 report에는 full `occurrences` 배열 대신 stream reference, SHA-256, row count, disposition counts, error summary를 기록한다.
* legacy consumer가 allowed-only payload를 요구하면 external work root에서 on-demand disposable view를 생성하고 canonical receipt에는 그 hash만 남긴다.
* old and new validator를 frozen input census에 적용해 guard verdict, hard-fail count, unclassified count, negative fixture reach parity를 비교한다.
* scan input manifest가 바뀌면 단순 output-size 개선으로 승인하지 않고 coverage delta를 review한다.
* 같은 checkout에서 두 번 실행했을 때 두 번째 run의 input census와 canonical occurrence hash가 첫 번째 run output 때문에 증가하지 않아야 한다.
* every scan receipt records selected backend, backend version / availability, canonical path-list SHA-256, input census SHA-256, denominator count, excluded-role counts, and timeout / error disposition.

Validation:

* exact current / historical / diagnostic scan-surface inclusion tests
* `rg` and explicit Python backend byte-identical canonical path-list test
* `rg` missing, timeout, and abnormal-exit fail-loud tests; no implicit fallback assertion
* report-only and run-owned output exclusion tests
* old/new verdict parity on the same frozen canonical census and named backend
* generated full payload count `1` assertion
* phase summary reference integrity and missing-object fail-loud test
* consecutive-run non-growth / deterministic hash test
* full current Round 3 route with current build closure enforced

---

### Change 4 - Evidence Disposition, Cold Archive, and Safe Repository Cleanup

Purpose:

Common Track pilot가 current / historical 계약을 보존한 뒤 기존 staging을 recoverable하고 proof-backed한 방식으로 축소한다.

Files:

* exact artifact paths approved by `artifact_role_manifest.jsonl`
* `Iris/validation/residual_refactor/execute_artifact_lifecycle.py` new, mandatory
* `Iris/build/description/v2/tests/test_artifact_lifecycle_executor.py` new
* `Iris/_docs/round3/round3_test_taxonomy.json`
* `Iris/_docs/round3/current_route_required_validations.json`
* `.gitignore`
* `Iris/_docs/refactor/repository_runtime_lightweighting/baseline_promotion_receipt.json`
* `Iris/_docs/refactor/repository_runtime_lightweighting/archive_operation_manifest.json`
* `Iris/_docs/refactor/repository_runtime_lightweighting/archive_restore_receipt.json`
* `Iris/build/description/v2/tools/build/INVENTORY.md`

Implementation Notes:

* delete eligibility는 `not current authority`, `not current required`, `zero live consumer`, `historical reproduction preserved`, `archive/restore verified`를 모두 만족해야 한다.
* ignored giant 4개는 Change 3 parity / non-growth / current-route pass 후 첫 cleanup candidate가 될 수 있지만 자동 승인하지 않는다.
* tracked staging 423.60 MiB는 broad deletion하지 않는다. durable manifest / receipt / owner seal은 원래 위치 또는 승인된 successor durable root에 유지한다.
* `2105_baseline_consumption_audit`는 현재 consumer migration이 끝날 때까지 blocked로 둔다.
* `Iris/build/package`, `Iris/build/description/v2/.tmp_tests`, `__pycache__`는 regenerability와 active process reachability가 확인된 뒤 high-confidence disposable class로 처리한다.
* `Iris/output`, `Iris/_archive`, tracked logs는 별도 consumer / historical audit 결과가 없는 한 보존한다.
* cold archive는 source checkout 밖을 기본으로 하며 compressed payload, canonical manifest, file hashes, original logical paths, restore instructions를 포함한다.
* cold archive store는 ordinary attempt result가 아니라 lifecycle role `archived`인 retained root다. archive receipt는 retention owner, durable successor identity, object reference count, `ordinary_attempt_cleanup_excluded=true`, `delete_eligible=false`를 기록한다. restore scratch만 검증 후 disposable이다.
* archive 완료는 random sample이 아니라 manifest 전체 extract + hash validation으로 증명한다.
* `execute_artifact_lifecycle.py`가 명명된 executor다. stable subcommands는 `dry-run`, `archive`, `verify`, `restore-verify`, `validate-delete-prerequisites`, `delete`, `post-delete-census`이며 각 단계는 이전 단계의 immutable receipt SHA-256와 exact `physical_capacity_subject` identity를 입력으로 요구한다.
* `dry-run`은 promoted durable baseline row와 exact approved path만 `archive_operation_manifest.json`에 봉인한다. glob, parent-directory inference, unresolved path와 baseline 밖의 path는 거부한다.
* `archive`는 original path / baseline row / content hash를 cold archive object와 결속하지만 source를 수정하지 않는다. `verify`와 `restore-verify`는 전체 manifest를 별도 external restore root에 materialize하고 모든 SHA-256를 검사한다.
* restore verification 뒤 `promote_artifact_lifecycle_evidence.py archive`가 operation manifest와 archive / verify / restore receipt chain을 `archive_operation_manifest.json`, `archive_restore_receipt.json`, `archive_promotion_receipt.json`으로 Git-visible durable root에 hash-preserving promotion한다.
* `delete`는 owner approval identity, promoted baseline / promotion receipt, committed durable archive receipt / promotion receipt와 final zero-live-reference check가 모두 일치할 때 exact approved leaf path만 삭제한다. deletion은 archive evidence가 durable commit / tree에 bind된 뒤 별도 operator step에서 수행한다.
* `post-delete-census`는 같은 `physical_capacity_subject` resolved root를 다시 읽고 deleted / retained path, scoped byte delta, unexpected path delta와 baseline row identity를 기록한다.
* `.gitignore`는 surviving durable exception을 exact path로 표현한다. broad unignore를 추가하지 않으며, stale exception 제거도 zero-reference 확인 후 수행한다.
* `.gitignore` 변경 전후 `git ls-files -z` path set과 protected artifact manifest를 hash-bind한다. newly tracked path는 approved manifest와 정확히 같아야 하고 unexpectedly untracked protected path는 0이어야 한다.
* terminal lifecycle invocation은 promoted durable Change 1 baseline만 `--baseline`으로 받아 같은 physical subject의 `tracking_set_transition.json`을 external result root에 생성하고, 검증 뒤 hash-preserving promotion으로 durable path에 승격한다.
* 고정 보존 개수 대신 authority role과 final seal 기준으로 retention을 결정한다.

Validation:

* `[physical_capacity_subject]` archive 전체 extract / SHA-256 verification
* `[cross_subject_binding]` fixture에서 `dry-run -> archive -> verify -> restore-verify -> durable promotion -> delete -> post-delete-census` receipt chain과 out-of-order / mismatched-subject rejection
* `[physical_capacity_subject]` exact approved leaf만 삭제되고 glob / parent / baseline 밖 path가 거부되는 executor test
* `[physical_capacity_subject]` deleted path reference graph 재검사
* `[validation_subject]` exact Common pre-delete checkpoint에서 `pre_delete_current_route` PASS. 이 receipt는 code / tracked current contract만 증명하며 ignored giant 존재, 삭제 성공 또는 physical byte delta를 증명하지 않는다.
* `[validation_subject]` Common closeout과 terminal successor checkpoint의 current / historical / diagnostic route
* `[validation_subject]` package regeneration to external output root
* `[cross_subject_binding]` pre/post role totals, physical checkout bytes와 Git tracked bytes 비교
* `[cross_subject_binding]` pre/post tracked path set diff: unapproved newly tracked 0, unexpectedly untracked protected 0
* `[cross_subject_binding]` no current authority / required evidence / runtime payload deletion assertion
* `[physical_capacity_subject]` archive / delete receipt의 physical resolved root, original path, baseline row identity, archive object identity와 post-delete result assertions
* `[validation_subject]` executor focused test IDs의 current taxonomy / required-validation adoption assertion

---

### Change 5 - Browser Demand Build and Runtime Baseline

Entry condition: implement and adopt this change only after Common closeout and a durable `runtime_first` Track Order decision. If Tooling Track is selected first, defer this change until the Tooling adoption checkpoint closes.

Purpose:

`OnGameBoot`에서 발생하는 전체 item scan과 classification cache build를 Browser 최초 사용 시점으로 옮기고, 기존 state / retry / compatibility 계약을 유지한다.

Files:

* `Iris/media/lua/client/Iris/IrisMain.lua`
* `Iris/media/lua/client/Iris/UI/Browser/IrisBrowser.lua`
* `Iris/media/lua/client/Iris/UI/Browser/IrisBrowserBase.lua`
* `Iris/media/lua/client/Iris/UI/Browser/IrisBrowserData.lua`
* `Iris/media/lua/client/Iris/UI/Browser/IrisBrowserItemIndex.lua`
* `Iris/_docs/round3/round3_test_taxonomy.json`
* `Iris/_docs/round3/current_route_required_validations.json`
* related tests and Lua harness

Implementation Notes:

* `IrisMain.INIT_MODULES`에서 `IrisBrowserData` module load는 유지할 수 있지만 `buildBrowserData` invoke를 제거한다.
* `IrisBrowserData.build()`와 `ensureReady()`는 유지한다. `openSearch()` / `openForItem()`의 existing `BrowserBase.ensureBrowserDataBuilt()`가 canonical demand-build boundary가 된다.
* `getAllItems()` 호출 수, scanned item count, build generation, elapsed time, degraded / retryable state를 dev/test instrumentation으로 기록한다.
* boot에서는 `getAllItems()` call count가 0이어야 한다.
* first open 이후 같은 generation에서 전체 scan은 한 번만 발생해야 한다.
* missing required dependency의 `retryable_failed`, optional data의 degraded state, re-open retry semantics를 보존한다.
* startup module order tests는 eager invoke를 요구하지 않도록 새 intended contract로 변경하되, 다른 tooltip / compat / context-menu hook order는 그대로 둔다.
* 고정 시간 budget 대신 동일 machine / save / mod set에서 before-after median과 p95를 기록한다.
* `test_iris_browser_state_selection_search_acceptance.py`는 현재 taxonomy에 포함되지 않은 상태를 baseline으로 기록한다. Change 5 adoption 전에 이 test와 새 boot no-build fixture를 current taxonomy / required-validation route에 명시적으로 채택한다.
* focused Browser test가 current route에 채택되지 않으면 Change 5는 implemented-only / partial이며 Runtime Track closeout으로 승격하지 않는다.

Validation:

* standalone Browser state harness: boot no-build, first-open build, repeat-open no rebuild
* required dependency missing / recovered retry cases
* public `build()` boolean adapter and `_built` compatibility assertions
* current-route `--list` output에 adopted Browser test IDs가 존재하는 assertion
* Project Zomboid boot log에서 Browser build absence 확인
* Browser 검색과 right-click `Iris` open 결과 parity

---

### Change 6 - Internal Layer3 / UseCase Demand Lookup with Public Facade Preservation

Entry condition: implement and adopt this change only as part of the selected Runtime Track, after the Track Order Gate and after Change 5's runtime baseline is available.

Purpose:

single fullType 조회가 전체 generated dataset을 병합하지 않도록 internal lookup path를 추가하되, 기존 direct require와 generated authority shape는 보존한다.

Files:

* `Iris/build/description/v2/tools/build/export_dvf_3_3_lua_bridge.py`
* `Iris/build/convert_descriptions_to_lua.py`
* generated chunk indexes and lookup routers
* `Iris/media/lua/client/Iris/Data/layer3_renderer.lua`
* `Iris/media/lua/client/Iris/API/StaticData.lua`
* `Iris/media/lua/client/Iris/API/UseCases.lua`
* `Iris/media/lua/client/Iris/UI/Browser/IrisBrowserInteractionRenderer.lua`
* `Iris/media/lua/client/Iris/UI/Browser/IrisBrowserInteractionCollector.lua`
* `Iris/media/lua/client/Iris/UI/Tooltip/IrisTooltipSummary.lua`
* package and payload identity validators
* `Iris/_docs/round3/round3_test_taxonomy.json`
* `Iris/_docs/round3/current_route_required_validations.json`

Implementation Notes:

* Layer3 exporter가 이미 fullType key를 정렬해 200-entry chunk를 만들므로 각 chunk의 inclusive first / last key, module name, row count, SHA-256를 deterministic index로 생성한다.
* `IrisLayer3DataLookup.get(fullType)`는 index에서 target module을 찾고 해당 chunk만 require / cache한다.
* `layer3_renderer`는 lookup router를 우선 사용하고, router가 unavailable인 compatibility failure에서만 기존 `IrisLayer3DataChunks` facade로 fail-safe fallback한다.
* `IrisLayer3DataChunks.lua`의 direct require는 계속 11 chunks를 병합하고 `IrisLayer3Data` global을 설정한다. metatable proxy로 바꾸지 않는다.
* UseCase generator도 정렬된 fullType을 200-entry 이하의 disjoint chunk로 생성한다. generator contract test가 first / last key와 non-overlap을 봉인한 뒤 chunk range index와 `fullType -> line count` index를 생성한다.
* `_requirementsLookup`은 fullType range index와 line-count index에서 제외한다. `getRequirements(recipeName)`만 dedicated `RequirementsLookup.lua`를 demand-load한다.
* `IrisUseCaseDescriptionsLookup.get(fullType)`, `getLineCount(fullType)`, `getRequirements(recipeName)`을 internal surface로 제공하고 loaded chunks를 session cache한다.
* `IrisAPI.UseCases`는 lookup을 사용하되 existing `getUseCaseLines`, `getOutcomes`, `getCapabilities` return shape와 copy-on-read를 유지한다.
* Browser interaction renderer / collector는 full `IrisUseCaseDescriptions` facade를 직접 require하지 않고 entry와 requirements lookup을 API / internal adapter로 받는다.
* `IrisTooltipSummary`는 line-count index를 사용해 Alt tooltip이 description chunks를 load하지 않게 한다.
* 기존 `IrisUseCaseDescriptions.lua` direct require는 9 chunks와 RequirementsLookup을 병합하는 compatibility path로 유지한다.
* index는 routing metadata일 뿐 새로운 semantic authority가 아니다. source facts나 text를 수정하지 않는다.
* live payload, package projection, protected-surface manifest, adoption receipt에 새 generated index / router file의 exact identity를 포함한다.
* current 11 Layer3 chunk count, 2105 entry count, UseCase 1631 fullType count는 유지한다.
* focused harness는 injected require spy로 exact module name과 require-call count를 기록한다. PZ dev evidence는 router의 internal loaded-chunk / fallback counters를 기록하며 counters는 semantic API나 public display surface로 노출하지 않는다.
* SHA-256 verification은 offline generator / package / adoption validator의 책임이다. index / chunk hash mismatch는 adoption을 fail-loud로 차단하며 Lua runtime이 SHA-256를 계산하거나 mismatch를 recovery authority로 해석하지 않는다.
* runtime의 reason-coded fallback은 router unavailable, index shape invalid, module name invalid, target module load failure, lookup miss로 한정한다. 이 경우 fail-safe full facade fallback을 허용하고 reason-coded fallback count를 남긴다. 정상 adoption receipt는 `fallback_count = 0`을 요구한다.
* fallback 뒤 결과는 fully materialized public facade와 같아야 한다. fallback이 발생한 run은 lazy-load performance PASS 근거로 사용할 수 없다.
* Layer3 / UseCase focused tests는 Runtime Track adoption 전에 current taxonomy / required-validation route에 명시적으로 채택한다.

Validation:

* all-key lookup parity against fully materialized facade
* missing key, first / last boundary key, adjacent chunk boundary tests
* injected require spy 기준 one Layer3 key loads at most one Layer3 data chunk
* tooltip line count loads zero UseCase description chunks
* injected require spy 기준 one UseCase detail key loads at most one UseCase description chunk
* repeated lookup does not reload a chunk
* offline validator의 index / chunk hash mismatch fail-loud fixtures
* runtime router unavailable, index shape invalid, module name invalid, target module load failure, lookup miss와 compatibility fallback fixtures
* fallback reason / count observability와 fallback-after-full-facade result parity
* direct public facade still materializes the complete table and compatibility global
* deterministic regeneration and chunk/index SHA-256 receipts
* live/package bidirectional identity including new support files
* Lua syntax and Project Zomboid / Kahlua runtime load tests

---

### Change 7 - Browser Cache Slimming and Hot-Path Caches

Entry condition: implement and adopt this change only as part of the selected Runtime Track, after the Track Order Gate and after Change 5's before profile identifies a measured hotspot.

Purpose:

demand loading으로 boot cost를 제거한 뒤, measured duplicate fields와 repeated per-frame / per-keystroke work만 줄인다.

Files:

* `Iris/media/lua/client/Iris/UI/Browser/IrisBrowserData.lua`
* `Iris/media/lua/client/Iris/UI/Browser/IrisBrowserItemIndex.lua`
* `Iris/media/lua/client/Iris/UI/Browser/IrisBrowserQuery.lua`
* `Iris/media/lua/client/Iris/UI/Tooltip/IrisTooltipSummary.lua`
* `Iris/media/lua/client/Iris/UI/Tooltip/IrisAltTooltip.lua`
* focused acceptance tests and harnesses

Implementation Notes:

* before profile에서 cache table별 row / scalar / engine-object reference count를 기록한다.
* `itemsByFullType`의 engine item reference는 `getItem()`과 detail 소비자가 사용하므로 consumer migration 없이 제거하지 않는다.
* `searchKeysByFullType`의 display name, lowercase display name, lowercase fullType 중 중복이 실제 memory / time hotspot으로 확인된 필드만 compact search row로 전환한다.
* search prefix cache는 normalized current query가 previous query의 strict extension이고 build generation / locale가 같을 때만 previous result를 filter한다. backspace, unrelated query, locale change, rebuild에서는 full scan한다.
* debounce는 real PZ input event profile에서 한 keypress에 여러 search가 발생할 때만 추가한다.
* result ordering은 display name, fullType 순서를 그대로 유지한다.
* `IrisBrowserData._cache.foldedCountsByGrouping`이 generation cache를 계속 소유하고 `IrisBrowserVariantIndex`는 계산 consumer로 남는다. duplicate grouping cache를 추가하지 않는다.
* tooltip summary cache는 유지한다. `IrisAltTooltip`에는 `(fullType, locale, summary revision)` keyed final display-line cache를 추가하고 consumer-local array copy를 반환한다.
* locale / data generation change 또는 explicit dev reset에서 cache를 invalidate한다.
* Alt 미입력 시 summary / UseCase lookup은 계속 수행하지 않는다.
* tooltip line text, truncation, order, maximum 4-line policy는 변경하지 않는다.

Validation:

* search before-after result deep equality for empty, casefold, prefix, backspace, no-result, locale cases
* build generation / locale invalidation tests
* cached return mutation이 canonical cache를 오염시키지 않는 test
* repeated tooltip frame에서 localized line rebuild count 감소 확인
* repeated search scan-row count 감소 확인
* Project Zomboid EN / KO Browser, tooltip, Wiki regression check

---

### Change 8 - Tooling Track Hygiene and Conditional Commonization

Entry condition: implement and adopt this change only after Common closeout and a durable `tooling_first` Track Order decision. If Runtime Track is selected first, defer this change until the Runtime adoption checkpoint closes.

Purpose:

Common Track의 role evidence를 사용해 확실한 disposable residue를 정리하고, 이번 계획에서 손댄 producer의 중복만 최소 공통화한다.

Files:

* `Iris/validation/residual_refactor/*`
* `Iris/build/description/v2/tools/common/paths.py`
* `Iris/build/description/v2/tools/common/artifact_paths.py` if approved
* exact touched producer scripts
* `Iris/build/description/v2/tools/build/INVENTORY.md`
* `.gitignore`

Implementation Notes:

* sealed predecessor 496 recursive, current physical probe 497 recursive, 공통 root-direct 484의 denominator drift를 exact checkout에서 다시 측정하고 historical snapshots와 current inventory를 구분한다.
* common helper extraction은 동일한 path / JSON / hash contract가 세 개 이상의 current producers에서 byte-for-byte 같을 때만 수행한다.
* helper extraction 전후에 function input/output, cwd, environment, exit code, stdout/stderr, timeout, partial artifact behavior를 비교한다.
* current / historical / diagnostic route별 import matrix를 유지한다.
* cleanup candidate는 import zero, subprocess zero, manifest reference zero, package reachability zero, historical reproduction preserved를 모두 요구한다.
* giant script data extraction, registry split, broad naming cleanup은 별도 승인 계획으로 남긴다.
* conditional gate가 성립하지 않으면 commonization은 no-op으로 closeout하며 억지로 새 abstraction을 만들지 않는다.

Validation:

* residual-refactor Python import matrix
* Round 3 current / historical / diagnostic route
* helper before-after artifact and stdout/stderr parity
* no newly admitted broad allowed-tooling module
* zero-consumer and no-reference reports for every archive / delete candidate

---

### Change 9 - Track Adoption, Full Validation, and Closeout

Purpose:

각 track의 결과를 현재 authority / runtime / package / evidence 계약에 맞게 adoption하고, storage 절감과 runtime 개선을 과장 없이 봉인한다.

Files:

* `Iris/_docs/refactor/repository_runtime_lightweighting/*`
* protected-surface manifest / approval records required by current governance
* `docs/iris_repository_runtime_lightweighting_closeout.md`
* approved DECISIONS / ARCHITECTURE / ROADMAP packets

Implementation Notes:

* bootstrap support, baseline adoption, Common pre-delete, Common closeout, selected Runtime / Tooling Track adoption과 terminal successor를 별도 commit / clean subject / receipt boundary로 유지한다.
* Track Order Gate의 선택과 근거를 durable record에 남긴다.
* Change 5~8의 adopted code는 `track_order_decision.json` 이전 commit에 존재할 수 없다. 선택 track을 먼저 구현·채택하고 나머지 track은 별도 후속 checkpoint로만 진행한다.
* protected runtime file delta는 pre-change hash, approved successor hash, package identity를 기록한다.
* source-checkout bytes는 exact `physical_capacity_subject`에서 tracked / ignored / untracked로, external footprint는 work scratch peak / retained result / cold archive로 나누어 비교한다. `validation_subject` bytes는 별도 재현성 지표로 기록한다.
* runtime은 boot, first use, warm repeat를 분리해 median / p95와 loaded module set을 비교한다.
* terminal receipt는 validation checkpoint manifest, `pre_delete_current_route_receipt`, `terminal_current_route_receipt`, physical / validation subject identities, baseline promotion receipt / commit / tree, every resolved external axis root, allocation receipts / ledger, Run A / Run B orchestration receipts, deterministic compare receipt, command-receipt-set hash, output-policy schema / approval identity, scan backend / census hash, diagnostic raw exit / adapter disposition, object lifecycle role, cold archive retention disposition, archive successor와 dangling-reference count를 기록한다.
* runtime receipt는 loaded chunk module names / counts와 reason-coded compatibility fallback count를 기록한다. `fallback_count > 0`인 run은 behavior parity evidence가 될 수는 있어도 lazy-load performance PASS가 될 수 없다.
* output text, order, count, publish state, public API surface의 parity report를 생성한다.
* manual PZ validation이 없으면 Runtime Track은 `partial`로 남긴다.
* release, Workshop, multiplayer, long-session stability는 별도 claim으로 남긴다.

Validation:

* Section 7의 automated / manual matrix가 모두 closeout receipt에 bind되어야 한다.
* mandatory gate 중 하나라도 fail / not-run이면 전체 `complete`를 주장하지 않는다.
* diagnostic은 adapter exit 0, `blocking=false`, allowed raw exit와 owner disposition 일치, raw result identity preservation을 mandatory gate로 사용한다.
* full-gate는 exact validation checkout 안의 receipt-bound launcher Run A / Run B와 deterministic compare receipt를 mandatory evidence로 사용한다. Python runner direct invocation 결과는 terminal receipt에 PASS evidence로 들어갈 수 없다.
* `pre_delete_current_route`와 `terminal_current_route`는 서로 다른 exact subject / claim / receipt다. 전자는 Common code / tracked contract의 cleanup 전제이고, 후자는 post-delete / post-promotion final successor closeout evidence다.
* final working tree와 generated external root disposition을 명시한다.

---

## 7. Validation Plan

### Automated Validation

The following order is normative and the blocks are arranged in execution order. A later step cannot run unless the prior checkpoint receipt is PASS and hash-bound into the next subject. Change 5~8 adopted implementation does not begin before STEP 15.

#### STEP 1/20 - Bootstrap support implementation

Implement only the lifecycle producer, allocator, promotion / archive executor, successor policy integration, diagnostic descriptor support, current-route output-isolation auditor and fail-loud command wrapper. Seal them in a bootstrap commit without adopting producer migration, cleanup, Runtime Track or Tooling Track changes.

#### STEP 2/20 - Bootstrap clean validation checkpoint

Materialize a new exact `bootstrap_validation_subject`. Resolve the pinned environment from the owner authority record, then use one wrapper for every native process. Pytest is reserved for pytest-native clean-checkout fixtures and always disables its cache provider; build-contract tests continue to use `unittest` discovery. Both use the same pinned interpreter and external test-output policy.

```powershell
$irisCheckpointCheckout = '<bootstrap-exact-clean-checkout>'
$irisCheckpointCommit = '<bootstrap-exact-commit>'
$irisCheckpointClaimId = '<bootstrap-validation-claim-id>'
$irisCheckpointSubjectReceipt = '<external-bootstrap-subject-receipt>'
$irisExternalAttemptParent = '<approved-external-attempt-parent>'
$irisCommandReceiptRoot = '<external-bootstrap-command-receipt-root>'
$irisEnvironmentDelta = '<external-checkout-pure-environment-delta-receipt>'
$irisPowerShell = (Get-Command powershell -ErrorAction Stop).Source
$irisGit = (Get-Command git -ErrorAction Stop).Source
$irisAuthorityPath = Join-Path $irisCheckpointCheckout 'Iris\validation\clean_checkout\authority\phase0_ratification_attempt_0002.json'
$irisAuthority = Get-Content -Raw -LiteralPath $irisAuthorityPath | ConvertFrom-Json
$irisOwnerEnvironment = $irisAuthority.implementation_contract_delta.'OR-06'
if ($irisOwnerEnvironment.status -ne 'resolved') { throw 'BLOCKED: environment_authority_unresolved' }
$irisEnvironmentReceipt = [System.IO.Path]::GetFullPath([string]$irisOwnerEnvironment.immutable_environment_receipt_path)
if (-not (Test-Path -LiteralPath $irisEnvironmentReceipt -PathType Leaf)) { throw 'BLOCKED: environment receipt missing' }
if ((Get-FileHash -LiteralPath $irisEnvironmentReceipt -Algorithm SHA256).Hash.ToLowerInvariant() -ne [string]$irisOwnerEnvironment.immutable_environment_receipt_sha256) { throw 'BLOCKED: environment receipt hash mismatch' }
$irisEnvironmentPayload = Get-Content -Raw -LiteralPath $irisEnvironmentReceipt | ConvertFrom-Json
$irisPinnedPython = [System.IO.Path]::GetFullPath([string]$irisEnvironmentPayload.interpreter.path)
if ((Get-FileHash -LiteralPath $irisPinnedPython -Algorithm SHA256).Hash.ToLowerInvariant() -ne [string]$irisOwnerEnvironment.interpreter_sha256) { throw 'BLOCKED: interpreter hash mismatch' }
$irisCommandWrapper = Join-Path $irisCheckpointCheckout 'Iris\validation\clean_checkout\invoke_repository_runtime_lightweighting_command.ps1'
[System.IO.Directory]::CreateDirectory($irisCommandReceiptRoot) | Out-Null
$script:irisCommandIndex = 0

function Invoke-IrisNative(
  [string]$Name,
  [string]$Executable,
  [string[]]$ArgumentList,
  [string]$WorkingDirectory,
  [string]$OutputAssertion = 'none',
  [string]$CommandEnvironmentDelta = $irisEnvironmentDelta,
  [string]$CommandClaimId = $irisCheckpointClaimId,
  [string]$CommandSubjectReceipt = $irisCheckpointSubjectReceipt
) {
  $script:irisCommandIndex += 1
  $irisCommandId = ('{0:D3}-{1}' -f $script:irisCommandIndex, $Name)
  $irisCommandReceipt = Join-Path $irisCommandReceiptRoot ($irisCommandId + '.json')
  $irisCommandSpec = Join-Path $irisCommandReceiptRoot ($irisCommandId + '.command.json')
  $irisCommandSpecTemp = $irisCommandSpec + '.tmp-' + [Guid]::NewGuid().ToString('N')
  $irisCommandSpecPayload = [ordered]@{
    schema_version = 'iris_repository_runtime_lightweighting_command_spec_v1'
    executable = [System.IO.Path]::GetFullPath($Executable)
    argv = @($ArgumentList)
    working_directory = [System.IO.Path]::GetFullPath($WorkingDirectory)
    subject_receipt = [System.IO.Path]::GetFullPath($CommandSubjectReceipt)
    environment_receipt = [System.IO.Path]::GetFullPath($irisEnvironmentReceipt)
    environment_delta = [System.IO.Path]::GetFullPath($CommandEnvironmentDelta)
    claim_id = $CommandClaimId
    command_id = $irisCommandId
    command_receipt = [System.IO.Path]::GetFullPath($irisCommandReceipt)
    output_assertion = $OutputAssertion
  }
  $irisUtf8NoBom = New-Object System.Text.UTF8Encoding($false)
  $irisCommandSpecJson = $irisCommandSpecPayload | ConvertTo-Json -Depth 8 -Compress
  [System.IO.File]::WriteAllText($irisCommandSpecTemp, $irisCommandSpecJson, $irisUtf8NoBom)
  Move-Item -LiteralPath $irisCommandSpecTemp -Destination $irisCommandSpec
  & $irisPowerShell -NoProfile -ExecutionPolicy Bypass -File $irisCommandWrapper -CommandSpec $irisCommandSpec
  $irisWrapperExit = $LASTEXITCODE
  if ($irisWrapperExit -ne 0) { throw "native command failed and was receipt-bound: $irisCommandId exit=$irisWrapperExit" }
  return Get-Content -Raw -LiteralPath $irisCommandReceipt | ConvertFrom-Json
}

function Assert-IrisCheckoutClean([string]$Label) {
  Invoke-IrisNative ("git-status-" + $Label) $irisGit @('-C', $irisCheckpointCheckout, 'status', '--porcelain=v1', '-z', '--untracked-files=all') $irisCheckpointCheckout 'empty_git_porcelain'
}

Assert-IrisCheckoutClean 'bootstrap-before'
Invoke-IrisNative 'wrapper-negative-and-argv-fixtures' $irisPinnedPython @('-B', '-m', 'pytest', '-p', 'no:cacheprovider', '-q', 'Iris/validation/clean_checkout/tests/test_repository_runtime_lightweighting_command_wrapper.py') $irisCheckpointCheckout 'checkout_unchanged'
Invoke-IrisNative 'route-output-audit-fixtures' $irisPinnedPython @('-B', '-m', 'pytest', '-p', 'no:cacheprovider', '-q', 'Iris/validation/clean_checkout/tests/test_current_route_output_isolation_audit.py') $irisCheckpointCheckout 'checkout_unchanged'
Invoke-IrisNative 'clean-checkout-fixtures' $irisPinnedPython @('-B', '-m', 'pytest', '-p', 'no:cacheprovider', '-q', 'Iris/validation/clean_checkout/tests/test_iris_clean_checkout_validation.py') $irisCheckpointCheckout 'checkout_unchanged'
Assert-IrisCheckoutClean 'bootstrap-after'
```

```powershell
$irisRouteAuditCheckout = '<separate-exact-current-route-output-audit-checkout>'
$irisRouteAuditEnvironmentDelta = '<external-route-audit-environment-delta-receipt>'
$irisRouteAuditResultRoot = '<external-route-audit-result-root>'
$irisRouteAuditScript = Join-Path $irisRouteAuditCheckout 'Iris\validation\clean_checkout\audit_current_route_output_isolation.py'
$irisRouteRunner = Join-Path $irisRouteAuditCheckout 'Iris\_docs\round3\round3_run_contract_tests.py'
Invoke-IrisNative 'route-audit-git-before' $irisGit @('-C', $irisRouteAuditCheckout, 'status', '--porcelain=v1', '-z', '--untracked-files=all') $irisRouteAuditCheckout 'empty_git_porcelain' $irisRouteAuditEnvironmentDelta
Invoke-IrisNative 'route-audit-static-inventory' $irisPinnedPython @('-B', $irisRouteAuditScript, 'inventory', '--repo', $irisRouteAuditCheckout, '--taxonomy', 'Iris/_docs/round3/round3_test_taxonomy.json', '--required-validations', 'Iris/_docs/round3/current_route_required_validations.json', '--out', "$irisRouteAuditResultRoot/static_inventory.json") $irisRouteAuditCheckout 'checkout_unchanged' $irisRouteAuditEnvironmentDelta
Invoke-IrisNative 'route-audit-current-list' $irisPinnedPython @('-B', $irisRouteRunner, '--class', 'current', '--enforce-current-build-closure', '--list') $irisRouteAuditCheckout 'checkout_unchanged' $irisRouteAuditEnvironmentDelta
Invoke-IrisNative 'route-audit-dynamic-current' $irisPinnedPython @('-B', $irisRouteRunner, '--class', 'current', '--enforce-current-build-closure', '--out', "$irisRouteAuditResultRoot/current_route.json") $irisRouteAuditCheckout 'checkout_unchanged' $irisRouteAuditEnvironmentDelta
Invoke-IrisNative 'route-audit-seal' $irisPinnedPython @('-B', $irisRouteAuditScript, 'seal', '--repo', $irisRouteAuditCheckout, '--static-inventory', "$irisRouteAuditResultRoot/static_inventory.json", '--route-result', "$irisRouteAuditResultRoot/current_route.json", '--command-receipt-root', $irisCommandReceiptRoot, '--out', "$irisRouteAuditResultRoot/current_route_output_isolation_audit_receipt.json") $irisRouteAuditCheckout 'checkout_unchanged' $irisRouteAuditEnvironmentDelta
Invoke-IrisNative 'route-audit-git-after' $irisGit @('-C', $irisRouteAuditCheckout, 'status', '--porcelain=v1', '-z', '--untracked-files=all') $irisRouteAuditCheckout 'empty_git_porcelain' $irisRouteAuditEnvironmentDelta
```

The only values crossing the Windows PowerShell 5.1 external `-File` boundary are the scalar wrapper path and scalar command-spec path. The wrapper validates the JSON schema, retains the spec hash and reconstructs the full ordered argv without PowerShell parameter binding. The round-trip probe must pass before any lifecycle command is admitted.

Before the first authoritative current route, materialize a separate exact `<current-route-output-audit-checkout>`. Run `round3_run_contract_tests.py --class current --list` and `audit_current_route_output_isolation.py` to map every selected ID, imported test module, temp / write site and resolved sink; then run the exact current route in that audit checkout through `Invoke-IrisNative` with `checkout_unchanged`. Use an audit-specific environment delta whose `IRIS_CLEAN_CHECKOUT_TEST_OUTPUT_ROOT`, Python / uv caches and route result all resolve outside both checkouts. Any tracked, untracked or ignored path delta, unreadable entry or unresolved write site is FAIL. The combined external audit receipt binds required-validation / taxonomy / selected-source census hashes and the dynamic route command receipt; `bootstrap_validation_receipt.json` binds its hash. This is an isolation characterization only, not Change 1 current-route authority. A later closure-identity change invalidates the cache and requires the same audit again before that closure's current route.

The normal external environment delta sets `PYTHONDONTWRITEBYTECODE=1`, `IRIS_CLEAN_CHECKOUT_TEST_OUTPUT_ROOT`, `UV_CACHE_DIR` and `UV_PROJECT_ENVIRONMENT` to approved checkout-external roots. If a bootstrap-only `uv` command is unavoidable, it also runs through `Invoke-IrisNative`; authoritative later checkpoints use `$irisPinnedPython` directly. `bootstrap_validation_receipt.json` binds the clean pre/post status, exact dirty-entry arrays including the empty PASS arrays, command-spec / receipt-set hash and output-isolation audit receipt.

#### STEP 3/20 - Physical baseline generation

After bootstrap PASS, allocate the physical-capacity roots. The allocator itself is wrapped and uses `-AllocationProfile`, not the `$PROFILE`-conflicting `-Profile` name.

```powershell
$irisPhysicalCapacityRoot = '<physical-checkout-containing-ignored-artifacts>'
$irisPhysicalCapacityClaimId = '<physical-capacity-claim-id>'
$irisAllocationLedger = '<external-append-only-allocation-ledger>'
$irisAllocationReceiptRoot = Join-Path $irisExternalAttemptParent 'allocation-receipts'
$irisCapacityAllocator = Join-Path $irisPhysicalCapacityRoot 'Iris\validation\clean_checkout\allocate_repository_runtime_lightweighting_roots.ps1'
[System.IO.Directory]::CreateDirectory($irisAllocationReceiptRoot) | Out-Null

function New-IrisAttemptAllocation([string]$Allocator, [string[]]$ProtectedRoots, [string]$AllocationProfile, [string]$Label, [string]$AllocationClaimId, [string]$AllocationSubjectReceipt) {
  $irisAttemptId = [Guid]::NewGuid().ToString('N')
  $irisAllocationReceipt = Join-Path $irisAllocationReceiptRoot ("$Label-$irisAttemptId.json")
  $irisAllocatorArgs = @('-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', $Allocator, '-ProtectedRepositoryRoots') + $ProtectedRoots + @('-ClaimId', $AllocationClaimId, '-AttemptId', $irisAttemptId, '-AllocationProfile', $AllocationProfile, '-ExternalParent', $irisExternalAttemptParent, '-AllocationLedger', $irisAllocationLedger, '-Out', $irisAllocationReceipt)
  Invoke-IrisNative ("allocate-" + $Label) $irisPowerShell $irisAllocatorArgs $irisPhysicalCapacityRoot 'none' $irisEnvironmentDelta $AllocationClaimId $AllocationSubjectReceipt
  return Get-Content -Raw -LiteralPath $irisAllocationReceipt | ConvertFrom-Json
}

# Bootstrap receipt identity is used only to wrap the three read-only Git probes
# that construct this separate physical subject receipt.  No capacity, archive,
# delete, or byte-accounting command runs until the physical receipt exists.
$irisPhysicalSubjectHead = Invoke-IrisNative 'physical-subject-head' $irisGit @('-C', $irisPhysicalCapacityRoot, 'rev-parse', 'HEAD') $irisPhysicalCapacityRoot
$irisPhysicalSubjectTree = Invoke-IrisNative 'physical-subject-tree' $irisGit @('-C', $irisPhysicalCapacityRoot, 'rev-parse', 'HEAD^{tree}') $irisPhysicalCapacityRoot
$irisPhysicalSubjectStatus = Invoke-IrisNative 'physical-subject-status' $irisGit @('-C', $irisPhysicalCapacityRoot, 'status', '--porcelain=v1', '-z', '--untracked-files=all') $irisPhysicalCapacityRoot
$irisPhysicalSubjectAttemptId = [Guid]::NewGuid().ToString('N')
$irisPhysicalCommandSubjectReceipt = Join-Path $irisAllocationReceiptRoot ("physical-command-subject-$irisPhysicalSubjectAttemptId.json")
if ([System.IO.File]::Exists($irisPhysicalCommandSubjectReceipt)) { throw 'physical command subject receipt already exists' }
$irisPhysicalCommandSubjectPayload = [ordered]@{
  schema_version = 'iris_repository_runtime_lightweighting_physical_command_subject_v1'
  subject_kind = 'physical_capacity_subject'
  attempt_id = $irisPhysicalSubjectAttemptId
  claim_id = $irisPhysicalCapacityClaimId
  physical_resolved_root = [System.IO.Path]::GetFullPath($irisPhysicalCapacityRoot)
  commit = ([System.IO.File]::ReadAllText([string]$irisPhysicalSubjectHead.stdout.path)).Trim()
  tree = ([System.IO.File]::ReadAllText([string]$irisPhysicalSubjectTree.stdout.path)).Trim()
  working_tree_status_sha256 = [string]$irisPhysicalSubjectStatus.stdout.sha256
  source_command_receipts = @(
    [string]$irisPhysicalSubjectHead.command_receipt,
    [string]$irisPhysicalSubjectTree.command_receipt,
    [string]$irisPhysicalSubjectStatus.command_receipt
  )
}
$irisPhysicalCommandSubjectJson = $irisPhysicalCommandSubjectPayload | ConvertTo-Json -Depth 8
$irisPhysicalCommandSubjectTemp = $irisPhysicalCommandSubjectReceipt + '.tmp-' + [Guid]::NewGuid().ToString('N')
[System.IO.File]::WriteAllText($irisPhysicalCommandSubjectTemp, ($irisPhysicalCommandSubjectJson.Replace("`r`n", "`n") + "`n"), (New-Object System.Text.UTF8Encoding($false)))
[System.IO.File]::Move($irisPhysicalCommandSubjectTemp, $irisPhysicalCommandSubjectReceipt)

$irisCapacityAttempt = New-IrisAttemptAllocation $irisCapacityAllocator @($irisPhysicalCapacityRoot) 'physical-capacity' 'capacity' $irisPhysicalCapacityClaimId $irisPhysicalCommandSubjectReceipt
$irisInventoryRoot = $irisCapacityAttempt.roots.inventory_result
$irisPromotionRoot = $irisCapacityAttempt.roots.promotion_result
$irisArchiveStore = $irisCapacityAttempt.roots.archive_store
$irisRestoreRoot = $irisCapacityAttempt.roots.restore_result
$irisTerminalInventoryRoot = $irisCapacityAttempt.roots.terminal_inventory_result
$irisLifecycleScript = Join-Path $irisPhysicalCapacityRoot 'Iris\validation\residual_refactor\report_artifact_lifecycle.py'
$irisPromotionScript = Join-Path $irisPhysicalCapacityRoot 'Iris\validation\residual_refactor\promote_artifact_lifecycle_evidence.py'
$irisExecutor = Join-Path $irisPhysicalCapacityRoot 'Iris\validation\residual_refactor\execute_artifact_lifecycle.py'
$irisDurableLifecycleRoot = Join-Path $irisPhysicalCapacityRoot 'Iris\_docs\refactor\repository_runtime_lightweighting'
$irisPromotedBaseline = Join-Path $irisDurableLifecycleRoot 'baseline_inventory.json'

Invoke-IrisNative 'physical-lifecycle-census' $irisPinnedPython @('-B', $irisLifecycleScript, '--repo', $irisPhysicalCapacityRoot, '--subject-kind', 'physical_capacity_subject', '--out', "$irisInventoryRoot/artifact_role_manifest.jsonl", '--summary-out', "$irisInventoryRoot/baseline_inventory.json", '--subject-receipt-out', "$irisInventoryRoot/physical_subject_receipt.json") $irisPhysicalCapacityRoot 'none' $irisEnvironmentDelta $irisPhysicalCapacityClaimId $irisPhysicalCommandSubjectReceipt
Invoke-IrisNative 'physical-lifecycle-focused' $irisPinnedPython @('-B', '-m', 'unittest', 'discover', '-s', (Join-Path $irisPhysicalCapacityRoot 'Iris\build\description\v2\tests'), '-p', 'test_artifact_lifecycle_inventory.py') $irisPhysicalCapacityRoot 'none' $irisEnvironmentDelta $irisPhysicalCapacityClaimId $irisPhysicalCommandSubjectReceipt
```

The census must include the ignored giant four and records `subject_kind=physical_capacity_subject`. This is provisional evidence only.

#### STEP 4/20 - Baseline durable promotion commit

```powershell
Invoke-IrisNative 'baseline-promotion' $irisPinnedPython @('-B', $irisPromotionScript, 'baseline', '--repo', $irisPhysicalCapacityRoot, '--source-manifest', "$irisInventoryRoot/artifact_role_manifest.jsonl", '--source-summary', "$irisInventoryRoot/baseline_inventory.json", '--subject-receipt', "$irisInventoryRoot/physical_subject_receipt.json", '--destination-root', $irisDurableLifecycleRoot, '--receipt-out', "$irisPromotionRoot/baseline_promotion_receipt.json") $irisPhysicalCapacityRoot 'none' $irisEnvironmentDelta $irisPhysicalCapacityClaimId $irisPhysicalCommandSubjectReceipt
```

Review the promoted bytes, commit the durable manifest / baseline / promotion receipt, and retain the external provisional source. No baseline authority is claimed yet.

#### STEP 5/20 - Baseline-adoption clean checkpoint

Materialize a new exact `baseline_adoption_validation_subject` from the promotion commit, re-resolve OR-06, create a new command receipt root, and rerun the STEP 2 wrapper / purity preamble with the new checkpoint variables. Run the lifecycle / promotion focused tests and current route, then seal `baseline_adoption_receipt.json`.

```powershell
$irisCheckpointCheckout = '<baseline-adoption-exact-clean-checkout>'
$irisCheckpointCommit = '<baseline-promotion-commit>'
$irisCheckpointClaimId = '<baseline-adoption-validation-claim-id>'
$irisCheckpointSubjectReceipt = '<external-baseline-adoption-subject-receipt>'
$irisCommandReceiptRoot = '<external-baseline-adoption-command-receipt-root>'
$irisEnvironmentDelta = '<external-baseline-adoption-environment-delta-receipt>'
$irisAuthorityPath = Join-Path $irisCheckpointCheckout 'Iris\validation\clean_checkout\authority\phase0_ratification_attempt_0002.json'
$irisAuthority = Get-Content -Raw -LiteralPath $irisAuthorityPath | ConvertFrom-Json
$irisOwnerEnvironment = $irisAuthority.implementation_contract_delta.'OR-06'
if ($irisOwnerEnvironment.status -ne 'resolved') { throw 'BLOCKED: environment_authority_unresolved' }
$irisEnvironmentReceipt = [System.IO.Path]::GetFullPath([string]$irisOwnerEnvironment.immutable_environment_receipt_path)
if (-not (Test-Path -LiteralPath $irisEnvironmentReceipt -PathType Leaf)) { throw 'BLOCKED: environment receipt missing' }
if ((Get-FileHash -LiteralPath $irisEnvironmentReceipt -Algorithm SHA256).Hash.ToLowerInvariant() -ne [string]$irisOwnerEnvironment.immutable_environment_receipt_sha256) { throw 'BLOCKED: environment receipt hash mismatch' }
$irisEnvironmentPayload = Get-Content -Raw -LiteralPath $irisEnvironmentReceipt | ConvertFrom-Json
$irisPinnedPython = [System.IO.Path]::GetFullPath([string]$irisEnvironmentPayload.interpreter.path)
if ((Get-FileHash -LiteralPath $irisPinnedPython -Algorithm SHA256).Hash.ToLowerInvariant() -ne [string]$irisOwnerEnvironment.interpreter_sha256) { throw 'BLOCKED: interpreter hash mismatch' }
$irisCommandWrapper = Join-Path $irisCheckpointCheckout 'Iris\validation\clean_checkout\invoke_repository_runtime_lightweighting_command.ps1'
[System.IO.Directory]::CreateDirectory($irisCommandReceiptRoot) | Out-Null
$script:irisCommandIndex = 0

Assert-IrisCheckoutClean 'baseline-adoption-before'
Invoke-IrisNative 'baseline-promotion-focused' $irisPinnedPython @('-B', '-m', 'unittest', 'discover', '-s', 'Iris/build/description/v2/tests', '-p', 'test_artifact_lifecycle_promotion.py') $irisCheckpointCheckout 'checkout_unchanged'
$irisCurrentRouteIsolationAudit = Join-Path $irisCheckpointCheckout 'Iris\validation\clean_checkout\audit_current_route_output_isolation.py'
$irisCurrentRouteIsolationReceipt = '<external-current-route-output-isolation-audit-receipt>'
Invoke-IrisNative 'verify-current-route-output-isolation' $irisPinnedPython @('-B', $irisCurrentRouteIsolationAudit, 'verify', '--repo', $irisCheckpointCheckout, '--taxonomy', 'Iris/_docs/round3/round3_test_taxonomy.json', '--required-validations', 'Iris/_docs/round3/current_route_required_validations.json', '--receipt', $irisCurrentRouteIsolationReceipt) $irisCheckpointCheckout 'checkout_unchanged'
Invoke-IrisNative 'baseline-adoption-current-route' $irisPinnedPython @('-B', 'Iris/_docs/round3/round3_run_contract_tests.py', '--class', 'current', '--enforce-current-build-closure', '--out', '<external-baseline-adoption-current-route-result>') $irisCheckpointCheckout 'checkout_unchanged'
Assert-IrisCheckoutClean 'baseline-adoption-after'
```

STEP 7, 8, 14, 17 and 18 repeat the six checkpoint assignments, OR-06 / interpreter / wrapper resolution, new command-receipt directory creation and `$script:irisCommandIndex = 0` reset shown above before their first wrapped command. No checkpoint inherits another checkpoint's checkout, commit, claim, subject receipt, command receipt root, environment delta or command sequence. Allocation claims are passed explicitly; the STEP 3 physical allocation uses `$irisPhysicalCapacityClaimId`, while later checkpoint / terminal allocations use that checkpoint's `$irisCheckpointClaimId`.

`verify-current-route-output-isolation` is repeated immediately before every later current route. It accepts the prior audit only when taxonomy, required-validation selected IDs and selected module-source hashes are identical; otherwise a new separate-checkout static + dynamic audit is mandatory. Each actual current-route command uses `checkout_unchanged`, so ignored writes are failures even when `git status --porcelain` is empty.

`baseline_adoption_receipt.json` binds exact commit / tree, taxonomy, required validations, output-isolation audit receipt, promotion receipt and route result. Only this checkpoint makes Change 1 authoritative. Tests executed only through the route are recorded in `current_route_coverage_map.json` with `coverage_disposition=covered_by_current_route`, taxonomy entry ID and required-validation entry ID.

#### STEP 6/20 - Common Change 2~4 implementation

Implement only the Common Track changes: successor output contract, allocator / launcher integration, diagnostic external descriptors, guard single-serialization pilot, lifecycle classification and archive executor wiring. Change 5~8 code remains absent from this commit.

#### STEP 7/20 - Common candidate validation

Materialize a dedicated exact `common_candidate_validation_subject`, not the future terminal successor checkout. Reinitialize the STEP 2 wrapper / OR-06 context and run Common-only focused tests. No Runtime / Tooling Track test or implementation is admitted here.

```powershell
Assert-IrisCheckoutClean 'common-candidate-before'
Invoke-IrisNative 'common-wrapper-fixtures' $irisPinnedPython @('-B', '-m', 'pytest', '-p', 'no:cacheprovider', '-q', 'Iris/validation/clean_checkout/tests/test_repository_runtime_lightweighting_command_wrapper.py') $irisCheckpointCheckout 'checkout_unchanged'
Invoke-IrisNative 'common-work-root' $irisPinnedPython @('-B', '-m', 'unittest', 'discover', '-s', 'Iris/build/description/v2/tests', '-p', 'test_artifact_work_root_contract.py') $irisCheckpointCheckout 'checkout_unchanged'
Invoke-IrisNative 'common-lifecycle-executor' $irisPinnedPython @('-B', '-m', 'unittest', 'discover', '-s', 'Iris/build/description/v2/tests', '-p', 'test_artifact_lifecycle_executor.py') $irisCheckpointCheckout 'checkout_unchanged'
Invoke-IrisNative 'common-guard' $irisPinnedPython @('-B', '-m', 'unittest', 'discover', '-s', 'Iris/build/description/v2/tests', '-p', 'test_legacy_active_silent_current_surface_guard.py') $irisCheckpointCheckout 'checkout_unchanged'
Invoke-IrisNative 'common-diagnostic' $irisPinnedPython @('-B', '-m', 'unittest', 'discover', '-s', 'Iris/build/description/v2/tests', '-p', 'test_iris_residual_diagnostic_disposition.py') $irisCheckpointCheckout 'checkout_unchanged'
Assert-IrisCheckoutClean 'common-candidate-after'
```

The command-wrapper negative fixtures prove that an earlier native failure stops the step and later commands are `not_run_due_to_prior_failure`; a later success can never overwrite the failing disposition.

#### STEP 8/20 - Authoritative pre-delete current route

Commit the validated Common candidate and materialize a new exact `common_pre_delete_validation_subject`. Reinitialize the clean wrapper context and run the adopted current route before archive eligibility is granted.

```powershell
Assert-IrisCheckoutClean 'pre-delete-before'
$irisPreDeleteRoute = '<external-pre-delete-current-route-result>'
Invoke-IrisNative 'verify-current-route-output-isolation' $irisPinnedPython @('-B', $irisCurrentRouteIsolationAudit, 'verify', '--repo', $irisCheckpointCheckout, '--taxonomy', 'Iris/_docs/round3/round3_test_taxonomy.json', '--required-validations', 'Iris/_docs/round3/current_route_required_validations.json', '--receipt', $irisCurrentRouteIsolationReceipt) $irisCheckpointCheckout 'checkout_unchanged'
Invoke-IrisNative 'pre-delete-current-route' $irisPinnedPython @('-B', 'Iris/_docs/round3/round3_run_contract_tests.py', '--class', 'current', '--enforce-current-build-closure', '--out', $irisPreDeleteRoute) $irisCheckpointCheckout 'checkout_unchanged'
Assert-IrisCheckoutClean 'pre-delete-after'
```

Seal `pre_delete_current_route_receipt.json` with the exact commit / tree, taxonomy / required-validation identity, command receipts and clean pre/post status. Its authority is deliberately limited to Common code and tracked current-contract behavior; it does not prove the ignored giant files exist, that deletion succeeded or that physical bytes changed.

#### STEP 9/20 - Non-destructive archive and full verification

`pre_delete_current_route_receipt.json` is a mandatory input. The archive store is retained with lifecycle role `archived`; restore scratch is disposable after verification.

```powershell
$irisApprovedSelection = '<owner-approved-exact-baseline-row-selection>'
Invoke-IrisNative 'archive-dry-run' $irisPinnedPython @('-B', $irisExecutor, 'dry-run', '--repo', $irisPhysicalCapacityRoot, '--baseline', $irisPromotedBaseline, '--promotion-receipt', (Join-Path $irisDurableLifecycleRoot 'baseline_promotion_receipt.json'), '--pre-delete-route-receipt', '<durable-pre-delete-current-route-receipt>', '--selection', $irisApprovedSelection, '--manifest-out', "$irisArchiveStore/archive_operation_manifest.json", '--receipt-out', "$irisArchiveStore/dry_run_receipt.json") $irisPhysicalCapacityRoot 'none' $irisEnvironmentDelta $irisPhysicalCapacityClaimId $irisPhysicalCommandSubjectReceipt
Invoke-IrisNative 'archive-create' $irisPinnedPython @('-B', $irisExecutor, 'archive', '--repo', $irisPhysicalCapacityRoot, '--operation-manifest', "$irisArchiveStore/archive_operation_manifest.json", '--prior-receipt', "$irisArchiveStore/dry_run_receipt.json", '--archive-root', $irisArchiveStore, '--receipt-out', "$irisArchiveStore/archive_receipt.json") $irisPhysicalCapacityRoot 'none' $irisEnvironmentDelta $irisPhysicalCapacityClaimId $irisPhysicalCommandSubjectReceipt
Invoke-IrisNative 'archive-verify' $irisPinnedPython @('-B', $irisExecutor, 'verify', '--operation-manifest', "$irisArchiveStore/archive_operation_manifest.json", '--prior-receipt', "$irisArchiveStore/archive_receipt.json", '--receipt-out', "$irisArchiveStore/archive_verify_receipt.json") $irisPhysicalCapacityRoot 'none' $irisEnvironmentDelta $irisPhysicalCapacityClaimId $irisPhysicalCommandSubjectReceipt
Invoke-IrisNative 'archive-restore-verify' $irisPinnedPython @('-B', $irisExecutor, 'restore-verify', '--operation-manifest', "$irisArchiveStore/archive_operation_manifest.json", '--prior-receipt', "$irisArchiveStore/archive_verify_receipt.json", '--restore-root', $irisRestoreRoot, '--receipt-out', "$irisArchiveStore/restore_verify_receipt.json") $irisPhysicalCapacityRoot 'none' $irisEnvironmentDelta $irisPhysicalCapacityClaimId $irisPhysicalCommandSubjectReceipt
```

Each wrapped command must exit 0 before the next starts. The archive receipt records retention owner, durable successor, reference count, `ordinary_attempt_cleanup_excluded=true` and `delete_eligible=false`.

#### STEP 10/20 - Archive evidence promotion commit

```powershell
Invoke-IrisNative 'archive-evidence-promotion' $irisPinnedPython @('-B', $irisPromotionScript, 'archive', '--repo', $irisPhysicalCapacityRoot, '--source-operation-manifest', "$irisArchiveStore/archive_operation_manifest.json", '--source-archive-receipt', "$irisArchiveStore/archive_receipt.json", '--source-verify-receipt', "$irisArchiveStore/archive_verify_receipt.json", '--source-restore-receipt', "$irisArchiveStore/restore_verify_receipt.json", '--destination-root', $irisDurableLifecycleRoot, '--receipt-out', "$irisPromotionRoot/archive_promotion_receipt.json") $irisPhysicalCapacityRoot 'none' $irisEnvironmentDelta $irisPhysicalCapacityClaimId $irisPhysicalCommandSubjectReceipt
```

Review and commit the promoted archive manifest / restore / promotion receipts before requesting delete approval.

#### STEP 11/20 - Machine-checkable delete prerequisite gate

The owner approval is resolved only after the archive-evidence commit. `validate-delete-prerequisites` checks the archive hashes, full verification, restore proof, exact leaf manifest, owner approval, `pre_delete_current_route_receipt`, physical subject, baseline and zero-live-reference report.

```powershell
$irisArchiveEvidenceCommit = '<exact-commit-containing-promoted-archive-evidence>'
$irisDeleteApproval = '<owner-delete-approval-receipt>'
$irisDeletePrerequisiteReceipt = "$irisArchiveStore/delete_prerequisite_receipt.json"
Invoke-IrisNative 'delete-prerequisites' $irisPinnedPython @('-B', $irisExecutor, 'validate-delete-prerequisites', '--repo', $irisPhysicalCapacityRoot, '--baseline', $irisPromotedBaseline, '--operation-manifest', (Join-Path $irisDurableLifecycleRoot 'archive_operation_manifest.json'), '--archive-receipt', (Join-Path $irisDurableLifecycleRoot 'archive_restore_receipt.json'), '--archive-promotion-receipt', (Join-Path $irisDurableLifecycleRoot 'archive_promotion_receipt.json'), '--archive-evidence-commit', $irisArchiveEvidenceCommit, '--pre-delete-route-receipt', '<durable-pre-delete-current-route-receipt>', '--approval', $irisDeleteApproval, '--out', $irisDeletePrerequisiteReceipt) $irisPhysicalCapacityRoot 'none' $irisEnvironmentDelta $irisPhysicalCapacityClaimId $irisPhysicalCommandSubjectReceipt
```

#### STEP 12/20 - Owner-approved exact delete and post-delete census

```powershell
$irisDurableArchiveManifest = Join-Path $irisDurableLifecycleRoot 'archive_operation_manifest.json'
Invoke-IrisNative 'exact-delete' $irisPinnedPython @('-B', $irisExecutor, 'delete', '--repo', $irisPhysicalCapacityRoot, '--operation-manifest', $irisDurableArchiveManifest, '--prerequisite-receipt', $irisDeletePrerequisiteReceipt, '--receipt-out', "$irisArchiveStore/delete_receipt.json") $irisPhysicalCapacityRoot 'none' $irisEnvironmentDelta $irisPhysicalCapacityClaimId $irisPhysicalCommandSubjectReceipt
Invoke-IrisNative 'post-delete-census' $irisPinnedPython @('-B', $irisExecutor, 'post-delete-census', '--repo', $irisPhysicalCapacityRoot, '--baseline', $irisPromotedBaseline, '--operation-manifest', $irisDurableArchiveManifest, '--prior-receipt', "$irisArchiveStore/delete_receipt.json", '--receipt-out', "$irisArchiveStore/post_delete_census_receipt.json") $irisPhysicalCapacityRoot 'none' $irisEnvironmentDelta $irisPhysicalCapacityClaimId $irisPhysicalCommandSubjectReceipt
```

No delete command appears elsewhere in this plan.

#### STEP 13/20 - Terminal physical evidence promotion and Common closeout commit

```powershell
Invoke-IrisNative 'terminal-physical-census' $irisPinnedPython @('-B', $irisLifecycleScript, '--repo', $irisPhysicalCapacityRoot, '--subject-kind', 'physical_capacity_subject', '--baseline', $irisPromotedBaseline, '--out', "$irisTerminalInventoryRoot/final_artifact_role_manifest.jsonl", '--summary-out', "$irisTerminalInventoryRoot/final_inventory.json", '--subject-receipt-out', "$irisTerminalInventoryRoot/final_physical_subject_receipt.json", '--tracking-transition-out', "$irisTerminalInventoryRoot/tracking_set_transition.json") $irisPhysicalCapacityRoot 'none' $irisEnvironmentDelta $irisPhysicalCapacityClaimId $irisPhysicalCommandSubjectReceipt
Invoke-IrisNative 'terminal-evidence-promotion' $irisPinnedPython @('-B', $irisPromotionScript, 'terminal', '--repo', $irisPhysicalCapacityRoot, '--baseline-promotion-receipt', (Join-Path $irisDurableLifecycleRoot 'baseline_promotion_receipt.json'), '--source-manifest', "$irisTerminalInventoryRoot/final_artifact_role_manifest.jsonl", '--source-summary', "$irisTerminalInventoryRoot/final_inventory.json", '--source-transition', "$irisTerminalInventoryRoot/tracking_set_transition.json", '--destination-root', $irisDurableLifecycleRoot, '--receipt-out', "$irisPromotionRoot/terminal_promotion_receipt.json") $irisPhysicalCapacityRoot 'none' $irisEnvironmentDelta $irisPhysicalCapacityClaimId $irisPhysicalCommandSubjectReceipt
Invoke-IrisNative 'repository-diff-check' $irisGit @('-C', $irisPhysicalCapacityRoot, 'diff', '--check') $irisPhysicalCapacityRoot 'none' $irisEnvironmentDelta $irisPhysicalCapacityClaimId $irisPhysicalCommandSubjectReceipt
Invoke-IrisNative 'repository-diff-stat' $irisGit @('-C', $irisPhysicalCapacityRoot, 'diff', '--stat') $irisPhysicalCapacityRoot 'none' $irisEnvironmentDelta $irisPhysicalCapacityClaimId $irisPhysicalCommandSubjectReceipt
```

Review and commit the terminal lifecycle evidence as the Common closeout candidate. Physical cleanup authority remains in the physical receipts; the next clean checkpoint validates tracked Common state.

#### STEP 14/20 - Common closeout clean checkpoint

Materialize a new exact `common_closeout_validation_subject`, reinitialize the STEP 2 wrapper / OR-06 context and allocate a `checkpoint` profile with distinct route, diagnostic and package result roots.

```powershell
$irisCheckpointAllocator = Join-Path $irisCheckpointCheckout 'Iris\validation\clean_checkout\allocate_repository_runtime_lightweighting_roots.ps1'
$irisCommonCloseoutAttempt = New-IrisAttemptAllocation $irisCheckpointAllocator @($irisPhysicalCapacityRoot, $irisCheckpointCheckout) 'checkpoint' 'common-closeout' $irisCheckpointClaimId $irisCheckpointSubjectReceipt
Assert-IrisCheckoutClean 'common-closeout-before'
Invoke-IrisNative 'verify-current-route-output-isolation' $irisPinnedPython @('-B', $irisCurrentRouteIsolationAudit, 'verify', '--repo', $irisCheckpointCheckout, '--taxonomy', 'Iris/_docs/round3/round3_test_taxonomy.json', '--required-validations', 'Iris/_docs/round3/current_route_required_validations.json', '--receipt', $irisCurrentRouteIsolationReceipt) $irisCheckpointCheckout 'checkout_unchanged'
Invoke-IrisNative 'common-closeout-current' $irisPinnedPython @('-B', 'Iris/_docs/round3/round3_run_contract_tests.py', '--class', 'current', '--enforce-current-build-closure', '--out', "$($irisCommonCloseoutAttempt.roots.current_result)/current_route.json") $irisCheckpointCheckout 'checkout_unchanged'
Invoke-IrisNative 'common-closeout-historical' $irisPinnedPython @('-B', 'Iris/_docs/round3/round3_run_contract_tests.py', '--class', 'historical', '--out', "$($irisCommonCloseoutAttempt.roots.historical_result)/historical_route.json") $irisCheckpointCheckout 'checkout_unchanged'
Invoke-IrisNative 'common-closeout-diagnostic' $irisPinnedPython @('-B', 'Iris/validation/residual_refactor/run_diagnostic_disposition.py', '--runner', 'Iris/_docs/round3/round3_run_contract_tests.py', '--raw-out', "$($irisCommonCloseoutAttempt.roots.diagnostic_raw_result)/diagnostic_raw.json", '--dispositions', 'Iris/_docs/refactor/residual_refactor/diagnostic_advisory_dispositions.json', '--out', "$($irisCommonCloseoutAttempt.roots.diagnostic_disposition_result)/diagnostic_disposition.json") $irisCheckpointCheckout 'checkout_unchanged'
Assert-IrisCheckoutClean 'common-closeout-after'
```

The diagnostic adapter must exit 0. Its nested raw exit may be approved advisory 1 only when `blocking=false` and raw / disposition / source identities agree. Seal `common_closeout_receipt.json`; this closes Common Track but does not authorize either follow-up track yet.

#### STEP 15/20 - Durable Track Order decision

Use the Common closeout measurements to commit `track_order_decision.json` with `runtime_first` or `tooling_first`, owner, rationale, Common closeout receipt identity and selected-track entry claim. If the record is absent, the plan remains Common-only `partial`.

The normalization rule is exactly `runtime_first -> runtime` and `tooling_first -> tooling`; no other decision value or selected-track token is valid.

#### STEP 16/20 - Selected track implementation only

If `runtime_first`, implement Change 5~7 only. If `tooling_first`, implement Change 8 only. The unselected track remains absent from this commit. Experimental pre-gate work is never cherry-picked without reimplementation / review under this selected-track claim.

#### STEP 17/20 - Selected-track adoption checkpoint

Materialize a new exact `selected_track_adoption_subject` and reinitialize the clean wrapper context. The selected track determines the focused matrix; both paths finish with the current route and a clean post-status.

```powershell
$irisTrackOrder = Get-Content -Raw -LiteralPath (Join-Path $irisCheckpointCheckout 'Iris\_docs\refactor\repository_runtime_lightweighting\track_order_decision.json') | ConvertFrom-Json
$irisTrackNormalization = @{ runtime_first = 'runtime'; tooling_first = 'tooling' }
$irisSelectedTrack = $irisTrackNormalization[[string]$irisTrackOrder.decision]
if ($irisSelectedTrack -notin @('runtime', 'tooling')) { throw 'selected track is not sealed' }
Assert-IrisCheckoutClean 'selected-track-before'
if ($irisSelectedTrack -eq 'runtime') {
  Invoke-IrisNative 'runtime-layer3' $irisPinnedPython @('-B', '-m', 'unittest', 'discover', '-s', 'Iris/build/description/v2/tests', '-p', 'test_layer3_lazy_lookup_contract.py') $irisCheckpointCheckout 'checkout_unchanged'
  Invoke-IrisNative 'runtime-usecase' $irisPinnedPython @('-B', '-m', 'unittest', 'discover', '-s', 'Iris/build/description/v2/tests', '-p', 'test_usecase_lazy_lookup_contract.py') $irisCheckpointCheckout 'checkout_unchanged'
  Invoke-IrisNative 'runtime-browser' $irisPinnedPython @('-B', '-m', 'unittest', 'discover', '-s', 'Iris/build/description/v2/tests', '-p', 'test_iris_browser_state_selection_search_acceptance.py') $irisCheckpointCheckout 'checkout_unchanged'
}
elseif ($irisSelectedTrack -eq 'tooling') {
  Invoke-IrisNative 'tooling-inventory' $irisPinnedPython @('-B', 'Iris/validation/residual_refactor/report_inventory.py', '--v2-root', 'Iris/build/description/v2', '--build-tools-root', 'Iris/build/description/v2/tools/build', '--closure', 'Iris/_docs/round3/round3_active_core_closure.json', '--out', '<external-selected-tooling-inventory>') $irisCheckpointCheckout 'checkout_unchanged'
}
else { throw 'selected track is not sealed' }
Invoke-IrisNative 'verify-current-route-output-isolation' $irisPinnedPython @('-B', $irisCurrentRouteIsolationAudit, 'verify', '--repo', $irisCheckpointCheckout, '--taxonomy', 'Iris/_docs/round3/round3_test_taxonomy.json', '--required-validations', 'Iris/_docs/round3/current_route_required_validations.json', '--receipt', $irisCurrentRouteIsolationReceipt) $irisCheckpointCheckout 'checkout_unchanged'
Invoke-IrisNative 'selected-track-current-route' $irisPinnedPython @('-B', 'Iris/_docs/round3/round3_run_contract_tests.py', '--class', 'current', '--enforce-current-build-closure', '--out', '<external-selected-track-current-route>') $irisCheckpointCheckout 'checkout_unchanged'
Assert-IrisCheckoutClean 'selected-track-after'
```

Seal `selected_track_adoption_receipt.json`. If the remaining track is later implemented, repeat STEP 16~17 with a new subject / claim / receipt before proceeding.

#### STEP 18/20 - Final terminal successor checkout and root allocation

Commit all adopted track changes, then materialize a new exact `terminal_successor_validation_subject`; it is not any earlier focused-test checkout. Re-resolve OR-06 and initialize a new command receipt root. Allocate a full Run A profile and minimal Run B profile.

```powershell
$irisTerminalAllocator = Join-Path $irisCheckpointCheckout 'Iris\validation\clean_checkout\allocate_repository_runtime_lightweighting_roots.ps1'
$irisProtectedSubjects = @($irisPhysicalCapacityRoot, $irisCheckpointCheckout)
$irisRunA = New-IrisAttemptAllocation $irisTerminalAllocator $irisProtectedSubjects 'terminal-run-a' 'terminal-run-a' $irisCheckpointClaimId $irisCheckpointSubjectReceipt
$irisRunB = New-IrisAttemptAllocation $irisTerminalAllocator $irisProtectedSubjects 'terminal-run-b' 'terminal-run-b' $irisCheckpointClaimId $irisCheckpointSubjectReceipt
```

Run B allocates only work / result / orchestration roots. If implementation retains any unused schema axis, its allocation receipt must mark `not_used`, `not_required_for_run_b_profile`, `empty_verified` and `delete_eligible_after_closeout`; otherwise closeout fails.

#### STEP 19/20 - Terminal route, diagnostic, package and purity validation

All output and caches remain outside the terminal checkout. Individual focused tests not invoked here are marked `covered_by_current_route` in `current_route_coverage_map.json` with taxonomy and required-validation entry IDs.

```powershell
Assert-IrisCheckoutClean 'terminal-before'
Invoke-IrisNative 'verify-current-route-output-isolation' $irisPinnedPython @('-B', $irisCurrentRouteIsolationAudit, 'verify', '--repo', $irisCheckpointCheckout, '--taxonomy', 'Iris/_docs/round3/round3_test_taxonomy.json', '--required-validations', 'Iris/_docs/round3/current_route_required_validations.json', '--receipt', $irisCurrentRouteIsolationReceipt) $irisCheckpointCheckout 'checkout_unchanged'
Invoke-IrisNative 'terminal-current-route' $irisPinnedPython @('-B', 'Iris/_docs/round3/round3_run_contract_tests.py', '--class', 'current', '--enforce-current-build-closure', '--out', "$($irisRunA.roots.current_result)/current_route.json") $irisCheckpointCheckout 'checkout_unchanged'
Invoke-IrisNative 'terminal-historical-route' $irisPinnedPython @('-B', 'Iris/_docs/round3/round3_run_contract_tests.py', '--class', 'historical', '--out', "$($irisRunA.roots.historical_result)/historical_route.json") $irisCheckpointCheckout 'checkout_unchanged'
Invoke-IrisNative 'terminal-diagnostic' $irisPinnedPython @('-B', 'Iris/validation/residual_refactor/run_diagnostic_disposition.py', '--runner', 'Iris/_docs/round3/round3_run_contract_tests.py', '--raw-out', "$($irisRunA.roots.diagnostic_raw_result)/diagnostic_raw.json", '--dispositions', 'Iris/_docs/refactor/residual_refactor/diagnostic_advisory_dispositions.json', '--out', "$($irisRunA.roots.diagnostic_disposition_result)/diagnostic_disposition.json") $irisCheckpointCheckout 'checkout_unchanged'
Invoke-IrisNative 'terminal-package' $irisPowerShell @('-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', (Join-Path $irisCheckpointCheckout 'Iris\tools\package_iris.ps1'), '-OutputRoot', $irisRunA.roots.package_result, '-Clean', '-Zip', '-PackageApplicability', 'current_runtime_payload') $irisCheckpointCheckout 'checkout_unchanged'
Invoke-IrisNative 'terminal-package-contract' $irisPinnedPython @('-B', '-m', 'unittest', 'discover', '-s', 'Iris/build/description/v2/tests', '-p', 'test_package_layer3_chunks_only_contract.py') $irisCheckpointCheckout 'checkout_unchanged'
Invoke-IrisNative 'terminal-lua-syntax' $irisPowerShell @('-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', (Join-Path $irisCheckpointCheckout 'tools\check_lua_syntax.ps1')) $irisCheckpointCheckout 'checkout_unchanged'
$irisPackageZip = Join-Path $irisRunA.roots.package_result 'Iris.zip'
if (-not (Test-Path -LiteralPath $irisPackageZip -PathType Leaf)) { throw 'package ZIP missing after successful package command' }
$irisPackageZipHash = (Get-FileHash -LiteralPath $irisPackageZip -Algorithm SHA256).Hash.ToLowerInvariant()
Assert-IrisCheckoutClean 'terminal-after-routes'
```

Seal `terminal_current_route_receipt.json` separately from `pre_delete_current_route_receipt.json`. The package receipt binds `PackageApplicability=current_runtime_payload`, ZIP / manifest hashes and live/package identity.

#### STEP 20/20 - Receipt-bound Run A / Run B, compare, manual validation and closeout

Immediately before the launchers, repeat the clean pre-flight. Work / result roots remain newly allocated, existing and empty because earlier terminal commands used different axes.

```powershell
Assert-IrisCheckoutClean 'full-gate-preflight'
$irisFullGateLauncher = Join-Path $irisCheckpointCheckout 'Iris\validation\clean_checkout\invoke_receipt_bound_full_gate.ps1'
$irisCompareLauncher = Join-Path $irisCheckpointCheckout 'Iris\validation\clean_checkout\invoke_deterministic_compare.ps1'
$irisRunAOrchestrationReceipt = Join-Path $irisRunA.roots.orchestration_result 'orchestration_receipt.json'
$irisRunBOrchestrationReceipt = Join-Path $irisRunB.roots.orchestration_result 'orchestration_receipt.json'
Invoke-IrisNative 'full-gate-run-a' $irisPowerShell @('-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', $irisFullGateLauncher, '-RepositoryRoot', $irisCheckpointCheckout, '-Commit', $irisCheckpointCommit, '-ClaimId', $irisCheckpointClaimId, '-EnvironmentReceipt', $irisEnvironmentReceipt, '-WorkRoot', $irisRunA.roots.work, '-ResultRoot', $irisRunA.roots.result, '-OrchestrationReceipt', $irisRunAOrchestrationReceipt, '-StdoutPath', (Join-Path $irisRunA.roots.orchestration_result 'full-gate.stdout.bin'), '-StderrPath', (Join-Path $irisRunA.roots.orchestration_result 'full-gate.stderr.bin')) $irisCheckpointCheckout 'checkout_unchanged'
Invoke-IrisNative 'full-gate-run-b' $irisPowerShell @('-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', $irisFullGateLauncher, '-RepositoryRoot', $irisCheckpointCheckout, '-Commit', $irisCheckpointCommit, '-ClaimId', $irisCheckpointClaimId, '-EnvironmentReceipt', $irisEnvironmentReceipt, '-WorkRoot', $irisRunB.roots.work, '-ResultRoot', $irisRunB.roots.result, '-OrchestrationReceipt', $irisRunBOrchestrationReceipt, '-StdoutPath', (Join-Path $irisRunB.roots.orchestration_result 'full-gate.stdout.bin'), '-StderrPath', (Join-Path $irisRunB.roots.orchestration_result 'full-gate.stderr.bin')) $irisCheckpointCheckout 'checkout_unchanged'
Invoke-IrisNative 'full-gate-compare' $irisPowerShell @('-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', $irisCompareLauncher, '-RepositoryRoot', $irisCheckpointCheckout, '-Commit', $irisCheckpointCommit, '-ClaimId', $irisCheckpointClaimId, '-EnvironmentReceipt', $irisEnvironmentReceipt, '-RunAOrchestrationReceipt', $irisRunAOrchestrationReceipt, '-RunBOrchestrationReceipt', $irisRunBOrchestrationReceipt, '-AttemptRoot', $irisRunA.roots.compare_result) $irisCheckpointCheckout 'checkout_unchanged'
Assert-IrisCheckoutClean 'full-gate-after'
```

Every mandatory native process is launched only through `Invoke-IrisNative`; wrapper nonzero is checked immediately before control returns. The diagnostic adapter's nested raw exit may be 1 only under its advisory contract. Missing prerequisites are `blocked`; an implemented command that runs and exits nonzero is `FAIL`. Manual validation follows this automated PASS, then `final_closeout_receipt.json` binds all checkpoint receipts, command-receipt-set hashes, Run A / Run B chains and deterministic compare.

### Manual Validation

Use the same Project Zomboid build, mod set, save, locale, and machine for before / after comparisons.

* EN and KO startup: no Browser build log or `getAllItems()` scan before Browser use
* first map icon Browser open: full list appears and first-use delay is recorded
* repeated Browser open: no full rebuild in the same generation
* case-insensitive search, prefix typing, backspace, no-result, selected item persistence
* item right-click `Iris` open and Browser detail rendering
* Alt tooltip: no overlay without Alt; same tag / connection / use-case / more lines with Alt
* repeated Alt-held frames: stable height, no duplicated lines, no stale locale text
* Layer3 text presence / absence and `internal_only` suppression parity
* UseCase recipe navigation and requirement coloring parity
* compatibility checks for direct `IrisLayer3DataChunks`, `IrisUseCaseDescriptions`, and `IrisData` require paths in dev console where available
* external package install smoke test without claiming release readiness

### Validation Limits

* no multiplayer validation
* no long-session leak or multi-hour cache growth validation unless separately scheduled
* no external mod compatibility sweep beyond supported public surfaces and selected direct-require probes
* no Workshop upload or release publication
* no comparison across different PZ builds, mod sets, saves, or hardware as performance evidence
* standalone Lua timing is structural / directional evidence only
* archive media durability beyond full immediate restore / hash verification is not claimed
* positional schema migration, registry split, and compatibility deletion are not validated because they are out of scope

---

## 8. Risk Surface Touch

### Authority Surface

High.

The plan changes a current active-core guard producer and adds routing metadata adjacent to the protected runtime chunk authority. It must not modify Layer3 facts, decisions, rendered text, publish state, or semantic content. New indexes are derived routing artifacts, not new fact authority.

### Runtime Behavior Surface

High.

Browser build timing, generated data load timing, search caching, tooltip caching, and failure fallback paths change. Display and public return behavior must remain equal.

### Compatibility Surface

High.

`IrisBrowserData.build`, Browser open facades, `IrisLayer3DataChunks`, `IrisUseCaseDescriptions`, `_requirementsLookup`, `IrisLayer3Data`, `IrisData`, and copy-on-read API behavior are protected.

### Sealed Artifact Surface

High.

Current active-core closure, required validations, runtime protected-surface manifests, package identity receipts, staging evidence roles, archive receipts, and `.gitignore` durable exceptions are touched or re-attested.

### Public-Facing Output Surface

None intended.

Tooltip text, Browser rows, Wiki text, Layer3 text, interaction labels, order, counts, and navigation behavior must not change. Any public delta blocks closeout and requires separate approval.

---

## 9. Risk Analysis

### Architecture Risk

* External payloads can be mistaken for authority if receipts do not state the authority boundary.
* The existing `technical_debt_gate` policy can be mistaken for an approved production producer policy.
* Excluding generated reports from the guard scan can accidentally reduce coverage if the scan-input census is incomplete.
* `rg` and implicit `rglob` behavior can produce different denominators.
* A shared work-root helper can become a new cross-cutting dependency and violate the current active-core closure.
* Generated routing indexes can be mistaken for an alternate Layer3 authority.
* Implementing a follow-up track before Common closeout can bypass Change 1 authority and make later evidence non-normative.
* Direct-durable checkpoint receipts and promoted lifecycle evidence can be mistaken for one undifferentiated creation ceremony.

Mitigations:

* authority role and logical artifact id are mandatory in every manifest.
* production output remains blocked until the separate successor policy is owner-approved and adopted.
* old/new guard verdict and scan-surface delta are reviewed before adoption.
* scan backend is explicit, silent fallback is forbidden, and backend path-list parity is tested.
* shared helper extraction has a three-current-producer gate and exact closure update.
* indexes contain only key boundaries, module names, counts, and hashes; payload remains in existing chunks.
* the checkpoint manifest enforces bootstrap, baseline adoption, Common pre-delete, Common closeout, Track Order, selected-track adoption and terminal successor chronology; pre-order experiments are never adoption inputs.
* the §5 creation table identifies every durable file's producer step and whether it requires external-byte promotion or direct-durable schema / commit binding.

### Runtime Risk

* Lazy loading can move work from boot to a visible first interaction and create a noticeable hitch.
* Kahlua require / table iteration behavior can differ from standalone Lua.
* one bad range boundary can return missing or wrong entry data.
* a silent compatibility fallback can restore full eager loading while appearing successful.
* cache invalidation errors can show stale locale or generation results.

Mitigations:

* measure boot, first use, and warm repeat separately.
* preserve full-table public facades; do not rely on `__pairs` proxies.
* all-key parity and boundary-key tests cover every generated entry.
* injected require-spy counts and reason-coded fallback counters are bound into receipts; normal adoption requires zero fallback.
* cache keys include generation and locale; explicit reset tests are mandatory.

### Compatibility Risk

* Direct consumers may rely on full facade iteration or compatibility globals.
* Browser interaction collector currently receives the full UseCase table, including `_requirementsLookup`.
* package validators currently enumerate an exact Layer3 payload surface.

Mitigations:

* full facades remain materializing compatibility paths.
* internal collector inputs change only after API adapter parity tests.
* package / live identity validation adopts each new support file explicitly.

### Regression Risk

* historical scripts may contain hardcoded staging paths and fail after source-checkout cleanup.
* ignored giant files are not recoverable from Git once deleted.
* archive manifests can preserve hashes but miss path / consumer context.
* durable manifests can retain dangling hashes after external result cleanup.
* prefix search optimization can change ordering or miss results after backspace.
* benchmark noise can lead to false performance claims.
* a failed native command can be masked by a later successful inspection command if `$LASTEXITCODE` is not captured immediately.
* reusing one current-route receipt before and after irreversible cleanup can hide which subject was actually validated.
* Windows PowerShell 5.1 `-File` binding can collapse, split or drop argv elements while the visible command still appears plausible.
* ambient checkpoint variables can bind a valid command receipt to the prior checkpoint or wrong allocation claim.

Mitigations:

* reference graph and historical route run before deletion.
* ignored payload deletion requires verified cold archive and restore receipt.
* archive rows retain original logical path, role, producer, consumers, and content hash.
* every retained hash must resolve to an active result object, archive successor, or named durable store before cleanup.
* query equivalence tests cover extension, backspace, reset, locale, and generation.
* same-environment repeated median / p95 is reported with raw samples.
* every native command is wrapper-bound, failure aborts the checkpoint, and injected masking fixtures prove later commands remain not-run.
* Common cleanup authority and terminal successor evidence use separately named subjects and receipts.
* a scalar JSON command-spec carries argv across the external PowerShell boundary and an adversarial child-probe fixture proves exact sequence round trip.
* every checkpoint repeats the explicit identity / output reinitialization block and allocation claim is a required function argument.

### Storage and Windows Path Risk

* external work roots can collide, exceed path budgets, or resolve back into the checkout through reparse points.
* permission-denied temp paths can make byte accounting appear complete when it is not.
* cleanup of a broad or unresolved path can destroy unrelated runs.
* focused pytest, bytecode, uv cache or test output can dirty the authoritative validation checkout and invalidate purity claims.
* in-process current-route tests can write into ignored temp paths that ordinary `git status` does not report.

Mitigations:

* short checkout / round identifiers and path-budget tests
* collision-resistant allocation, pre-create existence / ledger-reuse rejection, followed by newly created existing-empty root acceptance
* resolved outside-checkout guard
* exact manifest-owned run roots only
* separate unreadable denominator and no archive / delete while unreadable rows remain
* pinned Python `-B`, pytest `-p no:cacheprovider`, external cache / environment / output roots, and wrapper-recorded clean pre/post Git status
* one audit per unique current-route closure plus per-command `checkout_unchanged` physical census covering ignored paths and unreadable entries
* no recursive operation on workspace root, home, work-root parent, glob, or unresolved environment variable

---

## 10. Rollback Plan

Common storage lifecycle rollback:

* external provisional lifecycle evidence remains retained until promoted durable bytes, promotion receipt and commit / tree binding are verified. Failed promotion removes no physical source artifact and cannot authorize Change 4.
* Until archive and restore validation pass, original source-checkout payloads remain untouched.
* Producer migration is performed one producer at a time. A failed pilot returns that producer to its prior output path while retaining the external run for diagnosis.
* Content-addressed objects are immutable; rollback changes references rather than rewriting objects.
* retained external objects are not removed until a verified archive / durable-store successor is bound; dangling references block rollback completion.
* If a cleanup has occurred, restore the exact archived manifest paths, verify all SHA-256 values, then rerun current / historical routes before reopening work.
* `.gitignore` changes are reverted only after restored paths and durable exceptions are checked.

Runtime rollback:

* Browser rollback restores the `IrisMain` eager `buildBrowserData` invoke without removing the preserved `IrisBrowserData.build()` facade.
* Layer3 rollback switches `layer3_renderer` back to the existing full `IrisLayer3DataChunks` facade. Existing 11 chunk payloads are not rewritten.
* UseCase rollback switches API / interaction consumers back to `IrisUseCaseDescriptions`; the compatibility facade remains available throughout.
* Search / tooltip cache changes are isolated and can be disabled independently without reverting data loading changes.
* Runtime rollback restores the previously attested protected-surface hashes and regenerates the external package projection.

Rollback completion requires:

* current route pass
* affected historical / diagnostic route pass
* Lua syntax pass
* public facade parity pass
* package identity pass
* manual PZ smoke test for any adopted runtime change

No rollback step uses broad workspace deletion, `git reset --hard`, or an unverified archive.

---

## 11. Governance Constraints

* `docs/Philosophy.md` remains constitutional authority.
* runtime cannot interpret source evidence, compose prose, score utility, recommend, compare, or repair facts.
* offline generation remains the only place where payload indexes and receipts are created.
* current Layer3 facts and 11 chunks remain protected until an approved adoption receipt names exact successor hashes.
* public require paths and supported API signatures remain available.
* copy-on-read and consumer-local mutation rules remain in force.
* package projection is read-only and disposable; no source writer may use it as authority.
* tracked / ignored state is evidence metadata, not authority or delete authority.
* physical capacity authority and clean validation authority are separate: only `physical_capacity_subject` authorizes byte accounting / cleanup, while only exact `validation_subject` evidence authorizes clean route / full-gate claims.
* current / historical / diagnostic denominators remain distinct.
* raw diagnostic exit and terminal disposition remain distinct; advisory raw exit 1 is never rewritten as a raw PASS.
* this plan uses a separate successor claim ID and does not replace or retroactively complete the predecessor offline-tool / residual-runtime claim.
* historical reproduction cannot be silently reduced by output cleanup.
* current active-core and allowed-tooling sets are exact. Broad imports or broad allowlists are forbidden.
* broad staging unignore and glob-based archive / delete are forbidden.
* the existing `technical_debt_gate` output policy is not production authority. Change 2 requires the separately approved production-scoped successor policy.
* authoritative full-gate evidence must originate from the exact-checkout receipt-bound launcher and deterministic compare chain; direct Python runner execution is non-authoritative.
* unreadable and unclassified denominators are separate and both block cleanup of the affected root.
* archive requires manifest, hash, restore proof, final reference check, and closure / seal.
* fixed storage caps and retention counts require a later measured policy decision.
* generated positional schema migration, registry giant split, `IrisData` removal, and compatibility removal remain Hold.
* tooltip remains Alt-gated and within the existing maximum 4-line display policy.
* public-facing text, line order, counts, publish state, and navigation behavior cannot change under a performance claim.
* manual PZ evidence is mandatory for complete Runtime Track closeout.
* package identity does not imply release or Workshop readiness.
* DECISIONS / ARCHITECTURE / ROADMAP updates occur only after validated adoption, not when this plan is merely approved.

---

## 12. Expected Closeout State

Target: `complete` for the scoped Common, Runtime, and Tooling changes, subject to the Track Order Gate and mandatory manual runtime validation.

The expected closeout is `partial` with the blocked axis named explicitly if any of the following remains true:

* track order is not selected;
* archive / restore cannot be proven;
* manual PZ validation is unavailable;
* the predecessor output-isolation base contract remains unadopted;
* `repository_runtime_lightweighting_output_policy.json` remains unapproved or unadopted;
* mandatory lifecycle producer, hash-preserving promotion tool, root allocator, archive executor or their receipt contracts are missing;
* mandatory native command wrapper or any command-level stdout / stderr / exit receipt is missing;
* a Windows PowerShell 5.1 wrapper call passes `[string[]]` directly across external `-File`, or scalar command-spec argv round-trip fixtures do not pass;
* bootstrap, baseline adoption, Common pre-delete, Common closeout, selected-track adoption or terminal successor checkpoint is absent or reuses another checkpoint subject;
* any checkpoint reuses prior checkout / commit / claim / subject receipt / command receipt root / environment delta / command index, or a physical allocation inherits the bootstrap validation claim;
* `physical_capacity_subject` is not exact, ignored giant rows are absent from its denominator, or it is conflated with `validation_subject`;
* external baseline bytes have not been promoted to the Git-visible durable sink with matching SHA-256 and commit / tree binding;
* receipt-bound Run A / Run B, their allocation / orchestration receipts or deterministic compare receipt are absent;
* terminal checkout pre/post status is not clean, pytest cache is enabled, or Python / uv / test output can write inside a validation checkout;
* exact current-route selected closure lacks a matching static + dynamic output-isolation audit receipt, or `checkout_unchanged` reports tracked / untracked / ignored delta or unreadable entries;
* `pre_delete_current_route_receipt.json` or separately named `terminal_current_route_receipt.json` is absent;
* Change 5~8 adopted implementation appears before `track_order_decision.json`;
* Track Order normalization is anything other than `runtime_first -> runtime` or `tooling_first -> tooling`;
* only the first selected track is adopted and the deferred track has not subsequently closed through its own adoption checkpoint, while the target is claimed as full Common + Runtime + Tooling `complete`;
* diagnostic adapter external-output / raw-disposition parity is not current-route protected;
* diagnostic external-output is still `planned_change_not_adopted`;
* `rg` / explicit Python scan denominator parity is unproven;
* an affected cleanup root has nonzero unreadable or unclassified rows.

Complete closeout requires all of the following:

* baseline inventory names `physical_capacity_subject`, records the physical resolved root / working state, includes the ignored giant four, and accounts for all scoped physical bytes.
* mandatory artifact lifecycle producer and promotion tool exist; their focused tests pass; external manifest / summary SHA-256 equals the promoted Git-visible bytes; and `baseline_promotion_receipt.json` is bound to the exact commit / tree.
* the §5 durable creation table accounts for all 23 Git-visible files: the 10 external lifecycle rows have hash-preserving promotion evidence, and the 13 checkpoint / contract rows prove direct durable-path creation after post-purity assertion plus reviewed commit. Any exception caused by external construction is promoted before consumption.
* `validation_checkpoint_manifest.json` contains distinct bootstrap, baseline-adoption, Common pre-delete, Common closeout, selected-track and terminal successor subjects, each bound to exact commit / tree / claim / receipt. No validation subject substitutes for physical byte accounting.
* every scoped artifact is classified; `unclassified_count = 0` and `unreadable_count = 0` for any cleaned root.
* predecessor base output contract and production-scoped successor policy are separately identified, approved, and adopted without scope conflation.
* new large producer outputs are created only outside the source checkout.
* every attempt uses collision-resistant, ledger-checked outside-checkout paths; allocator-created work / result roots exist and are empty at launcher entry; non-empty and previous-attempt reuse fixtures fail; all resolved axis roots and allocation receipts are recorded.
* every mandatory native command has a fail-loud wrapper receipt with scalar command-spec path / hash, executable, decoded ordered argv, cwd, timestamps, exit, stdout / stderr hashes, environment and subject identity; Windows PowerShell 5.1 adversarial argv round-trip and failure-masking negative fixtures pass, and all later commands after failure are `not_run_due_to_prior_failure`.
* OR-06 resolves the immutable environment receipt and pinned interpreter; exact path / SHA-256 checks pass. Pytest uses `-p no:cacheprovider`, Python bytecode / uv cache / uv environment / test output are external, and each clean checkpoint has empty pre/post Git status with raw status hash and exact dirty-entry arrays recorded.
* each checkpoint reinitializes its six identity / output variables, OR-06 binding, wrapper path and command index before use; allocation receipts bind the explicit physical or checkpoint claim passed to the allocator.
* every unique current-route closure has a matching full selected-ID / source / write-site audit from a separate exact checkout, and each authoritative route command's `checkout_unchanged` census proves zero tracked, untracked and ignored path delta with zero unreadable entries.
* the guard pilot writes one canonical occurrence payload and small phase references.
* `rg` and explicit Python backends produce byte-identical canonical path lists; unavailable / timeout behavior is fail-loud and every receipt names backend, census hash, and denominator count.
* two consecutive guard runs use separate roots, have stable input census, and do not grow by scanning prior generated reports.
* ignored giant cleanup is executed only by the named lifecycle executor and is recoverable through the ordered dry-run / archive / verify / restore / durable-promotion / delete / post-census receipt chain bound to the exact physical subject.
* cleanup prerequisite binds an authoritative `pre_delete_current_route_receipt` whose scope is Common code / tracked contract, while physical receipts separately prove ignored artifact identity and deletion. `terminal_current_route_receipt` proves the final post-delete successor state.
* cold archive root is `archived`, names retention owner / durable successor / object reference count, is excluded from ordinary attempt cleanup and has `delete_eligible=false`.
* every durable hash reference resolves to an active object, approved archive successor, or named durable store; dangling-reference count is 0.
* no current authority, current-required evidence, historical reproduction input, or protected runtime file is lost.
* `.gitignore` pre/post path-set proof shows unapproved newly tracked 0 and unexpectedly untracked protected 0.
* Common closeout precedes a durable Track Order decision; only the selected track is implemented first, and any second track uses another adoption checkpoint.
* both Runtime and Tooling tracks close through distinct adoption checkpoints before the full Common + Runtime + Tooling target is called `complete`; a valid first-track-only result remains `partial`.
* `OnGameBoot` performs zero Browser `getAllItems()` scans.
* first Browser open builds once and warm re-open reuses the generation cache.
* single Layer3 lookup loads at most one Layer3 data chunk.
* Alt tooltip line count loads zero UseCase description chunks.
* single UseCase detail lookup loads at most one UseCase description chunk.
* injected require-spy and PZ diagnostic evidence agree on loaded module counts; normal runtime adoption has `fallback_count = 0`.
* direct public facades still materialize complete datasets with existing compatibility globals / fields.
* all-key data parity, search result parity, tooltip line parity, package identity, and deterministic generation pass.
* current and historical routes, diagnostic adapter, Lua syntax, focused tests, and `current_runtime_payload` package `-Clean -Zip` command exit 0.
* exact-checkout `invoke_receipt_bound_full_gate.ps1` Run A / Run B and `invoke_deterministic_compare.ps1` exit 0; both orchestration chains and the compare receipt are terminal-bound; no direct Python full-gate invocation is admitted as PASS evidence.
* Run B uses the minimal `terminal-run-b` allocation profile; any residual unused axis has the required `not_used` / `empty_verified` disposition.
* diagnostic raw exit is 0 or approved advisory 1, adapter reports `blocking=false`, and raw result / disposition identities match.
* `Iris.zip`, package manifest, and live/package support-file identities are receipt-bound.
* adopted lifecycle, work-root, diagnostic, Browser and lazy-load focused test IDs are present in the current taxonomy / required-validation result.
* every indirectly executed test has `covered_by_current_route`, taxonomy entry ID and required-validation entry ID in the coverage map.
* EN / KO Project Zomboid manual checks pass for Browser, tooltip, Wiki, Layer3, and interactions.
* final receipt separately reports physical tracked / ignored / untracked bytes, validation checkout bytes, work scratch peak bytes, retained result bytes, archive bytes, boot time, first-use time, warm time and loaded chunk counts without inventing an unapproved capacity target.
* closeout explicitly states that positional schema migration, registry split, compatibility removal, release readiness, multiplayer, and long-session stability remain unclaimed.
