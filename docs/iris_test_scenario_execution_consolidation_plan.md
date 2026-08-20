# Iris Test Scenario Execution Consolidation Implementation Plan

> Status: `implementation_pending_owner_selected_lightweight_entry_gate`
>
> Roadmap basis: `ROADMAP — Iris Test Scenario Execution Consolidation / Cost-Ranked Broader Adoption`
>
> Repository readpoint: 2026-08-17, `HEAD=e20119631df26fb48c590062f7aa2f86e491c342`, `HEAD tree=5974176876c9b9c4d2aaeaab4f36e1ac3f9fca4b`, unrelated dirty working-tree changes present
>
> Execution weight: **standard** — 여러 test family의 실행 ownership을 바꾸지만 Iris product/runtime behavior는 변경하지 않는다.

## 1. Objective

Iris 테스트가 서로 다른 assertion을 검증하기 위해 같은 source scan, input parse, producer, subprocess, temporary workspace, artifact materialization 또는 reload를 반복하는 구간을 실제 비용 순으로 식별하고 통합한다.

통합의 기본 형태는 다음과 같다.

```text
canonical input
-> shared immutable preparation
-> expensive producer/workflow execution
-> immutable structured result
   -> existing assertion identity A
   -> existing assertion identity B
   -> existing assertion identity C
   -> aggregate relationship assertion E
```

mutation, tamper, rollback, recovery, concurrent-owner 또는 standalone process semantics가 계약인 경우에는 공통 immutable prefix까지만 공유하고 writable suffix와 process boundary를 분리한다.

완료 목표는 다음과 같다.

1. configured/historical/diagnostic을 포함하는 `--round3-contract=all` baseline 1회의 source-policy-tagged profiling 결과로 전체 collected test universe의 cost-ranked duplication map을 만든다.
2. 완료된 public-text pilot을 제외하고 measured-cost 또는 아래의 qualified proxy evidence로 우선순위가 정해진 서로 다른 non-pilot `scenario_group_id`를 최소 3개 채택한다.
3. 각 cost-adopted scenario group의 `consolidatable_denominator` 기준 expensive producer/subprocess invocation을 최소 50% 줄이고 total before/after도 함께 공개한다.
4. 기존 test/case identity, assertion meaning, negative contract, fail-closed behavior와 failure attribution을 보존한다.
5. exact-current는 enforcement/readpoint와 full-gate required-selection execution coverage로, configured-current는 pytest collection authority로, canonical clean-checkout full gate는 최종 validation authority로 각각 유지한다.
6. Iris Lua runtime, 정보 authority, Browser/Menu/Tooltip/DVF/Registry product semantics를 변경하지 않는다.
7. 동일 route의 comparable before/after wall-time run을 추가하지 않으므로 이번 round에서는 configured/full-gate wall-time 절감 달성 여부를 주장하지 않는다.

### Repository-grounded current state

입력 roadmap이 predecessor pilot으로 분류한 `public-text-phase7-dispatch`는 현재 코드에도 구현되어 있다. `Iris/build/description/v2/tests/test_public_text_quality_acceptance_current_route.py`의 `setUpClass()`가 `_phase7_self_test()`를 한 번 호출하고, class-owned `ExecutionResult`/`ScenarioReport`를 다음 네 기존 test node가 각자의 probe로 소비한다.

```text
test_phase7_schema_dispatch_accepts_historical_v1_and_current_v2
test_phase7_schema_dispatch_rejects_unknown_and_malformed
test_phase7_schema_dispatch_rejects_successor_transaction_hash_mismatch
test_phase7_freeze_document_replay_is_deterministic
```

`Iris/validation/test_workflow_consolidation/scenario_contracts.py`에는 mapping을 `FrozenMap`, list/tuple을 tuple로 정규화하는 `freeze()`와 `ExecutionResult`, `ProbeResult`, `ScenarioReport`가 존재하며, `pilot_contract_mapping.json`과 `contract_preservation_matrix.jsonl`이 네 predecessor identity를 probe identity에 결속한다. `workflow_consolidation_reapplication_handoff.json`은 predecessor implementation identity를 `supplied`, reapplication을 `complete`로 기록한다.

다만 상태 표면은 완전히 정리되지 않았다.

- `pilot_receipt.json`과 `family_metrics/admission_summary.json`은 paired qualification/timing이 남아 있어 pilot disposition을 아직 `deferred`로 기록한다.
- top-level 문서는 선행 precision-preserving lightweighting의 terminal closeout은 완료 상태로 보존하지만, workflow-consolidation successor는 `docs/DECISIONS.md`에서 `implementation and timing validation pending`, `docs/ROADMAP.md`에서 `planned`로 남아 있다. ROADMAP의 public-text "우선 후보" 문구도 이미 구현된 pilot의 current code/handoff보다 뒤처져 있다.
- current `HEAD`는 predecessor baseline/admission subject보다 전진했고 working tree에도 unrelated 변경이 있다. Current-subject external qualification/durable evidence가 없다는 실제 blocker를 확인한 뒤, 2026-08-17 owner 선택에 따라 이번 broader-adoption entry는 새 Baseline Admission 대신 아래 lightweight exact-subject lock을 사용한다.

이 계획은 다음 원칙으로 불일치를 해소한다.

- 이미 존재하는 public-text 구현을 되돌리거나 다시 구현하지 않는다.
- pilot의 구조적 `4 -> 1` 구현은 predecessor pattern으로 사용하되, 미완료 paired timing/adoption claim은 상속하지 않는다.
- public-text family는 measurement/tooling calibration control로만 사용하고 non-pilot 최소 3-family adoption 수에 포함하지 않는다.
- broader-adoption baseline/final 호출 수와 wall time은 새 exact subject에서 수집한다.
- 선행 precision-preserving lightweighting의 scoped closeout은 재개방하지 않는다.
- 기존 `57482f64…` admission receipt는 historical predecessor evidence로만 남기고 current subject가 admitted됐다는 claim으로 재사용하지 않는다.

---

## 2. Scope

이번 실행은 다음 범위를 포함한다.

- owner-selected lightweight entry integrity gate로 clean exact base subject 고정
- exact-current/configured-current/full-repository denominator readpoint 확인
- representative `--round3-contract=all` full-universe profiling/baseline 1회
- candidate family별 common execution signature와 isolation boundary 작성
- cost-ranked non-pilot adoption 대상 최소 3개 선정
- read-only/deterministic family의 execute-once 구조 도입
- isolation-aware family의 immutable-prefix/isolated-suffix 구조 도입
- old test/case와 new assertion/checkpoint의 identity map 작성
- producer/subprocess/materialization/reload before/after 계수
- adopted non-pilot scenario group의 focused validation과 order-independence 확인
- Codex Reviewer static review 1회
- canonical clean-checkout full gate final long execution 1회
- compact successor evidence와 axis-qualified closeout 작성
- predecessor pilot의 구조적 구현, identity map과 sealed evidence 비변경 확인

### Initial candidate census

현재 코드의 정적 readpoint는 다음 우선 조사 대상을 보여준다. 이 표의 호출 지점 수는 비용 측정값이 아니라 profiling 순서를 정하기 위한 정적 신호다.

| Candidate family | Current code evidence | Initial boundary hypothesis |
| --- | --- | --- |
| public-text Phase 7 dispatch (predecessor control) | `setUpClass()`가 producer를 1회 실행하고 네 probe node가 `ScenarioReport`를 공유; standalone required gate는 별도 subprocess 유지 | 새 adoption 후보가 아님; identity/immutability/measurement calibration 기준으로만 사용 |
| runtime-payload residual seal | test file에 `subprocess.run` 15개, support module이 import 시 staging tree를 writable global `ROOT`로 1회 복사 | read-only baseline은 공유하되 mutating cases는 case-local clone 사용; module-global writable root 제거 |
| artifact lifecycle inventory | 6 tests, subprocess 호출 지점 5개, temporary directory 지점 7개 | 동일 synthetic repository/inventory producer를 쓰는 read-only subset만 공유 |
| artifact lifecycle promotion | 15 tests, subprocess 호출 지점 8개와 `Popen` 1개, temporary directory 지점 16개 | fixture construction/physical evidence prefix만 공유; rollback/crash/concurrent-owner suffix는 독립 유지 |
| artifact lifecycle executor | 2 required tests, 945-line source와 787-line support, Git/materialization 중심 fixture | full-chain 내부의 repeated inspection을 structured phase result로 축소; 두 test 간 mutable repository 공유 금지 |
| registry authority canonical closure | 30 tests/2,030 lines, current required identity 3개, external projected root와 subprocess/bootstrap 경계 존재 | read-only source/hash/inventory prefix만 후보; attempt write, preimport, transaction path는 격리 |
| registry runtime compatibility | current/contract/fixture/package test가 분리되어 있고 standalone required gate 존재 | deterministic manifest/toolchain scan만 공유 가능; standalone validator process는 유지 |

`repeated-generated-artifact-inspection`과 `table-driven-assertion-family`는 현재 repository의 파일명이 아니라 predecessor `family_disposition_ledger.jsonl`의 분석 family다. Phase 1에서 실제 source/test IDs에 매핑되기 전에는 가상의 module이나 framework를 만들지 않는다.

### Explicitly Out Of Scope

- Iris Lua runtime, Browser, Menu, Tooltip, Wiki 또는 DVF product behavior 변경
- Iris source/Evidence/classification/description/Registry/Publish authority 변경
- test count 자체를 목표로 한 node 삭제 또는 giant aggregate test 작성
- configured-current source set, exact-current required-validation 또는 full-repository denominator 축소
- historical/diagnostic source를 optimization 목적으로 current에서 제외하거나 재분류
- negative case, hash/identity check, fail-closed predicate 또는 timeout contract 완화
- fresh-process/bootstrap/crash semantics가 계약인 case의 in-process 전환
- xdist 등 병렬 실행 도입, CI 전체 재설계 또는 pytest 대체
- flaky test 일반 정리, unrelated current failure 수정 또는 historical advisory 정리
- 68-position qualification, 수십 회 timing 반복 또는 통계적 성능 인증
- current subject용 Baseline Admission qualification/durable bundle/owner-seal campaign 생성
- PZ 인게임, multiplayer, long-session, package publication, Workshop 또는 release 검증
- 선행 precision-preserving closeout evidence의 수정, 재봉인 또는 소급 해석
- 현재 병행 중인 Iris runtime/refactor 작업의 파일을 이 최적화에 흡수하는 것

