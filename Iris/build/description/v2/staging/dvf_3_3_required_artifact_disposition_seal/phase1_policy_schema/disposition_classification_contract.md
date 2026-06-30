# Required Artifact Disposition Classification Contract

Status: `schema_bound`.

The canonical enum source is `phase1_policy_schema/disposition_schema.json` with sha256 `2387d882894a80625f9684349913066c05c7b426b1afebdfd7b5329c91f266ef`.

Each active row must keep `axis`, `axis_disposition`, `preservation_result`, and `passability` separate. `tracked_hash_surrogate` and `explicit_non_hash_exception` are preservation results, not axis dispositions.

Automatic tracked negative-exception preservation is passable only when an owner-supplied rule ratification record validates. Without that record, matching rows remain `owner_pending`.
