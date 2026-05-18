# Iris DVF 3-3 Silent Metadata Intake / Cleanup Round Plan

> 상태: Draft v0.1-plan  
> 기준일: 2026-05-18  
> 상위 기준: `docs/Philosophy.md`, `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`, `docs/EXECUTION_CONTRACT.md`  
> authority input: `Silent Metadata Intake / Cleanup Round - Synthesized Roadmap` (2026-05-18 user-provided synthesis)  
> 계획 형식: `docs/PLAN_TEMPLATE.md`  
> template attestation: this plan follows the 1-12 section structure in `docs/PLAN_TEMPLATE.md`.  
> 실행 상태: planning authority only. 이 문서는 `unadopted` 21 row의 legacy `compose_profile` metadata disposition round를 열기 위한 계획이며, 작성 시점에는 decisions/source metadata, rendered output, Lua bridge, runtime artifact, quality_state, publish_state, resolver code, adapter code, top-doc closeout state를 변경하지 않는다.

---

## 1. Objective

이번 execution plan의 목적은 active/adopted metadata migration 이후 `unadopted` 21 row에 남아 있는 legacy `compose_profile` metadata의 처분 branch를 봉인하고, 선택된 branch에 따라 cleanup 또는 permanent deferred disposition을 evidence-bounded closeout으로 닫는 것이다.

Round official name:

```text
Silent Metadata Intake / Cleanup Round
```

Disposition branches:

| Branch | Meaning | Expected `persisted_old_profile_count` | Status |
|---|---|---:|---|
| A | Keep as permanent deferred inventory | 21 | explicit user override only; not cleanup-complete |
| B | Unadopted-only rewrite to native body_plan profile metadata | 0 | default execution target |
| C | Row deletion | n/a | non-goal / excluded |

Recommended closeout target:

```text
Branch B:
  persisted_old_profile_count = 0
  silent_old_profile_count = 0
  adopted_count = 2084 unchanged
  unadopted_count = 21 unchanged
  row_count = 2105 unchanged
  rendered/Lua/runtime unchanged
```

This plan defaults Phase 2 to Branch B because it is the only branch that reaches canonical zero for persisted legacy profile metadata while preserving all runtime invariants. Branch A may be selected only by explicit user override and must close as `closed_with_permanent_deferred_inventory`, not as cleanup complete. Branch C is excluded before execution.

---

## 2. Scope

This round is a metadata disposition / cleanup round for the 21 `unadopted` rows previously sealed as `silent_metadata_inventory`. It is not an active resolver correctness round, adapter cleanup round, runtime rollout, release round, or QA round.

In scope:

* Round opening and read-point seal for `Philosophy.md`, `DECISIONS.md`, `ARCHITECTURE.md`, and `ROADMAP.md`.
* Recovery of the authoritative 21 row_id list from the historical sealed `silent_metadata_inventory` record or adopted replacement reconstruction authority.
* Baseline capture for row counts, adopted/unadopted split, old/native profile counts, rendered hash, Lua hash, and default fallback reach.
* A/B/C branch enumeration, with C declared non-goal.
* Single branch lock: A or B.
* Branch A no-op marker, if selected.
* Branch B unadopted-only metadata rewrite, if selected:
  * target row allowlist: Phase 1 authoritative 21 row_id list only
  * canonical row mutation allowlist: `compose_profile` field only
  * legacy value source: active migration sealed mapping or adopted replacement reconstruction mapping only
  * no inference, no shape-only promotion, no unknown-label repair
* Round artifacts under:

```text
Iris/build/description/v2/staging/compose_contract_migration/silent_metadata_intake_cleanup_round/
```

* Post-execution invariant verification.
* Hard gate report.
* Adversarial review.
* Documentation closeout entries after gates pass:
  * `docs/DECISIONS.md`
  * `docs/ROADMAP.md`
  * `docs/ARCHITECTURE.md`

### Explicitly Out Of Scope