---

## 3. Non-Goals

- `644 -> N` 같은 전체 node 감축 수치를 성공 기준으로 만들지 않는다.
- cheap pure assertion, 이미 단일 execution인 test 또는 measured low-gain family를 억지로 scenario화하지 않는다.
- 서로 다른 producer, canonical input 또는 process contract를 하나의 generic runner로 숨기지 않는다.
- 한 test의 mutable output이나 cleanup 성공 여부에 다음 test가 의존하게 만들지 않는다.
- serialization/file boundary 자체가 계약인 artifact를 in-memory object로 대체하지 않는다.
- outer object만 frozen이고 내부 dict/list가 writable한 결과를 immutable result로 주장하지 않는다.
- 단일 wall-time 표본을 median, p95, variance 또는 통계적 개선률로 표현하지 않는다.
- 목표 수치를 맞추기 위해 unsafe sharing, low-gain merge 또는 추가 heavy timing campaign을 수행하지 않는다.
- application change보다 큰 telemetry, evidence 또는 governance subsystem을 만들지 않는다.
- 공통 실행 계약이 확인되지 않은 family-specific semantics를 `ScenarioRunner`로 일반화하지 않는다.

---

## 4. Assumptions

### Authority and entry assumptions

- `docs/Philosophy.md`가 최상위 설계 권위이며 Iris는 근거 기반 정보 모드, 100% Lua runtime, 타 spoke 비의존 경계를 유지한다.
- `docs/ARCHITECTURE.md`의 **Iris test workflow consolidation boundary** heading이 current architecture다. 2026-08-17 readpoint의 실제 heading은 `## 8-15. Iris test workflow consolidation boundary`이고 바로 앞 `8-14`는 row-cache/lazy-metadata boundary이므로 서로 대체하지 않는다. 의미 권위는 heading title이며 번호 drift는 실행 시작 시 다시 확인한다.
- `docs/DECISIONS.md`와 `docs/ROADMAP.md`는 선행 precision-lightweighting 완료와 workflow-consolidation successor pending을 분리하지만 public-text pilot의 구현 완료 상태까지 반영하지는 않는다. 실제 predecessor 구현 상태는 current code, merge commit `e2011963`과 `workflow_consolidation_reapplication_handoff.json`으로 판정한다. 문서 상태 불일치는 broader-adoption closeout에서 additive하게 정리하되 predecessor evidence를 다시 쓰지 않는다.
- `Iris/validation/baseline_admission/evidence/workflow_consolidation_reapplication_handoff.json`과 `baseline_admission_pointer.json`은 predecessor admission contract의 historical read-only evidence다. Current-subject receipt를 합성하거나 predecessor receipt를 재사용하지 않는다.
- 실제 구현 변경 전 first operation은 intended base commit/tree를 clean isolated checkout에 고정하고 `entry_subject.json`을 생성하는 lightweight entry integrity gate다.
- checkout이 clean하지 않거나 recorded commit/tree가 intended base와 다르면 code/test/config mutation을 시작하지 않고 `blocked_entry_integrity`로 종료한다.
- 현재 사용자 working tree는 다수의 unrelated Iris/runtime/docs 변경을 포함한다. 실행은 해당 변경을 덮어쓰지 않으며 implementation, timing과 validation은 locked base에서 분기한 isolated clean candidate worktree에서 수행한다.

### Test-route assumptions

- `pytest.ini` configured discovery와 `Iris/_docs/round3/round3_run_contract_tests.py` exact Round 3 runner는 별도 권위다.
- 현재 tracked readpoint는 `test_identity_census.jsonl` 644 rows, taxonomy 584 rows, required tests 148이다. source-policy denominator는 classification schema의 여러 source 집합과 clean-checkout 조건을 함께 해석해야 하므로 단일 수치를 계획에서 고정하지 않고 실행 시 collection/list receipt로 확정한다.
- public-text current-route test는 configured-current source이지만 현재 `round3_test_taxonomy.json`/required-test identity에는 포함되지 않는다.
- artifact lifecycle의 일부 identity와 registry authority closure의 3개 identity는 exact current/required-validation에 결속되어 있으므로 변경 시 manifest dependency와 identity를 반드시 대조한다.
- canonical full-repository gate는 `Iris/validation/clean_checkout/contracts/full_repository_gate.json` 및 기존 clean-checkout wrappers가 소유한다. focused/configured-current PASS로 이를 대체하지 않는다.

### Measurement assumptions

- candidate ranking의 primary signal은 **측정된 cumulative removable cost**다.
- primary signal을 얻을 수 없으면 **static duplicate invocation census × observed family wall time** proxy를 fallback ranking에 사용한다. 이는 순위용 proxy이지 measured removable cost나 ceiling이 아니다.
- candidate ledger는 `ranking_basis = measured_removable_cost | static_invocation_wall_time_proxy | unattributable`를 반드시 기록한다.
- proxy-ranked candidate도 deterministic invocation identity/count, 동일 canonical input과 producer signature, 동일 shared-prefix/isolation boundary, 그리고 comparable before/after invocation subject를 입증하면 구조적 cost-adoption 대상이 될 수 있다. 이 경우 50% gate는 wall time이 아니라 observed consolidatable invocation count에만 적용한다.
- proxy-ranked adoption은 `removable_cost_claim=none`, `wall_time_claim=none`, `theoretical_ceiling=unattributable`을 기록한다. proxy 수치나 invocation 감소율을 measured removable cost 또는 route wall-time 절감으로 표현하지 않는다.
- 측정 불가능한 비용은 `unattributable`로 기록하며 0으로 간주하거나 임의 ceiling으로 추정하지 않는다. primary와 fallback 모두 성립하지 않으면 해당 candidate는 `exclude_unattributable`로 종료한다.
- duplicate invocation count와 observed unit cost는 attribution과 tie-break에 사용한다.
- representative full-universe profiling은 current/historical/diagnostic source-policy class를 모두 실행 대상으로 삼고 class별 비용을 분리한다. Final canonical full gate는 다른 selection이므로 이 baseline과 wall time을 직접 비교하지 않는다.
- raw profiling trace는 repository-external disposable root에 두고 compact summary만 successor evidence 후보로 남긴다.

### Resolved roadmap choices

입력 roadmap의 여섯 미결 항목은 이 계획에서 다음과 같이 확정한다.

| Decision | Selected rule | Reason |
| --- | --- | --- |
| Entry gate | owner-selected lightweight exact-subject lock | Current subject에 결속된 qualification/durable evidence가 없으므로 strict admission을 실행 전제에서 제거하되 clean base identity와 predecessor non-reuse는 fail-closed로 유지한다. |
| Candidate ranking | cumulative measured removable cost 우선, invocation count/unit cost 보조 | 단순 호출 수가 싸거나 expensive single call을 놓치는 오류를 함께 줄인다. Adoption eligibility는 아래 C7을 따른다. |
| Order independence | focused batch 내부의 bounded order matrix | 별도 long session 없이 `alone`, forward, reverse, family batch를 한 focused transaction에서 확인한다. |
| Reviewer order | implementation -> Codex Reviewer static review -> focused batch -> final transaction | 정적 blocker를 focused/final 실행 전에 제거한다. |
| Final gate | canonical clean-checkout full gate 1회 | exact/configured를 별도 long execution으로 반복하지 않는다. Full gate receipt의 required selection과 outcome을 보존한다. |
| 20%/15% target | 이번 execution에서는 non-gating observation target | final과 동일 selection의 before run이 없으므로 full-gate 15%는 `not_measured_no_baseline`, configured 20%는 `not_measured_no_comparable_baseline`로 기록한다. |
| Extra governance | lightweight exact-subject lock, P0/P1=0, axis-qualified closeout과 long-run budget ceiling은 mandatory; current-subject Baseline Admission campaign, rigid runner LOC ratio, 별도 external independent review와 별도 collection/shuffle session은 non-mandatory | Owner-selected entry substitution을 명시하고 기존 admission PASS를 주장하지 않으면서 application change보다 큰 사전 campaign을 피한다. |

### Review conflict adjudication

2026-08-17 plan review의 Critical 충돌은 다음처럼 해소한다.

| Review issue | Plan decision |
| --- | --- |
| C1 profiling universe | configured-current 단독 profiling을 폐기하고 `--round3-contract=all` full-universe 실행 1회에서 current/historical/diagnostic/aggregate projection을 구분한다. |
| C2 validation budget | Owner-selected lightweight entry integrity gate는 metadata-only로 수행한다. Long execution은 baseline full profiling 1회와 final full gate 1회뿐이며 admission qualification과 exact/configured 별도 long run은 제거한다. |
| C3 unattributed ranking | measured cost -> static-count × family-time proxy -> `exclude_unattributable`의 fail-closed hierarchy를 사용한다. |
| C4 50% denominator | retained fresh-process/file-contract invocation을 제외한 `consolidatable_denominator`를 gate 분모로 정의하고 total before/after도 함께 공개한다. |
| C5 isolation-only correction | `adopt_isolation_correction_no_cost_claim`을 추가하고 cost-adoption count와 분리한다. |
| C6 full-gate baseline/ceiling | canonical full gate는 final에서만 실행하므로 15% target을 `not_measured_no_baseline`로 두고 이번 success gate에서 제외한다. Full-universe 및 source-class ceiling만 baseline selection에 맞춰 계산한다. |
| C7 proxy-ranked eligibility | qualified proxy candidate의 구조적 cost-adoption은 허용하되 50% gate를 comparable invocation count에만 적용하고 removable-cost/wall-time/ceiling claim은 금지한다. |
| C8 comparable 50% subject | before는 baseline full-universe의 동일 scenario/consumer projection, after는 focused transaction의 정상 full-family batch 1회로 고정한다. alone/forward/reverse replay는 cost after에서 제외한다. |
| C9 final denominator materialization | final subject에서 exact-current list와 configured-current collect-only receipt를 다시 생성하여 pre-change readpoint와 비교한다. metadata-only라 long-run budget을 늘리지 않는다. |

---

## 5. Repository Areas Affected

아래 경로는 실행 시 실제 profiling/adoption 결과에 따라 좁혀진다. `candidate` 표시는 무조건 수정한다는 뜻이 아니다.

