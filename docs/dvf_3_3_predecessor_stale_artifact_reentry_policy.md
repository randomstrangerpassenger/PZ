# DVF 3-3 Predecessor / Stale Artifact Reentry Policy

Status: current additive guard policy.

Historical, diagnostic, fixture, comparison, rollback, provenance, and review-input artifacts may remain preserved. Preservation is not current authority.

Forbidden reentry surfaces:

- current source or rendered output
- runtime bridge or runtime fallback
- package staging or package zip
- export output
- current-route required-validation manifest
- raw predecessor direct execution authority
- release-readiness or package-readiness claim surface

Disposition enum source:

- `historical_trace_only`
- `diagnostic_trace_only`
- `fixture_only`
- `comparison_only`
- `rollback_snapshot_only`
- `provenance_trace_only`
- `review_input_only_non_authority`
- `package_forbidden`
- `current_authority_forbidden`
- `unknown_blocked`

The spelling `review_input_only` is intentionally not accepted.
