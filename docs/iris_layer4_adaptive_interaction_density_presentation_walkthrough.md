# Iris Layer 4 adaptive interaction density presentation Walkthrough

Date: 2026-08-21

Closeout state: `partial`

## 1. Entry gates and owner policy

The execution base matched the approved identity:

- commit `bfdee1c29f82181e15b5924c750e6d44acf41fcc`
- tree `aee455bd36881e1167d454d470300a4f67fa3cf4`
- plan SHA-256 `f38d8bf976ec3b8b3d219e2c5e73090a0566a6113b2d658366f26dbdea116580`
- Gate 3 Walkthrough SHA-256 `a96a3a6e453d8df0f7549450020dd33b58f2f70cb748038c2bee369f88b376af`

The original working tree contained unrelated tracked Layer 3 changes, so this
execution used the isolated `codex/iris-layer4-adaptive` worktree. The fresh
Gate 3 focused test passed with `capability_only=0`, `recipe_only=0`,
`qg_only=3`, `contract_errors=[]`, and `L4-RAT-08=not_applicable`.

The current user message is the explicit repository-owner approval source. The
additive successor packet and fresh tracked seal are:

- `docs/iris_layer4_adaptive_interaction_density_presentation_owner_decision_packet.md`
  - SHA-256 `00a6d04fbdc8a8591d22cf986a0c62e040b0c3c5fd07a1fc9c881c28a1b1850f`
- `Iris/build/description/v2/owner_inputs/iris_layer4_adaptive_interaction_density_presentation/owner_policy_seal.json`
  - SHA-256 `2ed2fda9de08ee71694e7c793ec6db7ba811755263dc0a5b0f7b1d140a2345a5`
- packet/seal commit `3d9cd62294522fc1aaf4d421cdc99b593be8f40c`
- packet/seal tree `f339a7c366c08204760c8ea647b0734493a1732f`

The seal binds `L4-RAT-01` through `L4-RAT-07`, records
`L4-RAT-08=not_applicable`, approves the three exact QG-only relations, and
does not consume or reactivate the historical packet, blocked closeout, or
ignored staging seal. It is not inherited by another plan, base commit/tree,
or Gate 3 subject.

## 2. Implemented change

Change 2's mutation-independent status path was implemented:

- `UseCases._getDescriptionState(fullType)` preserves `available`,
  `verified_empty`, and `fault`, plus machine reason and fallback use.
- authoritative `lookup_miss` and valid positive-empty entries remain distinct
  from router/index/chunk/module/schema failure.
- fallback success remains observable without changing the public
  `getUseCaseLines()` return shape.
- one `IrisItemDetailViewModel.fromItem()` calls the private status lookup once
  and derives both `interactionState` and legacy `useCases` from the same
  ordered arrays.
- status, reason, fallback flag, entry, lines, exclusions, and debug lines are
  exposed only as read-only private ViewModel data.

Changed implementation/test files are:

- `Iris/media/lua/client/Iris/API/UseCases.lua`
- `Iris/media/lua/client/Iris/UI/Detail/IrisItemDetailViewModel.lua`
- `Iris/build/description/v2/tools/build/validate_interaction_presentation_contract.py`
- `Iris/test/test_interaction_presentation_contract.py`
- `Iris/build/description/v2/tests/test_iris_detail_view_model_acceptance.py`
- `Iris/build/description/v2/tests/test_usecase_lazy_lookup_contract.py`
- `Iris/test/lua/detail_view_model_locale_harness.lua`
- `Iris/test/lua/lazy_lookup_acceptance_harness.lua`

Code subject:

- commit `c9f814b66c663647e2e76a5456e436016eb343d4`
- tree `fa41959a45d71d5c1f26f7827e13b99ccad15c2b`

## 3. Gate 5 result and adaptive UI disposition

The installed Recipe projection does not carry the plan-required stable
`recipe_nav_ref.recipe_id`, while no authorized Layer 4
complete-generation/stateless-validation/safe-install contract or validator is
present. The DVF 3.3 installer is not Layer 4 authority. Under Change 9's
required partial branch, the existing renderer and Recipe fallback were
preserved byte-identically and projection-dependent Changes 3–8 and 10 were
deferred.

Consequently, current UI behavior remains the previous flat folded interaction
section. The following approved target behavior is **not implemented or
claimed** in this subject:

- adaptive `0 / 1 / 2~8 / 9+` rendering
- verified-empty/fault user-facing screens
- Recipe/Right-click peer Source sections and total/Source counts
- compact/full disclosure, literal local search, and row-local requirement fold
- full stable-identity/QG-order presentation cutover
- normalized external-row adaptive presentation
- KO/EN adaptive control and requirement localization
- disposable installed-package projection

