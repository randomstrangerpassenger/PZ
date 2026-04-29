# Iris DVF 3-3 Surface Contract Authority Migration Walkthrough

_Last updated: 2026-04-08_

## 1. 목적

이 문서는 [docs/iris-dvf-3-3-surface-contract-authority-migration-execution-plan.md](./iris-dvf-3-3-surface-contract-authority-migration-execution-plan.md)가 이번 세션에서 실제로 어떻게 구현되고 닫혔는지 한 번에 따라가기 위한 walkthrough다.

초점은 여섯 가지다.

- 왜 이번 round를 style 강화가 아니라 `surface contract authority migration`으로 읽어야 하는가
- advisory style lint와 structural contract signal이 어떤 artifact 경계로 분리됐는가
- 왜 `quality/publish decision stage`만 single writer로 유지한 채 structural gate를 추가할 수 있었는가
- 왜 이번 round는 publish split을 바꾸지 않고 authority만 명문화하는 방식으로 닫혔는가
- dry-run delta, baseline v4, bridge/runtime, in-game validation이 어떤 수치로 실제 닫혔는가
- 왜 `identity_fallback` source expansion은 이번 round 미완료가 아니라 후속 round handoff로 분리되는가

상위 기준은 다음 문서들이다.

- `docs/Philosophy.md`
- `docs/DECISIONS.md`
- `docs/ARCHITECTURE.md`
- `docs/ROADMAP.md`
- `docs/iris-dvf-3-3-three-axis-contract-migration-walkthrough.md`
- `docs/iris-dvf-3-3-surface-contract-authority-migration-execution-plan.md`

## 2. 시작점과 종료점

이번 세션은 three-axis contract migration round가 이미 닫힌 상태에서 시작했다.

시작 baseline은 다음처럼 고정돼 있었다.

- runtime contract는 이미 `runtime_state / quality_state / publish_state` 3축으로 닫혀 있었다.
- `publish_state = internal_only`는 이미 Browser/Wiki default surface suppression contract로 쓰이고 있었다.
- `identity_fallback 617`은 이미 `internal_only` lane으로 격리돼 있었고, row deletion이나 silent loss가 아니었다.
- style linter는 여전히 advisory-only였다.
- 하지만 role violation 계열 signal은 아직 decision stage의 authoritative input으로 들어가지 못하고 있었다.

이번 round의 종료점은 다음과 같다.

- `surface_contract_signal.jsonl` 분리 완료
- structural audit 구현 완료
- `quality/publish decision stage`가 structural signal을 읽는 single writer 구조 구현 완료
- `quality_baseline_v4.json` 동결 완료
- `2026-04-08` fresh manual in-game validation pass 기록 완료
- current closeout status: `rollout_pass_manual_validation_complete`

즉, 이번 round는 새 quality model을 만든 round가 아니라, **기존 3축 모델 위에서 default surface exposure authority를 single-writer decision stage 안으로 이관한 round**였다.

## 3. 가장 중요한 결론

이번 세션의 핵심 결론은 다섯 줄로 요약된다.

- style linter는 끝까지 advisory-only로 남았다.
- structural audit는 새 writer가 아니라 non-writer sensor로 추가됐다.
- `quality_state`와 `publish_state`는 여전히 `quality/publish decision stage` 하나만 기록한다.
- current cycle의 publish split은 `internal_only 617 / exposed 1467`로 그대로 유지됐다.
- 이번 round는 fresh manual rerun까지 포함해 closeout됐고, 남은 일은 source expansion과 future separate decision이다.

## 4. 전체 흐름

실행 흐름은 크게 8단계였다.

1. 이번 round를 style 강화가 아니라 authority migration round로 문서에서 먼저 봉인한다.
2. style/advisory와 layer-boundary violation을 재분류하고 ownership 경계를 문서로 고정한다.
3. structural audit를 별도 artifact로 분리한다.
4. decision stage preview가 그 signal을 input-only recommendation으로 읽도록 연결한다.
5. dry-run delta와 baseline v4를 만들고 publish split 안정성을 확인한다.
6. bridge/runtime validation pack을 다시 current v4 기준으로 정리한다.
7. `2026-04-08` fresh manual in-game rerun을 통과시킨다.
8. 이후 round를 다시 열지 않고, `identity_fallback` source expansion handoff artifact를 별도로 만든다.

