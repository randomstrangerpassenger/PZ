# Compose Entrypoint Guard Hardening Decisions Packet

> Status: STAGING DRAFT
> Canonical promotion: not approved
> Date: 2026-06-13

This packet is a staging draft only. It does not modify or supersede
`docs/DECISIONS.md`.

## Draft Decisions

1. `build_rendered()` is the authoritative write boundary for DVF 3-3 compose
   rendered output writes.
2. Every direct `build_rendered()` write must declare `compose_context` as one
   of `current`, `staging`, `historical`, or `diagnostic`.
3. CLI default mode may construct `compose_context=current` only when the caller
   uses default current output/style/requeue paths. Explicit output paths do not
   silently infer context.
4. Current output writes require `profile_class=v2_current`, current input
   authority paths, and a target in the closed protected current-output set.
5. Legacy, partial v2, ambiguous, and unknown compose profiles are rejected for
   current-equivalent output writes.
6. Staging, historical, and diagnostic routes remain supported only through
   explicit non-current paths and explicit context.
7. No external guard tool was introduced. Any future wrapper or validator is
   supplementary evidence and cannot replace the shared function-level guard.
8. The protected current set for this round is closed in
   `compose_protected_output_paths.json`.

## Non-Promotion Statement

This packet must not be copied into canonical decisions without a separate
post-execution adversarial review and user single-writer approval.
