# Implementation Plan — Iris 임시·일회성 Validation Authority 최대 물리 퇴역

> 계획 상태: 리뷰 반영본 — survival/retention adjudication 및 owner gate가 닫히기 전 destructive mutation 금지
>
> Roadmap authority input: 사용자 제공 attachment `739c27fb-cef7-4206-a29e-0c99e722d55a/pasted-text.txt` (discovery location `C:/Users/MW/.codex/attachments/739c27fb-cef7-4206-a29e-0c99e722d55a/pasted-text.txt`), title `ROADMAP — Iris 임시·일회성 검증기의 정규 Validation Authority 오승격 제거 및 물리 퇴역`, raw bytes `47,794`, line count `1,687`, raw SHA-256 `a379baf8be5563631c5d7c5ce00ea50d109600a344e3ca0d2c2407179a06b551`
>
> Roadmap decision readpoint: lines `479-496`; normalized P1~P10 table bytes `1,895`, SHA-256 `c0cd36edbcf25706e2f3cdf0661933df6a3d6c3da758a600807ff3908f9f65bb` (`lines 483-496`, LF join, terminal LF)
>
> Review limitation: 이 계획에 기록된 identity는 execution input을 특정하지만, roadmap 원본을 직접 열람하지 못한 reviewer의 독립 인증을 뜻하지 않는다. Change 1의 raw reread/hash/retrieval gate만 execution authority binding을 확정한다.
>
> 분류 input: `Iris/_docs/round3/validation_contract_reconfirmation/`의 1,167-row inventory/contract/disposition ledger
>
> 검증된 분류 readpoint: commit `18d0c2ff9de97a71ddf7aa6b03fb059ffbb35089`, tree `56250ea400511eaf84ff84ee19ee8550f89b8492`; PASS carrier `6a4cf63c001ec708929e57da64347e3e7a040d91`
>
> 계획 원칙: 기존 census의 역할 분류는 재사용하되 physical deletion 판정으로 오독하지 않는다. Current regular authority는 registration과 독립적으로 존속 심사하고, reproduction executable은 현재 재현 의무와 실행 필요성을 별도로 판정한 뒤 승인된 removal만 registration·route·source·exclusive support 단위로 제거한다.

---

## 1. Objective

완료된 1,167-row authority census를 다시 만들지 않고 다음 두 누락 축을 먼저 닫은 뒤, 독립적인 current contract나 current executable reproduction obligation이 없는 임시·일회성 validation authority와 live source를 최대한 제거한다.

1. current regular execution/membership/machinery 전량을 registration과 독립적으로 존속 심사한다.
2. `reproduction_only` contract family/source 전량의 repository-local executable 필요성을 별도로 판정한다.

계획 시점의 review universe는 다음과 같다. 이 수치는 심사 입력이지 terminal deletion denominator가 아니다.

| Review universe | Planning count | Required adjudication |
|---|---:|---|
| Current pytest execution | 433 identity | `keep`, `migrate_then_remove`, `remove`, `mixed_split` |
| Current standalone execution | 4 command | 동일 |
| Current regular census disposition | 599 identity (`445 + 154`) | registration-independent survival basis 완결 |
| Registered validation CLI | 9 identity, 위 599에 포함 | CLI/runner/comparator/source-census 각각 독립 심사 |
| Current evaluator/meta-validator/gate direct unit | execution-time closure | direct consumer와 failure meaning까지 심사 |
| Non-current census disposition | 568 identity | evidence/reproduction/expired terminal disposition |

선행 census의 non-current candidate composition은 다음과 같다.

| Disposition | Identity | 관련 source path | pure source path | mixed callable |
|---|---:|---:|---:|---:|
| `reproduction_only` | 434 | 177 | 176 | 1 |
| `evidence_only` | 133 | 38 | 37 | 1 |
| `expired_or_duplicate_remove` | 1 | 1 | 0 | 1 |
| **합계** | **568** |  | **213** | **3** |

계획 시점의 physical candidate snapshot은 다음과 같다. `keep` 또는 `preserve_isolated_executable`로 닫힌 source는 deletion set에서 빠지고, current regular review에서 새로 발견된 removal/migration 대상은 deletion set에 합쳐진다.

| Storage/state domain | Files | Identity | Planning raw bytes | Planning LOC |
|---|---:|---:|---:|---:|
| Git-tracked pure candidate | 37 | 216 | Windows materialization `329,344`; canonical Git blob `322,816` | execution-time 재측정 |
| 현재 존재하는 ignored/untracked pure candidate | 162 | 332 | `892,492` | `18,509` |
| 이미 부재한 ignored/untracked pure candidate | 14 | 17 | 0 | 0 |
| 현재 존재하는 mixed target callable | 2 | 2 | source 일부 | source 일부 |
| 이미 제거된 TC8 mixed callable | 0 | 1 | 0 | 0 |

코드 조사 결과 선행 census에서 `reproduction_only`인 source 7개, identity 56개가 `Iris/validation/clean_checkout/contracts/full_repository_gate.json`의 `additional_source_paths` 또는 `explicit_current_required_sources`를 통해 current full gate에서 실제 선택된다.

| Full-gate current-selection conflict | Source | Identity |
|---|---:|---:|
| `additional_source_paths` | 4 | 17 |
| `explicit_current_required_sources` | 3 | 39 |
| **합계** | **7** | **56** |

이는 census와 current registration의 conflict다. Contract adjudication 전에는 “오승격” 또는 “삭제 확정”으로 부르지 않는다. `current_route_required_validations.json`과의 planning-time intersection `0`도 독립 contract 부재의 증명으로 사용하지 않는다.

기존 pytest `433`, standalone `4`, required execution unit `437`은 baseline 관측값일 뿐 성공 목표값이 아니다. `433 - 56`과 같은 차감 projection도 만들지 않는다. Final comparator expected value는 adjudicated surviving contract set에서 생성한 exact source/node/standalone set으로부터 파생한다.

완료는 다음을 모두 요구한다.

- pytest, standalone, CLI, evaluator/meta-validator와 regular predecessor-row survival review가 각각 `분자 = 분모`
- independent survival basis 결측과 registration-only survivor `0`
- reproduction family/source retention adjudication coverage `100%`, unresolved `0`
- owner-approved `remove`/`migrate_then_remove`/`mixed_split` target의 active membership/source residue `0`
- unfinished `migrate_then_remove` `0`
- full-gate 7-source/56-identity conflict의 terminal disposition 및 coverage/migration proof 완결
- current product/validation-system contract 손실 `0`
- destructive mutation 전 conservative projected tracked delta `< 0`
- tracked repository bytes와 test/tooling LOC 순감소
- exact final subject의 Clean-Checkout Run A/B와 deterministic comparator exit `0`

---

## 2. Scope

이 계획은 다음 변경을 포함한다.

- 기존 1,167-row ledger를 immutable predecessor input으로 사용하고 execution subject의 identity/path/hash/registration delta만 결속한다.
- actual current pytest collection, standalone 4개, current CLI 9개, current evaluator/meta-validator/full-gate direct unit과 599 regular membership closure를 delta-only survival review 대상으로 포함한다.
- 각 current unit을 `keep`, `migrate_then_remove`, `remove`, `mixed_split`로 닫고 새 removal/migration target을 physical-retirement universe에 합친다.
- `reproduction_only` 434개를 contract family/source 단위로 `remove_executable`, `externalize_nonexecuting_evidence`, `preserve_isolated_executable` 중 하나로 닫는다.
- `evidence_only` 133개와 이미 제거된 expired identity 1개도 terminal disposition을 확인한다.
- Appendix A/B의 213개 pure path를 pre-adjudication candidate로 사용하고, adjudicated deletion set만 삭제한다.
- mixed source 3개는 callable/contract 단위로 심사하고 current callable과 shared support를 보존한다.
- full gate의 7개 source/56개 identity는 survival review의 mandatory named subset으로 심사한다.
- 고유 current contract가 발견되면 successor migration과 negative proof를 predecessor removal보다 먼저 수행한다.
- meta-validator와 fail-closed pinned set을 adjudicated surviving set에 destructive mutation보다 먼저 재고정한다.
- taxonomy, source classification, discovery, gate, CLI/route, denominator와 comparator를 final surviving universe에 정렬한다.
- 마지막 consumer가 removal target뿐인 fixture/helper/input/config/import/path literal/entrypoint를 같은 batch에서 제거한다.
- evidence-only implementation은 가능한 경우 compact non-authoritative carrier로 바꾼다.
- P2에서 승인되고 `remove_executable` 또는 `externalize_nonexecuting_evidence`로 판정된 reproduction source만 제거한다.
- ignored/untracked local candidate는 tracked isolated-worktree transaction과 분리하고, 별도 owner authorization과 verified rollback을 갖춘 local cleanup transaction으로만 제거한다.
- cleanup 전용 scanner, overlay generator와 negative probe는 repository-external temporary workspace에서 실행하고 final tree에 남기지 않는다.

### Explicitly Out Of Scope

- 1,167 identity의 역할 census 전면 재작성 또는 새 ecosystem-wide taxonomy 작성
- 599개 regular disposition의 일반 병합·성능 최적화·재설계. 단, registration-independent survival review 자체는 범위에 포함한다.
- surviving current test의 assertion style, framework, fixture 또는 producer 최적화
- multi-registry architecture의 구조적 단일화
- DVF, RTC, Publish Boundary 또는 Stateful IAR architecture 재설계
- 기존 sealed historical receipt/evidence의 in-place rewrite 또는 의미 변경
- raw 1,167-row census ledger의 externalization/deletion. 이는 executable retirement와 별도인 optional evidence-lightweighting transaction이다.
- Git history rewrite, unreachable object pruning 또는 clone-size 정리
- Iris runtime Lua, current generation, facts/outcomes, Layer 2/3/4, Menu/Tooltip, public text 또는 package product semantics 변경
- PZ in-game QA, release, Workshop, deployment 또는 B42 readiness
- wall-time, CPU, memory, FPS 또는 token 효율 개선 주장
- 다른 진행 중인 Iris product/runtime 변경을 cleanup baseline에 혼입

