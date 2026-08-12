# Implementation Plan

> 계획명: Iris 테스트 경량화 Terminal Closeout Recovery
>
> 기준일: 2026-08-12
>
> 선행 계획: `docs/iris_test_precision_preserving_test_suite_lightweighting_plan.md`
>
> 입력: `Iris 테스트 경량화 Terminal Closeout Recovery — 종합 로드맵`
>
> Revision: 종합 검토 R1~R17 및 실행 동기화 addendum 반영 — plan authority materialization, closeout carrier, route-scoped reconciliation, collection-only/environment/precondition materialization 보강
>
> Execution readiness: 먼저 Change 0에서 이 문서만을 운반하는 immutable `S_plan`을 materialize해야 한다. 그 뒤 plan-infrastructure capability 구현과 precondition materialization은 허용한다. Application blocker attribution/remediation은 Change 1의 carrier-aware retrieval, exact-current collection과 non-machine preconditions가 materialize되기 전까지 `blocked`다.
>
> 현재 공식 상태: `blocked_before_terminal_validation`
>
> 작성 시점 plan 상태: `S_preterminal` checkout에서 이 문서는 untracked다. 실행 전 plan-only commit으로 추적해야 하며, 해당 commit은 comparison/validation subject가 아니다.
>
> Execution weight: Heavy — validation authority, historical reproduction, sealed artifact와 terminal evidence chain을 다룸
>
> Runtime / production / public output 변경: 기본 범위에서 없음

## 1. Objective

이 계획의 목적은 Iris 테스트 정밀도 보존형 경량화 구현을 소급해 PASS로 바꾸는 것이 아니라, 현재 귀속되지 않은 terminal blocker를 동일 조건의 세 subject 비교로 분류하고 causal blocker만 최소 수정한 뒤 새 immutable candidate에서 terminal closeout 전체를 다시 수행하는 것이다.

비교 subject는 다음과 같이 고정한다.

```text
S_base
= 55bc0578cb0361cc35eb5830a859f66bb2b2872d
tree d7ff13ca7a61304a3d7b197eb602b31a532f6a3b

S_impl
= 8a10ac42ea6f8d5759e521ad041e5ee161bf1311
tree 932da95829eb69e7dc5afa2b7145387979061873

S_preterminal
= ecf9c75768ff824fdf4d441cfccb4708b3117c2b
tree c4b9de587ac8698dfd865de8afc50dcf6832c15f

S_plan
= Change 0에서 materialize할 plan-only immutable commit/tree
= parent S_preterminal
= exact delta docs/iris_test_lightweighting_terminal_closeout_recovery_plan.md only
!= S_base / S_impl / S_preterminal
!= comparison arm / remediation subject / terminal candidate
```

Git object와 ancestry를 직접 확인한 결과 세 subject는 모두 존재하고 `S_base -> S_impl -> S_preterminal` 계보를 이룬다. `S_base`는 tracked `baseline_manifest.json`이 `clean_checkout_only` accepted subject로 결속한 기준선이고, `S_preterminal`은 `S_impl` 이후 source 변경 없이 preterminal evidence를 추가한 chronology subject다. 이후 HEAD에서 얻은 관측은 별도 observation subject로 기록하며 이 셋 중 하나를 대체하지 않는다.

이 계획 문서는 작성 시점에 untracked이므로 실행 authority가 아직 Git object로 materialize되지 않았다. Change 0은 사용자 working tree의 다른 변경을 stage/commit하지 않고 이 파일 하나만 추가한 단일 plan-only child commit을 만든다. 그 commit을 `S_plan`으로 봉인한다. `S_plan`이 생겨도 고정 비교 subject와 공식 predecessor state는 바뀌지 않으며 `S_preterminal`을 현재 HEAD나 `S_plan`으로 재지정하지 않는다. 새 실행 세션은 `S_plan`에서 계획을 읽되 세 비교 arm은 계속 `S_base`, `S_impl`, `S_preterminal`이다.

현재 authoritative result는 계속 다음과 같다.

```text
focused             = assertion PASS / tracked source mutation observed
exact-current       = 219/219 PASS
configured-current  = 458 passed / 1 skipped / 3 failed / 9 errors
historical          = BLOCKED before canonical completion
diagnostic/all      = not run after fail-closed blocker
terminal state      = blocked_before_terminal_validation
```

완료 목표는 comparison contract → three-subject paired reproduction → attribution → minimum remediation → dependency/A1/precision/fault recensus → immutable candidate → five-route terminal Run A/B → independent review → owner seal → durable bundle → evidence-only closeout carrier → fresh-root retrieval/replay 순서로 닫는 것이다. Code/test/config validation, review와 owner seal은 `S_terminal`에 결속하고, final tracked pointer는 별도 `S_closeout_carrier`가 운반한다.

```text
S_terminal
= exact validated code/test/config subject
= terminal validation subject
= review subject
= owner seal subject

S_closeout_carrier
= evidence-only tracked pointer carrier
!= S_terminal
= references S_terminal + final bundle/seal identities

fresh-root validation replay subject
= S_terminal
```

최종 hard invariants:

```text
unattributed_blocker_count = 0
plan_authority_materialized = true
S_plan_parent = S_preterminal
S_preterminal_to_S_plan_delta = plan document only
comparison_subjects_exclude_S_plan = true
focused_tracked_write_violation_count = 0
precision_regression = 0
fault_matrix_delta = 0
original_A1_baseline_relative_conditions = preserved
mandatory_route_failure_count = 0
post_checkout_clean = true
```

---

## 2. Scope

이 계획은 선행 경량화 구현 이후 발생한 terminal closeout blocker의 비교, 귀속, 최소 수정, 재계측과 terminal governance chain만 다룬다.

포함 범위:

* untracked 계획 문서의 plan-only commit materialization과 immutable `S_plan` authority 동결
* 세 subject의 commit/tree/lineage 및 canonical command contract 동결
* focused, exact-current, configured-current, historical, diagnostic/all 다섯 route의 denominator와 node/source identity 화해
* 각 subject × 각 route × Run A/B의 clean-checkout comparison evidence
* focused 실행의 tracked staging/source mutation 제거
* configured-current `CC-1`~`CC-4` family별 causal attribution과 수정
* historical bootstrap, duplicate option registration, mixed-item denominator, source inventory와 selection 복구
* plan-local validator와 supporting test의 recursive dependency closure 재계산
* 경량화 A1, precision과 fault matrix의 remediation 이후 live recensus
* immutable `S_terminal_candidate`의 terminal Run A/B와 deterministic comparison
* independent review, owner seal, external durable bundle, fresh-root retrieval/replay
* `S_terminal`과 evidence-only `S_closeout_carrier`의 identity/DAG 검증
* reviewer eligibility, owner durable custody root와 retrieval capability의 remediation 이전 materialization
* 사용자 dirty worktree의 read-only pre/post identity proof
* 기존 FAIL/BLOCKED evidence의 additive preservation

### Conflict Decisions Adopted By This Plan

종합 로드맵의 보류 항목은 현재 코드와 선행 계획의 authority에 따라 다음처럼 고정한다.