아래부터는 이 순서를 그대로 따라간다.

## 5. Phase 0과 Phase 1: 라운드 성격과 권한 경계 재봉인

가장 먼저 닫은 것은 구현이 아니라 문서 해석이었다.

핵심 갱신 문서:

- `docs/DECISIONS.md`
- `docs/ROADMAP.md`
- `docs/ARCHITECTURE.md`
- `docs/quality_state_ownership_spec.md`
- `docs/publish_state_spec.md`
- `docs/layer3_structural_audit_spec.md`
- `docs/publish_state_mapping_table.md`
- `docs/false_positive_threshold_definition.md`
- `docs/pipeline_execution_order_check.md`
- `docs/surface_contract_rollout_order.md`

이 단계에서 고정한 문장은 세 가지였다.

- 이번 round는 style normalization 재개가 아니다.
- 이번 round는 compose 외부 repair 복귀가 아니다.
- 이번 round는 닫힌 runtime/bridge 계약 위에서 surface exposure authority를 single writer 안으로 명문화하는 작업이다.

동시에 role violation 계열은 style 문제가 아니라 `layer boundary contract violation`으로 재분류했다.

이 재분류의 결과는 다음 표로 닫혔다.

- `hard_block_candidate`
  - `LAYER4_ABSORPTION`
- `publish_isolation_candidate`
  - `IDENTITY_ONLY`
  - `BODY_LACKS_ITEM_SPECIFIC_USE`
  - unresolved `FUNCTION_NARROW`
  - unresolved `ACQ_DOMINANT`
- `advisory_only`
  - 반복 명사, 상투 표현, discovery residue 등 style advisory 계열

중요한 점은 이 단계가 새 권한을 validator나 linter로 넘긴 것이 아니라, **무엇이 decision stage input이 될 수 있는 structural signal인가를 문서로 먼저 닫은 단계**였다는 점이다.

## 6. Phase 2: structural audit를 별도 input artifact로 분리

이 round의 첫 핵심 구현은 advisory lint와 structural signal을 artifact 경계에서 분리하는 것이었다.

핵심 코드:

- `Iris/build/description/v2/tools/build/layer3_structural_audit.py`

핵심 산출물:

- `Iris/build/description/v2/staging/semantic_quality/phaseE_contract_migration/surface_contract_signal.jsonl`
- `Iris/build/description/v2/staging/semantic_quality/phaseE_contract_migration/surface_contract_signal_summary.json`
- `Iris/build/description/v2/staging/semantic_quality/phaseE_contract_migration/structural_audit_scope_inventory.json`

여기서 중요한 구현 결정은 다음과 같았다.

- structural audit는 `compose 이후 / rendered 생성 이전`의 pre-render contract candidate를 읽는다.
- output field는 `item_id / structural_verdict / violation_type / recommended_tier / evidence`로 고정한다.
- `recommended_tier`는 direct write instruction이 아니라 recommendation이다.
- structural audit는 `quality_state`나 `publish_state`를 직접 기록하지 않는다.

실데이터 기준 summary는 다음처럼 닫혔다.

- total rows: `2105`
- structural verdict counts: `clean 1481 / flag 624`
- violation type counts: `BODY_LACKS_ITEM_SPECIFIC_USE 617 / FUNCTION_NARROW 7 / none 1481`
- recommended tier counts: `advisory_only 1481 / publish_isolation_candidate 624`

이 수치의 의미는 명확하다.

- current publish surface를 새로 흔들만한 net-new violation은 없었다.
- current structural problem의 대부분은 기존 `identity_fallback` lane 위에서 다시 읽힌 `BODY_LACKS_ITEM_SPECIFIC_USE 617`이었다.
- residual `FUNCTION_NARROW 7`은 current cycle에서 auto-isolation이 아니라 preview/report flag로만 남는다.

## 7. Phase 3과 Phase 4: decision stage single writer 유지 상태로 structural gate 연결

structural audit를 분리한 뒤, 실제 authoritative write는 기존 decision stage 하나만 하도록 유지했다.

핵심 코드:

- `Iris/build/description/v2/tools/build/report_quality_publish_decision_preview.py`
- `Iris/build/description/v2/tools/build/validate_quality_publish_decision_preview.py`
- `Iris/build/description/v2/tools/build/build_quality_publish_phase5_runtime.py`

