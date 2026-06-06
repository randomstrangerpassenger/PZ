# Iris DVF 3-3 Silent 21 Replacement Authority Reconstruction Round Plan

> 상태: Draft v0.1-plan  
> 기준일: 2026-05-18  
> 상위 기준: `docs/Philosophy.md`, `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`, `docs/EXECUTION_CONTRACT.md`  
> authority input: `Silent 21 Replacement Authority Reconstruction Roadmap - Synthesized Final` (2026-05-18 user-provided synthesis)  
> review input: `REVIEW - Silent 21 Replacement Authority Reconstruction Round Plan - 종합 최종 검토안` Conditional PASS feedback (2026-05-19)  
> 계획 형식: `docs/PLAN_TEMPLATE.md`  
> template attestation: this plan follows the 1-12 section structure in `docs/PLAN_TEMPLATE.md`.  
> 실행 상태: planning authority only. 이 문서는 silent 21 cleanup rewrite 전에 필요한 replacement reconstruction authority 채택 계획이며, 작성 시점에는 source metadata, rendered output, Lua runtime artifact, resolver behavior, adapter disposition, runtime_state, quality_state, publish_state를 변경하지 않는다.

---

## 1. Objective

이번 execution plan의 목적은 `Silent Metadata Intake / Cleanup Round`가 요구한 original historical sealed authority artifacts 2개가 current checkout 및 local git history에 없다는 사실을 provenance gap으로 봉인하고, silent 21 cleanup 전용 replacement reconstruction authority를 새로 채택할 수 있는지 evidence-bounded 방식으로 판단하는 것이다.

Official round name:

```text
Silent 21 Replacement Authority Reconstruction Round
```

Round character:

```text
round_type = authority_reconstruction_prerequisite
execution_scale = governance-scale
mutation_round = false
cleanup_rewrite_round = false
```

Expected PASS closeout:

```text
closed_with_replacement_authority_adopted
```

Allowed BLOCKED closeouts:

```text
closed_blocked_replacement_authority_not_adopted
closed_blocked_conflicting_candidate_identity
closed_blocked_insufficient_provenance
```

PASS means only this:

```text
historical sealed authority absence = provenance gap sealed
shape-only candidate = rejected non-authority
AI-trace inventory = supporting trace only
sprint7 payload + dry-run post-migration decisions = primary reconstruction basis
silent 21 allowlist = adopted replacement authority
silent 21 mapping authority = interaction_tool -> tool_body
cleanup input authority rule may be amended to accept adopted replacement reconstruction authority
```

PASS does not mean silent metadata cleanup complete, runtime rollout, Lua regeneration, rendered rebaseline, manual in-game QA, Workshop readiness, or `ready_for_release`.

---

## 2. Scope

This round is an authority reconstruction prerequisite for the 21 silent/unadopted rows only. It creates and validates replacement authority artifacts, then prepares the cleanup round input-rule amendment. It does not execute cleanup rewrite.

In scope:

* Scope lock for the `Silent 21 Replacement Authority Reconstruction Round`.
* File-system and local git-history absence record for:
  * `silent_metadata_inventory.21.jsonl`
  * `migration_manifest.2084.jsonl`
* Provenance gap report for the missing original historical sealed artifacts.
* Pre-closure of two forbidden authority promotion paths:
  * shape-only candidate promotion
  * AI-trace-only authority promotion
* Candidate inventory intake with tier separation:
  * primary reconstruction candidates
  * supporting trace
  * rejected candidate
* Row-level identity cross-validation for the target 21 rows.
* Candidate allowlist artifact creation for silent 21 rows.
* Silent-only mapping authority seal:

```text
interaction_tool -> tool_body
```

* Replacement authority adoption or blocked closeout.
* Scope boundary seal proving no redefinition of active 2084 authority, resolver behavior, adapter disposition, rendered output, Lua artifact, runtime_state, quality_state, or publish_state.
* Cleanup input authority amendment artifact allowing:

```text
historical sealed authority OR adopted replacement reconstruction authority
```

* Top-doc readpoint updates:
  * PASS: `docs/DECISIONS.md`, `docs/ROADMAP.md`, and `docs/ARCHITECTURE.md` record adopted replacement authority readpoints.
  * BLOCKED: `docs/ROADMAP.md` records the blocked closeout reason at minimum. `docs/DECISIONS.md` and `docs/ARCHITECTURE.md` are updated only when the blocked result changes future authority policy or a persistent boundary/readpoint.

Round-local artifact root:

```text
Iris/build/description/v2/staging/compose_contract_migration/silent_21_replacement_authority_reconstruction_round/
```

Recommended phase directories:

