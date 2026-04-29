# Iris DVF 3-3 Role Fallback Hollow Follow-up Walkthrough

_Last updated: 2026-04-11_

## 1. 목적

이 문서는 `role_fallback hollow follow-up` lane가 이번 세션에서 실제로 어떻게 실행되고 닫혔는지 한 번에 따라가기 위한 walkthrough다.

초점은 여섯 가지다.

- 왜 이 lane를 더 이상 열린 source-expansion queue로 읽지 않는가
- `37` follow-up baseline이 어떤 단계로 분해되고 소비됐는가
- `C1-F / C1-G` residual source-expansion lane가 어떻게 실제 promotion과 replacement로 닫혔는가
- 왜 `Base.PaintbucketEmpty`, `Base.PlasterPowder`는 source-expansion이 아니라 policy closeout으로 닫혔는가
- 왜 `camping.SteelAndFlint`, `Base.ConcretePowder`, `Base.Yarn`는 미완료가 아니라 `carry_forward_hold`인가
- 왜 최종 canonical current-state는 planning artifact가 아니라 `terminal_status / terminal_handoff`인가

상위 기준은 다음 문서들이다.

- `docs/Philosophy.md`
- `docs/DECISIONS.md`
- `docs/ARCHITECTURE.md`
- `docs/ROADMAP.md`
- `docs/iris-dvf-3-3-compose-contract-migration-execution-plan.md`

## 2. 시작점과 끝점

이번 세션은 `role_fallback hollow`가 이미 follow-up split까지는 끝난 상태에서 시작했다.

시작 baseline:

- follow-up split: `37`
- split: `existing_cluster_reuse 20 / policy_revisit 2 / net_new_source_expansion 15`
- deterministic reusable cluster: `C1-B.container_storage 20`
- net-new residual axis split: `C1-F tool_use_recovery 6 / C1-G material_context_recovery 9`

이번 세션의 종료점은 다음과 같다.

- `C1-F / C1-G` source promotion 완료
- replacement-aware runtime handoff 완료
- policy review `2` closeout 완료
- residual tail `3` local discovery execution 완료
- residual tail round closeout 완료
- `residual_after_c1b_reuse 17` terminal status 완료
- full `37` follow-up lane terminal handoff 완료

최종 snapshot:

- full follow-up accounting: `37 = reuse preview 20 + promoted 12 + policy closed 2 + carry-forward hold 3`
- current evidence round active unresolved: `0`
- runtime rows: `2105`
- runtime paths: `cluster_summary 1275 / direct_use 12 / identity_fallback 718 / role_fallback 100`

즉, 이번 세션은 planning split를 더 자세히 적은 세션이 아니라, **role_fallback hollow follow-up lane를 current evidence round 기준으로 terminalized한 세션**이었다.

## 3. 가장 중요한 결론

이번 세션의 핵심 결론은 여섯 줄로 요약된다.

- `followup_split`, `followup_execution_inputs`, `followup_runbook`은 planning baseline으로 남는다.
- current-state는 `role_fallback_hollow_terminal_status.json`과 `role_fallback_hollow_terminal_handoff.json`으로 읽는다.
- `C1-B` reuse `20`은 preview-backed closure로 accounting된다.
- residual `17`은 `block_c_source_promoted 12 / policy_review_closed_maintain_exclusion 2 / carry_forward_hold 3`으로 닫혔다.
- `carry_forward_hold 3`은 active execution debt가 아니라 future hold다.
- 따라서 이 lane를 다시 열려면 closed lane 연장이 아니라 새 라운드가 필요하다.

## 4. 전체 흐름

실행 흐름은 크게 8단계였다.

