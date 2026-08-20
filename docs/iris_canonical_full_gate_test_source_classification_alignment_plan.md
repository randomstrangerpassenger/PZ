# Iris Canonical Full-Gate Test Source Classification Alignment Implementation Plan

> Planning authority: `docs/Philosophy.md`, `docs/DECISIONS.md`의 Iris Repository Validation / Clean-Checkout contract, `docs/ARCHITECTURE.md`의 Iris test workflow consolidation boundary, 첨부 roadmap.
>
> Immutable implementation predecessor: commit `991414badc7d470c04bad2967dd26e78aff0b697`, tree `7063a809500660e373fa74a8c06422b241d3572f` (`S_impl`).
>
> Planning-time repository observation: current `main`은 `e20119631df26fb48c590062f7aa2f86e491c342`이고 `S_impl`은 이 commit의 별도 successor다. 현재 authoring worktree에는 이 계획과 무관한 tracked/untracked Iris 변경이 존재하므로 실행과 validation은 반드시 `S_impl`에서 시작한 별도 clean exact checkout에서 수행한다.
>
> Codebase alignment note: roadmap의 네 범주 모델은 현재 canonical contract 전체를 열거하지 않는다. `Iris/validation/clean_checkout/contracts/full_repository_gate.json`과 `_full_required_source_roles()`는 기존 다섯 번째 범주 `dedicated_route_validation`을 `explicit_dedicated_route_sources`와 `owner_decision=not_applicable_dedicated_route`로 이미 운용한다. 본 계획은 이 현행 권위를 보존하며, 대상들을 네 범주 중 하나로 강제하지 않는다.
>
> Review disposition: synthesized review의 `SYN-R1`, `SYN-R2`, `SYN-R3`은 mandatory correction으로 채택한다. `SYN-R4`~`SYN-R8`, `SYN-R10`도 fail-closed evidence 강화로 반영한다. `SYN-R9`의 문서/코드 vocabulary 괴리는 `governance_document_code_divergence`로 closeout에 기록하되 이번 correction에서 top-level architecture 문서를 수정하지 않는다. 별도 independent-review gate의 필수 여부는 owner-reserved로 유지한다.
>
> Conditional authority chronology: exact-path owner amendment가 불필요하면 `S_impl -> S_validation -> external Run A/B -> S_closeout`, 필요하면 `S_impl -> S_authority -> S_validation -> external Run A/B -> S_closeout`으로 고정한다. `S_authority`는 owner amendment 한 파일만 포함하는 조건부 append-only authority successor이며 validation subject가 아니다.

---

## 1. Objective

완료된 Iris test scenario execution consolidation 구현은 변경하지 않고, `S_impl`의 tracked test-source reality와 canonical full-repository source-disposition authority를 정합화한다.

구체적인 목표는 다음과 같다.

1. `S_impl`의 tracked `test_*.py` 전체를 전수 조사해 unclassified, multiply-classified, policy-entry-but-file-absent 상태를 exact path 기준으로 고정한다.
2. roadmap에서 최초 관측된 `Iris/validation/test_workflow_consolidation/tests/test_classify_source_policy_impact.py`뿐 아니라 같은 fail-closed census에 걸리는 workflow consolidation test source 전체의 실제 역할을 판정한다.
3. 코드 근거와 명시적 owner disposition이 일치하는 경우, 해당 source를 기존 `explicit_dedicated_route_sources`에 개별 등록하여 `dedicated_route_validation`으로 분류한다.
4. configured pytest source policy와 canonical full-repository source-disposition authority를 혼합하거나 중복 수정하지 않는다.
5. 분류 수정 전후에 tracked source set, canonical classification membership, required dependency inventory, configured pytest node ID/denominator, clean-checkout regression node ID, workflow dedicated-route node ID, consolidation identity 35개를 각각 독립적으로 비교한다.
6. 수정된 exact successor `S_validation`에서 source-policy preflight를 통과시키고 canonical full-gate가 실제 pytest execution에 진입하게 한다.
7. canonical result와 receipt를 correction이 포함된 exact commit/tree에 결속하고, pytest 진입 이후의 unrelated failure는 source-classification 문제와 분리한다.
8. external Run A/B evidence를 기존 append-only gate-manifest 및 authority-closeout chain의 다음 evidence-only successor `S_closeout`에 채택한다. `S_closeout`은 `S_validation`의 validation subject가 아니며 validation 결과를 자기 자신에게 상속하지 않는다.
9. Phase-0 exact-path gap이 owner amendment를 요구하는 조건부 경로에서는 amendment-only `S_authority`를 먼저 만들고, `S_validation`이 이를 immediate predecessor로 삼도록 subject chronology를 고정한다. Amendment가 불필요하면 `S_authority`를 만들지 않는다.

계획 성공의 최소 기술 claim은 다음이다.

```text
tracked test-source classification aligned
+ source-policy preflight PASS
+ canonical pytest execution started
+ exact corrected-subject receipt binding
+ append-only evidence-only closeout adoption
```

canonical full-gate 전체 PASS는 최종 validation 결과로 기록하지만, pytest 진입 이후 별개 defect가 발생한 경우 source-classification 해결 여부를 그 defect와 합치지 않는다.

---

## 2. Scope

본 계획은 Iris Repository Validation / Clean-Checkout의 tracked test-source disposition에 한정한다.

포함 범위는 다음과 같다.

- `S_impl`의 immutable commit/tree와 pre-repair fail-closed 상태 고정
- tracked `test_*.py` 전체 source census
- canonical full-repository classification authority 및 consumer 관계 확인
- configured pytest policy와 canonical clean-checkout policy의 분리 확인
- workflow consolidation test source 10개의 파일별 role 근거 확인
- owner-reserved dedicated-route disposition 확정
- canonical contract에 대한 최소 additive classification amendment
- 기존 clean-checkout regression source 안에서의 분류 회귀 검증 강화
- correction 전후 source/node/denominator/identity exact comparison
- correction 전후 required dependency inventory exact comparison
- Phase-0 및 successor authority chain에 대한 changed-path authorization 확인
- 조건부 amendment-only `S_authority` 생성과 predecessor/delta identity 검증
- `S_impl` dedicated-route 74-node pre-change 실행 baseline
- focused source-policy 및 dedicated-route validation
- corrected exact subject의 receipt-bound canonical full-gate 실행
- 외부 receipt의 append-only gate-manifest/authority-closeout successor 채택

Planning-time code-equivalent census에서 `S_impl`은 tracked test source 144개를 가지며, 기존 명시적 role과 description-v2 historical fallback을 적용한 뒤 남는 unclassified source는 다음 10개다.

```text
Iris/validation/test_workflow_consolidation/tests/test_classify_source_policy_impact.py
Iris/validation/test_workflow_consolidation/tests/test_collect_execution_census.py
Iris/validation/test_workflow_consolidation/tests/test_compare_contract_parity.py
Iris/validation/test_workflow_consolidation/tests/test_measure_execution_cost.py
Iris/validation/test_workflow_consolidation/tests/test_public_text_phase7_scenario.py
Iris/validation/test_workflow_consolidation/tests/test_scenario_contracts.py
Iris/validation/test_workflow_consolidation/tests/test_validate_identity_transaction.py
Iris/validation/test_workflow_consolidation/tests/test_validate_measurement_comparability.py
Iris/validation/test_workflow_consolidation/tests/test_validate_scenario_report.py
Iris/validation/test_workflow_consolidation/tests/test_validate_workflow_closeout_carrier.py
```

이 목록의 path-set SHA-256은 planning-time canonicalization인 `sorted paths + LF + terminal LF` 기준 `44dd61998f784cb7bb32a43a9e5e780c24a2a6f43414c451569ffd606add894d`다. 이 값은 계획 근거이며 mutation 직전 `S_impl` exact census로 다시 생성한다.

### Explicitly Out Of Scope

- scenario consolidation 구현 또는 세 family의 execution sharing 재설계
- `runtime_payload_residual_seal_test_support.py` 및 세 consolidation 대상 test의 semantic 수정
- 기존 consolidation identity 35개의 node/assertion 재구성
- workflow consolidation 전용 test 자체의 삭제, rename, skip, deselect 또는 configured-current 편입
- `pytest.ini` testpaths/addopts 변경
- Round 3 taxonomy 또는 current/historical/diagnostic/excluded vocabulary 재설계
- `Iris/_docs/round3/round3_pytest_source_classification.json`의 unrelated 수정
- source filename/path heuristic, wildcard, glob 또는 catch-all 도입
- Registry Runtime Compatibility 또는 pytest 진입 이후 unrelated defect 수정
- DVF, QG, Artifact Registry, Naturalization, Publish Boundary 변경
- Iris runtime Lua, Browser, Wiki, Tooltip, package payload 또는 rendered data 변경
- Project Zomboid in-game, multiplayer, long-session 또는 외부 모드 호환성 검증
- release, Workshop, B42 또는 deployment readiness 판정
- 현재 dirty authoring worktree의 기존 사용자 변경 정리 또는 흡수

---

## 3. Non-Goals

- canonical full-gate를 통과시키기 위해 unclassified source를 묵시적으로 허용하지 않는다.
- workflow consolidation test 10개를 configured-current denominator에 추가하지 않는다.
- dedicated route를 historical, obsolete 또는 fixture로 위장하지 않는다.
- configured pytest source classification manifest를 canonical full-repository authority로 승격하지 않는다.
- source count와 pytest node count, configured denominator, dedicated-route 74 nodes, consolidation identity 35개를 서로 대체 가능한 수치로 취급하지 않는다.
- 기존 predecessor failure/result receipt를 rewrite하거나 `S_validation`의 결과로 재사용하지 않는다.
- external receipt만 남긴 채 canonical evidence lifecycle이 끝났다고 주장하지 않는다.
- source-policy preflight PASS를 canonical full-gate PASS로 표현하지 않는다.
- 새 tracked/authoritative evidence generator, 새 classification category 또는 별도 source-of-truth manifest를 만들지 않는다. Exact runner 함수를 호출하는 repository-external read-only census/dependency driver와 그 비권위적 receipt는 이 금지의 예외다.
- 이번 correction을 실행시간 최적화, 제품 runtime 개선 또는 전체 Iris validation 무결성 증명으로 해석하지 않는다.

---

## 4. Assumptions

1. 실행 기준 predecessor는 `S_impl=991414badc7d470c04bad2967dd26e78aff0b697`, tree `7063a809500660e373fa74a8c06422b241d3572f`다. 현재 `main`이나 dirty worktree는 validation subject가 아니다.
2. `S_impl`의 canonical classification authority는 `Iris/validation/clean_checkout/contracts/full_repository_gate.json`이며, planning-time blob은 `82af40d5b6abb2165ed54319437a58a7904f3668`다.
3. 이 authority의 consumer/enforcer는 `Iris/validation/clean_checkout/run_iris_clean_checkout_validation.py`이며, planning-time blob은 `2a90d97231fd05fa7d08b40de81583fba9ffa6cc`다.
4. `Iris/_docs/round3/round3_pytest_source_classification.json`은 configured general pytest discovery를 위한 별도 policy다. `classify_source_policy_impact.py`와 그 test는 route authority를 분리하고 workflow test root가 default/configured root 밖의 explicit path route임을 확인한다.
5. canonical full-repository authority의 실제 분류 vocabulary는 다음 다섯 범주를 포함한다.

   ```text
   required_tracked_source
   historical_optional_evidence
   obsolete_or_misrouted_test_dependency
   hermetic_test_fixture
   dedicated_route_validation
   ```

