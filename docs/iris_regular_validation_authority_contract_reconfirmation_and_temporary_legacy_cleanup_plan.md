# Implementation Plan — Iris 정규 검증 authority 계약 재확정 및 임시·레거시 검증 정리

> 대상 모듈: Iris  
> 계획 기준일: 2026-08-22  
> 기준 roadmap: `ROADMAP — Iris 정규 검증 체계 계약 기준 재확정 및 임시·레거시 검증 정리`  
> Review revision: Cycle 1 RV-1~RV-4, Cycle 2 `evidence_only` sequencing 및 R2-N-01~R2-N-05, Cycle 3 R3-N-01~R3-N-02/R3-M-01 반영  
> 예상 검증 깊이: heavy  
> 예상 종료 상태: `complete` (단, §12의 fail-closed 조건 충족 시에만)

## 1. Objective

Iris의 executable validation unit을 실제 observable contract 기준으로 전수 조사하고, 현행 제품 계약·validation-system 계약·historical reproduction·diagnostic/evidence 역할을 서로 대체하지 않는 상태에서 정규 validation authority의 최종 구성과 근거를 재확정한다.

임시·일회성·migration·Legacy DVF·retired Stateful IAR 관련 validation은 이름이나 작성 시기가 아니라 실제 contract로 판정한다. 제거 후보가 unique current contract를 보유하면 current architecture에 맞는 successor regular verifier에서 먼저 보존하고, source·policy·taxonomy·manifest·entrypoint를 한 transaction으로 정렬한 뒤 predecessor를 제거한다.

완료 시 다음 질문에 contract 단위로 답할 수 있어야 한다.

- 어떤 validation unit이 current regular authority에 참여하는가.
- 각 unit은 어떤 입력에서 무엇을 관찰하고 어떤 실패를 의미하는가.
- historical/diagnostic/evidence unit이 current PASS를 대체하지 않는 이유는 무엇인가.
- 제거되거나 격리된 unit이 current contract를 잃지 않았다는 근거는 무엇인가.
- 실제 source set, classification, configured discovery, required manifest, canonical entrypoint가 어떻게 같은 최종 구성을 가리키는가.

---

## 2. Scope

조사와 disposition의 1급 단위는 executable validation unit이다.

- pytest/unittest test, parameterized case 및 subtest identity
- `Iris/_docs/round3/round3_run_contract_tests.py`가 선택하는 current/historical/diagnostic identity
- `Iris/validation/clean_checkout/`의 source census, collection, full-gate, comparator 및 관련 meta-validation
- `Iris/validation/baseline_admission/`의 별도 admission validation boundary
- `full_repository_gate.json`에 등록된 네 standalone validation command
- current gate나 별도 정규 route에 명시적으로 등록된 validator/evaluator/validation CLI
- 위 executable unit이 소비하는 fixture, helper, shared data, frozen input, manifest, policy, taxonomy, entrypoint 및 configuration
- ignored, dedicated-route, historical overlay, evidence-only, obsolete/misrouted로 분류된 source의 실제 reachability와 consumer 관계

Disposition vocabulary는 다음 exact token으로 봉인한다.

1. `regular_product_contract`
2. `regular_validation_system_contract`
3. `migrate_then_remove`
4. `reproduction_only`
5. `evidence_only`
6. `expired_or_duplicate_remove`
7. `needs_decision`

Support unit에는 위 authority disposition을 억지로 부여하지 않는다. 대신 consumer/dependency 상태를 `shared_current_support`, `historical_support`, `evidence_support`, `removal_candidate`, `non_validation_consumer_out_of_scope`, `unresolved_dependency`로 기록한다. 이는 authority 종류가 아니라 생존 executable consumer에 따른 lifecycle 상태다.

하나의 executable이 current, historical-only, expired contract를 함께 가질 수 있다. 이 경우 executable disposition은 최종 실행·물리 처리 역할 하나를 나타내고, 개별 contract row는 서로 다른 `contract_role`과 `preservation_target`을 가질 수 있다. 안전한 contract 분리나 surviving coverage를 확정할 수 없으면 executable을 `needs_decision`으로 두고 destructive 변경을 금지한다.

`evidence_only`에는 새 disposition을 추가하지 않되 `physical_preservation` 필드를 필수로 둔다.

- `executable_source`: regular registration 없이 source 자체를 provenance/reproduction material로 보존
- `sealed_artifact_only`: executable source는 제거하고 sealed receipt/provenance artifact만 보존

### Explicitly Out Of Scope

- Iris runtime Lua, Menu, Tooltip, Browser/Wiki/Detail 동작 변경
- Layer 3/4 의미, fact/evidence authority, KO/EN projection, current generation/pointer 변경
- DVF System, IAR, Registry Runtime Compatibility 또는 Publish 책임 경계 재설계
- retired Stateful IAR product architecture 복원
- 유지 test 병합, assertion style 통일 또는 test framework 교체
- scenario execution consolidation, producer sharing, subprocess 횟수 및 wall-time 최적화 재개방
- test count나 LOC 감소를 목표로 한 refactor
- 모든 build/producer/packaging script를 validation unit으로 간주하는 전수 tooling disposition
- `package_iris.ps1`, Lua syntax checker 등 비등록 product/tooling command의 authority 승격
- coverage metric 도입 또는 새로운 제품 contract/validation authority 종류 추가
- PZ 인게임 QA, multiplayer, 장시간 세션, 성능 benchmark, 외부 모드 호환성 sweep
- RTC, Publish, package, release, Workshop, B42 또는 deployment readiness 판정
- 기존 historical seal, predecessor receipt, evidence bundle 또는 pinned denominator 재작성
- unrelated repository/document cleanup 및 현재 worktree의 사용자 변경 정리

---

## 3. Non-Goals

- test 이름의 `legacy`, `round`, `migration`, `temporary` 표식을 제거 근거로 사용하지 않는다.
- current PASS/FAIL 하나만으로 contract의 currentness 또는 duplication을 판정하지 않는다.
- historical reproduction을 current suite에 흡수하거나 diagnostic finding을 current failure/PASS로 환산하지 않는다.
- predecessor 구현 구조나 legacy fixture를 successor current contract로 복제하지 않는다.
- regular suite가 Iris 제품 전체 correctness를 증명한다고 주장하지 않는다.
- 제거 전후 탐지 가능한 모든 잠재 regression 집합의 완전한 동일성이나 suite 성능 향상을 주장하지 않는다.
- one-off evaluator가 저장소에 존재한다는 이유만으로 regular authority를 부여하지 않는다.
- fail-closed source/denominator guard를 cleanup 편의를 위해 완화하거나 비활성화하지 않는다.

---

## 4. Assumptions

### Constitutional and Authority Assumptions

- `docs/Philosophy.md`가 최상위 설계 authority다. Iris는 근거 기반 정보 모드이며 PZ runtime은 100% Lua로 유지한다.
- `docs/DECISIONS.md`와 `docs/ARCHITECTURE.md`의 current readpoint를 따른다. Historical trace는 current authority를 대체하지 않는다.
- current/historical/diagnostic은 기존 responsibility axis다. 이 계획은 해당 axis를 재설계하거나 제4의 authority 종류를 만들지 않는다.
- Stateful IAR product architecture는 `FULL_RETIREMENT`, Layer 1–5 active product IAR consumer는 `0`이라는 current readpoint를 유지한다. 관련 validation은 이 사실만으로 제거하지 않는다.
- current Layer 3는 immutable generation과 single pointer를 사용하는 successor architecture다. Legacy DVF/IAR test에서는 retired structure requirement와 successor에도 유효한 invariant를 분리한다.

### Repository Observations at Planning Time

아래 수치는 계획 작성 시 working tree에서 읽은 구조 설명용 snapshot이며, 최종 denominator 목표가 아니다.