1. follow-up split baseline `37`를 현재 작업 입력으로 다시 해석한다.
2. `C1-B` reuse `20`을 dry-run preview로 고정하고, residual `17`로 debt를 다시 계산한다.
3. residual `17`을 `policy 2 / net-new 15`로 분리하고, net-new를 `C1-F 6 / C1-G 9`로 다시 쪼갠다.
4. `C1-F / C1-G`에 대해 seed package, authoring queue, targeted/manual split, authority candidate, promotion manifest를 만든다.
5. reviewed replacement candidate `12`를 실제 package `source.raw`에 반영하고 runtime replacement lane으로 연결한다.
6. policy review `2`는 `maintain_exclusion` default branch로 closeout한다.
7. parked tail `3`는 local discovery execution을 끝까지 수행하고, reopen 실패를 artifact로 고정한다.
8. 마지막으로 `terminal_status`와 `terminal_handoff`를 만들어 current evidence round를 닫는다.

아래부터는 이 순서를 그대로 따라간다.

## 5. Phase 1: Follow-up Split를 실행 가능한 baseline으로 재고정

이 lane의 실제 출발점은 `role_fallback_hollow_followup_split.json`이었다.

핵심 artifact:

- `Iris/build/description/v2/staging/compose_contract_migration/full_runtime/role_fallback_hollow_followup_split.json`
- `Iris/build/description/v2/staging/compose_contract_migration/full_runtime/role_fallback_hollow_followup_execution_inputs.summary.json`
- `Iris/build/description/v2/staging/compose_contract_migration/full_runtime/role_fallback_hollow_followup_runbook.json`

이 단계에서 고정된 숫자는 다음과 같다.

- total follow-up rows: `37`
- reuse candidate: `20`
- policy revisit: `2`
- net-new source expansion: `15`

중요한 점은 이 숫자들이 current-state가 아니라 **planning baseline** 이라는 것이다.

이 baseline은 이후 단계에서 실제로 이렇게 갈린다.

- `reuse 20`은 `C1-B.container_storage` preview-backed closure로 간다.
- `policy 2`는 별도 review lane로 간다.
- `net-new 15`는 `C1-F / C1-G` execution lane로 간다.

## 6. Phase 2: Reuse 20 소비 후 Residual 17 재구성

reuse lane를 먼저 소비한 뒤, residual debt를 다시 계산했다.

핵심 artifact:

- `Iris/build/description/v2/staging/compose_contract_migration/full_runtime/role_fallback_hollow_c1b_reuse_promotion_preview/role_fallback_hollow_c1b_reuse_promotion_preview.summary.json`
- `Iris/build/description/v2/staging/compose_contract_migration/full_runtime/role_fallback_hollow_residual_after_c1b_reuse.json`
- `Iris/build/description/v2/staging/compose_contract_migration/full_runtime/role_fallback_hollow_net_new_work_packages.json`

여기서 닫힌 숫자는 다음과 같다.

- reuse preview: `20`
- projected recovery: `20/20 strong`, `20/20 exposed`
- residual after reuse: `17`
- residual split: `policy 2 / net-new 15`
- net-new work packages: `C1-F 6 / C1-G 9`

이 수치의 의미는 단순하다.

- container_body hollow rows는 새 source-expansion 없이도 existing cluster reuse로 회복 가능했다.
- 나머지 debt는 policy와 net-new source work로만 남았다.
- 따라서 이후 핵심 execution은 `C1-F / C1-G`와 policy `2`를 닫는 것이었다.

## 7. Phase 3: C1-F / C1-G Source Package Execution

이 세션에서 가장 긴 실행 구간은 `C1-F / C1-G`였다.

핵심 artifact 흐름:

- `role_fallback_hollow_seed_package_index.json`
- `role_fallback_hollow_source_authoring_queue.json`
- `role_fallback_hollow_targeted_authoring_pack.json`
- `role_fallback_hollow_manual_second_pass_upgrades.json`
- `role_fallback_hollow_targeted_source_authority_candidates_index.json`
- `role_fallback_hollow_source_promotion_manifest.json`
- `role_fallback_hollow_source_promotion_applied.json`

중간에 닫힌 숫자는 다음과 같다.

- targeted/manual split: `targeted 12 / manual 3`
- second-pass upgrade: `5`
- remaining manual: `3`
- promotion-ready authority candidate: `12`
- parked carry-forward: `3`
- actual package apply: `C1-F 5 / C1-G 7`

이 단계의 핵심은 `source.raw`를 실제로 교체했다는 점이다.

