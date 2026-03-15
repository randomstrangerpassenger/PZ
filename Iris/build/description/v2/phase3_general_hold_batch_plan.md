# Phase 3 General Hold Batch Plan

> general hold 161건에서 contextual promote(39건)를 분리한 뒤, MANUAL_REVIEW_REQUIRED 122건을 소배치로 나눠 cluster-level review를 진행한다.
> candidate-state baseline은 유지한다.

---

## General Hold 구성 분석

총 general hold 161건의 실제 구성:

| 분류 | 건수 | 처리 트랙 |
|---|---|---|
| MANUAL_REVIEW_REQUIRED (LAYER_COLLISION) | 122 | **이 문서** (Step 5) |
| CONTEXTUAL_PROMOTE_REVIEW | 39 | Step 6 별도 처리 |
| **합계** | **161** | |

### MANUAL_REVIEW_REQUIRED 122건의 collision 패턴 분석

hold_review_backlog.md에서 122건 전부의 collision note를 확인한 결과:

**전부 동일 구조의 collision이다.**

- collision 원인: 채집/낚시/농사 등 시스템 획득 채널 정보(3-4 상호작용층)가 3-3 개별 설명층과 겹침
- item-specific 장소 맥락 부재로 3-3 승격 규칙으로 닫을 수 없음
- 이미 known batch(Wearable.6-G 33건)과 known hotspot(Consumable.3-E 3건)에서 **동일 패턴으로 KEEP_HOLD_CLUSTER** 결론이 남

---

## Batch 구성

### 배치 분할 기준

122건 전부가 동일 collision 패턴(foraging/farming/fishing LAYER_COLLISION)이므로, 개별 철학 재논의가 불필요하다. bucket 단위로 grouping한다.

### Batch 목록

| Batch | Bucket | 건수 | Collision 유형 | Grouping Rule |
|---|---|---|---|---|
| **Batch 1** | `Consumable.3-A` | 109 | foraging/farming/fishing collision | 동일 bucket, 동일 collision |
| **Batch 2** | `Misc.9-A` | 4 | foraging collision | 동일 bucket, 동일 collision |
| **Batch 3** | `Tool.1-L` (MRR only) | 3 | foraging collision (bags: Handbag, Purse, BowlingBallBag) | MRR subset만 추출 |
| **Batch 4** | 산발 collision | 6 | foraging/channel collision | Resource.4-A,B,C,F + Literature.5-D + Tool.1-B |
| **합계** | | **122** | | |

---

## Batch 1: Consumable.3-A (109건) — Cluster Review

### Cluster 정보

| 항목 | 값 |
|---|---|
| batch_id | `GENERAL_HOLD_CONSUMABLE_3A_FORAGING_COLLISION` |
| bucket | `Consumable.3-A` |
| row 수 | 109 |
| candidate_state | `MANUAL_OVERRIDE_CANDIDATE` (전부) |
| candidate_reason_code | `LAYER_COLLISION` (전부) |
| collision 패턴 | 채집/낚시/농사 가능 여부가 3-4 상호작용층과 겹침 |

### Review 결과

**Q1. sync 가능한가?** → **아니다.** 109건 전부 동일한 foraging collision. Wearable.6-G(33건), Consumable.3-E(3건)과 같은 패턴. sync하면 3-4 정보가 3-3에 흘러들어감.

**Q2. 계속 HOLD가 맞는가?** → **맞다.** 층 경계 규칙 변경 없이는 해소 불가. 이 109건은 approval backlog에서 가장 큰 단일 군이며, 규칙 변경 시 파급 범위가 가장 넓다.

**Q3. 분리 검토?** → **불필요.** 109건 전부 동일 collision note. 예외 row 없음.

**결론: `KEEP_HOLD_CLUSTER`**

```
batch=GENERAL_HOLD_CONSUMABLE_3A_FORAGING_COLLISION | status=KEEP_HOLD | reason=foraging/farming/fishing LAYER_COLLISION; 3-3 vs 3-4 structural boundary | count=109 | candidate_state_change=none | review_date=2026-03-14
```

---

## Batch 2: Misc.9-A (4건) — Cluster Review

### 대상

| # | fulltype | collision note |
|---|---|---|
| 1 | `Base.Pinecone` | 채집 foraging collision |
| 2 | `Base.Stone` | 채집 foraging collision |
| 3 | `Base.Twigs` | 채집 foraging collision |
| 4 | `camping.Flint` | 채집 foraging collision |

