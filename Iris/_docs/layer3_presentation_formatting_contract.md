# Layer 3 Presentation Formatting Contract

Date: 2026-05-07

Status: active

Authority:

- `docs/Philosophy.md`
- `docs/DECISIONS.md`, 2026-03-25 Layer 3 render-time formatting decision
- `docs/ARCHITECTURE.md`, UI formatting and data contract separation

## Contract

Layer 3 presentation formatting is render-time only.

The production data contract remains source-text preserving:

- authoritative `rendered.json` text is not edited for display wrapping.
- `Iris/media/lua/client/Iris/Data/IrisLayer3Data.lua` stores the exported
  Layer 3 text without UI wrapping changes.
- `Iris/media/lua/client/Iris/Data/layer3_renderer.lua` returns raw gated
  Layer 3 text. It may enforce `publish_state`, but it must not split,
  summarize, filter, reorder, or rewrite the text for display.

UI display surfaces own presentation formatting:

- `Iris/media/lua/client/Iris/UI/Layer3/IrisLayer3DisplayFormatter.lua` is the
  canonical UI-only Layer 3 formatter.
- Browser and Wiki consumers may split formatter newlines into labels.
- UI consumers may adjust wrapping, spacing, and panel-specific line breaks.

## Allowed

- UI-only line breaks.
- UI-only block spacing.
- UI-width-sensitive wrapping.
- Splitting formatted text on newline when creating labels.

## Forbidden

- Editing `rendered.json` to add display-only wrapping.
- Editing `IrisLayer3Data.lua` to add display-only wrapping.
- Adding display formatting to `layer3_renderer.lua`.
- Deleting, filtering, summarizing, or reordering Layer 3 source sentences.
- Adding recommendation, comparison, or interpretation text at runtime.

## Gate

Phase 4-7 is guarded by static contract tests:

- the UI formatter must exist under `Iris/UI/Layer3`.
- `IrisWikiSections.lua` must call the UI formatter after
  `Layer3Renderer.getText(...)`.
- `layer3_renderer.lua` and `IrisLayer3Data.lua` must not contain UI formatting
  helpers.
- Browser/Wiki panel consumers must still split formatted newlines into display
  labels.

Formatting-only work must not rebaseline data contract hashes for
`rendered.json` or `IrisLayer3Data.lua`.
