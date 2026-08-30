# Iris current responsibility naming — execution record

Date: 2026-08-30. Final state: **complete — naming and file placement only**.
Authority: `iris_current_responsibility_naming_alignment_plan.md`; owner decisions and
protected naming changes preapproved by the execution prompt. No independent review
or extra seal is required for this scope; none is credited.


## 책임별 재명명 정정

사용자의 정정: 폴더를 작업명으로 분류하는 것이 아니라, 각 코드가 무엇을
입력받고 무엇을 처리·출력하는지 파악해 파일 자체의 이름을 바꾸는 작업이다.
이전 N1–N7 반영만으로 요청 전체가 완료되었다고 한 판단을 정정한다.

지목된 여섯 폴더의 실행 파일·테스트·현재 설정/경로 파일 85개를 실제로
재명명 또는 재배치했다. 아래 표는 구현된 파일의 역할이며 새 검사 목록이 아니다.
경로는 `Iris/validation/` 기준이다. 기능·판정·검사 대상·공개 schema/CLI 식별자는
유지했고, Python import·동적 파일 로딩·PowerShell 호출·테스트 fixture·현재 설정의
경로를 함께 갱신했다. 기존 테스트는 이동/참조 수정만 했으며 실행하지 않았다.

| 이전 파일 | 새 파일 | 코드가 하는 일 |
|---|---|---|
| `run_iris_clean_checkout_validation.py` | `execution/run_repository_tests.py` | 지정 Git 버전의 테스트·의존성을 모으고 격리 checkout에서 선정된 테스트 실행 |
| `validate_iris_clean_checkout_validation.py` | `execution/validate_environment_and_results.py` | 실행 환경, 반복 실행 결과, 보존 기록의 연결 확인 |
| `iris_clean_checkout_validation_common.py` | `execution/checkout_environment.py` | 저장소·인터프리터·설치 패키지·외부 출력 경로의 식별과 계약 처리 |
| `write_environment_receipt.py` | `execution/record_environment.py` | 실제 인터프리터와 설치 wheel을 원본 코드 버전에 연결해 기록 |
| `pytest_result_plugin.py` | `execution/pytest_outcome_recorder.py` | pytest가 수집한 테스트와 실행 결과 기록 |
| `invoke_receipt_bound_full_gate.ps1` | `execution/invoke_repository_tests.ps1` | 환경을 적용·복구하고 저장소 테스트 실행기를 호출 |
| `invoke_deterministic_compare.ps1` | `execution/compare_repeated_test_runs.ps1` | 두 실행의 기록을 읽어 동일한 조건·결과인지 비교 |
| `allocate_repository_runtime_lightweighting_roots.ps1` | `execution/allocate_external_workspaces.ps1` | 저장소와 겹치지 않고 재사용되지 않는 외부 실행 경로 할당 |
| `invoke_repository_runtime_lightweighting_command.ps1` | `execution/invoke_isolated_command.ps1` | 명령 명세에 따라 환경·출력 경계를 제한하고 명령 실행 |
| `audit_current_route_output_isolation.py` | `execution/audit_test_output_isolation.py` | 선택된 코드의 쓰기 위치와 실행 기록에서 저장소 내부 출력 여부 확인 |
| `run_contract_tests.py` | `execution/run_required_contract_tests.py` | 현재 필수 테스트 ID를 선정하고 계약 테스트 실행 |
| `run_python_import_matrix.py` | `execution/check_build_tool_imports_and_io.py` | 빌드 도구 import 방식·CLI·직렬화 바이트·긴 경로 사례 실행 |
| `run_diagnostic_disposition.py` | `execution/run_diagnostic_with_dispositions.py` | 진단 명령 결과에 명시된 owner 판정을 적용; 폐기된 selector는 복원하지 않음 |
| `write_manual_runtime_report.py` | `execution/record_unobserved_runtime_cases.py` | 운영자 명령 결과를 기록하고 관찰하지 않은 게임 사례는 blocked로 표시 |
| `inventory_iris_offline_tooling.py` | `source_analysis/inventory_offline_tooling_at_commit.py` | 지정 Git 버전의 오프라인 도구 구조·보존 대상 조사 |
| `report_inventory.py` | `source_analysis/inventory_build_tool_dependencies.py` | 빌드 도구의 호출자·import·subprocess·공유 입출력 함수 조사 |
| `repository_evidence_codec.py` | `artifacts/lifecycle_delta_codec.py` | 파일 목록의 공통 행과 변경분을 저장하고 원래 목록 바이트로 복원 |
| `migrate_repository_evidence.py` | `artifacts/migrate_evidence_storage.py` | 기록을 변경분 표현·내용 해시 저장소·압축 파일 사이에서 변환 |
| `execute_artifact_lifecycle.py` | `artifacts/archive_and_prune_artifacts.py` | 기존 승인·기록 조건에 따라 산출물을 보관·복원하고 삭제 가능 항목 처리 |
| `promote_artifact_lifecycle_evidence.py` | `artifacts/promote_lifecycle_evidence.py` | 외부 lifecycle 기록을 저장소의 보존 위치로 옮기고 중단된 교체 복구 |
| `report_artifact_lifecycle.py` | `artifacts/inventory_artifact_lifecycle.py` | 산출물 역할·소비 관계·추적 상태·보존/삭제 분류 조사 |
| `content_addressed_archive.py` | `artifacts/content_addressed_archive.py` | 내용 해시 기반 ZIP 생성·무결성 확인·복원; 이미 역할에 맞는 파일명 유지 |
| `write_evidence_manifest.py` | `artifacts/write_evidence_role_manifest.py` | 기록의 역할·생산 명령·입출력 해시 작성 |
| `write_evidence_index.py` | `artifacts/index_evidence_role_manifests.py` | 위 역할 기록들의 탐색용 색인 작성 |
| `validate_evidence_roles.py` | `artifacts/validate_evidence_role_manifests.py` | 역할 기록의 항목·경로·해시 확인 |
| `run_iris_baseline_admission.py` | `baseline/collect_baseline_qualification.py` | 이전 실패 자료와 기준점 채택 조건의 실행 결과 수집 |
| `validate_iris_baseline_admission.py` | `baseline/validate_baseline_qualification.py` | 기준점 채택 자료와 부정 사례 검사; 권한 쓰기 수행하지 않음 |
| `iris_baseline_admission_common.py` | `baseline/qualification_contracts.py` | 기준점 채택의 경로 제한·선행 조건·실패 코드 처리 |
| `invoke_iris_baseline_admission.ps1` | `baseline/invoke_baseline_qualification.ps1` | 기준점 자료 수집 명령을 PowerShell에서 호출 |
| `test_workflow_consolidation/_common.py` | `scenarios/scenario_evidence.py` | 시나리오 기록의 직렬화·저장소·환경·명령 식별 |
| `scenario_contracts.py` | `scenarios/scenario_report.py` | 변경 불가능한 시나리오 입력·실행 결과·개별 검사 결과 모델 |
| `validate_scenario_report.py` | `scenarios/validate_scenario_report.py` | 시나리오 식별·검사 간 의존 관계·최종 상태 일관성 확인 |
| `test_lightweighting/_common.py` | `test_coverage/source_metrics_io.py` | 테스트 소스/JSON 읽기와 함수 길이 계산 |
| `collect_test_inventory.py` | `test_coverage/inventory_test_sources_and_size.py` | 테스트 ID·파일·함수 크기 목록 작성 |
| `build_protection_map.py` | `test_coverage/infer_test_protection_map.py` | 테스트 **이름에서** 검사 조건을 추론; 실행 coverage 측정기가 아님 |
| `build_detection_baseline.py` | `test_coverage/build_fault_detection_baseline.py` | 선언된 결함과 검출 테스트의 대응을 기준 기록으로 결속 |
| `compare_precision.py` | `test_coverage/compare_test_coverage_and_size.py` | 변경 전후 선언된 보호 조건과 테스트 코드 크기 비교 |
| `compare_failure_localization.py` | `test_coverage/compare_fault_localization.py` | 결함을 찾아낼 테스트 대응이 사라졌거나 비었는지 비교 |
| `validate_dominance.py` | `test_coverage/validate_test_replacement_coverage.py` | 대체 테스트가 기존 테스트의 선언된 보호 조건을 포함하는지 확인 |
| `validate_identity_migration.py` | `test_coverage/validate_test_id_migration.py` | 테스트 ID 교체와 taxonomy/필수 목록 연결 확인 |
| `validate_terminal_evidence_bundle.py` | `test_coverage/verify_archived_closeout_bundle.py` | 보관된 종료 기록을 가져와 원본 버전과 해시 연결 확인 |

