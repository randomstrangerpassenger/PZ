# MIGV-QA Closeout v0.4

Generated at: `2026-05-23T23:35:17.452+09:00`
Updated at: `2026-05-24T21:13:43+09:00`

## Closeout Branch

`closed_with_manual_in_game_validation_complete_revised_contract`

## Reason

The v0.4 identity pre-gate passes and static validation passes. User-supplied Project Zomboid playtest evidence exists under `Iris/Playtest/`, and the environment is classified as the project default playtest baseline used during Pulse/Echo/Fuse/Nerve/Iris development.

The earlier Phase 6 expectation was revised: Iris Browser is an all-item Browser, so `internal_only` and nil `text_ko` do not suppress item entries. They classify Layer 3 body/source quality. The supplied in-game screenshots pass this revised contract because the tested items are visible with safe descriptions and no raw internal state, raw nil/table value, or broken placeholder is reported.

Separate Wiki/detail and default bounded baseline captures are accepted as not separately required for this user-supplied manual in-game validation closeout. They remain useful only for future expanded release-readiness QA.

## Validated

- Sealed current runtime hash manifest cited and matched: `790b5689097a8856e6213074fda25b723060073206a7ca44bd26d9f6f08c9171`
- Current deployable chunks match the sealed manifest.
- Row count `2105`, adopted/unadopted `2084/21`.
- Publish split `exposed 1486 / internal_only 600 / missing 19`.
- Missing `publish_state` findings `19`; nil `text_ko` findings `19`.
- Python unittest: `394 tests / OK`.
- Lua syntax: `183 files / OK` after the reverted hide-filter attempt.
- Legacy active/silent current-surface guard: hard-fail current-label occurrence `0`.
- Phase 2 source-axis coverage finalized; limitation_tail/meta_tail candidate count `0` in integrated facts.
- Playtest evidence supplied: enabled-mod screenshot, six Browser screenshots, and console log.
- Browser evidence confirms `.223 탄약 상자`, `스크류드라이버`, `철조망`, `서류 가방`, `앞치마`, and `빗자루` are visible with safe description text.
- No Iris Browser Lua stack trace was found in the supplied console.
- No raw `publish_state`, `runtime_state`, `source`, `nil`, table-address token, or broken placeholder was reported in the supplied screenshots.

## Revised Contract Result

- `앞치마` / `Base.Apron_Black` is visible in the Browser while sealed `publish_state = internal_only`; this is accepted because item-entry visibility is separate from Layer 3 body/source quality.
- `빗자루` / `Base.Broom` is visible with generated/tag-derived description text while sealed Layer 3 `text_ko = nil`; this is accepted because raw nil/table/placeholder/state tokens are not exposed.
- A runtime hide-filter attempt was reverted because hiding these items would conflict with Iris all-item Browser semantics and existing junk/no-use item exposure.

## Completed Scope

- Current runtime authority is sealed through the existing current runtime baseline evidence path/hash.
- User-supplied in-game validation evidence is accepted as complete for this round.
- Browser item-entry and description behavior passes the revised all-item contract.
- Project default playtest baseline is accepted as the practical in-game validation environment.

## Non-Claims

- No release readiness.
- No Workshop readiness.
- No B42 readiness.
- No tooltip completion.
- No full Iris release QA completion.
- No packaging, deployment, release note, or Workshop publish completion.

## Next Required Action

None for this manual in-game validation closeout.
