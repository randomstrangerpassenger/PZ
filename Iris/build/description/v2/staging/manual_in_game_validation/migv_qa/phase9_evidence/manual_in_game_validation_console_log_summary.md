# MIGV-QA Console Log Summary v0.4

Generated at: `2026-05-23T23:35:17.452+09:00`
Updated at: `2026-05-24T19:33:31+09:00`

Status: `captured_with_environment_findings`

Console evidence:

```text
Iris/Playtest/console.txt
```

## Window

```text
start = 2026-05-24 17:28:16 Asia/Seoul
end = 2026-05-24 17:35:50 Asia/Seoul
game_version = 41.78.19
locale = ko/KR
```

## Counts

```text
total_lines = 2585
error_line_count = 12
pulse_error_line_count = 2
iris_mention_line_count = 96
cheat_menu_mention_line_count = 43
```

## Load Evidence

```text
LOG  : Mod, loading Iris
LOG  : Mod, loading CheatMenuRB
LOG  : Lua, Loading: C:/Users/MW/Zomboid/mods/Iris/media/lua/client/Iris/...
```

The console confirms Iris loaded from `C:/Users/MW/Zomboid/mods/Iris`.

## Notable Errors And Warnings

```text
[Pulse/ERROR] [LuaAdapter] Failed to create event from Lua: OnSave
```

Observed twice:

```text
17:30:39.697
17:35:50.063
```

Other environment findings:

- Echo freeze/fallback warnings.
- `SleepWithFriends/icon.png` invalid PNG exception from a Workshop path.
- `SuburbsDistributions["laboratory"] is broken` appears three times.
- Multiple vanilla/world vehicle distribution warnings.

## Attribution

No Iris Browser Lua stack trace was found in the supplied console. The Pulse/Echo errors and project-baseline environment warnings are recorded as runtime environment observations. Under the revised all-item Browser contract, the screenshots do not show publish visibility failures because `internal_only` and nil Layer 3 text are not item-entry suppression signals.
