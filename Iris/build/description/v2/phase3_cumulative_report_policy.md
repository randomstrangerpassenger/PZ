# Phase 3 Cumulative Report Policy

## Authoritative Inputs

- cumulative Phase 3 truth source는 항상 `staging/phase3/candidate_state_phase3.review.jsonl` 하나다.
- cumulative report와 sync queue는 canonical overlay에서만 재계산한다.
- per-bucket overlay 파일은 working artifact이지만, canonical merge 전까지는 cumulative truth source가 아니다.

## Outputs

- summary: `staging/phase3/phase3_candidate_state_summary.json`
- by_bucket: `staging/phase3/phase3_candidate_state_by_bucket.json`
- gaps: `staging/phase3/phase3_candidate_state_gaps.json`
- sync queue: `staging/phase3/phase3_sync_queue.jsonl`

## Update Trigger

- initial seed build 직후 한 번 생성한다.
- bucket overlay가 validator PASS하면 canonical overlay를 regenerate하고 report 3종과 sync queue를 즉시 같이 regenerate한다.
- wave acceptance가 끝나면 별도 wave acceptance/drift artifact를 남기지만, canonical cumulative files는 이미 최신이어야 한다.

## Counting Rule

- cumulative summary의 `review_target_total`은 canonical overlay에 현재 적재된 row 수만 센다.
- rollout 전체 universe 기준 진행률은 `phase3_rollout_universe_manifest.json`의 reviewable total과 pending bucket 목록으로 별도 추적한다.
- `--require-complete` gate는 reviewable closed universe `2079` rows가 canonical overlay에 모두 적재된 마지막 시점에만 사용한다.

## Sync Queue Rule

- sync queue는 canonical overlay의 `PROMOTE_ACTIVE`와 `MANUAL_OVERRIDE_CANDIDATE` row만 포함한다.
- `KEEP_SILENT`는 queue에 들어가지 않는다.
- `approval_state`는 queue rebuild 과정에서만 계산하고 canonical overlay row를 바꾸지 않는다.
- HOLD backlog 분석은 queue 파생 산출물로 따로 관리하며 candidate_state 재평가와 섞지 않는다.

## Determinism And Replacement

- canonical regenerate는 같은 merge input이면 같은 determinism SHA를 내야 한다.
- bucket rerun이 있으면 해당 bucket의 old canonical slice를 제거하고 new slice를 넣은 뒤 전체 report/queue를 다시 계산한다.
- duplicate fulltype가 merge input에 있으면 cumulative build를 실패로 본다.

## Audit Boundary

- wave acceptance 문서와 drift report는 cumulative files의 스냅샷 해석 결과다.
- canonical summary/by_bucket/gaps/sync queue는 운영 파일이고, wave acceptance/diff 문서는 감사 기록이다.