---

## 3. Non-Goals

- 기존 `433 + 4`를 보존하거나 새 literal denominator를 만들기 위해 disposition을 조작하지 않는다.
- test count 감소 자체를 품질 개선 또는 regression으로 해석하지 않는다.
- `historical`, `diagnostic`, `reproduction_only`, 파일명 또는 과거 중요성만을 executable 보존 근거로 사용하지 않는다.
- 반대로 `reproduction_only`라는 역할 분류만으로 repository-local executable 불필요를 결론내리지 않는다.
- 7-source/56-identity conflict를 survival adjudication 전에 `full-gate 오승격`으로 확정하지 않는다.
- 사용자의 “최대한 제거” 지시를 roadmap P2 owner approval이나 ignored/untracked local deletion authorization으로 대체하지 않는다.
- tracked repository bytes, ignored/untracked local bytes와 external archive bytes를 하나의 감소 metric으로 합산하지 않는다.
- archived Python source를 normal checkout에 자동 복원하거나 default/current pytest가 수집하게 만들지 않는다.
- evidence carrier에 568개 contract row를 복제하거나 새 validation registry를 만들지 않는다.
- target 삭제를 통과시키기 위해 source-classification guard, negative assertion, failure timing 또는 fail-closed behavior를 완화하지 않는다.
- current와 non-current callable이 섞인 파일을 통째로 삭제하지 않는다.
- existing historical corpus ZIP이나 sealed predecessor artifact를 test-source 삭제 성과로 다시 포장하거나 소급 수정하지 않는다.
- 현재 작업 트리의 unrelated 변경·삭제를 cleanup 성과에 포함하지 않는다.

---

## 4. Assumptions

- 역할 분류의 canonical predecessor는 commit `18d0c2ff...`, tree `56250ea...`와 `Iris/_docs/round3/validation_contract_reconfirmation/`이다. 1,167-row census는 재작성하지 않지만 current survival과 reproduction physical retention을 위한 delta overlay는 새 `S0`에 작성한다.
- 선행 ledger의 `migrate_then_remove = 0`, `needs_decision = 0`은 역할 census 결과일 뿐 이번 심사의 결과가 아니다. 새 migration/unresolved set은 `0`으로 사전 고정하지 않는다.
- `test_tc8_full_pipeline_snapshot`은 이미 `Iris/test/test_rightclick_pipeline.py`에서 제거됐다. Execution에서는 absence와 stale registration만 확인한다.
- Git-tracked candidate 37개/216 identity의 planning snapshot은 Windows materialization 329,344 bytes, 같은 `18d0c2ff...` subject의 canonical Git blob 322,816 bytes다. 이를 terminal byte floor로 고정하지 않고 `S0`의 adjudicated tracked deletion set을 재측정한다.
- ignored/untracked candidate는 repository history로 복구할 수 없고 clean isolated worktree에는 존재하지 않을 수 있다. 삭제 전 실제 local root의 exact path/raw bytes/SHA-256와 external fresh-root restore를 검증한다.
- 사용자 제공 roadmap의 owner-decision 식별자는 `P1`~`P10`이다. 다른 문서의 합성 `D*` 이름을 만들지 않고 exact governing ID와 의미를 `decision_binding.json`에 보존한다.
- 위 roadmap authority는 plan의 self-declaration이 아니라 attachment UUID, raw byte count, line count, whole-file SHA-256와 decision-table SHA-256로 직접 결속한다. Change 1 시작 시 raw artifact를 다시 읽어 모든 identity가 일치해야 하며, unavailable/hash mismatch이면 destructive authority provenance를 `blocked`로 둔다.
- Review 시점에 원본 artifact를 직접 재검증하지 못했다는 사실은 plan mechanics의 blocker가 아니지만 hash 일치의 독립 인증으로 주장하지 않는다. Execution-time fail-closed verification이 성공하기 전에는 P1~P10 row를 destructive authority로 사용하지 않는다.
- Attachment의 machine-local path는 discovery location일 뿐 durable identity가 아니다. Exact raw roadmap은 owner-approved durable governance/evidence store에 immutable member로 보존하고, in-repo binding에는 attachment UUID, content hashes, store identity와 fresh-root retrieval proof를 기록한다.
- Roadmap P1 (baseline full-gate), P2 (`reproduction_only` physical removal), P3 (reproduction material 보존 형태), P4 (evidence-only artifact 위치), P6 (destructive granularity), P7 (unresolved disposition 처리), P8 (independent review), P10 (round/token)은 execution preflight에서 explicit owner decision artifact로 닫는다. P5는 immutable predecessor hash binding, P9는 structural unification out-of-scope로 기록한다.
- P2 미승인 상태에서는 reproduction destructive removal을 진행하지 않고 해당 scope를 `blocked`로 둔다. P2 범위가 physical completion 조건을 충족하지 못하면 전체 계획을 `complete`로 닫지 않는다.
- `Iris/_docs/refactor/repository_evidence_lightweighting/owner_policy_approval.json`은 다른 plan의 enumerated payload 승인이고 `current_authority_deletion_approved`가 `false`다. 이 artifact를 P2 승인이나 current authority deletion 승인으로 재사용하지 않는다.
- ignored/untracked source가 실제 존재하는 사용자 worktree에서의 삭제는 P2와 별개의 destructive local-state authorization을 요구한다.
- `Iris/validation/residual_refactor/migrate_repository_evidence.py`의 cold-store command를 재사용할 수 있지만, P3/P4가 외부 보존을 선택하고 대상 scope를 명시한 경우에만 사용한다.
- Cleanup/archive/restore 및 terminal measurement toolchain은 final evidence 생산이 끝날 때까지 deletion set 밖에 있어야 하며 `terminal measurement toolchain ∩ deletion set = 0`을 destructive preflight에서 확인한다.
- Adjudication, migration, re-anchor와 persistent carrier 초안이 끝난 뒤 `projected_tracked_delta < 0` 및 projected test/tooling LOC 감소를 확인하기 전에는 Change 5의 destructive mutation을 시작하지 않는다.
- existing current/historical/diagnostic claim의 상호 대체 금지는 유지한다.
- tracked change와 final Clean-Checkout은 clean isolated branch/worktree에서 수행한다. Local ignored/untracked cleanup은 대상이 실제 존재하는 사용자 worktree에서 별도 승인·archive·restore gate를 거쳐 수행한다.
- exact relevant command가 exit `0`일 때만 PASS를 주장한다. Required tooling이 없으면 AGENTS.md의 fail-closed 규칙에 따라 `blocked`다.

---

## 5. Repository Areas Affected

### Code

- Appendix A의 Git-tracked pure candidate 37개 중 adjudicated deletion set
- Appendix B selector가 찾는 ignored/untracked candidate 176개 중 owner-approved local deletion set
- Appendix C의 mixed source 3개
- `Iris/_docs/round3/round3_run_contract_tests.py`
- `Iris/build/description/v2/tests/conftest.py`
- `Iris/validation/clean_checkout/run_iris_clean_checkout_validation.py`
- `Iris/validation/clean_checkout/validate_iris_clean_checkout_validation.py`
- `Iris/validation/clean_checkout/pytest_result_plugin.py`
- `Iris/validation/clean_checkout/invoke_receipt_bound_full_gate.ps1`
- `Iris/validation/clean_checkout/invoke_deterministic_compare.ps1`
- `Iris/validation/clean_checkout/tests/test_iris_clean_checkout_validation.py`
- `Iris/build/description/v2/tests/test_iar_public_text_assessment.py`
- `Iris/build/description/v2/tools/build/iar_public_text_assessment.py`
- `Iris/build/description/v2/tools/build/run_iar_public_text_assessment.py`
- `Iris/build/description/v2/tools/build/validate_iar_public_text_assessment.py`
- candidate-only consumer가 확인된 fixture/helper/input/config/entrypoint
- `Iris/build/tools/pipeline/apply_registry_merge.py` — deleted path를 active output으로 제시하는 exact residue가 있을 때만 정리

### Docs

- `docs/iris_temporary_oneoff_validation_authority_maximal_physical_retirement_plan.md`
- `docs/ARCHITECTURE.md` — final surviving validation universe와 physical boundary만 additive update
- `docs/DECISIONS.md` — owner decision, measured removal, denominator와 claim ceiling만 additive update
- `docs/ROADMAP.md` — exact terminal state와 남은 blocked/preserved scope만 update
- `Iris/build/ENTRYPOINTS.md` — retired executable을 active entrypoint로 기술한 부분만 정정
- predecessor plans는 historical trace로 보존

### Config

- `pytest.ini`
- `Iris/_docs/round3/round3_test_taxonomy.json`
- `Iris/_docs/round3/round3_pytest_source_classification.json`
- `Iris/_docs/round3/round3_full_discovery_denominator.json`
- `Iris/_docs/round3/current_route_required_validations.json`
- `Iris/validation/clean_checkout/contracts/full_repository_gate.json`
- `Iris/validation/clean_checkout/contracts/canonical_gate.json` — referenced identity/hash가 실제로 바뀔 때만
- `.gitignore` / `.gitattributes` — exact orphan entry만

### Generated Artifacts