| 항목 | 이 계획의 판정 | 근거 |
|---|---|---|
| plan authority | 실행 전 이 문서만 추가하는 `S_plan`을 `S_preterminal`의 단일 child로 materialize하고 비교/검증 subject에서는 제외한다. | untracked working-tree 문서는 새 세션과 clean checkout의 durable execution authority가 될 수 없다. |
| baseline lineage | 필수 선행 gate. 현재 ancestry와 accepted baseline binding은 확인됐지만 실행 시 machine receipt로 다시 봉인한다. | chronology 혼입을 방지한다. |
| denominator reconciliation | source, node, mixed-item override, subtest 수준의 사전 화해를 필수화한다. | `conftest.py`는 source policy와 item override를 별도로 적용하며 sealed/observed 수치가 다르다. |
| attribution Run A/B | `3 subjects × 2 runs × 5 routes`를 필수화한다. | 동일 arm 변동을 causal chronology로 오인하지 않기 위해서다. |
| attribution diagnostic | route별 advisory 실행을 허용·요구한다. Terminal 단계만 fail-closed 순서를 쓴다. | 원인 규명과 terminal PASS chain은 목적이 다르다. |
| taxonomy | `A0`~`A6`를 사용한다. | nondeterminism과 denominator/subject identity를 독립 보존한다. |
| attribution acceptance | 전체 blocker ledger에 machine evidence와 owner acceptance를 요구한다. | hash adoption, denominator, historical selection처럼 owner authority가 포함될 수 있다. |
| validator universe | actual execution/import semantics의 recursive closure를 계산하고 counting rule을 사전 승인한다. | 모든 root가 `_common.py`를 import하지만 현재 manifest가 이를 누락한다. |
| `__init__.py` | package/import semantics에 실제 참여하면 포함하고 비참여를 증명하면 제외 사유를 기록한다. | 파일명 또는 임의 선택으로 closure를 만들지 않는다. |
| supporting test | 별도 축으로 보고하되 terminal round closure에는 포함한다. | 현재 manifest row에는 있지만 선언 file count/LOC에서는 제외돼 의미가 혼재한다. |
| common dependency | unique closure set에서 한 번 계상하고 consumer edge를 별도 기록한다. | 중복 LOC와 실제 edge 손실을 함께 피한다. |
| physical write denial | feasibility probe는 수행하되 보조 방어로만 사용한다. | 최종 authority는 external containment, pre/post Git identity와 tracked write 0이다. |
| remediation granularity | causal blocker/attribution class별 독립 commit과 rollback unit을 사용한다. | candidate rejection 뒤 부분 rollback을 가능하게 한다. |
| terminal Run A/B | 다섯 route 모두 필수다. | 선행 plan과 보호 test가 이미 terminal A/B를 계약화한다. |
| reviewer | 계획·구현·attribution 결정에 참여하지 않은 independent reviewer를 요구하며 제품/모델명으로 제한하지 않는다. | 독립성이 목적이다. |
| completion vocabulary | `machine_validation`, `independent_review`, `owner_seal` 세 축과 기존 closeout state를 유지한다. | 새 governance vocabulary를 만들지 않는다. |
| full implementation revert | invariant를 지킬 최소 remediation이 없을 때만 owner escalation option으로 연다. | 자동 fallback 범위를 넘어선다. |

Route denominator reconciliation state는 다음으로 고정한다.

```text
R-full
= prior/current observation 모두 존재
= full source/node/item/subtest reconciliation required

R-defer
= collection/bootstrap 미성립
= reconciliation_deferred_pending_bootstrap

R-first
= prior authoritative observation 없음
= first_observation_no_prior_denominator
```

`R-full`만 `unexplained_denominator_delta=0`을 요구한다. `R-defer`와 `R-first`는 unavailable을 0으로 바꾸지 않고 route, unavailable input, reason과 후속 transition을 기록한다. Historical `R-defer`는 bootstrap remediation 후 반드시 `R-full`로 전환되어야 terminal qualification에 진입할 수 있다. Diagnostic/all `R-first`는 first observation을 봉인한 뒤 terminal candidate에서 동일 command의 Run A/B identity를 비교한다.

### Explicitly Out Of Scope

* 새로운 test merge, 삭제, scenario deduplication 또는 추가 node 감소
* A1 정의, large-file/method 정의나 denominator를 현재 결과에 맞춰 변경
* skip, xfail, allowlist, ignore, deselection 또는 reclassification으로 gate 우회
* Iris runtime Lua, Browser, Wiki, Tooltip, Layer 3/4 또는 public output 변경
* test convenience를 위한 production hook
* Iris-wide pytest architecture 재설계와 unrelated historical defect 정리
* predecessor FAIL/BLOCKED evidence rewrite 또는 artifact in-place reseal
* release, Workshop, B42, multiplayer, long-session 또는 전체 mod compatibility 판정

---

## 3. Non-Goals

* exact-current PASS 하나로 terminal closeout 완료를 주장하지 않는다.
* failure signature 유사성만으로 pre-existing defect나 implementation regression을 선언하지 않는다.
* configured-current failures를 하나의 aggregate defect로 취급하지 않는다.
* current collection 수치로 historical denominator를 재정의하지 않는다.
* hash mismatch를 현재 bytes로 덮어써 manifest를 통과시키지 않는다.
* validator LOC 증가를 test-support LOC 감소와 상계하지 않는다.
* diagnostic raw failure를 disposition으로 PASS로 바꾸지 않는다.
* temporary checkout/output root를 durable evidence store로 쓰지 않는다.
* 이미 달성한 A1보다 추가 경량화를 요구하지 않는다.

---

## 4. Assumptions

### Constitutional and Authority Assumptions

* `docs/Philosophy.md`가 최상위 설계 authority다.
* Iris runtime은 100% Lua를 유지하며 이번 계획은 Python validation/test/evidence surface에 한정된다.
* `DECISIONS.md`, `ARCHITECTURE.md`, `ROADMAP.md`와 선행 plan/receipt는 predecessor 사실로 사용하되 현재 실패를 소급 변경하지 않는다.
* commit/tree bytes는 Git object가 authority다.
* `round3_test_taxonomy.json`, `current_route_required_validations.json`, `round3_pytest_source_classification.json`의 분리된 책임을 유지한다.
* historical denominator는 approved historical contract가 소유하며 configured discovery가 대체하지 않는다.
* external terminal bundle custody와 final owner seal은 repository owner 권한이다.
* independent reviewer 지정과 eligibility acceptance도 repository owner-reserved authority다.

### Current Codebase Readpoint

* `pytest.ini`는 configured discovery를, `round3_run_contract_tests.py`는 exact taxonomy와 current required-validation을 별도로 실행한다.
* `S_base`, `S_impl`, `S_preterminal` 세 subject의 exact runner는 모두 `--list` option과 required-validation을 합성한 `combined_test_ids` 경로를 가진다. 다만 ordered node/source receipt 계약 충족 여부는 Change 1 preflight에서 별도로 검증한다.
* `Iris/build/description/v2/tests/conftest.py`가 `--round3-contract`, additional source, denominator enforcement와 external receipt option을 등록한다.
* 같은 conftest는 source classification 외에 mixed-source item override를 적용하므로 source, node와 selected-item denominator를 합치면 안 된다.
* tracked preterminal matrix는 A1 만족, `precision_regression=0`, frozen fault hash 일치를 기록하지만 `change8_safety_exit_gate=FAIL`과 `terminal_entry_authorized=false`를 명시한다.
* focused route는 exit 0이지만 residual-seal staging regeneration으로 tracked mutation을 만들었다.
* configured-current는 phase6 evidence root/reseal, standalone subprocess exit, protected-surface hash, current required-validation hash와 연관된 `3 failures / 9 errors`를 보존한다.
* historical은 lower conftest bootstrap, duplicate option registration, mixed-item denominator/selection 문제로 canonical completion에 도달하지 못했다.
* `validator_dependency_manifest.json`은 8 root module에 대해 `671 LOC`와 `closure_complete=true`를 선언하지만 모든 root가 import하는 `_common.py`를 누락한다.
* 같은 manifest는 supporting test row를 포함하면서도 `plan_local_validator_file_count=8`로 선언한다. Root, supporting test, unique closure와 LOC를 분리해 재계산해야 한다.
* 이 알려진 모순은 Change 1에서 additive `known_defect_marker`로 즉시 고지한다. Predecessor bytes는 그대로 두되 terminal accounting authority로 사용하지 않는다.
* current dirty worktree에는 사용자의 runtime/test/evidence/docs 변경이 광범위하게 존재한다. 실행은 이를 stash/reset/clean/overwrite하지 않고 committed objects로 만든 external checkout만 사용한다.
* 이 계획 파일은 작성 시점에 untracked이고 현재 HEAD는 `S_preterminal`이다. Change 0에서 이 파일 하나만 stage/commit한 `S_plan`을 만든 뒤 실행하며, 그 외 dirty/untracked 파일은 plan commit의 tree에 들어가지 않는다.

