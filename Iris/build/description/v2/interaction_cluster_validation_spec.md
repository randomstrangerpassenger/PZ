# Interaction Cluster Validation Spec

> 목적: interaction cluster 연계가 reviewer 감이 아니라 validator와 gate에 의해 통제되도록 한다.

---

## 1. smoke test

### 1차 smoke test

- 시점: A-4-1 종료 시점
- 목적: cluster 정의를 다음 단계로 넘길 수 있는지 판단
- 통과 조건:
  - `assignment_rate >= 0.80`
  - 랜덤 샘플 50건 중 `cluster_misaligned <= 10%`
  - 랜덤 샘플 50건 중 `too_generic_use <= 10%`

세 조건 중 하나라도 실패하면 A-4-1을 재작업한다.

### 최종 smoke test

- 시점: G1 Spec Freeze 직전
- 목적: A-4-2~A-4-4 수정 반영 후 freeze 가능 여부 판단
- 통과 조건:
  - `assignment_rate >= 0.80`
  - 랜덤 샘플 50건 중 `cluster_misaligned <= 10%`
  - 랜덤 샘플 50건 중 `too_generic_use <= 10%`

## 2. HARD FAIL 코드

- `too_generic_use`
- `cluster_misaligned`
- `borrowed_list_structure`
- `role_fallback_too_hollow`

HARD FAIL이 발생한 row는 자동 승인하지 않는다.

## 3. SOFT GATE

### V8

- 정의: 범용 fallback 비율 `< 5%`
- 성격: soft ceiling
- 초과 시 요구 사항:
  - 이유 분해 보고
  - bucket별 집중 구간 보고
  - rework 또는 manual 보강 범위 명시

## 4. WARN

### V9

- 정의: 맥락어 자동 검사
- 성격: WARN only
- 처리:
  - V9는 PASS/FAIL을 만들지 않는다
  - V9 WARN row는 수동 검토 우선순위 버킷으로 자동 배정한다
  - 어휘 목록은 pilot 동안 보수적으로 운영하고 확장한다

## 5. 게이트 연계

| Gate | 조건 |
|---|---|
| G1 Spec Freeze | 최종 smoke test 3중 조건 통과 |
| G3 Data Ready | V8 soft ceiling 확인, 초과 시 사유 분해 보고 |
| G5 Scale Pass | HARD FAIL 0, V9 WARN triage 경로 기록 완료 |

## 6. 산출물

validator/report 계열은 최소 아래 결과를 남겨야 한다.

- `assignment_rate`
- `cluster_misaligned_rate_sample`
- `too_generic_use_rate_sample`
- `generic_fallback_ratio`
- `v9_warn_rows`
- `tie_break_rows`
