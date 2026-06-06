# Iris DVF 3-3 Structural Signal Missing Anchor Authority Resolution Round Plan

> 상태: Draft v0.3-final-review-applied
> 기준일: 2026-05-28
> 상위 기준: `docs/Philosophy.md`, `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`
> authority input: `Roadmap - Iris DVF 3-3 Structural Signal Missing Anchor Authority Resolution Round` (2026-05-28 user-provided synthesis)
> review input: `Review - Iris DVF 3-3 Structural Signal Missing Anchor Authority Resolution Round` Conditional PASS feedback (2026-05-28), R-1 through R-6 incorporated in v0.2; important issues I-1 through I-8 incorporated where they clarify branch semantics without changing round scope.
> final review input: `Final Synthesis Review - Iris DVF 3-3 Structural Signal Missing Anchor Authority Resolution Round` PASS feedback (2026-05-28), recommended revisions R-1 through R-7 incorporated in v0.3 without changing approved execution scope.
> 직접 상위 readpoint:
> - 2026-04-22 `Iris DVF 3-3 Phase D/E staged rollout override round` closeout
> - 2026-04-24 `closed_with_canonical_code_path_convergence_applied`
> - 2026-04-24 `closed_with_observer_patch_applied`
> - 2026-05-26 `closed_with_historical_runtime_vocabulary_readpoint_anchor`
> - 2026-05-27 `Default compose current authority input is data-root guarded`
> - 2026-05-27 `Iris DVF 3-3 Structural Signal Current Referent Inventory and Anchor Recovery Round` `blocked_missing_anchor`
> 계획 형식: `docs/PLAN_TEMPLATE.md`
> template attestation: this plan follows the 1-12 section structure in `docs/PLAN_TEMPLATE.md`; the template is a project planning form, not semantic authority over `docs/Philosophy.md`, `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, or `docs/ROADMAP.md`.
> 실행 상태: planning authority only. 이 문서는 current structural reclassification readpoint authority의 disposition을 정하기 위한 실행 계획이며, 작성 시점에는 runtime Lua, generated runtime artifacts, rendered text, source decisions, facts, publish_state, quality_state, runtime_state, deployed state, release state, or closeout state를 변경하지 않는다.

---

## 1. Objective

이번 execution plan의 목적은 `blocked_missing_anchor` 상태로 닫힌 structural signal current referent 문제를 한 번 더 같은 상태로 반복하지 않고, current structural reclassification readpoint authority의 정체를 단일하고 증거 기반으로 봉인하는 것이다.

이번 round는 다음 세 결과 중 정확히 하나를 목표로 한다.

```text
closed_with_anchor_restored
closed_with_authoritative_reconstruction_adopted
closed_with_readpoint_retired_or_repointed
```

모든 branch가 실패하면 다음 blocked closeout만 허용한다.

```text
blocked_unresolved_anchor_authority
```

precondition 자체가 불충족이면 다음 blocked closeout만 허용한다.

```text
blocked_precondition_not_satisfied
```

다음 closeout은 금지한다.

```text
blocked_missing_anchor
```

핵심 objective:

```text
2026-04-24 sealed canonical structural reclassification artifact set의 물리 상태를 재확인한다
restore / authoritative reconstruction / retirement-or-repointing 조건을 disjoint matrix로 봉인한다
matrix 결과에 따라 단일 branch만 실행한다
current structural readpoint authority의 위치 또는 retired/repointed 상태를 명확히 한다
sealed historical bodies and hash-sealed artifacts remain unmodified
runtime Lua, rendered text, publish_state, quality_state, and current compose writer authority remain unchanged
```

Sealed historical identity for comparison. All hash equality and invariance checks in this plan use `sha256`.

```text
row sha256 = 6e84bb2f9622b79493473631d391a01c857c04ddbea869993a99856283ecb6d9
summary sha256 = 8b6b7b34ba4c5de9bf6df6d8bcdfeacc6ec86ebda9f0c0b883672177d7b508cf
source distribution sha256 = 1c8f8a3431d01f6780f8fe1a602db24ef3ae38febd936df0dec98e8fe80c41b0
section distribution sha256 = b587c663ba928bd7e6a9f8609caba9e3620c92acb6f3fa8359d868b558c0c490
overlap distribution sha256 = 831303f7134bf7d8887efed18aaa69ee373fa1ae9b19002302fbb4ad32b973fc
crosswalk sha256 = 3d60c945d958778ec89b13ab3efff93732726b969a11e4da9887247b488b817b
artifact validation sha256 = 683323b9d52887d2ecf172e97bc6b8d7475a9ac3a8d04deec1db44fcf7c800a7
```

Historical distribution for comparison:

```text
source: BODY_LACKS_ITEM_SPECIFIC_USE 617 / FUNCTION_NARROW 7 / none 1481
section: SECTION_FUNCTION_NARROW 1433 / none 672
overlap: source_only 67 / section_only 876 / coexist 557 / dual_none 605
```

Common success must not claim:

```text
runtime rollout
deployed closeout
release readiness
Workshop readiness
manual in-game QA
ACQ_DOMINANT remeasurement
FUNCTION_NARROW / ACQ_DOMINANT blanket isolation
publish mutation review
rendered text rebaseline
Lua regeneration
```

Branch B success must additionally not claim:

```text
reconstruction adoption equals old artifact restoration
old 2026-04-24 sealed hash set recovery
```

Branch C success must additionally not claim:

```text
retirement/repointing equals sealed artifact obsolete declaration
new C-2 anchor is machine-enforced guard
```

---

## 2. Scope

This is an authority-artifact/static-validation round. It may inspect existing files, create round-local staging reports, create new reconstruction artifacts if Branch B is selected, add readpoint/closeout documentation, and add or adjust validators/tests only when required to make the selected disposition fail-loud.

Round-local artifact root:

```text
Iris/build/description/v2/staging/compose_contract_migration/structural_signal_missing_anchor_authority_resolution_round/
```

Mutable surfaces:

```text
round-local staging reports
reconstruction artifacts if Branch B is selected
structural readpoint manifest
docs addendum / closeout docs
tests or validators for readpoint resolution if required by selected branch
```

Immutable surfaces:

```text
runtime Lua chunks
packaged Lua
rendered text
source decisions row content
facts row content
quality_state
publish_state
quality_baseline_v4
Browser / Wiki / Tooltip runtime behavior
historical sealed decision bodies
hash-sealed artifacts
2026-04-24 sealed artifact body content
body_plan_signal_preservation.* traceability baseline
current runtime hash manifest 790b5689097a8856e6213074fda25b723060073206a7ca44bd26d9f6f08c9171
staged Lua hash 0390272b93a933d7e53bba996b322ffbdd9fc905585bec03fc78d338f469f062
```

In scope:

* Phase 0 scope lock and closeout ceiling declaration.
* Phase 1 inventory and precondition reconfirmation.
* Phase 2 disjoint disposition matrix and single-branch selection.
* Phase 3 execution of exactly one selected branch:
  * Branch A restore, split into A1 already-present reaffirmation or A2 exact-hash artifact restoration,
  * Branch B authoritative reconstruction,
  * Branch C readpoint retirement or repointing.
* Phase 4 sealed decision trace update.
* Phase 5 hard gate.
* Phase 6 adversarial review.
* Phase 7 final closeout and non-claim seal.

### Explicitly Out Of Scope

* `ACQ_DOMINANT` remeasurement.
* `FUNCTION_NARROW` / `ACQ_DOMINANT` / `BODY_LACKS_ITEM_SPECIFIC_USE` policy rejudgment.
* `LAYER4_ABSORPTION` source-family promotion.
* Blanket isolation.
* Publish mutation review.
* `body_plan_signal_preservation.*` traceability baseline recalculation.
* 2026-04-24 sealed canonical baseline hash recalculation or replacement.
* `quality_state`, `publish_state`, or `quality_baseline_v4` writer redesign.
* Source axis, section axis, or overlap semantics redefinition.
* Source expansion.
* Body-role structural lint redesign.
* Semantic axis policy change.
* Runtime Lua regeneration, packaged Lua regeneration, or rendered text rebaseline.
* Adapter / Diagnostic Compatibility Final Disposition reopening.
* Resolver compatibility mapping disposition change.
* Legacy adapter entrypoint mode reintroduction.
* Selected-role native resolver authority redefinition.
* Repo-wide `active/silent` lexical zero.
* Diagnostic / import / historical alias removal.
* GUARD-A redefinition, strengthening, or weakening.
* Browser / Wiki / Tooltip changes.
* `quality_exposed` activation.
* MIGV-QA Phase 1 identity pre-gate baseline redefinition.
* Manual in-game QA.
* Deployed closeout, runtime rollout, release readiness, Workshop readiness, B42 readiness, or tooltip completion.
* Packaging, release note, commit, or Workshop publish.
* Old staging artifact whole-tree restoration.
* Historical docs body-wide rewrite.

---

## 3. Non-Goals

This plan does not attempt to:

* Reopen the 2026-04-22 staged/static closeout.
* Recalculate or revise the 2026-04-24 sealed hash set.
* Mutate sealed staging artifact bodies or hash-sealed artifacts.
* Treat artifact absence as automatic obsolete status.
* Treat count-only or shape-only reconstruction as authority.
* Promote staging artifacts to current writer authority input.
* Change `compose_profiles_v2.json + body_plan` as the current default compose authority.
* Change the 2026-05-27 data-root guard for default current compose inputs.
* Convert historical `active/silent` vocabulary into current `adopted/unadopted` authority.
* Claim runtime behavior preservation beyond the explicit no-runtime-mutation and validation ceiling evidence.

---

## 4. Assumptions

Authority assumptions:

* `docs/Philosophy.md` remains the top authority. Iris remains a 100% Lua wiki-style module.
* `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, and `docs/ROADMAP.md` are current governance readpoints.
* `DECISIONS.md` already contains the 2026-05-27 `Structural Signal Current Referent Inventory and Anchor Recovery Round` `blocked_missing_anchor` closeout at plan-writing time. Phase 1 still records this as a precondition confirmation.
* 2026-04-24 sealed structural reclassification artifacts remain immutable historical references unless Branch A verifies exact physical restoration.
* 2026-05-26 historical runtime vocabulary readpoint anchor forbids direct mutation of sealed historical bodies, fixtures, staging artifact bodies, and hash-sealed artifacts.
* Current runtime payload authority remains `adopted/unadopted`.
* GUARD-A remains owner of current-surface legacy `active/silent` re-entry prevention.
* Default current compose authority inputs must resolve under `Iris/build/description/v2/data/` in default mode.