현재 실행 설정은 `execution/contracts/`, 기준점 채택 설정은
`baseline/contracts/`로 옮겼다. 작업명이 붙었던 출력 규칙은 실제 책임에 따라
`isolated_command_output_policy.json`, `evidence_storage_output_policy.json`,
`test_execution_output_policy.json`으로 바꿨다. 실행 대상 규칙은
`repository_test_gate.json`, `scoped_test_gate.json`이다. 기존 schema 식별자와
규칙 내용은 유지하며 파일명 변경에 따른 경로만 조정했다.

현재 필수 목록과 환경 안내 파일은 `execution/required_validations.json`,
`execution/current_environment.json`이다. `clean_checkout/authority`,
`clean_checkout/evidence`, `baseline_admission/authority`, `baseline_admission/evidence`의
과거 기록·해시·내용은 보존했다. 이 정정에서는 외부 파일 조회, 테스트, 빌드,
인게임 확인, 새 receipt/manifest/seal 생성, reviewer 호출을 하지 않았다.
이번 정정의 게임 기능 코드 변경은 없으며 별도 진행 중인 Tooltip 변경은 보존한다.

사용자 요청에 따라 현재 구조에서 불필요하다고 판단한 실행 파일만 별도로 추렸다.
삭제는 수행하지 않았다. 아래 세 파일의 이전/현재 이름을 사용하는 호출은 현재
실행 코드·CLI·필수 목록에서 확인되지 않았으며, 단순 미사용 여부 외에 본문의
구체적인 불일치도 확인했다.

