# Shared Disposition Consumption Contract

Status: `candidate_review_pass_owner_adoption_pending`.

Consumers read terminal disposition, denominator identity, lifecycle role, and provenance role through `shared_disposition_packet.json` or a report-consumption route that is pinned to that packet.

The packet does not recalculate terminal disposition, does not recompute denominator values, and does not promote raw audit, readiness sandbox, dry-run, diagnostic, or historical artifacts to current execution authority.

Required row fields: `row_identity`, `terminal_disposition`, `denominator_axis`, `lifecycle_role`, `source_artifact_role`, `provenance_reference`, `readiness_reference`, `sealed_value_source`, and `artifact_hash`.

Forbidden substitutions: `2105`, `2084`, and `21` are historical/runtime comparison values only; `311`, `163`, `153`, `109`, and `44` keep separate axes and lifecycle roles.
