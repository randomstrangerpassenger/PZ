# Phase 3 Contextual Promote Review

> CONTEXTUAL_PROMOTE_REVIEW 39건에 대한 별도 트랙 review.
> manual review backlog(LAYER_COLLISION 158건)와 성격이 다르므로 분리 처리한다.
> candidate-state baseline은 유지한다.

---

## Overview

| 항목 | 값 |
|---|---|
| 총 건수 | 39 |
| candidate_state | `PROMOTE_ACTIVE` (전부) |
| approval_reason | `CONTEXTUAL_PROMOTE_REVIEW` (전부) |
| candidate_reason 분포 | `IDENTITY_LINKED` = 33, `USE_CONTEXT_LINKED` = 6 |

**핵심 차이**: 이 39건은 LAYER_COLLISION이 아니다. candidate-state가 `PROMOTE_ACTIVE`로 판정된 상태에서, 문맥 적합성 검토(canon voice + layer-fit)가 필요해서 HOLD된 것이다. 즉 "구조적으로 sync 불가"가 아니라 "문맥 검토 후 sync 가능 여부를 본다"는 성격이다.

---

## Bucket별 분석

### Sub-batch A: Wearable.6-B (24건) — IDENTITY_LINKED

직업/브랜드 의류. 직업 정체성 또는 게임 내 브랜드와 연결된 아이템.

| # | fulltype | 성격 |
|---|---|---|
| 1 | `Base.Apron_PileOCrepe` | 브랜드 앞치마 |
| 2 | `Base.Apron_PizzaWhirled` | 브랜드 앞치마 |
| 3 | `Base.Jacket_Chef` | 직업 자켓 |
| 4 | `Base.Jacket_Ranger` | 직업 자켓 |
| 5 | `Base.Shirt_Jockey01~06` | 직업 셔츠 (6건) |
| 6 | `Base.Shirt_Priest` | 직업 셔츠 |
| 7 | `Base.Shirt_Ranger` | 직업 셔츠 |
| 8 | `Base.Tshirt_Fossoil` | 브랜드 티셔츠 |
| 9 | `Base.Tshirt_Gas2Go` | 브랜드 티셔츠 |
| 10 | `Base.Tshirt_McCoys` | 브랜드 티셔츠 |
| 11 | `Base.Tshirt_Profession_Police*` | 직업 티셔츠 (2건) |
| 12 | `Base.Tshirt_Profession_Ranger*` | 직업 티셔츠 (2건) |
| 13 | `Base.Tshirt_Ranger` | 직업 티셔츠 |
| 14 | `Base.Tshirt_ThunderGas` | 브랜드 티셔츠 |
| 15 | `Base.Vest_Waistcoat_GigaMart` | 브랜드 조끼 |
| 16 | `Base.WeddingDress` | 이벤트 의류 |
| 17 | `Base.WeddingJacket` | 이벤트 의류 |

**Review 질문 적용:**

**Q1. approval note만 추가하면 바로 sync 가능한가?**

→ **가능하다.** 이 24건은 전부 IDENTITY_LINKED다. 직업/브랜드와 연결된 의류는 3-3 개별 설명층에서 해당 직업이나 브랜드를 언급하는 것이 layer-fit하다. "이 셔츠는 레인저 유니폼이다" 같은 설명은 item-specific 정체성 정보이므로 3-4 상호작용층이 아니라 3-3 개별 설명층에 속한다.

**Q2. 추가 맥락 설명이 필요한가?**

→ **불필요하다.** 직업/브랜드 연결은 아이템 이름과 DisplayCategory에서 이미 드러나 있다. canon voice 적합성은 기계적으로 검증할 수 있는 수준이며, 특별한 추가 맥락 설명 없이 sync 가능하다.

**Q3. 계속 HOLD?**

→ **아니다.** APPROVE_SYNC로 전환한다.

**결론: `APPROVE_SYNC`** — 24건 전부

```
batch=CPR_WEARABLE_6B_IDENTITY | status=APPROVE_SYNC | reason=IDENTITY_LINKED clothing; profession/brand identity is item-specific 3-3 layer-fit | count=24 | candidate_state_change=none | review_date=2026-03-14
```

---

### Sub-batch B: Tool.1-L CPR subset (7건) — USE_CONTEXT/IDENTITY_LINKED

| # | fulltype | reason | 성격 |
|---|---|---|---|
| 1 | `Base.Bag_DoctorBag` | USE_CONTEXT_LINKED | 직업 맥락 가방 |
| 2 | `Base.Bag_JanitorToolbox` | USE_CONTEXT_LINKED | 직업 맥락 가방 |
| 3 | `Base.Lunchbag` | USE_CONTEXT_LINKED | 용도 맥락 |
| 4 | `Base.Lunchbox` | USE_CONTEXT_LINKED | 용도 맥락 |
| 5 | `Base.Lunchbox2` | USE_CONTEXT_LINKED | 용도 맥락 |
| 6 | `Base.Paperbag_Jays` | IDENTITY_LINKED | 브랜드 가방 |
| 7 | `Base.Paperbag_Spiffos` | IDENTITY_LINKED | 브랜드 가방 |