Branch assumptions:

* Branch A is allowed only on full expected artifact set presence plus full sealed hash equality, or exact-byte restoration from a recoverable source with the same full sealed hash set.
* Branch B is allowed only if reconstruction recipe and required inputs are available from current data-root authority paths or same-round fresh generated intermediates derived entirely from current data-root authority paths, without using old staging artifacts as current writer inputs.
* Branch C is allowed when restoration/reconstruction cannot be made authoritative, or when an explicit retirement/repointing instruction supersedes A/B preference.
* Partial artifact presence, same-name wrong-epoch artifacts, diagnostic legacy views, and signal preservation additive artifacts are not sufficient for Branch A.
* Branch C repointing must target same-surface structural readpoint authority or a newly created explicit structural readpoint governance anchor. The 2026-05-26 central anchor may be cited only as vocabulary/historical layering context, not as sufficient replacement structural authority by itself.

Validation assumptions:

* Missing validation tools or blocked commands are reported as blocked, not passed.
* Prior observed Python baseline was `398 tests / OK`; this plan requires the exact relevant unittest command to exit `0` and observed test count to be at least the baseline unless a separate documented reason explains a count change.
* Prior observed Lua syntax baseline was `183 files / OK`; this plan requires the exact syntax command to exit `0` and observed file count to be at least the baseline unless a separate documented reason explains a count change.

---

## 5. Repository Areas Affected

### Code

None by default.

Optional validators/tests may be touched only if the selected branch needs fail-loud readpoint resolution:

```text
Iris/build/description/v2/tools/**
Iris/build/description/v2/tests/**
```

No runtime Lua file is a planned code target.

### Docs

Planning doc:

```text
docs/Iris/iris-dvf-3-3-structural-signal-missing-anchor-authority-resolution-round-plan.md
```

Potential closeout addenda after gates pass:

```text
docs/DECISIONS.md
docs/ROADMAP.md
```

`docs/ARCHITECTURE.md` update triggers are branch-conditional:

```text
Branch A: no ARCHITECTURE.md update by default; existing reference is reaffirmed.
Branch B: update the Iris DVF 3-3 production / body_plan readpoint summary if current authority path moves to the new reconstruction path.
Branch C: update the same summary if the prior structural reference becomes retired/repointed; C-2 also records the new structural anchor reference.
```

### Config

None.

### Generated Artifacts

Round-local evidence root:

```text
Iris/build/description/v2/staging/compose_contract_migration/structural_signal_missing_anchor_authority_resolution_round/
```

Branch B reconstruction output root:

```text
Iris/build/description/v2/staging/compose_contract_migration/structural_signal_missing_anchor_authority_resolution_round/phase3_branch_b_reconstruction/
```

Branch C anchor output root, if needed:

```text
Iris/build/description/v2/staging/compose_contract_migration/structural_signal_missing_anchor_authority_resolution_round/phase3_branch_c_retirement_or_repointing/
```

---

## 6. Planned Changes

### Change 1 - Phase 0 Scope Lock

Purpose:

Open the round as an authority-artifact/static-validation round and seal the allowed mutation surface before any branch execution.

Files:

```text
Iris/build/description/v2/staging/compose_contract_migration/structural_signal_missing_anchor_authority_resolution_round/phase0_scope_lock.json
```

Implementation Notes:

* Record execution scale as `authority-artifact/static-validation round`.
* Record mutable and immutable surfaces from Section 2.
* Record intended closeout ceiling:

```text
closed_with_anchor_restored
closed_with_authoritative_reconstruction_adopted
closed_with_readpoint_retired_or_repointed
blocked_unresolved_anchor_authority
blocked_precondition_not_satisfied
```

* Record forbidden closeout:

```text
blocked_missing_anchor
```

* Record failure semantics:
  * unknown state is not pass,
  * missing old anchor is not automatically obsolete,
  * reconstruction basis failure blocks adoption,
  * all branch failure closes only as `blocked_unresolved_anchor_authority`,
  * precondition failure before Phase 2 closes only as `blocked_precondition_not_satisfied`.
* Record forbidden operations:
  * `ACQ_DOMINANT` remeasurement,
  * blanket isolation,
  * publish mutation review,
  * runtime Lua regeneration,
  * count-only or shape-only reconstruction.

Validation:

* `phase0_scope_lock.json` exists and is valid JSON.
* Mutable and immutable surfaces are explicit.
* No runtime/rendered/publish/quality mutation is authorized.
* `blocked_missing_anchor` is listed as forbidden re-closeout.

---

### Change 2 - Phase 1 Inventory and Precondition Reconfirmation

Purpose:

Reconfirm the prior sealed closeout, expected artifact physical state, generation recipe state, required input state, and structural readpoint tool/test references.

Files:

```text
Iris/build/description/v2/staging/compose_contract_migration/structural_signal_missing_anchor_authority_resolution_round/phase1_inventory_report.json
```

Implementation Notes:

* Confirm that `DECISIONS.md` contains the 2026-05-27 `blocked_missing_anchor` closeout and record:

```text
precondition_status = confirmed | missing_prior_closeout | mismatched_prior_closeout
```

* If `precondition_status != confirmed`, stop before Phase 2. The round must close as `blocked_precondition_not_satisfied`, not `blocked_missing_anchor` and not a branch disposition.
* Check file-system presence of the expected 2026-04-24 canonical artifact set:

```text
Iris/build/description/v2/staging/compose_contract_migration/phase_d_structural_reclassification_code_path_convergence_round/phase4_artifacts/body_plan_structural_reclassification.2105.jsonl
Iris/build/description/v2/staging/compose_contract_migration/phase_d_structural_reclassification_code_path_convergence_round/phase4_artifacts/body_plan_structural_reclassification.2105.summary.json
linked source distribution artifact
linked section distribution artifact
linked overlap distribution artifact
linked crosswalk artifact
linked artifact validation report
```

* If files exist, verify full sealed hash set equality.
* Search current checkout, git history, ignored/local artifacts, archive paths, previous staging roots, and closeout report references.
* Define previous staging roots as:

```text
Iris/build/description/v2/staging/compose_contract_migration/phase_d_e_current_session/
Iris/build/description/v2/staging/compose_contract_migration/phase_d_structural_reclassification_code_path_convergence_round/
Iris/build/description/v2/staging/compose_contract_migration/phase_d_signal_preservation_patch_round/
Iris/build/description/v2/staging/compose_contract_migration/structural_signal_current_referent_inventory_anchor_recovery_round/
other compose_contract_migration descendants whose manifests or closeout reports reference body_plan_structural_reclassification.*
```

* Classify candidates:

```text
exact expected artifact
same-name wrong epoch
diagnostic_or_legacy_view
signal_preservation_additive_lane
non_authority_trace
invalid_candidate
```

* Record whether an exact-hash recoverable source exists for Branch A2:

```text
recoverable_exact_hash_source_found = true | false
recoverable_source_path = "<path or null>"
recoverable_source_class = git_history | archive | ignored_local_artifact | previous_staging_root | closeout_reference
recoverable_source_hash_match = full_set_match | partial_match | mismatch | not_applicable
```

* Record generation recipe script path, owning round, and executable status:

```text
recipe_owner_round = 2026-04-22_phase_d | 2026-04-24_convergence | other | unknown
recipe_script_path = "<path>"
recipe_executable_status = executable | blocked | missing
recipe_dry_run_status = pass | blocked | not_applicable
recipe_dry_run_scope = input_validation_only | dry_run_no_output | not_applicable
```

* Recipe dry-run must validate that the recipe can bind to the enumerated current inputs without using old staging artifacts as current writer inputs. It must not create authoritative reconstruction output.
* Record required input paths and classify them:

```text
current_data_root_authority
fresh_generated_intermediate_from_current_data_root
historical_provenance_only
forbidden_old_staging_input
diagnostic_fixture
missing
```

* For `fresh_generated_intermediate_from_current_data_root`, record generator path, source data-root inputs, input hashes, intermediate hash, and same-round provenance. Old staging artifacts remain forbidden as current writer inputs even if their shape matches.
* Inventory tool/test references to structural reclassification paths.

Validation:

* `precondition_status` is recorded. Any non-confirmed value blocks Phase 2 and requires `blocked_precondition_not_satisfied`.
* Hash equality / inequality results are recorded per artifact.
* Required inputs are classified using the six input classes above.
* `recipe_dry_run_status` is recorded and only `pass` can satisfy Branch B matrix selection.
* Any fresh generated intermediate has a complete data-root-derived provenance and same-round hash manifest.
* Tool/test reference counts are recorded by current hard dependency, current soft reference, diagnostic/provenance reference, historical sealed reference, stale doc reference, and test fixture reference.

---

### Change 3 - Phase 2 Disposition Matrix

Purpose:

Seal a disjoint branch-selection matrix and select exactly one branch from Phase 1 evidence.

Files:

```text
Iris/build/description/v2/staging/compose_contract_migration/structural_signal_missing_anchor_authority_resolution_round/phase2_disposition_matrix.json
Iris/build/description/v2/staging/compose_contract_migration/structural_signal_missing_anchor_authority_resolution_round/phase2_disposition_decision.md
```

Implementation Notes:

* Apply this branch order unless the user explicitly instructs retirement/repointing:

```text
A restore -> B authoritative_reconstruction -> C readpoint_retirement_or_repointing
```

* Precondition gate:

```text
precondition_status = confirmed
```

