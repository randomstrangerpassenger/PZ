# Iris DVF 3-3 Identity Fallback Closure Policy Round Final Integrated Execution Plan

> 상태: FINAL v1.0  
> 기준일: 2026-04-16  
> 상위 기준: `docs/Philosophy.md`, `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`  
> 선행 문서: `docs/Iris/Done/iris-dvf-3-3-identity-fallback-residual-round-final-integrated-execution-plan.md`, `docs/Iris/Done/iris-dvf-3-3-identity-fallback-closure-policy-expansion-amendment.md`  
> authority input: `Iris/build/description/v2/staging/identity_fallback_source_expansion/residual_round/residual_round_manifest.json`, `Iris/build/description/v2/staging/identity_fallback_source_expansion/residual_round/closeout/residual_round_closeout_report.json`, `Iris/build/description/v2/staging/identity_fallback_source_expansion/residual_round/closeout/residual_round_post_closeout_branch_decision.json`, `Iris/build/description/v2/staging/identity_fallback_source_expansion/residual_round/batches/batch_hammer/batch_hammer_result.json`, `Iris/build/description/v2/staging/identity_fallback_source_expansion/residual_round/batches/batch_tail/batch_tail_result.json`  
> 목적: current residual round closeout 뒤 `carry_forward_hold 4`만 별도 closure policy round에서 다시 평가해, expanded `direct_use` / dominant-context / declared transform-build chain 기준으로 policy-level canonical path를 재확정한다.  
> 실행 상태: authority implementation complete. Current closeout snapshot은 `policy_scope 4 -> direct_use 4 / carry_forward_hold 0`이며, round-specific artifact는 `Iris/build/description/v2/staging/identity_fallback_source_expansion/closure_policy_round/closure_policy_round_manifest.json`, `Iris/build/description/v2/staging/identity_fallback_source_expansion/closure_policy_round/closure_policy_round_status.md`, `Iris/build/description/v2/staging/identity_fallback_source_expansion/closure_policy_round/closeout/closure_policy_round_closeout_report.json`를 기준으로 읽는다. current-state consumer는 후행 terminal snapshot인 `Iris/build/description/v2/staging/identity_fallback_source_expansion/identity_fallback_terminal_status.json`과 `Iris/build/description/v2/staging/identity_fallback_source_expansion/identity_fallback_terminal_handoff.json`를 canonical read point로 사용한다.

> 이 문서는 current residual round closeout을 덮어쓰지 않는다.  
> current residual round는 그대로 historical execution authority로 유지하고, 이 문서는 그 위에서 열린 separate closure policy round authority만 정의한다.

---

## 0. 이 round가 아닌 것

아래 해석은 금지한다.

- current residual round execution을 소급 수정하는 것
- `bucket_3_scope_hold 7`을 이번 round execution scope로 다시 여는 것
- `31번째 cluster`를 열거나 `cluster_count_limit = 30`을 바꾸는 것
- publish exposure 변경, runtime Lua overwrite, manual in-game validation을 이번 round와 섞는 것
- closure policy widening과 `A-4-1 rework / cluster budget` round opening을 같은 일로 읽는 것

즉 이번 round는 **current carry-forward hold `4`에 대한 policy-level reevaluation round** 다.

---

## 1. Opening baseline

### 1-1. Current baseline

| 항목 | 값 |
|---|---|
| residual round selected branch | `maintain_frozen_budget_hold` |
| residual round closing split | `absorption 2 / direct_use 4 / carry_forward_hold 4` |
| current frozen hold accounting before policy round | `carry_forward_hold 4 + bucket_3_scope_hold 7 = 11` |
| current runtime path | `cluster_summary 2040 / identity_fallback 17 / role_fallback 48` |
| current publish split | `internal_only 617 / exposed 1467` |
| cluster budget | `30 / 30` (frozen) |

### 1-2. Policy round execution scope

이번 round의 in-scope는 current residual round closeout에서 `carry_forward_hold`로 남은 `4`건뿐이다.

| # | item_id | previous hold reason | policy round primary path |
|---|---|---|---|
| 1 | `Base.Sledgehammer` | `direct_use_not_eligible` | `direct_use` |
| 2 | `Base.Sledgehammer2` | `direct_use_not_eligible` | `direct_use` |
| 3 | `Base.Rope` | `absorption_not_fit` | `direct_use` |
| 4 | `farming.WateredCan` | `absorption_not_fit` | `direct_use` |

### 1-3. Out-of-scope

- `bucket_3_scope_hold 7`
- current residual round에서 이미 `absorption` 또는 `direct_use`로 닫힌 item
- `A-4-1 rework / cluster budget`
- runtime/publish downstream lane

---

## 2. Scope lock

### 2-1. Scope lock invariant

