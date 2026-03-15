# Phase 3 Sync Approval Policy

> 목적은 `candidate_state` 평가와 canon sync 승인 상태를 분리 저장하는 것이다.

## 1. 분리 원칙

- `candidate_state`는 Phase 3 staging 판단이다.
- `approval_state`는 canon sync 승인 상태다.
- 두 상태는 같은 row에 함께 보일 수 있지만 의미와 책임은 다르다.
- sync queue는 `PROMOTE_ACTIVE`와 `MANUAL_OVERRIDE_CANDIDATE`만 대상으로 삼는다.

## 2. approval_state enum

- `APPROVE_SYNC`: canon sync에 바로 올릴 수 있다.
- `HOLD`: sync 검토 대기다. 추가 editorial 확인이나 layer 확인이 필요하다.
- `REJECT`: candidate는 남기되 canon sync에는 반영하지 않는다.

## 3. approval_reason_code enum

- `DIRECT_ACQUISITION_READY`
  - location/method 기반 promote로 item-specific 획득 문장이 이미 닫힌 경우
- `CONTEXTUAL_PROMOTE_REVIEW`
  - use/identity/context 축 promote라서 canon voice와 layer fit을 한 번 더 봐야 하는 경우
- `MANUAL_REVIEW_REQUIRED`
  - Phase 3에서 manual cluster로 남아 sync 판단을 미룬 경우
- `SYNC_REJECTED`
  - sync queue 단계에서 canon 반영 불가로 최종 거절한 경우

## 4. 기본 매핑 규칙

- `PROMOTE_ACTIVE`
  - `LOCATION_SPECIFIC`, `METHOD_SPECIFIC`, `LOCATION_METHOD_SPECIFIC` -> `APPROVE_SYNC` + `DIRECT_ACQUISITION_READY`
  - `CONTEXT_SPECIFIC`, `USE_CONTEXT_LINKED`, `IDENTITY_LINKED` -> `HOLD` + `CONTEXTUAL_PROMOTE_REVIEW`
- `MANUAL_OVERRIDE_CANDIDATE`
  - 전부 `HOLD` + `MANUAL_REVIEW_REQUIRED`

`REJECT`는 queue review 단계의 후속 human decision에 열어 두며, pilot queue 자동 생성에서는 기본으로 쓰지 않는다.

## 5. 저장 규칙

- queue row는 Phase 3 overlay row를 참조하는 `source_overlay`를 가진다.
- `phase3_notes`는 overlay의 manual notes를 보존한다.
- `approval_notes`는 approval 단계의 판단 사유만 적는다.
- queue는 `candidate_state`를 덮어쓰지 않고 병렬 상태로 저장한다.

## 6. Pilot 적용

- Pilot A는 direct acquisition promote만 있으므로 queue 대부분이 `APPROVE_SYNC`다.
- Pilot B는 `USE_CONTEXT_LINKED`, `IDENTITY_LINKED`, `LAYER_COLLISION`이 있어 `HOLD` 군집이 생긴다.
- 이 분리가 있어야 staging 판단이 곧바로 canon sync로 미끄러지지 않는다.