- `Iris/_docs/round3/temporary_validation_physical_retirement/survival_overlay.index.json`
- `Iris/_docs/round3/temporary_validation_physical_retirement/reproduction_retention_overlay.index.json`
- `Iris/_docs/round3/temporary_validation_physical_retirement/decision_binding.json`
- `Iris/_docs/round3/temporary_validation_physical_retirement/governing_roadmap_binding.json`
- `Iris/_docs/round3/temporary_validation_physical_retirement/historical_route_authority_transition.json` — route termination이 실제 후보일 때만
- `Iris/_docs/round3/temporary_validation_physical_retirement/metric_scope.json`
- `Iris/_docs/round3/temporary_validation_physical_retirement/tracked_byte_budget_preflight.json`
- `Iris/_docs/round3/temporary_validation_physical_retirement/measurement_toolchain_delta.json`
- `Iris/_docs/round3/temporary_validation_physical_retirement/retirement_summary.json`
- `Iris/_docs/round3/temporary_validation_physical_retirement/closeout.json`
- repository-external target source rollback/provenance archive와 deterministic manifest, P3가 이를 선택한 범위에 한함
- repository-external archive verify/fresh-root restore receipt
- repository-external durable detailed survival/reproduction adjudication rows, rationale와 governing roadmap raw artifact
- Run A/B, comparator, negative probe와 independent review의 hash-bound external result

In-repo overlay index는 predecessor/universe/detailed-result hash, aggregate disposition, exceptional delta와 durable external retrieval identity만 기록한다. Unit별 adjudication fields와 상세 rationale은 hash-bound owner-approved durable result root에 둔다. Closeout 이후에도 store identity만으로 fresh-root retrieve/verify할 수 있어야 하며, machine-local absolute path만 남거나 retrieval proof가 실패하면 coverage/retention claim을 `complete`로 닫지 않는다.

---

## 6. Planned Changes

### Change 1 — Exact subject와 current regular membership closure 결속

Purpose:

Cleanup의 baseline `S0`와 current execution/membership/machinery universe를 exact set으로 고정한다.

Files:

- predecessor inventory/contract/disposition/support ledgers
- current taxonomy, source classification, required manifest, full-gate contract
- `round3_run_contract_tests.py`, `conftest.py`, clean-checkout runner/comparator/plugin
- `governing_roadmap_binding.json`, `survival_overlay.index.json`, `metric_scope.json`, `decision_binding.json`, `retirement_summary.json`

Implementation Notes:

- `S0` exact commit/tree, predecessor ledger raw SHA-256와 census 이후 added/removed/renamed/registration-changed delta를 기록한다.
- User-provided roadmap attachment를 raw bytes로 다시 읽고 whole-file SHA-256 `a379...b551`, byte count `47,794`, line count `1,687`, P1~P10 table SHA-256 `c0cd...65bb`를 검증한다. P table은 원문 lines 483-496을 LF로 join하고 terminal LF를 붙인 1,895-byte projection이다.
- `governing_roadmap_binding.json`에는 logical attachment UUID, title, raw/table identities, durable store identity, retrieval contract와 verification receipt를 기록한다. Machine-specific attachment path는 discovery note로만 외부 receipt에 두고 in-repo authority identity로 사용하지 않는다.
- actual current pytest set은 configured `--round3-contract current` collection 결과의 exact node IDs로 고정한다.
- standalone set은 `full_repository_gate.json.required_standalone_validations`의 다음 네 command를 고정한다.
  - `legacy_rightclick_determinism`
  - `legacy_recipe_evidence_determinism`
  - `labelmap_fail_loud_coverage`
  - `require_render_contract`
- 선행 inventory의 current validation CLI 9개를 누락 없이 포함한다.
  - baseline-admission entrypoint/runner/validator 3개
  - clean-checkout comparator/full-gate/source-census 3개
  - deterministic-compare/receipt-bound-full-gate PowerShell entrypoint 2개
  - Round 3 contract runner 1개
- current evaluator/meta-validator/direct-gate closure에는 최소 generic IAR evaluator 4개 source, `conftest.py`, clean-checkout runner/comparator/result plugin, full-gate selection/source-disposition policy를 포함한다.
- 599 regular predecessor rows와 actual current execution/machinery mapping을 함께 기록하되 같은 denominator로 합산하지 않는다.
- `metric_scope.json`에 `S0` tracked-tree byte measurement method와 test/tooling LOC universe를 고정한다. LOC universe는 `S0`의 predecessor/current test·validation-tool paths에 이번 plan이 새로 추가하거나 수정하는 모든 Python/PowerShell test·tooling path를 더하며, added path를 제외할 수 없다.
- baseline mismatch는 cleanup 결과가 아니라 pre-existing finding으로 분리한다.
- 각 decision row는 boolean 대신 `governing_id`, `decision`, `scope`, `subject`, `status`, `authority`, `evidence_pointer`를 가진다.
- 각 P row는 `governing_roadmap_binding.json`의 whole-file/table hash를 역참조한다. Raw/table identity가 검증되지 않은 decision은 `status=unbound`이며 destructive authorization으로 사용할 수 없다.

#### Decision binding mapping

사용자 제공 roadmap은 `D*`가 아니라 다음 `P*` ID를 사용한다. 이 exact mapping을 `decision_binding.json`에 기록한다.

| Governing ID | Plan binding key | Execution meaning |
|---|---|---|
| P1 | `baseline_full_gate` | `S0` baseline full-gate 실행 여부 |
| P2 | `reproduction_physical_removal` | reproduction executable 삭제 허용 범위 |
| P3 | `reproduction_material_form` | in-repo non-executing / external durable form |
| P4 | `evidence_only_material_form` | evidence-only carrier 위치와 형태 |
| P5 | `predecessor_census_provenance` | hash-bound read-only predecessor 처리 |
| P6 | `destructive_granularity` | atomic / contract-family batch |
| P7 | `unresolved_disposition_policy` | unresolved 발생 시 축소/blocked 처리 |
| P8 | `independent_review_gate` | non-Claude review 요구 또는 explicit waiver |
| P9 | `registry_unification` | 이 plan에서는 `out_of_scope_not_adopted` |
| P10 | `round_and_completion_token` | closeout naming/token |
| local | `ignored_untracked_local_deletion` | exact local root/path destructive authorization |

Validation:

- predecessor census mapping unresolved `0`
- governing roadmap whole-file/table identity mismatch `0`
- durable roadmap retrieval/verify exit `0`
- review-time self-declaration을 execution-time verification으로 대체한 row `0`
- current pytest/standalone/CLI/machinery mapping missing `0`
- taxonomy/manifest/discovery/source-policy/full-gate mapping missing `0`
- repeated closure generation exact-set/hash equality
- `S0` tracked byte 및 test/tooling LOC scope hash가 재측정 가능
- owner gate가 필요한 scope에서 missing decision binding `0` before destructive mutation

---

### Change 2 — Registration-independent current-contract survival review

Purpose:

현재 regular로 취급되는 unit이 registration 상태와 독립적인 current contract를 실제로 보호하는지 전량 심사한다.

Files:

- Change 1의 current universe
- predecessor `contract_ledger.jsonl`
- `survival_overlay.index.json`과 repository-external detailed survival rows
- successor migration이 필요한 existing current validator/source

Implementation Notes:

- 각 current unit/contract에 다음 필드를 반드시 채운다.

```text
independent current authority source
protected current surface
observed property
current input partition
failure meaning and fail-closed branch
recurring execution necessity
migration / roadmap / closeout independence
duplicate / superset / non-subsumption relation
terminal disposition
```

- terminal disposition은 다음 네 값만 사용한다.

```text
keep
migrate_then_remove
remove
mixed_split
```

- taxonomy membership, required manifest, configured discovery, full-gate inclusion, old denominator, existing PASS, filename, historical importance는 independent survival basis가 아니다.
- Pure duplicate는 `same current contract + same relevant input partition + same-or-stronger failure condition + same fail-closed branch`가 모두 증명될 때만 `remove`로 닫는다.
- temporary-looking 기원 자체는 removal basis가 아니다. 반대로 완료된 migration/roadmap/adoption/seal/closeout/predecessor structure만 보호하고 recurring current failure meaning이 없으면 removal candidate다.
- 새 removal/migration/mixed target을 predecessor non-current candidate와 합쳐 final physical disposition universe를 만든다.
- 599개 regular identity의 일반 consolidation은 하지 않지만 survival row 누락은 허용하지 않는다.

#### Full-gate 7-source/56-identity mandatory adjudication

`additional_source_paths` 후보:

```text
Iris/build/description/v2/tests/test_dvf_3_3_korean_prose_acceptance_gate.py       7
Iris/build/description/v2/tests/test_dvf_3_3_korean_prose_candidate_route.py       2
Iris/build/description/v2/tests/test_dvf_3_3_korean_prose_policy.py                5
Iris/build/description/v2/tests/test_dvf_3_3_korean_prose_semantic_preservation.py 3
```

`explicit_current_required_sources` 후보:

```text
Iris/build/description/v2/tests/test_public_text_constituent_identity.py 20
Iris/build/description/v2/tests/test_dvf_3_3_korean_prose_compiler.py    16
Iris/build/description/v2/tests/test_naturalization_compiler_identity.py 3
```

각 contract는 다음 중 하나의 witness를 가져야 한다.

1. surviving validator의 `input partition ∩ failure branch`가 protected property를 완전히 포함한다.
2. protected property가 retired structure에만 결속되고 current recurring failure meaning이 없다.
3. 독립 current contract가 있어 해당 source를 `keep`한다.
4. 독립 current contract는 있으나 predecessor-specific source는 제거해야 하므로 `migrate_then_remove`한다.

1 또는 2가 증명되지 않고 source 자체를 keep하지 않는다면 반드시 4로 이동한다. `current_route_required_validations.json` intersection `0`은 witness가 아니다. Adjudication 뒤에 stale registration으로 판정된 항목만 “오승격 제거”라고 기록한다.