즉, 이 lane는 candidate draft 수준에서 멈추지 않고 다음 단계까지 갔다.

- exact replacement candidate 생성
- delta review 생성
- promotion manifest 생성
- package seed `source.raw` apply
- post-apply parity verification

결과적으로 `12`건은 실제 replacement lane으로 runtime handoff까지 연결됐다.

## 8. Phase 4: Runtime Replacement와 Post-Apply Preview

promotion은 package-level source 교체로 끝나지 않았다. replacement-aware runtime path까지 연결했다.

핵심 artifact:

- `Iris/build/description/v2/staging/source_coverage/block_c/role_fallback_hollow_post_apply_preview_index.json`
- `Iris/build/description/v2/staging/source_coverage/post_c/post_c_projection_summary.json`
- `Iris/build/description/v2/staging/interaction_cluster/source_coverage_runtime/source_coverage_runtime_summary.json`

여기서 닫힌 숫자는 다음과 같다.

- ready replacement rows: `12`
- parked rows: `3`
- direct_use preserved: `12/12`
- special_context preserved: `11/11`
- unexpected legacy hard fail: `0`
- integrated runtime rows: `2105`
- integrated runtime paths: `cluster_summary 1275 / direct_use 12 / identity_fallback 718 / role_fallback 100`

핵심 해석은 이렇다.

- `C1-F / C1-G`는 additive package가 아니라 replacement lane로 반영됐다.
- row count를 늘리지 않고 `role_fallback -12 / direct_use +12`가 반영됐다.
- downstream runtime 관점에서 이 lane의 실질 성과는 `direct_use 12` 확보였다.

## 9. Phase 5: Policy Review 2 Closeout

`Base.PaintbucketEmpty`, `Base.PlasterPowder`는 source-expansion lane으로 보내지 않고 policy lane에서 닫았다.

핵심 artifact:

- `role_fallback_hollow_policy_resolution_packet.json`
- `role_fallback_hollow_policy_outcome_projection.json`
- `role_fallback_hollow_policy_default_closeout.json`
- `role_fallback_hollow_post_policy_default_closeout_status.json`

여기서 닫힌 숫자는 다음과 같다.

- policy review rows: `2`
- default resolution: `maintain_exclusion 2`
- projected reopen if override: `2`
- current closeout: `policy_review_closed_maintain_exclusion 2`
- runtime delta: `0`

즉, policy lane는 reopen input이 아니라 review bookkeeping closeout으로 끝났다.

이 결정 덕분에 residual tail는 source-expansion 잔여 `3`으로만 압축됐다.

## 10. Phase 6: Residual Tail 3 Local Discovery Execution

마지막 열린 실행은 `camping.SteelAndFlint`, `Base.ConcretePowder`, `Base.Yarn` 세 row였다.

핵심 artifact:

- `role_fallback_hollow_residual_tail_handoff.json`
- `role_fallback_hollow_residual_tail_source_discovery_round.json`
- `c1-f/c1-f_residual_tail_discovery_pass.json`
- `c1-g/c1-g_residual_tail_discovery_pass.json`
- `role_fallback_hollow_residual_tail_source_discovery_status.json`

실행 결과:

- executed rows: `3`
- reopen_ready: `0`
- remain_parked: `3`
- pending_execution: `0`

row별 해석:

- `camping.SteelAndFlint`
  - generic `StartFire` 문맥과 translation token은 있었지만 direct non-translation requirement는 없었다.
- `Base.ConcretePowder`
  - declaration, spawn, related concrete object는 있었지만 direct build/action requirement는 없었다.
- `Base.Yarn`
  - declaration, spawn, sewing/garment 주변 문맥은 있었지만 direct requirement는 `Thread` 쪽이었고 `Yarn` 자체는 아니었다.

중요한 점은 이 `3`건이 단순히 “못 찾음”으로 남은 것이 아니라, **local discovery execution이 실제로 완료된 뒤에도 reopen gate를 통과하지 못했다는 사실이 artifact로 잠겼다**는 것이다.

## 11. Phase 7: Round Closeout와 Terminal Status