- `pytest.ini`는 `Iris/build/description/v2/tests`와 `Iris/build/tests/test_evidence_pipeline_cross_track.py`를 configured roots로 두고, legacy standalone 6개와 supporting-report 2개를 기본 discovery에서 ignore한다.
- `round3_test_taxonomy.json`은 593 identity / 231 source를 기록하며 `current=228`, `historical=285`, `diagnostic=80`이다.
- `round3_pytest_source_classification.json`은 reviewed 50, planned 14, mixed 2, additional 1, excluded 8 source를 관리한다.
- `current_route_required_validations.json`에는 156 required-test row가 있고 그중 155개가 `required=true`다. Historical optional override 76개가 current selection과 별도로 보존된다.
- `full_repository_gate.json` v7은 current/ok taxonomy, additional pytest source, explicit node identity, 네 standalone command, source disposition policy와 dependency policy를 결합한다.
- 현재 full gate source policy에는 explicit current-required 7, dedicated-route 18, explicit historical-optional 17, hermetic fixture 2, obsolete/misrouted source 3개가 존재한다.
- `round3_run_contract_tests.py`는 current/historical/diagnostic/all route를 분리하고 historical/diagnostic 실행 시 pinned reproduction overlay를 materialize한다.
- `run_iris_clean_checkout_validation.py`는 exact Git tree에서 census와 full gate를 실행하고 generated state를 repository 외부에 둔다. `validate_iris_clean_checkout_validation.py`는 Run A/B canonical raw-byte equality와 exact subject identity를 검증한다.
- 계획 작성 시 repository worktree에는 사용자 소유의 광범위한 수정·삭제·미추적 파일이 존재한다. 실행 baseline은 이 working tree를 암묵적으로 authority로 삼지 않고 owner가 선택한 exact tracked commit/tree에서 새로 고정해야 한다.

### Execution Decisions Resolving the Roadmap Holds

- **Proof standard:** `Proof A`를 채택한다. 모든 제거·migration 후보에 `(guarded surface, observable property, failure condition class, input partition)` contract trace를 요구한다. `migrate_then_remove`뿐 아니라 surviving verifier inclusion을 근거로 한 `expired_or_duplicate_remove`에서도 static full inclusion을 확정할 수 없으면 disposable checkout의 targeted defect injection을 removal prerequisite로 사용한다. `current contract 없음`이 입증된 expired 대상은 injection에서 제외한다. 모든 duplicate에 일률적인 injection framework를 만들지는 않는다.
- **Needs Decision closeout:** Option A를 채택한다. 각 residue에 `candidate_dispositions`와 후보별 영향 surface를 기록한다. 후보 집합에 `regular_product_contract`, `regular_validation_system_contract`, `migrate_then_remove` 또는 surviving-coverage 기반 `expired_or_duplicate_remove`가 포함되면 current/removal blocking으로 판정하며 `complete`를 금지한다. 이런 current/removal 후보가 있는 기존 current-route unresolved unit은 `unresolved_inherited_membership`으로 남긴다. 후보가 모두 `reproduction_only|evidence_only`이면 current authority 부재는 확정할 수 있지만, current membership 제거는 아래 pending-disposition source-policy landing이 합법적으로 봉인된 경우에만 수행한다.
- **Pending-disposition source-policy landing:** Change 1의 `disposition_contract.json`은 non-current-only unresolved unit이 착지할 exact existing policy class/token과 route mapping을 실행 전에 봉인한다. 이 착지는 disposition 확정이 아니라 `pending_disposition`이라는 임시 policy basis이며, (a) current discovery/required manifest에서 제외되고, (b) pinned historical corpus/overlay 의무를 발생시키지 않으며, (c) 후속 확정 시 `historical` 또는 `excluded`로 이동 가능하고, (d) source를 unclassified로 만들지 않아야 한다. 기존 `obsolete_or_misrouted` 계열을 재사용하면 ledger의 `policy_basis=pending_disposition`과 `semantic_disposition=needs_decision`으로 “obsolete”라는 의미론적 결론을 명시적으로 부인한다. 현행 schema/guard에서 이런 비확약적 착지를 새 authority 종류 없이 표현할 수 없으면 carve-out을 적용하지 않고 membership을 유지한 채 `unresolved_inherited_membership`으로 되돌리며 `complete`를 금지한다.
- **Support-unit model:** executable unit만 7개 disposition을 갖는다. Fixture/helper/config/manifest는 모든 consumer와 lifecycle 상태를 가져야 하지만 executable authority token은 갖지 않는다.
- **Full-gate cadence:** cadence B를 채택한다. Phase 5의 destructive/reclassification transaction 직후 Run A/B + comparator를 수행하고, Phase 6 최종 reconciliation 이후 exact final subject에서 다시 수행한다.
- **Vocabulary governance:** exact token과 route mapping은 disposition 전에 module-local contract로 봉인한다. Route semantics, authority ownership 또는 governing principle이 바뀌면 `docs/DECISIONS.md`에 compact decision을 추가하고 `docs/ARCHITECTURE.md`를 정합화한다. 같은 원칙 아래 source/test membership만 바뀌면 top-level 문서를 수정하지 않고 module-local `final_composition.json`과 실제 config를 durable readpoint로 삼는다.
- **Non-pytest scope:** current gate/manifest에 등록된 standalone command와 validation CLI는 disposition 대상이다. Lua syntax와 PowerShell package projection은 현재 regular authority에 등록된 경우에만 disposition하고, 그 외에는 변경된 소비자 경계의 조건부 compatibility check로만 다룬다.
- **Independent review:** 이 종합 검토는 작성 계보상 independent review credit으로 계산하지 않는다. Destructive Change 5 전에 roadmap/plan/disposition 구현에 관여하지 않은 eligible reviewer가 disposition, duplicate proof trigger, meta-validator semantic diff와 owner-action boundary를 검토해야 한다. Final reviewer gate는 P0/P1/P2/P3 모두 `0`이어야 하며, reviewer 부재 시 destructive execution과 `complete`는 `blocked`다.
- **Evidence location:** compact ledgers/contracts/closeout은 `Iris/_docs/round3/validation_contract_reconfirmation/`에 보존한다. 대형 collection, Run A/B, stdout/stderr 및 disposable evidence는 repository 외부 durable root에 두고 in-repo carrier에는 exact subject, SHA-256, schema와 claim boundary만 기록한다.
- **Atomic cleanup:** source removal, policy/taxonomy/manifest/denominator/entrypoint reconciliation과 전용 support cleanup은 동일 removal transaction에 포함한다.
- **Meta-validator approval:** 변경되는 meta-validator마다 predecessor→successor rule-level semantic diff를 기록하고 각 rule delta를 승인된 disposition row와 1:1로 결속한다. Approved disposition에 따라 declared validation universe membership/denominator 값이 감소하는 것은 허용된 data 변화다. 반면 declared final universe의 일부를 검사하지 않도록 guard coverage를 축소하거나 failure condition을 완화하거나 conditional bypass를 추가하는 것은 fail-closed semantic weakening으로 금지한다.
- **Owner writer boundary:** `scope_and_conflict_decisions.json`의 `full_repository_membership_with_owner_decision`과 해당 artifact의 `approved_by_owner` 계약에 따라 `Iris/validation/baseline_admission/authority/full_repository_test_membership_owner_decision.json` 및 관련 baseline-admission authority artifact를 owner-written으로 취급한다. Executor는 proposed delta와 근거만 생성하며 직접 수정하지 않는다. Writer census는 이 판정을 검증하는 evidence이지 authority를 덮어쓰는 도구가 아니다. Census가 계획의 판정과 충돌하면 current higher-authority 문서/owner decision이 우선하며 execution을 `blocked`로 멈추고 plan/owner action으로 충돌을 해소한다.
- **Route failure attribution:** baseline과 final의 historical/diagnostic identity 및 route-local result를 비교한다. Cleanup-attributable failure는 rollback과 `complete` 금지 사유다. Pre-existing/non-attributable failure는 route-local ceiling으로 기록하되 current closeout을 자동 하향하지 않는다. Attribution unknown은 attributable로 취급한다.
- **Valid-but-failing current contract:** contract currentness가 확정됐지만 baseline에서 제품 결함으로 실패하면 disposition은 `regular_product_contract`, `membership_confidence=confirmed_current`, `baseline_result=failing`, `failure_attribution=product_defect`로 분리 기록한다. 이번 closeout은 의도적으로 보수적인 기준을 사용하므로 required final full-gate가 PASS하지 않으면 `blocked`이며 `complete`로 닫지 않는다. 제품 코드는 이 cleanup 범위에서 수정하지 않고 별도 successor scope로 보내며, failure 발견을 이유로 cleanup scope를 확장하지 않는다. Currentness 또는 failure attribution 자체가 불명확할 때만 `needs_decision`을 사용한다.

