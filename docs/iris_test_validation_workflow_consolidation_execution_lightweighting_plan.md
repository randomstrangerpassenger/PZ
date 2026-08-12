# Implementation Plan

> Iris Test & Validation Workflow Consolidation and Execution Lightweighting 실행 계획
>
> 작성 기준일: 2026-08-13
>
> 작성 시 코드베이스 readpoint: commit `671c7b928ad5a1dbf26ea76949462fa8a7287903`, tree `20bbbdb919fa97a44e03c1f1cb9ea0a6973fb1db`
>
> 선행 terminal subject: commit `730849134400311a2fa10588c9adb58a8bd037e0`, tree `99dead8b472fe4a8fa6cf8288c9676db287a75de`
>
> 선행 evidence-only carrier: commit `07b26f1bae394f4f7e08f51ad1bbb312dbc3a491`, tree `e3a749ba3ec76b5dd5f32347c12081c0cfa97bdb`
>
> 선행 durable retrieval key: `iris-test-precision-lightweighting-20260812-01`
>
> 상태: roadmap/architecture direction adopted, implementation 및 terminal accepted paired measurement pending

---

## 1. Objective

Iris의 current, historical, diagnostic 및 Clean-Checkout 검증 의미와 authority를 유지하면서, 같은 immutable input과 repository subject에 대해 반복되는 producer 실행, subprocess 시작, workspace/materialization, 파일 read/parse/hash 및 copy 비용을 contract family 또는 scenario lifecycle 단위로 줄인다.

목표 실행 구조는 다음과 같다.

```text
explicit ScenarioContext
-> expensive producer/lifecycle execution once
-> immutable ExecutionResult
-> named ProbeResult/checkpoint set
-> dependency-aware adjudication
-> deterministic ScenarioReport
-> declarative contract assertions
```

Shared execution kernel은 input 준비, command 실행, output parse와 result 전달만 담당한다. Registry, DVF, IAR, RTC, Publish Boundary 또는 current/historical/diagnostic route의 semantic authority를 흡수하지 않는다.

첫 vertical slice는 `Iris/build/description/v2/tests/test_public_text_quality_acceptance_current_route.py`의 Phase 7 self-test family다. 이 파일의 앞 4개 test는 현재 동일한 `--self-test --no-write` CLI producer를 각각 실행해 같은 result의 서로 다른 case만 검사한다. Pilot은 기존 4개 test identity를 우선 보존한 채 class/scenario-owned immutable result를 한 번 만들고, 각 test를 named probe consumer로 유지하는 방식을 먼저 적용한다. 실제 runner semantics상 identity 보존 방식으로 단일 실행을 만들 수 없을 때만 old test ID에서 successor probe ID로의 원자적 migration을 연다.

완료 claim은 승인된 family에서 다음이 모두 증명될 때만 허용한다.

- 기존 contract, known-bad, protected mutation, fail-closed branch와 failure localization 손실 0
- route/denominator/required-validation/evidence binding의 dangling, stale 또는 dual-current identity 0
- hidden order dependency와 mutable-state contamination 0
- accepted before/after subject에서 expensive producer 및 eligible subprocess 실행 순감소
- accepted timing protocol에서 baseline noise로 설명되지 않는 targeted-family wall-time 순감소
- `adopted_family_union`에서 baseline이 0보다 큰 mandatory materialization/copy 축의 순감소
- exact terminal subject의 focused, exact-current, configured-current, historical, diagnostic/all, Lua syntax 및 Clean-Checkout Run A/B가 각 frozen route contract를 충족
- independent review와 owner seal의 별도 충족

이 계획은 선행 precision-preserving lightweighting의 scoped closeout을 재개방하지 않는다.

---

## 2. Scope

실행 순서는 다음과 같이 고정한다.

1. governance conflict lock 및 protected surface freeze
2. exact clean-checkout `S_base`, immutable `S_measure_tool`, eligible tooling review/`S_measure_gate`, measurement protocol 동결 및 `baseline_protocol_qualification` 수행; accepted before/after timing sample은 아직 만들지 않음
3. full execution census, producer/consumer attribution 및 isolation classification
4. contract preservation matrix와 scenario DAG 작성
5. 최소 scenario/report foundation 및 differential proof harness 구현
6. public-text Phase 7 current-route pilot 및 동일-session candidate qualification
7. pilot exit gate 통과 시에만 family별 admission, dry-run 및 transaction 설계
8. 각 admitted family의 implementation과 필요한 authority migration을 같은 atomic transaction으로 실행
9. `S_terminal` 동결 후 `S_base`와 함께 terminal `accepted_paired_measurement_session`에서 재측정하고 route validation, order/isolation 및 Clean-Checkout Run A/B 수행
10. independent review, owner seal, direct-child evidence-only `S_closeout_carrier`, durable evidence retrieval 및 governance closeout

Mandatory 범위는 다음과 같다.

- `baseline_protocol_qualification` subject/environment/command/input/repetition identity와 terminal `accepted_paired_measurement_session` identity
- configured test source와 exact taxonomy/current required-validation의 교집합 및 차집합 census
- test/node, producer, subprocess command signature, workspace, copy, read/parse/hash hotspot inventory
- 모든 in-scope test의 execution disposition, isolation requirement와 authority binding
- old test ID/contract/negative/failure signature에서 scenario/probe로의 preservation mapping
- `ScenarioContext`, `ExecutionResult`, `ProbeResult`, `ScenarioReport`의 최소 test-support contract
- report schema와 missing/malformed/stale/dependency/route-contamination negative tests
- public-text Phase 7 producer의 before/after invocation 및 timing proof
- family별 `adopted | must_isolate | deferred | no_material_benefit` disposition
- exact terminal subject에서 route별 validation, Clean-Checkout Run A/B와 review/owner seal, carrier checkout이 아닌 `S_terminal` replay

### Roadmap Conflict Locks

| Conflict | Adopted decision | Repository basis |
|---|---|---|
| C1 Classification | `primary_execution_disposition`과 `authority_bound`를 직교 축으로 둔다. `must_isolate`는 primary disposition 안에서 다른 실행 최적화보다 우선한다. `standalone_process_required`, `mutable_workspace_required` 같은 제약은 별도 constraint list에 기록한다. | 현행 `round3_pytest_source_classification.json`은 route/source 분류이고, exact taxonomy와 required-validation은 별도 authority다. 한 축으로 합치면 `current + shared_execution`, `cli_boundary + authority_bound` 같은 실제 복합 상태를 잃는다. |
| C2 Authority migration timing | dry-run/parity proof 뒤, 각 family의 implementation과 identity/taxonomy/denominator/required-validation/evidence mapping 변경을 같은 atomic transaction으로 적용한다. Half-state commit은 허용하지 않는다. | `ARCHITECTURE.md` §8-15가 workflow integration의 required-validation/taxonomy/source-policy identity 원자 이관을 요구한다. |
| C3 Persistent cache | persistent cross-run result cache는 명시적으로 out of scope다. reuse는 단일 scenario/class/run에 결속된 immutable result로 제한한다. | 현재 요구는 같은 execution graph 안의 중복 제거이며, cross-run freshness/eviction authority를 추가할 근거가 없다. |
| C4 Cost threshold | strict reduction denominator를 mandatory pilot과 최종 `adopted` family의 합집합인 `adopted_family_union`으로 고정한다. 그 집합에서 terminal accepted paired session A arm의 baseline이 0보다 큰 wall time, producer, subprocess, temporary workspace/materialization 및 copied bytes 축은 strict aggregate reduction 대상이다. 0 baseline은 `NOT_APPLICABLE`이며 감축으로 세지 않는다. Configured route 전체는 별도 performance observation/no-regression 축이고, strict improvement가 입증될 때만 configured-route execution improvement를 추가 claim한다. | 선택적 family adoption과 honest `must_isolate | deferred | no_material_benefit` disposition을 보존하면서 `DECISIONS.md`와 `ARCHITECTURE.md` §8-15의 cost evidence 요구를 claim 범위에 정확히 결속한다. |

### Measurement Tooling Identity Lock

`S_base`에는 이 successor의 신규 measurement harness가 존재하지 않을 수 있으므로 measurement tooling identity를 target subject identity와 분리한다.

```text
S_measure_tool
= adopted plan과 measurement/comparability tooling만 포함하고
  application test consolidation/authority migration을 포함하지 않는
  reviewed immutable plan-infrastructure tooling subject

measurement_tooling_identity
= runtime-resolved S_measure_tool commit/tree
 + measurement CLI schema/version
 + exact tool/dependency path set
 + Git blob IDs
 + raw SHA-256 set
 + dependency-manifest SHA-256
 + harness_interpreter_identity
 + target_execution_interpreter_identity
 + environment identity

measurement_protocol_identity
= measurement_contract schema/version
 + measurement_contract Git blob ID
 + measurement_contract raw SHA-256
 + canonical contract path
```

`S_measure_tool`은 `S_base`와 `S_terminal` checkout 밖의 별도 read-only tooling checkout/root에 materialize한다. 동일 harness가 `--target-repository <subject-checkout>`과 external result root를 인자로 받아 두 arm을 실행한다. Before/after receipt의 `measurement_tooling_identity`와 qualification/candidate/terminal receipt의 `measurement_protocol_identity`는 각각 byte-for-byte 동일해야 한다. Qualification 뒤 tool/dependency/CLI schema 또는 `measurement_contract.json` bytes가 바뀌면 이전 qualification과 candidate/terminal session을 폐기하고 새 identity로 tooling review, protocol qualification 및 paired before/after를 다시 수행한다.

`S_base`는 `S_measure_tool`의 ancestor여야 하며 `S_base..S_measure_tool` delta는 adopted plan, successor measurement/comparability tooling, tests와 그 manifest/schema에 한정한다. Pilot/application test, production/build producer, route taxonomy나 required-validation 변경이 하나라도 포함되면 tooling subject qualification은 FAIL이다.

Measurement command는 target checkout을 수정하거나 target producer에 instrumentation seam을 추가하지 않는다. External observation만으로 required metric을 얻을 수 없으면 그 metric은 `unobserved`이며, required acceptance를 판정할 수 없으면 implementation을 강행하지 않고 `BLOCKED`로 처분한다. 범위를 축소하려면 owner가 successor measurement contract와 touch surface를 승인한 뒤 protocol qualification과 terminal accepted paired session을 모두 새로 수행해야 한다.

### Measurement Session Lifecycle Lock

`S_base` 존재만으로 accepted performance baseline이 만들어졌다고 보지 않는다. 측정 lifecycle은 다음 세 artifact와 용도로 분리한다.

```text
baseline_protocol_qualification
= Change 1의 S_base-only Q/Q 반복
+ harness determinism, counter inventory, command signature, observation coverage 검증
+ configured-route detection ceiling 사전 계산
- accepted A/B timing 또는 reduction claim 근거

candidate_paired_qualification_session
= S_base + immutable S_candidate를 같은 session에 materialize한 A/B interleave
+ pilot exit/family material-benefit admission 근거
- terminal closeout timing 또는 final denominator baseline

accepted_paired_measurement_session
= Change 7에서 S_base + S_terminal을 첫 warm-up 전에 함께 materialize
+ 하나의 session_id/tool/environment 아래 warm-up과 모든 A/B measured block 실행
+ accepted before/after timing, final cost-axis baseline 및 closeout claim의 유일한 근거
```

Change 1의 `baseline_protocol_qualification` sample은 terminal A arm으로 재사용하지 않는다. Change 5/6의 candidate qualification sample도 terminal sample과 이어 붙이지 않는다. Accepted session의 A/B sample은 같은 session에서만 pair가 되며, arm 하나의 invalid/timeout/tool drift/target drift가 발생하면 유효 block을 다른 session에 보존·이식하지 않고 새 session에서 두 arm 전체를 다시 수집한다.

`measure_execution_cost.py`는 `--contract` 경로 문자열만 기록하지 않고 시작 시 contract bytes를 한 번 읽어 `measurement_protocol_identity`를 계산한다. 그 immutable in-memory snapshot으로 schedule/acceptance를 실행하고 종료 시 path의 raw hash를 다시 검사한다. Pre/post hash drift는 session FAIL이다. `baseline_protocol_qualification_receipt.json`, 모든 candidate receipt, `accepted_paired_measurement_summary.json`, comparability raw/carrier와 `cost_denominator_manifest.json`은 이 identity를 필수로 기록한다.

### Measurement Tooling Review Gate

Application mutation 전에 exact `S_measure_tool`에 대한 external immutable `measurement_tooling_review.json`과 tracked `measurement_tooling_review_pointer.json`이 필요하다. Review JSON을 reviewed commit에 넣는 self-reference를 피하기 위해 review는 owner-managed durable root에 생성하고, exact hash/pointer만 다음 plan-infrastructure-only `S_measure_gate` commit에 기록한다. 기존 plan review는 exact tooling commit/tree, tooling manifest hash, `S_base..S_measure_tool` diff scope와 아래 attestation을 모두 결속한 경우에만 이 gate를 대체할 수 있다.

```text
reviewed_tooling_commit_tree = exact S_measure_tool
reviewed_measurement_tooling_manifest = exact hash
reviewed_measurement_protocol_identity = exact measurement_contract identity
authored_roadmap = false
authored_plan = false
implemented_measurement_tooling = false
implemented_candidate = false
issued_owner_seal = false
verdict = PASS
```

Reviewer는 roadmap/plan 공동 작성자, measurement/comparability tooling 작성자, candidate implementer 또는 owner-seal issuer와 달라야 한다. External review 또는 tracked pointer 누락, raw hash retrieval 실패, identity 불일치, eligibility 위반 또는 `verdict != PASS`이면 application mutation과 candidate session을 열지 않는다. Terminal independent review와는 별도 artifact/gate이며, 같은 reviewer를 재사용하더라도 각 시점의 eligibility와 exact subject 결속을 다시 증명해야 한다.

### Cost Denominator Lock

서로 다른 denominator를 다음처럼 분리한다.

```text
census_universe
= 조사 대상 configured/exact/required test 전체

disposition_denominator
= census에서 candidate로 식별된 모든 family

strict_reduction_denominator
= mandatory pilot + final adopted family union

configured_route_performance_observation
= configured-current route 전체
```

