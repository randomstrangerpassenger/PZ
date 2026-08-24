# Implementation Plan

## 1. Objective

Iris의 current regular validation boundary를 현재의 pytest `234`개와 standalone `4`개, 합계 `238`개 starting execution unit에서 출발해 전수 분석하고, 보호해야 할 product/validation-system contract와 failure semantics는 유지하면서 실제로 독립 실행할 필요가 없는 preparation, producer, traversal, assertion, wrapper 및 중복 authority를 병합·제거한다.

완료 상태는 단순 inventory나 recommendation이 아니라 다음을 모두 포함한 구현 결과다.

- 모든 starting execution unit의 predecessor contract가 final successor execution/check 또는 구체적인 독립 유지 사유에 연결된다.
- predecessor taxonomy 123개 entry와 required-manifest 70개 obligation도 execution unit과 별개의 row universe로 전수 closure된다.
- 공유 가능한 immutable preparation과 lifecycle intermediate result가 실제로 한 번만 생성된다.
- 병합으로 불필요해진 pytest identity, standalone wrapper, helper, fixture, generator, staging logic 및 registration이 물리적으로 제거된다.
- taxonomy, required-validation manifest, runner, full gate, comparator 및 source policy가 final execution graph와 일치한다.
- exact terminal tracked subject의 clean-checkout Run A/B와 deterministic comparator가 exit `0`이다.
- Iris runtime/product source와 public output은 변경되지 않는다.

최종 execution unit 수는 미리 정하지 않는다. `238`은 starting denominator일 뿐 보존 목표나 감축 quota가 아니다.

---

## 2. Scope

이 계획은 current regular validation의 실행 구조만 변경한다.

- current pytest identity와 standalone validation 4개의 contract/execution topology 전수 조사
- 동일 input, scan, parse, load, preparation, producer, materialization 및 intermediate result의 반복 확인
- same-input fan-out, lifecycle chain, repeated logic, duplicate authority 및 execution fragmentation의 판정과 구현
- constituent별 failure attribution을 보존하는 named check/result aggregation
- mutable negative case, tamper/recovery, concurrency, fresh-process 및 CLI boundary의 격리 보존
- pytest source와 standalone source 사이의 shared validation core 도입 여부 판정
- predecessor source 삭제와 taxonomy/manifest/runner/full-gate/comparator/source-policy migration
- 동일 정의를 사용한 before/after structural measurement
- clean-checkout reproducibility, deterministic comparison 및 independent review
- terminal implementation subject와 post-validation documentation/evidence carrier의 exact-subject 분리

코드 조사에서 확인한 current 시작 구조는 다음과 같다.

- `Iris/_docs/round3/round3_test_taxonomy.json`: `current + ok` 123 identity, 25 source
- `Iris/_docs/round3/current_route_required_validations.json`: required test 70 entry
- `Iris/validation/clean_checkout/contracts/full_repository_gate.json`: taxonomy selection, additional source/node 및 standalone 4개를 결합하는 canonical gate
- 최종 predecessor evidence: pytest `234` + standalone `4` = `238`
- standalone source:
  - `Iris/build/tests/test_determinism_rc.py`
  - `Iris/build/tests/test_recipe_evidence.py`
  - `Iris/build/tests/test_fail_loud_coverage.py`
  - `Iris/build/test_require_render.py`

우선 분석할 concrete family는 다음과 같다. 이 목록은 consolidation 결론이 아니라 코드 기반 조사 우선순위다.

- repository/source scan family: `test_legacy_active_silent_current_surface_guard.py`의 current identity 21개
- Layer 3 compose/package/write-boundary family: `test_compose_layer3_text_v2.py` 15개, `test_compose_layer3_text_overlay.py` 7개, `test_compose_entrypoint_guard_hardening.py` 6개, `test_lua_bridge_export_contract_realign.py` 7개, `test_package_layer3_chunks_only_contract.py` 14개
- DVF lifecycle family: complete-generation, generation-install, runtime-compatibility 및 registry-runtime-compatibility 관련 source
- authority/registration family: current-route applicability, current-authority source-path guard, taxonomy/required manifest/runner/full-gate reconciliation
- runtime-source contract family: Browser cache, lazy lookup/line-count, object access, Tags isolation, session cache 및 ViewModel allocation source/harness
- legacy standalone pipeline family: right-click determinism, recipe evidence determinism, label-map fail-loud coverage 및 require-render contract

### Explicitly Out Of Scope

- temporary/nonregular validation physical retirement 재심사 또는 retired executable 복원
- predecessor 1,167 identity census, P8/P10, owner waiver 또는 `temporary_validation_physical_retirement__complete` 재개
- historical/diagnostic/all replay selector 복원
- Iris runtime Lua behavior, offline product facts, DVF/QG semantic production, Layer 2/3/4 presentation semantics 변경
- Browser, Wiki, Tooltip UI behavior 변경
- package content, current generation pointer, public API 또는 compatibility surface 변경
- Pulse 및 다른 생태계 모듈 변경
- RTC, Publish Boundary, release, Workshop, deployment 또는 B42 readiness 판정
- unrelated refactor, architecture redesign 또는 validation policy 확장

---

## 3. Non-Goals

- pytest test name과 기존 execution identity를 그대로 보존하는 것
- 목표 감축 수치나 감축률을 먼저 정한 뒤 contract를 그 수치에 맞추는 것
- 모든 validation을 하나의 mega-validator로 합치는 것
- production decision logic과 independent oracle의 expected-value derivation을 공통화하는 것
- test order 또는 이전 test의 mutable residue에 의존하는 공유 cache를 만드는 것
- standalone 개수 `4` 자체를 유지하거나, 반대로 pytest와 비슷하다는 이유만으로 일괄 제거하는 것
- static structural reduction을 wall time, CPU, memory, GPT/Codex token 또는 PZ runtime 성능 향상으로 환산하는 것
- 전수 census, candidate ledger, recommendation 또는 후속 roadmap만 만들고 구현을 미루는 것
- 대형 permanent governance framework나 새 validation authority를 만드는 것

---

## 4. Assumptions

