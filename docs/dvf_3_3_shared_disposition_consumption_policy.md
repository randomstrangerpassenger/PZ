# DVF 3-3 Shared Disposition Consumption Policy

Status: `complete_adopted`.

This policy binds downstream `manifest / tools / docs / tests / validators` consumption to the shared disposition packet produced under `Iris/build/description/v2/staging/dvf_3_3_shared_disposition_ledger_consumption/`.

Allowed claim: relevant downstream surfaces consume a shared contract or report-mediated route for terminal disposition, denominator axis, lifecycle role, and provenance role.

Blocked claims:

- `153 migrated` is not live migration completion.
- `109 live_mutation_eligible` is not proof that rows were already applied by this round.
- `163 sandbox mutation` is readiness or sandbox evidence, not live mutation evidence.
- `311 change-required` is not the terminal completion denominator.
- `1062 executing consumers` are member rows, not source entries.
- raw audit ledger, readiness execution artifacts, dry-run output, historical rows, and diagnostic rows are not current execution authority.
- predecessor `2105 / 2084 / 21` values are historical/runtime comparison roles, not current debt.

Shared disposition consumption contract only; not denominator adjudication, not terminal disposition re-adjudication, not Phase 4 live apply, not source/rendered/Lua-bridge/runtime/package authority mutation, not release readiness, not Workshop readiness, not B42 readiness, not deployment readiness, and not public-facing text quality acceptance.
