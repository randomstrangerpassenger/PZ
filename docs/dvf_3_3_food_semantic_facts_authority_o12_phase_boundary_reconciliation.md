# DVF 3-3 Food Semantic Facts Authority — O-12 Phase Boundary Reconciliation

> 상태: owner-ratified substantive planning reconciliation / independent plan review required before implementation re-entry
>
> 승인일: 2026-07-28
>
> 승인자: repository owner
>
> 승인 근거: `attempt-0021` Codex Reviewer의 0 Critical / 1 Important 판정 뒤, 실제 `text_ko` 반복 골격 검증을 fresh Naturalization attempt로 이관하는 제안에 대한 명시적 `승인`
>
> Machine contract: `Iris/_docs/round3/dvf_3_3_food_semantic_facts_authority_reconstruction/o12_phase_boundary_reconciliation.json`

## 1. Authority and precedence

이 문서는 다음 두 계획의 O-12/Phase 2 교차 계약만 좁게 정정하는 append-only planning reconciliation이다.

- `docs/dvf_3_3_food_semantic_facts_authority_reconstruction_implementation_plan.md`
- `docs/dvf_3_3_korean_prose_naturalization_public_text_rewrite_closure_plan.md`

두 원 계획과 G1 영수증은 수정하지 않는다. 아래 항목에 한해서만 이 문서가 우선하며, 317-row facts authority 범위, Rule/allowlist/lineage/writer/schema/curation/successor 경계와 four-plan stage order는 그대로 유지한다.

이 변경은 coordination-only addendum이 아니다. Terminal predicate의 검증 시점을 바꾸는 substantive planning reconciliation이므로 Codex Reviewer의 독립 계획 검토가 PASS하기 전에는 새 implementation attempt를 열 수 없다.

## 2. Resolved contradiction

원 계획은 다음 세 조건을 동시에 요구했다.

1. `maximum_same_skeleton_group`을 canonical `text_skeleton(text_ko)` detector로 계산한다.
2. Facts round의 actual Phase 2 consumer는 no-render source proposition inventory만 생성한다.
3. Facts round에서는 Naturalization candidate 생성과 Phase 4~8 실행을 금지한다.

역사적 canonical detector는 realized `text_ko`를 입력으로 사용하지만 actual Phase 2 inventory에는 `text_ko`가 없다. 따라서 semantic axis/value profile JSON을 text skeleton으로 대체하는 방식은 실제 최대 반복 골격 수를 과소계산할 수 있는 approximate harness이며 금지된다.

## 3. Amended Facts round Phase 2 contract

Facts round Change 12의 no-render compatibility probe는 다음만 검증한다.

- selected successor facts, input manifest, approved schema와 proposition-license의 exact four-identity consumption
- exact 317 member coverage와 licensed proposition inventory
- compiler-invented proposition 0
- item ID/hash/random/order/synonym-only partition 0
- D10-approved meaningful semantic partition criterion
- current facts read 0과 explicit non-current override
- Naturalization candidate write 0
- Naturalization Phase 4~8 execution 0
- threshold policy와 canonical detector의 immutable identity binding
- semantic profile을 canonical text skeleton으로 대체한 count 0

Facts round는 `maximum_same_skeleton_group`을 계산하거나 PASS로 주장하지 않는다. 다음 상태를 봉인한다.

```text
canonical_text_skeleton_evaluation_state = deferred_to_registry_adopted_fresh_naturalization_attempt
canonical_text_skeleton_evaluation_count = 0
semantic_profile_as_text_skeleton_substitution_count = 0
maximum_same_skeleton_group_claim_emitted_count = 0
threshold_policy_or_detector_modification_count = 0
waiver_added_count = 0
```

`phase12_phase2_handoff/skeleton_group_report.json`은 더 이상 실제 skeleton group 결과가 아니다. 새 implementation attempt는 이를 `phase12_phase2_handoff/canonical_text_skeleton_deferment_report.json`으로 대체하고, 이전 approximate report를 authority input으로 소비하지 않는다.

O-12는 삭제되거나 완화되지 않는다. Facts round terminal에서는 다음으로 닫힌다.

```text
O-12_in_round_disposition = deferred_without_gate_credit
O-12_downstream_owner = fresh Naturalization attempt
O-12_threshold_and_detector_unchanged = true
sealed_successor_handoff_complete_claim_allowed = true
canonical_same_skeleton_acceptance_claim_allowed = false
```

## 4. Amended Naturalization contract

Registry가 successor facts/manifest를 current로 채택하고 exact adoption receipt를 발행한 뒤에만 fresh Naturalization attempt를 Phase 0부터 연다. 그 attempt는 Phase 2 source inventory를 새로 봉인하고, 실제 candidate `text_ko`가 materialize된 최초 phase 뒤 canonical detector를 실행한다.

Downstream O-12 acceptance는 다음을 모두 요구한다.

```text
registry_adoption_receipt = present
fresh_naturalization_attempt = true
phase2_source_inventory_resealed = true
actual_candidate_text_ko_materialized = true
canonical_text_skeleton_detector_identity_match = true
canonical_threshold_policy_identity_match = true
maximum_same_skeleton_group <= bound_threshold_value
detector_modification_count = 0
threshold_modification_count = 0
waiver_added_count = 0
```

실제 검증 실패는 fresh Naturalization attempt의 blocker다. Facts round의 semantic partition 결과, `attempt-0014-remediation`, `attempt-0021`의 approximate profile grouping 또는 prior Publish disposition으로 대체할 수 없다.

## 5. G1 and attempt preservation

G1 receipt와 V0는 변경하거나 재실행하지 않는다.

```text
G1 receipt SHA-256 = 10755804a1d70ed0014ed7d32ee2c4dbe452684b30afad1fddf7cb2ff210f2bf
G1 V0 commit = 2a1741ce2e3ab85b0e5744f88b8a72a5a031b4db
```

이 reconciliation은 G1이 검증한 repository를 수정하지 않고 G2의 acceptance ownership만 정정한다. 새 implementation attempt는 exact G1 receipt를 다시 소비하고 이 reconciliation의 plan-review PASS binding을 추가로 요구한다.

`attempt-0021`은 append-only failed evidence다. 같은 attempt를 고치지 않는다. 이 변경은 terminal predicate와 cross-plan ownership을 바꾸는 구조적 변경이므로 독립 계획 검토 PASS 뒤 새 attempt를 Change 0부터 연다.

## 6. Scope ceiling

이 reconciliation은 다음을 허용하지 않는다.

- Facts round에서 Korean text 또는 Naturalization candidate 생성
- Naturalization Phase 4~8 조기 실행
- Publish Boundary 재시도
- canonical detector, threshold, ratio 또는 waiver 변경
- semantic profile, axis/value JSON 또는 proposition count를 text skeleton으로 재명명
- current facts/manifest, rendered output, Lua, runtime chunk 또는 package 변경
- `attempt-0021` 재작성