---

## 5. Repository Areas Affected

### Code

- `Iris/build/description/v2/tests/test_*.py`
- `Iris/build/description/v2/tests/conftest.py`
- `Iris/build/tests/test_*.py`
- `Iris/build/test_require_render.py`
- `Iris/test/test_rightclick_pipeline.py`
- `Iris/_docs/round3/registry_runtime_compatibility/bootstrap/test_reserve_registry_runtime_compatibility_attempt.py`
- `Iris/_docs/round3/round3_run_contract_tests.py`
- `Iris/validation/clean_checkout/*.py`
- `Iris/validation/clean_checkout/tests/test_*.py`
- `Iris/validation/clean_checkout/*.ps1`
- `Iris/validation/baseline_admission/*.py`
- `Iris/validation/baseline_admission/tests/test_*.py`
- executable validation의 exclusive dependency로 확인된 `Iris/build/description/v2/tools/build/*.py` 및 fixture/helper

위 경로는 조사 universe다. 실제 수정·삭제는 ledger에서 disposition과 consumer census가 확정된 파일에 한정한다.

### Docs

- `docs/DECISIONS.md` — route semantics, authority ownership 또는 governing principle 변경 시에만 compact decision 추가
- `docs/ARCHITECTURE.md` — 위 architecture/governance 의미가 변경될 때만 최소 정합화; membership-only delta는 module-local/config에 보존
- `docs/ARCHITECTURE.md` §8-13/§8-15 — current readpoint identity supersession 판정 대상; owner가 별도 갱신을 결정하기 전에는 read-only 비교 대상
- `docs/ROADMAP.md` §16 — current result identity supersession 판정 대상; 갱신 여부는 owner 결정이고 closeout은 disclosure만 수행
- `Iris/_docs/round3/round3_taxonomy_routing_map.md`
- `Iris/_docs/round3/round3_taxonomy_matrix.md`
- `Iris/_docs/round3/round3_d3_historical_preservation_policy.json`
- 신규 `Iris/_docs/round3/validation_contract_reconfirmation/`

### Config

- `pytest.ini`
- `Iris/_docs/round3/round3_test_taxonomy.json`
- `Iris/_docs/round3/round3_pytest_source_classification.json`
- `Iris/_docs/round3/round3_full_discovery_denominator.json`
- `Iris/_docs/round3/current_route_required_validations.json`
- `Iris/validation/clean_checkout/contracts/canonical_gate.json`
- `Iris/validation/clean_checkout/contracts/full_repository_gate.json`
- `Iris/validation/baseline_admission/authority/full_repository_test_membership_owner_decision.json` — owner-written/read-only input; executor는 proposed delta만 작성
- `Iris/validation/baseline_admission/authority/scope_and_conflict_decisions.json` — owner-written scope lock/read-only input
- executable/support dependency를 직접 등록한 관련 manifest와 schema

### Generated Artifacts

- `Iris/_docs/round3/validation_contract_reconfirmation/disposition_contract.json`
- `Iris/_docs/round3/validation_contract_reconfirmation/validation_unit_inventory.jsonl`
- `Iris/_docs/round3/validation_contract_reconfirmation/support_dependency_inventory.jsonl`
- `Iris/_docs/round3/validation_contract_reconfirmation/contract_ledger.jsonl`
- `Iris/_docs/round3/validation_contract_reconfirmation/disposition_ledger.jsonl`
- `Iris/_docs/round3/validation_contract_reconfirmation/migration_coverage.jsonl`
- `Iris/_docs/round3/validation_contract_reconfirmation/duplicate_inclusion_proof.jsonl`
- `Iris/_docs/round3/validation_contract_reconfirmation/contract_row_preservation_receipts.jsonl`
- `Iris/_docs/round3/validation_contract_reconfirmation/meta_validator_rule_diff.jsonl`
- `Iris/_docs/round3/validation_contract_reconfirmation/owner_action_proposal.json`
- `Iris/_docs/round3/validation_contract_reconfirmation/route_failure_attribution.json`
- `Iris/_docs/round3/validation_contract_reconfirmation/removal_transaction.json`
- `Iris/_docs/round3/validation_contract_reconfirmation/final_composition.json`
- `Iris/_docs/round3/validation_contract_reconfirmation/independent_review.json` — exact validated subject를 검토하는 post-validation evidence carrier
- `Iris/_docs/round3/validation_contract_reconfirmation/readpoint_supersession_disclosure.json` — top-level current readpoint supersession 판정과 owner-action disclosure
- `Iris/_docs/round3/validation_contract_reconfirmation/closeout.json` — validated subject를 재정의하지 않는 post-validation closeout carrier
- repository-external source census, collection receipts, focused proof receipts, canonical Run A/B results와 comparator receipt

기존 sealed evidence, historical corpus, predecessor receipt와 current product artifact는 regenerated artifact가 아니다.

---

## 6. Planned Changes

### Change 1 — Execution constitution, exact baseline and meta-validator pin

Purpose:

Disposition이 시작되기 전에 exact subject, vocabulary, route mapping, proof/closeout rule과 판정 도구의 predecessor identity를 고정한다.

Files:

- 신규 `Iris/_docs/round3/validation_contract_reconfirmation/disposition_contract.json`
- 신규 baseline/meta-validator identity carrier
- 신규 `meta_validator_rule_diff.jsonl`
- 신규 `owner_action_proposal.json`
- repository-external baseline current/historical/diagnostic result receipts
- 필요 시 `docs/DECISIONS.md`

Implementation Notes:

- owner-selected clean tracked commit/tree를 baseline으로 기록한다. Planning snapshot count를 baseline denominator로 복사하지 않는다.
- Change 1에서는 `meta_validator_rule_diff.jsonl`, `owner_action_proposal.json` 등 후속 결과 artifact의 schema, empty carrier와 writer rule만 만든다. 실제 delta/content는 해당 변경이 확정되는 Change 3~6에서 population하고 exact producing transaction을 기록한다.
- taxonomy, source policy, denominator, required manifest, canonical/full gate, runner, clean-checkout runner/comparator, pytest `conftest.py`의 path/blob/SHA-256를 pin한다.
- 7개 disposition token의 정의와 current/historical/diagnostic route mapping을 봉인한다.
- non-current-only unresolved unit용 `pending_disposition_policy_landing`을 `availability`, exact existing policy class/token, `policy_basis=pending_disposition`, current discovery/required exclusion, historical pinned-corpus non-trigger, 허용 successor transition(`historical|excluded`)과 guard/schema compatibility로 봉인한다. 이는 새 disposition이나 제4의 authority category가 아니다.
- 현행 source-policy schema와 fail-closed guard가 위 착지를 의미 왜곡 없이 표현하지 못하면 `availability=false`, `fallback=retain_unresolved_inherited_membership`을 봉인한다. `obsolete_or_misrouted` 계열 재사용 시에도 ledger가 `semantic_disposition=needs_decision`을 유지하고 obsolete 판정을 부인해야 한다.
- support lifecycle 상태가 authority disposition이 아님을 명시한다.
- meta-validator 변경 transaction과 일반 validation disposition transaction을 분리한다.
- changed meta-validator의 자기 PASS는 자기 변경 승인 근거로 단독 사용하지 않는다.
- baseline current/historical/diagnostic route의 identity set, result와 pre-existing failure를 exact subject에 결속해 final attribution 기준으로 삼는다.
- baseline-admission authority artifact의 schema/consumer/last-writer와 existing authority 문서를 확인해 owner-written/executor-writable 경계를 writer census에 기록한다. 현재 계획상 `full_repository_test_membership_owner_decision.json`과 `scope_and_conflict_decisions.json`은 owner-written/read-only다. Census가 이 판정과 충돌하면 스스로 재분류하지 않고 higher-authority/owner 확인 전 `blocked`다.
- meta-validator 변경 후보가 생기면 rule을 검사 대상 집합, observable, failure condition, bypass/exception으로 정규화해 predecessor→successor semantic diff를 작성하고 disposition row와 1:1 binding한다.
- denominator 값·membership data 변화는 rule weakening과 별도로 기록한다.

