# Compose Entrypoint Guard Hardening Roadmap Packet

> Status: STAGING DRAFT
> Canonical promotion: not approved
> Date: 2026-06-13

This packet is a staging draft only. It does not modify or supersede
`docs/ROADMAP.md`.

## Completed In This Round

- Shared compose write guard moved to `build_rendered()`.
- Direct compose callers migrated to explicit `compose_context`.
- Non-current direct callers migrated away from the canonical style-log default.
- Current-equivalent output-root writes are rejected unless the target is in the
  closed protected set and current guard checks pass.
- Regression and no-mutation evidence were recorded under
  `Iris/build/description/v2/staging/compose_entrypoint_guard_hardening/`.

## Follow-Up Candidates

1. Run a separate adversarial review of the guard hardening evidence before any
   canonical governance promotion.
2. If OS permissions allow it, add optional symlink/junction alias tests for
   protected output path normalization.
3. Keep the closed protected set reviewed when new current-equivalent side
   outputs are intentionally introduced.
4. Consider a supplementary validator only if a future workflow needs static
   preflight reporting; it must remain subordinate to `build_rendered()`.

## Explicitly Not Advanced

- vNext cutover
- runtime Lua replacement
- chunk manifest or chunk payload changes
- release, Workshop, B42, or manual in-game QA readiness
- canonical `DECISIONS.md` or `ROADMAP.md` promotion
