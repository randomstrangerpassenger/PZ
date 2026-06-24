# ROADMAP Draft Patch - DVF 3-3 vNext Current Authority

> Status: draft-only
> Intended target: `docs/ROADMAP.md`
> Do not apply without a separate approved reflection step.

## Proposed Patch Location

Section `# 5. Iris`, under `Doing` and `Next`.

## Draft Doing Text

- DVF 3-3 vNext current-authority work is in definition-only scope.
  - `vNext-CAB` is a pre-cutover program / authority-model label, not a sealed baseline identity.
  - Frozen `2105 / 2084 / 21` remains predecessor, comparison context, and migration input.
  - Existing runtime chunks remain deployable runtime authority until a later approved cutover.
  - Runtime-derived seed is non-authority bootstrap material only.
  - Runtime chunks and seed are not source authority.
  - DECISIONS / ARCHITECTURE / ROADMAP reflection remains draft-only until separately approved.

## Draft Next Text

- Open a separate DVF 3-3 vNext execution plan only after the definition-only contract is accepted.
  - Produce a validated source universe manifest.
  - Generate facts and decisions from accepted source inputs.
  - Regenerate rendered output from accepted decisions and compose profile / body_plan.
  - Export Lua bridge payload from rendered output.
  - Generate chunk manifest and chunk files from bridge payload.
  - Validate successor source-to-runtime self-consistency.
  - Classify predecessor-to-successor deltas.
  - Run consumer migration dry-run based on the 2105 audit.
  - Apply docs-canon reflection only through a separate approved step.

## Draft Hold Text

- Treating `vNext-CAB` as actual sealed baseline identity before regeneration evidence exists.
- Treating runtime chunks or runtime-derived seed as source authority.
- Replacing numbers or vocabulary mechanically instead of migrating authority roles.
- Promoting rendered-only, bridge-only, or chunk-generation-only output to current authority.
- Allowing old chunks and successor chunks to both be current.
- Marking vNext execution work Done from this definition-only scope.
- Reading this roadmap draft as package readiness, release readiness, Workshop readiness, B42 readiness, manual in-game validation, or public UI behavior validation.

## Draft Boundary

This patch is not a Done-state update. It must not be applied until a separate approved reflection step decides how ROADMAP should represent definition-only state versus later execution state.
