# Phase 3 Kickoff Checklist

> Pilot 착수 전 고정해야 하는 전제만 짧게 확인한다.

## 착수 체크

- [x] Phase 2 acquisition review는 immutable input으로 취급한다.
- [x] Phase 3 판단은 Phase 2 파일을 수정하지 않고 별도 overlay에만 기록한다.
- [x] `candidate_state`는 staging 판단이며 canon sync 승인과 동일하지 않다.
- [x] 3-3 candidate-state 평가는 3-4 상호작용층을 대체하지 않는다.
- [x] Phase 2 review row의 `candidate_state`, `candidate_reason_code`, `candidate_compose_profile`는 sentinel 값(`UNSET`, `null`, `null`)을 유지한다.
- [x] 이번 배치의 persisted Phase 3 산출물은 `staging/phase3/` 아래에만 기록한다.

## 종료 기준

- [x] 이번 배치에서 Phase 2 파일 수정 금지 원칙을 재확인했다.
- [x] `candidate_state`와 canon sync approval은 분리된 후속 단계라는 점을 재확인했다.
