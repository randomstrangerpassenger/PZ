# Completion Vocabulary Separation Policy

Status: `adopted_required_gate_governance_policy`.

This policy keeps DVF 3-3 completion words axis-qualified. A standalone `complete`, `closed`, `sealed`, `PASS`, `ready`, `allowed`, `migrated`, or `current` token is not enough to prove a lifecycle claim.

Allowed claim classes:

- `broad_consumer_completion`
- `cutover_subset_completion`
- `historical_predecessor_trace`
- `phase4_live_apply_allowed`
- `pre_apply_readiness_complete`
- `problem7_full_current_route_validation_pass`
- `required_validation_gate_adopted`
- `source_overlay_repair_current_route_validation_pass`
- `terminal_disposition_complete`

Forbidden overclaim classes:

- `deployment_readiness`
- `live_migration_execution_complete_without_execution`
- `manual_qa_pass`
- `package_readiness`
- `public_text_acceptance`
- `release_readiness`
- `runtime_authority_current_without_runtime_authority_input`
- `semantic_quality_completion`
- `workshop_readiness`

Rules:

- `complete` must be bound to an owning axis and evidence root.
- `_complete` suffixes require the owning evidence closeout state to be `complete` or `canonical_complete`.
- Problem 7 current-route validation PASS is not Closeout / Reentry Guard Seal completion.
- Required-validation gate adoption is governance-only; it is not a source, rendered, Lua bridge, runtime, or package writer.
- Release, package, Workshop, deployment, manual QA, semantic quality, and public text acceptance claims are outside this policy.
