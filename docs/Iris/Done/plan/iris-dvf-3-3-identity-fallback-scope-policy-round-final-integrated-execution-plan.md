# Iris DVF 3-3 Identity Fallback Scope Policy Round Final Integrated Execution Plan

> 상태: FINAL v1.0  
> 기준일: 2026-04-16  
> 상위 기준: `docs/Philosophy.md`, `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`  
> 선행 문서: `docs/Iris/Done/iris-dvf-3-3-identity-fallback-residual-round-final-integrated-execution-plan.md`, `docs/Iris/Done/iris-dvf-3-3-identity-fallback-closure-policy-expansion-amendment.md`, `docs/Iris/Done/iris-dvf-3-3-identity-fallback-closure-policy-round-final-integrated-execution-plan.md`  
> authority input: `Iris/build/description/v2/staging/identity_fallback_source_expansion/residual_round/scope_lock/residual_round_scope_lock.json`, `Iris/build/description/v2/staging/identity_fallback_source_expansion/closure_policy_round/closure_policy_round_manifest.json`, `Iris/build/description/v2/staging/identity_fallback_source_expansion/phase6_subset_rollout/exec_subset_600_wrench_crowbar_b7_b8_b9/subset_remaining_identity_fallback_rows.jsonl`, `Iris/build/description/v2/staging/identity_fallback_source_expansion/batches/batch_4_medical_kitchen_explosive_reuse/batch_4_overlay_preview_decisions.jsonl`, `Iris/build/description/v2/staging/identity_fallback_source_expansion/batches/batch_4_medical_kitchen_explosive_reuse/authority_promotion/batch_4_publish_preview.jsonl`  
> 목적: `bucket_3_scope_hold 7`을 별도 scope policy round에서 재검토해, source expansion reopen이나 runtime mutation 없이 `maintain_identity_fallback_isolation` policy closeout으로 전량 확정한다.  
> 실행 상태: authority implementation complete. Current scope policy closeout snapshot은 `policy_scope 7 -> policy_review_closed_maintain_identity_fallback_isolation 7 / hold 0`이며, round-specific artifact는 `Iris/build/description/v2/staging/identity_fallback_source_expansion/scope_policy_round/scope_policy_round_manifest.json`, `Iris/build/description/v2/staging/identity_fallback_source_expansion/scope_policy_round/scope_policy_round_status.md`, `Iris/build/description/v2/staging/identity_fallback_source_expansion/scope_policy_round/closeout/scope_policy_round_closeout_report.json`를 기준으로 읽는다. current-state consumer는 후행 terminal snapshot인 `Iris/build/description/v2/staging/identity_fallback_source_expansion/identity_fallback_terminal_status.json`, `Iris/build/description/v2/staging/identity_fallback_source_expansion/identity_fallback_terminal_handoff.json`를 canonical read point로 사용한다.

> 이 문서는 residual round나 closure policy round를 덮어쓰지 않는다.  
> 이번 round는 out-of-DVF-scope Group C cooking-tool fallback rows에 대한 **scope-policy closeout authority** 만 정의한다.

---

## 0. 이 round가 아닌 것

- source expansion reopen
- cluster budget reopen
- publish exposure 변경
- runtime Lua overwrite
- in-game validation

즉 이번 round는 **scope-policy bookkeeping closeout only** 다.

---

## 1. Opening baseline

### 1-1. Current baseline

| 항목 | 값 |
|---|---|
| selected branch before round | `policy_resolved_scope_hold_only` |
| current terminal unresolved execution | `0` |
| current remaining scope hold | `bucket_3_scope_hold 7` |
| current runtime path | `cluster_summary 2040 / identity_fallback 17 / role_fallback 48` |
| current publish split | `internal_only 617 / exposed 1467` |
| cluster budget | `30 / 30` (frozen) |

### 1-2. In-scope item 7

- `Base.Kettle`
- `Base.MugRed`
- `Base.MugSpiffo`
- `Base.MugWhite`
- `Base.Mugl`
- `Base.Saucepan`
- `Base.Teacup`

이 7건은 공통적으로 아래 조건을 공유한다.

- `bucket_3_out_of_dvf_scope_group_c`
- `cluster_policy_status = policy_excluded`
- `policy_excluded_reason_codes = ["action_only_not_representative"]`
- `publish_decision_reason = identity_fallback_policy_isolation`
- `structural_flag = BODY_LACKS_ITEM_SPECIFIC_USE`

---

## 2. Scope lock

- execution scope는 `bucket_3_scope_hold 7`만 포함한다
- source expansion이나 closure admissibility는 다시 열지 않는다
- 허용 경로는 `maintain_identity_fallback_isolation` 하나뿐이다
- runtime path counts와 publish split은 이번 round에서 직접 바뀌지 않는다

산출물 루트:

- `Iris/build/description/v2/staging/identity_fallback_source_expansion/scope_policy_round/`

---

## 3. Policy fit check

모든 row는 아래를 동시에 만족할 때만 close한다.

- current row가 `bucket_3_scope_hold`
- current row가 `identity_fallback_policy_isolation` publish decision을 이미 갖고 있음
- current row가 `BODY_LACKS_ITEM_SPECIFIC_USE`를 계속 유지함
- current row가 `action_only_not_representative`로 cluster policy exclusion됨
- current round가 이 row를 source expansion candidate로 다시 해석하지 않음

이 조건을 만족하면 final status는 아래로 고정한다.

- `policy_review_closed_maintain_identity_fallback_isolation`

---

## 4. Closeout reading

- `policy_scope 7 -> policy_closed 7 / hold 0`
- selected branch after round: `maintain_identity_fallback_isolation_confirmed`
- runtime delta: `0`
- publish delta: `0`
- residual lineage `17`은 terminal snapshot 기준으로 전량 closed state가 된다

---

## 5. Current-state consumer

round artifact는 historical provenance로 유지한다. current-state consumer는 아래를 canonical read point로 사용한다.

- `Iris/build/description/v2/staging/identity_fallback_source_expansion/identity_fallback_terminal_status.json`
- `Iris/build/description/v2/staging/identity_fallback_source_expansion/identity_fallback_terminal_handoff.json`

이 terminal snapshot 기준 current aggregate는 아래다.

- `existing_cluster_absorption 2`
- `direct_use 8`
- `policy_review_closed_maintain_identity_fallback_isolation 7`
- `active_execution_lane_count 0`
- `no_immediate_next_round_planned = true`

---

## 6. 성공 기준

- `bucket_3_scope_hold 7` 전량 policy closeout
- current runtime unchanged
- current publish split unchanged
- current residual lineage `17` 전량 terminalized
- immediate next round 자동 개시 없음