6. `explicit_current_required_sources`는 filename 또는 historical fallback보다 우선하며 이 precedence는 변경하지 않는다.
7. workflow consolidation test 10개는 planning-time inspection상 제품 current denominator를 정의하지 않고 별도의 validation tooling/contract route를 검증한다. 따라서 예상 role은 `dedicated_route_validation`이다. 단, 최종 mutation은 각 파일의 imports, assertions, consumer, configured collection 관계를 다시 확인하고 명시적 owner disposition이 확보된 후에만 수행한다.
8. 하나라도 required/current, historical, obsolete 또는 fixture 근거를 가진다면 directory 단위 일괄 판정을 중지하고 그 source를 파일별로 별도 disposition한다.
9. `S_impl`의 workflow dedicated route는 explicit collection에서 74개 node를 가진다. 이는 consolidation 구현이 보존한 35개 identity와 다른 검증 축이다.
10. consolidation identity authority는 `S_impl:Iris/_docs/refactor/test_scenario_execution_consolidation/identity_map.jsonl`이며 35 rows, Git blob `e39c810a4f7e9d024173ed37e4facdda7835c5e6`, raw SHA-256 `ee6a73c018b965d050eeeb95851b7261d7afe67a59ac0a7005b4f027ffb45888`다.
11. regression strategy는 canonical required source `Iris/validation/clean_checkout/tests/test_iris_clean_checkout_validation.py`의 기존 node `test_full_source_policy_classifies_only_declared_fallback` body만 확장하는 것으로 고정한다. 새 test function을 추가하지 않으므로 configured node, canonical required node, clean-checkout regression node와 denominator delta는 모두 `0`이어야 한다. `S_impl`의 embedded planning baseline에 있는 `collected=471`, `denominator=645`는 참고값일 뿐이며 execution에서 exact baseline을 재생성한다.
12. Python validation은 PowerShell에서 `uv run python`으로 실행한다. canonical full-gate는 repository 밖 dedicated environment receipt와 repository-external work/result/receipt roots를 사용한다.
13. pre-repair evidence와 expected delta는 mutation 전에 고정한다. 이는 roadmap의 보류 항목 중 fail-closed, exact-subject, rollback 요구를 가장 직접적으로 만족하는 선택이다.
14. dedicated-route source는 `_full_required_source_roles()`에서 `execution_role=not_required`가 되고 `_required_dependency_paths()`에는 required source set만 전달된다. 따라서 imports와 explicit direct-dependency rows를 변경하지 않는 본 correction의 expected required-dependency path-set delta는 구조적으로 `0`이다. 확인 driver는 exact checkout의 runner module을 직접 load하여 실제 `_full_required_source_roles()`, `_required_dependency_paths()`, `_validate_explicit_required_dependencies()`를 호출하고 runner blob/raw hash를 receipt에 결속한다. Post-change에는 canonical gate가 기록한 `required_dependency_inventory.path_count`, `sha256`, `explicit_direct_dependency_rows`와 driver 출력을 교차 확인한다. Runner가 직접 노출하지 않는 import-edge detail은 supporting structural diagnostic으로만 기록하며 독립 confirmation으로 과대 claim하지 않는다.
15. `build_source_census(..., full_repository=True)`는 `_classify_full_test_source()` dict comprehension에서 첫 unclassified source에 예외를 발생시키므로 pre-change non-zero output은 full enumeration baseline이 아니다. Pre-change full partition은 fail-fast receipt와 별도의 read-only exhaustive census receipt를 함께 사용한다.
16. 최초 target `test_classify_source_policy_impact.py`의 planning-time blob은 canonical full-gate contract나 자기 registration을 읽지 않고 hardcoded classification count도 assertion하지 않는다. 이 관측을 다른 target에 상속하지 않는다. Mutation 직전 actual exhaustive census로 확정한 target source 전체에서 canonical contract read, 자기 path membership assertion, hardcoded classification count를 파일별로 검사한다. 하나라도 발견되면 해당 source를 self-referential correction risk로 분리하고 owner disposition 전에는 mutation하지 않는다.
17. Phase-0 OR-05 approved tooling surface에는 regression source와 runner는 포함되지만 `contracts/full_repository_gate.json`은 포함되지 않는다. 후속 append-only gate manifests가 이 파일을 authority-owned classification contract로 계속 변경한 precedent와 owner disposition chain을 확인한다. 현재 transaction 권한이 닫히면 `S_authority` 없이 진행하고, 닫히지 않으면 exact-path owner amendment 한 파일만 포함하는 append-only `S_authority`를 `S_impl`의 direct successor로 먼저 발행한 뒤에만 classification mutation을 시작한다.
18. corrected subject에 대한 static review는 수행한다. 별도 non-Codex independent review 또는 owner seal을 technical completion의 추가 필수 gate로 둘지는 owner-reserved이며, dedicated-route authority mutation에 필요한 owner disposition/authority amendment와는 구분한다.
19. `S_validation`은 source-classification correction 두 파일이 commit된 clean exact commit이다. Owner amendment가 불필요하면 direct predecessor는 `S_impl`, 필요하면 direct predecessor는 `S_authority`다. 어느 경로에서도 `S_validation`의 immediate-predecessor-relative tracked delta는 `full_repository_gate.json`과 기존 regression test source 두 파일뿐이다.
20. identity 역할은 다음처럼 분리한다.

    ```text
    repository_reality_baseline = S_impl
    mutation_authority_subject = S_impl | S_authority
    validation_predecessor = S_impl | S_authority
    validation_subject = S_validation
    evidence_adoption_subject = S_closeout
    ```

    `S_impl`은 두 경로 모두에서 census, dependency, node, denominator, consolidation identity의 비교 baseline으로 유지한다. `S_authority`는 조건부 mutation authorization predecessor일 뿐 baseline이나 validation subject를 대체하지 않는다.
21. 모든 direct Python/pytest 검증은 bytecode/cache 생성을 억제한다. Python은 `-B` 또는 `PYTHONDONTWRITEBYTECODE=1`, pytest는 추가로 `-p no:cacheprovider`를 사용하고 각 command 전후 `git status --porcelain=v1 --untracked-files=all`을 기록한다. 예상하지 못한 `__pycache__`, `*.pyc`, `.pytest_cache`가 생기면 hygiene failure로 기록하고 그 checkout을 후속 validation에 재사용하지 않으며, 새 disposable exact checkout에서 다시 시작한다.

---

## 5. Repository Areas Affected

### Code

예상 변경:

- `Iris/validation/clean_checkout/tests/test_iris_clean_checkout_validation.py`
  - 기존 source-policy regression source 안에서 10개 explicit dedicated-route membership, exact role, owner decision, no-denominator-adoption을 검증한다.

읽기 전용 inspection/protected surface:

- `Iris/validation/clean_checkout/run_iris_clean_checkout_validation.py`
- `Iris/validation/test_workflow_consolidation/classify_source_policy_impact.py`
- `Iris/validation/test_workflow_consolidation/tests/test_classify_source_policy_impact.py`
- `Iris/validation/test_workflow_consolidation/tests/test_collect_execution_census.py`
- `Iris/validation/test_workflow_consolidation/tests/test_compare_contract_parity.py`
- `Iris/validation/test_workflow_consolidation/tests/test_measure_execution_cost.py`
- `Iris/validation/test_workflow_consolidation/tests/test_public_text_phase7_scenario.py`
- `Iris/validation/test_workflow_consolidation/tests/test_scenario_contracts.py`
- `Iris/validation/test_workflow_consolidation/tests/test_validate_identity_transaction.py`
- `Iris/validation/test_workflow_consolidation/tests/test_validate_measurement_comparability.py`
- `Iris/validation/test_workflow_consolidation/tests/test_validate_scenario_report.py`
- `Iris/validation/test_workflow_consolidation/tests/test_validate_workflow_closeout_carrier.py`

`run_iris_clean_checkout_validation.py`의 behavior 또는 receipt schema 변경은 기본 계획에 포함하지 않는다. 기존 `source_rows`가 다섯 번째 authority class를 보존하므로, completeness 요약은 external comparison receipt에서 계산한다. 기존 runner로 필요한 exact evidence를 표현할 수 없다는 실행 근거가 생긴 경우에만 별도 additive amendment로 연다.

### Docs

- `docs/iris_canonical_full_gate_test_source_classification_alignment_plan.md`

기존 `Philosophy.md`, `DECISIONS.md`, `ARCHITECTURE.md`, `ROADMAP.md`는 이번 execution에서 수정하지 않는다. 네-role 서술과 실제 five-role canonical behavior의 차이는 evidence-only closeout에 `governance_document_code_divergence`로 기록하고 별도 후속 reconciliation 대상으로 남긴다.

### Config

예상 변경:

- `Iris/validation/clean_checkout/contracts/full_repository_gate.json`
  - `source_disposition_policy.explicit_dedicated_route_sources`에 evidence-confirmed source를 파일별로 additive 등록한다.
- current authority chain이 Phase-0 OR-05의 exact-path gap을 충분히 승인하지 않는 경우에만 owner가 지정하는 append-only authority-amendment successor 한 파일
  - `S_authority`의 유일한 tracked delta다.
  - `full_repository_gate.json`의 이번 membership mutation과 exhaustive census로 확정한 exact target set만 승인한다.
  - amendment가 불필요한 경로에서는 이 artifact와 `S_authority`를 생성하지 않는다.

기본적으로 변경하지 않음:

- `pytest.ini`
- `Iris/_docs/round3/round3_pytest_source_classification.json`
- `Iris/_docs/round3/round3_test_taxonomy.json`
- `Iris/_docs/round3/current_route_required_validations.json`

현재 worktree의 `round3_pytest_source_classification.json` 수정은 사용자 소유의 별도 변경이며 본 계획에서 덮어쓰거나 정리하지 않는다.

### Generated Artifacts

Temporary execution artifact는 repository 밖 새 root에 생성한다.

- pre-repair failure-state orchestration receipt/stdout/stderr
- pre-change full-repository source census 및 path/category membership report
- expected admission delta declaration
- changed-path tooling authorization/owner-amendment receipt
- post-`S_authority` commit/tree/parent/amendment blob identity-binding receipt, 조건부
- pre/post required dependency path-set 및 inventory hash receipt
- pre/post configured collection denominator receipts
- pre/post canonical clean-checkout regression node-set receipt
- pre/post exact node ID sets 및 diff
- workflow dedicated-route 74-node pre-change/post-change collection 및 execution receipts
- consolidation 35-identity invariance report
- post-change full-repository source census
- focused validation logs
- per-command pre/post generated-cache hygiene status receipts
- canonical full-gate orchestration receipt
- canonical result/full-run receipt 또는 failure-stage receipt
- downstream failure attribution record, 필요한 경우

Owner amendment가 필요한 경우 external evidence 단계 전에 다음 tracked conditional artifact를 먼저 생성한다.

- `Iris/validation/clean_checkout/authority/<owner-designated-authority-amendment-successor>.json`
  - `S_authority`에 단독 commit하며 predecessor는 `S_impl`이다.
  - artifact 내부 predecessor는 reservation 시점의 latest applicable authority artifact path/blob/hash를 가리킨다.
  - exact path/content/blob/hash와 authority-chain predecessor는 single-writer reservation 후 authority receipt에 결속한다.

External evidence가 완성된 뒤 다음 tracked append-only artifacts를 기존 chain의 next unused successor ID로 생성한다.

- `Iris/validation/clean_checkout/evidence/full_repository_gate_manifest_successor_<next>.json`
- `Iris/validation/clean_checkout/authority/full_repository_technical_debt_closeout_successor_<next>.json`