- `docs/Philosophy.md`가 최상위 설계 권위이며, Iris는 근거 기반 정보 모드이자 PZ runtime에서 100% Lua인 제품 경계를 유지한다.
- canonical physical-retirement implementation baseline은 `052ef0e5c90282ef9afac830bb4491b36d4e92fc`, tree `9a952fab3442bea45cada05a4b660245f978a27e`다.
- repository integration readpoint `992f45645855830bb9c169827ae4bc60b7938f56` 및 이후 HEAD는 predecessor PASS를 자동 상속하지 않는다.
- 계획 작성 시 관측한 repository HEAD는 `f9e44e98b6ffd502410cce726ceab209c42c9873`, tree `3cc082ecb66aab00c3c81630e22a96030fd9313e`다. 이는 실행 S0가 아니며 Phase 1에서 clean tracked subject를 새로 결속한다.
- 실행 S0는 independent review를 통과한 이 계획 문서의 final tracked blob을 포함하는 clean commit이어야 한다. 현재 untracked 계획 사본이나 계획 문서가 없는 predecessor HEAD는 S0로 선택하지 않는다. 실행자는 S0 receipt에 계획 path, blob identity 및 S0 ancestry를 결속한다.
- 현재 worktree의 `.codex-worktrees/iris-validation-retirement-p10-successor` 변경은 사용자 소유 상태로 간주하고 S0, measurement 및 implementation transaction에서 제외한다.
- current authority 기준값은 predecessor closeout의 pytest `234`, standalone `4`, taxonomy/runner `123`, required manifest `70`, configured collection `244`다. 이들은 서로 다른 universe이며 합산하거나 대체하지 않는다.
- clean-checkout contract는 disposable checkout Run A/B와 denominator/dependency/canonical-result deterministic comparison을 mandatory terminal gate로 요구한다.
- Python 명령은 PowerShell에서 repository가 규정한 environment/runner를 사용하고, 일반 Python validation은 `uv run python <script>` 형식을 따른다.
- product source 변경이 필요해지는 candidate는 consolidation 대상에서 제외하고 `keep_independent` 또는 blocked candidate로 기록한다.

이 계획은 첨부 roadmap과 successor review의 보류 축을 다음처럼 고정한다. 외부 review-cycle finding ID는 실행 contract로 사용하지 않는다.

- M-1: static M6 homogeneous/heterogeneous invocation count의 before/after를 모두 필수 산출한다. 이와 별도로 execution reuse를 성과로 주장하는 각 family는 disposable counter, mock/spy, runner trace, fixture/parametrization count 또는 deterministic call ledger 중 bounded mechanism으로 actual execution-semantic before/after count를 증명한다. Static call-site 감소만으로 actual reuse를 주장하지 않는다.
- M-2: file-count denominator는 actual current execution graph에 도달 가능한 tracked regular validation source file로 정의한다. Helper/fixture/generator/staging source는 file count와 분리된 physical LOC/raw-byte universe에도 포함한다.
- V-1: clean-checkout Run A/B와 deterministic comparator는 unconditional terminal requirement다.
- G-1: independent review는 severity와 무관하게 actionable finding `0`을 closeout threshold로 사용한다.
- H-1: 새로운 mandatory state taxonomy는 도입하지 않는다. 목표 state는 `complete`이며, 중단 시 템플릿의 `partial`, `implemented_only`, `blocked` 중 사실에 맞는 상태와 validation ceiling을 서술한다.
- Constituent replay: 병합 대상 constituent의 predecessor-detectable failure replay coverage를 100%로 닫은 population에만 `detection loss = 0`을 사용한다. 동일 failure class는 하나의 reproducible injection으로 묶을 수 있지만 covered constituent 목록을 명시한다.
- S0 baseline: clean S0에서 canonical current gate를 1회 실행해 exit code와 canonical result identity를 baseline evidence로 결속한다. S0 Run A/B는 요구하지 않는다.
- Independent closure universes: execution unit 238, taxonomy entry 123, required-manifest obligation 70을 서로 독립된 closure universe로 취급한다.
- Gate integrity: runner, gate, denominator enforcement, comparator/result schema 또는 source policy가 변경되면 terminal에서 missing/unregistered source, denominator mismatch 및 canonical-result tamper fail-closed probe를 수행한다. 해당 machinery가 전혀 변경되지 않은 경우에만 `gate machinery unchanged`를 기록하고 probe를 면제한다.
- Exact-subject carrier: machine PASS는 final code/test/config/registration subject인 `S_terminal`에만 귀속한다. `S_carrier`는 `S_terminal`을 유일한 direct parent로 갖는 documentation/evidence-only child/successor commit이며 predecessor PASS를 상속하거나 terminal subject를 재정의하지 않는다. Git DAG는 `S_terminal -> S_carrier`로 고정한다.

---

## 5. Repository Areas Affected

### Code

- `Iris/build/description/v2/tests/test_*.py`
- `Iris/build/description/v2/tests/conftest.py`
- `Iris/build/tests/test_evidence_pipeline_cross_track.py`
- `Iris/test/test_rightclick_pipeline.py`
- `Iris/validation/clean_checkout/tests/test_*.py`
- `Iris/build/tests/test_determinism_rc.py`
- `Iris/build/tests/test_recipe_evidence.py`
- `Iris/build/tests/test_fail_loud_coverage.py`
- `Iris/build/test_require_render.py`
- test-only helper, fixture, generator 및 staging source 중 census에서 current execution dependency로 확인된 파일
- 필요 시 validation-only shared core를 둘 기존 응집도 높은 owner directory; 새 최상위 subsystem은 만들지 않는다.

### Docs

- `docs/iris_regular_validation_boundary_execution_consolidation_plan.md`
- `docs/DECISIONS.md`
- `docs/ARCHITECTURE.md`
- `docs/ROADMAP.md`
- 구현 evidence가 필요한 경우 `Iris/_docs/refactor/` 아래의 compact successor record

Top-level authority 문서 세 개는 구현 결과가 실제로 확정된 뒤 additive successor readpoint만 기록한다. 계획 단계에서 완료 상태를 선반영하지 않는다.

### Config

- `pytest.ini`
- `conftest.py`
- `Iris/_docs/round3/round3_test_taxonomy.json`
- `Iris/_docs/round3/current_route_required_validations.json`
- `Iris/_docs/round3/round3_run_contract_tests.py`
- `Iris/validation/clean_checkout/contracts/full_repository_gate.json`
- `Iris/validation/clean_checkout/run_iris_clean_checkout_validation.py`
- `Iris/validation/clean_checkout/iris_clean_checkout_validation_common.py`
- comparator/result schema와 source-disposition policy 중 actual migration이 필요한 파일

### Generated Artifacts

- before/final metric snapshot
- predecessor contract → successor execution/check mapping, taxonomy 123-entry mapping 및 required-manifest 70-obligation mapping
- candidate disposition 및 registration delta
- M6 homogeneous/heterogeneous static before/after와 family별 actual execution-semantic count
- net context-budget path ledger와 `added analysis/documentation`, S0/final validation/tooling total, net validation/tooling reduction 및 final proxy component breakdown
- merged constituent 100% detection-replay coverage와 negative/fault-injection receipt
- clean-checkout Run A/B orchestration receipt와 deterministic comparison result
- non-author `S_terminal` implementation review, non-author `S_carrier` bounded review receipt 및 compact closeout summary

