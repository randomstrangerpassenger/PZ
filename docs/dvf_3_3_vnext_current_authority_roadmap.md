# DVF 3-3 vNext Current Authority Roadmap

> Status: sealed definition-only roadmap
> Closeout state: `roadmap_sealed_definition_only`
> Parent plan: `docs/dvf_3_3_vnext_current_authority_plan.md`
> Top authority: `docs/Philosophy.md`

## Problem

Frozen `2105 / 2084 / 21` cannot be kept as the practical current source baseline because byte-level recovery has been sealed as unavailable. The DVF 3-3 system therefore needs a successor current-authority model that can replace the predecessor role without pretending that frozen 2105 was recovered.

This is a direction and boundary problem before implementation. It defines what a successor baseline may replace, what it may not replace, and which evidence is required before any current authority switch.

## Already Closed

- Frozen 2105 byte-level baseline is sealed as unrecoverable predecessor.
- Current deployable runtime authority exists only as chunk manifest plus chunk files.
- Staging artifacts and historical artifacts do not become current authority by existence.
- Current 6-entry facts / decisions / rendered files remain fixtures and non-authority.
- Runtime chunks are deployable runtime authority and comparison reference, not source authority.

## Unresolved Before This Roadmap

The unresolved issue was not how to generate the next payload. The unresolved issue was authority shape:

- What the new baseline replaces.
- What the new baseline does not replace.
- What status runtime-derived seed may have.
- Which conditions establish source / facts / decisions / profile / rendered / runtime authority.
- Which gates must pass before a successor can become current authority.
- How predecessor 2105 references are handled in ledgers and consumers.

## Successor Direction

The successor path is `vNext-CAB` before cutover.

`vNext-CAB` is a program / roadmap / authority-model label only. It is not the actual sealed baseline identity.

The actual sealed baseline identity is deferred until a later execution round produces:

- Source universe count.
- Source manifest fingerprint.
- Facts and decisions counts.
- Compose profile and body_plan identity.
- Rendered output hash.
- Lua bridge export fingerprint.
- Chunk manifest fingerprint.
- Consumer migration result.
- Ledger reflection evidence.

The successor relation is supersession, not recovery.

## Authority Model

The successor current-authority chain must be:

```text
source manifest
  -> facts
  -> decisions
  -> compose profile + body_plan
  -> rendered output
  -> Lua bridge export
  -> chunk manifest + chunk files
```

No later layer can become current if an earlier layer is missing, fixture-only, seed-only, basis-unavailable, or blocked.

`body_plan` is a compose profile implementation surface / alias label. It is not a second authority.

## Runtime Seed Rule

Runtime-derived seed may exist only as non-authority bootstrap material.

Required seed status:

```text
provenance: derived-from-runtime-chunks
authority_role: non_authority_bootstrap_seed
source_authority: false
current_fact: false
current_decision: false
rendered_authority: false
```

Runtime-derived seed may support inventory, comparison, and gap discovery. It must not become source authority, recovered source, current fact, current decision, rendered authority, bridge payload authority, chunk payload authority, consumer migration authority, or ledger canon.

## Source Authority Conditions

Source authority requires a later validated source universe manifest.

The following are not source authority:

- Runtime chunks.
- Runtime-derived seed.
- Fixture files.
- Current 6-entry facts / decisions / rendered files.
- Staging artifacts without manifest-backed source basis.
- Historical predecessor documents.
- Diagnostic reports.
- Docs-only references.

Allowed terminal states for later execution:

- `confirmed`
- `genuine-zero`
- `basis-unavailable`
- `blocked`

`genuine-zero` requires proof inside a validated source universe. It is not an alias for missing source.

## Regeneration Requirements

A later execution round must prove deterministic regeneration from source to runtime.

Required later validation families:

- Source manifest schema and fingerprint validation.
- Facts schema validation.
- Decisions schema validation.
- Fact-to-decision traceability.
- Compose profile and body_plan consistency.
- Rendered schema validation.
- Rendered determinism validation.
- Rendered-to-bridge parity.
- Bridge-to-chunk parity.
- Chunk manifest and chunk file consistency.
- Successor source-to-runtime self-consistency.

Successor parity is successor source-to-runtime self-consistency. It is not byte-level predecessor parity.

## Delta and Migration Rules

