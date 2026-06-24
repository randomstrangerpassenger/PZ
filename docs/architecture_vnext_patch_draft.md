# ARCHITECTURE Draft Patch - DVF 3-3 vNext Current Authority

> Status: draft-only
> Intended target: `docs/ARCHITECTURE.md`
> Do not apply without a separate approved reflection step.

## Proposed Patch Location

Section `2-5. Iris`, under `DVF / QG의 위치`, after the current DVF 3-3 authority paragraph.

## Draft Text

DVF 3-3 vNext authority work is a successor-authority model path. It does not treat frozen `2105 / 2084 / 21` as recovered source, and it does not make runtime chunks source authority.

Before a later approved cutover:

- `vNext-CAB` is only a program / roadmap / authority-model label.
- Actual sealed baseline identity is deferred until later regeneration evidence exists.
- Existing chunk manifest and chunk files remain deployable runtime authority.
- Runtime chunks may be comparison reference but not source authority.
- Runtime-derived seed is non-authority bootstrap material and requires runtime-chunk provenance.

A later successor must be regenerated through this chain:

```text
source manifest
  -> facts
  -> decisions
  -> compose profile + body_plan
  -> rendered output
  -> Lua bridge export
  -> chunk manifest + chunk files
```

`body_plan` remains a compose profile implementation surface / alias label, not an independent authority.

Cutover requires a single-authority switch. Old chunks and successor chunks cannot both be current. Rendered-only, bridge-only, chunk-generation-only, or draft-reflection-only outputs cannot become current authority by themselves.

The 2105 consumption audit is migration input only. Consumer migration changes authority-role references after successor approval; it is not numeric replacement and does not promote historical or diagnostic references to current hard gates.

## Draft Boundary

This patch must not be applied as a runtime state change. It is architecture wording only and remains draft until a separate approved reflection step mutates `docs/ARCHITECTURE.md`.
