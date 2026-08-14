# Implementation Plan

> 계획명: Iris Current Validation Baseline Admissibility Restoration
>
> 기준일: 2026-08-14
>
> 로드맵 입력: `ROADMAP — Iris Current Validation Baseline Admissibility Restoration`
>
> 로드맵 입력 SHA-256: `176c96295fa8b1e84ab82723e9d28535be7b97e6a0a271fd3f99f01dbe72c8f6`
>
> Historical baseline: commit `671c7b928ad5a1dbf26ea76949462fa8a7287903`, tree `20bbbdb919fa97a44e03c1f1cb9ea0a6973fb1db`
>
> Target baseline: qualification을 통과한 exact successor commit/tree인 `S_base'`
>
> Execution weight: Heavy — configured-current denominator, current-route required validation, Windows path contract, RTC durable bundle, clean-checkout qualification과 future application-entry handoff contract를 함께 다룸
>
> Runtime / production / public output 변경: 없음

## 1. Objective

이 계획의 목적은 historical `S_base=671c7b92`를 정상 baseline으로 소급 수정하는 것이 아니라, 그 subject에서 관측된 current-validation 부적격 상태와 실패 evidence를 불변 predecessor 사실로 보존하면서 validation infrastructure의 원인을 복구하고, 독립 clean checkout에서 자격 심사를 통과한 새 immutable successor baseline `S_base'`를 확립하는 것이다.

완료 lifecycle은 다음 순서를 강제한다.

```text
S_base
= frozen historical predecessor
+ exact failure reproduction subject
+ before-repair evidence anchor
        |
        v
S_repair_candidate_n
= classified baseline-repair delta only
        |
        +-> configured-current qualification
        +-> RTC durable-bundle qualification
        +-> reseal/path qualification
        +-> canonical mandatory full-repository Clean-Checkout Run A / Run B
        +-> separate near-boundary path-control run
        |
        v
S_base'
= exact qualified commit/tree
+ admitted_validation_baseline
        |
        v
Baseline Admission Gate implementation + receipt
        |
        +-> admitted: future wrapper consumption eligible
        +-> rejected: application mutation prohibited
        +-> real application-entry binding: pending while entrypoint is absent
        |
        v
workflow consolidation reapplication handoff
```

이 계획은 세 가지 결과를 분리해 닫는다.

```text
baseline_restoration.machine_validation
baseline_restoration.independent_review
baseline_restoration.owner_seal
```

한 축의 PASS는 다른 축을 대체하지 않는다. 최종 성공 상태에서도 `Registry Runtime Compatibility PASS`, Iris runtime correctness 또는 workflow consolidation terminal PASS를 주장하지 않는다.

### Codebase Readpoint Findings

계획 작성 시 확인한 실제 저장소 사실은 다음과 같다.

* 현재 `HEAD`와 historical `S_base`는 같은 commit/tree다. 현재 working tree에는 사용자의 광범위한 수정과 untracked 파일이 있으므로 inspection-only surface이며 재현·수정·PASS evidence의 baseline으로 사용하지 않는다.
* `pytest.ini`는 `Iris/build/description/v2/tests`와 cross-track test를 configured discovery 대상으로 삼고, root `conftest.py`와 `Iris/build/description/v2/tests/conftest.py`가 `--round3-contract`, source classification, mixed-item override와 denominator receipt를 분담한다.
* `Iris/_docs/round3/round3_pytest_source_classification.json`은 tracked policy source denominator를 count/hash로 봉인한다. configured-current를 green으로 만들기 위한 source reclassification, skip, xfail, ignore 또는 denominator 축소는 허용하지 않는다.
* `test_dvf_3_3_current_route_required_validation_evidence_freshness_reseal.py`의 class setup은 긴 tracked `phase6` report를 먼저 읽고, 읽을 수 없으면 runner를 기본 repository-local root로 실행한다. 해당 class에는 setup에 묶인 test node 5개가 있다.
* `test_dvf_3_3_current_source_authority_drift_verification_adoption_reseal.py`도 같은 구조이며 setup에 묶인 test node 4개가 있다. 따라서 현재 `9 errors`는 node 9개와 class-level setup root cause 2개를 별도 denominator로 기록해야 한다.
* 두 reseal 구현은 이미 `--root`를 받지만, `write_phase3_update_manifest()`는 live `current_route_required_validations.json`을 쓰고 `write_phase6_final()`은 tracked claim-boundary/ledger 문서를 쓴다. 외부 root 인자만 전달해서는 read-only configured-current execution이 보장되지 않는다.
* RTC promotion 코드는 attempt staging의 11개 source member를 짧은 `.rtc-promotion-staging`에 복사한 뒤 `_docs/round3/registry_runtime_compatibility/bundles/<bundle_id>`로 atomic rename하고 lifecycle을 `canonical_durable`로 기록한다. 현재 required manifest가 선택한 live bundle은 `46c87bf...5988b9`다.
* RTC live validator는 선택된 durable bundle destination의 member count, byte count, SHA-256, byte parity와 Git visibility를 검사한 뒤 toolchain freshness로 진행한다. 따라서 현재 코드의 authority relation은 `attempt staging = promotion provenance`, `durable bundle destination = live canonical consumer input`이다.
* `Iris/validation/clean_checkout/`에는 external work/result root, independent disposable clone, `core.longpaths=true`, checkout-root preflight, tracked-input/dependency census, Run A/B canonical result 비교와 source non-mutation receipt가 이미 있다. `docs/DECISIONS.md`는 이 경로를 subset/advisory가 아닌 canonical mandatory full-repository gate로 규정한다. 따라서 baseline qualification은 `invoke_receipt_bound_full_gate.ps1`과 `invoke_deterministic_compare.ps1`을 실제로 실행하고 그 receipt를 소비해야 하며, focused/configured-current evidence로 이를 대체하지 않는다.
* 기존 clean-checkout contract는 Windows execution checkout root 최대 길이 `56`, materialized path 최대 길이 `259`, `core.longpaths=true`를 사용한다. repository에는 tracked relative path를 `248 -> 221`로 줄인 additive relocation precedent도 있다.
* predecessor `S_terminal=73084913...` 이후 `S_base`까지의 tracked delta는 evidence carrier 2개와 `docs/DECISIONS.md`뿐이다. 과거 terminal PASS는 exact `S_terminal`에 귀속되므로 descendant `S_base`에 상속할 수 없다는 현재 governance와 일치한다.
* current canonical docs는 workflow consolidation의 architecture 방향을 채택했지만 implementation은 pending으로 기록한다. 로드맵의 “기존 implementation 완료” 전제와 저장소 tracked evidence가 일치하지 않으므로, Change 10은 exact predecessor implementation diff/identity가 materialize되기 전에는 handoff를 `ready`로 봉인하지 않는다.

---

## 2. Scope

이 계획은 current-validation prerequisite restoration과 그 admission boundary만 다룬다.

포함 범위:

* `S_base` exact commit/tree의 read-only forensic reproduction
* configured-current command, source/node denominator와 11 non-passing nodes의 exact census
* raw stdout/stderr, pytest log, JUnit 또는 explicit no-JUnit state의 durable capture
* 5+4 propagated node와 두 class-level setup root cause의 관계 기록
* remaining 2 failures의 evidence-based attribution
* RTC required-gate `durable_bundle_destination_drift`와 기대된 `implementation_toolchain_freshness_failed` ordering 조사
* RTC promotion provenance와 canonical durable destination의 authority/materialization contract 봉인
* Windows checkout-root, tracked relative path, generated suffix와 external evidence root의 path budget 정의
* 두 reseal workflow의 read-only/current-validation execution context와 repository-external output isolation
* 모든 setup-blocked node의 post-repair actual execution 결과 관측
* validation-infrastructure-only repair candidate 구성과 delta classification
* configured-current green qualification
* 두 independent fresh checkout에서 canonical mandatory full-repository gate를 포함한 Run A/B qualification과 deterministic comparison
* determinism A/B와 분리된 near-boundary path-control qualification
* exact subject/environment/path/evidence-bound Baseline Admission Gate
* positive/negative admission test matrix, synthetic application-entry ordering proof와 실제 entry binding 상태의 분리
* admitted `S_base'`에서 시작하는 workflow consolidation reapplication handoff
* machine validation, independent review, owner seal과 closeout evidence의 분리

### Conflict Decisions Adopted By This Plan

로드맵에서 별도 판정으로 남긴 항목은 코드베이스와 기존 authority 경계를 근거로 다음처럼 고정한다.

| 항목 | 판정 | 실행 효과 |
| --- | --- | --- |
| subject-side correction | 이 계획은 validation infrastructure와 validation-owned contract correction만 허용한다. `subject_finding`이 Iris facts/rendered/runtime/public behavior에 속하면 별도 owner-owned correction으로 escalation한다. | subject finding을 test expectation 완화로 흡수하지 않는다. 별도 correction successor가 나온 뒤 이 계획의 qualification을 새 identity에서 재개한다. |
| unresolved finding admission | 허용하지 않는다. | `unknown_failure_count=0`, `evidence_absent_unclassifiable_count=0`, configured-current exit `0`, failed `0`, error `0`이 `S_base'` seal의 hard requirement다. |
| Windows path branch | qualified short checkout root + external short work/result roots + physical namespace shortening where required + fail-closed preflight를 normative contract로 사용한다. `LongPathsEnabled=0`을 qualified range 안의 mandatory supported environment로 둔다. | `core.longpaths=true`와 long-path-safe I/O는 defense in depth이며 root/path budget을 대신하지 않는다. 범위 밖 root는 named preflight rejection으로 종료한다. |
| RTC canonical relation | atomic promotion 후 durable bundle destination이 canonical live consumer input이고, attempt staging source는 immutable promotion provenance다. | current live validation은 durable destination을 읽는다. source/destination parity는 promotion과 successor bundle qualification에서 증명하며 historical bundle을 rewrite하지 않는다. |
| completion vocabulary | bare `complete` 또는 `canonical_complete`를 단독으로 사용하지 않는다. | `baseline_restoration=complete`, `S_base'=admitted_validation_baseline`, `workflow_consolidation_reapplication_handoff=ready`처럼 axis-qualified token만 허용한다. |

### Explicitly Out Of Scope

* workflow consolidation architecture 재설계
* contract-family, named checkpoint 또는 measurement objective 변경
* 새 optimization 후보 탐색, node/LOC 추가 감축
* historical `S_base`, predecessor evidence, review 또는 closeout artifact rewrite
* Iris source facts, rendered text, generated runtime payload 또는 production Lua 수정
* Browser, Wiki, Tooltip, 메뉴, 아이템 정보 또는 public text 변경
* Registry Runtime Compatibility 전체 semantic certification
* Registry Authority, DVF Body Compiler 또는 Publish Boundary certification
* test 삭제, skip, xfail, deselect, ignore, source reclassification 또는 denominator 축소
* 기존 `Iris/validation/clean_checkout/`의 terminal claim 범위 확대 또는 과거 PASS 재사용
* 일반 CI/CD 시스템이나 범용 Windows filesystem abstraction 재설계
* 모든 checkout length, UNC, network drive, case mode 또는 filesystem 조합 지원
* Project Zomboid 실행, manual UI, multiplayer, long-session 또는 외부 mod compatibility 검증
* package publication, Workshop, release 또는 B42 readiness

---

## 3. Non-Goals