Validation:

- pytest review coverage `reviewed / actual S0 collected = 100%`
- standalone review coverage `reviewed / 4 = 100%`
- validation CLI review coverage `reviewed / actual S0 registered CLI = 100%` (planning baseline 9)
- evaluator/meta-validator/direct-gate coverage `reviewed / Change 1 closure = 100%`
- regular predecessor-row coverage `reviewed / reconciled regular rows = 100%` (planning baseline 599)
- `keep` row의 required field 결측 `0`
- registration-only survival basis `0`
- 7/56 adjudication coverage `56/56`
- duplicate/superset claim의 input/failure witness 결측 `0`
- 가능한 duplicate `remove`마다 surviving superset의 protected-property violation negative probe PASS
- unresolved `0` before Change 4

---

### Change 3 — Reproduction/evidence executable retention adjudication과 owner gate

Purpose:

`reproduction_only`를 곧바로 “삭제 가능”으로 해석하지 않고 current reproduction obligation과 executable necessity를 family/source 단위로 판정한다.

Files:

- predecessor disposition/contract ledger의 reproduction 434 identity, evidence 133 identity, expired 1 identity
- current/historical/diagnostic route binding과 direct consumers
- existing sealed historical corpus/receipt는 read-only input
- `reproduction_retention_overlay.index.json`, external detailed adjudication rows, `decision_binding.json`
- `docs/DECISIONS.md`, `historical_route_authority_transition.json` — route termination 후보가 있을 때 pre-destructive successor authority에 한함

Implementation Notes:

- reproduction contract family/source마다 다음 질문에 답한다.

```text
current reproduction obligation exists?
actual current consumer or route exists?
exact pinned subject/input exists?
defined failure meaning remains current?
must reproduction remain repository-local executable?
```

- terminal disposition은 다음 세 값만 사용한다.

```text
remove_executable
externalize_nonexecuting_evidence
preserve_isolated_executable
```

- `preserve_isolated_executable`을 `0`으로 사전 고정하지 않는다. 허용하려면 current reproduction obligation, actual consumer, pinned subject/input, defined failure meaning, executable necessity, isolated non-regular route, retention/review condition을 모두 제시한다.
- `preserve_isolated_executable`은 current/default discovery, regular denominator, full gate와 분리한다. 단 실제 current product contract로 재판정된 경우에는 Change 2의 `keep`/`migrate_then_remove` 규칙이 우선한다.
- evidence-only는 compact non-authoritative evidence로 대체 가능한지 확인한다. Executable necessity가 발견되면 단순 evidence exception으로 닫지 않고, 실제 의미가 current reproduction obligation인지 current validation-system contract인지 Change 2/이 Change의 해당 판정 축으로 되돌려 분류한 뒤 같은 수준의 근거를 요구한다.
- expired/duplicate candidate는 current contract와 stale reference 부재를 확인한다.
- P2 decision은 reproduction physical removal의 허용 범위, 제외 family와 subject를 명시해야 한다. P3 decision은 reproduction의 in-repo non-executing carrier와 owner-managed external durable bundle 중 보존 형태를 명시한다. P4는 evidence-only carrier의 위치와 형태를 별도로 명시한다.
- P2/P3/P4가 미결이거나 필요한 삭제/보존 범위를 승인하지 않으면 관련 destructive batch를 실행하지 않는다.
- Historical route membership cleanup과 route 자체 종료를 구분한다. Individual source가 불필요해도 surviving sealed historical route contract가 executable을 요구하면 필요한 최소 executable/consumer/input을 보존한다.

#### Historical-route pre-destructive authority transition

- 기본값은 `route_termination = false`다. Route membership만 정리하는 batch는 surviving historical route contract와 pinned denominator를 계속 실행할 수 있어야 한다.
- Normative invariant는 `source cleanup != historical route retirement`다. 일부 reproduction source/membership을 제거한 뒤에도 surviving historical contract가 정상 실행되면 `historical_route_authority_transition.json`과 `S_authority`를 생성하지 않는다.
- Adjudication 결과 route 자체 종료가 제안되면 plan/owner decision만으로 source를 먼저 삭제하지 않는다. `docs/DECISIONS.md`가 이 plan보다 상위 authority임을 인정하고 다음 successor decision을 destructive mutation 전에 active current readpoint로 만든다.
- Successor decision은 최소 다음을 명시한다.
  - predecessor heading `Iris validation — current / historical / diagnostic route separation`, 그 안의 sealed `historical denominator preservation: required`, 그리고 exact `S0` blob/readpoint
  - 종료되는 repository-local executable route/command/consumer와 effective subject
  - immutable historical denominator/identity set 및 sealed receipts를 rewrite하지 않는 보존 규칙
  - current/historical/diagnostic result cross-substitution 금지 유지
  - repository-local replay availability 종료와 claim ceiling
  - owner authority, P2/P3 binding, rollback/abort handling
- Authority-only commit/readpoint `S_authority`는 additive `DECISIONS.md` successor와 binding artifact만 포함하며 historical executable source, route registration, denominator 또는 pinned input을 아직 삭제하지 않는다.
- `S_authority`의 exact commit/tree에서 successor decision이 current readpoint로 검증되고 `historical_route_authority_transition.json`이 predecessor/successor blob, affected scope, effective state와 owner evidence를 결속한 뒤에만 해당 route termination set을 Change 4 projection과 Change 5 deletion에 넣는다.
- Successor authority를 활성화할 수 없거나 검증이 실패하면 route termination을 deletion set에서 제외하고 필요한 최소 executable을 `preserve_isolated_executable`로 유지한다. Change 7의 후행 governance record로 이 precondition을 소급 충족하지 않는다.

Validation:

- reproduction identity coverage `434/434`
- reproduction family/source terminal disposition coverage `100%`
- preserved executable의 7-field basis 결측 `0`
- unresolved retention disposition `0` before destructive mutation
- P2/P3/P4 approval scope와 planned deletion/archive/carrier set difference `0`
- route termination target이 있으면 verified `S_authority` predecessor/successor ordering PASS
- authority-only `S_authority`의 historical source/registration/input deletion `0`
- successor authority가 없는 route termination target `0`
- current/default route가 preserved isolated/archive source를 자동 수집·복원하는 path `0`
- `pytest.ini`, `conftest.py`, generator/setup/bootstrap command와 path injection을 포함한 dynamic re-entry probe에서 preserved isolated executable collection `0`

---

### Change 4 — Unique current-contract migration과 guard re-anchoring

Purpose:

고유 current contract를 successor에 보존하고 meta-validator/pinned set을 surviving set에 재고정한 뒤에만 source deletion을 허용한다.

Files:

- Change 2의 `migrate_then_remove`와 `mixed_split` rows
- existing surviving validator 또는 최소 successor validator
- `conftest.py`
- `round3_pytest_source_classification.json`
- `round3_full_discovery_denominator.json`
- clean-checkout runner/tests/comparator contract
- `metric_scope.json`, `tracked_byte_budget_preflight.json`

Implementation Notes:

- migration 우선순위는 같은 contract family의 surviving validator, 같은 current surface를 소유한 existing validation-system validator, 필요한 최소 successor 순이다.
- successor에는 predecessor의 migration/closeout-only assertion을 복제하지 않는다.
- migration은 current surface, input partition, assertion meaning, negative path, fail-closed behavior와 failure attribution을 보존한다.
- 각 migrated/mixed surviving contract에 valid-input PASS와 protected-property violation FAIL을 확인한다. Negative proof가 불가능하면 별도 reviewer approval로 우회하지 않고 disposition을 Change 2 survival/adjudication으로 되돌린다. 동등한 fail-closed proof를 만들 수 없으면 predecessor를 `keep`하거나 해당 scope를 `blocked`로 둔다.
- 전체 disposition과 successor proof가 닫힌 뒤, destructive deletion보다 먼저 meta-validator/current pinned set을 adjudicated surviving exact set에 re-anchor한다.
- Historical route termination set이 있으면 Change 3의 verified `S_authority`가 먼저 active해야 한다. Authority transition이 없는 route source/registration은 re-anchor deletion set에 넣지 않는다.
- old count assertion을 삭제하거나 느슨하게 하지 않는다. Expected set/count를 surviving set에서 파생하도록 입력을 바꾼다.
- disposable checkout에서 undeclared surviving source 하나를 policy 수정 없이 제거하면 collection/full gate 전에 fail-closed 해야 한다.

#### Destructive byte/LOC budget preflight

- Adjudication, required migration, guard re-anchor와 in-repo index/carrier 초안을 먼저 완료한다.
- Repository-external disposable projection worktree에서 verified `S_authority`를 포함한 exact planned registration/source/support deletion patch와 remaining closeout/governance carrier byte cap을 적용한 projected final tracked tree `T_projection`을 만든다. Authoritative execution branch의 target source는 이 단계에서 삭제하지 않는다.
- 동일한 Git blob-byte measurement method로 `B_S0`와 `B_projection`을 계산한다. Preflight artifact 자체, final summary/closeout, governance delta와 measurement-toolchain delta를 포함하지 않은 byte는 `remaining_tracked_byte_reserve`로 더한다.

```text
projected_tracked_delta
  = B_projection
  + remaining_tracked_byte_reserve
  - B_S0

required: projected_tracked_delta < 0
```