* Branch C row deletion.
* Adoption expansion or `unadopted -> adopted` promotion.
* Runtime Lua rebaseline or regeneration.
* Adapter reintroduction.
* Diagnostic legacy mapping physical deletion.
* Resolver compatibility cleanup reopening.
* `selected_role`, `selected_role_precedence`, or `selected_role_target` removal or authority redefinition.
* Semantic quality reevaluation.
* `quality_state` mutation.
* `publish_state` mutation.
* Facts, rendered text, body_plan content, body text, or primary_use mutation.
* Source expansion.
* Manual in-game QA pass.
* Deployed closeout, Workshop release, or `ready_for_release` declaration.
* Multiplayer validation.
* Korean lexical re-validation.
* External mod compatibility sweep.
* `quality_baseline_v4 -> v5` cutover.
* New field slot addition to decisions schema.

---

## 3. Non-Goals

This plan does not attempt to:

* Reopen the active 2084 row metadata migration.
* Reopen `Diagnostic-only Resolver Compatibility Guard Round`.
* Reopen `Adapter / Diagnostic Compatibility Final Disposition Round`.
* Treat the 21 rows as resolver correctness blockers.
* Use shape-only probes to infer or promote row identity.
* Rewrite historical sealed decision bodies from `active/silent` to `adopted/unadopted`.
* Treat `unadopted` as deletion, suppression, publish state, or quality state.
* Claim runtime behavior validation from build-time no-delta checks.
* Add any row-level `cleanup_trace` or `migration_trace` field.

Trace handling:

```text
canonical row payload mutation allowlist = compose_profile only
round trace = stored in phase artifacts
row-level cleanup_trace/migration_trace = prohibited in this round
round trace = stored in phase artifacts only
```

---

## 4. Assumptions

Authority assumptions:

* `docs/Philosophy.md` is the top authority.
* Latest `DECISIONS.md`, `ARCHITECTURE.md`, and `ROADMAP.md` readpoints are authoritative.
* `active/silent` historical wording is read through the 2026-04-26 terminology migration:

```text
active -> adopted
silent -> unadopted
```

* Historical sealed decision bodies are not rewritten.
* `selected_role`, `selected_role_precedence`, and `selected_role_target` remain native resolver authority / trace.
* Resolver Compatibility / Adapter Cleanup category is closed as active correctness and residual disposition debt; this round must not reopen it.

Schema model:

```text
compose_profile is the canonical single field for both legacy and native profile values.
Branch B migration is value-namespace migration within this field.
It is not a field rename, not a new body_plan field addition, and not a schema expansion.
```

Round-entry baseline assumptions:

```text
total_row_count = 2105
adopted_count = 2084
unadopted_count = 21
active_old_profile_count = 0
active_native_profile_count = 2084
persisted_old_profile_count = 21
all_persisted_old_profile_count = 21  # explicit all-scope alias
silent_old_profile_count = 21
legacy_fallback_target_count = 0
default_path_legacy_fallback_reach_count = 0
default_adapter_dependency_count = 0
canonical_legacy_residue_count = 0
canonical_row_legacy_field_residue_count = 0  # adopted scope
adopted_scope_legacy_field_residue_count = 0
rendered_output_delta = 0
staged_lua_hash = 0390272b93a933d7e53bba996b322ffbdd9fc905585bec03fc78d338f469f062
runtime_state = ready_for_in_game_validation
```

Metric alias notes:

```text
persisted_old_profile_count = all_persisted_old_profile_count
canonical_row_legacy_field_residue_count = adopted_scope_legacy_field_residue_count
```

`all_persisted_old_profile_count` is retained only as an explicit hard-gate scope label. `persisted_old_profile_count` remains the historical all-scope metric name.

Authority artifact assumptions:

* The 21 row_id allowlist must come from the historical sealed `silent_metadata_inventory` record or from an adopted replacement reconstruction authority. Reconstructed counts alone remain non-authority.
* Expected historical record location, subject to Phase 1 confirmation:

```text
Iris/build/description/v2/staging/compose_contract_migration/adapter_native_body_plan_readiness_round/phase4_silent_inventory/silent_metadata_inventory.21.jsonl
```

* If the expected historical record is missing, execution must fail loud unless another pre-existing sealed canonical readpoint explicitly identifies the same 21 rows or a separate authority reconstruction round has closed with adopted replacement authority.
* AI-trace or reconstructed artifacts may be cited as supporting trace only unless the separate reconstruction round has explicitly adopted a replacement authority.
* AI-trace-only or shape-only artifacts cannot replace the historical sealed authority within this round.
* If the historical sealed inventory is missing and no pre-existing sealed canonical readpoint or adopted replacement reconstruction authority identifies the same 21 rows, this round must close as `blocked`.