* `S_base` 실패를 repair 후 PASS로 다시 쓰지 않는다.
* `9 errors`를 두 root cause로 요약했다는 이유로 9개 node evidence를 생략하지 않는다.
* class setup을 function setup으로 바꿔 propagation만 숨기지 않는다.
* setup failure 제거를 9개 node PASS로 간주하지 않는다.
* remaining 2 failures를 “pre-existing” 또는 “historical”이라는 이유로 non-blocking disposition하지 않는다.
* path가 짧은 한 checkout에서 PASS했다는 이유로 path-invariant 또는 qualified-range 재현성을 주장하지 않는다.
* `LongPathsEnabled=1` 설정을 유일한 해결책으로 요구하지 않는다.
* RTC durable member hash만 확인하고 inventory, bytes, visibility 또는 consumer resolution을 생략하지 않는다.
* RTC materialization repair를 RTC semantic PASS나 새 RTC debt 선언으로 확대하지 않는다.
* stored PASS receipt를 다른 commit/tree, dirty state, environment 또는 path contract에 재사용하지 않는다.
* gate 실행 실패, receipt parse 실패 또는 evidence retrieval 실패를 PASS로 해석하지 않는다.
* baseline restoration delta와 workflow consolidation application delta를 같은 subject에 섞지 않는다.
* old timing, measurement, tooling review, protocol qualification 또는 terminal receipt를 successor chain에 상속하지 않는다.

---

## 4. Assumptions

### Constitutional and Authority Assumptions

* `docs/Philosophy.md`가 최상위 설계 authority다.
* Iris의 PZ runtime은 100% Lua로 유지한다. 이 계획의 Python과 PowerShell은 offline validation/governance tooling이며 production runtime에 포함되지 않는다.
* `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`와 기존 receipts는 predecessor 사실로 소비하되 새 subject의 PASS evidence로 상속하지 않는다.
* `S_base` commit/tree와 그 historical failure facts는 immutable하다.
* validation result는 commit, tree, working-tree state, command, denominator, dependency, environment, path contract와 evidence identity에 결속한다.
* current, historical, diagnostic route는 서로 대체하지 않는다.
* machine validation, independent review, owner seal은 별도 authority axis다.

### Repository and Execution Assumptions

* 계획 작성 workspace의 dirty/untracked 변경은 사용자 소유다. 실행은 이를 stash, reset, clean, checkout, overwrite, stage 또는 commit하지 않는다.
* historical reproduction과 모든 candidate qualification은 exact Git object에서 만든 repository-external disposable clone을 사용한다.
* Windows PowerShell을 orchestration shell로 사용한다.
* Python 명령은 `uv run python` 형식을 사용하고, uv/Python/pytest/plugin/package identity를 receipt에 기록한다.
* `PYTHONHOME`, `PYTHONPATH`, `PYTEST_ADDOPTS`는 제거하고 bytecode, pytest cache, uv cache, TEMP/TMP와 result root는 repository 밖의 run-specific root로 격리한다.
* existing clean-checkout common utilities와 receipt schemas는 재사용 가능한 implementation precedent지만, 그 과거 PASS와 claim token은 이 계획의 evidence가 아니다.
* `current_route_required_validations.json`과 `round3_pytest_source_classification.json`은 독립 책임을 유지한다. required-test union과 configured source denominator를 혼합해 새 denominator를 만들지 않는다.
* external durable evidence storage는 owner-managed append-only file store이며 checkout temp/cache와 서로 disjoint하다. tracked pointer에는 machine-specific absolute archive path를 기록하지 않는다.
* 신설 `Iris/validation/baseline_admission/tests/`는 `pytest.ini`의 configured-current discovery 밖에 두고 dedicated static/schema command에서 직접 실행한다. Owner는 canonical full-repository `explicit_current_required_sources` membership을 `PASS`로 채택하거나 `not_applicable`로 명시적으로 disposition한다. `not_applicable`은 required execution denominator를 유지하고 dedicated route가 regression coverage를 소유하며, full-repository census에 unclassified source나 무단 membership addition이 남지 않는 상태다.
* `current_route_required_validations.json` 또는 `full_repository_gate.json` 같은 current authority contract의 변경은 구현 편의만으로 승인되지 않는다. exact proposed diff, predecessor blob, applicable owner adoption/decision receipt와 successor transaction이 모두 있어야 candidate에 포함한다.

### Admission Preconditions

다음 중 하나라도 충족되지 않으면 `S_base'`를 seal하지 않는다.

```text
configured_current_exit_code = 0
configured_current_failed_count = 0
configured_current_error_count = 0
unknown_failure_count = 0
evidence_absent_unclassifiable_count = 0
configured_current_denominator_reduction_count = 0
full_repository_denominator_reduction_count = 0
workflow_consolidation_application_delta_count = 0
rtc_durable_bundle_qualification = PASS
reseal_a_qualification = PASS
reseal_b_qualification = PASS
baseline_admission_run_a_chain = PASS
baseline_admission_run_b_chain = PASS
canonical_full_repository_run_a_exit = 0
canonical_full_repository_run_b_exit = 0
full_repository_denominator_identity_match = true
full_repository_dependency_inventory_identity_match = true
full_repository_canonical_result_identity_match = true
run_a_run_b_canonical_result_match = true
near_boundary_path_control = PASS
baseline_admission_dedicated_test_route = PASS
full_repository_test_membership_owner_adoption = PASS | not_applicable
full_repository_census_membership_added_without_adoption_count = 0
required_manifest_mutation_without_owner_adoption_count = 0
rtc_successor_bundle_adoption_pending = false
```

`baseline_admission_run_a_chain`과 `baseline_admission_run_b_chain`은 preflight부터 durable evidence retrieval까지의 composite chain 전체를 뜻한다. `canonical_full_repository_run_*_exit`은 그 chain 안의 stage 6만 뜻한다. 이 범위 정의는 qualification contract와 receipt schema의 field description으로 고정한다.

RTC repair가 successor bundle selection을 요구하면 owner가 그 selection을 current required validation으로 명시적으로 채택한 뒤에만 manifest transaction을 수행한다. 채택되지 않은 상태는 `rtc_successor_bundle_adoption_pending`으로 보존하며 `S_base'` seal을 차단한다. Baseline Admission Gate 자체의 current-required adoption도 같은 predecessor/successor identity 조건을 따른다.

Full-repository test membership의 `PASS`는 owner decision receipt와 additive membership을 요구한다. `not_applicable`은 membership을 추가하지 않았고 dedicated test route가 PASS이며 existing full-repository required execution denominator가 유지됐음을 뜻한다. 두 상태 모두 `full_repository_census_membership_added_without_adoption_count=0`이어야 하고, owner decision이 없거나 census가 new source를 unclassified로 남기면 admission precondition을 충족하지 못한다.

### Workflow Consolidation Handoff Assumption

tracked codebase에서 확인된 상태는 `architecture direction adopted / implementation pending`이다. 따라서 로드맵이 전제한 prior implementation을 재적용하려면 Change 10 이전에 최소 다음 입력이 필요하다.

```text
predecessor implementation commit/tree or patch identity
implementation-to-contract mapping
checkpoint mapping
prior application delta manifest
```

이 입력이 없으면 baseline restoration은 자체 axis에서 완료할 수 있지만 reapplication handoff는 `blocked_missing_predecessor_implementation_identity`로 남는다.

---

## 5. Repository Areas Affected

정확한 write allowlist는 Change 1 preflight에서 commit/blob identity와 함께 봉인한다. 아래는 코드 조사로 확인한 planned surface다.

### Code

Existing paths expected to change:

* `Iris/build/description/v2/tests/test_dvf_3_3_registry_runtime_compatibility_current.py`
* `Iris/build/description/v2/tests/test_dvf_3_3_current_route_required_validation_evidence_freshness_reseal.py`
* `Iris/build/description/v2/tests/test_dvf_3_3_current_source_authority_drift_verification_adoption_reseal.py`
* `Iris/build/description/v2/tools/build/validate_dvf_3_3_registry_runtime_compatibility.py`
* `Iris/build/description/v2/tools/build/run_dvf_3_3_registry_runtime_compatibility.py`, only if a successor durable bundle must be materialized
* `Iris/build/description/v2/tools/build/dvf_3_3_current_route_required_validation_evidence_freshness_reseal.py`
* `Iris/build/description/v2/tools/build/dvf_3_3_current_source_authority_drift_verification_adoption_reseal.py`
* `Iris/_docs/round3/round3_run_contract_tests.py`, only if exact failure/evidence output cannot be captured by a wrapper without changing route semantics
* `Iris/validation/clean_checkout/iris_clean_checkout_validation_common.py`, only for a generic reusable helper proven necessary by dependency census
* `Iris/validation/clean_checkout/run_iris_clean_checkout_validation.py`, additive execution-context applicability fields for composite-chain receipts
* `Iris/validation/clean_checkout/validate_iris_clean_checkout_validation.py`, execution-context identity validation without weakening canonical comparison
* `Iris/validation/clean_checkout/invoke_receipt_bound_full_gate.ps1`, propagate receipt-bound composite-chain context for each Run A/B
* `Iris/validation/clean_checkout/invoke_deterministic_compare.ps1`, consume and preserve execution-context identity in the existing canonical result comparison
* `Iris/validation/clean_checkout/contracts/full_repository_gate.json`, owner decision for new baseline-admission test source disposition and additive execution-context vocabulary only; existing denominator/command semantics may not be narrowed or redefined

Candidate new implementation root:

* `Iris/validation/baseline_admission/__init__.py`
* `Iris/validation/baseline_admission/iris_baseline_admission_common.py`
* `Iris/validation/baseline_admission/run_iris_baseline_admission.py`
* `Iris/validation/baseline_admission/validate_iris_baseline_admission.py`
* `Iris/validation/baseline_admission/invoke_iris_baseline_admission.ps1`
* `Iris/validation/baseline_admission/tests/test_iris_baseline_admission.py`
* `Iris/validation/baseline_admission/tests/test_reseal_output_isolation.py`
* `Iris/validation/baseline_admission/tests/test_windows_path_contract.py`
* `Iris/validation/baseline_admission/tests/test_rtc_durable_bundle_contract.py`

Baseline admission은 별도 admission contract로 구성하지만 canonical Clean-Checkout authority를 대체하지 않는다. `full_repository_gate.json`은 기존 command와 denominator semantics를 유지하고, 신설 test source의 owner decision에 따른 additive source disposition과 composite execution-context vocabulary만 허용한다. 과거 full-gate PASS나 standalone execution-context receipt는 어떤 경우에도 candidate의 composite stage-6 evidence가 아니다.

### Docs

* `docs/iris_current_validation_baseline_admissibility_restoration_plan.md`
* `docs/DECISIONS.md`, closeout 시 additive successor entry만 허용
* `docs/ARCHITECTURE.md`, admission readpoint와 path/canonical relation이 durable architecture가 될 때 additive update
* `docs/ROADMAP.md`, `S_base'`와 handoff 상태를 반영하는 additive update
* `docs/iris_test_lightweighting_terminal_closeout_recovery_plan.md`, immutable predecessor reference only; rewrite 금지

Candidate tracked authority/evidence paths:

* `Iris/validation/baseline_admission/authority/scope_and_conflict_decisions.json`
* `Iris/validation/baseline_admission/authority/rtc_successor_bundle_owner_adoption.json`, successor selection이 필요한 경우만
* `Iris/validation/baseline_admission/authority/full_repository_test_membership_owner_decision.json`, `adopted` 또는 `not_applicable_dedicated_route` decision
* `Iris/validation/baseline_admission/authority/admission_gate_current_required_owner_adoption.json`, gate 자체를 current required validation으로 채택하는 경우만
* `Iris/validation/baseline_admission/contracts/evidence_bundle.schema.json`
* `Iris/validation/baseline_admission/contracts/failure_ledger.schema.json`
* `Iris/validation/baseline_admission/contracts/admission_precondition_registry.json`
* `Iris/validation/baseline_admission/contracts/admission_negative_fixture_registry.json`
* `Iris/validation/baseline_admission/contracts/windows_path_contract.json`
* `Iris/validation/baseline_admission/contracts/rtc_durable_bundle_contract.json`
* `Iris/validation/baseline_admission/contracts/qualification_contract.json`
* `Iris/validation/baseline_admission/contracts/admission_receipt.schema.json`
* `Iris/validation/baseline_admission/evidence/baseline_admission_pointer.json`, terminal evidence pointer only
* `Iris/validation/baseline_admission/evidence/workflow_consolidation_reapplication_handoff.json`, exact predecessor implementation identity가 확인된 경우만

### Config

* `pytest.ini` — 변경하지 않는다. 신설 baseline-admission tests는 explicit-path dedicated route로 실행하며 configured-current testpaths에 추가하지 않는다.
* `Iris/_docs/round3/round3_pytest_source_classification.json` — 신설 baseline-admission tests 때문에 변경하지 않는다. configured-current tracked source denominator와 기존 source 분류를 그대로 보존한다.
* `Iris/_docs/round3/current_route_required_validations.json` — RTC successor bundle selection 또는 새 mandatory gate를 owner가 current required validation으로 명시적으로 채택하고 exact adoption receipt가 있을 때만 additive/successor transaction으로 변경한다. adoption 없는 implementation transaction은 금지한다.
* `Iris/validation/clean_checkout/contracts/full_repository_gate.json` — 신설 `baseline_admission` tests는 configured-current에는 포함하지 않는다. Owner decision이 `adopted`이면 `explicit_current_required_sources` membership만 additive update하고, `not_applicable_dedicated_route`이면 existing required execution denominator를 유지하면서 census가 dedicated-route disposition을 명시적으로 인식해야 한다. Composite-chain execution-context vocabulary도 additive로 선언한다. 어느 branch도 기존 required source, standalone validation 또는 dependency inventory를 제거하지 않는다.
* `.gitignore` — 기본적으로 변경하지 않는다. broad unignore 금지.

### Generated Artifacts

모든 attempt-local artifact는 caller-supplied repository-external root 아래에 둔다.

```text
<external-durable-root>/iris-current-baseline-admission/<closure-id>/
  contracts/
  s-base-forensics/
    attempt-<id>/
      subject.json
      environment.json
      path-manifest.json
      command.json
      collection.json
      pytest.raw.log
      stdout.log
      stderr.log
      junit.xml | junit-status.json
      node-ledger.json
      root-cause-graph.json
      rtc-required-gate.json
  candidates/<candidate-id>/
    allowed-delta-manifest.json
    configured-current/
    rtc/
    reseal-a/
    reseal-b/
  qualification/<candidate-id>/
    run-a/
    run-b/
    path-control-near-boundary/
    comparison.json
    qualification-manifest.json
  admission/<candidate-id>/
    positive-receipt.json
    negative-matrix.json
    precondition-negative-coverage.json
  review/<candidate-id>/
    machine-report.json
    independent-review.json
    owner-seal.json
    hash-manifest.json
  handoff/<candidate-id>/
    workflow-consolidation-reapplication-handoff.json
    deviation-ledger.json
```

Temporary checkout, pytest base-temp, uv cache와 raw scratch data는 durable root와 분리한다. Cleanup 전에 failure-minimum evidence의 retrieval/hash 검증을 완료해야 한다.

---

## 6. Planned Changes

### Change 1 — Scope, claim, decision and durable-evidence contract lock

Purpose:

Repair 전에 authority boundary, unresolved roadmap decisions, evidence schema와 allowed write surface를 고정한다.

Files:

* `Iris/validation/baseline_admission/authority/scope_and_conflict_decisions.json`
* `Iris/validation/baseline_admission/contracts/evidence_bundle.schema.json`
* `Iris/validation/baseline_admission/contracts/failure_ledger.schema.json`
* `Iris/validation/baseline_admission/contracts/admission_precondition_registry.json`
* `Iris/validation/baseline_admission/contracts/admission_negative_fixture_registry.json`
* `Iris/validation/baseline_admission/iris_baseline_admission_common.py`
* `Iris/validation/baseline_admission/tests/test_iris_baseline_admission.py`

Implementation Notes:

* `S_base` full commit/tree, parent relation과 plan blob identity를 기록한다.
* 이 계획의 conflict decision table을 machine-readable contract로 materialize한다.
* exact allowed path list와 owner를 봉인한다. 이후 새 path가 필요하면 mutation 전에 additive amendment와 review가 필요하다.
* current authority mutation classes를 `RTC successor selection`, `baseline admission gate adoption`, `canonical full-repository test membership`으로 나누고 각 class의 owner adoption/decision requirement와 blocked state를 봉인한다.
* 신설 `baseline_admission` test의 configured-current membership은 `excluded_by_declared_testpath_boundary`로 선언한다. Canonical full-repository membership decision은 `owner_adopted_explicit_current_required_source | owner_dispositioned_not_applicable_dedicated_route` 중 하나이며, 두 denominator를 하나의 count로 합치지 않는다.
* admission precondition을 stable `precondition_id`, axis, predicate와 evidence field로 구성한 machine-readable registry로 만든다. Negative fixture registry는 모든 precondition ID를 하나 이상의 exact rejection fixture에 역참조해야 한다.
* schema validation은 precondition 추가/이름 변경 시 negative mapping이 같이 갱신되지 않으면 실패한다. 고정 `negative_case_count` 숫자는 완전성 보증으로 사용하지 않는다.
* evidence identity schema는 최소 `subject`, `attempt`, `route`, `command`, `denominator`, `environment`, `checkout/path`, `raw log`, `JUnit state`, `diagnostic artifact`, `hash`, `primary/propagated`, `root cause`, `disposition`을 요구한다.
* evidence writer failure, JUnit non-production, retrieval failure와 hash mismatch를 각각 named fail-closed state로 둔다.
* durable root는 subject checkout, temp root, Run A root와 Run B root에서 모두 disjoint해야 한다.
* `baseline_restoration`, `machine_validation`, `independent_review`, `owner_seal`, `admission`, `handoff` vocabulary를 분리한다.
* plan-local tooling은 Iris runtime Lua, source facts, rendered/runtime/package authority를 쓰지 못한다.

Validation:

```text
historical_s_base_immutable = true
application_mutation_before_admission = false
allowed_write_surface_complete = true
durable_root_outside_subject_checkout = true
evidence_capture_fail_closed = true
admission_precondition_registry_complete = true
every_admission_precondition_has_negative_case = true
uncovered_precondition_count = 0
orphan_negative_case_count = 0
bare_complete_token_count = 0
```

---

### Change 2 — Frozen S_base forensic reproduction and exact failure census

Purpose:

Repair 전에 `S_base`의 configured-current failure를 exact command와 qualified/observed environment에서 재현하고 모든 raw evidence를 보존한다.

Files:

* `Iris/validation/baseline_admission/run_iris_baseline_admission.py`
* `Iris/validation/baseline_admission/invoke_iris_baseline_admission.ps1`
* `Iris/validation/baseline_admission/contracts/qualification_contract.json`

Implementation Notes:

* current dirty workspace가 아닌 `S_base` exact object를 repository-external disposable clone에 materialize한다.
* source checkout은 시작 전 tracked/non-ignored untracked clean이어야 하며 ignored state도 before/after manifest로 비교한다.
* configured-current collection을 먼저 수행해 source count, ordered node IDs, deselection/skip state, mixed-item override와 denominator hash를 기록한다.
* configured-current execution에서 raw stdout/stderr, pytest result plugin output, `--junitxml` output 또는 explicit no-JUnit reason을 외부 result root에 기록한다.
* exact current runner도 별도로 실행해 current/historical/diagnostic non-substitution을 보존한다.
* 두 reseal class의 5개/4개 node ID, setup exception과 upstream root-cause edge를 개별 ledger row로 만든다.
* RTC standalone required-gate의 expected/observed failure code, selected bundle ID, resolved destination과 path lengths를 기록한다.
* remaining 2 failure node는 raw evidence가 확보되기 전까지 `evidence_absent_unclassifiable`이며 어떠한 waiver도 적용하지 않는다.
* 실행 전후 `S_base` checkout의 tracked bytes/status가 같아야 한다. mutation이 발생하면 그 run은 evidence-producing FAIL이며 repair evidence로만 보존한다.

Validation:

```text
s_base_commit = 671c7b928ad5a1dbf26ea76949462fa8a7287903
s_base_tree = 20bbbdb919fa97a44e03c1f1cb9ea0a6973fb1db
s_base_content_mutation_count = 0
observed_nonpassing_node_count = 11 or fresh evidence-bound successor observation
propagated_node_count = 9
known_setup_root_cause_count = 2
raw_evidence_complete = true
junit_state_explicit = true
durable_evidence_retrievable = true
```

과거 `11`과 다른 수치가 재현되면 숫자를 맞추지 않고 `reproduction_drift=true`라는 attempt-level observation flag로 기록해 attribution 입력으로 사용한다. 이 flag 자체는 canonical failure category가 아니다. 같은 exact subject/environment/root class의 control rerun에서도 비결정성이 입증된 경우에만 기존 canonical category 아래 `nondeterministic_reproduction` cause subtype을 부여하고, 그 전에는 개별 node를 evidence-based category로 계속 분류한다.

---

### Change 3 — Canonical failure attribution and disposition ledger

Purpose:

모든 non-passing node와 primary root cause를 evidence에 결속하고 repair eligibility를 결정한다.

Files:

* `Iris/validation/baseline_admission/contracts/failure_ledger.schema.json`
* `Iris/validation/baseline_admission/validate_iris_baseline_admission.py`
* external `node-ledger.json`, `root-cause-graph.json`, `rtc-hypothesis-report.json`

Implementation Notes:

Canonical high-level category:

```text
orchestration_failure
environment_contract_violation
subject_finding
evidence_absent_unclassifiable
propagated_from_root_cause
```

Canonical cause subtype:

```text
current_contract_defect
validation_tooling_defect
evidence_materialization_defect
windows_path_contract_defect
rtc_bundle_materialization_defect
gate_reason_classification_defect
stale_governance_expectation
current_subject_contract_finding
nondeterministic_reproduction
```

* 모든 propagated row는 exact upstream failure identity를 가져야 한다.
* node count와 unique root-cause count를 별도 field로 유지한다.
* RTC mismatch는 `H1 gate reason classification`, `H2 stale expected/governance state`, `H3 actual durable materialization defect`, `H4 Windows path observation defect`를 독립 판정한다. H4는 codebase path behavior를 반영한 추가 가설이며 H1~H3를 자동 배제하지 않는다.
* remaining 2 failures는 failure signature가 아니라 raw assertion/trace, exact inputs와 counterfactual/focused reproduction으로 분류한다.
* `subject_finding`은 이 계획 안에서 수정하지 않는다. 별도 correction owner와 required successor input을 기록하고 baseline admission을 차단한다.
* evidence가 부족하면 `evidence_absent_unclassifiable`로 남기며 `non_blocking`, `accepted risk` 또는 owner prose로 PASS 처리하지 않는다.

Validation:

```text
all_existing_nodes_have_evidence_bound_disposition = true
primary_and_propagated_relation_complete = true
preexisting_used_as_waiver_count = 0
unclassified_repair_delta_authorization_count = 0
```

---

### Change 4 — Windows path contract and preflight qualification

