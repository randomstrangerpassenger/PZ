# Implementation Plan

> 계획명: Iris 테스트 정밀도 보존형 테스트 수·구현 복잡도 경량화
> 기준일: 2026-08-12
> 입력 roadmap: `Iris 테스트 정밀도 보존형 테스트 수·구현 복잡도 경량화 — 종합 Roadmap`
> Revision: review cycle 3 후속 I11/I12/I13, M9/M10 및 branch-evidence/terminal-weight 권고 반영 successor
> Predecessor chain: SHA-256 `d7c922dbd7d91b447bf92e762869cdeac0195a1c780d8718043bd8ae259f9eb5` → `d0a93728f4c92a2abf4967b2ac1abedeab723b2dfddd19c67b6c96dc0b321416`
> Immediate predecessor plan identity: SHA-256 `6f6379a737bb577ddaa3123632b2846f8060a8141755fc9317d92b08c253535a`
> Review input identity: SHA-256 `ad8af755bba13c4e39ae9d58cba9188a16711da1b265f724254babbbec426758`
> Review addendum: 2026-08-12 direct feedback — CLD-TPL-I11/I12/I13, M9/M10 및 §4.1/§4.2
> 상위 기준: `Philosophy.md` → `DECISIONS.md` → `ARCHITECTURE.md` → `ROADMAP.md` → Iris validation authority → 본 계획
> Execution weight: Heavy — validation authority, required-validation identity 및 sealed evidence surface를 조건부로 다룸
> Runtime / production / public output 변경: 없음

## 1. Objective

Iris가 현재 보호하는 계약, input partition, production branch, fail-closed 경로, failure localization, validation route 및 authority binding을 잃지 않으면서 다음 두 축을 경량화한다.

1. `strong_dominance` 또는 `stronger_invariant`로 대체가 증명된 test node와 실제 중복 semantic scenario를 제거한다.
2. 테스트 의미와 identity를 바꾸지 않아도 줄일 수 있는 fixture, Git/subprocess, JSON/hash/path 및 repository orchestration 복잡도를 줄인다.

감축량은 분석 전에 quota로 정하지 않는다. 다만 본 successor plan은 roadmap 충돌 A를 **A1 — 실제 감축 필수**로 닫는다. 따라서 분석 lifecycle을 모두 수행했더라도 실제 node, 중복 executed scenario, test-support LOC, 대형 test file concentration 및 대형 test method concentration이 모두 감소하지 않으면 reduction problem은 완료되지 않는다. 완료 판정은 단순 pytest PASS가 아니라 고정된 before/after comparison domain에서 실제 감축과 다음 정밀도 조건을 모두 만족하는지로 판단한다.

```text
protected_contract_loss = 0
important_partition_loss = 0
required_branch_loss = 0
fail_closed_path_loss = 0
detection_regression = 0
failure_localization_regression = 0
authority_binding_unknown = 0
production_diff = 0
runtime_diff = 0
public_output_diff = 0
source_mutation = 0
unexpected_residue = 0
```

Roadmap의 초기 기대 기준선은 다음과 같다.

```text
environment_class         = planning_snapshot_unverified
configured total        = 991
configured current      = 487
historical              = 399
diagnostic              = 105
exact current authority = 219
test source files       = 276
test code LOC           ≈ 47,249
```

이 값은 roadmap 문제 정의에 기록된 planning snapshot이며 working overlay와 clean checkout 중 어느 environment class에서 얻었는지 검증되지 않았다. 따라서 실행 baseline이 아니다. Phase 0~1에서 exact tracked subject와 격리된 환경을 고정한 뒤 재수집한 값만 accepted baseline으로 사용한다.

Accepted baseline의 environment class는 다음 단일 값으로 고정한다.

```text
environment_class_of_accepted_baseline = clean_checkout_only
```

Working overlay에서 수집한 denominator는 진단값으로 별도 기록할 수 있지만 before/after precision comparison에 사용하지 않는다. Baseline에 포함할 ignored/untracked test가 있다면 먼저 owner-approved tracked source와 policy successor로 materialize한 뒤 새 clean-checkout baseline을 동결한다.

코드베이스 대조에서 확인한 현재 구조는 다음과 같다.

- `pytest.ini`의 configured discovery와 `Iris/_docs/round3/round3_run_contract_tests.py`의 exact Round 3 runner는 별도 경로다.
- `Iris/build/description/v2/tests/conftest.py`는 `current / historical / diagnostic / excluded` source policy, mixed item override, unknown/missing source fail-closed, denominator receipt를 소유한다.
- inspected `round3_test_taxonomy.json`의 exact taxonomy는 current `219` nodes / `45` sources, historical `285` / `157`, diagnostic `80` / `28`이다. 이는 configured denominator와 같은 숫자가 아니다.
- inspected `current_route_required_validations.json`은 required test identity `148`개와 required artifact `155`개를 별도로 결속한다.
- source policy는 Git-tracked policy source `115`개와 approval 당시 clean-checkout-absent policy source `183`개의 count/hash를 고정한다.
- 최근 owner closeout receipt의 configured-current 결과는 `486 passed + 1 not-applicable skipped = 487 selected`, exact current는 `219 passed`였다. 이 receipt는 실행 baseline으로 상속하지 않고 재수집의 기대값으로만 사용한다.
- `test_dvf_3_3_registry_authority_canonical_closure.py`는 `2,009 LOC / 30 tests`이나 exact-current taxonomy에는 3개만 있고 그 3개 모두 required-validation에 결속된다.
- `test_artifact_lifecycle_executor.py`는 `1,732 LOC / 2 tests`이며 2개 모두 exact-current 및 required-validation에 결속된다.
- 여러 test family에 `write_json`, `write_jsonl`, `load_jsonl`, `sha256`, Git invocation과 temporary repository setup이 반복된다. 단, 이 기계적 유사성 자체는 test 삭제 근거가 아니다.

---

## 2. Scope

본 계획은 Iris의 Python test/validation surface와 그 test-only support code를 대상으로 한다.

포함 범위:

- configured pytest와 exact Round 3 current route의 baseline·identity·denominator 재수집
- current / historical / diagnostic route와 exact-current / required-validation binding의 통합 inventory
- node → contract / branch / partition / failure / route / authority mapping
- regression provenance 및 intentional defense overlap inventory
- candidate별 mutation eligibility 또는 contract-equivalent fault-injection matrix
- failure-localization baseline과 before/after 비교
- domain-local test helper, minimal fixture 및 orchestration 단순화
- frozen 500+/1,000+ test-file 및 large-method metric의 실제 concentration 감소
- 증명된 중복 scenario/node의 작은 wave 단위 제거 또는 stronger invariant 대체
- identity가 바뀌는 경우 taxonomy, required-validation 및 predecessor→successor mapping 이관
- exact successor subject의 clean-checkout Run A / Run B, independent review와 owner seal
- terminal evidence placement decision, tracked pointer, owner custody/durability 및 fresh-root retrieval verification

실행 순서는 source identity를 유지하는 Type A를 우선한다.

```text
Type A: source-set 유지
  - test body 단순화
  - domain-local helper 추출
  - 같은 source 내부 scenario 제거
  - node identity 유지 또는 결속된 successor migration

Type B: source-set 변경
  - test file 삭제
  - test file 병합
  - source relocation
```

Type B는 Type A wave에 섞지 않으며 §6 Change 7의 별도 policy-migration gate가 열린 경우에만 수행한다.

### Explicitly Out Of Scope

- `Iris/media/lua/**` 또는 production Python tool의 동작·branch·fallback 변경
- Iris Browser, Wiki, Tooltip, Layer 3, Layer 4, package output 또는 public text 변경
- runtime semantic authority, source facts authority, rendered/runtime/package authority 변경
- 테스트 편의를 위한 production hook 또는 test-only production branch 추가
- current test를 historical/diagnostic으로 재분류하여 current count를 줄이는 작업
- `pytest.ini`의 ignore/deselect/collection 범위를 축소하여 숫자를 줄이는 작업
- historical/diagnostic test body 또는 sealed predecessor evidence 변경
- supported API / protected compatibility surface test 감축
- repository-wide universal test framework 또는 pytest 대체
- architecture 재설계, production 최적화, release/Workshop/B42/deployment 작업
- unrelated repository physical-size 또는 generated-data lightweighting

---

## 3. Non-Goals

- 특정 비율, 목표 node 수 또는 LOC quota를 달성하는 것
- parameterization, subtest 변환 또는 node naming만으로 실질 scenario 감소를 주장하는 것
- assertion 삭제·완화, snapshot/golden 확대 또는 mega-test 병합으로 failure condition을 숨기는 것
- current / historical / diagnostic route가 서로의 검증을 대체하게 만드는 것
- global branch coverage 100% 또는 repository 전체 exhaustive mutation testing
- candidate-local branch execution trace를 repository-wide mandatory branch-coverage infrastructure로 일반화하는 것
- round-scoped external terminal bundle/pointer 절차를 ecosystem 공용 architecture나 permanent validation layer로 승격하는 것
- 테스트 실행 시간, PZ FPS, latency, heap 또는 runtime 성능 개선을 주장하는 것
- 과거 historical failure나 raw diagnostic finding을 해결하거나 PASS로 다시 쓰는 것
- 기존 sealed receipt, review, failure 또는 predecessor artifact를 새 결과에 맞춰 수정하는 것
- 테스트 파일 본문을 별도 content-addressed archive로 복제 보존하는 것

---

## 4. Assumptions

### Authority and Repository Assumptions

- `Philosophy.md`의 Iris 경계가 최상위다. Iris는 100% Lua runtime 정보 모드이며 이번 계획은 runtime을 변경하지 않는다.
- configured discovery는 exact Round 3 current authority가 아니다. 어느 경로의 PASS도 다른 경로를 대체하지 않는다.
- `round3_test_taxonomy.json`, `current_route_required_validations.json`, `round3_pytest_source_classification.json`은 서로 다른 책임을 가지며 하나의 통합 manifest로 합치지 않는다.
- current working tree에는 사용자 변경과 generated/staging 변경이 함께 존재한다. 계획 작성 시점의 `HEAD` 또는 working overlay를 자동으로 baseline으로 채택하지 않는다.
- accepted baseline은 명시된 tracked commit/tree의 `clean_checkout_only` universe를 repository-external work/result root에서 재수집해야 한다. Working overlay는 accepted baseline이 될 수 없다.
- `denominator_working_overlay`와 `denominator_clean_checkout`을 모두 기록하되 `environment_class_of_accepted_baseline=clean_checkout_only`로 고정하고 상호 대체하지 않는다.
- 광범위한 recursive physical file census는 staging copy, ignored source 및 temporary residue를 포함해 denominator를 과대계상할 수 있다. source-policy와 exact taxonomy 기반 census를 canonical로 사용한다.
- 외부 mutation framework는 현재 repository dependency로 확인되지 않았다. 새 framework를 기본 전제로 두지 않고, applicable pure-Python target은 bounded mutant runner를 사용하며 external-contract target은 승인된 fault-injection matrix를 사용한다.
- 테스트 지원 코드를 helper로 옮긴 LOC도 `test_support_LOC`에 포함한다.

### Roadmap Conflict Locks

| ID | 채택 | 구현 계획상의 의미 | 코드베이스 근거 |
|---|---|---|---|
| A | A1 | `complete`에는 실제 node 감소, 실제 중복 executed scenario 제거, test-support LOC 감소, 500+·1,000+ LOC test file count 감소 및 frozen-definition large test method count 감소가 모두 필요하다. `measured_no_op`은 정상적인 분석 outcome이지만 reduction success가 아니며 top-level `partial`로 닫는다. | 실행 lifecycle 완료와 roadmap 문제 해결 완료를 분리하고 large-file/method concentration을 포함한 상위 success contract를 완화하지 않는다. |
| B | B1 | source mutation이 부적합한 Git/filesystem/subprocess/JSON 계약에는 고정된 contract-equivalent fault matrix를 mutation proof의 대체 증거로 허용한다. | 대형 lifecycle/registry tests가 temporary repository, Git, malformed manifest 및 subprocess failure를 주로 검증한다. |
| C | C1 | regression provenance는 필수 evidence 축이지만 절대 preserve filter는 아니다. 제거 시 provenance와 replacement contract/fault를 successor에 결속한다. | taxonomy reason, required-validation 및 historical trace가 이미 서로 다른 provenance/binding 역할을 가진다. |
| D | D2 | historical/diagnostic test code는 기본 no-change다. 별도 owner gate 없이는 mapping과 unchanged proof만 수행한다. | current taxonomy와 historical reproduction, diagnostic raw/disposition이 분리되어 있고 상호 대체가 금지돼 있다. |
| E | E2 | supported API와 protected compatibility surface test는 preserve-only다. 본 계획에서는 node/scenario 감축 후보로 열지 않는다. | Iris의 호환성 우선 원칙과 protected-surface manifest/acceptance route를 보존한다. |
| F | F2 | Type A를 먼저 소진한 뒤 별도 Type B policy-migration gate를 열어야 source 삭제·병합·이동을 수행한다. | `conftest.py`가 tracked policy source count/hash와 clean-checkout absence set을 fail-closed로 고정한다. |
| G | ChatGPT review schema + 별도 owner 축 | independent review는 `P0=P1=P2=P3=0`과 `Verdict=PASS`를 요구한다. 별도로 final owner seal을 exact successor subject/evidence bundle에 결속한다. | `REVIEW_TEMPLATE.md`의 canonical verdict가 PASS이고, review cycle 1이 machine/review/owner의 비대체성을 closure requirement로 제기했다. |
| H | 미채택 | 제거된 test body를 별도 CAS에 복제하지 않는다. Git predecessor identity와 migration/evidence ledger를 보존한다. | 별도 body archive는 Git history와 중복되고 새 storage/consumer 책임을 만든다. |

