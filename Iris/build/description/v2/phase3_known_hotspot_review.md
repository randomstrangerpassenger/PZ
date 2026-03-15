# Phase 3 Known Hotspot Review

> `HOTSPOT_CONSUMABLE_3E_FORAGING_COLLISION` cluster (Consumable.3-E, 3건)에 대한 cluster-level approval review.
> candidate-state baseline은 유지한다. 이 문서는 approval 관점의 결론만 기록한다.

---

## Cluster 정보

| 항목 | 값 |
|---|---|
| cluster_id | `HOTSPOT_CONSUMABLE_3E_FORAGING_COLLISION` |
| bucket | `Consumable.3-E` |
| row 수 | `3` |
| hotspot_type | `manual_concentration_3_of_3` |
| candidate_state | `MANUAL_OVERRIDE_CANDIDATE` (전부 동일) |
| candidate_reason_code | `LAYER_COLLISION` (전부 동일) |
| approval_reason_code | `MANUAL_REVIEW_REQUIRED` (전부 동일) |

---

## Step 1. Cluster 묶음 확인

3건 전부가 동일 cluster에 소속되어 있음을 확인했다.

- bucket: `Consumable.3-E` — 3건 전부 일치
- candidate_reason: `LAYER_COLLISION` — 3건 전부 일치
- collision 패턴: "채집 가능 여부는 시스템 획득 채널 정보라 3-4 상호작용층과 겹치고, 현재 row에는 item-specific 장소 맥락이 없어 3-3 승격 규칙으로 닫기 어렵다" — 3건 전부 동일
- `phase3_approval_hotspot_clusters.json` 정의와 실제 row 일치 확인: ✓

대상 fulltypes (3건):

| # | fulltype |
|---|---|
| 1 | `Base.Comfrey` |
| 2 | `Base.Lemongrass` |
| 3 | `Base.Plantain` |

---

## Step 2. Candidate-state 재검토 금지 확인

- `candidate_state = MANUAL_OVERRIDE_CANDIDATE` — **변경하지 않음**
- `candidate_reason_code = LAYER_COLLISION` — **변경하지 않음**
- `candidate_compose_profile` — **변경하지 않음**
- `phase3_notes` — **읽기 전용**

이 3건은 약용/허브 소비재(comfrey, lemongrass, plantain)로, 채집 가능 여부가 3-4 상호작용층 정보와 겹치는 구조적 collision이다. `Consumable.3-A`의 109건(식용 채집물)과 본질적으로 같은 패턴이며, `Wearable.6-G`의 33건(pure-foraging accessory)과도 동일한 구조적 경계 문제다.

---

## Step 3. Approval 질문 3개

### Q1. 이 cluster를 지금 sync 가능한가?

**아니다.**

이 3건은 전부 "채집 가능 여부"라는 시스템 획득 채널 정보를 3-3 개별 설명에 넣으려는 시도에서 발생한 collision이다. sync하면 3-4 상호작용층 정보가 3-3 개별 설명층에 흘러들어가 층 경계가 오염된다.

Consumable.3-E는 Consumable.3-A(109건)와 같은 foraging collision 패턴이며, bucket이 다를 뿐 collision 성격은 동일하다. 한쪽만 sync하면 일관성이 깨진다.

### Q2. 계속 HOLD가 맞는가?

**맞다.**

- 층 경계 규칙이 바뀌지 않는 한, 이 collision은 해소되지 않는다.
- 이 3건을 위해 규칙을 바꾸면 Consumable.3-A 109건, Wearable.6-G 33건에도 동일 효과가 파급된다.
- 규칙 변경은 approval backlog 단계의 책임이 아니다.

### Q3. 일부만 분리 검토해야 하는가?

**아니다.**

3건 전부 동일한 collision 패턴(약용/허브 채집물의 foraging collision)이고, 예외적인 row가 없다. 분할은 불필요하다.

---

## Step 4. Cluster 단위 결론

### 결론: `KEEP_HOLD_CLUSTER`

| 항목 | 값 |
|---|---|
| 결론 | `KEEP_HOLD_CLUSTER` |
| 근거 | 3-3/3-4 구조적 충돌. Consumable.3-A 109건과 동일 foraging collision 패턴. 규칙 변경 없이 정책적 HOLD 유지 |
| candidate-state 변경 | **없음** |
| approval_state 변경 | 없음 (HOLD 유지) |
| cluster_status 전이 | `OPEN` → `KEEP_HOLD` |
| 후속 조치 | 층 경계 규칙이 추후 재검토될 경우에만 재오픈 가능 |

---

## Hotspot Review 절차 검증 결과

이 review는 hotspot cluster 절차의 첫 실사용이었다. 검증 결과:

1. **cluster 묶음 확인** — `phase3_approval_hotspot_clusters.json` 정의와 실제 hold_review_backlog의 row가 정확히 일치했다. 절차 작동함.
2. **candidate-state 보호** — 재검토 금지 확인 단계가 불필요한 drift를 차단했다. 절차 유효함.
3. **3-질문 review** — cluster 단위로 한 번만 답하면 3건 전부에 적용 가능했다. row-by-row 반복 없이 닫힘. 절차 효율적.
4. **cluster 결론 기록** — `KEEP_HOLD_CLUSTER`로 닫았으며, 향후 같은 패턴의 hotspot에도 동일 절차 적용 가능. 절차 재사용 가능.

**절차 수정 필요 사항**: 없음. 현재 4단계 절차를 그대로 유지한다.

---

## 운영 note

```
cluster=HOTSPOT_CONSUMABLE_3E_FORAGING_COLLISION | status=KEEP_HOLD | reason=medicinal herb foraging LAYER_COLLISION; 3-3 vs 3-4 structural boundary; same pattern as Consumable.3-A (109) and Wearable.6-G (33) | candidate_state_change=none | review_date=2026-03-14 | conclusion=KEEP_HOLD_CLUSTER | procedure_validation=PASS
```