Purpose:

`LongPathsEnabled=0`에서도 declared qualified root range 안의 configured-current, RTC와 reseal workflow가 incidental path exception 없이 동작하도록 path budget과 named rejection boundary를 확립한다.

Files:

* `Iris/validation/baseline_admission/contracts/windows_path_contract.json`
* `Iris/validation/baseline_admission/iris_baseline_admission_common.py`
* `Iris/validation/baseline_admission/tests/test_windows_path_contract.py`
* `Iris/build/description/v2/tests/clean_checkout_test_paths.py`, only if the existing external allocator cannot expose the required budget/result identity without a generic additive extension

Implementation Notes:

* logical artifact identity, repository-relative physical layout, checkout absolute root와 external result root를 분리한다.
* tracked full repository, selected RTC bundle, 두 reseal roots와 generated temp/final suffix의 longest-path census를 수행한다.
* budget 식은 다음을 contract field로 materialize한다.

```text
checkout_root_length
+ longest_required_relative_path
+ worst_case_generated_suffix
+ separator_allowance
+ safety_margin
<= qualified_materialized_path_limit
```

* existing clean-checkout contract의 root `56` / materialized `259`는 precedent이지 자동 채택값이 아니다. fresh census와 두 reseal/RTC actual suffix를 반영해 baseline-admission-specific 값을 봉인한다.
* normal admitted root, near-boundary admitted root, one-character over-budget root를 fixture로 만든다.
* over-budget condition은 clone/test 중간 `FileNotFoundError`가 아니라 `windows_path_contract_rejected` preflight로 종료한다.
* test/evidence output은 short opaque run IDs를 사용하고 descriptive long names는 manifest metadata로 보존한다.
* physical shortening이 필요하면 Git rename과 logical identity mapping을 사용한다. historical embedded path strings/hash evidence는 rewrite하지 않는다.
* `core.longpaths=true`와 Python long-path-safe open helper는 defense in depth다. 둘 중 어느 것도 declared budget/preflight를 제거하지 않는다.

Validation:

```text
long_paths_enabled_zero_supported_in_qualified_range = true
path_budget_defined = true
supported_range_defined = true
normal_root_preflight = PASS
near_boundary_root_preflight = PASS
out_of_range_root = windows_path_contract_rejected
logical_identity_changed_count = 0
```

---

### Change 5 — RTC canonical durable-bundle resolution and parity restoration

Purpose:

RTC required gate가 canonical durable destination을 path-safe하게 resolve하고, member/parity 검사를 통과한 뒤 의도된 toolchain freshness 또는 이후 실제 verdict에 도달하도록 복구한다.

Files:

* `Iris/validation/baseline_admission/contracts/rtc_durable_bundle_contract.json`
* `Iris/build/description/v2/tools/build/validate_dvf_3_3_registry_runtime_compatibility.py`
* `Iris/build/description/v2/tools/build/run_dvf_3_3_registry_runtime_compatibility.py`, conditional successor promotion only
* `Iris/build/description/v2/tests/test_dvf_3_3_registry_runtime_compatibility_current.py`
* `Iris/validation/baseline_admission/tests/test_rtc_durable_bundle_contract.py`
* `Iris/_docs/round3/current_route_required_validations.json`, only if the owner explicitly adopts the successor bundle selection as a current required validation
* `Iris/validation/baseline_admission/authority/rtc_successor_bundle_owner_adoption.json`, required before any successor selection transaction

Implementation Notes:

* canonical live side를 `_docs/round3/registry_runtime_compatibility/bundles/<bundle_id>`로 봉인한다.
* `durable_bundle_manifest.json`의 11-role inventory, unique destinations, bytes, SHA-256, parity, tracking/ignore visibility와 lifecycle state를 검증한다.
* promotion source paths는 provenance로 보존하지만 live consumer가 ignored attempt staging을 runtime dependency처럼 읽지 않게 한다.
* `Path.is_file()`이 Windows path 조건 때문에 false가 되는 경우와 실제 missing/byte drift를 다른 error code로 분리한다.
* path preflight를 통과한 canonical destination에서 실제 drift가 없다면 historical bundle bytes는 변경하지 않고 resolver/gate-reason correction만 수행한다.
* actual destination/member defect가 확인되면 historical bundle을 고치지 않고 기존 `promotion_sources()`와 atomic short staging precedent를 통해 successor bundle을 생성한다.
* successor bundle materialization과 current-required selection adoption을 서로 다른 transaction으로 다룬다. materialization은 owner adoption을 암시하지 않는다.
* successor selection은 owner가 exact old/new bundle ID, manifest predecessor blob과 proposed diff를 명시적으로 채택한 경우에만 additive lifecycle event와 required manifest transaction으로 처리하며 old bundle evidence를 유지한다.
* successor bundle이 생성됐지만 adoption receipt가 없으면 live manifest를 쓰지 않고 `rtc_successor_bundle_adoption_pending`으로 종료한다. 이 상태는 configured-current/admission 입력으로 전달되어 `S_base'` seal을 차단한다.
* current-validation/reseal tooling은 adoption receipt를 생성하거나 owner decision을 추정할 수 없고, adoption 없는 write attempt는 fail-closed evidence다.
* durable/parity repair 뒤 required gate의 next observed reason을 fresh evidence로 기록한다. 기대 reason을 hard-code해 실제 subject finding을 가리지 않는다.

Validation:

```text
historical_bundle_mutation_count = 0
canonical_durable_destination_selected = true
promotion_provenance_role_explicit = true
promotion_role_count = 11
member_inventory_relation_verified = true
hash_relation_verified = true
byte_relation_verified = true
consumer_resolution_verified = true
path_observation_false_drift_count = 0
required_manifest_mutation_without_owner_adoption_count = 0
rtc_successor_bundle_adoption_pending = false
rtc_global_pass_claimed = false
```

---

### Change 6 — Reseal current-validation mode, external output isolation and 9-node observation

Purpose:

두 reseal workflow가 supported checkout root에서 tracked evidence를 정확히 읽고, regeneration이 필요할 때에도 live manifest/docs를 쓰지 않는 explicit current-validation context에서 external root만 사용하도록 복구한다.

Files:

* `Iris/build/description/v2/tools/build/dvf_3_3_current_route_required_validation_evidence_freshness_reseal.py`
* `Iris/build/description/v2/tools/build/dvf_3_3_current_source_authority_drift_verification_adoption_reseal.py`
* 두 runner/validator wrappers, CLI propagation이 필요한 경우
* `Iris/build/description/v2/tests/test_dvf_3_3_current_route_required_validation_evidence_freshness_reseal.py`
* `Iris/build/description/v2/tests/test_dvf_3_3_current_source_authority_drift_verification_adoption_reseal.py`
* `Iris/validation/baseline_admission/tests/test_reseal_output_isolation.py`

Implementation Notes:

* tool에 explicit execution context를 도입한다.

```text
authority_adoption
= existing explicit writer semantics

current_validation
= tracked live manifest/docs are read-only
+ all generated evidence under caller-supplied external root
+ authority mutation attempt fails closed
```

* 기존 CLI default/authority behavior를 조용히 뒤집지 않는다. configured-current tests가 `current_validation`을 명시한다.
* `write_phase3_update_manifest()`는 current-validation context에서 live manifest를 write하지 않고 in-memory projection과 external report를 생성한다.
* `write_phase6_final()`은 current-validation context에서 claim-boundary/ledger 문서를 external root에만 쓴다.
* test class setup은 long tracked report existence에 의존해 repository-local runner로 fallback하지 않는다. 짧은 external path를 할당하고 exact tracked seed/candidate projection을 materialize한 뒤 runner/validator에 `--root`와 context를 명시한다.
* test body는 class-owned external artifact root를 읽고, tracked `ROOT`는 immutable seed/reference로만 사용한다.
* primary setup failure가 나도 command, stdout/stderr, path manifest와 JUnit state를 cleanup 전에 durable sink로 복사한다.
* teardown은 successful temp cleanup만 수행하며 durable failure evidence를 지우지 않는다.
* setup repair 후 두 class의 5+4 node를 모두 실제 실행해 PASS/FAIL을 node별로 기록한다. 새 failure가 나타나면 Change 3 attribution으로 되돌아간다.
* live manifest, source/rendered/runtime/package와 tracked docs before/after hash가 같아야 한다.
* 현재 발견된 test-time live authority writer가 predecessor execution에도 영향을 주었을 가능성은 additive non-decision trace로 기록한다: `test_time_authority_write_predecessor_implication=unadjudicated_out_of_scope`. 이 trace는 predecessor PASS를 재평가하거나 historical evidence를 rewrite하지 않는다.

Validation:

```text
reseal_a_qualified = true
reseal_b_qualified = true
repository_local_generated_write_count = 0
live_required_manifest_mutation_count = 0
tracked_claim_doc_mutation_count = 0
tracked_artifact_lookup_contract_satisfied = true
final_write_contract_satisfied = true
durable_failure_evidence_survives_setup_failure = true
previously_blocked_9_nodes_observed = true
test_time_authority_write_predecessor_implication = unadjudicated_out_of_scope
```

---

### Change 7 — Remaining blocker resolution and S_repair_candidate construction

Purpose:

Attribution이 허용한 validation-owned repair만 결합하고 fresh configured-current가 green인 immutable candidate를 만든다.

Files:

* Change 3~6에서 승인된 exact validation paths only
* `Iris/tools/package_iris.ps1`, `Iris/test/validate_residual_refactor_surfaces.ps1`, `Iris/test/run_residual_refactor_acceptance.ps1`, only for PowerShell module-autoload-independent SHA-256 calculation required by configured-current execution
* `Iris/build/description/v2/tests/conftest.py`, `Iris/build/tests/test_recipe_evidence.py` and their existing external-output environment contract, only to keep legacy generated outputs outside the candidate checkout
* `Iris/_docs/refactor/repository_evidence_lightweighting/protected_surface_successor_manifest.json` and `Iris/_docs/refactor/repository_evidence_lightweighting/required_validation_adoption_receipt.successor.json`, only for an additive owner-approved successor binding of the changed clean-checkout validation inputs
* external `allowed-delta-manifest.json`
* external `before-after-classification.json`
* external `configured-current` evidence bundle

Implementation Notes:

* 각 candidate commit은 `S_base` 또는 직전 rejected successor와 parent relation을 명시한다.
* delta row마다 path/blob, owner, root cause, repair class, test evidence와 rollback unit을 기록한다.
* RTC/path/reseal/remaining failures의 독립성에 따라 repair commit을 분리한다.
* unrelated formatting, cleanup, refactor, consolidation application 또는 runtime changes를 포함하지 않는다.
* configured-current가 실제로 소비하는 PowerShell validation tools는 `Get-FileHash` cmdlet의 profile/module autoload에 의존하지 않는다. SHA-256 계산은 built-in cmdlet이 없는 isolated `uv` child environment에서도 동일하게 동작해야 한다.
* legacy recipe evidence validation은 `IRIS_CLEAN_CHECKOUT_LEGACY_OUTPUT_ROOT`를 받은 경우 그 repository-external root만 사용한다. candidate checkout의 `Iris/output/` write는 source mutation으로 qualification을 실패시킨다.
* clean-checkout runner 또는 full-gate contract를 변경할 경우, 기존 required-validation adoption과 protected-surface chain에는 predecessor bytes를 보존한 additive successor binding을 추가한다. 과거 receipt나 historical manifest row를 rewrite하지 않는다.
* 사용자의 untracked `Iris/_docs/refactor/codebase_optimization_followup/` overlay는 baseline candidate의 입력이 아니다. residual validation은 overlay가 clean checkout에 없을 때 empty optional overlay로 처리하고, 존재할 때만 기존 identity/row checks를 적용한다.
* `subject_finding` correction이 필요하면 현재 candidate를 seal하지 않고 `baseline_restoration=blocked_subject_finding_requires_owner_correction`으로 별도 plan/owner handoff에 종료한다. 별도 correction commit은 돌아왔을 때 새 `S_repair_candidate_n`의 explicit input이다.
* configured-current collection denominator가 `S_base` 대비 달라지면 모든 delta를 source addition/removal/classification/mixed override/required union별로 설명해야 한다.
* 새 regression test는 denominator addition으로 명시하며 denominator reduction을 상쇄하는 숫자로 사용하지 않는다.
* fresh configured-current의 exit, pass/fail/error/skip/deselect, ordered node IDs, source set과 JUnit을 보존한다.

