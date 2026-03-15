# Phase 3 Approval Operations Policy

> 이 문서는 Phase 3 approval backlog 운영 규칙을 정의한다.
> candidate-state baseline은 건드리지 않는다. 이 문서의 범위는 approval 운영 레이어에 한정된다.

---

## 0. 불변 원칙

| 항목 | 규칙 |
|---|---|
| `candidate_state` | **읽기 전용**. approval 처리 중 재오픈·변경·재분류 금지 |
| `phase3_notes` | **읽기 전용**. candidate-state 판정 근거 텍스트이며, approval 메모로 덮어쓰지 않음 |
| `approval_state` | **유일한 변경 대상**. sync/HOLD/REJECT만 관리 |
| approval 메모 | `cluster_note` / `hold_note` 계열로만 기록 |

candidate-state를 다시 뒤집거나 `KEEP_SILENT` 의미를 오염시키면 안 된다. Wave 3에서도 collision 의미를 보존한 채 approval backlog에서 따로 관리하는 방향으로 닫았다.

---

## 1. HOLD Queue 3층 구조

HOLD queue는 3개 tier로 분류한다.

### Tier 1: Known Batch Review Hold

- 이미 식별된 대량 collision 군.
- 예: `Wearable.6-G` pure-foraging accessory 33건.
- 정의 소스: `build_phase3_hold_queue.py` 내 `KNOWN_BATCH_REVIEW_RULES`.

### Tier 2: Known Hotspot Hold

- 규모는 작지만 특정 bucket에서 manual concentration이 100%로 뜨는 군.
- 예: `Consumable.3-E` 3/3.
- 정의 소스: `staging/phase3/phase3_approval_hotspot_clusters.json` (단일 진실 소스).

### Tier 3: General Hold

- 그 외 일반 manual/contextual 보류군.

### 3층 분리의 이점

- 33건짜리 대량 backlog와 3건짜리 hotspot을 같은 통에서 섞지 않는다.
- warning을 "존재는 알지만 아무 구조도 없는 상태"로 방치하지 않는다.
- approval backlog 보고서에서 각 군이 왜 따로 보이는지 설명 가능하다.

---

## 2. Cluster Note 템플릿

candidate-state 판정 근거(`phase3_notes`)와 approval backlog 운영 메모는 분리한다.

| 레이어 | 필드 | 용도 | 쓰기 권한 |
|---|---|---|---|
| candidate-state | `phase3_notes` | 판정 근거 텍스트 | baseline, 읽기 전용 |
| approval backlog | `cluster_note` | cluster 등록 사유 | hotspot tier 전용 |
| approval backlog | `hold_note` | 개별 HOLD row 운영 메모 | 모든 HOLD row |

### Hotspot용 cluster note 템플릿

```
cluster=HOTSPOT_CONSUMABLE_3E_FORAGING_COLLISION | status=known_hotspot_hold | reason=manual concentration; repeated 3-3 vs 3-4 collision | candidate_state_change=none | next_action=batch review with cluster
```

이 템플릿의 목적은 문장을 예쁘게 만드는 게 아니다. 나중에 왜 HOLD였는지 한 줄로 바로 읽히게 만드는 것이다.

---

## 3. Cluster Status Enum

cluster의 생애주기를 추적하는 상태 enum이다.

| 상태 | 의미 |
|---|---|
| `OPEN` | 미검토 |
| `IN_REVIEW` | 검토 진행 중 |
| `KEEP_HOLD` | 검토 완료, 정책적 HOLD 유지 결정. cluster는 닫혔으나 sync하지 않음 |
| `APPROVED_SYNC` | 검토 완료, sync 승인 |
| `SPLIT_FOR_REVIEW` | cluster 분할 후 개별 검토 필요 |
| `WONT_SYNC` | 검토 완료, sync 영구 불가 판정 |

`KEEP_HOLD_CLUSTER` 결론 시 `cluster_status`는 `KEEP_HOLD`로 전이한다. `RESOLVED`는 사용하지 않는다 — "이미 해결된 클러스터"로 오인되어 backlog 추적성이 깨지기 때문이다.

