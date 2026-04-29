# Iris DVF 3-3 Identity Fallback Residual Round Final Integrated Execution Plan

> 상태: FINAL v1.0  
> 기준일: 2026-04-16  
> 상위 기준: `docs/Philosophy.md`, `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`  
> 선행 문서: `docs/Iris/Done/iris-dvf-3-3-identity-fallback-source-expansion-execution-plan.md`, `docs/Iris/Done/iris-dvf-3-3-identity-fallback-source-expansion-walkthrough.md`  
> authority input: `Iris/build/description/v2/staging/identity_fallback_source_expansion/phase6_subset_rollout/exec_subset_600_wrench_crowbar_b7_b8_b9/subset_distribution_remeasurement.json`, `Iris/build/description/v2/staging/identity_fallback_source_expansion/phase3_taxonomy_manifest/phase3_residual_taxonomy_manifest.json`, `Iris/build/description/v2/staging/identity_fallback_source_expansion/phase3_taxonomy_manifest/phase3_residual_taxonomy_alignment_report.json`  
> 목적: `600 promoted / residual 17 / cluster budget 30/30` closeout 이후, `phase3_taxonomy_pending 10`을 frozen-budget residual round로 재분류해 `existing-cluster absorption`, 제한적 `direct_use`, `carry_forward_hold` 셋 중 하나로 deterministic하게 닫는 후속 실행 계획을 고정한다.  
> 실행 상태: authority implementation complete. Current closeout snapshot은 `absorption 2 / direct_use 4 / carry_forward_hold 4`이며, current-state artifact는 `Iris/build/description/v2/staging/identity_fallback_source_expansion/residual_round/residual_round_manifest.json`, `Iris/build/description/v2/staging/identity_fallback_source_expansion/residual_round/residual_round_status.md`, `Iris/build/description/v2/staging/identity_fallback_source_expansion/residual_round/closeout/residual_round_closeout_note.md`를 기준으로 읽는다.

> 이 문서는 기존 `identity_fallback source expansion` 실행 계획을 대체하지 않는다.  
> current cycle closeout 이후의 별도 frozen-budget residual round를 정의하는 후속 운영 계획 문서다.

---

## 0. 이 round가 아닌 것

아래 해석은 이번 round 전체에서 금지한다.

- current source expansion cycle의 same-session continuation
- `phase3_taxonomy_pending 10`을 자동 promote debt로 읽는 것
- `31번째` net-new cluster를 추가하는 것
- `bucket_3_scope_hold 7`을 실행 범위로 다시 여는 것
- publish exposure 변경, runtime Lua overwrite, manual in-game validation을 이번 round 실행과 섞는 것
- cluster budget `30`을 조용히 올리는 것

즉 이번 round는 닫힌 source expansion cycle의 연장이 아니라, `600 / 17` baseline 위에서 여는 별도 residual-only round다.

---

## 1. Opening baseline 고정

### 1-1. 수치 baseline

| 항목 | 값 |
|---|---|
| promoted executable subset | `600` |
| runtime path | `cluster_summary 2040 / identity_fallback 17 / role_fallback 48` |
| publish split | `internal_only 617 / exposed 1467` |
| residual accounting baseline | `17 = phase3_taxonomy_pending 10 / bucket_3_scope_hold 7` |
| active execution scope | `phase3_taxonomy_pending 10` |
| hold accounting scope | `bucket_3_scope_hold 7` |
| cluster budget | `30 / 30` |

`bucket_3_scope_hold 7`은 active execution에서는 봉인 유지지만, baseline accounting에서는 residual `17` 안에 계속 포함된다.  
다음 round에서 residual을 `10`으로 오해하지 않도록 `17` 전체 계상과 `10` 실행 범위를 분리해 함께 명시한다.

### 1-2. Authority baseline input 7종

1. `docs/DECISIONS.md`
2. `docs/ROADMAP.md`
3. `docs/ARCHITECTURE.md`
4. `docs/Iris/Done/iris-dvf-3-3-identity-fallback-source-expansion-walkthrough.md`
5. `Iris/build/description/v2/staging/identity_fallback_source_expansion/phase6_subset_rollout/exec_subset_600_wrench_crowbar_b7_b8_b9/subset_distribution_remeasurement.json`
6. `Iris/build/description/v2/staging/identity_fallback_source_expansion/phase3_taxonomy_manifest/phase3_residual_taxonomy_manifest.json`
7. `Iris/build/description/v2/staging/identity_fallback_source_expansion/phase3_taxonomy_manifest/phase3_residual_taxonomy_alignment_report.json`

