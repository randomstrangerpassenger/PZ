# DVF 3-3 Completion Vocabulary External Gate Split Policy

Status: current DVF 3-3 governance vocabulary split policy / governance-only.

This policy is a subordinate addendum to `docs/completion_vocabulary_separation_policy.md`.

Allowed `PASS` fields:

- `machine_contract_validation=PASS|FAIL`
- `external_validation_bundle_result=PASS|FAIL|null`
- `independent_review_verdict=PASS|FAIL|PASS_WITH_NOTES|null`

Forbidden bare `PASS` fields:

- `owner_decision=approved|rejected|pending`
- `owner_seal_state=sealed|pending|blocked`
- `external_gate_state=satisfied|blocked|pending`
- `canonical_external_review_state`: `satisfied` or `blocked`

`PASS_WITH_NOTES` belongs only to independent review verdicts. Blocking notes, missing note severity, or free-text-only notes keep the external gate blocked or pending.

Owner decision and owner seal are owner-supplied governance records. They do not replace independent review or external validation bundle evidence.

Machine validation, owner approval, and external validation bundle result cannot satisfy the canonical external review axis without a genuine independent review artifact whose scope, identity, independence, reviewed result, timestamp, and hash bundle are present.