If this fails, Phase 2 branch selection is forbidden and closeout must be `blocked_precondition_not_satisfied`.

* Branch A condition is split into A1 and A2:

```text
A1 already-present reaffirmation:
  all expected artifacts verified-present at current authority location
  full sealed hash set equality
  schema, row identity, linked artifacts, and summary stable subset pass

A2 exact-hash restoration:
  exact-hash recoverable source found outside current authority location
  restored target path is current authority location or approved restored path
  restored bytes equal recoverable source bytes
  restored file hashes equal the full sealed hash set
  linked artifact restoration is complete or branch is blocked
  restore manifest and post-restore resolver check pass
```

* Branch B condition:

```text
artifact absent or hash mismatch
generation recipe exists
recipe_dry_run_status = pass
required current inputs are available from current_data_root_authority paths
or from fresh_generated_intermediate_from_current_data_root with same-round hash/provenance manifest
forbidden_old_staging_input count = 0
unresolved required current input count = 0
```

* Branch C condition:

```text
artifact absent or hash mismatch
recipe or required current inputs cannot support authoritative reconstruction
or explicit retirement/repointing instruction exists
C-2 repoint target is same-surface structural readpoint authority
or newly created explicit structural readpoint governance anchor
```

* If none match, stop branch execution and close only as `blocked_unresolved_anchor_authority`.
* If Branch C is selected, choose sub-branch:

```text
C-1 retirement only
C-2 repointing
```

Validation:

* Matrix is internally disjoint.
* Selected branch and rejected branches include evidence-backed reasons.
* Partial hash match cannot select Branch A1 or A2.
* Branch B feasibility does not imply reconstruction output adoption; output adoption remains a Phase 3 gate.
* `recipe_dry_run_status != pass` blocks Branch B selection.
* `precondition_status != confirmed` blocks all branch selection and uses `blocked_precondition_not_satisfied`.

---

### Change 4A - Phase 3 Branch A Restore

Purpose:

If the sealed artifact set is physically present and hash-identical, reaffirm it as current structural readpoint authority. If an exact-hash recoverable source is found outside the current authority location, materialize it through an exact-byte restoration path before reaffirming authority.

Files:

```text
Iris/build/description/v2/staging/compose_contract_migration/structural_signal_missing_anchor_authority_resolution_round/phase3_branch_a_restore_report.json
Iris/build/description/v2/staging/compose_contract_migration/structural_signal_missing_anchor_authority_resolution_round/phase3_branch_a_restore_manifest.json
```

Implementation Notes:

* Branch A has two subtypes:

```text
A1 already_present_reaffirmation
A2 exact_hash_artifact_restoration
```

* A1:
  * Do not modify the artifacts.
  * Record verified-present path and full hash match.
  * Verify current structural readpoint resolver locates the restored authority.
* A2:
  * Record `restored_source_path`, `restored_source_class`, `restored_target_path`, and whether target is the current authority location or an approved restored path.
  * Approved restored path is limited to paths explicitly enumerated in `phase0_scope_lock.json`. The default target is the current authority location.
  * Materialize only exact bytes from the recoverable source. No content rewrite, normalization, formatting, or schema editing is allowed.
  * Restore the linked artifact set under the same all-or-block rule: row, summary, source distribution, section distribution, overlap distribution, crosswalk, and artifact validation must all be restored or already present with matching hashes.
  * A2 partial restoration is not a recoverable Branch A success. If any linked artifact cannot be restored or verified, the selected branch closes as `blocked_unresolved_anchor_authority` rather than silently reclassifying the partial set.
  * Record pre-restore target absence or mismatch, source sha256, target post-restore sha256, and full sealed hash equality.
  * Treat exact-byte restoration as physical artifact materialization, not sealed body mutation. Any content edit or regenerated body is not Branch A.
* Draft docs addendum stating 2026-04-24 authority statement is reaffirmed.

Validation:

* Full hash set verification pass.
* A2 restore manifest exists and records source path, target path, byte identity, linked artifact status, and post-restore hash equality.
* Structural readpoint resolver pass.
* Current hard dependency missing count `0`.
* Runtime/rendered/publish/quality delta `0`.
* Python unittest pass.
* Lua syntax pass.

---

### Change 4B - Phase 3 Branch B Authoritative Reconstruction

Purpose:

If the old artifact is not restorable but current data-root inputs can support reconstruction, generate a new observer-only authoritative reconstruction artifact set and adopt it as the current structural readpoint authority.

Files:

```text
Iris/build/description/v2/staging/compose_contract_migration/structural_signal_missing_anchor_authority_resolution_round/phase3_branch_b_reconstruction/body_plan_structural_reclassification.reconstructed.2105.jsonl
Iris/build/description/v2/staging/compose_contract_migration/structural_signal_missing_anchor_authority_resolution_round/phase3_branch_b_reconstruction/body_plan_structural_reclassification.reconstructed.summary.json
Iris/build/description/v2/staging/compose_contract_migration/structural_signal_missing_anchor_authority_resolution_round/phase3_branch_b_reconstruction/reconstruction_input_manifest.json
Iris/build/description/v2/staging/compose_contract_migration/structural_signal_missing_anchor_authority_resolution_round/phase3_branch_b_reconstruction/reconstruction_hash_manifest.json
Iris/build/description/v2/staging/compose_contract_migration/structural_signal_missing_anchor_authority_resolution_round/phase3_branch_b_reconstruction/reconstruction_schema_report.json
Iris/build/description/v2/staging/compose_contract_migration/structural_signal_missing_anchor_authority_resolution_round/phase3_branch_b_reconstruction/reconstruction_distribution_report.json
Iris/build/description/v2/staging/compose_contract_migration/structural_signal_missing_anchor_authority_resolution_round/phase3_branch_b_reconstruction/reconstruction_delta_report.json
Iris/build/description/v2/staging/compose_contract_migration/structural_signal_missing_anchor_authority_resolution_round/phase3_branch_b_reconstruction/phase3_branch_b_reconstruction_report.json
```

Implementation Notes:

* Seal reconstruction basis:
  * generation recipe path,
  * generation recipe owner round,
  * Phase 1 `recipe_dry_run_status`,
  * required inputs and hashes,
  * input authority class,
  * same-round fresh intermediate provenance where used,
  * missing input disposition,
  * forbidden old-staging input count,
  * row identity baseline,
  * dual-axis schema contract.
* Allow reconstruction input from:

```text
current_data_root_authority
fresh_generated_intermediate_from_current_data_root
```

* `fresh_generated_intermediate_from_current_data_root` is allowed only when every upstream source path resolves under `Iris/build/description/v2/data/`, the generator is recorded, and the intermediate is hash-manifested in this same round.
* Forbid reconstruction input from:

```text
historical_provenance_only
forbidden_old_staging_input
diagnostic_fixture
missing
```

* Use staging/historical/diagnostic artifacts only as provenance/supporting trace.
* Output must be `writer_role: observer_only`.
* Output must not include `quality_state`, `publish_state`, or rendered text fields.
* Run generation twice and compare output hash.
* Compare reconstructed distributions to the historical documented distributions, but do not represent mismatch as restoration failure if the adopted object is explicitly a new reconstruction.
* Define linked artifact equivalence for Branch B as:

```text
schema_equivalence: same dual-axis canonical model and required fields
row_identity_equivalence: exact 2105-row identity match to current baseline
distribution_comparison: source/section/overlap distributions reported against 2026-04-24 historical distribution; mismatch allowed only with explicit delta report
```

* Seal new hash set under the new path. Preserve the 2026-04-24 hash set as historical reference.

Validation:

* Input classification report pass.
* Forbidden old-staging input count `0`.
* Unresolved required current input count `0`.
* `recipe_dry_run_status = pass`.
* Fresh generated intermediate provenance, if used, is complete and data-root-derived.
* Row count `2105`.
* Row identity exact match.
* Schema pass.
* Allowed overlap values only:

```text
source_only
section_only
coexist
dual_none
```

* Summary stable subset pass.
* Linked artifacts satisfy schema equivalence and row identity equivalence, with distribution comparison reported.
* 2-run determinism pass.
* Hash manifest pass.
* Runtime/rendered/publish/quality delta `0`.
* Python unittest pass.
* Lua syntax pass.

---

### Change 4C - Phase 3 Branch C Retirement or Repointing

Purpose:

If neither restoration nor authoritative reconstruction is valid, retire or repoint the readpoint so the old sealed path no longer functions as an ambiguous missing current authority.

Files:

```text
Iris/build/description/v2/staging/compose_contract_migration/structural_signal_missing_anchor_authority_resolution_round/phase3_branch_c_retirement_or_repointing/phase3_branch_c_retirement_or_repointing_report.json
Iris/build/description/v2/staging/compose_contract_migration/structural_signal_missing_anchor_authority_resolution_round/phase3_branch_c_retirement_or_repointing/dependency_scan_report.json
Iris/build/description/v2/staging/compose_contract_migration/structural_signal_missing_anchor_authority_resolution_round/phase3_branch_c_retirement_or_repointing/readpoint_retirement_or_repointing_decision.md
Iris/build/description/v2/staging/compose_contract_migration/structural_signal_missing_anchor_authority_resolution_round/phase3_branch_c_retirement_or_repointing/new_anchor_body.md
```

Implementation Notes:

* Scan build tools, validators, tests, docs, CI scripts, structural reclassification consumers, and decision/readpoint references.
* Dependency scan input enumeration:

```text
Iris/build/description/v2/tools/**/*.py
Iris/build/description/v2/tests/**/*.py
Iris/build/description/v2/staging/compose_contract_migration/**/manifest*.json
Iris/build/description/v2/staging/compose_contract_migration/**/*structural*.* 
Iris/build/description/v2/staging/compose_contract_migration/**/*body_plan_structural_reclassification*.*
docs/DECISIONS.md
docs/ARCHITECTURE.md
docs/ROADMAP.md
docs/Iris/**/*.md
.github/workflows/**
tools/**
```

If a glob is unavailable or no files match, record that result explicitly in `dependency_scan_report.json`; do not silently omit it.
* Classify references:

```text
current_hard_dependency
current_soft_reference
diagnostic_provenance_reference
historical_sealed_reference
stale_doc_reference
test_fixture_reference
```

* C-1 retirement only is allowed only when current hard dependency count is `0`.
* C-2 repointing is required when current hard dependencies exist and a replacement authority or reader-facing governance anchor can be identified.
* C-2 repoint target must be one of:

```text
same_surface_structural_readpoint_authority
new_explicit_structural_readpoint_governance_anchor
```

* The 2026-05-26 central anchor may be cited only as historical/vocabulary layering context. It is not sufficient replacement structural authority by itself.
* If `closed_with_readpoint_retired_or_repointed` is selected, closeout must record:

```text
closeout_subtype = retired | repointed
```

* Repoint tools/tests so old sealed path lookup is labeled retired-authority lookup, or points to the new C-2 structural anchor as applicable. The 2026-05-26 central anchor may be referenced only in explanatory context.
* Change error/report wording from `missing anchor` to `retired readpoint` or `repointed readpoint` when this branch mutates references.
* Do not mutate sealed historical bodies.

Validation:

* C-1: current hard dependency count `0`.
* C-2: every current hard dependency is repointed to the new authority or explicit anchor.
* C-2: repoint target is same-surface structural authority or a new explicit structural readpoint governance anchor.
* 2026-05-26 anchor is cited only as context, not replacement authority.
* `closeout_subtype` is present for `closed_with_readpoint_retired_or_repointed`.
* Old sealed path remains only as retired-authority, historical, diagnostic, or provenance reference.
* New C-2 anchor is reader-facing governance output and not sealed body mutation.
* Sealed hash invariant unchanged.
* Python unittest pass.

---

### Change 5 - Phase 4 Sealed Decision Trace Update

Purpose:

Prepare the governance trace update that records the selected branch result without rewriting existing sealed bodies.

Files:

```text
Iris/build/description/v2/staging/compose_contract_migration/structural_signal_missing_anchor_authority_resolution_round/phase4_sealed_decision_trace_update.md
docs/DECISIONS.md
docs/ROADMAP.md
docs/ARCHITECTURE.md
```

Implementation Notes:

* Append to `docs/DECISIONS.md` only after selected branch validation passes.
* Update `docs/ROADMAP.md` only after selected branch validation passes.
* Update `docs/ARCHITECTURE.md` by branch trigger:
  * Branch A: no update by default; existing Iris DVF 3-3 structural readpoint reference is reaffirmed.
  * Branch B: update the Iris DVF 3-3 production / body_plan readpoint summary if current authority path moves to the new reconstruction path.
  * Branch C: update the same summary if the prior structural reference becomes retired/repointed; C-2 adds the new structural anchor reference.
* Relationship to 2026-04-24:
  * Branch A: 2026-04-24 authority statement reaffirmed.
  * Branch B: 2026-04-24 structural authority statement superseded; 2026-04-24 hash set preserved as historical reference.
  * Branch C: 2026-04-24 structural authority statement superseded; sealed path retired or repointed; 2026-04-24 hash set preserved as historical reference.
* Relationship to 2026-04-22:
  * The 2026-04-22 staged/static closeout remains intact as a historical staged/static closeout.
  * Its Phase D output fact is not deleted or reinterpreted as runtime/deployed authority.
  * If a 2026-04-22 path-level statement conflicts with the selected Branch B/C current structural readpoint, only that downstream structural readpoint chain is superseded; staged/static status and Lua parity facts remain historical trace.
