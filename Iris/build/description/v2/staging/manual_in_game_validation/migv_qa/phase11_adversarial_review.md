# MIGV-QA Adversarial Review v0.4

Updated at: `2026-05-24T21:13:43+09:00`

## 1. Verdict

PASS - MANUAL IN-GAME VALIDATION COMPLETE, REVISED ALL-ITEM CONTRACT

---

## 2. Executive Summary

The v0.4 identity pre-gate is corrected, Phase 2 source-axis coverage is finalized, and static validation is clean. The supplied playtest evidence is classified as the project default playtest baseline used during Pulse/Echo/Fuse/Nerve/Iris development.

The earlier Phase 6 assumption was corrected: `internal_only` and nil `text_ko` are Layer 3 body/state quality signals, not Browser item-entry suppression signals. Iris is an all-item Browser and already exposes junk/no-use item entries, so `앞치마` and `빗자루` being searchable is expected. The screenshots show safe Browser descriptions and no raw `nil`, table address, placeholder, or raw state token exposure.

This review accepts the user-supplied in-game evidence set as complete for manual in-game validation closeout under the revised contract. Separate Wiki/detail and default bounded baseline captures are no longer blockers for this closeout; they can be rerun later only for expanded release-readiness QA.

---

## 3. Critical Issues

No critical issue remains inside the accepted manual in-game validation closeout scope.

Resolved issue:

* Earlier runtime hiding was rejected and reverted because it would have hidden item entries in conflict with Iris all-item Browser semantics.
* Phase 6 now validates safe item-entry display and raw token suppression, not item disappearance.

---

## 4. Non-Critical Issues

* The console includes Pulse/Echo and project-baseline environment findings, including `LuaAdapter` OnSave errors and a Workshop invalid PNG exception. No Iris Browser Lua stack trace was found in the supplied console.
* Separate Wiki/detail and default bounded baseline captures were not supplied; they are accepted as not separately required for this user-supplied in-game closeout.
* Stale selection/reselection cannot be proven from still screenshots alone.

---

## 4A. Root Cause Reclassified

Code inspection found that Browser item search/list/detail is broader than sealed Layer 3 publish visibility:

* `Iris/media/lua/client/Iris/UI/Browser/IrisBrowserQuery.lua` searches `cache.itemsByFullType`, which is built from Project Zomboid script items rather than filtered by the sealed Layer 3 publish contract.
* `Iris/media/lua/client/Iris/API/Description.lua` generates Browser description text through `Tags.getTags(fullType)` and `IrisDescGenerator.generate(...)`.
* That path does not gate on `IrisLayer3DataChunks[fullType].publish_state` or `text_ko`.

This is compatible with Iris as an all-item Browser. The correct contract is:

* item entries may remain discoverable,
* Layer 3 body availability/quality remains separately classified,
* raw internal state tokens, raw nil/table values, and broken placeholders must not leak to users.

---

## 5. Scope Review

### Scope Drift

No runtime source mutation is retained for this review. No release-scope expansion was introduced.

### Accepted Scope

The project default playtest baseline is accepted as the practical in-game validation environment for this evidence review. The supplied screenshots and console are accepted as the closeout evidence set.

### Explicitly Out Of Scope Consistency

Alt tooltip validation remains deferred and out of scope.

---

## 6. Validation Review

### Validated

* Browser screenshots exist for `.223 탄약 상자`, `스크류드라이버`, `철조망`, `서류 가방`, `앞치마`, and `빗자루`.
* `앞치마` item-entry visibility is accepted under the revised all-item Browser contract.
* `빗자루` item-entry visibility with generated/tag-derived description text is accepted under the revised all-item Browser contract.
* No raw `publish_state`, `runtime_state`, `source`, `nil`, table-address token, or broken placeholder was reported in the supplied screenshots.
* No Iris Browser Lua stack trace was found in the supplied console.
* Lua syntax validation passed after the reverted hide-filter attempt.

### Validation Ceiling Risk

Controlled: current artifacts claim manual in-game validation completion under the revised contract. They do not claim release readiness, Workshop readiness, B42 readiness, or tooltip completion.

---

## 7. Governance Review

### Philosophy.md Compliance

The screenshots show Iris as a Lua wiki-style information surface. All-item discoverability is consistent with Iris as a tool for item use inspection.

### Runtime / Build-Time Separation

Preserved; runtime artifacts were observed, not regenerated.

### FAIL-LOUD Preservation

Preserved. The contract was corrected explicitly instead of silently converting a mismatched expectation into a runtime hide rule.

---

## 8. Risk Surface Review

### Authority Surface

No top-doc Branch A addenda were written.

### Runtime Behavior Surface

Browser visibility is accepted as item-entry visibility, not sealed Layer 3 body publication.

### Compatibility Surface

Current evidence is the project default playtest baseline and includes Cheat Menu : Rebirth.

### Public-Facing Output Surface

The supplied screenshots do not show raw internal/finding state leakage.

---

## 9. Remaining Work Outside This Closeout

1. Release-readiness QA can later capture separate Wiki/detail evidence if desired.
2. Release-readiness QA can later capture default bounded baseline evidence if desired.
3. Alt tooltip validation stays in its separate tooltip-system round.

---

## 10. Final Recommendation

PASS - MANUAL IN-GAME VALIDATION COMPLETE, REVISED ALL-ITEM CONTRACT

Close this evidence set as `closed_with_manual_in_game_validation_complete_revised_contract`. Do not claim release readiness from this evidence alone.
