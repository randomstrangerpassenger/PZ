# Runtime Payload State Policy

Current-compatible payload shape:

* adopted rows: `text_ko` must be a non-nil string, and `publish_state` must be absent.
* unadopted rows: `text_ko` must be missing or nil, and `publish_state` must be absent.
* predecessor rollback rows with `unadopted + exposed + non_nil text_ko` are legacy residue and must not re-enter current/current-looking payload surfaces.

This policy is a payload-shape guard, not runtime visibility policy or release readiness.