* Relationship to 2026-05-26:
  * Historical/staging bodies remain unmodified.
  * Current runtime vocabulary authority remains `adopted/unadopted`.
  * C-2 structural anchor, if present, must state that 2026-05-26 is vocabulary/historical layering context only and not the replacement structural authority.
* Explicitly block the interpretation that this supersedes the 2026-04-22 staged/static closeout as a whole.

Validation:

* Supersession scope is limited to the structural authority statement as selected by branch evidence.
* 2026-04-22, 2026-05-23, 2026-05-24, 2026-05-26, and 2026-05-27 readpoints remain consistent.
* Addenda are append-only and evidence-bound.

---

### Change 6 - Phase 5 Hard Gate

Purpose:

Fail-loud validation that the round reached one permitted outcome and preserved all immutable surfaces.

Files:

```text
Iris/build/description/v2/staging/compose_contract_migration/structural_signal_missing_anchor_authority_resolution_round/phase5_hard_gate_report.json
```

Implementation Notes:

Hard gate axes:

```text
G1 structural readpoint disposition resolved
G2 sealed body immutability
G3 sealed hash invariance
G4 runtime / Lua / staged invariance
G5 compose authority invariance
G6 scope guard
G7 other axis invariance
G8 user-facing surface invariance
G9 blocked_missing_anchor re-closure blocked
G10 Python unittest
G11 Lua syntax
```

G2 sealed body immutability methodology:

```text
Targets:
  DECISIONS.md sealed decision body sub-string set for 2026-04-22, 2026-04-24, 2026-05-26, and 2026-05-27 entries
  sealed staging artifact body file set referenced by the 2026-04-24 structural convergence closeout
  any hash-sealed artifact body file touched or referenced by this round

Measurement:
  DECISIONS.md sealed body sub-string equality against pre-round captured text, except additive new entries outside those sealed body ranges
  file-level sha256 invariance for sealed staging/hash-sealed artifact files
  Branch A2 exact-byte materialization is allowed only for absent targets restored from exact-hash source bytes; it is not allowed to alter an existing sealed body
```

G3 sealed hash invariance methodology:

```text
Targets:
  row sha256 6e84bb2f9622b79493473631d391a01c857c04ddbea869993a99856283ecb6d9
  summary sha256 8b6b7b34ba4c5de9bf6df6d8bcdfeacc6ec86ebda9f0c0b883672177d7b508cf
  source distribution sha256 1c8f8a3431d01f6780f8fe1a602db24ef3ae38febd936df0dec98e8fe80c41b0
  section distribution sha256 b587c663ba928bd7e6a9f8609caba9e3620c92acb6f3fa8359d868b558c0c490
  overlap distribution sha256 831303f7134bf7d8887efed18aaa69ee373fa1ae9b19002302fbb4ad32b973fc
  crosswalk sha256 3d60c945d958778ec89b13ab3efff93732726b969a11e4da9887247b488b817b
  artifact validation sha256 683323b9d52887d2ecf172e97bc6b8d7475a9ac3a8d04deec1db44fcf7c800a7

Branch A:
  sealed hash values are unchanged and restored/present files match them exactly.
Branch B:
  sealed hash values remain historical reference only; new reconstruction hashes are recorded under the new path and never overwrite the historical 7-set.
Branch C:
  sealed hash values and sealed files remain unchanged; old sealed path references are labeled retired-authority, historical, diagnostic, or provenance as selected.
```

Required validation commands:

```powershell
python -B -m unittest discover -s Iris\build\description\v2\tests -p "test_*.py"
```

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\check_lua_syntax.ps1
```

Validation:

* `phase5_hard_gate_report.json` is valid JSON.
* Every gate records `pass`, `fail`, `blocked`, or `not_applicable` with evidence.
* `blocked_missing_anchor` is not used as closeout state.
* Python command exits `0` with observed test count baseline or higher unless count variance is separately justified.
* Lua syntax command exits `0` with observed file count baseline or higher unless count variance is separately justified.

---

### Change 7 - Phase 6 Adversarial Review

Purpose:

Review the branch selection, supersession scope, sealed immutability, and non-claim boundary before final closeout.

Files:

```text
Iris/build/description/v2/staging/compose_contract_migration/structural_signal_missing_anchor_authority_resolution_round/phase6_adversarial_review.md
```

Implementation Notes:

* Review matrix application consistency.
* Review selected branch execution against branch-specific gates.
* Review that sealed bodies and hash-sealed artifacts were not modified.
* Review Phase 4 supersession scope.
* Review non-goals and forbidden claims.
* Review that `blocked_missing_anchor` re-closure is impossible in the closeout artifact.
* Verdict scale:

```text
PASS
FAIL
Conditional PASS
```

* `PASS` is required for success closeout.
* `Conditional PASS` or `FAIL` blocks final closeout until revised, re-reviewed to `PASS`, or explicitly converted to a blocked closeout.

Validation:

* Review file exists.
* Review verdict is `PASS` before Phase 7 success closeout.
* Findings are either resolved or cause blocked closeout.

---

### Change 8 - Phase 7 Final Closeout and Non-Claim Seal

Purpose:

Close the round with exactly one evidence-bound disposition and state the validation ceiling and non-claims.

Files:

```text
Iris/build/description/v2/staging/compose_contract_migration/structural_signal_missing_anchor_authority_resolution_round/phase7_closeout/closeout_report.md
Iris/build/description/v2/staging/compose_contract_migration/structural_signal_missing_anchor_authority_resolution_round/phase7_closeout/closeout_classification.json
docs/DECISIONS.md
docs/ROADMAP.md
```

Implementation Notes:

* Select exactly one closeout enum:

```text
closed_with_anchor_restored
closed_with_authoritative_reconstruction_adopted
closed_with_readpoint_retired_or_repointed
blocked_unresolved_anchor_authority
blocked_precondition_not_satisfied
```

* Include evidence bundle by closeout state:

```text
Success closeout:
  phase0_scope_lock.json
  phase1_inventory_report.json
  phase2_disposition_matrix.json
  phase2_disposition_decision.md
  selected phase3 branch report
  phase4_sealed_decision_trace_update.md
  phase5_hard_gate_report.json with PASS gates
  phase6_adversarial_review.md with PASS verdict
  closeout_report.md
  closeout_classification.json

blocked_unresolved_anchor_authority:
  phase0_scope_lock.json
  phase1_inventory_report.json
  phase2_disposition_matrix.json if reached, otherwise not_run
  selected or attempted phase report if reached, otherwise not_run
  phase5_hard_gate_report.json with failed/blocked axis
  phase6_adversarial_review.md if reached, otherwise not_run
  closeout_report.md with blocked reason
  closeout_classification.json

