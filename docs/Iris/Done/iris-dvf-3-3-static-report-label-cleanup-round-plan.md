# Iris DVF 3-3 Static Report Label Cleanup Round Plan

> 상태: Draft v0.3-plan  
> 기준일: 2026-05-20  
> 상위 기준: `docs/Philosophy.md`, `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`  
> authority input: `Iris DVF 3-3 Static Report Label Cleanup Round - ROADMAP (Consolidated)` (2026-05-19 user-provided synthesis)  
> review input: `Static Report Label Cleanup Round Plan - Consolidated Review` WARN feedback (2026-05-20), Critical C1-C3 and Important N1-N6 incorporated; `Static Report Label Cleanup Round Plan v0.2 - Consolidated Review` PASS feedback (2026-05-20), non-blocking robustness revisions incorporated.  
> 계획 형식: `docs/PLAN_TEMPLATE.md`  
> template attestation: this plan follows Section 0 disclosure plus the 1-12 section structure in `docs/PLAN_TEMPLATE.md`.  
> 실행 상태: planning authority only. 이 문서는 DVF 3-3 static report/operator-facing label cleanup round의 실행 계획이며, 작성 시점에는 source decisions, runtime Lua, rendered output, generated report artifacts, top-doc closeout state를 변경하지 않는다.

---

## 0. Round Opening Disclosure

Opening decision gate:

```text
Phase 3 mutation MUST NOT start until DECISIONS.md contains an append-only
Static Report Label Cleanup Round Opening Decision.
```

Opening decision may be either:

* a full opening entry that seals scope, Branch Y, immutable surfaces, failure semantics, and validation ceiling; or
* a one-line DECISIONS.md entry adopting this plan's Section 0 as the round opening decision.

The Phase 2 scope lock must record the DECISIONS.md opening entry location and hash. If no opening decision is present, the round is blocked with:

```text
blocked_opening_decision_missing
```

Execution scale:

```text
implementation/static-validation only
```

Round scope:

```text
current generated report / operator-facing static surface label hygiene
```

Canonical readpoint:

```text
runtime_state canonical enum = adopted / unadopted
legacy active / silent = diagnostic / import / historical read-only alias only
```

Chosen cleanup branch:

| Branch | Meaning | Disposition |
|---|---|---|
| `X_regenerate` | Re-run builders to regenerate reports | Rejected. Too much risk of overwriting sealed evidence artifacts or changing non-label payload. |
| `Y_in_place_label_substitution` | Rewrite eligible current static artifact labels with `active->adopted`, `silent->unadopted` | Adopted. This round is label-only and inherits the 2026-05-19 sealed mapping. |
| `Z_disclaimer_only` | Preserve labels and add disclaimer/sentinel text | Rejected. It leaves current operator surfaces visually ambiguous. |

Immutable surfaces:

* DECISIONS.md historical decision bodies.
* 2026-04-26 terminology migration note body.
* DECISIONS.md `증거:` path/hash locked artifacts.
* Runtime Lua chunk topology and staged/workspace Lua hashes.
* 2105-row source decision identity and rendered text.
* `runtime_state`, `quality_state`, and `publish_state` semantics.
* Browser/Wiki/Tooltip runtime behavior.

Mutable surfaces after scope lock only:

* Phase 1-7 round-local staging artifacts under:

```text
Iris/build/description/v2/staging/compose_contract_migration/static_report_label_cleanup_round/
```

* One single-writer build script:

```text
Iris/build/description/v2/tools/build/build_static_report_label_cleanup_round.py
```

