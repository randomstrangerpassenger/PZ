# DVF 3-3 Core / Registry Boundary Required Gate Adoption Contract

Status: governance-only required-validation adoption contract.

Claim meanings remain owned by `docs/dvf_3_3_core_registry_boundary_claim_contract.md`. This document only defines which stable machine fields the live current route consumes.

Manifest-required fields are hosted before the first post-adoption current route. Route-result fields, independent review fields, owner seal fields, canonical seal fields, and final no-mutation summary fields are not manifest-required predicates.

Required adoption fields:
- `required_gate_adopted=true`
- `future_current_route_blocking_claimed=true` only after live re-scan is consumed by both current-route passes
- `legacy_combined_route_pass_is_dvf_core_pass=false`
- `dvf_pass_standalone_current_claim_allowed=false`
- `required_manifest_adoption_mode=additive_only`
- `removed_required_artifact_count=0`
- `removed_required_test_count=0`
- `predicate_meaning_change_count=0`
- `existing_entry_reclassified_count=0`

Non-claims: this adoption does not claim Registry Authority PASS, Registry Runtime Compatibility PASS, Publish Boundary PASS, runtime compatibility closure, public text acceptance, package readiness, release readiness, Workshop readiness, B42 readiness, deployment readiness, manual QA, source mutation, rendered mutation, Lua bridge mutation, runtime chunk mutation, or package payload mutation.
