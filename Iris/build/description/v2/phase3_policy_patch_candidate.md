# Phase 3 Policy Patch Candidate

## Trigger

Wave 3는 새 manual reason cluster 없이 닫혔지만, `Wearable.6-G`의 pure-foraging accessory row `33`건 때문에 known `LAYER_COLLISION` backlog가 급증했다.

- wave 3 manual rate: `0.1129`
- pilot combined manual baseline: `0.0417`
- cumulative HOLD backlog: `47`

## What Changed

- pure `채집으로 구할 수 있다` row는 기존 pilot 규칙대로 `MANUAL_OVERRIDE_CANDIDATE + LAYER_COLLISION`으로 유지됐다.
- same bucket 안의 location+foraging row는 `LOCATION_SPECIFIC` promote로 닫혀, 규칙 충돌이 아니라 known collision cluster의 대량 유입 문제가 드러났다.

## Decision

- selected option: `NO_RULE_CHANGE_BATCH_REVIEW`
- candidate_state 규칙은 변경하지 않는다.
- `Wearable.6-G` pure-foraging subset은 known `LAYER_COLLISION` batch로 분리해 approval backlog에서 별도 운영한다.
- wave acceptance / drift에서는 이 batch를 일반 manual drift와 분리해 읽는다.

## Rejected Patch

- `NARROW_KEEP_DOWNGRADE`
- pure-foraging accessory row를 `KEEP_SILENT + INTERACTION_LAYER_ONLY`로 내리는 예외 규칙은 채택하지 않는다.
- 이유: `KEEP_SILENT` 의미를 오염시키고, 구조적 `LAYER_COLLISION`을 운영 편의로 침묵 처리하는 결과가 되기 때문이다.

## Operational Effect

- 새 manual reason cluster가 생긴 게 아니라 known collision backlog가 집중 유입된 것으로 해석한다.
- stop rule은 candidate_state 규칙 패치 신호가 아니라, known collision batch를 별도 운영 대상으로 분리하라는 신호로 처리한다.
- wave 4는 batch backlog 처리 기준을 확인한 뒤 재개한다.