Validation:

- exact commit/tree와 모든 pinned path 존재 및 blob identity 확인
- contract schema/required field/unique token validation
- pending-disposition landing이 available이면 네 가지 조건(current/required 제외, historical corpus non-trigger, historical/excluded 전이 가능, unclassified 방지)과 기존 guard 수용을 검증하고, unavailable이면 inherited-membership fallback이 유일한 허용 경로인지 검증
- planning worktree residue가 baseline input으로 섞이지 않았는지 확인
- baseline route result와 identity receipt 생성 및 hash binding
- owner-written artifact에 executor write가 없는지 확인
- independent reviewer가 meta-validator diff schema와 non-weakening rule을 승인

---

### Change 2 — Validation universe and support dependency census

Purpose:

파일 수가 아니라 executable identity와 실제 execution reachability를 기준으로 전체 validation universe를 확정한다.

Files:

- `pytest.ini`
- `Iris/build/description/v2/tests/conftest.py`
- `Iris/_docs/round3/round3_run_contract_tests.py`
- `Iris/_docs/round3/round3_test_taxonomy.json`
- `Iris/_docs/round3/round3_pytest_source_classification.json`
- `Iris/_docs/round3/current_route_required_validations.json`
- `Iris/validation/clean_checkout/contracts/{canonical_gate.json,full_repository_gate.json}`
- `Iris/validation/clean_checkout/run_iris_clean_checkout_validation.py`
- `Iris/validation/clean_checkout/inventory_iris_offline_tooling.py`
- 신규 inventory artifacts

Implementation Notes:

- static AST/source census와 actual collection census를 모두 사용한다.
- test file/class/function, parameterized/subtest, explicit node ID, standalone command ID를 stable validation identity로 기록한다.
- identity마다 configured discovery, taxonomy class/state, source policy, required manifest membership, dedicated route, canonical/full gate, standalone registration을 기록한다.
- ignored/excluded/optional/historical source도 실제 import와 entrypoint consumer를 조사한다.
- dynamic import, `importlib`, string-assembled path, subprocess command, historical overlay materialization은 별도 reachability note를 가진다.
- support unit은 executable consumer ID 전체, product/tooling consumer 유무, write surface, frozen/sealed 여부를 기록한다.
- 네 full-gate standalone command는 pytest source와 별도의 executable family로 inventory한다.
- package projection과 Lua syntax command는 등록 관계를 조사하되 미등록이면 authority disposition universe로 승격하지 않는다.
- baseline에서 이미 실패하는 executable은 `failure_at_baseline=true`와 contract currentness를 별도로 기록한다. Current contract가 유효하면 자동 expired 처리하지 않는다.

Validation:

- executable identity 미inventory `0`, duplicate identity `0`
- actual tracked source ↔ source policy bidirectional equality
- taxonomy ID/source ↔ collected identity cross-check
- required manifest target와 standalone path 존재 확인
- 동일 subject census 2회 raw-byte 또는 canonical semantic identity 재현
- support consumer가 없는 것으로 판정된 unit에 대해 static reference/import scan
- baseline route failure inventory의 identity와 result 재현

---

### Change 3 — Actual contract extraction and disposition

Purpose:

각 executable unit이 실제로 보장하는 contract와 최종 authority 역할을 확정한다.

Files:

- inventory에 포함된 executable source
- 신규 `contract_ledger.jsonl`
- 신규 `disposition_ledger.jsonl`
- 신규 `support_dependency_inventory.jsonl`

Implementation Notes:

각 executable identity에 최소 다음 필드를 기록한다.

- stable identity와 source blob
- execution route와 authority source
- input/prerequisite 및 input partition
- guarded surface
- observable property
- assertion/failure condition class
- failure가 의미하는 contract와 claim ceiling
- current product, validation-system, historical, diagnostic/evidence 관계
- fixture/helper/artifact/entrypoint dependency
- overlap, inclusion, supersession 후보와 근거
- exact disposition token 및 reviewer rationale
- contract별 `contract_role`, `preservation_target`과 successor/historical owner
- `candidate_dispositions` 및 각 후보의 current/removal 영향
- 기존 current membership이면 `membership_confidence=confirmed_current|unresolved_inherited_membership`
- current discovery/required authority의 baseline membership과 `target_regular_membership=true|false`
- `evidence_only`이면 `physical_preservation=executable_source|sealed_artifact_only`
- baseline failure 여부와 product-defect/validation-defect/unknown attribution

한 test가 여러 contract를 보장하면 contract row를 분리하되 executable disposition은 하나만 갖는다. Contract row는 서로 다른 successor 또는 historical/evidence 보존 대상을 가질 수 있다. 안전한 분리나 단일 executable disposition을 확정하지 못하면 `needs_decision`으로 둔다. 여러 test가 같은 contract를 보장하면 partial overlap과 full inclusion을 구분한다.

Legacy DVF/IAR 관련 unit은 다음을 명시적으로 분리한다.

- retired implementation 존재를 강제하는 expired contract
- immutable generation/pointer, stale-predecessor rejection, fail-closed identity 등 successor에도 유효한 invariant
- historical reproduction 전용 contract
- provenance/evidence만 남은 실행 흔적

Validation:

- executable identity 대비 contract mapping coverage 100%
- executable disposition 미배정 `0`, 다중 disposition `0`
- `expired_or_duplicate_remove`마다 current contract 없음 또는 surviving verifier의 full inclusion 근거 존재
- surviving verifier inclusion이 static proof로 확정되지 않으면 targeted defect-injection prerequisite 표시
- `reproduction_only`마다 pinned historical owner/route/corpus 존재
- `evidence_only`마다 contract currentness와 evidence/provenance-only 역할, 현재 regular discovery/required authority membership, `target_regular_membership=false` 및 physical preservation 형식을 기록한다. 현재 regular membership 존재는 disposition failure가 아니라 Change 5 cleanup input이다.
- `needs_decision`은 숨기거나 다른 category로 강제 이동하지 않으며 candidate disposition 기반 blocking 여부를 기록한다. Candidate가 모두 `reproduction_only|evidence_only`이면 current authority 부재와 pending-disposition landing 적용 자격을 기록한다. 실제 current membership 제거는 Change 1에서 `pending_disposition_policy_landing.availability=true`로 봉인된 경우에만 확정 대상으로 표시한다. Landing이 없거나 current 후보가 하나라도 있으면 membership을 `unresolved_inherited_membership`으로 유지하고 변경을 금지한다.
- current-valid baseline product failure는 `regular_product_contract`/`confirmed_current`와 failing result를 분리 기록하고 별도 successor scope로 보낸다. Product code를 수정하지 않으며 required final PASS를 우회하지 않는다.
- independent reviewer의 P0/P1/P2/P3 finding `0` 또는 수정 후 재검토

---

### Change 4 — Unique current contract migration

Purpose:

`migrate_then_remove` predecessor가 가진 unique current contract를 current architecture의 successor regular verifier로 먼저 이전한다.

Files:

- ledger에서 승인된 successor test source
- 필요한 current fixture/helper
- 신규 `migration_coverage.jsonl`

Implementation Notes:

- 각 row에 `predecessor identity -> contract identity -> successor identity` trace를 기록한다.
- assertion 문구가 아니라 guarded surface, observable, failure class, input partition과 fail-closed semantics를 보존한다.
- retired Stateful IAR descriptor/statefulness나 Legacy DVF combined-route 구조를 successor에 복제하지 않는다.
- successor는 current immutable generation/pointer, current manifest/route vocabulary 등 실제 successor surface를 검증한다.
- predecessor removal 전 successor가 regular route에 수집되고 focused validation에서 positive path를 통과해야 한다.
- 정적 trace로 failure semantics equivalence를 확정할 수 없으면 disposable checkout에서 targeted defect를 주입하고 successor의 예상 failure를 확인한다.
- migration이 새로운 제품 contract나 validation authority를 추가하지 않는지 검토한다.

Validation:

- migration row 누락 `0`
- predecessor 제거 전 successor collection/route/required membership 확인
- focused positive/negative validation exit `0`
- 필요한 targeted defect-injection receipt와 expected failure-class 일치
- source checkout mutation `0`

---

### Change 5 — Atomic temporary/legacy removal and isolation

Purpose:

regular authority가 없는 validation과 exclusive support residue를 disposition대로 제거·격리하고, source tree와 configuration을 한 transaction으로 일치시킨다.

Files:

- 승인된 predecessor/duplicate/expired test source
- predecessor-only fixture/helper/config
- `pytest.ini`
- taxonomy/source-policy/denominator/required manifest
- canonical/full gate 및 standalone registration
- historical reproduction manifest/overlay mapping
- 신규 `removal_transaction.json`

Implementation Notes:

- `expired_or_duplicate_remove`: `current contract 없음`이 입증된 expired source 또는 surviving verifier가 full inclusion을 보장하는 duplicate source와 exclusive support만 제거한다.
- `migrate_then_remove`: successor coverage receipt 확인 후 predecessor와 predecessor-only support를 제거한다.
- `reproduction_only`: current discovery/required gate에서 제외하되 pinned historical route와 corpus에 보존한다.
- `evidence_only`: `physical_preservation=executable_source`이면 regular registration만 제거하고 source를 보존한다. `sealed_artifact_only`이면 executable source를 제거하고 hash-bound provenance/receipt를 보존한다.
- `needs_decision`: source/artifact 삭제나 contract-row pruning은 하지 않는다. `candidate_dispositions`가 모두 `reproduction_only|evidence_only`이고 Change 1에서 비확약적 pending-disposition landing이 available로 봉인된 경우에만 independent review 후 current discovery/required membership 제거, exact policy landing 부여, source/evidence 보존을 하나의 atomic transaction으로 수행한다. Landing은 최종 `historical`/`excluded` disposition을 선점하지 않으며 historical pinned corpus 의무도 만들지 않는다. Landing이 unavailable이거나 current 후보가 하나라도 있으면 membership을 `unresolved_inherited_membership`으로 유지하고 destructive 변경을 하지 않는다.
- surviving verifier inclusion을 removal reason으로 사용하는 duplicate는 static full inclusion proof를 기록한다. Input partition 또는 failure branch inclusion이 불확실하면 targeted defect injection이 PASS하기 전 제거하지 않는다.
- Mixed-contract executable을 split/remove/isolate하기 전에 모든 contract row의 `preservation_target`을 실제 successor identity, historical route/corpus 또는 hash-bound evidence artifact에 연결하고 `contract_row_preservation_receipts.jsonl`에 충족 receipt를 남긴다. Receipt가 없는 contract row가 하나라도 있으면 제거하지 않는다.
- support unit은 surviving regular, historical, evidence, product/tooling consumer를 모두 확인한 뒤에만 제거한다.
- source deletion과 policy membership, taxonomy identity, configured/exact denominator, required manifest, entrypoint/config를 동일 commit에 정렬한다.
- fail-closed collection/source guard가 막으면 guard를 완화하지 않고 transaction 구성을 수정한다.
- historical pinned denominator와 predecessor seal은 successor current denominator로 덮어쓰지 않는다.
- owner-written baseline-admission authority artifact 변경이 필요하면 executor transaction에는 source/config proposed delta만 포함하고 `owner_action_proposal.json`을 생성한다. Owner가 별도 action으로 authority artifact를 승인하기 전 membership change는 발효되지 않으며 transaction은 destructive 실행 전에 `blocked`다.
- Change 5 terminal historical/diagnostic result를 baseline과 비교해 cleanup-attributable, pre-existing/non-attributable, unknown으로 분류한다. Unknown은 attributable로 처리한다.

Validation:

- dead reference/import/path scan
- source-policy bidirectional equality와 no unclassified/conflicting source
- pending-disposition landing을 적용한 모든 source의 `policy_basis=pending_disposition`, current discovery/required absence, historical pinned-corpus non-trigger와 허용 successor transition 확인
- manifest target existence와 collection census
- support consumer census 및 orphan support `0`
- duplicate inclusion proof completeness와 required targeted defect-injection PASS
- mixed-contract row preservation target receipt 누락 `0`; evidence artifact path/hash 존재 확인
- `evidence_only`와 landing이 적용된 non-current-only unresolved unit의 final regular discovery/required authority absence; landing unavailable fallback unit은 inherited membership과 blocking residue로 명시
- historical route의 pinned input/hash와 expected identity 보존
- historical/diagnostic baseline-to-terminal attribution 완료; attributable/unknown regression `0`
- owner-required membership delta가 있으면 owner action 및 adopted artifact identity 확인
- Phase 5 terminal subject에서 clean-checkout full Run A/B, four standalone command, deterministic comparator exit `0`
- Run A/B canonical raw-byte equality, source checkout mutation `0`, cleanup PASS

---

### Change 6 — Final composition verification and conditional atomic successor reconciliation

Purpose:

Change 5의 atomic transaction 결과가 모든 실행·분류 surface와 일치하는지 우선 read-only로 검증한다. 불일치 교정이 필요할 때만 별도의 atomic successor transaction으로 전체 관련 surface를 다시 정렬한다.

Files:

- `pytest.ini`
- `round3_test_taxonomy.json`
- `round3_pytest_source_classification.json`
- `round3_full_discovery_denominator.json`
- `current_route_required_validations.json`
- `round3_run_contract_tests.py`
- `canonical_gate.json`
- `full_repository_gate.json`
- `full_repository_test_membership_owner_decision.json` — read-only owner input 또는 owner가 별도 채택한 successor
- 관련 taxonomy/routing docs
- 신규 `final_composition.json`

Implementation Notes:

최종 identity chain을 다음과 같이 기록하고 각 단계의 set equality를 검증한다.

```text
actual executable source/identity set
-> source classification and taxonomy
-> configured discovery
-> required/dedicated/historical/diagnostic route
-> canonical and full-repository entrypoint
```

- count equality만으로 통과하지 않고 source path, node ID, command ID identity를 비교한다.
- current taxonomy와 required manifest의 역할 차이를 유지한다. Manifest subset/override와 taxonomy route를 하나의 수치로 혼합하지 않는다.
- historical optional override와 diagnostic route는 current denominator 밖의 소유권을 명시한다.
- one-off/evidence-only script가 required list에 남지 않았는지 확인한다.
- pending-disposition landing이 적용된 source는 exact sealed policy class와 `policy_basis=pending_disposition`을 가지며 current discovery/required route와 historical pinned corpus 어느 쪽에도 포함되지 않는지 확인한다. Landing unavailable fallback은 `unresolved_inherited_membership`과 blocking residue로만 남기며 unclassified 상태를 허용하지 않는다.
- Change 6은 기본적으로 validation/record-only다. Source/config mismatch가 발견되면 ad hoc 파일 한두 개만 수정하지 않고 source, policy, taxonomy, denominator, manifest와 entrypoint를 포함한 별도 atomic successor transaction을 연다. 그 transaction 뒤 focused validation과 final full gate를 다시 실행한다.
- meta-validator 변경은 predecessor→successor rule-level semantic diff, disposition row 1:1 binding과 독립 review로 검증한다. Approved disposition에 따른 declared membership 감소는 허용하되, declared final universe에 대한 guard coverage 누락, failure condition 완화 또는 conditional bypass 추가가 `0`이어야 한다.
- 최종 denominator는 execution subject에서 재산출하고 planning snapshot 또는 historical sealed count를 목표값으로 강제하지 않는다.
- baseline-admission owner decision 변경이 필요하면 executor는 proposal만 제시한다. Owner-written successor와 exact adoption identity가 없으면 final membership reconciliation은 `blocked`다.
- Route semantics, authority ownership 또는 governing principle이 달라지면 `DECISIONS.md`와 `ARCHITECTURE.md`를 같은 successor transaction 또는 owner-approved 후속 documentation transaction에서 정합화한다. 같은 원칙 아래 membership만 달라지면 top-level docs를 수정하지 않고 module-local `final_composition.json`과 config에 durable readpoint를 남긴다.