* Surface (C) current operator artifacts listed in the Phase 2 mutation manifest.
* Phase 7 closeout addenda in `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, and `docs/ROADMAP.md` only after gates pass.

Failure semantics:

```text
opening decision missing -> blocked_opening_decision_missing
mapping authority evidence missing -> blocked_mapping_authority_missing
unclassified occurrence -> blocked_unknown_authority
sealed evidence hash delta -> blocked_sealed_evidence_mutation
historical body diff -> blocked_historical_body_mutation
non-label payload delta -> blocked_non_label_delta
rewrite-disposition active/silent residue > 0 -> blocked_static_residue_gate
validation command unavailable -> blocked_validation_tool_missing
```

Validation ceiling:

* Static residue and invariant validation only.
* No runtime rollout.
* No deployed closeout.
* No manual in-game QA pass.
* No Workshop release readiness.
* No `ready_for_release`.

---

## 1. Objective

The objective of this execution plan is to clean current DVF 3-3 generated report and operator-facing static artifacts so they no longer present legacy `active / silent` as current `runtime_state` labels.

The round closes this specific claim:

```text
Current generated report / operator-facing static surfaces no longer present active/silent
as current runtime-state labels; preserved historical/diagnostic residues are explicitly
allowed and separated, with runtime/source/rendered/Lua invariants unchanged.
```

This is a canonical readpoint hygiene round. It does not reopen the runtime payload enum migration closed on 2026-05-19, and it does not redefine `runtime_state`.

Expected closeout target:

```text
closed_with_static_report_label_cleanup_complete
rewrite-disposition occurrence active token count = 0
rewrite-disposition occurrence silent token count = 0
sealed evidence chain unchanged
historical sealed bodies unchanged
runtime/source/rendered/Lua invariants unchanged
```

---

## 2. Scope

In scope:

* Repository inventory of `active` and `silent` tokens in text-like files:

```text
.json
.jsonl
.md
.py
.lua
.txt
```

* Three-surface classification:

| Surface | Definition | Disposition |
|---|---|---|
| `A_historical_sealed_body` | Historical decisions, terminology migration note body, conservative top-doc historical body/readpoint text | Preserve unchanged. |
| `B_sealed_evidence_chain_referenced` | DECISIONS.md `증거:` path/hash locked artifacts | Preserve unchanged and hash-gate. |
| `C_current_operator_artifact` | Current generated report/operator-facing static artifact positively classified by Phase 1/2 as current report output | Cleanup target only after Phase 2 occurrence-level rewrite lock. |

Surface C hard rule:

```text
A file is not a mutation target merely because it is not Surface A or B.
Mutation requires positive Surface C classification AND explicit occurrence-level
rewrite disposition in the Phase 2 mutation manifest.
```

* Occurrence semantic classification:

```text
runtime_state_enum_value
liveness_or_scope_word
migration_metric_key
diagnostic_alias
historical_sealed_body
unrelated_token
blocked_unknown_authority
```

* Occurrence presentation/disposition classification:

```text
current_report_label
operator_output_label
machine_readable_key_preserve_or_followup
markdown_generated_table_header_or_status_label
markdown_historical_prose
json_value_current_status_summary
json_value_freeform_explanation
```

Only `runtime_state_enum_value` occurrences are rewrite candidates. Terms such as `active_rendered_preview_only`, `active resolver correctness debt`, `active execution queue`, `non_fallback_active_metadata_swap`, `fallback_dependent_active`, `active_old_profile_count`, and `active_native_profile_count` are not enum-value rewrite candidates in this round. The same preserve rule applies to `Silent Metadata Intake / Cleanup Round`, `Silent 21 Replacement Authority Reconstruction Round`, `silent_metadata_inventory`, `silent_metadata_inventory_status`, and `silent_old_profile_count`. Phase 2 may record these names only as preserve or follow-up scope.

Sealed round names, artifact names, field names, metric keys, and queue/scope identifiers are not enum values even when they contain `active` or `silent`.

* Branch Y in-place label substitution for Phase 2-approved cleanup targets.
* Strict `active -> adopted` and `silent -> unadopted` mapping inherited from the 2026-05-19 closeout.
* JSON/JSONL structured enum-token substitution where token boundaries are exact.
* Markdown generated current report table/header/status label substitution only when the occurrence is approved by Phase 2.
* Markdown historical prose and free-form explanation paragraphs are preserved.
* JSON parse validation after mutation.
* Byte-level snapshots of mutation targets before execution.
* Pre-round immutable baseline capture before any mutation.
* Static residue hard gate on cleanup target scope.
* Sealed exclusion hash gate.
* Addendum-only closeout in `DECISIONS.md`, `ARCHITECTURE.md`, and `ROADMAP.md`.

### Explicitly Out Of Scope

* Runtime Lua chunk regeneration or redeployment.
* Staged/workspace Lua hash change.
* Runtime payload enum rename reopening.
* Source decisions row identity change.
* Rendered text change.
* Runtime behavior change.
* Browser/Wiki/Tooltip runtime consumer revalidation beyond inherited 2026-05-19 evidence.
* Historical sealed body rewrite.
* DECISIONS.md historical decision body cleanup.
* 2026-04-26 terminology migration note body rewrite.
* DECISIONS.md `증거:` path/hash locked artifact byte-level mutation.
* Repo-wide `active/silent` zero.
* Dynamic surface cleanup or builder default writer fail-loud expansion.
* New resolver, adapter, writer, validator, or mapping authority.
* Release strategy, deployed closeout, manual in-game QA pass, Workshop readiness, or `ready_for_release`.

---

## 3. Non-Goals

This plan does not attempt to:

* Redefine `adopted` or `unadopted`.
* Treat `adopted` as quality-pass.
* Treat `unadopted` as deletion, suppression, hidden state, or publish state.
* Remove diagnostic/import/historical read-only alias handling for legacy `active/silent`.
* Expand default writer or validator fail-loud guards beyond the 2026-05-19 closeout.
* Rename unrelated tokens such as `activeView`, `inactive`, `silently`, or semantic-loaded labels like `active_composed`.
* Rename machine-readable report keys. Key cleanup is separated into a follow-up round unless this plan is explicitly amended before execution.
* Regenerate current reports through broader builder scripts when that could change non-label payload.
* Rewrite Markdown free-text historical explanations.
* Claim future builder output policy enforcement. Dynamic surface cleanup is a separate future round.

---

## 4. Assumptions

Authority assumptions:

* `docs/Philosophy.md` is the top authority.
* `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, and `docs/ROADMAP.md` are the current governance readpoints.
* The 2026-05-19 Runtime Payload Enum Rename Scope Round closeout is authoritative for the mapping:

```text
active -> adopted
silent -> unadopted
```

* The round inherits that mapping only; it does not create new mapping authority.
* Historical sealed decision bodies are read-only.
* DECISIONS.md evidence-path artifacts are byte-preserved.

Baseline assumptions:

```text
row_count = 2105
adopted_count = 2084
unadopted_count = 21
previous legacy split = active 2084 / silent 21
quality_state values = strong / adequate / weak
publish_state values = internal_only / exposed
```