### Code

- `Iris/build/description/v2/tests/test_public_text_quality_acceptance_current_route.py` — read-only predecessor control; 재구현/재개방 금지
- `Iris/build/description/v2/tests/test_runtime_payload_state_integrity_residual_seal.py` — isolation-aware candidate
- `Iris/build/description/v2/tests/runtime_payload_residual_seal_test_support.py` — writable global root ownership 교정 후보
- `Iris/build/description/v2/tests/test_artifact_lifecycle_inventory.py` — inventory scenario candidate
- `Iris/build/description/v2/tests/test_artifact_lifecycle_promotion.py` — immutable-prefix candidate
- `Iris/build/description/v2/tests/test_artifact_lifecycle_executor.py` — phase-result/reload candidate
- `Iris/build/description/v2/tests/artifact_lifecycle_executor_support.py` — fixture/materialization ownership 후보
- `Iris/build/description/v2/tests/test_dvf_3_3_registry_authority_canonical_closure.py` — conditional cost-profile candidate
- `Iris/build/description/v2/tests/test_dvf_3_3_registry_runtime_compatibility_current.py` — standalone boundary 보존 대상
- `Iris/build/description/v2/tests/test_dvf_3_3_registry_runtime_compatibility_contract.py` — conditional read-only candidate
- `Iris/build/description/v2/tests/test_dvf_3_3_registry_runtime_compatibility_fixtures.py` — conditional table-driven candidate
- `Iris/build/description/v2/tests/test_dvf_3_3_registry_runtime_compatibility_package.py` — conditional process-isolated candidate
- `Iris/validation/test_workflow_consolidation/collect_execution_census.py` — existing static census 재사용
- `Iris/validation/test_workflow_consolidation/measure_execution_cost.py` — existing measurement contract/read-only calibration input; canonical profiling에는 environment-transparent backend만 허용
- `Iris/validation/test_workflow_consolidation/scenario_contracts.py` — existing immutable result contract; pilot을 포함해 총 3개 concrete consumer family가 같은 contract를 사용할 때만 새 direct dependency로 채택
- `Iris/validation/test_scenario_execution_consolidation/` — 기존 도구가 roadmap의 비주입 관측/ledger 요구를 충족하지 못할 때만 additive successor tooling 추가

새 support module은 family-local 의미를 유지한다. pilot을 포함한 서로 다른 세 concrete consumer family가 동일한 input capture/result contract를 실제로 공유하는 것이 확인되기 전에는 repository-wide `ScenarioRunner`를 새로 만들거나 확장하지 않는다.

### Docs

- `docs/iris_test_scenario_execution_consolidation_plan.md` — 이 실행 계획
- `Iris/_docs/refactor/test_workflow_consolidation/` — predecessor evidence; read-only
- `Iris/_docs/refactor/test_scenario_execution_consolidation/baseline_summary.json` — compact baseline timing/count summary
- `Iris/_docs/refactor/test_scenario_execution_consolidation/candidate_ledger.json` — cost rank, boundary와 terminal disposition
- `Iris/_docs/refactor/test_scenario_execution_consolidation/identity_map.jsonl` — old/new identity와 failure contract map
- `Iris/_docs/refactor/test_scenario_execution_consolidation/final_summary.json` — final invocation/timing/validation comparison
- `Iris/_docs/refactor/test_scenario_execution_consolidation/review.json` — Codex Reviewer verdict/disposition
- `Iris/_docs/refactor/test_scenario_execution_consolidation/closeout.md` — axis-qualified claim boundary
- `docs/DECISIONS.md`, `docs/ROADMAP.md` — final validated state를 반영하는 additive status update 후보; 병행 사용자 변경과 충돌하면 별도 owner handoff

새 namespace는 predecessor sealed surface와 섞이지 않도록 한다. 위 compact evidence 파일명은 implementation 시작 시 기존 naming/authority convention과 충돌하지 않는지 확인한 뒤 확정한다. raw stdout/stderr, per-event trace와 temporary workspace는 이 디렉터리에 저장하지 않는다.

### Config

기본 예상은 **변경 없음**이다.

- `pytest.ini` — 변경하지 않음
- `Iris/_docs/round3/round3_test_taxonomy.json` — test identity 이동이 불가피하고 owner-approved atomic mapping이 있을 때만 변경
- `Iris/_docs/round3/current_route_required_validations.json` — required identity가 바뀔 때만 owner-approved successor transaction으로 변경
- `Iris/_docs/round3/round3_pytest_source_classification.json` — 새 configured source가 실제 추가될 때만 denominator contract에 따라 변경
- `Iris/validation/clean_checkout/contracts/full_repository_gate.json` — 새 source membership이 실제 필요하고 owner disposition이 있을 때만 additive 변경
- `Iris/_docs/round3/round3_active_core_closure.json` — 변경하지 않음; test support를 product/current tooling authority로 승격하지 않음

기존 test node를 유지하고 내부 execution ownership만 바꾸는 방식을 우선하여 config/authority mutation을 피한다.

### Generated Artifacts

Repository-external run root에 다음을 생성한다.

- baseline/final command receipts
- collection and denominator receipts
- raw stdout/stderr and optional JUnit
- per-family invocation telemetry
- focused order-matrix results
- clean-checkout full-gate orchestration receipts
- pre/post Git status and tracked-source mutation report
- lightweight `entry_subject.json` with owner-selected substitution and exact base binding

Repository 안에는 compact, stable, claim에 필요한 successor summary만 저장한다. 기존 staging, sealed predecessor, runtime/package artifact를 profiling output root로 사용하지 않는다.

---

## 6. Planned Changes

### Change 0 — Owner-selected lightweight entry integrity and execution subject lock

Purpose:

Current-subject external qualification이 없는 상태에서 Baseline Admission을 합성하거나 predecessor receipt를 재사용하지 않는다. 대신 owner가 선택한 축소 gate로 구현 전 clean exact base subject와 predecessor non-reuse를 고정한다.

Files:

- `Iris/validation/baseline_admission/evidence/workflow_consolidation_reapplication_handoff.json` — historical predecessor input
- `Iris/validation/baseline_admission/evidence/baseline_admission_pointer.json` — historical strict contract and non-reuse reference
- repository-external `entry_subject.json`

Implementation Notes:

1. owner decision을 `entry_policy=owner_selected_lightweight_exact_subject_lock`, `baseline_admission_axis=not_run_no_current_subject_qualification`로 기록한다. 이를 `admitted`, waiver-equivalent machine PASS 또는 predecessor PASS 상속으로 표현하지 않는다.
2. implementation base commit/tree를 isolated checkout으로 materialize하고 plan header의 intended base identity와 일치하는지 확인한다.
3. checkout의 tracked, staged와 untracked status가 모두 clean인지 확인한다. 원래 사용자 worktree의 dirty state는 정보로만 기록하고 mutation/cleanup하지 않는다.
4. `entry_subject.json`에 schema, timestamp, owner-selected policy, base commit/tree, clean-status checks, original-worktree non-mutation statement와 predecessor admission `historical_only_not_reused` disposition을 기록한다.
5. entry lock 전에 application code/test/config mutation을 수행하지 않는다. 계획 문서 수정은 policy 선택 기록이며 implementation mutation으로 계상하지 않는다.
6. predecessor handoff의 `supplied` implementation과 `complete` reapplication은 그대로 보존하되, `57482f64…` receipt를 현재 base 또는 후속 implementation subject의 admission으로 재사용하지 않는다.
7. public-text pilot은 calibration control로 측정할 수 있지만 broader-adoption before/after 합계나 최소 3-family 수에 포함하지 않는다.
8. 이 단계에는 qualification, durable-bundle 생성, timing, candidate profiling, repeated full suite, independent review 또는 owner seal 생성을 붙이지 않는다.

Validation:

- intended base commit/tree match
- tracked/staged/untracked dirty count `0` in isolated candidate checkout
- `entry_subject.json` policy/subject/clean-status fields complete
- predecessor admission reuse count `0`; current-subject `admitted` claim count `0`
- entry integrity 실패 시 이후 Changes 1~7 미실행 및 `blocked_entry_integrity`

---

### Change 1 — Full-universe denominator and representative cost profile

Purpose:

candidate 선택 전에 현재 test identity와 configured/historical/diagnostic을 포함한 collected test universe의 실제 실행 비용을 `--round3-contract=all` 한 번으로 관측한다. Canonical clean-checkout full gate는 source disposition상 historical/diagnostic reenactment를 요구하지 않으므로 이 profiling run을 대체하지 않는다.

Files:

- `pytest.ini` — read-only
- `Iris/build/description/v2/tests/conftest.py` — read-only
- `Iris/_docs/round3/round3_run_contract_tests.py` — read-only
- `Iris/validation/test_workflow_consolidation/collect_execution_census.py` — existing static census
- `Iris/validation/test_workflow_consolidation/measure_execution_cost.py`와 `measurement_contract.json` — predecessor measurement capability/read-only constraint input
- conditional additive `Iris/validation/test_scenario_execution_consolidation/profile_execution.py`
- compact `baseline_summary.json`

Implementation Notes:

1. existing `collect_execution_census.py`를 repository-external output root에 실행하고 tracked 644-row census와 current source/test identities의 drift를 확인한다.
2. exact-current `--list`와 configured-current `--collect-only`는 selection/denominator readpoint만 materialize하며 long validation으로 취급하지 않는다. exact runner의 `--list` branch는 `--out`보다 먼저 종료하므로 stdout, stderr, command와 exit code를 repository-external orchestration receipt에 함께 보존한다.
3. configured denominator를 보존한 `--round3-contract=all` full-universe execution을 baseline/profiling 목적으로 한 번만 수행한다.
4. node/source classification을 current, historical, diagnostic, aggregate로 구분하여 최소 telemetry를 scenario group별로 집계한다. 각 candidate의 before count는 이 단일 full-universe 실행 안의 동일 `scenario_group_id`/consumer projection에서만 가져온다.

```text
selected test/node IDs and route projection
route, scenario-group and family wall time
scenario_group_id / shared_producer_group_id
producer signature / canonical input identity
consumer test IDs
producer identity and invocation count
subprocess spawn count and cumulative duration
temporary workspace/materialization count
copy operation count and attributable bytes
parse/load and artifact reload count where attributable
unattributable duration/count and actual ranking basis
```

