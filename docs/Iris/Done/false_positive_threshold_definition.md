# False Positive Threshold Definition

> 상태: draft v0.1  
> 기준일: 2026-04-08  
> scope: `surface contract authority migration` 1차 rollout

---

## 1. 기준

- 1차 rollout 허용 false positive rate: `0`
- 의미:
  - 수동 검수 표본 안에서 오판이 하나라도 확인되면 freeze를 보류한다.

## 2. 표본 선정 규칙

- 대상 row가 `50` 이하이면 전수 검수한다.
- `50` 초과이면 `max(50, 전체의 20%)`를 검수 표본으로 뽑는다.
- 표본은 아래 축으로 층화한다.
  - `violation_type`
  - source lane
  - 경계 사례

## 3. 현재 round 해석

- `2026-04-08` dry-run 결과는 `exposed -> internal_only` 신규 이동이 `0`건이다.
- 따라서 이번 round의 false positive 검수 상태는 `not_applicable_no_newly_isolated_rows`로 기록한다.
- 이는 threshold 완화가 아니라, **신규 격리 대상이 없어 수동 오판 검수를 열 표본이 없었다**는 뜻이다.

## 4. threshold 초과 시 처리

- structural audit 규칙 재조정
- rollout 중단
- baseline freeze 보류

## 5. 금지 해석

- warning 수 감소를 false positive 개선으로 읽지 않는다.
- style advisory 경고를 false positive denominator에 섞지 않는다.
- previous-round manual pass를 이번 round false positive 검수 완료로 재표기하지 않는다.