| 현재 파일 | 현재 구조에서 불필요한 이유 |
|---|---|
| `execution/run_diagnostic_with_dispositions.py` | 호출 명령에 `--class diagnostic`을 고정하지만 현재 계약 실행기는 `current`만 허용한다. 폐기된 진단 경로를 전제로 한 후처리 도구다. |
| `execution/check_build_tool_imports_and_io.py` | `tools.build.compose_layer3_io` 등 옛 description-tree import를 고정해 실행한다. 해당 위치의 파일은 없으며 현재 구현은 설치 패키지의 `iris_tooling.build.compose_layer3_io`에 있다. 현재 구조의 유효한 검사로 쓸 수 없는 과거 이동 작업용 도구다. |
| `execution/record_unobserved_runtime_cases.py` | 게임을 실행·관찰하지 않고 모든 게임 사례를 `not executed`/`blocked`로 채운다. 과거 무인 작업 당시 보고서를 만들던 도구이며 현재 기능이나 실제 게임 검증을 제공하지 않는다. |

보관/복원 codec, 현재 계약, 과거 기록 자체는 위 불필요 파일에 포함하지 않는다.
오래된 이름이나 단독 실행이라는 이유만으로 보존 가치까지 없다고 판단하지 않는다.

## Final user-directed scope (이전 실행 기록)

The user explicitly ended validation and restricted the work to renaming and
corresponding file placement/reference updates. Under that final scope, N1–N7
are complete. N7's current locator and the immutable record already emitted by
the existing environment writer were copied from the task checkout into the
selected repository. Historical environment records and the old locator remain
intact. No additional tests, generation, packaging or in-game checks were run.

Earlier `partial`, `blocked`, pending validation and next-action sections below
are historical execution notes under the broader plan; they are no longer
completion conditions for the user's narrowed request. Existing mixed/lifecycle
and historical retain/defer decisions remain. This is not a claim that every
stage-named path in the repository was renamed.