Validation:

```text
candidate_parent_relation_explicit = true
all_candidate_deltas_classified = true
unclassified_delta_count = 0
workflow_consolidation_application_delta_count = 0
runtime_product_delta_count = 0
skip_added_count = 0
xfail_added_count = 0
ignore_added_count = 0
deselect_added_count = 0
configured_current_denominator_reduction_count = 0
full_repository_denominator_reduction_count = 0
configured_current_exit_code = 0
configured_current_failed_count = 0
configured_current_error_count = 0
subject_finding_count = 0
```

---

### Change 8 — Canonical mandatory full-repository Run A/B, path control and immutable S_base' seal

Purpose:

Candidate가 local residue, run nondeterminism, checkout location 또는 cross-run mutable state에 의존하지 않음을 canonical mandatory full-repository gate로 증명하고 exact qualifying commit/tree만 `S_base'`로 봉인한다.

Files:

* `Iris/validation/baseline_admission/run_iris_baseline_admission.py`
* `Iris/validation/baseline_admission/invoke_iris_baseline_admission.ps1`
* `Iris/validation/baseline_admission/contracts/qualification_contract.json`
* `Iris/validation/clean_checkout/run_iris_clean_checkout_validation.py`, additive receipt applicability fields
* `Iris/validation/clean_checkout/validate_iris_clean_checkout_validation.py`, context-aware receipt validation
* `Iris/validation/clean_checkout/invoke_receipt_bound_full_gate.ps1`, preserve launcher semantics and propagate explicit execution context
* `Iris/validation/clean_checkout/invoke_deterministic_compare.ps1`, preserve raw canonical comparison and require matching context identity
* `Iris/validation/clean_checkout/contracts/full_repository_gate.json`, owner-decisioned test disposition and execution-context vocabulary only
* external Run A/B bundles, canonical comparison and near-boundary path-control bundle

Implementation Notes:

* Run A/B는 `git clone --no-local`로 만든 independent fresh checkout을 사용하고 object store, full-gate work root, temp/cache, materialized input과 result root를 공유하지 않는다.
* determinism A/B는 동일한 declared normal checkout slot에서 순차 실행한다. Run A checkout을 source non-mutation/retrieval 검증 후 제거하고 empty-slot proof를 남긴 뒤, 같은 absolute slot에 Run B를 새 object store로 clone한다. 이 방식은 existing comparator가 canonical result 안의 implementation path identity까지 raw-byte 비교하는 현재 계약을 보존하면서 run identity만 바꾼다.
* 두 run은 같은 candidate commit/tree, command contract, denominator contract, dependency inventory contract, uv/Python/pytest identity와 environment contract를 사용한다. Run A의 checkout/object/work/temp/cache/materialized input은 Run B에서 재사용하지 않고 durable result bundle만 compare input으로 읽는다.
* 각 Run A/B는 `preflight → collection → focused RTC/reseal qualification → exact-current → configured-current → existing canonical mandatory full-repository gate → source non-mutation → durable evidence retrieval` 순서로 fail-closed 실행한다.
* canonical full-repository 단계는 각 checkout 안의 `invoke_receipt_bound_full_gate.ps1`을 통해 `run_iris_clean_checkout_validation.py full-gate`를 실제 호출한다. `full_repository_gate.json`의 기존 pytest selection, standalone validations, source disposition과 dependency census를 subset으로 줄이거나 baseline-specific 의미로 재정의하지 않는다.
* Run A/B의 `full_run_receipt.json`, `canonical_full_result.json`과 orchestration receipt를 exact candidate에 결속하고, `invoke_deterministic_compare.ps1`로 raw canonical result byte equality를 검증한다. 비교 대상에는 `test_inventory_sha256`와 `required_dependency_inventory.sha256`가 포함된다.
* 각 full-gate receipt의 applicability에는 `execution_context=composite_baseline_admission_chain_stage_6`, stage index, 선행 1~5단계 receipt-set hash와 qualification-contract identity를 기록한다. 이 context는 owner가 contract token으로 ratify하며, context 누락/불일치 또는 historical standalone full-gate receipt와의 나이브한 equivalence 주장은 rejection이다.
* Run A 결과를 Run B input으로 복사하지 않는다. 비교기는 immutable retrieved receipt와 canonical result만 읽는다.
* Windows path invariance는 별도 `Path Control P`에서 검증한다. P는 computed near-boundary admitted root의 세 번째 independent fresh checkout에서 A/B와 같은 전체 chain과 canonical full-repository gate를 실행하고, Run A와 path-normalized semantic receipt를 비교한다. 따라서 A/B mismatch는 determinism 문제, A/P mismatch는 path dependence로 각각 귀속할 수 있다.
* A/B 또는 A/P mismatch가 발생하면 자동 재시도로 덮지 않는다. 같은 root-length class의 추가 control rerun은 원인 분리를 위한 rejected-attempt evidence이며 새로운 candidate qualification으로 계산하지 않는다.
* absolute root, timestamps, duration과 randomized attempt ID는 canonical comparison에서 제외할 수 있지만 raw evidence에는 보존한다. 제외 field list는 contract에 고정한다.
* 신설 `baseline_admission` tests는 configured-current denominator에 포함되지 않으며 dedicated validation으로 실행한다. Owner decision이 `PASS`이면 canonical full-repository census의 additive `explicit_current_required_sources`로 포함하고, adoption 없이 membership을 추가한 candidate는 qualified로 간주하지 않는다.
* Owner decision이 `not_applicable`이면 신설 tests를 required execution membership에 추가하지 않고 existing denominator로 full gate를 실행한다. 이 branch는 dedicated test route PASS, explicit owner disposition, unclassified source count `0`과 membership-added-without-adoption count `0`을 모두 요구한다.
* candidate run이 실패하면 그 commit/tree를 `S_base'`로 부르지 않는다. 수정은 새 successor candidate에서 수행한다.
* qualification PASS 뒤 external seal receipt가 exact commit/tree를 `S_base'` role에 결속한다. tracked artifact가 자신의 containing commit을 self-bind하지 않는다.

Validation:

```text
run_a_fresh_checkout = true
run_b_fresh_checkout = true
path_control_p_fresh_checkout = true
run_a_source_dirty_after = 0
run_b_source_dirty_after = 0
path_control_p_source_dirty_after = 0
cross_run_mutable_artifact_reuse_count = 0
canonical_full_repository_run_a_exit = 0
canonical_full_repository_run_b_exit = 0
canonical_full_repository_path_control_exit = 0
full_repository_denominator_identity_match = true
full_repository_denominator_reduction_count = 0
full_repository_dependency_inventory_identity_match = true
full_repository_canonical_result_identity_match = true
full_repository_run_a_run_b_raw_canonical_bytes_equal = true
full_repository_execution_context_identity_match = true
full_repository_standalone_receipt_equivalence_claimed = false
run_a_path_control_semantic_identity_match = true
configured_current_green_both_runs = true
configured_current_green_path_control = true
near_boundary_path_control = PASS
baseline_admission_dedicated_test_route = PASS
full_repository_test_membership_owner_adoption = PASS | not_applicable
full_repository_census_membership_added_without_adoption_count = 0
run_a_source_mutation_count = 0
run_b_source_mutation_count = 0
path_control_source_mutation_count = 0
s_base_prime_exact_identity_bound = true
```

---

### Change 9 — Fail-closed Baseline Admission Gate implementation and bounded enforcement proof

Purpose:

Exact baseline admissibility를 검사하는 fail-closed gate를 구현하고 synthetic mutator harness에서 ordering을 증명하되, 아직 존재하지 않는 workflow consolidation application entrypoint에 실제 결속됐다고 과대 주장하지 않는다.

Files:

* `Iris/validation/baseline_admission/contracts/admission_receipt.schema.json`
* `Iris/validation/baseline_admission/validate_iris_baseline_admission.py`
* `Iris/validation/baseline_admission/invoke_iris_baseline_admission.ps1`
* `Iris/validation/baseline_admission/tests/test_iris_baseline_admission.py`
* `Iris/_docs/round3/current_route_required_validations.json`, only if owner explicitly adopts the admission gate as a current required validation

Implementation Notes:

Gate input:

```text
candidate commit/tree
working-tree cleanliness
qualification contract/blob identity
configured-current result identity
Run A/B receipts and comparison
canonical mandatory full-repository Run A/B receipts and comparison
near-boundary path-control receipt
full-gate composite execution-context identity
environment/uv/Python/pytest identity
Windows path-contract identity
RTC qualification identity
reseal A/B qualification identity
durable evidence hash manifest
unresolved blocker counts
required current-authority owner-adoption receipts, when applicable
admission precondition registry and negative-fixture coverage receipt
```

* gate는 receipt existence가 아니라 subject/applicability/hash/producer chain을 검증한다.
* gate execution exception, missing schema, unreadable durable bundle 또는 stale receipt는 rejection이다.
* machine failure를 owner seal로 bypass할 수 없다.
* gate implementation, synthetic enforcement proof와 real application-entry binding을 별도 state field로 유지한다.
* negative matrix는 hand-maintained count가 아니라 Change 1의 precondition registry에서 생성한다. 각 precondition은 최소 한 fixture가 해당 predicate만 invalid하게 만들고 gate rejection과 mutator non-call을 증명해야 한다.
* generic synthetic harness는 gate PASS receipt를 확인한 뒤에만 mock mutator callback을 실행한다. 이 결과는 `gate_before_application_mutation_synthetic=true`까지만 증명한다.
* 현재 저장소에는 workflow consolidation mutator entrypoint가 없으므로 `baseline_admission_gate_real_entry_binding=pending_absent_application_entrypoint`로 기록한다. synthetic proof를 real enforced state 또는 `active_fail_closed`로 표현하지 않는다.
* Change 10 handoff에는 future application entry가 materialize될 때 first operation으로 실행할 exact mandatory wrapper command, accepted receipt schema/hash/subject checks와 same-transaction mutation rule을 기록한다. 실제 entry가 생기면 별도 successor validation에서 real binding을 증명한다.
* admission receipt는 one-time mutable token이 아니라 exact immutable subject applicability proof다. 다른 commit/tree 또는 dirty overlay에는 적용되지 않는다.

Positive case:

```text
qualified exact S_base' + matching receipts -> admitted
```

Required negative cases:

