# Phase 3 Approval Hotspot Clusters

> 이 문서는 approval backlog 안에서 known hotspot cluster를 cluster 단위로 추적·검토하는 운영 문서다.
> candidate-state baseline은 유지한다. 여기서 candidate_state / reason_code / compose_profile을 재판정하지 않는다.

## 등록 원칙

- hotspot cluster의 유일한 정의 소스는 `staging/phase3/phase3_approval_hotspot_clusters.json`이다.
- 등록은 JSON에 항목을 명시 추가하는 방식으로만 한다. 자동 승격은 금지한다.
- 등록 기준(후보 식별): 한 bucket에서 manual concentration = 100%, 동일 reason, LAYER_COLLISION 계열.
- 기준을 만족해도 자동으로 cluster가 되지 않는다. 후보로 식별될 뿐이다.

---

## Cluster: `HOTSPOT_CONSUMABLE_3E_FORAGING_COLLISION`

- bucket: `Consumable.3-E`
- hotspot type: `manual_concentration_3_of_3`
- dominant reason: `LAYER_COLLISION`
- candidate-state baseline: **유지 (읽기 전용)**
- approval handling path: `HOLD → known hotspot hold → cluster batch review`

### 대상 rows

| fulltype | candidate_state | candidate_reason_code |
|---|---|---|
| `Base.Comfrey` | `MANUAL_OVERRIDE_CANDIDATE` | `LAYER_COLLISION` |
| `Base.Lemongrass` | `MANUAL_OVERRIDE_CANDIDATE` | `LAYER_COLLISION` |
| `Base.Plantain` | `MANUAL_OVERRIDE_CANDIDATE` | `LAYER_COLLISION` |

### 왜 hotspot인가

- 3건 전부 manual이다 (concentration = 100%).
- 3건 전부 동일 reason (`LAYER_COLLISION`)이다.
- 채집 가능 여부가 시스템 획득 채널 정보(3-4 상호작용층)와 겹치며, item-specific 장소 맥락이 없어 3-3 승격 규칙으로 닫기 어렵다.
- 이 패턴은 `Consumable.3-A`(109건), `Wearable.6-G`(33건) 등에서도 반복된 구조적 collision이다.

### Policy patch 여부

- 현재 시점: **NO**
- candidate-state 규칙 변경 없음. approval 운영 분리로만 처리.

### 재발 시 처리

- 같은 패턴의 새 row가 나타나면 이 cluster로 합류시킨다.
- 새 규칙 패치 트리거가 아니다.

### Cluster 상태

- cluster_status: `OPEN`

---

## Batch Review 절차

hotspot cluster에 대한 batch review는 아래 4단계로 진행한다.

### Step 1. Cluster 묶음 확인

- 대상 row 전부가 같은 hotspot cluster에 소속되어 있는지 확인한다.

### Step 2. Candidate-state 재검토 금지 확인

- `candidate_state`, `candidate_reason_code`, `candidate_compose_profile`을 재판정하지 않는다.
- approval 관점에서만 본다.

### Step 3. Approval 질문 3개만 본다

1. 이 cluster를 지금 바로 sync할 수 있는가?
2. 추가 cluster note만으로 충분한가?
3. 아니면 계속 HOLD로 남겨야 하는가?

### Step 4. Cluster 단위 결론 기록

가능한 결론은 세 가지:

- `KEEP_HOLD_CLUSTER`: HOLD 유지. 현재 단계에선 대부분 이것.
- `APPROVE_CLUSTER_SYNC`: cluster 전체를 sync 승인.
- `SPLIT_CLUSTER_FOR_REVIEW`: cluster를 분할해 개별 검토.

핵심: **매 row마다 새로 판정을 논하지 않는다.**
