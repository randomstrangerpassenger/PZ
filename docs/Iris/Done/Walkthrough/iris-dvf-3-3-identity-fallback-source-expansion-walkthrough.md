# Iris DVF 3-3 Identity Fallback Source Expansion Walkthrough

_Last updated: 2026-04-16_

## 1. 목적

이 문서는 `identity_fallback 617` source expansion round가 이번 세션에서 실제로 어떻게 설계되고 구현되고, 어디에서 current cycle closeout으로 닫혔는지를 한 번에 따라가기 위한 walkthrough다.

초점은 여섯 가지다.

- 왜 이번 round를 compose 재설계나 style 개선이 아니라 `source evidence 확보` round로 잠갔는가
- `617` baseline이 Phase 0/1에서 어떤 실행 manifest로 분해됐는가
- targeted lane과 reusable bucket이 어떤 batch 순서로 실제 promotion까지 이어졌는가
- partial lane과 residual taxonomy가 어떻게 `600 promoted / 17 residual` 상태로 재측정됐는가
- 왜 publish split은 그대로 유지됐고, 왜 reflection apply / in-game validation은 아직 별도 lane로 남는가
- 왜 current cycle은 `30 / 30` interaction-cluster budget edge에서 멈추고, 다음 작업은 새 round opening으로만 이어져야 하는가

상위 기준은 다음 문서들이다.

- `docs/Philosophy.md`
- `docs/DECISIONS.md`
- `docs/ARCHITECTURE.md`
- `docs/ROADMAP.md`
- `docs/Iris/Done/iris-dvf-3-3-identity-fallback-source-expansion-scope-lock.md`
- `docs/Iris/Done/iris-dvf-3-3-identity-fallback-source-expansion-execution-plan.md`

## 2. 시작점과 끝점

이번 세션의 시작점은 `identity_fallback_source_expansion_backlog.json`이 이미 canonical handoff input으로 정렬된 상태였다.

시작 baseline:

- total rows: `2105`
- active / silent: `2084 / 21`
- active origin: `cluster_summary 1440 / identity_fallback 617 / role_fallback 48`
- publish split: `internal_only 617 / exposed 1467`
- backlog bucket split: `bucket_1 11 / bucket_2 599 / bucket_3 7`

이번 세션의 종료점은 다음과 같다.

- executable subset promote: `600`
- current runtime path counts: `cluster_summary 2040 / identity_fallback 17 / role_fallback 48`
- current residual split: `phase3_taxonomy_pending 10 / bucket_3_scope_hold 7`
- current publish split: `internal_only 617 / exposed 1467`
- current interaction cluster seed budget: `30 / 30`
- current source expansion cycle closeout와 후속 round handoff 기준이 `DECISIONS / ROADMAP / ARCHITECTURE`에 반영됨

중요한 점은 이번 세션이 계획 문서만 적은 세션이 아니라는 것이다. 실제로 `scope lock -> execution manifest -> batch authoring -> subset rollout -> residual taxonomy remeasurement -> budget-edge closeout`까지 current cycle 안에서 닫았다.

## 3. 가장 중요한 결론

이번 세션의 핵심 결론은 일곱 줄로 요약된다.

- 이번 round의 canonical input은 `phaseE_contract_migration`의 `identity_fallback_source_expansion_backlog.json`으로 고정됐다.
- Phase 1 manifest 결과 `bucket_2`는 `targeted 589 / partial 10`, execution label은 `mapping-patch 593 / new-cluster-only 6`으로 잠겼다.
- executable subset은 `batch 1~4`, `batch 5a`, `bucket_1 wrench/crowbar`, `batch 7~9`를 통해 `600`건까지 실제 promotion preview와 staged authority까지 올라갔다.
- current publish split은 바뀌지 않았다. 이번 round는 source promotion round이지 publish exposure 재판정 round가 아니기 때문이다.
- current residual inventory는 `17 = phase3_taxonomy_pending 10 + bucket_3_scope_hold 7`로 다시 고정됐다.
- current cycle은 `interaction cluster budget 30 / 30`에 도달했고, 이 상태는 same-cycle continuation point가 아니라 terminal budget edge다.
- 따라서 next work는 current session의 unfinished queue가 아니라 새 baseline 위의 후속 residual round로만 읽어야 한다.

## 4. 전체 흐름