Execution assumptions:

* Windows PowerShell is the execution shell.
* `rg` is used for search.
* `git diff --stat` and `git diff` are used for change review.
* Validation is claimable only when the exact command exits with code `0`.
* If `jq`, Python, or Lua validation tooling is unavailable, the affected validation is reported as blocked, not passed.

Classification assumptions:

* 4-document body text is classified conservatively as Surface A except Phase 7 append-only closeout entries.
* Markdown historical prose and free-form paragraphs are not substitution targets in Phase 3.
* Markdown generated current report table/header/status labels may be substituted only after occurrence-level Phase 2 approval.
* JSON/JSONL values are preferred substitution targets when Phase 2 marks them as current operator labels or current runtime-state count summaries.
* JSON value strings that are explanatory prose are preserve targets unless Phase 2 explicitly classifies the span as a current generated status label.
* Machine-readable key rename is prohibited in this round. If Phase 1 identifies key cleanup need, record it as follow-up scope.

---

## 5. Repository Areas Affected

### Code

Planned single writer:

```text
Iris/build/description/v2/tools/build/build_static_report_label_cleanup_round.py
```

Read-only or validation-only code areas:

```text
Iris/build/description/v2/tools/build/**
Iris/build/description/v2/tests/**
tools/check_lua_syntax.ps1
```

### Docs

This plan document:

```text
docs/Iris/iris-dvf-3-3-static-report-label-cleanup-round-plan.md
```

Phase 7 closeout addenda only:

```text
docs/DECISIONS.md
docs/ARCHITECTURE.md
docs/ROADMAP.md
```

Phase 0 opening decision before mutation:

```text
docs/DECISIONS.md
```

DECISIONS.md has two append-only mutation windows in this round:

```text
Phase 0 opening decision before Phase 3 mutation
Phase 7 closeout after gates pass
```

Both windows are append-only and must not rewrite historical bodies.

Historical body and terminology note text in the 4-document set remain unchanged outside append-only closeout entries.

### Config

No config mutation is planned.

### Generated Artifacts

Round-local staging root:

```text
Iris/build/description/v2/staging/compose_contract_migration/static_report_label_cleanup_round/
```

Primary generated deliverables:

```text
phase1_inventory/phase1_token_inventory.json
phase1_inventory/phase1_surface_classification.json
phase1_inventory/phase1_cleanup_target_list.json
phase1_inventory/phase1_sealed_exclusion_list.json
phase1_inventory/phase1_occurrence_classification.json
phase1_inventory/phase1_unknown_authority_blockers.json
phase1_inventory/pre_round_immutable_baseline.json
phase1_inventory/phase1_inventory_summary.md
phase2_scope_lock/scope_lock_report.json
phase2_scope_lock/mapping_authority_inheritance.json
phase2_scope_lock/branch_decision.json
phase2_disposition_matrix.json
phase2_allowed_legacy_residue.json
phase2_mutation_target_manifest.json
phase3_execution/pre_execution_snapshot/
phase3_execution/phase3_execution_diff_report.json
phase3_execution/phase3_substitution_log.jsonl
phase4_invariant_verification/phase4_invariant_verification_report.json
phase5_static_residue/static_residue_report.json
phase5_static_residue/phase5_invariant_verification_report.json
phase5_static_residue/phase5_hard_gate_report.json
phase5_static_residue/dynamic_surface_scope_out_note.md
phase6_adversarial_review/review_report.md
phase7_closeout/phase7_closeout.json
phase7_closeout/phase7_closeout.md
```

Cleanup target artifacts are determined only by Phase 1/2 outputs and must not be hand-expanded during Phase 3.

---

## 6. Planned Changes

### Change 0 - Phase 0 round opening decision gate

Purpose:

Seal the round opening in DECISIONS.md before any mutation-capable phase starts.

Files:

```text
docs/DECISIONS.md
Iris/build/description/v2/staging/compose_contract_migration/static_report_label_cleanup_round/phase2_scope_lock/scope_lock_report.json
```

Implementation Notes:

* Add an append-only `Static Report Label Cleanup Round Opening Decision` to DECISIONS.md before Phase 3 execution.
* The entry must seal scope, Branch Y, immutable surfaces, failure semantics, validation ceiling, and non-claims, or explicitly adopt this plan's Section 0 as the opening decision.
* Phase 2 must record the opening entry location and hash in `scope_lock_report.json`.
* If opening is absent, mutation is blocked.

Validation:

```text
opening_decision_present = true
opening_decision_mode = full_entry | section_0_adoption
opening_decision_hash_recorded = true
phase3_entry_allowed_only_after_opening = true
```

---

### Change 1 - Phase 1 scope inventory and three-surface classification

Purpose:

Inventory every `active` and `silent` token in the repository's text-like target extensions, classify each file and occurrence into Surface A/B/C, and capture immutable pre-round baselines before any mutation.

Files:

```text
Iris/build/description/v2/staging/compose_contract_migration/static_report_label_cleanup_round/phase1_inventory/phase1_token_inventory.json
Iris/build/description/v2/staging/compose_contract_migration/static_report_label_cleanup_round/phase1_inventory/phase1_surface_classification.json
Iris/build/description/v2/staging/compose_contract_migration/static_report_label_cleanup_round/phase1_inventory/phase1_cleanup_target_list.json
Iris/build/description/v2/staging/compose_contract_migration/static_report_label_cleanup_round/phase1_inventory/phase1_sealed_exclusion_list.json
Iris/build/description/v2/staging/compose_contract_migration/static_report_label_cleanup_round/phase1_inventory/phase1_occurrence_classification.json
Iris/build/description/v2/staging/compose_contract_migration/static_report_label_cleanup_round/phase1_inventory/phase1_unknown_authority_blockers.json
Iris/build/description/v2/staging/compose_contract_migration/static_report_label_cleanup_round/phase1_inventory/pre_round_immutable_baseline.json
Iris/build/description/v2/staging/compose_contract_migration/static_report_label_cleanup_round/phase1_inventory/phase1_inventory_summary.md
```

Implementation Notes:

* Use `rg` for repository-wide search.
* Restrict inventory to `.json`, `.jsonl`, `.md`, `.py`, `.lua`, and `.txt`.
* Parse DECISIONS.md evidence sections separately to extract sealed evidence path/hash references.
* Classify 4-document body text conservatively as Surface A unless it is a new Phase 7 closeout addendum.
* Split current report labels from historical explanations, diagnostic aliases, and unrelated tokens.
* Classify every occurrence with both a semantic axis and a presentation/disposition axis.
* Semantic axis values:

```text
runtime_state_enum_value
liveness_or_scope_word
migration_metric_key
diagnostic_alias
historical_sealed_body
unrelated_token
blocked_unknown_authority
```

* Treat liveness/scope/debt terms such as `active_rendered_preview_only`, `active resolver correctness debt`, and `active execution queue` as preserve targets.
* Treat migration metric keys such as `active_old_profile_count` and `active_native_profile_count` as machine-readable key preserve/follow-up targets.
* Treat sealed round names and artifact/metric identifiers such as `Silent Metadata Intake / Cleanup Round`, `Silent 21 Replacement Authority Reconstruction Round`, `silent_metadata_inventory`, `silent_metadata_inventory_status`, and `silent_old_profile_count` as preserve targets.
* Use 2026-05-19 static scan findings, including known unrelated `activeView`, as known-safe seed evidence where applicable.
* Place unknown authority occurrences in blockers instead of guessing.
* Capture `pre_round_immutable_baseline.json` before any Phase 3 mutation. The manifest must include source decisions, rendered artifacts, runtime chunks, staged/workspace Lua, DECISIONS.md historical body ranges or hashes, terminology migration note body hash, and every sealed evidence path hash.

Validation:

```text
token_total == sum(per_file_token_count)
all_inventory_hits_classified = true
surface_assignment_missing_count = 0
sealed_evidence_paths_classified_as_B = true
historical_sealed_body_in_cleanup_targets = false
semantic_axis_missing_count = 0
surface_c_candidate_requires_positive_classification = true
no_source_code_file_in_mutation_targets_except_round_writer = true
pre_round_immutable_baseline_captured_before_mutation = true
unknown_authority_occurrences_reported = true
```

---

### Change 2 - Phase 2 scope lock and disposition matrix

Purpose:

Freeze the cleanup target list, sealed exclusion list, mapping authority inheritance, branch decision, and occurrence-level disposition before mutation.

Files:

```text
Iris/build/description/v2/staging/compose_contract_migration/static_report_label_cleanup_round/phase2_scope_lock/scope_lock_report.json
Iris/build/description/v2/staging/compose_contract_migration/static_report_label_cleanup_round/phase2_scope_lock/mapping_authority_inheritance.json
Iris/build/description/v2/staging/compose_contract_migration/static_report_label_cleanup_round/phase2_scope_lock/branch_decision.json
Iris/build/description/v2/staging/compose_contract_migration/static_report_label_cleanup_round/phase2_disposition_matrix.json
Iris/build/description/v2/staging/compose_contract_migration/static_report_label_cleanup_round/phase2_allowed_legacy_residue.json
Iris/build/description/v2/staging/compose_contract_migration/static_report_label_cleanup_round/phase2_mutation_target_manifest.json
```

Implementation Notes:

* Record SHA-256 hashes for Phase 1 outputs in `scope_lock_report.json`.
* Record DECISIONS.md opening decision location and hash in `scope_lock_report.json`.
* Record 2026-05-19 closeout evidence path/hash as inherited mapping authority.
* Mapping authority lookup rule:

```text
1. primary:
   Iris/build/description/v2/staging/compose_contract_migration/runtime_payload_enum_rename_scope_round/phase4_runtime_artifact_disposition/runtime_payload_delta_report.json
   and/or
   Iris/build/description/v2/staging/compose_contract_migration/runtime_payload_enum_rename_scope_round/phase8_closeout/closeout_seal.json
2. fallback: docs/ROADMAP.md 2026-05-19 Runtime Payload Enum Rename Scope Round ledger
   plus docs/DECISIONS.md matching closeout entry.
3. if neither is present: blocked_mapping_authority_missing.
```