Execution output, temporary checkout, instrumentation 및 large raw logs는 repository 밖 disposable/durable evidence root에 둔다. Repository에는 final claim을 재현하는 데 필요한 compact summary와 hash-bound pointer만 추가한다.

---

## 6. Planned Changes

### Change 1 — Clean S0 및 measurement contract 고정

Purpose:

Dirty/local state와 predecessor PASS 상속을 배제하고 before/after 비교의 exact universe를 구현 전에 고정한다.

Files:

- `Iris/_docs/round3/round3_test_taxonomy.json`
- `Iris/_docs/round3/current_route_required_validations.json`
- `Iris/validation/clean_checkout/contracts/full_repository_gate.json`
- `pytest.ini`
- compact external/in-repo measurement record

Implementation Notes:

- clean tracked S0 commit/tree, Python interpreter/environment receipt 및 source blob identity를 결속한다.
- S0에서 canonical current gate를 1회 실행하고 exit code, canonical result identity 및 실행 subject를 baseline evidence로 기록한다. 이 baseline gate가 exit `0`이 아니면 consolidation regression attribution이 불가능하므로 destructive implementation wave를 시작하지 않고 `blocked`로 보고한다.
- S0 baseline FAIL 후에는 같은 failed subject에서 consolidation을 재개하지 않는다. 다음 중 하나를 별도 transaction으로 완료한 뒤 Change 1부터 새로 시작한다.
  - current authority와 intended implementation base를 모두 만족하고 attributable PASS가 있는 earlier tracked commit을 owner가 S0로 재선택하며, 원래 candidate와의 code/authority delta 및 제외된 변경을 disclose한다.
  - pre-existing defect correction을 이 계획 밖의 별도 scoped change로 구현·검증하고, correction exact subject를 새 clean S0로 결속한다.
- 어느 경로도 임의로 선택하거나 baseline FAIL을 consolidation 성과에 포함하지 않는다.
- pytest predecessor identity set과 canonical pytest collected identity set의 equality를 확인한다.
- standalone predecessor identity set과 canonical standalone execution set의 equality를 확인한다.
- 두 disjoint set의 union이 starting regular execution unit `238`과 같은지 확인한다.
- execution unit `238`, taxonomy entry `123`, required-manifest obligation `70`, configured collection `244` 및 actual runner reachability를 각각 별도 universe로 산출하고 서로 대체하지 않는다.
- tracked regular validation source file count와 test/helper/fixture/generator/staging physical LOC/raw bytes의 포함 규칙을 path 단위로 고정한다.
- M6는 setup, repository scan, manifest parse, source load, artifact generation, producer invocation, subprocess 및 temporary workspace/materialization의 static invocation signature를 계수한다. Homogeneous repeated invocation과 heterogeneous total을 분리한다.
- execution reuse를 claim할 candidate family마다 expensive operation의 actual execution-semantic count를 S0에서 포착한다. 계측은 repository 밖 disposable counter/trace, mock/spy, exact fixture/parametrization count 또는 deterministic call ledger를 사용하며 tracked subject를 변경하지 않는다.
- in-repo analysis/documentation 증가가 physical reduction을 상쇄하는지 확인할 수 있도록 `added analysis/documentation bytes - net validation/tooling reduction bytes`를 별도 net context-budget proxy로 정의한다. 두 피연산자는 Change 1에서 아래 path 단위 규칙으로 고정하고 measurement record에 path, S0 bytes, final bytes, delta 및 blob identity를 기록한다.
  - `added analysis/documentation bytes` universe는 이 계획 문서, 이번 execution을 위해 추가·수정한 `Iris/_docs/refactor/` compact successor record, `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md` additive readpoint 및 그 밖의 in-repo analysis/governance/evidence projection file을 포함한다. 각 included path의 `max(S_carrier bytes - S0 bytes, 0)`을 합산한다. S0에 이미 존재하는 이 계획 문서의 baseline bytes는 added 값이 아니지만 S0 이후 증가분은 포함한다. 삭제·축소된 documentation bytes로 다른 documentation 증가분을 상쇄하지 않는다.
  - `net validation/tooling reduction bytes` universe는 M-2에서 고정한 current validation/test source와 그 helper, fixture, generator, staging, shared core 및 validation-only runner/config/tool dependency closure 전체다. `S0 universe total bytes - S_terminal universe total bytes`로 계산한다. 신규 shared core/helper/tooling bytes는 final total에 포함되어 제거량에서 자동 차감한다. Final total이 더 크면 이 피연산자는 음수이며 gross-deleted bytes만을 유리하게 사용하지 않는다.
  - rename/move는 S0/final path-set과 tracked blob identity를 함께 대조해 deletion과 addition을 각각 반영한다. Generated disposable/result/evidence root와 repository 밖 raw log는 두 in-repo 피연산자에서 제외한다.
  - final proxy 공식은 `added analysis/documentation bytes - net validation/tooling reduction bytes`다. S0→`S_carrier` completion threshold는 `proxy <= 0`으로 고정한다. 양수이면 repository-side physical/context surface가 순증가한 것이므로 `complete`로 닫지 않는다. 이 proxy를 token 절감으로 해석하지 않는다.
  - contract preservation, independent oracle, negative/fail-closed detection, constituent localization 및 maximal safe consolidation은 context-budget proxy보다 우선한다. `proxy <= 0`을 맞추기 위해 이 검증력을 삭제하거나 병합 가능한 candidate를 `keep_independent`로 돌리는 것은 금지한다. Proxy가 양수이면 analysis/governance/evidence projection의 불필요한 payload를 먼저 축소하고, 그래도 양수라면 실제 수치를 공개한 채 completion threshold 미충족으로 처리한다.

Validation:

- S0 `git status --short`가 허용된 외부/worktree 상태를 제외하고 clean인지 확인한다.
- 동일 S0에서 measurement를 두 번 실행해 구조 count와 path set이 일치하는지 확인한다.
- S0 canonical current gate 1회가 exit `0`이고 canonical result identity가 receipt에 기록됐는지 확인한다.
- pytest set equality, standalone set equality 및 두 set의 union `238`을 각각 확인한다.
- taxonomy/runner `123`, manifest `70`, configured collection `244`를 execution set과 다른 label로 재확인한다.
- M6 static before와 candidate-family actual execution-semantic before를 함께 확정한다.

---

### Change 2 — Whole-boundary contract/execution census

Purpose:

Starting 238개 execution unit 전부를 contract와 execution-cost topology에 연결해 누락 없는 판정 기반을 만든다.

