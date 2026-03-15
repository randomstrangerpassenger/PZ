# Phase 3 Gate Spec

> reviewer의 감이 아니라 validator와 gate가 결정을 지배하도록 하는 봉인 문서다.

---

## 1. 기본 경로

- overlay: `staging/phase3/candidate_state_phase3.review.jsonl`
- summary: `staging/phase3/phase3_candidate_state_summary.json`
- by_bucket: `staging/phase3/phase3_candidate_state_by_bucket.json`
- gaps: `staging/phase3/phase3_candidate_state_gaps.json`

## 2. validator가 강제하는 것

- candidate_state / reason_code / compose_profile enum
- state ↔ reason_code ↔ compose_profile 조합
- manual notes 의무
- keep/promote notes 금지
- phase2 snapshot hash 일치
- SYSTEM_EXCLUDED, UNREVIEWED 혼입 차단
- phase2 candidate 필드 오염 차단
- summary/by_bucket/gaps 재계산 일치
- compare overlay 기반 2-run determinism

## 3. FAIL

- invalid enum
- invalid combo
- missing reason_code
- promote without profile
- manual without notes
- snapshot mismatch
- determinism mismatch
- system_excluded contamination
- state 누락 row
- phase2 overlay contamination

## 4. WARN

- manual 비율 과다
- 특정 reason_code 편중
- 특정 버킷 manual 집중

## 5. 실행 규칙

- pilot 검증: `validate_phase3_candidate_state.py`
- full rollout 검증: `validate_phase3_candidate_state.py --require-complete`
- 2-run determinism: `validate_phase3_candidate_state.py --compare-overlay <second-run-overlay>`

validator가 FAIL이면 reviewer 판단은 채택하지 않는다.