Validation:

- unclassified source `0`, conflicting classification `0`, missing manifest target `0`
- executable disposition coverage 100%, support consumer accounting 100%
- current/historical/diagnostic/dedicated/standalone route별 identity set 기록
- `target_regular_membership=false`인 `evidence_only`와 landing 적용 non-current-only unresolved unit의 regular discovery/required authority absence; landing fallback unit의 inherited membership/blocking 표기 일치
- configured discovery와 canonical/full gate selection parity
- denominator 및 dependency inventory deterministic regeneration
- stale predecessor path와 removed ID reference `0`
- meta-validator rule delta의 disposition binding 누락 `0`, fail-closed weakening `0`
- owner-required delta 미채택 `0`

---

### Change 7 — Final exact-subject validation, independent review and closeout

Purpose:

최종 tracked subject에서 contract preservation과 authority composition의 실행 가능성을 검증하고 claim boundary를 닫는다.

Files:

- repository-external Run A/B 및 comparator evidence
- 신규 `independent_review.json`
- 신규 `readpoint_supersession_disclosure.json`
- 신규 `closeout.json`
- 필요 시 compact current docs update

Implementation Notes:

- 이전 subject의 PASS나 Phase 5 결과를 final subject에 자동 승계하지 않는다.
- exact validated subject는 clean tracked terminal commit/tree여야 하며 runner/comparator도 그 subject blob과 일치해야 한다.
- 실행 순서와 identity 경계를 다음처럼 유지한다.

```text
exact validated subject
-> Run A/B + comparator + exact-subject independent review
-> post-validation evidence / closeout carrier
```

- Run A/B/comparator result와 independent reviewer 판정은 모두 같은 exact validated subject의 commit/tree 및 relevant blob identity에 결속한다. `independent_review.json`, `readpoint_supersession_disclosure.json`, `closeout.json`을 추가하는 후속 carrier commit은 validated subject를 hash-bound pointer로 참조할 뿐 validated terminal subject, product authority 또는 validation PASS의 귀속 대상을 재정의하지 않는다.
- Post-validation carrier transaction에는 evidence pointer/summary 외 source, policy, taxonomy, manifest, denominator, entrypoint, runner/comparator 또는 product artifact 변경을 포함하지 않는다. 그런 변경이 하나라도 필요하면 기존 subject는 final이 아니므로 새 validated subject를 만들고 Run A/B, comparator와 independent review를 다시 수행한다.
- applicable historical reproduction은 별도 route semantics로 실행한다. Diagnostic route도 advisory semantics를 유지한다.
- baseline과 final historical/diagnostic identity 및 result를 비교한다. Cleanup-attributable failure는 rollback하고 `complete`를 금지한다. Pre-existing/non-attributable failure는 route-local result와 ceiling을 기록하되 current closeout state를 자동 하향하지 않는다. Attribution unknown은 attributable로 처리한다.
- current-valid baseline product failure가 남으면 `regular_product_contract`, `confirmed_current`, failing result와 successor scope를 기록하며 final PASS 또는 `complete`로 우회하지 않는다. Currentness/attribution이 불명확한 경우에만 `needs_decision`을 사용한다.
- independent reviewer는 disposition completeness, duplicate inclusion proof, unique current coverage, support cleanup, meta-validator rule-level diff/non-weakening, owner-action boundary, route failure attribution과 claim ceiling을 검토한다.
- large run evidence는 external durable root에 보존하고 closeout에는 hash-bound pointer만 기록한다.
- `membership_confidence`, candidate disposition과 inherited-membership 상세는 module ledger/final composition에만 둔다. `closeout.json`은 새 closeout taxonomy field를 만들지 않고 해당 artifact의 path/SHA-256와 요약 count만 참조한다.
- `readpoint_supersession_disclosure.json`은 `docs/ARCHITECTURE.md` §8-13/§8-15와 `docs/ROADMAP.md` §16에 기록된 current subject/result identity가 이번 execution으로 superseded되는지를 문서별로 판정하고, 비교한 predecessor identity, validated successor identity, `superseded=true|false`, 근거와 `owner_action_required`를 기록한다. `closeout.json`은 이 artifact의 path/SHA-256와 판정 요약을 포함한다.
- 위 disclosure는 `EXECUTION_CONTRACT.md` §7-3의 task-specific 적용이다. Top-level readpoint 갱신 여부와 시점은 owner 결정이며 post-validation closeout carrier가 해당 문서를 자동 수정하거나 sealed/current authority를 자동 채택하지 않는다.

Validation:

- focused migrated-contract tests
- current regular route와 validation-system meta-tests
- applicable historical reproduction route
- diagnostic route의 기존 status/claim semantics 확인
- baseline-to-final route failure attribution 및 unknown `0`
- changed Python source import/compile 및 focused pytest
- exact validated subject clean-checkout full Run A/B + four standalone validations + comparator
- collection/taxonomy/manifest/route identity and denominator check
- source checkout tracked/untracked mutation `0`, external execution cleanup PASS
- independent reviewer P0/P1/P2/P3 `0`
- independent review와 closeout의 validated-subject pointer가 Run A/B/comparator exact subject와 일치하고 post-validation carrier의 authority redefinition `0`
- top-level readpoint supersession disclosure 누락 `0`; owner 결정이 필요한 경우 미공개 owner action `0`

---

## 7. Validation Plan

### Automated Validation

Execution owner는 각 명령의 exact arguments, exit code, subject commit/tree, output SHA-256를 receipt에 기록한다. Python 명령은 repository 지침에 따라 `uv run python ...` 형태로 실행한다.

1. Inventory/collection

   - `uv run python Iris/validation/clean_checkout/run_iris_clean_checkout_validation.py source-census --repo <repo> --commit <subject> --output-root <external-root> --full-repository`
   - `uv run python -m pytest --collect-only --round3-contract all --round3-enforce-denominator -p no:cacheprovider`
   - `uv run python Iris/_docs/round3/round3_run_contract_tests.py --class current`
   - route별 current/historical/diagnostic collection identity 비교

2. Focused contract/migration checks

   - 변경된 test source의 pytest node/family
   - changed clean-checkout/meta-validation tests
   - successor positive/negative case와 필요한 targeted defect-injection
   - surviving-verifier inclusion 제거의 static full-inclusion proof; 불확실한 input partition/failure branch의 targeted defect-injection
   - `uv run python`을 사용한 registered standalone validator/CLI focused execution

3. Structural integrity

   - source-policy/taxonomy/manifest/denominator schema와 set-equality validator
   - AST/import/reference/dependency scan
   - historical overlay manifest/hash/corpus validation
   - stale source, node ID, command path와 orphan support scan
   - every mixed-contract row의 successor/historical/evidence preservation receipt와 target path/hash 검증
   - same-subject inventory deterministic comparison
   - meta-validator predecessor/successor rule-level semantic diff, disposition 1:1 binding과 fail-closed non-weakening check
   - owner-written authority artifact write scan과 adopted owner-action identity check
   - baseline/final historical·diagnostic result attribution comparator