두 artifact만을 포함하는 evidence-only successor를 `S_closeout`으로 정의한다. Single-writer reservation 직전/commit 직전에 predecessor가 여전히 latest인지 확인하며, 경합 successor가 있으면 번호를 재할당하고 predecessor identity를 다시 결속한다.

Post-run receipt를 `S_validation`에 commit하지 않는다. 그렇게 하면 receipt가 결속한 subject와 receipt를 포함한 새 commit이 달라지는 자기참조 문제가 생긴다. 대신 다음 관계를 명시한다.

```text
validation_subject = S_validation
evidence_adoption_subject = S_closeout
S_closeout_is_validation_subject = false
S_closeout_authority_effect = evidence_only
tests_rerun_for_S_closeout = false
```

전체 subject chronology는 다음 두 경로 중 정확히 하나다.

```text
No-amendment path:
S_impl -> S_validation -> external Run A/B -> S_closeout

Amendment-required path:
S_impl -> S_authority -> S_validation -> external Run A/B -> S_closeout
```

두 경로 모두 `S_closeout`의 direct predecessor는 `S_validation`이다. `S_authority`는 존재하는 경우에도 외부 Run A/B 또는 `S_closeout`의 validation subject가 아니다.

---

## 6. Planned Changes

### Change 1 — Immutable predecessor and pre-repair failure-state freeze

Purpose:

correction 전에 `S_impl`과 현재 blocker를 재현 가능한 exact evidence로 고정한다.

Files:

Changed files:

- None

Read-only inputs / external outputs:

- read-only `S_impl` tracked tree
- repository-external baseline receipt root

Implementation Notes:

1. `S_impl`에서 별도 clean checkout을 만들고 commit/tree 및 `git status --porcelain=v1 --untracked-files=all`을 기록한다.
2. current dirty authoring worktree에서 source-policy mutation이나 canonical validation을 실행하지 않는다.
3. `source-census --full-repository`와 receipt-bound full-gate preflight를 실행해 fail-fast state를 기록한다. 현재 runner는 첫 unclassified source에서 중단하므로 이 결과를 full partition census로 사용하지 않는다.

   ```text
   native exit
   failure stage
   first reported source
   pytest_started
   full-run receipt presence
   subject commit/tree
   ```

4. 별도의 repository-external read-only exhaustive census driver로 `S_impl`의 실제 tracked test-source set 전체를 끝까지 열거한다. Planning reference는 144개지만 driver가 산출한 actual path set/count가 우선한다. Driver source bytes/command/hash, `S_impl` commit/tree, raw declarations와 output hash를 같은 receipt에 결속하며 tracked tooling으로 추가하지 않는다.
5. workflow dedicated route를 `S_impl`에서 explicit path로 collect하고 한 번 실행하여 pre-change 74-node ID set과 pass/fail result를 확보한다. Planning-time collect-only 결과를 execution PASS로 대체하지 않는다.
6. 첫 reported source가 전체 gap이라는 가정을 하지 않는다.
7. 실패 결과를 수정 후 PASS receipt로 덮어쓰지 않는다.

Validation:

```text
baseline_subject_commit = 991414badc7d470c04bad2967dd26e78aff0b697
baseline_subject_tree = 7063a809500660e373fa74a8c06422b241d3572f
checkout_clean = true
source_policy_preflight = FAIL
pytest_started = false
failure_stage = source classification
fail_fast_output_is_full_census = false
exhaustive_census_complete = true
prechange_dedicated_route_node_count = 74
prechange_dedicated_route_execution_exit = 0
```

로드맵의 기존 `native exit=2`, `full-run receipt absent` 관측과 달라지면 actual stage/exit를 우선 기록하고 차이를 설명한다. Exit code가 같아도 stage가 같다는 뜻은 아니며 stage는 receipt/log identity와 `pytest_started` evidence로 귀속한다.

---

### Change 2 — Full source census, authority localization, and role decision

Purpose:

단일 target correction이 아니라 tracked test-source universe 전체의 분할 완전성을 확인하고, configured policy와 canonical authority의 관계를 확정한다.

Files:

Changed files:

- None during this change

Read-only inputs / external outputs:

- `Iris/validation/clean_checkout/contracts/full_repository_gate.json`
- `Iris/validation/clean_checkout/run_iris_clean_checkout_validation.py`
- `Iris/_docs/round3/round3_pytest_source_classification.json`
- `pytest.ini`
- workflow consolidation test source 10개
- `Iris/validation/clean_checkout/authority/phase0_ratification_attempt_0001.json`
- latest append-only full-repository gate manifest/closeout authority pair
- repository-external census, dependency-inventory, route/node receipts

Implementation Notes:

1. `git ls-tree -r --name-only S_impl`에서 basename이 `test_`로 시작하고 `.py`로 끝나는 모든 tracked source를 census한다. 이는 runner의 `_test_sources()`와 동일한 universe다.
2. 각 source에 대해 다음 membership을 materialize한다.

   ```text
   taxonomy current/ok required
   full-gate additional source/node
   required standalone validation
   explicit current-required
   explicit historical optional
   explicit dedicated route
   hermetic fixture
   obsolete/misrouted
   description-v2 historical fallback
   unclassified
   ```

3. raw declaration 기준 cross-category membership을 비교해 같은 source가 서로 다른 authority class에 동시에 나타나는지 검사한다. `_full_required_source_roles()`의 dict overwrite 결과만 보고 exclusivity를 주장하지 않는다.
4. 모든 explicit policy path가 `S_impl`에 tracked인지 확인하고, absent entry는 category별 reverse mismatch로 기록한다. intentionally absent가 허용되는 별도 policy가 있으면 그 authority와 reason을 함께 기록한다.
5. workflow test 10개 각각에 대해 imports, assertions, configured root membership, current/historical taxonomy identity, direct consumer, fixture 여부, standalone/dedicated execution command를 확인한다.
6. 특히 target test가 검증하는 다음 사실을 보존한다.

   ```text
   workflow test root is outside pytest.ini default testpaths
   configured source policy authority remains separate
   explicit path route is expected
   ```

7. actual exhaustive census로 확정한 target source 전체가 canonical contract를 읽는지, 자기 path membership을 assertion하는지, hardcoded classification count를 assertion하는지 exact blob별로 검사한다. Planning-time 최초 target 관측은 세 항목 모두 `false`지만 이를 나머지 source에 상속하지 않는다. 어느 집합이라도 비어 있지 않으면 해당 source별 input/output feedback loop를 기록하고 owner disposition 전 mutation을 중지한다.
8. regression source의 route를 확정한다.

   ```text
   regression_source = Iris/validation/clean_checkout/tests/test_iris_clean_checkout_validation.py
   configured_pytest_root_member = false
   canonical_full_repository_required_source = true
   implementation_strategy = extend_existing_test_function_only
   existing_node = test_full_source_policy_classifies_only_declared_fallback
   new_test_function_allowed = false
   ```

9. Phase-0 OR-05와 current successor chain에서 예상 changed path를 exact path로 확인한다.

   ```text
   test_iris_clean_checkout_validation.py in Phase-0 approved tooling surface = true
   run_iris_clean_checkout_validation.py in Phase-0 approved tooling surface = true (read-only)
   full_repository_gate.json in Phase-0 approved tooling surface = false
   ```

   후속 manifests의 authority-owned classification-contract precedent와 현재 owner disposition이 이 gap을 닫는지 기록한다. 닫히지 않으면 owner가 exact `full_repository_gate.json` membership amendment를 승인할 때까지 mutation하지 않는다.
10. planning-time 예상 role `dedicated_route_validation`을 파일별 evidence report로 검증한다.
11. owner는 canonical contract가 요구하는 disposition을 명시적으로 승인한다.

   ```text
   owner_decision = not_applicable_dedicated_route
   configured_current_membership = unchanged
   full_repository_required_denominator_adoption = false
   dedicated_route_execution = required focused evidence
   ```

12. required dependency inventory baseline을 classification과 독립적으로 materialize한다. External driver는 exact `S_impl` runner module을 직접 load하고 실제 `_full_required_source_roles()`, `_required_dependency_paths()`, `_validate_explicit_required_dependencies()`를 호출하여 required source set, explicit rows, sorted path set/count/hash를 기록한다. Driver source/command hash와 runner Git blob/raw hash를 같은 receipt에 결속한다. Import-edge detail 산출에 별도 traversal glue가 필요하면 runner의 `_imports()`와 resolver를 사용하되 그 edge set은 supporting structural diagnostic으로 표시한다.
13. owner disposition/changed-path authority가 없거나 어떤 source의 근거가 dedicated route로 닫히지 않으면 mutation으로 진행하지 않는다.
14. changed-path authority 판정을 다음 둘 중 하나로 봉인한다.

    ```text
    authority_path = no_amendment
    mutation_authority_subject = S_impl
    validation_predecessor = S_impl

    또는

    authority_path = amendment_required
    authority_predecessor = S_impl
    mutation_authority_subject = S_authority
    validation_predecessor = S_authority
    ```

    `amendment_required`이면 owner가 지정한 next append-only amendment path, exact content hash, internal authority-chain predecessor identity를 mutation 전에 고정하고, 그 단일 artifact 이외의 `S_authority` delta를 허용하지 않는다.

Validation:

```text
tracked_test_source_count = 144  # S_impl planning baseline; exact run에서 재확인
unclassified_source_count = 10  # pre-change expected
multiply_classified_source_count = 0
fail_fast_census_used_as_full_baseline = false
sources_reading_canonical_contract = 0
sources_asserting_own_membership = 0
sources_hardcoding_classification_count = 0
self_reference_check_subject_set = actual exhaustive target source set
clean_checkout_regression_source_route = canonical_full_repository_required_source
clean_checkout_regression_strategy = extend_existing_test_function_only
required_dependency_inventory_materialized = true
changed_paths_authorized = true
target_role_reasoning = evidence-derived, not filename-derived
configured_policy_is_canonical_authority = false
canonical_authority_identified = true
owner_disposition_present = true
authority_path = no_amendment | amendment_required
repository_reality_baseline = S_impl
mutation_authority_subject = S_impl | S_authority
validation_predecessor = mutation_authority_subject
```

Exact census의 actual unclassified set/count가 planning value 10과 다르면 actual set을 우선한다. Mutation 전에 path-set hash, role evidence, expected delta와 owner disposition을 actual set에 맞춰 다시 봉인하며 planning value를 강제로 유지하지 않는다.

---

### Change 3 — Expected delta freeze

Purpose:

결과를 본 뒤 intended delta를 사후 정의하지 않도록 mutation 전에 허용 변화를 고정한다.

Files:

- Changed: none; receipt는 repository-external generated artifact다.
- Read-only: `S_impl:Iris/_docs/refactor/test_scenario_execution_consolidation/identity_map.jsonl`
- External output: expected-delta receipt

Implementation Notes:

dedicated-route 판정이 actual exhaustive target set 전체에 대해 확정된 경우 expected delta를 다음과 같이 고정한다. 아래 `+10`은 planning value이며 actual target count가 다르면 mutation 전에 그 actual로 대체한다.