```text
known-bad S_base -> rejected
wrong commit -> rejected
wrong tree -> rejected
dirty checkout -> rejected
path over budget -> rejected
missing raw/JUnit-state evidence -> rejected
tampered durable hash -> rejected
stale environment/toolchain -> rejected
RTC parity mismatch -> rejected
reseal qualification missing -> rejected
canonical full-repository Run A/B receipt missing or non-PASS -> rejected
full-repository denominator/dependency/canonical identity mismatch -> rejected
full-gate composite execution context missing or mismatched -> rejected
near-boundary path-control receipt missing or non-PASS -> rejected
configured-current denominator reduction count > 0 -> rejected
full-repository denominator reduction count > 0 -> rejected
workflow consolidation application delta count > 0 -> rejected
full-repository test membership added without owner adoption -> rejected
membership not_applicable with missing dedicated-route PASS or unclassified source -> rejected
required-manifest mutation without owner adoption -> rejected
RTC successor bundle adoption pending -> rejected
unresolved finding count > 0 -> rejected
gate process exception -> rejected
```

Validation:

```text
gate_fail_closed = true
baseline_admission_gate_implementation = fail_closed
baseline_admission_gate_enforcement_proof = synthetic_harness_only
baseline_admission_gate_real_entry_binding = pending_absent_application_entrypoint
gate_before_application_mutation_synthetic = true
known_bad_s_base_rejected = true
qualified_s_base_prime_accepted = true
negative_case_count >= admission_precondition_count
every_admission_precondition_has_negative_case = true
uncovered_precondition_count = 0
orphan_negative_case_count = 0
mutator_called_on_rejected_case_count = 0
stale_subject_receipt_accepted_count = 0
real_application_entry_enforcement_claimed = false
```

---

### Change 10 — Axis-qualified closeout and workflow consolidation reapplication handoff

Purpose:

Baseline restoration을 자체 claim boundary 안에서 closeout하고, 확인된 prior implementation을 `S_base'`에서 새 identity chain으로 재적용하기 위한 handoff를 만든다.

Files:

* `Iris/validation/baseline_admission/evidence/baseline_admission_pointer.json`
* `Iris/validation/baseline_admission/evidence/workflow_consolidation_reapplication_handoff.json`
* `docs/DECISIONS.md`
* `docs/ARCHITECTURE.md`
* `docs/ROADMAP.md`

Implementation Notes:

Historical chain:

```text
S_base
-> prior consolidation implementation, only if exact identity is supplied
-> prior blocked terminal attempt
```

Successor chain:

```text
S_base'
-> consolidation reapplication
-> S_impl'
-> tooling review
-> protocol qualification
-> new measurement
-> S_terminal'
```

* prior implementation commit/patch가 tracked evidence로 확인되지 않으면 `implementation_identity_state=missing`과 blocker를 기록한다. 구현을 추정하거나 architecture prose에서 patch를 합성하지 않는다.
* handoff `ready`는 exact predecessor implementation identity뿐 아니라 future application entry가 호출해야 할 mandatory admission wrapper argv, accepted receipt schema/hash/subject checks, mutation-before/after ordering과 same-receipt rule을 machine-readable field로 가져야 한다. 어느 하나라도 없으면 `ready`를 사용하지 않는다.
* 이 wrapper contract가 준비되어도 실제 application entrypoint가 현재 없으므로 real entry binding state는 `pending_absent_application_entrypoint`다. `ready`는 reapplication input contract의 준비 상태이지 실제 enforcement PASS가 아니다.
* 재적용 가능한 것은 implementation delta, design structure, contract/checkpoint mapping뿐이다.
* old machine PASS, tooling review, protocol qualification, timing, measurement와 terminal receipt는 상속하지 않는다.
* baseline repair와 reapplication patch가 충돌하면 path/hunk, chosen resolution, semantic reason과 reviewer disposition을 deviation ledger에 기록한다. silent conflict resolution은 금지한다.
* minimal tracked pointer는 external bundle retrieval key, bundle hash, exact `S_base'` identity와 claim ceiling을 결속한다.
* docs update는 additive successor record이며 historical `S_base`와 predecessor closeout prose를 rewrite하지 않는다.
* final state는 다음처럼 axis-qualified하게 기록한다.

```text
baseline_restoration = complete
machine_validation = PASS
independent_review = PASS
owner_seal = PASS
s_base_prime = admitted_validation_baseline
baseline_admission_gate_implementation = fail_closed
baseline_admission_gate_enforcement_proof = synthetic_harness_only
baseline_admission_gate_real_entry_binding = pending_absent_application_entrypoint
workflow_consolidation_reapplication_handoff = ready | blocked_missing_predecessor_implementation_identity
workflow_consolidation_terminal = not_run
```

Validation:

```text
historical_chain_preserved = true
successor_chain_defined = true
prior_pass_inherited = false
old_measurement_reused = false
old_terminal_receipt_reused = false
reapplication_delta_identity_recorded = true when handoff ready
mandatory_admission_wrapper_command_bound = true when handoff ready
same_receipt_subject_and_hash_rule_bound = true when handoff ready
real_application_entry_enforcement_claimed = false
silent_conflict_resolution_count = 0
machine_review_owner_axes_separate = true
claim_boundary_overreach_count = 0
```

---

## 7. Validation Plan

### Automated Validation

모든 명령은 PowerShell에서 실행하고 exact argv, exit code, stdout/stderr SHA-256, wall time, subject commit/tree, uv/Python/pytest identity, environment, checkout root와 post-run Git state를 receipt에 기록한다.

#### Static and Schema Validation

```powershell
uv run python -B -m pytest -s -q -p no:cacheprovider --round3-contract=all `
  Iris/validation/baseline_admission/tests/test_iris_baseline_admission.py `
  Iris/validation/baseline_admission/tests/test_reseal_output_isolation.py `
  Iris/validation/baseline_admission/tests/test_windows_path_contract.py `
  Iris/validation/baseline_admission/tests/test_rtc_durable_bundle_contract.py
```

이 explicit-path command는 신설 tests의 전용 regression route다. 신설 tests는 configured-current discovery에는 포함하지 않는다. Canonical full-repository gate에서는 owner decision에 따라 adopted membership과 갱신된 inventory를 회계하거나, `not_applicable_dedicated_route` disposition과 unchanged required execution denominator를 회계한다.

Schema validation은 최소 다음을 포함한다.

* incomplete subject/environment/path identity rejection
* primary/propagated relation without upstream identity rejection
* JUnit absent without explicit reason rejection
* external durable root nested under checkout rejection
* unknown failure admission rejection
* bare completion vocabulary rejection
* self-referential containing-commit field rejection
* current-authority manifest mutation without matching owner adoption receipt rejection
* synthetic gate proof presented as real application-entry binding rejection
* admission precondition without mapped negative fixture rejection
* negative fixture referencing an unknown or removed precondition rejection
* membership `not_applicable` without dedicated-route PASS/owner disposition rejection
* composite full-gate receipt without exact execution-context applicability rejection

#### Focused RTC and Reseal Validation

```powershell
uv run python -B -m pytest -s -q -p no:cacheprovider --round3-contract=all `
  Iris/build/description/v2/tests/test_dvf_3_3_registry_runtime_compatibility_current.py `
  Iris/build/description/v2/tests/test_dvf_3_3_current_route_required_validation_evidence_freshness_reseal.py `
  Iris/build/description/v2/tests/test_dvf_3_3_current_source_authority_drift_verification_adoption_reseal.py
```

Focused validation은 repository-external result root를 명시하고 live manifest/docs/runtime/package write count `0`을 검사한다.

#### Exact Current

```powershell
uv run python -B Iris/_docs/round3/round3_run_contract_tests.py `
  --class current `
  --enforce-current-build-closure `
  --out <external-result-root>\exact-current.json
```

#### Configured-Current Collection

```powershell
uv run python -B -m pytest -s --collect-only -q -p no:cacheprovider `
  --round3-contract=current `
  --round3-enforce-denominator `
  --round3-denominator-receipt <external-result-root>\configured-current-collection.json
```

#### Configured-Current Execution

```powershell
uv run python -B -m pytest -s -q -p no:cacheprovider `
  --round3-contract=current `
  --round3-enforce-denominator `
  --round3-denominator-receipt <external-result-root>\configured-current.json `
  --junitxml <external-result-root>\configured-current.junit.xml
```

Success predicate:

```text
native_exit_code = 0
collection_error_count = 0
failed_count = 0
error_count = 0
unknown_failure_count = 0
approved_skip_contract_match = true
denominator_receipt_valid = true
source_checkout_mutation_count = 0
```

#### Windows Path Matrix

동일 candidate에서 다음 세 root condition을 실행한다.

```text
normal admitted root       -> PASS
near-boundary admitted root -> PASS
one-character over budget  -> windows_path_contract_rejected before clone/test mutation
```

`LongPathsEnabled=0` registry state와 `git core.longpaths` state를 각각 기록한다.

#### RTC Durable-Bundle Matrix

* selected live bundle positive parity
* missing member
* wrong byte count
* SHA mismatch
* untracked/ignored destination
* duplicate role/destination
* wrong lifecycle state
* path over-budget false-drift prevention
* stale toolchain after durable parity

#### Reseal Output-Isolation Matrix

* both tracked final reports readable under supported root
* missing final report triggers external-only regeneration
* invalid final report fails with durable logs
* live manifest write attempt rejected
* claim-boundary/ledger tracked write attempt rejected
* setup exception still materializes command/path/JUnit-state evidence
* all 5+4 test nodes observed after setup repair

#### Canonical Full-Repository Clean-Checkout Run A/B and Path Control

```powershell
powershell -ExecutionPolicy Bypass -File .\Iris\validation\baseline_admission\invoke_iris_baseline_admission.ps1 `
  -Mode Qualify `
  -RepositoryRoot <clean-source-repository> `
  -Commit <candidate-commit> `
  -DeterminismCheckoutSlot <empty-normal-root-recreated-for-each-run> `
  -RunAWorkRoot <new-empty-short-root-a> `
  -RunAResultRoot <new-empty-result-root-a> `
  -RunBWorkRoot <new-empty-short-root-b> `
  -RunBResultRoot <new-empty-result-root-b> `
  -PathControlCheckoutRoot <new-empty-near-boundary-root-p> `
  -PathControlWorkRoot <new-empty-near-boundary-work-root-p> `
  -PathControlResultRoot <new-empty-result-root-p> `
  -EnvironmentReceipt <owner-bound-environment-receipt> `
  -DurableRoot <owner-managed-durable-root> `
  -PredecessorStageReceiptSet <external-stage-1-to-5-receipt-set> `
  -QualificationContract <external-qualification-contract-copy> `
  -Receipt <external-receipt-path>
```

Baseline wrapper는 A/B 각각에서 focused/configured steps 뒤 다음 existing canonical launcher를 실제 호출한다. `<run-checkout>`은 A 종료/삭제/empty proof 후 같은 normal slot에 새로 만든 B checkout을 의미한다.

```powershell
powershell -ExecutionPolicy Bypass -File <run-checkout>\Iris\validation\clean_checkout\invoke_receipt_bound_full_gate.ps1 `
  -RepositoryRoot <run-checkout> `
  -Commit <candidate-commit> `
  -ClaimId <candidate-claim-id> `
  -EnvironmentReceipt <owner-bound-environment-receipt> `
  -ExecutionContext composite_baseline_admission_chain_stage_6 `
  -PredecessorStageReceiptSetSha256 <stage-1-to-5-receipt-set-sha256> `
  -QualificationContractSha256 <qualification-contract-sha256> `
  -PredecessorStageReceiptSet <external-stage-1-to-5-receipt-set> `
  -QualificationContract <external-qualification-contract-copy> `
  -WorkRoot <run-specific-empty-full-gate-work-root> `
  -ResultRoot <run-specific-empty-full-gate-result-root> `
  -OrchestrationReceipt <run-specific-full-gate-orchestration-receipt>