4. Full authority gate — cadence B

   - Phase 5 removal transaction subject: `invoke_receipt_bound_full_gate.ps1`로 independent external checkout Run A/B 실행
   - `invoke_deterministic_compare.ps1`로 canonical raw-byte equality 및 exact subject binding 검증
   - Phase 6 reconciliation 이후 exact validated subject에서 동일 chain 재실행
   - 각 run에서 current pytest identity, four standalone command, dependency inventory, source mutation, external cleanup 결과 확인
   - 동일 subject에 대한 comparator PASS 뒤 independent review를 완료하고, post-validation carrier는 해당 subject/hash만 참조하는지 검증

5. Repository-prescribed conditional checks

   - Lua 파일을 변경하지 않으므로 기본 계획에는 인게임/Lua syntax gate를 추가하지 않는다. 예상 밖 Lua 변경이 발생하면 `powershell -ExecutionPolicy Bypass -File .\tools\check_lua_syntax.ps1`이 exit `0`이어야 한다.
   - PowerShell entrypoint를 변경하면 관련 Pester/fixture가 없더라도 해당 script의 positive/negative focused invocation과 full gate를 모두 수행한다.

PASS는 exact relevant command가 exit `0`일 때만 주장한다. `uv`, Python, PowerShell 또는 clean-checkout 환경 등 required tooling이 없으면 validation은 PASS가 아니라 `BLOCKED`다.

### Manual Validation

- disposition ledger의 contract tuple과 source assertion을 대조한다.
- duplicate/full inclusion 판정에서 partial overlap 및 unique failure branch 손실 여부를 표본이 아니라 removal 전 항목 전수로 검토한다.
- Change 3에서는 `evidence_only`의 baseline membership과 non-regular target을 검토하고, Change 5/6에서만 final membership absence를 승인한다.
- support unit의 모든 consumer와 sealed/historical 역할을 검토한다.
- current/historical/diagnostic/evidence claim 문구가 서로의 authority를 대체하지 않는지 확인한다.
- independent reviewer가 duplicate proof trigger, meta-validator rule diff/non-weakening, owner writer boundary, route failure attribution, fail-closed guard 완화와 historical denominator overwrite 여부를 확인한다.
- independent reviewer와 closeout 작성자는 exact validated subject와 post-validation carrier를 별도 identity로 대조하고 carrier가 product/validation authority를 재정의하지 않는지 확인한다.
- closeout 작성자는 `ARCHITECTURE.md` §8-13/§8-15와 `ROADMAP.md` §16 readpoint identity의 supersession 여부 및 owner-action disclosure를 전수 확인한다.
- final diff에 runtime Lua, current generation, pointer, public text, package payload 변경이 없는지 검사한다.

PZ 인게임 manual QA는 제품 runtime을 변경하지 않는 이 계획의 success gate가 아니다.

### Validation Limits

#### Out Of Scope / Not Performed

- multiplayer 및 long-session validation 없음
- PZ 인게임/UI behavioral QA 없음
- performance/wall-time benchmark 없음
- external mod compatibility sweep 없음
- release/Workshop/deployment/package readiness validation 없음

#### In Scope but Not Fully Validated

- 모든 historical validation의 PASS 보장 없음
- contract ledger에 기록되지 않은 암묵적 contract의 완전한 보존 주장 없음
- test count/LOC 감소 또는 탐지 가능한 regression 집합의 정량 동일성 주장 없음

Closeout은 두 분류를 별도 필드로 기록한다. 전자는 scope exclusion이고, 후자는 조사·증거 ceiling이므로 완료 claim의 한계로 남는다.

---

## 8. Risk Surface Touch

### Authority Surface

변경됨.

current-route membership, taxonomy/source classification, required-validation membership, canonical/full-gate composition, dedicated/standalone registration 및 validation-system meta-tests가 변경될 수 있다. Current/historical/diagnostic authority category 자체는 변경하지 않는다. Baseline-admission owner decision은 executor-writable config가 아니라 owner-written authority input이며 executor는 proposal만 작성한다.

### Runtime Behavior Surface

None.

Iris runtime Lua와 제품 artifact는 변경하지 않는다. Validation cleanup은 탐지 가능한 regression 집합에 영향을 줄 수 있으므로 contract-loss risk로 관리하지만 runtime behavior change로 주장하지 않는다.

### Compatibility Surface

기본적으로 None.

등록된 standalone/PowerShell validation entrypoint가 disposition 결과로 수정되는 경우 해당 CLI arguments, exit code와 external-output semantics에 한해 compatibility surface가 생긴다. Product packaging/runtime compatibility는 범위 밖이다.

### Sealed Artifact Surface

영향 가능.

최종 current denominator, test identity, required membership, standalone composition, clean-checkout result identity는 exact validated subject의 successor state가 된다. 후속 `independent_review.json`/`closeout.json` carrier는 그 subject와 결과를 참조하는 post-validation evidence일 뿐 validated terminal subject나 product authority를 다시 정의하지 않는다. 기존 historical seal, pinned reproduction corpus, predecessor receipt와 evidence hash는 수정하지 않는다.

### Public-Facing Output Surface

None.

Menu, Tooltip, Browser/Wiki, KO/EN text, README 제품 주장과 package payload를 변경하지 않는다.

---

## 9. Risk Analysis

### Architecture Risk

- retired implementation detail을 successor current contract로 잘못 복제할 수 있다.
- validation-system meta-test가 자신의 변경을 자기 PASS로 승인하는 순환이 생길 수 있다.
- owner-written membership artifact를 executor가 직접 수정해 authority를 우회할 수 있다.
- taxonomy, required manifest와 clean-checkout source policy의 서로 다른 역할을 단일 denominator로 오해할 수 있다.
- current cleanup이 historical pinned denominator나 reproduction corpus에 전파될 수 있다.
- non-current-only unresolved source에 `historical`/`excluded` 의미를 조기 부여하거나 unclassified로 남겨 후속 disposition을 선점하거나 fail-closed collection을 막을 수 있다.
- post-validation closeout carrier를 새 terminal subject로 오해하거나 superseded top-level readpoint identity를 disclosure 없이 current 진술로 남길 수 있다.

Mitigation: contract/verifier layer 분리, pinned meta baseline, rule-level semantic diff, owner-action gate, transaction 분리, identity-set 검증, pending-disposition landing/fallback 봉인, validated-subject/carrier identity 분리, readpoint supersession disclosure, historical immutable preservation.

### Runtime Risk

- 의도상 None이지만 fixture/helper 제거가 build/product tooling consumer까지 침범하면 offline artifact generation이 깨질 수 있다.

Mitigation: support-unit consumer census에 product/tooling consumer를 포함하고 해당 unit을 `non_validation_consumer_out_of_scope`로 보존한다.

### Compatibility Risk

- standalone command path, environment variable, exit semantics 또는 external-output isolation이 cleanup 중 깨질 수 있다.
- dynamic import/subprocess path를 static scan이 놓칠 수 있다.

Mitigation: registered command focused invocation, full gate의 standalone 4/4, dynamic reachability notes와 dead-reference scan.

### Regression Risk

- partial overlap을 duplicate로 오판하여 unique current failure branch를 잃을 수 있다.
- migration successor가 predecessor보다 좁은 input partition 또는 약한 failure condition만 검증할 수 있다.
- shared fixture/helper를 predecessor-only로 오판할 수 있다.
- one-off/evidence validation이 current required route에 남거나 historical unit이 current denominator에 침투할 수 있다.
- source deletion과 manifest/config update 사이의 중간 불일치가 fail-closed gate를 깨뜨릴 수 있다.

Mitigation: contract tuple, predecessor-contract-successor trace, duplicate-inclusion proof trigger, targeted proof, meta-validator non-weakening, atomic removal, cadence B Run A/B, unresolved destructive change 금지.

---

## 10. Rollback Plan

