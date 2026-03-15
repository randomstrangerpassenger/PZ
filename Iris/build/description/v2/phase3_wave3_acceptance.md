# Phase 3 Wave 3 Acceptance

## Scope

- wave: `wave3`
- buckets: `Consumable.3-E`, `Furniture.7-A`, `Vehicle.8-A`, `Wearable.6-G`
- canonical coverage rows: `319 / 319`

## Gate Result

Wave 3의 acceptance gate 자체는 `PASS`다. 다만 drift stop rule은 `NO_RULE_CHANGE_BATCH_REVIEW` 운영 분리를 요구하는 신호로 해석하고, 다음 wave advance는 `HOLD_PENDING_BATCH_REVIEW`로 본다.

근거:

- wave 3 bucket 4개가 모두 canonical overlay에 반영됐다.
- invalid combo: `0`
- snapshot mismatch: `0`
- excluded/unreviewed contamination: `0`
- cumulative summary / by_bucket / gaps regenerate PASS
- cumulative sync queue rebuild PASS
- cumulative HOLD queue rebuild PASS

## State Breakdown

- `PROMOTE_ACTIVE=97`
- `KEEP_SILENT=186`
- `MANUAL_OVERRIDE_CANDIDATE=36`
- direct sync-ready rows added by wave 3: `97`
- HOLD rows added by wave 3: `36`
- known batch review rows added by wave 3: `33`
- general manual rows added by wave 3: `3`

## Notes

- `Wearable.6-G`에서 pure-foraging accessory row `33`건이 모두 기존 `LAYER_COLLISION` 군집으로 수렴했다.
- Wave 3 general manual은 `Consumable.3-E`의 `3`건뿐이고, 급증분 대부분은 known collision batch 유입이다.
- [phase3_policy_patch_candidate.md](/C:/Users/MW/Downloads/coding/PZ/Iris/build/description/v2/phase3_policy_patch_candidate.md)에 따라 candidate_state 규칙은 유지하고, `Wearable.6-G` subset은 batch approval review로 분리 운영한다.