### 1-3. Manifest 읽기 규칙

`phase3_residual_taxonomy_manifest.json`은 current residual의 item inventory와 source/evidence context를 고정하는 authority input이다.  
다만 manifest 내부의 `cluster_id`, `expected_promotion_path`, `expected_path`는 closeout 직전 taxonomy note이며, frozen-budget residual round에서 곧바로 실행 경로를 강제하지는 않는다.

이번 round의 route selection authority는 아래 셋으로 다시 닫는다.

- `existing-cluster absorption`
- 제한적 `direct_use`
- `carry_forward_hold`

### 1-4. Frozen invariant

- `cluster_count_limit = 30`
- `bucket_3_scope_hold 7`은 execution scope 밖에서 봉인 유지
- publish split은 이번 round에서 직접 변경하지 않음
- 허용 경로는 `existing-cluster absorption`, `direct_use`, `carry_forward_hold` 셋뿐

---

## 2. Scope lock

### 2-1. Execution scope: `phase3_taxonomy_pending 10`

아래 표의 `primary path`는 item-level triage 시작점이다.  
이 표는 global waterfall이 아니라, 각 item이 어떤 경로를 먼저 검토할지 선언하는 운영 표다.

| # | item_id | primary path | fallback path | initial batch |
|---|---|---|---|---|
| 1 | `Base.ClubHammer` | `existing-cluster absorption` | 제한적 `direct_use` 가능 시 `batch_weapon`, 아니면 `carry_forward_hold` | `batch_hammer` |
| 2 | `Base.WoodenMallet` | `existing-cluster absorption` | 제한적 `direct_use` 가능 시 `batch_weapon`, 아니면 `carry_forward_hold` | `batch_hammer` |
| 3 | `Base.Sledgehammer` | `existing-cluster absorption` | 제한적 `direct_use` 가능 시 `batch_weapon`, 아니면 `carry_forward_hold` | `batch_hammer` |
| 4 | `Base.Sledgehammer2` | `existing-cluster absorption` | 제한적 `direct_use` 가능 시 `batch_weapon`, 아니면 `carry_forward_hold` | `batch_hammer` |
| 5 | `Base.Katana` | `direct_use` | `existing-cluster absorption` 적합 시 허용, 불가 시 `carry_forward_hold` | `batch_weapon` |
| 6 | `Base.LeadPipe` | `direct_use` | `existing-cluster absorption` 적합 시 허용, 불가 시 `carry_forward_hold` | `batch_weapon` |
| 7 | `Base.Nightstick` | `direct_use` | `existing-cluster absorption` 적합 시 허용, 불가 시 `carry_forward_hold` | `batch_weapon` |
| 8 | `Base.HandScythe` | `manual_validation` | validation 결과에 따라 `existing-cluster absorption` / `direct_use` / `carry_forward_hold` | `batch_handscythe` |
| 9 | `Base.Rope` | `existing-cluster absorption` | `carry_forward_hold` | `batch_tail` |
| 10 | `farming.WateredCan` | `existing-cluster absorption` | `carry_forward_hold` | `batch_tail` |

### 2-2. Out-of-scope

- `bucket_3_scope_hold 7`
- `role_fallback` lane 관련 작업
- publish exposure 변경, runtime Lua overwrite, manual in-game validation
- `A-4-1 rework / cluster budget` round opening

### 2-3. Accounting 분리 원칙

- baseline accounting scope: residual `17` 전체를 항상 계상
- active execution scope: `phase3_taxonomy_pending 10`
- hold accounting scope: `bucket_3_scope_hold 7`

`7`은 baseline에서 제거되는 것이 아니라, 이번 round 실행 밖에서 계속 계상된다.  
closeout 이후에도 `resolved 10 + frozen hold 7 = residual 17 baseline lineage`가 깨지지 않아야 한다.

### 2-4. Scope lock artifact contract

round scope lock artifact는 아래 파일로 고정한다.