- `must_isolate`, `deferred`, `no_material_benefit` family는 disposition denominator에는 남지만 strict reduction denominator에는 포함하지 않는다.
- 해당 family를 `complete` 수치 충족만을 위해 수정하거나 isolation/contract를 약화하지 않는다.
- `adopted_family_union`의 axis별 accepted baseline은 Change 7 `accepted_paired_measurement_session`의 A arm에서만 가져온다. Qualification/과거 session 값을 final denominator에 이식하지 않는다.
- `adopted_family_union`의 nonzero mandatory cost axis가 strict reduction을 충족하고 configured route wall time이 predeclared detection ceiling 이상의 regression을 보이지 않아야 scoped `complete`가 가능하다.
- Configured route 전체 wall-time strict reduction이 증명되지 않으면 scoped family completion은 가능하지만 `configured-current execution improved` claim은 금지한다.
- Configured route가 noise를 넘어 regression하면 family-local 개선이 있어도 closeout은 최대 `partial`이다.

### R1 Review Feedback Resolution

| Review ID | Adopted revision |
|---|---|
| C1 | `S_measure_tool`과 `measurement_tooling_identity`를 target subject에서 분리하고 동일 external harness로 before/after를 실행한다. |
| C2 | frozen touch surface, changed-path containment, tool/environment/command/input equality와 contract-denominator equivalence의 conjunctive comparability function을 추가한다. |
| C3 | strict reduction denominator를 mandatory pilot + final `adopted_family_union`으로 고정하고 configured route performance observation을 분리한다. |
| I1 | Roadmap/plan 공동 작성자, implementer와 owner-seal issuer를 independent-review credit에서 제외한다. |
| I2 | Pilot identity-preserving branch A와 successor scenario branch B의 acceptance/localization 기준을 분리한다. |
| I3 | `deterministic_core`와 volatile `execution_observations`, exact `normalization_excluded_fields`를 정의한다. |
| I4 | A/B arm, alternating block, adjacent pairing, delta sign, bootstrap seed/algorithm과 invalid sample disposition을 freeze한다. |
| I5 | Change 5를 mutation 없는 admission/dry-run, Change 6을 implementation+authority single transaction으로 정렬한다. |
| I6 | 최초 real authority-bound family에 별도 migration qualification gate를 둔다. |
| I7 | Production/build producer instrumentation seam을 금지하고 외부 관측 불충분 시 BLOCKED로 처분한다. |
| Minor | Deferred reason binding, owner-approved ClaimId, successor package 필요성, table-driven case attribution 및 route-validation/measurement 분리를 명시한다. |

### R2 Review Feedback Resolution

| Review ID | Adopted revision |
|---|---|
| R2-C1 | Change 1의 `baseline_protocol_qualification`과 Change 7의 `accepted_paired_measurement_session`을 분리하고 cross-session sample stitching을 금지한다. |
| R2-I1 | Exact `S_measure_tool` review의 reviewer eligibility, artifact identity, PASS verdict와 application-mutation blocking semantics를 명시한다. |
| R2-I2 | 신규 tracked Python source의 configured source-policy 영향 보고서를 Change 1에서 만들고 실제 discovery membership에 따라 `not_applicable` 또는 owner-approved additive transaction으로 처분한다. |
| R2-I3 | Configured route를 arm당 20 measured sample로 늘리고 S_base-only noise calibration으로 최소 검출 regression ceiling을 사전 고정·공개한다. |
| R2-M1 | Generated Artifacts의 중복 `round_identity.json`을 제거한다. |
| R2-SELF-1 | 자체 발견 항목인 `configured_route_observation`을 `configured_route_performance_observation`으로 명확화한다. |
| R2-M2 | Tracked comparability report를 external raw report의 hash-bound carrier/summary로 정의한다. |
| R2-M3 | Harness interpreter와 target execution interpreter identity를 분리한다. |
| R2-M4 | `S_impl`과 `S_preterminal`을 chronology label로만 정의하고 gate identity로 사용하지 않는다. |
| R2-M5 | Governance docs를 touch-surface의 `evidence_governance` role에 결속한다. |

### R3 Review Feedback Resolution

| Review ID | Adopted revision |
|---|---|
| R3-I1 | `measurement_protocol_identity`를 정의해 qualification/candidate/terminal receipt와 comparability conjunction/CLI에 결속한다. |
| R3-I2 | Final family 수를 열거하지 않고 stable family-order resolver와 family당 5 measured block의 파라미터화 배분 규칙을 봉인한다. |
| R3-4.1 | `S_terminal -> validation/measurement/review -> S_closeout_carrier` chronology와 carrier non-subject 규칙을 명시한다. |
| R3-4.2 | Change 1 qualification과 Change 7 terminal source-policy revalidation tracked artifact 이름을 분리한다. |
| R3-M1 | R2 자체 발견 항목을 `R2-SELF-1`로 이동하고 원 검토 Minor 번호를 복원한다. |
| R3-M2 | Q/Q detection ceiling이 S_base null 조건에서 추정된다는 validation ceiling을 추가한다. |
| R3-M3 | Accepted session 예상 소요, worst-case timeout 및 전면 재수집 비용을 사전 산출·공개한다. |

### Explicitly Out Of Scope

- Iris production Lua, Browser, Wiki, Tooltip, facts, description 또는 user-visible text 변경
- producer의 production semantic behavior 변경
- current, historical, diagnostic 또는 Clean-Checkout route의 통합
- Registry, DVF, IAR, RTC, Publish Boundary 또는 runtime payload authority 재설계
- 모든 test를 하나의 giant scenario로 합치는 작업
- subprocess 또는 CLI boundary의 일괄 제거
- fresh-process/bootstrap, tamper, crash/recovery, rollback, concurrent-owner test의 격리 약화
- persistent cross-run cache, cache eviction, TTL 또는 distributed cache
- pytest node 수, test 파일 수 또는 assertion 수 자체를 목표로 한 감축
- sealed predecessor bundle, pointer, closeout, review 또는 owner seal rewrite
- PZ runtime 성능, FPS/frame-time, heap, latency, multiplayer 또는 long-session 개선
- release, package publication, Workshop, deployment 또는 B42 readiness
- external mod ecosystem 전체 compatibility sweep
- arbitrary percentage reduction quota
- census에서 material benefit이 입증되지 않은 family의 강제 migration

---

## 3. Non-Goals

- 선행 `Iris test precision-preserving lightweighting`의 baseline, result 또는 completion claim을 재계산하지 않는다.
- test body를 짧게 만들거나 helper로 옮겼다는 이유만으로 consolidation을 선언하지 않는다.
- current PASS로 historical/diagnostic raw result를 대체하거나 그 반대 방향으로 대체하지 않는다.
- diagnostic raw failure를 disposition만으로 PASS로 세탁하지 않는다.
- historical denominator를 successor current test에 맞춰 소급 확장하지 않는다.
- direct function call이 빠르다는 이유만으로 standalone CLI contract를 제거하지 않는다.
- producer early failure가 독립 probe 결과를 숨기도록 만들지 않는다.
- shared kernel을 semantic master validator 또는 새 governance authority로 만들지 않는다.
- test-only Python 구조를 Iris runtime에 포함하거나 JVM+Lua 혼용을 도입하지 않는다.
- predecessor evidence/tooling을 successor 재현 책임과 consumer migration proof 없이 삭제하지 않는다.
- static call-site count를 dynamic invocation count나 wall-time improvement로 해석하지 않는다.

---

## 4. Assumptions

### Authority Assumptions

- `docs/Philosophy.md`가 최상위 설계 권한이다.
- Iris는 근거 기반 정보 모드이고 PZ runtime은 100% Lua다.
- `docs/DECISIONS.md`, `docs/ARCHITECTURE.md` §8-15, `docs/ROADMAP.md` §16이 이 successor의 현재 방향을 승인한다.
- `docs/EXECUTION_CONTRACT.md`의 Heavy execution disclosure, evidence, validation ceiling과 closeout discipline을 적용한다.
- `Iris/_docs/round3/round3_test_taxonomy.json`은 exact route identity, `Iris/_docs/round3/round3_pytest_source_classification.json`은 configured source routing, `Iris/_docs/round3/current_route_required_validations.json`은 live current required-validation binding을 각각 소유한다.
- `Iris/_docs/round3/round3_run_contract_tests.py`의 exact-current route와 pytest `conftest.py`의 configured route는 서로 대체되지 않는다.
- `Iris/validation/clean_checkout/invoke_receipt_bound_full_gate.ps1`와 `invoke_deterministic_compare.ps1`가 terminal Clean-Checkout evidence의 authoritative entrypoint다.
- predecessor terminal subject/carrier/retrieval key는 append-only historical trace다.

### Current Codebase Readpoint

작성 시 read-only inspection에서 다음을 확인했다.

- `pytest.ini`의 default test path는 `Iris/build/description/v2/tests`와 `Iris/build/tests/test_evidence_pipeline_cross_track.py`다.
- 신규 `Iris/validation/test_workflow_consolidation/tests/`는 현재 default `testpaths` 밖이며, `Iris/build/description/v2/tests/conftest.py`의 controlled-source enumeration도 `Iris/build/description/v2/tests/test_*.py`와 manifest에 명시된 auxiliary source에 한정된다. 따라서 신규 successor test의 현재 예상 source-policy disposition은 `not_applicable`이고 explicit-path supporting test로 실행한다.
- configured source policy는 tracked policy source `115`개와 approval 당시 clean-checkout-absent policy source `183`개를 별도 count/hash로 결속한다.
- `round3_run_contract_tests.py --class current --enforce-current-build-closure --list`는 작성 readpoint에서 exit `0`, 219개 exact-current test를 열거했다.
- `test_public_text_quality_acceptance_current_route.py`는 source classification상 `current`지만 exact-current 219개 list와 `current_route_required_validations.json`의 required test에는 포함되지 않는다. 따라서 pilot은 configured-current identity를 건드리지만 exact-current/required-validation migration은 현재 관측상 `NOT_APPLICABLE`이다. 실행 시 live recensus로 다시 확인한다.
- pilot 파일은 277 lines, 11 test methods, 8개 static `subprocess.run` site를 가진다.
- 앞 4개 test가 `_phase7_self_test()`를 각각 호출하며, helper는 같은 Python executable, validator path, attempt ID, `--self-test`, `--no-write`, cwd와 output contract로 실행된다.
- 해당 producer는 `validate_public_text_quality_acceptance_official_0005_phase7_v2.py`를 통해 `run_focused_schema_tests()`를 호출하고 4개 case를 하나의 JSON payload로 이미 반환한다.
- pilot file 단독 configured collection은 11개 node를 수집했다.
- working readpoint의 configured test subtree에 대한 정적 검색은 subprocess/temp/copy 계열 342 occurrences를 91개 파일에서 찾았다. 세부값은 subprocess/Popen 153, `TemporaryDirectory`/`mkdtemp` 149, copy 계열 40이다. 이 값은 후보 census이며 accepted dynamic baseline이 아니다.
- 후속 후보의 실재 파일로 `test_runtime_payload_state_integrity*.py`, `test_artifact_lifecycle_{inventory,executor,promotion}.py`, `test_dvf_3_3_registry_authority_canonical_closure.py` 및 registry-runtime family가 있다.
- artifact lifecycle과 registry authority tests에는 temp workspace, copy, subprocess, tamper/recovery state가 함께 있으므로 automatic consolidation 대상이 아니다.
- `Iris/validation/test_lightweighting/`에는 선행 inventory, protection, precision, dominance, identity migration, localization 및 terminal retrieval tooling이 있다. 이 tooling은 predecessor claim을 재현하므로 successor가 수정하지 않고 read-only input/behavior reference로 우선 재사용한다.
- `validate_terminal_evidence_bundle.py`는 `fresh-root-v1`과 `carrier-aware-v2`를 지원한다.

새 `test_workflow_consolidation` package가 필요한 이유는 predecessor tooling이 node/LOC, protection, precision, identity migration과 terminal retrieval을 소유하지만 dynamic producer/subprocess/materialization census, subject-independent measurement harness, ScenarioReport validation 및 baseline/terminal comparability 판정을 제공하지 않기 때문이다. Predecessor package에 이 책임을 추가하면 sealed closeout 재현 도구의 identity와 scope를 불필요하게 바꾸므로 successor package로 격리한다.

작성 중 수행한 producer 진단은 동일 no-write command 5회 모두 exit `0`, `status=PASS`, `case_count=4`였고 elapsed time은 약 `4173, 382, 367, 679, 494 ms`였다. 이 값은 cold/warm 편차와 실행 비용의 존재만 보여 주는 working-overlay diagnostic이다. clean-checkout subject, pinned environment, interleaved before/after protocol이 없으므로 accepted timing baseline이나 개선 claim에 사용하지 않는다.

### New Tracked Source-Policy Impact Lock

Change 1은 provisional tracked-index에서 사전 점검하고 exact immutable `S_measure_tool` checkout에서 각 신규 `test_*.py`의 canonical `source_policy_qualification_report.json`을 실제 collection으로 확정한다.

```text
source_file
default_pytest_discovery_member
round3_controlled_source_member
explicit_path_only
source_policy_disposition = current | historical | diagnostic | not_applicable | BLOCKED
authority_transaction_required
evidence_command_and_receipt
```

현재 코드 경계에서는 `Iris/validation/test_workflow_consolidation/tests/`가 default/configured denominator 밖이므로 `not_applicable + explicit_path_only=true`가 예상값이다. 이 정적 예상은 실행 증거를 대체하지 않는다. 실제 tracked-index collection에서 membership이 `true`이면 현재 `S_measure_tool`의 no-authority-delta qualification과 충돌하므로 임의 JSON row 추가나 Change 6까지의 지연 등록을 금지하고 `BLOCKED`로 닫는다. 진행하려면 owner가 별도 additive source-registration transaction, source-set count/hash, denominator receipt, touch-surface amendment와 plan revision을 승인해야 한다. 기존 controlled test source를 이동·대체하는 admitted family는 Change 6의 해당 identity/authority transaction에서 처리한다.

### Environment and Subject Assumptions

- 모든 authoritative 명령은 Windows PowerShell에서 실행한다.
- Harness Python은 external tooling checkout의 `harness_interpreter_identity`, target command Python은 각 checkout의 `target_execution_interpreter_identity`로 별도 기록한다. 둘 중 어느 identity라도 arm 사이에서 달라지면 comparison은 FAIL이다.
- accepted before/after는 같은 `accepted_paired_measurement_session` 안에서 같은 physical machine, OS, 두 interpreter identity, locale, environment contract, command, input identity와 repository-external root policy를 사용한다.
- authoring worktree에는 사용자 변경이 존재하므로 commit `671c7b...` 및 위 diagnostic 값은 accepted `S_base`가 아니다.
- `S_base`는 owner가 선택한 immutable commit/tree의 clean disposable checkout에서 새로 동결한다.
- `S_measure_tool`은 `S_base`와 별개인 immutable plan-infrastructure subject이며 application test consolidation을 포함하지 않는다.
- `S_measure_tool`의 별도 read-only external checkout에서 동일 measurement harness를 실행해 `S_base`와 `S_terminal`을 target으로 측정한다.
- raw traces, timing samples, checkout, temp, pycache와 result roots는 repository 밖에 둔다. Repository에는 compact schema/manifest/ledger/pointer만 추적한다.
- `baseline_protocol_qualification` 첫 실행 전에 repetition/warm-up/interleave/outlier/acceptance protocol과 configured-route regression margin/power algorithm을 hash-bound contract로 고정한다.
- 단일 timing run은 성능 claim 근거가 아니다.