The prior follow-up created a wheel, an external Python environment and its
existing-workflow receipt under `C:/Users/MW/PZ-N`. It did not execute canonical
full A/B/comparison or produce a new package. No further external input search
or recovery is required. Completion here does not claim production regeneration,
full-gate PASS, runtime certification, publication or deployment. The user subsequently
requested local main integration and a Git commit. The naming changes and preserved
Tooltip baseline are included; the unrelated DVF documentation folder is excluded.
The prior implementation snapshot is retained in ancestry. No remote push is requested.

## Scope and baseline

Base HEAD: `cc095398a273685f0e1c1216447d99927fe99316`. The existing Alt side-panel
layout and harness changes are the preserved working-tree baseline, not naming
changes. Existing additions in ARCHITECTURE, DECISIONS, ROADMAP and the T3 plan
are preserved. The unrelated `docs/dvf_b41_full_item_first_pass_2026-08-30/`
is excluded. No other module or external user directory is an input.

Baseline SHA-256:

| Asset | SHA-256 |
|---|---|
| Static Lua payload | `d9c88a437c60b49a631e214b577ab8e78a087435101e69d76c8b86e0c65aa10a` |
| Lookup | `e172d23d0c8ad7513fd97ac0a2e627f61d464fa13a54001e142848d4be17a22a` |
| Dirty Alt source | `63473fd5057d049b15c4db1040e17cc6a2948fe68609992e8f32eaa200bd3559` |
| Dirty runtime harness | `03edc33843454499040ffb7d32454ace94188fb626bf869445674bc0d3be1db3` |
| Required manifest | `ddd64d67d8f3132016ea418fbd751b3d921ff524622ce02118fa929d64f48e40` |

Read-only selection baseline is the exact sorted union of current/ok taxonomy IDs
and required IDs, excluding declared historical optional IDs: **103 identities**.
No baseline suite, generation or package was executed. No test source/node is renamed.
The source media tree and package selection rules are the package baseline;
older external packages are not assumed to contain the user's latest layout.

Scope scan: tracked filenames plus relevant source references under `Iris/media`,
`tooling`, `build`, `test`, `validation`, and individual live `_docs` readpoints;
root pytest discovery, package and syntax consumers; the four authority documents.
Historical `_docs/round3` and `_docs/refactor` records are classified by their
actual live reader, not by their containing directory. Ignored Iris inputs at
start: 154 Python bytecode files, 544 tooling-venv files and five tooling uv-cache
files. They are execution caches, not canonical source. Other temporary checkout
copies, `.git` internals, raw capsule objects and unrelated documents are not a
new source census. Capsule logical membership is read from its existing manifest.

## Scope lock and exact map

O1: dependency-driven C1/C3 preparation together; neither is adopted as a validated
successor before its required outcomes. O2: small module convention in `Iris/AGENTS.md`;
command ownership remains in ENTRYPOINTS. O3: no claim of solving all stage names.
The residual/current test families below are explicitly retained scope exceptions;
the user's preapproval covers this bounded disposition, not evidence of success.

All paths below are repository-relative. N3 maps each of `__init__.py`, `cli.py`,
`contract.py`, `projection.py`, `serialization.py` one-to-one within the directories.