- `Iris/build/description/v2/staging/identity_fallback_source_expansion/residual_round/scope_lock/residual_round_scope_lock.json`

최소 필드:

- `round_opening_baseline`
- `residual_accounting_baseline`
- `in_scope_count`
- `out_of_scope_hold_count`
- `cluster_budget_frozen`
- `cluster_count_limit`
- `permitted_paths`

### 2-5. Staging root와 디렉터리 규칙

새 round 산출물은 아래 루트로 고정한다.

- `Iris/build/description/v2/staging/identity_fallback_source_expansion/residual_round/`

이 루트는 닫힌 source expansion cycle 아래에 있지만, same-cycle continuation으로 읽지 않는다.  
오해 방지를 위해 아래 README를 함께 둔다.

- `Iris/build/description/v2/staging/identity_fallback_source_expansion/residual_round/README.md`

README 한 줄:

> 이 디렉터리는 closed source expansion cycle의 continuation이 아니라 별도 frozen-budget residual round다.

하위 디렉터리는 문서 section 번호가 아니라 기능명으로 고정한다.

- `scope_lock/`
- `triage/`
- `batches/batch_hammer/`
- `batches/batch_weapon/`
- `batches/batch_handscythe/`
- `batches/batch_tail/`
- `closeout/`

---

## 3. Triage 규칙

### 3-1. Item-level primary path 선언

triage는 모든 item이 absorption → direct_use → hold의 global waterfall을 강제로 밟는 방식으로 읽지 않는다.  
대신 Section 2-1의 `primary path`를 먼저 선언하고, 각 item은 자기 primary path의 fit check를 먼저 수행한다.

운영 원칙:

- absorption-primary item은 absorption fit을 먼저 본다.
- direct_use-primary item은 direct_use fit을 먼저 본다.
- manual-validation-primary item은 static/manual source 확인부터 수행한다.
- `carry_forward_hold`는 모든 item의 universal fallback이다.

### 3-2. `existing-cluster absorption` fit check

absorption-primary item 또는 absorption fallback item은 아래 조건을 모두 만족해야 한다.

- 기존 30개 cluster 중 item의 interaction context를 semantic drift 없이 수용할 수 있다.
- 기존 `cluster_summary`, `sentence_plan`, `slot_sequence`를 재정의하지 않고 item을 흡수할 수 있다.
- 기존 member와 granularity 충돌이 없다.
- 흡수를 위해 사실상 `31번째 cluster`가 필요하지 않다.

위 조건을 만족하면 `existing-cluster absorption` 확정이다.

### 3-3. 제한적 `direct_use` fit check

`direct_use`는 round-level default가 아니라 예외 경로다.  
다만 `Base.Katana`, `Base.LeadPipe`, `Base.Nightstick`은 item-level primary path를 `direct_use`로 선언하고 시작한다.

direct_use는 아래 조건을 모두 만족해야 한다.

- current pipeline에 `direct_use` path가 이미 구현되어 있다.
- cluster summary 없이 item-specific use를 단독으로 3-3 body에 고정할 수 있다.
- `identity_fallback` 대비 content quality gain이 명확하다.
- 범주형 추론이 아니라 item-specific evidence로 닫을 수 있다.

absorption-primary item은 absorption fit 실패 후에도 위 조건을 충족할 때만 `direct_use` fallback으로 넘어간다.

### 3-4. `Base.HandScythe` manual validation

`Base.HandScythe`는 농업/절단 맥락과 전투 맥락이 섞여 있어 별도 검토한다.

이번 round에서 말하는 manual validation은 아래만 뜻한다.

- 정적 source 재확인
- distribution / recipe / context outcome / existing cluster fit의 수동 판독
- 필요 시 소수의 deterministic sample inspection

이번 round에서 manual validation이 뜻하지 않는 것은 아래다.

- publish exposure 변경
- runtime Lua overwrite
- manual in-game validation

validation 결과는 `existing-cluster absorption`, 제한적 `direct_use`, `carry_forward_hold` 셋 중 하나로만 귀결된다.

### 3-5. `carry_forward_hold`와 abort 조건

primary path와 fallback path가 모두 성립하지 않으면 해당 item은 `carry_forward_hold`로 닫는다.  
이것은 실패가 아니라 frozen budget 아래의 governance decision이다.

