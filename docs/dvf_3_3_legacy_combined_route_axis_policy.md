# DVF 3-3 Legacy Combined Route Axis Policy

Status: governance-only routing preflight policy.

Freeze:

```text
current_route_required_validations.json = legacy_combined_governance_route != DVF Core PASS authority
```

The current combined governance route remains preserved. A route-level PASS is not DVF Core PASS authority.

## Axis Enum

* `dvf_core_body_compiler` - body compiler, compose, and DVF body production surfaces.
* `registry_authority` - source, decision, current authority, successor readpoint, and registry authority surfaces.
* `registry_runtime_compatibility` - runtime payload shape and consumer compatibility surfaces.
* `publish_boundary` - bridge export, package, publish, and release-boundary guard surfaces.
* `legacy_combined_governance_route` - runner container, manifest container, taxonomy/required-validation governance chain, current route PASS claim surface, and combined-route claim-boundary scaffolding.
* `historical_predecessor_trace` - predecessor, stale artifact, historical preservation, and reentry-prevention surfaces.
* `diagnostic_or_fixture` - diagnostic, negative fixture, and fail-closed test-only surfaces.

## Core Rules

```text
routed-through legacy combined route
!=
responsibility-of legacy combined governance route
```

Each item has exactly one `primary_axis`. `unknown`, `todo`, `tbd`, and `unclear` are blockers, not classifications.

Lifecycle disposition is metadata only. It does not replace the responsibility axis.

`legacy_combined_governance_route` is limited to route scaffolding, manifest/taxonomy containers, required-validation governance chain surfaces, combined-route closeout coordination, and explicit claim-boundary surfaces. Any required test or artifact assigned to this axis must include `route_container_or_claim_surface_reason_code`.

## Non-Claims

This policy does not claim DVF Core PASS, Registry Authority PASS, Registry Runtime Compatibility PASS, package readiness, release readiness, Workshop readiness, B42 readiness, deployment readiness, public text quality acceptance, runtime mutation, bridge export mutation, source mutation, rendered mutation, package mutation, independent review, owner seal, or canonical seal.