실행 흐름은 크게 10단계였다.

1. source expansion round의 scope lock과 execution plan을 `docs/Iris/Done`에 작성한다.
2. reviewer feedback을 반영해 B-path accounting, cumulative regression protection, lexical authority 기준을 execution plan에 명시한다.
3. `build_identity_fallback_source_expansion_phase0_1.py`로 Phase 0/1 baseline snapshot과 execution manifest를 생성한다.
4. targeted lane `batch_1 ~ batch_4`를 구현해 대형 mapping-patch subset을 먼저 닫는다.
5. partial lane의 `batch_5a`를 실행하고, residual `6`은 Phase 3 taxonomy artifact로 분리한다.
6. `bucket_1` reusable rows 중 `Wrench / PipeWrench / Crowbar`를 fast-lane으로 승격시키고 cumulative subset에 합친다.
7. residual family 중 `Glue / Woodglue`, `Charcoal`, `WeldingRods`를 새 cluster 안에서 executable subset으로 추가한다.
8. `phase6` cumulative subset rollout과 `phase3` residual taxonomy manifest를 계속 갱신해 `600 / 17` closeout baseline을 만든다.
9. `validate_interaction_cluster_seed.py`를 통해 cluster seed budget이 `30 / 30`에 도달했음을 확인한다.
10. `30-cap 유지 + next residual round 분리`를 `DECISIONS / ROADMAP / ARCHITECTURE`에 반영하고 current cycle을 닫는다.

아래부터는 이 순서를 그대로 따라간다.

## 5. Phase 0/1: Scope Lock과 Execution Manifest

가장 먼저 닫은 것은 코드보다 범위였다.

핵심 문서:

- `docs/Iris/Done/iris-dvf-3-3-identity-fallback-source-expansion-scope-lock.md`
- `docs/Iris/Done/iris-dvf-3-3-identity-fallback-source-expansion-execution-plan.md`

이 문서들에서 이번 round를 다음처럼 봉인했다.

- compose 재설계 round가 아니다.
- style round가 아니다.
- active/silent 의미 재정의 round가 아니다.
- 닫힌 `facts -> decisions -> compose -> normalizer -> style linter -> rendered -> Lua bridge -> runtime` 경로 안에서 source evidence를 채워 `identity_fallback`을 줄이는 round다.

이후 reviewer feedback을 반영해 plan 문서를 더 단단하게 수정했다.

- `special_context`는 authoritative lane이 아니라 planning memo로만 남겼다.
- Phase 2/4/6 gate에 B-path accounting, `requeue_tolerability`, `lane_stability` 확인을 명시했다.
- regression gate의 보호 대상을 round-opening `1467` 고정치가 아니라 누적 exposed surface 전체로 명시했다.
- 신규 facts 작성이 current lexical authority 기준을 따라야 한다는 조건을 plan에 추가했다.

실행 manifest는 다음 스크립트로 생성했다.

- `Iris/build/description/v2/tools/build/build_identity_fallback_source_expansion_phase0_1.py`

핵심 산출물:

- `Iris/build/description/v2/staging/identity_fallback_source_expansion/phase0_scope_lock/round_opening_baseline_snapshot.json`
- `Iris/build/description/v2/staging/identity_fallback_source_expansion/phase1_execution_manifest/bucket_1_cluster_reuse_mapping.json`
- `Iris/build/description/v2/staging/identity_fallback_source_expansion/phase1_execution_manifest/bucket_2_domain_inventory.json`
- `Iris/build/description/v2/staging/identity_fallback_source_expansion/phase1_execution_manifest/bucket_2_source_triage.json`
- `Iris/build/description/v2/staging/identity_fallback_source_expansion/phase1_execution_manifest/bucket_2_lane_summary.json`
- `Iris/build/description/v2/staging/identity_fallback_source_expansion/phase1_execution_manifest/bucket_2_cluster_design_plan.json`
- `Iris/build/description/v2/staging/identity_fallback_source_expansion/phase1_execution_manifest/bucket_2_batch_schedule.json`

여기서 고정된 실행 분해는 다음과 같다.

- `bucket_1`: `reuse_fast_lane_candidate 2 / needs_source_verification 5 / reassign_to_bucket_2 4`
- `bucket_2`: `targeted 589 / partial 10`
- execution label: `mapping-patch 593 / new-cluster-only 6`
- initial batch schedule: `254 / 194 / 121 / 20 / 10`

