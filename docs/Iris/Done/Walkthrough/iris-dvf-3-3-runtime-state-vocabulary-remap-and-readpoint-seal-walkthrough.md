# Iris DVF 3-3 Runtime-State Vocabulary Remap and Readpoint Seal Walkthrough

> 상태: traceability read point  
> 기준일: 2026-04-26  
> authority: `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`, generated phase artifacts  
> round: DVF 3-3 Runtime-State Vocabulary Remap and Three-Axis Readpoint Seal

This walkthrough is not a new authority or gate source. It records how the round moved from scope lock to closeout.

## Why adopted/unadopted

The round remapped runtime_state vocabulary from:

```text
active  -> adopted
silent  -> unadopted
```

`adopted` was selected because the runtime axis means runtime adoption only. It does not mean semantic quality pass and does not imply default exposure.

`unadopted` was selected as the conservative negation of `adopted`.

`not_emitted` was deferred because it would narrow legacy `silent` into emission semantics. This round was terminology remap only, not runtime-state semantic redefinition.

## Historical Body Preservation

Historical sealed decision bodies were not rewritten. They may still contain `active/silent`.

Those historical runtime_state references are read through the terminology migration note:

```text
active  -> adopted
silent  -> unadopted
```

Axis-external historical `active` is not normalized by that note.

## Current Readpoints Updated

The authoritative top docs were updated after Phase 5 PASS:

- `docs/DECISIONS.md`: added the 2026-04-26 closeout decision
- `docs/ARCHITECTURE.md`: updated the current three-axis readpoint to `adopted/unadopted`
- `docs/ROADMAP.md`: moved the round into current completed summary and removed the Phase 0 Doing/Next entries

## Axis-External Active Handling

Phase 1 found extensive `active/silent` usage outside the runtime_state axis, especially historical plans, reports, and execution queue wording.

Handling:

- current readpoint runtime_state wording was updated
- historical sealed bodies were preserved
- staged/static payloads were classified as out-of-mutation runtime payload
- axis-external adopted/unadopted collision risk was handled by the Type H rule: avoid bare adopted/unadopted outside runtime_state value lists in current patches

## Artifact Map

Phase artifacts were generated under:

```text
Iris/build/description/v2/staging/compose_contract_migration/runtime_state_vocabulary_remap_round/
```

Key outputs:

- `phase0_scope_lock/runtime_state_vocabulary_remap_scope_lock.md`
- `phase0_scope_lock/runtime_state_vocabulary_remap_baseline_snapshot.json`
- `phase1_audit/three_axis_terminology_audit.json`
- `phase1_audit/runtime_state_json_enum_inventory.json`
- `phase1_audit/runtime_state_vocabulary_remap_phase1_decision.json`
- `phase2_vocabulary_seal/runtime_state_vocabulary_spec.md`
- `phase2_vocabulary_seal/runtime_state_legacy_mapping.json`
- `phase3_drift_classification/drift_classification_matrix.json`
- `phase4_mutation/canonical_seal_draft.md`
- `phase4_mutation/DECISIONS_patch_draft.md`
- `phase5_review/adversarial_review_report.md`
- `phase5_review/three_axis_readpoint_seal_validation_report.json`
- `phase6_closeout/runtime_state_vocabulary_remap_closeout.md`
- `phase6_closeout/runtime_state_vocabulary_remap_closeout.json`

## JSON Enum Scope Decision

Phase 1 selected:

```json
{
  "json_enum_update_scope": "docs_only",
  "staged_lua_hash_delta_expected": false,
  "staged_lua_hash_delta_reason": "none",
  "manual_in_game_validation_recheck_required": false,
  "legacy_alias_reader_required": false,
  "legacy_alias_reader_scope": "not_required"
}
```

Reason:

Phase 1 found runtime/static payloads with `runtime_state: active/silent` in staged observer artifacts. Rewriting those payloads would be runtime-facing/static artifact mutation and would require hash-delta classification and runtime-surface validation. This round stayed docs-only and read those payloads through the migration note.

## What Changed

- current top-doc readpoints now use `adopted/unadopted`
- DECISIONS closeout seals the vocabulary remap
- ARCHITECTURE separates runtime, quality, and publish axes with current value lists
- ROADMAP current summary reflects the closed docs-only readpoint seal
- generated artifacts document audit, classification, draft patch, review, and closeout

## What Did Not Change

- row count
- runtime adoption counts
- quality distribution
- publish split
- runtime behavior
- Lua bridge behavior
- Browser/Wiki default surface behavior
- identity_fallback treatment
- staged Lua payload
- manual in-game validation status
- historical sealed decision bodies

## Verification Summary

Phase 5 PASS:

- canonical seal covers drift types A-H
- historical body rewrite count: `0`
- runtime-facing payload mutation: `false`
- staged Lua hash delta expected: `false`
- staged Lua hash remains `0390272b93a933d7e53bba996b322ffbdd9fc905585bec03fc78d338f469f062`
- semantic UI exposure remains deferred
- `quality_exposed` remains reserved inactive
- runtime_state reserved slot was not added

## Reserved Follow-Ups

- runtime-facing enum/payload rename, if ever needed, requires a separate runtime-facing branch
- legacy alias reader support requires a separate explicit reader/validator round
- manual in-game validation QA remains separate
- semantic quality UI exposure remains separate
- `quality_exposed` activation remains separate
- `not_emitted` remains deferred