### Review 결과

**Q1. sync 가능?** → **아니다.** Consumable.3-A 군과 동일 collision 패턴.
**Q2. HOLD 유지?** → **맞다.**
**Q3. 분리?** → **불필요.**

**결론: `KEEP_HOLD_CLUSTER`**

```
batch=GENERAL_HOLD_MISC_9A_FORAGING_COLLISION | status=KEEP_HOLD | reason=foraging LAYER_COLLISION; same structural pattern as Consumable.3-A | count=4 | candidate_state_change=none | review_date=2026-03-14
```

---

## Batch 3: Tool.1-L MRR subset (3건) — Cluster Review

### 대상

| # | fulltype | collision note |
|---|---|---|
| 1 | `Base.Bag_BowlingBallBag` | 채집 foraging collision |
| 2 | `Base.Handbag` | 채집 foraging collision |
| 3 | `Base.Purse` | 채집 foraging collision |

### Review 결과

**Q1. sync 가능?** → **아니다.** 동일 foraging collision 패턴.
**Q2. HOLD 유지?** → **맞다.**
**Q3. 분리?** → **불필요.**

**결론: `KEEP_HOLD_CLUSTER`**

```
batch=GENERAL_HOLD_TOOL_1L_MRR_FORAGING_COLLISION | status=KEEP_HOLD | reason=foraging LAYER_COLLISION; bags found via looting are system-level acquisition channel info | count=3 | candidate_state_change=none | review_date=2026-03-14
```

---

## Batch 4: 산발 collision (6건) — Cluster Review

### 대상

| # | bucket | fulltype | collision note |
|---|---|---|---|
| 1 | `Literature.5-D` | `Base.Journal` | 채집 발견물 문구가 시스템 획득 채널 설명과 겹침 |
| 2 | `Resource.4-A` | `Base.Log` | 채집 문구가 시스템 획득 채널 설명과 겹침 |
| 3 | `Resource.4-B` | `Base.Frog` | 채집 문구가 시스템 획득 채널 설명과 겹침 |
| 4 | `Resource.4-C` | `Base.TreeBranch` | 채집 foraging collision |
| 5 | `Resource.4-F` | `Base.Rope` | 쓰레기 채집 foraging collision |
| 6 | `Tool.1-B` | `Base.SharpedStone` | 채집 foraging collision |

### Review 결과

**Q1. sync 가능?** → **아니다.** 전부 동일한 acquisition channel collision.
**Q2. HOLD 유지?** → **맞다.** 개별 bucket에 1~2건씩 산재하지만 collision 성격은 동일.
**Q3. 분리?** → **불필요.** 6건 전부 같은 structural boundary 문제.

**결론: `KEEP_HOLD_CLUSTER`**

```
batch=GENERAL_HOLD_SCATTERED_FORAGING_COLLISION | status=KEEP_HOLD | reason=foraging/channel LAYER_COLLISION across multiple buckets; same structural pattern | count=6 | candidate_state_change=none | review_date=2026-03-14
```

---

## 전체 General Hold MANUAL_REVIEW_REQUIRED 요약

| Batch | 건수 | 결론 | 근거 |
|---|---|---|---|
| Consumable.3-A | 109 | KEEP_HOLD_CLUSTER | foraging/farming/fishing collision |
| Misc.9-A | 4 | KEEP_HOLD_CLUSTER | foraging collision |
| Tool.1-L MRR | 3 | KEEP_HOLD_CLUSTER | foraging collision (bags) |
| 산발 collision | 6 | KEEP_HOLD_CLUSTER | foraging/channel collision |
| **합계** | **122** | **전부 KEEP_HOLD** | **동일 구조적 경계 문제** |

### 핵심 관찰

122건 전부가 동일 collision 패턴이다. 이는 known batch(33건)과 known hotspot(3건)까지 포함하면 **MANUAL_REVIEW_REQUIRED 158건 전부**가 같은 3-3 vs 3-4 구조적 경계 충돌이다.

이 158건을 해소하려면 층 경계 규칙 자체를 재검토해야 하며, 이는 approval backlog 단계의 책임 범위를 넘는다. 따라서 전부 정책적 KEEP_HOLD로 닫고, 추후 층 경계 재검토 시에만 재오픈한다.

---

## Candidate-state 불변 확인

- 122건 전부 candidate_state, candidate_reason_code, candidate_compose_profile 변경 없음
- phase3_notes 변경 없음
- approval_state 계층에서만 review 결론 기록