### Classification Contract

각 in-scope test/node row는 최소 다음 필드를 가진다.

```text
test_id
source_file
route
primary_execution_disposition
authority_bound
execution_constraints[]
producer_ids[]
command_signatures[]
input_identity
workspace_ownership
mutable_state_dependency
contract_ids[]
negative_case_ids[]
failure_signature
scenario_candidate
probe_id
disposition_reason
deferred_reason_code
deferred_evidence_refs[]
deferred_owner
deferred_reentry_condition
```

`primary_execution_disposition` 값은 다음으로 제한한다.

```text
shared_execution
dependent_scenario
table_driven
direct_function_candidate
cli_boundary
must_isolate
obsolete_or_redundant
```

CLI가 contract이면서 동일 producer reuse 후보인 경우 primary는 실제 최적화 disposition인 `shared_execution`, constraint에는 `standalone_process_required`를 기록한다. Tamper/crash/recovery/fresh-process가 contract이면 `must_isolate`가 우선한다.

### Measurement Contract

- 모든 before/after sample은 동일 `measurement_tooling_identity`를 가진 external `S_measure_tool` harness가 target checkout을 인자로 받아 하나의 paired session 안에서 실행한다.
- Q/Q qualification, candidate session과 terminal accepted session은 같은 `measurement_protocol_identity`를 기록한다. Contract path가 같아도 raw SHA-256 또는 Git blob이 다르면 동일 protocol이 아니다.
- tool commit/tree, tool/dependency blob/raw SHA, CLI schema, harness interpreter, target execution interpreter와 environment 중 하나라도 arm 사이에서 다르면 `tooling_identity_equal=false` 또는 `execution_interpreter_identity_equal=false`이고 comparison은 FAIL이다.
- command signature는 executable identity, ordered argv, cwd contract, relevant environment contract, canonical input hashes와 expected output contract를 포함한다.
- 같은 executable이라도 input/environment/output contract가 다르면 duplicate로 세지 않는다.
- Qualification-only Q/Q run은 두 target 모두 `S_base`이고 A/B improvement sample로 분류하지 않는다. Paired timing arm은 `A=before(S_base)`, `B=after(S_candidate)` 또는 terminal accepted session의 `B=after(S_terminal)`로 고정한다.
- warm-up은 arm당 2회이며 `A-B-B-A` 1 block으로 실행하고 통계에서 제외한다.
- Pilot과 각 candidate/adopted family targeted timing은 family당 5 measured block을 사용해 arm당 10회를 수집하고, configured-current route timing은 10 measured block을 사용해 arm당 20회를 수집한다.
- Change 1 contract는 future family ID를 열거하지 않고 파라미터화 규칙을 봉인한다. Change 6 종료 후 final ledger에서 `adopted`이며 mandatory pilot이 아닌 stable `family_id`를 ordinal sort한 수를 `N_adopted_nonpilot`로 해소한다. Accepted session workload order는 `mandatory_pilot -> sorted adopted non-pilot families -> configured-current`다.
- Accepted session measured-block budget은 `5 + (5 * N_adopted_nonpilot) + 10`, measured command position은 그 값의 4배다. 각 workload에는 별도의 `A-B-B-A` warm-up 1 block을 배정하므로 전체 warm-up position은 `4 * (N_adopted_nonpilot + 2)`, 전체 expected execution position은 `24 * N_adopted_nonpilot + 68`이다. Family 수가 0이어도 pilot 5와 configured route 10은 유지한다.
- Orchestrator는 first warm-up 전에 final family ledger hash, stable family order, workload별 block/sample count, total position formula와 `measurement_protocol_identity`를 `accepted_session_schedule.json`에 기록한다. Rule 불일치, duplicate/missing adopted family 또는 runtime block-count 재량은 session preflight FAIL이다.
- measured block 순서는 `A-B-B-A`, `B-A-A-B`를 번갈아 사용한다. 각 block의 position `1↔2`, `3↔4`를 인접 cross-arm pair로 결속한다.
- paired delta는 항상 `A_elapsed - B_elapsed`다. 양수는 after improvement, 0은 no change, 음수는 regression을 뜻한다.
- raw sample, exit code, stdout/stderr hash, start order, machine/environment identity, Git subject와 post-run status를 기록한다.
- timeout/nonzero/contract-invalid sample은 삭제하거나 outlier로 버리지 않고 block failure로 기록한다. 사후 outlier 제거는 금지한다.
- wall-time acceptance는 after median이 before median보다 작고, frozen seed/algorithm으로 paired delta를 resample한 bootstrap 95% confidence interval lower bound가 0보다 클 때만 `improved_beyond_observed_noise=true`로 판정한다.
- Configured route no-regression은 Change 1 Q/Q noise calibration에서 고정 seed와 10,000회 paired bootstrap simulation, one-sided alpha `0.05`, power `0.80`으로 계산한 `minimum_detectable_regression_ms/pct`를 공개한다. Owner가 B 결과를 보기 전에 `maximum_acceptable_regression_ms/pct`를 봉인하며, detection ceiling이 이 margin보다 크면 sample block을 늘려 qualification을 다시 수행하고 그렇지 못하면 `UNDERPOWERED/BLOCKED`다. Terminal에서는 paired `B_elapsed-A_elapsed`의 one-sided 95% upper bound가 frozen maximum acceptable margin 미만일 때만 material no-regression gate를 통과한다.
- invocation/materialization/copy count는 exact integer delta로 판정한다. 계측 범위 밖 child-process 내부 I/O는 `unobserved`로 남기며 0으로 세지 않는다.
- instrumentation overhead는 no-instrumentation companion run으로 측정하고 별도 축으로 공개한다.
- route validation과 route measurement는 별개다. Route contract PASS는 cost improvement evidence가 아니고, route timing improvement는 route semantic PASS를 대체하지 않는다.

### Baseline/Terminal Comparability Contract

`S_base`와 `S_terminal`이 둘 다 clean이라는 사실만으로 performance delta를 이 round에 귀속하지 않는다. `validate_measurement_comparability.py`는 다음 conjunction으로 `comparability_verdict`를 계산한다.

```text
base_is_ancestor_of_terminal = true
measurement_tooling_identity_equal = true
measurement_contract_identity_equal_across_qualification_and_accepted_session = true
machine_environment_locale_equal = true
accepted_paired_session_single_session = true
harness_interpreter_identity_equal = true
target_execution_interpreter_identity_equal = true
command_and_input_contract_equal = true
contract_denominator_equivalent_via_preservation_map = true
accepted_session_schedule_matches_parameterized_contract_and_final_family_ledger = true
declared_round_touch_surface_frozen_before_protocol_qualification = true
S_base_to_S_terminal_changed_paths_subset_of_declared_touch_surface = true
out_of_scope_path_count = 0
```

`declared_round_touch_surface.json`은 protocol qualification 전에 exact path와 bounded prefix, role(`plan_infrastructure | application | authority_transaction | evidence | evidence_governance`) 및 conditional admission rule을 봉인한다. `DECISIONS.md`, `ROADMAP.md`, 조건부 `ARCHITECTURE.md` closeout delta는 `evidence_governance` role이다. `git diff --name-status --find-renames S_base S_terminal`의 모든 changed path가 이 manifest에 설명돼야 한다. Test node 변화는 contract preservation/identity transaction으로 denominator equivalence를 증명하며 단순 node equality를 요구하지 않는다.

Out-of-scope change가 하나라도 있으면 다음 중 하나만 허용한다.

1. unrelated change를 포함한 새 clean predecessor에 round transaction을 재적용해 `S_base'`/`S_terminal'`을 만들고 동일 tool로 before/after를 전부 재측정한다.
2. 분리가 불가능하면 aggregate 및 route wall-time을 `UNATTRIBUTABLE`로 기록하고 performance/scoped-complete claim을 차단한다.

Out-of-scope path를 사후 allowlist로 넓혀 기존 baseline을 살리는 것은 금지한다.

---

## 5. Repository Areas Affected

아래는 최대 예상 touch surface다. Census 또는 admission gate에서 `must_isolate`, `deferred`, `no_material_benefit`로 닫힌 family는 수정하지 않는다.

### Code

- `Iris/build/description/v2/tests/test_public_text_quality_acceptance_current_route.py` — mandatory pilot
- `Iris/build/description/v2/tools/build/validate_public_text_quality_acceptance_official_0005_phase7_v2.py` — CLI/output contract reference, read-only protected producer
- `Iris/build/description/v2/tools/build/public_text_quality_acceptance_official_0005_phase7_v2.py` — producer semantics reference, read-only protected producer
- `Iris/validation/test_workflow_consolidation/__init__.py` — new successor package
- `Iris/validation/test_workflow_consolidation/scenario_contracts.py` — minimal immutable scenario/result/probe/report types
- `Iris/validation/test_workflow_consolidation/validate_scenario_report.py` — schema/dependency/identity fail-closed validator
- `Iris/validation/test_workflow_consolidation/collect_execution_census.py` — static/dynamic execution census collector
- `Iris/validation/test_workflow_consolidation/classify_source_policy_impact.py` — 신규 tracked source의 configured/controlled membership 판정
- `Iris/validation/test_workflow_consolidation/measure_execution_cost.py` — command/timing/counter receipt producer
- `Iris/validation/test_workflow_consolidation/validate_measurement_comparability.py` — subject delta/tool identity/denominator comparability 판정
- `Iris/validation/test_workflow_consolidation/compare_contract_parity.py` — old contract/negative/localization parity checker
- `Iris/validation/test_workflow_consolidation/validate_identity_transaction.py` — taxonomy/denominator/required/evidence atomic migration checker
- `Iris/validation/test_workflow_consolidation/validate_workflow_closeout_carrier.py` — successor post-terminal allowed-delta/carrier DAG checker
- `Iris/validation/test_workflow_consolidation/tests/` — scenario/report/census/measurement/migration positive and negative tests
- `Iris/validation/test_lightweighting/` — read-only predecessor evidence/tooling reference
- `Iris/validation/clean_checkout/` — existing terminal runner/wrapper reuse; new successor receipt field가 실제로 필요할 때만 additive change
- admitted family의 existing test/helper files — conditional

Conditional candidate files는 최소 다음을 포함한다.

- `Iris/build/description/v2/tests/test_runtime_payload_state_integrity.py`
- `Iris/build/description/v2/tests/test_runtime_payload_state_integrity_residual_seal.py`
- `Iris/build/description/v2/tests/test_artifact_lifecycle_inventory.py`
- `Iris/build/description/v2/tests/test_artifact_lifecycle_executor.py`
- `Iris/build/description/v2/tests/test_artifact_lifecycle_promotion.py`
- `Iris/build/description/v2/tests/test_dvf_3_3_registry_authority_canonical_closure.py`
- `Iris/build/description/v2/tests/test_dvf_3_3_registry_runtime_compatibility_*.py`

### Docs

- `docs/iris_test_validation_workflow_consolidation_execution_lightweighting_plan.md` — this plan
- `docs/DECISIONS.md` — terminal closeout 후 additive successor decision
- `docs/ARCHITECTURE.md` — 구현이 이미 채택된 §8-15 boundary를 정정/명확화해야 할 때만 additive update
- `docs/ROADMAP.md` — implementation/timing/review 상태 전환
- `docs/EXECUTION_CONTRACT.md` — read-only
- `docs/iris_test_precision_preserving_test_suite_lightweighting_plan.md` — read-only predecessor plan
- `docs/iris_test_lightweighting_terminal_closeout_recovery_plan.md` — read-only predecessor recovery plan

### Config

- `pytest.ini` — read-only by default; test discovery 변경이 필요한 경우 별도 justification과 denominator validation 필수
- `Iris/build/description/v2/tests/conftest.py` — route/denominator behavior read-only by default; successor scenario source registration이 필요한 경우 conditional atomic edit
- `Iris/_docs/round3/round3_pytest_source_classification.json` — conditional source classification/hash migration
- `Iris/_docs/round3/round3_full_discovery_denominator.json` — conditional denominator binding migration
- `Iris/_docs/round3/round3_test_taxonomy.json` — exact identity 변경 family에 한한 conditional migration
- `Iris/_docs/round3/current_route_required_validations.json` — required-bound identity 변경 family에 한한 conditional migration
- `Iris/_docs/round3/round3_active_core_closure.json` — read-only; convenience import expansion 금지
- `Iris/validation/clean_checkout/contracts/full_repository_gate.json` — permanent gate admission이 별도 승인된 경우에만 conditional

### Generated Artifacts

새 successor evidence root는 predecessor와 분리한다.

- `Iris/_docs/refactor/test_workflow_consolidation/baseline_subject_manifest.json`
- `Iris/_docs/refactor/test_workflow_consolidation/measurement_tooling_manifest.json`
- `Iris/_docs/refactor/test_workflow_consolidation/measurement_tooling_review_pointer.json`
- `Iris/_docs/refactor/test_workflow_consolidation/measurement_contract.json`
- `Iris/_docs/refactor/test_workflow_consolidation/baseline_protocol_qualification_receipt.json`
- `Iris/_docs/refactor/test_workflow_consolidation/source_policy_qualification_report.json`
- `Iris/_docs/refactor/test_workflow_consolidation/terminal_source_policy_revalidation_report.json`
- `Iris/_docs/refactor/test_workflow_consolidation/declared_round_touch_surface.json`
- `Iris/_docs/refactor/test_workflow_consolidation/test_identity_census.jsonl`
- `Iris/_docs/refactor/test_workflow_consolidation/execution_census.jsonl`
- `Iris/_docs/refactor/test_workflow_consolidation/duplication_ledger.jsonl`
- `Iris/_docs/refactor/test_workflow_consolidation/classification_ledger.jsonl`
- `Iris/_docs/refactor/test_workflow_consolidation/contract_preservation_matrix.jsonl`
- `Iris/_docs/refactor/test_workflow_consolidation/scenario_dag.json`
- `Iris/_docs/refactor/test_workflow_consolidation/pilot_receipt.json`
- `Iris/_docs/refactor/test_workflow_consolidation/family_disposition_ledger.jsonl`
- `Iris/_docs/refactor/test_workflow_consolidation/identity_transactions.jsonl`
- `Iris/_docs/refactor/test_workflow_consolidation/round_identity.json`
- `Iris/_docs/refactor/test_workflow_consolidation/terminal_comparison.json`
- `Iris/_docs/refactor/test_workflow_consolidation/measurement_comparability_report.json`
- `Iris/_docs/refactor/test_workflow_consolidation/cost_denominator_manifest.json`
- `Iris/_docs/refactor/test_workflow_consolidation/accepted_paired_measurement_summary.json`
- `Iris/_docs/refactor/test_workflow_consolidation/accepted_session_schedule.json`
- `Iris/_docs/refactor/test_workflow_consolidation/accepted_session_resource_estimate.json`
- `Iris/_docs/refactor/test_workflow_consolidation/terminal_validation_manifest.json`
- `Iris/_docs/refactor/test_workflow_consolidation/independent_review.json`
- `Iris/_docs/refactor/test_workflow_consolidation/owner_seal.json`
- `Iris/_docs/refactor/test_workflow_consolidation/workflow_closeout_carrier_manifest.json`
- `Iris/_docs/refactor/test_workflow_consolidation/terminal_evidence_pointer.json`