```text
tracked_test_source_path_delta = 0
source_content_delta = 0 for workflow test sources
dedicated_route_membership_delta = +10
required_source_membership_delta = 0
historical_optional_membership_delta = 0
obsolete_or_misrouted_membership_delta = 0
hermetic_fixture_membership_delta = 0
configured_source_policy_delta = 0
configured_node_id_delta = 0
configured_denominator_delta = 0
clean_checkout_regression_source = Iris/validation/clean_checkout/tests/test_iris_clean_checkout_validation.py
clean_checkout_regression_existing_node_body_change = 1
clean_checkout_regression_new_test_function_delta = 0
clean_checkout_regression_node_id_delta = 0
canonical_required_node_id_delta = 0
workflow_dedicated_route_node_id_delta = 0
workflow_dedicated_route_node_count = 74
required_dependency_source_set_delta = 0
required_dependency_import_edge_delta = 0
explicit_direct_dependency_row_delta = 0
required_dependency_path_set_delta = 0
required_dependency_inventory_hash_delta = 0
consolidation_identity_map_row_delta = 0
consolidation_identity_map_rows = 35
scenario_consolidation_semantic_delta = 0
runtime_surface_delta = 0
```

Subject-relative tracked delta도 같은 receipt에서 조건부로 고정한다.

```text
No-amendment path:
S_authority = absent
S_validation_parent = S_impl
S_validation_immediate_predecessor_delta = {
  Iris/validation/clean_checkout/contracts/full_repository_gate.json,
  Iris/validation/clean_checkout/tests/test_iris_clean_checkout_validation.py
}

Amendment-required path:
S_authority_parent = S_impl
S_authority_delta = {exact owner authority-amendment artifact only}
S_validation_parent = S_authority
S_validation_immediate_predecessor_delta = {
  Iris/validation/clean_checkout/contracts/full_repository_gate.json,
  Iris/validation/clean_checkout/tests/test_iris_clean_checkout_validation.py
}
```

파일별 evidence가 다른 role을 지시하면 mutation 전에 이 receipt를 다시 작성하고 owner가 disposition한다. mutation 후 expected delta를 바꾸지 않는다.

Validation:

- mutation 전 expected-delta receipt는 `S_impl` commit/tree, sealed `authority_path`, owner-designated amendment path/content hash/internal authority-chain predecessor identity(필요한 경우), exhaustive census path-set hash, required-dependency path-set/hash, clean-checkout regression node set, workflow dedicated-route node set, identity-map blob/hash에만 결속한다. 이 시점에 아직 존재하지 않는 `S_authority` commit/tree를 요구하지 않는다.
- expected delta가 owner disposition보다 먼저 final로 봉인되지 않는다.
- receipt는 repository 밖에 있으며 source tree를 변경하지 않는다.
- `S_validation`의 immediate predecessor가 `S_impl`이든 `S_authority`든 tracked correction delta에는 contract와 기존 regression test body 두 파일만 포함한다. Optional owner amendment는 별도 `S_authority`의 단일-file delta이고, 외부 Run A/B 뒤 evidence pair `+2`는 별도 `S_closeout` delta다. 어느 것도 `S_validation` immediate-predecessor delta에 섞지 않는다.

---

### Change 4 — Conditional authority predecessor and minimal canonical source-disposition amendment

Purpose:

strict classification behavior를 유지하면서 repository reality를 기존 authority에 additive 정합화한다.

Files:

- Conditionally changed in `S_authority`: owner-designated append-only authority-amendment successor 한 파일
- Changed: `Iris/validation/clean_checkout/contracts/full_repository_gate.json`
- Read-only authority inputs: Phase 0 ratification receipt, latest append-only gate-manifest/authority-closeout chain, owner disposition or owner amendment
- External output when applicable: post-`S_authority` identity-binding receipt

Implementation Notes:

1. mutation 전에 changed path인 `Iris/validation/clean_checkout/contracts/full_repository_gate.json`에 대한 exact-path authority를 증명한다. Phase 0 OR-05 approved tooling surface에 이 contract가 없으므로, later append-only authority precedent와 `full_repository_membership_with_owner_decision` allowance가 이번 path mutation을 실제로 승인하는지 owner가 disposition한다.
2. authority가 충분하면 `S_authority`를 만들지 않고 clean `S_impl`에서 correction branch를 시작한다.
3. authority가 충분하지 않으면 single writer가 latest applicable authority artifact를 다시 읽고 owner-designated next append-only amendment path를 예약한다. Artifact 내부 predecessor를 그 latest path/blob/hash에 결속한 뒤 owner amendment 한 파일만 commit한 clean direct successor `S_authority`를 만든다. `S_authority` parent는 exact `S_impl`이어야 하며 contract/regression/source file은 이 commit에서 byte-identical이어야 한다. 경합이 확인되면 ID와 predecessor binding을 재계산하고, 이후 correction branch는 `S_authority`에서 시작한다.
4. `S_authority` 생성 직후 별도 external identity-binding receipt에 실제 commit/tree, single-parent `S_impl`, amendment path/blob/content hash, 내부 authority-chain predecessor를 기록하고 mutation 전 freeze receipt의 예정 path/hash/predecessor와 대조한다. 이 receipt는 Change 3 expected delta를 개정하지 않고 실현된 authority subject identity만 추가 결속한다.
5. selected correction branch에서 evidence-confirmed workflow source를 `source_disposition_policy.explicit_dedicated_route_sources`에 개별 row로 추가한다.
6. 각 row는 정확한 `path`, `owner_decision=not_applicable_dedicated_route`, 파일의 실제 역할을 설명하는 비어 있지 않은 `reason`을 가진다.
7. directory prefix, glob, wildcard, filename heuristic 또는 unknown fallback을 추가하지 않는다.
8. actual exhaustive census에서 확정된 target source를 configured discovery manifest의 `reviewed_sources`, `planned_sources`, `excluded_sources`에 복제하지 않는다.
9. `pytest.ini`, current taxonomy, required-validation manifest, source files, consolidation implementation은 변경하지 않는다.
10. 새 test source를 만들지 않는다.

Validation:

```text
each_target_path_occurrence_in_canonical_role_surface = 1
each_target_authority_class = dedicated_route_validation
each_target_execution_role = not_required
each_target_owner_decision = not_applicable_dedicated_route
required_denominator_adoption_delta = 0
unknown_allow_added = false
historical_default_expanded = false
collection_exclusion_added = false
changed_path_authority = proven_or_owner_amended_before_mutation
S_authority_present = true iff authority_path is amendment_required
S_authority_parent = S_impl when present
S_authority_tracked_delta = exact_one_owner_amendment_artifact when present
S_authority_internal_predecessor = reserved_latest_authority_identity when present
post_S_authority_identity_receipt_matches_freeze = true when present
```

---

### Change 5 — Existing regression surface extension

Purpose:

새 tracked test source를 추가하지 않고 classification amendment와 strict fail-closed behavior를 회귀 검증한다.

Files:

- Changed: `Iris/validation/clean_checkout/tests/test_iris_clean_checkout_validation.py`
- Read-only: `Iris/validation/clean_checkout/contracts/full_repository_gate.json`

Implementation Notes:

1. 기존 node `test_full_source_policy_classifies_only_declared_fallback`의 body만 확장한다. 새 test function, 새 test source, 별도 import를 추가하지 않는다.
2. actual exhaustive census에서 확정한 exact workflow source set이 dedicated-route rows에 포함되는지 검사한다. Planning value 10은 actual count가 다르면 대체한다.
3. 모든 row의 owner decision과 reason schema를 검사한다.
4. `_full_required_source_roles()`와 `_classify_full_test_source()` projection이 각 path에 대해 다음을 생성하는지 검사한다.

   ```json
   {
     "execution_role": "not_required",
     "authority_class": "dedicated_route_validation"
   }
   ```

5. 이 source들이 required gate source set이나 configured-current denominator에 편입되지 않았음을 검사한다.
6. 기존 unknown path가 계속 `CleanCheckoutError("unclassified ...")`를 발생시키는 negative assertion을 유지한다.
7. raw contract category membership audit에서 target path의 cross-category duplicate가 0인지 검사한다.
8. test가 자기 자신의 registration만 확인해 통과하지 않도록 target test body의 route-separation assertions와 canonical contract projection assertions을 함께 사용한다.
9. contract amendment와 이 regression body change를 함께 commit하여 `S_validation`을 만든다. No-amendment path에서는 parent가 `S_impl`, amendment-required path에서는 parent가 `S_authority`이며, 어느 경로든 parent-relative changed path set은 이 두 파일과 정확히 일치해야 한다.

Validation:

- focused regression native exit `0`
- 새 `test_*.py` source count delta `0`
- clean-checkout regression node ID delta `0`
- canonical required node ID delta `0`
- `S_validation` direct-parent identity가 selected authority path와 일치
- `S_validation` parent-relative tracked delta가 contract/regression 두 파일과 정확히 일치
- existing unknown fail-closed assertion 보존
- explicit current-required precedence regression 보존

---

### Change 6 — Source, node, denominator, and identity verification

Purpose:

classification correctness와 test execution identity correctness를 독립적으로 검증한다.

Files:

- Changed: none; this change only verifies the exact subject.
- Read-only: corrected exact checkout at `S_validation`
- External outputs: pre/post comparison receipts

Implementation Notes:

1. `S_validation`은 source-classification correction이 commit된 clean exact subject다. No-amendment path에서는 `S_impl`의 direct successor이고 amendment-required path에서는 `S_authority`의 direct successor다. working-tree-only correction은 canonical validation subject가 될 수 없다.
2. post-change `source-census --full-repository`를 실행한다.
3. pre/post source path set과 raw category membership을 exact identity로 비교한다.
4. configured current collect-only receipt를 pre/post 비교한다.
5. clean-checkout regression source의 exact node ID set을 pre/post 비교하고 기존 target node 외 신규 node가 생기지 않았음을 확인한다.
6. workflow dedicated route를 explicit path로 collect하여 74 node ID set을 pre/post 비교한다.
7. exact-subject runner 함수를 직접 호출하는 동일 external driver로 required execution-role source set, supporting resolved-import-edge diagnostic, explicit direct-dependency row, sorted required-dependency path set/count/hash를 `S_impl`과 `S_validation`에서 각각 materialize하고 exact 비교한다.
8. consolidation identity map 35 rows의 path, Git blob, raw hash 및 `old_test_id` set을 비교한다.
9. count equality만으로 PASS하지 않고 added/removed identity set을 모두 출력한다.
10. `S_validation`의 direct parent를 selected `validation_predecessor`와 비교하고 parent-relative changed path set이 contract/regression 두 파일뿐인지 확인한다. `S_authority`가 존재하면 그 parent가 `S_impl`이고 `S_impl..S_authority` changed path set이 exact owner amendment 한 파일뿐인지도 확인한다.

Expected post-change invariants:

```text
unclassified = 0
multiply_classified = 0
unexplained_policy_entry_but_file_absent = 0
tracked_test_source_path_delta = 0
configured_added_nodes = 0
configured_removed_nodes = 0
configured_denominator_delta = 0
duplicate_configured_node_identity = 0
clean_checkout_regression_added_nodes = 0
clean_checkout_regression_removed_nodes = 0
canonical_required_node_id_delta = 0
dedicated_route_added_nodes = 0
dedicated_route_removed_nodes = 0
dedicated_route_node_count = 74
required_dependency_source_set_delta = 0
required_dependency_import_edge_delta = 0
explicit_direct_dependency_row_delta = 0
required_dependency_added_paths = 0
required_dependency_removed_paths = 0
required_dependency_inventory_hash_delta = 0
consolidation_identity_count = 35
consolidation_identity_set_drift = 0
repository_reality_baseline = S_impl
mutation_authority_subject = S_impl | S_authority
S_validation_parent = mutation_authority_subject
S_validation_parent_relative_changed_path_count = 2
S_authority_parent = S_impl when present
S_authority_changed_path_count = 1 when present
```

올바른 per-file role 판정이 expected delta와 다른 collection change를 요구하면 canonical gate 전에 중지하고 Change 3의 owner disposition부터 새 transaction으로 다시 수행한다.

