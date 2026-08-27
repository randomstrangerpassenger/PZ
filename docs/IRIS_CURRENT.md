# Iris Current Readpoint

Status: canonical human and AI navigation owner

Iris is an evidence-driven information mod. Its constitutional authority is [Philosophy.md](Philosophy.md); current decisions and architecture remain in [DECISIONS.md](DECISIONS.md), [ARCHITECTURE.md](ARCHITECTURE.md), and [ROADMAP.md](ROADMAP.md).

## Current routes

| Role | Current owner |
|---|---|
| Iris authority classification | `Iris/_docs/authority/iris_current_authority_manifest.json` |
| Build and validation command literals | `Iris/build/ENTRYPOINTS.md` |
| Installed build producers | `Iris/tooling/src/iris_tooling/**` |
| Current validation membership | `Iris/_docs/round3/current_route_required_validations.json` |
| Clean-checkout validator | `Iris/validation/clean_checkout/run_iris_clean_checkout_validation.py` |
| Receipt-bound launcher | `Iris/validation/clean_checkout/invoke_receipt_bound_full_gate.ps1` |
| Deterministic comparator | `Iris/validation/clean_checkout/invoke_deterministic_compare.ps1` |
| Current environment locator | `Iris/validation/clean_checkout/authority/responsibility_refactor_environment_current.json` |
| Machine navigation projection | `Iris/_docs/authority/iris_current_route_index.json` |

## Result and evidence boundary

Build and validation use a deterministic canonical semantic result and a separate volatile execution envelope. Run receipts and failure evidence live in explicit repository-external result roots. There is no mutable latest receipt or cross-run ledger in this route; a receipt is queried by its explicit locator.

## Historical access

Files under `_docs`, predecessor tooling, plans, closeouts, and reproduction evidence remain historical or reproduction inputs unless the authority manifest or current route names an exact path. Historical and diagnostic test routes are opt-in through the command owner above. Their existence does not make them current authority.

## Scope boundary

This readpoint covers build, validation, authority navigation, and receipt lookup. It does not claim Wiki/Browser presentation completion, Lua UI optimization, release readiness, or external-mode compatibility.