### Environment and Attribution

* Windows PowerShell과 `uv run python`을 사용한다.
* Python/pytest/plugin identity, locale, timezone, Git config, env와 inputs를 모든 arm에서 고정한다.
* sealed clean-checkout command contract는 receipt interpreter, no `PYTHONPATH`, `-B`, `-s`를 요구한다. 단순히 세 arm의 environment가 같은 것과 authoritative sealed environment에 일치하는 것은 별도 gate다.
* bytecode와 pytest cache는 repository 밖으로 격리하거나 비활성화한다.
* tool 또는 exact input을 materialize할 수 없으면 PASS가 아니라 BLOCKED다.

Taxonomy:

```text
A0_unattributed
A1_preexisting_relative_to_lightweighting
A2_implementation_induced
A3_evidence_commit_drift
A4_environment_or_orchestration
A5_denominator_or_subject_identity
A6_nondeterministic
```

Chronology는 candidate signal일 뿐 단독 확정 근거가 아니다. Command, environment, input/dependency hash, failure signature와 causal/counterfactual evidence를 함께 요구한다. 부족하면 `A0`로 남아 terminal entry를 차단한다.

Scope routing:

```text
A1 pre-existing blocker that physically blocks a mandatory terminal route
=> in-scope minimum remediation candidate

A1 pre-existing defect that does not block a mandatory terminal route
=> out-of-scope / record only

A6 stabilization unsuccessful
=> A0_unattributed
=> terminal entry blocked
```

---

## 5. Repository Areas Affected

### Code

Comparison/attribution 단계에는 causal remediation code 변경이 없다. 단, Change 1 실행 전제인 carrier-aware retrieval mode/tests와 exact-current collection capability는 별도 plan-infrastructure prerequisite로 먼저 구현·검증할 수 있으며 application blocker attribution과 섞지 않는다. 이 예외 변경은 blocker ID 대신 각각 `prerequisite_capability_id=CAP-CARRIER-RETRIEVAL-V2`, `CAP-EXACT-CURRENT-COLLECTION`을 갖고 독립 commit/rollback unit으로 관리한다. 그 밖의 변경은 attribution 뒤 causal evidence와 연결된 경로만 조건부로 수행한다.

Plan-infrastructure source와 tests는 Change 3의 root/supporting/transitive validator universe recensus에 포함한다. 비용은 `plan_infrastructure_validator_file_count`, `plan_infrastructure_validator_LOC`, `plan_infrastructure_supporting_test_count`, `plan_infrastructure_supporting_test_LOC` 축에 기록하며 `gate_registered`와 lifecycle을 함께 보고한다. 이 축은 A1의 `test_support_LOC` denominator와 감축 delta에 산입하거나 상계하지 않는다.

* `Iris/build/description/v2/tests/conftest.py`
* `Iris/_docs/round3/round3_run_contract_tests.py`
* `Iris/_docs/round3/build_historical_reproduction_corpus.py`
* configured failure families를 소유한 `Iris/build/description/v2/tests/test_dvf_3_3_*.py`
* causal producer/orchestrator under `Iris/build/description/v2/tools/build/`
* `Iris/validation/test_lightweighting/**`
* 필요한 경우 `Iris/validation/clean_checkout/**`

경로 목록은 mutation authorization이 아니다. 실제 수정 path는 blocker ID, source of truth, authority와 rollback unit을 가져야 한다.

### Docs

* `docs/iris_test_lightweighting_terminal_closeout_recovery_plan.md`
  * Change 0에서 유일한 delta로 commit하고 immutable `S_plan` authority로 봉인한다.
* `S_terminal_candidate` freeze 전에 필요한 pending-only additive update의 `docs/DECISIONS.md`
* carrier contract 같은 실제 architecture 변경이 있을 때 candidate freeze 전에만 `docs/ARCHITECTURE.md`
* 필요하면 candidate freeze 전에 pending 상태/closure ID만 기록하는 `docs/ROADMAP.md`; final outcome authority는 external bundle이며 post-terminal 결과를 같은 closeout의 tracked docs에 복제하지 않는다.
* 새 evidence root `Iris/_docs/refactor/test_precision_lightweighting/terminal_closeout_recovery/`
* final pointer와 비순환 allowed-delta carrier manifest만 포함하는 evidence-only `S_closeout_carrier`

### Config

* `pytest.ini`는 기본적으로 변경하지 않는다.
* source classification, full-discovery denominator, required-validation와 historical selection manifest는 owner-approved authority change가 필요한 경우에만 additive successor로 변경한다.

### Generated Artifacts

* repository-local durable summary/manifest: comparison contract, normalized outcome/identity, attribution, recensus와 carrier manifest
* repository-external raw validation output: stdout/stderr, pytest reports, collection receipts와 Run A/B raw artifacts
* `3 × 2 × 5` route receipts와 outcome vectors
* node/source denominator reconciliation report
* attribution/remediation ledgers와 owner acceptance
* validator root/edge/closure/LOC recensus
* A1/precision/fault recensus와 candidate qualification
* terminal Run A/B attestation, external bundle, seal, `S_closeout_carrier` pointer와 retrieval report

Predecessor artifact는 overwrite하지 않는다. Raw Run A/B output은 source repository에 기록하지 않으며 repository-local evidence는 normalized durable summary/manifest만 허용한다.

---

## 6. Planned Changes

### Change 0 — Plan authority materialization and execution synchronization

Purpose:

현재 untracked인 이 문서를 새 실행 세션과 clean checkout이 참조할 수 있는 단일 Git authority로 materialize하되, 기존 predecessor와 comparison subject identity는 바꾸지 않는다.

Files:

* `docs/iris_test_lightweighting_terminal_closeout_recovery_plan.md` only
* external `plan_materialization_receipt.json`

Implementation Notes:

* 실행 직전 HEAD가 정확히 `S_preterminal`인지 확인한다. 다르면 commit하지 않고 relevant path/ancestry drift를 분류해 plan synchronization 필요 여부를 다시 판정한다.
* 사용자 working tree의 tracked/untracked 상태를 read-only로 기록한다. 다른 파일을 stash/reset/clean/restore하지 않는다.
* index pre-image를 기록하고, 이 계획 파일 하나만 명시적으로 stage한다. Commit 직전 staged delta가 exact `A docs/iris_test_lightweighting_terminal_closeout_recovery_plan.md`가 아니면 중단한다.
* plan-only commit의 parent가 정확히 `S_preterminal`이고 ancestry distance가 1이며 tree delta가 이 문서 하나인지 확인한 뒤 commit/tree를 `S_plan`으로 기록한다.
* `S_plan`은 plan authority와 execution entry point일 뿐 `S_base`, `S_impl`, `S_preterminal`, attribution arm, remediation subject, `S_terminal_candidate` 또는 `S_terminal`을 대체하지 않는다.
* 새 실행 세션은 `S_plan`의 tracked bytes와 blob hash를 읽고 Change 1을 시작한다. Working-tree copy나 대화에 붙인 사본을 authority로 사용하지 않는다.
* `S_plan` materialization 이후 application code/test/config/evidence가 변경됐거나 관련 committed HEAD가 더 진행됐다면 이를 observation drift로 기록한다. 고정된 three-subject comparison을 몰래 재기준화하지 않으며, 실행 영향이 있으면 계획 addendum/review 전까지 BLOCKED다.
* `plan_materialization_receipt.json`은 `S_plan` commit/tree/parent, plan blob hash, exact name-status delta, stage pre/post identity, excluded dirty-file inventory hash와 `comparison_subjects_unchanged=true`를 기록한다. Commit 자기참조를 피하기 위해 repository 외부 receipt로 둔다.

Validation:

```text
plan_authority_materialized = true
S_plan_parent = S_preterminal
S_plan_ancestry_distance = 1
S_preterminal_to_S_plan_name_status = exact A docs/iris_test_lightweighting_terminal_closeout_recovery_plan.md
S_preterminal_to_S_plan_code_test_config_evidence_delta = 0
unrelated_staged_or_committed_path_count = 0
comparison_subjects = exact [S_base, S_impl, S_preterminal]
comparison_subjects_exclude_S_plan = true
plan_blob_hash_verified_from_S_plan = true
user_worktree_nonplan_path_delta_caused_by_change0 = 0
```

Change 0이 완료되지 않으면 plan-infrastructure capability 구현, attribution 또는 remediation에 진입하지 않는다.

---

### Change 1 — Comparison contract, lineage and denominator reconciliation

Purpose:

수정 전에 모든 subject가 같은 command/environment/input/denominator contract로 비교 가능한지 증명한다.

Files:

* baseline/preterminal manifests, Round 3 taxonomy/source-policy/denominator
* 새 recovery comparison contract와 receipts
* 새 `closeout_preconditions.json`, `user_worktree_preimage.json`, `validator_accounting_known_defect.json`

Implementation Notes:

* subject commit/tree/parent와 `S_base` accepted binding을 봉인한다.
* Change 0 receipt와 `S_plan` commit/tree/blob/parent를 검증하고 comparison arm이 여전히 정확히 `S_base`, `S_impl`, `S_preterminal`인지 봉인한다.
* route별 `argv`, cwd, Python/pytest/plugin identity, env, external inputs, rootdir/conftest bootstrap, selection, exit semantics, output root, mutation policy와 authority manifest를 기록한다.
* outcome vector는 collected/passed/failed/errors/skipped/deselected/xfailed/subtests/exit code를 모두 가진다.
* focused `64+13` 대 `35+14`, configured `486+1+504 deselected+112 subtests` 대 `458+1+3+9`, metric `646 -> 645`와 route denominator 차이를 node/source ID 수준에서 화해한다.
* metric denominator와 validation route denominator를 별도 axis로 유지한다.
* 각 route를 `R-full`, `R-defer`, `R-first` 중 하나로 분류한다. Unavailable observation은 empty set이나 delta 0으로 materialize하지 않는다.
* 다섯 logical route에 execution command와 별도 collection-only companion command를 동결한다. Receipt는 ordered node IDs, source classification, mixed-item disposition, parameter/subtest expansion identity와 collection failure identity를 포함한다.
* pytest collection에서 생성되지 않는 runtime subtest identity는 collection receipt에서 임의 추정하지 않고 `subtest_identity_source=execution_receipt`로 명시해 같은 route의 execution receipt에 결속한다.
* focused route도 explicit affected-source set과 collection receipt를 가져야 한다.
* historical collection이 bootstrap 전에 실패하면 process exit, stderr identity, rootdir/conftest/plugin discovery와 unavailable denominator를 `R-defer` receipt로 남긴다.
* owner-reserved `closeout_preconditions.json`에 다음을 materialize한다.

```text
independent_reviewer_designated
independent_reviewer_eligibility
owner_durable_custody_root
terminal_retrieval_tool_present
terminal_retrieval_tool_mode_support = carrier-aware-v2
exact_current_collection_capability_present
user_worktree_owner_controlled_freeze_accepted
```

* current `fresh-root-v1`은 pointer-containing HEAD를 terminal subject로 해석하므로 `S_closeout_carrier != S_terminal`을 검증할 수 없다. Change 1 plan infrastructure로 `CAP-CARRIER-RETRIEVAL-V2` mode와 positive/missing/tampered/carrier-spoof/terminal-subject-spoof tests를 추가하고, 그 mode가 exit 0으로 preflight된 뒤에만 precondition을 true로 기록한다. `fresh-root-v1` predecessor semantics는 rewrite하지 않는다.
* exact runner의 `--list` capability는 Change 1에서 read-only preflight한다. 존재하지 않거나 required-validation을 포함한 ordered exact identity receipt를 만들지 못하면 `exact_current_collection_capability_present=false`로 기록하고, `CAP-EXACT-CURRENT-COLLECTION` plan-infrastructure 경로에서 기존 execution semantics를 바꾸지 않는 collection-only capability와 tests를 독립 commit으로 구현·검증한다.
* unavailable precondition을 false/blocked로 기록하고 remediation 진입을 차단한다. Reviewer 지정 및 eligibility acceptance는 owner authority다.
* 현재 user worktree의 tracked status, untracked inventory, file type/size와 per-file SHA-256을 read-only pre-image로 기록한다. 전체-equality 규칙을 채택하므로 owner는 closeout 동안 user worktree를 freeze 상태로 유지하는 precondition을 수용해야 한다. 실행 중 owner/user의 unrelated 변경도 false BLOCKED를 만들 수 있으며, 파일을 복원하거나 normalize하지 않고 최종 closeout 뒤 같은 rule로 `user_worktree_delta=0`을 확인한다.
* 알려진 `_common.py`/supporting-test accounting 모순을 additive known-defect marker로 즉시 발행하고 predecessor `closure_complete=true`를 terminal authority에서 제외한다.

Validation:

* ancestry/identity/hash checks exit 0
* `S_plan` authority/parent/exact plan-only delta와 comparison-subject exclusion checks exit 0
* `R-full` route의 unexplained denominator delta 0
* `R-defer`/`R-first` route의 explicit reason/input/transition 필드 누락 0
* collection-only receipt 누락 0
* same-environment-across-arms와 sealed-environment-match가 각각 true
* closeout prerequisite unavailable count 0
* `CAP-CARRIER-RETRIEVAL-V2` preflight exit 0과 positive/missing/tampered/carrier-spoof/terminal-subject-spoof 5개 case PASS
* exact-current collection capability preflight exit 0; capability가 최초 부재했다면 `CAP-EXACT-CURRENT-COLLECTION` implementation/tests exit 0
* user worktree pre-image와 known-defect marker 생성 성공

---

### Change 2 — Three-subject paired reproduction and attribution

Purpose:

현재 blocker를 implementation, preterminal evidence, pre-existing infrastructure, environment, denominator 또는 nondeterminism에 귀속한다.

Files:

* disposable checkout/result roots
* recovery run receipts와 attribution ledger

Implementation Notes:

* 각 subject에서 focused, exact-current, configured-current, historical, diagnostic/all을 Run A/B로 실행한다.
* `diagnostic/all`은 비교 matrix에서 하나의 composite route로 세되, raw diagnostic과 configured-all 두 invocation을 모두 실행하고 각각의 outcome vector를 보존한다. 따라서 logical arm-route count는 `3 × 2 × 5 = 30`, execution invocation receipt count는 `3 × 2 × 6 = 36`이다. Collection-only companion invocation은 이 execution count와 별도 collection receipt count로 보고한다.
* attribution 단계는 route별 advisory execution이다. 한 route failure가 후행 관측을 막지 않지만 raw failure는 그대로 보존한다.
* 동일 arm A/B vector가 다르면 먼저 `A6`로 분류하고 안정화 전 다른 causal class를 확정하지 않는다.
* bounded stabilization의 최대 추가 반복 횟수/시간/환경 재초기화 횟수는 첫 stabilization run 전에 freeze하고 attribution ledger에 hash-bind한다. Ledger는 frozen bound와 실제 반복 횟수를 모두 기록한다. Bound 안에서 A/B가 일치하지 않으면 해당 row를 `A0_unattributed`로 전환하고 terminal entry를 차단하며 결과를 본 뒤 bound를 늘리지 않는다.
* 필요한 synthetic cross-comparison은 diagnostic-only이며 accepted/terminal subject가 아니다.
* 최소 blocker IDs는 `F-focused`, `CC-1`~`CC-4`, `H-1`~`H-5`, `VAL-ACCOUNTING`이다.
* ledger는 subject/run/route, failure signature, first divergence, dependencies/inputs, attribution과 counterfactual evidence를 가진다. Owner acceptance는 외부 owner-authored record 또는 owner-authored approval section으로 materialize하고 exact bytes SHA-256을 ledger가 참조한다. Machine ledger가 owner acceptance를 자체 생성하지 않는다.

