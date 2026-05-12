# Iris Phase 4 English Playtest Validation

Date: 2026-05-06

Archived session logs:

- `Iris/_docs/refactor/playtest_evidence/2026-05-06-en/console.txt`
- `Iris/_docs/refactor/playtest_evidence/2026-05-06-en/DebugLog.txt`
- `Iris/_docs/refactor/playtest_evidence/2026-05-06-en/echo_report_20260506_073051.json`

## Verdict

English runtime smoke validation is acceptable as a Phase 4 baseline with one
qualification: the process starts with OS/JVM language `ko`, then the game
translator switches to `EN`. This validates the in-session English UI/resource
path, not a cold boot where `user.language=en` from process start.

## Log Evidence

Language and translation:

- `user.language=ko`
- initial `translator: language is KO`
- later `translator: language is EN`

Iris boot:

- Iris loaded once before the language switch and once after the English
  translator switch.
- Both boot sequences reached:
  - `IRIS BOOTSTRAP: START LOAD`
  - `IRIS BOOTSTRAP: IrisMain loaded successfully`
  - `[Iris] Bootstrap complete`

Iris runtime modules loaded after the English translator switch:

- `IrisLayer3Data.lua`
- `IrisUseCaseDescriptions.lua`
- `UseCaseDescriptions/Chunk001.lua` through `Chunk009.lua`
- `IrisTranslationLoader.lua`
- `IrisBrowser.lua`
- `IrisAltTooltip.lua`
- `IrisContextMenu.lua`
- `IrisWikiPanel.lua`
- `IrisWikiSections.lua`

Error scan:

- `Iris` log hits: 134
- `Lua error`: 0
- `stack traceback`: 0
- `ExceptionLogger`: 0
- `attempt to`: 0
- `nil value`: 0
- Iris-specific `ERROR` / `WARN`: 0 matched by log scan

Echo/Pulse runtime:

- Echo report quality: 100
- performance score: 100.0
- tick contract: OK
- phase status: OK
- total freezes in report: 2
- fallback ticks used: true, timing not contaminated

## Checklist Result

| Area | Status | Basis |
|---|---|---|
| Boot | PASS | Iris loaded and bootstrap completed after EN translator switch |
| Boot log | PASS_WITH_NOTE | Iris boot is clean; session contains non-Iris environment noise |
| Tooltip | OBSERVED | User completed English playtest; no tooltip interaction marker in logs |
| Tooltip off | OBSERVED | User completed English playtest; no tooltip interaction marker in logs |
| Right-click | OBSERVED | User completed English playtest; no context-menu interaction marker in logs |
| Right-click detail | OBSERVED | User completed English playtest; no detail-open marker in logs |
| Browser open/search/category/list/detail | OBSERVED | User completed English playtest; browser modules loaded after EN switch |
| Recipe requirements | OBSERVED | User completed English playtest; requirement renderer modules loaded |
| Right-click capability | OBSERVED | User completed English playtest; context menu modules loaded |
| Layer 3 description block | OBSERVED | Layer 3 and use-case description chunks loaded after EN switch |
| KO fallback | ALREADY_COVERED | Korean set covers KO path |
| EN fallback | PASS_WITH_NOTE | EN translator switch confirmed; no Iris translation error detected |
| Error logging | PASS_WITH_EXTERNAL_NOISE | No Iris error spam; non-Iris Echo/Pulse and vanilla warnings exist |

## Non-Iris Noise

The English session contains the same class of unrelated environment noise as
the Korean run:

- Echo freeze warnings during startup/shutdown
- Echo fallback tick emitter activation
- Pulse LuaAdapter `OnSave` event creation error on quit
- vanilla/mod warnings such as missing FMOD events, vehicle distribution
  warnings, broken `SuburbsDistributions["laboratory"]`, and mannequin zone
  warning

These were not tied to Iris by the log scan.

## Phase 4 Baseline Status

Korean and English playtest baselines are both recorded. The remaining caveat
for future runtime refactors is that UI flow success is still based on user
observation; the current logs verify language path, module loading, and absence
of Iris Lua exceptions.