`baseline_subject_manifest.json`부터 final family ledger/identity transaction까지 protocol/application/authority input artifact는 `S_terminal` ancestry에 존재한다. 반면 terminal measurement/validation/review 뒤에만 확정 가능한 `terminal_comparison.json`, `accepted_paired_measurement_summary.json`, `accepted_session_schedule.json`, `accepted_session_resource_estimate.json`, `measurement_comparability_report.json`, `cost_denominator_manifest.json`, `terminal_validation_manifest.json`, `terminal_source_policy_revalidation_report.json`, `independent_review.json`, `owner_seal.json`, `terminal_evidence_pointer.json`과 carrier manifest는 `S_closeout_carrier`의 exact allowlisted post-terminal evidence delta다.

Raw timing samples, profiler/event traces, stdout/stderr, disposable checkout and large report bundles는 owner-managed repository-external durable root에 둔다. External `measurement-comparability.json`이 canonical raw comparability report이고 tracked `measurement_comparability_report.json`은 그 exact raw SHA-256, schema, subject/session/protocol identity, deterministic verdict projection과 durable retrieval pointer를 가진 carrier/summary다. 둘의 verdict/identity projection이 다르거나 raw hash retrieval이 실패하면 comparability는 FAIL이다. 다른 tracked artifact도 raw data의 hash, schema, subject, command와 retrieval pointer만 가진다.

---

## 6. Planned Changes

### Change 1 — Immutable measurement tooling, review gate and protocol qualification

Purpose:

Implementation 전에 subject-independent measurement tooling, its independent review, roadmap conflict, predecessor boundary, exact subject와 measurement/comparability protocol을 fail-closed로 고정하고 S_base-only qualification을 수행한다. 이 단계는 accepted A/B performance baseline을 만들지 않는다.

Files:

- `docs/iris_test_validation_workflow_consolidation_execution_lightweighting_plan.md`
- `Iris/_docs/refactor/test_workflow_consolidation/baseline_subject_manifest.json`
- `Iris/_docs/refactor/test_workflow_consolidation/measurement_tooling_manifest.json`
- `Iris/_docs/refactor/test_workflow_consolidation/measurement_tooling_review_pointer.json`
- `Iris/_docs/refactor/test_workflow_consolidation/measurement_contract.json`
- `Iris/_docs/refactor/test_workflow_consolidation/baseline_protocol_qualification_receipt.json`
- `Iris/_docs/refactor/test_workflow_consolidation/source_policy_qualification_report.json`
- `Iris/_docs/refactor/test_workflow_consolidation/declared_round_touch_surface.json`
- `Iris/_docs/refactor/test_workflow_consolidation/protected_surface_manifest.json`
- `Iris/validation/test_workflow_consolidation/measure_execution_cost.py`
- `Iris/validation/test_workflow_consolidation/classify_source_policy_impact.py`
- `Iris/validation/test_workflow_consolidation/validate_measurement_comparability.py`
- `Iris/validation/test_workflow_consolidation/tests/test_measure_execution_cost.py`
- `Iris/validation/test_workflow_consolidation/tests/test_classify_source_policy_impact.py`
- `Iris/validation/test_workflow_consolidation/tests/test_validate_measurement_comparability.py`

Implementation Notes:

1. Application mutation 전에 adopted plan과 measurement/comparability tooling, tests 및 manifest/schema만 가진 immutable `S_measure_tool`을 만든다.
2. `measurement_tooling_manifest.json`에는 tool/dependency path, Git blob, raw SHA-256와 CLI schema를 결속한다. Self-reference를 피하기 위해 containing commit/tree를 manifest bytes 안에 넣지 않고, 실행 preflight가 clean tooling checkout의 HEAD commit/tree와 manifest hash를 해소해 external receipt의 `measurement_tooling_identity`에 결속한다. `measurement_contract.json`은 별도 `measurement_protocol_identity`로 raw SHA-256/Git blob/schema/path를 결속한다.
3. `S_measure_tool`을 target subject와 분리된 read-only external tooling checkout에 materialize하고 `S_base` 및 향후 `S_terminal` checkout을 argument로 받는다.
4. Owner-selected immutable clean commit/tree를 `S_base`로 pin한다. Authoring HEAD나 dirty working overlay를 자동 채택하지 않는다.
5. OS, PowerShell, Python/uv/pytest identity, locale, environment variables, CPU/power-state disclosure, canonical input hashes와 external root allocator identity를 기록한다.
6. Q/Q qualification 첫 실행 전에 warm-up, block/pairing, delta sign, bootstrap seed/algorithm, counter scope, noise adjudication, family당 block 배분 resolver, configured-route material regression margin/power target과 timeout을 `measurement_contract.json`에 봉인하고 raw `measurement_protocol_identity`를 계산한다.
7. 계획이 허용하는 exact path/prefix와 role을 `declared_round_touch_surface.json`에 protocol qualification 전에 봉인한다.
8. predecessor terminal/carrier/pointer/evidence bytes, production Lua와 public-text producer source를 protected surface로 기록한다.
9. Provisional tracked-index에서 사전 점검한 뒤 exact `S_measure_tool` checkout에서 신규 source의 default/configured discovery와 Round 3 controlled-source membership을 다시 수집해 canonical `source_policy_qualification_report.json`으로 닫는다. 예상 `not_applicable`과 다르면 source registration을 임의 수행하지 않고 BLOCKED다.
10. Configured collection, exact-current list, required-validation inventory 및 clean-checkout gate identity를 `S_base`에서 재수집한다.
11. Exact `S_measure_tool` commit/tree, manifest와 diff scope에 결속된 eligible reviewer의 external `measurement_tooling_review.json` PASS를 얻고 raw hash/retrieval pointer를 `measurement_tooling_review_pointer.json`에 준비한다. 이 gate 전에는 application test/helper mutation이나 candidate paired session을 열지 않는다.
12. `S_base`를 양쪽 target으로 쓰는 Q/Q `baseline_protocol_qualification`을 수행해 harness determinism, counter inventory, command signature와 observation coverage를 검증한다. 이 sample에 A/B label을 부여하거나 terminal before arm으로 보존하지 않는다.
13. Configured route는 arm-equivalent당 20 sample 기준 Q/Q noise calibration으로 minimum detectable regression을 계산한다. Detection ceiling이 owner-frozen maximum acceptable regression보다 크면 block 수를 늘려 contract를 다시 봉인·review하고 qualification을 반복하거나 BLOCKED로 닫는다. Review pointer, canonical source-policy report와 accepted qualification receipt를 plan-infrastructure-only `S_measure_gate`에 함께 봉인한 뒤에만 application mutation을 시작한다.
14. External process/pytest observation은 target checkout을 수정하지 않는 opt-in wrapper로만 수행한다. Production/build producer source에 timing/count용 sleep, log, write, hook 또는 instrumentation seam을 추가하지 않는다.
15. External observation이 child process 내부 operation을 관측하지 못하면 coverage field를 `parent_process_only` 또는 `unobserved`로 기록하고 그 내부 count를 0으로 추정하지 않는다. Required metric이 unobserved이면 해당 acceptance/claim은 BLOCKED다.

Validation:

- `S_base` commit/tree/clean status와 command hash 일치
- `S_measure_tool`에 application test/producer/authority migration delta 0
- eligible external `measurement_tooling_review.json` 및 tracked pointer의 exact identity/hash/verdict PASS
- tooling review/qualification receipt의 `measurement_protocol_identity`가 exact contract blob/raw SHA와 일치
- external tooling root와 target checkout의 disjointness
- S_base-only Q/Q protocol qualification repeated run exit `0`
- qualification sample이 accepted before/after inventory에 포함되지 않음
- same input에서 counter inventory와 command signature deterministic
- 신규 tracked source-policy impact가 `not_applicable`이거나 별도 owner-approved plan revision으로 닫힘
- configured-route `minimum_detectable_regression <= maximum_acceptable_regression`
- instrumentation on/off contract result parity
- protected surface pre/post hash delta 0
- qualification receipt missing field, wrong subject, dirty checkout, tool hash drift, environment drift와 reused result root rejection
- 동일 contract path의 bytes 교체, pre/post contract hash drift와 receipt protocol identity mismatch rejection
- changed path outside frozen touch surface의 comparability rejection

---

### Change 2 — Execution census, classification and contract preservation map

Purpose:

실제 중복 work와 must-isolate 경계를 관측하고, mutation 전에 모든 in-scope contract의 successor 위치를 결정한다.

Files:

- `Iris/validation/test_workflow_consolidation/collect_execution_census.py`
- `Iris/validation/test_workflow_consolidation/compare_contract_parity.py`
- `Iris/validation/test_workflow_consolidation/tests/test_collect_execution_census.py`
- `Iris/_docs/refactor/test_workflow_consolidation/test_identity_census.jsonl`
- `Iris/_docs/refactor/test_workflow_consolidation/execution_census.jsonl`
- `Iris/_docs/refactor/test_workflow_consolidation/duplication_ledger.jsonl`
- `Iris/_docs/refactor/test_workflow_consolidation/classification_ledger.jsonl`
- `Iris/_docs/refactor/test_workflow_consolidation/contract_preservation_matrix.jsonl`
- `Iris/_docs/refactor/test_workflow_consolidation/scenario_dag.json`

Implementation Notes:

1. configured pytest node, exact taxonomy ID, required-validation binding과 route를 하나의 inventory에서 연결하되 authority는 합치지 않는다.
2. producer invocation, subprocess command signature, cwd/env/input/output identity, temp workspace, copy count/bytes와 repeated read/parse/hash hotspot을 수집한다.
3. static AST/search census와 dynamic census를 별도 필드로 유지하고 discrepancy를 disposition한다.
4. 각 test에 primary disposition, `authority_bound`, execution constraints와 mutable-state dependency를 지정한다.
5. `must_isolate`는 다음 contract에 우선 부여한다: fresh process/bootstrap, tamper after mutation, crash/recovery, rollback, concurrent owner, lock lifecycle, source-write rejection, standalone CLI semantics.
6. contract preservation matrix는 old test ID, assertion/contract IDs, input partition, negative case, expected failure signature, successor scenario/probe, isolation과 authority migration requirement를 기록한다.
7. `obsolete_or_redundant`는 replacement proof와 before detection evidence가 없으면 사용할 수 없다.
8. `deferred` row는 `deferred_reason_code`, evidence references, 책임 owner, re-entry condition과 해당 expensive invocation identity를 필수로 가진다. Free-text reason만 있거나 invocation과 연결되지 않은 deferred row는 유효하지 않다.
9. pilot 외 family는 census 결과만으로 자동 채택하지 않고 candidate disposition으로 둔다.

Validation:

```text
unclassified_test_count = 0
unowned_contract_count = 0
unexplained_dependency_count = 0
unattributed_expensive_invocation_count = 0
deferred_invocation_without_reason_binding = 0
obsolete_without_replacement_proof = 0
authority_binding_without_transaction_disposition = 0
must_isolate_violation = 0
```

---

### Change 3 — Minimal scenario/report foundation and proof harness

Purpose:

Execution reuse와 semantic adjudication을 분리한 최소 immutable contract를 만들고, 새 구조 자체의 failure mode를 검증한다.

Files:

- `Iris/validation/test_workflow_consolidation/scenario_contracts.py`
- `Iris/validation/test_workflow_consolidation/validate_scenario_report.py`
- `Iris/validation/test_workflow_consolidation/compare_contract_parity.py`
- `Iris/validation/test_workflow_consolidation/tests/test_scenario_contracts.py`
- `Iris/validation/test_workflow_consolidation/tests/test_validate_scenario_report.py`
- `Iris/validation/test_workflow_consolidation/tests/test_compare_contract_parity.py`
- `Iris/_docs/refactor/test_workflow_consolidation/scenario_report.schema.json`

Implementation Notes:

`ScenarioContext`는 최소 다음 identity를 immutable하게 가진다.

```text
schema_version
scenario_id
validation_subject_commit/tree
route_class
contract_identity
input_identity
locale
environment_contract
workspace_mode/owner
producer_identity
```

`ExecutionResult`는 command signature, exit code, stdout/stderr byte hashes, parsed payload identity, producer invocation count와 observation coverage를 가진다. Raw mutable dict나 temp path owner를 외부에 노출하지 않는다.

`ProbeResult`는 `PASS | FAIL | BLOCKED | NOT_APPLICABLE`, probe ID, reason, evidence reference와 `blocked_by`를 가진다. `BLOCKED`는 PASS가 아니며 dependency target이 존재해야 한다.

`ScenarioReport`는 context/result identity, required probe inventory, ordered probe results, dependency edges, cross-probe adjudication, scenario disposition과 execution observations를 가진다. Scenario disposition은 그 scenario의 conjunction일 뿐 Registry/IAR/Publish/Iris 전체 PASS가 아니다.

Report는 byte-stability 대상인 `deterministic_core`와 volatile `execution_observations`를 구조적으로 분리한다.

```text
deterministic_core
- schema/context stable identities
- producer command/input/output hashes
- probe inventory/results/reasons
- dependency edges/blocked_by
- adjudication/disposition
- deterministic integer operation counts

execution_observations
- timestamps and elapsed time
- PID/process-tree runtime identities
- machine-specific absolute external paths
- run/order/sample IDs
- raw stdout/stderr/result locations
```

Schema의 `normalization_excluded_fields`는 제외 가능한 exact JSON Pointer 목록을 고정하며 `execution_observations`의 위 volatile field만 허용한다. Probe status/reason, hashes, dependency, disposition, operation count 또는 authority identity는 normalization에서 제외할 수 없다. Byte-stability claim은 canonical key ordering, UTF-8/LF와 path descriptor normalization을 적용한 `deterministic_core` projection에만 사용한다.