There is no task-owned generated Layer 4 artifact diff and no installation.
This is not an install PASS; the generated-dependent branch is deferred.

## 4. QG-only, navigation, locale, and unchanged surfaces

The owner-approved new public relations remain exactly:

- `Base.BallPeenHammer / uc.action.construction`
- `Base.GardenSaw / uc.action.wood_cutting`
- `Base.HammerStone / uc.action.construction`

They remain present in QG and were neither removed nor backfilled into legacy.
They are **approved but not newly exposed by this subject**, because the legacy
presentation fallback cutover is deferred.

Recipe navigation, requirement rendering, Source order/count presentation,
search, fold, scroll, and interaction state invalidation behavior were not
changed. The existing KO/EN ViewModel harness confirms locale-independent raw
status projection and one private lookup per build; it is not adaptive UI
localization evidence. Tooltip and Layer 3 files were not modified.

The preserved one-off Item-Page Information Sufficiency Layer 4 input set does
not intersect this subject's runtime facade/ViewModel/test/document diff, so
V7 is `unaffected_snapshot_reference` for this implementation diff. The prior
Gate 3 Walkthrough's separate stale disposition for its QG producer correction
remains historical and is not rewritten.

## 5. Validation results

| Command | Exit | Result |
|---|---:|---|
| `uv run python -m pytest -q Iris/test/test_interaction_presentation_contract.py` | 0 | `14 passed`; fresh seal, Gate 3 `0/0/3`, partial path, preserved renderer/fallback. |
| `uv run python -m pytest -q --round3-contract=all Iris/build/description/v2/tests/test_iris_detail_view_model_acceptance.py` | 0 | `3 passed`; ViewModel/KO-EN standalone Lua acceptance. |
| `uv run python -m pytest -q Iris/build/description/v2/tests/test_usecase_lazy_lookup_contract.py` | 0 | `1 passed`; available/verified-empty/fault/fallback and public-copy compatibility through the existing harness. |
| `uv run python -B Iris/build/quality_gates.py` | 0 | Q1–Q5 PASS, mismatches 0, unexpected/pending 0; timestamp-only report output was not retained. |
| `powershell -ExecutionPolicy Bypass -File .\tools\check_lua_syntax.ps1` | 0 | `Lua syntax validation OK: 128 files`. |
| `git diff --check` | 0 | no whitespace error; line-ending warnings only. |
| `uv run python -m pytest -q --round3-contract=current --round3-enforce-denominator` | 1 | `449 passed, 1 skipped, 7 failed, 15 errors, 120 subtests passed`; V3 FAIL. |

V3 failures were in existing DVF consumer/cutover/closeout setup, historical
protected-surface identities, runtime package parity, Python tooling inventory,
Round 3 reviewed-source count, and residual-surface checks. An initially added
one-off Lua harness also entered regular inventory; it was removed, and its
focused assertions were kept inside existing adopted harnesses. V3 was not
re-run merely for additional confidence, and no new validation authority or
receipt was created.

V5 PZ Kahlua runtime, V6 disposable installed package, and the adaptive manual
UI matrix are `not_applicable(no_subject)` on the plan-selected partial branch.
They are not PASS. No manual Project Zomboid/in-game validation was performed.

## 6. Closeout ceiling

- `validated`: exact owner packet/seal binding; Gate 3 `0/0/3`; Change 2
  status/legacy projection; public facade copy shape; KO/EN ViewModel harness;
  existing lazy lookup/fallback behavior; QG quality gates; Lua syntax; no
  task-owned generated Layer 4 diff; Tooltip/Layer 3/historical artifact
  non-mutation.
- `out_of_scope`: Layer 3/DVF changes, QG fact changes, IPS reassessment,
  Tooltip four-line work, Publish/release/Workshop/deployment readiness.
- `unvalidated_but_in_scope`: V3 current-denominator PASS for this terminal
  subject; adaptive UI/PZ/package/manual axes remain without a current subject
  because Gate 5 deferred them.

Final closeout is `partial`, not `complete` or `implemented_only`. Independent
review is pending. A final owner canonical seal and canonical top-document
promotion were not performed.

The next eligible work requires a repository-owner-authorized Layer 4
complete-generation/stateless-validation/safe-install contract that can carry
stable Recipe identity into the installed projection. After that gate, the
deferred adaptive renderer/cutover, V3, V5, V6, manual UI matrix, independent
review, and final owner canonical seal must be completed on the exact successor
subject.