Files:

- current test/standalone source 전체
- current fixture/helper/generator/staging dependency closure
- taxonomy, required manifest, runner 및 full-gate configuration
- compact census/disposition working record

Implementation Notes:

각 execution unit에 다음 필드를 연결한다.

```text
predecessor identity
-> contract key
-> product/validation-system owner
-> input universe
-> preparation/producer/intermediate result
-> observable/assertion/failure class
-> isolation/process requirement
-> registration/reachability path
```

- AST/import/call-site 조사와 code read를 함께 사용하고 filename 또는 기존 registration만으로 contract equivalence를 판정하지 않는다.
- taxonomy 123개뿐 아니라 additional source/node와 standalone 4개까지 final denominator 전체를 포함한다.
- S0 taxonomy 123개 entry와 required-manifest 70개 obligation은 execution row에 부수적으로 매달지 않고 각각 독립 row universe로 inventory한다. 각 row는 predecessor ID, current obligation/role, source/reachability 및 eventual successor target을 갖는다.
- fixture/helper/generator가 여러 family에서 같은 repository tree나 manifest를 다시 읽는지 확인한다.
- clean-checkout runner가 taxonomy, required manifest 및 full gate를 반복 parse/normalize하는 orchestration도 별도 candidate로 본다.

Validation:

- starting execution unit마다 census row가 정확히 하나 존재한다.
- census identity set과 canonical gate의 live collected identity set이 equality를 이룬다.
- predecessor taxonomy entry 123개와 required-manifest obligation 70개가 각각 중복·누락 없이 inventory된다.
- 누락 source, 중복 row 및 unresolved registration path가 `0`이다.

---

### Change 3 — Consolidation adjudication 및 successor 설계

Purpose:

모든 starting unit에 독립 유지 또는 구체적인 consolidation disposition을 부여하고 implementation transaction을 정한다.

Files:

- compact disposition/mapping record
- candidate family의 current source/configuration

Implementation Notes:

허용 disposition은 다음으로 제한한다.

- `keep_independent`
- `same_input_merge`
- `absorb_as_named_check`
- `table_driven_conversion`
- `pipeline_merge`
- `shared_core_replacement`
- `duplicate_authority_removal`

`keep_independent`에는 independent prerequisite, distinct side effect, mutable tamper/recovery, concurrency, fresh process/bootstrap, CLI/exit/stdout/stderr, independent oracle 또는 failure-isolation 중 실제 사유를 기록한다.

병합으로 responsibility cohesion, 유지보수성 또는 판독성이 실질적으로 악화되는 경우도 concrete code evidence와 함께 `keep_independent` 사유로 허용한다. 단순히 기존 파일/이름을 선호한다는 이유는 허용하지 않는다.

위 execution-structure disposition은 predecessor physical-retirement의 authority-survival disposition과 별개다.

```text
keep_independent / merge / absorb / table-driven / pipeline / shared-core
= current execution-structure disposition

keep_regular_product_contract / keep_regular_validation_system_contract / ...
= sealed predecessor authority-survival disposition
```

이번 계획은 두 번째 축을 재판정하지 않는다.

Merge candidate에는 shared input/preparation/result, case-local mutable state, successor check ID, sibling continuation semantics, producer-failure dependency, registration delta 및 predecessor physical removal target을 기록한다.

특히 다음을 확인한다.

- 21-check repository scan family가 `scan once -> named checks`로 전환 가능한가
- compose/overlay/write-boundary/package family가 같은 fixture/materialization 또는 producer result를 반복 생성하는가
- complete-generation → install → runtime compatibility가 intermediate result를 재생성하는가
- source-path/current-route/taxonomy/full-gate 검사가 equivalent validation-system observable을 중복 소유하는가
- standalone 4개의 process boundary가 contract 자체인지, 혹은 canonical shared core를 호출하는 thin CLI로 축소 가능한가

각 병합 constituent에는 predecessor가 탐지하던 failure 또는 failure class와 reproducible injection을 연결한다. 동일 failure-class injection을 공유하면 해당 probe가 cover하는 constituent ID 목록을 명시한다. Reproducible detection proof를 만들 수 없는 constituent는 병합하지 않는다.

Taxonomy/manifest entry에는 execution disposition과 별도로 다음 중 하나를 부여하고 successor target ID를 기록한다.

- `successor_entry`
- `absorbed_into_named_check`
- `removed_as_duplicate`

Validation:

- 모든 predecessor identity에 정확히 하나의 disposition이 있다.
- taxonomy 123개 entry와 required-manifest 70개 obligation 각각에 item-level disposition과 successor target이 있다.
- equivalent contract 판정은 `contract + input universe + observable + failure semantics`가 모두 같은 경우에만 허용한다.
- product producer와 expected oracle의 semantic decision logic을 공유하는 candidate는 reject한다.
- merged constituent detection replay plan의 coverage denominator와 expected coverage가 100%인지 확인한다.
- `keep_independent`가 아닌 모든 disposition은 구체적인 implementation wave, successor target 및 predecessor physical removal target에 연결된다. Recommendation-only 또는 unscheduled merge disposition은 허용하지 않는다.
- 모든 `keep_independent` row는 구체적인 code evidence와 함께 final non-author implementation review의 전수 검토 대상으로 표시한다. 파일 경계, 기존 이름, 구현 부담 또는 validation 비용만을 독립 유지 사유로 사용하지 않는다.

---

### Change 4 — Shared primitives 및 structural consolidation wave 구현

Purpose:

판정된 eligible candidate를 실제 실행/source 구조에서 병합한다.

Files:

- adjudicated current test source
- validation-only helper/fixture/core
- 필요한 taxonomy/manifest/runner/full-gate entry

Implementation Notes:

구현은 다음 wave 순서로 진행한다.

1. immutable input load, parse, path normalization 및 prepared-state primitive
2. same-input fan-out을 `prepare once -> multiple named checks`로 전환
3. lifecycle chain의 intermediate result를 explicit single-owner workflow state로 전달
4. 반복 traversal/assertion/comparison을 table-driven row 또는 common checker로 전환
5. duplicate authority와 execution-only wrapper 제거
6. standalone process contract가 남는 경우 CLI와 pytest가 canonical shared core를 소비하도록 전환

