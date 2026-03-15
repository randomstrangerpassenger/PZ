# Phase 3 Rollout Wave Plan

## Scope Lock

- 기준 시점: `2026-03-13`
- 입력 기준: `staging/acquisition_coverage_summary.json`, `staging/acquisition_coverage_by_bucket.json`, 기존 Phase 3 pilot/resource overlay
- rollout universe: reviewable closed `46` buckets / `2079` rows
- 제외 audit bucket: `SYSTEM_BLOCKLIST` / `206` rows / rollout 대상 아님
- Phase 2는 계속 immutable input이고, canonical Phase 3 target은 `staging/phase3/candidate_state_phase3.review.jsonl`로 유지한다.

## Seed Posture

- initial canonical seed는 `pilotA_candidate_state.review.jsonl`와 `pilotB_candidate_state.review.jsonl`만 쓴다.
- seed 방식은 direct-lift merge다. pilot row를 다시 해석하거나 필드를 재작성하지 않고 canonical full overlay로 그대로 승격한다.
- `Resource.4-B`는 `rollout_resource4b_candidate_state.review.jsonl`가 이미 있지만 pilot 범위 밖이고 compare-overlay determinism 증거가 없으므로 initial seed에는 넣지 않는다.
- 따라서 `Resource.4-B`는 wave 2의 exploratory reference로만 남기고, canonical full overlay에는 wave execution 규약으로 다시 편입한다.

## Wave Summary

| Wave | Class | Buckets | Total Rows | Already Covered | New Execution Rows | Purpose |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| Wave 1 | low-collision / high-signal | 5 | 56 | 27 | 29 | promote path를 빠르게 누적하면서 validator/report/canonical 루프를 안정화 |
| Wave 2 | mixed keep/promote | 5 | 197 | 45 | 152 | keep logic과 `ACQ_NULL` 처리, generic keep 경계를 대량 검증 |
| Wave 3 | collision-heavy | 4 | 319 | 0 | 319 | `채집`, 회수, 분해 계열의 3-3/3-4 drift와 HOLD queue 압력을 통제 |
| Wave 4 | long-tail / residual | 32 | 1507 | 0 | 1507 | 앞선 wave 규약으로 남은 잔여 bucket를 일괄 마감 |

## Wave 1

- `Consumable.3-C` (`27`, pilot seed): promote-heavy medical bucket으로 이미 `0` manual을 증명했다.
- `Combat.2-G` (`6`): 총기 보관/진열 출처가 직접적이라 location-specific promote 검증용으로 적합하다.
- `Combat.2-L` (`14`): 총기 부속 획득처가 명확하고 bucket 공통 genericity가 낮다.
- `Tool.1-A` (`6`): 모루 기반 제작 경로가 item-specific method로 닫히기 쉽다.
- `Tool.1-I` (`3`): 전자 부품 조립형 도구라 method-specific promote만 짧게 검증하기 좋다.

Wave 1 시작 대상은 seed bucket을 제외한 `Combat.2-G -> Combat.2-L -> Tool.1-A -> Tool.1-I` 순서로 닫는다.

## Wave 2

- `Tool.1-L` (`45`, pilot seed): keep/promote/manual 경계가 이미 검증된 mixed 기준 bucket이다.
- `Resource.4-B` (`52`, exploratory reference): existing overlay가 `keep=31 / promote=20 / manual=1`이라 mixed 운영 기준점으로 쓰되, canonical seed에는 넣지 않고 wave 2 재실행 대상으로 둔다.
- `Resource.4-E` (`45`): 전자용품 발견, 회수, 제작이 섞여 있어 generic keep과 promote 경계를 같이 본다.
- `Literature.5-B` (`30`): 잡지류 중심 generic keep에 `ACQ_NULL`이 섞여 keep logic 스트레스 테스트로 적합하다.
- `Wearable.6-F` (`25`): survival gear 계열이라 location mix와 `ACQ_NULL`이 함께 나타난다.

Wave 2는 promote 확장보다 keep logic, `ACQ_NULL`, partial HOLD 증가율을 보는 구간이다. 실행 순서는 `Resource.4-B -> Resource.4-E -> Literature.5-B -> Wearable.6-F`가 기본이다.

## Wave 3

- `Consumable.3-E` (`3`): 전 row가 `채집으로 구할 수 있다`라서 낮은 비용으로 foraging collision을 먼저 측정할 수 있다.
- `Furniture.7-A` (`140`): 배치 시설물 회수 문구가 `INTERACTION_LAYER_ONLY` 또는 layer collision로 흐를 위험이 크다.
- `Vehicle.8-A` (`46`): 차량 분리/엔진 분해 경로가 system interaction 설명으로 미끄러질 수 있다.
- `Wearable.6-G` (`130`): 장신구/시계 계열이 대부분 forage-linked라 manual/HOLD queue 압력 관찰에 가장 적합하다.

Wave 3는 stop rule을 실제로 발동시킬 가능성이 가장 높은 구간이다. 여기서 manual rate나 새로운 manual cluster가 pilot 대비 급증하면 Wave 4로 넘어가기 전에 patch 여부를 먼저 판정한다.

## Wave 4

- Consumable residual: `Consumable.3-A`, `Consumable.3-B`, `Consumable.3-D`
- Resource residual: `Resource.4-A`, `Resource.4-C`, `Resource.4-D`, `Resource.4-F`
- Vehicle residual: `Vehicle.8-B`
- Literature residual: `Literature.5-A`, `Literature.5-C`, `Literature.5-D`
- Tool residual: `Tool.1-B`, `Tool.1-D`, `Tool.1-H`, `Tool.1-J`, `Tool.1-K`
- Combat residual: `Combat.2-A`, `Combat.2-B`, `Combat.2-C`, `Combat.2-D`, `Combat.2-E`, `Combat.2-F`, `Combat.2-H`, `Combat.2-I`, `Combat.2-J`, `Combat.2-K`
- Wearable residual: `Wearable.6-A`, `Wearable.6-B`, `Wearable.6-C`, `Wearable.6-D`, `Wearable.6-E`
- Mixed long-tail residual: `Misc.9-A`

Wave 4는 앞선 wave에서 reason drift와 HOLD queue 증감이 허용 범위 안에 있다는 전제에서만 연다. 특히 `Consumable.3-A`, `Wearable.6-A/B/C`, `Misc.9-A`는 row 수가 커서 prior wave patch 결과를 반영한 뒤 들어가는 것이 안전하다.

## Closure Checks

- 모든 reviewable bucket `46`개를 정확히 한 wave에만 배치했다.
- pilot bucket은 자연 wave에 포함했지만 execution target이 아니라 canonical seed 대상으로 표시했다.
- `Resource.4-B`는 exploratory reference를 유지하되 canonical pending bucket으로 남겼다.
- `SYSTEM_BLOCKLIST`는 universe manifest에서 별도 audit bucket으로 남기고 rollout wave에서는 제외했다.
- initial canonical seed는 pilot 2개만으로 바로 생성 가능하고, 그 뒤 Wave 1 pending bucket 실행을 시작할 수 있다.