---

### Change 7 — Focused validation and static review

Purpose:

canonical long gate 전에 correction의 국소 정합성과 no-semantic-change 경계를 검증한다.

Files:

- Changed: none; this change only validates the correction subject
- Read-only: changed contract/regression files and workflow consolidation dedicated test route
- external focused receipts

Implementation Notes:

1. JSON parse, Python syntax, focused source-policy regression을 실행한다.
2. workflow consolidation test suite를 explicit path로 실행한다. 이 실행은 dedicated route evidence이며 configured-current adoption이 아니다.
3. correction diff를 정적으로 검토하여 다음을 확인한다.

   - wildcard/catch-all/implicit allow 없음
   - contract changed-path authority proof 또는 owner amendment 존재
   - selected authority path와 `S_validation` direct-parent relationship 일치
   - optional `S_authority`는 `S_impl` direct successor이며 owner amendment 한 파일 외 delta 없음
   - test deletion/rename/skip/deselect 없음
   - regression test는 기존 target function body만 변경되었고 새 test function/import/node 없음
   - configured policy mutation 없음
   - current-required precedence 유지
   - actual exhaustive census target path 모두 분류되고 다른 source에 accidental delta 없음
   - required dependency source/import/direct-row/path/hash delta 없음
   - 35 identity 및 three-family consolidation source semantic change 없음
   - 사용자 dirty worktree 변경 혼입 없음

4. P0/P1 correctness issue 또는 role evidence blocker가 남으면 canonical gate로 진행하지 않는다.

Validation:

```text
json_parse_exit = 0
py_compile_exit = 0
focused_source_policy_exit = 0
workflow_dedicated_route = 74 passed
workflow_dedicated_route_S_impl = 74 passed
workflow_dedicated_route_S_validation = 74 passed
clean_checkout_regression_node_id_delta = 0
required_dependency_inventory_delta = 0
static_review_correctness_blocker_count = 0
```

74 count가 exact subject에서 달라지면 단순 count update를 하지 않고 added/removed node ID를 설명한다.
별도 independent-review gate의 수행 여부와 reviewer identity는 owner-reserved field로 기록하며, owner가 요구한 경우 review 완료 전 canonical gate로 진행하지 않는다.

---

### Change 8 — Receipt-bound canonical full-gate re-entry

Purpose:

corrected exact subject에서 canonical source-policy preflight가 통과하고 pytest가 실제로 시작되는지 확인한다.

Files:

- Changed: none; canonical tooling and contract are validation inputs at this stage.
- Read-only: `Iris/validation/clean_checkout/invoke_receipt_bound_full_gate.ps1`
- Read-only: `Iris/validation/clean_checkout/run_iris_clean_checkout_validation.py`
- Read-only: `Iris/validation/clean_checkout/contracts/full_repository_gate.json`
- External outputs: work/result/orchestration roots

Implementation Notes:

1. `S_validation` commit/tree가 clean checkout과 일치하는지 확인한다.
2. Run A/B 전에 chronology receipt의 `repository_reality_baseline=S_impl`, `mutation_authority_subject=S_impl|S_authority`, `validation_predecessor`, `validation_subject=S_validation`이 selected branch와 일치하는지 확인한다.
3. repository 밖 dedicated Python environment receipt를 사용한다.
4. 기존 receipt-bound wrapper를 사용하며 manual pytest success로 대체하지 않는다.
5. receipt-bound wrapper를 서로 다른 external work/result/orchestration root로 Run A와 Run B에 각각 실행한 뒤 기존 `invoke_deterministic_compare.ps1`로 두 receipt chain을 비교한다. Disposable checkout, environment restoration, external output projection, Run A/B identity contract를 그대로 따른다.
6. 다음 stage를 별도로 기록한다.

   ```text
   launcher preflight
   source census/classification
   dependency closure
   disposable checkout/bootstrap
   pytest started/completed
   standalone validations
   cleanup/hygiene
   receipt binding
   ```

7. numeric exit code만으로 failure cause를 추정하지 않는다.
8. `S_impl` 또는 optional `S_authority`의 이전 focused/reviewer/canonical result를 재사용하지 않는다.
9. correction-boundary receipt에는 `S_impl`/`S_validation`의 required-dependency path-set/hash equality와 clean-checkout regression node equality를 함께 결속한다. Optional `S_authority`가 존재하면 그 commit/tree, parent, amendment path/blob/hash도 포함한다.
10. Run A와 Run B 중 dependency-closure stage를 완료한 각 canonical result의 `required_dependency_inventory.path_count`, `sha256`, `explicit_direct_dependency_rows`를 `S_validation` direct-runner driver receipt와 비교한다. 이 gate-side cross-check가 PASS해야 dependency inventory invariance를 independent confirmation으로 사용할 수 있다.

Validation:

```text
validation_subject_commit = S_validation commit
validation_subject_tree = S_validation tree
repository_reality_baseline = S_impl
mutation_authority_subject = S_impl | S_authority
validation_predecessor = mutation_authority_subject
S_validation_descends_directly_from_validation_predecessor = true
source_policy_preflight = PASS
pytest_started = true
target_unclassified_failure_absent = true
run_A_subject = S_validation
run_B_subject = S_validation
Run_A_B_denominator_identity = equal when deterministic comparator is performed
Run_A_B_dependency_inventory_identity = equal when deterministic comparator is performed
Run_A_B_canonical_result_identity = equal when contract reaches comparable completion
gate_vs_driver_dependency_inventory_identity = equal for each run completing dependency closure
Case_B_deterministic_compare = not_performed_due_to_downstream_nonzero
Case_B_Run_A_B_denominator_identity = not_compared_due_to_downstream_nonzero
Case_B_Run_A_B_dependency_inventory_identity = not_compared_due_to_downstream_nonzero
```

---

### Change 9 — Append-only evidence adoption, scoped closeout, and downstream separation

Purpose:

source-classification 해결 상태와 canonical full-gate 전체 결과를 exact subject에 결속하고, 외부 Run A/B evidence를 다음 append-only successor pair에 채택해 과대 claim 없이 종료한다.

Files:

- Read-only: repository-external closeout summary와 canonical orchestration/full-run/failure receipts
- Changed in `S_closeout`: `Iris/validation/clean_checkout/evidence/full_repository_gate_manifest_successor_<next>.json`
- Changed in `S_closeout`: `Iris/validation/clean_checkout/authority/full_repository_technical_debt_closeout_successor_<next>.json`

Implementation Notes:

1. Run A/B가 끝난 뒤 single writer가 latest predecessor pair를 다시 확인하고 다음 unused successor ID를 예약한다. 경합이 있으면 ID와 predecessor binding을 재계산한다.
2. `S_closeout`은 `S_validation`의 direct successor이며 위 두 새 JSON만을 포함하는 append-only evidence-adoption commit이다. Successor content에는 `repository_reality_baseline=S_impl`, optional `mutation_authority_subject=S_impl|S_authority`, `validation_subject=S_validation`, symbolic `evidence_adoption_subject=S_closeout`, `S_closeout_is_validation_subject=false`, `authority_effect=evidence_only`, `tests_rerun_for_S_closeout=false`를 명시한다.
3. 외부 receipt를 repository에 복사해 validation subject인 것처럼 취급하지 않는다. Successor에는 외부 path, content hash, retrieval method/command identity와 Run A/B/comparator 상태를 결속한다.
4. closeout status는 sealed vocabulary `{complete, partial, blocked}` 중 하나만 사용하며 다음 세 case로 기록한다.
5. 모든 case에서 top-level four-role documentation과 canonical five-role code의 차이를 `governance_document_code_divergence=recorded_open_followup`으로 기록한다. 이는 이번 classification result를 차단하거나 top-level 문서를 이 transaction에서 수정한다는 뜻이 아니다.

```text
Case A:
closeout_status = complete
classification_alignment_state = complete
source_policy_problem = resolved
source_policy_preflight = PASS
pytest_started = true
canonical_full_gate = PASS
deterministic_compare = PASS

Case B:
closeout_status = partial
classification_alignment_state = complete
source_policy_problem = resolved
source_policy_preflight = PASS
pytest_started = true
canonical_full_gate = FAIL
downstream_defect = separately_attributed
deterministic_compare = not_performed_due_to_downstream_nonzero
Run_A_B_denominator_identity = not_compared_due_to_downstream_nonzero
Run_A_B_dependency_inventory_identity = not_compared_due_to_downstream_nonzero
gate_vs_driver_dependency_inventory_identity = equal for each run completing dependency closure

Case C:
closeout_status = blocked
classification_alignment_state = blocked
source_policy_problem = unresolved
source_policy_preflight = FAIL
pytest_started = false
canonical_full_gate = blocked_before_pytest

All cases:
governance_document_code_divergence = recorded_open_followup
```

In-repository successor는 자기 자신의 commit/tree를 내용에 넣지 않는다. Commit 뒤 생성하는 repository-external final adoption receipt가 `S_closeout` commit/tree와 두 successor blob/hash를 기록하여 self-reference 없이 evidence-adoption identity를 닫는다.

최종 external summary에는 다음 identity를 포함한다.

```text
S_impl commit/tree
S_authority commit/tree, parent, amendment path/blob/hash, if present
mutation_authority_subject identity
S_validation commit/tree
S_validation direct-parent identity
S_closeout commit/tree
canonical contract blob
runner blob
tracked-source census identity
classification membership identity
configured node-set identity/denominator
clean-checkout regression node-set identity
workflow dedicated-route node-set identity
required dependency source/import/direct-row/path-set/count/hash identity
35-identity map blob/hash
canonical command and interpreter/environment receipt
Run A/B orchestration/full-result receipt path/hash and external retrieval identity
deterministic comparator receipt/hash, or exact not-produced reason
native exit and failure stage
pytest_started
source-policy result
canonical gate result
receipt path/hash
downstream failure identity, if any
governance_document_code_divergence status, owner/follow-up reference
```

Validation:

- receipt subject binding exact
- predecessor evidence unchanged
- source-policy and downstream status separated
- sealed closeout vocabulary only
- evidence successor pair is the only `S_closeout` tracked delta
- `S_closeout` direct parent is `S_validation`
- optional `S_authority` chronology and single-file delta are exact
- `S_validation` remains the validation subject; no PASS inheritance to `S_closeout`
- no release/runtime/compatibility claim expansion

---

## 7. Validation Plan

### Automated Validation

모든 명령은 PowerShell에서 실행한다. `<...>` placeholder는 실행 시 확정한 clean exact path와 repository-external path로 치환한다.

#### 1. Exact subject lock

```powershell
$repo = [System.IO.Path]::GetFullPath('<clean-S_impl-S_authority-or-S_validation-checkout>')
$expectedCommit = '<expected-commit>'
$expectedTree = '<expected-tree>'
$actualCommit = (& git -C $repo rev-parse HEAD).Trim()
if ($LASTEXITCODE -ne 0) { throw 'commit read failed' }
$actualTree = (& git -C $repo rev-parse 'HEAD^{tree}').Trim()
if ($LASTEXITCODE -ne 0) { throw 'tree read failed' }
$status = @(& git -C $repo status --porcelain=v1 --untracked-files=all)
if ($LASTEXITCODE -ne 0) { throw 'status read failed' }
if ($actualCommit -ne $expectedCommit -or $actualTree -ne $expectedTree) {
  throw 'exact subject mismatch'
}
if ($status.Count -ne 0) { throw 'checkout is not clean' }
```

Expected: native exit `0`, exact commit/tree match, status rows `0`.

#### 1A. Generated-cache hygiene

