# Round 3 Taxonomy Routing Map

Generated: `2026-06-11T12:14:22+00:00`

| Contract Class | State | Routing Status | Reconciliation Treatment |
| --- | --- | --- | --- |
| current | ok | default unittest discovery after D1 | identity/count included; must pass |
| current | non_passing | default unittest discovery | current gate fails loud |
| current | non_collectable | blocked-current ledger | current gate blocked; no split |
| current | stale | blocked-current or explicit owner decision | explicit blocker/subtraction; no silent pass |
| historical | ok | explicit historical command or D3 status | identity/count included or D3 frozen treatment |
| historical | non_passing | explicit historical fail-state ledger | no reproducibility claim unless D3 allows |
| historical | non_collectable | historical blocked/non-executable status | explicit collect error or D3 frozen treatment |
| historical | stale | excluded with reason / frozen ledger | explicit subtraction |
| diagnostic | ok | explicit diagnostic command or manifest-only | identity/count included or explicit exclusion |
| diagnostic | non_passing | diagnostic fail-state ledger | counted as diagnostic failure, not current pass |
| diagnostic | non_collectable | diagnostic blocked ledger | explicit collect error |
| diagnostic | stale | excluded with reason | explicit subtraction |