### Disposition Vocabulary

Candidate 상태는 다음 값으로만 정규화한다.

```text
eliminate_strongly_dominated
replace_with_stronger_invariant
simplify_identity_preserved
preserve_intentional_defense
split_for_failure_localization
defer_insufficient_evidence
no_op_no_material_gain
```

`reduction_outcome`은 closeout state가 아닌 plan-local 결과 속성이며 다음 세 값으로 닫는다.

```text
reduced
mixed_reduction
measured_no_op
```

`mixed_reduction`은 일부 scenario/LOC 또는 complexity 축이 감소했지만 split이나 concentration 잔존 등으로 A1의 모든 감축 조건을 만족하지 못한 경우다. `mixed_reduction`과 `measured_no_op`은 execution/analysis가 끝났더라도 top-level `complete`를 허용하지 않는다.

### Closure Axis Separation

다음 세 축은 서로 대체되지 않는다.

```text
machine_validation = PASS
independent_review = PASS
owner_seal = granted
```

Owner seal은 final terminal subject commit/tree, `machine_validation_manifest.json` SHA-256 및 independent-review identity를 함께 결속한다. 어느 한 축이라도 없으면 canonical `complete`로 닫지 않는다.

### Plan-Local Validator Lifecycle

Plan-local validator는 모두 exact round 재현을 위해 tracked 보존하지만, subject-specific producer/comparator를 future full-repository gate의 영구 dependency로 승격하지 않는다.

| Module | VCS state | Lifecycle role | Gate registered | Required closure |
|---|---|---|---:|---|
| `collect_test_inventory.py` | tracked | round_scoped_producer | false | current-round manifest + `test_universe.jsonl` identity |
| `build_protection_map.py` | tracked | round_scoped_producer | false | current-round manifest + protection/fault-universe identity |
| `build_detection_baseline.py` | tracked | round_scoped_producer | false | current-round manifest + frozen baseline identity |
| `compare_failure_localization.py` | tracked | round_scoped_comparator | false | current-round manifest + exact before/after subjects |
| `validate_dominance.py` | tracked | round_scoped_validator | false | current-round manifest + frozen candidate/fault domain |
| `validate_identity_migration.py` | tracked | round_scoped_validator | false | current-round manifest + exact migration transaction |
| `compare_precision.py` | tracked | round_scoped_comparator | false | current-round manifest + accepted baseline/successor identity |
| `validate_terminal_evidence_bundle.py` (`fresh-root-v1`) | tracked | round_scoped_validator | false | tracked pointer + durable archive + manifest/receipt chain; produces terminal retrieval Complete Gate values |
| `tests/test_validate_terminal_evidence_bundle.py` | tracked | round_scoped_validator_test | false | validator Git blob/mode identity + positive/missing/tampered bundle cases |

`validator_dependency_manifest.json`에는 8개 validator/comparator/producer root module, supporting test 1개 및 새 tracked transitive plan-local dependency의 path/hash, physical LOC, `lifecycle_role`, `gate_registered`, `post_closeout_disposition`, current-round command/dependency closure를 기록한다. Supporting test는 validator producer가 아니며 Complete Gate 값을 직접 생산하지 않는다. 다음 두 판정을 분리한다.

```text
terminal_round_validator_closure_complete
  = 이번 S_terminal에서 실행하는 tracked validator 8개 + supporting test 1개의 presence/hash/dependency 판정

validator_dependency_closure_complete
  = gate_registered=true인 reusable permanent dependency 집합만의 판정
```

현재 코드베이스의 `validate_iris_clean_checkout_validation.py`와 `run_iris_clean_checkout_validation.py`에는 terminal-evidence retrieval mode가 없다. 따라서 Phase 0에서 `Iris/validation/test_lightweighting/validate_terminal_evidence_bundle.py`의 `fresh-root-v1` capability와 positive/tamper tests를 먼저 구현·track한다. 이 capability는 다음 네 값을 생산하는 유일한 plan-local producer다.

```text
machine_validation_manifest_valid
external_bundle_retrieval_verified
terminal_bundle_hash_manifest_valid
closeout_receipt_valid
```

현재 8개 module과 supporting test는 모두 `gate_registered=false`이므로 `Iris/validation/clean_checkout/contracts/full_repository_gate.json`의 permanent dependency inventory를 변경하지 않는다. Phase 0은 clean checkout에서 8개 current-round module과 test 1개의 presence/hash를 fail-closed로 검사하되, permanent gate closure는 `gate_registered=true` 집합에 대해서만 계산하고 `gate_registered_validator_count=0`, `round_scoped_validator_test_count=1`을 명시한다. 향후 round-independent generic guard를 추출해 permanent gate에 채택하려면 별도 owner-approved transaction과 해당 gate의 tests가 필요하며 이번 계획이 자동 승인하지 않는다.

Post-closeout disposition은 이번 round에서 `retain_round_reproduction_evidence`로 고정한다. 이 파일들은 active/historical claim과 tracked pointer가 의존하는 동안 유지하되 permanent gate authority를 얻지 않는다. 이후 owner가 round 재현 책임을 대체하는 successor evidence와 removal impact를 승인한 경우에만 `future_round_removal_candidate`로 재분류할 수 있으며, 이번 계획의 PASS 또는 감축 수치가 제거를 요구하거나 미리 승인하지 않는다.

### Terminal Evidence Placement Contract

현재 코드베이스의 tracked closeout 선례는 `ARCHITECTURE.md` §8-13의 `fe4bb9f6 → b33ed2ac → 89f7499c → 91259769` successor chain이다. 이 방식은 implementation, endpoint-bound receipt, owner correction과 review seal을 서로 다른 tracked subject로 보존한다. 본 계획은 이를 검토했으나 Run A/B, review와 owner seal을 한 exact `S_terminal`에 결속하고 post-terminal tracked change의 PASS 상속을 금지한 현재 계약을 유지하기 위해 **repository-external durable bundle**을 채택한다.

이 절차의 무게는 exact test identity와 required-validation binding까지 바꿀 수 있는 Heavy governance 범위에 한정해 수용한다. 모든 producer/validator는 round-scoped이고 `gate_registered=false`이며 temporary execution root와 durable archive를 분리한다. 이 bundle/pointer 패턴의 repository-wide 일반화나 permanent architecture 채택은 별도 owner decision의 대상이고 이번 계획의 PASS 조건이 아니다.

Placement decision과 운영 계약은 `S_terminal` 전에 repository owner가 ratify하고 다음 값으로 고정한다.

```text
terminal_evidence_placement = external_bundle
terminal_evidence_placement_decision_owner = repository_owner
external_bundle_custody = repository_owner
external_bundle_durability = append_only_owner_managed_file_store
external_bundle_retrieval = tracked_pointer_plus_closure_id_and_allocator_receipt
tracked_pointer_artifact = Iris/_docs/refactor/test_precision_lightweighting/terminal_evidence_pointer.json
```

Tracked pointer는 pre-terminal evidence이며 다음을 포함한다.

- stable `closure_id`, pointer schema와 Git blob identity
- `subject_binding_mode=commit_and_tree_containing_pointer`
- owner-ratified storage profile, custodian role과 opaque allocator receipt identity
- machine-specific absolute path를 저장하지 않는 external retrieval key
- expected terminal filenames, schema versions와 SHA-256 verification rule
- append-only/no-overwrite rule, retention owner와 deletion prohibition
- external archive root가 temporary Run A/B work/result root와 분리돼야 한다는 constraint

External durable bundle은 existing `Iris/validation/clean_checkout/contracts/repository_evidence_lightweighting_output_policy.json`의 owner-managed external file-store 및 opaque allocator 원칙과 정렬하되 그 policy를 이 round의 새 authority로 확대하지 않는다. Bundle은 tracked pointer가 current 또는 historical claim을 지지하는 동안 삭제할 수 없고, supersede 시에도 §7-5 historical trace를 보존하는 approved successor pointer 없이는 폐기할 수 없다.

Terminal evidence DAG는 다음 순서와 identity로 고정한다.

```text
terminal_validation_attestation.json
  → machine_validation_manifest.json
  → independent_review.json
  → owner_seal.json
  → terminal_bundle_hash_manifest.json
  → closeout_receipt.json
  → terminal_evidence_retrieval_report.json
```

`machine_validation_manifest.json`은 owner seal보다 먼저 생성되는 정식 intermediate artifact다. 최소 `closure_id`, exact `S_terminal` commit/tree, tracked pointer Git blob ID, `terminal_validation_attestation.json` SHA-256과 Run A/B·route·no-mutation 등 constituent machine-evidence path/hash를 가진다. Independent review는 이 manifest를 review subject로 소비하고, owner seal은 exact `S_terminal`, machine manifest SHA-256과 independent-review SHA-256을 참조한다.

`terminal_bundle_hash_manifest.json`은 자기 자신과 그 뒤에 생성되는 closeout receipt/retrieval report를 제외하고 `closure_id`, exact `S_terminal` commit/tree, pointer Git blob ID, allocator receipt hash, machine manifest, independent review와 owner seal SHA-256을 결속한다. `closeout_receipt.json`은 이 final manifest SHA-256과 동일 subject/pointer tuple을 참조한다. `validate_terminal_evidence_bundle.py@fresh-root-v1`은 repository와 분리된 fresh root에서 pointer 기반 재조회·hash/schema/DAG 검증 후 `terminal_evidence_retrieval_report.json`을 append-only 기록하고 다음을 생산한다.

```text
external_bundle_custody_bound = true
external_bundle_durability_contract_bound = true
machine_validation_manifest_valid = true
external_bundle_retrieval_verified = true
terminal_bundle_hash_manifest_valid = true
closeout_receipt_valid = true
```

Retrieval이 실패하면 이미 생성된 closeout receipt는 canonical closeout이 아니라 failed-attempt trace로 append-only 보존한다. 같은 receipt를 수정하지 않고 새 `closure_id`, tracked pointer, allocator receipt와 terminal subject를 발급해 terminal 절차를 다시 수행한다. Ratification, durable archive 또는 retrieval capability/path가 없으면 external bundle을 임시 디렉터리 evidence로 대체하지 않고 closeout을 `blocked`로 낮춘다.

### Environment Assumptions

- Windows PowerShell을 사용한다.
- Python command는 `uv run python ...` 형식을 사용한다.
- 모든 pytest collection과 validation은 `-B -p no:cacheprovider`를 무조건 사용하고 receipt/output은 repository-external absolute path로 보낸다.
- parent와 child Python process 모두 `PYTHONDONTWRITEBYTECODE=1`을 상속한다. bytecode cache가 필요한 tool은 `PYTHONPYCACHEPREFIX`를 repository-external work root로 지정한다.
- required tool 또는 exact environment가 없으면 해당 validation axis는 PASS가 아니라 BLOCKED다.

---

## 5. Repository Areas Affected

### Code

- `Iris/build/description/v2/tests/conftest.py` — configured source routing, denominator enforcement 및 receipt 경계
- `Iris/_docs/round3/round3_run_contract_tests.py` — exact-current selection, required-validation consumption 및 build-closure 경계
- `Iris/validation/clean_checkout/` — repository-external 실행, Run A/B, deterministic compare 및 no-mutation 검증 재사용
- `Iris/validation/test_lightweighting/` — 신규 plan-local inventory, mapping, dominance, fault/mutant, migration 및 comparison tooling
- `Iris/validation/test_lightweighting/validate_terminal_evidence_bundle.py` — 신규 `fresh-root-v1` pointer/archive/DAG retrieval validator
- `Iris/validation/test_lightweighting/tests/test_validate_terminal_evidence_bundle.py` — retrieval positive 및 missing/tampered identity fail-closed tests
- `Iris/build/description/v2/tests/*.py` — 분석된 current Type A candidate와 승인된 Type B successor
- `Iris/build/tests/test_evidence_pipeline_cross_track.py` — configured current denominator의 별도 root test surface
- `Iris/build/description/v2/tests/test_dvf_3_3_registry_authority_canonical_closure.py` — 2,009 LOC / 30-node complexity pilot candidate; exact-current 3개는 required-bound preserve baseline
- `Iris/build/description/v2/tests/test_artifact_lifecycle_executor.py` — 1,732 LOC / 2-node orchestration pilot candidate; 두 node 모두 required-bound preserve baseline
- `Iris/build/description/v2/tests/test_compose_layer3_text_v2.py`
- `Iris/build/description/v2/tests/test_compose_layer3_text_overlay.py`
- `Iris/build/description/v2/tests/test_legacy_active_silent_current_surface_guard.py`
- contract-family local support module — 실제 pilot 분석 후 이름과 위치를 정하며 범용 `test_utils.py`는 만들지 않음

### Docs

