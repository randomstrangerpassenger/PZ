# DVF 3-3 Core / Registry Boundary Claim Contract

Status: governance-only claim meaning authority.

This document is the single claim meaning authority for the DVF Core, Iris Artifact Registry, Registry Runtime Compatibility, Publish Boundary, and Legacy Combined Current Route claim classes. Derivative boundary docs, ledger packets, final reports, and top-doc drafts must cite this document hash instead of redefining claim meanings.

## Claim Classes

### DVF Core PASS

Owner axis: `dvf_core_body_compiler`.

Allowed meaning:
- body compiler determinism
- facts / decisions / profile / body_plan consumption
- rendered 3-3 body shape inside DVF Core scope
- protected-output no-mutation inside the body compiler scope

Forbidden meaning:
- Registry Authority PASS
- Registry Runtime Compatibility PASS
- Publish Boundary PASS
- package safety
- release readiness
- public text acceptance
- runtime compatibility closure

### Registry Authority PASS

Owner axis: `registry_authority`.

Allowed meaning:
- artifact authority classification
- identity and role classification
- staging evidence and required-validation consumption boundary
- stale artifact and predecessor reentry guard

Forbidden meaning:
- runtime consumer compatibility
- public text acceptance
- release readiness
- package readiness

### Registry Runtime Compatibility PASS

Owner axis: `registry_runtime_compatibility`.

Allowed meaning:
- runtime consumer compatibility with the current Registry artifact shape
- no source authority mutation

Forbidden meaning:
- source mutation authority
- rendered text quality acceptance
- public text acceptance
- Registry Authority PASS

### Publish Boundary PASS

Owner axis: `publish_boundary`.

Allowed meaning:
- conjunctive closure over public text acceptance
- semantic quality acceptance
- package publication readiness
- release / Workshop readiness
- manual QA components

Forbidden meaning:
- compiler success alone
- Registry success alone
- any partial component success expressed as bare Publish Boundary PASS

### Legacy Combined Current Route PASS

Owner axis: `legacy_combined_governance_route`.

Allowed meaning:
- legacy combined governance route container passes at a readpoint
- current_route_required_validations remains legacy combined governance route

Forbidden meaning:
- DVF Core PASS
- Registry Authority PASS
- Registry Runtime Compatibility PASS
- Publish Boundary PASS

## DVF PASS Disposition

Standalone current `DVF PASS` is forbidden in this closure.

Allowed `dvf_pass_disposition` enum:

- `forbidden_standalone_current_claim`
- `legacy_alias_only`
- `blocked_owner_decision_pending`

`forbidden_standalone_current_claim` is the default non-blocking disposition and does not require an owner input record. `legacy_alias_only` requires a hash-bound owner record and still keeps `dvf_pass_standalone_current_claim_allowed=false`.

## Publish Boundary Rule

`publish_boundary_pass_composition=conjunctive_all_components`. Bare `Publish Boundary PASS` is allowed only when public text acceptance, semantic quality acceptance, package publication readiness, release / Workshop readiness, and manual QA components are all separately validated inside a Publish Boundary closure. Partial component success must use sub-qualified tokens and is forbidden as bare `Publish Boundary PASS`.

## Non-Claims

This contract does not claim Registry Authority completion, Registry Runtime Compatibility completion, Publish Boundary completion, runtime deployability, package readiness, release readiness, Workshop readiness, B42 readiness, deployment readiness, manual QA, semantic quality acceptance, public-facing text acceptance, source mutation, rendered mutation, Lua bridge mutation, runtime chunk mutation, or package payload mutation.

Staged mirror of `docs/dvf_3_3_core_registry_boundary_claim_contract.md` / sha256 `fb693a4b5ec1bebb7b99a59648b4c48c7d229143226d1c0b34b364b56a523001`.
