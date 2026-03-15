# Phase 3 Rollout Seed Policy

## Decision

- rollout 시작 시 canonical full overlay seed는 `pilotA_candidate_state.review.jsonl`와 `pilotB_candidate_state.review.jsonl`만 사용한다.
- seed 방식은 direct-lift merge다. pilot overlay row를 재판정하거나 필드를 다시 쓰지 않고 canonical full overlay로 그대로 병합한다.
- non-pilot exploratory overlay는 initial seed에 포함하지 않는다.

## Why Pilot-Only

- `pilotA`와 `pilotB`는 validator/report PASS가 이미 닫혀 있다.
- 두 pilot 모두 compare-overlay 기반 2-run determinism PASS가 있다.
- 두 pilot이 promote-heavy와 mixed bucket을 각각 대표하므로 rollout 출발점으로 충분하다.
- `rollout_resource4b_candidate_state.review.jsonl`는 유효한 exploratory reference지만 pilot 범위 밖이고 second-run determinism 증거가 없어서 initial seed input으로는 기준이 약하다.

## Initial Seed Set

- include:
  - `staging/phase3/pilotA_candidate_state.review.jsonl`
  - `staging/phase3/pilotB_candidate_state.review.jsonl`
- exclude from initial seed:
  - `staging/phase3/rollout_resource4b_candidate_state.review.jsonl`

## Canonicalization Rule

- canonical target file는 `staging/phase3/candidate_state_phase3.review.jsonl`다.
- seed build는 `tools/build/build_phase3_rollout_seed.py`로 수행한다.
- build 결과로 아래를 항상 같이 갱신한다.
  - `staging/phase3/phase3_candidate_state_summary.json`
  - `staging/phase3/phase3_candidate_state_by_bucket.json`
  - `staging/phase3/phase3_candidate_state_gaps.json`
  - `staging/phase3/phase3_sync_queue.jsonl`

## Bucket Replacement Rule

- bucket는 row-level patch 단위가 아니라 atomic replace 단위다.
- 어떤 bucket를 rerun하면 해당 bucket의 canonical slice 전체를 새 overlay로 교체한다.
- old overlay 파일은 traceability artifact로 남겨도 되지만 canonical merge input에서는 제외한다.
- `candidate_state`와 `approval_state`는 계속 분리하고, sync queue rebuild는 canonical overlay 기준으로만 한다.

## Wave Handling

- Wave 1 시작 전 initial seed를 한 번 생성한다.
- 이후 accepted bucket가 생길 때마다 canonical overlay/report/queue를 다시 생성한다.
- wave acceptance 문서는 wave 경계에서 추가로 남기되, canonical file update를 wave 끝까지 미루지 않는다.

## Resource.4-B Rule

- `Resource.4-B`는 wave 2 exploratory reference로만 유지한다.
- canonical completion으로 계산하지 않는다.
- wave 2에서 bucket execution loop를 다시 돌리고 PASS한 overlay만 canonical merge input으로 승격한다.
