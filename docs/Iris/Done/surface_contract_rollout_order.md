# Surface Contract Rollout Order

> 상태: draft v0.2  
> 기준일: 2026-04-29  
> scope: `surface contract authority migration`

---

## Rollout 1

- 대상:
  - `IDENTITY_ONLY`
  - explicit `BODY_LACKS_ITEM_SPECIFIC_USE`
  - existing `identity_fallback` internal-only lane 유지
- current 결과:
  - publish split 변화 없음
  - `BODY_LACKS_ITEM_SPECIFIC_USE 617`은 기존 `identity_fallback` lane 안에서 authority만 명문화됨

## Rollout 2

- 대상:
  - unresolved `FUNCTION_NARROW`
- gate:
  - 2026-04-29 `FUNCTION_NARROW Disposition Closure and Publish Writer Authority Seal Round`에서 disposition closure 완료
- current 상태:
  - closeout state: `closed_with_publish_writer_authority_sealed_delta_0`
  - residual `FUNCTION_NARROW 7`은 preview/report structural flag로만 남음
  - publish restore decision count `0`
  - applied publish/quality/runtime delta `0`
  - blanket isolation forbidden

## Rollout 3

- 대상:
  - residual `ACQ_DOMINANT`
- gate:
  - source expansion 재측정
  - future separate decision 완료
- current 상태:
  - blanket isolation 금지
  - residual remeasurement는 source expansion 이후 별도 scoped round로 유지
  - rollout hold

## 금지 해석

- style advisory 경고를 rollout lane으로 직접 승격하지 않는다.
- `FUNCTION_NARROW`와 `ACQ_DOMINANT`를 blanket isolation으로 다루지 않는다.
- previous-round manual pass를 이번 round rollout complete로 오독하지 않는다.

## 2026-04-29 Round A closeout note

- Publish writer authority는 semantic quality strength가 아니라 layer/position correctness다.
- `FUNCTION_NARROW` / `ACQ_DOMINANT` blanket isolation은 forbidden이다.
- `FUNCTION_NARROW` clean branch는 delta 0으로 닫혔다.
- `ACQ_DOMINANT` residual remeasurement는 source expansion 이후 별도 scoped round로만 열린다.
