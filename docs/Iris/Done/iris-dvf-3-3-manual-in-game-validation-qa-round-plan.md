# Iris DVF 3-3 Manual In-Game Validation QA Round Plan

> 상태: Draft v0.4-plan  
> 기준일: 2026-05-23  
> 상위 기준: `docs/Philosophy.md`, `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`  
> authority input: `ROADMAP - Iris DVF 3-3 Manual In-Game Validation QA Round (MIGV-QA)` (2026-05-21 user-provided synthesis)  
> authority input: `Iris DVF 3-3 Current Runtime Baseline Seal Round` closeout (2026-05-23), branch `sealed_with_inventory_findings`; MIGV-QA Phase 1 identity pre-gate must consume sealed current runtime baseline evidence, not historical staged hash evidence.  
> review input: `Plan Review - Iris DVF 3-3 Manual In-Game Validation QA Round (MIGV-QA)` v0.1 FAIL synthesis feedback (2026-05-21), Critical 1-2, Important 1-4, and Minor M-A through M-E incorporated in v0.2.  
> review input: `Plan Review - Iris DVF 3-3 MIGV-QA v0.2` PASS feedback with required I-1 correction (2026-05-22), prior staged-derivation identity boundary incorporated in v0.3 and superseded by the v0.4 current-runtime seal rebase.  
> rebase note: v0.4 supersedes the v0.3 staged/body_plan derivation gate with the sealed current deployable runtime baseline readpoint: `current_runtime_hash_manifest.json` sha256 `790b5689097a8856e6213074fda25b723060073206a7ca44bd26d9f6f08c9171`. Historical staged hash `0390272b...` is comparison-only and is not the current identity gate.  
> 계획 형식: `docs/PLAN_TEMPLATE.md`  
> template attestation: this plan follows the 1-12 section structure in `docs/PLAN_TEMPLATE.md`; the template file is present under `docs/`; the template is a project planning form, not semantic authority over `docs/Philosophy.md`, `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, or `docs/ROADMAP.md`.  
> 실행 상태: planning authority only. 이 문서는 mutation-free manual in-game validation QA round를 열기 위한 실행 계획이며, 작성 시점에는 canonical artifact, runtime Lua, rendered text, source decisions, staged hash, deployed state, release state, top-doc closeout state를 변경하지 않는다.

---

## 1. Objective

이번 execution plan의 목적은 DVF 3-3 `body_plan` output이 실제 Project Zomboid 인게임 사용자 표면에서 계약대로 표시되는지 확인하는 mutation-free observer round의 실행 범위와 증거 계약을 고정하는 것이다.

핵심 objective:

```text
ready_for_in_game_validation must not be read as deployed closeout
chunk deployable authority must be linked to the sealed current runtime baseline
Browser / Wiki-detail / default bounded user-facing baseline must be manually observed
publish visibility must pass both exposed and internal_only directions
finding rows must not render as broken nil/raw-placeholder bodies
canonical artifacts must not be regenerated or changed during QA
```

성공 시 최대 선언 가능 범위:

```text
closed_with_dvf_3_3_deployed_closeout
manual in-game validation passed for the validated DVF 3-3 body_plan surfaces
```

성공해도 선언 금지:

```text
Iris ready_for_release
Workshop ready
B42 ready
Tooltip complete
Tooltip system validation or completion
Full Iris QA complete
All user-facing Iris surfaces release-ready
packaging / deployment / release note / Workshop publish complete
```

DVF 3-3 deployed closeout may be used as an input for opening a separate tooltip-system round, but this plan does not validate, complete, or unblock that round by itself.

이번 round의 검증 질문은 다음 하나로 제한한다.

```text
승인된 body_plan output이 실제 게임 표면에서 깨지지 않고, 계약대로 표시되는가?
```

---

## 2. Scope

This round is a manual in-game validation, identity pre-gate, evidence packaging, and closeout classification round. It is not a build artifact regeneration round, content rewrite round, release readiness round, or Workshop packaging round.

In scope:

* Deployable authority identity pre-gate before launching the game.
* Round-local QA artifact root:

```text
Iris/build/description/v2/staging/manual_in_game_validation/migv_qa/
```

* Static confirmation that deployable chunk authority carries the sealed runtime/publish identity and finding inventory:

```text
row_count = 2105
adopted = 2084
unadopted = 21
publish_state.exposed = 1486
publish_state.internal_only = 600
publish_state.missing = 19
text_ko.present_non_empty = 2086
text_ko.nil = 19
quality_state.missing = 2105
runtime path distribution = supporting sample-axis input only; not a sealed current hard gate unless re-derived in Phase 2
sealed current runtime evidence = current_runtime_hash_manifest.json sha256 790b5689097a8856e6213074fda25b723060073206a7ca44bd26d9f6f08c9171
historical staged parity hash 0390272b... = comparison-only, not current identity gate
```

* Static confirmation that deployable authority is:

```text
IrisLayer3DataChunks.lua manifest + Chunk001..011.lua
```

and not monolith `IrisLayer3Data.lua`.

* QA harness and sample matrix construction across these axes:

```text
runtime_state
publish visibility
body source
text shape
chunk boundary
consumer surface
```

* Static pre-run validation before manual game launch.
* In-game environment setup and manifest recording for at least:

```text
minimal Iris-only or vanilla-adjacent environment
actual-use-like modded environment
```

* Manual surface validation for:

```text
Browser surface
Wiki/detail surface, category-subcategory-item-description hierarchy
default bounded baseline fixed in opening note:
  Iris-disabled vanilla behavior preservation + right-click entrypoint baseline only