- `tracked_byte_budget_preflight.json`은 `S0`, applicable `S_authority`, candidate/adjudicated deletion set hash, deleted blob bytes, added/modified tracked bytes, remaining reserve, projection-tree identity, projected delta와 measurement method를 기록한다.
- 각 persistent artifact/patch row는 `accounted_in = projection_tree | reserve` 중 정확히 하나를 가진다. Projection tree에 실제 materialize된 blob/patch는 reserve에 다시 넣지 않고, 아직 materialize되지 않은 upper-bound만 reserve로 계상한다. Coverage `100%`, overlap `0`, unaccounted `0`을 요구한다.
- 같은 `T_projection`과 `metric_scope.json`의 고정 selector로 projected test/tooling LOC를 계산하고 `projected_test_tooling_loc < S0_test_tooling_loc`를 요구한다.
- Remaining carrier가 reserve를 초과하거나 deletion/config set이 바뀌면 preflight를 다시 실행한다. Final S1 net reduction hard gate는 그대로 유지하며 projection PASS를 final evidence로 대체하지 않는다.
- 어느 projection gate라도 실패하면 Change 5를 시작하지 않는다. 상세 rationale을 external result root로 옮기고 in-repo index를 최소화해 다시 측정할 수 있지만, byte 목표를 만들기 위해 current contract나 미승인 source를 추가 삭제하지 않는다. 계속 net-negative가 불가능하면 owner decision으로 반환하고 `partial`/`blocked` 범위를 정한다.
- Authority precedence는 `current contract correctness > authorized retirement scope > byte/LOC reduction`이다. Projection은 이미 정당화된 deletion의 실행 가능성을 검사할 뿐 deletion universe를 확대하거나 contract disposition을 바꾸는 authority가 아니다.

Validation:

- unfinished `migrate_then_remove` `0`
- successor positive/negative proof 결측 `0`
- mixed surviving callable negative probe PASS
- re-anchored source/node set = adjudicated surviving set
- undeclared source deletion negative probe expected nonzero exit
- guard assertion/failure timing weakening `0`
- `projected_tracked_delta < 0`
- `projected_test_tooling_loc < S0_test_tooling_loc`
- projection inputs/reserve/set hashes unresolved `0`
- projection/reserve accounting coverage `100%`, overlap/unaccounted `0`

---

### Change 5 — Adjudicated source와 exclusive support의 물리 퇴역

Purpose:

Change 2~4의 adjudication/migration/re-anchor가 닫히고 byte/LOC projection hard gate가 PASS한 target만 membership, source와 exclusive support에서 실제로 제거한다.

Files:

- Appendix A/B/C candidate 중 final deletion set
- taxonomy/source classification/full-gate/pytest ignore/CLI/entrypoint exact binding
- reverse dependency가 exclusive로 증명한 support
- external archive toolchain, P3/P4가 선택한 범위에 한함

Implementation Notes:

#### Tracked repository transaction

- clean isolated branch/worktree에서 contract-family/dependency-closure batch로 실행한다.
- Historical route termination batch는 verified `S_authority`의 effective scope에 정확히 포함될 때만 시작한다. Plan-local decision, 후행 closeout 또는 source deletion commit 자체를 successor authority로 사용하지 않는다.
- `tracked_byte_budget_preflight.json`의 set hashes가 actual deletion/config set과 같고 projected tracked delta와 projected LOC delta가 모두 음수인지 재확인한다. 불일치하면 삭제 전에 projection으로 돌아간다.
- 각 batch에서 taxonomy, required manifest, discovery, source classification, gate selection, CLI/entrypoint, executable source, exclusive support와 compact evidence pointer를 원자적으로 정리한다.
- `S0`에서 final adjudicated tracked deletion set의 Git blob bytes와 materialized bytes를 다시 측정한다. Planning constant 322,816/329,344를 success threshold로 사용하지 않는다.
- repository success metric은 tracked domain만 사용한다.

```text
adjudicated tracked target source residue = 0
tracked repository bytes final < S0
test/tooling LOC final < S0
```

#### Ignored/untracked local transaction

- clean isolated checkout의 absence를 local cleanup 성공으로 계상하지 않는다.
- 대상이 실제 존재하는 사용자 worktree의 resolved root와 sorted repository-relative path/hash manifest를 기록한다.
- explicit local deletion authorization, exact archive manifest, `cold-verify`, fresh-root `cold-restore`가 모두 성공한 뒤에만 삭제한다.
- 가능하면 recoverable external quarantine 이동을 사용하고, 원래 path/raw bytes/hash restore가 검증될 때까지 dispose하지 않는다.
- local cleanup 결과는 tracked repository reduction과 별도로 기록한다.

```text
tracked repository bytes
ignored/untracked local bytes
external archive bytes
```

세 domain 사이의 합계나 순감소는 주장하지 않는다.

#### Mixed and support transaction

- Appendix C의 live callable 2개만 제거한다. 두 live mixed source의 surviving current callable은 `6 + 15 = 21`개이고, 이미 TC8이 제거된 별도 source의 current callable 9개까지 포함하면 Appendix C 전체 survivor는 30개다. Shared import/setup을 보존하고 TC8은 absence/stale-reference proof만 남긴다.
- reverse dependency에서 product/tooling/current consumer가 하나라도 있으면 shared support로 보존한다.
- path literal, import, generator output, `.gitignore`, pytest ignore와 docs entrypoint의 stale reference를 scan한다.
- execution toolchain 보호 범위에는 cleanup/archive/restore뿐 아니라 final evidence를 생산하는 `round3_run_contract_tests.py`, `conftest.py`, clean-checkout runner, validator, pytest result plugin, receipt-bound full-gate entrypoint와 deterministic comparator entrypoint를 포함한다. `terminal measurement toolchain ∩ deletion set = 0`을 deletion 직전에 확인한다.
- 위 계측 toolchain이 이번 execution에서 수정되면 `measurement_toolchain_delta.json`에 before/after blob hash, semantic change, focused validation과 target-retirement delta와의 분리 계상을 기록한다. 수정된 계측기는 focused test가 먼저 PASS해야 terminal evidence 생산에 사용할 수 있다.

Validation:

- final adjudicated tracked source residue `0`
- owner-approved local target residue `0`, 승인되지 않은 local target mutation `0`
- retired mixed callable residue `0`, surviving callable positive/negative probes PASS
- orphan exclusive support/reference `0`
- `terminal measurement toolchain ∩ deletion set = 0`
- changed measurement toolchain의 undisclosed delta `0`
- route termination target과 pre-active `S_authority` scope difference `0`
- tracked/local/archive metric domain 혼합 `0`

---

### Change 6 — Route, source-policy와 denominator 최종 정렬

Purpose:

최종 configuration이 adjudicated surviving current contracts와 preserved isolated reproduction boundary를 정확히 반영하게 한다.

Files:

- taxonomy, source classification, full-discovery denominator, current required manifest
- full/canonical gate contract
- `pytest.ini`, `round3_run_contract_tests.py`, `conftest.py`
- clean-checkout runner/comparator/tests

Implementation Notes:

- final regular source/node set은 `keep` rows와 validated migration successors에서만 생성한다.
- `full_repository_gate.json`의 7 conflict source는 Change 2 결과에 따라 유지·successor 교체·삭제한다. 삭제된 항목에 한해서만 stale full-gate 오승격 제거로 기록한다.
- `round3_run_contract_tests.py --class current`는 surviving current contract만 실행한다.
- preserved isolated reproduction executable은 명시적 non-regular route로만 실행할 수 있고 current/default route와 denominator에 포함하지 않는다.
- historical/diagnostic route를 종료했다면 obsolete membership cleanup과 route termination을 별도 delta로 기록한다.
- Terminal orphan scan은 exact values를 surviving/removal set에서 파생하되 최소 다음 registration sub-key를 이름별로 검사한다.
  - `required_pytest_selection.additional_source_paths`
  - `source_disposition_policy.explicit_current_required_sources`
  - `source_disposition_policy.explicit_historical_optional_sources`
  - `source_disposition_policy.evidence_only_sources`
  - `round3_pytest_source_classification.mixed_sources[].item_overrides`
  - `round3_pytest_source_classification.source_set_binding.approved_clean_checkout_absent_policy_sources`
  - `round3_pytest_source_classification.source_set_binding.tracked_policy_sources`
  - `pytest.ini` ignore entries
- final denominator는 literal이 아니라 다음 chain으로 생성한다.

```text
surviving current contracts
-> surviving regular source/node/standalone identities
-> actual configured collection
-> final pytest + standalone + required execution units
```

- comparator expected set/count도 같은 generated set을 입력으로 사용한다. 새 숫자를 코드나 receipt schema에 독립적으로 pin하지 않는다.

Validation:

- taxonomy/source-policy/discovery/gate/CLI exact-set difference `0`
- unclassified/multiple-classification/absent-policy entry `0`
- listed registration sub-key의 removed-path/node residue `0`
- current route archive/cold-store implicit access `0`
- preserved isolated executable의 regular membership `0`
- final denominator가 surviving set에서 재현됨

---

### Change 7 — Exact-subject terminal closeout

Purpose:

최종 exact subject `S1`에서 authority cleanup, contract 보존, physical reduction과 재현성을 claim-bounded하게 닫는다.

Files:

- `retirement_summary.json`, `closeout.json`
- `docs/ARCHITECTURE.md`, `docs/DECISIONS.md`, `docs/ROADMAP.md` — terminal outcome/trace update; route termination의 최초 authorization으로 사용하지 않음
- external Run A/B/comparator/review receipts

Implementation Notes:

- raw 1,167-row predecessor ledger는 이번 transaction에서 externalize/delete하지 않는다.
- summary는 aggregate, exact candidate/adjudicated/surviving set hashes, decision IDs, exceptional delta와 predecessor pointer만 기록한다.
- `tracked_byte_budget_preflight.json`의 projection inputs와 actual S1 tracked delta를 비교하고 reserve overrun, set drift와 projection error를 기록한다. Projection PASS는 actual S1 hard gate를 대체하지 않는다.
- `S1`에서 fresh disposable checkout A/B를 만들고 full repository gate와 deterministic comparator를 실행한다.
- External detailed adjudication evidence와 governing roadmap raw artifact를 owner-approved durable store의 store identity로 fresh-root retrieve/verify한다. In-repo index hash와 retrieved raw hash/row coverage가 같아야 한다.
- P8 decision이 independent review를 요구하면 non-Claude reviewer가 current survival coverage, reproduction retention, migration proof, removal completeness, shared support, guard non-weakening, metric-domain separation과 claim ceiling을 검토한다. P8이 review를 면제하면 explicit owner decision을 기록한다.
- historical CLI/source를 제거한 경우 closeout은 과거 receipt의 historical 사실만 보존하고 repository-local replay availability는 주장하지 않는다.
- Historical route termination이 있으면 이미 pre-destructive active였던 `S_authority` successor를 직접 참조하고 실제 execution outcome을 additive closeout trace로 남긴다. 이 후행 record는 authority transition을 새로 만들거나 소급 승인하지 않는다.
- post-validation closeout carrier는 `S1`을 재정의하지 않는다.

Validation:

- survival/reproduction overlay coverage와 predecessor hash binding PASS
- governing roadmap 및 external detailed adjudication durable retrieval/verify exit `0`
- final adjudicated removal target active residue `0`
- unfinished migration/unresolved/unauthorized mutation `0`
- exact `S1` Run A exit `0`
- exact `S1` Run B exit `0`
- deterministic comparator exit `0`
- source checkout mutation `0`
- required independent review 또는 explicit P8 waiver 결속
- route termination이 있으면 `S_authority commit time/order < first destructive commit` 및 scope equality PASS

---

## 7. Validation Plan

### Automated Validation

- Python syntax validation. 실제 diff에 남은 Python executable만 exact list로 실행한다.

```powershell
uv run python -m py_compile Iris/_docs/round3/round3_run_contract_tests.py Iris/validation/clean_checkout/run_iris_clean_checkout_validation.py Iris/validation/clean_checkout/validate_iris_clean_checkout_validation.py
```

- Source-policy/clean-checkout focused tests.

```powershell
uv run python -m pytest Iris/validation/clean_checkout/tests/test_iris_clean_checkout_validation.py -p no:cacheprovider
```

- Surviving current route.

```powershell
uv run python Iris/_docs/round3/round3_run_contract_tests.py --class current
```

- Final configured collection과 denominator guard.

```powershell
uv run python -m pytest --collect-only --round3-contract current --round3-enforce-denominator -p no:cacheprovider
```

- P3/P4가 external archive를 선택한 경우 exact adopted CLI schema로 `cold-verify`와 fresh-root `cold-restore`를 실행한다. Placeholder command는 그대로 실행하지 않는다.
- Governing roadmap raw artifact와 detailed adjudication store를 fresh external root로 retrieve하고 whole-file/table/result hashes 및 row coverage를 검증한다.
- Destructive mutation 전에 external disposable projection worktree에서 `tracked_byte_budget_preflight.json`을 생성·검증하고 `projected_tracked_delta < 0`, `projected_test_tooling_loc < S0_test_tooling_loc`을 확인한다.
- `invoke_receipt_bound_full_gate.ps1`로 exact `S1`을 fresh external checkout A/B에서 실행한다.
- `invoke_deterministic_compare.ps1`로 A/B canonical result와 generated final expected set을 비교한다.
- Guard negative probe는 surviving current source 하나의 undeclared deletion이 expected nonzero exit인지 확인한다.
- Migrated/mixed contract negative probe는 protected property 위반이 expected failure meaning으로 귀속되는지 확인한다.
- 가능한 duplicate-removal contract에도 surviving superset failure probe를 적용한다.
- Preserved isolated executable은 current configured collection을 generator/setup/bootstrap/path injection 조건에서도 반복 수집하여 selected node `0`을 확인한다.
- Static residue scan은 exact adjudicated target set만 검사하고 predecessor ledger/historical prose는 provenance allowlist로 분리한다.
- Before/after metric은 다음 domain을 별도 표로 낸다.
  - tracked repository files/bytes
  - tracked test/tooling LOC
  - ignored/untracked local files/bytes
  - external archive files/bytes
  - added in-repo evidence bytes
- Terminal measurement toolchain의 before/after blob·LOC delta는 retirement target delta와 별도 표로 disclosure한다.
- `git diff --check`
- Java/Gradle, JS/TS와 Lua runtime source는 intended diff가 아니다. 실제 diff에 들어오면 scope violation으로 중단하거나 AGENTS.md의 exact relevant validation을 추가한다.

### Manual Validation

- pytest, standalone, CLI, evaluator/meta-validator/direct-gate와 regular predecessor-row coverage를 각각 별도 분자/분모로 확인한다. `433`, `4`, `9`, `599`는 planning baseline이고 actual `S0` denominator를 우선한다.
- 모든 `keep` row에서 independent authority source, input partition, failure meaning, recurring necessity와 lifecycle independence를 확인한다.
- full-gate 7-source/56-identity 각각의 coverage/retired/keep/migration witness를 검토한다.
- reproduction preservation row마다 obligation, consumer, pinned input, failure meaning, executable necessity와 isolated route를 검토한다.
- P1~P10 exact roadmap ID mapping과 P2/P3/P4/P8/local deletion approval의 authority, exact scope와 subject binding을 검토한다.
- Roadmap mapping이 plan 자체가 아니라 attachment UUID `739c27fb-...`, whole-file `a379...b551`, P table `c0cd...65bb`와 durable retrieval proof에 직접 결속됐는지 검토한다.
- Byte-budget projection의 deletion-set hash, in-repo delta, remaining reserve와 actual planned patch가 일치하는지 destructive mutation 전에 검토한다.
- 모든 projected persistent artifact가 `projection_tree` 또는 `reserve` 정확히 한 domain에 있고 gap/double-count가 `0`인지 검토한다.
- final denominator가 old value 차감이나 새 literal이 아니라 actual surviving set에서 유도됐는지 확인한다.
- mixed surviving callable의 setup/import/assertion/failure attribution을 before/after 비교한다.
- deleted local source가 generator, ignored overlay 또는 setup command로 다시 생성되지 않는지 확인한다.
- final diff에 Iris runtime Lua, generated product payload, public text와 package product file 변경이 `0`인지 확인한다.
- historical route termination이 있었다면 sealed receipt claim과 repository-local replay availability claim을 구분한다.
- Historical route termination target이 있다면 `DECISIONS.md` successor `S_authority`가 first destructive commit보다 먼저 active였고 authority-only readpoint에서는 route/source가 아직 보존됐는지 확인한다.
- Final 계측 toolchain 변경이 retirement delta와 분리 disclosure되고 focused validation을 선행했는지 확인한다.

### Validation Limits

- PZ runtime gameplay, Browser/Wiki/Tooltip visual QA를 수행하지 않는다.
- multiplayer, long-session 또는 external mod compatibility sweep을 수행하지 않는다.
- FPS, wall-time, CPU, memory, heap 또는 token benchmark를 수행하지 않는다.
- RTC, Publish Boundary, package publication, release, Workshop, deployment 또는 B42 validation을 수행하지 않는다.
- archived historical scenario 전체의 replay PASS를 새로 주장하지 않는다.
- 599개 regular test의 일반 consolidation/architecture quality를 심사하지 않는다. 다만 independent current-contract survival은 전량 심사한다.
- exact final subject 이후의 후속 repository HEAD에 PASS를 상속하지 않는다.

---

## 8. Risk Surface Touch

### Authority Surface

영향 있음. Regular membership, taxonomy, source classification, configured discovery, validation CLI/evaluator/meta-validator, pinned set, denominator와 comparator가 변경될 수 있다. 7-source/56-identity conflict는 adjudication 뒤 결과에 따라 유지·migration·제거한다.

### Runtime Behavior Surface

None intended. Iris runtime Lua와 product behavior는 변경 대상이 아니다. Runtime/product file delta가 생기면 scope drift다.

### Compatibility Surface

Internal validation compatibility에 영향이 있다. Historical/diagnostic/reproduction live executable route와 ad hoc developer command는 승인된 범위에서 제거될 수 있다. Public API, Lua require surface, external mod interface와 package compatibility는 변경하지 않는다.

### Sealed Artifact Surface

영향 있음. Final current denominator, full-gate blob identity, pinned set, comparator input과 closeout이 새 exact subject로 전진한다. Existing sealed historical receipt/evidence와 predecessor verdict는 수정하지 않는다.

### Public-Facing Output Surface

None. Menu, Tooltip, localization, public description, release message와 Workshop output은 변경하지 않는다.

---

## 9. Risk Analysis

### Architecture Risk

- registration reachability를 independent contract로 오인해 temporary validator를 남길 위험이 있다. Full current-universe survival overlay로 차단한다.
- 선행 `reproduction_only`/`evidence_only`를 executable 불필요로 오독해 current obligation을 잃을 위험이 있다. 별도 retention overlay와 applicable P2/P3/P4 gate로 차단한다.
- Governing roadmap provenance를 plan-local 선언으로 순환 정당화할 위험이 있다. User attachment의 whole-file/P-table hash와 durable retrieval proof가 없으면 decision binding을 사용할 수 없게 한다.
- Active sealed historical route를 하위 plan decision으로 먼저 삭제할 위험이 있다. Route termination은 pre-destructive `DECISIONS.md` successor `S_authority` 없이는 deletion set에 들어갈 수 없다.
- 7/56을 stale registration으로 선확정해 public-text/Korean-prose current property를 잃을 위험이 있다. Source별 coverage/retired/migration witness를 요구한다.
- external archive나 isolated reproduction route를 새 regular authority로 오승격할 위험이 있다. Current/default access와 denominator membership `0`을 요구한다.