- 여러 기존 test body를 한 함수에서 차례로 호출하는 것만으로 consolidation을 인정하지 않는다. producer/preparation invocation 또는 physical execution/registration surface가 실제 감소해야 한다.
- 각 adopted family의 expensive operation에 S0와 동일한 bounded mechanism을 적용해 actual execution-semantic after count를 산출한다. `producer 4 -> 1`, `materialization 3 -> 1`처럼 before/after를 family와 operation에 결속하며, 증명하지 못한 reuse는 성과나 completion evidence로 계상하지 않는다.
- independent sibling check는 가능한 한 모두 실행하고, result에는 constituent ID별 PASS/FAIL을 남긴다.
- producer 실패로 downstream check가 불가능하면 producer failure와 blocked dependent check를 구분한다.
- immutable seed는 공유할 수 있으나 writable workspace, mutation state, temporary output 및 process-local state는 case-local로 유지한다.

Validation:

- 각 wave에 `same input -> same observable -> same failure class/meaning`을 통과 기준으로 predecessor-vs-successor shared primitive parity check를 수행한다.
- contract-family positive smoke와 병합 constituent 전수 negative/fail-closed replay의 failure localization을 focused command로 검증한다.
- 병합 대상의 predecessor-detectable constituent/failure-class population 100%에 대해 병합 전 포착한 injection을 successor에서 replay하고, failure detection과 constituent ID localization을 모두 확인한다. 동일 probe로 여러 constituent를 cover한 경우 coverage mapping을 receipt에 남긴다.
- mutable case를 순서 변경 및 반복 실행해 residue/order dependency가 없는지 확인한다.
- source와 registration migration을 같은 wave에서 완료하고 mixed dual-authority 상태를 남기지 않는다.
- 각 wave의 M6 static after와 family별 actual execution-semantic after를 임시 집계해 예상 감소가 실제로 발생했는지 확인한다.

---

### Change 5 — Authority/execution reconciliation

Purpose:

Final validation authority와 actual collection/execution graph를 일치시키고 deleted predecessor의 stale route를 제거한다.

Files:

- `Iris/_docs/round3/round3_test_taxonomy.json`
- `Iris/_docs/round3/current_route_required_validations.json`
- `Iris/_docs/round3/round3_run_contract_tests.py`
- `Iris/validation/clean_checkout/contracts/full_repository_gate.json`
- `Iris/validation/clean_checkout/run_iris_clean_checkout_validation.py`
- `pytest.ini`, `conftest.py` 및 관련 schemas/policies

Implementation Notes:

- successor node/check identity를 taxonomy와 required manifest에 반영한다.
- predecessor taxonomy 123개 entry와 required-manifest 70개 obligation의 item-level disposition을 final successor entry/check에 대조한다. Predecessor entry 삭제는 duplicate/absorption 근거와 successor target 없이 허용하지 않는다.
- additional source/node와 standalone command registration을 final structure에 맞춘다.
- runner selection, denominator enforcement, source policy classification, full-gate result projection 및 deterministic comparator가 같은 identity model을 사용하도록 정렬한다.
- predecessor identity compatibility만을 위한 alias/wrapper는 만들지 않는다.
- historical/diagnostic/all selector를 복원하지 않고 current fail-closed classification을 유지한다.

Validation:

- orphan registration `0`
- stale deleted-source reference `0`
- accidental duplicate execution registration `0`
- unclassified current validation source `0`
- multiple source classification `0`
- missing source-policy entry `0`
- unmapped predecessor taxonomy entry `0`
- unmapped predecessor required-manifest obligation `0`
- taxonomy/manifest/runner/collection/full-gate reachability reconciliation PASS

---

### Change 6 — Physical cleanup 및 second exhaustive sweep

Purpose:

병합 뒤 불필요해진 source/configuration을 실제 삭제하고 consolidation으로 새로 드러난 잔여 중복을 처리한다.

Files:

- obsolete pytest function/class/file
- obsolete standalone/validation wrapper
- unused fixture/helper/generator/staging source
- dead runner/comparator/schema/policy branch
- final code-reference and documentation successor records

Implementation Notes:

- `rg`, import graph, runner reachability 및 dynamic collection evidence를 함께 사용해 deletion closure를 확인한다.
- one-use wrapper, now-unused helper, repeated preparation/producer, duplicate authority 및 accidental new duplication을 두 번째 전수 sweep에서 다시 판정한다.
- Change 3에서 `keep_independent`가 아닌 disposition은 이 phase 종료 전에 모두 구현되어야 한다. 미구현 merge/absorb/table-driven/pipeline/shared-core/removal disposition을 후속 작업으로 넘기지 않는다.
- M6에서 동일 input, preparation, producer 또는 intermediate result가 둘 이상의 execution path에 남은 각 compatible group을 다시 대조한다. 병합 가능한 group은 같은 phase에서 구현하고, 병합할 수 없는 group은 isolation/oracle/process/side-effect 경계에 근거한 `keep_independent` 사유로 결속한다.
- 삭제는 exact path로 수행하고 unrelated/user-owned changes를 수정하거나 stage하지 않는다.
- large analysis ledger를 새 permanent payload로 남기지 않는다. predecessor mapping과 final claim에 필요한 compact record만 보존한다.

Validation:

- deleted path/callable의 repository-wide live reference `0`
- current source reachability 누락 `0`
- final tracked validation source count와 LOC/raw bytes를 Phase 1 정의로 재계산
- 최종 sweep에서 새 eligible candidate가 남으면 같은 phase 안에서 구현하거나 구체적인 independent reason을 기록
- second sweep에서 추가 구현이 발생하면 Change 4와 같은 wave-atomic source+registration transaction을 적용하고 Change 5의 전체 authority reconciliation을 다시 실행한다. 기존 reconciliation receipt는 재사용하지 않는다.
- second sweep 종료 시 remaining eligible consolidation candidate `0`, 미구현 non-keep disposition `0`, evidence가 없는 `keep_independent` disposition `0`

---

### Change 7 — Terminal validation 및 independent closeout

Purpose:

Final exact subject에 contract preservation, deterministic execution 및 authority closure를 결속한다.

Files:

- clean-checkout receipts/result bundle
- final measurement and predecessor-successor map
- independent review receipt
- `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`의 additive successor readpoint

Implementation Notes:

- final code, test, config, registration, gate command/denominator 및 compact predecessor-successor mapping을 포함한 exact commit/tree를 `S_terminal`로 동결한다.
- `S_terminal`에서 dedicated external environment와 서로 disjoint한 disposable checkout/result/evidence roots를 사용한다.
- runner, common gate logic, full-gate definition, denominator enforcement, comparator/result schema 또는 source policy가 S0 대비 변경됐다면 disposable negative subject/result를 사용해 다음 세 probe를 수행한다.
  - missing 또는 unregistered current source에서 gate가 FAIL한다.
  - denominator mismatch에서 enforcement가 FAIL한다.
  - canonical result tamper에서 comparator가 FAIL한다.