각 direct Python/pytest command 전후 exact checkout에서 다음을 확인한다.

```powershell
$beforeStatus = @(& git -C $repo status --porcelain=v1 --untracked-files=all)
if ($LASTEXITCODE -ne 0 -or $beforeStatus.Count -ne 0) { throw 'pre-command checkout is not clean' }

# Python command uses: uv run python -B ...
# Pytest command additionally uses: -p no:cacheprovider

$afterStatus = @(& git -C $repo status --porcelain=v1 --untracked-files=all)
if ($LASTEXITCODE -ne 0) { throw 'post-command status read failed' }
$cacheRows = @($afterStatus | Where-Object {
  $_ -match '(__pycache__/|\.pyc$|(^|/)\.pytest_cache/)'
})
if ($cacheRows.Count -ne 0) { throw 'generated cache hygiene failure' }
if ($afterStatus.Count -ne 0) { throw 'validation command dirtied exact checkout' }
```

Expected: before/after status rows `0`, generated cache rows `0`. 예상하지 못한 cache가 생기면 path/status를 receipt에 기록하고 해당 disposable checkout을 폐기한 뒤 새 exact checkout에서 command를 재실행한다. Dirty authoring worktree에서 cache cleanup을 수행하지 않는다.

#### 2. Approved tooling surface and changed-path authority

Mutation 전에 Phase 0 ratification과 later append-only authority chain을 exact path 기준으로 검사한다.

```text
regression_test_path_in_phase0_OR_05 = true
runner_path_in_phase0_OR_05 = true
canonical_contract_path_in_phase0_OR_05 = false
canonical_contract_later_authority_precedent = proven
owner_changed_path_disposition = approved
owner_amendment_identity = required_if_precedent_is_insufficient
authority_path = no_amendment | amendment_required
```

Expected: contract mutation authority가 exact predecessor identity에 결속되어야 한다. Later precedent만으로 승인 여부가 모호하면 classification mutation을 시작하지 않고 owner amendment-only `S_authority`를 먼저 발행한다. Authority가 충분하면 `S_authority`를 만들지 않는다.

#### 2A. Conditional authority chronology lock

Selected authority path를 receipt에 고정한 뒤 parent와 changed path set을 검증한다.

```powershell
$repo = [System.IO.Path]::GetFullPath('<clean-repository-containing-subject-objects>')
$freezeReceipt = Get-Content -Raw -LiteralPath '<sealed-change-2-authority-path-receipt>' | ConvertFrom-Json
$subjectReceipt = Get-Content -Raw -LiteralPath '<sealed-S_validation-subject-receipt>' | ConvertFrom-Json
$authorityPath = [string]$freezeReceipt.authority_path
if ($authorityPath -notin @('no_amendment', 'amendment_required')) {
  throw 'invalid sealed authority path'
}
$sImpl = [string]$freezeReceipt.repository_reality_baseline.commit
$sValidation = [string]$subjectReceipt.validation_subject.commit
$sAuthority = $null
$amendmentPath = $null

if ($authorityPath -eq 'amendment_required') {
  $authorityBinding = Get-Content -Raw -LiteralPath '<post-S_authority-identity-binding-receipt>' | ConvertFrom-Json
  $sAuthority = [string]$authorityBinding.authority_subject.commit
  $amendmentPath = [string]$freezeReceipt.owner_designated_amendment.path
  if ($authorityBinding.amendment.path -ne $amendmentPath) {
    throw 'S_authority binding does not match sealed amendment path'
  }
}

$expectedValidationParent = if ($authorityPath -eq 'amendment_required') { $sAuthority } else { $sImpl }
$validationParents = ((& git -C $repo rev-list --parents -n 1 $sValidation).Trim() -split '\s+')
if ($LASTEXITCODE -ne 0 -or $validationParents.Count -ne 2) {
  throw 'S_validation must be a single-parent commit'
}
$actualValidationParent = $validationParents[1]
if ($actualValidationParent -ne $expectedValidationParent) {
  throw 'S_validation predecessor mismatch'
}

$validationDelta = @(& git -C $repo diff-tree --no-commit-id --name-only -r $sValidation | Sort-Object)
if ($LASTEXITCODE -ne 0) { throw 'S_validation delta read failed' }
$expectedValidationDelta = @(
  'Iris/validation/clean_checkout/contracts/full_repository_gate.json'
  'Iris/validation/clean_checkout/tests/test_iris_clean_checkout_validation.py'
) | Sort-Object
if (@(Compare-Object $validationDelta $expectedValidationDelta).Count -ne 0) {
  throw 'S_validation delta is not the exact two-file correction'
}

if ($authorityPath -eq 'amendment_required') {
  $authorityParents = ((& git -C $repo rev-list --parents -n 1 $sAuthority).Trim() -split '\s+')
  if ($LASTEXITCODE -ne 0 -or $authorityParents.Count -ne 2) {
    throw 'S_authority must be a single-parent commit'
  }
  $actualAuthorityParent = $authorityParents[1]
  if ($actualAuthorityParent -ne $sImpl) {
    throw 'S_authority predecessor mismatch'
  }
  $authorityDelta = @(& git -C $repo diff-tree --no-commit-id --name-only -r $sAuthority)
  if ($LASTEXITCODE -ne 0 -or $authorityDelta.Count -ne 1 -or $authorityDelta[0] -ne $amendmentPath) {
    throw 'S_authority must contain exactly the owner amendment artifact'
  }
  $authorityTree = (& git -C $repo rev-parse "$sAuthority^{tree}").Trim()
  $amendmentBlob = (& git -C $repo rev-parse ("{0}:{1}" -f $sAuthority, $amendmentPath)).Trim()
  if ($LASTEXITCODE -ne 0) { throw 'S_authority identity read failed' }
} elseif ($subjectReceipt.mutation_authority_subject.commit -ne $sImpl) {
  throw 'no-amendment path must use S_impl as mutation authority subject'
}
```

`authority_path`는 검증자가 결과를 보고 입력하지 않고 Change 2.14의 sealed receipt에서만 읽는다. `amendment_required` 경로에서는 freeze receipt와 post-`S_authority` binding receipt의 content hash도 먼저 검증하고, amendment JSON 내부 predecessor path/blob/hash가 reservation receipt의 latest applicable authority identity와 같으며 승인 scope가 이번 canonical contract path와 exhaustive target set으로 제한되는지 확인한다. `no_amendment` 경로에서는 post-`S_authority` binding receipt나 authority commit identity가 존재하지 않는지 확인한다. 단순 changed-file count만으로 authority-chain 연결을 PASS하지 않는다.

Expected receipt identities:

```text
repository_reality_baseline = S_impl commit/tree
mutation_authority_subject = S_impl | S_authority
validation_predecessor = mutation_authority_subject
validation_subject = S_validation
S_authority commit/tree/parent/amendment path/blob/content hash = exact when present
S_authority internal authority-chain predecessor = reserved latest identity when present
S_validation parent and two-file delta = exact
```

#### 3. Full-repository source census

```powershell
uv run python -B Iris/validation/clean_checkout/run_iris_clean_checkout_validation.py `
  source-census `
  --repo <exact-checkout> `
  --commit <exact-commit> `
  --output-root <new-external-census-root> `
  --full-repository
```

Pre-change expected: source classification stage에서 non-zero. 현재 runner의 dict-comprehension은 첫 unclassified source에서 즉시 예외를 발생시키므로 이 command는 baseline failure-stage 증거일 뿐 exhaustive census가 아니다. `fail_fast_output_is_full_census=false`를 receipt에 기록한다.

별도의 repository-external read-only exhaustive census driver를 두 exact subject에서 실행한다. Driver는 tracked `test_*.py`를 전부 열거하고 canonical raw category membership 및 per-source projection을 끝까지 수집하되 repository file을 변경하지 않는다. Receipt에는 driver path/hash, command hash, interpreter identity, subject commit/tree, complete-enumeration marker, source path-set/count/hash를 포함한다.

Post-change expected: canonical command native exit `0`, exhaustive receipt의 unclassified `0`, target source가 exact `dedicated_route_validation` rows로 나타남. Planning reference tracked source 144와 target 10은 강제 expected 값이 아니며 actual exhaustive path set/count가 다르면 그 actual을 기준으로 expected-delta 및 owner disposition을 mutation 전에 재봉인한다.

#### 4. Contract parse and syntax

```powershell
uv run python -B -c "import json, pathlib; json.loads(pathlib.Path('Iris/validation/clean_checkout/contracts/full_repository_gate.json').read_text(encoding='utf-8'))"

uv run python -B -m py_compile `
  Iris/validation/clean_checkout/tests/test_iris_clean_checkout_validation.py
```

Expected: 각 command native exit `0`.

#### 5. Focused classification regression

```powershell
uv run python -B -m pytest -s -q -p no:cacheprovider `
  Iris/validation/clean_checkout/tests/test_iris_clean_checkout_validation.py::test_full_source_policy_classifies_only_declared_fallback
```

Expected: native exit `0`, exact existing node PASS. 새 test function이나 node ID를 추가하는 대안은 허용하지 않는다.

#### 6. Clean-checkout regression and canonical-required node identity

`S_impl`과 `S_validation` 각각에서 `Iris/validation/clean_checkout/tests/test_iris_clean_checkout_validation.py`의 collect-only node ID set과 canonical required-node projection을 외부 receipt로 materialize한다.

Expected:

```text
clean_checkout_regression_added_nodes = 0
clean_checkout_regression_removed_nodes = 0
target_existing_node_present_pre = true
target_existing_node_present_post = true
canonical_required_added_nodes = 0
canonical_required_removed_nodes = 0
```

#### 7. Workflow dedicated route

```powershell
uv run python -B -m pytest -s -q -p no:cacheprovider `
  Iris/validation/test_workflow_consolidation/tests
```

동일 command를 먼저 clean `S_impl`, 이후 clean `S_validation`에서 각각 실행한다. Expected planning baseline: 양쪽 모두 `74 passed`, native exit `0`. Pre/post `--collect-only` node list를 별도 저장하고 exact set equality를 검사한다. `S_impl` pre-change 실행이 native exit `0`이 아니면 74-node no-semantic-change baseline이 성립하지 않으므로 mutation/canonical gate를 중지하고 owner에게 disposition을 요청한다.

#### 8. Configured current collection identity

```powershell
uv run python -B -m pytest -s --collect-only -q -p no:cacheprovider `
  --round3-contract=current `
  --round3-enforce-denominator `
  --round3-denominator-receipt <external-result-root>\configured-current-collection.json
