# Phase 3 Manual Cluster Analysis

## 입력 범위

- Pilot A: `Consumable.3-C`, 27 rows
- Pilot B: `Tool.1-L`, 45 rows

## 요약

- Pilot A manual rate: `0 / 27 = 0.0000`
- Pilot B manual rate: `3 / 45 = 0.0667`
- combined manual rate: `3 / 72 = 0.0417`

manual은 낮은 편이고 하나의 reason으로 수렴했다.

## top manual reason

- `LAYER_COLLISION`: 3
  - `Base.Bag_BowlingBallBag`
  - `Base.Handbag`
  - `Base.Purse`

## cluster 성격

- 세 row 모두 Phase 2 hint가 `채집으로 구할 수 있다`다.
- 이 정보는 item-specific 장소 설명보다 시스템 획득 채널 설명에 가깝다.
- 따라서 reviewer 불안보다 3-3/3-4 경계 충돌이 manual의 직접 원인이다.
- manual notes도 동일 패턴으로 수렴했고 감상문성 note 확산은 없었다.

## notes 패턴

- routine keep/promote notes 사용: 없음
- manual notes 누락: 없음
- manual notes 내용: 3-4 상호작용층과 겹치며 item-specific 장소 맥락이 부족하다는 구조 설명으로 수렴

## compose profile 상태

- Pilot A: `ACQ_ONLY_LOCATION=16`, `ACQ_ONLY_METHOD=7`
- Pilot B: `ACQ_ONLY_LOCATION=22`, `USE_PLUS_ACQ=5`, `IDENTITY_PLUS_ACQ=2`

profile은 한두 개로 붕괴하지 않았고, promote reason과 profile 조합도 자연스럽게 매핑됐다.

## 판정

- manual의 원인은 reviewer 불안이 아니라 구조적 layer collision이다.
- 현재 manual rate는 예외 큐로 유지 가능한 수준이다.
- 현 시점에서는 `phase3_policy_patch_v2.md`나 `phase3_reason_profile_patch_v2.md`를 새로 열 필요가 없다.

## 후속 관찰 포인트

- 이후 bucket에서도 `채집`, `낚시`, `채광`처럼 시스템 획득 채널 문구가 반복되면 3-4 경계 예시를 policy 부록으로 추가하는 것이 좋다.
- manual cluster가 다른 reason으로 퍼지기 시작하면 그때 patch 여부를 다시 판정한다.