* Phase 2 must verify any selected primary mapping authority path exists before using it. If a primary candidate is absent, record that absence and either use the other primary artifact or fall back to the paired ROADMAP/DECISIONS entries.
* Freeze Branch Y as selected and Branch X/Z as rejected.
* Positively classify Surface C before mutation. A file is never a target merely because it is not Surface A or B.
* If Phase 1 finds no Surface C current operator/report residue, set disposition to `no_current_operator_residue_found`, skip Phase 3 mutation, and proceed only to verification/closeout for that state.
* For every occurrence, assign one disposition:

```text
rewrite
preserve
ignore
blocked
```

* Require expected replacement for each rewrite target.
* Require preserve reason for each preserved occurrence.
* Prohibit machine-readable key rename in this round. Record key cleanup needs as follow-up scope.
* Mark `active_composed` and unrelated identifiers as preserve/ignore unless Phase 1 proves a current report label meaning.
* Enum-value positive criteria:

```text
The occurrence must explicitly represent the current runtime_state value or the current
runtime_state count split, such as "active 2084 / silent 21" in a generated current
operator report. Liveness, scope, debt, queue, migration metric, code identifier,
sealed round names, artifact names, field names, metric keys, and historical prose usages
are not runtime_state_enum_value occurrences.
```

* Count-adjacent forms such as `active 2084 / silent 21` are rewrite-eligible only when Phase 2 records `runtime_state_enum_value` and `current_report_label` or `operator_output_label`.
* JSON value strings are rewrite-eligible only when the approved span is a current generated status label or count summary; explanatory prose remains preserve.

Validation:

```text
phase1_artifact_hashes_recorded = true
opening_decision_hash_recorded = true
mapping_authority_inheritance_matches_2026_05_19_closeout = true
branch_decision = Y_in_place_label_substitution
positive_surface_c_required_for_mutation = true
rewrite_targets_have_expected_replacement = true
preserve_targets_have_preserve_reason = true
blocked_targets_count = 0 before Phase 3
machine_readable_key_rewrite_target_count = 0
runtime_state_enum_value_required_for_rewrite = true
```

---

### Change 3 - Phase 3 in-place label substitution

Purpose:

Execute strict in-place substitution on Phase 2-approved cleanup targets only, with byte snapshots and label-only diff reporting.

Files:

```text
Iris/build/description/v2/tools/build/build_static_report_label_cleanup_round.py
Iris/build/description/v2/staging/compose_contract_migration/static_report_label_cleanup_round/phase3_execution/pre_execution_snapshot/
Iris/build/description/v2/staging/compose_contract_migration/static_report_label_cleanup_round/phase3_execution/phase3_execution_diff_report.json
Iris/build/description/v2/staging/compose_contract_migration/static_report_label_cleanup_round/phase3_execution/phase3_substitution_log.jsonl
```

Implementation Notes:

* The build script is the only writer for this round.
* Do not run mutation if Phase 2 selected `no_current_operator_residue_found`.
* The script must read Phase 2 mutation target manifest and sealed exclusion list.
* The script must fail loud if any target is inside or equals a sealed exclusion path.
* Preserve a byte-level pre-execution snapshot for every mutation target.
* Substitute only occurrences approved by Phase 2 as `runtime_state_enum_value` with rewrite disposition.
* Substitute only exact JSON/JSONL enum tokens or approved occurrence spans. Whole-file lexical replacement is forbidden.
* Apply only:

```text
"active" -> "adopted"
"silent" -> "unadopted"
```

* Rewrite display/count labels only when Phase 2 explicitly classifies them as current runtime-state labels, for example:

```text
active count -> adopted count
silent count -> unadopted count
active rows -> adopted rows
silent rows -> unadopted rows
active 2084 / silent 21 -> adopted 2084 / unadopted 21
```

* Do not modify machine-readable keys in this round. Parser-consumed keys such as `active_count` / `silent_count`, if found, are preserve/follow-up targets.
* Markdown handling:

```text
Markdown historical prose/body text -> preserve.
Markdown generated current report table/header/status label -> rewrite only with occurrence-level approval.
Markdown free-form explanation paragraph -> preserve.
```

* JSON value handling:

```text
JSON/JSONL enum value or current generated status summary span -> rewrite only with approval.
JSON/JSONL explanatory prose sentence -> preserve unless Phase 2 approves a precise label span.
```

* Do not modify unrelated substrings such as `inactive`, `silently`, or `activeView`.
* Do not modify liveness/scope/debt/queue usages such as `active_rendered_preview_only` or `active execution queue`.
* Re-parse each changed `.json` file with `json.loads`.
* Re-parse `.jsonl` files line by line when mutated.
* Stop the line on any non-label payload delta.
* For JSON/JSONL, compare normalized structures before/after after reverse-mapping approved label fields/spans only.
* For Markdown, compare only approved occurrence spans; all non-approved spans must be byte-identical.
* For any file type without structured diff support, require occurrence-span replacement log and byte-range verification.

Validation:

```text
target_file_count_before == target_file_count_after
changed_json_files_parse = true
changed_jsonl_files_parse = true
sealed_exclusion_files_hash_unchanged = true
rewrite_occurrences_all_runtime_state_enum_value = true
markdown_rewrite_occurrences_are_structured_generated_labels_only = true
machine_readable_key_rewrite_count = 0
non_label_payload_delta_count = 0
source_decisions_diff = 0
rendered_artifact_diff = 0
runtime_lua_diff = 0
```

---

### Change 4 - Phase 4 invariant verification