---

## 4. Batch Review 절차

hotspot cluster에 대한 batch review는 `phase3_approval_hotspot_clusters.md`에 정의된 4단계를 따른다.

1. Cluster 묶음 확인
2. Candidate-state 재검토 금지 확인
3. Approval 질문 3개 (sync 가능 / note 충분 / HOLD 유지)
4. Cluster 단위 결론 기록 (`KEEP_HOLD_CLUSTER` / `APPROVE_CLUSTER_SYNC` / `SPLIT_CLUSTER_FOR_REVIEW`)

---

## 5. Hotspot 등록 기준

아래 조건을 모두 만족하면 hotspot cluster 등록 **후보**로 식별한다.

- 한 bucket에서 manual concentration = 100%
- row 수가 작아도 모두 동일 reason
- reason이 `LAYER_COLLISION` 계열
- candidate-state baseline은 문제없음

### 등록 방식

- **명시 등록만 허용한다.** 자동 승격은 금지한다.
- 후보를 식별한 뒤 `phase3_approval_hotspot_clusters.json`에 항목을 명시 추가하는 것으로 등록한다.
- 코드에 개별 hotspot 값을 하드코딩하지 않는다.

`Consumable.3-E`는 일회성 예외가 아니라, 앞으로 같은 패턴을 분류하는 기준 사례가 된다.

---

## 6. Contextual Promote vs Manual Review 분리 원칙

`CONTEXTUAL_PROMOTE_REVIEW` 39건과 `MANUAL_REVIEW_REQUIRED` 158건은 **분리 처리**한다.

| 구분 | 대상 | 성격 | Review 질문 |
|---|---|---|---|
| Manual | LAYER_COLLISION 중심 158건 | 구조적 충돌 | sync 가능? / HOLD 유지? / split? |
| Contextual | IDENTITY/USE_CONTEXT 승격 39건 | 문맥 적합성 검토 | approval note로 sync 가능? / 맥락 보충 필요? / HOLD? |

이 둘을 섞으면 collision 처리와 문맥 검토가 뒤엉킨다.

---

## 7. General Hold 소배치 Review 절차

general hold 내 대량 동일 패턴은 다음 순서로 grouping한다.

1. 같은 `approval_reason`
2. 같은 `candidate_reason_code`
3. 같은 bucket
4. 같은 `cluster_note` 패턴
5. 같은 `hold_note` 패턴

배치 단위는 10~20 row를 권장하고, collision-heavy와 contextual promote는 섞지 않는다. 검토 결과 cluster 승격 조건을 충족하면 known batch review cluster로 등록할 수 있다.

---

## 8. Approval-Hotspot Gate

### PASS 조건

- hotspot warning bucket이 cluster로 등록됨
- 관련 HOLD rows 전부 cluster_id를 가짐
- general hold에 방치된 동일 패턴 row가 없음
- candidate-state 값 변경 없음

### FAIL 조건

- hotspot warning이 문장으로만 있고 backlog 객체가 없음
- cluster 등록 없이 general hold에 섞여 있음
- hotspot 처리 과정에서 candidate-state가 바뀜

---

## 9. Closeout 기준

### sync-ready complete = YES 필수 조건 (5개 전부 충족)

1. sync 가능 subset 전량 승인 (`APPROVE_SYNC` 대상 확정)
2. 잔존 HOLD는 전부 정책적 `KEEP_HOLD` cluster에 소속
3. 모든 known cluster `cluster_status ∈ {KEEP_HOLD, APPROVED_SYNC, WONT_SYNC}`로 전이 완료
4. contextual promote 39건 전부 처리 완료
5. candidate-state SHA 불변

### 불허 조건

- `OPEN` 또는 `IN_REVIEW` cluster 잔존 → 불가
- 미소속 general hold row 잔존 → 불가
- approval 결론 없이 backlog에만 남은 row → 불가

목표는 "warning을 없애는 것"이 아니다. **warning을 통제 가능한 운영 객체로 바꾸는 것**이다.
