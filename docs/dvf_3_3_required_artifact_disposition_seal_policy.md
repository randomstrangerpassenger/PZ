# DVF 3-3 Required Artifact Disposition Seal Policy

Status: governance-only / schema-bound.

Canonical schema: `Iris/build/description/v2/staging/dvf_3_3_required_artifact_disposition_seal/phase1_policy_schema/disposition_schema.json`

Schema sha256: `2387d882894a80625f9684349913066c05c7b426b1afebdfd7b5329c91f266ef`

Allowed axes: `dirty, ignored, untracked`.
Allowed axis dispositions: `owner_adopted_evidence_update, stale_local_mutation, regeneration_required, track_narrowly, preservation_exception_requested, manifest_removal_candidate, diagnostic_only_preserved_by_tracking, not_preservation_relevant_with_rationale, not_required_candidate, blocker`.
Allowed preservation results: `tracked_original_preservation, tracked_hash_surrogate, explicit_non_hash_exception, none`.
Allowed passability values: `passable, owner_pending, blocked, validation_failed`.

Owner decisions and owner rule ratifications must be supplied under `Iris/build/description/v2/owner_inputs/dvf_3_3_required_artifact_disposition_seal/`. Staging artifacts may validate and reference those records but cannot create or replace them.

This policy does not authorize source, rendered, Lua bridge, runtime, package, release, manual QA, semantic quality, public-facing text, owner seal, or canonical seal mutation.
