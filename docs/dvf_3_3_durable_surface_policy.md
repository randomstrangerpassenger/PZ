# DVF 3-3 Durable Surface Policy

Status: current durable preservation policy / governance-only.

Durable status means preservation requirement, not authority promotion.

Durable classes:

- current_source_authority_chain
- live_required_validation_manifest
- current_route_governance_surface
- essential_guard_and_regeneration_tooling
- deployable_runtime_chunk_authority
- required_adopted_evidence

Non-durable default classes:

- generated_staging_evidence
- sandbox_output
- candidate_manifest
- raw_audit_artifact
- readiness_or_dry_run_byproduct
- diagnostic_only_artifact
- historical_reproduction_artifact
- quarantine_copy
- round_local_scratch_artifact
- package_or_release_intermediate

Rules:

- Each artifact has one primary durable role.
- `dvf_3_3_input_manifest.json` is `current_source_authority_chain`; `current_regeneration_manifest` is only an attribute.
- Runtime chunk authority is derived from `IrisLayer3DataChunks.lua`; the current chunk count is a readpoint result.
- Required artifacts in the live current-route manifest are tracked because the manifest adopted them, not because their staging root is authority.
- `tracked_status_is_not_authority_status`.
- `ignored_status_is_not_deletable_status`.
- `required_artifact_adoption_is_governance_only`.
- `staging_evidence_root_is_not_current_authority`.
- `durable_surface_is_preservation_scope_not_writer_scope`.
- `required_gate_is_not_writer`.
- `complete_is_axis_qualified_not_release_readiness`.
- The staging evidence root is not current authority.