아래 셋 중 하나가 확인되면 즉시 실행을 중단하고 `carry_forward_hold`로 분류한다.

| 조건 | 의미 |
|---|---|
| A | 닫으려면 사실상 `31번째 cluster`가 필요하다고 확인됨 |
| B | absorption을 하려면 기존 cluster semantic을 재정의해야 함 |
| C | direct_use로 닫으려면 item-specific evidence가 아니라 범주형 추론이 필요함 |

reopen 조건은 아래 둘뿐이다.

- 별도 `A-4-1 rework / cluster budget` round
- `future_new_source_discovery_hold`

### 3-6. Triage artifact contract

triage 산출물은 아래 둘로 고정한다.

- `Iris/build/description/v2/staging/identity_fallback_source_expansion/residual_round/triage/residual_round_triage_manifest.json`
- `Iris/build/description/v2/staging/identity_fallback_source_expansion/residual_round/triage/residual_round_triage_alignment_report.json`

`residual_round_triage_manifest.json` 최소 필드:

- `item_id`
- `primary_path`
- `triage_path`
- `triage_reason`
- `target_cluster_id`
- `batch_assignment`

`residual_round_triage_alignment_report.json` 최소 체크:

- `cluster_count_after_triage <= 30`
- path별 count 합계 `= 10`
- `phase3_taxonomy_pending 10` item set과 triage manifest item set 일치

---

## 4. 공통 Gate 기준

모든 배치에 동일하게 적용한다. 하나라도 위반되면 해당 배치는 닫히지 않는다.

| Gate | 기준 |
|---|---|
| hard_fail | `0` |
| exposed_rendered_change | `0` |
| residual_accounting | opening residual `17`의 lineage가 `resolved 10 + frozen hold 7`로 끝까지 추적 가능 |
| requeue_tolerability | 이전 closeout baseline 이하 |
| lane_stability | `role_fallback`, 기존 `cluster_summary`, 기존 exposed surface에 side effect 없음 |
| cluster_count | `<= 30` |
| runtime_row_inflation | `0` |
| publish_split_change | `0` |

publish split은 downstream validation lane의 별도 decision 없이 이번 round에서 바꾸지 않는다.

---

## 5. 실행 — Batch A/B/C/D

모든 batch result artifact는 경로 결과 필드를 `final_path`로 통일한다.  
batch별 메모 필드는 추가될 수 있지만, closeout 집계는 공통적으로 `item_id / primary_path / final_path / target_cluster_id / preview_rendered_hash / gate_result`를 기준으로 읽는다.

### Batch A — Hammer fit batch (`batch_hammer/`)

대상:

- `Base.ClubHammer`
- `Base.WoodenMallet`
- `Base.Sledgehammer`
- `Base.Sledgehammer2`

이 배치의 primary path는 `existing-cluster absorption`이다.  
다만 fit check 실패 후 item-specific evidence로 단독 closure가 가능한 경우에만 `batch_weapon`으로 fallback 재배정한다.

실행 절차:

1. 기존 30개 cluster 중 striking / demolition / construction 계열 후보를 추출한다.
2. item별 absorption fit을 판정한다.
3. fit 성공 item은 기존 cluster 기반 draft를 작성한다.
4. fit 실패 item은 `direct_use` fallback 적격 여부를 다시 판정한다.
5. direct_use 부적격 item은 `batch_tail`로 재배정해 `carry_forward_hold` 후보로 보낸다.

산출물:

- `Iris/build/description/v2/staging/identity_fallback_source_expansion/residual_round/batches/batch_hammer/batch_hammer_result.json`

최소 필드:

- `item_id`
- `primary_path`
- `final_path`
- `target_cluster_id`
- `preview_rendered_hash`
- `gate_result`
- `fallback_reason`

### Batch B — Weapon direct-use batch (`batch_weapon/`)

대상:

- `Base.Katana`
- `Base.LeadPipe`
- `Base.Nightstick`
- Batch A에서 `direct_use` fallback으로 재배정된 item

이 배치의 primary path는 `direct_use`다.  
모든 item에 absorption을 먼저 강제하지 않는다.

실행 절차:

1. current `direct_use` path 구현과 current `direct_use 12` precedent를 확인한다.
2. item별 direct_use 적격 여부를 판정한다.
3. 적격 item은 `facts patch`와 `decisions patch` draft를 작성한다.
4. direct_use 부적격 item은 existing-cluster absorption fallback을 다시 본다.
5. 두 경로 모두 불가하면 `batch_tail`로 재배정한다.

산출물:

- `Iris/build/description/v2/staging/identity_fallback_source_expansion/residual_round/batches/batch_weapon/batch_weapon_result.json`

최소 필드:

- `item_id`
- `primary_path`
- `final_path`
- `target_cluster_id`
- `preview_rendered_hash`
- `gate_result`
- `fallback_reason`

### Batch C — HandScythe validation batch (`batch_handscythe/`)

대상:

- `Base.HandScythe`

이 배치는 `Base.HandScythe`의 static/manual validation만 담당한다.

실행 절차:

1. 정적 source와 distribution evidence를 수동 검토한다.
2. harvest-side context와 combat context 중 현재 budget 아래에서 safe representative path가 있는지 확인한다.
3. 결과를 `existing-cluster absorption`, `direct_use`, `carry_forward_hold` 셋 중 하나로 확정한다.
4. 선택된 경로에 맞는 candidate draft를 작성하고 preview gate를 확인한다.

산출물:

- `Iris/build/description/v2/staging/identity_fallback_source_expansion/residual_round/batches/batch_handscythe/batch_handscythe_result.json`

최소 필드:

- `item_id`
- `primary_path`
- `final_path`
- `target_cluster_id`
- `validation_note`
- `preview_rendered_hash`
- `gate_result`

### Batch D — Tail classification batch (`batch_tail/`)

대상:

- `Base.Rope`
- `farming.WateredCan`
- 이전 배치에서 `carry_forward_hold` 또는 tail recheck로 재배정된 item

이 배치의 원칙은 억지 promote 금지다.  
이번 round의 목적은 `10`건 전량 소거가 아니라, frozen budget 아래서 deterministic closeout을 늘리는 것이다.

실행 절차:

1. `Base.Rope`, `farming.WateredCan`에 대해 existing-cluster absorption fit을 최종 검토한다.
2. fit 성공 item은 absorption으로 닫는다.
3. fit 실패 item은 `carry_forward_hold`로 닫는다.
4. hold 사유를 `absorption_not_fit`, `direct_use_not_eligible`, `manual_validation_inconclusive` 중 하나로 기록한다.
5. reopen 조건을 `A-4-1 rework round` 또는 `future_new_source_discovery_hold`로 명시한다.

산출물:

- `Iris/build/description/v2/staging/identity_fallback_source_expansion/residual_round/batches/batch_tail/batch_tail_result.json`

최소 필드:

- `item_id`
- `primary_path`
- `final_path`
- `target_cluster_id`
- `hold_reason`
- `preview_rendered_hash`
- `gate_result`

---

## 6. Round closeout

### 6-1. Closeout 조건

아래를 모두 충족할 때만 round를 닫는다.

1. `phase3_taxonomy_pending 10` 전량이 `existing-cluster absorption`, `direct_use`, `carry_forward_hold` 중 하나로 확정된다.
2. `absorption_count + direct_use_count + carry_forward_hold_count = 10`이 성립한다.
3. `resolved 10 + bucket_3_scope_hold 7 = residual 17 lineage`가 유지된다.
4. 모든 배치가 공통 gate 위반 없이 닫힌다.
5. closeout 시점 `cluster_count <= 30`을 유지한다.
6. `role_fallback`, 기존 `cluster_summary`, exposed rendered surface에 무영향이다.

### 6-2. Closeout artifact contract

closeout 산출물은 아래 파일로 고정한다.

- `Iris/build/description/v2/staging/identity_fallback_source_expansion/residual_round/closeout/residual_round_closeout_report.json`

최소 필드:

- `opening_baseline`
- `closing_state`
- `gate_summary`
- `cluster_count_after`
- `runtime_path_after`
- `residual_after`
- `publish_split_after`

`closing_state`는 최소한 아래 count를 포함한다.

- `absorption_count`
- `direct_use_count`
- `carry_forward_hold_count`

### 6-3. Remeasurement artifact

