# Iris DVF 3-3 Diagnostic-only Resolver Compatibility Guard Round Scope Lock

> 상태: closed scope lock  
> 기준일: 2026-05-17  
> closeout label: `closed_with_diagnostic_only_resolver_guard`

## Authority Read Order

1. `docs/Philosophy.md`
2. `docs/DECISIONS.md`
3. `docs/ARCHITECTURE.md`
4. `docs/ROADMAP.md`
5. `docs/Iris/iris-dvf-3-3-diagnostic-only-resolver-compatibility-guard-round-plan.md`

## Locked Statements

- `selected_role` is native resolver authority.
- `selected_role_precedence` and `selected_role_target` are native resolver trace / authority observation.
- selected-role influence `0` is not a success criterion.
- complete-removal is out of scope.
- frozen 2105 byte-level recovery is not a blocker for this diagnostic-only guard round.
- adapter removal is out of scope.
- legacy compatibility mapping must not act as silent default authority.

## Implemented Boundary

Default resolver mode now fails loud with `DEFAULT_RESOLVER_REJECTED_LEGACY_COMPAT_LABEL` if native v2 authority cannot resolve a row and the remaining fallback source is a legacy compatibility label such as `interaction_tool`, `interaction_component`, or `interaction_output`.

Explicit diagnostic resolver mode is available only through `--mode diagnostic_resolver` or `resolver_authority_mode='diagnostic'`, and CLI diagnostic writes are constrained to the diagnostic staging root.

## Non-Claims

This scope lock does not declare selected-role removal, complete-removal cleanup, adapter removal, runtime Lua regeneration, manual in-game QA, deployed closeout, Workshop release, or `ready_for_release`.