2026-05-18 amendment:

```text
Input authority before:
  historical sealed authority

Input authority after:
  historical sealed authority
  OR adopted replacement reconstruction authority
```

The adopted replacement reconstruction authority is:

```text
Iris/build/description/v2/staging/compose_contract_migration/silent_21_replacement_authority_reconstruction_round/phase5_identity_crosscheck/silent_21_allowlist.candidate.jsonl
Iris/build/description/v2/staging/compose_contract_migration/silent_21_replacement_authority_reconstruction_round/phase6_mapping_authority/silent_21_mapping_authority.json
```

This amendment does not recover the missing original historical sealed artifacts byte-for-byte and does not execute Branch B rewrite.

Mapping assumptions for Branch B:

```text
interaction_tool -> tool_body
interaction_component -> material_body
interaction_output -> output_body
```

These inline values are expected values only, subject to Phase 1 verification against the sealed active metadata migration mapping artifact or adopted replacement reconstruction authority. The executor must load and use the sealed or adopted authority artifact, not these plan-body values. New inference, hardcoded plan-body authority, or unknown-label correction is forbidden.

Expected mapping authority artifact, subject to Phase 1 verification:

```text
Iris/build/description/v2/staging/compose_contract_migration/adapter_native_body_plan_metadata_migration_round/phase6_canonical_apply/migration_manifest.2084.jsonl
```

The Phase 1 mapping verification must derive the legacy-to-native mapping from that sealed artifact, byte-compare it with the expected values above, and fail loud on mismatch or missing authority.

---

## 5. Repository Areas Affected

### Code

Expected only if Branch B execution requires a deterministic executor or validator:

* `Iris/build/description/v2/tools/build/build_silent_metadata_intake_cleanup_round.py`

Allowed code work is limited to offline build-time tooling for this round. Runtime Lua, resolver default behavior, adapter behavior, and diagnostic mapping behavior are protected.

### Docs

Planning document:

* `docs/Iris/iris-dvf-3-3-silent-metadata-intake-cleanup-round-plan.md`

Closeout docs, only after Phase 5 and Phase 6 pass:

* `docs/DECISIONS.md`
* `docs/ROADMAP.md`
* `docs/ARCHITECTURE.md`

### Config

None expected.

If execution discovers a required config touch, the round must stop and either add a scoped Phase 2 amendment or close as blocked.

### Generated Artifacts

Allowed artifact root:

```text
Iris/build/description/v2/staging/compose_contract_migration/silent_metadata_intake_cleanup_round/
```

Recommended phase directories:

```text
phase0_read_point_seal/
phase1_baseline/
phase2_disposition_branch_lock/
phase3_execution/
phase4_invariant_verification/
phase5_hard_gate/
phase6_review/
phase7_closeout/
```

Forbidden generated artifacts:

* runtime Lua regeneration
* staged/workspace Lua rebaseline
* rendered text rebaseline
* quality/publish state mutation artifacts
* source expansion artifacts

---

## 6. Planned Changes

### Change 1

Purpose:

Open the round, seal scope, and capture read-point hashes before any branch decision or metadata mutation.

Files:

* `phase0_read_point_seal/phase0_read_point_seal.json`
* `phase0_read_point_seal/scope_lock.md`
* `phase0_read_point_seal/touched_surface_matrix.json`
* `phase0_read_point_seal/execution_scale_seal.json`

Implementation Notes:

* Seal official round name: `Silent Metadata Intake / Cleanup Round`.
* Seal execution scale:

```text
execution_scale = governance
round_type = cleanup / metadata disposition round
governed_surfaces_touched =
  - authoritative source metadata
  - sealed silent_metadata_inventory status
  - top-doc closeout entries
closeout_ceiling = metadata_cleanup
```

* Record authority order:

```text
Philosophy.md
DECISIONS.md
ARCHITECTURE.md
ROADMAP.md
approved roadmap / plan
EXECUTION_CONTRACT.md
local notes
```