5. 기존 `measure_execution_cost.py`의 `environment_transparent_timing_only` backend가 실제로 존재하고 target argv/env를 보존하는지 먼저 확인한다. `python_sitecustomize_process_tree` backend는 `PYTHONPATH`를 주입하므로 canonical representative run에는 사용하지 않는다.
6. subprocess/copy/materialization 동적 관측이 필요하면 target checkout/argv/env를 변경하지 않는 repository-external Windows process-tree observer를 먼저 사용한다. 해당 observer의 parity를 입증하지 못하면 그 축을 `unattributable`로 남기고 0으로 해석하지 않는다.
7. `--durations` 또는 개별 test duration만으로 duplicate cost를 확정하지 않는다. static execution census, producer signature, canonical input과 removable fraction을 함께 계산한다.
8. 측정된 removable cost가 있으면 baseline과 동일한 selection/class 분모로 theoretical ceiling을 별도로 기록한다.

`baseline_summary.json`에는 candidate마다 다음 축별 관측 가능성 row를 먼저 기록한다.

```text
scenario_group_id
measurement_axis = producer | subprocess | workspace_materialization | copy_bytes | parse_reload
process_tree_observer_required = true | false
deterministic_before_count_without_observer = true | false
before_count_evidence = static_straight_line | deterministic_bound | runner_visible_telemetry | observer | none
before_count_status = exact | unattributable
reason
```

정적 call-site 수만으로 runtime count를 단정하지 않는다. Unconditional straight-line call이거나 canonical input에서 loop bound와 conditional branch가 결정되고 그 결정을 census/runner-visible baseline evidence로 대조할 수 있을 때만 `deterministic_before_count_without_observer=true`로 둔다. Loop bound, conditional reachability 또는 process/materialization fan-out을 observer 없이 확정할 수 없으면 해당 축은 `unattributable`이다. 이 matrix는 새 실행 단계가 아니라 Change 1 compact summary의 일부다.

```text
theoretical_ceiling_round3_all
= full-universe attributable removable duplicate cost
  / full-universe --round3-contract=all wall time

theoretical_ceiling_<source_class>
= source-class attributable removable duplicate cost
  / source-class observed wall time
```

Canonical full gate의 comparable before receipt는 이번 baseline에서 생성되지 않으므로 full-gate 15% axis는 `not_measured_no_baseline`이며 success gate에서 제외한다. Configured-current도 동일 selection의 final execution이 없으므로 20% axis는 `not_measured_no_comparable_baseline`이다. Primary attribution이 불가능하고 proxy ranking만 사용한 class ceiling은 `unattributable`이며 proxy 값으로 대체하지 않는다.

Validation:

- baseline full-universe command exit `0`, 또는 source-policy/known historical advisory에 이미 결속된 기존 non-passing identity만 재현
- canonical collection/selection identity 변화 없음
- external observer 사용 시 observer off/on의 command, environment, selection, outcome parity
- candidate별 measurement axis row 존재 및 observer 없는 deterministic before-count 판정 누락 `0`
- unresolved loop/conditional/fan-out을 static call-site count로 `exact` 처리한 row `0`
- profiling 전후 tracked source mutation `0`
- raw telemetry가 repository 밖에 존재

---

### Change 2 — Family boundary adjudication and identity freeze

Purpose:

실제 비용과 코드 구조를 바탕으로 각 candidate를 terminal disposition으로 종료하고, 구현 전에 old/new identity와 isolation contract를 고정한다.

Files:

- `candidate_ledger.json`
- `identity_map.jsonl`
- candidate test/support sources — read-only analysis

Implementation Notes:

Change 2 adjudication은 `baseline_summary.json`의 축별 `deterministic_before_count_without_observer` matrix를 첫 입력으로 읽은 뒤 시작한다. 각 family는 다음 중 하나로 종료한다.

```text
adopt_full
adopt_immutable_prefix_only
adopt_isolation_correction_no_cost_claim
retain_full_process_isolation
exclude_low_measured_gain
exclude_no_safe_shared_boundary
exclude_unattributable
unmapped_analysis_family
```

`deferred`나 `must_isolate`만으로 분석을 종료하지 않는다.

각 candidate row에는 다음을 기록한다.

```text
family_id
scenario_group_id
shared_producer_group_id
source files
old test/case IDs
consumer test IDs
canonical input identity
producer signature / command identity
ranking basis
measured removable cost or proxy value
adoption evidence basis (`measured_cost` or `qualified_proxy_structure`)
removable cost / wall-time / theoretical-ceiling claim state
total_invocations_before / total_invocations_after
retained fresh-process invocation count
retained external/file-contract invocation count
consolidatable_invocations_before / consolidatable_invocations_after
consolidatable_reduction_pct
shared immutable prefix
mutable branch point
fresh-process-required tail
external-file-contract point
expected and observed before/after counts
before execution subject / after execution subject
excluded replay runs from cost after
isolation correction state
disposition and evidence-qualified reason
```

`scenario_group_id`는 file/family 이름이 아니라 동일 canonical input, producer signature와 isolation boundary를 가진 optimization unit이다. 여러 파일에 걸쳐도 동일 group이면 adoption 최소 수에서 한 번만 센다. `shared_producer_group_id`는 producer를 공유하지만 input/isolation boundary가 달라 별도 scenario로 남는 관계를 표시한다.

`repeated-generated-artifact-inspection`과 `table-driven-assertion-family` 같은 분석 family는 실제 source/test IDs에 매핑하거나 `unmapped_analysis_family`로 종료한다.

Candidate ledger는 scenario당 한 row의 구현 선택표로 유지한다. Raw trace, 중복 proof payload, 전체 assertion 결과를 복제하지 않으며 위 판정 필드와 adopt/skip reason만 보존한다. 새 hash chain, nested proof packet, attempt lifecycle 또는 별도 evidence-sealing subsystem을 candidate ledger에 추가하지 않는다.

각 identity map row에는 다음을 기록한다.

```text
old pytest node or unittest test_id
new node/assertion/subTest/checkpoint ID
assertion purpose
negative/fail-closed contract
expected failure identity/message class
execution owner
required-validation/taxonomy/source-policy binding
```

Cost-adoption 조건은 모두 충족해야 한다.

1. measured attributable duplicate cost가 있거나 아래 qualified proxy eligibility를 충족한다.
2. shared prefix가 명확하다.
3. assertion/failure identity를 보존할 수 있다.
4. isolation/process contract를 문장으로 설명할 수 있다.
5. expected 및 observed consolidatable expensive invocation reduction이 50% 이상이다.
6. maintenance/abstraction cost가 gain에 비례한다.

Qualified proxy eligibility는 다음을 모두 요구한다.

1. Change 1의 축별 matrix에서 adoption 계산에 쓰는 producer/subprocess/materialization invocation identity와 before count가 `exact`이고, process-tree observer 없이도 결정적이라고 입증된다.
2. before/after가 동일 `scenario_group_id`, `consumer_test_ids`, canonical input identity, producer signature와 retained contract set을 사용한다.
3. static duplicate count에 결합하는 family wall time이 baseline full-universe에서 관측됐고 ranking 용도로만 사용된다.
4. 구현 후 focused 정상 full-family batch 1회에서 after count를 관측할 수 있다.
5. observed consolidatable invocation reduction이 50% 이상이다.
6. ledger가 `removable_cost_claim=none`, `wall_time_claim=none`, `theoretical_ceiling=unattributable`을 명시한다.

따라서 qualified proxy row는 distinct non-pilot cost-adopted `scenario_group_id` 최소 수에 포함할 수 있지만 measured-cost 또는 performance claim에는 포함하지 않는다.

Measured attribution 실패 후 adoption-relevant 축 중 하나라도 observer 없이 exact before count를 입증하지 못하면 그 candidate는 qualified proxy eligibility를 충족하지 못해 `exclude_unattributable`로 종료한다. 모든 safe non-pilot candidate가 이 경로로 종료되면 구현을 강행하지 않고 `blocked_insufficient_safe_ranked_candidates`로 closeout한다.

50% gate의 분모는 중복 없는 invocation identity 기준으로 다음처럼 정의한다.

```text
consolidatable_denominator_before
= total_expensive_invocations_before
  - retained_fresh_process_invocations_before
  - retained_external_or_file_contract_invocations_before

consolidatable_reduction_pct
= (consolidatable_denominator_before - consolidatable_invocations_after)
  / consolidatable_denominator_before
```

retained category가 겹치면 한 번만 제외한다. 동일 invocation identity가 before/after 양쪽에서 같은 retained category일 때만 비교 분모에서 제외한다. category가 바뀐 identity는 별도 `retained_category_transition` row로 기록하며 조용히 분모에서 제거하지 않는다. 각 adopted scenario는 gate 값과 별도로 `total_invocations_before`, `total_invocations_after`, `total_reduction_pct`를 공개한다.

`consolidatable_denominator_before = 0`이면 cost adoption과 50% gate 대상이 아니며 `retain_full_process_isolation`, `exclude_no_safe_shared_boundary` 또는 isolation-only correction 중 실제 의미에 맞는 disposition으로 종료한다.

`adopt_isolation_correction_no_cost_claim`은 50% 조건을 적용하지 않는다. 이 disposition은 확인된 shared writable state를 제거하고 module-global writable state/writable-path intersection을 0으로 만들기 위한 것이며, cost-adopted scenario count와 performance claim에는 포함하지 않는다.

Validation:

- distinct adopted non-pilot `scenario_group_id` 최소 3개 또는 `partial_adoption_below_target`/`blocked_insufficient_safe_ranked_candidates`
- Change 1 축별 observability matrix가 각 adoption decision의 첫 evidence input으로 연결됨
- old identity unmapped count `0`
- required identity dangling/stale count `0`
- candidate마다 terminal disposition과 non-empty reason 존재
- 분석 family의 unmapped/terminal disposition 누락 `0`

---

### Change 3 — Predecessor pilot freeze and reusable-contract gate

Purpose:

이미 구현된 public-text Phase 7 pilot을 재개방하지 않고, broader adoption이 재사용할 수 있는 계약과 재사용하면 안 되는 predecessor-specific surface를 구분한다.

Files:

- `Iris/build/description/v2/tests/test_public_text_quality_acceptance_current_route.py` — read-only
- `Iris/validation/test_workflow_consolidation/scenario_contracts.py` — read-only contract inspection
- `Iris/_docs/refactor/test_workflow_consolidation/{pilot_contract_mapping.json,contract_preservation_matrix.jsonl,pilot_receipt.json}` — read-only predecessor evidence

Implementation Notes:

1. current `setUpClass() -> _phase7_self_test() -> ExecutionResult/ScenarioReport -> four probes` 구조를 baseline control로 고정한다. producer invocation count 1은 Change 1의 동일 full-universe baseline telemetry에서 확인하며 이를 위해 pilot 전용 실행을 추가하지 않는다.
2. 현재 `freeze()`가 nested mapping과 list/tuple을 각각 `FrozenMap`과 tuple로 변환하는 범위, 그리고 private backing state가 consumer에 의해 변형되지 않는다는 계약을 확인한다. 새 family가 같은 shape를 쓰지 않거나 strict immutability를 입증할 수 없다면 이 generic contract를 억지로 확장하지 않고 family-local frozen structure를 사용한다.
3. predecessor public-text test, mapping, receipt, handoff 또는 protected surface를 broader adoption의 구현 파일로 수정하지 않는다.
4. terminal, host-independent, replay, text-identity, long-path, inventory-completeness와 standalone required-gate validator는 서로 다른 command/contract이므로 새 consolidation 대상과 합치지 않는다.
5. `pilot_receipt.json`의 pending timing/adoption 상태를 broader-adoption 결과로 소급 변경하지 않는다. 필요하면 새 successor summary가 pilot을 `predecessor_control`로 참조한다.
6. 기존 scenario contract를 새 non-pilot family가 직접 import하면 dependency inventory 변화와 `pilot + 최소 2 non-pilot direct consumer` threshold를 함께 검증한다.

Validation:

- predecessor 네 probe node와 standalone required-gate identity 변화 `0`
- predecessor evidence/protected surface diff `0`
- new non-pilot adoption count에 pilot이 포함되지 않음
- reusable contract를 채택한 경우에만 dependency inventory 및 immutability contract 확인
- 별도 pilot execution은 수행하지 않고 baseline/final full gate에 이미 포함된 결과만 참조

---

### Change 4 — Read-only and deterministic family adoption

Purpose:

profiling에서 높은 순위를 받은 read-only scan, deterministic generation 또는 repeated artifact inspection family를 우선 통합한다.

Files:

- profiling에서 선택된 candidate test/support files
- 우선 검토: artifact lifecycle inventory, registry compatibility fixtures/contract, registry generator/validator read-only prefix

Implementation Notes:

1. 같은 canonical input + producer signature + command + normal workspace preparation + isolation boundary를 공유하는 assertion만 같은 `scenario_group_id`로 묶는다. 파일/family 경계가 달라도 이 identity가 같으면 한 group이며 adoption count에서 중복 계산하지 않는다.
2. 외부 file byte shape가 계약이 아니면 producer result를 structured in-memory result로 전달하고 aggregate consumer의 재-read/re-parse를 제거한다.
3. file existence, serialization, path, byte identity가 assertion subject이면 artifact 생성과 file inspection을 유지한다.
4. Scenario result는 frozen outer object만으로 충분하지 않다. nested mappings/sequences도 immutable하게 만들거나 consumer마다 defensive copy한다.
5. producer failure와 assertion failure를 별도 field로 보존한다.
6. 기존 test node를 유지하는 class fixture/family-local runner를 우선한다.
7. pilot을 포함한 최소 세 concrete consumer family가 정말 같은 execution contract를 공유하지 않으면 generic `ScenarioRunner`를 새로 도입하거나 확장하지 않는다.

Validation:

- cost-adopted scenario별 consolidatable producer/subprocess reduction 50% 이상과 total before/after 동시 기록
- hash가 기존 contract인 경우에만 existing hash assertion을 사용한다. 일반 structured result를 위해 새 deterministic hash infrastructure를 만들지 않는다.
- 동일 input의 structured result와 기존 assertion outcome 일치
- old/new identity map complete
- aggregate assertion이 individual failure를 가리지 않음
- repository-wide net test/tooling LOC와 새 infrastructure LOC 기록

---

### Change 5 — Isolation-aware runtime-payload and lifecycle adoption

Purpose:

mutation/recovery/authority semantics가 있는 cost-profile candidate family에서 immutable prefix만 공유하고 writable suffix를 case-local로 분리한다.

Files:

- `test_runtime_payload_state_integrity_residual_seal.py`
- `runtime_payload_residual_seal_test_support.py`
- selected artifact lifecycle test/support files
- selected registry authority test/support file

Implementation Notes:

#### Runtime-payload residual seal

- `ROOT` 제거 전에 repository 전체 reference를 census해 support module 외 consumer와 import-time side effect 의존을 기록한다.
- import 시 staging tree를 복사하고 module-global writable `ROOT`를 노출하는 현재 구조를 제거한다.
- source staging tree는 read-only seed input으로 취급한다.
- read-only report assertions는 하나의 class-owned immutable snapshot/result를 사용한다.
- author/review deletion, metadata tamper, drift injection과 restore path는 독립 external workspace clone에서 실행한다.
- case-local clone은 필요한 mutable subtree/file만 복사하며, 전체 tree copy보다 싸다는 것이 실측될 때만 채택한다.
- restore helper는 다른 case의 baseline을 복구하는 전역 cleanup이 아니라 해당 case workspace의 lifecycle owner가 된다.
- subprocess/standalone validator semantics는 유지한다.
- clone 증가로 cost gate를 충족하지 못해도 isolation defect가 확인되면 `adopt_isolation_correction_no_cost_claim`으로 수정하고 cost-adoption count에는 포함하지 않는다.

#### Artifact lifecycle

- synthetic Git repository 초기화, giant fixture 생성과 physical inventory production이 같은 input에서 반복되는 subset을 식별한다.
- immutable baseline repository는 template/seed로만 사용하고 각 mutation/transaction test는 별도 writable clone을 소유한다.
- promotion rollback, interrupted transaction, concurrent active owner, crash-after-publication과 external collision case는 서로 workspace/process를 공유하지 않는다.
- `Popen`을 사용하는 concurrent-owner case와 crash/recovery case는 full process isolation disposition을 유지한다.
- full-chain executor 내부에서 동일 phase artifact를 여러 번 읽는 경우 structured phase result 또는 한 번의 parse로 줄이되, on-disk receipt/hash contract 검사는 유지한다.

#### Registry authority/runtime compatibility

- projected repository root, attempt root 또는 module import/bootstrap state가 mutable인 test는 독립 유지한다.
- source/hash/toolchain inventory처럼 read-only deterministic prefix만 공유한다.
- current required standalone validator, preimport build-closure guard와 missing-input fail-closed process는 fresh subprocess를 유지한다.
- required identity 3개 및 RTC standalone required test의 taxonomy/manifest binding을 변경하지 않는다.

Validation:

- immutable seed pre/post hash 동일
- mutation branch 간 writable-path intersection `0`
- adopted/corrected scenario support scope의 module-global writable scenario state `0`
- predecessor `ROOT` consumer census의 unmapped consumer `0`
- case cleanup 전후 source checkout mutation `0`
- crash/concurrency/fresh-process identity 보존
- normal/tamper/rollback/recovery 결과가 단독 실행과 family batch에서 동일

---

### Change 6 — Identity, order, dependency and denominator verification

Purpose:

통합 구현이 test meaning, execution order, dependency identity 또는 validation denominator를 바꾸지 않았는지 검증한다.

Files:

- `identity_map.jsonl`
- candidate tests/support modules
- conditional Round 3/clean-checkout config files
- conditional `validate_consolidation.py`

Implementation Notes:

1. static scan으로 adopted/corrected scenario support scope의 module/class/global writable result, hidden memoization, previous-test output reuse와 shared mutable workspace를 찾는다. unrelated Iris module 전체에 대한 global absence claim은 하지 않는다.
2. focused transaction 안에서 각 adopted non-pilot scenario group의 대표 identity를 다음 matrix로 실행한다. 각 group에서 read-only consumer representative를 최소 1개 선택하고, isolation-sensitive consumer가 존재하면 이를 최소 1개 추가한다. `A`/`B`는 이 규칙으로 선택한 대표이며 선택 근거를 receipt에 기록한다.

```text
A alone
B alone
A -> B
B -> A
normal full adopted-family batch (cost-after subject)
```

3. order matrix는 명시적 node ID 순서를 사용한다. 새 pytest random-order plugin dependency를 추가하지 않는다. `alone`, forward, reverse replay는 order/isolation evidence일 뿐 cost after count에는 포함하지 않는다.
4. 50% 비교의 before는 Change 1 baseline full-universe 한 번에서 얻은 동일 scenario/consumer projection이고, after는 이 focused transaction의 normal full adopted-family batch sub-run 한 번이다. 양쪽은 동일 `scenario_group_id`, `consumer_test_ids`, canonical input identity, producer signature와 retained contract set을 사용한다.
5. result equality는 단순 PASS뿐 아니라 failure identity, negative contract, producer count와 source mutation을 비교한다.
6. 새 support module이 exact required test의 direct dependency가 되면 clean-checkout dependency inventory가 자동으로 포착하는지 확인한다. 포착되지 않으면 기존 authority contract에 따른 additive explicit dependency만 갱신한다.
7. node ID를 유지할 수 있으면 taxonomy/required/source config를 변경하지 않는다.
8. identity 이동이 불가피하면 code와 manifest update를 하나의 atomic transaction으로 수행하고 predecessor/new mapping을 남긴다.
9. post-change exact/configured/full denominator 비교는 Change 1에서 생성한 pre-change collection/census receipts를 유일한 baseline으로 사용한다. 다른 시점의 predecessor 수치를 섞지 않는다.

Validation:

- unmapped old identity `0`
- duplicate new identity `0`
- order-matrix semantic mismatch `0`
- shared writable state finding `0`
- required-validation dangling/stale binding `0`
- configured/exact/full denominator unauthorized reduction `0`

---

### Change 7 — Review, focused validation, final long gate and closeout

Purpose:

최종 implementation subject를 한 번 정적으로 검토하고, focused transaction에서 comparable invocation 감소를 확인한 뒤 canonical final long gate 한 번으로 correctness를 확인한다. Measured attribution이 있는 row만 실제 removable-cost claim을 낸다.