```

Run A/B가 모두 exit `0`을 반환한 뒤 existing comparator를 실행한다.

```powershell
powershell -ExecutionPolicy Bypass -File <run-b-checkout>\Iris\validation\clean_checkout\invoke_deterministic_compare.ps1 `
  -RepositoryRoot <run-b-checkout> `
  -Commit <candidate-commit> `
  -ClaimId <candidate-claim-id> `
  -EnvironmentReceipt <owner-bound-environment-receipt> `
  -RunAOrchestrationReceipt <run-a-full-gate-orchestration-receipt> `
  -RunBOrchestrationReceipt <run-b-full-gate-orchestration-receipt> `
  -AttemptRoot <new-empty-external-compare-root>
```

Path Control P도 같은 full-repository launcher를 near-boundary checkout에서 실행한다. P는 existing raw-byte deterministic comparator의 A/B pair에 섞지 않고, absolute-path fields만 contract-declared 방식으로 제거한 semantic receipt를 Run A와 비교한다. P의 full-gate exit, denominator hash, dependency inventory hash, subject와 source non-mutation이 모두 일치해야 path qualification이 PASS다.

기존 full-gate의 receipt-bound interpreter invocation semantics는 유지하고 actual argv를 receipt로 검증한다. Focused/configured 및 plan-local Python entry는 `uv run python` contract를 사용한다.

Required evidence:

```text
baseline_admission_run_a_chain = PASS
baseline_admission_run_b_chain = PASS
canonical_full_repository_run_a_exit = 0
canonical_full_repository_run_b_exit = 0
full_repository_denominator_identity_match = true
full_repository_dependency_inventory_identity_match = true
full_repository_canonical_result_identity_match = true
full_repository_execution_context = composite_baseline_admission_chain_stage_6
full_repository_execution_context_identity_match = true
historical_standalone_full_gate_receipt_substituted_count = 0
run_a_source_mutation_count = 0
run_b_source_mutation_count = 0
path_control_full_repository_exit = 0
path_control_source_mutation_count = 0
```

#### Admission Positive/Negative Matrix

```powershell
uv run python -B Iris/validation/baseline_admission/validate_iris_baseline_admission.py `
  admit `
  --repo <candidate-checkout> `
  --qualification <qualification-manifest> `
  --durable-root <retrieved-durable-root> `
  --out <admission-receipt>
```

```powershell
uv run python -B Iris/validation/baseline_admission/validate_iris_baseline_admission.py `
  validate-matrix `
  --preconditions Iris/validation/baseline_admission/contracts/admission_precondition_registry.json `
  --fixtures Iris/validation/baseline_admission/contracts/admission_negative_fixture_registry.json `
  --out <precondition-negative-coverage-receipt>
```

Matrix PASS는 case 숫자 하한이 아니라 `every_admission_precondition_has_negative_case=true`, `uncovered_precondition_count=0`, `orphan_negative_case_count=0`을 요구한다. 각 fixture는 expected rejection code와 synthetic mutator call count `0`을 함께 검증한다.

Known-bad `S_base`가 accepted되거나 gate exception이 exit `0`이면 전체 admission implementation은 FAIL이다.

### Manual Validation

* `S_base` forensic node ledger의 11개 row와 raw log/JUnit/path evidence를 대조한다.
* 5+4 node의 primary/propagated edge와 post-repair actual result를 검토한다.
* remaining 2 failures의 assertion, inputs, owner surface와 disposition을 검토한다.
* RTC 11-member inventory와 promotion provenance/canonical destination relation을 검토한다.
* Windows path census가 tracked paths, temp/generated suffix와 external roots를 모두 포함하는지 검토한다.
* every candidate delta가 root cause와 연결되고 workflow consolidation/runtime/public output delta가 없는지 검토한다.
* Run A/B가 동일 normal slot을 순차 재사용하더라도 checkout/object store/full-gate work/temp/cache/materialized input을 재사용하지 않고, Run A 제거와 empty-slot proof 뒤 Run B가 fresh clone인지 검토한다.
* 각 Run A/B의 existing canonical full-repository orchestration/full-run/canonical-result receipt와 deterministic compare receipt를 exact candidate에 대조한다.
* Path Control P가 near-boundary root에서 같은 full gate를 실행했으며 A/B determinism axis와 섞이지 않았는지 검토한다.
* RTC successor selection과 admission-gate current-required mutation에는 owner adoption receipt를, full-repository test membership에는 `adopted | not_applicable_dedicated_route` owner decision과 대응 denominator/dedicated-route evidence를 검토한다.
* admission precondition registry의 모든 row가 negative fixture registry에 매핑되고 새 precondition 누락이 schema validation에서 실패하는지 검토한다.
* independent reviewer가 exact `S_base'` candidate와 machine bundle을 검토했는지 확인한다.
* owner seal이 machine/review PASS를 결속할 뿐 machine failure를 override하지 않는지 확인한다.
* handoff가 exact predecessor implementation identity를 실제로 가졌는지 또는 blocked state를 정직하게 유지하는지 확인한다.

### Validation Limits

이 실행에서는 다음을 검증하지 않는다.

* Project Zomboid actual in-game behavior
* Browser, Wiki, Tooltip 또는 메뉴 manual QA
* multiplayer 또는 long-session runtime
* public-text semantic quality
* Iris runtime correctness 전체
* Registry Runtime Compatibility 전체 certification
* Registry Authority 또는 DVF Body Compiler PASS
* package, release, Workshop 또는 B42 readiness
* POSIX, cross-machine 또는 broad locale/timezone matrix
* 모든 Windows path length, UNC/network drive/filesystem configuration
* `S_base'` 이후 arbitrary successor HEAD의 automatic admissibility
* workflow consolidation의 성능 개선 또는 terminal acceptance
* 아직 존재하지 않는 workflow consolidation real application entrypoint에서의 admission-gate enforcement

---

## 8. Risk Surface Touch

### Authority Surface

변경 있음.

새로운 `S_base'` qualification record와 Baseline Admission Gate implementation이 future application mutation eligibility의 authority readpoint가 된다. 현재 실증 범위는 gate 자체와 synthetic harness ordering까지이며 real application entry binding은 pending이다. 이는 source, rendered, runtime, package, RTC semantic authority와 별개다.

### Runtime Behavior Surface

None.

Production Lua, Browser, Wiki, Tooltip, menu, item behavior와 game state를 변경하지 않는다.

### Compatibility Surface

변경 있음.

Windows checkout-root/path budget, external output root, uv/Python/pytest environment와 clean-checkout portability contract가 명시된다. 지원 범위 밖 조건은 named fail-closed rejection이 된다.

### Sealed Artifact Surface

변경 있음.

`S_base` forensic evidence, failure ledger, RTC/reseal/path qualification, candidate/Run A/B/canonical full-gate/path-control/admission receipts와 closeout pointer가 additive successor artifact로 생성된다. predecessor bundle/evidence는 변경하지 않는다.

### Public-Facing Output Surface

None.

Iris 사용자에게 보이는 텍스트, UI 또는 package payload는 변경하지 않는다.

---

## 9. Risk Analysis

### Architecture Risk

* Baseline Admission Gate가 기존 clean-checkout authority 또는 RTC semantic authority를 흡수할 수 있다.
* configured-current, exact-current와 기존 full-repository gate의 서로 다른 denominator가 하나로 오인될 수 있다.
* tracked docs/manifest를 self-binding artifact로 만들어 commit identity cycle이 생길 수 있다.
* codebase에 없는 workflow consolidation implementation을 prose에서 존재한다고 가정할 수 있다.
* synthetic mutator proof를 real application-entry enforcement로 과대 표기할 수 있다.
* RTC successor materialization을 current required-validation adoption으로 오인할 수 있다.
* admission precondition이 추가돼도 고정-size negative matrix가 갱신되지 않을 수 있다.
* composite stage-6 full-gate receipt를 historical standalone receipt와 같은 applicability로 소비할 수 있다.

Mitigation:

* 별도 `baseline_admission` root와 claim vocabulary를 사용한다.
* route/denominator별 receipt를 유지하고 대체 금지를 validator로 검사한다.
* exact commit/tree binding은 external receipt 또는 successor pointer에서 수행한다.
* gate implementation/synthetic proof/real entry binding state를 분리한다.
* handoff readiness는 predecessor implementation identity와 mandatory future wrapper contract의 machine-verifiable 존재를 요구한다.
* current-required manifest transaction은 owner adoption receipt를 별도 요구한다.
* precondition/negative-fixture registries의 total coverage를 schema invariant로 검사한다.
* full-gate receipt에 execution context와 predecessor stage-set identity를 결속하고 cross-context substitution을 거부한다.

### Runtime Risk

* configured-current setup이 live manifest, tracked staging docs 또는 package/runtime surface를 쓸 수 있다.
* external root를 전달해도 hard-coded global writer가 repository를 mutate할 수 있다.
* cleanup이 primary failure evidence를 삭제할 수 있다.

Mitigation:

* explicit `current_validation` no-authority-write context를 사용한다.
* protected surface before/after byte/status manifest와 write-attempt negative tests를 둔다.
* durable evidence retrieval/hash 확인 전 cleanup을 금지한다.

### Compatibility Risk

* `LongPathsEnabled=0`, Python path behavior와 Git `core.longpaths`의 차이가 false missing/drift를 만들 수 있다.
* path shortening이 logical artifact identity나 historical evidence path를 손상시킬 수 있다.
* determinism과 path length를 같은 A/B pair에서 동시에 바꾸면 mismatch 원인을 분리할 수 없다.
* uv/Python/pytest environment drift가 candidate 차이로 오인될 수 있다.

Mitigation:

* path budget과 OS/Git/Python observations를 별도 기록한다.
* physical/logical mapping과 historical string preservation contract를 적용한다.
* A/B는 같은 normal checkout slot에서 fresh sequential clone으로 determinism만 비교하고, 별도 Path Control P의 root length를 computed boundary에 결속한다.
* uv/Python/pytest/plugin/package identity를 exact hash/version receipt로 비교한다.

### Regression Risk

* 9 setup errors를 없앤 뒤 새로운 node failures가 나타날 수 있다.
* RTC ordering repair 뒤 actual subject finding이 드러날 수 있다.
* test expectation 또는 denominator를 완화해 false green을 만들 수 있다.
* candidate에 unrelated working-tree changes가 섞일 수 있다.
* stale PASS receipt가 다른 candidate를 admit할 수 있다.
* 신설 admission tests가 configured-current와 canonical full-repository denominator 중 어디에 속하는지 불명확하면 regression coverage가 누락될 수 있다.
* full-repository membership을 선택 사항과 필수 사항으로 동시에 표현하면 불필요한 owner-decision deadlock이 생길 수 있다.

Mitigation:

* post-setup 9-node actual result를 mandatory evidence로 둔다.
* 새 failure는 Change 3 attribution loop로 되돌린다.
* no skip/xfail/ignore/deselect/denominator-reduction invariants를 비교한다.
* candidate는 clean object-based checkout에서 allowed-delta manifest로 구성한다.
* gate는 commit/tree/environment/path/evidence applicability를 모두 재검증한다.
* 신설 tests는 configured-current 제외와 dedicated execution을 명시하고, full-repository membership은 `adopted | not_applicable_dedicated_route` owner decision에 따라 별도 receipt로 검증한다.
* `not_applicable` branch도 dedicated route PASS, unchanged required denominator와 unclassified source `0`을 요구해 안전성과 진행 가능성을 함께 보존한다.

---

## 10. Rollback Plan

Rollback은 historical `S_base`를 rewrite하거나 failed candidate identity를 재사용하는 방식이 아니다.