### Runtime Risk

- Product runtime risk는 낮다. Runtime Lua와 current data는 intended changed surface가 아니다.
- ignored/untracked local deletion은 Git으로 복구할 수 없다. 별도 owner authorization, archive verify와 fresh-root restore 전에는 삭제하지 않는다.
- archive restore의 path traversal, reparse point 또는 overwrite risk가 있다. Existing containment/create-new guard와 negative fixture를 유지한다.

### Compatibility Risk

- repository-local historical/reproduction command가 제거될 수 있다. Closeout에 정확한 removed command와 availability ceiling을 기록한다.
- Current source를 소비하는 helper를 exclusive로 오판할 수 있다. Reverse dependency와 current/product/tooling consumer 검사를 batch 전에 수행한다.
- Windows EOL/path normalization이 target-set/archive hash를 바꿀 수 있다. Repository-relative POSIX path, raw-byte hash와 ordinal ordering을 고정한다.

### Regression Risk

- successor가 positive path만 보존할 위험이 있다. Failure-branch negative proof를 migration gate로 둔다.
- mixed source의 shared setup/import 제거로 surviving callable이 약화될 수 있다. Positive와 negative probe를 함께 수행한다.
- pinned-set re-anchor가 guard relaxation으로 변질될 수 있다. Undeclared surviving-source deletion probe가 반드시 fail해야 한다.
- local cleanup absence를 clean checkout success로 오계상할 위험이 있다. Execution root와 metric domain을 별도 기록한다.
- plan/closeout evidence가 tracked reduction을 상쇄할 수 있다. Destructive mutation 전 conservative byte/LOC projection과 final S1 net-reduction을 모두 hard gate로 둔다.
- Projection reserve가 작아 false PASS할 위험이 있다. 아직 생성되지 않은 summary/closeout/governance/toolchain delta의 upper bound를 포함하고 reserve 또는 set 변경 시 재실행한다.
- Final gate 계측기 변경이 retirement success를 자기정당화할 위험이 있다. Toolchain delta를 분리 disclosure하고 focused validation을 먼저 수행한다.

---

## 10. Rollback Plan

Rollback 단위는 contract-family/dependency-closure batch다. 각 batch에는 다음 preimage가 있어야 한다.

- exact predecessor commit/tree
- affected identity와 source path/hash
- survival/retention disposition과 decision binding
- taxonomy/source-policy/full-gate/CLI registration
- predecessor contract, migration successor와 negative proof
- shared/exclusive support 판정
- tracked/local/archive storage domain
- external archive manifest와 restore receipt, 해당되는 경우
- before bytes/LOC

`projected_tracked_delta >= 0`, projected LOC 비감소, missing reserve 또는 projection/set hash drift가 있으면 destructive batch를 시작하지 않는다. 이 경우 rollback할 repository mutation을 만들지 않고 carrier 최소화·scope/owner decision 단계로 반환한다.

다음 조건이면 해당 batch 전체를 되돌리고 dependent batch를 진행하지 않는다.

- survival/retention adjudication unresolved
- applicable P1~P10 gate 또는 local destructive authorization scope mismatch
- surviving current contract 또는 failure meaning 손실
- mixed current callable/shared support 변화
- undeclared-deletion probe가 fail하지 않음
- archive verify/restore 실패
- dangling active reference 또는 orphan support 잔존
- tracked bytes/test LOC 순감소 실패
- source checkout mutation 또는 Clean-Checkout failure

Tracked change는 isolated branch의 batch commit을 `git revert`하여 되돌린다. 사용자 worktree에 `git reset --hard` 또는 `git checkout --`를 사용하지 않는다.

Ignored/untracked local rollback은 batch-bound external quarantine/archive에서 원래 resolved root 아래의 exact relative path/raw bytes/hash로 복원한다. Restore proof가 통과하기 전에는 archive를 dispose하지 않는다.

Source만 복구하고 membership은 제거 상태로 두거나, membership만 복구하고 source/config는 제거 상태로 두는 mixed rollback은 허용하지 않는다.

Historical route termination batch를 rollback하면 route source/membership/input을 pre-batch 상태로 함께 복구한다. 이미 활성화된 `S_authority`를 history에서 삭제하거나 rewrite하지 않고, failed/aborted execution과 restored route availability를 설명하는 additive successor correction을 상위 authority 절차로 남긴다.

---

## 11. Governance Constraints

- `docs/Philosophy.md`의 Iris 근거·중립성·표면·100% Lua runtime 원칙을 보존한다.
- Pulse와 다른 spoke module에 새 의존성을 추가하지 않는다.
- 기존 1,167-row census를 재작성하거나 새 validation-of-validation registry를 만들지 않는다.
- Current survival review와 reproduction retention adjudication은 기존 census 재분류가 아니라 execution disposition delta다.
- Registration, historical 중요성, 기존 PASS, filename과 old denominator는 regular survival basis가 아니다.
- `reproduction_only` disposition만으로 executable deletion을 승인하지 않는다.
- Applicable P1~P10 gate 및 local destructive authorization을 실행자가 해석으로 대체하지 않는다.
- User-provided roadmap whole-file/table hash와 durable retrieval proof가 없는 P decision row는 governing authority가 아니다.
- Review-time plan text만으로 roadmap hash나 P1~P10 원문 일치를 독립 인증했다고 주장하지 않는다. Execution-time raw reread/retrieval verification이 fail-closed authority gate다.
- `docs/DECISIONS.md`는 이 plan보다 상위 authority다. Historical route termination은 successor decision이 destructive mutation 전에 active하지 않으면 금지하며 terminal closeout으로 소급 승인하지 않는다.
- `source cleanup != historical route retirement`를 유지한다. Surviving historical contract가 계속 실행되면 `S_authority`를 만들지 않는다.
- Existing evidence-lightweighting approval을 current authority/reproduction removal 승인으로 확장하지 않는다.
- Existing `433 + 4`와 어떠한 새 literal도 final 목표값이 아니다.
- `projected_tracked_delta < 0`과 projected test/tooling LOC 감소는 physical retirement 진입 조건이며, actual S1 net reduction은 별도의 terminal 조건이다.
- Contract correctness와 owner-authorized scope는 byte/LOC 목표보다 상위다. Net-negative를 만들기 위한 추가 current contract, preserved executable 또는 미승인 source 삭제는 금지한다.
- Valid current product/validation-system contract 손실은 `0`이어야 한다.
- Source deletion, membership deletion, exclusive support cleanup과 evidence pointer는 batch 원자성을 가진다.
- Current/shared support, negative assertion, failure branch와 fail-closed guard를 완화하거나 우회하지 않는다.
- Current/historical/diagnostic PASS와 denominator는 서로 대체하지 않는다.
- Stateful IAR lifecycle을 cleanup 관리 수단으로 되살리지 않는다.
- Existing sealed historical artifact는 in-place rewrite하지 않는다.
- Cleanup-only helper를 taxonomy, required gate, canonical validator 또는 장기 tooling으로 채택하지 않는다.
- Runtime/build-time separation을 유지하고 Iris product/runtime에 Python을 추가하지 않는다.
- Unrelated dirty-worktree 변경을 보존하고 cleanup diff/metric에서 제외한다.
- Authority와 Sealed Artifact Surface를 만지는 heavy execution이므로 `docs/EXECUTION_CONTRACT.md`의 disclosure, evidence, validation ceiling과 closeout discipline을 따른다.
- exact relevant command가 exit `0`이 아니면 PASS를 주장하지 않는다. Missing required tooling은 `blocked`다.

---

## 12. Expected Closeout State

Expected closeout target: `complete` — 아래 모든 success condition을 충족한 경우. 그 외에는 기존 `partial`, `implemented_only`, `blocked` 중 사실에 맞는 상태를 사용한다.

`complete`는 다음을 모두 의미한다.

```text
pytest survival review                            = reviewed / actual S0 collected
standalone survival review                        = reviewed / actual S0 standalone
CLI survival review                               = reviewed / actual S0 registered CLI
evaluator/meta/gate survival review               = reviewed / exact closure
regular predecessor-row review                    = reviewed / reconciled regular rows
registration-only survivor                        = 0
reproduction retention adjudication coverage      = 100%
unresolved destructive disposition                = 0
unfinished migrate_then_remove                    = 0
owner-approved removal target active residue      = 0
retired mixed callable                            = 0
orphan support/reference                          = 0
temporary cleanup executable                      = 0
unauthorized local mutation                       = 0
projected tracked delta before deletion            < 0
projected test/tooling LOC before deletion         < S0
governing roadmap whole-file/table binding         = exact
durable adjudication retrieval/verify              = PASS
historical route authority ordering                = PASS or not_applicable
```

- Full-gate 7-source/56-identity conflict는 각 unit의 adjudication, coverage/migration proof와 final registration이 일치한다. 삭제된 subset만 오승격 제거로 계상한다.
- Adjudicated tracked target source가 제거되고 `tracked repository bytes final < S0`, `test/tooling LOC final < S0`가 확인된다. Planning byte constant는 terminal floor가 아니다.
- `tracked_byte_budget_preflight.json`의 projection이 destructive mutation 전에 PASS했고 actual S1 delta와의 차이가 설명된다.
- Owner-approved ignored/untracked local target은 실제 local execution root에서 제거되고 별도 local byte delta와 recoverability가 확인된다. 이는 tracked repository 감소에 합산하지 않는다.
- `preserve_isolated_executable`이 있으면 근거가 완전하고 regular/current route membership이 `0`이다.
- Current product/validation-system contract 손실은 `0`이다.
- Final pytest/standalone/required denominator와 comparator expected set은 surviving contract와 actual collection에서 파생된다.
- Taxonomy, source policy, discovery, gate, CLI와 final set difference가 `0`이다.
- Exact `S1` Clean-Checkout Run A/B, deterministic comparator와 P8 decision에 따른 review가 모두 PASS한다.
- Historical route termination이 있으면 verified authority-only `S_authority`가 first destructive mutation보다 먼저 active했고 final affected scope와 정확히 일치한다.
- Historical route termination이 없으면 `historical_route_authority_transition.json`/`S_authority`는 absent가 정상이며 surviving historical contract가 계속 실행된다.
- Validation ceiling, removed internal commands와 historical replay availability를 closeout에 기록한다.