**Q1. sync 가능?** → **가능하다.** 직업 연결(DoctorBag, JanitorToolbox)과 용도 맥락(Lunchbag/box)은 item-specific 정보로 3-3 layer-fit하다. 브랜드 가방(Jays, Spiffos)도 게임 내 브랜드 정체성이므로 동일.

**Q2. 맥락 보충?** → **불필요.**

**Q3. HOLD?** → **아니다.**

**결론: `APPROVE_SYNC`** — 7건 전부

```
batch=CPR_TOOL_1L_CONTEXT | status=APPROVE_SYNC | reason=USE_CONTEXT/IDENTITY_LINKED containers; profession/brand/use context is item-specific 3-3 layer-fit | count=7 | candidate_state_change=none | review_date=2026-03-14
```

---

### Sub-batch C: Wearable.6-C (5건) — IDENTITY_LINKED

| # | fulltype | 성격 |
|---|---|---|
| 1 | `Base.Shorts_BoxingBlue` | 직업 의류 |
| 2 | `Base.Shorts_BoxingRed` | 직업 의류 |
| 3 | `Base.Trousers_Black` | 범용 의류 (IDENTITY_LINKED) |
| 4 | `Base.Trousers_Chef` | 직업 의류 |
| 5 | `Base.Trousers_Ranger` | 직업 의류 |

**Q1. sync 가능?** → **가능하다.** 직업 연결 하의류. 3-3 layer-fit.

**Q2. 맥락 보충?** → **불필요.**

**Q3. HOLD?** → **아니다.**

**결론: `APPROVE_SYNC`** — 5건 전부

```
batch=CPR_WEARABLE_6C_IDENTITY | status=APPROVE_SYNC | reason=IDENTITY_LINKED trousers/shorts; profession identity is item-specific 3-3 layer-fit | count=5 | candidate_state_change=none | review_date=2026-03-14
```

---

### Sub-batch D: Wearable.6-A (2건) — IDENTITY_LINKED

| # | fulltype | 성격 |
|---|---|---|
| 1 | `Base.Hat_FastFood_Spiffo` | 브랜드 모자 |
| 2 | `Base.Hat_Ranger` | 직업 모자 |

**Q1. sync 가능?** → **가능하다.** 브랜드/직업 모자. 3-3 layer-fit.

**Q2. 맥락 보충?** → **불필요.**

**Q3. HOLD?** → **아니다.**

**결론: `APPROVE_SYNC`** — 2건 전부

```
batch=CPR_WEARABLE_6A_IDENTITY | status=APPROVE_SYNC | reason=IDENTITY_LINKED hats; brand/profession identity is item-specific 3-3 layer-fit | count=2 | candidate_state_change=none | review_date=2026-03-14
```

---

### Sub-batch E: Consumable.3-B (1건) — USE_CONTEXT_LINKED

| # | fulltype | 성격 |
|---|---|---|
| 1 | `Base.Bleach` | 용도 맥락 소비재 |

**Q1. sync 가능?** → **가능하다.** Bleach의 용도 맥락(세정/소독)은 item-specific 사용 정보로 3-3 layer-fit하다. 시스템 획득 채널 문제가 아니라 아이템 고유의 용도 설명이다.

**Q2. 맥락 보충?** → **불필요.**

**Q3. HOLD?** → **아니다.**

**결론: `APPROVE_SYNC`** — 1건

```
batch=CPR_CONSUMABLE_3B_CONTEXT | status=APPROVE_SYNC | reason=USE_CONTEXT_LINKED; bleach use-context is item-specific 3-3 layer-fit | count=1 | candidate_state_change=none | review_date=2026-03-14
```

---

## 전체 Contextual Promote Review 요약

| Sub-batch | Bucket | 건수 | Reason | 결론 |
|---|---|---|---|---|
| A | Wearable.6-B | 24 | IDENTITY_LINKED | **APPROVE_SYNC** |
| B | Tool.1-L CPR | 7 | USE_CONTEXT/IDENTITY | **APPROVE_SYNC** |
| C | Wearable.6-C | 5 | IDENTITY_LINKED | **APPROVE_SYNC** |
| D | Wearable.6-A | 2 | IDENTITY_LINKED | **APPROVE_SYNC** |
| E | Consumable.3-B | 1 | USE_CONTEXT_LINKED | **APPROVE_SYNC** |
| **합계** | | **39** | | **전부 APPROVE_SYNC** |

### 핵심 관찰

39건 전부가 APPROVE_SYNC다. IDENTITY_LINKED와 USE_CONTEXT_LINKED는 item-specific 정보로 3-3 개별 설명층에 layer-fit하다. LAYER_COLLISION(158건)과 달리 구조적 경계 충돌이 없으므로 sync 가능하다.

---

## Candidate-state 불변 확인

- 39건 전부 candidate_state (`PROMOTE_ACTIVE`) 변경 없음
- candidate_reason_code 변경 없음
- phase3_notes 변경 없음
- approval_state만 `HOLD` → `APPROVE_SYNC`로 전환
