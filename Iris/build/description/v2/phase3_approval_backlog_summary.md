# Phase 3 Approval Backlog Summary

> 이 문서는 approval backlog 운영의 기준선 수치를 한 페이지에 보여준다.
> 모든 수치는 `phase3_approval_backlog_manifest.json`과 동기된다.

---

## 전체 현황

| 항목 | 값 |
|---|---|
| Canonical overlay rows | `2079` |
| Sync queue total | `1247` |
| APPROVE_SYNC | `1050` |
| **HOLD (approval backlog)** | **`197`** |

---

## Approval Reason 분포

| Reason | 건수 | 비율 |
|---|---|---|
| `MANUAL_REVIEW_REQUIRED` | 158 | 80.2% |
| `CONTEXTUAL_PROMOTE_REVIEW` | 39 | 19.8% |

---

## HOLD Tier 분포

| Tier | 건수 | 설명 |
|---|---|---|
| Known Batch Review | 33 | `Wearable.6-G` pure-foraging accessory collision |
| Known Hotspot | 3 | `Consumable.3-E` manual concentration 3/3 |
| General Hold | 161 | 일반 보류 (미분류) |
| **합계** | **197** | |

---

## Bucket별 분포

| Bucket | 건수 | Approval Reason | 비고 |
|---|---|---|---|
| `Consumable.3-A` | 109 | MANUAL_REVIEW_REQUIRED | foraging/farming collision (general hold에 속함) |
| `Wearable.6-G` | 33 | MANUAL_REVIEW_REQUIRED | **known batch review** |
| `Wearable.6-B` | 24 | CONTEXTUAL_PROMOTE_REVIEW | IDENTITY_LINKED |
| `Tool.1-L` | 10 | Mixed (CPR 7 + MRR 3) | USE_CONTEXT/IDENTITY + collision |
| `Wearable.6-C` | 5 | CONTEXTUAL_PROMOTE_REVIEW | IDENTITY_LINKED |
| `Misc.9-A` | 4 | MANUAL_REVIEW_REQUIRED | foraging collision |
| `Consumable.3-E` | 3 | MANUAL_REVIEW_REQUIRED | **known hotspot** |
| `Wearable.6-A` | 2 | CONTEXTUAL_PROMOTE_REVIEW | IDENTITY_LINKED |
| `Consumable.3-B` | 1 | CONTEXTUAL_PROMOTE_REVIEW | USE_CONTEXT_LINKED |
| `Literature.5-D` | 1 | MANUAL_REVIEW_REQUIRED | collision |
| `Resource.4-A` | 1 | MANUAL_REVIEW_REQUIRED | collision |
| `Resource.4-B` | 1 | MANUAL_REVIEW_REQUIRED | collision |
| `Resource.4-C` | 1 | MANUAL_REVIEW_REQUIRED | collision |
| `Resource.4-F` | 1 | MANUAL_REVIEW_REQUIRED | collision |
| `Tool.1-B` | 1 | MANUAL_REVIEW_REQUIRED | collision |

---

## Canonical Reference

- determinism SHA: `409dff500686f4b7058484437c5c05d74640dc74c86a2d5cd87d32965621086a`
- candidate-state는 이 manifest에서 변경하지 않는다.