```text
S_base
historical immutable
  |
  +-> S_repair_candidate_1 -> rejected, evidence retained
  |
  +-> S_repair_candidate_2 -> qualified -> S_base'
```

### Before S_base' Seal

* failed candidate를 admitted baseline으로 승격하지 않는다.
* full raw evidence와 rejection reason을 append-only durable root에 보존한다.
* correction은 new child commit/tree로 만들고 새 qualification을 수행한다.
* application mutation은 계속 차단한다.
* subject finding이면 validation repair를 rollback하고 responsible owner에게 evidence-bound handoff를 전달한다.

### After S_base' Seal

* 새 defect가 발견돼도 기존 `S_base'` commit/tree 또는 receipt를 rewrite하지 않는다.
* successor baseline candidate를 만들고 full qualification/admission을 다시 수행한다.
* stale `S_base'` receipt는 successor HEAD에 적용하지 않는다.

### RTC Rollback

* historical durable bundle, lifecycle event 또는 predecessor manifest를 수정하지 않는다.
* resolver/gate correction은 ordinary successor revert로 되돌린다.
* successor bundle adoption 실패 시 new selection을 adopt하지 않고 predecessor live selection과 failure evidence를 유지한다.
* owner adoption이 아직 없으면 `rtc_successor_bundle_adoption_pending`을 보존하고 manifest mutation과 `S_base'` seal을 모두 중단한다.

### Reseal/Path Rollback

* current-validation context가 semantics를 바꾸거나 authority writer를 손상시키면 해당 successor를 reject한다.
* namespace shortening이 logical identity를 바꾸면 rename/adoption을 취소하고 path contract를 재설계한다.
* preflight는 유지할 수 있지만 그것만으로 repair PASS를 주장하지 않는다.

### Admission Gate Failure

* gate failure 시 application command를 실행하지 않는다.
* receipt를 수정하거나 owner prose로 bypass하지 않는다.
* environment/toolchain drift는 same subject requalification, baseline defect는 successor candidate correction으로 처리한다.

### Handoff Failure

Handoff가 닫히지 않아도 admitted baseline identity를 소급 무효화하지 않는다.

```text
S_base' = admitted_validation_baseline
workflow_consolidation_reapplication_handoff = blocked_missing_predecessor_implementation_identity
```

정확한 implementation input이 확보되면 handoff만 successor transaction으로 재평가한다.

---

## 11. Governance Constraints

* `docs/Philosophy.md`를 준수한다.
* Iris runtime은 100% Lua를 유지하고 JVM/Lua 혼용을 도입하지 않는다.
* Pulse 또는 다른 submod dependency를 새로 만들지 않는다.
* Iris는 정보 surface 역할을 유지하며 이 계획은 user-facing 기능을 변경하지 않는다.
* historical `S_base`, predecessor evidence, failed attempt와 review record는 immutable/additive preservation한다.
* current, historical, diagnostic route와 configured/exact/full-gate denominator를 혼합하지 않는다.
* canonical mandatory full-repository Run A/B를 focused/configured-current evidence로 대체하지 않으며 existing `full_repository_gate.json` contract를 축소하지 않는다.
* application mutation은 admitted baseline 전에는 금지한다.
* validation infrastructure repair와 application implementation을 같은 subject에 혼합하지 않는다.
* source finding은 validation expectation 변경으로 숨기지 않는다.
* test deletion, skip, xfail, deselect, ignore, source reclassification 또는 denominator reduction으로 PASS를 만들지 않는다.
* RTC durable bundle destination은 live canonical input, attempt staging은 promotion provenance로 구분한다.
* RTC materialization repair는 RTC semantic PASS/debt authority를 얻지 않는다.
* output/evidence는 repository-external root를 기본으로 하고 tracked surface에는 최소 contract/pointer만 둔다.
* machine validation, independent review, owner seal을 별도 axis로 유지한다.
* current required-validation selection 변경은 exact owner adoption receipt 없이는 수행하지 않는다. Canonical full-repository test membership은 exact `adopted | not_applicable_dedicated_route` owner decision 없이 변경하거나 생략하지 않는다.
* synthetic harness ordering PASS는 real application-entry binding PASS가 아니다.
* stored PASS는 exact subject/environment/path/evidence applicability가 일치할 때만 소비한다.
* gate exception, missing evidence, unreadable receipt 또는 retrieval failure는 PASS가 아니다.
* failed candidate를 같은 identity로 고쳐 재사용하지 않는다.
* current dirty workspace는 inspection-only이며 stash/reset/clean/overwrite/stage/commit하지 않는다.
* user의 unrelated changes와 untracked files를 candidate 또는 evidence에 포함하지 않는다.
* top-level canonical docs 반영은 additive successor entry를 우선한다.

---

## 12. Expected Closeout State

Expected closeout target:

```text
baseline_restoration = complete
machine_validation = PASS
independent_review = PASS
owner_seal = PASS
s_base_prime = admitted_validation_baseline
canonical_full_repository_run_a = PASS
canonical_full_repository_run_b = PASS
baseline_admission_gate_implementation = fail_closed
baseline_admission_gate_enforcement_proof = synthetic_harness_only
baseline_admission_gate_real_entry_binding = pending_absent_application_entrypoint
workflow_consolidation_reapplication_handoff = ready
workflow_consolidation_terminal = not_run
```

`ready`에는 exact predecessor implementation identity와 mandatory admission wrapper command/same-receipt binding contract가 모두 필요하다. 해당 input이 끝까지 materialize되지 않으면 허용되는 축별 closeout은 다음과 같다.

```text
baseline_restoration = complete
machine_validation = PASS
independent_review = PASS
owner_seal = PASS
s_base_prime = admitted_validation_baseline
canonical_full_repository_run_a = PASS
canonical_full_repository_run_b = PASS
baseline_admission_gate_implementation = fail_closed
baseline_admission_gate_enforcement_proof = synthetic_harness_only
baseline_admission_gate_real_entry_binding = pending_absent_application_entrypoint
workflow_consolidation_reapplication_handoff = blocked_missing_predecessor_implementation_identity
workflow_consolidation_terminal = not_run
```

두 번째 상태는 baseline restoration 실패가 아니지만 전체 계획의 handoff 목표는 `partial`이다.

RTC successor bundle을 materialize해야 하지만 owner adoption이 없는 경우에는 다음 blocked state를 사용하며 live required manifest와 `S_base'`를 seal하지 않는다.

```text
baseline_restoration = blocked_rtc_successor_bundle_adoption_pending
machine_validation = BLOCKED
independent_review = not_eligible_for_PASS
owner_seal = pending_rtc_successor_bundle_adoption
s_base_prime = not_sealed
rtc_successor_bundle_adoption_pending = true
required_manifest_mutation_without_owner_adoption_count = 0
workflow_consolidation_reapplication_handoff = not_started
```

`subject_finding`이 발생하면 validation expectation을 바꾸지 않고 다음 explicit closeout으로 owner-owned correction에 넘긴다.

```text
baseline_restoration = blocked_subject_finding_requires_owner_correction
machine_validation = BLOCKED
independent_review = not_eligible_for_PASS
owner_seal = pending_subject_correction
s_base_prime = not_sealed
subject_finding_count > 0
workflow_consolidation_reapplication_handoff = not_started
```

최종 success criteria:

* `S_base` commit/tree와 historical failure facts가 변경되지 않았다.
* existing non-passing nodes의 raw evidence, exact identity와 disposition이 모두 존재한다.
* 9 propagated nodes와 두 setup root cause가 분리돼 기록됐다.
* remaining 2 failures가 evidence-based classification을 가졌고 unknown count가 `0`이다.
* RTC canonical destination의 11-member inventory/hash/byte/visibility/consumer resolution이 PASS다.
* RTC successor selection이 필요했다면 exact owner adoption receipt가 있고, 필요하지 않았다면 manifest가 byte-identical하게 유지됐다. adoption 없는 manifest mutation count는 `0`이다.
* RTC materialization repair를 RTC global PASS로 확대하지 않았다.
* `LongPathsEnabled=0`의 qualified root range가 정의되고 normal/near-boundary PASS와 out-of-range named rejection이 존재한다.
* 두 reseal workflow가 external-only current-validation mode에서 PASS하고 5+4 node의 actual result가 관측됐다.
* configured-current가 fresh candidate, Run A/B와 Path Control P 모두 exit `0`, failure `0`, error `0`이다.
* Run A/B는 같은 normal slot에서 순차적으로 재생성한 independent fresh checkout이며 object/work/temp/input을 재사용하지 않는다.
* existing canonical mandatory full-repository gate가 Run A/B 각각 exit `0`이고 `test_inventory_sha256`, `required_dependency_inventory.sha256`와 raw canonical result identity가 일치한다.
* 각 full-gate receipt가 `composite_baseline_admission_chain_stage_6` applicability와 동일한 stage 1~5 receipt-set identity를 가지며 historical standalone receipt를 대체 사용하지 않았다.
* Path Control P가 near-boundary fresh checkout에서 같은 full-repository gate를 exit `0`으로 실행하고 Run A와 path-normalized semantic identity가 일치한다.
* 신설 baseline-admission tests의 configured-current 제외와 dedicated route PASS가 receipt에 명시됐고, canonical full-repository membership은 owner의 `adopted | not_applicable_dedicated_route` decision과 일치한다.
* exact qualified commit/tree만 `S_base'`로 봉인됐다.
* known-bad `S_base`는 admission gate에서 거부되고 qualified `S_base'`만 승인된다.
* machine-readable admission precondition registry의 모든 ID가 하나 이상의 rejecting negative fixture와 연결되고 uncovered/orphan count가 모두 `0`이다.
* synthetic harness에서 gate는 mock application mutation 전에 실행되고 rejection/exception에서 mutator call count가 `0`이다.
* gate implementation은 fail-closed지만 real application-entry binding은 실제 entrypoint 부재로 pending이며 active enforcement로 claim하지 않았다.
* old workflow consolidation PASS/timing/measurement/terminal receipt를 상속하지 않았다.
* reapplication handoff가 ready라면 exact predecessor implementation diff, mandatory admission wrapper command/same-receipt rule과 new successor chain이 정의됐다.

### Expected Claim Boundary

이 계획이 성공해도 자동으로 다음을 의미하지 않는다.

```text
Registry Runtime Compatibility PASS
Registry Authority PASS
DVF Body Compiler PASS
Publish Boundary PASS
workflow consolidation implementation PASS
workflow consolidation timing improvement PASS
workflow consolidation terminal PASS
Iris runtime correctness
full compatibility preservation
manual in-game QA
multiplayer stability
long-session stability
package publication
release readiness
Workshop readiness
B42 readiness
deployment readiness
```

허용되는 최대 의미는 다음과 같다.

```text
S_base
= frozen historical predecessor
+ preserved validation defects and evidence

S_base'
= exact qualified successor validation baseline
+ durable qualification evidence
+ admitted_validation_baseline

Baseline Admission Gate implementation
= fail-closed validator and receipt applicability boundary

Baseline Admission Gate enforcement proof
= synthetic mutator harness ordering only

Baseline Admission Gate real application-entry binding
= pending because the application entrypoint is absent

Workflow Consolidation Reapplication Handoff
= S_base'를 new before subject로 사용하고
  prior implementation identity와 mandatory wrapper contract가 확인된 경우에만
  새 S_impl' / tooling review / protocol qualification /
  measurement / S_terminal' chain을 시작할 수 있는 handoff
  (real entry binding PASS 또는 consolidation implementation PASS를 의미하지 않음)
```