| ID | Old path | Successor | Responsibility / consumers / binding |
|---|---|---|---|
| N1 | `Iris/media/lua/client/Iris/Data/IrisTooltipT2Lookup.lua` | `Iris/media/lua/client/Iris/Data/IrisTooltipStaticDataLookup.lua` | Internal first-use lookup; Alt and Lua harness require. No supported API entry promises the old require path; no external-consumer absence claim or new alias. V5/V6/V8. |
| N2 | `Iris/media/lua/client/Iris/Data/IrisTooltipT2Data.lua` | `Iris/media/lua/client/Iris/Data/IrisTooltipStaticData.lua` | Generated KO/EN arrays; serializer LUA_NAME, lookup, wrapper hash and recursive package projection. Raw payload is unchanged; production fresh generation still required. V3/V5/V7/V8. |
| N3 | `Iris/tooling/src/iris_tooling/domains/tooltip_t2/` | `Iris/tooling/src/iris_tooling/domains/tooltip_static_data_projection/` | Internal installed projection implementation; CLI dispatch and three dedicated tests. Both directory and qualified module change; CLI `tooltip-t2` stays supported. New wheel/environment binding required. V2/V3/V7/V9. |
| N4 | `Iris/test/lua/tooltip_t3_runtime_harness.lua` | `Iris/test/lua/tooltip_static_data_runtime_harness.lua` | Full runtime contract harness; Python subprocess path and menu_subject binding list. Existing dirty assertions, `next=nil`, marker and timeout retained. V6. |
| N5 | `Iris/_docs/round3/round3_run_contract_tests.py` | `Iris/validation/current_route/run_contract_tests.py` | Directory reclassification to validation; same parents[3] root, TEST_ROOT, current-only argparse and suite-lifetime projection. Audit, launcher-dependent readers and fixture runner paths move together. V4/V9. |
| N6 | `Iris/_docs/round3/current_route_required_validations.json` | `Iris/validation/current_route/required_validations.json` | Byte-preserving current binding projection. Original remains historical for pinned lifecycle readers. Current package, exporter, public-text consumer, audit, full A/B launchers and navigation read the successor. V1/V4/V8/V9. |
| Schema | `Iris/_docs/authority/tooltip_t2/tooltip_t2_projection_manifest.schema.json` | `Iris/_docs/authority/tooltip_static_data_projection/projection_manifest.schema.json` | Additive schema with new `$id` and only the Lua filename constraint changed; original preserved. Manifest schema_version/generator version and all other constraints unchanged. V3/V7. |

No semantic owner is transferred. N2 is currently a source payload move, **not**
an admitted production regeneration. N6 original is not a second current writer.
There is no global replacement of T1/T2, schema versions, content hashes or FullType.

## Retained / deferred ledger

| Paths / logical family | Disposition and reader |
|---|---|
| `tooltip_t1/{contract,models,projection,audit,cli}.py`, tests/fixtures and protected policy/authority | Mixed lifecycle/readiness and supporting contracts; keep original T1 identity. N3 imports its contract/model helpers. `admit()` still uses original CONTRACT_FILES against the historical T1 Git commit. No new handoff or weakened admission. |
| `tooltip_t1/d2.py`, `d5.py`, `d3_invariance.py`, `d4_invariance.py`; Layer3/4 `tooltip_t1_d3.py` / `tooltip_t1_d4.py` | Mixed or lifecycle-specific; defer extraction. d2 combines load_relation/HARNESS/PROJECTION_BUILDER with fixed-parent materialize/finalize; d5 combines exact identity/disposition helpers with fixed predecessor census/reconcile. Good whole-file functional name not established. |
| T2 dedicated `test_tooltip_t2_{projection,serialization,cli}.py`, `tooltip-t2`, JSON filenames and schema_version | Retained dedicated protocol/lifecycle identities; imports move, assertions/applicability do not. Not promoted to regular membership. |
| `_docs/round3/{round3_test_taxonomy,round3_active_core_closure,round3_pytest_source_classification,round3_full_discovery_denominator}.json` | Mixed historical records/live supporting projections; unchanged exact paths. Runner uses historical companions explicitly; pytest policy and full gate retain their existing reader. No directory-wide move. |
| `test_round3_*.py`, `runtime_payload_residual_seal_test_support.py`, `test_iris_residual_runtime_acceptance.py`, `Iris/test/*refactor*`, `validation/residual_refactor/**` | Current contracts coexist with lifecycle/evidence helpers. Only affected current references change. Pure recurring filenames in this group are bounded O3 scope exceptions, not solved naming targets. Structural/test-identity migration remains follow-up. |
| `validation/test_lightweighting/**`, `test_workflow_consolidation/**`, old build `*round*/*phase*/*migration*/*seal*/*refactor*` procedures | Historical/lifecycle investigation and fixtures retained; no restoration of executable historical selectors. Active package implementations are separate. These old procedures are not renamed or newly adopted. |
| N7 `responsibility_refactor_environment_current.json` and its immutable target | **Deferred/blocked**: only the existing environment receipt workflow may switch the locator; that requires a fresh external environment. No hand-written successor, source binding, or inherited PASS. |
| `_docs/refactor/core_refactor/phase0_supported_api_manifest.json` | Historical supported-API baseline with live acceptance reader; kept intact. IrisData, Browser, Wiki and legacy TooltipSummary remain supported as before. |
| Current capsule manifest/objects, historical archive/removal authorities, G5 chain | Retain original paths/bytes. None of N1–N6 is a capsule logical member. The 21 G5 compiler source paths do not intersect modified tooling files. No compiler identity successor required. |
| `v1/v2`, Layer 2/3/4, PhaseInput/Output/Runner, runtime session, `finalize` | Domain/version/execution semantics, not cosmetic stage names. |