```text
phase1_scope_lock/
phase2_provenance_gap/
phase3_forbidden_paths/
phase4_candidate_inventory/
phase5_identity_crosscheck/
phase6_mapping_authority/
phase7_adoption_decision/
phase8_scope_boundary_hard_gate/
phase9_cleanup_input_amendment/
```

### Explicitly Out Of Scope

* Silent 21 source metadata rewrite.
* `persisted_old_profile_count 21 -> 0`.
* Any canonical decisions/source metadata mutation.
* Active 2084 row revalidation or remigration.
* Frozen 2105 full recovery.
* Byte-level original sealed baseline recovery claim.
* Resolver cleanup.
* Adapter cleanup.
* Diagnostic compatibility mapping deletion.
* `selected_role`, `selected_role_precedence`, or `selected_role_target` removal.
* Rendered rebaseline.
* Lua regeneration.
* Runtime rollout.
* Manual in-game QA.
* Workshop readiness.
* `ready_for_release`.
* Public-facing output change.
* Treating replacement authority as full 2105 authority.

---

## 3. Non-Goals

This plan does not attempt to:

* Recover the missing historical sealed artifacts byte-for-byte.
* Replace active 2084 migration authority.
* Reopen sealed 2026-05-18 or earlier closeouts.
* Treat shape-only `2084 / 21` output as silent 21 authority.
* Treat AI-trace inventory as standalone authority.
* Use count shape as a substitute for row identity.
* Extend `interaction_tool -> tool_body` beyond the 21 silent rows.
* Change resolver default behavior or diagnostic resolver mode.
* Change adapter final disposition.
* Change rendered output, staged Lua, workspace Lua, runtime_state, quality_state, or publish_state.
* Claim cleanup completed.
* Claim runtime validation.
* Claim deployment, release readiness, or Workshop readiness.

Trace handling:

```text
replacement authority = newly adopted authority for silent 21 cleanup input only
original historical sealed artifact absence = preserved provenance gap
AI-trace = supporting trace only
shape-only candidate = non-authority
```

---

## 4. Assumptions

Authority assumptions:

* `docs/Philosophy.md` is the top authority.
* Latest `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, and `docs/ROADMAP.md` readpoints are authoritative.
* `docs/EXECUTION_CONTRACT.md` governs disclosure, evidence binding, and closeout ceiling for authority-surface work.
* Sealed decisions before and on 2026-05-18 are not reopened by this round.
* Iris interpretation, recommendation, and comparison prohibitions remain in force.
* Single-writer and determinism guarantees remain in force.
* Offline build authority and runtime Lua consumer remain separate.
* Current `body_plan` compose authority remains intact.
* Active 2084 metadata migration closeout remains intact.
* Selected-role native resolver authority remains intact.
* Resolver Compatibility / Adapter Disposition closeout remains intact.

Baseline assumptions at round entry:

```text
row_count = 2105
active_native_profile_count = 2084
persisted_old_profile_count = 21
silent_old_profile_count = 21
legacy_fallback_target_count = 0
default_path_legacy_fallback_reach_count = 0
adopted_scope_canonical_legacy_residue = 0
rendered output = unchanged
staged/workspace Lua = unchanged
runtime_state / quality_state / publish_state = unchanged
```

Evidence assumptions from current readpoints:

* Expected original sealed artifacts are absent from current checkout and local git history:
  * `silent_metadata_inventory.21.jsonl`
  * `migration_manifest.2084.jsonl`
* AI-trace silent inventory contains 21 rows but is supporting trace only.
* sprint7 2105-row payload contains 21/21 rows with:

```text
state = silent
compose_profile = interaction_tool
```

* dry-run post-migration decisions contain the same 21/21 row state/profile values.
* shape-only candidate is rejected because 18 rows drift active and row identity basis is insufficient.

---

## 5. Repository Areas Affected

### Code

Expected only if deterministic validation tooling is needed:

* `Iris/build/description/v2/tools/build/*silent_21*`
* `Iris/build/description/v2/tools/build/*replacement_authority*`

Any code work must be offline build/validation tooling only. Runtime Lua, resolver behavior, adapter behavior, and generated runtime artifacts are protected.

### Docs

This planning document:

* `docs/Iris/iris-dvf-3-3-silent-21-replacement-authority-reconstruction-round-plan.md`

Top-doc readpoint updates:

* `docs/DECISIONS.md`
* `docs/ROADMAP.md`
* `docs/ARCHITECTURE.md`

PASS updates record adopted replacement authority. BLOCKED updates record at least the ROADMAP blocked closeout reason and do not mark replacement authority as adopted.

Related downstream plan amendment target:

* `docs/Iris/iris-dvf-3-3-silent-metadata-intake-cleanup-round-plan.md`

### Config

None expected.

If execution discovers a required config touch, this round must stop and either add a scoped amendment or close as blocked.

### Generated Artifacts

Allowed generated artifact root:

```text
Iris/build/description/v2/staging/compose_contract_migration/silent_21_replacement_authority_reconstruction_round/
```

Expected generated artifacts:

* `round_scope_lock.md`
* `round_scope_lock.json`
* `provenance_gap_report.md`
* `provenance_gap_report.json`
* `forbidden_paths_seal.json`
* `shape_only_candidate_rejection_seal.md`
* `shape_only_candidate_rejection_seal.json`
* `candidate_inventory_index.json`
* `candidate_inventory_summary.md`
* `silent_21_row_identity_crosscheck.json`
* `silent_21_allowlist.candidate.jsonl`
* `silent_21_allowlist_diff_report.md`
* `silent_21_mapping_authority.md`
* `silent_21_mapping_authority.json`
* `replacement_authority_adoption_decision.md`
* `replacement_authority_adoption_decision.json`
* `scope_boundary_seal.json`
* `hard_gate_report.json`
* `cleanup_input_authority_amendment.md`
* `cleanup_input_authority_amendment.json`
* `cleanup_input_authority_amendment.blocked.md`
* `cleanup_input_authority_amendment.blocked.json`

Forbidden generated artifacts:

* runtime Lua regeneration artifacts
* rendered rebaseline artifacts
* source metadata rewrite artifacts for the 21 rows
* resolver cleanup artifacts
* adapter cleanup artifacts
* deployment or release-readiness artifacts

---

## 6. Planned Changes

### Change 1

Purpose:

Seal the round scope before any provenance or candidate work.

Files:

* `phase1_scope_lock/round_scope_lock.md`
* `phase1_scope_lock/round_scope_lock.json`
* `phase1_scope_lock/round_opening_baseline_snapshot.json`
* `phase1_scope_lock/protected_surface_hash_baseline.json`

Implementation Notes:

* Seal official round name:

```text
Silent 21 Replacement Authority Reconstruction Round
```

* Seal round type and closeout ceiling:

```text
round_type = governance_authority_reconstruction
cleanup_rewrite_executed = false
source_metadata_mutation = 0
rendered_lua_runtime_mutation = 0
closeout_ceiling = closed_with_replacement_authority_adopted
```

* Declare immutable surfaces:
  * active 2084 authority
  * resolver behavior
  * selected-role authority
  * adapter disposition
  * rendered output
  * staged/workspace Lua
  * runtime_state
  * quality_state
  * publish_state

* Freeze the hard gate baseline at round opening. The baseline is the round-opening workspace snapshot, not a missing frozen 2105 artifact.
* Capture and store:
  * `git status --short`
  * protected file hash list
  * rendered artifact hash, if the artifact exists
  * staged/workspace Lua hash, if the artifacts exist
  * runtime_state distribution
  * quality_state distribution
  * publish_state distribution
* If a protected file or baseline source cannot be found, record the field as `not_applicable` or `blocked`. Do not infer hashes or use frozen 2105 reconstruction as a substitute baseline.
* Non-drift proof must compare the exit state against this round-opening baseline by file hash, distribution snapshot, and protected file diff.

Validation:

```text
round_name = Silent 21 Replacement Authority Reconstruction Round
mutation_round = false
cleanup_rewrite_executed = false
runtime_surface_delta_expected = 0
out_of_scope_items_declared = true
hard_gate_baseline_source = round_opening_workspace_snapshot
frozen_2105_baseline_used = false
protected_surface_hash_baseline_captured = true
```

---

### Change 2

Purpose:

Seal the missing historical authority artifacts as a provenance gap.

Files:

* `phase2_provenance_gap/provenance_gap_report.md`
* `phase2_provenance_gap/provenance_gap_report.json`

Implementation Notes:

* Search current checkout and local git history for:
  * `silent_metadata_inventory.21.jsonl`
  * `migration_manifest.2084.jsonl`
* Record search commands, search scope, and absence findings.
* Separate absence of original historical sealed artifacts from adoption of replacement authority.
* Explicitly prohibit claims that the original sealed artifacts were recovered byte-for-byte.

Validation:

```text
historical_sealed_inventory_status = missing
sealed_migration_manifest_status = missing
provenance_gap_status = sealed
original_recovery_claim = false
```

Hard blocker:

* If the absence cannot be proven because the search scope is incomplete, close as `closed_blocked_insufficient_provenance`.

---

### Change 3

Purpose:

Pre-close forbidden authority promotion paths before candidate intake.

Files:

* `phase3_forbidden_paths/forbidden_paths_seal.json`
* `phase3_forbidden_paths/shape_only_candidate_rejection_seal.md`
* `phase3_forbidden_paths/shape_only_candidate_rejection_seal.json`

Implementation Notes:

* Reject shape-only 2084/21 candidate authority promotion because row state drift shows 18 rows active.
* Record that count-shape match is not row identity authority.
* Record that row identity 없는 preview cannot be cleanup authority.
* Seal AI-trace silent inventory as supporting trace only.
* Prohibit future cleanup input from using shape-only candidate or AI-trace-only authority.

Validation:

```text
shape_only_candidate_authority_status = rejected
row_identity_basis = insufficient
shape_only_future_cleanup_input_allowed = false
ai_trace_authority_status = supporting_trace_only
ai_trace_standalone_authority_allowed = false
```

---

### Change 4

Purpose:

Collect candidate inventories by authority tier.

Files:

* `phase4_candidate_inventory/candidate_inventory_index.json`
* `phase4_candidate_inventory/candidate_inventory_summary.md`

Implementation Notes:

Candidate tiers:

```text
Primary reconstruction candidates:
  - sprint7 2105-row payload
  - dry-run post-migration decisions

Supporting trace:
  - AI-trace silent inventory 21 row

Rejected candidate:
  - shape-only candidate
```

Primary candidate path resolution rule:

```text
exact path, if already known and present, has priority.
if exact path is absent, a candidate must satisfy all approved discovery constraints:
  - approved search root
  - filename pattern
  - required schema
  - required row_count
  - required state / compose_profile fields
if two or more candidates satisfy the rule, automatic selection is prohibited.
if duplicate candidates have identical content hash, record them as equivalent mirrors.
if duplicate candidates differ by content hash or row identity, close as
  closed_blocked_conflicting_candidate_identity
  or open a separate provenance diagnostic before adoption.
```

For each candidate record:

* source path
* row count
* row identity key fields
* state values
* compose_profile values
* accepted/rejected/supporting tier
* candidate hash if available

Validation:

```text
primary_candidate_count = 2
supporting_trace_count = 1
rejected_candidate_count >= 1
source_path_recorded = true
row_identity_key_recorded = true
tier_separation_pass = true
primary_candidate_path_resolution_status = unique | equivalent_mirror | blocked
automatic_candidate_selection_from_conflict = false
```

---

### Change 5

Purpose:

Cross-validate the 21-row identity set across primary candidates and supporting trace.

Files:

* `phase5_identity_crosscheck/silent_21_row_identity_crosscheck.json`
* `phase5_identity_crosscheck/silent_21_allowlist.candidate.jsonl`
* `phase5_identity_crosscheck/silent_21_allowlist_diff_report.md`

Implementation Notes:

Target population definition authority:

```text
target_21_population_authority =
  sprint7 2105-row payload state=silent row set
  AND dry-run post-migration decisions state=silent row set

AI-trace 21-row inventory =
  supporting trace only; it verifies whether the primary set has the same
  row identity, but it does not define the target population.
```

The sprint7 silent set and dry-run silent set must be 21/21 identical before AI-trace comparison is considered. If the two primary sets are not identical, Phase 5 closes as `closed_blocked_conflicting_candidate_identity`.

Row identity key rule:

```text
preferred key = item_id
fallback key = full_type
key invariant =
  item_id and full_type are both present and equivalent for all 21 rows,
  or Phase 5 explicitly seals which one is authoritative and why.
```

Cross-check axes:

* `item_id` or `full_type`
* `state`
* `compose_profile`
* sprint7 payload presence
* dry-run post-migration decisions presence
* AI-trace inventory presence as supporting comparison

Allowlist row schema:

```json
{
  "item_id": "Base.Example",
  "full_type": "Base.Example",
  "state": "silent",
  "compose_profile": "interaction_tool",
  "sprint7_presence": true,
  "dry_run_presence": true,
  "ai_trace_presence": true,
  "authority_status": "candidate_replacement_authority"
}
```

Validation:

```text
target_row_count = 21
sprint7_silent_row_count = 21
dry_run_silent_row_count = 21
sprint7_dry_run_identity_set_equal = true
target_population_defined_by_ai_trace = false
matched_row_count = 21
missing_row_count = 0
extra_row_count = 0
state_conflict_count = 0
compose_profile_conflict_count = 0
identity_key_invariant = pass
source_profile_set = ["interaction_tool"]
```

Failure branch:

```text
if matched_row_count != 21
or sprint7_silent_row_count != 21
or dry_run_silent_row_count != 21
or sprint7_dry_run_identity_set_equal != true
or missing_row_count > 0
or extra_row_count > 0
or state_conflict_count > 0
or compose_profile_conflict_count > 0:
  closeout = closed_blocked_conflicting_candidate_identity
```

---

### Change 6

Purpose:

Seal silent-only mapping authority.

Files:

* `phase6_mapping_authority/silent_21_mapping_authority.md`
* `phase6_mapping_authority/silent_21_mapping_authority.json`

Implementation Notes:

Adopt candidate mapping only for the 21 silent rows:

```text
interaction_tool -> tool_body
```

The mapping seal must explicitly state:

* affected row count is 21.
* active 2084 affected count is 0.
* resolver compatibility mapping is separate.
* adapter diagnostic mapping disposition is separate.
* this mapping does not authorize default resolver fallback behavior.
* this mapping does not extend to full 2105 authority.
* the mapping is semantically consistent with the adopted sentence_plan 3-profile to body_plan 6-profile authority migration readpoint in `docs/DECISIONS.md` and the local profile migration spec.

Mapping semantic correctness audit:

```text
source authority trace =
  DECISIONS.md sentence_plan 3-profile -> body_plan 6-profile replacement readpoint
  and local profile migration spec mapping
required mapping row =
  interaction_tool -> tool_body
semantic_audit_result = pass
```

Validation:

```text
source_profile_set = ["interaction_tool"]
target_profile_set = ["tool_body"]
affected_row_count = 21
active_row_affected_count = 0
resolver_behavior_delta_expected = 0
adapter_surface_delta_expected = 0
rendered_lua_runtime_delta_expected = 0
mapping_semantic_correctness_audit = pass
```

---

### Change 7

Purpose:

Adopt or block the replacement authority.

Files:

* `phase7_adoption_decision/replacement_authority_adoption_decision.md`
* `phase7_adoption_decision/replacement_authority_adoption_decision.json`

Implementation Notes:

PASS requires all prior gates:

```text
provenance_gap_status = sealed
shape_only_candidate_authority_status = rejected
ai_trace_authority_status = supporting_trace_only
silent_21_identity_crosscheck = pass
silent_21_mapping_authority = pass
non_drift_expectation = pass
```

Adoption decision fields:

```json
{
  "replacement_authority_status": "adopted | blocked",
  "closeout_branch": "closed_with_replacement_authority_adopted | closed_blocked_replacement_authority_not_adopted | closed_blocked_conflicting_candidate_identity | closed_blocked_insufficient_provenance",
  "replacement_scope": "silent_21_cleanup_only",
  "mapping_scope": "silent_21_cleanup_write_authority_not_resolver_compatibility_mapping",
  "original_historical_authority_recovery_claim": false,
  "cleanup_rewrite_executed": false
}
```

Validation:

```text
replacement_21_allowlist_status = adopted
silent_21_mapping_authority_status = adopted
cleanup_rewrite_executed = false
source_metadata_mutation = 0
replacement_scope = silent_21_cleanup_only
mapping_scope = silent_21_cleanup_write_authority_not_resolver_compatibility_mapping
```

---

### Change 8

Purpose:

Seal scope boundary and run the hard gate proving no unexpected drift.

Files:

* `phase8_scope_boundary_hard_gate/scope_boundary_seal.json`
* `phase8_scope_boundary_hard_gate/hard_gate_report.json`

Implementation Notes:

Scope boundary must assert non-redefinition of:

* active 2084 authority
* resolver behavior
* selected-role authority
* adapter disposition
* rendered output
* staged/workspace Lua
* runtime_state
* quality_state
* publish_state

Hard gate expected values:

```text
active_native_profile_count = 2084
row_count = 2105
persisted_old_profile_count = 21
silent_old_profile_count = 21
default_path_legacy_fallback_reach_count = 0
adopted_scope_canonical_legacy_residue = 0
rendered output hash = unchanged
staged-workspace Lua hash = unchanged
runtime_state distribution = unchanged
quality_state distribution = unchanged
publish_state distribution = unchanged
```

Required validation command:

```powershell
python -B -m unittest discover -s Iris\build\description\v2\tests -p "test_*.py"
```

Hard gate measurement source mapping:

| Hard gate field | Measurement source |
|---|---|
| `active_native_profile_count = 2084` | source metadata count audit over round-opening protected source set |
| `row_count = 2105` | source metadata row-count audit |
| `persisted_old_profile_count = 21` | legacy compose_profile scan over all rows |
| `silent_old_profile_count = 21` | legacy compose_profile scan scoped to silent rows |
| `default_path_legacy_fallback_reach_count = 0` | default-path reach probe or existing guard-round measurement script, recorded as an artifact |
| `adopted_scope_canonical_legacy_residue = 0` | adopted-scope legacy residue scanner |
| `rendered output hash = unchanged` | round-opening rendered hash baseline vs exit rendered hash; `not_applicable` only if no rendered artifact exists |
| `staged-workspace Lua hash = unchanged` | round-opening staged/workspace Lua hash baseline vs exit hash |
| `runtime_state / quality_state / publish_state distribution = unchanged` | round-opening distribution snapshot vs exit distribution snapshot |

`full unittest suite OK` is a regression guard. It is not the sole adoption authority. Replacement authority adoption depends on provenance gap sealing, candidate tiering, primary row-identity crosscheck, mapping authority, scope boundary assertions, and the non-drift hard gate above.

Validation:

```text
scope_boundary_surface_count >= 9
all_scope_boundary_assertions = pass
hard_gate_report.overall_status = pass
full Python unittest suite = OK
hard_gate_measurement_source_map_complete = true
unittest_suite_role = regression_guard
cleanup_rewrite_executed = false
```

Validation note:

Do not claim validation passed unless the exact command exits with code 0. If Python or the test suite is unavailable, record validation as blocked, not passed.

---

### Change 9

Purpose:

Seal cleanup input authority amendment artifacts and update top-doc readpoints after PASS or record blocked closeout readpoints when needed.

Files:

* `phase9_cleanup_input_amendment/cleanup_input_authority_amendment.md`
* `phase9_cleanup_input_amendment/cleanup_input_authority_amendment.json`
* `phase9_cleanup_input_amendment/cleanup_input_authority_amendment.blocked.md`
* `phase9_cleanup_input_amendment/cleanup_input_authority_amendment.blocked.json`
* `docs/DECISIONS.md`
* `docs/ROADMAP.md`
* `docs/ARCHITECTURE.md`
* optional amendment to `docs/Iris/iris-dvf-3-3-silent-metadata-intake-cleanup-round-plan.md`

Implementation Notes:

Phase 9 is split into two ordered substeps:

```text
9a. cleanup_input_authority_amendment artifact seal
9b. top-doc readpoint update or blocked readpoint record
```

Cleanup input rule amendment:

```text
Before:
  Input authority: historical sealed authority

After:
  Input authority: historical sealed authority
                   OR adopted replacement reconstruction authority
```

Required conditions:

```text
amendment_applies_only_if = closed_with_replacement_authority_adopted
silent_only_scope = true
cleanup_rewrite_executed = false
source_metadata_mutation = 0
```

PASS branch documentation rule:

```text
If closeout = closed_with_replacement_authority_adopted:
  DECISIONS / ROADMAP / ARCHITECTURE are updated as adopted replacement authority readpoints.
  cleanup input authority rule amendment may be applied.
  cleanup_input_authority_amendment.md/.json are generated with status = applied_or_applicable.
```

BLOCKED branch documentation rule:

```text
If closeout is blocked:
  ROADMAP records the blocked closeout reason at minimum.
  DECISIONS records the blocked result only if it changes future authority policy.
  ARCHITECTURE is updated only when a persistent boundary/readpoint changes.
  cleanup input authority rule amendment is not applied.
  cleanup_input_authority_amendment.blocked.md/.json are generated with status = not_applied.
  replacement authority is not marked adopted.
```

`docs/DECISIONS.md` addendum target:

```text
2026-05-18 - Silent 21 Replacement Authority Reconstruction Round closes with adopted replacement authority
```

`docs/ROADMAP.md` update target:

* Iris Done: reconstruction closeout added.
* Iris Next: cleanup rewrite round reopen condition added.
* Iris Hold: shape-only authority promotion forbidden.

`docs/ARCHITECTURE.md` update target:

* Replacement authority is silent 21 cleanup only.
* Active 2084 / resolver / adapter / rendered / Lua / runtime authority are not redefined.
* AI-trace is supporting trace.
* Shape-only candidate is non-authority.

Validation:

```text
cleanup_plan_input_rule_accepts_adopted_replacement_authority = true
cleanup_rewrite_executed = false
source_metadata_mutation = 0
top_doc_runtime_release_claim = false
historical_recovery_claim = false
silent_only_scope_declared = true
blocked_branch_roadmap_record_rule = present
pass_branch_amendment_rule = present
claim_wording_audit = pass
amendment_and_top_doc_recovery_word_absence_audit = pass
cleanup_completed_runtime_release_wording_absence_audit = pass
```

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

The unittest suite is a regression guard. It does not replace the provenance, candidate tiering, row identity, mapping authority, and non-drift audits listed below.

Required audits:

* Missing historical sealed artifact search audit.
* Candidate tier separation audit.
* Primary candidate source path resolution and uniqueness audit.
* Shape-only candidate rejection audit.
* AI-trace supporting-only audit.
* Target 21-row population authority audit proving sprint7 and dry-run silent sets define the population.
* 21-row identity cross-check.
* Row identity key invariant audit for `item_id` / `full_type`.
* Mapping authority scope audit.
* Mapping semantic correctness audit.
* Active 2084 non-impact audit.
* Resolver behavior non-impact audit.
* Adapter disposition non-impact audit.
* Round-opening hard gate baseline freeze audit.
* Hard gate measurement source mapping audit.
* Rendered hash non-drift audit.
* Staged/workspace Lua hash non-drift audit.
* runtime_state / quality_state / publish_state distribution non-drift audit.
* Cleanup input authority amendment language audit.
* Top-doc non-claim audit.

Hard blockers:

* Incomplete file-system or git-history absence search.
* Non-unique or conflicting primary candidate source path resolution.
* Conflicting 21-row identity.
* Any attempt to define the target population from AI-trace.
* Any missing row in primary candidate cross-check.
* Any extra row in primary candidate cross-check.
* Any state or compose_profile conflict.
* Missing hard gate baseline snapshot.
* Missing hard gate measurement source for any required value.
* Any attempt to use shape-only candidate as authority.
* Any attempt to use AI-trace as standalone authority.
* Any mutation to source metadata, rendered output, runtime Lua, resolver behavior, adapter disposition, runtime_state, quality_state, or publish_state.
* Failing Python test suite.

### Manual Validation

Manual validation is limited to artifact and documentation review:

* Provenance gap report review.
* Candidate inventory summary review.
* Row identity diff report review.
* Mapping authority review.
* Scope boundary seal review.
* Cleanup input amendment wording review.
* Top-doc addendum language review.

No manual in-game QA pass is performed or claimed.

### Validation Limits

This round will not perform:

* Runtime validation.
* Deployment validation.
* Long-session runtime validation.
* Multiplayer validation.
* External ecosystem compatibility sweep.
* Manual in-game QA.
* Lua regeneration parity validation.
* Rendered output rebaseline.
* Full 2105 byte-level historical baseline recovery validation.
* Silent 21 cleanup rewrite verification.

---

## 8. Risk Surface Touch

### Authority Surface

Touched.

* Provenance readpoint for missing historical sealed artifacts.
* Silent 21 replacement allowlist authority.
* Silent-only mapping authority.
* Cleanup plan input authority rule.
* Top-doc readpoints after PASS, or blocked closeout reason records after BLOCKED.

This is not original historical authority recovery.

### Runtime Behavior Surface

Expected none.

* No resolver behavior change.
* No runtime Lua regeneration.
* No rendered output change.
* No in-game behavior claim.

### Compatibility Surface

Expected no direct change.

* Legacy compatibility mapping remains permanent diagnostic-only non-authority fixture.
* Adapter final disposition remains closed and unchanged.
* External compatibility is not measured or claimed.

### Sealed Artifact Surface

Touched only through new replacement authority artifacts.

* Existing sealed artifacts are not rewritten.
* Missing historical artifacts remain recorded as missing.
* Newly generated authority artifacts are stored under this round's staging root.

### Public-Facing Output Surface

Expected none.

* Tooltip, Browser, Wiki, rendered text, Lua output, and public UI remain unchanged.
* No release-facing claim is introduced.

---

## 9. Risk Analysis

### Architecture Risk

* Replacement authority could be misread as full 2105 authority.
* Missing historical artifacts could be obscured by weak equivalence language.
* The cleanup amendment could be read as cleanup execution.
* Active 2084 authority could be accidentally redefined by overbroad mapping language.

### Runtime Risk

* A governance-only round could accidentally trigger generated runtime artifact work.
* Hard gate could compare against the wrong Lua/rendered baseline.
* Runtime state could be overclaimed without runtime validation.

### Compatibility Risk

* `interaction_tool -> tool_body` could be confused with resolver compatibility mapping.
* Adapter diagnostic disposition could be reopened through imprecise wording.
* Legacy compatibility mapping could be treated as default resolver fallback authority.

### Regression Risk

* Row count could match while row identity differs.
* AI-trace could silently become primary authority because it is convenient.
* Shape-only candidate could be reused in future cleanup inputs.
* Top-doc addenda could overclaim cleanup complete, runtime readiness, or release readiness.

---

## 10. Rollback Plan

This round should not mutate canonical source metadata, rendered output, Lua runtime artifacts, resolver behavior, adapter disposition, runtime_state, quality_state, or publish_state. Rollback is therefore documentation/artifact containment.

If a problem is found before adoption:

```text
replacement_authority_status = blocked
closeout = closed_blocked_replacement_authority_not_adopted
cleanup input amendment = not applied
silent 21 cleanup = deferred inventory branch
```

If Phase 5 identity cross-check fails:

```text
closeout = closed_blocked_conflicting_candidate_identity
replacement authority adoption = false
silent 21 cleanup = deferred inventory branch
```

If Phase 8 hard gate fails:

```text
closeout = closed_blocked_insufficient_provenance
or closed_blocked_replacement_authority_not_adopted
cleanup rewrite opening = prohibited
separate diagnostic round required
```

If an adopted decision is later found invalid:

* Do not delete generated artifacts.
* Mark the adoption decision superseded or corrected.
* Mark cleanup input authority amendment inactive or superseded.
* Add corrective addenda to `docs/DECISIONS.md`, `docs/ROADMAP.md`, and `docs/ARCHITECTURE.md`.
* Preserve rejected/superseded artifacts as provenance.
* Block subsequent cleanup rewrite opening until a new authority decision is sealed.

Forbidden rollback methods:

* history rewrite to silently remove adopted records
* reusing rejected shape-only candidate
* forcing silent 21 cleanup after failed reconstruction

---

## 11. Governance Constraints

* `docs/Philosophy.md` compliance is mandatory.
* Iris interpretation, recommendation, and comparison prohibitions remain in force.
* Hub & Spoke / SPI boundaries must remain intact.
* Single-writer principle must remain intact.
* Determinism guarantee must remain intact.
* Sealed decisions before and on 2026-05-18 must not be reopened.
* Three-axis contract remains intact:
  * runtime_state
  * quality_state
  * publish_state
* Offline build authority and runtime Lua consumer remain separate.
* Authority ownership is preserved.
* Current `body_plan` compose authority is preserved.
* Active 2084 metadata migration closeout is preserved.
* Selected-role native resolver authority is preserved.
* Resolver behavior change is forbidden.
* Adapter disposition change is forbidden.
* Rendered output change is forbidden.
* Lua runtime artifact change is forbidden.
* runtime_state / quality_state / publish_state redefinition is forbidden.
* Shape-only candidate authority promotion is forbidden.
* AI-trace standalone authority is forbidden.
* Replacement authority must not be expanded to full 2105 authority.
* Historical sealed artifact absence must remain visible as provenance gap.
* Top-doc updates must be additive and evidence-bounded.
* No cleanup completed, runtime rollout, Lua regeneration, Workshop readiness, or `ready_for_release` claim is allowed.

---

## 12. Expected Closeout State

Expected complete closeout on PASS:

```text
complete:
  closeout_state = closed_with_replacement_authority_adopted

  historical_sealed_authority_status = missing_provenance_gap_sealed
  shape_only_candidate_authority_status = rejected
  ai_trace_inventory_status = supporting_trace_only
  replacement_21_allowlist_status = adopted
  silent_21_mapping_authority_status = adopted
  mapping = interaction_tool -> tool_body
  affected_row_count = 21
  active_2084_impact = 0
  row_count = 2105 (unchanged from round entry)
  persisted_old_profile_count = 21 (unchanged from round entry)
  silent_old_profile_count = 21 (unchanged from round entry)
  default_path_legacy_fallback_reach_count = 0 (unchanged)
  adopted_scope_canonical_legacy_residue = 0 (unchanged)
  resolver_behavior_delta = 0
  adapter_surface_delta = 0
  rendered_delta = 0
  lua_delta = 0
  runtime_delta = 0
  cleanup_plan_input_rule = amended_to_accept_adopted_replacement_authority
  cleanup_rewrite_executed = false
```

Expected blocked closeout when authority cannot be adopted:

```text
blocked:
  closeout_state =
    closed_blocked_replacement_authority_not_adopted
    or closed_blocked_conflicting_candidate_identity
    or closed_blocked_insufficient_provenance

  replacement_21_allowlist_status = not_adopted
  silent_21_mapping_authority_status = not_adopted
  cleanup_plan_input_rule = not_amended
  cleanup_rewrite_executed = false
```

Common final non-claims:

```text
This is not silent 21 cleanup complete.
This is not persisted_old_profile_count = 0.
This is not runtime equivalence full validation.
This is not full compatibility preservation.
This is not release readiness or deployment readiness.
This is not production validation.
This is not frozen 2105 recovery.
This is not resolver cleanup.
This is not adapter cleanup.
This is not Lua regeneration.
This is not rendered rebaseline.
This is not manual in-game QA pass.
This is not Workshop readiness.
This is not ready_for_release.
This is not original historical sealed authority recovery.
```
