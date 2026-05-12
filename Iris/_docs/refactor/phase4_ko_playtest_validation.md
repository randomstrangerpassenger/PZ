# Iris Phase 4 Korean Playtest Validation

Date: 2026-05-06

Archived session logs:

- `Iris/_docs/refactor/playtest_evidence/2026-05-06-ko/console.txt`
- `Iris/_docs/refactor/playtest_evidence/2026-05-06-ko/DebugLog.txt`
- `Iris/_docs/refactor/playtest_evidence/2026-05-06-ko/echo_report_20260506_072312.json`

## Verdict

Korean runtime smoke validation is acceptable as a Phase 4 baseline with one
qualification: visual UI behavior is user-observed, not machine-verifiable from
the available logs.

## Log Evidence

Language and translation:

- `user.language=ko`
- `translator: language is KO`
- `Attempting to load translation: KO`

Iris boot:

- `loading Iris`
- `IRIS BOOTSTRAP: START LOAD`
- `IRIS BOOTSTRAP: IrisMain loaded successfully`
- `[Iris] Bootstrap complete`

Iris runtime modules loaded:

- `IrisLayer3Data.lua`
- `IrisUseCaseDescriptions.lua`
- `UseCaseDescriptions/Chunk001.lua` through `Chunk009.lua`
- `IrisAPI.lua`
- `IrisTranslationLoader.lua`
- `IrisBrowser*.lua`
- `IrisAltTooltip.lua`
- `IrisTooltipSummary.lua`
- `IrisContextMenu.lua`
- `IrisWikiPanel.lua`
- `IrisWikiSections.lua`

Error scan:

- `Iris` log hits: 67
- `Lua error`: 0
- `stack traceback`: 0
- `ExceptionLogger`: 0
- `attempt to`: 0
- `nil value`: 0

Echo/Pulse runtime:

- Echo report quality: 100
- tick contract: OK
- phase status: OK
- fallback ticks used: true, timing not contaminated
- total freezes in report: 2

## Checklist Result

| Area | Status | Basis |
|---|---|---|
| Boot | PASS | Iris loaded and bootstrap completed with no Iris Lua exception |
| Boot log | PASS_WITH_NOTE | Iris boot banners are visible but concise; no debug stack spam from Iris |
| Tooltip | OBSERVED | User completed Korean playtest; no tooltip interaction marker in logs |
| Tooltip off | OBSERVED | User completed Korean playtest; no tooltip interaction marker in logs |
| Right-click | OBSERVED | User completed Korean playtest; no context-menu interaction marker in logs |
| Right-click detail | OBSERVED | User completed Korean playtest; no detail-open marker in logs |
| Browser open/search/category/list/detail | OBSERVED | User completed Korean playtest; browser modules loaded, but UI flow has no log marker |
| Recipe requirements | OBSERVED | User completed Korean playtest; requirement renderer modules loaded |
| Right-click capability | OBSERVED | User completed Korean playtest; context menu modules loaded |
| Layer 3 description block | OBSERVED | Layer 3 and use-case description chunks loaded |
| KO fallback | PASS | KO translation load confirmed; no Iris translation error detected |
| EN fallback | NOT_TESTED_IN_KO_SET | Requires English playtest or explicit missing-key case |
| Error logging | PASS_WITH_EXTERNAL_NOISE | No Iris error spam; non-Iris Echo/Pulse and vanilla warnings exist |

## Non-Iris Noise

The session contains unrelated warnings/errors that should not block Iris
Phase 4 entry by themselves:

- Echo freeze warnings during startup/shutdown
- Echo fallback tick emitter activation
- Pulse LuaAdapter `OnSave` event creation error on quit
- vanilla/mod warnings such as missing FMOD events, model/texture warnings,
  broken `SuburbsDistributions["laboratory"]`, and mannequin zone warning

These are useful environment notes, but the scan did not tie them to Iris.

## Follow-up For English Playtest

Before starting the English pass, preserve this Korean `console.txt` and
DebugLog if exact comparison is needed. The English validation should confirm:

- `user.language=en` or equivalent English setting
- translation loader attempts English resources or falls back cleanly
- no Iris-specific Lua exception
- the same observed UI flows remain functional