```

Expected: native exit `0`; pre/post node ID set, denominator, duplicate count가 동일. Planning reference `collected=471`, `denominator=645`는 exact execution에서 재확인한다.

#### 9. Required dependency inventory invariance

Repository-external read-only driver로 `S_impl`과 `S_validation` 각각에서 다음을 materialize한다. Driver는 `importlib` 기반 exact-file load로 해당 checkout의 `run_iris_clean_checkout_validation.py`를 직접 import하고, ambient worktree module을 사용하지 않는다.

```text
required execution-role source set                         # direct runner function output/projection
resolved recursive import edge set                         # supporting structural diagnostic
explicit direct-dependency rows                            # direct runner function output
sorted required-dependency path set/count/hash              # direct runner function output
```

Driver는 runner logic을 복제하지 않고 exact module의 `_full_required_source_roles()`, `_required_dependency_paths()`, `_validate_explicit_required_dependencies()`를 직접 호출한다. Receipt에는 subject commit/tree, runner Git blob ID/raw SHA-256, loaded module absolute path, driver source/path/hash, command/interpreter identity를 결속한다. Direct call이 불가능하면 자체 재구현 결과로 대체하지 않고 validation을 중지한다.

Runner public result가 import edge set을 직접 노출하지 않으므로 edge detail에 필요한 traversal glue는 실제 runner `_imports()`와 resolver를 사용한다. 이 edge-set equality는 drift detector이지만 구조적 결론의 재진술인 `supporting_structural_diagnostic`으로 표시하며, 그 PASS만으로 dependency inventory의 독립 확인을 주장하지 않는다.

Expected:

```text
required_dependency_source_set_delta = 0
required_dependency_import_edge_delta = 0
explicit_direct_dependency_row_delta = 0
required_dependency_added_paths = 0
required_dependency_removed_paths = 0
required_dependency_inventory_hash_delta = 0
dependency_driver_calls_exact_runner_functions = true
dependency_driver_runner_blob_matches_subject = true
import_edge_measurement_class = supporting_structural_diagnostic
```

Dedicated-route registration이 required execution role이나 imports를 바꾸지 않으므로 expected delta는 0이다. Pre/post direct runner-function output이 이를 만족하지 못하면 canonical gate 전에 중지한다. Post-change canonical Run A/B에서는 dependency-closure stage를 완료한 각 gate result의 `required_dependency_inventory.path_count`, `sha256`, `explicit_direct_dependency_rows`를 `S_validation` driver receipt와 exact 비교한다. 이 gate-side comparison이 PASS한 경우에만 path/count/hash/direct-row invariance를 runner execution과 교차 확인되었다고 기록한다.

#### 10. Consolidation 35-identity invariance

`S_impl`과 `S_validation`의 다음 file을 Git object 기준으로 비교한다.

```text
Iris/_docs/refactor/test_scenario_execution_consolidation/identity_map.jsonl
```

Expected:

```text
row_count = 35
git_blob = e39c810a4f7e9d024173ed37e4facdda7835c5e6
raw_sha256 = ee6a73c018b965d050eeeb95851b7261d7afe67a59ac0a7005b4f027ffb45888
old_test_id_set_delta = 0
```

Blob/hash가 달라지면 classification-only correction이 아니므로 canonical gate 전에 중지한다.

#### 11. Final receipt-bound canonical Run A/B gate

```powershell
powershell -ExecutionPolicy Bypass -File .\Iris\validation\clean_checkout\invoke_receipt_bound_full_gate.ps1 `
  -RepositoryRoot <exact-repository-root> `
  -Commit <S_validation-commit> `
  -ClaimId <source-classification-alignment-claim-id> `
  -EnvironmentReceipt <external-environment-receipt> `
  -WorkRoot <new-external-run-a-work-root> `
  -ResultRoot <new-external-run-a-result-root> `
  -OrchestrationReceipt <external-run-a-orchestration-receipt>

$runAExit = $LASTEXITCODE

powershell -ExecutionPolicy Bypass -File .\Iris\validation\clean_checkout\invoke_receipt_bound_full_gate.ps1 `
  -RepositoryRoot <exact-repository-root> `
  -Commit <S_validation-commit> `
  -ClaimId <source-classification-alignment-claim-id> `
  -EnvironmentReceipt <external-environment-receipt> `
  -WorkRoot <new-external-run-b-work-root> `
  -ResultRoot <new-external-run-b-result-root> `
  -OrchestrationReceipt <external-run-b-orchestration-receipt>

$runBExit = $LASTEXITCODE