여기서 고정한 contract는 다음과 같다.

- `hard_fail + hard_block_candidate`
  - decision stage가 `quality_state = weak`와 `publish_state = internal_only`를 같이 적용
- `publish_isolation_candidate`
  - current rollout 1 open lane인 `IDENTITY_ONLY`와 explicit `BODY_LACKS_ITEM_SPECIFIC_USE`만 isolation 후보로 소비
- `FUNCTION_NARROW`, `ACQ_DOMINANT`
  - current hold lane 유지
- `structural_flag`
  - preview/report-only meta
  - emitted contract artifact, Lua bridge, runtime consumer에는 포함 금지

preview artifact는 다음 경로에 생성된다.

- `Iris/build/description/v2/staging/semantic_quality/phaseE_contract_migration/quality_publish_decision_preview.jsonl`
- `Iris/build/description/v2/staging/semantic_quality/phaseE_contract_migration/quality_publish_decision_preview_summary.json`
- `Iris/build/description/v2/staging/semantic_quality/phaseE_contract_migration/quality_publish_decision_preview_validation_report.json`

current preview/baseline snapshot 기준 핵심 수치는 다음과 같다.

- total rows: `2105`
- active total: `2084`
- silent total: `21`
- quality state counts: `strong 1316 / adequate 0 / weak 768`
- publish state counts: `internal_only 617 / exposed 1467`
- hard fail count: `0`
- preview structural flag counts: `BODY_LACKS_ITEM_SPECIFIC_USE 617 / FUNCTION_NARROW 7`

즉, decision stage는 새 structural signal을 읽되, **기존 publish split을 바꾸지 않고 authority ownership만 명문화한 상태로** 닫혔다.

## 8. Phase 5: dry-run delta와 baseline v4 동결

authority migration round가 실제 regression 없이 닫혔는지는 dry-run delta와 baseline freeze로 확인했다.

핵심 코드:

- `Iris/build/description/v2/tools/build/report_surface_contract_dry_run_delta.py`
- `Iris/build/description/v2/tools/build/freeze_quality_baseline_v4.py`
- `Iris/build/description/v2/tools/build/report_surface_contract_rollout_result.py`

핵심 산출물:

- `Iris/build/description/v2/staging/semantic_quality/phaseE_contract_migration/structural_audit_dry_run_delta.json`
- `Iris/build/description/v2/staging/semantic_quality/phaseE_contract_migration/quality_baseline_v4.json`
- `Iris/build/description/v2/staging/semantic_quality/phaseE_contract_migration/quality_baseline_v4.md`
- `Iris/build/description/v2/staging/semantic_quality/phaseE_contract_migration/surface_contract_rollout_result_report.json`
- `Iris/build/description/v2/staging/semantic_quality/phaseE_contract_migration/surface_contract_rollout_result_report.md`

dry-run delta 결과는 다음처럼 닫혔다.

- `strong_to_weak_count = 0`
- `adequate_to_weak_count = 0`
- `exposed_to_internal_only_count = 0`
- `internal_only_to_exposed_count = 0`
- `introduced_surface_regression_count = 0`
- `lane_stability_status = pass`

baseline v4는 다음 수치로 동결됐다.

- publish split: `internal_only 617 / exposed 1467`
- exposed quality ratio: `0.8970688479890934`
- expected internal_only range: `617..617`
- bridge publish state entry count: `2084`
- bridge runtime publish counts: `internal_only 617 / exposed 1467`

이 숫자의 의미는 단순하다.

- 이번 round는 publish behavior를 새로 바꿔서 통과한 것이 아니다.
- 기존 `identity_fallback` internal_only lane 위에 structural contract ownership만 얹었다.
- 따라서 성공 기준은 warn 감소가 아니라 **authority ownership 고정 + publish split 안정성 유지**였다.

## 9. Phase 6과 Phase 7: validation pack, fresh in-game rerun, closeout

이번 round는 offline artifact만으로 닫지 않았다. current baseline 기준 validation pack과 fresh manual rerun까지 다시 기록했다.

핵심 코드:

- `Iris/build/description/v2/tools/build/build_quality_publish_phase6_validation_pack.py`

핵심 산출물:

- `Iris/build/description/v2/staging/semantic_quality/phaseE_contract_migration/phase6_in_game_validation_pack.json`
- `Iris/build/description/v2/staging/semantic_quality/phaseE_contract_migration/phase6_in_game_validation_checklist.md`
- `Iris/build/description/v2/staging/semantic_quality/phaseE_contract_migration/in_game_validation_result.json`
- `Iris/build/description/v2/staging/semantic_quality/phaseE_contract_migration/in_game_validation_result.md`

`2026-04-08` fresh manual validation에서 확인한 항목은 다음 다섯 가지다.

- Browser/Wiki default surface의 `internal_only` suppression
- `exposed` body render
- context menu stability
- other layer regression 부재
- repeated open/close 기준 performance regression 부재

최종 closeout report는 다음처럼 닫혔다.

- rollout status: `rollout_pass_manual_validation_complete`
- newly isolated count: `0`
- reexposed count: `0`
- manual validation status: `pass`
- current round closeout evidence: `2026-04-08` fresh manual rerun pass

즉, 이 walkthrough 시점의 이번 round는 더 이상 manual validation blocker를 남기지 않는다.

## 10. 구현 세부: 왜 rendered text는 안 바뀌고 authority만 이동했는가

이번 round의 중요한 성질은 rendered text를 다시 쓰지 않았다는 점이다.

이것이 가능했던 이유는 세 가지다.

- structural audit는 rendered/body text를 rewrite하지 않고, structural role signal만 정리한다.
- decision stage는 current row를 `weak`나 `internal_only`로 다시 읽을 뿐 compose 결과를 고치지 않는다.
- browser/wiki consumer는 이미 존재하던 `publish_state` contract만 소비한다.

그래서 이번 round의 핵심 데모는 다음 한 줄로 요약된다.

> rendered text 한 글자도 바꾸지 않고,  
> 어떤 row를 default surface에 노출할지 결정하는 authority만 single-writer stage 안으로 명문화했다.

이 점 때문에 이번 round는 style upgrade나 compose repair round로 읽으면 안 된다.

## 11. 후속 handoff: source expansion은 이번 round 미완료가 아니라 다음 round 입력이다

이번 round가 닫힌 뒤 바로 만든 follow-up artifact는 다음이다.

- `Iris/build/description/v2/tools/build/report_identity_fallback_source_expansion_backlog.py`
- `Iris/build/description/v2/staging/semantic_quality/phaseE_contract_migration/identity_fallback_source_expansion_backlog.json`
- `Iris/build/description/v2/staging/semantic_quality/phaseE_contract_migration/identity_fallback_source_expansion_backlog.md`

이 artifact는 old `phase1_parallel` plan을 current `phaseE` baseline에 다시 연결하는 handoff report다.

정합성 결과는 다음처럼 닫혔다.

- plan row count: `617`
- policy isolation row count: `617`
- preview identity_fallback count: `617`
- all rows internal_only: `true`
- all rows identity origin: `true`

bucket 분포는 그대로 유지된다.

- `bucket_1_existing_cluster_reusable = 11`
- `bucket_2_net_new_cluster_required = 599`
- `bucket_3_out_of_dvf_scope_group_c = 7`

즉, source expansion은 이번 round가 덜 끝난 것이 아니라, **current closeout 위에서 다음 round로 넘겨진 explicit handoff backlog**다.

## 12. 최종 판정

이번 round는 다음 조건을 모두 충족한 상태로 완료됐다.

- `style_lint_report.json`은 advisory-only로 남았다.
- `surface_contract_signal.jsonl`이 별도 input artifact로 생성됐다.
- `quality/publish decision stage`만 single writer로 유지됐다.
- rendered text는 바뀌지 않았다.
- `internal_only` row는 runtime/bridge에서 보존됐다.
- Browser/Wiki default surface만 suppression을 수행했다.
- baseline-delta 기준 publish regression은 `0`이었다.
- `2026-04-08` fresh manual rerun이 `pass`로 기록됐다.

따라서 이번 round는 **completed**로 읽는 것이 맞다.

남아 있는 일은 이번 round 재개방이 아니라 다음 backlog다.

- `identity_fallback 617` source expansion
- future separate decision 이후의 `FUNCTION_NARROW` 2차 rollout 판단
- source expansion 재측정 이후의 `ACQ_DOMINANT` lane 판단

이 세 가지는 모두 current closeout 바깥의 후속 round다.