즉, `617`을 한 번에 처리하려 하지 않고, 먼저 deterministic batch 단위로 쪼개는 데 성공했다.

## 6. Phase 2~4: Targeted Lane 대형 subset 구현

가장 큰 감축은 targeted lane에서 나왔다.

구현 스크립트:

- `build_identity_fallback_batch1_clothing_surface_reuse.py`
- `build_identity_fallback_batch2_accessory_headgear_reuse.py`
- `build_identity_fallback_batch3_food_storage_reference_reuse.py`
- `build_identity_fallback_batch4_medical_kitchen_explosive_reuse.py`
- 각 batch의 `*_authority_promotion.py`

이 네 배치에서 실제로 승격된 수는 다음과 같다.

- `batch_1_clothing_surface_reuse`: `254`
- `batch_2_accessory_headgear_reuse`: `194`
- `batch_3_food_storage_reference_reuse`: `121`
- `batch_4_medical_kitchen_explosive_reuse`: `20`

이 단계의 cumulative promote count는 `589`였다.

핵심 의미는 단순하다.

- 기존 source 조합을 새 facts/decisions overlay로 다시 읽는 `mapping-patch` 계열은 대량 실행이 가능했다.
- 각 batch는 `introduced hard fail = 0`, `introduced warn = 0`, `changed exposed rendered = 0` 조건 아래 preview와 staged authority까지 닫혔다.
- B-path accounting상 `identity_fallback` lane은 silent loss나 row 삭제 없이 source promotion으로만 감소했다.

즉, 이번 round의 대형 감축은 새 compose path를 만드는 것이 아니라 기존 source와 cluster를 정확히 재배치하는 것으로 달성됐다.

## 7. Phase 4~5: Partial Lane, Bucket 1, Residual Taxonomy

partial lane의 첫 실행 대상은 `electronics_device_variants`였다.

구현 스크립트:

- `build_identity_fallback_batch5a_electronics_partial_reuse.py`
- `build_identity_fallback_batch5a_authority_promotion.py`

여기서 `DigitalWatch2 / Receiver / TimerCrafted / TriggerCrafted` `4`건이 실제 promotion으로 닫혔다. cumulative promote count는 `593`이 됐다.

반면 같은 `batch_5_partial_domain_split` 안의 나머지 `6`건은 즉시 promote하지 않고 Phase 3 taxonomy로 넘겼다.

해당 산출물:

- `Iris/build/description/v2/staging/identity_fallback_source_expansion/batches/batch_5_partial_domain_split/batch_5_cluster_definitions.json`
- `.../batch_5_smoke_samples.json`
- `.../batch_5_residual_readiness_report.json`

`bucket_1`에서는 fast-lane이 실제로 열렸다.

구현 스크립트:

- `build_identity_fallback_bucket1_wrench_reuse.py`
- `build_identity_fallback_bucket1_wrench_authority_promotion.py`
- `build_identity_fallback_bucket1_crowbar_reuse.py`
- `build_identity_fallback_bucket1_crowbar_authority_promotion.py`

실제 승격 수:

- `Wrench / PipeWrench`: `2`
- `Crowbar`: `1`

이 시점 cumulative promote count는 `596`이 됐다.

동시에 residual taxonomy도 더 정교하게 재구성했다.

구현 스크립트:

- `build_identity_fallback_bucket1_residual_taxonomy.py`
- `build_identity_fallback_batch6_residual_family_split_taxonomy.py`
- `build_identity_fallback_phase3_residual_taxonomy_manifest.py`

이 단계에서 남은 bucket은 planning artifact가 아니라 `phase3 pending inventory`로 다시 읽히게 됐다. 이후 배치 `7~9`가 이 inventory에서 일부를 실행하고 나면, manifest는 최종적으로 `10`개 pending set과 정확히 정렬된다.

## 8. Batch 7~9: Net-New Cluster를 cap 안에서 실행 가능한 subset으로 전환

세션 후반에는 residual 일부를 실제 executable subset으로 더 내렸다.

새 cluster와 배치는 다음과 같다.

- `adhesive_repair_supply`
  - 스크립트: `build_identity_fallback_batch7_adhesive_repair_supply.py`, `build_identity_fallback_batch7_authority_promotion.py`
  - 대상: `Base.Glue`, `Base.Woodglue`
  - 승격 수: `2`