blocked_precondition_not_satisfied:
  phase0_scope_lock.json
  phase1_inventory_report.json with precondition_status != confirmed
  phase2_disposition_matrix.json recorded as not_run
  phase3 branch reports recorded as not_run
  phase4/phase5/phase6 recorded as not_run unless needed only to document blocked closeout
  closeout_report.md with precondition failure reason
  closeout_classification.json
```

Minimum success evidence bundle:

```text
phase0_scope_lock.json
phase1_inventory_report.json
phase2_disposition_matrix.json
phase2_disposition_decision.md
selected phase3 branch report
phase4_sealed_decision_trace_update.md
phase5_hard_gate_report.json
phase6_adversarial_review.md
closeout_report.md
closeout_classification.json
```

* Common mandatory non-claims:

```text
runtime rollout 아님
deployed closeout 아님
release readiness 아님
Workshop readiness 아님
manual in-game QA 아님
ACQ_DOMINANT remeasurement 아님
blanket isolation 아님
publish mutation review 아님
rendered rebaseline 아님
Lua regeneration 아님
```

* Branch B-only non-claims:

```text
reconstruction adoption is not old artifact restoration
old 2026-04-24 sealed hash set recovery 아님
```

* Branch C-only non-claims:

```text
retirement/repointing is not sealed body mutation
retirement/repointing is not obsolete declaration for the sealed artifact body
new C-2 anchor is reader-facing governance output, not a machine-enforced guard
```

Validation:

* All sealed bodies unmodified.
* Phase 5 gates pass or closeout is `blocked_unresolved_anchor_authority` / `blocked_precondition_not_satisfied`.
* Phase 6 review verdict is PASS for success closeout.
* Closeout JSON valid.
* Closeout MD present.
* Validation ceiling explicitly stated.
* No undeclared mutation.

---

## 7. Validation Plan

### Automated Validation

Required change review:

```powershell
git diff --stat
git diff
```

Required before success closeout:

```powershell
python -B -m unittest discover -s Iris\build\description\v2\tests -p "test_*.py"
```

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\check_lua_syntax.ps1
```

Required generated artifact validation:

```text
all hash equality / invariance checks use sha256
JSON parse for all generated JSON files
JSONL parse for all generated JSONL files
sha256 manifest for generated artifacts
sha256 comparison against sealed historical hashes when Branch A is considered
G2 sealed body immutability by DECISIONS.md sub-string equality and sealed artifact file sha256 invariance
G3 sealed hash 7-set branch-conditional invariance check
recipe dry-run/input-validation status before Branch B selection
2-run determinism check when Branch B is selected
reference/dependency scan when Branch C is selected
```

Required invariance checks:

```text
runtime Lua delta = 0
packaged Lua delta = 0
rendered text delta = 0
source decisions row content delta = 0
facts row content delta = 0
quality_state delta = 0
publish_state delta = 0
quality_baseline_v4 delta = 0
body_plan_signal_preservation.* delta = 0
compose_profiles_v2.json + body_plan authority unchanged
2026-05-27 data-root guard unchanged
staged Lua hash remains 0390272b93a933d7e53bba996b322ffbdd9fc905585bec03fc78d338f469f062
runtime hash manifest remains 790b5689097a8856e6213074fda25b723060073206a7ca44bd26d9f6f08c9171
```

If an exact command cannot be run, the result must be recorded as `blocked` or `not_run`, not `pass`.

### Manual Validation

Manual validation here means artifact/document inspection, not manual in-game QA. It is performed before Phase 6 and becomes an input to the Phase 6 adversarial review; the Phase 6 reviewer may re-check any manual validation item as part of adversarial review.

* Review Phase 1 candidate classifications for wrong-epoch or diagnostic artifacts.
* Review `precondition_status`; non-confirmed precondition must stop before Phase 2.
* Review `recipe_dry_run_status`; non-pass status must block Branch B.
* Review Phase 2 matrix selection for disjointness.
* Review Branch A A1/A2 hash evidence and A2 restore manifest if selected.
* Review Branch B input authority classification, fresh intermediate provenance, linked artifact equivalence axes, and determinism if selected.
* Review Branch C dependency scan, same-surface repoint target, `closeout_subtype`, and retired/repointed wording if selected.
* Review Phase 4 supersession scope.
* Review branch-conditional closeout non-claims.
* Review adversarial review verdict and unresolved findings.

### Validation Limits

This execution will not perform:

* runtime behavior validation
* manual in-game QA
* multiplayer validation
* long-session runtime validation
* deployment validation
* Workshop validation
* external mod compatibility sweep
* MIGV-QA Phase 1 identity pre-gate revalidation
* semantic axis revalidation
* quality axis revalidation
* publish axis revalidation
* runtime equivalence validation

---

## 8. Risk Surface Touch

### Authority Surface

Touched. The round resolves the current structural reclassification observer readpoint authority by restoration, new authoritative reconstruction, or retirement/repointing. It does not create writer authority.

### Runtime Behavior Surface

None expected. Runtime Lua, packaged Lua, rendered text, and runtime consumers are immutable for this round.

### Compatibility Surface

None expected. Resolver compatibility mapping, adapter disposition, diagnostic resolver mode, Browser/Wiki/Tooltip behavior, and external mod compatibility contracts are out of scope.

### Sealed Artifact Surface

Read-only for existing sealed artifacts. Branch B may create new hash-sealed reconstruction artifacts at a new path. Existing sealed bodies and hashes remain historical reference and must not be overwritten.

### Public-Facing Output Surface

None. The round does not change user-facing UI, copy, tooltip, wiki, browser behavior, packaging, release notes, Workshop state, or public release claims.

---

## 9. Risk Analysis

### Architecture Risk

* False restore: a partial or wrong-epoch artifact could be treated as restored. The plan blocks this with A1 full expected artifact presence plus full hash equality, or A2 exact-byte restoration from full-hash recoverable source plus restore manifest.
* False reconstruction: a count-only or shape-only artifact could be treated as authoritative. The plan requires current data-root authority or same-round data-root-derived intermediates, recipe dry-run pass, row identity, schema, determinism, and hash manifest.
* Authority contamination: staging artifacts could be used as current writer inputs. The plan forbids this and requires input classification.
* False retirement: missing old anchor could be declared obsolete without non-dependency proof. The plan requires Branch C proof and blocks `blocked_missing_anchor` re-closure.
* Supersession overreach: Phase 4 could accidentally supersede the 2026-04-22 staged/static closeout as a whole. The plan limits supersession to structural readpoint authority wording.
* Anchor ambiguity: C-2 could conflict with the 2026-05-26 central readpoint anchor. The plan requires same-surface structural authority or a new explicit structural readpoint governance anchor, with 2026-05-26 cited only as vocabulary/historical context.

