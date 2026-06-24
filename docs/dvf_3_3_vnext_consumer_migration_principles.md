# DVF 3-3 vNext Consumer Migration Principles

> Status: definition-only migration principles
> Parent plan: `docs/dvf_3_3_vnext_current_authority_plan.md`
> Audit input: `Iris/build/description/v2/staging/2105_baseline_consumption_audit/`

## Purpose

This document defines how the `2105 Baseline Consumption Audit` is consumed by later DVF 3-3 vNext migration work.

It does not perform consumer migration and does not modify tests, validators, tools, runtime payloads, docs canon, or generated artifacts.

## Audit Inputs

Read-only migration inputs:

- `change_required_index.md`
- `change_forbidden_index.md`
- `classified_ledger.jsonl`
- `executing_consumer_impact.md`

Supporting audit files may be used only to clarify classification:

- `current_route_index.md`
- `diagnostic_route_index.md`
- `historical_route_index.md`
- `executing_consumers.jsonl`
- `consumer_matrix.csv`
- `validation_result.md`

## Current Audit Read

The audit split is authoritative as migration input, not as direct mutation instruction.

Observed classification summary from `classified_ledger.jsonl`:

- `preserve_as_historical_trace`: 23169
- `preserve_as_diagnostic_reference`: 3329
- `no_change`: 1185
- `migrate_when_new_baseline_approved`: 163
- `preserve_as_current_gate`: 23

Observed disposition summary:

- `historical-reference`: 23169
- `diagnostic-only`: 3329
- `no-op`: 1060
- `vNext-migration`: 229
- `current-hard-gate`: 82

Observed executing consumer impact:

- `current`: 126
- `current-route-index`: 211
- `diagnostic`: 673
- `historical`: 52

These numbers classify migration attention. They do not grant permission to edit every listed occurrence.

## Migration Unit

Migration is authority-role migration, not numeric text replacement.

Allowed later migration:

- Replace predecessor authority role assumptions with successor authority role references after a later baseline is approved.
- Update current hard gate consumers only when they must point to the later sealed successor identity.
- Keep historical and diagnostic references intact when their referent is historical or diagnostic.
- Preserve `active / silent` references when clearly historical, diagnostic, or import alias.

Forbidden later migration:

- Replace every `2105`, `2084`, `21`, `active`, or `silent` occurrence mechanically.
- Treat docs-only historical references as current hard gates.
- Treat generated diagnostic reports as source authority.
- Treat `change_required_index.md` as an executable instruction list.
- Treat `change_forbidden_index.md` rows as cleanup candidates.

## Consumer Classes

`current hard gate`

Validator, test, tool, runtime, or authoritative doc surface that participates in the current authority contract. Later changes require a sealed successor identity and execution plan.

`current route index`

Rows that point to current route behavior or guard expectations. Later migration must preserve route semantics and update only authority-role references.

`diagnostic-only`

Rows that exist for audits, reports, historical reconstruction, compatibility guards, or generated diagnostic trace. These must not be promoted to current gates.

`historical reference`

Rows that preserve predecessor trace. These should remain historical unless a separate authority says the historical reference itself is wrong.

`no-op`

Rows that are accepted audit candidates but do not require migration for vNext authority role work.

## Active / Silent Rule

Legacy `active / silent` occurrence scans are not automatic violations.

Violation exists only when `active / silent` re-enters current writer, current validator, or runtime payload vocabulary without explicit historical, diagnostic, or import-alias labeling.

Allowed:

- Historical predecessor trace.
- Diagnostic compatibility report.
- Import alias mapping.
- Explanation of why the vocabulary is not current.

Forbidden:

- Current writer output.
- Current validator required value.
- Runtime payload state value.
- Publish, quality, deletion, or suppression state.

## Forbidden Rows Rule

Rows in `change_forbidden_index.md` are preservation rows unless a later approved correction explicitly narrows a row.

They must not be touched by broad cleanup, numeric replacement, vocabulary replacement, or release-note wording passes.

## Future Execution Preconditions

A later consumer migration plan must include:

- Sealed successor identity.
- Migration target list by route class.
- Per-row rationale for current hard gate changes.
- No-op and preservation list.
- Dry-run report.
- Validation command list.
- Rollback plan that preserves pre-cutover runtime chunks.

## Closeout Claim

The maximum claim from this document is:

The 2105 audit is read-only migration input. Later vNext migration must change authority roles only after successor approval, preserve historical and diagnostic rows, avoid numeric replacement, and treat `active / silent` as a violation only if it re-enters current writer, validator, or runtime payload vocabulary.