Validation:

* logical arm-route count `30/30`
* execution invocation receipt count `36/36`
* collection-only receipt count가 frozen command contract와 일치
* missing receipt와 cross-arm environment drift 0
* owner acceptance record hash mismatch 0
* `A0_unattributed=0` 전 remediation 금지

---

### Change 3 — Validator dependency universe recensus

Purpose:

모순된 `8 files / 671 LOC / closure_complete=true` 선언을 overwrite하지 않고 successor accounting으로 교정한다.

Files:

* `Iris/validation/test_lightweighting/**`
* predecessor manifest read-only
* 새 root manifest, dependency-edge ledger와 closure report

Implementation Notes:

* roots, supporting tests, transitive Python modules, package initializers와 non-Python schema/config/fixture를 분리한다.
* import, runtime path manipulation, subprocess/CLI와 fixture/schema read를 추적한다.
* `_common.py`는 actual import edge 때문에 unique closure에 포함한다.
* `__init__.py`는 실제 semantics 참여 여부로 판정한다.
* supporting test는 별도 count/LOC로 보고하지만 terminal round closure에는 포함한다.
* common dependency LOC는 unique set에서 한 번 세고 consumer edges는 모두 기록한다.
* predecessor declaration은 수정하지 않고 `superseded_for_terminal_authority` successor를 추가한다.
* `__init__.py`, supporting test와 shared dependency set-once counting은 하나의 owner-approved `validator_universe_counting_rule` hash에 결속한다.
* closure 검출 범위는 static import graph, declared subprocess/CLI edges, AST와 string-fragment dynamic path scan, observed file-open/fixture/schema edges로 한정한다. Unobserved dynamic dependency 가능성을 부정하지 않는다.

Validation:

```text
unresolved_dependency = 0
unclassified_dependency = 0
declared counts/LOC = computed counts/LOC by category
validator_dependency_closure_complete_within_declared_detection_scope = true
known_limit = unobserved_dynamic_dependency_possibility_not_disproven
plan_infrastructure_validator_accounting_complete = true
plan_infrastructure_validator_LOC_not_in_A1_test_support_denominator = true
validator_universe_counting_rule_owner_approved = true
```

---

### Change 4 — Minimum causal remediation

Purpose:

owner-accepted attribution ledger에 결속된 blocker만 최소 수정한다.

Files:

* Change 3까지 미정이며 `§5`의 conditional paths 중 causal path만 사용
* remediation design/receipt ledger

Implementation Notes:

각 remediation은 blocker, attribution, affected path/before blob, causal mechanism, source of truth, authority, effect, consumer와 rollback commit을 기록한다.

Focused priority:

1. external output/evidence root를 기존 producer에 전달
2. 기존 `IRIS_CLEAN_CHECKOUT_LEGACY_OUTPUT_ROOT`와 wrapper 재사용
3. fixture/runner output path 교정
4. 불가능할 때만 최소 producer 변경

Configured:

* `CC-1`은 phase6 external root와 producer/fixture/orchestration 책임을 분리한다.
* `CC-2`는 actual subprocess exit, machine report, expectation과 approved CLI contract를 비교한다.
* `CC-3/CC-4`는 changing commit, approved scope와 adoption obligation을 추적하며 blind reseal을 금지한다.

Historical:

* cwd/path, rootdir, initial conftest/plugin loading과 option owner를 먼저 교정한다.
* custom option은 단일 bootstrap owner가 등록한다.
* mixed source는 source selection과 item override/authoritative denominator를 모두 검증한다.
* current collection으로 historical denominator를 바꾸지 않는다.

Remediation은 causal class별 commit으로 분리한다. Exit semantics, protected/required authority, historical denominator, runtime source 또는 full revert는 owner-reserved gate다.

Validation:

* blocker-local validation exit 0
* modified path ↔ blocker row bijection
* unrelated diff와 tracked write violation 0
* historical bootstrap remediation 뒤 historical collection-only companion을 다시 실행해 `R-defer -> R-full` transition receipt 생성
* 전환된 historical `R-full` receipt의 source/node/item/subtest reconciliation과 `unexplained_denominator_delta=0`

---

### Change 5 — A1, precision and fault recensus

Purpose:

remediation이 경량화 효과와 정밀도 계약을 침식하지 않았는지 새로 측정한다.

Files:

* plan-local inventory/protection/detection/comparison validators
* 새 recovery recensus artifacts

Implementation Notes:

Configured nodes, duplicate scenarios, test-support LOC, 500+/1,000+ files, 100+ LOC methods, protected contracts/branches/fail-closed paths, precision과 fault matrix를 candidate tree에서 재생성한다. Preterminal 값을 복사하지 않는다. Accepted baseline definitions를 유지하고 validator accounting은 별도 reporting axis로 둔다.

Validation:

```text
original_A1_baseline_relative_conditions = preserved
removed_duplicate_scenario_reintroduced = false
precision_regression = 0
fault_matrix_delta = 0
unreconciled_metric_row = 0
```

실패하면 candidate qualification을 중단하고 remediation으로 돌아간다.

---

### Change 6 — Immutable terminal candidate qualification

Purpose:

accepted remediation과 recensus를 포함하는 하나의 immutable candidate를 고정한다.

Files:

* Git `S_terminal_candidate`
* candidate qualification manifest

Implementation Notes:

Entry는 `A0=0`, 필요한 owner acceptance 완료, focused mutation/configured/historical/accounting 해결, A1 보존, precision/fault 0, frozen commands, clean checkout을 모두 요구한다. Change 1의 reviewer/eligibility/custody/retrieval precondition도 여전히 available하고 hash-identical해야 한다. Commit/tree, remediation set, diff, metrics와 evidence hashes를 봉인한다. 아직 `S_terminal`이라고 부르지 않는다.

Validation:

* candidate manifest self-verification exit 0
* tracked/nonignored residue와 unresolved authority decision 0

---

### Change 7 — Mandatory terminal Run A/B

Purpose:

fresh clean checkout에서 다섯 mandatory route를 동일 candidate로 두 번 재현한다.

Files:

* `Iris/validation/clean_checkout/**`
* disjoint external Run A/B roots
* terminal attestation와 deterministic comparison

Implementation Notes:

각 run은 focused → exact-current → configured-current → historical → diagnostic/all 순서로 fail-closed 실행한다. 앞 route가 실패하면 뒤 route는 그 run의 terminal chain으로 실행하지 않는다.

Run A/B는 candidate identity, commands, environment, denominator, outcome vector와 post-run Git state가 같아야 한다. Artifact parity의 authority는 checkout/result-root, wall time, run ID와 absolute path를 제거한 canonical payload hash다. Run envelope metadata는 각 run에 기록하지만 byte identity를 요구하지 않는다. Physical write denial은 가능한 경우 보조 방어로 사용하지만 tracked write 0과 cleanliness를 대체하지 않는다.

Fail-closed 중단으로 Run A와 Run B의 executed/skipped route set이 다르면 즉시 Run A/B mismatch다. 같은 route에서 같은 causal failure로 동일하게 중단돼도 terminal PASS는 아니며 rejected candidate evidence로만 보존한다.

모든 조건이 같은 candidate에서 만족된 뒤에만 `S_terminal = S_terminal_candidate`를 선언한다. 실패 candidate는 `terminal_candidate_rejected`로 보존하고 in-place 수정하지 않는다.

Validation:

```text
focused = PASS and tracked mutation 0
exact-current = PASS
configured-current = 0 failed / 0 errors / approved skips only
historical bootstrap, inventory, denominator and tests = PASS
diagnostic/all = executed and PASS
Run_A canonical result = Run_B canonical result
Run_A canonical payload hashes = Run_B canonical payload hashes
Run_A route set = Run_B route set
```

---

### Change 8 — Independent review, owner seal and fresh-root closeout

Purpose:

machine PASS를 governance closeout과 durable retrieval에 연결한다.

Files:

* evidence-only `S_closeout_carrier`의 tracked terminal pointer
* owner-managed external durable bundle의 attestation, machine manifest, review, seal, hash manifest, receipt와 retrieval report

Implementation Notes:

* reviewer는 계획/구현/attribution acceptance에 참여하지 않아야 한다.
* review는 exact terminal subject, commands, attribution, remediation, A1/precision/fault/dependency, A/B와 cleanliness를 검토한다.
* source/config 수정 요구가 나오면 새 candidate qualification부터 반복한다.
* owner seal은 terminal commit/tree와 machine/review/A1/precision/fault/dependency/command hashes를 결속한다.
* review와 owner seal 뒤 external final bundle identity를 확정하고, `S_terminal`에는 손대지 않은 채 exact evidence-only pointer와 비순환 allowed-delta carrier manifest만 포함하는 새 `S_closeout_carrier` commit/tree를 만든다. `S_closeout_carrier`의 유일한 parent는 `S_terminal`이어야 하며 ancestry distance는 정확히 1 commit이다.
* tracked pointer bytes는 `S_terminal` commit/tree, closure ID, bundle manifest hash, owner seal hash와 `carrier-aware-v2` retrieval mode를 결속한다. Pointer가 자신의 containing carrier commit/tree를 직접 포함하는 자기참조는 금지한다.
* `carrier-aware-v2` validator가 pointer-containing HEAD에서 `S_closeout_carrier` commit/tree를 해석하고, `S_terminal..S_closeout_carrier` diff가 approved pointer와 carrier-manifest path에만 한정됨을 검사한 뒤 resolved carrier identity를 external retrieval report에 기록한다. Optional carrier manifest는 pointer blob hash와 allowed-delta policy를 결속하지만 pointer가 carrier manifest hash를 역참조하지 않는다.
* fresh empty root에서 `S_closeout_carrier -> pointer -> external bundle -> S_terminal` DAG의 hash/schema/identity를 검증한 뒤 source checkout은 `S_terminal`로 전환해 mandatory routes를 replay한다.
* carrier에는 code/test/config, command contract, denominator 또는 validation semantics 변경을 허용하지 않는다. Exact allowed delta는 tracked pointer와 사전 승인된 evidence-only carrier manifest뿐이다.

Validation:

```text
independent_review = PASS
P0 = P1 = P2 = P3 = 0
owner_seal = valid
terminal_subject = review_subject = owner_seal_subject
S_closeout_carrier != S_terminal
closeout_carrier_code_test_config_delta = 0
closeout_carrier_allowed_evidence_delta_only = true
closeout_carrier_parent = S_terminal
closeout_carrier_ancestry_distance = 1
carrier_pointer_bundle_terminal_identity_chain = PASS
fresh_root_retrieval = PASS
fresh_root_terminal_revalidation = PASS
post_terminal_subject_change_count = 0
closeout_carrier_unapproved_change_count = 0
user_worktree_delta = 0
```

Terminal closeout 직후 canonical governance ledger에는 별도 additive supersession 의무가 생긴다.

```text
governance_supersession_obligation = required
target = docs/DECISIONS.md
source_authority = S_closeout_carrier pointer + external closeout receipt
execution_subject = S_governance_supersession
S_governance_supersession != S_terminal
S_governance_supersession != S_closeout_carrier
```

`S_governance_supersession`은 terminal validation authority를 새로 만들거나 `S_terminal` PASS를 자신의 PASS로 상속하지 않는 docs-only additive ledger subject다. 수행 전 canonical governance ledger 상태는 `pending_supersession_record`로 남고, terminal machine closeout과 별도로 governance follow-up 미완료를 fail-loud하게 표시한다. 수행 후에는 predecessor `blocked_before_terminal_validation`, `S_terminal`, `S_closeout_carrier`, external receipt와 non-claims를 additive record로 연결한다.

---

## 7. Validation Plan

### Automated Validation

모든 명령은 PowerShell에서 실행하고 exit code, stdout/stderr hash, wall time, subject, Python/pytest identity, env와 post-run Git status를 receipt에 기록한다.

0. Plan authority materialization preflight

```powershell
git rev-parse HEAD
git show -s --format="%H %T %P" <S_plan>
git rev-list --count <S_preterminal>..<S_plan>
git diff --name-status <S_preterminal> <S_plan>
git show --format= --name-status <S_plan>
```

Receipt interpreter는 `S_plan`의 parent가 exact `S_preterminal`, ancestry distance가 `1`, 두 tree 사이 delta가 이 계획 문서의 단일 addition인지 확인한다. 현재 user worktree의 다른 modified/untracked path는 허용된 사용자 pre-existing state로 inventory에만 기록하며, `S_plan` tree나 commit diff에 하나라도 포함되면 BLOCKED다. 이후 모든 comparison receipt는 `plan_subject=<S_plan>`을 provenance로 기록하되 `comparison_subject` 값으로는 허용하지 않는다.

공통 environment:

```powershell
Remove-Item Env:PYTHONPATH -ErrorAction SilentlyContinue
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:PYTHONPYCACHEPREFIX = '<external-work-root>\pycache'
```

Receipt interpreter는 각 command 직전에 `PYTHONPATH_present=false`를 확인한다. 모든 pytest invocation은 `-B -s`를 사용한다. Exact unittest runner에는 pytest의 `-s`를 임의 적용하지 않되 no `PYTHONPATH`, `-B`와 stdout/stderr 비캡처/receipt-interpreter 조건을 동일하게 검증한다. `same_environment_across_arms=true`와 `environment_matches_sealed_clean_checkout_contract=true`를 별도 필드로 기록한다.

각 execution command에는 다음 collection-only companion이 선행한다. Collection raw output은 external result root에 저장하고 receipt interpreter가 ordered node/source identity를 normalized JSON으로 만든다.

```powershell
# Focused logical route
uv run python -B -m pytest -s --collect-only -q -p no:cacheprovider --round3-contract=all <approved-affected-test-files>

# Exact-current logical route: exact runner의 collection-only equivalent
uv run python -B Iris/_docs/round3/round3_run_contract_tests.py --class current --enforce-current-build-closure --list

# Configured-current logical route
uv run python -B -m pytest -s --collect-only -q -p no:cacheprovider --round3-contract=current --round3-enforce-denominator --round3-denominator-receipt <external-result-root>\configured-current-collection.json

# Historical logical route; bootstrap failure도 receipt로 보존
uv run python -B -m pytest -s --collect-only -q -p no:cacheprovider --round3-contract=historical --round3-enforce-denominator --round3-denominator-receipt <external-result-root>\historical-collection.json

# Diagnostic/all composite logical route: 두 collection invocation 모두 필요
uv run python -B -m pytest -s --collect-only -q -p no:cacheprovider --round3-contract=diagnostic --round3-enforce-denominator --round3-denominator-receipt <external-result-root>\diagnostic-collection.json
uv run python -B -m pytest -s --collect-only -q -p no:cacheprovider --round3-contract=all --round3-enforce-denominator --round3-denominator-receipt <external-result-root>\all-collection.json
```

Focused collection receipt는 pytest stdout만 신뢰하지 않고 receipt interpreter가 explicit affected-source set, ordered node IDs, source files, parameter/subtest identity와 command hash를 결속해 생성한다.

1. Focused

```powershell
uv run python -B -m pytest -s -q -p no:cacheprovider --round3-contract=all <approved-affected-test-files>
```

2. Exact-current

```powershell
uv run python -B Iris/_docs/round3/round3_run_contract_tests.py --class current --enforce-current-build-closure --out <external-result-root>\exact-current.json
```

3. Configured-current

```powershell
uv run python -B -m pytest -s -q -p no:cacheprovider --round3-contract=current --round3-enforce-denominator --round3-denominator-receipt <external-result-root>\configured-current.json
```

4. Historical

```powershell
uv run python -B -m pytest -s -q -p no:cacheprovider --round3-contract=historical --round3-enforce-denominator --round3-denominator-receipt <external-result-root>\historical.json
```