### Runtime Risk

* Any runtime Lua, packaged Lua, rendered text, or chunk mutation is a stop-the-line violation.
* Lua syntax passing does not authorize runtime mutation; immutable-surface deltas must be zero.

### Compatibility Risk

* Tool/test repointing in Branch C could hide an unresolved dependency if a consumer is missed. The plan requires a full dependency scan over build tools, validators, tests, docs, CI scripts, and structural consumers.
* Diagnostic legacy single-slot views could be mistaken for current dual-axis authority. The plan requires explicit candidate classification.

### Regression Risk

* Linked artifact set could be incomplete even if row/summary files are present.
* Summary stable subset could pass while row-level identity fails.
* Historical distribution mismatch could be ignored during Branch B. The plan requires delta reporting and forbids calling reconstruction old artifact restoration.
* Validation could overclaim if commands are skipped. The plan requires exact command exit code `0` or blocked/not-run reporting.

---

## 10. Rollback Plan

Phase 0, Phase 1, and Phase 2 are observer-only except for round-local reports. Rollback is deletion or retention-as-failed-evidence of round-local artifacts.

Branch A rollback:

* A1 has no artifact mutation.
* A2 exact-byte restored artifacts may be removed or quarantined if restore validation fails, but only after verifying the target was created by this round and no unrelated user change is being removed.
* Discard or mark restore report as failed evidence if hash verification was wrong.

Branch B rollback:

* Remove or quarantine new reconstruction artifacts under the Branch B staging path.
* Do not modify or restore the 2026-04-24 sealed artifact path.
* If governance addenda were already appended, supersede them with additive correction entries rather than rewriting historical entries.

Branch C rollback:

* If tool/test repointing was applied before closeout, revert only the intended repointing changes after verifying no unrelated user changes are touched.
* If docs addenda were already appended, supersede with additive correction entries.

Common rollback rules:

* Runtime Lua chunks are not rollback targets because they must not change.
* Rendered text is not a rollback target because it must not change.
* `publish_state` and `quality_state` are not rollback targets because they must not change.
* Sealed bodies must not be rewritten during rollback.
* After failed rollback, close as `blocked_unresolved_anchor_authority`, not `blocked_missing_anchor`.

---

## 11. Governance Constraints

* `docs/Philosophy.md` remains the top authority.
* Iris remains 100% Lua wiki mode and does not alter Pulse Core or another spoke.
* Hub & Spoke and SPI boundaries remain untouched.
* Sealed decision immutability applies to 2026-04-22, 2026-04-24, 2026-05-26, and 2026-05-27 decision bodies.
* Hash-level immutability applies to existing sealed hash sets.
* Existing sealed artifacts are additive-only / read-only unless Branch A verifies physical identity or A2 materializes exact bytes from a full-hash recoverable source into an absent/approved restored target.
* Branch B must use a new path and new hash set.
* Branch B must not use old staging artifacts as current writer authority inputs.
* Branch B may use same-round fresh generated intermediates only when their full provenance is current-data-root-derived and hash-manifested.
* Single-writer compose authority remains `compose_profiles_v2.json + body_plan`.
* Structural reclassification remains observer authority only.
* Runtime Lua, rendered text, publish_state, quality_state, and current runtime hash manifest remain unchanged.
* Default compose current authority source-path guard remains unchanged.
* `count-only` and `shape-only` reconstruction are forbidden.
* Unknown state is not pass.
* `blocked_missing_anchor` re-closure is forbidden.
* `blocked_precondition_not_satisfied` is the only closeout allowed when the prior `blocked_missing_anchor` closeout precondition is missing or mismatched.
* Branch C repointing must use same-surface structural authority or a new explicit structural readpoint governance anchor; 2026-05-26 is context only.
* GUARD-A ownership remains unchanged.
* 2026-05-25 quality no-exposure contract remains unchanged.
* Non-goals from Section 2 and Section 3 remain prohibited unless a separate decision round explicitly opens them.

---

## 12. Expected Closeout State

Expected closeout target after execution is exactly one of:

```text
closed_with_anchor_restored
closed_with_authoritative_reconstruction_adopted
closed_with_readpoint_retired_or_repointed
blocked_unresolved_anchor_authority
blocked_precondition_not_satisfied
```

Closeout meaning:

| Closeout | Meaning |
|---|---|
| `closed_with_anchor_restored` | The expected 2026-04-24 artifact set is physically present, full sealed hash set matches, and the old current structural readpoint authority is restored. |
| `closed_with_authoritative_reconstruction_adopted` | A new observer-only reconstruction artifact set is generated from current data-root authority inputs, validated, hash-sealed at a new path, and adopted as current structural readpoint authority. The 2026-04-24 hash set becomes historical reference. |
| `closed_with_readpoint_retired_or_repointed` | The 2026-04-24 sealed path is retired or repointed, and the current structural readpoint status is unambiguous through same-surface structural authority or a new explicit structural readpoint governance anchor. Must include `closeout_subtype = retired | repointed`. |
| `blocked_unresolved_anchor_authority` | Restoration, reconstruction, and retirement/repointing all failed or could not be validated. Further progress requires new authority input or restored evidence. |
| `blocked_precondition_not_satisfied` | The prior `blocked_missing_anchor` closeout precondition is missing or mismatched in the governance readpoint, so branch selection is not allowed. |

`blocked_missing_anchor` is not an allowed expected closeout state for this plan.

Success criteria:

```text
current structural readpoint authority identity is single and unambiguous
sealed bodies remain unmodified
existing sealed hashes remain historical references
runtime Lua / packaged Lua / rendered text remain unchanged
staged Lua hash remains 0390272b93a933d7e53bba996b322ffbdd9fc905585bec03fc78d338f469f062
runtime hash manifest remains 790b5689097a8856e6213074fda25b723060073206a7ca44bd26d9f6f08c9171
compose_profiles_v2.json + body_plan authority remains unchanged
2026-05-27 data-root guard remains unchanged
quality_state / publish_state / quality_baseline_v4 remain unchanged
body_plan_signal_preservation.* remains unchanged
GUARD-A ownership remains unchanged
Python unittest exits 0
Lua syntax exits 0
adversarial review verdict PASS
```

Expected final claim boundary:

```text
This round resolves or blocks structural reclassification readpoint authority only.
It does not improve structural signal quality.
It does not remeasure ACQ_DOMINANT.
It does not alter runtime, rendered text, publish, quality, Browser, Wiki, Tooltip, or release state.
If reconstruction is adopted, it is a new current authority and not restoration of the missing old artifact.
```