- `docs/iris_test_precision_preserving_test_suite_lightweighting_plan.md`
- `docs/DECISIONS.md` — owner가 Type B 또는 evidence-placement policy decision을 채택한 경우 `S_terminal` 전에만 additive sync
- `docs/ARCHITECTURE.md` — validation architecture가 실제로 바뀐 경우 `S_terminal` 전에 pending subject/pointer와 claim boundary만 sync
- `docs/ROADMAP.md` — `S_terminal` 전에 `pending_terminal_validation`, stable `closure_id`와 tracked pointer identity만 sync; final PASS/complete를 미리 기록하지 않음
- `Iris/_docs/refactor/test_precision_lightweighting/` — tracked baseline, contract map, disposition, migration, comparison 및 terminal evidence pointer

이 계획은 **top-doc pending option**을 채택한다. Run A/B 이후 final outcome은 external terminal bundle만 소유하며, 같은 execution에서 top-doc에 post-closeout final state를 다시 쓰지 않는다. `pending_terminal_validation`은 informational gate marker이지 `EXECUTION_CONTRACT.md`의 새 closeout state가 아니다. External closeout receipt는 기존 `complete / partial / implemented_only / blocked` 중 하나만 사용한다. 따라서 `docs/ROADMAP.md`만 읽는 downstream consumer는 pending을 final outcome으로 추론하면 안 되며, stable `closure_id`와 tracked pointer를 따라 external terminal bundle의 closeout receipt를 조회해야 actual terminal state를 알 수 있다. 이는 의도된 tracked-document limitation/non-claim이다. Post-terminal top-doc sync가 별도로 승인되면 documentation-only successor라 하더라도 새 `S_next`이며 terminal Run A/B, review와 owner seal을 새 subject에서 다시 수행한다.

### Config

- `pytest.ini` — read-only baseline이 기본값. 수집 축소에 사용하지 않으며 Type B에서도 필요성이 별도 증명된 경우만 변경
- `Iris/_docs/round3/round3_pytest_source_classification.json` — Phase 0 실측에서 신규 plan-local test가 configured discovery에 수집될 때 owner-approved additive source registration을 먼저 수행하거나, Type B가 승인된 경우 source-set identity를 atomic하게 이관; 두 transaction을 혼합하지 않음
- `Iris/_docs/round3/round3_full_discovery_denominator.json` — denominator contract reconciliation
- `Iris/_docs/round3/round3_test_taxonomy.json` — exact item identity migration이 있는 경우 successor mapping과 함께 변경
- `Iris/_docs/round3/current_route_required_validations.json` — required-bound identity가 바뀌는 경우 같은 transaction에서 변경
- `Iris/validation/clean_checkout/contracts/full_repository_gate.json` — 이번 8개 round-scoped validator와 supporting test에 대해서는 read-only; `gate_registered=false`이므로 permanent dependency registration 없음

### Generated Artifacts

Terminal candidate freeze 전에 확정할 tracked canonical evidence의 기본 위치:

```text
Iris/_docs/refactor/test_precision_lightweighting/
  baseline_manifest.json
  execution_isolation_receipt.json
  source_role_inventory.json
  test_universe.jsonl
  protection_map.jsonl
  regression_provenance.jsonl
  scenario_inventory.jsonl
  complexity_baseline.json
  a1_feasibility_preassessment.json
  validator_dependency_manifest.json
  terminal_evidence_placement_decision.json
  terminal_evidence_pointer.json
  fault_matrix.jsonl
  fault_matrix_freeze.json
  detection_baseline.json
  dominance_ledger.jsonl
  candidate_dispositions.jsonl
  pilot_receipt.json
  identity_migration.jsonl
  cumulative_comparison.json
  validation_matrix.preterminal.json
  closeout_candidate.md
```

Terminal candidate commit/tree를 freeze한 뒤 생성되는 다음 artifact는 owner-ratified repository-external durable archive의 immutable attestation bundle에 둔다. Temporary work/result root와 durable archive root는 서로 달라야 한다.

```text
terminal_validation_attestation.json
machine_validation_manifest.json
independent_review.json
owner_seal.json
terminal_bundle_hash_manifest.json
closeout_receipt.json
terminal_evidence_retrieval_report.json
```

Raw logs, temporary repositories, mutated copies, coverage/mutant/fault work products 및 Run A/B intermediate output은 repository-external temporary work/result root에 둔다. 이 temporary root는 durable terminal bundle의 custody/durability를 만족하지 않으며 closeout 후 정리할 수 있다. Terminal attestation을 tracked tree에 복사하거나 top-level docs를 추가 변경하면 새로운 exact subject가 되므로 terminal Run A/B, review와 owner seal을 그 subject에서 다시 수행한다.

기존 historical, diagnostic, predecessor, review 및 sealed evidence는 rewrite하지 않는다.

---

## 6. Planned Changes

### Change 1 — Phase 0: Validation execution isolation과 exact subject freeze

Purpose:

Baseline과 before/after 비교가 test producer의 tracked source mutation, cache, temp directory 또는 generated residue에 오염되지 않게 한다.

Files:

- `Iris/validation/clean_checkout/**`
- `Iris/validation/test_lightweighting/**`
- `Iris/validation/test_lightweighting/validate_terminal_evidence_bundle.py`
- `Iris/validation/test_lightweighting/tests/test_validate_terminal_evidence_bundle.py`
- `Iris/build/description/v2/tests/conftest.py` — configured discovery 실측이 `true`인데 현 controlled-source registration surface가 신규 path를 포괄하지 못할 때만 additive registration 지원
- `Iris/_docs/round3/round3_pytest_source_classification.json` — configured discovery 실측이 `true`일 때만 additive source-registration transaction
- `Iris/_docs/round3/round3_full_discovery_denominator.json` — 위 registration으로 denominator identity가 바뀔 때만 같은 transaction에서 reconciliation
- `Iris/_docs/refactor/test_precision_lightweighting/execution_isolation_receipt.json`
- `Iris/_docs/refactor/test_precision_lightweighting/baseline_manifest.json`

Implementation Notes:

- Phase 0 순서는 다음과 같이 고정한다. 이 순서를 완료하기 전에는 accepted baseline을 동결하지 않는다.

```text
1. plan-local validator 8개와 supporting test 1개를 구현·track
2. 신규 test path를 명시적으로 넘기지 않은 configured collection으로 기본 수집 여부 실측
3. source-policy classification 및 test-support universe membership 확정
4. 수집되는 경우 owner-approved additive source-registration과 bound denominator reconciliation
5. standalone explicit-path test와 configured/exact collection을 모두 재실행
6. 위 registration decision을 포함한 exact clean-checkout subject에서 accepted baseline 동결
```

- 작성 시점의 `pytest.ini.testpaths`는 `Iris/build/description/v2/tests`와 `Iris/build/tests/test_evidence_pipeline_cross_track.py`만 가리키므로 신규 validation test의 configured discovery 결과는 `false`로 예상된다. 또한 current source policy는 tracked source count `115`를 봉인하고 `conftest.py`의 tracked enumeration은 `Iris/build/description/v2/tests`와 `Iris/build/tests`로 한정된다. 그러나 이 정적 관측은 실행 판정을 대체하지 않으며, 신규 파일을 track한 뒤 default configured collection을 실제로 한 번 실행한 값만 canonical이다. §7-6의 explicit-path pytest command는 기본 configured discovery 수집 여부의 증거로 사용하지 않는다.
- 실측이 `true`이면 `round3_pytest_source_classification.json`의 included classification(`current | historical | diagnostic`) 중 authority role에 맞는 값을 owner가 승인하고 controlled-source registration logic, source-set count/hash 및 `round3_full_discovery_denominator.json`을 같은 additive transaction에서 갱신한다. JSON row만 추가해 현 enumeration 경계 밖 tracked file을 clean-checkout-absent로 오인하게 해서는 안 되며 count를 기계적으로 `116`으로 가정하지 않고 실제 registered set에서 재계산한다. 이는 source 삭제·병합·relocation을 다루는 Type B와 별개이며 exact taxonomy/current required-validation authority를 자동 변경하지 않는다. 실측이 `false`이면 classification은 `not_applicable`로 기록하고 supporting test를 standalone explicit-path current-round closure로만 유지한다.
- 신규 supporting test는 configured discovery 결과와 무관하게 plan-local mandatory test source이므로 frozen `test_support_file_universe`에 포함한다. Configured node denominator에는 실측상 수집된 경우에만 포함하고, 그 여부를 baseline/final에 동일 적용한다.
- `execution_isolation_receipt.json`에는 observation command/exit/path set과 `new_test_source_collected_by_configured_discovery`를, `baseline_manifest.json`에는 classification 또는 `not_applicable`, policy/denominator blob identity, test-support membership과 `baseline_frozen_after_plan_local_source_registration`을 기록한다.
- `baseline_frozen_after_plan_local_source_registration=true`는 registration-decision 단계 뒤에 baseline을 동결했다는 순서 증명이다. `false` discovery 분기에서는 policy mutation을 뜻하지 않고 `not_applicable` 결정을 먼저 봉인했다는 의미다.
- owner가 승인한 exact tracked commit/tree를 기록한다. dirty working tree 또는 optional overlay를 accepted baseline에 포함하지 않는다.
- existing clean-checkout runner와 repository-external root 검증을 우선 재사용한다.
- `environment_class_of_accepted_baseline=clean_checkout_only`를 고정하고 `denominator_working_overlay`와 `denominator_clean_checkout`을 별도 field로 기록한다.
- plan-local validator path가 실제로 존재하고 Git-tracked이며 clean checkout에도 materialize되는지 검사한다. Validator별 hash, `lifecycle_role`, `gate_registered`와 current-round command/dependency edge를 `validator_dependency_manifest.json`에 결속한다.
- 코드베이스 preflight에서 existing clean-checkout CLI에 retrieval mode가 없음을 기록하고, candidate/refactor rollout 전에 신규 `validate_terminal_evidence_bundle.py@fresh-root-v1`을 구현한다. 단순 path 존재가 아니라 CLI mode identity, pointer/archive input contract, 네 output field와 positive/tamper test PASS를 확인한다.
- external evidence placement owner ratification과 tracked pointer contract를 확정한다. Durable archive allocation/custody/retrieval 계약이 없으면 baseline 이후 구현 phase를 열지 않는다.
- 계획에 열거된 docs/round3/clean-checkout path가 exact baseline subject에 존재하는지 execution-time path identity preflight를 수행한다.
- configured collection과 exact runner를 success path 및 대표 failure-injection path에서 실행해 실행 전후 Git status, tracked content hash와 residue를 비교한다.
- Run A / Run B collection에서 node identity, source set, denominator와 canonical receipt bytes가 결정적인지 확인한다.
- 현재 physical tree에서 관측되는 `__pycache__`, `tmp*`, `_tmp*` 같은 항목은 자동 삭제하지 않고 residue inventory로만 기록한다.
- execution producer가 source tree를 갱신하면 baseline을 채택하지 않는다. 먼저 output isolation을 고치거나 disposable-checkout-only 실행으로 범위를 제한한다.

Validation:

```text
successful_execution_source_mutation = 0
failure_execution_source_mutation = 0
unexpected_residue = 0
Run_A_node_set == Run_B_node_set
Run_A_source_set == Run_B_source_set
Run_A_denominator == Run_B_denominator
environment_class_of_accepted_baseline = clean_checkout_only
before_after_environment_class_match = true
plan_local_validator_present_in_clean_checkout = true
terminal_round_validator_closure_complete = true
validator_dependency_closure_complete = true
gate_registered_validator_count = 0
round_scoped_validator_test_count = 1
new_test_source_collected_by_configured_discovery = true | false
new_test_source_policy_classification = current | historical | diagnostic | not_applicable
new_test_source_registration_branch_consistent = true
new_test_source_in_test_support_file_universe = true
baseline_frozen_after_plan_local_source_registration = true
terminal_evidence_placement_decision_ratified = true
tracked_terminal_evidence_pointer_valid = true
terminal_evidence_retrieval_capability_present = true
terminal_evidence_retrieval_capability_identity = Iris/validation/test_lightweighting/validate_terminal_evidence_bundle.py@<git_blob>:fresh-root-v1
terminal_evidence_retrieval_capability_tests = PASS
required_repository_paths_present = true
```

Exit Gate:

- exact subject identity와 repository-external output 경계가 명시됨
- accepted baseline environment class와 clean-checkout denominator가 명시됨
- round-scoped validator tracking/presence/current-round closure와 `gate_registered` 집합의 permanent closure가 분리됨
- 신규 plan-local test의 configured-discovery 실측, conditional additive classification, test-support membership이 확정되고 그 뒤 baseline이 동결됨
- terminal retrieval capability의 tracked module/mode/output identity와 positive/tamper tests가 `S_terminal` 전에 확보됨
- external durable bundle의 owner custody, tracked pointer 및 retrieval contract가 확정됨
- source mutation/residue가 0인 반복 가능한 measurement path가 확보됨
- 그렇지 않으면 Change 2 이후 candidate/refactor rollout은 BLOCKED

---

### Change 2 — Phase 1~2: Denominator census와 test protection mapping

Purpose:

각 test node가 사라질 때 잃는 보호 책임을 조회 가능하게 만들고, node 수와 실제 scenario 수를 분리한다.

Files:

- `Iris/validation/test_lightweighting/collect_test_inventory.py`
- `Iris/validation/test_lightweighting/build_protection_map.py`
- `Iris/_docs/refactor/test_precision_lightweighting/test_universe.jsonl`
- `Iris/_docs/refactor/test_precision_lightweighting/protection_map.jsonl`
- `Iris/_docs/refactor/test_precision_lightweighting/scenario_inventory.jsonl`
- `Iris/_docs/refactor/test_precision_lightweighting/complexity_baseline.json`
- `Iris/_docs/refactor/test_precision_lightweighting/a1_feasibility_preassessment.json`

Implementation Notes:

- configured pytest node ID와 exact unittest-style `test_id`를 별도 field로 보존하고 canonical crosswalk를 만든다.
- 최소 다음 denominator를 독립적으로 기록한다.

```text
pytest_node_id_count
semantic_scenario_count
executed_case_count
input_row_count
protected_contract_count
protected_branch_count
test_source_count
test_source_LOC
test_support_LOC
plan_local_validator_LOC
plan_local_validator_file_count
files_ge_500_count
files_ge_1000_count
large_test_method_LOC_threshold
large_test_method_count
max_test_method_LOC
fixture_setup_LOC
large_source_route_distribution
type_a_addressable_large_source_LOC
```

`protected_contract_count`와 `protected_branch_count`는 감축 target이 아니라 보존해야 할 precision denominator다. 이 값의 감소는 어떤 LOC/node 감소로도 상쇄할 수 없다. `plan_local_validator_LOC`와 `plan_local_validator_file_count`는 lifecycle 표의 8개 root module, supporting test 1개와 새 tracked transitive plan-local dependency를 포함하는 보고 전용 governance cost이며 감축 축이 아니고 `test_support_LOC` 또는 node 감소를 상쇄하지 않는다.

Large-complexity metric은 candidate discovery 전에 `complexity_baseline.json`에 deterministic하게 freeze한다.

- `test_support_file_universe` selection rule은 configured test source, 이번 round가 explicit-path로 반드시 실행하는 plan-local test source와 test-only helper/fixture module을 canonical repo-relative POSIX path로 선택하도록 freeze한다. 따라서 `tests/test_validate_terminal_evidence_bundle.py`는 configured discovery 실측값과 무관하게 포함한다. Baseline member list/hash는 baseline identity와 reconciliation에만 사용하며 after count를 baseline member로 제한하지 않는다.
- 별도 `plan_local_validator_file_universe`는 lifecycle 표의 tracked root module/test와 그 신규 tracked transitive dependency를 선택한다. Supporting test처럼 두 universe에 속하는 파일은 overlap path/LOC를 기록하되 두 지표를 합산해 repository-wide LOC delta로 오해하지 않는다.
- after universe는 frozen selection rule을 final tracked tree에 다시 적용해 재구성한다. 새로 생성·이름 변경·이동된 helper/fixture도 rule에 해당하면 반드시 포함하며 final eligible path ↔ after inventory를 양방향 reconciliation한다.
- file LOC는 accepted baseline에서 확정한 UTF-8 physical-line counting rule과 EOL normalization rule을 before/after에 동일 적용한다.
- roadmap이 이미 사용한 `>=500 LOC`, `>=1,000 LOC` bucket을 그대로 사용하고 두 count를 각각 freeze한다. `large_test_file_count`라는 중복 alias는 사용하지 않는다.
- large method는 Python AST의 function/method source span(`lineno..end_lineno`)으로 측정한다. Numeric threshold는 기존 canonical metric definition이 있으면 그 identity를 사용하고, 없으면 candidate 결과를 보기 전에 repository owner가 하나의 rule을 ratify한다. Ratification 없이는 Phase 2를 닫지 않는다.
- `large_method_metric_definition`, threshold, parser/runtime identity와 baseline member list/hash를 freeze하며 after에서 threshold나 member-selection rule을 바꾸지 않는다.

- 각 node는 최소 다음 vector를 가진다.

```text
source_file
pytest_node_id
exact_test_id
route
authority_role
contract_owner
contract_ids
production_targets
branch_conditions
input_partitions
interaction_states
failure_conditions
fail_closed_paths
oracle
environment_boundary
required_validation_bindings
regression_provenance
```

- exact-current, required-bound, 500+ LOC source, 1,000+ LOC source, Git/subprocess-heavy fixture 및 multi-failure-condition node를 우선 수동 검토한다.
- 500+ LOC source 전체를 current/historical/diagnostic/protected-only로 분류하고 `large_source_route_distribution`과 Type A가 실제로 다룰 수 있는 `type_a_addressable_large_source_LOC`를 산출한다.
- Change 3 전에 `large_source_route_distribution_reported_to_owner=true`, `type_a_addressable_large_source_LOC` 및 `a1_feasibility_preassessment`를 owner에게 보고한다. Preassessment는 `projected_files_ge_1000_delta`, `projected_files_ge_500_delta`, `required_genuine_dedup_LOC_for_joint_satisfaction`와 node/scenario/support-LOC/500+/1,000+/large-method별 `per_axis_feasibility`를 포함한다. Type A addressable surface가 부족하고 Type B gate도 닫혀 있으면 이를 조기에 `complete_feasibility=low`로 기록하되 threshold나 preservation rule을 완화하지 않는다.
- `test_dvf_3_3_registry_authority_canonical_closure.py`의 30 configured nodes와 3 exact-required nodes를 섞어 회계하지 않는다.
- `test_artifact_lifecycle_executor.py`의 2개 giant node는 node 감소 후보가 아니라 multi-responsibility/failure-localization inventory로 먼저 분류한다.
- repeated JSON/Git/hash helper는 mechanics inventory로 표시하되 semantic duplicate로 자동 분류하지 않는다.

Validation:

- configured source inventory ↔ source policy 양방향 일치
- exact node inventory ↔ taxonomy/required manifest 일치
- `unmapped_exact_current = 0`
- `unmapped_required_binding = 0`
- `unknown_route = 0`
- helper로 이동한 LOC를 포함한 test-support LOC reconciliation
- `plan_local_validator_LOC`와 `plan_local_validator_file_count` before/final 보고 및 lifecycle inventory reconciliation
- `large_file_metric_definition_frozen=true`
- `large_method_metric_definition_frozen=true`
- `files_ge_500_count`, `files_ge_1000_count`, `large_test_method_count` member/hash reconciliation
- frozen selection rule을 final tree에 재적용한 `after_universe_reconciled=true`; 신규 helper/fixture omission `0`
- `large_source_route_distribution_reported_to_owner=true`
- per-axis 및 joint-bucket `a1_feasibility_preassessment` recorded before Change 3

---

### Change 3 — Phase 3: Precision baseline, detection evidence와 dominance census

Purpose:

코드 유사성이 아니라 보호 책임과 fault detection을 기준으로 제거 가능한 중복과 intentional defense overlap을 구분한다.

Files:

- `Iris/validation/test_lightweighting/build_detection_baseline.py`
- `Iris/validation/test_lightweighting/compare_failure_localization.py`
- `Iris/validation/test_lightweighting/validate_dominance.py`
- `Iris/_docs/refactor/test_precision_lightweighting/fault_matrix.jsonl`
- `Iris/_docs/refactor/test_precision_lightweighting/fault_matrix_freeze.json`
- `Iris/_docs/refactor/test_precision_lightweighting/detection_baseline.json`
- `Iris/_docs/refactor/test_precision_lightweighting/dominance_ledger.jsonl`
- `Iris/_docs/refactor/test_precision_lightweighting/candidate_dispositions.jsonl`

Implementation Notes:

- protection map을 먼저 확정하고 모든 `failure_conditions`와 `fail_closed_paths`에서 mutation/fault universe를 전사적으로 생성한다.
- candidate disposition을 하나라도 만들기 전에 `fault_matrix.jsonl`을 freeze한다. Freeze receipt는 exact baseline commit/tree, protection-map SHA-256, matrix SHA-256, row count와 시간을 기록한다.

```text
protection_map_failure_conditions_not_in_matrix = 0
protection_map_fail_closed_paths_not_in_matrix = 0
fault_matrix_frozen_at = <timestamp>
fault_matrix_sha256 = <sha256>
first_disposition_created_at = <timestamp>
freeze_precedes_disposition = true
```

- matrix freeze 이후 code/text similarity로 candidate를 발견한다. Similarity는 discovery에만 사용하며 기존 survivor 결과를 보고 matrix row/operator를 선택하지 않는다.
- removal 후보 `A`는 survivor set `S`에 대해 다음 subset 관계를 모두 만족해야 한다.

```text
Contracts(A)   ⊆ Contracts(S)
Partitions(A)  ⊆ Partitions(S)
Branches(A)    ⊆ Branches(S)
FailClosed(A)  ⊆ FailClosed(S)
Interactions(A) ⊆ Interactions(S)
```

- 각 candidate는 `branch_execution_evidence = static_proof | targeted_coverage | equivalent_trace | not_material`을 기록한다. Dominance가 특정 production branch의 실제 실행 여부에 materially 의존하면 해당 `production_targets`에만 coverage instrumentation 또는 동등한 execution trace를 적용하고 exact subject, tool/command identity, branch ID, before/after hit set과 trace hash를 `dominance_ledger.jsonl`에 결속한다.
- Targeted instrumentation은 repository-external result root 또는 disposable checkout에서 수행하고 accepted successor에 production instrumentation diff를 남기지 않는다. 이는 candidate-local evidence 강화이며 repository 전체 branch-coverage infrastructure, 새 permanent gate 또는 모든 candidate의 mandatory coverage layer를 만들지 않는다.
- materially branch-dependent candidate가 targeted execution evidence를 확보하지 못하면 subset을 추정하지 않고 `defer_insufficient_evidence` 또는 `preserve_intentional_defense`로 닫는다.
- pure-Python production target에서 safe bounded mutation이 가능하면 동일 revision, target, operator, mutant universe를 고정한다.
- Git/filesystem/subprocess/malformed JSON 등 source mutation이 부적합한 계약은 fault ID, injection point, expected failing contract, expected failure signature를 고정한 contract-equivalent matrix를 사용한다.
- before/after에서 mutation/fault denominator를 바꾸지 않는다. 새로운 failure condition/operator가 발견되면 기존 freeze를 폐기하고 deletion 전 상태에서 protection map과 matrix를 다시 freeze한다. 이미 변경된 successor 결과를 새 baseline으로 사용하지 않는다.
- representative fault가 어느 contract/node에 귀속되는지 비교해 failure localization 악화를 측정한다.
- regression provenance가 있는 후보는 provenance ID와 재현 fault/contract가 successor에 연결되지 않으면 `defer_insufficient_evidence` 또는 `preserve_intentional_defense`다.
- supported/protected compatibility node와 historical/diagnostic node는 removal disposition을 만들지 않는다.

Deletion eligibility:

```text
dominance = strong_dominance
candidate_branch_execution_evidence_sufficient = true
detection_after >= detection_before
newly_survived_critical_faults = 0
failure_localization_after >= failure_localization_before
determinism_after >= determinism_before
isolation_after >= isolation_before
authority_guarantee_after >= authority_guarantee_before
```

Exit Gate:

```text
evidence_free_elimination_candidate = 0
unknown_candidate_disposition = 0
unmapped_removal_candidate = 0
protection_map_failure_conditions_not_in_matrix = 0
protection_map_fail_closed_paths_not_in_matrix = 0
freeze_precedes_disposition = true
material_branch_evidence_gap = 0
```

---

### Change 4 — Phase 4: Source-preserving bounded pilot

Purpose:

전체 wave 전에 mapping, helper, fault comparison 및 migration 방법이 실제 codebase에서 정밀도를 보존하는지 검증한다.

Files:

- pilot에서 선택한 `Iris/build/description/v2/tests/*.py`
- pilot 전용 domain-local support module
- `Iris/_docs/refactor/test_precision_lightweighting/pilot_receipt.json`

Implementation Notes:

Pilot은 최대 세 family로 제한한다.

1. Registry authority family
   - `test_dvf_3_3_registry_authority_canonical_closure.py`의 repeated path/hash/subprocess/temporary-evidence mechanics를 분리한다.
   - exact-current required 3개 node의 identity와 assertion responsibility는 pilot에서 유지한다.
   - helper가 evidence root, current mode, expected status 또는 authority를 자동 선택하지 않게 한다.

2. Artifact lifecycle family
   - `test_artifact_lifecycle_executor.py`의 1,732 LOC fixture builder와 Git/tamper/restore orchestration을 step object 또는 explicit helper로 분리한다.
   - 두 exact-required nodes는 pilot에서 삭제·병합하지 않는다.
   - 각 tamper fault의 기존 failure signature와 cleanup/recoverability assertion을 보존한다.

3. Compose family
   - `test_compose_layer3_text_v2.py`와 `test_compose_layer3_text_overlay.py`의 JSON/JSONL fixture mechanics를 family-local helper로 단순화한다.
   - 각 selected role, legacy rejection, diagnostic-only path, optional section 및 quality-flag partition을 별도 contract로 유지한다.
   - dominance evidence가 있는 configured-current scenario가 있더라도 pilot의 첫 적용은 identity-preserving simplification을 우선한다.

`test_interaction_cluster_usecase_import.py`는 761 LOC의 historical source이므로 D2에 따라 pilot 대상에서 제외하고 unchanged comparison만 남긴다.

Pilot STOP conditions:

- unexplained denominator 또는 source-set drift
- exact-current/required-validation identity loss
- branch, partition, fault detection 또는 failure attribution loss
- helper가 semantic default, authority selection 또는 PASS/FAIL policy를 숨김
- new environment dependency, flakiness, source mutation 또는 residue
- production file diff 발생

STOP이 발생하면 해당 pilot wave 전체를 rollback하고 candidate/family disposition을 직접 갱신한다.

```text
precision_or_localization_loss -> preserve_intentional_defense
insufficient_or_unstable_evidence -> defer_insufficient_evidence
helper_material_gain_absent -> no_op_no_material_gain
```

Rollback 뒤 focused/exact/configured/no-mutation validation이 다시 exit `0`이 되기 전에는 다른 family pilot을 열지 않는다.

Validation:

- affected focused tests before/after
- exact current route
- configured current route with denominator enforcement
- fixed mutation/fault matrix
- failure-localization comparison
- production/no-source-mutation guard

---

### Change 5 — Phase 5: Test implementation complexity reduction waves

Purpose:

Pilot에서 검증된 방법을 contract family별 small wave로 확장해 test-support orchestration을 줄인다.

Files:

- Phase 2 inventory에서 승인된 current test family
- family-local support modules
- `Iris/_docs/refactor/test_precision_lightweighting/complexity_wave_*.json`

Implementation Notes:

- wave 하나는 하나의 contract owner 또는 긴밀히 결속된 family만 다룬다.
- helper는 mechanics만 소유한다.

허용 예:

```text
explicit temporary repository initialization
explicit Git invocation/result capture
canonical JSON/JSONL read-write
hash calculation
path construction
cleanup and residue assertion
fixture materialization with caller-supplied semantic inputs
```

Path helper는 기존 canonical repository-relative POSIX logical path를 그대로 보존한다. Absolute path, `..`, output escape와 reparse-ancestor 거부 의미를 완화하거나 Windows native separator로 CAS/logical identity를 재작성하지 않는다. Path normalization은 authority 선택이나 artifact role 변경 권한을 갖지 않는다.

금지 예:

```text
current/historical/diagnostic route 선택
authority 또는 expected semantic result 선택
PASS/FAIL policy 결정
required-validation successor 자동 선택
hidden default fixture mutation
```

- helper extraction이 exact runner의 preimport dependency closure에 새 module을 추가하면 allowed-module/dependency binding을 같은 wave에서 명시적으로 이관한다.
- large source에서 helper를 분리해도 helper LOC를 제외하지 않는다. total test-support LOC, setup LOC, max method LOC 및 duplicate mechanics를 함께 비교한다.
- failure localization을 위해 giant node를 나누어 local node 수가 증가하면 이를 별도 `split_for_failure_localization`으로 계상하며 감축 실패로 숨기지 않는다.
- `complete` 후보가 되려면 complexity wave의 누적 결과가 frozen 500+ file, 1,000+ file 및 large-method count를 각각 실제로 감소시켜야 한다. 작은 helper만 줄고 large concentration이 그대로면 해당 축은 미달이다.
- split 필요성이 확인됐으나 실행하지 않은 경우 candidate disposition에 `split_warranted_not_executed=true`, 미실행 사유, 영향받는 failure/localization IDs를 기록한다. Node-count 목표만을 이유로 필요한 split을 숨기거나 dominance를 승인하지 않는다.
- 모든 wave와 cumulative comparison에서 `gross_removed_node_count`, `localization_split_added_node_count`, `net_node_delta`를 분리 보고한다.

Validation:

- fixture output/negative fixture parity
- contract and branch parity
- representative fault signature parity
- no new environment/order/global-state dependency
- cumulative successor suite validation
- test-support LOC/complexity accounting
- frozen large-file/method member list와 500/1,000 LOC bucket reconciliation
- gross removals / localization splits / net node delta reconciliation

---

### Change 6 — Phase 6: Proven scenario/node reduction과 Type A identity migration

Purpose:

Phase 3에서 `strong_dominance` 또는 `replace_with_stronger_invariant`가 증명된 current 후보만 실제로 줄인다.

Files:

- 승인된 current test sources
- `round3_test_taxonomy.json` 및 `current_route_required_validations.json` — node identity가 바뀌는 경우에만
- `Iris/_docs/refactor/test_precision_lightweighting/identity_migration.jsonl`
- `Iris/_docs/refactor/test_precision_lightweighting/cumulative_comparison.json`

Implementation Notes:

- 한 wave의 변경 상한은 하나의 contract family와 그 결속 manifest로 둔다.
- 각 제거 identity는 다음 mapping을 가진다.

```text
predecessor_source_file
predecessor_node_id
successor_source_file
successor_node_id | removed
disposition
protected_contract_ids
replacement_evidence_ids
route
authority_role
required_validation_bindings
regression_provenance_ids
```

- exact-current 또는 required-bound identity 변경은 test change, taxonomy, manifest, negative migration test를 하나의 atomic wave로 처리한다.
- stale predecessor, missing successor, dual successor 및 dangling required binding을 fail-closed로 검사한다.
- parameterization/subtest 전환만으로 node 감소 credit을 주지 않는다.
- historical/diagnostic와 protected compatibility source는 unchanged 상태를 유지한다.
- 각 wave는 wave delta가 아니라 baseline부터 누적된 successor suite를 비교한다.

Validation:

```text
removed_without_dominance_or_replacement = 0
dangling_required_validation = 0
dual_current_test_binding = 0
stale_predecessor_binding = 0
precision_regression = 0
```

---

### Change 7 — Optional Phase 6B: Type B source-set migration transaction

Purpose:

Type A를 소진한 뒤에도 material한 file-level 감축 후보가 있고 owner가 별도 gate를 승인한 경우에만 source 삭제·병합·이동을 수행한다.

Files:

- approved source files
- `Iris/build/description/v2/tests/conftest.py`
- `Iris/_docs/round3/round3_pytest_source_classification.json`
- `Iris/_docs/round3/round3_full_discovery_denominator.json`
- `Iris/_docs/round3/round3_test_taxonomy.json`
- `Iris/_docs/round3/current_route_required_validations.json`
- Type B migration validator와 receipt

Implementation Notes:

- Type B entry에는 owner approval, exact source-set delta, predecessor/successor hash, all-node disposition 및 rollback path가 필요하다.
- current policy의 tracked source count/hash와 approved clean-checkout-absent set을 새 successor identity로 다시 계산한다.
- `pytest.ini --ignore`, silent deselection, route reclassification 또는 vanished-source 허용으로 migration을 우회하지 않는다.
- removed source의 모든 node가 successor 또는 `eliminate_strongly_dominated` evidence에 연결돼야 한다.
- 별도 test-body CAS는 만들지 않는다. exact predecessor commit/blob과 identity ledger를 provenance로 사용한다.
- Type B gate가 열리지 않아도 Type A가 A1의 실제 감축 조건을 만족하면 `complete`가 가능하다. Type A에서 안전한 후보가 없고 Type B gate도 열리지 않으면 `reduction_outcome=measured_no_op`, top-level `partial`로 닫으며 reduction success를 주장하지 않는다.

Validation:

- clean checkout에서 source-policy count/hash validation
- unknown, vanished, unclassified, unexpectedly missing source `0`
- exact taxonomy와 required-validation resolution
- negative fixtures: stale policy hash, missing source, dual successor, dangling required test가 모두 fail-closed
- full before/after denominator and precision comparison

---

### Change 8 — Phase 7~8: Authority reconciliation과 full precision equivalence

Purpose:

최종 successor suite에 stale/dangling/dual identity가 없고 baseline 대비 정밀도 손실이 없음을 machine-readable evidence로 증명한다.

Files:

- `Iris/validation/test_lightweighting/validate_identity_migration.py`
- `Iris/validation/test_lightweighting/compare_precision.py`
- `Iris/_docs/refactor/test_precision_lightweighting/cumulative_comparison.json`
- `Iris/_docs/refactor/test_precision_lightweighting/validation_matrix.preterminal.json`

Implementation Notes:

- fixed comparison domain에서 다음 set을 독립 비교한다.

```text
protected contracts
input partitions
production branches/conditions
fail-closed paths
interaction states
mutation/fault detections
failure signatures/localization
route guarantees
authority guarantees
```

- 다음 complexity/count 축을 별도 비교한다.

```text
node IDs
semantic scenarios
executed cases
input rows
test source LOC
test-support LOC
large files/methods
fixture/setup LOC
duplicate mechanics
plan-local validator LOC/file count (report-only)
```

- `large files/methods`는 aggregate 서술이 아니라 frozen metric definition에 따라 exact delta를 산출한다.

```text
files_ge_500_delta = files_ge_500_final - files_ge_500_baseline
files_ge_1000_delta = files_ge_1000_final - files_ge_1000_baseline
large_test_method_count_delta = large_test_method_count_final - large_test_method_count_baseline
large_method_metric_definition_after == large_method_metric_definition_baseline
```

- 한 family의 improvement로 다른 family의 regression을 상쇄하지 않는다.
- `protected_contract_count`와 `protected_branch_count`는 preservation denominator이며 reduction metric으로 합산하지 않는다.
- `plan_local_validator_LOC`와 `plan_local_validator_file_count`의 baseline/final value 및 post-closeout disposition을 별도 보고한다. 이는 `test_support_LOC_delta`를 상쇄하거나 `reduced` classifier를 만족시키는 값이 아니다.
- historical/diagnostic를 변경하지 않았다면 source/node/hash와 route behavior뿐 아니라 baseline canonical result identity의 unchanged proof를 남긴다.
- before/after는 모두 `environment_class=clean_checkout_only`에서 실행한다. Working-overlay denominator를 clean-checkout successor와 비교하지 않는다.
- accepted baseline과 denominator/operator set이 달라졌다면 직접 score 비교를 중단한다. 비교를 계속하려면 deletion 전 clean-checkout subject에서 새 baseline/fault matrix를 freeze하고 delta reason을 기록한다.

Outcome Classifier — Change 9 진입을 막지 않음:

```text
pytest_node_count_delta = pytest_node_count_final - pytest_node_count_baseline
removed_redundant_executed_scenario_count = <recorded integer>
test_support_LOC_delta = test_support_LOC_final - test_support_LOC_baseline
files_ge_500_delta = <recorded integer>
files_ge_1000_delta = <recorded integer>
large_test_method_count_delta = <recorded integer>
gross_removed_node_count = <recorded integer>
localization_split_added_node_count = <recorded integer>
net_node_delta = localization_split_added_node_count - gross_removed_node_count
reduction_axis_values_recorded = true
a1_all_reduction_conditions_satisfied = true | false
```

`a1_all_reduction_conditions_satisfied=true`는 node delta `<0`, redundant executed scenario 제거 `>0`, test-support LOC delta `<0`, 두 large-file bucket delta `<0`, large-method delta `<0`가 모두 참일 때만 산출한다. `false`는 unsafe 또는 phase failure가 아니라 final outcome classifier input이다. Safety Exit Gate가 PASS하고 classifier 값이 완전하면 `true`, valid mixed `false`, safe-candidate-zero `false` 모두 Change 9로 진행한다.

Governance cost report — reduction classifier input이 아님:

```text
plan_local_validator_LOC = <recorded integer>
plan_local_validator_file_count = <recorded integer>
plan_local_validator_metrics_reporting_only = true
post_closeout_disposition = retain_round_reproduction_evidence
```

Safety Exit Gate — fail-closed:

```text
unknown_current_binding = 0
dangling_required_validation = 0
dual_current_test_binding = 0
historical_reproduction_gap = 0
diagnostic_identity_or_disposition_drift = 0
historical_result_identity_matches_baseline = true
diagnostic_raw_result_identity_matches_baseline = true
before_after_environment_class_match = true
fault_matrix_sha256_matches_frozen_baseline = true
large_file_metric_definition_matches_baseline = true
large_method_metric_definition_matches_baseline = true
after_universe_reconciled = true
new_helper_or_fixture_omission = 0
reduction_axis_values_recorded = true
a1_all_reduction_conditions_satisfied in {true, false}
precision_regression = 0
```

`a1_all_reduction_conditions_satisfied=false`만으로 이 Safety Exit Gate를 실패시키거나 Change 9를 차단하지 않는다.

---

### Change 9 — Phase 9: Clean-checkout terminal validation, independent review와 closeout

Purpose:

exact tracked successor subject에서 결과를 두 번 재현하고 claim boundary를 봉인한다.

Files:

- `Iris/validation/clean_checkout/**`
- `Iris/_docs/refactor/test_precision_lightweighting/validation_matrix.preterminal.json`
- `Iris/_docs/refactor/test_precision_lightweighting/terminal_evidence_placement_decision.json`
- `Iris/_docs/refactor/test_precision_lightweighting/terminal_evidence_pointer.json`
- owner-managed external durable archive의 `terminal_validation_attestation.json`
- owner-managed external durable archive의 `machine_validation_manifest.json`
- owner-managed external durable archive의 `independent_review.json`
- owner-managed external durable archive의 `owner_seal.json`
- owner-managed external durable archive의 `terminal_bundle_hash_manifest.json`
- owner-managed external durable archive의 `closeout_receipt.json`
- owner-managed external durable archive의 `terminal_evidence_retrieval_report.json`
- 필요한 경우 `S_terminal` 전 pending-only `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`

Implementation Notes:

- terminal sequence를 다음 순서로 고정한다.

```text
1. implementation/test/migration 완료 subject S_impl freeze
2. S_impl에서 preterminal validation/comparison evidence 생성, Change 8 Safety Exit Gate PASS 및 reduction classifier 기록
3. owner가 external placement/custody/durability/retrieval contract를 ratify
4. required tracked evidence, stable closure_id, tracked pointer, closeout candidate 및 pending-only top-doc 확정
5. 위 tracked material을 포함한 terminal candidate S_terminal commit/tree freeze
6. pointer의 containing commit/tree가 S_terminal임을 resolve한 뒤 clean checkout exact Run A / Run B 수행
7. terminal_validation_attestation과 machine_validation_manifest를 external durable archive에 append-only 기록
8. S_terminal + machine_validation_manifest에 independent review 수행
9. S_terminal + machine_validation_manifest + review identity에 owner seal 수행
10. terminal_bundle_hash_manifest를 생성해 machine manifest/review/owner artifact hash를 봉인
11. manifest SHA-256과 동일 subject/pointer tuple을 참조하는 closeout_receipt를 final manifest 직후 생성
12. fresh retrieval root에서 tracked pointer 기반 bundle 재조회·hash/schema/DAG 검증
13. 성공한 terminal_evidence_retrieval_report를 durable archive에 append-only 기록
```

- `S_impl`의 PASS를 `S_terminal`에 상속하지 않는다. Run A/B, independent review와 owner seal은 모두 같은 `S_terminal` commit/tree에 결속한다.
- Change 9 entry는 `change8_safety_exit_gate=PASS`, `reduction_axis_values_recorded=true`, boolean classifier 존재와 `plan_local_validator_metrics_reporting_only=true`를 요구한다. `a1_all_reduction_conditions_satisfied=false`인 mixed/no-op candidate도 terminal Run A/B, review, owner seal과 closeout evidence를 생성하도록 진입을 허용한다.
- step 12 retrieval이 실패하면 step 11 receipt는 canonical closeout이 아닌 failed-attempt trace로 남긴다. In-place 수정이나 임시 결과 대체 없이 새 `closure_id`/pointer/allocator receipt를 발급하고 pointer를 포함하는 새 terminal subject에서 step 5 이후를 다시 수행한다.
- terminal validation 이후 terminal attestation, review, owner seal, closeout receipt 또는 top-doc을 tracked tree에 추가·수정하면 그 tree는 `S_next`다. 이 경우 기존 terminal claim을 폐기하고 `S_next`에서 Run A/B, review, owner seal을 전부 다시 수행한다.
- Existing tracked successor chain과 external bundle을 Phase 0에서 비교한 placement decision은 `external_bundle`로 고정한다. 이를 실행 중 임의로 tracked successor chain으로 바꾸지 않으며 변경에는 새 owner decision과 새 terminal subject가 필요하다.
- repository-external work/result root에서 `environment_class=clean_checkout_only`인 Run A와 Run B를 실행한다.
- exact current, configured current, historical, diagnostic, configured all advisory, required full-repository gate 및 no-mutation audit를 서로 다른 row로 기록한다.
- historical result identity와 diagnostic raw result identity를 accepted baseline의 canonical identity와 비교한다. Diagnostic raw result와 terminal disposition을 별도 field로 보존하고 raw failure를 closeout PASS로 다시 쓰지 않는다.
- terminal command 시작 전에 tracked round-scoped validator 8개, supporting test 1개와 `validator_dependency_manifest.json`의 clean-checkout presence/hash/current-round command closure를 검증한다. Permanent `validator_dependency_closure_complete`는 `gate_registered=true` 집합만 소비하며 이번 round의 validator count는 0이다.
- parent/child process에 bytecode/cache isolation environment를 적용하고 work/result root 밖 child residue가 0인지 검사한다.
- independent reviewer는 plan/roadmap 작성 또는 implementation에 참여하지 않아야 하며 exact successor bundle을 검토한다.
- review result는 `Verdict=PASS`와 P0/P1/P2/P3 모두 0이어야 complete gate를 만족한다.
- owner seal은 machine validation이나 independent review를 대체하지 않으며 exact `S_terminal`, `machine_validation_manifest.json` SHA-256과 independent-review SHA-256을 직접 참조해야 한다. Final terminal bundle manifest는 machine manifest, review와 owner seal hash를 봉인하며 owner-seal predecessor로 사용하지 않는다.
- top-level docs는 `S_terminal` freeze 전에 `top_doc_terminal_state=pending_terminal_validation`, stable `closure_id`, tracked pointer path/blob identity와 non-claims만 기록한다. Final outcome을 예측하거나 post-closeout sync하지 않으며 `final_outcome_authority=external_terminal_bundle`로 고정한다.
- tracked top-doc이 참조하는 evidence identity는 `closure_id + terminal_evidence_pointer Git blob + containing S_terminal commit/tree`다. External closeout receipt는 같은 tuple과 final terminal bundle manifest SHA-256을 결속한다.

Validation:

```text
Run_A_denominator == Run_B_denominator
Run_A_canonical_result == Run_B_canonical_result
Run_A_environment_class == Run_B_environment_class == clean_checkout_only
source_mutation = 0
unexpected_residue = 0
child_process_residue = 0
exact_current = PASS
configured_current = PASS
historical_policy_preserved = true
diagnostic_raw_and_disposition_preserved = true
historical_result_identity_matches_baseline = true
diagnostic_raw_result_identity_matches_baseline = true
plan_local_validator_present_in_clean_checkout = true
terminal_round_validator_closure_complete = true
validator_dependency_closure_complete = true
gate_registered_validator_count = 0
round_scoped_validator_test_count = 1
new_test_source_registration_branch_consistent = true
baseline_frozen_after_plan_local_source_registration = true
terminal_evidence_retrieval_capability_present = true
terminal_evidence_retrieval_capability_identity = Iris/validation/test_lightweighting/validate_terminal_evidence_bundle.py@<git_blob>:fresh-root-v1
change8_safety_exit_gate = PASS
reduction_axis_values_recorded = true
a1_all_reduction_conditions_satisfied in {true, false}
plan_local_validator_metrics_reporting_only = true
terminal_repository_gate = current_policy_compliant
independent_review = PASS
P0 = P1 = P2 = P3 = 0
owner_seal = granted
terminal_subject == review_subject == owner_seal_subject
machine_validation_manifest_valid = true
machine_validation_manifest_valid.producer = Iris/validation/test_lightweighting/validate_terminal_evidence_bundle.py@<git_blob>:fresh-root-v1
top_doc_terminal_state = pending_terminal_validation
final_outcome_authority = external_terminal_bundle
external_bundle_custody_bound = true
external_bundle_durability_contract_bound = true
external_bundle_retrieval_verified = true
external_bundle_retrieval_verified.producer = Iris/validation/test_lightweighting/validate_terminal_evidence_bundle.py@<git_blob>:fresh-root-v1
terminal_bundle_hash_manifest_valid = true
terminal_bundle_hash_manifest_valid.producer = Iris/validation/test_lightweighting/validate_terminal_evidence_bundle.py@<git_blob>:fresh-root-v1
closeout_receipt_valid = true
closeout_receipt_valid.producer = Iris/validation/test_lightweighting/validate_terminal_evidence_bundle.py@<git_blob>:fresh-root-v1
terminal_evidence_retrieval_report = PASS
post_terminal_tracked_change_count = 0
```

---

## 7. Validation Plan

### Automated Validation