5. Diagnostic/all

```powershell
uv run python -B -m pytest -s -q -p no:cacheprovider --round3-contract=diagnostic --round3-enforce-denominator --round3-denominator-receipt <external-result-root>\diagnostic.json
uv run python -B -m pytest -s -q -p no:cacheprovider --round3-contract=all --round3-enforce-denominator --round3-denominator-receipt <external-result-root>\all.json
```

6. Plan-local closure and terminal retrieval

```powershell
uv run python -B -m pytest -s -q -p no:cacheprovider Iris/validation/test_lightweighting/tests/test_validate_terminal_evidence_bundle.py
uv run python -B Iris/validation/test_lightweighting/validate_terminal_evidence_bundle.py --mode carrier-aware-v2 --pointer <tracked-pointer> --archive-root <owner-durable-root> --fresh-root <new-empty-external-root> --output <owner-durable-root>\terminal_evidence_retrieval_report.json
```

7. Terminal wrappers

```powershell
powershell -ExecutionPolicy Bypass -File .\Iris\validation\clean_checkout\invoke_receipt_bound_full_gate.ps1 <approved-arguments>
powershell -ExecutionPolicy Bypass -File .\Iris\validation\clean_checkout\invoke_deterministic_compare.ps1 <approved-arguments>
```

Arguments는 frozen command contract에서 materialize하고 임의 생략하지 않는다. Run A/B는 각각 새 checkout/work/result root를 사용한다.

Runtime Lua는 out of scope다. 승인된 scope expansion으로 Lua가 수정된다면 다음도 exit 0이어야 한다.

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\check_lua_syntax.ps1
```

### Manual Validation

* blocker attribution/counterfactual ledger 검토
* protected/required manifest authority 검토
* historical denominator/selection owner acceptance
* independent review와 owner seal
* durable custody와 fresh-root retrieval 위치 확인

기본 경로는 runtime behavior를 바꾸지 않으므로 PZ 인게임 UI 검증을 요구하지 않는다. Runtime/product source가 필요하면 scope expansion과 별도 PZ validation 없이 진행하지 않는다.

### Validation Limits

* PZ runtime 전체 correctness, multiplayer, long-session과 외부 mod sweep
* FPS, frame time, heap 또는 latency 개선
* package/release/Workshop/B42 readiness
* unrelated historical infrastructure의 일반적 건전성

---

## 8. Risk Surface Touch

### Authority Surface

높음. Required-validation, protected manifest, historical denominator, attribution acceptance, reviewer designation, terminal subject/seal과 evidence-only carrier를 다룬다. Hash mismatch는 adoption 근거가 아니며 owner의 additive successor decision 없이 reseal하지 않는다. `S_closeout_carrier`는 `S_terminal` authority를 대체하거나 새 validation subject가 되지 않는다.

### Runtime Behavior Surface

기본 범위에서는 없음. Runtime/product source 필요성이 드러나면 owner-reserved scope expansion으로 중단한다.

### Compatibility Surface

낮음~중간. Pytest bootstrap과 validation orchestration은 바뀔 수 있지만 Iris public/runtime API는 바꾸지 않는다. Historical option ownership 변경은 current/historical/diagnostic/all selection parity를 지켜야 한다.

### Sealed Artifact Surface

높음. Predecessor manifest/evidence, known-defect marker, successor accounting, terminal pointer/bundle/review/seal과 carrier DAG를 다룬다. Predecessor bytes는 보존하며 pointer chronology를 위해 code subject와 carrier subject를 분리한다.

### Public-Facing Output Surface

없음. 메뉴, 툴팁, localization, facts와 user behavior를 변경하지 않는다.

---

## 9. Risk Analysis

### Architecture Risk

* exact/configured/historical 책임을 합쳐 새 authority를 만들 수 있다.
* round-scoped validator를 permanent gate로 잘못 승격할 수 있다.
* blind reseal이 authority migration을 숨길 수 있다.
* `S_closeout_carrier`가 evidence-only 경계를 넘어 code/test/config successor로 오인될 수 있다.

Mitigation: route/authority manifest를 독립 유지하고 `gate_registered=false` lifecycle을 보존하며 source authorization/adoption obligation을 먼저 증명한다. Carrier allowed-delta manifest와 `carrier -> pointer -> bundle -> S_terminal` 검증을 요구한다.

### Runtime Risk

* validation producer/child가 source tree나 cache/staging을 변경할 수 있다.

Mitigation: external roots, inherited env, pre/post Git object comparison과 가능한 write denial을 사용한다.

### Compatibility Risk

* pytest option owner 이동이 invocation bootstrap을 바꿀 수 있다.
* mixed-item selection을 source-only로 단순화하면 denominator가 변할 수 있다.

Mitigation: 모든 route의 collection-only node identity를 비교하고 CLI semantics와 item override를 유지한다.

### Regression Risk

* false attribution, canonical environment 오염, A1/precision/fault 침식, diagnostic 신규 blocker, subject/evidence circularity, user worktree 오염과 dependency 재누락 위험이 있다.

Mitigation: `3×2×5` logical comparison과 36 execution receipts, no `PYTHONPATH`/`-B -s`, A0 fail-closed, remediation 후 live recensus, actual diagnostic/all, post-terminal subject change 0, carrier allowed-delta, user-worktree delta 0과 detection-scope-qualified root/edge/closure accounting을 요구한다.

---

## 10. Rollback Plan

Change 0 실패 또는 plan-only delta 위반 시 plan commit을 만들지 않고 `plan_authority_unmaterialized`로 BLOCKED 처리한다. 이미 잘못된 plan commit을 만들었다면 사용자 working tree를 reset/clean하지 않고 해당 commit을 execution authority에서 제외한 뒤 owner에게 새 plan-only subject 발급을 요청한다. `S_base`, `S_impl`, `S_preterminal`은 rollback 대상으로 삼지 않는다.

1. Comparison/attribution/accounting 단계는 아래 Change 1 plan-infrastructure 예외 외에는 committed source를 변경하지 않는다. 실패 시 disposable roots만 폐기하고 receipts는 보존한다.
2. Change 1 plan-infrastructure인 `CAP-CARRIER-RETRIEVAL-V2`와 `CAP-EXACT-CURRENT-COLLECTION`은 blocker ID 대신 `prerequisite_capability_id`를 갖는 서로 독립적인 commit/rollback unit이다. 실패 capability commit은 application remediation과 함께 revert하지 않고 해당 capability unit만 revert한 뒤 precondition을 unavailable/BLOCKED로 되돌린다. Rollback 뒤 predecessor mode/runner tests와 capability-negative preflight를 다시 실행한다.
3. Plan-infrastructure commit은 Change 3 validator universe recensus에 포함하고 plan-infrastructure validator/supporting-test 비용 축에 기록한다. A1 `test_support_LOC` denominator에는 산입하거나 상계하지 않는다.
4. Remediation은 causal class별 commit이다. 실패 class의 code/config/evidence successor를 함께 revert한다.
5. Focused output-root 실패 시 producer semantics를 바꾸지 않은 predecessor orchestration으로 복구하고 blocker를 재귀속한다.
6. Configured manifest transaction 실패 시 manifest, producer, adoption record와 tests를 같은 unit으로 되돌린다.
7. Historical 실패 시 option owner/plugin wiring, `R-defer -> R-full` transition과 denominator receipts를 함께 복구하며 ignore/deselect를 추가하지 않는다.
8. Accounting predecessor는 삭제하지 않고 잘못된 successor만 superseded 처리한다.
9. A1/precision/fault가 깨지면 candidate를 만들지 않고 offending remediation을 rollback한다.
10. 실패 candidate는 `terminal_candidate_rejected`로 보존하고 새 commit/tree를 발급한다.
11. Review 수정 요구 시 machine PASS를 새 tree에 상속하지 않고 qualification부터 반복한다.
12. Retrieval 실패가 bundle/pointer/carrier defect이면 `S_terminal`을 유지한 채 새 external bundle identity와 새 evidence-only carrier를 만들 수 있다. Source/code/test/config 또는 terminal evidence 의미가 바뀌면 새 candidate qualification부터 반복한다.
13. 최소 remediation이 invariant를 지킬 수 없을 때만 owner에게 full implementation revert를 제시한다. 자동 reset/clean/revert는 금지한다.
14. Rollback validation command가 exit 0이 아니면 완료를 주장하지 않는다.

---

## 11. Governance Constraints

* `docs/Philosophy.md`의 hub-and-spoke, Iris 역할, 근거 기반 중립성과 100% Lua runtime을 유지한다.
* Pulse는 Iris에 의존하지 않고 Iris는 다른 spoke에 직접 의존하지 않는다.
* current dirty worktree를 stash/reset/clean/overwrite/자동 commit하지 않는다.
* Change 0의 명시적 plan-only commit 외에는 계획 materialization 단계에서 어떤 파일도 stage/commit하지 않는다. 이미 stage된 unrelated path가 있으면 index를 변경하지 않고 BLOCKED 처리한다.
* `S_plan`은 predecessor/result authority가 아니다. `S_preterminal` identity, 세 comparison arm, 기존 FAIL/BLOCKED evidence 또는 baseline binding을 변경하지 않는다.
* committed object에서 파생한 external disposable checkout만 실행한다.
* user worktree는 read-only pre/post inventory와 hash로 `user_worktree_delta=0`을 증명하며 차이가 나도 자동 복원하지 않는다.
* 전체 user-worktree equality를 사용하는 동안 owner-controlled freeze가 필수다. Owner/user의 unrelated change로 delta가 발생하면 plan-induced mutation으로 단정하지 않지만 closeout은 false-BLOCKED 가능성을 수용하고 새 freeze/pre-image에서 재시도한다.
* predecessor FAIL/BLOCKED evidence는 immutable trace로 보존한다.
* comparison 전에는 blocker 원인을 단정하지 않고 `A0`를 terminal blocker로 둔다.
* 다섯 route는 서로 대체하지 않는다.
* skip/xfail/allowlist/deselect/ignore/denominator 축소로 gate를 우회하지 않는다.
* raw FAIL을 disposition으로 PASS로 바꾸지 않는다.
* hash mismatch만으로 protected/required manifest를 reseal하지 않는다.
* 실행 중 bytes가 바뀌었다 복원되는 것도 tracked mutation violation이다.
* A1, precision, fault matrix와 mandatory route semantics를 완화하지 않는다.
* dependency closure는 actual execution/import semantics를 사용한다.
* closure complete claim은 declared detection scope 안에서만 허용하고 unobserved dynamic dependency 가능성을 non-claim으로 남긴다.
* formal PASS는 exact relevant command exit 0에 결속하며 tool/input/authority 부재는 BLOCKED다.
* machine validation, independent review와 owner seal은 서로 대체되지 않는다.
* five-route Run A/B 전에는 `S_terminal`이 존재하지 않는다.
* terminal evidence는 external durable bundle, evidence-only `S_closeout_carrier`의 tracked pointer와 fresh-root retrieval로 검증한다.
* `S_terminal`의 post-validation change count는 0이어야 한다. Carrier의 exact evidence-only pointer/manifest delta만 별도 denominator로 허용한다.
* carrier가 code/test/config 또는 command/denominator semantics를 바꾸면 이전 PASS를 상속하지 않고 새 terminal candidate를 요구한다.
* final terminal outcome은 external bundle이 authority지만 canonical governance ledger의 pending entry를 영구 방치하지 않는다. `DECISIONS.md` additive supersession은 terminal subject/carrier 밖의 필수 후속 의무이며 terminal PASS를 새 subject에 상속하지 않는다.

---

## 12. Expected Closeout State

Expected closeout target: **complete**

실행 시작 상태는 계속 `blocked_before_terminal_validation`이다. `complete`는 다음이 모두 성립할 때만 허용한다.

```text
A0_unattributed = 0
owner_required_attribution_unaccepted = 0
owner_attribution_acceptance_hash_mismatch = 0
remediation_without_causal_binding = 0
closeout_precondition_unavailable_count = 0
plan_authority_materialized = true
S_plan = immutable plan-only commit/tree
S_plan_parent = S_preterminal
S_plan_ancestry_distance = 1
S_preterminal_to_S_plan_delta = exact plan document addition only
comparison_subjects = exact [S_base, S_impl, S_preterminal]
comparison_subjects_exclude_S_plan = true
terminal_retrieval_tool_mode_support = carrier-aware-v2
PYTHONPATH_present = false
environment_matches_sealed_clean_checkout_contract = true

