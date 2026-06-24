# DVF 3-3 Terminal Disposition Policy

Status: `machine_complete_review_pending`.

Allowed terminal dispositions are `migrated`, `no-op`, `diagnostic-only`, and `historical-only`.
`blocked`, `conditional`, `pending`, `review`, `unknown`, `deferred`, and `needs_adjudication` are transient or failure states only.

`actual_apply_eligible` and readiness sandbox mutation are not sufficient by themselves for `migrated`; terminal migrated rows require positive row-level migration evidence and actual-diff-to-ledger mapping.
Lack of migration evidence is never a positive terminal reason.

This policy preserves the sealed normalization vocabulary and adds a terminal projection layer only.