```

* Deferred out-of-scope reference:

```text
Alt key Iris tooltip above vanilla tooltip, max 4 lines
```

Alt tooltip validation belongs to the later tooltip-system round unless a separate sealed decision reopens it. This MIGV-QA plan must not make Alt tooltip pass a hard gate for DVF 3-3 deployed closeout.

* Publish visibility two-sided check:

```text
exposed sample appears on intended user-facing surfaces
internal_only sample may appear as an item entry but does not leak raw internal state tokens or broken placeholders
unadopted sample may appear as an item entry but does not appear as broken placeholder body
missing publish_state / nil text_ko finding sample follows the revised all-item Browser contract without raw nil/table/placeholder exposure
```

* Runtime consumer baseline preservation after QA.
* Negative invariant verification:

```text
monolith absent / 0 loads
manifest 1 load
chunk files 11 loads
hashes unchanged
legacy active/silent current-surface reentry absent
mutation count = 0
```

* Evidence packaging, walkthrough, hard gate, adversarial review, and branch-accurate closeout classification.

### Explicitly Out Of Scope

* DVF 3-3 body text rewrite.
* `body_plan` section structure mutation.
* Compose profile mutation.
* Resolver logic mutation.
* `adopted / unadopted` reclassification.
* `internal_only / exposed` reclassification.
* `quality_state` or `publish_state` recomputation.
* Lua chunk regeneration.
* `body_plan` recomposition.
* Runtime Lua architecture changes.
* Tooltip system implementation.
* Alt tooltip surface validation.
* B42 porting.
* Workshop packaging or release preparation.
* External mod compatibility sweep.
* Multiplayer validation.
* Long-session validation.
* 2105-row exhaustive click-through validation.
* User-friendly text polishing or Korean prose mutation.
* Complete-removal cleanup path.
* Prior metadata migration adapter removal debt.

---

## 3. Non-Goals

This plan does not attempt to:

* Prove full runtime equivalence.
* Prove every one of the 2105 rows by manual click-through.
* Reopen staged/static closeout decisions.
* Treat refactor v4.1 targeted in-game smoke as manual surface QA.
* Treat static validation pass as deployed closeout.
* Change source decisions, facts, rendered text, runtime state, quality state, or publish state.
* Promote internal/debug/admin surfaces into default user-facing contract.
* Fix runtime bugs found during QA in the same round.
* Classify awkward phrasing as a content defect requiring mutation.
* Convert modded-environment-only behavior into an Iris defect without minimal-environment reproduction evidence.
* Claim release readiness, Workshop readiness, or B42 readiness.

---

## 4. Assumptions

Authority assumptions:

* `docs/Philosophy.md` is the top authority.
* Iris remains a 100% Lua wiki-style information module.
* Iris output must avoid interpretation, recommendation, and comparison.
* `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, and `docs/ROADMAP.md` are current governance readpoints.
* Current DVF 3-3 state is `ready_for_in_game_validation`, not `deployed_closeout`.

Runtime/data assumptions:

* Current runtime payload canonical enum is `adopted / unadopted`.
* Legacy `active / silent` is diagnostic/import/historical read-only alias only.
* Layer 3 runtime deployable authority is chunk manifest plus chunk files.
* Monolith `IrisLayer3Data.lua` is not deployable authority and must not be auto-loaded.
* Current deployable runtime baseline is sealed as `sealed_with_inventory_findings` by the DVF 3-3 Current Runtime Baseline Seal Round.
* The current identity pre-gate authority is `Iris/build/description/v2/staging/dvf_3_3_current_runtime_baseline_seal_round/reports/current_runtime_hash_manifest.json` sha256 `790b5689097a8856e6213074fda25b723060073206a7ca44bd26d9f6f08c9171`.
* Historical staged hash `0390272b...` is comparison-only and must not be used as the current identity gate.
* Current sealed publish split is `exposed 1486 / internal_only 600 / missing 19`.
* Current sealed finding inventories are missing `publish_state 19` and nil `text_ko 19`.
* Runtime Lua is a render-only consumer.
* Compose writer remains the single writer for canonical output.

QA assumptions:

* The round is observer-only and mutation-free.
* QA findings are recorded before any bugfix work is opened.
* Console log readpoint is recorded before validation begins.
* Screenshots, screen recordings, or structured visual notes are accepted as evidence when indexed.
* Static validation is required but not sufficient for deployed closeout.
* Manual in-game validation is sample-matrix-based across contract axes, not 2105-row exhaustive clicking.

Validation assumptions:

* Python and Lua validation may be claimed only when the exact command exits code `0`.
* Missing tools or inaccessible game/runtime environment produce `blocked_*`, not pass.
* MIGV-QA opening decision must select the sealed current runtime baseline identity-link mode before this round starts:

```text
mode_current_runtime_baseline_seal_consume
```

* In `mode_current_runtime_baseline_seal_consume`, Phase 1 cites the sealed current runtime evidence path/hash and remains confirm-only.
* Phase 1 must not derive a new parity authority during MIGV-QA.
* Chunk topology-only evidence, including v4.1 load-count smoke evidence, is supporting context only and is insufficient without the sealed current runtime baseline evidence.
* If the opening decision still requires `0390272b...` as the current gate, MIGV-QA is blocked before manual QA until the plan/opening note is corrected.
* If the sealed current runtime evidence is missing, mutated, or not cited by path/hash, MIGV-QA is blocked before manual QA.

---

## 5. Repository Areas Affected

### Code

None planned.

Read-only or validation-only code/script areas:

```text
Iris/build/description/v2/tools/**
Iris/build/description/v2/tests/**
Iris/media/lua/client/Iris/Data/**
tools/check_lua_syntax.ps1
```

If a missing identity/reporting helper is required, it must be opened as a separate implementation round or explicitly amended into this plan before code mutation.

### Docs

This plan document:

```text
docs/Iris/iris-dvf-3-3-manual-in-game-validation-qa-round-plan.md
```

Conditional closeout addenda after Branch A only:

```text
docs/DECISIONS.md
docs/ARCHITECTURE.md
docs/ROADMAP.md
```

Top-doc updates must be append-only or current-readpoint additions. Historical bodies must not be rewritten.

### Config

None planned.

Game/client environment state is recorded as QA evidence, not repository config mutation.

### Generated Artifacts

Round-local QA evidence root:

```text
Iris/build/description/v2/staging/manual_in_game_validation/migv_qa/
```

Planned deliverables:

```text
phase1_identity_pregate/deployable_authority_identity_report.json
phase1_identity_pregate/deployable_authority_identity_report.sha256
phase1_identity_pregate/opening_scope_note.md
phase2_harness/validation_harness.md
phase2_harness/manual_in_game_validation_sample_matrix.json
phase2_harness/manual_in_game_validation_checklist.md
phase3_static_prerun/static_prerun_validation_report.json
phase4_environment/manual_in_game_validation_environment.md
phase4_environment/enabled_mods_minimal.md
phase4_environment/enabled_mods_modded.md
phase5_surface/surface_display_result.json
phase5_surface/browser_surface_result.json
phase5_surface/wiki_detail_result.json
phase5_surface/default_surface_result.json
phase6_publish/publish_visibility_two_sided_result.json
phase7_baseline/runtime_baseline_preservation_result.json
phase8_negative/negative_invariant_report.json
phase9_evidence/manual_in_game_validation_results.json
phase9_evidence/manual_in_game_validation_console_log_summary.md
phase9_evidence/manual_in_game_validation_screenshots_index.md
phase9_evidence/manual_in_game_validation_walkthrough.md
phase10_hard_gate/phase10_hard_gate_report.json
phase11_adversarial_review.md
phase12_closeout/closeout_classification.json
phase12_closeout/closeout.md
```

---

## 6. Planned Changes

### Change 1 - Phase 1 deployable authority identity pre-gate

Purpose:

Prove before game launch that the game-loaded chunk deployable authority matches the sealed current runtime baseline that MIGV-QA is allowed to consume.

Files:

```text
Iris/build/description/v2/staging/manual_in_game_validation/migv_qa/phase1_identity_pregate/deployable_authority_identity_report.json
Iris/build/description/v2/staging/manual_in_game_validation/migv_qa/phase1_identity_pregate/deployable_authority_identity_report.sha256
Iris/build/description/v2/staging/manual_in_game_validation/migv_qa/phase1_identity_pregate/opening_scope_note.md
```

Implementation Notes:

* Before the MIGV-QA opening decision is sealed, choose the Phase 1 mode:

```text
mode_current_runtime_baseline_seal_consume:
  Existing sealed evidence from DVF 3-3 Current Runtime Baseline Seal Round
  proves the current deployable runtime file identity and payload inventory.
  Phase 1 cites path/hash and confirms it.
```

* Phase 1 is confirm-only. It must not invent a new parity authority during MIGV-QA.
* Do not treat v4.1 chunk externalization/topology evidence as current identity authority.
* Do not treat historical staged hash `0390272b...` as the current identity gate.
* Confirm chunk manifest and `Chunk001..011.lua` presence.
* Confirm row count `2105`, `adopted 2084`, `unadopted 21`.
* Confirm publish split `exposed 1486 / internal_only 600 / missing 19`.
* Confirm finding inventory counts: missing `publish_state 19`, nil `text_ko 19`.
* Confirm `quality_state` runtime observation: missing `2105`.
* Confirm sealed current runtime evidence by citing `current_runtime_hash_manifest.json` sha256 `790b5689097a8856e6213074fda25b723060073206a7ca44bd26d9f6f08c9171`.
* Confirm monolith is not deployable authority.
* Record that refactor v4.1 smoke validated chunk topology only, not body_plan user-facing surface display.
* Do not regenerate artifacts.

Validation:

```text
identity_pregate = pass
row_count = 2105
publish_split = exposed 1486 / internal_only 600 / missing 19
chunk_manifest_present = true
chunk_file_count = 11
sealed_current_runtime_baseline_link = confirmed
identity_link_mode = mode_current_runtime_baseline_seal_consume
sealed_current_runtime_evidence_path_hash_cited = true
sealed_current_runtime_hash_manifest_sha256 = 790b5689097a8856e6213074fda25b723060073206a7ca44bd26d9f6f08c9171
missing_publish_state_count = 19
nil_text_ko_count = 19
quality_state_missing_count = 2105
historical_staged_hash_used_as_current_gate = false
topology_only_evidence_used_as_identity_gate = false
monolith_deployable_authority = false
artifact_regeneration_count = 0
```

Failure branch:

```text
blocked_sealed_current_runtime_baseline_missing
blocked_identity_link_mode_not_sealed_in_opening_decision
blocked_historical_staged_hash_used_as_current_gate
blocked_topology_only_identity_evidence
blocked_current_runtime_baseline_hash_mismatch
```

---

### Change 2 - Phase 2 QA harness and sample matrix construction

Purpose:

Freeze the observation harness and construct a sample matrix that covers the contract axes before manual QA begins.

Files:

```text
Iris/build/description/v2/staging/manual_in_game_validation/migv_qa/phase2_harness/validation_harness.md
Iris/build/description/v2/staging/manual_in_game_validation/migv_qa/phase2_harness/manual_in_game_validation_sample_matrix.json
Iris/build/description/v2/staging/manual_in_game_validation/migv_qa/phase2_harness/manual_in_game_validation_checklist.md
```

Implementation Notes:

* Record `Console.txt` readpoint path and timestamp convention.
* Define evidence schema by sample and surface.
* Include at least one sample for each required axis:

```text
runtime_state: adopted / unadopted / legacy enum influence candidate
publish visibility: exposed / internal_only / missing publish_state finding / boundary case
body source: direct_use / cluster_summary / role_fallback / identity_fallback / acquisition_support / limitation_tail / meta_tail
text shape: short / long / Korean josa-spacing-sensitive / multi-section / sparse / fallback-heavy
finding shape: nil text_ko / missing publish_state / non-empty text_ko control
chunk boundary: Chunk001 first-middle-last / mid chunk boundary / Chunk011 first-middle-last
consumer: Browser / Wiki-detail / default bounded baseline / search-select-reselect
```

* Declare the round mutation-free observer scope.
* Separate checklist sections for Browser, Wiki/detail, default bounded baseline, publish visibility, baseline preservation, and negative invariants.
* Explicitly mark Alt tooltip validation as deferred/out-of-scope, not a hard gate.

Validation:

```text
axis_coverage_complete = true
exposed_sample_count >= 1
internal_only_sample_count >= 1
unadopted_sample_count >= 1
missing_publish_state_finding_sample_count >= 1
nil_text_ko_finding_sample_count >= 1
chunk_boundary_sample_count >= 1
fallback_path_sample_count >= 1
harness_schema_defined = true
surface_checklists_separated = true
alt_tooltip_hard_gate = false
```

---

### Change 3 - Phase 3 static pre-run validation

Purpose:

Prove that the QA target is not already broken by static gates before starting Project Zomboid.

Files:

```text
Iris/build/description/v2/staging/manual_in_game_validation/migv_qa/phase3_static_prerun/static_prerun_validation_report.json
```

Implementation Notes:

* Run Python unittest discovery.
* Run Lua syntax validation.
* Check chunk manifest integrity and expected chunk count.
* Check row identity, rendered text parity, publish visibility data, and static Browser/Wiki/default bounded-baseline consumer scans where existing tooling supports it.
* Scan for known regression markers:

```text
item selection error
chunk load failure
nil body display
legacy enum dependency
stale active/silent current-surface token
```

Validation:

```powershell
python -B -m unittest discover -s Iris\build\description\v2\tests -p "test_*.py"
```

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\check_lua_syntax.ps1
```

Pass may be claimed only if the exact relevant commands exit `0`.

Failure branch:

```text
blocked_with_static_prerun_failure
```

---

### Change 4 - Phase 4 in-game environment setup

Purpose:

Record a reproducible in-game QA environment and confirm console/screenshot capture readiness.

Files:

```text
Iris/build/description/v2/staging/manual_in_game_validation/migv_qa/phase4_environment/manual_in_game_validation_environment.md
Iris/build/description/v2/staging/manual_in_game_validation/migv_qa/phase4_environment/enabled_mods_minimal.md
Iris/build/description/v2/staging/manual_in_game_validation/migv_qa/phase4_environment/enabled_mods_modded.md
```

Implementation Notes:

* Record Project Zomboid version and B41/B42 environment identity.
* Record Iris mod install/build path.
* Record enabled mod list separately for minimal and modded runs.
* Record language/locale settings.
* Record save/world/test character/inventory setup.
* Record clean console log handling.
* Record screenshot or screen recording method.
* Do not alter canonical repository artifacts.

Validation:

```text
environment_manifest_present = true
minimal_environment_recorded = true
modded_environment_recorded = true
console_capture_ready = true
visual_evidence_capture_ready = true
test_save_entered = true
Iris_UI_entered = true
```

---

### Change 5 - Phase 5A Browser surface validation

Purpose:

Validate the Browser surface as the current in-game entry for selecting and viewing DVF 3-3 body_plan output.

Files:

```text
Iris/build/description/v2/staging/manual_in_game_validation/migv_qa/phase5_surface/browser_surface_result.json
```

Implementation Notes:

For each applicable sample:

* Confirm Browser opens from the expected current user path.
* Confirm category browse, item search, item select, and item reselect.
* Confirm selected item changes do not leave stale body text.
* Confirm Layer 3 body text is not mixed with Layer 1/2/4/5.
* Confirm body section order is not runtime-reordered.
* Confirm raw `publish_state`, `runtime_state`, `source`, nil, table addresses, or placeholders are not displayed to users.
* Confirm Iris-attributable console error count for the observation window.

Validation:

```text
browser_surface = pass
stale_selection_artifact_count = 0
layer_boundary_confusion_count = 0
nil_placeholder_raw_token_exposure = 0
iris_attributable_console_error_count = 0
```

---

### Change 6 - Phase 5B Wiki/detail surface validation

Purpose:

Validate the Wiki/detail surface, including the four-level hierarchy and Browser-to-detail transition.

Files:

```text
Iris/build/description/v2/staging/manual_in_game_validation/migv_qa/phase5_surface/wiki_detail_result.json
```

Implementation Notes:

For each applicable sample:

* Confirm Wiki/detail panel opens from Browser selection.
* Confirm 대분류 - 소분류 - 아이템 목록 - 아이템 설명 hierarchy.
* Confirm item description displays the intended DVF 3-3 body_plan output.
* Confirm close/reopen and refresh do not show stale content.
* Confirm Layer 3 body text is not mixed with Layer 1/2/4/5.
* Confirm raw `publish_state`, `runtime_state`, `source`, nil, table addresses, or placeholders are not displayed to users.
* Confirm Iris-attributable console error count for the observation window.

Validation:

```text
wiki_detail_surface = pass
four_level_hierarchy = pass
stale_selection_artifact_count = 0
layer_boundary_confusion_count = 0
nil_placeholder_raw_token_exposure = 0
iris_attributable_console_error_count = 0
```

---

### Change 7 - Phase 5C default bounded baseline validation

Purpose:

Validate the default bounded baseline after fixing its definition in the round opening note.

Files:

```text
Iris/build/description/v2/staging/manual_in_game_validation/migv_qa/phase5_surface/default_surface_result.json
Iris/build/description/v2/staging/manual_in_game_validation/migv_qa/phase5_surface/surface_display_result.json
```

Implementation Notes:

* Define default bounded baseline before validation begins.
* The definition must stay inside the Philosophy.md two-surface model and may only cover:

```text
Iris-disabled vanilla behavior preservation
right-click entrypoint baseline leading to the Browser/Wiki path
```

* Reject any opening definition that creates a new third Iris body display surface.
* Reject any opening definition that duplicates Browser/Wiki validation under a new name.
* Confirm Iris-disabled vanilla behavior remains preserved where applicable.
* Confirm body display is validated through Browser/Wiki, not through a newly-created default body surface.
* Confirm context menu and item selection regressions do not recur.
* Confirm known conflict marker recurrence, including CheatMenu-related item selection/context issues, is absent or classified with reproduction status.
* Confirm repeated open/close does not accumulate Iris-attributable errors.

Validation:

```text
default_bounded_baseline_definition_documented = true
default_bounded_baseline_within_philosophy_two_surface_model = true
default_bounded_baseline = pass
vanilla_behavior_preserved = true
context_menu_regression_count = 0
item_selection_regression_count = 0
known_conflict_marker_recurrence = 0
iris_attributable_console_error_count = 0
```

---

### Change 8 - Phase 6 publish visibility contract two-sided check

Purpose:

Verify the `exposed 1486 / internal_only 600 / missing 19` Layer 3 body/source quality contract on actual user-facing surfaces, including finding-row behavior. Iris Browser is an all-item Browser: item-entry visibility is not the same thing as Layer 3 body publication.

Files:

```text
Iris/build/description/v2/staging/manual_in_game_validation/migv_qa/phase6_publish/publish_visibility_two_sided_result.json
```

Implementation Notes:

* Confirm exposed samples appear on intended surfaces.
* Confirm internal_only samples may remain discoverable as item entries but do not leak raw internal state tokens or broken placeholders.
* Separate internal/debug path observations from default user-facing observations.
* Confirm unadopted samples may remain discoverable as item entries but do not display broken body placeholders.
* Confirm missing `publish_state` finding samples follow the revised all-item Browser contract and are not misclassified as cleanup targets during QA.
* Confirm nil `text_ko` finding samples display safe generated/tag-derived text or safe absence without raw nil/table/placeholder exposure.
* Confirm Browser/Wiki item-entry/body-state behavior is consistent when Wiki/detail evidence is in scope.
* Confirm raw `publish_state`, `runtime_state`, or `source` tokens are not shown to users.

Validation:

```text
exposed_display_sample_pass = true
internal_only_item_entry_visible_allowed = true
internal_only_raw_state_token_exposure_count = 0
missing_publish_state_finding_rows_classified = true
nil_text_ko_broken_placeholder_count = 0
unadopted_broken_exposure_count = 0
raw_state_token_exposure_count = 0
browser_wiki_visibility_consistent = true when Wiki/detail evidence is in scope
```

---

### Change 9 - Phase 7 runtime consumer baseline preservation

Purpose:

Prove that manual QA did not mutate the runtime consumer baseline or canonical artifacts.

Files:

```text
Iris/build/description/v2/staging/manual_in_game_validation/migv_qa/phase7_baseline/runtime_baseline_preservation_result.json
```

Implementation Notes:

* Reconfirm chunk runtime load topology:

```text
monolith 0 loads
manifest 1 load
chunk files 11 loads
```

* Reconfirm row count, adopted/unadopted count, publish split, finding inventory counts, chunk count, rendered text hash/parity, and source decisions identity.
* Record `quality_state missing 2105` as the current sealed runtime observation.
* Historical `quality_baseline_v4` may be cited only as comparison context from older staged/static rounds and is not a current runtime hard gate.
* Re-run relevant static validation after QA.
* Review `git diff --stat` and `git diff` to confirm only QA evidence artifacts or permitted docs changed.
* Record no regeneration and no canonical mutation declaration.
* `canonical_mutation_count = 0` excludes round-local QA evidence artifacts and Branch A append-only top-doc closeout addenda.

Validation:

```text
source_runtime_authoritative_artifact_delta = 0
row_count = 2105
publish_split = exposed 1486 / internal_only 600 / missing 19
adopted_unadopted_count = 2084/21
missing_publish_state_count = 19
nil_text_ko_count = 19
quality_state_missing_count = 2105
rendered_text_unchanged = true
chunk_topology_unchanged = true
only_QA_evidence_artifacts_changed = true
canonical_mutation_count_excludes_round_evidence_and_branch_a_top_doc_addenda = true
```

---

### Change 10 - Phase 8 negative invariant verification

Purpose:

Verify deployable boundary and baseline invariants independently from positive surface observations.

Files:

```text
Iris/build/description/v2/staging/manual_in_game_validation/migv_qa/phase8_negative/negative_invariant_report.json
```

Implementation Notes:

* Confirm monolith absent from deployable path and 0 loads.
* Confirm sealed current runtime baseline hash manifest `790b5689097a8856e6213074fda25b723060073206a7ca44bd26d9f6f08c9171` remains the cited current identity evidence.
* Confirm historical staged parity hash `0390272b...` is not used as the current identity gate.
* Confirm GUARD-A current-surface legacy `active/silent` hard-fail protection remains satisfied.
* Confirm mutation count `0` for canonical artifacts. Round-local QA evidence and Branch A append-only top-doc closeout addenda are not canonical artifact mutation.

Validation:

```text
monolith_absent = true
monolith_load_count = 0
sealed_current_runtime_hash_manifest_unchanged = true
historical_staged_hash_used_as_current_gate = false
legacy_enum_current_surface_reentry = 0
canonical_mutation_count = 0
canonical_mutation_count_excludes_round_evidence_and_branch_a_top_doc_addenda = true
```

---

### Change 11 - Phase 9 evidence packaging, Phase 10 hard gate, Phase 11 adversarial review

Purpose:

Package evidence into reviewable artifacts, evaluate the single hard gate, and perform adversarial review before closeout.

Files:

```text
Iris/build/description/v2/staging/manual_in_game_validation/migv_qa/phase9_evidence/manual_in_game_validation_results.json
Iris/build/description/v2/staging/manual_in_game_validation/migv_qa/phase9_evidence/manual_in_game_validation_console_log_summary.md
Iris/build/description/v2/staging/manual_in_game_validation/migv_qa/phase9_evidence/manual_in_game_validation_screenshots_index.md
Iris/build/description/v2/staging/manual_in_game_validation/migv_qa/phase9_evidence/manual_in_game_validation_walkthrough.md
Iris/build/description/v2/staging/manual_in_game_validation/migv_qa/phase10_hard_gate/phase10_hard_gate_report.json
Iris/build/description/v2/staging/manual_in_game_validation/migv_qa/phase11_adversarial_review.md
```

Implementation Notes:

* Walkthrough must cover target artifact, environment, sample rationale, identity pre-gate, surface results, publish visibility, console/runtime errors, baseline preservation, negative invariant, closeout branch recommendation, non-goal compliance, and no mutation declaration.
* Hard gate passes only if:

```text
Phase 1 identity pre-gate = pass
Phase 1 sealed current runtime evidence path/hash = cited
historical staged hash used as current gate = false
Phase 2 axis coverage = pass
Phase 3 static pre-run = pass
Phase 4 environment manifest = pass, minimal + modded recorded
minimal/vanilla-adjacent environment validation = pass
modded environment observation = recorded with reproduction classification
Phase 5A Browser surface = pass
Phase 5B Wiki/detail surface = pass
Phase 5C default bounded baseline = pass
Phase 6 publish contract = pass
Phase 6 finding-row behavior = pass
Phase 7 runtime baseline = pass
Phase 8 negative invariant = pass
mutation count = 0
release-overclaim count = 0
```

* Use `docs/REVIEW_TEMPLATE.md` structure for adversarial review.
* Review validation ceiling, identity evidence, surface partial-pass overclaim, release overclaim, and no-mutation proof.

Validation:

```text
all_QA_artifacts_present = true
sample_surface_trace_complete = true
phase10_hard_gate = pass
adversarial_review_verdict = PASS
critical_issue_count = 0
unsupported_release_claim_count = 0
```

---

### Change 12 - Phase 12 closeout classification

Purpose:

Select the closeout branch that matches the evidence and, only for Branch A, add top-doc closeout addenda.

Files:

```text
Iris/build/description/v2/staging/manual_in_game_validation/migv_qa/phase12_closeout/closeout_classification.json
Iris/build/description/v2/staging/manual_in_game_validation/migv_qa/phase12_closeout/closeout.md
```

Conditional Branch A docs:

```text
docs/DECISIONS.md
docs/ARCHITECTURE.md
docs/ROADMAP.md
```

Implementation Notes:

Branch A:

```text
closed_with_dvf_3_3_deployed_closeout
```

Allowed only if every hard gate passes, adversarial review passes, mutation count is `0`, and no release-overclaim exists.

Branch A closeout addenda must explicitly state:

```text
validated consumers = Browser / Wiki-detail / default bounded baseline
Alt tooltip consumption = unvalidated / deferred to separate tooltip-system round
```

Branch B:

```text
blocked_with_runtime_surface_bug
```

For nil display, stale body, panel crash, chunk load failure, item selection error, or context menu regression.

Branch C:

```text
blocked_with_visibility_contract_violation
```

For raw internal state token exposure, exposed omission, unadopted broken body exposure, raw nil/table/placeholder exposure, or raw state token exposure.

Branch D:

```text
blocked_with_identity_pregate_failure
```

For missing sealed current runtime baseline evidence, hash mismatch, topology-only identity evidence, or an opening note that still treats historical `0390272b...` as the current identity gate.

Branch E:

```text
partial_manual_qa_only
```

For incomplete surfaces, incomplete sample matrix, missing console capture, insufficient environment record, or unresolved mod conflict ambiguity.

Branch F:

```text
blocked_with_static_prerun_failure
```

For Python test failure, Lua syntax failure, chunk manifest integrity failure, row identity failure, static consumer scan blocker, or required validation tooling unavailable.

Validation:

```text
closeout_branch_matches_evidence = true
Branch_A_docs_written_only_after_hard_gate = true
release_readiness_claim_count = 0
canonical_mutation_count = 0
canonical_mutation_count_excludes_round_evidence_and_branch_a_top_doc_addenda = true
```

---

## 7. Validation Plan

### Automated Validation

Required validation commands:

```powershell
python -B -m unittest discover -s Iris\build\description\v2\tests -p "test_*.py"
```

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\check_lua_syntax.ps1
```

