# Public Text Quality Denominator Contract

> 상태: G4 development-foundation successor candidate
>
> 권한 효과: none

machine-readable 기준은 tracked foundation contract의 `denominator_registry_candidate`다.

## Identity

denominator는 count가 아니라 ID와 unit, subject applicability로 식별한다. 우연히 count가 같아도 서로 다른 denominator ID를 alias하지 않는다.

current payload denominator는 total item, quality-evaluable adopted item, unadopted item, required-section opportunity, section별 opportunity, profile별 adopted item을 분리한다.

naturalization candidate denominator는 candidate item, source proposition, required body-plan role, detector별 full-candidate opportunity, required human-review row를 분리한다.

## Fail-closed rules

- missing/unknown denominator는 technical blocker다.
- applicable denominator가 0이면 0%나 PASS로 처리하지 않고 technical blocker로 처리한다.
- unadopted item을 adopted quality denominator에 넣지 않는다.
- raw detector는 configured detector별 full-candidate denominator를 완전하게 산출한다.
- human review 결과는 `naturalization_human_review_required_v1` 바깥으로 확대하지 않는다.
