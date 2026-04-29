# Publish State Mapping Table

> 상태: draft v0.1  
> 기준일: 2026-04-08  
> scope: `surface contract authority migration`

---

## Decision Mapping

| input condition | decision stage 처리 | 비고 |
|---|---|---|
| baseline rule: `origin == identity_fallback` | `publish_state = internal_only` | 기존 lane 유지 |
| `hard_fail + hard_block_candidate` | `publish_state = internal_only` | `quality_state = weak`도 동시 적용 |
| `hard_block_candidate` | `publish_state = internal_only` | current implementation상 hard_fail과 함께만 사용 중 |
| `publish_isolation_candidate` + rollout lane open | `publish_state = internal_only` 가능 | current round는 `IDENTITY_ONLY` / explicit `BODY_LACKS_ITEM_SPECIFIC_USE`만 열림 |
| `publish_isolation_candidate` + rollout hold | 기존 publish 유지 | `FUNCTION_NARROW`, `ACQ_DOMINANT` current hold |
| signal 없음 / advisory-only | 기존 publish 유지 | writer non-owner |

## Current Round Snapshot

- active rows: `2084`
- `internal_only`: `617`
- `exposed`: `1467`
- `exposed -> internal_only` 신규 이동: `0`
- `internal_only -> exposed` 역이동: `0`

## 해석 규칙

- `internal_only`는 deletion contract가 아니다.
- bridge/runtime row는 보존한다.
- Browser/Wiki default surface만 suppression한다.
- `recommended_tier`는 recommendation이며, 최종 state write는 decision stage가 닫는다.