Foundation은 처음부터 범용 framework로 확장하지 않는다. Pilot과 두 번째 admitted family에서 동일 abstraction이 실제로 재사용될 때만 helper를 추가한다.

Proof harness는 before/after에 동일 known-bad fixture와 focused failure injection을 주입해 detection과 localization을 비교한다. Producer failure와 consumer probe failure를 서로 다른 failure signature로 보존한다.

Validation:

- same immutable input -> byte-stable `deterministic_core`
- undeclared normalization exclusion과 semantic field exclusion rejection
- missing required probe rejection
- duplicate/unexpected probe rejection
- malformed/unsupported schema rejection
- stale subject/input/environment identity rejection
- undeclared dependency와 invalid `blocked_by` rejection
- impossible PASS/BLOCKED combination rejection
- route contamination 및 undeclared authority promotion rejection
- shared result mutation attempt rejection
- isolated/grouped/repeated/shuffled execution result parity

---

### Change 4 — Pilot: public-text Phase 7 current-route scenario

Purpose:

가장 명시적인 repeated producer family에서 contract identity와 CLI boundary를 유지하면서 실제 execution 중복을 제거한다.

Files:

- `Iris/build/description/v2/tests/test_public_text_quality_acceptance_current_route.py`
- `Iris/validation/test_workflow_consolidation/scenario_contracts.py`
- `Iris/validation/test_workflow_consolidation/tests/test_public_text_phase7_scenario.py`
- `Iris/_docs/refactor/test_workflow_consolidation/pilot_contract_mapping.json`
- `Iris/_docs/refactor/test_workflow_consolidation/pilot_receipt.json`

Implementation Notes:

1. 다음 4개 predecessor test identity를 우선 그대로 유지한다.
   - `test_phase7_schema_dispatch_accepts_historical_v1_and_current_v2`
   - `test_phase7_schema_dispatch_rejects_unknown_and_malformed`
   - `test_phase7_schema_dispatch_rejects_successor_transaction_hash_mismatch`
   - `test_phase7_freeze_document_replay_is_deterministic`
2. class/scenario setup이 exact command signature의 producer를 한 번 실행하고, parsed result를 immutable `ExecutionResult`와 4개 named probe로 변환한다.
3. fixture owner는 test class/run lifecycle에 명시적으로 결속한다. module global cache, previous test residue 또는 persistent filesystem cache를 사용하지 않는다.
4. 각 test는 자신의 기존 assertion 책임에 해당하는 named probe만 확인한다. Producer/report validation은 모든 test보다 먼저 동일 lifecycle에서 수행한다.
5. test 하나만 isolated 선택해도 독립적으로 setup/cleanup하고 PASS/FAIL을 재현해야 한다.
6. CLI behavior가 이 family의 contract이므로 subprocess boundary는 1회 유지한다. Direct function conversion은 pilot success에 포함하지 않는다.
7. 나머지 7개 test의 서로 다른 Phase 7 producer와 required-gate subprocess는 census가 duplicate로 증명하지 않는 한 변경하지 않는다.
8. class fixture 방식이 configured pytest와 supported unittest grouping에서 단일 실행을 보장하지 못하거나 localization을 악화시키면, 하나의 scenario test + named subtests로 전환한다. 이때 old IDs, source classification, denominator와 evidence mapping을 Change 6의 atomic transaction으로 함께 이관한다.
9. 예상 효과는 기존 4회 producer/subprocess 실행을 grouped run에서 1회로 줄이는 것이지만, 실행 전 수치이므로 claim하지 않는다.
10. Pilot은 live recensus상 exact-current/required-validation test identity에 결속되지 않았으므로 실제 authority-bound migration proof로 사용하지 않는다. 최초 real authority-bound family는 Change 6의 별도 qualification gate를 통과해야 한다.

Pilot branch별 acceptance는 다음처럼 분리한다.

| Branch | Identity model | Required localization/isolation evidence |
|---|---|---|
| A | 기존 4개 predecessor node 유지 + explicit class/scenario-owned immutable execution | 각 predecessor node isolated PASS, grouped run의 producer 1회, 기존 node ID별 failure attribution 유지 |
| B | 1개 successor scenario node + 4개 named subtest/checkpoint | removed predecessor node의 isolated 실행을 요구하지 않는다. 대신 successor scenario isolated PASS, 각 old ID -> checkpoint ID 1:1 mapping, checkpoint별 focused fault injection과 failure reason, grouped/isolated attribution parity 및 atomic identity transaction을 요구한다. |

Validation:

- before/after 4 contract result parity
- unknown/malformed schema와 3개 transaction hash mismatch detection parity
- deterministic replay parity
- producer nonzero/malformed JSON/stale result의 new negative coverage
- grouped producer invocation `4 -> 1`
- grouped eligible subprocess `4 -> 1`
- branch A: each predecessor node isolated execution PASS
- branch B: successor scenario isolated PASS + each named checkpoint focused failure-attribution PASS
- order shuffle/repeat PASS 및 invocation owner reset 확인
- pilot file 전체 11 predecessor contract의 result parity
- S_base와 immutable pilot candidate를 함께 측정한 `candidate_paired_qualification_session`에서 pilot median wall time improvement beyond observed noise; terminal closeout에서는 최종 S_terminal과 다시 증명
- exact-current/required-validation live recensus에서 관측된 non-applicability 또는 필요한 atomic migration 증명

Pilot에서 semantic parity, localization, isolation, producer/subprocess reduction 또는 candidate paired timing acceptance 중 하나라도 실패하면 pilot을 rollback하고 broader family expansion을 열지 않는다. 이 candidate PASS는 terminal accepted paired session의 재측정을 대체하지 않는다.

---

### Change 5 — Controlled family admission and transaction dry-run

Purpose:

Pilot pattern을 실제 중복 비용과 safe reuse가 입증된 contract family에 한해서만 admission하고, implementation과 authority migration을 하나로 묶은 transaction을 mutation 전에 설계한다.

Files:

- census가 candidate로 판정한 test/helper files — read-only analysis input
- `Iris/_docs/refactor/test_workflow_consolidation/family_disposition_ledger.jsonl`
- `Iris/_docs/refactor/test_workflow_consolidation/family_metrics/`
- `Iris/_docs/refactor/test_workflow_consolidation/family_contract_parity/`
- `Iris/_docs/refactor/test_workflow_consolidation/family_transaction_dry_runs/`

Implementation Notes:

후보 순서는 다음이다.

1. runtime payload validation/seal
2. artifact lifecycle inventory/executor/promotion
3. Registry Authority lifecycle/workflow
4. registry-runtime validator/generator
5. repeated generated-artifact inspection
6. table-driven assertion family

각 family admission 조건은 모두 충족해야 한다.

```text
same_expensive_work = proven
canonical_input_identity = same
result_reusable_without_mutation = true
contract_mapping_complete = true
isolation_preserved = true
authority_impact_known = true
measured_material_benefit = true
```

Tamper, crash, rollback, concurrent-owner 또는 fresh-process test는 정상-flow seed 준비만 공유할 수 있다. Mutation 후 state와 workspace는 독립 clone/process에 남긴다. 하나의 early producer failure가 서로 독립적으로 관측 가능한 probe를 전부 `BLOCKED`로 만들면 consolidation design을 재검토한다.

`measured_material_benefit`에 timing이 필요하면 exact `S_base`와 immutable family candidate를 첫 warm-up 전에 함께 materialize한 `candidate_paired_qualification_session`에서만 판정한다. Change 1 Q/Q sample이나 서로 다른 session의 before/after를 결합하지 않는다. Candidate session은 admission 증거일 뿐 terminal closeout sample 또는 `cost_denominator_manifest.json`의 final axis baseline이 아니다.

각 family는 `adopted`, `must_isolate`, `deferred`, `no_material_benefit` 중 하나로 닫는다. `adopted`는 Change 6에서 실행할 exact implementation+authority transaction manifest, stable unique `family_id`와 terminal targeted measurement command가 완전한 경우에만 허용한다. Change 5에서는 application test/helper를 수정하지 않는다. `no_material_benefit`는 실패가 아니라 측정 결과지만 전체 execution-lightweighting complete claim의 감축 수치에는 포함하지 않는다.

Table-driven candidate는 각 predecessor case의 stable `case_id`, human-readable subtest label, input partition, expected result와 failure signature를 보존한다. Parameter row 수 감소나 label 합병으로 서로 다른 failure attribution을 잃으면 admission하지 않는다.

Validation:

- family별 S_base command/counter qualification receipt, 필요 시 same-session candidate paired timing receipt와 projected observation coverage
- candidate receipt `measurement_protocol_identity` equality와 family당 5 measured block/arm당 10 sample 준수
- old contract/negative/mutation/failure signature mapping completeness
- table-driven case ID/label/failure signature preservation
- implementation+authority transaction dry-run과 rollback simulation
- source application worktree delta 0
- expected framework overhead와 repository-wide net test/tooling LOC 별도 계상 계획

---

### Change 6 — Family implementation and atomic identity/authority transaction

Purpose:

Admitted family의 execution consolidation을 구현하고, test/scenario identity 변경이 필요한 경우 taxonomy, source classification, denominator, required-validation과 evidence mapping을 같은 transaction에 포함해 half-state를 방지한다.

Files:

- `Iris/validation/test_workflow_consolidation/validate_identity_transaction.py`
- `Iris/validation/test_workflow_consolidation/tests/test_validate_identity_transaction.py`
- admitted family의 exact test/helper files — conditional application delta
- `Iris/_docs/refactor/test_workflow_consolidation/family_metrics/`
- `Iris/_docs/refactor/test_workflow_consolidation/family_contract_parity/`
- `Iris/_docs/refactor/test_workflow_consolidation/identity_transactions.jsonl`
- `Iris/_docs/round3/round3_pytest_source_classification.json` — conditional
- `Iris/_docs/round3/round3_full_discovery_denominator.json` — conditional
- `Iris/_docs/round3/round3_test_taxonomy.json` — conditional
- `Iris/_docs/round3/current_route_required_validations.json` — conditional
- affected current evidence pointer/manifest — conditional additive successor only

Implementation Notes:

1. Change 5 dry-run이 봉인한 exact transaction manifest에 따라 test/helper implementation과 모든 required authority changes를 같은 family commit/transaction에 적용한다.
2. Authority identity가 바뀌지 않는 family도 implementation, contract mapping, actual after measurement와 disposition evidence를 하나의 rollback unit으로 유지한다.
3. Source-level configured classification이 유지되고 exact/current-required binding이 없으면 해당 축은 `NOT_APPLICABLE`로 기록하며 불필요한 manifest churn을 만들지 않는다.
4. 기존 identity는 삭제하지 않고 predecessor mapping으로 남긴다. Sealed historical artifact bytes는 바꾸지 않는다.
5. taxonomy/current-required row의 hash mismatch는 owner adoption 근거가 아니다. Live successor subject와 consumer closure를 재계산한다.
6. partial migration, dangling ID, duplicate current identity, stale evidence binding, route reassignment와 denominator laundering은 fail-closed다.
7. Family-local after observation은 Change 1의 동일 external `measurement_tooling_identity`, block/pairing protocol과 observation scope를 사용한다. Timing acceptance가 필요하면 `S_base`와 immutable family candidate를 같은 candidate session에서 다시 수집하며 Change 1 Q/Q sample을 before arm으로 재사용하지 않는다. 이 결과는 transaction qualification용이고 terminal closeout sample은 Change 7에서 별도로 수집한다.
8. 각 family는 old contract/negative/mutation/failure signature parity, isolated/grouped/repeated/shuffled execution, workspace preimage/postimage, cleanup/recoverability, source delta와 framework overhead를 검증한다.
9. 모든 family transaction 뒤 final ledger의 `adopted` non-pilot `family_id`가 unique/stable하고 terminal targeted command가 관측 가능함을 확인한다. Change 1의 parameterized resolver가 이 ledger를 exact ordinal order로 해소하지 못하면 `S_terminal`을 발급하지 않는다.

최초로 `authority_bound=true`이며 실제 taxonomy, classification, denominator, required-validation 또는 current evidence identity를 변경하는 family는 별도 qualification gate다.

```text
first_real_authority_bound_migration
= exact live binding recensus
 + migration dry-run
 + implementation/authority single-transaction candidate
 + partial/rollback failure injection
 + exact-current/configured-current/required-integrity validation
 + predecessor mapping preservation
```

이 gate가 PASS하기 전에는 두 번째 authority-bound family transaction을 열지 않는다. Authority-bound family가 하나도 admission되지 않으면 gate는 `NOT_APPLICABLE`이며, closeout은 authority migration이 실증됐다고 주장하지 않는다.

Validation:

```text
unmapped_predecessor_id = 0
dangling_successor_id = 0
stale_required_validation = 0
dual_current_identity = 0
route_reclassification_without_owner_basis = 0
historical_denominator_rewrite = 0
diagnostic_laundering = 0
partial_transaction = 0
first_real_authority_bound_migration = PASS or NOT_APPLICABLE_no_admitted_authority_family
family_contract_or_negative_regression = 0
family_isolation_regression = 0
family_source_mutation = 0
```

---

### Change 7 — Terminal remeasurement, Clean-Checkout validation and closeout

Purpose:

최종 exact subject가 검증 의미를 보존하면서 accepted execution cost를 줄였는지 판정하고 evidence-bounded closeout을 만든다.

Files:

- `Iris/_docs/refactor/test_workflow_consolidation/terminal_comparison.json`
- `Iris/_docs/refactor/test_workflow_consolidation/accepted_paired_measurement_summary.json`
- `Iris/_docs/refactor/test_workflow_consolidation/accepted_session_schedule.json`
- `Iris/_docs/refactor/test_workflow_consolidation/accepted_session_resource_estimate.json`
- `Iris/_docs/refactor/test_workflow_consolidation/measurement_comparability_report.json`
- `Iris/_docs/refactor/test_workflow_consolidation/cost_denominator_manifest.json`
- `Iris/_docs/refactor/test_workflow_consolidation/terminal_source_policy_revalidation_report.json`
- `Iris/_docs/refactor/test_workflow_consolidation/terminal_validation_manifest.json`
- `Iris/_docs/refactor/test_workflow_consolidation/independent_review.json`
- `Iris/_docs/refactor/test_workflow_consolidation/owner_seal.json`
- `Iris/_docs/refactor/test_workflow_consolidation/workflow_closeout_carrier_manifest.json`
- `Iris/_docs/refactor/test_workflow_consolidation/terminal_evidence_pointer.json`
- `Iris/validation/test_workflow_consolidation/validate_workflow_closeout_carrier.py`
- `Iris/validation/test_workflow_consolidation/tests/test_validate_workflow_closeout_carrier.py`
- `docs/DECISIONS.md` — `evidence_governance` role, closeout 후 additive entry
- `docs/ROADMAP.md` — `evidence_governance` role, state update
- `docs/ARCHITECTURE.md` — 실제 architecture correction이 있으면 `S_terminal` 전 relevant mutation으로 처리하고 재검증; carrier에는 status-only cross-reference 외 semantic correction 금지