- 위 machinery가 하나도 변경되지 않았다면 blob/path comparison과 함께 `gate machinery unchanged`를 기록하고 세 probe를 면제한다.
- clean-checkout Run A와 Run B를 `S_terminal`에서 각각 실행하고 deterministic comparator로 denominator, dependency inventory, source identity 및 canonical result identity를 비교한다.
- comparator/result schema가 변경됐다면 predecessor와 terminal canonical-result SHA-256을 직접 비교 가능한 delta로 사용하지 않는다. 대신 각 schema 내부의 required invariant와 Run A/B 동등성을 검증한다.
- predecessor contract → successor execution → named check, taxonomy entry 및 required-manifest obligation mapping의 closure를 별도로 확인한다.
- final M6 static homogeneous/heterogeneous after 값을 setup, scan, parse, source load, artifact generation, producer invocation, subprocess 및 workspace/materialization 전 축에 대해 산출한다. 감소하지 않은 축도 그대로 보고한다.
- adopted family별 actual execution-semantic before/after count와 merged constituent replay coverage를 final metric에 포함한다.
- S0→`S_terminal` implementation range의 non-author independent review를 수행한다. Reviewer는 reviewed implementation delta의 작성자이거나 그 closeout claim의 작성자여서는 안 된다.
- implementation reviewer는 모든 `keep_independent` disposition과 final residual repeated-operation group을 전수 검토해 추가로 안전하게 병합할 수 있는 candidate가 남지 않았는지 판정한다. Unsupported keep, 미구현 non-keep disposition 또는 remaining eligible candidate는 severity와 무관하게 actionable finding이다.
- review correction이 code/test/config/command/denominator/gate dependency 또는 `S_terminal`의 tracked content를 변경하면 새 `S_terminal`을 만들고 영향 범위 validation, negative probe, Run A/B, comparator 및 implementation review를 새 subject에 다시 귀속한다.
- machine PASS authority는 `S_terminal`에만 귀속한다.
- terminal validation과 implementation review가 끝난 뒤 `S_terminal`을 유일한 direct parent로 갖는 documentation/evidence-only child/successor commit `S_carrier`를 만든다. Git DAG는 `S_terminal -> S_carrier`다. Carrier delta는 measured result/closeout summary, evidence pointer와 `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md` additive successor readpoint로 제한한다.
- `S_carrier`의 code/test/config/command/denominator/gate dependency mutation은 `0`이어야 한다. 해당 surface가 바뀌면 carrier가 아니라 새 implementation subject로 취급한다.
- `S_carrier`는 `S_terminal`의 machine PASS를 자신의 PASS로 상속하지 않고 terminal validation subject를 재정의하지 않는다. Closeout 문구는 "`S_terminal`에서 machine PASS한 implementation을 `S_carrier`가 기록한다"는 범위로 제한한다.
- final authority-document delta를 포함한 `S_terminal`→`S_carrier` 범위에 non-author bounded carrier review를 수행한다. Reviewer는 reviewed carrier delta 또는 그 closeout claim의 작성자여서는 안 된다. Implementation reviewer와 carrier reviewer는 동일인일 수 있지만, 동일인이 양쪽 reviewed delta 모두의 non-author 조건을 충족해야 한다. Actionable finding 또는 forbidden delta가 있으면 carrier를 수정하고 review를 반복한다.

Validation:

- S0 gate baseline exit `0` 및 canonical result identity 결속
- gate machinery 변경 시 missing/unregistered source probe expected FAIL
- gate machinery 변경 시 denominator mismatch probe expected FAIL
- gate machinery 변경 시 canonical result tamper comparator probe expected FAIL
- terminal Run A exit `0`
- terminal Run B exit `0`
- deterministic comparator exit `0`
- standalone successor boundary 전부 exit `0`
- M6 static before/after 전 축 산출 및 family별 actual execution-semantic before/after 결속
- merged constituent detection replay coverage `100%`
- unmapped taxonomy entry `0`, unmapped required-manifest obligation `0`
- clean-checkout Run A/B 각각의 실행 전후 tracked tree mutation `0`; S0→`S_terminal`의 승인된 implementation range 밖 unexpected tracked-path mutation `0`; declared disposable/result/evidence roots 이외의 external mutation `0`
- non-author implementation review와 non-author bounded carrier review의 actionable finding `0`
- `S_carrier` parent count `1` 및 sole parent identity = `S_terminal`
- `S_carrier`의 code/test/config/command/denominator/gate-dependency mutation `0`
- product/runtime/public output mutation `0`

---

## 7. Validation Plan

### Automated Validation

- Phase 1 census/metric determinism: 동일 S0에서 두 번 실행한 identity/path/count equality
- S0 canonical current gate 1회: exit code `0`, canonical result identity 및 exact subject receipt
- current collection reconciliation: pytest predecessor/canonical-collected set equality, standalone predecessor/canonical-execution set equality 및 두 set union `238`
- taxonomy 123 entry와 required-manifest 70 obligation의 독립 inventory 및 item-level successor closure
- changed Python source: `uv run python <script>` 또는 repository가 소유한 `uv run python -m pytest <focused selection>`
- focused family validation:
  - shared preparation/result predecessor parity
  - named constituent check result와 sibling continuation
  - producer failure와 assertion failure 구분
  - missing input, malformed manifest, stale identity, duplicate/collision 및 forbidden state
  - tamper, mutation, rollback/recovery 및 process failure
  - order permutation, repeated run, previous-run residue 및 writable workspace isolation
- adopted family별 bounded actual execution-semantic before/after count와 final M6 static before/after
- merged constituent predecessor-detectable failure population 100% replay와 constituent localization
- runner/taxonomy/manifest/full-gate graph reachability와 stale/orphan/duplicate registration 검사
- gate machinery 변경 시 missing/unregistered source, denominator mismatch 및 canonical-result tamper의 expected-failure probe
- standalone CLI가 유지될 경우 exit code, stdout/stderr, fresh-process 및 environment restoration 검사
- Lua source가 변경되지 않았음을 tree diff로 검증한다. 예상 밖 Lua 변경이 있으면 fail closed하고, 승인된 validation-only Lua fixture 변경이 있을 때만 `powershell -ExecutionPolicy Bypass -File .\tools\check_lua_syntax.ps1`를 실행한다.
- exact terminal subject의 canonical clean-checkout Run A/B와 `Iris/validation/clean_checkout/invoke_deterministic_compare.ps1`
- S0→`S_terminal` implementation range의 non-author independent static review와 `S_terminal`→`S_carrier` documentation/evidence-only non-author bounded review
- Git ancestry check: `S_carrier`의 parent가 정확히 하나이고 그 identity가 `S_terminal`인지 확인