Required automated/static checks:

* Deployable identity pre-gate.
* Sealed current runtime baseline hash manifest path/hash check.
* Chunk manifest integrity.
* Chunk file count.
* Row count and row identity check.
* Publish split check.
* Missing `publish_state` / nil `text_ko` finding inventory check.
* Rendered text parity or hash check.
* Browser/Wiki/default bounded-baseline static consumer scan where existing tooling supports it.
* Legacy monolith duplicate load possibility scan.
* Legacy `active/silent` current-surface guard validation where existing tooling supports it.
* Post-QA baseline preservation check.
* `git diff --stat` and `git diff` review for forbidden mutation.

Validation claim rule:

* Do not claim Python tests passed unless the exact command exits `0`.
* Do not claim Lua syntax passed unless the exact command exits `0`.
* If a required tool is missing, report validation as blocked.
* Static validation pass is not manual in-game QA pass.

### Manual Validation

Manual validation is the core of this round.

Required manual checks:

* Browser surface.
* Wiki/detail surface.
* Default bounded baseline as fixed in the opening note.
* Publish visibility two-sided behavior.
* Finding-row behavior for missing `publish_state` and nil `text_ko`.
* Repeated open/close and item reselection behavior.
* Iris-attributable console/runtime error inspection.
* Minimal environment observation; Branch A requires the minimal or vanilla-adjacent run to pass.
* Modded environment observation with reproduction classification; non-Iris console errors are Compatibility observations, not automatic Branch A blockers.
* Screenshot, screen recording, or structured visual note capture.