Files:

- `review.json`
- `final_summary.json`
- `closeout.md`
- repository-external final receipts

Implementation Notes:

1. 구현 완료 후 Codex Reviewer static review를 1회 수행한다.
2. review 범위는 assertion meaning, identity map, negative/fail-closed contract, mutable leak, order dependency, process boundary, aggregate masking, low-gain abstraction과 dependency binding이다.
3. P0/P1 또는 semantic/isolation blocker가 있으면 해당 family만 수정하고 필요한 focused 범위만 재검증한다.
4. review blocker가 없으면 focused transaction 1회를 실행한다. Change 6의 order matrix와 cost after용 normal full-family batch sub-run을 이 transaction에 포함하되, cost after 값은 normal batch 한 번에서만 산출한다.
5. focused failure 이후 assertion message, ledger reference 또는 path literal처럼 execution ownership/contract를 바꾸지 않는 사전 정의된 correction만 수행했다면 focused delta를 확인한다. Producer ownership, isolation, identity, process/file boundary 또는 denominator를 바꾸는 수정이면 affected diff에 한정한 delta-only static re-review를 수행한다.
6. focused validation 이후 동일 final subject에서 exact-current list와 configured-current collect-only receipt를 materialize하고 pre-change receipt와 비교한다. 이는 metadata readpoint이며 별도 long execution이 아니다.
7. final long execution은 exact same commit/tree에 대해 canonical clean-checkout full-repository gate 한 번만 수행한다.

```text
canonical clean-checkout full-repository gate
-> full-run and pytest result receipts
-> baseline/final comparison and closeout
```

8. full gate의 command, environment, subject, required selection, exit code와 wall time을 기록한다. Baseline `--round3-contract=all`과 selection이 다르므로 두 wall time을 before/after performance delta로 비교하지 않는다.
9. actual consolidation correctness failure가 있을 때만 관련 validation을 재실행한다. telemetry formatting, optional report formatting, non-semantic cache cleanup 또는 unrelated historical advisory는 자동 full rerun 사유가 아니다.
10. `final_summary.json`과 `closeout.md`는 `measured-cost consolidation`과 `proxy-ranked structural consolidation`을 별도 category로 집계한다. Proxy row를 `high-cost family`, measured saving 또는 performance improvement로 축약하지 않는다.
11. final claim은 실제 adopted non-pilot scenario group과 관측된 reduction 범위까지만 작성한다.

Validation:

- Codex Reviewer P0/P1 `0`, unresolved implementation blocker `0`
- focused family batch exit `0`
- final exact-current list/configured-current collect-only receipt exit `0` 및 unauthorized denominator drift `0`
- canonical clean-checkout full gate exit `0`
- full-gate required selection failure `0`
- tracked source mutation `0`
- cost-adopted non-pilot scenario group 각각 consolidatable invocation reduction 50% 이상
- isolation-only correction의 module-global writable state count `0`, `cost_claim=none`
- performance target은 아래 Section 7의 조건부 판정 적용

---

## 7. Validation Plan

### Automated Validation

모든 Python command는 PowerShell에서 `uv run python`을 사용하고 Change 0에서 고정한 clean exact checkout을 working directory로 삼는다. 실제 result/work/receipt root는 repository 밖의 새 absolute path를 사용한다.

#### 1. Lightweight entry integrity precondition

Owner-selected substitution을 repository-external metadata receipt로 기록한다. 이 command는 Baseline Admission validator를 호출하지 않는다.

```powershell
$entryCheckout = [System.IO.Path]::GetFullPath('<exact-candidate-checkout>')
$entryReceipt = [System.IO.Path]::GetFullPath('<external-result-root>\entry_subject.json')
$entryCommit = (& git -C $entryCheckout rev-parse HEAD).Trim()
if ($LASTEXITCODE -ne 0) { throw 'entry commit read failed' }
$entryTree = (& git -C $entryCheckout rev-parse 'HEAD^{tree}').Trim()
if ($LASTEXITCODE -ne 0) { throw 'entry tree read failed' }
$entryStatus = @(& git -C $entryCheckout status --porcelain=v1 --untracked-files=all)
if ($LASTEXITCODE -ne 0) { throw 'entry status read failed' }
if ($entryCommit -ne '<expected-base-commit>' -or $entryTree -ne '<expected-base-tree>') {
  throw 'entry subject mismatch'
}
if ($entryStatus.Count -ne 0) { throw 'entry checkout is not clean' }
[ordered]@{
  schema_version = 'iris-scenario-consolidation-entry-subject-v1'
  timestamp_utc = [DateTime]::UtcNow.ToString('o')
  entry_policy = 'owner_selected_lightweight_exact_subject_lock'
  baseline_admission_axis = 'not_run_no_current_subject_qualification'
  subject = [ordered]@{ commit = $entryCommit; tree = $entryTree }
  checkout_clean = $true
  predecessor_admission = 'historical_only_not_reused'
  current_subject_admitted_claim = $false
  original_worktree_mutated_by_gate = $false
} | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $entryReceipt -Encoding utf8
```

Expected: PowerShell exit `0`; schema `iris-scenario-consolidation-entry-subject-v1`; intended base commit/tree match; clean checkout; `baseline_admission_axis=not_run_no_current_subject_qualification`; predecessor receipt reuse와 current-subject admitted claim 모두 없음.

#### 2. Identity/collection readpoint

```powershell
uv run python -B Iris/validation/test_workflow_consolidation/collect_execution_census.py `
  --target-repository <exact-candidate-checkout> `
  --output-root <external-result-root>\census

$baselineExactCurrentListReceipt = '<external-result-root>\baseline-exact-current-list.txt'
uv run python -B Iris/_docs/round3/round3_run_contract_tests.py `
  --class current `
  --enforce-current-build-closure `
  --list 2>&1 | Tee-Object -FilePath $baselineExactCurrentListReceipt
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

uv run python -B -m pytest -s --collect-only -q -p no:cacheprovider `
  --round3-contract=current `
  --round3-enforce-denominator `
  --round3-denominator-receipt <external-result-root>\configured-current-collection.json
```

Expected: 세 command exit `0`; static census, current identities, source denominator와 collection errors가 external receipt에 고정됨. Exact list의 command/environment/exit code는 같은 orchestration receipt에 결속한다. Tracked predecessor census 644 rows와 차이가 있으면 증감 identity를 설명하고 새 값을 current denominator로 사용한다.

#### 3. Representative profiling

Configured/historical/diagnostic source-policy class를 포함하는 full-universe pytest selection을 한 번 실행하고 environment-transparent external observer telemetry와 denominator receipt를 같은 transaction에 결속한다.

```powershell
uv run python -B -m pytest -s -q -p no:cacheprovider `
  --round3-contract=all `
  --round3-enforce-denominator `
  --round3-denominator-receipt <external-result-root>\baseline-full-universe.json `
  --durations=0
```

Profiler가 별도 entrypoint로 필요하면 이 command의 selection/argv/env를 그대로 전달해야 한다. 기존 `python_sitecustomize_process_tree` backend는 profiling에 사용하지 않는다. 외부 observer가 개별 축을 신뢰성 있게 관측하지 못하면 measured attribution을 `unattributable`로 남기고 Section 4의 fallback ranking을 사용한다. Node IDs를 source-policy classification과 결합해 current/historical/diagnostic/aggregate projection을 구분하며, known historical advisory는 기존 exact identity일 때만 baseline observation으로 수용한다. 이 단일 표본을 statistical certification으로 해석하지 않는다.

#### 4. Static/syntax sanity during implementation

```powershell
uv run python -B -m py_compile <changed-python-files>
```

필요 시 family-local validator tests를 explicit path로 실행한다. 새 validation directory는 configured-current denominator에 자동 편입하지 않는다.

#### 5. Codex Reviewer static review

한 번의 review에서 다음을 확인한다.

- old/new identity completeness
- assertion/negative/fail-closed meaning preservation
- class/module/global mutable state
- process/bootstrap/crash boundary
- order dependency와 previous-test residue
- aggregate failure masking
- family-specific semantics의 generic runner 흡수 여부
- conditional dependency/config update 누락
- infrastructure proportionality

P0/P1 또는 correctness blocker가 남으면 focused/final로 진행하지 않는다.

#### 6. Focused adopted-family batch and order matrix

```powershell
uv run python -B -m pytest -s -q -p no:cacheprovider `
  --round3-contract=all `
  <explicit-adopted-nonpilot-family-files-or-node-ids>
```

같은 focused transaction이 explicit node order로 `alone`, forward, reverse와 normal full family batch를 실행하고 결과를 하나의 receipt set으로 묶는다. 각 group은 read-only representative 최소 1개와, 존재하는 경우 isolation-sensitive representative 최소 1개를 포함한다. Cost after는 normal full family batch sub-run 한 번의 count만 사용하며 order replay count를 합산하지 않는다.

`--round3-contract=all`은 adopted candidates가 current/historical/diagnostic source에 걸칠 수 있어 explicit node IDs의 source-policy applicability를 유지하기 위해 사용한다. 이는 전체 `all` route PASS 주장이나 unrelated historical advisory 재판정이 아니며, 선택되지 않은 advisory는 실행/closeout 대상에 포함하지 않는다.

Expected:

- mapped assertions PASS
- negative/fail-closed cases 보존
- producer failure와 consumer assertion failure 구분
- mutation/fresh-process contract 보존
- order-dependent mismatch `0`
- source mutation `0`

#### 7. Post-change exact/configured metadata readpoint

Focused transaction과 동일 final subject에서 metadata-only receipt를 생성한다.

```powershell
$finalExactCurrentListReceipt = '<external-result-root>\final-exact-current-list.txt'
uv run python -B Iris/_docs/round3/round3_run_contract_tests.py `
  --class current `
  --enforce-current-build-closure `
  --list 2>&1 | Tee-Object -FilePath $finalExactCurrentListReceipt
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

uv run python -B -m pytest -s --collect-only -q -p no:cacheprovider `
  --round3-contract=current `
  --round3-enforce-denominator `
  --round3-denominator-receipt <external-result-root>\final-configured-current-collection.json
```

