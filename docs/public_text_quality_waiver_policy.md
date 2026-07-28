# Public Text Quality Waiver Policy

S1 foundation에서 default waiver set은 빈 배열이다.

non-empty waiver는 exact payload binding, policy hash, metric ID, item 또는 aggregate scope, owner identity, rationale, 발행/만료 또는 재평가 조건, evidence reference, owner-binding proof를 요구한다.

waiver invariant:

```text
waived_disposition = deferred_internal_debt
raw_metric_mutated = false
technical_failure_scope = forbidden
expired_or_unbound_waiver = invalid
waiver cannot create clean accepted
```

S1은 waiver를 발행하거나 owner authorization을 대신하지 않는다.
