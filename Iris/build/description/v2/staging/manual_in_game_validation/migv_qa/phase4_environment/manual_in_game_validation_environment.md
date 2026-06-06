# MIGV-QA Environment Manifest v0.4

Generated at: `2026-05-23T23:35:17.452+09:00`
Updated at: `2026-05-24T21:13:43+09:00`

## Status

`pass_project_default_playtest_baseline_accepted`

Manual Project Zomboid evidence was supplied under:

```text
Iris/Playtest/
```

The observed run is the project default playtest baseline used during Pulse, Echo, Fuse, Nerve, and Iris development. It is not an arbitrary modded compatibility run. The enabled mod screenshot shows:

```text
Mod Manager
Iris
Cheat Menu : Rebirth
```

## Observed Environment

- Game version/build: `41.78.19`
- Locale: `ko`, `KR`
- Evidence window: `2026-05-24 17:28:16` to `2026-05-24 17:35:50` Asia/Seoul, derived from `Iris/Playtest/console.txt`
- Console path in evidence packet: `Iris/Playtest/console.txt`
- Visual evidence root: `Iris/Playtest/`
- Test character: `Jimmy Hollis`, visible in screenshots
- Save/world evidence: console reports `WorldLoadEvent: 24-05-2026_05-28-56`

## Vanilla-Adjacent / Iris-Only Environment Record

`accepted_not_separately_required_for_user_supplied_in_game_closeout`

No separate Iris-only or vanilla-adjacent enabled-mod screenshot was supplied. The project default playtest baseline is accepted as the practical in-game validation environment for this closeout.

## Project Default Playtest Baseline Record

`observed`

Evidence:

```text
Iris/Playtest/Enabled_modlist.jpg
```

Enabled mods visible in the screenshot:

```text
Mod Manager
Iris
Cheat Menu : Rebirth
```

## Console Summary

The supplied console confirms Iris runtime load:

```text
LOG  : Mod, loading Iris
LOG  : Lua, Loading: C:/Users/MW/Zomboid/mods/Iris/...
```

Console findings:

```text
total_lines = 2585
error_line_count = 12
pulse_error_line_count = 2
iris_mention_line_count = 96
cheat_menu_mention_line_count = 43
```

Notable project-baseline environment findings:

- Cheat Menu Rebirth is loaded.
- `SleepWithFriends/icon.png` is not a valid PNG.
- `SuburbsDistributions["laboratory"] is broken` appears three times.
- Multiple vehicle distribution warnings appear.

Notable Pulse/Echo findings:

- `[Pulse/ERROR] [LuaAdapter] Failed to create event from Lua: OnSave` appears at `17:30:39.697` and `17:35:50.063`.
- Echo fallback/freeze warnings appear.

No Iris Browser Lua stack trace was observed in the supplied console. The Pulse/Echo errors are recorded as environment/runtime observations, not as DVF 3-3 Browser text rendering proof.

## Validation

```text
environment_manifest_present = true
vanilla_adjacent_environment_recorded = accepted_not_separately_required
project_default_playtest_baseline_recorded = true
console_capture_ready = true
visual_evidence_capture_ready = true
test_save_entered = true
Iris_UI_entered = true
```

## Classification

Phase 4 is `pass_project_default_playtest_baseline_accepted`: the project default playtest baseline and console window are recorded and accepted for this manual in-game validation closeout.
