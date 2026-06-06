# MIGV-QA Validation Harness v0.4

Generated at: `2026-05-23T23:35:17.452+09:00`

## Evidence Schema

Each manual observation must record: sample id, fullType, chunk, runtime state, publish state, surface, environment, expected behavior, observed behavior, result, screenshot or structured note path, and console attribution note.

## Console Readpoint Convention

Record the Project Zomboid `Console.txt` path, timestamp window, and whether the capture is vanilla-adjacent/Iris-only or the project default playtest baseline before opening Iris surfaces. No console capture was performed by this static artifact generation step.

## Required Surfaces

- Browser
- Wiki/detail
- Default bounded baseline
- Search/select/reselect

## Required Publish Checks

- exposed sample appears on intended user-facing surfaces
- internal_only sample may remain visible as an item entry but does not leak raw internal state tokens or broken placeholders
- missing publish_state finding row follows the revised all-item Browser contract
- nil text_ko finding row does not render as a broken placeholder
- raw state tokens are not shown to users

## Deferred Surface

Alt tooltip validation is out of scope for this round.

## Current Execution Status

Static gates are prepared. Manual in-game validation is pending.
