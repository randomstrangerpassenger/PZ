# Iris DVF 3-3 Body Plan Full Runtime Rollout Round Attempt

기준일: `2026-04-21`

## Correction Status

상태: `quarantined / not adopted`

이 문서는 same-session Phase E-0 / Phase E execution attempt의 기록이다. 후속 검토에서 이 attempt는 current closeout으로 채택하지 않기로 했다.

Quarantine 사유:

- 사전 `scope_policy_override_round` opening decision이 없다.
- 입력 source가 봉인된 current runtime baseline `2105 rows / active 2084 / silent 21`이 아니라 `1050` row snapshot이었다.
- `quality_publish_decision_v2_preview.full.jsonl`이 `quality_state / publish_state`를 새로 계산해 `adequate 130`을 만들었으므로 `quality_baseline_v4` 유지와 충돌한다.
- `1050` row 기반 `IrisLayer3Data.lua`는 deployed authority가 아니며, runtime Lua data는 sealed `quality_publish` bridge baseline으로 복구했다.

## Round Identity

이 attempt는 Phase D closeout 이후 여는 Phase E-0 / Phase E execution 후보였다. 목적은 `body_plan` compose 결과를 full-runtime gate로 검증하고 Lua bridge/runtime surface에 반영하는 것이었다.

## Scope

Phase E-0 포함:

- full-runtime row count consistency gate
- determinism gate
- legacy-vs-body_plan delta gate
- `unexpected_delta = 0`
- publish regression 없음 확인
- blocker inventory `0` 확인

Phase E 포함:

- full-runtime body_plan rendered preview를 Lua bridge 입력으로 사용
- `IrisLayer3Data.lua` 재생성
- Browser/Wiki/Lua renderer가 generated flat string과 `publish_state`를 소비하는지 static validation

제외:

- Phase D structural taxonomy 재개방
- writer 추가
- runtime-side compose / repair
- Browser/Wiki UI redesign

## Exit Gate

- regression gate report `pass`
- Lua bridge export report `pass`
- runtime validation report `ready_for_in_game_validation`
- `deployed_matches_staged` 또는 equivalent bridge parity 확인
- manual in-game validation은 별도 exhaustive QA가 아니라 static/runtime bridge closeout note로 남김

## Closeout Read

상태: `quarantined / not closed`

Diagnostic artifacts:

- `Iris/build/description/v2/staging/compose_contract_migration/full_runtime/body_plan_v2_regression_gate_report.json`
- `Iris/build/description/v2/staging/compose_contract_migration/full_runtime/body_plan_v2_lua_bridge_report.json`
- `Iris/build/description/v2/staging/compose_contract_migration/full_runtime/body_plan_v2_runtime_validation_report.json`
- `Iris/build/description/v2/staging/compose_contract_migration/full_runtime/body_plan_v2_runtime_rollout_report.json`
- `Iris/media/lua/client/Iris/Data/IrisLayer3Data.lua`

Quarantined E-0 regression gate snapshot:

- `overall_status = pass`
- row count: `1050`
- active/silent: `975 / 75`
- quality states: `strong 360 / adequate 130 / weak 485`
- publish states: `exposed 490 / internal_only 485`
- unexpected delta: `0`
- blocker count: `0`
- accidental change count: `0`
- hard block candidate: `0`

Quarantined E runtime rollout snapshot:

- Lua bridge source entries: `1050`
- Lua bridge runtime entries: `1050`
- runtime publish states: `internal_only 485 / exposed 490`
- static runtime validation: `ready_for_in_game_validation`
- deployed/staged Lua parity: `pass`

Manual in-game exhaustive sampling 없이 runtime rollout closeout을 선언하지 않는다. Future Phase E는 `2105` current runtime source, frozen `quality_baseline_v4 / quality_publish_decision_preview`, and in-game validation policy를 함께 닫아야 한다.