Implementation Notes:

Subject chronology는 다음을 사용한다.

```text
S_base        = accepted clean-checkout before subject
S_measure_tool = immutable subject-independent measurement/comparability tooling
S_measure_gate = tooling-review pointer/qualification evidence chronology label; measurement target/tool identity 아님
S_impl        = implementation candidate chronology label; acceptance/gate identity 아님
S_preterminal = all admitted changes completed chronology label; acceptance/gate identity 아님
S_terminal    = final code/test/config/command/protocol/denominator/semantic-authority mutation 이후 immutable validation subject
S_closeout_carrier = terminal evidence/governance only direct child; validation/measurement subject 아님
```

`S_measure_gate`, `S_impl`과 `S_preterminal`은 작업 순서를 설명할 뿐 artifact가 이 label을 measurement target/tool acceptance identity로 참조하거나 PASS를 상속하지 않는다. Acceptance subject는 오직 exact `S_base`, `S_measure_tool`, `S_terminal`이다.

Post-terminal chronology는 다음으로 고정한다.

```text
S_terminal
-> terminal validation + accepted paired measurement
-> comparability + source-policy revalidation
-> independent review + owner seal + external durable bundle
-> evidence-only S_closeout_carrier
-> fresh-root carrier DAG retrieval + S_terminal replay
```

`S_closeout_carrier`의 유일한 parent는 `S_terminal`이고 ancestry distance는 정확히 1 commit이며, carrier는 `S_terminal`의 PASS를 받는 새 validation subject가 아니다. Route, measurement와 Clean-Checkout replay는 carrier checkout이 아니라 pointer가 결속한 exact `S_terminal` checkout에서 실행한다.

`S_terminal`에 predecessor PASS를 상속하지 않는다. 마지막 code/test/config/command/protocol/denominator/semantic-authority 변경 뒤 `S_base`와 `S_terminal` disposable checkout을 같은 machine에 모두 materialize하고, 한 `accepted_paired_measurement_session` 안에서 첫 warm-up부터 마지막 measured block까지 A/B를 interleave한다. Change 1 Q/Q 또는 Change 5/6 candidate sample을 이 session에 이식하지 않는다. Focused와 모든 route validation, 동일 `S_measure_tool`/`measurement_protocol_identity` 기반 measurement 및 Clean-Checkout Run A/B를 새로 수행한다. `S_base..S_terminal` changed-path containment, tool/protocol/environment/command/input/session equality와 contract-denominator equivalence가 모두 PASS하기 전에는 cost delta를 이 round에 귀속하지 않는다. Review 수정이 source/config/command/denominator/measurement semantics를 바꾸면 새 `S_terminal`을 발급하고 machine validation과 paired session을 반복한다.

Accepted session preflight는 final family ledger를 parameterized contract로 해소해 external canonical `accepted-session-schedule.json`을 만든다. Mandatory pilot과 각 sorted adopted non-pilot family에 5 measured block, configured route에 10 block을 정확히 배정하고 workload별 warm-up을 포함한다. 이 schedule과 `measurement_protocol_identity`가 session receipt에 hash-bound되기 전에는 첫 warm-up을 시작하지 않는다. Tracked `accepted_session_schedule.json`은 raw schedule SHA-256와 deterministic projection/pointer를 가진 post-terminal carrier/summary다.

첫 warm-up 전에 external `accepted-session-resource-estimate.json`을 생성해 owner에게 공개한다. 최소 필드는 `N_adopted_nonpilot`, workload/block/sample/position 총수, qualification/candidate receipt 기반 expected p50/p95 duration, worst-case timeout duration, 예상 external disk, session 전체 실패 시 full-restart 시간/비용과 owner acknowledgment다. Tracked `accepted_session_resource_estimate.json`은 acknowledged raw estimate의 hash-bound carrier/summary다. Estimate가 운영 한도를 넘으면 block을 즉석에서 줄이지 않고 contract 변경 -> tooling review -> Q/Q qualification을 반복하거나 closeout을 BLOCKED/partial로 낮춘다.

`cost_denominator_manifest.json`은 `S_terminal`에 이미 존재하는 final family ledger hash와 parameterized schedule을 입력 authority로 결속하고, mandatory pilot/final adopted family의 exact scenario/test/probe ID, accepted terminal session A arm에서 얻은 axis별 baseline, paired B value, `NOT_APPLICABLE` reason 및 aggregate result를 기록한다. Carrier의 이 manifest는 family membership이나 aggregate formula를 새로 정하는 authority가 아니다. Configured route performance observation은 별도 row로 두고 family aggregate에 혼합하지 않는다. Ledger/schedule 불일치 또는 다른 session에서 얻은 axis별 baseline은 final manifest validation에서 거부한다.

`accepted_paired_measurement_summary.json`은 external raw terminal session의 session ID, 두 subject, tooling/environment/interpreter identity, `measurement_protocol_identity`, accepted schedule/ledger hash, sample inventory/hash, block validity, statistical result와 durable pointer를 결속한다. `measurement_comparability_report.json`은 canonical external `measurement-comparability.json`의 hash-bound carrier/summary이며 deterministic verdict/protocol identity projection이 raw report와 정확히 같아야 한다.

Terminal configured collection 전에 qualification artifact를 덮어쓰지 않고 exact `S_terminal` 결과를 별도 `terminal_source_policy_revalidation_report.json`으로 만든다. 이 tracked carrier/summary는 external `terminal-source-policy-impact.json`의 raw SHA-256와 retrieval pointer를 결속한다. Successor package가 계속 explicit-path only인지, admitted family transaction의 source classification/count/hash가 완전한지 모두 확인한다.

Independent reviewer는 roadmap/plan의 실질 공동 작성자, 해당 implementation/migration의 수행자 또는 owner seal 발급자와 달라야 한다. Reviewer artifact는 `authored_roadmap=false`, `authored_plan=false`, `implemented_candidate=false`, `issued_owner_seal=false`를 attestation하고 exact `S_terminal`, machine manifest와 measurement comparability report를 결속한다. 이 계획 또는 상위 roadmap을 공동 작성한 AI/model의 review는 terminal independent-review credit으로 사용할 수 없다.

Round ID와 Clean-Checkout `ClaimId`는 이 문서의 예시 문자열로 자동 확정하지 않는다. Terminal 실행 전 owner가 approved vocabulary로 예약하고, 모든 runner/evidence/owner-seal artifact가 동일 owner-approved ID를 사용해야 한다.

Post-terminal JSON과 closeout governance bytes는 external staging에서 먼저 완성한다. Owner seal은 exact `S_terminal`, machine/session/comparability/validation/review/bundle hashes와 staged governance delta hash를 결속하지만 자신의 blob, terminal pointer, carrier manifest 또는 containing carrier identity를 역참조하지 않는다. 그 뒤 전체 allowed delta를 한 `S_closeout_carrier` commit으로만 추적한다. `workflow_closeout_carrier_manifest.json`은 exact allowed path/role과 manifest 자신을 제외한 staged Git blob IDs를 기록한다. Pointer는 containing carrier commit/tree나 carrier-manifest hash를 역참조하지 않으며 validator가 runtime에 carrier commit/tree와 manifest blob을 해소해 비순환 receipt를 만든다.

Predecessor `carrier-aware-v2`의 single-parent/one-generation/non-self-reference/fresh-root DAG 원칙은 재사용하지만, 그 구현은 pointer+manifest 두 파일만 허용하므로 이번 다중 post-terminal artifact에 그대로 호출하지 않는다. Successor `validate_workflow_closeout_carrier.py`는 exact allowlist에 있는 evidence file 추가와 `DECISIONS.md`/`ROADMAP.md`의 additive closeout delta만 허용한다. Code/test/config, command/measurement contract, family membership/denominator authority, source policy, required-validation 또는 semantic `ARCHITECTURE.md` delta가 있으면 carrier FAIL이며 새 `S_terminal`과 전면 재검증이 필요하다.

Validation:

- focused/exact/configured/Lua/Clean-Checkout 등 zero-exit contract 명령의 exit `0`
- historical 및 diagnostic/all의 raw result와 disposition이 각 frozen route policy를 충족
- Run A/B subject/environment/command/result canonical equality
- terminal post-validation relevant change count 0
- `S_closeout_carrier` single parent=`S_terminal`, ancestry distance 1, exact allowed evidence/governance delta only
- carrier checkout이 validation/measurement subject로 사용된 count 0
- accepted paired session이 한 session ID 안에서 S_base/S_terminal 양 arm 전체를 수집하고 cross-session sample count 0
- baseline/terminal measurement comparability PASS, raw/carrier projection equality 및 `out_of_scope_path_count=0`
- before/after `measurement_tooling_identity` equality
- qualification/candidate/terminal `measurement_protocol_identity` equality
- accepted schedule가 final ledger/parameterized block formula와 일치하고 adopted family targeted measurement 누락 0
- accepted session resource/restart estimate owner disclosure PASS
- harness/target execution interpreter identity equality
- `strict_reduction_denominator=adopted_family_union`
- required cost-axis acceptance PASS
- configured route arm당 measured sample 20 이상, detection ceiling이 frozen maximum acceptable regression 이하이며 one-sided upper bound가 그 margin 미만
- exact terminal source-policy impact/registration disposition PASS
- precision/localization/isolation/authority regression 0
- eligible independent review PASS
- owner seal valid
- fresh-root durable bundle retrieval and terminal replay PASS

---

## 7. Validation Plan

### Automated Validation

Target validation command는 clean disposable checkout, repository-external empty result root와 exact subject에서 실행한다. Measurement/comparability command는 별도 read-only `S_measure_tool` checkout에서 target subject checkout을 argument로 받아 실행한다. 아래 `<external-result-root>` 등은 execution에서 allocator receipt가 제공한 절대 경로로 materialize한다.

Route validation과 route measurement는 독립 evidence다. Validation PASS를 timing improvement로 읽지 않고 timing improvement를 semantic/route PASS로 읽지 않는다.

1. Measurement tooling identity and subject/environment preflight

```powershell
git -C <measurement-tool-checkout> rev-parse HEAD
git -C <measurement-tool-checkout> rev-parse 'HEAD^{tree}'
git -C <measurement-tool-checkout> status --short
uv run --project <measurement-tool-checkout> python -B <measurement-tool-checkout>\Iris\validation\test_workflow_consolidation\measure_execution_cost.py --mode verify-tooling --tooling-manifest <measurement-tooling-manifest> --contract <measurement-contract>
uv run --project <measurement-tool-checkout> python -B <measurement-tool-checkout>\Iris\validation\test_workflow_consolidation\classify_source_policy_impact.py --target-repository <measurement-tool-checkout> --output <external-result-root>\new-source-policy-impact.json
uv run --project <measurement-tool-checkout> python -B <measurement-tool-checkout>\Iris\validation\test_workflow_consolidation\measure_execution_cost.py --mode qualify-protocol --target-repository <s-base-checkout> --contract <measurement-contract> --output-root <external-qualification-root>
git rev-parse HEAD
git rev-parse 'HEAD^{tree}'
git status --short
uv run python -B -c "import platform,sys; print(sys.executable); print(sys.version); print(platform.platform())"
uv run python -B -m pytest --version
```

Qualification command는 S_base-only Q/Q이며 accepted A/B sample을 만들지 않는다. Terminal acceptance는 exact `S_base`와 `S_terminal`을 한 orchestration command에 함께 넘겨 하나의 session에서 interleave한다. Arm별 `run-arm`을 별도 시점에 실행해 사후 pairing하는 방식은 금지한다. Contract는 경로가 아니라 raw `measurement_protocol_identity`로 receipt 전체에 결속한다.

```powershell
uv run --project <measurement-tool-checkout> python -B <measurement-tool-checkout>\Iris\validation\test_workflow_consolidation\measure_execution_cost.py --mode plan-paired-session --session-kind terminal-acceptance --base-repository <s-base-checkout> --terminal-repository <s-terminal-checkout> --contract <measurement-contract> --family-ledger <terminal-family-disposition-ledger> --qualification-receipt <external-qualification-root>\qualification-receipt.json --candidate-receipt-root <external-candidate-receipt-root> --schedule-output <external-paired-session-root>\accepted-session-schedule.json --resource-estimate-output <external-paired-session-root>\accepted-session-resource-estimate.json
uv run --project <measurement-tool-checkout> python -B <measurement-tool-checkout>\Iris\validation\test_workflow_consolidation\measure_execution_cost.py --mode run-paired-session --session-kind terminal-acceptance --session-id <owner-approved-session-id> --base-repository <s-base-checkout> --terminal-repository <s-terminal-checkout> --contract <measurement-contract> --family-ledger <terminal-family-disposition-ledger> --schedule <external-paired-session-root>\accepted-session-schedule.json --resource-estimate <external-paired-session-root>\accepted-session-resource-estimate.json --owner-acknowledgment <owner-session-resource-ack> --output-root <external-paired-session-root>
uv run --project <measurement-tool-checkout> python -B <measurement-tool-checkout>\Iris\validation\test_workflow_consolidation\validate_measurement_comparability.py --base-repository <s-base-checkout> --terminal-repository <s-terminal-checkout> --accepted-session <external-paired-session-root>\session-receipt.json --protocol-qualification-receipt <external-qualification-root>\qualification-receipt.json --measurement-contract <measurement-contract> --tooling-manifest <measurement-tooling-manifest> --touch-surface <declared-round-touch-surface> --contract-map <terminal-contract-preservation-map> --output <external-result-root>\measurement-comparability.json
```

2. Collection-only identity

```powershell
uv run python -B -m pytest -s --collect-only -q -p no:cacheprovider --round3-contract=all Iris/build/description/v2/tests/test_public_text_quality_acceptance_current_route.py
uv run python -B Iris/_docs/round3/round3_run_contract_tests.py --class current --enforce-current-build-closure --list
uv run python -B -m pytest -s --collect-only -q -p no:cacheprovider --round3-contract=current --round3-enforce-denominator --round3-denominator-receipt <external-result-root>\configured-current-collection.json
uv run python -B -m pytest -s --collect-only -q -p no:cacheprovider --round3-contract=historical --round3-enforce-denominator --round3-denominator-receipt <external-result-root>\historical-collection.json
uv run python -B -m pytest -s --collect-only -q -p no:cacheprovider --round3-contract=diagnostic --round3-enforce-denominator --round3-denominator-receipt <external-result-root>\diagnostic-collection.json
uv run python -B -m pytest -s --collect-only -q -p no:cacheprovider --round3-contract=all --round3-enforce-denominator --round3-denominator-receipt <external-result-root>\all-collection.json
```

