# Negative Case Matrix

| Case | Guard | Expected |
| --- | --- | --- |
| `invalid_disposition_enum` | `disposition_coverage` | fail-loud |
| `rejected_runtime_eligible` | `unapproved_delta` | fail-loud |
| `missing_reviewer_identity` | `disposition_coverage` | fail-loud |
| `publish_state_classified` | `legacy_vocabulary` | fail-loud |
| `monolith_current_path` | `monolith_re_entry` | fail-loud |
| `staging_direct_promotion` | `staging_direct_promotion` | fail-loud |
| `rejected_in_cutover_input` | `unapproved_delta` | fail-loud |
| `dual_current_authority` | `single_authority` | fail-loud |
