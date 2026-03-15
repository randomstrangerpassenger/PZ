# Phase 3 Scope Contract

> Phase 3 candidate-state 평가는 Phase 2의 닫힌 획득 입력을 읽어 별도 overlay에 판단만 남기는 단계다.

---

## 1. Phase 2 입력 불변

- Phase 2의 진실 소스는 `staging/reviews/*.acquisition.jsonl`이다.
- Phase 3는 Phase 2의 `coverage_disposition`, `acquisition_hint`, `acquisition_null_reason`를 읽기만 한다.
- Phase 3 시작 이후 Phase 2의 `candidate_state`, `candidate_reason_code`, `candidate_compose_profile`는 sentinel 값(`UNSET`, `null`, `null`)을 유지한다.
- Phase 3 판단 결과는 `staging/phase3/candidate_state_phase3.review.jsonl`에만 기록한다.

## 2. 3-3 / 3-4 / 3-5 경계

- 3-3은 개별 아이템 설명층이다. 개별 이해를 실제로 늘리는 획득성만 다룬다.
- 3-4는 상호작용/시스템/목록형 층이다. 조합표, 운용 목록, 범용 상호작용은 3-3으로 올리지 않는다.
- 3-5는 canon sync와 승인층이다. `candidate_state`는 staging 판단일 뿐 canon 결정이 아니다.

## 3. Staging-First

- Phase 3의 1차 산출물은 언제나 staging overlay다.
- `PROMOTE_ACTIVE`는 “활성화 가능 후보”라는 뜻이지, compose 완료나 canon 확정이 아니다.
- sync approval은 별도 queue와 승인 정책에서 닫는다.

## 4. Fail-Loud

- snapshot hash mismatch, invalid enum, invalid state/profile 조합, SYSTEM_EXCLUDED 혼입은 FAIL이다.
- silent fallback, 자동 보정, reviewer 재해석으로 문제를 숨기지 않는다.
- 규칙으로 못 닫히면 `MANUAL_OVERRIDE_CANDIDATE`로 보낸다.

## 5. Determinism

- overlay는 동일 입력에 대해 동일 정렬, 동일 hash, 동일 summary를 만들어야 한다.
- `determinism_sha`는 normalized overlay row를 fulltype 기준 정렬한 뒤 SHA-256으로 계산한다.
- 2-run determinism 실패는 validator FAIL이다.

## 6. 표현 금지선

- recommendation, comparison, interpretation은 Phase 3 판단 근거로 허용하지 않는다.
- notes는 예외 설명용이며 routine keep/promote 설명란이 아니다.
- reviewer 감상문, 가치판단, 가이드성 문구는 금지한다.