Manual validation pass requires all selected samples in the matrix to have traceable sample/surface/result evidence.

Console attribution rule:

```text
minimal_environment_iris_attributable_console_error_count = 0
minimal_environment_total_console_error_count should be 0 unless a documented non-Iris source is isolated
modded_environment_iris_attributable_console_error_count = 0
modded_environment_non_iris_console_errors = recorded_as_compatibility_observation
modded_only_failure = blocker | known_conflict | partial, based on reproduction status
```

### Validation Limits

This execution does not perform:

* 2105-row exhaustive manual clicking.
* Multiplayer validation.
* Long-session validation.
* External mod compatibility sweep.
* Workshop validation.
* B42 porting validation unless the recorded environment explicitly is B42 and still within current scope.
* Tooltip system implementation validation.
* Alt tooltip validation.
* Release readiness validation.
* Packaging validation.
* Full Iris user-facing QA beyond the three validated surfaces.

---

## 8. Risk Surface Touch

### Authority Surface

Touched only as read/closeout governance. The round may add Branch A closeout addenda after hard gate pass, but it must not change source decisions, compose authority, publish authority, or enum authority.

### Runtime Behavior Surface

Observed, not mutated. Manual QA exercises runtime UI surfaces but does not modify runtime Lua behavior.

### Compatibility Surface

Observed through minimal and modded environments. Modded-environment findings must be separated by reproduction status and cannot be overclaimed as Iris defects without evidence.

### Sealed Artifact Surface

Read-only. Sealed current runtime hash manifest, source decisions, rendered text, runtime chunks, publish split, finding inventories, and chunk topology must remain unchanged. Historical staged hash and `quality_baseline_v4` are comparison context only unless a separate decision reopens them as authority.

### Public-Facing Output Surface

Observed. The round checks existing user-facing surfaces but does not rewrite displayed text or redesign UI.

---

## 9. Risk Analysis

### Architecture Risk

* Static closeout can be overread as deployed closeout.
* Chunk deployable authority may not be positively linked to the sealed current runtime baseline.
* Historical staged hash `0390272b...` may be accidentally re-promoted from comparison-only readpoint to current identity gate.
* Default bounded baseline definition may drift into an unauthorized third Iris display surface unless the opening note rejects that drift.
* Tooltip-system scope may re-enter by wording unless Alt tooltip remains deferred/out-of-scope.
* Branch A closeout wording may accidentally imply release readiness.

### Runtime Risk

* Nil body display, stale selection, chunk load failure, or panel crash may appear only in-game.
* UI formatting issues can be confused with data identity issues.
* Repeated open/close may reveal accumulated errors not seen in one-shot checks.

### Compatibility Risk

* Modded environment errors may come from external conflicts.
* Minimal and modded observations can be conflated.
* `internal_only` may be misread as "must not exist anywhere" instead of "Layer 3 body/source quality must not leak as raw internal state."
* Missing `publish_state` or nil `text_ko` finding rows may be misread as cleanup targets instead of finding-aware QA samples that still may have safe Browser item entries.

### Regression Risk

* QA debug changes may accidentally remain in the working tree.
* Evidence artifacts may be mixed with source/runtime mutations.
* Sample matrix may over-cover exposed/adopted happy paths and under-cover fallback/internal/unadopted paths.
* Sample matrix may omit the 19/19 finding rows introduced by the sealed current runtime baseline.
* Console capture failure can make an otherwise real observation non-reviewable.

---

## 10. Rollback Plan

Normal no-mutation case:

* No source/data/code rollback is needed.
* QA evidence artifacts remain as review evidence.
* Top-doc closeout addenda are written only after Branch A conditions pass.

Phase 1 failure:

* Stop before manual QA.
* Close as `blocked_with_identity_pregate_failure`.
* Preserve pre-gate report.
* Do not change canonical state from `ready_for_in_game_validation`.

Phase 3-8 failure:

* Record the failing phase and `blocked_*` branch.
* Do not declare deployed closeout.
* Preserve QA evidence.
* Do not write Branch A top-doc closeout addenda.

Accidental mutation case:

* Record mutation file list and intent status.
* Restore source/runtime authoritative artifacts to pre-QA baseline.
* Re-run static validation.
* Close as `blocked_due_to_undeclared_mutation` or partial QA.
* Open a separate bugfix or correction round if needed.

Wrong closeout claim case:

* Do not silently rewrite historical text.
* Add a correction addendum.
* Re-seal claim ceiling at or below DVF 3-3 deployed closeout.
* Re-evaluate whether `DECISIONS.md`, `ARCHITECTURE.md`, and `ROADMAP.md` need correction entries.

---

## 11. Governance Constraints

Required constraints:

* `docs/Philosophy.md` compliance.
* Iris remains wiki-style and does not add interpretation, recommendation, or comparison.
* Runtime/build-time separation is preserved.
* Mutation-free observer scope is preserved.
* No source decisions mutation.
* No facts mutation.
* No rendered text mutation.
* No Lua chunk regeneration.
* No body_plan recomposition.
* No publish_state or quality_state rejudgment.
* No silent fallback on pre-gate or invariant failures.
* Findings are recorded before fixes.
* Bugfix work is opened as a separate round.
* Static validation and deployed closeout remain separate gates.
* Alt tooltip validation remains deferred/out-of-scope and is not a DVF 3-3 deployed closeout hard gate.
* Default bounded baseline must stay inside the Philosophy.md two-surface model and must not create a new Iris body display surface.
* Console gating is Iris-attributable; non-Iris modded-environment errors are compatibility observations unless reproduced as Iris-attributable defects.
* Current runtime `quality_state` observation is `missing 2105`; historical `quality_baseline_v4` may be used only as comparison context, not as a current runtime hard gate.
* Missing `publish_state 19` and nil `text_ko 19` are finding-aware QA targets, not same-round cleanup triggers.
* Manual in-game validation pass does not imply release readiness.
* Existing fail-loud guards remain in force:

```text
DEFAULT_RUNTIME_STATE_REJECTED_LEGACY_ENUM
DEFAULT_RESOLVER_REJECTED_LEGACY_COMPAT_LABEL
CURRENT_SURFACE_REJECTED_LEGACY_ACTIVE_SILENT_LABEL
```

* Dirty working tree handling must preserve unrelated user changes.

---

## 12. Expected Closeout State

Expected successful closeout:

```text
closed_with_dvf_3_3_deployed_closeout
```

Required successful closeout conditions:

```text
Phase 1 identity pre-gate = pass
Phase 1 cites sealed current runtime baseline hash manifest 790b5689097a8856e6213074fda25b723060073206a7ca44bd26d9f6f08c9171
historical 0390272b... hash is not used as current identity gate
Phase 2 axis coverage = pass
Phase 3 static pre-run = pass
Phase 4 environment manifest = pass, minimal + modded recorded
minimal/vanilla-adjacent environment validation = pass
modded environment observation = recorded with reproduction classification
Browser surface = pass
Wiki/detail surface = pass
default bounded baseline = pass
publish visibility two-sided check = pass
missing publish_state / nil text_ko finding rows are classified and do not render broken placeholders
runtime baseline preservation = pass
negative invariant verification = pass
Iris-attributable console/runtime error count = 0 for validated windows
nil / placeholder / raw token exposure = 0
internal_only item-entry visibility is allowed under all-item Browser semantics
internal_only raw state token exposure = 0
unadopted broken exposure = 0
canonical mutation count = 0
canonical mutation count excludes round-local evidence and Branch A append-only top-doc addenda
Phase 10 hard gate = pass
Phase 11 adversarial review = PASS
release-overclaim count = 0
```

Blocked or partial closeout states:

```text
blocked_with_runtime_surface_bug
blocked_with_visibility_contract_violation
blocked_with_identity_pregate_failure
blocked_with_static_prerun_failure
partial_manual_qa_only
blocked_due_to_undeclared_mutation
```

If the expected closeout is not `complete`, the reason must be explicit:

* identity link missing,
* sealed current runtime baseline evidence missing or mismatched,
* historical staged hash used as current identity gate,
* static validation blocked or failed,
* one or more surfaces failed,
* revised item-entry/body-state contract failed,
* finding-row safe-display behavior failed or was not sampled,
* baseline mutation detected,
* negative invariant failed,
* console capture failed,
* sample matrix incomplete,
* modded conflict not reproduced or separated,
* or adversarial review found a blocker.

Non-claims at any closeout:

* No Iris `ready_for_release`.
* No Workshop readiness.
* No B42 readiness.
* No Tooltip completion.
* No Tooltip system validation or completion claim.
* No claim that this plan itself opens or completes a tooltip-system round.
* DVF 3-3 deployed closeout may be cited only as input if a separate tooltip-system round is later opened.
* No full Iris release QA completion.
* No packaging, deployment, release note, or Workshop publish completion.
* No complete-removal cleanup closure.
* No adapter removal debt closure.
* No `quality_baseline_v4 -> v5` cutover.
