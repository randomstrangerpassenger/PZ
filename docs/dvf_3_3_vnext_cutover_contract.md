# DVF 3-3 vNext Cutover Contract

> Status: definition-only cutover contract
> Parent plan: `docs/dvf_3_3_vnext_current_authority_plan.md`
> Related docs:
> - `docs/dvf_3_3_vnext_authority_scope_lock.md`
> - `docs/dvf_3_3_vnext_regeneration_requirements.md`
> - `docs/dvf_3_3_vnext_consumer_migration_principles.md`

## Purpose

This document defines the conditions under which a later DVF 3-3 vNext successor can become the single current authority.

It does not perform cutover, generate successor artifacts, modify runtime chunks, or update DECISIONS / ARCHITECTURE / ROADMAP.

## Pre-Cutover Rule

Before a later approved cutover:

- Existing chunk manifest and chunk files remain the deployable runtime authority.
- Runtime chunks remain comparison reference, not source authority.
- `vNext-CAB` remains a program and authority-model label, not the sealed baseline identity.
- Runtime-derived seed remains non-authority bootstrap material.
- No successor partial output may replace runtime payload.

## Cutover Preconditions

All of the following must pass in a later execution and reflection step:

- Source universe manifest sealed.
- Facts generated and validated.
- Decisions generated and validated.
- Compose profile and body_plan identity sealed.
- Rendered output generated, deterministic, and schema-valid.
- Lua bridge export generated from accepted rendered output.
- Chunk manifest and chunk files generated from accepted bridge payload.
- Rendered-to-runtime parity report passes.
- Delta matrix classifies every predecessor-to-successor difference.
- Unexplained delta count is zero.
- Consumer migration dry-run passes.
- Current hard gate consumers are updated or explicitly preserved.
- Ledger reflection packet is applied through an approved docs-canon update.
- Monolith / chunk dual deployment guard passes.
- Public require contract is preserved.

If any required layer is missing, partial, fixture-only, seed-only, or blocked, cutover is forbidden.

## Single-Authority Rule

DVF 3-3 allows one current runtime authority family.

Forbidden states:

- Old chunks and successor chunks both described as current.
- Monolith and chunks both deployed as current payloads.
- Rendered output treated as current while bridge/chunks remain predecessor.
- Bridge payload treated as current while chunks remain predecessor.
- Docs ledger naming a successor current before runtime and consumer migration pass.

## Partial Promotion Rule

Partial output cannot become current authority.

Examples of insufficient evidence:

- Source manifest only.
- Facts and decisions only.
- Rendered output only.
- Lua bridge export only.
- Chunk generation success only.
- Chunk load smoke only.
- Consumer migration draft only.
- Reflection packet draft only.

Each may be evidence for a later step, but none is cutover by itself.

## Rollback Rule

Rollback means retaining the pre-cutover deployable chunk family or reverting to it if a later approved cutover fails after application.

Rollback must not be described as predecessor recovery. It is current chunk retention before successor acceptance.

## Ledger Rule

DECISIONS / ARCHITECTURE / ROADMAP must not be directly modified by this contract.

Later ledger mutation requires:

- Approved reflection application.
- Sealed successor identity.
- Evidence paths.
- Non-release-readiness disclaimer.
- Explicit predecessor/successor language.

Closeout reports and draft packets do not replace DECISIONS.

## Runtime and Release Boundary

Cutover validation is not the same as:

- Package readiness.
- Workshop readiness.
- B42 readiness.
- Manual in-game validation.
- Long-session runtime behavior validation.
- Multiplayer validation.
- Public UI behavior validation.

Those require separate release or QA scopes.

## Closeout Claim

The maximum claim from this document is:

DVF 3-3 vNext has a no-premature-cutover contract. Existing chunks remain deployable runtime authority until a separate approved execution and reflection step passes source, facts, decisions, rendered, bridge, chunk, parity, delta, consumer, and ledger gates. Dual current authority and partial promotion are forbidden.
