# Iris Refactor Baseline - 20260512

Approved plan source: `C:\Users\MW\Downloads\1.txt` (`최종 리팩토링 로드맵 v4.1`)

This baseline records the Pre-Gate remeasurement required before execution.

| Gate | 줄 수 / 함수 수 | 모듈 분리 여부 | 결론 |
|---|---:|---|---|
| PG-1 `IrisBrowser.lua` | 122 / 11 | `IrisBrowserLayout`, `IrisBrowserDetail`, `IrisBrowserListController`, `IrisBrowserInteractionRenderer` all exist | valid measurement; T3-A Browser UI split is stale as a full task |
| PG-2 `IrisMain.lua` bootstrap | 177 / 11 | `INIT_MODULES` and `runModuleSpec()` exist | valid measurement; T1-C is not applicable |
| PG-3 `compose_layer3_text.py` | 250 / 7 | all 6 split modules exist: `compose_layer3_io.py`, `compose_layer3_blocks.py`, `compose_layer3_identity.py`, `compose_layer3_body_profile.py`, `compose_layer3_item.py`, `compose_layer3_render.py` | valid measurement; T3-B is stale as a full task |
| PG-4 Browser KO fallback / boot logs | `IrisBrowser.lua` 122 / 11, `AIrisBoot.lua` 16 / 0 | `return "KO"` and inline `TRANSLATIONS_KO` not found in `IrisBrowser.lua`; `AIrisBoot.lua` still has `!!!!!` banner prints | partial; T0-C targets `AIrisBoot.lua` only, T1-A does not need inline `TRANSLATIONS_KO` removal |
| PG-5 `IrisUseCaseDescriptions.lua` responsibility mix | 108 / 0 | chunk manifest and `_requirementsLookup` coexist in the facade; chunks also contain `recipe_requirements` payloads | valid; T2-B remains actionable |
| PG-6 `tools/build/` script count | 273 script files | build scripts are already broad and partially manifest-documented | partial; P1 needs separate manifest-sizing round, not T0 scope |
| PG-7 T1-A regression checklist | n/a | `Iris/_docs/refactor/t1a_regression_checklist.md` missing | partial; PG-7W is required before T1-A |

## Scope Adjustments

- T3-A is downgraded to no-op for this execution because all four Browser split modules already exist.
- T3-B is downgraded to no-op for this execution because `compose_layer3_text.py` is at 250 lines and all six target split modules exist.
- T0-C does not include Browser `return "KO"` cleanup because that pattern is absent.
- T1-A is blocked until PG-7W creates the Browser/Wiki Korean display regression checklist.
- T2-B remains valid because generated chunk manifest loading and recipe requirements lookup still coexist in `IrisUseCaseDescriptions.lua`.

## Validation Ceiling

- Validated: static file existence, line/function counts, targeted pattern searches, and `tools/build` script count.
- Out of scope: in-game runtime validation, packaging, release readiness, and T1-T3 implementation.
- Unvalidated but in scope: T0 implementation smoke after code changes.