tail 실행이 끝난 뒤, 이 lane를 closeout artifact로 봉인했다.

핵심 artifact:

- `role_fallback_hollow_residual_tail_round_closeout.json`
- `role_fallback_hollow_terminal_status.json`

이 단계에서 고정된 숫자는 다음과 같다.

- tail round complete: `true`
- carry-forward hold: `3`
- next lane: `future_new_source_discovery_hold`
- residual `17` terminal aggregate:
  - `block_c_source_promoted 12`
  - `policy_review_closed_maintain_exclusion 2`
  - `carry_forward_hold 3`
  - `active_unresolved_count 0`

즉, `residual_after_c1b_reuse 17` 기준으로는 더 이상 열린 실행 debt가 없다.

남은 `3`건은 미완료 queue가 아니라 hold inventory다.

## 12. Phase 8: Full 37 Terminal Handoff

마지막으로 `37` follow-up baseline 전체를 다시 current-state accounting으로 닫았다.

핵심 artifact:

- `Iris/build/description/v2/staging/compose_contract_migration/full_runtime/role_fallback_hollow_terminal_handoff.json`

최종 accounting:

- `existing_cluster_reuse_preview_backed 20`
- `block_c_source_promoted 12`
- `policy_review_closed_maintain_exclusion 2`
- `carry_forward_hold 3`
- total `37`

이 artifact의 의미는 명확하다.

- planning baseline `37`과 current-state terminal aggregate를 한 장에서 연결한다.
- reuse `20`은 preview-backed closure로 계산한다.
- residual `17`은 terminalized current-state로 계산한다.
- current evidence round의 active execution lane는 `0`이다.

이 단계가 닫히면서, 이 lane는 더 이상 “계속 이어서 할 실행”이 아니라 **종료된 current round**가 됐다.

## 13. 왜 이 lane를 완료로 읽는가

이번 세션 종료 기준으로 `role_fallback hollow` lane를 완료로 읽는 이유는 세 가지다.

1. current-state aggregate가 artifact 기준으로 완결됐다.
   - `terminal_status`
   - `terminal_handoff`

2. residual tail도 실행이 끝난 뒤 hold로 봉인됐다.
   - `executed 3`
   - `reopen_ready 0`
   - `carry_forward_hold 3`

3. downstream runtime snapshot도 이미 current integrated baseline으로 닫혔다.
   - runtime rows `2105`
   - direct_use `12`
   - runtime status `ready_for_in_game_validation`

즉, 남은 일이 없는 것이 아니라, **이 lane 안에서 더 할 실행이 없다**는 뜻이다.

## 14. 지금 남은 일

이 walkthrough 시점에서 남은 것은 세 가지뿐이다.

- `future_new_source_discovery_hold`
  - `camping.SteelAndFlint`
  - `Base.ConcretePowder`
  - `Base.Yarn`
- downstream runtime / in-game validation lane
- 별도 새 라운드로 열리는 future source-expansion 또는 remeasurement lane

중요한 점은, 이 셋이 현재 lane의 미완료가 아니라 **다음 라운드 후보**라는 것이다.

따라서 이후 작업은 `role_fallback hollow follow-up`의 계속이 아니라, 새 로드맵을 가진 새 round로만 열어야 한다.

## 15. 최종 요약

이번 세션은 `role_fallback hollow follow-up`을 다음 상태로 닫았다.

- full baseline: `37`
- reuse preview-backed: `20`
- block_c promoted: `12`
- policy closed: `2`
- carry-forward hold: `3`
- active unresolved: `0`

그리고 이 상태를 planning artifact와 current-state artifact로 분리해 기록했다.

- planning baseline:
  - `followup_split`
  - `followup_execution_inputs`
  - `followup_runbook`
- current-state terminal:
  - `terminal_status`
  - `terminal_handoff`

이 분리가 이번 세션의 가장 중요한 산출물이다. 이후 작업은 이 closed lane 위에 덧붙이는 것이 아니라, 이 terminal handoff를 시작점으로 새 round를 여는 방식으로만 진행해야 한다.
