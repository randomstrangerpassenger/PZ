# DVF 3-3 vNext Authority Scope Lock

> Status: definition-only scope lock
> Parent plan: `docs/dvf_3_3_vnext_current_authority_plan.md`
> Top authority: `docs/Philosophy.md`

## Purpose

This document locks the scope and vocabulary for DVF 3-3 vNext current-authority work before any execution round starts.

The vNext work is a successor-authority definition path. It is not an attempt to revive frozen `2105 / 2084 / 21` as a recovered baseline, and it does not grant current authority to any new source, rendered output, Lua bridge payload, chunk manifest, or chunk file.

## Scope

This scope lock allows only governance and contract drafting.

Allowed outputs:

- Authority vocabulary and role definitions.
- Successor identity rules.
- Runtime-derived seed disposition rules.
- Source, facts, decisions, compose, rendered, bridge, chunk, consumer, and cutover conditions.
- Draft-only reflection material for DECISIONS / ARCHITECTURE / ROADMAP.

Not allowed in this scope:

- New baseline generation.
- Source manifest instance creation.
- Facts or decisions JSONL instance creation.
- Rendered output generation.
- Lua bridge export.
- Chunk manifest or chunk file generation or replacement.
- Consumer migration execution.
- Direct mutation of `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, or `docs/ROADMAP.md`.
- Runtime rollout, package build, Workshop readiness, B42 readiness, or manual in-game validation claims.

## Terms

`vNext-CAB`

Program, roadmap, and authority-model label used before cutover. It is not the sealed baseline identity.

`actual sealed baseline identity`

The identity sealed after a later execution round produces count, source manifest fingerprint, rendered hash, chunk manifest fingerprint, and required validation evidence. Until that later artifact exists, this identity is intentionally deferred.

`predecessor`

The frozen `2105 / 2084 / 21` authority family as a historical baseline and migration context. It is not the target of reconstruction in this scope.

`successor`

A future authority family that may replace the predecessor role only after a separate approved execution and reflection step.

`comparison reference`

Existing runtime chunks may be used to compare successor output. This does not make those chunks source authority.

`migration input`

Audit rows from `Iris/build/description/v2/staging/2105_baseline_consumption_audit/` that classify consumers and migration principles. The audit is read-only input.

`seed candidate`

Runtime-derived bootstrap material with explicit provenance. A seed candidate is not source, fact, decision, or rendered authority.

`source authority`

The validated input universe from which facts and decisions can be generated. Fixture, staging-only, runtime-derived-only, or partial inputs do not satisfy this role.

`deployable runtime authority`

The currently deployed chunk manifest plus chunk files. Before a later cutover, this remains the existing runtime chunk family.

`current authority`

The single active authority chain accepted by the ledger and runtime contract. DVF 3-3 does not allow old and successor chunk families to both hold this role.

## Identity Rules

`vNext-CAB` is allowed only as a pre-cutover program label.

The actual sealed baseline identity must remain blank until a later execution round has all of the following:

- Source universe manifest fingerprint.
- Facts and decisions counts.
- Compose profile and body_plan identity.
- Rendered output hash.
- Lua bridge export fingerprint.
- Chunk manifest fingerprint.
- Consumer migration result.
- Ledger reflection result.

No document may replace `2105` with a new number and call that an authority migration. The migration unit is authority role, not number text.

## Successor Relation

The successor relation is supersession, not recovery.

Allowed statement:

- The vNext path defines conditions under which a later successor may replace the predecessor role.

Forbidden statement:

- The frozen predecessor has been reconstructed, recovered, or restored by this scope.

## Boundary Rules

- Runtime chunks are deployable runtime authority and comparison reference only.
- Runtime-derived seed is non-authority bootstrap material only.
- Current 6-entry facts / decisions / rendered fixtures remain fixtures and cannot stand in for full authority.
- Body_plan remains a compose profile implementation surface or alias label, not a second authority.
- `active / silent` remains historical, diagnostic, or import alias vocabulary only.
- Current runtime vocabulary remains `adopted / unadopted`.
- `adopted / unadopted` must not be used as quality, publish, deletion, or suppression vocabulary.

## Closeout Claim

The maximum claim from this scope lock is:

DVF 3-3 vNext is scoped as a successor-authority definition path. Frozen `2105 / 2084 / 21` remains predecessor, comparison, and migration context. `vNext-CAB` is a program label until later sealed identity evidence exists. No source, rendered, bridge, chunk, runtime, package, release, or ledger-canon mutation is authorized here.