- execution scope는 `carry_forward_hold 4`만 포함한다
- `bucket_3_scope_hold 7`은 계속 baseline accounting에 포함되지만 execution scope 밖이다
- cluster budget은 계속 `30 / 30` frozen이다
- 이번 round의 허용 경로는 `direct_use`, `existing-cluster absorption`, `carry_forward_hold` 셋뿐이다

### 2-2. Staging root

산출물 루트는 아래로 고정한다.

- `Iris/build/description/v2/staging/identity_fallback_source_expansion/closure_policy_round/`

하위 디렉터리:

- `scope_lock/`
- `triage/`
- `resolution/`
- `closeout/`

---

## 3. Closure policy rules

### 3-1. Expanded `direct_use`

`direct_use`는 weapon-only 예외가 아니라 item-specific evidence로 cluster를 열지 않고 닫는 non-cluster closure path다.

확정 기준:

- item-specific evidence `2`개 이상
- evidence가 같은 대표 작업 맥락으로 수렴
- one-sentence 3-3 body closure 가능
- downstream validation 불요구

### 3-2. dominant/dual-context structural rule

- dominant-context: 주 맥락이 명확하고 부 맥락이 종속적이면 주 맥락으로 닫는다
- dual-context 예외: `compose_profile`과 `slot_sequence`가 구조적으로 수용할 때만 허용한다
- 금지: style naturalness나 문장 인상을 closure admissibility 기준으로 쓰는 것

### 3-3. declared transform/build chain rule

허용:

- recipe transform fact
- build requirement fact
- 짧고 deterministic한 declared transform/build chain

금지:

- chain 전체를 최종 용도로 해석하는 것
- derived utility interpretation

---

## 4. 실행

### 4-1. Triage

이번 round의 triage는 `carry_forward_hold 4`를 expanded `direct_use` 기준으로 다시 읽는다.

- `Base.Sledgehammer`, `Base.Sledgehammer2`
  - demolition-dominant direct_use 검토
- `Base.Rope`
  - declared transform/build chain 기반 direct_use 검토
- `farming.WateredCan`
  - dominant-context 기반 direct_use 검토

### 4-2. Resolution

모든 in-scope item은 아래 둘 중 하나로만 닫는다.

- expanded `direct_use`
- 그래도 admissibility가 불가하면 `carry_forward_hold`

이번 round는 cluster reopen round가 아니므로, `existing-cluster absorption`은 이론상 허용 경로이지만 실제 primary 목표로 쓰지 않는다.

### 4-3. Resolution artifact contract

- `scope_lock/closure_policy_round_scope_lock.json`
- `triage/closure_policy_round_triage_manifest.json`
- `triage/closure_policy_round_triage_alignment_report.json`
- `resolution/closure_policy_round_resolution_result.json`
- `closeout/closure_policy_round_closeout_report.json`
- `closure_policy_round_manifest.json`
- `closure_policy_round_status.md`

`closure_policy_round_resolution_result.json` 최소 필드:

- `item_id`
- `previous_final_path`
- `previous_hold_reason`
- `primary_path`
- `final_path`
- `policy_rule_applied`
- `preview_rendered_hash`
- `gate_result`

---

## 5. Closeout

### 5-1. Closeout 조건

1. `carry_forward_hold 4` 전량이 `direct_use` 또는 `carry_forward_hold`로 다시 확정된다
2. `policy_scope_resolved_count + policy_scope_carry_forward_hold_count = 4`가 성립한다
3. `bucket_3_scope_hold 7`은 계속 봉인 상태로 유지된다
4. `cluster_count <= 30`을 유지한다
5. runtime/publish는 이번 round에서 직접 바뀌지 않는다

### 5-2. Closeout 읽기 규칙

이번 round가 닫히면 current unresolved active hold는 `0`이 되고, 남는 것은 `bucket_3_scope_hold 7` 뿐이다.

즉 closeout 이후 상태는:

- `policy_scope_carry_forward_hold_after = 0`
- `remaining_scope_hold = bucket_3_scope_hold 7`
- `selected_branch_after = policy_resolved_scope_hold_only`

---

## 6. 성공 기준

### 6-1. 최소 성공

- current residual round를 소급 수정하지 않는다
- `carry_forward_hold 4`만 별도 round로 다시 평가한다
- `bucket_3_scope_hold 7`을 건드리지 않는다
- cluster budget `30 / 30`을 유지한다

### 6-2. 좋은 성공

- `carry_forward_hold 4`를 전량 policy-level `direct_use`로 소거한다
- 남는 unresolved active hold 없이 `bucket_3_scope_hold 7`만 봉인 상태로 남긴다
- why-closed가 item별로 구조적으로 설명 가능하다

### 6-3. 실패

- current residual round closeout artifact를 새 round 결과로 덮어쓴다
- derived utility interpretation을 canonical fact처럼 취급한다
- dual-context를 style naturalness로 판단한다
- policy widening 없이 바로 `A-4-1`로 점프한다
