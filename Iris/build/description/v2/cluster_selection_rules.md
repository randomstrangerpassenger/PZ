# Cluster Selection Rules

> 목적: 다중 소속 아이템에서 대표 interaction cluster를 결정론적으로 선택한다.

---

## 1. 입력

선택기는 각 아이템에 대해 아래 정보를 받는다고 가정한다.

- `candidate_clusters`
- `cluster_frequency`
- `cluster_unique_item_count`
- `candidate_roles`
- `direct_use_present`
- `manual_override_flag`

## 2. 선택 순서

대표 cluster 선택 순서는 아래와 같다.

1. 전용 우선
2. 빈도 우선
3. 특수성 우선
4. 수동 override

## 3. 전용 우선

- 아이템이 사실상 한 작업군에만 자연스럽게 귀속되면 그 cluster를 우선 선택한다.
- 전용 판단은 `candidate_clusters`의 의미적 좁힘이 아니라, 4계층 evidence가 가리키는 대표 interaction context의 집중도로 본다.

## 4. 빈도 우선

- 전용 cluster가 없으면, 4계층 evidence에서 가장 자주 나타난 cluster를 우선 선택한다.
- 빈도는 `cluster_frequency`로 계산한다.

## 5. 특수성 우선

- 빈도가 동률이면 더 좁은 cluster를 선택한다.
- 조작적 정의: `cluster_unique_item_count`가 더 작은 쪽이 더 좁다.
- 즉, 해당 cluster에 속한 고유 아이템 수가 적을수록 더 특수한 cluster다.

## 6. role tie-breaker

- 빈도와 특수성까지 동률이면 `tool -> material -> output` 순서를 사용한다.
- 이 규칙은 **provisional tie-breaker**다.
- tie-breaker가 적용된 row는 `tie_break_applied = true`로 기록한다.
- tie-breaker 적용 row는 Phase C pilot에서 별도 추적하고, pilot 후 freeze 또는 수정 판정을 내린다.

## 7. 수동 override

- 아래 경우에만 manual override를 허용한다.
- 계산 결과가 여러 cluster에 대해 끝까지 동률인 경우
- selection 결과가 `cluster_misaligned`로 반복 검출되는 경우
- evidence 결손 때문에 전용/빈도/특수성 판단이 불가능한 경우

애매하다는 이유만으로 override에 떨어뜨리는 것은 금지다.

## 8. 출력 필드

선택 결과는 최소 아래 필드를 남긴다.

- `selected_cluster`
- `selection_path`
- `selected_role`
- `tie_break_applied`
- `manual_override_required`

## 9. 비목표

- approval backlog의 hotspot cluster와 동일한 운영 객체로 취급하는 것
- tie-breaker를 현재 단계에서 영구 규칙으로 확정하는 것