- `Iris/build/description/v2/staging/identity_fallback_source_expansion/residual_round/closeout/residual_round_remeasurement.json`

이 파일은 `subset_distribution_remeasurement.json`과 같은 lineage를 따르되, residual round closeout 이후 분포를 다시 잰 current-state artifact로 둔다.

### 6-4. Post-closeout branch

| 상태 | 판단 |
|---|---|
| `phase3_taxonomy_pending` 완전 소진 | downstream validation lane으로 이행 여부를 별도 판단 |
| `carry_forward_hold` 잔존 | frozen-budget hold로 봉인할지, 별도 `A-4-1 rework / cluster budget` round를 열지 판단 |

이 판단은 closeout 이후에만 내린다. 실행 중에 미리 결정하지 않는다.

---

## 7. Downstream validation lane 분리

아래 항목은 이번 round와 섞지 않는다.

| 항목 | 시점 |
|---|---|
| publish exposure 변경 | round closeout 이후 별도 decision |
| runtime Lua overwrite / reflection apply | round closeout 이후 별도 downstream |
| manual in-game validation | round closeout 이후 별도 downstream |
| `bucket_3_scope_hold 7` 재개방 검토 | 이번 round 바깥 별도 round |
| `A-4-1 rework / cluster budget` round | 이번 round 바깥 별도 설계 round |

---

## 8. 전체 phase 요약

이 section은 무엇이 성공인지가 아니라, 이번 round가 어떤 artifact를 남기는지에만 초점을 둔 artifact map이다.

| Phase | 산출물 | 성격 |
|---|---|---|
| Opening baseline | authority input re-read, baseline freeze | baseline 봉인 |
| Scope lock | `scope_lock/residual_round_scope_lock.json`, `residual_round/README.md` | 경계 봉인 |
| Triage | `triage/residual_round_triage_manifest.json`, `triage/residual_round_triage_alignment_report.json` | item-level 경로 확정 |
| Batch A | `batches/batch_hammer/batch_hammer_result.json` | hammer 계열 fit check |
| Batch B | `batches/batch_weapon/batch_weapon_result.json` | direct_use primary batch |
| Batch C | `batches/batch_handscythe/batch_handscythe_result.json` | static/manual validation |
| Batch D | `batches/batch_tail/batch_tail_result.json` | tail classification |
| Closeout | `closeout/residual_round_closeout_report.json`, `closeout/residual_round_remeasurement.json` | 정산 |

---

## 9. 성공 기준

이 section은 phase 산출물 목록이 아니라 round의 PASS / FAIL 판정 기준만 다룬다.

### 9-1. 최소 성공

- residual round를 current cycle continuation이 아니라 별도 round로 연다.
- `30-cap`을 끝까지 유지한다.
- `phase3_taxonomy_pending 10`에 대해 item별 governance path를 전량 확정한다.
- same-cycle net-new cluster는 `0`이다.
- downstream validation lane 혼합은 `0`이다.
- residual accounting remeasurement를 완료한다.

### 9-2. 좋은 성공

- `10`건 중 일부를 deterministic하게 promote한다.
- 나머지는 억지 승격 없이 hold 또는 future branch로 정리한다.
- 각 item에 대해 `왜 이번 round에서 닫혔는가 / 왜 hold로 남았는가`를 설명할 수 있다.

### 9-3. 실패

- `31번째 cluster`를 사실상 열어놓고도 같은 round라고 주장한다.
- `bucket_3_scope_hold 7`을 baseline accounting에서 누락한다.
- 모든 item에 absorption을 먼저 강제하는 global waterfall로 triage를 다시 읽는다.
- publish / runtime / in-game validation을 본 round에 뒤섞는다.

---

## Appendix A. 문서 self-check

- baseline 수치가 actual authority artifact와 일치하는지 확인한다.
- `phase3_taxonomy_pending 10` item list가 actual manifest와 정확히 일치하는지 확인한다.
- `bucket_3_scope_hold 7`, `31번째 cluster`, downstream validation lane이 본문에서 재개방되지 않는지 확인한다.
- artifact 경로가 기존 `identity_fallback_source_expansion` 산출물과 충돌하지 않는지 확인한다.
- `Base.HandScythe`의 manual validation이 downstream manual in-game validation으로 오해되지 않는지 확인한다.
