# Iris DVF 3-3 Body Plan Structural Violation Redesign Round Attempt

기준일: `2026-04-21`

## Correction Status

상태: `quarantined / not adopted`

이 문서는 same-session Phase D execution attempt의 기록이다. 후속 검토에서 이 attempt는 current closeout으로 채택하지 않기로 했다.

Quarantine 사유:

- 사전 `scope_policy_override_round` opening decision이 없다.
- 입력 source가 봉인된 current runtime baseline `2105 rows / active 2084 / silent 21`이 아니라 `historical_snapshot/full_runtime`의 `1050` rows였다.
- 아래 artifact는 Phase E-0 gate input으로 채택하지 않는다.

## Round Identity

이 attempt는 `compose authority migration round`의 A+B+C closeout 이후 여는 Phase D execution 후보였다. 목적은 rendered 문장을 다시 쓰는 것이 아니라, `body_plan` section trace를 기준으로 structural signal 계상 방식을 재정의하는 것이었다.

## Scope

포함:

- `LAYER4_ABSORPTION`을 `body_plan` section / overlay source 기준 proxy signal로 재정의
- legacy structural family(`IDENTITY_ONLY / BODY_LACKS_ITEM_SPECIFIC_USE / FUNCTION_NARROW / ACQ_DOMINANT`)를 section coverage 기준 reclassification report로 고정
- new proxy flags(`INTERACTION_LIST_DUPLICATION / CROSS_LAYER_RAW_COPY / SECTION_COVERAGE_DEFICIT / BODY_COLLAPSES_TO_ACQUISITION / BODY_LOSES_ITEM_CENTRICITY`)와 legacy family bridge를 함께 기록
- structural signal은 validator/report 계층에서만 산출

제외:

- `compose_layer3_text.py` writer 재설계
- `quality_state / publish_state` axis 재정의
- runtime Lua consumer 변경
- full-runtime rollout gate

## Ownership

- writer: `compose_layer3_text.py`의 `body_plan` section emission만 권위
- structural report: section trace를 읽는 observer / validator 계층
- quality/publish decision stage: post-compose single writer 유지
- runtime consumer: staged flat string만 소비

## Exit Gate

- full-runtime active rows에 대해 section-based structural reclassification artifact 생성
- `LAYER4_ABSORPTION` proxy family count와 hard-block candidate count 기록
- legacy family bridge count 기록
- structural report가 rendered 문장이나 publish decision을 직접 변경하지 않음 확인
- Phase E-0 regression gate의 입력으로 쓸 수 있는 summary 생성

## Closeout Read

상태: `quarantined / not closed`

Diagnostic artifacts:

- `Iris/build/description/v2/staging/compose_contract_migration/full_runtime/body_plan_structural_reclassification.full.jsonl`
- `Iris/build/description/v2/staging/compose_contract_migration/full_runtime/body_plan_structural_reclassification.summary.full.json`

Quarantined snapshot:

- row count: `1050`
- runtime split: `active 975 / silent 75`
- legacy family bridge: `BODY_LACKS_ITEM_SPECIFIC_USE 485 / none 565`
- proxy flags: `SECTION_COVERAGE_DEFICIT 459 / BODY_LOSES_ITEM_CENTRICITY 37`
- hard block candidate: `0`

이 attempt는 structural signal 계상만 수행했으나, `1050` row subset을 current full-runtime처럼 읽었기 때문에 closeout evidence가 아니다. Future Phase D는 `2105` current runtime source를 precondition으로 다시 열어야 한다.