- `solid_fuel_material`
  - 스크립트: `build_identity_fallback_batch8_solid_fuel_material.py`, `build_identity_fallback_batch8_authority_promotion.py`
  - 대상: `Base.Charcoal`
  - 승격 수: `1`
- `metalworking_consumable_supply`
  - 스크립트: `build_identity_fallback_batch9_metalworking_consumable_supply.py`, `build_identity_fallback_batch9_authority_promotion.py`
  - 대상: `Base.WeldingRods`
  - 승격 수: `1`

이 세 배치를 더하면서 cumulative promote count는 `600`이 됐다.

중요한 부수 작업도 있었다.

- `interaction_clusters.json`과 `cluster_summary_templates.json`에 위 3개 cluster seed를 추가했다.
- `validate_interaction_cluster_seed.py`를 반복 실행해 cluster/template count를 검증했다.
- batch 9 시점에서 seed budget이 정확히 `30 / 30`에 도달했다.
- cumulative phase6 wrapper는 Windows 경로 길이 문제를 피하기 위해 output dir를 `exec_subset_600_wrench_crowbar_b7_b8_b9`로 줄였다.

즉, residual 일부는 새 cluster가 필요했지만, 그것도 현재 cycle의 frozen budget 안에서만 허용되는 범위까지 실행했다.

## 9. Phase 6: Executable Subset Closeout

current cycle의 canonical closeout read point는 Phase 6 cumulative subset rollout이다.

핵심 스크립트:

- `Iris/build/description/v2/tools/build/build_identity_fallback_phase6_executable_subset_rollout.py`
- `Iris/build/description/v2/tools/build/build_identity_fallback_phase6_subset_plus_bucket1_wrench.py`
- `Iris/build/description/v2/tools/build/build_identity_fallback_phase6_subset_plus_bucket1_wrench_crowbar.py`
- `Iris/build/description/v2/tools/build/build_identity_fallback_phase6_subset_plus_bucket1_wrench_crowbar_batch7_adhesive.py`
- `Iris/build/description/v2/tools/build/build_identity_fallback_phase6_subset_plus_bucket1_wrench_crowbar_batch7_adhesive_batch8_charcoal.py`
- `Iris/build/description/v2/tools/build/build_identity_fallback_phase6_subset_plus_bucket1_wrench_crowbar_batch7_adhesive_batch8_charcoal_batch9_welding.py`

current authoritative artifact:

- `Iris/build/description/v2/staging/identity_fallback_source_expansion/phase6_subset_rollout/exec_subset_600_wrench_crowbar_b7_b8_b9/subset_rollout_report.json`
- `Iris/build/description/v2/staging/identity_fallback_source_expansion/phase6_subset_rollout/exec_subset_600_wrench_crowbar_b7_b8_b9/subset_distribution_remeasurement.json`
- `Iris/build/description/v2/staging/identity_fallback_source_expansion/phase6_subset_rollout/exec_subset_600_wrench_crowbar_b7_b8_b9/subset_remaining_identity_fallback_rows.jsonl`

이 snapshot에서 고정된 숫자는 다음과 같다.

- promoted executable subset: `600`
- remaining identity_fallback: `17`
- runtime path counts: `cluster_summary 2040 / identity_fallback 17 / role_fallback 48`
- publish split: `internal_only 617 / exposed 1467`
- lane delta: `identity_fallback -600 / cluster_summary +600`
- residual split: `phase3_taxonomy_pending 10 / bucket_3_scope_hold 7`

gate 상태도 명확하다.

- `delta_gate_pass = true`
- `preview_validation_status = pass`
- `runtime_report_status = ready_for_in_game_validation`
- `requeue_tolerability_status = true`
- `lane_stability_status = true`

반대로 아직 닫지 않은 것도 분명하다.

- `reflection_applied = false`
- `current_authority_matches_subset_staged = false`
- `workspace_deployed_matches_subset_staged = false`

즉, current cycle은 staged authority subset closeout까지는 닫혔지만, workspace Lua overwrite와 deployed reflection은 아직 별도 실행 단계다.

## 10. Phase 3 Residual Manifest 재정렬

current closeout의 residual inventory는 아래 artifact로 읽는다.