if ($runAExit -eq 0 -and $runBExit -eq 0) {
  powershell -ExecutionPolicy Bypass -File .\Iris\validation\clean_checkout\invoke_deterministic_compare.ps1 `
    -RepositoryRoot <exact-repository-root> `
    -Commit <S_validation-commit> `
    -ClaimId <source-classification-alignment-claim-id> `
    -EnvironmentReceipt <external-environment-receipt> `
    -RunAOrchestrationReceipt <external-run-a-orchestration-receipt> `
    -RunBOrchestrationReceipt <external-run-b-orchestration-receipt> `
    -AttemptRoot <new-external-deterministic-comparison-root>
  if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
} else {
  Write-Output "Run A exit=$runAExit; Run B exit=$runBExit; inspect stage-bound receipts"
  if ($runAExit -ne 0) { exit $runAExit }
  exit $runBExit
}
```

Expected minimum: Run A/B 모두 source-policy preflight PASS, pytest started, target unclassified error absent. Comparator native exit `0`은 두 run이 전체 comparable completion에 도달했을 때만 요구한다. 어느 run이 pytest 이후 unrelated nonzero로 종료되면 comparator는 실행하지 않고 `deterministic_compare=not_performed_due_to_downstream_nonzero`, Run A/B denominator/dependency equality는 `not_compared_due_to_downstream_nonzero`로 기록한다. 단, dependency closure를 완료한 각 run의 gate inventory와 `S_validation` direct-runner driver receipt 대조는 comparator와 독립적으로 수행한다. Failure stage와 receipt를 별도로 보존하고 classification 해결 상태를 분리하며 comparator PASS 또는 Run A/B equality를 추정하지 않는다.

#### 12. Append-only closeout successor validation

Run A/B 판정 후 single writer가 next-unused gate-manifest/authority-closeout successor pair만 추가한 `S_closeout`을 만든다. Commit 전 latest predecessor를 다시 읽고 충돌 시 successor ID와 predecessor binding을 갱신한다.

Expected:

```text
S_closeout_tracked_delta = exactly_two_new_successor_json_files
S_closeout_parent = S_validation
validation_subject = S_validation
evidence_adoption_subject = S_closeout
S_closeout_is_validation_subject = false
S_closeout_authority_effect = evidence_only
tests_rerun_for_S_closeout = false
external_receipt_path_hash_retrieval_identity = complete
closeout_status in {complete, partial, blocked}
```

새 successor pair의 JSON parse, predecessor identity, `S_impl`/optional `S_authority`/`S_validation` fields, Run A/B receipt hashes, comparator receipt 또는 not-produced reason을 검증한다. `S_closeout`의 direct parent가 `S_validation`인지 확인한다. Commit 뒤 repository-external final adoption receipt에서 `S_closeout` commit/tree와 새 successor 두 개의 Git blob/content hash를 검증한다. 이 검증은 evidence 채택 무결성 확인이며 `S_closeout`에 `S_validation`의 test PASS를 상속하지 않는다.

### Manual Validation

- correction diff에서 actual exhaustive target path가 exact file rows로만 추가됐는지 확인한다. Planning count 10과 다르면 actual receipt를 우선한다.
- 각 reason이 실제 test purpose를 설명하고 filename-only 문구가 아닌지 확인한다.
- Phase 0/later authority/owner disposition이 contract changed path를 실제로 승인하는지 확인한다.
- selected authority path에 따라 optional `S_authority`와 `S_validation` parent/delta chronology가 정확한지 확인한다.
- owner disposition이 contract의 existing vocabulary와 일치하는지 확인한다.
- configured source policy JSON과 `pytest.ini`가 byte-identical인지 확인한다.
- workflow test source 및 three-family consolidation implementation이 byte-identical인지 확인한다.
- pre/post receipts의 commit/tree, interpreter, environment receipt, contract/runner blob이 올바른지 확인한다.
- pre/post required-dependency inventory와 clean-checkout regression/canonical-required node identity가 동일한지 확인한다.
- external dependency driver가 exact subject runner blob을 직접 load/call했고 gate-side inventory와 교차 확인됐는지 확인한다.
- 모든 validation command 전후 generated cache 및 dirty status가 0인지 확인한다.
- full-gate FAIL이면 stderr text가 아니라 receipt의 stage와 pytest-start evidence로 source-policy 해결 여부를 판정한다.
- independent-review requirement와 reviewer identity는 owner-reserved field에 owner 결정대로 기록한다.
- `S_closeout`이 external evidence를 채택하는 append-only successor일 뿐 validation subject가 아닌지 확인한다.

Project Zomboid in-game 수동 검증은 수행하지 않는다. runtime/product surface 변경이 없기 때문이다.

### Validation Limits

- no Project Zomboid runtime validation
- no Lua behavior or package parity validation
- no multiplayer or long-session validation
- no external mod compatibility sweep
- no performance certification
- no Registry Runtime Compatibility remediation
- no public text or semantic quality validation
- no release, Workshop, B42 or deployment validation
- no correction of unrelated failure reached after pytest starts
- no terminal PASS inheritance from `S_impl` or any predecessor
- no validation PASS inference from optional authority-only `S_authority`
- no terminal PASS inheritance from `S_validation` to evidence-only `S_closeout`

---

## 8. Risk Surface Touch

### Authority Surface

변경 있음.

`Iris Repository Validation / Clean-Checkout Reproducibility Authority`의 `source_disposition_policy.explicit_dedicated_route_sources`에 tracked source identity를 추가한다. Phase 0 OR-05 surface에 canonical contract path가 없으므로 later append-only authority precedent와 owner disposition을 exact changed path에 결속한다. 불충분하면 classification mutation 전에 amendment-only `S_authority`를 `S_impl`의 direct successor로 발행하고 `S_validation`의 immediate predecessor로 사용한다. Category vocabulary, current-required precedence, required dependency closure, configured pytest policy는 변경하지 않는다.

### Runtime Behavior Surface

None.

Iris runtime Lua, UI, data, package, Project Zomboid state를 변경하지 않는다.

### Compatibility Surface

제품 compatibility surface는 None이다.

Validation compatibility surface에서는 configured denominator와 dedicated-route collection identity가 metadata amendment 전후 동일해야 한다.

### Sealed Artifact Surface

기존 predecessor evidence와 consolidation 35-identity map은 read-only다.

Canonical contract blob은 additive correction으로 변경되므로 `S_validation`의 새 blob identity를 receipt에 결속한다. 기존 evidence/authority JSON을 rewrite하지 않는다.

Owner amendment가 필요한 경로에서만 `S_authority`가 owner-designated append-only amendment 한 파일을 추가한다. `S_authority` parent는 `S_impl`, `S_validation` parent는 `S_authority`이며 commit/tree/amendment blob/hash를 보존한다. Amendment가 불필요하면 `S_authority`는 존재하지 않고 `S_validation` parent는 `S_impl`이다.

External Run A/B 뒤 next-unused gate-manifest/authority-closeout successor pair를 append-only `S_closeout`으로 추가한다. 이는 evidence-only adoption이며 `S_closeout`을 validation subject로 만들거나 test PASS를 상속하지 않는다.

### Public-Facing Output Surface

None.

Iris menu, Tooltip, public copy, release text, package output을 변경하지 않는다.

---

## 9. Risk Analysis

### Architecture Risk

- **로드맵의 네 범주를 코드보다 우선하는 위험:** 현재 codebase에는 `dedicated_route_validation`이 존재한다. 이를 무시하면 전용 validation route를 historical/obsolete/fixture로 잘못 분류할 수 있다.
- **dual authority 생성:** canonical contract와 configured source policy JSON에 같은 disposition을 복제하면 두 source-of-truth가 생긴다.
- **explicit current precedence 훼손:** dedicated registration helper나 test를 수정하면서 current-required override를 약화할 수 있다.
- **directory-level 추론:** 같은 root라는 이유만으로 10개를 검토 없이 일괄 분류할 수 있다.
- **changed-path authority gap:** Phase 0 approved tooling surface에 canonical contract path가 없는데 later precedent를 자동 승인으로 간주할 수 있다.
- **conditional subject chronology 혼입:** owner amendment를 `S_validation` correction delta에 섞거나, amendment-required 경로에서도 `S_validation` predecessor를 `S_impl`로 기록할 수 있다.
- **external driver 순환 확증:** runner semantics를 별도로 재구현한 결과를 runner-independent verification처럼 사용할 수 있다.
- **문서/코드 vocabulary divergence:** top-level 문서는 네 role을 설명하지만 canonical code는 `dedicated_route_validation`을 포함한 다섯 role을 구현한다.

Mitigation: authority/consumer localization, `S_impl -> optional S_authority -> S_validation` parent/delta lock, exact-path owner disposition/amendment, exact runner-function direct call과 gate-result cross-check, 파일별 evidence, canonical contract 단일 amendment, raw membership audit, closeout의 `governance_document_code_divergence` 기록.

### Runtime Risk

- 제품 runtime risk는 없다.
- test runtime에서 dedicated source를 required denominator에 잘못 편입하면 full-gate 실행량과 result identity가 바뀔 수 있다.
- `test_public_text_phase7_scenario.py`는 current-route test class를 import하므로 role을 current-required로 오판할 수 있다.
- classification-only metadata change라도 hidden import/dependency projection을 놓치면 canonical required-dependency inventory가 바뀔 수 있다.

Mitigation: execution role과 imported assertion origin을 구분하고 predeclared node/denominator delta `0` 및 directly measured required-dependency path/hash delta `0`을 강제한다.

### Compatibility Risk

- configured pytest collection과 canonical full-repository census의 taxonomy를 혼동할 수 있다.
- source count 144, workflow nodes 74, consolidation identities 35, configured denominator를 같은 지표로 취급할 수 있다.
- current dirty worktree의 unrelated source-policy manifest 변경이 correction subject에 섞일 수 있다.
- pre-change `source-census` fail-fast 출력이나 planning count 144/10을 exhaustive inventory로 오인할 수 있다.

Mitigation: fail-fast stage receipt와 exhaustive external census receipt 분리, 각 축의 exact identity receipt 분리, clean S_impl successor 사용, dirty overlay 배제.

### Regression Risk

- 첫 reported target만 고치면 나머지 9개에서 다음 fail-closed가 발생한다.
- 같은 path를 두 category에 등록해도 dict overwrite 때문에 apparent classification이 하나처럼 보일 수 있다.
- regression test를 새 file로 만들면 새 file 자체가 unclassified source가 될 수 있다.
- regression assertions를 인접 새 function으로 분리하면 canonical required node identity와 regression route node delta 0 계약을 깨뜨릴 수 있다.
- 최초 target만 자기참조를 검사하면 canonical contract를 읽는 다른 target의 self-registration feedback loop를 놓칠 수 있다.
- full-gate가 pytest 이후 실패했을 때 해결된 classification을 다시 unresolved로 기록하거나, 반대로 pytest_started만으로 남은 classification gap을 무시할 수 있다.
- post-run receipt를 commit해 validated subject를 바꾸는 자기참조 closeout을 만들 수 있다.
- 동시에 둘 이상의 writer가 append-only successor ID를 예약하면 predecessor/latest chain이 충돌할 수 있다.

Mitigation: exhaustive target-set 전체 self-reference audit, raw declaration exclusivity audit, exact existing regression function body-only change, stage-separated closeout, external receipts, single-writer reservation과 commit 직전 latest-predecessor 재검증.

---

## 10. Rollback Plan

1. `S_impl`은 immutable predecessor로 유지한다.
2. correction이 잘못된 경우 `S_validation`에서 다음 bounded delta만 새 revert successor로 되돌린다.

   - `full_repository_gate.json`의 이번 dedicated-route rows
   - `test_iris_clean_checkout_validation.py`의 이번 regression assertions

3. scenario consolidation implementation, 35 identity map, workflow source contents, runtime payload correction, 현재 사용자 worktree 변경은 되돌리지 않는다.
4. 실패한 pre-repair/post-repair/canonical receipt는 삭제하거나 PASS로 rewrite하지 않는다.
5. owner가 dedicated-route role을 승인하지 않거나 파일별 근거가 닫히지 않으면 다음 상태를 유지한다.

   ```text
   classification_role_unresolved
   source_policy_problem_unresolved
   canonical_gate_blocked
   ```

6. 새 correction이 필요하면 새 successor commit/tree와 새 external receipt root를 사용한다. 이전 `S_validation` result를 다른 tree에 상속하지 않는다.
7. rollback은 분류 gap을 복원하므로 rollback 자체를 PASS 경로로 취급하지 않는다. Rollback successor의 closeout은 `blocked` 또는 이미 확보한 일부 증거 범위의 `partial`로만 기록한다.
8. 후속 corrected successor가 필요하면 새 exact subject에서 focused/census/dependency/route/canonical Run A/B를 다시 실행하고 새 append-only closeout successor에 채택해야 한다.
9. 이미 발행한 `S_closeout` successor는 삭제하거나 revert하지 않는다. 새 successor가 supersession과 사유를 append-only로 기록한다.
10. 이미 발행한 `S_authority`는 append-only authority history이므로 correction rollback에 섞어 삭제하거나 rewrite하지 않는다. Amendment가 더 이상 적용되지 않음을 기록해야 하면 owner가 새 authority successor로 supersede한다.

---

## 11. Governance Constraints

- `docs/Philosophy.md` 준수: Iris는 근거 기반 정보 모드이며 PZ runtime은 100% Lua다. 이번 repository-validation correction은 runtime/product role로 확장하지 않는다.
- Pulse 및 다른 submod dependency boundary를 건드리지 않는다.
- canonical full-repository gate는 exact tracked subject에 결속하며 predecessor PASS 상속은 금지한다.
- focused/configured/dedicated-route PASS는 canonical full-repository PASS를 대체하지 않는다.
- explicitly current-required source는 filename/historical heuristic보다 우선한다.
- unclassified source는 fail-closed이며 unknown allow, skip, implicit historical 또는 excluded fallback을 만들지 않는다.
- classification authority와 configured discovery projection을 분리한다.
- source classification은 exact path별 additive amendment로 수행하고 wildcard/catch-all을 사용하지 않는다.
- mutation 전에 모든 changed path가 approved authority surface에 있는지 확인하고, 없는 canonical contract path는 later precedent plus owner disposition 또는 explicit owner amendment로 승인한다.
- explicit owner amendment가 필요하면 `S_impl -> S_authority -> S_validation` chronology를 사용한다. `S_authority`는 amendment 한 파일만, `S_validation`은 direct parent 대비 contract/regression 두 파일만 포함한다.
- owner amendment가 불필요하면 `S_authority`를 만들지 않고 `S_impl -> S_validation` chronology를 사용한다.
- evidence는 `repository_reality_baseline`, `mutation_authority_subject`, `validation_predecessor`, `validation_subject`, `evidence_adoption_subject`를 별도 identity로 보존한다.
- owner-reserved `not_applicable_dedicated_route` disposition 없이 dedicated role을 authoritative contract에 기록하지 않는다.
- test 삭제, rename, skip, deselect, source relocation으로 gate를 우회하지 않는다.
- regression coverage는 기존 `test_full_source_policy_classifies_only_declared_fallback` function body만 확장하며 새 test function/source/import/node를 추가하지 않는다.
- predecessor evidence는 append-only successor 원칙을 지키며 rewrite하지 않는다.
- closeout successor는 single writer만 예약/commit하고, reservation 직전과 commit 직전에 latest predecessor identity를 재검증한다.
- external Run A/B가 실제 실행되어 orchestration/full-result 또는 failure-stage receipt가 생성된 경우에 한해 evidence-only `S_closeout` successor pair를 반드시 발행하며 `S_validation`만 validation subject로 유지한다. Mutation 미승인 등으로 Run A/B가 시작되지 않은 경로에는 `S_closeout` 발행 의무가 없다.
- execution work/result/receipt와 temporary output은 repository 밖에 둔다.
- validation은 PowerShell 및 `uv run python`을 사용하고 native exit `0`일 때만 해당 focused command를 PASS로 기록한다.
- canonical wrapper의 environment receipt, disposable checkout, Run A/B, denominator/dependency/result identity contract를 축소하지 않는다.
- source-policy resolution과 downstream failure를 별도 상태로 기록한다.
- failure stage는 numeric exit code 추정이 아니라 orchestration/stage receipt와 log identity로 결정한다.
- sealed closeout status vocabulary는 `{complete, partial, blocked}`만 사용한다.
- 별도 independent-review requirement 및 reviewer identity는 owner-reserved다.
- canonical full-gate PASS를 release, deployment, Workshop, B42, Registry, Publish 또는 runtime readiness로 확장하지 않는다.

---

## 12. Expected Closeout State

Expected target: Case A에서만 `complete`; Case B 및 focused-only 상태는 `partial`; pre-pytest classification 차단은 `blocked`.

`complete`는 다음 조건을 모두 만족할 때만 사용한다.

```text
all tracked test sources classified by current canonical authority
unclassified = 0
multiply_classified = 0
unexplained reverse mismatch = 0
workflow target sources classified exactly once
self-reference risk sources = 0 or owner-dispositioned before mutation
configured node/denominator unexplained delta = 0
clean-checkout regression node ID delta = 0
workflow dedicated route node-set drift = 0
S_impl workflow dedicated route = 74 passed
S_validation workflow dedicated route = 74 passed
required dependency source/import/direct-row/path/hash drift = 0
35 consolidation identity drift = 0
focused validation native exit = 0
canonical source-policy preflight = PASS
pytest_started = true
canonical full gate = PASS
deterministic comparator = PASS
receipt bound to exact S_validation commit/tree
Run A/B and comparator external receipt identities = complete
scenario consolidation semantic change = 0
changed-path authority = proven or owner-amended before mutation
repository reality baseline = exact S_impl
mutation authority subject = exact S_impl or S_authority
S_authority parent/single-file delta = exact when amendment is required
S_authority = absent when amendment is unnecessary
S_validation direct parent = mutation authority subject
S_validation direct-parent-relative delta = exact contract/regression two-file correction
append-only evidence successor pair = committed as S_closeout
S_closeout direct parent = S_validation
S_closeout authority effect = evidence_only
```

최종 결과는 다음처럼 표현한다.

- canonical full-gate 전체 PASS 및 comparator PASS, evidence-only `S_closeout` 채택 완료: `complete`, `classification_alignment_state=complete`, `canonical_full_gate=PASS`
- pytest 진입 후 unrelated nonzero: `partial`, `classification_alignment_state=complete`, `canonical_full_gate=FAIL`, `downstream_defect=separate`, `deterministic_compare=not_performed_due_to_downstream_nonzero`
- source-policy 단계 재차 차단: `blocked`, classification problem unresolved
- owner disposition 또는 role evidence 미확정: `blocked`, mutation not authorized
- focused validation만 끝나고 canonical gate 미실행: `partial`, `partial_reason=implemented_only`, complete claim 금지
- external Run A/B evidence가 아직 append-only `S_closeout`에 채택되지 않음: 최대 `partial`, complete claim 금지

이 계획의 완료가 자동으로 의미하지 않는 항목은 다음과 같다.

- Iris 전체 test suite green
- Registry Runtime Compatibility PASS
- Project Zomboid in-game equivalence
- package/release/Workshop/B42/deployment readiness
- 성능 개선
- 전체 validation infrastructure의 무결성 증명

최대 허용 claim은 다음으로 제한한다.

```text
Iris tracked test-source classification is aligned with the exact corrected repository subject;
the canonical clean-checkout source-policy preflight passes;
the canonical full gate reaches pytest execution;
the resulting evidence is bound to that exact S_validation subject;
and an append-only evidence-only S_closeout successor adopts the external receipts without becoming the validation subject.
```