Old runtime chunks may be used as comparison reference. Every old-runtime-to-successor-runtime delta must later be classified.

Allowed delta categories:

- `intentional_successor_delta`
- `source_gap`
- `schema_gap`
- `compose_delta`
- `validation_failure`
- `migration_required`

Unexplained deltas are fail-loud.

The 2105 Baseline Consumption Audit is read-only migration input. Migration means authority-role migration after successor approval, not numeric replacement.

Historical and diagnostic references stay historical or diagnostic unless a later approved correction narrows a specific row.

Legacy `active / silent` remains historical / diagnostic / import alias vocabulary only. It is a violation only if it re-enters current writer, current validator, or runtime payload vocabulary.

Current runtime vocabulary remains `adopted / unadopted`, and those words must not become quality, publish, deletion, or suppression vocabulary.

## Cutover Strategy

Before cutover:

- Existing chunks remain deployable runtime authority.
- `vNext-CAB` remains a pre-cutover label.
- Runtime-derived seed remains non-authority bootstrap.
- Successor partial output remains staging-only.

Cutover requires:

- Source manifest sealed.
- Facts and decisions validated.
- Compose profile and body_plan identity sealed.
- Rendered output generated deterministically.
- Lua bridge export generated from accepted rendered output.
- Chunk manifest and chunk files generated from accepted bridge payload.
- Parity and delta classification passed.
- Unexplained delta count is zero.
- Consumer migration dry-run passed.
- Current hard gate consumers updated or explicitly preserved.
- Ledger reflection applied through a separate approved docs-canon step.
- Monolith / chunks dual deployment guard passed.
- Public require contract preserved.

Partial promotion is forbidden. Rendered-only, bridge-only, chunk-generation-only, smoke-only, migration-draft-only, or reflection-draft-only output cannot become current authority.

Old chunks and successor chunks cannot both be current.

## Ledger Reflection

DECISIONS / ARCHITECTURE / ROADMAP mutation is not performed by this roadmap.

This roadmap authorizes draft packet preparation only. Canon mutation requires a separate approved reflection application or follow-up closeout step.

Draft packet:

- `docs/dvf_3_3_vnext_ledger_update_packet.md`
- `docs/decisions_vnext_entry_draft.md`
- `docs/architecture_vnext_patch_draft.md`
- `docs/roadmap_vnext_patch_draft.md`

## Completion Definition

This roadmap is sealed when the following documents exist and agree on definition-only scope:

- `docs/dvf_3_3_vnext_current_authority_plan.md`
- `docs/dvf_3_3_vnext_authority_scope_lock.md`
- `docs/dvf_3_3_vnext_runtime_seed_disposition.md`
- `docs/dvf_3_3_vnext_source_authority_conditions.md`
- `docs/dvf_3_3_vnext_regeneration_requirements.md`
- `docs/dvf_3_3_vnext_consumer_migration_principles.md`
- `docs/dvf_3_3_vnext_cutover_contract.md`
- `docs/dvf_3_3_vnext_ledger_update_packet.md`
- `docs/dvf_3_3_vnext_current_authority_roadmap.md`

## Non-Completion

This roadmap does not complete or approve:

- Frozen 2105 recovery.
- New sealed baseline generation.
- Source manifest instance generation.
- Facts / decisions / rendered output generation.
- Lua bridge export.
- Chunk manifest or chunk file generation.
- Runtime cutover.
- Consumer migration execution.
- Direct DECISIONS / ARCHITECTURE / ROADMAP mutation.
- Package readiness.
- Workshop readiness.
- B42 readiness.
- Release readiness.
- Manual in-game validation.
- Browser / Wiki / Tooltip behavior change.
- Quality exposure change.
- Layer4 reopen.
- ACQ_DOMINANT reopen.
- Acquisition Lexical reopen.
- Closed readpoint re-adjudication.

## Final Roadmap Claim

DVF 3-3 vNext is sealed as a successor current-authority roadmap. Frozen `2105 / 2084 / 21` remains predecessor, comparison reference, and migration input. The successor path must establish source-to-runtime authority through validated source manifest, facts, decisions, compose profile / body_plan, rendered output, Lua bridge export, chunk manifest, chunk files, parity, delta classification, consumer migration, and separate ledger reflection before current authority cutover. Runtime chunks and runtime-derived seed cannot replace source authority, and partial or dual current authority is forbidden.
