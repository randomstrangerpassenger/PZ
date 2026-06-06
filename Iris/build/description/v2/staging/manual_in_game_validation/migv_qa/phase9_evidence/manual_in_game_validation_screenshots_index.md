# MIGV-QA Screenshots Index v0.4

Generated at: `2026-05-23T23:35:17.452+09:00`
Updated at: `2026-05-24T21:13:43+09:00`

Status: `captured_user_supplied_in_game_validation_complete`

Evidence root:

```text
Iris/Playtest/
```

## Environment

| File | Observation |
|---|---|
| `Iris/Playtest/Enabled_modlist.jpg` | New game setup screen shows enabled mods: Mod Manager, Iris, Cheat Menu : Rebirth. This is the project default playtest baseline used for Pulse/Echo/Fuse/Nerve/Iris development, not an arbitrary modded compatibility run. |

## Browser Surface

| File | Sample | Observation | Result |
|---|---|---|---|
| `Iris/Playtest/.223ammobox.jpg` | `.223 탄약 상자` / `Base.223Box` | Browser search/detail displays exposed sample text. | pass for exposed display |
| `Iris/Playtest/Screwdriver.jpg` | `스크류드라이버` / `Base.Screwdriver` | Browser search/detail displays sample text. | observed |
| `Iris/Playtest/Barbedwire.jpg` | `철조망` / `Base.BarbedWire` | Browser search/detail displays sample text. | observed |
| `Iris/Playtest/Briefcase.jpg` | `서류 가방` / `Base.Briefcase` | Browser search/detail displays sample text. | observed |
| `Iris/Playtest/Apron.jpg` | `앞치마` / `Base.Apron_Black` | Browser search/detail displays the item entry and safe description text; revised contract treats `internal_only` as Layer 3 body/state quality, not item-entry suppression. | pass |
| `Iris/Playtest/Broom.jpg` | `빗자루` / `Base.Broom` | Browser search/detail displays the item entry and safe generated/tag-derived description text; no raw nil/table/placeholder/state token was reported. | pass |

## Missing Visual Evidence

- No separate Wiki/detail panel screenshot; accepted as not separately required for this user-supplied in-game closeout.
- No Browser-to-Wiki transition screenshot; accepted as not separately required for this user-supplied in-game closeout.
- No Iris-disabled vanilla/default bounded baseline screenshot; accepted as not separately required for this user-supplied in-game closeout.
- No separate Iris-only or vanilla-adjacent enabled-mod screenshot; the project default playtest baseline is accepted for this evidence review.