다음 중 하나라도 남으면 `complete`로 닫지 않는다.

- applicable P1~P10 gate가 unbound/missing이거나 승인 범위가 required physical-retirement condition을 충족하지 못함
- survival/retention/migration disposition unresolved
- registration-only regular survivor
- current/shared support 또는 failure-branch 손실
- guard relaxation
- old/new literal denominator 강제
- unauthorized ignored/untracked mutation
- metric domain 혼합
- byte/LOC projection gate 실패, reserve 초과 또는 set hash drift
- governing roadmap/detailed adjudication durable retrieval 실패
- route termination에 pre-active `S_authority`가 없거나 predecessor/successor/destructive commit ordering 불일치
- source checkout mutation
- Run A/B/comparator failure
- tracked bytes 또는 test/tooling LOC 순감소 미달

일부 승인된 batch만 제거되면 `partial`, 구현은 끝났지만 exact-subject terminal validation이 없으면 `implemented_only`, authority/storage/tooling 부재로 진전할 수 없으면 `blocked`를 사용한다.

완료되어도 review 시점에 roadmap 원본 hash를 독립 인증했다는 주장, Iris runtime 전체 correctness, external compatibility 전체 보존, historical reproduction 전체 PASS, RTC/Publish/release/Workshop/deployment/B42 readiness, public-text quality acceptance, PZ in-game QA 또는 성능 개선을 주장하지 않는다. Roadmap authority에 관한 완료 주장은 Change 1 execution-time raw reread/retrieval verification 범위에 한정한다.

---

## Appendix A — Git-tracked pure non-current candidate 37개

이 표는 선행 census의 pre-adjudication candidate다. Evidence/reproduction retention adjudication과 applicable P2/P3/P4 decision 뒤 final deletion set을 별도로 생성한다.

### Evidence-only 13개

| # | Source | Identity | Planning Windows bytes |
|---:|---|---:|---:|
| 1 | `Iris/build/description/v2/tests/test_dvf_3_3_legacy_combined_route_axis_inventory.py` | 6 | 6,481 |
| 2 | `Iris/build/description/v2/tests/test_dvf_3_3_required_artifact_surface_preflight_census.py` | 4 | 8,145 |
| 3 | `Iris/build/description/v2/tests/test_iris_pre_refactor_browser_characterization.py` | 1 | 1,650 |
| 4 | `Iris/build/description/v2/tests/test_iris_pre_refactor_description_characterization.py` | 1 | 1,174 |
| 5 | `Iris/build/description/v2/tests/test_iris_pre_refactor_detail_characterization.py` | 1 | 1,546 |
| 6 | `Iris/build/description/v2/tests/test_layer3_current_authority_reconstruction.py` | 2 | 2,228 |
| 7 | `Iris/build/description/v2/tests/test_phase5_array_util_contract.py` | 4 | 3,178 |
| 8 | `Iris/build/description/v2/tests/test_phase5_iris_main_function_specs_contract.py` | 4 | 2,704 |
| 9 | `Iris/build/description/v2/tests/test_public_text_quality_acceptance_fixtures.py` | 4 | 2,840 |
| 10 | `Iris/build/description/v2/tests/test_public_text_quality_metric_contract.py` | 8 | 5,825 |
| 11 | `Iris/build/tests/test_description_generator.py` | 5 | 10,955 |
| 12 | `Iris/build/tests/test_layer3_pipeline.py` | 22 | 12,068 |
| 13 | `Iris/build/tests/test_wearable_6f.py` | 1 | 2,031 |
| **합계** |  | **63** | **60,825** |

### Reproduction-only 24개

| # | Source | Identity | Planning Windows bytes |
|---:|---|---:|---:|
| 1 | `Iris/build/description/v2/tests/test_body_plan_phase_d_e.py` | 4 | 14,506 |
| 2 | `Iris/build/description/v2/tests/test_build_acquisition_sprint7_authority_promotion.py` | 1 | 15,058 |
| 3 | `Iris/build/description/v2/tests/test_build_body_role_lexical_cleanup_authority.py` | 1 | 12,720 |
| 4 | `Iris/build/description/v2/tests/test_dvf_3_3_core_registry_boundary_claim_contract_closure.py` | 6 | 6,845 |
| 5 | `Iris/build/description/v2/tests/test_dvf_3_3_food_semantic_closeout.py` | 6 | 7,710 |
| 6 | `Iris/build/description/v2/tests/test_dvf_3_3_food_semantic_curation_writer.py` | 5 | 9,964 |
| 7 | `Iris/build/description/v2/tests/test_dvf_3_3_food_semantic_handoff.py` | 4 | 7,587 |
| 8 | `Iris/build/description/v2/tests/test_dvf_3_3_food_semantic_kernel.py` | 2 | 8,202 |
| 9 | `Iris/build/description/v2/tests/test_dvf_3_3_korean_prose_acceptance_gate.py` | 7 | 6,209 |
| 10 | `Iris/build/description/v2/tests/test_dvf_3_3_korean_prose_candidate_route.py` | 2 | 7,630 |
| 11 | `Iris/build/description/v2/tests/test_dvf_3_3_korean_prose_compiler.py` | 16 | 17,637 |
| 12 | `Iris/build/description/v2/tests/test_dvf_3_3_korean_prose_policy.py` | 5 | 3,333 |
| 13 | `Iris/build/description/v2/tests/test_dvf_3_3_korean_prose_semantic_preservation.py` | 3 | 2,809 |
| 14 | `Iris/build/description/v2/tests/test_dvf_3_3_required_artifact_disposition_seal.py` | 8 | 14,804 |
| 15 | `Iris/build/description/v2/tests/test_interaction_cluster_phase_d_runtime.py` | 4 | 14,984 |
| 16 | `Iris/build/description/v2/tests/test_layer3_data_chunking_contract.py` | 5 | 10,822 |
| 17 | `Iris/build/description/v2/tests/test_live_consumer_migration_execution.py` | 7 | 11,863 |
| 18 | `Iris/build/description/v2/tests/test_naturalization_compiler_identity.py` | 3 | 6,441 |
| 19 | `Iris/build/description/v2/tests/test_post_cleanup_phase2_runtime_adoption.py` | 1 | 17,081 |
| 20 | `Iris/build/description/v2/tests/test_public_text_constituent_identity.py` | 20 | 23,928 |
| 21 | `Iris/build/description/v2/tests/test_public_text_quality_acceptance_policy.py` | 9 | 9,371 |
| 22 | `Iris/build/description/v2/tests/test_public_text_quality_acceptance.py` | 6 | 7,719 |
| 23 | `Iris/build/description/v2/tests/test_terminal_disposition_adjudication.py` | 12 | 12,008 |
| 24 | `Iris/build/description/v2/tests/test_validated_naturalization_runtime_adoption.py` | 16 | 19,288 |
| **합계** |  | **153** | **268,519** |

두 표의 planning materialization 합계는 329,344 bytes이고 `18d0c2ff...` canonical Git blob 합계는 322,816 bytes다. Final metric은 `S0`의 adjudicated deletion set을 storage domain별로 재측정한다.

---

## Appendix B — Ignored/untracked pure candidate selector

176개 ignored/untracked path를 문서에 다시 복제하지 않는다. Candidate set은 predecessor `disposition_ledger.jsonl`에서 다음 조건으로 결정하고 `S0`/actual local root에서 existence/hash를 다시 결속한다.

```text
group rows by source_path
where unique(disposition) in ({evidence_only}, {reproduction_only})
and source_path is not Git-tracked at S0
```

Planning-time state:

| Disposition / state | Paths | Identity | Local raw bytes | LOC |
|---|---:|---:|---:|---:|
| evidence-only / present ignored | 24 | 69 | 105,608 | 2,188 |
| reproduction-only / present ignored | 138 | 263 | 786,884 | 16,321 |
| reproduction-only / already absent | 14 | 17 | 0 | 0 |
| **합계** | **176** | **349** | **892,492** | **18,509** |

이 selector는 deletion authorization이 아니다. Execution-time local manifest는 resolved worktree root, sorted POSIX relative path list SHA-256, per-file raw SHA-256, adjudication, applicable P2/P3/P4 decision과 local deletion authorization을 결속한다.

---

## Appendix C — Mixed source candidate 3개

| Source | Candidate remove identity | Surviving current identity | Planning state |
|---|---|---:|---|
| `Iris/build/description/v2/tests/test_compose_entrypoint_guard_hardening.py` | `ComposeEntrypointGuardHardeningTest.test_legacy_profile_explicit_historical_output_passes` | 6 | live `mixed_split` candidate |
| `Iris/build/description/v2/tests/test_package_layer3_chunks_only_contract.py` | `PackageLayer3ChunksOnlyContractTest.test_workspace_copy_flow_excludes_layer3_monolith` | 15 | live `mixed_split` candidate |
| `Iris/test/test_rightclick_pipeline.py` | `test_rightclick_pipeline.test_tc8_full_pipeline_snapshot` | 9 | already removed; absence proof |

Live candidates는 Change 2에서 current-contract absence를 확인하고 Change 4에서 surviving callable의 positive/negative behavior를 검증한 뒤에만 제거한다.
