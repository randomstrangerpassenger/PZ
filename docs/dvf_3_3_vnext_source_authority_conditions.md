# DVF 3-3 vNext Source Authority Conditions

> Status: definition-only source authority contract
> Parent plan: `docs/dvf_3_3_vnext_current_authority_plan.md`
> Related scope lock: `docs/dvf_3_3_vnext_authority_scope_lock.md`

## Purpose

This document defines when DVF 3-3 vNext source authority can exist.

It does not create a source manifest instance, facts JSONL, decisions JSONL, rendered output, Lua bridge output, or runtime chunks.

## Source Authority Rule

Source authority requires a validated source universe. It cannot be inferred from:

- Runtime chunks.
- Runtime-derived seed.
- Fixture files.
- Current 6-entry facts / decisions / rendered files.
- Generated staging artifacts without source manifest backing.
- Historical predecessor documents.
- Diagnostic reports.
- Docs-only references.

## Required Source Manifest Contract

A later execution plan must produce a source manifest with, at minimum:

- Manifest schema version.
- Authority label.
- Actual sealed baseline identity placeholder or sealed identity after validation.
- Source root list.
- Included file list.
- Per-file fingerprint.
- Source type classification.
- Row coverage basis.
- Exclusion rationale for non-source material.
- Tool version or generator identity.
- Validation result.

The manifest must distinguish source input from comparison input, migration input, fixture input, and seed input.

## Terminal States

`confirmed`

The row has accepted source basis, passed validation, and may flow into facts or decisions according to its role.

`genuine-zero`

The row is proven absent inside a known, validated source universe. This is not an alias for missing input. It requires a manifest-backed search basis.

`basis-unavailable`

The source universe does not contain enough accepted basis to decide the row. This is a terminal fail-loud state for that row until a new input authority is approved.

`blocked`

The row cannot proceed because source, schema, validation, or governance prerequisites are missing. This must remain visible and must not silently fall back to predecessor or runtime seed.

## Source Absence Rules

Source absence must be recorded explicitly.

Allowed:

- `basis-unavailable` when the required source basis is missing.
- `blocked` when governance or validation prevents continuation.
- `genuine-zero` only when a validated source universe proves the zero.

Forbidden:

- Treating a missing source file as `genuine-zero`.
- Treating runtime chunks as replacement source.
- Treating seed candidates as recovered source.
- Treating a fixture as full authority.
- Treating docs-only historical references as source rows.

## Facts and Decisions Entry Gate

Facts and decisions may consume only accepted source-backed input or explicitly approved manual override input from a later execution plan.

Every accepted row must be traceable to one of:

- Source manifest entry.
- Approved manual override entry.
- Validated genuine-zero proof.

Rows with `basis-unavailable` or `blocked` must not be normalized into facts or decisions.

## Fail-Loud Conditions

The following conditions must stop later execution or mark the row blocked:

- No source manifest exists.
- Source manifest is partial without explicit scope lock.
- Source fingerprint mismatch.
- Fixture promoted to full source role.
- Runtime-derived seed consumed without provenance.
- Runtime chunks used as source.
- A zero is declared without source universe proof.

## Closeout Claim

The maximum claim from this contract is:

DVF 3-3 vNext source authority requires a later validated source universe manifest. Fixture, staging, runtime-derived, historical, diagnostic, and docs-only surfaces are not enough. `confirmed`, `genuine-zero`, `basis-unavailable`, and `blocked` are the terminal states that later execution must use without silent fallback.