모든 required validation은 exact command exit code `0`일 때만 PASS로 기록한다. 필수 도구나 dedicated environment가 없으면 PASS가 아니라 `blocked`다.

### Manual Validation

- predecessor contract → successor check mapping의 전수 code review
- `keep_independent` 사유가 실제 isolation/oracle/CLI contract인지 검토
- shared helper가 production expected logic 또는 mutable global cache를 흡수하지 않았는지 검토
- removed wrapper/fixture/helper의 hidden consumer 및 dynamic path reference 검토
- final Git diff에서 Iris runtime Lua, product data, public text, package 및 generation pointer 변경이 없는지 확인
- before/after claim이 동일 universe/definition을 사용하는지 검토
- carrier delta가 documentation/evidence projection으로만 구성되고 code/test/config/command/denominator/gate dependency를 바꾸지 않는지 검토

인게임/UI 수동 검증은 product source를 변경하지 않는 이번 계획의 기본 gate가 아니다. 예상 밖 product diff가 생기면 구현을 중단하고 scope 위반으로 처리한다.

### Validation Limits

- PZ in-game behavior, FPS/frame time 및 runtime heap을 검증하지 않는다.
- multiplayer, long-session 및 external mod compatibility sweep을 수행하지 않는다.
- RTC, Publish Boundary, packaging publication, deployment, release, Workshop 또는 B42 readiness를 검증하지 않는다.
- historical/diagnostic executable replay를 복원하거나 재실행하지 않는다.
- comparable benchmark campaign이 없으면 wall time, CPU, memory 또는 token 개선률을 주장하지 않는다.
- static invocation reduction은 runtime cost reduction의 직접 측정값으로 해석하지 않는다.
- `S_carrier` 자체에 `S_terminal`의 machine PASS가 귀속됐다고 주장하지 않는다.

---

## 8. Risk Surface Touch

### Authority Surface

High. Current pytest/standalone identity, taxonomy, required manifest, runner, full gate, comparator/result projection 및 source classification을 직접 변경한다. Product contract ownership은 바꾸지 않고 successor named check로 이관한다. Closeout lineage는 `S_terminal -> S_carrier` 단일-parent DAG로 제한하고 두 delta의 review는 각각 non-author가 수행한다.

### Runtime Behavior Surface

None by design. `Iris/media/lua/`, product build source, current data/generation 및 runtime package behavior는 변경하지 않는다.

### Compatibility Surface

Product compatibility surface는 변경하지 않는다. Validation-side standalone CLI/process surface는 contract 판정에 따라 유지·축소·제거될 수 있으나, 유지되는 CLI의 exit/stdout/stderr/environment contract는 보존한다.

### Sealed Artifact Surface

Existing physical-retirement ledger, receipt, completion token 및 sealed historical evidence는 read-only이며 rewrite하지 않는다. 새 terminal evidence는 `S_terminal` exact subject에 결속하고, top-level authority 문서와 compact evidence projection은 `S_terminal`을 유일한 direct parent로 갖는 documentation-only successor `S_carrier`에 append-only successor record로 추가한다. Carrier는 terminal result를 재정의하거나 자신의 machine PASS로 상속하지 않는다.

### Public-Facing Output Surface

None. Iris 메뉴, Tooltip, KO/EN public text 및 package projection은 변경하지 않는다.

---

## 9. Risk Analysis

### Architecture Risk

- 같은 producer를 쓴다는 이유만으로 서로 다른 contract를 병합할 수 있다.
- production decision logic과 independent oracle을 공통화해 defect detection power를 낮출 수 있다.
- 과도한 merge로 mega-validator 또는 새 validation governance subsystem이 생길 수 있다.
- source migration과 registration migration이 어긋나 dual/orphan authority가 생길 수 있다.

완화책은 contract axis와 execution axis 분리, exact predecessor-successor mapping, wave-atomic registration migration, shared I/O/preparation과 semantic oracle 분리다.

### Runtime Risk

- Product runtime risk는 설계상 없어야 한다.
- validation execution에서는 shared mutable state, test-order dependency, workspace residue 또는 subprocess environment leak가 생길 수 있다.

완화책은 immutable/single-owner result만 공유하고 writable workspace와 process-local state를 case-local로 유지하며 order/repeat/failure-injection 검사를 수행하는 것이다.

### Compatibility Risk

- standalone을 제거하거나 in-process로 바꾸면서 CLI, bootstrap, exit code 또는 stdout/stderr contract를 잃을 수 있다.
- predecessor node name을 소비하는 manifest/runner/comparator가 stale해질 수 있다.

완화책은 standalone별 contract 판정, reachability reconciliation 및 long-lived compatibility alias 금지다.

### Regression Risk

- merged workflow의 첫 failure가 sibling 결과를 불필요하게 차단할 수 있다.
- negative/fail-closed condition이 positive parity만 남고 사라질 수 있다.
- helper 삭제 시 dynamic consumer를 놓칠 수 있다.
- before/after metric universe drift로 감축을 과장할 수 있다.
- S0 baseline 없이 predecessor defect와 consolidation regression을 혼동할 수 있다.
- modified gate/comparator가 자기 PASS만으로 integrity를 인증할 수 있다.
- terminal PASS 뒤 docs carrier가 tracked subject를 바꾸어 exact-subject authority가 모호해질 수 있다.

완화책은 S0 canonical gate baseline, 100% merged-constituent replay, family별 actual execution count, modified-gate negative probes, named result aggregation, static+live collection reference 확인, Phase 1 metric definition freeze 및 `S_terminal`/`S_carrier` 분리다.

---

## 10. Rollback Plan

Rollback 단위는 consolidation wave다.

각 wave는 다음을 하나의 transaction으로 취급한다.

```text
shared source/core change
+ successor checks
+ predecessor deletion
+ taxonomy/manifest/runner/full-gate migration
+ focused validation evidence
```

unique contract loss, false-negative, failure attribution loss, oracle independence collapse, fresh-process/CLI/isolation loss, order dependency, mutable state leak, product source mutation 또는 registration mismatch가 확인되면 해당 wave 전체를 되돌린다.

- predecessor execution/source와 registration을 함께 복원한다.
- partial successor registration과 dead shared helper를 함께 제거한다.
- predecessor와 successor를 장기간 동시에 current authority로 남기지 않는다.
- unrelated/user-owned worktree 변경은 rollback 대상에 포함하지 않는다.
- physical-retirement source, retired route 또는 owner-waived archive/restore 요구를 rollback material로 사용하지 않는다.
- terminal review correction이 필요하면 correction commit을 만든 뒤 새 exact subject에서 관련 validation과 Run A/B를 다시 수행한다. 이전 subject PASS를 재사용하지 않는다.
- non-author bounded carrier review에서 documentation/evidence-only finding이 나오면 carrier만 교정하고 non-author carrier review를 반복한다. Carrier correction이 forbidden implementation/gate surface를 건드리면 carrier rollback 후 새 `S_terminal` 절차로 돌아간다.