* Capture current hashes for:
  * `docs/Philosophy.md`
  * `docs/DECISIONS.md`
  * `docs/ARCHITECTURE.md`
  * `docs/ROADMAP.md`
  * `docs/EXECUTION_CONTRACT.md`
  * `docs/PLAN_TEMPLATE.md`
* Record staged Lua hash target:

```text
0390272b93a933d7e53bba996b322ffbdd9fc905585bec03fc78d338f469f062
```

* Confirm the historical `silent_metadata_inventory` record location.
* Confirm `docs/EXECUTION_CONTRACT.md` and `docs/PLAN_TEMPLATE.md` exist before citing them; if either is absent, Phase 0 must remove or correct the reference before proceeding.
* State that adopted row mutation, runtime/Lua mutation, rendered mutation, quality mutation, and publish mutation are prohibited.

Validation:

* Scope lock names only the 21 `unadopted` legacy `compose_profile` rows.
* Adopted 2084 mutation prohibition is explicit.
* Runtime/Lua/rendered mutation prohibition is explicit.
* This cleanup is separated from active resolver correctness.
* Execution scale is declared as `governance`.
* `EXECUTION_CONTRACT.md` and `PLAN_TEMPLATE.md` existence/hash checks are recorded.

---

### Change 2

Purpose:

Capture Phase 1 baseline and recover the authoritative 21-row allowlist.

Files:

* `phase1_baseline/silent_metadata_baseline_snapshot.json`
* `phase1_baseline/phase1_unadopted_inventory_authority.json`
* `phase1_baseline/legacy_compose_profile_label_snapshot.jsonl`

Implementation Notes:

* Locate canonical decisions/source file at execution time and record it in the baseline snapshot.
* Locate and verify the sealed active metadata migration mapping artifact or adopted replacement reconstruction mapping artifact.
* Load the legacy-to-native mapping from that artifact; do not use plan-body inline values as executor authority.
* Write the mapping authority path and byte-equivalence result into `phase1_unadopted_inventory_authority.json`.
* Measure:

```text
row_count
adopted_count
unadopted_count
active_old_profile_count
active_native_profile_count
silent_old_profile_count
persisted_old_profile_count
rendered hash
rendered row-keyed text diff baseline
staged Lua hash
workspace Lua hash
default_path_legacy_fallback_reach_count
```

* Load exactly 21 row_id values from the historical sealed `silent_metadata_inventory` record or adopted replacement reconstruction allowlist.
* For each target row, snapshot:
  * row_id
  * current runtime_state literal
  * runtime_state literal warning status if value differs from historical `silent`
  * current legacy `compose_profile`
  * current native profile/body_plan profile metadata state
  * selected_role fields for negative invariant comparison
  * runtime_state, quality_state, publish_state
* Explicitly reject shape-only reconstruction or inferred promotion.
* Treat `unadopted` runtime_state literal as a warning marker at Phase 1, not a failure, because the 2026-04-26 vocabulary remap was docs-only and did not require static payload rewrite.

Validation:

```text
row_id count = 21
runtime_state_silent_count = 21 expected
unadopted_literal_runtime_state_count = 0 expected
unadopted_literal_runtime_state_count > 0 emits warning marker and requires Phase 2 reconciliation before execution
all target rows have non-null legacy compose_profile
all target rows are not adopted
active_old_profile_count = 0
active_native_profile_count = 2084
silent_old_profile_count = 21
persisted_old_profile_count = 21
rendered/Lua baseline captured
sealed/adopted mapping artifact path recorded
sealed/adopted mapping artifact byte-equivalence = pass
```

---

### Change 3

Purpose:

Seal the disposition branch before any execution.

Files:

* `phase2_disposition_branch_lock/phase2_disposition_branch_lock.json`
* `phase2_disposition_branch_lock/branch_comparison.md`
* `phase2_disposition_branch_lock/non_goals.md`
* `phase2_disposition_branch_lock/reopen_triggers.md`

Implementation Notes:

* Enumerate Branch A, Branch B, Branch C.
* Declare Branch C non-goal because it violates `row_count = 2105`.
* Select exactly one branch: A or B.
* Default selected branch is Branch B.
* Branch A requires explicit user override and must close as `closed_with_permanent_deferred_inventory`, not cleanup complete.
* If Branch B is selected, seal:

```text
row_id allowlist = Phase 1 authoritative 21 row_id list only
canonical row field allowlist = compose_profile only
legacy-to-native mapping = sealed active migration mapping only
mapping authority artifact path = explicit sealed artifact path
mapping byte-equivalence check = pass
unknown label behavior = fail-loud
inference path count = 0
2026-04-26 terminology hold = reconciled because runtime_state field is untouched
Phase 1 unadopted literal warning, if any = reconciled before execution without runtime_state write
```

Runtime-state literal reconciliation means explicit Phase 2 artifact acknowledgement that an `unadopted` literal is equivalent to historical `silent` for this round's invariant checks. It does not permit data mutation of the `runtime_state` field.

* If Branch A is selected, seal:

```text
persisted_old_profile_count = 21 as canonical permanent value
silent_metadata_inventory = permanent diagnostic-only non-authority inventory
closeout_state = closed_with_permanent_deferred_inventory
cleanup_complete_claim_allowed = false
```

* Set closeout ceiling to `metadata_cleanup`.

Validation:

* `chosen_branch` exists and is one of `A` or `B`.
* Branch C is excluded.
* Mutation surface is explicit.
* Non-goals are explicit.
* No release, QA, runtime, or resolver cleanup claim is introduced.

---

### Change 4

Purpose:

Execute the selected branch.

Files:

Branch A:

* `phase3_execution/phase3_no_op_marker.json`

Branch B:

* `phase3_execution/phase3_pre_execution_snapshot.json`
* `phase3_execution/phase3_execution_diff_report.json`
* optional deterministic executor under `Iris/build/description/v2/tools/build/`

Implementation Notes:

Branch A:

* Perform no source metadata mutation.
* Mark the 21 legacy rows as permanently deferred by decision artifact only.

Branch B:

* Read the Phase 1 row_id allowlist and Phase 2 field allowlist.
* Load the sealed or adopted legacy-to-native mapping artifact path recorded in Phase 1/2.
* Refuse to execute if the mapping artifact is missing, mismatched, or replaced by inline plan-body values.
* Before mutation, write a pre-execution snapshot sufficient for rollback.
* Iterate target rows in sorted row_id order.
* For each target row:
  * verify row_id is in allowlist
  * verify row is still historical `silent`; an `unadopted` literal must match the Phase 1 warning marker and must not be introduced by this round
  * verify current `compose_profile` is one of the sealed legacy labels
  * rewrite `compose_profile` to the sealed native value
  * leave every other canonical row field byte-for-byte equivalent
* Store cleanup trace in phase artifacts, not canonical row fields.
* If Phase 3 fail-louds mid-execution, immediately restore the 21 target rows from `phase3_pre_execution_snapshot.json`, close the round as `blocked`, and do not advance to Phase 4.
* Fail loud on:
  * allowlist miss
  * non-target row access
  * field other than `compose_profile`
  * unknown legacy label
  * missing or mismatched sealed/adopted mapping artifact
  * adopted row target
  * runtime_state, quality_state, or publish_state drift

Validation:

```text
Branch B:
  target row mutation count = 21
  compose_profile mutations = 21
  unknown label count = 0
  inference path count = 0
  sealed_mapping_artifact_loaded = true
  sealed_mapping_artifact_byte_equivalence = pass
  non-target row mutation count = 0
  adopted row mutation count = 0
  runtime_state_delta_count = 0
  quality_state_delta_count = 0
  publish_state_delta_count = 0
```

---

### Change 5

Purpose:

Run post-execution invariant verification.

Files:

* `phase4_invariant_verification/silent_metadata_inventory.after.json`
* `phase4_invariant_verification/phase4_invariant_verification_report.json`
* `phase4_invariant_verification/adopted_row_immutability_report.json`
* `phase4_invariant_verification/rendered_lua_parity_report.json`

Implementation Notes:

* Re-run baseline scan.
* Re-run legacy `compose_profile` scan.
* Compare rendered preview using Phase 1 captured canonical rendered preview artifact as source.
* Rendered parity method is full row-keyed rendered text diff plus aggregate hash comparison.
* Compare staged Lua hash and workspace Lua hash.
* Re-measure default resolver fallback reach.
* Compare all adopted rows against Phase 1 snapshot.
* Compare all non-target rows against Phase 1 snapshot.
* Compare selected_role fields and traces.