Purpose:

Seal that the cleanup did not mutate source/runtime/decision/rendered/sealed evidence surfaces.

Files:

```text
Iris/build/description/v2/staging/compose_contract_migration/static_report_label_cleanup_round/phase4_invariant_verification/phase4_invariant_verification_report.json
```

Implementation Notes:

* Compare source decisions hash against the pre-round baseline.
* Use only `phase1_inventory/pre_round_immutable_baseline.json` as the comparison baseline.
* Treat any baseline computed after Phase 3 mutation as invalid for invariant claims.
* Verify row count and row identity are unchanged.
* Verify rendered artifact hash is unchanged.
* Verify runtime chunk hashes and topology are unchanged.
* Verify staged/workspace Lua hashes are unchanged.
* Verify `runtime_state`, `quality_state`, and `publish_state` semantics are unchanged through hash/report comparison.
* Verify DECISIONS.md historical decision bodies and terminology migration note body are unchanged.
* Verify DECISIONS.md evidence path/hash locked artifacts are byte unchanged.

Validation:

```text
row_count = 2105
baseline_source = phase1_inventory/pre_round_immutable_baseline.json
baseline_captured_before_mutation = true
row_identity_unchanged = true
rendered_text_unchanged = true
runtime_state_semantics_unchanged = true
quality_state_unchanged = true
publish_state_unchanged = true
staged_lua_hash_unchanged = true
workspace_lua_hash_unchanged = true
chunk_topology_unchanged = true
historical_decision_bodies_unchanged = true
terminology_migration_note_body_unchanged = true
sealed_evidence_chain_hash_gate = pass
```

---

### Change 5 - Phase 5 static residue hard gate

Purpose:

Prove that Surface C cleanup target scope has zero current operator-facing `active/silent` label residue while allowed historical/diagnostic residues remain separated.

Files:

```text
Iris/build/description/v2/staging/compose_contract_migration/static_report_label_cleanup_round/phase5_static_residue/static_residue_report.json
Iris/build/description/v2/staging/compose_contract_migration/static_report_label_cleanup_round/phase5_static_residue/phase5_invariant_verification_report.json
Iris/build/description/v2/staging/compose_contract_migration/static_report_label_cleanup_round/phase5_static_residue/phase5_hard_gate_report.json
Iris/build/description/v2/staging/compose_contract_migration/static_report_label_cleanup_round/phase5_static_residue/dynamic_surface_scope_out_note.md
```

Implementation Notes:

* Evaluate the hard zero gate at occurrence/disposition level, not whole-file lexical level.
* Scan Phase 2 rewrite-disposition occurrences for residue.
* Count adopted/unadopted replacement tokens for traceability.
* Count sealed exclusion legacy tokens as information only.
* If a cleanup target file contains approved diagnostic/historical preserve occurrences, preserve those spans and verify exact match instead of forcing whole-file lexical zero.
* Confirm allowed historical residue exact match.
* Confirm allowed diagnostic/import alias residue exact match.
* Record dynamic surface cleanup as explicitly out of scope.

Validation:

```text
cleanup_target_rewrite_occurrence_scope_active_token_count = 0
cleanup_target_rewrite_occurrence_scope_silent_token_count = 0
rewrite_disposition_occurrence_active_silent_residue = 0
current_report_label_residue = 0
operator_output_label_residue = 0
allowed_preserve_occurrence_exact_match = true
operator_output_legacy_label_residue = 0
blocked_unknown_occurrence = 0
allowed_historical_residue_exact_match = true
allowed_diagnostic_import_alias_residue_exact_match = true
sealed_exclusion_scope_hash_gate = pass
```

Regression validation:

```powershell
python -B -m unittest discover -s Iris\build\description\v2\tests -p "test_*.py"
```