3. Successor tooling and negative contracts

```powershell
uv run python -B -m pytest -s -q -p no:cacheprovider Iris/validation/test_workflow_consolidation/tests
uv run python -B Iris/validation/test_workflow_consolidation/classify_source_policy_impact.py --target-repository <terminal-checkout> --output <external-result-root>\terminal-source-policy-impact.json
uv run python -B Iris/validation/test_workflow_consolidation/collect_execution_census.py <frozen-args>
uv run python -B Iris/validation/test_workflow_consolidation/compare_contract_parity.py <frozen-args>
uv run python -B Iris/validation/test_workflow_consolidation/validate_identity_transaction.py <frozen-args>
uv run --project <measurement-tool-checkout> python -B <measurement-tool-checkout>\Iris\validation\test_workflow_consolidation\measure_execution_cost.py <frozen-args>
uv run --project <measurement-tool-checkout> python -B <measurement-tool-checkout>\Iris\validation\test_workflow_consolidation\validate_measurement_comparability.py <frozen-args>
```

4. Pilot/family focused validation

```powershell
uv run python -B -m pytest -s -q -p no:cacheprovider --round3-contract=all Iris/build/description/v2/tests/test_public_text_quality_acceptance_current_route.py
```

각 admitted family file을 같은 command shape에 explicit positional path로 추가한다. Focused PASS는 configured-current나 exact-current PASS를 대체하지 않는다.

5. Exact-current

```powershell
uv run python -B Iris/_docs/round3/round3_run_contract_tests.py --class current --enforce-current-build-closure --out <external-result-root>\exact-current.json
```

6. Configured current, historical, diagnostic and all

```powershell
uv run python -B -m pytest -s -q -p no:cacheprovider --round3-contract=current --round3-enforce-denominator --round3-denominator-receipt <external-result-root>\configured-current.json
uv run python -B -m pytest -s -q -p no:cacheprovider --round3-contract=historical --round3-enforce-denominator --round3-denominator-receipt <external-result-root>\historical.json
uv run python -B -m pytest -s -q -p no:cacheprovider --round3-contract=diagnostic --round3-enforce-denominator --round3-denominator-receipt <external-result-root>\diagnostic.json
uv run python -B -m pytest -s -q -p no:cacheprovider --round3-contract=all --round3-enforce-denominator --round3-denominator-receipt <external-result-root>\all.json
```

Current/configured command는 frozen zero-exit contract를 따른다. Historical 및 diagnostic/all은 pytest launcher exit만 보지 않고 raw result, selected denominator와 disposition field를 해당 route policy로 판정한다. Diagnostic raw finding을 current PASS로 승격하지 않는다.

7. Lua syntax

Production Lua가 의도상 바뀌지 않아도 terminal source boundary 확인을 위해 실행한다.

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\check_lua_syntax.ps1
```

8. Clean-Checkout Run A/B and deterministic compare

```powershell
powershell -ExecutionPolicy Bypass -File .\Iris\validation\clean_checkout\invoke_receipt_bound_full_gate.ps1 -RepositoryRoot <run-a-checkout> -Commit <S_terminal> -ClaimId <owner-approved-claim-id> -EnvironmentReceipt <environment-receipt> -WorkRoot <run-a-work> -ResultRoot <run-a-result> -OrchestrationReceipt <run-a-orchestration>
powershell -ExecutionPolicy Bypass -File .\Iris\validation\clean_checkout\invoke_receipt_bound_full_gate.ps1 -RepositoryRoot <run-b-checkout> -Commit <S_terminal> -ClaimId <owner-approved-claim-id> -EnvironmentReceipt <environment-receipt> -WorkRoot <run-b-work> -ResultRoot <run-b-result> -OrchestrationReceipt <run-b-orchestration>
powershell -ExecutionPolicy Bypass -File .\Iris\validation\clean_checkout\invoke_deterministic_compare.ps1 -RepositoryRoot <terminal-checkout> -Commit <S_terminal> -ClaimId <owner-approved-claim-id> -EnvironmentReceipt <environment-receipt> -RunAOrchestrationReceipt <run-a-orchestration> -RunBOrchestrationReceipt <run-b-orchestration> -AttemptRoot <compare-attempt-root>
```

9. Successor closeout carrier and terminal evidence retrieval

이번 carrier는 post-terminal artifact와 additive governance delta를 포함하므로 pointer+manifest 두 파일만 허용하는 predecessor `carrier-aware-v2`와 동일하지 않다. Successor validator가 direct-parent/one-generation/exact-allowlist/non-self-reference를 확인하고 fresh root에서 bundle을 회수한 뒤 exact `S_terminal`로 replay한다.

```powershell
uv run python -B Iris/validation/test_workflow_consolidation/validate_workflow_closeout_carrier.py --carrier-repository <s-closeout-carrier-checkout> --terminal <S_terminal> --pointer <tracked-pointer> --carrier-manifest <workflow-closeout-carrier-manifest> --archive-root <owner-durable-root> --fresh-root <new-empty-external-root> --output <owner-durable-root>\terminal-evidence-retrieval-report.json
```

### Manual Validation

- conflict lock과 roadmap-to-plan traceability review
- full classification 및 `must_isolate` disposition review
- old contract -> probe/checkpoint mapping과 failure signature review
- CLI/direct-function boundary 판정 review
- timing protocol, raw sample, instrumentation coverage와 noise adjudication review
- raw `measurement_contract_sha256`와 qualification/candidate/terminal `measurement_protocol_identity` equality review
- Change 1 Q/Q qualification과 terminal accepted paired session의 sample inventory 분리 및 cross-session stitching 0 review
- `S_measure_tool` dependency closure 및 before/after tooling identity equality review
- `measurement_tooling_review.json` reviewer eligibility, exact subject/hash와 blocking verdict review
- 신규/이동 tracked test source의 configured discovery, controlled-source membership 및 registration timing review
- `S_base..S_terminal` changed-path containment과 comparability disposition review
- `adopted_family_union` cost denominator membership/axis review
- final family ledger -> sorted family schedule, family당 5 block/arm당 10 sample 및 total position formula review
- accepted session expected/p95/worst-case/full-restart resource estimate와 owner acknowledgment review
- configured-route arm당 sample 수, minimum detectable regression, owner-frozen maximum acceptable margin 및 one-sided bound review
- family별 material benefit/adoption decision
- taxonomy/denominator/required-validation/evidence atomic migration review
- first real authority-bound migration qualification review 또는 exact `NOT_APPLICABLE` 근거
- predecessor sealed artifacts no-rewrite 확인
- roadmap/plan 공동 작성자 및 implementer가 아닌 eligible independent reviewer의 exact `S_terminal` 검토
- owner-approved round ID/ClaimId vocabulary 확인
- owner seal 및 durable custody/retrieval 확인
- `S_terminal -> external validation/review/seal -> S_closeout_carrier` chronology, exact carrier allowlist와 carrier non-subject review

기본 범위에는 runtime/product mutation이 없으므로 PZ in-game UI validation은 요구하지 않는다. Production Lua 또는 public behavior 변경이 필요하다는 사실이 발견되면 이 계획에 암묵적으로 포함하지 않고 별도 scope/validation authority를 요청한다.

### Validation Limits

- PZ multiplayer, long-session, FPS, frame time, heap 또는 latency
- package publication, Workshop, release, deployment 또는 B42 readiness
- external mod 전체 compatibility
- persistent cross-run cache safety
- 다른 hardware/OS로의 benchmark portability
- frozen configured-route maximum acceptable regression보다 작은 wall-time 변화; closeout은 이 이하의 regression 부재를 주장하지 않음
- configured-route detection ceiling은 `S_base` 동질 Q/Q null 조건에서 추정되며 `S_terminal` 구조의 실제 분산과 같음을 보증하지 않음; terminal 판정은 사전 margin과 실제 paired bound에 한정
- instrumentation detection scope 밖 child-process 내부의 모든 read/hash/parse 부재
- 모든 future workload에서의 최적성
- unrelated historical tooling 전체의 건전성
- tokenizer 또는 Codex prompt/cache 비용 개선

---

## 8. Risk Surface Touch

### Authority Surface

높음. Test/scenario identity, configured source classification, route denominator, exact taxonomy, current required-validation과 evidence mapping을 조건부로 만진다. Semantic/artifact authority ownership은 변경하지 않는다.

### Runtime Behavior Surface

의도된 변경 없음. Iris production Lua와 game behavior는 protected surface다. 변경 필요성이 발견되면 current plan을 확장하지 않고 BLOCKED/scope-expansion request로 전환한다.

### Compatibility Surface

중간. Test/validator CLI, output JSON, fresh-process/bootstrap semantics와 runner invocation은 실제 consumer가 있는 경우 compatibility surface다. Public Iris runtime API는 변경하지 않는다.

### Sealed Artifact Surface

높음. Predecessor terminal subject, carrier, durable bundle, prior review/seal은 read-only로 보존한다. Successor evidence는 별도 root와 closure identity를 사용한다.

### Public-Facing Output Surface

없음. Browser, Wiki, Tooltip, localization, facts와 public claim text는 변경 대상이 아니다. Closeout docs는 execution claim boundary만 additive하게 기록한다.

---

## 9. Risk Analysis

### Architecture Risk

- shared kernel이 Registry/IAR/RTC/Publish semantics를 흡수할 위험
- current/historical/diagnostic route를 report 하나로 합쳐 authority를 흐릴 위험
- class-scoped reuse가 hidden global cache 또는 test-order dependency가 될 위험
- convenience import를 위해 current core closure 12 또는 allowed tooling 4를 확장할 위험
- framework LOC/complexity가 실제 절감보다 커질 위험
- family implementation과 authority migration이 별도 commit으로 갈라질 위험

Mitigation: execution mechanics와 probe semantics를 분리하고, route를 ScenarioContext identity에 결속하며, run-scoped immutable owner만 허용한다. Core closure는 read-only로 두고, 두 번째 family가 요구하기 전에는 foundation surface를 늘리지 않는다. Change 5는 mutation 없는 dry-run만 수행하고 Change 6에서 implementation+authority를 single transaction으로 적용한다.

### Runtime Risk

- 기본 범위의 runtime risk는 낮다.
- test producer 또는 instrumentation이 source checkout/cache/staging에 write residue를 남길 위험이 있다.

Mitigation: no-write command, external roots, `-B`, no cache provider, pre/post Git inventory와 Clean-Checkout wrapper를 사용한다. Write 후 복원도 mutation violation으로 센다. Producer instrumentation seam은 금지하며 external observation이 부족하면 BLOCKED로 처분한다.

### Compatibility Risk

- CLI를 direct call로 바꾸어 argument parsing, cwd, encoding, exit code 또는 stdout/stderr contract를 잃을 위험
- unittest class fixture와 pytest grouping의 lifecycle 차이로 producer가 예상보다 여러 번 실행될 위험
- individual node execution이 grouped execution에 의존할 위험

Mitigation: pilot CLI subprocess 1회는 유지하고 configured pytest, exact unittest runner applicability, isolated node와 grouped run을 각각 측정한다. Lifecycle별 actual invocation count가 acceptance evidence다.

### Regression Risk

- node/LOC 감소가 contract 또는 negative branch 손실을 숨길 위험
- producer early failure가 여러 probe의 원인을 가릴 위험
- tamper/crash/recovery state가 정상-flow shared state에 오염될 위험
- stale result가 다른 subject/input/environment에서 재사용될 위험
- identity migration이 dangling required-validation 또는 dual-current 상태를 만들 위험
- timing noise, cold cache 또는 instrumentation overhead를 improvement로 오인할 위험
- current dirty worktree와 clean-checkout baseline을 비교할 위험
- `S_base`에 없는 after-only harness로 before arm을 측정하거나 tool version이 달라질 위험
- clean하지만 unrelated path가 섞인 `S_terminal`의 cost delta를 round 효과로 오인할 위험
- admitted family와 configured route denominator를 혼합해 closeout status를 바꿀 위험
- Change 1의 Q/Q sample 또는 candidate session sample을 terminal A/B sample과 이어 붙일 위험
- configured route sample이 material regression을 검출하기에 underpowered일 위험
- 신규 tracked successor test가 configured source-policy denominator에 조용히 진입할 위험
- exact tooling subject가 아닌 일반 plan review를 tooling-review PASS로 오인할 위험
- 같은 `measurement_contract.json` 경로의 bytes가 바뀌어도 command argv가 같다는 이유로 동일 protocol로 오인할 위험
- Change 1 이후 확정된 adopted family 수에 따라 block 수/순서를 즉석 결정하거나 일부 family targeted timing을 누락할 위험
- 긴 accepted session의 중단 비용을 공개하지 않거나 partial sample을 재사용할 위험
- post-terminal evidence carrier를 새 validation subject 또는 denominator/command authority로 오인할 위험

Mitigation: contract preservation/fault matrix/localization proof, explicit `BLOCKED` dependency, must-isolate census, exact identity binding, atomic transaction, external immutable `S_measure_tool`, raw `measurement_protocol_identity`, exact tooling review, 분리된 source-policy qualification/terminal report, changed-path comparability function, parameterized family schedule, frozen `adopted_family_union`, owner-disclosed session/restart estimate, single-session interleaved paired timing, predeclared detection ceiling/margin, successor carrier validator, overhead companion과 clean-checkout-only comparison을 요구한다.

---

## 10. Rollback Plan

Rollback 단위는 foundation, pilot 및 admitted family transaction이다. 사용자 working tree를 reset/clean/stash하거나 unrelated 변경을 덮어쓰지 않는다.

1. `S_measure_tool` identity/dependency closure, eligible tooling review, source-policy impact disposition 또는 `baseline_protocol_qualification`이 재현되지 않으면 implementation을 시작하지 않는다. Diagnostic artifacts는 `rejected_protocol_qualification` trace로 보존한다.
2. Measurement tool 또는 `measurement_contract.json` bytes가 qualification 뒤 바뀌면 old/new 결과를 비교하지 않고 새 tooling/protocol identity로 tooling review, Q/Q qualification과 paired before/after를 모두 다시 수행한다.
3. Accepted paired session에서 한 arm/block이 invalid하거나 session/tool/protocol/environment/subject identity가 바뀌면 다른 session의 sample로 보충하지 않는다. 해당 accepted session 전체를 폐기하고 resource estimate에 공개한 full-restart 비용으로 두 checkout과 모든 adopted family/configured route arm을 다시 수집한다.
4. 신규 successor source가 예상과 달리 configured/controlled denominator에 들어가면 application mutation 전에 BLOCKED로 닫고 owner-approved source-registration plan revision 없이는 진행하지 않는다.
5. Configured route detection ceiling이 frozen maximum acceptable regression보다 크면 sample block을 늘려 protocol qualification을 다시 수행한다. Terminal B 결과를 본 뒤 margin을 넓히는 rollback/구제는 금지한다.
6. Scenario foundation negative test가 실패하면 foundation commit만 되돌리고 predecessor tests를 그대로 유지한다.
7. Pilot이 semantic parity, localization, isolation 또는 measured benefit gate를 통과하지 못하면 pilot test/support change만 되돌린다. Census와 failure evidence는 보존하고 broader expansion을 열지 않는다.
8. Family failure는 해당 family implementation, scenario mapping과 authority migration transaction 전체를 함께 되돌린다. 성공한 독립 family는 자동 rollback하지 않는다.
9. Identity migration failure 시 test ID, taxonomy, source classification, denominator, required-validation과 evidence pointer를 부분적으로 되돌리지 않는다. 해당 atomic transaction 전체를 predecessor identity로 복귀한다.
10. `S_base..S_terminal`에 frozen touch surface 밖 변경이 있으면 unrelated change를 포함한 새 base에 round transaction을 재적용해 양 arm을 재측정한다. 분리/재적용이 불가능하면 timing을 `UNATTRIBUTABLE`로 두고 closeout을 최대 `partial`로 제한한다.
11. Production runtime/semantic mutation이 필요하면 자동 진행하지 않고 변경을 적용하기 전 plan scope를 BLOCKED로 닫는다.
12. Measurement noise가 effect를 지배하거나 material candidate가 없으면 quota를 맞추기 위해 test를 합치지 않는다. `no_material_benefit` 또는 `partial`로 기록한다.
13. `must_isolate`, `deferred`, `no_material_benefit` family를 complete 수치 충족만을 위해 재분류하거나 수정하지 않는다.
14. Review 수정이 `S_terminal`의 code/test/config/command/denominator semantics를 바꾸면 기존 machine PASS와 accepted paired session을 폐기하고 새 terminal subject에서 전부 재실행한다.
15. External evidence packaging/retrieval 또는 allowed carrier bytes만 실패하고 `S_terminal`과 evidence meaning이 그대로임이 증명되면 failed carrier의 child가 아니라 `S_terminal`의 새 direct-child branch로 bundle/pointer/carrier를 재발급할 수 있다. Carrier delta에 code/test/config/command/protocol/denominator/semantic authority 변화가 있으면 새 terminal validation이 필요하다.
16. `S_closeout_carrier` 검증이 실패하면 `S_terminal` machine PASS는 historical evidence로 보존할 수 있지만 scoped `complete`와 durable retrieval claim은 금지한다.
17. Rollback 후 predecessor focused/configured/exact route와 relevant clean-checkout command가 frozen route policy를 충족하지 않으면 복구 완료를 주장하지 않는다.

---

## 11. Governance Constraints

- `docs/Philosophy.md`의 hub-and-spoke, Iris 역할, 근거 기반 중립성과 100% Lua runtime을 유지한다.
- Pulse는 Iris에 의존하지 않고 Iris는 다른 spoke를 직접 참조하지 않는다.
- production semantic behavior와 public-facing output은 protected surface다.
- predecessor terminal closeout, carrier, bundle, review와 seal을 rewrite하지 않는다.
- current/historical/diagnostic/Clean-Checkout route, denominator와 disposition을 서로 대체하지 않는다.
- raw FAIL/BLOCKED를 aggregation 또는 disposition으로 PASS로 바꾸지 않는다.
- missing probe/report/dependency/identity/schema는 fail-closed다.
- module global mutable cache, previous test workspace, prior failure residue와 persistent cross-run result를 공유하지 않는다.
- must-isolate test를 wall-time 감축을 위해 shared mutable workspace/process로 합치지 않는다.
- CLI가 contract이면 standalone subprocess boundary를 유지한다.
- exact test/scenario identity 변경은 implementation, taxonomy, classification, denominator, required-validation과 evidence mapping의 atomic transaction이다.
- exact tooling review와 `baseline_protocol_qualification` 없이 implementation을 열지 않고, qualification timing이나 single-run timing으로 improvement를 주장하지 않는다.
- `S_base`에 존재하지 않는 after-only tool 문제는 immutable external `S_measure_tool`로 해결하며 동일 tooling, harness interpreter와 target execution interpreter identity가 두 arm을 측정해야 한다.
- Accepted timing과 final cost-axis baseline은 Change 7의 한 `accepted_paired_measurement_session`에서만 나온다. Change 1 Q/Q, candidate session 또는 서로 다른 session의 sample stitching은 금지한다.
- Measurement contract는 path/argv가 아니라 schema/blob/raw SHA의 `measurement_protocol_identity`로 qualification, candidate, accepted session, comparability와 closeout에 결속한다.
- Final adopted non-pilot family 수는 Change 1에서 열거하지 않는다. Frozen resolver가 stable ledger를 ordinal sort하고 각 family에 5 measured block/arm당 10 sample을 배정하며 configured route 10 block과 함께 exact schedule을 만든다.
- Accepted session 시작 전에 예상/p95/worst-case/full-restart 시간과 외부 저장 비용을 owner에게 공개한다. 운영 편의를 위해 block을 줄이거나 partial session을 재사용하지 않는다.
- working overlay와 clean-checkout subject를 accepted before/after로 비교하지 않는다.
- `S_base..S_terminal` changed path가 frozen round touch surface를 벗어나면 기존 timing attribution을 폐기하고 rebaseline/replay하거나 `UNATTRIBUTABLE`로 닫는다.
- strict reduction denominator는 mandatory pilot과 final adopted family 합집합이다. Configured route 전체 performance observation과 혼합하지 않는다.
- configured route material no-regression은 B 결과 전에 봉인한 sample count, detection ceiling과 maximum acceptable margin으로만 판정한다. Terminal 결과 뒤 margin 완화는 금지한다.
- `must_isolate`, `deferred`, `no_material_benefit` family를 complete threshold 충족만을 위해 수정·재분류하지 않는다.
- node/LOC 감소를 producer/subprocess/materialization/timing 감소로 대체하지 않는다.
- static call-site 감소를 dynamic execution 감소로 주장하지 않는다.
- 0 baseline axis는 `NOT_APPLICABLE`이며 감축 수치가 아니다.
- route semantic validation과 route cost measurement를 서로 대체하지 않는다.
- production/build producer에는 measurement-only instrumentation seam을 추가하지 않는다. External observation으로 required evidence를 만들 수 없으면 BLOCKED다.
- 신규 tracked test source의 configured/controlled membership을 Change 1과 terminal에서 판정한다. Expected `not_applicable`과 다른 source를 owner-approved registration transaction 없이 실행 denominator에 넣지 않는다.
- Change 1 `source_policy_qualification_report.json`과 terminal `terminal_source_policy_revalidation_report.json`을 덮어쓰거나 같은 provenance로 취급하지 않는다.
- External raw comparability report와 tracked carrier/summary의 hash, session identity와 deterministic verdict projection은 일치해야 한다.
- `S_closeout_carrier`는 `S_terminal`의 direct one-generation evidence/governance child일 뿐 validation/measurement subject가 아니다. `post_terminal_relevant_change_count=0`은 allowlisted evidence/governance delta를 제외한 code/test/config/command/protocol/denominator/semantic authority 변화가 0이라는 뜻이다.
- existing round-scoped evidence helper는 successor reproduction과 consumer migration이 증명되기 전 삭제하지 않는다.
- machine validation, independent review와 owner seal은 서로 대체하지 않는다.
- independent reviewer는 roadmap/plan 공동 작성자, candidate implementer와 owner-seal issuer가 아니어야 한다.
- zero-exit contract 명령은 exact exit `0`, historical/diagnostic은 frozen raw/disposition policy를 충족할 때만 PASS를 주장한다. Required tool/input/authority가 없으면 BLOCKED다.
- Round ID와 ClaimId는 owner-approved reserved vocabulary만 사용한다.
- `complete` closeout에는 `validated`, `out_of_scope`, `unvalidated_but_in_scope` ceiling과 non-claims를 함께 기록한다.

---

## 12. Expected Closeout State

Expected closeout target: **complete**

다음 조건을 모두 만족할 때만 `Iris test workflow consolidation / execution lightweighting = scoped complete`를 사용할 수 있다.

```text
accepted_S_base = immutable_clean_checkout_subject
S_measure_tool = immutable_subject_independent_tooling_subject
measurement_tooling_review = PASS_exact_subject_eligible_reviewer_and_retrievable_pointer
baseline_protocol_qualification = PASS_not_accepted_timing_sample
measurement_tooling_identity_before_equals_after = true
measurement_contract_sha256_present_in_all_measurement_receipts = true
measurement_protocol_identity_qualification_candidate_terminal_equal = true
harness_interpreter_identity_before_equals_after = true
target_execution_interpreter_identity_before_equals_after = true
measurement_contract_frozen_before_protocol_qualification = true
declared_round_touch_surface_frozen_before_protocol_qualification = true
source_policy_qualification = PASS_not_applicable_explicit_path_only or PASS_owner_approved_transaction
terminal_source_policy_revalidation = PASS_separate_artifact_and_raw_hash
accepted_paired_measurement_session = PASS_single_session_S_base_and_S_terminal
accepted_session_schedule_matches_final_ledger_and_parameterized_contract = true
adopted_family_targeted_measurement_missing_count = 0
targeted_measured_blocks_per_pilot_or_adopted_family = 5
targeted_measured_samples_per_arm_per_family = 10
accepted_session_total_measured_blocks = 5 + (5 * N_adopted_nonpilot) + 10
accepted_session_total_execution_positions = (24 * N_adopted_nonpilot) + 68
accepted_session_resource_estimate_owner_acknowledged = true
cross_session_sample_count = 0
measurement_comparability_verdict = PASS
measurement_comparability_raw_carrier_projection_equal = true
out_of_scope_path_count = 0
unclassified_test_count = 0
unowned_contract_count = 0
unexplained_dependency_count = 0
deferred_invocation_without_reason_binding = 0
must_isolate_violation = 0

