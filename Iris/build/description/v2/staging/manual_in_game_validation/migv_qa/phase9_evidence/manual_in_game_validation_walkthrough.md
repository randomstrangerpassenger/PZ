# MIGV-QA Walkthrough v0.4

Generated at: `2026-05-23T23:35:17.452+09:00`
Updated at: `2026-05-24T21:13:43+09:00`

## Target Artifact

Current deployable authority is the chunk manifest plus `Chunk001..011.lua`; monolith `IrisLayer3Data.lua` is absent.

## Identity Pre-Gate

Phase 1 passed by consuming the sealed current runtime baseline evidence:

- `Iris/build/description/v2/staging/dvf_3_3_current_runtime_baseline_seal_round/reports/current_runtime_hash_manifest.json` sha256 `790b5689097a8856e6213074fda25b723060073206a7ca44bd26d9f6f08c9171`

Historical staged hash `0390272b...` was not used as the current identity gate.

## Static Validation

- Python unittest: 394 tests / OK
- Lua syntax: 183 files / OK
- Legacy active/silent current-surface guard: pass, hard-fail current-label occurrence 0

## Manual Evidence Supplied

The user supplied `Iris/Playtest/` with one enabled-mod screenshot, six Iris Browser screenshots, and `console.txt`.

Observed environment:

- Project Zomboid `41.78.19`
- Locale `ko/KR`
- Enabled mods visible: Mod Manager, Iris, Cheat Menu : Rebirth
- Environment classification: project default playtest baseline used for Pulse/Echo/Fuse/Nerve/Iris development
- Evidence window: `17:28:16` to `17:35:50` on `2026-05-24`

## Manual Surface Results

Browser surface was observed with six sample screenshots.

Passing/neutral observations:

- `.223 탄약 상자` / `Base.223Box` is visible with description text.
- `스크류드라이버`, `철조망`, and `서류 가방` are visible with description text.
- No raw `publish_state`, `runtime_state`, `source`, `nil`, or table-address token is visible in the supplied screenshots.

Revised contract observations:

- `앞치마` / `Base.Apron_Black` is visible in the default Browser surface. This passes the revised all-item Browser contract because `publish_state = internal_only` is treated as Layer 3 body/state quality, not item-entry suppression, and no raw internal token was reported.
- `빗자루` / `Base.Broom` is visible with generated/tag-derived description text. This passes the revised all-item Browser contract because nil Layer 3 text did not leak as raw `nil`, table address, placeholder, or raw state token.

Accepted closeout scope notes:

- Separate Wiki/detail surface was not captured and is accepted as not separately required for this user-supplied in-game closeout.
- Default bounded baseline was not captured and is accepted as not separately required for this user-supplied in-game closeout.
- Separate Iris-only or vanilla-adjacent environment was not captured; the project default playtest baseline is accepted for this evidence review.

## Console Review

The console confirms Iris loaded and records no Iris Browser Lua stack trace. It does record Pulse/Echo and project-baseline environment findings, including two `LuaAdapter` OnSave errors and a Workshop invalid PNG exception unrelated to the Browser screenshots.

## Closeout Recommendation

Close the supplied evidence as `closed_with_manual_in_game_validation_complete_revised_contract`.

This supports manual in-game validation completion for the supplied playtest evidence under the revised all-item Browser contract.

## Non-Claims

No release readiness, Workshop readiness, B42 readiness, or tooltip completion is claimed.