Lua syntax baseline validation:

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\check_lua_syntax.ps1
```

---

### Change 6 - Phase 6 adversarial review

Purpose:

Review the round against governance, sealed entries, current readpoints, claim boundaries, and non-goals before closeout.

Files:

```text
Iris/build/description/v2/staging/compose_contract_migration/static_report_label_cleanup_round/phase6_adversarial_review/review_report.md
```

Implementation Notes:

Review axes:

* `docs/Philosophy.md` compliance.
* Hub & Spoke / SPI preservation.
* Iris-only scope.
* 2026-05-19 mapping inheritance integrity.
* 2026-04-26 terminology migration note body preservation.
* Sealed evidence chain hash gate.
* Single-writer principle.
* Fail-loud principle.
* Runtime/build-time separation.
* Non-goals and claim ceiling.
* Generator source/orphan artifact disposition.
* Machine-readable key compatibility risk.
* Missing scope and validation weakness.

Validation:

```text
verdict = PASS | WARN | FAIL
PASS permits Phase 7
WARN requires documented residual risk or revisions
FAIL blocks closeout
critical_issue_count = 0 before Phase 7
WARN_with_documented_revisions is closeout-eligible only when critical_issue_count = 0
and remaining warnings do not affect mutation target classification, sealed-surface
preservation, or invariant claims.
```

---

### Change 7 - Phase 7 documentation and closeout

Purpose:

Seal the static label cleanup result in round-local closeout artifacts and top-level governance addenda without rewriting historical bodies.

Files:

```text
Iris/build/description/v2/staging/compose_contract_migration/static_report_label_cleanup_round/phase7_closeout/phase7_closeout.json
Iris/build/description/v2/staging/compose_contract_migration/static_report_label_cleanup_round/phase7_closeout/phase7_closeout.md
docs/DECISIONS.md
docs/ARCHITECTURE.md
docs/ROADMAP.md
```

Implementation Notes:

* DECISIONS.md update is append-only.
* DECISIONS.md has two append-only mutation windows for this round: Phase 0 opening before Phase 3 mutation, and Phase 7 closeout after gates pass. Both must preserve historical bodies.
* DECISIONS.md closeout entry records:

```text
rewrite-disposition current_report/operator occurrence active/silent residue = 0
sealed scope unchanged
terminology migration note body unchanged
terminology migration note applicability narrowed to historical sealed body read alias
runtime rollout non-claim
dynamic surface cleanup non-claim
default writer guard expansion non-claim
```

* ARCHITECTURE.md update is append-only or a current-readpoint ledger addition in `9-3. Historical addendum trace ledger`.
* Existing historical rows and historical bodies are not rewritten.
* If an existing current ledger row must be superseded, add a new current row instead of editing historical content.
* ROADMAP.md update adds a Done item for this round and does not rewrite older Done records.
* Closeout artifacts list Phase 1-6 evidence paths and hashes.

Validation:

```text
top_doc_update_mode = append_only_or_current_readpoint_addendum
historical_body_direct_rewrite_count = 0
docs_claims_match_hard_gate = true
non_claims_explicit = true
blocked_residue_count = 0 or documented closed_with_allowed_historical_residue
```

After docs closeout updates, rerun:

```powershell
python -B -m unittest discover -s Iris\build\description\v2\tests -p "test_*.py"
powershell -ExecutionPolicy Bypass -File .\tools\check_lua_syntax.ps1
```

---

## 7. Validation Plan

### Automated Validation

Required search and review:

The repository-wide `rg` scan is a review aid. The hard gate is occurrence/disposition-scoped through Phase 5, not repo-wide lexical zero.

```powershell
rg "active|silent" docs Iris
git diff --stat
git diff
```

Required parsing/checks:

```text
Phase 1 token total reconciliation
Phase 1 all-hit classification
Phase 1 pre_round_immutable_baseline capture before mutation
Phase 0 DECISIONS.md opening decision present before Phase 3
Phase 2 scope-lock artifact hash verification
Phase 2 mapping authority lookup verification
Phase 2 positive Surface C mutation manifest verification
Phase 3 JSON/JSONL parse validation
Phase 3 occurrence-span replacement verification
Phase 4 invariant verification
Phase 5 occurrence/disposition-level static residue hard gate
Phase 6 adversarial review verdict
```

Required mutation manifest assertions:

```text
mutation_target_manifest_contains_only_positive_surface_c_files = true
no_source_code_file_in_mutation_targets_except_round_writer = true
markdown_rewrite_occurrences_are_structured_generated_labels_only = true
machine_readable_key_rewrite_target_count = 0
runtime_state_enum_value_required_for_rewrite = true
```

Required regression commands:

```powershell
python -B -m unittest discover -s Iris\build\description\v2\tests -p "test_*.py"
powershell -ExecutionPolicy Bypass -File .\tools\check_lua_syntax.ps1
```

Validation claim rule:

* Do not claim Python tests passed unless the exact command exits `0`.
* Do not claim Lua syntax passed unless the exact command exits `0`.
* If required tooling is missing, report validation as blocked.

### Manual Validation

Manual review is limited to:

* Phase 1 Surface A/B/C classification review.
* Phase 2 disposition matrix review.
* Phase 3 diff review for label-only changes.
* Phase 4 sealed hash gate review.
* Phase 5 residue report review.
* Phase 6 adversarial review.
* Phase 7 closeout wording review.

No manual in-game QA pass is part of this plan.

### Validation Limits

This execution does not perform:

* Runtime equivalence validation.
* Manual in-game QA pass.
* Deployed runtime smoke.
* Multiplayer validation.
* Long-session runtime validation.
* External ecosystem compatibility sweep.
* Browser/Wiki/Tooltip runtime consumer revalidation.
* Dynamic surface validation for future builder output.
* Machine-readable key consumer safety validation. Machine-readable key rename is prohibited in this round; any key cleanup is follow-up scope.
* Workshop compatibility sweep.
* Release readiness validation.

---

## 8. Risk Surface Touch

### Authority Surface

No new authority is created. The round inherits the 2026-05-19 mapping authority only. The single writer is a round-local cleanup script that writes approved static report/operator artifact labels; it is not a state writer or mapping authority.

### Runtime Behavior Surface

None. Runtime Lua chunks, Browser/Wiki/Tooltip behavior, in-game behavior, source decisions, and rendered output remain unchanged.

### Compatibility Surface

Low if label/value-only. Machine-readable key rename creates compatibility surface and is prohibited in this round. If Phase 1 finds parser-consumed key residue, record it as follow-up scope rather than renaming it here. Diagnostic/import alias residues are preserved as legacy contexts when needed.

### Sealed Artifact Surface

Preserved. Surface A and Surface B are byte-unchanged. Sealed evidence chain hash gate is mandatory.

### Public-Facing Output Surface

Internal/operator-facing static output only. This is not Workshop/public release output and does not change user-facing runtime behavior.

---

## 9. Risk Analysis

### Architecture Risk

* Surface A/B/C misclassification could mutate sealed material or miss current operator residue.
* The cleanup script could be misread as new enum authority.
* Dynamic surface cleanup could drift into scope without an explicit follow-up round.
* Closeout wording could imply runtime rollout or release readiness.

### Runtime Risk

* Expected none, because runtime Lua and behavior are immutable.
* Any runtime Lua diff is a hard failure and rollback trigger.

### Compatibility Risk

* Blind key rename could break downstream parsers.
* Removing diagnostic/import legacy alias references could break compatibility fixtures.
* `active_composed` or other semantic-loaded historical metrics could be renamed incorrectly.

### Regression Risk

* JSON/JSONL formatting or parse validity could break if substitution is not structured.
* Non-label payload could change if broad regeneration is used.
* Sealed evidence artifacts could be overwritten if exclusion guard is incomplete.
* Historical top-doc wording could be rewritten accidentally.

---

## 10. Rollback Plan

Before Phase 3 mutation:

* Create byte-level snapshots for every mutation target under `phase3_execution/pre_execution_snapshot/`.
* Record target file hashes before substitution.

Rollback triggers:

```text
Phase 4 invariant failure
Phase 5 hard gate failure
sealed evidence hash delta
historical body diff
non-label payload delta
source decisions / rendered / Lua / runtime artifact diff
machine-readable key compatibility risk discovered after mutation
```

Rollback action:

* Restore each mutation target from its Phase 3 snapshot.
* Verify restored hashes match pre-execution hashes.
* Emit `phase_rollback_report.json` with reason, restored files, and verification result.
* If classification was wrong, reopen Phase 1 classification only for the affected surface.

Closeout-after-discovery rule:

* If additional residue is found after closeout, preserve this round's closeout append-only and open a separate follow-up round.

---

## 11. Governance Constraints

Required constraints:

* `docs/Philosophy.md` compliance.
* Hub & Spoke boundary preservation.
* Iris-only scope; Pulse is not a spoke and is not referenced as an implementation dependency.
* Four-document governance authority preservation.
* Single-writer principle for cleanup artifacts.
* Fail-loud principle.
* Runtime/build-time separation.
* Historical sealed body direct rewrite prohibition.
* DECISIONS.md evidence path/hash artifact byte preservation.
* 2026-04-26 terminology migration note body unchanged.
* 2026-05-19 mapping authority inherited only.
* No new resolver, adapter, validator, writer, or mapping authority.
* Row identity, row count, rendered text, runtime_state, quality_state, publish_state, staged/workspace Lua hash, and chunk topology unchanged.
* Machine-readable key rename prohibited in this round; key cleanup requires a separate follow-up or explicit plan amendment before execution.
* Dynamic surface cleanup and future builder output enforcement are out of scope.
* Closeout ceiling: implementation/static-validation only.
* No runtime rollout, deployed closeout, manual in-game QA pass, Workshop readiness, or `ready_for_release`.

---

## 12. Expected Closeout State

Expected closeout is `complete` if Phase 1-7 pass:

```text
closed_with_static_report_label_cleanup_complete
opening_decision_present = true
pre_round_immutable_baseline_captured_before_mutation = true
cleanup_target_rewrite_occurrence_scope_active_token_count = 0
cleanup_target_rewrite_occurrence_scope_silent_token_count = 0
current_report_label_residue = 0
operator_output_label_residue = 0
allowed_preserve_occurrence_exact_match = true
operator_output_legacy_label_residue = 0
sealed_exclusion_scope_hash_gate = pass
historical_body_direct_rewrite_count = 0
terminology_migration_note_body_unchanged = true
source_decisions_unchanged = true
row_count = 2105
row_identity_unchanged = true
rendered_text_unchanged = true
runtime_lua_unchanged = true
chunk_topology_unchanged = true
quality_state_unchanged = true
publish_state_unchanged = true
phase6_adversarial_review = PASS or WARN_with_documented_revisions
warn_closeout_eligible_only_if_critical_issue_count_0 = true
warn_closeout_eligible_only_if_no_target_or_sealed_or_invariant_impact = true
```

If Phase 1 finds no Surface C current operator/report residue, close as:

```text
closed_with_no_current_operator_residue_found
```

This state means the round premise was investigated and no current operator-facing static legacy label surface was found. It is not a cleanup-executed claim and does not imply repo-wide `active/silent` zero.

Allowed partial closeout states:

```text
closed_with_no_current_operator_residue_found
closed_with_allowed_historical_residue
closed_with_dynamic_surface_scope_out
blocked_unknown_authority
blocked_mapping_authority_missing
blocked_opening_decision_missing
blocked_sealed_evidence_mutation
blocked_static_residue_gate
blocked_validation_tool_missing
```

Non-claims at closeout:

* No runtime rollout.
* No deployed closeout.
* No runtime equivalence claim beyond checked invariants.
* No manual in-game QA pass.
* No Workshop release readiness.
* No `ready_for_release`.
* No repo-wide `active/silent` zero.
* No dynamic builder output guarantee.
* No terminology migration note body rewrite.
* No DECISIONS.md historical decision body cleanup.
* No new mapping authority.