Validation:

```text
row_count = 2105
adopted_count = 2084
unadopted_count = 21
adopted_row_mutation_count = 0
non_target_row_mutation_count = 0
rendered_delta_count = 0
staged_lua_hash = 0390272b93a933d7e53bba996b322ffbdd9fc905585bec03fc78d338f469f062
workspace_lua_hash = unchanged vs Phase 1 baseline
default_path_legacy_fallback_reach_count = 0
default_adapter_dependency_count = 0
adopted_scope_legacy_field_residue_count = 0
canonical_row_legacy_field_residue_count = 0  # adopted scope alias only
selected_role / selected_role_precedence / selected_role_target unchanged
runtime_state_delta_count = 0
quality_state_delta_count = 0
publish_state_delta_count = 0
```

Branch-specific expected values:

```text
Branch A:
  all_persisted_old_profile_count = 21
  persisted_old_profile_count = 21
  silent_old_profile_count = 21

Branch B:
  all_persisted_old_profile_count = 0
  persisted_old_profile_count = 0
  silent_old_profile_count = 0
```

---

### Change 6

Purpose:

Run the hard gate and rollback if required.

Files:

* `phase5_hard_gate/phase5_hard_gate_report.json`
* `phase5_hard_gate/test_run_report.json`
* `phase5_hard_gate/shape_only_authority_promotion_check.json`

Implementation Notes:

* Hard gate must bind branch-specific expected state to common invariants.
* Execute the full Python test suite:

```powershell
python -B -m unittest discover -s Iris\build\description\v2\tests -p "test_*.py"
```

* Expected current baseline is `386 tests / OK` or the current repository equivalent at execution time.
* Verify that no shape-only probe was promoted to authority.
* Verify deterministic re-run: the Branch B executor, when rerun from identical Phase 3 pre-execution input in dry-run mode, produces byte-equivalent decisions payload and identical diff report.
* If Branch B fails a hard gate, restore the 21 rows from `phase3_pre_execution_snapshot.json` and rerun Phase 4/5.

Validation:

```text
hard_gate_report.overall_status = pass
full Python unittest suite = OK
shape_only_authority_promotion = false
executor_rerun_byte_equivalent = true  # Branch B only
adopted_scope_legacy_field_residue_count = 0
all_persisted_old_profile_count = 0   # Branch B only
all_persisted_old_profile_count = 21  # Branch A only
```

Rollback triggers:

```text
adopted_row_mutation_count > 0
rendered_delta_count > 0
staged_lua_hash_changed = true
workspace_lua_hash_changed = true
runtime_state_delta_count > 0
quality_state_delta_count > 0
publish_state_delta_count > 0
default_path_legacy_fallback_reach_count > 0
```

---

### Change 7

Purpose:

Perform adversarial review and close documentation only after evidence passes.

Files:

* `phase6_review/phase6_adversarial_review.md`
* `phase7_closeout/phase7_closeout.json`
* `phase7_closeout/silent_metadata_closeout_snapshot.json`
* `docs/DECISIONS.md`
* `docs/ROADMAP.md`
* `docs/ARCHITECTURE.md`

Implementation Notes:

Adversarial review must check:

* The 21-row allowlist came from historical sealed authority or adopted replacement reconstruction authority.
* Branch B, if selected, mutated only `compose_profile` on the 21 target rows.
* Adopted 2084 rows are untouched.
* No runtime/Lua/rendered mutation occurred.
* No resolver cleanup was reopened.
* No deployment, QA pass, or release readiness claim leaked into docs.

Documentation after PASS:

* Add a dated `DECISIONS.md` entry for this round.
* Add a concise `ROADMAP.md` Done entry.
* Add an `ARCHITECTURE.md` current-readpoint note that `silent_metadata_inventory` status moved from `sealed` to `disposed`.
* Record evidence artifact paths and reopen triggers.

Validation:

* `phase6_adversarial_review.md` verdict is `PASS`, or `Conditional PASS` followed by immediate fix and re-PASS.
* Docs claim no more than evidence proves.
* Closeout ceiling remains `metadata_cleanup`.
* Resolver Compatibility / Adapter Cleanup category is not reopened.

---

## 7. Validation Plan

### Automated Validation

Required command:

```powershell
python -B -m unittest discover -s Iris\build\description\v2\tests -p "test_*.py"
```

Required result:

```text
full unittest suite OK
```

Required audits:

* Row-count audit.
* Adopted/unadopted split audit.
* Legacy/native profile count audit.
* 21-row allowlist authority audit.
* Sealed legacy-to-native mapping artifact load and byte-equivalence audit.
* Per-row before/after diff audit.
* Adopted row immutability audit.
* Non-target row immutability audit.
* Rendered preview row-keyed text diff and aggregate hash audit.
* Staged Lua hash audit.
* Workspace Lua hash audit.
* Default resolver fallback reach audit.
* Selected-role preservation audit.
* Shape-only authority promotion negative audit.
* Deterministic executor re-run audit for Branch B.

Hard blockers:

* Missing historical sealed inventory authority and missing adopted replacement reconstruction authority.
* Missing sealed legacy-to-native mapping artifact authority and missing adopted replacement reconstruction mapping authority.
* Sealed mapping artifact mismatch.
* Any adopted row mutation.
* Any non-target row mutation.
* Unknown legacy label.
* Any inference path used for target mapping.
* Any rendered delta.
* Any staged/workspace Lua hash drift.
* Any runtime_state, quality_state, or publish_state drift.
* Failing Python test suite.

### Manual Validation

Manual validation is limited to artifact and diff review:

* Phase artifact inspection.
* Branch lock review.
* Per-row diff review.
* Adversarial review.
* Top-doc language review.

No manual in-game QA pass is performed or claimed.

### Validation Limits

This round will not perform:

* In-game runtime QA.
* Multiplayer validation.
* Long-session runtime validation.
* External mod compatibility sweep.
* Workshop packaging validation.
* Deployment validation.
* Korean lexical re-validation.
* Full release QA.

---

## 8. Risk Surface Touch

### Authority Surface

Touched.

* `unadopted` 21 row metadata disposition is authority-bearing source metadata.
* `silent_metadata_inventory` status changes only after closeout evidence passes.
* Top-doc entries are updated after hard gate and review.

### Runtime Behavior Surface

Expected none.

* Runtime Lua regeneration is forbidden.
* Rendered output delta must remain `0`.
* Runtime state remains `ready_for_in_game_validation`.

### Compatibility Surface

Expected none.

* Resolver compatibility mapping remains permanent diagnostic-only non-authority fixture.
* Adapter cleanup category remains closed.
* External compatibility is not measured or claimed.

### Sealed Artifact Surface

Protected.

* Sealed staged Lua hash must remain unchanged.
* Workspace Lua hash must remain unchanged versus Phase 1 baseline.
* Historical sealed decisions are preserved as historical trace.

### Public-Facing Output Surface

Expected none.

* Rendered text remains unchanged.
* User-facing runtime output remains unchanged.
* No release, deployed, or ready-for-release claim is introduced.

---

## 9. Risk Analysis

### Architecture Risk

* The round could be misread as active resolver cleanup rather than unadopted metadata disposition.
* Branch B could accidentally become adoption expansion if runtime_state is touched.
* `silent` / `unadopted` terminology could drift and blur historical trace.

### Runtime Risk

* A source metadata rewrite could accidentally regenerate or rebaseline Lua artifacts.
* Rendered parity could be claimed without full preview recompute.
* Workspace Lua hash could be compared against the wrong baseline.

### Compatibility Risk

* Diagnostic mapping preservation could be confused with legacy fallback authority.
* Adapter cleanup final disposition could be reopened by overbroad wording.
* Shape-only reconstructed row identity could replace historical authority if Phase 1 is weak.

### Regression Risk

* Branch B could mutate adopted rows through a broad script filter.
* Optional trace fields could break downstream schema if written into canonical rows.
* Unknown labels could be silently repaired instead of failing.
* Docs could overclaim metadata cleanup as release readiness.

---

## 10. Rollback Plan

Branch A:

* No payload mutation.
* Rollback is unnecessary.
* Future Branch B requires a separate reopen decision.

Branch B:

* Before mutation, write `phase3_pre_execution_snapshot.json`.
* If Phase 3 fail-louds mid-execution because of allowlist miss, unknown label, missing/mismatched mapping artifact, or drift detection, immediately restore the 21 target rows from `phase3_pre_execution_snapshot.json` and close the round as `blocked`. Do not advance to Phase 4.
* If Phase 4 or Phase 5 fails, restore only the 21 target rows from the snapshot.
* After restore, rerun Phase 4 and Phase 5.
* Preserve failed evidence artifacts as historical trace.
* If rollback cannot restore invariants, close as `blocked` and do not write top-doc closeout entries.

Immediate rollback triggers:

```text
adopted_row_mutation_count > 0
non_target_row_mutation_count > 0
rendered_delta_count > 0
staged_lua_hash_changed = true
workspace_lua_hash_changed = true
runtime_state_delta_count > 0
quality_state_delta_count > 0
publish_state_delta_count > 0
default_path_legacy_fallback_reach_count > 0
```

Documentation correction:

* If a docs claim error is found after closeout, do not delete the historical entry.
* Add a correction addendum preserving the original trace.

---

## 11. Governance Constraints

* `docs/Philosophy.md` compliance is mandatory.
* Hub & Spoke / SPI boundaries must remain intact.
* Iris remains a 100% Lua runtime module; this round is offline source metadata/docs/tooling only.
* Adopted 2084 rows are protected.
* `row_count = 2105` is protected.
* `adopted_count = 2084` and `unadopted_count = 21` are protected.
* `runtime_state`, `quality_state`, and `publish_state` are protected.
* `facts`, rendered text, body text, body_plan content, and primary_use are protected.
* `selected_role`, `selected_role_precedence`, and `selected_role_target` are protected native authority / trace.
* Runtime Lua regeneration is forbidden.
* Resolver code mutation is forbidden.
* Adapter reintroduction is forbidden.
* Diagnostic mapping deletion is forbidden.
* Shape-only probe authority promotion is forbidden.
* Closeout must disclose validation ceiling per `docs/EXECUTION_CONTRACT.md`.
* Top-doc updates must be additive and evidence-bounded.
* No deployed closeout, manual QA pass, Workshop release, or `ready_for_release` claim is allowed.

---

## 12. Expected Closeout State

Expected complete closeout if Branch B is selected and passes:

```text
complete:
  closeout_state = closed_with_unadopted_legacy_compose_profile_rewritten_to_native
  Silent Metadata Intake / Cleanup Round is closed with unadopted legacy compose_profile inventory rewritten to native body_plan profile metadata.

  persisted_old_profile_count = 0
  silent_old_profile_count = 0
  adopted 2084 unchanged
  unadopted 21 unchanged
  row_count 2105 unchanged
  rendered output unchanged
  staged/workspace Lua unchanged
  runtime_state unchanged
  quality_state unchanged
  publish_state unchanged
```

Expected complete closeout if Branch A is selected and passes:

```text
complete:
  closeout_state = closed_with_permanent_deferred_inventory
  Silent Metadata Intake / Cleanup Round is closed with unadopted legacy compose_profile inventory retained as permanent deferred diagnostic-only non-authority inventory.
  This is not cleanup-complete and does not reduce persisted legacy profile metadata.

  persisted_old_profile_count = 21
  silent_old_profile_count = 21
  adopted 2084 unchanged
  unadopted 21 unchanged
  row_count 2105 unchanged
  rendered output unchanged
  staged/workspace Lua unchanged
  runtime_state unchanged
  quality_state unchanged
  publish_state unchanged
```

Common final non-claims:

```text
This is not adoption expansion.
This is not source expansion.
This is not resolver compatibility reopening.
This is not diagnostic mapping deletion.
This is not adapter reintroduction.
This is not runtime Lua regeneration.
This is not manual in-game QA pass.
This is not deployed closeout.
This is not ready_for_release.
```

Reopen triggers:

* Any of the 21 rows is promoted to adopted/active runtime_state.
* New unadopted rows increase `persisted_old_profile_count` beyond the chosen branch canonical value.
* The 21 rows become reachable through default resolver path or writer path.
* The historical sealed `silent_metadata_inventory` record is damaged, lost, or fails integrity checks.
* Branch A only: retained legacy labels are promoted to default authority.
* Branch B only: rewritten native profile metadata causes determinism loss or hash drift.
* Adopted/unadopted vocabulary is architecturally redefined in a future round.