missing_current_contract = 0
unresolved_contract_mapping = 0
known_bad_detection_loss = 0
protected_mutation_detection_loss = 0
negative_branch_loss = 0
fail_closed_branch_loss = 0
failure_localization_regression = 0

missing_or_malformed_probe_detection = PASS
stale_identity_detection = PASS
invalid_dependency_detection = PASS
route_contamination_detection = PASS
undeclared_authority_promotion_detection = PASS

pilot_producer_invocation_delta < 0
pilot_eligible_subprocess_delta < 0
pilot_targeted_wall_time_improved_beyond_observed_noise_from_terminal_accepted_session = true
strict_reduction_denominator = mandatory_pilot_plus_final_adopted_family_union
adopted_family_union_nonzero_mandatory_cost_axes_strictly_reduced = true
configured_route_performance_observation = PASS_predeclared_margin_no_regression
configured_route_measured_samples_per_arm >= 20
configured_route_detection_ceiling <= frozen_maximum_acceptable_regression
configured_route_one_sided_upper_bound < frozen_maximum_acceptable_regression
configured_route_improvement_claimed = false or strict_improvement_proven
zero_baseline_axes_claimed_as_reduction = 0
unexplained_metric_regression = 0

mutation_leakage = 0
source_worktree_mutation = 0
test_order_dependency = 0
previous_test_dependency = 0
stale_shared_result_reuse = 0

current_historical_diagnostic_mixing = 0
historical_denominator_rewrite = 0
diagnostic_raw_failure_laundering = 0
dangling_or_stale_required_validation = 0
dual_current_identity = 0
predecessor_evidence_rewrite = 0
first_real_authority_bound_migration = PASS or NOT_APPLICABLE_no_admitted_authority_family

focused = PASS
exact_current = PASS
configured_current = PASS
historical_route = PASS_under_its_policy
diagnostic_all = PASS_under_raw_and_disposition_contract
lua_syntax = PASS
clean_checkout_run_a = PASS
clean_checkout_run_b = PASS
run_a_run_b_deterministic_compare = PASS

S_terminal = immutable_commit_and_tree
post_terminal_relevant_change_count = 0
S_closeout_carrier = immutable_evidence_governance_commit_and_tree
S_closeout_carrier_parent = S_terminal
S_closeout_carrier_ancestry_distance = 1
S_closeout_carrier_validation_subject = false
post_terminal_allowed_evidence_governance_delta_only = true
closeout_carrier_exact_allowlist_validation = PASS
independent_reviewer_eligible = true
independent_review = PASS
owner_seal = valid
owner_approved_round_and_claim_id = true
durable_bundle_fresh_root_retrieval = PASS
```

State mapping은 다음과 같다.

| Condition | Closeout state |
|---|---|
| `adopted_family_union`의 모든 mandatory gate/parameterized targeted measurement/strict reduction, configured-route predeclared-margin no-regression, exact post-terminal carrier 및 terminal governance 충족 | `complete` |
| 구현은 끝났으나 terminal timing/route/review/seal 미실행 | `implemented_only` |
| family-local 개선은 있으나 configured route regression, unattributable delta 또는 일부 admitted family/authority closeout 미완료 | `partial` |
| protocol identity/qualification/tooling review, accepted family schedule/single-session pairing, resource disclosure, identical measurement tool/interpreters, comparability, source-policy qualification/revalidation, carrier validation, authority, required input, clean subject 또는 validation path 부재 | `blocked` |

허용 가능한 최대 claim은 승인된 family와 accepted measurement scope에 한정한다.

```text
선택된 Iris test contract family의 validation semantics, named failure localization,
route/authority binding과 isolation을 보존하면서 동일 producer/workflow의 반복 실행을
줄였고, 그 감소는 S_base와 S_terminal을 함께 측정한 accepted clean-checkout
single-session before/after timing 및 operation-count evidence와
exact terminal validation, independent review 및 owner seal에 결속됐다.
```

이 closeout은 다음을 의미하지 않는다.

- Iris 전체 runtime correctness
- Registry Authority, Registry Runtime Compatibility, DVF 또는 Publish Boundary 전체 PASS
- 모든 Iris test의 통합 또는 최적화
- 모든 subprocess 제거
- historical/diagnostic raw PASS의 current 대체
- persistent cache safety
- PZ FPS, frame time, heap, multiplayer 또는 long-session 개선
- package, release, Workshop, deployment 또는 B42 readiness
- 모든 machine/environment에서 같은 performance improvement