- `Iris/build/description/v2/staging/identity_fallback_source_expansion/phase3_taxonomy_manifest/phase3_residual_taxonomy_manifest.json`
- `Iris/build/description/v2/staging/identity_fallback_source_expansion/phase3_taxonomy_manifest/phase3_residual_taxonomy_alignment_report.json`

최종 pending `10`개는 다음과 같다.

- `Base.ClubHammer`
- `Base.HandScythe`
- `Base.Katana`
- `Base.LeadPipe`
- `Base.Nightstick`
- `Base.Rope`
- `Base.Sledgehammer`
- `Base.Sledgehammer2`
- `Base.WoodenMallet`
- `farming.WateredCan`

alignment report는 이 집합이 phase6 remeasurement의 pending set과 정확히 일치함을 확인한다.

- `phase3_pending_count_matches_manifest = true`
- `phase3_pending_id_set_matches_manifest = true`

즉, current residual은 흐릿한 “아직 남은 것들”이 아니라 다음 round input으로 바로 쓸 수 있는 정확한 manifest다.

## 11. 왜 여기서 current cycle을 닫았는가

세션 마지막 판단은 기술 구현이 아니라 governance boundary에 관한 것이었다.

`validate_interaction_cluster_seed.py`와 interaction-cluster plan 기준으로 current seed budget은 `30 / 30`에 도달했다. 이 상태에서 `31번째` cluster를 열면, 그것은 source expansion round의 연장이 아니라 `A-4-1` granularity와 budget 자체를 다시 여는 별도 설계 행위가 된다.

그래서 current cycle에서는 다음을 결정했다.

- `cluster_count_limit = 30`은 frozen invariant로 유지한다.
- current source expansion cycle은 `600 promoted / residual 17` 상태에서 닫는다.
- 남은 `17`은 same-session unfinished queue가 아니라 후속 round input으로만 읽는다.

이 판단은 상위 문서에도 반영됐다.

- `docs/DECISIONS.md`
  - `2026-04-15 — Iris DVF 3-3 identity_fallback source expansion current cycle은 600 promote / residual 17 상태에서 닫는다`
  - `2026-04-15 — current source expansion cycle에서는 A-4-1 interaction cluster budget 30을 재개방하지 않는다`
- `docs/ROADMAP.md`
  - `# 11. 2026-04-15 Addendum — Iris DVF 3-3 identity_fallback source expansion round closeout at current cluster budget`
- `docs/ARCHITECTURE.md`
  - `## 11-44. Iris DVF 3-3 identity_fallback source expansion current closeout is bounded by the frozen A-4-1 cluster budget`

즉, current authority path는 `same-session continuation`이 아니라 `current cycle closeout + next residual round handoff`다.

## 12. 이번 세션에서 하지 않은 것

범위를 넘지 않기 위해 일부 작업은 의도적으로 열지 않았다.

- workspace Lua overwrite
- staged subset의 deployed runtime reflection apply
- in-game validation
- `internal_only -> exposed` publish promotion
- `bucket_3_scope_hold 7` 실행
- `31번째` net-new cluster 추가
- `A-4-1 interaction cluster budget` 재개방

따라서 current cycle의 성공 기준은 “617 전부를 same-session에 끝냈다”가 아니라, frozen budget 안에서 executable subset을 deterministic하게 밀고 residual inventory를 정확히 다시 쟀다는 점이다.

## 13. 다음 세션을 위한 handoff

다음 세션에서 읽어야 할 current authoritative start point는 아래 다섯 개다.

- `docs/DECISIONS.md`
- `docs/ROADMAP.md`
- `docs/ARCHITECTURE.md`
- `Iris/build/description/v2/staging/identity_fallback_source_expansion/phase6_subset_rollout/exec_subset_600_wrench_crowbar_b7_b8_b9/subset_distribution_remeasurement.json`
- `Iris/build/description/v2/staging/identity_fallback_source_expansion/phase3_taxonomy_manifest/phase3_residual_taxonomy_manifest.json`

그리고 next work는 둘 중 하나로만 읽는다.

1. frozen-budget residual round
2. separate `A-4-1 rework / cluster budget` round

current decision은 첫 번째 branch를 기본으로 둔다. 즉, 다음 세션에서는 `600 / 17` baseline 위에서 residual 전용 scope lock과 execution plan을 새로 열어야 한다.