logical_attribution_arm_route_count = 30
attribution_execution_invocation_receipt_count = 36
collection_only_receipt_count = frozen_contract_expected_count
R_full_unexplained_denominator_delta = 0
R_defer_remaining_at_terminal_entry = 0
R_first_missing_first_observation = 0

focused = PASS
tracked_write_violation_count = 0
exact_current = PASS
configured_current_failed = 0
configured_current_errors = 0
historical_bootstrap/inventory/denominator/validation = PASS
diagnostic_all_executed = true
diagnostic_all = PASS
Run_A = Run_B
post_checkout_clean = true

original_A1_baseline_relative_conditions = preserved
precision_regression = 0
fault_matrix_delta = 0
unresolved_dependency_within_declared_detection_scope = 0
unclassified_dependency_within_declared_detection_scope = 0
declared_accounting = computed_accounting
validator_dependency_closure_complete_within_declared_detection_scope = true
known_limit = unobserved_dynamic_dependency_possibility_not_disproven

S_terminal = immutable commit/tree
independent_review = PASS
owner_seal = valid
S_closeout_carrier != S_terminal
carrier_pointer_bundle_terminal_identity_chain = PASS
post_terminal_subject_change_count = 0
closeout_carrier_unapproved_change_count = 0
fresh_root_retrieval = PASS
fresh_root_validation_replay_subject = S_terminal
fresh_root_terminal_revalidation = PASS
user_worktree_delta = 0
```

State mapping:

| Condition | Closeout state |
|---|---|
| 모든 조건 충족 | `complete` |
| causal remediation 구현 후 terminal chain 미실행 | `implemented_only` |
| attribution/수정 일부 또는 재검증 잔존 | `partial` |
| plan authority 미동결, A0, 필수 authority/tool/input/reviewer/custody 또는 route failure 잔존 | `blocked` |

위 표의 `complete`는 terminal machine/governance bundle closeout 상태다. `DECISIONS.md` supersession 전에는 별도 ledger axis가 `pending_supersession_record`이며, 후속 docs-only subject가 성공해야 `governance_ledger_state=current`가 된다.

실패 candidate 또는 source/config 수정을 요구하는 review는 predecessor trace를 보존한 채 새 candidate를 요구한다. Retrieval failure가 external bundle/pointer/carrier packaging에만 국한되고 `S_terminal` bytes와 evidence meaning이 그대로임이 증명되면 새 bundle과 `S_closeout_carrier`만 발급할 수 있다. 기존 `blocked_before_terminal_validation` 기록은 성공 후에도 historical trace로 남는다.

최대 허용 claim:

```text
Iris 테스트 경량화의 terminal-closeout blocker를 동일 조건의 three-subject
comparison으로 귀속하고 causal minimum remediation을 적용했으며, 새 immutable
terminal subject에서 기존 A1 감축, precision과 fault contract를 보존한 채 focused,
exact-current, configured-current, historical 및 diagnostic/all Run A/B를 통과했다.
그 결과는 independent review, owner seal과 durable bundle의 fresh-root retrieval 및
revalidation에 결속됐고, evidence-only closeout carrier가 validated terminal subject와
분리된 identity chain으로 이를 운반한다.
```

이는 Iris 전체 runtime correctness, release/Workshop/B42 readiness, multiplayer/long-session 안정성, 정량 성능 향상 또는 unrelated validation infrastructure 전체의 건전성을 의미하지 않는다.
