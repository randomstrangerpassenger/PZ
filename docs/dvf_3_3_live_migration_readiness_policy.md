# DVF 3-3 Live Migration Readiness Policy

Status: implemented execution evidence policy.

This policy covers only the pre-apply readiness gate for the terminal `migrated=153`
projection. It does not authorize live migration execution, current authority cutover,
runtime chunk replacement, source/rendered/package mutation, required-validation manifest
adoption, release readiness, Workshop readiness, B42 readiness, deployment readiness, or
manual in-game QA.

Rows are classified into exactly one live-readiness disposition:

* `live_mutation_eligible`: a consumer-only target can be represented by the sealed dry-run
  patch bundle.
* `evidence_only`: positive evidence exists but no live writer target is opened in this
  readiness round.
* `blocked`: the row or a global gate is not safe to authorize.

Partial authorization is not allowed. Any blocked row keeps `phase4_live_apply_allowed=false`.