---

## 11. Governance Constraints

- `docs/Philosophy.md`와 Iris의 근거 기반 정보/중립성/100% Lua runtime 경계를 준수한다.
- Pulse가 Iris를 참조하거나 의존하지 않으며, Iris consolidation을 이유로 다른 spoke와 직접 의존하지 않는다.
- current/historical/diagnostic route 결과를 서로 대체하지 않는다.
- physical retirement의 P8/P10, owner waiver 및 completion token을 재판정하거나 reopen하지 않는다.
- runtime/build-time separation과 product/validation authority separation을 유지한다.
- product contract coverage와 valid negative/fail-closed detection을 execution identity보다 우선한다.
- independent oracle의 expected derivation을 production logic과 공유하지 않는다.
- test-order dependency와 mutable global scenario cache를 금지한다.
- fresh-process, CLI, tamper/recovery, concurrency 및 destructive isolation이 contract이면 경계를 유지한다.
- source deletion과 authority/registration migration을 wave-atomic하게 수행한다.
- identity 보존만을 위한 wrapper/alias를 만들지 않는다.
- exact subject 이후의 변경에 predecessor PASS를 상속하지 않는다.
- `S_terminal` 이후의 documentation/evidence carrier는 machine PASS를 상속하거나 validated subject를 재정의하지 않으며, forbidden carrier delta는 새 implementation subject로 승격한다.
- sealed evidence는 rewrite하지 않고 successor record를 additive하게 추가한다.
- dirty/untracked/user-owned state를 조사 결과나 성과 metric에 혼입하지 않는다.
- analysis/governance artifact가 실제 validation source reduction을 상쇄할 정도로 커지지 않게 한다.
- measured structural reduction만 보고하고 runtime/token 개선을 추정하지 않는다.
- final authority 문서에는 구현·검증으로 확인된 사실만 기록한다.

---

## 12. Expected Closeout State

Expected closeout target: `complete`

`complete` closeout은 아래 machine/implementation 조건을 만족한 `S_terminal`과, `S_terminal`을 유일한 direct parent로 갖고 documentation/evidence-only 조건을 만족한 child/successor `S_carrier`의 pair에만 기록한다. Git DAG는 `S_terminal -> S_carrier`이며 machine PASS 자체는 계속 `S_terminal`에만 귀속한다.

- starting 238개 unit 전부에 final disposition과 predecessor→successor/keep mapping이 있다.
- predecessor taxonomy 123개 entry와 required-manifest 70개 obligation 전부에 item-level disposition과 successor target이 있으며 unmapped entry가 각각 `0`이다.
- `keep_independent`가 아닌 모든 disposition이 실제 구현되고 해당 predecessor source/registration이 제거됐다. 미구현 non-keep disposition은 `0`이다.
- second exhaustive sweep과 non-author implementation review를 모두 마친 뒤 remaining eligible consolidation candidate와 evidence 없는 `keep_independent` disposition이 각각 `0`이다. 현재 contract와 failure semantics를 보존하면서 추가로 병합·흡수·공통화·삭제할 수 있는 regular execution structure가 남아 있으면 `complete`가 아니다.
- adopted candidate의 구현 결과를 execution/source/registration 및 actual execution-semantic metric별로 모두 보고한다. 한 개 metric 또는 한 개 family의 감소만으로 maximal consolidation 완료를 주장하지 않는다. Eligible candidate가 `0`인 개별 metric 축에는 감축 quota를 강제하지 않지만, 잔존 compatible repeated-operation group에는 각각 검토된 독립 유지 사유가 있어야 한다.
- S0 canonical current gate 1회가 exit `0`이고 canonical result identity가 exact S0에 결속됐다.
- merged constituent의 predecessor-detectable failure replay coverage가 `100%`이며, 이 population에 대한 contract protection loss와 valid negative/fail-closed detection loss가 각각 `0`이다.
- independent oracle collapse가 `0`이다.
- orphan/stale/duplicate registration과 unclassified current source가 각각 `0`이다.
- failure attribution, sibling result collection, mutable isolation 및 required process/CLI boundary가 보존된다.
- final exact tracked subject의 clean-checkout Run A/B와 deterministic comparator가 exit `0`이다.
- gate machinery가 변경됐다면 missing/unregistered source, denominator mismatch 및 canonical-result tamper probe가 모두 expected FAIL을 냈고, 변경되지 않았다면 `gate machinery unchanged`가 증명됐다.
- clean-checkout Run A/B 각각의 실행 전후 tracked tree mutation, S0→`S_terminal` 승인 범위 밖 unexpected tracked-path mutation, declared disposable/result/evidence roots 이외의 external mutation 및 Iris runtime/product/public-output change가 각각 `0`이다.
- non-author `S_terminal` implementation review와 non-author `S_carrier` bounded review의 actionable finding이 각각 `0`이다.
- final pytest, standalone, total execution, taxonomy, required manifest, source file 및 LOC/raw-byte 수치를 Phase 1과 같은 정의로 산출했다.
- final M6 static homogeneous/heterogeneous after가 모든 정의된 operation 축에 존재하고, 감소하지 않은 축도 공개됐다.
- execution reuse를 주장하는 각 family에 actual execution-semantic before/after count가 결속됐다.
- S0→`S_carrier`의 `added analysis/documentation bytes - net validation/tooling reduction bytes` proxy가 Change 1의 frozen path universe와 per-path ledger로 산출되어 `<= 0`이다. 신규 shared core/helper/tooling은 final validation/tooling total에 포함됐고 gross deletion을 net reduction으로 오인하지 않으며, 이 결과를 token 절감으로 오독하지 않는다.
- context-budget proxy를 맞추기 위한 contract coverage, independent oracle, negative/fail-closed detection, constituent localization 또는 eligible consolidation 포기는 `0`이다.
- machine PASS는 `S_terminal`에만 귀속되고 `S_carrier`의 sole parent identity는 `S_terminal`, parent count는 `1`, code/test/config/command/denominator/gate-dependency mutation은 `0`이다.

조사만 끝났으면 `complete`가 아니다. 구현은 끝났지만 terminal gate가 없으면 `implemented_only`, 일부 wave만 끝났으면 `partial`, 필수 환경·권한·외부 조건 때문에 진행할 수 없으면 `blocked`로 보고하고 충족하지 못한 validation ceiling을 명시한다.