## Dynamic resolution and documentation

This is task-local inventory, not a registry or a validator. Actual execution
results are shared across the applicable rows; no independent inventory gate exists.

| Origin / mechanism | Target set and disposition | Evidence |
|---|---|---|
| Lookup protected require; Alt require | Exactly successor Data/Lookup; C1 | V5/V6; V8 pending |
| Static harness DATA/READER, dofile, package.loaded/preload; browser/residual/metrics harness loaders | New static module names and repository media tree; C1 | V6; other full-gate harness consumers V9 pending |
| Browser Python wrapper PAYLOAD, subprocess and menu_subject | Successor payload hash and N4 path; Menu pointer-selected generation unchanged | V6; optional external Menu replay not run |
| CLI lazy import; five N3 relative imports; hatch package glob | `iris_tooling.domains.tooltip_static_data_projection.*`; C1 | V3; exact installed wheel V2 pending |
| T2 fixture Path.parents[3], temporary Git repo and schema copy | Original T1 contracts plus additive schema, fixture-only sibling output roots | V3 |
| N3 admit git show of T1 CONTRACT_FILES | Historical subject/path binding unchanged; C2 retained | V3 negative/admission cases; production input V7 pending |
| Runner parents[3], TEST_ROOT, importlib, unittest.loadTestsFromName | Same repository/test root and 103 identity set; C3 | V4 listing; actual full resolution V9 pending |
| Runner suite-lifetime IRIS_ROUND3_REQUIRED_VALIDATIONS_PROJECTION | Existing environment protocol retained; current successor manifest | V9 pending; no alias/protocol rewrite |
| Applicability/Git tests spec_from_file_location | New runner path; synthetic module labels retained | V9 pending |
| Audit AST walker, fixture copy/subprocess and launcher identity bindings | New runner and required manifest; taxonomy fixed; no path-check relaxation | V9 pending |
| Exporter / public-text / package defaults and fixture path composition | Successor required manifest; historical one-off readers keep baseline | V8/V9 pending |
| Package recursive media copy plus pointer-selected Layer3 generation | Baseline exact media members with N1/N2 substitution; one future package/install pair | V8 blocked |
| Environment writer/reader; capsule/archive lookup | N7 locator unchanged; historical logical paths unmodified | Deferred; V9 blocked |
| Root pytest / v2 conftest discovery | No test filename/node/class change; taxonomy/source policy unchanged | V9 blocked; no collected-count claim |

DECISIONS receives an additive current source readpoint; existing sealed entries,
hashes and statuses remain untouched. ARCHITECTURE updates the current runtime
chain and adds the current tooling/navigation mapping without rewriting dated
T1/T2 snapshots. ROADMAP adds the actual naming implementation/validation state;
earlier T3 completion remains about its old subject. ENTRYPOINTS changes current
paths and removes already-retired historical/diagnostic command examples.
The T3 plan itself is retained unchanged. These are Change 5 updates, not new
decision or validation authorities.

## Validation and ceiling

Final local execution results (all run after implementation, no intermediate suite):

