# DVF 3-3 vNext Regeneration Requirements

> Status: definition-only regeneration contract
> Parent plan: `docs/dvf_3_3_vnext_current_authority_plan.md`
> Related docs:
> - `docs/dvf_3_3_vnext_authority_scope_lock.md`
> - `docs/dvf_3_3_vnext_source_authority_conditions.md`
> - `docs/dvf_3_3_vnext_runtime_seed_disposition.md`

## Purpose

This document defines the required source-to-runtime regeneration chain for a later DVF 3-3 vNext execution round.

It does not run regeneration, generate rendered output, export Lua bridge data, create chunk files, replace runtime chunks, or declare package or release readiness.

## Authority Chain

The required vNext chain is:

```text
source manifest
  -> facts
  -> decisions
  -> compose profile + body_plan
  -> rendered output
  -> Lua bridge export
  -> chunk manifest + chunk files
```

Every later artifact must be reproducible from the previous approved layer. A later layer cannot become authoritative if an earlier layer is missing, fixture-only, seed-only, or blocked.

## Input Authority Requirements

Facts may encode source-backed observations, normalized source facts, and accepted manual override facts.

Decisions may encode chosen disposition, wording authority, terminal state, and rule outcome.

Facts must not carry final prose policy. Decisions must not invent source facts.

Required later checks:

- Facts schema validation.
- Decisions schema validation.
- Fact-to-decision traceability.
- Manual override provenance.
- Terminal state validation.
- No backward flow from rendered validator output into decisions.

## Compose Profile and Body Plan

`body_plan` is a compose profile implementation surface and alias label. It is not a second authority.

The compose layer may consume accepted facts and decisions, but it must not:

- Create new source facts.
- Override decisions because rendered text looks better.
- Treat advisory style, structural signal, or quality signal as hard gate unless a separate authority says so.
- Read runtime chunks as source.
- Reintroduce legacy `active / silent` as current writer or validator vocabulary.

## Rendered Authority Requirements

Rendered output can become an accepted output only after a later execution plan proves:

- It was generated from accepted facts, decisions, compose profile, and body_plan.
- It passed rendered schema validation.
- It is deterministic for the same input set.
- It preserves the current runtime vocabulary `adopted / unadopted`.
- It does not expose quality state as badge, sorting, filtering, hiding, recommendation, or trust/confidence display.

Rendered generation alone is not enough to switch authority roles. Rendered output must continue through bridge, chunk, consumer, and reflection requirements before any later current-authority switch.

## Runtime Regeneration Requirements

Runtime regeneration means:

```text
rendered output -> Lua bridge export -> chunk manifest + chunk files
```

Later runtime regeneration must prove:

- Bridge export consumed the accepted rendered output.
- Chunk generation consumed the accepted bridge payload.
- Chunk manifest fingerprint is recorded.
- Chunk files match the chunk manifest.
- Public require contract is preserved.
- Monolith and chunk families are not both deployed as current payloads.

Chunk generation success by itself is not cutover evidence.

Generated chunk load smoke is a later execution validation item only. It is not manual in-game validation, package readiness, Workshop readiness, B42 readiness, or release readiness.

## Parity Rule

Successor parity is source-to-runtime self-consistency, not byte-level predecessor parity.

Required later parity checks:

- Source manifest to facts.
- Facts to decisions.
- Decisions to rendered output.
- Rendered output to Lua bridge payload.
- Lua bridge payload to chunk manifest and chunk files.
- Successor runtime to successor rendered output.

Existing chunks remain comparison reference, but byte-for-byte equality with predecessor chunks is not the successor criterion.

## Delta Classification Requirements

A later execution plan must classify every old-runtime-to-successor-runtime delta.

Allowed categories:

- `intentional_successor_delta`
- `source_gap`
- `schema_gap`
- `compose_delta`
- `validation_failure`
- `migration_required`

Unexplained deltas are fail-loud and must not be hidden by default text, fallback source, runtime seed, or fixture substitution.

## Terminal States

`confirmed`

The row has source basis and completed the required layer checks.

`genuine-zero`

The row is proven zero within a validated source universe.

`basis-unavailable`

The row cannot be proven because accepted source basis is missing.

`blocked`

The row cannot proceed because a required schema, validation, governance, or parity condition is absent.

## Later Execution Artifacts

The following names are allowed only as later execution outputs, not as outputs of this definition scope:

- `dvf_3_3_vnext_input_manifest.json`
- `dvf_3_3_vnext_facts.jsonl`
- `dvf_3_3_vnext_decisions.jsonl`
- `compose_profiles_vnext.json`
- `dvf_3_3_vnext_rendered.json`
- `rendered_runtime_parity.json`
- `vnext_parity_matrix.json`
- `intentional_delta_ledger.jsonl`
- `chunk_generation_result.md`
- `lua_bridge_export_result.md`

## Closeout Claim

The maximum claim from this document is:

DVF 3-3 vNext must later regenerate deterministically from source manifest through facts, decisions, compose profile, rendered output, Lua bridge, and chunks before authority roles can switch. This document defines requirements only and does not create, validate, deploy, package, or release any successor runtime payload.