Rollback 단위는 삭제된 파일 하나가 아니라 해당 cleanup transaction 이전의 validation composition 전체다.

각 transaction 전에 exact predecessor commit/tree와 다음 surface의 blob identity를 기록한다.

- validation source와 successor source
- fixture/helper/shared data
- source classification/taxonomy
- configured/exact denominator
- required-validation manifest
- canonical/full gate와 standalone registration
- historical reproduction route/manifest
- entrypoint/configuration

다음 조건이 발생하면 후속 transaction을 중단하고 해당 transaction 전체를 되돌린다.

- unique current contract coverage가 사라짐
- successor가 required failure semantics/input partition을 보장하지 못함
- current required source/identity 누락 또는 unclassified/conflicting source 발생
- historical reproduction input, pinned identity 또는 denominator 훼손
- support-unit 제거로 surviving validation 또는 product/tooling consumer가 깨짐
- cleanup에 귀속되는 focused/full-gate failure
- baseline-to-final 비교에서 cleanup-attributable historical/diagnostic failure 또는 attribution unknown
- Run A/B raw-byte mismatch, comparator failure 또는 source checkout mutation
- source taxonomy와 configured discovery/entrypoint를 fail-closed 상태로 정렬할 수 없음
- guard 완화 없이는 transaction이 통과하지 못함
- owner-written authority 변경이 필요하지만 owner action/adoption identity가 없음
- eligible independent reviewer gate를 충족하지 못함

Rollback은 기존 사용자 worktree 변경에 `git reset --hard`, `git checkout --` 같은 destructive 명령을 사용하지 않는다. 실행은 isolated branch/disposable checkout에서 수행하고, 필요한 경우 해당 cleanup commit을 명시적으로 revert하거나 transaction patch를 역적용한다.

Investigation ledger, failed disposition rationale, proof receipt와 predecessor historical evidence는 rollback 때문에 삭제하지 않는다.

---

## 11. Governance Constraints

- `docs/Philosophy.md` 준수
- Iris runtime 100% Lua 및 offline compiler/Lua viewer separation 유지
- Pulse 또는 다른 spoke 모듈 dependency 추가 금지
- 근거 기반·중립성·침묵 원칙과 Menu/Tooltip surface contract 불변
- current/historical/diagnostic responsibility separation 유지
- contract-first disposition; 이름·연령·PASS/FAIL 단독 판정 금지
- predecessor removal 전 unique current successor coverage 확보
- duplicate surviving-verifier inclusion의 full contract/input partition/failure branch proof 확보
- mixed-contract executable 변경 전 모든 contract-row preservation target receipt 확보
- unresolved 항목의 추측 제거 금지
- source/policy/taxonomy/manifest/entrypoint atomic reconciliation
- fail-closed guard 우회·완화 금지
- scenario execution consolidation identity/isolation 비재개방
- historical denominator, seal, receipt와 evidence 불변
- generated state repository-external, source checkout mutation `0`
- exact validated subject에만 validation PASS 귀속
- post-validation evidence/closeout carrier는 exact validated subject를 hash-bound pointer로만 참조하며 terminal subject/product authority를 재정의하지 않음
- governing semantics/ownership/principle 변화만 top-level decision/architecture에 반영하고 membership-only delta는 module-local/config에 보존; `DECISIONS.md`에 실행 로그/대형 hash 목록 중복 금지
- top-level current readpoint identity supersession 여부는 closeout에 disclose하고 문서 갱신/채택은 owner 결정으로 유지
- runtime/product artifact 변경을 validation cleanup의 해결 수단으로 사용 금지
- meta-validator predecessor/successor rule-level diff와 disposition 1:1 binding 유지. Approved declared-membership 감소는 허용하되 declared final universe에 대한 guard coverage 축소, failure 완화와 bypass 추가 금지
- owner-written authority artifact에 대한 executor direct write 금지; required owner action 부재 시 `blocked`
- independent reviewer P0/P1/P2/P3 `0` 및 meta-validator self-approval 금지
- historical/diagnostic failure는 baseline-to-final attribution 후에만 current closeout과 분리; unknown은 attributable 처리
- 사용자 소유의 현재 worktree 변경 보존

---

## 12. Expected Closeout State

Expected target: `complete`.

`complete`는 다음을 모두 만족할 때만 허용한다.

- 모든 executable validation identity가 inventory되고 actual contract가 기록됨
- executable disposition 미배정 `0`, 다중 disposition `0`
- final current authority나 removal 안전성에 영향을 주는 `needs_decision` `0`
- non-current 후보만 남은 `needs_decision` 중 current membership을 제거한 항목은 sealed pending-disposition landing, current discovery/required absence, historical corpus non-trigger와 conservative preservation 누락 `0`
- pending-disposition landing을 표현할 수 없어 fallback한 `unresolved_inherited_membership` residue `0`
- 제거된 current-contract predecessor 중 successor coverage 부재 `0`
- surviving inclusion으로 제거된 duplicate의 static full-inclusion 또는 required targeted defect proof 누락 `0`
- mixed-contract executable의 contract-row preservation receipt 누락 `0`
- `target_regular_membership=false`인 `evidence_only`의 final regular discovery/required membership `0`
- historical reproduction과 diagnostic/evidence route가 current authority와 분리됨
- cleanup-attributable 또는 attribution-unknown historical/diagnostic regression `0`
- orphan fixture/helper/config/manifest/entrypoint reference `0`
- final source/classification/discovery/required route/canonical entrypoint identity chain 일치
- meta-validator rule delta의 disposition binding 누락 `0`, fail-closed weakening `0`
- required owner action 미채택 `0`
- Phase 5와 exact validated subject의 cadence B clean-checkout Run A/B + comparator PASS
- exact validated subject source checkout mutation `0`
- independent reviewer P0/P1/P2/P3 `0`
- independent review/closeout carrier의 validated-subject pointer mismatch `0`, authority redefinition `0`
- top-level current readpoint identity supersession disclosure 누락 `0`
- Iris runtime/product/public output diff `0`

### Closeout State Decision Rules

- current membership 또는 unique coverage 관련 `needs_decision` 잔존: `partial`
- non-current-only unresolved unit의 legal pending-disposition landing이 없어 inherited current membership을 유지한 경우: `partial`; 해당 residue가 남아 있는 동안 `complete` 금지
- current-valid baseline failure가 제품 결함으로 확인됨: disposition/current membership은 확정 상태로 유지하되 별도 successor가 required gate를 회복할 때까지 이번 execution은 `blocked`
- required tooling/environment, owner action 또는 eligible independent reviewer 부재: `blocked`
- implementation만 끝나고 exact final-subject full gate가 미실행/실패: `implemented_only` 또는 `partial`
- cleanup-attributable 또는 attribution-unknown historical/diagnostic failure: rollback, `complete` 불가

### Validation Ceiling Recording Rules

- baseline부터 존재한 non-attributable historical/diagnostic failure는 route-local result와 ceiling을 기록하되 current closeout state를 자동 하향하지 않는다.
- 모든 historical validation PASS, implicit contract 완전 보존, 전체 regression-detection parity는 주장하지 않는다.
- `membership_confidence`, candidate disposition과 inherited-membership 상세는 `disposition_ledger.jsonl`/`final_composition.json`에 유지한다. `closeout.json`은 해당 artifact의 path/SHA-256와 blocking/non-blocking summary count만 참조한다.
- `closeout.json`은 exact validated subject와 post-validation carrier identity를 각각 기록하고, `readpoint_supersession_disclosure.json`의 path/SHA-256 및 owner-action 요약을 참조한다. Carrier 추가는 validated subject 변경으로 해석하지 않는다.
- Out-of-scope 미검증과 in-scope evidence ceiling은 §7 분류를 그대로 사용하며 서로 환산하지 않는다.

최종 claim은 다음을 넘지 않는다.

> Iris의 정규 validation authority와 조사된 actual current contract 사이의 대응 관계를 재확정하고, temporary / legacy validation의 역할을 그 관계에 맞게 정리했다.