| Evidence | Exact command / result |
|---|---|
| V3 dedicated projection route | `uv run --project .\Iris\tooling python -B -m pytest .\Iris\tooling\tests\test_tooltip_t2_projection.py .\Iris\tooling\tests\test_tooltip_t2_serialization.py .\Iris\tooling\tests\test_tooltip_t2_cli.py -q --basetemp=.tmp/n/t` — exit **0**, **18 passed**, 18.39 seconds. Existing editable environment, not a fresh installed-wheel PASS. |
| V4 listing | `uv run python .\Iris\validation\current_route\run_contract_tests.py --class current --list` — exit **0**; exact 103-ID baseline match, missing/extra **0**. Listing is not test execution. |
| V4 retired selectors | Same listing command with `--class historical`, `--class diagnostic`, `--class all`: each exit **2**, argparse `invalid choice`; expected rejection, not a gate PASS. |
| V5 syntax | `powershell -ExecutionPolicy Bypass -File .\tools\check_lua_syntax.ps1` — exit **0**, **153 files**. Only repository `Iris/media/lua` existed; the default build/package root was absent. No external/install syntax claim. |
| V6 existing fallback | `uv run python .\Iris\build\description\v2\tests\test_iris_browser_state_selection_search_acceptance.py full` — exit **0**, `IRIS_TOOLTIP_T3_PASS mode=full exact_keys=2280 legacy_calls=0`. Menu source counts KO/EN 2084, L4 415. One fallback invocation because V9 cannot run; no extra smoke/replacement or external Menu replay. |
| V1 content/document comparison | Original payload SHA unchanged; lookup, dirty Alt and dirty harness exactly equal their pre-move text after only the declared module substitutions. Original and successor required manifest equal; the T3 plan unchanged. Existing DECISIONS/ROADMAP are exact preserved prefixes. No semantic equality inferred from mere counts. |
| Diff hygiene | `git -c core.safecrlf=false diff --check` — exit **0** after fixing one CRLF trailing-whitespace finding on the changed PAYLOAD declaration. This EOL-only fix followed V6; harness/runtime bytes and Python execution semantics did not change. No confidence rerun. |

UV cache, Python temporary roots and pytest fixtures were restricted to short
repository-local `.tmp/n` paths; sync/download/config discovery were disabled.
The running dedicated route was polled and completed normally; no long-running
process was left behind. Scratch code and outputs have no validator/authority status.
The final guarded PowerShell removal of `.tmp/n` was rejected by tool policy
before execution. It was not retried through another mechanism: this ignored
scratch directory remains, including the one-off editing script and baseline copies.
No new test function/file, validation framework, seal, receipt, manifest authority
or proof package was introduced; the schema is the plan-required filename contract.

V10 remains **partial**: listing and C1's exercised dynamic paths have evidence,
but installed producer, output-isolation/full-gate and package consumers have no
successor execution evidence. The retained denominator's
`exact_authority_reanchored.required_validations` is historical reanchoring metadata;
pytest enforcement reads its `enforcement` section, not that old locator.
Retired build procedures retaining old command literals are not current execution
dependencies, and this change does not make their replay supported.

Repository-external input/output
paths are not expressly authorized by this execution boundary. Consequently V2,
production V7, V8 and canonical V9 cannot be run by inventing sibling workspaces
or by weakening their external-root requirements. No external handoff, wheel,
environment, package, live game or save has been read or modified.

No fresh package means there is no exact package for the required KO/EN PZ smoke.
Existing T3 observations and receipts are not successor evidence. Final naming
adoption, canonical A/B/comparator and complete behavior preservation remain
unvalidated. No release, RTC, Publish, Workshop, deployment, architecture-redesign,
all-names-resolved, independent-review or sealed-closeout claim is made.

Ceiling: **validated** = the local commands and exact source comparisons above;
**unvalidated_but_in_scope** = V2, production V7/finalizer, V8 package/install,
V9 exact tracked A/B/comparator, remaining V10 consumers, N7 workflow and bounded
KO/EN PZ smoke; **out_of_scope** = mixed-file extraction, historical replay,
other modules, all-item/external-mod/performance QA and release/publication.
The source remains an uncommitted working-tree preparation, not an adopted
exact terminal subject. Owner preapproval was used for implementation/disposition;
it did not waive the external execution boundary or synthesize machine evidence.

Next required action is a concretely authorized external execution input/output
scope, followed by the existing fresh-wheel/environment, production A/B/finalizer,
package/install and canonical A/B/comparator workflows. N2's byte-preserved source
must still be regenerated directly under its successor name. Use the one resulting
package for the bounded PZ observation. No extra review/seal or validation-of-validation
gate is needed to resume.