모든 command는 exact subject, environment class, command line, environment receipt, exit code, selected/deselected/skipped/subtest count, wall-clock 및 output identity를 기록한다. 아래 명령의 repository-external receipt 경로는 실행 시 확정한다. Parent와 child Python process에는 다음 environment contract를 적용한다.

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
# bytecode가 필요한 검증에만 repository-external 경로를 사용한다.
$env:PYTHONPYCACHEPREFIX = '<repository-external-work-root>\pycache'
```

각 command wrapper는 child environment 상속과 종료 후 repository/external-root residue를 검증한다.

Phase 0 pre-baseline source-registration observation:

```powershell
# 신규 test path를 positional argument로 주지 않아야 default configured discovery 실측이 된다.
uv run python -B -m pytest --collect-only -q -p no:cacheprovider --round3-contract=all
uv run python -B -m pytest -q -p no:cacheprovider Iris/validation/test_lightweighting/tests/test_validate_terminal_evidence_bundle.py
```

- 첫 command의 path/node output과 exit를 `execution_isolation_receipt.json`에 기록해 `new_test_source_collected_by_configured_discovery`를 판정한다. Unclassified failure가 발생하면 관측 trace로만 보존하고 conditional additive registration 후 같은 configured collection이 exit `0`일 때만 baseline을 동결한다.
- 두 번째 command는 `standalone_explicit_path` plan-local test contract다. `--round3-contract` 부재는 route 우회가 아니라 configured source-policy 판정과 분리된 명시적 supporting-test 실행이며, 첫 command의 discovery evidence를 대체하지 않는다.

1. Focused wave validation

```powershell
uv run python -B -m pytest -q -p no:cacheprovider --round3-contract=all <affected-test-files>
```

2. Exact current authority

```powershell
uv run python -B Iris/_docs/round3/round3_run_contract_tests.py --class current --enforce-current-build-closure
```

3. Configured current denominator

```powershell
uv run python -B -m pytest -q -p no:cacheprovider --round3-contract=current --round3-enforce-denominator --round3-denominator-receipt <external-absolute-path>
```

4. Historical and diagnostic unchanged routes

```powershell
uv run python -B -m pytest -q -p no:cacheprovider --round3-contract=historical --round3-enforce-denominator --round3-denominator-receipt <external-absolute-path>
uv run python -B -m pytest -q -p no:cacheprovider --round3-contract=diagnostic --round3-enforce-denominator --round3-denominator-receipt <external-absolute-path>
```

5. Configured full advisory

```powershell
uv run python -B -m pytest -q -p no:cacheprovider --round3-contract=all --round3-enforce-denominator --round3-denominator-receipt <external-absolute-path>
```

Configured full exit가 0이 아니면 PASS를 주장하지 않는다. failure는 current/modified/mandatory intersection과 historical/diagnostic-only disposition을 분리한다.

6. Plan-local mapping, dominance, migration, comparison 및 terminal-retrieval validators

```powershell
uv run python -B Iris/validation/test_lightweighting/collect_test_inventory.py <args>
uv run python -B Iris/validation/test_lightweighting/build_protection_map.py <args>
uv run python -B Iris/validation/test_lightweighting/build_detection_baseline.py <args>
uv run python -B Iris/validation/test_lightweighting/compare_failure_localization.py <args>
uv run python -B Iris/validation/test_lightweighting/validate_dominance.py <args>
uv run python -B Iris/validation/test_lightweighting/validate_identity_migration.py <args>
uv run python -B Iris/validation/test_lightweighting/compare_precision.py <args>
uv run python -B Iris/validation/test_lightweighting/validate_terminal_evidence_bundle.py --mode fresh-root-v1 --pointer <tracked-pointer> --archive-root <owner-durable-root> --fresh-root <new-empty-external-root> --output <owner-durable-root>\terminal_evidence_retrieval_report.json
uv run python -B -m pytest -q -p no:cacheprovider Iris/validation/test_lightweighting/tests/test_validate_terminal_evidence_bundle.py
```

- 각 validator는 `validator_dependency_manifest.json`의 tracked path/hash와 일치해야 한다.
- clean checkout에서 `plan_local_validator_present_in_clean_checkout=true`와 `terminal_round_validator_closure_complete=true`를 먼저 검증한다.
- `validator_dependency_closure_complete`는 `gate_registered=true` row만 대상으로 계산하고 이번 8개 validator와 supporting test가 permanent full-repository gate에 등록되지 않았음을 검사한다.
- fault matrix freeze receipt가 candidate disposition보다 앞서며 protection-map failure universe 누락이 0인지 검사한다.
- terminal-retrieval command와 test는 Phase 0 capability preflight와 Change 9 fresh-root retrieval에서 같은 tracked Git blob 및 `fresh-root-v1` mode identity를 사용한다. Phase 0에서는 synthetic positive/tampered fixture로 capability를 검증하고, Change 9에서는 exact terminal pointer/archive를 입력한다.

7. Clean-checkout full gate and deterministic compare

- `Iris/validation/clean_checkout/invoke_receipt_bound_full_gate.ps1`
- `Iris/validation/clean_checkout/invoke_deterministic_compare.ps1`
- exact successor commit, environment receipt, disjoint external work/result roots를 명시한다.
- `S_terminal` 이후 tracked 변경이 0인지 검사한다. 변경이 있으면 이 gate와 review/owner seal을 새 subject에서 재실행한다.
- final bundle 작성 후 새 empty external retrieval root에서 tracked pointer, owner-provided durable archive root와 `closure_id`를 입력해 `Iris/validation/test_lightweighting/validate_terminal_evidence_bundle.py --mode fresh-root-v1`을 실행한다.
- pointer blob, containing commit/tree, allocator receipt, artifact schemas와 terminal bundle hashes가 하나라도 다르면 retrieval PASS를 내지 않는다.
- 이 producer identity를 `<tracked Git blob>:fresh-root-v1`으로 retrieval report에 기록하고 `machine_validation_manifest_valid`, `external_bundle_retrieval_verified`, `terminal_bundle_hash_manifest_valid`, `closeout_receipt_valid` 네 값 모두에 결속한다. 다른 command 또는 수동 판정은 이 값을 생산할 수 없다.

8. Diff and scope guards

```powershell
git diff --check
git status --short
```

- allowed test/validation/docs paths 밖 production diff `0`
- tracked source mutation `0`
- unexpected repository residue `0`

Validation은 다음 비교를 반드시 포함한다.

- node/source/route denominator
- contract / partition / branch / fail-closed parity
- dominance가 실제 branch 실행 여부에 materially 의존한 candidate에 한한 production-target-scoped coverage/equivalent trace parity
- applicable mutation 또는 approved fault matrix parity
- failure-localization parity
- identity/required-validation migration reconciliation
- historical canonical result identity와 diagnostic raw result identity parity
- deterministic Run A/B canonical result
- child-process bytecode/cache/residue isolation
- validator clean-checkout presence, current-round closure와 `gate_registered=true` permanent dependency closure
- total test-support LOC, 500+/1,000+ file count와 frozen-definition large-method count 감소
- plan-local validator LOC/file count와 post-closeout disposition 보고; reduction metric과 상쇄하지 않음
- gross removals / localization splits / net node delta
- external bundle custody/durability/pointer-based retrieval, intermediate machine manifest, final hash manifest 및 closeout receipt DAG

### Manual Validation

- candidate disposition과 protection map의 contract-owner review
- materially branch-dependent candidate의 targeted trace가 production branch ID와 survivor 책임을 실제로 입증하는지 검토
- multi-responsibility node와 regression provenance의 수동 확인
- required-bound predecessor→successor mapping review
- independent artifact-bound review
- owner의 external evidence placement/custody/retention ratification과 fresh retrieval 시연

Project Zomboid 인게임 검증은 production/runtime/public-output diff가 0인 본 계획의 mandatory gate가 아니다. 실행 중 production/runtime surface가 변경되면 해당 변경을 본 계획에서 제거하거나 별도 승인 계획으로 분리한다.

### Validation Limits

- no multiplayer/dedicated-server validation
- no long-session/soak validation
- no B42 validation
- no Workshop, deployment, release-readiness validation
- no external mod compatibility sweep
- no repository-wide exhaustive mutation testing
- no global 100% branch coverage claim
- no runtime FPS/latency/heap improvement claim
- no exact tokenizer/context-cost reduction claim
- no historical failure resolution claim
- no diagnostic finding resolution claim
- no production behavior or architecture improvement claim

---

## 8. Risk Surface Touch

### Authority Surface

**High, validation governance에 한정.**

가능한 변경:

- exact test identity
- taxonomy successor mapping
- required-validation binding
- configured source-set identity
- validation receipt와 closeout evidence

변경하지 않음:

- Iris source facts, rendered, runtime, package, Publish Boundary authority
- `full_repository_gate.json`의 permanent validator dependency inventory; 8개 plan-local module과 supporting test 1개는 round-scoped로 남음

### Runtime Behavior Surface

**None.** Production/runtime source 변경은 금지한다.

### Compatibility Surface

**Product compatibility surface 변경 없음.** Supported API와 protected compatibility test는 preserve-only다. Test identity migration이 발생해도 제품 API 또는 Lua require contract를 바꾸지 않는다.

### Sealed Artifact Surface

**High.** 기존 artifact는 immutable predecessor로 보존한다. 신규 baseline, dominance, migration, pre-terminal comparison, evidence-placement decision과 pointer는 tracked successor evidence로 추가한다. Terminal attestation, independent review, owner seal과 closeout receipt는 exact terminal subject를 바꾸지 않는 owner-managed external durable archive에 append-only로 생성하며 tracked pointer로 재조회한다.

### Public-Facing Output Surface

**None.** Browser/Wiki/Tooltip/public text/package output을 변경하지 않는다.

---

## 9. Risk Analysis

### Architecture Risk

- configured source policy, exact taxonomy와 required-validation을 하나의 denominator로 오해할 위험
- test helper가 authority selection 또는 semantic default를 소유해 새 비공식 validation layer가 될 위험
- Type B source migration이 preimport build dependency closure 또는 clean-checkout source binding을 우회할 위험
- working overlay baseline과 clean-checkout successor를 비교해 감축량을 왜곡할 위험
- plan-local validator가 작업 디렉터리에만 존재하여 clean checkout에서 terminal gate를 재현하지 못할 위험
- subject-specific validator를 permanent full-repository dependency로 승격해 future gate를 stale하게 만들 위험
- 신규 plan-local supporting test의 configured discovery/classification을 확정하기 전에 baseline을 동결할 위험
- plan-local validator/tooling LOC가 test-support 감축 지표 밖에 남아 repository maintenance cost를 숨길 위험
- candidate-local branch instrumentation을 repository-wide mandatory layer로 일반화할 위험
- machine validation, independent review와 owner seal을 하나의 승인 축으로 오해할 위험
- owner seal의 machine-side predecessor와 final bundle manifest를 혼동해 evidence DAG를 순환시키는 위험
- precision safety gate와 reduction success classifier를 혼합해 valid `mixed_reduction`/`measured_no_op`을 `blocked`로 왜곡할 위험
- terminal retrieval producer의 부재를 owner seal 이후에야 발견할 위험
- external terminal bundle을 temporary output과 혼동해 closeout evidence가 유실되거나 재조회되지 않을 위험
- pending top-doc에 아직 발생하지 않은 final PASS/complete를 기록할 위험

Mitigation:

- 세 authority를 별도 inventory와 crosswalk로 유지한다.
- helper charter와 explicit arguments를 요구한다.
- Type B를 별도 owner-approved atomic transaction으로 제한한다.
- accepted before/after를 모두 `environment_class=clean_checkout_only`로 고정하고 working-overlay denominator는 diagnostic field로만 보존한다.
- 8개 round-scoped validator의 clean-checkout current-round closure를 확인하되 `gate_registered=false`로 permanent full-repository dependency와 분리한다.
- 신규 supporting test를 track한 뒤 default configured discovery를 직접 관측하고 conditional additive classification을 끝낸 후에만 baseline을 동결한다.
- plan-local module/test LOC와 file count를 별도 보고하고 `retain_round_reproduction_evidence`/future-removal-candidate disposition을 명시한다.
- branch execution evidence는 materially branch-dependent candidate와 production target에만 한정하고 global coverage infrastructure를 PASS 조건으로 만들지 않는다.
- machine PASS, reviewer PASS, `owner_seal=granted`를 서로 대체할 수 없는 세 개의 closure axis로 기록한다.
- owner seal보다 앞선 `machine_validation_manifest.json`과 owner seal 뒤의 `terminal_bundle_hash_manifest.json`을 별도 schema/hash node로 고정한다.
- Change 8은 precision safety를 fail-closed로 판정하고 reduction 축 값은 boolean classifier로만 기록한다. Safety PASS이면 classifier가 false여도 모든 정식 outcome이 Change 9 terminal evidence 절차를 통과한다.
- tracked `validate_terminal_evidence_bundle.py@fresh-root-v1`을 Phase 0에서 구현·시험하고 machine manifest 및 세 retrieval Complete Gate 값의 유일한 producer로 결속한다.
- owner-ratified custody/durability/retrieval contract, tracked pointer와 fresh-root retrieval verification이 없으면 external evidence closeout을 block한다.
- top-doc은 `pending_terminal_validation`과 pointer identity만 기록하고 final outcome은 external terminal bundle에만 둔다. Repository-only consumer는 pending을 final로 해석하지 않고 pointer를 조회한다.

### Runtime Risk

- 원칙상 없음. Production diff가 생기면 해당 wave를 중단한다.
- test fixture가 실제 source tree를 import-time 또는 runtime에 mutate할 수 있는 execution contamination 위험은 존재한다.

Mitigation:

- external work/result root, `-B`, cacheprovider 비활성화, pre/post Git state와 residue 비교를 사용한다.
- parent와 모든 child process에 `PYTHONDONTWRITEBYTECODE=1`을 강제하고, 필요하면 repository-external `PYTHONPYCACHEPREFIX`를 사용한다.

### Compatibility Risk

- protected compatibility test를 일반 duplicate로 잘못 제거할 위험
- legacy/current representation이 같은 production function을 호출한다는 이유로 한쪽을 지우는 cross-boundary 오류

Mitigation:

- protected surface preserve-only(E2)
- representation boundary, consumer path, oracle와 lifecycle이 다르면 intentional defense로 보존

### Regression Risk

- false dominance로 고유 partition, interaction 또는 fail-closed path를 잃을 위험
- aggregate coverage/mutation score가 특정 critical fault loss를 숨길 위험
- static branch subset 추정이 실제 branch 실행 차이를 숨길 위험
- node 병합으로 failure localization이 악화될 위험
- exact-current predecessor를 제거한 뒤 required-validation이 stale/dangling 상태가 될 위험
- current 감축을 historical/diagnostic denominator 조정으로 세탁할 위험
- helper 이동만으로 LOC 감소를 과장할 위험
- total LOC만 줄이고 500+/1,000+ file 또는 frozen-definition large-method concentration을 그대로 두는 위험
- node 감소 압력 때문에 필요한 localization split을 실행하지 않거나 숨기는 위험
- candidate disposition을 본 뒤 fault universe를 축소하는 result-conditioned matrix 위험
- terminal 검증 뒤 tracked evidence나 문서를 수정하고 predecessor PASS를 successor에 상속하는 chronology 위험

Mitigation:

- contract/branch/partition/interaction/fault/failure-signature/authority vector의 subset proof와 materially branch-dependent candidate의 targeted execution trace
- fixed per-family mutant/fault universe와 critical fault 개별 비교
- representative failure attribution comparison
- atomic identity migration과 negative fail-closed fixtures
- D2 route no-change 및 route cross-substitution 금지
- total test-support LOC accounting
- frozen large-file/method definition과 member-selection rule을 유지하고 그 rule을 final tree에 재적용해 신규 helper/fixture까지 포함한 500+, 1,000+ 및 large-method count를 각각 completion gate에 결속한다. Baseline member list/hash는 before identity와 reconciliation에만 사용한다.
- gross removals, localization splits와 net node delta를 분리하고 미실행 split의 사유/영향 ID를 disposition에 기록한다.
- protection map의 모든 `failure_conditions`와 `fail_closed_paths`에서 fault matrix를 파생하고 disposition 전에 SHA-256으로 freeze한다.
- tracked implementation/evidence/docs를 먼저 동결한 exact terminal subject에서 Run A/B와 review를 수행하며, 이후 tracked tree가 바뀌면 새 subject에서 terminal validation을 전부 재실행한다.

---

## 10. Rollback Plan

Rollback 단위는 contract-family wave다. 각 wave는 다음을 함께 결속한다.

```text
predecessor test code and source identity
predecessor taxonomy/source-policy/required binding
successor test code and source identity
successor taxonomy/source-policy/required binding
before/after precision evidence
fault/mutation and failure-localization evidence
```

Rollback 절차:

1. 실패한 wave 이후의 후속 wave를 열지 않는다.
2. test code만 단독 복구하지 않고 해당 helper, taxonomy, source policy, required-validation, migration map을 같은 wave 경계로 되돌린다.
3. 기존 failed receipt, review 및 disposition evidence는 삭제하지 않고 superseded/rolled-back trace로 보존한다.
4. rollback된 exact subject에서 focused, exact current, configured current, identity reconciliation 및 no-mutation 검증을 다시 실행한다.
5. Type B rollback은 predecessor source file과 source-set count/hash를 함께 복구한다. `pytest.ini` ignore로 vanished source를 숨기지 않는다.
6. precision loss가 발생한 candidate는 `preserve_intentional_defense`, 증거가 부족하면 `defer_insufficient_evidence`, material gain이 없으면 `no_op_no_material_gain`으로 닫는다.
7. rollback validation command가 exit `0`이 아니면 복구 완료를 주장하지 않는다.
8. rollback으로 protection map, fault universe 또는 candidate domain이 바뀌면 기존 disposition을 재사용하지 않고 fault matrix를 다시 생성·freeze한 뒤 disposition을 재평가한다.
9. terminal Run A/B 이후 rollback 또는 tracked 변경이 발생하면 기존 terminal attestation, review와 owner seal은 predecessor evidence로만 보존하고 새 exact subject에서 세 절차를 다시 수행한다.
10. 실패하거나 superseded된 external terminal bundle은 append-only historical trace로 보존하고 새 `closure_id`/pointer/allocator receipt를 발급한다. Durable archive를 temporary cleanup 대상으로 삭제하지 않는다.

---

## 11. Governance Constraints

- `Philosophy.md`와 Iris의 근거 기반·중립적 정보 모드 경계를 유지한다.
- Pulse가 Iris를 참조하거나 의존하게 만들지 않으며 다른 spoke와의 직접 의존성을 추가하지 않는다.
- Iris runtime은 100% Lua로 유지한다. 본 계획은 JVM/Java/Mixin 또는 runtime Lua 변경을 도입하지 않는다.
- production behavior, runtime authority, public output 및 package identity를 변경하지 않는다.
- configured current, exact current, historical, diagnostic, required-validation을 서로 대체하지 않는다.
- raw diagnostic result와 terminal disposition을 분리하고 raw FAIL을 laundering하지 않는다.
- historical/predecessor/sealed evidence를 rewrite하지 않고 successor evidence를 additive하게 만든다.
- unexpected missing, unknown, unclassified, stale, dangling 및 dual binding은 fail-closed blocker다.
- skip/ignore/deselect 증가, route reclassification, parameterization-only 또는 subtest-only 변경을 감축으로 인정하지 않는다.
- test 삭제에는 `strong_dominance` 또는 `stronger_invariant` evidence가 필요하다.
- 실제 branch 실행 여부가 dominance에 materially 영향을 주는 candidate는 target-scoped coverage/equivalent trace를 요구하되 repository-wide coverage layer를 신설하지 않는다. Evidence가 없으면 삭제하지 않는다.
- supported API/protected compatibility와 historical/diagnostic test는 본 계획에서 preserve-only다.
- domain-local helper를 우선하고 범용 helper가 semantic policy나 authority를 소유하지 않게 한다.
- test-support LOC는 helper 이동분을 포함한다.
- 신규 plan-local supporting test의 configured discovery/classification decision과 test-support universe membership을 실측·확정한 뒤에만 accepted baseline을 동결한다.
- plan-local validator/test LOC와 file count는 보고 전용이며 test-support 감축과 상쇄하지 않고 post-closeout disposition을 함께 기록한다.
- 500+·1,000+ file bucket과 owner-ratified frozen-definition large-method count는 별도 completion axis이며 total LOC 감소로 대체하지 않는다.
- 모든 formal PASS는 exact command exit `0`과 evidence identity에 결속한다. tool 부재는 BLOCKED다.
- `EXECUTION_CONTRACT.md`의 `validated / out_of_scope / unvalidated_but_in_scope` ceiling을 closeout에 기록한다.
- `reduction_outcome=measured_no_op`은 정상적인 analysis/execution outcome이지만 roadmap의 감축 문제 해결은 아니다. 이는 top-level `partial`로만 닫고 `EXECUTION_CONTRACT.md`의 closeout state를 대체하거나 새 governance state를 만들지 않는다.
- `reduction_outcome=mixed_reduction`도 A1의 node/scenario/LOC/large-file/large-method 감축 조건을 모두 만족하지 않으면 top-level `partial`이다.
- reduction success 조건은 outcome classifier이며 safety/identity/precision fail-closed gate가 아니다. `a1_all_reduction_conditions_satisfied=false`라도 Change 8 Safety Exit Gate가 PASS하면 Change 9 terminal 절차를 생략하지 않는다.
- accepted baseline과 successor는 모두 `environment_class=clean_checkout_only`여야 하며 working-overlay와 clean-checkout denominator를 교차 비교하지 않는다.
- round-scoped plan-local validator와 transitive dependency는 exact terminal subject에 tracked되어 clean checkout에 존재해야 하지만 `gate_registered=false`인 module은 permanent full-repository dependency authority를 얻지 않는다.
- fault matrix는 protection map의 failure/fail-closed universe에서 omission 없이 파생하여 candidate disposition 전에 freeze한다.
- independent review는 exact successor artifact에 결속하며 plan/implementation 참여자가 수행하지 않는다.
- machine validation PASS, independent review PASS와 `owner_seal=granted`는 별개의 필수 축이며 어느 것도 다른 축을 대체하지 않는다.
- `machine_validation_manifest.json`은 owner seal의 비순환 machine-side predecessor이고 final `terminal_bundle_hash_manifest.json`와 동일 artifact가 아니다.
- tracked implementation, pre-terminal evidence, placement decision/pointer와 pending-only top-level 문서를 모두 동결한 뒤 exact terminal subject에서 Run A/B, independent review, owner seal 순으로 수행한다. 그 뒤 tracked tree가 바뀌면 predecessor PASS를 상속하지 않고 새 subject에서 terminal 절차를 전부 재실행한다.
- external terminal evidence는 owner-managed durable archive, append-only retention, tracked pointer와 tracked `validate_terminal_evidence_bundle.py@fresh-root-v1` producer의 fresh-root retrieval 검증을 모두 만족해야 하며 temporary output은 이를 대체하지 않는다.
- external durable bundle/pointer와 8개 validator는 이번 Heavy round에 한정된 evidence mechanism이다. Permanent gate 또는 repository-wide architecture로의 일반화는 이번 PASS 범위 밖이다.
- tracked top-doc의 `pending_terminal_validation`은 external final outcome을 복제하지 않는다. Downstream consumer는 `closure_id`/pointer로 bundle을 조회하며 별도 top-doc sync는 새 terminal subject를 요구한다.

---

## 12. Expected Closeout State

Expected closeout target: **complete**. 단, 이는 아래 `reduced` outcome과 모든 closure gate가 함께 성립할 때만 가능하다. 분석 및 구현 lifecycle의 정상 종료와 roadmap 감축 문제의 해결을 별도로 판정한다.

### Outcome 1 — Reduced

```text
reduction_outcome = reduced
a1_all_reduction_conditions_satisfied = true
pytest_node_count_final < pytest_node_count_baseline
removed_redundant_executed_scenario_count > 0
test_support_LOC_final < test_support_LOC_baseline
files_ge_500_final < files_ge_500_baseline
files_ge_1000_final < files_ge_1000_baseline
large_test_method_count_final < large_test_method_count_baseline
precision_regression = 0
```

Node, semantic scenario, executed case, input row, LOC, large-file bucket과 large-method delta는 각각 보고한다. `protected_contract_count`와 `protected_branch_count`는 감축 지표가 아니라 정밀도 보존 denominator이며 감소해서는 안 된다. Large-file/method threshold와 counting rule은 accepted baseline freeze 이후 변경할 수 없다.

### Outcome 2 — Mixed Reduction

```text
reduction_outcome = mixed_reduction
at_least_one_material_reduction_axis_improved = true
a1_all_reduction_conditions_satisfied = false
precision_regression = 0
top_level_closeout = partial
```

예를 들어 중복 scenario와 test-support LOC는 감소했지만 필요한 split으로 node 수가 baseline 이상인 경우다. 성과와 비용을 그대로 기록하되 `complete` 또는 roadmap 감축 성공으로 승격하지 않는다.

### Outcome 3 — Measured No-Op

```text
reduction_outcome = measured_no_op
all_candidates_dispositioned = true
safe_material_reduction_candidate_count = 0
a1_all_reduction_conditions_satisfied = false
precision_regression = 0
top_level_closeout = partial
```

이는 감축 quota를 맞추기 위해 정밀도를 약화하지 않았다는 evidence-bounded 분석 결과다. Mapping, disposition, validation, clean-checkout 재현과 review가 모두 끝나도 실제 감축이 없으므로 roadmap 문제는 해결되지 않았고 `complete`를 사용할 수 없다.

### Complete Gate

#### Baseline and source identity

- accepted exact baseline subject, `denominator_working_overlay`, `denominator_clean_checkout`과 모든 preservation denominator가 봉인됨
- before/after `environment_class_of_accepted_baseline=clean_checkout_only` 일치
- `new_test_source_collected_by_configured_discovery`와 conditional classification이 실측·기록되고 `new_test_source_registration_branch_consistent=true`, `baseline_frozen_after_plan_local_source_registration=true`
- `plan_local_validator_present_in_clean_checkout=true`, 8개 module + supporting test 1개의 `terminal_round_validator_closure_complete=true` 및 `gate_registered=true` 집합의 permanent dependency closure 일치

#### Measurement integrity

- source mutation과 parent/child cache residue가 없는 measurement path 확보
- large-file/method metric definition과 baseline member/hash가 고정되고 frozen selection rule을 final tree에 재적용한 after universe가 신규 helper/fixture 및 mandatory plan-local test를 포함해 양방향 reconciliation됨
- gross removals, localization splits와 net node delta가 분리 reconciliation됨
- `plan_local_validator_LOC`/`plan_local_validator_file_count`와 `post_closeout_disposition=retain_round_reproduction_evidence`가 보고되고 reduction metric과 상쇄되지 않음

#### Precision and authority

- protection-map failure/fail-closed universe와 fault matrix의 omission `0`, disposition 이전 freeze 및 frozen SHA-256 일치
- removal candidate 100% contract/dominance mapping, materially branch-dependent candidate의 `material_branch_evidence_gap=0`, 근거 없는 삭제 `0`
- exact-current / configured-current required validation PASS
- `historical_result_identity_matches_baseline=true`
- `diagnostic_raw_result_identity_matches_baseline=true`
- dangling/stale/dual binding `0`, fixed-domain precision regression `0`

#### Reduction classifier

- `a1_all_reduction_conditions_satisfied=true`, `reduction_outcome=reduced`
- node 감소, 중복 executed scenario 제거 `>0`, test-support LOC 감소, 500+·1,000+ file count 감소 및 frozen-definition large-method count 감소를 모두 만족

#### Terminal evidence

- `terminal_evidence_retrieval_capability_present=true`, tracked `<Git blob>:fresh-root-v1` identity와 positive/tamper capability tests PASS
- tracked implementation/evidence/docs가 포함된 exact terminal subject 동결 후 clean-checkout Run A/B canonical equality
- Run A/B 이후 terminal subject에 tracked 변경 `0`; 변경 시 새 subject에서 terminal validation 재실행
- independent review `Verdict=PASS`, P0/P1/P2/P3 `0`
- `machine_validation_manifest_valid=true`; producer가 tracked `validate_terminal_evidence_bundle.py@<Git blob>:fresh-root-v1`이며 manifest가 terminal attestation·constituent machine evidence와 exact terminal subject/pointer를 봉인하고 independent review가 이를 소비함
- `owner_seal=granted`, `terminal_subject == review_subject == owner_seal_subject`; owner seal이 machine manifest와 review SHA-256을 직접 참조함
- `terminal_evidence_placement=external_bundle`, owner custody/durability contract 및 tracked pointer 유효
- `terminal_bundle_hash_manifest.json`이 machine manifest/review/owner seal을 비순환 순서로 봉인하고 closeout receipt가 final manifest를 참조함
- fresh root의 `external_bundle_retrieval_verified=true`, `terminal_bundle_hash_manifest_valid=true`, `closeout_receipt_valid=true`; 세 값의 producer가 tracked `validate_terminal_evidence_bundle.py@<Git blob>:fresh-root-v1`과 일치

#### Closure and claim boundary

- top-doc은 `pending_terminal_validation`과 closure/pointer identity만 기록하고 final outcome은 같은 identity의 external terminal bundle에 결속됨
- validation ceiling과 non-claims가 closeout에 명시됨

다음 경우 expected state를 낮춘다.

- 구현은 끝났으나 required validation이 미실시이면 `implemented_only`
- `mixed_reduction`, `measured_no_op`, 일부 wave 또는 in-scope validation이 남으면 `partial`
- exact subject, required tool, clean-checkout current-round validator closure, external durable evidence custody/retrieval, eligible independent reviewer 또는 필수 owner seal이 없어 closure gate를 수행할 수 없으면 `blocked`

`a1_all_reduction_conditions_satisfied=false` 자체는 `blocked` 조건이 아니다. Change 8 Safety Exit Gate가 PASS하고 classifier가 완전하면 `mixed_reduction` 또는 `measured_no_op`으로 Change 9를 끝까지 수행한 뒤 `partial`로 닫는다. 반대로 safety/identity/custody/retrieval 같은 필수 closure gate를 수행할 수 없거나 실패한 경우에만 `blocked`를 사용한다.

Type B gate가 열리지 않아도 Type A가 A1의 모든 축을 충족하면 `complete`가 가능하다. 따라서 Type B 미승인 자체는 state를 낮추는 조건이 아니다.

최대 허용 claim:

```text
승인된 exact successor subject에서 Iris의 validation route, authority binding,
protected contract/partition/branch/fail-closed 책임과 적용 가능한 detection 및
failure localization을 보존하면서, 증명된 중복 test/scenario와 불필요한
test-support orchestration을 제거하여 node, 중복 executed scenario 및 test-support
LOC뿐 아니라 frozen 500+/1,000+ test-file 및 large-method concentration의 실제
감소를 모두 달성했다. 결과는 deterministic clean checkout에서 재현됐고
independent review와 owner seal이 동일 subject에 결속됐으며 owner-managed durable
bundle에서 tracked pointer로 재조회됐고 production/runtime/public output은 변경하지 않았다.
```

공통 non-claim: `test_support_LOC` 감소는 repository 전체 tracked LOC 또는 tracked Python LOC의 순감소를 의미하지 않는다. 이번 round의 8개 plan-local module과 supporting test 비용은 `plan_local_validator_LOC`/`plan_local_validator_file_count`로 별도 공개하며 감축값과 순상계하지 않는다. 이 tooling은 closeout 시 `retain_round_reproduction_evidence`이고, 향후 제거 여부는 별도 owner-approved successor에서만 판단한다.

`measured_no_op`의 최대 허용 claim은 "정밀도를 약화하지 않고 모든 후보를 disposition했으나 안전한 material reduction을 입증하지 못했다"이며, 위 `complete` claim을 사용할 수 없다.

이 closeout은 Iris release readiness, Workshop/B42/deployment readiness, runtime 성능 향상, 모든 historical/diagnostic 문제 해결, production architecture 개선 또는 외부 생태계 전체 호환성 보존을 의미하지 않는다.
