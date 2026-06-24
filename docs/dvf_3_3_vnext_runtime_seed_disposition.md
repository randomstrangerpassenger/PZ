# DVF 3-3 vNext Runtime Seed Disposition

> Status: definition-only seed disposition
> Parent plan: `docs/dvf_3_3_vnext_current_authority_plan.md`
> Related scope lock: `docs/dvf_3_3_vnext_authority_scope_lock.md`

## Purpose

This document defines the only allowed status of runtime-derived seed material in the DVF 3-3 vNext path.

Runtime-derived seed exists only to help a later execution round bootstrap comparison or reconstruction work. It is not source authority, fact authority, decision authority, rendered authority, or runtime cutover evidence.

## Seed Definition

A runtime-derived seed is any row, text, field, identifier, status value, or structure derived from existing chunk manifest or chunk files.

Required provenance:

```text
provenance: derived-from-runtime-chunks
authority_role: non_authority_bootstrap_seed
source_authority: false
current_fact: false
current_decision: false
rendered_authority: false
```

Seed-derived artifacts must carry provenance forward. A later artifact that consumes seed material without provenance fails the vNext authority contract.

## Allowed Use

Runtime-derived seed may be used for:

- Bootstrap inventory.
- Comparison candidate extraction.
- Candidate fullType or text alignment.
- Parity investigation planning.
- Gap discovery.
- Manual review queue construction.

Runtime-derived seed may not be used for:

- Source authority.
- Canonical fact creation.
- Canonical decision creation.
- Rendered output promotion.
- Lua bridge payload promotion.
- Chunk payload promotion.
- Consumer migration execution.
- Ledger canon update.

## Existing Runtime Chunks

Existing runtime chunks keep two roles before a later cutover:

- Deployable runtime authority.
- Comparison reference.

They do not become source authority because source authority must come from a validated input universe, not from the deployed rendering result.

## Promotion Gate

A seed row can only contribute to a future authority artifact after a later execution plan verifies it against accepted source inputs.

Minimum later requirements:

- Source universe coverage exists for the row.
- Source manifest records the accepted source path and fingerprint.
- Facts validator accepts the row as source-backed.
- Decisions validator accepts the decision basis.
- Rendered output is generated from accepted decisions.
- Runtime output is regenerated from rendered output.

Until those conditions pass, the seed row remains a candidate and must not be described as a current fact.

## Failure Modes

The following are fail-loud conditions:

- Seed material is written without provenance.
- Seed material is used as source authority.
- Existing chunks are described as recovered source.
- Seed-derived facts bypass source validation.
- Seed-derived rendered output bypasses decisions.
- Seed-derived chunk output is treated as cutover evidence without source-to-runtime regeneration.

## Vocabulary Boundary

`active / silent` may appear only when clearly labeled as historical, diagnostic, or import alias vocabulary.

`adopted / unadopted` remains the runtime vocabulary for current payload status, but seed disposition does not grant these words quality, publish, deletion, or suppression meaning.

## Closeout Claim

The maximum claim from this disposition is:

Runtime-derived seed is allowed only as non-authority bootstrap material with explicit runtime-chunk provenance. Existing chunks remain deployable runtime authority and comparison reference, not source authority. No seed-derived row becomes current fact, current decision, rendered authority, bridge payload, chunk payload, or ledger canon under this document.
