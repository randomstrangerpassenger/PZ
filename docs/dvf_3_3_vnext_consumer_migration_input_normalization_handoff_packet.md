# DVF 3-3 vNext Consumer Migration Input Normalization Handoff

Use `Iris/build/description/v2/staging/dvf_3_3_vnext_consumer_migration_input_normalization/phase6/consumer_migration_reconciled_input_manifest.json`
as the only normalized downstream entrypoint.

Do not consume raw `change_required_index.md`, raw `consumer_migration_matrix.jsonl`, or dry-run output as executable migration input.

Handoff status:

* `handoff_usable`: `true`
* `handoff_usage_scope`: `downstream_tooling_readiness_input_only`
* `machine_contract_status`: `PASS`
* `governance_closeout_status`: `review_pending`

This handoff is for downstream tooling-readiness input only. It is not migration execution or cutover authorization.