Exact runner는 `--list`일 때 `--out`을 처리하지 않으므로 list file과 함께 command, environment, subject 및 exit code를 orchestration receipt에 보존한다. Pre-change exact list/configured receipt와 final receipt를 identity별로 비교하여 authorized mapping 이외의 추가/누락, build-closure failure, collection error와 denominator 축소가 `0`인지 확인한다. 이 두 command는 execution-cost 또는 wall-time 표본이 아니며 long-run budget에 포함하지 않는다.

#### 8. Final canonical long gate

```powershell
powershell -ExecutionPolicy Bypass -File .\Iris\validation\clean_checkout\invoke_receipt_bound_full_gate.ps1 `
  -RepositoryRoot <exact-repository-root> `
  -Commit <exact-final-commit> `
  -ClaimId <claim-id> `
  -EnvironmentReceipt <external-environment-receipt> `
  -WorkRoot <new-external-work-root> `
  -ResultRoot <new-external-result-root> `
  -OrchestrationReceipt <external-orchestration-receipt>
```

필요한 deterministic Run A/B는 canonical full-gate wrapper 내부의 기존 `invoke_deterministic_compare.ps1` contract를 그대로 사용하며 별도 long execution으로 중복 계상하지 않는다. 이 계획은 full gate의 denominator, command 또는 claim boundary를 축소하지 않는다. Comparable full-gate before가 없으므로 이 final 결과는 validation outcome과 final observation으로만 기록하고 wall-time reduction을 계산하지 않는다.

### Cost and success interpretation

구조적 success gate:

```text
distinct_nonpilot_scenario_group_count >= 3
each_cost_adopted_group_consolidatable_invocation_reduction >= 50%
unmapped_identity_count = 0
negative_contract_loss_count = 0
shared_mutable_state_violation_count = 0
adopted_or_corrected_support_module_global_writable_state_count = 0
required_fresh_process_violation_count = 0
tracked_source_mutation_count = 0
final_exact_current_unauthorized_identity_drift_count = 0
final_configured_current_unauthorized_denominator_drift_count = 0
```

Isolation-only correction은 distinct cost-adopted group count와 50% gate에 포함하지 않으며 `cost_claim=none`을 기록한다. 모든 cost-adopted group은 consolidatable gate 외에 total invocation before/after와 total reduction percentage를 함께 공개한다.

Performance target:

```text
configured-current wall time reduction target >= 20%
canonical full-gate wall time reduction target >= 15%
```

판정은 다음과 같다.

- baseline/final에 동일 configured-current selection이 없으므로 20% target은 `not_measured_no_comparable_baseline`이다.
- canonical full gate는 final에서만 실행하므로 15% target은 `not_measured_no_baseline`이다.
- 두 target은 이번 execution의 success gate가 아니며 달성/미달을 주장하지 않는다.
- `theoretical_ceiling_round3_all`과 source-class ceilings는 candidate prioritization에만 사용하며 다른 selection의 configured/full-gate target으로 전파하지 않는다.
- measured attribution이 없어 proxy ranking만 사용했다면 full-universe/source-class ceiling도 `unattributable`이다.
- 단일 full-universe baseline 표본은 `observed baseline cost breakdown`으로만 기록한다.
- 어느 경우에도 timing target 때문에 isolation/assertion/denominator를 완화하지 않는다.

### Manual Validation

Product/runtime/UI 변경이 없으므로 PZ 인게임 검증은 수행하지 않는다.

대신 다음 수동 inspection을 수행한다.

- candidate ledger의 shared/mutable/process boundary가 실제 code path와 일치하는지 검토
- old/new identity map과 test failure message 대조
- raw telemetry와 compact summary의 수치 reconciliation
- config diff가 있다면 owner adoption/denominator 의미 검토
- excluded-low-gain family reason 검토
- final closeout claim이 실제 adopted/validated 범위를 넘지 않는지 검토

### Validation Limits

- no multiplayer validation
- no long-session runtime validation
- no PZ manual runtime/UI validation
- no deployment, package publication or Workshop validation
- no external mod compatibility sweep
- no global 644-test order-independence proof
- no global shared-state absence proof
- no statistical benchmark certification
- no median/p95/variance claim from the single representative/final samples
- no historical/diagnostic reproduction beyond the single declared `--round3-contract=all` baseline and what the canonical final gate itself requires
- no unrelated failure remediation

---

## 8. Risk Surface Touch

### Authority Surface

**Direct Iris information authority change: None.**

`ScenarioResult`, profiler output와 identity/cost ledger는 test execution artifact이며 source, Evidence, classification, DVF, Registry, Publish 또는 runtime payload authority가 아니다.

Test dependency/source authority는 조건부로만 touch한다. 기존 node와 source를 유지하면 taxonomy, required-validation, source policy와 full-gate membership은 byte-identical하게 유지한다. 새 support dependency 또는 identity migration이 unavoidable할 때만 owner-approved additive transaction을 수행한다.

### Runtime Behavior Surface

**None.**

- production Lua 변경 없음
- Browser/Menu/Tooltip/Wiki behavior 변경 없음
- DVF/Registry/runtime/package production code 변경 없음
- JVM/JAR/Mixin component 추가 없음

### Compatibility Surface

**Internal test compatibility surface only.**

보존 대상:

- pytest node IDs와 unittest exact test IDs
- configured/exact/full entrypoints
- standalone CLI and subprocess semantics
- fixture-visible error/output contract
- Windows path/external-root contract
- required-validation and source-policy identity

### Sealed Artifact Surface

기존 sealed predecessor와 precision-lightweighting evidence는 수정하지 않는다.

신규 successor summary는 새 namespace에 additive하게 기록하고 predecessor PASS, blocked trace 또는 historical receipt를 소급 변경하지 않는다.

### Public-Facing Output Surface

**None.**

Iris Menu, Tooltip, public text, package/Workshop output은 변경하지 않는다.

---

## 9. Risk Analysis

### Architecture Risk

- **Generic runner overreach**: family-specific authority/lifecycle semantics가 공통 infrastructure로 흡수될 수 있다.
  - Mitigation: 세 concrete family가 동일 contract를 공유하기 전까지 family-local fixture/runner 사용.
- **Test infrastructure의 새 authority화**: ScenarioResult나 ledger가 Iris fact/Registry authority로 오인될 수 있다.
  - Mitigation: test-only namespace와 `authority_effect=none` claim boundary 유지.
- **Denominator bypass**: node/source merge로 current validation 분모가 조용히 줄 수 있다.
  - Mitigation: pre/post exact list, configured collection, full-gate inventory hash와 identity map 대조.
- **Scenario counting inflation**: 하나의 producer를 여러 family 이름으로 나눠 최소 3개를 형식적으로 충족할 수 있다.
  - Mitigation: canonical input + producer signature + isolation boundary가 같은 대상은 하나의 `scenario_group_id`로만 계수.
- **Current-subject admission evidence reduction**: owner-selected lightweight gate는 Baseline Admission의 Run A/B, durable bundle, independent review 또는 owner seal을 대체하지 않으며 그 수준의 entry evidence를 제공하지 않는다.
  - Mitigation: clean exact base lock, predecessor receipt non-reuse, full-universe baseline, focused validation과 final canonical full gate를 각각 수행하고 `baseline_admission_axis=not_run_no_current_subject_qualification` claim ceiling을 closeout까지 유지한다.

### Runtime Risk

- Product runtime risk는 낮다. production Lua를 수정하지 않는다.
- **Test process-state risk**는 높다. class fixture, import cache 또는 environment가 test 결과에 영향을 줄 수 있다.
  - Mitigation: class-owned lifecycle, immutable raw result, explicit teardown, order matrix와 standalone process retention.
- **Profiler distortion**: observer가 subprocess/env/cache behavior를 바꿀 수 있다.
  - Mitigation: observer on/off parity probe; mismatch 시 telemetry 폐기.
- **Attribution loss**: external observer가 removable cost를 귀속하지 못할 수 있다.
  - Mitigation: `baseline_summary.json`의 축별 observer-free deterministic-count matrix를 Change 2의 첫 입력으로 사용한다. Qualified proxy proof가 없는 row는 fail-closed exclusion하며 모든 safe row가 제외되면 round 전체를 `blocked_insufficient_safe_ranked_candidates`로 종료한다.

### Compatibility Risk

- **Fresh-process loss**: standalone CLI, import/bootstrap, crash semantics를 in-process fixture가 대체할 수 있다.
  - Mitigation: candidate ledger에 fresh-process-required tail 명시; 해당 invocation은 reduction denominator에서 제외.
- **Required identity drift**: artifact lifecycle/registry authority test support 변경이 exact dependency inventory와 어긋날 수 있다.
  - Mitigation: exact-current enforcement/readpoint와 clean-checkout dependency census를 실행하고, canonical full gate receipt에서 required-selection execution coverage를 확인.
- **File-contract loss**: JSON artifact를 in-memory result로 바꾸며 byte/path/serialization assertion을 잃을 수 있다.
  - Mitigation: external/file contract point를 family boundary에 명시하고 해당 serialize/inspect 유지.

### Regression Risk

- **Shared mutable state**: nested dict/list 또는 shared workspace가 assertion 간 오염을 만들 수 있다.
  - Mitigation: immutable primitives/deep-immutable structures, defensive parse/copy, case-local writable suffix. Zero-state gate는 adopted/corrected scenario support scope에 한정한다.
- **Failure identity collapse**: class setup failure가 여러 node를 하나의 setup error로 축약할 수 있다.
  - Mitigation: setup은 outcome을 capture하되 throw하지 않고 각 node가 producer status와 자신의 checkpoint를 독립 검증.
- **Order dependency**: cleanup/restore나 cached result가 앞선 test에 의존할 수 있다.
  - Mitigation: alone/forward/reverse/family batch matrix.
- **Clone cost inversion**: seed clone 비용이 original setup보다 커질 수 있다.
  - Mitigation: before/after materialization bytes/time 측정; cost gain이 없지만 isolation defect가 확인되면 `adopt_isolation_correction_no_cost_claim`, defect가 없으면 prefix-only 또는 exclude disposition.
- **Reduction denominator overstatement**: retained process/file-contract invocation을 감춘 채 50% reduction을 과장할 수 있다.
  - Mitigation: consolidatable denominator와 total before/after를 동시에 공개하고 overlapping retained category를 한 번만 제외.
- **Current dirty worktree contamination**: 병행 사용자 변경이 timing/identity에 섞일 수 있다.
  - Mitigation: exact clean candidate checkout에서 profiling/final validation; 현재 worktree에는 계획 문서 외 unrelated 파일을 수정하지 않음.

---

## 10. Rollback Plan

Rollback unit은 `scenario_group_id` 단위다.

```text
old direct execution per test
<->
shared immutable scenario execution + independent assertions
```

다음 중 하나가 발생하면 해당 family만 기존 direct execution path로 되돌린다.

- assertion parity 또는 failure attribution 손실
- old/new identity mapping 불완전
- shared mutable state 또는 order dependency
- fresh-process/bootstrap/crash contract 손실
- required-validation/dependency binding drift
- cost-adopted scenario의 consolidatable invocation reduction 50% 미달
- clone/materialization overhead가 제거 비용을 상쇄
- abstraction/maintenance cost가 measured 또는 qualified structural invocation gain보다 큼

Rollback 순서:

1. 해당 scenario group의 test/support code만 predecessor structure로 복원한다.
2. 해당 scenario group의 identity/cost ledger disposition을 `rollback_<reason>`으로 갱신한다.
3. 해당 scenario group focused tests와 denominator/dependency check를 다시 실행한다.
4. 다른 정상 adopted non-pilot scenario group은 유지한다.
5. rollback 후 정상 cost-adopted group이 1~2개면 이미 검증된 개선을 유지하고 closeout을 `partial_adoption_below_target`으로 기록한다. 0개이거나 안전한 candidate 자체가 없으면 `blocked_insufficient_safe_ranked_candidates`로 종료한다.

Isolation-only correction은 cost 감소 미달만으로 rollback하지 않는다. Isolation contract 자체의 regression 또는 호환성 손실이 있을 때만 해당 correction을 되돌린다.

Generic runner가 도입된 뒤 공통 문제가 발견되면 consumer를 family-local fixture 또는 direct producer로 되돌린다. Iris product/runtime/data rollback은 필요하지 않다.

Profiler가 environment를 변경한 것으로 확인되면 해당 baseline/final telemetry와 그로부터 계산한 rank/ceiling을 폐기한다. profiler를 교정한 뒤 representative profiling 범위만 다시 수행하며 기존 sealed predecessor는 수정하지 않는다.

Config/manifest 변경이 있었던 family를 rollback할 때는 code와 taxonomy/required/source/dependency mapping을 동일 transaction에서 되돌려 dangling identity를 남기지 않는다.

---

## 11. Governance Constraints

- `docs/Philosophy.md` 준수: Iris는 정보 모드이고 product runtime은 100% Lua이며 Pulse 또는 다른 spoke의 역할을 침범하지 않는다.
- Pulse는 Iris에 의존하지 않고 Iris는 다른 spoke를 직접 참조하지 않는다.
- Owner-selected lightweight entry integrity gate를 application code/test/config mutation 전에 통과한다.
- Current subject에 대해 Baseline Admission PASS, external qualification, durable bundle, independent admission review 또는 owner seal이 존재한다고 주장하지 않는다. 기존 predecessor receipt는 historical-only다.
- 실행 시작 시 `ARCHITECTURE.md`의 실제 consolidation section과 `DECISIONS.md`/`ROADMAP.md` status를 현재 code/handoff와 대조하고 section number나 status drift를 ledger에 기록한다.
- exact-current enforcement/readpoint, configured-current pytest collection authority와 canonical full-gate validation authority를 서로 대체하거나 하나의 합격 수치로 혼합하지 않는다. Exact-current execution coverage는 full-gate receipt의 required selection으로 입증한다.
- source denominator, required validation, historical/diagnostic role을 optimization 수단으로 변경하지 않는다.
- existing test node 유지와 minimal diff를 우선한다.
- shared result는 immutable이어야 하며 module-global writable cache, previous-test output reuse와 hidden memoization을 금지한다.
- mutation/tamper/rollback/recovery/concurrency state는 case-local writable owner를 가진다.
- standalone executable, import/bootstrap, process environment, crash/termination이 subject인 case는 fresh process를 유지한다.
- serialization/file contract가 subject인 artifact는 materialize/inspect 경계를 유지한다.
- generic framework의 신규 도입/확장은 pilot을 포함해 최소 3 concrete consumer family가 동일 execution contract를 공유할 때만 허용한다.
- raw telemetry, temp roots, JUnit/stdout/stderr와 disposable cache는 repository 밖에 둔다.
- generated cache/bytecode residue와 tracked source semantic failure를 구분한다.
- unrelated historical advisory 또는 병행 사용자 변경을 이 scope에서 수정하지 않는다.
- 기존 sealed predecessor evidence는 additive trace로 보존하고 소급 수정하지 않는다.
- Codex Reviewer static review는 1회이며 P0/P1과 unresolved semantic/isolation blocker가 0이어야 한다.
- 공식 기본 budget은 baseline `--round3-contract=all` full-universe profiling 1회, static review 1회, focused transaction 1회, final canonical full gate 1회다. Lightweight entry receipt와 pre/final list/collect/census는 metadata readpoint이며 long-run budget에 포함되지 않지만 실제 실행 횟수는 숨기지 않고 기록한다.
- actual correctness failure가 확인되지 않으면 formatting/cache/advisory 이유로 full long transaction을 반복하지 않는다.
- performance target은 correctness/isolation/denominator 완화를 허가하지 않는다.
- rigid `runner LOC <= consolidation LOC` 수식은 mandatory gate가 아니지만 새 infrastructure LOC와 repository-wide net test/tooling LOC를 반드시 기록한다.
- 별도 external independent review 또는 owner seal을 이번 successor closeout에 새로 요구하지 않는다. Codex Reviewer static review와 owner-selected entry policy는 서로 다른 축이며 external admission review PASS로 표현하지 않는다.
- bare `complete` vocabulary를 사용하지 않는다. implementation, identity, validation, cost reduction과 performance observation을 축별로 기록한다.

---

## 12. Expected Closeout State

정상 목표 상태는 다음과 같다.

```text
implementation_axis = implementation_complete
entry_axis = clean_exact_subject_locked
baseline_admission_axis = not_run_no_current_subject_qualification
identity_axis = identity_preserved
isolation_axis = isolation_preserved
validation_axis = focused_and_canonical_full_gate_pass
denominator_axis = final_exact_and_configured_receipts_match
cost_axis = distinct_nonpilot_scenario_target_met
profiling_axis = full_universe_baseline_observed | unattributable
adoption_evidence_axis = measured_cost_consolidation | proxy_ranked_structural_consolidation | mixed
configured_performance_axis = not_measured_no_comparable_baseline
full_gate_performance_axis = not_measured_no_baseline
overall = selected_nonpilot_scenario_consolidation_complete
```

이번 execution에서는 comparable-route before/after wall-time evidence를 생성하지 않는다. 따라서 closeout에는 `comparable_route_wall_time_evidence = not_produced_this_round`를 명시한다.

`overall=selected_nonpilot_scenario_consolidation_complete`는 current subject의 Baseline Admission, external qualification, independent admission review 또는 owner seal 완료를 뜻하지 않는다. 해당 축은 항상 `baseline_admission_axis=not_run_no_current_subject_qualification`로 남긴다.

`selected_nonpilot_scenario_consolidation_complete`를 주장하려면 다음이 모두 필요하다.

1. Lightweight entry integrity gate가 intended base commit/tree와 clean isolated checkout을 고정했고 entry lock 전 application code/test/config mutation이 없었다.
2. full-universe cost-ranked duplication map과 각 row의 ranking/adoption evidence basis가 존재한다. Measured attribution이 없으면 row category는 `proxy_ranked_structural_consolidation`, removable-cost/wall-time claim은 `none`, ceiling은 `unattributable`로 명시한다.
3. 서로 다른 safe non-pilot `scenario_group_id` 최소 3개가 cost-adopted 됐다.
4. 각 cost-adopted scenario group의 consolidatable expensive invocation이 최소 50% 줄고 total before/after도 공개됐다.
5. old/new test/case identity에 unmapped row가 없다.
6. assertion, negative/fail-closed contract와 failure attribution 손실이 없다.
7. shared mutable state, order dependency와 required fresh-process 위반이 없다.
8. Codex Reviewer P0/P1 및 unresolved blocker가 0이다.
9. focused transaction과 canonical full gate가 final subject에서 PASS했다.
10. final exact-current list/configured-current collection receipt가 pre-change readpoint와 대조됐고 authorized mapping 이외 denominator drift가 없다.
11. tracked source mutation과 unauthorized dependency drift가 없다.

다음 상태는 축별로 명시한다.

- entry subject가 intended base와 다르거나 isolated checkout이 dirty임: `blocked_entry_integrity`
- safe measured-cost/qualified-proxy non-pilot candidate가 0개: `blocked_insufficient_safe_ranked_candidates`
- 구현/rollback 후 검증된 cost-adopted scenario group이 1~2개: `partial_adoption_below_target`
- implementation은 끝났으나 final gate 실패: `implementation_complete_validation_blocked`
- proxy ranking만 가능하여 performance ceiling/claim을 만들 수 없음: `selected_nonpilot_scenario_consolidation_complete_performance_unattributable`
- configured-current comparable final이 없음: configured performance axis `not_measured_no_comparable_baseline`
- canonical full-gate before가 없음: full-gate performance axis `not_measured_no_baseline`
- isolation-only correction만 완료되고 cost-adoption target은 충족하지 못함: `isolation_correction_complete_cost_adoption_partial_or_blocked`

최종 claim은 다음 범위로 제한한다.

```text
selected non-pilot Iris scenario groups
-> owner-selected lightweight entry used; current-subject baseline admission not run or claimed
-> measured-cost consolidation and proxy-ranked structural consolidation separated
-> comparable-subject common execution invocation counts consolidated
-> existing assertion identity preserved
-> isolation/process semantics preserved
-> observed comparable-subject consolidatable producer/subprocess/materialization counts reduced
-> wall-time target not claimed without comparable route baseline
```

이 closeout은 Iris 644-test 전체 consolidation, global order-independence, global shared-state absence, statistical performance certification, Iris runtime correctness 재인증, PZ runtime 성능 향상, package/release/Workshop readiness 또는 external ecosystem compatibility를 의미하지 않는다.
