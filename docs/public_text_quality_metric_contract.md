# Public Text Quality Metric Contract

> 상태: S1 development-foundation candidate
>
> 권한 효과: none
>
> 공식 disposition: not issued

이 문서는 Iris Publish Boundary의 public-text acceptance metric 의미를 candidate 결과와 무관하게 고정한다. machine-readable 기준은 tracked `public_text_quality_foundation_contract.json`의 `metric_registry_candidate`다. 이 S1 문서와 계약은 공식 policy ratification, evaluation-subject disposition, live gate adoption 또는 policy closure가 아니다.

## 공통 규칙

- `disposition_class`는 `blocking_gate | advisory_debt | non_claim`만 허용한다.
- 모든 metric은 하나 이상의 `applicable_subject_kinds`를 명시한다.
- 다른 subject kind의 metric을 0이나 PASS로 합성하지 않는다.
- raw metric은 immutable하며 exception과 waiver가 raw numerator를 바꾸지 않는다.
- unknown metric, unknown profile, unknown denominator, zero denominator는 technical blocker다.
- row cardinality와 occurrence cardinality는 서로 다른 unit이다.
- aggregate ratio는 per-profile/per-section 전수 breakdown을 대체하지 않는다.
- overlapping metric을 합산한 hidden master score를 만들지 않는다.

## Current runtime payload

`coverage_quality_weak`, `coverage_quality_adequate`, `coverage_quality_strong`은 quality-evaluable adopted item을 정확히 한 번 partition한다. `unadopted`는 quality denominator에서 제외하고 separate adoption axis로 유지한다.

`missing_any_required_section_row`는 missing section이 하나 이상인 unique adopted row 수다. `missing_required_section_occurrence`는 모든 missing section occurrence 합이다. occurrence metric은 row blocker와 별도의 중복 blocker가 아니다.

## Naturalization candidate

semantic preservation, required body-plan role satisfaction, equivalence proof, compiler-invalid pattern, raw Korean prose detector, required-denominator human review를 별도 metric으로 유지한다.

required structural role는 `emitted_direct | satisfied_by_verified_fusion | satisfied_by_verified_suppression`일 때만 satisfied다. required role에 `not_required`를 사용할 수 없고, fusion/suppression은 typed equivalence proof가 유효해야 한다.

human-only finding은 sealed selection contract가 만든 required review denominator 안에서만 주장한다. 전수 review가 아니면 corpus-wide human-only blocker 0을 주장하지 않는다.
